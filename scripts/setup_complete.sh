#!/bin/bash
# Script de setup completo do projeto Charlee

set -e  # Exit on error

echo "🚀 Iniciando setup completo do Charlee..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório raiz do projeto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Diretório do projeto: $PROJECT_ROOT"
echo ""

# 1. Verificar pré-requisitos
echo "1️⃣  Verificando pré-requisitos..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Instale Docker primeiro.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado. Instale Docker Compose primeiro.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker e Docker Compose encontrados${NC}"
echo ""

# 2. Configurar .env
echo "2️⃣  Configurando variáveis de ambiente..."

if [ -f "docker/.env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env já existe. Criando backup...${NC}"
    cp docker/.env "docker/.env.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Executar script de atualização do .env
if [ -f "scripts/update_env.sh" ]; then
    bash scripts/update_env.sh
else
    echo -e "${YELLOW}⚠️  Script update_env.sh não encontrado. Copie .env.example manualmente.${NC}"
    if [ ! -f "docker/.env" ]; then
        cp docker/.env.example docker/.env
        echo -e "${GREEN}✅ Criado docker/.env a partir de .env.example${NC}"
    fi
fi

echo ""

# 3. Verificar OpenAI API Key
echo "3️⃣  Verificando OpenAI API Key..."

if ! grep -q "^OPENAI_API_KEY=sk-" docker/.env; then
    echo -e "${RED}❌ OpenAI API Key não configurada no docker/.env${NC}"
    echo "Por favor, adicione sua API key:"
    echo "  OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

echo -e "${GREEN}✅ OpenAI API Key configurada${NC}"
echo ""

# 4. Iniciar containers Docker
echo "4️⃣  Iniciando containers Docker..."

cd docker
docker-compose down 2>/dev/null || true
docker-compose up -d

echo -e "${GREEN}✅ Containers iniciados${NC}"
echo ""

# 5. Aguardar PostgreSQL ficar pronto
echo "5️⃣  Aguardando PostgreSQL ficar pronto..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec charlee_db pg_isready -U charlee &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL está pronto${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ PostgreSQL não ficou pronto em tempo hábil${NC}"
    exit 1
fi

echo ""

# 6. Executar migrations
echo "6️⃣  Executando migrations do banco de dados..."

docker exec charlee_backend alembic upgrade head

echo -e "${GREEN}✅ Migrations executadas${NC}"
echo ""

# 7. Verificar pgvector
echo "7️⃣  Verificando instalação do pgvector..."

if docker exec charlee_db psql -U charlee -d charlee_db -c "SELECT * FROM pg_extension WHERE extname='vector';" | grep -q "vector"; then
    echo -e "${GREEN}✅ pgvector instalado e funcionando${NC}"
else
    echo -e "${YELLOW}⚠️  pgvector não encontrado. Tentando instalar...${NC}"
    docker exec charlee_db psql -U charlee -d charlee_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    if docker exec charlee_db psql -U charlee -d charlee_db -c "SELECT * FROM pg_extension WHERE extname='vector';" | grep -q "vector"; then
        echo -e "${GREEN}✅ pgvector instalado com sucesso${NC}"
    else
        echo -e "${RED}❌ Falha ao instalar pgvector. Verifique manualmente.${NC}"
    fi
fi

echo ""

# 8. Verificar WorkLog table
echo "8️⃣  Verificando tabela WorkLog..."

if docker exec charlee_db psql -U charlee -d charlee_db -c "\dt work_logs;" | grep -q "work_logs"; then
    echo -e "${GREEN}✅ Tabela work_logs criada${NC}"
else
    echo -e "${YELLOW}⚠️  Tabela work_logs não encontrada. Execute a migration 009 manualmente.${NC}"
fi

echo ""

# 9. Verificar embedding column
echo "9️⃣  Verificando coluna embedding..."

if docker exec charlee_db psql -U charlee -d charlee_db -c "\d freelance_opportunities;" 2>/dev/null | grep -q "embedding"; then
    echo -e "${GREEN}✅ Coluna embedding configurada${NC}"
else
    echo -e "${YELLOW}⚠️  Coluna embedding não encontrada. Isso é normal se você ainda não executou a migration 009.${NC}"
fi

echo ""

# 10. Testar backup system
echo "🔟 Testando sistema de backup..."

if docker exec charlee_backend python -c "
from services.system_monitor import system_monitor
print('Backup dir:', system_monitor.backup_dir)
print('Uptime:', system_monitor.get_uptime_formatted())
" 2>/dev/null; then
    echo -e "${GREEN}✅ Sistema de backup configurado${NC}"
else
    echo -e "${YELLOW}⚠️  Sistema de backup pode não estar completamente funcional${NC}"
fi

echo ""

# 11. Resumo final
echo "═══════════════════════════════════════════════════════"
echo "🎉 SETUP COMPLETO!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📊 Status dos Serviços:"
echo "  • PostgreSQL (com pgvector): http://localhost:5432"
echo "  • Redis: http://localhost:6379"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Próximos Passos:"
echo "  1. Acesse http://localhost:8000/docs"
echo "  2. Crie um usuário via POST /api/v1/auth/register"
echo "  3. Faça login via POST /api/v1/auth/login"
echo "  4. Teste as funcionalidades!"
echo ""
echo "🔧 Comandos Úteis:"
echo "  • Ver logs: docker logs charlee_backend -f"
echo "  • Parar: docker-compose down"
echo "  • Reiniciar: docker-compose restart"
echo "  • Backup manual: curl -X POST http://localhost:8000/api/v1/settings/backup"
echo ""
echo "⚠️  Não esqueça de configurar:"
echo "  • Google Calendar credentials (se usar calendar sync)"
echo "  • Microsoft Calendar credentials (se usar calendar sync)"
echo ""
echo "📚 Documentação completa: SETUP.md"
echo "═══════════════════════════════════════════════════════"
