# Prompts de Teste - Agent Orchestrator

Este arquivo contém prompts de teste para validar o sistema de orquestração inteligente do Charlee.

## Como Usar

### Via API (Docker rodando)
```bash
# Testar análise de roteamento (sem executar)
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "SEU_PROMPT_AQUI"}'

# Executar chat (com execução real)
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "SEU_PROMPT_AQUI", "user_id": "samara"}'
```

---

## 🌸 Categoria: WELLNESS (CycleAwareAgent)

### Prompt 1: Fase do Ciclo
```
Qual fase do ciclo menstrual estou?
```
**Resultado Esperado:**
- Intent: `wellness`
- Agente: `CycleAwareAgent`
- Keywords: `["ciclo", "menstrual"]`
- Comportamento: Retorna fase atual, energia esperada, sugestões

### Prompt 2: Energia Baixa
```
Estou me sentindo muito cansada e com pouca energia hoje
```
**Resultado Esperado:**
- Intent: `wellness`
- Agente: `CycleAwareAgent`
- Keywords: `["cansada", "energia"]`
- Comportamento: Analisa fase atual e sugere tarefas leves

### Prompt 3: TPM
```
Estou com TPM e muito estresse, o que devo fazer?
```
**Resultado Esperado:**
- Intent: `wellness`
- Agente: `CycleAwareAgent`
- Keywords: `["TPM", "estresse"]`
- Comportamento: Recomendações adaptadas para fase menstrual

### Prompt 4: Sono
```
Dormi muito mal essa noite, como adaptar meu dia?
```
**Resultado Esperado:**
- Intent: `wellness`
- Agente: `CycleAwareAgent`
- Keywords: `["dormi"]`
- Comportamento: Sugestões considerando baixa energia

### Prompt 5: Bem-estar Geral
```
Como está meu bem-estar e saúde essa semana?
```
**Resultado Esperado:**
- Intent: `wellness`
- Agente: `CycleAwareAgent`
- Keywords: `["bem-estar", "saúde"]`
- Comportamento: Análise de bem-estar e recomendações

---

## 🛡️ Categoria: CAPACITY (CapacityGuardAgent)

### Prompt 6: Novo Projeto
```
Me ofereceram um novo projeto com 15 tarefas. Consigo aceitar?
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["novo projeto"]`
- Comportamento: Avalia capacidade, retorna ACEITAR/REJEITAR com justificativa

### Prompt 7: Sobrecarga
```
Estou com muita sobrecarga de trabalho
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["sobrecarga", "trabalho"]`
- Comportamento: Analisa carga atual, sugere trade-offs

### Prompt 8: Avaliar Capacidade
```
Qual minha carga de trabalho nas próximas 3 semanas?
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["carga", "trabalho"]`
- Comportamento: Mostra distribuição por Big Rock, identifica sobrecargas

### Prompt 9: Aceitar Compromisso
```
Posso aceitar um compromisso novo essa semana?
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["aceitar", "compromisso"]`
- Comportamento: Decisão baseada em capacidade atual

### Prompt 10: Trade-offs
```
Preciso adiar algumas tarefas, quais você sugere?
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["adiar"]`
- Comportamento: Sugere tarefas menos urgentes para adiar

### Prompt 11: Prazo Apertado
```
Não vou conseguir dar conta de tudo até o deadline
```
**Resultado Esperado:**
- Intent: `capacity`
- Agente: `CapacityGuardAgent`
- Keywords: `["não consigo", "dar conta", "deadline"]`
- Comportamento: Análise de priorização e sugestões de ajuste

---

## 📋 Categoria: TASKS (CharleeAgent com Capacity Check)

### Prompt 12: Criar Tarefa
```
Criar tarefa: Apresentação Janeiro para dia 15/01
```
**Resultado Esperado:**
- Intent: `tasks`
- Agente: `CharleeAgent (com check de capacidade)`
- Keywords: `["criar tarefa"]`
- Comportamento:
  1. Consulta CapacityGuardAgent sobre carga atual
  2. Cria tarefa
  3. Alerta se houver sobrecarga

### Prompt 13: Listar Tarefas
```
Listar minhas tarefas de hoje
```
**Resultado Esperado:**
- Intent: `tasks`
- Agente: `CharleeAgent (com check de capacidade)`
- Keywords: `["listar tarefa", "fazer hoje"]`
- Comportamento: Lista tarefas do dia

### Prompt 14: Adicionar Tarefa
```
Adicionar nova tarefa: Reunião com Breno
```
**Resultado Esperado:**
- Intent: `tasks`
- Agente: `CharleeAgent (com check de capacidade)`
- Keywords: `["adicionar", "nova tarefa"]`
- Comportamento: Verifica capacidade + adiciona tarefa

### Prompt 15: Big Rock
```
Criar um novo big rock para Finanças Pessoais
```
**Resultado Esperado:**
- Intent: `tasks`
- Agente: `CharleeAgent (com check de capacidade)`
- Keywords: `["big rock"]`
- Comportamento: Cria novo pilar

### Prompt 16: Completar Tarefa
```
Marcar como concluída a tarefa de Relatório Semanal
```
**Resultado Esperado:**
- Intent: `tasks`
- Agente: `CharleeAgent (com check de capacidade)`
- Keywords: `["marcar como", "concluída"]`
- Comportamento: Marca tarefa como completa

---

## 🎯 Categoria: GENERAL com Consulta Multi-Agente

### Prompt 17: Foco do Dia (Multi-Agent)
```
Qual deve ser meu foco hoje?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent (com consulta multi-agente)`
- Will Consult: `true`
- Keywords: `["foco hoje"]`
- Comportamento:
  1. Consulta CycleAwareAgent (fase e energia)
  2. Consulta CapacityGuardAgent (carga atual)
  3. Responde com recomendação personalizada

### Prompt 18: Priorização (Multi-Agent)
```
O que devo priorizar essa semana?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent (com consulta multi-agente)`
- Will Consult: `true`
- Keywords: `["prioridade"]`
- Comportamento: Consulta multi-agente + sugestão de prioridades

### Prompt 19: Planejamento (Multi-Agent)
```
Me ajuda a planejar meu mês de janeiro
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent (com consulta multi-agente)`
- Will Consult: `true`
- Keywords: `["planejar"]`
- Comportamento: Consulta wellness + capacity + gera plano

### Prompt 20: O que Fazer (Multi-Agent)
```
O que fazer agora com minha situação atual?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent (com consulta multi-agente)`
- Will Consult: `true`
- Keywords: `["o que fazer"]`
- Comportamento: Análise completa de contexto

---

## 💬 Categoria: GENERAL (Sem Consulta)

### Prompt 21: Saudação
```
Oi Charlee, tudo bem?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent`
- Will Consult: `false`
- Comportamento: Resposta conversacional simples

### Prompt 22: Ajuda Geral
```
Como você funciona?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent`
- Will Consult: `false`
- Comportamento: Explica funcionalidades

### Prompt 23: Pergunta Aleatória
```
Qual o significado da vida?
```
**Resultado Esperado:**
- Intent: `general`
- Agente: `CharleeAgent`
- Will Consult: `false`
- Comportamento: Resposta filosófica/conversacional

---

## 🧪 Casos de Teste Complexos

### Prompt 24: Múltiplos Intents (Wellness + Capacity)
```
Estou muito cansada e com muita sobrecarga de trabalho
```
**Resultado Esperado:**
- Intent: `wellness` (primeiro match)
- Agente: `CycleAwareAgent`
- Keywords: `["cansada", "sobrecarga", "trabalho"]`
- **Nota:** Sistema prioriza wellness sobre capacity quando ambos detectados

### Prompt 25: Tarefa + Capacidade Explícita
```
Criar nova tarefa mas estou preocupada com sobrecarga
```
**Resultado Esperado:**
- Intent: `tasks` (ou `capacity` dependendo de ordem)
- Comportamento: Verifica capacidade antes de criar

### Prompt 26: Planejamento com Contexto de Energia
```
Planejar minha semana considerando que estou com baixa energia
```
**Resultado Esperado:**
- Intent: `general` (ou `wellness`)
- Will Consult: `true`
- Comportamento: Injeta contexto de energia no planejamento

---

## 📊 Scripts de Teste Rápido

### Teste 1: Validar Todos os Intents
```bash
#!/bin/bash

# Wellness
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "Estou cansada"}' | jq

# Capacity
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "Novo projeto"}' | jq

# Tasks
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "Criar tarefa"}' | jq

# General
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "Oi Charlee"}' | jq
```

### Teste 2: Status do Orquestrador
```bash
curl http://localhost:8000/api/v1/agent/status?user_id=samara | jq
```

### Teste 3: Tools Disponíveis
```bash
curl http://localhost:8000/api/v1/agent/tools | jq
```

---

## ✅ Checklist de Validação

### Testes de Intent Detection
- [ ] Prompt 1-5: Wellness detectado corretamente
- [ ] Prompt 6-11: Capacity detectado corretamente
- [ ] Prompt 12-16: Tasks detectado corretamente
- [ ] Prompt 17-20: General com consulta detectado
- [ ] Prompt 21-23: General sem consulta detectado

### Testes de Roteamento
- [ ] Wellness → CycleAwareAgent
- [ ] Capacity → CapacityGuardAgent
- [ ] Tasks → CharleeAgent (com capacity check)
- [ ] General + consultation → CharleeAgent (multi-agent)
- [ ] General → CharleeAgent (simples)

### Testes de Funcionalidade
- [ ] Capacity check automático ao criar tarefa
- [ ] Consulta multi-agente em planejamento
- [ ] Context injection funciona corretamente
- [ ] Status endpoint retorna dados corretos
- [ ] Analyze-routing retorna keywords corretas

### Testes de Edge Cases
- [ ] Prompt com múltiplos intents
- [ ] Prompt vazio
- [ ] Prompt muito longo
- [ ] Caracteres especiais
- [ ] Múltiplos idiomas (se aplicável)

---

## 📝 Template de Teste Manual

```markdown
### Teste: [NOME]

**Prompt:**
```
[SEU_PROMPT_AQUI]
```

**Comando:**
```bash
curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \
  -H "Content-Type: application/json" \
  -d '{"message": "SEU_PROMPT_AQUI"}'
```

**Resultado Esperado:**
- Intent: `[wellness|capacity|tasks|general]`
- Agente: `[nome_do_agente]`
- Keywords: `[lista]`

**Resultado Real:**
```json
[COLAR_RESPOSTA_AQUI]
```

**Status:** ✅ PASS / ❌ FAIL

**Notas:**
[Observações adicionais]
```

---

## 🎯 Métricas de Sucesso

- ✅ 95%+ de precisão na detecção de intent
- ✅ Roteamento correto para agente apropriado
- ✅ Capacity check funciona em 100% das criações de tarefa
- ✅ Multi-agent consultation funciona em planejamentos
- ✅ Context injection enriquece respostas

---

**Última atualização:** 2025-01-08
**Branch:** feat/intelligent-agent-orchestration
