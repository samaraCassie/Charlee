# Advanced Authentication Features

## 🔒 Funcionalidades Avançadas de Segurança

Este documento descreve as funcionalidades avançadas de autenticação implementadas no sistema Charlee.

---

## 📋 Índice

1. [OAuth Login (Google & GitHub)](#oauth-login)
2. [Account Lockout](#account-lockout)
3. [Audit Log](#audit-log)
4. [Configuração](#configuração)
5. [API Endpoints](#api-endpoints)
6. [Testes](#testes)
7. [Segurança](#segurança)

---

## 🌐 OAuth Login

### Visão Geral

O sistema suporta autenticação via OAuth2 com:
- **Google** - Login com conta Google
- **GitHub** - Login com conta GitHub

### Como Funciona

1. Usuário clica em "Login with Google/GitHub"
2. Redirecionado para página de autorização do provider
3. Após autorização, callback recebe dados do usuário
4. Sistema cria ou atualiza conta do usuário
5. Retorna JWT tokens para autenticação

### Configuração

#### 1. Google OAuth

**Obter Credenciais:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione existente
3. Vá para "APIs & Services" > "Credentials"
4. Crie "OAuth 2.0 Client ID"
5. Adicione URIs autorizados:
   - `http://localhost:8000` (desenvolvimento)
   - `https://your-domain.com` (produção)
6. Adicione redirect URIs:
   - `http://localhost:8000/api/v1/auth/oauth/google/callback`
   - `https://your-domain.com/api/v1/auth/oauth/google/callback`

**Configurar `.env`:**
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

#### 2. GitHub OAuth

**Obter Credenciais:**
1. Acesse [GitHub Developer Settings](https://github.com/settings/developers)
2. Clique em "New OAuth App"
3. Preencha:
   - Application name: `Charlee`
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/api/v1/auth/oauth/github/callback`
4. Copie Client ID e gere Client Secret

**Configurar `.env`:**
```bash
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

### Endpoints OAuth

```bash
# Google Login
GET /api/v1/auth/oauth/google/login

# Google Callback (não chamar diretamente)
GET /api/v1/auth/oauth/google/callback

# GitHub Login
GET /api/v1/auth/oauth/github/login

# GitHub Callback (não chamar diretamente)
GET /api/v1/auth/oauth/github/callback
```

### Exemplo de Uso (Frontend)

```javascript
// Redirecionar para Google OAuth
window.location.href = 'http://localhost:8000/api/v1/auth/oauth/google/login';

// Após callback, tokens estarão na URL
const urlParams = new URLSearchParams(window.location.search);
const accessToken = urlParams.get('access_token');
const refreshToken = urlParams.get('refresh_token');

// Armazenar tokens
localStorage.setItem('access_token', accessToken);
localStorage.setItem('refresh_token', refreshToken);
```

### Campos OAuth no User Model

```python
oauth_provider: Optional[str]  # 'google', 'github', None
oauth_id: str                  # ID do usuário no provider
avatar_url: Optional[str]       # URL do avatar do provider
```

---

## 🔐 Account Lockout

### Visão Geral

Proteção contra ataques de força bruta através de bloqueio temporário de conta após múltiplas tentativas falhas de login.

### Configuração Padrão

```python
MAX_FAILED_ATTEMPTS = 5          # Máximo de tentativas falhas
LOCKOUT_DURATION_MINUTES = 30    # Duração do bloqueio
RESET_ATTEMPTS_AFTER_HOURS = 24  # Reset do contador após 24h
```

### Como Funciona

1. **Tentativa Falha:** Incrementa contador de falhas
2. **Atingiu Máximo:** Bloqueia conta por 30 minutos
3. **Durante Bloqueio:** Todas as tentativas de login retornam 403
4. **Após Tempo:** Bloqueio expira automaticamente
5. **Login Bem-Sucedido:** Reseta contador de falhas

### Comportamento

```bash
# Tentativa 1 (falha)
→ Resposta: 401 - "4 attempts remaining"

# Tentativa 2 (falha)
→ Resposta: 401 - "3 attempts remaining"

# ...

# Tentativa 5 (falha)
→ Resposta: 403 - "Account locked. Try again in 30 minutes."

# Durante bloqueio (mesmo com senha correta)
→ Resposta: 403 - "Account is locked. Try again in 15 minutes."

# Após 30 minutos
→ Bloqueio expira, contador resetado

# Login bem-sucedido
→ Contador resetado imediatamente
```

### Campos no User Model

```python
failed_login_attempts: int     # Contador de tentativas falhas
locked_until: DateTime         # Data/hora até quando está bloqueado
last_failed_login: DateTime    # Última tentativa falha
```

### Métodos

```python
user.is_locked() -> bool
# Verifica se conta está bloqueada

user.reset_failed_attempts() -> None
# Reseta contador e remove bloqueio
```

### Desbloquear Manualmente

```python
from api.auth.lockout import unlock_account

# Desbloquear usuário
unlock_account(db, user)
```

---

## 📊 Audit Log

### Visão Geral

Sistema completo de auditoria que registra todos os eventos de autenticação e segurança.

### Eventos Registrados

| Evento | Tipo | Status | Descrição |
|--------|------|--------|-----------|
| **register** | `register` | success | Novo usuário registrado |
| **login** | `login` | success | Login bem-sucedido |
| **login** | `login` | failure | Tentativa de login falha |
| **oauth_login** | `oauth_login` | success | Login via OAuth |
| **logout** | `logout` | success | Logout realizado |
| **password_change** | `password_change` | success | Senha alterada |
| **account_locked** | `account_locked` | blocked | Conta bloqueada |

### Campos do AuditLog

```python
id: int
user_id: int                    # ID do usuário (null se não identificado)
event_type: str                 # Tipo do evento
event_status: str               # 'success', 'failure', 'blocked'
event_message: str              # Mensagem descritiva
ip_address: str                 # IP da requisição
user_agent: str                 # User agent do navegador
request_path: str               # Caminho da API
metadata: JSON                  # Dados adicionais (JSON)
created_at: DateTime            # Timestamp do evento
```

### Consultar Audit Log

```python
from database.models import AuditLog

# Todos os eventos de um usuário
logs = db.query(AuditLog).filter(
    AuditLog.user_id == user_id
).order_by(AuditLog.created_at.desc()).all()

# Logins falhos nas últimas 24h
from datetime import datetime, timedelta
yesterday = datetime.utcnow() - timedelta(days=1)

failed_logins = db.query(AuditLog).filter(
    AuditLog.event_type == "login",
    AuditLog.event_status == "failure",
    AuditLog.created_at >= yesterday
).all()

# Eventos de um IP específico
ip_logs = db.query(AuditLog).filter(
    AuditLog.ip_address == "192.168.1.1"
).all()
```

### API Endpoint (Admin Only - Futuro)

```bash
# Listar audit logs (requer admin)
GET /api/v1/admin/audit-logs?user_id=1&limit=100

# Audit logs por tipo de evento
GET /api/v1/admin/audit-logs?event_type=login&status=failure
```

### Exemplo de Log Entry

```json
{
  "id": 123,
  "user_id": 5,
  "event_type": "login",
  "event_status": "failure",
  "event_message": "Failed login attempt for 'john': Invalid credentials. 2 attempts remaining.",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "request_path": "/api/v1/auth/login",
  "metadata": {
    "username": "john",
    "reason": "Invalid credentials. 2 attempts remaining."
  },
  "created_at": "2025-01-15T14:30:00Z"
}
```

---

## ⚙️ Configuração

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais OAuth
```

### 3. Rodar Migrations

```bash
alembic upgrade head
```

Isso criará:
- ✅ Campos OAuth no User
- ✅ Campos de lockout no User
- ✅ Tabela audit_logs

### 4. Popular Dados Iniciais (Opcional)

```bash
python -m database.seed_default_user
```

---

## 🔌 API Endpoints

### Authentication Endpoints (Atualizados)

```bash
# Registro (com audit log)
POST /api/v1/auth/register

# Login (com lockout protection e audit log)
POST /api/v1/auth/login

# Logout (com audit log)
POST /api/v1/auth/logout

# Password Change (com audit log)
POST /api/v1/auth/change-password
```

### OAuth Endpoints (Novos)

```bash
# Google OAuth Flow
GET  /api/v1/auth/oauth/google/login
GET  /api/v1/auth/oauth/google/callback

# GitHub OAuth Flow
GET  /api/v1/auth/oauth/github/login
GET  /api/v1/auth/oauth/github/callback
```

---

## 🧪 Testes

### Executar Testes

```bash
cd backend

# Todos os testes de autenticação
pytest tests/test_api/test_auth.py -v
pytest tests/test_api/test_auth_advanced.py -v

# Testes específicos
pytest tests/test_api/test_auth_advanced.py::TestAccountLockout -v
pytest tests/test_api/test_auth_advanced.py::TestAuditLog -v
```

### Cobertura de Testes

- ✅ **Account Lockout** (6 testes)
  - Bloqueio após 5 tentativas
  - Conta bloqueada não pode logar
  - Login bem-sucedido reseta contador
  - Reset automático após 24h

- ✅ **Audit Log** (7 testes)
  - Log de registro
  - Log de login (sucesso e falha)
  - Log de logout
  - Log de password change
  - Log de account lockout
  - Captura de IP e User-Agent

- ✅ **OAuth** (3 testes)
  - Criação de usuário OAuth
  - Métodos de lockout disponíveis
  - Segurança geral

---

## 🛡️ Segurança

### Melhores Práticas Implementadas

1. **OAuth Seguro**
   - State validation (CSRF protection)
   - Secure token storage
   - Provider verification

2. **Account Lockout**
   - Proteção contra brute force
   - Duração configurável
   - Reset automático

3. **Audit Log**
   - Registro completo de eventos
   - IP tracking
   - Metadata extensível

4. **Rate Limiting**
   - Já configurado no sistema
   - 60 requests/minuto
   - 1000 requests/hora

### Recomendações de Produção

1. **OAuth:**
   - Use HTTPS obrigatório
   - Valide redirect URIs
   - Implemente state parameter

2. **Account Lockout:**
   - Configure alertas para múltiplos bloqueios
   - Implemente CAPTCHA após X tentativas
   - Considere lockout progressivo

3. **Audit Log:**
   - Configure retention policy
   - Implemente arquivamento
   - Configure alertas para eventos suspeitos

4. **Monitoring:**
   - Monitor failed login patterns
   - Track lockout frequency
   - Analyze audit logs regularly

---

## 📈 Métricas e Monitoring

### Queries Úteis

```sql
-- Logins falhos por usuário (últimas 24h)
SELECT user_id, COUNT(*) as failures
FROM audit_logs
WHERE event_type = 'login'
  AND event_status = 'failure'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_id
ORDER BY failures DESC;

-- IPs com mais tentativas falhas
SELECT ip_address, COUNT(*) as attempts
FROM audit_logs
WHERE event_type = 'login'
  AND event_status = 'failure'
GROUP BY ip_address
ORDER BY attempts DESC
LIMIT 10;

-- Contas bloqueadas atualmente
SELECT id, username, locked_until
FROM users
WHERE locked_until > NOW();
```

---

## 🚀 Próximos Passos Opcionais

- [ ] 2FA (Two-Factor Authentication)
- [ ] Email verification
- [ ] Password reset via email
- [ ] Social login (Facebook, Twitter, etc.)
- [ ] Admin panel para audit logs
- [ ] IP whitelist/blacklist
- [ ] Device fingerprinting
- [ ] Session management dashboard

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação acima
2. Consulte os testes em `tests/test_api/test_auth_advanced.py`
3. Revise o código fonte em `backend/api/auth/`

---

**Implementado com ❤️ seguindo os mais altos padrões de qualidade e segurança.**
