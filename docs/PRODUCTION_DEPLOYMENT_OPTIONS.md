# 🚀 Opções de Deploy em Produção - Charlee

> Guia completo de alternativas viáveis para banco de dados e infraestrutura de produção

## 📊 Stack Atual da Aplicação

- **Backend**: FastAPI + Python 3.12
- **Banco de Dados**: PostgreSQL + pgvector
- **Cache/Sessões**: Redis
- **Frontend**: React + Vite
- **Containerização**: Docker

---

## 💾 Opções de Banco de Dados para Produção

### 1. **Supabase** ⭐ RECOMENDADO

**Por que escolher?**
- PostgreSQL gerenciado com pgvector incluído (perfeito para a aplicação)
- Tier gratuito generoso: 500MB storage, 2GB bandwidth/mês
- Backup automático e point-in-time recovery
- Dashboard intuitivo para gerenciar dados
- APIs REST e Realtime prontas
- Autenticação integrada (pode substituir o JWT atual)
- Edge Functions para lógica serverless

**Custo:**
- **Free**: $0/mês (até 500MB)
- **Pro**: $25/mês (8GB storage + recursos avançados)
- **Escalabilidade**: Cresce conforme uso

**Setup:**
```bash
# 1. Criar projeto no Supabase (https://supabase.com)
# 2. Obter connection string
# 3. Atualizar .env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Prós:**
- ✅ Suporta pgvector nativamente
- ✅ Backups automáticos
- ✅ SSL/TLS por padrão
- ✅ Connection pooling integrado
- ✅ Monitoring e logs

**Contras:**
- ❌ Vendor lock-in parcial
- ❌ Tier gratuito tem limitações de conexões simultâneas

---

### 2. **Neon** ⚡ MODERNA E ESCALÁVEL

**Por que escolher?**
- PostgreSQL serverless com arquitetura moderna
- Autoscaling automático (escala para zero quando não usado)
- Branching de bancos de dados (ótimo para dev/staging)
- Tier gratuito: 512MB storage

**Custo:**
- **Free**: $0/mês (512MB + 300h compute/mês)
- **Pro**: A partir de $19/mês

**Setup:**
```bash
# Connection string exemplo
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/charlee_db
```

**Prós:**
- ✅ Escala para zero (economia de custos)
- ✅ Branching de DB (dev/test)
- ✅ Latência baixa
- ✅ Backups automáticos

**Contras:**
- ❌ Pgvector pode exigir configuração extra
- ❌ Relativamente novo no mercado

---

### 3. **Railway** 🚂 SIMPLES E DIRETO

**Por que escolher?**
- PostgreSQL gerenciado com setup instantâneo
- Integração nativa com deploy da aplicação
- $5 de crédito gratuito/mês

**Custo:**
- **Free**: $5 crédito/mês
- **Pay as you go**: ~$0.000463/min ($20/mês típico para DB pequeno)

**Prós:**
- ✅ Setup extremamente rápido
- ✅ Deploy integrado (DB + App no mesmo lugar)
- ✅ Volumes persistentes

**Contras:**
- ❌ Mais caro que alternativas para uso contínuo
- ❌ Tier gratuito limitado

---

### 4. **Render PostgreSQL** 🎨

**Por que escolher?**
- PostgreSQL gerenciado com tier gratuito
- Integração perfeita com deploy do backend

**Custo:**
- **Free**: $0/mês (expira após 90 dias de inatividade)
- **Starter**: $7/mês (permanente)

**Prós:**
- ✅ Tier gratuito disponível
- ✅ Deploy integrado
- ✅ Backups automáticos no plano pago

**Contras:**
- ❌ Free tier expira após inatividade
- ❌ Performance limitada no tier gratuito

---

### 5. **ElephantSQL** 🐘

**Por que escolher?**
- Especializado em PostgreSQL
- Tier gratuito: 20MB storage

**Custo:**
- **Tiny Turtle**: $0/mês (20MB)
- **Small**: $5/mês (1GB)

**Prós:**
- ✅ Especializado em PostgreSQL
- ✅ Setup rápido
- ✅ Confiável

**Contras:**
- ❌ 20MB é muito limitado
- ❌ UI mais antiga

---

### 📝 Comparação Resumida - Bancos de Dados

| Provedor | Free Tier | Custo Inicial | pgvector | Backup Auto | Recomendação |
|----------|-----------|---------------|----------|-------------|--------------|
| **Supabase** | 500MB | $0 → $25 | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Neon** | 512MB | $0 → $19 | ⚠️ | ✅ | ⭐⭐⭐⭐ |
| **Railway** | $5 crédito | $5+ | ✅ | ✅ | ⭐⭐⭐ |
| **Render** | Sim (90d) | $0 → $7 | ✅ | ✅ | ⭐⭐⭐ |
| **ElephantSQL** | 20MB | $0 → $5 | ✅ | ✅ | ⭐⭐ |

---

## 🌐 Opções de Deploy da Aplicação

### 1. **Render** ⭐ RECOMENDADO PARA COMEÇAR

**Por que escolher?**
- Deploy automático do GitHub
- Tier gratuito para web services
- Suporta Docker
- SSL automático

**Custo:**
- **Free**: $0/mês (750h/mês, sleep após inatividade)
- **Starter**: $7/mês (always-on)

**Setup:**
```yaml
# render.yaml
services:
  - type: web
    name: charlee-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        sync: false

  - type: web
    name: charlee-frontend
    env: static
    buildCommand: "npm install && npm run build"
    staticPublishPath: ./dist
```

**Prós:**
- ✅ Tier gratuito generoso
- ✅ Deploy automático via GitHub
- ✅ SSL grátis
- ✅ Preview environments

**Contras:**
- ❌ Free tier hiberna após inatividade
- ❌ Cold start de ~30s

---

### 2. **Railway** 🚂 MELHOR DX (Developer Experience)

**Por que escolher?**
- Setup em 2 cliques
- Suporta Docker Compose completo
- Logs em tempo real
- Métricas integradas

**Custo:**
- **Free**: $5 crédito/mês
- **Typical**: ~$10-20/mês para app pequeno

**Setup:**
```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login e deploy
railway login
railway init
railway up
```

**Prós:**
- ✅ Melhor DX do mercado
- ✅ Suporta Docker Compose
- ✅ Volumes persistentes
- ✅ Métricas e logs excelentes

**Contras:**
- ❌ Mais caro que alternativas
- ❌ Free tier limitado

---

### 3. **Fly.io** ✈️ MODERNA E GLOBAL

**Por que escolher?**
- Edge deployment (servidores globais)
- Suporte nativo a Docker
- Tier gratuito: 3 VMs compartilhadas

**Custo:**
- **Free**: 3 shared-cpu VMs, 3GB storage
- **Paid**: ~$1.94/mês por VM (256MB RAM)

**Setup:**
```bash
# 1. Instalar flyctl
curl -L https://fly.io/install.sh | sh

# 2. Deploy
fly launch
fly deploy
```

**Prós:**
- ✅ Edge deployment (baixa latência global)
- ✅ Free tier generoso
- ✅ Suporta Docker nativamente
- ✅ Escalabilidade automática

**Contras:**
- ❌ Curva de aprendizado maior
- ❌ Redis requer configuração extra

---

### 4. **Google Cloud Run** ☁️ SERVERLESS

**Por que escolher?**
- Serverless (paga apenas quando usa)
- Escala automático (zero → milhões)
- Tier gratuito: 2 milhões requests/mês

**Custo:**
- **Free**: 2M requests/mês
- **Paid**: ~$0.00002400/request após limite

**Setup:**
```bash
# 1. Build e push imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/charlee-backend

# 2. Deploy
gcloud run deploy charlee-backend \
  --image gcr.io/PROJECT_ID/charlee-backend \
  --platform managed \
  --allow-unauthenticated
```

**Prós:**
- ✅ Serverless (custo eficiente)
- ✅ Escala automático
- ✅ Tier gratuito generoso
- ✅ Infraestrutura Google

**Contras:**
- ❌ Cold start possível
- ❌ Requer Cloud Build
- ❌ Mais complexo para iniciantes

---

### 5. **Vercel (Frontend) + Render/Railway (Backend)** 🎨

**Por que escolher?**
- Vercel é otimizado para React/Vite
- Separação de concerns (frontend/backend)

**Custo:**
- **Vercel Free**: Ilimitado para hobby
- **Backend**: Depende da escolha (Render/Railway)

**Setup:**
```bash
# Frontend no Vercel
vercel

# Backend no Render/Railway (ver opções acima)
```

**Prós:**
- ✅ Vercel é o melhor para frontends
- ✅ Deploy instantâneo
- ✅ CDN global
- ✅ Preview deployments

**Contras:**
- ❌ Gerenciar 2 plataformas
- ❌ CORS precisa configuração

---

### 6. **DigitalOcean App Platform** 🌊

**Por que escolher?**
- Plataforma completa (PaaS)
- Tier gratuito: $0 para 3 static sites

**Custo:**
- **Static**: $0/mês
- **Basic**: $5/mês (512MB RAM)
- **Professional**: $12/mês (1GB RAM)

**Prós:**
- ✅ Interface simples
- ✅ Integração com DO Database
- ✅ Preços previsíveis

**Contras:**
- ❌ Mais limitado que concorrentes
- ❌ Menos features modernas

---

### 📝 Comparação Resumida - Deploy

| Plataforma | Free Tier | Custo Típico | Docker | DX | Recomendação |
|------------|-----------|--------------|--------|----|--------------|
| **Render** | 750h/mês | $0 → $7 | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Railway** | $5 crédito | $10-20 | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Fly.io** | 3 VMs | $2-10 | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cloud Run** | 2M reqs | $0-20 | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Vercel** | Ilimitado | $0 (front) | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **DO App** | Static only | $5-12 | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 Recomendações por Cenário

### 🆓 Cenário 1: Começar GRÁTIS (MVP/Testes)

**Stack Recomendada:**
- **Banco**: Supabase Free (500MB)
- **Backend**: Render Free (750h/mês)
- **Frontend**: Vercel Free (ilimitado)
- **Redis**: Upstash Free (10k commands/dia)

**Custo Total: $0/mês**

**Limitações:**
- Backend hiberna após 15min inatividade
- Cold start de ~30s
- 500MB storage no banco

---

### 💰 Cenário 2: Produção Básica ($10-15/mês)

**Stack Recomendada:**
- **Banco**: Render PostgreSQL ($7/mês)
- **Backend**: Render Starter ($7/mês)
- **Frontend**: Vercel Free
- **Redis**: Upstash Pay-as-you-go (~$1-2/mês)

**Custo Total: ~$15/mês**

**Vantagens:**
- Always-on (sem hibernação)
- Backups automáticos
- SSL incluído

---

### 🚀 Cenário 3: Produção Profissional ($30-40/mês)

**Stack Recomendada:**
- **Banco**: Supabase Pro ($25/mês)
- **Backend + Frontend**: Railway (~$15-20/mês)
- **Redis**: Incluído no Railway

**Custo Total: ~$40/mês**

**Vantagens:**
- Melhor performance
- Backups point-in-time
- Métricas avançadas
- Escalabilidade automática

---

### ⚡ Cenário 4: Máxima Escalabilidade (Variável)

**Stack Recomendada:**
- **Banco**: Supabase Pro ($25/mês base)
- **Backend**: Google Cloud Run (serverless)
- **Frontend**: Vercel Pro ($20/mês)
- **Redis**: Google Memorystore ou Upstash

**Custo Total: $45/mês + uso**

**Vantagens:**
- Escala infinita
- Pay-per-use no backend
- CDN global
- Infraestrutura enterprise

---

## 🔧 Configuração de Redis para Produção

### Upstash ⭐ RECOMENDADO

**Por que?**
- Serverless Redis (pay-per-use)
- Tier gratuito: 10k commands/dia
- Global latência baixa

**Custo:**
- **Free**: 10k commands/dia
- **Pay-as-you-go**: $0.2/100k commands

**Setup:**
```bash
# 1. Criar database em https://upstash.com
# 2. Copiar REDIS_URL
REDIS_URL=redis://default:[PASSWORD]@[HOST].upstash.io:6379
```

---

### Redis Cloud (Redis Labs)

**Custo:**
- **Free**: 30MB
- **Paid**: $5/mês (250MB)

---

### Incluído na Plataforma

**Railway** e **Render** oferecem Redis add-ons:
- Railway: ~$5/mês
- Render: $10/mês

---

## 📋 Checklist de Migração para Produção

### Antes do Deploy

- [ ] Remover secrets do código (usar .env)
- [ ] Atualizar `jwt_secret_key` com chave forte
  ```bash
  openssl rand -hex 32
  ```
- [ ] Configurar `FRONTEND_URL` para domínio de produção
- [ ] Desabilitar `debug=False` em produção
- [ ] Configurar CORS apenas para domínios específicos
- [ ] Adicionar monitoring (Sentry, LogRocket)
- [ ] Configurar backups automáticos do banco

### Variáveis de Ambiente Necessárias

```bash
# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# JWT
JWT_SECRET_KEY=<generate-with-openssl>
JWT_REFRESH_SECRET_KEY=<generate-with-openssl>

# App
APP_ENV=production
DEBUG=false
FRONTEND_URL=https://seu-dominio.com

# APIs
ANTHROPIC_API_KEY=sk-...
```

### Após Deploy

- [ ] Testar health check: `GET /health`
- [ ] Verificar métricas: `GET /metrics`
- [ ] Testar autenticação
- [ ] Validar CORS
- [ ] Configurar domínio customizado
- [ ] Setup monitoring de uptime (UptimeRobot)
- [ ] Documentar credenciais (1Password/Bitwarden)

---

## 🎓 Recomendação Final

### Para começar AGORA (MVP):

```
✅ Banco: Supabase Free
✅ Backend: Render Free
✅ Frontend: Vercel Free
✅ Redis: Upstash Free
💰 Custo: $0/mês
```

### Quando tiver primeiros usuários (Produção):

```
✅ Banco: Supabase Pro ($25/mês)
✅ App: Railway ($15/mês)
✅ Redis: Incluído no Railway
💰 Custo: $40/mês
```

### Quando escalar (Crescimento):

```
✅ Banco: Supabase Pro + Réplicas
✅ Backend: Cloud Run (serverless)
✅ Frontend: Vercel Pro
✅ Redis: Upstash ou Memorystore
💰 Custo: $50-100/mês (conforme uso)
```

---

## 📚 Recursos Úteis

- [Supabase Docs](https://supabase.com/docs)
- [Render Deploy Guide](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Fly.io Docs](https://fly.io/docs)
- [Vercel Docs](https://vercel.com/docs)

---

**Criado em:** 2025-11-13
**Versão:** 1.0
**Status:** ✅ Pronto para uso
