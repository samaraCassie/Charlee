"""CRUD operations for database models."""

from typing import Optional, cast

from sqlalchemy.orm import Session

from database.models import (
    BigRock,
    FocusSession,
    Notification,
    NotificationDigest,
    NotificationPattern,
    NotificationPreference,
    NotificationRule,
    NotificationSource,
    ResponseTemplate,
    Task,
)
from database.schemas import (
    BigRockCreate,
    BigRockUpdate,
    FocusSessionCreate,
    FocusSessionUpdate,
    NotificationCreate,
    NotificationDigestBase,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationRuleCreate,
    NotificationRuleUpdate,
    NotificationSourceCreate,
    NotificationSourceUpdate,
    NotificationUpdate,
    ResponseTemplateCreate,
    ResponseTemplateUpdate,
    TaskCreate,
    TaskUpdate,
)

# ==================== Big Rock CRUD ====================


def get_big_rock(db: Session, big_rock_id: int, user_id: int) -> Optional[BigRock]:
    """Get a single BigRock by ID for a specific user."""
    return cast(
        Optional[BigRock],
        db.query(BigRock).filter(BigRock.id == big_rock_id, BigRock.user_id == user_id).first(),
    )


def get_big_rocks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
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
        list[Task],
        query.order_by(Task.deadline.asc().nullslast()).offset(skip).limit(limit).all(),
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

    return db.query(WorkLog).filter(WorkLog.id == log_id, WorkLog.user_id == user_id).first()


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

    return db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == user_id).first()


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


# ==================== Projects Intelligence System CRUD ====================


# ----- FreelancePlatform CRUD -----


def get_platform(db: Session, platform_id: int, user_id: int):
    """Get a specific freelance platform by ID for a user."""
    from database.models import FreelancePlatform

    return (
        db.query(FreelancePlatform)
        .filter(FreelancePlatform.id == platform_id, FreelancePlatform.user_id == user_id)
        .first()
    )


def get_platforms(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list:
    """Get all freelance platforms for a user with optional filters."""
    from database.models import FreelancePlatform

    query = db.query(FreelancePlatform).filter(FreelancePlatform.user_id == user_id)

    if active_only:
        query = query.filter(FreelancePlatform.active == True)  # noqa: E712

    return query.order_by(FreelancePlatform.created_at.desc()).offset(skip).limit(limit).all()


def create_platform(db: Session, platform_data, user_id: int):
    """Create a new freelance platform for a user."""
    from database.models import FreelancePlatform

    db_platform = FreelancePlatform(**platform_data.model_dump(), user_id=user_id)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform


def update_platform(db: Session, platform_id: int, platform_update, user_id: int):
    """Update a freelance platform for a user."""
    db_platform = get_platform(db, platform_id, user_id)
    if not db_platform:
        return None

    update_data = platform_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_platform, field, value)

    db.commit()
    db.refresh(db_platform)
    return db_platform


def delete_platform(db: Session, platform_id: int, user_id: int) -> bool:
    """Delete a freelance platform for a user."""
    db_platform = get_platform(db, platform_id, user_id)
    if not db_platform:
        return False

    db.delete(db_platform)
    db.commit()
    return True


# ----- FreelanceOpportunity CRUD -----


def get_opportunity(db: Session, opportunity_id: int, user_id: int):
    """Get a specific freelance opportunity by ID for a user."""
    from database.models import FreelanceOpportunity

    return (
        db.query(FreelanceOpportunity)
        .filter(
            FreelanceOpportunity.id == opportunity_id,
            FreelanceOpportunity.user_id == user_id,
        )
        .first()
    )


def get_opportunities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    platform_id: Optional[int] = None,
    min_score: Optional[float] = None,
    recommendation: Optional[str] = None,
) -> list:
    """Get all freelance opportunities for a user with optional filters."""
    from database.models import FreelanceOpportunity

    query = db.query(FreelanceOpportunity).filter(FreelanceOpportunity.user_id == user_id)

    if status:
        query = query.filter(FreelanceOpportunity.status == status)

    if platform_id:
        query = query.filter(FreelanceOpportunity.platform_id == platform_id)

    if min_score is not None:
        query = query.filter(FreelanceOpportunity.final_score >= min_score)

    if recommendation:
        query = query.filter(FreelanceOpportunity.recommendation == recommendation)

    return (
        query.order_by(FreelanceOpportunity.final_score.desc().nullslast())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_opportunity(db: Session, opportunity_data, user_id: int):
    """Create a new freelance opportunity for a user."""
    from database.models import FreelanceOpportunity

    # Validate platform_id if provided
    if hasattr(opportunity_data, "platform_id") and opportunity_data.platform_id is not None:
        platform = get_platform(db, opportunity_data.platform_id, user_id)
        if not platform:
            raise ValueError(f"Platform with id {opportunity_data.platform_id} not found")

    db_opportunity = FreelanceOpportunity(**opportunity_data.model_dump(), user_id=user_id)
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


def update_opportunity(db: Session, opportunity_id: int, opportunity_update, user_id: int):
    """Update a freelance opportunity for a user."""
    db_opportunity = get_opportunity(db, opportunity_id, user_id)
    if not db_opportunity:
        return None

    update_data = opportunity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_opportunity, field, value)

    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


def delete_opportunity(db: Session, opportunity_id: int, user_id: int) -> bool:
    """Delete a freelance opportunity for a user."""
    db_opportunity = get_opportunity(db, opportunity_id, user_id)
    if not db_opportunity:
        return False

    db.delete(db_opportunity)
    db.commit()
    return True


# ----- PricingParameter CRUD -----


def get_pricing_parameter(db: Session, param_id: int, user_id: int):
    """Get a specific pricing parameter by ID for a user."""
    from database.models import PricingParameter

    return (
        db.query(PricingParameter)
        .filter(PricingParameter.id == param_id, PricingParameter.user_id == user_id)
        .first()
    )


def get_pricing_parameters(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> list:
    """Get all pricing parameters for a user with optional filters."""
    from database.models import PricingParameter

    query = db.query(PricingParameter).filter(PricingParameter.user_id == user_id)

    if active_only:
        query = query.filter(PricingParameter.active)

    return query.order_by(PricingParameter.version.desc()).offset(skip).limit(limit).all()


def get_active_pricing_parameter(db: Session, user_id: int):
    """Get the current active pricing parameter for a user."""
    from database.models import PricingParameter

    return (
        db.query(PricingParameter)
        .filter(PricingParameter.user_id == user_id, PricingParameter.active)
        .order_by(PricingParameter.version.desc())
        .first()
    )


def create_pricing_parameter(db: Session, pricing_data, user_id: int):
    """Create a new pricing parameter version for a user."""
    from database.models import PricingParameter

    # Get next version number
    latest = (
        db.query(PricingParameter)
        .filter(PricingParameter.user_id == user_id)
        .order_by(PricingParameter.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1

    # Deactivate previous version if setting new as active
    if hasattr(pricing_data, "active") and pricing_data.active:
        db.query(PricingParameter).filter(
            PricingParameter.user_id == user_id,
            PricingParameter.active == True,  # noqa: E712
        ).update({"active": False})

    db_pricing = PricingParameter(
        **pricing_data.model_dump(), user_id=user_id, version=next_version
    )
    db.add(db_pricing)
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


def update_pricing_parameter(db: Session, param_id: int, pricing_update, user_id: int):
    """Update a pricing parameter for a user."""
    from database.models import PricingParameter

    db_pricing = get_pricing_parameter(db, param_id, user_id)
    if not db_pricing:
        return None

    update_data = pricing_update.model_dump(exclude_unset=True)

    # If activating this version, deactivate others
    if update_data.get("active") is True:
        db.query(PricingParameter).filter(
            PricingParameter.user_id == user_id,
            PricingParameter.id != param_id,
            PricingParameter.active == True,  # noqa: E712
        ).update({"active": False})

    for field, value in update_data.items():
        setattr(db_pricing, field, value)

    db.commit()
    db.refresh(db_pricing)
    return db_pricing


def delete_pricing_parameter(db: Session, param_id: int, user_id: int) -> bool:
    """Delete a pricing parameter for a user (only if not active)."""
    db_pricing = get_pricing_parameter(db, param_id, user_id)
    if not db_pricing:
        return False

    if db_pricing.active:
        raise ValueError("Cannot delete active pricing parameter")

    db.delete(db_pricing)
    db.commit()
    return True


# ----- ProjectExecution CRUD -----


def get_project_execution(db: Session, execution_id: int, user_id: int):
    """Get a specific project execution by ID for a user."""
    from database.models import ProjectExecution

    return (
        db.query(ProjectExecution)
        .filter(ProjectExecution.id == execution_id, ProjectExecution.user_id == user_id)
        .first()
    )


def get_project_executions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    opportunity_id: Optional[int] = None,
) -> list:
    """Get all project executions for a user with optional filters."""
    from database.models import ProjectExecution

    query = db.query(ProjectExecution).filter(ProjectExecution.user_id == user_id)

    if status:
        query = query.filter(ProjectExecution.status == status)

    if opportunity_id:
        query = query.filter(ProjectExecution.opportunity_id == opportunity_id)

    return query.order_by(ProjectExecution.created_at.desc()).offset(skip).limit(limit).all()


def create_project_execution(db: Session, execution_data, user_id: int):
    """Create a new project execution for a user."""
    from database.models import ProjectExecution

    # Validate opportunity_id
    if hasattr(execution_data, "opportunity_id"):
        opportunity = get_opportunity(db, execution_data.opportunity_id, user_id)
        if not opportunity:
            raise ValueError(f"Opportunity with id {execution_data.opportunity_id} not found")

    db_execution = ProjectExecution(**execution_data.model_dump(), user_id=user_id)
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


def update_project_execution(db: Session, execution_id: int, execution_update, user_id: int):
    """Update a project execution for a user."""
    db_execution = get_project_execution(db, execution_id, user_id)
    if not db_execution:
        return None

    update_data = execution_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_execution, field, value)

    db.commit()
    db.refresh(db_execution)
    return db_execution


def delete_project_execution(db: Session, execution_id: int, user_id: int) -> bool:
    """Delete a project execution for a user."""
    db_execution = get_project_execution(db, execution_id, user_id)
    if not db_execution:
        return False

    db.delete(db_execution)
    db.commit()
    return True


# ----- Negotiation CRUD -----


def get_negotiation(db: Session, negotiation_id: int, user_id: int):
    """Get a specific negotiation by ID for a user."""
    from database.models import Negotiation

    return (
        db.query(Negotiation)
        .filter(Negotiation.id == negotiation_id, Negotiation.user_id == user_id)
        .first()
    )


def get_negotiations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    opportunity_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list:
    """Get all negotiations for a user with optional filters."""
    from database.models import Negotiation

    query = db.query(Negotiation).filter(Negotiation.user_id == user_id)

    if opportunity_id:
        query = query.filter(Negotiation.opportunity_id == opportunity_id)

    if status:
        query = query.filter(Negotiation.outcome == status)

    return query.order_by(Negotiation.created_at.desc()).offset(skip).limit(limit).all()


def create_negotiation(db: Session, negotiation_data, user_id: int):
    """Create a new negotiation record for a user."""
    from database.models import Negotiation

    # Validate opportunity_id
    if hasattr(negotiation_data, "opportunity_id"):
        opportunity = get_opportunity(db, negotiation_data.opportunity_id, user_id)
        if not opportunity:
            raise ValueError(f"Opportunity with id {negotiation_data.opportunity_id} not found")

    negotiation_dict = negotiation_data.model_dump()

    db_negotiation = Negotiation(**negotiation_dict, user_id=user_id)
    db.add(db_negotiation)
    db.commit()
    db.refresh(db_negotiation)
    return db_negotiation


def update_negotiation(db: Session, negotiation_id: int, negotiation_update, user_id: int):
    """Update a negotiation for a user."""
    db_negotiation = get_negotiation(db, negotiation_id, user_id)
    if not db_negotiation:
        return None

    update_data = negotiation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_negotiation, field, value)

    db.commit()
    db.refresh(db_negotiation)
    return db_negotiation


def delete_negotiation(db: Session, negotiation_id: int, user_id: int) -> bool:
    """Delete a negotiation for a user."""
    db_negotiation = get_negotiation(db, negotiation_id, user_id)
    if not db_negotiation:
        return False

    db.delete(db_negotiation)
    db.commit()
    return True


# ==================== Notification CRUD ====================


def get_notification(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Get a single Notification by ID for a specific user."""
    return cast(
        Optional[Notification],
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first(),
    )


def get_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
) -> list[Notification]:
    """Get list of Notifications for a specific user."""
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if unread_only:
        query = query.filter(Notification.read == False)  # noqa: E712

    if notification_type:
        query = query.filter(Notification.type == notification_type)

    return cast(
        list[Notification],
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all(),
    )


def count_unread_notifications(db: Session, user_id: int) -> int:
    """Count unread notifications for a user."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)  # noqa: E712
        .count()
    )


def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Create a new Notification."""
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(
    db: Session, notification_id: int, notification_update: NotificationUpdate, user_id: int
) -> Optional[Notification]:
    """Update a Notification for a specific user."""
    db_notification = get_notification(db, notification_id, user_id)
    if not db_notification:
        return None

    update_data = notification_update.model_dump(exclude_unset=True)

    # If marking as read, call the model method to set read_at
    if update_data.get("read") is True:
        db_notification.mark_as_read()
    else:
        for field, value in update_data.items():
            setattr(db_notification, field, value)

    db.commit()
    db.refresh(db_notification)
    return db_notification


def mark_notification_as_read(
    db: Session, notification_id: int, user_id: int
) -> Optional[Notification]:
    """Mark a single notification as read."""
    db_notification = get_notification(db, notification_id, user_id)
    if not db_notification:
        return None

    db_notification.mark_as_read()
    db.commit()
    db.refresh(db_notification)
    return db_notification


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a user. Returns count of updated notifications."""
    from datetime import datetime, timezone

    updated_count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)  # noqa: E712
        .update({"read": True, "read_at": datetime.now(timezone.utc)}, synchronize_session=False)
    )
    db.commit()
    return cast(int, updated_count)


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """Delete a Notification for a specific user."""
    db_notification = get_notification(db, notification_id, user_id)
    if not db_notification:
        return False

    db.delete(db_notification)
    db.commit()
    return True


# ==================== Notification Preference CRUD ====================


def get_notification_preference(
    db: Session, user_id: int, notification_type: str
) -> Optional[NotificationPreference]:
    """Get a notification preference for a user and type."""
    return cast(
        Optional[NotificationPreference],
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == notification_type,
        )
        .first(),
    )


def get_notification_preferences(
    db: Session,
    user_id: int,
) -> list[NotificationPreference]:
    """Get all notification preferences for a user."""
    return cast(
        list[NotificationPreference],
        db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).all(),
    )


def create_notification_preference(
    db: Session, preference: NotificationPreferenceCreate, user_id: int
) -> NotificationPreference:
    """Create a new NotificationPreference for a user."""
    db_preference = NotificationPreference(**preference.model_dump(), user_id=user_id)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference


def update_notification_preference(
    db: Session,
    notification_type: str,
    preference_update: NotificationPreferenceUpdate,
    user_id: int,
) -> Optional[NotificationPreference]:
    """Update a NotificationPreference for a user."""
    db_preference = get_notification_preference(db, user_id, notification_type)
    if not db_preference:
        return None

    update_data = preference_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_preference, field, value)

    db.commit()
    db.refresh(db_preference)
    return db_preference


def delete_notification_preference(db: Session, notification_type: str, user_id: int) -> bool:
    """Delete a NotificationPreference for a user."""
    db_preference = get_notification_preference(db, user_id, notification_type)
    if not db_preference:
        return False

    db.delete(db_preference)
    db.commit()
    return True


def get_or_create_default_preferences(db: Session, user_id: int) -> list[NotificationPreference]:
    """Get or create default notification preferences for a user."""
    default_types = [
        "task_due_soon",
        "capacity_overload",
        "cycle_phase_change",
        "freelance_invoice_ready",
        "system",
        "achievement",
    ]

    preferences = []
    for notif_type in default_types:
        pref = get_notification_preference(db, user_id, notif_type)
        if not pref:
            pref_data = NotificationPreferenceCreate(
                notification_type=notif_type,  # type: ignore[arg-type]
                enabled=True,
                in_app_enabled=True,
                email_enabled=False,
                push_enabled=False,
            )
            pref = create_notification_preference(db, pref_data, user_id)
        preferences.append(pref)

    return preferences


# ==================== Notification Source CRUD ====================


def get_notification_source(db: Session, source_id: int, user_id: int) -> NotificationSource | None:
    """Get a notification source by ID for a specific user."""
    return db.query(NotificationSource).filter_by(id=source_id, user_id=user_id).first()


def get_notification_sources(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[NotificationSource]:
    """Get all notification sources for a user."""
    return db.query(NotificationSource).filter_by(user_id=user_id).offset(skip).limit(limit).all()


def create_notification_source(
    db: Session, source: NotificationSourceCreate, user_id: int
) -> NotificationSource:
    """Create a new notification source."""
    db_source = NotificationSource(user_id=user_id, **source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def update_notification_source(
    db: Session, source_id: int, user_id: int, source_update: NotificationSourceUpdate
) -> NotificationSource | None:
    """Update a notification source."""
    db_source = get_notification_source(db, source_id, user_id)
    if not db_source:
        return None

    update_data = source_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)

    db.commit()
    db.refresh(db_source)
    return db_source


def delete_notification_source(db: Session, source_id: int, user_id: int) -> bool:
    """Delete a notification source."""
    db_source = get_notification_source(db, source_id, user_id)
    if not db_source:
        return False

    db.delete(db_source)
    db.commit()
    return True


# ==================== Notification Rule CRUD ====================


def get_notification_rule(db: Session, rule_id: int, user_id: int) -> NotificationRule | None:
    """Get a notification rule by ID for a specific user."""
    return db.query(NotificationRule).filter_by(id=rule_id, user_id=user_id).first()


def get_notification_rules(
    db: Session, user_id: int, enabled_only: bool = False, skip: int = 0, limit: int = 100
) -> list[NotificationRule]:
    """Get all notification rules for a user."""
    query = db.query(NotificationRule).filter_by(user_id=user_id)

    if enabled_only:
        query = query.filter_by(enabled=True)

    return query.order_by(NotificationRule.priority.desc()).offset(skip).limit(limit).all()


def create_notification_rule(
    db: Session, rule: NotificationRuleCreate, user_id: int
) -> NotificationRule:
    """Create a new notification rule."""
    db_rule = NotificationRule(user_id=user_id, **rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def update_notification_rule(
    db: Session, rule_id: int, user_id: int, rule_update: NotificationRuleUpdate
) -> NotificationRule | None:
    """Update a notification rule."""
    db_rule = get_notification_rule(db, rule_id, user_id)
    if not db_rule:
        return None

    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)

    db.commit()
    db.refresh(db_rule)
    return db_rule


def delete_notification_rule(db: Session, rule_id: int, user_id: int) -> bool:
    """Delete a notification rule."""
    db_rule = get_notification_rule(db, rule_id, user_id)
    if not db_rule:
        return False

    db.delete(db_rule)
    db.commit()
    return True


# ==================== Notification Digest CRUD ====================


def get_notification_digest(db: Session, digest_id: int, user_id: int) -> NotificationDigest | None:
    """Get a notification digest by ID for a specific user."""
    return db.query(NotificationDigest).filter_by(id=digest_id, user_id=user_id).first()


def get_notification_digests(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> list[NotificationDigest]:
    """Get all notification digests for a user."""
    return (
        db.query(NotificationDigest)
        .filter_by(user_id=user_id)
        .order_by(NotificationDigest.period_start.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_notification_digest(
    db: Session, digest: NotificationDigestBase, user_id: int
) -> NotificationDigest:
    """Create a new notification digest."""
    db_digest = NotificationDigest(user_id=user_id, **digest.model_dump())
    db.add(db_digest)
    db.commit()
    db.refresh(db_digest)
    return db_digest


def get_latest_digest(db: Session, user_id: int, digest_type: str) -> NotificationDigest | None:
    """Get the latest digest of a specific type for a user."""
    return (
        db.query(NotificationDigest)
        .filter_by(user_id=user_id, digest_type=digest_type)
        .order_by(NotificationDigest.period_start.desc())
        .first()
    )


# ==================== Notification Pattern CRUD ====================


def get_notification_pattern(
    db: Session, pattern_id: int, user_id: int
) -> NotificationPattern | None:
    """Get a notification pattern by ID for a specific user."""
    return db.query(NotificationPattern).filter_by(id=pattern_id, user_id=user_id).first()


def get_notification_patterns(
    db: Session,
    user_id: int,
    pattern_key: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[NotificationPattern]:
    """Get notification patterns for a user with optional filtering."""
    query = db.query(NotificationPattern).filter_by(user_id=user_id)

    if pattern_key:
        query = query.filter(NotificationPattern.pattern_key == pattern_key)

    return query.order_by(NotificationPattern.updated_at.desc()).offset(skip).limit(limit).all()


# ==================== Focus Session CRUD ====================


def get_focus_session(db: Session, session_id: int, user_id: int) -> FocusSession | None:
    """Get a focus session by ID for a specific user."""
    return db.query(FocusSession).filter_by(id=session_id, user_id=user_id).first()


def get_focus_sessions(
    db: Session, user_id: int, active_only: bool = False, skip: int = 0, limit: int = 100
) -> list[FocusSession]:
    """Get all focus sessions for a user."""
    query = db.query(FocusSession).filter_by(user_id=user_id)

    if active_only:
        query = query.filter(FocusSession.end_time.is_(None))

    return query.order_by(FocusSession.start_time.desc()).offset(skip).limit(limit).all()


def get_active_focus_session(db: Session, user_id: int) -> FocusSession | None:
    """Get the currently active focus session for a user."""
    return (
        db.query(FocusSession)
        .filter_by(user_id=user_id)
        .filter(FocusSession.end_time.is_(None))
        .order_by(FocusSession.start_time.desc())
        .first()
    )


def create_focus_session(db: Session, session: FocusSessionCreate, user_id: int) -> FocusSession:
    """Create a new focus session."""
    db_session = FocusSession(user_id=user_id, **session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_focus_session(
    db: Session, session_id: int, user_id: int, session_update: FocusSessionUpdate
) -> FocusSession | None:
    """Update a focus session."""
    db_session = get_focus_session(db, session_id, user_id)
    if not db_session:
        return None

    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)

    db.commit()
    db.refresh(db_session)
    return db_session


def end_focus_session(db: Session, session_id: int, user_id: int) -> FocusSession | None:
    """End a focus session by setting end_time to now."""
    from datetime import datetime, timezone

    db_session = get_focus_session(db, session_id, user_id)
    if not db_session:
        return None

    db_session.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_session)
    return db_session


# ==================== Response Template CRUD ====================


def get_response_template(db: Session, template_id: int, user_id: int) -> ResponseTemplate | None:
    """Get a response template by ID for a specific user."""
    return db.query(ResponseTemplate).filter_by(id=template_id, user_id=user_id).first()


def get_response_templates(
    db: Session, user_id: int, category: str | None = None, skip: int = 0, limit: int = 100
) -> list[ResponseTemplate]:
    """Get all response templates for a user."""
    query = db.query(ResponseTemplate).filter_by(user_id=user_id)

    if category:
        query = query.filter_by(category=category)

    return query.order_by(ResponseTemplate.times_used.desc()).offset(skip).limit(limit).all()


def create_response_template(
    db: Session, template: ResponseTemplateCreate, user_id: int
) -> ResponseTemplate:
    """Create a new response template."""
    db_template = ResponseTemplate(user_id=user_id, **template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_response_template(
    db: Session, template_id: int, user_id: int, template_update: ResponseTemplateUpdate
) -> ResponseTemplate | None:
    """Update a response template."""
    db_template = get_response_template(db, template_id, user_id)
    if not db_template:
        return None

    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)

    db.commit()
    db.refresh(db_template)
    return db_template


def delete_response_template(db: Session, template_id: int, user_id: int) -> bool:
    """Delete a response template."""
    db_template = get_response_template(db, template_id, user_id)
    if not db_template:
        return False

    db.delete(db_template)
    db.commit()
    return True


def increment_template_usage(db: Session, template_id: int, user_id: int) -> bool:
    """Increment the usage counter for a response template."""
    from datetime import datetime, timezone

    db_template = get_response_template(db, template_id, user_id)
    if not db_template:
        return False

    db_template.times_used += 1
    db_template.last_used = datetime.now(timezone.utc)
    db.commit()
    return True
