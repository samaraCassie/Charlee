# 🧠 Charlee - Sistema de Inteligência Pessoal

> O segundo cérebro de Samara para gestão de tarefas, Big Rocks e produtividade consciente.

## 📋 Sobre o Projeto

Charlee é um sistema de inteligência pessoal desenvolvido com agentes AI que ajuda a gerenciar tarefas, prioridades e bem-estar, considerando fatores como ciclo menstrual, capacidade de trabalho e padrões de produtividade.

### ✨ Features Principais

- **🎙️ Input Multimodal**: Transcrição de voz (Whisper) e análise de imagem (GPT-4o Vision)
- **📅 Calendar Integration**: Sincronização com Google Calendar e Microsoft Calendar
- **🔐 RBAC System**: Controle de acesso baseado em roles (admin/moderator/user) ✨ **NOVO!**
- **⚡ High Performance**: 30+ índices de database para queries 10-100x mais rápidas ✨ **NOVO!**
- **🛡️ Production Security**: Headers de segurança OWASP-compliant + XSS prevention ✨ **NOVO!**
- **🤖 Agente Conversacional com Memória**: Chat natural com contexto e aprendizado sobre preferências
- **🎯 Big Rocks**: Gestão de pilares de vida (áreas importantes)
- **📝 Tarefas Inteligentes**: Sistema de tarefas com priorização automática
- **🌸 Cycle-Aware**: Adaptação baseada no ciclo menstrual
- **🛡️ Capacity Guard**: Proteção contra sobrecarga
- **📊 Priorização Automática**: Algoritmo multi-fator para ordenar tarefas
- **💼 Freelancer Manager**: Gestão de projetos freelance, timetracking e invoicing (V2)
- **💾 Memória Persistente**: Redis para sessões e aprendizado contínuo

## 🏗️ Estrutura do Projeto

```
Charlee/
├── backend/                 # Backend FastAPI + Agno
│   ├── agent/              # Agentes AI (Core, Cycle-Aware, Capacity Guard)
│   ├── api/                # Rotas REST API
│   │   └── routes/         # Analytics, Inbox, Settings, etc.
│   ├── database/           # Models, CRUD, migrations
│   └── services/           # Serviços de negócio
├── interfaces/             # Interfaces de usuário
│   └── web/               # ✨ Frontend React (NEW!)
│       ├── src/
│       │   ├── pages/     # Dashboard, BigRocks, Tasks, etc.
│       │   ├── components/# UI components (Calendar, DatePicker)
│       │   ├── stores/    # Zustand state management
│       │   ├── services/  # API integration layer
│       │   └── __tests__/ # Unit tests (71 tests, 88% coverage)
│       └── vitest.config.ts
├── docker/                 # Arquivos Docker
│   ├── docker-compose.yml
│   └── .env
├── docs/                   # Documentação completa
│   ├── V1_IMPLEMENTATION.md
│   ├── V2_IMPLEMENTATION.md
│   ├── MEMORY_IMPLEMENTATION.md
│   └── Charlee_Documentacao.docx.md
├── scripts/                # Scripts utilitários
│   ├── setup.sh
│   └── clear_session.py
└── tests/                  # Testes backend
    ├── test_memory.py
    └── test_conversation_history.py
```

## 🚀 Quick Start

### Pré-requisitos

- Docker & Docker Compose
- Python 3.12+
- OpenAI API Key

### Instalação Rápida

```bash
# Clone e configure
git clone https://github.com/sam-cassie/Charlee.git
cd Charlee

# Setup automático (recomendado)
bash scripts/setup_complete.sh
```

**Ou manualmente:**

1. **Configure environment**
```bash
cp docker/.env.example docker/.env
bash scripts/update_env.sh
# Edite docker/.env com suas chaves
```

2. **Inicie os containers**
```bash
cd docker && docker-compose up -d
```

3. **Execute migrations**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Acesse a aplicação**
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

📖 **Documentação completa:** [SETUP.md](SETUP.md) | [QUICKSTART.md](QUICKSTART.md) | [DEPLOYMENT.md](DEPLOYMENT.md)

## 💬 Usando o Charlee

### Via API

```bash
# Enviar mensagem
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Oi! Me ajuda a organizar minhas tarefas?"}'

# Com sessão específica
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Você lembra do que falamos?", "session_id": "abc-123"}'
```

### Gerenciando Sessões

```bash
# Listar sessões
python3 scripts/clear_session.py list

# Limpar sessão específica
python3 scripts/clear_session.py clear <session-id>
```

## 🧪 Testes

```bash
# Teste de memória
python3 tests/test_memory.py

# Teste de histórico de conversação
python3 tests/test_conversation_history.py
```

## 📚 Documentação

### 📖 Guias Principais

- **[QUICKSTART.md](QUICKSTART.md)** - Setup em 3 comandos
- **[SETUP.md](SETUP.md)** - Configuração completa e troubleshooting
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy em produção (VPS/Cloud)
- **[MODULES_STATUS.md](MODULES_STATUS.md)** - Status de todos os 17 módulos
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Índice completo de 40+ documentos

### 🔒 Segurança & Performance

- **[SECURITY_SANITIZATION.md](backend/api/SECURITY_SANITIZATION.md)** - XSS prevention e sanitização
- **[INDEXES_DOCUMENTATION.md](backend/database/migrations/INDEXES_DOCUMENTATION.md)** - Performance indexes

### 📋 Implementação

- **[V1_IMPLEMENTATION.md](docs/V1_IMPLEMENTATION.md)** - Base do sistema
- **[V2_IMPLEMENTATION.md](docs/V2_IMPLEMENTATION.md)** - Wellness e Capacity
- **[MEMORY_IMPLEMENTATION.md](docs/MEMORY_IMPLEMENTATION.md)** - Memória e sessões

## 🏛️ Arquitetura

### Stack Tecnológico

**Backend:**
- FastAPI + Python 3.12
- Agno AI Framework (OpenAI GPT-4o-mini)
- PostgreSQL 14+ with pgvector
- Redis 5.0+ (caching + sessions)
- Celery (background tasks)

**Performance & Security:**
- ⚡ 30+ database indexes (10-100x faster queries)
- 🛡️ OWASP security headers (CSP, HSTS, X-Frame-Options)
- 🔐 RBAC with role hierarchy
- 🛡️ 100% input sanitization (XSS prevention)
- 🚦 Rate limiting (60 req/min, 1000/hour)
- 📊 Advanced health monitoring

### Agentes AI

1. **CharleeAgent** (Core): Agente principal conversacional
2. **CycleAwareAgent**: Especialista em bem-estar e ciclo menstrual
3. **CapacityGuardAgent**: Guardião da capacidade de trabalho
4. **FreelancerAgent** (V2): Gerenciamento de projetos freelance e faturamento
5. **DailyTrackingAgent**: Rastreamento de padrões diários e otimizações

## 🎯 Roadmap

- [x] V1: Sistema base (Big Rocks, Tarefas, CRUD)
- [x] V2: Bem-estar consciente + Capacity Guard
- [x] V2.1: Memória e sessões persistentes
- [x] **V3.0: Frontend Web React**
  - [x] Dashboard com visão geral
  - [x] Gerenciamento de Big Rocks e Tasks
  - [x] Analytics e relatórios
  - [x] Chat interface com IA
  - [x] Wellness tracking
  - [x] Test coverage > 80%
- [x] **V3.1: Agent Orchestration**
  - [x] Sistema de roteamento automático
  - [x] Análise de intenção do usuário
  - [x] Consulta multi-agente
- [x] **V3.2: Calendar Integration**
  - [x] Google Calendar sync (OAuth 2.0)
  - [x] Microsoft Calendar sync
  - [x] Sincronização bidirecional
  - [x] Detecção de conflitos
- [x] **V3.3: Input Multimodal** ✨ **NOVO!**
  - [x] Transcrição de voz (Whisper API)
  - [x] Análise de imagem (GPT-4o Vision)
  - [x] VoiceInput e ImageUpload components
  - [x] Sistema de anexos (attachments)
  - [x] 173 testes, 79.8% cobertura
- [ ] V3.4: Notificações e Lembretes
- [ ] V4: Bot Telegram/WhatsApp

> 📊 **Status Detalhado:** Veja [MODULES_STATUS.md](MODULES_STATUS.md) para informações completas sobre cada módulo (implementado, parcial ou planejado).

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

## 📝 Licença

Projeto privado - Todos os direitos reservados

## 👩‍💻 Autora

**Samara Cassie**
- Sistema desenvolvido para uso pessoal de produtividade

---

## 💼 Freelancer System (V2)

O Charlee V2 inclui um sistema completo de gerenciamento de projetos freelance:

### Features

- **📁 Gerenciamento de Projetos**: Crie e gerencie projetos de clientes
- **⏱️ Time Tracking**: Registre horas trabalhadas por projeto
- **💰 Invoicing**: Gere invoices profissionais baseados em horas
- **📊 Relatórios**: Análise mensal de faturamento e produtividade
- **🤖 IA Integrada**: Sugestões inteligentes para aceitar/rejeitar projetos
- **🛡️ Proteção de Capacidade**: Integração com CapacityGuard para evitar sobrecarga

### Uso via API

```bash
# Criar projeto freelance
curl -X POST http://localhost:8000/api/v2/freelancer/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "client_name": "Acme Corp",
    "project_name": "Website Redesign",
    "hourly_rate": 150,
    "estimated_hours": 40,
    "deadline": "2025-12-31"
  }'

# Registrar horas trabalhadas
curl -X POST http://localhost:8000/api/v2/freelancer/projects/1/log-work \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "hours": 5,
    "description": "Implemented login feature"
  }'

# Gerar invoice
curl -X GET http://localhost:8000/api/v2/freelancer/projects/1/invoice \
  -H "Authorization: Bearer $TOKEN"
```

### Database Models

- **FreelanceProject**: Projetos de clientes com taxas, deadlines e status
- **WorkLog**: Registro de horas trabalhadas com descrições
- **Invoice**: Invoices geradas com cálculo automático de valores

---

---

## 🔐 Security & Performance

### Security Features ✅

- ✅ **RBAC** - Role-based access control (admin/moderator/user)
- ✅ **Input Sanitization** - 100% coverage, XSS prevention
- ✅ **Security Headers** - OWASP compliant (CSP, HSTS, X-Frame-Options)
- ✅ **CORS Restricted** - Specific origins, methods, headers
- ✅ **Rate Limiting** - 60 req/min, 1000/hour, 10000/day
- ✅ **SQL Injection Protection** - SQLAlchemy ORM parameterized queries
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **OAuth 2.0** - Google + GitHub integration
- ✅ **Error Handling** - Stack trace protection in production

### Performance Optimizations ⚡

- ⚡ **30+ Database Indexes** - 10-100x faster queries
  - Tasks: 250ms → 3ms (83x faster)
  - Calendar sync: 100-300ms → <5ms
  - Notifications: 150-400ms → <3ms
- ⚡ **Redis Caching** - Session storage and performance
- ⚡ **pgvector** - Vector similarity search with HNSW indexes
- ⚡ **Background Tasks** - Celery for async processing
- ⚡ **Query Optimization** - Composite indexes on frequent queries

### Health Monitoring 🏥

Advanced health check endpoint: `/health`

Monitors:
- ✅ PostgreSQL database connection
- ✅ Redis cache connectivity
- ✅ Celery workers status
- ✅ Database migrations version
- ✅ Critical tables existence

---

**Status**: 🚀 **PRODUCTION-READY** - MVP Complete with enterprise-grade security & performance!
**Última atualização**: 2025-12-26
**Versão**: 2.0.0
