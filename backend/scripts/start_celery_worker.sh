#!/bin/bash
# Start Celery worker for processing background tasks

set -e

echo "Starting Celery Worker..."
echo "========================"

# Change to backend directory
cd "$(dirname "$0")/.."

# Start Celery worker
celery -A celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=1800 \
    --soft-time-limit=1500

# Options explained:
# -A celery_app: App module location
# --loglevel=info: Logging level
# --concurrency=4: Number of worker processes
# --max-tasks-per-child=1000: Restart worker after 1000 tasks (prevents memory leaks)
# --time-limit=1800: Hard timeout (30 minutes)
# --soft-time-limit=1500: Soft timeout (25 minutes)
