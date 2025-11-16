#!/usr/bin/env python3
"""Test script for Celery setup and tasks.

This script tests:
1. Celery connection
2. Task execution
3. Auto-collector functionality
"""

import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from celery_app import celery_app
from tasks.opportunity_collector import (
    collect_all_opportunities,
    collect_user_opportunities,
)


def test_celery_connection():
    """Test if Celery can connect to Redis."""
    print("Testing Celery connection...")
    try:
        # Ping Redis
        celery_app.control.ping(timeout=1.0)
        print("✅ Celery connected to Redis successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        print("\nMake sure Redis is running:")
        print("  sudo systemctl start redis")
        print("  OR")
        print("  docker run -d -p 6379:6379 redis:7-alpine")
        return False


def test_celery_workers():
    """Test if Celery workers are running."""
    print("\nTesting Celery workers...")
    try:
        # Check active workers
        inspect = celery_app.control.inspect()
        active = inspect.active()

        if active:
            print(f"✅ Found {len(active)} active worker(s):")
            for worker, tasks in active.items():
                print(f"  - {worker}: {len(tasks)} task(s) running")
            return True
        else:
            print("❌ No active workers found!")
            print("\nStart a worker with:")
            print("  cd backend && ./scripts/start_celery_worker.sh")
            return False
    except Exception as e:
        print(f"❌ Failed to inspect workers: {e}")
        return False


def test_task_execution():
    """Test executing a task."""
    print("\nTesting task execution...")
    try:
        # Send test task
        print("Sending collect_all_opportunities task...")
        result = collect_all_opportunities.delay()

        print(f"Task ID: {result.id}")
        print("Waiting for task to complete (max 60s)...")

        # Wait for result
        task_result = result.get(timeout=60)

        print("✅ Task completed successfully!")
        print(f"Result: {task_result}")
        return True

    except Exception as e:
        print(f"❌ Task failed: {e}")
        return False


def test_scheduled_tasks():
    """Check if scheduled tasks are configured."""
    print("\nChecking scheduled tasks...")
    try:
        inspect = celery_app.control.inspect()
        scheduled = inspect.scheduled()

        print("✅ Beat schedule configured:")
        for task_name, config in celery_app.conf.beat_schedule.items():
            print(f"  - {task_name}")
            print(f"    Task: {config['task']}")
            print(f"    Schedule: {config['schedule']}")

        return True
    except Exception as e:
        print(f"❌ Failed to check scheduled tasks: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Celery Setup Test Suite")
    print("=" * 60)

    tests = [
        ("Connection", test_celery_connection),
        ("Workers", test_celery_workers),
        ("Scheduled Tasks", test_scheduled_tasks),
        ("Task Execution", test_task_execution),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results[name] = False

        print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Celery is ready to use.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
