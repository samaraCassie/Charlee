# 📐 Padrões de Qualidade - Projeto Charlee

> **Versão:** 1.0
> **Data:** 2025-11-10
> **Status:** Ativo e obrigatório para todos os contribuidores

---

## 📋 Visão Geral

Este documento serve como **índice central** para todos os padrões de qualidade do projeto Charlee. Cada área técnica possui seu próprio documento detalhado com regras, exemplos e checklists.

**Objetivo**: Garantir código de alta qualidade, seguro, testável e manutenível em todo o projeto.

---

## 🎯 Princípios Fundamentais

### 1. **Qualidade Não É Opcional**
- ✅ Todo código deve passar por linting e formatação
- ✅ Todo código deve ter testes
- ✅ Todo PR deve passar no CI/CD
- ❌ Não há "exceções temporárias"

### 2. **Prevenção > Correção**
- ✅ Use pre-commit hooks
- ✅ Valide na IDE em tempo real
- ✅ CI/CD bloqueia merges com problemas
- ❌ Não corrija depois, previna antes

### 3. **Automatize Tudo**
- ✅ Formatação automática (black, prettier)
- ✅ Testes automáticos (pytest, vitest)
- ✅ Deploy automático (CI/CD)
- ❌ Nada manual que possa ser automatizado

### 4. **Documente Decisões**
- ✅ Comentários explicam "por quê", não "o quê"
- ✅ ADRs para decisões arquiteturais
- ✅ README atualizado
- ❌ Código "auto-explicativo" sem contexto

### 5. **Segurança em Primeiro Lugar**
- ✅ Nunca commite secrets
- ✅ Validação de inputs sempre
- ✅ Autenticação em produção
- ❌ "Vou adicionar depois" não existe

---

## 📚 Documentos de Padrões

### Backend (Python/FastAPI)
📄 **[Backend Standards](standards/BACKEND_STANDARDS.md)**

Cobre:
- Estrutura de código e organização
- Type hints e validação
- Padrões de API (FastAPI)
- Tratamento de erros
- Logging e observabilidade
- Dependências e gerenciamento

**Regras obrigatórias**:
- ✅ Type hints em todas as funções
- ✅ Docstrings em funções públicas
- ✅ Black formatação (line-length=100)
- ✅ Ruff linting (sem warnings)
- ✅ MyPy type checking (strict mode)

---

### Frontend (React/TypeScript)
📄 **[Frontend Standards](standards/FRONTEND_STANDARDS.md)**

Cobre:
- Estrutura de componentes
- TypeScript strict mode
- State management (Zustand)
- Performance e otimização
- Acessibilidade (a11y)
- Estilização (Tailwind CSS)

**Regras obrigatórias**:
- ✅ TypeScript strict mode habilitado
- ✅ Componentes funcionais com hooks
- ✅ ESLint sem warnings
- ✅ Interfaces explícitas para props
- ✅ Acessibilidade (WCAG 2.1 AA)

---

### Versionamento e Git
📄 **[Git Standards](standards/GIT_STANDARDS.md)**

Cobre:
- Conventional Commits
- Branching strategy (Git Flow)
- Pull Request process
- Commit message guidelines
- .gitignore best practices

**Regras obrigatórias**:
- ✅ Conventional Commits (feat:, fix:, docs:)
- ✅ Branches descritivos (feat/*, fix/*)
- ✅ PRs com descrição e reviewers
- ✅ Squash merge para features
- ❌ Nunca commitar secrets

---

### Testes
📄 **[Testing Standards](standards/TESTING_STANDARDS.md)**

Cobre:
- Pirâmide de testes
- Testes unitários (pytest, vitest)
- Testes de integração
- Testes E2E (Playwright)
- Coverage requirements
- Mocking e fixtures

**Regras obrigatórias**:
- ✅ Cobertura mínima: 80%
- ✅ Testes para toda feature nova
- ✅ Testes rodam no CI/CD
- ✅ Fixtures reusáveis
- ❌ Não mergeie se testes falharem

---

### Segurança
📄 **[Security Standards](standards/SECURITY_STANDARDS.md)**

Cobre:
- Gestão de secrets
- Autenticação e autorização
- Validação de inputs
- OWASP Top 10
- Dependency scanning
- Security headers

**Regras obrigatórias**:
- ✅ Secrets em variáveis de ambiente
- ✅ Validação com Pydantic/Zod
- ✅ HTTPS em produção
- ✅ Scan de dependências semanal
- ❌ Zero tolerância para vulnerabilidades críticas

---

### Code Review
📄 **[Code Review Checklist](standards/CODE_REVIEW_CHECKLIST.md)**

Cobre:
- Checklist de revisão
- O que procurar
- Como dar feedback
- Aprovação de PRs
- Bloqueios automáticos

**Regras obrigatórias**:
- ✅ Pelo menos 1 aprovação
- ✅ CI/CD verde
- ✅ Checklist completo
- ✅ Sem comentários não resolvidos
- ❌ Auto-merge proibido

---

### CI/CD
📄 **[CI/CD Standards](standards/CI_CD_STANDARDS.md)**

Cobre:
- Pipeline structure
- Testes automatizados
- Build e deploy
- Environments (dev, staging, prod)
- Rollback strategy

**Regras obrigatórias**:
- ✅ Todos os testes rodam no CI
- ✅ Deploy automático após merge
- ✅ Rollback em < 5 minutos
- ✅ Zero downtime deploys
- ❌ Deploy manual proibido em prod

---

## 🚦 Níveis de Enforcement

### 🔴 BLOQUEANTE
**Pipeline falha, merge impossível**
- Testes falhando
- Coverage abaixo de 80%
- Linting com erros
- Type errors
- Security vulnerabilities (critical/high)

### 🟡 WARNING
**Revisor deve avaliar, pode mergear com justificativa**
- Coverage entre 70-80%
- Warnings de linting
- Security vulnerabilities (medium)
- TODO comments sem issue linkado

### 🟢 INFORMATIVO
**Não bloqueia, mas deve ser endereçado**
- Code smells
- Complexity warnings
- Performance suggestions
- Security vulnerabilities (low)

---

## 🛠️ Ferramentas Obrigatórias

### Backend
```bash
# Formatação
black==23.12.1

# Linting
ruff==0.1.11

# Type checking
mypy==1.8.0

# Testes
pytest>=7.4.4
pytest-cov>=4.1.0
pytest-asyncio>=0.23.3

# Security
pip-audit
bandit
```

### Frontend
```json
{
  "devDependencies": {
    "eslint": "^9.36.0",
    "prettier": "^3.0.0",
    "typescript": "~5.9.3",
    "vitest": "^4.0.8",
    "@vitest/coverage-v8": "^4.0.8",
    "playwright": "^1.40.0"
  }
}
```

### Git
```bash
# Pre-commit hooks
pre-commit==3.5.0
```

---

## 📊 Métricas de Qualidade

### Mínimos Aceitáveis

| Métrica | Mínimo | Ideal | Atual Charlee |
|---------|--------|-------|---------------|
| Test Coverage (Backend) | 70% | 85%+ | ❌ 0% |
| Test Coverage (Frontend) | 70% | 85%+ | ✅ 88% |
| Linting Pass Rate | 100% | 100% | ⚠️ N/A |
| Type Coverage | 90% | 100% | ⚠️ Desconhecido |
| Security Vulnerabilities | 0 critical | 0 high/critical | ⚠️ Não monitorado |
| Build Success Rate | 95% | 99%+ | ⚠️ Sem CI/CD |
| Code Review Time | < 24h | < 8h | ⚠️ Não rastreado |

---

## 🎯 Workflow de Desenvolvimento

### 1. Antes de Começar
```bash
# Atualizar branch
git checkout main
git pull origin main

# Criar feature branch
git checkout -b feat/minha-feature

# Instalar pre-commit hooks (primeira vez)
pre-commit install
```

### 2. Durante o Desenvolvimento
```bash
# Rodar formatação
black backend/
prettier --write interfaces/web/src/

# Rodar linting
ruff check backend/ --fix
npm run lint --fix

# Rodar testes
pytest backend/tests -v
npm run test

# Verificar cobertura
pytest --cov=backend --cov-report=html
npm run test:coverage
```

### 3. Antes do Commit
```bash
# Pre-commit roda automaticamente, mas pode rodar manual:
pre-commit run --all-files

# Verificar que tudo está ok
git status
```

### 4. Criando PR
```bash
# Push da branch
git push -u origin feat/minha-feature

# No GitHub:
# 1. Criar PR
# 2. Preencher template
# 3. Adicionar reviewers
# 4. Linkar issues
# 5. Aguardar CI/CD
```

### 5. Code Review
```markdown
# Checklist do Revisor:
- [ ] Código segue padrões do projeto
- [ ] Testes cobrem casos principais
- [ ] Documentação atualizada
- [ ] Sem hardcoded secrets
- [ ] Performance considerada
- [ ] Acessibilidade verificada (frontend)
```

### 6. Após Aprovação
```bash
# Squash merge (preferido)
# Ou rebase se histórico importante

# Deletar branch após merge
git branch -d feat/minha-feature
git push origin --delete feat/minha-feature
```

---

## ⚡ Quick Reference

### Comandos Essenciais

```bash
# Backend - Validação completa
cd backend
black . && ruff check . --fix && mypy . && pytest --cov

# Frontend - Validação completa
cd interfaces/web
npm run lint --fix && npm run test:coverage && npm run build

# Pre-commit - Validar antes de commit
pre-commit run --all-files

# Docker - Build e test local
cd docker
docker-compose build
docker-compose up -d
curl http://localhost:8000/health
```

### Atalhos Recomendados

**VS Code** (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

## 🚨 Violações Comuns e Como Evitar

### ❌ Commitar Secrets
```python
# ERRADO ❌
API_KEY = "sk-1234567890abcdef"

# CERTO ✅
import os
API_KEY = os.getenv("OPENAI_API_KEY")
```

### ❌ Código Sem Testes
```python
# ERRADO ❌
def calculate_total(items):
    return sum(items)

# (sem testes)

# CERTO ✅
def calculate_total(items):
    return sum(items)

# tests/test_calculations.py
def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6
    assert calculate_total([]) == 0
```

### ❌ Type Hints Faltando
```python
# ERRADO ❌
def process_data(data, limit):
    return data[:limit]

# CERTO ✅
def process_data(data: list[str], limit: int) -> list[str]:
    return data[:limit]
```

### ❌ Commit Messages Ruins
```bash
# ERRADO ❌
git commit -m "fix"
git commit -m "updates"
git commit -m "WIP"

# CERTO ✅
git commit -m "fix: corrigir validação de email no formulário de cadastro"
git commit -m "feat: adicionar filtro de tarefas por Big Rock"
git commit -m "docs: atualizar README com instruções de deploy"
```

---

## 📖 Leitura Obrigatória

### Para Todos
- [ ] [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] [The Twelve-Factor App](https://12factor.net/)
- [ ] Clean Code (Robert C. Martin) - Capítulos 1-3

### Backend
- [ ] [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [ ] [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [ ] [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)

### Frontend
- [ ] [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [ ] [Web Content Accessibility Guidelines (WCAG) 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [ ] [Airbnb React/JSX Style Guide](https://github.com/airbnb/javascript/tree/master/react)

### Segurança
- [ ] [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [ ] [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

---

## 🤝 Contribuindo para os Padrões

Estes padrões são **vivos e evoluem** com o projeto.

### Como Propor Mudanças

1. Abrir issue com label `standards`
2. Descrever problema e solução proposta
3. Discussão com time
4. PR atualizando documentação
5. Aprovação e merge

### Processo de Aprovação

- Mudanças menores: 1 aprovação
- Mudanças significativas: 2 aprovações + discussão
- Breaking changes: Consenso do time + migration guide

---

## 📞 Dúvidas e Suporte

**Dúvidas sobre padrões?**
- Abra issue com label `question`
- Consulte os documentos específicos
- Pergunte em code review

**Encontrou violação?**
- Abra issue com label `quality`
- Sugira melhoria
- Contribua com fix

---

## ✅ Checklist de Onboarding

Todo novo desenvolvedor deve:

- [ ] Ler este documento completo
- [ ] Ler todos os 7 documentos de padrões
- [ ] Configurar ambiente local com ferramentas
- [ ] Instalar pre-commit hooks
- [ ] Fazer commit de teste
- [ ] Abrir PR de teste (pode ser só documentação)
- [ ] Participar de code review

---

## 📊 Status dos Padrões no Projeto

| Padrão | Documentado | Implementado | Enforced (CI/CD) |
|--------|-------------|--------------|------------------|
| Backend Standards | ✅ | ⚠️ Parcial | ❌ |
| Frontend Standards | ✅ | ✅ | ⚠️ Parcial |
| Git Standards | ✅ | ✅ | ❌ |
| Testing Standards | ✅ | ⚠️ Frontend only | ⚠️ Parcial |
| Security Standards | ✅ | ⚠️ Básico | ❌ |
| Code Review | ✅ | ⚠️ Manual | ❌ |
| CI/CD | ✅ | ❌ | ❌ |

**Meta**: Todos com ✅ em 3 meses.

---

## 🎯 Próximos Passos

### Semana 1
- [ ] Implementar CI/CD básico
- [ ] Configurar pre-commit hooks
- [ ] Adicionar linting ao pipeline

### Semana 2-3
- [ ] Adicionar testes backend (target 60%)
- [ ] Configurar security scanning
- [ ] Documentar processo de code review

### Mês 2
- [ ] Atingir 80% coverage backend
- [ ] Implementar testes E2E
- [ ] Automatizar deploy

---

**Última atualização:** 2025-11-10
**Responsável:** Samara Cassie
**Revisão:** Trimestral ou quando necessário

---

> "Quality is not an act, it is a habit." - Aristotle

**Vamos construir o Charlee com excelência! 🚀**
