"""Authentication routes for user registration, login, and token management."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, RefreshToken
from api.auth.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    MessageResponse,
    PasswordChangeRequest,
)
from api.auth.password import hash_password, verify_password
from api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    JWTConfig,
)
from api.auth.dependencies import get_current_user
from api.auth.audit import (
    log_registration,
    log_login_success,
    log_login_failure,
    log_logout,
    log_password_change,
    log_account_locked,
)
from api.auth.lockout import (
    check_account_lockout,
    record_failed_login,
    record_successful_login,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data
        request: FastAPI request object
        db: Database session

    Returns:
        Created user data

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pw,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    log_registration(db=db, request=request, user_id=new_user.id, username=new_user.username)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login user and return JWT tokens with account lockout protection.

    Args:
        login_data: Login credentials
        request: FastAPI request object
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid or account is locked
    """
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Check account lockout first
    if user:
        is_locked, lock_message = check_account_lockout(user)
        if is_locked:
            log_login_failure(
                db=db,
                request=request,
                username=login_data.username,
                reason="Account locked",
                user_id=user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=lock_message,
            )

    # Verify credentials
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Record failed login attempt
        if user:
            is_now_locked, remaining = record_failed_login(db, user)

            if is_now_locked:
                log_account_locked(
                    db=db,
                    request=request,
                    user_id=user.id,
                    username=login_data.username,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked due to multiple failed login attempts. Try again in 30 minutes.",
                )

            log_login_failure(
                db=db,
                request=request,
                username=login_data.username,
                reason=f"Invalid credentials. {remaining} attempts remaining.",
                user_id=user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect username or password. {remaining} attempts remaining before account lockout.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # User not found
        log_login_failure(
            db=db,
            request=request,
            username=login_data.username,
            reason="User not found",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        log_login_failure(
            db=db,
            request=request,
            username=login_data.username,
            reason="Inactive user",
            user_id=user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Record successful login
    record_successful_login(db, user)

    # Create tokens
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }

    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token(token_data)

    # Store refresh token in database
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(
        days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS
    )

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=refresh_token_expires,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    db.add(refresh_token)
    db.commit()

    # Log successful login
    log_login_success(db=db, request=request, user_id=user.id, username=user.username)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_request: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_request: Refresh token request
        db: Database session

    Returns:
        New access token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    # Decode refresh token
    token_data = decode_refresh_token(refresh_request.refresh_token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Check if refresh token exists in database and is not revoked
    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_request.refresh_token,
            RefreshToken.user_id == token_data.user_id,
            RefreshToken.revoked == False,
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked",
        )

    # Check if token is expired
    # Make expires_at timezone-aware if it isn't already
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # Get user
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    new_token_data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }
    access_token = create_access_token(new_token_data)

    return TokenRefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    refresh_request: TokenRefreshRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking refresh token.

    Args:
        refresh_request: Refresh token to revoke
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Find and revoke refresh token
    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_request.refresh_token,
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False,
        )
        .first()
    )

    if db_token:
        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()
        db.commit()

    # Log logout
    log_logout(db=db, request=request, user_id=current_user.id, username=current_user.username)

    return MessageResponse(message="Successfully logged out")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout user from all devices by revoking all refresh tokens.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Revoke all refresh tokens for the user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False,
    ).update({"revoked": True, "revoked_at": datetime.utcnow()})

    db.commit()

    # Log logout
    log_logout(db=db, request=request, user_id=current_user.id, username=current_user.username)

    return MessageResponse(message="Successfully logged out from all devices")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User data
    """
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change user password.

    Args:
        password_data: Current and new password
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)

    # Update password
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.utcnow()

    db.commit()

    # Log password change
    log_password_change(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
    )

    return MessageResponse(message="Password changed successfully")
