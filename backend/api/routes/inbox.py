"""Inbox API routes - Inbox rápido e gestão de tarefas prioritárias."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database.config import get_db
from database import schemas
from skills.priorizacao import create_sistema_priorizacao

router = APIRouter()


class InboxResponse(BaseModel):
    """Response do inbox rápido."""

    inbox_text: str
    tarefas: List[schemas.TarefaResponse]
    total: int


@router.get("/rapido", response_model=InboxResponse)
async def inbox_rapido(limite: int = 10, db: Session = Depends(get_db)):
    """
    Inbox Rápido - Top tarefas priorizadas para hoje.

    Retorna as tarefas mais urgentes com base em:
    - Deadline próximo
    - Big Rock prioritário
    - Tempo sem movimento
    - Tipo de tarefa
    """
    sistema = create_sistema_priorizacao(db)

    # Gerar inbox em texto
    inbox_texto = sistema.gerar_inbox_rapido(limite=limite)

    # Obter tarefas priorizadas
    tarefas_priorizadas = sistema.priorizar_tarefas(status="Pendente", limite=limite)

    return {
        "inbox_text": inbox_texto,
        "tarefas": tarefas_priorizadas,
        "total": len(tarefas_priorizadas),
    }


@router.get("/hoje", response_model=schemas.TarefaListResponse)
async def tarefas_hoje(db: Session = Depends(get_db)):
    """Tarefas com deadline para hoje."""
    from datetime import date
    from database import crud

    today = date.today()
    tarefas = crud.get_tarefas(db, status="Pendente", limit=50)

    # Filtrar por deadline hoje
    tarefas_hoje = [t for t in tarefas if t.deadline and t.deadline.date() == today]

    return {"total": len(tarefas_hoje), "tarefas": tarefas_hoje}


@router.get("/atrasadas", response_model=schemas.TarefaListResponse)
async def tarefas_atrasadas(db: Session = Depends(get_db)):
    """Tarefas com deadline já passado."""
    from datetime import date
    from database import crud

    today = date.today()
    tarefas = crud.get_tarefas(db, status="Pendente", limit=100)

    # Filtrar por deadline atrasada
    tarefas_atrasadas = [t for t in tarefas if t.deadline and t.deadline.date() < today]

    # Ordenar por deadline (mais antigo primeiro)
    tarefas_atrasadas.sort(key=lambda t: t.deadline)

    return {"total": len(tarefas_atrasadas), "tarefas": tarefas_atrasadas}


@router.get("/proxima-semana", response_model=schemas.TarefaListResponse)
async def tarefas_proxima_semana(db: Session = Depends(get_db)):
    """Tarefas com deadline nos próximos 7 dias."""
    from datetime import date, timedelta
    from database import crud

    today = date.today()
    next_week = today + timedelta(days=7)

    tarefas = crud.get_tarefas(db, status="Pendente", limit=100)

    # Filtrar por deadline próxima semana
    tarefas_semana = [t for t in tarefas if t.deadline and today <= t.deadline.date() <= next_week]

    # Ordenar por deadline
    tarefas_semana.sort(key=lambda t: t.deadline)

    return {"total": len(tarefas_semana), "tarefas": tarefas_semana}
