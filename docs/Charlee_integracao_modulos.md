# 🔗 Integração Completa dos Módulos Charlee

## 19. Arquitetura de Integração

### 19.1 Visão Geral da Integração

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHARLEE CORE (Orquestrador)                  │
│              Agente Central que coordena tudo                   │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┼────────┬──────────┬──────────┬───────────┐
    │        │        │          │          │           │
    ▼        ▼        ▼          ▼          ▼           ▼
┌────────┐┌────────┐┌─────────┐┌─────────┐┌──────────┐┌─────────┐
│ Task   ││Wellness││Capacity ││  OKR    ││  Focus   ││Projects │
│Manager ││ Coach  ││Guardian ││Dashboard││  Module  ││ Module  │
└────┬───┘└───┬────┘└────┬────┘└────┬────┘└────┬─────┘└────┬────┘
     │        │          │          │          │           │
     └────────┴──────────┴──────────┴──────────┴───────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  SHARED MEMORY   │  │  EVENT BUS       │
          │  (Vector DB)     │  │  (Pub/Sub)       │
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

## 19.9 Orquestrador Central Integrado

```python
class CharleeOrchestrator(Agent):
    """Agente Central que coordena todos os módulos"""
    
    def __init__(self, db_connection, vector_db, event_bus, context_manager):
        self.db = db_connection
        self.vector_db = vector_db
        self.event_bus = event_bus
        self.context = context_manager
        
        # Inicializa módulos especializados
        self.wellness_coach = WellnessCoachAgent(db_connection)
        self.capacity_guardian = CapacityGuardianAgent(db_connection)
        self.focus_guard = FocusGuardAgent(db_connection)
        self.okr_dashboard = OKRDashboardAgent(db_connection)
        self.projects_orchestrator = ProjectsOrchestrator(db_connection, event_bus)
        
        # Inicializa integrações
        self.task_project_integration = TaskProjectIntegration(
            db_connection, event_bus, context_manager
        )
        self.focus_capacity_integration = FocusCapacityIntegration(
            db_connection, event_bus, context_manager
        )
        self.wellness_projects_integration = WellnessProjectsIntegration(
            db_connection, event_bus, self.wellness_coach
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

⚡ FOCO DO DIA
{self.get_daily_focus()}

📊 OKRS
{self.okr_dashboard.generate_okr_report()}

💼 PROJETOS FREELANCE
{self.projects_orchestrator.get_project_summary()}

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

**Próximos passos:**

Quer que eu gere agora:

1. ✅ **Docker Compose completo** (todos os serviços)
2. ✅ **Script de setup inicial** (one-command install)
3. ✅ **Testes de integração** (end-to-end)
4. ✅ **Dashboard web** (Streamlit) mostrando tudo
5. ✅ **Guia de deploy** (local + cloud)

**Ou começamos a implementar?** 🚀