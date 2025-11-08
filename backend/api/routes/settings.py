"""Settings API routes - Configurações do usuário e sistema."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database.config import get_db

router = APIRouter()


class UserSettings(BaseModel):
    """Configurações do usuário."""
    user_id: str = "samara"
    display_name: str = "Samara"
    email: Optional[str] = None
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"
    
    # Preferências de notificação
    notifications_enabled: bool = True
    email_notifications: bool = False
    push_notifications: bool = True
    
    # Preferências de exibição
    theme: str = "auto"  # auto, light, dark
    density: str = "comfortable"  # compact, comfortable, spacious
    
    # Preferências de planejamento
    work_hours_per_day: int = 8
    work_days_per_week: int = 5
    planning_horizon_days: int = 7
    
    # Ciclo menstrual
    cycle_tracking_enabled: bool = True
    cycle_length_days: int = 28
    
    # Integrações
    google_calendar_enabled: bool = False
    notion_enabled: bool = False
    trello_enabled: bool = False


class SystemStats(BaseModel):
    """Estatísticas do sistema."""
    version: str
    uptime_seconds: int
    total_users: int
    total_tasks: int
    total_big_rocks: int
    last_backup: Optional[str]


@router.get("/user", response_model=UserSettings)
async def get_user_settings(db: Session = Depends(get_db)):
    """Obter configurações do usuário."""
    # TODO: Buscar do banco quando implementar tabela de settings
    return UserSettings()


@router.patch("/user", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    db: Session = Depends(get_db)
):
    """Atualizar configurações do usuário."""
    # TODO: Salvar no banco
    return settings


@router.get("/system", response_model=SystemStats)
async def get_system_stats(db: Session = Depends(get_db)):
    """Obter estatísticas do sistema."""
    from database.models import Tarefa, BigRock
    
    total_tasks = db.query(Tarefa).count()
    total_big_rocks = db.query(BigRock).count()
    
    return {
        "version": "2.0.0",
        "uptime_seconds": 0,  # TODO: Implementar tracking de uptime
        "total_users": 1,
        "total_tasks": total_tasks,
        "total_big_rocks": total_big_rocks,
        "last_backup": None  # TODO: Implementar sistema de backup
    }


@router.post("/reset")
async def reset_user_data(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """Resetar todos os dados do usuário (CUIDADO!)."""
    if not confirm:
        return {
            "error": "Confirmação necessária",
            "message": "Para resetar os dados, envie confirm=true"
        }
    
    # TODO: Implementar reset seguro com backup
    return {
        "message": "Reset de dados ainda não implementado",
        "status": "safe"
    }


@router.post("/export")
async def export_user_data(db: Session = Depends(get_db)):
    """Exportar todos os dados do usuário."""
    from database.models import Tarefa, BigRock
    import json
    
    # Buscar todos os dados
    big_rocks = db.query(BigRock).all()
    tarefas = db.query(Tarefa).all()
    
    export_data = {
        "version": "2.0.0",
        "exported_at": str(date.today()),
        "big_rocks": [
            {
                "id": br.id,
                "nome": br.nome,
                "cor": br.cor,
                "ativo": br.ativo,
                "criado_em": str(br.criado_em)
            }
            for br in big_rocks
        ],
        "tarefas": [
            {
                "id": t.id,
                "descricao": t.descricao,
                "tipo": t.tipo,
                "status": t.status,
                "deadline": str(t.deadline) if t.deadline else None,
                "big_rock_id": t.big_rock_id,
                "criado_em": str(t.criado_em),
                "concluido_em": str(t.concluido_em) if t.concluido_em else None
            }
            for t in tarefas
        ]
    }
    
    return export_data


@router.get("/integrations")
async def get_integrations_status():
    """Status das integrações externas."""
    return {
        "google_calendar": {
            "enabled": False,
            "connected": False,
            "last_sync": None
        },
        "notion": {
            "enabled": False,
            "connected": False,
            "last_sync": None
        },
        "trello": {
            "enabled": False,
            "connected": False,
            "last_sync": None
        },
        "github": {
            "enabled": False,
            "connected": False,
            "last_sync": None
        }
    }


@router.post("/integrations/{service}/connect")
async def connect_integration(service: str):
    """Conectar uma integração externa."""
    return {
        "message": f"Integração com {service} ainda não implementada",
        "status": "coming_soon"
    }