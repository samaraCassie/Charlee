#!/bin/bash
# Script para verificar se o código vai passar no CI antes de fazer merge
# Uso: ./check-ci.sh

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}🔍 Verificando CI localmente...${NC}"
echo ""

FAILED=0

# ==================== Backend Linting ====================
echo -e "${BOLD}📝 Backend - Linting & Type Check${NC}"
cd backend

echo "  ✓ Running Black..."
if python -m black --check . > /dev/null 2>&1; then
  echo -e "    ${GREEN}✅ Black: OK${NC}"
else
  echo -e "    ${RED}❌ Black: FAILED${NC}"
  FAILED=1
fi

echo "  ✓ Running Ruff..."
if python -m ruff check . > /dev/null 2>&1; then
  echo -e "    ${GREEN}✅ Ruff: OK${NC}"
else
  echo -e "    ${RED}❌ Ruff: FAILED${NC}"
  FAILED=1
fi

echo "  ✓ Running MyPy..."
if python -m mypy . --ignore-missing-imports > /dev/null 2>&1; then
  echo -e "    ${GREEN}✅ MyPy: OK${NC}"
else
  echo -e "    ${YELLOW}⚠️  MyPy: WARNINGS (continue-on-error)${NC}"
fi

# ==================== Backend Tests ====================
echo ""
echo -e "${BOLD}🧪 Backend - Tests${NC}"
export DATABASE_URL="sqlite:///:memory:"
export REDIS_URL="redis://localhost:6379"
export OPENAI_API_KEY="sk-test-key"
export SECRET_KEY="test-secret"
export RATE_LIMIT_ENABLED=false
export LOG_LEVEL=ERROR
export PYTHONPATH="$(pwd)"

if python -m pytest tests/ -q --tb=line 2>&1 | tee /tmp/pytest_output.txt | grep -q "passed"; then
  TESTS=$(tail -1 /tmp/pytest_output.txt)
  echo -e "    ${GREEN}✅ Tests: $TESTS${NC}"
else
  echo -e "    ${RED}❌ Tests: FAILED${NC}"
  FAILED=1
fi

# ==================== Frontend Linting ====================
echo ""
echo -e "${BOLD}📝 Frontend - Linting & Type Check${NC}"
cd ../interfaces/web

echo "  ✓ Running ESLint..."
if npm run lint > /dev/null 2>&1; then
  echo -e "    ${GREEN}✅ ESLint: OK${NC}"
else
  echo -e "    ${RED}❌ ESLint: FAILED${NC}"
  FAILED=1
fi

echo "  ✓ Running TypeScript Build..."
if npm run build > /dev/null 2>&1; then
  echo -e "    ${GREEN}✅ TypeScript: OK${NC}"
else
  echo -e "    ${RED}❌ TypeScript: FAILED${NC}"
  FAILED=1
fi

# ==================== Frontend Tests ====================
echo ""
echo -e "${BOLD}🧪 Frontend - Tests${NC}"

if npm test 2>&1 | tee /tmp/vitest_output.txt | grep -q "passed"; then
  TESTS=$(grep "Test Files" /tmp/vitest_output.txt | tail -1)
  echo -e "    ${GREEN}✅ Tests: $TESTS${NC}"
else
  echo -e "    ${RED}❌ Tests: FAILED${NC}"
  FAILED=1
fi

# ==================== Summary ====================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}${BOLD}✅ Todos os checks passaram! Pronto para merge 🚀${NC}"
  exit 0
else
  echo -e "${RED}${BOLD}❌ Alguns checks falharam. Corrija antes de fazer merge.${NC}"
  exit 1
fi
