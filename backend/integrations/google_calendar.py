"""Google Calendar integration for bidirectional task synchronization.

This module provides OAuth 2.0 authentication and bidirectional synchronization
between Charlee tasks and Google Calendar events.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from database.models import CalendarConnection, CalendarEvent, Task

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes required for calendar access
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class GoogleCalendarError(Exception):
    """Base exception for Google Calendar integration errors."""

    pass


class GoogleCalendarAuthError(GoogleCalendarError):
    """Exception raised for authentication errors."""

    pass


class GoogleCalendarSyncError(GoogleCalendarError):
    """Exception raised for synchronization errors."""

    pass


def get_oauth_flow(redirect_uri: str) -> Flow:
    """
    Create OAuth 2.0 flow for Google Calendar authentication.

    Args:
        redirect_uri: OAuth redirect URI after authorization

    Returns:
        Flow: Google OAuth 2.0 flow instance

    Raises:
        GoogleCalendarAuthError: If OAuth configuration is invalid
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise GoogleCalendarAuthError(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment"
        )

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        return flow
    except Exception as e:
        logger.error("Failed to create OAuth flow", extra={"error": str(e)}, exc_info=True)
        raise GoogleCalendarAuthError(f"Failed to create OAuth flow: {e}") from e


def get_authorization_url(redirect_uri: str, state: str) -> str:
    """
    Generate Google Calendar OAuth authorization URL.

    Args:
        redirect_uri: OAuth redirect URI
        state: CSRF protection state parameter

    Returns:
        str: Authorization URL for user to visit

    Raises:
        GoogleCalendarAuthError: If URL generation fails
    """
    try:
        flow = get_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=state,
            prompt="consent",  # Force consent to get refresh token
        )
        return auth_url
    except Exception as e:
        logger.error("Failed to generate authorization URL", extra={"error": str(e)}, exc_info=True)
        raise GoogleCalendarAuthError(f"Failed to generate authorization URL: {e}") from e


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: Authorization code from OAuth callback
        redirect_uri: OAuth redirect URI used in authorization

    Returns:
        dict: Token information including access_token, refresh_token, expires_in

    Raises:
        GoogleCalendarAuthError: If token exchange fails
    """
    try:
        flow = get_oauth_flow(redirect_uri)
        flow.fetch_token(code=code)

        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry,
        }
    except Exception as e:
        logger.error("Failed to exchange code for tokens", extra={"error": str(e)}, exc_info=True)
        raise GoogleCalendarAuthError(f"Failed to exchange code for tokens: {e}") from e


def refresh_access_token(connection: CalendarConnection) -> str:
    """
    Refresh expired access token using refresh token.

    Args:
        connection: CalendarConnection instance with refresh token

    Returns:
        str: New access token

    Raises:
        GoogleCalendarAuthError: If token refresh fails
    """
    if not connection.refresh_token:
        raise GoogleCalendarAuthError("No refresh token available")

    try:
        credentials = Credentials(
            token=connection.access_token,
            refresh_token=connection.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        )

        credentials.refresh(Request())

        connection.access_token = credentials.token
        if credentials.expiry:
            connection.token_expires_at = credentials.expiry.replace(tzinfo=timezone.utc)

        logger.info(
            "Access token refreshed successfully",
            extra={"connection_id": connection.id, "user_id": connection.user_id},
        )

        return credentials.token

    except Exception as e:
        logger.error(
            "Failed to refresh access token",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarAuthError(f"Failed to refresh access token: {e}") from e


def get_calendar_service(connection: CalendarConnection):
    """
    Get authenticated Google Calendar API service.

    Args:
        connection: CalendarConnection with valid credentials

    Returns:
        Resource: Google Calendar API service instance

    Raises:
        GoogleCalendarAuthError: If service creation fails
    """
    try:
        # Refresh token if expired
        if connection.is_token_expired():
            refresh_access_token(connection)

        credentials = Credentials(
            token=connection.access_token,
            refresh_token=connection.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        )

        service = build("calendar", "v3", credentials=credentials)
        return service

    except Exception as e:
        logger.error(
            "Failed to create calendar service",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarAuthError(f"Failed to create calendar service: {e}") from e


def list_calendars(connection: CalendarConnection) -> list[dict[str, Any]]:
    """
    List all calendars accessible to the user.

    Args:
        connection: CalendarConnection with valid credentials

    Returns:
        list: List of calendar dictionaries with id, summary, description

    Raises:
        GoogleCalendarSyncError: If listing fails
    """
    try:
        service = get_calendar_service(connection)
        calendar_list = service.calendarList().list().execute()

        calendars = []
        for calendar_entry in calendar_list.get("items", []):
            calendars.append(
                {
                    "id": calendar_entry["id"],
                    "summary": calendar_entry.get("summary", ""),
                    "description": calendar_entry.get("description", ""),
                    "primary": calendar_entry.get("primary", False),
                    "access_role": calendar_entry.get("accessRole", ""),
                }
            )

        logger.info(
            "Listed calendars successfully",
            extra={"connection_id": connection.id, "count": len(calendars)},
        )

        return calendars

    except HttpError as e:
        logger.error(
            "HTTP error listing calendars",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to list calendars: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to list calendars",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to list calendars: {e}") from e


def get_calendar_info(access_token: str, calendar_id: str = "primary") -> dict[str, Any]:
    """
    Get information about a specific calendar.

    Args:
        access_token: Google OAuth access token
        calendar_id: Calendar ID to fetch (default: "primary")

    Returns:
        dict: Calendar information with id, summary, etc.

    Raises:
        GoogleCalendarSyncError: If fetching calendar info fails
    """
    try:
        credentials = Credentials(
            token=access_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        )

        service = build("calendar", "v3", credentials=credentials)
        calendar = service.calendars().get(calendarId=calendar_id).execute()

        return {
            "id": calendar.get("id"),
            "summary": calendar.get("summary", ""),
            "description": calendar.get("description", ""),
            "timeZone": calendar.get("timeZone", ""),
        }

    except HttpError as e:
        logger.error(
            "HTTP error getting calendar info",
            extra={"calendar_id": calendar_id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to get calendar info: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to get calendar info",
            extra={"calendar_id": calendar_id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to get calendar info: {e}") from e


def sync_task_to_calendar(connection: CalendarConnection, task: Task, db: Session) -> CalendarEvent:
    """
    Sync Charlee task to Google Calendar event.

    Args:
        connection: CalendarConnection to use
        task: Task to sync
        db: Database session

    Returns:
        CalendarEvent: Created or updated calendar event

    Raises:
        GoogleCalendarSyncError: If sync fails
    """
    try:
        service = get_calendar_service(connection)

        # Check if event already exists
        existing_event = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.connection_id == connection.id,
                CalendarEvent.task_id == task.id,
            )
            .first()
        )

        # Prepare event data
        event_body = {
            "summary": task.descricao,
            "description": f"Charlee Task ID: {task.id}",
            "start": {},
            "end": {},
        }

        # Handle different task types
        if task.tipo == "fixed_appointment" and task.deadline:
            # Fixed appointment - use deadline as date
            event_body["start"]["date"] = task.deadline.isoformat()
            event_body["end"]["date"] = task.deadline.isoformat()
        elif task.deadline:
            # Regular task - create all-day event on deadline
            event_body["start"]["date"] = task.deadline.isoformat()
            event_body["end"]["date"] = task.deadline.isoformat()
        else:
            # No deadline - skip sync
            logger.warning(
                "Task has no deadline, skipping sync",
                extra={"task_id": task.id, "connection_id": connection.id},
            )
            raise GoogleCalendarSyncError("Task has no deadline")

        if existing_event:
            # Update existing event
            service.events().update(
                calendarId=connection.calendar_id,
                eventId=existing_event.external_event_id,
                body=event_body,
            ).execute()

            existing_event.title = task.descricao
            existing_event.charlee_modified_at = datetime.now(timezone.utc)
            existing_event.last_modified_at = datetime.now(timezone.utc)

            logger.info(
                "Updated calendar event",
                extra={
                    "event_id": existing_event.id,
                    "task_id": task.id,
                    "connection_id": connection.id,
                },
            )

            return existing_event
        else:
            # Create new event
            created_event = (
                service.events()
                .insert(calendarId=connection.calendar_id, body=event_body)
                .execute()
            )

            # Create CalendarEvent record
            calendar_event = CalendarEvent(
                connection_id=connection.id,
                user_id=connection.user_id,
                external_event_id=created_event["id"],
                task_id=task.id,
                title=task.descricao,
                description=event_body.get("description"),
                start_time=datetime.fromisoformat(
                    created_event["start"].get("dateTime", created_event["start"]["date"])
                ),
                end_time=datetime.fromisoformat(
                    created_event["end"].get("dateTime", created_event["end"]["date"])
                ),
                all_day=True,
                status="confirmed",
                source="charlee",
                charlee_modified_at=datetime.now(timezone.utc),
                last_modified_at=datetime.now(timezone.utc),
            )

            db.add(calendar_event)
            db.flush()

            logger.info(
                "Created calendar event",
                extra={
                    "event_id": calendar_event.id,
                    "task_id": task.id,
                    "connection_id": connection.id,
                },
            )

            return calendar_event

    except HttpError as e:
        logger.error(
            "HTTP error syncing task to calendar",
            extra={"task_id": task.id, "connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to sync task to calendar: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to sync task to calendar",
            extra={"task_id": task.id, "connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to sync task to calendar: {e}") from e


def sync_calendar_to_tasks(
    connection: CalendarConnection, db: Session, time_min: Optional[datetime] = None
) -> list[CalendarEvent]:
    """
    Sync Google Calendar events to Charlee tasks.

    Args:
        connection: CalendarConnection to use
        db: Database session
        time_min: Minimum time for events to sync (default: now)

    Returns:
        list[CalendarEvent]: List of synced calendar events

    Raises:
        GoogleCalendarSyncError: If sync fails
    """
    try:
        service = get_calendar_service(connection)

        # Default to events from now onwards
        if time_min is None:
            time_min = datetime.now(timezone.utc)

        # Fetch events from Google Calendar
        events_result = (
            service.events()
            .list(
                calendarId=connection.calendar_id,
                timeMin=time_min.isoformat(),
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        synced_events = []

        for event in events:
            # Skip events without start time
            if "start" not in event:
                continue

            # Check if event already exists
            existing_event = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.connection_id == connection.id,
                    CalendarEvent.external_event_id == event["id"],
                )
                .first()
            )

            # Parse event times
            start_str = event["start"].get("dateTime", event["start"].get("date"))
            end_str = event["end"].get("dateTime", event["end"].get("date"))
            all_day = "date" in event["start"]

            if existing_event:
                # Update existing event
                existing_event.title = event.get("summary", "Untitled")
                existing_event.description = event.get("description")
                existing_event.start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                existing_event.end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                existing_event.all_day = all_day
                existing_event.location = event.get("location")
                existing_event.status = event.get("status", "confirmed")
                existing_event.external_modified_at = datetime.now(timezone.utc)
                existing_event.last_modified_at = datetime.now(timezone.utc)

                synced_events.append(existing_event)
            else:
                # Create new event
                calendar_event = CalendarEvent(
                    connection_id=connection.id,
                    user_id=connection.user_id,
                    external_event_id=event["id"],
                    title=event.get("summary", "Untitled"),
                    description=event.get("description"),
                    start_time=datetime.fromisoformat(start_str.replace("Z", "+00:00")),
                    end_time=datetime.fromisoformat(end_str.replace("Z", "+00:00")),
                    all_day=all_day,
                    location=event.get("location"),
                    status=event.get("status", "confirmed"),
                    source="external",
                    external_modified_at=datetime.now(timezone.utc),
                    last_modified_at=datetime.now(timezone.utc),
                )

                db.add(calendar_event)
                synced_events.append(calendar_event)

        db.flush()

        logger.info(
            "Synced calendar events to Charlee",
            extra={"connection_id": connection.id, "count": len(synced_events)},
        )

        return synced_events

    except HttpError as e:
        logger.error(
            "HTTP error syncing calendar to tasks",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to sync calendar to tasks: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to sync calendar to tasks",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to sync calendar to tasks: {e}") from e


def setup_webhook(connection: CalendarConnection, webhook_url: str) -> dict[str, Any]:
    """
    Setup webhook for real-time calendar change notifications.

    Args:
        connection: CalendarConnection to setup webhook for
        webhook_url: HTTPS URL to receive webhook notifications

    Returns:
        dict: Webhook configuration with id and expiration

    Raises:
        GoogleCalendarSyncError: If webhook setup fails
    """
    try:
        service = get_calendar_service(connection)

        # Create watch request
        watch_body = {
            "id": f"charlee-webhook-{connection.id}",
            "type": "web_hook",
            "address": webhook_url,
        }

        watch_response = (
            service.events().watch(calendarId=connection.calendar_id, body=watch_body).execute()
        )

        # Update connection with webhook info
        connection.webhook_id = watch_response["id"]
        connection.webhook_expires_at = datetime.fromtimestamp(
            int(watch_response["expiration"]) / 1000, tz=timezone.utc
        )

        logger.info(
            "Webhook setup successfully",
            extra={
                "connection_id": connection.id,
                "webhook_id": connection.webhook_id,
                "expires_at": connection.webhook_expires_at,
            },
        )

        return {
            "webhook_id": watch_response["id"],
            "resource_id": watch_response["resourceId"],
            "expiration": watch_response["expiration"],
        }

    except HttpError as e:
        logger.error(
            "HTTP error setting up webhook",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to setup webhook: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to setup webhook",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise GoogleCalendarSyncError(f"Failed to setup webhook: {e}") from e
