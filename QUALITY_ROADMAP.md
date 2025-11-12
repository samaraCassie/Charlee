# 🎯 Quality Roadmap - O que Falta Implementar

> **Status Atual**: Foundation Phase Completa ✅
> **Próximo**: Consolidation Phase (60 dias)

---

## 📊 Status Atual vs Meta

| Área | Atual | Meta | Prioridade |
|------|-------|------|------------|
| **Testes Backend** | 17 tests (~15%) | 80%+ | 🔴 CRÍTICO |
| **Testes Frontend** | 0% | 80%+ | 🔴 CRÍTICO |
| **Segurança** | Básica | OWASP Top 10 | 🔴 CRÍTICO |
| **CI/CD** | ✅ Completo | ✅ | ✅ OK |
| **Code Quality** | ✅ 100% | ✅ | ✅ OK |
| **Documentação** | Parcial | Completa | 🟡 IMPORTANTE |
| **Performance** | Não otimizado | Otimizado | 🟢 DESEJÁVEL |
| **Monitoring** | ❌ Nenhum | Completo | 🟡 IMPORTANTE |

---

## 🔴 CRÍTICO - Precisa ser Feito Agora

### 1. Cobertura de Testes Backend (80%+)

**Atual**: 17 testes (~15% de cobertura)
**Meta**: 80% de cobertura de código

#### Testes Faltando:

**API Routes V1** (50% cobertura atual):
```bash
✅ test_api/test_big_rocks.py (8 tests)
✅ test_api/test_tasks.py (6 tests)
✅ test_api/test_health.py (2 tests)
❌ test_api/test_agent.py (0 tests) - FALTA CRIAR
```

**API Routes V2** (0% cobertura):
```bash
❌ test_api/test_wellness.py (0 tests) - FALTA CRIAR
❌ test_api/test_capacity.py (0 tests) - FALTA CRIAR
❌ test_api/test_priorizacao.py (0 tests) - FALTA CRIAR
❌ test_api/test_inbox.py (0 tests) - FALTA CRIAR
❌ test_api/test_analytics.py (0 tests) - FALTA CRIAR
❌ test_api/test_settings.py (0 tests) - FALTA CRIAR
```

**Business Logic** (0% cobertura):
```bash
❌ test_services/test_priorizacao.py - Sistema de priorização
❌ test_agents/test_orchestrator.py - Orquestração de agentes
❌ test_agents/test_core_agent.py - Agente principal
❌ test_agents/test_capacity_guard.py - Agente de capacidade
❌ test_agents/test_cycle_aware.py - Agente de ciclo
```

**CRUD Operations** (0% cobertura além dos testes de API):
```bash
❌ test_database/test_crud_edge_cases.py - Casos extremos
❌ test_database/test_models_methods.py - Métodos dos models
```

**Estimativa**: 60-80 testes adicionais necessários

---

### 2. Segurança (OWASP Top 10)

#### 2.1 Autenticação e Autorização ❌

**Falta Implementar**:
```python
# JWT Authentication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@router.get("/tasks")
async def get_tasks(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = verify_jwt_token(credentials.credentials)
    # ...
```

**Checklist**:
- [ ] Implementar geração de JWT tokens
- [ ] Criar endpoints `/auth/login` e `/auth/register`
- [ ] Adicionar middleware de autenticação
- [ ] Proteger todas as rotas (exceto `/health`, `/docs`)
- [ ] Implementar refresh tokens
- [ ] Hash de senhas com bcrypt

**Arquivos a criar**:
- `backend/auth/jwt.py`
- `backend/auth/dependencies.py`
- `backend/api/routes/auth.py`
- `backend/tests/test_api/test_auth.py`

---

#### 2.2 Rate Limiting ❌

**Falta Implementar**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/tasks")
@limiter.limit("10/minute")  # Max 10 criações por minuto
async def create_task(...):
    ...
```

**Checklist**:
- [ ] Instalar `slowapi`
- [ ] Configurar limites por endpoint
- [ ] Configurar limites por usuário (após auth)
- [ ] Adicionar headers de rate limit nas respostas
- [ ] Testar rate limiting

---

#### 2.3 Validação de Input Robusta ❌

**Problema Atual**: Validação básica com Pydantic, mas falta:

```python
# ❌ VULNERÁVEL a SQL Injection (via ORM é seguro, mas...)
# ❌ VULNERÁVEL a XSS em descrições
# ❌ SEM validação de tamanho de payloads
# ❌ SEM sanitização de HTML

# ✅ ADICIONAR
from pydantic import validator, field_validator
from bleach import clean

class TaskCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: str) -> str:
        # Remove HTML tags e scripts
        return clean(v, tags=[], strip=True)
```

**Checklist**:
- [ ] Adicionar sanitização de HTML em todos os campos de texto
- [ ] Validar tamanhos máximos de payloads
- [ ] Adicionar validação de tipos de arquivo (se uploads existirem)
- [ ] Validar ranges de datas (deadline não pode ser no passado para novos tasks)
- [ ] Adicionar validação de emails (se existir)

---

#### 2.4 CORS Muito Permissivo ⚠️

**Problema Atual**:
```python
# ❌ MUITO PERMISSIVO
allow_origins=["http://localhost:3000", "http://localhost:5173", ...]
allow_credentials=True
allow_methods=["*"]  # ❌ Permite DELETE, PUT, etc sem restrição
allow_headers=["*"]  # ❌ Aceita qualquer header
```

**Solução**:
```python
# ✅ RESTRITIVO
allow_origins=[
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    # Apenas origens específicas
]
allow_credentials=True
allow_methods=["GET", "POST", "PATCH", "DELETE"]  # Explícito
allow_headers=["Content-Type", "Authorization"]  # Específico
max_age=3600  # Cache preflight
```

---

#### 2.5 Secrets Management ⚠️

**Problema Atual**: `.env.example` tem senhas de exemplo
**Checklist**:
- [ ] Usar secrets manager (AWS Secrets Manager, Azure Key Vault, ou Vault)
- [ ] Nunca commitar `.env`
- [ ] Rotação automática de secrets em produção
- [ ] Diferentes secrets por ambiente (dev/staging/prod)

---

#### 2.6 Logging e Auditoria ❌

**Falta Implementar**:
```python
import logging
import structlog

logger = structlog.get_logger()

@router.post("/tasks")
async def create_task(task: TaskCreate, user: User = Depends(get_current_user)):
    logger.info(
        "task_created",
        user_id=user.id,
        task_description=task.description,
        timestamp=datetime.utcnow().isoformat()
    )
    # ...
```

**Checklist**:
- [ ] Implementar logging estruturado (JSON)
- [ ] Log de todas as mutações (CREATE, UPDATE, DELETE)
- [ ] Log de tentativas de autenticação
- [ ] Log de rate limit violations
- [ ] Log de erros com stack traces
- [ ] Integração com Sentry ou similar

---

### 3. Database - Migrations e Otimizações

#### 3.1 Criar Migrations Alembic ❌

**Problema**: Alembic configurado mas sem migrations criadas

```bash
# FALTA FAZER
cd backend
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

**Checklist**:
- [ ] Criar migration inicial com schema atual
- [ ] Criar migration para renomear colunas PT→EN
- [ ] Criar migrations para índices de performance
- [ ] Configurar auto-migration em CI/CD
- [ ] Testar rollback de migrations

---

#### 3.2 Índices de Performance ❌

**Problema**: Índices apenas comentados no código

```sql
-- CRIAR ESTES ÍNDICES
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_big_rock ON tasks(big_rock_id);
CREATE INDEX idx_tasks_status_deadline ON tasks(status, deadline);  -- Compound index

CREATE INDEX idx_cycle_date ON menstrual_cycles(start_date);
CREATE INDEX idx_workload_period ON workloads(period_start, period_end);
CREATE INDEX idx_daily_log_date ON daily_logs(date);
```

---

#### 3.3 N+1 Queries ⚠️

**Problema Potencial**:
```python
# ❌ N+1 Query Problem
tasks = db.query(Task).all()
for task in tasks:
    print(task.big_rock.name)  # Faz 1 query adicional por task!

# ✅ SOLUÇÃO: Eager Loading
from sqlalchemy.orm import joinedload

tasks = db.query(Task).options(joinedload(Task.big_rock)).all()
for task in tasks:
    print(task.big_rock.name)  # Sem queries adicionais!
```

**Checklist**:
- [ ] Auditar queries com `echo=True` no SQLAlchemy
- [ ] Adicionar `joinedload` onde necessário
- [ ] Implementar paginação cursor-based para grandes datasets
- [ ] Adicionar query profiling em logs

---

## 🟡 IMPORTANTE - Próximos 30 Dias

### 4. Testes Frontend (0% → 80%)

**Falta Implementar**:
```typescript
// Vitest + React Testing Library
import { render, screen, fireEvent } from '@testing-library/react'
import { TaskCard } from './TaskCard'

describe('TaskCard', () => {
  it('should render task description', () => {
    const task = { id: 1, description: 'Test task', status: 'pending' }
    render(<TaskCard task={task} />)
    expect(screen.getByText('Test task')).toBeInTheDocument()
  })

  it('should call onComplete when clicked', () => {
    const onComplete = vi.fn()
    const task = { id: 1, description: 'Test', status: 'pending' }
    render(<TaskCard task={task} onComplete={onComplete} />)

    fireEvent.click(screen.getByRole('button', { name: /complete/i }))
    expect(onComplete).toHaveBeenCalledWith(1)
  })
})
```

**Checklist**:
- [ ] Configurar Vitest
- [ ] Configurar React Testing Library
- [ ] Testes de componentes UI (50+ componentes)
- [ ] Testes de hooks customizados
- [ ] Testes de stores Zustand
- [ ] Testes de integração com API (MSW)
- [ ] Coverage mínimo 80%

---

### 5. Linting e Type Checking Frontend

**Verificar Configuração**:
```bash
# ESLint
cd interfaces/web
npm run lint  # Verificar se está configurado
npm run lint:fix

# TypeScript
npm run type-check  # Verificar se existe
```

**Checklist**:
- [ ] Verificar se ESLint está funcionando
- [ ] Configurar regras strict do TypeScript
- [ ] Adicionar `tsc --noEmit` no CI
- [ ] Corrigir todos os warnings de TypeScript
- [ ] Adicionar Prettier para formatação

---

### 6. Documentação Completa

#### 6.1 API Documentation ⚠️

**Melhorar**:
```python
# ❌ Documentação básica
@router.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    """Create a task."""
    ...

# ✅ Documentação completa
@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
    description="""
    Creates a new task associated with a Big Rock.

    **Requirements:**
    - Description must be between 1-1000 characters
    - big_rock_id must exist (returns 404 if invalid)
    - deadline must be in the future for new tasks

    **Returns:**
    - 201: Task created successfully
    - 404: BigRock not found
    - 422: Validation error
    """,
    responses={
        404: {"description": "BigRock not found"},
        422: {"description": "Validation error"},
    }
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    ...
```

**Checklist**:
- [ ] Adicionar descriptions em todos os endpoints
- [ ] Adicionar exemplos de requests/responses
- [ ] Documentar todos os status codes possíveis
- [ ] Adicionar tags e grupos lógicos
- [ ] Gerar OpenAPI spec estável

---

#### 6.2 README e Setup Guides ⚠️

**Falta Criar**:
- [ ] `backend/README.md` - Setup detalhado do backend
- [ ] `interfaces/web/README.md` - Setup do frontend
- [ ] `ARCHITECTURE.md` - Documentação de arquitetura
- [ ] `DEPLOYMENT.md` - Guia de deploy
- [ ] Diagramas de arquitetura (C4 Model)

---

### 7. Monitoring e Observabilidade ❌

**Falta Implementar Completamente**:

#### 7.1 Application Monitoring
```python
# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram

task_created_counter = Counter('tasks_created_total', 'Total tasks created')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

**Checklist**:
- [ ] Métricas de aplicação (Prometheus)
- [ ] Health checks detalhados (DB, Redis, etc)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (APM)
- [ ] Log aggregation (ELK ou Loki)

---

#### 7.2 Dashboards
**Checklist**:
- [ ] Grafana dashboard de métricas de sistema
- [ ] Dashboard de business metrics (tasks criados/dia, etc)
- [ ] Alertas para erros críticos
- [ ] Alertas para performance degradation

---

## 🟢 DESEJÁVEL - Próximos 60-90 Dias

### 8. Performance Otimizations

#### 8.1 Caching ❌
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@router.get("/big-rocks")
@cache(expire=60)  # Cache por 1 minuto
async def get_big_rocks(...):
    ...
```

**Checklist**:
- [ ] Implementar Redis caching
- [ ] Cache de queries frequentes
- [ ] Cache invalidation strategy
- [ ] Cache warming

---

#### 8.2 Database Connection Pooling ⚠️
```python
# Verificar configuração atual
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Número de conexões persistentes
    max_overflow=20,  # Conexões extras permitidas
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600  # Recicla conexões a cada hora
)
```

---

### 9. E2E Testing ❌

**Falta Implementar**:
```typescript
// Playwright E2E tests
import { test, expect } from '@playwright/test'

test('user can create and complete a task', async ({ page }) => {
  await page.goto('http://localhost:3000')
  await page.click('button:has-text("New Task")')
  await page.fill('input[name="description"]', 'Buy groceries')
  await page.click('button:has-text("Create")')

  await expect(page.locator('text=Buy groceries')).toBeVisible()

  await page.click('button[aria-label="Complete task"]')
  await expect(page.locator('text=Buy groceries')).toHaveClass(/completed/)
})
```

**Checklist**:
- [ ] Configurar Playwright
- [ ] Testes de fluxos críticos (10-15 scenarios)
- [ ] Testes de autenticação
- [ ] Testes de formulários
- [ ] Testes de navegação
- [ ] CI/CD com E2E tests

---

### 10. Advanced Features

#### 10.1 GraphQL API (Opcional)
- [ ] Substituir REST por GraphQL
- [ ] Resolver N+1 queries automaticamente
- [ ] Subscriptions para real-time

#### 10.2 WebSockets (Opcional)
- [ ] Notificações em tempo real
- [ ] Sincronização multi-dispositivo

#### 10.3 Background Jobs
```python
from celery import Celery

celery = Celery('charlee', broker='redis://localhost:6379/0')

@celery.task
def send_daily_summary_email(user_id: int):
    # Tarefa assíncrona para enviar email
    ...
```

---

## 📋 Priorização Sugerida (Next 90 Days)

### Semana 1-2: Segurança Crítica
- [ ] Implementar JWT Authentication
- [ ] Adicionar Rate Limiting
- [ ] Melhorar validação de inputs
- [ ] Configurar CORS restritivo

### Semana 3-4: Testes Backend
- [ ] Aumentar cobertura para 60% (40+ testes)
- [ ] Testes de API V2
- [ ] Testes de agentes

### Semana 5-6: Database
- [ ] Criar todas as migrations
- [ ] Adicionar índices de performance
- [ ] Otimizar queries (eager loading)

### Semana 7-8: Testes Frontend
- [ ] Configurar Vitest
- [ ] Testes de componentes (50%)
- [ ] Testes de integração com API

### Semana 9-10: Monitoring
- [ ] Implementar logging estruturado
- [ ] Configurar Sentry
- [ ] Criar dashboards básicos

### Semana 11-12: Aumentar Cobertura
- [ ] Backend 80%+ coverage
- [ ] Frontend 80%+ coverage
- [ ] E2E tests críticos

---

## 📊 Métricas de Qualidade - Meta Final

| Métrica | Atual | Meta 30d | Meta 60d | Meta 90d |
|---------|-------|----------|----------|----------|
| **Backend Coverage** | 15% | 60% | 75% | 85% |
| **Frontend Coverage** | 0% | 40% | 70% | 80% |
| **Security Score** | 3/10 | 6/10 | 8/10 | 9/10 |
| **API Response Time** | ? | <200ms | <100ms | <50ms |
| **Uptime** | ? | 99% | 99.9% | 99.95% |
| **Error Rate** | ? | <1% | <0.5% | <0.1% |

---

## 🎯 Definition of Done - Qualidade Excelente

Quando TODOS estes itens estiverem ✅:

### Code Quality
- [x] 100% código em inglês
- [x] Black, Ruff, MyPy sem erros
- [ ] ESLint, TypeScript strict no frontend
- [x] Pre-commit hooks ativos
- [x] CI/CD pipeline completo

### Testing
- [ ] Backend coverage ≥ 80%
- [ ] Frontend coverage ≥ 80%
- [ ] E2E tests para fluxos críticos
- [ ] Todos os testes passando em CI

### Security
- [ ] Autenticação JWT implementada
- [ ] Rate limiting ativo
- [ ] Input validation robusta
- [ ] CORS configurado corretamente
- [ ] Secrets em vault (não em .env)
- [ ] Auditoria de segurança passando

### Performance
- [ ] Índices de DB criados
- [ ] Queries otimizadas (sem N+1)
- [ ] Cache implementado
- [ ] Response time < 200ms (p95)

### Observability
- [ ] Logs estruturados
- [ ] Error tracking (Sentry)
- [ ] Métricas (Prometheus)
- [ ] Dashboards (Grafana)
- [ ] Alertas configurados

### Documentation
- [ ] API docs completa (OpenAPI)
- [ ] README de setup atualizado
- [ ] Arquitetura documentada
- [ ] Guia de contribuição completo

---

**Última atualização**: 2025-11-10
**Próxima revisão**: Após completar Semana 1-2 (Segurança)
