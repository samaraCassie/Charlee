"""CRUD operations for database models."""

from typing import Optional, cast

from sqlalchemy.orm import Session

from database.models import BigRock, Task
from database.schemas import BigRockCreate, BigRockUpdate, TaskCreate, TaskUpdate

# ==================== Big Rock CRUD ====================


def get_big_rock(db: Session, big_rock_id: int, user_id: int) -> Optional[BigRock]:
    """Get a single BigRock by ID for a specific user."""
    return cast(
        Optional[BigRock],
        db.query(BigRock).filter(BigRock.id == big_rock_id, BigRock.user_id == user_id).first(),
    )


def get_big_rocks(
    db: Session, user_id: int, skip: int = 0, limit: int = 100, active_only: bool = False
) -> list[BigRock]:
    """Get list of BigRocks for a specific user."""
    query = db.query(BigRock).filter(BigRock.user_id == user_id)

    if active_only:
        query = query.filter(BigRock.active)

    return cast(list[BigRock], query.offset(skip).limit(limit).all())


def create_big_rock(db: Session, big_rock: BigRockCreate, user_id: int) -> BigRock:
    """Create a new BigRock for a specific user."""
    db_big_rock = BigRock(**big_rock.model_dump(), user_id=user_id)
    db.add(db_big_rock)
    db.commit()
    db.refresh(db_big_rock)
    return db_big_rock


def update_big_rock(
    db: Session, big_rock_id: int, big_rock_update: BigRockUpdate, user_id: int
) -> Optional[BigRock]:
    """Update a BigRock for a specific user."""
    db_big_rock = get_big_rock(db, big_rock_id, user_id)
    if not db_big_rock:
        return None

    update_data = big_rock_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_big_rock, field, value)

    db.commit()
    db.refresh(db_big_rock)
    return db_big_rock


def delete_big_rock(db: Session, big_rock_id: int, user_id: int) -> bool:
    """Delete a BigRock (soft delete by setting active=False) for a specific user."""
    db_big_rock = get_big_rock(db, big_rock_id, user_id)
    if not db_big_rock:
        return False

    db_big_rock.active = False  # type: ignore[assignment]
    db.commit()
    return True


# ==================== Task CRUD ====================


def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Get a single Task by ID for a specific user."""
    return cast(
        Optional[Task],
        db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first(),
    )


def get_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    big_rock_id: Optional[int] = None,
    task_type: Optional[str] = None,
) -> list[Task]:
    """Get list of Tasks for a specific user with optional filters."""
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    if big_rock_id:
        query = query.filter(Task.big_rock_id == big_rock_id)

    if task_type:
        query = query.filter(Task.type == task_type)

    return cast(
        list[Task], query.order_by(Task.deadline.asc().nullslast()).offset(skip).limit(limit).all()
    )


def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    """Create a new Task for a specific user.

    Args:
        db: Database session
        task: Task data
        user_id: User ID

    Returns:
        Created task

    Raises:
        ValueError: If big_rock_id is provided but doesn't exist
    """
    # Validate big_rock_id if provided
    if task.big_rock_id is not None:
        big_rock = get_big_rock(db, task.big_rock_id, user_id)
        if not big_rock:
            raise ValueError(f"BigRock with id {task.big_rock_id} not found")

    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
    """Update a Task for a specific user."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def mark_task_completed(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Mark a Task as completed for a specific user."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None

    db_task.mark_as_completed()
    db.commit()
    db.refresh(db_task)
    return db_task


def reopen_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Reopen a completed Task for a specific user."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None

    db_task.reopen()
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """Delete a Task permanently for a specific user."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True
