"""Script to test the Charlee backend setup."""

import sys
from database.config import engine, Base, settings
from database.models import BigRock, Task
from sqlalchemy import text


def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")

    try:
        with engine.connect() as conn:
            _ = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_create_tables():
    """Test creating database tables."""
    print("\n🔍 Testing table creation...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def test_models():
    """Test creating sample data."""
    print("\n🔍 Testing models with sample data...")

    from sqlalchemy.orm import Session

    try:
        with Session(engine) as session:
            # Create a Big Rock
            big_rock = BigRock(nome="Test Big Rock", cor="#FF5733")
            session.add(big_rock)
            session.commit()
            session.refresh(big_rock)

            print(f"✅ Created Big Rock: {big_rock}")

            # Create a Task
            from datetime import date

            tarefa = Task(descricao="Test Task", big_rock_id=big_rock.id, deadline=date.today())
            session.add(tarefa)
            session.commit()
            session.refresh(tarefa)

            print(f"✅ Created Task: {tarefa}")

            # Clean up test data
            session.delete(tarefa)
            session.delete(big_rock)
            session.commit()

            print("✅ Test data cleaned up!")
            return True

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🌸 Charlee Backend Setup Test\n")
    print(f"Database URL: {settings.database_url}\n")

    tests = [test_database_connection, test_create_tables, test_models]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed! Backend is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
