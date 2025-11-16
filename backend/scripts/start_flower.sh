#!/bin/bash
# Start Flower monitoring UI for Celery

set -e

echo "Starting Flower Monitoring UI..."
echo "================================"

# Change to backend directory
cd "$(dirname "$0")/.."

# Start Flower
celery -A celery_app flower \
    --port=5555 \
    --loglevel=info

# Access Flower at: http://localhost:5555
# Options explained:
# -A celery_app: App module location
# --port=5555: Web UI port
# --loglevel=info: Logging level
