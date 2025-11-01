"""SQLAlchemy database models for Charlee V1."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from database.config import Base


class BigRock(Base):
    """
    Big Rocks - Pilares principais da vida.

    Representa as áreas/pilares fundamentais que estruturam
    a vida e as tarefas de Samara.
    """
    __tablename__ = "big_rocks"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cor = Column(String(20))  # Para UI futura (ex: "#FF5733")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tarefas = relationship("Tarefa", back_populates="big_rock")

    def __repr__(self):
        return f"<BigRock(id={self.id}, nome='{self.nome}')>"


class Tarefa(Base):
    """
    Tarefas - Tasks associadas aos Big Rocks.

    Representa tarefas que podem ser:
    - Compromisso Fixo: Eventos com hora marcada
    - Tarefa: To-do com deadline
    - Contínuo: Hábitos/rotinas sem deadline específico
    """
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(Text, nullable=False)
    tipo = Column(
        String(20),
        CheckConstraint("tipo IN ('Compromisso Fixo', 'Tarefa', 'Contínuo')"),
        default="Tarefa"
    )
    deadline = Column(Date, nullable=True)
    big_rock_id = Column(Integer, ForeignKey("big_rocks.id"), nullable=True)
    status = Column(
        String(20),
        CheckConstraint("status IN ('Pendente', 'Em Progresso', 'Concluída', 'Cancelada')"),
        default="Pendente"
    )

    # Priorização (V2)
    prioridade_calculada = Column(Integer, default=5)  # 1 (mais urgente) a 10 (menos urgente)
    pontuacao_prioridade = Column(Float, default=0.0)  # Score calculado por algoritmo

    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    concluido_em = Column(DateTime, nullable=True)

    # Relationships
    big_rock = relationship("BigRock", back_populates="tarefas")

    def __repr__(self):
        return f"<Tarefa(id={self.id}, descricao='{self.descricao[:30]}...', status='{self.status}')>"

    def marcar_concluida(self):
        """Marca a tarefa como concluída."""
        self.status = "Concluída"
        self.concluido_em = datetime.utcnow()
        self.atualizado_em = datetime.utcnow()

    def reabrir(self):
        """Reabre uma tarefa concluída."""
        self.status = "Pendente"
        self.concluido_em = None
        self.atualizado_em = datetime.utcnow()


# Índices para performance (criados via Alembic migrations)
# CREATE INDEX idx_tarefas_status ON tarefas(status);
# CREATE INDEX idx_tarefas_deadline ON tarefas(deadline);
# CREATE INDEX idx_tarefas_big_rock ON tarefas(big_rock_id);


# ==================== V2 Models ====================


class CicloMenstrual(Base):
    """
    Ciclo Menstrual - Tracking de bem-estar e padrões.

    Registra informações sobre o ciclo menstrual para adaptar
    recomendações e planejamento baseado na fase atual.
    """
    __tablename__ = "ciclo_menstrual"

    id = Column(Integer, primary_key=True, index=True)
    data_inicio = Column(Date, nullable=False)
    fase = Column(
        String(20),
        CheckConstraint("fase IN ('menstrual', 'folicular', 'ovulacao', 'lutea')"),
        nullable=False
    )
    # Sintomas como lista separada por vírgula
    sintomas = Column(Text, nullable=True)  # 'fadiga,criatividade_alta,dor'

    # Níveis de energia e humor (1-10)
    nivel_energia = Column(Integer, CheckConstraint("nivel_energia BETWEEN 1 AND 10"), nullable=True)
    nivel_foco = Column(Integer, CheckConstraint("nivel_foco BETWEEN 1 AND 10"), nullable=True)
    nivel_criatividade = Column(Integer, CheckConstraint("nivel_criatividade BETWEEN 1 AND 10"), nullable=True)

    notas = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CicloMenstrual(data={self.data_inicio}, fase='{self.fase}')>"


class PadroesCiclo(Base):
    """
    Padrões do Ciclo - Aprendizado sobre produtividade por fase.

    Armazena padrões identificados pela IA sobre como cada fase
    do ciclo afeta a produtividade e bem-estar.
    """
    __tablename__ = "padroes_ciclo"

    id = Column(Integer, primary_key=True, index=True)
    fase = Column(String(20), nullable=False)
    padrao_identificado = Column(Text, nullable=False)

    # Métricas médias dessa fase
    produtividade_media = Column(Float, default=1.0)  # Multiplicador (1.0 = normal)
    foco_medio = Column(Float, default=1.0)
    energia_media = Column(Float, default=1.0)

    confianca_score = Column(Float, default=0.0)  # 0.0 a 1.0
    sugestoes = Column(Text, nullable=True)  # Sugestões separadas por ;
    amostras_usadas = Column(Integer, default=0)

    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PadroesCiclo(fase='{self.fase}', confianca={self.confianca_score})>"


class CargaTrabalho(Base):
    """
    Carga de Trabalho - Análise de capacidade vs. demanda.

    Calcula e monitora a carga de trabalho por Big Rock para
    identificar sobrecargas e ajudar em decisões de trade-off.
    """
    __tablename__ = "carga_trabalho"

    id = Column(Integer, primary_key=True, index=True)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)

    big_rock_id = Column(Integer, ForeignKey("big_rocks.id"), nullable=True)

    # Estimativas de carga
    horas_estimadas = Column(Float, default=0.0)
    horas_disponiveis = Column(Float, default=0.0)
    percentual_carga = Column(Float, default=0.0)  # (estimadas/disponiveis) * 100

    # Alertas
    em_risco = Column(Boolean, default=False)
    motivo_risco = Column(Text, nullable=True)

    calculado_em = Column(DateTime, default=datetime.utcnow)

    # Relationships
    big_rock = relationship("BigRock")

    def __repr__(self):
        return f"<CargaTrabalho(big_rock_id={self.big_rock_id}, carga={self.percentual_carga}%)>"


class RegistroDiario(Base):
    """
    Registro Diário - Tracking de hábitos e energia.

    Registro diário para aprender padrões de sono, energia e produtividade.
    """
    __tablename__ = "registro_diario"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, unique=True, nullable=False)

    # Sono
    hora_acordar = Column(String(5), nullable=True)  # HH:MM
    hora_dormir = Column(String(5), nullable=True)   # HH:MM
    horas_sono = Column(Float, nullable=True)
    qualidade_sono = Column(Integer, CheckConstraint("qualidade_sono BETWEEN 1 AND 10"), nullable=True)

    # Energia ao longo do dia
    energia_manha = Column(Integer, CheckConstraint("energia_manha BETWEEN 1 AND 10"), nullable=True)
    energia_tarde = Column(Integer, CheckConstraint("energia_tarde BETWEEN 1 AND 10"), nullable=True)
    energia_noite = Column(Integer, CheckConstraint("energia_noite BETWEEN 1 AND 10"), nullable=True)

    # Produtividade
    horas_deep_work = Column(Float, default=0.0)
    tarefas_completadas = Column(Integer, default=0)

    # Contexto
    fase_ciclo = Column(String(20), nullable=True)
    eventos_especiais = Column(Text, nullable=True)  # Separados por vírgula
    notas_livre = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RegistroDiario(data={self.data})>"


# Índices adicionais para V2
# CREATE INDEX idx_ciclo_data ON ciclo_menstrual(data_inicio);
# CREATE INDEX idx_carga_periodo ON carga_trabalho(periodo_inicio, periodo_fim);
# CREATE INDEX idx_registro_data ON registro_diario(data);
