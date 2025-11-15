"""Integration for Capacity Guardian with other modules."""

import logging
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from database.models import Task
from integration.event_bus import Event, EventBus
from integration.event_types import EventType
from integration.context_manager import ContextManager

logger = logging.getLogger(__name__)


class CapacityIntegration:
    """
    Integration for Capacity Guardian.

    Manages workload protection across all modules.
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
        self.event_bus.subscribe(EventType.CAPACITY_CRITICAL, self.on_capacity_critical)
        self.event_bus.subscribe(EventType.CAPACITY_WARNING, self.on_capacity_warning)
        self.event_bus.subscribe(EventType.TASK_CREATED, self.on_task_created)

        logger.info("📡 Capacity integration subscribed to events")

    def on_capacity_critical(self, event: Event) -> None:
        """
        Handle critical capacity - activate maximum protection.

        Args:
            event: Capacity critical event
        """
        carga = event.payload.get("percentual_carga", 95)

        logger.error(f"🚨 CRITICAL CAPACITY: {carga}% - Activating protection")

        # Block new non-critical tasks
        # This is a policy that could be implemented

        # Suggest task cancellations/postponements
        suggestions = self._suggest_task_postponements()

        if suggestions:
            logger.warning(f"💡 Suggested {len(suggestions)} tasks for postponement")

    def on_capacity_warning(self, event: Event) -> None:
        """
        Handle capacity warning.

        Args:
            event: Capacity warning event
        """
        carga = event.payload.get("percentual_carga", 80)

        logger.warning(f"⚠️ Capacity warning: {carga}%")

        # Could implement gentle warnings or suggestions here

    def on_task_created(self, event: Event) -> None:
        """
        Evaluate new task against current capacity.

        Args:
            event: Task creation event
        """
        context = self.context.get_context()

        # If capacity is high, warn about new task
        if context["carga_trabalho_percentual"] > 80:
            task_id = event.payload.get("task_id")
            logger.warning(
                f"⚠️ New task created (ID: {task_id}) while capacity is {context['carga_trabalho_percentual']:.0f}%"
            )

    def _suggest_task_postponements(self) -> List[Task]:
        """
        Suggest tasks that could be postponed.

        Returns:
            List of tasks that could be postponed
        """
        from datetime import datetime, timedelta

        # Get non-urgent tasks
        later_date = datetime.now() + timedelta(days=3)

        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.context.user_id,
                Task.status == "pending",
                Task.type != "fixed_appointment",
                Task.deadline > later_date,
            )
            .order_by(Task.deadline.desc())
            .limit(10)
            .all()
        )

        return tasks

    def check_capacity_before_accept(self, estimated_hours: float) -> Dict[str, Any]:
        """
        Check if new work can be accepted given current capacity.

        Args:
            estimated_hours: Hours estimated for new work

        Returns:
            Dictionary with acceptance recommendation
        """
        context = self.context.get_context()
        current_load = context["carga_trabalho_percentual"]

        # Calculate rough impact (simplified)
        # Assuming 40 hours/week capacity
        impact = (estimated_hours / 40) * 100

        new_load = current_load + impact

        # Decision logic
        if new_load > 100:
            recommendation = "reject"
            reason = f"Capacity would exceed 100% (current: {current_load:.0f}%, +{impact:.0f}% = {new_load:.0f}%)"
        elif new_load > 90:
            recommendation = "negotiate"
            reason = f"Capacity would be critical (current: {current_load:.0f}%, +{impact:.0f}% = {new_load:.0f}%)"
        elif new_load > 75:
            recommendation = "accept_with_caution"
            reason = f"Capacity would be high (current: {current_load:.0f}%, +{impact:.0f}% = {new_load:.0f}%)"
        else:
            recommendation = "accept"
            reason = f"Capacity within safe limits (current: {current_load:.0f}%, +{impact:.0f}% = {new_load:.0f}%)"

        return {
            "recommendation": recommendation,
            "reason": reason,
            "current_load": current_load,
            "estimated_impact": impact,
            "projected_load": new_load,
            "wellness_consideration": self._get_wellness_consideration(),
        }

    def _get_wellness_consideration(self) -> str:
        """
        Get wellness consideration for capacity decisions.

        Returns:
            Wellness consideration message
        """
        context = self.context.get_context()

        if context["fase_ciclo"] == "menstrual" and context["energia_atual"] < 5:
            return "⚠️ Fase menstrual com baixa energia - seja mais seletiva"

        if context["nivel_stress"] >= 8:
            return "⚠️ Nível de stress alto - evite sobrecarga adicional"

        if context["necessita_pausa"]:
            return "⚠️ Pausa recomendada - não aceite trabalho adicional agora"

        return "✅ Condições de bem-estar normais"
