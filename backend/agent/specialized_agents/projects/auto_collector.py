"""Auto-collection scheduler for freelance opportunities.

Automatically collects opportunities from configured platforms at scheduled intervals.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from database.models import FreelancePlatform
from .integrations import (
    PlatformConfig,
    create_upwork_integration,
    create_freelancer_com_integration,
)

logger = logging.getLogger(__name__)


class AutoCollector:
    """
    Automated job opportunity collector.

    Runs collection tasks for all active platforms based on their
    configured collection intervals.
    """

    def __init__(self, db: Session):
        """Initialize auto-collector."""
        self.db = db

    def should_collect(self, platform: FreelancePlatform) -> bool:
        """
        Determine if a platform should be collected now.

        Args:
            platform: FreelancePlatform instance

        Returns:
            True if collection should run
        """
        if not platform.active or not platform.auto_collect:
            return False

        if not platform.last_collection_at:
            return True  # Never collected before

        # Check if enough time has passed
        next_collection = platform.last_collection_at + timedelta(
            minutes=platform.collection_interval_minutes
        )

        return datetime.now() >= next_collection

    def collect_from_platform(self, platform: FreelancePlatform, max_results: int = 50) -> int:
        """
        Collect opportunities from a single platform.

        Args:
            platform: FreelancePlatform instance
            max_results: Maximum opportunities to collect

        Returns:
            Number of new opportunities collected
        """
        try:
            logger.info(f"Starting collection from {platform.name}")

            # Create platform integration
            config = PlatformConfig(
                api_key=platform.api_config.get("api_key") if platform.api_config else None,
                api_secret=platform.api_config.get("api_secret") if platform.api_config else None,
            )

            # Select appropriate integration
            if "upwork" in platform.name.lower():
                integration = create_upwork_integration(config)
            elif "freelancer" in platform.name.lower():
                integration = create_freelancer_com_integration(config)
            else:
                logger.warning(f"No integration available for platform: {platform.name}")
                return 0

            # Fetch opportunities
            opportunities = integration.fetch_opportunities(max_results=max_results)

            # Save to database (implementation would call CollectorAgent)
            logger.info(f"Collected {len(opportunities)} opportunities from {platform.name}")

            # Update platform stats
            platform.last_collection_at = datetime.now()
            platform.last_collection_count = len(opportunities)
            platform.total_projects_collected += len(opportunities)
            self.db.commit()

            return len(opportunities)

        except Exception as e:
            logger.error(f"Error collecting from {platform.name}: {e}")
            self.db.rollback()
            return 0

    def run_collection_cycle(self, user_id: Optional[int] = None) -> dict:
        """
        Run a full collection cycle for all eligible platforms.

        Args:
            user_id: Optional user ID to filter platforms

        Returns:
            Collection results summary
        """
        try:
            query = self.db.query(FreelancePlatform).filter(
                FreelancePlatform.active == True,  # noqa: E712
                FreelancePlatform.auto_collect == True,  # noqa: E712
            )

            if user_id:
                query = query.filter(FreelancePlatform.user_id == user_id)

            platforms = query.all()

            results = {"total_platforms": 0, "collected": 0, "platforms": []}

            for platform in platforms:
                if self.should_collect(platform):
                    count = self.collect_from_platform(platform)
                    results["total_platforms"] += 1
                    results["collected"] += count
                    results["platforms"].append({"name": platform.name, "count": count})

            logger.info(f"Collection cycle complete: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in collection cycle: {e}")
            return {"error": str(e)}


def create_auto_collector(db: Session) -> AutoCollector:
    """Factory function to create AutoCollector."""
    return AutoCollector(db)
