"""Negotiation Engine - Intelligent counter-proposal generation.

This module is responsible for:
- Analyzing client budget vs strategic pricing
- Generating intelligent counter-proposals with justifications
- Creating diplomatic negotiation messages
- Suggesting scope/deadline adjustments
- Tracking negotiation history and outcomes
"""

import logging
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import FreelanceOpportunity, Negotiation

logger = logging.getLogger(__name__)


class NegotiationEngine(Agent):
    """
    Agent that generates intelligent counter-proposals for project negotiations.

    Uses strategic pricing and project analysis to create persuasive,
    data-driven negotiation strategies.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize NegotiationEngine.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

        super().__init__(
            name="Negotiation Expert",
            model=OpenAIChat(id="gpt-4o"),  # Use strong model for persuasive communication
            instructions=[
                "You are an expert negotiation strategist for freelance projects.",
                "You analyze budget gaps and create persuasive counter-proposals.",
                "You always provide clear, professional justifications based on:",
                "  - Project complexity and estimated effort",
                "  - Market rates for required skills",
                "  - Value delivered to the client",
                "  - Risk factors and timeline constraints",
                "You generate diplomatic, respectful messages that:",
                "  - Acknowledge the client's budget constraints",
                "  - Explain the value proposition clearly",
                "  - Offer alternatives (scope reduction, timeline extension)",
                "  - Maintain professional tone while being firm on fair pricing",
                "You never apologize for charging fair rates.",
                "You focus on value, not on defending your time.",
            ],
            tools=[
                self.generate_counter_proposal,
                self.generate_negotiation_message,
                self.suggest_scope_adjustments,
                self.analyze_negotiation_gap,
                self.get_negotiation_history,
            ],
        )

    def generate_counter_proposal(
        self,
        opportunity_id: int,
        original_budget: Optional[float] = None,
        justification_style: str = "value_based",
    ) -> str:
        """
        Generate an intelligent counter-proposal for an opportunity.

        Args:
            opportunity_id: Opportunity ID
            original_budget: Client's original budget (if different from opportunity.client_budget)
            justification_style: Style of justification (value_based, market_based, effort_based)

        Returns:
            Counter-proposal with justification
        """
        try:
            # Get opportunity
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

            # Use provided budget or fall back to opportunity's client_budget
            client_budget = original_budget or opportunity.client_budget

            if not client_budget:
                return "Cannot generate counter-proposal: client budget not specified"

            if not opportunity.suggested_price:
                return "Cannot generate counter-proposal: opportunity not evaluated yet. Run evaluate_opportunity first."

            # Calculate gap
            gap_amount = opportunity.suggested_price - client_budget
            gap_percentage = (gap_amount / client_budget * 100) if client_budget > 0 else 0

            # Analyze factors for justification
            factors = {
                "complexity": opportunity.estimated_complexity or "Not estimated",
                "hours": opportunity.estimated_hours or "Not estimated",
                "skills": opportunity.required_skills or [],
                "deadline_days": opportunity.client_deadline_days,
                "viability_score": opportunity.viability_score,
                "alignment_score": opportunity.alignment_score,
                "strategic_score": opportunity.strategic_score,
            }

            # Create counter-proposal record
            counter_proposal = Negotiation(
                user_id=self.user_id,
                opportunity_id=opportunity_id,
                original_budget=client_budget,
                counter_proposal_budget=opportunity.suggested_price,
                counter_proposal_justification=self._build_justification(
                    opportunity, gap_amount, gap_percentage, factors, justification_style
                ),
                outcome="pending",
            )

            self.db.add(counter_proposal)
            self.db.commit()
            self.db.refresh(counter_proposal)

            # Build response
            result = "💰 **Counter-Proposal Generated**\n\n"
            result += "📊 **Budget Analysis**:\n"
            result += f"  • Client Budget: ${client_budget:,.2f}\n"
            result += f"  • Suggested Price: ${opportunity.suggested_price:,.2f}\n"
            result += f"  • Gap: ${gap_amount:,.2f} ({gap_percentage:+.1f}%)\n\n"

            result += f"📊 **Justification** ({justification_style}):\n"
            result += counter_proposal.counter_proposal_justification + "\n\n"

            # Add recommendations
            if gap_percentage > 50:
                result += " **Warning**: Large gap (>50%). Consider:\n"
                result += "  • Breaking project into phases\n"
                result += "  • Reducing scope to fit budget\n"
                result += "  • Offering a discovery/planning phase first\n\n"
            elif gap_percentage > 25:
                result += (
                    "= **Tip**: Moderate gap. Emphasize value and outcomes in your message.\n\n"
                )
            else:
                result += "✅ **Good news**: Small gap. High chance of acceptance.\n\n"

            result += f"< **Negotiation ID**: {counter_proposal.id}\n"
            result += "= Use generate_negotiation_message() to create the client message.\n"

            return result

        except Exception as e:
            logger.error(f"Error generating counter-proposal: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"

    def _build_justification(
        self,
        opportunity: FreelanceOpportunity,
        gap_amount: float,
        gap_percentage: float,
        factors: Dict[str, Any],
        style: str,
    ) -> str:
        """Build justification based on style and factors."""
        justifications = []

        if style == "value_based":
            if opportunity.strategic_score and opportunity.strategic_score > 7:
                justifications.append(
                    f"This project offers high strategic value (score: {opportunity.strategic_score}/10) "
                    "for building expertise and portfolio in high-demand skills."
                )

            if factors["complexity"] and factors["complexity"] >= 7:
                justifications.append(
                    f"Complex project (complexity: {factors['complexity']}/10) requiring specialized "
                    "knowledge and careful execution to deliver quality results."
                )

            justifications.append(
                "Pricing reflects the value delivered: a complete, professional solution "
                "that meets all requirements and solves the client's core business problem."
            )

        elif style == "market_based":
            justifications.append(
                f"Market rates for {', '.join(factors['skills'][:3])} expertise align with this pricing, "
                "ensuring quality professionals who can deliver reliably."
            )

            if factors["deadline_days"] and factors["deadline_days"] < 14:
                justifications.append(
                    f"Tight deadline ({factors['deadline_days']} days) requires prioritized scheduling "
                    "and may involve some overtime to ensure on-time delivery."
                )

        elif style == "effort_based":
            if factors["hours"]:
                justifications.append(
                    f"Based on detailed analysis, this project requires approximately {factors['hours']:.1f} hours "
                    "of focused development work, not including planning, testing, and revisions."
                )

            if opportunity.estimated_complexity and opportunity.estimated_complexity >= 7:
                justifications.append(
                    "High complexity projects require additional time for architecture planning, "
                    "quality assurance, and documentation to ensure long-term maintainability."
                )

        # Always add professional closing
        justifications.append(
            "This pricing ensures dedicated focus, quality execution, and professional "
            "support throughout the project lifecycle."
        )

        return " ".join(justifications)

    def generate_negotiation_message(
        self,
        negotiation_id: int,
        tone: str = "professional",
        include_alternatives: bool = True,
    ) -> str:
        """
        Generate a diplomatic negotiation message for the client.

        Args:
            negotiation_id: Negotiation record ID
            tone: Message tone (professional, friendly, firm)
            include_alternatives: Include scope/timeline alternatives

        Returns:
            Ready-to-send negotiation message
        """
        try:
            # Get negotiation record
            negotiation = (
                self.db.query(Negotiation)
                .filter(
                    Negotiation.id == negotiation_id,
                    Negotiation.user_id == self.user_id,
                )
                .first()
            )

            if not negotiation:
                return f"Negotiation {negotiation_id} not found"

            opportunity = negotiation.opportunity

            # Build message structure
            message_parts = []

            # Opening
            if tone == "friendly":
                message_parts.append(
                    f"Hi! Thank you for considering me for the '{opportunity.title}' project. "
                    "I've reviewed the requirements carefully and I'm excited about the opportunity!"
                )
            else:
                message_parts.append(
                    f"Thank you for your interest in my services for the '{opportunity.title}' project. "
                    "I've completed a thorough analysis of the requirements."
                )

            # Budget acknowledgment
            message_parts.append(
                f"\nI understand your budget is ${negotiation.original_budget:,.2f}. "
                "Based on my analysis of the project scope, complexity, and deliverables, "
                f"I propose ${negotiation.counter_proposal_budget:,.2f}."
            )

            # Justification
            message_parts.append(
                f"\n**Why this pricing:**\n{negotiation.counter_proposal_justification}"
            )

            # Alternatives (if requested)
            if include_alternatives:
                gap_percentage = (
                    (negotiation.counter_proposal_budget - negotiation.original_budget)
                    / negotiation.original_budget
                    * 100
                )

                if gap_percentage > 25:
                    message_parts.append("\n**Alternative Options:**")

                    # Option 1: Phased approach
                    phase_1_price = negotiation.original_budget
                    message_parts.append(
                        f"\n1. **Phased Delivery**: Start with Phase 1 for ${phase_1_price:,.2f}, "
                        "delivering core features. We can then evaluate Phase 2 based on results."
                    )

                    # Option 2: Reduced scope
                    message_parts.append(
                        "\n2. **Adjusted Scope**: I can work within your budget by prioritizing "
                        "the most critical features and postponing nice-to-have elements."
                    )

                    # Option 3: Extended timeline
                    if opportunity.client_deadline_days and opportunity.client_deadline_days < 30:
                        extended_days = opportunity.client_deadline_days + 14
                        message_parts.append(
                            f"\n3. **Extended Timeline**: With a {extended_days}-day timeline instead of "
                            f"{opportunity.client_deadline_days} days, I can optimize scheduling "
                            "and offer more competitive pricing."
                        )

            # Closing
            if tone == "firm":
                message_parts.append(
                    "\n\nI'm committed to delivering exceptional quality and value. "
                    "I'm happy to discuss these options and find the best path forward for your project."
                )
            else:
                message_parts.append(
                    "\n\nI'd love to work with you on this project! Let me know which option "
                    "works best for you, or if you'd like to discuss a customized approach."
                )

            message = "".join(message_parts)

            # Save generated message
            negotiation.generated_message = message
            self.db.commit()

            return (
                f"= **Negotiation Message Generated**\n\n{message}\n\n---\n\n"
                f" Message saved to negotiation {negotiation_id}. Ready to send!"
            )

        except Exception as e:
            logger.error(f"Error generating message: {e}")
            return f"Error: {str(e)}"

    def suggest_scope_adjustments(self, opportunity_id: int, target_budget: float) -> str:
        """
        Suggest specific scope adjustments to match a target budget.

        Args:
            opportunity_id: Opportunity ID
            target_budget: Target budget to match

        Returns:
            Suggested scope adjustments
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

            if not opportunity or not opportunity.suggested_price:
                return "Cannot suggest adjustments: opportunity not found or not evaluated"

            budget_ratio = target_budget / opportunity.suggested_price
            hours_reduction = (
                opportunity.estimated_hours * (1 - budget_ratio)
                if opportunity.estimated_hours
                else 0
            )

            result = f"< **Scope Adjustments to Match ${target_budget:,.2f}**\n\n"
            result += f"Current estimate: ${opportunity.suggested_price:,.2f} ({opportunity.estimated_hours:.1f}h)\n"
            result += f"Target budget: ${target_budget:,.2f}\n"
            result += f"Reduction needed: {(1-budget_ratio)*100:.1f}% (~{hours_reduction:.1f}h)\n\n"

            result += "**Suggested Adjustments:**\n\n"

            if budget_ratio < 0.7:
                result += " **Large reduction required (>30%)**\n"
                result += "• Focus on MVP features only\n"
                result += "• Defer all non-essential features to Phase 2\n"
                result += "• Reduce testing scope\n"
                result += "• Minimal documentation\n"
                result += "• Client provides more assets/content\n\n"
            elif budget_ratio < 0.85:
                result += " **Moderate reduction (15-30%)**\n"
                result += "• Simplify some complex features\n"
                result += "• Use existing templates/libraries more\n"
                result += "• Reduce custom design elements\n"
                result += "• Streamline QA process\n\n"
            else:
                result += " **Minor reduction (< 15%)**\n"
                result += "• Optimize some workflows\n"
                result += "• Reduce rounds of revisions\n"
                result += "• Focus on core deliverables\n\n"

            result += (
                "= **Recommendation**: Present these options to the client and "
                "let them prioritize which features are most important."
            )

            return result

        except Exception as e:
            logger.error(f"Error suggesting adjustments: {e}")
            return f"Error: {str(e)}"

    def analyze_negotiation_gap(self, opportunity_id: int) -> str:
        """
        Analyze the gap between client budget and suggested pricing.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Detailed gap analysis
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

            if not opportunity.client_budget or not opportunity.suggested_price:
                return "Cannot analyze gap: missing budget or pricing data"

            gap = opportunity.suggested_price - opportunity.client_budget
            gap_pct = (
                (gap / opportunity.client_budget * 100) if opportunity.client_budget > 0 else 0
            )

            result = "= **Negotiation Gap Analysis**\n\n"
            result += f"Client Budget: ${opportunity.client_budget:,.2f}\n"
            result += f"Suggested Price: ${opportunity.suggested_price:,.2f}\n"
            result += f"Gap: ${gap:,.2f} ({gap_pct:+.1f}%)\n\n"

            # Classification
            if gap_pct < -10:
                result += "< **STATUS: BUDGET EXCEEDS PRICING**\n"
                result += "Client's budget is higher than your estimate. This is ideal!\n"
                result += "• Accept at suggested price\n"
                result += "• Or add value with extra features/services\n"
                result += "• Consider building in buffer for scope changes\n"
            elif gap_pct < 5:
                result += " **STATUS: EXCELLENT FIT**\n"
                result += "Budget and pricing are well-aligned (< 5% gap).\n"
                result += "• Very high acceptance probability\n"
                result += "• Can proceed with confidence\n"
            elif gap_pct < 15:
                result += "= **STATUS: GOOD FIT**\n"
                result += "Small gap (5-15%). Easy to bridge.\n"
                result += "• Emphasize value in proposal\n"
                result += "• Show ROI/outcomes clearly\n"
                result += "• High acceptance probability\n"
            elif gap_pct < 30:
                result += "= **STATUS: MODERATE GAP**\n"
                result += "Negotiation likely needed (15-30% gap).\n"
                result += "• Present clear justification\n"
                result += "• Offer payment plan or phases\n"
                result += "• Show market comparisons\n"
                result += "• Medium acceptance probability\n"
            elif gap_pct < 50:
                result += "= **STATUS: SIGNIFICANT GAP**\n"
                result += "Large gap (30-50%). Strategic approach needed.\n"
                result += "• Offer phased delivery\n"
                result += "• Provide scope reduction options\n"
                result += "• Build strong value case\n"
                result += "• Lower acceptance probability\n"
            else:
                result += "=4 **STATUS: CRITICAL GAP**\n"
                result += "Very large gap (>50%). Consider carefully.\n"
                result += "• Client may have unrealistic expectations\n"
                result += "• Significant scope reduction needed\n"
                result += "• Or client needs to adjust budget significantly\n"
                result += "• Low acceptance probability - may not be worth pursuing\n"

            # Add strategic recommendations
            result += "\n= **Strategic Recommendation:**\n"
            if gap_pct > 30:
                result += "Generate counter-proposal with multiple options (phased, reduced scope, extended timeline)"
            elif gap_pct > 15:
                result += "Send professional counter-proposal with clear value justification"
            else:
                result += "Submit proposal at suggested price with confidence"

            return result

        except Exception as e:
            logger.error(f"Error analyzing gap: {e}")
            return f"Error: {str(e)}"

    def get_negotiation_history(self, opportunity_id: Optional[int] = None, limit: int = 10) -> str:
        """
        Get negotiation history for learning and improvement.

        Args:
            opportunity_id: Optional opportunity ID to filter by
            limit: Maximum number of records

        Returns:
            Negotiation history summary
        """
        try:
            query = self.db.query(Negotiation).filter(Negotiation.user_id == self.user_id)

            if opportunity_id:
                query = query.filter(Negotiation.opportunity_id == opportunity_id)

            negotiations = query.order_by(Negotiation.created_at.desc()).limit(limit).all()

            if not negotiations:
                return "No negotiation history found"

            result = "= **Negotiation History**\n\n"

            # Summary stats
            total = len(negotiations)
            accepted = sum(1 for n in negotiations if n.outcome == "accepted")
            agreed = sum(1 for n in negotiations if n.outcome == "agreed")
            rejected = sum(1 for n in negotiations if n.outcome == "rejected")
            pending = sum(1 for n in negotiations if n.outcome == "pending")

            result += f"Total negotiations: {total}\n"
            result += f" Accepted: {accepted} ({accepted/total*100:.1f}%)\n"
            result += f"> Agreed: {agreed} ({agreed/total*100:.1f}%)\n"
            result += f"L Rejected: {rejected} ({rejected/total*100:.1f}%)\n"
            result += f" Pending: {pending} ({pending/total*100:.1f}%)\n\n"

            # Success rate
            success_rate = (accepted + agreed) / total * 100 if total > 0 else 0
            result += f"< **Success Rate**: {success_rate:.1f}%\n\n"

            # Recent negotiations
            result += "**Recent Negotiations:**\n\n"
            for neg in negotiations[:5]:
                outcome_emoji = {
                    "accepted": "",
                    "agreed": ">",
                    "rejected": "L",
                    "pending": "",
                    "no_response": "={",
                }.get(neg.outcome, "S")

                result += f"{outcome_emoji} **Negotiation #{neg.id}**\n"
                if neg.opportunity:
                    result += f"   Project: {neg.opportunity.title[:50]}...\n"
                result += f"   Original: ${neg.original_budget:,.2f}\n"
                result += f"   Counter: ${neg.counter_proposal_budget:,.2f}\n"
                if neg.final_agreed_budget:
                    result += f"   Final: ${neg.final_agreed_budget:,.2f}\n"
                result += f"   Outcome: {neg.outcome}\n\n"

            # Learning insights
            if accepted + agreed > 0:
                avg_gap = []
                for n in negotiations:
                    if n.outcome in ["accepted", "agreed"] and n.final_agreed_budget:
                        gap = (
                            (n.final_agreed_budget - n.original_budget) / n.original_budget * 100
                            if n.original_budget > 0
                            else 0
                        )
                        avg_gap.append(gap)

                if avg_gap:
                    result += "📊 **Learning Insight**:\n"
                    result += f"Average successful negotiation increased budget by {sum(avg_gap)/len(avg_gap):.1f}%\n"

            return result

        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return f"Error: {str(e)}"


def create_negotiation_engine(db: Session, user_id: int) -> NegotiationEngine:
    """
    Factory function to create a NegotiationEngine instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured NegotiationEngine instance
    """
    return NegotiationEngine(db=db, user_id=user_id)
