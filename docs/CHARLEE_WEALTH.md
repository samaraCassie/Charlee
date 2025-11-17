# 💰 Charlee Wealth - Módulo de Gestão Financeira Comportamental

> **Versão**: 1.0 (Planejamento)
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V4.0 - Wealth Management System

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Inputs de Dados](#inputs-de-dados)
4. [Agentes Especializados](#agentes-especializados)
5. [Modelos de Dados](#modelos-de-dados)
6. [API Endpoints](#api-endpoints)
7. [Integrações](#integrações)
8. [Casos de Uso](#casos-de-uso)
9. [Roadmap](#roadmap)

---

## 🎯 Visão Geral

O **Charlee Wealth** transforma o Charlee de um gestor de produtividade em um **gestor de património holístico**, que entende que as finanças não são apenas sobre números, mas sobre **comportamento, energia e estratégia de longo prazo**.

### Filosofia

```
Finanças = Comportamento × Energia × Estratégia
```

O módulo não apenas rastreia gastos, mas:
- **Entende por que** você gasta (conexões com stress, ciclo, sono)
- **Previne** gastos impulsivos (alertas proativos)
- **Conecta** finanças pessoais com objetivos profissionais (OKRs, projetos freelance)

### Integração Profunda com Outros Módulos

```
┌─────────────────────────────────────────────────────┐
│              CHARLEE WEALTH ECOSYSTEM               │
└─────────────────────────────────────────────────────┘
           ↓           ↓            ↓           ↓
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Wellness │ │ Capacity │ │  Focus   │ │ Projects │
    │  Coach   │ │ Guardian │ │  Agent   │ │ Manager  │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
         │            │            │            │
         └────────────┴────────────┴────────────┘
                      Event Bus
```

**Conexões**:
- 🌸 **Wellness Coach**: Correlaciona gastos com fase do ciclo menstrual
- 🛡️ **Capacity Guardian**: Identifica gastos relacionados a sobrecarga
- 🎯 **Focus Agent**: Captura transações de notificações (e-mails bancários)
- 💼 **Projects Manager**: Conecta faturamento freelance com metas financeiras

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────┐
│                 CHARLEE WEALTH                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         1. INPUT LAYER (Skills)             │   │
│  │  • ParseNotificationExpense                 │   │
│  │  • ImportBatchExpense                       │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │      2. INTELLIGENCE LAYER (Agents)         │   │
│  │  • BehavioralFinanceAgent (Análise Causal)  │   │
│  │  • SavingsAdvisor (Prevenção Proativa)      │   │
│  │  • ForecastAgent (Previsão e Metas)         │   │
│  └─────────────────────────────────────────────┘   │
│                       ↓                             │
│  ┌─────────────────────────────────────────────┐   │
│  │         3. DATA LAYER (Models)              │   │
│  │  • Despesas (+ contexto comportamental)     │   │
│  │  • Categorias                               │   │
│  │  • MetasFinanceiras                         │   │
│  │  • PrevisaoGastos                           │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 📥 Inputs de Dados

### 1.1. Skill: ParseNotificationExpense (Captura em Tempo Real)

**Objetivo**: Eliminar o atrito de registro manual capturando transações automaticamente de notificações bancárias.

#### Integração com Event Bus

```python
# Subscrição ao evento
@event_bus.subscribe(EventType.FINANCIAL_TRANSACTION_DETECTED)
async def on_financial_notification(event: FinancialTransactionEvent):
    """
    Ativado quando o Focus Agent detecta um e-mail bancário.
    """
    # Processar notificação...
```

#### Fluxo Completo

```
┌──────────────────────────────────────────────────────┐
│  1. E-mail chega (Nubank, Inter, etc.)               │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  2. NotificationAgent (Focus) recebe                 │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  3. ClassifierAgent identifica:                      │
│     tipo: 'transacao_financeira'                     │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  4. Publica: EventType.FINANCIAL_TRANSACTION_DETECTED│
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  5. WealthAgent ouve e processa com LLM:             │
│     Extrai: {valor: 45.90, estabelecimento: "iFood"} │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  6. Insere na tabela `despesas`:                     │
│     status: 'nao_categorizado'                       │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  7. Notificação ao usuário:                          │
│     "Vi compra R$45.90 em iFood. Qual categoria?"    │
└──────────────────────────────────────────────────────┘
```

#### Implementação

```python
class ParseNotificationExpenseSkill:
    """
    Skill para capturar transações de notificações bancárias.
    """

    async def parse_transaction(self, email_body: str) -> Transaction:
        """
        Usa LLM para extrair dados da transação.

        Args:
            email_body: Corpo do e-mail bancário

        Returns:
            Transaction: Dados extraídos (valor, estabelecimento, data)
        """
        prompt = f"""
        Analise este e-mail bancário e extraia os dados da transação:

        {email_body}

        Retorne JSON com:
        - valor: float
        - estabelecimento: string
        - data: datetime
        - tipo: "debito" | "credito"
        """

        result = await self.llm.process(prompt)
        return Transaction.parse_obj(result)

    async def store_transaction(self, transaction: Transaction) -> Despesa:
        """
        Armazena transação com status 'nao_categorizado'.
        """
        despesa = Despesa(
            valor=transaction.valor,
            estabelecimento=transaction.estabelecimento,
            data=transaction.data,
            tipo=transaction.tipo,
            status="nao_categorizado",
            fonte="notificacao_automatica"
        )

        db.add(despesa)
        db.commit()

        # Publica evento para categorização
        event_bus.publish(
            EventType.EXPENSE_NEEDS_CATEGORIZATION,
            ExpenseEvent(expense_id=despesa.id)
        )

        return despesa
```

---

### 1.2. Skill: ImportBatchExpense (Reconciliação)

**Objetivo**: Importar extratos bancários em lote (CSV, OFX, PDF) e reconciliar com transações já capturadas.

#### Comando CLI

```bash
# Importar extrato
charlee wealth import --file extrato_nubank_nov.csv

# Com opções
charlee wealth import \
  --file extrato.csv \
  --format csv \
  --banco nubank \
  --auto-categorize
```

#### Fluxo de Reconciliação

```
┌──────────────────────────────────────────────────────┐
│  1. Upload de arquivo (CSV/OFX/PDF)                  │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  2. Parse do arquivo (extrai transações)             │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  3. Para cada transação:                             │
│     Verifica duplicata (data + valor + ID)           │
└────────────────────┬─────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
┌─────────────────┐      ┌─────────────────┐
│  JÁ EXISTE      │      │  NOVA           │
│  (skip/update)  │      │  (categorizar)  │
└─────────────────┘      └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │  LLM Auto-      │
                         │  Categorização  │
                         └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │  Insere no DB   │
                         └─────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────┐
│  4. Relatório final:                                 │
│     "50 importadas, 10 duplicadas, 3 manuais"        │
└──────────────────────────────────────────────────────┘
```

#### Implementação

```python
class ImportBatchExpenseSkill:
    """
    Skill para importação em lote de extratos bancários.
    """

    def parse_file(self, file_path: str, format: str) -> List[RawTransaction]:
        """
        Faz parse do arquivo baseado no formato.
        """
        if format == "csv":
            return self._parse_csv(file_path)
        elif format == "ofx":
            return self._parse_ofx(file_path)
        elif format == "pdf":
            return self._parse_pdf(file_path)

    async def reconcile(self, transactions: List[RawTransaction]) -> ReconciliationReport:
        """
        Reconcilia transações importadas com as existentes.
        """
        report = ReconciliationReport()

        for raw_tx in transactions:
            # Busca duplicata
            existing = db.query(Despesa).filter(
                Despesa.data == raw_tx.data,
                Despesa.valor == raw_tx.valor,
                Despesa.external_id == raw_tx.id
            ).first()

            if existing:
                report.duplicates.append(raw_tx)
                continue

            # Auto-categorização com LLM
            category = await self._auto_categorize(raw_tx)

            # Insere nova despesa
            despesa = Despesa(
                valor=raw_tx.valor,
                estabelecimento=raw_tx.estabelecimento,
                data=raw_tx.data,
                categoria=category,
                status="categorizado" if category else "nao_categorizado",
                fonte="importacao_lote"
            )

            db.add(despesa)
            report.imported.append(despesa)

        db.commit()
        return report

    async def _auto_categorize(self, transaction: RawTransaction) -> Optional[str]:
        """
        Usa LLM + histórico para categorizar automaticamente.
        """
        # Busca transações similares já categorizadas
        similar = db.query(Despesa).filter(
            Despesa.estabelecimento.ilike(f"%{transaction.estabelecimento}%"),
            Despesa.categoria.isnot(None)
        ).limit(5).all()

        if similar:
            # Usa categoria mais comum
            categories = [d.categoria for d in similar]
            return max(set(categories), key=categories.count)

        # Fallback: LLM
        prompt = f"Categorize esta transação: {transaction.estabelecimento}"
        return await self.llm.categorize(prompt)
```

---

## 🤖 Agentes Especializados

### 2. BehavioralFinanceAgent (Análise Causal)

**Objetivo**: Não apenas registrar **o quê** foi gasto, mas **por quê**.

#### Integração com Context Manager

```python
@event_bus.subscribe(EventType.FINANCIAL_TRANSACTION_DETECTED)
async def on_transaction(event: FinancialTransactionEvent):
    """
    Analisa contexto comportamental da transação.
    """
    # 1. Busca contexto da hora da transação
    context = await context_manager.get_context_at(
        timestamp=event.transaction_time,
        lookback_hours=3
    )

    # 2. Enriquece transação com dados comportamentais
    behavioral_context = {
        "carga_trabalho": context.carga_trabalho_percentual,
        "nivel_stress": context.nivel_stress,
        "horas_sono": context.horas_sono,
        "fase_ciclo": context.fase_ciclo,
        "energia": context.nivel_energia
    }

    # 3. Armazena no campo JSONB
    despesa.contexto_comportamental = behavioral_context
    db.commit()
```

#### Análise de Padrões

```python
class BehavioralFinanceAgent:
    """
    Agente que analisa correlações entre comportamento e gastos.
    """

    async def analyze_patterns(self, user_id: int, period_days: int = 90) -> List[Insight]:
        """
        Analisa padrões comportamentais nos últimos N dias.
        """
        despesas = db.query(Despesa).filter(
            Despesa.user_id == user_id,
            Despesa.data >= datetime.now() - timedelta(days=period_days)
        ).all()

        insights = []

        # Padrão 1: Stress → Delivery
        delivery_expenses = [d for d in despesas if d.categoria == "Alimentacao/Delivery"]
        high_stress_deliveries = [
            d for d in delivery_expenses
            if d.contexto_comportamental.get("nivel_stress", 0) > 7
        ]

        if len(high_stress_deliveries) / len(delivery_expenses) > 0.4:
            insights.append(Insight(
                tipo="correlacao_stress_delivery",
                mensagem=(
                    f"40% dos seus gastos com delivery ocorrem em dias de "
                    f"stress alto (>7/10). Economia potencial: R$ {self._calculate_savings()}"
                ),
                impacto="medio"
            ))

        # Padrão 2: Fase Lútea → Compras por Impulso
        lutea_expenses = [
            d for d in despesas
            if d.contexto_comportamental.get("fase_ciclo") == "lutea"
            and d.categoria == "Compras/Impulso"
        ]

        # ... mais análises

        return insights

    def _calculate_correlation(
        self,
        expenses: List[Despesa],
        behavioral_factor: str
    ) -> float:
        """
        Calcula correlação entre fator comportamental e gastos.
        """
        # Implementação de correlação estatística
        pass
```

#### Geração de Insights

```python
async def generate_weekly_insights(user_id: int) -> InsightReport:
    """
    Gera relatório semanal de insights comportamentais.
    """
    agent = BehavioralFinanceAgent()
    insights = await agent.analyze_patterns(user_id, period_days=7)

    report = InsightReport(
        periodo="Última Semana",
        insights=insights,
        recomendacoes=[]
    )

    # Exemplo de insight
    if "correlacao_stress_delivery" in [i.tipo for i in insights]:
        report.recomendacoes.append(Recomendacao(
            titulo="Previna Gastos com Delivery em Dias de Stress",
            descricao=(
                "Configure um alerta para que o Charlee te lembre de usar "
                "a refeição planejada quando o stress estiver alto."
            ),
            economia_estimada=200.00,
            facilidade="facil"
        ))

    return report
```

---

### 3. SavingsAdvisor (Prevenção Proativa)

**Objetivo**: Usar insights para **prevenir** gastos, não apenas reportá-los.

#### Subscrição a Eventos de Contexto

```python
# O agente ouve eventos de outros módulos
@event_bus.subscribe(EventType.ENERGY_LOW)
@event_bus.subscribe(EventType.OVERLOAD_DETECTED)
@event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED)
async def on_context_change(event: ContextEvent):
    """
    Ativado quando contexto comportamental muda.
    """
    # Verifica se há padrão de gasto associado
    pattern = await behavioral_finance_agent.get_pattern_for_context(event)

    if pattern:
        # Envia alerta proativo
        await send_proactive_alert(pattern)
```

#### Exemplo de Alerta Proativo

```python
class SavingsAdvisor:
    """
    Agente que envia alertas proativos de economia.
    """

    async def on_overload_detected(self, event: OverloadEvent):
        """
        Quando Capacity Guardian detecta sobrecarga.
        """
        # 1. Busca padrão histórico
        pattern = await self.get_pattern(
            context="stress_alto",
            categoria="Alimentacao/Delivery"
        )

        if not pattern:
            return

        # 2. Calcula economia potencial
        economia = pattern.gasto_medio * pattern.frequencia_mensal

        # 3. Gera sugestões contextuais
        sugestoes = await self._generate_suggestions(event)

        # 4. Envia notificação
        notification = ProactiveAlert(
            titulo="🛡️ Proteção de Gastos Ativada",
            mensagem=(
                f"Samara, notei que o seu stress está em {event.stress_level}/10.\n\n"
                f"Nos últimos 3 meses, isso levou a gastos extras de R$ {economia:.2f} "
                f"com delivery.\n\n"
                f"Sugestões de Economia:\n"
            ),
            sugestoes=sugestoes,
            tipo="prevencao_gasto"
        )

        await notification_service.send(notification)

    async def _generate_suggestions(self, event: OverloadEvent) -> List[str]:
        """
        Gera sugestões contextuais baseadas no estado atual.
        """
        suggestions = []

        # Verifica se há refeição planejada (Habit Tracker)
        meal_planned = await habit_tracker.has_meal_planned(date.today())
        if meal_planned:
            suggestions.append(
                "✅ Usar a refeição saudável que você planejou hoje"
            )

        # Verifica histórico de bloqueios
        block_effective = await self.check_block_effectiveness()
        if block_effective:
            suggestions.append(
                "🚫 Ativar bloqueio temporário (2h) em apps de delivery"
            )

        # Sugere alternativa de autocuidado
        suggestions.append(
            "🧘 Fazer 10min de meditação (reduz stress e previne gastos impulsivos)"
        )

        return suggestions
```

#### Bloqueio Temporário de Gastos

```python
class SpendingBlocker:
    """
    Sistema de bloqueio temporário de categorias de gasto.
    """

    async def activate_block(
        self,
        categoria: str,
        duration_hours: int = 2,
        user_id: int
    ):
        """
        Ativa bloqueio temporário para uma categoria.
        """
        block = SpendingBlock(
            user_id=user_id,
            categoria=categoria,
            inicio=datetime.now(),
            fim=datetime.now() + timedelta(hours=duration_hours),
            motivo="prevencao_gasto_impulsivo",
            ativo=True
        )

        db.add(block)
        db.commit()

        # Envia notificação
        await notification_service.send(Notification(
            titulo="🚫 Bloqueio de Gastos Ativado",
            mensagem=(
                f"Bloqueio de {duration_hours}h ativado para '{categoria}'.\n"
                f"Você poderá gastar novamente às {block.fim.strftime('%H:%M')}."
            )
        ))

    async def check_block(self, user_id: int, categoria: str) -> Optional[SpendingBlock]:
        """
        Verifica se há bloqueio ativo para a categoria.
        """
        return db.query(SpendingBlock).filter(
            SpendingBlock.user_id == user_id,
            SpendingBlock.categoria == categoria,
            SpendingBlock.ativo == True,
            SpendingBlock.fim > datetime.now()
        ).first()
```

---

### 4. ForecastAgent (Previsão e Metas)

**Objetivo**: Conectar gastos diários com objetivos de longo prazo.

#### 4.1. Previsão de Custos

```python
class ForecastAgent:
    """
    Agente de previsão e planejamento financeiro.
    """

    async def forecast_expenses(
        self,
        user_id: int,
        months_ahead: int = 1
    ) -> ExpenseForecast:
        """
        Prevê gastos para os próximos N meses.
        """
        # 1. Busca histórico (últimos 90 dias)
        historico = db.query(Despesa).filter(
            Despesa.user_id == user_id,
            Despesa.data >= datetime.now() - timedelta(days=90)
        ).all()

        # 2. Agrupa por categoria
        by_category = self._group_by_category(historico)

        # 3. Calcula médias e desvios
        forecast = ExpenseForecast(periodo=f"Próximos {months_ahead} meses")

        for categoria, despesas in by_category.items():
            valores = [d.valor for d in despesas]

            previsao = CategoryForecast(
                categoria=categoria,
                valor_medio_mensal=statistics.mean(valores),
                desvio_padrao=statistics.stdev(valores),
                tendencia=self._calculate_trend(valores),
                confianca=self._calculate_confidence(valores)
            )

            forecast.categorias.append(previsao)

        # 4. Identifica anomalias
        forecast.alertas = self._detect_anomalies(by_category)

        return forecast

    def _calculate_trend(self, valores: List[float]) -> str:
        """
        Calcula tendência (crescente, estável, decrescente).
        """
        if len(valores) < 3:
            return "estavel"

        # Regressão linear simples
        slope = (valores[-1] - valores[0]) / len(valores)

        if slope > 0.1:
            return "crescente"
        elif slope < -0.1:
            return "decrescente"
        else:
            return "estavel"

    def _detect_anomalies(self, by_category: Dict) -> List[Alert]:
        """
        Detecta gastos anômalos.
        """
        alertas = []

        for categoria, despesas in by_category.items():
            valores = [d.valor for d in despesas]
            media = statistics.mean(valores)
            desvio = statistics.stdev(valores)

            # Identifica outliers (> 2 desvios padrões)
            outliers = [v for v in valores if abs(v - media) > 2 * desvio]

            if outliers:
                alertas.append(Alert(
                    tipo="anomalia",
                    categoria=categoria,
                    mensagem=(
                        f"O seu gasto com '{categoria}' está 15% acima da média. "
                        f"Valor esperado: R$ {media:.2f}, Atual: R$ {max(valores):.2f}"
                    )
                ))

        return alertas
```

#### 4.2. Planejamento de Metas

```python
class GoalPlanner:
    """
    Sistema de planejamento de metas financeiras.
    """

    async def create_financial_goal(
        self,
        user_id: int,
        goal_data: FinancialGoalCreate
    ) -> FinancialGoal:
        """
        Cria uma meta financeira e calcula plano de economia.
        """
        # 1. Cria a meta
        goal = FinancialGoal(
            user_id=user_id,
            titulo=goal_data.titulo,
            valor_alvo=goal_data.valor_alvo,
            data_alvo=goal_data.data_alvo,
            categoria="viagem",  # ou outra
            status="ativo"
        )

        # 2. Calcula meses até a meta
        meses_restantes = (goal_data.data_alvo - datetime.now()).days / 30

        # 3. Calcula economia mensal necessária
        goal.economia_mensal_necessaria = goal_data.valor_alvo / meses_restantes

        # 4. Analisa viabilidade
        viabilidade = await self._analyze_feasibility(user_id, goal)
        goal.viabilidade = viabilidade

        db.add(goal)
        db.commit()

        return goal

    async def _analyze_feasibility(
        self,
        user_id: int,
        goal: FinancialGoal
    ) -> GoalFeasibility:
        """
        Analisa se a meta é viável com a taxa de poupança atual.
        """
        # 1. Calcula faturamento mensal
        faturamento = await self._calculate_monthly_income(user_id)

        # 2. Prevê gastos mensais
        forecast = await ForecastAgent().forecast_expenses(user_id)
        gastos_previstos = sum([c.valor_medio_mensal for c in forecast.categorias])

        # 3. Calcula taxa de poupança atual
        taxa_poupanca_atual = faturamento - gastos_previstos

        # 4. Calcula défice/superavit
        deficit = goal.economia_mensal_necessaria - taxa_poupanca_atual

        # 5. Gera análise
        viabilidade = GoalFeasibility(
            viavel=(deficit <= 0),
            taxa_poupanca_atual=taxa_poupanca_atual,
            economia_necessaria=goal.economia_mensal_necessaria,
            deficit=max(0, deficit),
            superavit=max(0, -deficit)
        )

        # 6. Gera sugestões se houver défice
        if viabilidade.deficit > 0:
            viabilidade.sugestoes = await self._generate_deficit_solutions(
                user_id,
                viabilidade.deficit
            )

        return viabilidade

    async def _calculate_monthly_income(self, user_id: int) -> float:
        """
        Calcula faturamento mensal médio.
        """
        # Freelance (últimos 3 meses)
        freelance_income = db.query(
            func.avg(Invoice.valor_total)
        ).filter(
            Invoice.user_id == user_id,
            Invoice.created_at >= datetime.now() - timedelta(days=90)
        ).scalar() or 0

        # Salário fixo (da tabela de configurações)
        salario_fixo = await settings_service.get_user_setting(
            user_id,
            "salario_fixo"
        ) or 0

        return freelance_income + salario_fixo

    async def _generate_deficit_solutions(
        self,
        user_id: int,
        deficit: float
    ) -> List[DeficitSolution]:
        """
        Gera sugestões para cobrir défice.
        """
        solutions = []

        # Solução 1: Reduzir gastos variáveis
        forecast = await ForecastAgent().forecast_expenses(user_id)
        variable_expenses = [
            c for c in forecast.categorias
            if c.categoria in ["Restaurantes", "Entretenimento", "Compras"]
        ]

        if variable_expenses:
            total_variable = sum([c.valor_medio_mensal for c in variable_expenses])
            reducao_percentual = (deficit / total_variable) * 100

            solutions.append(DeficitSolution(
                tipo="reducao_gastos",
                titulo="Reduzir Gastos Variáveis",
                descricao=(
                    f"Reduzir gastos em '{variable_expenses[0].categoria}' "
                    f"em {reducao_percentual:.0f}% ({deficit:.2f})"
                ),
                impacto_mensal=deficit,
                dificuldade="medio"
            ))

        # Solução 2: Aumentar faturamento
        projetos_info = await projects_service.get_capacity_info(user_id)
        if projetos_info.capacidade_disponivel > 0:
            valor_hora_atual = projetos_info.valor_hora_medio
            horas_extras_necessarias = deficit / valor_hora_atual

            solutions.append(DeficitSolution(
                tipo="aumentar_faturamento",
                titulo="Aceitar Mais Projetos Freelance",
                descricao=(
                    f"Trabalhar +{horas_extras_necessarias:.0f}h/mês em projetos "
                    f"(você tem {projetos_info.capacidade_disponivel}h disponíveis)"
                ),
                impacto_mensal=deficit,
                dificuldade="medio"
            ))

        # Solução 3: Aumentar valor/hora
        aumento_necessario = (deficit / projetos_info.horas_trabalhadas_mes)
        percentual_aumento = (aumento_necessario / valor_hora_atual) * 100

        solutions.append(DeficitSolution(
            tipo="aumentar_valor_hora",
            titulo="Aumentar Valor/Hora",
            descricao=(
                f"Aumentar o seu valor/hora de R$ {valor_hora_atual:.2f} para "
                f"R$ {valor_hora_atual + aumento_necessario:.2f} "
                f"(+{percentual_aumento:.0f}%)"
            ),
            impacto_mensal=deficit,
            dificuldade="dificil"
        ))

        return solutions
```

#### 4.3. Relatório Integrado de Metas

```python
async def generate_goal_progress_report(user_id: int, goal_id: int) -> GoalProgressReport:
    """
    Gera relatório de progresso de meta financeira.
    """
    goal = db.query(FinancialGoal).get(goal_id)

    # Calcula progresso atual
    total_saved = db.query(
        func.sum(Despesa.valor)
    ).filter(
        Despesa.user_id == user_id,
        Despesa.categoria == "Poupanca/Meta",
        Despesa.meta_id == goal_id
    ).scalar() or 0

    # Calcula taxa de poupança dos últimos 30 dias
    recent_savings = db.query(
        func.sum(Despesa.valor)
    ).filter(
        Despesa.user_id == user_id,
        Despesa.categoria == "Poupanca/Meta",
        Despesa.meta_id == goal_id,
        Despesa.data >= datetime.now() - timedelta(days=30)
    ).scalar() or 0

    # Projeção
    meses_restantes = (goal.data_alvo - datetime.now()).days / 30
    projecao = total_saved + (recent_savings * meses_restantes)

    report = GoalProgressReport(
        meta=goal,
        progresso_atual=total_saved,
        percentual_concluido=(total_saved / goal.valor_alvo) * 100,
        taxa_poupanca_mensal=recent_savings,
        projecao_final=projecao,
        status="on_track" if projecao >= goal.valor_alvo else "at_risk"
    )

    # Adiciona recomendações se estiver fora do caminho
    if report.status == "at_risk":
        deficit_projetado = goal.valor_alvo - projecao
        report.recomendacoes = await GoalPlanner()._generate_deficit_solutions(
            user_id,
            deficit_projetado / meses_restantes
        )

    return report
```

---

## 📊 Modelos de Dados

### Database Schema

```python
class Despesa(Base):
    """
    Tabela principal de despesas com contexto comportamental.
    """
    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Dados da transação
    valor = Column(Numeric(10, 2), nullable=False)
    estabelecimento = Column(String(255))
    descricao = Column(Text)
    data = Column(DateTime, nullable=False)
    tipo = Column(Enum("debito", "credito", name="tipo_transacao"))

    # Categorização
    categoria = Column(String(100))  # ex: "Alimentacao/Delivery"
    subcategoria = Column(String(100))
    status = Column(
        Enum("nao_categorizado", "categorizado", "revisao", name="status_despesa"),
        default="nao_categorizado"
    )

    # Rastreamento
    fonte = Column(
        Enum("notificacao_automatica", "importacao_lote", "manual", name="fonte_despesa"),
        nullable=False
    )
    external_id = Column(String(255))  # ID do banco (para deduplicação)

    # 🧠 CONTEXTO COMPORTAMENTAL (chave do módulo!)
    contexto_comportamental = Column(JSONB, default={})
    # Exemplo de estrutura:
    # {
    #   "carga_trabalho": 95,
    #   "nivel_stress": 8,
    #   "horas_sono": 5.5,
    #   "fase_ciclo": "lutea",
    #   "energia": 4,
    #   "eventos_recentes": ["deadline_projeto_x", "reuniao_dificil"]
    # }

    # Metas
    meta_id = Column(Integer, ForeignKey("metas_financeiras.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="despesas")
    meta = relationship("FinancialGoal", back_populates="despesas")


class Categoria(Base):
    """
    Categorias hierárquicas de despesas.
    """
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)  # ex: "Alimentacao"
    parent_id = Column(Integer, ForeignKey("categorias.id"))  # para hierarquia
    cor = Column(String(7))  # hex color para UI
    icone = Column(String(50))  # emoji ou ícone
    tipo = Column(Enum("fixa", "variavel", "investimento", name="tipo_categoria"))

    # Relacionamentos
    subcategorias = relationship("Categoria", back_populates="parent")
    parent = relationship("Categoria", remote_side=[id], back_populates="subcategorias")


class FinancialGoal(Base):
    """
    Metas financeiras de longo prazo.
    """
    __tablename__ = "metas_financeiras"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Detalhes da meta
    titulo = Column(String(255), nullable=False)  # ex: "Viagem Japão 2027"
    descricao = Column(Text)
    valor_alvo = Column(Numeric(12, 2), nullable=False)
    data_alvo = Column(Date, nullable=False)
    categoria = Column(String(100))  # ex: "viagem", "emergencia", "aposentadoria"

    # Planejamento
    economia_mensal_necessaria = Column(Numeric(10, 2))
    taxa_poupanca_atual = Column(Numeric(10, 2))

    # Viabilidade (JSONB)
    viabilidade = Column(JSONB, default={})
    # Exemplo:
    # {
    #   "viavel": false,
    #   "deficit_mensal": 350.00,
    #   "sugestoes": [...]
    # }

    # Status
    status = Column(
        Enum("ativo", "pausado", "concluido", "cancelado", name="status_meta"),
        default="ativo"
    )
    progresso_percentual = Column(Numeric(5, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="metas_financeiras")
    despesas = relationship("Despesa", back_populates="meta")


class PrevisaoGastos(Base):
    """
    Previsões mensais de gastos por categoria.
    """
    __tablename__ = "previsao_gastos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Período
    mes = Column(Integer, nullable=False)  # 1-12
    ano = Column(Integer, nullable=False)

    # Previsão por categoria (JSONB)
    previsoes = Column(JSONB, nullable=False)
    # Exemplo:
    # {
    #   "Alimentacao": {
    #     "valor_previsto": 800.00,
    #     "confianca": 0.85,
    #     "tendencia": "estavel"
    #   },
    #   "Transporte": {...}
    # }

    # Alertas detectados
    alertas = Column(JSONB, default=[])

    # Acurácia (calculada após o mês)
    valor_real_total = Column(Numeric(10, 2))
    acuracia_percentual = Column(Numeric(5, 2))

    created_at = Column(DateTime, default=datetime.utcnow)


class SpendingBlock(Base):
    """
    Bloqueios temporários de categorias de gasto.
    """
    __tablename__ = "spending_blocks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Bloqueio
    categoria = Column(String(100), nullable=False)
    inicio = Column(DateTime, nullable=False)
    fim = Column(DateTime, nullable=False)
    ativo = Column(Boolean, default=True)

    # Contexto
    motivo = Column(String(255))  # ex: "prevencao_gasto_impulsivo"
    trigger_event = Column(String(100))  # ex: "overload_detected"

    # Resultado
    gastos_evitados = Column(Integer, default=0)  # contador
    efetividade = Column(Numeric(5, 2))  # % de redução de gastos

    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔌 API Endpoints

### Expenses

```python
# Listar despesas com filtros
GET /api/v1/wealth/expenses
  ?categoria=Alimentacao
  &data_inicio=2025-11-01
  &data_fim=2025-11-30
  &status=categorizado

# Criar despesa manual
POST /api/v1/wealth/expenses
{
  "valor": 45.90,
  "estabelecimento": "iFood",
  "data": "2025-11-17T20:30:00",
  "categoria": "Alimentacao/Delivery"
}

# Atualizar categorização
PATCH /api/v1/wealth/expenses/{id}
{
  "categoria": "Alimentacao/Delivery",
  "status": "categorizado"
}

# Deletar despesa
DELETE /api/v1/wealth/expenses/{id}
```

### Import & Reconciliation

```python
# Importar extrato
POST /api/v1/wealth/import
Content-Type: multipart/form-data
{
  "file": <arquivo.csv>,
  "format": "csv",
  "banco": "nubank",
  "auto_categorize": true
}

# Obter relatório de importação
GET /api/v1/wealth/import/{import_id}/report
```

### Behavioral Analysis

```python
# Obter insights comportamentais
GET /api/v1/wealth/insights
  ?period_days=90

Response:
{
  "insights": [
    {
      "tipo": "correlacao_stress_delivery",
      "mensagem": "40% dos gastos com delivery ocorrem em stress alto",
      "impacto": "medio",
      "economia_potencial": 200.00
    }
  ],
  "recomendacoes": [...]
}

# Análise de padrão específico
POST /api/v1/wealth/analyze-pattern
{
  "behavioral_factor": "nivel_stress",
  "categoria": "Alimentacao/Delivery",
  "threshold": 7
}
```

### Savings & Blocks

```python
# Ativar bloqueio de categoria
POST /api/v1/wealth/blocks
{
  "categoria": "Alimentacao/Delivery",
  "duration_hours": 2,
  "motivo": "prevencao_gasto_impulsivo"
}

# Listar bloqueios ativos
GET /api/v1/wealth/blocks/active

# Desativar bloqueio
DELETE /api/v1/wealth/blocks/{id}
```

### Forecast & Goals

```python
# Obter previsão de gastos
GET /api/v1/wealth/forecast
  ?months_ahead=3

Response:
{
  "periodo": "Próximos 3 meses",
  "categorias": [
    {
      "categoria": "Alimentacao",
      "valor_medio_mensal": 800.00,
      "tendencia": "estavel",
      "confianca": 0.85
    }
  ],
  "alertas": [...]
}

# Criar meta financeira
POST /api/v1/wealth/goals
{
  "titulo": "Viagem Japão 2027",
  "valor_alvo": 30000.00,
  "data_alvo": "2027-06-01",
  "categoria": "viagem"
}

# Obter progresso de meta
GET /api/v1/wealth/goals/{id}/progress

Response:
{
  "meta": {...},
  "progresso_atual": 5400.00,
  "percentual_concluido": 18.0,
  "taxa_poupanca_mensal": 900.00,
  "projecao_final": 27000.00,
  "status": "at_risk",
  "deficit_projetado": 3000.00,
  "recomendacoes": [
    {
      "tipo": "reducao_gastos",
      "titulo": "Reduzir Gastos Variáveis",
      "impacto_mensal": 125.00
    }
  ]
}
```

---

## 🔗 Integrações

### Event Bus Events

```python
# Eventos que o Wealth PUBLICA
EventType.EXPENSE_DETECTED = "expense.detected"
EventType.EXPENSE_NEEDS_CATEGORIZATION = "expense.needs_categorization"
EventType.SPENDING_BLOCK_ACTIVATED = "spending_block.activated"
EventType.GOAL_AT_RISK = "goal.at_risk"
EventType.SAVINGS_OPPORTUNITY_DETECTED = "savings.opportunity_detected"

# Eventos que o Wealth OUVE
EventType.FINANCIAL_TRANSACTION_DETECTED = "notification.financial_transaction"
EventType.ENERGY_LOW = "wellness.energy_low"
EventType.OVERLOAD_DETECTED = "capacity.overload_detected"
EventType.CYCLE_PHASE_CHANGED = "wellness.cycle_phase_changed"
EventType.PROJECT_INVOICED = "projects.invoiced"
```

### Integração com Wellness Coach

```python
# O Wealth consulta fase do ciclo ao analisar padrões
@event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED)
async def on_cycle_phase_change(event: CyclePhaseEvent):
    """
    Quando a fase do ciclo muda, verifica padrões de gasto.
    """
    if event.new_phase == "lutea":
        # Ativa alertas para compras por impulso
        await savings_advisor.activate_impulse_watch(
            user_id=event.user_id,
            categoria="Compras/Impulso"
        )
```

### Integração com Capacity Guardian

```python
# O Wealth ouve eventos de sobrecarga
@event_bus.subscribe(EventType.OVERLOAD_DETECTED)
async def on_overload(event: OverloadEvent):
    """
    Quando sobrecarga é detectada, previne gastos impulsivos.
    """
    pattern = await behavioral_finance_agent.get_pattern(
        user_id=event.user_id,
        context="stress_alto"
    )

    if pattern and pattern.categoria == "Alimentacao/Delivery":
        await savings_advisor.send_proactive_alert(event.user_id, pattern)
```

### Integração com Projects Manager

```python
# O Wealth consulta faturamento freelance
async def calculate_monthly_income(user_id: int) -> float:
    """
    Calcula faturamento total (freelance + salário).
    """
    # Busca invoices dos últimos 3 meses
    invoices = await projects_service.get_invoices(
        user_id=user_id,
        period_days=90
    )

    freelance_income = sum([inv.valor_total for inv in invoices]) / 3

    # Busca salário fixo
    salario = await settings_service.get_user_setting(user_id, "salario_fixo")

    return freelance_income + (salario or 0)
```

### Integração com Focus Agent

```python
# O Focus Agent detecta e-mails bancários
@event_bus.subscribe(EventType.NOTIFICATION_RECEIVED)
async def on_notification(event: NotificationEvent):
    """
    ClassifierAgent identifica transações financeiras.
    """
    if event.tipo == "transacao_financeira":
        # Publica evento para o Wealth processar
        event_bus.publish(
            EventType.FINANCIAL_TRANSACTION_DETECTED,
            FinancialTransactionEvent(
                email_body=event.body,
                timestamp=event.timestamp,
                user_id=event.user_id
            )
        )
```

---

## 💡 Casos de Uso

### Caso 1: Captura Automática de Transação

```
Fluxo completo de captura em tempo real:

1. E-mail do Nubank chega às 20:30
   "Compra aprovada: R$ 45,90 - iFood"

2. Focus Agent detecta e-mail bancário
   └─> ClassifierAgent: tipo = 'transacao_financeira'

3. Event Bus: FINANCIAL_TRANSACTION_DETECTED

4. WealthAgent processa com LLM
   └─> Extrai: {valor: 45.90, estabelecimento: "iFood"}

5. Context Manager: busca estado às 20:30
   └─> {stress: 8/10, sono: 5.5h, fase: "lutea"}

6. BehavioralFinanceAgent: armazena com contexto
   └─> contexto_comportamental salvono JSONB

7. Notificação ao usuário:
   "💳 Compra detectada: R$ 45,90 - iFood
    Categorizar como 'Alimentacao/Delivery'?"

8. Usuário confirma categorização

9. SavingsAdvisor: analisa padrão
   └─> Detecta: stress alto → delivery (padrão recorrente)

10. Alerta proativo futuro configurado
```

### Caso 2: Prevenção Proativa de Gasto

```
Fluxo de prevenção baseada em contexto:

1. Capacity Guardian detecta sobrecarga
   └─> Event: OVERLOAD_DETECTED (stress: 9/10)

2. SavingsAdvisor ouve evento

3. Consulta padrões do BehavioralFinanceAgent
   └─> Encontra: "Stress >7 → R$200/mês em delivery"

4. Verifica alternativas disponíveis
   └─> Habit Tracker: refeição planejada existe

5. Envia notificação proativa:
   "🛡️ Proteção de Gastos Ativada

   Samara, seu stress está em 9/10.

   Nos últimos 3 meses, isso levou a gastos
   extras de R$ 200 com delivery.

   Sugestões:
   ✅ Usar a refeição planejada de hoje
   🚫 Ativar bloqueio de 2h em apps de delivery
   🧘 10min de meditação (reduz stress 30%)"

6. Usuário escolhe: "Ativar bloqueio"

7. SpendingBlock criado (2h de duração)

8. Após 2h: análise de efetividade
   └─> Gasto evitado: R$ 60 (estimado)
```

### Caso 3: Planejamento de Meta Financeira

```
Fluxo de criação e análise de meta:

1. Usuário cria meta:
   "Viagem Japão 2027 - R$ 30.000"

2. GoalPlanner calcula:
   └─> Meses até meta: 24
   └─> Economia mensal: R$ 1.250

3. ForecastAgent analisa viabilidade:
   a) Calcula faturamento:
      - Freelance: R$ 4.500/mês (média 3 meses)
      - Salário Syssa: R$ 2.000/mês
      - Total: R$ 6.500/mês

   b) Prevê gastos:
      - Fixos: R$ 2.500
      - Variáveis: R$ 3.100
      - Total: R$ 5.600/mês

   c) Taxa de poupança atual:
      R$ 6.500 - R$ 5.600 = R$ 900/mês

4. Detecta défice:
   R$ 1.250 (necessário) - R$ 900 (atual) = R$ 350/mês

5. Gera soluções personalizadas:

   OPÇÃO 1 (Finanças):
   "Reduzir 'Restaurantes' de R$ 400 para R$ 50/mês
    Economia: R$ 350 ✅ Cobre o défice
    Dificuldade: Média"

   OPÇÃO 2 (Carreira):
   "Aumentar valor/hora de R$ 75 para R$ 82
    (+9% aumento)
    Impacto: +R$ 420/mês
    Dificuldade: Difícil"

   OPÇÃO 3 (Capacidade):
   "Aceitar +1 projeto pequeno/mês
    (Você tem 15h disponíveis)
    5h × R$ 75 = R$ 375/mês
    Dificuldade: Média"

6. Usuário escolhe combinação:
   - Reduzir restaurantes em 50% (R$ 200)
   - Aceitar +2h/mês de freelance (R$ 150)
   - Total: R$ 350 ✅

7. Sistema monitora progresso mensalmente
```

---

## 🗓️ Roadmap

### Fase 1: MVP 
- ✅ Modelos de dados (Despesa, Categoria, FinancialGoal)
- ✅ ParseNotificationExpense skill
- ✅ BehavioralFinanceAgent (análise causal)
- ✅ API básica (CRUD despesas)

### Fase 2: Inteligência 
- ✅ ImportBatchExpense skill
- ✅ SavingsAdvisor (alertas proativos)
- ✅ SpendingBlock system
- ✅ Integração com Event Bus

### Fase 3: Previsão
- ✅ ForecastAgent (previsão de gastos)
- ✅ GoalPlanner (metas financeiras)
- ✅ Análise de viabilidade
- ✅ Geração de soluções para défice

### Fase 4: Frontend 
- [ ] Dashboard financeiro
- [ ] Gráficos de gastos por categoria
- [ ] Visualização de insights comportamentais
- [ ] Interface de metas e progresso
- [ ] Configuração de bloqueios de gasto

### Fase 5: Avançado (futuro)
- [ ] Machine Learning para previsões
- [ ] Integração com Open Banking
- [ ] Sincronização automática de contas
- [ ] Relatórios de imposto de renda
- [ ] Investimentos e patrimônio líquido

---

## 📚 Referências

### Finanças Comportamentais
- **Thinking, Fast and Slow** - Daniel Kahneman
- **Predictably Irrational** - Dan Ariely
- **The Psychology of Money** - Morgan Housel

### Integração com Bem-estar
- **Burnout** - Emily Nagoski (conexão stress → gastos)
- **Period Power** - Maisie Hill (ciclo → comportamento)

### Frameworks Técnicos
- **Event-Driven Architecture** - Martin Fowler
- **Domain-Driven Design** - Eric Evans

---

**Desenvolvido com ❤️ por Samara Cassie**

*Versão: 1.0 - Draft Inicial*
*Última atualização: 2025-11-17*
