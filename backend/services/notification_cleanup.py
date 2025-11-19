"""
Auto-archiving and cleanup service for notifications.

Automatically archives spam, removes old notifications, and maintains
a clean notification inbox for users.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from database.config import SessionLocal
from database.models import Notification

logger = logging.getLogger(__name__)


class NotificationCleanupService:
    """
    Service for automated notification cleanup and archiving.

    Handles:
    - Auto-archiving spam notifications
    - Removing old archived notifications
    - Cleaning up read notifications after retention period
    """

    def __init__(self, db: Session | None = None):
        """
        Initialize cleanup service.

        Args:
            db: Optional database session. If not provided, creates a new one.
        """
        self.db = db or SessionLocal()
        self._should_close_db = db is None

    def __del__(self):
        """Close database session if we created it."""
        if self._should_close_db and self.db:
            self.db.close()

    def auto_archive_spam(self, user_id: int | None = None) -> dict:
        """
        Automatically archive notifications classified as spam.

        Args:
            user_id: Optional user ID. If None, processes all users.

        Returns:
            Dict with archive statistics
        """
        query = self.db.query(Notification).filter(
            Notification.categoria == "spam", Notification.arquivada == False  # noqa: E712
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        spam_notifications = query.all()

        archived_count = 0
        for notification in spam_notifications:
            notification.arquivada = True
            archived_count += 1

        self.db.commit()

        logger.info(f"Auto-archived {archived_count} spam notifications")

        return {"archived": archived_count, "total_processed": len(spam_notifications)}

    def delete_old_archived(self, user_id: int | None = None, retention_days: int = 30) -> dict:
        """
        Delete archived notifications older than retention period.

        Args:
            user_id: Optional user ID. If None, processes all users.
            retention_days: Number of days to retain archived notifications

        Returns:
            Dict with deletion statistics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        query = self.db.query(Notification).filter(
            Notification.arquivada == True, Notification.created_at < cutoff_date  # noqa: E712
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        old_notifications = query.all()
        deleted_count = 0

        for notification in old_notifications:
            self.db.delete(notification)
            deleted_count += 1

        self.db.commit()

        logger.info(
            f"Deleted {deleted_count} archived notifications older than {retention_days} days"
        )

        return {
            "deleted": deleted_count,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
        }

    def archive_old_read(self, user_id: int | None = None, archive_after_days: int = 7) -> dict:
        """
        Archive read notifications older than specified days.

        Args:
            user_id: Optional user ID. If None, processes all users.
            archive_after_days: Number of days after which to archive read notifications

        Returns:
            Dict with archive statistics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=archive_after_days)

        query = self.db.query(Notification).filter(
            Notification.read == True,  # noqa: E712
            Notification.arquivada == False,  # noqa: E712
            Notification.read_at < cutoff_date,
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        old_read_notifications = query.all()
        archived_count = 0

        for notification in old_read_notifications:
            notification.arquivada = True
            archived_count += 1

        self.db.commit()

        logger.info(
            f"Archived {archived_count} read notifications older than {archive_after_days} days"
        )

        return {
            "archived": archived_count,
            "archive_after_days": archive_after_days,
            "cutoff_date": cutoff_date.isoformat(),
        }

    def cleanup_informativo(self, user_id: int | None = None, archive_after_days: int = 3) -> dict:
        """
        Archive informational notifications after a short period.

        Informational notifications are typically newsletters, updates, etc.
        that don't require action and can be archived quickly.

        Args:
            user_id: Optional user ID. If None, processes all users.
            archive_after_days: Number of days after which to archive

        Returns:
            Dict with archive statistics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=archive_after_days)

        query = self.db.query(Notification).filter(
            Notification.categoria == "informativo",
            Notification.arquivada == False,  # noqa: E712
            Notification.created_at < cutoff_date,
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        informativo_notifications = query.all()
        archived_count = 0

        for notification in informativo_notifications:
            notification.arquivada = True
            archived_count += 1

        self.db.commit()

        logger.info(
            f"Archived {archived_count} informativo notifications older than {archive_after_days} days"
        )

        return {
            "archived": archived_count,
            "archive_after_days": archive_after_days,
            "cutoff_date": cutoff_date.isoformat(),
        }

    def run_full_cleanup(self, user_id: int | None = None) -> dict:
        """
        Run complete cleanup routine.

        Args:
            user_id: Optional user ID. If None, processes all users.

        Returns:
            Dict with comprehensive cleanup statistics
        """
        logger.info(f"Starting full cleanup for user_id={user_id or 'ALL'}")

        results = {
            "spam_archived": self.auto_archive_spam(user_id),
            "old_read_archived": self.archive_old_read(user_id, archive_after_days=7),
            "informativo_archived": self.cleanup_informativo(user_id, archive_after_days=3),
            "old_deleted": self.delete_old_archived(user_id, retention_days=30),
        }

        total_archived = (
            results["spam_archived"]["archived"]
            + results["old_read_archived"]["archived"]
            + results["informativo_archived"]["archived"]
        )
        total_deleted = results["old_deleted"]["deleted"]

        logger.info(f"Cleanup completed: {total_archived} archived, {total_deleted} deleted")

        return {
            "success": True,
            "total_archived": total_archived,
            "total_deleted": total_deleted,
            "details": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_cleanup_stats(self, user_id: int) -> dict:
        """
        Get statistics about notifications that need cleanup.

        Args:
            user_id: User ID

        Returns:
            Dict with cleanup statistics
        """
        # Count spam not archived
        spam_count = (
            self.db.query(Notification)
            .filter_by(user_id=user_id, categoria="spam", arquivada=False)
            .count()
        )

        # Count old read notifications (>7 days)
        old_read_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        old_read_count = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.read == True,  # noqa: E712
                Notification.arquivada == False,  # noqa: E712
                Notification.read_at < old_read_cutoff,
            )
            .count()
        )

        # Count old informativo (>3 days)
        informativo_cutoff = datetime.now(timezone.utc) - timedelta(days=3)
        informativo_count = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.categoria == "informativo",
                Notification.arquivada == False,  # noqa: E712
                Notification.created_at < informativo_cutoff,
            )
            .count()
        )

        # Count old archived (>30 days)
        archived_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        old_archived_count = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.arquivada == True,  # noqa: E712
                Notification.created_at < archived_cutoff,
            )
            .count()
        )

        return {
            "spam_to_archive": spam_count,
            "old_read_to_archive": old_read_count,
            "informativo_to_archive": informativo_count,
            "old_archived_to_delete": old_archived_count,
            "total_to_cleanup": spam_count + old_read_count + informativo_count,
            "total_to_delete": old_archived_count,
        }
