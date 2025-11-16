# Celery Background Tasks - Setup Guide

Este guia explica como configurar e usar o Celery para tarefas em background no Charlee, incluindo a coleta automática de oportunidades de freelance.

## 📋 Visão Geral

O Celery é usado para executar tarefas assíncronas e periódicas:
- **Auto-coleta de oportunidades**: Monitora plataformas de freelance a cada 15 minutos
- **Análise de dados**: Processamento de insights em background
- **Notificações**: Alertas e lembretes programados

## 🔧 Requisitos

1. **Redis**: Message broker e result backend
2. **Python dependencies**: Celery e Flower (já em requirements.txt)

### Instalar Redis (se ainda não tiver)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Instalar dependências Python

```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Executando o Celery

Você precisa rodar **3 processos separados** (em terminais diferentes):

### 1. Worker (Processa tarefas)

```bash
cd backend
./scripts/start_celery_worker.sh
```

Ou manualmente:
```bash
celery -A celery_app worker --loglevel=info --concurrency=4
```

### 2. Beat Scheduler (Agenda tarefas periódicas)

```bash
cd backend
./scripts/start_celery_beat.sh
```

Ou manualmente:
```bash
celery -A celery_app beat --loglevel=info
```

### 3. Flower (Monitoramento - Opcional)

```bash
cd backend
./scripts/start_flower.sh
```

Ou manualmente:
```bash
celery -A celery_app flower --port=5555
```

Acesse: http://localhost:5555

## 📅 Tarefas Configuradas

### Coleta Automática de Oportunidades

**Frequência:** A cada 15 minutos
**Task:** `tasks.opportunity_collector.collect_all_opportunities`

Esta task:
1. Verifica todas as plataformas ativas com `auto_collect=True`
2. Respeita o `collection_interval_minutes` de cada plataforma
3. Coleta novas oportunidades
4. Armazena no banco de dados
5. Atualiza `last_collection_at`

### Tarefas Disponíveis

```python
# Coletar de todas as plataformas (executado automaticamente)
from tasks.opportunity_collector import collect_all_opportunities
result = collect_all_opportunities.delay()

# Coletar para um usuário específico
from tasks.opportunity_collector import collect_user_opportunities
result = collect_user_opportunities.delay(user_id=1)

# Coletar de uma plataforma específica
from tasks.opportunity_collector import collect_platform_opportunities
result = collect_platform_opportunities.delay(platform_id=1)
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# .env
REDIS_URL=redis://localhost:6379/0
```

### Ajustar Frequência de Coleta

Edite `backend/celery_app.py`:

```python
beat_schedule={
    "collect-opportunities-every-15-minutes": {
        "task": "tasks.opportunity_collector.collect_all_opportunities",
        "schedule": crontab(minute="*/15"),  # Altere aqui
    },
}
```

**Exemplos de schedules:**
```python
crontab(minute="*/5")           # A cada 5 minutos
crontab(minute=0, hour="*/1")   # A cada hora
crontab(hour=9, minute=0)       # Às 9:00 todos os dias
crontab(day_of_week=1, hour=9)  # Segundas às 9:00
```

### Configurar Intervalo por Plataforma

Via API ou banco de dados:

```python
# Configurar plataforma para coletar a cada 30 minutos
platform.collection_interval_minutes = 30
platform.auto_collect = True
db.commit()
```

## 🔍 Monitoramento

### Via Flower (Recomendado)

1. Acesse: http://localhost:5555
2. Veja tasks em execução, histórico, estatísticas
3. Monitore workers e performance

### Via Logs

```bash
# Worker logs
tail -f celery-worker.log

# Beat logs
tail -f celery-beat.log
```

### Via Código

```python
from celery.result import AsyncResult

# Verificar status de uma task
result = AsyncResult(task_id)
print(result.state)      # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)     # Resultado da task
print(result.traceback)  # Se falhou
```

## 🐳 Docker (Produção)

### docker-compose.yml

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - redis
      - db
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@db:5432/charlee
    volumes:
      - ./backend:/app

  celery_beat:
    build: ./backend
    command: celery -A celery_app beat --loglevel=info
    depends_on:
      - redis
      - db
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@db:5432/charlee
    volumes:
      - ./backend:/app

  flower:
    build: ./backend
    command: celery -A celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis_data:
```

## 🧪 Testar Manualmente

```python
# backend/test_celery.py
from tasks.opportunity_collector import collect_all_opportunities

# Testar task síncronamente (sem Celery)
result = collect_all_opportunities()
print(result)

# Testar task assíncronamente (com Celery)
task = collect_all_opportunities.delay()
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")

# Aguardar resultado
result = task.get(timeout=60)
print(result)
```

## 🚨 Troubleshooting

### "Connection refused" ao conectar no Redis

```bash
# Verificar se Redis está rodando
redis-cli ping
# Deve retornar: PONG

# Se não estiver rodando
sudo systemctl start redis
```

### Tasks não executam

1. Verificar se Worker está rodando
2. Verificar se Beat está rodando
3. Verificar logs: `celery -A celery_app inspect active`

### Tasks executam mas dão erro

1. Verificar logs do worker
2. Verificar conexão com banco de dados
3. Verificar credenciais das plataformas

### Flower não abre

```bash
# Verificar se porta está em uso
lsof -i :5555

# Matar processo
kill -9 <PID>
```

## 📊 Boas Práticas

1. **Use rate limiting** para APIs externas
2. **Configure retries** para tasks que podem falhar
3. **Monitore via Flower** em produção
4. **Configure alertas** para tasks críticas
5. **Limite concurrency** para não sobrecarregar o sistema
6. **Use dead letter queue** para tasks que falharam muito

## 📚 Recursos

- [Celery Documentation](https://docs.celeryq.dev/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
