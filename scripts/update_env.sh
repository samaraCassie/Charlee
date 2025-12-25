#!/bin/bash
# Script para adicionar variáveis faltantes ao .env sem sobrescrever as existentes

ENV_FILE="/home/sam-cassie/GitHub/Charlee/docker/.env"
BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

echo "🔧 Atualizando arquivo .env com novas variáveis..."

# Criar backup
cp "$ENV_FILE" "$BACKUP_FILE"
echo "✅ Backup criado em: $BACKUP_FILE"

# Função para adicionar variável se não existir
add_if_missing() {
    local var_name="$1"
    local var_value="$2"
    local comment="$3"
    
    if ! grep -q "^${var_name}=" "$ENV_FILE"; then
        echo "" >> "$ENV_FILE"
        if [ -n "$comment" ]; then
            echo "# $comment" >> "$ENV_FILE"
        fi
        echo "${var_name}=${var_value}" >> "$ENV_FILE"
        echo "➕ Adicionado: $var_name"
    else
        echo "⏭️  Já existe: $var_name"
    fi
}

# Adicionar novas variáveis

add_if_missing "FRONTEND_URL" "http://localhost:3000" "Frontend URL"

add_if_missing "GOOGLE_CALENDAR_CLIENT_ID" "your-google-client-id" "Google Calendar OAuth"
add_if_missing "GOOGLE_CALENDAR_CLIENT_SECRET" "your-google-client-secret" ""
add_if_missing "GOOGLE_CALENDAR_REDIRECT_URI" "http://localhost:3000/calendar/callback/google" ""

add_if_missing "MICROSOFT_CALENDAR_CLIENT_ID" "your-microsoft-client-id" "Microsoft Calendar OAuth"
add_if_missing "MICROSOFT_CALENDAR_CLIENT_SECRET" "your-microsoft-client-secret" ""
add_if_missing "MICROSOFT_CALENDAR_REDIRECT_URI" "http://localhost:3000/calendar/callback/microsoft" ""

# Adicionar PostgreSQL credentials se não existirem
add_if_missing "POSTGRES_USER" "charlee" "PostgreSQL"
add_if_missing "POSTGRES_PASSWORD" "charlee123" ""
add_if_missing "POSTGRES_DB" "charlee_db" ""

# Adicionar Redis
add_if_missing "REDIS_URL" "redis://redis:6379" "Redis"

# Adicionar JWT secret
add_if_missing "JWT_SECRET_KEY" "$(openssl rand -hex 32)" "JWT Authentication (generated)"
add_if_missing "JWT_REFRESH_SECRET_KEY" "$(openssl rand -hex 32)" ""

echo ""
echo "✅ Arquivo .env atualizado com sucesso!"
echo "📝 Backup salvo em: $BACKUP_FILE"
echo ""
echo "⚠️  IMPORTANTE: Preencha as seguintes variáveis com valores reais:"
echo "   - GOOGLE_CALENDAR_CLIENT_ID"
echo "   - GOOGLE_CALENDAR_CLIENT_SECRET"
echo "   - MICROSOFT_CALENDAR_CLIENT_ID"
echo "   - MICROSOFT_CALENDAR_CLIENT_SECRET"
echo ""
