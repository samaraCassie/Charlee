"""Tests for NotificationCleanupService."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from database.models import Notification, User
from services.notification_cleanup import NotificationCleanupService


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def cleanup_service(db_session: Session) -> NotificationCleanupService:
    """Create cleanup service instance."""
    return NotificationCleanupService(db=db_session)


class TestNotificationCleanupService:
    """Test suite for NotificationCleanupService."""

    def test_auto_archive_spam(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test automatic archiving of spam notifications."""
        # Create spam notifications
        for i in range(5):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Spam {i}",
                message="Spam message",
                categoria="spam",
                arquivada=False,
            )
            db_session.add(notif)

        # Create non-spam notification
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Important",
            message="Important message",
            categoria="importante",
            arquivada=False,
        )
        db_session.add(notif)

        db_session.commit()

        # Run auto-archive
        result = cleanup_service.auto_archive_spam(user_id=test_user.id)

        assert result["archived"] == 5
        assert result["total_processed"] == 5

        # Verify spam was archived
        spam_count = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, categoria="spam", arquivada=True)
            .count()
        )
        assert spam_count == 5

        # Verify important notification was not archived
        important = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, categoria="importante")
            .first()
        )
        assert important.arquivada is False

    def test_delete_old_archived(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test deletion of old archived notifications."""
        now = datetime.now(timezone.utc)

        # Create old archived notifications (35 days old)
        for i in range(3):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old {i}",
                message="Old message",
                arquivada=True,
                created_at=now - timedelta(days=35),
            )
            db_session.add(notif)

        # Create recent archived notification (20 days old)
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Recent",
            message="Recent message",
            arquivada=True,
            created_at=now - timedelta(days=20),
        )
        db_session.add(notif)

        db_session.commit()

        # Run deletion with 30-day retention
        result = cleanup_service.delete_old_archived(
            user_id=test_user.id, retention_days=30
        )

        assert result["deleted"] == 3
        assert result["retention_days"] == 30

        # Verify old ones were deleted
        old_count = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == test_user.id,
                Notification.arquivada == True,  # noqa: E712
                Notification.created_at < now - timedelta(days=30),
            )
            .count()
        )
        assert old_count == 0

        # Verify recent one remains
        recent = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, title="Recent")
            .first()
        )
        assert recent is not None

    def test_archive_old_read(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test archiving old read notifications."""
        now = datetime.now(timezone.utc)

        # Create old read notifications (10 days old)
        for i in range(4):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Read {i}",
                message="Old read message",
                read=True,
                read_at=now - timedelta(days=10),
                arquivada=False,
            )
            db_session.add(notif)

        # Create recent read notification (5 days old)
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Recent Read",
            message="Recent read message",
            read=True,
            read_at=now - timedelta(days=5),
            arquivada=False,
        )
        db_session.add(notif)

        # Create unread notification
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Unread",
            message="Unread message",
            read=False,
            arquivada=False,
        )
        db_session.add(notif)

        db_session.commit()

        # Run archive with 7-day threshold
        result = cleanup_service.archive_old_read(user_id=test_user.id, archive_after_days=7)

        assert result["archived"] == 4

        # Verify old read were archived
        archived_count = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == test_user.id,
                Notification.read == True,  # noqa: E712
                Notification.arquivada == True,  # noqa: E712
            )
            .count()
        )
        assert archived_count == 4

        # Verify recent read and unread were not archived
        recent_read = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, title="Recent Read")
            .first()
        )
        assert recent_read.arquivada is False

        unread = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, title="Unread")
            .first()
        )
        assert unread.arquivada is False

    def test_cleanup_informativo(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test cleanup of informativo notifications."""
        now = datetime.now(timezone.utc)

        # Create old informativo notifications (5 days old)
        for i in range(3):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Info {i}",
                message="Old info",
                categoria="informativo",
                arquivada=False,
                created_at=now - timedelta(days=5),
            )
            db_session.add(notif)

        # Create recent informativo (2 days old)
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Recent Info",
            message="Recent info",
            categoria="informativo",
            arquivada=False,
            created_at=now - timedelta(days=2),
        )
        db_session.add(notif)

        # Create old important notification
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Important",
            message="Important",
            categoria="importante",
            arquivada=False,
            created_at=now - timedelta(days=5),
        )
        db_session.add(notif)

        db_session.commit()

        # Run cleanup with 3-day threshold
        result = cleanup_service.cleanup_informativo(
            user_id=test_user.id, archive_after_days=3
        )

        assert result["archived"] == 3

        # Verify old informativo were archived
        archived_info = (
            db_session.query(Notification)
            .filter(
                Notification.user_id == test_user.id,
                Notification.categoria == "informativo",
                Notification.arquivada == True,  # noqa: E712
            )
            .count()
        )
        assert archived_info == 3

        # Verify recent informativo and important were not archived
        recent_info = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, title="Recent Info")
            .first()
        )
        assert recent_info.arquivada is False

        important = (
            db_session.query(Notification)
            .filter_by(user_id=test_user.id, title="Important")
            .first()
        )
        assert important.arquivada is False

    def test_run_full_cleanup(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test running full cleanup routine."""
        now = datetime.now(timezone.utc)

        # Create various types of notifications to be cleaned
        # 1. Spam (should be archived)
        for i in range(2):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Spam {i}",
                message="Spam",
                categoria="spam",
                arquivada=False,
            )
            db_session.add(notif)

        # 2. Old read (should be archived)
        for i in range(3):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Read {i}",
                message="Old read",
                read=True,
                read_at=now - timedelta(days=10),
                arquivada=False,
            )
            db_session.add(notif)

        # 3. Old informativo (should be archived)
        for i in range(4):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Info {i}",
                message="Old info",
                categoria="informativo",
                arquivada=False,
                created_at=now - timedelta(days=5),
            )
            db_session.add(notif)

        # 4. Very old archived (should be deleted)
        for i in range(2):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Very Old {i}",
                message="Very old",
                arquivada=True,
                created_at=now - timedelta(days=35),
            )
            db_session.add(notif)

        db_session.commit()

        # Run full cleanup
        result = cleanup_service.run_full_cleanup(user_id=test_user.id)

        assert result["success"] is True
        assert result["total_archived"] == 2 + 3 + 4  # spam + old_read + informativo
        assert result["total_deleted"] == 2  # very old archived

        # Verify total count of notifications
        remaining_count = (
            db_session.query(Notification).filter_by(user_id=test_user.id).count()
        )
        # Started with 11 (2+3+4+2), deleted 2, so should have 9
        assert remaining_count == 9

    def test_get_cleanup_stats(
        self, db_session: Session, test_user: User, cleanup_service: NotificationCleanupService
    ):
        """Test getting cleanup statistics."""
        now = datetime.now(timezone.utc)

        # Create notifications that need cleanup
        # 2 spam to archive
        for i in range(2):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Spam {i}",
                message="Spam",
                categoria="spam",
                arquivada=False,
            )
            db_session.add(notif)

        # 3 old read to archive (10 days old)
        for i in range(3):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Read {i}",
                message="Old read",
                read=True,
                read_at=now - timedelta(days=10),
                arquivada=False,
            )
            db_session.add(notif)

        # 4 old informativo to archive (5 days old)
        for i in range(4):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Old Info {i}",
                message="Old info",
                categoria="informativo",
                arquivada=False,
                created_at=now - timedelta(days=5),
            )
            db_session.add(notif)

        # 1 very old archived to delete (35 days old)
        notif = Notification(
            user_id=test_user.id,
            type="email",
            title="Very Old",
            message="Very old",
            arquivada=True,
            created_at=now - timedelta(days=35),
        )
        db_session.add(notif)

        db_session.commit()

        # Get stats
        stats = cleanup_service.get_cleanup_stats(test_user.id)

        assert stats["spam_to_archive"] == 2
        assert stats["old_read_to_archive"] == 3
        assert stats["informativo_to_archive"] == 4
        assert stats["old_archived_to_delete"] == 1
        assert stats["total_to_cleanup"] == 2 + 3 + 4
        assert stats["total_to_delete"] == 1

    def test_cleanup_respects_user_isolation(
        self, db_session: Session, cleanup_service: NotificationCleanupService
    ):
        """Test that cleanup operations don't affect other users."""
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password="hashed",
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password="hashed",
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()

        # Create spam for both users
        for user in [user1, user2]:
            notif = Notification(
                user_id=user.id,
                type="email",
                title="Spam",
                message="Spam",
                categoria="spam",
                arquivada=False,
            )
            db_session.add(notif)

        db_session.commit()

        # Run cleanup only for user1
        result = cleanup_service.auto_archive_spam(user_id=user1.id)

        assert result["archived"] == 1

        # Verify only user1's spam was archived
        user1_spam = (
            db_session.query(Notification)
            .filter_by(user_id=user1.id, categoria="spam")
            .first()
        )
        assert user1_spam.arquivada is True

        user2_spam = (
            db_session.query(Notification)
            .filter_by(user_id=user2.id, categoria="spam")
            .first()
        )
        assert user2_spam.arquivada is False
