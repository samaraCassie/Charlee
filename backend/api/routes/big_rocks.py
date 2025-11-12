"""Big Rocks API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from database import crud, schemas
from database.models import User
from api.cache import invalidate_pattern
from api.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=schemas.BigRockListResponse)
def get_big_rocks(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of Big Rocks for the authenticated user.

    Cached for 5 minutes. Cache is invalidated on create/update/delete operations.
    """
    big_rocks = crud.get_big_rocks(
        db, user_id=current_user.id, skip=skip, limit=limit, active_only=active_only
    )
    return {"total": len(big_rocks), "big_rocks": big_rocks}


@router.get("/{big_rock_id}", response_model=schemas.BigRockResponse)
def get_big_rock(
    big_rock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single Big Rock by ID for the authenticated user.

    Cached for 5 minutes. Cache is invalidated on update/delete operations.
    """
    big_rock = crud.get_big_rock(db, big_rock_id, user_id=current_user.id)
    if not big_rock:
        raise HTTPException(status_code=404, detail="Big Rock not found")
    return big_rock


@router.post("/", response_model=schemas.BigRockResponse, status_code=201)
def create_big_rock(
    big_rock: schemas.BigRockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new Big Rock for the authenticated user and invalidate cache."""
    result = crud.create_big_rock(db, big_rock, user_id=current_user.id)

    # Invalidate all Big Rock caches
    invalidate_pattern("big_rocks:*")

    return result


@router.patch("/{big_rock_id}", response_model=schemas.BigRockResponse)
def update_big_rock(
    big_rock_id: int,
    big_rock_update: schemas.BigRockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a Big Rock for the authenticated user and invalidate cache."""
    big_rock = crud.update_big_rock(db, big_rock_id, big_rock_update, user_id=current_user.id)
    if not big_rock:
        raise HTTPException(status_code=404, detail="Big Rock not found")

    # Invalidate all Big Rock caches
    invalidate_pattern("big_rocks:*")

    return big_rock


@router.delete("/{big_rock_id}", status_code=204)
def delete_big_rock(
    big_rock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete a Big Rock (sets active=False) for the authenticated user and invalidate cache."""
    success = crud.delete_big_rock(db, big_rock_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Big Rock not found")

    # Invalidate all Big Rock caches
    invalidate_pattern("big_rocks:*")

    return None
