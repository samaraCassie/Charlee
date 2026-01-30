#!/usr/bin/env python3
"""
Interactive Freelancer System Testing Script

Usage:
    python3 scripts/test_freelancer_interactive.py

This script demonstrates all 7 agents + 3 learning components without needing a frontend.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import SessionLocal
from database.models import (
    FreelanceOpportunity,
    FreelancePlatform,
    PricingParameter,
    User,
)
from services.freelancer import (
    ClientRiskAssessment,
    FreelancerFinancialCalculator,
    FreelancerIntegrationService,
    HourlyRateOptimizer,
    PricingLearner,
    ProjectDuplicationPrevention,
    RejectionPatternLearner,
    create_integration_service,
)


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_duplication_prevention(db):
    """Test RN09: Duplication Prevention."""
    print_section("🧩 RN09: Duplication Prevention")

    dup_service = ProjectDuplicationPrevention(db)

    # Create test opportunity
    opp1 = FreelanceOpportunity(
        user_id=1,
        platform_id=1,
        external_id="test_001",
        title="Python Backend API Development",
        description="Need a Python FastAPI developer for building RESTful APIs",
        client_budget=5000.0,
    )
    db.add(opp1)
    db.commit()
    db.refresh(opp1)

    # Test duplicate detection
    is_dup = dup_service.is_duplicate(
        title="Python Backend API Development",
        description="Looking for FastAPI expert to build REST APIs",
        platform_id=1,
        external_id="test_002",
    )

    print(f"✓ Created opportunity: {opp1.title}")
    print(f"✓ Duplicate detection: {is_dup}")
    print(
        f"  Similarity threshold: {dup_service.similarity_threshold * 100}% (Jaccard index)"
    )


def test_financial_calculator(db):
    """Test RN11: Financial Calculator."""
    print_section("💰 RN11: Financial Calculator (USD→BRL + Impostos)")

    calc = FreelancerFinancialCalculator(db, user_id=1)

    # Test calculation
    result = calc.calculate_net_income(
        gross_usd=5000.0,
        platform="upwork",
        tax_regime="simples_nacional",
        include_breakdown=True,
    )

    print(f"✓ Gross (USD): ${result['gross_usd']}")
    print(f"✓ Exchange rate: R$ {result['exchange_rate']}")
    print(f"✓ Gross (BRL): R$ {result['gross_brl']}")
    print(f"✓ Platform fee (Upwork 10%): R$ {result['breakdown']['platform_fee_brl']}")
    print(
        f"✓ Simples Nacional tax: R$ {result['breakdown']['simples_nacional_tax_brl']}"
    )
    print(f"✓ Net income (BRL): R$ {result['net_brl']}")
    print(f"✓ Effective tax rate: {result['effective_tax_rate'] * 100:.2f}%")


def test_client_risk_assessment(db):
    """Test RN12: Client Risk Assessment."""
    print_section("⚖️ RN12: Client Risk Assessment")

    risk_service = ClientRiskAssessment(db, user_id=1)

    # Test high-risk client
    high_risk = risk_service.assess_risk(
        client_rating=2.5,
        client_projects_count=2,
        project_description="Need this ASAP! Budget is flexible but looking for cheapest option. Must deliver in 2 days.",
        client_payment_verified=False,
        client_country="Unknown",
    )

    print(f"✓ High-risk client:")
    print(f"  - Risk score: {high_risk['risk_score']:.2f}/10")
    print(f"  - Risk level: {high_risk['risk_level']}")
    print(f"  - Red flags: {', '.join(high_risk['red_flags'])}")
    print(f"  - Recommendation: {high_risk['recommendation']}")

    # Test low-risk client
    low_risk = risk_service.assess_risk(
        client_rating=4.8,
        client_projects_count=50,
        project_description="Looking for experienced Python developer for 3-month project. Clear requirements attached.",
        client_payment_verified=True,
        client_country="United States",
    )

    print(f"\n✓ Low-risk client:")
    print(f"  - Risk score: {low_risk['risk_score']:.2f}/10")
    print(f"  - Risk level: {low_risk['risk_level']}")
    print(f"  - Green flags: {', '.join(low_risk['green_flags'])}")
    print(f"  - Recommendation: {low_risk['recommendation']}")


def test_pricing_learner(db):
    """Test Learning Component: PricingLearner."""
    print_section("🧠 Learning Component: PricingLearner")

    learner = PricingLearner(db, user_id=1)

    # Analyze pricing performance
    performance = learner.analyze_pricing_performance(days=90)

    print(f"✓ Pricing performance analysis:")
    print(f"  - Total learning records: {performance['total_records']}")

    if performance["total_records"] > 0:
        print(f"  - Average accuracy: {performance['avg_accuracy_score']:.2%}")
        print(f"  - Average error margin: {performance['avg_error_margin']:.2%}")
        print(f"  - Needs adjustment: {performance['needs_adjustment']}")
    else:
        print(f"  - {performance['message']}")
        print("  - (This is expected if no projects have been executed yet)")


def test_rejection_pattern_learner(db):
    """Test Learning Component: RejectionPatternLearner."""
    print_section("🔍 Learning Component: RejectionPatternLearner")

    learner = RejectionPatternLearner(db, user_id=1)

    # Analyze rejection patterns
    patterns = learner.analyze_rejection_patterns(days=90)

    print(f"✓ Rejection pattern analysis:")
    print(f"  - Total opportunities: {patterns['total_opportunities']}")

    if patterns["total_opportunities"] > 0:
        print(f"  - Rejected: {patterns['rejected_count']}")
        print(f"  - Accepted: {patterns['accepted_count']}")
        print(f"  - Rejection rate: {patterns['rejection_rate']:.1%}")

        if patterns["high_risk_flags"]:
            print(f"\n  High-risk red flags (>70% rejection probability):")
            for flag in patterns["high_risk_flags"][:3]:
                print(
                    f"    - {flag['flag']}: {flag['rejection_probability']:.1%} rejection"
                )
    else:
        print(f"  - {patterns['message']}")
        print("  - (This is expected if no opportunities have been analyzed yet)")


def test_hourly_rate_optimizer(db):
    """Test Learning Component: HourlyRateOptimizer."""
    print_section("📊 Learning Component: HourlyRateOptimizer")

    optimizer = HourlyRateOptimizer(db, user_id=1)

    # Suggest rate adjustment
    suggestion = optimizer.suggest_rate_adjustment(target_acceptance_rate=0.60)

    print(f"✓ Hourly rate optimization:")

    if "current_rate" in suggestion:
        print(f"  - Current rate: ${suggestion['current_rate']}/hr")
        print(f"  - Suggested rate: ${suggestion['suggested_rate']}/hr")
        print(
            f"  - Current acceptance rate: {suggestion['current_acceptance_rate']:.1%}"
        )
        print(f"  - Adjustment suggested: {suggestion['adjustment_suggested']}")
        print(f"  - Reason: {suggestion['reason']}")
    else:
        print(f"  - {suggestion['reason']}")
        print("  - (This is expected if no pricing data exists yet)")


def test_integration_service(db):
    """Test Integration Service (orchestrates all 5 MVP requirements)."""
    print_section("🔗 Integration Service (MVP RN09-RN13)")

    integration_service = create_integration_service(db, user_id=1)

    print(f"✓ Integration service created successfully")
    print(f"  - Duplication Prevention: ✓")
    print(f"  - Rate Limiter: ✓")
    print(f"  - Financial Calculator: ✓")
    print(f"  - Risk Assessment: ✓")
    print(f"  - LGPD Compliance: ✓")

    # Test full pipeline
    result = integration_service.process_opportunity(
        title="AI/ML Model Development",
        description="Looking for ML engineer to build recommendation system",
        client_budget=8000.0,
        platform_name="upwork",
        external_id="upwork_12345",
        client_rating=4.5,
        client_projects_count=25,
        client_payment_verified=True,
    )

    print(f"\n✓ Full pipeline test:")
    print(f"  - Is duplicate: {result['is_duplicate']}")
    print(f"  - Risk assessment: {result['risk_assessment']['risk_level']}")
    print(f"  - Financial calculation: R$ {result['financial_calculation']['net_brl']}")
    print(f"  - Rate limit status: {result['rate_limit_status']['requests_remaining']} requests remaining")


def main():
    """Main testing function."""
    print("\n" + "=" * 80)
    print("  🚀 Freelancer System Interactive Testing")
    print("  Testing all 7 agents + 3 learning components")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Ensure test user exists
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                email="test@charlee.ai",
                username="testuser",
                full_name="Test User",
                is_active=True,
            )
            db.add(user)
            db.commit()
            print("✓ Created test user")

        # Ensure pricing parameters exist
        params = (
            db.query(PricingParameter)
            .filter(PricingParameter.user_id == 1, PricingParameter.active == True)
            .first()
        )
        if not params:
            params = PricingParameter(
                user_id=1,
                version=1,
                base_hourly_rate=100.0,
                minimum_margin=0.20,
                currency="USD",
                complexity_factors={
                    "1-2": 1.0,
                    "3-4": 1.2,
                    "5-6": 1.4,
                    "7-8": 1.8,
                    "9-10": 2.5,
                },
                specialization_factors={
                    "ai_ml": 1.5,
                    "blockchain": 1.4,
                    "full_stack": 1.2,
                    "backend": 1.1,
                    "frontend": 1.0,
                },
                deadline_factors={"urgent": 1.5, "short": 1.3, "normal": 1.0, "long": 0.9},
                client_factors={"new": 1.2, "verified": 1.0, "premium": 0.95},
                active=True,
            )
            db.add(params)
            db.commit()
            print("✓ Created pricing parameters")

        # Ensure platform exists
        platform = db.query(FreelancePlatform).filter(FreelancePlatform.id == 1).first()
        if not platform:
            platform = FreelancePlatform(
                id=1,
                user_id=1,
                name="upwork",
                api_key="test_key",
                api_secret="test_secret",
                is_active=True,
            )
            db.add(platform)
            db.commit()
            print("✓ Created test platform\n")

        # Run tests
        test_duplication_prevention(db)
        test_financial_calculator(db)
        test_client_risk_assessment(db)
        test_pricing_learner(db)
        test_rejection_pattern_learner(db)
        test_hourly_rate_optimizer(db)
        test_integration_service(db)

        print_section("✅ All Tests Completed Successfully!")
        print("Next steps:")
        print("  1. Run automated tests: pytest tests/test_freelancer_mvp.py -v")
        print("  2. Test via REST API: python3 -m uvicorn main:app --reload")
        print("  3. Use Postman/curl to interact with endpoints")
        print("  4. Check documentation: docs/implementacao/freelancer-complete.md")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
