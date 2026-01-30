# 📮 Guia Postman - Sistema Freelancer

Guia completo para testar o sistema freelancer usando Postman.

---

## 🚀 Setup Rápido (3 passos)

### 1. Importe a Coleção

**Opção A: Import direto do arquivo**
1. Abra Postman
2. Click em **Import** (canto superior esquerdo)
3. Arraste o arquivo `postman_collection_freelancer.json`
4. Click em **Import**

**Opção B: Import via link**
1. No Postman, click em **Import**
2. Selecione **Link**
3. Cole o caminho: `/home/sam-cassie/GitHub/Charlee/backend/postman_collection_freelancer.json`

### 2. Importe o Environment

1. No Postman, click em **Environments** (ícone de olho, canto superior direito)
2. Click em **Import**
3. Selecione o arquivo `postman_environment_local.json`
4. Click em **Import**

### 3. Configure o Environment

1. No dropdown de environments (canto superior direito), selecione **Charlee - Local Development**
2. Click no ícone de olho → **Edit**
3. Verifique as variáveis:
   - `base_url`: `http://localhost:8000` ✓
   - `token`: (vazio por enquanto) ✓
   - `test_email`: `test@charlee.ai` ✓
   - `test_password`: `test123` ✓

---

## 🔑 Obter Token de Autenticação

### Passo 1: Inicie o Backend

```bash
cd /home/sam-cassie/GitHub/Charlee/backend
python3 -m uvicorn main:app --reload
```

### Passo 2: Faça Login no Postman

1. Na coleção **Charlee - Freelancer System API**
2. Abra a pasta **0. Authentication**
3. Click no request **Login**
4. Click em **Send**

**Resultado esperado:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Passo 3: Token Salvo Automaticamente

O script de teste do request **Login** salva o token automaticamente no environment!

Verifique:
1. Click no ícone de olho (environments)
2. Veja que a variável `token` agora tem um valor

---

## 📋 Testando os Módulos

### 1. RN09: Duplication Prevention

**Objetivo:** Prevenir projetos duplicados

**Requests:**
1. **Create Opportunity #1** - Cria primeira oportunidade
2. **Check Duplicate (Should Detect)** - Deve detectar como duplicata (>70% similaridade)
3. **Check Non-Duplicate** - Não deve detectar (projeto diferente)

**O que esperar:**
```json
{
  "is_duplicate": true,
  "similarity_score": 0.85,
  "similar_opportunities": [
    {
      "id": 1,
      "title": "Python Backend API Development",
      "similarity": 0.85
    }
  ]
}
```

---

### 2. RN11: Financial Calculator

**Objetivo:** Calcular income líquido (USD→BRL + impostos brasileiros)

**Requests:**
1. **Calculate Net Income (Upwork + Simples Nacional)** - Taxa Upwork 10% + Simples 6%
2. **Calculate Net Income (Freelancer.com + MEI)** - Taxa Freelancer 15% + MEI fixo
3. **Calculate Net Income (Toptal + Lucro Presumido)** - Sem taxa plataforma + LP 13.33%

**O que esperar:**
```json
{
  "gross_usd": 5000.0,
  "exchange_rate": 5.75,
  "gross_brl": 28750.0,
  "net_brl": 24150.0,
  "effective_tax_rate": 0.16,
  "breakdown": {
    "platform_fee_brl": 2875.0,
    "simples_nacional_tax_brl": 1725.0,
    "net_after_platform_brl": 25875.0
  }
}
```

---

### 3. RN12: Client Risk Assessment

**Objetivo:** Avaliar risco do cliente

**Requests:**
1. **Assess High-Risk Client** - Rating baixo, red flags na descrição
2. **Assess Low-Risk Client** - Rating alto, green flags
3. **Assess Medium-Risk Client** - Moderado

**O que esperar:**

**High-Risk:**
```json
{
  "risk_score": 7.5,
  "risk_level": "high",
  "recommendation": "reject",
  "red_flags": [
    "unrealistic_deadline",
    "vague_requirements",
    "payment_issues_mentioned"
  ],
  "green_flags": [],
  "risk_factors": {
    "client_rating_risk": 0.5,
    "client_experience_risk": 0.8,
    "payment_verification_risk": 1.0
  }
}
```

**Low-Risk:**
```json
{
  "risk_score": 2.0,
  "risk_level": "low",
  "recommendation": "accept",
  "red_flags": [],
  "green_flags": [
    "verified_payment",
    "detailed_requirements",
    "experienced_client"
  ]
}
```

---

### 4. Learning - PricingLearner

**Objetivo:** Aprender com projetos executados e ajustar precificação

**Requests:**
1. **Get Pricing Performance** - Analisa accuracy de precificação
2. **Suggest Pricing Adjustment** - Sugere ajustes de parâmetros
3. **Apply Pricing Adjustment (Auto)** - Aplica ajustes automaticamente

**O que esperar:**

**Performance:**
```json
{
  "total_records": 15,
  "avg_accuracy_score": 0.72,
  "avg_error_margin": 0.18,
  "needs_adjustment": true,
  "complexity_performance": {
    "5-6": {
      "count": 5,
      "avg_accuracy": 0.65,
      "avg_error": 0.25
    }
  }
}
```

**Sugestão:**
```json
{
  "adjustment_suggested": true,
  "current_complexity_factors": {
    "5-6": 1.4
  },
  "suggested_complexity_factors": {
    "5-6": 1.65
  },
  "reason": "Low accuracy (65%) for complexity 5-6, increasing factor"
}
```

---

### 5. Learning - RejectionPatternLearner

**Objetivo:** Aprender quais red flags predizem rejeição

**Requests:**
1. **Analyze Rejection Patterns** - Analisa correlação flags → rejeição
2. **Suggest Risk Weight Adjustments** - Sugere ajuste de pesos
3. **Discover New Red Flags** - Descobre novos flags de feedback

**O que esperar:**

**Patterns:**
```json
{
  "total_opportunities": 50,
  "rejected_count": 20,
  "accepted_count": 30,
  "rejection_rate": 0.40,
  "red_flag_stats": {
    "unrealistic_deadline": {
      "in_rejections": 15,
      "in_acceptances": 2,
      "total_occurrences": 17,
      "rejection_probability": 0.88
    }
  },
  "high_risk_flags": [
    {
      "flag": "unrealistic_deadline",
      "rejection_probability": 0.88,
      "occurrences": 17
    }
  ]
}
```

---

### 6. Learning - HourlyRateOptimizer

**Objetivo:** Otimizar taxa horária baseado em acceptance patterns

**Requests:**
1. **Analyze Acceptance by Rate Range** - Analisa acceptance por faixa ($40-60, $60-80, etc.)
2. **Analyze Category-Specific Rates** - Analisa por categoria (ai_ml vs frontend)
3. **Suggest Rate Adjustment** - Sugere ajuste de taxa
4. **Apply Rate Adjustment** - Aplica ajuste

**O que esperar:**

**Analysis:**
```json
{
  "total_opportunities": 40,
  "rate_range_stats": {
    "mid": {
      "total": 15,
      "accepted": 9,
      "acceptance_rate": 0.60,
      "avg_revenue_per_opportunity": 6500.0,
      "expected_value": 3900.0
    },
    "senior": {
      "total": 10,
      "accepted": 4,
      "acceptance_rate": 0.40,
      "avg_revenue_per_opportunity": 10000.0,
      "expected_value": 4000.0
    }
  },
  "optimal_range": {
    "range_name": "senior",
    "range_min": 100,
    "range_max": 125,
    "expected_value": 4000.0
  }
}
```

**Suggestion:**
```json
{
  "adjustment_suggested": true,
  "current_rate": 100.0,
  "suggested_rate": 110.0,
  "current_acceptance_rate": 0.55,
  "target_acceptance_rate": 0.60,
  "optimal_range": "$100-$125/hr",
  "reason": "Current rate $100/hr is optimal. Acceptance rate: 55%"
}
```

---

### 7. Integration Service (Full Pipeline)

**Objetivo:** Testar pipeline completo (RN09-RN13)

**Requests:**
1. **Process Opportunity (Full Pipeline)** - Testa com oportunidade normal
2. **Process High-Risk Opportunity** - Testa com oportunidade high-risk

**O que esperar:**
```json
{
  "is_duplicate": false,
  "risk_assessment": {
    "risk_score": 3.5,
    "risk_level": "medium",
    "recommendation": "negotiate"
  },
  "financial_calculation": {
    "gross_usd": 8000.0,
    "net_brl": 38640.0,
    "effective_tax_rate": 0.16
  },
  "rate_limit_status": {
    "requests_remaining": 98,
    "window_seconds": 3600
  },
  "lgpd_compliance": {
    "pii_encrypted": true,
    "retention_compliant": true
  }
}
```

---

## 🎯 Ordem Recomendada de Testes

### Para Primeira Vez

1. **Authentication** → Login (salva token automaticamente)
2. **RN09** → Create Opportunity #1 → Check Duplicate
3. **RN11** → Calculate Net Income (Upwork + Simples)
4. **RN12** → Assess High-Risk Client → Assess Low-Risk Client
5. **Integration** → Process Opportunity (Full Pipeline)

### Para Testar Learning Components

**Nota:** Learning components precisam de dados históricos. Se você acabou de criar o banco, não terá dados suficientes.

**Solução:** Use o script Python para popular dados de teste:
```bash
python3 scripts/test_freelancer_interactive.py
```

Depois teste:
1. **PricingLearner** → Get Pricing Performance
2. **RejectionPatternLearner** → Analyze Rejection Patterns
3. **HourlyRateOptimizer** → Analyze Acceptance by Rate Range

---

## 🔍 Dicas de Uso

### 1. Verificar Autenticação

Se receber **401 Unauthorized**:
1. Verifique se o environment está selecionado (canto superior direito)
2. Rode o request **Login** novamente
3. Verifique se a variável `token` está preenchida (ícone de olho)

### 2. Testar Rate Limiting

Para testar o rate limiting (RN10):
1. Rode **Check Rate Limit Status** várias vezes rápido
2. Observe o campo `requests_remaining` diminuir
3. Quando chegar a 0, receberá **429 Too Many Requests**

### 3. Visualizar Respostas

**Prettify JSON:**
- Click em **Pretty** (abaixo da resposta)
- Ou use Ctrl+B (Windows/Linux) / Cmd+B (Mac)

**Salvar Respostas:**
- Click em **Save Response** → **Save as Example**
- Útil para comparar resultados

### 4. Testar Múltiplos Cenários

**Use variáveis de environment:**
```json
{
  "client_budget": {{client_budget_high}},
  "client_rating": {{client_rating_low}}
}
```

**Crie múltiplos environments:**
- **Charlee - Local** (localhost:8000)
- **Charlee - Staging** (staging.charlee.ai)
- **Charlee - Production** (api.charlee.ai)

---

## 📊 Status Codes Esperados

| Endpoint | Sucesso | Erro Comum |
|----------|---------|------------|
| Login | 200 OK | 401 (credenciais inválidas) |
| Create Opportunity | 201 Created | 400 (dados inválidos) |
| Check Duplicate | 200 OK | 404 (plataforma não encontrada) |
| Risk Assessment | 200 OK | 422 (validação falhou) |
| Financial Calculation | 200 OK | 500 (erro ao buscar exchange rate) |
| Learning Components | 200 OK | 404 (dados insuficientes) |

---

## 🧪 Casos de Teste Sugeridos

### Caso 1: Cliente Ideal (Accept)
- Rating: 4.8+
- Projects: 50+
- Description: Clara, sem red flags
- Payment verified: true
- **Resultado esperado:** risk_level = "low", recommendation = "accept"

### Caso 2: Cliente Perigoso (Reject)
- Rating: <3.0
- Projects: <5
- Description: "URGENT! ASAP! Cheapest option!"
- Payment verified: false
- **Resultado esperado:** risk_level = "high", recommendation = "reject"

### Caso 3: Cliente Negociável (Negotiate)
- Rating: 3.5-4.0
- Projects: 10-20
- Description: Normal, sem red/green flags extremos
- Payment verified: true
- **Resultado esperado:** risk_level = "medium", recommendation = "negotiate"

---

## 🐛 Troubleshooting

### Problema: "Connection refused"
**Solução:** Certifique-se que o backend está rodando:
```bash
python3 -m uvicorn main:app --reload
```

### Problema: "Token expired"
**Solução:** Rode o request **Login** novamente (token tem TTL de 1 hora)

### Problema: "Insufficient data for learning components"
**Solução:** Popule o banco com dados de teste:
```bash
python3 scripts/test_freelancer_interactive.py
```

### Problema: "Database error"
**Solução:** Verifique se PostgreSQL e Redis estão rodando:
```bash
docker-compose up -d postgres redis
```

---

## 📚 Recursos Adicionais

- **Documentação completa:** [docs/implementacao/freelancer-complete.md](../docs/implementacao/freelancer-complete.md)
- **Swagger UI:** http://localhost:8000/docs (quando backend estiver rodando)
- **Script Python:** [scripts/test_freelancer_interactive.py](scripts/test_freelancer_interactive.py)
- **Jupyter Notebook:** [notebooks/test_freelancer_system.ipynb](notebooks/test_freelancer_system.ipynb)

---

## ✅ Checklist de Testes

### MVP Requirements
- [ ] RN09: Duplication Prevention (Create + Check Duplicate)
- [ ] RN10: Rate Limiting (Status + Bulk requests)
- [ ] RN11: Financial Calculator (3 tax regimes)
- [ ] RN12: Client Risk Assessment (High/Medium/Low risk)
- [ ] RN13: LGPD Compliance (Encrypt + Decrypt + Retention)

### Learning Components
- [ ] PricingLearner (Performance + Suggest + Apply)
- [ ] RejectionPatternLearner (Patterns + Weights + Discover)
- [ ] HourlyRateOptimizer (Analyze + Categories + Suggest)

### Integration
- [ ] Full Pipeline (Normal opportunity)
- [ ] Full Pipeline (High-risk opportunity)

---

**🎉 Pronto! Agora você pode testar todo o sistema freelancer via Postman sem precisar do frontend!**
