"""Notification API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.NotificationListResponse,
    summary="List notifications",
    description="""
    Retrieve a list of notifications for the authenticated user with optional filtering.

    **Filters:**
    - `unread_only`: Only show unread notifications
    - `notification_type`: Filter by specific notification type
    - `skip`: Number of records to skip (pagination)
    - `limit`: Maximum number of records to return (max: 100)

    **Returns:** List of notifications ordered by creation date (descending)
    """,
)
def get_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of notifications for authenticated user with optional filters."""
    notifications = crud.get_notifications(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        notification_type=notification_type,
    )

    unread_count = crud.count_unread_notifications(db, user_id=current_user.id)

    return {
        "total": len(notifications),
        "unread_count": unread_count,
        "notifications": notifications,
    }


@router.get(
    "/{notification_id}",
    response_model=schemas.NotificationResponse,
    summary="Get notification by ID",
    description="Retrieve a single notification by its unique ID for the authenticated user.",
    responses={
        200: {"description": "Notification found and returned"},
        404: {"description": "Notification not found"},
    },
)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single notification by ID for authenticated user."""
    notification = crud.get_notification(db, notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=schemas.NotificationResponse,
    summary="Mark notification as read",
    description="Mark a specific notification as read for the authenticated user.",
    responses={
        200: {"description": "Notification marked as read"},
        404: {"description": "Notification not found"},
    },
)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single notification as read."""
    notification = crud.mark_notification_as_read(db, notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    logger.info(
        f"Notification {notification_id} marked as read",
        extra={
            "notification_id": notification_id,
            "user_id": current_user.id,
        },
    )

    return notification


@router.post(
    "/mark-all-read",
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="Mark all unread notifications as read for the authenticated user.",
    responses={
        200: {"description": "All notifications marked as read"},
    },
)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read for authenticated user."""
    updated_count = crud.mark_all_notifications_as_read(db, user_id=current_user.id)

    logger.info(
        f"Marked {updated_count} notifications as read",
        extra={
            "user_id": current_user.id,
            "updated_count": updated_count,
        },
    )

    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count,
    }


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
    description="Delete a specific notification for the authenticated user.",
    responses={
        204: {"description": "Notification deleted successfully"},
        404: {"description": "Notification not found"},
    },
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a notification for authenticated user."""
    success = crud.delete_notification(db, notification_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    logger.info(
        f"Notification {notification_id} deleted",
        extra={
            "notification_id": notification_id,
            "user_id": current_user.id,
        },
    )

    return None


# ==================== Notification Preferences ====================


@router.get(
    "/preferences/",
    response_model=schemas.NotificationPreferenceListResponse,
    summary="List notification preferences",
    description="""
    Retrieve notification preferences for the authenticated user.
    Creates default preferences if none exist.
    """,
)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all notification preferences for authenticated user."""
    # Get or create default preferences
    preferences = crud.get_or_create_default_preferences(db, user_id=current_user.id)

    return {
        "total": len(preferences),
        "preferences": preferences,
    }


@router.get(
    "/preferences/{notification_type}",
    response_model=schemas.NotificationPreferenceResponse,
    summary="Get notification preference by type",
    description="Retrieve notification preference for a specific type.",
    responses={
        200: {"description": "Preference found and returned"},
        404: {"description": "Preference not found"},
    },
)
def get_notification_preference(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single notification preference by type for authenticated user."""
    preference = crud.get_notification_preference(db, current_user.id, notification_type)
    if not preference:
        raise HTTPException(status_code=404, detail="Notification preference not found")
    return preference


@router.post(
    "/preferences/",
    response_model=schemas.NotificationPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification preference",
    description="Create a new notification preference for the authenticated user.",
    responses={
        201: {"description": "Preference created successfully"},
        409: {"description": "Preference already exists for this type"},
    },
)
def create_notification_preference(
    preference: schemas.NotificationPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new notification preference for authenticated user."""
    # Check if preference already exists
    existing = crud.get_notification_preference(
        db, current_user.id, preference.notification_type
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Preference for {preference.notification_type} already exists",
        )

    new_preference = crud.create_notification_preference(db, preference, user_id=current_user.id)

    logger.info(
        f"Notification preference created: {preference.notification_type}",
        extra={
            "user_id": current_user.id,
            "notification_type": preference.notification_type,
        },
    )

    return new_preference


@router.patch(
    "/preferences/{notification_type}",
    response_model=schemas.NotificationPreferenceResponse,
    summary="Update notification preference",
    description="Update notification preference for a specific type.",
    responses={
        200: {"description": "Preference updated successfully"},
        404: {"description": "Preference not found"},
    },
)
def update_notification_preference(
    notification_type: str,
    preference_update: schemas.NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a notification preference for authenticated user."""
    updated_preference = crud.update_notification_preference(
        db, notification_type, preference_update, user_id=current_user.id
    )

    if not updated_preference:
        raise HTTPException(status_code=404, detail="Notification preference not found")

    logger.info(
        f"Notification preference updated: {notification_type}",
        extra={
            "user_id": current_user.id,
            "notification_type": notification_type,
        },
    )

    return updated_preference


@router.delete(
    "/preferences/{notification_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification preference",
    description="Delete notification preference for a specific type.",
    responses={
        204: {"description": "Preference deleted successfully"},
        404: {"description": "Preference not found"},
    },
)
def delete_notification_preference(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a notification preference for authenticated user."""
    success = crud.delete_notification_preference(db, notification_type, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification preference not found")

    logger.info(
        f"Notification preference deleted: {notification_type}",
        extra={
            "user_id": current_user.id,
            "notification_type": notification_type,
        },
    )

    return None
