"""OAuth utilities for Google and GitHub authentication."""

from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session
from database.models import User
from api.auth.password import hash_password
import secrets

# OAuth configuration
config = Config(
    environ={
        "GOOGLE_CLIENT_ID": "",
        "GOOGLE_CLIENT_SECRET": "",
        "GITHUB_CLIENT_ID": "",
        "GITHUB_CLIENT_SECRET": "",
    }
)

oauth = OAuth(config)

# Register Google OAuth
oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID", default=""),
    client_secret=config("GOOGLE_CLIENT_SECRET", default=""),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Register GitHub OAuth
oauth.register(
    name="github",
    client_id=config("GITHUB_CLIENT_ID", default=""),
    client_secret=config("GITHUB_CLIENT_SECRET", default=""),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


def create_or_update_oauth_user(
    db: Session,
    provider: str,
    oauth_id: str,
    email: str,
    username: str,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    """
    Create or update user from OAuth provider data.

    Args:
        db: Database session
        provider: OAuth provider name ('google' or 'github')
        oauth_id: User ID from OAuth provider
        email: User email
        username: Username (generated if needed)
        full_name: Optional full name
        avatar_url: Optional avatar URL

    Returns:
        User instance
    """
    # Check if user exists with this OAuth provider
    user = db.query(User).filter(User.oauth_provider == provider, User.oauth_id == oauth_id).first()

    if user:
        # Update existing OAuth user
        user.email = email
        user.full_name = full_name
        user.avatar_url = avatar_url
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user

    # Check if user exists with this email (local account)
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        # Link OAuth to existing local account
        existing_user.oauth_provider = provider
        existing_user.oauth_id = oauth_id
        existing_user.avatar_url = avatar_url
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # Create new OAuth user
    # Generate random password for OAuth users (they won't use it)
    random_password = secrets.token_urlsafe(32)

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(random_password),
        full_name=full_name,
        oauth_provider=provider,
        oauth_id=oauth_id,
        avatar_url=avatar_url,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def extract_google_user_info(token: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user information from Google OAuth token.

    Args:
        token: OAuth token data from Google

    Returns:
        Dictionary with user information
    """
    user_info = token.get("userinfo", {})

    return {
        "oauth_id": user_info.get("sub"),
        "email": user_info.get("email"),
        "username": user_info.get("email", "").split("@")[0],  # Use email prefix as username
        "full_name": user_info.get("name"),
        "avatar_url": user_info.get("picture"),
    }


def extract_github_user_info(user_data: Dict[str, Any], email_data: list) -> Dict[str, Any]:
    """
    Extract user information from GitHub OAuth data.

    Args:
        user_data: User data from GitHub API
        email_data: Email data from GitHub API

    Returns:
        Dictionary with user information
    """
    # Get primary email
    primary_email = None
    for email in email_data:
        if email.get("primary"):
            primary_email = email.get("email")
            break

    if not primary_email and email_data:
        primary_email = email_data[0].get("email")

    return {
        "oauth_id": str(user_data.get("id")),
        "email": primary_email or user_data.get("email"),
        "username": user_data.get("login"),
        "full_name": user_data.get("name"),
        "avatar_url": user_data.get("avatar_url"),
    }


def generate_unique_username(db: Session, base_username: str) -> str:
    """
    Generate a unique username by appending numbers if needed.

    Args:
        db: Database session
        base_username: Base username to start with

    Returns:
        Unique username
    """
    username = base_username
    counter = 1

    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    return username
