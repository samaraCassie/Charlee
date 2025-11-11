"""Tasks API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database.config import get_db
from database import crud, schemas

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.TaskListResponse,
    summary="List all tasks",
    description="""
    Retrieve a list of tasks with optional filtering.

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
    db: Session = Depends(get_db),
):
    """Get list of Tasks with optional filters."""
    tasks = crud.get_tasks(
        db, skip=skip, limit=limit, status=status, big_rock_id=big_rock_id, task_type=task_type
    )
    return {"total": len(tasks), "tasks": tasks}


@router.get(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Get task by ID",
    description="Retrieve a single task by its unique ID.",
    responses={
        200: {"description": "Task found and returned"},
        404: {"description": "Task not found"},
    },
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single Task by ID."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/",
    response_model=schemas.TaskResponse,
    status_code=201,
    summary="Create new task",
    description="""
    Create a new task with optional Big Rock association.

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
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new Task."""
    try:
        return crud.create_task(db, task)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Update task",
    description="Partially update a task. Only provided fields will be updated.",
    responses={
        200: {"description": "Task updated successfully"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a Task."""
    task = crud.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/{task_id}/complete",
    response_model=schemas.TaskResponse,
    summary="Mark task as completed",
    description="Mark a task as completed and set completion timestamp.",
    responses={
        200: {"description": "Task marked as completed"},
        404: {"description": "Task not found"},
    },
)
def mark_task_completed(task_id: int, db: Session = Depends(get_db)):
    """Mark a Task as completed."""
    task = crud.mark_task_completed(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/{task_id}/reopen",
    response_model=schemas.TaskResponse,
    summary="Reopen completed task",
    description="Reopen a completed task and reset its status to pending.",
    responses={
        200: {"description": "Task reopened successfully"},
        404: {"description": "Task not found"},
    },
)
def reopen_task(task_id: int, db: Session = Depends(get_db)):
    """Reopen a completed Task."""
    task = crud.reopen_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete task",
    description="Permanently delete a task. This action cannot be undone.",
    responses={
        204: {"description": "Task deleted successfully"},
        404: {"description": "Task not found"},
    },
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a Task permanently."""
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
