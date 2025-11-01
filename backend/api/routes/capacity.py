"""Capacity API routes - Gestão de capacidade e sobrecarga."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.config import get_db
from agent.specialized_agents.capacity_guard_agent import create_capacity_guard_agent

router = APIRouter()


class AgentResponse(BaseModel):
    """Response padrão dos agentes."""
    response: str


class AvaliacaoCompromissoRequest(BaseModel):
    """Request para avaliar novo compromisso."""
    nome_compromisso: str
    tarefas_estimadas: int
    big_rock_nome: str | None = None


@router.get("/carga/atual", response_model=AgentResponse)
async def calcular_carga_atual(
    proximas_semanas: int = 3,
    db: Session = Depends(get_db)
):
    """Calcula a carga de trabalho atual por Big Rock."""
    agent = create_capacity_guard_agent(db)
    response = agent.calcular_carga_atual(proximas_semanas)
    return AgentResponse(response=response)


@router.post("/avaliar-compromisso", response_model=AgentResponse)
async def avaliar_compromisso(
    request: AvaliacaoCompromissoRequest,
    db: Session = Depends(get_db)
):
    """Avalia se há capacidade para um novo compromisso."""
    agent = create_capacity_guard_agent(db)

    response = agent.avaliar_novo_compromisso(
        nome_compromisso=request.nome_compromisso,
        tarefas_estimadas=request.tarefas_estimadas,
        big_rock_nome=request.big_rock_nome
    )

    return AgentResponse(response=response)


@router.get("/tradeoffs", response_model=AgentResponse)
async def sugerir_tradeoffs(
    num_tarefas_liberar: int = 5,
    db: Session = Depends(get_db)
):
    """Sugere tarefas que podem ser adiadas para liberar capacidade."""
    agent = create_capacity_guard_agent(db)
    response = agent.sugerir_tradeoffs(num_tarefas_liberar)
    return AgentResponse(response=response)


@router.get("/big-rocks/analise", response_model=AgentResponse)
async def analisar_big_rocks(db: Session = Depends(get_db)):
    """Analisa a distribuição de tarefas entre Big Rocks."""
    agent = create_capacity_guard_agent(db)
    response = agent.analisar_big_rocks()
    return AgentResponse(response=response)
