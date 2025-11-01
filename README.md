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
│   ├── database/           # Models, CRUD, migrations
│   └── services/           # Serviços de negócio
├── docker/                 # Arquivos Docker
│   ├── docker-compose.yml
│   └── .env
├── docs/                   # Documentação completa
│   ├── V1_IMPLEMENTATION.md
│   ├── V2_IMPLEMENTATION.md
│   ├── MEMORY_IMPLEMENTATION.md
│   └── info_charlee.txt
├── interfaces/             # Frontends (futuros)
├── scripts/                # Scripts utilitários
│   ├── setup.sh
│   └── clear_session.py
├── shared/                 # Recursos compartilhados
└── tests/                  # Testes automatizados
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

- **[V1_IMPLEMENTATION.md](docs/V1_IMPLEMENTATION.md)**: Base do sistema (Big Rocks, Tarefas, CRUD)
- **[V2_IMPLEMENTATION.md](docs/V2_IMPLEMENTATION.md)**: Sistemas de bem-estar e capacidade
- **[MEMORY_IMPLEMENTATION.md](docs/MEMORY_IMPLEMENTATION.md)**: Memória e sessões com Redis

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
- [ ] V3: CLI interativo
- [ ] V3: Frontend web
- [ ] V3: Integração Google Calendar
- [ ] V3: Input multimodal (voz, imagens)
- [ ] V3: Bot Telegram/WhatsApp

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

## 📝 Licença

Projeto privado - Todos os direitos reservados

## 👩‍💻 Autora

**Samara Cassie**
- Sistema desenvolvido para uso pessoal de produtividade

---

**Status**: ✅ V2.1 - Memória Persistente Implementada
**Última atualização**: 2025-11-01
