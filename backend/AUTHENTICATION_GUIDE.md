# 🔐 Guia Completo de Autenticação - Charlee

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Recursos Implementados](#recursos-implementados)
- [Instalação e Configuração](#instalação-e-configuração)
- [API Endpoints](#api-endpoints)
- [Proteção de Rotas](#proteção-de-rotas)
- [Segurança](#segurança)
- [Testes](#testes)

---

## 🎯 Visão Geral

Sistema completo de autenticação JWT com recursos avançados de segurança implementado para o Charlee.

### Características Principais

- ✅ **JWT (JSON Web Tokens)**: Access tokens (30 min) e Refresh tokens (7 dias)
- ✅ **OAuth 2.0**: Login com Google e GitHub
- ✅ **Account Lockout**: Bloqueio após 5 tentativas falhas (30 minutos)
- ✅ **Audit Log**: Registro completo de eventos de segurança
- ✅ **Password Hashing**: bcrypt com salt
- ✅ **Multi-tenancy**: Isolamento completo de dados por usuário
- ✅ **49+ Testes**: Cobertura completa de casos de uso

---

## 📦 Recursos Implementados

### 1. Autenticação JWT

**Tokens:**
- **Access Token**: 30 minutos de validade
- **Refresh Token**: 7 dias de validade com armazenamento em banco

**Endpoints:**
```
POST   /api/v1/auth/register       # Registro de novo usuário
POST   /api/v1/auth/login          # Login com email/senha
POST   /api/v1/auth/refresh        # Renovar access token
POST   /api/v1/auth/logout         # Logout (revoga refresh token)
POST   /api/v1/auth/logout-all     # Logout de todos os dispositivos
GET    /api/v1/auth/me             # Informações do usuário atual
POST   /api/v1/auth/change-password # Trocar senha
```

### 2. OAuth 2.0

**Providers Suportados:**
- Google
- GitHub

**Endpoints:**
```
GET    /api/v1/auth/oauth/google/login     # Inicia login com Google
GET    /api/v1/auth/oauth/google/callback  # Callback do Google
GET    /api/v1/auth/oauth/github/login     # Inicia login com GitHub
GET    /api/v1/auth/oauth/github/callback  # Callback do GitHub
```

### 3. Account Lockout

**Configuração:**
- Máximo de tentativas: 5
- Duração do bloqueio: 30 minutos
- Reset automático após 24 horas

**Comportamento:**
- Após 3 tentativas: Aviso de tentativas restantes
- Após 5 tentativas: Conta bloqueada temporariamente
- Registro no Audit Log

### 4. Audit Log

**Eventos Rastreados:**
- `login` - Login bem-sucedido/falhado
- `register` - Registro de novo usuário
- `logout` - Logout
- `password_change` - Troca de senha
- `account_locked` - Bloqueio de conta
- `oauth_login` - Login via OAuth

**Informações Capturadas:**
- User ID
- IP Address
- User Agent
- Request Path
- Metadata adicional (JSON)
- Timestamp

---

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

**Novas dependências:**
- `python-jose[cryptography]` - JWT
- `passlib[bcrypt]` - Password hashing
- `authlib` - OAuth
- `httpx` - HTTP client async

### 2. Configurar Variáveis de Ambiente

Crie/atualize o arquivo `.env`:

```bash
# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here_use_openssl_rand_hex_32
JWT_REFRESH_SECRET_KEY=your_jwt_refresh_secret_key_here_use_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Configuration (opcional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/charlee_db
```

**Gerar chaves seguras:**
```bash
# JWT Secret Key
openssl rand -hex 32

# JWT Refresh Secret Key
openssl rand -hex 32
```

### 3. Executar Migrações

```bash
cd backend
alembic upgrade head
```

**Migrações criadas:**
- `002_add_authentication.py` - Tabelas users, refresh_tokens, user_id em todas as tabelas
- `003_add_oauth_lockout_audit.py` - OAuth, account lockout, audit logs

### 4. Criar Usuário Padrão (Opcional)

```bash
python -m database.seed_default_user
```

**Credenciais padrão:**
- Username: `admin`
- Email: `admin@charlee.local`
- Password: `ChangeMe123!`

**⚠️ IMPORTANTE:** Troque a senha em produção!

---

## 📡 API Endpoints

### Autenticação Básica

#### 1. Registrar Novo Usuário

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "usuario",
  "email": "usuario@example.com",
  "password": "SenhaForte123!",
  "full_name": "Nome Completo"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "usuario",
  "email": "usuario@example.com",
  "full_name": "Nome Completo",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00"
}
```

#### 2. Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "usuario",
  "password": "SenhaForte123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 3. Renovar Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### 4. Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### 5. Obter Informações do Usuário

```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

#### 6. Trocar Senha

```http
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "SenhaAntiga123!",
  "new_password": "SenhaNova456!"
}
```

---

## 🔒 Proteção de Rotas

### Todas as Rotas Protegidas (14 endpoints)

#### 1. **Big Rocks** (`/api/v1/big-rocks`)
```python
from api.auth.dependencies import get_current_user

@router.get("/")
async def get_big_rocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_big_rocks(db, user_id=current_user.id)
```

#### 2. **Tasks** (`/api/v1/tasks`)
- `GET /` - Listar tarefas
- `POST /` - Criar tarefa
- `GET /{id}` - Obter tarefa
- `PUT /{id}` - Atualizar tarefa
- `DELETE /{id}` - Deletar tarefa

#### 3. **Agent** (`/api/v1/agent`)
- `POST /chat` - Chat com Charlee
- `GET /status` - Status do orchestrator
- `POST /analyze-routing` - Analisar roteamento

#### 4. **Wellness** (`/api/v1/wellness`)
- `POST /ciclo/registrar` - Registrar fase do ciclo
- `GET /ciclo/atual` - Fase atual
- `GET /ciclo/sugestoes` - Sugestões
- `GET /ciclo/analise-carga` - Análise de carga

#### 5. **Capacity** (`/api/v1/capacity`)
- `GET /carga/atual` - Carga de trabalho atual
- `POST /avaliar-compromisso` - Avaliar compromisso
- `GET /tradeoffs` - Sugestões de trade-offs
- `GET /big-rocks/analise` - Análise de Big Rocks

#### 6. **Priorização** (`/api/v1/priorizacao`)
- `GET /inbox` - Inbox rápido
- `POST /recalcular` - Recalcular prioridades
- `GET /tarefas-priorizadas` - Listar priorizadas

#### 7. **Inbox** (`/api/v1/inbox`)
- `GET /rapido` - Inbox rápido
- `GET /hoje` - Tarefas de hoje
- `GET /atrasadas` - Tarefas atrasadas
- `GET /proxima-semana` - Próxima semana

#### 8. **Analytics** (`/api/v1/analytics`)
- `GET /weekly` - Estatísticas semanais
- `GET /monthly` - Estatísticas mensais
- `GET /big-rocks-distribution` - Distribuição por Big Rock
- `GET /productivity` - Estatísticas de produtividade
- `GET /cycle-productivity` - Produtividade por ciclo

#### 9. **Settings** (`/api/v1/settings`)
- `GET /user` - Configurações do usuário
- `PATCH /user` - Atualizar configurações
- `GET /system` - Estatísticas do sistema
- `POST /export` - Exportar dados
- `POST /reset` - Resetar dados

### Como Usar em Novas Rotas

```python
from fastapi import APIRouter, Depends
from api.auth.dependencies import get_current_user
from database.models import User

router = APIRouter()

@router.get("/minha-rota")
async def minha_funcao(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user.id - ID do usuário autenticado
    # current_user.username - Username
    # current_user.email - Email

    # Filtrar dados por usuário
    dados = db.query(MinhaTabela).filter(
        MinhaTabela.user_id == current_user.id
    ).all()

    return dados
```

---

## 🛡️ Segurança

### Validação de Senha

**Requisitos:**
- Mínimo 8 caracteres
- Pelo menos 1 letra maiúscula
- Pelo menos 1 letra minúscula
- Pelo menos 1 dígito

### Password Hashing

- **Algoritmo**: bcrypt
- **Salt**: Automático (bcrypt)
- **Cost Factor**: 12 (padrão)

### Token Security

**Access Token:**
- Expira em 30 minutos
- Não pode ser revogado manualmente
- Contém: user_id, username, email

**Refresh Token:**
- Expira em 7 dias
- Armazenado em banco de dados
- Pode ser revogado manualmente
- Rastreia: user_agent, ip_address

### Account Lockout

**Proteção contra brute force:**
- 5 tentativas máximas
- Bloqueio de 30 minutos
- Reset automático após 24h
- Registro em Audit Log

### Audit Log

**Compliance e Segurança:**
- Todos os eventos de autenticação são registrados
- Informações de IP e User Agent
- Metadata em JSON
- Retenção ilimitada (configurável)

---

## 🧪 Testes

### Executar Todos os Testes

```bash
cd backend
pytest tests/test_api/test_auth.py -v
pytest tests/test_api/test_auth_advanced.py -v
```

### Cobertura

**49+ testes implementados:**

#### Autenticação Básica (20 testes)
- ✅ Registro de usuário
- ✅ Login com credenciais válidas
- ✅ Login com credenciais inválidas
- ✅ Refresh token
- ✅ Logout
- ✅ Logout all devices
- ✅ Troca de senha
- ✅ Validação de email único
- ✅ Validação de username único

#### Account Lockout (4 testes)
- ✅ Bloqueio após 5 tentativas
- ✅ Desbloqueio automático após timeout
- ✅ Reset de contador após login bem-sucedido
- ✅ Mensagens de feedback

#### Audit Log (7 testes)
- ✅ Registro de login bem-sucedido
- ✅ Registro de login falhado
- ✅ Registro de bloqueio de conta
- ✅ Registro de logout
- ✅ Registro de troca de senha
- ✅ Captura de IP e User Agent
- ✅ Metadata JSON

#### OAuth (2 testes)
- ✅ Criação de usuário OAuth
- ✅ Métodos do modelo

#### Isolamento de Dados (1 teste)
- ✅ Usuário não acessa dados de outro usuário

#### Segurança (3 testes)
- ✅ Token inválido
- ✅ Token expirado
- ✅ Senha forte

### Exemplo de Teste

```python
def test_login_success(client, sample_user):
    """Should login successfully with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
```

---

## 🔧 Configuração OAuth

### Google OAuth

1. **Criar Projeto no Google Cloud Console**
   - Acesse: https://console.cloud.google.com/
   - Crie novo projeto

2. **Configurar OAuth Consent Screen**
   - APIs & Services > OAuth consent screen
   - User Type: External
   - Adicione escopos: `email`, `profile`

3. **Criar Credenciais**
   - APIs & Services > Credentials
   - Create Credentials > OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/oauth/google/callback`

4. **Copiar Credenciais para `.env`**
   ```bash
   GOOGLE_CLIENT_ID=seu_client_id
   GOOGLE_CLIENT_SECRET=seu_client_secret
   ```

### GitHub OAuth

1. **Criar OAuth App no GitHub**
   - Settings > Developer settings > OAuth Apps
   - New OAuth App

2. **Configurar**
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/v1/auth/oauth/github/callback`

3. **Copiar Credenciais para `.env`**
   ```bash
   GITHUB_CLIENT_ID=seu_client_id
   GITHUB_CLIENT_SECRET=seu_client_secret
   ```

---

## 📊 Estrutura do Banco de Dados

### Tabela: `users`

```sql
id                      SERIAL PRIMARY KEY
username                VARCHAR(50) UNIQUE NOT NULL
email                   VARCHAR(255) UNIQUE NOT NULL
hashed_password         VARCHAR(255) NOT NULL
full_name               VARCHAR(100)
is_active               BOOLEAN DEFAULT TRUE
is_superuser            BOOLEAN DEFAULT FALSE
created_at              TIMESTAMP DEFAULT NOW()
updated_at              TIMESTAMP DEFAULT NOW()
last_login              TIMESTAMP

-- OAuth
oauth_provider          VARCHAR(50)
oauth_id                VARCHAR(255) INDEX
avatar_url              VARCHAR(500)

-- Account Lockout
failed_login_attempts   INTEGER DEFAULT 0
locked_until            TIMESTAMP
last_failed_login       TIMESTAMP
```

### Tabela: `refresh_tokens`

```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE
token           VARCHAR(500) UNIQUE NOT NULL
expires_at      TIMESTAMP NOT NULL
created_at      TIMESTAMP DEFAULT NOW()
revoked         BOOLEAN DEFAULT FALSE
revoked_at      TIMESTAMP
user_agent      VARCHAR(255)
ip_address      VARCHAR(50)
```

### Tabela: `audit_logs`

```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE
event_type      VARCHAR(50) NOT NULL INDEX
event_status    VARCHAR(20) NOT NULL
event_message   TEXT
ip_address      VARCHAR(50) INDEX
user_agent      VARCHAR(255)
request_path    VARCHAR(255)
event_metadata  JSON
created_at      TIMESTAMP DEFAULT NOW() INDEX
```

---

## 🚀 Deploy em Produção

### Checklist de Segurança

- [ ] Gerar chaves JWT únicas e fortes
- [ ] Configurar HTTPS/TLS
- [ ] Configurar CORS adequadamente
- [ ] Trocar senha do usuário padrão
- [ ] Configurar rate limiting
- [ ] Configurar backup do banco de dados
- [ ] Configurar logs de aplicação
- [ ] Revisar permissões de banco de dados
- [ ] Configurar OAuth URLs de produção
- [ ] Testar account lockout
- [ ] Revisar audit logs regularmente

### Variáveis de Ambiente Produção

```bash
# JWT - GERAR NOVAS CHAVES!
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/charlee_prod

# OAuth - URLs de produção
GOOGLE_CLIENT_ID=prod_client_id
GOOGLE_CLIENT_SECRET=prod_secret
GITHUB_CLIENT_ID=prod_client_id
GITHUB_CLIENT_SECRET=prod_secret
```

---

## 📚 Referências

- [JWT.io](https://jwt.io/) - JSON Web Tokens
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth 2.0](https://oauth.net/2/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## 🆘 Troubleshooting

### Erro: "Token has expired"

**Solução:** Use o refresh token para obter novo access token:
```http
POST /api/v1/auth/refresh
```

### Erro: "Account is locked"

**Solução:** Aguarde 30 minutos ou contacte administrador.

### Erro: "Invalid credentials"

**Solução:** Verifique username/password. Após 3 tentativas, você receberá aviso de tentativas restantes.

### Erro: "User already exists"

**Solução:** Username ou email já cadastrado. Use outro.

---

## 📞 Suporte

Para questões ou problemas:
1. Verifique os logs do audit log
2. Execute os testes
3. Consulte esta documentação
4. Crie uma issue no GitHub

---

**Versão:** 2.0.0
**Última Atualização:** 12/11/2025
**Status:** ✅ Produção Ready
