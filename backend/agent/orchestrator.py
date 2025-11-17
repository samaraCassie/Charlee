"""Agent Orchestrator - Coordena todos os agentes especializados."""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from agent.core_agent import CharleeAgent
from agent.specialized_agents.capacity_guard_agent import CapacityGuardAgent
from agent.specialized_agents.cycle_aware_agent import CycleAwareAgent
from agent.specialized_agents.daily_tracking_agent import DailyTrackingAgent
from agent.specialized_agents.freelancer_agent import FreelancerAgent
from agent.specialized_agents.projects import (
    CareerInsightsAgent,
    PortfolioBuilderAgent,
)


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
        self.freelancer_agent = FreelancerAgent(db=db)

        # Initialize MVP 3 Projects Intelligence agents
        # Convert user_id to int for projects agents (they use numeric user_id)
        try:
            numeric_user_id = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else 1
        except (ValueError, AttributeError):
            numeric_user_id = 1  # Default to user 1

        self.career_insights_agent = CareerInsightsAgent(db=db, user_id=numeric_user_id)
        self.portfolio_builder_agent = PortfolioBuilderAgent(db=db, user_id=numeric_user_id)

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
        # Check for unread notifications proactively
        unread_count = self._get_unread_notifications_count()
        notification_context = ""

        if unread_count > 0:
            # Add notification context to message
            notification_context = f"\n\n[SISTEMA: Usuário tem {unread_count} notificações não lidas. Se relevante, mencione isso proativamente.]"

        # Analyze message to determine intent
        intent = self._analyze_intent(message)

        # Add notification context if present
        enhanced_message = message + notification_context if notification_context else message

        # Route to appropriate agent based on intent
        if intent == "notifications":
            response = self._handle_notifications(enhanced_message)
        elif intent == "dashboard":
            response = self._handle_dashboard(enhanced_message)
        elif intent == "daily_tracking":
            response = self._handle_daily_tracking(enhanced_message)
        elif intent == "freelancer":
            response = self._handle_freelancer(enhanced_message)
        elif intent == "career_insights":
            response = self._handle_career_insights(enhanced_message)
        elif intent == "portfolio":
            response = self._handle_portfolio(enhanced_message)
        elif intent == "wellness" or intent == "cycle":
            response = self._handle_wellness(enhanced_message)
        elif intent == "capacity" or intent == "workload":
            response = self._handle_capacity(enhanced_message)
        elif intent == "tasks":
            # Para tarefas, sempre consultar capacidade antes
            response = self._handle_tasks_with_capacity_check(enhanced_message)
        else:
            # Default to core agent for general queries
            response = self._handle_core(enhanced_message)

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

        # Freelancer keywords
        freelancer_keywords = [
            "freelance",
            "cliente",
            "projeto freelance",
            "projeto novo",
            "orçamento",
            "invoice",
            "fatura",
            "horas trabalhadas",
            "registrar horas",
            "timetracking",
            "taxa hora",
            "projeto cliente",
            "faturamento",
            "receita mensal",
            "pagamento cliente",
            "trabalho freelance",
            "aceitar projeto",
            "proposta",
            "trabalho remoto",
            "contrato",
        ]

        # Career insights keywords
        career_insights_keywords = [
            "carreira",
            "evolução profissional",
            "progresso",
            "crescimento profissional",
            "análise de carreira",
            "resumo de carreira",
            "habilidades que usei",
            "skills progression",
            "minhas estatísticas",
            "meu desempenho",
            "projetos completados",
            "receita total",
            "valor médio",
            "satisfação do cliente",
            "tendências",
            "recomendações",
            "como está minha carreira",
            "últimos 90 dias",
            "últimos meses",
            "top projetos",
            "melhores projetos",
            "income trends",
        ]

        # Portfolio keywords
        portfolio_keywords = [
            "portfólio",
            "portfolio",
            "meu trabalho",
            "showcas",
            "projetos por skill",
            "categorizar projetos",
            "achievements",
            "conquistas",
            "realizações",
            "descrição do projeto",
            "mostrar meu portfolio",
            "visualizar portfolio",
            "exportar portfolio",
            "projetos python",
            "projetos react",
            "top achievements",
        ]

        # Dashboard keywords (multi-agent summary)
        dashboard_keywords = [
            "resumo geral",
            "dashboard",
            "visão geral",
            "panorama",
            "status geral",
            "como estou",
            "tudo",
            "resumo completo",
            "overview",
            "relatório geral",
            "meu status",
        ]

        # Notification keywords
        notification_keywords = [
            "notificações",
            "notificação",
            "alertas",
            "alerta",
            "avisos",
            "aviso",
            "minhas notificações",
            "ver notificações",
            "listar notificações",
            "notificações não lidas",
            "marcar como lida",
            "marcar lida",
            "limpar notificações",
        ]

        # Check for notification intent (highest priority)
        if any(keyword in message_lower for keyword in notification_keywords):
            return "notifications"

        # Check for dashboard intent (multi-agent summary)
        if any(keyword in message_lower for keyword in dashboard_keywords):
            return "dashboard"

        # Check for career insights intent (check before freelancer as it's more specific)
        if any(keyword in message_lower for keyword in career_insights_keywords):
            return "career_insights"

        # Check for portfolio intent
        if any(keyword in message_lower for keyword in portfolio_keywords):
            return "portfolio"

        # Check for freelancer intent
        if any(keyword in message_lower for keyword in freelancer_keywords):
            return "freelancer"

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

    def _handle_notifications(self, message: str) -> str:
        """Handle notification-related queries."""
        self.context["last_agent_used"] = "core_notifications"
        self.context["conversation_topic"] = "notifications"

        # Core agent has notification tools, so just route to it
        response = self.core_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

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

    def _handle_freelancer(self, message: str) -> str:
        """Handle freelancer project management and invoicing queries."""
        self.context["last_agent_used"] = "freelancer"
        self.context["conversation_topic"] = "freelancer"

        # Get response from freelancer agent
        response = self.freelancer_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_career_insights(self, message: str) -> str:
        """Handle career insights and analytics queries with portfolio cross-reference."""
        self.context["last_agent_used"] = "career_insights"
        self.context["conversation_topic"] = "career_insights"

        # Check for stagnation patterns
        stagnation_alert = self._detect_career_stagnation()
        if stagnation_alert:
            message += f"\n\n**ALERTA PROATIVO:** {stagnation_alert}"

        # Get response from career insights agent
        response = self.career_insights_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_portfolio(self, message: str) -> str:
        """Handle portfolio building and showcasing queries."""
        self.context["last_agent_used"] = "portfolio"
        self.context["conversation_topic"] = "portfolio"

        # Get response from portfolio builder agent
        response = self.portfolio_builder_agent.print_response(message)  # type: ignore[func-returns-value]

        # Extract text from response if it's a RunResponse object
        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _handle_dashboard(self, message: str) -> str:
        """
        Handle comprehensive dashboard queries by consulting multiple agents.

        Provides a unified view combining:
        - Career insights and statistics
        - Portfolio summary
        - Current capacity and workload
        - Wellness/cycle status
        - Recent tracking data
        """
        self.context["last_agent_used"] = "dashboard"
        self.context["conversation_topic"] = "dashboard"

        # Gather comprehensive insights from all agents
        insights = {}

        # Career insights
        try:
            career_summary = self.career_insights_agent.get_career_summary(days=90)
            insights["career"] = career_summary
        except Exception as e:
            insights["career"] = f"⚠️ Dados de carreira indisponíveis: {str(e)}"

        # Portfolio summary
        try:
            portfolio = self.portfolio_builder_agent.build_full_portfolio(include_in_progress=False)
            insights["portfolio"] = portfolio[:500] if len(portfolio) > 500 else portfolio
        except Exception as e:
            insights["portfolio"] = f"⚠️ Portfólio indisponível: {str(e)}"

        # Capacity/workload
        try:
            capacity_info = self.capacity_agent.calcular_carga_atual(proximas_semanas=2)
            insights["capacity"] = capacity_info
        except Exception as e:
            insights["capacity"] = f"⚠️ Informação de capacidade indisponível: {str(e)}"

        # Wellness/cycle
        try:
            cycle_info = self.cycle_agent.obter_fase_atual()
            insights["wellness"] = cycle_info
        except Exception as e:
            insights["wellness"] = f"⚠️ Informação de bem-estar indisponível: {str(e)}"

        # Check for stagnation
        stagnation_alert = self._detect_career_stagnation()
        if stagnation_alert:
            insights["alerts"] = stagnation_alert

        # Build comprehensive dashboard message
        dashboard_message = f"""**📊 DASHBOARD COMPLETO - CHARLEE**

**🎯 Carreira & Projetos (últimos 90 dias):**
{insights.get('career', 'N/A')}

**📂 Portfólio:**
{insights.get('portfolio', 'N/A')}

**⚖️ Capacidade & Carga de Trabalho:**
{insights.get('capacity', 'N/A')}

**🌸 Bem-estar & Energia:**
{insights.get('wellness', 'N/A')}
"""

        if insights.get("alerts"):
            dashboard_message += f"\n\n**⚠️ ALERTAS PROATIVOS:**\n{insights['alerts']}"

        dashboard_message += f"\n\n{message}\n\n**CONTEXTO COMPLETO FORNECIDO ACIMA**"

        # Let core agent synthesize the dashboard with all context
        response = self.core_agent.print_response(dashboard_message)  # type: ignore[func-returns-value]

        if hasattr(response, "content"):
            return response.content
        return str(response)

    def _get_unread_notifications_count(self) -> int:
        """
        Get count of unread notifications for the user.

        Returns:
            Number of unread notifications
        """
        try:
            from database.models import UserNotification

            # Get numeric user_id
            try:
                numeric_user_id = (
                    int(self.user_id) if isinstance(self.user_id, str) and self.user_id.isdigit() else 1
                )
            except (ValueError, AttributeError):
                numeric_user_id = 1

            count = (
                self.database.query(UserNotification)
                .filter(
                    UserNotification.user_id == numeric_user_id,
                    UserNotification.read == False,  # noqa: E712
                )
                .count()
            )

            return count

        except Exception:
            return 0

    def _detect_career_stagnation(self) -> str:
        """
        Detect career stagnation patterns.

        Checks for:
        - No completed projects in last 30 days
        - No new skills in last 60 days
        - Decreasing income trends
        - Low client satisfaction

        Returns:
            Alert message if stagnation detected, empty string otherwise
        """
        try:
            from database.models import ProjectExecution
            from datetime import datetime, timedelta

            # Check completed projects in last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_projects = (
                self.database.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.career_insights_agent.user_id,
                    ProjectExecution.status == "completed",
                    ProjectExecution.created_at >= thirty_days_ago,
                )
                .count()
            )

            alerts = []

            if recent_projects == 0:
                alerts.append(
                    "Nenhum projeto completado nos últimos 30 dias - considere buscar novas oportunidades"
                )

            # Check income trends
            try:
                income_analysis = self.career_insights_agent.get_income_trends(months=3)
                if "decrescente" in income_analysis.lower() or "queda" in income_analysis.lower():
                    alerts.append(
                        "Tendência de receita decrescente detectada - analise oportunidades de maior valor"
                    )
            except Exception:
                pass

            # Check client satisfaction
            sixty_days_ago = datetime.now() - timedelta(days=60)
            low_satisfaction_projects = (
                self.database.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.career_insights_agent.user_id,
                    ProjectExecution.status == "completed",
                    ProjectExecution.created_at >= sixty_days_ago,
                    ProjectExecution.client_satisfaction < 4.0,
                )
                .count()
            )

            if low_satisfaction_projects > 2:
                alerts.append(
                    f"{low_satisfaction_projects} projetos com satisfação baixa (<4.0) - foque em qualidade"
                )

            return "\n".join(f"• {alert}" for alert in alerts) if alerts else ""

        except Exception:
            return ""

    def _get_career_insights_context(self) -> str:
        """
        Get enriched career insights for context injection.

        Returns summary of:
        - Recent projects performance
        - Top skills used
        - Income trends
        - Recommendations
        """
        try:
            summary = self.career_insights_agent.get_career_summary(days=90)
            return f"**Contexto de Carreira (últimos 90 dias):**\n{summary}"
        except Exception as e:
            return f"⚠️ Contexto de carreira indisponível: {str(e)}"

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
        Gather enriched insights from all specialized agents.

        Returns dictionary with context from:
        - Career insights and performance
        - Portfolio and achievements
        - Cycle phase and energy levels
        - Current workload capacity
        - Potential overload warnings
        - Stagnation alerts
        """
        insights = {}

        # Gather career context (NOVO!)
        try:
            career_context = self._get_career_insights_context()
            insights["career"] = career_context
        except Exception as e:
            insights["career"] = f"⚠️ Contexto de carreira indisponível: {str(e)}"

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

        # Check for stagnation alerts (NOVO!)
        try:
            stagnation_alert = self._detect_career_stagnation()
            if stagnation_alert:
                insights["stagnation"] = stagnation_alert
        except Exception:
            pass

        return insights

    def _enhance_message_with_context(self, message: str, insights: Dict[str, str]) -> str:
        """
        Enhances user message with rich context from specialized agents.

        Adds career, wellness, capacity, and Big Rocks context to help core agent
        make more informed decisions.
        """
        context_parts = []

        if insights.get("career"):
            context_parts.append(f"**💼 {insights['career']}\n")

        if insights.get("cycle"):
            context_parts.append(f"**🌸 Contexto de Bem-Estar:**\n{insights['cycle']}\n")

        if insights.get("capacity"):
            context_parts.append(f"**📊 Contexto de Capacidade:**\n{insights['capacity']}\n")

        if insights.get("big_rocks"):
            context_parts.append(f"**🎯 Distribuição de Big Rocks:**\n{insights['big_rocks']}\n")

        if insights.get("stagnation"):
            context_parts.append(f"**⚠️ ALERTAS PROATIVOS:**\n{insights['stagnation']}\n")

        if context_parts:
            context_str = "\n".join(context_parts)
            enhanced = f"{message}\n\n**📋 Contexto Adicional Enriquecido (use para dar respostas mais personalizadas e proativas):**\n{context_str}"
            enhanced += "\n\n**INSTRUÇÃO**: Use os contextos acima para adaptar sua resposta. Por exemplo:\n- Se a energia está baixa, sugira tarefas leves\n- Se há sobrecarga, alerte sobre isso\n- Se detectar estagnação na carreira, sugira ações proativas\n- Se há oportunidades não aproveitadas, recomende análise"
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
                "freelancer": True,
                "career_insights": True,
                "portfolio_builder": True,
            },
            "orchestration_features": {
                "intelligent_routing": True,
                "cross_agent_consultation": True,
                "capacity_aware_task_creation": True,
                "wellness_context_injection": True,
                "daily_tracking_and_patterns": True,
                "career_analytics": True,
                "portfolio_generation": True,
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
        if intent == "dashboard":
            agent = "Multi-Agent Dashboard (Career + Portfolio + Capacity + Wellness)"
            reason = "Mensagem solicita visão geral completa - consulta todos os agentes"
        elif intent == "daily_tracking":
            agent = "DailyTrackingAgent"
            reason = "Mensagem contém palavras-chave relacionadas a registro diário e padrões"
        elif intent == "career_insights":
            agent = "CareerInsightsAgent (com detecção de estagnação)"
            reason = (
                "Mensagem contém palavras-chave relacionadas a análise de carreira e estatísticas"
            )
        elif intent == "portfolio":
            agent = "PortfolioBuilderAgent"
            reason = (
                "Mensagem contém palavras-chave relacionadas a portfólio e showcasing de projetos"
            )
        elif intent == "freelancer":
            agent = "FreelancerAgent"
            reason = "Mensagem contém palavras-chave relacionadas a gestão freelancer e faturamento"
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
                agent = "CharleeAgent (com consulta multi-agente enriquecida)"
                reason = "Mensagem requer contexto de múltiplos agentes especializados incluindo career insights"
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

        if intent == "career_insights":
            career_insights_keywords = [
                "carreira",
                "evolução profissional",
                "progresso",
                "crescimento profissional",
                "análise de carreira",
                "resumo de carreira",
                "habilidades que usei",
                "skills progression",
                "minhas estatísticas",
                "meu desempenho",
                "projetos completados",
                "receita total",
                "valor médio",
                "satisfação do cliente",
                "tendências",
                "recomendações",
                "como está minha carreira",
                "últimos 90 dias",
                "últimos meses",
                "top projetos",
                "melhores projetos",
                "income trends",
            ]
            matched = [kw for kw in career_insights_keywords if kw in message_lower]

        elif intent == "portfolio":
            portfolio_keywords = [
                "portfólio",
                "portfolio",
                "meu trabalho",
                "showcas",
                "projetos por skill",
                "categorizar projetos",
                "achievements",
                "conquistas",
                "realizações",
                "descrição do projeto",
                "mostrar meu portfolio",
                "visualizar portfolio",
                "exportar portfolio",
                "projetos python",
                "projetos react",
                "top achievements",
            ]
            matched = [kw for kw in portfolio_keywords if kw in message_lower]

        elif intent == "freelancer":
            freelancer_keywords = [
                "freelance",
                "cliente",
                "projeto freelance",
                "orçamento",
                "invoice",
                "fatura",
                "horas trabalhadas",
                "registrar horas",
                "timetracking",
                "taxa hora",
                "projeto cliente",
                "faturamento",
                "receita mensal",
                "pagamento cliente",
                "trabalho freelance",
                "aceitar projeto",
                "proposta",
                "trabalho remoto",
                "contrato",
            ]
            matched = [kw for kw in freelancer_keywords if kw in message_lower]

        elif intent == "daily_tracking":
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
