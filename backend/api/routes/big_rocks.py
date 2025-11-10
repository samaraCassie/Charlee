"""Big Rocks API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from database import crud, schemas

router = APIRouter()


@router.get("/", response_model=schemas.BigRockListResponse)
def get_big_rocks(
    ativo_apenas: bool = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get list of Big Rocks."""
    big_rocks = crud.get_big_rocks(db, skip=skip, limit=limit, ativo_apenas=ativo_apenas)
    return {"total": len(big_rocks), "big_rocks": big_rocks}


@router.get("/{big_rock_id}", response_model=schemas.BigRockResponse)
def get_big_rock(big_rock_id: int, db: Session = Depends(get_db)):
    """Get a single Big Rock by ID."""
    big_rock = crud.get_big_rock(db, big_rock_id)
    if not big_rock:
        raise HTTPException(status_code=404, detail="Big Rock not found")
    return big_rock


@router.post("/", response_model=schemas.BigRockResponse, status_code=201)
def create_big_rock(big_rock: schemas.BigRockCreate, db: Session = Depends(get_db)):
    """Create a new Big Rock."""
    return crud.create_big_rock(db, big_rock)


@router.patch("/{big_rock_id}", response_model=schemas.BigRockResponse)
def update_big_rock(
    big_rock_id: int, big_rock_update: schemas.BigRockUpdate, db: Session = Depends(get_db)
):
    """Update a Big Rock."""
    big_rock = crud.update_big_rock(db, big_rock_id, big_rock_update)
    if not big_rock:
        raise HTTPException(status_code=404, detail="Big Rock not found")
    return big_rock


@router.delete("/{big_rock_id}", status_code=204)
def delete_big_rock(big_rock_id: int, db: Session = Depends(get_db)):
    """Soft delete a Big Rock (sets ativo=False)."""
    success = crud.delete_big_rock(db, big_rock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Big Rock not found")
    return None
