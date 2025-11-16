"""Celery tasks for automated opportunity collection.

This module contains background tasks that automatically collect
freelance opportunities from configured platforms.
"""

import logging
from typing import Dict, Any

from celery import Task
from celery_app import celery_app
from database.session import SessionLocal
from agent.specialized_agents.projects.auto_collector import AutoCollector

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""

    _db = None

    @property
    def db(self):
        """Get database session."""
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Close database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.opportunity_collector.collect_all_opportunities",
    max_retries=3,
    default_retry_delay=60,
)
def collect_all_opportunities(self) -> Dict[str, Any]:
    """
    Collect opportunities from all active platforms.

    This task runs periodically (every 15 minutes by default) and:
    1. Queries all active platforms with auto_collect enabled
    2. Checks if collection interval has elapsed for each platform
    3. Collects new opportunities and stores them in the database

    Returns:
        Dict with collection statistics:
        - total_platforms: Number of platforms processed
        - total_collected: Total opportunities collected
        - platforms_processed: List of platform names
        - errors: List of any errors encountered
    """
    try:
        logger.info("Starting automated opportunity collection")

        # Create auto-collector
        collector = AutoCollector(db=self.db)

        # Run collection cycle for all users
        results = collector.run_collection_cycle()

        logger.info(
            f"Collection completed: {results['total_collected']} opportunities "
            f"from {results['total_platforms']} platforms"
        )

        return {
            "status": "success",
            "total_platforms": results["total_platforms"],
            "total_collected": results["total_collected"],
            "platforms_processed": results.get("platforms_processed", []),
            "timestamp": results.get("timestamp"),
        }

    except Exception as exc:
        logger.error(f"Error during opportunity collection: {exc}", exc_info=True)

        # Retry the task
        raise self.retry(exc=exc)


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.opportunity_collector.collect_user_opportunities",
)
def collect_user_opportunities(self, user_id: int) -> Dict[str, Any]:
    """
    Collect opportunities for a specific user.

    Args:
        user_id: User ID to collect opportunities for

    Returns:
        Dict with collection statistics
    """
    try:
        logger.info(f"Starting opportunity collection for user {user_id}")

        # Create auto-collector
        collector = AutoCollector(db=self.db)

        # Run collection cycle for specific user
        results = collector.run_collection_cycle(user_id=user_id)

        logger.info(
            f"Collection completed for user {user_id}: "
            f"{results['total_collected']} opportunities"
        )

        return {
            "status": "success",
            "user_id": user_id,
            "total_platforms": results["total_platforms"],
            "total_collected": results["total_collected"],
            "timestamp": results.get("timestamp"),
        }

    except Exception as exc:
        logger.error(
            f"Error during opportunity collection for user {user_id}: {exc}",
            exc_info=True,
        )

        # Retry the task
        raise self.retry(exc=exc)


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.opportunity_collector.collect_platform_opportunities",
)
def collect_platform_opportunities(self, platform_id: int) -> Dict[str, Any]:
    """
    Collect opportunities from a specific platform.

    Args:
        platform_id: Platform ID to collect from

    Returns:
        Dict with collection statistics
    """
    try:
        from database.models import FreelancePlatform

        logger.info(f"Starting opportunity collection for platform {platform_id}")

        # Get platform
        platform = (
            self.db.query(FreelancePlatform).filter(FreelancePlatform.id == platform_id).first()
        )

        if not platform:
            logger.error(f"Platform {platform_id} not found")
            return {"status": "error", "message": "Platform not found"}

        # Create auto-collector
        collector = AutoCollector(db=self.db)

        # Collect from specific platform
        count = collector.collect_from_platform(platform, max_results=50)

        logger.info(f"Collection completed for platform {platform.name}: {count} opportunities")

        return {
            "status": "success",
            "platform_id": platform_id,
            "platform_name": platform.name,
            "opportunities_collected": count,
        }

    except Exception as exc:
        logger.error(
            f"Error during opportunity collection for platform {platform_id}: {exc}",
            exc_info=True,
        )

        # Retry the task
        raise self.retry(exc=exc)
