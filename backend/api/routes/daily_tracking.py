"""Daily Tracking API routes."""

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent.specialized_agents.daily_tracking_agent import create_daily_tracking_agent
from database.config import get_db

# Configure structured logging
logger = logging.getLogger(__name__)

router = APIRouter()


class DailyRecordRequest(BaseModel):
    """Request model for daily record."""

    data: Optional[str] = Field(None, description="Data no formato YYYY-MM-DD (padrão: hoje)")
    horas_sono: Optional[float] = Field(None, ge=0, le=24, description="Horas de sono")
    qualidade_sono: Optional[int] = Field(None, ge=1, le=10, description="Qualidade do sono 1-10")
    energia_manha: Optional[int] = Field(None, ge=1, le=10, description="Energia pela manhã 1-10")
    energia_tarde: Optional[int] = Field(None, ge=1, le=10, description="Energia à tarde 1-10")
    energia_noite: Optional[int] = Field(None, ge=1, le=10, description="Energia à noite 1-10")
    horas_deep_work: Optional[float] = Field(
        None, ge=0, le=24, description="Horas de trabalho focado"
    )
    notas: Optional[str] = Field(None, description="Observações livres")


class DailyRecordResponse(BaseModel):
    """Response model for daily record."""

    message: str
    data: str


class AnalysisRequest(BaseModel):
    """Request model for analysis."""

    dias: int = Field(7, ge=1, le=90, description="Número de dias para analisar")


@router.post("/record", response_model=DailyRecordResponse)
async def create_daily_record(request: DailyRecordRequest, db: Session = Depends(get_db)):
    """
    Registra dados do dia (hoje ou data específica).

    Coleta informações sobre:
    - Sono (horas e qualidade)
    - Energia em diferentes períodos
    - Produtividade (deep work)
    - Notas livres

    Automaticamente:
    - Conta tarefas concluídas do dia
    - Vincula com fase do ciclo menstrual
    - Atualiza padrões identificados
    """
    try:
        agent = create_daily_tracking_agent(db)

        # Call agent tool
        response = agent.registrar_dia(
            data=request.data,
            horas_sono=request.horas_sono,
            qualidade_sono=request.qualidade_sono,
            energia_manha=request.energia_manha,
            energia_tarde=request.energia_tarde,
            energia_noite=request.energia_noite,
            horas_deep_work=request.horas_deep_work,
            notas=request.notas,
        )

        return DailyRecordResponse(message=response, data=request.data or str(date.today()))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating daily record: {str(e)}")


@router.get("/today")
async def get_today_record(db: Session = Depends(get_db)):
    """
    Obtém o registro de hoje (se existir).

    Retorna:
    - Dados de sono
    - Níveis de energia
    - Produtividade
    - Fase do ciclo
    - Notas
    """
    try:
        agent = create_daily_tracking_agent(db)
        response = agent.obter_registro_hoje()

        return {"record": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting today's record: {str(e)}")


@router.get("/analysis")
async def get_analysis(dias: int = 7, db: Session = Depends(get_db)):
    """
    Analisa tendências dos últimos N dias.

    Retorna:
    - Médias de sono, energia, produtividade
    - Melhor e pior dia
    - Insights sobre padrões

    Parâmetros:
    - dias: Número de dias para analisar (padrão: 7, máx: 90)
    """
    try:
        if dias > 90:
            raise HTTPException(status_code=400, detail="Maximum 90 days allowed")

        agent = create_daily_tracking_agent(db)
        response = agent.analise_ultimos_dias(dias=dias)

        return {"analysis": response}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing records: {str(e)}")


@router.get("/patterns")
async def identify_patterns(db: Session = Depends(get_db)):
    """
    Identifica padrões de produtividade baseados em dados históricos.

    Analisa:
    - Correlação entre sono e energia
    - Produtividade por fase do ciclo menstrual
    - Melhores horários de performance
    - Padrões comportamentais

    Atualiza automaticamente a tabela de padrões do ciclo.

    Requer: Pelo menos 7 dias de registros com dados de sono e energia.
    """
    try:
        agent = create_daily_tracking_agent(db)
        response = agent.identificar_padroes()

        return {"patterns": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying patterns: {str(e)}")


@router.get("/suggestions")
async def get_suggestions(db: Session = Depends(get_db)):
    """
    Sugere otimizações baseadas nos padrões identificados.

    Retorna sugestões personalizadas sobre:
    - Sono e descanso
    - Trabalho focado (deep work)
    - Consistência de registro
    - Adaptação ao ciclo menstrual

    Baseado em:
    - Dados históricos dos últimos 14 dias
    - Padrões identificados
    - Fase atual do ciclo
    - Correlações entre variáveis
    """
    try:
        agent = create_daily_tracking_agent(db)
        response = agent.sugerir_otimizacoes()

        return {"suggestions": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")


@router.get("/status")
async def get_tracking_status(db: Session = Depends(get_db)):
    """
    Retorna status geral do sistema de tracking.

    Informações:
    - Número total de registros
    - Consistência (% de dias com registro)
    - Última atualização
    - Padrões identificados disponíveis
    """
    try:
        from datetime import timedelta

        from database.models import CyclePatterns, DailyLog

        # Contar registros
        total_registros = db.query(DailyLog).count()

        # Calcular consistência (últimos 30 dias)
        data_inicio = date.today() - timedelta(days=30)
        registros_recentes = db.query(DailyLog).filter(DailyLog.date >= data_inicio).count()

        consistencia = (registros_recentes / 30) * 100

        # Último registro
        ultimo_registro = db.query(DailyLog).order_by(DailyLog.date.desc()).first()

        # Padrões identificados
        padroes = db.query(CyclePatterns).all()

        return {
            "total_records": total_registros,
            "consistency_30days": f"{consistencia:.1f}%",
            "last_record_date": str(ultimo_registro.date) if ultimo_registro else None,
            "patterns_identified": len(padroes),
            "patterns": (
                [
                    {
                        "fase": p.phase,
                        "produtividade_media": p.average_productivity,
                        "confianca_score": p.confidence_score,
                        "amostras": p.samples_used,
                    }
                    for p in padroes
                ]
                if padroes
                else []
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tracking status: {str(e)}")


class ReminderConfigRequest(BaseModel):
    """Request model for reminder configuration."""

    enabled: bool = Field(..., description="Ativar/desativar lembretes")
    preferred_time: Optional[str] = Field(None, description="Horário preferido (HH:MM)")


@router.post("/reminder/config")
async def configure_reminder(request: ReminderConfigRequest, db: Session = Depends(get_db)):
    """
    Configura lembretes diários para registro de dados.

    Ajuda a manter consistência no tracking incentivando
    registros regulares.

    Parâmetros:
    - enabled: Ativar ou desativar lembretes
    - preferred_time: Horário preferido para receber lembretes (formato HH:MM)

    Nota: Esta é uma configuração de intenção. A implementação real
    de notificações requer integração com sistema de notificações.
    """
    logger.info(
        "Configuring reminder",
        extra={"enabled": request.enabled, "preferred_time": request.preferred_time},
    )

    return {
        "message": "Configuração de lembrete salva com sucesso",
        "config": {
            "enabled": request.enabled,
            "preferred_time": request.preferred_time or "20:00",
            "status": "active" if request.enabled else "inactive",
        },
    }


@router.get("/reminder/status")
async def get_reminder_status(db: Session = Depends(get_db)):
    """
    Verifica status do lembrete diário.

    Retorna:
    - Se já registrou hoje
    - Últimos dias sem registro
    - Sugestão de quando registrar
    """
    try:
        from database.models import DailyLog

        logger.info("Checking reminder status")

        # Verificar se já registrou hoje
        hoje = date.today()
        registro_hoje = db.query(DailyLog).filter(DailyLog.date == hoje).first()

        # Contar dias consecutivos sem registro (últimos 7 dias)
        dias_sem_registro = []
        for i in range(1, 8):
            data_check = hoje - timedelta(days=i)
            registro = db.query(DailyLog).filter(DailyLog.date == data_check).first()
            if not registro:
                dias_sem_registro.append(str(data_check))

        # Status do lembrete
        precisa_lembrete = not registro_hoje
        mensagem = (
            "Você já registrou hoje! ✓" if registro_hoje else "Lembre-se de registrar seu dia!"
        )

        logger.info(
            "Reminder status checked",
            extra={"recorded_today": bool(registro_hoje), "missing_count": len(dias_sem_registro)},
        )

        return {
            "needs_reminder": precisa_lembrete,
            "recorded_today": bool(registro_hoje),
            "today_date": str(hoje),
            "missing_days_last_week": dias_sem_registro,
            "missing_count": len(dias_sem_registro),
            "message": mensagem,
            "suggestion": (
                "Registre antes de dormir para melhor precisão nos dados de sono."
                if precisa_lembrete
                else None
            ),
        }

    except Exception as e:
        logger.error(f"Error checking reminder status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking reminder status: {str(e)}")


@router.get("/insights")
async def get_insights(days: int = 30, db: Session = Depends(get_db)):
    """
    Retorna dados estruturados para dashboard de insights.

    Fornece dados formatados para visualização em gráficos:
    - Séries temporais de sono, energia e produtividade
    - Médias móveis (7 dias)
    - Tendências e comparações
    - Correlações entre variáveis

    Parâmetros:
    - days: Número de dias para retornar (padrão: 30, máx: 90)

    Formato de retorno otimizado para frontend charts (Chart.js, Recharts, etc).
    """
    logger.info(f"Generating insights for {days} days")

    if days > 90:
        logger.warning(f"Requested days ({days}) exceeds maximum (90)")
        raise HTTPException(status_code=400, detail="Maximum 90 days allowed")

    try:
        import statistics

        from database.models import DailyLog

        # Buscar registros
        data_inicio = date.today() - timedelta(days=days)
        registros = (
            db.query(DailyLog)
            .filter(DailyLog.date >= data_inicio)
            .order_by(DailyLog.date.asc())
            .all()
        )

        logger.info(f"Found {len(registros)} records for insights")

        if not registros:
            return {
                "message": "No data available for the requested period",
                "days_requested": days,
                "records_found": 0,
            }

        # Preparar séries temporais
        time_series = {
            "dates": [],
            "sleep_hours": [],
            "sleep_quality": [],
            "energy_morning": [],
            "energy_afternoon": [],
            "energy_evening": [],
            "deep_work_hours": [],
            "tasks_completed": [],
        }

        for reg in registros:
            time_series["dates"].append(str(reg.date))
            time_series["sleep_hours"].append(reg.sleep_hours)
            time_series["sleep_quality"].append(reg.sleep_quality)
            time_series["energy_morning"].append(reg.morning_energy)
            time_series["energy_afternoon"].append(reg.afternoon_energy)
            time_series["energy_evening"].append(reg.evening_energy)
            time_series["deep_work_hours"].append(reg.deep_work_hours)
            time_series["tasks_completed"].append(reg.completed_tasks)

        # Calcular médias móveis (7 dias)
        def moving_average(data: List[Optional[float]], window: int = 7) -> List[Optional[float]]:
            """Calculate moving average, handling None values."""
            result = []
            for i in range(len(data)):
                window_data = [x for x in data[max(0, i - window + 1) : i + 1] if x is not None]
                if window_data:
                    result.append(round(statistics.mean(window_data), 2))
                else:
                    result.append(None)
            return result

        moving_averages = {
            "sleep_hours_ma": moving_average(time_series["sleep_hours"]),
            "sleep_quality_ma": moving_average(time_series["sleep_quality"]),
            "energy_morning_ma": moving_average(time_series["energy_morning"]),
            "deep_work_hours_ma": moving_average(time_series["deep_work_hours"]),
        }

        # Calcular estatísticas gerais
        def safe_stats(data: List[Optional[float]]) -> Dict:
            """Calculate stats filtering None values."""
            clean_data = [x for x in data if x is not None]
            if not clean_data:
                return {"mean": None, "min": None, "max": None}
            return {
                "mean": round(statistics.mean(clean_data), 2),
                "min": min(clean_data),
                "max": max(clean_data),
            }

        stats = {
            "sleep_hours": safe_stats(time_series["sleep_hours"]),
            "sleep_quality": safe_stats(time_series["sleep_quality"]),
            "energy_morning": safe_stats(time_series["energy_morning"]),
            "deep_work_hours": safe_stats(time_series["deep_work_hours"]),
            "tasks_completed": safe_stats(time_series["tasks_completed"]),
        }

        # Calcular correlação sono x energia (simplificada)
        sleep_data = [x for x in time_series["sleep_hours"] if x is not None]
        energy_data = [x for x in time_series["energy_morning"] if x is not None]

        correlation_strength = "insufficient_data"
        if len(sleep_data) >= 7 and len(energy_data) >= 7:
            # Correlação simples baseada em tendências
            avg_sleep = statistics.mean(sleep_data)
            above_avg_sleep = [
                i
                for i, s in enumerate(time_series["sleep_hours"])
                if s is not None and s > avg_sleep
            ]

            if above_avg_sleep and len(
                [i for i in above_avg_sleep if i < len(time_series["energy_morning"])]
            ):
                energy_on_good_sleep = [
                    time_series["energy_morning"][i]
                    for i in above_avg_sleep
                    if i < len(time_series["energy_morning"])
                    and time_series["energy_morning"][i] is not None
                ]
                if energy_on_good_sleep:
                    avg_energy_good_sleep = statistics.mean(energy_on_good_sleep)
                    avg_energy_overall = statistics.mean(energy_data)

                    if avg_energy_good_sleep > avg_energy_overall * 1.1:
                        correlation_strength = "strong_positive"
                    elif avg_energy_good_sleep > avg_energy_overall:
                        correlation_strength = "moderate_positive"
                    else:
                        correlation_strength = "weak"

        # Tendências (comparar primeira metade vs segunda metade)
        mid_point = len(registros) // 2
        if mid_point > 0:
            first_half_energy = [
                x for x in time_series["energy_morning"][:mid_point] if x is not None
            ]
            second_half_energy = [
                x for x in time_series["energy_morning"][mid_point:] if x is not None
            ]

            trend = "stable"
            if first_half_energy and second_half_energy:
                diff = statistics.mean(second_half_energy) - statistics.mean(first_half_energy)
                if diff > 1:
                    trend = "improving"
                elif diff < -1:
                    trend = "declining"
        else:
            trend = "insufficient_data"

        return {
            "period": {
                "start_date": str(data_inicio),
                "end_date": str(date.today()),
                "days_requested": days,
                "records_found": len(registros),
            },
            "time_series": time_series,
            "moving_averages": moving_averages,
            "statistics": stats,
            "insights": {
                "sleep_energy_correlation": correlation_strength,
                "energy_trend": trend,
                "most_productive_phase": _get_most_productive_phase(registros),
                "consistency_score": round((len(registros) / days) * 100, 1),
            },
            "chart_config": {
                "recommended_chart_types": {
                    "sleep_and_energy": "line",
                    "deep_work": "bar",
                    "tasks_completed": "bar",
                    "phase_comparison": "radar",
                },
                "color_palette": {
                    "sleep": "#4F46E5",
                    "energy": "#F59E0B",
                    "productivity": "#10B981",
                    "quality": "#8B5CF6",
                },
            },
        }

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


def _get_most_productive_phase(registros: List) -> str:
    """Helper to identify most productive cycle phase."""
    from collections import defaultdict

    phase_productivity = defaultdict(list)

    for reg in registros:
        if reg.cycle_phase and reg.deep_work_hours:
            phase_productivity[reg.cycle_phase].append(reg.deep_work_hours)

    if not phase_productivity:
        return "not_enough_data"

    avg_by_phase = {
        phase: sum(hours) / len(hours) for phase, hours in phase_productivity.items() if hours
    }

    if not avg_by_phase:
        return "not_enough_data"

    return max(avg_by_phase, key=avg_by_phase.get)
