"""Calendar integration API routes.

RESTful API endpoints for managing calendar connections and synchronization
with Google Calendar and Microsoft Outlook/Office 365.
"""

import logging
import secrets
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database.config import get_db
from database.models import (
    CalendarConflict,
    CalendarConnection,
    CalendarEvent,
    CalendarSyncLog,
    User,
)
from database.schemas import (
    CalendarConflictListResponse,
    CalendarConflictResponse,
    CalendarConnectionListResponse,
    CalendarConnectionResponse,
    CalendarConnectionUpdate,
    CalendarEventListResponse,
    CalendarEventResponse,
    CalendarOAuthCallback,
    CalendarSyncLogListResponse,
    CalendarSyncLogResponse,
    CalendarSyncRequest,
    GoogleCalendarAuthUrl,
    MicrosoftCalendarAuthUrl,
)
from integrations import google_calendar, microsoft_calendar

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/calendar", tags=["Calendar Integration"])


# ==================== OAuth Authorization ====================


@router.get(
    "/connect/google/auth-url",
    response_model=GoogleCalendarAuthUrl,
    summary="Get Google Calendar authorization URL",
)
async def get_google_auth_url(
    current_user: User = Depends(get_current_user),
) -> GoogleCalendarAuthUrl:
    """
    Generate Google Calendar OAuth authorization URL.

    Returns:
        GoogleCalendarAuthUrl: Authorization URL and state for CSRF protection

    Raises:
        HTTPException 500: If URL generation fails
    """
    try:
        state = secrets.token_urlsafe(32)
        redirect_uri = "http://localhost:3000/calendar/callback/google"  # TODO: from env

        auth_url = google_calendar.get_authorization_url(redirect_uri, state)

        logger.info(
            "Generated Google auth URL",
            extra={"user_id": current_user.id, "state": state[:8]},
        )

        return GoogleCalendarAuthUrl(auth_url=auth_url, state=state)

    except Exception as e:
        logger.error(
            "Failed to generate Google auth URL",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}",
        ) from e


@router.get(
    "/connect/microsoft/auth-url",
    response_model=MicrosoftCalendarAuthUrl,
    summary="Get Microsoft Calendar authorization URL",
)
async def get_microsoft_auth_url(
    current_user: User = Depends(get_current_user),
) -> MicrosoftCalendarAuthUrl:
    """
    Generate Microsoft Calendar OAuth authorization URL.

    Returns:
        MicrosoftCalendarAuthUrl: Authorization URL and state for CSRF protection

    Raises:
        HTTPException 500: If URL generation fails
    """
    try:
        state = secrets.token_urlsafe(32)
        redirect_uri = "http://localhost:3000/calendar/callback/microsoft"  # TODO: from env

        auth_url = microsoft_calendar.get_authorization_url(redirect_uri, state)

        logger.info(
            "Generated Microsoft auth URL",
            extra={"user_id": current_user.id, "state": state[:8]},
        )

        return MicrosoftCalendarAuthUrl(auth_url=auth_url, state=state)

    except Exception as e:
        logger.error(
            "Failed to generate Microsoft auth URL",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}",
        ) from e


@router.post(
    "/connect/google",
    response_model=CalendarConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect Google Calendar",
)
async def connect_google_calendar(
    callback: CalendarOAuthCallback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    Complete Google Calendar OAuth flow and create connection.

    Args:
        callback: OAuth callback with code and state
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarConnectionResponse: Created calendar connection

    Raises:
        HTTPException 400: If OAuth exchange fails
        HTTPException 500: If connection creation fails
    """
    try:
        redirect_uri = "http://localhost:3000/calendar/callback/google"  # TODO: from env

        # Exchange code for tokens
        token_info = google_calendar.exchange_code_for_tokens(callback.code, redirect_uri)

        # Get primary calendar ID
        # For now, use 'primary' - later we can let user choose
        calendar_id = "primary"

        # Create connection
        connection = CalendarConnection(
            user_id=current_user.id,
            provider="google",
            calendar_id=calendar_id,
            calendar_name="Primary Calendar",
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            token_expires_at=token_info.get("expiry"),
            sync_enabled=True,
            sync_direction="both",
        )

        db.add(connection)
        db.commit()
        db.refresh(connection)

        logger.info(
            "Google Calendar connected successfully",
            extra={"user_id": current_user.id, "connection_id": connection.id},
        )

        return connection

    except google_calendar.GoogleCalendarAuthError as e:
        logger.error(
            "Google OAuth error",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {str(e)}",
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to connect Google Calendar",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connection: {str(e)}",
        ) from e


@router.post(
    "/connect/microsoft",
    response_model=CalendarConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect Microsoft Calendar",
)
async def connect_microsoft_calendar(
    callback: CalendarOAuthCallback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    Complete Microsoft Calendar OAuth flow and create connection.

    Args:
        callback: OAuth callback with code and state
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarConnectionResponse: Created calendar connection

    Raises:
        HTTPException 400: If OAuth exchange fails
        HTTPException 500: If connection creation fails
    """
    try:
        redirect_uri = "http://localhost:3000/calendar/callback/microsoft"  # TODO: from env

        # Exchange code for tokens
        token_info = microsoft_calendar.exchange_code_for_tokens(callback.code, redirect_uri)

        # Get primary calendar ID
        # For Microsoft, we'll use a placeholder and update it after fetching calendars
        calendar_id = "primary"  # Will be updated with actual calendar ID

        # Create connection
        connection = CalendarConnection(
            user_id=current_user.id,
            provider="microsoft",
            calendar_id=calendar_id,
            calendar_name="Primary Calendar",
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            token_expires_at=token_info.get("expiry"),
            sync_enabled=True,
            sync_direction="both",
        )

        db.add(connection)
        db.commit()
        db.refresh(connection)

        logger.info(
            "Microsoft Calendar connected successfully",
            extra={"user_id": current_user.id, "connection_id": connection.id},
        )

        return connection

    except microsoft_calendar.MicrosoftCalendarAuthError as e:
        logger.error(
            "Microsoft OAuth error",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {str(e)}",
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to connect Microsoft Calendar",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connection: {str(e)}",
        ) from e


# ==================== Connection Management ====================


@router.get(
    "/connections",
    response_model=CalendarConnectionListResponse,
    summary="List calendar connections",
)
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> CalendarConnectionListResponse:
    """
    List all calendar connections for the current user.

    Args:
        current_user: Authenticated user
        db: Database session
        skip: Number of connections to skip
        limit: Maximum number of connections to return

    Returns:
        CalendarConnectionListResponse: List of calendar connections
    """
    connections = (
        db.query(CalendarConnection)
        .filter(CalendarConnection.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = (
        db.query(CalendarConnection).filter(CalendarConnection.user_id == current_user.id).count()
    )

    logger.info(
        "Listed calendar connections",
        extra={"user_id": current_user.id, "count": len(connections)},
    )

    return CalendarConnectionListResponse(total=total, connections=connections)


@router.get(
    "/connections/{connection_id}",
    response_model=CalendarConnectionResponse,
    summary="Get calendar connection",
)
async def get_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    Get a specific calendar connection.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarConnectionResponse: Calendar connection details

    Raises:
        HTTPException 404: If connection not found
        HTTPException 403: If connection doesn't belong to user
    """
    connection = db.query(CalendarConnection).filter(CalendarConnection.id == connection_id).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    if connection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return connection


@router.patch(
    "/connections/{connection_id}",
    response_model=CalendarConnectionResponse,
    summary="Update calendar connection",
)
async def update_connection(
    connection_id: int,
    update_data: CalendarConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    Update calendar connection settings.

    Args:
        connection_id: Connection ID
        update_data: Update data
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarConnectionResponse: Updated connection

    Raises:
        HTTPException 404: If connection not found
        HTTPException 403: If connection doesn't belong to user
    """
    connection = db.query(CalendarConnection).filter(CalendarConnection.id == connection_id).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    if connection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(connection, key, value)

    connection.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(connection)

    logger.info(
        "Updated calendar connection",
        extra={"user_id": current_user.id, "connection_id": connection_id},
    )

    return connection


@router.delete(
    "/connections/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete calendar connection",
)
async def delete_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a calendar connection.

    Args:
        connection_id: Connection ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 404: If connection not found
        HTTPException 403: If connection doesn't belong to user
    """
    connection = db.query(CalendarConnection).filter(CalendarConnection.id == connection_id).first()

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    if connection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(connection)
    db.commit()

    logger.info(
        "Deleted calendar connection",
        extra={"user_id": current_user.id, "connection_id": connection_id},
    )


# ==================== Calendar Events ====================


@router.get(
    "/events",
    response_model=CalendarEventListResponse,
    summary="List calendar events",
)
async def list_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    connection_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> CalendarEventListResponse:
    """
    List calendar events for the current user.

    Args:
        current_user: Authenticated user
        db: Database session
        connection_id: Optional filter by connection ID
        skip: Number of events to skip
        limit: Maximum number of events to return

    Returns:
        CalendarEventListResponse: List of calendar events
    """
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id)

    if connection_id:
        query = query.filter(CalendarEvent.connection_id == connection_id)

    events = query.offset(skip).limit(limit).all()

    total = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id).count()

    logger.info("Listed calendar events", extra={"user_id": current_user.id, "count": len(events)})

    return CalendarEventListResponse(total=total, events=events)


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    summary="Get calendar event",
)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarEventResponse:
    """
    Get a specific calendar event.

    Args:
        event_id: Event ID
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarEventResponse: Calendar event details

    Raises:
        HTTPException 404: If event not found
        HTTPException 403: If event doesn't belong to user
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return event


# ==================== Synchronization ====================


@router.post(
    "/sync",
    response_model=CalendarSyncLogResponse,
    summary="Trigger manual calendar sync",
)
async def trigger_sync(
    sync_request: CalendarSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarSyncLogResponse:
    """
    Manually trigger calendar synchronization.

    Args:
        sync_request: Sync request parameters
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarSyncLogResponse: Sync log entry

    Raises:
        HTTPException 404: If connection not found
        HTTPException 403: If connection doesn't belong to user
        HTTPException 500: If sync fails
    """
    connection = (
        db.query(CalendarConnection)
        .filter(CalendarConnection.id == sync_request.connection_id)
        .first()
    )

    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    if connection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Create sync log
    sync_log = CalendarSyncLog(
        connection_id=connection.id,
        user_id=current_user.id,
        sync_type="manual",
        direction=sync_request.direction,
        status="started",
        started_at=datetime.utcnow(),
    )

    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)

    try:
        # TODO: Trigger async Celery task for sync
        # For now, return the sync log with started status
        logger.info(
            "Triggered manual sync",
            extra={
                "user_id": current_user.id,
                "connection_id": connection.id,
                "sync_log_id": sync_log.id,
            },
        )

        return sync_log

    except Exception as e:
        sync_log.status = "failed"
        sync_log.error_message = str(e)
        sync_log.mark_completed("failed")
        db.commit()

        logger.error(
            "Manual sync failed",
            extra={
                "user_id": current_user.id,
                "connection_id": connection.id,
                "error": str(e),
            },
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        ) from e


@router.get(
    "/sync-logs",
    response_model=CalendarSyncLogListResponse,
    summary="List sync logs",
)
async def list_sync_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    connection_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> CalendarSyncLogListResponse:
    """
    List synchronization logs.

    Args:
        current_user: Authenticated user
        db: Database session
        connection_id: Optional filter by connection ID
        skip: Number of logs to skip
        limit: Maximum number of logs to return

    Returns:
        CalendarSyncLogListResponse: List of sync logs
    """
    query = db.query(CalendarSyncLog).filter(CalendarSyncLog.user_id == current_user.id)

    if connection_id:
        query = query.filter(CalendarSyncLog.connection_id == connection_id)

    logs = query.order_by(CalendarSyncLog.started_at.desc()).offset(skip).limit(limit).all()

    total = db.query(CalendarSyncLog).filter(CalendarSyncLog.user_id == current_user.id).count()

    logger.info("Listed sync logs", extra={"user_id": current_user.id, "count": len(logs)})

    return CalendarSyncLogListResponse(total=total, logs=logs)


# ==================== Conflicts ====================


@router.get(
    "/conflicts",
    response_model=CalendarConflictListResponse,
    summary="List calendar conflicts",
)
async def list_conflicts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> CalendarConflictListResponse:
    """
    List calendar synchronization conflicts.

    Args:
        current_user: Authenticated user
        db: Database session
        status_filter: Optional filter by conflict status
        skip: Number of conflicts to skip
        limit: Maximum number of conflicts to return

    Returns:
        CalendarConflictListResponse: List of conflicts
    """
    query = db.query(CalendarConflict).filter(CalendarConflict.user_id == current_user.id)

    if status_filter:
        query = query.filter(CalendarConflict.status == status_filter)

    conflicts = query.order_by(CalendarConflict.created_at.desc()).offset(skip).limit(limit).all()

    total = db.query(CalendarConflict).filter(CalendarConflict.user_id == current_user.id).count()

    logger.info("Listed conflicts", extra={"user_id": current_user.id, "count": len(conflicts)})

    return CalendarConflictListResponse(total=total, conflicts=conflicts)


@router.get(
    "/conflicts/{conflict_id}",
    response_model=CalendarConflictResponse,
    summary="Get calendar conflict",
)
async def get_conflict(
    conflict_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarConflictResponse:
    """
    Get a specific calendar conflict.

    Args:
        conflict_id: Conflict ID
        current_user: Authenticated user
        db: Database session

    Returns:
        CalendarConflictResponse: Conflict details

    Raises:
        HTTPException 404: If conflict not found
        HTTPException 403: If conflict doesn't belong to user
    """
    conflict = db.query(CalendarConflict).filter(CalendarConflict.id == conflict_id).first()

    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found")

    if conflict.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return conflict
