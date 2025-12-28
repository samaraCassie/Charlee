# 🤝 Charlee Diplomat - Sistema de Gestão de Relacionamentos

> **Versão**: 1.0 (Planejamento)
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V6.x - Relationship Management & Social Capital

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Agentes Especializados](#agentes-especializados)
4. [Modelos de Dados](#modelos-de-dados)
5. [Skills e Automações](#skills-e-automações)
6. [Fluxos de Trabalho](#fluxos-de-trabalho)
7. [API Endpoints](#api-endpoints)
8. [Integrações](#integrações)
9. [Casos de Uso](#casos-de-uso)
10. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

O **Charlee Diplomat** transforma o Charlee de um assistente pessoal em um **gestor de capital social**, reconhecendo que o sucesso profissional e pessoal é definido por liderança e qualidade de interações com outros.

### O Problema: Gestão de Relacionamentos É Complexa

Atualmente, o Charlee foca em **você**. Mas sua vida é definida por:

```
Capital Social = Qualidade × Frequência × Contexto das Interações
```

**Desafios sem o Diplomat**:
1. **📅 Esquecimento**: "Quando foi a última vez que falei com minha mentora?"
2. **🧠 Perda de Contexto**: "O que discutimos na última reunião com Sênior?"
3. **⏰ Timing Ruim**: Deixar relacionamentos esfriarem por falta de contato
4. **📊 Falta de Visão**: Não saber o status geral de suas relações-chave
5. **🎯 Preparação Inadequada**: Entrar em 1:1s sem contexto do histórico

### A Solução: Personal CRM + AI

```
┌─────────────────────────────────────────────────────┐
│              CHARLEE DIPLOMAT                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Personal CRM:                                      │
│  • Pessoas-chave catalogadas                        │
│  • Histórico completo de interações                 │
│  • Sentimento e status da relação                   │
│                                                     │
│  AI Proativo:                                       │
│  • Lembretes de manter contato                      │
│  • Preparação automática para 1:1s                  │
│  • Sugestões de tópicos baseadas em contexto        │
│  • Tracking de pupilos/mentorados                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Quem São as "Pessoas-Chave"?

**Categorias**:
1. **👔 Profissionais**: Sênior (chefe), colegas de trabalho
2. **🎓 Mentoria**: Mentora, professores
3. **👥 Equipe**: Breno, Julio (WickedBotz), pupilos
4. **❤️ Pessoal**: Parceiro ("Osito"), família próxima
5. **🌐 Network**: Contatos estratégicos, ex-colegas

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────┐
│              CHARLEE DIPLOMAT SYSTEM                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   1. DATA LAYER (Personal CRM)              │   │
│  │  • pessoas_chave (contatos principais)      │   │
│  │  • interacoes (histórico de conversas)      │   │
│  │  • relacionamentos (status e sentimento)    │   │
│  │  • pupilos (mentorados da WickedBotz)       │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   2. INTELLIGENCE LAYER (Agents)            │   │
│  │  • Relationship Manager (CRM principal)     │   │
│  │  • Connection Nurturer (lembretes)          │   │
│  │  • 1:1 Prep Agent (preparação de reuniões)  │   │
│  │  • Pupil Tracker (gestão de mentorados)     │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   3. AUTOMATION LAYER (Skills)              │   │
│  │  • Auto-logging de interações               │   │
│  │  • Lembretes proativos de conexão           │   │
│  │  • Análise de sentimento de conversas       │   │
│  │  • Sugestões de tópicos para 1:1s           │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Integração com Outros Módulos

```
Charlee Diplomat
         ↓
    ┌────┴────┐
    ↓         ↓
Calendar    Memory
(1:1s)      (contexto)
    ↓         ↓
    └────┬────┘
         ↓
  Strategic Advisor
  (preparação)
```

---

## 🤖 Agentes Especializados

### 1. Relationship Manager (Agente Principal)

**Responsabilidade**: Gerenciar CRM pessoal e tracking de relacionamentos.

```python
class RelationshipManager:
    """
    Agente central de gestão de relacionamentos.
    """

    async def add_key_person(
        self,
        user_id: int,
        person_data: PersonCreate
    ) -> Person:
        """
        Adiciona pessoa-chave ao CRM.

        Args:
            person_data: Dados da pessoa (nome, categoria, importância)

        Returns:
            Person: Pessoa criada com metadados iniciais
        """
        # 1. Cria registro da pessoa
        person = Person(
            user_id=user_id,
            nome=person_data.nome,
            categoria=person_data.categoria,
            importancia=person_data.importancia,
            empresa=person_data.empresa,
            cargo=person_data.cargo,
            contexto_relacao=person_data.contexto_relacao,
            frequencia_contato_ideal=person_data.frequencia_contato_ideal or "mensal"
        )

        db.add(person)
        db.commit()

        # 2. Cria relacionamento inicial
        relacionamento = Relacionamento(
            user_id=user_id,
            pessoa_id=person.id,
            status="ativo",
            sentimento="neutro",
            nivel_confianca=50,  # baseline
            ultimas_interacoes=[]
        )

        db.add(relacionamento)
        db.commit()

        # 3. Agenda primeiro lembrete de conexão
        await self._schedule_connection_reminder(person)

        logger.info(f"Pessoa-chave adicionada: {person.nome} ({person.categoria})")

        return person

    async def log_interaction(
        self,
        user_id: int,
        pessoa_id: UUID,
        interaction_data: InteractionCreate
    ) -> Interaction:
        """
        Registra interação com pessoa-chave.

        Tipos de interação:
        - reuniao_1_1
        - conversa_informal
        - email
        - mensagem
        - evento
        """
        # 1. Cria registro de interação
        interaction = Interaction(
            user_id=user_id,
            pessoa_id=pessoa_id,
            data=interaction_data.data or datetime.now(),
            tipo=interaction_data.tipo,
            canal=interaction_data.canal,
            duracao_min=interaction_data.duracao_min,
            resumo=interaction_data.resumo,
            topicos_discutidos=interaction_data.topicos_discutidos,
            sentimento=interaction_data.sentimento,
            proximos_passos=interaction_data.proximos_passos
        )

        db.add(interaction)

        # 2. Atualiza relacionamento
        relacionamento = await self._get_relacionamento(user_id, pessoa_id)

        # Atualiza última interação
        relacionamento.ultima_interacao_em = interaction.data

        # Atualiza sentimento (média ponderada)
        if interaction.sentimento:
            relacionamento.sentimento = self._calculate_sentiment(
                current=relacionamento.sentimento,
                new=interaction.sentimento
            )

        # Incrementa contador
        relacionamento.total_interacoes += 1

        # 3. Analisa se precisa de follow-up
        if interaction.proximos_passos:
            await self._create_followup_tasks(
                user_id,
                pessoa_id,
                interaction.proximos_passos
            )

        # 4. Reseta timer de lembrete
        await self._reset_connection_reminder(pessoa_id)

        db.commit()

        return interaction

    async def get_relationship_health(
        self,
        user_id: int,
        pessoa_id: UUID
    ) -> RelationshipHealth:
        """
        Analisa saúde do relacionamento.

        Métricas:
        - Frequência de contato vs ideal
        - Sentimento médio
        - Tempo desde última interação
        - Balanceamento de iniciativa
        """
        pessoa = await self._get_pessoa(pessoa_id)
        relacionamento = await self._get_relacionamento(user_id, pessoa_id)
        interactions = await self._get_recent_interactions(pessoa_id, days=90)

        # 1. Frequência de contato
        ideal_days = self._parse_frequency(pessoa.frequencia_contato_ideal)
        days_since_last = (datetime.now() - relacionamento.ultima_interacao_em).days

        frequency_score = 100 - min(100, (days_since_last / ideal_days) * 100)

        # 2. Sentimento médio
        sentiment_scores = {
            "excelente": 100,
            "bom": 75,
            "neutro": 50,
            "tenso": 25,
            "ruim": 0
        }
        sentiment_score = sentiment_scores.get(relacionamento.sentimento, 50)

        # 3. Engajamento recente
        recent_count = len([i for i in interactions if i.data > datetime.now() - timedelta(days=30)])
        engagement_score = min(100, recent_count * 25)

        # 4. Score geral (média ponderada)
        overall_score = (
            frequency_score * 0.4 +
            sentiment_score * 0.3 +
            engagement_score * 0.3
        )

        # 5. Determina status
        if overall_score >= 80:
            status = "excelente"
            recommendation = "Continue mantendo este ritmo!"
        elif overall_score >= 60:
            status = "bom"
            recommendation = "Considere agendar uma conversa em breve."
        elif overall_score >= 40:
            status = "atencao"
            recommendation = f"Faz {days_since_last} dias desde última interação. Hora de reconectar!"
        else:
            status = "critico"
            recommendation = f"⚠️ Relacionamento pode estar esfriando. Priorize contato urgente!"

        return RelationshipHealth(
            pessoa=pessoa,
            overall_score=overall_score,
            status=status,
            frequency_score=frequency_score,
            sentiment_score=sentiment_score,
            engagement_score=engagement_score,
            days_since_last_contact=days_since_last,
            recommendation=recommendation
        )

    def _calculate_sentiment(
        self,
        current: str,
        new: str
    ) -> str:
        """
        Calcula sentimento atualizado (média ponderada).

        Peso: 70% atual, 30% novo
        """
        sentiment_values = {
            "ruim": 0,
            "tenso": 25,
            "neutro": 50,
            "bom": 75,
            "excelente": 100
        }

        current_val = sentiment_values.get(current, 50)
        new_val = sentiment_values.get(new, 50)

        updated_val = (current_val * 0.7) + (new_val * 0.3)

        # Mapeia de volta para categoria
        if updated_val >= 90:
            return "excelente"
        elif updated_val >= 70:
            return "bom"
        elif updated_val >= 40:
            return "neutro"
        elif updated_val >= 20:
            return "tenso"
        else:
            return "ruim"
```

---

### 2. Connection Nurturer (Lembrete de Conexões)

**Responsabilidade**: Monitorar tempo desde última interação e sugerir contato proativo.

```python
class ConnectionNurturer:
    """
    Agente que monitora relacionamentos e sugere reconexões.
    """

    async def check_relationships_needing_attention(
        self,
        user_id: int
    ) -> List[ConnectionReminder]:
        """
        Identifica relacionamentos que precisam de atenção.

        Executado: Diariamente (scheduled task)
        """
        pessoas = await self._get_all_key_people(user_id)
        reminders = []

        for pessoa in pessoas:
            relacionamento = await self._get_relacionamento(user_id, pessoa.id)

            # Calcula tempo desde última interação
            if not relacionamento.ultima_interacao_em:
                days_since = 999  # Nunca interagiu
            else:
                days_since = (datetime.now() - relacionamento.ultima_interacao_em).days

            # Calcula threshold baseado em frequência ideal
            threshold_days = self._parse_frequency(pessoa.frequencia_contato_ideal)

            # Se passou do threshold, cria lembrete
            if days_since >= threshold_days:
                severity = self._calculate_severity(days_since, threshold_days)

                reminder = ConnectionReminder(
                    pessoa=pessoa,
                    days_since_last_contact=days_since,
                    threshold_days=threshold_days,
                    severity=severity,
                    suggested_actions=await self._generate_suggestions(pessoa, relacionamento)
                )

                reminders.append(reminder)

        # Ordena por severidade (crítico primeiro)
        reminders.sort(key=lambda r: r.severity, reverse=True)

        return reminders

    async def send_daily_relationship_digest(
        self,
        user_id: int
    ) -> RelationshipDigest:
        """
        Envia resumo diário de relacionamentos.

        Incluído no Morning Briefing.
        """
        reminders = await self.check_relationships_needing_attention(user_id)

        if not reminders:
            return RelationshipDigest(
                message="🤝 Todos os relacionamentos estão em dia!",
                reminders=[]
            )

        # Separa por prioridade
        critical = [r for r in reminders if r.severity == "critico"]
        attention = [r for r in reminders if r.severity == "atencao"]

        digest = RelationshipDigest(
            critical_count=len(critical),
            attention_count=len(attention),
            reminders=reminders[:5]  # Top 5
        )

        return digest

    def _calculate_severity(
        self,
        days_since: int,
        threshold: int
    ) -> str:
        """
        Calcula severidade do lembrete.
        """
        ratio = days_since / threshold

        if ratio >= 2.0:
            return "critico"  # 2x do tempo ideal
        elif ratio >= 1.5:
            return "alta"
        elif ratio >= 1.2:
            return "atencao"
        else:
            return "normal"

    async def _generate_suggestions(
        self,
        pessoa: Person,
        relacionamento: Relacionamento
    ) -> List[str]:
        """
        Gera sugestões contextuais de reconexão.
        """
        suggestions = []

        # 1. Sugestão baseada em categoria
        if pessoa.categoria == "mentor":
            suggestions.append("Enviar atualização sobre progresso no TCC")
            suggestions.append("Pedir feedback sobre decisão recente")

        elif pessoa.categoria == "equipe":
            suggestions.append("Agendar 1:1 para check-in")
            suggestions.append("Perguntar como está o projeto X")

        elif pessoa.categoria == "network":
            suggestions.append("Compartilhar artigo relevante")
            suggestions.append("Convite para café")

        # 2. Sugestão baseada em eventos futuros
        upcoming_events = await calendar_service.get_events_with_person(pessoa.id)
        if upcoming_events:
            suggestions.append(f"Preparar para reunião dia {upcoming_events[0].date}")

        # 3. Sugestão baseada em datas especiais
        if pessoa.aniversario:
            days_until = (pessoa.aniversario - datetime.now().date()).days
            if 0 <= days_until <= 7:
                suggestions.append(f"🎂 Aniversário em {days_until} dias! Enviar mensagem.")

        return suggestions
```

---

### 3. OneOnOne Prep Agent (Preparação para 1:1s)

**Responsabilidade**: Preparar contexto completo para reuniões 1:1.

```python
class OneOnOnePrepAgent:
    """
    Agente que prepara contexto para reuniões 1:1.

    Integrado ao Strategic Advisor.
    """

    async def prepare_meeting(
        self,
        user_id: int,
        pessoa_id: UUID,
        meeting_date: datetime
    ) -> MeetingPrep:
        """
        Gera preparação completa para 1:1.

        Inclui:
        - Resumo da última conversa
        - Status de follow-ups pendentes
        - Tópicos sugeridos
        - Perguntas recomendadas
        """
        pessoa = await self._get_pessoa(pessoa_id)
        relacionamento = await self._get_relacionamento(user_id, pessoa_id)

        # 1. Busca última interação
        last_interaction = await self._get_last_interaction(pessoa_id)

        # 2. Busca pendências
        pending_tasks = await tasks_service.get_tasks_related_to_person(pessoa_id)

        # 3. Analisa tendência do relacionamento
        health = await relationship_manager.get_relationship_health(user_id, pessoa_id)

        # 4. Gera sugestões de tópicos via LLM
        topics = await self._generate_topics(
            pessoa,
            relacionamento,
            last_interaction,
            pending_tasks,
            health
        )

        # 5. Monta preparação
        prep = MeetingPrep(
            pessoa=pessoa,
            meeting_date=meeting_date,
            last_interaction_summary=self._summarize_interaction(last_interaction),
            days_since_last_contact=(datetime.now() - last_interaction.data).days,
            relationship_status=health.status,
            pending_followups=pending_tasks,
            suggested_topics=topics,
            talking_points=await self._generate_talking_points(pessoa, topics)
        )

        return prep

    async def _generate_topics(
        self,
        pessoa: Person,
        relacionamento: Relacionamento,
        last_interaction: Interaction,
        pending_tasks: List[Task],
        health: RelationshipHealth
    ) -> List[Topic]:
        """
        Gera tópicos sugeridos para a reunião via LLM.
        """
        prompt = f"""
        Você está preparando Samara para uma reunião 1:1 com {pessoa.nome}.

        Contexto:
        - Categoria: {pessoa.categoria}
        - Cargo: {pessoa.cargo}
        - Relação: {pessoa.contexto_relacao}
        - Última conversa: {last_interaction.resumo}
        - Tópicos anteriores: {', '.join(last_interaction.topicos_discutidos)}
        - Status do relacionamento: {health.status}
        - Pendências: {len(pending_tasks)} tarefas relacionadas

        Gere 3-5 tópicos estratégicos para esta reunião, considerando:
        1. Continuidade dos tópicos anteriores
        2. Follow-up de pendências
        3. Desenvolvimento da relação
        4. Objetivos profissionais de Samara

        Para cada tópico, forneça:
        - Título
        - Objetivo
        - Perguntas-chave
        """

        response = await self.llm.process(prompt)

        return response.topics

    async def _generate_talking_points(
        self,
        pessoa: Person,
        topics: List[Topic]
    ) -> List[str]:
        """
        Gera talking points específicos.
        """
        talking_points = []

        # Baseado na categoria da pessoa
        if pessoa.categoria == "chefe":
            talking_points.extend([
                "1️⃣ Elogiar progresso/conquista recente",
                "2️⃣ Discutir desafio atual e pedir input",
                "3️⃣ Alinhar expectativas para próxima sprint",
                "4️⃣ Perguntar como posso ajudar a equipe"
            ])

        elif pessoa.categoria == "pupilo":
            talking_points.extend([
                "1️⃣ Revisar progresso desde último encontro",
                "2️⃣ Identificar obstáculos e oferecer suporte",
                "3️⃣ Celebrar pequenas vitórias",
                "4️⃣ Definir próximo desafio/meta"
            ])

        elif pessoa.categoria == "mentor":
            talking_points.extend([
                "1️⃣ Atualizar sobre progresso (TCC, carreira)",
                "2️⃣ Apresentar dilema/decisão para feedback",
                "3️⃣ Pedir conselhos sobre próximo passo",
                "4️⃣ Agradecer e perguntar como posso retribuir"
            ])

        return talking_points
```

---

### 4. Pupil Tracker (Gestão de Mentorados)

**Responsabilidade**: Dashboard dedicado para acompanhar progresso de pupilos/mentorados.

```python
class PupilTracker:
    """
    Agente especializado em gestão de mentorados (pupilos da WickedBotz).
    """

    async def add_pupil(
        self,
        user_id: int,
        pupil_data: PupilCreate
    ) -> Pupil:
        """
        Adiciona pupilo ao sistema de mentoria.
        """
        # 1. Cria pessoa-chave
        person = await relationship_manager.add_key_person(
            user_id,
            PersonCreate(
                nome=pupil_data.nome,
                categoria="pupilo",
                importancia="alta",
                empresa="WickedBotz",
                contexto_relacao=f"Mentorado em {pupil_data.area_mentoria}",
                frequencia_contato_ideal="semanal"
            )
        )

        # 2. Cria registro de pupilo
        pupil = Pupil(
            user_id=user_id,
            pessoa_id=person.id,
            area_mentoria=pupil_data.area_mentoria,
            nivel_atual=pupil_data.nivel_atual or "iniciante",
            data_inicio_mentoria=pupil_data.data_inicio or datetime.now(),
            metas=[],
            progresso={}
        )

        db.add(pupil)
        db.commit()

        return pupil

    async def track_progress(
        self,
        user_id: int,
        pupil_id: UUID,
        progress_update: ProgressUpdate
    ) -> PupilProgress:
        """
        Registra progresso do pupilo.
        """
        pupil = await self._get_pupil(pupil_id)

        # 1. Cria registro de progresso
        progress = PupilProgress(
            pupil_id=pupil_id,
            data=progress_update.data or datetime.now(),
            tipo=progress_update.tipo,  # "meta_atingida", "desafio", "feedback"
            descricao=progress_update.descricao,
            nivel_anterior=pupil.nivel_atual,
            nivel_novo=progress_update.nivel_novo,
            feedback=progress_update.feedback
        )

        db.add(progress)

        # 2. Atualiza nível se mudou
        if progress_update.nivel_novo:
            pupil.nivel_atual = progress_update.nivel_novo

        # 3. Registra como interação
        await relationship_manager.log_interaction(
            user_id,
            pupil.pessoa_id,
            InteractionCreate(
                tipo="mentoria",
                resumo=progress_update.descricao,
                topicos_discutidos=[progress_update.tipo],
                sentimento="bom"  # Assumindo positivo
            )
        )

        db.commit()

        return progress

    async def get_pupils_dashboard(
        self,
        user_id: int
    ) -> PupilsDashboard:
        """
        Gera dashboard de todos os pupilos.
        """
        pupils = await self._get_all_pupils(user_id)

        dashboard_data = []

        for pupil in pupils:
            # Busca dados do relacionamento
            pessoa = await self._get_pessoa(pupil.pessoa_id)
            relacionamento = await self._get_relacionamento(user_id, pupil.pessoa_id)

            # Busca progresso recente
            recent_progress = await self._get_recent_progress(pupil.id, days=30)

            # Calcula métricas
            dashboard_data.append(PupilDashboardItem(
                pupil=pupil,
                pessoa=pessoa,
                nivel_atual=pupil.nivel_atual,
                dias_desde_ultima_sessao=(
                    datetime.now() - relacionamento.ultima_interacao_em
                ).days,
                total_sessoes=relacionamento.total_interacoes,
                metas_ativas=len([m for m in pupil.metas if not m.concluida]),
                progresso_recente=recent_progress,
                proxima_acao_sugerida=self._suggest_next_action(pupil, recent_progress)
            ))

        return PupilsDashboard(
            total_pupilos=len(pupils),
            pupilos_ativos=len([p for p in dashboard_data if p.dias_desde_ultima_sessao < 14]),
            pupilos=dashboard_data
        )

    def _suggest_next_action(
        self,
        pupil: Pupil,
        recent_progress: List[PupilProgress]
    ) -> str:
        """
        Sugere próxima ação para o pupilo.
        """
        if not recent_progress:
            return "📅 Agendar sessão de check-in"

        last_progress = recent_progress[0]

        if last_progress.tipo == "desafio":
            return "💪 Follow-up sobre desafio apresentado"
        elif last_progress.tipo == "meta_atingida":
            return "🎯 Definir próxima meta"
        else:
            return "🗣️ Sessão de feedback e planejamento"
```

---

## 📊 Modelos de Dados

### Schema PostgreSQL

```sql
-- ========================================
-- Tabela: pessoas_chave
-- ========================================
CREATE TABLE pessoas_chave (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,  -- chefe, mentor, equipe, pupilo, parceiro, network
    importancia TEXT DEFAULT 'media',  -- baixa, media, alta, critica

    -- Contexto profissional
    empresa TEXT,
    cargo TEXT,
    contexto_relacao TEXT,  -- Ex: "Minha chefe na Syssa", "Pupilo WickedBotz"

    -- Preferências de contato
    frequencia_contato_ideal TEXT DEFAULT 'mensal',  -- semanal, quinzenal, mensal, trimestral
    canal_preferido TEXT[],  -- Ex: ['presencial', 'videochamada', 'whatsapp']

    -- Datas importantes
    aniversario DATE,
    data_conheceu DATE,

    -- Metadados
    linkedin_url TEXT,
    email TEXT,
    telefone TEXT,
    notas TEXT,
    tags TEXT[],

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_pessoas_user ON pessoas_chave(user_id);
CREATE INDEX idx_pessoas_categoria ON pessoas_chave(categoria);
CREATE INDEX idx_pessoas_importancia ON pessoas_chave(importancia);


-- ========================================
-- Tabela: relacionamentos
-- ========================================
CREATE TABLE relacionamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pessoa_id UUID REFERENCES pessoas_chave(id) ON DELETE CASCADE,

    -- Status da relação
    status TEXT DEFAULT 'ativo',  -- ativo, pausado, inativo
    sentimento TEXT DEFAULT 'neutro',  -- excelente, bom, neutro, tenso, ruim
    nivel_confianca INTEGER DEFAULT 50,  -- 0-100

    -- Tracking
    primeira_interacao_em DATE,
    ultima_interacao_em TIMESTAMP,
    total_interacoes INTEGER DEFAULT 0,

    -- Análise
    tendencia TEXT,  -- melhorando, estavel, piorando
    balanco_iniciativa JSONB,  -- {voce: 60, pessoa: 40}

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, pessoa_id)
);

-- Índices
CREATE INDEX idx_relacionamentos_user ON relacionamentos(user_id);
CREATE INDEX idx_relacionamentos_pessoa ON relacionamentos(pessoa_id);
CREATE INDEX idx_relacionamentos_status ON relacionamentos(status);


-- ========================================
-- Tabela: interacoes
-- ========================================
CREATE TABLE interacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pessoa_id UUID REFERENCES pessoas_chave(id) ON DELETE CASCADE,

    -- Detalhes da interação
    data TIMESTAMP NOT NULL,
    tipo TEXT NOT NULL,  -- reuniao_1_1, conversa_informal, email, mensagem, evento, mentoria
    canal TEXT,  -- presencial, videochamada, telefone, whatsapp, email
    duracao_min INTEGER,

    -- Conteúdo
    resumo TEXT,
    topicos_discutidos TEXT[],
    sentimento TEXT,  -- excelente, bom, neutro, tenso, ruim

    -- Resultados
    decisoes_tomadas TEXT[],
    proximos_passos TEXT[],
    follow_up_criado BOOLEAN DEFAULT FALSE,

    -- Metadados
    local TEXT,
    participantes TEXT[],  -- Outras pessoas presentes
    anexos TEXT[],  -- URLs de arquivos relacionados
    notas TEXT,

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_interacoes_user ON interacoes(user_id);
CREATE INDEX idx_interacoes_pessoa ON interacoes(pessoa_id);
CREATE INDEX idx_interacoes_data ON interacoes(data DESC);
CREATE INDEX idx_interacoes_tipo ON interacoes(tipo);


-- ========================================
-- Tabela: pupilos (Mentorados)
-- ========================================
CREATE TABLE pupilos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pessoa_id UUID REFERENCES pessoas_chave(id) ON DELETE CASCADE,

    -- Mentoria
    area_mentoria TEXT NOT NULL,  -- Ex: "Programação Python", "Robótica"
    nivel_atual TEXT DEFAULT 'iniciante',  -- iniciante, intermediario, avancado
    data_inicio_mentoria DATE NOT NULL,
    data_fim_mentoria DATE,

    -- Metas (JSONB)
    metas JSONB DEFAULT '[]',
    -- Estrutura:
    -- [
    --   {
    --     "titulo": "Aprender loops",
    --     "deadline": "2025-12-01",
    --     "concluida": false,
    --     "progresso": 60
    --   }
    -- ]

    -- Progresso (JSONB)
    progresso JSONB DEFAULT '{}',
    -- Estrutura:
    -- {
    --   "aulas_completadas": 10,
    --   "projetos_finalizados": 3,
    --   "skills_adquiridas": ["loops", "funcoes", "listas"]
    -- }

    -- Status
    ativo BOOLEAN DEFAULT TRUE,

    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_pupilos_user ON pupilos(user_id);
CREATE INDEX idx_pupilos_pessoa ON pupilos(pessoa_id);
CREATE INDEX idx_pupilos_ativo ON pupilos(ativo);


-- ========================================
-- Tabela: progresso_pupilos
-- ========================================
CREATE TABLE progresso_pupilos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pupilo_id UUID REFERENCES pupilos(id) ON DELETE CASCADE,

    -- Registro
    data TIMESTAMP NOT NULL,
    tipo TEXT NOT NULL,  -- meta_atingida, desafio, feedback, nivel_up

    -- Detalhes
    descricao TEXT NOT NULL,
    nivel_anterior TEXT,
    nivel_novo TEXT,
    feedback TEXT,

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_progresso_pupilo ON progresso_pupilos(pupilo_id);
CREATE INDEX idx_progresso_data ON progresso_pupilos(data DESC);


-- ========================================
-- Tabela: lembretes_conexao
-- ========================================
CREATE TABLE lembretes_conexao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pessoa_id UUID REFERENCES pessoas_chave(id) ON DELETE CASCADE,

    -- Lembrete
    data_lembrete DATE NOT NULL,
    severidade TEXT NOT NULL,  -- normal, atencao, alta, critico
    mensagem TEXT NOT NULL,
    acoes_sugeridas TEXT[],

    -- Status
    visto BOOLEAN DEFAULT FALSE,
    visto_em TIMESTAMP,
    acao_tomada BOOLEAN DEFAULT FALSE,
    acao_tomada_em TIMESTAMP,

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_lembretes_user ON lembretes_conexao(user_id);
CREATE INDEX idx_lembretes_pessoa ON lembretes_conexao(pessoa_id);
CREATE INDEX idx_lembretes_data ON lembretes_conexao(data_lembrete);
CREATE INDEX idx_lembretes_visto ON lembretes_conexao(visto);
```

### Schemas Pydantic

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import List, Optional, Literal
from uuid import UUID

# ========================================
# Pessoas-Chave
# ========================================

class PersonCreate(BaseModel):
    """Schema para adicionar pessoa-chave."""
    nome: str = Field(..., min_length=1)
    categoria: Literal[
        "chefe", "mentor", "equipe", "pupilo",
        "parceiro", "network", "familia"
    ]
    importancia: Literal["baixa", "media", "alta", "critica"] = "media"
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    contexto_relacao: str = Field(..., description="Como você conheceu/contexto")
    frequencia_contato_ideal: Literal[
        "semanal", "quinzenal", "mensal", "trimestral"
    ] = "mensal"
    aniversario: Optional[date] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    linkedin_url: Optional[str] = None

class Person(PersonCreate):
    """Pessoa-chave completa."""
    id: UUID
    user_id: int
    canal_preferido: List[str]
    data_conheceu: Optional[date]
    notas: Optional[str]
    tags: List[str]
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Interações
# ========================================

class InteractionCreate(BaseModel):
    """Registro de interação."""
    data: Optional[datetime] = None  # Default: now
    tipo: Literal[
        "reuniao_1_1", "conversa_informal", "email",
        "mensagem", "evento", "mentoria"
    ]
    canal: Optional[Literal[
        "presencial", "videochamada", "telefone",
        "whatsapp", "email", "outro"
    ]] = None
    duracao_min: Optional[int] = None
    resumo: str = Field(..., min_length=10)
    topicos_discutidos: List[str] = []
    sentimento: Optional[Literal[
        "excelente", "bom", "neutro", "tenso", "ruim"
    ]] = "neutro"
    decisoes_tomadas: Optional[List[str]] = []
    proximos_passos: Optional[List[str]] = []
    notas: Optional[str] = None

class Interaction(InteractionCreate):
    """Interação completa."""
    id: UUID
    user_id: int
    pessoa_id: UUID
    follow_up_criado: bool
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Relacionamentos
# ========================================

class RelationshipHealth(BaseModel):
    """Análise de saúde do relacionamento."""
    pessoa: Person
    overall_score: float
    status: Literal["excelente", "bom", "atencao", "critico"]
    frequency_score: float
    sentiment_score: float
    engagement_score: float
    days_since_last_contact: int
    recommendation: str

class Relacionamento(BaseModel):
    """Relacionamento completo."""
    id: UUID
    user_id: int
    pessoa_id: UUID
    status: str
    sentimento: str
    nivel_confianca: int
    primeira_interacao_em: Optional[date]
    ultima_interacao_em: Optional[datetime]
    total_interacoes: int
    tendencia: Optional[str]

    class Config:
        from_attributes = True


# ========================================
# Pupilos
# ========================================

class PupilCreate(BaseModel):
    """Criar pupilo/mentorado."""
    nome: str
    area_mentoria: str = Field(..., description="Ex: Programação Python")
    nivel_atual: Literal["iniciante", "intermediario", "avancado"] = "iniciante"
    data_inicio: Optional[date] = None

class ProgressUpdate(BaseModel):
    """Atualização de progresso do pupilo."""
    data: Optional[datetime] = None
    tipo: Literal["meta_atingida", "desafio", "feedback", "nivel_up"]
    descricao: str
    nivel_novo: Optional[Literal["iniciante", "intermediario", "avancado"]] = None
    feedback: Optional[str] = None

class Pupil(BaseModel):
    """Pupilo completo."""
    id: UUID
    user_id: int
    pessoa_id: UUID
    area_mentoria: str
    nivel_atual: str
    data_inicio_mentoria: date
    data_fim_mentoria: Optional[date]
    metas: List[dict]
    progresso: dict
    ativo: bool

    class Config:
        from_attributes = True


# ========================================
# Preparação de Reuniões
# ========================================

class Topic(BaseModel):
    """Tópico sugerido para reunião."""
    titulo: str
    objetivo: str
    perguntas_chave: List[str]
    prioridade: Literal["alta", "media", "baixa"] = "media"

class MeetingPrep(BaseModel):
    """Preparação completa para 1:1."""
    pessoa: Person
    meeting_date: datetime
    last_interaction_summary: str
    days_since_last_contact: int
    relationship_status: str
    pending_followups: List[dict]
    suggested_topics: List[Topic]
    talking_points: List[str]
```

---

## 🔌 API Endpoints

### Pessoas-Chave

```python
# Adicionar pessoa-chave
POST /api/v1/relationships/people
{
  "nome": "Maria Silva",
  "categoria": "mentor",
  "importancia": "critica",
  "cargo": "Professora Orientadora",
  "contexto_relacao": "Orientadora do TCC",
  "frequencia_contato_ideal": "quinzenal",
  "email": "maria.silva@universidade.edu"
}

# Listar pessoas-chave
GET /api/v1/relationships/people
  ?categoria=mentor
  ?importancia=alta

# Obter pessoa específica
GET /api/v1/relationships/people/{id}

# Atualizar pessoa
PATCH /api/v1/relationships/people/{id}

# Deletar pessoa
DELETE /api/v1/relationships/people/{id}
```

### Interações

```python
# Registrar interação
POST /api/v1/relationships/interactions
{
  "pessoa_id": "uuid",
  "tipo": "reuniao_1_1",
  "canal": "videochamada",
  "duracao_min": 45,
  "resumo": "Discutimos progresso do TCC e próximos passos",
  "topicos_discutidos": ["metodologia", "cronograma", "revisão literária"],
  "sentimento": "bom",
  "proximos_passos": [
    "Revisar capítulo 2",
    "Agendar próxima reunião em 2 semanas"
  ]
}

# Listar interações
GET /api/v1/relationships/interactions
  ?pessoa_id=uuid
  ?tipo=reuniao_1_1
  ?start_date=2025-11-01

# Obter interação
GET /api/v1/relationships/interactions/{id}
```

### Análise de Relacionamentos

```python
# Saúde de relacionamento específico
GET /api/v1/relationships/{pessoa_id}/health

Response:
{
  "overall_score": 75.5,
  "status": "bom",
  "frequency_score": 80,
  "sentiment_score": 85,
  "engagement_score": 62,
  "days_since_last_contact": 12,
  "recommendation": "Considere agendar conversa em breve."
}

# Dashboard de todos os relacionamentos
GET /api/v1/relationships/dashboard

Response:
{
  "total_people": 15,
  "relationships_needing_attention": 3,
  "categories": {
    "mentor": 2,
    "equipe": 5,
    "pupilo": 4
  },
  "critical_reminders": [...]
}

# Lembretes de conexão
GET /api/v1/relationships/reminders
  ?severity=critico
```

### Preparação de Reuniões

```python
# Preparar para reunião 1:1
POST /api/v1/relationships/prep-meeting
{
  "pessoa_id": "uuid",
  "meeting_date": "2025-11-20T14:00:00"
}

Response:
{
  "pessoa": {...},
  "last_interaction_summary": "Última conversa: 15 dias atrás...",
  "days_since_last_contact": 15,
  "relationship_status": "bom",
  "pending_followups": [
    {"task": "Revisar capítulo 2", "status": "em_andamento"}
  ],
  "suggested_topics": [
    {
      "titulo": "Progress Update no TCC",
      "objetivo": "Mostrar avanço e pedir feedback",
      "perguntas_chave": [
        "O que acha da estrutura do capítulo 2?",
        "Estou no caminho certo com a metodologia?"
      ]
    }
  ],
  "talking_points": [
    "1️⃣ Atualizar sobre progresso",
    "2️⃣ Pedir feedback sobre decisão",
    "3️⃣ Alinhar próximos passos"
  ]
}
```

### Pupilos

```python
# Adicionar pupilo
POST /api/v1/relationships/pupils
{
  "nome": "João Pedro",
  "area_mentoria": "Programação Python",
  "nivel_atual": "iniciante"
}

# Dashboard de pupilos
GET /api/v1/relationships/pupils/dashboard

Response:
{
  "total_pupilos": 4,
  "pupilos_ativos": 3,
  "pupilos": [
    {
      "pupil": {...},
      "nivel_atual": "intermediario",
      "dias_desde_ultima_sessao": 5,
      "total_sessoes": 12,
      "metas_ativas": 2,
      "proxima_acao_sugerida": "📅 Agendar sessão de feedback"
    }
  ]
}

# Registrar progresso
POST /api/v1/relationships/pupils/{id}/progress
{
  "tipo": "meta_atingida",
  "descricao": "João completou primeiro projeto Python!",
  "feedback": "Ótimo progresso, código bem estruturado"
}
```

---

## 🔗 Integrações

### Event Bus Events

```python
# Eventos que o Diplomat PUBLICA
EventType.RELATIONSHIP_CRITICAL = "relationship.needs_urgent_attention"
EventType.MEETING_PREP_READY = "relationship.meeting_prep.ready"
EventType.PUPIL_MILESTONE_REACHED = "relationship.pupil.milestone"
EventType.CONNECTION_REMINDER = "relationship.connection.reminder"

# Eventos que o Diplomat OUVE
EventType.CALENDAR_EVENT_CREATED = "calendar.event.created"
EventType.TASK_COMPLETED = "task.completed"
EventType.MEMORY_CONVERSATION_LOGGED = "memory.conversation.logged"
```

### Integração com Calendar

```python
@event_bus.subscribe(EventType.CALENDAR_EVENT_CREATED)
async def on_calendar_event(event: CalendarEventCreated):
    """
    Quando reunião 1:1 é agendada, prepara contexto automaticamente.
    """
    # Detecta se é reunião 1:1 (título contém nome de pessoa-chave)
    pessoa = await relationship_manager.find_person_by_name(event.title)

    if pessoa:
        # Gera preparação automática
        prep = await one_on_one_prep.prepare_meeting(
            user_id=event.user_id,
            pessoa_id=pessoa.id,
            meeting_date=event.start_time
        )

        # Envia notificação 1 dia antes
        await scheduler.schedule_notification(
            user_id=event.user_id,
            send_at=event.start_time - timedelta(days=1),
            message=f"📋 Preparação para reunião com {pessoa.nome} pronta!",
            link=f"/relationships/meeting-prep/{prep.id}"
        )
```

### Integração com Memory Agent

```python
@event_bus.subscribe(EventType.MEMORY_CONVERSATION_LOGGED)
async def on_conversation_logged(event: ConversationEvent):
    """
    Quando conversa é logada na memória, registra como interação.
    """
    # Analisa se conversa menciona pessoa-chave
    pessoas_mencionadas = await nlp_service.extract_people(event.conversation)

    for pessoa_nome in pessoas_mencionadas:
        pessoa = await relationship_manager.find_person_by_name(pessoa_nome)

        if pessoa:
            # Cria interação automática
            await relationship_manager.log_interaction(
                user_id=event.user_id,
                pessoa_id=pessoa.id,
                InteractionCreate(
                    tipo="conversa_informal",
                    resumo=f"Mencionado em conversa com Charlee: {event.summary}",
                    topicos_discutidos=event.topics,
                    sentimento="neutro"
                )
            )
```

### Integração com Tasks

```python
@event_bus.subscribe(EventType.TASK_COMPLETED)
async def on_task_completed(event: TaskCompletedEvent):
    """
    Quando tarefa relacionada a pessoa é completada, atualiza follow-up.
    """
    task = await tasks_service.get_task(event.task_id)

    # Verifica se tarefa tem tag de pessoa
    if task.tags and any(tag.startswith("pessoa:") for tag in task.tags):
        pessoa_tag = [t for t in task.tags if t.startswith("pessoa:")][0]
        pessoa_id = pessoa_tag.split(":")[1]

        # Marca follow-up como concluído
        await relationship_manager.mark_followup_completed(
            user_id=event.user_id,
            pessoa_id=pessoa_id,
            task_id=event.task_id
        )
```

### Integração com Strategic Advisor

```python
class StrategicAdvisor:
    """
    Strategic Advisor agora usa dados do Diplomat.
    """

    async def prepare_strategic_decision(
        self,
        user_id: int,
        decision_context: str
    ) -> StrategicAdvice:
        """
        Prepara conselho estratégico considerando relacionamentos.
        """
        # ... lógica existente ...

        # NOVO: Considera input de pessoas-chave
        relevant_people = await relationship_manager.get_relevant_people(
            user_id,
            context=decision_context
        )

        advice_sections.append({
            "title": "🤝 Stakeholders-Chave",
            "content": self._analyze_stakeholders(relevant_people)
        })

        return advice
```

---

## 💡 Casos de Uso

### Caso 1: Lembrete de Conexão Crítico

```
Fluxo automático diário (Morning Briefing):

SEGUNDA-FEIRA (05:00)

1. Connection Nurturer executa check diário:
   └─> Analisa todas as pessoas-chave
   └─> Detecta: Mentora sem contato há 28 dias (threshold: 14)

2. Calcula severidade:
   └─> 28 dias / 14 dias ideal = 2.0x
   └─> Severidade: CRÍTICO

3. Gera lembrete:

   Morning Briefing inclui:

   ☀️ BOM DIA, SAMARA!

   🤝 Relacionamentos Precisando de Atenção:

   ⚠️ CRÍTICO (1):
   • Maria Silva (Mentora)
     └─> Sem contato há 28 dias
     └─> Ideal: quinzenal (14 dias)
     └─> Relação pode estar esfriando!

   Ações Sugeridas:
   [1] Enviar atualização sobre TCC
   [2] Pedir feedback sobre decisão recente
   [3] Agendar reunião de alinhamento

   [Enviar mensagem agora] [Agendar para depois]

4. Usuário escolhe [1]: "Enviar atualização sobre TCC"

5. Charlee auxilia:

   "Ótimo! Vou te ajudar a preparar essa mensagem.

   Com base nas últimas interações com Maria:
   - Última conversa: 28 dias atrás
   - Tópicos: Metodologia do TCC, cronograma
   - Pendências: Revisar capítulo 2

   Sugestão de mensagem:

   'Oi Maria! Espero que esteja bem.

   Queria dar um update sobre o TCC:
   - Finalizei a revisão do capítulo 2 que discutimos
   - Já comecei a implementação da metodologia
   - Gostaria de agendar uma reunião para validar

   Você tem disponibilidade na próxima semana?'

   Enviar assim ou quer ajustar?"

6. Usuário aprova e envia

7. Sistema registra interação:
   └─> Tipo: "email"
   └─> Reseta timer de lembrete
   └─> Atualiza relacionamento: "ativo"
```

### Caso 2: Preparação Automática para 1:1

```
Contexto: Reunião com Sênior (chefe) agendada para quinta-feira

QUARTA-FEIRA (18:00 - 1 dia antes)

1. Calendar trigger detecta reunião amanhã
   └─> "1:1 Sênior Syssa - 14:00"

2. OneOnOne Prep Agent ativado automaticamente

3. Coleta contexto:

   a) Última interação (DB):
      - 12 dias atrás
      - Tipo: reuniao_1_1
      - Tópicos: ["qualidade_codigo", "sprint_planning"]
      - Sentimento: "bom"
      - Próximos passos: [
          "Implementar code review",
          "Melhorar cobertura de testes"
        ]

   b) Status de follow-ups:
      - ✅ "Implementar code review" → Concluído
      - 🔄 "Melhorar cobertura de testes" → Em andamento (78%)

   c) Saúde do relacionamento:
      - Score: 85/100 (Excelente)
      - Sentimento: Bom
      - Frequência: Semanal (ideal)

   d) LLM gera tópicos sugeridos:

4. Charlee envia notificação:

   "📋 Preparação para Reunião Pronta!

   1:1 com Sênior amanhã às 14:00

   [Ver preparação completa]"

5. Usuário abre preparação:

   ─────────────────────────────────────
   📅 1:1 COM SÊNIOR (Chefe Syssa)
   Quinta, 14:00 | Última conversa: 12 dias atrás
   ─────────────────────────────────────

   📝 RESUMO DA ÚLTIMA CONVERSA:
   Discutimos qualidade de código e sprint planning.
   Você se comprometeu a implementar code review e
   melhorar cobertura de testes.

   ✅ FOLLOW-UPS CONCLUÍDOS:
   • Implementar code review ✓

   🔄 FOLLOW-UPS EM ANDAMENTO:
   • Melhorar cobertura de testes (78% atual)

   💡 TÓPICOS SUGERIDOS:

   1️⃣ Celebrar Vitória: Code Review Implementado
      Objetivo: Mostrar progresso e pedir feedback
      Perguntas:
      - O que achou do processo de code review?
      - Algo para ajustar?

   2️⃣ Update: Cobertura de Testes
      Objetivo: Reportar progresso
      Perguntas:
      - 78% de cobertura está adequado?
      - Priorizar mais antes de novas features?

   3️⃣ Planejamento: Próxima Sprint
      Objetivo: Alinhar expectativas
      Perguntas:
      - Quais as prioridades para próxima sprint?
      - Algum projeto urgente?

   4️⃣ Desenvolvimento Pessoal
      Objetivo: Pedir feedback de crescimento
      Perguntas:
      - Como você avalia meu progresso no trimestre?
      - Áreas para desenvolver?

   🗣️ TALKING POINTS:
   1. Elogiar equipe pelo engajamento no code review
   2. Mostrar métrica de redução de bugs
   3. Pedir input sobre priorização de tech debt
   4. Perguntar como posso ajudar a equipe

   ─────────────────────────────────────

6. Durante a reunião (quinta 14:00):
   └─> Usuário usa preparação como guia

7. Após reunião:

   Charlee (proativo):
   "Como foi a 1:1 com Sênior?
    Quer registrar os principais pontos?"

8. Usuário registra interação:

   $ charlee log-interaction --pessoa "Sênior"

   Resumo: "Reunião produtiva, Sênior gostou do code review"
   Tópicos: ["code_review", "cobertura_testes", "prox_sprint"]
   Sentimento: "excelente"
   Próximos passos:
   - Aumentar cobertura para 85%
   - Liderar planning da próxima sprint

9. Sistema atualiza:
   └─> Relacionamento: sentimento "excelente"
   └─> Cria 2 tarefas de follow-up automaticamente
```

### Caso 3: Dashboard de Pupilos (Mentoria WickedBotz)

```
Contexto: Samara mentora 4 alunos na WickedBotz

DOMINGO À TARDE (Planejamento da Semana)

1. Usuário abre dashboard:

   $ charlee pupils-dashboard

2. Sistema gera visão completa:

   ─────────────────────────────────────
   👥 DASHBOARD DE PUPILOS
   ─────────────────────────────────────

   Total: 4 pupilos
   Ativos: 3 (1 pausado)

   ┌─────────────────────────────────┐
   │ JOÃO PEDRO                      │
   ├─────────────────────────────────┤
   │ Área: Programação Python        │
   │ Nível: Intermediário            │
   │ Última sessão: 5 dias atrás     │
   │ Total sessões: 12               │
   │ Metas ativas: 2/3               │
   │                                 │
   │ Progresso Recente:              │
   │ ✅ Completou projeto "To-Do List"│
   │ 📚 Estudando POO                │
   │                                 │
   │ Próxima ação:                   │
   │ 🎯 Definir projeto final        │
   └─────────────────────────────────┘

   ┌─────────────────────────────────┐
   │ MARIA EDUARDA                   │
   ├─────────────────────────────────┤
   │ Área: Robótica (Arduino)        │
   │ Nível: Iniciante                │
   │ Última sessão: 14 dias atrás ⚠️ │
   │ Total sessões: 6                │
   │ Metas ativas: 1/2               │
   │                                 │
   │ Progresso Recente:              │
   │ 💪 Desafio: LED RGB não funciona│
   │                                 │
   │ Próxima ação:                   │
   │ 📅 URGENTE: Agendar follow-up   │
   │    (desafio há 14 dias)         │
   └─────────────────────────────────┘

   [Continua para outros 2 pupilos...]

   ─────────────────────────────────────

   🚨 AÇÕES RECOMENDADAS:

   1. Maria Eduarda: Follow-up urgente sobre desafio
      └─> Sem contato há 14 dias
      └─> Pode estar travada no problema

   2. João Pedro: Definir projeto final
      └─> Pronto para próximo nível
      └─> Agendar sessão de planejamento

3. Usuário escolhe ação [1]: Maria Eduarda

4. Charlee prepara follow-up:

   "Vou te ajudar com o follow-up da Maria.

   Contexto do desafio (14 dias atrás):
   'LED RGB não está funcionando'

   Sugestões de abordagem:

   [1] Mensagem encorajadora + oferta de ajuda
   [2] Agendar sessão de debugging ao vivo
   [3] Enviar material de apoio primeiro

   O que prefere?"

5. Usuário escolhe [2]

6. Charlee agenda automaticamente:
   └─> Cria evento no calendário
   └─> Prepara materiais de debugging
   └─> Registra ação no sistema

7. Após sessão de mentoria:

   $ charlee pupil-progress --nome "Maria Eduarda"

   Tipo: "desafio" → "resolvido"
   Descrição: "Problema era resistor errado! Agora funciona."
   Feedback: "Ótimo raciocínio lógico para debugar"
   Nível: Mantém "iniciante" (ainda aprendendo)

8. Sistema atualiza dashboard automaticamente
```

---

## 🗓️ Roadmap

### Fase 1: MVP - Personal CRM
- [ ] Modelos de dados (pessoas_chave, relacionamentos, interacoes)
- [ ] Relationship Manager agent básico
- [ ] API CRUD de pessoas e interações
- [ ] CLI: `charlee add-person`, `charlee log-interaction`

### Fase 2: Análise de Relacionamentos
- [ ] Cálculo de saúde de relacionamento
- [ ] Dashboard de relacionamentos
- [ ] Métricas de sentimento e frequência
- [ ] Tendências (melhorando/piorando)

### Fase 3: Lembretes Proativos
- [ ] Connection Nurturer agent
- [ ] Scheduled task para check diário
- [ ] Sistema de severidade (normal → crítico)
- [ ] Inclusão no Morning Briefing
- [ ] Sugestões de ações contextuais

### Fase 4: Preparação de 1:1s
- [ ] OneOnOne Prep Agent
- [ ] Integração com Google Calendar
- [ ] Geração automática de tópicos (LLM)
- [ ] Preparação 1 dia antes de reuniões
- [ ] Talking points personalizados

### Fase 5: Gestão de Pupilos
- [ ] Pupil Tracker agent
- [ ] Dashboard de mentorados
- [ ] Sistema de metas e progresso
- [ ] Tracking de níveis (iniciante → avançado)
- [ ] Sugestões de próximas ações

### Fase 6: Automações Avançadas
- [ ] Auto-logging de interações (via Memory Agent)
- [ ] Detecção de menções em conversas
- [ ] Análise de sentimento automática
- [ ] Follow-up tasks automáticas
- [ ] Timeline visual de relacionamentos

### Fase 7: Frontend (futuro)
- [ ] CRM dashboard visual
- [ ] Kanban de relacionamentos
- [ ] Timeline de interações
- [ ] Preparação de reuniões (interface)
- [ ] Dashboard de pupilos (cards visuais)

### Fase 8: Inteligência Avançada (futuro)
- [ ] ML para prever riscos de relacionamentos
- [ ] Análise de rede social (grafo de conexões)
- [ ] Sugestões de networking baseadas em objetivos
- [ ] Insights de padrões de comunicação
- [ ] Warm introductions (conectar pessoas)

---

## 📚 Referências

### Relacionamentos e Networking
- **Never Eat Alone** - Keith Ferrazzi
- **How to Win Friends and Influence People** - Dale Carnegie
- **The Like Switch** - Jack Schafer (FBI)

### Gestão de Pessoas
- **Radical Candor** - Kim Scott
- **The Coaching Habit** - Michael Bungay Stanier
- **Thanks for the Feedback** - Douglas Stone

### Personal CRM
- **Dory** - Personal CRM tool (inspiração)
- **Monica** - Open-source personal CRM
- **Clay** - Modern relationship management

### Tecnologia
- **Graph Databases** - Para rede de relacionamentos
- **Sentiment Analysis** - NLP para análise de conversas
- **Recommendation Systems** - Para sugestões de tópicos

---

**Desenvolvido com ❤️ por Samara Cassie**

*Versão: 1.0 - Draft Inicial*
*Última atualização: 2025-11-17*
