#!/bin/bash
# Start Celery Beat scheduler for periodic tasks

set -e

echo "Starting Celery Beat Scheduler..."
echo "================================="

# Change to backend directory
cd "$(dirname "$0")/.."

# Start Celery beat
celery -A celery_app beat \
    --loglevel=info \
    --scheduler celery.beat:PersistentScheduler

# Options explained:
# -A celery_app: App module location
# --loglevel=info: Logging level
# --scheduler: Use persistent scheduler (saves schedule to disk)
