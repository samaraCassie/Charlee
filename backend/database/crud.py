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


# ==================== Freelance System CRUD ====================


def get_freelance_projects(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> list:
    """Get all freelance projects for a user with optional filters."""
    from database.models import FreelanceProject

    query = db.query(FreelanceProject).filter(FreelanceProject.user_id == user_id)

    if status:
        query = query.filter(FreelanceProject.status == status)

    return query.order_by(FreelanceProject.created_at.desc()).offset(skip).limit(limit).all()


def get_freelance_project(db: Session, project_id: int, user_id: int):
    """Get a specific freelance project by ID for a user."""
    from database.models import FreelanceProject

    return (
        db.query(FreelanceProject)
        .filter(FreelanceProject.id == project_id, FreelanceProject.user_id == user_id)
        .first()
    )


def create_freelance_project(db: Session, project_data, user_id: int):
    """Create a new freelance project for a user."""
    from database.models import FreelanceProject

    db_project = FreelanceProject(**project_data.model_dump(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_freelance_project(db: Session, project_id: int, project_update, user_id: int):
    """Update a freelance project for a user."""
    db_project = get_freelance_project(db, project_id, user_id)
    if not db_project:
        return None

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_freelance_project(db: Session, project_id: int, user_id: int) -> bool:
    """Delete a freelance project for a user."""
    db_project = get_freelance_project(db, project_id, user_id)
    if not db_project:
        return False

    db.delete(db_project)
    db.commit()
    return True


def get_work_logs(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list:
    """Get work logs for a user with optional project filter."""
    from database.models import WorkLog

    query = db.query(WorkLog).filter(WorkLog.user_id == user_id)

    if project_id:
        query = query.filter(WorkLog.project_id == project_id)

    return query.order_by(WorkLog.work_date.desc()).offset(skip).limit(limit).all()


def get_work_log(db: Session, log_id: int, user_id: int):
    """Get a specific work log by ID for a user."""
    from database.models import WorkLog

    return (
        db.query(WorkLog)
        .filter(WorkLog.id == log_id, WorkLog.user_id == user_id)
        .first()
    )


def create_work_log(db: Session, log_data, user_id: int):
    """Create a new work log for a user."""
    from database.models import WorkLog
    from datetime import date

    # Set work_date to today if not provided
    log_dict = log_data.model_dump()
    if not log_dict.get("work_date"):
        log_dict["work_date"] = date.today()

    db_log = WorkLog(**log_dict, user_id=user_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Update project actual hours
    project = get_freelance_project(db, db_log.project_id, user_id)
    if project:
        project.update_actual_hours(db)
        db.commit()

    return db_log


def update_work_log(db: Session, log_id: int, log_update, user_id: int):
    """Update a work log for a user."""
    db_log = get_work_log(db, log_id, user_id)
    if not db_log:
        return None

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)

    db.commit()
    db.refresh(db_log)

    # Update project actual hours
    project = get_freelance_project(db, db_log.project_id, user_id)
    if project:
        project.update_actual_hours(db)
        db.commit()

    return db_log


def delete_work_log(db: Session, log_id: int, user_id: int) -> bool:
    """Delete a work log for a user."""
    db_log = get_work_log(db, log_id, user_id)
    if not db_log:
        return False

    project_id = db_log.project_id
    db.delete(db_log)
    db.commit()

    # Update project actual hours
    project = get_freelance_project(db, project_id, user_id)
    if project:
        project.update_actual_hours(db)
        db.commit()

    return True


def get_invoices(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list:
    """Get invoices for a user with optional project filter."""
    from database.models import Invoice

    query = db.query(Invoice).filter(Invoice.user_id == user_id)

    if project_id:
        query = query.filter(Invoice.project_id == project_id)

    return query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()


def get_invoice(db: Session, invoice_id: int, user_id: int):
    """Get a specific invoice by ID for a user."""
    from database.models import Invoice

    return (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == user_id)
        .first()
    )


def create_invoice(db: Session, invoice_data, user_id: int):
    """Create a new invoice for a user."""
    from database.models import Invoice, WorkLog
    from datetime import date, timedelta

    project_id = invoice_data.project_id
    include_unbilled = invoice_data.include_unbilled_only

    # Get project
    project = get_freelance_project(db, project_id, user_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Get work logs
    query = db.query(WorkLog).filter(
        WorkLog.project_id == project_id,
        WorkLog.billable == True,  # noqa: E712
    )

    if include_unbilled:
        query = query.filter(WorkLog.invoiced == False)  # noqa: E712

    work_logs = query.all()

    if not work_logs:
        raise ValueError("No billable work logs found for this project")

    # Calculate totals
    total_hours = sum(log.hours for log in work_logs)
    total_amount = sum(log.calculate_amount() for log in work_logs)

    # Generate invoice number if not provided
    invoice_number = invoice_data.invoice_number
    if not invoice_number:
        today = date.today()
        count = db.query(Invoice).filter(Invoice.user_id == user_id).count()
        invoice_number = f"INV-{today.strftime('%Y%m')}-{count + 1:04d}"

    # Create invoice
    db_invoice = Invoice(
        user_id=user_id,
        project_id=project_id,
        invoice_number=invoice_number,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        total_amount=total_amount,
        total_hours=total_hours,
        hourly_rate=project.hourly_rate,
        payment_terms=invoice_data.payment_terms or "Net 30",
        notes=invoice_data.notes,
        status="draft",
    )

    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    # Mark work logs as invoiced
    for log in work_logs:
        log.invoiced = True
        log.invoice_id = db_invoice.id

    db.commit()

    return db_invoice


def update_invoice(db: Session, invoice_id: int, invoice_update, user_id: int):
    """Update an invoice for a user."""
    db_invoice = get_invoice(db, invoice_id, user_id)
    if not db_invoice:
        return None

    update_data = invoice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def delete_invoice(db: Session, invoice_id: int, user_id: int) -> bool:
    """Delete an invoice for a user and unmark associated work logs."""
    from database.models import WorkLog

    db_invoice = get_invoice(db, invoice_id, user_id)
    if not db_invoice:
        return False

    # Unmark work logs as invoiced
    work_logs = db.query(WorkLog).filter(WorkLog.invoice_id == invoice_id).all()
    for log in work_logs:
        log.invoiced = False
        log.invoice_id = None

    db.delete(db_invoice)
    db.commit()
    return True
