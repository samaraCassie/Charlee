"""
API routes for notification digests.

Endpoints for generating and managing notification digest summaries.
"""

import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.jwt import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User
from services.digest_service import DigestService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/notifications/digests", tags=["Notification Digests"])


@router.get("/", response_model=List[schemas.NotificationDigestResponse])
def list_digests(
    digest_type: str = Query(None, description="Filter by digest type (daily, weekly, monthly)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List notification digests for the current user.

    Returns paginated list of digests, optionally filtered by type.
    """
    digests = crud.get_notification_digests(
        db, user_id=current_user.id, digest_type=digest_type, skip=skip, limit=limit
    )
    return digests


@router.get("/{digest_id}", response_model=schemas.NotificationDigestResponse)
def get_digest(
    digest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific notification digest by ID."""
    digest = crud.get_notification_digest(db, digest_id=digest_id, user_id=current_user.id)

    if not digest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digest not found")

    return digest


@router.post(
    "/generate",
    response_model=schemas.NotificationDigestResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_digest(
    digest_type: str = Query(
        ..., description="Type of digest to generate (daily, weekly, monthly)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually generate a notification digest.

    Generates a summary of recent notifications using AI.
    Available types: daily, weekly, monthly.
    """
    if digest_type not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid digest_type. Must be one of: daily, weekly, monthly",
        )

    try:
        service = DigestService(db)
        digest = service.generate_digest(user_id=current_user.id, digest_type=digest_type)

        logger.info(f"Generated {digest_type} digest for user {current_user.id}: {digest.id}")

        return digest

    except Exception as e:
        logger.error(f"Error generating digest for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate digest: {str(e)}",
        )


@router.get("/latest/{digest_type}", response_model=schemas.NotificationDigestResponse)
def get_latest_digest(
    digest_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest digest of a specific type."""
    if digest_type not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid digest_type. Must be one of: daily, weekly, monthly",
        )

    digest = crud.get_latest_digest(db, user_id=current_user.id, digest_type=digest_type)

    if not digest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No {digest_type} digest found"
        )

    return digest
