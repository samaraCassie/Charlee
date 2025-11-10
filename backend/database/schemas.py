"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# ==================== Big Rock Schemas ====================


class BigRockBase(BaseModel):
    """Base schema for BigRock."""

    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    active: bool = True


class BigRockCreate(BigRockBase):
    """Schema for creating a BigRock."""

    pass


class BigRockUpdate(BaseModel):
    """Schema for updating a BigRock."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None


class BigRockResponse(BigRockBase):
    """Schema for BigRock response."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Task Schemas ====================


class TaskBase(BaseModel):
    """Base schema for Task."""

    description: str = Field(..., min_length=1)
    type: Literal["fixed_appointment", "task", "continuous"] = "task"
    deadline: Optional[date] = None
    big_rock_id: Optional[int] = None


class TaskCreate(TaskBase):
    """Schema for creating a Task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a Task."""

    description: Optional[str] = Field(None, min_length=1)
    type: Optional[Literal["fixed_appointment", "task", "continuous"]] = None
    deadline: Optional[date] = None
    big_rock_id: Optional[int] = None
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled"]] = None


class TaskResponse(TaskBase):
    """Schema for Task response."""

    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    big_rock: Optional[BigRockResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== List Responses ====================


class TaskListResponse(BaseModel):
    """Schema for list of tasks."""

    total: int
    tasks: list[TaskResponse]


class BigRockListResponse(BaseModel):
    """Schema for list of big rocks."""

    total: int
    big_rocks: list[BigRockResponse]
