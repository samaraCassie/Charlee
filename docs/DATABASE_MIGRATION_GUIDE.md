# 📦 Guia de Migração: PostgreSQL Local → Produção

> Migrar seu banco PostgreSQL do container Docker local para produção

## 🎯 Opção Recomendada: Supabase

### Por que Supabase?
- ✅ PostgreSQL 100% compatível
- ✅ Suporta pgvector (necessário para a aplicação)
- ✅ Tier gratuito: 500MB storage
- ✅ Backup automático incluído
- ✅ SSL/TLS por padrão
- ✅ Dashboard web para gerenciar dados

---

## 📋 Passo 1: Criar Conta no Supabase

1. Acesse: https://supabase.com
2. Criar conta (grátis)
3. Criar novo projeto:
   - **Name**: charlee-production
   - **Database Password**: [gerar senha forte]
   - **Region**: São Paulo (Brazil) ou US East
4. Aguardar provisioning (~2min)

---

## 📋 Passo 2: Exportar Banco Local

### 2.1 Verificar nome do container PostgreSQL

```bash
# Listar containers
docker ps | grep postgres

# Ou se estiver usando docker-compose
cd docker/
docker-compose ps
```

### 2.2 Criar dump do banco atual

```bash
# Método 1: Dump completo (schema + dados)
docker exec -t <container-name> pg_dump -U charlee charlee_db > charlee_backup.sql

# Método 2: Se preferir dump customizado (compactado)
docker exec -t <container-name> pg_dump -U charlee -Fc charlee_db > charlee_backup.dump

# Método 3: Dump apenas dados (se schema já existe)
docker exec -t <container-name> pg_dump -U charlee --data-only charlee_db > charlee_data.sql
```

### 2.3 Verificar backup criado

```bash
# Verificar tamanho do arquivo
ls -lh charlee_backup.sql

# Ver primeiras linhas
head -n 50 charlee_backup.sql
```

---

## 📋 Passo 3: Conectar ao Supabase

### 3.1 Obter credenciais

No dashboard do Supabase:
1. Ir em **Settings** → **Database**
2. Copiar **Connection String**:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### 3.2 Testar conexão

```bash
# Instalar psql se necessário (no Mac)
brew install postgresql

# Ou no Ubuntu/Debian
sudo apt-get install postgresql-client

# Testar conexão
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
```

---

## 📋 Passo 4: Importar Dados para Supabase

### 4.1 Restaurar schema e dados

```bash
# Método 1: Restaurar dump SQL
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" < charlee_backup.sql

# Método 2: Restaurar dump customizado
pg_restore --verbose --clean --no-acl --no-owner \
  -h db.[PROJECT-REF].supabase.co \
  -U postgres \
  -d postgres \
  charlee_backup.dump
```

### 4.2 Verificar migração

```bash
# Conectar ao Supabase
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Verificar tabelas
\dt

# Verificar dados
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM tasks;
SELECT COUNT(*) FROM big_rocks;

# Sair
\q
```

---

## 📋 Passo 5: Habilitar pgvector (se necessário)

```sql
-- Conectar ao Supabase e executar
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 📋 Passo 6: Atualizar Aplicação

### 6.1 Atualizar variáveis de ambiente

```bash
# Criar/editar .env (NÃO commitar!)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Ou usar connection pooling (recomendado para produção)
DATABASE_URL=postgresql://postgres:[PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

### 6.2 Atualizar configuração de pool

No arquivo `backend/database/config.py`, já está configurado para produção:

```python
# Connection pooling já está otimizado
pool_size=5
max_overflow=10
pool_timeout=30
pool_recycle=3600  # 1 hora
```

Para Supabase, ajustar para:

```python
# Recomendado para Supabase (tier free tem limite de conexões)
pool_size=2
max_overflow=3
```

---

## 📋 Passo 7: Testar Localmente com Banco de Produção

```bash
# 1. Atualizar .env com DATABASE_URL do Supabase
# 2. Reiniciar aplicação
cd /home/user/Charlee

# Se usando Docker
docker-compose down
docker-compose up

# Ou diretamente
cd backend
uvicorn api.main:app --reload

# 3. Testar health check
curl http://localhost:8000/health
```

---

## 🔄 Alternativa: Script de Migração Automatizado

Criar script para facilitar migrações futuras:

```bash
#!/bin/bash
# scripts/migrate_to_production.sh

set -e

echo "🚀 Migrando banco local para produção..."

# Variáveis
LOCAL_CONTAINER="charlee-postgres-1"  # Ajustar nome do container
LOCAL_DB="charlee_db"
LOCAL_USER="charlee"
BACKUP_FILE="charlee_backup_$(date +%Y%m%d_%H%M%S).sql"

# 1. Criar backup local
echo "📦 Criando backup local..."
docker exec -t $LOCAL_CONTAINER pg_dump -U $LOCAL_USER $LOCAL_DB > $BACKUP_FILE

# 2. Verificar backup
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ Backup criado: $BACKUP_FILE ($(du -h $BACKUP_FILE | cut -f1))"
else
    echo "❌ Erro ao criar backup"
    exit 1
fi

# 3. Importar para Supabase
echo "📤 Importando para Supabase..."
if [ -z "$SUPABASE_DATABASE_URL" ]; then
    echo "❌ Variável SUPABASE_DATABASE_URL não definida"
    echo "   Execute: export SUPABASE_DATABASE_URL='postgresql://...'"
    exit 1
fi

psql "$SUPABASE_DATABASE_URL" < $BACKUP_FILE

echo "✅ Migração concluída!"
echo "📝 Backup salvo em: $BACKUP_FILE"
```

Usar o script:

```bash
# Dar permissão
chmod +x scripts/migrate_to_production.sh

# Exportar URL do Supabase
export SUPABASE_DATABASE_URL='postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres'

# Executar migração
./scripts/migrate_to_production.sh
```

---

## 🎯 Outras Opções de Banco para Produção

### Opção 2: Render PostgreSQL

**Prós:**
- Setup simples
- $7/mês (always-on)
- Backups automáticos

**Migração:**
```bash
# 1. Criar PostgreSQL no Render
# 2. Copiar Internal Database URL
# 3. Restaurar backup
psql "postgres://user:pass@hostname.render.com/dbname" < charlee_backup.sql
```

**Custo:** $7/mês (plano starter)

---

### Opção 3: Railway PostgreSQL

**Prós:**
- DX excelente
- Integração com deploy da app
- Métricas em tempo real

**Migração:**
```bash
# 1. Criar PostgreSQL no Railway
# 2. Usar railway CLI
railway login
railway run psql < charlee_backup.sql
```

**Custo:** ~$5-10/mês (pay-as-you-go)

---

### Opção 4: Neon (Serverless PostgreSQL)

**Prós:**
- Serverless (escala para zero)
- Branching de databases
- Tier free: 512MB

**Migração:**
```bash
# Similar ao Supabase
psql "postgresql://user:pass@ep-xxx.neon.tech/dbname" < charlee_backup.sql
```

**Custo:** $0 (free tier) → $19/mês (pro)

---

## 📊 Comparação de Custos

| Provedor | Free Tier | Custo Mensal | Backup Auto | Connection Pool | Recomendação |
|----------|-----------|--------------|-------------|-----------------|--------------|
| **Supabase** | 500MB | $0 → $25 | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Render** | 90 dias | $7 | ✅ | ✅ | ⭐⭐⭐⭐ |
| **Railway** | $5 crédito | $5-10 | ✅ | ✅ | ⭐⭐⭐⭐ |
| **Neon** | 512MB | $0 → $19 | ✅ | ✅ | ⭐⭐⭐⭐ |

---

## ⚠️ Checklist de Segurança

Antes de ir para produção:

- [ ] **Senha forte** no banco de produção
  ```bash
  # Gerar senha segura
  openssl rand -base64 32
  ```

- [ ] **SSL/TLS habilitado** (Supabase já vem por padrão)

- [ ] **Credenciais em .env** (nunca no código)
  ```bash
  # .gitignore deve incluir
  .env
  .env.local
  .env.production
  ```

- [ ] **Backup automático configurado**

- [ ] **Limitar IPs** (se possível)
  - No Supabase: Database → Settings → Connection pooling

- [ ] **Monitoring configurado**
  - Supabase tem dashboard built-in
  - Adicionar Sentry para erros da app

---

## 🔄 Estratégia de Backup Contínuo

### Backup automático diário

```bash
#!/bin/bash
# scripts/backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/charlee_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# Backup do Supabase
pg_dump "$SUPABASE_DATABASE_URL" > $BACKUP_FILE

# Comprimir
gzip $BACKUP_FILE

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "✅ Backup criado: $BACKUP_FILE.gz"
```

### Agendar com cron

```bash
# Editar crontab
crontab -e

# Adicionar (backup diário às 3am)
0 3 * * * /path/to/scripts/backup_database.sh
```

---

## 🚀 Próximos Passos

Após migrar o banco:

1. **Deploy da Aplicação**
   - Ver: `PRODUCTION_DEPLOYMENT_OPTIONS.md`
   - Recomendado: Render (backend) + Vercel (frontend)

2. **Redis para Produção**
   - Recomendado: Upstash (serverless)
   - Free tier: 10k commands/dia

3. **Monitoring**
   - Uptime: UptimeRobot
   - Errors: Sentry
   - Logs: Supabase Dashboard

4. **CI/CD**
   - GitHub Actions para deploy automático
   - Testes antes de deploy

---

## 📚 Recursos Úteis

- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [PostgreSQL Migration Best Practices](https://www.postgresql.org/docs/current/backup.html)
- [pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)

---

**Criado em:** 2025-11-13
**Versão:** 1.0
**Recomendação:** ⭐ Supabase Free para começar → Supabase Pro quando escalar
