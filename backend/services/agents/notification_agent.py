"""
NotificationAgent - Collector for external notification sources.

This agent collects notifications from external sources like email, Slack,
GitHub, LinkedIn, etc. and imports them into the Charlee notification system.
"""

import email
import imaplib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
from sqlalchemy.orm import Session

from database import crud
from database.models import Notification, NotificationSource
from database.schemas import NotificationCreate
from services.agents.classifier_agent import ClassifierAgent

logger = logging.getLogger(__name__)


class SourceCollector(ABC):
    """Base class for source-specific collectors."""

    def __init__(self, db: Session, source: NotificationSource):
        """
        Initialize collector.

        Args:
            db: Database session
            source: NotificationSource configuration
        """
        self.db = db
        self.source = source
        self.user_id = source.user_id

    @abstractmethod
    def collect(self) -> List[Dict]:
        """
        Collect notifications from source.

        Returns:
            List of notification dicts with keys:
            - title: str
            - message: str
            - external_id: str
            - thread_id: Optional[str]
            - extra_data: Dict
        """
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external source.

        Returns:
            True if authentication successful, False otherwise
        """
        pass


class EmailCollector(SourceCollector):
    """Collector for Email (IMAP) sources."""

    def authenticate(self) -> bool:
        """Authenticate with IMAP server."""
        try:
            credentials = self.source.credentials
            imap_server = credentials.get("imap_server")
            username = credentials.get("username")
            password = credentials.get("password")

            if not all([imap_server, username, password]):
                logger.error(f"Missing IMAP credentials for source {self.source.id}")
                return False

            # Test connection
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)
            mail.logout()

            return True

        except Exception as e:
            logger.error(f"IMAP authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect emails from IMAP server."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            imap_server = credentials.get("imap_server")
            username = credentials.get("username")
            password = credentials.get("password")
            folders = settings.get("folders", ["INBOX"])
            only_unread = settings.get("only_unread", True)
            max_emails = settings.get("max_emails_per_sync", 50)

            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)

            for folder in folders:
                try:
                    mail.select(folder)

                    # Search criteria
                    search_criteria = "UNSEEN" if only_unread else "ALL"
                    _, message_numbers = mail.search(None, search_criteria)

                    # Limit number of emails
                    email_ids = message_numbers[0].split()[-max_emails:]

                    for email_id in email_ids:
                        try:
                            _, msg_data = mail.fetch(email_id, "(RFC822)")
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)

                            # Extract email details
                            subject = email_message.get("Subject", "No Subject")
                            sender = email_message.get("From", "Unknown")
                            message_id = email_message.get("Message-ID", f"email-{email_id}")
                            in_reply_to = email_message.get("In-Reply-To")

                            # Get body
                            body = self._extract_email_body(email_message)

                            # Create notification dict
                            notification_dict = {
                                "title": f"{sender}: {subject}",
                                "message": body[:500],  # Limit message length
                                "external_id": message_id,
                                "thread_id": in_reply_to or message_id,
                                "extra_data": {
                                    "sender": sender,
                                    "subject": subject,
                                    "folder": folder,
                                    "email_id": str(email_id.decode()),
                                },
                            }

                            collected_notifications.append(notification_dict)

                        except Exception as e:
                            logger.error(f"Error processing email {email_id}: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error accessing folder {folder}: {e}")
                    continue

            mail.logout()

        except Exception as e:
            logger.error(f"Error collecting emails for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications

    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email."""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except Exception:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except Exception:
                body = str(email_message.get_payload())

        return body.strip()


class GitHubCollector(SourceCollector):
    """Collector for GitHub notifications."""

    def authenticate(self) -> bool:
        """Authenticate with GitHub API."""
        try:
            credentials = self.source.credentials
            token = credentials.get("token")

            if not token:
                logger.error(f"Missing GitHub token for source {self.source.id}")
                return False

            # Test token
            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"GitHub authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect GitHub notifications."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            token = credentials.get("token")
            repos = settings.get("repos", [])  # Specific repos to watch
            include_types = settings.get("include_types", ["all"])
            # Types: PullRequest, Issue, Commit, Release, Discussion

            headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

            # Get notifications
            url = "https://api.github.com/notifications"
            params = {"per_page": 50}

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            notifications = response.json()

            for notif in notifications:
                try:
                    # Filter by repo if specified
                    repo_name = notif["repository"]["full_name"]
                    if repos and repo_name not in repos:
                        continue

                    # Filter by type
                    subject_type = notif["subject"]["type"]
                    if include_types and "all" not in include_types:
                        if subject_type not in include_types:
                            continue

                    # Create notification dict
                    notification_dict = {
                        "title": f"[GitHub] {notif['subject']['title']}",
                        "message": f"{subject_type} in {repo_name}: {notif['subject']['title']}",
                        "external_id": notif["id"],
                        "thread_id": notif.get("thread_id"),
                        "extra_data": {
                            "repo": repo_name,
                            "type": subject_type,
                            "reason": notif["reason"],
                            "url": notif["subject"]["url"],
                            "github_url": notif.get("html_url"),
                        },
                    }

                    collected_notifications.append(notification_dict)

                except Exception as e:
                    logger.error(f"Error processing GitHub notification: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error collecting GitHub notifications for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class SlackCollector(SourceCollector):
    """Collector for Slack messages and notifications."""

    def authenticate(self) -> bool:
        """Authenticate with Slack API."""
        try:
            credentials = self.source.credentials
            token = credentials.get("token")

            if not token:
                logger.error(f"Missing Slack token for source {self.source.id}")
                return False

            # Test token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://slack.com/api/auth.test", headers=headers, timeout=10)

            data = response.json()
            return data.get("ok", False)

        except Exception as e:
            logger.error(f"Slack authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect messages from Slack."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            token = credentials.get("token")
            channels = settings.get("channels", [])  # Channel IDs to monitor
            max_messages = settings.get("max_messages_per_sync", 50)

            headers = {"Authorization": f"Bearer {token}"}

            # Get conversations
            url = "https://slack.com/api/conversations.list"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            conversations_data = response.json()

            if not conversations_data.get("ok"):
                logger.error(f"Slack API error: {conversations_data.get('error')}")
                return collected_notifications

            conversations = conversations_data.get("channels", [])

            # Filter channels if specified
            if channels:
                conversations = [c for c in conversations if c["id"] in channels]

            # Get messages from each conversation
            for conv in conversations[:10]:  # Limit to 10 conversations
                try:
                    # Get conversation history
                    history_url = "https://slack.com/api/conversations.history"
                    params = {
                        "channel": conv["id"],
                        "limit": min(max_messages // len(conversations), 20),
                    }

                    history_response = requests.get(
                        history_url, headers=headers, params=params, timeout=10
                    )
                    history_data = history_response.json()

                    if not history_data.get("ok"):
                        continue

                    messages = history_data.get("messages", [])

                    for msg in messages:
                        try:
                            # Skip bot messages if configured
                            if msg.get("bot_id") and not settings.get("include_bots", False):
                                continue

                            text = msg.get("text", "")
                            user = msg.get("user", "Unknown")
                            ts = msg.get("ts", "")

                            notification_dict = {
                                "title": f"[Slack] {conv['name']}: New message",
                                "message": text[:500],
                                "external_id": f"slack-{conv['id']}-{ts}",
                                "thread_id": msg.get("thread_ts", ts),
                                "extra_data": {
                                    "channel": conv["name"],
                                    "channel_id": conv["id"],
                                    "user": user,
                                    "timestamp": ts,
                                    "type": msg.get("type", "message"),
                                },
                            }

                            collected_notifications.append(notification_dict)

                        except Exception as e:
                            logger.error(f"Error processing Slack message: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error processing Slack conversation {conv['id']}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error collecting Slack messages for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class DiscordCollector(SourceCollector):
    """Collector for Discord messages."""

    def authenticate(self) -> bool:
        """Authenticate with Discord API."""
        try:
            credentials = self.source.credentials
            token = credentials.get("token")

            if not token:
                logger.error(f"Missing Discord token for source {self.source.id}")
                return False

            # Test token
            headers = {"Authorization": f"Bot {token}"}
            response = requests.get(
                "https://discord.com/api/v10/users/@me", headers=headers, timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Discord authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect messages from Discord."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            token = credentials.get("token")
            guild_ids = settings.get("guild_ids", [])  # Server IDs to monitor
            channel_ids = settings.get("channel_ids", [])  # Specific channels
            max_messages = settings.get("max_messages_per_sync", 50)

            headers = {"Authorization": f"Bot {token}"}

            # If specific channels provided
            channels_to_check = channel_ids

            # Otherwise get channels from guilds
            if not channels_to_check and guild_ids:
                for guild_id in guild_ids[:5]:  # Limit to 5 guilds
                    try:
                        url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
                        response = requests.get(url, headers=headers, timeout=10)
                        response.raise_for_status()
                        channels = response.json()

                        # Filter text channels
                        text_channels = [c["id"] for c in channels if c["type"] == 0]
                        channels_to_check.extend(text_channels[:10])  # Max 10 per guild

                    except Exception as e:
                        logger.error(f"Error getting Discord guild channels: {e}")
                        continue

            # Get messages from each channel
            for channel_id in channels_to_check[:20]:  # Limit total channels
                try:
                    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
                    params = {"limit": min(max_messages // max(len(channels_to_check), 1), 20)}

                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    response.raise_for_status()
                    messages = response.json()

                    for msg in messages:
                        try:
                            notification_dict = {
                                "title": f"[Discord] {msg['author']['username']}: New message",
                                "message": msg["content"][:500],
                                "external_id": f"discord-{msg['id']}",
                                "thread_id": msg.get("message_reference", {}).get(
                                    "message_id", msg["id"]
                                ),
                                "extra_data": {
                                    "channel_id": channel_id,
                                    "author": msg["author"]["username"],
                                    "author_id": msg["author"]["id"],
                                    "timestamp": msg["timestamp"],
                                    "attachments": len(msg.get("attachments", [])),
                                },
                            }

                            collected_notifications.append(notification_dict)

                        except Exception as e:
                            logger.error(f"Error processing Discord message: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error processing Discord channel {channel_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error collecting Discord messages for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class TelegramCollector(SourceCollector):
    """Collector for Telegram messages via Bot API."""

    def authenticate(self) -> bool:
        """Authenticate with Telegram Bot API."""
        try:
            credentials = self.source.credentials
            bot_token = credentials.get("bot_token")

            if not bot_token:
                logger.error(f"Missing Telegram bot token for source {self.source.id}")
                return False

            # Test token
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            data = response.json()

            return data.get("ok", False)

        except Exception as e:
            logger.error(f"Telegram authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect messages from Telegram."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            bot_token = credentials.get("bot_token")
            offset = settings.get("last_update_id", 0)
            max_updates = settings.get("max_updates_per_sync", 50)

            # Get updates
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {"offset": offset + 1, "limit": max_updates, "timeout": 10}

            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                logger.error(f"Telegram API error: {data.get('description')}")
                return collected_notifications

            updates = data.get("result", [])
            last_update_id = offset

            for update in updates:
                try:
                    last_update_id = max(last_update_id, update["update_id"])

                    # Process different update types
                    if "message" in update:
                        msg = update["message"]
                    elif "edited_message" in update:
                        msg = update["edited_message"]
                    else:
                        continue

                    chat = msg.get("chat", {})
                    sender = msg.get("from", {})
                    text = msg.get("text", msg.get("caption", ""))

                    notification_dict = {
                        "title": f"[Telegram] {sender.get('first_name', 'Unknown')}: New message",
                        "message": text[:500],
                        "external_id": f"telegram-{msg['message_id']}-{msg['chat']['id']}",
                        "thread_id": str(
                            msg.get("reply_to_message", {}).get("message_id", msg["message_id"])
                        ),
                        "extra_data": {
                            "chat_id": chat.get("id"),
                            "chat_type": chat.get("type"),
                            "chat_title": chat.get("title", chat.get("username")),
                            "sender_id": sender.get("id"),
                            "sender_username": sender.get("username"),
                            "date": msg.get("date"),
                        },
                    }

                    collected_notifications.append(notification_dict)

                except Exception as e:
                    logger.error(f"Error processing Telegram update: {e}")
                    continue

            # Update last_update_id in settings
            if last_update_id > offset:
                self.source.settings["last_update_id"] = last_update_id
                self.db.commit()

        except Exception as e:
            logger.error(f"Error collecting Telegram messages for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class LinkedInCollector(SourceCollector):
    """Collector for LinkedIn notifications (requires LinkedIn API access)."""

    def authenticate(self) -> bool:
        """Authenticate with LinkedIn API."""
        try:
            credentials = self.source.credentials
            access_token = credentials.get("access_token")

            if not access_token:
                logger.error(f"Missing LinkedIn access token for source {self.source.id}")
                return False

            # Test token with userinfo endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://api.linkedin.com/v2/me", headers=headers, timeout=10)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"LinkedIn authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect notifications from LinkedIn."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            access_token = credentials.get("access_token")
            max_notifications = settings.get("max_notifications_per_sync", 50)

            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
            }

            # Note: LinkedIn API has limited notification access
            # This is a simplified implementation
            # Real implementation may require different endpoints based on API access level

            # Get network updates (shares, posts)
            url = "https://api.linkedin.com/v2/shares"
            params = {"count": max_notifications}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"LinkedIn API returned {response.status_code}")
                return collected_notifications

            data = response.json()
            elements = data.get("elements", [])

            for element in elements:
                try:
                    share_id = element.get("id")
                    text = element.get("text", {}).get("text", "")
                    created = element.get("created", {}).get("time", 0)

                    notification_dict = {
                        "title": "[LinkedIn] New network update",
                        "message": text[:500],
                        "external_id": f"linkedin-{share_id}",
                        "thread_id": share_id,
                        "extra_data": {
                            "share_id": share_id,
                            "created_time": created,
                            "type": "share",
                        },
                    }

                    collected_notifications.append(notification_dict)

                except Exception as e:
                    logger.error(f"Error processing LinkedIn update: {e}")
                    continue

        except Exception as e:
            logger.error(
                f"Error collecting LinkedIn notifications for source {self.source.id}: {e}"
            )
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class TrelloCollector(SourceCollector):
    """Collector for Trello board notifications."""

    def authenticate(self) -> bool:
        """Authenticate with Trello API."""
        try:
            credentials = self.source.credentials
            api_key = credentials.get("api_key")
            token = credentials.get("token")

            if not all([api_key, token]):
                logger.error(f"Missing Trello credentials for source {self.source.id}")
                return False

            # Test credentials
            url = "https://api.trello.com/1/members/me"
            params = {"key": api_key, "token": token}

            response = requests.get(url, params=params, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Trello authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect notifications from Trello."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            api_key = credentials.get("api_key")
            token = credentials.get("token")
            board_ids = settings.get("board_ids", [])
            max_notifications = settings.get("max_notifications_per_sync", 50)

            params = {"key": api_key, "token": token}

            # Get notifications for the authenticated user
            url = "https://api.trello.com/1/members/me/notifications"
            notif_params = {**params, "limit": max_notifications, "read_filter": "unread"}

            response = requests.get(url, params=notif_params, timeout=10)
            response.raise_for_status()
            notifications = response.json()

            for notif in notifications:
                try:
                    # Filter by board if specified
                    board_id = notif.get("data", {}).get("board", {}).get("id")
                    if board_ids and board_id not in board_ids:
                        continue

                    notif_type = notif.get("type")
                    data = notif.get("data", {})
                    card = data.get("card", {})
                    board = data.get("board", {})

                    # Build message based on notification type
                    message = f"{notif_type} on {board.get('name', 'board')}"
                    if card:
                        message = f"{notif_type}: {card.get('name', '')}"

                    notification_dict = {
                        "title": f"[Trello] {message}",
                        "message": notif.get("data", {}).get("text", message)[:500],
                        "external_id": f"trello-{notif['id']}",
                        "thread_id": card.get("id", notif["id"]),
                        "extra_data": {
                            "type": notif_type,
                            "board_id": board_id,
                            "board_name": board.get("name"),
                            "card_id": card.get("id"),
                            "card_name": card.get("name"),
                            "date": notif.get("date"),
                        },
                    }

                    collected_notifications.append(notification_dict)

                except Exception as e:
                    logger.error(f"Error processing Trello notification: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error collecting Trello notifications for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class NotionCollector(SourceCollector):
    """Collector for Notion page and database notifications."""

    def authenticate(self) -> bool:
        """Authenticate with Notion API."""
        try:
            credentials = self.source.credentials
            token = credentials.get("token")

            if not token:
                logger.error(f"Missing Notion token for source {self.source.id}")
                return False

            # Test token
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
            }
            response = requests.get(
                "https://api.notion.com/v1/users/me", headers=headers, timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Notion authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """Collect updates from Notion."""
        collected_notifications = []

        try:
            credentials = self.source.credentials
            settings = self.source.settings or {}

            token = credentials.get("token")
            database_ids = settings.get("database_ids", [])

            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }

            # Check databases for new items
            for db_id in database_ids[:10]:  # Limit to 10 databases
                try:
                    url = f"https://api.notion.com/v1/databases/{db_id}/query"
                    data = {
                        "page_size": 10,
                        "sorts": [{"timestamp": "created_time", "direction": "descending"}],
                    }

                    response = requests.post(url, headers=headers, json=data, timeout=10)

                    if response.status_code != 200:
                        continue

                    result = response.json()
                    pages = result.get("results", [])

                    for page in pages:
                        try:
                            page_id = page["id"]
                            created_time = page.get("created_time")
                            properties = page.get("properties", {})

                            # Try to get title from properties
                            title = "Untitled"
                            for prop_name, prop_value in properties.items():
                                if prop_value.get("type") == "title":
                                    title_array = prop_value.get("title", [])
                                    if title_array:
                                        title = title_array[0].get("plain_text", "Untitled")
                                    break

                            notification_dict = {
                                "title": f"[Notion] New page: {title}",
                                "message": f"New page created in database: {title}",
                                "external_id": f"notion-page-{page_id}",
                                "thread_id": db_id,
                                "extra_data": {
                                    "page_id": page_id,
                                    "database_id": db_id,
                                    "created_time": created_time,
                                    "page_url": page.get("url"),
                                },
                            }

                            collected_notifications.append(notification_dict)

                        except Exception as e:
                            logger.error(f"Error processing Notion page: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error querying Notion database {db_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error collecting Notion notifications for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class WhatsAppCollector(SourceCollector):
    """Collector for WhatsApp Business messages via Cloud API."""

    def authenticate(self) -> bool:
        """Authenticate with WhatsApp Business API."""
        try:
            credentials = self.source.credentials
            access_token = credentials.get("access_token")
            phone_number_id = credentials.get("phone_number_id")

            if not all([access_token, phone_number_id]):
                logger.error(f"Missing WhatsApp credentials for source {self.source.id}")
                return False

            # Test credentials by getting phone number info
            headers = {"Authorization": f"Bearer {access_token}"}
            url = f"https://graph.facebook.com/v17.0/{phone_number_id}"

            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"WhatsApp authentication failed for source {self.source.id}: {e}")
            return False

    def collect(self) -> List[Dict]:
        """
        Collect messages from WhatsApp Business.

        Note: WhatsApp Cloud API uses webhooks for real-time messages.
        This collector retrieves recent conversations.
        """
        collected_notifications = []

        try:
            credentials = self.source.credentials

            access_token = credentials.get("access_token")

            # Note: WhatsApp Cloud API primarily uses webhooks
            # This is a placeholder implementation
            # Real implementation would store webhook data and retrieve it here

            logger.info(
                f"WhatsApp collector for source {self.source.id}: "
                "WhatsApp uses webhooks. Configure webhook endpoint to receive messages."
            )

            # Placeholder: In production, you'd query your webhook message storage
            # For now, return empty list
            # To implement: Store webhook POST data in a temporary table,
            # then query that table here

        except Exception as e:
            logger.error(f"Error collecting WhatsApp messages for source {self.source.id}: {e}")
            self.source.last_error = str(e)
            self.db.commit()

        return collected_notifications


class NotificationAgent:
    """
    Main agent for collecting notifications from external sources.

    Coordinates collection, deduplication, and classification.
    """

    # Map source types to collector classes
    COLLECTORS = {
        "email": EmailCollector,
        "github": GitHubCollector,
        "slack": SlackCollector,
        "discord": DiscordCollector,
        "telegram": TelegramCollector,
        "linkedin": LinkedInCollector,
        "trello": TrelloCollector,
        "notion": NotionCollector,
        "whatsapp": WhatsAppCollector,
    }

    def __init__(self, db: Session):
        """
        Initialize notification agent.

        Args:
            db: Database session
        """
        self.db = db

    def collect_from_source(self, source_id: int) -> Dict:
        """
        Collect notifications from a specific source.

        Args:
            source_id: ID of NotificationSource

        Returns:
            Dict with collection results:
            - collected: int
            - spam_filtered: int
            - errors: List[str]
        """
        source = self.db.query(NotificationSource).filter_by(id=source_id).first()

        if not source:
            raise ValueError(f"Source {source_id} not found")

        if not source.enabled:
            logger.info(f"Source {source_id} is disabled, skipping collection")
            return {"collected": 0, "spam_filtered": 0, "errors": ["Source is disabled"]}

        # Get collector class
        collector_class = self.COLLECTORS.get(source.source_type)

        if not collector_class:
            error_msg = f"No collector available for source type: {source.source_type}"
            logger.error(error_msg)
            return {"collected": 0, "spam_filtered": 0, "errors": [error_msg]}

        # Initialize collector
        collector = collector_class(self.db, source)

        # Authenticate
        if not collector.authenticate():
            error_msg = "Authentication failed"
            source.last_error = error_msg
            self.db.commit()
            return {"collected": 0, "spam_filtered": 0, "errors": [error_msg]}

        # Collect notifications
        raw_notifications = collector.collect()

        # Process and store notifications
        collected_count = 0
        spam_filtered_count = 0
        errors = []

        classifier = ClassifierAgent(self.db, source.user_id)

        for notif_dict in raw_notifications:
            try:
                # Check for duplicates
                existing = (
                    self.db.query(Notification)
                    .filter_by(
                        user_id=source.user_id,
                        source_id=source.id,
                        external_id=notif_dict["external_id"],
                    )
                    .first()
                )

                if existing:
                    logger.debug(f"Skipping duplicate notification: {notif_dict['external_id']}")
                    continue

                # Create notification
                notification_data = NotificationCreate(
                    user_id=source.user_id,
                    type=source.source_type,
                    title=notif_dict["title"],
                    message=notif_dict["message"],
                    extra_data=notif_dict.get("extra_data", {}),
                )

                notification = crud.create_notification(self.db, notification_data)

                # Update notification with source tracking
                notification.source_id = source.id
                notification.external_id = notif_dict["external_id"]
                notification.thread_id = notif_dict.get("thread_id")
                self.db.commit()

                # Classify notification with AI
                try:
                    classifier.classify_and_apply(notification.id)
                    self.db.refresh(notification)

                    # Check if classified as spam
                    if notification.categoria == "spam":
                        notification.arquivada = True
                        self.db.commit()
                        spam_filtered_count += 1

                except Exception as e:
                    logger.error(f"Error classifying notification {notification.id}: {e}")

                collected_count += 1

            except Exception as e:
                error_msg = f"Error processing notification: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

        # Update source statistics
        source.total_collected += collected_count
        source.total_spam_filtered += spam_filtered_count
        source.last_sync = datetime.now(timezone.utc)
        source.last_error = None if not errors else "; ".join(errors[:3])
        self.db.commit()

        return {
            "collected": collected_count,
            "spam_filtered": spam_filtered_count,
            "errors": errors,
        }

    def collect_from_all_sources(self, user_id: Optional[int] = None) -> Dict:
        """
        Collect from all enabled sources (optionally for specific user).

        Args:
            user_id: Optional user ID to filter sources

        Returns:
            Dict with aggregated results
        """
        query = self.db.query(NotificationSource).filter_by(enabled=True)

        if user_id:
            query = query.filter_by(user_id=user_id)

        sources = query.all()

        total_collected = 0
        total_spam_filtered = 0
        all_errors = []

        for source in sources:
            try:
                result = self.collect_from_source(source.id)
                total_collected += result["collected"]
                total_spam_filtered += result["spam_filtered"]
                all_errors.extend(result["errors"])
            except Exception as e:
                logger.error(f"Error collecting from source {source.id}: {e}")
                all_errors.append(f"Source {source.id}: {str(e)}")

        return {
            "sources_processed": len(sources),
            "total_collected": total_collected,
            "total_spam_filtered": total_spam_filtered,
            "errors": all_errors,
        }
