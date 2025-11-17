"""WebSocket endpoint for real-time notifications."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from api.auth.security import SECRET_KEY, ALGORITHM
from database.config import SessionLocal
from database import crud

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.

    Maintains active connections per user and broadcasts notifications
    to connected clients.
    """

    def __init__(self):
        """Initialize connection manager."""
        # Map of user_id -> set of websocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

        logger.info(
            f"WebSocket connected for user {user_id}",
            extra={
                "user_id": user_id,
                "total_connections": len(self.active_connections[user_id]),
            },
        )

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(
            f"WebSocket disconnected for user {user_id}",
            extra={
                "user_id": user_id,
            },
        )

    async def send_notification_to_user(self, user_id: int, notification_data: dict):
        """
        Send notification to all connections for a specific user.

        Args:
            user_id: User ID
            notification_data: Notification data to send
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        message = json.dumps(notification_data)
        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message)
                logger.debug(
                    f"Sent notification to user {user_id}",
                    extra={
                        "user_id": user_id,
                        "notification_id": notification_data.get("id"),
                    },
                )
            except Exception as e:
                logger.error(
                    f"Error sending notification to user {user_id}: {e}",
                    extra={
                        "user_id": user_id,
                        "error": str(e),
                    },
                )
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def broadcast_to_all(self, message: str):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass


# Global connection manager instance
manager = ConnectionManager()


async def get_user_from_token(token: str) -> int:
    """
    Extract and validate user ID from JWT token.

    Args:
        token: JWT access token

    Returns:
        User ID

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("user_id"))  # type: ignore
        if user_id is None:
            raise ValueError("Invalid token: missing user_id")
        return user_id
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.

    Protocol:
    1. Client connects with JWT token as query parameter: /ws/notifications?token={jwt}
    2. Server validates token and accepts connection
    3. Server sends heartbeat pings every 30 seconds
    4. Client responds to pings with pong
    5. Server sends notifications in real-time as they're created
    6. Client can send commands (e.g., mark_as_read)

    Message format (server -> client):
    {
        "type": "notification" | "heartbeat" | "error",
        "data": {...}
    }

    Message format (client -> server):
    {
        "type": "pong" | "mark_as_read",
        "data": {...}
    }
    """
    # Extract token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    # Validate token and get user_id
    try:
        user_id = await get_user_from_token(token)
    except ValueError as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Accept connection
    await manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "data": {
                "message": "Connected to notifications",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })

        # Send initial unread count
        db = SessionLocal()
        try:
            unread_count = crud.count_unread_notifications(db, user_id)
            await websocket.send_json({
                "type": "unread_count",
                "data": {
                    "count": unread_count,
                },
            })
        finally:
            db.close()

        # Heartbeat and message handling loop
        async def heartbeat():
            """Send periodic heartbeat pings."""
            while True:
                try:
                    await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                    await websocket.send_json({
                        "type": "heartbeat",
                        "data": {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    })
                except Exception:
                    break

        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat())

        try:
            # Listen for client messages
            while True:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "pong":
                    # Client responded to heartbeat
                    logger.debug(f"Received pong from user {user_id}")

                elif message_type == "mark_as_read":
                    # Handle mark as read command
                    notification_id = data.get("data", {}).get("notification_id")
                    if notification_id:
                        db = SessionLocal()
                        try:
                            notification = crud.mark_notification_as_read(
                                db, notification_id, user_id
                            )
                            if notification:
                                # Send confirmation
                                await websocket.send_json({
                                    "type": "notification_read",
                                    "data": {
                                        "notification_id": notification_id,
                                        "success": True,
                                    },
                                })
                                # Send updated unread count
                                unread_count = crud.count_unread_notifications(db, user_id)
                                await websocket.send_json({
                                    "type": "unread_count",
                                    "data": {
                                        "count": unread_count,
                                    },
                                })
                        finally:
                            db.close()

                else:
                    logger.warning(f"Unknown message type from user {user_id}: {message_type}")

        finally:
            # Cancel heartbeat task
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(
            f"WebSocket error for user {user_id}: {e}",
            extra={
                "user_id": user_id,
                "error": str(e),
            },
            exc_info=True,
        )
    finally:
        manager.disconnect(websocket, user_id)


def get_connection_manager() -> ConnectionManager:
    """
    Get the global connection manager instance.

    Returns:
        ConnectionManager instance
    """
    return manager
