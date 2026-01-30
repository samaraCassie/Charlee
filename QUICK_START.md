# ⚡ Quick Start - Sistema Freelancer

Setup rápido para rodar o sistema **AGORA** (5 minutos).

---

## 🚨 Problemas Encontrados e Soluções

Durante o setup inicial, você pode enfrentar estes problemas:

### **Problema 1: Database não existe**
```
FATAL: database "charlee_db" does not exist
```

**Solução:**
```bash
docker exec charlee-postgres psql -U charlee -c "CREATE DATABASE charlee_db;"
```

### **Problema 2: Extensão pgvector não instalada**
```
ERROR: extension "vector" is not available
type "vector" does not exist
```

**Solução Rápida:** Use container PostgreSQL com pgvector pré-instalado:

```bash
# Pare o container atual
docker stop charlee-postgres
docker rm charlee-postgres

# Crie novo container com pgvector
docker run -d \
  --name charlee-postgres-pgvector \
  -e POSTGRES_PASSWORD=charlee123 \
  -e POSTGRES_USER=charlee \
  -e POSTGRES_DB=charlee_db \
  -p 5432:5432 \
  ankane/pgvector:latest

# Aguarde 5 segundos
sleep 5

# Verifique se pgvector está disponível
docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "CREATE EXTENSION vector;"
```

---

## ✅ Setup Completo do Zero

### **Passo 1: PostgreSQL com pgvector**

```bash
# Limpe containers anteriores (se existirem)
docker stop charlee-postgres 2>/dev/null || true
docker rm charlee-postgres 2>/dev/null || true

# Crie novo container
docker run -d \
  --name charlee-postgres-pgvector \
  -e POSTGRES_PASSWORD=charlee123 \
  -e POSTGRES_USER=charlee \
  -e POSTGRES_DB=charlee_db \
  -p 5432:5432 \
  ankane/pgvector:latest

# Aguarde inicialização
sleep 5

# Habilite extensão pgvector
docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "CREATE EXTENSION vector;"

echo "✓ PostgreSQL with pgvector ready!"
```

### **Passo 2: Redis**

```bash
# Verifique se Redis já está rodando
docker ps | grep redis && echo "Redis já está rodando" || \
docker run -d --name charlee-redis -p 6379:6379 redis:7-alpine

echo "✓ Redis ready!"
```

### **Passo 3: Backend Python**

```bash
cd /home/sam-cassie/GitHub/Charlee/backend

# Crie virtual environment (se não existir)
test -d venv || python3 -m venv venv

# Ative venv
source venv/bin/activate

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt

# Configure .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://charlee:charlee123@localhost:5432/charlee_db
POSTGRES_USER=charlee
POSTGRES_PASSWORD=charlee123
POSTGRES_DB=charlee_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long
ENVIRONMENT=development
DEBUG=true
EOF

# Gere encryption key
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env

echo "✓ Backend configured!"
```

### **Passo 4: Inicie o Backend**

```bash
# Certifique-se que está no backend com venv ativado
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate

# Inicie servidor
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🧪 Teste Imediato

### **Opção 1: Navegador (Swagger UI)**

1. Abra: http://localhost:8000/docs
2. Você verá a interface Swagger
3. Teste endpoint: **GET /health**
4. Click em **"Try it out"** → **"Execute"**
5. Deve retornar: `{"status":"healthy"}`

### **Opção 2: Terminal (cURL)**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar:
# {"status":"healthy","database":"connected","redis":"connected"}
```

---

## 📮 Usar com Postman (Recomendado)

Agora que o backend está rodando:

1. **Baixe Postman Desktop** (se ainda não tem):
   ```bash
   sudo snap install postman
   postman
   ```

2. **Import coleção:**
   - Postman → **Import**
   - Arraste: `/home/sam-cassie/GitHub/Charlee/backend/postman_collection_freelancer.json`
   - Arraste: `/home/sam-cassie/GitHub/Charlee/backend/postman_environment_local.json`

3. **Selecione environment:**
   - Dropdown (canto superior direito) → **"Charlee - Local Development"**

4. **Teste:**
   - Abra pasta **0. Authentication**
   - Rode request **Login**
   - Token será salvo automaticamente
   - Comece a usar todos os outros endpoints!

**Guia completo:** [backend/POSTMAN_GUIDE.md](backend/POSTMAN_GUIDE.md)

---

## 🎯 Primeiros Testes

### **1. Health Check**
```bash
curl http://localhost:8000/health
```

### **2. Listar Usuários (via Swagger)**
1. Abra http://localhost:8000/docs
2. Procure **GET /api/v1/users**
3. **Try it out** → **Execute**

### **3. Criar Primeira Oportunidade**
- No Postman: **1. RN09 → Create Opportunity #1**
- Ou Swagger UI: **POST /api/v1/opportunities**

---

## 🐛 Troubleshooting

### **Backend não inicia**
```bash
# Ver logs
tail -50 /tmp/charlee_backend.log

# Ou rode em foreground para ver erros:
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python -m uvicorn api.main:app --reload
```

### **Erro: "Connection refused" (PostgreSQL)**
```bash
# Verifique se PostgreSQL está rodando
docker ps | grep postgres

# Se não estiver, inicie
docker start charlee-postgres-pgvector
```

### **Erro: "Extension vector does not exist"**
```bash
# Instale extensão
docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "CREATE EXTENSION vector;"
```

### **Erro: "Module not found" (Python)**
```bash
# Certifique-se que venv está ativado
source venv/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

---

## ✅ Checklist de Verificação

Antes de usar o sistema, verifique:

- [ ] PostgreSQL rodando: `docker ps | grep postgres`
- [ ] Redis rodando: `docker ps | grep redis`
- [ ] Backend rodando: `curl http://localhost:8000/health`
- [ ] Extensão pgvector instalada: `docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "\dx"`
- [ ] Postman instalado (ou usar Swagger UI)

---

## 🚀 Próximos Passos

Depois que tudo estiver funcionando:

1. ✅ Leia: [backend/POSTMAN_GUIDE.md](backend/POSTMAN_GUIDE.md)
2. ✅ Veja documentação completa: [docs/implementacao/freelancer-complete.md](docs/implementacao/freelancer-complete.md)
3. ✅ Configure seus parâmetros de precificação
4. ✅ Adicione suas plataformas freelance
5. ✅ Comece a adicionar oportunidades reais!

---

## 📚 Recursos

- **Swagger UI:** http://localhost:8000/docs
- **Postman Collection:** `backend/postman_collection_freelancer.json`
- **Guia Postman:** `backend/POSTMAN_GUIDE.md`
- **Testes:** `backend/TESTING_FREELANCER.md`
- **Setup completo:** `SETUP_REAL_USE.md`

---

**Pronto! Agora você tem o sistema rodando de verdade!** 🎉
