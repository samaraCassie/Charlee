"""OAuth authentication routes for Google and GitHub."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.config import get_db
from api.auth.oauth import (
    oauth,
    create_or_update_oauth_user,
    extract_google_user_info,
    extract_github_user_info,
    generate_unique_username,
)
from api.auth.jwt import create_access_token, create_refresh_token, JWTConfig
from api.auth.audit import log_oauth_login, log_login_failure
from api.auth.lockout import check_account_lockout
from datetime import datetime, timedelta, timezone
from database.models import RefreshToken
import httpx

router = APIRouter(prefix="/api/v1/auth/oauth", tags=["OAuth"])


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.

    Redirects user to Google authorization page.
    """
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.

    Processes the OAuth response and creates/updates user.
    """
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)

        # Extract user info
        user_info = extract_google_user_info(token)

        # Ensure username is unique
        username = generate_unique_username(db, user_info['username'])
        user_info['username'] = username

        # Create or update user
        user = create_or_update_oauth_user(
            db=db,
            provider='google',
            oauth_id=user_info['oauth_id'],
            email=user_info['email'],
            username=user_info['username'],
            full_name=user_info.get('full_name'),
            avatar_url=user_info.get('avatar_url'),
        )

        # Check account lockout (even for OAuth)
        is_locked, lock_message = check_account_lockout(user)
        if is_locked:
            log_login_failure(
                db=db,
                request=request,
                username=user.username,
                reason="Account locked",
                user_id=user.id,
            )
            raise HTTPException(status_code=403, detail=lock_message)

        # Create tokens
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }

        access_token = create_access_token(token_data)
        refresh_token_str = create_refresh_token(token_data)

        # Store refresh token
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

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Log successful OAuth login
        log_oauth_login(
            db=db,
            request=request,
            user_id=user.id,
            username=user.username,
            provider='google',
        )

        # Redirect to frontend with tokens
        # In production, use a more secure method (e.g., httponly cookies)
        frontend_url = request.url_for('root').replace('/api/v1/auth/oauth/google/callback', '')
        redirect_url = f"{frontend_url}/?access_token={access_token}&refresh_token={refresh_token_str}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        log_login_failure(
            db=db,
            request=request,
            username='unknown',
            reason=f"OAuth error: {str(e)}",
        )
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")


@router.get("/github/login")
async def github_login(request: Request):
    """
    Initiate GitHub OAuth login flow.

    Redirects user to GitHub authorization page.
    """
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle GitHub OAuth callback.

    Processes the OAuth response and creates/updates user.
    """
    try:
        # Get token from GitHub
        token = await oauth.github.authorize_access_token(request)

        # Get user data from GitHub API
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f"token {token['access_token']}",
                'Accept': 'application/vnd.github.v3+json',
            }

            # Get user info
            user_response = await client.get('https://api.github.com/user', headers=headers)
            user_data = user_response.json()

            # Get user emails
            emails_response = await client.get('https://api.github.com/user/emails', headers=headers)
            email_data = emails_response.json()

        # Extract user info
        user_info = extract_github_user_info(user_data, email_data)

        # Ensure username is unique
        username = generate_unique_username(db, user_info['username'])
        user_info['username'] = username

        # Create or update user
        user = create_or_update_oauth_user(
            db=db,
            provider='github',
            oauth_id=user_info['oauth_id'],
            email=user_info['email'],
            username=user_info['username'],
            full_name=user_info.get('full_name'),
            avatar_url=user_info.get('avatar_url'),
        )

        # Check account lockout
        is_locked, lock_message = check_account_lockout(user)
        if is_locked:
            log_login_failure(
                db=db,
                request=request,
                username=user.username,
                reason="Account locked",
                user_id=user.id,
            )
            raise HTTPException(status_code=403, detail=lock_message)

        # Create tokens
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }

        access_token = create_access_token(token_data)
        refresh_token_str = create_refresh_token(token_data)

        # Store refresh token
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

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Log successful OAuth login
        log_oauth_login(
            db=db,
            request=request,
            user_id=user.id,
            username=user.username,
            provider='github',
        )

        # Redirect to frontend with tokens
        frontend_url = request.url_for('root').replace('/api/v1/auth/oauth/github/callback', '')
        redirect_url = f"{frontend_url}/?access_token={access_token}&refresh_token={refresh_token_str}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        log_login_failure(
            db=db,
            request=request,
            username='unknown',
            reason=f"OAuth error: {str(e)}",
        )
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
