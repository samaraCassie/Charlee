"""
API routes for response templates.

Endpoints for managing quick response templates for notifications.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.jwt import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/templates", tags=["Response Templates"])


@router.get("/", response_model=List[schemas.ResponseTemplateResponse])
def list_response_templates(
    category: str = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List response templates for the current user.

    Returns paginated list of templates, optionally filtered by category.
    """
    templates = crud.get_response_templates(
        db, user_id=current_user.id, category=category, skip=skip, limit=limit
    )
    return templates


@router.get("/{template_id}", response_model=schemas.ResponseTemplateResponse)
def get_response_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific response template by ID."""
    template = crud.get_response_template(db, template_id=template_id, user_id=current_user.id)

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return template


@router.post(
    "/", response_model=schemas.ResponseTemplateResponse, status_code=status.HTTP_201_CREATED
)
def create_response_template(
    template: schemas.ResponseTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new response template.

    Templates can include variables like {{name}}, {{date}}, etc.
    """
    try:
        db_template = crud.create_response_template(db, template=template, user_id=current_user.id)
        logger.info(f"Created response template {db_template.id} for user {current_user.id}")
        return db_template

    except Exception as e:
        logger.error(f"Error creating response template for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create response template: {str(e)}",
        )


@router.put("/{template_id}", response_model=schemas.ResponseTemplateResponse)
def update_response_template(
    template_id: int,
    template: schemas.ResponseTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing response template."""
    db_template = crud.update_response_template(
        db, template_id=template_id, template=template, user_id=current_user.id
    )

    if not db_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    logger.info(f"Updated response template {template_id} for user {current_user.id}")
    return db_template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a response template."""
    success = crud.delete_response_template(db, template_id=template_id, user_id=current_user.id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    logger.info(f"Deleted response template {template_id} for user {current_user.id}")
    return None


@router.post("/{template_id}/use", response_model=dict)
def use_response_template(
    template_id: int,
    variables: dict = {},
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Use a response template.

    Increments usage counter and returns the rendered template text
    with variables replaced.
    """
    template = crud.get_response_template(db, template_id=template_id, user_id=current_user.id)

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    # Increment usage counter
    crud.increment_template_usage(db, template_id=template_id, user_id=current_user.id)

    # Render template with variables
    rendered_text = template.template_text
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        rendered_text = rendered_text.replace(placeholder, str(value))

    logger.info(f"Used response template {template_id} for user {current_user.id}")

    return {
        "rendered_text": rendered_text,
        "template_id": template_id,
        "times_used": template.times_used + 1,
    }
