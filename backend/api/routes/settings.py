"""Settings API routes - Configurações do usuário e sistema."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database.config import get_db, settings as app_settings
from database.models import User, UserSettings as DBUserSettings
from services.system_monitor import system_monitor

router = APIRouter()


class UserSettings(BaseModel):
    """Configurações do usuário."""

    user_id: int
    username: str
    display_name: str
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
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter configurações do usuário."""
    # Get or create settings
    db_settings = db.query(DBUserSettings).filter(DBUserSettings.user_id == current_user.id).first()

    if not db_settings:
        # Create default settings
        db_settings = DBUserSettings(user_id=current_user.id)
        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)

    # Parse integrations JSON
    integrations = db_settings.integrations or {}

    return UserSettings(
        user_id=current_user.id,
        username=current_user.username,
        display_name=current_user.full_name or current_user.username,
        email=current_user.email,
        timezone=db_settings.timezone,
        language=db_settings.language,
        notifications_enabled=db_settings.notifications_enabled,
        email_notifications=db_settings.email_notifications,
        push_notifications=db_settings.push_notifications,
        theme=db_settings.theme,
        density=db_settings.density,
        work_hours_per_day=db_settings.work_hours_per_day,
        work_days_per_week=db_settings.work_days_per_week,
        planning_horizon_days=db_settings.planning_horizon_days,
        cycle_tracking_enabled=db_settings.cycle_tracking_enabled,
        cycle_length_days=db_settings.cycle_length_days,
        google_calendar_enabled=integrations.get("google_calendar", {}).get("enabled", False),
        notion_enabled=integrations.get("notion", {}).get("enabled", False),
        trello_enabled=integrations.get("trello", {}).get("enabled", False),
    )


@router.patch("/user", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualizar configurações do usuário."""
    # Get or create settings
    db_settings = db.query(DBUserSettings).filter(DBUserSettings.user_id == current_user.id).first()

    if not db_settings:
        db_settings = DBUserSettings(user_id=current_user.id)
        db.add(db_settings)

    # Update fields
    db_settings.timezone = settings.timezone
    db_settings.language = settings.language
    db_settings.notifications_enabled = settings.notifications_enabled
    db_settings.email_notifications = settings.email_notifications
    db_settings.push_notifications = settings.push_notifications
    db_settings.theme = settings.theme
    db_settings.density = settings.density
    db_settings.work_hours_per_day = settings.work_hours_per_day
    db_settings.work_days_per_week = settings.work_days_per_week
    db_settings.planning_horizon_days = settings.planning_horizon_days
    db_settings.cycle_tracking_enabled = settings.cycle_tracking_enabled
    db_settings.cycle_length_days = settings.cycle_length_days

    # Update integrations
    integrations = db_settings.integrations or {}
    integrations["google_calendar"] = {"enabled": settings.google_calendar_enabled}
    integrations["notion"] = {"enabled": settings.notion_enabled}
    integrations["trello"] = {"enabled": settings.trello_enabled}
    db_settings.integrations = integrations

    db.commit()
    db.refresh(db_settings)

    return settings


@router.get("/system", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter estatísticas do sistema."""
    from database.models import BigRock, Task

    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    total_big_rocks = db.query(BigRock).filter(BigRock.user_id == current_user.id).count()
    total_users = db.query(User).count()

    # Get uptime from system monitor
    uptime_seconds = system_monitor.get_uptime_seconds()

    # Get last backup info
    last_backup = None
    backup_info = system_monitor.get_last_backup_info()
    if backup_info:
        last_backup = backup_info.get("created_at")

    return {
        "version": "3.3.0",  # Updated to reflect multimodal system
        "uptime_seconds": uptime_seconds,
        "total_users": total_users,
        "total_tasks": total_tasks,
        "total_big_rocks": total_big_rocks,
        "last_backup": last_backup,
    }


@router.post("/backup")
async def create_backup(
    current_user: User = Depends(get_current_user),
):
    """Criar backup manual do banco de dados."""
    try:
        backup_path = system_monitor.create_database_backup(app_settings.database_url)

        if backup_path:
            # Cleanup old backups (keep last 5)
            removed = system_monitor.cleanup_old_backups(keep_last_n=5)

            backup_info = system_monitor.get_last_backup_info()
            return {
                "success": True,
                "message": "Backup criado com sucesso",
                "backup_info": backup_info,
                "old_backups_removed": removed,
            }
        else:
            return {
                "success": False,
                "message": "Falha ao criar backup",
                "error": "Verifique os logs para mais detalhes",
            }

    except Exception as e:
        return {"success": False, "message": "Erro ao criar backup", "error": str(e)}


@router.post("/reset")
async def reset_user_data(
    confirm: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resetar todos os dados do usuário (CUIDADO!)."""
    if not confirm:
        return {
            "error": "Confirmação necessária",
            "message": "Para resetar os dados, envie confirm=true",
        }

    # Criar backup antes de resetar
    backup_path = system_monitor.create_database_backup(
        app_settings.database_url, backup_name=f"pre_reset_{current_user.username}.sql"
    )

    if not backup_path:
        return {
            "error": "Backup falhou",
            "message": "Por segurança, não é possível resetar sem criar backup",
            "status": "safe",
        }

    # TODO: Implementar reset real (deletar tasks, big rocks, etc do usuário)
    return {
        "message": "Reset de dados ainda não totalmente implementado",
        "status": "safe",
        "backup_created": backup_path,
    }


@router.post("/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exportar todos os dados do usuário."""
    from database.models import BigRock, Task

    # Buscar todos os dados
    big_rocks = db.query(BigRock).filter(BigRock.user_id == current_user.id).all()
    tarefas = db.query(Task).filter(Task.user_id == current_user.id).all()

    export_data = {
        "version": "2.0.0",
        "exported_at": str(date.today()),
        "big_rocks": [
            {
                "id": br.id,
                "nome": br.nome,
                "cor": br.cor,
                "ativo": br.ativo,
                "criado_em": str(br.criado_em),
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
                "concluido_em": str(t.concluido_em) if t.concluido_em else None,
            }
            for t in tarefas
        ],
    }

    return export_data


@router.get("/integrations")
async def get_integrations_status():
    """Status das integrações externas."""
    return {
        "google_calendar": {"enabled": False, "connected": False, "last_sync": None},
        "notion": {"enabled": False, "connected": False, "last_sync": None},
        "trello": {"enabled": False, "connected": False, "last_sync": None},
        "github": {"enabled": False, "connected": False, "last_sync": None},
    }


@router.post("/integrations/{service}/connect")
async def connect_integration(service: str):
    """Conectar uma integração externa."""
    return {
        "message": f"Integração com {service} ainda não implementada",
        "status": "coming_soon",
    }
