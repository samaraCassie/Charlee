"""RN12: Client Risk Assessment Service.

Identifies problematic clients before accepting projects using:
- Red flag detection (vague requirements, low budget, payment issues, etc.)
- Green flag detection (detailed specs, experienced clients, fair compensation)
- Client history scoring based on platform data
- Comprehensive risk score calculation (0-100, higher = safer)
- Accept/reject/conditional recommendations with specific protections

This service helps freelancers avoid problematic clients that waste time,
don't pay, or create scope creep situations.
"""

import logging
from typing import Any, List, Optional, TypedDict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Pydantic Models for Validation
class ProjectRiskInput(BaseModel):
    """Project data for risk assessment.

    Attributes:
        title: Project title
        description: Project description
        client_budget: Client's stated budget in USD
        client_rating: Client rating (0.0-5.0)
        client_projects_count: Number of completed projects by client
        client_deadline_days: Client's requested deadline in days
        budget: Alternative budget field name
    """

    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = Field(None, max_length=10000)
    client_budget: Optional[float] = Field(None, gt=0)
    client_rating: Optional[float] = Field(None, ge=0, le=5)
    client_projects_count: Optional[int] = Field(None, ge=0)
    client_deadline_days: Optional[int] = Field(None, gt=0)
    budget: Optional[float] = Field(None, gt=0)  # Alternative budget field


# TypedDicts for Return Types
class FlagDetail(TypedDict, total=False):
    """Details about a detected flag (red or green).

    Attributes:
        type: Flag type identifier
        name: Human-readable flag name
        weight: Score adjustment weight
        severity: Severity level (critical, high, medium, low) - for red flags only
        details: Detailed explanation with specific findings
    """

    type: str
    name: str
    weight: int
    severity: Optional[str]
    details: str


class RecommendationDetail(TypedDict):
    """Recommendation decision and reasoning.

    Attributes:
        decision: Decision code (safe_to_accept, accept_with_protection, reject_high_risk)
        reason: Human-readable explanation of the decision
    """

    decision: str
    reason: str


class RiskAssessmentResult(TypedDict):
    """Complete risk assessment result.

    Attributes:
        risk_score: Numeric risk score (0-100, higher = safer)
        risk_level: Risk level category (low, medium, high, critical)
        recommendation: Decision code
        recommendation_reason: Explanation for the recommendation
        red_flags: List of detected red flags
        green_flags: List of detected green flags
        red_flags_count: Number of red flags found
        green_flags_count: Number of green flags found
    """

    risk_score: float
    risk_level: str
    recommendation: str
    recommendation_reason: str
    red_flags: List[FlagDetail]
    green_flags: List[FlagDetail]
    red_flags_count: int
    green_flags_count: int


class ClientRiskAssessment:
    """
    Evaluates client risk to protect freelancers from problematic projects.

    Analyzes project descriptions, client history, budget, and timeline to
    identify red flags (warning signs) and green flags (positive indicators).
    Provides a comprehensive risk score and actionable recommendations.

    The service uses keyword matching, threshold comparisons, and heuristics
    to evaluate project risk across multiple dimensions:
    - Requirements clarity
    - Budget fairness
    - Payment terms
    - Communication style
    - Client history and reputation
    - Timeline reasonableness

    Attributes:
        RED_FLAGS: Configuration for warning sign detection
        GREEN_FLAGS: Configuration for positive indicator detection

    Examples:
        >>> assessor = ClientRiskAssessment()
        >>> project = {
        ...     "title": "Build website ASAP",
        ...     "description": "Need simple website today",
        ...     "client_budget": 50,
        ...     "client_rating": 2.5,
        ...     "client_projects_count": 0
        ... }
        >>> result = assessor.score_project(project, fair_value_usd=500)
        >>> print(f"Risk score: {result['risk_score']}/100")
        >>> print(f"Decision: {result['recommendation']}")
        >>> for flag in result['red_flags']:
        ...     print(f"⚠️  {flag['name']}: {flag['details']}")
    """

    # Red flags configuration (warning signs)
    RED_FLAGS: dict[str, dict[str, Any]] = {
        "vague_requirements": {
            "name": "Vague Requirements",
            "keywords": [
                "asap",
                "simple",
                "quick",
                "easy",
                "urgent",
                "basic",
                "straightforward",
                "trivial",
            ],
            "weight": -15,
            "severity": "medium",
        },
        "unrealistic_budget": {
            "name": "Unrealistic Budget",
            "threshold": 0.7,  # Less than 70% of fair value
            "weight": -25,
            "severity": "high",
        },
        "no_payment_history": {
            "name": "Client Without History",
            "weight": -10,
            "severity": "low",
        },
        "low_client_rating": {
            "name": "Low Client Rating",
            "threshold": 3.0,
            "weight": -30,
            "severity": "high",
        },
        "unrealistic_deadline": {
            "name": "Impossible Deadline",
            "keywords": ["today", "tomorrow", "hours", "immediately"],
            "weight": -20,
            "severity": "high",
        },
        "free_work_request": {
            "name": "Free Work Request",
            "keywords": [
                "test task",
                "sample",
                "trial",
                "proof",
                "demo",
                "free sample",
                "unpaid test",
            ],
            "weight": -35,
            "severity": "critical",
        },
        "scope_creep_indicators": {
            "name": "Scope Creep Indicators",
            "keywords": [
                "and more",
                "additional features",
                "ongoing changes",
                "flexible requirements",
                "we'll figure out",
            ],
            "weight": -15,
            "severity": "medium",
        },
        "payment_red_flags": {
            "name": "Payment Red Flags",
            "keywords": [
                "pay after launch",
                "revenue share",
                "equity",
                "commission only",
                "pay when profitable",
            ],
            "weight": -40,
            "severity": "critical",
        },
        "communication_red_flags": {
            "name": "Communication Problems",
            "keywords": [
                "don't contact",
                "no questions",
                "just do it",
                "figure it out",
            ],
            "weight": -20,
            "severity": "high",
        },
    }

    # Green flags configuration (positive indicators)
    GREEN_FLAGS: dict[str, dict[str, Any]] = {
        "detailed_requirements": {
            "name": "Detailed Requirements",
            "min_description_words": 100,
            "weight": +10,
        },
        "experienced_client": {
            "name": "Experienced Client",
            "min_projects": 10,
            "weight": +15,
        },
        "excellent_rating": {
            "name": "Excellent Client Rating",
            "min_rating": 4.5,
            "weight": +15,
        },
        "fair_budget": {
            "name": "Fair Budget",
            "min_ratio": 1.0,  # >= fair value
            "weight": +20,
        },
        "realistic_deadline": {
            "name": "Realistic Deadline",
            "buffer_ratio": 1.3,  # 30% time buffer
            "weight": +10,
        },
        "clear_scope": {
            "name": "Well-Defined Scope",
            "keywords": [
                "requirements",
                "specification",
                "documentation",
                "mockups",
                "wireframes",
            ],
            "weight": +10,
        },
    }

    def __init__(self) -> None:
        """
        Initialize risk assessment service.

        Examples:
            >>> assessor = ClientRiskAssessment()
        """
        pass

    def score_project(
        self,
        project: dict[str, Any],
        fair_value_usd: Optional[float] = None,
        estimated_hours: Optional[float] = None,
    ) -> RiskAssessmentResult:
        """
        Calculate comprehensive risk score for a project.

        Evaluates the project across multiple dimensions, detects red and
        green flags, calculates a final risk score, and provides an
        actionable recommendation.

        Args:
            project: Project data dictionary with client info and description
            fair_value_usd: Fair market value in USD (for budget comparison)
            estimated_hours: Estimated hours to complete (for deadline check)

        Returns:
            Complete risk assessment with score, flags, and recommendation

        Raises:
            No exceptions raised - handles missing data gracefully

        Examples:
            >>> assessor = ClientRiskAssessment()
            >>> project = {
            ...     "title": "Django REST API Development",
            ...     "description": "Need to build REST API with detailed specs...",
            ...     "client_budget": 3000,
            ...     "client_rating": 4.8,
            ...     "client_projects_count": 25
            ... }
            >>> result = assessor.score_project(project, fair_value_usd=2500)
            >>> assert result['risk_score'] > 70  # Should be low risk
            >>> assert result['recommendation'] == 'safe_to_accept'
            >>> # High risk example
            >>> bad_project = {
            ...     "title": "Quick website ASAP",
            ...     "description": "Need simple site today, pay after launch",
            ...     "client_budget": 50,
            ...     "client_rating": 2.0,
            ...     "client_projects_count": 0
            ... }
            >>> result = assessor.score_project(bad_project, fair_value_usd=500)
            >>> assert result['risk_score'] < 50  # Should be high risk
        """
        base_score = 70  # Start at 70 (neutral baseline)
        red_flags_detected: List[FlagDetail] = []
        green_flags_detected: List[FlagDetail] = []

        # Step 1: Detect all red flags
        red_flags_detected.extend(self._detect_vague_requirements(project))
        red_flags_detected.extend(self._detect_unrealistic_budget(project, fair_value_usd))
        red_flags_detected.extend(self._detect_no_payment_history(project))
        red_flags_detected.extend(self._detect_low_client_rating(project))
        red_flags_detected.extend(self._detect_unrealistic_deadline(project))
        red_flags_detected.extend(self._detect_free_work_request(project))
        red_flags_detected.extend(self._detect_scope_creep_indicators(project))
        red_flags_detected.extend(self._detect_payment_red_flags(project))
        red_flags_detected.extend(self._detect_communication_red_flags(project))

        # Step 2: Detect all green flags
        green_flags_detected.extend(self._detect_detailed_requirements(project))
        green_flags_detected.extend(self._detect_experienced_client(project))
        green_flags_detected.extend(self._detect_excellent_rating(project))
        green_flags_detected.extend(self._detect_fair_budget(project, fair_value_usd))
        green_flags_detected.extend(self._detect_realistic_deadline(project, estimated_hours))
        green_flags_detected.extend(self._detect_clear_scope(project))

        # Step 3: Calculate final risk score
        risk_score = base_score

        for flag in red_flags_detected:
            risk_score += flag["weight"]  # Negative weights

        for flag in green_flags_detected:
            risk_score += flag["weight"]  # Positive weights

        # Clamp score to valid range [0, 100]
        risk_score = max(0, min(100, risk_score))

        # Step 4: Generate recommendation
        recommendation = self._generate_recommendation(
            risk_score, red_flags_detected, green_flags_detected
        )

        logger.info(
            "Completed risk assessment",
            extra={
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "red_flags_count": len(red_flags_detected),
                "green_flags_count": len(green_flags_detected),
                "recommendation": recommendation["decision"],
            },
        )

        return RiskAssessmentResult(
            risk_score=round(risk_score, 1),
            risk_level=self._get_risk_level(risk_score),
            recommendation=recommendation["decision"],
            recommendation_reason=recommendation["reason"],
            red_flags=red_flags_detected,
            green_flags=green_flags_detected,
            red_flags_count=len(red_flags_detected),
            green_flags_count=len(green_flags_detected),
        )

    # Red Flag Detection Methods

    def _detect_vague_requirements(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect vague requirement indicators.

        Searches for keywords that suggest unclear or poorly defined requirements.

        Args:
            project: Project data dictionary

        Returns:
            List of detected vague requirement flags
        """
        flags: List[FlagDetail] = []
        description = (project.get("description") or "").lower()
        title = (project.get("title") or "").lower()
        combined_text = f"{title} {description}"

        keywords = self.RED_FLAGS["vague_requirements"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in combined_text:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="vague_requirements",
                    name=self.RED_FLAGS["vague_requirements"]["name"],
                    weight=self.RED_FLAGS["vague_requirements"]["weight"],
                    severity=self.RED_FLAGS["vague_requirements"]["severity"],
                    details=f"Vague keywords found: {', '.join(found_keywords)}",
                )
            )

        return flags

    def _detect_unrealistic_budget(
        self, project: dict[str, Any], fair_value: Optional[float]
    ) -> List[FlagDetail]:
        """
        Detect unrealistically low budgets.

        Compares client's budget to fair market value (if provided).

        Args:
            project: Project data dictionary
            fair_value: Fair market value in USD

        Returns:
            List of detected unrealistic budget flags
        """
        flags: List[FlagDetail] = []

        if not fair_value:
            return flags

        client_budget = project.get("client_budget") or project.get("budget")
        if not client_budget:
            return flags

        ratio = client_budget / fair_value
        threshold = self.RED_FLAGS["unrealistic_budget"]["threshold"]

        if ratio < threshold:
            flags.append(
                FlagDetail(
                    type="unrealistic_budget",
                    name=self.RED_FLAGS["unrealistic_budget"]["name"],
                    weight=self.RED_FLAGS["unrealistic_budget"]["weight"],
                    severity=self.RED_FLAGS["unrealistic_budget"]["severity"],
                    details=f"Budget ${client_budget:.0f} is {ratio*100:.0f}% of fair value (${fair_value:.0f})",
                )
            )

        return flags

    def _detect_no_payment_history(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect clients with no payment history.

        New clients without completed projects carry higher risk.

        Args:
            project: Project data dictionary

        Returns:
            List of detected no payment history flags
        """
        flags: List[FlagDetail] = []

        projects_count = project.get("client_projects_count") or 0

        if projects_count == 0:
            flags.append(
                FlagDetail(
                    type="no_payment_history",
                    name=self.RED_FLAGS["no_payment_history"]["name"],
                    weight=self.RED_FLAGS["no_payment_history"]["weight"],
                    severity=self.RED_FLAGS["no_payment_history"]["severity"],
                    details="Client has no completed projects history",
                )
            )

        return flags

    def _detect_low_client_rating(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect clients with low ratings.

        Low ratings indicate past issues with other freelancers.

        Args:
            project: Project data dictionary

        Returns:
            List of detected low client rating flags
        """
        flags: List[FlagDetail] = []

        rating = project.get("client_rating")
        if not rating:
            return flags

        threshold = self.RED_FLAGS["low_client_rating"]["threshold"]

        if rating < threshold:
            flags.append(
                FlagDetail(
                    type="low_client_rating",
                    name=self.RED_FLAGS["low_client_rating"]["name"],
                    weight=self.RED_FLAGS["low_client_rating"]["weight"],
                    severity=self.RED_FLAGS["low_client_rating"]["severity"],
                    details=f"Rating {rating:.1f}/5.0 (below {threshold})",
                )
            )

        return flags

    def _detect_unrealistic_deadline(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect unrealistic deadline requests.

        Searches for extreme urgency keywords in project description.

        Args:
            project: Project data dictionary

        Returns:
            List of detected unrealistic deadline flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        title = (project.get("title") or "").lower()
        combined_text = f"{title} {description}"

        keywords = self.RED_FLAGS["unrealistic_deadline"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in combined_text:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="unrealistic_deadline",
                    name=self.RED_FLAGS["unrealistic_deadline"]["name"],
                    weight=self.RED_FLAGS["unrealistic_deadline"]["weight"],
                    severity=self.RED_FLAGS["unrealistic_deadline"]["severity"],
                    details=f"Extreme urgency detected: {', '.join(found_keywords)}",
                )
            )

        return flags

    def _detect_free_work_request(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect requests for free or unpaid work.

        Identifies attempts to get free work disguised as "tests" or "samples".

        Args:
            project: Project data dictionary

        Returns:
            List of detected free work request flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        keywords = self.RED_FLAGS["free_work_request"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in description:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="free_work_request",
                    name=self.RED_FLAGS["free_work_request"]["name"],
                    weight=self.RED_FLAGS["free_work_request"]["weight"],
                    severity=self.RED_FLAGS["free_work_request"]["severity"],
                    details=f"Unpaid work request detected: {', '.join(found_keywords)}",
                )
            )

        return flags

    def _detect_scope_creep_indicators(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect indicators of potential scope creep.

        Identifies vague scope that could expand indefinitely.

        Args:
            project: Project data dictionary

        Returns:
            List of detected scope creep indicator flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        keywords = self.RED_FLAGS["scope_creep_indicators"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in description:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="scope_creep_indicators",
                    name=self.RED_FLAGS["scope_creep_indicators"]["name"],
                    weight=self.RED_FLAGS["scope_creep_indicators"]["weight"],
                    severity=self.RED_FLAGS["scope_creep_indicators"]["severity"],
                    details=f"Undefined scope detected: {', '.join(found_keywords)}",
                )
            )

        return flags

    def _detect_payment_red_flags(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect payment-related red flags.

        Identifies problematic payment terms like revenue share or deferred payment.

        Args:
            project: Project data dictionary

        Returns:
            List of detected payment red flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        keywords = self.RED_FLAGS["payment_red_flags"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in description:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="payment_red_flags",
                    name=self.RED_FLAGS["payment_red_flags"]["name"],
                    weight=self.RED_FLAGS["payment_red_flags"]["weight"],
                    severity=self.RED_FLAGS["payment_red_flags"]["severity"],
                    details=f"Payment issues detected: {', '.join(found_keywords)}",
                )
            )

        return flags

    def _detect_communication_red_flags(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect communication red flags.

        Identifies hostile or non-collaborative communication patterns.

        Args:
            project: Project data dictionary

        Returns:
            List of detected communication red flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        keywords = self.RED_FLAGS["communication_red_flags"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in description:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="communication_red_flags",
                    name=self.RED_FLAGS["communication_red_flags"]["name"],
                    weight=self.RED_FLAGS["communication_red_flags"]["weight"],
                    severity=self.RED_FLAGS["communication_red_flags"]["severity"],
                    details=f"Communication problems detected: {', '.join(found_keywords)}",
                )
            )

        return flags

    # Green Flag Detection Methods

    def _detect_detailed_requirements(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect detailed requirement descriptions.

        Long descriptions typically indicate well-thought-out projects.

        Args:
            project: Project data dictionary

        Returns:
            List of detected detailed requirements flags
        """
        flags: List[FlagDetail] = []

        description = project.get("description") or ""
        word_count = len(description.split())
        min_words = self.GREEN_FLAGS["detailed_requirements"]["min_description_words"]

        if word_count >= min_words:
            flags.append(
                FlagDetail(
                    type="detailed_requirements",
                    name=self.GREEN_FLAGS["detailed_requirements"]["name"],
                    weight=self.GREEN_FLAGS["detailed_requirements"]["weight"],
                    details=f"Detailed description with {word_count} words",
                )
            )

        return flags

    def _detect_experienced_client(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect experienced clients.

        Clients with many completed projects are typically more professional.

        Args:
            project: Project data dictionary

        Returns:
            List of detected experienced client flags
        """
        flags: List[FlagDetail] = []

        projects_count = project.get("client_projects_count") or 0
        min_projects = self.GREEN_FLAGS["experienced_client"]["min_projects"]

        if projects_count >= min_projects:
            flags.append(
                FlagDetail(
                    type="experienced_client",
                    name=self.GREEN_FLAGS["experienced_client"]["name"],
                    weight=self.GREEN_FLAGS["experienced_client"]["weight"],
                    details=f"Client with {projects_count} completed projects",
                )
            )

        return flags

    def _detect_excellent_rating(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect excellent client ratings.

        High ratings indicate client is professional and pays fairly.

        Args:
            project: Project data dictionary

        Returns:
            List of detected excellent rating flags
        """
        flags: List[FlagDetail] = []

        rating = project.get("client_rating")
        if not rating:
            return flags

        min_rating = self.GREEN_FLAGS["excellent_rating"]["min_rating"]

        if rating >= min_rating:
            flags.append(
                FlagDetail(
                    type="excellent_rating",
                    name=self.GREEN_FLAGS["excellent_rating"]["name"],
                    weight=self.GREEN_FLAGS["excellent_rating"]["weight"],
                    details=f"Excellent rating: {rating:.1f}/5.0",
                )
            )

        return flags

    def _detect_fair_budget(
        self, project: dict[str, Any], fair_value: Optional[float]
    ) -> List[FlagDetail]:
        """
        Detect fair or generous budgets.

        Budgets at or above fair value indicate realistic client expectations.

        Args:
            project: Project data dictionary
            fair_value: Fair market value in USD

        Returns:
            List of detected fair budget flags
        """
        flags: List[FlagDetail] = []

        if not fair_value:
            return flags

        client_budget = project.get("client_budget") or project.get("budget")
        if not client_budget:
            return flags

        ratio = client_budget / fair_value
        min_ratio = self.GREEN_FLAGS["fair_budget"]["min_ratio"]

        if ratio >= min_ratio:
            flags.append(
                FlagDetail(
                    type="fair_budget",
                    name=self.GREEN_FLAGS["fair_budget"]["name"],
                    weight=self.GREEN_FLAGS["fair_budget"]["weight"],
                    details=f"Budget ${client_budget:.0f} ({ratio*100:.0f}% of fair value)",
                )
            )

        return flags

    def _detect_realistic_deadline(
        self, project: dict[str, Any], estimated_hours: Optional[float]
    ) -> List[FlagDetail]:
        """
        Detect realistic deadlines with time buffer.

        Compares client deadline to estimated time needed plus buffer.

        Args:
            project: Project data dictionary
            estimated_hours: Estimated hours to complete project

        Returns:
            List of detected realistic deadline flags
        """
        flags: List[FlagDetail] = []

        if not estimated_hours:
            return flags

        client_deadline_days = project.get("client_deadline_days")
        if not client_deadline_days:
            return flags

        # Assume 6 productive hours per working day
        required_days = estimated_hours / 6.0
        buffer_ratio = self.GREEN_FLAGS["realistic_deadline"]["buffer_ratio"]
        comfortable_deadline = required_days * buffer_ratio

        if client_deadline_days >= comfortable_deadline:
            flags.append(
                FlagDetail(
                    type="realistic_deadline",
                    name=self.GREEN_FLAGS["realistic_deadline"]["name"],
                    weight=self.GREEN_FLAGS["realistic_deadline"]["weight"],
                    details=f"Deadline of {client_deadline_days} days is comfortable (minimum: {comfortable_deadline:.0f} days)",
                )
            )

        return flags

    def _detect_clear_scope(self, project: dict[str, Any]) -> List[FlagDetail]:
        """
        Detect clear scope definition.

        Presence of specification keywords indicates well-defined project.

        Args:
            project: Project data dictionary

        Returns:
            List of detected clear scope flags
        """
        flags: List[FlagDetail] = []

        description = (project.get("description") or "").lower()
        keywords = self.GREEN_FLAGS["clear_scope"]["keywords"]

        found_keywords = []
        for keyword in keywords:
            if keyword in description:
                found_keywords.append(keyword)

        if found_keywords:
            flags.append(
                FlagDetail(
                    type="clear_scope",
                    name=self.GREEN_FLAGS["clear_scope"]["name"],
                    weight=self.GREEN_FLAGS["clear_scope"]["weight"],
                    details=f"Well-defined scope: {', '.join(found_keywords)}",
                )
            )

        return flags

    # Helper Methods

    def _get_risk_level(self, risk_score: float) -> str:
        """
        Convert numeric score to risk level category.

        Args:
            risk_score: Numeric risk score (0-100)

        Returns:
            Risk level string (low, medium, high, critical)

        Examples:
            >>> assessor = ClientRiskAssessment()
            >>> assert assessor._get_risk_level(85) == "low"
            >>> assert assessor._get_risk_level(60) == "medium"
            >>> assert assessor._get_risk_level(40) == "high"
            >>> assert assessor._get_risk_level(20) == "critical"
        """
        if risk_score >= 70:
            return "low"
        elif risk_score >= 50:
            return "medium"
        elif risk_score >= 30:
            return "high"
        else:
            return "critical"

    def _generate_recommendation(
        self,
        risk_score: float,
        red_flags: List[FlagDetail],
        green_flags: List[FlagDetail],
    ) -> RecommendationDetail:
        """
        Generate accept/reject recommendation with specific reasoning.

        Decision logic:
        - Critical red flags → automatic reject
        - Score >= 70 → safe to accept
        - Score 50-69 → accept with protections
        - Score < 50 → reject

        Args:
            risk_score: Calculated risk score
            red_flags: List of detected red flags
            green_flags: List of detected green flags

        Returns:
            Recommendation with decision code and human-readable reason

        Examples:
            >>> assessor = ClientRiskAssessment()
            >>> # Critical red flag → reject
            >>> critical_flags = [{"severity": "critical", "name": "Free Work Request"}]
            >>> rec = assessor._generate_recommendation(60, critical_flags, [])
            >>> assert rec['decision'] == 'reject_high_risk'
            >>> # High score → accept
            >>> rec = assessor._generate_recommendation(85, [], [])
            >>> assert rec['decision'] == 'safe_to_accept'
        """
        critical_red_flags = [f for f in red_flags if f.get("severity") == "critical"]
        high_red_flags = [f for f in red_flags if f.get("severity") == "high"]

        # Critical red flags = automatic reject (regardless of score)
        if critical_red_flags:
            return RecommendationDetail(
                decision="reject_high_risk",
                reason=f"Critical red flags detected: {', '.join(f['name'] for f in critical_red_flags)}. Very high risk.",
            )

        # Risk score based recommendations
        if risk_score >= 70:
            return RecommendationDetail(
                decision="safe_to_accept",
                reason=f"Safe project (score: {risk_score}/100). {len(green_flags)} positive indicators, {len(red_flags)} warnings.",
            )

        elif risk_score >= 50:
            # Moderate risk - recommend specific protections
            protection_measures = []
            if high_red_flags:
                protection_measures.append("detailed contract")
            if any(f["type"] == "unrealistic_budget" for f in red_flags):
                protection_measures.append("negotiate budget")
            if any(f["type"] == "no_payment_history" for f in red_flags):
                protection_measures.append("upfront payment")

            return RecommendationDetail(
                decision="accept_with_protection",
                reason=f"Moderate risk (score: {risk_score}/100). Accept with protections: {', '.join(protection_measures)}.",
            )

        else:
            return RecommendationDetail(
                decision="reject_high_risk",
                reason=f"High risk project (score: {risk_score}/100). {len(red_flags)} red flags detected. Not recommended.",
            )
