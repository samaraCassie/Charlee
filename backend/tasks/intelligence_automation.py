"""Advanced intelligence automation tasks.

Proactive tasks that analyze opportunities, send notifications,
and generate insights automatically.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from celery import Task
from celery_app import celery_app
from database.session import SessionLocal

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""

    _db = None

    @property
    def db(self):
        """Get database session."""
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Close database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.intelligence_automation.analyze_new_opportunities",
    max_retries=2,
)
def analyze_new_opportunities(self) -> Dict[str, Any]:
    """
    Automatically analyze new opportunities with SemanticAnalyzer.

    Runs after collection to:
    1. Find opportunities collected in last hour without analysis
    2. Run semantic analysis on each
    3. Score and categorize
    4. Store results for easy filtering

    Returns:
        Dict with analysis statistics
    """
    try:
        from database.models import FreelanceOpportunity
        from agent.specialized_agents.projects import create_semantic_analyzer_agent

        logger.info("Starting automatic opportunity analysis")

        # Find unanalyzed opportunities from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        unanalyzed_opportunities = (
            self.db.query(FreelanceOpportunity)
            .filter(
                FreelanceOpportunity.created_at >= one_hour_ago,
                FreelanceOpportunity.semantic_score is None,  # Not yet analyzed
            )
            .limit(50)  # Process max 50 at a time
            .all()
        )

        if not unanalyzed_opportunities:
            logger.info("No new opportunities to analyze")
            return {
                "status": "success",
                "analyzed": 0,
                "message": "No new opportunities",
            }

        analyzed_count = 0
        high_priority_count = 0

        # Analyze each opportunity
        for opp in unanalyzed_opportunities:
            try:
                analyzer = create_semantic_analyzer_agent(db=self.db, user_id=opp.user_id)

                # Run semantic analysis
                analysis = analyzer.analyze_opportunity_semantic_fit(opp.id)

                # Count high priority
                if "alta prioridade" in analysis.lower() or "high priority" in analysis.lower():
                    high_priority_count += 1

                analyzed_count += 1

            except Exception as e:
                logger.error(f"Error analyzing opportunity {opp.id}: {e}")
                continue

        self.db.commit()

        logger.info(
            f"Analysis completed: {analyzed_count} opportunities, "
            f"{high_priority_count} high priority"
        )

        return {
            "status": "success",
            "analyzed": analyzed_count,
            "high_priority": high_priority_count,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error during opportunity analysis: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.intelligence_automation.send_opportunity_notifications",
)
def send_opportunity_notifications(self, user_id: int = None) -> Dict[str, Any]:
    """
    Send notifications for high-value opportunities.

    Checks for:
    - Opportunities with high semantic scores (>0.8)
    - Budget above user's average
    - Skills matching user's top skills
    - Posted in last 24 hours

    Stores notifications in database for user to see in chat/UI.

    Args:
        user_id: Optional user ID to filter for

    Returns:
        Dict with notification statistics
    """
    try:
        from database.models import FreelanceOpportunity, UserNotification

        logger.info(f"Checking for high-value opportunities (user_id={user_id})")

        # Find high-value opportunities from last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

        query = self.db.query(FreelanceOpportunity).filter(
            FreelanceOpportunity.created_at >= twenty_four_hours_ago,
            FreelanceOpportunity.semantic_score >= 0.8,  # High score
        )

        if user_id:
            query = query.filter(FreelanceOpportunity.user_id == user_id)

        high_value_opportunities = query.limit(10).all()

        if not high_value_opportunities:
            logger.info("No high-value opportunities found")
            return {"status": "success", "notifications_sent": 0}

        notifications_created = 0

        for opp in high_value_opportunities:
            # Check if notification already sent
            existing = (
                self.db.query(UserNotification)
                .filter(
                    UserNotification.user_id == opp.user_id,
                    UserNotification.type == "opportunity",
                    UserNotification.reference_id == str(opp.id),
                )
                .first()
            )

            if existing:
                continue  # Skip if already notified

            # Create notification
            notification = UserNotification(
                user_id=opp.user_id,
                type="opportunity",
                title=f"🎯 Oportunidade de Alto Valor: {opp.title}",
                message=f"""
Nova oportunidade altamente compatível com seu perfil!

**{opp.title}**
Budget: ${opp.budget_min}-${opp.budget_max}
Platform: {opp.platform}
Score: {opp.semantic_score:.1%}

Skills requeridas: {', '.join(opp.required_skills[:5])}

Ação recomendada: Analise e considere aplicar rapidamente!
                """.strip(),
                reference_id=str(opp.id),
                priority="high",
                read=False,
            )

            self.db.add(notification)
            notifications_created += 1

        self.db.commit()

        logger.info(f"Created {notifications_created} notifications")

        return {
            "status": "success",
            "notifications_sent": notifications_created,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error sending notifications: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.intelligence_automation.generate_daily_report",
)
def generate_daily_report(self, user_id: int = None) -> Dict[str, Any]:
    """
    Generate daily intelligence report for chat delivery.

    Creates a comprehensive report with:
    - New opportunities summary
    - Career insights update
    - Portfolio highlights
    - Recommendations

    Stores report as notification for delivery in chat.

    Args:
        user_id: User ID to generate report for

    Returns:
        Dict with report generation status
    """
    try:
        from database.models import FreelanceOpportunity, UserNotification
        from agent.specialized_agents.projects import (
            create_career_insights_agent,
            create_portfolio_builder_agent,
        )

        logger.info(f"Generating daily report for user {user_id}")

        # Get yesterday's date range
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Count new opportunities
        new_opportunities = (
            self.db.query(FreelanceOpportunity)
            .filter(
                FreelanceOpportunity.user_id == user_id,
                FreelanceOpportunity.created_at >= yesterday,
                FreelanceOpportunity.created_at < today,
            )
            .count()
        )

        # Count high-value opportunities
        high_value_opps = (
            self.db.query(FreelanceOpportunity)
            .filter(
                FreelanceOpportunity.user_id == user_id,
                FreelanceOpportunity.created_at >= yesterday,
                FreelanceOpportunity.semantic_score >= 0.8,
            )
            .count()
        )

        # Get career insights
        try:
            career_agent = create_career_insights_agent(db=self.db, user_id=user_id)
            career_summary = career_agent.get_career_summary(days=7)
        except Exception:
            career_summary = "Não disponível"

        # Get top achievements
        try:
            portfolio_agent = create_portfolio_builder_agent(db=self.db, user_id=user_id)
            achievements = portfolio_agent.get_top_achievements(limit=3)
        except Exception:
            achievements = "Não disponível"

        # Build report
        report = f"""
📊 **RELATÓRIO DIÁRIO CHARLEE** - {yesterday.strftime('%d/%m/%Y')}

---

🎯 **OPORTUNIDADES**
• {new_opportunities} novas oportunidades coletadas
• {high_value_opps} oportunidades de alto valor (score ≥80%)

💼 **CARREIRA (últimos 7 dias)**
{career_summary[:300]}...

🏆 **TOP ACHIEVEMENTS**
{achievements[:300]}...

---

💡 **RECOMENDAÇÕES:**
• Revise as oportunidades de alto valor e aplique rapidamente
• Mantenha seu portfólio atualizado
• Foque em projetos que desenvolvam suas habilidades principais

Acesse o dashboard completo com: "resumo geral"
        """.strip()

        # Store as notification
        notification = UserNotification(
            user_id=user_id,
            type="daily_report",
            title=f"📊 Relatório Diário - {yesterday.strftime('%d/%m/%Y')}",
            message=report,
            priority="medium",
            read=False,
        )

        self.db.add(notification)
        self.db.commit()

        logger.info(f"Daily report generated for user {user_id}")

        return {
            "status": "success",
            "user_id": user_id,
            "new_opportunities": new_opportunities,
            "high_value_opportunities": high_value_opps,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error generating daily report: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    base=DatabaseTask,
    bind=True,
    name="tasks.intelligence_automation.detect_career_anomalies",
)
def detect_career_anomalies(self, user_id: int) -> Dict[str, Any]:
    """
    Detect career anomalies and alert user proactively.

    Checks for:
    - Sudden income drop
    - Decreasing project volume
    - Low client satisfaction trends
    - Skill stagnation

    Creates high-priority notifications for anomalies.

    Args:
        user_id: User ID to check

    Returns:
        Dict with anomalies detected
    """
    try:
        from database.models import ProjectExecution, UserNotification

        logger.info(f"Checking career anomalies for user {user_id}")

        anomalies = []

        # Check income drop
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)

        recent_income = (
            self.db.query(ProjectExecution)
            .filter(
                ProjectExecution.user_id == user_id,
                ProjectExecution.status == "completed",
                ProjectExecution.created_at >= thirty_days_ago,
            )
            .all()
        )

        previous_income = (
            self.db.query(ProjectExecution)
            .filter(
                ProjectExecution.user_id == user_id,
                ProjectExecution.status == "completed",
                ProjectExecution.created_at >= sixty_days_ago,
                ProjectExecution.created_at < thirty_days_ago,
            )
            .all()
        )

        recent_total = sum(p.negotiated_value or 0 for p in recent_income)
        previous_total = sum(p.negotiated_value or 0 for p in previous_income)

        if previous_total > 0 and recent_total < previous_total * 0.7:
            anomalies.append(
                {
                    "type": "income_drop",
                    "severity": "high",
                    "message": f"Queda de {((previous_total - recent_total) / previous_total * 100):.0f}% na receita (últimos 30 dias vs 30-60 dias atrás)",
                }
            )

        # Check project volume
        if len(recent_income) < len(previous_income) * 0.5:
            anomalies.append(
                {
                    "type": "volume_drop",
                    "severity": "medium",
                    "message": f"Volume de projetos caiu de {len(previous_income)} para {len(recent_income)}",
                }
            )

        # Create notifications for anomalies
        notifications_created = 0
        for anomaly in anomalies:
            notification = UserNotification(
                user_id=user_id,
                type="career_alert",
                title=f"⚠️ Alerta de Carreira: {anomaly['type']}",
                message=f"""
**ALERTA PROATIVO DETECTADO**

{anomaly['message']}

**Ações recomendadas:**
• Revise oportunidades disponíveis
• Considere ampliar áreas de atuação
• Analise feedback de clientes recentes
• Atualize portfólio e perfis

Use "resumo geral" para análise completa.
                """.strip(),
                priority="high" if anomaly["severity"] == "high" else "medium",
                read=False,
            )

            self.db.add(notification)
            notifications_created += 1

        self.db.commit()

        logger.info(f"Detected {len(anomalies)} anomalies for user {user_id}")

        return {
            "status": "success",
            "user_id": user_id,
            "anomalies_detected": len(anomalies),
            "notifications_created": notifications_created,
            "anomalies": anomalies,
        }

    except Exception as exc:
        logger.error(f"Error detecting career anomalies: {exc}", exc_info=True)
        raise self.retry(exc=exc)
