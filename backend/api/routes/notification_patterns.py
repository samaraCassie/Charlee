"""
API routes for notification patterns.

Endpoints for viewing learned notification patterns and insights.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.jwt import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/notifications/patterns", tags=["Notification Patterns"])


@router.get("/", response_model=List[schemas.NotificationPatternResponse])
def list_notification_patterns(
    pattern_key: str = Query(None, description="Filter by pattern key"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List learned notification patterns for the current user.

    Patterns are automatically learned from notification history and
    AI classification to improve future classification accuracy.

    Returns paginated list of patterns, optionally filtered by pattern_key.
    """
    patterns = crud.get_notification_patterns(
        db, user_id=current_user.id, pattern_key=pattern_key, skip=skip, limit=limit
    )
    return patterns


@router.get("/{pattern_id}", response_model=schemas.NotificationPatternResponse)
def get_notification_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific notification pattern by ID."""
    pattern = crud.get_notification_pattern(db, pattern_id=pattern_id, user_id=current_user.id)

    if not pattern:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pattern not found")

    return pattern


@router.get("/insights/summary", response_model=dict)
def get_pattern_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary insights from learned notification patterns.

    Returns aggregated statistics and insights about notification patterns.
    """
    patterns = crud.get_notification_patterns(db, user_id=current_user.id, skip=0, limit=1000)

    if not patterns:
        return {
            "total_patterns": 0,
            "most_confident_patterns": [],
            "most_frequent_patterns": [],
            "average_confidence": 0.0,
        }

    # Calculate insights
    total_patterns = len(patterns)
    average_confidence = (
        sum(p.confidence for p in patterns) / total_patterns if total_patterns > 0 else 0.0
    )

    # Most confident patterns
    most_confident = sorted(patterns, key=lambda p: p.confidence, reverse=True)[:5]
    most_confident_data = [
        {
            "pattern_key": p.pattern_key,
            "pattern_type": p.pattern_type,
            "confidence": p.confidence,
            "frequency": p.frequency,
        }
        for p in most_confident
    ]

    # Most frequent patterns
    most_frequent = sorted(patterns, key=lambda p: p.frequency, reverse=True)[:5]
    most_frequent_data = [
        {
            "pattern_key": p.pattern_key,
            "pattern_type": p.pattern_type,
            "confidence": p.confidence,
            "frequency": p.frequency,
        }
        for p in most_frequent
    ]

    return {
        "total_patterns": total_patterns,
        "average_confidence": round(average_confidence, 3),
        "most_confident_patterns": most_confident_data,
        "most_frequent_patterns": most_frequent_data,
    }
