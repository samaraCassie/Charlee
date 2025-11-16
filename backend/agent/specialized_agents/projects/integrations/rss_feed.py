"""RSS Feed integration for generic job feeds."""

import logging
from typing import List, Optional

from .base_platform import BasePlatformIntegration, JobOpportunity, PlatformConfig

logger = logging.getLogger(__name__)


class RSSFeedIntegration(BasePlatformIntegration):
    """RSS Feed platform integration."""

    PLATFORM_NAME = "RSS Feed"

    def test_connection(self) -> bool:
        """Test connection."""
        self.logger.info("RSS Feed connection test (mock mode)")
        return True

    def fetch_opportunities(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Fetch opportunities."""
        self.logger.info("Fetching RSS Feed opportunities (mock mode)")
        return []  # Mock: return empty for now

    def get_opportunity_details(self, external_id: str) -> Optional[JobOpportunity]:
        """Get opportunity details."""
        return None


def create_rss_feed_integration(config: PlatformConfig) -> RSSFeedIntegration:
    """Factory function."""
    return RSSFeedIntegration(config)
