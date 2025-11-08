"""Analytics API routes - Métricas e estatísticas."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Dict, List
from datetime import date, timedelta
from database.config import get_db
from database.models import Tarefa, BigRock

router = APIRouter()


class WeeklyStats(BaseModel):
    """Estatísticas semanais."""
    day: str
    completed: int
    pending: int


class MonthlyStats(BaseModel):
    """Estatísticas mensais."""
    month: str
    tasks: int


class BigRockDistribution(BaseModel):
    """Distribuição por Big Rock."""
    name: str
    value: int
    color: str


class ProductivityStats(BaseModel):
    """Estatísticas de produtividade."""
    completion_rate: float
    avg_time_per_task: float
    productivity_trend: float
    overdue_tasks: int


@router.get("/weekly", response_model=List[WeeklyStats])
async def weekly_stats(db: Session = Depends(get_db)):
    """Estatísticas dos últimos 7 dias."""
    today = date.today()
    stats = []
    
    days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
    
    for i in range(7):
        day_date = today - timedelta(days=6-i)
        
        # Contar tarefas concluídas neste dia
        completed = db.query(Tarefa).filter(
            Tarefa.status == "Concluída",
            func.date(Tarefa.concluido_em) == day_date
        ).count()
        
        # Contar tarefas pendentes neste dia
        pending = db.query(Tarefa).filter(
            Tarefa.status == "Pendente",
            func.date(Tarefa.deadline) == day_date
        ).count()
        
        stats.append({
            "day": days[day_date.weekday()],
            "completed": completed,
            "pending": pending
        })
    
    return stats


@router.get("/monthly", response_model=List[MonthlyStats])
async def monthly_stats(db: Session = Depends(get_db)):
    """Estatísticas dos últimos 6 meses."""
    today = date.today()
    stats = []
    
    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for i in range(6):
        # Calcular mês
        month_date = today - timedelta(days=30*(5-i))
        month_start = month_date.replace(day=1)
        
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1)
        
        # Contar tarefas concluídas no mês
        tasks = db.query(Tarefa).filter(
            Tarefa.status == "Concluída",
            Tarefa.concluido_em >= month_start,
            Tarefa.concluido_em < month_end
        ).count()
        
        stats.append({
            "month": months[month_date.month - 1],
            "tasks": tasks
        })
    
    return stats


@router.get("/big-rocks-distribution", response_model=List[BigRockDistribution])
async def big_rocks_distribution(db: Session = Depends(get_db)):
    """Distribuição de tarefas por Big Rock."""
    big_rocks = db.query(BigRock).filter(BigRock.ativo == True).all()
    
    distribution = []
    colors = ['#3b82f6', '#a855f7', '#22c55e', '#f59e0b', '#ef4444', '#94a3b8']
    
    for i, br in enumerate(big_rocks):
        # Contar tarefas deste Big Rock (últimos 30 dias)
        thirty_days_ago = date.today() - timedelta(days=30)
        
        count = db.query(Tarefa).filter(
            Tarefa.big_rock_id == br.id,
            Tarefa.status == "Concluída",
            Tarefa.concluido_em >= thirty_days_ago
        ).count()
        
        if count > 0:
            distribution.append({
                "name": br.nome,
                "value": count,
                "color": br.cor or colors[i % len(colors)]
            })
    
    return distribution


@router.get("/productivity", response_model=ProductivityStats)
async def productivity_stats(db: Session = Depends(get_db)):
    """Estatísticas gerais de produtividade."""
    
    # Total de tarefas
    total_tasks = db.query(Tarefa).count()
    
    # Tarefas concluídas
    completed_tasks = db.query(Tarefa).filter(
        Tarefa.status == "Concluída"
    ).count()
    
    # Taxa de conclusão
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Tarefas atrasadas
    overdue_tasks = db.query(Tarefa).filter(
        Tarefa.status == "Pendente",
        Tarefa.deadline < date.today()
    ).count()
    
    # Tempo médio por tarefa (estimativa)
    avg_time = 2.3  # TODO: Calcular baseado em horas reais quando disponível
    
    # Tendência de produtividade (comparar com mês anterior)
    # TODO: Implementar cálculo real
    productivity_trend = 12.0
    
    return {
        "completion_rate": round(completion_rate, 1),
        "avg_time_per_task": avg_time,
        "productivity_trend": productivity_trend,
        "overdue_tasks": overdue_tasks
    }


@router.get("/cycle-productivity")
async def cycle_productivity(db: Session = Depends(get_db)):
    """Produtividade por fase do ciclo menstrual."""
    
    # TODO: Implementar análise real quando houver dados de ciclo
    return {
        "menstrual": 65,
        "follicular": 92,
        "ovulation": 95,
        "luteal": 78
    }