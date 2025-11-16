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


# ==================== Projects Intelligence System Schemas ====================


# ----- FreelancePlatform Schemas -----


class FreelancePlatformBase(BaseModel):
    """Base schema for FreelancePlatform."""

    name: str = Field(..., min_length=1, max_length=100)
    platform_type: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=255)
    api_config: Optional[dict] = None
    auto_collect: bool = True
    active: bool = True
    collection_interval_minutes: Optional[int] = Field(None, ge=1)

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


class FreelancePlatformCreate(FreelancePlatformBase):
    """Schema for creating a FreelancePlatform."""

    pass


class FreelancePlatformUpdate(BaseModel):
    """Schema for updating a FreelancePlatform."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    platform_type: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=255)
    api_config: Optional[dict] = None
    auto_collect: Optional[bool] = None
    active: Optional[bool] = None
    collection_interval_minutes: Optional[int] = Field(None, ge=1)


class FreelancePlatformResponse(FreelancePlatformBase):
    """Schema for FreelancePlatform response."""

    id: int
    last_collection_at: Optional[datetime] = None
    last_collection_count: int
    total_projects_collected: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----- FreelanceOpportunity Schemas -----


class FreelanceOpportunityBase(BaseModel):
    """Base schema for FreelanceOpportunity."""

    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    platform_id: Optional[int] = Field(None, gt=0)
    external_id: Optional[str] = Field(None, max_length=100)
    client_name: Optional[str] = Field(None, max_length=200)
    client_rating: Optional[float] = Field(None, ge=0, le=5)
    client_country: Optional[str] = Field(None, max_length=100)
    client_projects_count: Optional[int] = Field(None, ge=0)
    required_skills: Optional[list[str]] = None
    client_budget: Optional[float] = Field(None, gt=0)
    client_currency: str = Field(default="USD", max_length=3)
    client_deadline_days: Optional[int] = Field(None, gt=0)
    contract_type: Optional[str] = Field(None, max_length=50)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Sanitize title to prevent XSS."""
        if not v:
            raise ValueError("Title cannot be empty")
        sanitized = sanitize_string(v, max_length=300, allow_newlines=False)
        if not sanitized.strip():
            raise ValueError("Title cannot be empty after sanitization")
        return sanitized

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        """Sanitize description to prevent XSS."""
        if not v:
            raise ValueError("Description cannot be empty")
        sanitized = sanitize_string(v, max_length=10000, allow_newlines=True)
        if not sanitized.strip():
            raise ValueError("Description cannot be empty after sanitization")
        return sanitized


class FreelanceOpportunityCreate(FreelanceOpportunityBase):
    """Schema for creating a FreelanceOpportunity."""

    pass


class FreelanceOpportunityUpdate(BaseModel):
    """Schema for updating a FreelanceOpportunity."""

    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    client_name: Optional[str] = Field(None, max_length=200)
    client_rating: Optional[float] = Field(None, ge=0, le=5)
    client_country: Optional[str] = Field(None, max_length=100)
    client_projects_count: Optional[int] = Field(None, ge=0)
    required_skills: Optional[list[str]] = None
    client_budget: Optional[float] = Field(None, gt=0)
    client_currency: Optional[str] = Field(None, max_length=3)
    client_deadline_days: Optional[int] = Field(None, gt=0)
    contract_type: Optional[str] = Field(None, max_length=50)
    status: Optional[Literal["new", "analyzed", "evaluated", "accepted", "rejected"]] = None
    recommendation: Optional[Literal["accept", "negotiate", "reject", "pending"]] = None


class FreelanceOpportunityResponse(FreelanceOpportunityBase):
    """Schema for FreelanceOpportunity response."""

    id: int
    status: str
    estimated_complexity: Optional[int] = None
    skill_level: Optional[str] = None
    category: Optional[str] = None
    estimated_hours: Optional[float] = None
    suggested_price: Optional[float] = None
    viability_score: Optional[float] = None
    alignment_score: Optional[float] = None
    strategic_score: Optional[float] = None
    final_score: Optional[float] = None
    client_intent: Optional[str] = None
    red_flags: Optional[list[str]] = None
    opportunities: Optional[list[str]] = None
    recommendation: str
    analyzed_at: Optional[datetime] = None
    evaluated_at: Optional[datetime] = None
    collected_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----- PricingParameter Schemas -----


class PricingParameterBase(BaseModel):
    """Base schema for PricingParameter."""

    base_hourly_rate: float = Field(..., gt=0)
    minimum_margin: float = Field(default=0.20, ge=0, le=1)
    minimum_project_value: float = Field(default=100.0, gt=0)
    complexity_factors: Optional[dict] = None
    specialization_factors: Optional[dict] = None
    deadline_factors: Optional[dict] = None
    client_factors: Optional[dict] = None
    active: bool = True

    @field_validator(
        "complexity_factors",
        "specialization_factors",
        "deadline_factors",
        "client_factors",
    )
    @classmethod
    def validate_factors(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate factor dictionaries contain positive multipliers."""
        if v is None:
            return v
        for key, value in v.items():
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"Factor '{key}' must be a positive number, got {value}")
        return v


class PricingParameterCreate(PricingParameterBase):
    """Schema for creating a PricingParameter."""

    pass


class PricingParameterUpdate(BaseModel):
    """Schema for updating a PricingParameter."""

    base_hourly_rate: Optional[float] = Field(None, gt=0)
    minimum_margin: Optional[float] = Field(None, ge=0, le=1)
    minimum_project_value: Optional[float] = Field(None, gt=0)
    complexity_factors: Optional[dict] = None
    specialization_factors: Optional[dict] = None
    deadline_factors: Optional[dict] = None
    client_factors: Optional[dict] = None
    active: Optional[bool] = None


class PricingParameterResponse(PricingParameterBase):
    """Schema for PricingParameter response."""

    id: int
    version: int
    auto_adjusted: bool
    based_on_executions_count: int
    adjustment_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----- ProjectExecution Schemas -----


class ProjectExecutionBase(BaseModel):
    """Base schema for ProjectExecution."""

    opportunity_id: Optional[int] = Field(None, gt=0)
    freelance_project_id: Optional[int] = Field(None, gt=0)

    # Planning
    start_date: date
    planned_end_date: Optional[date] = None

    # Time investment
    planned_hours: Optional[float] = Field(None, ge=0)

    # Financial
    negotiated_value: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=10)

    # Client evaluation
    client_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    client_feedback: Optional[str] = None

    # Personal notes
    personal_notes: Optional[str] = None

    @field_validator("client_feedback", "personal_notes")
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields to prevent XSS."""
        if v is None:
            return v
        sanitized = sanitize_string(v, max_length=5000, allow_newlines=True)
        return sanitized if sanitized.strip() else None


class ProjectExecutionCreate(ProjectExecutionBase):
    """Schema for creating a ProjectExecution."""

    pass


class ProjectExecutionUpdate(BaseModel):
    """Schema for updating a ProjectExecution."""

    planned_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    planned_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    received_value: Optional[float] = Field(None, ge=0)
    payment_date: Optional[date] = None
    client_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    client_feedback: Optional[str] = None
    personal_notes: Optional[str] = None
    status: Optional[Literal["planned", "in_progress", "completed", "cancelled", "on_hold"]] = None


class ProjectExecutionResponse(ProjectExecutionBase):
    """Schema for ProjectExecution response."""

    id: int
    user_id: int
    status: str
    actual_end_date: Optional[date] = None
    actual_hours: float
    received_value: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----- Negotiation Schemas -----


class NegotiationBase(BaseModel):
    """Base schema for Negotiation."""

    opportunity_id: int = Field(..., gt=0)

    # Original proposal
    original_budget: Optional[float] = Field(None, gt=0)
    original_deadline_days: Optional[int] = Field(None, gt=0)

    # Counter-proposal
    counter_proposal_budget: float = Field(..., gt=0)
    counter_proposal_deadline_days: Optional[int] = Field(None, gt=0)
    counter_proposal_justification: str = Field(..., min_length=1)

    # Client response
    final_agreed_budget: Optional[float] = Field(None, gt=0)
    final_agreed_deadline_days: Optional[int] = Field(None, gt=0)

    @field_validator("counter_proposal_justification")
    @classmethod
    def sanitize_text_fields(cls, v: str) -> str:
        """Sanitize text fields to prevent XSS."""
        sanitized = sanitize_string(v, max_length=5000, allow_newlines=True)
        if not sanitized.strip():
            raise ValueError("Justification cannot be empty")
        return sanitized


class NegotiationCreate(NegotiationBase):
    """Schema for creating a Negotiation."""

    pass


class NegotiationUpdate(BaseModel):
    """Schema for updating a Negotiation."""

    counter_proposal_budget: Optional[float] = Field(None, gt=0)
    counter_proposal_deadline_days: Optional[int] = Field(None, gt=0)
    counter_proposal_justification: Optional[str] = None
    client_response: Optional[str] = None
    final_agreed_budget: Optional[float] = Field(None, gt=0)
    final_agreed_deadline_days: Optional[int] = Field(None, gt=0)
    outcome: Optional[Literal["accepted", "rejected", "agreed", "no_response", "pending"]] = None
    outcome_notes: Optional[str] = None


class NegotiationResponse(NegotiationBase):
    """Schema for Negotiation response."""

    id: int
    user_id: int
    outcome: str
    client_response: Optional[str] = None
    generated_message: Optional[str] = None
    outcome_notes: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== Projects Intelligence List Responses ====================


class FreelancePlatformListResponse(BaseModel):
    """Schema for list of freelance platforms."""

    total: int
    platforms: list[FreelancePlatformResponse]


class FreelanceOpportunityListResponse(BaseModel):
    """Schema for list of freelance opportunities."""

    total: int
    opportunities: list[FreelanceOpportunityResponse]


class PricingParameterListResponse(BaseModel):
    """Schema for list of pricing parameters."""

    total: int
    pricing_parameters: list[PricingParameterResponse]


class ProjectExecutionListResponse(BaseModel):
    """Schema for list of project executions."""

    total: int
    executions: list[ProjectExecutionResponse]


class NegotiationListResponse(BaseModel):
    """Schema for list of negotiations."""

    total: int
    negotiations: list[NegotiationResponse]
