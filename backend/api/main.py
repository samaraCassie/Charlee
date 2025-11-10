# backend/api/main.py

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
    settings,
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
    lifespan=lifespan,
)

# ========================================
# CORS CONFIGURATION
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
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ========================================
# ROUTERS V1
# ========================================
app.include_router(big_rocks.router, prefix="/api/v1/big-rocks", tags=["Big Rocks"])
app.include_router(tarefas.router, prefix="/api/v1/tarefas", tags=["Tarefas"])
app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])

# ========================================
# ROUTERS V2
# ========================================
app.include_router(wellness.router, prefix="/api/v2/wellness", tags=["Wellness (V2)"])
app.include_router(capacity.router, prefix="/api/v2/capacity", tags=["Capacity (V2)"])
app.include_router(priorizacao.router, prefix="/api/v2/priorizacao", tags=["Priorização (V2)"])
app.include_router(inbox.router, prefix="/api/v2/inbox", tags=["Inbox (V2)"])
app.include_router(analytics.router, prefix="/api/v2/analytics", tags=["Analytics (V2)"])
app.include_router(settings.router, prefix="/api/v2/settings", tags=["Settings (V2)"])


# ========================================
# BASIC ENDPOINTS
# ========================================
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🌸 Charlee API - Sistema de Inteligência Pessoal",
        "version": "2.0.0",
        "status": "online",
        "cors": "enabled",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "charlee-backend", "version": "2.0.0"}
