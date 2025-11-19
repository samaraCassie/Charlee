"""Celery application configuration for background tasks.

This module configures Celery for handling asynchronous tasks like:
- Auto-collection of freelance opportunities
- Periodic data analysis and insights generation
- Scheduled notifications and alerts
- Calendar synchronization with external providers
"""

import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "charlee",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "tasks.opportunity_collector",
        "tasks.intelligence_automation",
        "tasks.calendar_sync",
        "tasks.notification_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",  # Adjust to your timezone
    enable_utc=True,
    # Task execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={"master_name": "mymaster"},
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Beat schedule (periodic tasks)
    beat_schedule={
        # Collect opportunities every 15 minutes
        "collect-opportunities-every-15-minutes": {
            "task": "tasks.opportunity_collector.collect_all_opportunities",
            "schedule": crontab(minute="*/15"),
            "options": {"expires": 600},
        },
        # Analyze new opportunities every 30 minutes (after collection)
        "analyze-new-opportunities-every-30-minutes": {
            "task": "tasks.intelligence_automation.analyze_new_opportunities",
            "schedule": crontab(minute="*/30"),
            "options": {"expires": 900},
        },
        # Send notifications for high-value opportunities every hour
        "send-opportunity-notifications-hourly": {
            "task": "tasks.intelligence_automation.send_opportunity_notifications",
            "schedule": crontab(minute=30),  # Every hour at :30
            "options": {"expires": 1800},
        },
        # Generate daily reports every morning at 8 AM
        "generate-daily-reports-morning": {
            "task": "tasks.intelligence_automation.generate_daily_report",
            "schedule": crontab(hour=8, minute=0),
            "options": {"expires": 3600},
        },
        # Detect career anomalies weekly (Mondays at 9 AM)
        "detect-career-anomalies-weekly": {
            "task": "tasks.intelligence_automation.detect_career_anomalies",
            "schedule": crontab(day_of_week=1, hour=9, minute=0),
            "options": {"expires": 3600},
        },
        # Calendar synchronization tasks
        # Sync all calendar connections every 15 minutes
        "sync-all-calendars-every-15-minutes": {
            "task": "calendar.sync_all_connections",
            "schedule": crontab(minute="*/15"),
            "options": {"expires": 600},
        },
        # Refresh expired OAuth tokens every 2 hours
        "refresh-calendar-tokens-every-2-hours": {
            "task": "calendar.refresh_tokens",
            "schedule": crontab(minute=0, hour="*/2"),
            "options": {"expires": 1800},
        },
        # Notification collection and processing tasks
        # Collect notifications from all sources every 15 minutes
        "collect-notifications-every-15-minutes": {
            "task": "notifications.collect_all_sources",
            "schedule": crontab(minute="*/15"),
            "options": {"expires": 600},
        },
        # Generate daily digests every morning at 7 AM
        "generate-daily-digests-morning": {
            "task": "notifications.generate_daily_digests",
            "schedule": crontab(hour=7, minute=0),
            "options": {"expires": 3600},
        },
        # Generate weekly digests every Monday at 7 AM
        "generate-weekly-digests-monday": {
            "task": "notifications.generate_weekly_digests",
            "schedule": crontab(day_of_week=1, hour=7, minute=0),
            "options": {"expires": 3600},
        },
        # Generate monthly digests on the 1st of each month at 7 AM
        "generate-monthly-digests-monthly": {
            "task": "notifications.generate_monthly_digests",
            "schedule": crontab(day_of_month=1, hour=7, minute=0),
            "options": {"expires": 3600},
        },
        # Cleanup old notifications daily at 3 AM
        "cleanup-old-notifications-daily": {
            "task": "notifications.cleanup_old_notifications",
            "schedule": crontab(hour=3, minute=0),
            "options": {"expires": 7200},
        },
    },
)


def get_celery_app() -> Celery:
    """Get configured Celery application instance."""
    return celery_app
