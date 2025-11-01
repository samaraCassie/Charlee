# Charlee Backend

Backend do sistema de inteligência pessoal Charlee.

## Estrutura

```
backend/
├── agent/                  # Agentes Agno
│   ├── specialized_agents/ # Agentes especializados
│   └── memory/            # Sistema de memória
├── integrations/          # Integrações externas
├── multimodal/            # Processamento de voz/imagem
├── automation/            # Automações
├── database/              # Models e migrations
│   └── migrations/        # Alembic migrations
├── api/                   # FastAPI
│   └── routes/           # Rotas da API
└── skills/               # Agno Skills customizadas

## Instalação

```bash
cd backend
pip install -r requirements.txt
```

## Desenvolvimento

```bash
uvicorn api.main:app --reload
```
