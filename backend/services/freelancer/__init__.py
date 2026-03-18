"""Freelancer Services Module - MVP Critical Requirements + Learning Components.

This module implements the critical MVP requirements for the freelancer
management system as documented in docs/modulos-planejados/gestao-projetos-freelancers.md

Implemented Requirements:
- RN09: Project Duplication Prevention
- RN10: Rate Limiting for External APIs
- RN11: Complete Financial Calculator (Brazilian taxes)
- RN12: Client Risk Assessment
- RN13: LGPD Compliance (PII encryption & data retention)

Learning Components (Continuous Improvement):
- PricingLearner: Adaptive pricing parameter optimization
- RejectionPatternLearner: Red flag pattern detection and optimization
- HourlyRateOptimizer: Dynamic hourly rate optimization based on acceptance
"""

from services.freelancer.client_risk import ClientRiskAssessment
from services.freelancer.duplication_prevention import ProjectDuplicationPrevention
from services.freelancer.financial_calculator import (
    FreelancerFinancialCalculator,
    Platform,
    TaxRegime,
)
from services.freelancer.hourly_rate_optimizer import HourlyRateOptimizer
from services.freelancer.integration_service import (
    FreelancerIntegrationService,
    create_integration_service,
)
from services.freelancer.lgpd_compliance import (
    LGPDCompliance,
    LGPDDataRetention,
    PIIEncryption,
)
from services.freelancer.pricing_learner import PricingLearner
from services.freelancer.rate_limiter import (
    FreelancerRateLimiter,
    PlatformRateLimiter,
    RateLimitExceeded,
    RetryWithBackoff,
    UpworkRateLimiter,
    create_rate_limiter,
)
from services.freelancer.rejection_pattern_learner import RejectionPatternLearner

__all__ = [
    # RN09: Duplication Prevention
    "ProjectDuplicationPrevention",
    # RN10: Rate Limiting
    "PlatformRateLimiter",
    "UpworkRateLimiter",
    "FreelancerRateLimiter",
    "RateLimitExceeded",
    "RetryWithBackoff",
    "create_rate_limiter",
    # RN11: Financial Calculator
    "FreelancerFinancialCalculator",
    "Platform",
    "TaxRegime",
    # RN12: Client Risk
    "ClientRiskAssessment",
    # RN13: LGPD Compliance
    "LGPDCompliance",
    "PIIEncryption",
    "LGPDDataRetention",
    # Integration Service
    "FreelancerIntegrationService",
    "create_integration_service",
    # Learning Components
    "PricingLearner",
    "RejectionPatternLearner",
    "HourlyRateOptimizer",
]
