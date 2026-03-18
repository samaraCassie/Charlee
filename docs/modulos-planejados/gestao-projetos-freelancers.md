Tbm terá um módulo de gestão de projetos e freelancers

---

🧭 Documentação Técnica — Agente Profissional de Inteligência de Projetos e Carreira (Samara AI Career System)


---

📘 1. Visão Geral do Sistema

1.1. Objetivo

Desenvolver um sistema de agentes inteligentes autônomos capazes de:

Monitorar plataformas de freelancers;

Analisar e avaliar oportunidades de projetos;

Estimar valor, complexidade e viabilidade técnica;

Aprender com o histórico de decisões e entregas;

Gerar relatórios sobre evolução técnica, financeira e comportamental;

Apoiar o posicionamento estratégico e o personal branding da usuária.



---

1.2. Contexto

O sistema apoiará uma profissional (Samara) especializada em desenvolvimento full-stack e orquestração de agentes de IA, fornecendo:

Decisões de aceitação ou rejeição de projetos;

Insights estratégicos sobre desempenho;

Aprendizado contínuo sobre valor de mercado e evolução pessoal.



---

⚙️ 2. Escopo do Sistema

2.1. Escopo Funcional

O sistema será composto por múltiplos agentes especializados, atuando em cooperação, orquestrados por um Agente Gestor Central.

Agente	Função Principal	Descrição

🧩 Agente Coletor	Monitoramento	Busca e coleta de projetos nas plataformas configuradas
🧠 Agente Analisador	Análise semântica	Interpreta descrições, infere escopo, stack e nível técnico
⚖️ Agente Avaliador	Precificação e viabilidade	Estima valor justo, prazo e classifica relevância
💬 Agente Negociador	Comunicação estratégica	Gera mensagens diplomáticas de contra-proposta
📊 Agente Analítico	Desempenho e histórico	Compila dados, métricas e insights sobre evolução
🪞 Agente de Autoaprendizado	Aprendizado contínuo	Ajusta parâmetros conforme feedbacks e resultados
🧭 Agente de Branding & Insights	Estratégia e reflexão	Analisa forças, fraquezas e posicionamento profissional



---

📥 2.2. Estratégias de Coleta de Dados (RF01)

O sistema suporta múltiplos métodos de entrada de oportunidades, priorizando abordagens legais e sustentáveis.

#### Métodos de Coleta

| Método | Prioridade | Status | Descrição |
|--------|------------|--------|-----------|
| **Smart Paste (LLM)** | Alta | 🎯 MVP | Usuário cola texto → LLM extrai dados estruturados |
| **Bookmarklet** | Média | 🎯 MVP | 1 clique no browser → extrai dados da página |
| **APIs Oficiais** | Alta | 🔜 Pós-MVP | Upwork API, Freelancer.com API (requer aprovação) |
| **RSS Feeds** | Baixa | 🔜 Futuro | Job boards com feeds públicos |
| **Manual Entry** | Baixa | ✅ Existe | Formulário tradicional (fallback) |

---

#### 2.2.1 Smart Paste (Extração Inteligente com LLM)

**Fluxo:**
```
┌─────────────────────────────────────────────────────┐
│  Usuário cola URL ou texto completo do projeto      │
│  ↓                                                  │
│  "https://upwork.com/jobs/~01abc123"               │
│  OU                                                 │
│  "Looking for Python developer to build..."         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  LLM (GPT-4) extrai automaticamente:                │
│  • Título                                           │
│  • Descrição limpa                                  │
│  • Budget (se mencionado)                           │
│  • Skills requeridas                                │
│  • Deadline estimado                                │
│  • Nome do cliente (se disponível)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Usuário confirma/edita os dados extraídos          │
│  ↓                                                  │
│  Salva no banco → Análise semântica → Scoring       │
└─────────────────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Funciona com qualquer fonte (Upwork, email, WhatsApp, LinkedIn)
- ✅ LLM adapta a diferentes formatos automaticamente
- ✅ Não depende de APIs externas ou aprovações
- ✅ 100% legal (usuário controla o input)

**Exemplo de Input:**
```
Estou procurando um desenvolvedor Python experiente para construir
uma API REST com FastAPI. O projeto inclui integração com PostgreSQL,
autenticação JWT e deploy na AWS. Budget: $2000-3000.
Preciso que seja concluído em 2 semanas.
```

**Output Estruturado:**
```json
{
  "title": "API REST com FastAPI",
  "description": "Construir API REST com FastAPI incluindo integração
                  com PostgreSQL, autenticação JWT e deploy na AWS",
  "skills": ["Python", "FastAPI", "PostgreSQL", "JWT", "AWS"],
  "budget_min": 2000,
  "budget_max": 3000,
  "deadline_days": 14,
  "complexity_estimate": 7
}
```

---

#### 2.2.2 Bookmarklet (Extração via Browser)

**O que é:** Um "bookmark inteligente" - código JavaScript salvo como favorito que extrai dados da página atual com 1 clique.

**Fluxo:**
```
┌─────────────────────────────────────────────────────┐
│ Usuário no Upwork vê projeto interessante           │
│           ↓                                         │
│ Clica no bookmark "⭐ Charlee"                      │
│           ↓                                         │
│ JavaScript extrai dados do DOM da página            │
│           ↓                                         │
│ Abre Charlee em nova aba com dados preenchidos      │
└─────────────────────────────────────────────────────┘
Passos: 1 clique
```

**Plataformas Suportadas:**
- ✅ Upwork (seletores CSS mapeados)
- ✅ Freelancer.com (seletores CSS mapeados)
- ✅ LinkedIn Jobs (seletores CSS mapeados)
- 🔜 Extensível para outras plataformas

**Código do Bookmarklet:**
```javascript
javascript:(function(){
  /* Charlee Project Extractor v1.0 */

  const CHARLEE_URL = 'http://localhost:8501'; // ou URL de produção
  const url = window.location.href;
  let project = { url, source: 'unknown' };

  // Detector de plataforma e extração
  if (url.includes('upwork.com')) {
    project.source = 'upwork';
    project.title = document.querySelector('h2[itemprop="title"]')?.innerText?.trim();
    project.description = document.querySelector('[data-test="Description"]')?.innerText?.trim();
    project.budget = document.querySelector('[data-test="budget"]')?.innerText?.trim();
    project.skills = Array.from(document.querySelectorAll('.skill-tag, [data-test="skill"]'))
      .map(s => s.innerText.trim()).join(', ');
  }
  else if (url.includes('freelancer.com')) {
    project.source = 'freelancer';
    project.title = document.querySelector('h1.project-title')?.innerText?.trim();
    project.description = document.querySelector('.project-description')?.innerText?.trim();
    project.budget = document.querySelector('.budget-amount')?.innerText?.trim();
  }
  else if (url.includes('linkedin.com/jobs')) {
    project.source = 'linkedin';
    project.title = document.querySelector('.job-details-jobs-unified-top-card__job-title')?.innerText?.trim();
    project.description = document.querySelector('.jobs-description__content')?.innerText?.trim();
  }

  // Abre Charlee com dados
  const encoded = encodeURIComponent(JSON.stringify(project));
  window.open(`${CHARLEE_URL}?project=${encoded}`, 'charlee_analysis');
})();
```

**Vantagens:**
- ✅ Zero instalação (só arrastar para favoritos)
- ✅ Instantâneo (sem chamada de API)
- ✅ 100% legal (roda no browser do usuário)
- ✅ Funciona offline (extração local)

**Manutenção:**
- ⚠️ Seletores CSS podem quebrar se plataforma mudar layout
- 📝 Atualizar seletores periodicamente

---

#### 2.2.3 APIs Oficiais (Pós-MVP)

Quando aprovação for obtida, integrar com APIs oficiais:

| Plataforma | API | Status | Processo |
|------------|-----|--------|----------|
| **Upwork** | [Developer API](https://www.upwork.com/services/api/apply) | 🔜 Pendente | Requer aprovação (2-4 semanas) |
| **Freelancer.com** | [Freelancer API](https://developers.freelancer.com/) | 🔜 Pendente | API pública disponível |
| **RemoteOK** | JSON público | ✅ Disponível | Sem aprovação necessária |
| **We Work Remotely** | RSS/JSON | ✅ Disponível | Sem aprovação necessária |

**Nota sobre Web Scraping:**
> ❌ **NÃO implementar web scraping automático**
>
> Plataformas como Upwork e Freelancer têm proteções anti-bot e proíbem scraping nos ToS.
> Riscos: bloqueio de conta, ações legais.
>
> ✅ Usar apenas: APIs oficiais, bookmarklet (usuário controla), smart paste (usuário cola).

---

#### 2.2.4 Comparação: Smart Paste vs Bookmarklet

| Aspecto | Smart Paste | Bookmarklet |
|---------|-------------|-------------|
| **Onde roda** | Backend (servidor) | Browser (cliente) |
| **Input do usuário** | Cola texto | Clica 1 botão |
| **Extração de dados** | LLM analisa texto | JavaScript lê DOM |
| **Precisão** | Alta (LLM entende contexto) | Média (depende de seletores) |
| **Manutenção** | Baixa (LLM adapta) | Média (seletores quebram) |
| **Custo** | ~$0.01-0.05/extração | Zero |
| **Velocidade** | 2-5 segundos | Instantâneo |

**Recomendação:** Usar ambos!
- **Bookmarklet** → Navegando em plataformas conhecidas (1 clique)
- **Smart Paste** → Projetos de email, WhatsApp, sites sem suporte

---

�� 3. Requisitos Funcionais (RF)

ID	Requisito	Descrição	Prioridade

RF01	Coletar oportunidades de projetos	O sistema deve permitir entrada via Smart Paste, Bookmarklet, APIs oficiais (quando disponíveis) ou manual entry.	Alta
RF02	Analisar semanticamente descrições	O agente deve interpretar o escopo mesmo que não haja termos técnicos.	Alta
RF03	Classificar nível técnico	Determinar se o projeto é júnior, pleno, sênior ou especializado.	Alta
RF04	Estimar valor e prazo	Calcular preço sugerido e prazo realista conforme complexidade.	Alta
RF05	Avaliar viabilidade	Comparar valor e prazo propostos com os estimados e identificar desequilíbrios.	Alta
RF06	Gerar contra-proposta diplomática	Criar mensagens automáticas e adaptativas de negociação.	Média
RF07	Registrar histórico de projetos	Armazenar todos os dados, decisões e resultados em banco de dados.	Alta
RF08	Aprender com feedback	Ajustar valores e pesos com base em decisões (aceitar/recusar).	Alta
RF09	Gerar relatórios analíticos	Exibir métricas de desempenho financeiro, técnico e estratégico.	Média
RF10	Detectar padrões e tendências	Identificar áreas de especialização e oportunidades de mercado.	Média
RF11	Analisar comunicação e evolução pessoal	Registrar aprendizados, reflexões e feedbacks qualitativos.	Baixa
RF12	Gerar relatórios de branding	Criar insights sobre portfólio e diferenciais profissionais.	Média



---

⚙️ 4. Requisitos Não Funcionais (RNF)

ID	Requisito	Descrição

RNF01	Desempenho	O agente deve processar novas oportunidades em menos de 10 segundos.
RNF02	Escalabilidade	Suportar múltiplas fontes de dados simultaneamente.
RNF03	Persistência	Manter histórico detalhado (mínimo 2 anos de dados).
RNF04	Segurança	Tokens das plataformas devem ser criptografados.
RNF05	Privacidade	Dados pessoais e de clientes devem seguir LGPD.
RNF06	Auditabilidade	Todas as decisões e sugestões do agente devem ser rastreáveis.
RNF07	Explicabilidade	Cada insight gerado deve vir acompanhado de justificativa textual.
RNF08	Extensibilidade	Permitir adicionar novas plataformas e agentes com mínima refatoração.
RNF09	Interoperabilidade	Comunicação via APIs REST e Webhooks.
RNF10	Observabilidade	Logs e métricas de uso devem ser monitoráveis.



---

📐 5. Regras de Negócio (RN)

ID	Regra	Descrição

RN01	Cada projeto deve ser analisado apenas uma vez por coleta.	
RN02	A precificação deve considerar hora base, margem mínima e fator de especialização.	
RN03	Projetos com valor ou prazo inviável devem ser marcados como “não recomendados”.	
RN04	Feedbacks de aceitação/rejeição influenciam o aprendizado de precificação.	
RN05	Insights devem ser gerados semanalmente e armazenados como relatórios.	
RN06	Reflexões pessoais adicionadas manualmente entram no aprendizado qualitativo.	
RN07	O agente não deve enviar mensagens automáticas a clientes sem confirmação.	
RN08	Aumentos automáticos no valor/hora só podem ocorrer com base em 3 ou mais entregas bem-sucedidas.	



---

🤖 5.1. Sistema de Machine Learning e Aprendizado Contínuo (RF08)

> ⏳ **STATUS: PLANEJADO PARA V2 DO MÓDULO FREELANCER**
>
> Esta seção documenta o sistema de ML que será implementado na **próxima versão** deste módulo.
> O MVP do módulo Freelancer funcionará com regras fixas de precificação.

O sistema não deve apenas **coletar dados**, mas **aprender e melhorar** com o tempo.

#### Analogia: A Diferença entre "Estrutura" e "Aprendizado Real"

**Situação ERRADA (só estrutura):**
```
Academia:
- ✅ Você comprou balança digital
- ✅ Você anota o peso todo dia: 70kg, 71kg, 70.5kg...
- ❌ Você não faz NADA com os dados

Resultado: Dados existem, mas não há melhoria
```

**Situação CORRETA (aprendizado real):**
```
Academia:
- ✅ Balança + caderno
- ✅ Personal trainer (algoritmo) analisa padrões
- ✅ Sistema ajusta: "peso aumentou após comer X → reduza Y"
- ✅ Próxima semana: peso diminuiu!

Resultado: Sistema APRENDE e MELHORA
```

#### No Contexto do Charlee Projects

**SEM aprendizado (problema atual):**
```python
# Mês 1
projeto = analyzer.analyze("chatbot e-commerce Python+React")
# Sistema diz: "$2,500"
# Você aceita por: $3,200 (cliente pagou mais!)
# Erro: -21.8%

# Mês 2 - projeto similar
novo_projeto = analyzer.analyze("chatbot e-commerce similar")
# Sistema AINDA diz: "$2,500" ❌
# Sistema NÃO aprendeu que errou!
```

**COM aprendizado (objetivo):**
```python
# Mês 1
projeto = analyzer.analyze("chatbot e-commerce Python+React")
# Sistema diz: "$2,500"
# Você aceita por: $3,200

# Sistema ANALISA o erro:
learner.record_feedback(project_id=123, actual_price=3200)
# "Hmm, projetos 'chatbot e-commerce' eu subestimei 28%"

# Sistema AJUSTA:
# fator_especializacao['chatbot_ecommerce'] = 1.35 (era 1.0)

# Mês 2 - projeto similar
novo_projeto = analyzer.analyze("chatbot e-commerce similar")
# Sistema AGORA diz: "$3,100" ✅
# Sistema APRENDEU!
```

---

#### 5.1.1 Componentes de Aprendizado

| Componente | Função | Prioridade |
|------------|--------|------------|
| **PricingLearner** | Ajusta fatores de precificação por categoria | Alta |
| **RejectionPatternLearner** | Detecta red flags que causam rejeições | Média |
| **HourlyRateOptimizer** | Otimiza valor/hora baseado em aceitação | Alta |
| **ProjectSimilarityLearner** | Usa embeddings para prever outcomes | Baixa (V3+) |

---

#### 5.1.2 PricingLearner - Ajuste por Categoria

```python
class PricingLearner:
    """Aprende com decisões reais e ajusta precificação"""

    def __init__(self, db):
        self.db = db
        self.min_samples = 3  # Precisa 3+ exemplos para ajustar

    def record_outcome(self, project_id: int, outcome: ProjectOutcome):
        """Registra resultado de um projeto"""

        project = self.db.get_project(project_id)

        # Calcula erros
        price_error = None
        if outcome.actual_price:
            price_error = (outcome.actual_price - project.suggested_price) / project.suggested_price
            # Ex: (3200 - 2500) / 2500 = 0.28 = +28% erro

        hours_error = None
        if outcome.actual_hours:
            hours_error = (outcome.actual_hours - project.estimated_hours) / project.estimated_hours

        # Salva no banco
        learning_record = LearningRecord(
            project_id=project_id,
            user_decision=outcome.decision,
            actual_price=outcome.actual_price,
            actual_hours=outcome.actual_hours,
            price_error=price_error,
            hours_error=hours_error,
            recorded_at=datetime.now()
        )

        self.db.save(learning_record)

        # Dispara análise de aprendizado
        self.analyze_and_adjust(project)

    def analyze_and_adjust(self, project):
        """Analisa padrões e ajusta parâmetros"""

        # Busca projetos similares no histórico
        similar_projects = self.db.query("""
            SELECT * FROM freelance_opportunities fo
            JOIN learning_records lr ON fo.id = lr.project_id
            WHERE fo.category = %s
              AND fo.complexity_estimated BETWEEN %s - 1 AND %s + 1
              AND lr.actual_price IS NOT NULL
            ORDER BY lr.recorded_at DESC
            LIMIT 10
        """, (project.category, project.complexity, project.complexity))

        if len(similar_projects) < self.min_samples:
            return  # Não tem dados suficientes ainda

        # Calcula erro médio nessa categoria
        avg_price_error = sum(p.price_error for p in similar_projects) / len(similar_projects)

        # Se erro consistente > 15%, ajusta
        if abs(avg_price_error) > 0.15:
            self._adjust_category_factor(
                category=project.category,
                complexity=project.complexity,
                error=avg_price_error
            )

    def _adjust_category_factor(self, category: str, complexity: int, error: float):
        """Ajusta fator multiplicador para categoria/complexidade"""

        params = self.db.get_pricing_params()

        # Calcula novo fator (ajuste gradual de 50% do erro)
        current_factor = params['fator_especializacao'].get(category, 1.0)
        adjustment = 1 + (error * 0.5)  # Ajuste conservador
        new_factor = current_factor * adjustment

        # Limita entre 0.5x e 3.0x (proteção contra outliers)
        new_factor = max(0.5, min(3.0, new_factor))

        # Atualiza no banco
        params['fator_especializacao'][category] = new_factor
        self.db.update_pricing_params(params)

        logger.info(f"📊 Ajustado fator de '{category}': {current_factor:.2f} → {new_factor:.2f}")
        logger.info(f"   Baseado em erro médio de {error:.1%} em {self.min_samples}+ projetos")
```

---

#### 5.1.3 RejectionPatternLearner - Detecta Red Flags

```python
class RejectionPatternLearner:
    """Aprende por que a usuária rejeita projetos"""

    def learn_from_rejections(self):
        """Identifica red flags que causam rejeições"""

        # Busca projetos rejeitados que tinham score alto
        # (falsos positivos - sistema recomendou mas usuária rejeitou)
        false_positives = self.db.query("""
            SELECT * FROM freelance_opportunities
            WHERE score_final > 0.7
              AND user_decision = 'rejected'
        """)

        # Extrai palavras/padrões em comum
        rejection_keywords = []

        for project in false_positives:
            # Palavras que aparecem em rejeitados mas não em aceitos
            rejection_keywords.extend(
                self._extract_negative_keywords(project.description)
            )

        # Encontra padrões (palavras que aparecem em 3+ rejeições)
        common_keywords = Counter(rejection_keywords).most_common(10)

        for keyword, count in common_keywords:
            if count >= 3:
                self._add_red_flag_pattern(keyword)
                logger.info(f"🚩 Novo red flag detectado: '{keyword}' (aparece em {count} rejeições)")

        return common_keywords

    def _add_red_flag_pattern(self, keyword: str):
        """Adiciona nova regra de red flag ao sistema"""

        self.db.execute("""
            INSERT INTO red_flag_patterns (keyword, severity, count, created_at)
            VALUES (%s, 'medium', 1, NOW())
            ON CONFLICT (keyword) DO UPDATE SET count = count + 1
        """, (keyword,))
```

---

#### 5.1.4 HourlyRateOptimizer - Otimiza Valor/Hora

```python
class HourlyRateOptimizer:
    """Otimiza valor/hora baseado em taxa de aceitação real"""

    def optimize_hourly_rate(self):
        """Ajusta valor/hora para maximizar aceitação de bons projetos"""

        # Analisa últimos 30 dias
        recent_projects = self.db.query("""
            SELECT
                fo.suggested_price / fo.estimated_hours as suggested_hourly,
                lr.actual_price / lr.actual_hours as actual_hourly,
                lr.user_decision,
                fo.score_final
            FROM freelance_opportunities fo
            JOIN learning_records lr ON fo.id = lr.project_id
            WHERE lr.recorded_at > NOW() - INTERVAL '30 days'
              AND lr.actual_price IS NOT NULL
        """)

        if len(recent_projects) < 5:
            return None  # Dados insuficientes

        # Calcula taxa de aceitação por faixa de preço
        acceptance_by_rate = {}

        for project in recent_projects:
            rate_bucket = round(project.suggested_hourly / 10) * 10  # Faixas de $10

            if rate_bucket not in acceptance_by_rate:
                acceptance_by_rate[rate_bucket] = {'accepted': 0, 'total': 0}

            acceptance_by_rate[rate_bucket]['total'] += 1
            if project.user_decision == 'accepted':
                acceptance_by_rate[rate_bucket]['accepted'] += 1

        # Encontra taxa com melhor aceitação
        best_rate = max(
            acceptance_by_rate.keys(),
            key=lambda r: acceptance_by_rate[r]['accepted'] / max(acceptance_by_rate[r]['total'], 1)
        )

        # Atualiza gradualmente (80% atual + 20% ótimo)
        current_rate = self.db.get_pricing_params()['valor_hora_base']
        new_rate = current_rate * 0.8 + best_rate * 0.2

        self.db.update_pricing_params({'valor_hora_base': new_rate})

        logger.info(f"💰 Valor/hora ajustado: ${current_rate:.0f} → ${new_rate:.0f}")

        return {
            'old_rate': current_rate,
            'new_rate': new_rate,
            'change': new_rate - current_rate
        }
```

---

#### 5.1.5 Evolução Esperada do Sistema

| Período | Estado | Precisão | Comportamento |
|---------|--------|----------|---------------|
| **Mês 1** | "Burro" | ~60% | Usa apenas regras fixas |
| **Mês 2** | Aprendendo | ~75% | Começa a ajustar fatores |
| **Mês 3** | "Esperto" | ~85% | Detecta padrões de rejeição |
| **Mês 6+** | Personalizado | ~90%+ | Totalmente calibrado para o usuário |

**Resultado esperado:**
- Taxa de aceitação das recomendações: 45% → 78%
- Erro médio de precificação: 25% → 5%
- Red flags detectados automaticamente: 0 → 15+

---

#### 5.1.6 Implementação Faseada

| Fase | Componente | Esforço | Impacto |
|------|------------|---------|---------|
| **V1 (MVP)** | Sem ML - Regras fixas de precificação | - | Base funcional |
| **V2** | PricingLearner + HourlyRateOptimizer | 8-12h | Alto |
| **V2** | RejectionPatternLearner | 3-5h | Médio |
| **V3** | ProjectSimilarityLearner (embeddings) | 10-15h | Alto |

> 📌 **Decisão:** ML será implementado na **V2 do módulo Freelancer**, não no MVP.

**Versão para V2 (pós-MVP):**
```python
# Adicionar ao ProjectEvaluatorAgent existente:

def learn_from_outcome(self, project_id: int, actual_price: float):
    """Versão simples: apenas ajusta valor/hora base"""

    project = self.db.get(project_id)
    error = (actual_price - project.suggested_price) / project.suggested_price

    # Se erro consistente > 15%, ajusta valor/hora
    if abs(error) > 0.15:
        params = self.db.get_pricing_params()
        adjustment = 1 + (error * 0.1)  # Ajuste de 10% do erro
        params['valor_hora_base'] *= adjustment
        self.db.update_pricing_params(params)

        logger.info(f"💡 Valor/hora ajustado para ${params['valor_hora_base']:.0f}")
```

---

#### 🧠 6. Arquitetura de Agentes e Módulos

┌──────────────────────────────┐
│       Agente Gestor          │
│ Coordena os demais agentes   │
└──────────────┬───────────────┘
               │
┌──────────────┼──────────────────────────────────────────────────────────────────────────────┐
│              │                                                                              │
│     Núcleo de Execução                                 Núcleo de Aprendizado                │
│                                                                                             │
│ 🧩 Coletor  → coleta projetos                       🧠 Autoaprendizado → ajusta parâmetros  │
│ 🧠 Analisador → entende escopo                      📊 Analítico → compila métricas         │
│ ⚖️ Avaliador → precifica e avalia viabilidade       🪞 Branding → gera insights de carreira │
│ 💬 Negociador → contra-propostas                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘


---

#### 🧩 7. MVP (Versão 1.0)

Objetivo:

Provar a viabilidade técnica e conceitual do sistema.

Funcionalidades incluídas:

RF01–RF05: coleta, análise semântica, classificação de nível, precificação, e viabilidade.

Banco local (SQLite) para histórico.

Interface CLI ou script Python com prints de relatório básico.

Integração com uma plataforma (ex: Upwork via API).

Logs detalhados de decisões.


Não inclusos:

Interface web.

Feedback learning automatizado.

Análises de branding e comportamento.



---

#### 🚀 8. Versão 2.0 — Inteligência e Aprendizado

Funcionalidades adicionadas:

RF06–RF09: geração de contra-propostas e aprendizado contínuo.

Armazenamento de histórico detalhado.

Métricas básicas de desempenho (ticket médio, taxa de sucesso).

Geração de relatórios semanais automáticos.


Infraestrutura:

DynamoDB ou PostgreSQL.

Scheduler (AWS Lambda ou CRON).

API REST local para comunicação com UI futura.



---

#### 💡 9. Versão 3.0 — Inteligência Estratégica e Branding

Funcionalidades:

RF10–RF12: análises de portfólio, branding e insights pessoais.

Detecção de padrões e evolução técnica.

Correlação entre habilidades, tipos de projeto e lucro.

Geração de relatórios em PDF ou painel web (Streamlit / LangFlow).


Funcionalidades avançadas:

Recomendações automáticas de posicionamento (“enfatize automação IA em seu perfil”).

Análises emocionais e qualitativas baseadas nas observações manuais.



---

#### 🧠 10. Versão 4.0 — Autonomia e Coach Profissional

Funcionalidades:

Comunicação natural via chat (interação direta com o agente).

Aprendizado auto-reflexivo (“insight semanal sobre seu desempenho”).

Comparação temporal de evolução (gráficos de complexidade e valor médio).

Estratégia preditiva (“setor de IA em alta, priorize esses projetos”).

Geração automática de material de portfólio (descrições otimizadas de projetos).



---

#### 💾 11. Estrutura de Dados (resumo)

Entidade	Campos principais

Projeto	id, título, descrição, plataforma, complexidade, valor_sugerido, valor_cliente, prazo, aceito, resultado
Feedback	id_projeto, decisão, motivo, tempo_gasto, observacoes_pessoais
Parametros	valor_hora_base, margem_minima, fator_especializacao, limite_prazo
Relatorio	periodo, faturamento, taxa_sucesso, complexidade_media, setor_dominante
Insight	data, tipo, descricao, impacto, recomendacao



---

#### 📊 12. Tecnologias sugeridas

Categoria	Ferramenta

Framework de agentes	Agno
LLM	GPT-4o-mini / Claude 3.5
Banco de dados	DynamoDB (produção) / SQLite (MVP)
Dashboard	Streamlit / LangFlow
Scheduler	APScheduler / AWS Lambda
APIs externas	Upwork, Freelancer.com, Apify
Integração	Telegram Bot, Gmail API (alertas)



---

#### 🧭 13. Roadmap sugerido

Fase	Entrega	Período estimado

Fase 1 (MVP)	Coleta + Análise + Avaliação	2–4 semanas
Fase 2	Aprendizado + Contra-propostas	4–6 semanas
Fase 3	Branding + Insights Profissionais	6–8 semanas
Fase 4	Autonomia e Preditividade	8–12 semanas



---

#### 🔐 14. Considerações Finais

O sistema deve ser modular e evolutivo:
cada agente atua de forma independente, mas compartilha memória e contexto global.
A arquitetura deve priorizar interpretação, aprendizado e valor humano, refletindo a visão central do produto:

> “Um agente que entende não só o mercado, mas o profissional por trás — e o ajuda a evoluir técnica, financeira e emocionalmente.”




---


# 📊 Módulo Charlee Projects - Gestão Inteligente de Projetos e Freelancing

## 18. Sistema de Inteligência de Projetos e Carreira

### 18.1 Visão Geral

**Charlee Projects** é o módulo responsável por transformar Samara em uma **CEO de sua própria carreira freelance**, automatizando análise de oportunidades, precificação estratégica, negociação e aprendizado contínuo sobre posicionamento profissional.

**Problema que resolve:**
- Análise manual demorada de dezenas de propostas/semana
- Dificuldade em precificar trabalho (síndrome do impostor)
- Negociações difíceis (medo de perder projeto vs. ser mal paga)
- Falta de visão estratégica sobre evolução de carreira
- Não saber quais habilidades desenvolver para maximizar valor

**Solução:**
Um **time de agentes especializados** que monitora, analisa, precifica, negocia e aprende continuamente, funcionando como um **agente de carreira + consultor financeiro + coach técnico**.

---

### 18.2 Arquitetura Multi-Agente

```
┌─────────────────────────────────────────────────────────────┐
│              AGENTE GESTOR CENTRAL (Orchestrator)           │
│         Coordena time de agentes especializados             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────────┐
        │             │                 │
        ▼             ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   NÚCLEO DE  │ │   NÚCLEO DE  │ │   NÚCLEO DE  │
│   EXECUÇÃO   │ │ APRENDIZADO  │ │  ESTRATÉGIA  │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │                 │
        │             │                 │
┌───────┴────┬────────┴─────┬──────────┴──────┐
│            │              │                 │
▼            ▼              ▼                 ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ 🧩      │ │ 🧠      │ │ 🧠      │ │ 🪞      │
│ Coletor │ │Analisador│ │Auto     │ │Branding │
│         │ │         │ │Learning │ │ Advisor │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
     │           │           │           │
     ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ ⚖️      │ │ 💬      │ │ 📊      │ │         │
│Avaliador│ │Negociador│ │Analítico│ │         │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

---

### 18.3 Modelo de Dados

```sql
-- PLATAFORMAS FREELANCER
CREATE TABLE plataformas_freelance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT NOT NULL,  -- 'Upwork', 'Freelancer.com', 'Fiverr', etc
    tipo TEXT,  -- 'marketplace', 'network', 'direct'
    config JSONB,  -- API keys, webhooks, etc
    ativo BOOLEAN DEFAULT TRUE,
    ultima_coleta TIMESTAMP,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- PROJETOS COLETADOS
CREATE TABLE projetos_freelance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plataforma_id UUID REFERENCES plataformas_freelance(id),
    
    -- Dados originais
    external_id TEXT UNIQUE,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    cliente_nome TEXT,
    cliente_rating FLOAT,
    cliente_pais TEXT,
    
    -- Requisitos técnicos
    stack_tecnologias TEXT[],
    nivel_requerido TEXT,  -- 'junior', 'pleno', 'senior', 'especialista'
    categoria TEXT,  -- 'full-stack', 'backend', 'frontend', 'ai/ml', 'devops'
    
    -- Condições comerciais
    orcamento_cliente NUMERIC(10,2),
    prazo_cliente INTEGER,  -- dias
    tipo_contrato TEXT,  -- 'fixed', 'hourly', 'milestone'
    
    -- Análise do sistema
    complexidade_estimada INTEGER CHECK(complexidade_estimada BETWEEN 1 AND 10),
    horas_estimadas FLOAT,
    valor_sugerido NUMERIC(10,2),
    prazo_sugerido INTEGER,
    
    -- Classificação
    score_viabilidade FLOAT,  -- 0-1 (quão viável financeiramente)
    score_alinhamento FLOAT,  -- 0-1 (alinhamento com skills de Samara)
    score_estrategico FLOAT,  -- 0-1 (valor para carreira)
    score_final FLOAT,  -- Média ponderada
    
    recomendacao TEXT,  -- 'aceitar', 'negociar', 'recusar'
    justificativa TEXT,
    
    -- Análise semântica
    intencao_cliente TEXT,  -- 'projeto_serio', 'teste', 'exploração'
    red_flags TEXT[],  -- Alertas identificados
    oportunidades TEXT[],  -- Pontos positivos
    contexto_extraido JSONB,
    embedding VECTOR(1536),
    
    -- Estado
    status TEXT DEFAULT 'novo',  -- 'novo', 'analisado', 'negociando', 'aceito', 'recusado', 'concluido'
    decisao_final TEXT,  -- 'aceito', 'recusado', 'não_respondido'
    motivo_decisao TEXT,
    
    -- Timestamps
    coletado_em TIMESTAMP DEFAULT NOW(),
    analisado_em TIMESTAMP,
    respondido_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- EXECUÇÃO DE PROJETOS
CREATE TABLE projetos_execucao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID REFERENCES projetos_freelance(id),
    
    -- Planejamento
    data_inicio DATE NOT NULL,
    data_fim_prevista DATE,
    data_fim_real DATE,
    
    -- Tempo investido
    horas_planejadas FLOAT,
    horas_reais FLOAT,
    
    -- Financeiro
    valor_negociado NUMERIC(10,2),
    valor_recebido NUMERIC(10,2),
    moeda TEXT DEFAULT 'USD',
    
    -- Avaliação
    satisfacao_cliente INTEGER CHECK(satisfacao_cliente BETWEEN 1 AND 5),
    rating_recebido FLOAT,
    feedback_cliente TEXT,
    
    -- Reflexão pessoal
    dificuldade_real INTEGER CHECK(dificuldade_real BETWEEN 1 AND 10),
    aprendizados TEXT[],
    desafios_enfrentados TEXT[],
    observacoes TEXT,
    
    -- Impacto na carreira
    novas_skills_adquiridas TEXT[],
    portfolio_asset BOOLEAN DEFAULT FALSE,
    testimonial_obtido BOOLEAN DEFAULT FALSE,
    
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- PARÂMETROS DE PRECIFICAÇÃO
CREATE TABLE parametros_precificacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    versao INTEGER NOT NULL,
    
    -- Valores base
    valor_hora_base NUMERIC(10,2) NOT NULL,  -- Taxa horária base
    margem_minima FLOAT DEFAULT 0.2,  -- 20% mínimo de margem
    
    -- Fatores multiplicadores
    fator_complexidade JSONB,
    -- {1: 0.8, 2-3: 1.0, 4-6: 1.3, 7-8: 1.6, 9-10: 2.0}
    
    fator_especializacao JSONB,
    -- {'ai/ml': 1.5, 'blockchain': 1.4, 'full-stack': 1.2, 'frontend': 1.0}
    
    fator_prazo JSONB,
    -- {'urgente_<7dias': 1.5, 'curto_7-14dias': 1.2, 'normal_15-30dias': 1.0, 'longo_>30dias': 0.9}
    
    fator_cliente JSONB,
    -- {'novo_sem_rating': 1.1, 'bom_rating': 1.0, 'excelente_rating': 0.95}
    
    -- Limites
    valor_minimo_projeto NUMERIC(10,2) DEFAULT 500,
    prazo_minimo_dias INTEGER DEFAULT 7,
    
    -- Aprendizado
    ajustado_automaticamente BOOLEAN DEFAULT FALSE,
    baseado_em_execucoes INTEGER DEFAULT 0,
    
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- NEGOCIAÇÕES
CREATE TABLE negociacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID REFERENCES projetos_freelance(id),
    
    -- Proposta inicial
    valor_original NUMERIC(10,2),
    prazo_original INTEGER,
    
    -- Contra-proposta
    valor_contra_proposta NUMERIC(10,2),
    prazo_contra_proposta INTEGER,
    justificativa TEXT,
    mensagem_gerada TEXT,
    
    -- Resposta do cliente
    resposta_cliente TEXT,
    valor_final_acordado NUMERIC(10,2),
    prazo_final_acordado INTEGER,
    
    resultado TEXT,  -- 'aceito', 'recusado', 'acordo', 'sem_resposta'
    
    criado_em TIMESTAMP DEFAULT NOW(),
    finalizado_em TIMESTAMP
);

-- INSIGHTS DE CARREIRA
CREATE TABLE insights_carreira (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    periodo_inicio DATE,
    periodo_fim DATE,
    tipo TEXT,  -- 'mensal', 'trimestral', 'anual'
    
    -- Métricas financeiras
    faturamento_total NUMERIC(10,2),
    ticket_medio NUMERIC(10,2),
    valor_hora_real NUMERIC(10,2),  -- faturamento / horas trabalhadas
    
    -- Métricas de produtividade
    projetos_completados INTEGER,
    taxa_sucesso FLOAT,  -- % projetos concluídos com sucesso
    horas_trabalhadas FLOAT,
    
    -- Evolução técnica
    complexidade_media FLOAT,
    novas_tecnologias TEXT[],
    areas_dominantes TEXT[],
    
    -- Posicionamento
    categorias_mais_lucrativas JSONB,
    clientes_preferenciais TEXT[],
    tendencias_identificadas TEXT[],
    
    -- Recomendações estratégicas
    recomendacoes TEXT[],
    proximo_passo_sugerido TEXT,
    
    gerado_em TIMESTAMP DEFAULT NOW()
);

-- PORTFOLIO AUTOMÁTICO
CREATE TABLE portfolio_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_execucao_id UUID REFERENCES projetos_execucao(id),
    
    titulo TEXT NOT NULL,
    descricao_otimizada TEXT,  -- Gerada por IA
    tecnologias_usadas TEXT[],
    desafios_superados TEXT[],
    resultados_metricas JSONB,
    
    imagens_urls TEXT[],
    demo_url TEXT,
    case_study_url TEXT,
    
    destaque BOOLEAN DEFAULT FALSE,
    categoria TEXT,
    
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- APRENDIZADO CONTÍNUO
CREATE TABLE aprendizado_modelo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_aprendizado TEXT,  -- 'precificacao', 'classificacao', 'negociacao'
    
    input_features JSONB,
    output_esperado TEXT,
    output_real TEXT,
    
    acurácia FLOAT,
    feedback_usuario TEXT,
    
    ajuste_realizado BOOLEAN DEFAULT FALSE,
    impacto_ajuste TEXT,
    
    criado_em TIMESTAMP DEFAULT NOW()
);

-- REFLEXÕES PESSOAIS
CREATE TABLE reflexoes_pessoais (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data DATE NOT NULL,
    categoria TEXT,  -- 'aprendizado', 'desafio', 'conquista', 'insight'
    
    conteudo TEXT NOT NULL,
    sentimento TEXT,  -- 'positivo', 'neutro', 'desafiador'
    tags TEXT[],
    
    relacionado_a UUID,  -- ID de projeto, se aplicável
    acao_tomada TEXT,
    
    criado_em TIMESTAMP DEFAULT NOW()
);

-- ÍNDICES
CREATE INDEX idx_projetos_status ON projetos_freelance(status, score_final DESC);
CREATE INDEX idx_projetos_recomendacao ON projetos_freelance(recomendacao);
CREATE INDEX idx_projetos_coletado ON projetos_freelance(coletado_em DESC);
CREATE INDEX idx_projetos_embedding ON projetos_freelance USING ivfflat(embedding vector_cosine_ops);
CREATE INDEX idx_execucao_data ON projetos_execucao(data_inicio, data_fim_real);
```

---

### 18.4 Agentes Especializados

#### 18.4.1 🧩 CollectorAgent (Coletor)

**Responsabilidade:** Monitorar plataformas e coletar novas oportunidades

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import requests
from upwork import Client as UpworkClient

class ProjectCollectorAgent(Agent):
    """Agente que coleta projetos de múltiplas plataformas"""
    
    def __init__(self, db_connection, platforms_config):
        self.db = db_connection
        self.platforms = platforms_config
        
        super().__init__(
            name="Project Collector",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "Você coleta projetos de plataformas freelance",
                "Normaliza dados para estrutura comum",
                "Detecta projetos duplicados",
                "Extrai informações técnicas básicas"
            ]
        )
    
    def collect_from_upwork(self, config):
        """Coleta projetos do Upwork"""
        client = UpworkClient(
            public_key=config['public_key'],
            secret_key=config['secret_key'],
            oauth_token=config['oauth_token'],
            oauth_token_secret=config['oauth_token_secret']
        )
        
        # Busca projetos recentes que matcham skills de Samara
        query = {
            'q': 'python OR react OR ai OR automation',
            'sort': 'recency',
            'paging': '0;50',
            'job_status': 'open'
        }
        
        response = client.provider.get_jobs(params=query)
        projects = []
        
        for job in response['jobs']:
            project = {
                'plataforma': 'upwork',
                'external_id': job['id'],
                'titulo': job['title'],
                'descricao': job['description'],
                'cliente_nome': job['client']['name'],
                'cliente_rating': job['client']['rating'],
                'cliente_pais': job['client']['country'],
                'orcamento_cliente': job.get('budget'),
                'prazo_cliente': self.extract_deadline(job['description']),
                'tipo_contrato': job['job_type'],  # 'Fixed' ou 'Hourly'
                'stack_tecnologias': job.get('skills', []),
                'coletado_em': datetime.now()
            }
            projects.append(project)
        
        return projects
    
    def collect_from_freelancer(self, config):
        """Coleta projetos do Freelancer.com"""
        headers = {
            'freelancer-oauth-v1': config['access_token']
        }
        
        params = {
            'query': 'python react ai',
            'limit': 50,
            'sort_field': 'time_submitted'
        }
        
        response = requests.get(
            'https://www.freelancer.com/api/projects/0.1/projects/active',
            headers=headers,
            params=params
        )
        
        projects = []
        for job in response.json()['result']['projects']:
            project = {
                'plataforma': 'freelancer',
                'external_id': str(job['id']),
                'titulo': job['title'],
                'descricao': job['description'],
                'cliente_nome': job['owner_id'],
                'orcamento_cliente': job['budget']['minimum'],
                'tipo_contrato': job['type'],
                'stack_tecnologias': [skill['name'] for skill in job.get('jobs', [])],
                'coletado_em': datetime.now()
            }
            projects.append(project)
        
        return projects
    
    def collect_all(self):
        """Coleta de todas as plataformas ativas"""
        all_projects = []
        
        for platform in self.platforms:
            if not platform['ativo']:
                continue
            
            try:
                if platform['nome'] == 'Upwork':
                    projects = self.collect_from_upwork(platform['config'])
                elif platform['nome'] == 'Freelancer':
                    projects = self.collect_from_freelancer(platform['config'])
                # ... outras plataformas
                
                all_projects.extend(projects)
                
                # Atualiza timestamp
                self.db.execute("""
                    UPDATE plataformas_freelance
                    SET ultima_coleta = NOW()
                    WHERE id = %s
                """, (platform['id'],))
                
            except Exception as e:
                logger.error(f"Erro coletando de {platform['nome']}: {e}")
        
        return all_projects
    
    def smart_add_opportunity(self, raw_text: str, source_url: Optional[str] = None) -> dict:
        """
        Adiciona oportunidade a partir de texto colado pelo usuário.

        LLM extrai automaticamente: título, descrição, skills, budget, deadline.

        Args:
            raw_text: Texto colado pelo usuário (descrição do projeto)
            source_url: URL de origem opcional

        Returns:
            Dados estruturados extraídos + ID da oportunidade criada
        """
        # Prompt para extração estruturada
        extraction_prompt = f"""
Extraia informações estruturadas deste texto de oportunidade de projeto freelance.

TEXTO:
{raw_text}

URL DE ORIGEM (se disponível): {source_url or 'Não informada'}

Retorne JSON com os seguintes campos (use null se não encontrar):
{{
    "title": "Título do projeto (inferir se não explícito)",
    "description": "Descrição limpa e organizada",
    "client_name": "Nome do cliente/empresa",
    "budget_min": 0,
    "budget_max": 0,
    "currency": "USD",
    "deadline_days": 0,
    "required_skills": ["skill1", "skill2"],
    "contract_type": "fixed | hourly | milestone",
    "complexity_estimate": 1-10,
    "category": "full-stack | backend | frontend | ai-ml | devops | mobile | other",
    "red_flags": ["alerta1", "alerta2"],
    "opportunities": ["oportunidade1", "oportunidade2"]
}}

Seja preciso na extração. Se o budget estiver em range (ex: $2000-3000),
extraia min e max separadamente.
"""

        # Chama LLM para extração
        response = self.run(extraction_prompt)
        extracted = json.loads(response.content)

        # Cria oportunidade no banco
        opportunity = FreelanceOpportunity(
            user_id=self.user_id,
            platform_id=None,  # Smart paste não tem plataforma específica
            title=extracted['title'],
            description=extracted['description'],
            client_name=extracted.get('client_name'),
            required_skills=extracted.get('required_skills', []),
            client_budget=extracted.get('budget_max'),
            client_budget_min=extracted.get('budget_min'),
            currency=extracted.get('currency', 'USD'),
            client_deadline_days=extracted.get('deadline_days'),
            contract_type=extracted.get('contract_type'),
            source_url=source_url,
            raw_input_text=raw_text,
            status="new",
            collected_at=datetime.now(timezone.utc),
            # Pré-análise do LLM
            complexity_estimated=extracted.get('complexity_estimate'),
            category=extracted.get('category'),
            red_flags=extracted.get('red_flags', []),
            opportunities=extracted.get('opportunities', []),
        )

        self.db.add(opportunity)
        self.db.commit()

        return {
            "id": opportunity.id,
            "extracted": extracted,
            "message": f"✅ Oportunidade '{extracted['title']}' criada com sucesso!"
        }

    def add_from_bookmarklet(self, bookmarklet_data: dict) -> dict:
        """
        Adiciona oportunidade a partir de dados do bookmarklet.

        Args:
            bookmarklet_data: JSON enviado pelo bookmarklet do browser
                {
                    "source": "upwork" | "freelancer" | "linkedin",
                    "url": "https://...",
                    "title": "...",
                    "description": "...",
                    "budget": "$1000-2000",
                    "skills": "Python, React, ..."
                }

        Returns:
            Oportunidade criada
        """
        # Parse budget string se necessário
        budget_min, budget_max = self._parse_budget(bookmarklet_data.get('budget'))

        # Parse skills string se necessário
        skills = bookmarklet_data.get('skills', '')
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]

        opportunity = FreelanceOpportunity(
            user_id=self.user_id,
            platform_id=self._get_platform_id(bookmarklet_data['source']),
            title=bookmarklet_data['title'],
            description=bookmarklet_data['description'],
            required_skills=skills,
            client_budget=budget_max,
            client_budget_min=budget_min,
            source_url=bookmarklet_data.get('url'),
            status="new",
            collected_at=datetime.now(timezone.utc),
        )

        self.db.add(opportunity)
        self.db.commit()

        return {
            "id": opportunity.id,
            "message": f"✅ Oportunidade do {bookmarklet_data['source'].title()} importada!"
        }

    def _parse_budget(self, budget_str: str) -> tuple:
        """Parse budget string like '$1000-2000' into (min, max)"""
        if not budget_str:
            return None, None

        import re
        numbers = re.findall(r'[\d,]+', budget_str.replace(',', ''))
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
        elif len(numbers) == 1:
            return float(numbers[0]), float(numbers[0])
        return None, None

    def _get_platform_id(self, source: str) -> Optional[int]:
        """Get platform ID by source name"""
        platform = self.db.query(FreelancePlatform).filter(
            FreelancePlatform.user_id == self.user_id,
            FreelancePlatform.name.ilike(f"%{source}%")
        ).first()
        return platform.id if platform else None

    def save_projects(self, projects):
        """Salva projetos no banco (evita duplicatas)"""
        saved_count = 0

        for proj in projects:
            # Verifica duplicata
            existing = self.db.execute("""
                SELECT id FROM projetos_freelance
                WHERE external_id = %s AND plataforma_id = (
                    SELECT id FROM plataformas_freelance WHERE nome = %s
                )
            """, (proj['external_id'], proj['plataforma'])).fetchone()
            
            if not existing:
                self.db.execute("""
                    INSERT INTO projetos_freelance
                    (plataforma_id, external_id, titulo, descricao, 
                     cliente_nome, orcamento_cliente, stack_tecnologias, ...)
                    VALUES (
                        (SELECT id FROM plataformas_freelance WHERE nome = %s),
                        %s, %s, %s, %s, %s, %s, ...
                    )
                """, (...))
                saved_count += 1
        
        logger.info(f"✅ {saved_count} novos projetos coletados")
        return saved_count
```

#### 18.4.2 🧠 AnalyzerAgent (Analisador Semântico)

**Responsabilidade:** Interpretar descrições e extrair informações técnicas

```python
class ProjectAnalyzerAgent(Agent):
    """Agente que analisa semanticamente projetos"""
    
    def __init__(self, db_connection, vector_db):
        self.db = db_connection
        self.vector_db = vector_db
        
        super().__init__(
            name="Project Analyzer",
            model=OpenAIChat(id="gpt-4o"),
            storage=vector_db,
            instructions=[
                "Você é especialista em análise de requisitos técnicos",
                "Interpreta descrições vagas e infere escopo real",
                "Identifica complexidade e nível técnico requerido",
                "Detecta red flags (sinais de alerta)",
                "Extrai oportunidades e pontos positivos"
            ]
        )
    
    def analyze_project(self, project_id):
        """Analisa um projeto detalhadamente"""
        
        # Busca projeto
        project = self.db.execute("""
            SELECT * FROM projetos_freelance WHERE id = %s
        """, (project_id,)).fetchone()
        
        # Busca projetos similares históricos
        similar_projects = self.vector_db.search(
            query=project['descricao'],
            filter={'status': 'concluido'},
            limit=5
        )
        
        # Monta prompt de análise
        prompt = f"""
Analise este projeto freelance em profundidade:

INFORMAÇÕES BÁSICAS:
Título: {project['titulo']}
Cliente: {project['cliente_nome']} (Rating: {project['cliente_rating']}, País: {project['cliente_pais']})
Orçamento: ${project['orcamento_cliente']}
Prazo: {project['prazo_cliente']} dias
Tipo: {project['tipo_contrato']}

DESCRIÇÃO COMPLETA:
{project['descricao']}

SKILLS SOLICITADAS:
{', '.join(project['stack_tecnologias'])}

PROJETOS SIMILARES PASSADOS:
{self.format_similar_projects(similar_projects)}

ANÁLISE REQUERIDA:

1. NÍVEL TÉCNICO (júnior/pleno/sênior/especialista)
2. COMPLEXIDADE (1-10)
3. ESCOPO REAL (o que realmente está sendo pedido)
4. STACK TECNOLÓGICA COMPLETA (inferida)
5. CATEGORIA (full-stack/backend/frontend/ai-ml/devops)
6. HORAS ESTIMADAS (seja realista)
7. RED FLAGS (se houver):
   - Orçamento irrealista
   - Escopo vago ou muito amplo
   - Cliente sem histórico
   - Prazo incompatível
   - Sinais de projeto "teste" ou não sério
8. OPORTUNIDADES:
   - Valor para portfólio
   - Novas skills a desenvolver
   - Networking valioso
   - Potencial de projeto recorrente
9. INTENÇÃO DO CLIENTE (projeto_serio/teste/exploração)

Retorne JSON estruturado com toda análise.
"""
        
        response = self.print_response(prompt, stream=False)
        analysis = json.loads(response)
        
        # Gera embedding
        embedding = self.generate_embedding(project['descricao'])
        
        # Atualiza banco
        self.db.execute("""
            UPDATE projetos_freelance
            SET nivel_requerido = %s,
                complexidade_estimada = %s,
                horas_estimadas = %s,
                categoria = %s,
                stack_tecnologias = %s,
                intencao_cliente = %s,
                red_flags = %s,
                oportunidades = %s,
                contexto_extraido = %s,
                embedding = %s,
                analisado_em = NOW(),
                status = 'analisado'
            WHERE id = %s
        """, (
            analysis['nivel_tecnico'],
            analysis['complexidade'],
            analysis['horas_estimadas'],
            analysis['categoria'],
            analysis['stack_completa'],
            analysis['intencao_cliente'],
            analysis['red_flags'],
            analysis['oportunidades'],
            json.dumps(analysis),
            embedding,
            project_id
        ))
        
        return analysis
```

#### 18.4.3 ⚖️ EvaluatorAgent (Avaliador)

**Responsabilidade:** Precificar e avaliar viabilidade

```python
class ProjectEvaluatorAgent(Agent):
    """Agente que precifica e avalia viabilidade de projetos"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.params = self.load_pricing_params()
        
        super().__init__(
            name="Project Evaluator",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "Você precifica projetos de forma justa e estratégica",
                "Considera complexidade, especialização e mercado",
                "Protege Samara de propostas ruins",
                "Equilibra valor justo com competitividade"
            ]
        )
    
    def load_pricing_params(self):
        """Carrega parâmetros de precificação atuais"""
        return self.db.execute("""
            SELECT * FROM parametros_precificacao
            WHERE ativo = TRUE
            ORDER BY versao DESC
            LIMIT 1
        """).fetchone()
    
    def calculate_price(self, project_id):
        """Calcula preço sugerido para o projeto"""
        
        # Busca projeto analisado
        project = self.db.execute("""
            SELECT * FROM projetos_freelance WHERE id = %s
        """, (project_id,)).fetchone()
        
        # Calcula valor base
        valor_base = project['horas_estimadas'] * self.params['valor_hora_base']
        
        # Aplica fatores multiplicadores
        
        # 1. Fator complexidade
        complexidade = project['complexidade_estimada']
        fator_comp = self.params['fator_complexidade'].get(
            str(complexidade), 1.0
        )
        
        # 2. Fator especialização
        categoria = project['categoria']
        fator_espec = self.params['fator_especializacao'].get(
            categoria, 1.0
        )
        
        # 3. Fator prazo
        prazo = project['prazo_cliente']
        if prazo < 7:
            fator_prazo = self.params['fator_prazo']['urgente_<7dias']
        elif prazo <= 14:
            fator_prazo = self.params['fator_prazo']['curto_7-14dias']
        elif prazo <= 30:
            fator_prazo = self.params['fator_prazo']['normal_15-30dias']
        else:
            fator_prazo = self.params['fator_prazo']['longo_>30dias']
        
        # 4. Fator cliente
        rating = project['cliente_rating']
        if rating is None:
            fator_cliente = self.params['fator_cliente']['novo_sem_rating']
        elif rating >= 4.5:
            fator_cliente = self.params['fator_cliente']['excelente_rating']
        else:
            fator_cliente = self.params['fator_cliente']['bom_rating']
        
        # Calcula valor final
        valor_sugerido = valor_base * fator_comp * fator_espec * fator_prazo * fator_cliente
        
        # Aplica margem mínima
        valor_minimo = valor_base * (1 + self.params['margem_minima'])
        valor_sugerido = max(valor_sugerido, valor_minimo)
        
        # Aplica limite mínimo de projeto
        valor_sugerido = max(valor_sugerido, self.params['valor_minimo_projeto'])
        
        # Calcula prazo sugerido (+ buffer de 20%)
        prazo_sugerido = int(project['horas_estimadas'] / 6)  # 6h/dia
        prazo_sugerido = max(prazo_sugerido, self.params['prazo_minimo_dias'])
        prazo_sugerido = int(prazo_sugerido * 1.2)  # Buffer
        
        return {
            'valor_base': valor_base,
            'valor_sugerido': round(valor_sugerido, 2),
            'prazo_sugerido': prazo_sugerido,
            'fatores_aplicados': {
                'complexidade': fator_comp,
                'especializacao': fator_espec,
                'prazo': fator_prazo,
                'cliente': fator_cliente
            }
        }
    
    def evaluate_viability(self, project_id):
        """Avalia viabilidade financeira e estratégica"""
        
        project = self.db.execute("""
            SELECT * FROM projetos_freelance WHERE id = %s
        """, (project_id,)).fetchone()
        
        pricing = self.calculate_price(project_id)
        
        # Score de viabilidade financeira
        if project['orcamento_cliente'] is None:
            score_viabilidade = 0.5  # Indefinido
        else:
            ratio = project['orcamento_cliente'] / pricing['valor_sugerido']
            if ratio >= 1.0:
                score_viabilidade = min(ratio / 1.2, 1.0)  # Cap em 1.0
            else:
                score_viabilidade = ratio * 0.7  # Penaliza subpagamento
        
        # Score de alinhamento técnico
        samara_skills = self.get_samara_skills()
        project_skills = set(project['stack_tecnologias'])
        match_ratio = len(project_skills.intersection(samara_skills)) / len(project_skills)
        score_alinhamento = match_ratio
        
        # Score estratégico
        score_estrategico = self.calculate_strategic_score(project)
        
        # Score final (média ponderada)
        score_final = (
            score_viabilidade * 0.4 +
            score_alinhamento * 0.3 +
            score_estrategico * 0.3
        )
        
        # Recomendação
        if score_final >= 0.75 and not project['red_flags']:
            recomendacao = 'aceitar'
        elif score_final >= 0.5:
            recomendacao = 'negociar'
        else:
            recomendacao = 'recusar'
        
        # Justificativa
        justificativa = self.generate_justification(
            project, pricing, score_final, recomendacao
        )
        
        # Atualiza banco
        self.db.execute("""
            UPDATE projetos_freelance
            SET valor_sugerido = %s,
                prazo_sugerido = %s,
                score_viabilidade = %s,
                score_alinhamento = %s,
                score_estrategico = %s,
                score_final = %s,
                recomendacao = %s,
                justificativa = %s
            WHERE id = %s
        """, (
            pricing['valor_sugerido'],
            pricing['prazo_sugerido'],
            score_viabilidade,
            score_alinhamento,
            score_estrategico,
            score_final,
            recomendacao,
            justificativa,
            project_id
        ))
        
        return {
            'recomendacao': recomendacao,
            'score_final': score_final,
            'pricing': pricing,
            'justificativa': justificativa
        }
    
    def calculate_strategic_score(self, project):
        """Calcula valor estratégico do projeto"""
        score = 0.5  # Base
        
        # Boost por oportunidades
        if 'portfolio' in ' '.join(project.get('oportunidades', [])).lower():
            score += 0.15
        if 'nova skill' in ' '.join(project.get('oportunidades', [])).lower():
            score += 0.10
        if 'networking' in ' '.join(project.get('oportunidades', [])).lower():
            score += 0.10
        if 'recorrente' in ' '.join(project.get('oportunidades', [])).lower():
            score += 0.15
        
        # Penalidade por red flags
        score -= len(project.get('red_flags', [])) * 0.10
        
        return min(max(score, 0.0), 1.0)  # Clamp entre 0-1
```

---

## 18.5 Requisitos Adicionais Críticos para MVP

> **Atualizado em:** 2026-01-28
>
> Requisitos essenciais identificados para garantir operação segura e eficiente em produção.

### 18.5.1 Priorização de Requisitos

| Prioridade | Quantidade | Implementação |
|-----------|------------|---------------|
| 🔴 **MVP Obrigatório** | 5 requisitos | Deve ser implementado antes de produção |
| 🟡 **V2 do Módulo** | 7 requisitos | Qualidade e robustez |
| 🟢 **V3+ Futuro** | 3 requisitos | Otimizações avançadas |

---

### 🔴 18.5.2 Requisitos Críticos do MVP

#### **RN09: Prevenção de Análise Duplicada**

**Contexto:** Evitar desperdício de recursos processando o mesmo projeto múltiplas vezes.

**Regras:**
- Projetos duplicados em diferentes plataformas devem ser detectados via similarity matching
- Lock distribuído deve prevenir race conditions entre workers
- Timeout de processamento: 5 minutos

**Implementação:**
```python
# backend/services/freelancer/project_processor.py

class ProjectDuplicationPrevention:
    """Previne análise duplicada de projetos"""

    def detect_duplicate(self, new_project):
        """Detecta projetos duplicados via similarity matching"""

        similar_projects = self.db.query("""
            SELECT id, title, client_email, budget
            FROM freelance_opportunities
            WHERE created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at DESC
            LIMIT 50
        """)

        for candidate in similar_projects:
            is_duplicate = (
                self._is_same_client(new_project, candidate) and
                self._text_similarity(new_project.title, candidate.title) > 0.85 and
                abs(new_project.budget - candidate.budget) / new_project.budget < 0.15
            )

            if is_duplicate:
                return {'is_duplicate': True, 'original_id': candidate.id}

        return {'is_duplicate': False}

    def acquire_processing_lock(self, project_id, timeout=300):
        """Adquire lock distribuído para processar projeto"""
        lock_key = f"processing:project:{project_id}"
        return self.redis.set(lock_key, 'processing', nx=True, ex=timeout)
```

**Esforço:** 4-6h | **Prioridade:** 🔴 Crítica

---

#### **RN10: Rate Limiting para APIs Externas**

**Contexto:** Upwork limita a 100 requests/hora. Exceder resulta em bloqueio de conta.

**Regras:**
- Máximo 100 requests por hora para Upwork API
- Implementar leaky bucket algorithm
- Retry automático com exponential backoff

**Implementação:**
```python
# backend/services/freelancer/upwork_client.py

class UpworkRateLimiter:
    """Rate limiter para Upwork API (100 req/hora)"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_requests = 100
        self.window_seconds = 3600

    def can_make_request(self):
        """Verifica se pode fazer request sem violar rate limit"""
        key = "upwork:ratelimit"
        now = time.time()

        # Remove requests antigos
        self.redis.zremrangebyscore(key, 0, now - self.window_seconds)

        # Conta requests atuais
        current_requests = self.redis.zcard(key)

        if current_requests >= self.max_requests:
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                wait_time = (oldest[0][1] + self.window_seconds) - now
                raise RateLimitExceeded(f"Aguarde {wait_time:.0f}s")

        # Registra novo request
        self.redis.zadd(key, {str(uuid.uuid4()): now})
        self.redis.expire(key, self.window_seconds)
        return True
```

**Esforço:** 2-3h | **Prioridade:** 🔴 Crítica

---

#### **RN11: Cálculo Financeiro Completo**

**Contexto:** Precificação deve considerar impostos, comissões e custos de conversão para evitar prejuízo.

**Regras:**
- Calcular comissão da plataforma (Upwork: 20% até $500, 10% depois)
- Aplicar cotação USD→BRL do Banco Central
- Deduzir spread cambial (3%), IOF (1.1%), taxa bancária (1%)
- Calcular imposto conforme regime tributário (Simples: 6%)

**Implementação:**
```python
# backend/services/freelancer/financial_calculator.py

class FreelancerFinancialCalculator:
    """Calcula valor líquido considerando todos os custos"""

    def calculate_net_value(self, gross_usd, platform='upwork', regime='Simples_Nacional'):
        """Calcula quanto realmente vai cair na conta"""

        # 1. Comissão da plataforma
        if platform == 'upwork':
            platform_fee = (500 * 0.20 + (gross_usd - 500) * 0.10) if gross_usd > 500 else gross_usd * 0.20
        else:
            platform_fee = 0

        after_platform = gross_usd - platform_fee

        # 2. Conversão USD → BRL (API Banco Central)
        exchange_rate = self._get_exchange_rate('USD', 'BRL')
        gross_brl = after_platform * exchange_rate

        # 3. Custos de conversão
        spread_fee = gross_brl * 0.03  # 3% spread
        iof = gross_brl * 0.011  # 1.1% IOF
        bank_fee = gross_brl * 0.01  # 1% taxa bancária

        after_conversion = gross_brl - spread_fee - iof - bank_fee

        # 4. Impostos Brasil
        if regime == 'Simples_Nacional':
            tax = after_conversion * 0.06  # 6% Anexo III
        elif regime == 'MEI':
            tax = 66.60  # Fixo mensal
        else:
            tax = 0

        net_brl = after_conversion - tax

        return {
            'gross_usd': gross_usd,
            'net_brl': net_brl,
            'platform_fee_usd': platform_fee,
            'tax_brl': tax,
            'exchange_rate': exchange_rate,
            'effective_rate': (gross_usd * exchange_rate - net_brl) / (gross_usd * exchange_rate)
        }

    def _get_exchange_rate(self, from_currency, to_currency):
        """Busca cotação do Banco Central (cache 1h)"""
        cache_key = f"forex:{from_currency}:{to_currency}"
        cached = redis_client.get(cache_key)

        if cached:
            return float(cached)

        response = requests.get(
            f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
            f"CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?"
            f"@moeda='{from_currency}'&@dataCotacao='{datetime.now().strftime('%m-%d-%Y')}'&$format=json"
        )

        rate = response.json()['value'][0]['cotacaoVenda']
        redis_client.setex(cache_key, 3600, str(rate))
        return rate
```

**Esforço:** 3-4h | **Prioridade:** 🔴 Crítica

---

#### **RN12: Avaliação de Risco de Clientes**

**Contexto:** Identificar clientes problemáticos antes de aceitar projeto.

**Regras:**
- Score de risco: 0-100 (menor = mais risco)
- Red flags detectados reduzem score
- Score < 50: recomendar rejeição ou proteções extras

**Red Flags:**
- Requisitos vagos ("asap", "simple", "quick")
- Orçamento < 70% do valor justo
- Cliente sem histórico de pagamentos
- Rating < 3.0 stars
- Solicita trabalho grátis ("test task", "sample")

**Implementação:**
```python
# backend/services/freelancer/client_risk.py

class ClientRiskAssessment:
    """Avalia risco de clientes"""

    RED_FLAGS = {
        'vague_requirements': {
            'keywords': ['asap', 'simple', 'quick', 'easy', 'urgent'],
            'weight': -15
        },
        'unrealistic_budget': {
            'threshold': 0.7,
            'weight': -25
        },
        'no_payment_history': {
            'weight': -10
        },
        'low_rating': {
            'threshold': 3.0,
            'weight': -30
        }
    }

    def score_project(self, project):
        """Calcula risk score (0-100)"""
        base_score = 70
        flags_detected = []

        # Detecta red flags
        for flag_name, config in self.RED_FLAGS.items():
            if self._detect_flag(project, flag_name, config):
                base_score += config['weight']
                flags_detected.append(flag_name)

        risk_score = max(0, min(100, base_score))

        if risk_score >= 70:
            recommendation = 'safe_to_accept'
        elif risk_score >= 50:
            recommendation = 'accept_with_protection'
        else:
            recommendation = 'reject_high_risk'

        return {
            'risk_score': risk_score,
            'recommendation': recommendation,
            'red_flags': flags_detected
        }
```

**Esforço:** 3-4h | **Prioridade:** 🔴 Crítica

---

#### **RN13: Compliance LGPD Básico**

**Contexto:** Dados de clientes devem ser protegidos conforme LGPD.

**Regras:**
- Criptografar dados pessoais (nome, email de clientes)
- Retenção máxima: 5 anos após conclusão do projeto
- Auto-anonimização após período de retenção
- Exportação de dados disponível (direito à portabilidade)

**Implementação:**
```python
# backend/services/security/pii_encryption.py

from cryptography.fernet import Fernet

class PIIEncryption:
    """Criptografia de dados pessoais (LGPD)"""

    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY').encode()
        self.cipher = Fernet(key)

    def encrypt(self, data):
        if not data:
            return None
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        if not encrypted_data:
            return None
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Modelo com propriedades criptografadas
class FreelanceOpportunity(Base):
    __tablename__ = 'freelance_opportunities'

    _client_name_encrypted = Column('client_name', Text)
    _client_email_encrypted = Column('client_email', Text)

    data_processing_consent = Column(Boolean, default=False)
    data_retention_until = Column(Date)  # Auto-delete após 5 anos

    @hybrid_property
    def client_name(self):
        return pii_crypto.decrypt(self._client_name_encrypted)

    @client_name.setter
    def client_name(self, value):
        self._client_name_encrypted = pii_crypto.encrypt(value)


# Job diário de limpeza
@celery_app.task
def cleanup_expired_data():
    """LGPD: Anonimiza dados expirados"""
    expired = db.query(FreelanceOpportunity).filter(
        FreelanceOpportunity.data_retention_until <= date.today()
    ).all()

    for project in expired:
        project.client_name = None
        project.client_email = None
        project.anonymized = True

    db.commit()
```

**Esforço:** 2-3h | **Prioridade:** 🔴 Crítica

---

### 🟡 18.5.3 Requisitos para V2

> Implementar após validação do MVP

1. **RN14:** Gestão de Capacidade (integração Google Calendar)
2. **RN15:** Contratos Automatizados (geração + assinatura eletrônica)
3. **RN16:** Negociação Multi-Rodadas (tracking de contra-propostas)
4. **RN17:** Analytics Avançada (LTV, forecasting, benchmarks)
5. **RN18:** Time Tracking Integration (Toggl, Clockify)
6. **RN19:** ML Pricing Optimizer (ajuste automático)
7. **RN20:** Client CRM (relacionamentos, follow-ups)

---

### 🟢 18.5.4 Requisitos para V3+

1. **RN21:** Personal Branding Automation
2. **RN22:** Network Management
3. **RN23:** Advanced Integrations (Notion, GitHub, accounting)

---

### 18.5.5 Checklist de Implementação MVP

**Antes de produção:**

- [x] ✅ Modelo de dados (seção 18.3)
- [ ] 🔴 RN09: Prevenção de duplicação
- [ ] 🔴 RN10: Rate limiting Upwork
- [ ] 🔴 RN11: Cálculo financeiro completo
- [ ] 🔴 RN12: Client risk scoring
- [ ] 🔴 RN13: LGPD compliance
- [ ] Testes end-to-end
- [ ] Monitoring (Sentry)

**Tempo estimado:** 14-20 horas

---

Quer que eu continue com os próximos agentes?

1. ✅ **NegotiatorAgent** (gera contra-propostas diplomáticas)
2. ✅ **AnalyticsAgent** (métricas e insights)
3. ✅ **BrandingAdvisorAgent** (análise de posicionamento)
4. ✅ **LearningAgent** (aprendizado contínuo)
5. ✅ **OrchestratorAgent** (coordena todos)