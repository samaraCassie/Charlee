#!/bin/bash

# Script para verificar se o código passará no CI antes de fazer push
# Executa os mesmos checks que o GitHub Actions

set -e  # Para na primeira falha

echo "=========================================="
echo "🔍 CI Pre-Check - Backend Quality & Tests"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de checks
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Função para executar check
run_check() {
    local name=$1
    local command=$2

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶️  Check $TOTAL_CHECKS: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if eval "$command"; then
        echo -e "${GREEN}✅ PASSED${NC}: $name"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ FAILED${NC}: $name"
        return 1
    fi
    echo ""
}

# Verifica se está no diretório correto
if [ ! -f "requirements-dev.txt" ]; then
    echo -e "${RED}❌ Erro: Execute este script do diretório backend/${NC}"
    exit 1
fi

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🐍 Ativando ambiente virtual..."
    source venv/bin/activate
fi

echo ""

# 1. Black - Formatação
run_check "Black (formatação)" \
    "python -m black --check --diff . 2>&1 | head -50"

# 2. Ruff - Linting
run_check "Ruff (linting)" \
    "python -m ruff check ."

# 3. MyPy - Type checking (opcional no CI)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "▶️  Check (opcional): MyPy (type checking)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -m mypy . --ignore-missing-imports 2>&1 | head -20 || echo -e "${YELLOW}⚠️  MyPy: Continue-on-error (opcional)${NC}"
echo ""

# 4. Pytest - Testes
run_check "Pytest (todos os testes)" \
    "python -m pytest tests/ -v --tb=short -x 2>&1 | tail -100"

# Resumo final
echo "=========================================="
echo "📊 RESUMO FINAL"
echo "=========================================="
echo -e "Total de checks obrigatórios: $TOTAL_CHECKS"
echo -e "Checks passados: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Checks falhados: ${RED}$((TOTAL_CHECKS - PASSED_CHECKS))${NC}"
echo ""

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✅ SUCESSO! Seu código deve passar no CI do GitHub Actions${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. git add ."
    echo "  2. git commit -m 'sua mensagem'"
    echo "  3. git push"
    exit 0
else
    echo -e "${RED}❌ FALHOU! Corrija os erros acima antes de fazer push${NC}"
    echo ""
    echo "Dicas:"
    echo "  - Para formatar automaticamente: python -m black ."
    echo "  - Para ver erros do Ruff: python -m ruff check ."
    echo "  - Para rodar um teste específico: python -m pytest tests/caminho/para/teste.py -v"
    exit 1
fi
