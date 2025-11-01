"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# ==================== Big Rock Schemas ====================

class BigRockBase(BaseModel):
    """Base schema for BigRock."""
    nome: str = Field(..., min_length=1, max_length=100)
    cor: Optional[str] = Field(None, max_length=20)
    ativo: bool = True


class BigRockCreate(BigRockBase):
    """Schema for creating a BigRock."""
    pass


class BigRockUpdate(BaseModel):
    """Schema for updating a BigRock."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cor: Optional[str] = Field(None, max_length=20)
    ativo: Optional[bool] = None


class BigRockResponse(BigRockBase):
    """Schema for BigRock response."""
    id: int
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Tarefa Schemas ====================

class TarefaBase(BaseModel):
    """Base schema for Tarefa."""
    descricao: str = Field(..., min_length=1)
    tipo: Literal["Compromisso Fixo", "Tarefa", "Contínuo"] = "Tarefa"
    deadline: Optional[date] = None
    big_rock_id: Optional[int] = None


class TarefaCreate(TarefaBase):
    """Schema for creating a Tarefa."""
    pass


class TarefaUpdate(BaseModel):
    """Schema for updating a Tarefa."""
    descricao: Optional[str] = Field(None, min_length=1)
    tipo: Optional[Literal["Compromisso Fixo", "Tarefa", "Contínuo"]] = None
    deadline: Optional[date] = None
    big_rock_id: Optional[int] = None
    status: Optional[Literal["Pendente", "Em Progresso", "Concluída", "Cancelada"]] = None


class TarefaResponse(TarefaBase):
    """Schema for Tarefa response."""
    id: int
    status: str
    criado_em: datetime
    atualizado_em: datetime
    concluido_em: Optional[datetime] = None
    big_rock: Optional[BigRockResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== List Responses ====================

class TarefaListResponse(BaseModel):
    """Schema for list of tasks."""
    total: int
    tarefas: list[TarefaResponse]


class BigRockListResponse(BaseModel):
    """Schema for list of big rocks."""
    total: int
    big_rocks: list[BigRockResponse]
