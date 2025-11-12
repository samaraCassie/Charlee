# 🔐 Security Standards - Segurança

> **Projeto:** Charlee
> **OWASP Top 10:** Compliance obrigatório
> **Status:** Crítico

---

## 📋 Índice

1. [Gestão de Secrets](#gestão-de-secrets)
2. [Autenticação e Autorização](#autenticação-e-autorização)
3. [Validação de Inputs](#validação-de-inputs)
4. [OWASP Top 10](#owasp-top-10)
5. [Dependency Scanning](#dependency-scanning)
6. [Security Headers](#security-headers)

---

## 🔑 Gestão de Secrets

### ❌ NUNCA Faça Isso

```python
# ❌ ERRADO - Hardcoded
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ❌ ERRADO - Commitado no código
OPENAI_API_KEY = "sk-proj-abc123..."

# ❌ ERRADO - Em arquivo versionado
# config.py
SECRET_KEY = "my-secret-key-123"
```

### ✅ Forma Correta

```python
# ✅ CERTO - Variáveis de ambiente
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str
    secret_key: str
    redis_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Uso
client = OpenAI(api_key=settings.openai_api_key)
```

### .env Best Practices

```bash
# .env (NÃO commitado)
OPENAI_API_KEY=sk-proj-actual-key-here
DATABASE_URL=postgresql://user:real_password@localhost/db
SECRET_KEY=generate-with-secrets-token-urlsafe-32

# .env.example (COMMITADO como template)
OPENAI_API_KEY=sk-your-api-key-here
DATABASE_URL=postgresql://user:password@localhost/charlee_db
SECRET_KEY=your-secret-key-here
```

### Validação de Secrets na Inicialização

```python
# api/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validar secrets antes de iniciar."""

    required_secrets = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY",
    ]

    missing = []
    for secret in required_secrets:
        value = os.getenv(secret)
        if not value or value.startswith("your-") or value.startswith("change-me"):
            missing.append(secret)

    if missing:
        raise ValueError(
            f"❌ Secrets não configurados: {', '.join(missing)}\n"
            f"Configure no arquivo .env antes de iniciar."
        )

    logger.info("✅ Secrets validados com sucesso")
    yield
```

### Rotação de Secrets

```bash
# Trocar secrets regularmente (a cada 90 dias)

# 1. Gerar novo secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Atualizar .env
# 3. Restart aplicação
# 4. Revogar secret antigo
```

---

## 🔐 Autenticação e Autorização

### JWT Authentication (Futuro)

```python
# auth/jwt.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Criar JWT token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash de senha."""
    return pwd_context.hash(password)
```

### Proteger Endpoints

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obter usuário do token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception

    return user

# Uso
@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## ✅ Validação de Inputs

### Sempre Validar com Pydantic

```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr  # ← Validação automática de email
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        """Validar força da senha."""
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve conter letra maiúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter número')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Senha deve conter caractere especial')
        return v

    @validator('name')
    def name_sanitize(cls, v):
        """Sanitizar nome."""
        # Remove caracteres perigosos
        return v.strip()
```

### SQL Injection Prevention

```python
# ✅ CERTO - SQLAlchemy ORM (previne SQL injection automaticamente)
from sqlalchemy import select

stmt = select(User).where(User.email == email)
user = db.execute(stmt).scalar_one_or_none()

# ✅ CERTO - Parametrização explícita
from sqlalchemy import text

stmt = text("SELECT * FROM users WHERE email = :email")
result = db.execute(stmt, {"email": email})

# ❌ ERRADO - String concatenation (SQL injection!)
query = f"SELECT * FROM users WHERE email = '{email}'"  # NUNCA!
```

### XSS Prevention (Frontend)

```typescript
// ✅ React automaticamente escapa output
const UserProfile = ({ name }: { name: string }) => {
  return <h1>{name}</h1>; // Seguro, React escapa automaticamente
};

// ❌ EVITAR - dangerouslySetInnerHTML sem sanitização
const Component = ({ html }: { html: string }) => {
  return <div dangerouslySetInnerHTML={{ __html: html }} />; // Perigoso!
};

// ✅ Se realmente necessário, sanitize primeiro
import DOMPurify from 'dompurify';

const SafeHTML = ({ html }: { html: string }) => {
  const sanitized = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
};
```

---

## 🛡️ OWASP Top 10

### 1. Broken Access Control

```python
# ✅ Verificar autorização
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404)

    # ✅ Verificar que tarefa pertence ao usuário
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado"
        )

    return task
```

### 2. Cryptographic Failures

```python
# ✅ Usar HTTPS em produção
# ✅ Hash senhas com bcrypt/argon2
# ✅ Não armazenar senhas em plain text

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],  # ← Mais seguro que bcrypt
    deprecated="auto"
)

hashed = pwd_context.hash(password)
```

### 3. Injection

- ✅ Use ORMs (SQLAlchemy)
- ✅ Parametrize queries
- ✅ Valide inputs com Pydantic
- ❌ Nunca concatene strings em queries

### 4. Insecure Design

- ✅ Authentication obrigatória em produção
- ✅ Rate limiting
- ✅ Logging de ações sensíveis
- ✅ Princípio do menor privilégio

### 5. Security Misconfiguration

```python
# ✅ Produção
DEBUG = False
ALLOWED_HOSTS = ["charlee.app"]
CORS_ORIGINS = ["https://charlee.app"]

# ❌ NUNCA em produção
DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ORIGINS = ["*"]
```

### 6. Vulnerable Components

```bash
# Scan de vulnerabilidades

# Backend
pip-audit

# Frontend
npm audit

# Fix automaticamente
npm audit fix

# Atualizar deps regularmente
pip-review --auto
npm update
```

### 7. Authentication Failures

```python
# ✅ Rate limiting em login
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # ← Máximo 5 tentativas por minuto
async def login(request: Request, credentials: LoginRequest):
    ...
```

### 8. Software and Data Integrity

- ✅ Verificar assinaturas de packages
- ✅ Use lock files (requirements.txt, package-lock.json)
- ✅ Pin versões em produção
- ✅ CI/CD com verificação de integridade

### 9. Logging Failures

```python
# ✅ Log ações sensíveis
logger.info(
    "Login attempt",
    extra={
        "user": username,
        "ip": request.client.host,
        "success": True
    }
)

# ❌ NÃO logar secrets
logger.info(f"API key: {api_key}")  # NUNCA!

# ✅ Maskare secrets em logs
logger.info(f"API key: {api_key[:8]}...")  # Primeiros 8 chars apenas
```

### 10. Server-Side Request Forgery (SSRF)

```python
# ✅ Validar URLs externas
from urllib.parse import urlparse

ALLOWED_DOMAINS = ["api.openai.com", "api.anthropic.com"]

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname in ALLOWED_DOMAINS

# Uso
if not validate_url(external_url):
    raise ValueError("URL not allowed")
```

---

## 🔍 Dependency Scanning

### Automatizar Scans

```yaml
# .github/workflows/security.yml

name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 1'  # Toda segunda-feira
  push:
    branches: [main]

jobs:
  backend-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit -r backend/requirements.txt

  frontend-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run npm audit
        run: |
          cd interfaces/web
          npm audit --audit-level=high

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
```

---

## 🔒 Security Headers

### Configurar Headers (FastAPI)

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Apenas hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["charlee.app", "*.charlee.app"]
)

# Force HTTPS em produção
if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response
```

---

## ✅ Checklist de Segurança

Antes de deploy em produção:

- [ ] Sem secrets hardcoded
- [ ] .env não commitado
- [ ] Validação de secrets na inicialização
- [ ] HTTPS habilitado
- [ ] Security headers configurados
- [ ] Authentication implementada
- [ ] Rate limiting ativo
- [ ] Inputs validados com Pydantic
- [ ] SQLAlchemy ORM (sem queries raw)
- [ ] Dependency scan passou
- [ ] Logs não expõem secrets
- [ ] CORS configurado (não *)

---

**Última atualização:** 2025-11-10
