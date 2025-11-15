# 🚀 Roadmap de Desenvolvimento - Charlee

## 📊 Estado Atual (V3.0)

**Completado:**
- ✅ Sistema base de Big Rocks e Tarefas
- ✅ Agentes de bem-estar (Cycle-Aware, Capacity Guard)
- ✅ Memória persistente com Redis
- ✅ Frontend React completo (Dashboard, Analytics, Chat)
- ✅ Sistema de autenticação JWT
- ✅ Testes com 88% de cobertura

---

## 🌟 Opções de Branches (Escopo Robusto)

### **Opção 1: `feat/integration-layer` ⭐ RECOMENDADO**

**Tema:** Camada de integração entre todos os módulos

**Escopo completo:**

#### 1. Event Bus (Sistema pub/sub)
- Schema de eventos (`system_events`)
- Publishers e subscribers
- Processamento assíncrono de eventos
- Event types para todos módulos
- Redis pub/sub para real-time
- Fila de processamento com prioridade

#### 2. Context Manager
- Schema `contexto_global` (snapshot de estado)
- Subscribers para eventos relevantes
- Decisões baseadas em contexto holístico
- API de consulta de contexto
- Predicados de decisão (should_accept_interruption, get_optimal_activity_type)

#### 3. Cross-Module Relations
- Schema `cross_module_relations`
- Schema `decisoes_integradas`
- Links entre entidades de diferentes módulos
- Sistema de decisões cross-module
- Tracking de relacionamentos

#### 4. Integrações Específicas
- **Task ↔ Wellness:** Ajuste de prioridade por fase do ciclo
- **Focus ↔ Capacity:** Proteção máxima por sobrecarga
- **Wellness ↔ Projects:** Avaliação de projetos por energia
- **Analytics integrado:** Métricas cross-module
- **Orquestrador central aprimorado**

#### 5. Completar TODOs Técnicos
- Settings persistence no DB (backend/api/routes/settings.py:68)
- Sistema de backup (settings.py:106)
- Analytics calculations reais (analytics.py:193)
- Cycle analysis real (analytics.py:214)

#### 6. Testes de Integração
- Event flow end-to-end
- Context updates e propagação
- Decision-making cross-module
- Performance de event processing

**Estimativa:** 2-3 semanas

**Benefícios:**
- ✅ Base para TODAS as features futuras
- ✅ Desbloqueia desenvolvimento paralelo de módulos
- ✅ Escopo grande mas coeso
- ✅ Alto impacto técnico
- ✅ Sistema já bem documentado

**Dependências:** Nenhuma

**Desbloqueia:** Todas as outras features

---

### **Opção 2: `feat/focus-notification-system`**

**Tema:** Sistema completo de gestão de atenção e notificações

**Escopo completo:**

#### 1. Database Schema
- `notification_sources` - Fontes de notificação
- `notifications` - Notificações recebidas
- `notification_rules` - Regras personalizadas
- `focus_sessions` - Sessões de deep work
- `notification_digests` - Resumos periódicos
- `notification_patterns` - Aprendizado de padrões
- `response_templates` - Templates de resposta

#### 2. Agentes AI
- **NotificationAgent:** Coletor multi-fonte
- **ClassifierAgent:** LLM semântico (categorização)
- **ResponderAgent:** Gerador de respostas contextuais
- **FocusGuardAgent:** Protetor de foco

#### 3. Integrações de Fontes
- Gmail (IMAP + OAuth2)
- Slack (WebClient API)
- LinkedIn (REST API)
- GitHub notifications
- Extensível para outras fontes

#### 4. Sistema de Foco
- Focus sessions (deep work tracking)
- Do Not Disturb mode
- Snooze inteligente por contexto
- Urgency verification (ML)
- Focus quality tracking
- Interrupções bloqueadas

#### 5. Auto-resposta
- Template engine
- Context-aware responses
- Approval workflow
- Learning from feedback
- Estilo linguístico personalizado

#### 6. Frontend
- Notification inbox UI
- Focus session controls
- Rules management interface
- Stats dashboard
- Digest viewer

#### 7. Integração com Módulos Existentes
- Wellness (proteção maior na fase menstrual)
- Capacity (bloqueio por sobrecarga)
- Event Bus (eventos de notificação)

**Estimativa:** 3-4 semanas

**Benefícios:**
- ✅ Feature completa e fechada
- ✅ Alto valor para usuário final
- ✅ Resolve problema real (200+ notif/dia)
- ✅ Economia de ~6h/semana

**Dependências:** Event Bus (básico)

**Desbloqueia:** Modo "Co-Piloto" de vida digital

---

### **Opção 3: `feat/productivity-orchestrator`**

**Tema:** Orquestração completa de produtividade (Calendar + Analytics + Integrations)

**Escopo completo:**

#### 1. Google Calendar Integration
- OAuth2 flow completo
- Sync bidirecional (Charlee ↔ Calendar)
- Event detection e parsing
- Auto-scheduling baseado em capacity
- Time blocking automático
- Meeting conflict resolution

#### 2. Event Bus (base)
- Core pub/sub system
- Event types essenciais
- Basic context manager
- Minimal viable integration

#### 3. Enhanced Analytics
- Real-time calculations
- Productivity patterns (ML)
- Cycle-aware insights
- Capacity trending
- Predictive analytics
- Burnout detection

#### 4. Smart Scheduling
- Task → Calendar sync
- Optimal time suggestions (por energia)
- Meeting conflict resolution
- Energy-based scheduling
- Focus blocks automáticos
- Pomodoro integration

#### 5. Completar TODOs Técnicos
- Settings DB persistence
- Backup system automático
- Analytics calculations reais
- Cycle analysis implementation

#### 6. Frontend Enhancements
- Calendar view integrado
- Analytics dashboard avançado
- Scheduling wizard
- Insights panel
- Timeline view

**Estimativa:** 3-4 semanas

**Benefícios:**
- ✅ Junta várias features de alto valor
- ✅ Calendário é feature muito pedida
- ✅ Analytics melhora visibilidade
- ✅ Smart scheduling é diferenciado

**Dependências:** Nenhuma (cria Event Bus mínimo)

**Desbloqueia:** Time management completo

---

### **Opção 4: `feat/freelance-project-hub`**

**Tema:** Sistema completo de gestão de projetos freelance

**Escopo completo:**

#### 1. Database Schema
- `projetos_freelance` - Projetos coletados
- `analises_projetos` - Análises e scores
- `portfolio_entries` - Portfólio
- `client_profiles` - Perfis de clientes
- `project_templates` - Templates de proposta
- `negotiations` - Histórico de negociações

#### 2. Agentes Especializados
- **ProjectCollectorAgent:** Coleta de múltiplas fontes
- **ProjectAnalyzerAgent:** Análise multifatorial
- **NegotiationAgent:** Assistente de negociação
- **PortfolioManagerAgent:** Gestão de portfólio
- **ClientRelationshipAgent:** CRM inteligente

#### 3. Coleta Automática
- Email parsing (proposals)
- Upwork integration (API)
- Webhook receivers
- Manual input form
- Duplicate detection

#### 4. Análise Inteligente
- Scoring multifatorial (10+ critérios)
- Capacity checking (viabilidade)
- ROI estimation
- Risk assessment
- Recommendation engine (aceitar/negociar/recusar)
- Wellness-aware (ajuste por fase do ciclo)

#### 5. Gestão de Portfólio
- Active projects tracking
- Client history e ratings
- Skills matrix
- Revenue forecasting
- Success rate analytics

#### 6. Integração com Tasks
- Auto-create tasks from project
- Project → Big Rock mapping
- Milestone tracking
- Capacity allocation
- Deadline management

#### 7. Event Bus Integration
- Project lifecycle events
- Capacity updates
- Wellness considerations
- Analytics events

#### 8. Frontend
- Project pipeline view (Kanban)
- Analysis dashboard
- Portfolio overview
- Negotiation assistant UI
- Client profiles

**Estimativa:** 4-5 semanas

**Benefícios:**
- ✅ Feature diferenciada e única
- ✅ Alto valor de negócio
- ✅ Muito bem documentada
- ✅ Resolve dor real (gestão freelance)

**Dependências:** Event Bus (recomendado)

**Desbloqueia:** Revenue management, Client CRM

---

## 🎯 Ordem Recomendada de Execução

### **Fase 1: Fundação (V3.1)**
```
feat/integration-layer
```
- Cria base para tudo
- Permite desenvolvimento paralelo depois
- Resolve débitos técnicos

### **Fase 2: Features de Alto Valor (V3.2-V3.3)**
```
feat/focus-notification-system
feat/productivity-orchestrator
```
- Usa Event Bus da Fase 1
- Alto impacto no dia-a-dia
- Features independentes (podem ser paralelas)

### **Fase 3: Diferenciação (V4)**
```
feat/freelance-project-hub
feat/multimodal-input (voz, imagens)
feat/telegram-bot
```
- Features avançadas
- Usa toda infraestrutura anterior

---

## 📊 Comparação Rápida

| Branch | Escopo | Semanas | Valor Usuário | Valor Técnico | Dependências |
|--------|--------|---------|---------------|---------------|--------------|
| **integration-layer** | Grande | 2-3 | Médio | **Muito Alto** | Nenhuma |
| **focus-notification** | Grande | 3-4 | **Muito Alto** | Alto | Event Bus |
| **productivity-orchestrator** | Grande | 3-4 | **Muito Alto** | Alto | Nenhuma* |
| **freelance-project-hub** | Muito Grande | 4-5 | Alto | Médio | Event Bus |

*Cria Event Bus mínimo

---

## 🚀 Decisão: Começar por `feat/integration-layer`

**Justificativa:**
1. É a **fundação** para tudo mais
2. Depois dela, você pode desenvolver features em paralelo
3. Resolve os TODOs técnicos (cleanup)
4. Permite que Wellness, Capacity, Tasks, Analytics conversem de verdade
5. Habilita decisões inteligentes cross-module
6. Escopo grande mas muito bem definido na documentação

**Branch:**
```bash
claude/integration-layer-01FGs7tV5uco9E5JgaL5ZJhi
```

---

## 📝 Tracking de Progresso

### feat/integration-layer
- [ ] Event Bus implementation
- [ ] Context Manager
- [ ] Cross-Module Relations
- [ ] Task ↔ Wellness integration
- [ ] Focus ↔ Capacity integration
- [ ] Wellness ↔ Projects integration
- [ ] Analytics enhancement
- [ ] TODOs técnicos
- [ ] Testes de integração
- [ ] Documentação

---

**Criado em:** 2025-01-15
**Última atualização:** 2025-01-15
**Status:** Em execução (Opção 1)
