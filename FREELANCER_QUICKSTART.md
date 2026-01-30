# 🚀 Quick Start - Sistema Freelancer Completo

Sistema completo de gestão de projetos freelance com **backend FastAPI + frontend React**.

---

## ⚡ Iniciar Sistema (2 comandos)

### **Terminal 1: Backend**
```bash
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **Terminal 2: Frontend**
```bash
cd /home/sam-cassie/GitHub/Charlee/interfaces/web
npm run dev
```

### **Acesse:**
- **Frontend:** http://localhost:5173/freelancer/opportunities
- **Backend API:** http://localhost:8000/docs

---

## 🎯 Primeiro Uso

1. **Acesse o frontend**: http://localhost:5173/freelancer/opportunities

2. **Crie uma oportunidade**:
   - Click **"Nova Oportunidade"**
   - Preencha os dados (plataforma, título, descrição, orçamento)
   - Salve

3. **Analise automaticamente**:
   - Click **"Analisar"** no card da oportunidade
   - Aguarde alguns segundos
   - Veja risco, pricing e cálculo financeiro

4. **Tome decisão**:
   - Click **"Ver Detalhes"**
   - Veja análise completa com red/green flags
   - Aceitar / Negociar / Rejeitar

5. **Configure seus parâmetros**:
   - Acesse: http://localhost:5173/freelancer/pricing
   - Ajuste taxa horária, multiplicadores, etc.

6. **Veja seus insights**:
   - Acesse: http://localhost:5173/freelancer/analytics
   - Veja receita, top skills, performance de learning

---

## 📱 Páginas Disponíveis

| Página | URL | Função |
|--------|-----|--------|
| **Oportunidades** | `/freelancer/opportunities` | Lista e gerencia todas as oportunidades |
| **Detalhes** | `/freelancer/opportunities/:id` | Análise completa da oportunidade |
| **Analytics** | `/freelancer/analytics` | Insights de carreira e performance |
| **Pricing** | `/freelancer/pricing` | Configuração de parâmetros de precificação |

---

## 🛠️ Pré-requisitos (primeira vez)

### **1. PostgreSQL com pgvector**
```bash
docker run -d \
  --name charlee-postgres-pgvector \
  -e POSTGRES_PASSWORD=charlee123 \
  -e POSTGRES_USER=charlee \
  -e POSTGRES_DB=charlee_db \
  -p 5432:5432 \
  ankane/pgvector:latest

docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "CREATE EXTENSION vector;"
```

### **2. Redis**
```bash
docker run -d --name charlee-redis -p 6379:6379 redis:7-alpine
```

### **3. Backend Dependencies**
```bash
cd /home/sam-cassie/GitHub/Charlee/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **4. Frontend Dependencies**
```bash
cd /home/sam-cassie/GitHub/Charlee/interfaces/web
npm install
```

### **5. .env Backend**
Crie `backend/.env`:
```bash
DATABASE_URL=postgresql://charlee:charlee123@localhost:5432/charlee_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long
ENVIRONMENT=development
DEBUG=true
```

Gere encryption key:
```bash
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" >> .env
```

---

## ✨ Funcionalidades

### **Backend (FastAPI)**
- ✅ RN09: Prevenção de duplicação
- ✅ RN10: Rate limiting
- ✅ RN11: Cálculo financeiro (USD→BRL + impostos)
- ✅ RN12: Avaliação de risco de cliente
- ✅ RN13: Conformidade LGPD
- ✅ Pricing automático com multiplicadores
- ✅ Geração de propostas de negociação
- ✅ 3 Learning components (Pricing, Rejection, Hourly Rate)
- ✅ 7 Agentes AI (Collector, Analyzer, Evaluator, Negotiator, etc.)

### **Frontend (React + TypeScript)**
- ✅ Interface moderna e responsiva
- ✅ Dark mode
- ✅ Gestão completa de oportunidades
- ✅ Analytics com gráficos interativos
- ✅ Configuração de parâmetros de pricing
- ✅ Dashboard de learning components
- ✅ Componentes shadcn/ui

---

## 📊 Fluxo Completo

```
1. Adicionar Oportunidade
   ↓
2. Processar (Auto)
   ├─ Checagem de duplicação
   ├─ Avaliação de risco
   ├─ Cálculo financeiro
   └─ Sugestão de pricing
   ↓
3. Ver Análise Completa
   ├─ Red/Green flags
   ├─ Risk score
   ├─ Breakdown de pricing
   └─ Cálculo USD→BRL
   ↓
4. Tomar Decisão
   ├─ Aceitar
   ├─ Negociar (gera proposta)
   └─ Rejeitar
   ↓
5. Sistema Aprende
   ├─ Pricing accuracy
   ├─ Rejection patterns
   └─ Hourly rate optimization
```

---

## 🧪 Teste Rápido

### **Via Frontend** (recomendado)
1. Acesse: http://localhost:5173/freelancer/opportunities
2. Click "Nova Oportunidade"
3. Preencha e salve
4. Click "Analisar"
5. Click "Ver Detalhes"

### **Via Postman**
1. Abra Postman
2. Import: `backend/postman_collection_freelancer.json`
3. Import: `backend/postman_environment_local.json`
4. Selecione environment "Charlee - Local Development"
5. Rode: **0. Authentication → Login**
6. Teste endpoints

### **Via Swagger UI**
1. Acesse: http://localhost:8000/docs
2. Expand endpoint
3. Click "Try it out"
4. Execute

---

## 🐛 Troubleshooting Rápido

### **Backend não inicia**
```bash
# Verifique PostgreSQL
docker ps | grep postgres

# Se não estiver, inicie
docker start charlee-postgres-pgvector

# Verifique Redis
docker ps | grep redis

# Se não estiver, inicie
docker start charlee-redis
```

### **Frontend não conecta**
```bash
# Verifique se backend está rodando
curl http://localhost:8000/health

# Deve retornar: {"status":"healthy",...}
```

### **Erro de extensão pgvector**
```bash
docker exec charlee-postgres-pgvector psql -U charlee -d charlee_db -c "CREATE EXTENSION vector;"
```

---

## 📚 Documentação Completa

- **Frontend Guide**: [interfaces/web/FREELANCER_FRONTEND_GUIDE.md](interfaces/web/FREELANCER_FRONTEND_GUIDE.md)
- **Backend Setup**: [QUICK_START.md](QUICK_START.md)
- **Postman Guide**: [backend/POSTMAN_GUIDE.md](backend/POSTMAN_GUIDE.md)
- **Testing Guide**: [backend/TESTING_FREELANCER.md](backend/TESTING_FREELANCER.md)
- **Implementação**: [docs/implementacao/freelancer-mvp.md](docs/implementacao/freelancer-mvp.md)

---

## 🎉 Pronto!

Agora você tem:
- ✅ Backend rodando com API completa
- ✅ Frontend moderno e responsivo
- ✅ Sistema de análise automática
- ✅ Learning components funcionando
- ✅ Analytics com insights de carreira

**Comece a adicionar oportunidades reais e deixe o sistema te ajudar a tomar decisões melhores!** 🚀
