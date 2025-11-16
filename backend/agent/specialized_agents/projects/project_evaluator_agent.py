"""Project Evaluator Agent - Strategic pricing and opportunity evaluation.

This agent is responsible for:
- Calculating suggested pricing based on complexity and factors
- Evaluating financial viability
- Scoring skill alignment
- Scoring strategic value for career
- Generating final recommendations (accept/negotiate/reject)
- Providing detailed justifications
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agno import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import FreelanceOpportunity, PricingParameter

logger = logging.getLogger(__name__)


class ProjectEvaluatorAgent(Agent):
    """
    Agent that evaluates opportunities and provides strategic pricing recommendations.

    Uses dynamic pricing parameters and multi-factor analysis to determine
    if an opportunity is worth pursuing and at what price.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize ProjectEvaluatorAgent.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

        super().__init__(
            name="Project Evaluator",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
                "You are a strategic project evaluation and pricing expert.",
                "You calculate fair pricing based on complexity, specialization, and market factors.",
                "You evaluate financial viability, skill alignment, and strategic value.",
                "You protect the user from underpriced or problematic projects.",
                "You provide clear recommendations: accept, negotiate, or reject.",
                "Always justify your recommendations with specific reasons.",
            ],
            tools=[
                self.evaluate_opportunity,
                self.batch_evaluate,
                self.get_pricing_parameters,
                self.update_pricing_parameters,
                self.calculate_suggested_price,
            ],
        )

    def get_pricing_parameters(self) -> str:
        """
        Get current active pricing parameters.

        Returns:
            Current pricing configuration
        """
        try:
            params = self._get_active_pricing_params()

            if not params:
                return "No pricing parameters configured. Please set up pricing first."

            result = {
                "version": params.version,
                "base_hourly_rate": params.base_hourly_rate,
                "currency": params.currency,
                "minimum_margin": params.minimum_margin,
                "minimum_project_value": params.minimum_project_value,
                "minimum_deadline_days": params.minimum_deadline_days,
                "complexity_factors": params.complexity_factors,
                "specialization_factors": params.specialization_factors,
                "deadline_factors": params.deadline_factors,
                "client_factors": params.client_factors,
                "auto_adjusted": params.auto_adjusted,
                "based_on_executions": params.based_on_executions_count,
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error getting pricing parameters: {e}")
            return f"Error: {str(e)}"

    def _get_active_pricing_params(self) -> Optional[PricingParameter]:
        """Get active pricing parameters for user."""
        return (
            self.db.query(PricingParameter)
            .filter(
                PricingParameter.user_id == self.user_id,
                PricingParameter.active == True,  # noqa: E712
            )
            .order_by(PricingParameter.version.desc())
            .first()
        )

    def _get_or_create_default_pricing_params(self) -> PricingParameter:
        """Get active pricing parameters or create default ones."""
        params = self._get_active_pricing_params()

        if not params:
            # Create default pricing parameters
            params = PricingParameter(
                user_id=self.user_id,
                version=1,
                base_hourly_rate=100.0,  # Default $100/hour
                minimum_margin=0.20,  # 20% minimum margin
                currency="USD",
                complexity_factors={
                    "1-2": 0.8,
                    "3-4": 1.0,
                    "5-6": 1.3,
                    "7-8": 1.6,
                    "9-10": 2.0,
                },
                specialization_factors={
                    "ai_ml": 1.5,
                    "blockchain": 1.4,
                    "full_stack": 1.2,
                    "backend": 1.1,
                    "frontend": 1.0,
                    "mobile": 1.1,
                    "devops": 1.3,
                    "data": 1.2,
                    "other": 1.0,
                },
                deadline_factors={
                    "urgent": 1.5,  # <7 days
                    "short": 1.2,  # 7-14 days
                    "normal": 1.0,  # 15-30 days
                    "long": 0.95,  # >30 days
                },
                client_factors={
                    "no_rating": 1.1,
                    "low_rating": 1.15,
                    "good_rating": 1.0,
                    "excellent_rating": 0.95,
                },
                minimum_project_value=500.0,
                minimum_deadline_days=7,
                active=True,
                activated_at=datetime.now(timezone.utc),
            )
            self.db.add(params)
            self.db.commit()
            logger.info(f"Created default pricing parameters for user {self.user_id}")

        return params

    def calculate_suggested_price(self, opportunity_id: int) -> str:
        """
        Calculate suggested price for an opportunity.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Pricing calculation details
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.id == opportunity_id,
                    FreelanceOpportunity.user_id == self.user_id,
                )
                .first()
            )

            if not opportunity:
                return f"Opportunity {opportunity_id} not found"

            if opportunity.status == "new":
                return "Opportunity must be analyzed first before pricing"

            pricing = self._calculate_pricing(opportunity)

            return json.dumps(pricing, indent=2)

        except Exception as e:
            logger.error(f"Error calculating price: {e}")
            return f"Error: {str(e)}"

    def _calculate_pricing(self, opportunity: FreelanceOpportunity) -> Dict[str, Any]:
        """
        Calculate comprehensive pricing for an opportunity.

        Args:
            opportunity: Opportunity to price

        Returns:
            Pricing details dictionary
        """
        params = self._get_or_create_default_pricing_params()

        # Base calculation
        estimated_hours = opportunity.estimated_hours or 40.0
        base_value = estimated_hours * params.base_hourly_rate

        # Apply factors
        factors_applied = {}

        # 1. Complexity factor
        complexity = opportunity.estimated_complexity or 5
        if complexity <= 2:
            complexity_factor = params.complexity_factors.get("1-2", 1.0)
        elif complexity <= 4:
            complexity_factor = params.complexity_factors.get("3-4", 1.0)
        elif complexity <= 6:
            complexity_factor = params.complexity_factors.get("5-6", 1.0)
        elif complexity <= 8:
            complexity_factor = params.complexity_factors.get("7-8", 1.0)
        else:
            complexity_factor = params.complexity_factors.get("9-10", 1.0)
        factors_applied["complexity"] = complexity_factor

        # 2. Specialization factor
        category = opportunity.category or "other"
        specialization_factor = params.specialization_factors.get(category, 1.0)
        factors_applied["specialization"] = specialization_factor

        # 3. Deadline factor
        deadline_days = opportunity.client_deadline_days or 30
        if deadline_days < 7:
            deadline_factor = params.deadline_factors.get("urgent", 1.0)
        elif deadline_days <= 14:
            deadline_factor = params.deadline_factors.get("short", 1.0)
        elif deadline_days <= 30:
            deadline_factor = params.deadline_factors.get("normal", 1.0)
        else:
            deadline_factor = params.deadline_factors.get("long", 1.0)
        factors_applied["deadline"] = deadline_factor

        # 4. Client factor
        client_rating = opportunity.client_rating or 0
        if client_rating == 0:
            client_factor = params.client_factors.get("no_rating", 1.0)
        elif client_rating < 3.0:
            client_factor = params.client_factors.get("low_rating", 1.0)
        elif client_rating >= 4.5:
            client_factor = params.client_factors.get("excellent_rating", 1.0)
        else:
            client_factor = params.client_factors.get("good_rating", 1.0)
        factors_applied["client"] = client_factor

        # Calculate final suggested price
        suggested_price = (
            base_value
            * complexity_factor
            * specialization_factor
            * deadline_factor
            * client_factor
        )

        # Apply minimum margin
        minimum_with_margin = base_value * (1 + params.minimum_margin)
        suggested_price = max(suggested_price, minimum_with_margin)

        # Apply minimum project value
        suggested_price = max(suggested_price, params.minimum_project_value)

        # Calculate suggested deadline (with 20% buffer)
        work_hours_per_day = 6.0  # Assume 6 productive hours/day
        suggested_deadline = max(
            int((estimated_hours / work_hours_per_day) * 1.2),
            params.minimum_deadline_days,
        )

        return {
            "base_value": round(base_value, 2),
            "suggested_price": round(suggested_price, 2),
            "suggested_deadline_days": suggested_deadline,
            "currency": params.currency,
            "factors_applied": factors_applied,
            "base_hourly_rate": params.base_hourly_rate,
            "estimated_hours": estimated_hours,
        }

    def evaluate_opportunity(self, opportunity_id: int) -> str:
        """
        Perform complete evaluation of an opportunity.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Evaluation results with recommendation
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.id == opportunity_id,
                    FreelanceOpportunity.user_id == self.user_id,
                )
                .first()
            )

            if not opportunity:
                return f"Opportunity {opportunity_id} not found"

            if opportunity.status == "new":
                return "Opportunity must be analyzed first before evaluation"

            # Calculate pricing
            pricing = self._calculate_pricing(opportunity)

            # Calculate scores
            scores = self._calculate_scores(opportunity, pricing)

            # Generate recommendation
            recommendation = self._generate_recommendation(opportunity, scores)

            # Update opportunity
            opportunity.suggested_price = pricing["suggested_price"]
            opportunity.suggested_deadline_days = pricing["suggested_deadline_days"]
            opportunity.viability_score = scores["viability"]
            opportunity.alignment_score = scores["alignment"]
            opportunity.strategic_score = scores["strategic"]
            opportunity.final_score = scores["final"]
            opportunity.recommendation = recommendation["decision"]
            opportunity.recommendation_reason = recommendation["reason"]

            self.db.commit()

            result = {
                "opportunity_id": opportunity_id,
                "title": opportunity.title,
                "pricing": pricing,
                "scores": scores,
                "recommendation": recommendation,
                "status": "✅ Evaluation complete",
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error evaluating opportunity: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"

    def _calculate_scores(
        self, opportunity: FreelanceOpportunity, pricing: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate viability, alignment, and strategic scores."""
        # 1. Viability score (financial)
        if opportunity.client_budget:
            ratio = opportunity.client_budget / pricing["suggested_price"]
            if ratio >= 1.0:
                viability_score = min(ratio / 1.2, 1.0)  # Cap at 1.0
            else:
                viability_score = ratio * 0.7  # Penalize underpayment
        else:
            viability_score = 0.5  # Neutral if no budget specified

        # 2. Alignment score (skills match)
        # TODO: Implement proper skill matching with user profile
        # For now, use a simple heuristic based on category and red flags
        alignment_score = 0.7  # Default neutral-positive
        if opportunity.red_flags and len(opportunity.red_flags) > 3:
            alignment_score -= 0.2
        if opportunity.skill_level == "expert":
            alignment_score += 0.1
        alignment_score = max(0.0, min(1.0, alignment_score))

        # 3. Strategic score (career value)
        strategic_score = 0.5  # Base
        if opportunity.opportunities:
            for opp in opportunity.opportunities:
                if "portfolio" in opp.lower():
                    strategic_score += 0.15
                if "skill" in opp.lower():
                    strategic_score += 0.10
                if "network" in opp.lower():
                    strategic_score += 0.10
                if "recurring" in opp.lower():
                    strategic_score += 0.15

        # Penalize red flags
        if opportunity.red_flags:
            strategic_score -= len(opportunity.red_flags) * 0.05

        strategic_score = max(0.0, min(1.0, strategic_score))

        # 4. Final score (weighted average)
        final_score = (
            viability_score * 0.4 + alignment_score * 0.3 + strategic_score * 0.3
        )

        return {
            "viability": round(viability_score, 2),
            "alignment": round(alignment_score, 2),
            "strategic": round(strategic_score, 2),
            "final": round(final_score, 2),
        }

    def _generate_recommendation(
        self, opportunity: FreelanceOpportunity, scores: Dict[str, float]
    ) -> Dict[str, str]:
        """Generate final recommendation based on scores and analysis."""
        final_score = scores["final"]
        has_red_flags = opportunity.red_flags and len(opportunity.red_flags) > 0

        # Decision logic
        if final_score >= 0.75 and not has_red_flags:
            decision = "accept"
            reason = f"Excellent opportunity with final score {final_score:.2f}. "
            reason += f"Strong viability ({scores['viability']:.2f}), "
            reason += f"good alignment ({scores['alignment']:.2f}), and "
            reason += f"strategic value ({scores['strategic']:.2f}). "
            if opportunity.opportunities:
                reason += f"Opportunities: {', '.join(opportunity.opportunities[:3])}."

        elif final_score >= 0.5:
            decision = "negotiate"
            reason = f"Moderate opportunity with final score {final_score:.2f}. "
            if scores["viability"] < 0.6:
                reason += "Budget appears low for the complexity. "
            if has_red_flags:
                reason += f"Address red flags: {', '.join(opportunity.red_flags[:2])}. "
            reason += "Recommend negotiating better terms before acceptance."

        else:
            decision = "reject"
            reason = f"Low-value opportunity with final score {final_score:.2f}. "
            if scores["viability"] < 0.4:
                reason += "Budget too low for estimated work. "
            if has_red_flags:
                reason += f"Multiple red flags: {', '.join(opportunity.red_flags)}. "
            reason += "Not recommended to pursue."

        return {"decision": decision, "reason": reason}

    def batch_evaluate(self, status: str = "analyzed", limit: int = 10) -> str:
        """
        Evaluate multiple opportunities in batch.

        Args:
            status: Status filter
            limit: Maximum number to evaluate

        Returns:
            Batch evaluation results
        """
        try:
            opportunities = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.status == status,
                )
                .limit(limit)
                .all()
            )

            if not opportunities:
                return f"No opportunities found with status '{status}'"

            results = []
            for opp in opportunities:
                try:
                    self.evaluate_opportunity(opp.id)
                    results.append(
                        f"✅ {opp.title[:40]}... - {opp.recommendation} (score: {opp.final_score:.2f})"
                    )
                except Exception as e:
                    logger.error(f"Error evaluating {opp.id}: {e}")
                    results.append(f"❌ {opp.title[:40]}... - Error")

            summary = f"Evaluated {len(results)} opportunities:\n" + "\n".join(results)
            return summary

        except Exception as e:
            logger.error(f"Error in batch evaluation: {e}")
            return f"Error: {str(e)}"

    def update_pricing_parameters(
        self,
        base_hourly_rate: Optional[float] = None,
        minimum_margin: Optional[float] = None,
        minimum_project_value: Optional[float] = None,
    ) -> str:
        """
        Update pricing parameters (creates new version).

        Args:
            base_hourly_rate: New base rate
            minimum_margin: New minimum margin
            minimum_project_value: New minimum project value

        Returns:
            Confirmation message
        """
        try:
            current_params = self._get_or_create_default_pricing_params()

            # Deactivate current version
            current_params.active = False

            # Create new version with updates
            new_params = PricingParameter(
                user_id=self.user_id,
                version=current_params.version + 1,
                base_hourly_rate=base_hourly_rate or current_params.base_hourly_rate,
                minimum_margin=minimum_margin or current_params.minimum_margin,
                minimum_project_value=minimum_project_value
                or current_params.minimum_project_value,
                currency=current_params.currency,
                complexity_factors=current_params.complexity_factors,
                specialization_factors=current_params.specialization_factors,
                deadline_factors=current_params.deadline_factors,
                client_factors=current_params.client_factors,
                minimum_deadline_days=current_params.minimum_deadline_days,
                active=True,
                activated_at=datetime.now(timezone.utc),
            )

            self.db.add(new_params)
            self.db.commit()

            return f"✅ Created pricing parameters v{new_params.version} with updated values"

        except Exception as e:
            logger.error(f"Error updating pricing parameters: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"


def create_project_evaluator_agent(db: Session, user_id: int) -> ProjectEvaluatorAgent:
    """
    Factory function to create a ProjectEvaluatorAgent instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured ProjectEvaluatorAgent instance
    """
    return ProjectEvaluatorAgent(db=db, user_id=user_id)
