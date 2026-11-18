# 🌸 Estudo: O Ciclo Menstrual — Ciência, Dados Reais e Implicações para o Charlee

> Pesquisa feita em 18/11/2026 a partir de literatura científica e dos dados do app de ciclo (capturas de tela de 18/11/2026).
> **Aviso:** este documento é informativo e de apoio ao produto. Não substitui avaliação médica/ginecológica.

---

## Sumário

1. [Fisiologia: o que acontece em um ciclo](#1-fisiologia-o-que-acontece-em-um-ciclo)
2. [O que é "normal" (critérios FIGO)](#2-o-que-é-normal-critérios-figo)
3. [O que os dados de larga escala mostram](#3-o-que-os-dados-de-larga-escala-mostram)
4. [Mitos vs. evidências: energia, cognição, exercício, sono, humor](#4-mitos-vs-evidências)
5. [Análise dos seus dados (abr–nov/2026)](#5-análise-dos-seus-dados-abrnov2026)
6. [Implicações para o Charlee (Cycle-Aware)](#6-implicações-para-o-charlee-cycle-aware)
7. [Fontes](#7-fontes)

---

## 1. Fisiologia: o que acontece em um ciclo

O ciclo é contado do **1º dia da menstruação (D1)** até o dia anterior à menstruação seguinte. Ele acontece em dois "relógios" sincronizados: o **ovário** (ciclo ovariano) e o **endométrio** (ciclo uterino), comandados pelo eixo **hipotálamo → hipófise → ovário**.

| Fase | Dias típicos (ciclo ~28d) | Ovário | Útero | Hormônios dominantes |
|---|---|---|---|---|
| **Menstrual** | D1–D5 | Início do recrutamento de folículos | Descamação do endométrio | Estrogênio e progesterona **baixos**; FSH começa a subir |
| **Folicular** (inclui a menstrual) | D1 → ovulação | Um folículo dominante amadurece | Fase **proliferativa**: endométrio engrossa | **Estradiol subindo** progressivamente |
| **Ovulação** | ~24–36h após o pico de LH | O folículo libera o óvulo (vive ~12–24h) | — | **Pico de LH** (disparado por estradiol alto); pequena alta de testosterona |
| **Lútea** | Ovulação → próxima menstruação | Corpo lúteo produz hormônios | Fase **secretora**: endométrio se prepara | **Progesterona alta** + estradiol moderado; sem gravidez, ambos caem → menstruação |

Pontos-chave:

- **Quem varia é a fase folicular.** A fase lútea é relativamente estável; ciclos longos ou curtos são quase sempre resultado de uma fase folicular mais longa ou mais curta.
- **A progesterona eleva a temperatura basal** em ~0,3–0,5 °C após a ovulação e aumenta a frequência cardíaca noturna — é isso que relógios/anéis usam para *confirmar* (retroativamente) a ovulação.
- **Janela fértil** ≈ os 5 dias antes da ovulação + o dia da ovulação (sobrevida do espermatozoide ~5 dias).

---

## 2. O que é "normal" (critérios FIGO)

A FIGO (Federação Internacional de Ginecologia e Obstetrícia, revisão de 2018) define:

| Parâmetro | Normal |
|---|---|
| **Frequência** (D1 a D1) | **24 a 38 dias** |
| **Regularidade** (diferença entre o ciclo mais curto e o mais longo em 12 meses) | **≤ 7 dias** (26–41 anos) · ≤ 9 dias (18–25 e 42–45 anos) |
| **Duração do sangramento** | **≤ 8 dias** |
| Volume | O que a própria pessoa não considera excessivo / não atrapalha a vida |

Fora disso (ex.: ciclos < 24 ou > 38 dias, variação > 7–9 dias, sangramento > 8 dias, sangramento entre ciclos) vale procurar avaliação médica.

---

## 3. O que os dados de larga escala mostram

O estudo de **Bull et al. (2019, *npj Digital Medicine*)**, com **612.613 ciclos ovulatórios** de 124.648 usuárias (ovulação estimada por temperatura + LH):

- Ciclo médio: **29,3 dias**. Apenas **13% dos ciclos tinham exatamente 28 dias**. 65% ficaram entre 25 e 30 dias.
- Fase folicular média: **16,9 dias** (IC95% 10–30).
- Fase lútea média: **12,4 dias** (IC95% 7–17) — **mais curta que os "14 dias" que muitos apps assumem**.
- Ciclos ficam ~**0,18 dia mais curtos por ano** entre 25 e 45 anos (por encurtamento da fase folicular).
- IMC > 35 associado a ~14% mais variabilidade.

**Wilcox, Dunson & Baird (2000, *BMJ*)**, com ovulação confirmada por hormônios urinários:

- Só **~30% das mulheres** têm a janela fértil inteiramente entre os dias 10 e 17.
- Em **qualquer dia entre D6 e D21** há pelo menos 10% de chance de se estar na janela fértil.
- Conclusão dos autores: a janela fértil é **imprevisível mesmo em ciclos regulares**.

➡️ **Consequência prática:** previsões de ovulação baseadas só em calendário são estimativas grosseiras. Apps que usam temperatura (relógio/anel) ou testes de LH são bem melhores — e mesmo assim confirmam a ovulação *depois* que ela aconteceu.

---

## 4. Mitos vs. evidências

O Charlee hoje parte da premissa "folicular = 120% de energia, ovulação = 140%, lútea = 80%, menstrual = 60%". A literatura **não sustenta multiplicadores universais** desse tipo:

| Tema | O que a evidência diz | Força |
|---|---|---|
| **Cognição** (memória, atenção, raciocínio) | Meta-análise de **102 artigos / 3.943 participantes** (Jang, Zhang & Elfenbein, *PLOS ONE*, 2025): **sem evidência robusta** de mudança sistemática de desempenho cognitivo entre fases. | Moderada-alta |
| **Desempenho físico** | Meta-análise de 78 estudos (McNulty et al., *Sports Medicine*, 2020): desempenho **talvez trivialmente menor no início da fase folicular** (menstruação); efeito muito pequeno, evidência de baixa qualidade. Recomenda **abordagem individualizada**. | Baixa |
| **Sono e fisiologia** | Estudo com anel Oura (Alzueta et al., 2022): arquitetura e qualidade do sono **não mudaram** entre fases, mas **FC noturna e temperatura sobem na fase lútea média/tardia**; VFC tende a cair. | Moderada |
| **Humor — TPM** | Sintomas pré-menstruais são muito comuns, mas a prevalência varia enormemente conforme a definição. | Variável |
| **Humor — TDPM** (transtorno disfórico pré-menstrual) | Meta-análise de 44 estudos / 50.659 pessoas (Reilly et al., 2024): **3,2%** com diagnóstico confirmado; **7,7%** com diagnóstico provisório. | Alta |
| **Libido** | Tende a subir perto da ovulação (alta de estradiol/testosterona) em muitas mulheres — efeito real, mas com grande variação individual. | Moderada |

**Síntese:** o ciclo influencia **sintomas** (cólica, fadiga, sono, humor, libido, inchaço) de forma muito **individual**. Para algumas mulheres o efeito é grande; para outras, quase nulo. O que funciona é **aprender o padrão de cada pessoa** a partir dos próprios registros — e não aplicar uma tabela genérica.

---

## 5. Análise dos seus dados (abr–nov/2026)

### 5.1 Menstruações registradas

| # | Menstruação | Duração | Ciclo (D1 → próximo D1) |
|---|---|---|---|
| 1 | 09/04 – 13/04 | 5 dias | 28 dias |
| 2 | 07/05 – 11/05 | 5 dias | 28 dias |
| 3 | 04/06 – 08/06 | 5 dias | 27 dias |
| 4 | 01/07 – 05/07 | 5 dias | 29 dias |
| 5 | 30/07 – 03/08 | 5 dias | **24 dias** |
| 6 | 23/08 – 27/08 | 5 dias | 28 dias |
| 7 | 20/09 – 24/09 | 5 dias | 26 dias |
| 8 | 16/10 – 20/10 | 5 dias | 28 dias |
| 9 | 13/11 – 17/11 | 5 dias | *(atual)* |

### 5.2 Estatísticas

| Métrica | Valor | Referência FIGO | Status |
|---|---|---|---|
| Ciclo médio | **27,25 dias** (mediana 28) | 24–38 | ✅ Normal |
| Desvio-padrão | **~1,6 dia** | — | Baixa variação |
| Mais curto / mais longo | 24 / 29 dias | — | — |
| Variação (regularidade) | **5 dias** | ≤ 7 dias | ✅ **Regular** |
| Duração do sangramento | **5 dias** (sempre) | ≤ 8 dias | ✅ Normal e muito consistente |

O ciclo de 24 dias (jul→ago) é o único fora da faixa 26–29 e ainda está dentro do normal. Um ciclo mais curto isolado costuma refletir uma fase folicular mais curta (estresse, viagem, sono, doença podem influenciar). Vale observar se coincidiu com algum evento.

### 5.3 Situação hoje (18/11/2026)

- **D6 do ciclo — fase folicular** (pós-menstrual, estradiol em subida).
- Registros de hoje: *Feliz, Energética, Libido alta, Está tudo bem, Meditação, Exercícios de respiração, Ioga* — compatível com o que muitas mulheres relatam nesta fase.
- ⚠️ **Sono: 3h06min dormindo**, mas o app classificou como "Regular". 3 horas é **muito pouco** independentemente da fase do ciclo; privação de sono por si só eleva FC de repouso e piora humor/foco. Pode ser falha de medição do relógio — vale conferir. Para o Charlee, **sono deveria pesar mais do que a fase** na capacidade do dia.

### 5.4 Previsões (e o quanto confiar nelas)

| Evento | App | Estimativa por estatística dos seus dados |
|---|---|---|
| Próxima menstruação | 10/12 – 14/12 | **10/12** (média), faixa provável **07/12 – 12/12** (ciclos de 24 a 29 dias) |
| Ovulação | 25/11 | ~**26–28/11** se a fase lútea for ~12–14 dias (média populacional 12,4); incerteza real de vários dias para cada lado |
| Janela fértil | 20/11 – 26/11 | Considerar uma janela mais larga (~20/11 – 28/11) se o objetivo for evitar gravidez |

Observação: as ovulações previstas pelo app nos ciclos anteriores ficaram, em geral, **15 dias** antes da menstruação seguinte (ex.: 29/10 → 13/11; 01/10 → 16/10), o que sugere que o app assume uma fase lútea mais longa do que a média encontrada em dados reais (12,4 dias). Se o app usa a temperatura do relógio, a confirmação pode ser melhor que isso — mas **calendário sozinho não é método contraceptivo confiável**.

### 5.5 Calendário 2027 (projeção)

O app projeta 2027 com ciclos de ~27 dias (ex.: jan 06–10, fev 02–06, mar 01–05, mar 28–abr 01…). Com seu desvio-padrão de ~1,6 dia, o erro se acumula: depois de 6 ciclos, a incerteza da projeção já é de **±4 dias**. Projeções de longo prazo servem para planejamento grosso, não para datas exatas.

---

## 6. Implicações para o Charlee (Cycle-Aware)

### 6.1 Problemas encontrados no código atual

1. **Bug — nomes de campos não batem com o modelo.** `backend/agent/specialized_agents/cycle_aware_agent.py` cria `MenstrualCycle(data_inicio=..., fase=..., nivel_energia=...)` e filtra por `MenstrualCycle.data_inicio`/`CyclePatterns.fase`, mas `backend/database/models.py` define `start_date`, `phase`, `energy_level`, `average_productivity` etc. Além disso o agente usa valores `'folicular'`, `'ovulacao'`, `'lutea'`, enquanto o `CheckConstraint` aceita apenas `'follicular'`, `'ovulation'`, `'luteal'`. As ferramentas do agente provavelmente falham em tempo de execução. Também falta `user_id` ao criar o registro.
2. **`CyclePatterns` não tem `user_id`** — padrões aprendidos não são por usuária.
3. **Modelo de dados centrado em "fase" digitada.** O dado primário confiável é a **data de início/fim da menstruação**; a fase deveria ser **derivada**, não registrada manualmente.
4. **Multiplicadores fixos (60/120/140/80%)** não têm suporte científico como regra geral (ver seção 4).

### 6.2 Modelo recomendado

**Dados primários (registrados):**
- `period_start`, `period_end` (como o app faz)
- Registro diário opcional: sintomas (mesmas categorias do app: sintomas físicos, humor, secreção, libido, digestão, outros, atividade física), energia/foco 1–10, sono (horas/qualidade), notas
- (Futuro) sinais de wearable: temperatura, FC de repouso, VFC, passos — via integração

**Dados derivados (calculados):**
- Dia do ciclo, duração média e desvio-padrão (média móvel dos últimos 6–12 ciclos)
- Previsão da próxima menstruação **com intervalo** (média ± 1–2 DP), nunca uma data única
- Fase estimada: `menstrual` (dias de sangramento) → `folicular` → `ovulação estimada` (próxima menstruação − ~12–14 dias, com margem) → `lútea`
- Flag de confiança: alta (temperatura/LH confirmando) vs. baixa (só calendário)

### 6.3 Aprender o padrão *dela*, não aplicar a tabela

- Começar com **multiplicador neutro (1,0)** em todas as fases.
- Após ≥ 3 ciclos com registros, calcular por fase (ou por dia do ciclo) a média de energia/foco, tarefas concluídas, sintomas. Só ajustar a capacidade quando a diferença for consistente (ex.: aparece em ≥ 2/3 dos ciclos).
- Exemplos de padrões aprendíveis: "nos D1–D2 você registra cólica e conclui 30% menos tarefas", "nos 3 dias antes da menstruação o sono piora".
- **Sono da noite anterior** e **sintomas do dia** devem ter peso maior que a fase na capacidade diária.
- Linguagem: sugerir, não determinar ("seus registros mostram que…" em vez de "na fase lútea você rende 80%").

### 6.4 Alertas de saúde úteis (baseados na FIGO)

- Ciclo < 24 ou > 38 dias
- Variação entre ciclos > 7 dias em 12 meses
- Menstruação > 8 dias, ou sangramento fora do período (o app tem "Sangramento de escape")
- Atraso > 7 dias além da faixa prevista
- Sintomas pré-menstruais intensos e recorrentes de humor (possível TPM/TDPM → sugerir conversar com profissional)
- Sono muito curto recorrente

Sempre com tom informativo e sugestão de procurar profissional de saúde — nunca diagnóstico.

### 6.5 Próximos passos sugeridos

1. Corrigir o bug de nomes de campos/valores no `CycleAwareAgent` (+ testes).
2. Adicionar tabela `menstrual_periods` (start/end) e `cycle_daily_logs` (sintomas por dia); derivar fase.
3. Implementar previsão com intervalo de confiança.
4. Substituir multiplicadores fixos por aprendizado individual com padrão neutro.
5. Importar o histórico acima (9 menstruações) como dados iniciais.
6. (Futuro) Integração com wearable (temperatura/FC) para confirmar ovulação.

---

## 7. Fontes

- Munro MG, Critchley HOD, Fraser IS (FIGO Menstrual Disorders Committee). *The two FIGO systems for normal and abnormal uterine bleeding symptoms and classification of causes of abnormal uterine bleeding in the reproductive years: 2018 revisions.* Int J Gynaecol Obstet 2018;143(3):393–408 — tabela em [MSD Manuals](https://www.msdmanuals.com/professional/multimedia/table/normal-menstrual-parameters) e [StatPearls – Physiology, Menstrual Cycle](https://pubmed.ncbi.nlm.nih.gov/29763196/)
- Bull JR et al. *Real-world menstrual cycle characteristics of more than 600,000 menstrual cycles.* npj Digital Medicine 2019 — [PMC6710244](https://pmc.ncbi.nlm.nih.gov/articles/PMC6710244) (autores ligados à Natural Cycles)
- Wilcox AJ, Dunson D, Baird DD. *The timing of the "fertile window" in the menstrual cycle.* BMJ 2000;321:1259 — [PMC27529](https://pmc.ncbi.nlm.nih.gov/articles/PMC27529)
- Jang D, Zhang J, Elfenbein HA. *Menstrual cycle effects on cognitive performance: A meta-analysis.* PLOS ONE 2025 — [PMC11913300](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11913300/)
- McNulty KL et al. *The Effects of Menstrual Cycle Phase on Exercise Performance in Eumenorrheic Women.* Sports Medicine 2020;50:1813–1827 — [NTU repository](https://irep.ntu.ac.uk/id/eprint/41201/1/1344931_Elliott-Sale.pdf)
- Alzueta E et al. *Tracking Sleep, Temperature, Heart Rate, and Daily Symptoms Across the Menstrual Cycle with the Oura Ring.* Int J Women's Health 2022 — [PMC9005074](https://pmc.ncbi.nlm.nih.gov/articles/PMC9005074)
- Reilly TJ et al. *The prevalence of premenstrual dysphoric disorder: Systematic review and meta-analysis.* J Affect Disord 2024 — [PubMed 38199397](https://pubmed.ncbi.nlm.nih.gov/38199397/)
