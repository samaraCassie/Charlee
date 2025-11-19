# 📋 Charlee Routines - Sistema de Roteiros Detalhados

> **Versão**: 1.0 (Planejamento)
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V4.x - Detailed Routines & Decision Automation

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Filosofia: Bullet Journal Automatizado](#filosofia-bullet-journal-automatizado)
3. [Arquitetura](#arquitetura)
4. [Agentes Especializados](#agentes-especializados)
5. [Modelos de Dados](#modelos-de-dados)
6. [Fluxos de Trabalho](#fluxos-de-trabalho)
7. [API Endpoints](#api-endpoints)
8. [Integrações](#integrações)
9. [Casos de Uso](#casos-de-uso)
10. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

O **Charlee Routines** é um sistema de automação de decisões logísticas que combate diretamente a **Sobrecarga Cognitiva** e a **Fadiga de Decisão**, transformando o Charlee em um verdadeiro "segundo cérebro" para gestão do dia a dia.

### O Problema: Economia de Tokens Mentais

```
Capacidade Mental = Recursos Finitos ("Tokens Mentais")
```

Cada micro-decisão consome "tokens" mentais:
- ❓ "Que roupa usar?"
- ❓ "O que comer no café da manhã?"
- ❓ "Quanto tempo vai levar preparar a marmita?"
- ❓ "O que fazer agora?"

**Resultado**: Ao final do dia, mesmo sem trabalho de alto esforço, a exaustão mental se instala, prejudicando a performance em tarefas críticas (trabalho, estudos) que exigem foco profundo.

### A Solução: Roteiros Detalhados

**Antecipar e automatizar** o máximo de decisões logísticas e de baixo valor.

```
┌─────────────────────────────────────────────────────┐
│         ECONOMIA DE TOKENS MENTAIS                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  SEM Charlee Routines:                             │
│  ❌ 50+ micro-decisões/dia                         │
│  ❌ Fadiga mental às 14h                           │
│  ❌ Procrastinação por sobrecarga                  │
│                                                     │
│  COM Charlee Routines:                             │
│  ✅ 5-10 decisões estratégicas/dia                 │
│  ✅ Energia mental preservada                      │
│  ✅ Execução no piloto automático                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Características Principais

1. **⏰ Roteiro Minuto a Minuto**: Plano detalhado pré-gerado
2. **🧠 Gestão Dinâmica**: Recalcula em tempo real diante de imprevistos
3. **📊 Aprendizado de Padrões**: Melhora estimativas baseado em histórico
4. **🌸 Context-Aware**: Ajusta densidade baseado em energia/ciclo
5. **👔 Decisões Antecipadas**: Look, refeições, ordem de tarefas

---

## 📖 Filosofia: Bullet Journal Automatizado

O Charlee Routines adota os princípios do método **Bullet Journal (BuJo)** e os automatiza para eliminar a fadiga de decisão.

### 1. Captura Rápida (Rapid Logging)

```
┌─────────────────────────────────────────────────────┐
│  BuJo Manual:                                       │
│  ✏️ Anota tarefas (•), eventos (○), notas (-)     │
│                                                     │
│  Charlee (Automático):                             │
│  🎤 CLI: $ charlee add-task "Preparar marmita"    │
│  🎙️ Voz: "Charlee, adicionar tarefa..."          │
│  📧 Email: Captura automática de compromissos     │
│                                                     │
│  ✅ Captura digital + integração imediata ao DB    │
└─────────────────────────────────────────────────────┘
```

### 2. Organização (Collections)

```
┌─────────────────────────────────────────────────────┐
│  BuJo Manual:                                       │
│  📓 Coleções manuais: "Metas", "Rotina", "Projetos"│
│                                                     │
│  Charlee (Automático):                             │
│  📊 big_rocks - Pilares de vida                    │
│  🎯 okrs - Metas estruturadas                      │
│  📋 rotina_templates - Roteiros reutilizáveis      │
│  👔 plano_semanal_looks - Decisões de vestuário    │
│                                                     │
│  ✅ Coleções inteligentes no banco de dados        │
└─────────────────────────────────────────────────────┘
```

### 3. Revisão e Migração (A Grande Inovação)

**O núcleo do BuJo - mas automatizado!**

```
┌─────────────────────────────────────────────────────┐
│  BuJo Manual:                                       │
│  🔄 Fim do dia: revisar tarefas manualmente        │
│  📝 Decidir o que migrar, cancelar ou reagendar    │
│  😫 GASTA TOKENS MENTAIS na revisão                │
│                                                     │
│  Charlee (Automático):                             │
│  🤖 Capacity Guardian faz revisão proativa         │
│  🧠 Aprende padrões e avisa ANTES de errar         │
│  ⚡ Força decisões de trade-off em tempo real      │
│  🎯 Você apenas EXECUTA, não revisa               │
│                                                     │
│  ✅ Transforma revisão passiva em gestão ativa     │
└─────────────────────────────────────────────────────┘
```

### O Diferencial

> **BuJo tradicional**: Registra o que aconteceu (reativo)
>
> **Charlee Routines**: Sistema de execução ativo que usa princípios do BuJo para **proteger foco e energia** (proativo)

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────┐
│              CHARLEE ROUTINES SYSTEM                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   1. INPUT LAYER (Data Sources)             │   │
│  │  • rotina_templates (DB)                    │   │
│  │  • tarefas (Tasks)                          │   │
│  │  • Google Calendar (eventos)                │   │
│  │  • plano_semanal_looks (Wardrobe)           │   │
│  │  • Wellness status (ciclo/energia)          │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   2. ORCHESTRATION LAYER (Agents)           │   │
│  │  • Routine Manager (Geração de roteiro)     │   │
│  │  • Wardrobe Manager (Decisão de look)       │   │
│  │  • Capacity Guardian (Proteção + Aprendizado)│  │
│  │  • Wellness Coach (Contexto de energia)     │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   3. OUTPUT LAYER (Execution)               │   │
│  │  • Morning Briefing (roteiro do dia)        │   │
│  │  • Real-time recalculation (imprevistos)    │   │
│  │  • Trade-off decisions (ajustes dinâmicos)  │   │
│  │  • Pattern learning (melhoria contínua)     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Fluxo de Geração de Roteiro

```
04:00 (ou ao acordar)
         ↓
┌─────────────────────────────────────────────────────┐
│  Charlee Orchestrator inicia morning_briefing()     │
└────────────────────┬────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
┌─────────────────┐      ┌─────────────────┐
│ Routine Manager │      │ Wardrobe Manager│
│ busca template  │      │ busca look      │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └────────┬───────────────┘
                  ↓
         ┌────────────────┐
         │ Wellness Coach │
         │ (energia/ciclo)│
         └────────┬───────┘
                  ↓
         ┌────────────────┐
         │ Google Calendar│
         │ (eventos)      │
         └────────┬───────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  Charlee sintetiza tudo → Morning Briefing Completo │
└─────────────────────────────────────────────────────┘
```

---

## 🤖 Agentes Especializados

### 1. Routine Manager (Novo Agente)

**Responsabilidade**: Gerar e exibir o roteiro diário minuto a minuto.

#### Lógica de Operação

```python
class RoutineManager:
    """
    Agente responsável pela geração de roteiros detalhados.
    """

    async def generate_daily_routine(
        self,
        user_id: int,
        date: datetime
    ) -> DailyRoutine:
        """
        Gera roteiro completo para um dia específico.

        Steps:
        1. Busca rotina_template apropriado (ex: "Rotina Manhã Faculdade")
        2. Busca tarefas agendadas para o dia
        3. Busca eventos do Google Calendar
        4. Busca look planejado (Wardrobe Manager)
        5. Consulta status de energia (Wellness Coach)
        6. Ajusta tempos baseado em energia
        7. Adiciona buffers de imprevisto
        8. Retorna roteiro minuto a minuto
        """
        # 1. Busca template base
        template = await self._get_routine_template(user_id, date)

        # 2. Busca compromissos
        tasks = await tasks_service.get_tasks_for_day(user_id, date)
        calendar_events = await calendar_service.get_events(user_id, date)

        # 3. Busca decisões antecipadas
        outfit = await wardrobe_manager.get_planned_outfit(user_id, date)

        # 4. Consulta contexto de energia
        wellness = await wellness_coach.get_energy_level(user_id, date)

        # 5. Aplica ajustes baseados em energia
        adjusted_template = self._adjust_for_energy(template, wellness)

        # 6. Monta roteiro integrado
        routine = self._build_routine(
            adjusted_template,
            tasks,
            calendar_events,
            outfit
        )

        return routine

    def _adjust_for_energy(
        self,
        template: RoutineTemplate,
        wellness: WellnessStatus
    ) -> RoutineTemplate:
        """
        Ajusta duração de passos baseado em energia disponível.

        Exemplos:
        - Fase Menstrual (60% energia): +20% tempo, +10min buffer
        - Fase Folicular (120% energia): -10% tempo
        - Sono ruim (<6h): +15% tempo
        """
        energy_multiplier = wellness.energy_percentage / 100

        adjusted_steps = []
        for step in template.steps:
            # Ajusta duração baseado em energia
            adjusted_duration = step.duration_min / energy_multiplier

            # Arredonda para múltiplos de 5 minutos
            adjusted_duration = round(adjusted_duration / 5) * 5

            adjusted_steps.append(
                RoutineStep(
                    name=step.name,
                    duration_min=adjusted_duration,
                    original_duration=step.duration_min
                )
            )

        # Adiciona buffer extra em dias de baixa energia
        if wellness.energy_percentage < 70:
            buffer_extra = 10  # minutos
            adjusted_steps.append(
                RoutineStep(
                    name="Buffer Extra (Baixa Energia)",
                    duration_min=buffer_extra
                )
            )

        return RoutineTemplate(steps=adjusted_steps)

    def _build_routine(
        self,
        template: RoutineTemplate,
        tasks: List[Task],
        events: List[CalendarEvent],
        outfit: PlannedOutfit
    ) -> DailyRoutine:
        """
        Constrói roteiro final integrando todas as fontes.
        """
        routine_blocks = []
        current_time = datetime.now().replace(hour=5, minute=0)  # Começa às 5h

        # 1. Bloco da rotina matinal
        morning_block = RoutineBlock(
            title="Rotina Matinal",
            start_time=current_time,
            steps=template.steps,
            outfit=outfit
        )
        routine_blocks.append(morning_block)

        # Atualiza hora atual
        current_time += timedelta(minutes=template.total_duration)

        # 2. Blocos de compromissos fixos (Calendar)
        for event in events:
            routine_blocks.append(
                RoutineBlock(
                    title=event.title,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    type="calendar_event"
                )
            )

        # 3. Blocos de tarefas (com tempo estimado)
        for task in tasks:
            routine_blocks.append(
                RoutineBlock(
                    title=task.title,
                    start_time=current_time,
                    duration_min=task.estimated_hours * 60,
                    type="task"
                )
            )
            current_time += timedelta(minutes=task.estimated_hours * 60)

        # 4. Ordena tudo cronologicamente
        routine_blocks.sort(key=lambda b: b.start_time)

        return DailyRoutine(
            date=date,
            blocks=routine_blocks,
            total_planned_minutes=sum([b.duration_min for b in routine_blocks])
        )
```

#### Formatação do Output

```python
def format_morning_briefing(routine: DailyRoutine, wellness: WellnessStatus) -> str:
    """
    Formata o roteiro para exibição no terminal.
    """
    output = [
        "☀️ BOM DIA, SAMARA!\n",
        "🌸 Status de Bem-Estar:",
        f"Você está na {wellness.cycle_phase} (Dia {wellness.cycle_day}).",
        f"Energia esperada: {wellness.energy_level} ({wellness.energy_percentage}%).",
        f"Adicionei {wellness.buffer_minutes}min de buffer ao seu roteiro.\n",
    ]

    # Look do dia
    if routine.outfit:
        output.extend([
            "👔 Seu Look de Hoje (Pré-definido):",
            f"• {routine.outfit.name}",
            f"• ({routine.outfit.items_summary})\n"
        ])

    # Roteiro detalhado
    output.append("🎯 Roteiro Detalhado (Manhã):")

    for block in routine.blocks:
        if block.type == "morning_routine":
            current_time = block.start_time
            for step in block.steps:
                output.append(
                    f"{current_time.strftime('%H:%M')} | {step.name}"
                )
                current_time += timedelta(minutes=step.duration_min)

    # Foco principal
    output.extend([
        "\n🔥 Foco Principal Hoje:",
        *[f"• {task.title}" for task in routine.priority_tasks]
    ])

    return "\n".join(output)
```

---

### 2. Wardrobe Manager (Novo Agente)

**Responsabilidade**: Eliminar a decisão "o que vestir".

#### Lógica de Planejamento

```python
class WardrobeManager:
    """
    Agente que planeja looks semanais com antecedência.
    """

    async def plan_weekly_outfits(
        self,
        user_id: int,
        week_start: datetime
    ) -> List[PlannedOutfit]:
        """
        Planeja todos os looks da semana de uma vez.

        Considera:
        - Calendário (compromissos profissionais vs casuais)
        - Clima (API de previsão)
        - Fase do ciclo (conforto vs estilo)
        - Regras de estilo (cores, estampas)
        - Últimos looks usados (evitar repetição)
        """
        outfits = []

        for day in range(7):
            date = week_start + timedelta(days=day)

            # 1. Contexto do dia
            events = await calendar_service.get_events(user_id, date)
            weather = await weather_api.get_forecast(date)
            cycle_phase = await wellness_coach.get_cycle_phase(user_id, date)

            # 2. Determina ocasião (casual, profissional, esporte)
            occasion = self._determine_occasion(events)

            # 3. Filtra roupas compatíveis
            available_clothes = await self._get_available_clothes(
                user_id=user_id,
                occasion=occasion,
                weather=weather,
                cycle_phase=cycle_phase
            )

            # 4. Aplica regras de estilo
            valid_combinations = self._apply_style_rules(available_clothes)

            # 5. Evita repetição recente
            recent_outfits = await self._get_recent_outfits(user_id, days=7)
            valid_combinations = self._filter_recent(
                valid_combinations,
                recent_outfits
            )

            # 6. Seleciona melhor combinação (via LLM)
            outfit = await self._select_best_outfit(
                valid_combinations,
                context={
                    "occasion": occasion,
                    "weather": weather,
                    "cycle_phase": cycle_phase
                }
            )

            outfits.append(outfit)

        # 7. Salva plano semanal
        await self._save_weekly_plan(user_id, week_start, outfits)

        return outfits

    async def _select_best_outfit(
        self,
        combinations: List[OutfitCombination],
        context: dict
    ) -> PlannedOutfit:
        """
        Usa LLM para escolher a melhor combinação.
        """
        prompt = f"""
        Você é um personal stylist. Escolha o melhor look para este contexto:

        Ocasião: {context['occasion']}
        Clima: {context['weather'].temperature}°C, {context['weather'].condition}
        Fase do ciclo: {context['cycle_phase']} (priorizar conforto)

        Combinações disponíveis:
        {self._format_combinations(combinations)}

        Retorne o número da combinação escolhida e justifique.
        """

        response = await self.llm.process(prompt)

        selected = combinations[response.choice_index]

        return PlannedOutfit(
            date=context['date'],
            combination=selected,
            reasoning=response.justification
        )
```

---

### 3. Capacity Guardian (Agente Existente - Expandido)

**Responsabilidades Adicionais**:
1. **Proteção de Estimativa**: Avisa quando estimativas são otimistas
2. **Gestão de Imprevistos**: Recalcula roteiro em tempo real
3. **Aprendizado de Padrões**: Melhora estimativas futuras

#### Proteção de Estimativa

```python
class CapacityGuardian:
    """
    Agente que protege a integridade do roteiro.
    """

    async def validate_task_estimation(
        self,
        user_id: int,
        task: TaskCreate
    ) -> EstimationWarning:
        """
        Valida se a estimativa de tempo é realista baseado em histórico.
        """
        # 1. Busca padrões históricos
        patterns = await self._get_historical_patterns(
            user_id=user_id,
            task_tags=task.tags,
            task_type=task.type
        )

        if not patterns or patterns.total_samples < 5:
            # Não há dados suficientes
            return EstimationWarning(
                is_valid=True,
                message="Sem histórico suficiente para validar."
            )

        # 2. Compara estimativa com média histórica
        user_estimate = task.estimated_hours * 60  # minutos
        historical_avg = patterns.actual_avg_minutes

        deviation = (historical_avg - user_estimate) / historical_avg

        # 3. Se a diferença for > 20%, avisa
        if deviation > 0.2:
            return EstimationWarning(
                is_valid=False,
                user_estimate=user_estimate,
                historical_avg=historical_avg,
                message=(
                    f"🧠 **Posso fazer uma observação?**\n"
                    f"Notei que tarefas como '{task.title}' costumam levar "
                    f"em média **{historical_avg:.0f} minutos**, não {user_estimate:.0f}.\n"
                    f"Você prefere que eu já aloque **{historical_avg:.0f} minutos**?\n"
                    f"Isso garantirá que seu roteiro não seja comprometido."
                ),
                suggested_estimate=historical_avg,
                confidence=patterns.confidence
            )

        return EstimationWarning(is_valid=True)

    async def _get_historical_patterns(
        self,
        user_id: int,
        task_tags: List[str],
        task_type: str
    ) -> HistoricalPattern:
        """
        Analisa tarefas similares completadas no passado.
        """
        # Busca tarefas similares (por tags)
        similar_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "completed",
            Task.tags.overlap(task_tags)  # PostgreSQL array overlap
        ).all()

        if len(similar_tasks) < 5:
            return None

        # Calcula médias
        estimates = [t.estimated_hours * 60 for t in similar_tasks]
        actuals = [t.actual_duration_minutes for t in similar_tasks]

        return HistoricalPattern(
            total_samples=len(similar_tasks),
            estimated_avg=statistics.mean(estimates),
            actual_avg_minutes=statistics.mean(actuals),
            deviation_pattern=(
                "subestima" if statistics.mean(actuals) > statistics.mean(estimates)
                else "superestima"
            ),
            confidence=min(len(similar_tasks) / 10, 1.0)  # Max confidence at 10 samples
        )
```

#### Gestão de Imprevistos

```python
async def handle_interruption(
    self,
    user_id: int,
    interruption: Interruption
) -> RecalculationResult:
    """
    Recalcula roteiro quando ocorre um imprevisto.

    Exemplo:
    Usuário: "Charlee, não encontro o microfone, preciso procurar!"
    """
    # 1. Pausa roteiro atual
    current_routine = await self._get_active_routine(user_id)
    current_step = current_routine.current_step

    await self._pause_routine(current_routine.id)

    # 2. Inicia cronômetro do imprevisto
    interruption_timer = Timer(
        task_name=interruption.description,
        started_at=datetime.now()
    )

    # 3. Calcula impacto
    buffer_remaining = current_routine.buffer_remaining_minutes
    next_hard_deadline = current_routine.next_hard_deadline  # ex: "Sair para faculdade 07:05"

    # 4. Envia alerta proativo
    alert = ProactiveAlert(
        title="🚨 Alerta de Recálculo",
        message=(
            f"Entendido! Um imprevisto.\n"
            f"Pausei seu roteiro atual ('{current_step.name}' às {current_step.start_time}).\n"
            f"Vou iniciar um cronômetro para '{interruption.description}'.\n\n"
            f"⚠️ Seu tempo de '{next_hard_deadline.name}' é às {next_hard_deadline.time}.\n"
            f"Você tem **{buffer_remaining} minutos** de buffer restantes.\n"
            f"Se demorar mais que isso, você se atrasará."
        )
    )

    await notification_service.send(alert)

    # 5. Quando o usuário resolver (via voz: "Charlee, achei!")
    # O método handle_interruption_resolved() é chamado

    return RecalculationResult(
        interruption_timer=interruption_timer,
        buffer_remaining=buffer_remaining,
        next_deadline=next_hard_deadline
    )

async def handle_interruption_resolved(
    self,
    user_id: int,
    interruption_timer: Timer
) -> TradeOffDecision:
    """
    Quando imprevisto é resolvido, força decisão de trade-off.
    """
    # 1. Para cronômetro
    interruption_timer.stop()
    time_spent = interruption_timer.duration_minutes

    # 2. Busca roteiro
    routine = await self._get_active_routine(user_id)

    # 3. Calcula atraso
    buffer_remaining = routine.buffer_remaining_minutes
    delay = max(0, time_spent - buffer_remaining)

    if delay == 0:
        # Sem atraso, apenas retoma roteiro
        await self._resume_routine(routine.id)
        return TradeOffDecision(no_action_needed=True)

    # 4. Gera opções de trade-off
    options = self._generate_tradeoff_options(routine, delay)

    # 5. Força decisão do usuário
    decision = TradeOffDecision(
        delay_minutes=delay,
        message=(
            f"Ok. Você gastou {time_spent} minutos "
            f"({delay} min além do seu buffer).\n\n"
            f"⚖️ **Decisão de Trade-Off Necessária:**\n"
            f"Você está {delay} minutos atrasada. "
            f"Para sair às {routine.next_deadline.time}, você precisa:"
        ),
        options=options
    )

    await notification_service.send_decision_request(decision)

    return decision

def _generate_tradeoff_options(
    self,
    routine: DailyRoutine,
    delay_minutes: int
) -> List[TradeOffOption]:
    """
    Gera opções de ajuste para compensar atraso.
    """
    options = []

    # Busca passos que podem ser pulados/reduzidos
    remaining_steps = [
        s for s in routine.steps
        if s.start_time > datetime.now()
    ]

    for step in remaining_steps:
        # Opção 1: Pular passo completamente
        if step.duration_min >= delay_minutes and step.optional:
            options.append(TradeOffOption(
                id=1,
                action="skip",
                step=step.name,
                time_saved=step.duration_min,
                description=f"Pular '{step.name}' ({step.duration_min} min)"
            ))

        # Opção 2: Reduzir duração do passo
        if step.duration_min > 10:
            reduction = min(delay_minutes, step.duration_min - 5)
            options.append(TradeOffOption(
                id=2,
                action="reduce",
                step=step.name,
                time_saved=reduction,
                description=(
                    f"Reduzir '{step.name}' de {step.duration_min} "
                    f"para {step.duration_min - reduction} min"
                )
            ))

    # Opção final: aceitar atraso
    options.append(TradeOffOption(
        id=len(options) + 1,
        action="accept_delay",
        time_saved=0,
        description=f"Sair {delay_minutes} minutos atrasada"
    ))

    return options
```

---

### 4. Wellness Coach (Agente Existente - Interface)

**Responsabilidade**: Fornecer contexto sobre nível de energia.

```python
class WellnessCoach:
    """
    Agente que fornece contexto de bem-estar para ajustar roteiros.
    """

    async def get_energy_context(
        self,
        user_id: int,
        date: datetime
    ) -> EnergyContext:
        """
        Retorna contexto completo de energia para um dia.
        """
        # 1. Fase do ciclo
        cycle_info = await self._get_cycle_phase(user_id, date)

        # 2. Qualidade do sono (da noite anterior)
        sleep_quality = await self._get_sleep_quality(user_id, date - timedelta(days=1))

        # 3. Nível de energia esperado
        base_energy = self._calculate_base_energy(cycle_info)
        sleep_adjustment = self._calculate_sleep_adjustment(sleep_quality)

        energy_percentage = base_energy * sleep_adjustment

        # 4. Buffer recomendado
        buffer_minutes = self._calculate_buffer(energy_percentage)

        return EnergyContext(
            cycle_phase=cycle_info.phase,
            cycle_day=cycle_info.day,
            energy_level=self._energy_level_label(energy_percentage),
            energy_percentage=energy_percentage,
            buffer_minutes=buffer_minutes,
            recommendations=self._generate_recommendations(
                cycle_info,
                sleep_quality,
                energy_percentage
            )
        )

    def _calculate_base_energy(self, cycle_info: CycleInfo) -> float:
        """
        Energia base por fase do ciclo.
        """
        energy_map = {
            "menstrual": 0.60,    # 60% (baixa energia)
            "folicular": 1.20,    # 120% (alta energia)
            "ovulatoria": 1.30,   # 130% (pico)
            "lutea": 0.80,        # 80% (média-baixa)
        }

        return energy_map.get(cycle_info.phase, 1.0)

    def _calculate_sleep_adjustment(self, sleep: SleepQuality) -> float:
        """
        Ajuste baseado em qualidade do sono.
        """
        if sleep.hours >= 8:
            return 1.05  # +5%
        elif sleep.hours >= 7:
            return 1.0   # normal
        elif sleep.hours >= 6:
            return 0.90  # -10%
        else:
            return 0.75  # -25%

    def _calculate_buffer(self, energy_percentage: float) -> int:
        """
        Calcula buffer extra baseado em energia.
        """
        if energy_percentage < 70:
            return 20  # 20 minutos extras
        elif energy_percentage < 90:
            return 10  # 10 minutos extras
        else:
            return 5   # buffer mínimo
```

---

## 📊 Modelos de Dados

### Schema PostgreSQL

```sql
-- ========================================
-- Tabela: rotina_templates
-- ========================================
CREATE TABLE rotina_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    nome_template TEXT NOT NULL,  -- Ex: "Rotina Manhã (Faculdade)"
    descricao TEXT,
    tipo TEXT,  -- Ex: "manha", "noite", "pre_trabalho"

    -- Passos do roteiro (JSONB)
    passos JSONB NOT NULL,
    -- Estrutura:
    -- [
    --   {"passo": "Levantar", "duracao_min": 2, "opcional": false},
    --   {"passo": "Chapinha", "duracao_min": 20, "opcional": true}
    -- ]

    -- Metadados
    duracao_total_min INTEGER,  -- Calculado automaticamente
    buffer_padrao_min INTEGER DEFAULT 10,

    -- Condições de uso
    dias_semana TEXT[],  -- Ex: ['seg', 'ter', 'qua']
    ativo BOOLEAN DEFAULT TRUE,

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_rotina_templates_user ON rotina_templates(user_id);
CREATE INDEX idx_rotina_templates_tipo ON rotina_templates(tipo);


-- ========================================
-- Tabela: roteiros_diarios
-- ========================================
CREATE TABLE roteiros_diarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Data
    data DATE NOT NULL,

    -- Template usado
    template_id UUID REFERENCES rotina_templates(id),

    -- Roteiro gerado (JSONB)
    roteiro JSONB NOT NULL,
    -- Estrutura:
    -- {
    --   "blocos": [
    --     {
    --       "tipo": "morning_routine",
    --       "titulo": "Rotina Matinal",
    --       "inicio": "05:00",
    --       "passos": [...],
    --       "look": {...}
    --     },
    --     {
    --       "tipo": "calendar_event",
    --       "titulo": "Faculdade",
    --       "inicio": "07:30",
    --       "fim": "12:00"
    --     },
    --     {
    --       "tipo": "task",
    --       "titulo": "Documentar Módulo X",
    --       "inicio": "14:00",
    --       "duracao_min": 90
    --     }
    --   ],
    --   "total_planejado_min": 600
    -- }

    -- Contexto de energia
    energia_percentual NUMERIC(5, 2),  -- Ex: 80.00
    fase_ciclo TEXT,
    buffer_adicionado_min INTEGER,

    -- Status de execução
    status TEXT DEFAULT 'pendente',  -- pendente, em_andamento, completo, interrompido
    passo_atual TEXT,
    pausado_em TIMESTAMP,

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    iniciado_em TIMESTAMP,
    finalizado_em TIMESTAMP
);

-- Índices
CREATE INDEX idx_roteiros_diarios_user_data ON roteiros_diarios(user_id, data);
CREATE INDEX idx_roteiros_diarios_status ON roteiros_diarios(status);


-- ========================================
-- Tabela: interrupcoes
-- ========================================
CREATE TABLE interrupcoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Relacionamento
    roteiro_id UUID REFERENCES roteiros_diarios(id),

    -- Detalhes da interrupção
    descricao TEXT NOT NULL,  -- Ex: "Procurar microfone"

    -- Tempo
    inicio TIMESTAMP NOT NULL,
    fim TIMESTAMP,
    duracao_min INTEGER,  -- Calculado ao finalizar

    -- Impacto
    buffer_disponivel_min INTEGER,  -- Buffer antes da interrupção
    atraso_causado_min INTEGER,     -- Tempo além do buffer

    -- Decisão tomada (JSONB)
    tradeoff_escolhido JSONB,
    -- Estrutura:
    -- {
    --   "acao": "skip|reduce|accept_delay",
    --   "passo_afetado": "Pelinhos",
    --   "tempo_economizado": 5
    -- }

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_interrupcoes_roteiro ON interrupcoes(roteiro_id);


-- ========================================
-- Tabela: padroes_estimativa
-- ========================================
CREATE TABLE padroes_estimativa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação do padrão
    categoria TEXT NOT NULL,  -- Ex: "cozinha", "preparacao_aula"
    tags TEXT[],

    -- Estatísticas
    total_amostras INTEGER DEFAULT 0,
    estimativa_media_min NUMERIC(10, 2),
    real_media_min NUMERIC(10, 2),
    desvio_padrao NUMERIC(10, 2),

    -- Padrão identificado
    tendencia TEXT,  -- "subestima" | "superestima" | "acurado"
    percentual_desvio NUMERIC(5, 2),  -- Ex: -13.5 (subestima 13.5%)

    -- Confiança
    confianca NUMERIC(3, 2),  -- 0.0 a 1.0

    -- Timestamps
    ultima_analise TIMESTAMP DEFAULT NOW(),
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_padroes_estimativa_user ON padroes_estimativa(user_id);
CREATE INDEX idx_padroes_estimativa_categoria ON padroes_estimativa(categoria);


-- ========================================
-- Tabela: roupas (Wardrobe Manager)
-- ========================================
CREATE TABLE roupas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,  -- Ex: "camiseta", "calca", "tenis"
    cor_principal TEXT,
    cor_secundaria TEXT,
    estampa TEXT,  -- "lisa", "estampada", "listrada"

    -- Ocasiões
    ocasioes TEXT[],  -- Ex: ['casual', 'profissional', 'esporte']

    -- Clima
    temperatura_min NUMERIC(5, 2),  -- Ex: 15.0 (°C)
    temperatura_max NUMERIC(5, 2),  -- Ex: 30.0 (°C)

    -- Status
    limpa BOOLEAN DEFAULT TRUE,
    disponivel BOOLEAN DEFAULT TRUE,

    -- Metadados
    foto_url TEXT,
    tags TEXT[],

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_roupas_user ON roupas(user_id);
CREATE INDEX idx_roupas_categoria ON roupas(categoria);


-- ========================================
-- Tabela: plano_semanal_looks
-- ========================================
CREATE TABLE plano_semanal_looks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Semana
    semana_inicio DATE NOT NULL,

    -- Looks planejados (JSONB array)
    looks JSONB NOT NULL,
    -- Estrutura:
    -- [
    --   {
    --     "data": "2025-11-18",
    --     "ocasiao": "faculdade",
    --     "itens": [
    --       {"tipo": "camiseta", "id": "uuid", "nome": "Camiseta WickedBotz"},
    --       {"tipo": "calca", "id": "uuid", "nome": "Jeans Escuro"}
    --     ],
    --     "justificativa": "Look confortável para dia longo na faculdade"
    --   }
    -- ]

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_plano_semanal_user_semana ON plano_semanal_looks(user_id, semana_inicio);
```

### Schemas Pydantic

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Literal
from uuid import UUID

# ========================================
# Routine Templates
# ========================================

class RoutineStep(BaseModel):
    """Passo individual de uma rotina."""
    passo: str = Field(..., description="Nome do passo")
    duracao_min: int = Field(..., gt=0, description="Duração em minutos")
    opcional: bool = Field(default=False, description="Se pode ser pulado")

class RoutineTemplateCreate(BaseModel):
    """Schema para criar template de rotina."""
    nome_template: str
    descricao: Optional[str] = None
    tipo: Literal["manha", "noite", "pre_trabalho", "pos_trabalho"]
    passos: List[RoutineStep]
    buffer_padrao_min: int = 10
    dias_semana: Optional[List[str]] = None

class RoutineTemplate(RoutineTemplateCreate):
    """Template de rotina completo."""
    id: UUID
    user_id: int
    duracao_total_min: int
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Daily Routines
# ========================================

class RoutineBlock(BaseModel):
    """Bloco de roteiro (manhã, evento, tarefa)."""
    tipo: Literal["morning_routine", "calendar_event", "task", "break"]
    titulo: str
    inicio: str  # HH:MM
    fim: Optional[str] = None
    duracao_min: Optional[int] = None
    passos: Optional[List[RoutineStep]] = None
    look: Optional[dict] = None

class DailyRoutineGenerate(BaseModel):
    """Request para gerar roteiro diário."""
    data: date
    template_id: Optional[UUID] = None  # Se None, usa template padrão

class DailyRoutine(BaseModel):
    """Roteiro diário completo."""
    id: UUID
    user_id: int
    data: date
    template_id: Optional[UUID]
    roteiro: dict  # JSONB com blocos
    energia_percentual: float
    fase_ciclo: str
    buffer_adicionado_min: int
    status: Literal["pendente", "em_andamento", "completo", "interrompido"]
    passo_atual: Optional[str]

    class Config:
        from_attributes = True


# ========================================
# Interruptions
# ========================================

class InterruptionCreate(BaseModel):
    """Registra início de interrupção."""
    descricao: str = Field(..., description="Ex: 'Procurar microfone'")

class TradeOffOption(BaseModel):
    """Opção de trade-off após interrupção."""
    id: int
    acao: Literal["skip", "reduce", "accept_delay"]
    passo_afetado: Optional[str] = None
    tempo_economizado: int
    descricao: str

class InterruptionResolve(BaseModel):
    """Resolve interrupção com escolha de trade-off."""
    interrupcao_id: UUID
    tradeoff_escolhido: TradeOffOption

class Interruption(BaseModel):
    """Interrupção completa."""
    id: UUID
    user_id: int
    roteiro_id: UUID
    descricao: str
    inicio: datetime
    fim: Optional[datetime]
    duracao_min: Optional[int]
    buffer_disponivel_min: int
    atraso_causado_min: Optional[int]
    tradeoff_escolhido: Optional[dict]

    class Config:
        from_attributes = True


# ========================================
# Estimation Patterns
# ========================================

class EstimationPattern(BaseModel):
    """Padrão de estimativa para categoria."""
    categoria: str
    tags: List[str]
    total_amostras: int
    estimativa_media_min: float
    real_media_min: float
    desvio_padrao: float
    tendencia: Literal["subestima", "superestima", "acurado"]
    percentual_desvio: float
    confianca: float

    class Config:
        from_attributes = True


# ========================================
# Wardrobe
# ========================================

class RoupaCreate(BaseModel):
    """Criar peça de roupa."""
    nome: str
    categoria: Literal["camiseta", "blusa", "calca", "saia", "vestido", "tenis", "sapato"]
    cor_principal: str
    cor_secundaria: Optional[str] = None
    estampa: Literal["lisa", "estampada", "listrada", "xadrez"]
    ocasioes: List[Literal["casual", "profissional", "esporte", "festa"]]
    temperatura_min: Optional[float] = None
    temperatura_max: Optional[float] = None

class Roupa(RoupaCreate):
    """Peça de roupa completa."""
    id: UUID
    user_id: int
    limpa: bool
    disponivel: bool
    foto_url: Optional[str]
    tags: List[str]

    class Config:
        from_attributes = True

class PlannedOutfit(BaseModel):
    """Look planejado para um dia."""
    data: date
    ocasiao: str
    itens: List[dict]  # Lista de peças
    justificativa: str
```

---

## 🔌 API Endpoints

### Routine Templates

```python
# Criar template de rotina
POST /api/v1/routines/templates
{
  "nome_template": "Rotina Manhã (Faculdade)",
  "tipo": "manha",
  "passos": [
    {"passo": "Levantar", "duracao_min": 2},
    {"passo": "Banheiro", "duracao_min": 3},
    {"passo": "Preparar café", "duracao_min": 15}
  ],
  "buffer_padrao_min": 10,
  "dias_semana": ["seg", "ter", "qua"]
}

# Listar templates
GET /api/v1/routines/templates

# Obter template específico
GET /api/v1/routines/templates/{id}

# Atualizar template
PATCH /api/v1/routines/templates/{id}

# Deletar template
DELETE /api/v1/routines/templates/{id}
```

### Daily Routines

```python
# Gerar roteiro do dia
POST /api/v1/routines/daily/generate
{
  "data": "2025-11-18",
  "template_id": "uuid-opcional"
}

Response:
{
  "id": "uuid",
  "data": "2025-11-18",
  "roteiro": {
    "blocos": [
      {
        "tipo": "morning_routine",
        "titulo": "Rotina Matinal",
        "inicio": "05:00",
        "passos": [...],
        "look": {...}
      }
    ]
  },
  "energia_percentual": 80.0,
  "fase_ciclo": "lutea",
  "buffer_adicionado_min": 10
}

# Obter roteiro do dia
GET /api/v1/routines/daily/{data}

# Iniciar execução de roteiro
POST /api/v1/routines/daily/{id}/start

# Pausar roteiro
POST /api/v1/routines/daily/{id}/pause

# Retomar roteiro
POST /api/v1/routines/daily/{id}/resume

# Marcar passo como concluído
POST /api/v1/routines/daily/{id}/complete-step
{
  "passo": "Preparar marmita",
  "tempo_real_min": 25
}
```

### Interruptions

```python
# Registrar interrupção
POST /api/v1/routines/interruptions
{
  "roteiro_id": "uuid",
  "descricao": "Procurar microfone"
}

Response:
{
  "id": "uuid",
  "buffer_disponivel_min": 10,
  "proximo_deadline": {
    "nome": "SAIR PARA FACULDADE",
    "horario": "07:05"
  },
  "message": "Cronômetro iniciado. Você tem 10 min de buffer."
}

# Resolver interrupção
POST /api/v1/routines/interruptions/{id}/resolve
{
  "tradeoff_escolhido": {
    "id": 1,
    "acao": "skip",
    "passo_afetado": "Pelinhos",
    "tempo_economizado": 5
  }
}

# Listar interrupções
GET /api/v1/routines/interruptions
  ?roteiro_id=uuid
```

### Estimation Validation

```python
# Validar estimativa de tarefa
POST /api/v1/routines/validate-estimation
{
  "task": {
    "title": "Preparar marmita e janta",
    "estimated_hours": 0.5,
    "tags": ["cozinha", "marmita"]
  }
}

Response:
{
  "is_valid": false,
  "user_estimate": 30,
  "historical_avg": 40,
  "message": "Tarefas como esta costumam levar 40min, não 30min.",
  "suggested_estimate": 40,
  "confidence": 0.85
}

# Obter padrões de estimativa
GET /api/v1/routines/patterns
  ?categoria=cozinha
```

### Wardrobe

```python
# Adicionar roupa
POST /api/v1/wardrobe/clothes
{
  "nome": "Camiseta WickedBotz",
  "categoria": "camiseta",
  "cor_principal": "preta",
  "estampa": "estampada",
  "ocasioes": ["casual", "profissional"]
}

# Planejar looks da semana
POST /api/v1/wardrobe/plan-week
{
  "semana_inicio": "2025-11-18"
}

Response:
{
  "looks": [
    {
      "data": "2025-11-18",
      "ocasiao": "faculdade",
      "itens": [
        {"tipo": "camiseta", "nome": "Camiseta WickedBotz"},
        {"tipo": "calca", "nome": "Jeans Escuro"}
      ],
      "justificativa": "Look confortável para dia longo"
    }
  ]
}

# Obter look do dia
GET /api/v1/wardrobe/outfit/{data}
```

---

## 🔗 Integrações

### Event Bus Events

```python
# Eventos que o Routines PUBLICA
EventType.ROUTINE_GENERATED = "routine.daily.generated"
EventType.ROUTINE_STARTED = "routine.daily.started"
EventType.ROUTINE_STEP_COMPLETED = "routine.step.completed"
EventType.INTERRUPTION_DETECTED = "routine.interruption.detected"
EventType.TRADEOFF_DECISION_NEEDED = "routine.tradeoff.needed"
EventType.ESTIMATION_WARNING = "routine.estimation.warning"

# Eventos que o Routines OUVE
EventType.TASK_CREATED = "task.created"
EventType.CALENDAR_EVENT_CREATED = "calendar.event.created"
EventType.WELLNESS_STATUS_UPDATED = "wellness.status.updated"
EventType.CYCLE_PHASE_CHANGED = "wellness.cycle_phase_changed"
```

### Integração com Wellness Coach

```python
@event_bus.subscribe(EventType.WELLNESS_STATUS_UPDATED)
async def on_wellness_update(event: WellnessStatusEvent):
    """
    Quando status de bem-estar muda, ajusta roteiro do dia.
    """
    routine = await routines_service.get_today_routine(event.user_id)

    if not routine:
        return

    # Recalcula buffer baseado em nova energia
    new_context = await wellness_coach.get_energy_context(
        event.user_id,
        date.today()
    )

    # Ajusta roteiro
    await routines_service.adjust_routine_for_energy(
        routine.id,
        new_context
    )
```

### Integração com Calendar

```python
@event_bus.subscribe(EventType.CALENDAR_EVENT_CREATED)
async def on_calendar_event(event: CalendarEventCreated):
    """
    Quando evento é adicionado ao calendário, atualiza roteiro.
    """
    routine = await routines_service.get_routine_for_date(
        event.user_id,
        event.event_date
    )

    if routine:
        # Adiciona evento ao roteiro
        await routines_service.add_block_to_routine(
            routine.id,
            RoutineBlock(
                tipo="calendar_event",
                titulo=event.event_title,
                inicio=event.start_time,
                fim=event.end_time
            )
        )
```

### Integração com Wardrobe Manager

```python
@event_bus.subscribe(EventType.ROUTINE_GENERATED)
async def on_routine_generated(event: RoutineGeneratedEvent):
    """
    Quando roteiro é gerado, adiciona look planejado.
    """
    outfit = await wardrobe_manager.get_planned_outfit(
        event.user_id,
        event.date
    )

    if outfit:
        # Adiciona look ao roteiro
        await routines_service.add_outfit_to_routine(
            event.routine_id,
            outfit
        )
```

---

## 💡 Casos de Uso

### Caso 1: Morning Briefing Completo

```
Fluxo automático às 04:00 (ou ao acordar):

1. Charlee Orchestrator inicia morning_briefing()

2. Routine Manager é ativado
   └─> Busca rotina_templates: "Rotina Manhã (Faculdade)"

3. Consulta fontes de dados em paralelo:
   ├─> Google Calendar: "Faculdade 07:30", "Reunião Syssa 14:00"
   ├─> Wellness Coach: "Fase Lútea, energia 80%"
   └─> Wardrobe Manager: "Look Faculdade Conforto"

4. Ajusta template baseado em energia
   └─> Adiciona 10min de buffer (energia 80%)

5. Monta roteiro integrado

6. Exibe Morning Briefing:

   ☀️ BOM DIA, SAMARA!

   🌸 Status de Bem-Estar:
   Você está na Fase Lútea (Dia 20).
   Energia esperada: Média (80%).
   Adicionei 10min de buffer ao seu roteiro.

   👔 Seu Look de Hoje (Pré-definido):
   • "Look Faculdade Conforto"
   • (Camiseta WickedBotz + Jeans Escuro)

   🎯 Roteiro Detalhado (Manhã):
   05:00 | Levantar
   05:02 | Banheiro e lavar rosto
   05:05 | Ver roupa (Look já separado)
   05:10 | Comida gatinha
   05:20 | Limpar tênis
   05:25 | Omelete
   05:35 | Vitaminas e ferro
   05:40 | Comer e tomar café
   06:00 | Preparar marmita
   06:20 | Pelinhos
   06:25 | Chapinha
   06:45 | Escovar os dentes e perfume
   06:55 | Buffer de Imprevisto (10 min)
   07:05 | SAIR PARA FACULDADE

   🔥 Foco Principal Hoje:
   • Reunião Syssa (14:00) - 1h prep necessária
   • Task Robótica: Documentar Módulo X (1.5h)
```

### Caso 2: Proteção de Estimativa

```
Contexto: Usuário planeja noite

1. Usuário:
   $ charlee add-task "Preparar marmita e janta" --time 30m

2. Charlee Orchestrator → Capacity Guardian

3. Capacity Guardian busca padrões históricos:
   └─> get_historical_patterns(tags=['cozinha', 'marmita'])

4. DB retorna:
   {
     "tarefas_analisadas": 12,
     "estimativa_media": 25,
     "real_media": 38,
     "padrao": "Samara subestima 'cozinha' em ~13min"
   }

5. Capacity Guardian detecta desvio de 26% (38 vs 30)

6. Intervenção:

   "Samara, registrei 'Preparar marmita e janta' (30min).

   🧠 Posso fazer uma observação?

   Notei em meus registros que tarefas de 'cozinha'
   como esta costumam levar em média 38-40 minutos,
   e não 30.

   Você prefere que eu já aloque 40 minutos?
   Isso garantirá que seu roteiro não seja comprometido.

   [1] Manter 30min
   [2] Ajustar para 40min (Recomendado)"

7. Usuário escolhe [2]

8. Tarefa salva com 40min
   └─> Padrão de estimativa é reforçado no DB
```

### Caso 3: Gestão de Imprevisto em Tempo Real

```
Contexto: Usuário no meio da rotina matinal (06:25)

1. Usuário (voz):
   "Charlee, não encontro o microfone, preciso procurar!"

2. Charlee Orchestrator processa interrupção

3. Capacity Guardian é ativado:

   a) Pausa roteiro atual (passo: "Chapinha às 06:25")

   b) Inicia cronômetro da interrupção

   c) Calcula impacto:
      - Próximo deadline: "SAIR PARA FACULDADE 07:05"
      - Buffer disponível: 10min
      - Tempo até deadline: 40min

   d) Envia alerta proativo:

      "Entendido! Um imprevisto.

      Pausei seu roteiro atual ('Chapinha' às 06:25).
      Vou iniciar um cronômetro para 'Procurar microfone'.

      🚨 Alerta de Recálculo:
      Seu tempo de 'SAIR PARA FACULDADE' é às 07:05.
      Você tem 10 minutos de buffer restantes.
      Se demorar mais que isso, você se atrasará."

4. [12 minutos depois]

   Usuário: "Charlee, achei!"

5. Capacity Guardian analisa:
   - Tempo gasto: 12min
   - Buffer: 10min
   - Atraso: 2min

6. Gera opções de trade-off:

   "Ok. Você gastou 12 minutos (2min além do buffer).

   ⚖️ Decisão de Trade-Off Necessária:

   Você está 2 minutos atrasada.
   Para sair às 07:05, você precisa:

   [1] Pular 'Pelinhos' (5min) ✅ Recomendado
   [2] Reduzir 'Chapinha' de 20 para 15min
   [3] Sair 2 minutos atrasada

   O que você decide?"

7. Usuário escolhe [1]

8. Roteiro recalculado:
   - Passo "Pelinhos" removido
   - Horários ajustados
   - Roteiro retomado

9. Interrupção salva no DB para análise futura
```

---

## 🗓️ Roadmap

### Fase 1: MVP - Templates e Geração Básica
- [ ] Modelo de dados (rotina_templates, roteiros_diarios)
- [ ] Routine Manager agent básico
- [ ] API para CRUD de templates
- [ ] Geração de roteiro simples (sem integrações)
- [ ] CLI: `charlee routine generate`

### Fase 2: Integrações Core
- [ ] Integração com Wellness Coach (energia/ciclo)
- [ ] Integração com Google Calendar (eventos)
- [ ] Morning Briefing automático (4:00 AM)
- [ ] Ajuste dinâmico de buffer baseado em energia

### Fase 3: Capacity Guardian - Proteção
- [ ] Modelo de padrões de estimativa
- [ ] Validação de estimativas em tempo real
- [ ] Aprendizado de padrões históricos
- [ ] Alertas de estimativas otimistas

### Fase 4: Gestão de Imprevistos
- [ ] Modelo de interrupções
- [ ] Pausar/retomar roteiro
- [ ] Recálculo em tempo real
- [ ] Sistema de trade-offs
- [ ] Força decisão do usuário

### Fase 5: Wardrobe Manager
- [ ] Modelo de roupas e looks
- [ ] Planejamento semanal de looks
- [ ] Integração com calendário (ocasiões)
- [ ] API de clima (temperatura)
- [ ] Regras de estilo (cores, estampas)

### Fase 6: Frontend (futuro)
- [ ] Dashboard de roteiro do dia
- [ ] Visualização de timeline
- [ ] Interface de trade-offs
- [ ] Gerenciamento de templates
- [ ] Wardrobe visual (fotos de looks)

### Fase 7: Avançado (futuro)
- [ ] Voice integration completa
- [ ] Notificações push de passos
- [ ] Apple Watch integration
- [ ] ML para previsão de tempo de tarefas
- [ ] Otimização automática de ordem de passos

---

## 📚 Referências

### Metodologias
- **Bullet Journal Method** - Ryder Carroll
- **Getting Things Done (GTD)** - David Allen
- **Atomic Habits** - James Clear

### Ciência Cognitiva
- **Decision Fatigue** - Roy Baumeister (Ego Depletion)
- **Thinking, Fast and Slow** - Daniel Kahneman
- **Deep Work** - Cal Newport

### Frameworks Técnicos
- **Event-Driven Architecture** - Martin Fowler
- **Domain-Driven Design** - Eric Evans
- **AI Agents Orchestration** - Multi-agent systems

---

**Desenvolvido com ❤️ por Samara Cassie**

*Versão: 1.0 - Draft Inicial*
*Última atualização: 2025-11-17*
