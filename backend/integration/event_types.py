"""Event types for the Event Bus system."""

from enum import Enum


class EventType(Enum):
    """All event types supported by the Event Bus."""

    # ==================== Task Manager Events ====================
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    TASK_DEADLINE_APPROACHING = "task_deadline_approaching"
    TASK_OVERDUE = "task_overdue"

    # ==================== Big Rocks Events ====================
    BIG_ROCK_CREATED = "big_rock_created"
    BIG_ROCK_UPDATED = "big_rock_updated"
    BIG_ROCK_CAPACITY_CHANGED = "big_rock_capacity_changed"

    # ==================== Wellness Coach Events ====================
    CYCLE_PHASE_CHANGED = "cycle_phase_changed"
    CYCLE_LOGGED = "cycle_logged"
    ENERGY_LOW = "energy_low"
    ENERGY_HIGH = "energy_high"
    WELLNESS_ALERT = "wellness_alert"

    # ==================== Capacity Guardian Events ====================
    CAPACITY_WARNING = "capacity_warning"
    CAPACITY_CRITICAL = "capacity_critical"
    OVERLOAD_DETECTED = "overload_detected"
    CAPACITY_NORMALIZED = "capacity_normalized"

    # ==================== Focus Module Events (Future) ====================
    FOCUS_SESSION_STARTED = "focus_session_started"
    FOCUS_SESSION_ENDED = "focus_session_ended"
    NOTIFICATION_URGENT = "notification_urgent"
    INTERRUPTION_BLOCKED = "interruption_blocked"

    # ==================== Projects Module Events (Future) ====================
    PROJECT_COLLECTED = "project_collected"
    PROJECT_ANALYZED = "project_analyzed"
    PROJECT_ACCEPTED = "project_accepted"
    PROJECT_REJECTED = "project_rejected"
    PROJECT_COMPLETED = "project_completed"
    PROJECT_DEADLINE_APPROACHING = "project_deadline_approaching"

    # ==================== OKR Dashboard Events (Future) ====================
    OKR_CREATED = "okr_created"
    OKR_UPDATED = "okr_updated"
    OKR_AT_RISK = "okr_at_risk"
    OKR_COMPLETED = "okr_completed"
    MILESTONE_ACHIEVED = "milestone_achieved"

    # ==================== User/Authentication Events ====================
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    USER_REGISTERED = "user_registered"

    # ==================== Calendar Integration Events ====================
    CALENDAR_CONNECTED = "calendar_connected"
    CALENDAR_DISCONNECTED = "calendar_disconnected"
    CALENDAR_SYNCED = "calendar_synced"
    CALENDAR_SYNC_FAILED = "calendar_sync_failed"
    CALENDAR_EVENT_CREATED = "calendar_event_created"
    CALENDAR_EVENT_UPDATED = "calendar_event_updated"
    CALENDAR_EVENT_DELETED = "calendar_event_deleted"
    CALENDAR_CONFLICT_DETECTED = "calendar_conflict_detected"
    CALENDAR_CONFLICT_RESOLVED = "calendar_conflict_resolved"

    # ==================== System Events ====================
    CONTEXT_UPDATED = "context_updated"
    DECISION_REQUIRED = "decision_required"
    DECISION_EXECUTED = "decision_executed"
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"


class ModuleName(Enum):
    """Module names for event tracking."""

    TASK_MANAGER = "task_manager"
    BIG_ROCKS = "big_rocks"
    WELLNESS_COACH = "wellness_coach"
    CAPACITY_GUARDIAN = "capacity_guardian"
    FOCUS_MODULE = "focus_module"
    PROJECTS = "projects"
    OKR_DASHBOARD = "okr_dashboard"
    CALENDAR = "calendar"
    NOTIFICATIONS = "notifications"
    ANALYTICS = "analytics"
    CONTEXT_MANAGER = "context_manager"
    EVENT_BUS = "event_bus"
    AUTH = "auth"
    SYSTEM = "system"
