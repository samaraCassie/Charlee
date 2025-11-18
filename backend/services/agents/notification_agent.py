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


class NotificationAgent:
    """
    Main agent for collecting notifications from external sources.

    Coordinates collection, deduplication, and classification.
    """

    # Map source types to collector classes
    COLLECTORS = {"email": EmailCollector, "github": GitHubCollector}

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
                    logger.debug(
                        f"Skipping duplicate notification: {notif_dict['external_id']}"
                    )
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
