#!/bin/bash
# scripts/backup_database.sh
# Script para backup automático do banco de dados (local ou produção)

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Configurações
BACKUP_DIR="${BACKUP_DIR:-backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-7}"

mkdir -p $BACKUP_DIR

echo "💾 Backup Automático - Charlee Database"
echo "========================================"
echo ""

# Decidir qual banco fazer backup
if [ -n "$PRODUCTION_DATABASE_URL" ]; then
    # Backup de produção
    BACKUP_FILE="$BACKUP_DIR/production_backup_$DATE.sql"
    print_info "Fazendo backup do banco de PRODUÇÃO..."

    if pg_dump "$PRODUCTION_DATABASE_URL" > $BACKUP_FILE 2>/dev/null; then
        print_success "Backup de produção criado: $BACKUP_FILE"
    else
        print_warning "Erro ao criar backup de produção"
        exit 1
    fi
else
    # Backup local (Docker)
    LOCAL_CONTAINER="${LOCAL_CONTAINER:-charlee-postgres-1}"
    LOCAL_DB="${LOCAL_DB:-charlee_db}"
    LOCAL_USER="${LOCAL_USER:-charlee}"
    BACKUP_FILE="$BACKUP_DIR/local_backup_$DATE.sql"

    print_info "Fazendo backup do banco LOCAL (Docker)..."

    if docker exec -t $LOCAL_CONTAINER pg_dump -U $LOCAL_USER $LOCAL_DB > $BACKUP_FILE 2>/dev/null; then
        print_success "Backup local criado: $BACKUP_FILE"
    else
        print_warning "Erro ao criar backup local"
        print_info "Container não encontrado ou não está rodando"
        exit 1
    fi
fi

# Comprimir backup
print_info "Comprimindo backup..."
gzip $BACKUP_FILE
BACKUP_FILE="$BACKUP_FILE.gz"
BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
print_success "Backup comprimido: $BACKUP_SIZE"

# Limpar backups antigos
print_info "Limpando backups antigos (>$RETENTION_DAYS dias)..."
DELETED=$(find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ $DELETED -gt 0 ]; then
    print_success "Removidos $DELETED backups antigos"
else
    print_info "Nenhum backup antigo para remover"
fi

# Listar backups disponíveis
echo ""
print_info "Backups disponíveis:"
ls -lh $BACKUP_DIR/*.gz 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'

echo ""
print_success "✨ Backup concluído!"
echo ""
echo "📁 Arquivo: $BACKUP_FILE"
echo "💾 Tamanho: $BACKUP_SIZE"
echo "🗑️  Retenção: $RETENTION_DAYS dias"
echo ""
