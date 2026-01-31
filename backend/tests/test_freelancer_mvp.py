"""Tests for Freelancer MVP Critical Requirements.

Tests RN09-RN13:
- RN09: Duplication Prevention
- RN10: Rate Limiting
- RN11: Financial Calculator
- RN12: Client Risk Assessment
- RN13: LGPD Compliance
"""

import time
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fakeredis import FakeRedis

from services.freelancer import (
    ClientRiskAssessment,
    FreelancerFinancialCalculator,
    LGPDCompliance,
    PIIEncryption,
    Platform,
    PlatformRateLimiter,
    ProjectDuplicationPrevention,
    RateLimitExceeded,
    UpworkRateLimiter,
)


# ==================== RN09: Duplication Prevention Tests ====================


class TestProjectDuplicationPrevention:
    """Test RN09: Project duplication prevention."""

    @pytest.fixture
    def redis_client(self):
        """Provide fake Redis client."""
        return FakeRedis()

    @pytest.fixture
    def db_session(self):
        """Provide mock database session."""
        return MagicMock()

    @pytest.fixture
    def duplication_service(self, db_session, redis_client):
        """Provide duplication prevention service."""
        return ProjectDuplicationPrevention(db_session, redis_client)

    def test_text_similarity_exact_match(self, duplication_service):
        """Test exact text match gives similarity of 1.0."""
        similarity = duplication_service._text_similarity("Test Project", "Test Project")
        assert similarity == 1.0

    def test_text_similarity_similar_text(self, duplication_service):
        """Test similar text gives high similarity."""
        similarity = duplication_service._text_similarity(
            "Build a Django website", "Build Django website"
        )
        assert similarity > 0.80

    def test_text_similarity_different_text(self, duplication_service):
        """Test different text gives low similarity."""
        similarity = duplication_service._text_similarity(
            "Python developer needed", "React frontend developer"
        )
        assert similarity < 0.30

    def test_acquire_processing_lock_success(self, duplication_service):
        """Test successful lock acquisition."""
        project_id = 123
        token = duplication_service.acquire_processing_lock(project_id)

        assert token is not None
        assert isinstance(token, str)

    def test_acquire_processing_lock_already_locked(self, duplication_service):
        """Test lock acquisition fails when already locked."""
        project_id = 123

        # Acquire lock first time
        token1 = duplication_service.acquire_processing_lock(project_id)
        assert token1 is not None

        # Try to acquire again (should fail)
        token2 = duplication_service.acquire_processing_lock(project_id)
        assert token2 is None

    def test_release_processing_lock(self, duplication_service):
        """Test lock release."""
        project_id = 123

        # Acquire lock
        token = duplication_service.acquire_processing_lock(project_id)
        assert token is not None

        # Release lock
        released = duplication_service.release_processing_lock(project_id, token)
        assert released is True

        # Should be able to acquire again
        token2 = duplication_service.acquire_processing_lock(project_id)
        assert token2 is not None

    def test_is_same_client_exact_match(self, duplication_service):
        """Test client matching with exact name."""
        project1 = {"client_name": "TechCorp Inc"}
        candidate = MagicMock()
        candidate.client_name = "TechCorp Inc"

        assert duplication_service._is_same_client(project1, candidate) is True

    def test_is_same_client_case_insensitive(self, duplication_service):
        """Test client matching is case-insensitive."""
        project1 = {"client_name": "TechCorp Inc"}
        candidate = MagicMock()
        candidate.client_name = "techcorp inc"

        assert duplication_service._is_same_client(project1, candidate) is True


# ==================== RN10: Rate Limiting Tests ====================


class TestRateLimiting:
    """Test RN10: Rate limiting for external APIs."""

    @pytest.fixture
    def redis_client(self):
        """Provide fake Redis client."""
        return FakeRedis()

    @pytest.fixture
    def upwork_limiter(self, redis_client):
        """Provide Upwork rate limiter (100 req/hour)."""
        return UpworkRateLimiter(redis_client)

    def test_rate_limiter_allows_requests_under_limit(self, upwork_limiter):
        """Test that requests under limit are allowed."""
        # Make 10 requests (well under 100 limit)
        for i in range(10):
            assert upwork_limiter.can_make_request() is True

    def test_rate_limiter_blocks_when_limit_exceeded(self, redis_client):
        """Test that rate limiter blocks when limit exceeded."""
        # Create limiter with very low limit for testing
        limiter = PlatformRateLimiter(redis_client, platform="test")
        limiter.max_requests = 3  # Only 3 requests allowed

        # Make 3 requests (at limit)
        for i in range(3):
            limiter.can_make_request()

        # 4th request should raise exception
        with pytest.raises(RateLimitExceeded):
            limiter.can_make_request()

    def test_rate_limiter_resets_after_window(self, redis_client):
        """Test that rate limiter resets after time window."""
        limiter = PlatformRateLimiter(redis_client, platform="test")
        limiter.max_requests = 2
        limiter.window_seconds = 1  # 1 second window for testing

        # Use up quota
        limiter.can_make_request()
        limiter.can_make_request()

        # Should be blocked
        with pytest.raises(RateLimitExceeded):
            limiter.can_make_request()

        # Wait for window to expire
        time.sleep(1.1)

        # Should work again
        assert limiter.can_make_request() is True

    def test_get_remaining_requests(self, upwork_limiter):
        """Test getting remaining request count."""
        # Initially should have full quota
        remaining = upwork_limiter.get_remaining_requests()
        assert remaining == 100

        # Make some requests
        upwork_limiter.can_make_request()
        upwork_limiter.can_make_request()

        # Should have 2 less
        remaining = upwork_limiter.get_remaining_requests()
        assert remaining == 98

    def test_reset_rate_limit(self, upwork_limiter):
        """Test manual rate limit reset."""
        # Use some quota
        upwork_limiter.can_make_request()
        upwork_limiter.can_make_request()

        remaining = upwork_limiter.get_remaining_requests()
        assert remaining == 98

        # Reset
        upwork_limiter.reset()

        # Should have full quota again
        remaining = upwork_limiter.get_remaining_requests()
        assert remaining == 100


# ==================== RN11: Financial Calculator Tests ====================


class TestFinancialCalculator:
    """Test RN11: Complete financial calculator."""

    @pytest.fixture
    def calculator(self):
        """Provide financial calculator."""
        return FreelancerFinancialCalculator(redis_client=None)

    def test_calculate_net_value_simples_nacional(self, calculator):
        """Test calculation with Simples Nacional regime."""
        result = calculator.calculate_net_value(
            gross_usd=1000.0,
            platform="upwork",
            tax_regime="Simples_Nacional",
            custom_exchange_rate=5.00,  # Fixed rate for testing
        )

        # Basic assertions
        assert result["gross_usd"] == 1000.0
        assert result["platform"] == "upwork"
        assert result["tax_regime"] == "Simples_Nacional"
        assert result["exchange_rate"] == 5.00

        # Platform fee (Upwork: 20% on first $500, 10% on rest)
        expected_fee = 500 * 0.20 + 500 * 0.10  # $100 + $50 = $150
        assert result["platform_fee_usd"] == expected_fee

        # Net should be less than gross
        assert result["net_brl"] < result["gross_brl"]

        # Should have all required fields
        assert "spread_fee_brl" in result
        assert "iof_brl" in result
        assert "bank_fee_brl" in result
        assert "tax_brl" in result
        assert "net_brl" in result

    def test_calculate_net_value_mei(self, calculator):
        """Test calculation with MEI regime (fixed tax)."""
        result = calculator.calculate_net_value(
            gross_usd=500.0,
            platform="direct",  # No platform commission
            tax_regime="MEI",
            custom_exchange_rate=5.00,
        )

        # MEI has fixed monthly tax
        assert result["tax_brl"] == 66.60

    def test_platform_commission_upwork_tiered(self, calculator):
        """Test Upwork's tiered commission structure."""
        # Test with $1000 (above $500 threshold)
        fee = calculator._calculate_platform_commission(1000.0, Platform.UPWORK)

        # Should be: $500 * 20% + $500 * 10% = $100 + $50 = $150
        assert fee == 150.0

    def test_platform_commission_direct_no_fee(self, calculator):
        """Test direct clients have no commission."""
        fee = calculator._calculate_platform_commission(1000.0, Platform.DIRECT)
        assert fee == 0.0

    def test_effective_loss_rate_calculation(self, calculator):
        """Test effective loss rate is calculated correctly."""
        result = calculator.calculate_net_value(
            gross_usd=1000.0,
            platform="upwork",
            tax_regime="Simples_Nacional",
            custom_exchange_rate=5.00,
        )

        # Effective loss should be between 0 and 1
        assert 0.0 <= result["effective_loss_rate"] <= 1.0

        # For this scenario, should lose around 35-45% total
        assert 0.30 < result["effective_loss_rate"] < 0.50

    @patch("requests.get")
    def test_banco_central_api_call(self, mock_get, calculator):
        """Test Banco Central API is called correctly."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": [{"cotacaoVenda": 5.123}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        rate = calculator._get_exchange_rate("USD", "BRL")

        assert rate == 5.123
        assert mock_get.called


# ==================== RN12: Client Risk Assessment Tests ====================


class TestClientRiskAssessment:
    """Test RN12: Client risk assessment."""

    @pytest.fixture
    def risk_service(self):
        """Provide risk assessment service."""
        return ClientRiskAssessment()

    def test_score_project_with_red_flags(self, risk_service):
        """Test project with red flags gets low score."""
        project = {
            "title": "Quick simple task ASAP",
            "description": "Need a quick and easy app. No payment until launch.",
            "client_rating": 2.5,
            "client_projects_count": 0,
            "budget": 100.0,
        }

        result = risk_service.score_project(project, fair_value_usd=1000.0)

        # Should have low risk score
        assert result["risk_score"] < 50
        assert result["risk_level"] in ["high", "critical"]
        assert result["recommendation"] == "reject_high_risk"
        assert result["red_flags_count"] > 0

    def test_score_project_with_green_flags(self, risk_service):
        """Test project with green flags gets high score."""
        project = {
            "title": "Professional Django application development",
            "description": (
                "We need an experienced Django developer to build a custom CRM system. "
                "Detailed requirements and mockups are ready. We have 15 completed projects "
                "and excellent ratings from previous freelancers. Budget is flexible for "
                "the right candidate. Timeline is realistic with proper documentation provided."
            ),
            "client_rating": 4.8,
            "client_projects_count": 15,
            "budget": 12000.0,
        }

        result = risk_service.score_project(project, fair_value_usd=10000.0)

        # Should have high risk score (low risk)
        assert result["risk_score"] >= 70
        assert result["risk_level"] == "low"
        assert result["recommendation"] == "safe_to_accept"
        assert result["green_flags_count"] > 0

    def test_detect_vague_requirements(self, risk_service):
        """Test detection of vague requirements."""
        project = {
            "title": "Simple quick project",
            "description": "Just a basic app, very easy and straightforward.",
        }

        flags = risk_service._detect_vague_requirements(project)

        assert len(flags) > 0
        assert flags[0]["type"] == "vague_requirements"

    def test_detect_unrealistic_budget(self, risk_service):
        """Test detection of unrealistically low budget."""
        project = {"budget": 500.0}

        flags = risk_service._detect_unrealistic_budget(project, fair_value=2000.0)

        assert len(flags) > 0
        assert flags[0]["type"] == "unrealistic_budget"

    def test_detect_free_work_request(self, risk_service):
        """Test detection of free work requests."""
        project = {
            "description": "Please provide a test task to prove your skills before we hire you."
        }

        flags = risk_service._detect_free_work_request(project)

        assert len(flags) > 0
        assert flags[0]["type"] == "free_work_request"
        assert flags[0]["severity"] == "critical"

    def test_detect_experienced_client(self, risk_service):
        """Test detection of experienced clients."""
        project = {"client_projects_count": 25}

        flags = risk_service._detect_experienced_client(project)

        assert len(flags) > 0
        assert flags[0]["type"] == "experienced_client"


# ==================== RN13: LGPD Compliance Tests ====================


class TestLGPDCompliance:
    """Test RN13: LGPD compliance."""

    @pytest.fixture
    def pii_encryption(self):
        """Provide PII encryption service."""
        # Generate a test key
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        return PIIEncryption(encryption_key=key.decode())

    @pytest.fixture
    def db_session(self):
        """Provide mock database session."""
        return MagicMock()

    @pytest.fixture
    def lgpd_service(self, db_session):
        """Provide LGPD compliance service."""
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        return LGPDCompliance(db_session, encryption_key=key.decode())

    def test_encrypt_decrypt_roundtrip(self, pii_encryption):
        """Test data can be encrypted and decrypted."""
        original = "John Doe"

        encrypted = pii_encryption.encrypt(original)
        assert encrypted != original  # Should be encrypted
        assert encrypted is not None

        decrypted = pii_encryption.decrypt(encrypted)
        assert decrypted == original  # Should match original

    def test_encrypt_none_returns_none(self, pii_encryption):
        """Test encrypting None returns None."""
        assert pii_encryption.encrypt(None) is None

    def test_decrypt_none_returns_none(self, pii_encryption):
        """Test decrypting None returns None."""
        assert pii_encryption.decrypt(None) is None

    def test_encrypt_dict_fields(self, pii_encryption):
        """Test encrypting specific fields in dictionary."""
        data = {"client_name": "John Doe", "title": "Project Title", "budget": 1000}

        encrypted = pii_encryption.encrypt_dict(data, fields=["client_name"])

        # Client name should be encrypted
        assert encrypted["client_name"] != data["client_name"]

        # Other fields should remain unchanged
        assert encrypted["title"] == data["title"]
        assert encrypted["budget"] == data["budget"]

    def test_decrypt_dict_fields(self, pii_encryption):
        """Test decrypting specific fields in dictionary."""
        data = {"client_name": "John Doe", "title": "Project Title"}

        encrypted = pii_encryption.encrypt_dict(data, fields=["client_name"])
        decrypted = pii_encryption.decrypt_dict(encrypted, fields=["client_name"])

        # Should match original
        assert decrypted["client_name"] == data["client_name"]
        assert decrypted["title"] == data["title"]

    def test_encrypt_opportunity_pii(self, lgpd_service):
        """Test encrypting opportunity PII."""
        opportunity_data = {
            "client_name": "TechCorp Inc",
            "title": "Django Project",
            "budget": 5000,
        }

        encrypted = lgpd_service.encrypt_opportunity_pii(opportunity_data)

        # Client name should be encrypted
        assert encrypted["client_name"] != opportunity_data["client_name"]

        # Other fields unchanged
        assert encrypted["title"] == opportunity_data["title"]

    def test_decrypt_opportunity_pii(self, lgpd_service):
        """Test decrypting opportunity PII."""
        opportunity_data = {"client_name": "TechCorp Inc", "title": "Django Project"}

        encrypted = lgpd_service.encrypt_opportunity_pii(opportunity_data)
        decrypted = lgpd_service.decrypt_opportunity_pii(encrypted)

        # Should match original
        assert decrypted["client_name"] == opportunity_data["client_name"]


# ==================== Integration Tests ====================


class TestIntegrationService:
    """Test integrated MVP services working together."""

    @pytest.fixture
    def redis_client(self):
        """Provide fake Redis client."""
        return FakeRedis()

    @pytest.fixture
    def db_session(self):
        """Provide mock database session."""
        return MagicMock()

    @pytest.fixture
    def encryption_key(self):
        """Provide test encryption key."""
        from cryptography.fernet import Fernet

        return Fernet.generate_key().decode()

    @pytest.fixture
    def integration_service(self, db_session, redis_client, encryption_key):
        """Provide integration service."""
        from services.freelancer import create_integration_service

        return create_integration_service(db_session, redis_client, encryption_key)

    def test_all_services_can_be_initialized(self, db_session, redis_client):
        """Test all MVP services can be initialized together."""
        from services.freelancer.integration_service import FreelancerIntegrationService

        service = FreelancerIntegrationService(db_session, redis_client)

        assert service.duplication is not None
        assert service.financial is not None
        assert service.risk_assessment is not None
        assert service.lgpd is not None

    def test_process_opportunity_complete_pipeline(self, integration_service, db_session):
        """
        Test complete opportunity processing pipeline.

        Scenario: Good project with fair budget and experienced client.
        Expected: All checks pass, recommendation is ACCEPT.
        """
        from services.freelancer.integration_service import OpportunityProcessingInput

        # Mock database query for duplication check (no duplicates found)
        db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )

        opportunity_data = OpportunityProcessingInput(
            title="Senior Django Developer for E-commerce Platform",
            description="""
                We need an experienced Django developer to build a REST API
                for our e-commerce platform. Full specification and mockups available.

                Requirements:
                - 5+ years Django experience
                - REST API design
                - PostgreSQL database
                - Docker deployment

                Timeline: 6 weeks
                Budget: $8,000 USD

                We have worked with 20+ developers and have 4.9 rating.
            """,
            budget=8000.0,
            client_name="Global Retail Corp",
            client_rating=4.9,
            client_projects_count=20,
            client_payment_verified=True,
            external_id="upwork_test_12345",
            estimated_hours=200.0,
            deadline_date=date.today().isoformat(),
        )

        result = integration_service.process_new_opportunity(
            opportunity_data=opportunity_data,
            user_id=1,
            platform="upwork",
            tax_regime="Simples_Nacional",
        )

        # Verify all checks passed
        assert "rate_limit" in result["checks_passed"]
        assert "duplication" in result["checks_passed"]
        assert "financial" in result["checks_passed"]
        assert "risk_assessment" in result["checks_passed"]

        # Verify no critical failures
        assert len(result["checks_failed"]) == 0

        # Verify financial calculation
        assert result["financial_analysis"] is not None
        assert result["financial_analysis"]["gross_usd"] == 8000.0
        assert result["financial_analysis"]["net_brl"] > 0

        # Verify risk assessment
        assert result["risk_assessment"] is not None
        assert result["risk_assessment"]["risk_score"] >= 70  # Safe to accept
        assert result["risk_assessment"]["risk_level"] == "safe_to_accept"

        # Verify final recommendation
        assert result["final_recommendation"]["decision"] == "accept"

    def test_process_opportunity_high_risk_rejection(self, integration_service, db_session):
        """
        Test pipeline with high-risk project.

        Scenario: Project with unrealistic budget, vague requirements, new client.
        Expected: High risk detected, recommendation is REJECT.
        """
        from services.freelancer.integration_service import OpportunityProcessingInput

        # Mock database query (no duplicates)
        db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )

        opportunity_data = OpportunityProcessingInput(
            title="Quick simple task ASAP",
            description="Need app done today. Will pay after launch. No budget yet.",
            budget=100.0,  # Unrealistic for "app"
            client_name="Anonymous Client",
            client_rating=2.3,  # Low rating
            client_projects_count=0,  # New client
            client_payment_verified=False,
            external_id="upwork_risky_999",
            estimated_hours=40.0,  # Would need much more time
            deadline_date=date.today().isoformat(),  # Today = urgent
        )

        result = integration_service.process_new_opportunity(
            opportunity_data=opportunity_data,
            user_id=1,
            platform="upwork",
            tax_regime="Simples_Nacional",
        )

        # Risk assessment should detect red flags
        assert result["risk_assessment"] is not None
        assert result["risk_assessment"]["risk_score"] < 50  # High risk
        assert result["risk_assessment"]["risk_level"] == "reject_high_risk"

        # Should have red flags
        assert result["risk_assessment"]["red_flags_count"] > 0

        # Final recommendation should be reject
        assert result["final_recommendation"]["decision"] == "reject"

    def test_process_opportunity_duplicate_detected(self, integration_service, db_session):
        """
        Test duplicate detection stops processing.

        Scenario: Same project submitted twice.
        Expected: Duplicate detected, processing stopped, warning issued.
        """
        from services.freelancer.integration_service import OpportunityProcessingInput

        # Mock database query to return existing similar project
        mock_existing = MagicMock()
        mock_existing.id = 42
        mock_existing.title = "Build Django API"
        mock_existing.client_name = "Test Client"
        mock_existing.budget = 3000.0

        db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_existing
        ]

        opportunity_data = OpportunityProcessingInput(
            title="Build Django API",  # Same title
            description="Build REST API with Django",
            budget=3000.0,  # Same budget
            client_name="Test Client",  # Same client
            external_id="upwork_duplicate_123",
            estimated_hours=100.0,
            deadline_date=date.today().isoformat(),
        )

        result = integration_service.process_new_opportunity(
            opportunity_data=opportunity_data,
            user_id=1,
            platform="upwork",
            tax_regime="Simples_Nacional",
        )

        # Should detect duplicate
        assert result["duplicate_info"] is not None
        assert result["duplicate_info"]["is_duplicate"] is True
        assert result["duplicate_info"]["original_id"] == 42

        # Should have warning about duplicate
        assert any("duplicate" in warning.lower() for warning in result["warnings"])

    def test_financial_and_risk_integration(self, integration_service):
        """
        Test that financial calculator and risk assessment work together.

        Scenario: Fair budget project → calculate net value → assess risk.
        Expected: Both services agree on project viability.
        """
        from services.freelancer.financial_calculator import FinancialCalculationInput
        from services.freelancer.client_risk import ProjectRiskInput

        # Financial calculation
        financial_input = FinancialCalculationInput(
            gross_usd=5000.0, platform="upwork", tax_regime="Simples_Nacional"
        )

        financial_result = integration_service.financial.calculate_net_value(financial_input)

        # Risk assessment
        risk_input = ProjectRiskInput(
            title="Build Django REST API",
            description="Detailed project with clear requirements and mockups available",
            budget=5000.0,
            client_rating=4.5,
            client_projects_count=15,
        )

        risk_result = integration_service.risk_assessment.score_project(
            project=risk_input, fair_value_usd=4500.0, estimated_hours=120
        )

        # Verify integration
        # Financial should show good net value
        assert financial_result["net_brl"] > 10000.0  # Reasonable net in BRL

        # Risk should be acceptable
        assert risk_result["risk_score"] >= 50
        assert risk_result["risk_level"] != "reject_high_risk"

        # Both agree this is a viable project
        assert financial_result["effective_loss_rate"] < 0.50  # Less than 50% loss
        assert risk_result["risk_score"] > 40  # Above critical threshold


# ==================== Edge Cases and Error Handling ====================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_financial_calculator_with_zero_budget(self):
        """Test financial calculator rejects zero budget."""
        from pydantic import ValidationError
        from services.freelancer.financial_calculator import FinancialCalculationInput

        with pytest.raises(ValidationError):
            FinancialCalculationInput(
                gross_usd=0.0,  # Invalid: must be > 0
                platform="upwork",
                tax_regime="Simples_Nacional",
            )

    def test_financial_calculator_with_negative_budget(self):
        """Test financial calculator rejects negative budget."""
        from pydantic import ValidationError
        from services.freelancer.financial_calculator import FinancialCalculationInput

        with pytest.raises(ValidationError):
            FinancialCalculationInput(
                gross_usd=-1000.0,  # Invalid: must be > 0
                platform="upwork",
                tax_regime="Simples_Nacional",
            )

    def test_risk_assessment_with_missing_data(self):
        """Test risk assessment works with partial data."""
        from services.freelancer import ClientRiskAssessment
        from services.freelancer.client_risk import ProjectRiskInput

        risk = ClientRiskAssessment()

        # Minimal data (only title)
        project = ProjectRiskInput(
            title="Test Project",
            description=None,  # Missing
            budget=None,  # Missing
            client_rating=None,  # Missing
            client_projects_count=None,  # Missing
        )

        result = risk.score_project(project=project, fair_value_usd=1000.0, estimated_hours=20)

        # Should still return valid result (with default penalties)
        assert "risk_score" in result
        assert "risk_level" in result
        assert "recommendation" in result

        # Score should be lower due to missing data
        assert result["risk_score"] < 70

    def test_lgpd_encryption_with_empty_string(self):
        """Test LGPD encryption handles empty strings."""
        from cryptography.fernet import Fernet
        from services.freelancer import PIIEncryption

        encryption_key = Fernet.generate_key().decode()
        pii = PIIEncryption(encryption_key)

        # Empty string should return None
        encrypted = pii.encrypt("")
        assert encrypted is None

        # None should return None
        encrypted_none = pii.encrypt(None)
        assert encrypted_none is None

    def test_lgpd_decryption_of_invalid_token(self):
        """Test LGPD decryption handles invalid tokens gracefully."""
        from cryptography.fernet import Fernet
        from services.freelancer import PIIEncryption

        encryption_key = Fernet.generate_key().decode()
        pii = PIIEncryption(encryption_key)

        # Invalid token should raise error or return None
        with pytest.raises(Exception):  # Fernet raises InvalidToken
            pii.decrypt("invalid_token_not_base64")

    def test_rate_limiter_concurrent_requests(self):
        """Test rate limiter handles concurrent requests correctly."""
        redis_client = FakeRedis()
        rate_limiter = UpworkRateLimiter(redis_client)

        # Make multiple requests rapidly
        successful_requests = 0
        for i in range(150):  # Try to exceed limit of 100
            try:
                rate_limiter.can_make_request(user_id=1)
                successful_requests += 1
            except RateLimitExceeded:
                break

        # Should allow exactly 100 requests
        assert successful_requests == 100

    def test_duplication_with_very_long_titles(self):
        """Test duplication detection handles very long titles."""
        redis_client = FakeRedis()
        db_session = MagicMock()
        duplication = ProjectDuplicationPrevention(db_session, redis_client)

        # Very long title (300+ chars)
        long_title = "A" * 500

        similarity = duplication._text_similarity(long_title, long_title)

        # Should still work correctly
        assert similarity == 1.0

    def test_integration_service_with_missing_encryption_key(self):
        """Test integration service fails gracefully without encryption key."""
        from services.freelancer import create_integration_service

        redis_client = FakeRedis()
        db_session = MagicMock()

        # Missing encryption key should raise ValueError
        with pytest.raises(ValueError, match="ENCRYPTION_KEY.*required"):
            create_integration_service(db_session, redis_client, encryption_key=None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
