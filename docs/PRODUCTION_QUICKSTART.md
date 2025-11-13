# ⚡ Quick Start - Deploy em Produção

> Guia rápido para colocar o Charlee em produção em minutos

## 🎯 Stack Recomendada (Gratuita)

```
✅ Banco de Dados: Supabase (500MB free)
✅ Backend: Render (750h/mês free)
✅ Frontend: Vercel (ilimitado free)
✅ Redis: Upstash (10k commands/dia free)
💰 Custo Total: $0/mês
```

---

## 📦 Passo 1: Migrar Banco de Dados (5min)

### 1.1 Criar conta no Supabase

1. Acessar https://supabase.com
2. Criar novo projeto:
   - Nome: `charlee-production`
   - Região: `São Paulo` ou `US East`
   - Senha: Gerar senha forte
3. Aguardar provisioning (~2min)

### 1.2 Migrar dados locais

```bash
# Exportar banco local
docker exec -t charlee-postgres-1 pg_dump -U charlee charlee_db > charlee_backup.sql

# Ou usar script automatizado
./scripts/migrate_to_production.sh

# Definir URL de produção
export PRODUCTION_DATABASE_URL='postgresql://postgres:[SUA-SENHA]@db.[PROJECT-REF].supabase.co:5432/postgres'

# Importar para Supabase
psql "$PRODUCTION_DATABASE_URL" < charlee_backup.sql
```

**✅ Pronto!** Banco de dados em produção configurado.

---

## 🚀 Passo 2: Deploy do Backend (3min)

### 2.1 Preparar repositório

```bash
# Criar arquivo de configuração do Render
cat > render.yaml << 'EOF'
services:
  - type: web
    name: charlee-backend
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: JWT_REFRESH_SECRET_KEY
        generateValue: true
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: APP_ENV
        value: production
      - key: DEBUG
        value: false
EOF

# Commit
git add render.yaml
git commit -m "Add Render configuration"
git push
```

### 2.2 Deploy no Render

1. Acessar https://render.com
2. Conectar repositório GitHub
3. Selecionar branch `main`
4. Adicionar variáveis de ambiente:
   ```
   DATABASE_URL=postgresql://postgres:...@db.xxx.supabase.co:5432/postgres
   REDIS_URL=(copiar do Upstash)
   ANTHROPIC_API_KEY=sk-ant-...
   ```
5. Clicar em **Create Web Service**

**✅ Pronto!** Backend no ar em ~3min.

---

## 🎨 Passo 3: Deploy do Frontend (2min)

### 3.1 Atualizar configuração

```bash
# Criar arquivo de ambiente para Vercel
cat > interfaces/web/.env.production << 'EOF'
VITE_API_URL=https://charlee-backend.onrender.com/api/v1
EOF
```

### 3.2 Deploy no Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd interfaces/web
vercel --prod
```

Ou via dashboard:
1. Acessar https://vercel.com
2. Importar repositório
3. Configurar:
   - Framework: Vite
   - Root Directory: `interfaces/web`
   - Build Command: `npm run build`
4. Deploy

**✅ Pronto!** Frontend no ar!

---

## 🔴 Passo 4: Configurar Redis (2min)

### 4.1 Criar database no Upstash

1. Acessar https://upstash.com
2. Criar novo Redis database:
   - Nome: `charlee-redis`
   - Região: Próxima do backend
3. Copiar `REDIS_URL`

### 4.2 Adicionar ao backend

No dashboard do Render:
1. Ir em **Environment**
2. Adicionar variável:
   ```
   REDIS_URL=redis://default:[PASSWORD]@[HOST].upstash.io:6379
   ```
3. Salvar e aguardar redeploy

**✅ Pronto!** Redis configurado.

---

## ✅ Verificar Deploy

```bash
# Health check do backend
curl https://charlee-backend.onrender.com/health

# Deve retornar
{
  "service": "charlee-backend",
  "version": "2.0.0",
  "status": "healthy",
  "checks": {
    "database": { "status": "healthy" },
    "tables": { "status": "healthy" }
  }
}
```

**Acessar aplicação:**
- Frontend: https://seu-app.vercel.app
- Backend API: https://charlee-backend.onrender.com
- Docs: https://charlee-backend.onrender.com/docs

---

## 🔧 Configurações Importantes

### Atualizar CORS no backend

Editar `backend/api/main.py`:

```python
# Adicionar domínio do Vercel
allowed_origins = [
    "http://localhost:3000",
    "https://seu-app.vercel.app",  # ← Adicionar
]
```

Commit e push para atualizar.

---

## 🔐 Segurança Essencial

### Gerar chaves JWT seguras

```bash
# Gerar JWT_SECRET_KEY
openssl rand -hex 32

# Gerar JWT_REFRESH_SECRET_KEY
openssl rand -hex 32
```

Adicionar no Render (Environment Variables).

### Checklist de segurança

- [ ] `DEBUG=false` em produção
- [ ] Chaves JWT fortes (32+ caracteres)
- [ ] CORS configurado apenas para domínios específicos
- [ ] Variáveis sensíveis em `.env` (não commitar)
- [ ] SSL/TLS habilitado (automático no Render/Vercel)
- [ ] Backup automático do banco (Supabase já tem)

---

## 📊 Monitoring e Logs

### Render Dashboard
- Logs: https://dashboard.render.com → Logs tab
- Métricas: CPU, Memory, Response time
- Health checks: Automático

### Supabase Dashboard
- Database size: https://app.supabase.com → Database
- Queries: Logs & Extensions
- Backups: Point-in-time recovery (Pro plan)

### Adicionar Uptime Monitoring (Grátis)

1. Acessar https://uptimerobot.com
2. Adicionar monitor:
   - URL: `https://charlee-backend.onrender.com/health`
   - Interval: 5 minutos
   - Alerts: Email/SMS

---

## 🔄 CI/CD Automático

### GitHub Actions (Opcional)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 🆙 Upgrade para Produção Paga

Quando app crescer:

```
✅ Banco: Supabase Pro ($25/mês)
   - 8GB storage
   - Point-in-time recovery
   - Métricas avançadas

✅ Backend: Render Starter ($7/mês)
   - Always-on (sem hibernação)
   - Melhor performance
   - Mais recursos

✅ Frontend: Vercel Pro ($20/mês)
   - Analytics
   - Mais builds/mês
   - Suporte prioritário

💰 Total: ~$52/mês
```

---

## 🚨 Troubleshooting

### Backend retorna 503
- Verificar logs no Render
- Checar se `DATABASE_URL` está correto
- Validar health check: `/health`

### CORS errors no frontend
- Adicionar domínio Vercel em `allowed_origins`
- Verificar se `FRONTEND_URL` está configurado

### Cold start lento (Render Free)
- Normal no tier gratuito (~30s)
- Upgrade para Starter ($7) elimina cold start

### Banco de dados conexão falha
- Verificar URL do Supabase
- Checar firewall rules (Supabase permite todos IPs por padrão)
- Testar conexão: `psql $DATABASE_URL`

---

## 📚 Recursos Adicionais

- **Documentação completa**: [PRODUCTION_DEPLOYMENT_OPTIONS.md](./PRODUCTION_DEPLOYMENT_OPTIONS.md)
- **Guia de migração**: [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md)
- **Scripts úteis**: `/scripts/migrate_to_production.sh`

---

## ⏱️ Resumo de Tempo

| Etapa | Tempo | Status |
|-------|-------|--------|
| Setup Supabase | 5min | ⬜ |
| Migrar dados | 3min | ⬜ |
| Deploy backend (Render) | 5min | ⬜ |
| Deploy frontend (Vercel) | 2min | ⬜ |
| Configurar Redis | 2min | ⬜ |
| Testes finais | 3min | ⬜ |
| **TOTAL** | **~20min** | |

---

**Última atualização:** 2025-11-13
**Status:** ✅ Testado e funcionando
