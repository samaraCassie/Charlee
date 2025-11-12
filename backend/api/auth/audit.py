"""Audit logging utilities for authentication events."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from database.models import AuditLog


def log_auth_event(
    db: Session,
    event_type: str,
    event_status: str,
    request: Request,
    user_id: Optional[int] = None,
    event_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Log an authentication event to the audit log.

    Args:
        db: Database session
        event_type: Type of event ('login', 'logout', 'register', 'password_change', etc.)
        event_status: Status of event ('success', 'failure', 'blocked')
        request: FastAPI request object
        user_id: Optional user ID
        event_message: Optional descriptive message
        metadata: Optional additional data

    Returns:
        Created AuditLog instance
    """
    audit_log = AuditLog(
        user_id=user_id,
        event_type=event_type,
        event_status=event_status,
        event_message=event_message,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_path=str(request.url.path),
        metadata=metadata,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def log_login_success(db: Session, request: Request, user_id: int, username: str) -> None:
    """Log successful login."""
    log_auth_event(
        db=db,
        event_type="login",
        event_status="success",
        request=request,
        user_id=user_id,
        event_message=f"User '{username}' logged in successfully",
    )


def log_login_failure(
    db: Session,
    request: Request,
    username: str,
    reason: str,
    user_id: Optional[int] = None,
) -> None:
    """Log failed login attempt."""
    log_auth_event(
        db=db,
        event_type="login",
        event_status="failure",
        request=request,
        user_id=user_id,
        event_message=f"Failed login attempt for '{username}': {reason}",
        metadata={"username": username, "reason": reason},
    )


def log_account_locked(db: Session, request: Request, user_id: int, username: str) -> None:
    """Log account lockout."""
    log_auth_event(
        db=db,
        event_type="account_locked",
        event_status="blocked",
        request=request,
        user_id=user_id,
        event_message=f"Account '{username}' locked due to multiple failed login attempts",
    )


def log_registration(db: Session, request: Request, user_id: int, username: str) -> None:
    """Log new user registration."""
    log_auth_event(
        db=db,
        event_type="register",
        event_status="success",
        request=request,
        user_id=user_id,
        event_message=f"New user '{username}' registered",
    )


def log_logout(db: Session, request: Request, user_id: int, username: str) -> None:
    """Log user logout."""
    log_auth_event(
        db=db,
        event_type="logout",
        event_status="success",
        request=request,
        user_id=user_id,
        event_message=f"User '{username}' logged out",
    )


def log_password_change(db: Session, request: Request, user_id: int, username: str) -> None:
    """Log password change."""
    log_auth_event(
        db=db,
        event_type="password_change",
        event_status="success",
        request=request,
        user_id=user_id,
        event_message=f"User '{username}' changed password",
    )


def log_oauth_login(
    db: Session,
    request: Request,
    user_id: int,
    username: str,
    provider: str,
) -> None:
    """Log OAuth login."""
    log_auth_event(
        db=db,
        event_type="oauth_login",
        event_status="success",
        request=request,
        user_id=user_id,
        event_message=f"User '{username}' logged in via {provider}",
        metadata={"provider": provider},
    )
