# ✅ Checklist de Verificação Pós-Setup

Use este checklist para garantir que tudo foi configurado corretamente.

## 🐳 Docker & Containers

- [ ] Docker e Docker Compose instalados
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] Containers rodando
  ```bash
  docker ps
  # Deve mostrar: charlee_db, charlee_redis, charlee_backend
  ```

- [ ] PostgreSQL saudável
  ```bash
  docker exec charlee_db pg_isready -U charlee
  # Deve retornar: accepting connections
  ```

- [ ] Redis acessível
  ```bash
  docker exec charlee_redis redis-cli ping
  # Deve retornar: PONG
  ```

---

## 🗄️ Banco de Dados

- [ ] Migrations executadas
  ```bash
  docker exec charlee_backend alembic current
  # Deve mostrar: 009_add_pgvector_and_worklog
  ```

- [ ] pgvector instalado
  ```bash
  docker exec charlee_db psql -U charlee -d charlee_db \
    -c "SELECT extname, extversion FROM pg_extension WHERE extname='vector';"
  # Deve retornar: vector | 0.5.1 (ou superior)
  ```

- [ ] Tabela WorkLog existe
  ```bash
  docker exec charlee_db psql -U charlee -d charlee_db -c "\dt work_logs;"
  # Deve listar: work_logs table
  ```

- [ ] Coluna embedding existe
  ```bash
  docker exec charlee_db psql -U charlee -d charlee_db \
    -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='freelance_opportunities' AND column_name='embedding';"
  # Deve retornar: embedding | USER-DEFINED
  ```

- [ ] Índice HNSW criado
  ```bash
  docker exec charlee_db psql -U charlee -d charlee_db \
    -c "SELECT indexname FROM pg_indexes WHERE tablename='freelance_opportunities' AND indexname LIKE '%embedding%';"
  # Deve retornar: idx_freelance_opportunities_embedding
  ```

---

## 🔧 Configuração

- [ ] Arquivo .env existe e tem OPENAI_API_KEY
  ```bash
  grep "^OPENAI_API_KEY=sk-" docker/.env
  # Deve retornar a linha com sua API key
  ```

- [ ] Variáveis de redirect URI configuradas
  ```bash
  grep "REDIRECT_URI" docker/.env
  # Deve mostrar GOOGLE_CALENDAR_REDIRECT_URI e MICROSOFT_CALENDAR_REDIRECT_URI
  ```

- [ ] Frontend URL configurado
  ```bash
  grep "^FRONTEND_URL" docker/.env
  # Deve retornar: FRONTEND_URL=http://localhost:3000
  ```

---

## 🚀 API Endpoints

- [ ] Health check OK
  ```bash
  curl -s http://localhost:8000/health | jq
  # Deve retornar: {"status": "ok"}
  ```

- [ ] System stats funcionando
  ```bash
  curl -s http://localhost:8000/api/v1/settings/system | jq
  # Deve retornar JSON com version, uptime_seconds, etc
  ```

- [ ] API docs acessível
  ```bash
  curl -s http://localhost:8000/docs | grep -q "Swagger"
  echo $?
  # Deve retornar: 0 (sucesso)
  ```

---

## 🔐 Autenticação

- [ ] Registro de usuário funciona
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"test","email":"test@example.com","password":"test123","full_name":"Test"}' \
    | jq .username
  # Deve retornar: "test"
  ```

- [ ] Login funciona
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test123"}' \
    | jq .access_token
  # Deve retornar um JWT token
  ```

---

## 💾 Sistema de Backup

- [ ] pg_dump disponível
  ```bash
  docker exec charlee_backend which pg_dump
  # Deve retornar: /usr/bin/pg_dump
  ```

- [ ] SystemMonitor funciona
  ```bash
  docker exec charlee_backend python -c "
from services.system_monitor import system_monitor
print('Uptime:', system_monitor.get_uptime_formatted())
print('Backup dir:', system_monitor.backup_dir)
"
  # Deve mostrar uptime e diretório de backup
  ```

- [ ] Backup pode ser criado (com autenticação)
  ```bash
  # Primeiro faça login e pegue o token
  TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test123"}' | jq -r .access_token)
  
  # Depois teste backup
  curl -X POST http://localhost:8000/api/v1/settings/backup \
    -H "Authorization: Bearer $TOKEN" | jq
  # Deve retornar: {"success": true, ...}
  ```

---

## 📊 Analytics

- [ ] WorkLog model importável
  ```bash
  docker exec charlee_backend python -c "
from database.models import WorkLog
print('WorkLog OK')
"
  # Deve retornar: WorkLog OK
  ```

- [ ] Endpoint de analytics funciona
  ```bash
  # Com autenticação
  TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test123"}' | jq -r .access_token)
  
  curl -s http://localhost:8000/api/v1/analytics/productivity \
    -H "Authorization: Bearer $TOKEN" | jq
  # Deve retornar JSON com completion_rate, avg_time_per_task, productivity_trend
  ```

---

## 🔍 Vector Search

- [ ] Embedding generation funciona
  ```bash
  docker exec charlee_backend python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.embeddings.create(model='text-embedding-ada-002', input='test')
print('Embedding dim:', len(response.data[0].embedding))
"
  # Deve retornar: Embedding dim: 1536
  ```

- [ ] Vector similarity search disponível
  ```bash
  docker exec charlee_backend python -c "
from agent.specialized_agents.projects.semantic_analyzer_agent import SemanticAnalyzerAgent
print('SemanticAnalyzerAgent OK')
"
  # Deve retornar: SemanticAnalyzerAgent OK
  ```

---

## 📅 Calendar Integration

- [ ] Calendar routes carregadas
  ```bash
  curl -s http://localhost:8000/docs | grep -q "calendar"
  echo $?
  # Deve retornar: 0
  ```

- [ ] Redirect URIs usando settings
  ```bash
  docker exec charlee_backend python -c "
from database.config import settings
print('Google redirect:', settings.google_calendar_redirect_uri)
print('Microsoft redirect:', settings.microsoft_calendar_redirect_uri)
"
  # Deve mostrar as URIs configuradas
  ```

---

## 🎨 Frontend (Opcional)

Se você configurou o frontend:

- [ ] Frontend rodando
  ```bash
  curl -s http://localhost:3000 | grep -q "Charlee"
  echo $?
  # Deve retornar: 0
  ```

- [ ] Frontend conecta com backend
  - Abra http://localhost:3000
  - Verifique console do navegador
  - Não deve ter erros de CORS

---

## 📝 Resumo

**Checklist Completo:**

```
[ ] Containers rodando (3/3)
[ ] PostgreSQL + pgvector OK
[ ] Redis OK
[ ] Migrations executadas (009/009)
[ ] .env configurado
[ ] API funcionando
[ ] Autenticação OK
[ ] Backup system OK
[ ] Analytics OK
[ ] Vector search OK
[ ] Calendar integration OK
```

---

## 🆘 Se algo falhou

1. **Veja os logs:**
   ```bash
   docker logs charlee_backend
   docker logs charlee_db
   ```

2. **Reinicie os containers:**
   ```bash
   cd docker
   docker-compose restart
   ```

3. **Execute migrations novamente:**
   ```bash
   docker exec charlee_backend alembic upgrade head
   ```

4. **Consulte a documentação:**
   - [SETUP.md](SETUP.md) para troubleshooting detalhado
   - [QUICKSTART.md](QUICKSTART.md) para instruções básicas

---

**Data da verificação:** _________

**Resultado:** ☐ Tudo OK  ☐ Alguns problemas  ☐ Precisa ajuda

