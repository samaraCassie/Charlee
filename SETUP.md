# 🚀 Guia de Setup Completo - Charlee

Este guia detalha como configurar o projeto Charlee do zero, incluindo todas as dependências e features implementadas.

> **⚡ Performance:** Migration 011 adiciona 30+ índices de database para otimizar queries comuns (melhoria de 10-100x).

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.12+** (para desenvolvimento local)
- **Node.js 18+** e **npm** (para frontend)
- **OpenAI API Key** (obrigatório)

## 🔧 Setup Rápido (Recomendado)

### 1. Clone o Repositório

```bash
git clone https://github.com/sam-cassie/Charlee.git
cd Charlee
```

### 2. Configure Variáveis de Ambiente

Atualize o arquivo `.env` com as novas variáveis:

```bash
cd Charlee
./scripts/update_env.sh
```

Ou manualmente, edite `docker/.env` e adicione:

```bash
# Frontend
FRONTEND_URL=http://localhost:3000

# Google Calendar OAuth (opcional, mas recomendado para V3.2)
GOOGLE_CALENDAR_CLIENT_ID=seu-client-id-aqui
GOOGLE_CALENDAR_CLIENT_SECRET=seu-client-secret-aqui
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:3000/calendar/callback/google

# Microsoft Calendar OAuth (opcional)
MICROSOFT_CALENDAR_CLIENT_ID=seu-client-id-aqui
MICROSOFT_CALENDAR_CLIENT_SECRET=seu-client-secret-aqui
MICROSOFT_CALENDAR_REDIRECT_URI=http://localhost:3000/calendar/callback/microsoft

# JWT (será gerado automaticamente)
JWT_SECRET_KEY=seu-secret-key-aqui
JWT_REFRESH_SECRET_KEY=seu-refresh-secret-key-aqui
```

**Como obter credenciais OAuth:**

- **Google Calendar**: https://console.cloud.google.com/apis/credentials
- **Microsoft Calendar**: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps

### 3. Inicie os Containers

```bash
cd docker
docker-compose up -d
```

Isso irá:
- ✅ Iniciar PostgreSQL com **pgvector** pré-instalado
- ✅ Iniciar Redis
- ✅ Construir e iniciar o backend FastAPI
- ✅ Instalar **postgresql-client** (inclui `pg_dump` para backups)

### 4. Execute as Migrations

```bash
docker exec -it charlee_backend alembic upgrade head
```

Isso irá:
- ✅ Criar todas as tabelas do banco de dados
- ✅ Instalar extensão **pgvector** no PostgreSQL
- ✅ Criar tabela **WorkLog** para time tracking
- ✅ Adicionar coluna `embedding` com índice HNSW para similarity search

### 5. Verifique o Backend

```bash
# Verificar logs
docker logs charlee_backend

# Acessar API docs
open http://localhost:8000/docs
```

### 6. (Opcional) Configure o Frontend

```bash
cd interfaces/web
npm install
npm run dev
```

Acesse: http://localhost:3000

---

## 🔍 Verificação Pós-Setup

### Verificar pgvector

```bash
docker exec -it charlee_db psql -U charlee -d charlee_db -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

Deve retornar:

```
 extname | extowner | extnamespace | extrelocatable | extversion 
---------+----------+--------------+----------------+------------
 vector  |       10 |         2200 | t              | 0.5.1
```

### Verificar WorkLog Table

```bash
docker exec -it charlee_db psql -U charlee -d charlee_db -c "\d work_logs;"
```

Deve listar a estrutura da tabela com colunas:
- id, user_id, task_id, project_id, hours_worked, description, logged_at, work_date

### Verificar Embedding Column

```bash
docker exec -it charlee_db psql -U charlee -d charlee_db -c "\d freelance_opportunities;" | grep embedding
```

Deve mostrar:
```
 embedding | vector(1536) |  |  | 
```

### Testar Backup System

```bash
# Via API (precisa estar autenticado)
curl -X POST http://localhost:8000/api/v1/settings/backup \
  -H "Authorization: Bearer YOUR_TOKEN"

# Ou manualmente
docker exec -it charlee_backend python -c "
from services.system_monitor import system_monitor
from database.config import settings
result = system_monitor.create_database_backup(settings.database_url)
print(f'Backup criado: {result}')
"
```

### Testar Uptime Tracking

```bash
curl http://localhost:8000/api/v1/settings/system
```

Deve retornar:
```json
{
  "version": "3.3.0",
  "uptime_seconds": 123,
  "total_users": 0,
  "total_tasks": 0,
  "total_big_rocks": 0,
  "last_backup": null
}
```

---

## 🛠️ Features Implementadas Recentemente

### ✅ 1. Redirect URIs em Environment Variables

**Antes:** Hardcoded em calendar.py
**Agora:** Configurável via `.env`

```python
# backend/api/routes/calendar.py
redirect_uri = settings.google_calendar_redirect_uri  # Vem do .env
```

### ✅ 2. Analytics com Cálculos Reais

**Antes:** Valores mockados
**Agora:** Cálculos baseados em dados reais do banco

```python
# Tempo médio por tarefa (baseado em WorkLog)
# Tendência de produtividade (mês atual vs anterior)
# Produtividade por ciclo menstrual (análise de MenstrualCycle)
```

### ✅ 3. Sistema de Backup Completo

**Novo módulo:** `backend/services/system_monitor.py`

**Features:**
- `create_database_backup()` - Backup PostgreSQL via `pg_dump`
- `get_last_backup_info()` - Informações do último backup
- `cleanup_old_backups()` - Mantém apenas últimos 5 backups
- Endpoint: `POST /api/v1/settings/backup`

**Exemplo de uso:**

```bash
# Criar backup manual
curl -X POST http://localhost:8000/api/v1/settings/backup \
  -H "Authorization: Bearer $TOKEN"

# Listar backups
ls -lh /tmp/charlee_backups/
```

### ✅ 4. Uptime Tracking

**Novo módulo:** Mesmo `system_monitor.py`

**Features:**
- `get_uptime_seconds()` - Tempo desde SERVER_START_TIME
- `get_uptime_formatted()` - Formato legível "2d 5h 30m"
- Endpoint: `GET /api/v1/settings/system` retorna uptime

### ✅ 5. Calendar Sync com Celery

**Antes:** Comentário TODO
**Agora:** Trigger async implementado

```python
# backend/api/routes/calendar.py linha 689
task = sync_connection.delay(connection.id, sync_direction)
```

### ✅ 6. Fetch External Event Version

**Novo:** `backend/tasks/calendar_sync.py`

```python
def fetch_external_event_version(connection, event):
    # Busca versão atual do evento no provider (Google/Microsoft)
    # Usado para detectar conflitos de sincronização
```

### ✅ 7. Skill Matching Inteligente

**Novo:** `backend/agent/specialized_agents/projects/project_evaluator_agent.py`

```python
def _calculate_skill_alignment(opportunity):
    # Busca skills de PortfolioItem e ProjectExecution
    # Compara com required_skills da oportunidade
    # Retorna score de 0.4 a 1.0
```

### ✅ 8. Vector Similarity Search

**Novo:** `backend/agent/specialized_agents/projects/semantic_analyzer_agent.py`

```python
# Usa pgvector para buscar projetos similares
# Operador <-> para L2 distance
# Fallback gracioso se pgvector não disponível
```

---

## 📊 Estrutura do Banco de Dados (Atualizada)

```
PostgreSQL com pgvector
├── users
├── tasks
├── big_rocks
├── menstrual_cycles
├── work_logs ✨ NOVO
├── freelance_opportunities
│   └── embedding vector(1536) ✨ NOVO
├── calendar_connections
├── calendar_events
├── attachments
└── ... (25+ tabelas total)
```

---

## 🐛 Troubleshooting

### Erro: "extension vector does not exist"

**Solução:**

```bash
# Verificar se imagem Docker tem pgvector
docker exec -it charlee_db psql -U charlee -d charlee_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Se falhar, usar imagem correta no docker-compose.yml
# Já configurado: ankane/pgvector:latest ✅
```

### Erro: "pg_dump: command not found"

**Solução:**

```bash
# Reconstruir imagem Docker com postgresql-client
cd docker
docker-compose build backend
docker-compose up -d
```

Já configurado no Dockerfile ✅

### Erro: "WorkLog model not found"

**Solução:**

```bash
# Executar migration 009
docker exec -it charlee_backend alembic upgrade head
```

### Backups não funcionam

**Diagnóstico:**

```bash
# Verificar se pg_dump está disponível
docker exec -it charlee_backend which pg_dump

# Verificar logs
docker exec -it charlee_backend python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from services.system_monitor import system_monitor
from database.config import settings
result = system_monitor.create_database_backup(settings.database_url)
print(result)
"
```

---

## 📚 Documentação Adicional

- **V1-V3.3 Implementation**: Ver `docs/` para detalhes de cada versão
- **API Docs**: http://localhost:8000/docs
- **Standards**: Ver `standards/` para padrões de código

---

## 🎯 Próximos Passos

Após setup completo:

1. ✅ Criar primeiro usuário via `/api/v1/auth/register`
2. ✅ Fazer login e obter JWT token
3. ✅ Criar Big Rocks e Tasks
4. ✅ (Opcional) Conectar Google/Microsoft Calendar
5. ✅ (Opcional) Testar upload de voz/imagem (V3.3)
6. ✅ Configurar backup automático (Celery Beat)

---

## 🆘 Suporte

- **Issues**: https://github.com/sam-cassie/Charlee/issues
- **Docs**: `docs/` folder
- **Standards**: `standards/` folder

---

**Status**: ✅ Todas as dependências configuradas
**Versão**: 3.3.0 (Multimodal Input System)
**Última atualização**: 2024-12-24
