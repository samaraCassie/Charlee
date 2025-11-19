"""Tests for advanced notification system CRUD operations."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from database import crud
from database.models import User
from database.schemas import (
    FocusSessionCreate,
    NotificationDigestBase,
    NotificationRuleCreate,
    NotificationRuleUpdate,
    NotificationSourceCreate,
    NotificationSourceUpdate,
    ResponseTemplateCreate,
)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestNotificationSourceCRUD:
    """Test suite for NotificationSource CRUD operations."""

    def test_create_notification_source(self, db: Session, test_user: User):
        """Test creating a notification source."""
        source_data = NotificationSourceCreate(
            source_type="email",
            name="Gmail Account",
            credentials={"username": "test@gmail.com", "password": "encrypted"},
            settings={"folders": ["INBOX"], "only_unread": True},
            enabled=True,
            sync_frequency_minutes=15,
        )

        source = crud.create_notification_source(db, source_data, test_user.id)

        assert source.id is not None
        assert source.user_id == test_user.id
        assert source.source_type == "email"
        assert source.name == "Gmail Account"
        assert source.enabled is True
        assert source.sync_frequency_minutes == 15

    def test_get_notification_source(self, db: Session, test_user: User):
        """Test retrieving a notification source."""
        source_data = NotificationSourceCreate(
            source_type="github",
            name="GitHub Notifications",
            credentials={"token": "ghp_xxx"},
            enabled=True,
        )

        created_source = crud.create_notification_source(db, source_data, test_user.id)

        retrieved_source = crud.get_notification_source(db, created_source.id, test_user.id)

        assert retrieved_source is not None
        assert retrieved_source.id == created_source.id
        assert retrieved_source.source_type == "github"

    def test_get_notification_sources(self, db: Session, test_user: User):
        """Test retrieving all notification sources for a user."""
        # Create multiple sources
        for i, source_type in enumerate(["email", "github", "slack"]):
            source_data = NotificationSourceCreate(
                source_type=source_type,  # type: ignore[arg-type]
                name=f"{source_type.title()} #{i}",
                enabled=True,
            )
            crud.create_notification_source(db, source_data, test_user.id)

        sources = crud.get_notification_sources(db, test_user.id)

        assert len(sources) == 3
        assert {s.source_type for s in sources} == {"email", "github", "slack"}

    def test_update_notification_source(self, db: Session, test_user: User):
        """Test updating a notification source."""
        source_data = NotificationSourceCreate(
            source_type="email",
            name="Old Name",
            enabled=True,
        )

        source = crud.create_notification_source(db, source_data, test_user.id)

        update_data = NotificationSourceUpdate(
            name="New Name",
            enabled=False,
            sync_frequency_minutes=30,
        )

        updated_source = crud.update_notification_source(db, source.id, test_user.id, update_data)

        assert updated_source is not None
        assert updated_source.name == "New Name"
        assert updated_source.enabled is False
        assert updated_source.sync_frequency_minutes == 30

    def test_delete_notification_source(self, db: Session, test_user: User):
        """Test deleting a notification source."""
        source_data = NotificationSourceCreate(
            source_type="email",
            name="To Delete",
            enabled=True,
        )

        source = crud.create_notification_source(db, source_data, test_user.id)
        source_id = source.id

        success = crud.delete_notification_source(db, source_id, test_user.id)

        assert success is True

        # Verify it's deleted
        deleted_source = crud.get_notification_source(db, source_id, test_user.id)
        assert deleted_source is None


class TestNotificationRuleCRUD:
    """Test suite for NotificationRule CRUD operations."""

    def test_create_notification_rule(self, db: Session, test_user: User):
        """Test creating a notification rule."""
        rule_data = NotificationRuleCreate(
            name="Spam Filter",
            description="Filter out recruiter spam",
            enabled=True,
            priority=10,
            conditions={"all": [{"field": "sender", "operator": "contains", "value": "recruiter"}]},
            actions=[{"type": "classify", "categoria": "spam"}, {"type": "archive"}],
        )

        rule = crud.create_notification_rule(db, rule_data, test_user.id)

        assert rule.id is not None
        assert rule.user_id == test_user.id
        assert rule.name == "Spam Filter"
        assert rule.enabled is True
        assert rule.priority == 10
        assert "all" in rule.conditions
        assert len(rule.actions) == 2

    def test_get_notification_rules(self, db: Session, test_user: User):
        """Test retrieving notification rules."""
        # Create enabled and disabled rules
        for i in range(3):
            rule_data = NotificationRuleCreate(
                name=f"Rule {i}",
                enabled=i < 2,  # First 2 enabled, last disabled
                priority=i,
                conditions={"all": []},
                actions=[],
            )
            crud.create_notification_rule(db, rule_data, test_user.id)

        # Get all rules
        all_rules = crud.get_notification_rules(db, test_user.id)
        assert len(all_rules) == 3

        # Get only enabled rules
        enabled_rules = crud.get_notification_rules(db, test_user.id, enabled_only=True)
        assert len(enabled_rules) == 2

    def test_update_notification_rule(self, db: Session, test_user: User):
        """Test updating a notification rule."""
        rule_data = NotificationRuleCreate(
            name="Old Rule",
            enabled=True,
            priority=5,
            conditions={"all": []},
            actions=[],
        )

        rule = crud.create_notification_rule(db, rule_data, test_user.id)

        update_data = NotificationRuleUpdate(
            name="Updated Rule",
            enabled=False,
            priority=20,
        )

        updated_rule = crud.update_notification_rule(db, rule.id, test_user.id, update_data)

        assert updated_rule is not None
        assert updated_rule.name == "Updated Rule"
        assert updated_rule.enabled is False
        assert updated_rule.priority == 20

    def test_delete_notification_rule(self, db: Session, test_user: User):
        """Test deleting a notification rule."""
        rule_data = NotificationRuleCreate(
            name="To Delete",
            enabled=True,
            priority=5,
            conditions={"all": []},
            actions=[],
        )

        rule = crud.create_notification_rule(db, rule_data, test_user.id)
        rule_id = rule.id

        success = crud.delete_notification_rule(db, rule_id, test_user.id)

        assert success is True

        deleted_rule = crud.get_notification_rule(db, rule_id, test_user.id)
        assert deleted_rule is None


class TestNotificationDigestCRUD:
    """Test suite for NotificationDigest CRUD operations."""

    def test_create_notification_digest(self, db: Session, test_user: User):
        """Test creating a notification digest."""
        now = datetime.now(timezone.utc)
        period_start = now - timedelta(days=1)
        period_end = now

        digest_data = NotificationDigestBase(
            digest_type="daily",
            period_start=period_start,
            period_end=period_end,
            total_notifications=50,
            urgent_count=5,
            important_count=10,
            informativo_count=20,
            spam_count=15,
            archived_count=15,
            time_saved_minutes=30,
            summary_text="You had a busy day with 50 notifications.",
            highlights=[{"title": "Important meeting", "why": "Deadline approaching"}],
        )

        digest = crud.create_notification_digest(db, digest_data, test_user.id)

        assert digest.id is not None
        assert digest.user_id == test_user.id
        assert digest.digest_type == "daily"
        assert digest.total_notifications == 50
        assert digest.urgent_count == 5
        assert digest.time_saved_minutes == 30

    def test_get_notification_digests(self, db: Session, test_user: User):
        """Test retrieving notification digests."""
        now = datetime.now(timezone.utc)

        # Create multiple digests
        for i in range(3):
            period_start = now - timedelta(days=i + 1)
            period_end = now - timedelta(days=i)

            digest_data = NotificationDigestBase(
                digest_type="daily",
                period_start=period_start,
                period_end=period_end,
                total_notifications=10 * (i + 1),
            )
            crud.create_notification_digest(db, digest_data, test_user.id)

        digests = crud.get_notification_digests(db, test_user.id)

        assert len(digests) == 3
        # Should be ordered by period_start descending
        assert digests[0].total_notifications == 10  # Most recent

    def test_get_latest_digest(self, db: Session, test_user: User):
        """Test retrieving the latest digest of a type."""
        now = datetime.now(timezone.utc)

        # Create multiple daily digests
        for i in range(3):
            period_start = now - timedelta(days=i + 1)
            period_end = now - timedelta(days=i)

            digest_data = NotificationDigestBase(
                digest_type="daily",
                period_start=period_start,
                period_end=period_end,
                total_notifications=10 * (i + 1),
            )
            crud.create_notification_digest(db, digest_data, test_user.id)

        latest = crud.get_latest_digest(db, test_user.id, "daily")

        assert latest is not None
        assert latest.total_notifications == 10  # Most recent one


class TestFocusSessionCRUD:
    """Test suite for FocusSession CRUD operations."""

    def test_create_focus_session(self, db: Session, test_user: User):
        """Test creating a focus session."""
        now = datetime.now(timezone.utc)

        session_data = FocusSessionCreate(
            start_time=now,
            planned_duration_minutes=60,
            session_type="deep_work",
            suppress_all=False,
            allow_urgent_only=True,
        )

        session = crud.create_focus_session(db, session_data, test_user.id)

        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.session_type == "deep_work"
        assert session.planned_duration_minutes == 60
        assert session.allow_urgent_only is True

    def test_get_active_focus_session(self, db: Session, test_user: User):
        """Test retrieving the active focus session."""
        now = datetime.now(timezone.utc)

        # Create an active session (no end_time)
        session_data = FocusSessionCreate(
            start_time=now,
            session_type="deep_work",
        )

        active_session = crud.create_focus_session(db, session_data, test_user.id)

        # Create an ended session
        ended_session_data = FocusSessionCreate(
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            session_type="meeting",
        )

        crud.create_focus_session(db, ended_session_data, test_user.id)

        # Get active session
        active = crud.get_active_focus_session(db, test_user.id)

        assert active is not None
        assert active.id == active_session.id
        assert active.end_time is None

    def test_end_focus_session(self, db: Session, test_user: User):
        """Test ending a focus session."""
        now = datetime.now(timezone.utc)

        session_data = FocusSessionCreate(
            start_time=now,
            session_type="deep_work",
        )

        session = crud.create_focus_session(db, session_data, test_user.id)

        assert session.end_time is None

        ended_session = crud.end_focus_session(db, session.id, test_user.id)

        assert ended_session is not None
        assert ended_session.end_time is not None


class TestResponseTemplateCRUD:
    """Test suite for ResponseTemplate CRUD operations."""

    def test_create_response_template(self, db: Session, test_user: User):
        """Test creating a response template."""
        template_data = ResponseTemplateCreate(
            name="Meeting Decline",
            description="Politely decline meeting invitations",
            category="meeting_response",
            template_text="Thank you for the invitation. Unfortunately, I won't be able to attend due to {{reason}}.",
            variables={"reason": "prior commitments"},
        )

        template = crud.create_response_template(db, template_data, test_user.id)

        assert template.id is not None
        assert template.user_id == test_user.id
        assert template.name == "Meeting Decline"
        assert template.category == "meeting_response"
        assert "{{reason}}" in template.template_text

    def test_get_response_templates_by_category(self, db: Session, test_user: User):
        """Test retrieving templates by category."""
        # Create templates in different categories
        for i, category in enumerate(["meeting_response", "project_update", "meeting_response"]):
            template_data = ResponseTemplateCreate(
                name=f"Template {i}",
                category=category,
                template_text=f"Template text {i}",
            )
            crud.create_response_template(db, template_data, test_user.id)

        # Get all templates
        all_templates = crud.get_response_templates(db, test_user.id)
        assert len(all_templates) == 3

        # Get only meeting_response templates
        meeting_templates = crud.get_response_templates(
            db, test_user.id, category="meeting_response"
        )
        assert len(meeting_templates) == 2

    def test_increment_template_usage(self, db: Session, test_user: User):
        """Test incrementing template usage counter."""
        template_data = ResponseTemplateCreate(
            name="Test Template",
            template_text="Test text",
        )

        template = crud.create_response_template(db, template_data, test_user.id)

        assert template.times_used == 0
        assert template.last_used is None

        # Increment usage
        success = crud.increment_template_usage(db, template.id, test_user.id)

        assert success is True

        db.refresh(template)
        assert template.times_used == 1
        assert template.last_used is not None

    def test_delete_response_template(self, db: Session, test_user: User):
        """Test deleting a response template."""
        template_data = ResponseTemplateCreate(
            name="To Delete",
            template_text="Delete me",
        )

        template = crud.create_response_template(db, template_data, test_user.id)
        template_id = template.id

        success = crud.delete_response_template(db, template_id, test_user.id)

        assert success is True

        deleted_template = crud.get_response_template(db, template_id, test_user.id)
        assert deleted_template is None
