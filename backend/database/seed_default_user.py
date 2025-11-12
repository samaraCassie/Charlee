#!/usr/bin/env python3
"""
Seed script to create a default user after authentication migration.

Run this after running the authentication migration (002) to create a default
user and migrate existing data to that user.

Usage:
    python -m database.seed_default_user
"""

import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from api.auth.password import hash_password
from database.config import settings
from database.models import BigRock, DailyLog, MenstrualCycle, Task, User


def create_default_user(db):
    """Create a default user if none exists."""
    existing_user = db.query(User).first()

    if existing_user:
        print(f"✓ User already exists: {existing_user.username}")
        return existing_user

    # Create default user
    default_user = User(
        username="admin",
        email="admin@charlee.local",
        hashed_password=hash_password("ChangeMe123!"),
        full_name="Charlee Admin",
        is_active=True,
        is_superuser=True,
    )

    db.add(default_user)
    db.commit()
    db.refresh(default_user)

    print(f"✓ Created default user: {default_user.username}")
    print(f"  Email: {default_user.email}")
    print("  Password: ChangeMe123!")
    print("  ⚠️  IMPORTANT: Change the password after first login!")

    return default_user


def migrate_existing_data(db, user):
    """Migrate existing data to the default user."""
    # Count existing data
    big_rocks_count = db.query(BigRock).filter(BigRock.user_id is None).count()
    tasks_count = db.query(Task).filter(Task.user_id is None).count()
    cycles_count = db.query(MenstrualCycle).filter(MenstrualCycle.user_id is None).count()
    logs_count = db.query(DailyLog).filter(DailyLog.user_id is None).count()

    if big_rocks_count == 0 and tasks_count == 0 and cycles_count == 0 and logs_count == 0:
        print("\n✓ No existing data to migrate")
        return

    print(f"\n📦 Migrating existing data to user '{user.username}':")
    print(f"  - Big Rocks: {big_rocks_count}")
    print(f"  - Tasks: {tasks_count}")
    print(f"  - Menstrual Cycles: {cycles_count}")
    print(f"  - Daily Logs: {logs_count}")

    # Migrate Big Rocks
    db.query(BigRock).filter(BigRock.user_id is None).update(
        {BigRock.user_id: user.id}, synchronize_session=False
    )

    # Migrate Tasks
    db.query(Task).filter(Task.user_id is None).update(
        {Task.user_id: user.id}, synchronize_session=False
    )

    # Migrate Menstrual Cycles
    db.query(MenstrualCycle).filter(MenstrualCycle.user_id is None).update(
        {MenstrualCycle.user_id: user.id}, synchronize_session=False
    )

    # Migrate Daily Logs
    db.query(DailyLog).filter(DailyLog.user_id is None).update(
        {DailyLog.user_id: user.id}, synchronize_session=False
    )

    db.commit()
    print("\n✓ Data migration completed successfully")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Charlee Authentication System - Data Seeding")
    print("=" * 60)

    # Create engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if users table exists
        result = db.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='users'")
        )
        if result.scalar() == 0:
            print("\n❌ Error: 'users' table not found!")
            print("   Please run the authentication migration first:")
            print("   alembic upgrade head")
            sys.exit(1)

        # Create default user
        user = create_default_user(db)

        # Migrate existing data
        migrate_existing_data(db, user)

        print("\n" + "=" * 60)
        print("✅ Seeding completed successfully!")
        print("=" * 60)
        print("\n📋 Next steps:")
        print("1. Login to the system with the default credentials")
        print("2. Change the default password immediately")
        print("3. Create additional users as needed via the registration endpoint")
        print("\n🔐 Default credentials:")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print("   Password: ChangeMe123!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
