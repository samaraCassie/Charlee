"""JWT token utilities for access and refresh tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from database.config import settings


class TokenData(BaseModel):
    """Token data extracted from JWT."""

    user_id: int
    username: str
    email: str
    token_type: str  # "access" or "refresh"


class JWTConfig:
    """JWT configuration loaded from environment variables."""

    SECRET_KEY: str = settings.jwt_secret_key
    REFRESH_SECRET_KEY: str = settings.jwt_refresh_secret_key
    ALGORITHM: str = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.jwt_access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = settings.jwt_refresh_token_expire_days


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user data to encode
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Dictionary containing user data to encode
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWTConfig.REFRESH_SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        TokenData if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        token_type: str = payload.get("token_type")

        if user_id is None or username is None or token_type != "access":
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            token_type=token_type,
        )
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify a JWT refresh token.

    Args:
        token: JWT refresh token string to decode

    Returns:
        TokenData if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWTConfig.REFRESH_SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        token_type: str = payload.get("token_type")

        if user_id is None or username is None or token_type != "refresh":
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            token_type=token_type,
        )
    except JWTError:
        return None
