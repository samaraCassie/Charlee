# 🔍 CI Pre-Check - Como verificar antes de fazer push

Este guia mostra como verificar se seu código passará no CI do GitHub Actions **antes** de fazer push.

## 🚀 Uso Rápido

```bash
cd backend
./check-ci.sh
```

Esse script executa **exatamente os mesmos checks** que o GitHub Actions CI executará.

## 📋 O que é verificado?

### ✅ Checks Obrigatórios (devem passar)

1. **Black (formatação)**
   - Verifica se o código está formatado corretamente
   - Para corrigir: `python -m black .`

2. **Ruff (linting)**
   - Verifica erros de estilo e código
   - Para ver erros: `python -m ruff check .`
   - Para corrigir alguns automaticamente: `python -m ruff check --fix .`

3. **Pytest (testes)**
   - Executa todos os testes
   - Para rodar: `python -m pytest tests/ -v`

### ⚠️ Checks Opcionais (não bloqueiam)

4. **MyPy (type checking)**
   - Verifica tipos estáticos
   - Configurado como `continue-on-error` no CI
   - Para rodar: `python -m mypy . --ignore-missing-imports`

## 🛠️ Comandos Individuais

Se quiser rodar cada check separadamente:

### 1. Formatação (Black)

```bash
# Verificar formatação
python -m black --check --diff .

# Aplicar formatação automaticamente
python -m black .
```

### 2. Linting (Ruff)

```bash
# Verificar problemas
python -m ruff check .

# Corrigir automaticamente (quando possível)
python -m ruff check --fix .

# Ver lista de regras violadas
python -m ruff check --statistics .
```

### 3. Testes (Pytest)

```bash
# Todos os testes
python -m pytest tests/ -v

# Testes de um arquivo específico
python -m pytest tests/test_api/test_auth.py -v

# Parar no primeiro erro
python -m pytest tests/ -v -x

# Com cobertura
python -m pytest tests/ -v --cov=. --cov-report=term

# Testes rápidos (apenas API)
python -m pytest tests/test_api/ -v
```

### 4. Type Checking (MyPy - opcional)

```bash
# Verificar tipos
python -m mypy . --ignore-missing-imports
```

## 🎯 Workflow Recomendado

### Antes de cada commit:

```bash
# 1. Formatar código
python -m black .

# 2. Verificar linting
python -m ruff check .

# 3. Rodar testes rápidos
python -m pytest tests/test_api/ -v
```

### Antes de fazer push:

```bash
# Verificar tudo de uma vez
./check-ci.sh
```

## 🔧 Troubleshooting

### Script não executa

```bash
# Tornar executável
chmod +x check-ci.sh
```

### Erro "No module named pytest"

```bash
# Instalar dependências
pip install -r requirements-dev.txt
```

### Ambiente virtual não ativado

```bash
# Ativar venv
source venv/bin/activate
```

### Muitos erros de formatação

```bash
# Deixar o Black corrigir automaticamente
python -m black .
```

## 📊 Entendendo o Output

### ✅ Sucesso
```
✅ SUCESSO! Seu código deve passar no CI do GitHub Actions

Próximos passos:
  1. git add .
  2. git commit -m 'sua mensagem'
  3. git push
```

### ❌ Falha
```
❌ FALHOU! Corrija os erros acima antes de fazer push

Dicas:
  - Para formatar automaticamente: python -m black .
  - Para ver erros do Ruff: python -m ruff check .
  - Para rodar um teste específico: python -m pytest tests/caminho/para/teste.py -v
```

## 🎨 Configurações dos Tools

### Black (`.black` ou `pyproject.toml`)
- Line length: 100
- Target version: Python 3.12

### Ruff (`.ruff.toml` ou `pyproject.toml`)
- Select: E, F, W, I, N
- Ignore: E501 (line too long)

### Pytest (`pytest.ini`)
- Testpaths: tests/
- Verbosity: -v
- Coverage config: `.coveragerc`

## 💡 Dicas Pro

### Pre-commit Hook

Crie `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd backend
python -m black --check . && python -m ruff check .
```

### Alias úteis

Adicione ao seu `.bashrc` ou `.zshrc`:

```bash
alias ci-check='cd backend && ./check-ci.sh'
alias fmt='cd backend && python -m black .'
alias lint='cd backend && python -m ruff check .'
alias test='cd backend && python -m pytest tests/ -v'
```

## 📚 Mais Informações

- [Workflow CI completo](.github/workflows/ci.yml)
- [Documentação do Black](https://black.readthedocs.io/)
- [Documentação do Ruff](https://docs.astral.sh/ruff/)
- [Documentação do Pytest](https://docs.pytest.org/)
