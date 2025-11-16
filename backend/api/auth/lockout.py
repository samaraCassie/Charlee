"""Account lockout utilities."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from database.models import User


class LockoutConfig:
    """Account lockout configuration."""

    MAX_FAILED_ATTEMPTS: int = 5  # Maximum failed login attempts
    LOCKOUT_DURATION_MINUTES: int = 30  # Lockout duration in minutes
    RESET_ATTEMPTS_AFTER_HOURS: int = 24  # Reset counter after this many hours


def check_account_lockout(user: User) -> tuple[bool, Optional[str]]:
    """
    Check if user account is locked.

    Args:
        user: User instance

    Returns:
        Tuple of (is_locked: bool, message: Optional[str])
    """
    if user.is_locked():
        # Ensure locked_until is timezone-aware
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)

        remaining_time = locked_until - datetime.now(timezone.utc)
        minutes_remaining = int(remaining_time.total_seconds() / 60)
        return True, f"Account is locked. Try again in {minutes_remaining} minutes."

    return False, None


def record_failed_login(db: Session, user: User) -> tuple[bool, int]:
    """
    Record a failed login attempt and lock account if threshold is reached.

    Args:
        db: Database session
        user: User instance

    Returns:
        Tuple of (is_now_locked: bool, remaining_attempts: int)
    """
    # Reset counter if last failed attempt was more than 24 hours ago
    if user.last_failed_login:
        # Ensure last_failed_login is timezone-aware
        last_failed = user.last_failed_login
        if last_failed.tzinfo is None:
            last_failed = last_failed.replace(tzinfo=timezone.utc)

        hours_since_last_failure = (datetime.now(timezone.utc) - last_failed).total_seconds() / 3600

        if hours_since_last_failure > LockoutConfig.RESET_ATTEMPTS_AFTER_HOURS:
            user.failed_login_attempts = 0

    # Increment failed attempts
    user.failed_login_attempts += 1
    user.last_failed_login = datetime.now(timezone.utc)

    # Check if threshold is reached
    remaining_attempts = LockoutConfig.MAX_FAILED_ATTEMPTS - user.failed_login_attempts

    if user.failed_login_attempts >= LockoutConfig.MAX_FAILED_ATTEMPTS:
        # Lock the account
        user.locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=LockoutConfig.LOCKOUT_DURATION_MINUTES
        )
        db.commit()
        return True, 0

    db.commit()
    return False, remaining_attempts


def unlock_account(db: Session, user: User) -> None:
    """
    Manually unlock a user account.

    Args:
        db: Database session
        user: User instance
    """
    user.reset_failed_attempts()
    db.commit()


def record_successful_login(db: Session, user: User) -> None:
    """
    Record successful login and reset failed attempts.

    Args:
        db: Database session
        user: User instance
    """
    user.reset_failed_attempts()
    user.last_login = datetime.now(timezone.utc)
    db.commit()
