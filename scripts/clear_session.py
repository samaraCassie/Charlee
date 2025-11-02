#!/usr/bin/env python3
"""Script to clear old Redis sessions."""

import redis
import sys

def clear_session(session_id):
    """Clear a specific session from Redis."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Find and delete session keys
    keys = r.keys(f"*{session_id}*")

    if not keys:
        print(f"❌ Session '{session_id}' not found in Redis")
        return

    print(f"🔍 Found {len(keys)} keys for session '{session_id}':")
    for key in keys:
        print(f"  - {key}")

    confirm = input("\n⚠️  Delete these keys? (yes/no): ")

    if confirm.lower() == 'yes':
        for key in keys:
            r.delete(key)
            print(f"✅ Deleted: {key}")
        print(f"\n✅ Session '{session_id}' cleared successfully!")
    else:
        print("❌ Cancelled")

def list_sessions():
    """List all sessions in Redis."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Get all session keys
    keys = r.keys("*session*")

    if not keys:
        print("📭 No sessions found in Redis")
        return

    print(f"📋 Found {len(keys)} session(s):\n")
    for key in keys:
        print(f"  - {key}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 clear_session.py list              - List all sessions")
        print("  python3 clear_session.py clear <session_id> - Clear specific session")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_sessions()
    elif command == "clear" and len(sys.argv) == 3:
        session_id = sys.argv[2]
        clear_session(session_id)
    else:
        print("❌ Invalid command")
        sys.exit(1)
