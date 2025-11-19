# 👔 Charlee Wardrobe - Sistema Inteligente de Guarda-Roupa

> **Versão**: 1.0 (Planejamento)
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V4.x - Wardrobe Management & Decision Automation

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Agentes Especializados](#agentes-especializados)
4. [Modelos de Dados](#modelos-de-dados)
5. [Regras de Estilo](#regras-de-estilo)
6. [Fluxos de Trabalho](#fluxos-de-trabalho)
7. [API Endpoints](#api-endpoints)
8. [Integrações](#integrações)
9. [Casos de Uso](#casos-de-uso)
10. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

O **Charlee Wardrobe** transforma o Charlee de um assistente de produtividade em um **assistente de estilo de vida completo**, erradicando uma das maiores fontes diárias de fadiga de decisão: **"O que eu vou vestir?"**

### O Problema: Vazamento de Tokens Mentais

```
Decisão Diária de Roupa = Múltiplas Variáveis Complexas
```

Cada manhã, a escolha do que vestir consome tokens mentais valiosos:

1. **🧺 Logística**: O que está limpo? Para lavar? Para consertar?
2. **📅 Contexto**: Que compromissos tenho hoje? Reunião? Faculdade? Evento?
3. **🎨 Estilo**: O que combina? Cores? Estampas? Materiais?
4. **⚡ Energia**: Como me sinto? Quero conforto ou look poderoso?

**Impacto**: Em uma rotina de alta performance (acordar às 5h), gastar energia mental nessa decisão é um **desperdício de capacidade cognitiva** que deveria ser alocada para trabalho estratégico.

### A Solução: Planejamento Semanal Automatizado

```
┌─────────────────────────────────────────────────────┐
│         ANTES: Decisão Diária (5-15 min)            │
│  ❌ 7 decisões/semana × 10 min = 70 min gastos     │
│  ❌ Fadiga mental toda manhã                       │
│  ❌ Possibilidade de atraso                        │
│                                                     │
│         DEPOIS: Sessão Semanal (1× 15 min)          │
│  ✅ 1 sessão prazerosa de planejamento             │
│  ✅ 0 decisões matinais (piloto automático)        │
│  ✅ Economia de 55 min/semana                      │
│  ✅ Looks otimizados para contexto + energia       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Características Principais

1. **📸 Catalogação Inteligente**: Sistema de inventário digital de roupas
2. **🤖 Planejamento Proativo**: Sugestão automática de looks semanais
3. **🎨 Regras de Estilo**: Aplica combinações de cores, estampas e ocasiões
4. **🌸 Context-Aware**: Adapta looks baseado em calendário, ciclo e energia
5. **🔄 Gestão de Status**: Rastreamento de roupas limpas, para lavar, para consertar
6. **📋 Lista de Compras Automática**: Cria tarefas quando peças precisam ser substituídas

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────┐
│              CHARLEE WARDROBE SYSTEM                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   1. INVENTORY LAYER (Data Management)      │   │
│  │  • roupas (peças individuais)               │   │
│  │  • looks (combinações salvas)               │   │
│  │  • look_items (relação N-M)                 │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   2. INTELLIGENCE LAYER (Agents + Rules)    │   │
│  │  • Wardrobe Manager (planejamento)          │   │
│  │  • Style Rules Engine (cores, estampas)     │   │
│  │  • Context Analyzer (calendário + ciclo)    │   │
│  │  • Vision Cataloger (V3+: fotos → dados)    │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │   3. PLANNING LAYER (Execution)             │   │
│  │  • plano_semanal_looks (plano aprovado)     │   │
│  │  • Morning Briefing integration             │   │
│  │  • Feedback loop (melhoria contínua)        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Fluxo de Planejamento Semanal

```
Domingo à noite (ou quando preferir)
         ↓
┌─────────────────────────────────────────────────────┐
│  $ charlee wardrobe plan-week                       │
└────────────────────┬────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
┌─────────────────┐      ┌─────────────────┐
│ Wardrobe Manager│      │ Context Analyzer│
│ busca roupas    │      │ consulta agenda │
│ disponíveis     │      │ + ciclo         │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └────────┬───────────────┘
                  ↓
         ┌────────────────┐
         │ Style Rules    │
         │ (combinar tudo)│
         └────────┬───────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│  Charlee apresenta: "Plano de Looks da Semana"     │
│  (usuário aprova ou ajusta)                        │
└────────────────────┬────────────────────────────────┘
                     ↓
         ┌────────────────────┐
         │ Salva no DB:       │
         │ plano_semanal_looks│
         └────────────────────┘
```

---

## 🤖 Agentes Especializados

### 1. Wardrobe Manager (Agente Principal)

**Responsabilidade**: Gerenciar inventário de roupas e gerar planos semanais de looks.

#### Lógica de Planejamento

```python
class WardrobeManager:
    """
    Agente especialista em gestão de guarda-roupa e estilo.
    """

    async def plan_weekly_outfits(
        self,
        user_id: int,
        week_start: datetime
    ) -> WeeklyOutfitPlan:
        """
        Gera plano completo de looks para a semana.

        Steps:
        1. Busca roupas disponíveis (status='limpa')
        2. Consulta calendário para contexto de cada dia
        3. Consulta Wellness Coach para fase do ciclo
        4. Aplica regras de estilo (cores, estampas)
        5. Filtra por ocasião (casual, profissional, etc.)
        6. Evita repetição de peças
        7. Gera sugestões e apresenta ao usuário
        """
        outfits = []

        for day_offset in range(7):
            date = week_start + timedelta(days=day_offset)

            # 1. Consulta contexto do dia
            context = await self._get_day_context(user_id, date)

            # 2. Filtra roupas disponíveis
            available_clothes = await self._get_available_clothes(
                user_id=user_id,
                occasion=context.occasion,
                season=context.season,
                weather=context.weather
            )

            # 3. Gera combinações válidas
            combinations = self._generate_combinations(
                available_clothes,
                context
            )

            # 4. Aplica regras de estilo
            valid_combinations = self._apply_style_rules(combinations)

            # 5. Evita repetição
            valid_combinations = self._filter_recent_usage(
                valid_combinations,
                used_items=outfits
            )

            # 6. Seleciona melhor combinação
            outfit = await self._select_best_outfit(
                valid_combinations,
                context
            )

            outfits.append(outfit)

        return WeeklyOutfitPlan(
            week_start=week_start,
            outfits=outfits,
            status="pending_approval"
        )

    async def _get_day_context(
        self,
        user_id: int,
        date: datetime
    ) -> DayContext:
        """
        Coleta contexto completo para um dia específico.
        """
        # 1. Calendário
        events = await calendar_service.get_events(user_id, date)
        occasion = self._determine_occasion(events)

        # 2. Wellness (ciclo menstrual)
        wellness = await wellness_coach.get_energy_context(user_id, date)

        # 3. Clima (API externa)
        weather = await weather_api.get_forecast(date)

        # 4. Estação do ano
        season = self._get_season(date)

        return DayContext(
            date=date,
            occasion=occasion,
            events=events,
            cycle_phase=wellness.cycle_phase,
            energy_level=wellness.energy_percentage,
            weather=weather,
            season=season
        )

    def _determine_occasion(self, events: List[CalendarEvent]) -> str:
        """
        Determina ocasião do dia baseado em eventos.

        Prioridade: formal > profissional > casual
        """
        if any(e.is_formal for e in events):
            return "formal"  # Reunião importante

        if any(e.is_professional for e in events):
            return "profissional"  # Trabalho normal

        if any(e.is_sport for e in events):
            return "esporte"  # Academia, caminhada

        return "casual"  # Dia normal

    def _generate_combinations(
        self,
        clothes: List[Roupa],
        context: DayContext
    ) -> List[OutfitCombination]:
        """
        Gera todas as combinações possíveis de roupas.
        """
        combinations = []

        # Separa por tipo
        tops = [c for c in clothes if c.tipo in ["camiseta", "blusa", "camisa"]]
        bottoms = [c for c in clothes if c.tipo in ["calca", "saia", "shorts"]]
        shoes = [c for c in clothes if c.tipo in ["tenis", "sapato", "sandalia"]]

        # Combina tudo
        for top in tops:
            for bottom in bottoms:
                for shoe in shoes:
                    combination = OutfitCombination(
                        items=[top, bottom, shoe],
                        occasion=context.occasion,
                        date=context.date
                    )
                    combinations.append(combination)

        return combinations

    def _apply_style_rules(
        self,
        combinations: List[OutfitCombination]
    ) -> List[OutfitCombination]:
        """
        Filtra combinações inválidas baseado em regras de estilo.
        """
        valid = []

        for combo in combinations:
            # Regra 1: Não misturar estampas diferentes
            if not self._check_pattern_rule(combo):
                continue

            # Regra 2: Pelo menos uma peça neutra
            if not self._check_neutral_rule(combo):
                continue

            # Regra 3: Cores complementares
            if not self._check_color_harmony(combo):
                continue

            valid.append(combo)

        return valid

    def _check_pattern_rule(self, combo: OutfitCombination) -> bool:
        """
        Regra: Não combinar duas estampas diferentes.

        Permitido:
        - Sólido + sólido
        - Sólido + estampado
        - Estampado (mesmo tipo) + sólido

        Proibido:
        - Listrado + floral
        - Xadrez + listrado
        """
        patterns = [item.estampa for item in combo.items]

        # Remove sólidos
        non_solid = [p for p in patterns if p != "solida"]

        # Se tem 2+ estampas diferentes, inválido
        if len(set(non_solid)) > 1:
            return False

        return True

    def _check_neutral_rule(self, combo: OutfitCombination) -> bool:
        """
        Regra: Pelo menos uma peça neutra (exceto looks casuais).

        Cores neutras: branco, preto, cinza, bege, marrom
        """
        if combo.occasion == "casual":
            return True  # Casual pode ser mais livre

        neutral_colors = ["branco", "preto", "cinza", "bege", "marrom"]

        for item in combo.items:
            if item.cor_primaria in neutral_colors:
                return True
            if item.paleta_cor == "neutra":
                return True

        return False

    def _check_color_harmony(self, combo: OutfitCombination) -> bool:
        """
        Regra: Verifica harmonia de cores.

        Lógica simplificada:
        - Monocromático (mesma cor)
        - Complementar (cores opostas)
        - Análogo (cores vizinhas)
        - Neutro + qualquer cor
        """
        colors = [item.cor_primaria for item in combo.items]

        # Se tem cor neutra, sempre válido
        neutral_colors = ["branco", "preto", "cinza", "bege"]
        if any(c in neutral_colors for c in colors):
            return True

        # Monocromático (mesma cor ou tons)
        if len(set(colors)) == 1:
            return True

        # TODO: Implementar lógica de cores complementares/análogas
        # Por enquanto, aceita qualquer combinação com neutro

        return True

    async def _select_best_outfit(
        self,
        combinations: List[OutfitCombination],
        context: DayContext
    ) -> PlannedOutfit:
        """
        Usa LLM para escolher a melhor combinação.
        """
        if not combinations:
            raise ValueError("Nenhuma combinação válida encontrada")

        # Se só tem 1, retorna ela
        if len(combinations) == 1:
            return PlannedOutfit(
                date=context.date,
                combination=combinations[0],
                reasoning="Única combinação disponível"
            )

        # Usa LLM para escolher entre múltiplas opções
        prompt = f"""
        Você é um personal stylist. Escolha o melhor look para este contexto:

        Data: {context.date.strftime('%d/%m/%Y (%A)')}
        Ocasião: {context.occasion}
        Eventos: {', '.join([e.title for e in context.events])}
        Clima: {context.weather.temperature}°C, {context.weather.condition}
        Fase do ciclo: {context.cycle_phase} (energia {context.energy_level}%)

        Combinações disponíveis:
        {self._format_combinations_for_llm(combinations)}

        Critérios de escolha:
        1. Adequação à ocasião
        2. Conforto (se energia baixa)
        3. Estilo e harmonia de cores
        4. Clima apropriado

        Retorne:
        - Número da combinação escolhida (1-{len(combinations)})
        - Breve justificativa (1 frase)
        """

        response = await self.llm.process(prompt)

        selected = combinations[response.choice_index - 1]

        return PlannedOutfit(
            date=context.date,
            combination=selected,
            reasoning=response.justification,
            occasion=context.occasion,
            cycle_phase=context.cycle_phase
        )

    def _format_combinations_for_llm(
        self,
        combinations: List[OutfitCombination]
    ) -> str:
        """
        Formata combinações para o LLM analisar.
        """
        formatted = []

        for i, combo in enumerate(combinations, 1):
            items_desc = " + ".join([
                f"{item.nome} ({item.tipo}, {item.cor_primaria})"
                for item in combo.items
            ])
            formatted.append(f"{i}. {items_desc}")

        return "\n".join(formatted)
```

---

### 2. Style Rules Engine (Sistema de Regras)

**Responsabilidade**: Aplicar regras automáticas de estilo, cores e ocasiões.

```python
class StyleRulesEngine:
    """
    Motor de regras de estilo para validação de combinações.
    """

    def __init__(self):
        # Matriz de harmonia de cores (simplificada)
        self.color_harmony = {
            "vermelho": ["branco", "preto", "cinza", "azul-marinho"],
            "azul": ["branco", "preto", "cinza", "bege"],
            "verde": ["branco", "preto", "marrom", "bege"],
            "amarelo": ["branco", "preto", "azul-marinho"],
            "rosa": ["branco", "preto", "cinza", "azul"],
            # Neutros combinam com tudo
            "branco": "*",
            "preto": "*",
            "cinza": "*",
            "bege": "*",
        }

    def validate_combination(
        self,
        items: List[Roupa],
        occasion: str,
        cycle_phase: str
    ) -> ValidationResult:
        """
        Valida uma combinação completa de roupas.
        """
        errors = []
        warnings = []

        # Regra 1: Estampas
        pattern_check = self._validate_patterns(items)
        if not pattern_check.valid:
            errors.append(pattern_check.message)

        # Regra 2: Cores
        color_check = self._validate_colors(items)
        if not color_check.valid:
            warnings.append(color_check.message)

        # Regra 3: Ocasião
        occasion_check = self._validate_occasion(items, occasion)
        if not occasion_check.valid:
            errors.append(occasion_check.message)

        # Regra 4: Conforto (ciclo menstrual)
        comfort_check = self._validate_comfort(items, cycle_phase)
        if not comfort_check.valid:
            warnings.append(comfort_check.message)

        return ValidationResult(
            valid=(len(errors) == 0),
            errors=errors,
            warnings=warnings
        )

    def _validate_patterns(self, items: List[Roupa]) -> RuleCheck:
        """
        Valida regra de estampas.

        PROIBIDO: Misturar 2+ estampas diferentes
        PERMITIDO: Sólido + qualquer coisa
        """
        patterns = [item.estampa for item in items]
        non_solid_patterns = [p for p in patterns if p != "solida"]

        if len(set(non_solid_patterns)) > 1:
            return RuleCheck(
                valid=False,
                message=f"Evite misturar estampas: {', '.join(set(non_solid_patterns))}"
            )

        return RuleCheck(valid=True)

    def _validate_colors(self, items: List[Roupa]) -> RuleCheck:
        """
        Valida harmonia de cores.
        """
        colors = [item.cor_primaria for item in items]

        # Se todas as cores se harmonizam, ok
        for i, color1 in enumerate(colors):
            for color2 in colors[i+1:]:
                if not self._colors_match(color1, color2):
                    return RuleCheck(
                        valid=False,
                        message=f"Cores {color1} e {color2} não harmonizam bem"
                    )

        return RuleCheck(valid=True)

    def _colors_match(self, color1: str, color2: str) -> bool:
        """
        Verifica se duas cores combinam.
        """
        # Neutros combinam com tudo
        if color1 in ["branco", "preto", "cinza", "bege"]:
            return True
        if color2 in ["branco", "preto", "cinza", "bege"]:
            return True

        # Mesma cor
        if color1 == color2:
            return True

        # Consulta matriz de harmonia
        harmonious_colors = self.color_harmony.get(color1, [])
        if harmonious_colors == "*" or color2 in harmonious_colors:
            return True

        return False

    def _validate_occasion(
        self,
        items: List[Roupa],
        occasion: str
    ) -> RuleCheck:
        """
        Valida se peças são apropriadas para a ocasião.

        REGRA CRÍTICA: NUNCA peça 'casual' em evento 'formal'
        """
        for item in items:
            if occasion == "formal" and "casual" in item.ocasioes:
                # Se a peça é APENAS casual, erro
                if item.ocasioes == ["casual"]:
                    return RuleCheck(
                        valid=False,
                        message=(
                            f"'{item.nome}' é muito casual para ocasião formal"
                        )
                    )

            # Aviso se não é ideal
            if occasion not in item.ocasioes:
                return RuleCheck(
                    valid=False,
                    message=(
                        f"'{item.nome}' não é marcada para ocasião '{occasion}'"
                    )
                )

        return RuleCheck(valid=True)

    def _validate_comfort(
        self,
        items: List[Roupa],
        cycle_phase: str
    ) -> RuleCheck:
        """
        Valida conforto baseado na fase do ciclo.

        RECOMENDAÇÃO: Em fase menstrual, priorizar algodão e conforto
        """
        if cycle_phase not in ["menstrual", "lutea"]:
            return RuleCheck(valid=True)  # Sem restrições

        # Verifica se há peça confortável
        has_comfort = any(
            item.material in ["algodao", "moletom"] or
            "conforto" in item.tags
            for item in items
        )

        if not has_comfort:
            return RuleCheck(
                valid=True,  # Warning, não erro
                message=(
                    f"Considere peças mais confortáveis durante {cycle_phase}."
                )
            )

        return RuleCheck(valid=True)
```

---

### 3. Vision Cataloger (V3+ - Futuro)

**Responsabilidade**: Automatizar catalogação via análise de fotos.

```python
class VisionCataloger:
    """
    Agente que usa Vision API para catalogar roupas automaticamente.

    Roadmap: V3+
    """

    async def catalog_from_photo(
        self,
        user_id: int,
        image_file: UploadFile
    ) -> RoupaCreate:
        """
        Analisa foto de roupa e extrai atributos automaticamente.

        Usa: Claude 3.5 Sonnet (Vision) ou GPT-4o Vision
        """
        # 1. Upload da imagem
        image_url = await storage_service.upload_image(
            user_id,
            image_file,
            folder="wardrobe"
        )

        # 2. Análise com Vision API
        prompt = """
        Você é um especialista em moda. Analise esta foto de roupa e extraia:

        1. Tipo (camiseta, blusa, calça, saia, vestido, tênis, sapato, etc.)
        2. Cor primária
        3. Cor secundária (se houver)
        4. Estampa (solida, listrada, floral, xadrez, etc.)
        5. Material aparente (algodão, seda, jeans, couro, etc.)
        6. Ocasiões apropriadas (casual, profissional, formal, esporte)
        7. Paleta de cor (neutra, quente, fria, vibrante)

        Retorne em JSON estruturado.
        """

        analysis = await self.vision_api.analyze_image(
            image_url=image_url,
            prompt=prompt
        )

        # 3. Cria objeto de roupa
        roupa_data = RoupaCreate(
            nome=analysis.get("nome_sugerido", f"Peça #{random.randint(1000, 9999)}"),
            tipo=analysis["tipo"],
            cor_primaria=analysis["cor_primaria"],
            cor_secundaria=analysis.get("cor_secundaria"),
            estampa=analysis["estampa"],
            material=analysis["material"],
            ocasioes=analysis["ocasioes"],
            paleta_cor=analysis["paleta_cor"],
            imagem_url=image_url,
            tags=analysis.get("tags", [])
        )

        return roupa_data

    async def batch_catalog(
        self,
        user_id: int,
        images: List[UploadFile]
    ) -> List[Roupa]:
        """
        Cataloga múltiplas fotos de uma vez.

        Ideal para setup inicial do guarda-roupa.
        """
        cataloged = []

        for image in images:
            try:
                roupa_data = await self.catalog_from_photo(user_id, image)

                # Salva no DB
                roupa = await wardrobe_service.create_roupa(user_id, roupa_data)
                cataloged.append(roupa)

            except Exception as e:
                logger.error(f"Falha ao catalogar {image.filename}: {e}")
                continue

        return cataloged
```

---

## 📊 Modelos de Dados

### Schema PostgreSQL

```sql
-- ========================================
-- Tabela: roupas (Inventário de Peças)
-- ========================================
CREATE TABLE roupas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    nome TEXT NOT NULL,  -- Ex: "Camiseta WickedBotz Preta"
    tipo TEXT NOT NULL,  -- Ex: "camiseta", "calca", "tenis"

    -- Status de disponibilidade
    status TEXT DEFAULT 'limpa',  -- limpa, para_lavar, para_consertar, para_substituir
    disponivel BOOLEAN DEFAULT TRUE,

    -- Atributos visuais
    cor_primaria TEXT NOT NULL,  -- Ex: "preto", "azul"
    cor_secundaria TEXT,
    paleta_cor TEXT,  -- Ex: "neutra", "quente", "fria", "vibrante"
    estampa TEXT DEFAULT 'solida',  -- solida, listrada, floral, xadrez

    -- Características físicas
    material TEXT,  -- Ex: "algodao", "jeans", "seda", "couro"
    estacao TEXT[],  -- Ex: ['verao', 'primavera']

    -- Contexto de uso
    ocasioes TEXT[],  -- Ex: ['casual', 'profissional', 'formal', 'esporte']

    -- Metadados
    imagem_url TEXT,
    tags TEXT[],
    notas TEXT,

    -- Rastreamento de uso
    ultima_vez_usada DATE,
    total_usos INTEGER DEFAULT 0,

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_roupas_user ON roupas(user_id);
CREATE INDEX idx_roupas_tipo ON roupas(tipo);
CREATE INDEX idx_roupas_status ON roupas(status);
CREATE INDEX idx_roupas_ocasioes ON roupas USING GIN(ocasioes);


-- ========================================
-- Tabela: looks (Combinações Salvas)
-- ========================================
CREATE TABLE looks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    nome TEXT NOT NULL,  -- Ex: "Look Reunião Sênior Syssa"
    descricao TEXT,

    -- Contexto
    ocasiao TEXT NOT NULL,  -- Ex: "profissional", "casual"

    -- Metadados
    imagem_url TEXT,  -- Foto do look completo
    notas TEXT,

    -- Rastreamento
    total_usos INTEGER DEFAULT 0,
    ultima_vez_usado DATE,

    -- Feedback
    rating NUMERIC(2, 1),  -- 1.0 a 5.0
    feedback_tags TEXT[],  -- Ex: ['confortavel', 'poderoso', 'frio']

    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_looks_user ON looks(user_id);
CREATE INDEX idx_looks_ocasiao ON looks(ocasiao);


-- ========================================
-- Tabela: look_items (Relação N-M)
-- ========================================
CREATE TABLE look_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    look_id UUID REFERENCES looks(id) ON DELETE CASCADE,
    roupa_id UUID REFERENCES roupas(id) ON DELETE CASCADE,

    -- Ordem de exibição (opcional)
    ordem INTEGER,

    criado_em TIMESTAMP DEFAULT NOW(),

    UNIQUE(look_id, roupa_id)
);

-- Índices
CREATE INDEX idx_look_items_look ON look_items(look_id);
CREATE INDEX idx_look_items_roupa ON look_items(roupa_id);


-- ========================================
-- Tabela: plano_semanal_looks
-- ========================================
CREATE TABLE plano_semanal_looks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Período do plano
    semana_inicio DATE NOT NULL,
    semana_fim DATE NOT NULL,

    -- Status do plano
    status TEXT DEFAULT 'pendente',  -- pendente, aprovado, em_uso, completo

    -- Plano completo (JSONB)
    plano JSONB NOT NULL,
    -- Estrutura:
    -- {
    --   "segunda": {
    --     "data": "2025-11-18",
    --     "look_id": "uuid",
    --     "look_nome": "Look Faculdade Conforto",
    --     "itens": [...],
    --     "ocasiao": "casual",
    --     "evento_contexto": "Faculdade + RobotClass",
    --     "fase_ciclo": "folicular",
    --     "energia_esperada": 110
    --   },
    --   "terca": {...}
    -- }

    -- Timestamps
    criado_em TIMESTAMP DEFAULT NOW(),
    aprovado_em TIMESTAMP,
    completo_em TIMESTAMP
);

-- Índices
CREATE INDEX idx_plano_semanal_user ON plano_semanal_looks(user_id);
CREATE INDEX idx_plano_semanal_semana ON plano_semanal_looks(semana_inicio);
CREATE INDEX idx_plano_semanal_status ON plano_semanal_looks(status);


-- ========================================
-- Tabela: feedback_looks
-- ========================================
CREATE TABLE feedback_looks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Relacionamento
    look_id UUID REFERENCES looks(id),
    plano_id UUID REFERENCES plano_semanal_looks(id),

    -- Feedback
    data_uso DATE NOT NULL,
    rating NUMERIC(2, 1),  -- 1.0 a 5.0
    sentimento TEXT[],  -- Ex: ['poderosa', 'confortavel', 'confiante']
    problemas TEXT[],  -- Ex: ['frio', 'desconfortavel', 'cores_nao_combinaram']
    notas TEXT,

    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_feedback_looks_look ON feedback_looks(look_id);
CREATE INDEX idx_feedback_looks_data ON feedback_looks(data_uso);
```

### Schemas Pydantic

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Literal
from uuid import UUID

# ========================================
# Roupas (Inventory)
# ========================================

class RoupaCreate(BaseModel):
    """Schema para criar peça de roupa."""
    nome: str = Field(..., min_length=1)
    tipo: Literal[
        "camiseta", "blusa", "camisa", "calca", "saia", "shorts",
        "vestido", "jaqueta", "casaco", "tenis", "sapato", "sandalia"
    ]
    cor_primaria: str
    cor_secundaria: Optional[str] = None
    paleta_cor: Literal["neutra", "quente", "fria", "vibrante"]
    estampa: Literal["solida", "listrada", "floral", "xadrez", "poa", "geometrica"] = "solida"
    material: Optional[str] = None
    estacao: Optional[List[Literal["verao", "outono", "inverno", "primavera"]]] = None
    ocasioes: List[Literal["casual", "profissional", "formal", "esporte"]]
    tags: Optional[List[str]] = []
    notas: Optional[str] = None

class RoupaUpdate(BaseModel):
    """Schema para atualizar roupa."""
    nome: Optional[str] = None
    status: Optional[Literal["limpa", "para_lavar", "para_consertar", "para_substituir"]] = None
    disponivel: Optional[bool] = None
    tags: Optional[List[str]] = None
    notas: Optional[str] = None

class Roupa(RoupaCreate):
    """Peça de roupa completa."""
    id: UUID
    user_id: int
    status: str
    disponivel: bool
    imagem_url: Optional[str]
    ultima_vez_usada: Optional[date]
    total_usos: int
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Looks (Combinações)
# ========================================

class LookCreate(BaseModel):
    """Schema para criar look."""
    nome: str
    descricao: Optional[str] = None
    ocasiao: Literal["casual", "profissional", "formal", "esporte"]
    item_ids: List[UUID] = Field(..., min_items=2)  # Pelo menos 2 peças
    notas: Optional[str] = None

class Look(BaseModel):
    """Look completo."""
    id: UUID
    user_id: int
    nome: str
    descricao: Optional[str]
    ocasiao: str
    imagem_url: Optional[str]
    items: List[Roupa]  # Peças do look
    total_usos: int
    ultima_vez_usado: Optional[date]
    rating: Optional[float]
    feedback_tags: List[str]

    class Config:
        from_attributes = True


# ========================================
# Planejamento Semanal
# ========================================

class DayOutfit(BaseModel):
    """Look planejado para um dia."""
    data: date
    look_id: Optional[UUID] = None
    look_nome: str
    itens: List[dict]  # Peças simplificadas
    ocasiao: str
    evento_contexto: Optional[str]
    fase_ciclo: str
    energia_esperada: int

class WeeklyPlanCreate(BaseModel):
    """Solicita criação de plano semanal."""
    semana_inicio: date

class WeeklyOutfitPlan(BaseModel):
    """Plano semanal completo."""
    id: UUID
    user_id: int
    semana_inicio: date
    semana_fim: date
    status: Literal["pendente", "aprovado", "em_uso", "completo"]
    plano: dict  # JSONB com DayOutfit para cada dia
    criado_em: datetime

    class Config:
        from_attributes = True


# ========================================
# Feedback
# ========================================

class FeedbackCreate(BaseModel):
    """Feedback sobre look usado."""
    look_id: UUID
    data_uso: date
    rating: float = Field(..., ge=1.0, le=5.0)
    sentimento: List[Literal[
        "poderosa", "confortavel", "confiante", "elegante",
        "criativa", "profissional", "casual", "relaxada"
    ]]
    problemas: Optional[List[Literal[
        "frio", "calor", "desconfortavel", "apertado",
        "cores_nao_combinaram", "inadequado_ocasiao"
    ]]] = []
    notas: Optional[str] = None

class Feedback(FeedbackCreate):
    """Feedback completo."""
    id: UUID
    user_id: int
    plano_id: Optional[UUID]

    class Config:
        from_attributes = True
```

---

## 🎨 Regras de Estilo

### Matriz de Regras Implementadas

| ID | Regra | Severidade | Descrição |
|----|-------|------------|-----------|
| **R-EST-001** | Estampas Conflitantes | ❌ ERRO | Não combinar 2+ estampas diferentes (ex: listrado + floral) |
| **R-EST-002** | Peça Neutra Obrigatória | ⚠️ WARNING | Looks profissionais/formais devem ter ≥1 peça neutra |
| **R-EST-003** | Harmonia de Cores | ⚠️ WARNING | Cores devem ser complementares ou ter cor neutra |
| **R-EST-004** | Ocasião Apropriada | ❌ ERRO | NUNCA peça casual em evento formal |
| **R-EST-005** | Conforto em Baixa Energia | 💡 SUGESTÃO | Em fase menstrual/lútea, priorizar algodão e conforto |
| **R-EST-006** | Clima Apropriado | ⚠️ WARNING | Verificar se roupa é adequada para temperatura |
| **R-EST-007** | Evitar Repetição | 💡 SUGESTÃO | Não usar mesma peça 2 dias seguidos (exceto básicos) |

### Matriz de Harmonia de Cores

```python
COLOR_HARMONY_MATRIX = {
    # Cores primárias
    "vermelho": {
        "combina": ["branco", "preto", "cinza", "azul-marinho", "bege"],
        "evitar": ["rosa", "laranja"]
    },
    "azul": {
        "combina": ["branco", "preto", "cinza", "bege", "marrom"],
        "evitar": ["verde-escuro"]
    },
    "amarelo": {
        "combina": ["branco", "preto", "cinza", "azul-marinho", "marrom"],
        "evitar": ["verde-claro"]
    },

    # Cores secundárias
    "verde": {
        "combina": ["branco", "preto", "marrom", "bege", "cinza"],
        "evitar": ["azul-claro", "rosa"]
    },
    "rosa": {
        "combina": ["branco", "preto", "cinza", "azul", "bege"],
        "evitar": ["vermelho", "laranja"]
    },
    "roxo": {
        "combina": ["branco", "preto", "cinza", "azul", "verde-claro"],
        "evitar": ["marrom"]
    },

    # Neutros (combinam com TUDO)
    "branco": {"combina": "*"},
    "preto": {"combina": "*"},
    "cinza": {"combina": "*"},
    "bege": {"combina": "*"},
    "marrom": {"combina": "*"},
}
```

---

## 🔌 API Endpoints

### Roupas (Inventory)

```python
# Adicionar peça de roupa
POST /api/v1/wardrobe/clothes
{
  "nome": "Camiseta WickedBotz Preta",
  "tipo": "camiseta",
  "cor_primaria": "preto",
  "paleta_cor": "neutra",
  "estampa": "estampada",
  "material": "algodao",
  "ocasioes": ["casual", "profissional"]
}

# Catalogar via foto (V3+)
POST /api/v1/wardrobe/clothes/from-photo
Content-Type: multipart/form-data
{
  "image": <arquivo.jpg>
}

Response:
{
  "id": "uuid",
  "nome": "Peça #1234",
  "tipo": "camiseta",
  "cor_primaria": "preto",
  "estampa": "estampada",
  "auto_cataloged": true
}

# Listar roupas
GET /api/v1/wardrobe/clothes
  ?tipo=camiseta
  &status=limpa
  &ocasiao=profissional

# Atualizar status de roupa
PATCH /api/v1/wardrobe/clothes/{id}
{
  "status": "para_lavar"
}

# Deletar roupa
DELETE /api/v1/wardrobe/clothes/{id}
```

### Looks (Combinações)

```python
# Criar look salvo
POST /api/v1/wardrobe/looks
{
  "nome": "Look Reunião Sênior",
  "ocasiao": "profissional",
  "item_ids": ["uuid1", "uuid2", "uuid3"],
  "notas": "Sempre me sinto confiante neste look"
}

# Listar looks
GET /api/v1/wardrobe/looks
  ?ocasiao=profissional

# Obter look específico
GET /api/v1/wardrobe/looks/{id}

# Registrar uso de look
POST /api/v1/wardrobe/looks/{id}/use
{
  "data": "2025-11-18"
}
```

### Planejamento Semanal

```python
# Gerar plano semanal
POST /api/v1/wardrobe/plan-week
{
  "semana_inicio": "2025-11-18"
}

Response:
{
  "id": "uuid",
  "status": "pendente",
  "plano": {
    "segunda": {
      "data": "2025-11-18",
      "look_nome": "Look Faculdade Conforto",
      "itens": [
        {"tipo": "camiseta", "nome": "Camiseta WickedBotz"},
        {"tipo": "calca", "nome": "Jeans Escuro"}
      ],
      "ocasiao": "casual",
      "evento_contexto": "Faculdade",
      "fase_ciclo": "folicular",
      "energia_esperada": 110
    },
    "terca": {...}
  }
}

# Aprovar plano
POST /api/v1/wardrobe/plans/{id}/approve

# Rejeitar e pedir novo plano
POST /api/v1/wardrobe/plans/{id}/reject
{
  "motivo": "Segunda-feira muito casual, tenho reunião"
}

# Obter look do dia
GET /api/v1/wardrobe/today-outfit

Response:
{
  "data": "2025-11-18",
  "look_nome": "Look Faculdade Conforto",
  "itens": [...],
  "ocasiao": "casual"
}
```

### Feedback

```python
# Enviar feedback sobre look usado
POST /api/v1/wardrobe/feedback
{
  "look_id": "uuid",
  "data_uso": "2025-11-18",
  "rating": 4.5,
  "sentimento": ["confortavel", "confiante"],
  "problemas": [],
  "notas": "Perfeito para dia longo na faculdade"
}

# Obter histórico de feedback
GET /api/v1/wardrobe/feedback
  ?look_id=uuid
```

---

## 🔗 Integrações

### Event Bus Events

```python
# Eventos que o Wardrobe PUBLICA
EventType.WARDROBE_ITEM_NEEDS_REPLACEMENT = "wardrobe.item.needs_replacement"
EventType.WEEKLY_PLAN_GENERATED = "wardrobe.weekly_plan.generated"
EventType.WEEKLY_PLAN_APPROVED = "wardrobe.weekly_plan.approved"
EventType.OUTFIT_FEEDBACK_RECEIVED = "wardrobe.outfit.feedback"

# Eventos que o Wardrobe OUVE
EventType.CALENDAR_EVENT_CREATED = "calendar.event.created"
EventType.WELLNESS_STATUS_UPDATED = "wellness.status.updated"
EventType.CYCLE_PHASE_CHANGED = "wellness.cycle_phase_changed"
EventType.ROUTINE_GENERATED = "routine.daily.generated"
```

### Integração com Tasks (Automação de Lista de Compras)

```python
@event_bus.subscribe(EventType.WARDROBE_ITEM_NEEDS_REPLACEMENT)
async def on_item_needs_replacement(event: WardrobeItemEvent):
    """
    Quando uma peça é marcada como 'para_substituir',
    cria tarefa automaticamente.
    """
    roupa = await wardrobe_service.get_roupa(event.item_id)

    # Cria tarefa
    task = TaskCreate(
        title=f"Comprar novo(a) {roupa.tipo} {roupa.cor_primaria}",
        description=(
            f"Substituir: {roupa.nome}\n"
            f"Características: {roupa.cor_primaria}, {roupa.estampa}, {roupa.material}\n"
            f"Ocasiões: {', '.join(roupa.ocasioes)}"
        ),
        big_rock_id=None,  # Ou "Autocuidado"
        priority="medium",
        tags=["compras", "guarda-roupa"]
    )

    await tasks_service.create_task(event.user_id, task)

    logger.info(f"Tarefa criada para substituir {roupa.nome}")
```

### Integração com Wellness Coach

```python
@event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED)
async def on_cycle_phase_change(event: CyclePhaseEvent):
    """
    Quando fase do ciclo muda, atualiza preferências do plano.
    """
    # Se mudou para fase menstrual, avisa para próximo planejamento
    if event.new_phase == "menstrual":
        # Adiciona nota para priorizar conforto
        await wardrobe_service.set_planning_preference(
            user_id=event.user_id,
            preference="priorizar_conforto",
            duration_days=5
        )
```

### Integração com Google Calendar

```python
@event_bus.subscribe(EventType.CALENDAR_EVENT_CREATED)
async def on_calendar_event(event: CalendarEventCreated):
    """
    Quando evento importante é criado, ajusta plano da semana.
    """
    # Se é evento formal e está na semana atual
    if event.is_formal and event.is_current_week:
        # Marca o dia para replanejar
        await wardrobe_service.mark_day_for_replan(
            user_id=event.user_id,
            date=event.event_date,
            reason=f"Evento formal adicionado: {event.title}"
        )
```

### Integração com Routine Manager

```python
@event_bus.subscribe(EventType.ROUTINE_GENERATED)
async def on_routine_generated(event: RoutineGeneratedEvent):
    """
    Quando roteiro do dia é gerado, adiciona look planejado.
    """
    # Busca look do dia
    outfit = await wardrobe_service.get_outfit_for_date(
        user_id=event.user_id,
        date=event.date
    )

    if outfit:
        # Adiciona ao roteiro
        await routine_service.add_outfit_info(
            routine_id=event.routine_id,
            outfit=outfit
        )
```

---

## 💡 Casos de Uso

### Caso 1: Planejamento Semanal de Looks

```
Fluxo completo de planejamento:

DOMINGO À NOITE (ou quando preferir)

1. Usuário:
   $ charlee wardrobe plan-week --start 2025-11-18

2. Wardrobe Manager inicia processo:

   a) Busca roupas disponíveis (status='limpa')
      └─> 45 peças encontradas

   b) Para cada dia da semana (seg-dom):

      i) Consulta Google Calendar
         seg: "Faculdade 07:30", "RobotClass 14:00"
         ter: "Reunião Syssa 09:00" (formal!)
         qua: "Faculdade 07:30"
         ...

      ii) Consulta Wellness Coach
          Fase: Folicular
          Energia esperada: 110-120%

      iii) Context Analyzer determina ocasião:
           seg: casual
           ter: profissional/formal
           qua: casual
           ...

      iv) Gera combinações válidas:
          seg: 120 combinações possíveis

      v) Aplica Style Rules:
          seg: 45 combinações válidas (filtradas)

      vi) Seleciona melhor (via LLM):

          Prompt ao LLM:
          "Escolha o melhor look para:
           - Segunda-feira (Faculdade + RobotClass)
           - Ocasião: casual
           - Fase folicular (alta energia)
           - Clima: 22°C, ensolarado

           Opções:
           1. Camiseta WickedBotz + Jeans Escuro + Tênis
           2. Blusa Azul + Calça Jeans + Tênis
           3. ..."

3. Charlee apresenta plano completo:

   📅 PLANO DE LOOKS DA SEMANA (18-24 Nov)

   Segunda (18/11):
   • Look: "Casual Faculdade Energizado"
   • Camiseta WickedBotz + Jeans Escuro + Tênis
   • Ocasião: Casual
   • Energia: Alta (110%)

   Terça (19/11):
   • Look: "Reunião Sênior Profissional"
   • Blusa Seda Azul + Calça Preta + Sapato
   • Ocasião: Profissional/Formal
   • Energia: Alta (115%)

   Quarta (20/11):
   • Look: "Faculdade Conforto"
   • ...

   Aprovar plano?
   [1] Aprovar tudo
   [2] Ajustar dia específico
   [3] Gerar novo plano

4. Usuário aprova:
   $ charlee wardrobe approve-plan

5. Sistema salva plano no DB:
   └─> plano_semanal_looks (status: 'aprovado')
   └─> Marca roupas como 'reservada' para os dias

6. SEGUNDA-FEIRA (05:00)

   Morning Briefing inclui automaticamente:

   ☀️ BOM DIA, SAMARA!

   👔 Seu Look de Hoje (Pré-definido):
   • "Casual Faculdade Energizado"
   • Camiseta WickedBotz (preta, estampada)
   • Jeans Escuro
   • Tênis Nike

   ✨ Já está tudo separado! 0 decisões para fazer.

   🎯 Roteiro Detalhado (Manhã):
   05:00 | Levantar
   05:02 | Banheiro
   05:05 | Ver roupa (✅ Look já decidido)
   ...
```

### Caso 2: Catalogação Automática via Foto (V3+)

```
Fluxo de setup inicial do guarda-roupa:

1. Usuário tira fotos de todas as roupas

2. Upload em lote:
   $ charlee wardrobe catalog-photos --folder ~/roupas/

3. Para cada foto:

   a) Vision API analisa imagem

      Foto: camiseta_preta.jpg
      ↓
      Claude Vision detecta:
      - Tipo: camiseta
      - Cor primária: preto
      - Estampa: logo WickedBotz (estampada)
      - Material: algodão (aparente)
      - Ocasiões sugeridas: casual, profissional

   b) Sistema cria entrada no DB:

      Roupa criada:
      ✅ Nome: "Camiseta WickedBotz Preta"
      ✅ Tipo: camiseta
      ✅ Cor: preto
      ✅ Status: limpa
      ✅ Ocasiões: [casual, profissional]

4. Resultado final:

   📸 Catalogação Completa!

   50 peças catalogadas automaticamente:
   • 15 camisetas
   • 10 blusas
   • 8 calças
   • 5 saias
   • 12 tênis/sapatos

   Tempo total: 3 minutos
   (vs ~30 minutos manual!)

   Próximo passo:
   $ charlee wardrobe plan-week
```

### Caso 3: Feedback Loop e Melhoria Contínua

```
Fluxo de feedback após usar um look:

1. Usuário usa look sugerido (Terça: "Reunião Sênior")

2. Durante o dia:
   └─> Reunião foi muito bem!
   └─> Sentiu-se confiante e profissional
   └─> MAS: passou um pouco de frio (AC forte)

3. No final do dia:

   Charlee (proativo):
   "Como foi o look de hoje? ('Reunião Sênior Profissional')"

   [1] Adorei! ⭐⭐⭐⭐⭐
   [2] Bom, mas... ⭐⭐⭐⭐
   [3] Não gostei ⭐⭐

4. Usuário escolhe [2]:

   Charlee:
   "O que poderia melhorar?"
   [Sentimento] □ Confortável □ Poderosa ☑ Confiante □ Elegante
   [Problemas] ☑ Frio □ Calor □ Desconfortável □ Cores

   Notas: "AC muito forte na Syssa, preciso de blazer"

5. Sistema armazena feedback:
   └─> feedback_looks (rating: 4.0, problemas: ['frio'])

6. PRÓXIMA VEZ que planejar para "Reunião Syssa":

   Wardrobe Manager consulta histórico:
   └─> "Última vez passou frio, adicionar blazer"

   Sugestão ajustada:
   ✅ Blusa Seda Azul
   ✅ Calça Preta
   ✅ Sapato
   ✅ Blazer Preto ← NOVO!

   Justificativa (LLM):
   "Baseado no seu feedback anterior, adicionei o blazer
    para compensar o AC forte da Syssa."
```

---

## 🗓️ Roadmap

### Fase 1: MVP - Inventário Manual
- [ ] Modelos de dados (roupas, looks, look_items)
- [ ] API CRUD de roupas
- [ ] API de criação de looks
- [ ] CLI: `charlee wardrobe add-item`
- [ ] CLI: `charlee wardrobe create-look`

### Fase 2: Planejamento Básico
- [ ] Wardrobe Manager agent
- [ ] Style Rules Engine (regras básicas)
- [ ] Integração com Google Calendar
- [ ] Geração de plano semanal (sem IA)
- [ ] API: `POST /wardrobe/plan-week`

### Fase 3: Inteligência e Contexto
- [ ] Integração com Wellness Coach (ciclo)
- [ ] LLM para seleção de looks
- [ ] Aplicação de regras de estilo (cores, estampas)
- [ ] Context Analyzer completo
- [ ] Sistema de aprovação de planos

### Fase 4: Automação de Manutenção
- [ ] Rastreamento de status (limpa, para lavar)
- [ ] Criação automática de tarefas (para_substituir)
- [ ] Rastreamento de uso (última vez usada)
- [ ] Alertas de peças não usadas há muito tempo

### Fase 5: Feedback Loop
- [ ] Sistema de feedback de looks
- [ ] Modelo de preferências do usuário
- [ ] Aprendizado contínuo (rating + sentimentos)
- [ ] Ajuste de sugestões baseado em histórico

### Fase 6: Vision AI (V3+)
- [ ] Vision Cataloger agent
- [ ] Integração com Claude 3.5 Sonnet (Vision)
- [ ] Upload de fotos para catalogação
- [ ] Batch cataloging (múltiplas fotos)
- [ ] Auto-preenchimento de atributos

### Fase 7: Frontend (futuro)
- [ ] Dashboard de guarda-roupa
- [ ] Visualização de looks (fotos)
- [ ] Interface de planejamento semanal
- [ ] Drag-and-drop de combinações
- [ ] Galeria de looks favoritos

### Fase 8: Avançado (futuro)
- [ ] Integração com lojas (links de compra)
- [ ] Sugestões de peças para comprar
- [ ] Análise de custo por uso
- [ ] Capsule wardrobe generator
- [ ] Social: compartilhar looks com amigas

---

## 📚 Referências

### Moda e Estilo
- **The Curated Closet** - Anuschka Rees
- **Capsule Wardrobe Guide** - Minimalist principles
- **Color Theory for Fashion** - Harmonia de cores

### Produtividade
- **Decision Fatigue** - Roy Baumeister
- **Essentialism** - Greg McKeown (foco no essencial)
- **Atomic Habits** - James Clear (rotinas automáticas)

### Tecnologia
- **Computer Vision in Fashion** - AI for style
- **Recommendation Systems** - Collaborative filtering
- **Multi-agent Systems** - Agent coordination

---

**Desenvolvido com ❤️ por Samara Cassie**

*Versão: 1.0 - Draft Inicial*
*Última atualização: 2025-11-17*
