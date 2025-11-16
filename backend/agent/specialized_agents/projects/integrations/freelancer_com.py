"""Freelancer.com integration."""

import logging
from typing import List, Optional

from .base_platform import BasePlatformIntegration, JobOpportunity, PlatformConfig

logger = logging.getLogger(__name__)


class FreelancerComIntegration(BasePlatformIntegration):
    """Freelancer.com platform integration."""

    PLATFORM_NAME = "Freelancer.com"

    def test_connection(self) -> bool:
        """Test connection."""
        self.logger.info("Freelancer.com connection test (mock mode)")
        return True

    def fetch_opportunities(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Fetch opportunities."""
        self.logger.info("Fetching Freelancer.com opportunities (mock mode)")
        return []  # Mock: return empty for now

    def get_opportunity_details(self, external_id: str) -> Optional[JobOpportunity]:
        """Get opportunity details."""
        return None


def create_freelancer_com_integration(config: PlatformConfig) -> FreelancerComIntegration:
    """Factory function."""
    return FreelancerComIntegration(config)
