# Charlee V2 - Implementação Completa ✅

## 🎉 O que foi implementado na V2

### ⚡ Mudança Principal: GPT-4o Mini
- **Modelo atualizado**: Todos os agentes agora usam GPT-4o mini (OpenAI)
- **Custo reduzido**: GPT-4o mini é muito mais barato que Claude
- **Performance**: Resposta rápida e eficiente

### 🌸 Sistema de Bem-Estar e Ciclo Menstrual

#### Novos Models:
1. **CicloMenstrual** - Registra fases e sintomas
   - Fases: menstrual, folicular, ovulação, lutea
   - Tracking: energia, foco, criatividade (1-10)
   - Sintomas e notas livres

2. **PadroesCiclo** - Aprende padrões de produtividade
   - Identifica como cada fase afeta o desempenho
   - Score de confiança aumenta com mais dados
   - Sugestões personalizadas por fase

3. **RegistroDiario** - Tracking diário de hábitos
   - Sono (qualidade, duração)
   - Energia em diferentes períodos do dia
   - Deep work e produtividade
   - Eventos e notas

4. **CargaTrabalho** - Análise de capacidade
   - Monitora carga por Big Rock
   - Identifica riscos de sobrecarga
   - Alertas proativos

#### CycleAwareAgent (Wellness Coach)
Agente especializado que:
- Registra e tracked o ciclo menstrual
- Sugere tipos de tarefas ideais para cada fase
- Adapta planejamento baseado na energia esperada
- Analisa se a carga está adequada para a fase

**Ferramentas disponíveis:**
- `registrar_fase_ciclo` - Registra nova fase
- `obter_fase_atual` - Mostra fase e recomendações
- `sugerir_tarefas_fase` - Sugere tarefas por fase
- `analisar_carga_para_fase` - Valida carga vs. energia

**Endpoints API:**
- `POST /api/v2/wellness/ciclo/registrar` - Registrar fase
- `GET /api/v2/wellness/ciclo/atual` - Ver fase atual
- `GET /api/v2/wellness/ciclo/sugestoes` - Sugestões por fase
- `GET /api/v2/wellness/ciclo/analise-carga` - Análise de carga

### 🛡️ Sistema de "Não Estratégico" (Capacity Guard)

#### CapacityGuardAgent
Agente guardião que **protege contra sobrecarga**:
- Calcula carga atual por Big Rock
- Avalia novo compromisso ANTES de aceitar
- Força decisões conscientes sobre trade-offs
- Sugere o que adiar quando necessário

**Ferramentas disponíveis:**
- `calcular_carga_atual` - Análise de carga por Big Rock
- `avaliar_novo_compromisso` - Decisão: aceitar ou não?
- `sugerir_tradeoffs` - O que adiar?
- `analisar_big_rocks` - Distribuição entre pilares

**Endpoints API:**
- `GET /api/v2/capacity/carga/atual` - Ver carga atual
- `POST /api/v2/capacity/avaliar-compromisso` - Avaliar novo projeto
- `GET /api/v2/capacity/tradeoffs` - Sugestões de trade-off
- `GET /api/v2/capacity/big-rocks/analise` - Análise de equilíbrio

### 📊 Sistema de Priorização Inteligente

#### SistemaPriorizacao
Algoritmo que calcula prioridade baseado em:

1. **Urgência (40%)** - Quão próximo está o deadline
   - Atrasado = máxima prioridade
   - Hoje = 95%
   - 1-2 dias = 90%
   - 1 semana = 70%
   - etc.

2. **Importância (30%)** - Big Rock estratégico
   - Big Rocks prioritários (ex: Syssa, Crise Lunelli) = 100%
   - Outros = 60%
   - Sem Big Rock = 50%

3. **Abandono (20%)** - Tempo sem movimento
   - Mais de 1 mês = precisa atenção (80%)
   - 2 semanas = 60%
   - 1 semana = 40%

4. **Tipo (10%)** - Natureza da tarefa
   - Compromisso Fixo = 100%
   - Tarefa = 70%
   - Contínuo = 40%

**Resultado:**
- Score de 0.0 a 1.0
- Convertido para nível 1-10 (1 = mais prioritário)
- Atualizado automaticamente

**Endpoints API:**
- `GET /api/v2/priorizacao/inbox` - Inbox rápido (top tarefas)
- `POST /api/v2/priorizacao/recalcular` - Recalcular prioridades
- `GET /api/v2/priorizacao/tarefas-priorizadas` - Lista ordenada

### 📈 Campos Adicionados em Tarefa

```python
# Novos campos V2
prioridade_calculada: int  # 1 (urgente) a 10 (baixo)
pontuacao_prioridade: float  # Score do algoritmo
```

## 🚀 Endpoints da V2

### Wellness (Bem-Estar)
```bash
# Registrar fase do ciclo
POST /api/v2/wellness/ciclo/registrar
{
  "data_inicio": "2025-01-15",
  "fase": "folicular",
  "nivel_energia": 8,
  "nivel_foco": 7,
  "nivel_criatividade": 9
}

# Ver fase atual e recomendações
GET /api/v2/wellness/ciclo/atual

# Sugestões para a fase
GET /api/v2/wellness/ciclo/sugestoes?fase=ovulacao

# Analisar carga vs. energia
GET /api/v2/wellness/ciclo/analise-carga?dias_futuro=7
```

### Capacity (Sobrecarga)
```bash
# Calcular carga atual
GET /api/v2/capacity/carga/atual?proximas_semanas=3

# Avaliar novo compromisso
POST /api/v2/capacity/avaliar-compromisso
{
  "nome_compromisso": "Projeto Novo XYZ",
  "tarefas_estimadas": 15,
  "big_rock_nome": "Syssa - Estágio"
}

# Sugestões de trade-off
GET /api/v2/capacity/tradeoffs?num_tarefas_liberar=5

# Análise de Big Rocks
GET /api/v2/capacity/big-rocks/analise
```

### Priorização
```bash
# Inbox rápido (top 10 tarefas)
GET /api/v2/priorizacao/inbox?limite=10

# Recalcular prioridades
POST /api/v2/priorizacao/recalcular

# Lista completa priorizada
GET /api/v2/priorizacao/tarefas-priorizadas?limite=20
```

## 💡 Exemplos de Uso

### Exemplo 1: Planejamento consciente do ciclo

```bash
# 1. Registrar fase atual
curl -X POST http://localhost:8000/api/v2/wellness/ciclo/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "data_inicio": "2025-01-15",
    "fase": "menstrual",
    "nivel_energia": 4,
    "sintomas": "fadiga,dor"
  }'

# 2. Ver recomendações
curl http://localhost:8000/api/v2/wellness/ciclo/sugestoes

# Resposta:
# "Fase de baixa energia. Priorize descanso e tarefas leves."
# Tipos ideais: administrativo, reflexão, planejamento
# Evitar: reuniões longas, decisões grandes
```

### Exemplo 2: Decisão sobre novo projeto

```bash
# Avaliar se pode aceitar novo projeto
curl -X POST http://localhost:8000/api/v2/capacity/avaliar-compromisso \
  -H "Content-Type: application/json" \
  -d '{
    "nome_compromisso": "Consultoria Empresa X",
    "tarefas_estimadas": 12
  }'

# Resposta pode ser:
# ✅ ACEITAR - Capacidade confortável
# ⚠️ ACEITAR COM RESSALVAS - Carga acima do ideal
# 🚨 NÃO ACEITAR - Sobrecarga! Precisa trade-offs
```

### Exemplo 3: Inbox rápido diário

```bash
# Ver top 10 tarefas priorizadas
curl http://localhost:8000/api/v2/priorizacao/inbox?limite=10

# Resposta exemplo:
# 📥 INBOX RÁPIDO - Top 10 tarefas
#
# 🔴 1. Apresentação Janeiro
#    📁 Syssa - Estágio | 🔥 HOJE | P1
#
# 🔴 2. Reunião com Breno
#    📁 Crise Lunelli | 📅 2d | P2
#
# 🟡 3. Relatório semanal
#    📁 Syssa - Estágio | 📅 15/01 | P4
```

## 🔄 Fluxo Completo V2

### Morning Routine com V2:

1. **Ver fase do ciclo atual**
   ```bash
   GET /api/v2/wellness/ciclo/atual
   ```

2. **Inbox priorizado**
   ```bash
   GET /api/v2/priorizacao/inbox
   ```

3. **Verificar carga da semana**
   ```bash
   GET /api/v2/capacity/carga/atual
   ```

4. **Analisar se carga está adequada para a fase**
   ```bash
   GET /api/v2/wellness/ciclo/analise-carga
   ```

### Quando surge novo projeto:

1. **Avaliar capacidade**
   ```bash
   POST /api/v2/capacity/avaliar-compromisso
   ```

2. **Se necessário, ver trade-offs**
   ```bash
   GET /api/v2/capacity/tradeoffs
   ```

3. **Tomar decisão informada**

## 📊 Arquitetura V2

```
┌─────────────────────────────────────────────────┐
│              Charlee V2                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  V1 (Base)                                      │
│  ├── Big Rocks & Tarefas                        │
│  ├── CRUD completo                              │
│  └── Agent básico (GPT-4o mini)                 │
│                                                 │
│  V2 (Inteligência)                              │
│  ├── 🌸 Wellness System                         │
│  │   ├── CycleAwareAgent                        │
│  │   ├── Tracking de ciclo                      │
│  │   └── Recomendações adaptativas              │
│  │                                               │
│  ├── 🛡️ Capacity Guard                          │
│  │   ├── CapacityGuardAgent                     │
│  │   ├── Análise de carga                       │
│  │   ├── Sistema de "não estratégico"           │
│  │   └── Trade-off advisor                      │
│  │                                               │
│  └── 📊 Priorização Inteligente                 │
│      ├── Algoritmo multi-fator                  │
│      ├── Inbox rápido                           │
│      └── Score automático                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## ✅ Checklist V2

- [x] Atualizar para GPT-4o mini
- [x] Models de ciclo menstrual
- [x] Models de carga de trabalho
- [x] CycleAwareAgent implementado
- [x] CapacityGuardAgent implementado
- [x] Sistema de priorização
- [x] Rotas API completas
- [x] Campos de prioridade em Tarefa
- [x] Documentação V2

## 🎯 Próximos Passos (V3)

1. **Interface CLI** - Facilitar uso diário
2. **Integração Google Calendar** - Sync automático
3. **Input multimodal** - Voz e screenshots
4. **Dashboard visual** - Métricas e gráficos
5. **Análise preditiva** - ML para padrões

## 🔧 Como testar a V2

```bash
# 1. Reconstruir o container (novos models)
docker-compose build backend

# 2. Reiniciar
docker-compose up -d

# 3. Acessar docs interativas
# http://localhost:8000/docs

# 4. Explorar os novos endpoints V2:
# - /api/v2/wellness/*
# - /api/v2/capacity/*
# - /api/v2/priorizacao/*
```

## 📝 Configuração

No arquivo [.env](.env), certifique-se de ter:

```bash
# OpenAI API para GPT-4o mini
OPENAI_API_KEY=sk-sua-chave-aqui

# Database
DATABASE_URL=postgresql://charlee:charlee123@postgres:5432/charlee_db
```

## 🎉 Status

**V2 COMPLETA E FUNCIONAL!** ✅

Features implementadas:
- ✅ Bem-estar consciente do ciclo
- ✅ Proteção contra sobrecarga
- ✅ Priorização inteligente
- ✅ GPT-4o mini (custo reduzido)
- ✅ API completa e documentada

**Pronto para uso!** 🚀
