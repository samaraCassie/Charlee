#!/bin/bash

# ===========================================
# Charlee Backend Setup Script
# ===========================================
# This script sets up the development environment
# with all necessary dependencies and configurations

set -e  # Exit on error

echo "🚀 Setting up Charlee Backend..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
print_success "Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
print_info "Installing production dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "Production dependencies installed"

print_info "Installing development dependencies..."
pip install -r requirements-dev.txt > /dev/null 2>&1
print_success "Development dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created"
        print_info "⚠️  Please update .env with your actual configuration values"
    else
        print_error ".env.example not found"
    fi
else
    print_success ".env file already exists"
fi

# Install pre-commit hooks
if [ -f "../.pre-commit-config.yaml" ]; then
    print_info "Installing pre-commit hooks..."
    pre-commit install > /dev/null 2>&1
    print_success "Pre-commit hooks installed"
fi

echo ""
echo "════════════════════════════════════════"
echo "✨ Setup completed successfully!"
echo "════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Update .env with your configuration"
echo ""
echo "  3. Run database migrations:"
echo "     alembic upgrade head"
echo ""
echo "  4. Run tests:"
echo "     pytest tests/"
echo ""
echo "  5. Start the development server:"
echo "     uvicorn api.main:app --reload"
echo ""
