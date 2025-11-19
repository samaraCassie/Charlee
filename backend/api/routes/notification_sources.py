"""API routes for managing notification sources (external integrations)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User
from services.agents import NotificationAgent

router = APIRouter()


@router.get("/", response_model=schemas.NotificationSourceListResponse)
def get_notification_sources(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all notification sources for the current user.

    Returns:
        List of notification sources with statistics
    """
    sources = crud.get_notification_sources(db, user_id=current_user.id, skip=skip, limit=limit)
    return {"total": len(sources), "sources": sources}


@router.get("/{source_id}", response_model=schemas.NotificationSourceResponse)
def get_notification_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific notification source by ID.

    Args:
        source_id: ID of the source

    Returns:
        Notification source details

    Raises:
        404: Source not found
    """
    source = crud.get_notification_source(db, source_id=source_id, user_id=current_user.id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification source {source_id} not found",
        )
    return source


@router.post(
    "/", response_model=schemas.NotificationSourceResponse, status_code=status.HTTP_201_CREATED
)
def create_notification_source(
    source: schemas.NotificationSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new notification source.

    Args:
        source: Source configuration (type, credentials, settings)

    Returns:
        Created notification source

    Note:
        Credentials should be encrypted by the client before sending
    """
    db_source = crud.create_notification_source(db, source=source, user_id=current_user.id)
    return db_source


@router.patch("/{source_id}", response_model=schemas.NotificationSourceResponse)
def update_notification_source(
    source_id: int,
    source_update: schemas.NotificationSourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a notification source.

    Args:
        source_id: ID of the source to update
        source_update: Fields to update

    Returns:
        Updated notification source

    Raises:
        404: Source not found
    """
    db_source = crud.update_notification_source(
        db, source_id=source_id, user_id=current_user.id, source_update=source_update
    )
    if not db_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification source {source_id} not found",
        )
    return db_source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a notification source.

    Args:
        source_id: ID of the source to delete

    Raises:
        404: Source not found
    """
    success = crud.delete_notification_source(db, source_id=source_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification source {source_id} not found",
        )


@router.post("/{source_id}/sync", response_model=dict)
def sync_notification_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger a sync for a notification source.

    Args:
        source_id: ID of the source to sync

    Returns:
        Sync results (collected count, spam filtered, errors)

    Raises:
        404: Source not found
    """
    # Verify source exists and belongs to user
    source = crud.get_notification_source(db, source_id=source_id, user_id=current_user.id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification source {source_id} not found",
        )

    # Trigger collection
    agent = NotificationAgent(db)
    try:
        result = agent.collect_from_source(source_id)
        return {
            "success": True,
            "collected": result["collected"],
            "spam_filtered": result["spam_filtered"],
            "errors": result["errors"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing source: {str(e)}",
        )


@router.post("/sync-all", response_model=dict)
def sync_all_sources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sync all enabled notification sources for the current user.

    Returns:
        Aggregated sync results
    """
    agent = NotificationAgent(db)
    try:
        result = agent.collect_from_all_sources(user_id=current_user.id)
        return {
            "success": True,
            "sources_processed": result["sources_processed"],
            "total_collected": result["total_collected"],
            "total_spam_filtered": result["total_spam_filtered"],
            "errors": result["errors"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing sources: {str(e)}",
        )
