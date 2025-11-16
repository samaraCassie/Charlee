"""Tests for Calendar Integration Models and Schemas."""

import pytest
from datetime import datetime, timedelta, timezone
from database.models import CalendarConnection, CalendarEvent, CalendarSyncLog, CalendarConflict
from database.schemas import (
    CalendarConnectionCreate,
    CalendarConnectionUpdate,
    CalendarEventCreate,
    CalendarEventUpdate,
)


class TestCalendarConnectionModel:
    """Test suite for CalendarConnection model."""

    def test_create_google_connection(self, db, sample_user):
        """Should create a Google Calendar connection."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            calendar_name="My Google Calendar",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            sync_enabled=True,
            sync_direction="both",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)

        assert connection.id is not None
        assert connection.provider == "google"
        assert connection.calendar_id == "primary"
        assert connection.sync_enabled is True
        assert connection.created_at is not None

    def test_create_microsoft_connection(self, db, sample_user):
        """Should create a Microsoft Calendar connection."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="microsoft",
            calendar_id="AAMkADQ1234567890",
            calendar_name="Work Calendar",
            access_token="test_ms_token",
            refresh_token="test_ms_refresh",
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            sync_enabled=True,
            sync_direction="both",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)

        assert connection.id is not None
        assert connection.provider == "microsoft"
        assert connection.sync_direction == "both"

    def test_is_token_expired_future(self, db, sample_user):
        """Should return False for token expiring in the future."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(connection)
        db.commit()

        assert connection.is_token_expired() is False

    def test_is_token_expired_past(self, db, sample_user):
        """Should return True for expired token."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
            token_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.add(connection)
        db.commit()

        assert connection.is_token_expired() is True

    def test_needs_sync_never_synced(self, db, sample_user):
        """Should return True for connection never synced."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
            last_sync_at=None,
        )
        db.add(connection)
        db.commit()

        assert connection.needs_sync() is True

    def test_needs_sync_recently_synced(self, db, sample_user):
        """Should return False for recently synced connection."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
            last_sync_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        db.add(connection)
        db.commit()

        assert connection.needs_sync(sync_interval_minutes=15) is False

    def test_needs_sync_old_sync(self, db, sample_user):
        """Should return True for connection with old sync."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
            last_sync_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        )
        db.add(connection)
        db.commit()

        assert connection.needs_sync(sync_interval_minutes=15) is True


class TestCalendarEventModel:
    """Test suite for CalendarEvent model."""

    @pytest.fixture
    def sample_calendar_connection(self, db, sample_user):
        """Create a sample calendar connection."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection

    def test_create_calendar_event(self, db, sample_user, sample_calendar_connection):
        """Should create a calendar event."""
        event = CalendarEvent(
            connection_id=sample_calendar_connection.id,
            user_id=sample_user.id,
            external_event_id="google_event_123",
            title="Team Meeting",
            description="Weekly sync meeting",
            start_time=datetime.now(timezone.utc) + timedelta(hours=2),
            end_time=datetime.now(timezone.utc) + timedelta(hours=3),
            source="external",
            status="confirmed",
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.id is not None
        assert event.title == "Team Meeting"
        assert event.source == "external"
        assert event.status == "confirmed"

    def test_event_to_dict(self, db, sample_user, sample_calendar_connection):
        """Should convert event to dictionary."""
        event = CalendarEvent(
            connection_id=sample_calendar_connection.id,
            user_id=sample_user.id,
            external_event_id="google_event_456",
            title="Project Review",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            source="charlee",
        )
        db.add(event)
        db.commit()

        event_dict = event.to_dict()
        assert event_dict["title"] == "Project Review"
        assert event_dict["source"] == "charlee"
        assert "start_time" in event_dict
        assert "end_time" in event_dict


class TestCalendarSyncLogModel:
    """Test suite for CalendarSyncLog model."""

    @pytest.fixture
    def sample_calendar_connection(self, db, sample_user):
        """Create a sample calendar connection."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection

    def test_create_sync_log(self, db, sample_user, sample_calendar_connection):
        """Should create a sync log."""
        sync_log = CalendarSyncLog(
            connection_id=sample_calendar_connection.id,
            user_id=sample_user.id,
            sync_type="scheduled",
            direction="both",
            status="started",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)

        assert sync_log.id is not None
        assert sync_log.sync_type == "scheduled"
        assert sync_log.status == "started"

    def test_mark_completed_success(self, db, sample_user, sample_calendar_connection):
        """Should mark sync log as completed successfully."""
        sync_log = CalendarSyncLog(
            connection_id=sample_calendar_connection.id,
            user_id=sample_user.id,
            sync_type="manual",
            direction="both",
            status="started",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sync_log)
        db.commit()

        sync_log.mark_completed("success")
        db.commit()

        assert sync_log.status == "success"
        assert sync_log.completed_at is not None
        assert sync_log.duration_seconds is not None
        assert sync_log.duration_seconds >= 0

    def test_mark_completed_failed(self, db, sample_user, sample_calendar_connection):
        """Should mark sync log as failed."""
        sync_log = CalendarSyncLog(
            connection_id=sample_calendar_connection.id,
            user_id=sample_user.id,
            sync_type="webhook",
            direction="from_calendar",
            status="started",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sync_log)
        db.commit()

        sync_log.status = "failed"
        sync_log.error_message = "Token expired"
        sync_log.mark_completed("failed")
        db.commit()

        assert sync_log.status == "failed"
        assert sync_log.error_message == "Token expired"
        assert sync_log.completed_at is not None


class TestCalendarConflictModel:
    """Test suite for CalendarConflict model."""

    @pytest.fixture
    def sample_calendar_event(self, db, sample_user):
        """Create a sample calendar event."""
        connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="primary",
            access_token="token",
        )
        db.add(connection)
        db.commit()

        event = CalendarEvent(
            connection_id=connection.id,
            user_id=sample_user.id,
            external_event_id="event_789",
            title="Conflicting Event",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            source="external",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def test_create_conflict(self, db, sample_user, sample_calendar_event):
        """Should create a calendar conflict."""
        conflict = CalendarConflict(
            event_id=sample_calendar_event.id,
            user_id=sample_user.id,
            conflict_type="both_modified",
            charlee_version={"title": "Charlee Version"},
            external_version={"title": "External Version"},
            resolution_strategy="last_modified_wins",
            status="detected",
        )
        db.add(conflict)
        db.commit()
        db.refresh(conflict)

        assert conflict.id is not None
        assert conflict.conflict_type == "both_modified"
        assert conflict.status == "detected"

    def test_resolve_conflict(self, db, sample_user, sample_calendar_event):
        """Should resolve a conflict."""
        conflict = CalendarConflict(
            event_id=sample_calendar_event.id,
            user_id=sample_user.id,
            conflict_type="both_modified",
            charlee_version={"title": "Charlee"},
            external_version={"title": "External"},
            resolution_strategy="charlee_wins",
            status="detected",
        )
        db.add(conflict)
        db.commit()

        resolved_version = {"title": "Charlee"}
        conflict.resolve(resolved_version, "system_charlee")
        db.commit()

        assert conflict.status == "resolved"
        assert conflict.resolved_version == resolved_version
        assert conflict.resolved_by == "system_charlee"
        assert conflict.resolved_at is not None


class TestCalendarSchemas:
    """Test suite for Calendar Pydantic schemas."""

    def test_calendar_connection_create_schema(self):
        """Should validate CalendarConnectionCreate schema."""
        data = CalendarConnectionCreate(
            provider="google",
            calendar_id="primary",
            calendar_name="Work Calendar",
            access_token="token123",
            refresh_token="refresh123",
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            sync_enabled=True,
            sync_direction="both",
        )

        assert data.provider == "google"
        assert data.sync_direction == "both"
        assert data.sync_enabled is True

    def test_calendar_connection_update_schema(self):
        """Should validate CalendarConnectionUpdate schema."""
        data = CalendarConnectionUpdate(
            sync_enabled=False,
            sync_direction="to_calendar",
        )

        assert data.sync_enabled is False
        assert data.sync_direction == "to_calendar"

    def test_calendar_event_create_schema(self):
        """Should validate CalendarEventCreate schema."""
        data = CalendarEventCreate(
            connection_id=1,
            external_event_id="event_123",
            title="Meeting",
            description="Project discussion",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            source="charlee",
        )

        assert data.title == "Meeting"
        assert data.source == "charlee"

    def test_calendar_event_update_schema(self):
        """Should validate CalendarEventUpdate schema."""
        data = CalendarEventUpdate(
            title="Updated Meeting",
            start_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        assert data.title == "Updated Meeting"
