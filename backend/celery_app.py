"""Celery application configuration for background tasks.

This module configures Celery for handling asynchronous tasks like:
- Auto-collection of freelance opportunities
- Periodic data analysis and insights generation
- Scheduled notifications and alerts
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
    include=["tasks.opportunity_collector"],
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
        "collect-opportunities-every-15-minutes": {
            "task": "tasks.opportunity_collector.collect_all_opportunities",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
            "options": {"expires": 600},  # Task expires if not picked up in 10 min
        },
    },
)


def get_celery_app() -> Celery:
    """Get configured Celery application instance."""
    return celery_app
