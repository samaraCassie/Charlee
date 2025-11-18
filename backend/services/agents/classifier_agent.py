"""
ClassifierAgent - Intelligent notification classification using LLM.

This agent analyzes incoming notifications and automatically classifies them
using AI, extracting key information and suggesting appropriate actions.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import openai
from sqlalchemy.orm import Session

from database import crud
from database.models import Notification, NotificationPattern, User

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")


class ClassificationResult:
    """Result of notification classification."""

    def __init__(
        self,
        categoria: str,
        prioridade: int,
        intencao: str,
        tom_emocional: str,
        entidades_extraidas: Dict,
        acao_sugerida: str,
        rascunho_resposta: Optional[str],
        contexto: Dict,
        confidence_score: float,
    ):
        self.categoria = categoria
        self.prioridade = prioridade
        self.intencao = intencao
        self.tom_emocional = tom_emocional
        self.entidades_extraidas = entidades_extraidas
        self.acao_sugerida = acao_sugerida
        self.rascunho_resposta = rascunho_resposta
        self.contexto = contexto
        self.confidence_score = confidence_score


class ClassifierAgent:
    """
    Intelligent notification classifier using GPT-4 and embeddings.

    Analyzes notifications to:
    - Classify by urgency and importance
    - Extract entities (people, dates, projects)
    - Detect intent and emotional tone
    - Suggest appropriate actions
    - Generate response drafts
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize classifier agent.

        Args:
            db: Database session
            user_id: User ID for context-aware classification
        """
        self.db = db
        self.user_id = user_id
        self.user = crud.get_user(db, user_id)
        self.model = "gpt-4-turbo-preview"
        self.embedding_model = "text-embedding-3-small"

    def classify_notification(
        self, notification: Notification, user_context: Optional[Dict] = None
    ) -> ClassificationResult:
        """
        Classify a notification using AI.

        Args:
            notification: Notification object to classify
            user_context: Optional context about user's projects, OKRs, etc.

        Returns:
            ClassificationResult with all extracted information
        """
        try:
            # Build classification prompt
            prompt = self._build_classification_prompt(notification, user_context)

            # Call GPT-4 for classification
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                response_format={"type": "json_object"},
            )

            # Parse response
            result_json = json.loads(response.choices[0].message.content)

            # Create ClassificationResult
            return ClassificationResult(
                categoria=result_json.get("categoria", "informativo"),
                prioridade=result_json.get("prioridade", 3),
                intencao=result_json.get("intencao", "informacao"),
                tom_emocional=result_json.get("tom_emocional", "neutro"),
                entidades_extraidas=result_json.get("entidades_extraidas", {}),
                acao_sugerida=result_json.get("acao_sugerida", "arquivar"),
                rascunho_resposta=result_json.get("rascunho_resposta"),
                contexto=result_json.get("contexto", {}),
                confidence_score=result_json.get("confidence_score", 0.8),
            )

        except Exception as e:
            logger.error(f"Error classifying notification {notification.id}: {e}")
            # Return default classification on error
            return self._get_default_classification()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for semantic search.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        try:
            response = openai.embeddings.create(model=self.embedding_model, input=text)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def apply_classification(
        self, notification_id: int, classification: ClassificationResult
    ) -> Notification:
        """
        Apply classification results to a notification.

        Args:
            notification_id: ID of notification to update
            classification: ClassificationResult to apply

        Returns:
            Updated notification
        """
        notification = crud.get_notification(self.db, notification_id, self.user_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        # Update notification with classification results
        notification.categoria = classification.categoria
        notification.prioridade = classification.prioridade
        notification.intencao = classification.intencao
        notification.tom_emocional = classification.tom_emocional
        notification.entidades_extraidas = classification.entidades_extraidas
        notification.acao_sugerida = classification.acao_sugerida
        notification.rascunho_resposta = classification.rascunho_resposta
        notification.contexto = classification.contexto

        # Generate and store embedding
        combined_text = f"{notification.title} {notification.message}"
        embedding = self.generate_embedding(combined_text)
        if embedding:
            notification.embedding = embedding

        self.db.commit()
        self.db.refresh(notification)

        # Learn pattern from this notification
        self._learn_pattern(notification, classification)

        return notification

    def classify_and_apply(
        self, notification_id: int, user_context: Optional[Dict] = None
    ) -> Notification:
        """
        Classify and apply results in one step.

        Args:
            notification_id: ID of notification to classify
            user_context: Optional user context

        Returns:
            Updated notification with classification
        """
        notification = crud.get_notification(self.db, notification_id, self.user_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        classification = self.classify_notification(notification, user_context)
        return self.apply_classification(notification_id, classification)

    def batch_classify(
        self, notification_ids: List[int], user_context: Optional[Dict] = None
    ) -> List[Notification]:
        """
        Classify multiple notifications in batch.

        Args:
            notification_ids: List of notification IDs
            user_context: Optional user context

        Returns:
            List of updated notifications
        """
        results = []
        for notification_id in notification_ids:
            try:
                result = self.classify_and_apply(notification_id, user_context)
                results.append(result)
            except Exception as e:
                logger.error(f"Error batch classifying notification {notification_id}: {e}")
                continue

        return results

    def _build_classification_prompt(
        self, notification: Notification, user_context: Optional[Dict]
    ) -> str:
        """Build prompt for GPT-4 classification."""
        context_str = ""
        if user_context:
            context_str = f"\n\nUser Context:\n{json.dumps(user_context, indent=2)}"

        return f"""
Analyze this notification and classify it:

**Type:** {notification.type}
**Title:** {notification.title}
**Message:** {notification.message}
**Source:** {notification.source.name if notification.source else 'Internal'}
{context_str}

Provide a comprehensive classification in JSON format with these fields:

1. **categoria**: "urgente" | "importante" | "informativo" | "spam"
   - urgente: Requires immediate action (deadline today, critical issue)
   - importante: Significant but not urgent (deadlines this week, important updates)
   - informativo: FYI only (newsletters, updates, notifications)
   - spam: Irrelevant or promotional content

2. **prioridade**: 1-5 (1=lowest, 5=highest)

3. **intencao**: "solicitacao" | "informacao" | "convite" | "cobranca"
   - solicitacao: Someone is asking for something
   - informacao: Sharing information
   - convite: Invitation to event/meeting
   - cobranca: Following up on something pending

4. **tom_emocional**: "neutro" | "urgente" | "amigavel" | "formal"

5. **entidades_extraidas**: {{
     "pessoas": ["names of people mentioned"],
     "datas": ["dates mentioned"],
     "locais": ["locations mentioned"],
     "projetos": ["project names mentioned"],
     "valores": ["monetary amounts mentioned"]
   }}

6. **acao_sugerida**: "responder" | "arquivar" | "criar_tarefa" | "snooze"

7. **contexto**: {{
     "projeto": "related project if identified",
     "tipo": "category of notification",
     "stakeholder": "key person involved"
   }}

8. **rascunho_resposta**: If acao_sugerida is "responder", provide a draft response. Otherwise null.

9. **confidence_score**: 0.0-1.0 indicating confidence in classification

Return ONLY valid JSON, no additional text.
"""

    def _get_system_prompt(self) -> str:
        """Get system prompt for classifier."""
        return """You are an expert AI assistant specializing in notification classification and triage.

Your role is to analyze incoming notifications and help users focus on what matters most.
You understand context, urgency, and intent. You can identify spam, extract key information,
and suggest appropriate actions.

Key principles:
1. Be conservative with "urgente" - only truly time-sensitive items
2. Identify spam aggressively - most notifications are not important
3. Extract entities accurately - people, dates, projects matter
4. Suggest helpful actions - automate when possible
5. Draft responses that are professional and contextual

You output ONLY valid JSON, following the exact schema requested."""

    def _get_default_classification(self) -> ClassificationResult:
        """Get default classification when AI fails."""
        return ClassificationResult(
            categoria="informativo",
            prioridade=3,
            intencao="informacao",
            tom_emocional="neutro",
            entidades_extraidas={},
            acao_sugerida="arquivar",
            rascunho_resposta=None,
            contexto={},
            confidence_score=0.5,
        )

    def _learn_pattern(self, notification: Notification, classification: ClassificationResult):
        """
        Learn patterns from classified notification for future improvements.

        Args:
            notification: Classified notification
            classification: Classification result
        """
        try:
            # Extract pattern key (e.g., sender for emails)
            pattern_key = None
            pattern_type = None

            if notification.type == "email":
                # Extract sender from extra_data or contexto
                sender = notification.contexto.get("stakeholder")
                if sender:
                    pattern_key = f"sender:{sender}"
                    pattern_type = "sender_preference"

            if not pattern_key:
                return

            # Check if pattern exists
            existing_pattern = (
                self.db.query(NotificationPattern)
                .filter_by(user_id=self.user_id, pattern_type=pattern_type, pattern_key=pattern_key)
                .first()
            )

            pattern_data = {
                "typical_action": classification.acao_sugerida,
                "avg_priority": classification.prioridade,
                "typical_category": classification.categoria,
            }

            if existing_pattern:
                # Update existing pattern
                existing_pattern.occurrences += 1
                existing_pattern.pattern_data = pattern_data
                existing_pattern.confidence_score = min(
                    1.0, existing_pattern.confidence_score + 0.1
                )
                existing_pattern.last_occurrence = datetime.now(timezone.utc)
            else:
                # Create new pattern
                new_pattern = NotificationPattern(
                    user_id=self.user_id,
                    pattern_type=pattern_type,
                    pattern_key=pattern_key,
                    pattern_data=pattern_data,
                    confidence_score=0.5,
                    occurrences=1,
                    last_occurrence=datetime.now(timezone.utc),
                )
                self.db.add(new_pattern)

            self.db.commit()

        except Exception as e:
            logger.error(f"Error learning pattern: {e}")
            self.db.rollback()
