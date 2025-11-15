"""Context Manager - Maintains holistic view of user's current state."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import extract
from sqlalchemy.orm import Session

from database.models import GlobalContext, Task, User
from integration.event_bus import Event, EventBus
from integration.event_types import EventType, ModuleName

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Context Manager - Maintains and updates global user context.

    Tracks user's current state including wellness, capacity, focus,
    and uses this for context-aware decisions.
    """

    def __init__(self, db_session: Session, event_bus: EventBus, user_id: int):
        """
        Initialize Context Manager.

        Args:
            db_session: Database session
            event_bus: Event bus for subscribing to updates
            user_id: User ID to manage context for
        """
        self.db = db_session
        self.event_bus = event_bus
        self.user_id = user_id
        self.current_context: Optional[ContextoGlobal] = self.load_context()

        # Subscribe to events that affect context
        self._subscribe_to_events()

    def load_context(self) -> GlobalContext:
        """
        Load current context from database.

        Returns:
            Current GlobalContext object
        """
        context = (
            self.db.query(GlobalContext)
            .filter(GlobalContext.user_id == self.user_id)
            .order_by(GlobalContext.atualizado_em.desc())
            .first()
        )

        if not context:
            # Create initial context
            context = self.initialize_context()

        return context

    def initialize_context(self) -> GlobalContext:
        """
        Initialize context for the first time.

        Returns:
            Newly created GlobalContext object
        """
        now = datetime.utcnow()

        context = GlobalContext(
            user_id=self.user_id,
            fase_ciclo="folicular",  # Default phase
            energia_atual=7,
            carga_trabalho_percentual=50.0,
            em_sessao_foco=False,
            tarefas_pendentes=self._count_pending_tasks(),
            projetos_ativos=0,
            notificacoes_nao_lidas=0,
            hora_dia=now.hour,
            dia_semana=now.weekday(),
            periodo_produtivo=self._get_periodo_produtivo(now.hour),
            nivel_stress=5,
            necessita_pausa=False,
        )

        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)

        logger.info(f"✅ Initialized context for user {self.user_id}")

        return context

    def _subscribe_to_events(self) -> None:
        """Subscribe to events that affect context."""

        # Wellness events
        self.event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED, self.on_cycle_phase_changed)
        self.event_bus.subscribe(EventType.ENERGY_LOW, self.on_energy_low)
        self.event_bus.subscribe(EventType.ENERGY_HIGH, self.on_energy_high)

        # Capacity events
        self.event_bus.subscribe(EventType.CAPACITY_WARNING, self.on_capacity_warning)
        self.event_bus.subscribe(EventType.CAPACITY_CRITICAL, self.on_capacity_critical)
        self.event_bus.subscribe(EventType.CAPACITY_NORMALIZED, self.on_capacity_normalized)

        # Focus events
        self.event_bus.subscribe(EventType.FOCUS_SESSION_STARTED, self.on_focus_started)
        self.event_bus.subscribe(EventType.FOCUS_SESSION_ENDED, self.on_focus_ended)

        # Task events
        self.event_bus.subscribe(EventType.TASK_CREATED, self.on_task_created)
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self.on_task_completed)

        logger.info(f"📡 Context Manager subscribed to {len(self.event_bus.subscribers)} event types")

    # ==================== Event Handlers ====================

    def on_cycle_phase_changed(self, event: Event) -> None:
        """Handle cycle phase change."""
        new_phase = event.payload.get("nova_fase")
        energia_esperada = event.payload.get("energia_esperada", 7)

        self.update_context({
            "fase_ciclo": new_phase,
            "energia_atual": int(energia_esperada * 10),
        })

        logger.info(f"🌸 Context updated: cycle phase → {new_phase}")

    def on_energy_low(self, event: Event) -> None:
        """Handle low energy event."""
        self.update_context({
            "nivel_stress": min(self.current_context.nivel_stress + 2, 10),
            "necessita_pausa": True,
        })

        logger.warning("⚡ Energy low - stress increased, pause recommended")

    def on_energy_high(self, event: Event) -> None:
        """Handle high energy event."""
        self.update_context({
            "nivel_stress": max(self.current_context.nivel_stress - 1, 1),
            "necessita_pausa": False,
        })

        logger.info("⚡ Energy high - stress decreased")

    def on_capacity_warning(self, event: Event) -> None:
        """Handle capacity warning."""
        carga = event.payload.get("percentual_carga", 75)

        self.update_context({
            "carga_trabalho_percentual": carga,
            "nivel_stress": min(int(carga / 10), 10),
        })

        logger.warning(f"⚖️ Capacity warning: {carga}%")

    def on_capacity_critical(self, event: Event) -> None:
        """Handle critical capacity."""
        carga = event.payload.get("percentual_carga", 90)

        self.update_context({
            "carga_trabalho_percentual": carga,
            "nivel_stress": 10,
            "necessita_pausa": True,
        })

        logger.error(f"🚨 CRITICAL capacity: {carga}%")

    def on_capacity_normalized(self, event: Event) -> None:
        """Handle capacity normalization."""
        carga = event.payload.get("percentual_carga", 60)

        self.update_context({
            "carga_trabalho_percentual": carga,
            "nivel_stress": max(self.current_context.nivel_stress - 2, 1),
            "necessita_pausa": False,
        })

        logger.info(f"✅ Capacity normalized: {carga}%")

    def on_focus_started(self, event: Event) -> None:
        """Handle focus session start."""
        self.update_context({"em_sessao_foco": True})
        logger.info("🎯 Focus session started")

    def on_focus_ended(self, event: Event) -> None:
        """Handle focus session end."""
        qualidade = event.payload.get("qualidade_foco", 7)

        # Decrease energy slightly after focus session
        energia_nova = max(self.current_context.energia_atual - 1, 1)

        self.update_context({
            "em_sessao_foco": False,
            "energia_atual": energia_nova,
        })

        logger.info(f"🎯 Focus session ended (quality: {qualidade}/10)")

    def on_task_created(self, event: Event) -> None:
        """Handle task creation."""
        self.update_context({"tarefas_pendentes": self._count_pending_tasks()})

    def on_task_completed(self, event: Event) -> None:
        """Handle task completion."""
        self.update_context({"tarefas_pendentes": self._count_pending_tasks()})

    # ==================== Context Updates ====================

    def update_context(self, updates: Dict[str, Any]) -> None:
        """
        Update context fields.

        Args:
            updates: Dictionary of field names and new values
        """
        if not self.current_context:
            self.current_context = self.load_context()

        # Update local object
        for key, value in updates.items():
            if hasattr(self.current_context, key):
                setattr(self.current_context, key, value)

        # Update temporal context
        now = datetime.utcnow()
        self.current_context.hora_dia = now.hour
        self.current_context.dia_semana = now.weekday()
        self.current_context.periodo_produtivo = self._get_periodo_produtivo(now.hour)

        # Save to database
        self.db.commit()
        self.db.refresh(self.current_context)

        # Publish context update event
        try:
            import asyncio

            asyncio.create_task(
                self.event_bus.publish(
                    Event(
                        tipo=EventType.CONTEXT_UPDATED,
                        modulo_origem=ModuleName.CONTEXT_MANAGER,
                        payload=updates,
                        prioridade=7,
                    )
                )
            )
        except Exception as e:
            logger.error(f"Failed to publish context update event: {e}")

        logger.debug(f"Context updated: {updates}")

    def get_context(self) -> Dict[str, Any]:
        """
        Get current context as dictionary.

        Returns:
            Dictionary with current context
        """
        if not self.current_context:
            self.current_context = self.load_context()

        return {
            "fase_ciclo": self.current_context.fase_ciclo,
            "energia_atual": self.current_context.energia_atual,
            "carga_trabalho_percentual": self.current_context.carga_trabalho_percentual,
            "em_sessao_foco": self.current_context.em_sessao_foco,
            "tarefas_pendentes": self.current_context.tarefas_pendentes,
            "projetos_ativos": self.current_context.projetos_ativos,
            "notificacoes_nao_lidas": self.current_context.notificacoes_nao_lidas,
            "hora_dia": self.current_context.hora_dia,
            "dia_semana": self.current_context.dia_semana,
            "periodo_produtivo": self.current_context.periodo_produtivo,
            "nivel_stress": self.current_context.nivel_stress,
            "necessita_pausa": self.current_context.necessita_pausa,
            "atualizado_em": self.current_context.atualizado_em.isoformat(),
        }

    # ==================== Decision Helpers ====================

    def should_accept_interruption(self) -> bool:
        """
        Decide if interruption should be accepted based on context.

        Returns:
            True if interruption can be accepted
        """
        if not self.current_context:
            return True

        # In focus? Only critical interruptions
        if self.current_context.em_sessao_foco:
            return False

        # Low energy? Avoid more load
        if self.current_context.energia_atual < 4:
            return False

        # Menstrual phase? More protective
        if self.current_context.fase_ciclo == "menstrual":
            return False

        # High load? Avoid
        if self.current_context.carga_trabalho_percentual > 90:
            return False

        return True

    def get_optimal_activity_type(self) -> str:
        """
        Suggest optimal activity type for current context.

        Returns:
            Activity type recommendation
        """
        if not self.current_context:
            return "flexible"

        fase = self.current_context.fase_ciclo
        energia = self.current_context.energia_atual
        hora = self.current_context.hora_dia

        # Menstrual phase: light work
        if fase == "menstrual":
            return "administrative" if energia < 5 else "light_development"

        # Follicular phase: creative
        if fase == "folicular":
            if 9 <= hora <= 12:  # Morning
                return "strategic_planning"
            else:
                return "creative_development"

        # Ovulation: communication
        if fase == "ovulacao":
            return "meetings_presentations"

        # Luteal: execution
        if fase == "lutea":
            return "execution_completion"

        return "flexible"

    def needs_break(self) -> bool:
        """
        Check if user needs a break.

        Returns:
            True if break is recommended
        """
        if not self.current_context:
            return False

        return (
            self.current_context.necessita_pausa
            or self.current_context.nivel_stress >= 8
            or self.current_context.energia_atual <= 3
        )

    # ==================== Helper Methods ====================

    def _count_pending_tasks(self) -> int:
        """Count pending tasks for user."""
        count = (
            self.db.query(Task)
            .filter(Task.user_id == self.user_id, Task.status.in_(["Pendente", "Em Andamento"]))
            .count()
        )
        return count

    def _get_periodo_produtivo(self, hora: int) -> str:
        """
        Get productivity period based on hour.

        Args:
            hora: Hour of day (0-23)

        Returns:
            Period name
        """
        if 6 <= hora < 12:
            return "manha"
        elif 12 <= hora < 18:
            return "tarde"
        elif 18 <= hora < 22:
            return "noite"
        else:
            return "madrugada"
