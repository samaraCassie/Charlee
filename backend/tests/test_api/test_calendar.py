"""Tests for Calendar API Routes."""

import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from database.models import CalendarConnection, CalendarEvent


@pytest.fixture
def sample_calendar_connection(db, sample_user):
    """Create a sample calendar connection."""
    connection = CalendarConnection(
        user_id=sample_user.id,
        provider="google",
        calendar_id="primary",
        calendar_name="My Calendar",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        sync_enabled=True,
        sync_direction="both",
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@pytest.fixture
def sample_calendar_event(db, sample_user, sample_calendar_connection):
    """Create a sample calendar event."""
    event = CalendarEvent(
        connection_id=sample_calendar_connection.id,
        user_id=sample_user.id,
        external_event_id="external_123",
        title="Team Meeting",
        description="Weekly sync",
        start_time=datetime.now(timezone.utc) + timedelta(hours=2),
        end_time=datetime.now(timezone.utc) + timedelta(hours=3),
        source="external",
        status="confirmed",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


class TestGoogleCalendarOAuth:
    """Test suite for Google Calendar OAuth endpoints."""

    def test_get_google_auth_url(self, client, auth_headers):
        """Should generate Google OAuth authorization URL."""
        response = client.get(
            "/api/v1/calendar/connect/google/auth-url",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "auth_url" in data
        assert "state" in data
        assert "https://accounts.google.com/o/oauth2" in data["auth_url"]

    def test_get_google_auth_url_unauthenticated(self, client):
        """Should return 403 for unauthenticated request."""
        response = client.get("/api/v1/calendar/connect/google/auth-url")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("api.routes.calendar.google_calendar.exchange_code_for_tokens")
    @patch("api.routes.calendar.google_calendar.get_calendar_info")
    def test_connect_google_calendar_success(
        self,
        mock_get_calendar,
        mock_exchange_tokens,
        client,
        auth_headers,
    ):
        """Should successfully connect Google Calendar."""
        # Mock OAuth token exchange
        mock_exchange_tokens.return_value = {
            "access_token": "ya29.test_access_token",
            "refresh_token": "1//test_refresh_token",
            "expires_in": 3600,
        }

        # Mock calendar info
        mock_get_calendar.return_value = {
            "id": "primary",
            "summary": "My Google Calendar",
        }

        response = client.post(
            "/api/v1/calendar/connect/google",
            headers=auth_headers,
            json={
                "code": "test_auth_code",
                "state": "test_state",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["provider"] == "google"
        assert data["calendar_id"] == "primary"
        assert data["sync_enabled"] is True


class TestMicrosoftCalendarOAuth:
    """Test suite for Microsoft Calendar OAuth endpoints."""

    def test_get_microsoft_auth_url(self, client, auth_headers):
        """Should generate Microsoft OAuth authorization URL."""
        response = client.get(
            "/api/v1/calendar/connect/microsoft/auth-url",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "auth_url" in data
        assert "state" in data
        assert "login.microsoftonline.com" in data["auth_url"]

    @pytest.mark.asyncio
    @patch("api.routes.calendar.microsoft_calendar.exchange_code_for_tokens")
    @patch("api.routes.calendar.microsoft_calendar.get_calendar_info")
    async def test_connect_microsoft_calendar_success(
        self,
        mock_get_calendar,
        mock_exchange_tokens,
        client,
        auth_headers,
    ):
        """Should successfully connect Microsoft Calendar."""
        # Mock OAuth token exchange
        mock_exchange_tokens.return_value = {
            "access_token": "EwAoA8l6BAAU...",
            "refresh_token": "MCabIRmfGO...",
            "expires_in": 3600,
        }

        # Mock calendar info
        mock_get_calendar.return_value = {
            "id": "AAMkADQ1234567890",
            "name": "Calendar",
        }

        response = client.post(
            "/api/v1/calendar/connect/microsoft",
            headers=auth_headers,
            json={
                "code": "test_ms_code",
                "state": "test_state",
            },
        )

        # Note: This might need async handling depending on your FastAPI setup
        assert response.status_code == status.HTTP_201_CREATED


class TestCalendarConnectionManagement:
    """Test suite for calendar connection CRUD operations."""

    def test_list_connections(self, client, auth_headers, sample_calendar_connection):
        """Should list user's calendar connections."""
        response = client.get(
            "/api/v1/calendar/connections",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["connections"]) >= 1
        assert data["connections"][0]["provider"] == "google"

    def test_list_connections_empty(self, client, auth_headers):
        """Should return empty list when no connections."""
        response = client.get(
            "/api/v1/calendar/connections",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["connections"]) == 0

    def test_get_connection(self, client, auth_headers, sample_calendar_connection):
        """Should get specific calendar connection."""
        response = client.get(
            f"/api/v1/calendar/connections/{sample_calendar_connection.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_calendar_connection.id
        assert data["provider"] == "google"

    def test_get_connection_not_found(self, client, auth_headers):
        """Should return 404 for non-existent connection."""
        response = client.get(
            "/api/v1/calendar/connections/99999",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_connection_unauthorized(self, client, auth_headers, db):
        """Should return 403 for accessing another user's connection."""
        from database.models import User, CalendarConnection
        from api.auth.password import hash_password

        # Create another user's connection
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=hash_password("Pass123"),
        )
        db.add(other_user)
        db.commit()

        other_connection = CalendarConnection(
            user_id=other_user.id,
            provider="google",
            calendar_id="other_calendar",
            access_token="token",
        )
        db.add(other_connection)
        db.commit()

        response = client.get(
            f"/api/v1/calendar/connections/{other_connection.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_connection(self, client, auth_headers, sample_calendar_connection):
        """Should update calendar connection settings."""
        response = client.put(
            f"/api/v1/calendar/connections/{sample_calendar_connection.id}",
            headers=auth_headers,
            json={
                "sync_enabled": False,
                "sync_direction": "to_calendar",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sync_enabled"] is False
        assert data["sync_direction"] == "to_calendar"

    def test_delete_connection(self, client, auth_headers, sample_calendar_connection):
        """Should delete calendar connection."""
        response = client.delete(
            f"/api/v1/calendar/connections/{sample_calendar_connection.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/api/v1/calendar/connections/{sample_calendar_connection.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestCalendarEvents:
    """Test suite for calendar events endpoints."""

    def test_list_events(self, client, auth_headers, sample_calendar_event):
        """Should list user's calendar events."""
        response = client.get(
            "/api/v1/calendar/events",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["events"]) >= 1
        assert data["events"][0]["title"] == "Team Meeting"

    def test_list_events_with_date_range(self, client, auth_headers, sample_calendar_event):
        """Should filter events by date range."""
        start_date = datetime.now(timezone.utc).date()
        end_date = (datetime.now(timezone.utc) + timedelta(days=7)).date()

        response = client.get(
            f"/api/v1/calendar/events?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should include the event created 2 hours from now
        assert data["total"] >= 1

    def test_list_events_by_connection(
        self, client, auth_headers, sample_calendar_connection, sample_calendar_event
    ):
        """Should filter events by connection."""
        response = client.get(
            f"/api/v1/calendar/events?connection_id={sample_calendar_connection.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(
            event["connection_id"] == sample_calendar_connection.id for event in data["events"]
        )


class TestCalendarSync:
    """Test suite for calendar synchronization endpoints."""

    @patch("api.routes.calendar.sync_connection.delay")
    def test_trigger_manual_sync(
        self, mock_sync_task, client, auth_headers, sample_calendar_connection
    ):
        """Should trigger manual calendar sync."""
        # Mock Celery task
        mock_task = MagicMock()
        mock_task.id = "test_task_id"
        mock_sync_task.return_value = mock_task

        response = client.post(
            f"/api/v1/calendar/connections/{sample_calendar_connection.id}/sync",
            headers=auth_headers,
            json={"direction": "both"},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["message"] == "Sync started"
        assert "task_id" in data

        # Verify task was called
        mock_sync_task.assert_called_once()

    def test_trigger_sync_disabled_connection(self, client, auth_headers, db, sample_user):
        """Should return 400 for sync on disabled connection."""
        disabled_connection = CalendarConnection(
            user_id=sample_user.id,
            provider="google",
            calendar_id="disabled",
            access_token="token",
            sync_enabled=False,
        )
        db.add(disabled_connection)
        db.commit()

        response = client.post(
            f"/api/v1/calendar/connections/{disabled_connection.id}/sync",
            headers=auth_headers,
            json={"direction": "both"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCalendarConflicts:
    """Test suite for calendar conflict endpoints."""

    @pytest.fixture
    def sample_conflict(self, db, sample_user, sample_calendar_event):
        """Create a sample calendar conflict."""
        from database.models import CalendarConflict

        conflict = CalendarConflict(
            event_id=sample_calendar_event.id,
            user_id=sample_user.id,
            conflict_type="both_modified",
            charlee_version={"title": "Meeting (Charlee)"},
            external_version={"title": "Meeting (External)"},
            resolution_strategy="manual",
            status="detected",
        )
        db.add(conflict)
        db.commit()
        db.refresh(conflict)
        return conflict

    def test_list_conflicts(self, client, auth_headers, sample_conflict):
        """Should list calendar conflicts."""
        response = client.get(
            "/api/v1/calendar/conflicts",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["conflicts"]) >= 1
        assert data["conflicts"][0]["conflict_type"] == "both_modified"

    def test_list_unresolved_conflicts_only(self, client, auth_headers, sample_conflict):
        """Should filter unresolved conflicts."""
        response = client.get(
            "/api/v1/calendar/conflicts?status=detected",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(conflict["status"] == "detected" for conflict in data["conflicts"])

    def test_resolve_conflict_charlee_wins(self, client, auth_headers, sample_conflict, db):
        """Should resolve conflict with charlee_wins strategy."""
        response = client.post(
            f"/api/v1/calendar/conflicts/{sample_conflict.id}/resolve",
            headers=auth_headers,
            json={"resolution_strategy": "charlee_wins"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolution_strategy"] == "charlee_wins"

    def test_resolve_conflict_not_found(self, client, auth_headers):
        """Should return 404 for non-existent conflict."""
        response = client.post(
            "/api/v1/calendar/conflicts/99999/resolve",
            headers=auth_headers,
            json={"resolution_strategy": "charlee_wins"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCalendarWebhooks:
    """Test suite for calendar webhook endpoints."""

    @patch("api.routes.calendar.sync_connection.delay")
    def test_google_webhook_notification(self, mock_sync_task, client, sample_calendar_connection):
        """Should handle Google Calendar webhook notification."""
        # Mock Celery task
        mock_task = MagicMock()
        mock_task.id = "webhook_task_id"
        mock_sync_task.return_value = mock_task

        response = client.post(
            "/api/v1/calendar/webhooks/google",
            headers={
                "X-Goog-Channel-ID": str(sample_calendar_connection.id),
                "X-Goog-Resource-State": "update",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify sync was triggered
        mock_sync_task.assert_called_once()

    def test_google_webhook_sync_notification(self, client):
        """Should handle Google webhook sync verification."""
        response = client.post(
            "/api/v1/calendar/webhooks/google",
            headers={
                "X-Goog-Resource-State": "sync",
            },
        )

        # Sync notifications should be acknowledged
        assert response.status_code == status.HTTP_200_OK
