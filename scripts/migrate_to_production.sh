#!/bin/bash
# scripts/migrate_to_production.sh
# Script para migrar banco PostgreSQL local para produção

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cor
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo ""
echo "🚀 Migração de Banco de Dados - Charlee"
echo "========================================"
echo ""

# Configurações
LOCAL_CONTAINER="${LOCAL_CONTAINER:-charlee-postgres-1}"
LOCAL_DB="${LOCAL_DB:-charlee_db}"
LOCAL_USER="${LOCAL_USER:-charlee}"
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/charlee_backup_$(date +%Y%m%d_%H%M%S).sql"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Verificar se container existe
print_info "Verificando container Docker..."
if ! docker ps | grep -q "$LOCAL_CONTAINER"; then
    print_error "Container '$LOCAL_CONTAINER' não encontrado"
    echo ""
    echo "Containers disponíveis:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    echo ""
    echo "💡 Dica: Defina o nome correto do container:"
    echo "   export LOCAL_CONTAINER='nome-do-container'"
    exit 1
fi
print_success "Container encontrado: $LOCAL_CONTAINER"

# Criar backup local
print_info "Criando backup do banco local..."
if docker exec -t $LOCAL_CONTAINER pg_dump -U $LOCAL_USER $LOCAL_DB > $BACKUP_FILE 2>/dev/null; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    print_success "Backup criado: $BACKUP_FILE ($BACKUP_SIZE)"
else
    print_error "Erro ao criar backup"
    exit 1
fi

# Verificar se backup tem conteúdo
if [ ! -s "$BACKUP_FILE" ]; then
    print_error "Backup está vazio!"
    exit 1
fi

# Mostrar estatísticas do backup
print_info "Estatísticas do backup:"
echo "   📦 Tamanho: $(du -h $BACKUP_FILE | cut -f1)"
echo "   📝 Linhas: $(wc -l < $BACKUP_FILE)"
echo ""

# Verificar URL de produção
if [ -z "$PRODUCTION_DATABASE_URL" ]; then
    print_warning "Variável PRODUCTION_DATABASE_URL não definida"
    echo ""
    echo "Para importar para produção, defina a URL do banco:"
    echo ""
    echo "  export PRODUCTION_DATABASE_URL='postgresql://user:pass@host:5432/dbname'"
    echo ""
    echo "Exemplos de URL por provedor:"
    echo ""
    echo "  📘 Supabase:"
    echo "     postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
    echo ""
    echo "  🎨 Render:"
    echo "     postgresql://user:pass@hostname.render.com/dbname"
    echo ""
    echo "  🚂 Railway:"
    echo "     postgresql://user:pass@containers-us-west-xxx.railway.app:5432/railway"
    echo ""
    print_success "Backup local concluído! Arquivo: $BACKUP_FILE"
    exit 0
fi

# Confirmar importação
print_warning "Você está prestes a importar dados para PRODUÇÃO"
echo ""
echo "Destino: $PRODUCTION_DATABASE_URL"
echo ""
read -p "Tem certeza que deseja continuar? (yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Operação cancelada pelo usuário"
    exit 0
fi

# Importar para produção
print_info "Importando para banco de produção..."
if psql "$PRODUCTION_DATABASE_URL" < $BACKUP_FILE; then
    print_success "Dados importados com sucesso!"
else
    print_error "Erro ao importar dados"
    print_warning "Backup salvo em: $BACKUP_FILE"
    exit 1
fi

# Verificar dados importados
print_info "Verificando dados importados..."
psql "$PRODUCTION_DATABASE_URL" -c "
    SELECT
        'users' as table_name, COUNT(*) as count FROM users
    UNION ALL
    SELECT 'big_rocks', COUNT(*) FROM big_rocks
    UNION ALL
    SELECT 'tasks', COUNT(*) FROM tasks
    ORDER BY table_name;
" 2>/dev/null || print_warning "Não foi possível verificar contagem (tabelas podem não existir)"

# Sucesso
echo ""
print_success "🎉 Migração concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Atualizar variáveis de ambiente da aplicação"
echo "   2. Testar conexão: curl http://localhost:8000/health"
echo "   3. Fazer deploy da aplicação"
echo ""
echo "💾 Backup mantido em: $BACKUP_FILE"
echo ""
