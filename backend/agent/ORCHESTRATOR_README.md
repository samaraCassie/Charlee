# Agent Orchestrator - Sistema de Orquestração Inteligente

## Visão Geral

O **AgentOrchestrator** é o cérebro central do Charlee que coordena múltiplos agentes especializados para fornecer respostas contextualizadas e personalizadas baseadas nas necessidades da usuária.

## Arquitetura

```
┌─────────────────────────────────────────────┐
│         Usuário envia mensagem              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      AgentOrchestrator (Roteador)           │
│   - Analisa intenção da mensagem            │
│   - Decide qual agente usar                 │
│   - Coleta contexto de múltiplos agentes    │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│  Cycle   │ │ Capacity │ │  Charlee │
│  Aware   │ │  Guard   │ │   Agent  │
│  Agent   │ │  Agent   │ │  (Core)  │
└──────────┘ └──────────┘ └──────────┘
```

## Agentes Especializados

### 1. CycleAwareAgent (Wellness Coach)
- **Quando é acionado**: Mensagens sobre ciclo menstrual, energia, bem-estar, saúde
- **Responsabilidades**:
  - Registrar e tracked fases do ciclo
  - Sugerir tarefas adequadas para cada fase
  - Analisar se carga de trabalho está compatível com energia atual
- **Palavras-chave**: ciclo, menstruação, energia, TPM, ovulação, fase, bem-estar, descanso, sono, estresse

### 2. CapacityGuardAgent (Guardian)
- **Quando é acionado**: Mensagens sobre carga de trabalho, novos projetos, sobrecarga
- **Responsabilidades**:
  - Calcular carga de trabalho atual
  - Avaliar se há capacidade para novos compromissos
  - Sugerir trade-offs quando necessário
  - Proteger contra sobrecarga
- **Palavras-chave**: sobrecarga, muito trabalho, novo projeto, capacidade, trade-off, prazo, deadline, adiar

### 3. CharleeAgent (Core)
- **Quando é acionado**: Tarefas gerais, planejamento, perguntas sobre foco
- **Responsabilidades**:
  - Gestão de tarefas e Big Rocks
  - Planejamento estratégico
  - Perguntas gerais
- **Palavras-chave**: tarefa, big rock, pilar, objetivo, fazer hoje, completar, concluir

## Funcionalidades Inteligentes

### 1. Roteamento Automático por Intenção
O orquestrador analisa a mensagem e detecta automaticamente qual agente deve responder:

**Exemplo 1: Wellness**
```
Usuário: "Estou me sentindo muito cansada hoje, é minha fase menstrual"
→ Roteado para: CycleAwareAgent
→ Resposta: Informações sobre fase menstrual + sugestões de tarefas leves
```

**Exemplo 2: Capacity**
```
Usuário: "Posso aceitar um novo projeto de 15 tarefas?"
→ Roteado para: CapacityGuardAgent
→ Resposta: Análise de capacidade + decisão (aceitar/rejeitar/trade-offs)
```

**Exemplo 3: Tasks**
```
Usuário: "Criar tarefa: Apresentação Janeiro"
→ Roteado para: CharleeAgent (com check de capacidade)
→ Resposta: Tarefa criada + alerta se houver sobrecarga
```

### 2. Consulta Multi-Agente Automática
Para decisões complexas, o orquestrador consulta múltiplos agentes automaticamente:

**Exemplo: Planejamento do dia**
```
Usuário: "Qual deve ser meu foco hoje?"
→ Orquestrador consulta:
  1. CycleAwareAgent → Qual minha fase e energia esperada?
  2. CapacityGuardAgent → Qual minha carga de trabalho?
  3. CharleeAgent → Baseado nos contextos, sugere prioridades
→ Resposta: Sugestão personalizada considerando energia + carga
```

### 3. Capacity-Aware Task Creation
Quando o usuário cria uma nova tarefa, o sistema automaticamente:
1. Consulta o CapacityGuardAgent sobre a carga atual
2. Alerta se houver risco de sobrecarga
3. Sugere redistribuir tarefas se necessário

**Exemplo:**
```
Usuário: "Adicionar nova tarefa: Implementar feature X"
→ Sistema verifica capacidade automaticamente
→ Se sobrecarga detectada:
   ⚠️ "Atenção: Você já tem 25 tarefas nas próximas 2 semanas.
       Considere adiar: [lista de tarefas menos urgentes]"
```

### 4. Wellness Context Injection
Para perguntas sobre planejamento, o sistema injeta contexto de bem-estar:

```
Usuário: "O que priorizar essa semana?"
→ Sistema adiciona ao contexto:
   🌸 Fase atual: Lutea (energia 80%)
   📊 Carga: 18 tarefas (moderada)
   🎯 Big Rocks: Equilíbrio OK
→ CharleeAgent responde com base nos 3 contextos
```

## API Endpoints

### POST /api/v1/agent/chat
Envia mensagem ao orquestrador (roteamento automático)

**Request:**
```json
{
  "message": "Estou muito cansada, qual fase do ciclo estou?",
  "user_id": "samara",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "🌸 Fase Atual: Menstrual\n📅 Desde: 2025-01-05...",
  "session_id": "abc-123"
}
```

### GET /api/v1/agent/status
Verifica status do orquestrador

**Response:**
```json
{
  "session_id": "abc-123",
  "user_id": "samara",
  "last_agent_used": "cycle_aware",
  "conversation_topic": "wellness",
  "agents_available": {
    "core": true,
    "cycle_aware": true,
    "capacity_guard": true
  },
  "orchestration_features": {
    "intelligent_routing": true,
    "cross_agent_consultation": true,
    "capacity_aware_task_creation": true,
    "wellness_context_injection": true
  }
}
```

### POST /api/v1/agent/analyze-routing
Analisa como uma mensagem seria roteada (DEBUG)

**Request:**
```json
{
  "message": "Posso aceitar um novo projeto?",
  "user_id": "samara"
}
```

**Response:**
```json
{
  "message": "Posso aceitar um novo projeto?",
  "intent_detected": "capacity",
  "agent_to_use": "CapacityGuardAgent",
  "reason": "Mensagem contém palavras-chave relacionadas a carga de trabalho/capacidade",
  "will_consult_other_agents": false,
  "keywords_matched": ["aceitar", "projeto"]
}
```

## Exemplos de Uso Completos

### Cenário 1: Morning Routine

```bash
# 1. Verificar fase do ciclo
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Como está minha energia hoje?"}'

# Resposta: CycleAwareAgent informa fase e energia esperada

# 2. Ver carga da semana
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Qual minha carga de trabalho essa semana?"}'

# Resposta: CapacityGuardAgent mostra distribuição por Big Rock

# 3. Pedir sugestão de foco
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "O que devo focar hoje?"}'

# Resposta: CharleeAgent consulta os outros 2 agentes e dá sugestão personalizada
```

### Cenário 2: Avaliação de Novo Projeto

```bash
# Perguntar se pode aceitar
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Me ofereceram um projeto de 12 tarefas. Consigo aceitar?"}'

# CapacityGuardAgent analisa:
# - Carga atual: 18 tarefas
# - Capacidade máxima: 25 tarefas
# - Decisão: ACEITAR COM RESSALVAS
# - Aviso: Carga ficará acima do ideal (30 tarefas)
# - Sugestão: Negociar prazos flexíveis
```

### Cenário 3: Criação de Tarefa com Proteção

```bash
# Criar nova tarefa
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Criar tarefa: Reunião Syssa Janeiro para amanhã"}'

# Sistema:
# 1. Detecta intent="tasks"
# 2. Consulta CapacityGuardAgent automaticamente
# 3. Se houver sobrecarga, CharleeAgent alerta antes de criar
# 4. Cria a tarefa
# 5. Sugere ajustes se necessário
```

## Testes e Debugging

### Ver qual agente será usado (sem executar)
```bash
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "Estou exausta e com muita dor de cabeça"}'
```

Resposta mostra:
- Intent: "wellness"
- Agente: "CycleAwareAgent"
- Keywords: ["exausta", "dor"]

### Ver status da orquestração
```bash
curl http://localhost:8000/api/v1/agent/status?user_id=samara
```

## Como Estender

### Adicionar novo agente especializado

1. **Criar o agente** em `backend/agent/specialized_agents/`:
```python
class NewSpecializedAgent(Agent):
    def __init__(self, db: Session):
        super().__init__(
            name="New Agent",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=["..."],
            tools=[...]
        )
```

2. **Registrar no orquestrador** em `orchestrator.py`:
```python
def __init__(self, ...):
    # ...
    self.new_agent = NewSpecializedAgent(db=db)
```

3. **Adicionar palavras-chave** em `_analyze_intent()`:
```python
new_keywords = ["palavra1", "palavra2", ...]
if any(keyword in message_lower for keyword in new_keywords):
    return "new_intent"
```

4. **Criar handler** em `route_message()`:
```python
elif intent == "new_intent":
    response = self._handle_new_agent(message)
```

## Benefícios da Orquestração

✅ **Respostas mais contextualizadas**: Agentes especializados fornecem insights específicos
✅ **Proteção contra sobrecarga**: Sistema alerta automaticamente sobre riscos
✅ **Consciência de bem-estar**: Recomendações adaptadas à fase do ciclo
✅ **Decisões informadas**: Consulta múltiplos agentes para decisões complexas
✅ **Experiência única**: Combina produtividade com bem-estar de forma inteligente

## Status

✅ **Implementado e funcional**
- Roteamento inteligente por intenção
- Consulta multi-agente
- Capacity-aware task creation
- Wellness context injection
- Endpoints de debug e status

🎯 **Pronto para uso em produção**
