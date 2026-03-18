# Frontend do Sistema Freelancer - Guia Completo

Interface web completa para gerenciamento de projetos freelance com análise automatizada.

---

## ✨ Funcionalidades

### 1. **Gestão de Oportunidades** ([FreelancerOpportunities.tsx](src/pages/FreelancerOpportunities.tsx))
- ✅ Listagem de todas as oportunidades com filtros
- ✅ Cards visuais com status, risco e pricing
- ✅ Criação rápida de novas oportunidades
- ✅ Estatísticas em tempo real (total, aceitas, receita)
- ✅ Processamento automático (análise de risco + pricing + financial)
- ✅ Badges coloridos por status e nível de risco

### 2. **Detalhes da Oportunidade** ([OpportunityDetail.tsx](src/pages/OpportunityDetail.tsx))
- ✅ Visualização completa do projeto
- ✅ Informações do cliente (rating, projetos, país, pagamento verificado)
- ✅ Análise de risco automática com red/green flags
- ✅ Sugestão de precificação com breakdown de multiplicadores
- ✅ Cálculo financeiro (USD → BRL com impostos)
- ✅ Geração de proposta de negociação
- ✅ Ações rápidas: aceitar, rejeitar, negociar

### 3. **Analytics e Insights** ([FreelancerAnalytics.tsx](src/pages/FreelancerAnalytics.tsx))
- ✅ **Career Insights**:
  - Total de oportunidades e taxa de aceitação
  - Receita total e taxa horária média
  - Gráfico de tendência de receita por mês
  - Top skills mais lucrativas
  - Top plataformas por receita
- ✅ **Learning Components Performance**:
  - **Pricing Accuracy**: Score de precisão da precificação automática
  - **Rejection Patterns**: Red flags com maior probabilidade de rejeição
  - **Hourly Rate Optimization**: Taxa horária sugerida e faixa ótima

### 4. **Configuração de Precificação** ([PricingParameters.tsx](src/pages/PricingParameters.tsx))
- ✅ Configuração da taxa horária base
- ✅ Margem mínima de lucro
- ✅ Valor mínimo de projeto e prazo mínimo
- ✅ **Fatores de Complexidade**: multiplicadores de 1-10
- ✅ **Fatores de Especialização**: AI/ML, Blockchain, Full-stack, etc.
- ✅ **Fatores de Prazo**: Urgent, Short, Normal, Long
- ✅ **Fatores de Cliente**: New, Verified, Premium
- ✅ Salvamento com controle de alterações
- ✅ Informações de versão e status

---

## 🗂️ Estrutura de Arquivos

```
interfaces/web/src/
├── types/
│   └── freelancer.ts                    # TypeScript types
├── services/
│   └── freelancerService.ts             # API service layer
├── stores/
│   └── freelancerStore.ts               # Zustand state management
├── pages/
│   ├── FreelancerOpportunities.tsx      # Lista de oportunidades
│   ├── OpportunityDetail.tsx            # Detalhes da oportunidade
│   ├── FreelancerAnalytics.tsx          # Analytics e insights
│   └── PricingParameters.tsx            # Configurações de pricing
└── components/ui/
    ├── badge.tsx                        # Badge component (novo)
    ├── button.tsx                       # Já existia
    ├── card.tsx                         # Já existia
    ├── dialog.tsx                       # Já existia
    ├── input.tsx                        # Já existia
    └── select.tsx                       # Já existia
```

---

## 🚀 Como Usar

### 1. **Inicie o Frontend**

```bash
cd /home/sam-cassie/GitHub/Charlee/interfaces/web
npm run dev
```

O frontend estará disponível em: **http://localhost:5173**

### 2. **Certifique-se que o Backend está rodando**

```bash
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. **Navegue para o Sistema Freelancer**

Acesse: **http://localhost:5173/freelancer/opportunities**

Ou clique no menu **Freelancer** no header.

---

## 📋 Fluxo de Uso Típico

### **Adicionar Nova Oportunidade**

1. Clique em **"Nova Oportunidade"**
2. Preencha:
   - Plataforma (Upwork, Freelancer.com, etc.)
   - ID externo
   - Título e descrição
   - Orçamento, rating do cliente, horas estimadas
3. Click **"Criar Oportunidade"**

### **Analisar Oportunidade**

1. Na listagem, click **"Analisar"** no card da oportunidade
2. O sistema executa automaticamente:
   - ✅ Checagem de duplicação (RN09)
   - ✅ Avaliação de risco (RN12)
   - ✅ Cálculo financeiro (RN11)
   - ✅ Sugestão de pricing
3. Resultados aparecem no card

### **Ver Detalhes e Decidir**

1. Click **"Ver Detalhes"**
2. Revise:
   - Análise de risco (low/medium/high)
   - Red flags e green flags
   - Pricing sugerido com breakdown
   - Cálculo financeiro (USD → BRL)
3. Tome decisão:
   - ✅ **Aceitar** (se risco baixo e preço bom)
   - 💬 **Negociar** (se preço abaixo do ideal)
   - ❌ **Rejeitar** (se alto risco ou baixo valor)

### **Gerar Negociação**

1. No detalhe da oportunidade, click **"Negociar"**
2. O sistema gera:
   - Contra-oferta calculada
   - Raciocínio baseado em seus parâmetros
   - Mensagem template pronta para enviar ao cliente
   - Estratégia de negociação

### **Configurar Parâmetros de Pricing**

1. Acesse: `/freelancer/pricing`
2. Ajuste:
   - Taxa horária base
   - Multiplicadores de complexidade
   - Multiplicadores de especialização
   - Fatores de prazo e cliente
3. Click **"Salvar Alterações"**

### **Analisar Performance**

1. Acesse: `/freelancer/analytics`
2. Veja:
   - Receita total e taxa de aceitação
   - Gráficos de tendência
   - Top skills e plataformas
   - Performance dos learning components
   - Sugestões de otimização

---

## 🎨 Design e UI

### **Stack de UI**
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Componentes React reutilizáveis
- **Recharts** - Gráficos e visualizações
- **Lucide React** - Ícones modernos

### **Dark Mode**
- ✅ Totalmente suportado
- ✅ Botão de toggle no header
- ✅ Persistência no localStorage

### **Responsividade**
- ✅ Mobile-first design
- ✅ Breakpoints: sm, md, lg, xl
- ✅ Menu mobile com drawer lateral

### **Cores de Status**

**Oportunidades:**
- 🟢 `accepted` - Verde (success)
- 🔴 `rejected` - Vermelho (destructive)
- 🟡 `negotiating` - Amarelo (warning)
- 🔵 `completed` - Azul (info)
- ⚪ `pending` - Cinza (secondary)

**Risco:**
- 🟢 `low` - Verde
- 🟡 `medium` - Amarelo
- 🔴 `high` - Vermelho

---

## 📊 Componentes de Dados

### **FreelancerStore (Zustand)**

Estado global gerenciado com Zustand:

```typescript
const {
  // Data
  opportunities,
  selectedOpportunity,
  platforms,
  pricingParameters,
  stats,
  careerInsights,
  learningPerformance,

  // UI State
  loading,
  error,
  filters,

  // Actions
  fetchOpportunities,
  fetchOpportunityById,
  createOpportunity,
  updateOpportunityStatus,
  processOpportunity,
  fetchPricingParameters,
  updatePricingParameters,
  fetchStats,
  fetchCareerInsights,
  fetchLearningPerformance,
} = useFreelancerStore();
```

### **API Service Layer**

Todas as chamadas ao backend passam por `freelancerService.ts`:

```typescript
// Opportunities
getOpportunities(filters?)
getOpportunityById(id)
createOpportunity(data)
updateOpportunityStatus(id, status)
deleteOpportunity(id)

// Processing
checkDuplicate(title, description, platform_id, external_id)
assessRisk(opportunity_id)
calculateFinancial(data)
calculatePricing(opportunity_id)
generateNegotiation(data)
processOpportunity(data) // Full pipeline

// Pricing
getPricingParameters()
updatePricingParameters(data)

// Learning
getPricingPerformance()
getRejectionPatterns()
getHourlyRateAnalysis()
applyPricingAdjustment()
applyRateAdjustment()

// Insights
getCareerInsights()
getTopPerformingProjects()
getIncomeTrends(period)
getOpportunityStats()
getLearningPerformance()
```

---

## 🔧 Configuração

### **Variável de Ambiente**

Crie `.env` em `interfaces/web/`:

```bash
VITE_API_URL=http://localhost:8000/api
```

Se não definida, usa `http://localhost:8000/api` por padrão.

### **API Base URL**

Configurado em [src/services/api.ts](src/services/api.ts):

```typescript
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 400000,
});
```

---

## 📝 TypeScript Types

Todos os tipos estão definidos em [src/types/freelancer.ts](src/types/freelancer.ts):

```typescript
// Main types
FreelanceOpportunity
FreelancePlatform
PricingParameter
RiskAssessment
FinancialCalculation
PricingSuggestion
NegotiationResponse
CareerInsight
LearningComponentPerformance

// Request types
CreateOpportunityRequest
ProcessOpportunityRequest
CalculateFinancialRequest
GenerateNegotiationRequest

// Filter types
OpportunityFilters
OpportunityStats
```

---

## 🧪 Testando o Frontend

### **Teste Manual Completo**

1. **Criar Oportunidade**:
   ```
   Plataforma: Upwork
   Título: Python Backend Developer
   Descrição: Need FastAPI expert for REST API
   Orçamento: $5000
   Rating: 4.5
   Horas: 100
   ```

2. **Processar**:
   - Click "Analisar"
   - Aguarde alguns segundos
   - Veja resultados populados

3. **Ver Detalhes**:
   - Click "Ver Detalhes"
   - Revise todas as seções
   - Teste botão "Negociar"

4. **Analytics**:
   - Acesse `/freelancer/analytics`
   - Veja gráficos e insights

5. **Configurar Pricing**:
   - Acesse `/freelancer/pricing`
   - Ajuste valores
   - Salve

### **Teste com Dados Reais**

Use o script Python para popular dados de teste:

```bash
cd /home/sam-cassie/GitHub/Charlee/backend
source venv/bin/activate
python scripts/test_freelancer_interactive.py
```

Isso criará múltiplas oportunidades com análises completas.

---

## 🐛 Troubleshooting

### **Erro: "Failed to fetch opportunities"**

**Causa:** Backend não está rodando ou URL incorreta

**Solução:**
```bash
# Verifique se backend está rodando
curl http://localhost:8000/health

# Se não, inicie
cd backend
source venv/bin/activate
python -m uvicorn api.main:app --reload
```

### **Erro: "Network Error"**

**Causa:** CORS não configurado ou API URL errada

**Solução:**
```bash
# Verifique VITE_API_URL
echo $VITE_API_URL

# Deve ser: http://localhost:8000/api
```

### **Erro: "404 Not Found" em endpoints**

**Causa:** Rota da API não existe no backend

**Solução:**
- Verifique se backend tem o endpoint
- Confira `/docs` do FastAPI: http://localhost:8000/docs
- Atualize `freelancerService.ts` se necessário

### **Gráficos não aparecem**

**Causa:** Recharts não instalado ou dados vazios

**Solução:**
```bash
npm install recharts
```

---

## 🚀 Próximos Passos

### **Melhorias Futuras**

1. **Autenticação**:
   - [ ] Integrar com sistema de auth do backend
   - [ ] JWT token storage
   - [ ] Refresh token flow

2. **Filtros Avançados**:
   - [ ] Filtro por skills
   - [ ] Filtro por range de orçamento
   - [ ] Filtro por nível de risco
   - [ ] Filtro por plataforma

3. **Notificações**:
   - [ ] Toast notifications para ações
   - [ ] Real-time updates via WebSocket
   - [ ] Notificações de novas oportunidades

4. **Export de Dados**:
   - [ ] Export para CSV
   - [ ] Export para PDF
   - [ ] Relatórios personalizados

5. **Integração com Plataformas**:
   - [ ] Auto-import de oportunidades do Upwork
   - [ ] Auto-import do Freelancer.com
   - [ ] Auto-submit de propostas

6. **Dashboard Personalizado**:
   - [ ] Widgets configuráveis
   - [ ] Métricas favoritas
   - [ ] Alerts personalizados

---

## 📚 Recursos

- **Swagger UI Backend**: http://localhost:8000/docs
- **Postman Collection**: `backend/postman_collection_freelancer.json`
- **Backend Guide**: `backend/POSTMAN_GUIDE.md`
- **Setup Guide**: `QUICK_START.md`

---

## ✅ Checklist de Uso

- [ ] Backend rodando (porta 8000)
- [ ] Frontend rodando (porta 5173)
- [ ] PostgreSQL com pgvector rodando
- [ ] Redis rodando
- [ ] Criar pelo menos 1 plataforma
- [ ] Configurar parâmetros de pricing
- [ ] Adicionar primeira oportunidade
- [ ] Processar oportunidade
- [ ] Ver analytics

---

**Pronto para usar! O sistema freelancer está completamente funcional com interface web moderna e responsiva.** 🎉
