"""Daily Tracking API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from database.config import get_db
from agent.specialized_agents.daily_tracking_agent import create_daily_tracking_agent

router = APIRouter()


class DailyRecordRequest(BaseModel):
    """Request model for daily record."""
    data: Optional[str] = Field(None, description="Data no formato YYYY-MM-DD (padrão: hoje)")
    horas_sono: Optional[float] = Field(None, ge=0, le=24, description="Horas de sono")
    qualidade_sono: Optional[int] = Field(None, ge=1, le=10, description="Qualidade do sono 1-10")
    energia_manha: Optional[int] = Field(None, ge=1, le=10, description="Energia pela manhã 1-10")
    energia_tarde: Optional[int] = Field(None, ge=1, le=10, description="Energia à tarde 1-10")
    energia_noite: Optional[int] = Field(None, ge=1, le=10, description="Energia à noite 1-10")
    horas_deep_work: Optional[float] = Field(None, ge=0, le=24, description="Horas de trabalho focado")
    notas: Optional[str] = Field(None, description="Observações livres")


class DailyRecordResponse(BaseModel):
    """Response model for daily record."""
    message: str
    data: str


class AnalysisRequest(BaseModel):
    """Request model for analysis."""
    dias: int = Field(7, ge=1, le=90, description="Número de dias para analisar")


@router.post("/record", response_model=DailyRecordResponse)
async def create_daily_record(
    request: DailyRecordRequest,
    db: Session = Depends(get_db)
):
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
            notas=request.notas
        )

        return DailyRecordResponse(
            message=response,
            data=request.data or str(date.today())
        )

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
async def get_analysis(
    dias: int = 7,
    db: Session = Depends(get_db)
):
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
        from database.models import RegistroDiario, PadroesCiclo
        from datetime import timedelta

        # Contar registros
        total_registros = db.query(RegistroDiario).count()

        # Calcular consistência (últimos 30 dias)
        data_inicio = date.today() - timedelta(days=30)
        registros_recentes = db.query(RegistroDiario).filter(
            RegistroDiario.data >= data_inicio
        ).count()

        consistencia = (registros_recentes / 30) * 100

        # Último registro
        ultimo_registro = db.query(RegistroDiario).order_by(
            RegistroDiario.data.desc()
        ).first()

        # Padrões identificados
        padroes = db.query(PadroesCiclo).all()

        return {
            "total_records": total_registros,
            "consistency_30days": f"{consistencia:.1f}%",
            "last_record_date": str(ultimo_registro.data) if ultimo_registro else None,
            "patterns_identified": len(padroes),
            "patterns": [
                {
                    "fase": p.fase,
                    "produtividade_media": p.produtividade_media,
                    "confianca_score": p.confianca_score,
                    "amostras": p.amostras_usadas
                }
                for p in padroes
            ] if padroes else []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tracking status: {str(e)}")
