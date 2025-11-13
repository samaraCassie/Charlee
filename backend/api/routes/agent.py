"""Agent API routes for interacting with Charlee."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agent.orchestrator import create_orchestrator
from api.auth.dependencies import get_current_user
from database.config import get_db
from database.models import User

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_charlee(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Chat with Charlee agent usando orquestração inteligente.

    Envia uma mensagem para Charlee e recebe uma resposta.
    O orquestrador analisa a mensagem e roteia para o agente especializado apropriado:
    - CycleAwareAgent: questões sobre ciclo menstrual, energia, bem-estar
    - CapacityGuardAgent: questões sobre carga de trabalho, capacidade, sobrecarga
    - CharleeAgent: tarefas gerais, Big Rocks, planejamento

    O agente mantém histórico de conversação e memória entre sessões.
    """
    try:
        # Create orchestrator (manages all specialized agents)
        orchestrator = create_orchestrator(
            db=db, user_id=current_user.username, session_id=request.session_id
        )

        # Route message to appropriate agent
        response = orchestrator.route_message(request.message)

        return ChatResponse(response=response, session_id=orchestrator.session_id or "default")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with agent: {str(e)}")


@router.get("/status")
async def get_orchestrator_status(
    session_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtém o status atual do orquestrador de agentes.

    Retorna informações sobre:
    - Sessão atual
    - Último agente utilizado
    - Tópico da conversa
    - Agentes disponíveis
    - Features de orquestração ativas
    """
    try:
        orchestrator = create_orchestrator(
            db=db, user_id=current_user.username, session_id=session_id
        )

        return orchestrator.get_status()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting orchestrator status: {str(e)}")


@router.post("/analyze-routing")
async def analyze_routing(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analisa como uma mensagem seria roteada pelo orquestrador SEM executá-la.

    Útil para debugging e entender o comportamento do sistema de orquestração.

    Retorna:
    - Intent detectado
    - Agente que seria usado
    - Razão da decisão
    - Palavras-chave que acionaram o intent
    - Se haverá consulta entre agentes
    """
    try:
        orchestrator = create_orchestrator(
            db=db, user_id=current_user.username, session_id=request.session_id
        )

        routing_decision = orchestrator.get_routing_decision(request.message)

        return routing_decision

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing routing: {str(e)}")


@router.get("/tools")
async def list_agent_tools():
    """Lista todas as ferramentas disponíveis para os agentes Charlee."""
    return {
        "tools": [
            {
                "name": "listar_big_rocks",
                "description": "Lista todos os Big Rocks (pilares de vida) cadastrados",
            },
            {"name": "criar_big_rock", "description": "Cria um novo Big Rock (pilar de vida)"},
            {"name": "listar_tarefas", "description": "Lista tarefas com filtros opcionais"},
            {"name": "criar_tarefa", "description": "Cria uma nova tarefa"},
            {"name": "marcar_tarefa_concluida", "description": "Marca uma tarefa como concluída"},
            {"name": "atualizar_tarefa", "description": "Atualiza uma tarefa existente"},
        ],
        "specialized_agents": [
            {
                "name": "CycleAwareAgent",
                "description": "Agente especializado em ciclo menstrual e bem-estar",
                "triggers": ["ciclo", "menstruação", "energia", "TPM", "ovulação", "fase"],
            },
            {
                "name": "CapacityGuardAgent",
                "description": "Agente especializado em gestão de capacidade e carga de trabalho",
                "triggers": [
                    "sobrecarga",
                    "capacidade",
                    "novo projeto",
                    "muito trabalho",
                    "trade-off",
                ],
            },
            {
                "name": "CharleeAgent",
                "description": "Agente principal para tarefas gerais, Big Rocks e planejamento",
                "triggers": ["default", "tarefas", "planejamento", "organização"],
            },
        ],
    }
