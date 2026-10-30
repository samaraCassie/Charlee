# 👑 Charlee Feminine Power - Módulo de Insights Históricos de Poder Feminino

**Versão:** V5.0 (Planejado)
**Status:** 🔴 Não Implementado
**Prioridade:** 🔥 Alta (Diferencial Estratégico)
**Dependências:** Diplomat (V4.0), Listener (V5.0), Wellness (V2.0)

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquétipos Históricos](#2-arquétipos-históricos)
3. [Base de Conhecimento](#3-base-de-conhecimento)
4. [Sistema de Matching](#4-sistema-de-matching)
5. [Princípios Universais](#5-princípios-universais)
6. [Framework de Aplicação](#6-framework-de-aplicação)
7. [Integração com Outros Módulos](#7-integração-com-outros-módulos)
8. [Schemas de Banco de Dados](#8-schemas-de-banco-de-dados)
9. [API Endpoints](#9-api-endpoints)
10. [Exemplos de Conversação](#10-exemplos-de-conversação)
11. [Roadmap de Implementação](#11-roadmap-de-implementação)
12. [Conclusão](#12-conclusão)

---

## 1. Visão Geral

### 1.1 O que é o Charlee Feminine Power?

O **Charlee Feminine Power** é um módulo de conhecimento histórico que integra estratégias comprovadas de **cinco mulheres icônicas** que redefiniram poder em seus contextos:

1. **Cleópatra VII** (69-30 a.C.) - Diplomacia e alianças estratégicas
2. **Elizabeth I** (1533-1603) - Ambiguidade estratégica e frames
3. **Catarina II** (1729-1796) - Tomada de poder e autoconhecimento
4. **Wu Zetian** (624-705) - Escalada hierárquica e meritocracia
5. **Teodora** (497-548) - Transformação radical e parceria

### 1.2 Por que este módulo é crítico?

**Problema:** Mulheres em posições de liderança frequentemente enfrentam:
- Estruturas de poder historicamente masculinas
- Duplos padrões de comportamento
- Falta de modelos de referência
- Pressão para "escolher" entre feminilidade e autoridade

**Solução:** Este módulo oferece:
- ✅ **Estratégias testadas por 2000+ anos de história**
- ✅ **Insights acionáveis** (não apenas inspiração abstrata)
- ✅ **Contexto moderno** (adapta princípios, não copia ações)
- ✅ **Ética atualizada** (reconhece que contextos mudaram)

### 1.3 Diferencial do Charlee

**Não é:**
- ❌ Curso de história feminina
- ❌ Inspiração vaga tipo "seja você mesma"
- ❌ Glorificação de crueldade histórica

**É:**
- ✅ Sistema de matching situação → estratégia histórica
- ✅ Perguntas reflexivas que aprofundam pensamento
- ✅ Frameworks práticos baseados em casos reais
- ✅ Adaptação ética para contexto moderno

---

## 2. Arquétipos Históricos

### 2.1 Os Cinco Arquétipos

```python
# backend/modules/feminine_power/archetypes.py

from enum import Enum
from typing import List, Dict

class HistoricalArchetype(Enum):
    """Cinco arquétipos de poder feminino"""

    CLEOPATRA = "cleopatra"       # A Diplomata
    ELIZABETH = "elizabeth"        # A Estrategista de Frames
    CATHERINE = "catherine"        # A Tomadora de Poder
    WU_ZETIAN = "wu_zetian"       # A Escaladora Metódica
    THEODORA = "theodora"          # A Transformadora

class ArchetypeProfile:
    """Perfil completo de um arquétipo histórico"""

    def __init__(self, archetype: HistoricalArchetype):
        self.archetype = archetype
        self.data = self._load_archetype_data()

    def _load_archetype_data(self) -> Dict:
        """Carrega dados do arquétipo"""

        profiles = {
            HistoricalArchetype.CLEOPATRA: {
                "nome": "Cleópatra VII do Egito",
                "periodo": "69-30 a.C.",
                "contexto": "Última governante ptolemaica, Reino ameaçado por Roma",
                "conquista": "Manteve Egito independente 20 anos via diplomacia",

                "estrategias_chave": [
                    "Educação multilíngue como vantagem",
                    "Alianças românticas estratégicas",
                    "Adaptação cultural pragmática",
                    "Diplomacia sobre força bruta",
                    "Construção de imagem mitológica"
                ],

                "quando_aplicar": [
                    "Negociação com adversários mais poderosos",
                    "Contexto multicultural/multinacional",
                    "Necessidade de alianças estratégicas",
                    "Desvantagem em recursos/força",
                    "Importância de soft power"
                ],

                "principios_core": {
                    "educacao": "Conhecimento é primeira camada de poder",
                    "aliancas": "Alianças > Confronto quando inferior em força",
                    "adaptabilidade": "Camaleão cultural = fluência estratégica",
                    "timing": "Controle narrativo no primeiro contato",
                    "simbolismo": "Apresentação importa tanto quanto substância"
                },

                "erros_evitar": [
                    "Subestimar 'jogador silencioso'",
                    "Misturar emoção com estratégia em momentos críticos"
                ]
            },

            HistoricalArchetype.ELIZABETH: {
                "nome": "Elizabeth I da Inglaterra",
                "periodo": "1533-1603",
                "contexto": "Era Elisabetana, legitimidade questionada, divisão religiosa",
                "conquista": "45 anos de reinado estável, vitória sobre Armada",

                "estrategias_chave": [
                    "Jogo de frames (casamento como optionalidade)",
                    "Diplomacia da ambiguidade",
                    "Imagem como instrumento de estado",
                    "Oratória transformativa (Tilbury)",
                    "Patronato das artes como soft power"
                ],

                "quando_aplicar": [
                    "Múltiplas ofertas/opções disponíveis",
                    "Pressão para decidir rapidamente",
                    "Contexto polarizado (precisa agradar múltiplos lados)",
                    "Necessidade de manter independência",
                    "Situação requer ambiguidade estratégica"
                ],

                "principios_core": {
                    "optionalidade": "POSSIBILIDADE > COMPROMISSO = Poder",
                    "ambiguidade": "Clareza nem sempre é virtude",
                    "imagem": "Aparência = ferramenta política consciente",
                    "oratoria": "Frame fraqueza aparente como força interior",
                    "cultura": "Invista no que sobrevive além de você"
                },

                "erros_evitar": [
                    "Procrastinação indefinida em decisões críticas",
                    "Adiamento de questões sucessórias"
                ]
            },

            HistoricalArchetype.CATHERINE: {
                "nome": "Catarina II da Rússia",
                "periodo": "1729-1796",
                "contexto": "Estrangeira (alemã) em corte russa, marido incompetente",
                "conquista": "34 anos de reinado, expansão de 517.000 km²",

                "estrategias_chave": [
                    "Autoconhecimento como base estratégica",
                    "Golpe de estado como empreendimento",
                    "Mecenato e iluminismo para legitimação",
                    "Reforma pragmática (não idealista)",
                    "Gestão de amantes como política de estado"
                ],

                "quando_aplicar": [
                    "Usuário é 'estrangeiro' no sistema",
                    "Estrutura atual é hostil/incompetente",
                    "Oportunidade de mudança revolucionária",
                    "Necessidade de legitimação cultural",
                    "Pragmatismo > Idealismo"
                ],

                "principios_core": {
                    "autoconhecimento": "Mapeie forças/fraquezas objetivamente",
                    "golpe": "Preparação meticulosa + timing + coalizão",
                    "cultura": "Patrocine artes para validar poder",
                    "pragmatismo": "Reforme o suficiente, não demais",
                    "quebra_normas": "Desafie regras APENAS com poder consolidado"
                },

                "erros_evitar": [
                    "Pragmatismo excessivo deixa problemas para sucessores",
                    "Sucessão mal gerida destrói legado"
                ]
            },

            HistoricalArchetype.WU_ZETIAN: {
                "nome": "Wu Zetian da China",
                "periodo": "624-705",
                "contexto": "Sistema confucionista anti-mulheres, harém competitivo",
                "conquista": "Única mulher a reinar como IMPERADOR na China",

                "estrategias_chave": [
                    "Escalada metódica através de instituições",
                    "Instrumentalização da religião (Budismo)",
                    "Meritocracia como arma contra aristocracia",
                    "Rede de espionagem e controle",
                    "Poder da simbologia linguística (caractere 曌)"
                ],

                "quando_aplicar": [
                    "Usuário em posição subordinada",
                    "Sistema hierárquico rígido",
                    "Necessidade de subir de baixo",
                    "Ideologia dominante bloqueia usuário",
                    "Ambiente tradicional/confucionista"
                ],

                "principios_core": {
                    "escalada": "Aprenda cada degrau antes de subir",
                    "ideologia": "Se sistema bloqueia, crie novo sistema",
                    "meritocracia": "Promova talento leal a você",
                    "informacao": "Sistemas de inteligência = sobrevivência",
                    "simbolismo": "Controle linguagem e símbolos"
                },

                "erros_evitar": [
                    "Sucesso levando a autoindulgência",
                    "Tratamento brutal de sucessores"
                ]
            },

            HistoricalArchetype.THEODORA: {
                "nome": "Teodora de Bizâncio",
                "periodo": "497-548",
                "contexto": "Origem prostituta, sociedade misógina bizantina",
                "conquista": "Co-governante de fato com Justiniano I, reformas legais",

                "estrategias_chave": [
                    "Transformação radical de identidade",
                    "Parceria igualitária em estrutura hierárquica",
                    "Reformas sociais baseadas em experiência vivida",
                    "Influência através de redes informais",
                    "Coragem em crise (Revolta Nika)"
                ],

                "quando_aplicar": [
                    "Avaliação de potencial parceiro",
                    "Passado doloroso/estigmatizado a superar",
                    "Necessidade de reformas sociais",
                    "Transformação radical de identidade",
                    "Construção de rede informal"
                ],

                "principios_core": {
                    "transformacao": "Passado não define futuro com mudança genuína",
                    "parceria": "Encontre quem respeita intelectualmente",
                    "missao": "Use feridas como combustível para mudança",
                    "rede": "Influência através de lealdades pessoais",
                    "coragem": "Momento de maior risco = maior impacto"
                },

                "erros_evitar": [
                    "Transformação sem compromisso total",
                    "Parceria com quem não respeita intelectualmente"
                ]
            }
        }

        return profiles[self.archetype]
```

---

## 3. Base de Conhecimento

### 3.1 Estrutura de Dados Históricos

```python
# backend/modules/feminine_power/knowledge_base.py

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class HistoricalStrategy:
    """Uma estratégia específica de uma figura histórica"""

    strategy_id: str
    archetype: HistoricalArchetype
    strategy_name: str
    context: str                    # Quando foi usada
    execution: str                  # Como foi executada
    result: str                     # O que aconteceu
    modern_application: str         # Como aplicar hoje
    ethical_considerations: str     # Cuidados éticos
    examples: List[str]            # Casos práticos

class KnowledgeBase:
    """Base de conhecimento completa sobre estratégias históricas"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.strategies = self._load_all_strategies()

    def _load_all_strategies(self) -> Dict[str, HistoricalStrategy]:
        """Carrega todas as estratégias"""

        strategies = {}

        # CLEÓPATRA - Alianças Românticas Estratégicas
        strategies["cleopatra_romantic_alliances"] = HistoricalStrategy(
            strategy_id="cleopatra_romantic_alliances",
            archetype=HistoricalArchetype.CLEOPATRA,
            strategy_name="Alianças Românticas Estratégicas",
            context=(
                "Cleópatra tinha 21 anos, estava exilada, César controlava Roma. "
                "Egito era militarmente inferior mas economicamente rico."
            ),
            execution=(
                "1. Entrada dramática (escondida em tapete) - controle narrativo\n"
                "2. Relacionamento com César (48-44 a.C.) = apoio militar\n"
                "3. Filho (Cesárion) = possível herdeiro de dois impérios\n"
                "4. Após morte de César: Marco Antônio (41-30 a.C.)\n"
                "5. Encontro espetacular no rio Cydnus - teatralidade diplomática"
            ),
            result=(
                "✅ Legitimação como rainha\n"
                "✅ Apoio militar romano\n"
                "✅ Expansão territorial egípcia\n"
                "✅ Egito independente por 20 anos\n"
                "❌ Eventual derrota para Otaviano"
            ),
            modern_application=(
                "Princípios de Alianças Estratégicas:\n"
                "• Avaliação de necessidade: Qual problema esta aliança resolve?\n"
                "• Análise de poder: O que cada parte tem que a outra precisa?\n"
                "• Timing: Este é o momento de maior alavancagem?\n"
                "• Simbolismo: Como apresento de forma memorável?\n"
                "• Garantias: Quais são os 'reféns' mútuos (projetos conjuntos)?\n"
                "• Saída estratégica: Como preservo dignidade se terminar?"
            ),
            ethical_considerations=(
                "⚠️ Não romantize: Cleópatra usou relacionamentos como ferramenta política\n"
                "⚠️ Contexto moderno: Alianças devem ser mutuamente benéficas e transparentes\n"
                "✅ Adapte: Foque em 'alianças estratégicas', não necessariamente românticas\n"
                "✅ Ética: Parcerias devem ser honestas sobre motivações"
            ),
            examples=[
                "Negócio: Co-founder com complementaridade de skills (você=tech, ele=sales)",
                "Carreira: Mentoria com executivo influente (você=energia, ele=network)",
                "Pessoal: Casamento como parceria econômica/estratégica (além de amor)"
            ]
        )

        # ELIZABETH - Jogo de Frames do Casamento
        strategies["elizabeth_optionality"] = HistoricalStrategy(
            strategy_id="elizabeth_optionality",
            archetype=HistoricalArchetype.ELIZABETH,
            strategy_name="Optionalidade como Poder (Jogo de Frames)",
            context=(
                "Elizabeth recusou 20+ propostas de casamento de príncipes europeus. "
                "Casamento = perda de poder (submissão ao marido, alinhamento com país dele)."
            ),
            execution=(
                "1. Manteve TODOS na esperança de possível 'sim'\n"
                "2. Usou pretendentes como peças diplomáticas\n"
                "3. Nunca entregou o 'prêmio'\n"
                "4. Frase icônica: 'Estou casada com a Inglaterra'\n"
                "5. 45 anos de independência total"
            ),
            result=(
                "✅ Independência total de decisão\n"
                "✅ Múltiplos países cortejando favores\n"
                "✅ Imprevisibilidade = respeito\n"
                "✅ Controle absoluto da narrativa\n"
                "❌ Sem herdeiro direto (sucessão problemática)"
            ),
            modern_application=(
                "Princípio: OPTIONALIDADE É PODER\n\n"
                "Quando aplicar:\n"
                "• Múltiplas ofertas de emprego/parceria\n"
                "• Pressão para decisão rápida\n"
                "• Você tem leverage atual\n\n"
                "Como aplicar:\n"
                "1. 'Estou muito interessado, mas preciso garantir fit perfeito'\n"
                "2. 'Podem me dar mais 2 semanas para decisão tão importante?'\n"
                "3. Use oferta A para melhorar B, B para melhorar C\n"
                "4. Mantenha todas as portas abertas até VOCÊ decidir\n\n"
                "Pergunte: Quem se beneficia da minha decisão RÁPIDA?"
            ),
            ethical_considerations=(
                "⚠️ Não abuse: Eventualmente precisa tomar decisão\n"
                "⚠️ Respeite tempo alheio: Não enrole indefinidamente\n"
                "✅ Seja honesto: 'Estou avaliando múltiplas opções'\n"
                "✅ Comunique timeline: 'Decidirei até [data]'"
            ),
            examples=[
                "3 ofertas de emprego: Mantém todas em 'talvez' por 2 semanas",
                "Investidores: Não fecha com primeiro que oferece, usa para melhorar termos",
                "Relacionamento: Não define exclusividade até ter certeza"
            ]
        )

        # CATARINA - Golpe de Estado
        strategies["catherine_coup"] = HistoricalStrategy(
            strategy_id="catherine_coup",
            archetype=HistoricalArchetype.CATHERINE,
            strategy_name="Golpe de Estado como Empreendimento",
            context=(
                "1762: Pedro III (marido de Catarina) tornou-se czar. "
                "Decisões desastrosas: aliança com inimigos, hostilização da Igreja."
            ),
            execution=(
                "PREPARAÇÃO (6 meses):\n"
                "1. Identificou insatisfação: Guarda, nobreza, clero\n"
                "2. Posicionou-se como alternativa legitimada (mãe do herdeiro)\n"
                "3. Aliados-chave: Irmãos Orlov, Panin, Dashkov\n\n"
                "EXECUÇÃO (Julho 1762):\n"
                "4. Pedro ausente em campanha\n"
                "5. Guarda proclamou Catarina imperatriz\n"
                "6. Pedro abdicou sem resistência\n"
                "7. Pedro eliminado 'por conta própria'"
            ),
            result=(
                "✅ 34 anos de reinado transformador\n"
                "✅ Expansão de 517.000 km²\n"
                "✅ Modernização cultural\n"
                "❌ Legitimidade sempre questionada\n"
                "❌ Necessidade de controle constante"
            ),
            modern_application=(
                "Princípios de Mudança Revolucionária:\n\n"
                "PREPARAÇÃO:\n"
                "• Identifique insatisfação generalizada\n"
                "• Posicione-se como solução óbvia\n"
                "• Construa coalizão (poder militar, econômico, legitimidade)\n"
                "• Espere erro fatal do oponente\n\n"
                "EXECUÇÃO:\n"
                "• Aja rápido quando janela abrir\n"
                "• Controle narrativa imediatamente\n"
                "• Neutralize oposição de forma irreversível\n"
                "• Ofereça estabilidade imediata\n\n"
                "PERGUNTAS:\n"
                "1. Quem está insatisfeito mas sem alternativa?\n"
                "2. Você tem legitimidade (track record)?\n"
                "3. Quem são seus 'executores práticos'?\n"
                "4. Qual erro do 'regime atual' você espera?\n"
                "5. Você está pronto para assumir IMEDIATAMENTE?"
            ),
            ethical_considerations=(
                "⚠️ CRÍTICO: Catarina usou métodos violentos e ditatoriais\n"
                "⚠️ Não replique: Assassinato/violência são inaceitáveis\n"
                "✅ Adapte: Use princípios para mudança ÉTICA:\n"
                "   - Mudança de liderança via processos legítimos\n"
                "   - 'Golpe' corporativo = mudança de CEO via board\n"
                "   - Revolução = startup disruptiva, não destruição\n"
                "⚠️ Sempre: Dentro da lei e ética moderna"
            ),
            examples=[
                "Startup: Identificar problema de mercado, construir solução, esperar incumbente falhar",
                "Corporativo: Documentar falhas de gestão, construir coalizão de board, propor mudança",
                "Político: Organizar movimento, construir consenso, vencer eleição democraticamente"
            ]
        )

        # WU ZETIAN - Escalada Metódica
        strategies["wu_methodical_climb"] = HistoricalStrategy(
            strategy_id="wu_methodical_climb",
            archetype=HistoricalArchetype.WU_ZETIAN,
            strategy_name="Escalada Metódica Através de Instituições",
            context=(
                "Wu Zetian: de lavadeira (concubina 5ª categoria) a IMPERADOR. "
                "Sistema confucionista explicitamente anti-mulheres no poder."
            ),
            execution=(
                "TRAJETÓRIA (50 anos):\n"
                "638 (14 anos): Concubina baixa → Quebrou protocolo falando com imperador\n"
                "649: Secretária → Aprendeu política de dentro\n"
                "655: Imperatriz → Eliminou rivais (Imperatriz Wang, Concubina Xiao)\n"
                "660-683: Co-governante → Gaozong doente, Wu decide\n"
                "684-690: Regente → Controlou filhos-imperadores\n"
                "690: IMPERADOR → Criou próprio caractere (曌), Dinastia Zhou"
            ),
            result=(
                "✅ 15 anos de reinado direto + 23 como regente\n"
                "✅ Única mulher a reinar como IMPERADOR na China\n"
                "✅ Reformas meritocráticas duradouras\n"
                "❌ Métodos brutais\n"
                "❌ Legado controverso"
            ),
            modern_application=(
                "Framework de Escalada Institucional:\n\n"
                "FASE 1 - ENTRADA:\n"
                "• Objetivo: Entrar no sistema (mesmo em posição baixa)\n"
                "• Estratégia: Seja notada por quebrar protocolo ESTRATEGICAMENTE\n\n"
                "FASE 2 - APRENDIZADO:\n"
                "• Objetivo: Dominar mecânica interna\n"
                "• Estratégia: Aceite posição de 'assistente' (acesso a decisões)\n\n"
                "FASE 3 - ELIMINAÇÃO:\n"
                "• Objetivo: Remover bloqueadores\n"
                "• Estratégia: Identifique rivais e elimine ANTES de serem ameaça\n\n"
                "FASE 4 - CONTROLE PROXY:\n"
                "• Objetivo: Poder de fato sem exposição\n"
                "• Estratégia: Governe através de figurehead\n\n"
                "FASE 5 - CONSOLIDAÇÃO:\n"
                "• Objetivo: Poder formal\n"
                "• Estratégia: Quando controla infraestrutura, ENTÃO pega título"
            ),
            ethical_considerations=(
                "⚠️ CRÍTICO: Wu foi extremamente cruel (assassinatos, tortura)\n"
                "⚠️ Não replique: Violência é inaceitável\n"
                "✅ Adapte a ética moderna:\n"
                "   - 'Eliminação' = competir por mérito, não destruir\n"
                "   - 'Controle' = influência legítima, não manipulação\n"
                "   - 'Escalada' = promoções meritocráticas\n"
                "⚠️ Wu nos ensina PRINCÍPIOS, não AÇÕES"
            ),
            examples=[
                "Tech: Intern → Junior → Senior → Tech Lead → VP Engineering → CTO",
                "Academia: PhD Student → Postdoc → Assistant Prof → Associate → Full Professor → Dean",
                "Corporativo: Analyst → Manager → Director → VP → SVP → C-Suite"
            ]
        )

        # TEODORA - Transformação Radical
        strategies["theodora_transformation"] = HistoricalStrategy(
            strategy_id="theodora_transformation",
            archetype=HistoricalArchetype.THEODORA,
            strategy_name="Transformação Radical de Identidade",
            context=(
                "Teodora: prostituta em Constantinopla (profissão estigmatizada). "
                "Sociedade bizantina extremamente misógina e hierárquica."
            ),
            execution=(
                "TRAJETÓRIA:\n"
                "~512 (15 anos): Atriz/prostituta\n"
                "~520: Viaja pelo Oriente, converte-se ao Cristianismo\n"
                "522 (25 anos): Retorna como 'fiandeira' (trabalho honesto)\n"
                "523-525: Relacionamento com Justiniano\n"
                "   → Lei MUDADA para permitir casamento\n"
                "525: Casamento → Elevada a Patrícia\n"
                "527: Imperatriz (Justiniano assume trono)\n\n"
                "ESTRATÉGIAS:\n"
                "1. Mudança de contexto físico (viagem)\n"
                "2. Reframe religioso ('pecadora arrependida')\n"
                "3. Comportamento consistente (nunca voltou à vida anterior)\n"
                "4. Aliado validador (Justiniano mudou LEI por ela)\n"
                "5. Missão redentora (fechou bordéis, criou Convento Metanoia)"
            ),
            result=(
                "✅ De prostituta a co-governante\n"
                "✅ Reformas legais pioneiras (direitos femininos)\n"
                "✅ Parceria igualitária com Justiniano\n"
                "✅ Legado duradouro (Corpus Juris Civilis)\n"
                "❌ Sempre criticada por origem"
            ),
            modern_application=(
                "Framework de Transformação Radical:\n\n"
                "PASSO 1 - RECONHECIMENTO:\n"
                "• Admita honestamente onde você está\n"
                "• Qual rótulo/situação você quer mudar?\n\n"
                "PASSO 2 - DECISÃO DEFINITIVA:\n"
                "• Faça escolha IRREVERSÍVEL de mudar\n"
                "• Você está disposto a CORTAR ponte com passado?\n\n"
                "PASSO 3 - MUDANÇA DE CONTEXTO:\n"
                "• Mude ambiente físico/social\n"
                "• Você pode mudar de cidade/empresa/círculo?\n\n"
                "PASSO 4 - NOVO SIMBOLISMO:\n"
                "• Adote símbolos da nova identidade\n"
                "• Quais comportamentos comunicam mudança?\n\n"
                "PASSO 5 - ALIADO VALIDADOR:\n"
                "• Encontre quem valida publicamente\n"
                "• Quem, ao te aceitar, faz outros aceitarem?\n\n"
                "PASSO 6 - CONSISTÊNCIA:\n"
                "• NUNCA volte ao comportamento antigo\n"
                "• 100% comprometido ou 'tentando'?\n\n"
                "PASSO 7 - LEGADO REDENTOR:\n"
                "• Use passado doloroso para ajudar outros\n"
                "• Como seu passado vira sua missão?"
            ),
            ethical_considerations=(
                "✅ POSITIVO: Transformação genuína é possível\n"
                "✅ Passado não define futuro com mudança real\n"
                "✅ Use dor como combustível para ajudar outros\n"
                "⚠️ Requer: Compromisso total, não 'tentativa'\n"
                "⚠️ Não romantize: Foi extremamente difícil para Teodora"
            ),
            examples=[
                "Ex-presidiário → Advogado de direitos humanos (via educação + persistência)",
                "Dropout → CEO (via startup + validação de investidores)",
                "Bancário → Professor (via mestrado + nova rede social)"
            ]
        )

        return strategies

    def get_strategy(self, strategy_id: str) -> HistoricalStrategy:
        """Retorna estratégia específica"""
        return self.strategies.get(strategy_id)

    def get_strategies_by_archetype(self, archetype: HistoricalArchetype) -> List[HistoricalStrategy]:
        """Retorna todas as estratégias de um arquétipo"""
        return [s for s in self.strategies.values() if s.archetype == archetype]
```

---

## 4. Sistema de Matching

### 4.1 Algoritmo de Matching Situação → Estratégia

```python
# backend/modules/feminine_power/matcher.py

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass

@dataclass
class UserSituation:
    """Situação do usuário para matching"""

    description: str
    context: Dict[str, Any]
    keywords: List[str]
    urgency: str  # "high" | "medium" | "low"
    power_dynamics: str  # "inferior" | "equal" | "superior"

@dataclass
class StrategyMatch:
    """Match entre situação e estratégia"""

    strategy: HistoricalStrategy
    relevance_score: float  # 0.0 - 1.0
    reasoning: str
    adaptation_notes: str

class HistoricalStrategyMatcher:
    """Sistema de matching situação → estratégia histórica"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    async def find_best_strategies(
        self,
        situation: UserSituation,
        top_n: int = 3
    ) -> List[StrategyMatch]:
        """
        Encontra as melhores estratégias históricas para situação
        """

        all_matches = []

        for strategy in self.kb.strategies.values():
            score = self._calculate_relevance(situation, strategy)

            if score > 0.3:  # threshold mínimo
                match = StrategyMatch(
                    strategy=strategy,
                    relevance_score=score,
                    reasoning=self._generate_reasoning(situation, strategy, score),
                    adaptation_notes=self._generate_adaptation_notes(situation, strategy)
                )
                all_matches.append(match)

        # Ordenar por relevância
        all_matches.sort(key=lambda m: m.relevance_score, reverse=True)

        return all_matches[:top_n]

    def _calculate_relevance(
        self,
        situation: UserSituation,
        strategy: HistoricalStrategy
    ) -> float:
        """
        Calcula score de relevância (0.0 - 1.0)
        """

        score = 0.0

        # 1. Keyword matching (0.0 - 0.3)
        situation_keywords_lower = [kw.lower() for kw in situation.keywords]
        strategy_context_lower = strategy.context.lower()

        keyword_matches = sum(
            1 for kw in situation_keywords_lower
            if kw in strategy_context_lower
        )
        score += min(0.3, keyword_matches * 0.1)

        # 2. Power dynamics matching (0.0 - 0.3)
        power_matches = {
            "inferior": ["cleopatra", "wu_zetian", "theodora"],
            "equal": ["elizabeth", "catherine"],
            "superior": ["elizabeth", "catherine", "wu_zetian"]
        }

        if strategy.archetype.value in power_matches.get(situation.power_dynamics, []):
            score += 0.3

        # 3. Context similarity (0.0 - 0.4)
        context_indicators = {
            "negotiation": 0.4 if "cleopatra" in strategy.strategy_id else 0.0,
            "optionality": 0.4 if "elizabeth" in strategy.strategy_id else 0.0,
            "transformation": 0.4 if "theodora" in strategy.strategy_id else 0.0,
            "climb": 0.4 if "wu" in strategy.strategy_id else 0.0,
            "takeover": 0.4 if "catherine" in strategy.strategy_id else 0.0
        }

        for indicator, indicator_score in context_indicators.items():
            if indicator in situation.description.lower():
                score += indicator_score
                break

        return min(1.0, score)

    def _generate_reasoning(
        self,
        situation: UserSituation,
        strategy: HistoricalStrategy,
        score: float
    ) -> str:
        """
        Gera explicação do por quê essa estratégia é relevante
        """

        archetype_name = strategy.archetype.value.replace("_", " ").title()

        reasoning = f"{archetype_name} enfrentou situação similar:\n\n"
        reasoning += f"**Contexto Histórico:**\n{strategy.context}\n\n"
        reasoning += f"**Similaridade com sua situação:**\n"

        # Identificar pontos de conexão
        if "negotiation" in situation.description.lower() and "cleopatra" in strategy.strategy_id:
            reasoning += "• Você está negociando com parte mais poderosa (como Cleópatra vs Roma)\n"

        if "options" in situation.description.lower() and "elizabeth" in strategy.strategy_id:
            reasoning += "• Você tem múltiplas opções (como Elizabeth com pretendentes)\n"

        if "transform" in situation.description.lower() and "theodora" in strategy.strategy_id:
            reasoning += "• Você busca transformação radical (como Teodora de prostituta a imperatriz)\n"

        reasoning += f"\n**Relevância:** {score*100:.0f}%"

        return reasoning

    def _generate_adaptation_notes(
        self,
        situation: UserSituation,
        strategy: HistoricalStrategy
    ) -> str:
        """
        Gera notas sobre como adaptar estratégia para contexto moderno
        """

        notes = "**Como adaptar para seu contexto:**\n\n"

        # Considerações éticas sempre primeiro
        notes += f"⚠️ **Ética:** {strategy.ethical_considerations}\n\n"

        # Adaptação prática
        notes += "**Passos práticos:**\n"

        # Extrair primeiros 3 pontos da aplicação moderna
        application_points = strategy.modern_application.split("\n")[:5]
        for point in application_points:
            if point.strip():
                notes += f"• {point.strip()}\n"

        return notes
```

---

## 5. Princípios Universais

### 5.1 Os 6 Princípios Atemporais

```python
# backend/modules/feminine_power/universal_principles.py

from enum import Enum

class UniversalPrinciple(Enum):
    """Princípios universais extraídos das 5 figuras"""

    EDUCATION_AS_FOUNDATION = "education"
    STRATEGIC_ALLIANCES = "alliances"
    PERFECT_TIMING = "timing"
    NARRATIVE_CONTROL = "narrative"
    PRAGMATISM_OVER_IDEALISM = "pragmatism"
    COURAGE_IN_CRISIS = "courage"

class UniversalPrinciplesSystem:
    """Sistema de princípios universais"""

    @staticmethod
    def get_principle_details(principle: UniversalPrinciple) -> Dict:
        """Retorna detalhes de um princípio universal"""

        principles = {
            UniversalPrinciple.EDUCATION_AS_FOUNDATION: {
                "nome": "Educação como Base de Poder",
                "descricao": (
                    "Todas as 5 figuras investiram pesadamente em aprender: "
                    "línguas, política, cultura, artes."
                ),
                "exemplos_historicos": [
                    "Cleópatra: 9 línguas, única ptolemaica a falar egípcio",
                    "Elizabeth: Educação formal em literatura, filosofia, oratória",
                    "Catarina: Aprendeu russo fluentemente (Pedro nunca aprendeu bem)",
                    "Wu Zetian: Secretária imperial = acesso a documentos/decisões",
                    "Teodora: Aprendeu política através de relacionamento com Justiniano"
                ],
                "pergunta_charlee": "Qual conhecimento te daria vantagem assimétrica?",
                "aplicacao_moderna": [
                    "Aprenda língua dos seus 'adversários' (literal ou figurativa)",
                    "Domine técnicas que 90% não dominam",
                    "Entenda profundamente o 'sistema' antes de tentar mudá-lo",
                    "Invista em educação contínua (mestrado, cursos, mentorias)"
                ]
            },

            UniversalPrinciple.STRATEGIC_ALLIANCES: {
                "nome": "Alianças Estratégicas",
                "descricao": (
                    "Todas construíram redes de poder e usaram alianças "
                    "para multiplicar força."
                ),
                "exemplos_historicos": [
                    "Cleópatra: César + Marco Antônio = apoio militar romano",
                    "Elizabeth: Manteve 20 pretendentes = leverage diplomático",
                    "Catarina: Irmãos Orlov + Panin = golpe bem-sucedido",
                    "Wu Zetian: Classe mercantil + budistas = nova base de poder",
                    "Teodora: Justiniano + rede de eunucos/bispos = influência"
                ],
                "pergunta_charlee": "Quem, ao apoiar você, multiplica seu poder?",
                "aplicacao_moderna": [
                    "Identifique 'multiplicadores de força' (investidores, mentores, sócios)",
                    "Construa alianças ANTES de precisar delas",
                    "Mantenha rede ativa (não contate só quando precisa)",
                    "Ofereça valor ANTES de pedir (reciprocidade)"
                ]
            },

            UniversalPrinciple.PERFECT_TIMING: {
                "nome": "Timing Perfeito",
                "descricao": (
                    "Todas souberam QUANDO agir vs QUANDO esperar. "
                    "Mesmo decisão certa no momento errado = falha."
                ),
                "exemplos_historicos": [
                    "Cleópatra: Entrada dramática com César no momento de vulnerabilidade dele",
                    "Elizabeth: Manteve pretendentes em suspense 45 anos (nunca fechou cedo)",
                    "Catarina: Golpe quando Pedro estava ausente + impopular",
                    "Wu Zetian: 50 anos de escalada metódica (não pulou etapas)",
                    "Teodora: Discurso Nika no momento de maior desespero de Justiniano"
                ],
                "pergunta_charlee": "Este é momento de alavancagem máxima ou você está precipitado?",
                "aplicacao_moderna": [
                    "Espere adversário cometer erro antes de atacar",
                    "Lance produto quando mercado está pronto (não antes)",
                    "Negocie aumento quando você é indispensável (não quando está fraco)",
                    "Tome decisões importantes quando tem clareza (não sob pressão)"
                ]
            },

            UniversalPrinciple.NARRATIVE_CONTROL: {
                "nome": "Controle Narrativo",
                "descricao": (
                    "Todas definiram ativamente como eram vistas. "
                    "Quem não controla sua história terá ela escrita por inimigos."
                ),
                "exemplos_historicos": [
                    "Cleópatra: Apresentação como Ísis (deusa, não apenas rainha)",
                    "Elizabeth: 'Rainha Virgem' = independência política",
                    "Catarina: 'Déspota esclarecida' via correspondência com Voltaire",
                    "Wu Zetian: Criou PRÓPRIO caractere chinês (曌) = única na história",
                    "Teodora: De 'pecadora' a 'reformadora compassiva'"
                ],
                "pergunta_charlee": "Você está controlando sua história ou outros a escrevem?",
                "aplicacao_moderna": [
                    "Personal branding ativo (LinkedIn, Twitter, blog)",
                    "Corrija ativamente descrições incorretas de você",
                    "Crie 'neologismos' para seus conceitos únicos",
                    "Conte sua história ANTES que outros contem por você"
                ]
            },

            UniversalPrinciple.PRAGMATISM_OVER_IDEALISM: {
                "nome": "Pragmatismo > Idealismo",
                "descricao": (
                    "Todas escolheram efetividade sobre pureza moral. "
                    "Vencedoras fazem o que funciona, não o que é 'puro'."
                ),
                "exemplos_historicos": [
                    "Cleópatra: Usou beleza/charme (ferramentas disponíveis)",
                    "Elizabeth: Ambiguidade religiosa (não pureza teológica)",
                    "Catarina: Manteve servidão (pragmatismo vs idealismo abolicionista)",
                    "Wu Zetian: Budismo como ferramenta (não necessariamente fé profunda)",
                    "Teodora: Métodos brutais quando necessário (espionagem, eliminação)"
                ],
                "pergunta_charlee": "Você quer estar certo ou quer vencer? (Às vezes não pode ambos)",
                "aplicacao_moderna": [
                    "Use ferramentas disponíveis (mesmo se não ideais)",
                    "Compromissos estratégicos > pureza absoluta",
                    "Resultados > Processos perfeitos",
                    "Mas: SEMPRE dentro da ética/lei moderna (não replique crueldade)"
                ]
            },

            UniversalPrinciple.COURAGE_IN_CRISIS: {
                "nome": "Coragem em Momentos Críticos",
                "descricao": (
                    "Todas tiveram momentos de escolha existencial e escolheram risco. "
                    "Grandes líderes são definidos por decisões em crises."
                ),
                "exemplos_historicos": [
                    "Cleópatra: Entrar escondida em tapete para César (risco de morte)",
                    "Elizabeth: Ficar e lutar em Tilbury (vs fugir da Armada)",
                    "Catarina: Executar golpe contra marido (risco de execução)",
                    "Wu Zetian: Eliminar Imperatriz Wang (tudo ou nada)",
                    "Teodora: 'Prefiro púrpura como mortalha' (Revolta Nika)"
                ],
                "pergunta_charlee": "Se você não arriscar agora, quando?",
                "aplicacao_moderna": [
                    "Grandes oportunidades vêm disfarçadas de problemas",
                    "Momento de maior risco = momento de maior impacto potencial",
                    "Coragem não é ausência de medo, é ação APESAR do medo",
                    "Inação em crise é TAMBÉM uma decisão (geralmente pior)"
                ]
            }
        }

        return principles[principle]
```

---

## 6. Framework de Aplicação

### 6.1 Sistema de Conversação

```python
# backend/modules/feminine_power/conversation.py

from typing import List, Dict
from backend.agents.base import Agent
from backend.llm.openai import OpenAIChat

class FemininePowerConversationAgent(Agent):
    """
    Agente conversacional especializado em aplicar insights históricos
    """

    def __init__(
        self,
        db_connection,
        knowledge_base: KnowledgeBase,
        matcher: HistoricalStrategyMatcher
    ):
        super().__init__(
            name="Feminine Power Advisor",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "Você é especialista em estratégias de poder feminino histórico",
                "Sua função é conectar situações modernas com insights de 5 mulheres icônicas",
                "Seja conversacional, provocativo (faz pensar), prático (acionável)",
                "SEMPRE adapte para ética moderna (não glorifique crueldade)",
                "Use histórias para ilustrar, perguntas para aprofundar"
            ]
        )
        self.db = db_connection
        self.kb = knowledge_base
        self.matcher = matcher

    async def respond_to_situation(
        self,
        user_id: str,
        situation_description: str
    ) -> Dict:
        """
        Responde a situação do usuário com insights históricos
        """

        # 1. Analisar situação
        situation = await self._analyze_situation(situation_description)

        # 2. Encontrar estratégias relevantes
        matches = await self.matcher.find_best_strategies(situation, top_n=2)

        if not matches:
            return {
                "response": "Não encontrei paralelo histórico direto. Pode me dar mais contexto?",
                "suggestions": []
            }

        # 3. Gerar resposta conversacional
        response = await self._generate_conversational_response(
            situation,
            matches
        )

        # 4. Gerar perguntas reflexivas
        questions = self._generate_reflection_questions(situation, matches[0])

        # 5. Registrar interação
        await self._log_interaction(user_id, situation, matches, response)

        return {
            "response": response,
            "strategy_matches": [m.strategy.strategy_name for m in matches],
            "reflection_questions": questions,
            "learn_more_links": [
                f"/api/feminine-power/strategy/{m.strategy.strategy_id}"
                for m in matches
            ]
        }

    async def _analyze_situation(self, description: str) -> UserSituation:
        """Analisa descrição e extrai contexto"""

        # Usar LLM para extrair keywords e contexto
        prompt = f"""
Analise a seguinte situação e extraia:
1. Keywords principais (3-5 palavras)
2. Power dynamics (inferior/equal/superior)
3. Urgência (high/medium/low)

Situação: "{description}"

Retorne JSON:
{{
    "keywords": ["palavra1", "palavra2", ...],
    "power_dynamics": "inferior",
    "urgency": "medium"
}}
"""

        analysis = await self.run(prompt)
        parsed = self._parse_json(analysis)

        return UserSituation(
            description=description,
            context=parsed,
            keywords=parsed["keywords"],
            urgency=parsed["urgency"],
            power_dynamics=parsed["power_dynamics"]
        )

    async def _generate_conversational_response(
        self,
        situation: UserSituation,
        matches: List[StrategyMatch]
    ) -> str:
        """
        Gera resposta conversacional conectando situação com história
        """

        best_match = matches[0]
        strategy = best_match.strategy

        # Template de resposta
        response = f"**{strategy.archetype.value.replace('_', ' ').title()} enfrentou algo similar:**\n\n"

        # Contexto histórico conciso
        response += f"📜 **Contexto:** {strategy.context}\n\n"

        # Estratégia usada
        response += f"⚡ **O que ela fez:**\n{strategy.execution[:200]}...\n\n"

        # Resultado
        response += f"✅ **Resultado:** {strategy.result[:150]}...\n\n"

        # Aplicação moderna
        response += f"🎯 **Para você:**\n{strategy.modern_application[:300]}...\n\n"

        # Considerações éticas
        if "⚠️" in strategy.ethical_considerations:
            response += f"⚠️ **Importante:** {strategy.ethical_considerations[:200]}...\n\n"

        # Call to action
        response += "💡 **Quer explorar mais essa estratégia ou ver outra perspectiva?**"

        return response

    def _generate_reflection_questions(
        self,
        situation: UserSituation,
        match: StrategyMatch
    ) -> List[str]:
        """
        Gera perguntas reflexivas para aprofundar pensamento
        """

        archetype = match.strategy.archetype

        # Perguntas específicas por arquétipo
        questions_by_archetype = {
            HistoricalArchetype.CLEOPATRA: [
                "Qual conhecimento você tem que seus adversários NÃO têm?",
                "Quem é o 'César' ou 'Marco Antônio' que poderia ser seu aliado?",
                "Como você pode tornar-se INDISPENSÁVEL (não apenas útil)?",
                "Qual é sua vantagem assimétrica nessa negociação?"
            ],

            HistoricalArchetype.ELIZABETH: [
                "Quem se beneficia da sua decisão RÁPIDA? (Normalmente não é você)",
                "O que você ganha mantendo as opções em 'talvez'?",
                "Existe deadline REAL ou ARTIFICIAL?",
                "Como você pode usar oferta A para melhorar oferta B?"
            ],

            HistoricalArchetype.CATHERINE: [
                "Quem está insatisfeito mas ainda não tem alternativa?",
                "Você tem legitimidade (track record, credenciais)?",
                "Quem são seus 'executores práticos' (Irmãos Orlov)?",
                "Qual erro do 'regime atual' você está esperando?",
                "Você está pronto para assumir IMEDIATAMENTE após mudança?"
            ],

            HistoricalArchetype.WU_ZETIAN: [
                "Você está disposto a começar 'abaixo' de sua capacidade para aprender o sistema?",
                "Qual posição lhe dá VISIBILIDADE de como decisões reais são tomadas?",
                "Quem está no caminho E é vulnerável agora (não espere ficarem fortes)?",
                "Você pode ter poder SEM título formal por um tempo?",
                "Quando já controla o essencial, AÍ pega o título?"
            ],

            HistoricalArchetype.THEODORA: [
                "Você está 'experimentando' ou CORTANDO ponte com passado?",
                "Pode mudar fisicamente (cidade, empresa, círculo)?",
                "Que comportamentos comunicam nova identidade?",
                "Quem, ao te aceitar, faz outros aceitarem?",
                "Você está disposto a NUNCA voltar ao comportamento antigo?",
                "Como seu passado doloroso pode se tornar sua missão?"
            ]
        }

        return questions_by_archetype.get(archetype, [
            "O que você está disposto a arriscar?",
            "Qual é o custo de NÃO agir?",
            "Se não agora, quando?"
        ])

    async def _log_interaction(
        self,
        user_id: str,
        situation: UserSituation,
        matches: List[StrategyMatch],
        response: str
    ):
        """Registra interação para aprendizado"""

        self.db.execute("""
            INSERT INTO feminine_power_interactions
            (user_id, situation_description, strategy_matches, response, criado_em)
            VALUES (%s, %s, %s, %s, NOW())
        """, (
            user_id,
            situation.description,
            json.dumps([m.strategy.strategy_id for m in matches]),
            response
        ))
```

---

## 7. Integração com Outros Módulos

### 7.1 Feminine Power → Diplomat

```python
# backend/modules/feminine_power/integrations/diplomat.py

class FemininePowerDiplomatIntegration:
    """
    Integração entre Feminine Power e Diplomat
    Oferece insights históricos para gestão de relacionamentos
    """

    def __init__(self, event_bus: EventBus, feminine_power, diplomat):
        self.event_bus = event_bus
        self.fp = feminine_power
        self.diplomat = diplomat

        # Subscribe a eventos do Diplomat
        self.event_bus.subscribe(
            "diplomat.relationship_challenge",
            self.on_relationship_challenge
        )

    async def on_relationship_challenge(self, event_data: dict):
        """
        Quando há desafio em relacionamento, oferece insights históricos
        """

        challenge_type = event_data["challenge_type"]
        pessoa_id = event_data["pessoa_id"]

        # Mapear desafio para estratégia histórica
        strategy_suggestions = {
            "difficult_negotiation": "cleopatra_romantic_alliances",
            "power_imbalance": "cleopatra_romantic_alliances",
            "partner_evaluation": "theodora_transformation",
            "building_alliance": "catherine_coup"
        }

        strategy_id = strategy_suggestions.get(challenge_type)

        if strategy_id:
            strategy = self.fp.kb.get_strategy(strategy_id)

            # Enviar sugestão via notificação
            await self._send_historical_insight(
                user_id=event_data["user_id"],
                pessoa_id=pessoa_id,
                strategy=strategy,
                challenge=challenge_type
            )
```

### 7.2 Feminine Power → Listener

```python
# backend/modules/feminine_power/integrations/listener.py

class FemininePowerListenerIntegration:
    """
    Integração entre Feminine Power e Listener
    Analisa evolução comunicacional com base em arquétipos históricos
    """

    def __init__(self, event_bus: EventBus, feminine_power, listener):
        self.event_bus = event_bus
        self.fp = feminine_power
        self.listener = listener

        # Subscribe a relatórios de soberania
        self.event_bus.subscribe(
            "listener.sovereignty_report_ready",
            self.on_sovereignty_report
        )

    async def on_sovereignty_report(self, event_data: dict):
        """
        Quando relatório de soberania está pronto, adiciona contexto histórico
        """

        report = event_data["report"]
        user_id = event_data["user_id"]

        # Identificar padrões similares a figuras históricas
        patterns = report["padroes_positivos"]

        historical_parallels = []

        if "tom_calmo" in patterns:
            historical_parallels.append({
                "archetype": "Elizabeth I",
                "trait": "Serenidade mesmo em crise (Discurso de Tilbury)",
                "quote": "'Tenho coração e estômago de um rei'"
            })

        if "decisoes_claras" in patterns:
            historical_parallels.append({
                "archetype": "Catarina II",
                "trait": "Decisões rápidas e pragmáticas",
                "quote": "'Reforme o suficiente para manter controle'"
            })

        # Adicionar ao relatório
        report["historical_parallels"] = historical_parallels

        # Enviar relatório enriquecido
        await self.event_bus.emit("listener.sovereignty_report_enriched", {
            "user_id": user_id,
            "report": report
        })
```

---

## 8. Schemas de Banco de Dados

```sql
-- Interações com módulo Feminine Power
CREATE TABLE feminine_power_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    -- Situação do usuário
    situation_description TEXT NOT NULL,
    situation_context JSONB,

    -- Estratégias sugeridas
    strategy_matches JSONB NOT NULL,  -- array de strategy_ids

    -- Resposta gerada
    response TEXT NOT NULL,

    -- Feedback do usuário
    user_rating INTEGER,  -- 1-5
    was_helpful BOOLEAN,
    user_feedback TEXT,

    criado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_created (user_id, criado_em),
    INDEX idx_rating (user_rating)
);

-- Estratégias favoritas do usuário
CREATE TABLE feminine_power_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    strategy_id VARCHAR(100) NOT NULL,
    archetype VARCHAR(50) NOT NULL,

    notes TEXT,  -- notas pessoais do usuário
    applied BOOLEAN DEFAULT FALSE,  -- usuário aplicou a estratégia?
    result TEXT,  -- resultado quando aplicou

    criado_em TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, strategy_id),
    INDEX idx_user_archetype (user_id, archetype)
);

-- Princípios universais aprendidos
CREATE TABLE feminine_power_principles_learned (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    principle VARCHAR(50) NOT NULL,  -- 'education', 'alliances', etc.

    -- Aprendizado
    first_learned TIMESTAMP DEFAULT NOW(),
    times_reinforced INTEGER DEFAULT 1,
    confidence_level DECIMAL(3,2),  -- 0.0 - 1.0

    -- Aplicação
    applied_situations JSONB,  -- array de situações onde aplicou

    INDEX idx_user_principle (user_id, principle)
);

-- Analytics de uso
CREATE TABLE feminine_power_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    -- Arquétipo mais usado
    most_consulted_archetype VARCHAR(50),

    -- Princípios mais aplicados
    most_applied_principles JSONB,

    -- Efetividade
    avg_rating DECIMAL(3,2),
    success_rate DECIMAL(3,2),  -- % de estratégias que funcionaram

    -- Temporal
    periodo VARCHAR(20),  -- 'week' | 'month'
    data_inicio DATE,
    data_fim DATE,

    criado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_periodo (user_id, periodo, data_fim)
);
```

---

## 9. API Endpoints

```python
# backend/modules/feminine_power/routes.py

from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/feminine-power", tags=["Feminine Power"])

@router.post("/analyze-situation")
async def analyze_situation(
    situation: str,
    user_id: str = Depends(get_current_user)
):
    """
    Analisa situação e retorna insights históricos relevantes
    """

    agent = FemininePowerConversationAgent(db, kb, matcher)
    response = await agent.respond_to_situation(user_id, situation)

    return response

@router.get("/archetypes")
async def get_archetypes():
    """
    Retorna lista de todos os arquétipos disponíveis
    """

    archetypes = []
    for archetype in HistoricalArchetype:
        profile = ArchetypeProfile(archetype)
        archetypes.append({
            "id": archetype.value,
            "nome": profile.data["nome"],
            "periodo": profile.data["periodo"],
            "conquista": profile.data["conquista"]
        })

    return {"archetypes": archetypes}

@router.get("/archetype/{archetype_id}")
async def get_archetype_details(archetype_id: str):
    """
    Retorna detalhes completos de um arquétipo
    """

    archetype = HistoricalArchetype(archetype_id)
    profile = ArchetypeProfile(archetype)

    return profile.data

@router.get("/strategies")
async def get_all_strategies(
    archetype: str = None,
    user_id: str = Depends(get_current_user)
):
    """
    Retorna todas as estratégias (opcionalmente filtradas por arquétipo)
    """

    strategies = kb.strategies.values()

    if archetype:
        archetype_enum = HistoricalArchetype(archetype)
        strategies = [s for s in strategies if s.archetype == archetype_enum]

    return {
        "strategies": [
            {
                "id": s.strategy_id,
                "nome": s.strategy_name,
                "archetype": s.archetype.value,
                "context": s.context[:150] + "..."
            }
            for s in strategies
        ]
    }

@router.get("/strategy/{strategy_id}")
async def get_strategy_details(strategy_id: str):
    """
    Retorna detalhes completos de uma estratégia
    """

    strategy = kb.get_strategy(strategy_id)

    if not strategy:
        raise HTTPException(404, "Estratégia não encontrada")

    return {
        "strategy": strategy.__dict__
    }

@router.post("/favorites/{strategy_id}")
async def add_favorite(
    strategy_id: str,
    notes: str = None,
    user_id: str = Depends(get_current_user)
):
    """
    Adiciona estratégia aos favoritos
    """

    strategy = kb.get_strategy(strategy_id)

    db.execute("""
        INSERT INTO feminine_power_favorites
        (user_id, strategy_id, archetype, notes, criado_em)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (user_id, strategy_id) DO UPDATE SET
            notes = EXCLUDED.notes
    """, (user_id, strategy_id, strategy.archetype.value, notes))

    return {"status": "added"}

@router.get("/favorites")
async def get_favorites(user_id: str = Depends(get_current_user)):
    """
    Retorna estratégias favoritas do usuário
    """

    favorites = db.execute("""
        SELECT strategy_id, archetype, notes, applied, result
        FROM feminine_power_favorites
        WHERE user_id = %s
        ORDER BY criado_em DESC
    """, (user_id,)).fetchall()

    return {"favorites": favorites}

@router.post("/feedback")
async def submit_feedback(
    interaction_id: str,
    rating: int,
    was_helpful: bool,
    feedback_text: str = None,
    user_id: str = Depends(get_current_user)
):
    """
    Envia feedback sobre uma interação
    """

    db.execute("""
        UPDATE feminine_power_interactions
        SET user_rating = %s,
            was_helpful = %s,
            user_feedback = %s
        WHERE id = %s AND user_id = %s
    """, (rating, was_helpful, feedback_text, interaction_id, user_id))

    return {"status": "feedback_received"}

@router.get("/analytics")
async def get_analytics(
    periodo: str = "month",
    user_id: str = Depends(get_current_user)
):
    """
    Retorna analytics de uso do módulo
    """

    analytics = FemininePowerAnalytics(db)
    return await analytics.get_user_analytics(user_id, periodo)
```

---

## 10. Exemplos de Conversação

### 10.1 Exemplo 1: Negociação Difícil

**Usuário:** "Estou negociando com empresa muito maior que eu. Como não ser esmagado?"

**Charlee:**
```
**Cleópatra VII enfrentou EXATAMENTE isso:**

📜 **Contexto:** O Egito era rico mas militarmente inferior a Roma.
Cleópatra não tentou competir em força.

⚡ **O que ela fez:**
• Maximizou o que tinha: Riqueza → investiu em mostrar valor para Roma
• Cultura → apresentou-se como ponte civilizacional
• Inteligência → conhecia língua e cultura romana melhor que romanos conheciam egípcia
• Alianças → César e Marco Antônio tornaram-se aliados, não conquistadores

✅ **Resultado:** Egito manteve independência por 20 anos contra maior império do mundo

🎯 **Para você:**

Perguntas de reflexão:
1. O que VOCÊ tem que o 'império' maior PRECISA? (Não o que você acha - o que ELE precisa)
2. Como você pode ser INDISPENSÁVEL ao invés de descartável?
3. Qual 'aliança' você pode oferecer que neutraliza desvantagem de tamanho?
4. Você conhece a 'cultura' deles melhor que eles conhecem a sua?

**Princípio de Cleópatra:** Tamanho não é destino. Compensate fraquezas maximizando forças únicas.

💡 Quer explorar estratégias de aliança específicas ou ver perspectiva diferente?
```

### 10.2 Exemplo 2: Múltiplas Ofertas

**Usuário:** "Tenho 3 ofertas de emprego. Todos pressionando para decidir rápido. O que faço?"

**Charlee:**
```
**Elizabeth I manteve 20 pretendentes em suspense por 45 anos. Por quê?**

📜 **Contexto:** Casamento real = perda de poder (submissão ao marido, alinhamento com país dele)

⚡ **O que ela fez:**
• Manteve TODOS na esperança de possível 'sim'
• Usou pretendentes como peças diplomáticas
• Nunca entregou o 'prêmio'
• Frase icônica: "Estou casada com a Inglaterra"

✅ **Resultado:** 45 anos de independência total, múltiplos países cortejando favores

🎯 **Para você:**

**Framework Elizabeth:**
1. 'Estou muito interessado, mas preciso garantir fit perfeito' = Não é não, não é sim
2. 'Podem me dar mais 2 semanas para decisão tão importante?' = Compra tempo
3. Enquanto isso: Use oferta A para melhorar oferta B, B para melhorar C

**Perguntas:**
• Quem se BENEFICIA da sua decisão rápida? (Normalmente não é você)
• O que você ganha mantendo as 3 em 'talvez'? (Leverage em cada negociação)
• Há deadline REAL ou ARTIFICIAL? (Se artificial, ignore)

⚠️ **CUIDADO:** Elizabeth sabia quando fechar negócio vs manter aberto.
Não abuse - eventualmente precisa decidir.

**Princípio:** OPTIONALIDADE É PODER. Mas não deixe SER pressionado quando você tem as cartas.

💡 Quer ver como Catarina II tomava decisões irreversíveis?
```

### 10.3 Exemplo 3: Transformação Radical

**Usuário:** "Quero mudar completamente minha carreira/vida mas tenho passado 'questionável'."

**Charlee:**
```
**Teodora foi LITERALMENTE prostituta e virou imperatriz. No século VI.**

📜 **Contexto:** Prostituta em Constantinopla (profissão estigmatizada).
Sociedade bizantina extremamente misógina.

⚡ **O que ela fez:**

**TRAJETÓRIA:**
~512 (15 anos): Atriz/prostituta
~520: Viajou pelo Oriente, converteu-se ao Cristianismo
522 (25 anos): Retornou como 'fiandeira' (trabalho honesto)
523-525: Relacionamento com Justiniano → Lei MUDADA para permitir casamento
525: Casamento → Elevada a Patrícia
527: Imperatriz

**ESTRATÉGIAS:**
1. Mudança de contexto físico (viagem = 'reset')
2. Reframe religioso ('pecadora arrependida' = arquétipo de Maria Madalena)
3. Comportamento consistente (NUNCA voltou à vida anterior)
4. Aliado validador (Justiniano mudou LEI por ela)
5. Missão redentora (fechou bordéis, criou Convento Metanoia para ex-prostitutas)

✅ **Resultado:** Co-governante de fato, primeira lei de proteção feminina no Ocidente

🎯 **Framework de Transformação Radical para você:**

**7 PASSOS:**
1. RECONHECIMENTO: Admita onde você está (sem vergonha)
2. DECISÃO DEFINITIVA: Você está 'experimentando' ou CORTANDO ponte?
3. MUDANÇA DE CONTEXTO: Pode mudar fisicamente (cidade, empresa, círculo)?
4. NOVO SIMBOLISMO: Que comportamentos comunicam nova identidade?
5. ALIADO VALIDADOR: Quem, ao te aceitar, faz outros aceitarem?
6. CONSISTÊNCIA ABSOLUTA: Nunca volte ao comportamento antigo (mesmo em privado)
7. LEGADO REDENTOR: Use passado doloroso para ajudar outros

**Perguntas:**
• Você está disposto a REALMENTE mudar (não 'tentar')?
• Qual é a ação irreversível que sinaliza mudança?
• Como seu passado doloroso pode se tornar sua missão?

**Teodora nos ensina:** Passado não define futuro. Mas exige mudança genuína, não cosmética.

Sua ferida pode ser sua tese. Seu passado pode ser seu propósito.

💡 Quer explorar como construir aliança validadora ou ver estratégia diferente?
```

---

## 11. Roadmap de Implementação

### 11.1 Fase 1: Base de Conhecimento (1 mês)

**Objetivo:** Estruturar conhecimento histórico

**Componentes:**
- [ ] Schemas de banco de dados
- [ ] Knowledge Base completa (5 arquétipos + estratégias)
- [ ] Sistema de princípios universais
- [ ] Documentação técnica

🎯 **Critério de Sucesso:**
- 5 arquétipos completamente documentados
- 20+ estratégias específicas mapeadas
- 6 princípios universais estruturados

### 11.2 Fase 2: Sistema de Matching (1 mês)

**Objetivo:** Conectar situações a estratégias

**Componentes:**
- [ ] Algoritmo de matching situação → estratégia
- [ ] Sistema de scoring de relevância
- [ ] Gerador de adaptação para contexto moderno
- [ ] Testes com casos reais

🎯 **Critério de Sucesso:**
- Precisão >70% em matching correto
- Usuário valida relevância em >80% dos casos
- Tempo de resposta <3 segundos

### 11.3 Fase 3: Agente Conversacional (1 mês)

**Objetivo:** Interface conversacional natural

**Componentes:**
- [ ] FemininePowerConversationAgent
- [ ] Templates de resposta por arquétipo
- [ ] Sistema de perguntas reflexivas
- [ ] Integração com LLM (GPT-4o)

🎯 **Critério de Sucesso:**
- Respostas naturais e engajantes
- Perguntas provocam reflexão (feedback qualitativo)
- NPS ≥ 8/10 para feature

### 11.4 Fase 4: Integrações (1 mês)

**Objetivo:** Conectar com outros módulos

**Componentes:**
- [ ] Integração com Diplomat (insights relacionais)
- [ ] Integração com Listener (soberania comunicacional)
- [ ] Integração com Wellness (correlação com bem-estar)
- [ ] API completa

🎯 **Critério de Sucesso:**
- Insights aparecem proativamente quando relevante
- Usuário usa módulo >2x/semana
- Correlação positiva com métricas de bem-estar

---

## 12. Conclusão

**Charlee Feminine Power** oferece um diferencial único:

✨ **2000+ anos de estratégias comprovadas**
✨ **Insights acionáveis** (não apenas inspiração)
✨ **Adaptação ética** para contexto moderno
✨ **Sistema inteligente** de matching situação → estratégia

Este módulo transforma conhecimento histórico em **ferramenta prática** para liderança feminina moderna.

**Próximos passos:**
1. Implementar Fase 1 (Base de Conhecimento)
2. Testar matching com usuários reais
3. Refinar conversação baseado em feedback
4. Expandir para mais figuras históricas (Fase 5+)

---

**Versão:** V5.0
**Última atualização:** 17 Janeiro 2025
**Autor:** Charlee Development Team
**Status:** 🔴 Planejamento (V5.0)
