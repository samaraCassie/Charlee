# Daily Tracking Agent - Sistema de Tracking Diário e Pattern Recognition

## Visão Geral

O **DailyTrackingAgent** é um agente especializado que coleta dados diários, identifica padrões de comportamento e fornece sugestões personalizadas baseadas em histórico real.

## Funcionalidades

### 1. Registro Diário
Coleta de dados sobre:
- **Sono**: horas dormidas e qualidade (1-10)
- **Energia**: níveis em diferentes períodos (manhã, tarde, noite)
- **Produtividade**: horas de deep work
- **Tarefas**: contagem automática de tarefas concluídas
- **Ciclo**: vinculação automática com fase menstrual
- **Notas**: observações livres

### 2. Análise de Tendências
- Médias de sono, energia e produtividade
- Identificação de melhor e pior dia
- Comparação temporal
- Estatísticas agregadas

### 3. Pattern Recognition (ML Básico)
Identifica automaticamente:
- **Correlação Sono x Energia**: quanto o sono afeta a energia
- **Produtividade por Fase do Ciclo**: padrões em cada fase menstrual
- **Melhores Horários**: quando você tem mais energia
- **Padrões Comportamentais**: tendências personalizadas

### 4. Sugestões Personalizadas
Baseadas em:
- Histórico dos últimos 14 dias
- Padrões identificados
- Fase atual do ciclo
- Correlações entre variáveis

Sugestões sobre:
- Otimização de sono
- Trabalho focado (deep work)
- Consistência de registro
- Adaptação ao ciclo menstrual

## API Endpoints

### POST `/api/v2/daily-tracking/record`
Registra dados do dia (hoje ou data específica).

**Request:**
```json
{
  "data": "2025-01-09",  // opcional, padrão: hoje
  "horas_sono": 7.5,
  "qualidade_sono": 8,
  "energia_manha": 7,
  "energia_tarde": 6,
  "energia_noite": 5,
  "horas_deep_work": 3.5,
  "notas": "Bom dia de trabalho focado!"
}
```

**Response:**
```json
{
  "message": "✅ Registro registrado para 2025-01-09!...",
  "data": "2025-01-09"
}
```

### GET `/api/v2/daily-tracking/today`
Obtém o registro de hoje.

**Response:**
```json
{
  "record": "📊 **Registro de Hoje...**"
}
```

### GET `/api/v2/daily-tracking/analysis?dias=7`
Analisa tendências dos últimos N dias.

**Parâmetros:**
- `dias`: número de dias para analisar (padrão: 7, máx: 90)

**Response:**
```json
{
  "analysis": "📊 **Análise dos Últimos 7 Dias**\n\n..."
}
```

### GET `/api/v2/daily-tracking/patterns`
Identifica padrões de produtividade.

**Requer:** Pelo menos 7 dias de registros

**Response:**
```json
{
  "patterns": "🔍 **Padrões Identificados:**\n\n..."
}
```

**Atualiza automaticamente:** Tabela `padroes_ciclo` com dados identificados

### GET `/api/v2/daily-tracking/suggestions`
Sugere otimizações personalizadas.

**Response:**
```json
{
  "suggestions": "💡 **Sugestões de Otimização:**\n\n..."
}
```

### GET `/api/v2/daily-tracking/status`
Retorna status geral do sistema de tracking.

**Response:**
```json
{
  "total_records": 45,
  "consistency_30days": "86.7%",
  "last_record_date": "2025-01-09",
  "patterns_identified": 4,
  "patterns": [
    {
      "fase": "folicular",
      "produtividade_media": 6.2,
      "confianca_score": 0.8,
      "amostras": 24
    }
  ]
}
```

## Integração com Orquestrador

O DailyTrackingAgent está integrado ao orquestrador e é acionado automaticamente quando detecta keywords relacionadas a tracking diário.

### Keywords que acionam:
- "registrar dia", "registro diário", "como foi o dia"
- "dormi", "sono", "acordei"
- "energia hoje", "produtividade hoje"
- "padrões", "identificar padrão"
- "otimizar", "sugestões", "análise"
- "últimos dias"

### Exemplo via Chat:
```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Registrar que dormi 8 horas e estou com energia 7"}'
```

O orquestrador detecta automaticamente e roteia para DailyTrackingAgent.

## Modelo de Dados

### RegistroDiario
```python
{
    "data": "2025-01-09",           # Único por dia
    "horas_sono": 7.5,
    "qualidade_sono": 8,            # 1-10
    "energia_manha": 7,             # 1-10
    "energia_tarde": 6,             # 1-10
    "energia_noite": 5,             # 1-10
    "horas_deep_work": 3.5,
    "tarefas_completadas": 5,       # Auto-calculado
    "fase_ciclo": "folicular",      # Auto-vinculado
    "notas_livre": "..."
}
```

### PadroesCiclo (Atualizado automaticamente)
```python
{
    "fase": "folicular",
    "produtividade_media": 6.2,     # Tarefas/dia
    "foco_medio": 1.0,
    "energia_media": 1.2,           # Multiplicador
    "confianca_score": 0.8,         # 0-1 (baseado em amostras)
    "amostras_usadas": 24,
    "sugestoes": "..."
}
```

## Algoritmo de Pattern Recognition

### 1. Correlação Sono vs Energia
```python
- Separa dias com sono >= média vs < média
- Calcula energia média em cada grupo
- Identifica se diferença é significativa (>1 ponto)
- Gera insight personalizado
```

### 2. Produtividade por Fase do Ciclo
```python
- Agrupa registros por fase menstrual
- Calcula média de tarefas completadas por fase
- Atualiza PadroesCiclo com média móvel
- Score de confiança aumenta com mais amostras (max: 30)
```

### 3. Melhores Horários
```python
- Conta dias com energia >= 7 em cada período
- Compara manhã vs tarde vs noite
- Identifica período com mais alta energia
```

## Fluxo de Uso Recomendado

### Morning Routine:
1. Ao acordar, registrar como foi o sono:
   ```
   POST /api/v2/daily-tracking/record
   { "horas_sono": 7.5, "qualidade_sono": 8 }
   ```

2. Durante o dia, atualizar energia:
   ```
   POST /api/v2/daily-tracking/record
   { "energia_manha": 7, "energia_tarde": 6 }
   ```

3. Fim do dia, registrar produtividade:
   ```
   POST /api/v2/daily-tracking/record
   { "horas_deep_work": 3.5, "notas": "Bom foco hoje" }
   ```

### Weekly Review:
```bash
# Ver análise da semana
GET /api/v2/daily-tracking/analysis?dias=7

# Identificar padrões
GET /api/v2/daily-tracking/patterns

# Receber sugestões
GET /api/v2/daily-tracking/suggestions
```

## Exemplos de Insights Gerados

### Correlação Sono:
```
💡 Insight: Dormir ≥7.5h aumenta significativamente sua energia!
- Com sono ≥7.5h: energia média 8.2/10
- Com sono <7.5h: energia média 5.8/10
```

### Produtividade por Fase:
```
🌸 Produtividade por Fase do Ciclo:
- Folicular: 6.5 tarefas/dia (12 dias)
- Ovulação: 7.2 tarefas/dia (8 dias)
- Lutea: 4.8 tarefas/dia (10 dias)
- Menstrual: 3.2 tarefas/dia (7 dias)
```

### Sugestões Personalizadas:
```
💡 Sugestões de Otimização:

💤 Sono:
- Você está dormindo 6.2h em média (< 7h recomendadas)
- Sugestão: Tente ir para cama 30min mais cedo
- Benefício: Mais energia e foco no dia seguinte

🌸 Adaptação ao Ciclo (Fase folicular):
- Ótimo momento para projetos criativos!
- Planeje novos projetos estratégicos
- Aproveite alta energia para tarefas complexas
```

## Benefícios

✅ **Autoconhecimento**: Entenda seus padrões reais
✅ **Decisões Baseadas em Dados**: Não em suposições
✅ **Otimização Contínua**: Sugestões personalizadas
✅ **Adaptação ao Ciclo**: Planejamento consciente
✅ **ML Básico**: Aprendizado automático de padrões
✅ **Sem Overhead**: Integrado ao fluxo natural

## Próximas Melhorias (Futuro)

- [ ] ML avançado com scikit-learn
- [ ] Predição de energia para próximos dias
- [ ] Alertas proativos via notificações
- [ ] Integração com wearables (sono automático)
- [ ] Dashboard visual de padrões
- [ ] Comparação com benchmarks

---

**Status:** ✅ Implementado e Testado
**Versão:** 1.0
**Branch:** feat/daily-tracking-and-patterns
**Data:** 2025-01-09
