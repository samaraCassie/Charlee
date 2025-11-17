"""API routes for managing task attachments."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database.config import get_db
from database.models import Attachment, Task, User
from database.schemas import AttachmentResponse

router = APIRouter()


@router.get("/tasks/{task_id}/attachments", response_model=List[AttachmentResponse])
async def get_task_attachments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all attachments for a specific task.

    Args:
        task_id: ID of the task
        db: Database session
        current_user: Authenticated user

    Returns:
        List of attachments

    Raises:
        HTTPException: If task not found or user doesn't own the task
    """
    # Verify task exists and belongs to user
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it",
        )

    # Get all attachments for the task
    attachments = (
        db.query(Attachment)
        .filter(Attachment.task_id == task_id)
        .order_by(Attachment.created_at.desc())
        .all()
    )

    return attachments


@router.get("/attachments", response_model=List[AttachmentResponse])
async def get_all_user_attachments(
    file_type: Optional[str] = Query(None, description="Filter by file type: 'audio' or 'image'"),
    task_id: Optional[int] = Query(None, description="Filter by task ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of attachments to return"),
    offset: int = Query(0, ge=0, description="Number of attachments to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all attachments for the current user with optional filtering.

    This endpoint is useful for:
    - Transcription history page
    - Analytics dashboard
    - Searching across all attachments

    Args:
        file_type: Optional filter by 'audio' or 'image'
        task_id: Optional filter by task ID
        limit: Maximum number of results (default 100, max 500)
        offset: Pagination offset (default 0)
        db: Database session
        current_user: Authenticated user

    Returns:
        List of attachments belonging to the user's tasks
    """
    # Build query to get attachments from user's tasks
    query = (
        db.query(Attachment)
        .join(Task, Attachment.task_id == Task.id)
        .filter(Task.user_id == current_user.id)
    )

    # Apply filters
    if file_type:
        if file_type not in ["audio", "image"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file_type must be 'audio' or 'image'",
            )
        query = query.filter(Attachment.file_type == file_type)

    if task_id:
        # Verify task belongs to user
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or you don't have permission to access it",
            )
        query = query.filter(Attachment.task_id == task_id)

    # Order by most recent first
    query = query.order_by(Attachment.created_at.desc())

    # Apply pagination
    attachments = query.offset(offset).limit(limit).all()

    return attachments


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific attachment by ID.

    Args:
        attachment_id: ID of the attachment
        db: Database session
        current_user: Authenticated user

    Returns:
        Attachment details

    Raises:
        HTTPException: If attachment not found or user doesn't own it
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    # Verify user owns the task that this attachment belongs to
    task = db.query(Task).filter(Task.id == attachment.task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this attachment",
        )

    return attachment


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an attachment.

    Args:
        attachment_id: ID of the attachment to delete
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If attachment not found or user doesn't own it
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    # Verify user owns the task
    task = db.query(Task).filter(Task.id == attachment.task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this attachment",
        )

    # Delete attachment
    db.delete(attachment)
    db.commit()


@router.post("/attachments/{attachment_id}/reprocess", response_model=AttachmentResponse)
async def reprocess_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reprocess an attachment (re-transcribe audio or re-analyze image).

    Args:
        attachment_id: ID of the attachment to reprocess
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated attachment with new processed text

    Raises:
        HTTPException: If attachment not found or user doesn't own it
    """
    from multimodal.audio_service import get_audio_service
    from multimodal.vision_service import get_vision_service
    import os

    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    # Verify user owns the task
    task = db.query(Task).filter(Task.id == attachment.task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reprocess this attachment",
        )

    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment file not found on server",
        )

    try:
        # Reprocess based on file type
        if attachment.file_type == "audio":
            audio_service = get_audio_service()
            with open(attachment.file_path, "rb") as f:
                result = audio_service.transcribe_audio(f, attachment.file_name, language=None)
                attachment.processed_text = result["text"]

        elif attachment.file_type == "image":
            vision_service = get_vision_service()
            with open(attachment.file_path, "rb") as f:
                result = vision_service.analyze_image(f, attachment.file_name)
                attachment.processed_text = result["analysis"]

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {attachment.file_type}",
            )

        db.commit()
        db.refresh(attachment)

        return attachment

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reprocess attachment: {str(e)}",
        )


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download an attachment file.

    Args:
        attachment_id: ID of the attachment to download
        db: Database session
        current_user: Authenticated user

    Returns:
        File response with attachment

    Raises:
        HTTPException: If attachment not found or user doesn't own it
    """
    from fastapi.responses import FileResponse
    import os

    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    # Verify user owns the task
    task = db.query(Task).filter(Task.id == attachment.task_id).first()
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to download this attachment",
        )

    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment file not found on server",
        )

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type="application/octet-stream",
    )
