"""Priorização API routes - Sistema de priorização inteligente."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.config import get_db
from database import schemas
from skills.priorizacao import create_sistema_priorizacao

router = APIRouter()


class InboxResponse(BaseModel):
    """Response do inbox rápido."""

    inbox: str


@router.get("/inbox", response_model=InboxResponse)
async def inbox_rapido(limite: int = 10, db: Session = Depends(get_db)):
    """
    Inbox Rápido - Top tarefas priorizadas.

    Retorna as tarefas mais urgentes e importantes com base em:
    - Deadline
    - Big Rock
    - Tempo sem movimento
    - Tipo de tarefa
    """
    sistema = create_sistema_priorizacao(db)
    inbox_texto = sistema.gerar_inbox_rapido(limite=limite)

    return InboxResponse(inbox=inbox_texto)


@router.post("/recalcular")
async def recalcular_prioridades(big_rock_id: int | None = None, db: Session = Depends(get_db)):
    """
    Recalcula prioridades de todas as tarefas pendentes.

    Opcionalmente, pode filtrar por Big Rock.
    """
    sistema = create_sistema_priorizacao(db)

    tarefas_priorizadas = sistema.priorizar_tarefas(status="Pendente", big_rock_id=big_rock_id)

    return {"message": "Prioridades recalculadas", "tarefas_processadas": len(tarefas_priorizadas)}


@router.get("/tarefas-priorizadas", response_model=schemas.TarefaListResponse)
async def listar_tarefas_priorizadas(
    big_rock_id: int | None = None, limite: int = 20, db: Session = Depends(get_db)
):
    """
    Lista tarefas ordenadas por prioridade calculada.
    """
    sistema = create_sistema_priorizacao(db)

    tarefas = sistema.priorizar_tarefas(status="Pendente", big_rock_id=big_rock_id, limite=limite)

    return {"total": len(tarefas), "tarefas": tarefas}
