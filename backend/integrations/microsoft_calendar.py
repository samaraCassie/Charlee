"""Microsoft Graph (Outlook) Calendar integration for bidirectional task synchronization.

This module provides OAuth 2.0 authentication and bidirectional synchronization
between Charlee tasks and Microsoft Outlook/Office 365 calendar events.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
import msal
from sqlalchemy.orm import Session

from database.models import CalendarConnection, CalendarEvent, Task

logger = logging.getLogger(__name__)

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
AUTHORITY = "https://login.microsoftonline.com/common"

# OAuth 2.0 scopes required for calendar access
# Note: offline_access is reserved and automatically added by MSAL
SCOPES = [
    "Calendars.ReadWrite",
    "Calendars.ReadWrite.Shared",
]


class MicrosoftCalendarError(Exception):
    """Base exception for Microsoft Calendar integration errors."""

    pass


class MicrosoftCalendarAuthError(MicrosoftCalendarError):
    """Exception raised for authentication errors."""

    pass


class MicrosoftCalendarSyncError(MicrosoftCalendarError):
    """Exception raised for synchronization errors."""

    pass


def get_msal_app() -> msal.ConfidentialClientApplication:
    """
    Create MSAL (Microsoft Authentication Library) application.

    Returns:
        ConfidentialClientApplication: MSAL app instance

    Raises:
        MicrosoftCalendarAuthError: If MSAL configuration is invalid
    """
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise MicrosoftCalendarAuthError(
            "MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET must be set in environment"
        )

    try:
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=AUTHORITY,
            client_credential=client_secret,
        )
        return app
    except Exception as e:
        logger.error("Failed to create MSAL app", extra={"error": str(e)}, exc_info=True)
        raise MicrosoftCalendarAuthError(f"Failed to create MSAL app: {e}") from e


def get_authorization_url(redirect_uri: str, state: str) -> str:
    """
    Generate Microsoft OAuth authorization URL.

    Args:
        redirect_uri: OAuth redirect URI
        state: CSRF protection state parameter

    Returns:
        str: Authorization URL for user to visit

    Raises:
        MicrosoftCalendarAuthError: If URL generation fails
    """
    try:
        app = get_msal_app()
        auth_url = app.get_authorization_request_url(
            scopes=SCOPES,
            state=state,
            redirect_uri=redirect_uri,
        )
        return auth_url
    except Exception as e:
        logger.error("Failed to generate authorization URL", extra={"error": str(e)}, exc_info=True)
        raise MicrosoftCalendarAuthError(f"Failed to generate authorization URL: {e}") from e


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: Authorization code from OAuth callback
        redirect_uri: OAuth redirect URI used in authorization

    Returns:
        dict: Token information including access_token, refresh_token, expires_in

    Raises:
        MicrosoftCalendarAuthError: If token exchange fails
    """
    try:
        app = get_msal_app()
        result = app.acquire_token_by_authorization_code(
            code=code,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )

        if "error" in result:
            error_desc = result.get("error_description", result["error"])
            raise MicrosoftCalendarAuthError(f"Token exchange failed: {error_desc}")

        # Calculate expiry time
        expires_in = result.get("expires_in", 3600)
        expiry = datetime.now(timezone.utc).timestamp() + expires_in

        return {
            "access_token": result["access_token"],
            "refresh_token": result.get("refresh_token"),
            "expires_in": expires_in,
            "expiry": datetime.fromtimestamp(expiry, tz=timezone.utc),
            "scope": result.get("scope", ""),
        }
    except MicrosoftCalendarAuthError:
        raise
    except Exception as e:
        logger.error("Failed to exchange code for tokens", extra={"error": str(e)}, exc_info=True)
        raise MicrosoftCalendarAuthError(f"Failed to exchange code for tokens: {e}") from e


def refresh_access_token(connection: CalendarConnection) -> str:
    """
    Refresh expired access token using refresh token.

    Args:
        connection: CalendarConnection instance with refresh token

    Returns:
        str: New access token

    Raises:
        MicrosoftCalendarAuthError: If token refresh fails
    """
    if not connection.refresh_token:
        raise MicrosoftCalendarAuthError("No refresh token available")

    try:
        app = get_msal_app()
        result = app.acquire_token_by_refresh_token(
            refresh_token=connection.refresh_token,
            scopes=SCOPES,
        )

        if "error" in result:
            error_desc = result.get("error_description", result["error"])
            raise MicrosoftCalendarAuthError(f"Token refresh failed: {error_desc}")

        connection.access_token = result["access_token"]

        # Update refresh token if provided (some flows return new refresh token)
        if "refresh_token" in result:
            connection.refresh_token = result["refresh_token"]

        # Calculate and update expiry
        expires_in = result.get("expires_in", 3600)
        expiry = datetime.now(timezone.utc).timestamp() + expires_in
        connection.token_expires_at = datetime.fromtimestamp(expiry, tz=timezone.utc)

        logger.info(
            "Access token refreshed successfully",
            extra={"connection_id": connection.id, "user_id": connection.user_id},
        )

        return result["access_token"]

    except MicrosoftCalendarAuthError:
        raise
    except Exception as e:
        logger.error(
            "Failed to refresh access token",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarAuthError(f"Failed to refresh access token: {e}") from e


async def get_graph_client(connection: CalendarConnection) -> httpx.AsyncClient:
    """
    Get authenticated Microsoft Graph API client.

    Args:
        connection: CalendarConnection with valid credentials

    Returns:
        httpx.AsyncClient: Authenticated HTTP client for Graph API

    Raises:
        MicrosoftCalendarAuthError: If authentication fails
    """
    try:
        # Refresh token if expired
        if connection.is_token_expired():
            refresh_access_token(connection)

        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Content-Type": "application/json",
        }

        client = httpx.AsyncClient(
            base_url=GRAPH_API_ENDPOINT,
            headers=headers,
            timeout=30.0,
        )

        return client

    except Exception as e:
        logger.error(
            "Failed to create Graph API client",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarAuthError(f"Failed to create Graph API client: {e}") from e


async def list_calendars(connection: CalendarConnection) -> list[dict[str, Any]]:
    """
    List all calendars accessible to the user.

    Args:
        connection: CalendarConnection with valid credentials

    Returns:
        list: List of calendar dictionaries with id, name, description

    Raises:
        MicrosoftCalendarSyncError: If listing fails
    """
    try:
        client = await get_graph_client(connection)

        try:
            response = await client.get("/me/calendars")
            response.raise_for_status()

            data = response.json()
            calendars = []

            for calendar in data.get("value", []):
                calendars.append(
                    {
                        "id": calendar["id"],
                        "name": calendar.get("name", ""),
                        "description": calendar.get("description", ""),
                        "is_default": calendar.get("isDefaultCalendar", False),
                        "can_edit": calendar.get("canEdit", False),
                        "owner": calendar.get("owner", {}).get("name", ""),
                    }
                )

            logger.info(
                "Listed calendars successfully",
                extra={"connection_id": connection.id, "count": len(calendars)},
            )

            return calendars

        finally:
            await client.aclose()

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error listing calendars",
            extra={
                "connection_id": connection.id,
                "status_code": e.response.status_code,
                "error": str(e),
            },
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to list calendars: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to list calendars",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to list calendars: {e}") from e


async def sync_task_to_calendar(
    connection: CalendarConnection, task: Task, db: Session
) -> CalendarEvent:
    """
    Sync Charlee task to Microsoft Calendar event.

    Args:
        connection: CalendarConnection to use
        task: Task to sync
        db: Database session

    Returns:
        CalendarEvent: Created or updated calendar event

    Raises:
        MicrosoftCalendarSyncError: If sync fails
    """
    try:
        client = await get_graph_client(connection)

        try:
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
            event_body: dict[str, Any] = {
                "subject": task.descricao,
                "body": {
                    "contentType": "text",
                    "content": f"Charlee Task ID: {task.id}",
                },
                "isAllDay": True,
            }

            # Handle different task types
            if task.tipo == "fixed_appointment" and task.deadline:
                # Fixed appointment - use deadline as date
                event_body["start"] = {
                    "dateTime": task.deadline.isoformat(),
                    "timeZone": "UTC",
                }
                event_body["end"] = {
                    "dateTime": task.deadline.isoformat(),
                    "timeZone": "UTC",
                }
            elif task.deadline:
                # Regular task - create all-day event on deadline
                event_body["start"] = {
                    "dateTime": task.deadline.isoformat(),
                    "timeZone": "UTC",
                }
                event_body["end"] = {
                    "dateTime": task.deadline.isoformat(),
                    "timeZone": "UTC",
                }
            else:
                # No deadline - skip sync
                logger.warning(
                    "Task has no deadline, skipping sync",
                    extra={"task_id": task.id, "connection_id": connection.id},
                )
                raise MicrosoftCalendarSyncError("Task has no deadline")

            if existing_event:
                # Update existing event
                response = await client.patch(
                    f"/me/calendars/{connection.calendar_id}/events/{existing_event.external_event_id}",
                    json=event_body,
                )
                response.raise_for_status()

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
                response = await client.post(
                    f"/me/calendars/{connection.calendar_id}/events",
                    json=event_body,
                )
                response.raise_for_status()

                created_event = response.json()

                # Create CalendarEvent record
                calendar_event = CalendarEvent(
                    connection_id=connection.id,
                    user_id=connection.user_id,
                    external_event_id=created_event["id"],
                    task_id=task.id,
                    title=task.descricao,
                    description=event_body["body"]["content"],
                    start_time=datetime.fromisoformat(
                        created_event["start"]["dateTime"].replace("Z", "+00:00")
                    ),
                    end_time=datetime.fromisoformat(
                        created_event["end"]["dateTime"].replace("Z", "+00:00")
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

        finally:
            await client.aclose()

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error syncing task to calendar",
            extra={
                "task_id": task.id,
                "connection_id": connection.id,
                "status_code": e.response.status_code,
                "error": str(e),
            },
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to sync task to calendar: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to sync task to calendar",
            extra={"task_id": task.id, "connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to sync task to calendar: {e}") from e


async def sync_calendar_to_tasks(
    connection: CalendarConnection, db: Session, time_min: Optional[datetime] = None
) -> list[CalendarEvent]:
    """
    Sync Microsoft Calendar events to Charlee tasks.

    Args:
        connection: CalendarConnection to use
        db: Database session
        time_min: Minimum time for events to sync (default: now)

    Returns:
        list[CalendarEvent]: List of synced calendar events

    Raises:
        MicrosoftCalendarSyncError: If sync fails
    """
    try:
        client = await get_graph_client(connection)

        try:
            # Default to events from now onwards
            if time_min is None:
                time_min = datetime.now(timezone.utc)

            # Build filter query
            filter_query = f"start/dateTime ge '{time_min.isoformat()}'"

            # Fetch events from Microsoft Calendar
            response = await client.get(
                f"/me/calendars/{connection.calendar_id}/events",
                params={
                    "$filter": filter_query,
                    "$top": 100,
                    "$orderby": "start/dateTime",
                },
            )
            response.raise_for_status()

            data = response.json()
            events = data.get("value", [])
            synced_events = []

            for event in events:
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
                start_dt = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                all_day = event.get("isAllDay", False)

                if existing_event:
                    # Update existing event
                    existing_event.title = event.get("subject", "Untitled")
                    existing_event.description = event.get("body", {}).get("content")
                    existing_event.start_time = start_dt
                    existing_event.end_time = end_dt
                    existing_event.all_day = all_day
                    existing_event.location = event.get("location", {}).get("displayName")
                    existing_event.status = "confirmed"
                    existing_event.external_modified_at = datetime.now(timezone.utc)
                    existing_event.last_modified_at = datetime.now(timezone.utc)

                    synced_events.append(existing_event)
                else:
                    # Create new event
                    calendar_event = CalendarEvent(
                        connection_id=connection.id,
                        user_id=connection.user_id,
                        external_event_id=event["id"],
                        title=event.get("subject", "Untitled"),
                        description=event.get("body", {}).get("content"),
                        start_time=start_dt,
                        end_time=end_dt,
                        all_day=all_day,
                        location=event.get("location", {}).get("displayName"),
                        status="confirmed",
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

        finally:
            await client.aclose()

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error syncing calendar to tasks",
            extra={
                "connection_id": connection.id,
                "status_code": e.response.status_code,
                "error": str(e),
            },
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to sync calendar to tasks: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to sync calendar to tasks",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to sync calendar to tasks: {e}") from e


async def setup_webhook(connection: CalendarConnection, webhook_url: str) -> dict[str, Any]:
    """
    Setup webhook for real-time calendar change notifications.

    Args:
        connection: CalendarConnection to setup webhook for
        webhook_url: HTTPS URL to receive webhook notifications

    Returns:
        dict: Webhook configuration with id and expiration

    Raises:
        MicrosoftCalendarSyncError: If webhook setup fails
    """
    try:
        client = await get_graph_client(connection)

        try:
            # Create subscription
            subscription_body = {
                "changeType": "created,updated,deleted",
                "notificationUrl": webhook_url,
                "resource": f"/me/calendars/{connection.calendar_id}/events",
                "expirationDateTime": (
                    datetime.now(timezone.utc)
                    .replace(hour=0, minute=0, second=0, microsecond=0)
                    .timestamp()
                    + (3 * 24 * 60 * 60)  # 3 days max
                ),
                "clientState": f"charlee-webhook-{connection.id}",
            }

            response = await client.post("/subscriptions", json=subscription_body)
            response.raise_for_status()

            subscription = response.json()

            # Update connection with webhook info
            connection.webhook_id = subscription["id"]
            connection.webhook_expires_at = datetime.fromisoformat(
                subscription["expirationDateTime"].replace("Z", "+00:00")
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
                "webhook_id": subscription["id"],
                "resource": subscription["resource"],
                "expiration": subscription["expirationDateTime"],
            }

        finally:
            await client.aclose()

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error setting up webhook",
            extra={
                "connection_id": connection.id,
                "status_code": e.response.status_code,
                "error": str(e),
            },
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to setup webhook: {e}") from e
    except Exception as e:
        logger.error(
            "Failed to setup webhook",
            extra={"connection_id": connection.id, "error": str(e)},
            exc_info=True,
        )
        raise MicrosoftCalendarSyncError(f"Failed to setup webhook: {e}") from e
