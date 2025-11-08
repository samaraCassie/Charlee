# backend/api/main.py - ATUALIZADO COM CORS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.config import engine, Base
from api.routes import (
    big_rocks,
    tarefas,
    agent as agent_routes,
    wellness,
    capacity,
    priorizacao,
    inbox,
    analytics,
    settings
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    yield
    print("👋 Shutting down Charlee...")


app = FastAPI(
    title="Charlee API",
    description="API do sistema de inteligência pessoal Charlee",
    version="2.0.0",
    lifespan=lifespan
)

# ========================================
# CORS CONFIGURATION - CRÍTICO
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server
        "http://localhost:5173",  # Vite alternative port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],  # Authorization, Content-Type, etc
    expose_headers=["*"],
)

# Include routers V1
app.include_router(big_rocks.router, prefix="/api/v1/big-rocks", tags=["Big Rocks"])
app.include_router(tarefas.router, prefix="/api/v1/tarefas", tags=["Tarefas"])
app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])

# Include routers V2
app.include_router(wellness.router, prefix="/api/v2/wellness", tags=["Wellness (V2)"])
app.include_router(capacity.router, prefix="/api/v2/capacity", tags=["Capacity (V2)"])
app.include_router(priorizacao.router, prefix="/api/v2/priorizacao", tags=["Priorização (V2)"])
app.include_router(inbox.router, prefix="/api/v2/inbox", tags=["Inbox (V2)"])
app.include_router(analytics.router, prefix="/api/v2/analytics", tags=["Analytics (V2)"])
app.include_router(settings.router, prefix="/api/v2/settings", tags=["Settings (V2)"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🌸 Charlee API - Sistema de Inteligência Pessoal",
        "version": "2.0.0",
        "status": "online",
        "cors": "enabled",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "charlee-backend",
        "version": "2.0.0"
    }


# ========================================
# INBOX ROUTES - CORRIGIDO
# ========================================

# backend/api/routes/inbox.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date, timedelta
from database.config import get_db
from database import schemas, crud

router = APIRouter()


class InboxResponse(BaseModel):
    """Response do inbox rápido."""
    inbox_text: str
    tarefas: List[schemas.TarefaResponse]
    total: int


@router.get("/rapido", response_model=InboxResponse)
async def inbox_rapido(
    limite: int = 10,
    db: Session = Depends(get_db)
):
    """
    Inbox Rápido - Top tarefas priorizadas para hoje.
    """
    try:
        from skills.priorizacao import create_sistema_priorizacao
        
        sistema = create_sistema_priorizacao(db)
        
        # Gerar inbox em texto
        inbox_texto = sistema.gerar_inbox_rapido(limite=limite)
        
        # Obter tarefas priorizadas
        tarefas_priorizadas = sistema.priorizar_tarefas(
            status="Pendente",
            limite=limite
        )
        
        return {
            "inbox_text": inbox_texto,
            "tarefas": tarefas_priorizadas,
            "total": len(tarefas_priorizadas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar inbox: {str(e)}")


@router.get("/hoje", response_model=schemas.TarefaListResponse)
async def tarefas_hoje(db: Session = Depends(get_db)):
    """Tarefas com deadline para hoje."""
    try:
        today = date.today()
        
        # Buscar todas tarefas pendentes
        tarefas = crud.get_tarefas(db, status="Pendente", limit=100)
        
        # Filtrar por deadline hoje
        tarefas_hoje = [
            t for t in tarefas 
            if t.deadline and t.deadline == today
        ]
        
        return {
            "total": len(tarefas_hoje),
            "tarefas": tarefas_hoje
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao buscar tarefas de hoje: {str(e)}"
        )


@router.get("/atrasadas", response_model=schemas.TarefaListResponse)
async def tarefas_atrasadas(db: Session = Depends(get_db)):
    """Tarefas com deadline já passado."""
    try:
        today = date.today()
        
        # Buscar todas tarefas pendentes
        tarefas = crud.get_tarefas(db, status="Pendente", limit=100)
        
        # Filtrar por deadline atrasada
        tarefas_atrasadas = [
            t for t in tarefas 
            if t.deadline and t.deadline < today
        ]
        
        # Ordenar por deadline (mais antigo primeiro)
        tarefas_atrasadas.sort(key=lambda t: t.deadline)
        
        return {
            "total": len(tarefas_atrasadas),
            "tarefas": tarefas_atrasadas
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar tarefas atrasadas: {str(e)}"
        )


@router.get("/proxima-semana", response_model=schemas.TarefaListResponse)
async def tarefas_proxima_semana(db: Session = Depends(get_db)):
    """Tarefas com deadline nos próximos 7 dias."""
    try:
        today = date.today()
        next_week = today + timedelta(days=7)
        
        # Buscar tarefas pendentes
        tarefas = crud.get_tarefas(db, status="Pendente", limit=100)
        
        # Filtrar por deadline próxima semana
        tarefas_semana = [
            t for t in tarefas 
            if t.deadline and today <= t.deadline <= next_week
        ]
        
        # Ordenar por deadline
        tarefas_semana.sort(key=lambda t: t.deadline)
        
        return {
            "total": len(tarefas_semana),
            "tarefas": tarefas_semana
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar tarefas da próxima semana: {str(e)}"
        )


# ========================================
# TESTE RÁPIDO NO TERMINAL
# ========================================

# Para testar CORS:
# curl -H "Origin: http://localhost:3000" \
#      -H "Access-Control-Request-Method: GET" \
#      -H "Access-Control-Request-Headers: Content-Type" \
#      -X OPTIONS \
#      http://localhost:8000/api/v2/inbox/hoje -v

# Deve retornar headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: *
# Access-Control-Allow-Headers: *