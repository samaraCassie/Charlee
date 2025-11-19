# 🎯 Charlee Brand - Sistema de Gestão de Personal Branding

> **Versão**: 1.0 (Planejamento)
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V8.x - Personal Branding & Content Marketing
> **Última Atualização**: 2025-11-18

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [O Problema](#o-problema)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Agentes Especializados](#agentes-especializados)
5. [Modelos de Dados](#modelos-de-dados)
6. [Fluxos de Trabalho](#fluxos-de-trabalho)
7. [Pilares de Branding](#pilares-de-branding)
8. [Sistema de Segurança](#sistema-de-segurança)
9. [API Endpoints](#api-endpoints)
10. [Integrações](#integrações)
11. [Casos de Uso](#casos-de-uso)
12. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

### O "CMO Pessoal"

O **Charlee Brand** é um módulo proativo que atua como seu **Chief Marketing Officer pessoal**. Ele "minera" suas conquistas nos outros módulos do Charlee, identifica oportunidades de branding e gera conteúdo estratégico automaticamente.

```
┌─────────────────────────────────────────────────────────┐
│                    CHARLEE BRAND                        │
│              "Seu CMO Pessoal Automatizado"             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Conquista Real → Conteúdo Estratégico → Visibilidade  │
│                                                         │
│  Exemplo:                                               │
│  1. Você resolve crise no projeto ✅                    │
│  2. Charlee detecta conquista 🔍                        │
│  3. Gera post sobre "QA em IA" 📝                       │
│  4. Alinhado com "Gestão de Produto" 🎯                 │
│  5. Pronto para publicar no LinkedIn ✨                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Objetivos Principais

1. **Automatizar Mineração de Conquistas**: Detectar marcos importantes automaticamente
2. **Garantir Alinhamento Estratégico**: Todo conteúdo alinhado com pilares de branding
3. **Eliminar Atrito de Criação**: Resolver bloqueio da "página em branco"
4. **Gerenciar Portfólio Ativamente**: Manter portfólio e GitHub atualizados
5. **Proteger Confidencialidade**: Garantir que nada sensível seja exposto

---

## 💔 O Problema

### A Invisibilidade das Conquistas

**Cenário Real:**
```
Semana 1: Você resolve crise crítica no projeto Lunelli
         ↓
Semana 2: Projeta arquitetura do "Agente Wicked" (TCC)
         ↓
Semana 3: Transforma projeto de estudo em produto real
         ↓
Semana 4: ???

Resultado LinkedIn: [Silêncio de 6 meses]
Resultado GitHub: README.md desatualizado de 2023
Resultado Portfólio: Último projeto adicionado há 1 ano
```

### Por Que Isso Acontece?

**Problema #1: Atrito de Criação**
- Bloqueio da "página em branco"
- "O que eu devo compartilhar?"
- "Como transformar isso em post?"
- Resultado: Procrastinação infinita

**Problema #2: Falta de Tempo**
- No meio da "correria", branding é sempre "para depois"
- Quando termina projeto, já está no próximo
- 3 meses depois: "Deveria ter postado sobre aquilo..."

**Problema #3: Falta de Estratégia**
- Posts aleatórios sem direção clara
- Não há narrativa de evolução profissional
- LinkedIn diz "Dev Júnior" mas você faz trabalho de CTO

**Problema #4: Insegurança**
- "Será que isso é relevante?"
- "Vou parecer arrogante?"
- "E se expor informação confidencial?"

### O Custo da Invisibilidade

```python
IMPACTO_REAL = {
    "curto_prazo": [
        "Recrutadores não encontram você",
        "Network não sabe suas conquistas reais",
        "Oportunidades passam despercebidas"
    ],

    "medio_prazo": [
        "Perfil desatualizado vs realidade",
        "Subestimação de capacidades",
        "Perda de momentum de conquistas"
    ],

    "longo_prazo": [
        "Evolução profissional invisível",
        "Objetivo de CTO parece distante",
        "Portfólio não reflete expertise real"
    ]
}
```

---

## 🏗️ Arquitetura do Sistema

### Visão de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                    CHARLEE BRAND SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   1. INPUT LAYER (Detecção de Conquistas)           │   │
│  │                                                      │   │
│  │  Event Bus ─┬─→ TASK_COMPLETED (impacto_alto)       │   │
│  │             ├─→ PROJECT_COMPLETED                    │   │
│  │             ├─→ MILESTONE_ACHIEVED (OKRs)            │   │
│  │             ├─→ ARCHIVE_DOCUMENT_ADDED (TCC)         │   │
│  │             └─→ PUPIL_MILESTONE (WickedBotz)         │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   2. INTELLIGENCE LAYER (Agentes)                   │   │
│  │                                                      │   │
│  │  ContentMiningAgent     → Garimpeiro de Conquistas  │   │
│  │  ContentStrategyAgent   → Estrategista de Marca     │   │
│  │  ContentGenerationAgent → Escritor Fantasma         │   │
│  │  ProfileAuditorAgent    → Auditor de Perfil         │   │
│  │  TrendAnalysisAgent     → Analista de Tendências    │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   3. OUTPUT LAYER (Conteúdo Gerado)                 │   │
│  │                                                      │   │
│  │  • LinkedIn Posts (rascunhos)                        │   │
│  │  • GitHub READMEs                                    │   │
│  │  • Portfolio Updates                                 │   │
│  │  • Profile Optimization Suggestions                  │   │
│  │  • Content Calendar (próximos 30 dias)               │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integração com Outros Módulos

```
Charlee Brand
       │
   ┌───┴────┐
   ↓        ↓
Event Bus  Archive
   ↓        ↓
Projects  OKRs
   ↓        ↓
Tasks    Diplomat
   ↓        ↓
   └────┬───┘
        ↓
  Content Output
```

---

## 🤖 Agentes Especializados

### 1. ContentMiningAgent (O "Garimpeiro de Conquistas")

**Responsabilidade**: Detectar e catalogar conquistas automaticamente.

```python
class ContentMiningAgent:
    """
    Agente que monitora Event Bus e identifica conquistas dignas de branding.
    """

    def __init__(self, db: Session, event_bus: EventBus):
        self.database = db
        self.event_bus = event_bus

        # Subscribe aos eventos relevantes
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self.on_task_completed)
        self.event_bus.subscribe(EventType.PROJECT_COMPLETED, self.on_project_completed)
        self.event_bus.subscribe(EventType.MILESTONE_ACHIEVED, self.on_milestone_achieved)
        self.event_bus.subscribe(EventType.ARCHIVE_DOCUMENT_ADDED, self.on_document_added)
        self.event_bus.subscribe(EventType.PUPIL_MILESTONE, self.on_pupil_milestone)

    async def on_task_completed(self, event: TaskCompletedEvent):
        """
        Detecta tarefas de alto impacto concluídas.
        """
        task = await self._get_task(event.task_id)

        # Apenas tarefas marcadas como alto impacto
        if not task.impacto_alto:
            return

        # Cria briefing de conteúdo
        briefing = await self._create_content_briefing(
            tipo="task_completion",
            source_id=task.id,
            titulo=task.description,
            contexto=await self._gather_task_context(task),
            tags=task.tags,
            big_rock=await self._get_big_rock(task.big_rock_id)
        )

        # Envia para estrategista
        await self.event_bus.publish(
            EventType.CONTENT_OPPORTUNITY_DETECTED,
            briefing
        )

        logger.info(f"Conquista detectada: {task.description}")

    async def on_project_completed(self, event: ProjectCompletedEvent):
        """
        Detecta projetos freelance concluídos.
        """
        project = await self._get_project(event.project_id)
        execution = await self._get_execution(event.execution_id)

        # Critérios de relevância
        if not self._is_brandable_project(execution):
            return

        briefing = await self._create_content_briefing(
            tipo="project_completion",
            source_id=project.id,
            titulo=f"Projeto: {project.titulo}",
            contexto={
                "skills_usadas": execution.skills_usadas,
                "desafios_superados": execution.desafios_superados,
                "resultados": execution.resultados,
                "satisfacao_cliente": execution.client_satisfaction,
                "duracao": execution.duracao_dias
            },
            tags=project.tags
        )

        await self.event_bus.publish(
            EventType.CONTENT_OPPORTUNITY_DETECTED,
            briefing
        )

    async def on_milestone_achieved(self, event: MilestoneEvent):
        """
        Detecta marcos importantes de OKRs.
        """
        milestone = await self._get_milestone(event.milestone_id)
        okr = await self._get_okr(milestone.okr_id)

        # Apenas milestones de Big Rocks críticos
        if okr.importancia not in ["alta", "critica"]:
            return

        briefing = await self._create_content_briefing(
            tipo="milestone",
            source_id=milestone.id,
            titulo=f"Marco: {milestone.titulo}",
            contexto={
                "okr": okr.titulo,
                "progresso": milestone.progresso,
                "impacto": milestone.impacto_descricao,
                "aprendizados": milestone.licoes_aprendidas
            }
        )

        await self.event_bus.publish(
            EventType.CONTENT_OPPORTUNITY_DETECTED,
            briefing
        )

    async def on_document_added(self, event: ArchiveDocumentEvent):
        """
        Detecta documentos importantes adicionados ao Archive.

        Especialmente: TCC, artigos publicados, certificações.
        """
        document = await self._get_document(event.document_id)

        # Detecta tipo de documento
        if self._is_tcc(document):
            briefing = await self._create_tcc_briefing(document)
        elif self._is_certification(document):
            briefing = await self._create_certification_briefing(document)
        elif self._is_article(document):
            briefing = await self._create_article_briefing(document)
        else:
            return

        await self.event_bus.publish(
            EventType.CONTENT_OPPORTUNITY_DETECTED,
            briefing
        )

    async def on_pupil_milestone(self, event: PupilMilestoneEvent):
        """
        Detecta conquistas de mentorados (WickedBotz).

        Branding através de liderança: "Meu aluno conquistou X".
        """
        pupil = await self._get_pupil(event.pupil_id)
        milestone = event.milestone_data

        briefing = await self._create_content_briefing(
            tipo="mentoria",
            source_id=pupil.id,
            titulo=f"Pupilo {pupil.nome}: {milestone['titulo']}",
            contexto={
                "pupilo": pupil.nome,  # Será anonimizado
                "conquista": milestone['descricao'],
                "area": pupil.area_mentoria,
                "nivel": pupil.nivel_atual,
                "tempo_mentoria": self._calculate_mentoring_duration(pupil)
            },
            tags=["mentoria", "lideranca", "wickedbotz"]
        )

        await self.event_bus.publish(
            EventType.CONTENT_OPPORTUNITY_DETECTED,
            briefing
        )

    def _is_brandable_project(self, execution: ProjectExecution) -> bool:
        """
        Determina se projeto é relevante para branding.

        Critérios:
        - Satisfação cliente >= 4.5
        - Projeto complexo (skills >= 3)
        - Resultados mensuráveis
        - Não é confidencial
        """
        if execution.client_satisfaction < 4.5:
            return False

        if len(execution.skills_usadas) < 3:
            return False

        if not execution.resultados:
            return False

        if execution.confidencial:
            return False

        return True

    async def _gather_task_context(self, task: Task) -> Dict:
        """
        Reúne contexto completo da tarefa para o briefing.
        """
        context = {
            "descricao": task.description,
            "big_rock": await self._get_big_rock(task.big_rock_id),
            "notas": task.notes,
            "tags": task.tags,
            "data_conclusao": task.completed_at
        }

        # Busca documentos relacionados no Archive
        related_docs = await self._find_related_documents(task)
        if related_docs:
            context["documentos"] = related_docs

        # Busca conversas com Strategic Advisor sobre essa tarefa
        strategic_context = await self._get_strategic_context(task)
        if strategic_context:
            context["strategic_insights"] = strategic_context

        return context

    async def _create_content_briefing(
        self,
        tipo: str,
        source_id: UUID,
        titulo: str,
        contexto: Dict,
        tags: List[str] = None
    ) -> ContentBriefing:
        """
        Cria briefing estruturado para o ContentStrategyAgent.
        """
        return ContentBriefing(
            id=uuid4(),
            tipo=tipo,
            source_id=source_id,
            source_type=self._determine_source_type(tipo),
            titulo=titulo,
            contexto=contexto,
            tags=tags or [],
            detected_at=datetime.now(timezone.utc),
            status="pending_strategy"
        )
```

### 2. ContentStrategyAgent (O "Estrategista de Marca")

**Responsabilidade**: Definir ângulo estratégico baseado nos pilares de branding.

```python
class ContentStrategyAgent:
    """
    Guardião dos pilares de branding. Define como cada conquista deve ser apresentada.
    """

    def __init__(self, db: Session, user_id: int):
        self.database = db
        self.user_id = user_id
        self.pilares = self._load_branding_pilares()

    async def process_briefing(self, briefing: ContentBriefing) -> ContentStrategy:
        """
        Processa briefing e define estratégia de conteúdo.

        Passos:
        1. Identifica pilar de branding relevante
        2. Define ângulo narrativo
        3. Aplica regras de segurança
        4. Define formato(s) de conteúdo
        5. Define prioridade
        """
        # 1. Match com pilares
        pilar_match = await self._match_to_pilar(briefing)

        # 2. Define ângulo
        angulo = await self._define_narrative_angle(briefing, pilar_match)

        # 3. Segurança
        security_rules = await self._apply_security_rules(briefing)

        # 4. Formatos
        formatos = self._determine_content_formats(briefing, pilar_match)

        # 5. Prioridade
        prioridade = self._calculate_priority(briefing, pilar_match)

        # Cria estratégia
        strategy = ContentStrategy(
            briefing_id=briefing.id,
            pilar_primario=pilar_match.pilar.nome,
            pilar_secundario=pilar_match.pilar_secundario,
            angulo_narrativo=angulo,
            security_rules=security_rules,
            formatos=formatos,
            prioridade=prioridade,
            tom_voz=self._get_tone_for_pilar(pilar_match.pilar),
            keywords=self._extract_keywords(briefing, pilar_match),
            cta=self._define_call_to_action(pilar_match.pilar)
        )

        logger.info(
            f"Estratégia definida: {briefing.titulo} → "
            f"Pilar: {strategy.pilar_primario}, Formato: {strategy.formatos}"
        )

        return strategy

    async def _match_to_pilar(self, briefing: ContentBriefing) -> PilarMatch:
        """
        Identifica qual pilar de branding é mais relevante.

        Algoritmo:
        - Analisa tags do briefing
        - Analisa skills envolvidas
        - Analisa contexto semântico
        - Retorna pilar com maior score
        """
        scores = {}

        for pilar in self.pilares:
            score = 0

            # Score por tags
            tag_overlap = set(briefing.tags) & set(pilar.keywords)
            score += len(tag_overlap) * 10

            # Score por skills (se disponível)
            if "skills_usadas" in briefing.contexto:
                skill_overlap = set(briefing.contexto["skills_usadas"]) & set(pilar.skills)
                score += len(skill_overlap) * 15

            # Score semântico (embeddings)
            semantic_score = await self._calculate_semantic_similarity(
                briefing.titulo + " " + str(briefing.contexto),
                pilar.descricao
            )
            score += semantic_score * 20

            scores[pilar.nome] = score

        # Pilar com maior score
        pilar_primario = max(scores, key=scores.get)
        pilar_obj = next(p for p in self.pilares if p.nome == pilar_primario)

        # Pilar secundário (se score alto também)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        pilar_secundario = sorted_scores[1][0] if sorted_scores[1][1] > 30 else None

        return PilarMatch(
            pilar=pilar_obj,
            pilar_secundario=pilar_secundario,
            confidence_score=scores[pilar_primario]
        )

    async def _define_narrative_angle(
        self,
        briefing: ContentBriefing,
        pilar_match: PilarMatch
    ) -> str:
        """
        Define ângulo narrativo usando LLM.

        Prompt Engineering para garantir alinhamento estratégico.
        """
        prompt = f"""
        Você é o estrategista de marca de Samara. Defina o melhor ângulo narrativo.

        CONQUISTA:
        {briefing.titulo}

        CONTEXTO:
        {json.dumps(briefing.contexto, indent=2, ensure_ascii=False)}

        PILAR DE BRANDING:
        {pilar_match.pilar.nome} - {pilar_match.pilar.descricao}

        REGRAS:
        1. Foque no APRENDIZADO, não na conquista em si
        2. Evite falar de problemas/crises diretamente
        3. Transforme desafio em insight universal
        4. Mantenha tom profissional mas acessível
        5. NUNCA mencione: clientes, colegas, empresas específicas

        EXEMPLOS DE ÂNGULOS:

        ❌ Ruim: "Resolvi crise no projeto Lunelli"
        ✅ Bom: "A importância de processos de QA em projetos de IA"

        ❌ Ruim: "Breno estava atrasando e eu tive que intervir"
        ✅ Bom: "Como gestão de expectativas previne surpresas em entregas"

        Defina o melhor ângulo narrativo para esta conquista (1 frase):
        """

        response = await self.llm.process(prompt)
        return response.angle

    async def _apply_security_rules(self, briefing: ContentBriefing) -> SecurityRules:
        """
        Define regras de segurança/confidencialidade.
        """
        rules = SecurityRules(
            anonimizar_nomes=True,  # Sempre
            anonimizar_empresas=True,  # Sempre
            nivel_detalhamento="alto_nivel",  # Default
            topics_proibidos=[]
        )

        # Regras específicas por tipo
        if briefing.tipo == "project_completion":
            rules.nivel_detalhamento = "medio"
            rules.topics_proibidos = [
                "valores_financeiros",
                "prazos_especificos",
                "nomes_clientes"
            ]

        elif briefing.tipo == "task_completion":
            # Verifica se tarefa é de crise
            if self._is_crisis_task(briefing):
                rules.nivel_detalhamento = "baixo"
                rules.topics_proibidos.extend([
                    "problemas_especificos",
                    "pessoas_envolvidas",
                    "impacto_negativo"
                ])
                rules.foco_recomendado = "processo_solucao"

        elif briefing.tipo == "mentoria":
            rules.anonimizar_nomes = True  # Proteger identidade do pupilo
            rules.nivel_detalhamento = "alto"  # Pode ser mais específico sobre métodos

        return rules

    def _determine_content_formats(
        self,
        briefing: ContentBriefing,
        pilar_match: PilarMatch
    ) -> List[str]:
        """
        Define quais formatos de conteúdo gerar.
        """
        formatos = []

        # LinkedIn post é sempre gerado
        formatos.append("linkedin_post")

        # Formatos adicionais baseados no tipo
        if briefing.tipo == "project_completion":
            formatos.append("portfolio_update")

            # Se projeto tem repositório, gerar README
            if "repositorio" in briefing.contexto:
                formatos.append("github_readme")

        elif briefing.tipo == "milestone":
            # Milestones podem virar artigos se muito relevantes
            if pilar_match.confidence_score > 80:
                formatos.append("article_outline")

        elif briefing.tipo == "tcc":
            formatos.extend([
                "linkedin_post",
                "github_readme",
                "portfolio_update",
                "article_outline"  # TCC merece artigo longo
            ])

        elif briefing.tipo == "mentoria":
            formatos.append("linkedin_post")
            # Mentorias podem virar série de posts
            if self._count_pupil_milestones() > 5:
                formatos.append("content_series")

        return formatos

    def _calculate_priority(
        self,
        briefing: ContentBriefing,
        pilar_match: PilarMatch
    ) -> int:
        """
        Calcula prioridade de publicação (0-100).

        Fatores:
        - Recência (quanto mais recente, maior prioridade)
        - Relevância para pilar estratégico
        - Tipo de conquista
        - Impacto potencial
        """
        priority = 50  # Base

        # Recência (max +20)
        days_ago = (datetime.now(timezone.utc) - briefing.detected_at).days
        if days_ago == 0:
            priority += 20  # Hoje
        elif days_ago <= 3:
            priority += 15  # Esta semana
        elif days_ago <= 7:
            priority += 10
        elif days_ago <= 30:
            priority += 5

        # Relevância para pilar (max +30)
        priority += min(pilar_match.confidence_score / 3, 30)

        # Tipo de conquista (max +20)
        tipo_scores = {
            "tcc": 20,
            "project_completion": 15,
            "milestone": 12,
            "task_completion": 8,
            "mentoria": 10,
            "certification": 18
        }
        priority += tipo_scores.get(briefing.tipo, 5)

        # Impacto (max +10)
        if "impacto_alto" in briefing.tags:
            priority += 10

        return min(priority, 100)
```

### 3. ContentGenerationAgent (O "Escritor Fantasma")

**Responsabilidade**: Gerar rascunhos de alta qualidade.

```python
class ContentGenerationAgent:
    """
    O melhor escritor de LinkedIn de Samara.
    """

    def __init__(self, db: Session, user_id: int):
        self.database = db
        self.user_id = user_id
        self.user_profile = self._load_user_profile()

    async def generate_content(
        self,
        briefing: ContentBriefing,
        strategy: ContentStrategy
    ) -> List[ContentDraft]:
        """
        Gera rascunhos de conteúdo baseados na estratégia.
        """
        drafts = []

        for formato in strategy.formatos:
            if formato == "linkedin_post":
                draft = await self.draft_linkedin_post(briefing, strategy)
            elif formato == "github_readme":
                draft = await self.draft_github_readme(briefing, strategy)
            elif formato == "portfolio_update":
                draft = await self.update_portfolio_item(briefing, strategy)
            elif formato == "article_outline":
                draft = await self.draft_article_outline(briefing, strategy)
            elif formato == "content_series":
                draft = await self.plan_content_series(briefing, strategy)
            else:
                continue

            drafts.append(draft)

        return drafts

    async def draft_linkedin_post(
        self,
        briefing: ContentBriefing,
        strategy: ContentStrategy
    ) -> ContentDraft:
        """
        Gera rascunho de post para LinkedIn.

        Estrutura otimizada:
        - Hook (primeira linha impactante)
        - Contexto (2-3 linhas)
        - Insight principal (core do post)
        - Lição/Aprendizado
        - CTA opcional
        - Hashtags estratégicas
        """
        # Aplica anonimização
        contexto_safe = self._anonymize_context(
            briefing.contexto,
            strategy.security_rules
        )

        # Prompt para LLM
        prompt = f"""
        Você é o escritor de LinkedIn de Samara. Escreva um post impactante.

        PERFIL DE SAMARA:
        {self.user_profile.bio}
        Objetivos: {self.user_profile.objetivos_carreira}
        Tom de voz: {strategy.tom_voz}

        CONQUISTA:
        {briefing.titulo}

        CONTEXTO (JÁ ANONIMIZADO):
        {json.dumps(contexto_safe, indent=2, ensure_ascii=False)}

        ÂNGULO NARRATIVO:
        {strategy.angulo_narrativo}

        PILAR DE BRANDING:
        {strategy.pilar_primario}

        REGRAS DE ESCRITA:
        1. HOOK: Primeira linha deve parar o scroll
        2. ESTRUTURA: Parágrafos curtos (2-3 linhas)
        3. FOCO: Insight > Conquista (ensine algo)
        4. TOM: Profissional mas acessível (evite jargão desnecessário)
        5. COMPRIMENTO: 150-250 palavras (LinkedIn sweet spot)
        6. CTA: {strategy.cta}
        7. HASHTAGS: Máximo 5, relevantes

        EXEMPLOS DE HOOKS QUE FUNCIONAM:
        - "Esta semana aprendi uma lição valiosa sobre..."
        - "Você sabia que 80% dos projetos de IA falham por...?"
        - "Depois de [X meses] trabalhando em..., uma conclusão me surpreendeu:"
        - "A diferença entre código que funciona e código robusto é..."

        EVITE:
        - "Estou feliz em anunciar..." (clichê)
        - Listas longas de tecnologias
        - Auto-promoção excessiva
        - Negatividade sobre pessoas/empresas

        Escreva o post:
        """

        response = await self.llm.process(prompt)

        # Pós-processamento
        post_text = response.content

        # Adiciona emojis estratégicos (se apropriado)
        post_text = self._add_strategic_emojis(post_text, strategy.pilar_primario)

        # Valida comprimento
        if len(post_text.split()) > 300:
            post_text = await self._condense_post(post_text)

        # Extrai hashtags ou gera se não houver
        hashtags = self._extract_or_generate_hashtags(post_text, strategy)

        draft = ContentDraft(
            briefing_id=briefing.id,
            formato="linkedin_post",
            titulo=briefing.titulo[:100],
            conteudo=post_text,
            metadata={
                "hashtags": hashtags,
                "pilar": strategy.pilar_primario,
                "estimated_reach": self._estimate_reach(hashtags),
                "optimal_posting_time": self._suggest_posting_time()
            },
            status="draft",
            created_at=datetime.now(timezone.utc)
        )

        return draft

    async def draft_github_readme(
        self,
        briefing: ContentBriefing,
        strategy: ContentStrategy
    ) -> ContentDraft:
        """
        Gera README.md excepcional para repositório GitHub.
        """
        # README tem estrutura específica
        prompt = f"""
        Escreva um README.md profissional e completo.

        PROJETO:
        {briefing.titulo}

        CONTEXTO:
        {json.dumps(briefing.contexto, indent=2, ensure_ascii=False)}

        ESTRUTURA DO README:

        # [Nome do Projeto]
        > [Descrição concisa em 1 linha]

        ## 🎯 Visão Geral
        [2-3 parágrafos explicando o QUE é e POR QUE existe]

        ## ✨ Features Principais
        - Feature 1
        - Feature 2
        - Feature 3

        ## 🏗️ Arquitetura
        [Diagrama ou descrição da arquitetura]

        ## 🚀 Como Usar
        ```bash
        # Comandos de instalação/uso
        ```

        ## 🛠️ Tecnologias
        - Tech 1 - Razão de escolha
        - Tech 2 - Razão de escolha

        ## 📊 Resultados/Impacto
        [Métricas, se disponível]

        ## 🧠 Aprendizados
        [O que você aprendeu construindo isso]

        ## 📝 Licença
        [MIT/Apache/etc]

        ---

        REGRAS:
        1. Use emojis para seções (facilita scan visual)
        2. Code blocks para comandos
        3. Seja técnico MAS acessível
        4. Mostre resultados/impacto (não só features)
        5. Seção "Aprendizados" diferencia de READMEs genéricos

        Escreva o README:
        """

        readme_content = await self.llm.process(prompt)

        draft = ContentDraft(
            briefing_id=briefing.id,
            formato="github_readme",
            titulo=f"README.md - {briefing.titulo}",
            conteudo=readme_content.content,
            metadata={
                "repositorio": briefing.contexto.get("repositorio"),
                "linguagem_principal": briefing.contexto.get("linguagem")
            },
            status="draft"
        )

        return draft

    async def update_portfolio_item(
        self,
        briefing: ContentBriefing,
        strategy: ContentStrategy
    ) -> ContentDraft:
        """
        Cria/atualiza item no portfólio.
        """
        # Extrai dados relevantes
        portfolio_data = {
            "titulo": briefing.titulo,
            "descricao_curta": strategy.angulo_narrativo,
            "skills": briefing.contexto.get("skills_usadas", []),
            "categoria": self._map_pilar_to_category(strategy.pilar_primario),
            "destaque": strategy.prioridade > 80,
            "imagens": briefing.contexto.get("screenshots", []),
            "repositorio": briefing.contexto.get("repositorio"),
            "demo_url": briefing.contexto.get("demo_url"),
            "resultados": briefing.contexto.get("resultados"),
            "data_conclusao": briefing.detected_at
        }

        # Gera descrição longa usando LLM
        descricao_longa = await self._generate_portfolio_description(
            briefing,
            strategy
        )

        portfolio_data["descricao_longa"] = descricao_longa

        # Cria draft (será inserido na tabela portfolio_items)
        draft = ContentDraft(
            briefing_id=briefing.id,
            formato="portfolio_update",
            titulo=briefing.titulo,
            conteudo=json.dumps(portfolio_data, ensure_ascii=False, indent=2),
            metadata={"category": portfolio_data["categoria"]},
            status="draft"
        )

        return draft

    def _anonymize_context(
        self,
        contexto: Dict,
        security_rules: SecurityRules
    ) -> Dict:
        """
        Anonimiza contexto aplicando regras de segurança.
        """
        safe_context = contexto.copy()

        if security_rules.anonimizar_nomes:
            safe_context = self._replace_names_with_generic(safe_context)

        if security_rules.anonimizar_empresas:
            safe_context = self._replace_companies_with_generic(safe_context)

        # Remove tópicos proibidos
        for topic in security_rules.topics_proibidos:
            if topic in safe_context:
                del safe_context[topic]

        # Ajusta nível de detalhamento
        if security_rules.nivel_detalhamento == "baixo":
            safe_context = self._reduce_detail_level(safe_context)

        return safe_context

    def _replace_names_with_generic(self, context: Dict) -> Dict:
        """
        Substitui nomes próprios por genéricos.

        Ex: "Breno" → "um colega desenvolvedor"
             "Maria" → "uma aluna"
        """
        # Implementação com NER (Named Entity Recognition)
        # ou lista conhecida de nomes
        ...

    def _add_strategic_emojis(self, text: str, pilar: str) -> str:
        """
        Adiciona emojis alinhados com pilar de branding.
        """
        emoji_map = {
            "Liderança de IA": ["🤖", "🧠", "✨"],
            "Gestão de Produto": ["🎯", "📊", "🚀"],
            "Engenharia de Software": ["💻", "🏗️", "⚙️"],
            "Robótica & STEM": ["🤖", "🔬", "🎓"],
            "Mentoria & Liderança": ["👥", "🌱", "💡"]
        }

        emojis = emoji_map.get(pilar, ["✨"])

        # Adiciona emoji na primeira linha (hook)
        lines = text.split("\n")
        if lines and not any(emoji in lines[0] for emoji in emojis):
            lines[0] = f"{emojis[0]} {lines[0]}"

        return "\n".join(lines)

    def _extract_or_generate_hashtags(
        self,
        text: str,
        strategy: ContentStrategy
    ) -> List[str]:
        """
        Extrai hashtags do texto ou gera estrategicamente.
        """
        # Tenta extrair do texto
        existing_hashtags = re.findall(r'#(\w+)', text)

        if len(existing_hashtags) >= 3:
            return existing_hashtags[:5]

        # Gera baseado em keywords da estratégia
        hashtags = []

        # Hashtag do pilar
        pilar_hashtag = strategy.pilar_primario.replace(" ", "").replace("&", "")
        hashtags.append(pilar_hashtag)

        # Hashtags das keywords
        for keyword in strategy.keywords[:3]:
            hashtag = keyword.replace(" ", "").capitalize()
            if hashtag not in hashtags:
                hashtags.append(hashtag)

        # Hashtags genéricas de alto alcance
        generic = ["IA", "TechBrasil", "WomenInTech", "DesenvolvedoraBR"]
        for tag in generic:
            if len(hashtags) < 5:
                hashtags.append(tag)

        return hashtags[:5]

    def _suggest_posting_time(self) -> datetime:
        """
        Sugere melhor horário para postar no LinkedIn.

        Baseado em pesquisas:
        - Terça, Quarta, Quinta: melhores dias
        - 8h-10h ou 17h-18h: melhores horários
        """
        now = datetime.now(timezone.utc)

        # Próxima terça, quarta ou quinta
        days_ahead = (2 - now.weekday()) % 7  # Terça
        if days_ahead == 0:
            days_ahead = 7  # Próxima semana

        next_good_day = now + timedelta(days=days_ahead)

        # Hora: 8h30 (pico da manhã)
        optimal_time = next_good_day.replace(hour=8, minute=30, second=0)

        return optimal_time
```

### 4. ProfileAuditorAgent (O "Auditor de Perfil")

**Responsabilidade**: Auditar LinkedIn/GitHub e sugerir otimizações.

```python
class ProfileAuditorAgent:
    """
    Audita perfis externos e sugere melhorias alinhadas com branding.
    """

    def __init__(self, db: Session, user_id: int):
        self.database = db
        self.user_id = user_id
        self.pilares = self._load_branding_pilares()

    async def audit_linkedin_profile(self) -> ProfileAuditReport:
        """
        Audita perfil do LinkedIn.

        Analisa:
        - Título
        - Sobre
        - Experiência
        - Skills endossadas
        - Atividade recente
        """
        # Fetch LinkedIn data (via API ou scraping)
        linkedin_data = await self._fetch_linkedin_data()

        report = ProfileAuditReport(
            platform="linkedin",
            audit_date=datetime.now(timezone.utc),
            current_state=linkedin_data,
            issues=[],
            recommendations=[]
        )

        # Análise 1: Título
        titulo_issue = self._audit_titulo(linkedin_data["headline"])
        if titulo_issue:
            report.issues.append(titulo_issue)

        # Análise 2: Sobre
        sobre_issue = self._audit_sobre(linkedin_data["about"])
        if sobre_issue:
            report.issues.append(sobre_issue)

        # Análise 3: Alinhamento com pilares
        alignment_issue = self._audit_pilar_alignment(linkedin_data)
        if alignment_issue:
            report.issues.append(alignment_issue)

        # Análise 4: Atividade
        activity_issue = self._audit_activity(linkedin_data["recent_posts"])
        if activity_issue:
            report.issues.append(activity_issue)

        # Gera recomendações
        report.recommendations = self._generate_recommendations(report.issues)

        return report

    def _audit_titulo(self, current_headline: str) -> Optional[AuditIssue]:
        """
        Audita título do LinkedIn.

        Problemas comuns:
        - Título genérico demais ("Desenvolvedora")
        - Não reflete nível atual
        - Não menciona especializações
        """
        # Analisa projetos recentes para determinar nível
        recent_projects = self._get_recent_projects(months=6)

        seniority_level = self._infer_seniority_level(recent_projects)
        specializations = self._infer_specializations(recent_projects)

        # Compara com título atual
        if seniority_level == "senior" and "júnior" in current_headline.lower():
            return AuditIssue(
                severidade="alta",
                categoria="titulo_desatualizado",
                descricao=f"""
                Seu título diz "{current_headline}" mas 80% dos seus projetos
                dos últimos 6 meses foram classificados como nível Sênior ou
                Gestão de Produto.
                """,
                recomendacao=f"""
                Sugestão de novo título:
                "Engenheira de Software & Product Owner | IA, Robótica & Gestão de Produto"

                Isso reflete melhor suas responsabilidades reais.
                """
            )

        if not any(spec in current_headline for spec in specializations):
            return AuditIssue(
                severidade="media",
                categoria="titulo_generico",
                descricao=f"""
                Seu título não menciona especializações-chave: {', '.join(specializations)}
                """,
                recomendacao=f"""
                Considere adicionar ao título:
                "{current_headline} | {' · '.join(specializations[:2])}"
                """
            )

        return None

    def _audit_sobre(self, current_about: str) -> Optional[AuditIssue]:
        """
        Audita seção "Sobre" do LinkedIn.
        """
        issues = []

        # Verifica comprimento
        if len(current_about) < 300:
            issues.append("Seção 'Sobre' muito curta (< 300 caracteres)")

        # Verifica menção aos pilares
        pilares_mencionados = []
        for pilar in self.pilares:
            if any(keyword.lower() in current_about.lower() for keyword in pilar.keywords):
                pilares_mencionados.append(pilar.nome)

        if len(pilares_mencionados) < 2:
            issues.append(f"Apenas {len(pilares_mencionados)}/5 pilares de branding mencionados")

        # Verifica storytelling
        if "porque" not in current_about.lower() and "por que" not in current_about.lower():
            issues.append("Falta storytelling (seu 'porquê')")

        if issues:
            return AuditIssue(
                severidade="media",
                categoria="sobre_incompleto",
                descricao="\n".join(f"• {issue}" for issue in issues),
                recomendacao=self._generate_about_suggestion()
            )

        return None

    async def _generate_about_suggestion(self) -> str:
        """
        Gera sugestão de seção 'Sobre' usando LLM.
        """
        prompt = f"""
        Escreva uma seção "Sobre" poderosa para o LinkedIn de Samara.

        PILARES DE BRANDING:
        {json.dumps([p.nome for p in self.pilares], ensure_ascii=False)}

        CONQUISTAS RECENTES:
        {self._summarize_recent_achievements()}

        OBJETIVOS DE CARREIRA:
        Evoluir de Desenvolvedora/PO para CTO

        ESTRUTURA:
        1. Hook: Quem é você em 1 frase impactante
        2. O que faz: Suas especializações
        3. Como faz: Seu diferencial/abordagem
        4. Resultados: Conquistas mensuráveis
        5. Futuro: Onde está indo
        6. CTA: Como pessoas podem te contatar

        COMPRIMENTO: 400-600 palavras

        TOM: Profissional, confiante mas acessível

        Escreva a seção 'Sobre':
        """

        response = await self.llm.process(prompt)
        return response.content

    async def audit_github_profile(self) -> ProfileAuditReport:
        """
        Audita perfil do GitHub.

        Analisa:
        - README do perfil
        - Repositórios pinnados
        - Atividade (contributions)
        - README dos repos principais
        """
        github_data = await self._fetch_github_data()

        report = ProfileAuditReport(
            platform="github",
            audit_date=datetime.now(timezone.utc),
            current_state=github_data,
            issues=[],
            recommendations=[]
        )

        # Análise 1: README do perfil
        if not github_data.get("profile_readme"):
            report.issues.append(AuditIssue(
                severidade="alta",
                categoria="sem_profile_readme",
                descricao="Você não tem README de perfil no GitHub",
                recomendacao="""
                Crie um repositório com seu username (ex: samaracassie/samaracassie)
                e adicione README.md. Isso aparece no topo do seu perfil.

                Sugestão de estrutura:
                - Sobre você (2-3 linhas)
                - Áreas de expertise
                - Projetos em destaque
                - Como te contatar
                """
            ))

        # Análise 2: Repositórios pinnados
        pinned_repos = github_data.get("pinned_repositories", [])
        if len(pinned_repos) < 4:
            report.issues.append(AuditIssue(
                severidade="media",
                categoria="poucos_repos_pinnados",
                descricao=f"Apenas {len(pinned_repos)} repositórios pinnados",
                recomendacao="Pinne 6 repositórios que melhor representam suas skills"
            ))

        # Análise 3: READMEs dos repos
        repos_sem_readme = [
            repo["name"] for repo in github_data.get("repositories", [])
            if not repo.get("has_readme")
        ]
        if repos_sem_readme:
            report.issues.append(AuditIssue(
                severidade="baixa",
                categoria="repos_sem_readme",
                descricao=f"{len(repos_sem_readme)} repositórios sem README",
                recomendacao=f"Adicione READMEs aos repos: {', '.join(repos_sem_readme[:5])}"
            ))

        return report
```

### 5. TrendAnalysisAgent (O "Analista de Tendências") - BONUS

**Responsabilidade**: Analisar tendências do LinkedIn e sugerir conteúdo oportuno.

```python
class TrendAnalysisAgent:
    """
    Analisa tendências do LinkedIn para timing oportuno de conteúdo.
    """

    async def analyze_linkedin_trends(self) -> TrendReport:
        """
        Analisa o que está em alta no LinkedIn.

        Fontes:
        - Hashtags trending
        - Posts virais na sua rede
        - Tópicos do LinkedIn News
        """
        trends = await self._fetch_linkedin_trends()

        # Match com pilares de branding
        relevant_trends = []
        for trend in trends:
            for pilar in self.pilares:
                if self._is_trend_relevant(trend, pilar):
                    relevant_trends.append({
                        "trend": trend,
                        "pilar": pilar.nome,
                        "opportunity_score": self._calculate_opportunity_score(trend)
                    })

        # Gera sugestões de conteúdo oportunista
        content_suggestions = []
        for rel_trend in sorted(relevant_trends, key=lambda x: x["opportunity_score"], reverse=True)[:3]:
            suggestion = await self._generate_trend_based_content(rel_trend)
            content_suggestions.append(suggestion)

        return TrendReport(
            analyzed_at=datetime.now(timezone.utc),
            trending_topics=trends,
            relevant_trends=relevant_trends,
            content_suggestions=content_suggestions
        )

    def _is_trend_relevant(self, trend: Dict, pilar: BrandingPilar) -> bool:
        """
        Determina se tendência é relevante para pilar.
        """
        # Análise semântica
        similarity = self._calculate_semantic_similarity(
            trend["description"],
            pilar.descricao
        )

        return similarity > 0.6

    async def _generate_trend_based_content(self, rel_trend: Dict) -> ContentSuggestion:
        """
        Gera sugestão de conteúdo baseado em tendência.

        Exemplo:
        Tendência: "Agentic AI" está em alta
        Pilar: "Liderança de IA"
        Sugestão: Post sobre "Como Agentic AI se relaciona com seu TCC do Agente Wicked"
        """
        prompt = f"""
        Há uma tendência no LinkedIn que combina com a expertise de Samara.

        TENDÊNCIA:
        {rel_trend["trend"]["title"]}
        {rel_trend["trend"]["description"]}

        PILAR DE SAMARA:
        {rel_trend["pilar"]}

        CONQUISTAS RELEVANTES DE SAMARA:
        {self._find_relevant_achievements(rel_trend["pilar"])}

        Sugira um ângulo de conteúdo que:
        1. Surfe na tendência (oportunismo positivo)
        2. Mostre expertise de Samara
        3. Adicione valor único (não apenas repetir o hype)

        Sugestão:
        """

        response = await self.llm.process(prompt)

        return ContentSuggestion(
            titulo=response.title,
            descricao=response.description,
            pilar=rel_trend["pilar"],
            urgencia="alta",  # Tendências são temporais
            suggested_posting_date=datetime.now(timezone.utc) + timedelta(days=1)
        )
```

---

## 📊 Modelos de Dados

### Schema PostgreSQL

```sql
-- ========================================
-- Tabela: branding_pilares
-- ========================================
CREATE TABLE branding_pilares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Definição do pilar
    nome TEXT NOT NULL,  -- Ex: "Liderança de IA"
    descricao TEXT NOT NULL,
    keywords TEXT[] NOT NULL,  -- Ex: ['IA', 'machine learning', 'agentes']
    skills TEXT[],  -- Ex: ['Python', 'LangChain', 'GPT-4']

    -- Configuração
    ativo BOOLEAN DEFAULT TRUE,
    prioridade INTEGER DEFAULT 50,  -- 0-100
    cor_hex TEXT DEFAULT '#3B82F6',  -- Para visualização

    -- Meta
    objetivo TEXT,  -- Ex: "Posicionar como especialista em Agentic AI"
    publico_alvo TEXT[],  -- Ex: ['CTOs', 'Tech Leaders', 'Startups de IA']

    -- Métricas
    total_posts INTEGER DEFAULT 0,
    ultimo_post_em TIMESTAMP,

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pilares_user ON branding_pilares(user_id);
CREATE INDEX idx_pilares_ativo ON branding_pilares(ativo);


-- ========================================
-- Tabela: content_briefings
-- ========================================
CREATE TABLE content_briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Source
    tipo TEXT NOT NULL,  -- 'task_completion', 'project_completion', 'milestone', 'tcc', 'mentoria'
    source_type TEXT NOT NULL,  -- 'Task', 'Project', 'OKR', 'Document', 'Pupil'
    source_id UUID NOT NULL,  -- ID da entidade source

    -- Conteúdo
    titulo TEXT NOT NULL,
    contexto JSONB NOT NULL,  -- Dados completos da conquista
    tags TEXT[],

    -- Status
    status TEXT DEFAULT 'pending_strategy',  -- 'pending_strategy', 'strategy_defined', 'content_generated', 'published', 'archived'

    -- Timestamps
    detected_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,

    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_briefings_user ON content_briefings(user_id);
CREATE INDEX idx_briefings_status ON content_briefings(status);
CREATE INDEX idx_briefings_source ON content_briefings(source_type, source_id);


-- ========================================
-- Tabela: content_strategies
-- ========================================
CREATE TABLE content_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    briefing_id UUID REFERENCES content_briefings(id) ON DELETE CASCADE,

    -- Estratégia
    pilar_primario TEXT NOT NULL,  -- Referência a branding_pilares.nome
    pilar_secundario TEXT,
    angulo_narrativo TEXT NOT NULL,  -- O "spin" estratégico

    -- Segurança
    security_rules JSONB NOT NULL,  -- SecurityRules object

    -- Formato
    formatos TEXT[] NOT NULL,  -- ['linkedin_post', 'github_readme', 'portfolio_update']

    -- Direção editorial
    tom_voz TEXT NOT NULL,  -- 'profissional', 'inspirador', 'educativo', 'técnico'
    keywords TEXT[],
    cta TEXT,  -- Call-to-action

    -- Priorização
    prioridade INTEGER NOT NULL,  -- 0-100

    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_strategies_briefing ON content_strategies(briefing_id);
CREATE INDEX idx_strategies_pilar ON content_strategies(pilar_primario);


-- ========================================
-- Tabela: content_drafts
-- ========================================
CREATE TABLE content_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    briefing_id UUID REFERENCES content_briefings(id) ON DELETE CASCADE,
    strategy_id UUID REFERENCES content_strategies(id),

    -- Conteúdo
    formato TEXT NOT NULL,  -- 'linkedin_post', 'github_readme', 'portfolio_update', 'article_outline'
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,  -- O rascunho gerado

    -- Metadata
    metadata JSONB,  -- Hashtags, tempo sugerido, etc.

    -- Workflow
    status TEXT DEFAULT 'draft',  -- 'draft', 'reviewed', 'approved', 'published', 'rejected'
    feedback_usuario TEXT,  -- Se usuário deu feedback

    -- Versionamento
    versao INTEGER DEFAULT 1,
    parent_draft_id UUID REFERENCES content_drafts(id),  -- Se foi revisado

    -- Publishing
    publicado_em TIMESTAMP,
    plataforma TEXT,  -- 'linkedin', 'github', 'portfolio'
    url_publicacao TEXT,

    -- Métricas (se disponível via API)
    impressoes INTEGER,
    engajamento INTEGER,
    cliques INTEGER,

    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_drafts_briefing ON content_drafts(briefing_id);
CREATE INDEX idx_drafts_status ON content_drafts(status);
CREATE INDEX idx_drafts_formato ON content_drafts(formato);


-- ========================================
-- Tabela: profile_audits
-- ========================================
CREATE TABLE profile_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Plataforma
    platform TEXT NOT NULL,  -- 'linkedin', 'github'

    -- Snapshot do estado atual
    current_state JSONB NOT NULL,  -- Headline, about, repos, etc.

    -- Análise
    issues JSONB NOT NULL,  -- Array de AuditIssue
    recommendations JSONB NOT NULL,  -- Array de recomendações

    -- Score
    overall_score INTEGER,  -- 0-100

    -- Ações tomadas
    acoes_implementadas TEXT[],

    audit_date TIMESTAMP NOT NULL,
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audits_user ON profile_audits(user_id);
CREATE INDEX idx_audits_platform ON profile_audits(platform);
CREATE INDEX idx_audits_date ON profile_audits(audit_date DESC);


-- ========================================
-- Tabela: content_calendar
-- ========================================
CREATE TABLE content_calendar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    draft_id UUID REFERENCES content_drafts(id),

    -- Agendamento
    data_planejada DATE NOT NULL,
    hora_planejada TIME,  -- Opcional

    -- Status
    status TEXT DEFAULT 'scheduled',  -- 'scheduled', 'published', 'skipped'

    -- Notas
    notas TEXT,

    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_calendar_user ON content_calendar(user_id);
CREATE INDEX idx_calendar_data ON content_calendar(data_planejada);
CREATE INDEX idx_calendar_status ON content_calendar(status);
```

### Schemas Pydantic

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime, date
from uuid import UUID

# ========================================
# Branding Pilares
# ========================================

class BrandingPilarCreate(BaseModel):
    """Schema para criar pilar de branding"""
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: str = Field(..., min_length=10)
    keywords: List[str] = Field(..., min_items=3)
    skills: Optional[List[str]] = []
    objetivo: Optional[str] = None
    publico_alvo: Optional[List[str]] = []
    prioridade: int = Field(50, ge=0, le=100)

class BrandingPilar(BrandingPilarCreate):
    """Pilar de branding completo"""
    id: UUID
    user_id: int
    ativo: bool
    total_posts: int
    ultimo_post_em: Optional[datetime]
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Content Briefings
# ========================================

class ContentBriefing(BaseModel):
    """Briefing de oportunidade de conteúdo"""
    id: UUID
    user_id: int
    tipo: Literal[
        "task_completion", "project_completion",
        "milestone", "tcc", "mentoria", "certification"
    ]
    source_type: str
    source_id: UUID
    titulo: str
    contexto: Dict
    tags: List[str]
    status: str
    detected_at: datetime

    class Config:
        from_attributes = True


# ========================================
# Content Strategy
# ========================================

class SecurityRules(BaseModel):
    """Regras de segurança/confidencialidade"""
    anonimizar_nomes: bool = True
    anonimizar_empresas: bool = True
    nivel_detalhamento: Literal["baixo", "medio", "alto"] = "medio"
    topics_proibidos: List[str] = []
    foco_recomendado: Optional[str] = None

class ContentStrategy(BaseModel):
    """Estratégia de conteúdo"""
    id: UUID
    briefing_id: UUID
    pilar_primario: str
    pilar_secundario: Optional[str]
    angulo_narrativo: str
    security_rules: SecurityRules
    formatos: List[str]
    tom_voz: Literal["profissional", "inspirador", "educativo", "técnico"]
    keywords: List[str]
    cta: Optional[str]
    prioridade: int

    class Config:
        from_attributes = True


# ========================================
# Content Drafts
# ========================================

class ContentDraftCreate(BaseModel):
    """Criação de rascunho de conteúdo"""
    briefing_id: UUID
    strategy_id: Optional[UUID]
    formato: Literal[
        "linkedin_post", "github_readme",
        "portfolio_update", "article_outline", "content_series"
    ]
    titulo: str
    conteudo: str
    metadata: Optional[Dict] = {}

class ContentDraft(ContentDraftCreate):
    """Rascunho de conteúdo completo"""
    id: UUID
    status: str
    feedback_usuario: Optional[str]
    versao: int
    parent_draft_id: Optional[UUID]
    publicado_em: Optional[datetime]
    plataforma: Optional[str]
    url_publicacao: Optional[str]
    impressoes: Optional[int]
    engajamento: Optional[int]
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Profile Audits
# ========================================

class AuditIssue(BaseModel):
    """Problema identificado em auditoria"""
    severidade: Literal["baixa", "media", "alta"]
    categoria: str
    descricao: str
    recomendacao: str

class ProfileAuditReport(BaseModel):
    """Relatório de auditoria de perfil"""
    id: UUID
    user_id: int
    platform: Literal["linkedin", "github"]
    current_state: Dict
    issues: List[AuditIssue]
    recommendations: List[str]
    overall_score: Optional[int]
    audit_date: datetime

    class Config:
        from_attributes = True


# ========================================
# Content Calendar
# ========================================

class ContentCalendarEntry(BaseModel):
    """Entrada no calendário de conteúdo"""
    id: UUID
    user_id: int
    draft_id: UUID
    data_planejada: date
    hora_planejada: Optional[str]  # "08:30"
    status: Literal["scheduled", "published", "skipped"]
    notas: Optional[str]

    class Config:
        from_attributes = True
```

---

## 🔄 Fluxos de Trabalho

### Fluxo 1: Conquista no Estágio (Crise Lunelli)

```
┌────────────────────────────────────────────────────────────┐
│  FLUXO: RESOLUÇÃO DE CRISE → POST NO LINKEDIN              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. GATILHO                                                │
│     └─> Você marca OKR "Estabilidade Lunelli" como 95%    │
│     └─> Event Bus: EventType.OKR_UPDATED                   │
│                                                            │
│  2. CONTENT MINING AGENT                                   │
│     └─> Detecta que é OKR crítico                          │
│     └─> Coleta contexto:                                   │
│         • Notas do Strategic Advisor                       │
│         • Tarefas do Task Manager                          │
│         • Documentos do Archive                            │
│     └─> Cria ContentBriefing                               │
│                                                            │
│  3. CONTENT STRATEGY AGENT                                 │
│     └─> Match com pilar: "Gestão de Produto e Qualidade"  │
│     └─> Define ângulo:                                     │
│         "Importância de Definition of Done em projetos IA" │
│     └─> Aplica security rules:                             │
│         • NÃO mencionar: "Lunelli", "Breno", "crise"       │
│         • Foco: Processo, não problema                     │
│     └─> Define formatos: ["linkedin_post"]                 │
│     └─> Prioridade: 85/100 (alta)                          │
│                                                            │
│  4. CONTENT GENERATION AGENT                               │
│     └─> Gera rascunho de post LinkedIn                     │
│     └─> Estrutura:                                         │
│         • Hook: "Esta semana aprendi sobre qualidade..."   │
│         • Contexto: "Projetos de IA complexos"             │
│         • Insight: "DoD claro = estabilidade"              │
│         • Lição: "Qualidade se constrói no início"         │
│         • Hashtags: #GestaoDeProduto #IA #QA               │
│     └─> Salva como ContentDraft                            │
│                                                            │
│  5. NOTIFICAÇÃO PARA USUÁRIO                               │
│     └─> Charlee: "Samara, parabéns pelo marco no projeto! │
│                   Preparei um rascunho de post sobre QA.   │
│                   Quer revisar?"                           │
│                                                            │
│  6. USUÁRIO REVISA E APROVA                                │
│     └─> Usuário lê rascunho                                │
│     └─> Faz ajustes se necessário                          │
│     └─> Marca como "approved"                              │
│     └─> Copia para LinkedIn e publica                      │
│                                                            │
│  7. TRACKING PÓS-PUBLICAÇÃO                                │
│     └─> Usuário adiciona URL do post                       │
│     └─> Charlee monitora métricas (se API disponível)      │
│     └─> Aprende quais tipos de post funcionam melhor       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Resultado Real:**

```markdown
POST NO LINKEDIN:

🧠 Esta semana tive um aprendizado profundo sobre como a qualidade
é construída em projetos de IA.

Não basta o código funcionar; ele precisa ser robusto.

Em projetos de alta complexidade, um "Definition of Done" claro
não é burocracia — é o que garante a estabilidade.

Implementamos um processo onde cada entrega deve incluir:
• Testes unitários
• Tratamento de erros
• Validação funcional

Antes de ser considerada "pronta".

O resultado?
✅ Entrega mais estável
✅ Cliente mais confiante
✅ Equipe alinhada

A lição: Qualidade não se testa no final. Constrói-se no início.

#GestaoDeProduto #IA #EngenhariaDeSoftware #QA #TechLeadership

---

Impacto esperado:
• Posicionamento: Gestão de Produto
• Audiência: Tech Leaders, CTOs
• Mensagem: Profissionalismo e processos
```

### Fluxo 2: TCC (Agente Wicked)

```
┌────────────────────────────────────────────────────────────┐
│  FLUXO: DEFESA DO TCC → MÚLTIPLOS CONTEÚDOS                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. GATILHO                                                │
│     └─> Você faz upload de "TCC_Agente_Wicked_Final.pdf"  │
│     └─> Event Bus: EventType.ARCHIVE_DOCUMENT_ADDED        │
│                                                            │
│  2. CONTENT MINING AGENT                                   │
│     └─> Detecta: documento é TCC (tipo "TCC" na metadata) │
│     └─> Identifica: Big Rock "TCC" associado              │
│     └─> Coleta contexto:                                   │
│         • Título do TCC                                    │
│         • Abstract/Resumo                                  │
│         • Orientador (será anonimizado)                    │
│         • Repositório GitHub (se existir)                  │
│         • Notas do Charlee Archive                         │
│     └─> Cria ContentBriefing (tipo="tcc")                  │
│                                                            │
│  3. CONTENT STRATEGY AGENT                                 │
│     └─> TCC = evento MAJOR                                 │
│     └─> Match com pilares:                                 │
│         • Primário: "Liderança de IA"                      │
│         • Secundário: "Robótica & STEM"                    │
│     └─> Define múltiplos formatos:                         │
│         • linkedin_post (anúncio)                          │
│         • github_readme (repo do TCC)                      │
│         • portfolio_update (destaque)                      │
│         • article_outline (artigo técnico)                 │
│     └─> Prioridade: 95/100 (máxima)                        │
│                                                            │
│  4. CONTENT GENERATION AGENT                               │
│     └─> Gera 4 conteúdos diferentes:                       │
│                                                            │
│     A) LINKEDIN POST                                       │
│        "Depois de X meses de trabalho, orgulhosa de        │
│         apresentar meu TCC: 'Wicked: Arquitetura de        │
│         Agentes de IA para Gestão de Laboratórios'..."     │
│                                                            │
│     B) GITHUB README                                       │
│        Estrutura completa do repositório:                  │
│        • Visão geral da arquitetura                        │
│        • Diagramas de agentes                              │
│        • Como executar                                     │
│        • Resultados/benchmarks                             │
│        • Paper PDF                                         │
│                                                            │
│     C) PORTFOLIO UPDATE                                    │
│        Item destaque no portfólio:                         │
│        • Imagem: Diagrama da arquitetura                   │
│        • Descrição técnica                                 │
│        • Skills: Python, LangChain, Multi-Agent Systems    │
│        • Link para repo e paper                            │
│                                                            │
│     D) ARTICLE OUTLINE                                     │
│        Esboço de artigo técnico para Medium/Dev.to:        │
│        "Building Multi-Agent Systems for Lab Management:   │
│         Lessons from the Wicked Architecture"              │
│                                                            │
│  5. CONTENT CALENDAR                                       │
│     └─> Cria plano de publicação escalonado:               │
│         • Dia 1: Post LinkedIn (anúncio imediato)          │
│         • Dia 2: Atualizar GitHub README                   │
│         • Dia 3: Atualizar portfólio                       │
│         • Semana 2: Artigo técnico aprofundado             │
│                                                            │
│  6. NOTIFICAÇÃO PARA USUÁRIO                               │
│     └─> Charlee: "Parabéns pela defesa do TCC! 🎓         │
│                   Preparei 4 conteúdos para você:          │
│                   • Post LinkedIn (pronto)                 │
│                   • README GitHub (draft)                  │
│                   • Portfólio (sugestão)                   │
│                   • Artigo técnico (outline)               │
│                   Quer começar pelo LinkedIn?"             │
│                                                            │
│  7. PUBLICAÇÃO ESCALONADA                                  │
│     └─> Usuário aprova e publica cada peça                 │
│     └─> Momentum sustentado por 2 semanas                  │
│     └─> Máxima visibilidade para conquista importante      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Fluxo 3: Mentoria (Pupilo WickedBotz)

```
┌────────────────────────────────────────────────────────────┐
│  FLUXO: CONQUISTA DE PUPILO → POST DE LIDERANÇA            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. GATILHO                                                │
│     └─> Pupilo João completa primeiro projeto Python      │
│     └─> Você registra: "João finalizou To-Do List app!"   │
│     └─> Event Bus: EventType.PUPIL_MILESTONE               │
│                                                            │
│  2. CONTENT MINING AGENT                                   │
│     └─> Detecta milestone de mentoria                      │
│     └─> Coleta contexto:                                   │
│         • Nome do pupilo: "João" (será anonimizado)        │
│         • Conquista: "Primeiro projeto completo"           │
│         • Área: "Programação Python"                       │
│         • Nível: "Iniciante → Intermediário"               │
│         • Tempo de mentoria: "3 meses"                     │
│     └─> Cria ContentBriefing (tipo="mentoria")             │
│                                                            │
│  3. CONTENT STRATEGY AGENT                                 │
│     └─> Match com pilar: "Mentoria & Liderança"           │
│     └─> Define ângulo:                                     │
│         "Lições sobre ensinar programação para iniciantes" │
│     └─> Security rules:                                    │
│         • Anonimizar: "João" → "um aluno"                  │
│         • Foco: Processo de mentoria, não identidade       │
│     └─> Tom: Inspirador + Educativo                        │
│     └─> Formato: linkedin_post                             │
│     └─> Prioridade: 70/100                                 │
│                                                            │
│  4. CONTENT GENERATION AGENT                               │
│     └─> Gera post sobre liderança através de mentoria:     │
│                                                            │
│         "Uma das maiores alegrias de ser mentora:          │
│          Ver um aluno completar seu primeiro projeto.      │
│                                                            │
│          Há 3 meses, ele nunca tinha escrito uma linha     │
│          de Python. Hoje, construiu um To-Do List app      │
│          completo — com interface, banco de dados e        │
│          deploy funcional.                                 │
│                                                            │
│          O que aprendi ensinando programação:              │
│          • Paciência > Conhecimento técnico                │
│          • Projetos reais > Tutoriais teóricos             │
│          • Celebrar pequenas vitórias é essencial          │
│                                                            │
│          Ensinar me fez relembrar:                         │
│          A melhor forma de solidificar conhecimento        │
│          é explicar para alguém.                           │
│                                                            │
│          #Mentoria #WomenInTech #ProgramaçãoPython         │
│          #Liderança #WickedBotz"                           │
│                                                            │
│  5. PADRÃO DETECTADO (BONUS)                               │
│     └─> Após 5+ posts sobre mentoria, Charlee sugere:     │
│         "Samara, você já tem 5 histórias de mentoria.     │
│          Que tal criar uma série 'Lições de Mentoria'?    │
│          Posso compilar em artigo ou ebook."               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Sistema de Segurança

### Princípios de Confidencialidade

```python
PRINCIPIOS_SEGURANCA = {
    "regra_1_anonimizacao": {
        "o_que": "SEMPRE anonimizar nomes de pessoas e empresas",
        "como": [
            "Nomes de colegas → 'um colega desenvolvedor', 'uma colega de equipe'",
            "Nomes de clientes → 'um cliente', 'a empresa'",
            "Nomes de empresas → 'a organização', 'o projeto'",
            "Nomes de pupilos → 'um aluno', 'uma mentoranda'"
        ],
        "excecao": "Apenas você (Samara) pode ser nomeada"
    },

    "regra_2_foco_aprendizado": {
        "o_que": "Focar no INSIGHT, não no fato específico",
        "exemplo_ruim": "O Breno atrasou o projeto Lunelli",
        "exemplo_bom": "A importância de processos de QA em projetos complexos",
        "principio": "Ensine algo universal, não conte fofoca"
    },

    "regra_3_valores_financeiros": {
        "o_que": "NUNCA mencionar valores de contratos/salários",
        "permitido": "Mencionar crescimento percentual (ex: 'aumentei receita em 40%')",
        "proibido": "Valores absolutos (ex: 'projeto de R$ 50.000')"
    },

    "regra_4_codigo_proprietario": {
        "o_que": "Não compartilhar código proprietário de clientes",
        "permitido": "Arquitetura conceitual, padrões de design",
        "proibido": "Implementação específica de cliente"
    },

    "regra_5_reframe_negativo": {
        "o_que": "Transformar problemas em insights",
        "como": [
            "Crise → Aprendizado sobre gestão de crise",
            "Bug grave → Importância de testes",
            "Conflito → Lição sobre comunicação"
        ],
        "principio": "Positivo vende, negativo queima pontes"
    }
}
```

### Sistema de Validação

```python
class SecurityValidator:
    """
    Valida conteúdo antes de ser apresentado ao usuário.
    """

    def validate_content(self, draft: ContentDraft) -> ValidationResult:
        """
        Valida draft contra regras de segurança.
        """
        issues = []

        # Check 1: Detecta nomes próprios
        names_found = self._detect_proper_names(draft.conteudo)
        if names_found:
            issues.append(ValidationIssue(
                severidade="alta",
                tipo="nome_proprio_detectado",
                detalhes=f"Nomes encontrados: {', '.join(names_found)}",
                sugestao="Substitua por termos genéricos"
            ))

        # Check 2: Detecta valores financeiros
        financial_values = self._detect_financial_values(draft.conteudo)
        if financial_values:
            issues.append(ValidationIssue(
                severidade="alta",
                tipo="valor_financeiro",
                detalhes=f"Valores encontrados: {', '.join(financial_values)}",
                sugestao="Remova valores absolutos ou use percentuais"
            ))

        # Check 3: Detecta linguagem negativa excessiva
        negativity_score = self._calculate_negativity_score(draft.conteudo)
        if negativity_score > 0.3:
            issues.append(ValidationIssue(
                severidade="media",
                tipo="tom_negativo",
                detalhes=f"Score de negatividade: {negativity_score:.0%}",
                sugestao="Reframe para focar em aprendizados positivos"
            ))

        # Check 4: Detecta auto-promoção excessiva
        self_promo_score = self._calculate_self_promotion_score(draft.conteudo)
        if self_promo_score > 0.5:
            issues.append(ValidationIssue(
                severidade="baixa",
                tipo="auto_promocao_excessiva",
                detalhes=f"Score de auto-promoção: {self_promo_score:.0%}",
                sugestao="Balance com mais conteúdo educativo"
            ))

        # Check 5: Verifica presença de hashtags
        if draft.formato == "linkedin_post":
            hashtags = re.findall(r'#\w+', draft.conteudo)
            if not hashtags:
                issues.append(ValidationIssue(
                    severidade="baixa",
                    tipo="sem_hashtags",
                    detalhes="Post sem hashtags",
                    sugestao="Adicione 3-5 hashtags relevantes"
                ))

        return ValidationResult(
            aprovado=not any(i.severidade == "alta" for i in issues),
            issues=issues,
            score_geral=self._calculate_overall_score(issues)
        )

    def _detect_proper_names(self, text: str) -> List[str]:
        """
        Detecta nomes próprios usando NER.
        """
        # Implementação com spaCy ou similar
        doc = nlp(text)
        names = [
            ent.text for ent in doc.ents
            if ent.label_ == "PERSON" and ent.text != "Samara"
        ]
        return names

    def _detect_financial_values(self, text: str) -> List[str]:
        """
        Detecta valores financeiros (R$, USD, etc).
        """
        pattern = r'R\$\s*[\d.,]+|USD?\s*[\d.,]+|\$\s*[\d.,]+'
        return re.findall(pattern, text)

    def _calculate_negativity_score(self, text: str) -> float:
        """
        Calcula score de negatividade usando análise de sentimento.
        """
        negative_keywords = [
            "problema", "crise", "erro", "falha", "atraso",
            "ruim", "terrível", "horrível", "desastre"
        ]

        text_lower = text.lower()
        negative_count = sum(
            text_lower.count(keyword) for keyword in negative_keywords
        )

        total_words = len(text.split())
        return negative_count / max(total_words, 1)

    def _calculate_self_promotion_score(self, text: str) -> float:
        """
        Calcula score de auto-promoção.
        """
        self_promo_keywords = [
            "eu fiz", "eu criei", "eu desenvolvi", "eu implementei",
            "meu projeto", "minha solução", "meu trabalho"
        ]

        text_lower = text.lower()
        promo_count = sum(
            text_lower.count(keyword) for keyword in self_promo_keywords
        )

        total_sentences = len(text.split('.'))
        return promo_count / max(total_sentences, 1)
```

---

## 🔌 API Endpoints

```python
# ========================================
# Branding Pilares
# ========================================

@router.post("/api/v1/branding/pilares")
def create_pilar(
    pilar: BrandingPilarCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria novo pilar de branding"""
    ...

@router.get("/api/v1/branding/pilares")
def list_pilares(
    ativo_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista pilares de branding"""
    ...

@router.patch("/api/v1/branding/pilares/{pilar_id}")
def update_pilar(
    pilar_id: UUID,
    updates: Dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza pilar de branding"""
    ...


# ========================================
# Content Briefings & Drafts
# ========================================

@router.get("/api/v1/branding/briefings")
def list_briefings(
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista oportunidades de conteúdo detectadas"""
    ...

@router.get("/api/v1/branding/drafts")
def list_drafts(
    status: str = "draft",
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista rascunhos de conteúdo"""
    ...

@router.get("/api/v1/branding/drafts/{draft_id}")
def get_draft(
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém rascunho específico"""
    ...

@router.post("/api/v1/branding/drafts/{draft_id}/approve")
def approve_draft(
    draft_id: UUID,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Aprova rascunho para publicação"""
    ...

@router.post("/api/v1/branding/drafts/{draft_id}/reject")
def reject_draft(
    draft_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Rejeita rascunho"""
    ...

@router.post("/api/v1/branding/drafts/{draft_id}/request-revision")
def request_revision(
    draft_id: UUID,
    feedback: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Solicita revisão do rascunho"""
    # Cria nova versão do draft com feedback
    ...


# ========================================
# Content Calendar
# ========================================

@router.get("/api/v1/branding/calendar")
def get_calendar(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém calendário de conteúdo"""
    ...

@router.post("/api/v1/branding/calendar")
def schedule_content(
    draft_id: UUID,
    data_planejada: date,
    hora_planejada: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Agenda conteúdo para publicação"""
    ...


# ========================================
# Profile Audits
# ========================================

@router.post("/api/v1/branding/audits/linkedin")
async def audit_linkedin(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Executa auditoria do LinkedIn"""
    auditor = ProfileAuditorAgent(db, current_user.id)
    report = await auditor.audit_linkedin_profile()
    return report

@router.post("/api/v1/branding/audits/github")
async def audit_github(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Executa auditoria do GitHub"""
    auditor = ProfileAuditorAgent(db, current_user.id)
    report = await auditor.audit_github_profile()
    return report

@router.get("/api/v1/branding/audits")
def list_audits(
    platform: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lista auditorias anteriores"""
    ...


# ========================================
# Dashboard & Analytics
# ========================================

@router.get("/api/v1/branding/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dashboard geral de branding.

    Retorna:
    - Drafts pendentes de revisão
    - Próximos conteúdos agendados
    - Performance de posts anteriores
    - Saúde dos pilares de branding
    - Últimas conquistas detectadas
    """
    ...
```

---

## 🔗 Integrações

### Event Bus Events

```python
# Eventos que Charlee Brand OUVE
EventType.TASK_COMPLETED = "task.completed"
EventType.PROJECT_COMPLETED = "projects.freelance.completed"
EventType.MILESTONE_ACHIEVED = "okr.milestone.achieved"
EventType.ARCHIVE_DOCUMENT_ADDED = "archive.document.added"
EventType.PUPIL_MILESTONE = "relationships.pupil.milestone"

# Eventos que Charlee Brand PUBLICA
EventType.CONTENT_OPPORTUNITY_DETECTED = "brand.opportunity.detected"
EventType.CONTENT_DRAFT_READY = "brand.draft.ready"
EventType.CONTENT_PUBLISHED = "brand.content.published"
EventType.PROFILE_AUDIT_COMPLETED = "brand.audit.completed"
```

### Integração com Charlee Archive

```python
@event_bus.subscribe(EventType.ARCHIVE_DOCUMENT_ADDED)
async def on_document_added(event: ArchiveDocumentEvent):
    """
    Quando documento é adicionado ao Archive, verifica se é oportunidade de branding.
    """
    document = await archive_service.get_document(event.document_id)

    # Tipos de documentos relevantes
    if document.tipo in ["TCC", "Certificação", "Artigo Publicado", "Apresentação"]:
        mining_agent = ContentMiningAgent(db, event_bus)
        await mining_agent.on_document_added(event)
```

### Integração com Charlee Projects (Freelancer)

```python
@event_bus.subscribe(EventType.PROJECT_COMPLETED)
async def on_project_completed(event: ProjectCompletedEvent):
    """
    Quando projeto freelance é concluído, considera para portfólio/LinkedIn.
    """
    mining_agent = ContentMiningAgent(db, event_bus)
    await mining_agent.on_project_completed(event)
```

### Integração com Charlee Diplomat (Mentorias)

```python
@event_bus.subscribe(EventType.PUPIL_MILESTONE)
async def on_pupil_milestone(event: PupilMilestoneEvent):
    """
    Quando pupilo atinge marco, cria oportunidade de branding através de liderança.
    """
    mining_agent = ContentMiningAgent(db, event_bus)
    await mining_agent.on_pupil_milestone(event)
```

---

## 🛣️ Roadmap

### Fase 1: MVP - Detecção e Geração Manual ✅
- [ ] Implementar ContentMiningAgent
- [ ] Implementar ContentStrategyAgent
- [ ] Implementar ContentGenerationAgent
- [ ] Criar tabelas de dados
- [ ] API básica (drafts, pilares)
- [ ] Interface CLI para aprovar drafts
- [ ] Teste com 1 pilar de branding

### Fase 2: Automação de Workflow
- [ ] Implementar ProfileAuditorAgent
- [ ] Sistema de Content Calendar
- [ ] Notificações proativas de drafts prontos
- [ ] Integração com todos eventos relevantes
- [ ] Dashboard de branding

### Fase 3: Inteligência Avançada
- [ ] TrendAnalysisAgent
- [ ] Machine Learning para otimizar match pilar-conquista
- [ ] A/B testing de ângulos narrativos
- [ ] Análise de performance de posts publicados
- [ ] Recomendações baseadas em dados

### Fase 4: Integrações Externas
- [ ] LinkedIn API (publicação automática)
- [ ] GitHub API (atualização de READMEs)
- [ ] Analytics (rastreamento de métricas)
- [ ] Zapier/Make integration
- [ ] Buffer/Hootsuite integration (opcional)

### Fase 5: Features Avançadas
- [ ] Geração de imagens para posts (Dall-E/Midjourney)
- [ ] Vídeos curtos (roteiros para Reels/TikTok)
- [ ] Séries de conteúdo (multi-post threads)
- [ ] Ebooks/Whitepapers compilados
- [ ] Newsletter automation

---

## 📚 Referências

### Personal Branding

- **Books**:
  - *Crushing It!* - Gary Vaynerchuk
  - *Building a StoryBrand* - Donald Miller
  - *Show Your Work!* - Austin Kleon

- **Artigos**:
  - [LinkedIn's Guide to Personal Branding](https://business.linkedin.com/marketing-solutions/blog)
  - [How to Build Your Personal Brand on LinkedIn](https://www.forbes.com/sites/forbescoachescouncil/)

### Content Marketing

- **Resources**:
  - HubSpot Blog
  - Content Marketing Institute
  - Ann Handley's newsletters

### Technical Writing

- **Guides**:
  - [Google Technical Writing Courses](https://developers.google.com/tech-writing)
  - [Write the Docs](https://www.writethedocs.org/)

---

**Versão**: 1.0
**Data**: 2025-11-18
**Mantenedor**: Sistema Charlee - Módulo Brand
**Status**: 📝 Documento de Planejamento

---

**Desenvolvido com ❤️ por Samara Cassie**

*"Suas conquistas só são invisíveis até você compartilhá-las estrategicamente."*
