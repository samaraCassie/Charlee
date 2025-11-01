# Charlee - Sistema de Inteligência Pessoal

Charlee é um sistema de inteligência pessoal que funciona como seu segundo cérebro, combinando gestão de tarefas, bem-estar, automações e inteligência artificial.

## Estrutura do Projeto

```
Charlee/
├── backend/                    # Backend (Python + FastAPI + Agno)
│   ├── agent/                  # Agentes de IA
│   ├── api/                    # API REST
│   ├── database/               # Models e migrations
│   ├── integrations/           # Integrações externas
│   ├── multimodal/             # Processamento voz/imagem
│   └── automation/             # Automações
│
├── interfaces/                 # Interfaces do usuário
│   ├── cli/                    # CLI (V1)
│   └── web/                    # Dashboard web (futuro)
│
├── shared/                     # Código compartilhado
│   ├── types/                  # Tipos
│   └── utils/                  # Utilitários
│
├── docker-compose.yml          # Orquestração
└── .env                        # Variáveis de ambiente
```

## Requisitos

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL com pgvector
- OpenAI API Key

## Instalação Rápida

1. Clone o repositório:
```bash
git clone <repo-url>
cd Charlee
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

3. Inicie os serviços:
```bash
docker-compose up -d
```

## Desenvolvimento

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### CLI
```bash
cd interfaces/cli
pip install -r requirements.txt
python main.py
```

## Roadmap

- **V1 (Atual)**: MVP com gestão de tarefas + Big Rocks + CLI
- **V2**: Inteligência de capacidade e tracking de ciclo menstrual
- **V3**: Multimodal (voz e imagem) + Integrações
- **V4**: Automações e gerenciamento de comunicações
- **V5**: Inteligência completa e conselheiro estratégico

## Documentação

Veja [Charlee_Documentacao.docx.txt](./Charlee_Documentacao.docx.txt) para detalhes completos da arquitetura e visão do projeto.

## Licença

Privado - Uso pessoal
