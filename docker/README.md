# Docker Configuration

Arquivos de configuração Docker para o sistema Charlee.

## Estrutura

- `docker-compose.yml`: Orquestração de todos os serviços
- `.env`: Variáveis de ambiente (não versionado)

## Serviços

### PostgreSQL + pgvector
- **Porta**: 5432
- **Database**: charlee_db
- **Volume**: postgres_data (persistente)

### Redis
- **Porta**: 6379
- **Volume**: redis_data (persistente)
- **Uso**: Sessões e memórias do agente

### Backend (FastAPI)
- **Porta**: 8000
- **Hot-reload**: Ativado para desenvolvimento
- **Volumes**: Backend e shared montados

## Comandos Úteis

### Iniciar serviços
```bash
cd docker
docker-compose up -d
```

### Ver logs
```bash
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f postgres
```

### Parar serviços
```bash
docker-compose down
```

### Rebuild após mudanças
```bash
docker-compose build backend
docker-compose up -d
```

### Limpar tudo (incluindo volumes)
```bash
docker-compose down -v
```

## Configuração do .env

Crie um arquivo `.env` nesta pasta com:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Database
DATABASE_URL=postgresql://charlee:charlee123@postgres:5432/charlee_db

# Redis
REDIS_URL=redis://redis:6379

# App
DEBUG=true
LOG_LEVEL=INFO
```

## Health Checks

- PostgreSQL: `pg_isready -U charlee`
- Redis: Automático (condition: service_started)
- Backend: Disponível em http://localhost:8000/docs
