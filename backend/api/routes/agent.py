"""Agent API routes for interacting with Charlee."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.config import get_db
from agent.core_agent import create_charlee_agent

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    user_id: str = "samara"
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_charlee(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with Charlee agent.

    Send a message to Charlee and get a response.
    The agent has access to all Big Rocks and Tarefas tools.
    The agent maintains conversation history and memory across sessions.
    """
    try:
        # Create Charlee agent with session support
        charlee = create_charlee_agent(
            db=db,
            user_id=request.user_id,
            session_id=request.session_id
        )

        # Get response from agent (with history and memory)
        response = charlee.run(request.message)

        return ChatResponse(
            response=response.content,
            session_id=charlee.session_id or "default"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with agent: {str(e)}")


@router.get("/tools")
async def list_agent_tools():
    """List all available tools for the Charlee agent."""
    return {
        "tools": [
            {
                "name": "listar_big_rocks",
                "description": "Lista todos os Big Rocks (pilares de vida) cadastrados"
            },
            {
                "name": "criar_big_rock",
                "description": "Cria um novo Big Rock (pilar de vida)"
            },
            {
                "name": "listar_tarefas",
                "description": "Lista tarefas com filtros opcionais"
            },
            {
                "name": "criar_tarefa",
                "description": "Cria uma nova tarefa"
            },
            {
                "name": "marcar_tarefa_concluida",
                "description": "Marca uma tarefa como concluída"
            },
            {
                "name": "atualizar_tarefa",
                "description": "Atualiza uma tarefa existente"
            }
        ]
    }
