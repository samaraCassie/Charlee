# 🚀 Quick Start - Celery Auto-Collection

Guia rápido para iniciar o monitoramento automático de oportunidades de freelance.

## 1️⃣ Instalar Dependências

```bash
# Instalar Redis
sudo apt-get install redis-server

# Instalar pacotes Python
cd backend
pip install -r requirements.txt
```

## 2️⃣ Configurar Plataformas

Adicione suas plataformas via API ou diretamente no banco:

```python
from database.session import SessionLocal
from database.models import FreelancePlatform

db = SessionLocal()

# Exemplo: Configurar Upwork
platform = FreelancePlatform(
    user_id=1,
    name="Upwork",
    active=True,
    auto_collect=True,
    collection_interval_minutes=30,  # Coletar a cada 30 min
    api_config={
        "api_key": "sua_api_key",
        "api_secret": "seu_api_secret"
    }
)
db.add(platform)
db.commit()
```

## 3️⃣ Iniciar Celery (3 terminais)

**Terminal 1 - Worker:**
```bash
cd backend
./scripts/start_celery_worker.sh
```

**Terminal 2 - Beat Scheduler:**
```bash
cd backend
./scripts/start_celery_beat.sh
```

**Terminal 3 - Flower (Opcional):**
```bash
cd backend
./scripts/start_flower.sh
# Acesse: http://localhost:5555
```

## 4️⃣ Verificar Funcionamento

```bash
cd backend
python scripts/test_celery.py
```

## ✅ Pronto!

O sistema agora coleta oportunidades automaticamente a cada 15 minutos!

### Verificar Logs

```bash
# Ver oportunidades coletadas
tail -f logs/celery-worker.log

# Verificar schedule
celery -A celery_app inspect scheduled
```

### Coletar Manualmente (teste)

```python
from tasks.opportunity_collector import collect_all_opportunities

# Executar agora
result = collect_all_opportunities.delay()
print(result.get())
```

## 📚 Documentação Completa

Veja [docs/CELERY_SETUP.md](docs/CELERY_SETUP.md) para mais detalhes.
