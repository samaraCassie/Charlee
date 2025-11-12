# 🔀 Git Standards - Versionamento e Commits

> **Projeto:** Charlee
> **Branching:** Git Flow adaptado
> **Status:** Obrigatório

---

## 📋 Índice

1. [Conventional Commits](#conventional-commits)
2. [Branching Strategy](#branching-strategy)
3. [Pull Request Process](#pull-request-process)
4. [.gitignore Best Practices](#gitignore-best-practices)
5. [Git Hooks](#git-hooks)

---

## 📝 Conventional Commits

### Formato Obrigatório

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types Permitidos

| Type | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova feature | `feat: adicionar filtro de tarefas por status` |
| `fix` | Bug fix | `fix: corrigir validação de email no formulário` |
| `docs` | Apenas documentação | `docs: atualizar README com instruções de deploy` |
| `style` | Formatação, sem mudança de código | `style: formatar código com black` |
| `refactor` | Refactoring sem fix/feature | `refactor: simplificar lógica de priorização` |
| `perf` | Melhoria de performance | `perf: otimizar query de tarefas` |
| `test` | Adicionar/corrigir testes | `test: adicionar testes para orquestrador` |
| `chore` | Manutenção, deps | `chore: atualizar dependências` |
| `ci` | Mudanças em CI/CD | `ci: adicionar workflow de testes` |
| `build` | Build system, deps | `build: atualizar configuração do Vite` |
| `revert` | Reverter commit anterior | `revert: reverter "feat: novo filtro"` |

### Scope (Opcional mas Recomendado)

```bash
feat(backend): adicionar endpoint de analytics
fix(frontend): corrigir bug no TaskCard
docs(api): documentar endpoint de Big Rocks
test(stores): adicionar testes para taskStore
```

### Subject Rules

```bash
# ✅ CERTO
feat: adicionar filtro de tarefas por deadline
fix: corrigir cálculo de capacidade
docs: atualizar guia de contribuição

# ❌ ERRADO
feat: Adicionar filtro  # ← Não capitalize
fix: corrigir bug.      # ← Sem pontuação final
feat: added filter      # ← Usar imperativo (add, não added)
fix                     # ← Muito vago
```

**Regras do Subject**:
- ✅ Imperativo ("add", não "added" ou "adds")
- ✅ Minúscula no início
- ✅ Sem ponto final
- ✅ Máximo 72 caracteres
- ✅ Descritivo e claro

### Body (Opcional mas Recomendado)

```bash
git commit -m "feat: adicionar sistema de notificações

Implementa sistema de notificações push para:
- Lembretes de tarefas
- Alertas de capacidade
- Updates de Big Rocks

Usa Firebase Cloud Messaging para delivery.

Closes #42"
```

### Footer

```bash
# Referências
Closes #123
Fixes #456
Refs #789

# Breaking changes
BREAKING CHANGE: campo 'priority' agora é string ('low', 'medium', 'high')

# Reviewed by
Reviewed-by: Samara Cassie <samara@example.com>
```

### Exemplos Completos

```bash
# Feature simples
git commit -m "feat(tasks): adicionar filtro por Big Rock"

# Fix com contexto
git commit -m "fix(auth): corrigir validação de token expirado

O token estava sendo aceito mesmo após expiração.
Adiciona verificação de timestamp antes de validar.

Fixes #234"

# Breaking change
git commit -m "feat(api)!: alterar formato de resposta de tarefas

BREAKING CHANGE: O endpoint /api/v1/tarefas agora retorna
{ data: [], total: N } em vez de array direto.

Migração: wrapper response.data em consumers.

Closes #567"

# Revert
git commit -m "revert: reverter 'feat: adicionar filtro complexo'

Reverte commit 1234abc.
Feature causando performance issues em produção."
```

---

## 🌳 Branching Strategy

### Branch Principal

```
main  ← Branch de produção, sempre deployável
```

### Branch de Desenvolvimento

```
develop  ← Branch de desenvolvimento, integração contínua
```

### Feature Branches

```bash
# Nomenclatura
feat/nome-da-feature
feat/filtro-tarefas
feat/google-calendar-integration
feat/agent-orchestration

# Criar e trabalhar
git checkout -b feat/minha-feature develop
# ... fazer commits ...
git push -u origin feat/minha-feature
# Abrir PR para develop
```

### Fix Branches

```bash
# Nomenclatura
fix/nome-do-bug
fix/email-validation
fix/capacity-calculation

# Criar
git checkout -b fix/meu-bug develop
```

### Hotfix Branches (Produção)

```bash
# Para bugs críticos em produção
hotfix/critical-bug

# Criar a partir de main
git checkout -b hotfix/security-patch main

# Mergear em main E develop
git checkout main
git merge --no-ff hotfix/security-patch
git checkout develop
git merge --no-ff hotfix/security-patch
```

### Release Branches

```bash
# Preparar release
git checkout -b release/v3.2.0 develop

# Bump version, changelog, etc.
# Mergear em main e develop

git checkout main
git merge --no-ff release/v3.2.0
git tag -a v3.2.0 -m "Release v3.2.0"

git checkout develop
git merge --no-ff release/v3.2.0
```

### Diagrama de Fluxo

```
main ─────●─────────●─────────●──────► (produção)
          │         │         │
          │    release/v3.1   │
          │         │         │
develop ──┴─●─●─●─●─┴─●─●─●─●─┴──────► (dev)
            │   │     │   │
        feat/A  │  feat/B │
                │         │
            fix/C      fix/D
```

---

## 🔍 Pull Request Process

### Template de PR

```markdown
## 📝 Descrição

Breve descrição do que este PR faz.

## 🎯 Motivação e Contexto

Por que esta mudança é necessária? Que problema resolve?

Closes #123

## 🧪 Como foi testado?

- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais
- [ ] Testado no navegador X, Y, Z

## 📸 Screenshots (se aplicável)

[Adicionar screenshots]

## ✅ Checklist

- [ ] Meu código segue os padrões do projeto
- [ ] Revisei meu próprio código
- [ ] Comentei código complexo
- [ ] Atualizei documentação
- [ ] Não introduzi warnings
- [ ] Adicionei testes
- [ ] Testes passam localmente
- [ ] Mudanças dependentes foram mergeadas

## 🔗 Issues Relacionadas

- #123
- #456
```

### Regras de PR

**Obrigatório**:
- ✅ Título descritivo (Conventional Commits)
- ✅ Descrição completa (use template)
- ✅ Pelo menos 1 reviewer
- ✅ CI/CD verde
- ✅ Sem merge conflicts
- ✅ Branch atualizada com target

**Proibido**:
- ❌ Auto-merge (sem aprovação)
- ❌ Mergear com CI failing
- ❌ PRs gigantes (> 500 linhas)
- ❌ Mergear com comentários não resolvidos

### Tamanho de PR

```bash
# ✅ Ideal
100-300 linhas

# ⚠️ Aceitável
300-500 linhas

# ❌ Muito grande - quebrar em PRs menores
> 500 linhas
```

### Review Process

1. **Autor abre PR**
   - Preenche template
   - Adiciona reviewers
   - Linka issues

2. **Reviewers analisam**
   - Código
   - Testes
   - Documentação
   - Segurança

3. **Feedback e Iteração**
   - Comentários
   - Solicitação de mudanças
   - Autor faz updates

4. **Aprovação**
   - Pelo menos 1 aprovação
   - Todos comentários resolvidos
   - CI verde

5. **Merge**
   - Squash merge (preferido)
   - Rebase merge (se histórico importante)
   - Delete branch após merge

### Merge Strategies

```bash
# ✅ Squash Merge (preferido para features)
# Cria 1 commit limpo com todos changes
git merge --squash feat/minha-feature

# ✅ Rebase Merge (se histórico importante)
git rebase develop
git merge --ff-only feat/minha-feature

# ⚠️ Merge Commit (apenas para releases/hotfixes)
git merge --no-ff release/v3.2.0

# ❌ Fast-forward (evitar)
git merge feat/minha-feature
```

---

## 📁 .gitignore Best Practices

### Estrutura Correta

```gitignore
# ============================================
# PYTHON
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtualenv
venv/
env/
ENV/

# ============================================
# NODE / FRONTEND
# ============================================
node_modules/
dist/
build/
.cache/

# ❌ NUNCA ignore package.json ou package-lock.json!
# Eles são essenciais para reproduzir build

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
.env
.env.local
.env.*.local

# ✅ Mantenha .env.example (versionado)

# ============================================
# IDEs
# ============================================
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# ============================================
# TESTING
# ============================================
.pytest_cache/
.coverage
htmlcov/
coverage/

# ❌ NUNCA ignore arquivos de teste!

# ============================================
# LOGS
# ============================================
*.log
logs/

# ============================================
# DATABASE
# ============================================
*.db
*.sqlite3

# ❌ NUNCA ignore migrations!
# !backend/database/migrations/*.py

# ============================================
# TEMPORÁRIOS
# ============================================
*.tmp
*.temp
.cache/
```

### ❌ O QUE NUNCA IGNORAR

```gitignore
# ❌ NUNCA FAÇA ISSO:
package.json          # ← Essencial para deps
package-lock.json
yarn.lock

src/                  # ← Código fonte
backend/api/
components/

README.md             # ← Documentação
docs/

tests/                # ← Testes
__tests__/

Dockerfile            # ← Infra
docker-compose.yml
```

### Verificar .gitignore

```bash
# Ver o que está sendo ignorado
git check-ignore -v *

# Testar padrão específico
git check-ignore -v src/components/Button.tsx

# Forçar adicionar arquivo ignorado (se realmente necessário)
git add -f arquivo-especial.txt
```

---

## 🪝 Git Hooks

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml

repos:
  # Backend - Python
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.11
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # Frontend - TypeScript
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.36.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]

  # Geral
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: detect-private-key  # ← Previne commit de secrets!
```

### Instalar Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Rodar manualmente
pre-commit run --all-files

# Atualizar hooks
pre-commit autoupdate
```

### Commit-msg Hook (Conventional Commits)

```bash
# .git/hooks/commit-msg

#!/bin/bash

# Verificar formato de commit message
commit_msg=$(cat "$1")

# Regex para Conventional Commits
pattern="^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .{1,72}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "❌ Commit message inválido!"
    echo ""
    echo "Formato esperado:"
    echo "  <type>(<scope>): <subject>"
    echo ""
    echo "Exemplos:"
    echo "  feat: adicionar filtro de tarefas"
    echo "  fix(auth): corrigir validação de token"
    echo ""
    exit 1
fi
```

---

## ✅ Checklist de Git

Antes de commitar:

- [ ] Código formatado (black/prettier)
- [ ] Linting passou (ruff/eslint)
- [ ] Testes passando
- [ ] Commit message segue Conventional Commits
- [ ] Sem arquivos desnecessários (node_modules, .env)
- [ ] Sem secrets ou keys
- [ ] Branch atualizada com base

Antes de abrir PR:

- [ ] Branch atualizada com target
- [ ] Sem merge conflicts
- [ ] CI/CD passando
- [ ] Template de PR preenchido
- [ ] Reviewers adicionados
- [ ] Issues linkadas

---

**Última atualização:** 2025-11-10
