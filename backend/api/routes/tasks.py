"""Tasks API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database.config import get_db
from database import crud, schemas

router = APIRouter()


@router.get("/", response_model=schemas.TaskListResponse)
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


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single Task by ID."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new Task."""
    try:
        return crud.create_task(db, task)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a Task."""
    task = crud.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/complete", response_model=schemas.TaskResponse)
def mark_task_completed(task_id: int, db: Session = Depends(get_db)):
    """Mark a Task as completed."""
    task = crud.mark_task_completed(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/reopen", response_model=schemas.TaskResponse)
def reopen_task(task_id: int, db: Session = Depends(get_db)):
    """Reopen a completed Task."""
    task = crud.reopen_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a Task permanently."""
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
