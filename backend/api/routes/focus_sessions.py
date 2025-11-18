"""
API routes for focus sessions.

Endpoints for managing focus mode sessions that suppress notifications.
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/focus", tags=["Focus Sessions"])


@router.post(
    "/start", response_model=schemas.FocusSessionResponse, status_code=status.HTTP_201_CREATED
)
def start_focus_session(
    session: schemas.FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a new focus session.

    During a focus session, notifications can be suppressed or delivered
    only for certain categories (e.g., only 'urgente').
    """
    # Check if there's already an active focus session
    active_session = crud.get_active_focus_session(db, user_id=current_user.id)

    if active_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Focus session already active (started at {active_session.start_time}). "
            "End the current session before starting a new one.",
        )

    try:
        db_session = crud.create_focus_session(db, session=session, user_id=current_user.id)
        logger.info(f"Started focus session {db_session.id} for user {current_user.id}")
        return db_session

    except Exception as e:
        logger.error(f"Error starting focus session for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start focus session: {str(e)}",
        )


@router.post("/end", response_model=schemas.FocusSessionResponse)
def end_focus_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    End the currently active focus session.

    Returns the ended session with calculated duration.
    """
    active_session = crud.get_active_focus_session(db, user_id=current_user.id)

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active focus session found"
        )

    try:
        # End the session
        active_session.end_time = datetime.now(timezone.utc)
        db.commit()
        db.refresh(active_session)

        logger.info(f"Ended focus session {active_session.id} for user {current_user.id}")

        return active_session

    except Exception as e:
        logger.error(f"Error ending focus session for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end focus session: {str(e)}",
        )


@router.get("/active", response_model=schemas.FocusSessionResponse)
def get_active_focus_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the currently active focus session.

    Returns 404 if no focus session is currently active.
    """
    active_session = crud.get_active_focus_session(db, user_id=current_user.id)

    if not active_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active focus session")

    return active_session


@router.get("/history", response_model=List[schemas.FocusSessionResponse])
def get_focus_session_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get focus session history.

    Returns paginated list of past focus sessions, ordered by start time (newest first).
    """
    sessions = crud.get_focus_sessions(db, user_id=current_user.id, skip=skip, limit=limit)
    return sessions
