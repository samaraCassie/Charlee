"""Agent Orchestrator - Coordena todos os agentes especializados."""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from agent.core_agent import CharleeAgent
from agent.specialized_agents.cycle_aware_agent import CycleAwareAgent
from agent.specialized_agents.capacity_guard_agent import CapacityGuardAgent
from agent.specialized_agents.daily_tracking_agent import DailyTrackingAgent


class AgentOrchestrator:
    """
    Orquestrador inteligente que coordena múltiplos agentes especializados.

    Responsabilidades:
    - Decidir qual agente especializado usar baseado no contexto
    - Coordenar comunicação entre agentes
    - Manter contexto compartilhado
    - Garantir respostas coerentes
    """

    def __init__(
        self,
        db: Session,
        user_id: str = "samara",
        session_id: Optional[str] = None,
        redis_url: str = "redis://redis:6379",
    ):
        """Initialize the orchestrator with all specialized agents."""
        self.database = db
        self.user_id = user_id
        self.session_id = session_id
        self.redis_url = redis_url

        # Initialize all specialized agents
        self.core_agent = CharleeAgent(
            db=db, user_id=user_id, session_id=session_id, redis_url=redis_url
        )

        self.cycle_agent = CycleAwareAgent(db=db)
        self.capacity_agent = CapacityGuardAgent(db=db)
        self.daily_tracking_agent = DailyTrackingAgent(db=db)

        # Track current context
        self.context: Dict[str, Any] = {
            "last_agent_used": None,
            "conversation_topic": None,
            "requires_followup": False,
        }

    def route_message(self, message: str) -> str:
        """
        Routes a message to the appropriate agent based on content analysis.

        Args:
            message: User message

        Returns:
            Response from the appropriate agent
        """
        # Analyze message to determine intent
        intent = self._analyze_intent(message)

        # Route to appropriate agent based on intent
        if intent == "daily_tracking":
            response = self._handle_daily_tracking(message)
        elif intent == "wellness" or intent == "cycle":
            response = self._handle_wellness(message)
        elif intent == "capacity" or intent == "workload":
            response = self._handle_capacity(message)
        elif intent == "tasks":
            # Para tarefas, sempre consultar capacidade antes
            response = self._handle_tasks_with_capacity_check(message)
        else:
            # Default to core agent for general queries
            response = self._handle_core(message)

        return response

    def _analyze_intent(self, message: str) -> str:
        """
        Analyzes message to determine user intent.

        Returns one of:
        - "wellness": cycle-related, energy, health
        - "capacity": workload, overwhelm, new projects
        - "tasks": task management
        - "general": general conversation
        """
        message_lower = message.lower()

        # Wellness/Cycle keywords (expandido)
        wellness_keywords = [
            "ciclo",
            "menstrua",
            "energia",
            "cansa",
            "fase",
            "TPM",
            "ovula",
            "humor",
            "sintoma",
            "período",
            "bem-estar",
            "descanso",
            "saúde",
            "dormir",
            "sono",
            "estresse",
            "ansiedade",
            "hormônio",
        ]

        # Capacity keywords (expandido)
        capacity_keywords = [
            "sobrecarga",
            "muito trabalho",
            "novo projeto",
            "aceitar",
            "compromisso",
            "carga",
            "capacidade",
            "não consigo",
            "muito",
            "trade-off",
            "projeto novo",
            "conseguir fazer",
            "dar conta",
            "prazo",
            "deadline",
            "adiar",
            "priorizar",
            "tempo suficiente",
        ]

        # Task management keywords
        task_keywords = [
            "tarefa",
            "criar tarefa",
            "adicionar tarefa",
            "listar tarefa",
            "big rock",
            "pilar",
            "objetivo",
            "fazer hoje",
            "completar",
            "concluir",
            "marcar como",
        ]

        # Daily tracking keywords
        daily_tracking_keywords = [
            "registrar dia",
            "registro diário",
            "como foi o dia",
            "dormi",
            "sono",
            "acordei",
            "energia hoje",
            "produtividade hoje",
            "deep work",
            "padrões",
            "identificar padrão",
            "otimizar",
            "sugestões",
            "análise",
            "últimos dias",
        ]

        # Check for daily tracking intent
        if any(keyword in message_lower for keyword in daily_tracking_keywords):
            return "daily_tracking"

        # Check for wellness intent
        if any(keyword in message_lower for keyword in wellness_keywords):
            return "wellness"

        # Check for capacity intent
        if any(keyword in message_lower for keyword in capacity_keywords):
            return "capacity"

        # Check for task management
        if any(keyword in message_lower for keyword in task_keywords):
            return "tasks"

        # Default to general
        return "general"

    def _handle_daily_tracking(self, message: str) -> str:
        """Handle daily tracking and pattern analysis queries."""
        self.context["last_agent_used"] = "daily_tracking"
        self.context["conversation_topic"] = "daily_tracking"

        # Get response from daily tracking agent
        response = self.daily_tracking_agent.print_response(message)

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_wellness(self, message: str) -> str:
        """Handle wellness/cycle-related queries."""
        self.context["last_agent_used"] = "cycle_aware"
        self.context["conversation_topic"] = "wellness"

        # Get response from cycle-aware agent
        response = self.cycle_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_capacity(self, message: str) -> str:
        """Handle capacity/workload-related queries."""
        self.context["last_agent_used"] = "capacity_guard"
        self.context["conversation_topic"] = "capacity"

        # Get response from capacity guard agent
        response = self.capacity_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_tasks_with_capacity_check(self, message: str) -> str:
        """
        Handle task-related queries with automatic capacity check.

        When creating new tasks, consults capacity agent to warn about overload.
        """
        self.context["last_agent_used"] = "core_with_capacity"
        self.context["conversation_topic"] = "tasks"

        # Check if user is trying to create/add a task
        is_creating_task = any(
            word in message.lower()
            for word in ["criar", "adicionar", "nova tarefa", "novo compromisso"]
        )

        if is_creating_task:
            # Get capacity insight before creating task
            try:
                capacity_info = self.capacity_agent.calcular_carga_atual(proximas_semanas=2)

                # Add capacity warning to message
                enhanced_message = f"{message}\n\n**IMPORTANTE - Contexto de Capacidade:**\n{capacity_info}\n\nConsidera isso ao criar a tarefa e avise o usuário se houver risco de sobrecarga."
                response = self.core_agent.print_response(enhanced_message)  # type: ignore[func-returns-value]
            except Exception:
                # If capacity check fails, proceed normally
                response = self.core_agent.print_response(message)  # type: ignore[func-returns-value]
        else:
            # For other task operations, use core agent normally
            response = self.core_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_core(self, message: str) -> str:
        """Handle general queries with core agent."""
        self.context["last_agent_used"] = "core"

        # Check if we should consult other agents
        consultation_needed = self._check_consultation_needed(message)

        if consultation_needed:
            # Get insights from specialized agents
            insights = self._gather_insights()

            # Add context to message
            enhanced_message = self._enhance_message_with_context(message, insights)
            response = self.core_agent.print_response(enhanced_message)  # type: ignore[func-returns-value]
        else:
            response = self.core_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _check_consultation_needed(self, message: str) -> bool:
        """
        Checks if specialized agents should be consulted.

        Examples:
        - "Qual meu foco hoje?" -> Check cycle phase, check capacity
        - "Adicionar nova tarefa" -> Check capacity
        """
        message_lower = message.lower()

        needs_consultation_keywords = [
            "foco hoje",
            "o que fazer",
            "prioridade",
            "adicionar tarefa",
            "novo",
            "planejar",
        ]

        return any(keyword in message_lower for keyword in needs_consultation_keywords)

    def _gather_insights(self) -> Dict[str, str]:
        """
        Gather insights from all specialized agents.

        Returns dictionary with context from:
        - Cycle phase and energy levels
        - Current workload capacity
        - Potential overload warnings
        """
        insights = {}

        # Gather cycle/wellness context
        try:
            cycle_info = self.cycle_agent.obter_fase_atual()
            insights["cycle"] = cycle_info
        except Exception as e:
            insights["cycle"] = f"⚠️ Informação de ciclo indisponível: {str(e)}"

        # Gather capacity context
        try:
            capacity_info = self.capacity_agent.calcular_carga_atual(proximas_semanas=2)
            insights["capacity"] = capacity_info
        except Exception as e:
            insights["capacity"] = f"⚠️ Informação de capacidade indisponível: {str(e)}"

        # Gather Big Rocks distribution
        try:
            big_rocks_analysis = self.capacity_agent.analisar_big_rocks()
            insights["big_rocks"] = big_rocks_analysis
        except Exception as e:
            insights["big_rocks"] = f"⚠️ Análise de Big Rocks indisponível: {str(e)}"

        return insights

    def _enhance_message_with_context(self, message: str, insights: Dict[str, str]) -> str:
        """
        Enhances user message with rich context from specialized agents.

        Adds wellness, capacity, and Big Rocks context to help core agent
        make more informed decisions.
        """
        context_parts = []

        if insights.get("cycle"):
            context_parts.append(f"**🌸 Contexto de Bem-Estar:**\n{insights['cycle']}\n")

        if insights.get("capacity"):
            context_parts.append(f"**📊 Contexto de Capacidade:**\n{insights['capacity']}\n")

        if insights.get("big_rocks"):
            context_parts.append(f"**🎯 Distribuição de Big Rocks:**\n{insights['big_rocks']}\n")

        if context_parts:
            context_str = "\n".join(context_parts)
            enhanced = f"{message}\n\n**📋 Contexto Adicional (use para dar respostas mais personalizadas):**\n{context_str}"
            enhanced += "\n\n**INSTRUÇÃO**: Use os contextos acima para adaptar sua resposta. Por exemplo, se a energia está baixa, sugira tarefas leves. Se há sobrecarga, alerte sobre isso."
            return enhanced

        return message

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status with rich details."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "last_agent_used": self.context.get("last_agent_used"),
            "conversation_topic": self.context.get("conversation_topic"),
            "agents_available": {
                "core": True,
                "cycle_aware": True,
                "capacity_guard": True,
                "daily_tracking": True,
            },
            "agents_available": {"core": True, "cycle_aware": True, "capacity_guard": True},
            "orchestration_features": {
                "intelligent_routing": True,
                "cross_agent_consultation": True,
                "capacity_aware_task_creation": True,
                "wellness_context_injection": True,
                "daily_tracking_and_patterns": True,
            },
        }

    def get_routing_decision(self, message: str) -> Dict[str, Any]:
        """
        Analisa uma mensagem e retorna a decisão de roteamento sem executar.

        Útil para debugging e entender como o orquestrador funciona.

        Args:
            message: Mensagem do usuário

        Returns:
            Dictionary com intent, agente escolhido e razão
        """
        intent = self._analyze_intent(message)
        consultation_needed = self._check_consultation_needed(message)

        # Determine which agent would be used
        if intent == "daily_tracking":
            agent = "DailyTrackingAgent"
            reason = "Mensagem contém palavras-chave relacionadas a registro diário e padrões"
        elif intent == "wellness":
            agent = "CycleAwareAgent"
            reason = "Mensagem contém palavras-chave relacionadas a bem-estar/ciclo menstrual"
        elif intent == "capacity":
            agent = "CapacityGuardAgent"
            reason = "Mensagem contém palavras-chave relacionadas a carga de trabalho/capacidade"
        elif intent == "tasks":
            agent = "CharleeAgent (com check de capacidade)"
            reason = "Mensagem relacionada a gestão de tarefas"
        else:
            if consultation_needed:
                agent = "CharleeAgent (com consulta multi-agente)"
                reason = "Mensagem requer contexto de múltiplos agentes especializados"
            else:
                agent = "CharleeAgent"
                reason = "Mensagem geral não requer agentes especializados"

        return {
            "message": message,
            "intent_detected": intent,
            "agent_to_use": agent,
            "reason": reason,
            "will_consult_other_agents": consultation_needed or intent == "tasks",
            "keywords_matched": self._get_matched_keywords(message, intent),
        }

    def _get_matched_keywords(self, message: str, intent: str) -> list:
        """Helper to identify which keywords triggered the intent."""
        message_lower = message.lower()
        matched = []

        if intent == "daily_tracking":
            daily_tracking_keywords = [
                "registrar dia",
                "registro diário",
                "como foi o dia",
                "dormi",
                "sono",
                "acordei",
                "energia hoje",
                "produtividade hoje",
                "deep work",
                "padrões",
                "identificar padrão",
                "otimizar",
                "sugestões",
                "análise",
                "últimos dias",
            ]
            matched = [kw for kw in daily_tracking_keywords if kw in message_lower]

        elif intent == "wellness":
            wellness_keywords = [
                "ciclo",
                "menstrua",
                "energia",
                "cansa",
                "fase",
                "TPM",
                "ovula",
                "humor",
                "sintoma",
                "período",
                "bem-estar",
                "descanso",
                "saúde",
                "dormir",
                "sono",
                "estresse",
                "ansiedade",
                "hormônio",
            ]
            matched = [kw for kw in wellness_keywords if kw in message_lower]

        elif intent == "capacity":
            capacity_keywords = [
                "sobrecarga",
                "muito trabalho",
                "novo projeto",
                "aceitar",
                "compromisso",
                "carga",
                "capacidade",
                "não consigo",
                "muito",
                "trade-off",
                "projeto novo",
                "conseguir fazer",
                "dar conta",
                "prazo",
                "deadline",
                "adiar",
                "priorizar",
                "tempo suficiente",
            ]
            matched = [kw for kw in capacity_keywords if kw in message_lower]

        elif intent == "tasks":
            task_keywords = [
                "tarefa",
                "criar tarefa",
                "adicionar tarefa",
                "listar tarefa",
                "big rock",
                "pilar",
                "objetivo",
                "fazer hoje",
                "completar",
                "concluir",
                "marcar como",
            ]
            matched = [kw for kw in task_keywords if kw in message_lower]

        return matched


def create_orchestrator(
    db: Session,
    user_id: str = "samara",
    session_id: Optional[str] = None,
    redis_url: str = "redis://redis:6379",
) -> AgentOrchestrator:
    """Factory function to create an orchestrator instance."""
    return AgentOrchestrator(db=db, user_id=user_id, session_id=session_id, redis_url=redis_url)
