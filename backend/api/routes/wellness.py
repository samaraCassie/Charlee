"""Wellness API routes - Ciclo menstrual e bem-estar."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.config import get_db
from agent.specialized_agents.cycle_aware_agent import create_cycle_aware_agent

router = APIRouter()


class CicloRequest(BaseModel):
    """Request para registrar fase do ciclo."""

    data_inicio: str
    fase: str
    nivel_energia: int | None = None
    nivel_foco: int | None = None
    nivel_criatividade: int | None = None
    sintomas: str | None = None
    notas: str | None = None


class AgentResponse(BaseModel):
    """Response padrão dos agentes."""

    response: str


@router.post("/ciclo/registrar", response_model=AgentResponse)
async def registrar_fase_ciclo(request: CicloRequest, db: Session = Depends(get_db)):
    """Registra uma nova fase do ciclo menstrual."""
    agent = create_cycle_aware_agent(db)

    response = agent.registrar_fase_ciclo(
        data_inicio=request.data_inicio,
        fase=request.fase,
        nivel_energia=request.nivel_energia,
        nivel_foco=request.nivel_foco,
        nivel_criatividade=request.nivel_criatividade,
        sintomas=request.sintomas,
        notas=request.notas,
    )

    return AgentResponse(response=response)


@router.get("/ciclo/atual", response_model=AgentResponse)
async def obter_fase_atual(db: Session = Depends(get_db)):
    """Obtém a fase atual do ciclo e recomendações."""
    agent = create_cycle_aware_agent(db)
    response = agent.obter_fase_atual()
    return AgentResponse(response=response)


@router.get("/ciclo/sugestoes", response_model=AgentResponse)
async def sugestoes_fase(fase: str | None = None, db: Session = Depends(get_db)):
    """Obtém sugestões de tarefas para a fase do ciclo."""
    agent = create_cycle_aware_agent(db)
    response = agent.sugerir_tarefas_fase(fase)
    return AgentResponse(response=response)


@router.get("/ciclo/analise-carga", response_model=AgentResponse)
async def analisar_carga_ciclo(dias_futuro: int = 7, db: Session = Depends(get_db)):
    """Analisa se a carga está adequada para a fase atual."""
    agent = create_cycle_aware_agent(db)
    response = agent.analisar_carga_para_fase(dias_futuro)
    return AgentResponse(response=response)
