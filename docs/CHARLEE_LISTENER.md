# 🎤 Charlee Listener - Módulo de Escuta Ativa e Análise Conversacional

**Versão:** V5.0 (Planejado)
**Status:** 🔴 Não Implementado
**Prioridade:** 🔥 Alta (Recurso Transformacional)
**Dependências:** Calendar (V3.2), Tasks (V1.0), Diplomat (V4.0), Wellness (V2.0)

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Pipeline de Processamento](#3-pipeline-de-processamento)
4. [Detecção de Intenções](#4-detecção-de-intenções)
5. [Análise de Evolução Pessoal](#5-análise-de-evolução-pessoal)
6. [Autonomia e Ações Automáticas](#6-autonomia-e-ações-automáticas)
7. [Privacidade e Segurança](#7-privacidade-e-segurança)
8. [Schemas de Banco de Dados](#8-schemas-de-banco-de-dados)
9. [API Endpoints](#9-api-endpoints)
10. [Integração com Outros Módulos](#10-integração-com-outros-módulos)
11. [Métricas e Analytics](#11-métricas-e-analytics)
12. [Roadmap de Implementação](#12-roadmap-de-implementação)

---

## 1. Visão Geral

### 1.1 Propósito

**Charlee Listener** é o módulo de **escuta ativa contínua** que monitora conversas da usuária via microfone do celular para:

- ✅ **Capturar compromissos automaticamente** (datas, horários, pessoas)
- ✅ **Criar tarefas quando você se comprometer verbalmente**
- ✅ **Analisar sua evolução como "imperatriz graciosa/soberana"**
- ✅ **Detectar lacunas de informação e pesquisar proativamente**
- ✅ **Tomar ações autônomas** sem precisar de confirmação

### 1.2 Problema que Resolve

**Antes do Charlee Listener:**
- 📝 Você precisa **lembrar** de adicionar compromissos na agenda
- 📝 Tarefas combinadas verbalmente **são esquecidas**
- 📝 Você não tem **feedback objetivo** sobre sua comunicação
- 📝 Informações necessárias para planejamento **exigem pesquisa manual**

**Depois do Charlee Listener:**
- ✅ Charlee **escuta e adiciona automaticamente** na agenda
- ✅ Compromissos verbais **viram tarefas** sem você precisar digitar
- ✅ Você recebe **análise semanal** da sua evolução comunicacional
- ✅ Charlee **pesquisa autonomamente** quando detecta lacunas

### 1.3 Exemplo de Uso

**Cenário: Você está conversando com uma amiga**

```
Você: "Adorei a ideia! Vamos marcar um café na terça, 15h?"
Amiga: "Fechado! Vou levar aquele livro que te falei."

[Charlee detecta automaticamente]
✅ Evento criado: "Café com [Nome da Amiga]" - Terça, 15h
✅ Tarefa criada: "Confirmar local do café com [Amiga]" - Hoje, 20h
✅ Nota adicionada no Diplomat: "Ela vai trazer o livro [título detectado]"
✅ Notificação enviada: "Compromisso registrado para terça às 15h"
```

**Cenário: Você está planejando uma viagem**

```
Você: "Quero ir pra Bahia em março, mas não sei se o clima é bom..."

[Charlee detecta lacuna de informação]
✅ Pesquisa realizada: "Clima em Salvador em março"
✅ Resumo enviado: "Março na Bahia: 28-32°C, chance de chuva 40%"
✅ Meta criada: "Planejar viagem para Bahia - Março 2026"
✅ Tarefa criada: "Pesquisar hospedagens em Salvador"
```

---

## 2. Arquitetura do Sistema

### 2.1 Componentes Principais

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHARLEE LISTENER SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Mobile Audio    │────────▶│  Audio Stream    │             │
│  │  Capture Service │         │  Buffer (Redis)  │             │
│  │  (React Native)  │         └──────────────────┘             │
│  └──────────────────┘                  │                        │
│                                        │                        │
│                                        ▼                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Speech-to-Text Pipeline (Whisper)             │  │
│  │  • Streaming transcription                              │  │
│  │  • Speaker diarization (você vs. outras pessoas)        │  │
│  │  • Timestamp marking                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                        │                        │
│                                        ▼                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              NLP Intent Detection Engine                │  │
│  │  • CommitmentDetector (compromissos)                    │  │
│  │  • DateTimeExtractor (datas/horários)                   │  │
│  │  • TaskDetector (tarefas verbalizadas)                  │  │
│  │  • InformationGapDetector (lacunas de info)             │  │
│  │  • PersonalityAnalyzer (tom, postura, "soberania")      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                        │                        │
│                                        ▼                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Autonomous Action Orchestrator                │  │
│  │  • Decide: criar evento, tarefa, pesquisar, etc.        │  │
│  │  • Confidence scoring (agir vs. perguntar)              │  │
│  │  • Event Bus integration                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                        │                        │
│                                        ▼                        │
│  ┌──────────────────┬─────────────────┬──────────────────────┐ │
│  │  Calendar Agent  │  Tasks Agent    │  Web Search Agent    │ │
│  │  (criar eventos) │  (criar tarefas)│  (pesquisar info)    │ │
│  └──────────────────┴─────────────────┴──────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Fluxo de Dados

```python
# backend/modules/listener/pipeline.py

from typing import AsyncGenerator
import asyncio
from openai import AsyncOpenAI
from backend.core.event_bus import EventBus

class AudioTranscriptionPipeline:
    """
    Pipeline de transcrição contínua de áudio
    """

    def __init__(self, openai_client: AsyncOpenAI, event_bus: EventBus):
        self.openai = openai_client
        self.event_bus = event_bus
        self.whisper_model = "whisper-1"  # ou Whisper local para privacidade

    async def process_audio_stream(
        self,
        audio_chunks: AsyncGenerator[bytes, None],
        user_id: str
    ) -> AsyncGenerator[dict, None]:
        """
        Processa stream de áudio do celular em tempo real

        Yields:
            {
                "timestamp": "2025-01-17T14:32:15",
                "speaker": "user" | "other",
                "text": "Vamos marcar um café na terça às 15h",
                "confidence": 0.95,
                "audio_segment_id": "abc123"
            }
        """

        buffer = AudioBuffer()

        async for chunk in audio_chunks:
            buffer.add(chunk)

            # Transcrever quando buffer atingir 5 segundos
            if buffer.duration >= 5.0:
                audio_data = buffer.flush()

                # Transcrição via Whisper
                transcription = await self.openai.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=audio_data,
                    language="pt",
                    response_format="verbose_json",  # timestamps incluídos
                    timestamp_granularities=["segment"]
                )

                # Speaker diarization (simples: volume/timbre)
                speaker = self._identify_speaker(audio_data, transcription)

                result = {
                    "timestamp": transcription.segments[0].start,
                    "speaker": speaker,
                    "text": transcription.text,
                    "confidence": transcription.segments[0].confidence,
                    "audio_segment_id": self._save_audio_segment(audio_data)
                }

                # Emitir evento para análise downstream
                await self.event_bus.emit(
                    "listener.transcription_ready",
                    result
                )

                yield result

    def _identify_speaker(self, audio_data: bytes, transcription) -> str:
        """
        Identifica se é a usuária falando ou outra pessoa

        Futuramente: usar voice fingerprinting
        """
        # Placeholder: análise de volume/timbre
        # TODO: implementar voice recognition para identificar a usuária
        return "user"  # assumir que é a usuária por enquanto

    def _save_audio_segment(self, audio_data: bytes) -> str:
        """
        Salva segmento de áudio criptografado para auditoria
        Retém por 30 dias, depois deleta automaticamente
        """
        # TODO: implementar storage criptografado
        pass
```

---

## 3. Pipeline de Processamento

### 3.1 Real-Time Intent Detection

```python
# backend/modules/listener/intent_detector.py

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.agents.base import Agent

class DetectedIntent(BaseModel):
    """Schema para intenção detectada"""

    intent_type: str  # "commitment", "task", "question", "planning"
    confidence: float  # 0.0 - 1.0
    entities: dict  # entidades extraídas (datas, pessoas, locais, etc.)
    source_text: str
    timestamp: datetime
    suggested_action: dict  # ação que Charlee deve tomar

class CommitmentDetector(Agent):
    """
    Detecta quando você assume compromissos verbalmente
    """

    COMMITMENT_PATTERNS = [
        r"vamos marcar",
        r"vou fazer",
        r"vou entregar",
        r"a gente pode",
        r"combina",
        r"fechado",
        r"tá marcado",
        r"me comprometo",
        r"pode deixar comigo"
    ]

    async def analyze(self, transcription: dict) -> Optional[DetectedIntent]:
        """
        Analisa transcrição para detectar compromissos
        """

        text = transcription["text"].lower()

        # Verificar padrões de compromisso
        if not any(pattern in text for pattern in self.COMMITMENT_PATTERNS):
            return None

        # Usar LLM para extração estruturada
        prompt = f"""
Analise a seguinte fala e extraia TODOS os compromissos assumidos:

Fala: "{transcription['text']}"

Se houver compromisso, retorne JSON:
{{
    "tem_compromisso": true,
    "tipo": "evento_social" | "tarefa_trabalho" | "meta_pessoal",
    "o_que": "descrição do compromisso",
    "quando": "data/horário se mencionado",
    "com_quem": "pessoa(s) envolvida(s)",
    "onde": "local se mencionado",
    "prioridade": "alta" | "média" | "baixa"
}}
"""

        response = await self.run(prompt)
        result = self._parse_json(response)

        if not result.get("tem_compromisso"):
            return None

        # Criar intent estruturado
        return DetectedIntent(
            intent_type="commitment",
            confidence=0.85,
            entities={
                "tipo": result["tipo"],
                "descricao": result["o_que"],
                "data_hora": self._parse_datetime(result.get("quando")),
                "pessoas": result.get("com_quem", []),
                "local": result.get("onde")
            },
            source_text=transcription["text"],
            timestamp=datetime.now(),
            suggested_action={
                "action": "create_calendar_event",
                "params": {
                    "title": result["o_que"],
                    "datetime": self._parse_datetime(result.get("quando")),
                    "attendees": result.get("com_quem", []),
                    "location": result.get("onde")
                }
            }
        )

class InformationGapDetector(Agent):
    """
    Detecta quando você tem dificuldade por falta de informação
    """

    GAP_INDICATORS = [
        r"não sei",
        r"será que",
        r"preciso pesquisar",
        r"não tenho certeza",
        r"como funciona",
        r"quanto custa",
        r"onde fica"
    ]

    async def analyze(self, transcription: dict) -> Optional[DetectedIntent]:
        """
        Detecta lacunas de informação e sugere pesquisa
        """

        text = transcription["text"].lower()

        if not any(indicator in text for indicator in self.GAP_INDICATORS):
            return None

        # Usar LLM para identificar o que pesquisar
        prompt = f"""
A usuária disse: "{transcription['text']}"

Identifique:
1. Qual informação ela precisa?
2. Qual seria uma boa query de busca no Google?
3. Essa informação é crítica para planejamento? (sim/não)

Retorne JSON:
{{
    "informacao_necessaria": "...",
    "google_query": "...",
    "critico": true/false,
    "contexto": "viagem" | "trabalho" | "saude" | "financas" | "geral"
}}
"""

        response = await self.run(prompt)
        result = self._parse_json(response)

        return DetectedIntent(
            intent_type="information_gap",
            confidence=0.80,
            entities={
                "informacao_necessaria": result["informacao_necessaria"],
                "contexto": result["contexto"]
            },
            source_text=transcription["text"],
            timestamp=datetime.now(),
            suggested_action={
                "action": "web_search",
                "params": {
                    "query": result["google_query"],
                    "priority": "high" if result["critico"] else "medium",
                    "deliver_as": "notification"  # enviar resultado via push
                }
            }
        )

class PersonalityAnalyzer(Agent):
    """
    Analisa tom, postura e evolução como "imperatriz graciosa"
    """

    SOVEREIGNTY_INDICATORS = {
        "positivo": [
            "tom_calmo",
            "decisao_clara",
            "limite_estabelecido",
            "gratidao_expressa",
            "delegacao_efetiva",
            "foco_em_solucoes"
        ],
        "negativo": [
            "tom_ansioso",
            "indecisao",
            "justificativa_excessiva",
            "acomodacao_automatica",
            "micro_gerenciamento",
            "foco_em_problemas"
        ]
    }

    async def analyze_sovereignty(
        self,
        transcriptions: List[dict],
        time_window: str = "week"
    ) -> dict:
        """
        Analisa evolução comunicacional ao longo do tempo

        Args:
            transcriptions: Lista de transcrições recentes
            time_window: "day" | "week" | "month"

        Returns:
            {
                "sovereignty_score": 7.5,  # 0-10
                "tendencia": "crescente" | "estável" | "decrescente",
                "padroes_positivos": [...],
                "areas_atencao": [...],
                "insights": "...",
                "exemplos": [...]
            }
        """

        # Compilar todas as falas
        all_text = "\n".join([t["text"] for t in transcriptions])

        prompt = f"""
Analise as seguintes conversas da usuária ao longo da última semana.

Avalie sua evolução como "imperatriz graciosa" / "soberana":

Indicadores POSITIVOS:
- Tom calmo e assertivo
- Decisões claras sem justificativa excessiva
- Estabelecimento de limites saudáveis
- Expressão de gratidão e reconhecimento
- Delegação efetiva
- Foco em soluções (não em problemas)

Indicadores NEGATIVOS:
- Tom ansioso ou hesitante
- Indecisão crônica
- Justificativas excessivas
- Acomodação automática às demandas dos outros
- Micro-gerenciamento
- Foco em problemas

Conversas:
{all_text[:5000]}  # primeiros 5000 chars

Retorne JSON:
{{
    "sovereignty_score": 7.5,
    "tendencia": "crescente",
    "padroes_positivos": ["exemplo1", "exemplo2"],
    "areas_atencao": ["area1", "area2"],
    "insights": "análise qualitativa...",
    "exemplos_soberanos": ["frase que demonstrou soberania"],
    "exemplos_melhorar": ["frase que pode melhorar"]
}}
"""

        response = await self.run(prompt)
        return self._parse_json(response)
```

---

## 4. Detecção de Intenções

### 4.1 Tipos de Intenções Suportadas

| Intent Type | Descrição | Ação Automática | Exemplo |
|-------------|-----------|-----------------|---------|
| **commitment** | Compromisso assumido | Criar evento no Calendar | "Vamos marcar terça às 15h" |
| **task_verbal** | Tarefa verbalizada | Criar tarefa no Tasks | "Preciso ligar pro dentista" |
| **planning** | Planejamento em andamento | Criar meta/projeto | "Quero organizar a viagem em março" |
| **information_gap** | Falta de informação | Pesquisar na web | "Não sei se o clima é bom lá" |
| **relationship_event** | Interação social | Registrar no Diplomat | "Almoço com Joana foi ótimo" |
| **decision_made** | Decisão tomada | Registrar no Context | "Decidi aceitar o projeto" |
| **emotion_expressed** | Emoção verbalizada | Registrar no Wellness | "Estou muito ansiosa hoje" |

### 4.2 Intent Confidence Scoring

```python
# backend/modules/listener/confidence.py

class ConfidenceScorer:
    """
    Calcula confiança para decidir se age automaticamente ou pergunta
    """

    THRESHOLDS = {
        "auto_action": 0.85,      # Agir automaticamente
        "ask_confirmation": 0.60,  # Perguntar antes de agir
        "ignore": 0.30            # Confiança muito baixa, ignorar
    }

    def should_take_action(self, intent: DetectedIntent) -> str:
        """
        Decide se deve agir, perguntar ou ignorar

        Returns:
            "auto" | "confirm" | "ignore"
        """

        if intent.confidence >= self.THRESHOLDS["auto_action"]:
            # Confiança alta: agir automaticamente
            return "auto"

        elif intent.confidence >= self.THRESHOLDS["ask_confirmation"]:
            # Confiança média: perguntar antes
            return "confirm"

        else:
            # Confiança baixa: ignorar
            return "ignore"

    def calculate_confidence(self, intent: DetectedIntent) -> float:
        """
        Calcula confiança baseada em múltiplos fatores
        """

        base_confidence = intent.confidence

        # Boost: entidades extraídas com sucesso
        if "data_hora" in intent.entities and intent.entities["data_hora"]:
            base_confidence += 0.10

        if "pessoas" in intent.entities and intent.entities["pessoas"]:
            base_confidence += 0.05

        # Penalty: ambiguidade temporal
        if "quando" in intent.entities and intent.entities["quando"] == "depois":
            base_confidence -= 0.15

        # Boost: confirmação explícita ("fechado", "combinado")
        if any(word in intent.source_text.lower() for word in ["fechado", "combinado", "ok"]):
            base_confidence += 0.10

        return min(1.0, base_confidence)
```

---

## 5. Análise de Evolução Pessoal

### 5.1 Sovereignty Metrics

```python
# backend/modules/listener/sovereignty.py

from typing import List
from datetime import datetime, timedelta

class SovereigntyTracker:
    """
    Rastreia evolução da usuária como "imperatriz graciosa"
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def generate_weekly_report(self, user_id: str) -> dict:
        """
        Gera relatório semanal de evolução
        """

        # Buscar todas as transcrições da semana
        transcriptions = self.db.execute("""
            SELECT
                text,
                speaker,
                timestamp,
                conversation_context
            FROM listener_transcriptions
            WHERE user_id = %s
              AND speaker = 'user'
              AND timestamp > NOW() - INTERVAL '7 days'
            ORDER BY timestamp ASC
        """, (user_id,)).fetchall()

        # Analisar com PersonalityAnalyzer
        analyzer = PersonalityAnalyzer(self.db)
        analysis = await analyzer.analyze_sovereignty(transcriptions)

        # Calcular métricas comparativas
        previous_week = await self._get_previous_week_score(user_id)

        delta = analysis["sovereignty_score"] - previous_week

        report = {
            "periodo": "Última semana",
            "score_atual": analysis["sovereignty_score"],
            "score_anterior": previous_week,
            "delta": delta,
            "tendencia": analysis["tendencia"],
            "padroes_positivos": analysis["padroes_positivos"],
            "areas_atencao": analysis["areas_atencao"],
            "insights": analysis["insights"],
            "exemplos_destaque": {
                "soberanos": analysis["exemplos_soberanos"][:3],
                "melhorar": analysis["exemplos_melhorar"][:3]
            },
            "recomendacoes": self._generate_recommendations(analysis)
        }

        # Salvar report no banco
        self.db.execute("""
            INSERT INTO listener_sovereignty_reports
            (user_id, periodo, score, delta, analysis_json, criado_em)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            user_id,
            "week",
            analysis["sovereignty_score"],
            delta,
            json.dumps(report)
        ))

        return report

    def _generate_recommendations(self, analysis: dict) -> List[str]:
        """
        Gera recomendações personalizadas baseadas na análise
        """

        recommendations = []

        if "indecisao" in analysis.get("areas_atencao", []):
            recommendations.append(
                "💡 Pratique tomar decisões pequenas rapidamente. "
                "Lembre-se: uma decisão 80% boa HOJE é melhor que "
                "uma decisão 100% perfeita AMANHÃ."
            )

        if "justificativa_excessiva" in analysis.get("areas_atencao", []):
            recommendations.append(
                "👑 Você não precisa justificar suas decisões. "
                "Pratique dizer 'Decidi assim' sem explicações extensas."
            )

        if analysis["sovereignty_score"] >= 8.0:
            recommendations.append(
                "🌟 Você está em excelente forma! Continue assim."
            )

        return recommendations
```

### 5.2 Weekly Sovereignty Report

**Exemplo de relatório enviado à usuária:**

```
┌─────────────────────────────────────────────────────────────────┐
│              📊 RELATÓRIO SEMANAL DE SOBERANIA                  │
│                  10-16 Janeiro 2026                             │
└─────────────────────────────────────────────────────────────────┘

🏆 SOVEREIGNTY SCORE: 8.2/10 (↑ +1.3 vs. semana anterior)

📈 TENDÊNCIA: Crescente ✨

✅ PADRÕES POSITIVOS IDENTIFICADOS:
   • Tom calmo em 87% das conversas
   • Decisões claras sem justificativas excessivas (12 ocorrências)
   • Estabelecimento de limites saudáveis (5 exemplos)
   • Delegação efetiva (3 situações)

⚠️  ÁREAS DE ATENÇÃO:
   • Micro-gerenciamento em contextos de trabalho (2 situações)
   • Acomodação automática em 1 situação familiar

🌟 EXEMPLOS DE SOBERANIA:

   1. "Vou fazer assim. Fechado."
      (Decisão clara, sem justificativa excessiva)

   2. "Não vou conseguir fazer isso agora. Podemos marcar
       para semana que vem?"
      (Limite saudável com alternativa construtiva)

   3. "Pode deixar com a equipe, confio neles."
      (Delegação efetiva)

💡 RECOMENDAÇÕES:

   • Continue praticando delegação - você está indo muito bem!
   • Em contextos familiares, lembre-se que 'não' é uma frase
     completa.

────────────────────────────────────────────────────────────────

Próximo relatório: 17 Janeiro 2026
```

---

## 6. Autonomia e Ações Automáticas

### 6.1 Autonomous Action Orchestrator

```python
# backend/modules/listener/autonomous_actions.py

from typing import Optional
from backend.core.event_bus import EventBus
from backend.modules.calendar.orchestrator import CalendarOrchestrator
from backend.modules.tasks.orchestrator import TasksOrchestrator

class AutonomousActionOrchestrator:
    """
    Orquestra ações autônomas baseadas em intenções detectadas
    """

    def __init__(
        self,
        db_connection,
        event_bus: EventBus,
        calendar: CalendarOrchestrator,
        tasks: TasksOrchestrator,
        web_search_agent
    ):
        self.db = db_connection
        self.event_bus = event_bus
        self.calendar = calendar
        self.tasks = tasks
        self.web_search = web_search_agent
        self.confidence_scorer = ConfidenceScorer()

    async def handle_detected_intent(
        self,
        intent: DetectedIntent,
        user_id: str
    ) -> dict:
        """
        Processa intenção detectada e toma ação apropriada

        Returns:
            {
                "action_taken": "auto" | "confirmation_sent" | "ignored",
                "details": {...}
            }
        """

        # Calcular confiança
        confidence_level = self.confidence_scorer.calculate_confidence(intent)
        action_mode = self.confidence_scorer.should_take_action(intent)

        if action_mode == "ignore":
            return {"action_taken": "ignored", "reason": "low_confidence"}

        # Executar ação baseada no tipo de intent
        if intent.intent_type == "commitment":
            return await self._handle_commitment(intent, user_id, action_mode)

        elif intent.intent_type == "task_verbal":
            return await self._handle_task(intent, user_id, action_mode)

        elif intent.intent_type == "information_gap":
            return await self._handle_information_gap(intent, user_id, action_mode)

        elif intent.intent_type == "planning":
            return await self._handle_planning(intent, user_id, action_mode)

    async def _handle_commitment(
        self,
        intent: DetectedIntent,
        user_id: str,
        mode: str
    ) -> dict:
        """
        Trata compromisso detectado
        """

        if mode == "auto":
            # Criar evento automaticamente
            event = await self.calendar.create_event(
                user_id=user_id,
                title=intent.entities["descricao"],
                start_time=intent.entities.get("data_hora"),
                attendees=intent.entities.get("pessoas", []),
                location=intent.entities.get("local"),
                source="listener_auto"
            )

            # Enviar notificação confirmando
            await self._send_notification(
                user_id,
                f"✅ Compromisso adicionado: {intent.entities['descricao']} "
                f"em {self._format_datetime(intent.entities.get('data_hora'))}"
            )

            # Emitir evento
            await self.event_bus.emit("listener.commitment_created", {
                "user_id": user_id,
                "intent": intent.dict(),
                "event_id": event.id,
                "auto_created": True
            })

            return {
                "action_taken": "auto",
                "details": {"event_id": event.id}
            }

        else:  # mode == "confirm"
            # Enviar para confirmação
            await self._send_confirmation_request(
                user_id,
                intent,
                action_type="create_calendar_event"
            )

            return {
                "action_taken": "confirmation_sent",
                "details": {"intent_id": intent.id}
            }

    async def _handle_information_gap(
        self,
        intent: DetectedIntent,
        user_id: str,
        mode: str
    ) -> dict:
        """
        Trata lacuna de informação detectada
        """

        # Informação sempre é pesquisada automaticamente
        # (baixo risco de erro)

        query = intent.suggested_action["params"]["query"]

        # Pesquisar na web
        search_results = await self.web_search.search(query, num_results=3)

        # Sintetizar resposta
        summary = await self.web_search.summarize(search_results)

        # Enviar via notificação
        await self._send_notification(
            user_id,
            f"🔍 Pesquisei sobre: {intent.entities['informacao_necessaria']}\n\n"
            f"{summary}\n\n"
            f"Fontes: {', '.join([r['url'] for r in search_results])}"
        )

        # Salvar no banco para referência futura
        self.db.execute("""
            INSERT INTO listener_searches
            (user_id, query, results_json, criado_em)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, query, json.dumps(search_results)))

        return {
            "action_taken": "auto",
            "details": {
                "query": query,
                "results_count": len(search_results)
            }
        }
```

### 6.2 Action Confidence Rules

**Regras para decidir quando agir automaticamente:**

| Situação | Confidence Threshold | Ação |
|----------|---------------------|------|
| Data/hora explícita + pessoa conhecida | ≥ 0.90 | ✅ Criar evento automaticamente |
| Data vaga ("depois", "semana que vem") | 0.60-0.80 | ⚠️ Perguntar antes de criar |
| Tarefa simples ("ligar pro dentista") | ≥ 0.85 | ✅ Criar tarefa automaticamente |
| Pesquisa web | Sempre | ✅ Pesquisar automaticamente |
| Decisão financeira | Nunca | ⛔ SEMPRE perguntar |
| Envio de mensagem para terceiros | Nunca | ⛔ SEMPRE perguntar |

---

## 7. Privacidade e Segurança

### 7.1 Políticas de Retenção

```python
# backend/modules/listener/privacy.py

from datetime import datetime, timedelta

class PrivacyManager:
    """
    Gerencia privacidade e retenção de dados de áudio/transcrição
    """

    RETENTION_POLICIES = {
        "audio_raw": timedelta(days=7),        # Áudio bruto: 7 dias
        "transcriptions": timedelta(days=90),  # Transcrições: 90 dias
        "sovereignty_analysis": None,          # Análises: permanente (anonimizadas)
        "detected_intents": timedelta(days=180)  # Intenções: 180 dias
    }

    def __init__(self, db_connection):
        self.db = db_connection

    async def cleanup_expired_data(self):
        """
        Remove dados expirados automaticamente
        """

        # Deletar áudio bruto > 7 dias
        self.db.execute("""
            DELETE FROM listener_audio_segments
            WHERE criado_em < NOW() - INTERVAL '7 days'
        """)

        # Deletar transcrições > 90 dias
        self.db.execute("""
            DELETE FROM listener_transcriptions
            WHERE criado_em < NOW() - INTERVAL '90 days'
        """)

        # Anonimizar análises de soberania (manter métricas, remover texto)
        self.db.execute("""
            UPDATE listener_sovereignty_reports
            SET analysis_json = jsonb_set(
                analysis_json,
                '{exemplos_soberanos}',
                '[]'::jsonb
            )
            WHERE criado_em < NOW() - INTERVAL '90 days'
        """)

    def should_record_conversation(self, context: dict) -> bool:
        """
        Decide se deve gravar conversa baseado em contexto

        NÃO GRAVAR:
        - Conversas médicas sensíveis
        - Conversas com advogados (privileged)
        - Terapia
        - Situações marcadas como "privado"
        """

        # Verificar se usuária ativou "modo privado"
        if context.get("privacy_mode_active"):
            return False

        # Verificar contexto sensível
        sensitive_keywords = [
            "terapeuta", "psicólogo", "advogado",
            "médico", "exame", "sintoma"
        ]

        if any(kw in context.get("location", "").lower() for kw in sensitive_keywords):
            return False

        return True
```

### 7.2 Criptografia e Storage

```python
# backend/modules/listener/encryption.py

from cryptography.fernet import Fernet
import os

class AudioEncryption:
    """
    Criptografa segmentos de áudio antes de armazenar
    """

    def __init__(self):
        # Chave de criptografia (deve estar em variável de ambiente)
        self.key = os.getenv("AUDIO_ENCRYPTION_KEY").encode()
        self.cipher = Fernet(self.key)

    def encrypt_audio(self, audio_data: bytes) -> bytes:
        """Criptografa áudio bruto"""
        return self.cipher.encrypt(audio_data)

    def decrypt_audio(self, encrypted_data: bytes) -> bytes:
        """Descriptografa áudio para reprodução (apenas admin)"""
        return self.cipher.decrypt(encrypted_data)

    def store_encrypted_segment(
        self,
        audio_data: bytes,
        user_id: str,
        metadata: dict
    ) -> str:
        """
        Armazena segmento de áudio criptografado

        Returns:
            segment_id
        """

        encrypted = self.encrypt_audio(audio_data)

        # Salvar em storage seguro (S3 com SSE, ou local)
        segment_id = f"{user_id}_{datetime.now().timestamp()}"

        # Placeholder: salvar no filesystem
        # TODO: migrar para S3 com encryption at rest
        storage_path = f"/secure_storage/audio/{segment_id}.enc"

        with open(storage_path, "wb") as f:
            f.write(encrypted)

        # Registrar no banco (sem o áudio)
        self.db.execute("""
            INSERT INTO listener_audio_segments
            (segment_id, user_id, storage_path, metadata, criado_em)
            VALUES (%s, %s, %s, %s, NOW())
        """, (segment_id, user_id, storage_path, json.dumps(metadata)))

        return segment_id
```

### 7.3 Controle de Acesso

```python
# backend/modules/listener/access_control.py

class ListenerAccessControl:
    """
    Define quem pode acessar dados do Listener
    """

    PERMISSIONS = {
        "view_transcriptions": ["user", "admin"],
        "view_audio_raw": ["admin"],  # APENAS admin
        "view_sovereignty_reports": ["user", "admin"],
        "delete_data": ["user", "admin"],
        "export_data": ["user", "admin"]
    }

    def can_access_audio_raw(self, requesting_user_id: str, target_user_id: str) -> bool:
        """
        Áudio bruto NUNCA é acessível via API pública
        Apenas para debugging de admin
        """

        # Verificar se é admin
        is_admin = self._is_admin(requesting_user_id)

        # Verificar se é a própria usuária
        is_owner = requesting_user_id == target_user_id

        return is_admin and is_owner

    def can_access_transcriptions(self, requesting_user_id: str, target_user_id: str) -> bool:
        """
        Transcrições são acessíveis pela própria usuária
        """
        return requesting_user_id == target_user_id
```

---

## 8. Schemas de Banco de Dados

### 8.1 Tabela: `listener_transcriptions`

```sql
CREATE TABLE listener_transcriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    -- Dados da transcrição
    text TEXT NOT NULL,
    speaker VARCHAR(20) NOT NULL,  -- 'user' | 'other' | 'unknown'
    confidence DECIMAL(3,2),

    -- Temporal
    timestamp TIMESTAMP NOT NULL,
    audio_segment_id VARCHAR(255),  -- referência ao áudio criptografado

    -- Contexto
    conversation_context JSONB,  -- {location, people_present, activity}

    -- Metadata
    criado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_speaker (speaker)
);
```

### 8.2 Tabela: `listener_detected_intents`

```sql
CREATE TABLE listener_detected_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),
    transcription_id UUID REFERENCES listener_transcriptions(id),

    -- Intent detectado
    intent_type VARCHAR(50) NOT NULL,  -- 'commitment', 'task_verbal', etc.
    confidence DECIMAL(3,2) NOT NULL,

    -- Entidades extraídas
    entities JSONB NOT NULL,  -- {data_hora, pessoas, local, descricao, etc.}

    -- Ação sugerida
    suggested_action JSONB NOT NULL,  -- {action, params}

    -- Resultado
    action_taken VARCHAR(20),  -- 'auto' | 'confirm' | 'ignored'
    resulting_event_id UUID,  -- ID do evento/tarefa criado

    criado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_intent_type (user_id, intent_type),
    INDEX idx_action_taken (action_taken)
);
```

### 8.3 Tabela: `listener_sovereignty_reports`

```sql
CREATE TABLE listener_sovereignty_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    -- Período analisado
    periodo VARCHAR(20) NOT NULL,  -- 'day' | 'week' | 'month'
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,

    -- Métricas
    score DECIMAL(3,1) NOT NULL,  -- 0.0 - 10.0
    delta DECIMAL(3,1),  -- diferença vs. período anterior

    -- Análise completa (JSON)
    analysis_json JSONB NOT NULL,

    criado_em TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_periodo (user_id, periodo, data_fim)
);
```

### 8.4 Tabela: `listener_audio_segments`

```sql
CREATE TABLE listener_audio_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),

    segment_id VARCHAR(255) UNIQUE NOT NULL,
    storage_path TEXT NOT NULL,  -- caminho do arquivo criptografado

    -- Metadata
    metadata JSONB,  -- {duration, format, sample_rate}

    -- Retenção
    criado_em TIMESTAMP DEFAULT NOW(),
    expira_em TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',

    INDEX idx_expiration (expira_em)
);
```

---

## 9. API Endpoints

### 9.1 Audio Streaming

```python
# backend/modules/listener/routes.py

from fastapi import APIRouter, WebSocket, Depends
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/listener", tags=["Listener"])

@router.websocket("/stream")
async def audio_stream(
    websocket: WebSocket,
    user_id: str = Depends(get_current_user)
):
    """
    WebSocket para streaming de áudio do celular

    Cliente (React Native) envia chunks de áudio
    Servidor retorna transcrições + ações tomadas
    """

    await websocket.accept()

    pipeline = AudioTranscriptionPipeline(openai_client, event_bus)
    orchestrator = AutonomousActionOrchestrator(db, event_bus, calendar, tasks, web_search)

    try:
        async def audio_generator():
            while True:
                # Receber chunk de áudio do cliente
                audio_chunk = await websocket.receive_bytes()
                yield audio_chunk

        # Processar stream
        async for transcription in pipeline.process_audio_stream(audio_generator(), user_id):

            # Enviar transcrição de volta para o cliente
            await websocket.send_json({
                "type": "transcription",
                "data": transcription
            })

            # Detectar intenções
            detectors = [
                CommitmentDetector(db),
                InformationGapDetector(db),
                TaskDetector(db)
            ]

            for detector in detectors:
                intent = await detector.analyze(transcription)

                if intent:
                    # Processar intenção
                    result = await orchestrator.handle_detected_intent(intent, user_id)

                    # Enviar resultado para o cliente
                    await websocket.send_json({
                        "type": "action_taken",
                        "data": result
                    })

    except Exception as e:
        logger.error(f"Error in audio stream: {e}")
        await websocket.close()
```

### 9.2 Sovereignty Reports

```python
@router.get("/sovereignty/reports")
async def get_sovereignty_reports(
    periodo: str = "week",
    user_id: str = Depends(get_current_user)
):
    """
    Retorna relatórios de evolução de soberania
    """

    tracker = SovereigntyTracker(db)

    if periodo == "week":
        report = await tracker.generate_weekly_report(user_id)
    elif periodo == "month":
        report = await tracker.generate_monthly_report(user_id)
    else:
        raise HTTPException(400, "Período inválido")

    return report

@router.get("/sovereignty/score/current")
async def get_current_sovereignty_score(
    user_id: str = Depends(get_current_user)
):
    """
    Retorna score de soberania atual (últimas 24h)
    """

    tracker = SovereigntyTracker(db)
    score = await tracker.get_current_score(user_id)

    return {
        "score": score,
        "last_updated": datetime.now(),
        "tendencia": await tracker.get_trend(user_id)
    }
```

### 9.3 Privacy Controls

```python
@router.post("/privacy/toggle")
async def toggle_privacy_mode(
    enabled: bool,
    user_id: str = Depends(get_current_user)
):
    """
    Ativa/desativa modo privado (para de gravar temporariamente)
    """

    db.execute("""
        UPDATE usuarios
        SET listener_privacy_mode = %s
        WHERE id = %s
    """, (enabled, user_id))

    return {"privacy_mode_active": enabled}

@router.delete("/data/transcriptions")
async def delete_all_transcriptions(
    user_id: str = Depends(get_current_user)
):
    """
    Deleta TODAS as transcrições da usuária
    (irreversível, para compliance GDPR)
    """

    db.execute("""
        DELETE FROM listener_transcriptions
        WHERE user_id = %s
    """, (user_id,))

    db.execute("""
        DELETE FROM listener_audio_segments
        WHERE user_id = %s
    """, (user_id,))

    return {"deleted": True}
```

---

## 10. Integração com Outros Módulos

### 10.1 Listener → Calendar Integration

```python
# backend/modules/listener/integrations/calendar.py

class ListenerCalendarIntegration:
    """
    Integração entre Listener e Calendar
    """

    def __init__(self, event_bus: EventBus, calendar: CalendarOrchestrator):
        self.event_bus = event_bus
        self.calendar = calendar

        # Subscribe to listener events
        self.event_bus.subscribe(
            "listener.commitment_created",
            self.on_commitment_created
        )

    async def on_commitment_created(self, event_data: dict):
        """
        Quando compromisso é detectado, criar evento no Calendar
        """

        intent = event_data["intent"]
        user_id = event_data["user_id"]

        # Criar evento
        calendar_event = await self.calendar.create_event(
            user_id=user_id,
            title=intent["entities"]["descricao"],
            start_time=intent["entities"]["data_hora"],
            attendees=intent["entities"].get("pessoas", []),
            location=intent["entities"].get("local"),
            source="listener",
            metadata={
                "transcription_id": intent.get("transcription_id"),
                "confidence": intent["confidence"]
            }
        )

        # Emitir evento de confirmação
        await self.event_bus.emit("calendar.event_created_by_listener", {
            "event_id": calendar_event.id,
            "user_id": user_id,
            "source_intent": intent
        })
```

### 10.2 Listener → Diplomat Integration

```python
# backend/modules/listener/integrations/diplomat.py

class ListenerDiplomatIntegration:
    """
    Integração entre Listener e Diplomat
    Registra interações sociais automaticamente
    """

    def __init__(self, event_bus: EventBus, diplomat: DiplomatOrchestrator):
        self.event_bus = event_bus
        self.diplomat = diplomat

        self.event_bus.subscribe(
            "listener.transcription_ready",
            self.on_transcription_ready
        )

    async def on_transcription_ready(self, transcription: dict):
        """
        Analisa transcrição para detectar interações sociais
        """

        # Detectar se está conversando com alguém conhecido
        detector = RelationshipInteractionDetector(db)
        interaction = await detector.analyze(transcription)

        if not interaction:
            return

        # Registrar no Diplomat
        await self.diplomat.log_interaction(
            user_id=transcription["user_id"],
            pessoa_id=interaction["pessoa_id"],
            tipo="conversa_presencial",
            qualidade=interaction["qualidade"],  # "positiva" | "neutra" | "negativa"
            topicos=interaction["topicos"],
            timestamp=transcription["timestamp"],
            metadata={
                "transcription_id": transcription["id"],
                "duracao_estimada": interaction["duracao"]
            }
        )

        # Emitir evento
        await self.event_bus.emit("diplomat.interaction_logged_by_listener", {
            "pessoa_id": interaction["pessoa_id"],
            "qualidade": interaction["qualidade"]
        })
```

### 10.3 Listener → Wellness Integration

```python
# backend/modules/listener/integrations/wellness.py

class ListenerWellnessIntegration:
    """
    Integração entre Listener e Wellness
    Detecta estado emocional via tom de voz e conteúdo
    """

    def __init__(self, event_bus: EventBus, wellness: WellnessCoachAgent):
        self.event_bus = event_bus
        self.wellness = wellness

        self.event_bus.subscribe(
            "listener.transcription_ready",
            self.analyze_emotional_state
        )

    async def analyze_emotional_state(self, transcription: dict):
        """
        Analisa estado emocional pela fala
        """

        # Usar LLM para detectar emoções
        detector = EmotionDetector(db)
        emotion = await detector.analyze(transcription["text"])

        if emotion["intensidade"] < 0.5:
            return  # Emoção não significativa

        # Registrar no Wellness
        await self.wellness.log_emotional_state(
            user_id=transcription["user_id"],
            emocao=emotion["tipo"],  # "ansiedade", "frustração", "alegria", etc.
            intensidade=emotion["intensidade"],
            gatilho=emotion.get("gatilho"),
            timestamp=transcription["timestamp"],
            fonte="listener"
        )

        # Se detectar ansiedade/stress alto, enviar alerta
        if emotion["tipo"] in ["ansiedade", "stress"] and emotion["intensidade"] > 0.7:
            await self.event_bus.emit("wellness.high_stress_detected", {
                "user_id": transcription["user_id"],
                "intensidade": emotion["intensidade"],
                "fonte": "voice_analysis"
            })
```

---

## 11. Métricas e Analytics

### 11.1 Listener Metrics Dashboard

```python
# backend/modules/listener/analytics.py

class ListenerAnalytics:
    """
    Métricas de uso e eficácia do Listener
    """

    def __init__(self, db_connection):
        self.db = db_connection

    async def get_metrics(self, user_id: str, periodo: str = "week") -> dict:
        """
        Retorna métricas de uso do Listener
        """

        if periodo == "week":
            interval = "7 days"
        elif periodo == "month":
            interval = "30 days"
        else:
            interval = "1 day"

        # Total de transcrições
        total_transcriptions = self.db.execute(f"""
            SELECT COUNT(*) as count
            FROM listener_transcriptions
            WHERE user_id = %s
              AND timestamp > NOW() - INTERVAL '{interval}'
        """, (user_id,)).fetchone()["count"]

        # Compromissos detectados
        commitments_detected = self.db.execute(f"""
            SELECT COUNT(*) as count
            FROM listener_detected_intents
            WHERE user_id = %s
              AND intent_type = 'commitment'
              AND criado_em > NOW() - INTERVAL '{interval}'
        """, (user_id,)).fetchone()["count"]

        # Ações autônomas tomadas
        autonomous_actions = self.db.execute(f"""
            SELECT COUNT(*) as count
            FROM listener_detected_intents
            WHERE user_id = %s
              AND action_taken = 'auto'
              AND criado_em > NOW() - INTERVAL '{interval}'
        """, (user_id,)).fetchone()["count"]

        # Pesquisas realizadas
        searches_performed = self.db.execute(f"""
            SELECT COUNT(*) as count
            FROM listener_searches
            WHERE user_id = %s
              AND criado_em > NOW() - INTERVAL '{interval}'
        """, (user_id,)).fetchone()["count"]

        # Sovereignty score médio
        avg_sovereignty = self.db.execute(f"""
            SELECT AVG(score) as avg_score
            FROM listener_sovereignty_reports
            WHERE user_id = %s
              AND criado_em > NOW() - INTERVAL '{interval}'
        """, (user_id,)).fetchone()["avg_score"]

        return {
            "periodo": periodo,
            "total_transcriptions": total_transcriptions,
            "commitments_detected": commitments_detected,
            "autonomous_actions": autonomous_actions,
            "searches_performed": searches_performed,
            "avg_sovereignty_score": float(avg_sovereignty or 0),
            "time_saved_estimate": self._estimate_time_saved(
                commitments_detected,
                searches_performed
            )
        }

    def _estimate_time_saved(
        self,
        commitments: int,
        searches: int
    ) -> int:
        """
        Estima tempo economizado (em minutos)
        """

        # Assumindo:
        # - Cada compromisso manual leva ~2 min para adicionar
        # - Cada pesquisa manual leva ~5 min

        time_saved = (commitments * 2) + (searches * 5)
        return time_saved
```

### 11.2 Exemplo de Métricas

```json
{
    "periodo": "week",
    "total_transcriptions": 1247,
    "commitments_detected": 8,
    "autonomous_actions": 15,
    "searches_performed": 6,
    "avg_sovereignty_score": 8.2,
    "time_saved_estimate": 46,
    "breakdown": {
        "commitments_by_type": {
            "evento_social": 5,
            "tarefa_trabalho": 2,
            "meta_pessoal": 1
        },
        "searches_by_context": {
            "viagem": 3,
            "trabalho": 2,
            "saude": 1
        },
        "sovereignty_evolution": [
            {"dia": "2025-01-10", "score": 7.8},
            {"dia": "2025-01-11", "score": 8.1},
            {"dia": "2025-01-12", "score": 8.3},
            {"dia": "2025-01-13", "score": 8.5},
            {"dia": "2025-01-14", "score": 8.2},
            {"dia": "2025-01-15", "score": 8.0},
            {"dia": "2025-01-16", "score": 8.4}
        ]
    }
}
```

---

## 12. Roadmap de Implementação

### 12.1 Fase 1: MVP (2-3 meses)

**Objetivo:** Transcrição básica + detecção de compromissos

✅ **Componentes:**
- [ ] Audio streaming via WebSocket (React Native → Backend)
- [ ] Integração com Whisper API para transcrição
- [ ] CommitmentDetector básico (padrões regex + LLM)
- [ ] DateTimeExtractor para datas/horários
- [ ] Criação automática de eventos no Calendar
- [ ] Notificações push quando ação é tomada

🎯 **Critério de Sucesso:**
- 80%+ de compromissos detectados corretamente
- <10% de falsos positivos
- Latência <5 segundos entre fala → evento criado

### 12.2 Fase 2: Análise de Soberania (1-2 meses)

✅ **Componentes:**
- [ ] PersonalityAnalyzer com indicadores de soberania
- [ ] SovereigntyTracker com relatórios semanais
- [ ] Speaker diarization (você vs. outras pessoas)
- [ ] Análise de tom/emoção via prosódia

🎯 **Critério de Sucesso:**
- Relatórios semanais gerados automaticamente
- Exemplos concretos de falas "soberanas" e "a melhorar"
- Correlação entre sovereignty score e bem-estar geral

### 12.3 Fase 3: Autonomia Avançada (2 meses)

✅ **Componentes:**
- [ ] InformationGapDetector + Web Search Agent
- [ ] TaskDetector para tarefas verbalizadas
- [ ] Integração com Diplomat (registro automático de interações)
- [ ] Integração com Wellness (detecção emocional)
- [ ] Confidence scoring adaptativo (aprende com feedback)

🎯 **Critério de Sucesso:**
- 90%+ de ações autônomas aceitas pela usuária
- <5% de ações que precisam ser revertidas
- 30+ minutos economizados por semana

### 12.4 Fase 4: Privacidade & Compliance (1 mês)

✅ **Componentes:**
- [ ] Criptografia end-to-end para áudio
- [ ] Auto-deleção de dados expirados
- [ ] Modo privado (pause recording)
- [ ] Exportação de dados (GDPR compliance)
- [ ] Auditoria de acessos

🎯 **Critério de Sucesso:**
- Compliance total com LGPD/GDPR
- Auditoria de segurança externa aprovada
- Zero vazamentos de dados

---

## 13. Considerações Finais

### 13.1 Challenges Técnicos

**1. Battery Consumption**
- Áudio contínuo consome muita bateria
- **Solução:** Usar VAD (Voice Activity Detection) para gravar apenas quando há fala

**2. Network Bandwidth**
- Streaming de áudio contínuo consome dados
- **Solução:** Compressão Opus, buffer local, upload em WiFi

**3. Accuracy em Ambientes Ruidosos**
- Cafés, rua, etc. degradam transcrição
- **Solução:** Noise cancellation via ML, múltiplos microfones

**4. Privacy Concerns**
- Gravação contínua é sensível
- **Solução:** Transparência total, controles granulares, criptografia

### 13.2 Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Falsos positivos criando eventos errados | Alto | Média | Confidence scoring + confirmação para baixa confiança |
| Vazamento de áudio sensível | Crítico | Baixa | Criptografia E2E + retenção curta + auditoria |
| Battery drain afastando usuários | Alto | Alta | VAD + processamento local + otimização |
| Accuracy baixa em PT-BR | Médio | Média | Fine-tuning Whisper + feedback loop |

### 13.3 Métricas de Sucesso (OKRs)

**Objetivo 1:** Charlee se torna assistente proativo indispensável

- **KR1:** 80% dos compromissos verbais são capturados automaticamente
- **KR2:** 30+ minutos/semana economizados via ações autônomas
- **KR3:** NPS ≥ 9/10 para feature de Listener

**Objetivo 2:** Usuária evolui como "imperatriz graciosa"

- **KR1:** Sovereignty score aumenta 15% em 3 meses
- **KR2:** 80% das usuárias reportam maior autoconsciência comunicacional
- **KR3:** Redução de 30% em padrões de "justificativa excessiva"

---

## 14. Conclusão

**Charlee Listener** representa o próximo nível de assistência proativa:

✨ **Captura automática** de compromissos e tarefas
✨ **Análise objetiva** de evolução pessoal como "soberana"
✨ **Autonomia inteligente** para pesquisar e agir sem fricção
✨ **Privacidade robusta** com criptografia e controles granulares

Este módulo transforma Charlee de um **assistente reativo** (você pede, ele faz) em um **parceiro proativo** (ele antecipa, aprende e age).

**Próximos passos:**
1. Validar arquitetura técnica (especialmente battery/bandwidth)
2. Implementar MVP (Fase 1)
3. Testar com usuária real (você) por 30 dias
4. Iterar baseado em feedback
5. Escalar para Fase 2-4

---

**Versão:** 1.0
**Última atualização:** 17 Janeiro 2025
**Autor:** Charlee Development Team
**Status:** 🔴 Planejamento (V5.0)
