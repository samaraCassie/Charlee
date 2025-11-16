"""Base platform integration class for freelance platforms."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """Configuration for platform integration."""

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    oauth_token: Optional[str] = None
    rate_limit_per_hour: int = 100
    timeout_seconds: int = 30
    custom_headers: Optional[Dict[str, str]] = None
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class JobOpportunity:
    """Standardized job opportunity data structure."""

    external_id: str
    title: str
    description: str
    client_name: Optional[str] = None
    client_rating: Optional[float] = None
    client_country: Optional[str] = None
    client_projects_count: Optional[int] = None
    required_skills: Optional[List[str]] = None
    skill_level: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[float] = None
    currency: str = "USD"
    deadline_days: Optional[int] = None
    contract_type: Optional[str] = None
    posted_at: Optional[datetime] = None
    url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class BasePlatformIntegration(ABC):
    """
    Abstract base class for freelance platform integrations.

    All platform-specific integrations should inherit from this class
    and implement the abstract methods.
    """

    def __init__(self, config: PlatformConfig):
        """
        Initialize platform integration.

        Args:
            config: Platform configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the connection to the platform is working.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def fetch_opportunities(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """
        Fetch job opportunities from the platform.

        Args:
            keywords: Search keywords
            category: Job category filter
            min_budget: Minimum budget filter
            max_results: Maximum number of results to return

        Returns:
            List of standardized job opportunities
        """
        pass

    @abstractmethod
    def get_opportunity_details(self, external_id: str) -> Optional[JobOpportunity]:
        """
        Get detailed information about a specific opportunity.

        Args:
            external_id: Platform-specific opportunity ID

        Returns:
            Detailed opportunity data or None if not found
        """
        pass

    def normalize_skills(self, raw_skills: Any) -> List[str]:
        """
        Normalize skill names to standard format.

        Args:
            raw_skills: Platform-specific skill data

        Returns:
            List of normalized skill names
        """
        if not raw_skills:
            return []

        if isinstance(raw_skills, str):
            return [s.strip() for s in raw_skills.split(",")]
        elif isinstance(raw_skills, list):
            return [str(s).strip() for s in raw_skills]
        else:
            return []

    def normalize_budget(self, raw_budget: Any, currency: str = "USD") -> Optional[float]:
        """
        Normalize budget to float value.

        Args:
            raw_budget: Platform-specific budget data
            currency: Budget currency

        Returns:
            Normalized budget in USD or None
        """
        if not raw_budget:
            return None

        try:
            # Remove currency symbols and convert to float
            if isinstance(raw_budget, str):
                cleaned = raw_budget.replace("$", "").replace(",", "").replace("USD", "").strip()
                return float(cleaned)
            return float(raw_budget)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not normalize budget: {raw_budget}")
            return None

    def deduplicate_opportunities(
        self, opportunities: List[JobOpportunity]
    ) -> List[JobOpportunity]:
        """
        Remove duplicate opportunities based on external_id.

        Args:
            opportunities: List of opportunities

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for opp in opportunities:
            if opp.external_id not in seen:
                seen.add(opp.external_id)
                unique.append(opp)

        return unique
