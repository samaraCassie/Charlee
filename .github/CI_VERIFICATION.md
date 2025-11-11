# 🔍 Como Verificar o Status do CI

Este documento explica como verificar se seus commits vão passar no CI **antes** de fazer o merge.

---

## 🚀 Método 1: Script Automático (Recomendado)

Execute o script na raiz do projeto:

```bash
./check-ci.sh
```

Este script verifica localmente:
- ✅ Backend: Black, Ruff, MyPy
- ✅ Backend: 90 testes
- ✅ Frontend: ESLint, TypeScript
- ✅ Frontend: 71 testes

**Saída esperada se tudo estiver OK:**
```
✅ Todos os checks passaram! Pronto para merge 🚀
```

---

## 🖥️ Método 2: Verificar no GitHub (Interface Web)

### Opção A: Via Pull Request

1. Acesse seu PR no GitHub:
   ```
   https://github.com/samaraCassie/Charlee/pulls
   ```

2. Procure por ícones de status:
   - ✅ **Verde** = Todos os checks passaram
   - ❌ **Vermelho** = Alguns checks falharam
   - 🟡 **Amarelo** = Checks em execução
   - ⚪ **Cinza** = Checks não iniciados

3. Clique em "Details" para ver logs detalhados de cada check

### Opção B: Via Commits

1. Vá para a aba "Commits" no GitHub:
   ```
   https://github.com/samaraCassie/Charlee/commits/your-branch
   ```

2. Cada commit mostra o status ao lado:
   - ✅ = Passou
   - ❌ = Falhou
   - 🟡 = Em execução

---

## 🔧 Método 3: Comandos Individuais

Execute cada check separadamente:

### Backend - Linting
```bash
cd backend

# Black (formatação)
python -m black --check .

# Ruff (linting)
python -m ruff check .

# MyPy (type checking)
python -m mypy . --ignore-missing-imports
```

### Backend - Tests
```bash
cd backend

# Configurar ambiente
export DATABASE_URL="sqlite:///:memory:"
export REDIS_URL="redis://localhost:6379"
export OPENAI_API_KEY="sk-test-key"
export SECRET_KEY="test-secret"
export RATE_LIMIT_ENABLED=false
export LOG_LEVEL=ERROR

# Rodar testes
pytest tests/ -v --cov=. --cov-report=term
```

### Frontend - Linting
```bash
cd interfaces/web

# ESLint
npm run lint

# TypeScript build
npm run build
```

### Frontend - Tests
```bash
cd interfaces/web

# Testes com coverage
npm run test:coverage
```

---

## 📊 Método 4: GitHub CLI

Se você tem o `gh` CLI instalado:

```bash
# Ver status do último commit
gh run list --branch your-branch-name --limit 1

# Ver detalhes de uma run específica
gh run view RUN_ID

# Ver logs de um job específico
gh run view RUN_ID --log --job JOB_ID

# Watch em tempo real
gh run watch
```

**Exemplo:**
```bash
# Ver runs da branch atual
gh run list --branch claude/create-project-status-doc-011CUzNycUNpPbvKChQJYy7m

# Ver última run
gh run view

# Assistir run em andamento
gh run watch
```

---

## 🎯 Método 5: Git Hooks (Automático)

Configure pre-push hooks para verificar antes de cada push:

### Instalar pre-commit
```bash
pip install pre-commit
```

### Configurar hook
Já está configurado em `.pre-commit-config.yaml`

### Ativar
```bash
pre-commit install
```

Agora, toda vez que você fizer `git push`, os checks rodarão automaticamente!

---

## 📋 Checklist Rápido

Antes de criar/atualizar um PR, verifique:

- [ ] `./check-ci.sh` passou localmente
- [ ] Todos os arquivos foram commitados
- [ ] Push foi feito para o remote
- [ ] PR foi criado/atualizado no GitHub
- [ ] Aguardou 2-5 minutos para os checks rodarem
- [ ] Verificou status no GitHub (ícones verdes)

---

## 🐛 Troubleshooting

### "Script falhou mas não sei qual arquivo"

Execute os comandos individuais (Método 3) para ver output detalhado.

### "CI passou localmente mas falhou no GitHub"

Possíveis causas:
1. **Dependências diferentes**: CI usa `npm ci` (versões exatas do lock file)
2. **Arquivos não commitados**: Esqueceu de adicionar algum arquivo
3. **Variáveis de ambiente**: CI usa PostgreSQL real, local usa SQLite

### "MyPy sempre tem warnings"

É normal! O workflow tem `continue-on-error: true` para MyPy, então não bloqueia o merge.

### "Testes passam localmente mas falham no CI"

1. Limpe o cache local:
   ```bash
   # Backend
   rm -rf backend/.pytest_cache backend/__pycache__

   # Frontend
   rm -rf interfaces/web/node_modules/.cache
   ```

2. Reinstale dependências:
   ```bash
   # Backend
   cd backend && pip install -r requirements-dev.txt

   # Frontend
   cd interfaces/web && npm ci
   ```

---

## 🎓 Boas Práticas

1. **Sempre rode `./check-ci.sh` antes de push**
2. **Commit com frequência** (pequenos commits são mais fáceis de debugar)
3. **Aguarde CI passar** antes de pedir review
4. **Não faça force push** após CI iniciar (cancela os checks)
5. **Use mensagens descritivas** nos commits para facilitar debug

---

## 📚 Referências

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub CLI Docs](https://cli.github.com/manual/)
- [Pre-commit Hooks](https://pre-commit.com/)

---

**💡 Dica:** Adicione este alias no seu `.bashrc` ou `.zshrc`:

```bash
alias ci-check='./check-ci.sh'
```

Agora você pode rodar apenas `ci-check` de qualquer lugar no projeto! 🚀
