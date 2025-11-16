"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


# ==================== Freelance System Schemas ====================


class FreelanceProjectBase(BaseModel):
    """Base schema for FreelanceProject."""

    client_name: str = Field(..., min_length=1, max_length=200)
    project_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    hourly_rate: float = Field(..., gt=0)
    estimated_hours: float = Field(..., gt=0)
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

    @field_validator("client_name", "project_name")
    @classmethod
    def sanitize_names(cls, v: str) -> str:
        """Sanitize names to prevent XSS."""
        if not v:
            raise ValueError("Field cannot be empty")
        sanitized = sanitize_string(v, max_length=200, allow_newlines=False)
        if not sanitized.strip():
            raise ValueError("Field cannot be empty after sanitization")
        return sanitized

    @field_validator("description", "notes")
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields to prevent XSS."""
        if v is None:
            return v
        sanitized = sanitize_string(v, max_length=5000, allow_newlines=True)
        return sanitized if sanitized.strip() else None


class FreelanceProjectCreate(FreelanceProjectBase):
    """Schema for creating a FreelanceProject."""

    pass


class FreelanceProjectUpdate(BaseModel):
    """Schema for updating a FreelanceProject."""

    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, gt=0)
    estimated_hours: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Optional[Literal["proposal", "active", "completed", "cancelled"]] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class FreelanceProjectResponse(FreelanceProjectBase):
    """Schema for FreelanceProject response."""

    id: int
    status: str
    actual_hours: float
    completed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkLogBase(BaseModel):
    """Base schema for WorkLog."""

    project_id: int = Field(..., gt=0)
    hours: float = Field(..., gt=0)
    description: str = Field(..., min_length=1)
    work_date: Optional[date] = None
    task_type: Optional[str] = Field(None, max_length=50)
    billable: bool = True

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


class WorkLogCreate(WorkLogBase):
    """Schema for creating a WorkLog."""

    pass


class WorkLogUpdate(BaseModel):
    """Schema for updating a WorkLog."""

    hours: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1)
    work_date: Optional[date] = None
    task_type: Optional[str] = Field(None, max_length=50)
    billable: Optional[bool] = None


class WorkLogResponse(WorkLogBase):
    """Schema for WorkLog response."""

    id: int
    user_id: int
    invoiced: bool
    invoice_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    """Base schema for Invoice."""

    project_id: int = Field(..., gt=0)
    invoice_number: str = Field(..., min_length=1, max_length=50)
    issue_date: date
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("invoice_number")
    @classmethod
    def sanitize_invoice_number(cls, v: str) -> str:
        """Sanitize invoice number."""
        sanitized = sanitize_string(v, max_length=50, allow_newlines=False)
        if not sanitized.strip():
            raise ValueError("Invoice number cannot be empty")
        return sanitized


class InvoiceCreate(BaseModel):
    """Schema for creating an Invoice."""

    project_id: int = Field(..., gt=0)
    invoice_number: Optional[str] = None  # Auto-generated if not provided
    payment_terms: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    include_unbilled_only: bool = True


class InvoiceUpdate(BaseModel):
    """Schema for updating an Invoice."""

    status: Optional[Literal["draft", "sent", "paid", "overdue", "cancelled"]] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for Invoice response."""

    id: int
    user_id: int
    total_amount: float
    total_hours: float
    hourly_rate: float
    status: str
    paid_date: Optional[date] = None
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Freelance List Responses ====================


class FreelanceProjectListResponse(BaseModel):
    """Schema for list of freelance projects."""

    total: int
    projects: list[FreelanceProjectResponse]


class WorkLogListResponse(BaseModel):
    """Schema for list of work logs."""

    total: int
    work_logs: list[WorkLogResponse]


class InvoiceListResponse(BaseModel):
    """Schema for list of invoices."""

    total: int
    invoices: list[InvoiceResponse]
