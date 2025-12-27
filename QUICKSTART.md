# ⚡ Quick Start - Charlee

Setup rápido em 3 comandos!

## 🚀 Setup Automático (Recomendado)

```bash
# 1. Clone e entre no diretório
git clone https://github.com/sam-cassie/Charlee.git
cd Charlee

# 2. Configure .env com sua OpenAI API key
nano docker/.env
# Adicione: OPENAI_API_KEY=sk-sua-key-aqui

# 3. Execute o setup automático
./scripts/setup_complete.sh
```

Pronto! Acesse:
- **API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (se configurado)

---

## 🛠️ Setup Manual

Se preferir fazer manualmente:

```bash
# 1. Configure .env
cp docker/.env.example docker/.env
nano docker/.env  # Adicione sua OPENAI_API_KEY

# 2. Inicie containers
cd docker
docker-compose up -d

# 3. Execute migrations
docker exec -it charlee_backend alembic upgrade head
```

---

## ✅ Verificação Rápida

### Teste o backend
```bash
curl http://localhost:8000/api/v1/settings/system
```

Deve retornar JSON com uptime, versão, etc.

### Teste criação de usuário
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### Faça login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test123"
  }'
```

Copie o `access_token` retornado.

### Teste backup
```bash
curl -X POST http://localhost:8000/api/v1/settings/backup \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🔧 Troubleshooting

### Containers não iniciam
```bash
docker-compose down
docker-compose up -d
docker logs charlee_backend
```

### Migrations falham
```bash
docker exec -it charlee_backend alembic current
docker exec -it charlee_backend alembic upgrade head
```

### pgvector não instalado
```bash
docker exec -it charlee_db psql -U charlee -d charlee_db \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## 📚 Documentação Completa

Para setup detalhado e troubleshooting avançado, veja:
- **[SETUP.md](SETUP.md)** - Guia completo com todos os detalhes
- **[README.md](README.md)** - Visão geral do projeto
- **[docs/](docs/)** - Documentação de features por versão

---

## 🎯 Próximos Passos

1. ✅ Explorar API em http://localhost:8000/docs
2. ✅ Criar Big Rocks e Tasks
3. ✅ (Opcional) Configurar Google/Microsoft Calendar
4. ✅ (Opcional) Testar upload de voz/imagem

---

**Versão:** 3.3.0  
**Última atualização:** 2024-12-24
