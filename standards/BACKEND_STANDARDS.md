# 🐍 Backend Standards - Python/FastAPI

> **Projeto:** Charlee
> **Stack:** Python 3.12+, FastAPI, SQLAlchemy, Pydantic
> **Status:** Obrigatório

---

## 📋 Índice

1. [Convenções de Nomenclatura e Idioma](#convenções-de-nomenclatura-e-idioma)
2. [Estrutura de Código](#estrutura-de-código)
3. [Type Hints e Validação](#type-hints-e-validação)
4. [Padrões de API](#padrões-de-api-fastapi)
5. [Database e ORM](#database-e-orm)
6. [Tratamento de Erros](#tratamento-de-erros)
7. [Logging](#logging)
8. [Formatação e Linting](#formatação-e-linting)
9. [Dependencies](#dependencies)
10. [Performance](#performance)
11. [Exemplos](#exemplos)

---

## 🌍 Convenções de Nomenclatura e Idioma

### Regra Fundamental: Inglês no Código

**TODO código deve ser escrito em INGLÊS** - variáveis, funções, classes, comentários de código, docstrings, nomes de tabelas e colunas no banco de dados.

#### ✅ CORRETO - Inglês no código

```python
# Models
class Task(Base):
    """Task model - represents a user task."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    type = Column(String(20), default="task")
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    def mark_as_completed(self):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()


# Schemas
class TaskCreate(BaseModel):
    """Schema for creating a task."""
    description: str = Field(..., min_length=1)
    type: Literal["fixed_appointment", "task", "continuous"] = "task"
    deadline: Optional[date] = None


# CRUD
def get_tasks(
    db: Session,
    status: Optional[str] = None,
    big_rock_id: Optional[int] = None,
    task_type: Optional[str] = None,
) -> list[Task]:
    """Get list of tasks with optional filters."""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    return query.all()


# Routes
@router.get("/", response_model=TaskListResponse)
def get_tasks(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of tasks with optional filters."""
    tasks = crud.get_tasks(db, skip=skip, limit=limit, status=status)
    return {"total": len(tasks), "tasks": tasks}
```

#### ❌ ERRADO - Português no código

```python
# ❌ NUNCA FAÇA ISSO
class Tarefa(Base):
    """Modelo de tarefa."""
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True)
    descricao = Column(Text, nullable=False)
    tipo = Column(String(20), default="Tarefa")
    status = Column(String(20), default="Pendente")
    criado_em = Column(DateTime, default=datetime.utcnow)

    def marcar_concluida(self):
        """Marca tarefa como concluída."""
        self.status = "Concluída"
```

### Tradução para o Usuário

**Português é usado APENAS**:
- Na interface do usuário (frontend)
- Em mensagens de erro para o usuário final
- Em documentação voltada para usuários finais (READMEs em português)
- Em logs de sistema quando necessário

```python
# ✅ CORRETO - Tradução no frontend/UI
{
    "task": "Clean the kitchen",
    "translation": {
        "pt-BR": "Limpar a cozinha"
    }
}

# ✅ CORRETO - Mensagens de erro
raise HTTPException(
    status_code=404,
    detail="Task not found"  # Frontend traduz para "Tarefa não encontrada"
)
```

### Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| **Classes** | PascalCase | `Task`, `BigRock`, `MenstrualCycle` |
| **Funções/Métodos** | snake_case | `get_tasks()`, `mark_as_completed()` |
| **Variáveis** | snake_case | `task_id`, `big_rock_name` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_STATUS` |
| **Schemas** | PascalCase + Suffix | `TaskCreate`, `TaskResponse` |
| **Rotas** | kebab-case | `/big-rocks`, `/tasks` |
| **Tabelas DB** | snake_case plural | `tasks`, `big_rocks`, `menstrual_cycles` |
| **Colunas DB** | snake_case | `created_at`, `big_rock_id` |

### Status e Tipos em Inglês

```python
# ✅ CORRETO - Valores em inglês
status = Literal["pending", "in_progress", "completed", "cancelled"]
task_type = Literal["fixed_appointment", "task", "continuous"]
phase = Literal["menstrual", "follicular", "ovulation", "luteal"]

# ❌ ERRADO - Valores em português
status = Literal["Pendente", "Em Progresso", "Concluída", "Cancelada"]
```

---

## 🏗️ Estrutura de Código

### Organização de Diretórios

```
backend/
├── api/
│   ├── main.py           # ← FastAPI app, APENAS configuração
│   └── routes/           # ← Um arquivo por domínio
│       ├── __init__.py
│       ├── big_rocks.py
│       ├── tarefas.py
│       └── agent.py
├── agent/
│   ├── core_agent.py
│   ├── orchestrator.py
│   └── specialized_agents/
├── database/
│   ├── config.py         # ← DB connection
│   ├── models/           # ← SQLAlchemy models
│   ├── schemas.py        # ← Pydantic schemas
│   └── crud.py           # ← CRUD operations
├── services/             # ← Business logic
│   ├── __init__.py
│   └── priorizacao.py
├── tests/                # ← Testes organizados igual src
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_agents/
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

### ✅ Regras de Estrutura

**main.py deve conter APENAS**:
```python
# ✅ PERMITIDO em main.py
- Configuração do FastAPI app
- Middlewares (CORS, etc)
- Include de routers
- Endpoints básicos (/, /health)
- Lifespan events

# ❌ PROIBIDO em main.py
- Lógica de rotas
- Funções de negócio
- CRUD operations
- Validações complexas
```

**Um arquivo = Um propósito**:
```python
# ✅ CERTO
# api/routes/tarefas.py - Apenas rotas de tarefas
# services/priorizacao.py - Apenas lógica de priorização

# ❌ ERRADO
# api/routes/utils.py - "Miscelânea" não é propósito
```

---

## 🔤 Type Hints e Validação

### Regra Obrigatória

**TODOS os parâmetros e retornos devem ter type hints.**

```python
# ❌ ERRADO - Sem type hints
def calculate_priority(task, factors):
    return task.score * factors

# ✅ CERTO - Com type hints
def calculate_priority(
    task: Task,
    factors: dict[str, float]
) -> float:
    return task.score * sum(factors.values())
```

### Type Hints Complexos

```python
from typing import Optional, Union, List, Dict, Any
from collections.abc import Sequence

# Opcionais
def get_task(task_id: int) -> Optional[Task]:
    return db.query(Task).get(task_id)

# Union types
def process(data: str | bytes) -> dict[str, Any]:
    ...

# Generics
def filter_items(
    items: Sequence[Task],
    predicate: Callable[[Task], bool]
) -> list[Task]:
    return [item for item in items if predicate(item)]

# Type aliases para reutilização
TaskDict = dict[str, str | int | None]
```

### Pydantic para Validação

**Sempre use Pydantic schemas para request/response.**

```python
from pydantic import BaseModel, Field, validator

class TarefaCreate(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=500)
    big_rock_id: Optional[int] = None
    deadline: Optional[date] = None
    estimativa_horas: float = Field(default=1.0, ge=0.1, le=24.0)

    @validator('descricao')
    def descricao_nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('Descrição não pode ser vazia')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "descricao": "Implementar autenticação JWT",
                "big_rock_id": 1,
                "deadline": "2025-12-01",
                "estimativa_horas": 4.0
            }
        }
```

### MyPy Strict Mode

**Configure `pyproject.toml`:**

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false  # Pode ser muito restritivo
```

---

## 🌐 Padrões de API (FastAPI)

### Estrutura de Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

@router.post(
    "/tarefas",
    response_model=TarefaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova tarefa",
    description="Cria uma nova tarefa associada a um Big Rock",
    tags=["Tarefas"],
    responses={
        201: {"description": "Tarefa criada com sucesso"},
        400: {"description": "Dados inválidos"},
        404: {"description": "Big Rock não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def create_tarefa(
    tarefa: TarefaCreate,
    db: Session = Depends(get_db)
) -> TarefaResponse:
    """
    Criar nova tarefa.

    Args:
        tarefa: Dados da tarefa a ser criada
        db: Sessão do banco de dados

    Returns:
        TarefaResponse: Tarefa criada com ID

    Raises:
        HTTPException 404: Se Big Rock não existir
        HTTPException 400: Se validação falhar
    """
    # Validar Big Rock existe
    if tarefa.big_rock_id:
        big_rock = crud.get_big_rock(db, tarefa.big_rock_id)
        if not big_rock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Big Rock {tarefa.big_rock_id} não encontrado"
            )

    # Criar tarefa
    try:
        nova_tarefa = crud.create_tarefa(db, tarefa)
        return nova_tarefa
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar tarefa"
        )
```

### Status Codes Corretos

| Operação | Sucesso | Erro Comum |
|----------|---------|------------|
| GET (lista) | 200 | 500 |
| GET (item) | 200 | 404, 500 |
| POST | 201 | 400, 409, 500 |
| PUT | 200 | 400, 404, 500 |
| PATCH | 200 | 400, 404, 500 |
| DELETE | 204 | 404, 409, 500 |

```python
# ✅ CERTO
@router.delete("/tarefas/{id}", status_code=status.HTTP_204_NO_CONTENT)

# ❌ ERRADO
@router.delete("/tarefas/{id}")  # Default 200, mas deveria ser 204
```

### Versionamento de API

```python
# ✅ Use prefixos para versões
app.include_router(
    big_rocks.router,
    prefix="/api/v1/big-rocks",
    tags=["Big Rocks"]
)

app.include_router(
    analytics.router,
    prefix="/api/v2/analytics",
    tags=["Analytics (V2)"]
)
```

### Paginação

```python
from fastapi import Query

@router.get("/tarefas")
async def list_tarefas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> PaginatedTarefasResponse:
    total = crud.count_tarefas(db, status=status)
    tarefas = crud.get_tarefas(db, skip=skip, limit=limit, status=status)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tarefas
    }
```

---

## 💾 Database e ORM

### SQLAlchemy Models

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    # ✅ Primary key sempre Integer com autoincrement
    id = Column(Integer, primary_key=True, index=True)

    # ✅ Campos obrigatórios sem default
    descricao = Column(String(500), nullable=False)

    # ✅ Campos opcionais com nullable=True
    big_rock_id = Column(Integer, ForeignKey("big_rocks.id"), nullable=True)

    # ✅ Timestamps automáticos
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ✅ Relationships
    big_rock = relationship("BigRock", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, descricao='{self.descricao[:30]}...')>"
```

### CRUD Operations

**Crie função separada para cada operação:**

```python
# database/crud.py

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Buscar tarefa por ID."""
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> list[Task]:
    """Listar tarefas com filtros."""
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task_data: TarefaCreate) -> Task:
    """Criar nova tarefa."""
    db_task = Task(**task_data.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session,
    task_id: int,
    task_data: TarefaUpdate
) -> Optional[Task]:
    """Atualizar tarefa existente."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    """Deletar tarefa."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True
```

### Transações

```python
from sqlalchemy.exc import SQLAlchemyError

def create_task_with_subtasks(
    db: Session,
    task_data: TarefaCreate,
    subtasks: list[SubtaskCreate]
) -> Task:
    """Criar tarefa com subtarefas em transação."""
    try:
        # Criar tarefa principal
        main_task = Task(**task_data.model_dump())
        db.add(main_task)
        db.flush()  # ← Gera ID sem commitar

        # Criar subtarefas
        for subtask_data in subtasks:
            subtask = Subtask(
                **subtask_data.model_dump(),
                parent_id=main_task.id
            )
            db.add(subtask)

        db.commit()
        db.refresh(main_task)
        return main_task

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erro ao criar tarefa com subtarefas: {e}")
        raise
```

---

## ⚠️ Tratamento de Erros

### Hierarquia de Exceções Custom

```python
# errors.py

class CharleeException(Exception):
    """Base exception para todas as exceções do Charlee."""
    pass

class ValidationError(CharleeException):
    """Erro de validação de dados."""
    pass

class NotFoundError(CharleeException):
    """Recurso não encontrado."""
    pass

class CapacityExceededError(CharleeException):
    """Capacidade de trabalho excedida."""
    pass
```

### Exception Handlers

```python
# api/main.py

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "type": "not_found_error"
        }
    )

@app.exception_handler(CapacityExceededError)
async def capacity_exceeded_handler(request: Request, exc: CapacityExceededError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "type": "capacity_exceeded",
            "severity": "warning"
        }
    )
```

### Uso em Endpoints

```python
@router.get("/tarefas/{id}")
async def get_tarefa(id: int, db: Session = Depends(get_db)) -> TarefaResponse:
    tarefa = crud.get_task(db, id)

    if not tarefa:
        raise NotFoundError(f"Tarefa {id} não encontrada")

    return tarefa
```

---

## 📝 Logging

### Configuração

```python
import logging
from pythonjsonlogger import jsonlogger

# Configurar logger estruturado
def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    return logger

logger = setup_logging()
```

### Uso

```python
# ✅ CERTO - Logs estruturados
logger.info(
    "Tarefa criada",
    extra={
        "task_id": tarefa.id,
        "user_id": user_id,
        "big_rock_id": tarefa.big_rock_id
    }
)

logger.error(
    "Falha ao criar tarefa",
    extra={
        "user_id": user_id,
        "error": str(e),
        "task_data": task_data.model_dump()
    },
    exc_info=True
)

# ❌ ERRADO - Logs não estruturados
print(f"Tarefa {tarefa.id} criada")  # Nunca use print!
logger.info(f"Erro: {e}")  # F-string ruim para parsing
```

### Níveis de Log

| Nível | Quando Usar |
|-------|-------------|
| DEBUG | Detalhes de debugging, variáveis intermediárias |
| INFO | Eventos normais (tarefa criada, API chamada) |
| WARNING | Algo inesperado mas não crítico |
| ERROR | Erro que impede operação |
| CRITICAL | Erro que afeta sistema todo |

```python
logger.debug(f"Query SQL: {query}")
logger.info(f"Usuário {user_id} autenticado")
logger.warning(f"Capacidade em {capacity}% - próximo do limite")
logger.error(f"Falha ao conectar DB: {error}")
logger.critical(f"Redis offline - sistema degradado")
```

---

## 🎨 Formatação e Linting

### Black (Formatador)

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''
```

```bash
# Formatar tudo
black backend/

# Verificar sem modificar
black --check backend/

# Diff do que seria mudado
black --diff backend/
```

### Ruff (Linter)

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "A",   # flake8-builtins
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "RUF", # Ruff-specific rules
]

ignore = [
    "E501",  # line too long (black já cuida)
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # imports não usados ok em __init__
```

```bash
# Lint com auto-fix
ruff check backend/ --fix

# Apenas verificar
ruff check backend/

# Específico para um arquivo
ruff check backend/api/routes/tarefas.py
```

### MyPy (Type Checker)

```bash
# Type check tudo
mypy backend/

# Específico
mypy backend/agent/orchestrator.py

# Com relatório HTML
mypy backend/ --html-report ./mypy-report
```

---

## 📦 Dependencies

### requirements.txt vs requirements-dev.txt

```txt
# requirements.txt - Apenas produção
fastapi[standard]>=0.115.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
pydantic>=2.5.3
python-dotenv>=1.0.0

# requirements-dev.txt - Desenvolvimento
-r requirements.txt  # ← Inclui produção

# Testing
pytest>=7.4.4
pytest-cov>=4.1.0
pytest-asyncio>=0.23.3

# Quality
black>=23.12.1
ruff>=0.1.11
mypy>=1.8.0

# Utilities
ipython>=8.20.0
```

### Pin de Versões

```txt
# ❌ EVITAR - Muito permissivo
fastapi

# ⚠️ OK para dev - Mas teste antes de prod
fastapi>=0.115.0

# ✅ IDEAL para prod - Pin exato
fastapi==0.115.5
uvicorn==0.27.2
```

### Atualização de Deps

```bash
# Ver deps desatualizadas
pip list --outdated

# Atualizar com cuidado
pip install --upgrade fastapi

# Re-gerar requirements.txt pinado
pip freeze > requirements-frozen.txt
```

---

## ⚡ Performance

### Query Optimization

```python
# ❌ ERRADO - N+1 queries
tasks = db.query(Task).all()
for task in tasks:
    big_rock = task.big_rock  # ← Query adicional para cada task!

# ✅ CERTO - Eager loading
from sqlalchemy.orm import joinedload

tasks = db.query(Task).options(joinedload(Task.big_rock)).all()
for task in tasks:
    big_rock = task.big_rock  # ← Já está carregado
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_priority_weights() -> dict[str, float]:
    """Cache de pesos de priorização (raramente mudam)."""
    return {
        "urgency": 0.3,
        "importance": 0.25,
        "effort": 0.15,
        # ...
    }
```

### Async quando faz sentido

```python
# ✅ Async para I/O bound
@router.get("/external-data")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()

# ❌ Async desnecessário para CPU bound
@router.get("/calculate")
async def calculate():  # ← async não ajuda aqui
    return sum(range(1000000))  # CPU bound

# ✅ Melhor síncrono
@router.get("/calculate")
def calculate():
    return sum(range(1000000))
```

---

## 📚 Exemplos Completos

### Endpoint Completo

```python
# api/routes/tarefas.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from database import crud, schemas
from database.config import get_db
from errors import NotFoundError, CapacityExceededError
from services.capacity import check_capacity

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=schemas.TarefaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova tarefa",
    description="Cria uma nova tarefa e verifica capacidade de trabalho",
)
async def create_tarefa(
    tarefa: schemas.TarefaCreate,
    db: Session = Depends(get_db)
) -> schemas.TarefaResponse:
    """
    Criar nova tarefa com verificação de capacidade.

    Args:
        tarefa: Dados da tarefa
        db: Sessão do banco

    Returns:
        Tarefa criada

    Raises:
        HTTPException 404: Big Rock não encontrado
        HTTPException 400: Capacidade excedida
    """
    # Validar Big Rock se fornecido
    if tarefa.big_rock_id:
        big_rock = crud.get_big_rock(db, tarefa.big_rock_id)
        if not big_rock:
            logger.warning(
                "Tentativa de criar tarefa com Big Rock inexistente",
                extra={"big_rock_id": tarefa.big_rock_id}
            )
            raise NotFoundError(
                f"Big Rock {tarefa.big_rock_id} não encontrado"
            )

    # Verificar capacidade
    try:
        capacity_ok = check_capacity(
            db,
            additional_hours=tarefa.estimativa_horas
        )
        if not capacity_ok:
            raise CapacityExceededError(
                "Adicionar esta tarefa excederia sua capacidade"
            )
    except Exception as e:
        logger.error(
            "Erro ao verificar capacidade",
            extra={"error": str(e)},
            exc_info=True
        )
        # Continua mesmo se check falhar

    # Criar tarefa
    try:
        nova_tarefa = crud.create_tarefa(db, tarefa)
        logger.info(
            "Tarefa criada com sucesso",
            extra={
                "task_id": nova_tarefa.id,
                "big_rock_id": tarefa.big_rock_id
            }
        )
        return nova_tarefa

    except Exception as e:
        logger.error(
            "Erro ao criar tarefa",
            extra={"task_data": tarefa.model_dump()},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar tarefa"
        )


@router.get(
    "/",
    response_model=schemas.PaginatedTarefasResponse,
    summary="Listar tarefas",
)
async def list_tarefas(
    skip: int = Query(0, ge=0, description="Itens para pular"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de itens"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    big_rock_id: Optional[int] = Query(None, description="Filtrar por Big Rock"),
    db: Session = Depends(get_db)
) -> schemas.PaginatedTarefasResponse:
    """Listar tarefas com paginação e filtros."""
    tarefas = crud.get_tarefas(
        db,
        skip=skip,
        limit=limit,
        status=status,
        big_rock_id=big_rock_id
    )

    total = crud.count_tarefas(db, status=status, big_rock_id=big_rock_id)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tarefas
    }
```

---

## ✅ Checklist de Qualidade

Antes de commitar código backend:

- [ ] Type hints em todas as funções
- [ ] Docstrings em funções públicas
- [ ] Validação com Pydantic
- [ ] Tratamento de erros adequado
- [ ] Logging estruturado
- [ ] Black formatação (100 chars)
- [ ] Ruff linting sem warnings
- [ ] MyPy type check passando
- [ ] Testes unitários escritos
- [ ] Cobertura >= 80%

---

**Última atualização:** 2025-11-10
**Responsável:** Samara Cassie
