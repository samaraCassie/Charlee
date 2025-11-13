# ===========================================
# Charlee Backend Makefile
# ===========================================
# Easy commands for development workflow

.PHONY: help setup install test test-fast test-cov lint format clean run migrate db-reset

# Default target
help:
	@echo "════════════════════════════════════════"
	@echo "Charlee Backend - Available Commands"
	@echo "════════════════════════════════════════"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        - Initial project setup (venv + deps + .env)"
	@echo "  make install      - Install all dependencies"
	@echo "  make install-prod - Install production dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Start development server"
	@echo "  make run-prod     - Start production server"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-fast    - Run tests in parallel"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make test-auth    - Run authentication tests only"
	@echo "  make test-watch   - Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linters (ruff + mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make check        - Run all quality checks"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migration    - Create new migration (msg='description')"
	@echo "  make db-reset     - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove cache and temporary files"
	@echo "  make clean-all    - Remove venv and all generated files"
	@echo ""

# Setup commands
setup:
	@chmod +x setup.sh
	@./setup.sh

install:
	@echo "Installing all dependencies..."
	@pip install -r requirements-dev.txt

install-prod:
	@echo "Installing production dependencies..."
	@pip install -r requirements.txt

# Development commands
run:
	@echo "Starting development server..."
	@uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "Starting production server..."
	@uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Testing commands
test:
	@echo "Running all tests..."
	@pytest tests/ -v

test-fast:
	@echo "Running tests in parallel..."
	@pytest tests/ -n auto

test-cov:
	@echo "Running tests with coverage..."
	@pytest tests/ --cov=api --cov=database --cov-report=html --cov-report=term

test-auth:
	@echo "Running authentication tests..."
	@pytest tests/test_api/test_auth.py tests/test_api/test_auth_advanced.py -v

test-watch:
	@echo "Running tests in watch mode..."
	@pytest-watch tests/

# Code quality commands
lint:
	@echo "Running linters..."
	@ruff check .
	@mypy api/ database/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	@black .
	@ruff check --fix .

check: lint test
	@echo "✨ All checks passed!"

# Database commands
migrate:
	@echo "Running database migrations..."
	@alembic upgrade head

migration:
	@echo "Creating new migration..."
	@alembic revision --autogenerate -m "$(msg)"

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		alembic downgrade base; \
		alembic upgrade head; \
		echo "Database reset completed"; \
	fi

# Cleanup commands
clean:
	@echo "Cleaning cache and temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/
	@echo "Cleanup completed"

clean-all: clean
	@echo "Removing virtual environment..."
	@rm -rf venv/
	@echo "Full cleanup completed"
