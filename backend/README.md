# 🚀 Charlee Backend

FastAPI backend for the Charlee personal intelligence system.

## 🛠️ Tech Stack

- **Python** 3.12+
- **FastAPI** 0.115.0+ - Modern web framework
- **SQLAlchemy** 2.0+ - ORM
- **Pydantic** 2.5+ - Data validation
- **PostgreSQL** - Production database
- **Redis** - Cache and sessions
- **Alembic** - Database migrations
- **Pytest** - Testing framework
- **agno** - AI agent framework

## 📋 Prerequisites

- Python 3.12 or higher
- PostgreSQL 14+ (or Docker)
- Redis 7+ (or Docker)
- pip or uv

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone https://github.com/samaraCassie/Charlee.git
cd Charlee/backend
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### 4. Environment Variables
```bash
cp docker/.env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://charlee:your_password@localhost:5432/charlee_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# AI Services
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### 5. Database Setup

**Option A: Docker (Recommended for Development)**
```bash
cd docker
docker-compose up -d postgres redis
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb charlee_db

# Or with psql
psql -c "CREATE DATABASE charlee_db;"
```

### 6. Run Migrations
```bash
# Apply all migrations
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

### 7. Run the Application
```bash
# Development server with auto-reload
uvicorn api.main:app --reload --port 8000

# Production server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run Specific Test File
```bash
pytest tests/test_api/test_tasks.py -v
```

### Run Tests in Parallel
```bash
pytest -n auto  # Requires pytest-xdist
```

## 📊 Code Quality

### Format Code
```bash
black . --line-length=100
```

### Lint Code
```bash
ruff check .
ruff check . --fix  # Auto-fix issues
```

### Type Checking
```bash
mypy . --ignore-missing-imports
```

### Run All Quality Checks
```bash
black . --line-length=100 && ruff check . --fix && mypy . --ignore-missing-imports && pytest
```

### Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📁 Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI app configuration
│   └── routes/              # API route handlers
│       ├── big_rocks.py     # Big Rocks endpoints
│       ├── tasks.py         # Tasks endpoints
│       ├── agent.py         # AI Agent endpoints
│       └── ...
├── agent/
│   ├── core_agent.py        # Core AI agent
│   ├── orchestrator.py      # Agent orchestration
│   └── specialized_agents/  # Specialized agents
├── database/
│   ├── config.py            # DB connection setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   └── migrations/          # Alembic migrations
├── skills/                  # Agent skills
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api/            # API tests
│   ├── test_agents/         # Agent tests
│   └── test_database/       # Database tests
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── alembic.ini             # Alembic configuration
├── pytest.ini              # Pytest configuration
└── mypy.ini                # MyPy configuration
```

## 🔧 Development Workflow

### 1. Create a New Migration
```bash
# After modifying models.py
alembic revision --autogenerate -m "add_new_table"

# Review the generated migration in database/migrations/versions/
# Then apply it
alembic upgrade head
```

### 2. Add a New Endpoint
```python
# 1. Define schema in database/schemas.py
class MyDataCreate(BaseModel):
    name: str
    description: Optional[str] = None

# 2. Add CRUD function in database/crud.py
def create_my_data(db: Session, data: MyDataCreate) -> MyData:
    db_data = MyData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

# 3. Create route in api/routes/my_route.py
@router.post("/", response_model=MyDataResponse, status_code=201)
def create(data: MyDataCreate, db: Session = Depends(get_db)):
    return crud.create_my_data(db, data)

# 4. Include router in api/main.py
from api.routes import my_route
app.include_router(my_route.router, prefix="/api/v1/my-route", tags=["My Route"])
```

### 3. Write Tests
```python
# tests/test_api/test_my_route.py
def test_create_my_data(client, db):
    response = client.post("/api/v1/my-route", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn api.main:app --reload --port 8001
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -h localhost -U charlee -d charlee_db

# Reset database
alembic downgrade base
alembic upgrade head
```

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements-dev.txt
```

## 📖 Additional Documentation

- [Quality Standards](../standards/BACKEND_STANDARDS.md)
- [Git Workflow](../standards/GIT_STANDARDS.md)
- [Testing Guide](tests/README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Quality Roadmap](../QUALITY_ROADMAP.md)

## 🔗 Useful Commands

```bash
# Database
alembic upgrade head                    # Apply migrations
alembic downgrade -1                    # Rollback one migration
alembic current                         # Show current version
alembic history                         # Show migration history

# Testing
pytest -v                               # Verbose output
pytest --lf                             # Run last failed tests
pytest -k "test_tasks"                  # Run tests matching pattern
pytest --cov=. --cov-report=term        # Coverage in terminal

# Code Quality
black . --check                         # Check formatting without changes
ruff check . --statistics               # Show linting statistics
mypy . --show-error-codes               # Show error codes

# Development
uvicorn api.main:app --reload           # Auto-reload on changes
uvicorn api.main:app --log-level debug  # Debug logging
```

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License.
