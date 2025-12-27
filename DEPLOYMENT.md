# 🚀 Deployment Guide - Charlee Production

Guia completo para deploy do Charlee em produção (VPS/Cloud).

## 📋 Pré-requisitos

- **Servidor Linux** (Ubuntu 22.04 LTS recomendado)
- **Domain** configurado apontando para o servidor
- **Acesso SSH** com sudo privileges
- **Mínimo:** 2 CPU cores, 4GB RAM, 20GB storage
- **Recomendado:** 4 CPU cores, 8GB RAM, 40GB storage

---

## 🛠️ Setup do Servidor

### 1. Atualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Docker e Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Verificar instalação
docker --version
docker compose version
```

### 3. Instalar Nginx (Reverse Proxy)

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 4. Instalar Certbot (SSL/TLS)

```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

## 📦 Deploy da Aplicação

### 1. Clonar Repositório

```bash
cd /opt
sudo git clone https://github.com/samaraCassie/Charlee.git
sudo chown -R $USER:$USER /opt/Charlee
cd Charlee
```

### 2. Configurar Environment Variables

```bash
# Copiar template
cp docker/.env.example docker/.env

# Editar com valores de produção
nano docker/.env
```

**Variáveis CRÍTICAS para produção:**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database (usar senha forte!)
POSTGRES_USER=charlee_prod
POSTGRES_PASSWORD=<SENHA_FORTE_AQUI>
POSTGRES_DB=charlee_production

# Security
JWT_SECRET_KEY=<GERAR_CHAVE_SEGURA_64_CHARS>
JWT_REFRESH_SECRET_KEY=<GERAR_CHAVE_SEGURA_64_CHARS>

# OpenAI (obrigatório)
OPENAI_API_KEY=sk-...

# Frontend URL (seu domínio)
FRONTEND_URL=https://charlee.seudominio.com

# Redis
REDIS_URL=redis://redis:6379/0

# Calendar (opcional)
GOOGLE_CALENDAR_CLIENT_ID=...
GOOGLE_CALENDAR_CLIENT_SECRET=...
GOOGLE_CALENDAR_REDIRECT_URI=https://charlee.seudominio.com/calendar/callback/google

MICROSOFT_CALENDAR_CLIENT_ID=...
MICROSOFT_CALENDAR_CLIENT_SECRET=...
MICROSOFT_CALENDAR_REDIRECT_URI=https://charlee.seudominio.com/calendar/callback/microsoft
```

**Gerar chaves seguras:**
```bash
# Gerar JWT secrets (64 caracteres aleatórios)
openssl rand -hex 32
openssl rand -hex 32
```

### 3. Configurar Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/charlee
```

**Configuração Nginx:**

```nginx
# Backend API
server {
    listen 80;
    server_name api.seudominio.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts para requests longos
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support para notificações
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_read_timeout 86400;
    }
}

# Frontend (se houver)
server {
    listen 80;
    server_name charlee.seudominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Ativar configuração:**

```bash
sudo ln -s /etc/nginx/sites-available/charlee /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Configurar SSL/TLS com Certbot

```bash
# Obter certificados SSL (substitua pelos seus domínios)
sudo certbot --nginx -d api.seudominio.com -d charlee.seudominio.com

# Renovação automática já está configurada
sudo certbot renew --dry-run
```

### 5. Build e Start dos Containers

```bash
cd /opt/Charlee/docker

# Build das imagens
docker compose build

# Iniciar serviços
docker compose up -d

# Verificar status
docker compose ps
```

### 6. Executar Migrations

```bash
# Entrar no container do backend
docker compose exec backend bash

# Rodar migrations
alembic upgrade head

# Verificar versão atual
alembic current

# Sair do container
exit
```

### 7. Criar Primeiro Usuário Admin

```bash
# Via container
docker compose exec backend python -c "
from database.config import SessionLocal
from database.models import User
from api.auth.password import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@seudominio.com',
    hashed_password=get_password_hash('SENHA_ADMIN_AQUI'),
    full_name='Admin User',
    is_active=True,
    is_superuser=True,
    role='admin'
)
db.add(admin)
db.commit()
print('✅ Admin user created')
db.close()
"
```

---

## 🔍 Verificação de Deploy

### 1. Health Check

```bash
curl https://api.seudominio.com/health
```

**Esperado:**
```json
{
  "service": "charlee-backend",
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "celery": {"status": "healthy"},
    "migrations": {"status": "healthy", "version": "012_add_user_role"}
  }
}
```

### 2. Verificar Logs

```bash
# Backend logs
docker compose logs backend --tail=50 --follow

# Celery worker logs
docker compose logs celery_worker --tail=50 --follow

# Todos os logs
docker compose logs --tail=100
```

### 3. Verificar Serviços

```bash
# Status dos containers
docker compose ps

# Uso de recursos
docker stats

# Verificar portas
sudo netstat -tulpn | grep -E ':(8000|3000|5432|6379)'
```

---

## 🔒 Segurança Pós-Deploy

### 1. Firewall (UFW)

```bash
# Permitir apenas SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Verificar status
sudo ufw status
```

### 2. Fail2Ban (Proteção contra Brute Force)

```bash
sudo apt install fail2ban -y

# Configurar
sudo nano /etc/fail2ban/jail.local
```

**Configuração básica:**
```ini
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Configurar Backups Automáticos

```bash
# Criar script de backup
sudo nano /opt/backup-charlee.sh
```

**Script:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/charlee"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco de dados
docker compose exec -T postgres pg_dump -U charlee_prod charlee_production | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup de arquivos de configuração
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /opt/Charlee/docker/.env

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
```

```bash
# Tornar executável
sudo chmod +x /opt/backup-charlee.sh

# Agendar no crontab (todo dia às 2h)
sudo crontab -e
```

Adicionar linha:
```cron
0 2 * * * /opt/backup-charlee.sh >> /var/log/charlee-backup.log 2>&1
```

---

## 📊 Monitoring

### 1. Setup Monitoring Básico

```bash
# Instalar htop
sudo apt install htop -y

# Verificar recursos
htop
```

### 2. Logs Estruturados

```bash
# Ver logs em tempo real com filtro
docker compose logs backend | grep ERROR
docker compose logs backend | grep WARNING

# Exportar logs para análise
docker compose logs backend > backend_logs_$(date +%Y%m%d).log
```

### 3. Prometheus Metrics (Opcional)

Métricas já expostas em:
```
https://api.seudominio.com/metrics
```

---

## 🔄 Atualizações e Manutenção

### Atualizar Aplicação

```bash
cd /opt/Charlee

# Backup antes de atualizar
/opt/backup-charlee.sh

# Pull latest code
git pull origin main

# Rebuild e restart
cd docker
docker compose down
docker compose build
docker compose up -d

# Rodar novas migrations
docker compose exec backend alembic upgrade head

# Verificar saúde
curl https://api.seudominio.com/health
```

### Rollback em Caso de Problema

```bash
# Voltar para commit anterior
git log --oneline -5
git checkout <COMMIT_ANTERIOR>

# Rebuild
docker compose down
docker compose build
docker compose up -d

# Downgrade migrations se necessário
docker compose exec backend alembic downgrade -1
```

---

## 🆘 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs backend

# Verificar configuração
docker compose config

# Reconstruir do zero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker compose ps postgres

# Conectar direto ao banco
docker compose exec postgres psql -U charlee_prod -d charlee_production

# Verificar logs do banco
docker compose logs postgres
```

### SSL/HTTPS não funciona

```bash
# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --force-renewal

# Verificar configuração Nginx
sudo nginx -t
```

### Performance lenta

```bash
# Verificar uso de recursos
docker stats

# Verificar queries lentas no banco
docker compose exec postgres psql -U charlee_prod -d charlee_production -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# Verificar índices
docker compose exec backend alembic current
```

---

## 📚 Documentação Adicional

- [SETUP.md](SETUP.md) - Configuração detalhada
- [QUICKSTART.md](QUICKSTART.md) - Início rápido
- [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - Checklist de validação
- [MODULES_STATUS.md](MODULES_STATUS.md) - Status dos módulos

---

## 🔐 Checklist de Segurança Pós-Deploy

- [ ] SSL/TLS configurado e funcionando
- [ ] Firewall ativo (UFW)
- [ ] Fail2Ban configurado
- [ ] Senhas fortes em todas as variáveis
- [ ] JWT secrets únicos e seguros
- [ ] Backups automáticos configurados
- [ ] CORS restrito apenas aos domínios necessários
- [ ] Rate limiting ativo
- [ ] Debug mode DESATIVADO (DEBUG=false)
- [ ] Security headers ativos
- [ ] Logs sendo monitorados
- [ ] Health check endpoint funcionando
- [ ] Primeiro usuário admin criado
- [ ] OAuth credentials configurados (se usar)

---

**Última atualização:** 2025-12-26
**Versão:** 2.0.0
**Mantido por:** Samara Cassie
