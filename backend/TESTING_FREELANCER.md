# 🧪 Testing Freelancer System Without Frontend

Este guia mostra **5 formas diferentes** de testar todo o sistema freelancer **sem precisar do frontend**.

---

## 📋 Quick Reference

| Método | Dificuldade | Setup Time | Ideal Para |
|--------|------------|-----------|-----------|
| 1. Testes Automatizados | ⭐ Fácil | 1 min | Validação rápida de funcionalidade |
| 2. **Postman Collection** 🆕 | ⭐ Fácil | 2 min | **Testes realistas via GUI** |
| 3. Script Python Interativo | ⭐⭐ Médio | 2 min | Demonstração didática do sistema |
| 4. REST API (cURL/Bash) | ⭐⭐ Médio | 5 min | Testes via terminal |
| 5. Jupyter Notebook | ⭐⭐⭐ Avançado | 5 min | Exploração interativa e análise |
| 6. Python REPL | ⭐ Fácil | 30 seg | Testes rápidos ad-hoc |

**🎯 Recomendado para começar:** Postman Collection (método #2) - mais visual e interativo!

---

## 🆕 NOVO: Postman Collection

**Criamos uma coleção Postman completa para você!**

📁 **Arquivos:**
- `postman_collection_freelancer.json` - Coleção com 40+ requests
- `postman_environment_local.json` - Environment pré-configurado
- `POSTMAN_GUIDE.md` - Guia completo de uso

**Import em 3 passos:**
1. Abra Postman → **Import** → Arraste `postman_collection_freelancer.json`
2. **Import** → Arraste `postman_environment_local.json`
3. Selecione environment **Charlee - Local Development**

**Veja o guia completo:** [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)

---

## 1. ⚡ Testes Automatizados (Mais Rápido)

**Vantagens:** Já existem 81+ testes prontos, execução rápida, validação automática
**Desvantagens:** Menos interativo, não mostra valores reais

### Como Usar

```bash
# Navegar para o backend
cd /home/sam-cassie/GitHub/Charlee/backend

# Instalar dependências (se necessário)
pip install pytest pytest-cov fakeredis

# Rodar TODOS os testes do freelancer
pytest tests/test_freelancer_mvp.py tests/test_learning_components.py -v

# Rodar testes específicos
pytest tests/test_freelancer_mvp.py::TestDuplicationPrevention -v
pytest tests/test_freelancer_mvp.py::TestFinancialCalculator -v
pytest tests/test_learning_components.py::TestPricingLearner -v

# Com relatório de cobertura
pytest tests/test_freelancer_mvp.py tests/test_learning_components.py \
    --cov=services.freelancer \
    --cov-report=html \
    --cov-report=term

# Abrir relatório HTML
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
```

### Testes Disponíveis

**MVP Requirements (36 testes):**
- ✅ RN09: Duplication Prevention (6 testes)
- ✅ RN10: Rate Limiting (8 testes)
- ✅ RN11: Financial Calculator (7 testes)
- ✅ RN12: Client Risk Assessment (8 testes)
- ✅ RN13: LGPD Compliance (7 testes)

**Learning Components (30 testes):**
- ✅ PricingLearner (9 testes)
- ✅ RejectionPatternLearner (8 testes)
- ✅ HourlyRateOptimizer (8 testes)
- ✅ Integration (1 teste)

---

## 2. 🐍 Script Python Interativo (Mais Didático)

**Vantagens:** Mostra valores reais, fácil de entender, didático
**Desvantagens:** Precisa de database configurado

### Como Usar

```bash
# 1. Certifique-se que o banco está rodando
docker-compose up -d postgres redis

# 2. Execute o script
cd /home/sam-cassie/GitHub/Charlee/backend
python3 scripts/test_freelancer_interactive.py
```

### O que o Script Testa

```
========================================
  🚀 Freelancer System Interactive Testing
========================================

1. RN09: Duplication Prevention
   - Cria oportunidade de teste
   - Testa detecção de duplicatas
   - Mostra threshold de similaridade

2. RN11: Financial Calculator
   - Converte USD → BRL
   - Calcula impostos brasileiros
   - Mostra breakdown detalhado

3. RN12: Client Risk Assessment
   - Avalia cliente high-risk
   - Avalia cliente low-risk
   - Compara scores e flags

4. PricingLearner
   - Analisa performance de precificação
   - Mostra accuracy score
   - Sugere ajustes

5. RejectionPatternLearner
   - Analisa padrões de rejeição
   - Identifica high-risk flags
   - Detecta false positives

6. HourlyRateOptimizer
   - Analisa acceptance rate por faixa
   - Identifica sweet spot
   - Sugere ajuste de taxa

7. Integration Service
   - Testa pipeline completo
   - Mostra orquestração de serviços
```

**Output Esperado:**

```
========================================
  🧩 RN09: Duplication Prevention
========================================

✓ Created opportunity: Python Backend API Development
✓ Duplicate detection: True
  Similarity threshold: 70.0% (Jaccard index)

========================================
  💰 RN11: Financial Calculator
========================================

✓ Gross (USD): $5000.0
✓ Exchange rate: R$ 5.75
✓ Gross (BRL): R$ 28750.0
✓ Platform fee (Upwork 10%): R$ 2875.0
✓ Simples Nacional tax: R$ 1725.0
✓ Net income (BRL): R$ 24150.0
✓ Effective tax rate: 16.00%
```

---

## 3. 🌐 REST API Testing (Mais Realista)

**Vantagens:** Testa endpoints reais, simula frontend, usa autenticação
**Desvantagens:** Precisa backend rodando, precisa token JWT

### Setup

```bash
# 1. Inicie o backend
cd /home/sam-cassie/GitHub/Charlee/backend
python3 -m uvicorn main:app --reload

# 2. Em outro terminal, obtenha token JWT
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@charlee.ai", "password": "test123"}'

# 3. Copie o token retornado
```

### Opção A: cURL (Terminal)

```bash
# Edite o script com seu token
nano backend/scripts/test_freelancer_api.sh

# Linha 11: TOKEN="cole_seu_token_aqui"

# Execute
./backend/scripts/test_freelancer_api.sh
```

### Opção B: Postman (GUI)

1. **Importe coleção:**
   - Abra Postman
   - File > Import > Raw Text
   - Cole os comandos do script `test_freelancer_api.sh`

2. **Configure autenticação:**
   - Create Environment: `Charlee Local`
   - Add variable: `token` = `seu_jwt_token`
   - Add variable: `base_url` = `http://localhost:8000`

3. **Execute requests:**
   - Test Duplication Prevention
   - Test Risk Assessment
   - Test Financial Calculator
   - Test Learning Components

### Opção C: Swagger UI (Navegador)

```bash
# 1. Backend rodando
python3 -m uvicorn main:app --reload

# 2. Abra no navegador
http://localhost:8000/docs

# 3. Clique em "Authorize"
# 4. Cole seu JWT token
# 5. Teste endpoints interativamente
```

### Endpoints Disponíveis

```
POST   /api/v1/opportunities                    # Cria oportunidade
GET    /api/v1/opportunities                    # Lista oportunidades
POST   /api/v1/opportunities/check-duplicate    # Verifica duplicata

POST   /api/v1/risk/assess                      # Avalia risco do cliente

POST   /api/v1/financial/calculate              # Calcula income líquido

GET    /api/v1/learning/pricing/performance     # Performance de precificação
GET    /api/v1/learning/pricing/suggest         # Sugere ajustes

GET    /api/v1/learning/rejection/patterns      # Padrões de rejeição
GET    /api/v1/learning/rejection/weights       # Sugere pesos de red flags

GET    /api/v1/learning/rate/analyze            # Analisa acceptance por rate
GET    /api/v1/learning/rate/suggest            # Sugere ajuste de taxa

POST   /api/v1/integration/process-opportunity  # Pipeline completo
```

---

## 4. 📓 Jupyter Notebook (Mais Exploratório)

**Vantagens:** Interativo, visualizações, análise de dados
**Desvantagens:** Precisa instalar Jupyter, mais setup

### Setup

```bash
# 1. Instalar Jupyter
pip install jupyter pandas

# 2. Iniciar Jupyter
cd /home/sam-cassie/GitHub/Charlee/backend
jupyter notebook

# 3. Abrir notebook
# No navegador: notebooks/test_freelancer_system.ipynb
```

### O que o Notebook Oferece

- **Cell-by-cell execution:** Execute código passo a passo
- **Visualizações:** DataFrames do pandas para comparar resultados
- **Documentação inline:** Markdown cells explicando cada teste
- **Exploração interativa:** Modifique parâmetros e re-execute

### Exemplo de Uso

```python
# Cell 1: Setup
from services.freelancer import ClientRiskAssessment
risk_service = ClientRiskAssessment(db, user_id=1)

# Cell 2: Test high-risk client
high_risk = risk_service.assess_risk(
    client_rating=2.5,
    client_projects_count=2,
    project_description="Need ASAP! Cheapest option!",
)

# Cell 3: Visualize results
import pandas as pd
df = pd.DataFrame([{
    "Risk Score": f"{high_risk['risk_score']:.1f}/10",
    "Risk Level": high_risk['risk_level'],
    "Red Flags": len(high_risk['red_flags']),
    "Recommendation": high_risk['recommendation'],
}])
df
```

---

## 5. 🔧 Python REPL (Mais Ad-hoc)

**Vantagens:** Sem setup, testes rápidos, debugging
**Desvantagens:** Sem persistência, precisa conhecer API

### Como Usar

```bash
# 1. Abra Python REPL
cd /home/sam-cassie/GitHub/Charlee/backend
python3

# 2. No REPL
>>> from database.connection import SessionLocal
>>> from services.freelancer import FreelancerFinancialCalculator
>>>
>>> db = SessionLocal()
>>> calc = FreelancerFinancialCalculator(db, user_id=1)
>>>
>>> result = calc.calculate_net_income(
...     gross_usd=5000.0,
...     platform="upwork",
...     tax_regime="simples_nacional",
... )
>>>
>>> print(f"Gross: ${result['gross_usd']}")
>>> print(f"Net (BRL): R$ {result['net_brl']}")
>>>
>>> db.close()
```

---

## 🎯 Comparação de Métodos

### Para Validação Rápida
**Use:** Testes Automatizados (pytest)
**Comando:** `pytest tests/test_freelancer_mvp.py -v`

### Para Entender o Sistema
**Use:** Script Python Interativo
**Comando:** `python3 scripts/test_freelancer_interactive.py`

### Para Testes Realistas
**Use:** REST API (Postman/cURL/Swagger)
**Comando:** `./scripts/test_freelancer_api.sh`

### Para Análise de Dados
**Use:** Jupyter Notebook
**Comando:** `jupyter notebook notebooks/test_freelancer_system.ipynb`

### Para Debugging Rápido
**Use:** Python REPL
**Comando:** `python3` → import services

---

## 📚 Documentação Relacionada

- **Implementação completa:** [docs/implementacao/freelancer-complete.md](../docs/implementacao/freelancer-complete.md)
- **Planejamento do módulo:** [docs/modulos-planejados/gestao-projetos-freelancers.md](../docs/modulos-planejados/gestao-projetos-freelancers.md)
- **Standards de qualidade:** [docs/qualidade/](../docs/qualidade/)

---

## ❓ FAQ

### P: Preciso do frontend rodando?
**R:** Não! Todos os métodos acima funcionam sem frontend.

### P: Preciso de dados reais?
**R:** Não. Os testes usam fixtures e dados mock. Para testes mais realistas, você pode popular o banco manualmente.

### P: Como adiciono dados de teste?
**R:** Use o script Python interativo ou Jupyter notebook para criar oportunidades, execuções, etc.

### P: Qual método é mais rápido?
**R:** Testes automatizados (pytest) - execução em ~5 segundos.

### P: Qual método é mais didático?
**R:** Script Python interativo - mostra valores reais e explicações.

### P: Como testo os 7 agentes?
**R:** Os agentes estão em `agent/specialized_agents/projects/`. Use REST API para testá-los ou veja a documentação em `freelancer-complete.md`.

---

## 🚀 Next Steps

1. **Execute os testes automatizados** para validar funcionalidade
2. **Rode o script interativo** para ver valores reais
3. **Teste via REST API** para simular frontend
4. **Explore no Jupyter** para análise de dados
5. **Leia a documentação** em `freelancer-complete.md`

---

**Desenvolvido com ❤️ para facilitar testes sem frontend**
