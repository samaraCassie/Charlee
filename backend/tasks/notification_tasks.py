"""Celery tasks for notification system automation.

This module contains periodic tasks for:
- Collecting notifications from external sources
- Generating intelligent digests
- Cleanup of old notifications
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

from celery import shared_task
from sqlalchemy.orm import Session

from database.config import SessionLocal
from database.models import NotificationSource
from services.agents.notification_agent import NotificationAgent
from services.digest_service import DigestService
from services.cleanup_service import CleanupService

logger = logging.getLogger(__name__)


@shared_task(name="notifications.collect_all_sources")
def collect_all_sources() -> Dict[str, any]:
    """
    Collect notifications from all enabled sources.

    This task runs periodically to fetch new notifications from all
    configured and enabled external sources (Email, GitHub, Slack, etc.).

    Returns:
        Dict with collection statistics:
        - sources_processed: Number of sources checked
        - total_collected: Total notifications collected
        - total_spam_filtered: Total spam filtered
        - errors: List of error messages
    """
    db = SessionLocal()
    try:
        logger.info("Starting notification collection from all sources")

        # Get all enabled notification sources
        sources = db.query(NotificationSource).filter(NotificationSource.enabled == True).all()

        if not sources:
            logger.info("No enabled notification sources found")
            return {
                "sources_processed": 0,
                "total_collected": 0,
                "total_spam_filtered": 0,
                "errors": [],
            }

        agent = NotificationAgent(db)
        total_collected = 0
        total_spam = 0
        all_errors = []

        # Collect from each source
        for source in sources:
            try:
                logger.info(f"Collecting from source {source.id}: {source.name} ({source.source_type})")
                result = agent.collect_from_source(source.id)

                total_collected += result["collected"]
                total_spam += result["spam_filtered"]
                all_errors.extend(result["errors"])

                # Update last_sync timestamp
                source.last_sync = datetime.now(timezone.utc)
                if result["errors"]:
                    source.last_error = "; ".join(result["errors"])
                else:
                    source.last_error = None
                db.commit()

                logger.info(
                    f"Collected {result['collected']} notifications from source {source.id}, "
                    f"{result['spam_filtered']} filtered as spam"
                )

            except Exception as e:
                error_msg = f"Error collecting from source {source.id}: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)

                # Update source error status
                source.last_error = str(e)
                db.commit()

        logger.info(
            f"Notification collection complete: {len(sources)} sources processed, "
            f"{total_collected} notifications collected, {total_spam} filtered as spam"
        )

        return {
            "sources_processed": len(sources),
            "total_collected": total_collected,
            "total_spam_filtered": total_spam,
            "errors": all_errors,
        }

    except Exception as e:
        logger.error(f"Fatal error in notification collection: {e}")
        return {
            "sources_processed": 0,
            "total_collected": 0,
            "total_spam_filtered": 0,
            "errors": [str(e)],
        }
    finally:
        db.close()


@shared_task(name="notifications.generate_daily_digests")
def generate_daily_digests() -> Dict[str, any]:
    """
    Generate daily digests for all users.

    Creates AI-powered summary of yesterday's notifications for each user.

    Returns:
        Dict with generation statistics:
        - users_processed: Number of users who received digests
        - errors: List of error messages
    """
    db = SessionLocal()
    try:
        logger.info("Starting daily digest generation for all users")

        service = DigestService(db)

        # Get all users who have notifications
        from database.models import User, Notification

        users = (
            db.query(User.id)
            .join(Notification, Notification.user_id == User.id)
            .distinct()
            .all()
        )

        users_processed = 0
        errors = []

        for (user_id,) in users:
            try:
                digest = service.generate_digest(user_id=user_id, digest_type="daily")
                logger.info(
                    f"Generated daily digest {digest.id} for user {user_id} "
                    f"({digest.notification_count} notifications)"
                )
                users_processed += 1

            except Exception as e:
                error_msg = f"Error generating daily digest for user {user_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        logger.info(f"Daily digest generation complete: {users_processed} users processed")

        return {
            "users_processed": users_processed,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Fatal error in daily digest generation: {e}")
        return {
            "users_processed": 0,
            "errors": [str(e)],
        }
    finally:
        db.close()


@shared_task(name="notifications.generate_weekly_digests")
def generate_weekly_digests() -> Dict[str, any]:
    """
    Generate weekly digests for all users.

    Creates AI-powered summary of the past week's notifications.

    Returns:
        Dict with generation statistics.
    """
    db = SessionLocal()
    try:
        logger.info("Starting weekly digest generation for all users")

        service = DigestService(db)

        from database.models import User, Notification

        users = (
            db.query(User.id)
            .join(Notification, Notification.user_id == User.id)
            .distinct()
            .all()
        )

        users_processed = 0
        errors = []

        for (user_id,) in users:
            try:
                digest = service.generate_digest(user_id=user_id, digest_type="weekly")
                logger.info(
                    f"Generated weekly digest {digest.id} for user {user_id} "
                    f"({digest.notification_count} notifications)"
                )
                users_processed += 1

            except Exception as e:
                error_msg = f"Error generating weekly digest for user {user_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        logger.info(f"Weekly digest generation complete: {users_processed} users processed")

        return {
            "users_processed": users_processed,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Fatal error in weekly digest generation: {e}")
        return {
            "users_processed": 0,
            "errors": [str(e)],
        }
    finally:
        db.close()


@shared_task(name="notifications.generate_monthly_digests")
def generate_monthly_digests() -> Dict[str, any]:
    """
    Generate monthly digests for all users.

    Creates AI-powered summary of the past month's notifications.

    Returns:
        Dict with generation statistics.
    """
    db = SessionLocal()
    try:
        logger.info("Starting monthly digest generation for all users")

        service = DigestService(db)

        from database.models import User, Notification

        users = (
            db.query(User.id)
            .join(Notification, Notification.user_id == User.id)
            .distinct()
            .all()
        )

        users_processed = 0
        errors = []

        for (user_id,) in users:
            try:
                digest = service.generate_digest(user_id=user_id, digest_type="monthly")
                logger.info(
                    f"Generated monthly digest {digest.id} for user {user_id} "
                    f"({digest.notification_count} notifications)"
                )
                users_processed += 1

            except Exception as e:
                error_msg = f"Error generating monthly digest for user {user_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        logger.info(f"Monthly digest generation complete: {users_processed} users processed")

        return {
            "users_processed": users_processed,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Fatal error in monthly digest generation: {e}")
        return {
            "users_processed": 0,
            "errors": [str(e)],
        }
    finally:
        db.close()


@shared_task(name="notifications.cleanup_old_notifications")
def cleanup_old_notifications() -> Dict[str, any]:
    """
    Clean up old notifications based on retention policies.

    Removes:
    - Archived notifications older than 90 days
    - Read notifications older than 30 days
    - Spam notifications older than 7 days
    - Old digests (keeps only latest 10 of each type per user)

    Returns:
        Dict with cleanup statistics:
        - notifications_deleted: Number of notifications deleted
        - digests_deleted: Number of digests deleted
        - errors: List of error messages
    """
    db = SessionLocal()
    try:
        logger.info("Starting cleanup of old notifications and digests")

        service = CleanupService(db)
        result = service.cleanup_old_data()

        logger.info(
            f"Cleanup complete: {result['notifications_deleted']} notifications deleted, "
            f"{result['digests_deleted']} digests deleted"
        )

        return result

    except Exception as e:
        logger.error(f"Fatal error in notification cleanup: {e}")
        return {
            "notifications_deleted": 0,
            "digests_deleted": 0,
            "errors": [str(e)],
        }
    finally:
        db.close()
