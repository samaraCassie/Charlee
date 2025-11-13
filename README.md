# 🧠 Charlee - Sistema de Inteligência Pessoal

> O segundo cérebro de Samara para gestão de tarefas, Big Rocks e produtividade consciente.

## 📋 Sobre o Projeto

Charlee é um sistema de inteligência pessoal desenvolvido com agentes AI que ajuda a gerenciar tarefas, prioridades e bem-estar, considerando fatores como ciclo menstrual, capacidade de trabalho e padrões de produtividade.

### ✨ Features Principais

- **🤖 Agente Conversacional com Memória**: Chat natural com contexto e aprendizado sobre preferências
- **🎯 Big Rocks**: Gestão de pilares de vida (áreas importantes)
- **📝 Tarefas Inteligentes**: Sistema de tarefas com priorização automática
- **🌸 Cycle-Aware**: Adaptação baseada no ciclo menstrual
- **🛡️ Capacity Guard**: Proteção contra sobrecarga
- **📊 Priorização Automática**: Algoritmo multi-fator para ordenar tarefas
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

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/sam-cassie/Charlee.git
cd Charlee
```

2. **Configure as variáveis de ambiente**
```bash
cp docker/.env.example docker/.env
# Edite docker/.env
```

3. **Inicie os containers**
```bash
cd docker
docker-compose up -d
```

4. **Acesse a API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

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

Documentação detalhada em [`docs/`](docs/):

### Implementação
- **[V1_IMPLEMENTATION.md](docs/V1_IMPLEMENTATION.md)**: Base do sistema (Big Rocks, Tarefas, CRUD)
- **[V2_IMPLEMENTATION.md](docs/V2_IMPLEMENTATION.md)**: Sistemas de bem-estar e capacidade
- **[MEMORY_IMPLEMENTATION.md](docs/MEMORY_IMPLEMENTATION.md)**: Memória e sessões com Redis

### Deploy e Produção
- **[PRODUCTION_QUICKSTART.md](docs/PRODUCTION_QUICKSTART.md)**: ⚡ Quick start - Deploy em 20 minutos
- **[PRODUCTION_DEPLOYMENT_OPTIONS.md](docs/PRODUCTION_DEPLOYMENT_OPTIONS.md)**: Guia completo de opções de banco de dados e deploy
- **[DATABASE_MIGRATION_GUIDE.md](docs/DATABASE_MIGRATION_GUIDE.md)**: Passo-a-passo para migrar PostgreSQL local para produção
- **[AWS_DEPLOYMENT_GUIDE.md](docs/AWS_DEPLOYMENT_GUIDE.md)**: AWS é mais caro? Análise completa de custos
- **[DEPLOYMENT_SUMMARY.md](docs/DEPLOYMENT_SUMMARY.md)**: Resumo executivo com recomendações

## 🏛️ Arquitetura

### Stack Tecnológico

- **Backend**: FastAPI + Python 3.12
- **AI Framework**: Agno (com OpenAI GPT-4o-mini)
- **Database**: PostgreSQL + pgvector
- **Cache/Sessions**: Redis
- **Containers**: Docker + Docker Compose

### Agentes AI

1. **CharleeAgent** (Core): Agente principal conversacional
2. **CycleAwareAgent**: Especialista em bem-estar e ciclo menstrual
3. **CapacityGuardAgent**: Guardião da capacidade de trabalho

## 🎯 Roadmap

- [x] V1: Sistema base (Big Rocks, Tarefas, CRUD)
- [x] V2: Bem-estar consciente + Capacity Guard
- [x] V2.1: Memória e sessões persistentes
- [x] **V3.0: Frontend Web React** ✨ **NEW!**
  - [x] Dashboard com visão geral
  - [x] Gerenciamento de Big Rocks e Tasks
  - [x] Analytics e relatórios
  - [x] Chat interface com IA
  - [x] Wellness tracking
  - [x] Test coverage > 80%
- [ ] V3.1: Integração Google Calendar
- [ ] V3.2: Input multimodal (voz, imagens)
- [ ] V3.3: CLI interativo aprimorado
- [ ] V4: Bot Telegram/WhatsApp

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

## 📝 Licença

Projeto privado - Todos os direitos reservados

## 👩‍💻 Autora

**Samara Cassie**
- Sistema desenvolvido para uso pessoal de produtividade

---

**Status**: 🎉 V3.0 - Frontend Web React + MVP Complete!
**Última atualização**: 2025-01-08
