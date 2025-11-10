"""Tarefas API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database.config import get_db
from database import crud, schemas

router = APIRouter()


@router.get("/", response_model=schemas.TarefaListResponse)
def get_tarefas(
    status: Optional[str] = None,
    big_rock_id: Optional[int] = None,
    tipo: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of Tarefas with optional filters."""
    tarefas = crud.get_tarefas(
        db, skip=skip, limit=limit, status=status, big_rock_id=big_rock_id, tipo=tipo
    )
    return {"total": len(tarefas), "tarefas": tarefas}


@router.get("/{tarefa_id}", response_model=schemas.TarefaResponse)
def get_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    """Get a single Tarefa by ID."""
    tarefa = crud.get_tarefa(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa not found")
    return tarefa


@router.post("/", response_model=schemas.TarefaResponse, status_code=201)
def create_tarefa(tarefa: schemas.TarefaCreate, db: Session = Depends(get_db)):
    """Create a new Tarefa."""
    return crud.create_tarefa(db, tarefa)


@router.patch("/{tarefa_id}", response_model=schemas.TarefaResponse)
def update_tarefa(
    tarefa_id: int, tarefa_update: schemas.TarefaUpdate, db: Session = Depends(get_db)
):
    """Update a Tarefa."""
    tarefa = crud.update_tarefa(db, tarefa_id, tarefa_update)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa not found")
    return tarefa


@router.post("/{tarefa_id}/concluir", response_model=schemas.TarefaResponse)
def marcar_tarefa_concluida(tarefa_id: int, db: Session = Depends(get_db)):
    """Mark a Tarefa as completed."""
    tarefa = crud.marcar_tarefa_concluida(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa not found")
    return tarefa


@router.post("/{tarefa_id}/reabrir", response_model=schemas.TarefaResponse)
def reabrir_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    """Reopen a completed Tarefa."""
    tarefa = crud.reabrir_tarefa(db, tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa not found")
    return tarefa


@router.delete("/{tarefa_id}", status_code=204)
def delete_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    """Delete a Tarefa permanently."""
    success = crud.delete_tarefa(db, tarefa_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarefa not found")
    return None
