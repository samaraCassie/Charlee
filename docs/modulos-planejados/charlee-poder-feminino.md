# 👑 Charlee - Módulo: Poder Feminino Histórico

> **Versão**: 1.0
> **Status**: 📝 Em Desenvolvimento
> **Integração**: V7.x - Historical Intelligence & Strategic Advisory
> **Última Atualização**: 2025-11-18

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Módulo](#arquitetura-do-módulo)
3. [Base de Conhecimento](#base-de-conhecimento)
4. [Framework de Aplicação](#framework-de-aplicação)
5. [Integração com Charlee](#integração-com-charlee)
6. [Casos de Uso](#casos-de-uso)
7. [API e Interfaces](#api-e-interfaces)
8. [Considerações Éticas](#considerações-éticas)
9. [Roadmap](#roadmap)
10. [Referências](#referências)

---

## 🎯 Visão Geral

### Propósito do Módulo

O **Módulo de Poder Feminino Histórico** integra ao Charlee conhecimento profundo sobre estratégias de poder, influência e liderança feminina baseadas em cinco figuras históricas icônicas. O objetivo é fornecer **insights acionáveis** sobre:

- 🎭 Astúcia política e diplomacia
- 🤝 Construção de alianças estratégicas
- 👑 Tomada e manutenção de poder
- 🎨 Controle de narrativa e imagem
- ⚔️ Reconfiguração de poder em ambientes hostis

### Figuras Históricas Incluídas

| Figura | Período | Arquétipo | Expertise Principal |
|--------|---------|-----------|---------------------|
| **Cleópatra VII** | 69-30 a.C. | A Estrategista | Alianças e diplomacia multicultural |
| **Elizabeth I** | 1533-1603 | A Soberana | Frames e ambiguidade estratégica |
| **Catarina II** | 1729-1796 | A Imperatriz Graciosa | Tomada de poder sistemática |
| **Wu Zetian** | 624-705 | A Locomotiva | Escalada metodológica institucional |
| **Teodora** | 497-548 | A Cúmplice no Poder | Transformação radical e parcerias |

### Princípios Universais Extraídos

```python
PRINCIPIOS_UNIVERSAIS = {
    "educacao_como_base": "Conhecimento é primeira camada de poder",
    "aliancas_estrategicas": "Conexões multiplicam poder individual",
    "timing_perfeito": "Momento certo é tão importante quanto ação",
    "controle_narrativo": "Defina sua história antes que outros definam",
    "pragmatismo": "Efetividade > Pureza moral em conquista de poder",
    "coragem_critica": "Risco calculado em momentos decisivos"
}
```

---

## 🏗️ Arquitetura do Módulo

### Visão de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│           CHARLEE - MÓDULO PODER FEMININO                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   1. KNOWLEDGE BASE (Base de Conhecimento)          │   │
│  │  • Biografias detalhadas (5 figuras)                │   │
│  │  • Estratégias catalogadas (30+ frameworks)         │   │
│  │  • Contextos históricos completos                   │   │
│  │  • Erros e lições aprendidas                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   2. MATCHING ENGINE (Motor de Correspondência)     │   │
│  │  • Análise situacional do usuário                   │   │
│  │  • Mapeamento para figura relevante                 │   │
│  │  • Extração de insights aplicáveis                  │   │
│  │  • Geração de perguntas reflexivas                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                       ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   3. RESPONSE GENERATOR (Gerador de Respostas)      │   │
│  │  • Formatação conversacional                        │   │
│  │  • Contextualização moderna                         │   │
│  │  • Frameworks acionáveis                            │   │
│  │  • Avisos éticos quando necessário                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integração com Outros Módulos

```
Módulo Poder Feminino
         │
    ┌────┴────┐
    ↓         ↓
Strategic   Career
Advisor    Insights
    ↓         ↓
    └────┬────┘
         ↓
   Core Agent
   (Respostas)
```

---

## 📚 Base de Conhecimento

### Estrutura de Dados

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from datetime import date

class HistoricalStrategy(BaseModel):
    """Estratégia histórica catalogada"""
    nome: str = Field(..., description="Nome da estratégia")
    figura: Literal["cleopatra", "elizabeth_i", "catarina_ii", "wu_zetian", "teodora"]
    categoria: Literal[
        "aliancas", "frames", "tomada_poder",
        "escalada", "transformacao", "diplomacia"
    ]
    contexto_historico: str = Field(..., min_length=50)
    insight_principal: str
    aplicacao_moderna: str
    framework_code: Dict[str, any]
    avisos_eticos: List[str] = []
    exemplos_praticos: List[str]

class HistoricalFigure(BaseModel):
    """Figura histórica completa"""
    nome: str
    periodo: str
    anos_poder: int
    arquetipo: str
    contexto: str
    desafios: List[str]
    conquistas: List[str]
    estrategias: List[HistoricalStrategy]
    erros_criticos: List[Dict[str, str]]
    legado: Dict[str, int]  # Métricas quantificadas
    fontes: List[str]

class SituationMatch(BaseModel):
    """Correspondência situação-figura"""
    situacao_usuario: str
    figura_recomendada: str
    confianca_match: float = Field(..., ge=0, le=1)
    estrategias_aplicaveis: List[str]
    perguntas_reflexivas: List[str]
    avisos: List[str] = []
```

### Taxonomia de Situações

```python
SITUACOES_MAPEADAS = {
    "diplomacia_aliancas": {
        "keywords": [
            "negociação", "múltiplos atores", "poder desigual",
            "internacional", "aliança estratégica"
        ],
        "figura_primaria": "cleopatra",
        "secundaria": "elizabeth_i"
    },

    "ambiguidade_optionalidade": {
        "keywords": [
            "múltiplas ofertas", "pressão decisão", "polarizado",
            "independência", "casamento", "compromisso"
        ],
        "figura_primaria": "elizabeth_i",
        "secundaria": "cleopatra"
    },

    "tomada_poder_sistematica": {
        "keywords": [
            "estrangeiro", "outsider", "golpe", "revolução",
            "sistema hostil", "incompetente"
        ],
        "figura_primaria": "catarina_ii",
        "secundaria": "wu_zetian"
    },

    "escalada_hierarquica": {
        "keywords": [
            "subordinado", "hierarquia rígida", "subir de baixo",
            "tradicional", "conservador"
        ],
        "figura_primaria": "wu_zetian",
        "secundaria": "teodora"
    },

    "parceria_transformacao": {
        "keywords": [
            "parceiro", "relacionamento", "passado difícil",
            "transformação", "reforma social"
        ],
        "figura_primaria": "teodora",
        "secundaria": "catarina_ii"
    }
}
```

---

## 🔧 Framework de Aplicação

### Classe Principal do Módulo

```python
class PoderFemininoAgent:
    """
    Agente especializado em estratégias de poder feminino histórico.
    """

    def __init__(self, db: Session, knowledge_base: Dict):
        self.database = db
        self.knowledge_base = knowledge_base
        self.figuras = self._load_historical_figures()

    def analyze_situation(self, user_message: str) -> SituationMatch:
        """
        Analisa mensagem do usuário e identifica situação.

        Returns:
            SituationMatch com figura recomendada e insights
        """
        # 1. Extrai contexto da mensagem
        situacao = self._extract_situation_context(user_message)

        # 2. Mapeia para taxonomia
        categoria = self._match_situation_category(situacao)

        # 3. Seleciona figura histórica
        figura = self._select_historical_figure(categoria)

        # 4. Extrai estratégias aplicáveis
        estrategias = self._get_applicable_strategies(figura, situacao)

        # 5. Gera perguntas reflexivas
        perguntas = self._generate_reflection_questions(situacao, estrategias)

        return SituationMatch(
            situacao_usuario=situacao,
            figura_recomendada=figura.nome,
            confianca_match=self._calculate_confidence(situacao, figura),
            estrategias_aplicaveis=estrategias,
            perguntas_reflexivas=perguntas,
            avisos=self._generate_ethical_warnings(estrategias)
        )

    def generate_response(self, match: SituationMatch) -> str:
        """
        Gera resposta conversacional baseada no match.
        """
        figura = self.figuras[match.figura_recomendada]

        # Template de resposta
        response = f"""
        **{figura.nome}** enfrentou situação similar. Deixa eu te contar:

        **CONTEXTO HISTÓRICO:**
        {self._format_historical_context(figura)}

        **ESTRATÉGIA APLICÁVEL:**
        {self._format_strategy(match.estrategias_aplicaveis[0])}

        **PERGUNTAS PARA VOCÊ:**
        {self._format_questions(match.perguntas_reflexivas)}

        **FRAMEWORK PRÁTICO:**
        {self._format_framework(match.estrategias_aplicaveis[0])}

        {self._format_warnings(match.avisos) if match.avisos else ""}
        """

        return response

    def _extract_situation_context(self, message: str) -> str:
        """Extrai contexto usando NLP"""
        # Análise semântica da mensagem
        entities = self._extract_entities(message)
        intent = self._detect_intent(message)

        return {
            "text": message,
            "entities": entities,
            "intent": intent,
            "keywords": self._extract_keywords(message)
        }

    def _match_situation_category(self, situacao: Dict) -> str:
        """Mapeia situação para categoria da taxonomia"""
        scores = {}

        for categoria, config in SITUACOES_MAPEADAS.items():
            score = self._calculate_similarity(
                situacao["keywords"],
                config["keywords"]
            )
            scores[categoria] = score

        # Retorna categoria com maior score
        return max(scores, key=scores.get)

    def _generate_reflection_questions(
        self,
        situacao: Dict,
        estrategias: List[str]
    ) -> List[str]:
        """Gera perguntas reflexivas contextualizadas"""
        questions = []

        # Perguntas baseadas na estratégia
        for estrategia in estrategias:
            template = self.knowledge_base[estrategia]["question_template"]
            questions.append(template.format(**situacao))

        return questions

    def _generate_ethical_warnings(self, estrategias: List[str]) -> List[str]:
        """Gera avisos éticos quando estratégia envolver métodos questionáveis"""
        warnings = []

        # Estratégias que requerem aviso
        REQUIRES_WARNING = [
            "golpe_de_estado",
            "eliminacao_rivais",
            "espionagem_totalitaria",
            "manipulacao_religiosa"
        ]

        for estrategia in estrategias:
            if any(keyword in estrategia for keyword in REQUIRES_WARNING):
                warnings.append(
                    f"⚠️ AVISO ÉTICO: A estratégia '{estrategia}' foi efetiva "
                    f"historicamente mas envolveu métodos questionáveis. "
                    f"Adapte os PRINCÍPIOS (não as ações literais) ao contexto "
                    f"moderno e valores éticos."
                )

        return warnings
```

### Frameworks Específicos por Figura

#### 1. Framework Cleópatra - Alianças Estratégicas

```python
def framework_aliancas_cleopatra():
    """
    Framework baseado nas estratégias de aliança de Cleópatra.
    """
    return {
        "titulo": "Construindo Alianças Estratégicas à la Cleópatra",

        "passos": [
            {
                "passo": "1. Avaliação de Necessidade",
                "pergunta": "Qual problema esta aliança resolve?",
                "exemplo_cleopatra": "Egito precisava proteção militar de Roma",
                "acao_moderna": "Identifique sua vulnerabilidade principal"
            },
            {
                "passo": "2. Análise de Poder",
                "pergunta": "O que cada parte tem que a outra precisa?",
                "exemplo_cleopatra": "Egito: riqueza + conhecimento; Roma: legião",
                "acao_moderna": "Mapeie value exchange bilateral"
            },
            {
                "passo": "3. Timing",
                "pergunta": "Este é o momento de maior alavancagem?",
                "exemplo_cleopatra": "Esperou César estar na posição mais poderosa",
                "acao_moderna": "Espere momento de máxima necessidade do outro"
            },
            {
                "passo": "4. Simbolismo",
                "pergunta": "Como apresento isso de forma memorável?",
                "exemplo_cleopatra": "Entrada dramática escondida em tapete",
                "acao_moderna": "Crie first impression inesquecível"
            },
            {
                "passo": "5. Garantias Mútuas",
                "pergunta": "Quais são os 'reféns' mútuos?",
                "exemplo_cleopatra": "Filho (Cesárion) = garantia política",
                "acao_moderna": "Projetos conjuntos, equity, incentivos alinhados"
            },
            {
                "passo": "6. Saída Estratégica",
                "pergunta": "Como preservo dignidade se terminar?",
                "exemplo_cleopatra": "Manteve Egito independente até morte",
                "acao_moderna": "Defina exit clauses dignos antecipadamente"
            }
        ],

        "metricas_sucesso": {
            "curto_prazo": "Aliança formada sem submissão",
            "medio_prazo": "Benefícios mútuos realizados",
            "longo_prazo": "Poder ampliado através da aliança"
        },

        "red_flags": [
            "Aliança baseada apenas em emoção (não estratégia)",
            "Você precisa mais do aliado que ele de você (poder desigual)",
            "Sem 'garantias' mútuas (sem skin in the game)",
            "Impossibilidade de saída digna"
        ]
    }
```

#### 2. Framework Elizabeth I - Optionalidade e Frames

```python
def framework_optionalidade_elizabeth():
    """
    Framework de jogo de frames e manutenção de optionalidade.
    """
    return {
        "titulo": "Jogo de Frames à la Elizabeth I",

        "principio_central": "OPTIONALIDADE É PODER",

        "situacoes_aplicaveis": [
            "Múltiplas ofertas de emprego/parceria",
            "Pressão para tomar decisão rápida",
            "Contexto polarizado",
            "Necessidade de manter independência"
        ],

        "estrategia_frame_casamento": {
            "problema": "Como manter poder sem comprometer-se?",
            "solucao_elizabeth": "Manteve POSSIBILIDADE de casamento, nunca realizou",
            "porque_funcionou": [
                "Pretendentes mantidos na esperança",
                "Cada um oferecia benefícios para conquistá-la",
                "Casamento real = perda de poder (submissão legal)",
                "Virgindade estratégica = multiplicação de influência"
            ],
            "modernizacao": {
                "cenario": "Múltiplas ofertas de trabalho",
                "aplicacao": [
                    "Mantenha todas as opções 'talvez' (não sim, não não)",
                    "Use oferta A para melhorar B, B para C",
                    "Pergunta-chave: 'Quem se beneficia da MINHA decisão rápida?'",
                    "Compre tempo: 'Preciso garantir fit perfeito'",
                    "Só feche quando for MELHOR para você"
                ]
            }
        },

        "estrategia_ambiguidade_religiosa": {
            "problema": "Como liderar em contexto polarizado?",
            "solucao_elizabeth": "Igreja Anglicana = meio-termo flexível",
            "principio": "Clareza nem sempre é virtude",
            "aplicacao_moderna": [
                "Nem sempre defina posição 100%",
                "Ambiguidade permite múltiplos grupos se identificarem",
                "Propor 'terceira via' em debates polarizados",
                "Reconhecer mérito em ambos os lados"
            ]
        },

        "framework_discurso_tilbury": {
            "contexto": "Momento de crise, necessidade de inspirar",
            "estrutura": [
                "1. Reconheça percepção negativa diretamente",
                "2. Use 'mas/porém/contudo' como ponte",
                "3. Reframe 'fraqueza' como força única",
                "4. Conecte com valor maior (nação, missão, equipe)"
            ],
            "exemplo_elizabeth": [
                "'Sei que tenho corpo de mulher fraca...'",
                "'...MAS tenho coração de rei da Inglaterra'"
            ],
            "exemplo_moderno": [
                "'Sei que sou o mais jovem desta sala...'",
                "'...MAS justamente por isso trago energia fresca que precisamos'"
            ]
        },

        "quando_fechar_opcao": {
            "sinais": [
                "Melhor oferta melhorou 30%+ através do processo",
                "Outras opções começam a desistir (você maximizou leverage)",
                "Custo de oportunidade de esperar > benefício",
                "Você genuinamente quer essa opção (não só processo)"
            ]
        }
    }
```

#### 3. Framework Catarina II - Tomada Sistemática de Poder

```python
def framework_golpe_catarina():
    """
    Framework para mudança radical sistemática (aplicação ética).
    """
    return {
        "titulo": "Tomada de Poder Sistemática à la Catarina II",

        "aviso_inicial": "⚠️ Este framework é sobre mudança organizacional profunda, não golpe literal.",

        "fase_1_autoconhecimento": {
            "objetivo": "Mapear suas forças e fraquezas objetivamente",
            "perguntas": [
                "Liste 5 coisas que você faz melhor que 90% das pessoas",
                "Quais dessas são VALORIZADAS no contexto atual?",
                "Liste 3 desvantagens inegáveis da sua situação",
                "Quais dessas podem ser TRANSFORMADAS em vantagens?",
                "O que você NÃO tem mas PRECISA? Quem tem?"
            ],
            "exemplo_catarina": {
                "forcas": ["Influência interpessoal", "Objetividade", "Foco"],
                "fraquezas": ["Estrangeira", "Jovem", "Casamento ruim"],
                "compensacao": "Aprendeu russo fluentemente (superou 'estrangeira')"
            }
        },

        "fase_2_construcao_consenso": {
            "objetivo": "Identificar insatisfação generalizada",
            "acoes": [
                "Mapeie quem está insatisfeito com status quo",
                "Identifique por QUE estão insatisfeitos",
                "Posicione-se como solução óbvia",
                "Construa coalizão (militar, econômico, legitimidade)"
            ],
            "exemplo_catarina": {
                "insatisfacao": "Pedro III tomou decisões desastrosas",
                "coalizao": ["Guarda Imperial", "Nobreza", "Clero"],
                "legitimidade": "Mãe do herdeiro legítimo (Paulo)"
            }
        },

        "fase_3_timing": {
            "objetivo": "Esperar erro fatal do 'regime atual'",
            "principio": "Nunca interrompa inimigo cometendo erro",
            "sinais_prontos": [
                "Insatisfação atinge ponto crítico",
                "Oponente comete erro visível e inegável",
                "Sua coalizão está completa e pronta",
                "Janela de oportunidade se abre (oponente ausente/fraco)"
            ]
        },

        "fase_4_execucao": {
            "objetivo": "Ação rápida e decisiva",
            "principios": [
                "Aja RÁPIDO quando janela abrir (não hesite)",
                "Controle narrativa IMEDIATAMENTE",
                "Neutralize oposição de forma irreversível",
                "Ofereça estabilidade imediata pós-mudança"
            ]
        },

        "fase_5_legitimacao": {
            "objetivo": "Transformar poder tomado em poder merecido",
            "estrategias": [
                "Entregue resultados visíveis rapidamente",
                "Invista em cultura/arte (soft power)",
                "Construa narrativa de 'necessidade histórica'",
                "Recompense aliados generosamente"
            ],
            "exemplo_catarina": {
                "resultados": "Expansão territorial, modernização",
                "cultura": "Hermitage, correspondência com Voltaire",
                "narrativa": "'Despotismo Esclarecido'",
                "recompensas": "Orlov promovido, terras distribuídas"
            }
        },

        "aplicacao_corporativa": {
            "contexto": "Mudança de liderança/cultura organizacional",
            "traducao_etica": {
                "golpe": "→ Mudança legítima de liderança",
                "eliminacao": "→ Realocação de pessoas-chave",
                "controle_narrativa": "→ Comunicação estratégica clara",
                "coalizao": "→ Stakeholder buy-in",
                "timing": "→ Change management no momento certo"
            }
        }
    }
```

#### 4. Framework Wu Zetian - Escalada Hierárquica

```python
def framework_escalada_wu():
    """
    Framework de ascensão sistemática em hierarquias rígidas.
    """
    return {
        "titulo": "Escalada Metodológica à la Wu Zetian",

        "principio_central": "Aprenda cada degrau antes de subir",

        "fase_1_entrada": {
            "objetivo": "Entrar no sistema (mesmo posição baixa)",
            "estrategia": "Seja notada por quebrar protocolo ESTRATEGICAMENTE",
            "exemplo_wu": "Falou com imperador (proibido para concubina baixa)",
            "modernizacao": [
                "Aceite posição 'abaixo' de sua capacidade para aprender",
                "Faça algo memorável que demonstre valor único",
                "Priorize ACESSO sobre título inicial"
            ],
            "pergunta": "Estou disposto a começar 'de baixo' para aprender sistema?"
        },

        "fase_2_aprendizado": {
            "objetivo": "Dominar mecânica interna do sistema",
            "estrategia": "Aceite posição de 'assistente/secretária'",
            "exemplo_wu": "Secretária do imperador = acesso a documentos/decisões",
            "modernizacao": [
                "Chief of Staff",
                "Executive Assistant",
                "Special Projects",
                "Qualquer role que dê VISIBILIDADE de como decisões reais são tomadas"
            ],
            "pergunta": "Qual posição me dá visibilidade máxima de mecânica de poder?"
        },

        "fase_3_eliminacao": {
            "objetivo": "Remover bloqueadores acima de você",
            "estrategia_wu": "Imperatriz Wang eliminada quando vulnerável",
            "estrategia_etica": [
                "Identifique quem está no caminho",
                "Espere eles cometerem erro/ficarem vulneráveis",
                "Ofereça alternativa melhor que os torna irrelevantes",
                "Nunca destrua - torne obsoletos ou realoque"
            ],
            "pergunta": "Quem está bloqueando meu caminho E está vulnerável agora?"
        },

        "fase_4_controle_proxy": {
            "objetivo": "Poder de fato sem exposição total",
            "estrategia": "Governe através de figurehead",
            "exemplo_wu": "Marido doente = Wu decide, ele assina",
            "modernizacao": [
                "Torne-se 'person behind the throne'",
                "Deixe líder formal ter título, você tem decisão",
                "Vantagem: menos atenção, mais controle"
            ],
            "quando_usar": "Quando ambiente é hostil a você ter poder direto"
        },

        "fase_5_oficializacao": {
            "objetivo": "Poder formal e título",
            "estrategia": "Quando infraestrutura está sob controle, ENTÃO pegue título",
            "exemplo_wu": "690 = já controlava tudo, só tornou oficial",
            "sinais_prontos": [
                "Você controla decisões reais há tempo suficiente",
                "Coalizão de apoio está consolidada",
                "Oposição foi neutralizada",
                "Custo de manter proxy > benefício"
            ]
        },

        "estrategias_complementares": {
            "troca_base_ideologica": {
                "contexto": "Sistema atual te bloqueia ideologicamente",
                "exemplo_wu": "Confucionismo bloqueava → Budismo favorecia",
                "modernizacao": "Se meritocracia te bloqueia, promova inovação; se tradição te bloqueia, promova disrupção"
            },
            "meritocracia_como_arma": {
                "contexto": "Aristocracia hereditária te exclui",
                "exemplo_wu": "Exames imperiais = nova classe leal a ela",
                "modernizacao": "Crie novo sistema de avaliação que TE favorece"
            }
        },

        "tempo_total": "40-50 anos (Wu levou 50 anos de lavadeira a imperador)",
        "mentalidade": "Paciência estratégica + ação decisiva no momento certo"
    }
```

#### 5. Framework Teodora - Transformação e Parcerias

```python
def framework_transformacao_teodora():
    """
    Framework de transformação radical de identidade e parcerias igualitárias.
    """
    return {
        "titulo": "Transformação Radical e Parcerias à la Teodora",

        "parte_1_transformacao_identidade": {
            "contexto": "Passado 'questionável' que você quer superar",

            "passo_1_reconhecimento": {
                "acao": "Admita honestamente onde você está",
                "exemplo_teodora": "Sou atriz/prostituta em sociedade que me estigmatiza",
                "pergunta": "Qual é o rótulo/situação atual que quero mudar?"
            },

            "passo_2_decisao_irreversivel": {
                "acao": "Faça escolha irreversível de mudar",
                "exemplo_teodora": "Deixou vida de atriz PERMANENTEMENTE",
                "pergunta": "Estou disposto a CORTAR ponte com passado?"
            },

            "passo_3_mudanca_contexto": {
                "acao": "Mude ambiente físico/social",
                "exemplo_teodora": "Viajou, voltou como 'outra pessoa'",
                "pergunta": "Posso mudar de cidade/empresa/círculo social?"
            },

            "passo_4_novo_simbolismo": {
                "acao": "Adote símbolos da nova identidade",
                "exemplo_teodora": "Conversão cristã, trabalho de fiandeira",
                "pergunta": "Quais símbolos/comportamentos comunicam nova identidade?"
            },

            "passo_5_aliado_validador": {
                "acao": "Encontre quem valida nova identidade PUBLICAMENTE",
                "exemplo_teodora": "Justiniano mudou LEI para casar com ela",
                "pergunta": "Quem, ao me aceitar, faz outros terem que aceitar?"
            },

            "passo_6_consistencia": {
                "acao": "NUNCA volte ao comportamento antigo",
                "exemplo_teodora": "Jamais voltou à vida de atriz",
                "pergunta": "Estou 100% comprometido ou 'tentando'?"
            },

            "passo_7_legado_redentor": {
                "acao": "Use passado doloroso para ajudar outros",
                "exemplo_teodora": "Criou Convento Metanoia para ex-prostitutas",
                "pergunta": "Como meu passado pode se tornar minha missão?"
            }
        },

        "parte_2_parceria_igualitaria": {
            "contexto": "Avaliação de potencial parceiro(a) de negócios/vida",

            "criterios_selecao": [
                {
                    "criterio": "Respeito Intelectual",
                    "pergunta": "Ele/ela pede minha opinião ANTES de decidir?",
                    "exemplo_teodora": "Justiniano consultava Teodora em tudo",
                    "red_flag": "Só informa depois de decidir"
                },
                {
                    "criterio": "Segurança Emocional",
                    "pergunta": "Ele/ela se sente ameaçado quando brilho?",
                    "exemplo_teodora": "Justiniano amava quando Teodora brilhava",
                    "red_flag": "Insegurança competitiva, ciúme de sucesso"
                },
                {
                    "criterio": "Coragem Mútua",
                    "pergunta": "Em crise, nos fortalecemos ou culpamos?",
                    "exemplo_teodora": "Revolta Nika - ela salvou trono dele",
                    "red_flag": "Culpa mútua em dificuldades"
                },
                {
                    "criterio": "Divisão Clara",
                    "pergunta": "Cada um tem domínio próprio?",
                    "exemplo_teodora": "Justiniano: guerra/lei; Teodora: social/intel",
                    "red_flag": "Sobreposição competitiva de papéis"
                },
                {
                    "criterio": "Divergência Saudável",
                    "pergunta": "Podemos discordar E nos apoiar publicamente?",
                    "exemplo_teodora": "Ele calcedônio, ela miafisita (discordavam teologicamente)",
                    "red_flag": "Desautorização pública"
                }
            ],

            "scoring": {
                "interpretacao": [
                    "5/5 'sim': Você tem Teodora-Justiniano",
                    "3-4/5: Parceria viável com trabalho",
                    "≤2/5: Reavalie antes de comprometer-se"
                ]
            },

            "momento_critico_teste": {
                "nome": "Teste da Revolta Nika",
                "cenario": "Situação de crise extrema",
                "pergunta": "Parceiro(a) te salva ou abandona?",
                "exemplo_teodora": "Todos queriam fugir, Teodora disse 'eu fico'",
                "licao": "Parceria real se revela em momentos de colapso"
            }
        },

        "parte_3_passado_em_missao": {
            "principio": "Sua maior dor pode ser sua maior missão",

            "framework": [
                {
                    "passo": "Identifique Sofrimento Sistêmico",
                    "pergunta": "O que sofri que NINGUÉM deveria sofrer?",
                    "exemplo_teodora": "Prostituição forçada"
                },
                {
                    "passo": "Chegue a Posição de Poder",
                    "pergunta": "Onde preciso estar para fazer diferença sistêmica?",
                    "exemplo_teodora": "Imperatriz = poder legislativo"
                },
                {
                    "passo": "Crie Estruturas Protetivas",
                    "pergunta": "Que 'lei/regra/norma' posso criar?",
                    "exemplo_teodora": "Leis anti-prostituição forçada, Convento Metanoia"
                },
                {
                    "passo": "Transforme Vergonha em Propósito",
                    "pergunta": "Como ferida se torna sabedoria?",
                    "exemplo_teodora": "PORQUE foi prostituta, entendia prostituição profundamente"
                }
            ],

            "resultado": "Legado redentor - Teodora = primeira defensora legal de mulheres no Ocidente"
        }
    }
```

---

## 🔌 Integração com Charlee

### Integração com Strategic Advisor

```python
class StrategicAdvisor:
    """
    Strategic Advisor ampliado com insights de poder feminino.
    """

    def __init__(self, db: Session):
        self.database = db
        self.poder_feminino = PoderFemininoAgent(db, knowledge_base)

    async def prepare_strategic_decision(
        self,
        user_id: int,
        decision_context: str
    ) -> StrategicAdvice:
        """
        Prepara conselho estratégico integrando insights históricos.
        """
        # Lógica existente do Strategic Advisor
        base_advice = await self._generate_base_advice(decision_context)

        # NOVO: Adiciona perspectiva de poder feminino
        historical_match = self.poder_feminino.analyze_situation(decision_context)

        if historical_match.confianca_match > 0.7:
            historical_insights = self.poder_feminino.generate_response(historical_match)

            base_advice.sections.append({
                "title": f"📚 Insight Histórico: {historical_match.figura_recomendada}",
                "content": historical_insights,
                "priority": "high"
            })

        return base_advice
```

### Integração com Core Agent

```python
class CharleeAgent:
    """
    Core Agent com acesso a módulo de poder feminino.
    """

    def __init__(self, db: Session, user_id: str):
        self.database = db
        self.user_id = user_id
        self.poder_feminino = PoderFemininoAgent(db, knowledge_base)

        # Adiciona tools de poder feminino
        self.agent = Agent(
            name="Charlee",
            tools=[
                # ... tools existentes ...
                self.consultar_estrategia_historica,
                self.listar_figuras_historicas,
                self.aplicar_framework_historico,
            ]
        )

    def consultar_estrategia_historica(
        self,
        situacao: str,
        figura_especifica: str = None
    ) -> str:
        """
        Consulta estratégia histórica relevante para situação.

        Args:
            situacao: Descrição da situação atual do usuário
            figura_especifica: Nome da figura (opcional, para consulta direta)
        """
        if figura_especifica:
            # Consulta direta a figura específica
            figura = self.poder_feminino.figuras[figura_especifica]
            return self.poder_feminino._format_figura_completa(figura)
        else:
            # Match automático
            match = self.poder_feminino.analyze_situation(situacao)
            return self.poder_feminino.generate_response(match)

    def listar_figuras_historicas(self) -> str:
        """Lista todas as figuras históricas disponíveis com resumo."""
        figuras = self.poder_feminino.figuras

        result = "📚 **Figuras Históricas no Charlee:**\n\n"

        for nome, figura in figuras.items():
            result += f"**{figura.nome}** ({figura.periodo})\n"
            result += f"└─ Arquétipo: {figura.arquetipo}\n"
            result += f"└─ Expertise: {figura.expertise}\n"
            result += f"└─ `consultar_estrategia_historica(figura_especifica='{nome}')`\n\n"

        return result

    def aplicar_framework_historico(
        self,
        framework: str,
        contexto_usuario: str
    ) -> str:
        """
        Aplica framework específico ao contexto do usuário.

        Args:
            framework: Nome do framework (ex: 'aliancas_cleopatra')
            contexto_usuario: Contexto específico do usuário
        """
        framework_func = getattr(self.poder_feminino, f"framework_{framework}")
        framework_data = framework_func()

        # Personaliza framework com contexto do usuário
        personalized = self.poder_feminino._personalize_framework(
            framework_data,
            contexto_usuario
        )

        return personalized
```

### Integração com Career Insights

```python
class CareerInsightsAgent:
    """
    Career Insights ampliado com padrões históricos de ascensão.
    """

    def __init__(self, db: Session, user_id: int):
        self.database = db
        self.user_id = user_id
        self.poder_feminino = PoderFemininoAgent(db, knowledge_base)

    def analyze_career_trajectory(self) -> CareerAnalysis:
        """
        Analisa trajetória de carreira comparando com padrões históricos.
        """
        # Análise existente
        base_analysis = self._generate_base_career_analysis()

        # Identifica padrão histórico similar
        trajectory_pattern = self._extract_trajectory_pattern(base_analysis)

        historical_parallel = self._find_historical_parallel(trajectory_pattern)

        if historical_parallel:
            base_analysis.historical_insights = {
                "figura": historical_parallel.nome,
                "semelhanca": historical_parallel.similarity_score,
                "proximos_passos_historicos": historical_parallel.next_moves,
                "licoes": historical_parallel.lessons
            }

        return base_analysis

    def _find_historical_parallel(self, pattern: Dict) -> HistoricalParallel:
        """
        Encontra paralelo histórico baseado em padrão de trajetória.

        Padrões mapeados:
        - "outsider_escalando": Wu Zetian (40-50 anos escalando)
        - "transformacao_radical": Teodora (prostituta → imperatriz)
        - "estrangeiro_conquistando": Catarina II (alemã → czarina)
        - "diplomata_navegando": Cleópatra (aliançasse estratégicas)
        - "independente_mantendo": Elizabeth I (virgindade política)
        """
        # Implementação de matching de padrões
        ...
```

---

## 📊 Casos de Uso

### Caso de Uso 1: Negociação com Empresa Maior

**Situação do Usuário:**
```
"Estou negociando contrato com empresa 100x maior que eu.
Como não ser esmagado? Eles têm todo o poder."
```

**Resposta do Charlee (via Poder Feminino):**

```
**Cleópatra** enfrentou EXATAMENTE isso. O Egito era rico mas
militarmente inferior a Roma (maior império do mundo).

**CONTEXTO HISTÓRICO:**
- Roma podia esmagar Egito militarmente a qualquer momento
- Cleópatra tinha 21 anos, recém-chegada ao poder
- Júlio César controlava legião mais poderosa da época

**O QUE ELA FEZ:**
1. **Não competiu em força**: Maximizou o que TINHA (riqueza, cultura)
2. **Estudou o "inimigo"**: Aprendeu latim, cultura romana
3. **Ofereceu valor único**: Egito como ponte civilizacional
4. **Timing perfeito**: Esperou César estar em posição de precisar dela
5. **Entrada memorável**: Escondida em tapete (first impression inesquecível)

**FRAMEWORK PARA VOCÊ:**

┌─────────────────────────────────────┐
│  ALIANÇA DESIGUAL À LA CLEÓPATRA    │
├─────────────────────────────────────┤
│                                     │
│ 1. VALOR ÚNICO                      │
│    O que VOCÊ tem que gigante       │
│    PRECISA (mas não consegue        │
│    facilmente em outro lugar)?      │
│                                     │
│    No seu caso:                     │
│    • Agilidade? Inovação?           │
│    • Conhecimento de nicho?         │
│    • Acesso a mercado específico?   │
│                                     │
│ 2. CONHECIMENTO PROFUNDO            │
│    Você conhece ELES melhor que     │
│    eles conhecem você?              │
│                                     │
│    Ação: Estude cultura deles,      │
│    linguagem interna, prioridades   │
│                                     │
│ 3. TIMING DE NECESSIDADE            │
│    Quando ELES mais precisam de     │
│    você? (prazo, problema, crise)   │
│                                     │
│    Espere esse momento para         │
│    maximizar leverage               │
│                                     │
│ 4. INDISPENSABILIDADE               │
│    Como ser INDISPENSÁVEL vs        │
│    DESCARTÁVEL?                     │
│                                     │
│    Cleópatra: única fonte de        │
│    estabilidade no Egito            │
│    Você: único que resolve X?       │
│                                     │
└─────────────────────────────────────┘

**PERGUNTAS PARA VOCÊ:**

1. Se você fosse ELES, o que seria mais difícil de encontrar em outro fornecedor?

2. Que conhecimento sobre ELES você pode adquirir que dá vantagem na mesa?

3. Há momento específico em que ELES precisam mais de você? (Deadline, crise, lacuna)

4. Como transformar "pequeno" em "ágil e especializado" (vs "fraco")?

**CLEÓPATRA SOBREVIVEU 20 ANOS CONTRA ROMA.**
Tamanho não é destino. Estratégia é.

⚠️ Nota: Cleópatra eventualmente perdeu para Roma. Mas manteve Egito
independente por 2 décadas através de inteligência (não força).
E entrou para história como uma das figuras mais icônicas já existidas.
```

### Caso de Uso 2: Múltiplas Ofertas de Emprego

**Situação:**
```
"Tenho 3 ofertas de emprego. Empresas A, B e C pressionando
para eu decidir esta semana. Estou perdido."
```

**Resposta do Charlee:**

```
**Elizabeth I** manteve 20 pretendentes em suspense por 45 ANOS.
Por quê? Porque descobriu algo fundamental:

🔑 OPTIONALIDADE É PODER

**CONTEXTO DELA:**
- Casamento = submissão legal ao marido (perda de poder)
- Cada pretendente oferecia benefícios (alianças, proteção)
- Enquanto TODOS achavam que tinham chance, TODOS ofereciam

**O JOGO DE ELIZABETH:**
- Nunca disse "não" definitivo
- Nunca disse "sim"
- Manteve TODOS na categoria "talvez"
- Resultado: 45 anos de ofertas crescentes

**SEU CENÁRIO:**

Empresas pressionando para decidir RÁPIDO?
Pergunte: QUEM se beneficia da SUA decisão rápida?

Resposta: ELAS (não você)

**FRAMEWORK OPTIONALIDADE:**

┌────────────────────────────────────┐
│   JOGO DE FRAMES À LA ELIZABETH    │
├────────────────────────────────────┤
│                                    │
│ SEMANA 1: "Preciso garantir fit    │
│            perfeito antes de       │
│            decisão tão importante" │
│                                    │
│ → Compra 1-2 semanas               │
│ → Usa oferta A p/ melhorar B       │
│ → Usa oferta B p/ melhorar C       │
│ → Usa oferta C p/ melhorar A       │
│                                    │
│ SEMANA 2-3: Continua 'avaliando'   │
│                                    │
│ → Melhor oferta melhora 20-30%     │
│ → Você tem CONTROLE do processo    │
│                                    │
│ DECISÃO: Quando VOCÊ decide        │
│          (não quando elas pressionam)│
│                                    │
└────────────────────────────────────┘

**SCRIPT ELIZABETH:**

Empresa: "Precisamos de resposta até sexta"

Você: "Entendo a urgência. E justamente porque
valorizo muito essa oportunidade, preciso ter
certeza absoluta do fit. Posso ter até [data +2 semanas]
para uma decisão tão importante quanto essa?"

[90% das vezes elas aceitam]

**PERGUNTAS REFLEXIVAS:**

1. Qual dessas 3 empresas MAIS precisa de você?
   (Eles têm menos leverage)

2. Se você pedisse mais 2 semanas, qual recusaria?
   (Red flag: se não podem esperar 2 semanas,
   imagina trabalhando lá)

3. Usando oferta mais alta, você consegue melhorar
   as outras? (Teste: "Empresa X ofereceu Y,
   vocês conseguem igualar?")

4. Qual você GENUINAMENTE quer (vs qual é só
   resultado de ansiedade para decidir logo)?

**QUANDO FECHAR:**
- Melhor oferta melhorou 30%+ no processo
- Você maximizou leverage possível
- Custo de esperar > benefício
- Você GENUINAMENTE quer essa (não só processo)

Elizabeth I só "fecharia" se alguém oferecesse algo
que justificasse perder a optionalidade.

Nenhum príncipe ofereceu. Então ela manteve poder.

No seu caso: só feche quando oferta justifica perder
o jogo de leverage.

⚠️ CUIDADO: Não abuse. Elizabeth sabia QUANDO fechar
(apenas nenhum pretendente justificou). Se você
identificar "the one", não perca por jogar demais.
```

### Caso de Uso 3: Passado "Questionável" e Transformação

**Situação:**
```
"Quero mudar completamente de carreira mas meu histórico
é 'questionável'. Como superar isso?"
```

**Resposta do Charlee:**

```
**Teodora de Bizâncio** foi LITERALMENTE prostituta e
virou imperatriz. Se ela conseguiu no século VI...

**CONTEXTO DELA:**
- Nasceu em família pobre (treinador de animais)
- Aos 15: atriz (= prostituta na percepção da época)
- Profissão mais estigmatizada da sociedade
- Chance de virar imperatriz: ZERO (teoricamente)

**O QUE MUDOU:**
Aos 25 anos, fez decisão IRREVERSÍVEL de transformar-se.

**FRAMEWORK DE TRANSFORMAÇÃO RADICAL:**

┌──────────────────────────────────────────┐
│     TRANSFORMAÇÃO À LA TEODORA           │
├──────────────────────────────────────────┤
│                                          │
│ FASE 1: DECISÃO IRREVERSÍVEL             │
│                                          │
│ Teodora: Deixou vida de atriz            │
│         PERMANENTEMENTE (não "pausa")    │
│                                          │
│ Você: Está "experimentando" ou          │
│       CORTANDO ponte com passado?        │
│                                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│ FASE 2: MUDANÇA DE CONTEXTO              │
│                                          │
│ Teodora: Viajou (Alexandria, Antioquia), │
│         voltou como "outra pessoa"       │
│                                          │
│ Você: Pode mudar fisicamente?            │
│       (cidade, empresa, círculo social)  │
│                                          │
│ Princípio: Novo contexto = novo você    │
│                                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│ FASE 3: NOVO SIMBOLISMO                  │
│                                          │
│ Teodora: • Conversão cristã (pública)    │
│         • Trabalho honesto (fiandeira)   │
│         • Postura de dignidade           │
│                                          │
│ Você: Quais símbolos comunicam nova      │
│       identidade? (certificação, role,   │
│       aparência, linguagem, network)     │
│                                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│ FASE 4: ALIADO VALIDADOR                 │
│                                          │
│ Teodora: Justiniano MUDOU A LEI para     │
│         poder casar com ela              │
│                                          │
│ Você: Quem, ao te aceitar, faz          │
│       outros TEREM que aceitar?          │
│                                          │
│ Exemplos: CEO renomado te contrata,     │
│          instituição prestigiosa te      │
│          certifica, mentor respeitado    │
│          te valida publicamente          │
│                                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│ FASE 5: CONSISTÊNCIA ABSOLUTA            │
│                                          │
│ Teodora: JAMAIS voltou à vida antiga     │
│         (mesmo em privado)               │
│                                          │
│ Você: 100% comprometido ou "tentando"?   │
│                                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                          │
│ FASE 6: LEGADO REDENTOR                  │
│                                          │
│ Teodora: Usou experiência dolorosa       │
│         para criar primeiras leis de     │
│         proteção a mulheres              │
│                                          │
│ Você: Como seu passado pode se tornar    │
│       sua MISSÃO (não vergonha)?         │
│                                          │
└──────────────────────────────────────────┘

**PERGUNTAS CRÍTICAS:**

1. **COMPROMISSO**
   Numa escala 1-10, quão comprometido você está?
   Teodora foi 10/10 (deixou tudo para trás)
   Você está em que número?

2. **RESET GEOGRÁFICO**
   Você pode mudar de ambiente completamente?
   (Cidade nova, empresa nova, rede social nova)
   Se não, como criar "reset" simbólico?

3. **VALIDAÇÃO EXTERNA**
   Quem é seu "Justiniano"?
   Quem tem poder de validar você publicamente?
   Como conseguir atenção/apoio dessa pessoa?

4. **TESTE DA TENTAÇÃO**
   Se algo do passado te chamar de volta,
   você recusaria 100%? Ou "talvez"?
   Teodora recusou 100% sempre.

5. **MISSÃO REDENTORA**
   Seu sofrimento passado pode ajudar outros?
   Como transformar ferida em propósito?

**A TRANSFORMAÇÃO MAIS IMPRESSIONANTE DA HISTÓRIA:**

Teodora: Prostituta (15 anos) → Imperatriz (30 anos)
Timeline: 10-15 anos de transformação
Resultado: Primeira defensora legal de mulheres no Ocidente

Sua dor não precisa ser em vão.
Pode ser sua TESE.

⚠️ REALISMO: Teodora teve sorte (conhecer Justiniano).
Mas ela CRIOU a oportunidade:
- Mudou-se perto do palácio (não coincidência)
- Manteve dignidade (não suplicou)
- Era intelectualmente fascinante (não só beleza)

Você pode não virar "imperatriz" mas pode transformar
completamente sua trajetória.

A pergunta é: você está disposto a CORTAR pontes
irrevogavelmente com o passado?
```

---

## ⚠️ Considerações Éticas

### Princípios Éticos do Módulo

```python
PRINCIPIOS_ETICOS = {
    "contextualizacao_historica": {
        "principio": "História ≠ Manual de Ações",
        "regra": "Adapte PRINCÍPIOS, não AÇÕES literais",
        "exemplo": [
            "❌ Não copie: 'Eliminar rivais fisicamente'",
            "✅ Adapte: 'Neutralizar bloqueadores através de performance superior'"
        ]
    },

    "avisos_obrigatorios": {
        "situacoes_requiring_warning": [
            "Estratégias envolvendo eliminação/violência",
            "Manipulação religiosa/ideológica",
            "Espionagem totalitária",
            "Relacionamentos puramente instrumentais"
        ],
        "template_aviso": """
        ⚠️ AVISO ÉTICO: Esta estratégia foi efetiva historicamente
        mas envolveu [MÉTODO QUESTIONÁVEL]. Em contexto moderno:

        • Adapte os PRINCÍPIOS (timing, análise de poder, coalizão)
        • NÃO copie os MÉTODOS (violência, coerção, manipulação)
        • Considere alternativas éticas que mantêm efetividade
        • Sucesso sustentável requer integridade
        """
    },

    "diferenciacao_poder_coercao": {
        "principio": "Poder ≠ Coerção",
        "definicoes": {
            "poder_legitimo": "Influência baseada em valor, competência, respeito",
            "coercao": "Força baseada em medo, violência, chantagem"
        },
        "orientacao": "Charlee promove poder legítimo, não coerção"
    },

    "reconhecimento_privilegio": {
        "principio": "Contexto histórico ≠ Contexto moderno",
        "fatores": [
            "Figuras históricas tinham poder absoluto (ditadoras)",
            "Ausência de checks & balances modernos",
            "Violência era ferramenta política aceitável",
            "Direitos humanos eram conceito inexistente"
        ],
        "conclusao": "Admire estratégia, não romanticize brutalidade"
    },

    "genero_como_foco": {
        "principio": "Por que foco em mulheres?",
        "justificativa": [
            "Mulheres tiveram que ser MAIS estratégicas (menos poder formal)",
            "Estratégias de 'outsider' aplicáveis a qualquer grupo marginalizado",
            "Diversidade de arquétipos: diplomata, guerreira, parceira, transformadora",
            "Lições sobre poder sem privilégio estrutural"
        ],
        "aplicabilidade": "Frameworks aplicáveis a qualquer pessoa enfrentando assimetria de poder"
    }
}
```

### Sistema de Filtros Éticos

```python
class EthicalFilter:
    """
    Filtro ético para respostas do módulo de poder feminino.
    """

    @staticmethod
    def apply_filter(response: str, estrategia: Dict) -> str:
        """
        Aplica filtros éticos antes de retornar resposta.
        """
        filtered_response = response

        # Detecção de estratégias problemáticas
        problematic_keywords = [
            "eliminar", "matar", "assassinar", "envenenar",
            "tortura", "execução", "golpe violento", "espionagem totalitária"
        ]

        if any(keyword in response.lower() for keyword in problematic_keywords):
            # Adiciona aviso ético
            warning = EthicalFilter._generate_warning(estrategia)
            filtered_response = f"{warning}\n\n{response}"

            # Adiciona alternativa ética
            ethical_alternative = EthicalFilter._generate_ethical_alternative(estrategia)
            filtered_response += f"\n\n{ethical_alternative}"

        return filtered_response

    @staticmethod
    def _generate_warning(estrategia: Dict) -> str:
        """Gera aviso ético contextualizado"""
        return f"""
        ⚠️ **AVISO ÉTICO IMPORTANTE**

        A estratégia histórica descrita envolve métodos que eram aceitos
        em {estrategia['epoca']} mas são **INACEITÁVEIS** hoje:

        • Violência física/psicológica
        • Violação de direitos humanos
        • Coerção e intimidação

        **O que você DEVE extrair:**
        ✓ Princípios de análise de poder
        ✓ Timing estratégico
        ✓ Construção de coalizões
        ✓ Controle de narrativa

        **O que você NÃO deve fazer:**
        ✗ Copiar métodos violentos
        ✗ Justificar coerção
        ✗ Ignorar ética moderna
        """

    @staticmethod
    def _generate_ethical_alternative(estrategia: Dict) -> str:
        """Gera alternativa ética para estratégia problemática"""
        alternatives = {
            "eliminacao_rivais": """
            **ALTERNATIVA ÉTICA:** Em vez de "eliminar" rivais:
            • Torne-os irrelevantes através de performance superior
            • Construa consenso que os isola naturalmente
            • Ofereça saída honrosa (realocação, promoção lateral)
            • Foque em construir seu valor (vs destruir deles)
            """,

            "espionagem": """
            **ALTERNATIVA ÉTICA:** Em vez de espionagem invasiva:
            • Crie cultura de feedback honesto e aberto
            • Sistemas de comunicação transparente
            • 1-on-1s genuínos (não interrogatórios)
            • Intelligence situacional via observação respeitosa
            """,

            "manipulacao_religiosa": """
            **ALTERNATIVA ÉTICA:** Em vez de manipular crenças:
            • Alinhe valores genuinamente
            • Comunique missão inspiradora honestamente
            • Respeite diversidade de crenças
            • Liderança por exemplo (não manipulação)
            """
        }

        # Identifica tipo de estratégia e retorna alternativa
        for tipo, alternativa in alternatives.items():
            if tipo in estrategia.get("categoria", ""):
                return alternativa

        return ""
```

---

## 🛣️ Roadmap

### Fase 1: MVP - Base de Conhecimento ✅ (Completo)
- [x] Documentação de 5 figuras históricas
- [x] Catalogação de 30+ estratégias
- [x] Frameworks de aplicação prática
- [x] Sistema de matching situação-figura

### Fase 2: Integração com Charlee (Em Desenvolvimento)
- [ ] Implementação da classe `PoderFemininoAgent`
- [ ] Integração com Strategic Advisor
- [ ] Integração com Core Agent (tools)
- [ ] Integração com Career Insights
- [ ] Testes de matching situacional

### Fase 3: Refinamento de UX
- [ ] Modo interativo: usuário escolhe figura
- [ ] Comparação lado-a-lado de estratégias
- [ ] Timeline visual de trajetórias
- [ ] Quiz: "Qual figura histórica você se parece?"

### Fase 4: Expansão de Conteúdo
- [ ] Adicionar figuras modernas (Indira Gandhi, Golda Meir, Angela Merkel)
- [ ] Adicionar figuras de outras culturas (Hatshepsut, Nzinga, Ching Shih)
- [ ] Estratégias de homens em posição de outsider (para comparação)
- [ ] Casos de fracasso detalhados (anti-patterns)

### Fase 5: Análise Avançada
- [ ] ML para melhor matching situação-estratégia
- [ ] Análise de padrões de trajetória do usuário
- [ ] Recomendações proativas baseadas em fase de carreira
- [ ] Integração com dados reais de carreira (LinkedIn, etc.)

### Fase 6: Community & Feedback
- [ ] Sistema de feedback em insights
- [ ] Comunidade de usuários compartilhando aplicações
- [ ] Votação em figuras/estratégias mais úteis
- [ ] Casos de uso submetidos por usuários

---

## 📚 Referências

### Livros Acadêmicos

**Cleópatra:**
- Schiff, Stacy. *Cleopatra: A Life*. Little, Brown and Company, 2010.
- Tyldesley, Joyce. *Cleopatra: Last Queen of Egypt*. Basic Books, 2008.
- Roller, Duane W. *Cleopatra: A Biography*. Oxford University Press, 2010.

**Elizabeth I:**
- Weir, Alison. *The Life of Elizabeth I*. Ballantine Books, 1998.
- Somerset, Anne. *Elizabeth I*. St. Martin's Press, 1991.
- Haigh, Christopher. *Elizabeth I*. Longman, 1988.

**Catarina II:**
- Massie, Robert K. *Catherine the Great: Portrait of a Woman*. Random House, 2011.
- Dixon, Simon. *Catherine the Great*. Ecco, 2009.
- Rounding, Virginia. *Catherine the Great: Love, Sex, and Power*. St. Martin's Press, 2006.

**Wu Zetian:**
- Woo, X. L. *Empress Wu the Great*. Algora Publishing, 2008.
- Rothschild, N. Harry. *Wu Zhao: China's Only Woman Emperor*. Pearson, 2008.
- Guisso, R. W. L. *Wu Tse-t'ien and the Politics of Legitimation*. Western Washington, 1978.

**Teodora:**
- Potter, David. *Theodora: Actress, Empress, Saint*. Oxford University Press, 2015.
- Bridge, Antony. *Theodora: Portrait in a Byzantine Landscape*. Academy Chicago Publishers, 1984.
- Garland, Lynda. *Byzantine Empresses: Women and Power in Byzantium*. Routledge, 1999.

### Fontes Primárias

- Plutarco. *Vidas Paralelas* (sobre Cleópatra via Marco Antônio)
- Procópio. *História das Guerras* & *História Secreta* (sobre Teodora)
- Camden, William. *The History of the Most Renowned Princess Elizabeth* (1615)
- Catarina II. *Memórias* (autobiografia)
- *Old Book of Tang* e *New Book of Tang* (sobre Wu Zetian)

### Recursos Online

- [Ancient History Encyclopedia](https://www.worldhistory.org/)
- [Smithsonian Magazine - History](https://www.smithsonianmag.com/history/)
- [JSTOR](https://www.jstor.org/) - Artigos acadêmicos
- [Britannica](https://www.britannica.com/) - Biografias verificadas

### Mídia e Documentários

**Filmes:**
- *Cleopatra* (1963) - Elizabeth Taylor
- *Elizabeth* (1998) + *Elizabeth: The Golden Age* (2007)
- *The Great* (2020-2023, série) - Catarina II (comédia histórica)

**Documentários:**
- *Cleopatra: Portrait of a Killer* (BBC, 2009)
- *Elizabeth I's Secret Agents* (BBC, 2013)
- *Catherine the Great* (PBS, 2005)

**Podcasts:**
- *The History of Rome* (episódios sobre Cleópatra)
- *Rex Factor* (episódios sobre Elizabeth I)
- *Emperors of Rome* (episódio sobre Teodora)

---

## 🔄 Manutenção e Atualizações

### Processo de Atualização

```python
class ModuleUpdateProcess:
    """
    Processo de manutenção do módulo de poder feminino.
    """

    @staticmethod
    def review_cycle():
        """
        Ciclo de revisão baseado em feedback de usuários.
        """
        return {
            "frequencia": "Trimestral",

            "metricas_rastreadas": [
                "Número de consultas por figura",
                "Taxa de satisfação por insight",
                "Estratégias mais/menos úteis",
                "Situações não-mapeadas (gaps)",
                "Requests de novas figuras/estratégias"
            ],

            "criterios_adicao_figura": {
                "relevancia_historica": "Figura reconhecida academicamente",
                "diversidade_arquetipo": "Adiciona arquétipo novo",
                "aplicabilidade_moderna": "Estratégias transferíveis",
                "qualidade_fontes": "Mínimo 3 fontes acadêmicas"
            },

            "criterios_remocao_conteudo": {
                "baixo_uso": "< 5% de consultas em 6 meses",
                "feedback_negativo": "> 60% de feedback negativo",
                "desatualizado": "Contexto mudou (raro em história)"
            },

            "atualizacoes_eticas": {
                "frequencia": "Contínua",
                "gatilhos": [
                    "Feedback de uso problemático",
                    "Novos standards éticos emergentes",
                    "Casos de má interpretação identificados"
                ]
            }
        }
```

### Sistema de Feedback

```python
from pydantic import BaseModel
from datetime import datetime

class ModuleFeedback(BaseModel):
    """Feedback de usuário sobre módulo"""
    user_id: int
    figura_consultada: str
    estrategia_aplicada: str
    timestamp: datetime

    rating: int = Field(..., ge=1, le=5)  # 1-5 stars

    utilidade: Literal["muito_util", "util", "neutro", "pouco_util", "inutl"]

    feedback_texto: Optional[str] = None

    contexto_aplicacao: Optional[str] = None  # Onde aplicou
    resultado: Optional[Literal["sucesso", "parcial", "fracasso"]] = None

    sugestao_melhoria: Optional[str] = None

# Endpoint para coletar feedback
@router.post("/api/v1/poder-feminino/feedback")
def submit_feedback(
    feedback: ModuleFeedback,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Coleta feedback de usuário sobre módulo"""
    db.add(feedback)
    db.commit()

    # Trigger review se feedback muito negativo
    if feedback.rating <= 2:
        notify_maintainers(feedback)

    return {"status": "success", "message": "Feedback registrado. Obrigado!"}
```

---

## 💡 Notas Finais

### Filosofia do Módulo

Este módulo não tem como objetivo:
- ❌ Glorificar violência ou métodos antiéticos
- ❌ Promover maquiavelismo destrutivo
- ❌ Romantizar ditaduras ou autocracia
- ❌ Ignorar privilégios e contextos dessas figuras

Este módulo TEM como objetivo:
- ✅ Extrair princípios universais de estratégia
- ✅ Inspirar através de resiliência histórica
- ✅ Mostrar que assimetria de poder pode ser superada
- ✅ Ensinar análise sofisticada de dinâmicas de poder
- ✅ Contextualizar ética moderna vs pragmatismo histórico

### Tom de Voz do Charlee

Ao usar este módulo, Charlee deve:
1. **Ser educador, não propagandista**: Apresente história honestamente
2. **Ser realista, não cínico**: Poder tem custos, mas pode ser usado para bem
3. **Ser provocativo, não prescritivista**: Faça usuário PENSAR (não diga o que fazer)
4. **Ser respeitoso, não romântico**: Admire estratégia, não brutalidade
5. **Ser aplicável, não acadêmico**: Traduza história em ação moderna

### Mensagem Central

> "Poder não é algo que você tem ou não tem.
> Poder é algo que você **constrói** através de:
> • Conhecimento
> • Alianças
> • Timing
> • Narrativa
> • Coragem calculada
>
> Estas 5 mulheres provaram isso em contextos onde
> TUDO estava contra elas. Se elas conseguiram então...
> O que você pode fazer com as ferramentas de hoje?"

---

**Versão**: 1.0
**Data**: 2025-11-18
**Mantenedor**: Sistema Charlee - Módulo de Poder Feminino Histórico
**Contato**: charlee-team@charlee.ai (futuro)
**Licença**: Proprietário - Uso exclusivo Charlee

---

**Desenvolvido com ❤️ por Samara Cassie**

*"Não estudamos história para copiar o passado.
Estudamos para entender princípios atemporais de poder humano."*
