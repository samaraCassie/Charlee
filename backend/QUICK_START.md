# ⚡ Quick Start - Charlee Database

## 🚀 Configurar Banco de Dados (Primeira Vez)

```bash
cd backend
python setup_database.py
```

Isso vai:
- ✅ Criar todas as tabelas
- ✅ Popular com dados de teste
- ✅ Criar 4 usuários de teste

## 👥 Credenciais de Teste

| Username | Email | Password | Tipo | Status |
|----------|-------|----------|------|--------|
| `samara` | samara@charlee.app | `TestPass123` | Admin | Ativo ✅ |
| `maria.silva` | maria.silva@gmail.com | `TestPass123` | OAuth Google | Ativo ✅ |
| `joaodev` | joao@example.com | `TestPass123` | OAuth GitHub | Ativo ✅ |
| `ana` | ana@example.com | `TestPass123` | Local | Inativo ❌ |

## 🔧 Comandos Úteis

### Resetar Banco de Dados

```bash
python setup_database.py
```

### Apenas Criar Tabelas (Banco Vazio)

```bash
python create_tables.py
```

### Apenas Popular Dados (Tabelas Existem)

```bash
python seed_database.py
```

## 🎯 Iniciar Servidor

```bash
uvicorn api.main:app --reload
```

Acesse:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 📊 Dados Disponíveis

Após executar `setup_database.py`:

- **4 usuários** (1 admin, 2 OAuth, 1 inativo)
- **13 Big Rocks** distribuídos entre usuários
- **23 tarefas** com diversos status
- **8 ciclos menstruais** registrados
- **10 logs diários** da última semana
- **9 logs de auditoria**

## 🧪 Testar API

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "samara", "password": "TestPass123"}'
```

### Listar Big Rocks

```bash
# Primeiro obtenha o token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "samara", "password": "TestPass123"}' | jq -r '.access_token')

# Liste os Big Rocks
curl http://localhost:8000/api/v1/big-rocks \
  -H "Authorization: Bearer $TOKEN"
```

### Listar Tarefas

```bash
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

## 🔍 Verificar Banco de Dados

### SQLite

```bash
sqlite3 charlee.db

sqlite> .tables
sqlite> SELECT COUNT(*) FROM users;
sqlite> SELECT username, email, is_active FROM users;
sqlite> .quit
```

### PostgreSQL

```bash
psql -d charlee -U seu_usuario

charlee=# \dt
charlee=# SELECT COUNT(*) FROM users;
charlee=# SELECT username, email, is_active FROM users;
charlee=# \q
```

## ⚠️ Troubleshooting

### "No module named 'api'"

```bash
# Certifique-se de estar no diretório backend/
cd backend
python setup_database.py
```

### "Cannot import database.config"

```bash
# Instale as dependências
pip install -r requirements.txt
```

### "Connection refused"

```bash
# Verifique as variáveis de ambiente no .env
DATABASE_URL=sqlite:///./charlee.db  # Para SQLite
# ou
DATABASE_URL=postgresql://user:pass@localhost/charlee  # Para PostgreSQL
```

### Resetar Completamente

```bash
# SQLite
rm charlee.db
python setup_database.py

# PostgreSQL
psql -c "DROP DATABASE charlee;"
psql -c "CREATE DATABASE charlee;"
python setup_database.py
```

## 📚 Documentação Completa

Ver [SEED_README.md](SEED_README.md) para documentação detalhada.

---

**Dúvidas?** Consulte a [documentação completa](SEED_README.md) ou abra uma issue.
