# Guia de Contribuição - Charlee

Obrigado por contribuir com o Charlee! Este guia ajudará você a configurar o ambiente e seguir nossos padrões de qualidade.

## 🚀 Setup Rápido

### 1. Clone e Configure

```bash
git clone https://github.com/samaraCassie/Charlee.git
cd Charlee

# Configure variáveis de ambiente
cp docker/.env.example docker/.env
# Edite docker/.env com suas API keys
```

### 2. Instale Dependências de Desenvolvimento

#### Backend
```bash
cd backend
pip install -r requirements-dev.txt
```

#### Frontend
```bash
cd interfaces/web
npm install
```

### 3. Configure Pre-commit Hooks

```bash
# Na raiz do projeto
pip install pre-commit
pre-commit install

# Teste (opcional)
pre-commit run --all-files
```

## 📝 Padrões de Código

### Leia a Documentação de Padrões

Antes de contribuir, leia:
- **[QUALITY_STANDARDS.md](QUALITY_STANDARDS.md)** - Índice principal
- **[standards/BACKEND_STANDARDS.md](standards/BACKEND_STANDARDS.md)** - Python/FastAPI
- **[standards/FRONTEND_STANDARDS.md](standards/FRONTEND_STANDARDS.md)** - React/TypeScript
- **[standards/GIT_STANDARDS.md](standards/GIT_STANDARDS.md)** - Git e commits

### Ferramentas Obrigatórias

Antes de cada commit, rode:

```bash
# Backend
cd backend
black .
ruff check . --fix
mypy .
pytest

# Frontend
cd interfaces/web
npm run lint --fix
npm run test
```

**Ou deixe o pre-commit fazer automaticamente!**

## 🧪 Testes

### Backend

```bash
cd backend

# Todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Coverage mínimo: 80%
pytest --cov=. --cov-fail-under=80
```

### Frontend

```bash
cd interfaces/web

# Todos os testes
npm run test

# Com coverage
npm run test:coverage

# Coverage mínimo: 80%
```

## 🔀 Workflow de Git

### 1. Criar Branch

```bash
# Para features
git checkout -b feat/nome-da-feature

# Para bugs
git checkout -b fix/nome-do-bug
```

### 2. Fazer Commits

**Formato obrigatório** (Conventional Commits):

```bash
<type>(<scope>): <subject>

# Exemplos:
git commit -m "feat: adicionar filtro de tarefas por status"
git commit -m "fix(auth): corrigir validação de token"
git commit -m "docs: atualizar README com instruções"
```

**Types permitidos**:
- `feat`: Nova feature
- `fix`: Bug fix
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refactoring
- `test`: Testes
- `chore`: Manutenção

### 3. Push e Pull Request

```bash
git push -u origin feat/minha-feature
```

Então abra PR no GitHub com:
- Título descritivo
- Descrição completa (use template)
- Link para issues relacionadas
- Screenshots se aplicável

## ✅ Checklist Antes de Abrir PR

- [ ] Código formatado (black/prettier)
- [ ] Linting sem warnings (ruff/eslint)
- [ ] Type checking passou (mypy)
- [ ] Testes passando
- [ ] Coverage >= 80%
- [ ] Documentação atualizada
- [ ] Commit messages seguem Conventional Commits
- [ ] Sem secrets/senhas no código
- [ ] Branch atualizada com base (main/develop)

## 🚨 O Que NÃO Fazer

### ❌ NUNCA commite:
- Senhas ou API keys
- Arquivos `.env`
- Chaves privadas
- Tokens de acesso
- Dados pessoais

### ❌ NUNCA ignore regras de qualidade:
- Pre-commit hooks
- Testes falhando
- Warnings de linting
- Type errors

### ❌ NUNCA faça PRs gigantes:
- Máximo 500 linhas
- Se maior, quebrar em múltiplos PRs

## 🎯 Tipos de Contribuição

### 🐛 Reportar Bug

1. Verifique se já não existe issue
2. Abra issue com template de bug
3. Inclua:
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots se aplicável
   - Ambiente (OS, versões)

### ✨ Propor Feature

1. Abra issue descrevendo a feature
2. Aguarde discussão e aprovação
3. Siga o workflow de desenvolvimento

### 📖 Melhorar Documentação

Documentação sempre bem-vinda!
- README
- Comentários de código
- Docstrings
- Guias e tutoriais

## 💬 Comunicação

### Code Review

Ao fazer review:
- Seja construtivo e respeitoso
- Sugira melhorias claramente
- Aprove apenas se confiante
- Use emojis de prioridade:
  - 🔴 BLOQUEANTE
  - 🟡 IMPORTANTE
  - 🟢 NITPICK

### Feedback em Issues

- Use linguagem clara e objetiva
- Seja cortês
- Forneça contexto
- Inclua exemplos quando possível

## 🆘 Precisa de Ajuda?

- **Dúvidas técnicas**: Abra issue com label `question`
- **Problemas de setup**: Veja [QUICKSTART.md](backend/QUICKSTART.md)
- **Padrões de código**: Veja [QUALITY_STANDARDS.md](QUALITY_STANDARDS.md)

## 📚 Recursos Úteis

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Obrigado por contribuir! 🙏**

*Toda contribuição, grande ou pequena, é valorizada e apreciada.*
