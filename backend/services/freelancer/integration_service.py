"""Integration Service for Freelancer MVP Services.

Provides a unified interface to use all MVP critical services together
with the existing agent architecture. This service orchestrates:

- RN09: Project duplication prevention with distributed locking
- RN10: Platform rate limiting (Upwork, Freelancer.com, etc.)
- RN11: Complete financial calculations for Brazilian freelancers
- RN12: Client risk assessment with red/green flags
- RN13: LGPD compliance with PII encryption and data retention

Use this service as the single entry point for processing new freelance
opportunities through all compliance and analysis checks.
"""

import logging
from typing import Any, Optional, TypedDict

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.freelancer.client_risk import ClientRiskAssessment, RiskAssessmentResult
from services.freelancer.duplication_prevention import (
    DuplicateCheckResult,
    ProjectData,
    ProjectDuplicationPrevention,
)
from services.freelancer.financial_calculator import (
    FinancialBreakdown,
    FreelancerFinancialCalculator,
)
from services.freelancer.lgpd_compliance import LGPDCompliance
from services.freelancer.rate_limiter import (
    PlatformRateLimiter,
    create_rate_limiter,
)

logger = logging.getLogger(__name__)


# Pydantic Models for Validation
class OpportunityProcessingInput(BaseModel):
    """Input data for opportunity processing.

    Attributes:
        title: Project title
        description: Project description
        budget: Project budget in USD
        client_name: Client name (PII)
        client_rating: Client rating (0.0-5.0)
        client_projects_count: Number of completed projects by client
        estimated_hours: Estimated hours to complete
        external_id: External platform ID
    """

    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=10000)
    budget: Optional[float] = Field(None, gt=0)
    client_name: Optional[str] = Field(None, max_length=200)
    client_rating: Optional[float] = Field(None, ge=0, le=5)
    client_projects_count: Optional[int] = Field(None, ge=0)
    estimated_hours: Optional[float] = Field(None, gt=0)
    external_id: Optional[str] = Field(None, max_length=100)


# TypedDicts for Return Types
class FinalRecommendation(TypedDict, total=False):
    """Final recommendation after all checks.

    Attributes:
        decision: Decision code (accept, reject, negotiate, accept_with_caution)
        reason: Human-readable reason
        confidence: Confidence level (high, medium, low)
        details: Additional details
    """

    decision: str
    reason: str
    confidence: str
    details: Optional[str]


class OpportunityProcessingResult(TypedDict, total=False):
    """Complete opportunity processing result.

    Attributes:
        original_data: Original opportunity data
        checks_passed: List of passed check names
        checks_failed: List of failed check names
        warnings: List of warning messages
        duplicate_info: Duplicate detection result
        encrypted_pii: Whether PII was encrypted
        financial_analysis: Financial breakdown
        risk_assessment: Risk assessment result
        final_recommendation: Final decision
        error: Error message if processing failed
        recommendation: Quick recommendation (for backwards compatibility)
    """

    original_data: dict[str, Any]
    checks_passed: list[str]
    checks_failed: list[str]
    warnings: list[str]
    duplicate_info: Optional[DuplicateCheckResult]
    encrypted_pii: Optional[bool]
    financial_analysis: Optional[FinancialBreakdown]
    risk_assessment: Optional[RiskAssessmentResult]
    final_recommendation: Optional[FinalRecommendation]
    error: Optional[str]
    recommendation: Optional[str]


class RateLimitInfo(TypedDict):
    """Rate limit status information.

    Attributes:
        platform: Platform name
        remaining_requests: Number of remaining requests
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        reset_time: When the window resets (timestamp)
    """

    platform: str
    remaining_requests: int
    max_requests: int
    window_seconds: int
    reset_time: Optional[float]


class FreelancerIntegrationService:
    """
    Unified service integrating all MVP critical requirements.

    This service coordinates all five MVP requirements (RN09-RN13) and provides
    a single interface for processing freelance opportunities. It ensures:

    1. No duplicate processing (RN09)
    2. Rate limit compliance (RN10)
    3. Financial transparency (RN11)
    4. Client risk awareness (RN12)
    5. LGPD compliance (RN13)

    The typical workflow is:
    1. Check rate limits before fetching opportunities
    2. Process each new opportunity through all checks
    3. Get enriched data with risk scores, financial analysis, and recommendations
    4. Store with encrypted PII and proper data retention settings

    Attributes:
        db: SQLAlchemy database session
        redis: Redis client for locking and caching
        duplication: Duplication prevention service
        financial: Financial calculator service
        risk_assessment: Client risk assessment service
        lgpd: LGPD compliance service

    Examples:
        >>> from database.session import get_db
        >>> from redis import Redis
        >>> db = next(get_db())
        >>> redis = Redis()
        >>> service = FreelancerIntegrationService(db, redis)
        >>> # Process new opportunity
        >>> opp_data = {
        ...     "title": "Django REST API",
        ...     "description": "Build REST API with auth...",
        ...     "budget": 3000,
        ...     "client_name": "John Doe",
        ...     "client_rating": 4.8,
        ...     "client_projects_count": 25
        ... }
        >>> result = service.process_new_opportunity(
        ...     opp_data,
        ...     user_id=1,
        ...     platform="upwork",
        ...     tax_regime="Simples_Nacional"
        ... )
        >>> print(f"Decision: {result['final_recommendation']['decision']}")
        >>> print(f"Net value: R$ {result['financial_analysis']['net_brl']:.2f}")
        >>> print(f"Risk score: {result['risk_assessment']['risk_score']}/100")
    """

    def __init__(
        self,
        db: Session,
        redis_client: Any,
        encryption_key: Optional[str] = None,
    ) -> None:
        """
        Initialize integration service with all sub-services.

        Args:
            db: SQLAlchemy database session
            redis_client: Redis client for locking and rate limiting
            encryption_key: Optional encryption key for LGPD compliance
                          (reads from env if not provided)

        Raises:
            ValueError: If encryption_key not provided and ENCRYPTION_KEY env var not set

        Examples:
            >>> from database.session import get_db
            >>> from redis import Redis
            >>> db = next(get_db())
            >>> redis = Redis(host='localhost', port=6379)
            >>> service = FreelancerIntegrationService(db, redis)
        """
        self.db = db
        self.redis = redis_client

        # Initialize all MVP services
        self.duplication = ProjectDuplicationPrevention(db, redis_client)
        self.financial = FreelancerFinancialCalculator(redis_client)
        self.risk_assessment = ClientRiskAssessment()
        self.lgpd = LGPDCompliance(db, encryption_key)

        # Rate limiters cache (created on-demand per platform)
        self._rate_limiters: dict[str, PlatformRateLimiter] = {}

        logger.info(
            "Initialized FreelancerIntegrationService",
            extra={
                "has_redis": redis_client is not None,
                "has_encryption": encryption_key is not None,
            },
        )

    def get_rate_limiter(self, platform: str) -> PlatformRateLimiter:
        """
        Get or create rate limiter for a platform.

        Rate limiters are cached per platform for efficiency.

        Args:
            platform: Platform name (upwork, freelancer, fiverr, etc.)

        Returns:
            Platform-specific rate limiter instance

        Examples:
            >>> service = FreelancerIntegrationService(db, redis)
            >>> limiter = service.get_rate_limiter("upwork")
            >>> if limiter.can_make_request(user_id=1):
            ...     # Make API request
            ...     pass
        """
        if platform not in self._rate_limiters:
            self._rate_limiters[platform] = create_rate_limiter(self.redis, platform)
            logger.debug("Created rate limiter for platform", extra={"platform": platform})

        return self._rate_limiters[platform]

    def process_new_opportunity(
        self,
        opportunity_data: dict[str, Any],
        user_id: int,
        platform: str = "upwork",
        tax_regime: str = "Simples_Nacional",
    ) -> OpportunityProcessingResult:
        """
        Process a new opportunity through all MVP checks.

        This is the main integration point that runs all five MVP requirements
        in sequence:

        1. **Duplication Check (RN09)**: Prevents re-analyzing same project
        2. **PII Encryption (RN13)**: Encrypts client names per LGPD
        3. **Financial Analysis (RN11)**: Calculates net value after all fees
        4. **Risk Assessment (RN12)**: Scores client risk with red/green flags
        5. **Final Recommendation**: Combines all analyses for decision

        Args:
            opportunity_data: Raw opportunity data from platform scraper
            user_id: User ID for multi-tenancy isolation
            platform: Platform name (upwork, freelancer, fiverr)
            tax_regime: User's Brazilian tax regime (Simples_Nacional, MEI, etc.)

        Returns:
            Complete analysis result with all checks and recommendations

        Raises:
            No exceptions raised - returns error in result dict on failure

        Examples:
            >>> service = FreelancerIntegrationService(db, redis)
            >>> opp_data = {
            ...     "title": "Build Django app",
            ...     "description": "Need full-stack Django developer...",
            ...     "budget": 5000,
            ...     "client_name": "Acme Corp",
            ...     "client_rating": 4.9,
            ...     "client_projects_count": 50
            ... }
            >>> result = service.process_new_opportunity(
            ...     opp_data, user_id=1, platform="upwork"
            ... )
            >>> if result['final_recommendation']['decision'] == 'accept':
            ...     print("Safe to accept!")
            ...     print(f"Net: R$ {result['financial_analysis']['net_brl']}")
        """
        try:
            result: OpportunityProcessingResult = {
                "original_data": opportunity_data,
                "checks_passed": [],
                "checks_failed": [],
                "warnings": [],
            }

            # Step 1: Check for duplicates (RN09)
            logger.debug(
                "Running duplicate check",
                extra={"user_id": user_id, "title": opportunity_data.get("title")},
            )

            # Convert to ProjectData for validation
            project_data = ProjectData(
                title=opportunity_data.get("title", ""),
                description=opportunity_data.get("description"),
                client_name=opportunity_data.get("client_name"),
                budget=opportunity_data.get("budget"),
                external_id=opportunity_data.get("external_id"),
            )

            duplicate_check = self.duplication.detect_duplicate(project_data, user_id)

            if duplicate_check.get("is_duplicate"):
                result["checks_failed"].append("duplicate_detection")
                result["duplicate_info"] = duplicate_check
                result["recommendation"] = "reject_duplicate"
                result["final_recommendation"] = FinalRecommendation(
                    decision="reject",
                    reason="Duplicate project detected",
                    confidence="high",
                    details=duplicate_check.get("reason", ""),
                )
                logger.info(
                    "Duplicate detected, rejecting",
                    extra={"user_id": user_id, "original_id": duplicate_check.get("original_id")},
                )
                return result

            result["checks_passed"].append("duplicate_detection")

            # Step 2: Encrypt PII (RN13 - LGPD)
            self.lgpd.encrypt_opportunity_pii(opportunity_data)
            result["encrypted_pii"] = True
            result["checks_passed"].append("lgpd_encryption")
            logger.debug("PII encrypted successfully")

            # Step 3: Calculate financial breakdown (RN11)
            gross_usd = opportunity_data.get("budget")
            if gross_usd:
                try:
                    financial_breakdown = self.financial.calculate_net_value(
                        gross_usd=gross_usd,
                        platform=platform,
                        tax_regime=tax_regime,
                    )
                    result["financial_analysis"] = financial_breakdown
                    result["checks_passed"].append("financial_calculation")

                    # Add warning if effective loss is too high (> 40%)
                    if financial_breakdown["effective_loss_rate"] > 0.40:
                        result["warnings"].append(
                            f"High effective loss rate: {financial_breakdown['effective_loss_rate']*100:.1f}%"
                        )
                        logger.warning(
                            "High loss rate detected",
                            extra={"loss_rate": financial_breakdown["effective_loss_rate"]},
                        )

                except Exception as e:
                    logger.error(
                        "Financial calculation failed",
                        extra={"error_type": type(e).__name__, "error": str(e)},
                        exc_info=True,
                    )
                    result["checks_failed"].append("financial_calculation")
                    result["financial_analysis"] = {"error": str(e)}
            else:
                result["warnings"].append("No budget specified - cannot calculate financials")

            # Step 4: Assess client risk (RN12)
            try:
                # Estimate fair value for risk assessment
                # Use 120% of stated budget as baseline fair value
                fair_value = (gross_usd * 1.2) if gross_usd else None

                risk_assessment = self.risk_assessment.score_project(
                    project=opportunity_data,
                    fair_value_usd=fair_value,
                    estimated_hours=opportunity_data.get("estimated_hours"),
                )

                result["risk_assessment"] = risk_assessment
                result["checks_passed"].append("risk_assessment")

                # Add warnings for high-risk projects
                if risk_assessment["risk_level"] in ["high", "critical"]:
                    result["warnings"].append(
                        f"High-risk client detected (score: {risk_assessment['risk_score']}/100)"
                    )
                    logger.warning(
                        "High-risk client detected",
                        extra={
                            "risk_score": risk_assessment["risk_score"],
                            "risk_level": risk_assessment["risk_level"],
                            "red_flags_count": risk_assessment["red_flags_count"],
                        },
                    )

            except Exception as e:
                logger.error(
                    "Risk assessment failed",
                    extra={"error_type": type(e).__name__, "error": str(e)},
                    exc_info=True,
                )
                result["checks_failed"].append("risk_assessment")
                result["risk_assessment"] = {"error": str(e)}

            # Step 5: Generate final recommendation
            result["final_recommendation"] = self._generate_final_recommendation(result)

            logger.info(
                "Opportunity processing completed",
                extra={
                    "user_id": user_id,
                    "checks_passed_count": len(result["checks_passed"]),
                    "checks_failed_count": len(result["checks_failed"]),
                    "warnings_count": len(result["warnings"]),
                    "final_decision": result["final_recommendation"]["decision"],
                },
            )

            return result

        except Exception as e:
            logger.error(
                "Error processing opportunity",
                extra={"user_id": user_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            return OpportunityProcessingResult(
                original_data=opportunity_data,
                error=str(e),
                checks_passed=[],
                checks_failed=["processing_error"],
                warnings=[],
            )

    def _generate_final_recommendation(
        self, analysis_result: OpportunityProcessingResult
    ) -> FinalRecommendation:
        """
        Generate final recommendation based on all analyses.

        Combines duplication, risk, and financial data to make a final decision:
        - **reject**: Duplicate or critical risk
        - **negotiate**: High risk or low margins
        - **accept**: Low risk and good margins
        - **accept_with_caution**: Medium risk/margins, monitor during execution

        Args:
            analysis_result: Combined analysis result from process_new_opportunity

        Returns:
            Final recommendation with decision code and reasoning

        Examples:
            >>> # Called internally by process_new_opportunity()
            >>> result = {...}  # Analysis result
            >>> recommendation = service._generate_final_recommendation(result)
            >>> if recommendation['decision'] == 'reject':
            ...     print(recommendation['reason'])
        """
        # If duplicate, reject immediately
        if "duplicate_detection" in analysis_result.get("checks_failed", []):
            return FinalRecommendation(
                decision="reject",
                reason="Duplicate project detected",
                confidence="high",
            )

        # Check risk assessment
        risk_data = analysis_result.get("risk_assessment", {})
        risk_level = risk_data.get("risk_level", "medium")
        risk_recommendation = risk_data.get("recommendation", "accept_with_protection")

        # Check financial viability
        financial_data = analysis_result.get("financial_analysis", {})
        effective_loss = financial_data.get("effective_loss_rate", 0.35)

        # Decision logic
        if risk_level == "critical" or risk_recommendation == "reject_high_risk":
            return FinalRecommendation(
                decision="reject",
                reason="High-risk client detected",
                confidence="high",
                details=risk_data.get("recommendation_reason", ""),
            )

        elif risk_level == "high" or effective_loss > 0.45:
            return FinalRecommendation(
                decision="negotiate",
                reason="Project requires negotiation (risk or low margin)",
                confidence="medium",
                details=f"Risk: {risk_level}, Loss rate: {effective_loss*100:.1f}%",
            )

        elif risk_level == "low" and effective_loss < 0.35:
            return FinalRecommendation(
                decision="accept",
                reason="Safe project with good financial viability",
                confidence="high",
                details=f"Risk score: {risk_data.get('risk_score', 0)}/100",
            )

        else:
            return FinalRecommendation(
                decision="accept_with_caution",
                reason="Acceptable project, requires monitoring",
                confidence="medium",
                details="Requires attention during execution",
            )

    # Convenience Methods (delegate to sub-services)

    def acquire_processing_lock(self, opportunity_id: int, timeout: int = 300) -> Optional[str]:
        """
        Acquire distributed processing lock for an opportunity.

        Delegates to duplication prevention service (RN09).

        Args:
            opportunity_id: Opportunity ID
            timeout: Lock timeout in seconds (default 5 minutes)

        Returns:
            Lock token if acquired, None if lock is already held

        Examples:
            >>> service = FreelancerIntegrationService(db, redis)
            >>> lock_token = service.acquire_processing_lock(opp_id=123)
            >>> if lock_token:
            ...     try:
            ...         # Process opportunity
            ...         pass
            ...     finally:
            ...         service.release_processing_lock(123, lock_token)
        """
        return self.duplication.acquire_processing_lock(opportunity_id, timeout)

    def release_processing_lock(self, opportunity_id: int, lock_token: str) -> bool:
        """
        Release distributed processing lock.

        Args:
            opportunity_id: Opportunity ID
            lock_token: Lock token from acquire_processing_lock

        Returns:
            True if released successfully, False otherwise

        Examples:
            >>> service.release_processing_lock(123, lock_token)
        """
        return self.duplication.release_processing_lock(opportunity_id, lock_token)

    def check_rate_limit(self, platform: str, user_id: Optional[int] = None) -> bool:
        """
        Check if API request can be made without exceeding rate limit.

        Delegates to platform rate limiter (RN10).

        Args:
            platform: Platform name (upwork, freelancer, etc.)
            user_id: Optional user ID for per-user limits

        Returns:
            True if request is allowed

        Raises:
            RateLimitExceeded: If rate limit would be exceeded

        Examples:
            >>> service = FreelancerIntegrationService(db, redis)
            >>> if service.check_rate_limit("upwork", user_id=1):
            ...     # Make API request
            ...     fetch_opportunities()
        """
        rate_limiter = self.get_rate_limiter(platform)
        return rate_limiter.can_make_request(user_id)

    def get_rate_limit_status(self, platform: str, user_id: Optional[int] = None) -> RateLimitInfo:
        """
        Get current rate limit status for a platform.

        Args:
            platform: Platform name
            user_id: Optional user ID

        Returns:
            Rate limit status information

        Examples:
            >>> service = FreelancerIntegrationService(db, redis)
            >>> status = service.get_rate_limit_status("upwork", user_id=1)
            >>> print(f"Remaining: {status['remaining_requests']}")
            >>> print(f"Resets at: {status['reset_time']}")
        """
        rate_limiter = self.get_rate_limiter(platform)
        status = rate_limiter.get_status(user_id)

        return RateLimitInfo(
            platform=platform,
            remaining_requests=status["remaining"],
            max_requests=status["max_requests"],
            window_seconds=status["window_seconds"],
            reset_time=status.get("reset_time"),
        )


def create_integration_service(
    db: Session,
    redis_client: Any,
    encryption_key: Optional[str] = None,
) -> FreelancerIntegrationService:
    """
    Factory function to create integration service.

    Convenience function for dependency injection patterns.

    Args:
        db: SQLAlchemy database session
        redis_client: Redis client
        encryption_key: Optional encryption key for LGPD

    Returns:
        Configured FreelancerIntegrationService instance

    Examples:
        >>> from database.session import get_db
        >>> from redis import Redis
        >>> db = next(get_db())
        >>> redis = Redis()
        >>> service = create_integration_service(db, redis)
    """
    return FreelancerIntegrationService(db, redis_client, encryption_key)
