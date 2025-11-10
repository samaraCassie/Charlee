"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from database.config import Base, get_db

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db():
    """
    Database fixture that creates schema and cleans up after each test.

    Yields:
        Session: SQLAlchemy database session
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    TestClient fixture with database override.

    Args:
        db: Database session fixture

    Yields:
        TestClient: FastAPI test client
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_big_rock(db):
    """Create a sample Big Rock for testing."""
    from database.models import BigRock

    big_rock = BigRock(name="Health & Wellness", color="#22c55e", active=True)
    db.add(big_rock)
    db.commit()
    db.refresh(big_rock)
    return big_rock


@pytest.fixture
def sample_task(db, sample_big_rock):
    """Create a sample Task for testing."""
    from database.models import Task
    from datetime import date, timedelta

    task = Task(
        description="Walk for 30 minutes",
        type="task",
        big_rock_id=sample_big_rock.id,
        status="pending",
        deadline=date.today() + timedelta(days=7),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
