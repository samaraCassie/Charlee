"""FastAPI main application."""

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
    priorizacao
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app."""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    yield

    # Shutdown
    print("👋 Shutting down Charlee...")


# Create FastAPI app
app = FastAPI(
    title="Charlee API",
    description="API do sistema de inteligência pessoal Charlee",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers V1
app.include_router(big_rocks.router, prefix="/api/v1/big-rocks", tags=["Big Rocks"])
app.include_router(tarefas.router, prefix="/api/v1/tarefas", tags=["Tarefas"])
app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])

# Include routers V2
app.include_router(wellness.router, prefix="/api/v2/wellness", tags=["Wellness (V2)"])
app.include_router(capacity.router, prefix="/api/v2/capacity", tags=["Capacity (V2)"])
app.include_router(priorizacao.router, prefix="/api/v2/priorizacao", tags=["Priorização (V2)"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🌸 Charlee API - Sistema de Inteligência Pessoal",
        "version": "0.2.0",
        "v1": "Gestão de tarefas e Big Rocks",
        "v2": "Wellness (ciclo) + Capacity Guard (sobrecarga)",
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "charlee-backend"}
