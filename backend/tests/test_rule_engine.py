"""Tests for RuleEngine - automated notification filtering."""

import pytest
from sqlalchemy.orm import Session

from database.models import Notification, NotificationRule, User
from services.rule_engine import RuleEngine


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


@pytest.fixture
def test_notification(db: Session, test_user: User) -> Notification:
    """Create a test notification."""
    notification = Notification(
        user_id=test_user.id,
        type="email",
        title="Job Opportunity: Senior Python Developer",
        message="We have an exciting opportunity for you...",
        extra_data={
            "sender": "recruiter@company.com",
            "subject": "Job Opportunity: Senior Python Developer",
        },
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@pytest.fixture
def spam_rule(db: Session, test_user: User) -> NotificationRule:
    """Create a spam filtering rule."""
    rule = NotificationRule(
        user_id=test_user.id,
        name="Filter recruiter spam",
        description="Auto-archive job opportunity emails",
        enabled=True,
        priority=10,
        conditions={
            "all": [
                {"field": "extra_data.sender", "operator": "contains", "value": "recruiter"},
                {"field": "extra_data.subject", "operator": "contains", "value": "job opportunity"},
            ]
        },
        actions=[
            {"type": "classify", "categoria": "spam"},
            {"type": "archive"},
        ],
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


class TestRuleEngine:
    """Test suite for RuleEngine."""

    def test_evaluate_simple_condition_match(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that a simple condition matches correctly."""
        engine = RuleEngine(db, test_user.id)

        conditions = {
            "all": [{"field": "extra_data.sender", "operator": "contains", "value": "recruiter"}]
        }

        result = engine._evaluate_conditions(test_notification, conditions)
        assert result is True

    def test_evaluate_simple_condition_no_match(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that a simple condition doesn't match when it shouldn't."""
        engine = RuleEngine(db, test_user.id)

        conditions = {
            "all": [{"field": "extra_data.sender", "operator": "contains", "value": "admin"}]
        }

        result = engine._evaluate_conditions(test_notification, conditions)
        assert result is False

    def test_evaluate_multiple_conditions_all(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that multiple conditions with ALL logic work correctly."""
        engine = RuleEngine(db, test_user.id)

        conditions = {
            "all": [
                {"field": "extra_data.sender", "operator": "contains", "value": "recruiter"},
                {"field": "extra_data.subject", "operator": "contains", "value": "job"},
            ]
        }

        result = engine._evaluate_conditions(test_notification, conditions)
        assert result is True

    def test_evaluate_multiple_conditions_any(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that multiple conditions with ANY logic work correctly."""
        engine = RuleEngine(db, test_user.id)

        conditions = {
            "any": [
                {"field": "extra_data.sender", "operator": "contains", "value": "admin"},
                {"field": "extra_data.subject", "operator": "contains", "value": "job"},
            ]
        }

        result = engine._evaluate_conditions(test_notification, conditions)
        assert result is True  # Should match because subject contains "job"

    def test_operator_equals(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test equals operator."""
        engine = RuleEngine(db, test_user.id)

        assert engine._apply_operator("test", "equals", "test") is True
        assert engine._apply_operator("test", "equals", "Test") is True  # Case insensitive
        assert engine._apply_operator("test", "equals", "other") is False

    def test_operator_contains(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test contains operator."""
        engine = RuleEngine(db, test_user.id)

        assert engine._apply_operator("hello world", "contains", "world") is True
        assert engine._apply_operator("hello world", "contains", "WORLD") is True
        assert engine._apply_operator("hello world", "contains", "foo") is False

    def test_operator_starts_with(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test starts_with operator."""
        engine = RuleEngine(db, test_user.id)

        assert engine._apply_operator("hello world", "starts_with", "hello") is True
        assert engine._apply_operator("hello world", "starts_with", "world") is False

    def test_operator_numeric_comparison(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test numeric comparison operators."""
        engine = RuleEngine(db, test_user.id)

        assert engine._apply_operator(10, ">", 5) is True
        assert engine._apply_operator(10, "<", 5) is False
        assert engine._apply_operator(10, ">=", 10) is True
        assert engine._apply_operator(10, "<=", 10) is True

    def test_execute_classify_action(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that classify action works."""
        engine = RuleEngine(db, test_user.id)

        actions = [{"type": "classify", "categoria": "spam"}]

        executed = engine._execute_actions(test_notification, actions)

        assert len(executed) == 1
        assert executed[0]["type"] == "classify"
        assert test_notification.categoria == "spam"

    def test_execute_archive_action(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that archive action works."""
        engine = RuleEngine(db, test_user.id)

        actions = [{"type": "archive"}]

        executed = engine._execute_actions(test_notification, actions)

        assert len(executed) == 1
        assert executed[0]["type"] == "archive"
        assert test_notification.arquivada is True

    def test_execute_multiple_actions(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that multiple actions execute in order."""
        engine = RuleEngine(db, test_user.id)

        actions = [
            {"type": "classify", "categoria": "spam"},
            {"type": "set_priority", "prioridade": 1},
            {"type": "archive"},
        ]

        executed = engine._execute_actions(test_notification, actions)

        assert len(executed) == 3
        assert test_notification.categoria == "spam"
        assert test_notification.prioridade == 1
        assert test_notification.arquivada is True

    def test_evaluate_full_rule(
        self,
        db: Session,
        test_user: User,
        test_notification: Notification,
        spam_rule: NotificationRule,
    ):
        """Test evaluation of a complete rule."""
        engine = RuleEngine(db, test_user.id)

        actions = engine.evaluate_notification(test_notification)

        assert len(actions) > 0
        assert test_notification.categoria == "spam"
        assert test_notification.arquivada is True

        # Check that rule statistics were updated
        db.refresh(spam_rule)
        assert spam_rule.times_triggered == 1
        assert spam_rule.last_triggered is not None

    def test_rule_priority_ordering(self, db: Session, test_user: User):
        """Test that rules execute in priority order."""
        # Create two rules with different priorities
        rule_low = NotificationRule(
            user_id=test_user.id,
            name="Low priority rule",
            enabled=True,
            priority=1,
            conditions={"all": [{"field": "type", "operator": "equals", "value": "email"}]},
            actions=[{"type": "set_priority", "prioridade": 5}],
        )

        rule_high = NotificationRule(
            user_id=test_user.id,
            name="High priority rule",
            enabled=True,
            priority=10,
            conditions={"all": [{"field": "type", "operator": "equals", "value": "email"}]},
            actions=[{"type": "classify", "categoria": "importante"}],
        )

        db.add(rule_low)
        db.add(rule_high)
        db.commit()

        notification = Notification(
            user_id=test_user.id,
            type="email",
            title="Test",
            message="Test message",
        )
        db.add(notification)
        db.commit()

        engine = RuleEngine(db, test_user.id)
        actions = engine.evaluate_notification(notification)

        # High priority rule should execute first
        assert len(actions) == 2
        assert notification.categoria == "importante"
        assert notification.prioridade == 5

    def test_disabled_rule_not_executed(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test that disabled rules are not executed."""
        rule = NotificationRule(
            user_id=test_user.id,
            name="Disabled rule",
            enabled=False,  # Disabled
            priority=10,
            conditions={"all": [{"field": "type", "operator": "equals", "value": "email"}]},
            actions=[{"type": "classify", "categoria": "spam"}],
        )
        db.add(rule)
        db.commit()

        engine = RuleEngine(db, test_user.id)
        actions = engine.evaluate_notification(test_notification)

        assert len(actions) == 0
        assert test_notification.categoria is None

    def test_test_rule_method(
        self,
        db: Session,
        test_user: User,
        test_notification: Notification,
        spam_rule: NotificationRule,
    ):
        """Test the test_rule method that doesn't execute actions."""
        engine = RuleEngine(db, test_user.id)

        result = engine.test_rule(spam_rule.id, test_notification.id)

        assert result["matches"] is True
        assert len(result["actions_that_would_execute"]) == 2

        # Verify actions were NOT actually executed
        db.refresh(test_notification)
        assert test_notification.categoria is None
        assert test_notification.arquivada is False

        # Verify rule statistics were NOT updated
        db.refresh(spam_rule)
        assert spam_rule.times_triggered == 0

    def test_batch_processing(
        self, db: Session, test_user: User, spam_rule: NotificationRule
    ):
        """Test batch processing of multiple notifications."""
        # Create multiple notifications
        notifications = []
        for i in range(5):
            notif = Notification(
                user_id=test_user.id,
                type="email",
                title=f"Job Opportunity #{i}",
                message="Test message",
                extra_data={
                    "sender": "recruiter@company.com",
                    "subject": f"Job Opportunity #{i}",
                },
            )
            db.add(notif)
            notifications.append(notif)

        db.commit()

        notification_ids = [n.id for n in notifications]

        engine = RuleEngine(db, test_user.id)
        result = engine.process_batch(notification_ids)

        assert result["processed"] == 5
        assert result["actions_executed"] > 0

        # Verify all were processed
        for notif in notifications:
            db.refresh(notif)
            assert notif.categoria == "spam"
            assert notif.arquivada is True

    def test_field_extraction_nested(
        self, db: Session, test_user: User, test_notification: Notification
    ):
        """Test extraction of nested fields."""
        engine = RuleEngine(db, test_user.id)

        # Test direct field
        value = engine._get_field_value(test_notification, "type")
        assert value == "email"

        # Test nested field in extra_data
        value = engine._get_field_value(test_notification, "extra_data.sender")
        assert value == "recruiter@company.com"

        # Test non-existent field
        value = engine._get_field_value(test_notification, "extra_data.nonexistent")
        assert value is None
