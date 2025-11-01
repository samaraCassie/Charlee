# Charlee Backend - Quickstart

## 🚀 Início Rápido

### 1. Configurar Ambiente

```bash
# Voltar para o diretório raiz
cd /home/sam-cassie/GitHub/Charlee

# Copiar .env.example
cp backend/.env.example .env

# Editar .env com suas credenciais
nano .env
```

**Variáveis importantes:**
- `DATABASE_URL`: Conexão com PostgreSQL
- `ANTHROPIC_API_KEY`: Sua chave da API Anthropic

### 2. Iniciar com Docker

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Status dos serviços
docker-compose ps
```

### 3. Testar o Backend

```bash
# Entrar no container
docker-compose exec backend bash

# Rodar testes
python test_setup.py

# Sair
exit
```

### 4. Acessar a API

Abra no navegador:
- **Documentação Interativa**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Endpoints Principais

### Big Rocks
- `GET /api/v1/big-rocks` - Listar Big Rocks
- `POST /api/v1/big-rocks` - Criar Big Rock
- `GET /api/v1/big-rocks/{id}` - Ver Big Rock
- `PATCH /api/v1/big-rocks/{id}` - Atualizar Big Rock
- `DELETE /api/v1/big-rocks/{id}` - Deletar Big Rock

### Tarefas
- `GET /api/v1/tarefas` - Listar tarefas
- `POST /api/v1/tarefas` - Criar tarefa
- `GET /api/v1/tarefas/{id}` - Ver tarefa
- `PATCH /api/v1/tarefas/{id}` - Atualizar tarefa
- `POST /api/v1/tarefas/{id}/concluir` - Marcar como concluída
- `POST /api/v1/tarefas/{id}/reabrir` - Reabrir tarefa
- `DELETE /api/v1/tarefas/{id}` - Deletar tarefa

### Agent (Charlee)
- `POST /api/v1/agent/chat` - Conversar com Charlee
- `GET /api/v1/agent/tools` - Ver ferramentas disponíveis

## 💬 Exemplos de Uso

### Criar um Big Rock

```bash
curl -X POST "http://localhost:8000/api/v1/big-rocks" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Syssa - Estágio",
    "cor": "#4CAF50"
  }'
```

### Criar uma Tarefa

```bash
curl -X POST "http://localhost:8000/api/v1/tarefas" \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Apresentação Janeiro",
    "big_rock_id": 1,
    "deadline": "2025-01-31",
    "tipo": "Tarefa"
  }'
```

### Conversar com Charlee

```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Liste minhas tarefas pendentes"
  }'
```

## 🔧 Comandos Úteis

```bash
# Ver logs do backend
docker-compose logs -f backend

# Reiniciar backend
docker-compose restart backend

# Parar todos os serviços
docker-compose down

# Parar e limpar volumes (⚠️ deleta dados)
docker-compose down -v

# Reconstruir imagens
docker-compose build

# Executar migrations (quando implementado)
docker-compose exec backend alembic upgrade head
```

## 🐛 Troubleshooting

### Erro de conexão com banco de dados
```bash
# Verificar se o PostgreSQL está rodando
docker-compose ps postgres

# Ver logs do PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

### Erro "Module not found"
```bash
# Reconstruir a imagem
docker-compose build backend

# Reiniciar
docker-compose up -d backend
```

### Atualizar dependências
```bash
# Editar backend/requirements.txt

# Reconstruir
docker-compose build backend
docker-compose up -d backend
```

## 📖 Próximos Passos

1. ✅ Backend V1 completo
2. 🔄 Criar interface CLI
3. 🔄 Implementar migrations com Alembic
4. 🔄 Adicionar testes unitários
5. 🔄 Implementar agentes especializados (V2)

## 🆘 Suporte

Para problemas, verifique:
1. Logs: `docker-compose logs backend`
2. Documentação interativa: http://localhost:8000/docs
3. Arquivo de configuração: `.env`
