"""Celery tasks for automatic calendar synchronization.

Background tasks for scheduled and webhook-triggered calendar synchronization
between Charlee tasks and external calendar providers (Google, Microsoft).
"""

import logging
from datetime import datetime, timezone
from typing import Optional, cast

from celery import shared_task
from sqlalchemy.orm import Session

from database.config import SessionLocal
from database.models import CalendarConnection, CalendarConflict, CalendarEvent, CalendarSyncLog
from integrations import google_calendar, microsoft_calendar

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Get database session for Celery tasks."""
    return SessionLocal()


def fetch_external_event_version(
    connection: CalendarConnection, event: CalendarEvent
) -> Optional[dict]:
    """
    Fetch current version of an event from external calendar provider.

    Args:
        connection: Calendar connection to use
        event: Event to fetch external version for

    Returns:
        Dict with external event data or None if not found
    """
    try:
        if not event.external_event_id:
            logger.warning(
                "Event has no external_event_id",
                extra={"event_id": event.id},
            )
            return None

        # Fetch from provider based on connection type
        if connection.provider == "google":
            external_event = google_calendar.get_event(connection, event.external_event_id)
        elif connection.provider == "microsoft":
            import asyncio

            external_event = asyncio.run(
                microsoft_calendar.get_event(connection, event.external_event_id)
            )
        else:
            logger.error(
                "Unsupported provider",
                extra={"provider": connection.provider},
            )
            return None

        if external_event:
            return {
                "title": external_event.get("summary") or external_event.get("subject"),
                "start_time": external_event.get("start", {}).get("dateTime"),
                "end_time": external_event.get("end", {}).get("dateTime"),
                "description": external_event.get("description")
                or external_event.get("body", {}).get("content"),
                "location": external_event.get("location"),
                "updated": external_event.get("updated")
                or external_event.get("lastModifiedDateTime"),
                "raw_data": external_event,
            }

        return None

    except Exception as e:
        logger.error(
            "Failed to fetch external event version",
            extra={"event_id": event.id, "error": str(e)},
            exc_info=True,
        )
        return None


@shared_task(
    name="calendar.sync_all_connections",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def sync_all_connections(self) -> dict[str, int]:
    """
    Sync all active calendar connections (scheduled task).

    Runs every 15 minutes via Celery Beat to keep calendars synchronized.

    Returns:
        dict: Statistics about synced connections

    Raises:
        Exception: If sync fails critically (will retry)
    """
    db = get_db()
    stats = {
        "total_connections": 0,
        "synced": 0,
        "failed": 0,
        "skipped": 0,
    }

    try:
        # Get all connections that need sync
        connections = (
            db.query(CalendarConnection)
            .filter(CalendarConnection.sync_enabled == True)  # noqa: E712
            .all()
        )

        stats["total_connections"] = len(connections)

        for connection in connections:
            # Check if connection needs sync (last sync > 15 min ago)
            if not connection.needs_sync(sync_interval_minutes=15):
                stats["skipped"] += 1
                logger.debug(
                    "Skipping connection - recently synced",
                    extra={"connection_id": connection.id},
                )
                continue

            try:
                # Trigger sync for this connection
                sync_connection.delay(connection.id)
                stats["synced"] += 1

                logger.info(
                    "Triggered sync for connection",
                    extra={"connection_id": connection.id, "provider": connection.provider},
                )

            except Exception as e:
                stats["failed"] += 1
                logger.error(
                    "Failed to trigger sync",
                    extra={"connection_id": connection.id, "error": str(e)},
                    exc_info=True,
                )

        logger.info("Completed sync all connections", extra=stats)
        return stats

    except Exception as e:
        logger.error("Fatal error in sync_all_connections", extra={"error": str(e)}, exc_info=True)
        raise self.retry(exc=e)
    finally:
        db.close()


@shared_task(
    name="calendar.sync_connection",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def sync_connection(self, connection_id: int, direction: str = "both") -> dict[str, int | str]:
    """
    Sync a specific calendar connection.

    Args:
        connection_id: Calendar connection ID
        direction: Sync direction ('both', 'to_calendar', 'from_calendar')

    Returns:
        dict: Sync statistics

    Raises:
        Exception: If sync fails (will retry)
    """
    db = get_db()

    try:
        connection = (
            db.query(CalendarConnection).filter(CalendarConnection.id == connection_id).first()
        )

        if not connection:
            logger.error("Connection not found", extra={"connection_id": connection_id})
            return cast(dict[str, int | str], {"error": "Connection not found"})

        if not connection.sync_enabled:
            logger.warning(
                "Sync disabled for connection",
                extra={"connection_id": connection_id},
            )
            return cast(dict[str, int | str], {"error": "Sync disabled"})

        # Create sync log
        sync_log = CalendarSyncLog(
            connection_id=connection.id,
            user_id=connection.user_id,
            sync_type="scheduled",
            direction=direction,
            status="started",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)

        stats: dict[str, int] = {
            "events_created": 0,
            "events_updated": 0,
            "events_deleted": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
        }

        try:
            # Perform sync based on direction
            if direction in ("both", "from_calendar"):
                # Sync from external calendar to Charlee
                if connection.provider == "google":
                    events = google_calendar.sync_calendar_to_tasks(connection, db)
                elif connection.provider == "microsoft":
                    # Microsoft sync is async
                    import asyncio

                    events = asyncio.run(microsoft_calendar.sync_calendar_to_tasks(connection, db))
                else:
                    raise ValueError(f"Unsupported provider: {connection.provider}")

                stats["events_created"] = len([e for e in events if e.source == "external"])

            if direction in ("both", "to_calendar"):
                # Sync from Charlee to external calendar
                # Get tasks that need syncing (tasks with deadlines)
                from database.models import Task

                tasks = (
                    db.query(Task)
                    .filter(
                        Task.user_id == connection.user_id,
                        Task.deadline.isnot(None),
                        Task.status != "Concluída",
                    )
                    .all()
                )

                for task in tasks:
                    try:
                        if connection.provider == "google":
                            google_calendar.sync_task_to_calendar(connection, task, db)
                        elif connection.provider == "microsoft":
                            import asyncio

                            asyncio.run(
                                microsoft_calendar.sync_task_to_calendar(connection, task, db)
                            )

                        stats["events_updated"] += 1

                    except Exception as e:
                        logger.error(
                            "Failed to sync task",
                            extra={
                                "task_id": task.id,
                                "connection_id": connection_id,
                                "error": str(e),
                            },
                        )

            # Detect conflicts
            conflicts = detect_conflicts.apply_async(args=[connection_id])
            if conflicts and conflicts.get():
                stats["conflicts_detected"] = conflicts.get()

            # Update connection last sync time
            connection.last_sync_at = datetime.now(timezone.utc)

            # Update sync log
            sync_log.events_created = stats["events_created"]
            sync_log.events_updated = stats["events_updated"]
            sync_log.events_deleted = stats["events_deleted"]
            sync_log.conflicts_detected = stats["conflicts_detected"]
            sync_log.conflicts_resolved = stats["conflicts_resolved"]
            sync_log.mark_completed("success")

            db.commit()

            logger.info(
                "Sync completed successfully",
                extra={"connection_id": connection_id, "stats": stats},
            )

            return cast(dict[str, int | str], stats)

        except Exception as e:
            # Update sync log with error
            sync_log.status = "failed"
            sync_log.error_message = str(e)
            sync_log.mark_completed("failed")
            db.commit()

            logger.error(
                "Sync failed",
                extra={"connection_id": connection_id, "error": str(e)},
                exc_info=True,
            )

            raise self.retry(exc=e)

    except Exception as e:
        logger.error(
            "Fatal error in sync_connection",
            extra={"connection_id": connection_id, "error": str(e)},
            exc_info=True,
        )
        raise
    finally:
        db.close()


@shared_task(name="calendar.detect_conflicts", bind=True)
def detect_conflicts(self, connection_id: int) -> int:
    """
    Detect synchronization conflicts for a connection.

    Conflicts occur when an event is modified in both Charlee and the external
    calendar since the last sync.

    Args:
        connection_id: Calendar connection ID

    Returns:
        int: Number of conflicts detected

    Raises:
        Exception: If conflict detection fails
    """
    db = get_db()

    try:
        connection = (
            db.query(CalendarConnection).filter(CalendarConnection.id == connection_id).first()
        )

        if not connection:
            logger.error("Connection not found", extra={"connection_id": connection_id})
            return 0

        # Get events that might have conflicts
        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.connection_id == connection_id,
                CalendarEvent.charlee_modified_at.isnot(None),
                CalendarEvent.external_modified_at.isnot(None),
            )
            .all()
        )

        conflicts_detected = 0

        for event in events:
            # Check if both sides were modified since last sync
            if event.charlee_modified_at and event.external_modified_at:
                # Compare modification times
                charlee_time = event.charlee_modified_at
                external_time = event.external_modified_at

                # Ensure timezone aware
                if charlee_time.tzinfo is None:
                    charlee_time = charlee_time.replace(tzinfo=timezone.utc)
                if external_time.tzinfo is None:
                    external_time = external_time.replace(tzinfo=timezone.utc)

                # If both modified after last sync, we have a conflict
                if connection.last_sync_at:
                    last_sync = connection.last_sync_at
                    if last_sync.tzinfo is None:
                        last_sync = last_sync.replace(tzinfo=timezone.utc)

                    if charlee_time > last_sync and external_time > last_sync:
                        # Check if conflict already exists
                        existing_conflict = (
                            db.query(CalendarConflict)
                            .filter(
                                CalendarConflict.event_id == event.id,
                                CalendarConflict.status != "resolved",
                            )
                            .first()
                        )

                        if not existing_conflict:
                            # Fetch external version
                            external_version = fetch_external_event_version(connection, event)

                            # Create conflict
                            conflict = CalendarConflict(
                                event_id=event.id,
                                user_id=connection.user_id,
                                conflict_type="both_modified",
                                charlee_version=event.to_dict(),
                                external_version=external_version or event.to_dict(),
                                resolution_strategy="last_modified_wins",
                                status="detected",
                            )

                            db.add(conflict)
                            conflicts_detected += 1

        db.commit()

        logger.info(
            "Conflict detection completed",
            extra={"connection_id": connection_id, "conflicts": conflicts_detected},
        )

        # Auto-resolve conflicts
        if conflicts_detected > 0:
            resolve_conflicts.delay(connection_id)

        return conflicts_detected

    except Exception as e:
        logger.error(
            "Conflict detection failed",
            extra={"connection_id": connection_id, "error": str(e)},
            exc_info=True,
        )
        raise
    finally:
        db.close()


@shared_task(name="calendar.resolve_conflicts", bind=True)
def resolve_conflicts(self, connection_id: int, strategy: Optional[str] = None) -> int:
    """
    Automatically resolve calendar conflicts.

    Args:
        connection_id: Calendar connection ID
        strategy: Resolution strategy override (default: use conflict's strategy)

    Returns:
        int: Number of conflicts resolved

    Raises:
        Exception: If resolution fails
    """
    db = get_db()

    try:
        # Get unresolved conflicts
        conflicts = (
            db.query(CalendarConflict)
            .join(CalendarEvent)
            .filter(
                CalendarEvent.connection_id == connection_id,
                CalendarConflict.status == "detected",
            )
            .all()
        )

        resolved_count = 0

        for conflict in conflicts:
            try:
                # Determine resolution strategy
                res_strategy = strategy or conflict.resolution_strategy

                if res_strategy == "last_modified_wins":
                    # Use the version with the latest modification time
                    charlee_time = conflict.charlee_version.get("last_modified_at")
                    external_time = conflict.external_version.get("last_modified_at")

                    if charlee_time and external_time:
                        charlee_dt = datetime.fromisoformat(charlee_time)
                        external_dt = datetime.fromisoformat(external_time)

                        if charlee_dt > external_dt:
                            resolved_version = conflict.charlee_version
                            resolved_by = "system_charlee"
                        else:
                            resolved_version = conflict.external_version
                            resolved_by = "system_external"

                        conflict.resolve(resolved_version, resolved_by)
                        resolved_count += 1

                elif res_strategy == "charlee_wins":
                    # Always use Charlee version
                    conflict.resolve(conflict.charlee_version, "system_charlee")
                    resolved_count += 1

                elif res_strategy == "external_wins":
                    # Always use external version
                    conflict.resolve(conflict.external_version, "system_external")
                    resolved_count += 1

                elif res_strategy == "manual":
                    # Mark for manual review
                    conflict.status = "manual_review"
                    db.commit()

                else:
                    logger.warning(
                        "Unknown resolution strategy",
                        extra={"conflict_id": conflict.id, "strategy": res_strategy},
                    )

            except Exception as e:
                logger.error(
                    "Failed to resolve conflict",
                    extra={"conflict_id": conflict.id, "error": str(e)},
                    exc_info=True,
                )

        db.commit()

        logger.info(
            "Conflict resolution completed",
            extra={"connection_id": connection_id, "resolved": resolved_count},
        )

        return resolved_count

    except Exception as e:
        logger.error(
            "Conflict resolution failed",
            extra={"connection_id": connection_id, "error": str(e)},
            exc_info=True,
        )
        raise
    finally:
        db.close()


@shared_task(name="calendar.refresh_tokens", bind=True)
def refresh_tokens(self) -> dict[str, int]:
    """
    Refresh expired OAuth tokens for all connections.

    Runs periodically to ensure tokens are always valid.

    Returns:
        dict: Statistics about refreshed tokens

    Raises:
        Exception: If refresh fails critically
    """
    db = get_db()
    stats = {
        "total_checked": 0,
        "refreshed": 0,
        "failed": 0,
    }

    try:
        # Get all connections
        connections = db.query(CalendarConnection).all()
        stats["total_checked"] = len(connections)

        for connection in connections:
            try:
                # Check if token is expired or will expire soon (within 5 minutes)
                if connection.is_token_expired():
                    if connection.provider == "google":
                        google_calendar.refresh_access_token(connection)
                    elif connection.provider == "microsoft":
                        microsoft_calendar.refresh_access_token(connection)

                    stats["refreshed"] += 1
                    db.commit()

                    logger.info(
                        "Token refreshed",
                        extra={"connection_id": connection.id, "provider": connection.provider},
                    )

            except Exception as e:
                stats["failed"] += 1
                logger.error(
                    "Failed to refresh token",
                    extra={"connection_id": connection.id, "error": str(e)},
                    exc_info=True,
                )

        logger.info("Token refresh completed", extra=stats)
        return stats

    except Exception as e:
        logger.error("Fatal error in refresh_tokens", extra={"error": str(e)}, exc_info=True)
        raise
    finally:
        db.close()
