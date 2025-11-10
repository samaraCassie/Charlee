# 🧪 Testing Standards - Testes e Qualidade

> **Projeto:** Charlee
> **Frameworks:** Pytest (backend), Vitest (frontend), Playwright (E2E)
> **Coverage Mínimo:** 80%
> **Status:** Obrigatório

---

## 📋 Índice

1. [Pirâmide de Testes](#pirâmide-de-testes)
2. [Testes Backend (Pytest)](#testes-backend-pytest)
3. [Testes Frontend (Vitest)](#testes-frontend-vitest)
4. [Testes E2E (Playwright)](#testes-e2e-playwright)
5. [Coverage Requirements](#coverage-requirements)
6. [Mocking e Fixtures](#mocking-e-fixtures)

---

## 🔺 Pirâmide de Testes

```
        /\
       /  \      E2E (10%)
      /____\     - Fluxos críticos
     /      \    - Happy paths
    /  Inte  \   Integração (20%)
   /  gração  \  - APIs + DB
  /____________\ - Services
 /              \
/   Unitários    \ Unit (70%)
/__________________\ - Funções puras
                     - Componentes isolados
```

### Distribuição Recomendada

| Tipo | % do Total | Quantidade (estimada) |
|------|------------|----------------------|
| **Unitários** | 70% | ~100-150 testes |
| **Integração** | 20% | ~30-40 testes |
| **E2E** | 10% | ~15-20 testes |

---

## 🐍 Testes Backend (Pytest)

### Estrutura de Testes

```
backend/tests/
├── conftest.py              # ← Fixtures globais
├── test_api/
│   ├── __init__.py
│   ├── test_big_rocks.py
│   ├── test_tarefas.py
│   ├── test_agent.py
│   └── test_wellness.py
├── test_services/
│   ├── test_priorizacao.py
│   └── test_capacity.py
├── test_agents/
│   ├── test_orchestrator.py
│   ├── test_cycle_aware.py
│   └── test_capacity_guard.py
└── test_database/
    ├── test_models.py
    └── test_crud.py
```

### Fixtures Globais

```python
# conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from database.config import Base, get_db

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db():
    """
    Database fixture que cria schema e limpa após cada teste.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    TestClient FastAPI com DB override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_big_rock(db):
    """Big Rock de exemplo."""
    from database.models import BigRock

    big_rock = BigRock(
        name="Saúde e Bem-estar",
        description="Cuidar da saúde física e mental",
        priority=1
    )
    db.add(big_rock)
    db.commit()
    db.refresh(big_rock)
    return big_rock


@pytest.fixture
def sample_task(db, sample_big_rock):
    """Tarefa de exemplo."""
    from database.models import Task

    task = Task(
        descricao="Caminhar 30 minutos",
        tipo="Tarefa",
        big_rock_id=sample_big_rock.id,
        status="Pendente"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

### Testes de API

```python
# tests/test_api/test_big_rocks.py

import pytest
from fastapi import status

class TestBigRocksAPI:
    """Testes para endpoints de Big Rocks."""

    def test_create_big_rock(self, client):
        """Deve criar Big Rock com sucesso."""
        response = client.post(
            "/api/v1/big-rocks",
            json={
                "name": "Carreira",
                "description": "Desenvolvimento profissional",
                "priority": 1
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Carreira"
        assert "id" in data
        assert "criado_em" in data

    def test_create_big_rock_invalid_data(self, client):
        """Deve retornar 400 para dados inválidos."""
        response = client.post(
            "/api/v1/big-rocks",
            json={
                "name": "",  # ← Nome vazio inválido
                "priority": 1
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_big_rocks(self, client, sample_big_rock):
        """Deve listar Big Rocks."""
        response = client.get("/api/v1/big-rocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == sample_big_rock.name

    def test_get_big_rock(self, client, sample_big_rock):
        """Deve obter Big Rock por ID."""
        response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_big_rock.id

    def test_get_big_rock_not_found(self, client):
        """Deve retornar 404 para ID inexistente."""
        response = client.get("/api/v1/big-rocks/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_big_rock(self, client, sample_big_rock):
        """Deve atualizar Big Rock."""
        response = client.patch(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            json={"name": "Saúde"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Saúde"

    def test_delete_big_rock(self, client, sample_big_rock):
        """Deve deletar Big Rock."""
        response = client.delete(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verificar que foi deletado
        get_response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
```

### Testes de Services

```python
# tests/test_services/test_priorizacao.py

import pytest
from datetime import date, timedelta
from services.priorizacao import SistemaPriorizacao

class TestSistemaPriorizacao:
    """Testes para sistema de priorização."""

    @pytest.fixture
    def sistema(self, db):
        return SistemaPriorizacao(db)

    def test_calcular_urgencia(self, sistema):
        """Deve calcular urgência corretamente."""
        hoje = date.today()

        # Tarefa vencendo hoje = urgência alta
        urgencia_hoje = sistema.calcular_urgencia(hoje)
        assert urgencia_hoje >= 0.9

        # Tarefa em 7 dias = urgência média
        urgencia_semana = sistema.calcular_urgencia(hoje + timedelta(days=7))
        assert 0.4 <= urgencia_semana <= 0.6

        # Tarefa em 30 dias = urgência baixa
        urgencia_mes = sistema.calcular_urgencia(hoje + timedelta(days=30))
        assert urgencia_mes <= 0.3

    def test_priorizar_tarefas(self, sistema, sample_task):
        """Deve ordenar tarefas por prioridade."""
        tarefas = sistema.priorizar_tarefas(limite=10)

        assert isinstance(tarefas, list)
        # Verificar que está ordenado (prioridade decrescente)
        for i in range(len(tarefas) - 1):
            assert tarefas[i].prioridade_calculada >= tarefas[i+1].prioridade_calculada
```

### Testes Parametrizados

```python
# Testar múltiplos cenários com @pytest.mark.parametrize

@pytest.mark.parametrize("status_input,status_expected", [
    ("Pendente", "pending"),
    ("Em Progresso", "in_progress"),
    ("Concluída", "completed"),
])
def test_status_mapping(status_input, status_expected):
    """Deve mapear status corretamente."""
    result = map_status(status_input)
    assert result == status_expected


@pytest.mark.parametrize("hours,expected_capacity", [
    (2.0, True),   # Dentro da capacidade
    (8.0, True),   # Limite da capacidade
    (10.0, False), # Acima da capacidade
])
def test_check_capacity(db, hours, expected_capacity):
    """Deve verificar capacidade corretamente."""
    result = check_capacity(db, additional_hours=hours)
    assert result == expected_capacity
```

---

## ⚛️ Testes Frontend (Vitest)

### Configuração Vitest

```typescript
// vitest.config.ts

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'src/main.tsx',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Setup de Testes

```typescript
// src/__tests__/setup.ts

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup após cada teste
afterEach(() => {
  cleanup();
});

// Mock de window.matchMedia (para testes de responsividade)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

### Testes de Stores (Zustand)

```typescript
// src/__tests__/unit/stores/taskStore.test.ts

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTaskStore } from '@/stores/taskStore';
import { taskService } from '@/services/taskService';

// Mock do service
vi.mock('@/services/taskService');

describe('taskStore', () => {
  beforeEach(() => {
    // Reset store
    useTaskStore.setState({
      tasks: [],
      loading: false,
      error: null,
    });

    // Clear mocks
    vi.clearAllMocks();
  });

  it('deve buscar tarefas com sucesso', async () => {
    const mockTasks = [
      { id: '1', title: 'Task 1', status: 'pending' },
      { id: '2', title: 'Task 2', status: 'completed' },
    ];

    vi.mocked(taskService.getTasks).mockResolvedValue(mockTasks);

    const { fetchTasks } = useTaskStore.getState();
    await fetchTasks();

    const { tasks, loading, error } = useTaskStore.getState();

    expect(tasks).toHaveLength(2);
    expect(loading).toBe(false);
    expect(error).toBe(null);
    expect(taskService.getTasks).toHaveBeenCalledTimes(1);
  });

  it('deve tratar erro ao buscar tarefas', async () => {
    vi.mocked(taskService.getTasks).mockRejectedValue(
      new Error('Network error')
    );

    const { fetchTasks } = useTaskStore.getState();
    await fetchTasks();

    const { tasks, loading, error } = useTaskStore.getState();

    expect(tasks).toHaveLength(0);
    expect(loading).toBe(false);
    expect(error).toContain('Network error');
  });

  it('deve adicionar tarefa', async () => {
    const newTask = { id: '3', title: 'New Task', status: 'pending' };

    vi.mocked(taskService.createTask).mockResolvedValue(newTask);

    const { addTask } = useTaskStore.getState();
    await addTask({ title: 'New Task', status: 'pending' });

    const { tasks } = useTaskStore.getState();

    expect(tasks).toHaveLength(1);
    expect(tasks[0].title).toBe('New Task');
  });
});
```

### Testes de Componentes

```typescript
// src/__tests__/unit/components/TaskCard.test.tsx

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from '@/components/TaskCard';

describe('TaskCard', () => {
  const mockTask = {
    id: '1',
    title: 'Test Task',
    description: 'Test description',
    status: 'pending' as const,
    createdAt: new Date().toISOString(),
  };

  it('deve renderizar tarefa corretamente', () => {
    render(<TaskCard task={mockTask} onComplete={vi.fn()} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('deve chamar onComplete ao clicar no botão', () => {
    const onCompleteMock = vi.fn();

    render(<TaskCard task={mockTask} onComplete={onCompleteMock} />);

    const completeButton = screen.getByRole('button', { name: /completar/i });
    fireEvent.click(completeButton);

    expect(onCompleteMock).toHaveBeenCalledWith(mockTask.id);
    expect(onCompleteMock).toHaveBeenCalledTimes(1);
  });

  it('deve aplicar classe correta baseado no status', () => {
    const { rerender } = render(
      <TaskCard task={mockTask} onComplete={vi.fn()} />
    );

    let card = screen.getByRole('article');
    expect(card).toHaveClass('border-yellow-500'); // pending

    rerender(
      <TaskCard
        task={{ ...mockTask, status: 'completed' }}
        onComplete={vi.fn()}
      />
    );

    card = screen.getByRole('article');
    expect(card).toHaveClass('border-green-500'); // completed
  });
});
```

---

## 🎭 Testes E2E (Playwright)

### Configuração

```typescript
// playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Testes E2E

```typescript
// e2e/task-flow.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Fluxo de Tarefas', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('deve criar e completar tarefa', async ({ page }) => {
    // Criar Big Rock
    await page.click('text=Novo Big Rock');
    await page.fill('input[name="name"]', 'Saúde');
    await page.fill('textarea[name="description"]', 'Cuidar da saúde');
    await page.click('button[type="submit"]');

    // Aguardar confirmação
    await expect(page.locator('text=Saúde')).toBeVisible();

    // Criar Tarefa
    await page.click('text=Nova Tarefa');
    await page.fill('input[name="title"]', 'Caminhar 30 minutos');
    await page.selectOption('select[name="bigRock"]', { label: 'Saúde' });
    await page.click('button[type="submit"]');

    // Verificar que tarefa aparece
    await expect(page.locator('text=Caminhar 30 minutos')).toBeVisible();

    // Completar tarefa
    await page.click('[data-testid="complete-task-button"]');

    // Verificar status
    await expect(page.locator('[data-testid="task-status"]')).toHaveText(
      'completed'
    );
  });

  test('deve filtrar tarefas por status', async ({ page }) => {
    // Navegar para lista de tarefas
    await page.goto('/tasks');

    // Selecionar filtro
    await page.selectOption('select[name="status-filter"]', 'pending');

    // Verificar que apenas tarefas pendentes aparecem
    const tasks = page.locator('[data-testid="task-card"]');
    const count = await tasks.count();

    for (let i = 0; i < count; i++) {
      const status = await tasks.nth(i).getAttribute('data-status');
      expect(status).toBe('pending');
    }
  });
});
```

---

## 📊 Coverage Requirements

### Mínimos Obrigatórios

| Métrica | Mínimo | Ideal |
|---------|--------|-------|
| **Lines** | 80% | 90%+ |
| **Functions** | 80% | 90%+ |
| **Branches** | 75% | 85%+ |
| **Statements** | 80% | 90%+ |

### Comando de Coverage

```bash
# Backend
pytest --cov=backend --cov-report=html --cov-fail-under=80

# Frontend
npm run test:coverage

# Ver relatório
open coverage/index.html
```

### Arquivos Excluídos de Coverage

```python
# Backend - pyproject.toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
    "*/venv/*",
]
```

```typescript
// Frontend - vitest.config.ts
exclude: [
  'node_modules/',
  'src/__tests__/',
  '**/*.d.ts',
  '**/*.config.*',
  'src/main.tsx',
]
```

---

## 🎭 Mocking e Fixtures

### Mocks de Serviços

```typescript
// Mock de API service
vi.mock('@/services/taskService', () => ({
  taskService: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
  },
}));
```

### Factory de Dados de Teste

```python
# tests/factories.py

from datetime import date, timedelta
from database.models import Task, BigRock

class BigRockFactory:
    @staticmethod
    def create(db, **kwargs):
        defaults = {
            "name": "Test Big Rock",
            "description": "Test description",
            "priority": 1,
        }
        defaults.update(kwargs)

        big_rock = BigRock(**defaults)
        db.add(big_rock)
        db.commit()
        db.refresh(big_rock)
        return big_rock

class TaskFactory:
    @staticmethod
    def create(db, big_rock=None, **kwargs):
        if not big_rock:
            big_rock = BigRockFactory.create(db)

        defaults = {
            "descricao": "Test task",
            "tipo": "Tarefa",
            "big_rock_id": big_rock.id,
            "status": "Pendente",
            "deadline": date.today() + timedelta(days=7),
        }
        defaults.update(kwargs)

        task = Task(**defaults)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

# Uso
def test_something(db):
    big_rock = BigRockFactory.create(db, name="Saúde")
    task = TaskFactory.create(db, big_rock=big_rock, descricao="Caminhar")
```

---

## ✅ Checklist de Testes

Antes de mergear:

- [ ] Todos os testes passam
- [ ] Coverage >= 80%
- [ ] Testes para features novas
- [ ] Testes para bug fixes
- [ ] Casos edge testados
- [ ] Mocks apropriados
- [ ] Sem testes skip/xfail sem justificativa
- [ ] Testes E2E para fluxos críticos

---

**Última atualização:** 2025-11-10
