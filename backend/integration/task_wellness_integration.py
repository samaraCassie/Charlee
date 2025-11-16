"""Integration between Task Manager and Wellness Coach."""

import logging
from typing import Dict, Any

from sqlalchemy.orm import Session

from database.models import Task
from integration.event_bus import Event, EventBus
from integration.event_types import EventType
from integration.context_manager import ContextManager

logger = logging.getLogger(__name__)


class TaskWellnessIntegration:
    """
    Integration between Task Manager and Wellness Coach.

    Adjusts task priorities and recommendations based on wellness state.
    """

    def __init__(self, db_session: Session, event_bus: EventBus, context_manager: ContextManager):
        """
        Initialize integration.

        Args:
            db_session: Database session
            event_bus: Event bus for subscriptions
            context_manager: Context manager for state
        """
        self.db = db_session
        self.event_bus = event_bus
        self.context = context_manager

        # Subscribe to relevant events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED, self.on_cycle_phase_changed)
        self.event_bus.subscribe(EventType.ENERGY_LOW, self.on_energy_low)
        self.event_bus.subscribe(EventType.TASK_CREATED, self.on_task_created)

        logger.info("📡 Task-Wellness integration subscribed to events")

    def on_cycle_phase_changed(self, event: Event) -> None:
        """
        Adjust task priorities when cycle phase changes.

        Args:
            event: Cycle phase change event
        """
        new_phase = event.payload.get("nova_fase")
        energia_esperada = event.payload.get("energia_esperada", 0.7)

        logger.info(f"🌸 Adjusting tasks for {new_phase} phase (energia: {energia_esperada:.0%})")

        # Get pending tasks
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.context.user_id,
                Task.status.in_(["pending", "in_progress"]),
            )
            .all()
        )

        for task in tasks:
            # Adjust based on phase
            adjustment = self._calculate_priority_adjustment(task, new_phase, energia_esperada)

            if adjustment != 0:
                logger.debug(
                    f"Task '{task.description[:30]}': priority adjusted by {adjustment:+d}"
                )

    def on_energy_low(self, event: Event) -> None:
        """
        Suggest easier tasks when energy is low.

        Args:
            event: Low energy event
        """
        logger.info("⚡ Energy low - recommending lighter tasks")

        # Could publish recommendations for light tasks
        # This is a placeholder for future enhancement

    def on_task_created(self, event: Event) -> None:
        """
        Evaluate new task against current wellness state.

        Args:
            event: Task creation event
        """
        task_id = event.payload.get("task_id")

        if not task_id:
            return

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        context = self.context.get_context()

        # Check if task is appropriate for current state
        if context["fase_ciclo"] == "menstrual" and context["energia_atual"] < 5:
            # Suggest postponing heavy tasks
            if self._is_heavy_task(task):
                logger.warning(
                    f"⚠️ Heavy task '{task.description[:30]}' created during low-energy menstrual phase"
                )

    def _calculate_priority_adjustment(self, task: Task, phase: str, energia: float) -> int:
        """
        Calculate priority adjustment based on phase and energy.

        Args:
            task: Task to adjust
            phase: Current cycle phase
            energia: Expected energy level

        Returns:
            Priority adjustment (-2 to +2)
        """
        # During menstrual phase with low energy, deprioritize non-urgent tasks
        if phase == "menstrual" and energia < 0.6:
            if task.type != "fixed_appointment":
                return -1

        # During ovulation, boost communication tasks
        if phase == "ovulacao":
            if "reunião" in task.description.lower() or "apresenta" in task.description.lower():
                return +1

        # During luteal, boost completion tasks
        if phase == "lutea":
            if task.status == "in_progress":
                return +1

        return 0

    def _is_heavy_task(self, task: Task) -> bool:
        """
        Check if task is considered heavy.

        Args:
            task: Task to check

        Returns:
            True if task is heavy
        """
        # Check for keywords indicating heavy tasks
        heavy_keywords = [
            "desenvolvimento",
            "implementar",
            "criar",
            "desenvolver",
            "migrar",
        ]
        description_lower = task.description.lower()

        return any(keyword in description_lower for keyword in heavy_keywords)

    def get_wellness_adjusted_tasks(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get task recommendations adjusted for wellness.

        Args:
            limit: Maximum number of tasks

        Returns:
            Dictionary with recommended tasks
        """
        context = self.context.get_context()

        # Get pending tasks
        tasks = (
            self.db.query(Task)
            .filter(Task.user_id == self.context.user_id, Task.status == "pending")
            .order_by(Task.deadline.asc().nullslast())
            .limit(limit * 2)  # Get more to filter
            .all()
        )

        # Filter based on wellness
        recommended = []
        deferred = []

        for task in tasks:
            if self._should_recommend_task(task, context):
                recommended.append(task)
            else:
                deferred.append(task)

            if len(recommended) >= limit:
                break

        return {
            "recommended": recommended[:limit],
            "deferred": deferred,
            "reason": self._get_recommendation_reason(context),
        }

    def _should_recommend_task(self, task: Task, context: Dict[str, Any]) -> bool:
        """
        Check if task should be recommended given context.

        Args:
            task: Task to check
            context: Current context

        Returns:
            True if task should be recommended
        """
        # Always recommend fixed appointments
        if task.type == "fixed_appointment":
            return True

        # During menstrual phase with low energy, only light tasks
        if context["fase_ciclo"] == "menstrual" and context["energia_atual"] < 5:
            return not self._is_heavy_task(task)

        # High stress? Only urgent tasks
        if context["nivel_stress"] >= 8:
            # Check deadline (simplified - assuming deadline within 2 days is urgent)
            if task.deadline:
                from datetime import datetime, timedelta

                if task.deadline <= datetime.now() + timedelta(days=2):
                    return True
                return False
            return False

        return True

    def _get_recommendation_reason(self, context: Dict[str, Any]) -> str:
        """
        Get reason for current recommendations.

        Args:
            context: Current context

        Returns:
            Explanation string
        """
        reasons = []

        if context["fase_ciclo"] == "menstrual" and context["energia_atual"] < 5:
            reasons.append(f"Fase menstrual com energia baixa ({context['energia_atual']}/10)")

        if context["nivel_stress"] >= 8:
            reasons.append(f"Nível de stress alto ({context['nivel_stress']}/10)")

        if context["em_sessao_foco"]:
            reasons.append("Em sessão de foco")

        if not reasons:
            return "Condições normais - todas as tarefas podem ser realizadas"

        return "Recomendações ajustadas por: " + ", ".join(reasons)
