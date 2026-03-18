# 🚀 Setup para Uso Real - Sistema Freelancer

Este guia te leva do zero até o sistema funcionando **de verdade** em 5-10 minutos.

---

## ✅ **Pré-requisitos**

- [ ] Docker instalado
- [ ] Python 3.10+ instalado
- [ ] Git clone do projeto já feito

---

## 📋 **Setup Completo (5 Passos)**

### **Passo 1: Inicie PostgreSQL e Redis**

```bash
# Opção A: Containers já existem, apenas inicie
docker start charlee-postgres charlee_redis

# Opção B: Se não existirem, crie novos
docker run -d \
  --name charlee-postgres \
  -e POSTGRES_PASSWORD=charlee123 \
  -e POSTGRES_USER=charlee \
  -e POSTGRES_DB=charlee \
  -p 5432:5432 \
  postgres:15

docker run -d \
  --name charlee-redis \
  -p 6379:6379 \
  redis:7-alpine

# Verifique se estão rodando
docker ps | grep -E "(postgres|redis)"
```

**Resultado esperado:**
```
charlee-postgres   Up 2 seconds   0.0.0.0:5432->5432/tcp
charlee_redis      Up 2 seconds   0.0.0.0:6379->6379/tcp
```

---

### **Passo 2: Crie Virtual Environment e Instale Dependências**

```bash
# Navegue para o backend
cd /home/sam-cassie/GitHub/Charlee/backend

# Crie virtual environment
python3 -m venv venv

# Ative o virtual environment
source venv/bin/activate

# Atualize pip
pip install --upgrade pip

# Instale dependências
pip install -r requirements.txt

# Verifique instalação
python -c "import fastapi, sqlalchemy, redis; print('✓ Dependencies OK')"
```

**Resultado esperado:**
```
✓ Dependencies OK
```

---

### **Passo 3: Configure Variáveis de Ambiente**

```bash
# Crie arquivo .env no backend
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://charlee:charlee123@localhost:5432/charlee
POSTGRES_USER=charlee
POSTGRES_PASSWORD=charlee123
POSTGRES_DB=charlee

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ENCRYPTION_KEY=generate-with-python-cryptography-fernet

# API Keys (opcional para testes)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Environment
ENVIRONMENT=development
DEBUG=true
EOF

echo "✓ .env created"
```

**Gere encryption key:**
```bash
python3 << 'EOF'
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f"\nAdicione ao .env:")
print(f"ENCRYPTION_KEY={key.decode()}")
EOF
```

Copie a chave gerada e adicione ao `.env`.

---

### **Passo 4: Rode as Migrações do Banco**

```bash
# Certifique-se que está no backend com venv ativado
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate

# Rode migrações (cria todas as tabelas)
python -m alembic upgrade head

# Ou se não tiver alembic, use o script de init
python scripts/init_db.py
```

**Resultado esperado:**
```
INFO  [alembic.runtime.migration] Running upgrade -> xxxxx, create users table
INFO  [alembic.runtime.migration] Running upgrade xxxxx -> yyyyy, create opportunities table
...
✓ Database initialized successfully
```

---

### **Passo 5: Inicie o Backend**

```bash
# Ainda no backend com venv ativado
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

🎉 **Backend rodando!** Acesse: http://localhost:8000/docs

---

## 🧪 **Teste Rápido (Smoke Test)**

### **No navegador:**

1. Abra: http://localhost:8000/docs
2. Você deve ver a interface Swagger UI
3. Click em **Health Check** → **Try it out** → **Execute**
4. Deve retornar: `{"status": "healthy"}`

### **Via cURL (Terminal 2):**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar: {"status":"healthy","database":"connected","redis":"connected"}
```

---

## 📮 **Usando via Postman (Recomendado)**

Agora que o backend está rodando, use Postman para testes:

```bash
# 1. Abra Postman
# 2. Import → Arraste este arquivo:
#    /home/sam-cassie/GitHub/Charlee/backend/postman_collection_freelancer.json
# 3. Import → Arraste este arquivo:
#    /home/sam-cassie/GitHub/Charlee/backend/postman_environment_local.json
# 4. Selecione environment: "Charlee - Local Development"
# 5. Rode request: "Login" (token será salvo automaticamente)
# 6. Comece a testar!
```

**Veja guia completo:** [backend/POSTMAN_GUIDE.md](backend/POSTMAN_GUIDE.md)

---

## 🎯 **Primeiros Passos de Uso Real**

### **1. Crie seu usuário**

**Via Postman:**
- Rode request: **0. Authentication → Register** (se disponível)

**Via Python (se não tiver endpoint de registro):**
```bash
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python << 'EOF'
from database.connection import SessionLocal
from database.models import User
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user = User(
    email="seu_email@example.com",
    username="seu_username",
    full_name="Seu Nome",
    hashed_password=pwd_context.hash("sua_senha_segura"),
    is_active=True
)

db.add(user)
db.commit()
db.refresh(user)

print(f"✓ User created: {user.email} (ID: {user.id})")
db.close()
EOF
```

### **2. Configure seus parâmetros de precificação**

```python
from database.connection import SessionLocal
from database.models import PricingParameter

db = SessionLocal()

params = PricingParameter(
    user_id=1,  # Seu user_id
    version=1,
    base_hourly_rate=100.0,  # Sua taxa horária base (USD)
    minimum_margin=0.20,  # Margem mínima 20%
    currency="USD",
    complexity_factors={
        "1-2": 1.0,    # Projetos simples
        "3-4": 1.2,    # +20%
        "5-6": 1.4,    # +40%
        "7-8": 1.8,    # +80%
        "9-10": 2.5,   # +150%
    },
    specialization_factors={
        "ai_ml": 1.5,       # +50% para AI/ML
        "blockchain": 1.4,   # +40%
        "full_stack": 1.2,   # +20%
        "backend": 1.1,      # +10%
        "frontend": 1.0,     # Base
        "devops": 1.3,       # +30%
        "mobile": 1.2,       # +20%
        "data": 1.4,         # +40%
    },
    deadline_factors={
        "urgent": 1.5,   # <1 semana: +50%
        "short": 1.3,    # 1-2 semanas: +30%
        "normal": 1.0,   # 2-4 semanas: base
        "long": 0.9,     # >4 semanas: -10%
    },
    client_factors={
        "new": 1.2,      # Cliente novo: +20% (risco)
        "verified": 1.0, # Cliente verificado: base
        "premium": 0.95, # Cliente premium: -5% (volume)
    },
    minimum_project_value=500.0,  # Valor mínimo USD
    minimum_deadline_days=7,      # Prazo mínimo 7 dias
    active=True
)

db.add(params)
db.commit()
db.refresh(params)

print(f"✓ Pricing parameters created (ID: {params.id}, Version: {params.version})")
print(f"  Base rate: ${params.base_hourly_rate}/hr")
db.close()
```

### **3. Configure plataformas freelance**

```python
from database.connection import SessionLocal
from database.models import FreelancePlatform

db = SessionLocal()

# Upwork
upwork = FreelancePlatform(
    user_id=1,
    name="upwork",
    api_key="your-upwork-api-key",  # Opcional
    api_secret="your-upwork-secret",
    is_active=True
)

# Freelancer.com
freelancer = FreelancePlatform(
    user_id=1,
    name="freelancer",
    api_key="your-freelancer-api-key",  # Opcional
    api_secret="your-freelancer-secret",
    is_active=True
)

db.add_all([upwork, freelancer])
db.commit()

print("✓ Platforms configured: Upwork, Freelancer.com")
db.close()
```

### **4. Adicione sua primeira oportunidade real**

**Via Postman:**
1. Rode request: **1. RN09 - Duplication Prevention → Create Opportunity #1**
2. Edite o body com dados reais do projeto

**Via Python:**
```python
from database.connection import SessionLocal
from database.models import FreelanceOpportunity

db = SessionLocal()

opportunity = FreelanceOpportunity(
    user_id=1,
    platform_id=1,  # Upwork
    external_id="upwork_12345",
    title="Python Backend Developer - E-commerce API",
    description="""
    Looking for experienced Python developer to build RESTful API for e-commerce platform.

    Requirements:
    - FastAPI or Django REST Framework
    - PostgreSQL database design
    - Payment gateway integration (Stripe)
    - 3 months timeline
    - Remote work

    Budget: $8,000 - $12,000
    """,
    client_budget=10000.0,
    client_rating=4.7,
    client_projects_count=30,
    client_payment_verified=True,
    client_country="United States",
    estimated_hours=150,
    skills_required=["Python", "FastAPI", "PostgreSQL", "Stripe", "Docker"],
    status="pending"
)

db.add(opportunity)
db.commit()
db.refresh(opportunity)

print(f"✓ Opportunity created: {opportunity.title} (ID: {opportunity.id})")
db.close()
```

### **5. Processe a oportunidade (Pipeline Completo)**

**Via Postman:**
- Rode request: **7. Integration Service → Process Opportunity (Full Pipeline)**
- Veja análise completa: duplicação, risco, cálculo financeiro, etc.

**Resultado esperado:**
```json
{
  "opportunity_id": 1,
  "is_duplicate": false,
  "risk_assessment": {
    "risk_score": 2.5,
    "risk_level": "low",
    "recommendation": "accept",
    "red_flags": [],
    "green_flags": ["verified_payment", "experienced_client"]
  },
  "suggested_pricing": {
    "suggested_hourly_rate": 132.0,
    "suggested_value": 19800.0,
    "breakdown": {
      "base_rate": 100.0,
      "complexity_multiplier": 1.4,
      "specialization_multiplier": 1.0,
      "deadline_multiplier": 1.0,
      "client_multiplier": 1.0
    }
  },
  "financial_calculation": {
    "gross_usd": 10000.0,
    "net_brl": 48300.0,
    "effective_tax_rate": 0.16
  }
}
```

---

## 🔄 **Workflow Real de Uso**

### **Diariamente:**

1. **Colete oportunidades** (manual ou via script)
   - Via Postman: Create Opportunity
   - Via bookmarklet (quando implementado)
   - Via integração com API da plataforma

2. **Analise automaticamente**
   - Rode Integration Service → Process Opportunity
   - Sistema detecta duplicatas, avalia risco, calcula preço

3. **Tome decisão**
   - `recommendation: "accept"` → Candidate-se
   - `recommendation: "negotiate"` → Negocie preço/escopo
   - `recommendation: "reject"` → Ignore

4. **Negocie (se necessário)**
   - Use Negotiation Engine para gerar contra-proposta
   - Sistema sugere mensagem diplomática

5. **Acompanhe projetos aceitos**
   - Marque status como "accepted"
   - Sistema aprende com outcomes

### **Semanalmente:**

1. **Analise learning components**
   - Pricing Performance (accuracy de precificação)
   - Rejection Patterns (red flags que importam)
   - Hourly Rate Optimization (taxa ideal)

2. **Ajuste parâmetros** (se necessário)
   - Apply Pricing Adjustment (se accuracy < 75%)
   - Apply Rate Adjustment (se acceptance rate desbalanceado)

### **Mensalmente:**

1. **Análise de carreira**
   - Career Insights (revenue, skills progression)
   - Top Performing Projects
   - Income Trends

2. **Otimize estratégia**
   - Identifique high-value skills
   - Ajuste pricing por categoria
   - Refine red flag weights

---

## 🛠️ **Comandos Úteis**

### **Iniciar tudo:**
```bash
# Terminal 1: Containers
docker start charlee-postgres charlee_redis

# Terminal 2: Backend
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
uvicorn main:app --reload
```

### **Parar tudo:**
```bash
# Ctrl+C no terminal do uvicorn

# Parar containers
docker stop charlee-postgres charlee_redis
```

### **Ver logs:**
```bash
# Backend: já aparece no terminal do uvicorn

# PostgreSQL logs
docker logs charlee-postgres -f

# Redis logs
docker logs charlee_redis -f
```

### **Acessar banco diretamente:**
```bash
docker exec -it charlee-postgres psql -U charlee -d charlee

# No psql:
\dt  # Listar tabelas
SELECT * FROM freelance_opportunities LIMIT 5;
\q   # Sair
```

### **Limpar dados de teste:**
```bash
docker exec -it charlee-postgres psql -U charlee -d charlee -c "TRUNCATE TABLE freelance_opportunities CASCADE;"
```

---

## 🐛 **Troubleshooting**

### **Erro: "Connection refused" (PostgreSQL)**
```bash
# Verifique se container está rodando
docker ps | grep postgres

# Se não estiver, inicie
docker start charlee-postgres

# Verifique logs
docker logs charlee-postgres
```

### **Erro: "ENCRYPTION_KEY not set"**
```bash
# Gere nova chave
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Adicione ao .env
echo "ENCRYPTION_KEY=<chave-gerada>" >> .env
```

### **Erro: "Table doesn't exist"**
```bash
# Rode migrações
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python -m alembic upgrade head
```

### **Erro: "No module named 'fastapi'"**
```bash
# Ative virtual environment
source venv/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

---

## 📚 **Próximos Passos**

Depois que tudo estiver funcionando:

1. ✅ **Leia guia Postman:** [backend/POSTMAN_GUIDE.md](backend/POSTMAN_GUIDE.md)
2. ✅ **Explore Swagger UI:** http://localhost:8000/docs
3. ✅ **Configure integrações** com Upwork/Freelancer APIs (opcional)
4. ✅ **Customize parâmetros** de precificação e risk assessment
5. ✅ **Automatize coleta** de oportunidades (cron job + Collector Agent)

---

## 🎉 **Pronto!**

Agora você tem o sistema freelancer **rodando de verdade** e pode:

- ✅ Adicionar oportunidades reais
- ✅ Avaliar risco de clientes
- ✅ Calcular preços automaticamente
- ✅ Gerar contra-propostas inteligentes
- ✅ Aprender com projetos executados
- ✅ Otimizar taxa horária
- ✅ Acompanhar métricas de carreira

**Boa sorte nos projetos!** 🚀
