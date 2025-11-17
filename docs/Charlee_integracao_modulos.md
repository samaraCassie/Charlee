# 🔗 Integração Completa dos Módulos Charlee

## 19. Arquitetura de Integração

### 19.1 Visão Geral da Integração

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHARLEE CORE (Orquestrador)                  │
│              Agente Central que coordena tudo                   │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┼────────┬──────────┬──────────┬───────────┬──────────┐
    │        │        │          │          │           │          │
    ▼        ▼        ▼          ▼          ▼           ▼          ▼
┌────────┐┌────────┐┌─────────┐┌─────────┐┌──────────┐┌─────────┐┌─────────┐
│ Task   ││Wellness││Capacity ││  OKR    ││  Focus   ││Projects ││Calendar │
│Manager ││ Coach  ││Guardian ││Dashboard││  Module  ││ Module  ││ Module  │
└────┬───┘└───┬────┘└────┬────┘└────┬────┘└────┬─────┘└────┬────┘└────┬────┘
     │        │          │          │          │           │          │
     └────────┴──────────┴──────────┴──────────┴───────────┴──────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐      ┌──────────────┐      ┌──────────┐
    │ WEALTH  │      │   ROUTINES   │      │ WARDROBE │
    │ MODULE  │      │    MODULE    │      │  MODULE  │
    └────┬────┘      └──────┬───────┘      └────┬─────┘
         │                  │                    │
         └──────────────────┼────────────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
            ┌──────────┐    ┌───────────────┐
            │ DIPLOMAT │    │  EVENT BUS    │
            │  MODULE  │    │  (Pub/Sub)    │
            └────┬─────┘    └───────┬───────┘
                 │                  │
                 └──────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
        ┌──────────────────┐  ┌──────────────────┐
        │  SHARED MEMORY   │  │  CONTEXT MANAGER │
        │  (Vector DB)     │  │  (Global State)  │
        └──────────────────┘  └──────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
 ┌─────────────┐     ┌─────────────┐
 │ PostgreSQL  │     │   Redis     │
 │ (Relacional)│     │   (Cache)   │
 └─────────────┘     └─────────────┘
```

### 19.2 Princípios de Integração

**1. Memória Compartilhada**
- Todos os módulos compartilham Vector DB (PgVector)
- Contexto holístico: cada módulo enriquece a memória global

**2. Event-Driven Architecture**
- Módulos se comunicam via eventos (Pub/Sub)
- Desacoplamento: cada módulo opera independentemente
- Reações em cadeia: um evento pode triggerar múltiplos módulos

**3. Context Awareness**
- Todos os módulos têm acesso ao contexto global de Samara
- Decisões consideram: ciclo menstrual, carga de trabalho, OKRs, foco atual

**4. Priorização Unificada**
- Sistema único de prioridade que considera todos os módulos
- Conflitos resolvidos pelo Orquestrador Central

---

### 19.3 Schema de Integração

```sql
-- EVENTOS DO SISTEMA (Event Bus)
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo TEXT NOT NULL,
    -- 'task_created', 'project_accepted', 'focus_started', 
    -- 'cycle_phase_changed', 'capacity_alert', 'okr_updated'
    
    modulo_origem TEXT NOT NULL,
    -- 'task_manager', 'projects', 'focus', 'wellness', etc
    
    payload JSONB NOT NULL,
    -- Dados específicos do evento
    
    prioridade INTEGER DEFAULT 5,
    processado BOOLEAN DEFAULT FALSE,
    
    criado_em TIMESTAMP DEFAULT NOW(),
    processado_em TIMESTAMP
);

-- CONTEXTO GLOBAL (Snapshot do estado atual)
CREATE TABLE contexto_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Estado atual
    fase_ciclo TEXT,
    energia_atual INTEGER,
    carga_trabalho_percentual FLOAT,
    em_sessao_foco BOOLEAN DEFAULT FALSE,
    
    -- Métricas agregadas
    tarefas_pendentes INTEGER,
    projetos_ativos INTEGER,
    notificacoes_nao_lidas INTEGER,
    
    -- Contexto temporal
    hora_dia INTEGER,
    dia_semana INTEGER,
    periodo_produtivo TEXT,  -- 'manha', 'tarde', 'noite'
    
    -- Estado emocional (inferido)
    nivel_stress INTEGER CHECK(nivel_stress BETWEEN 1 AND 10),
    necessita_pausa BOOLEAN DEFAULT FALSE,
    
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- CROSS-MODULE LINKS (Relacionamentos entre módulos)
CREATE TABLE cross_module_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    tipo_relacao TEXT NOT NULL,
    -- 'project_to_task', 'notification_to_task', 
    -- 'task_to_okr', 'project_to_portfolio'
    
    modulo_origem TEXT NOT NULL,
    entidade_origem_id UUID NOT NULL,
    
    modulo_destino TEXT NOT NULL,
    entidade_destino_id UUID NOT NULL,
    
    metadata JSONB,
    
    criado_em TIMESTAMP DEFAULT NOW()
);

-- DECISÕES CROSS-MODULE
CREATE TABLE decisoes_integradas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    situacao TEXT NOT NULL,
    -- Descrição da situação que requer decisão
    
    modulos_envolvidos TEXT[],
    contexto_considerado JSONB,
    
    opcoes_avaliadas JSONB[],
    decisao_tomada TEXT,
    justificativa TEXT,
    
    executado BOOLEAN DEFAULT FALSE,
    resultado TEXT,
    
    criado_em TIMESTAMP DEFAULT NOW()
);

-- ÍNDICES
CREATE INDEX idx_events_tipo ON system_events(tipo, processado);
CREATE INDEX idx_events_prioridade ON system_events(prioridade DESC, criado_em);
CREATE INDEX idx_cross_module_origem ON cross_module_relations(modulo_origem, entidade_origem_id);
CREATE INDEX idx_cross_module_destino ON cross_module_relations(modulo_destino, entidade_destino_id);
```

---

## 19.4 Event Bus - Sistema de Eventos

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
import asyncio
import json

class EventType(Enum):
    # Task Manager
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_DEADLINE_APPROACHING = "task_deadline_approaching"

    # Projects Module
    PROJECT_COLLECTED = "project_collected"
    PROJECT_ANALYZED = "project_analyzed"
    PROJECT_ACCEPTED = "project_accepted"
    PROJECT_REJECTED = "project_rejected"
    PROJECT_COMPLETED = "project_completed"

    # Focus Module
    FOCUS_SESSION_STARTED = "focus_session_started"
    FOCUS_SESSION_ENDED = "focus_session_ended"
    NOTIFICATION_URGENT = "notification_urgent"
    INTERRUPTION_BLOCKED = "interruption_blocked"

    # Wellness Coach
    CYCLE_PHASE_CHANGED = "cycle_phase_changed"
    ENERGY_LOW = "energy_low"
    WELLNESS_ALERT = "wellness_alert"

    # Capacity Guardian
    CAPACITY_WARNING = "capacity_warning"
    CAPACITY_CRITICAL = "capacity_critical"
    OVERLOAD_DETECTED = "overload_detected"

    # OKR Dashboard
    OKR_UPDATED = "okr_updated"
    OKR_AT_RISK = "okr_at_risk"
    MILESTONE_ACHIEVED = "milestone_achieved"

    # Calendar Module
    CALENDAR_EVENT_CREATED = "calendar_event_created"
    CALENDAR_EVENT_UPDATED = "calendar_event_updated"
    CALENDAR_CONFLICT_DETECTED = "calendar_conflict_detected"

    # === NOVOS MÓDULOS V4+ ===

    # Wealth Module
    EXPENSE_CREATED = "wealth.expense_created"
    EXPENSE_PATTERN_DETECTED = "wealth.pattern_detected"
    SAVINGS_GOAL_AT_RISK = "wealth.goal_at_risk"
    IMPULSE_SPENDING_ALERT = "wealth.impulse_alert"
    FINANCIAL_FORECAST_UPDATED = "wealth.forecast_updated"
    SPENDING_BLOCK_ACTIVATED = "wealth.block_activated"

    # Routines Module
    ROUTINE_GENERATED = "routines.script_generated"
    ROUTINE_STARTED = "routines.started"
    ROUTINE_INTERRUPTED = "routines.interrupted"
    ROUTINE_COMPLETED = "routines.completed"
    DECISION_FATIGUE_HIGH = "routines.decision_fatigue_high"
    MORNING_SCRIPT_READY = "routines.morning_ready"

    # Wardrobe Module
    WEEKLY_PLAN_GENERATED = "wardrobe.plan_generated"
    OUTFIT_CHANGED = "wardrobe.outfit_changed"
    WARDROBE_ITEM_ADDED = "wardrobe.item_added"
    LAUNDRY_NEEDED = "wardrobe.laundry_needed"
    STYLE_CONFLICT_DETECTED = "wardrobe.style_conflict"

    # Diplomat Module
    RELATIONSHIP_HEALTH_CHANGED = "diplomat.health_changed"
    RECONNECTION_REMINDER = "diplomat.reconnection_due"
    ONE_ON_ONE_SCHEDULED = "diplomat.meeting_scheduled"
    INTERACTION_LOGGED = "diplomat.interaction_logged"
    PUPIL_MILESTONE_REACHED = "diplomat.pupil_milestone"
    NETWORKING_OPPORTUNITY = "diplomat.networking_opportunity"

    # System
    CONTEXT_UPDATED = "context_updated"
    DECISION_REQUIRED = "decision_required"

@dataclass
class Event:
    """Evento do sistema"""
    tipo: EventType
    modulo_origem: str
    payload: Dict[str, Any]
    prioridade: int = 5
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class EventBus:
    """Sistema de eventos pub/sub"""
    
    def __init__(self, db_connection, redis_client):
        self.db = db_connection
        self.redis = redis_client
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """Registra subscriber para um tipo de evento"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"📡 {handler.__name__} subscribed to {event_type.value}")
    
    async def publish(self, event: Event):
        """Publica evento no bus"""
        
        # Salva no banco
        event_id = self.db.execute("""
            INSERT INTO system_events 
            (tipo, modulo_origem, payload, prioridade)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            event.tipo.value,
            event.modulo_origem,
            json.dumps(event.payload),
            event.prioridade
        )).fetchone()['id']
        
        # Publica no Redis (para processamento real-time)
        self.redis.publish(
            f'charlee:events:{event.tipo.value}',
            json.dumps({
                'id': str(event_id),
                'payload': event.payload,
                'timestamp': event.timestamp
            })
        )
        
        # Adiciona à fila de processamento
        await self.event_queue.put(event)
        
        logger.info(f"📤 Event published: {event.tipo.value} from {event.modulo_origem}")
        
        return event_id
    
    async def process_events(self):
        """Loop de processamento de eventos"""
        while True:
            event = await self.event_queue.get()
            
            # Notifica subscribers
            if event.tipo in self.subscribers:
                for handler in self.subscribers[event.tipo]:
                    try:
                        # Executa handler assincronamente
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler {handler.__name__}: {e}")
            
            # Marca como processado
            self.db.execute("""
                UPDATE system_events
                SET processado = TRUE, processado_em = NOW()
                WHERE tipo = %s AND modulo_origem = %s 
                  AND criado_em = %s
            """, (event.tipo.value, event.modulo_origem, event.timestamp))
    
    def get_recent_events(self, event_type: EventType = None, limit: int = 50):
        """Busca eventos recentes"""
        if event_type:
            query = """
                SELECT * FROM system_events
                WHERE tipo = %s
                ORDER BY criado_em DESC
                LIMIT %s
            """
            return self.db.execute(query, (event_type.value, limit)).fetchall()
        else:
            query = """
                SELECT * FROM system_events
                ORDER BY prioridade DESC, criado_em DESC
                LIMIT %s
            """
            return self.db.execute(query, (limit,)).fetchall()
```

---

## 19.5 Context Manager - Gerenciador de Contexto Global

```python
class ContextManager:
    """Gerencia contexto global de Samara"""
    
    def __init__(self, db_connection, event_bus):
        self.db = db_connection
        self.event_bus = event_bus
        self.current_context = self.load_context()
        
        # Subscribe para eventos que afetam contexto
        self.subscribe_to_events()
    
    def load_context(self):
        """Carrega contexto atual"""
        context = self.db.execute("""
            SELECT * FROM contexto_global
            ORDER BY atualizado_em DESC
            LIMIT 1
        """).fetchone()
        
        if not context:
            # Cria contexto inicial
            context = self.initialize_context()
        
        return context
    
    def initialize_context(self):
        """Inicializa contexto pela primeira vez"""
        return self.db.execute("""
            INSERT INTO contexto_global
            (fase_ciclo, energia_atual, carga_trabalho_percentual, 
             em_sessao_foco, hora_dia, dia_semana)
            VALUES (
                'folicular', 7, 50, FALSE,
                EXTRACT(HOUR FROM NOW()),
                EXTRACT(DOW FROM NOW())
            )
            RETURNING *
        """).fetchone()
    
    def subscribe_to_events(self):
        """Registra handlers para eventos relevantes"""
        
        # Wellness events
        self.event_bus.subscribe(
            EventType.CYCLE_PHASE_CHANGED,
            self.on_cycle_phase_changed
        )
        self.event_bus.subscribe(
            EventType.ENERGY_LOW,
            self.on_energy_low
        )
        
        # Capacity events
        self.event_bus.subscribe(
            EventType.CAPACITY_WARNING,
            self.on_capacity_warning
        )
        
        # Focus events
        self.event_bus.subscribe(
            EventType.FOCUS_SESSION_STARTED,
            self.on_focus_started
        )
        self.event_bus.subscribe(
            EventType.FOCUS_SESSION_ENDED,
            self.on_focus_ended
        )
    
    def on_cycle_phase_changed(self, event: Event):
        """Atualiza contexto quando fase do ciclo muda"""
        new_phase = event.payload['nova_fase']
        energia_esperada = event.payload['energia_esperada']
        
        self.update_context({
            'fase_ciclo': new_phase,
            'energia_atual': int(energia_esperada * 10)
        })
        
        logger.info(f"🌸 Context updated: cycle phase → {new_phase}")
    
    def on_energy_low(self, event: Event):
        """Marca necessidade de pausa"""
        self.update_context({
            'nivel_stress': min(self.current_context['nivel_stress'] + 2, 10),
            'necessita_pausa': True
        })
    
    def on_capacity_warning(self, event: Event):
        """Aumenta nível de stress quando capacidade alta"""
        carga = event.payload['percentual_carga']
        
        self.update_context({
            'carga_trabalho_percentual': carga,
            'nivel_stress': min(int(carga / 10), 10)
        })
    
    def on_focus_started(self, event: Event):
        """Marca início de sessão de foco"""
        self.update_context({'em_sessao_foco': True})
    
    def on_focus_ended(self, event: Event):
        """Marca fim de sessão de foco"""
        qualidade = event.payload.get('qualidade_foco', 7)
        
        self.update_context({
            'em_sessao_foco': False,
            'energia_atual': max(self.current_context['energia_atual'] - 1, 1)
        })
    
    def update_context(self, updates: Dict[str, Any]):
        """Atualiza contexto global"""
        
        # Atualiza memória local
        self.current_context.update(updates)
        
        # Atualiza banco
        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values())
        
        self.db.execute(f"""
            UPDATE contexto_global
            SET {set_clause}, atualizado_em = NOW()
            WHERE id = %s
        """, values + [self.current_context['id']])
        
        # Publica evento de atualização
        asyncio.create_task(self.event_bus.publish(Event(
            tipo=EventType.CONTEXT_UPDATED,
            modulo_origem='context_manager',
            payload=updates
        )))
    
    def get_context(self) -> Dict[str, Any]:
        """Retorna contexto atual"""
        return self.current_context
    
    def should_accept_interruption(self) -> bool:
        """Decide se deve aceitar interrupção baseado em contexto"""
        
        # Em foco? Só urgências críticas
        if self.current_context['em_sessao_foco']:
            return False
        
        # Energia baixa? Evita mais carga
        if self.current_context['energia_atual'] < 4:
            return False
        
        # Fase menstrual? Mais protetor
        if self.current_context['fase_ciclo'] == 'menstrual':
            return False
        
        # Carga alta? Evita
        if self.current_context['carga_trabalho_percentual'] > 90:
            return False
        
        return True
    
    def get_optimal_activity_type(self) -> str:
        """Sugere tipo de atividade ideal para o momento"""
        
        fase = self.current_context['fase_ciclo']
        energia = self.current_context['energia_atual']
        hora = self.current_context['hora_dia']
        carga = self.current_context['carga_trabalho_percentual']
        
        # Fase menstrual: leve
        if fase == 'menstrual':
            return 'administrative' if energia < 5 else 'light_development'
        
        # Fase folicular: criativo
        if fase == 'folicular':
            if hora >= 9 and hora <= 12:  # Manhã
                return 'strategic_planning'
            else:
                return 'creative_development'
        
        # Ovulação: comunicação
        if fase == 'ovulacao':
            return 'meetings_presentations'
        
        # Lútea: execução
        if fase == 'lutea':
            return 'execution_completion'
        
        return 'flexible'
```

---

## 19.6 Integração Específica: Task Manager ↔ Projects

```python
class TaskProjectIntegration:
    """Integração entre gestão de tarefas e projetos freelance"""
    
    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager
        
        # Subscribe eventos relevantes
        self.event_bus.subscribe(
            EventType.PROJECT_ACCEPTED,
            self.on_project_accepted
        )
        self.event_bus.subscribe(
            EventType.PROJECT_COMPLETED,
            self.on_project_completed
        )
    
    async def on_project_accepted(self, event: Event):
        """Quando projeto é aceito, cria tasks automaticamente"""
        
        project_id = event.payload['project_id']
        
        # Busca projeto
        project = self.db.execute("""
            SELECT * FROM projetos_freelance WHERE id = %s
        """, (project_id,)).fetchone()
        
        # Cria big rock para o projeto (se não existir)
        big_rock = self.db.execute("""
            INSERT INTO big_rocks (nome, cor, capacidade_semanal)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (
            f"Projeto: {project['titulo'][:30]}",
            '#4ECDC4',  # Cor padrão para projetos
            project['horas_estimadas'] / 4  # Distribuído em 4 semanas
        )).fetchone()
        
        if big_rock:
            big_rock_id = big_rock['id']
        else:
            big_rock_id = self.db.execute("""
                SELECT id FROM big_rocks WHERE nome = %s
            """, (f"Projeto: {project['titulo'][:30]}",)).fetchone()['id']
        
        # Cria tasks decompostas
        tasks = self.decompose_project_into_tasks(project)
        
        for task in tasks:
            task_id = self.db.execute("""
                INSERT INTO tarefas
                (descricao, tipo, deadline, big_rock_id, 
                 estimativa_horas, tags, fonte, id_externo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                task['descricao'],
                'Tarefa',
                task['deadline'],
                big_rock_id,
                task['horas'],
                ['projeto', 'freelance'] + task.get('tags', []),
                'projects_module',
                str(project_id)
            )).fetchone()['id']
            
            # Cria link cross-module
            self.db.execute("""
                INSERT INTO cross_module_relations
                (tipo_relacao, modulo_origem, entidade_origem_id,
                 modulo_destino, entidade_destino_id)
                VALUES ('project_to_task', 'projects', %s, 'task_manager', %s)
            """, (project_id, task_id))
        
        logger.info(f"✅ Projeto {project['titulo']} convertido em {len(tasks)} tasks")
        
        # Atualiza carga de trabalho
        await self.event_bus.publish(Event(
            tipo=EventType.CONTEXT_UPDATED,
            modulo_origem='task_project_integration',
            payload={'novo_projeto_adicionado': True}
        ))
    
    def decompose_project_into_tasks(self, project):
        """Decompõe projeto em tasks menores"""
        
        # Usa LLM para decomposição inteligente
        prompt = f"""
Decomponha este projeto freelance em tasks específicas e acionáveis:

Projeto: {project['titulo']}
Descrição: {project['descricao']}
Prazo: {project['prazo_sugerido']} dias
Horas estimadas: {project['horas_estimadas']}h

Crie entre 5-10 tasks que:
1. Sejam específicas e acionáveis
2. Tenham estimativa de horas realista
3. Estejam em ordem lógica de execução
4. Considerem marcos importantes

Retorne JSON:
[
    {{
        "descricao": "Setup inicial e configuração do ambiente",
        "horas": 2,
        "deadline": "YYYY-MM-DD",
        "tags": ["setup", "inicial"]
    }},
    ...
]
"""
        
        # Chama LLM (usando Charlee)
        response = charlee_orchestrator.print_response(prompt, stream=False)
        tasks = json.loads(response)
        
        return tasks
    
    async def on_project_completed(self, event: Event):
        """Quando projeto é concluído, marca tasks relacionadas"""
        
        project_id = event.payload['project_id']
        
        # Busca tasks relacionadas
        related_tasks = self.db.execute("""
            SELECT t.id
            FROM tarefas t
            JOIN cross_module_relations cmr 
                ON cmr.entidade_destino_id = t.id
            WHERE cmr.modulo_origem = 'projects'
              AND cmr.entidade_origem_id = %s
              AND t.status != 'Concluída'
        """, (project_id,)).fetchall()
        
        # Marca todas como concluídas
        for task in related_tasks:
            self.db.execute("""
                UPDATE tarefas
                SET status = 'Concluída', concluido_em = NOW()
                WHERE id = %s
            """, (task['id'],))
        
        logger.info(f"✅ {len(related_tasks)} tasks marcadas como concluídas")
```

---

## 19.7 Integração: Focus ↔ Capacity Guardian

```python
class FocusCapacityIntegration:
    """Integração entre proteção de foco e gestão de capacidade"""
    
    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager
        
        # Subscriptions
        self.event_bus.subscribe(
            EventType.CAPACITY_CRITICAL,
            self.on_capacity_critical
        )
        self.event_bus.subscribe(
            EventType.NOTIFICATION_URGENT,
            self.on_urgent_notification
        )
        self.event_bus.subscribe(
            EventType.INTERRUPTION_BLOCKED,
            self.on_interruption_blocked
        )
    
    async def on_capacity_critical(self, event: Event):
        """Quando capacidade crítica, ativa proteção máxima"""
        
        carga = event.payload['percentual_carga']
        
        if carga > 95:
            # Ativa modo "deep protection"
            logger.warn(f"🛡️ MODO PROTEÇÃO MÁXIMA: Carga {carga}%")
            
            # Bloqueia TODAS notificações não-críticas
            self.db.execute("""
                UPDATE notifications
                SET snooze_until = NOW() + INTERVAL '4 hours'
                WHERE categoria != 'urgente' AND lida = FALSE
            """)
            
            # Cancela reuniões não-essenciais automaticamente
            self.suggest_meeting_cancellations()
            
            # Publica alerta
            await self.event_bus.publish(Event(
                tipo=EventType.WELLNESS_ALERT,
                modulo_origem='focus_capacity_integration',
                payload={
                    'tipo': 'overload_protection_activated',
                    'mensagem': 'Modo de proteção máxima ativado. Apenas trabalho crítico.'
                },
                prioridade=1
            ))
    
    async def on_urgent_notification(self, event: Event):
        """Avalia se notificação urgente deve interromper, considerando carga"""
        
        notification_id = event.payload['notification_id']
        context = self.context.get_context()
        
        # Se carga > 90% E em sessão de foco, só permite CRÍTICO
        if (context['carga_trabalho_percentual'] > 90 and 
            context['em_sessao_foco']):
            
            # Verifica se é REALMENTE crítico
            notification = self.db.execute("""
                SELECT * FROM notifications WHERE id = %s
            """, (notification_id,)).fetchone()
            
            is_truly_critical = self.verify_critical_urgency(notification)
            
            if not is_truly_critical:
                # Bloqueia mesmo sendo "urgente"
                self.db.execute("""
                    UPDATE notifications
                    SET snooze_until = NOW() + INTERVAL '2 hours',
                        categoria = 'importante'
                    WHERE id = %s
                """, (notification_id,))
                
                logger.info(f"🛡️ Bloqueada urgência não-crítica durante sobrecarga")
                
                await self.event_bus.publish(Event(
                    tipo=EventType.INTERRUPTION_BLOCKED,
                    modulo_origem='focus_capacity_integration',
                    payload={
                        'notification_id': notification_id,
                        'motivo': 'sobrecarga_critica'
                    }
                ))
    
    def verify_critical_urgency(self, notification):
        """Verifica se é urgência verdadeira"""
        critical_patterns = [
            'servidor down',
            'produção offline',
            'incidente crítico',
            'emergência',
            'cliente bloqueado'
        ]
        
        text = (notification.get('assunto', '') + ' ' + 
                notification['corpo']).lower()
        
        return any(pattern in text for pattern in critical_patterns)
    
    def suggest_meeting_cancellations(self):
        """Sugere cancelamento de reuniões não-essenciais"""
        
        # Busca reuniões próximas
        upcoming_meetings = self.db.execute("""
            SELECT * FROM tarefas
            WHERE tipo = 'Compromisso Fixo'
              AND deadline BETWEEN NOW() AND NOW() + INTERVAL '2 days'
              AND status = 'Pendente'
        """).fetchall()
        
        suggestions = []
        for meeting in upcoming_meetings:
            # Analisa se é essencial
            is_essential = self.is_meeting_essential(meeting)
            
            if not is_essential:
                suggestions.append({
                    'meeting_id': meeting['id'],
                    'titulo': meeting['descricao'],
                    'sugestao': 'cancelar_ou_reagendar'
                })
        
        if suggestions:
            logger.info(f"💡 {len(suggestions)} reuniões sugeridas para cancelamento")
            # Notifica Samara
            return suggestions
```

---

## 19.8 Integração: Wellness ↔ Projects

```python
class WellnessProjectsIntegration:
    """Integração entre bem-estar e análise de projetos"""
    
    def __init__(self, db_connection, event_bus, wellness_coach):
        self.db = db_connection
        self.event_bus = event_bus
        self.wellness = wellness_coach
        
        # Subscriptions
        self.event_bus.subscribe(
            EventType.PROJECT_ANALYZED,
            self.adjust_project_evaluation_by_wellness
        )
        self.event_bus.subscribe(
            EventType.CYCLE_PHASE_CHANGED,
            self.reevaluate_pending_projects
        )
    
    async def adjust_project_evaluation_by_wellness(self, event: Event):
        """Ajusta avaliação de projeto baseado em bem-estar atual"""
        
        project_id = event.payload['project_id']
        context = self.wellness.get_current_phase()
        
        # Busca projeto
        project = self.db.execute("""
            SELECT * FROM projetos_freelance WHERE id = %s
        """, (project_id,)).fetchone()
        
        # Ajusta scores baseado na fase do ciclo
        fase = context['fase']
        energia_esperada = context['energia_esperada']
        
        # Durante fase menstrual, aumenta threshold para aceitar
        if fase == 'menstrual' and energia_esperada < 0.7:
            # Projetos precisam ser MUITO bons para serem aceitos
            score_ajustado = project['score_final'] * 0.8
            
            justificativa_adicional = (
                f"\n\n⚠️ CONSIDERAÇÃO DE BEM-ESTAR: "
                f"Você está na fase menstrual (energia {energia_esperada:.0%}). "
                f"Recomendo ser mais seletiva. Este projeto foi avaliado com "
                f"critério mais rigoroso."
            )
            
            # Atualiza
            self.db.execute("""
                UPDATE projetos_freelance
                SET score_final = %s,
                    justificativa = justificativa || %s
                WHERE id = %s
            """, (score_ajustado, justificativa_adicional, project_id))
            
            logger.info(f"🌸 Score do projeto ajustado por fase menstrual")
        
        # Durante ovulação, boost para projetos de networking
        elif fase == 'ovulacao':
            if 'networking' in ' '.join(project.get('oportunidades', [])).lower():
                score_ajustado = min(project['score_final'] * 1.15, 1.0)
                
                justificativa_adicional = (
                    f"\n\n✨ OPORTUNIDADE DE TIMING: "
                    f"Você está na fase de ovulação (alta energia social). "
                    f"Este é um momento ideal para projetos com componente "
                    f"de networking/apresentação."
                )
                
                self.db.execute("""
                    UPDATE projetos_freelance
                    SET score_final = %s,
                        justificativa = justificativa || %s
                    WHERE id = %s
                """, (score_ajustado, justificativa_adicional, project_id))
    
    async def reevaluate_pending_projects(self, event: Event):
        """Reavalia projetos pendentes quando fase muda"""
        
        nova_fase = event.payload['nova_fase']
        
        # Busca projetos aguardando decisão
        pending_projects = self.db.execute("""
            SELECT id FROM projetos_freelance
            WHERE status IN ('analisado', 'novo')
              AND recomendacao = 'negociar'
              AND coletado_em > NOW() - INTERVAL '7 days'
        """).fetchall()
        
        logger.info(f"🔄 Reavaliando {len(pending_projects)} projetos para fase {nova_fase}")
        
        for project in pending_projects:
            await self.event_bus.publish(Event(
                tipo=EventType.PROJECT_ANALYZED,
                modulo_origem='wellness_projects_integration',
                payload={'project_id': project['id']},
                prioridade=3
            ))
```

---

## 19.9 Integração: Wealth ↔ Wellness + Capacity

```python
class WealthWellnessIntegration:
    """Integração entre finanças comportamentais e bem-estar"""

    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager

        # Subscriptions
        self.event_bus.subscribe(
            EventType.CYCLE_PHASE_CHANGED,
            self.adjust_spending_guardrails
        )
        self.event_bus.subscribe(
            EventType.OVERLOAD_DETECTED,
            self.activate_impulse_protection
        )
        self.event_bus.subscribe(
            EventType.EXPENSE_CREATED,
            self.check_behavioral_context
        )

    async def adjust_spending_guardrails(self, event: Event):
        """Ajusta proteções financeiras baseado na fase do ciclo"""

        user_id = event.payload['user_id']
        nova_fase = event.payload['nova_fase']

        # TPM: ativa proteção máxima contra impulso
        if nova_fase == 'pre_menstrual':
            logger.info("🛡️ Ativando modo economia TPM")

            # Reduz limite de gasto impulsivo
            self.db.execute("""
                UPDATE configuracoes_financeiras
                SET limite_compra_sem_aprovacao = limite_compra_sem_aprovacao * 0.5,
                    modo_protecao = 'tpm'
                WHERE user_id = %s
            """, (user_id,))

            await self.event_bus.publish(Event(
                tipo=EventType.SPENDING_BLOCK_ACTIVATED,
                modulo_origem='wealth_wellness_integration',
                payload={
                    'motivo': 'fase_tpm',
                    'nivel_protecao': 'alto',
                    'mensagem': 'Proteção financeira TPM ativada. Compras > R$50 precisam de reflexão de 24h.'
                }
            ))

        # Fase folicular: mais flexível
        elif nova_fase == 'folicular':
            self.db.execute("""
                UPDATE configuracoes_financeiras
                SET modo_protecao = 'normal'
                WHERE user_id = %s
            """, (user_id,))

    async def activate_impulse_protection(self, event: Event):
        """Quando sobrecarga detectada, bloqueia gastos não-essenciais"""

        user_id = event.payload['user_id']
        carga = event.payload['percentual_carga']

        if carga > 90:
            logger.warn("💰 Bloqueando compras impulsivas durante sobrecarga")

            # Busca padrão histórico: stress → gasto
            pattern = self.db.execute("""
                SELECT AVG(valor) as media_gasto_stress
                FROM despesas
                WHERE user_id = %s
                  AND contexto_comportamental->>'stress_nivel' = 'alto'
                  AND categoria IN ('lazer', 'restaurante', 'shopping')
                  AND criado_em > NOW() - INTERVAL '90 days'
            """, (user_id,)).fetchone()

            if pattern and pattern['media_gasto_stress'] > 100:
                await self.event_bus.publish(Event(
                    tipo=EventType.IMPULSE_SPENDING_ALERT,
                    modulo_origem='wealth_wellness_integration',
                    payload={
                        'risco': 'alto',
                        'contexto': 'sobrecarga_critica',
                        'historico_gasto_stress': pattern['media_gasto_stress'],
                        'recomendacao': 'Compras não-essenciais bloqueadas até redução de carga'
                    },
                    prioridade=1
                ))

    async def check_behavioral_context(self, event: Event):
        """Quando despesa criada, analisa contexto comportamental"""

        despesa_id = event.payload['despesa_id']

        # Busca contexto atual
        context = self.context.get_context()

        # Enriquece despesa com contexto comportamental
        self.db.execute("""
            UPDATE despesas
            SET contexto_comportamental = jsonb_build_object(
                'fase_ciclo', %s,
                'energia_nivel', %s,
                'stress_nivel', CASE
                    WHEN %s >= 8 THEN 'alto'
                    WHEN %s >= 5 THEN 'medio'
                    ELSE 'baixo'
                END,
                'carga_trabalho', %s,
                'em_foco', %s
            )
            WHERE id = %s
        """, (
            context['fase_ciclo'],
            context['energia_atual'],
            context['nivel_stress'],
            context['nivel_stress'],
            context['carga_trabalho_percentual'],
            context['em_sessao_foco'],
            despesa_id
        ))

        logger.info(f"💡 Despesa enriquecida com contexto comportamental")
```

---

## 19.10 Integração: Routines ↔ Wellness + Wardrobe + Calendar

```python
class RoutinesIntegration:
    """Integração do módulo de rotinas com outros sistemas"""

    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager

        # Subscriptions
        self.event_bus.subscribe(
            EventType.CYCLE_PHASE_CHANGED,
            self.adjust_routine_timing
        )
        self.event_bus.subscribe(
            EventType.CALENDAR_EVENT_CREATED,
            self.check_routine_conflict
        )
        self.event_bus.subscribe(
            EventType.WEEKLY_PLAN_GENERATED,
            self.integrate_outfit_selection
        )

    async def adjust_routine_timing(self, event: Event):
        """Ajusta timing de rotinas baseado na fase do ciclo"""

        user_id = event.payload['user_id']
        nova_fase = event.payload['nova_fase']
        energia_esperada = event.payload['energia_esperada']

        # Busca rotina ativa
        rotina_hoje = self.db.execute("""
            SELECT * FROM roteiros_diarios
            WHERE user_id = %s
              AND data = CURRENT_DATE
              AND status = 'pendente'
        """, (user_id,)).fetchone()

        if not rotina_hoje:
            return

        adjustments = {}

        # Menstruação: mais tempo para tudo
        if nova_fase == 'menstruacao':
            adjustments = {
                'wake_time_adjustment': '+15min',
                'task_buffer': '+5min',
                'rest_periods': 'increased',
                'exercise': 'optional'
            }

            logger.info("🌸 Rotina ajustada para fase menstrual: +15min geral")

        # Fase folicular: otimizada
        elif nova_fase == 'folicular':
            adjustments = {
                'wake_time_adjustment': 'normal',
                'task_buffer': 'normal',
                'deep_work_blocks': '+30min',
                'exercise': 'encouraged'
            }

        # Atualiza rotina
        self.db.execute("""
            UPDATE roteiros_diarios
            SET roteiro = roteiro || %s::jsonb,
                energia_percentual = %s
            WHERE id = %s
        """, (
            json.dumps({'adjustments': adjustments}),
            energia_esperada * 100,
            rotina_hoje['id']
        ))

        await self.event_bus.publish(Event(
            tipo=EventType.ROUTINE_GENERATED,
            modulo_origem='routines_integration',
            payload={
                'rotina_id': rotina_hoje['id'],
                'adjustments': adjustments,
                'motivo': f'fase_{nova_fase}'
            }
        ))

    async def check_routine_conflict(self, event: Event):
        """Verifica se evento de calendário conflita com rotina"""

        calendar_event = event.payload['event']
        user_id = event.payload['user_id']

        # Busca rotina do dia
        event_date = calendar_event['start_time'].date()

        rotina = self.db.execute("""
            SELECT * FROM roteiros_diarios
            WHERE user_id = %s
              AND data = %s
        """, (user_id, event_date)).fetchone()

        if not rotina:
            return

        # Verifica conflito de horário
        event_start = calendar_event['start_time'].time()
        event_end = calendar_event['end_time'].time()

        roteiro = rotina['roteiro']
        conflicting_activities = []

        for activity in roteiro.get('activities', []):
            act_start = datetime.strptime(activity['start'], '%H:%M').time()
            act_end = datetime.strptime(activity['end'], '%H:%M').time()

            # Overlap check
            if (act_start < event_end and act_end > event_start):
                conflicting_activities.append(activity)

        if conflicting_activities:
            logger.warn(f"⚠️ Conflito detectado: evento sobrepõe {len(conflicting_activities)} atividades")

            # Propõe ajuste
            await self.event_bus.publish(Event(
                tipo=EventType.ROUTINE_INTERRUPTED,
                modulo_origem='routines_integration',
                payload={
                    'rotina_id': rotina['id'],
                    'conflicting_event': calendar_event,
                    'affected_activities': conflicting_activities,
                    'requires_decision': True,
                    'options': self.generate_conflict_options(rotina, calendar_event)
                }
            ))

    def generate_conflict_options(self, rotina, calendar_event):
        """Gera opções para resolver conflito"""

        return [
            {
                'option': 'reschedule_routine',
                'description': 'Mover atividades da rotina para depois do evento',
                'impact': 'Rotina termina 1h mais tarde'
            },
            {
                'option': 'skip_non_essential',
                'description': 'Pular atividades não-essenciais da rotina',
                'impact': 'Economiza 20min, mas algumas tarefas ficam pendentes'
            },
            {
                'option': 'decline_calendar_event',
                'description': 'Recusar evento do calendário',
                'impact': 'Mantém rotina, mas compromisso externo cancelado'
            }
        ]

    async def integrate_outfit_selection(self, event: Event):
        """Integra seleção de roupa no roteiro matinal"""

        user_id = event.payload['user_id']
        plano_semanal = event.payload['plano_semanal']

        # Para cada dia da semana, adiciona outfit à rotina
        for dia, outfit in plano_semanal.items():
            rotina = self.db.execute("""
                SELECT * FROM roteiros_diarios
                WHERE user_id = %s
                  AND data = %s
            """, (user_id, dia)).fetchone()

            if rotina:
                # Adiciona etapa de vestir com outfit pré-selecionado
                roteiro = rotina['roteiro']

                # Encontra atividade "Roupa" e enriquece
                for activity in roteiro.get('activities', []):
                    if activity['name'] == 'Vestir roupa':
                        activity['outfit'] = outfit
                        activity['duration'] = 5  # Reduz tempo pois já está decidido
                        activity['note'] = f"Outfit pré-planejado: {outfit['descricao']}"

                self.db.execute("""
                    UPDATE roteiros_diarios
                    SET roteiro = %s
                    WHERE id = %s
                """, (json.dumps(roteiro), rotina['id']))

        logger.info("👔 Outfits integrados nas rotinas da semana")
```

---

## 19.11 Integração: Wardrobe ↔ Calendar + Wellness

```python
class WardrobeIntegration:
    """Integração do guarda-roupa com calendário e bem-estar"""

    def __init__(self, db_connection, event_bus):
        self.db = db_connection
        self.event_bus = event_bus

        # Subscriptions
        self.event_bus.subscribe(
            EventType.CALENDAR_EVENT_CREATED,
            self.check_outfit_appropriateness
        )
        self.event_bus.subscribe(
            EventType.CYCLE_PHASE_CHANGED,
            self.adjust_comfort_priorities
        )

    async def check_outfit_appropriateness(self, event: Event):
        """Verifica se outfit planejado é apropriado para evento"""

        calendar_event = event.payload['event']
        user_id = event.payload['user_id']
        event_date = calendar_event['start_time'].date()

        # Busca outfit planejado para o dia
        plano = self.db.execute("""
            SELECT * FROM plano_semanal_looks
            WHERE user_id = %s
              AND semana_inicio <= %s
              AND semana_inicio + INTERVAL '7 days' > %s
        """, (user_id, event_date, event_date)).fetchone()

        if not plano:
            return

        dia_semana = event_date.weekday()
        outfit_planejado = plano['plano'][str(dia_semana)]

        # Analisa tipo de evento
        event_type = self.classify_event_formality(calendar_event)

        # Verifica compatibilidade
        outfit_details = self.get_outfit_details(outfit_planejado)
        is_appropriate = self.check_outfit_event_match(outfit_details, event_type)

        if not is_appropriate:
            logger.warn(f"👔 Outfit planejado inadequado para evento {event_type}")

            # Sugere alternativa
            alternative = self.suggest_appropriate_outfit(
                user_id,
                event_type,
                event_date
            )

            await self.event_bus.publish(Event(
                tipo=EventType.OUTFIT_CHANGED,
                modulo_origem='wardrobe_integration',
                payload={
                    'date': str(event_date),
                    'reason': f"Evento {event_type}: {calendar_event['title']}",
                    'original_outfit': outfit_planejado,
                    'suggested_outfit': alternative,
                    'requires_approval': True
                }
            ))

    def classify_event_formality(self, calendar_event):
        """Classifica formalidade do evento"""

        title = calendar_event['title'].lower()

        if any(w in title for w in ['apresentação', 'cliente', 'reunião importante']):
            return 'profissional'
        elif any(w in title for w in ['casual', 'café', 'almoço informal']):
            return 'casual'
        elif any(w in title for w in ['evento', 'networking', 'conferência']):
            return 'business_casual'
        else:
            return 'casual'

    def check_outfit_event_match(self, outfit, event_type):
        """Verifica se outfit combina com tipo de evento"""

        compatibility_matrix = {
            'profissional': ['profissional', 'business_casual'],
            'business_casual': ['profissional', 'business_casual', 'casual'],
            'casual': ['casual', 'business_casual']
        }

        outfit_occasions = outfit.get('ocasioes', ['casual'])
        compatible = compatibility_matrix.get(event_type, ['casual'])

        return any(occ in compatible for occ in outfit_occasions)

    async def adjust_comfort_priorities(self, event: Event):
        """Ajusta prioridades de conforto baseado em fase do ciclo"""

        user_id = event.payload['user_id']
        nova_fase = event.payload['nova_fase']

        # Menstruação: prioriza conforto máximo
        if nova_fase == 'menstruacao':
            logger.info("🌸 Ajustando guarda-roupa para conforto máximo")

            # Marca preferências temporárias
            self.db.execute("""
                UPDATE configuracoes_guarda_roupa
                SET preferencias_temporarias = jsonb_build_object(
                    'prioridade_conforto', 10,
                    'evitar_calcas_apertadas', true,
                    'preferir_vestidos_soltos', true,
                    'cores_preferidas', ARRAY['preto', 'cinza', 'azul-marinho']
                )
                WHERE user_id = %s
            """, (user_id,))

            # Regenera plano semanal com novas prioridades
            await self.event_bus.publish(Event(
                tipo=EventType.WEEKLY_PLAN_GENERATED,
                modulo_origem='wardrobe_integration',
                payload={
                    'user_id': user_id,
                    'regenerate': True,
                    'reason': 'cycle_phase_comfort_adjustment'
                }
            ))
```

---

## 19.12 Integração: Diplomat ↔ Calendar + Tasks

```python
class DiplomatIntegration:
    """Integração do módulo de relacionamentos"""

    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager

        # Subscriptions
        self.event_bus.subscribe(
            EventType.CALENDAR_EVENT_CREATED,
            self.check_if_one_on_one
        )
        self.event_bus.subscribe(
            EventType.TASK_COMPLETED,
            self.check_relationship_commitment
        )
        self.event_bus.subscribe(
            EventType.OVERLOAD_DETECTED,
            self.postpone_non_critical_networking
        )

    async def check_if_one_on_one(self, event: Event):
        """Verifica se evento é 1:1 e prepara automaticamente"""

        calendar_event = event.payload['event']
        user_id = event.payload['user_id']

        # Identifica se é 1:1 (2 participantes)
        attendees = calendar_event.get('attendees', [])

        if len(attendees) == 2:
            # Identifica a outra pessoa
            other_person_email = next(
                (a['email'] for a in attendees if a.get('self') is not True),
                None
            )

            if not other_person_email:
                return

            # Busca pessoa no banco de relacionamentos
            pessoa = self.db.execute("""
                SELECT * FROM pessoas_chave
                WHERE email = %s
            """, (other_person_email,)).fetchone()

            if pessoa:
                logger.info(f"🤝 Detectado 1:1 com {pessoa['nome']}")

                # Prepara reunião
                prep = await self.prepare_one_on_one(pessoa, calendar_event)

                # Cria task de preparação
                prep_task_id = self.db.execute("""
                    INSERT INTO tarefas
                    (descricao, tipo, deadline, big_rock_id, tags, fonte)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    f"Preparar 1:1 com {pessoa['nome']}",
                    'Tarefa',
                    calendar_event['start_time'] - timedelta(hours=2),
                    None,
                    ['relacionamento', '1:1', 'preparacao'],
                    'diplomat_module'
                )).fetchone()['id']

                await self.event_bus.publish(Event(
                    tipo=EventType.ONE_ON_ONE_SCHEDULED,
                    modulo_origem='diplomat_integration',
                    payload={
                        'pessoa_id': pessoa['id'],
                        'meeting': calendar_event,
                        'preparation': prep,
                        'prep_task_id': prep_task_id
                    }
                ))

    async def prepare_one_on_one(self, pessoa, meeting):
        """Prepara contexto para 1:1"""

        # Busca última interação
        last_interaction = self.db.execute("""
            SELECT * FROM interacoes
            WHERE pessoa_id = %s
            ORDER BY data DESC
            LIMIT 1
        """, (pessoa['id'],)).fetchone()

        # Busca follow-ups pendentes
        pending_followups = self.db.execute("""
            SELECT proximos_passos FROM interacoes
            WHERE pessoa_id = %s
              AND proximos_passos IS NOT NULL
              AND proximos_passos != '[]'
            ORDER BY data DESC
            LIMIT 5
        """, (pessoa['id'],)).fetchall()

        # Calcula health do relacionamento
        health = self.calculate_relationship_health(pessoa['id'])

        return {
            'last_interaction_summary': last_interaction['resumo'] if last_interaction else None,
            'pending_followups': [item for row in pending_followups for item in row['proximos_passos']],
            'relationship_health': health,
            'suggested_topics': self.generate_talking_points(pessoa, health)
        }

    async def check_relationship_commitment(self, event: Event):
        """Verifica se task completada está relacionada a compromisso"""

        task = event.payload['task']

        # Verifica se task tem pessoa_id no metadata
        pessoa_id = task.get('metadata', {}).get('pessoa_id')

        if pessoa_id:
            # Loga como interação
            self.db.execute("""
                INSERT INTO interacoes
                (pessoa_id, data, tipo, resumo, sentimento)
                VALUES (%s, NOW(), %s, %s, %s)
            """, (
                pessoa_id,
                'acao_completada',
                f"Completou compromisso: {task['descricao']}",
                'positivo'
            ))

            # Atualiza health
            new_health = self.calculate_relationship_health(pessoa_id)

            await self.event_bus.publish(Event(
                tipo=EventType.RELATIONSHIP_HEALTH_CHANGED,
                modulo_origem='diplomat_integration',
                payload={
                    'pessoa_id': pessoa_id,
                    'new_health': new_health,
                    'trigger': 'commitment_fulfilled'
                }
            ))

    async def postpone_non_critical_networking(self, event: Event):
        """Adia networking não-crítico durante sobrecarga"""

        user_id = event.payload['user_id']
        carga = event.payload['percentual_carga']

        if carga > 90:
            logger.info("🤝 Adiando networking não-crítico durante sobrecarga")

            # Busca relacionamentos em "atenção" mas não "crítico"
            non_critical_people = self.db.execute("""
                SELECT * FROM pessoas_chave
                WHERE user_id = %s
                  AND importancia != 'critica'
                  AND health_status = 'atencao'
            """, (user_id,)).fetchall()

            if non_critical_people:
                await self.event_bus.publish(Event(
                    tipo=EventType.RECONNECTION_REMINDER,
                    modulo_origem='diplomat_integration',
                    payload={
                        'suggestion': f'Você está sobrecarregada. Vou adiar {len(non_critical_people)} reconexões não-urgentes.',
                        'postponed_people': [p['nome'] for p in non_critical_people],
                        'new_reminder_date': (datetime.now() + timedelta(days=7)).date()
                    }
                ))

    def calculate_relationship_health(self, pessoa_id):
        """Calcula saúde do relacionamento"""

        # Busca última interação
        last_contact = self.db.execute("""
            SELECT data FROM interacoes
            WHERE pessoa_id = %s
            ORDER BY data DESC
            LIMIT 1
        """, (pessoa_id,)).fetchone()

        if not last_contact:
            return {'score': 0, 'status': 'critico'}

        # Calcula dias desde último contato
        days_since = (datetime.now().date() - last_contact['data'].date()).days

        # Busca frequência ideal
        pessoa = self.db.execute("""
            SELECT frequencia_contato_ideal FROM pessoas_chave
            WHERE id = %s
        """, (pessoa_id,)).fetchone()

        ideal_days = {
            'semanal': 7,
            'quinzenal': 14,
            'mensal': 30,
            'trimestral': 90
        }.get(pessoa['frequencia_contato_ideal'], 30)

        # Calcula score
        ratio = days_since / ideal_days

        if ratio <= 1.0:
            score = 100
            status = 'excelente'
        elif ratio <= 1.5:
            score = 75
            status = 'bom'
        elif ratio <= 2.0:
            score = 50
            status = 'atencao'
        else:
            score = 25
            status = 'critico'

        return {'score': score, 'status': status, 'days_since': days_since}
```

---

## 19.13 Orquestrador Central Integrado (ATUALIZADO)

```python
class CharleeOrchestrator(Agent):
    """Agente Central que coordena todos os módulos"""

    def __init__(self, db_connection, vector_db, event_bus, context_manager):
        self.db = db_connection
        self.vector_db = vector_db
        self.event_bus = event_bus
        self.context = context_manager

        # === MÓDULOS CORE (V1-V3) ===
        self.wellness_coach = WellnessCoachAgent(db_connection)
        self.capacity_guardian = CapacityGuardianAgent(db_connection)
        self.focus_guard = FocusGuardAgent(db_connection)
        self.okr_dashboard = OKRDashboardAgent(db_connection)
        self.projects_orchestrator = ProjectsOrchestrator(db_connection, event_bus)

        # === NOVOS MÓDULOS (V4+) ===
        from backend.modules.wealth.orchestrator import WealthOrchestrator
        from backend.modules.routines.orchestrator import RoutinesOrchestrator
        from backend.modules.wardrobe.orchestrator import WardrobeOrchestrator
        from backend.modules.diplomat.orchestrator import DiplomatOrchestrator

        self.wealth = WealthOrchestrator(db_connection, event_bus, context_manager)
        self.routines = RoutinesOrchestrator(db_connection, event_bus, context_manager)
        self.wardrobe = WardrobeOrchestrator(db_connection, event_bus)
        self.diplomat = DiplomatOrchestrator(db_connection, event_bus, context_manager)

        # === INTEGRAÇÕES CORE ===
        self.task_project_integration = TaskProjectIntegration(
            db_connection, event_bus, context_manager
        )
        self.focus_capacity_integration = FocusCapacityIntegration(
            db_connection, event_bus, context_manager
        )
        self.wellness_projects_integration = WellnessProjectsIntegration(
            db_connection, event_bus, self.wellness_coach
        )

        # === INTEGRAÇÕES NOVOS MÓDULOS ===
        self.wealth_wellness_integration = WealthWellnessIntegration(
            db_connection, event_bus, context_manager
        )
        self.routines_integration = RoutinesIntegration(
            db_connection, event_bus, context_manager
        )
        self.wardrobe_integration = WardrobeIntegration(
            db_connection, event_bus
        )
        self.diplomat_integration = DiplomatIntegration(
            db_connection, event_bus, context_manager
        )
        
        super().__init__(
            name="Charlee",
            model=OpenAIChat(id="gpt-4o"),
            team=[
                self.wellness_coach,
                self.capacity_guardian,
                self.focus_guard,
                self.okr_dashboard,
                self.projects_orchestrator
            ],
            storage=vector_db,
            instructions=[
                "Você é Charlee, o segundo cérebro de Samara",
                "Coordene todos os módulos de forma holística",
                "Considere SEMPRE o contexto global antes de decisões",
                "Priorize bem-estar sobre produtividade quando necessário",
                "Seja proativa em identificar conflitos entre módulos",
                "Comunique decisões de forma clara e justificada"
            ]
        )
        
        # Subscribe para eventos de decisão
        self.event_bus.subscribe(
            EventType.DECISION_REQUIRED,
            self.handle_cross_module_decision
        )
    
    async def handle_cross_module_decision(self, event: Event):
        """Resolve decisões que envolvem múltiplos módulos"""
        
        situacao = event.payload['situacao']
        modulos_envolvidos = event.payload['modulos']
        opcoes = event.payload['opcoes']
        
        # Busca contexto global
        context = self.context.get_context()
        
        # Consulta módulos envolvidos
        module_inputs = {}
        for modulo in modulos_envolvidos:
            agent = getattr(self, f"{modulo}_agent", None)
            if agent:
                module_inputs[modulo] = agent.provide_input_for_decision(situacao)
        
        # Usa LLM para decisão holística
        prompt = f"""
SITUAÇÃO REQUERENDO DECISÃO:
{situacao}

CONTEXTO GLOBAL:
- Fase ciclo: {context['fase_ciclo']}
- Energia: {context['energia_atual']}/10
- Carga trabalho: {context['carga_trabalho_percentual']:.0f}%
- Em foco: {context['em_sessao_foco']}
- Nível stress: {context['nivel_stress']}/10

INPUTS DOS MÓDULOS:
{json.dumps(module_inputs, indent=2)}

OPÇÕES DISPONÍVEIS:
{json.dumps(opcoes, indent=2)}

Como Charlee, analise holisticamente e decida:
1. Qual opção escolher
2. Por que (considerando todos os fatores)
3. Quais ações tomar
4. Como comunicar para Samara

Retorne JSON estruturado.
"""
        
        response = self.print_response(prompt, stream=False)
        decision = json.loads(response)
        
        # Salva decisão
        self.db.execute("""
            INSERT INTO decisoes_integradas
            (situacao, modulos_envolvidos, contexto_considerado,
             opcoes_avaliadas, decisao_tomada, justificativa)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            situacao,
            modulos_envolvidos,
            json.dumps(context),
            json.dumps(opcoes),
            decision['opcao_escolhida'],
            decision['justificativa']
        ))
        
        logger.info(f"🧠 Decisão cross-module tomada: {decision['opcao_escolhida']}")
        
        return decision
    
    def morning_briefing_integrated(self):
        """Briefing matinal considerando TODOS os módulos"""

        context = self.context.get_context()

        briefing = f"""
☀️ BOM DIA, SAMARA!

═══════════════════════════════════════════════════

🌸 BEM-ESTAR
• Fase: {context['fase_ciclo'].capitalize()}
• Energia esperada: {context['energia_atual']}/10
• Recomendação: {self.wellness_coach.get_daily_recommendation()}

📅 ROTINA DO DIA
{self.routines.get_today_summary()}

👔 OUTFIT DO DIA
{self.wardrobe.get_today_outfit()}

⚡ FOCO DO DIA
{self.get_daily_focus()}

📊 OKRS
{self.okr_dashboard.generate_okr_report()}

💼 PROJETOS FREELANCE
{self.projects_orchestrator.get_project_summary()}

💰 FINANÇAS
{self.wealth.get_daily_financial_summary()}

🤝 RELACIONAMENTOS
{self.diplomat.get_relationship_summary()}

📬 NOTIFICAÇÕES
{self.focus_guard.comm_manager.format_inbox_summary()}

⚖️ CARGA DE TRABALHO
• Atual: {context['carga_trabalho_percentual']:.0f}%
• Status: {self.capacity_guardian.get_capacity_status()}

═══════════════════════════════════════════════════

💡 INSIGHT DO DIA:
{self.generate_daily_insight()}

❓ Pronta para começar?
"""

        return briefing
    
    def get_daily_focus(self):
        """Determina foco do dia considerando todos os fatores"""
        
        context = self.context.get_context()
        
        # Busca tarefas priorizadas
        tasks = self.get_prioritized_tasks_integrated()
        
        # Ajusta por fase do ciclo
        optimal_type = context_manager.get_optimal_activity_type()
        
        # Filtra tasks compatíveis
        compatible_tasks = [
            t for t in tasks 
            if self.is_task_compatible_with_context(t, optimal_type)
        ]
        
        if compatible_tasks:
            top_task = compatible_tasks[0]
            return f"""
🎯 PRIORIDADE MÁXIMA:
{top_task['descricao']}

💡 Por quê agora?
• Alinhado com sua fase {context['fase_ciclo']}
• Tipo de atividade ideal: {optimal_type}
• Deadline: {top_task['deadline']}
"""
        else:
            return "Nenhuma tarefa urgente hoje. Bom momento para planejamento estratégico."
    
    def generate_daily_insight(self):
        """Gera insight diário cross-module"""
        
        # Analisa padrões dos últimos 7 dias
        insights = []
        
        # Wellness patterns
        wellness_insight = self.wellness_coach.get_weekly_pattern()
        if wellness_insight:
            insights.append(wellness_insight)
        
        # Productivity patterns
        prod_insight = self.analyze_productivity_pattern()
        if prod_insight:
            insights.append(prod_insight)
        
        # Projects insights
        projects_insight = self.projects_orchestrator.get_strategic_insight()
        if projects_insight:
            insights.append(projects_insight)
        
        if insights:
            return "\n• ".join(insights)
        else:
            return "Continue assim! Seus padrões estão saudáveis."
```

---

## 19.10 CLI Integrado

```bash
# Briefing matinal completo
$ charlee morning

☀️ BOM DIA, SAMARA!
[Output do briefing integrado completo]

---

# Comando integrado que considera tudo
$ charlee decide "Aceitar projeto Upwork $2000"

🧠 ANÁLISE INTEGRADA...

✅ Consultando módulos:
  • Wellness Coach: Fase folicular, energia alta ✅
  • Capacity Guardian: Carga atual 72%, viável ✅
  • Projects Analyzer: Projeto bem avaliado (score 0.82) ✅
  • Focus Module: Sem sessões críticas próximas ✅

💡 RECOMENDAÇÃO: ACEITAR COM AJUSTES

Justificativa:
• Valor justo para complexidade estimada
• Alinhado com suas skills atuais
• Fase do ciclo favorável para início de projeto
• Carga permite absorver 15h/semana

⚠️ ATENÇÃO:
• Você já tem apresentação Syssa em 3 semanas
• Recomendo negociar deadline para 6 semanas (não 4)

📝 Mensagem de contra-proposta preparada:
[Ver rascunho]

Confirmar aceitação? [S/n]:

---

# Status geral
$ charlee status

📊 STATUS GLOBAL - CHARLEE

🌸 Bem-estar: 8/10 (Fase folicular)
⚡ Energia: 8/10
⚖️ Carga: 72% (Saudável)
🎯 Foco: Ativo (Deep work até 12:30)
💼 Projetos: 2 ativos, 1 pendente análise
📬 Notificações: 3 urgentes, 12 adiadas
📊 OKRs: 2 no caminho, 1 em risco

💡 Tudo sob controle! Continue assim.

---

# Comando de emergência
$ charlee emergency-mode

🚨 MODO EMERGÊNCIA ATIVADO

Ações automáticas:
✅ Todas notificações não-críticas bloqueadas
✅ Reuniões não-essenciais sugeridas para cancelamento
✅ Novos projetos pausados automaticamente
✅ Sessão de foco forçada (próximas 4h)
✅ Alertas de bem-estar ativados

Você está protegida. Foque apenas no essencial.

Desativar: charlee emergency-mode off
```

---

## 19.11 Métricas de Integração

```python
def get_integration_health_metrics():
    """Métricas de saúde da integração"""
    
    metrics = {
        'eventos_processados_24h': db.execute("""
            SELECT COUNT(*) FROM system_events
            WHERE criado_em > NOW() - INTERVAL '24 hours'
              AND processado = TRUE
        """).fetchone()['count'],
        
        'latencia_media_eventos': db.execute("""
            SELECT AVG(EXTRACT(EPOCH FROM (processado_em - criado_em)))
            FROM system_events
            WHERE processado_em IS NOT NULL
              AND criado_em > NOW() - INTERVAL '24 hours'
        """).fetchone()['avg'],
        
        'decisoes_cross_module_7d': db.execute("""
            SELECT COUNT(*) FROM decisoes_integradas
            WHERE criado_em > NOW() - INTERVAL '7 days'
        """).fetchone()['count'],
        
        'taxa_sucesso_integracao': db.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE executado = TRUE) * 100.0 / 
                COUNT(*)
            FROM decisoes_integradas
            WHERE criado_em > NOW() - INTERVAL '30 days'
        """).fetchone(),
        
        'contexto_atualizado_ultima_vez': db.execute("""
            SELECT atualizado_em FROM contexto_global
            ORDER BY atualizado_em DESC LIMIT 1
        """).fetchone()['atualizado_em']
    }
    
    return metrics
```

---

**Pronto!** 🎉

Agora todos os módulos estão **completamente integrados**:

✅ **Event Bus** conecta tudo em tempo real  
✅ **Context Manager** mantém visão holística  
✅ **Integrações específicas** entre módulos  
✅ **Orquestrador Central** resolve conflitos  
✅ **CLI unificado** para controle total  
✅ **Métricas** de saúde da integração  

---

## 19.14 Fluxos End-to-End com Novos Módulos

### Fluxo 1: Início da Manhã (Todos os módulos)

```
7:00 AM - Samara acorda

┌─────────────────────────────────────────────────────────┐
│ 1. ROUTINES MODULE                                      │
│    └─> Gera roteiro matinal baseado em:                │
│        • Fase do ciclo (energia disponível)             │
│        • Eventos do calendário hoje                     │
│        • Carga de trabalho atual                        │
│        ↓                                                │
│    Event: ROUTINE_GENERATED                             │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ 2. WARDROBE MODULE (subscribed to ROUTINE_GENERATED)    │
│    └─> Confirma outfit do dia:                         │
│        • Verifica eventos do calendário                 │
│        • Ajusta por fase do ciclo (conforto?)          │
│        • Integra no passo "Vestir" da rotina           │
│        ↓                                                │
│    Event: WEEKLY_PLAN_CONFIRMED                         │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ 3. WEALTH MODULE (subscribed to ROUTINE_STARTED)        │
│    └─> Verifica orçamento do dia:                      │
│        • Modo proteção ativo? (TPM ou overload)        │
│        • Gastos planejados hoje                        │
│        • Alerta se meta em risco                       │
│        ↓                                                │
│    Event: FINANCIAL_FORECAST_UPDATED                    │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ 4. DIPLOMAT MODULE (subscribed to MORNING_SCRIPT_READY) │
│    └─> Verifica reuniões do dia:                       │
│        • 1:1s agendados?                               │
│        • Cria tasks de preparação                      │
│        • Alerta reconexões pendentes                   │
│        ↓                                                │
│    Event: ONE_ON_ONE_SCHEDULED (se aplicável)           │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ 5. ORCHESTRATOR                                         │
│    └─> Sintetiza briefing completo:                    │
│        • Bem-estar (fase, energia)                     │
│        • Rotina do dia                                 │
│        • Outfit escolhido                              │
│        • Foco prioritário                              │
│        • Situação financeira                           │
│        • Relacionamentos que precisam atenção          │
│        ↓                                                │
│    Apresenta briefing matinal unificado                 │
└─────────────────────────────────────────────────────────┘
```

### Fluxo 2: Detecção de Sobrecarga (Multi-módulo)

```
Usuario completa 10ª tarefa do dia → Capacity Guardian detecta overload (95%)

┌─────────────────────────────────────────────────────────┐
│ Event: OVERLOAD_DETECTED                                │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────────┐
        │           │           │               │
        ▼           ▼           ▼               ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ WEALTH   │ │ DIPLOMAT │ │ FOCUS    │ │ ROUTINES     │
│          │ │          │ │          │ │              │
│ Ativa    │ │ Adia     │ │ Bloqueia │ │ Adiciona     │
│ proteção │ │ networking│ │ notifs   │ │ pausas       │
│ impulso  │ │ não-crítico│ │ não-    │ │ obrigatórias │
│ spending │ │          │ │ urgentes │ │              │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │            │               │
     └────────────┴────────────┴───────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Context Manager       │
        │  atualiza:             │
        │  • stress_nivel = 9    │
        │  • necessita_pausa =   │
        │    TRUE                │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  ORCHESTRATOR          │
        │  Sintetiza ação:       │
        │  "Modo proteção ativo" │
        │  + Lista de ações      │
        │    tomadas             │
        └───────────────────────┘
```

### Fluxo 3: Mudança de Fase do Ciclo (Cascata de ajustes)

```
Wellness Coach detecta: Fase mudou para "pre_menstrual" (TPM)

┌─────────────────────────────────────────────────────────┐
│ Event: CYCLE_PHASE_CHANGED                              │
│ payload: { nova_fase: "pre_menstrual",                  │
│            energia_esperada: 0.60 }                     │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────────┐
        │           │           │               │
        ▼           ▼           ▼               ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ WEALTH   │ │ ROUTINES │ │ WARDROBE │ │ CAPACITY     │
│          │ │          │ │          │ │              │
│ • Limite │ │ • +15min │ │ • Priori-│ │ • Reduz      │
│   impulso│ │   buffer │ │   za con-│ │   threshold  │
│   = 50%  │ │ • Exercise│ │   forto  │ │   de alerta  │
│ • Modo   │ │   optional│ │ • Evita  │ │   (mais      │
│   TPM    │ │ • Mais   │ │   calcas │ │   protetor)  │
│   ativo  │ │   pausas │ │   apertad│ │              │
│          │ │          │ │   as     │ │              │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │            │               │
     │            │            │               │
     └────────────┴────────────┴───────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Context Manager       │
        │  atualiza:             │
        │  • fase_ciclo = TPM    │
        │  • energia = 6/10      │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  Todos módulos agora   │
        │  operam com awareness  │
        │  de TPM                │
        └───────────────────────┘

Resultado para usuária:
• Rotinas ajustadas automaticamente
• Proteção financeira ativada
• Outfits mais confortáveis priorizados
• Menor threshold para pausas obrigatórias
```

---

## 19.15 Tabela de Status de Integração

| Módulo | Status | Eventos Publicados | Eventos Subscritos | Integrado com | Prioridade V4 |
|--------|--------|-------------------|-------------------|---------------|---------------|
| **Task Manager** | ✅ V1 | task_created, task_completed | capacity_warning, overload_detected | Todos | - |
| **Wellness Coach** | ✅ V1 | cycle_phase_changed, energy_low | - | Todos | - |
| **Capacity Guardian** | ✅ V2 | overload_detected, capacity_warning | task_created, focus_ended | Todos | - |
| **Focus Module** | ✅ V2 | focus_started, interruption_blocked | capacity_critical | Capacity, Tasks | - |
| **OKR Dashboard** | ✅ V2 | okr_updated, milestone_achieved | task_completed | Tasks | - |
| **Projects Module** | ✅ V2 | project_accepted, project_completed | cycle_phase_changed | Tasks, Wellness | - |
| **Calendar Integration** | ✅ V3.2 | calendar_event_created | - | Todos | - |
| **Multimodal Input** | ✅ V3.3 | - | - | Task Manager | - |
| **Wealth Module** | 📋 V4 | expense_created, impulse_alert, goal_at_risk | cycle_phase_changed, overload_detected | Wellness, Capacity | 🔥 Alta |
| **Routines Module** | 📋 V4 | routine_generated, routine_interrupted | cycle_phase_changed, calendar_event_created | Wellness, Calendar, Wardrobe | 🔥 Alta |
| **Wardrobe Module** | 📋 V4 | weekly_plan_generated, outfit_changed | calendar_event_created, cycle_phase_changed | Calendar, Wellness, Routines | 🟡 Média |
| **Diplomat Module** | 📋 V4 | one_on_one_scheduled, relationship_health_changed | calendar_event_created, task_completed | Calendar, Tasks | 🟡 Média |

### Legenda
- ✅ Implementado
- 📋 Documentado, pronto para implementação
- 🔥 Alta prioridade
- 🟡 Média prioridade

---

## 19.16 Métricas de Integração Consolidadas

```python
def get_consolidated_integration_metrics():
    """Métricas consolidadas de todos os módulos"""

    return {
        'eventos': {
            'processados_24h': db.execute("""
                SELECT COUNT(*) FROM system_events
                WHERE criado_em > NOW() - INTERVAL '24 hours'
                  AND processado = TRUE
            """).fetchone()['count'],

            'por_modulo': db.execute("""
                SELECT modulo_origem, COUNT(*) as total
                FROM system_events
                WHERE criado_em > NOW() - INTERVAL '24 hours'
                GROUP BY modulo_origem
                ORDER BY total DESC
            """).fetchall(),

            'latencia_media_ms': db.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (processado_em - criado_em)) * 1000)
                FROM system_events
                WHERE processado_em IS NOT NULL
                  AND criado_em > NOW() - INTERVAL '24 hours'
            """).fetchone()['avg']
        },

        'cross_module_decisions': {
            'ultimas_24h': db.execute("""
                SELECT COUNT(*) FROM decisoes_integradas
                WHERE criado_em > NOW() - INTERVAL '24 hours'
            """).fetchone()['count'],

            'taxa_sucesso': db.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE executado = TRUE) * 100.0 / COUNT(*)
                FROM decisoes_integradas
                WHERE criado_em > NOW() - INTERVAL '7 days'
            """).fetchone()['?column?']
        },

        'modulos_novos': {
            'wealth': {
                'expenses_tracked': db.execute("""
                    SELECT COUNT(*) FROM despesas
                    WHERE criado_em > NOW() - INTERVAL '7 days'
                """).fetchone()['count'],

                'impulse_blocks': db.execute("""
                    SELECT COUNT(*) FROM system_events
                    WHERE tipo = 'wealth.impulse_alert'
                      AND criado_em > NOW() - INTERVAL '7 days'
                """).fetchone()['count']
            },

            'routines': {
                'routines_generated': db.execute("""
                    SELECT COUNT(*) FROM roteiros_diarios
                    WHERE criado_em > NOW() - INTERVAL '7 days'
                """).fetchone()['count'],

                'completion_rate': db.execute("""
                    SELECT
                        COUNT(*) FILTER (WHERE status = 'completo') * 100.0 / COUNT(*)
                    FROM roteiros_diarios
                    WHERE data > CURRENT_DATE - INTERVAL '7 days'
                """).fetchone()['?column?']
            },

            'wardrobe': {
                'weekly_plans_active': db.execute("""
                    SELECT COUNT(*) FROM plano_semanal_looks
                    WHERE semana_inicio <= CURRENT_DATE
                      AND semana_inicio + INTERVAL '7 days' > CURRENT_DATE
                """).fetchone()['count'],

                'outfit_changes': db.execute("""
                    SELECT COUNT(*) FROM system_events
                    WHERE tipo = 'wardrobe.outfit_changed'
                      AND criado_em > NOW() - INTERVAL '7 days'
                """).fetchone()['count']
            },

            'diplomat': {
                'relationships_tracked': db.execute("""
                    SELECT COUNT(*) FROM pessoas_chave
                """).fetchone()['count'],

                'interactions_logged': db.execute("""
                    SELECT COUNT(*) FROM interacoes
                    WHERE data > NOW() - INTERVAL '7 days'
                """).fetchone()['count'],

                'health_critical': db.execute("""
                    SELECT COUNT(*) FROM pessoas_chave
                    WHERE health_status = 'critico'
                """).fetchone()['count']
            }
        },

        'health_geral': {
            'context_freshness': db.execute("""
                SELECT EXTRACT(EPOCH FROM (NOW() - atualizado_em)) / 60
                FROM contexto_global
                ORDER BY atualizado_em DESC LIMIT 1
            """).fetchone()['?column?'],  # minutos desde última atualização

            'modules_active': 11,  # Core (7) + New (4)
            'integrations_active': 7
        }
    }
```

---

**Pronto!** 🎉

Agora o arquivo **`Charlee_integracao_modulos.md`** está **completamente atualizado** com:

✅ **Arquitetura expandida** incluindo os 4 novos módulos
✅ **Event Bus atualizado** com 18 novos tipos de eventos
✅ **4 novas seções de integração**:
   - Wealth ↔ Wellness + Capacity
   - Routines ↔ Wellness + Wardrobe + Calendar
   - Wardrobe ↔ Calendar + Wellness
   - Diplomat ↔ Calendar + Tasks

✅ **Orquestrador atualizado** com todos os módulos V4+
✅ **Briefing matinal expandido** incluindo finanças, rotinas, outfit e relacionamentos
✅ **3 fluxos end-to-end** mostrando coordenação multi-módulo
✅ **Tabela de status** de integração de todos os módulos
✅ **Métricas consolidadas** incluindo estatísticas dos novos módulos

**Todos os módulos agora estão integrados ao orquestrador central via Event Bus!** 🚀

---

## 19.17 Auto-Conhecimento e Consciência Arquitetural do Charlee

### 🧠 Visão Geral

O Charlee possui **auto-conhecimento** de sua própria arquitetura, permitindo:

1. **Ensinar o usuário** a utilizar recursos disponíveis
2. **Detectar dificuldades** e oferecer ajuda proativa
3. **Auxiliar no desenvolvimento** de novas versões (apenas admin)
4. **Sugerir melhorias** baseado em padrões de uso

### 🔐 Níveis de Acesso

```python
class AccessLevel(Enum):
    """Níveis de acesso às informações do sistema"""

    USER = "user"              # Usuário final: funcionalidades e tutoriais
    ADMIN = "admin"            # Admin/Developer: arquitetura completa, debugging
    SYSTEM = "system"          # Acesso interno entre módulos

# Informações sensíveis NUNCA devem ser expostas para USER
RESTRICTED_INFO = {
    "admin_only": [
        "database_schemas",
        "api_keys_management",
        "system_architecture",
        "event_bus_internals",
        "integration_code",
        "security_mechanisms"
    ]
}
```

### 📚 Sistema de Ensino Proativo (USER Level)

```python
class CharleeTeacher:
    """
    Sistema de ensino proativo do Charlee
    Detecta quando usuário não está usando recursos disponíveis
    """

    def __init__(self, db_connection, user_id):
        self.db = db_connection
        self.user_id = user_id
        self.usage_patterns = self.load_usage_patterns()

    async def analyze_user_behavior(self):
        """Analisa comportamento para oferecer ajuda"""

        suggestions = []

        # 1. Usuário criando muitas tarefas manualmente?
        if self.is_creating_repetitive_tasks():
            suggestions.append({
                "tipo": "feature_discovery",
                "feature": "Rotinas Automatizadas",
                "mensagem": "💡 Percebi que você cria tarefas similares toda semana. "
                           "Você sabia que pode criar rotinas automatizadas? "
                           "Quer que eu te mostre como?"
            })

        # 2. Usuário não está usando BigRocks?
        if self.is_not_using_bigrocks():
            suggestions.append({
                "tipo": "feature_discovery",
                "feature": "BigRocks",
                "mensagem": "💡 Você tem muitas tarefas soltas! BigRocks ajudam a "
                           "organizar tarefas por área da vida. Posso criar alguns para você?"
            })

        # 3. Usuário registrou período menstrual mas não usa predições?
        if self.registered_cycle_but_not_using():
            suggestions.append({
                "tipo": "feature_discovery",
                "feature": "Predições de Ciclo",
                "mensagem": "🌸 Você registrou seu ciclo! Posso usar isso para ajustar "
                           "automaticamente suas rotinas e proteger seu bem-estar. Ativar?"
            })

        # 4. Usuário tem reuniões 1:1 mas não usa Diplomat?
        if self.has_recurring_meetings_but_no_diplomat():
            suggestions.append({
                "tipo": "feature_discovery",
                "feature": "Diplomat (CRM Pessoal)",
                "mensagem": "🤝 Vi que você tem várias reuniões 1:1 recorrentes. "
                           "Posso te ajudar a preparar essas reuniões automaticamente?"
            })

        # 5. Usuário gasta muito tempo escolhendo roupa?
        if self.detects_morning_delay_pattern():
            suggestions.append({
                "tipo": "feature_discovery",
                "feature": "Planejamento de Outfits",
                "mensagem": "👔 Notei que suas manhãs ficam longas. Planejamento semanal "
                           "de outfits economiza ~15min/dia. Quer experimentar?"
            })

        return suggestions

    def is_creating_repetitive_tasks(self) -> bool:
        """Detecta padrão de tarefas repetitivas"""

        recent_tasks = self.db.execute("""
            SELECT descricao FROM tarefas
            WHERE user_id = %s
              AND criado_em > NOW() - INTERVAL '30 days'
        """, (self.user_id,)).fetchall()

        # Usa similarity para detectar tarefas parecidas
        from difflib import SequenceMatcher

        repetitive_count = 0
        for i, task1 in enumerate(recent_tasks):
            for task2 in recent_tasks[i+1:]:
                similarity = SequenceMatcher(
                    None,
                    task1['descricao'].lower(),
                    task2['descricao'].lower()
                ).ratio()

                if similarity > 0.7:  # 70% similar
                    repetitive_count += 1

        return repetitive_count > 5  # Mais de 5 pares de tarefas similares

    def is_not_using_bigrocks(self) -> bool:
        """Verifica se usuário não usa BigRocks"""

        bigrocks_count = self.db.execute("""
            SELECT COUNT(*) FROM big_rocks
            WHERE user_id = %s
        """, (self.user_id,)).fetchone()['count']

        tasks_count = self.db.execute("""
            SELECT COUNT(*) FROM tarefas
            WHERE user_id = %s
              AND big_rock_id IS NULL
        """, (self.user_id,)).fetchone()['count']

        # Tem muitas tarefas mas nenhum BigRock
        return bigrocks_count == 0 and tasks_count > 10

    def registered_cycle_but_not_using(self) -> bool:
        """Usuário registrou ciclo mas não ativou features relacionadas"""

        has_cycle_data = self.db.execute("""
            SELECT COUNT(*) FROM registro_ciclo
            WHERE user_id = %s
        """, (self.user_id,)).fetchone()['count'] > 0

        using_cycle_features = self.db.execute("""
            SELECT configuracoes->>'cycle_aware_scheduling' as enabled
            FROM user_preferences
            WHERE user_id = %s
        """, (self.user_id,)).fetchone()

        return has_cycle_data and not using_cycle_features.get('enabled', False)

    async def offer_tutorial(self, feature: str):
        """Oferece tutorial interativo de uma feature"""

        tutorials = {
            "Rotinas Automatizadas": """
📅 ROTINAS AUTOMATIZADAS - Tutorial Rápido

Rotinas eliminam decisões repetitivas. Você define UMA VEZ,
Charlee executa SEMPRE.

Exemplo: Rotina Matinal
1. "Charlee, crie uma rotina matinal"
2. Eu pergunto: "A que horas você acorda?"
3. Você lista atividades: "Pelinhos, hidratação, maquiagem..."
4. Eu crio cronograma otimizado
5. Toda manhã, você recebe o roteiro pronto!

Economia: ~30min/semana de planejamento
Benefício: Zero decisões pela manhã = energia para o que importa

Quer criar sua primeira rotina agora?
""",

            "BigRocks": """
🪨 BIGROCKS - Tutorial Rápido

BigRocks = Grandes áreas da sua vida que precisam de atenção semanal.

Exemplos:
• 💼 Trabalho Syssa (15h/semana)
• 🎓 Mestrado (10h/semana)
• 💪 Saúde & Fitness (5h/semana)
• 👥 Relacionamentos (3h/semana)

Como funciona:
1. Você define capacidade de cada BigRock
2. Charlee te alerta quando um está sobrecarregado
3. Tarefas ficam organizadas por área
4. Você visualiza facilmente onde seu tempo vai

Quer que eu crie BigRocks para você com base nas suas tarefas atuais?
""",

            "Diplomat (CRM Pessoal)": """
🤝 DIPLOMAT - Tutorial Rápido

Diplomat = CRM para suas relações pessoais/profissionais importantes.

Problema que resolve:
"Quando foi a última vez que falei com meu mentor?"
"O que discutimos na última 1:1 com minha chefe?"
"Preciso reconectar com aquele contato de networking..."

Como funciona:
1. Você cadastra pessoas importantes (chefe, mentor, pupilos...)
2. Define frequência ideal de contato (semanal, mensal...)
3. Charlee te alerta quando relação precisa atenção
4. Antes de cada 1:1, recebe resumo automático:
   - Última conversa
   - Follow-ups pendentes
   - Sugestões de tópicos

Economia: ~2h/mês em preparação de reuniões
Benefício: Relacionamentos mais fortes e consistentes

Quer cadastrar sua primeira pessoa importante?
"""
        }

        return tutorials.get(feature, "Tutorial não encontrado")


class CharleeIntrospection:
    """
    Sistema de auto-conhecimento do Charlee
    Permite que Charlee explique sua própria arquitetura
    """

    def __init__(self, access_level: AccessLevel):
        self.access_level = access_level

    def explain_architecture(self, question: str) -> str:
        """
        Charlee explica sua própria arquitetura
        Resposta varia conforme nível de acesso
        """

        # USER: Explicações de alto nível, focadas em benefícios
        if self.access_level == AccessLevel.USER:
            return self._explain_for_user(question)

        # ADMIN: Detalhes técnicos completos
        elif self.access_level == AccessLevel.ADMIN:
            return self._explain_for_admin(question)

    def _explain_for_user(self, question: str) -> str:
        """Explicações para usuário final (high-level)"""

        user_explanations = {
            "como você funciona?": """
🧠 Como eu funciono (versão simples):

Sou um sistema modular que aprende com você:

1. **Módulos Especializados**: Tenho "cérebros" diferentes para cada área:
   - Um para tarefas e produtividade
   - Um para seu bem-estar e ciclo menstrual
   - Um para suas finanças comportamentais
   - Um para seus relacionamentos
   - E vários outros!

2. **Coordenação Inteligente**: Esses módulos conversam entre si.
   Exemplo: Se você está em TPM + sobrecarregada, meu módulo financeiro
   bloqueia compras impulsivas automaticamente.

3. **Memória Compartilhada**: Tudo que você me conta fica armazenado
   de forma segura. Eu lembro do contexto e melhoro com o tempo.

4. **Proatividade**: Não espero você pedir. Vejo padrões e ofereço
   ajuda antes de você precisar.

Quer saber mais sobre algum módulo específico?
""",

            "quais recursos você tem?": """
📦 Recursos Disponíveis (versão atual):

✅ **Implementados:**
- Task Manager: Gestão inteligente de tarefas
- BigRocks: Organização por áreas da vida
- Cycle Tracking: Rastreamento de ciclo menstrual
- Capacity Guardian: Proteção contra sobrecarga
- Focus Mode: Bloqueio de distrações
- Calendar Integration: Sincronização com Google/Microsoft
- Multimodal Input: Envio de áudio, imagem, texto

📋 **Em Documentação (próximas versões):**
- Charlee Wealth: Finanças comportamentais
- Charlee Routines: Rotinas automatizadas
- Charlee Wardrobe: Planejamento de outfits
- Charlee Diplomat: CRM pessoal

Qual recurso você gostaria de explorar?
""",

            "como você me protege?": """
🛡️ Como eu protejo você:

1. **Proteção de Capacidade:**
   - Monitoro sua carga de trabalho em tempo real
   - Bloqueio novas tarefas quando você está no limite
   - Sugiro pausas antes de você quebrar

2. **Proteção de Bem-Estar:**
   - Ajusto expectativas baseado na sua fase do ciclo
   - Reduzo pressão durante menstruação/TPM
   - Recomendo atividades adequadas para sua energia

3. **Proteção Financeira (V4+):**
   - Detecto padrões de gasto impulsivo
   - Bloqueio compras durante stress/TPM
   - Te protejo de você mesma em momentos vulneráveis 😊

4. **Proteção de Foco:**
   - Bloqueio notificações não-urgentes
   - Cancelo reuniões desnecessárias em crises
   - Defendo seu tempo como se fosse meu

Meu trabalho é ser sua guardiã digital!
"""
        }

        return user_explanations.get(
            question.lower(),
            "Não entendi sua pergunta. Pode reformular?"
        )

    def _explain_for_admin(self, question: str) -> str:
        """Explicações técnicas completas (ADMIN ONLY)"""

        admin_explanations = {
            "arquitetura completa": """
🏗️ ARQUITETURA COMPLETA DO CHARLEE (ADMIN VIEW)

**Stack Tecnológico:**
- Backend: FastAPI + Python 3.11+
- Database: PostgreSQL 15 + PgVector (embeddings)
- Cache/Sessions: Redis 7
- LLM: GPT-4o (orquestrador) + GPT-4o-mini (agentes especializados)
- Frontend: React + TypeScript (V3.0)
- Deployment: Docker + Docker Compose

**Camadas Arquiteturais:**

1. **API Layer** (`backend/api/`)
   - REST endpoints (OpenAPI/Swagger)
   - Authentication: JWT tokens
   - Rate limiting: Redis-based
   - CORS: Configurável por ambiente

2. **Orchestrator Layer** (`backend/orchestrator/`)
   - `CharleeOrchestrator`: Agente central (PhiData Agent)
   - Intent Analysis: Classifica intenção do usuário
   - Agent Router: Roteia para agente especializado
   - Context Manager: Mantém estado global

3. **Agent Layer** (`backend/agent/`)
   - Agentes especializados por domínio
   - Cada agente tem acesso ao Event Bus
   - Comunicação assíncrona via pub/sub

4. **Integration Layer** (`backend/integrations/`)
   - Google Calendar OAuth 2.0
   - Microsoft Calendar OAuth 2.0
   - Webhooks para sync bidirecional
   - API clients para serviços externos

5. **Data Layer** (`backend/db/`)
   - PostgreSQL: Dados estruturados + JSONB
   - PgVector: Embeddings para memória semântica
   - Redis: Cache + Sessions + Event Queue

**Event Bus Architecture:**

```python
# Fluxo de evento:
1. Agente A: event_bus.publish(Event(...))
2. Event Bus: Salva em PostgreSQL + Redis
3. Event Bus: Notifica subscribers (async)
4. Agentes B, C, D: Recebem evento em paralelo
5. Cada agente processa independentemente
6. Resultados propagam novos eventos (cascata)
```

**State Management:**

- **Session State** (Redis): TTL 24h
  - Conversação atual
  - Contexto temporário
  - Cache de queries frequentes

- **Long-term State** (PostgreSQL):
  - Histórico completo de tarefas
  - Registro de ciclo menstrual
  - Preferências do usuário
  - Relacionamentos (Diplomat)

- **Semantic Memory** (PgVector):
  - Embeddings de conversas passadas
  - Busca semântica de contexto relevante
  - Aprendizado de padrões

**Security Mechanisms:**

1. **Authentication:**
   - JWT tokens com refresh
   - Sessões invalidáveis (Redis blacklist)
   - Rate limiting por usuário

2. **Authorization:**
   - Role-based: USER vs ADMIN
   - Resource-level permissions
   - Admin-only endpoints bloqueados

3. **Data Protection:**
   - Passwords: bcrypt + salt
   - API keys: Encrypted at rest
   - PII: Encrypted columns (PostgreSQL)

4. **API Security:**
   - HTTPS only
   - CORS whitelist
   - Input validation (Pydantic)
   - SQL injection protection (parameterized queries)

**Observability:**

- Logging: Structured (JSON) via loguru
- Metrics: Prometheus-compatible
- Tracing: Correlation IDs em eventos
- Debugging: Event history por correlation_id

**Deployment:**

```yaml
Production Stack:
- 2x Orchestrator instances (load balanced)
- 1x PostgreSQL (replicado)
- 1x Redis (sentinel mode)
- Nginx como reverse proxy
```

Quer detalhes sobre alguma camada específica?
""",

            "database schema completo": """
📊 DATABASE SCHEMA COMPLETO (ADMIN ONLY)

**Core Tables:**

```sql
-- Usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',  -- 'user' ou 'admin'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tarefas
CREATE TABLE tarefas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    descricao TEXT NOT NULL,
    tipo TEXT,  -- 'Tarefa', 'Compromisso Fixo', etc
    deadline TIMESTAMP,
    big_rock_id UUID REFERENCES big_rocks(id),
    status TEXT DEFAULT 'Pendente',
    prioridade INTEGER,
    estimativa_horas FLOAT,
    tags TEXT[],
    fonte TEXT,  -- origem da tarefa
    id_externo TEXT,  -- ID em sistema externo
    metadata JSONB,  -- dados extras flexíveis
    criado_em TIMESTAMP DEFAULT NOW(),
    concluido_em TIMESTAMP
);

-- BigRocks
CREATE TABLE big_rocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    nome TEXT NOT NULL,
    cor TEXT,
    capacidade_semanal FLOAT,  -- horas
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Ciclo Menstrual
CREATE TABLE registro_ciclo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    data_inicio DATE NOT NULL,
    duracao_ciclo INTEGER,  -- dias
    duracao_menstruacao INTEGER,
    sintomas JSONB,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Calendar Events (cached)
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    provider TEXT,  -- 'google' ou 'microsoft'
    external_id TEXT,
    title TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    attendees JSONB,
    synced_at TIMESTAMP DEFAULT NOW()
);
```

**Event Bus Tables:**

```sql
-- System Events
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo TEXT NOT NULL,
    modulo_origem TEXT NOT NULL,
    payload JSONB NOT NULL,
    prioridade INTEGER DEFAULT 5,
    processado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT NOW(),
    processado_em TIMESTAMP
);

-- Cross-Module Relations
CREATE TABLE cross_module_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_relacao TEXT NOT NULL,
    modulo_origem TEXT NOT NULL,
    entidade_origem_id UUID NOT NULL,
    modulo_destino TEXT NOT NULL,
    entidade_destino_id UUID NOT NULL,
    metadata JSONB,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Context Global
CREATE TABLE contexto_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    fase_ciclo TEXT,
    energia_atual INTEGER,
    carga_trabalho_percentual FLOAT,
    em_sessao_foco BOOLEAN DEFAULT FALSE,
    nivel_stress INTEGER,
    atualizado_em TIMESTAMP DEFAULT NOW()
);
```

**V4+ Module Tables:**

```sql
-- Wealth Module
CREATE TABLE despesas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    valor NUMERIC(10, 2),
    estabelecimento TEXT,
    data TIMESTAMP,
    categoria TEXT,
    contexto_comportamental JSONB,  -- fase_ciclo, stress, etc
    meta_id UUID REFERENCES metas_financeiras(id),
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Routines Module
CREATE TABLE roteiros_diarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    data DATE,
    roteiro JSONB,  -- cronograma completo
    energia_percentual NUMERIC(5, 2),
    fase_ciclo TEXT,
    status TEXT,  -- 'pendente', 'em_andamento', 'completo'
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Wardrobe Module
CREATE TABLE roupas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    nome TEXT,
    tipo TEXT,  -- 'camiseta', 'calca', 'tenis'
    cor_primaria TEXT,
    estampa TEXT,
    ocasioes TEXT[],
    status TEXT,  -- 'limpa', 'para_lavar'
    foto_url TEXT,
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE plano_semanal_looks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    semana_inicio DATE,
    plano JSONB,  -- outfits para cada dia
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Diplomat Module
CREATE TABLE pessoas_chave (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    nome TEXT NOT NULL,
    email TEXT,
    categoria TEXT,  -- 'chefe', 'mentor', 'pupilo'
    importancia TEXT,  -- 'baixa', 'media', 'alta', 'critica'
    frequencia_contato_ideal TEXT,  -- 'semanal', 'mensal'
    health_status TEXT,  -- 'excelente', 'bom', 'atencao', 'critico'
    aniversario DATE,
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pessoa_id UUID REFERENCES pessoas_chave(id),
    data TIMESTAMP,
    tipo TEXT,  -- 'reuniao_1_1', 'email', 'mensagem'
    resumo TEXT,
    topicos_discutidos TEXT[],
    sentimento TEXT,  -- 'positivo', 'neutro', 'negativo'
    proximos_passos TEXT[],
    criado_em TIMESTAMP DEFAULT NOW()
);
```

**Vector Storage (PgVector):**

```sql
-- Semantic Memory
CREATE TABLE memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    content TEXT,
    embedding vector(1536),  -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index para busca vetorial
CREATE INDEX memory_embeddings_vector_idx
ON memory_embeddings
USING ivfflat (embedding vector_cosine_ops);
```

Quer o schema de algum módulo específico em detalhe?
""",

            "como adicionar novo módulo": """
🔧 GUIA: COMO ADICIONAR NOVO MÓDULO (ADMIN ONLY)

**Passo 1: Estrutura de Diretórios**

```bash
backend/modules/
└── nome_modulo/
    ├── __init__.py
    ├── orchestrator.py      # Orquestrador do módulo
    ├── agents/              # Agentes especializados
    │   ├── __init__.py
    │   └── agente_principal.py
    ├── schemas.py           # Pydantic schemas
    ├── models.py            # SQLAlchemy models
    └── integration.py       # Integração com Event Bus
```

**Passo 2: Definir Schemas (Pydantic)**

```python
# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EntidadeCreate(BaseModel):
    campo1: str
    campo2: int
    campo3: Optional[str] = None

class EntidadeResponse(EntidadeCreate):
    id: str
    criado_em: datetime
```

**Passo 3: Criar Models (SQLAlchemy)**

```python
# models.py
from sqlalchemy import Column, String, Integer, TIMESTAMP
from backend.db.base import Base

class Entidade(Base):
    __tablename__ = "nome_tabela"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, nullable=False)
    campo1 = Column(String, nullable=False)
    campo2 = Column(Integer)
    criado_em = Column(TIMESTAMP, server_default="NOW()")
```

**Passo 4: Criar Agente Especializado**

```python
# agents/agente_principal.py
from phidata.agent import Agent
from phidata.models.openai import OpenAIChat

class AgenteModulo(Agent):
    def __init__(self, db_connection):
        super().__init__(
            name="NomeAgente",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você é especialista em X",
                "Seu objetivo é Y"
            ]
        )
        self.db = db_connection

    async def processar(self, input_data):
        # Lógica do agente
        pass
```

**Passo 5: Criar Integração com Event Bus**

```python
# integration.py
from backend.core.event_bus import event_bus, EventType, Event

class ModuloIntegration:
    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager

        # Subscreve eventos relevantes
        self.event_bus.subscribe(
            EventType.EVENTO_EXTERNO,
            self.on_evento_externo
        )

    async def on_evento_externo(self, event: Event):
        # Reage ao evento
        # ... processar ...

        # Publica novo evento se necessário
        await self.event_bus.publish(Event(
            tipo=EventType.NOVO_MODULO_EVENT,
            modulo_origem='nome_modulo',
            payload={...}
        ))
```

**Passo 6: Criar Orquestrador do Módulo**

```python
# orchestrator.py
from .agents.agente_principal import AgenteModulo
from .integration import ModuloIntegration

class ModuloOrchestrator:
    def __init__(self, db_connection, event_bus, context_manager):
        self.db = db_connection
        self.event_bus = event_bus
        self.context = context_manager

        # Inicializa agente
        self.agente = AgenteModulo(db_connection)

        # Inicializa integração
        self.integration = ModuloIntegration(
            db_connection,
            event_bus,
            context_manager
        )

    async def processar_request(self, input_data):
        return await self.agente.processar(input_data)
```

**Passo 7: Registrar no CharleeOrchestrator**

```python
# backend/orchestrator/charlee_orchestrator.py

from backend.modules.nome_modulo.orchestrator import ModuloOrchestrator

class CharleeOrchestrator(Agent):
    def __init__(self, ...):
        # ... existing code ...

        # Adiciona novo módulo
        self.nome_modulo = ModuloOrchestrator(
            db_connection,
            event_bus,
            context_manager
        )

        # Adiciona integração
        self.nome_modulo_integration = ModuloIntegration(
            db_connection,
            event_bus,
            context_manager
        )
```

**Passo 8: Criar Migration para BD**

```bash
# Criar nova migration
alembic revision -m "add_nome_modulo_tables"
```

```python
# migrations/versions/xxx_add_nome_modulo_tables.py
def upgrade():
    op.create_table(
        'nome_tabela',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('campo1', sa.String(), nullable=False),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('NOW()'))
    )

def downgrade():
    op.drop_table('nome_tabela')
```

**Passo 9: Adicionar API Endpoints**

```python
# backend/api/routes/nome_modulo.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/nome-modulo", tags=["nome-modulo"])

@router.post("/entidade")
async def criar_entidade(
    data: EntidadeCreate,
    user_id: int = Depends(get_current_user_id)
):
    # ... implementação ...
    pass
```

**Passo 10: Documentar**

Criar `docs/NOME_MODULO.md` seguindo template dos módulos existentes.

**Checklist Final:**

- [ ] Schemas Pydantic definidos
- [ ] Models SQLAlchemy criados
- [ ] Migration do BD executada
- [ ] Agente especializado implementado
- [ ] Integração com Event Bus configurada
- [ ] Orquestrador do módulo criado
- [ ] Registrado no CharleeOrchestrator
- [ ] API endpoints criados
- [ ] Testes unitários escritos
- [ ] Documentação completa
- [ ] Event types adicionados ao EventType enum

Precisa de ajuda em algum passo específico?
"""
        }

        return admin_explanations.get(
            question.lower(),
            "Pergunta admin não encontrada. Perguntas disponíveis: " +
            ", ".join(admin_explanations.keys())
        )

    def get_current_state(self) -> dict:
        """Retorna estado atual completo do sistema (ADMIN ONLY)"""

        if self.access_level != AccessLevel.ADMIN:
            return {"error": "Unauthorized. Admin access required."}

        return {
            "version": "V3.3",
            "modules": {
                "implemented": [
                    "Task Manager (V1)",
                    "BigRocks (V1)",
                    "Cycle Tracking (V1)",
                    "Capacity Guardian (V2)",
                    "Focus Module (V2)",
                    "OKR Dashboard (V2)",
                    "Projects Module (V2)",
                    "Calendar Integration (V3.2)",
                    "Multimodal Input (V3.3)"
                ],
                "documented": [
                    "Charlee Wealth (V4 - planned)",
                    "Charlee Routines (V4 - planned)",
                    "Charlee Wardrobe (V4 - planned)",
                    "Charlee Diplomat (V4 - planned)"
                ]
            },
            "database": {
                "provider": "PostgreSQL 15",
                "extensions": ["pgvector"],
                "total_tables": 25  # aproximado
            },
            "api": {
                "version": "v1",
                "endpoints": 40,  # aproximado
                "authentication": "JWT"
            },
            "integrations": {
                "google_calendar": "active",
                "microsoft_calendar": "active"
            },
            "event_bus": {
                "total_event_types": 40,  # aproximado incluindo V4+
                "active_subscriptions": 20  # aproximado
            }
        }
```

---

### 🎓 Exemplos de Uso

**Exemplo 1: Usuário Descobrindo Feature**

```
Usuário: "Gasto muito tempo pensando no que vestir de manhã"

Charlee (detecta padrão):
👔 Percebi que você menciona isso frequentemente!

Eu tenho um recurso que pode ajudar: **Planejamento Semanal de Outfits**

Como funciona:
• Você cadastra suas roupas uma vez (posso usar foto!)
• Todo domingo, eu monto 7 outfits para a semana
• Considera seu calendário (reunião = outfit profissional)
• Considera sua fase do ciclo (TPM = conforto máximo)

Economia: ~15min/dia = 1h45min/semana

Quer que eu te mostre como configurar?
```

**Exemplo 2: Admin Consultando Arquitetura (ADMIN ONLY)**

```
Admin (Samara): "Charlee, explique a arquitetura completa"

Charlee:
🏗️ ARQUITETURA COMPLETA DO CHARLEE

[Retorna explicação técnica detalhada conforme código acima]

Admin: "Como adiciono um novo módulo?"

Charlee:
🔧 GUIA: COMO ADICIONAR NOVO MÓDULO

[Retorna guia passo-a-passo completo]
```

**Exemplo 3: Charlee Sendo Proativa**

```
Charlee (detecta que usuário criou 3 tarefas similares em 3 semanas):

💡 SUGESTÃO PROATIVA

Percebi que você cria estas tarefas toda semana:
• "Enviar relatório semanal para chefe"
• "Atualizar planilha de horas"
• "Revisar PRs da equipe"

Posso automatizar isso com uma **Rotina Semanal**?

Ao invés de criar manualmente toda semana, você define UMA VEZ
e eu crio as tarefas automaticamente toda sexta-feira.

Quer experimentar? [Sim] [Agora não] [Não me mostre de novo]
```

---

### 🔒 Segurança e Privacidade

**Regras de Acesso:**

```python
# Informações que NUNCA devem vazar para USER
RESTRICTED_ADMIN_INFO = [
    "Database credentials",
    "API keys e secrets",
    "Internal system architecture details",
    "Event Bus internals",
    "Security mechanisms implementation",
    "Admin-only commands",
    "System debugging information"
]

# Informações seguras para USER
SAFE_USER_INFO = [
    "Feature tutorials",
    "How-to guides",
    "Benefits and use cases",
    "High-level architecture (without implementation details)",
    "Feature discovery suggestions"
]
```

**Validação de Acesso:**

```python
def can_access_info(user_id: int, info_type: str) -> bool:
    """Valida se usuário pode acessar informação"""

    user_role = db.execute("""
        SELECT role FROM users WHERE id = %s
    """, (user_id,)).fetchone()['role']

    if info_type in RESTRICTED_ADMIN_INFO:
        return user_role == 'admin'

    return True  # Informações USER são públicas
```

---

**Status**: 📋 Auto-Conhecimento Documentado
**Acesso**: USER (tutoriais) + ADMIN (arquitetura completa)
**Objetivo**: Charlee consciente de si mesmo para ensinar usuários e auxiliar desenvolvimento