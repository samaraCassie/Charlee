# Backend Tests

## Estrutura

```
tests/
├── conftest.py              # Pytest config e fixtures globais
├── test_api/                # Testes de API (endpoints)
│   ├── test_health.py
│   ├── test_big_rocks.py
│   └── test_tarefas.py
├── test_services/           # Testes de lógica de negócio
└── test_agents/             # Testes de agentes AI
```

## Rodando os Testes

### Todos os testes
```bash
cd backend
pytest
```

### Com coverage
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Apenas um arquivo
```bash
pytest tests/test_api/test_health.py
```

### Apenas uma classe
```bash
pytest tests/test_api/test_big_rocks.py::TestBigRocksAPI
```

### Apenas um teste específico
```bash
pytest tests/test_api/test_big_rocks.py::TestBigRocksAPI::test_create_big_rock
```

### Com output verbose
```bash
pytest -v
```

### Com print statements
```bash
pytest -s
```

## Fixtures Disponíveis

### `db`
Session do banco de dados de teste (SQLite em memória).

```python
def test_something(db):
    # Usar db aqui
    pass
```

### `client`
TestClient do FastAPI com database override.

```python
def test_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
```

### `sample_big_rock`
Big Rock de exemplo já criado no banco.

```python
def test_with_big_rock(sample_big_rock):
    assert sample_big_rock.name == "Saúde e Bem-estar"
```

### `sample_task`
Tarefa de exemplo já criada no banco.

```python
def test_with_task(sample_task):
    assert sample_task.descricao == "Caminhar 30 minutos"
```

## Escrevendo Novos Testes

### Estrutura de um teste

```python
import pytest
from fastapi import status

class TestMeuEndpoint:
    """Test suite para meu endpoint."""

    def test_caso_sucesso(self, client):
        """Deve retornar sucesso para input válido."""
        response = client.post("/api/v1/endpoint", json={"data": "valid"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["result"] == "expected"

    def test_caso_erro(self, client):
        """Deve retornar erro para input inválido."""
        response = client.post("/api/v1/endpoint", json={"data": "invalid"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

### Boas Práticas

1. **Nomes descritivos**: `test_create_task_with_valid_data`
2. **Arrange-Act-Assert**: Separar preparação, ação e verificação
3. **Um conceito por teste**: Não testar múltiplas coisas juntas
4. **Docstrings**: Explicar o que o teste valida
5. **Fixtures**: Reutilizar setup comum

## Coverage Goals

- **Mínimo**: 80%
- **Ideal**: 90%+

Verificar coverage:
```bash
pytest --cov=. --cov-report=term --cov-fail-under=80
```
