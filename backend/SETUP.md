# Setup Guide - Charlee Backend

Este guia explica como configurar o ambiente de desenvolvimento do backend do Charlee de forma rápida e fácil.

## 📋 Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 14 ou superior (para produção)
- Redis 7.0 ou superior (para cache)
- Git

## 🚀 Setup Rápido (Recomendado)

### Opção 1: Script Automatizado

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

O script irá:
- ✅ Verificar a versão do Python
- ✅ Criar ambiente virtual
- ✅ Instalar todas as dependências
- ✅ Criar arquivo `.env` a partir do `.env.example`
- ✅ Configurar pre-commit hooks

### Opção 2: Usando Make

```bash
cd backend
make setup
```

## 📦 Setup Manual

Se preferir fazer o setup manualmente:

### 1. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências

```bash
# Instalar todas as dependências (desenvolvimento)
pip install -r requirements-dev.txt

# Ou apenas produção
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

Variáveis essenciais no `.env`:

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/charlee

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (gere um aleatório)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# APIs (opcional para funcionalidades AI)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

### 4. Executar Migrações

```bash
alembic upgrade head
```

### 5. Rodar Testes

```bash
pytest tests/
```

### 6. Iniciar Servidor

```bash
uvicorn api.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`

## 🛠️ Comandos Úteis (Make)

Após o setup, você pode usar estes comandos:

### Desenvolvimento

```bash
make run          # Inicia servidor de desenvolvimento
make test         # Roda todos os testes
make test-fast    # Testes em paralelo
make test-cov     # Testes com cobertura
make format       # Formata código
make lint         # Executa linters
```

### Database

```bash
make migrate              # Aplica migrações
make migration msg="..."  # Cria nova migração
make db-reset            # Reset completo (⚠️ CUIDADO)
```

### Limpeza

```bash
make clean        # Remove cache
make clean-all    # Remove venv e cache
```

## 🔧 Dependências Principais

### Produção

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validação de dados
- **PostgreSQL** (psycopg2-binary) - Banco de dados
- **Redis** - Cache e filas
- **Alembic** - Migrações
- **python-jose** - JWT tokens
- **passlib + bcrypt** - Hash de senhas
- **authlib** - OAuth
- **agno** - Framework de agentes AI

### Desenvolvimento

- **pytest** - Framework de testes
- **black** - Formatação de código
- **ruff** - Linter moderno
- **mypy** - Type checking
- **pre-commit** - Git hooks

## 🐛 Troubleshooting

### Erro: "No module named 'jose'"

```bash
pip install python-jose[cryptography]
```

### Erro: "bcrypt version compatibility"

```bash
pip install "bcrypt>=4.1.0,<4.2.0" --force-reinstall
```

### Erro: "email-validator not installed"

```bash
pip install email-validator
```

### Erro: "No module named 'authlib'"

```bash
pip install authlib itsdangerous
```

### Testes falhando por falta de dependências

```bash
# Reinstale todas as dependências
pip install -r requirements-dev.txt --force-reinstall
```

### Erro de permissão no setup.sh

```bash
chmod +x setup.sh
```

## 📚 Estrutura de Dependências

```
requirements.txt          # Produção (mínimo necessário)
├── fastapi
├── sqlalchemy
├── pydantic
├── python-jose
├── passlib
└── bcrypt (fixado em 4.1.x)

requirements-dev.txt      # Desenvolvimento (inclui produção)
├── requirements.txt
├── pytest (+ plugins)
├── black
├── ruff
└── mypy
```

## ✅ Verificação de Setup

Para verificar se tudo está funcionando:

```bash
# 1. Ativar ambiente
source venv/bin/activate

# 2. Verificar instalação
python -c "import fastapi, sqlalchemy, pytest; print('✓ Dependencies OK')"

# 3. Rodar testes rápidos
pytest tests/test_api/test_health.py -v

# 4. Verificar servidor
curl http://localhost:8000/health
```

## 🔄 Atualizando Dependências

```bash
# Atualizar todas as dependências
pip install --upgrade -r requirements-dev.txt

# Gerar novo requirements (se necessário)
pip freeze > requirements-frozen.txt
```

## 📝 Notas Importantes

1. **bcrypt fixado em 4.1.x**: O bcrypt 5.0+ tem incompatibilidade com passlib. Por isso fixamos em `4.1.x`.

2. **email-validator**: Necessário para validação de emails com Pydantic v2.

3. **authlib + itsdangerous**: Necessários para OAuth e segurança de sessões.

4. **Ambiente virtual**: Sempre use um ambiente virtual para evitar conflitos de dependências.

5. **Pre-commit hooks**: Instalados automaticamente pelo script de setup. Execute `pre-commit install` se fizer setup manual.

## 🆘 Suporte

Se encontrar problemas:

1. Verifique que está usando Python 3.11+
2. Certifique-se de estar no ambiente virtual (`source venv/bin/activate`)
3. Tente `make clean` seguido de `make install`
4. Confira os logs de erro e mensagens de traceback
5. Consulte a documentação das dependências específicas

## 🎯 Próximos Passos

Após o setup:

1. Leia [BACKEND_STANDARDS.md](../standards/BACKEND_STANDARDS.md)
2. Confira [TESTING_STANDARDS.md](../standards/TESTING_STANDARDS.md)
3. Explore a documentação da API em `http://localhost:8000/docs`
4. Rode os testes: `make test`
5. Comece a desenvolver! 🚀
