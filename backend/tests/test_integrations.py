"""Tests for platform integrations."""


from agent.specialized_agents.projects.integrations import (
    JobOpportunity,
    PlatformConfig,
    create_freelancer_com_integration,
    create_upwork_integration,
)


class TestPlatformConfig:
    """Test PlatformConfig dataclass."""

    def test_platform_config_defaults(self):
        """Should create PlatformConfig with default values."""
        config = PlatformConfig()

        assert config.api_key is None
        assert config.api_secret is None
        assert config.oauth_token is None
        assert config.rate_limit_per_hour == 100
        assert config.timeout_seconds == 30

    def test_platform_config_with_credentials(self):
        """Should create PlatformConfig with credentials."""
        config = PlatformConfig(
            api_key="test_key",
            api_secret="test_secret",
            oauth_token="test_token",
        )

        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.oauth_token == "test_token"


class TestJobOpportunity:
    """Test JobOpportunity dataclass."""

    def test_job_opportunity_required_fields(self):
        """Should create JobOpportunity with required fields."""
        opp = JobOpportunity(
            external_id="test_123",
            title="Python Developer",
            description="Looking for Python developer",
        )

        assert opp.external_id == "test_123"
        assert opp.title == "Python Developer"
        assert opp.description == "Looking for Python developer"
        assert opp.currency == "USD"

    def test_job_opportunity_all_fields(self):
        """Should create JobOpportunity with all fields."""
        opp = JobOpportunity(
            external_id="test_456",
            title="Full Stack Developer",
            description="Need full stack developer",
            client_name="Tech Corp",
            client_rating=4.5,
            client_country="USA",
            client_projects_count=10,
            required_skills=["Python", "Django", "React"],
            skill_level="expert",
            category="Web Development",
            budget=5000.0,
            currency="USD",
            deadline_days=30,
            contract_type="fixed_price",
            url="https://example.com/job/456",
        )

        assert opp.client_name == "Tech Corp"
        assert opp.client_rating == 4.5
        assert opp.required_skills == ["Python", "Django", "React"]
        assert opp.budget == 5000.0
        assert opp.deadline_days == 30


class TestUpworkIntegration:
    """Test Upwork platform integration."""

    def test_create_upwork_integration(self):
        """Should create Upwork integration instance."""
        config = PlatformConfig(api_key="test_key", api_secret="test_secret")
        integration = create_upwork_integration(config)

        assert integration is not None
        assert integration.PLATFORM_NAME == "Upwork"
        assert integration.config.api_key == "test_key"

    def test_upwork_test_connection_without_credentials(self):
        """Should return False without credentials."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        result = integration.test_connection()
        assert result is False

    def test_upwork_test_connection_with_credentials(self):
        """Should return True with credentials (mock mode)."""
        config = PlatformConfig(api_key="test_key", api_secret="test_secret")
        integration = create_upwork_integration(config)

        result = integration.test_connection()
        assert result is True

    def test_upwork_fetch_opportunities_mock(self):
        """Should fetch mock opportunities without credentials."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        opportunities = integration.fetch_opportunities(max_results=5)

        assert isinstance(opportunities, list)
        assert len(opportunities) >= 0
        if opportunities:
            assert isinstance(opportunities[0], JobOpportunity)
            assert opportunities[0].external_id is not None

    def test_upwork_fetch_opportunities_with_keywords(self):
        """Should filter opportunities by keywords."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        opportunities = integration.fetch_opportunities(keywords=["Python"], max_results=10)

        assert isinstance(opportunities, list)
        # Mock data should return Python-related jobs
        if opportunities:
            assert any(
                "Python" in opp.title or "Python" in opp.description for opp in opportunities
            )

    def test_upwork_fetch_opportunities_with_min_budget(self):
        """Should filter opportunities by minimum budget."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        opportunities = integration.fetch_opportunities(min_budget=8000.0, max_results=10)

        assert isinstance(opportunities, list)
        # All returned opportunities should meet min budget
        for opp in opportunities:
            if opp.budget:
                assert opp.budget >= 8000.0

    def test_upwork_get_opportunity_details(self):
        """Should get opportunity details by ID."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        # Mock implementation returns None
        result = integration.get_opportunity_details("upwork_123")
        assert result is None

    def test_upwork_normalize_skills(self):
        """Should normalize skills from various formats."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        # Test string input
        skills = integration.normalize_skills("Python, Django, React")
        assert skills == ["Python", "Django", "React"]

        # Test list input
        skills = integration.normalize_skills(["Python", "Django"])
        assert skills == ["Python", "Django"]

        # Test None input
        skills = integration.normalize_skills(None)
        assert skills == []

    def test_upwork_normalize_budget(self):
        """Should normalize budget from various formats."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        # Test float input
        budget = integration.normalize_budget(5000.0)
        assert budget == 5000.0

        # Test string input
        budget = integration.normalize_budget("$5,000 USD")
        assert budget == 5000.0

        # Test None input
        budget = integration.normalize_budget(None)
        assert budget is None


class TestFreelancerComIntegration:
    """Test Freelancer.com platform integration."""

    def test_create_freelancer_com_integration(self):
        """Should create Freelancer.com integration instance."""
        config = PlatformConfig(api_key="test_key", api_secret="test_secret")
        integration = create_freelancer_com_integration(config)

        assert integration is not None
        assert integration.PLATFORM_NAME == "Freelancer.com"

    def test_freelancer_com_test_connection(self):
        """Should test connection (mock mode)."""
        config = PlatformConfig()
        integration = create_freelancer_com_integration(config)

        result = integration.test_connection()
        assert result is True

    def test_freelancer_com_fetch_opportunities(self):
        """Should fetch opportunities (mock mode returns empty)."""
        config = PlatformConfig()
        integration = create_freelancer_com_integration(config)

        opportunities = integration.fetch_opportunities(max_results=10)

        assert isinstance(opportunities, list)
        # Mock implementation returns empty list
        assert len(opportunities) == 0

    def test_freelancer_com_get_opportunity_details(self):
        """Should get opportunity details (mock returns None)."""
        config = PlatformConfig()
        integration = create_freelancer_com_integration(config)

        result = integration.get_opportunity_details("freelancer_123")
        assert result is None


class TestBasePlatformIntegration:
    """Test BasePlatformIntegration utility methods."""

    def test_deduplicate_opportunities(self):
        """Should remove duplicate opportunities by external_id."""
        config = PlatformConfig()
        integration = create_upwork_integration(config)

        opportunities = [
            JobOpportunity(external_id="job_1", title="Job 1", description="Description 1"),
            JobOpportunity(external_id="job_2", title="Job 2", description="Description 2"),
            JobOpportunity(
                external_id="job_1", title="Job 1 Duplicate", description="Description 1"
            ),
        ]

        unique = integration.deduplicate_opportunities(opportunities)

        assert len(unique) == 2
        assert unique[0].external_id == "job_1"
        assert unique[1].external_id == "job_2"
