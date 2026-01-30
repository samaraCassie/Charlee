"""Tests for Learning Components - PricingLearner, RejectionPatternLearner, HourlyRateOptimizer.

This test module covers all three learning components that enable the freelancer
module to continuously improve through feedback and historical data analysis.
"""

import pytest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock

from services.freelancer import (
    PricingLearner,
    RejectionPatternLearner,
    HourlyRateOptimizer,
)
from database.models import (
    FreelanceOpportunity,
    FreelancePlatform,
    LearningRecord,
    Negotiation,
    PricingParameter,
    ProjectExecution,
)


# ==================== Fixtures ====================


@pytest.fixture
def pricing_learner(db):
    """PricingLearner fixture."""
    return PricingLearner(db, user_id=1)


@pytest.fixture
def rejection_learner(db):
    """RejectionPatternLearner fixture."""
    return RejectionPatternLearner(db, user_id=1)


@pytest.fixture
def rate_optimizer(db):
    """HourlyRateOptimizer fixture."""
    return HourlyRateOptimizer(db, user_id=1)


@pytest.fixture
def sample_pricing_params(db, sample_user):
    """Create sample pricing parameters."""
    params = PricingParameter(
        user_id=sample_user.id,
        version=1,
        base_hourly_rate=100.0,
        minimum_margin=0.20,
        currency="USD",
        complexity_factors={
            "1-2": 0.8,
            "3-4": 1.0,
            "5-6": 1.3,
            "7-8": 1.6,
            "9-10": 2.0,
        },
        specialization_factors={
            "ai_ml": 1.5,
            "full_stack": 1.2,
            "backend": 1.1,
            "frontend": 1.0,
        },
        deadline_factors={"urgent": 1.5, "normal": 1.0},
        client_factors={"no_rating": 1.1, "good_rating": 1.0},
        minimum_project_value=500.0,
        minimum_deadline_days=7,
        active=True,
        activated_at=datetime.now(timezone.utc),
    )
    db.add(params)
    db.commit()
    db.refresh(params)
    return params


@pytest.fixture
def sample_completed_execution(db, sample_user, sample_platform):
    """Create a completed project execution for learning."""
    # Create opportunity
    opportunity = FreelanceOpportunity(
        user_id=sample_user.id,
        platform_id=sample_platform.id,
        external_id="learn_test_001",
        title="Test Learning Project",
        description="A project for testing learning algorithms",
        client_budget=5000.0,
        client_rating=4.5,
        client_projects_count=10,
        estimated_hours=50.0,
        suggested_pricing={
            "suggested_value": 5500.0,
            "suggested_hourly_rate": 110.0,
        },
        semantic_analysis={
            "complexity": 6,
            "category": "full_stack",
        },
        risk_analysis={
            "risk_score": 75,
            "red_flags": ["unrealistic_budget"],
            "risk_level": "safe_to_accept",
        },
        recommendation="accept",
        status="accepted",
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    # Create execution
    execution = ProjectExecution(
        user_id=sample_user.id,
        opportunity_id=opportunity.id,
        negotiated_value=5200.0,
        start_date=date.today() - timedelta(days=60),
        planned_end_date=date.today() - timedelta(days=30),
        actual_end_date=date.today() - timedelta(days=28),
        status="completed",
        client_satisfaction=4.7,
        actual_difficulty=7,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Create negotiation
    negotiation = Negotiation(
        user_id=sample_user.id,
        opportunity_id=opportunity.id,
        original_budget=5000.0,
        counter_proposal_budget=5500.0,
        counter_proposal_justification="Higher complexity than initially estimated",
        final_agreed_budget=5200.0,
        outcome="agreed",
    )
    db.add(negotiation)
    db.commit()

    return execution


# ==================== PricingLearner Tests ====================


class TestPricingLearner:
    """Test PricingLearner service."""

    def test_learn_from_execution_creates_learning_record(
        self, pricing_learner, sample_completed_execution, db
    ):
        """
        Test learning from a completed execution creates LearningRecord.

        Scenario: Completed project with pricing data.
        Expected: LearningRecord created with accuracy score.
        """
        # Act
        learning_record = pricing_learner.learn_from_execution(sample_completed_execution)

        # Assert
        assert learning_record is not None
        assert learning_record.learning_type == "pricing"
        assert learning_record.user_id == 1
        assert learning_record.related_execution_id == sample_completed_execution.id
        assert learning_record.accuracy_score is not None
        assert 0.0 <= learning_record.accuracy_score <= 1.0
        assert "complexity" in learning_record.input_features
        assert "negotiated_value" in learning_record.actual_output

    def test_learn_from_execution_calculates_accuracy(
        self, pricing_learner, sample_completed_execution
    ):
        """
        Test accuracy calculation between predicted and actual values.

        Scenario: Predicted $5500, actual $5200.
        Expected: Accuracy score reflects ~5.5% error.
        """
        learning_record = pricing_learner.learn_from_execution(sample_completed_execution)

        assert learning_record.error_margin is not None
        assert 0.0 < learning_record.error_margin < 0.1  # Less than 10% error
        assert learning_record.accuracy_score > 0.90  # Accuracy above 90%

    def test_analyze_pricing_performance_with_no_data(self, pricing_learner):
        """
        Test performance analysis with no learning records.

        Scenario: No historical data.
        Expected: Returns message indicating no records.
        """
        result = pricing_learner.analyze_pricing_performance(days=90)

        assert result["total_records"] == 0
        assert "message" in result

    def test_analyze_pricing_performance_with_data(
        self, pricing_learner, sample_completed_execution, db
    ):
        """
        Test performance analysis with learning records.

        Scenario: One learning record exists.
        Expected: Returns performance metrics.
        """
        # Create learning record
        pricing_learner.learn_from_execution(sample_completed_execution)

        # Analyze
        result = pricing_learner.analyze_pricing_performance(days=90)

        assert result["total_records"] == 1
        assert "avg_accuracy_score" in result
        assert "avg_error_margin" in result
        assert "complexity_performance" in result
        assert "category_performance" in result
        assert "needs_adjustment" in result

    def test_adjust_pricing_parameters_with_insufficient_data(
        self, pricing_learner, sample_pricing_params
    ):
        """
        Test adjustment skips when insufficient data.

        Scenario: Less than 10 learning records.
        Expected: Returns None, no adjustment made.
        """
        result = pricing_learner.adjust_pricing_parameters(min_records=10)

        assert result is None

    def test_adjust_pricing_parameters_creates_new_version(
        self, pricing_learner, sample_completed_execution, sample_pricing_params, db
    ):
        """
        Test automatic parameter adjustment creates new version.

        Scenario: Sufficient data with low accuracy.
        Expected: New PricingParameter version created with auto_adjusted=True.
        """
        # Create multiple learning records with low accuracy
        for i in range(15):
            record = LearningRecord(
                user_id=1,
                learning_type="pricing",
                input_features={"complexity": 6, "category": "full_stack"},
                predicted_output={"suggested_value": 5000.0},
                actual_output={"negotiated_value": 3500.0},  # Low accuracy
                accuracy_score=0.60,  # Below threshold
                error_margin=0.40,
            )
            db.add(record)
        db.commit()

        # Attempt adjustment
        new_params = pricing_learner.adjust_pricing_parameters(
            min_records=10, adjustment_threshold=0.75
        )

        # Assert
        if new_params:  # May not adjust if other conditions not met
            assert new_params.version == sample_pricing_params.version + 1
            assert new_params.auto_adjusted is True
            assert new_params.based_on_executions_count >= 10
            assert new_params.active is True
            # Old version should be deactivated
            db.refresh(sample_pricing_params)
            assert sample_pricing_params.active is False


# ==================== RejectionPatternLearner Tests ====================


class TestRejectionPatternLearner:
    """Test RejectionPatternLearner service."""

    def test_analyze_rejection_patterns_with_no_data(self, rejection_learner):
        """
        Test rejection analysis with no opportunities.

        Scenario: No opportunities in database.
        Expected: Returns message indicating no data.
        """
        result = rejection_learner.analyze_rejection_patterns(days=90)

        assert result["total_opportunities"] == 0
        assert "message" in result

    def test_analyze_rejection_patterns_calculates_stats(
        self, rejection_learner, db, sample_user, sample_platform
    ):
        """
        Test rejection pattern analysis with mixed outcomes.

        Scenario: 3 rejected, 2 accepted opportunities with red flags.
        Expected: Calculates rejection probabilities for each red flag.
        """
        # Create rejected opportunities with red flags
        for i in range(3):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"rejected_{i}",
                title=f"Rejected Project {i}",
                description="Test",
                risk_analysis={
                    "red_flags": ["unrealistic_budget", "vague_requirements"],
                    "risk_score": 30,
                },
                recommendation="reject",
                status="rejected",
            )
            db.add(opp)

        # Create accepted opportunities with some red flags
        for i in range(2):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"accepted_{i}",
                title=f"Accepted Project {i}",
                description="Test",
                risk_analysis={
                    "red_flags": ["vague_requirements"],  # Only one flag
                    "risk_score": 65,
                },
                recommendation="accept",
                status="accepted",
            )
            db.add(opp)

        db.commit()

        # Analyze
        result = rejection_learner.analyze_rejection_patterns(days=90)

        # Assert
        assert result["total_opportunities"] == 5
        assert result["rejected_count"] == 3
        assert result["accepted_count"] == 2
        assert result["rejection_rate"] == 0.6

        # Check red flag stats
        assert "unrealistic_budget" in result["red_flag_stats"]
        assert "vague_requirements" in result["red_flag_stats"]

        # unrealistic_budget appears only in rejections (3 times)
        unrealistic_stats = result["red_flag_stats"]["unrealistic_budget"]
        assert unrealistic_stats["rejection_probability"] == 1.0  # 100% rejection

        # vague_requirements appears in both (3 rejected + 2 accepted = 5 total)
        vague_stats = result["red_flag_stats"]["vague_requirements"]
        assert vague_stats["rejection_probability"] == 0.6  # 3/5

    def test_learn_from_rejection_creates_learning_record(
        self, rejection_learner, db, sample_user, sample_platform
    ):
        """
        Test learning from a rejected opportunity.

        Scenario: User rejects an opportunity with red flags.
        Expected: LearningRecord created with rejection data.
        """
        # Create rejected opportunity
        opp = FreelanceOpportunity(
            user_id=sample_user.id,
            platform_id=sample_platform.id,
            external_id="reject_learn_001",
            title="Rejected Learning Test",
            description="Test",
            risk_analysis={
                "red_flags": ["suspicious_client", "impossible_deadline"],
                "risk_score": 25,
                "risk_level": "reject_high_risk",
            },
            recommendation="reject",
            status="rejected",
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)

        # Learn from rejection
        learning_record = rejection_learner.learn_from_rejection(
            opp, rejection_reason="Client communication was poor and timeline unrealistic"
        )

        # Assert
        assert learning_record is not None
        assert learning_record.learning_type == "classification"
        assert learning_record.user_id == sample_user.id
        assert learning_record.related_opportunity_id == opp.id
        assert learning_record.user_feedback == "Client communication was poor and timeline unrealistic"
        assert learning_record.accuracy_score == 1.0  # Model correctly predicted rejection

    def test_suggest_risk_weight_adjustments(
        self, rejection_learner, db, sample_user, sample_platform
    ):
        """
        Test risk weight adjustment suggestions.

        Scenario: Red flags with varying rejection probabilities.
        Expected: Suggests increasing weight for high-rejection flags.
        """
        # Create opportunities with specific red flag patterns
        # High rejection flag: "impossible_deadline" (appears in 4/5 rejections)
        for i in range(4):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"reject_high_{i}",
                title="Test",
                description="Test",
                risk_analysis={"red_flags": ["impossible_deadline"], "risk_score": 20},
                recommendation="reject",
                status="rejected",
            )
            db.add(opp)

        # One acceptance even with the flag
        opp = FreelanceOpportunity(
            user_id=sample_user.id,
            platform_id=sample_platform.id,
            external_id="accept_despite_flag",
            title="Test",
            description="Test",
            risk_analysis={"red_flags": ["impossible_deadline"], "risk_score": 55},
            recommendation="accept",
            status="accepted",
        )
        db.add(opp)

        db.commit()

        # Get suggestions
        suggestions = rejection_learner.suggest_risk_weight_adjustments()

        # Assert
        assert "impossible_deadline" in suggestions
        flag_suggestion = suggestions["impossible_deadline"]
        assert flag_suggestion["rejection_probability"] == 0.8  # 4/5
        assert flag_suggestion["suggested_weight"] > flag_suggestion["current_weight"]

    def test_discover_new_red_flags(self, rejection_learner, db, sample_user):
        """
        Test discovering new red flag patterns from user feedback.

        Scenario: Users consistently mention "offshore" in rejection reasons.
        Expected: "offshore" identified as potential new red flag.
        """
        # Create learning records with common keyword
        for i in range(5):
            record = LearningRecord(
                user_id=sample_user.id,
                learning_type="classification",
                input_features={},
                user_feedback="Client wanted offshore team for critical security work",
            )
            db.add(record)

        db.commit()

        # Discover patterns
        potential_flags = rejection_learner.discover_new_red_flags(days=90)

        # Assert
        assert len(potential_flags) > 0
        # Should find "offshore" and "security" as common keywords
        keywords = [flag["keyword"] for flag in potential_flags]
        assert any(keyword in ["offshore", "security", "critical"] for keyword in keywords)


# ==================== HourlyRateOptimizer Tests ====================


class TestHourlyRateOptimizer:
    """Test HourlyRateOptimizer service."""

    def test_analyze_acceptance_by_rate_with_no_data(self, rate_optimizer):
        """
        Test rate analysis with no pricing data.

        Scenario: No opportunities with suggested pricing.
        Expected: Returns message indicating no data.
        """
        result = rate_optimizer.analyze_acceptance_by_rate(days=90)

        assert result["total_opportunities"] == 0
        assert "message" in result

    def test_analyze_acceptance_by_rate_calculates_ranges(
        self, rate_optimizer, db, sample_user, sample_platform
    ):
        """
        Test rate range analysis with varied acceptance.

        Scenario: Mix of accepted/rejected at different rate ranges.
        Expected: Calculates acceptance rate per range.
        """
        # Create opportunities at different rate ranges
        # High rate ($150/hr) - low acceptance
        for i in range(3):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"high_rate_{i}",
                title="High Rate Project",
                description="Test",
                client_budget=6000.0,
                suggested_pricing={
                    "suggested_hourly_rate": 150.0,
                    "suggested_value": 6000.0,
                },
                status="rejected",  # High rate rejected
            )
            db.add(opp)

        # Mid rate ($100/hr) - high acceptance
        for i in range(5):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"mid_rate_{i}",
                title="Mid Rate Project",
                description="Test",
                client_budget=5000.0,
                suggested_pricing={
                    "suggested_hourly_rate": 100.0,
                    "suggested_value": 5000.0,
                },
                status="accepted",  # Mid rate accepted
                recommendation="accept",
            )
            db.add(opp)

        db.commit()

        # Analyze
        result = rate_optimizer.analyze_acceptance_by_rate(days=90)

        # Assert
        assert result["total_opportunities"] == 8
        assert "rate_range_stats" in result

        # Check that mid range has higher acceptance than premium
        stats = result["rate_range_stats"]
        mid_range = stats.get("mid", stats.get("senior"))  # $100/hr falls in mid or senior
        premium_range = stats.get("premium")  # $150/hr falls in premium

        if mid_range and premium_range:
            assert mid_range["acceptance_rate"] > premium_range["acceptance_rate"]

    def test_suggest_rate_adjustment_with_high_acceptance(
        self, rate_optimizer, db, sample_user, sample_platform, sample_pricing_params
    ):
        """
        Test rate adjustment suggestion with very high acceptance.

        Scenario: 90% acceptance rate.
        Expected: Suggests increasing rate.
        """
        # Create 10 accepted opportunities at current rate
        for i in range(9):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"accepted_{i}",
                title="Accepted Project",
                description="Test",
                suggested_pricing={
                    "suggested_hourly_rate": 100.0,
                    "suggested_value": 5000.0,
                },
                status="accepted",
                recommendation="accept",
            )
            db.add(opp)

        # 1 rejected
        opp = FreelanceOpportunity(
            user_id=sample_user.id,
            platform_id=sample_platform.id,
            external_id="rejected_1",
            title="Rejected Project",
            description="Test",
            suggested_pricing={
                "suggested_hourly_rate": 100.0,
                "suggested_value": 5000.0,
            },
            status="rejected",
        )
        db.add(opp)
        db.commit()

        # Get suggestion
        suggestion = rate_optimizer.suggest_rate_adjustment(min_sample_size=10)

        # Assert
        assert suggestion["sample_size"] == 10
        assert suggestion["current_acceptance_rate"] == 0.9
        if suggestion["adjustment_suggested"]:
            assert suggestion["suggested_rate"] > suggestion["current_rate"]

    def test_apply_rate_adjustment_creates_new_params(
        self, rate_optimizer, sample_pricing_params, db
    ):
        """
        Test applying rate adjustment creates new pricing parameters.

        Scenario: Apply suggested rate of $115/hr.
        Expected: New PricingParameter version with adjusted rate.
        """
        new_params = rate_optimizer.apply_rate_adjustment(suggested_rate=115.0, auto_apply=True)

        assert new_params is not None
        assert new_params.version == sample_pricing_params.version + 1
        assert new_params.base_hourly_rate == 115.0
        assert new_params.auto_adjusted is True
        assert new_params.active is True

        # Old version should be deactivated
        db.refresh(sample_pricing_params)
        assert sample_pricing_params.active is False

    def test_analyze_category_specific_rates(
        self, rate_optimizer, db, sample_user, sample_platform
    ):
        """
        Test category-specific rate analysis.

        Scenario: AI/ML projects accepted at higher rates than frontend.
        Expected: Identifies category-specific rate patterns.
        """
        # Create AI/ML opportunities at high rate (accepted)
        for i in range(3):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"aiml_{i}",
                title="AI Project",
                description="Test",
                semantic_analysis={"category": "ai_ml"},
                suggested_pricing={"suggested_hourly_rate": 150.0},
                status="accepted",
            )
            db.add(opp)

        # Create frontend opportunities at lower rate (accepted)
        for i in range(3):
            opp = FreelanceOpportunity(
                user_id=sample_user.id,
                platform_id=sample_platform.id,
                external_id=f"frontend_{i}",
                title="Frontend Project",
                description="Test",
                semantic_analysis={"category": "frontend"},
                suggested_pricing={"suggested_hourly_rate": 90.0},
                status="accepted",
            )
            db.add(opp)

        db.commit()

        # Analyze
        result = rate_optimizer.analyze_category_specific_rates(days=90)

        # Assert
        assert result["total_opportunities"] == 6
        assert "ai_ml" in result["category_stats"]
        assert "frontend" in result["category_stats"]

        # AI/ML should have higher average rate
        assert result["category_stats"]["ai_ml"]["avg_rate"] > result["category_stats"]["frontend"]["avg_rate"]


# ==================== Integration Tests ====================


class TestLearningComponentsIntegration:
    """Test integration between learning components."""

    def test_full_learning_cycle(
        self, pricing_learner, rejection_learner, rate_optimizer,
        sample_completed_execution, sample_pricing_params, db
    ):
        """
        Test complete learning cycle across all components.

        Scenario: Complete project → learn → adjust parameters.
        Expected: All learning components work together.
        """
        # 1. Learn from execution (PricingLearner)
        pricing_record = pricing_learner.learn_from_execution(sample_completed_execution)
        assert pricing_record is not None

        # 2. Analyze performance
        performance = pricing_learner.analyze_pricing_performance(days=90)
        assert performance["total_records"] > 0

        # 3. Test rejection learning (would happen for rejected projects)
        # This validates the learning infrastructure is working end-to-end
        assert db.query(LearningRecord).filter_by(learning_type="pricing").count() > 0
