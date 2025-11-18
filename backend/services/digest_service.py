"""
Digest generation service for notification summaries.

Generates daily, weekly, and monthly summaries of notifications
with AI-powered highlights and time-saved calculations.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import openai
from sqlalchemy.orm import Session

from database import crud
from database.config import SessionLocal
from database.models import Notification, NotificationDigest
from database.schemas import NotificationDigestBase

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")


class DigestService:
    """
    Service for generating notification digest summaries.

    Creates periodic summaries (daily/weekly/monthly) with:
    - Statistical breakdown by category
    - AI-generated highlights
    - Time saved estimation
    """

    def __init__(self, db: Session | None = None):
        """
        Initialize digest service.

        Args:
            db: Optional database session. If not provided, creates a new one.
        """
        self.db = db or SessionLocal()
        self._should_close_db = db is None

    def __del__(self):
        """Close database session if we created it."""
        if self._should_close_db and self.db:
            self.db.close()

    def generate_daily_digest(self, user_id: int) -> NotificationDigest:
        """
        Generate daily digest for a user.

        Args:
            user_id: User ID

        Returns:
            Created digest
        """
        # Define time period (yesterday)
        now = datetime.now(timezone.utc)
        period_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)

        return self._generate_digest(user_id, "daily", period_start, period_end)

    def generate_weekly_digest(self, user_id: int) -> NotificationDigest:
        """
        Generate weekly digest for a user.

        Args:
            user_id: User ID

        Returns:
            Created digest
        """
        # Define time period (last 7 days)
        now = datetime.now(timezone.utc)
        period_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_start = period_end - timedelta(days=7)

        return self._generate_digest(user_id, "weekly", period_start, period_end)

    def generate_monthly_digest(self, user_id: int) -> NotificationDigest:
        """
        Generate monthly digest for a user.

        Args:
            user_id: User ID

        Returns:
            Created digest
        """
        # Define time period (last 30 days)
        now = datetime.now(timezone.utc)
        period_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_start = period_end - timedelta(days=30)

        return self._generate_digest(user_id, "monthly", period_start, period_end)

    def _generate_digest(
        self, user_id: int, digest_type: str, period_start: datetime, period_end: datetime
    ) -> NotificationDigest:
        """
        Generate digest for a specific period.

        Args:
            user_id: User ID
            digest_type: Type of digest (daily/weekly/monthly)
            period_start: Start of period
            period_end: End of period

        Returns:
            Created digest
        """
        # Get notifications for period
        notifications = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.created_at >= period_start,
                Notification.created_at < period_end,
            )
            .all()
        )

        # Calculate statistics
        stats = self._calculate_stats(notifications)

        # Generate AI summary and highlights
        summary_text, highlights = self._generate_ai_summary(notifications, digest_type)

        # Calculate time saved
        time_saved = self._calculate_time_saved(stats)

        # Create digest
        digest_data = NotificationDigestBase(
            digest_type=digest_type,  # type: ignore[arg-type]
            period_start=period_start,
            period_end=period_end,
            total_notifications=len(notifications),
            urgent_count=stats["urgent_count"],
            important_count=stats["important_count"],
            informativo_count=stats["informativo_count"],
            spam_count=stats["spam_count"],
            archived_count=stats["archived_count"],
            time_saved_minutes=time_saved,
            summary_text=summary_text,
            highlights=highlights,
        )

        digest = crud.create_notification_digest(self.db, digest=digest_data, user_id=user_id)

        logger.info(
            f"Created {digest_type} digest for user {user_id}: "
            f"{len(notifications)} notifications, {time_saved}min saved"
        )

        return digest

    def _calculate_stats(self, notifications: List[Notification]) -> Dict:
        """
        Calculate statistics from notifications.

        Args:
            notifications: List of notifications

        Returns:
            Dict with statistics
        """
        stats = {
            "urgent_count": 0,
            "important_count": 0,
            "informativo_count": 0,
            "spam_count": 0,
            "archived_count": 0,
            "read_count": 0,
            "unread_count": 0,
        }

        for notification in notifications:
            # Count by category
            if notification.categoria == "urgente":
                stats["urgent_count"] += 1
            elif notification.categoria == "importante":
                stats["important_count"] += 1
            elif notification.categoria == "informativo":
                stats["informativo_count"] += 1
            elif notification.categoria == "spam":
                stats["spam_count"] += 1

            # Count archived
            if notification.arquivada:
                stats["archived_count"] += 1

            # Count read/unread
            if notification.read:
                stats["read_count"] += 1
            else:
                stats["unread_count"] += 1

        return stats

    def _generate_ai_summary(
        self, notifications: List[Notification], digest_type: str
    ) -> tuple[str, List[Dict]]:
        """
        Generate AI-powered summary and highlights.

        Args:
            notifications: List of notifications
            digest_type: Type of digest

        Returns:
            Tuple of (summary_text, highlights_list)
        """
        if not notifications:
            return f"No notifications received in this {digest_type} period.", []

        # Prepare notifications for AI
        notif_summaries = []
        for notif in notifications[:50]:  # Limit to 50 most recent
            notif_summaries.append(
                {
                    "title": notif.title,
                    "message": notif.message[:200],  # Truncate long messages
                    "type": notif.type,
                    "categoria": notif.categoria,
                    "prioridade": notif.prioridade,
                }
            )

        prompt = f"""
Analyze these {digest_type} notifications and create a concise summary.

Notifications: {json.dumps(notif_summaries, indent=2)}

Provide a JSON response with:
1. "summary": A 2-3 sentence summary of the period's notifications
2. "highlights": List of 3-5 most important notifications (with title and why important)
3. "insights": One key insight about notification patterns

Focus on what matters most to the user. Be concise and actionable.

Return ONLY valid JSON, no additional text.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise notification summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            summary_text = result.get("summary", "")
            highlights = result.get("highlights", [])

            # Add insights to summary
            if "insights" in result:
                summary_text += f"\n\n💡 Insight: {result['insights']}"

            return summary_text, highlights

        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback to simple summary
            total = len(notifications)
            urgent = sum(1 for n in notifications if n.categoria == "urgente")
            important = sum(1 for n in notifications if n.categoria == "importante")

            summary = (
                f"You received {total} notifications this {digest_type} period. "
                f"{urgent} urgent, {important} important."
            )
            return summary, []

    def _calculate_time_saved(self, stats: Dict) -> int:
        """
        Estimate time saved by automatic filtering and archiving.

        Args:
            stats: Statistics dict

        Returns:
            Time saved in minutes
        """
        # Estimate time per notification type:
        # - Spam: 2 minutes (would waste time reading and deleting)
        # - Informativo archived: 1 minute (quick read and archive decision)
        # - Auto-archived: 0.5 minutes (decision time saved)

        time_saved = 0

        # Time saved from spam filtering (2 min per spam)
        time_saved += stats["spam_count"] * 2

        # Time saved from auto-archiving (0.5 min per archived)
        time_saved += stats["archived_count"] * 0.5

        return int(time_saved)

    def should_generate_digest(self, user_id: int, digest_type: str) -> bool:
        """
        Check if a digest should be generated.

        Args:
            user_id: User ID
            digest_type: Type of digest

        Returns:
            True if digest should be generated, False otherwise
        """
        latest_digest = crud.get_latest_digest(self.db, user_id=user_id, digest_type=digest_type)

        if not latest_digest:
            return True

        # Check if enough time has passed
        now = datetime.now(timezone.utc)

        if digest_type == "daily":
            # Generate if last digest was more than 20 hours ago
            threshold = timedelta(hours=20)
        elif digest_type == "weekly":
            # Generate if last digest was more than 6 days ago
            threshold = timedelta(days=6)
        else:  # monthly
            # Generate if last digest was more than 28 days ago
            threshold = timedelta(days=28)

        time_since_last = now - latest_digest.created_at.replace(tzinfo=timezone.utc)

        return time_since_last >= threshold

    def generate_all_pending_digests(self, user_id: int) -> Dict:
        """
        Generate all pending digests for a user.

        Args:
            user_id: User ID

        Returns:
            Dict with generation results
        """
        results = {"generated": [], "skipped": []}

        for digest_type in ["daily", "weekly", "monthly"]:
            if self.should_generate_digest(user_id, digest_type):
                try:
                    if digest_type == "daily":
                        digest = self.generate_daily_digest(user_id)
                    elif digest_type == "weekly":
                        digest = self.generate_weekly_digest(user_id)
                    else:
                        digest = self.generate_monthly_digest(user_id)

                    results["generated"].append(
                        {
                            "type": digest_type,
                            "id": digest.id,
                            "notifications": digest.total_notifications,
                            "time_saved": digest.time_saved_minutes,
                        }
                    )
                except Exception as e:
                    logger.error(f"Error generating {digest_type} digest: {e}")
                    results["skipped"].append({"type": digest_type, "error": str(e)})
            else:
                results["skipped"].append(
                    {"type": digest_type, "reason": "Too soon since last digest"}
                )

        return results
