"""LinkedIn Jobs integration."""

import logging
from typing import List, Optional

from .base_platform import BasePlatformIntegration, JobOpportunity, PlatformConfig

logger = logging.getLogger(__name__)


class LinkedInJobsIntegration(BasePlatformIntegration):
    """LinkedIn Jobs platform integration."""

    PLATFORM_NAME = "LinkedIn Jobs"

    def test_connection(self) -> bool:
        """Test connection."""
        self.logger.info("LinkedIn Jobs connection test (mock mode)")
        return True

    def fetch_opportunities(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Fetch opportunities."""
        self.logger.info("Fetching LinkedIn Jobs (mock mode)")
        return []  # Mock: return empty for now

    def get_opportunity_details(self, external_id: str) -> Optional[JobOpportunity]:
        """Get opportunity details."""
        return None


def create_linkedin_jobs_integration(config: PlatformConfig) -> LinkedInJobsIntegration:
    """Factory function."""
    return LinkedInJobsIntegration(config)
