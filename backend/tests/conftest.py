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
def sample_user(db):
    """Create a sample User for testing."""
    from api.auth.password import hash_password
    from database.models import User

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("TestPass123"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(sample_user):
    """Create authentication headers with valid JWT token."""
    from api.auth.jwt import create_access_token

    token_data = {
        "user_id": sample_user.id,
        "username": sample_user.username,
        "email": sample_user.email,
    }
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_big_rock(db, sample_user):
    """Create a sample Big Rock for testing."""
    from database.models import BigRock

    big_rock = BigRock(
        name="Health & Wellness", color="#22c55e", active=True, user_id=sample_user.id
    )
    db.add(big_rock)
    db.commit()
    db.refresh(big_rock)
    return big_rock


@pytest.fixture
def sample_task(db, sample_big_rock, sample_user):
    """Create a sample Task for testing."""
    from datetime import date, timedelta

    from database.models import Task

    task = Task(
        description="Walk for 30 minutes",
        type="task",
        big_rock_id=sample_big_rock.id,
        status="pending",
        deadline=date.today() + timedelta(days=7),
        user_id=sample_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def sample_freelance_project(db, sample_user):
    """Create a sample FreelanceProject for testing."""
    from datetime import date, timedelta

    from database.models import FreelanceProject

    project = FreelanceProject(
        user_id=sample_user.id,
        client_name="Test Client",
        project_name="Test Project",
        description="Test project description",
        hourly_rate=100.0,
        estimated_hours=20.0,
        deadline=date.today() + timedelta(days=30),
        status="active",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def sample_work_log(db, sample_user, sample_freelance_project):
    """Create a sample WorkLog for testing."""
    from datetime import date

    from database.models import WorkLog

    work_log = WorkLog(
        user_id=sample_user.id,
        project_id=sample_freelance_project.id,
        work_date=date.today(),
        hours=5.0,
        description="Test work description",
        task_type="development",
        billable=True,
    )
    db.add(work_log)
    db.commit()
    db.refresh(work_log)

    # Update project actual hours
    sample_freelance_project.update_actual_hours(db)
    db.commit()

    return work_log


@pytest.fixture
def sample_invoice(db, sample_user, sample_freelance_project, sample_work_log):
    """Create a sample Invoice for testing."""
    from datetime import date, timedelta

    from database.models import Invoice

    invoice = Invoice(
        user_id=sample_user.id,
        project_id=sample_freelance_project.id,
        invoice_number="INV-TEST-001",
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        total_amount=500.0,
        total_hours=5.0,
        hourly_rate=100.0,
        payment_terms="Net 30",
        status="draft",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Mark work log as invoiced
    sample_work_log.invoiced = True
    sample_work_log.invoice_id = invoice.id
    db.commit()

    return invoice


# ==================== Projects Intelligence System Fixtures ====================


@pytest.fixture
def sample_platform(db, sample_user):
    """Create a sample FreelancePlatform for testing."""
    from database.models import FreelancePlatform

    platform = FreelancePlatform(
        user_id=sample_user.id,
        name="Upwork",
        platform_type="freelance_marketplace",
        active=True,
        auto_collect=True,
        collection_interval_minutes=1440,  # 24 hours = 1440 minutes
    )
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform


@pytest.fixture
def sample_opportunity(db, sample_user, sample_platform):
    """Create a sample FreelanceOpportunity for testing."""
    from database.models import FreelanceOpportunity

    opportunity = FreelanceOpportunity(
        user_id=sample_user.id,
        platform_id=sample_platform.id,
        external_id="upwork-12345",
        title="Build a Full-Stack Web Application",
        description="We need a full-stack developer to build a web application using React and Node.js. Must have experience with PostgreSQL and Docker.",
        client_name="Tech Startup Inc",
        client_rating=4.8,
        client_country="United States",
        client_projects_count=25,
        required_skills=["React", "Node.js", "PostgreSQL", "Docker"],
        client_budget=5000.0,
        client_currency="USD",
        client_deadline_days=30,
        contract_type="fixed_price",
        status="new",
        recommendation="pending",
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@pytest.fixture
def sample_pricing_parameter(db, sample_user):
    """Create a sample PricingParameter for testing."""
    from database.models import PricingParameter

    pricing = PricingParameter(
        user_id=sample_user.id,
        version=1,
        base_hourly_rate=100.0,
        minimum_margin=0.20,
        minimum_project_value=500.0,
        complexity_factors={
            "1-2": 0.7,
            "3-4": 0.9,
            "5-6": 1.0,
            "7-8": 1.2,
            "9-10": 1.5,
        },
        specialization_factors={
            "backend": 1.0,
            "frontend": 0.9,
            "full_stack": 1.1,
            "ai_ml": 1.3,
        },
        deadline_factors={"normal": 1.0, "tight": 1.2, "urgent": 1.5},
        client_factors={"good_rating": 1.0, "new_client": 0.9, "premium": 1.2},
        active=True,
        auto_adjusted=False,
        based_on_executions_count=0,
    )
    db.add(pricing)
    db.commit()
    db.refresh(pricing)
    return pricing


@pytest.fixture
def sample_project_execution(db, sample_user, sample_opportunity):
    """Create a sample ProjectExecution for testing."""
    from datetime import date, timedelta

    from database.models import ProjectExecution

    execution = ProjectExecution(
        user_id=sample_user.id,
        opportunity_id=sample_opportunity.id,
        negotiated_value=5000.0,
        start_date=date.today(),
        planned_end_date=date.today() + timedelta(days=30),
        status="in_progress",
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@pytest.fixture
def sample_negotiation(db, sample_user, sample_opportunity):
    """Create a sample Negotiation for testing."""
    from database.models import Negotiation

    negotiation = Negotiation(
        user_id=sample_user.id,
        opportunity_id=sample_opportunity.id,
        original_budget=5000.0,
        counter_proposal_budget=6000.0,
        counter_proposal_justification="Increased scope requires higher budget",
        final_agreed_budget=5500.0,
        outcome="agreed",
    )
    db.add(negotiation)
    db.commit()
    db.refresh(negotiation)
    return negotiation
