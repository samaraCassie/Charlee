"""Tasks API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database.config import get_db
from database import crud, schemas
from database.models import User
from api.cache import invalidate_pattern
from api.auth.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.TaskListResponse,
    summary="List all tasks",
    description="""
    Retrieve a list of tasks for the authenticated user with optional filtering.

    **Filters:**
    - `status`: Filter by task status (pending, in_progress, completed, cancelled)
    - `big_rock_id`: Filter by Big Rock association
    - `task_type`: Filter by type (fixed_appointment, task, continuous)
    - `skip`: Number of records to skip (pagination)
    - `limit`: Maximum number of records to return (max: 100)

    **Returns:** List of tasks ordered by deadline (ascending, nulls last)
    """,
)
def get_tasks(
    status: Optional[str] = None,
    big_rock_id: Optional[int] = None,
    task_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of Tasks for authenticated user with optional filters."""
    tasks = crud.get_tasks(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        big_rock_id=big_rock_id,
        task_type=task_type,
    )
    return {"total": len(tasks), "tasks": tasks}


@router.get(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Get task by ID",
    description="Retrieve a single task by its unique ID for the authenticated user.",
    responses={
        200: {"description": "Task found and returned"},
        404: {"description": "Task not found"},
    },
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single Task by ID for authenticated user."""
    task = crud.get_task(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/",
    response_model=schemas.TaskResponse,
    status_code=201,
    summary="Create new task",
    description="""
    Create a new task for the authenticated user with optional Big Rock association.

    **Required fields:**
    - `description`: Task description (min 1 char, max 5000 chars, HTML escaped)

    **Optional fields:**
    - `type`: Task type (fixed_appointment, task, continuous)
    - `deadline`: Due date in ISO format (YYYY-MM-DD)
    - `big_rock_id`: Associate with a Big Rock (validated)

    **Security:** All text inputs are sanitized to prevent XSS attacks.
    """,
    responses={
        201: {"description": "Task created successfully"},
        404: {"description": "Big Rock not found (if big_rock_id provided)"},
        422: {"description": "Validation error (invalid input)"},
    },
)
def create_task(
    task: schemas.TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new Task for authenticated user and invalidate cache."""
    try:
        result = crud.create_task(db, task, user_id=current_user.id)

        # Invalidate all task caches
        invalidate_pattern("tasks:*")

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Update task",
    description="Partially update a task for the authenticated user. Only provided fields will be updated.",
    responses={
        200: {"description": "Task updated successfully"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a Task for authenticated user and invalidate cache."""
    task = crud.update_task(db, task_id, task_update, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Invalidate all task caches
    invalidate_pattern("tasks:*")

    return task


@router.post(
    "/{task_id}/complete",
    response_model=schemas.TaskResponse,
    summary="Mark task as completed",
    description="Mark a task as completed and set completion timestamp for the authenticated user.",
    responses={
        200: {"description": "Task marked as completed"},
        404: {"description": "Task not found"},
    },
)
def mark_task_completed(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a Task as completed for authenticated user and invalidate cache."""
    task = crud.mark_task_completed(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Invalidate all task caches
    invalidate_pattern("tasks:*")

    return task


@router.post(
    "/{task_id}/reopen",
    response_model=schemas.TaskResponse,
    summary="Reopen completed task",
    description="Reopen a completed task and reset its status to pending for the authenticated user.",
    responses={
        200: {"description": "Task reopened successfully"},
        404: {"description": "Task not found"},
    },
)
def reopen_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reopen a completed Task for authenticated user and invalidate cache."""
    task = crud.reopen_task(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Invalidate all task caches
    invalidate_pattern("tasks:*")

    return task


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete task",
    description="Permanently delete a task for the authenticated user. This action cannot be undone.",
    responses={
        204: {"description": "Task deleted successfully"},
        404: {"description": "Task not found"},
    },
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a Task permanently for authenticated user and invalidate cache."""
    success = crud.delete_task(db, task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    # Invalidate all task caches
    invalidate_pattern("tasks:*")

    return None
