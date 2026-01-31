"""HourlyRateOptimizer - Dynamic hourly rate optimization based on acceptance.

This service optimizes the base hourly rate by analyzing acceptance patterns
across different rate ranges, categories, and client types.

Optimization Strategy:
- Tracks acceptance rate by hourly rate range
- Identifies "sweet spot" rates (maximum revenue with high acceptance)
- Segments analysis by project category (ai_ml, full_stack, etc.)
- Considers time-to-acceptance as quality signal
- Balances profitability vs. opportunity cost
- Suggests category-specific rate adjustments
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import (
    FreelanceOpportunity,
    PricingParameter,
)

logger = logging.getLogger(__name__)


class HourlyRateOptimizer:
    """
    Optimizes base hourly rate based on acceptance patterns.

    Analyzes:
    - Acceptance rate by rate range
    - Revenue per opportunity at different rates
    - Category-specific optimal rates
    - Client willingness to pay patterns
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize HourlyRateOptimizer.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

    def analyze_acceptance_by_rate(self, days: int = 90) -> Dict:
        """
        Analyze acceptance patterns across different hourly rate ranges.

        Args:
            days: Number of days to analyze (default: 90)

        Returns:
            Analysis of acceptance rates by hourly rate range
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get opportunities with pricing data
        opportunities = (
            self.db.query(FreelanceOpportunity)
            .filter(
                and_(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.created_at >= cutoff_date,
                    FreelanceOpportunity.suggested_pricing.isnot(None),
                )
            )
            .all()
        )

        if not opportunities:
            return {
                "total_opportunities": 0,
                "message": f"No opportunities with pricing data found in last {days} days",
            }

        # Group by rate ranges
        rate_ranges = self._define_rate_ranges()
        range_stats = {
            range_name: {"total": 0, "accepted": 0, "rejected": 0, "revenue": 0.0}
            for range_name in rate_ranges.keys()
        }

        for opp in opportunities:
            suggested_rate = opp.suggested_pricing.get("suggested_hourly_rate")
            if not suggested_rate:
                continue

            # Find appropriate range
            range_name = self._find_rate_range(suggested_rate, rate_ranges)
            if not range_name:
                continue

            # Update stats
            range_stats[range_name]["total"] += 1

            if opp.status in ("accepted", "negotiating") or opp.recommendation == "accept":
                range_stats[range_name]["accepted"] += 1
                # Add negotiated or suggested value
                value = opp.client_budget or opp.suggested_pricing.get("suggested_value", 0.0)
                range_stats[range_name]["revenue"] += value
            elif opp.status == "rejected" or opp.recommendation == "reject":
                range_stats[range_name]["rejected"] += 1

        # Calculate acceptance rates and average revenue
        for range_name, stats in range_stats.items():
            if stats["total"] > 0:
                stats["acceptance_rate"] = round(stats["accepted"] / stats["total"], 3)
                stats["avg_revenue_per_opportunity"] = round(stats["revenue"] / stats["total"], 2)
                stats["expected_value"] = round(
                    stats["acceptance_rate"] * stats["avg_revenue_per_opportunity"], 2
                )  # EV = probability * payoff
            else:
                stats["acceptance_rate"] = 0.0
                stats["avg_revenue_per_opportunity"] = 0.0
                stats["expected_value"] = 0.0

        # Identify optimal range
        optimal_range = self._identify_optimal_range(range_stats)

        return {
            "total_opportunities": len(opportunities),
            "period_days": days,
            "rate_range_stats": range_stats,
            "optimal_range": optimal_range,
        }

    def analyze_category_specific_rates(self, days: int = 90) -> Dict:
        """
        Analyze optimal rates by project category.

        Different categories may support different rate ranges
        (e.g., AI/ML projects typically pay more than frontend).

        Args:
            days: Number of days to analyze

        Returns:
            Category-specific rate analysis
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get opportunities with semantic analysis
        opportunities = (
            self.db.query(FreelanceOpportunity)
            .filter(
                and_(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.created_at >= cutoff_date,
                    FreelanceOpportunity.semantic_analysis.isnot(None),
                    FreelanceOpportunity.suggested_pricing.isnot(None),
                )
            )
            .all()
        )

        if not opportunities:
            return {
                "total_opportunities": 0,
                "message": "No opportunities with category data found",
            }

        # Group by category
        category_stats = {}

        for opp in opportunities:
            category = opp.semantic_analysis.get("category", "other")
            suggested_rate = opp.suggested_pricing.get("suggested_hourly_rate")

            if not suggested_rate:
                continue

            if category not in category_stats:
                category_stats[category] = {
                    "total": 0,
                    "accepted": 0,
                    "total_rate": 0.0,
                    "accepted_rate": 0.0,
                    "max_accepted_rate": 0.0,
                }

            stats = category_stats[category]
            stats["total"] += 1
            stats["total_rate"] += suggested_rate

            if opp.status in ("accepted", "negotiating") or opp.recommendation == "accept":
                stats["accepted"] += 1
                stats["accepted_rate"] += suggested_rate
                stats["max_accepted_rate"] = max(stats["max_accepted_rate"], suggested_rate)

        # Calculate averages and acceptance rates
        for category, stats in category_stats.items():
            stats["avg_rate"] = (
                round(stats["total_rate"] / stats["total"], 2) if stats["total"] > 0 else 0.0
            )
            stats["avg_accepted_rate"] = (
                round(stats["accepted_rate"] / stats["accepted"], 2)
                if stats["accepted"] > 0
                else 0.0
            )
            stats["acceptance_rate"] = (
                round(stats["accepted"] / stats["total"], 3) if stats["total"] > 0 else 0.0
            )
            stats["max_accepted_rate"] = round(stats["max_accepted_rate"], 2)

        return {
            "total_opportunities": len(opportunities),
            "period_days": days,
            "category_stats": category_stats,
        }

    def suggest_rate_adjustment(
        self,
        target_acceptance_rate: float = 0.60,
        min_sample_size: int = 10,
    ) -> Dict:
        """
        Suggest base hourly rate adjustment based on acceptance patterns.

        Args:
            target_acceptance_rate: Desired acceptance rate (default: 0.60 = 60%)
            min_sample_size: Minimum opportunities needed for suggestion

        Returns:
            Rate adjustment suggestion with reasoning
        """
        analysis = self.analyze_acceptance_by_rate(days=90)

        if analysis["total_opportunities"] < min_sample_size:
            return {
                "adjustment_suggested": False,
                "reason": f"Insufficient data ({analysis['total_opportunities']} opportunities, need {min_sample_size})",
            }

        # Get current pricing parameters
        current_params = (
            self.db.query(PricingParameter)
            .filter(
                and_(
                    PricingParameter.user_id == self.user_id,
                    PricingParameter.active == True,  # noqa: E712
                )
            )
            .order_by(PricingParameter.version.desc())
            .first()
        )

        if not current_params:
            return {
                "adjustment_suggested": False,
                "reason": "No active pricing parameters found",
            }

        current_rate = current_params.base_hourly_rate

        # Find optimal range
        optimal = analysis["optimal_range"]
        if not optimal:
            return {
                "adjustment_suggested": False,
                "reason": "Unable to identify optimal rate range",
            }

        # Determine suggested rate based on optimal range
        optimal_rate_mid = (optimal["range_min"] + optimal["range_max"]) / 2

        # Calculate overall acceptance rate
        total_accepted = sum(stats["accepted"] for stats in analysis["rate_range_stats"].values())
        total_opps = analysis["total_opportunities"]
        overall_acceptance_rate = total_accepted / total_opps if total_opps > 0 else 0.0

        # Decision logic
        adjustment_suggested = False
        suggested_rate = current_rate
        reason = ""

        if overall_acceptance_rate > 0.80:
            # Very high acceptance: can increase rate
            adjustment_suggested = True
            suggested_rate = min(current_rate * 1.15, optimal_rate_mid * 1.1)
            reason = f"High acceptance rate ({overall_acceptance_rate:.1%}). Can increase rate to capture more value."

        elif overall_acceptance_rate < 0.40:
            # Low acceptance: should decrease rate
            adjustment_suggested = True
            suggested_rate = max(current_rate * 0.90, optimal_rate_mid * 0.95)
            reason = f"Low acceptance rate ({overall_acceptance_rate:.1%}). Should decrease rate to win more projects."

        elif abs(current_rate - optimal_rate_mid) > current_rate * 0.15:
            # Current rate differs significantly from optimal
            adjustment_suggested = True
            suggested_rate = optimal_rate_mid
            reason = f"Current rate ${current_rate}/hr differs from optimal range. Adjusting to ${optimal_rate_mid:.0f}/hr."

        else:
            reason = f"Current rate ${current_rate}/hr is optimal. Acceptance rate: {overall_acceptance_rate:.1%}"

        return {
            "adjustment_suggested": adjustment_suggested,
            "current_rate": current_rate,
            "suggested_rate": round(suggested_rate, 2) if adjustment_suggested else current_rate,
            "current_acceptance_rate": round(overall_acceptance_rate, 3),
            "target_acceptance_rate": target_acceptance_rate,
            "optimal_range": f"${optimal['range_min']}-${optimal['range_max']}/hr",
            "reason": reason,
            "sample_size": analysis["total_opportunities"],
        }

    def apply_rate_adjustment(
        self,
        suggested_rate: Optional[float] = None,
        auto_apply: bool = False,
    ) -> Optional[PricingParameter]:
        """
        Apply hourly rate adjustment to create new pricing parameters.

        Args:
            suggested_rate: Rate to apply (if None, uses suggest_rate_adjustment)
            auto_apply: If True, applies without checking thresholds

        Returns:
            New PricingParameter if adjustment applied, None otherwise
        """
        if suggested_rate is None:
            suggestion = self.suggest_rate_adjustment()
            if not suggestion["adjustment_suggested"] and not auto_apply:
                logger.info("No rate adjustment suggested")
                return None
            suggested_rate = suggestion["suggested_rate"]

        try:
            # Get current pricing parameters
            current_params = (
                self.db.query(PricingParameter)
                .filter(
                    and_(
                        PricingParameter.user_id == self.user_id,
                        PricingParameter.active == True,  # noqa: E712
                    )
                )
                .order_by(PricingParameter.version.desc())
                .first()
            )

            if not current_params:
                logger.warning("No active pricing parameters to adjust")
                return None

            # Deactivate current version
            current_params.active = False

            # Create new version with adjusted rate
            new_params = PricingParameter(
                user_id=self.user_id,
                version=current_params.version + 1,
                base_hourly_rate=suggested_rate,
                minimum_margin=current_params.minimum_margin,
                currency=current_params.currency,
                complexity_factors=current_params.complexity_factors,
                specialization_factors=current_params.specialization_factors,
                deadline_factors=current_params.deadline_factors,
                client_factors=current_params.client_factors,
                minimum_project_value=current_params.minimum_project_value,
                minimum_deadline_days=current_params.minimum_deadline_days,
                auto_adjusted=True,
                based_on_executions_count=0,  # This is rate-based, not execution-based
                adjustment_reason=f"Hourly rate optimized from ${current_params.base_hourly_rate}/hr to ${suggested_rate}/hr based on acceptance patterns",
                active=True,
                activated_at=datetime.now(timezone.utc),
            )

            self.db.add(new_params)
            self.db.commit()
            self.db.refresh(new_params)

            logger.info(
                f"Applied rate adjustment: ${current_params.base_hourly_rate} -> ${suggested_rate}"
            )
            return new_params

        except Exception as e:
            logger.error(f"Error applying rate adjustment: {e}")
            self.db.rollback()
            return None

    def _define_rate_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Define hourly rate ranges for analysis."""
        return {
            "entry": (40, 60),
            "junior": (60, 80),
            "mid": (80, 100),
            "senior": (100, 125),
            "expert": (125, 150),
            "premium": (150, 200),
            "elite": (200, 999),
        }

    def _find_rate_range(
        self, rate: float, ranges: Dict[str, Tuple[float, float]]
    ) -> Optional[str]:
        """Find which range a rate falls into."""
        for range_name, (range_min, range_max) in ranges.items():
            if range_min <= rate < range_max:
                return range_name
        return None

    def _identify_optimal_range(self, range_stats: Dict) -> Optional[Dict]:
        """
        Identify optimal rate range based on expected value.

        Expected Value = Acceptance Rate × Average Revenue
        This balances probability of winning vs. project value.
        """
        best_ev = 0.0
        best_range = None

        ranges_def = self._define_rate_ranges()

        for range_name, stats in range_stats.items():
            if stats["total"] < 3:  # Need at least 3 samples
                continue

            ev = stats["expected_value"]
            if ev > best_ev:
                best_ev = ev
                best_range = range_name

        if best_range:
            range_min, range_max = ranges_def[best_range]
            return {
                "range_name": best_range,
                "range_min": range_min,
                "range_max": range_max,
                "expected_value": best_ev,
                "acceptance_rate": range_stats[best_range]["acceptance_rate"],
                "avg_revenue": range_stats[best_range]["avg_revenue_per_opportunity"],
            }

        return None
