# 🌙 Charlee Optimizer - Módulo de Gestão de Otimização Contínua

**Versão:** V5.0 (Planejado)
**Status:** 🔴 Não Implementado
**Prioridade:** 🔥 Alta (Sistema Nervoso Executivo)
**Dependências:** Todos os módulos (atua como meta-orquestrador)

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura de Agentes](#2-arquitetura-de-agentes)
3. [Funções Principais](#3-funções-principais)
4. [Arquitetura Interna](#4-arquitetura-interna)
5. [Implementação dos Agentes](#5-implementação-dos-agentes)
6. [Exemplos de Otimizações Práticas](#6-exemplos-de-otimizações-práticas)
7. [Aprendizado Adaptativo](#7-aprendizado-adaptativo)
8. [Níveis de Autonomia](#8-níveis-de-autonomia)
9. [Interações com Outros Módulos](#9-interações-com-outros-módulos)
10. [Schemas de Banco de Dados](#10-schemas-de-banco-de-dados)
11. [API Endpoints](#11-api-endpoints)
12. [Métricas e Analytics](#12-métricas-e-analytics)
13. [Roadmap de Implementação](#13-roadmap-de-implementação)

---

## 1. Visão Geral

### 1.1 O que é o Charlee Optimizer?

O **Charlee Optimizer** é o **Sistema Nervoso Executivo** do Charlee - o módulo que:

- 🧠 **Aprende continuamente** com seu comportamento
- ⚡ **Melhora a performance** técnica e operacional
- 💰 **Reduz custos** (tokens, API calls, processamento)
- 🔄 **Adapta automações** ao seu estilo de vida
- 🎯 **Otimiza fluxos** de trabalho e produtividade
- 🌟 **Antecipa necessidades** antes que você perceba

### 1.2 Por que este módulo é crítico?

**Sem o Optimizer:**
- Charlee consome tokens desnecessariamente
- Fluxos ficam engessados e desatualizados
- Duplicações e redundâncias se acumulam
- Performance degrada ao longo do tempo
- Você precisa ajustar tudo manualmente

**Com o Optimizer:**
- ✅ Sistema **se auto-aprimora** continuamente
- ✅ Custos **reduzem naturalmente** ao longo do tempo
- ✅ Fluxos **se adaptam** ao seu estilo de vida
- ✅ Performance **melhora** com o uso
- ✅ Você **não precisa pensar** em otimização

### 1.3 Diferencial Competitivo

Este módulo transforma Charlee de **ferramenta estática** em **parceiro evolutivo**.

**Exemplo:**
```
Janeiro 2026:
  - Charlee responde tudo de forma genérica
  - Consome 500k tokens/mês
  - Você precisa ajustar manualmente

Junho 2026 (com Optimizer):
  - Charlee responde no SEU estilo
  - Consome 200k tokens/mês (60% redução)
  - Antecipa suas necessidades
  - Se adapta automaticamente às mudanças
```

---

## 2. Arquitetura de Agentes

O **Charlee Optimizer** não é um módulo monolítico — é um **orquestrador leve** que coordena **5 agentes especializados**, cada um com domínio, autonomia e responsabilidade próprios.

```
OptimizationOrchestrator
├── TechOptimizerAgent      → custo, performance, infraestrutura
├── LifeFlowAgent           → rotinas, produtividade, padrões de vida
├── CommStyleAgent          → comunicação, tom, relações interpessoais
├── OrgCleanerAgent         → organização, dados, deduplicação
└── StrategyAdvisorAgent    → decisões de alto nível, ecossistema
```

O orquestrador **não otimiza nada diretamente** — ele agenda, prioriza, consolida os relatórios dos agentes e decide o que apresentar para você.

---

### 2.1 🖥️ TechOptimizerAgent

**Domínio:** Infraestrutura, custos e performance técnica

**Responsabilidades:**
- Monitorar consumo de tokens (GPT-4o, Whisper, embeddings)
- Gerenciar cache inteligente de respostas repetidas
- Escolher automaticamente o modelo adequado (gpt-4o vs gpt-4o-mini)
- Detectar duplicações de dados e compressão de histórico antigo
- Identificar lentidão, gargalos e erros recorrentes

**Input:** Logs de API, métricas de latência, registros de uso de LLM
**Output:** Relatório de custos, regras de roteamento de modelos, alertas de performance
**Autonomia padrão:** Aplica otimizações técnicas automaticamente (sem confirmação)

---

### 2.2 📊 LifeFlowAgent

**Domínio:** Rotinas, produtividade e padrões de comportamento

**Responsabilidades:**
- Detectar padrões de comportamento (horários, dias, tipos de tarefa)
- Sugerir simplificações de processos repetitivos
- Criar e ajustar rotinas personalizadas com base no uso real
- Identificar gargalos de tempo, energia e foco
- Priorizar tarefas de forma contextual

**Input:** Eventos do sistema, histórico de agenda, dados do Wellness
**Output:** Sugestões de rotina, alertas de sobrecarga, redistribuições de tarefas
**Autonomia padrão:** Modo assistido (sugere, aguarda confirmação)

---

### 2.3 💬 CommStyleAgent

**Domínio:** Comunicação, escrita e relações interpessoais

**Responsabilidades:**
- Aprender o estilo de escrita da Samara ao longo do tempo
- Aprender o estilo das pessoas com quem ela se comunica
- Sugerir respostas mais eficientes e diretas
- Preparar mensagens que reduzem idas e vindas
- Detectar potenciais conflitos antes de acontecerem
- Ajustar tom conforme contexto (Imperatriz Graciosa, técnico, pessoal)

**Input:** Histórico de mensagens, feedbacks de comunicação, perfis de contatos
**Output:** Templates de resposta, alertas de tom inadequado, sugestões de reformulação
**Autonomia padrão:** Sugestivo (nunca envia mensagens sem aprovação)

---

### 2.4 🗂️ OrgCleanerAgent

**Domínio:** Organização de dados, bases e estruturas

**Responsabilidades:**
- Agrupar tags e categorias semelhantes automaticamente
- Detectar e remover redundâncias (Notion, Drive, banco de dados)
- Arquivar itens "mortos" (documentos antigos, projetos cancelados)
- Ajustar estrutura de dados para melhor performance
- Criar índices e atalhos inteligentes

**Input:** Estado atual do Notion, Drive, banco de dados Charlee
**Output:** Relatório de redundâncias, lista de arquivamentos sugeridos, novos índices
**Autonomia padrão:** Modo assistido (lista o que vai limpar antes de executar)

---

### 2.5 🎯 StrategyAdvisorAgent

**Domínio:** Decisões de alto nível e ecossistema de negócios

**Responsabilidades:**
- Sugerir melhorias operacionais na WickedBotz e no Summit
- Identificar gargalos de liderança e redistribuição de funções
- Apontar oportunidades de eficiência no ecossistema
- Detectar riscos estratégicos antes que se materializem
- Consolidar padrões dos outros agentes em insights executivos

**Input:** Dados agregados de todos os outros agentes, contexto de negócios
**Output:** Relatório semanal de insights estratégicos, alertas de risco
**Autonomia padrão:** Somente sugestivo (nunca age diretamente)

---

## 3. Funções Principais

### 3.1 Aprendizado Contínuo

```python
# O Optimizer aprende observando:
aprendizado = {
    "preferências_explícitas": [
        "Usuária ativou 'modo silencioso' após 20h",
        "Usuária prefere resumos concisos (não extensos)",
        "Usuária gosta de notificações via push (não email)"
    ],
    "padrões_comportamentais": [
        "Trabalha melhor entre 9h-12h (foco profundo)",
        "Segundas-feiras sempre sobrecarregadas",
        "Ignora tarefas <5min (não são prioritárias para ela)"
    ],
    "feedbacks_implícitos": [
        "Ignorou sugestão de reunião 3x → não sugerir mais",
        "Aceitou reorganização de agenda 5x → automatizar",
        "Deletou documento auto-gerado → não gerar mais"
    ]
}
```

### 3.2 Detecção de Padrões

**Padrões de Tempo:**
- Horários de pico de energia
- Dias da semana mais produtivos
- Momentos de procrastinação recorrente

**Padrões de Trabalho:**
- Tipos de tarefas mais frequentes
- Projetos que consomem mais tempo
- Atividades que geram mais valor

**Padrões Emocionais:**
- Gatilhos de stress (via Wellness + Listener)
- Momentos de fadiga de decisão
- Correlação entre ciclo menstrual e produtividade

**Padrões de Comunicação:**
- Pessoas que você responde rapidamente vs. devagar
- Tipos de mensagem que você ignora
- Tom de voz em diferentes contextos

### 3.3 Geração de Otimizações

**Exemplo 1: Otimização de Agenda**
```
[LifeFlowAgent detecta]
→ Segundas-feiras: 8 reuniões (média 6h de reunião)
→ Terças-feiras: 2 reuniões (média 1.5h)

[LifeFlowAgent sugere ao Orchestrator]
💡 "Notei que segundas estão sobrecarregadas.
   Posso redistribuir 2 reuniões para terça?"

[Usuária aceita]

[OptimizationOrchestrator executa via Calendar]
✅ Moveu "1-on-1 com Ana" para terça 10h
✅ Moveu "Review de PRs" para terça 14h
✅ Resultado: Segunda com 4h de reunião (mais sustentável)
```

**Exemplo 2: Otimização de Custos**
```
[TechOptimizerAgent detecta]
→ 40% das queries usam GPT-4o para tarefas simples
→ Custo: $200/mês desnecessários

[TechOptimizerAgent aplica automaticamente]
✅ Criou regra: "Resumos curtos → usar gpt-4o-mini"
✅ Criou regra: "Análises complexas → usar gpt-4o"

[Resultado após 1 mês]
✅ Redução de 35% no custo de tokens
✅ Performance mantida (usuária não notou diferença)
```

---

## 4. Arquitetura Interna

### 4.1 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│               CHARLEE OPTIMIZER (Meta-Orquestrador)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │            OptimizationOrchestrator (Coordenador)             │  │
│  │  • Agenda e prioriza execução dos agentes                     │  │
│  │  • Consolida relatórios e decide o que apresentar             │  │
│  │  • NÃO otimiza diretamente — delega sempre                    │  │
│  └──────────────────────────┬────────────────────────────────────┘  │
│                             │                                        │
│      ┌──────────────────────┼───────────────────┬──────────────┐    │
│      │          ┌───────────┴──────┐             │              │    │
│      ▼          ▼                  ▼             ▼              ▼    │
│  ┌────────┐ ┌─────────┐  ┌──────────────┐ ┌─────────┐ ┌──────────┐ │
│  │ Tech   │ │LifeFlow │  │  CommStyle   │ │  Org    │ │Strategy  │ │
│  │Optim.  │ │ Agent   │  │    Agent     │ │Cleaner  │ │Advisor   │ │
│  │        │ │         │  │              │ │ Agent   │ │ Agent    │ │
│  │• Tokens│ │• Rotinas│  │• Tom/Estilo  │ │• Dedup. │ │• Riscos  │ │
│  │• Cache │ │• Padrões│  │• Conflitos   │ │• Limpeza│ │• Estratég│ │
│  │• Modelos│ │• Foco  │  │• Respostas   │ │• Índices│ │• Ecossist│ │
│  └────────┘ └─────────┘  └──────────────┘ └─────────┘ └──────────┘ │
│      │           │               │               │           │       │
│      └───────────┴───────────────┴───────────────┴───────────┘       │
│                                       │                              │
│                                       ▼                              │
│                           ┌──────────────────┐                       │
│                           │ OPTIMIZATION DB  │                       │
│                           │ • Padrões        │                       │
│                           │ • Sugestões      │                       │
│                           │ • Otimiz. Aplic. │                       │
│                           └──────────────────┘                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
         ┌─────────┐          ┌──────────┐          ┌─────────┐
         │ TODOS   │          │ EVENT    │          │MÓDULOS  │
         │ MÓDULOS │◀─────────│  BUS     │─────────▶│EXTERNOS │
         │ CHARLEE │  observa │(Calendar)│  age em  │(Notion, │
         └─────────┘          └──────────┘          │ Drive)  │
                                                     └─────────┘
```

### 4.2 Fluxo de Otimização

```
1. Agentes coletam dados de forma independente e contínua
   │
   ├─▶ [TechOptimizerAgent]   → métricas de tokens, latência, erros
   ├─▶ [LifeFlowAgent]        → eventos de agenda, padrões de comportamento
   ├─▶ [CommStyleAgent]       → histórico de mensagens, feedbacks de tom
   ├─▶ [OrgCleanerAgent]      → estado de Notion, Drive, banco de dados
   └─▶ [StrategyAdvisorAgent] → dados agregados dos outros 4 agentes

2. Cada agente detecta padrões no seu domínio
   │
   ├─▶ TechOptimizer:  "GPT-4o usado 60% para tarefas simples"
   ├─▶ LifeFlow:       "Segundas sempre sobrecarregadas"
   ├─▶ CommStyle:      "Tom agressivo em e-mails enviados às 23h"
   ├─▶ OrgCleaner:     "47 documentos duplicados no Drive"
   └─▶ StrategyAdvisor:"WickedBotz com gargalo no processo de onboarding"

3. Cada agente gera sugestões e envia ao Orchestrator
   │
   ├─▶ TechOptimizer:  "Criar regra de roteamento por complexidade"
   ├─▶ LifeFlow:       "Redistribuir 2 reuniões de segunda para terça"
   ├─▶ CommStyle:      "Alertar antes de enviar mensagens após 22h"
   ├─▶ OrgCleaner:     "Arquivar 47 duplicados (lista para revisão)"
   └─▶ StrategyAdvisor:"Revisar fluxo de onboarding na WickedBotz"

4. [OptimizationOrchestrator] Prioriza e executa conforme autonomia
   │
   ├─▶ Autonomia Total:    aplica imediatamente (TechOptimizer)
   ├─▶ Modo Assistido:     pede confirmação antes de aplicar (LifeFlow, OrgCleaner)
   └─▶ Modo Sugestivo:     apresenta insight sem agir (CommStyle, StrategyAdvisor)

5. [OptimizationOrchestrator] Registra o ciclo no banco
   │
   ├─▶ Salva métricas, padrões detectados e sugestões geradas
   └─▶ Emite evento `optimizer.cycle_completed` no event bus

6. [Feedback Loop] Monitora resultados
   │
   ├─▶ Otimização funcionou? (sucesso)
   ├─▶ Usuária reverteu? (falha - aprender)
   └─▶ Nenhuma ação? (neutro - reavaliar)
```

---

## 5. Implementação dos Agentes

### 5.1 TechOptimizerAgent

**Responsabilidade:** Monitorar custos, performance e infraestrutura técnica

```python
# backend/modules/optimizer/agents/tech_optimizer.py

from typing import Dict, List

class TechOptimizerAgent:
    """
    Monitora custos de API, performance técnica e escolha de modelos.
    Age com autonomia total — não requer confirmação da usuária.
    """

    def __init__(self, db_connection, event_bus):
        self.db = db_connection
        self.event_bus = event_bus

    async def collect_and_optimize(self) -> Dict:
        costs = await self._analyze_costs()
        performance = await self._analyze_performance()
        suggestions = self._generate_suggestions(costs, performance)

        # Aplica automaticamente — autonomia total
        for s in suggestions:
            await self._apply(s)

        return {"costs": costs, "performance": performance, "applied": suggestions}

    async def _analyze_costs(self) -> Dict:
        token_usage = self.db.execute("""
            SELECT model,
                   SUM(input_tokens)  AS total_input,
                   SUM(output_tokens) AS total_output,
                   AVG(input_tokens)  AS avg_input,
                   COUNT(*)           AS call_count
            FROM llm_usage_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY model
        """).fetchall()

        PRICING = {
            "gpt-4o":      {"input": 0.0025,  "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        }
        total_cost = sum(
            (u["total_input"] / 1000) * PRICING.get(u["model"], {}).get("input", 0) +
            (u["total_output"] / 1000) * PRICING.get(u["model"], {}).get("output", 0)
            for u in token_usage if u["model"] in PRICING
        )
        return {"token_usage": token_usage, "total_cost_month": total_cost}

    async def _analyze_performance(self) -> Dict:
        latency = self.db.execute("""
            SELECT endpoint,
                   AVG(response_time_ms) AS avg_latency,
                   COUNT(*)              AS request_count
            FROM api_logs
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            GROUP BY endpoint
            ORDER BY avg_latency DESC
        """).fetchall()

        error_rate = self.db.execute("""
            SELECT COUNT(CASE WHEN status_code >= 400 THEN 1 END)::float /
                   COUNT(*)::float AS error_rate
            FROM api_logs
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """).fetchone()["error_rate"]

        return {
            "slow_endpoints": [e for e in latency if e["avg_latency"] > 2000],
            "error_rate": error_rate,
        }

    def _generate_suggestions(self, costs, performance) -> List[Dict]:
        suggestions = []

        # Roteamento de modelos: chamadas curtas não precisam de gpt-4o
        for u in costs["token_usage"]:
            if u["model"] == "gpt-4o" and u["avg_input"] < 500:
                suggestions.append({
                    "action": "add_model_routing_rule",
                    "rule": {"max_tokens": 500, "use_model": "gpt-4o-mini"},
                    "reason": f"{u['call_count']} chamadas curtas em gpt-4o"
                })

        # Alertas de endpoints lentos
        for ep in performance["slow_endpoints"]:
            suggestions.append({
                "action": "flag_slow_endpoint",
                "endpoint": ep["endpoint"],
                "avg_latency_ms": ep["avg_latency"],
            })

        return suggestions

    async def _apply(self, suggestion: Dict):
        await self.event_bus.emit("optimizer.tech_action", suggestion)
```

### 5.2 LifeFlowAgent

**Responsabilidade:** Detectar padrões de rotina e produtividade, sugerir redistribuições

```python
# backend/modules/optimizer/agents/life_flow.py

from typing import Dict, List
import numpy as np

class LifeFlowAgent:
    """
    Analisa padrões de tempo, tarefas e energia.
    Opera em modo assistido — sugere, aguarda confirmação.
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def analyze(self, user_id: str) -> Dict:
        return {
            "time_patterns":   await self._time_patterns(user_id),
            "task_patterns":   await self._task_patterns(user_id),
            "energy_patterns": await self._energy_patterns(user_id),
            "suggestions":     await self._generate_suggestions(user_id),
        }

    async def _time_patterns(self, user_id: str) -> Dict:
        by_hour = self.db.execute("""
            SELECT EXTRACT(HOUR FROM criado_em) AS hour,
                   COUNT(*) AS activity_count
            FROM system_events
            WHERE user_id = %s AND criado_em > NOW() - INTERVAL '30 days'
            GROUP BY hour ORDER BY hour
        """, (user_id,)).fetchall()

        avg = np.mean([a["activity_count"] for a in by_hour]) if by_hour else 0
        peak_hours = [a["hour"] for a in by_hour if a["activity_count"] > avg * 1.5]

        by_weekday = self.db.execute("""
            SELECT EXTRACT(DOW FROM criado_em) AS weekday,
                   COUNT(*) AS activity_count
            FROM system_events
            WHERE user_id = %s AND criado_em > NOW() - INTERVAL '30 days'
            GROUP BY weekday ORDER BY weekday
        """, (user_id,)).fetchall()

        names = ["Domingo","Segunda","Terça","Quarta","Quinta","Sexta","Sábado"]
        busiest = sorted(by_weekday, key=lambda x: x["activity_count"], reverse=True)[:3]

        return {
            "peak_hours": peak_hours,
            "busiest_days": [names[int(d["weekday"])] for d in busiest],
        }

    async def _task_patterns(self, user_id: str) -> Dict:
        ignored = self.db.execute("""
            SELECT descricao, COUNT(*) AS ignore_count,
                   AVG(EXTRACT(EPOCH FROM (NOW() - criado_em))/3600) AS avg_age_hours
            FROM tarefas
            WHERE user_id = %s AND status = 'pending'
              AND criado_em < NOW() - INTERVAL '7 days'
            GROUP BY descricao HAVING COUNT(*) > 2
            ORDER BY ignore_count DESC LIMIT 5
        """, (user_id,)).fetchall()

        return {"ignored_tasks": ignored}

    async def _energy_patterns(self, user_id: str) -> Dict:
        cycle = self.db.execute("""
            SELECT c.fase_ciclo, COUNT(t.id) AS tasks_completed
            FROM cycle_tracking c
            LEFT JOIN tarefas t ON t.user_id = c.user_id
              AND DATE(t.completado_em) = c.data
            WHERE c.user_id = %s AND c.data > NOW() - INTERVAL '90 days'
              AND t.completado_em IS NOT NULL
            GROUP BY c.fase_ciclo
        """, (user_id,)).fetchall()

        most_productive = max(cycle, key=lambda x: x["tasks_completed"]) if cycle else None
        return {"cycle_productivity": cycle, "most_productive_phase": most_productive}

    async def _generate_suggestions(self, user_id: str) -> List[Dict]:
        patterns = await self._time_patterns(user_id)
        suggestions = []

        if "Segunda" in patterns.get("busiest_days", []):
            suggestions.append({
                "id": "lifeflow_001",
                "title": "Redistribuir carga de segunda-feira",
                "description": "Segundas estão consistentemente sobrecarregadas. Redistribuir 2 reuniões para terça?",
                "action": "redistribute_meetings",
                "params": {"from_day": "Monday", "to_days": ["Tuesday","Wednesday"], "max_to_move": 2},
                "autonomy": "assistido",
            })

        return suggestions
```

### 5.3 CommStyleAgent

**Responsabilidade:** Aprender estilos de comunicação e prevenir conflitos

```python
# backend/modules/optimizer/agents/comm_style.py

from typing import Dict, List

class CommStyleAgent:
    """
    Analisa padrões de comunicação e tom.
    Opera em modo sugestivo — nunca age sem aprovação explícita.
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def analyze(self, user_id: str) -> Dict:
        patterns = await self._communication_patterns(user_id)
        suggestions = self._generate_suggestions(patterns)
        return {"patterns": patterns, "suggestions": suggestions}

    async def _communication_patterns(self, user_id: str) -> Dict:
        interactions = self.db.execute("""
            SELECT payload->>'pessoa_id' AS pessoa_id,
                   COUNT(*) AS interaction_count,
                   AVG(EXTRACT(EPOCH FROM (respondido_em - criado_em))/60) AS avg_response_min
            FROM system_events
            WHERE user_id = %s AND modulo_origem = 'diplomat'
              AND criado_em > NOW() - INTERVAL '30 days'
            GROUP BY pessoa_id
            ORDER BY interaction_count DESC
        """, (user_id,)).fetchall()

        late_messages = self.db.execute("""
            SELECT COUNT(*) AS count
            FROM mensagens_enviadas
            WHERE user_id = %s AND EXTRACT(HOUR FROM enviado_em) >= 22
              AND enviado_em > NOW() - INTERVAL '30 days'
        """, (user_id,)).fetchone()

        return {
            "top_contacts": interactions[:5],
            "late_night_messages": late_messages["count"] if late_messages else 0,
        }

    def _generate_suggestions(self, patterns: Dict) -> List[Dict]:
        suggestions = []

        if patterns["late_night_messages"] > 5:
            suggestions.append({
                "id": "comm_001",
                "title": "Mensagens tardias detectadas",
                "description": f"{patterns['late_night_messages']} mensagens enviadas após 22h no último mês. Deseja ativar alerta antes de enviar nesses horários?",
                "action": "enable_late_message_alert",
                "autonomy": "sugestivo",
            })

        return suggestions
```

### 5.4 OrgCleanerAgent

**Responsabilidade:** Detectar redundâncias e manter dados limpos

```python
# backend/modules/optimizer/agents/org_cleaner.py

from typing import Dict, List

class OrgCleanerAgent:
    """
    Identifica duplicações, arquivos mortos e tags redundantes.
    Opera em modo assistido — lista tudo antes de executar.
    """

    def __init__(self, db_connection, notion_client, drive_client):
        self.db = db_connection
        self.notion = notion_client
        self.drive = drive_client

    async def audit(self, user_id: str) -> Dict:
        tags = await self._find_redundant_tags(user_id)
        dead_items = await self._find_dead_items(user_id)
        return {
            "redundant_tags": tags,
            "dead_items": dead_items,
            "suggestions": self._generate_suggestions(tags, dead_items),
        }

    async def _find_redundant_tags(self, user_id: str) -> List[Dict]:
        return self.db.execute("""
            SELECT tag, COUNT(*) AS usage_count
            FROM item_tags
            WHERE user_id = %s
            GROUP BY tag
            ORDER BY usage_count DESC
        """, (user_id,)).fetchall()

    async def _find_dead_items(self, user_id: str) -> Dict:
        dead_tasks = self.db.execute("""
            SELECT id, descricao, criado_em
            FROM tarefas
            WHERE user_id = %s AND status = 'pending'
              AND criado_em < NOW() - INTERVAL '90 days'
        """, (user_id,)).fetchall()

        return {"dead_tasks": dead_tasks}

    def _generate_suggestions(self, tags, dead_items) -> List[Dict]:
        suggestions = []

        if dead_items["dead_tasks"]:
            count = len(dead_items["dead_tasks"])
            suggestions.append({
                "id": "org_001",
                "title": f"Arquivar {count} tarefas antigas",
                "description": f"{count} tarefas pendentes há mais de 90 dias. Deseja arquivá-las?",
                "action": "archive_dead_tasks",
                "autonomy": "assistido",
            })

        return suggestions
```

### 5.5 StrategyAdvisorAgent

**Responsabilidade:** Consolidar insights dos outros agentes em recomendações executivas

```python
# backend/modules/optimizer/agents/strategy_advisor.py

from typing import Dict, List

class StrategyAdvisorAgent:
    """
    Agrega saídas dos 4 agentes e gera insights de alto nível.
    Opera exclusivamente em modo sugestivo — nunca age diretamente.
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def advise(self, aggregated_data: Dict) -> Dict:
        risks = self._detect_risks(aggregated_data)
        opportunities = self._detect_opportunities(aggregated_data)
        return {
            "risks": risks,
            "opportunities": opportunities,
            "weekly_report": self._build_report(risks, opportunities),
        }

    def _detect_risks(self, data: Dict) -> List[Dict]:
        risks = []

        cost = data.get("tech", {}).get("costs", {}).get("total_cost_month", 0)
        if cost > 300:
            risks.append({
                "area": "custos",
                "severity": "high",
                "description": f"Custo mensal de tokens em ${cost:.0f} — acima do limite recomendado de $300.",
                "action_suggested": "Revisar regras de roteamento de modelos com TechOptimizerAgent",
            })

        dead_tasks = data.get("org", {}).get("dead_items", {}).get("dead_tasks", [])
        if len(dead_tasks) > 20:
            risks.append({
                "area": "organização",
                "severity": "medium",
                "description": f"{len(dead_tasks)} tarefas abandonadas acumuladas — risco de perda de contexto.",
                "action_suggested": "Executar limpeza via OrgCleanerAgent",
            })

        return risks

    def _detect_opportunities(self, data: Dict) -> List[Dict]:
        opportunities = []

        energy = data.get("life_flow", {}).get("energy_patterns", {})
        phase = energy.get("most_productive_phase")
        if phase:
            opportunities.append({
                "area": "produtividade",
                "description": f"Fase '{phase['fase_ciclo']}' é a mais produtiva. Agendar decisões estratégicas nesse período.",
            })

        return opportunities

    def _build_report(self, risks, opportunities) -> str:
        lines = ["## Relatório Semanal — Charlee Optimizer\n"]
        if risks:
            lines.append("### ⚠️ Riscos Detectados")
            for r in risks:
                lines.append(f"- **{r['area'].title()}** ({r['severity']}): {r['description']}")
        if opportunities:
            lines.append("\n### ✨ Oportunidades")
            for o in opportunities:
                lines.append(f"- **{o['area'].title()}**: {o['description']}")
        return "\n".join(lines)
```

### 5.6 OptimizationOrchestrator

**Responsabilidade:** Coordenar os 5 agentes, consolidar relatórios, nunca otimizar diretamente

```python
# backend/modules/optimizer/orchestrator.py

from typing import List
from enum import Enum

class OptimizationOrchestrator:
    """
    Coordenador central. Delega tudo para os agentes especializados.
    Não detecta padrões nem aplica otimizações diretamente.
    """

    def __init__(
        self,
        db_connection,
        event_bus,
        tech_optimizer: TechOptimizerAgent,
        life_flow: LifeFlowAgent,
        comm_style: CommStyleAgent,
        org_cleaner: OrgCleanerAgent,
        strategy_advisor: StrategyAdvisorAgent,
    ):
        self.db = db_connection
        self.event_bus = event_bus
        self.tech = tech_optimizer
        self.life = life_flow
        self.comm = comm_style
        self.org = org_cleaner
        self.strategy = strategy_advisor

    async def run_cycle(self, user_id: str):
        """
        Ciclo diário de otimização — chamado automaticamente a cada 24h.
        """

        # 1. Coleta paralela — cada agente trabalha no seu domínio
        tech_data  = await self.tech.collect_and_optimize()        # autonomia total
        life_data  = await self.life.analyze(user_id)              # modo assistido
        comm_data  = await self.comm.analyze(user_id)              # sugestivo
        org_data   = await self.org.audit(user_id)                 # modo assistido

        # 2. Strategy recebe os dados agregados dos outros 4
        strategy_data = await self.strategy.advise({
            "tech": tech_data,
            "life_flow": life_data,
            "comm": comm_data,
            "org": org_data,
        })

        # 3. Distribuir sugestões conforme autonomia de cada agente
        all_suggestions = (
            life_data["suggestions"] +
            comm_data["suggestions"] +
            org_data["suggestions"]
        )
        await self._dispatch_suggestions(user_id, all_suggestions)

        # 4. Registrar ciclo
        self.db.execute("""
            INSERT INTO optimizer_cycles
                (user_id, tech_report, life_report, comm_report,
                 org_report, strategy_report, executado_em)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (user_id,
              json.dumps(tech_data), json.dumps(life_data),
              json.dumps(comm_data), json.dumps(org_data),
              json.dumps(strategy_data)))

        await self.event_bus.emit("optimizer.cycle_completed", {"user_id": user_id})

    async def _dispatch_suggestions(self, user_id: str, suggestions: List[Dict]):
        for s in suggestions:
            if s["autonomy"] == "assistido":
                await self._request_confirmation(user_id, s)
            elif s["autonomy"] == "sugestivo":
                await self._send_notification(user_id, s)
            # "total" nunca chega aqui — TechOptimizer aplica diretamente

    async def _request_confirmation(self, user_id: str, suggestion: Dict):
        await self.event_bus.emit("optimizer.confirmation_needed", {
            "user_id": user_id, "suggestion": suggestion
        })

    async def _send_notification(self, user_id: str, suggestion: Dict):
        await self.event_bus.emit("optimizer.suggestion_ready", {
            "user_id": user_id, "suggestion": suggestion
        })
```

---

## 6. Exemplos de Otimizações Práticas

### 6.1 ⚙️ Reduzir Custo e Acelerar o Sistema

**Otimização 1: Uso inteligente de modelos**

```python
# Antes (custo alto)
def responder_usuario(pergunta: str):
    return openai.chat.completions.create(
        model="gpt-4o",  # sempre usa o modelo caro
        messages=[{"role": "user", "content": pergunta}]
    )

# Depois (otimizado)
def responder_usuario(pergunta: str):
    # Avaliar complexidade
    complexity = avaliar_complexidade(pergunta)

    if complexity == "simples":
        model = "gpt-4o-mini"  # 94% mais barato
    else:
        model = "gpt-4o"

    return openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": pergunta}]
    )

# Resultado: 60% de redução de custo sem perda de qualidade
```

**Otimização 2: Cache de respostas repetidas**

```python
# Sistema detecta que você pergunta a mesma coisa 5x/semana
perguntas_frequentes = [
    "Qual o status do projeto X?",
    "Quantas tarefas tenho pendentes?",
    "Qual minha próxima reunião?"
]

# Charlee implementa cache de 1h para essas queries
# Redução: 30% menos chamadas de API
```

### 6.2 ✨ Melhorar sua Rotina Pessoal

**Otimização 3: Redistribuição de agenda**

```
[LifeFlowAgent detecta]
→ Segundas: 8 reuniões (6h de reunião)
→ Terças: 2 reuniões (1.5h)

[LifeFlowAgent → Orchestrator (modo assistido)]
💡 "Notei que segundas estão sobrecarregadas. Posso redistribuir 2 reuniões para terça?"

[Usuária aceita]

[Orchestrator executa via Calendar]
✅ Segunda: 4h de reunião (sustentável)
✅ Terça: 3.5h de reunião (ainda confortável)
✅ Redução de 30% no stress de segunda-feira
```

**Otimização 4: Bloco de foco automático**

```
[LifeFlowAgent detecta]
→ Você tem >15 tarefas pendentes há 2 semanas
→ Tarefas de deep work não são completadas

[LifeFlowAgent → Orchestrator (modo assistido)]
💡 "Posso criar um bloco de foco de 2h terça-feira 9h-11h para tarefas de programação?"

[Usuária aceita]

[Orchestrator executa via Calendar]
✅ Bloco recorrente criado
✅ Notificações desabilitadas durante o bloco
✅ Produtividade aumenta 40% nesse período
```

### 6.3 🔧 Otimizar Drive/Notion Automaticamente

**Otimização 5: Consolidação de páginas**

```
[OrgCleanerAgent detecta]
→ 5 páginas no Notion com título similar: "Reunião WickedBotz"
→ Conteúdo 80% duplicado

[OrgCleanerAgent → Orchestrator (modo assistido)]
💡 "Detectei 5 páginas similares sobre reuniões WickedBotz. Posso consolidar em uma?"

[Usuária aceita]

[Orchestrator executa via Notion]
✅ 1 página master criada com timeline de todas as reuniões
✅ 4 páginas antigas arquivadas
✅ Navegação 50% mais rápida
```

**Otimização 6: Limpeza de arquivos "mortos"**

```
[OrgCleanerAgent detecta]
→ 20 arquivos no Drive não acessados há >6 meses
→ 10GB de espaço ocupado

[OrgCleanerAgent → Orchestrator (modo assistido)]
💡 "20 arquivos não foram acessados há 6+ meses. Posso movê-los para 'Arquivo Morto'?"

[Usuária aceita]

[Orchestrator executa via Drive]
✅ Arquivos movidos para pasta "Arquivo Morto 2024"
✅ 10GB liberados
✅ Drive mais organizado
```

### 6.4 🤝 Otimizar Comunicação e Relações

**Otimização 7: Preparação de mensagens**

```
[CommStyleAgent detecta via Listener]
→ Você troca 10+ mensagens com pessoa X para marcar 1 reunião
→ Falta de clareza sobre disponibilidade

[CommStyleAgent → Orchestrator (modo sugestivo)]
💡 "Notei que você troca muitas mensagens para marcar reuniões. Posso enviar sua disponibilidade automaticamente?"

[Usuária aceita]

[Orchestrator executa via Diplomat]
✅ Mensagens incluem automaticamente: "Disponível: Ter 14h, Qua 10h, Qui 16h"
✅ Redução de 60% nas idas e vindas
✅ Reuniões marcadas 2x mais rápido
```

**Otimização 8: Ajuste de tom**

```
[CommStyleAgent detecta via Diplomat]
→ Pessoa X responde melhor a tom mais direto
→ Pessoa Y prefere tom mais suave

[CommStyleAgent → Orchestrator (modo sugestivo)]
💡 "Aprendi os estilos de X e Y. Posso ajustar o tom das mensagens automaticamente?"

[Usuária aceita]

[Orchestrator executa via Diplomat]
✅ Pessoa X: "Preciso da aprovação até sexta."
✅ Pessoa Y: "Quando você tiver um tempinho, seria ótimo ter sua aprovação até sexta 🙏"
✅ Taxa de resposta aumenta 30%
✅ Menos atritos em comunicação
```

### 6.5 🧠 Aprimorar Big Rocks e Projetos

**Otimização 9: Detecção precoce de riscos**

```
[StrategyAdvisorAgent agrega dados de LifeFlowAgent + OrgCleanerAgent]
→ Projeto X: 70% das tarefas atrasadas >5 dias
→ Último 1-on-1 com líder técnico foi há 3 semanas

[StrategyAdvisorAgent → Orchestrator (modo sugestivo)]
⚠️ "Projeto X está em risco. Sugiro:"
   • 1-on-1 urgente com líder técnico
   • Revisão de deadlines
   • Redistribuição de 3 tarefas críticas

[Resultado]
✅ Problema identificado 2 semanas antes do deadline
✅ Ações corretivas tomadas a tempo
✅ Projeto entregue dentro do prazo
```

---

## 7. Aprendizado Adaptativo

### 7.1 Como o Charlee Aprende com Você

```python
# O Optimizer aprende através de múltiplos sinais

class AdaptiveLearning:
    """
    Sistema de aprendizado contínuo
    """

    def learn_from_feedback(self, user_id: str, feedback: Dict):
        """
        Aprende com feedback explícito
        """

        if feedback["type"] == "suggestion_accepted":
            # Aumentar peso desse tipo de sugestão
            self._increase_suggestion_weight(feedback["suggestion_id"])

        elif feedback["type"] == "suggestion_rejected":
            # Reduzir peso + aprender por que foi rejeitada
            self._decrease_suggestion_weight(feedback["suggestion_id"])
            self._learn_rejection_reason(feedback["reason"])

    def learn_from_behavior(self, user_id: str, behavior: Dict):
        """
        Aprende com comportamento implícito
        """

        # Usuária reverteu otimização?
        if behavior["action"] == "revert_optimization":
            self._mark_optimization_as_failed(behavior["optimization_id"])

        # Usuária ignorou sugestão 3x?
        if behavior["action"] == "ignored_suggestion":
            if behavior["ignore_count"] >= 3:
                self._stop_suggesting(behavior["suggestion_type"])

    def learn_from_patterns(self, user_id: str, patterns: Dict):
        """
        Aprende com padrões detectados
        """

        # Padrão: usuária sempre aceita redistribuição de reuniões
        if patterns["redistribution_acceptance_rate"] > 0.8:
            self._enable_auto_redistribution()

        # Padrão: usuária nunca usa sugestões de organização
        if patterns["organization_acceptance_rate"] < 0.2:
            self._disable_organization_suggestions()
```

### 7.2 Calibração ao Estilo "Imperatriz Graciosa"

```python
class ImperatrizGraciosaCalibration:
    """
    Ajusta comportamento do Charlee ao estilo de liderança
    """

    IMPERATRIZ_STYLE = {
        "elegância": {
            "comunicação": "concisa e sofisticada",
            "notificações": "discretas e no momento certo",
            "sugestões": "elevadas e estratégicas"
        },
        "serenidade": {
            "urgência": "evitar alarmes desnecessários",
            "tom": "calmo mesmo em crises",
            "apresentação": "organizada e limpa"
        },
        "precisão": {
            "dados": "sempre exatos e verificados",
            "timing": "pontual e alinhado ao contexto",
            "ações": "executadas perfeitamente"
        },
        "suavidade": {
            "interrupções": "mínimas e gentis",
            "transições": "suaves entre contextos",
            "mudanças": "introduzidas gradualmente"
        },
        "proatividade_calma": {
            "antecipação": "problemas resolvidos antes de surgirem",
            "sugestões": "oferecidas, nunca impostas",
            "presença": "sempre disponível, nunca invasiva"
        }
    }

    def calibrate_to_style(self, optimizer_behavior):
        """
        Ajusta comportamento do Optimizer ao estilo Imperatriz
        """

        # Elegância: sugestões elevadas
        optimizer_behavior.suggestion_tone = "estratégico e elevado"

        # Serenidade: sem alarmes desnecessários
        optimizer_behavior.urgency_threshold = 0.8  # apenas crítico

        # Precisão: verificar antes de agir
        optimizer_behavior.confidence_threshold = 0.9  # alta confiança

        # Suavidade: introduzir mudanças gradualmente
        optimizer_behavior.change_velocity = "gradual"

        # Proatividade calma: antecipar sem pressionar
        optimizer_behavior.proactive_mode = "suggestions_only"
```

---

## 8. Níveis de Autonomia

### 8.1 Três Modos de Operação

```python
# backend/modules/optimizer/autonomy.py

class AutonomyLevel(Enum):
    """
    Níveis de autonomia do Optimizer
    """

    SUAVE = "suave"          # 🟢 Apenas sugere
    ASSISTIDO = "assistido"  # 🟡 Confirma antes de agir
    TOTAL = "total"          # 🔴 Age automaticamente

class AutonomyManager:
    """
    Gerencia níveis de autonomia por tipo de ação
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def can_act_autonomously(
        self,
        user_id: str,
        action_type: str
    ) -> bool:
        """
        Verifica se pode agir autonomamente para esse tipo de ação
        """

        # Buscar configuração da usuária
        settings = self.db.execute("""
            SELECT autonomy_settings
            FROM user_settings
            WHERE user_id = %s
        """, (user_id,)).fetchone()["autonomy_settings"]

        # Regras de autonomia por tipo de ação
        autonomy_rules = settings.get("autonomy_rules", {})

        action_autonomy = autonomy_rules.get(action_type, "suave")

        return action_autonomy == "total"

    async def request_confirmation(
        self,
        user_id: str,
        action: Dict
    ) -> bool:
        """
        Solicita confirmação antes de agir (Modo Assistido)
        """

        # Enviar notificação com ações [Sim] [Não]
        notification_id = await self._send_confirmation_request(
            user_id,
            action
        )

        # Aguardar resposta (timeout 24h)
        response = await self._wait_for_response(
            notification_id,
            timeout_hours=24
        )

        return response == "yes"
```

### 8.2 Configuração de Autonomia

```python
# Exemplo de configuração da usuária

AUTONOMY_CONFIG = {
    "global_mode": "assistido",  # padrão

    # Configurações granulares por tipo de ação
    "autonomy_rules": {
        # Modo Total (age sem perguntar)
        "cost_optimization": "total",          # reduzir custos sempre
        "cache_responses": "total",            # cachear respostas sempre
        "cleanup_old_files": "total",          # limpar arquivos antigos
        "consolidate_tags": "total",           # organizar tags

        # Modo Assistido (pergunta antes)
        "redistribute_meetings": "assistido",  # mover reuniões
        "archive_tasks": "assistido",          # arquivar tarefas
        "adjust_notifications": "assistido",   # ajustar notificações

        # Modo Suave (apenas sugere)
        "change_workflow": "suave",            # mudar fluxos de trabalho
        "delete_data": "suave",                # deletar dados
        "strategic_changes": "suave"           # mudanças estratégicas
    },

    # Limites de segurança
    "safety_limits": {
        "max_meetings_to_move_per_week": 3,
        "max_files_to_delete_per_day": 10,
        "max_cost_reduction_per_month": 100  # USD
    }
}
```

---

## 9. Interações com Outros Módulos

O **Optimizer** conversa com **todos os outros módulos** para otimizar o sistema holisticamente:

### 9.1 Optimizer → Calendar

```python
# Otimiza agenda
- Redistribui reuniões sobrecarregadas
- Cria blocos de foco automáticos
- Ajusta horários conforme energia (Wellness)
- Minimiza conflitos
```

### 9.2 Optimizer → Tasks

```python
# Otimiza tarefas
- Arquiva tarefas ignoradas >2 semanas
- Cria rotinas para tarefas repetitivas
- Prioriza automaticamente conforme contexto
- Sugere delegação de tarefas de baixo valor
```

### 9.3 Optimizer → Wellness

```python
# Otimiza bem-estar
- Detecta padrões emocionais
- Ajusta carga de trabalho conforme ciclo
- Sugere pausas estratégicas
- Correlaciona produtividade com energia
```

### 9.4 Optimizer → Diplomat

```python
# Otimiza relacionamentos
- Detecta padrões de comunicação
- Ajusta frequência de 1-on-1s
- Sugere reconhecimento de pessoas negligenciadas
- Prepara mensagens mais eficazes
```

### 9.5 Optimizer → Listener (V5.0)

```python
# Otimiza escuta e análise
- Aprende padrões de fala
- Ajusta confidence scoring
- Melhora detecção de intenções
- Refina análise de soberania
```

### 9.6 Optimizer → Wealth, Routines, Wardrobe (V4.0)

```python
# Otimiza módulos futuros
- Wealth: detecta padrões de gastos → sugere ajustes
- Routines: ajusta rotinas conforme eficácia
- Wardrobe: aprende preferências de estilo → melhora sugestões
```

---

## 10. Schemas de Banco de Dados

```sql
-- Ciclos de otimização executados
CREATE TABLE optimizer_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    -- Dados coletados
    metrics JSONB NOT NULL,          -- métricas técnicas
    patterns JSONB NOT NULL,         -- padrões detectados
    suggestions_count INTEGER,       -- quantas sugestões geradas

    executado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_executed (user_id, executado_em)
);

-- Sugestões de otimização geradas
CREATE TABLE optimizer_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),
    cycle_id UUID REFERENCES optimizer_cycles(id),

    -- Sugestão
    category VARCHAR(50) NOT NULL,   -- 'time', 'cost', 'organization', 'communication'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    impact VARCHAR(20) NOT NULL,     -- 'high', 'medium', 'low'
    effort VARCHAR(20) NOT NULL,     -- 'high', 'medium', 'low'

    suggested_action JSONB NOT NULL,
    estimated_savings JSONB,

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'applied'
    user_response TEXT,                    -- feedback da usuária

    criado_em TIMESTAMP DEFAULT NOW(),
    respondido_em TIMESTAMP,

    INDEX idx_user_status (user_id, status),
    INDEX idx_category (category)
);

-- Otimizações aplicadas
CREATE TABLE optimizer_applied_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),
    suggestion_id UUID REFERENCES optimizer_suggestions(id),

    -- Resultado
    applied_at TIMESTAMP DEFAULT NOW(),
    reverted_at TIMESTAMP,               -- se foi revertida
    results JSONB,                       -- resultados medidos

    -- Aprendizado
    success BOOLEAN,                     -- foi bem sucedida?
    user_feedback TEXT,

    INDEX idx_user_applied (user_id, applied_at),
    INDEX idx_success (success)
);

-- Padrões detectados (para aprendizado)
CREATE TABLE optimizer_learned_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    pattern_type VARCHAR(50) NOT NULL,   -- 'time', 'task', 'communication', 'energy'
    pattern_data JSONB NOT NULL,
    confidence DECIMAL(3,2),             -- 0.0 - 1.0

    first_detected TIMESTAMP DEFAULT NOW(),
    last_confirmed TIMESTAMP DEFAULT NOW(),
    confirmation_count INTEGER DEFAULT 1,

    INDEX idx_user_pattern_type (user_id, pattern_type)
);

-- Configurações de autonomia
CREATE TABLE optimizer_autonomy_settings (
    user_id UUID PRIMARY KEY REFERENCES usuarios(id),

    global_mode VARCHAR(20) DEFAULT 'assistido',  -- 'suave', 'assistido', 'total'
    autonomy_rules JSONB NOT NULL,                -- regras granulares por tipo
    safety_limits JSONB NOT NULL,

    atualizado_em TIMESTAMP DEFAULT NOW()
);
```

---

## 11. API Endpoints

```python
# backend/modules/optimizer/routes.py

from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/optimizer", tags=["Optimizer"])

@router.get("/suggestions")
async def get_suggestions(
    status: str = "pending",
    user_id: str = Depends(get_current_user)
):
    """
    Retorna sugestões de otimização pendentes
    """

    suggestions = db.execute("""
        SELECT *
        FROM optimizer_suggestions
        WHERE user_id = %s
          AND status = %s
        ORDER BY criado_em DESC
    """, (user_id, status)).fetchall()

    return {"suggestions": suggestions}

@router.post("/suggestions/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Aceita uma sugestão de otimização
    """

    # Aplicar otimização
    orchestrator = OptimizationOrchestrator(...)
    await orchestrator.apply_suggestion(suggestion_id)

    return {"status": "applied"}

@router.post("/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: str,
    reason: str,
    user_id: str = Depends(get_current_user)
):
    """
    Rejeita uma sugestão de otimização
    """

    db.execute("""
        UPDATE optimizer_suggestions
        SET status = 'rejected',
            user_response = %s,
            respondido_em = NOW()
        WHERE id = %s
    """, (reason, suggestion_id))

    # Aprender com rejeição
    optimizer.learn_from_rejection(suggestion_id, reason)

    return {"status": "rejected"}

@router.get("/metrics")
async def get_optimizer_metrics(
    user_id: str = Depends(get_current_user)
):
    """
    Retorna métricas do Optimizer (economia, melhorias)
    """

    analytics = OptimizerAnalytics(db)
    return await analytics.get_metrics(user_id)

@router.put("/autonomy/settings")
async def update_autonomy_settings(
    settings: AutonomySettings,
    user_id: str = Depends(get_current_user)
):
    """
    Atualiza configurações de autonomia
    """

    db.execute("""
        INSERT INTO optimizer_autonomy_settings
        (user_id, global_mode, autonomy_rules, safety_limits, atualizado_em)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            global_mode = EXCLUDED.global_mode,
            autonomy_rules = EXCLUDED.autonomy_rules,
            safety_limits = EXCLUDED.safety_limits,
            atualizado_em = NOW()
    """, (
        user_id,
        settings.global_mode,
        json.dumps(settings.autonomy_rules),
        json.dumps(settings.safety_limits)
    ))

    return {"status": "updated"}

@router.post("/trigger-cycle")
async def trigger_optimization_cycle(
    user_id: str = Depends(get_current_user)
):
    """
    Força execução de um ciclo de otimização (para testing)
    """

    orchestrator = OptimizationOrchestrator(...)
    await orchestrator.run_optimization_cycle(user_id)

    return {"status": "cycle_completed"}
```

---

## 12. Métricas e Analytics

### 12.1 Dashboard de Otimização

```python
# backend/modules/optimizer/analytics.py

class OptimizerAnalytics:
    """
    Analytics do Optimizer (economia, melhorias)
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def get_metrics(self, user_id: str) -> Dict:
        """
        Retorna métricas consolidadas do Optimizer
        """

        return {
            "savings": await self._calculate_savings(user_id),
            "improvements": await self._calculate_improvements(user_id),
            "learning": await self._calculate_learning_progress(user_id),
            "suggestions": await self._get_suggestion_stats(user_id)
        }

    async def _calculate_savings(self, user_id: str) -> Dict:
        """
        Calcula economia gerada (tempo, custo, energia)
        """

        applied_opts = self.db.execute("""
            SELECT
                s.estimated_savings,
                a.applied_at
            FROM optimizer_applied_optimizations a
            JOIN optimizer_suggestions s ON s.id = a.suggestion_id
            WHERE a.user_id = %s
              AND a.success = TRUE
              AND a.applied_at > NOW() - INTERVAL '30 days'
        """, (user_id,)).fetchall()

        total_time_saved = sum(
            opt["estimated_savings"].get("time_minutes", 0)
            for opt in applied_opts
        )

        total_cost_saved = sum(
            opt["estimated_savings"].get("cost_usd", 0)
            for opt in applied_opts
        )

        total_energy_saved = sum(
            opt["estimated_savings"].get("energy_points", 0)
            for opt in applied_opts
        )

        return {
            "time_saved_minutes": total_time_saved,
            "time_saved_hours": total_time_saved / 60,
            "cost_saved_usd": total_cost_saved,
            "energy_saved_points": total_energy_saved,
            "optimizations_applied": len(applied_opts)
        }

    async def _calculate_improvements(self, user_id: str) -> Dict:
        """
        Calcula melhorias qualitativas
        """

        # Performance: latência média antes vs depois
        before_latency = self.db.execute("""
            SELECT AVG(response_time_ms) as avg_latency
            FROM api_logs
            WHERE timestamp BETWEEN NOW() - INTERVAL '60 days' AND NOW() - INTERVAL '30 days'
        """).fetchone()["avg_latency"]

        after_latency = self.db.execute("""
            SELECT AVG(response_time_ms) as avg_latency
            FROM api_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
        """).fetchone()["avg_latency"]

        latency_improvement = (
            (before_latency - after_latency) / before_latency * 100
            if before_latency else 0
        )

        return {
            "latency_improvement_percent": latency_improvement,
            "system_faster": latency_improvement > 0
        }

    async def _calculate_learning_progress(self, user_id: str) -> Dict:
        """
        Calcula progresso de aprendizado
        """

        patterns_learned = self.db.execute("""
            SELECT COUNT(*) as pattern_count
            FROM optimizer_learned_patterns
            WHERE user_id = %s
              AND confirmation_count >= 3  -- padrão confirmado 3x
        """, (user_id,)).fetchone()["pattern_count"]

        return {
            "patterns_learned": patterns_learned,
            "learning_stage": self._determine_learning_stage(patterns_learned)
        }

    def _determine_learning_stage(self, patterns_count: int) -> str:
        """
        Determina estágio de aprendizado
        """

        if patterns_count < 5:
            return "iniciante"
        elif patterns_count < 20:
            return "intermediário"
        else:
            return "avançado"
```

### 12.2 Exemplo de Métricas

```json
{
    "period": "últimos 30 dias",
    "savings": {
        "time_saved_minutes": 420,
        "time_saved_hours": 7.0,
        "cost_saved_usd": 125.50,
        "energy_saved_points": 180,
        "optimizations_applied": 15
    },
    "improvements": {
        "latency_improvement_percent": 25.3,
        "system_faster": true,
        "error_rate_reduction": 40.0
    },
    "learning": {
        "patterns_learned": 12,
        "learning_stage": "intermediário",
        "confidence": 0.85
    },
    "suggestions": {
        "total_generated": 25,
        "accepted": 15,
        "rejected": 5,
        "pending": 5,
        "acceptance_rate": 0.75
    },
    "highlights": [
        "✅ Sistema 25% mais rápido",
        "✅ $125 economizados em custos de API",
        "✅ 7 horas economizadas no último mês",
        "✅ 12 padrões de comportamento aprendidos"
    ]
}
```

---

## 13. Roadmap de Implementação

### 13.1 Fase 1: Observabilidade (1-2 meses)

**Objetivo:** Ter visibilidade completa do sistema

✅ **Componentes:**
- [ ] ObservabilityAgent com coleta de métricas
- [ ] Dashboards de performance
- [ ] Logging estruturado de todos os módulos
- [ ] Tracking de custos de API

🎯 **Critério de Sucesso:**
- Métricas coletadas em tempo real
- Dashboard funcional com latência, custos, erros
- Alertas automáticos para problemas críticos

### 13.2 Fase 2: Detecção de Padrões (2 meses)

**Objetivo:** Aprender com comportamento da usuária

✅ **Componentes:**
- [ ] PatternAgent com análise temporal
- [ ] Detecção de padrões de tarefas
- [ ] Correlação de energia com ciclo (Wellness)
- [ ] Análise de comunicação (Diplomat)

🎯 **Critério de Sucesso:**
- 10+ padrões detectados automaticamente
- Confiança >80% na detecção
- Insights acionáveis gerados

### 13.3 Fase 3: Sugestões e Autonomia (2 meses)

**Objetivo:** Gerar e aplicar otimizações

✅ **Componentes:**
- [ ] EfficiencyAgent com geração de sugestões
- [ ] CalibrationAgent para ajustes finos
- [ ] OptimizationOrchestrator completo
- [ ] 3 níveis de autonomia (Suave/Assistido/Total)

🎯 **Critério de Sucesso:**
- 20+ sugestões geradas por mês
- Taxa de aceitação >70%
- Pelo menos 5 otimizações aplicadas automaticamente (Modo Total)

### 13.4 Fase 4: Aprendizado Contínuo (2 meses)

**Objetivo:** Sistema se aprimora sozinho

✅ **Componentes:**
- [ ] Feedback loop completo
- [ ] Calibração adaptativa
- [ ] Aprendizado de rejeições
- [ ] Ajuste automático de confidence thresholds

🎯 **Critério de Sucesso:**
- Sistema melhora métricas mês a mês
- Redução de 30%+ em custos de API
- Economia de 5+ horas/mês para usuária

---

## 14. Conclusão

**Charlee Optimizer** é o **Sistema Nervoso Executivo** que transforma Charlee em um parceiro evolutivo:

✨ **Aprende continuamente** com seu comportamento
✨ **Reduz custos** automaticamente
✨ **Melhora performance** técnica
✨ **Adapta fluxos** ao seu estilo de vida
✨ **Antecipa necessidades** antes que você perceba

Este módulo é **crítico** porque:
- Garante que Charlee **nunca fique obsoleto**
- Torna o sistema **cada vez mais eficiente** com o tempo
- **Aprende seu estilo** de liderança (Imperatriz Graciosa)
- **Se auto-aprimora** sem intervenção manual

**Próximos passos:**
1. Implementar Fase 1 (Observabilidade)
2. Testar com dados reais por 30 dias
3. Iniciar Fase 2 (Detecção de Padrões)
4. Iterar baseado em feedback

---

**Versão:** 1.0
**Última atualização:** 17 Janeiro 2025
**Autor:** Charlee Development Team
**Status:** 🔴 Planejamento (V5.0)
