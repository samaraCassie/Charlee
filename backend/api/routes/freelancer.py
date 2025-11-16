"""Freelancer API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from api.cache import invalidate_pattern
from database import crud, schemas
from database.config import get_db
from database.models import User

router = APIRouter()


# ==================== Projects ====================


@router.get("/projects", response_model=schemas.FreelanceProjectListResponse)
def get_freelance_projects(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of freelance projects for the authenticated user.

    Optional filters:
    - status: Filter by project status (proposal, active, completed, cancelled)
    """
    projects = crud.get_freelance_projects(
        db, user_id=current_user.id, skip=skip, limit=limit, status=status
    )
    return {"total": len(projects), "projects": projects}


@router.get("/projects/{project_id}", response_model=schemas.FreelanceProjectResponse)
def get_freelance_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single freelance project by ID for the authenticated user."""
    project = crud.get_freelance_project(db, project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")
    return project


@router.post("/projects", response_model=schemas.FreelanceProjectResponse, status_code=201)
def create_freelance_project(
    project: schemas.FreelanceProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new freelance project for the authenticated user and invalidate cache."""
    result = crud.create_freelance_project(db, project, user_id=current_user.id)

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return result


@router.patch("/projects/{project_id}", response_model=schemas.FreelanceProjectResponse)
def update_freelance_project(
    project_id: int,
    project_update: schemas.FreelanceProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a freelance project for the authenticated user and invalidate cache."""
    project = crud.update_freelance_project(db, project_id, project_update, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_freelance_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a freelance project for the authenticated user and invalidate cache."""
    success = crud.delete_freelance_project(db, project_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return None


# ==================== Work Logs ====================


@router.get("/work-logs", response_model=schemas.WorkLogListResponse)
def get_work_logs(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of work logs for the authenticated user.

    Optional filters:
    - project_id: Filter by project ID
    """
    work_logs = crud.get_work_logs(
        db, user_id=current_user.id, project_id=project_id, skip=skip, limit=limit
    )
    return {"total": len(work_logs), "work_logs": work_logs}


@router.get("/work-logs/{log_id}", response_model=schemas.WorkLogResponse)
def get_work_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single work log by ID for the authenticated user."""
    work_log = crud.get_work_log(db, log_id, user_id=current_user.id)
    if not work_log:
        raise HTTPException(status_code=404, detail="Work log not found")
    return work_log


@router.post("/work-logs", response_model=schemas.WorkLogResponse, status_code=201)
def create_work_log(
    work_log: schemas.WorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new work log for the authenticated user and invalidate cache."""
    # Verify project exists and belongs to user
    project = crud.get_freelance_project(db, work_log.project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    result = crud.create_work_log(db, work_log, user_id=current_user.id)

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return result


@router.patch("/work-logs/{log_id}", response_model=schemas.WorkLogResponse)
def update_work_log(
    log_id: int,
    work_log_update: schemas.WorkLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a work log for the authenticated user and invalidate cache."""
    work_log = crud.update_work_log(db, log_id, work_log_update, user_id=current_user.id)
    if not work_log:
        raise HTTPException(status_code=404, detail="Work log not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return work_log


@router.delete("/work-logs/{log_id}", status_code=204)
def delete_work_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a work log for the authenticated user and invalidate cache."""
    success = crud.delete_work_log(db, log_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Work log not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return None


# ==================== Invoices ====================


@router.get("/invoices", response_model=schemas.InvoiceListResponse)
def get_invoices(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of invoices for the authenticated user.

    Optional filters:
    - project_id: Filter by project ID
    """
    invoices = crud.get_invoices(
        db, user_id=current_user.id, project_id=project_id, skip=skip, limit=limit
    )
    return {"total": len(invoices), "invoices": invoices}


@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single invoice by ID for the authenticated user."""
    invoice = crud.get_invoice(db, invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/invoices", response_model=schemas.InvoiceResponse, status_code=201)
def create_invoice(
    invoice: schemas.InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new invoice for the authenticated user and invalidate cache."""
    # Verify project exists and belongs to user
    project = crud.get_freelance_project(db, invoice.project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    try:
        result = crud.create_invoice(db, invoice, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return result


@router.patch("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_update: schemas.InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an invoice for the authenticated user and invalidate cache."""
    invoice = crud.update_invoice(db, invoice_id, invoice_update, user_id=current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return invoice


@router.delete("/invoices/{invoice_id}", status_code=204)
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an invoice for the authenticated user and invalidate cache."""
    success = crud.delete_invoice(db, invoice_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return None


# ==================== Additional Endpoints ====================


@router.post(
    "/projects/{project_id}/log-work",
    response_model=schemas.WorkLogResponse,
    status_code=201,
)
def log_work_on_project(
    project_id: int,
    work_log: schemas.WorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Convenience endpoint to log work on a specific project.

    Sets the project_id from the URL path, overriding any value in the request body.
    """
    # Verify project exists and belongs to user
    project = crud.get_freelance_project(db, project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    # Override project_id from path
    work_log_data = work_log.model_copy(update={"project_id": project_id})

    result = crud.create_work_log(db, work_log_data, user_id=current_user.id)

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return result


@router.get(
    "/projects/{project_id}/invoice",
    response_model=schemas.InvoiceResponse,
    status_code=201,
)
def generate_invoice_for_project(
    project_id: int,
    invoice_number: Optional[str] = None,
    payment_terms: Optional[str] = "Net 30",
    include_unbilled_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Convenience endpoint to generate an invoice for a specific project.

    Automatically includes all unbilled work logs for the project.
    """
    # Verify project exists and belongs to user
    project = crud.get_freelance_project(db, project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Freelance project not found")

    # Create invoice data
    invoice_data = schemas.InvoiceCreate(
        project_id=project_id,
        invoice_number=invoice_number,
        payment_terms=payment_terms,
        include_unbilled_only=include_unbilled_only,
    )

    try:
        result = crud.create_invoice(db, invoice_data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Invalidate all freelance caches
    invalidate_pattern("freelance:*")

    return result
