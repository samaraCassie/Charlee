"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationError
from api.security import sanitize_string, validate_color_hex


# ==================== Big Rock Schemas ====================


class BigRockBase(BaseModel):
    """Base schema for BigRock."""

    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    active: bool = True

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name to prevent XSS."""
        if not v:
            raise ValueError("Name cannot be empty")
        sanitized = sanitize_string(v, max_length=100, allow_newlines=False)
        if not sanitized.strip():
            raise ValueError("Name cannot be empty after sanitization")
        return sanitized

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is a valid hex code."""
        if v is None:
            return v
        if not validate_color_hex(v):
            raise ValueError(f"Invalid hex color format: {v}. Expected format: #RRGGBB")
        return v


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

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        """Sanitize description to prevent XSS."""
        if not v:
            raise ValueError("Description cannot be empty")
        sanitized = sanitize_string(v, max_length=5000, allow_newlines=True)
        if not sanitized.strip():
            raise ValueError("Description cannot be empty after sanitization")
        return sanitized

    @field_validator("big_rock_id")
    @classmethod
    def validate_big_rock_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate big_rock_id is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("big_rock_id must be a positive integer")
        return v


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
