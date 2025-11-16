"""Tests for MVP 3 orchestrator integration."""

from agent.orchestrator import create_orchestrator


class TestOrchestratorMVP3Integration:
    """Test suite for MVP 3 orchestrator integration."""

    def test_career_insights_intent_detection(self, db, sample_user):
        """Should detect career insights intent correctly."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        messages = [
            "Como está minha carreira nos últimos 90 dias?",
            "Mostre minhas estatísticas de projetos",
            "Análise de carreira",
            "Recomendações para crescimento profissional",
        ]

        for message in messages:
            result = orchestrator.get_routing_decision(message)
            assert result["intent_detected"] == "career_insights"
            assert "CareerInsightsAgent" in result["agent_to_use"]
            assert len(result["keywords_matched"]) > 0

    def test_portfolio_intent_detection(self, db, sample_user):
        """Should detect portfolio intent correctly."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        messages = [
            "Mostrar meu portfólio",
            "Visualizar portfolio de projetos Python",
            "Minhas conquistas",
            "Top achievements",
        ]

        for message in messages:
            result = orchestrator.get_routing_decision(message)
            assert result["intent_detected"] == "portfolio"
            assert result["agent_to_use"] == "PortfolioBuilderAgent"
            assert len(result["keywords_matched"]) > 0

    def test_agents_available_in_status(self, db, sample_user):
        """Should list MVP 3 agents in status."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        status = orchestrator.get_status()

        assert status["agents_available"]["career_insights"] is True
        assert status["agents_available"]["portfolio_builder"] is True

    def test_orchestration_features_updated(self, db, sample_user):
        """Should include MVP 3 features in orchestration features."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        status = orchestrator.get_status()

        assert status["orchestration_features"]["career_analytics"] is True
        assert status["orchestration_features"]["portfolio_generation"] is True

    def test_career_insights_vs_freelancer_priority(self, db, sample_user):
        """Career insights keywords should take priority over freelancer."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        # "carreira" should trigger career_insights, not freelancer
        result = orchestrator.get_routing_decision("Como está minha carreira?")
        assert result["intent_detected"] == "career_insights"

    def test_portfolio_vs_tasks_priority(self, db, sample_user):
        """Portfolio keywords should take priority over tasks."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        # "portfolio" should trigger portfolio, not general
        result = orchestrator.get_routing_decision("Mostrar meu portfólio")
        assert result["intent_detected"] == "portfolio"

    def test_agents_initialization(self, db, sample_user):
        """Should initialize MVP 3 agents correctly."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        assert orchestrator.career_insights_agent is not None
        assert orchestrator.portfolio_builder_agent is not None

        # Check agent properties
        assert orchestrator.career_insights_agent.db is db
        assert orchestrator.portfolio_builder_agent.db is db

    def test_multiple_keywords_matching(self, db, sample_user):
        """Should match multiple keywords correctly."""
        orchestrator = create_orchestrator(db=db, user_id=str(sample_user.id))

        result = orchestrator.get_routing_decision(
            "Mostre meu portfólio de projetos Python e minhas conquistas"
        )

        assert result["intent_detected"] == "portfolio"
        assert len(result["keywords_matched"]) >= 2  # Should match multiple keywords
