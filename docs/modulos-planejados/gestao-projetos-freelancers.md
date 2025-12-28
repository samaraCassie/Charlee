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

🧩 3. Requisitos Funcionais (RF)

ID	Requisito	Descrição	Prioridade

RF01	Monitorar plataformas freelancer	O sistema deve integrar-se a APIs (Upwork, Freelancer.com etc.) e coletar novos projetos.	Alta
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

🧠 6. Arquitetura de Agentes e Módulos

┌──────────────────────────────┐
│       Agente Gestor          │
│ Coordena os demais agentes   │
└──────────────┬───────────────┘
               │
┌──────────────┼────────────────────────────────────────────────┐
│              │                                                │
│     Núcleo de Execução                                 Núcleo de Aprendizado    │
│                                                    │
│ 🧩 Coletor  → coleta projetos                       🧠 Autoaprendizado → ajusta parâmetros  │
│ 🧠 Analisador → entende escopo                      📊 Analítico → compila métricas         │
│ ⚖️ Avaliador → precifica e avalia viabilidade       🪞 Branding → gera insights de carreira │
│ 💬 Negociador → contra-propostas                    │
└────────────────────────────────────────────────────┘


---

🧩 7. MVP (Versão 1.0)

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

🚀 8. Versão 2.0 — Inteligência e Aprendizado

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

💡 9. Versão 3.0 — Inteligência Estratégica e Branding

Funcionalidades:

RF10–RF12: análises de portfólio, branding e insights pessoais.

Detecção de padrões e evolução técnica.

Correlação entre habilidades, tipos de projeto e lucro.

Geração de relatórios em PDF ou painel web (Streamlit / LangFlow).


Funcionalidades avançadas:

Recomendações automáticas de posicionamento (“enfatize automação IA em seu perfil”).

Análises emocionais e qualitativas baseadas nas observações manuais.



---

🧠 10. Versão 4.0 — Autonomia e Coach Profissional

Funcionalidades:

Comunicação natural via chat (interação direta com o agente).

Aprendizado auto-reflexivo (“insight semanal sobre seu desempenho”).

Comparação temporal de evolução (gráficos de complexidade e valor médio).

Estratégia preditiva (“setor de IA em alta, priorize esses projetos”).

Geração automática de material de portfólio (descrições otimizadas de projetos).



---

💾 11. Estrutura de Dados (resumo)

Entidade	Campos principais

Projeto	id, título, descrição, plataforma, complexidade, valor_sugerido, valor_cliente, prazo, aceito, resultado
Feedback	id_projeto, decisão, motivo, tempo_gasto, observacoes_pessoais
Parametros	valor_hora_base, margem_minima, fator_especializacao, limite_prazo
Relatorio	periodo, faturamento, taxa_sucesso, complexidade_media, setor_dominante
Insight	data, tipo, descricao, impacto, recomendacao



---

📊 12. Tecnologias sugeridas

Categoria	Ferramenta

Framework de agentes	Agno
LLM	GPT-5 / Claude 3.5
Banco de dados	DynamoDB (produção) / SQLite (MVP)
Dashboard	Streamlit / LangFlow
Scheduler	APScheduler / AWS Lambda
APIs externas	Upwork, Freelancer.com, Apify
Integração	Telegram Bot, Gmail API (alertas)



---

🧭 13. Roadmap sugerido

Fase	Entrega	Período estimado

Fase 1 (MVP)	Coleta + Análise + Avaliação	2–4 semanas
Fase 2	Aprendizado + Contra-propostas	4–6 semanas
Fase 3	Branding + Insights Profissionais	6–8 semanas
Fase 4	Autonomia e Preditividade	8–12 semanas



---

🔐 14. Considerações Finais

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

Quer que eu continue com os próximos agentes?

1. ✅ **NegotiatorAgent** (gera contra-propostas diplomáticas)
2. ✅ **AnalyticsAgent** (métricas e insights)
3. ✅ **BrandingAdvisorAgent** (análise de posicionamento)
4. ✅ **LearningAgent** (aprendizado contínuo)
5. ✅ **OrchestratorAgent** (coordena todos)

Ou prefere que eu gere:
- **Fluxo completo** de análise (do Collector ao Negotiator)
- **CLI** do módulo Projects
- **Dashboard** de métricas
- **Integração com Charlee principal**

**O que prefere?** 🚀