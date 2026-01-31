"""RejectionPatternLearner - Red flag pattern detection and optimization.

This service analyzes rejected projects to identify which red flags
most strongly correlate with rejection decisions, improving future
risk assessment accuracy.

Learning Strategy:
- Tracks red flags present in rejected vs. accepted projects
- Calculates rejection probability for each red flag
- Identifies high-value red flags (strong rejection predictors)
- Learns new red flag patterns from rejection reasons
- Adjusts risk scoring weights based on historical correlation
"""

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import (
    FreelanceOpportunity,
    LearningRecord,
)

logger = logging.getLogger(__name__)


class RejectionPatternLearner:
    """
    Learns which red flags most strongly predict project rejection.

    Analyzes historical rejection patterns to:
    - Identify high-risk red flags
    - Calculate rejection probability by red flag
    - Discover new warning patterns
    - Recommend risk scoring adjustments
    """

    # Known red flags from ClientRiskAssessment
    KNOWN_RED_FLAGS = {
        "unrealistic_budget",
        "vague_requirements",
        "suspicious_client",
        "impossible_deadline",
        "free_work_request",
        "scope_creep_signals",
        "payment_issues_mentioned",
        "poor_communication",
        "too_good_to_be_true",
    }

    def __init__(self, db: Session, user_id: int):
        """
        Initialize RejectionPatternLearner.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

    def analyze_rejection_patterns(self, days: int = 90) -> Dict:
        """
        Analyze rejection patterns over recent period.

        Args:
            days: Number of days to analyze (default: 90)

        Returns:
            Analysis of red flags and rejection correlations
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get all opportunities from period
        opportunities = (
            self.db.query(FreelanceOpportunity)
            .filter(
                and_(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.created_at >= cutoff_date,
                    FreelanceOpportunity.recommendation.isnot(None),
                )
            )
            .all()
        )

        if not opportunities:
            return {
                "total_opportunities": 0,
                "message": f"No opportunities found in last {days} days",
            }

        # Separate by outcome
        rejected = [
            opp
            for opp in opportunities
            if opp.recommendation == "reject" or opp.status == "rejected"
        ]
        accepted = [
            opp
            for opp in opportunities
            if opp.recommendation == "accept" or opp.status in ("accepted", "negotiating")
        ]

        # Analyze red flags in each group
        rejection_red_flags = self._extract_red_flags(rejected)
        acceptance_red_flags = self._extract_red_flags(accepted)

        # Calculate red flag statistics
        red_flag_stats = self._calculate_red_flag_stats(
            rejection_red_flags,
            acceptance_red_flags,
            len(rejected),
            len(accepted),
        )

        # Identify high-risk patterns
        high_risk_flags = self._identify_high_risk_flags(red_flag_stats)

        # Identify false positives (red flags that don't predict rejection)
        false_positive_flags = self._identify_false_positives(red_flag_stats)

        return {
            "total_opportunities": len(opportunities),
            "rejected_count": len(rejected),
            "accepted_count": len(accepted),
            "rejection_rate": (
                round(len(rejected) / len(opportunities), 3) if opportunities else 0.0
            ),
            "red_flag_stats": red_flag_stats,
            "high_risk_flags": high_risk_flags,
            "false_positive_flags": false_positive_flags,
            "period_days": days,
        }

    def learn_from_rejection(
        self,
        opportunity: FreelanceOpportunity,
        rejection_reason: Optional[str] = None,
    ) -> Optional[LearningRecord]:
        """
        Learn from a rejected opportunity.

        Args:
            opportunity: Rejected opportunity
            rejection_reason: Optional user-provided reason for rejection

        Returns:
            LearningRecord if learning was successful, None otherwise
        """
        try:
            # Extract risk analysis from opportunity
            risk_analysis = opportunity.risk_analysis or {}
            red_flags = risk_analysis.get("red_flags", [])
            risk_score = risk_analysis.get("risk_score", 0)

            # Input features
            input_features = {
                "title": opportunity.title,
                "description_length": len(opportunity.description or ""),
                "budget": opportunity.client_budget or 0.0,
                "client_rating": opportunity.client_rating or 0.0,
                "client_projects_count": opportunity.client_projects_count or 0,
                "red_flags_detected": red_flags,
                "red_flags_count": len(red_flags),
                "risk_score": risk_score,
            }

            # Predicted vs actual
            predicted_output = {
                "recommendation": opportunity.recommendation,
                "risk_level": risk_analysis.get("risk_level", "unknown"),
            }

            actual_output = {
                "user_decision": "rejected",
                "rejection_reason": rejection_reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Calculate accuracy (did model correctly predict rejection?)
            model_predicted_rejection = opportunity.recommendation == "reject"
            accuracy_score = 1.0 if model_predicted_rejection else 0.0

            # Create learning record
            learning_record = LearningRecord(
                user_id=self.user_id,
                learning_type="classification",  # Red flag classification
                input_features=input_features,
                predicted_output=predicted_output,
                actual_output=actual_output,
                accuracy_score=accuracy_score,
                user_feedback=rejection_reason,
                related_opportunity_id=opportunity.id,
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(learning_record)
            self.db.commit()
            self.db.refresh(learning_record)

            logger.info(
                f"Created rejection learning record {learning_record.id} for opportunity {opportunity.id}"
            )
            return learning_record

        except Exception as e:
            logger.error(f"Error learning from rejection {opportunity.id}: {e}")
            self.db.rollback()
            return None

    def suggest_risk_weight_adjustments(self) -> Dict[str, float]:
        """
        Suggest adjustments to red flag weights based on rejection correlation.

        Returns:
            Dictionary mapping red flags to suggested weight multipliers
        """
        analysis = self.analyze_rejection_patterns(days=90)

        if analysis["total_opportunities"] < 10:
            return {"message": "Insufficient data for weight adjustment suggestions"}

        red_flag_stats = analysis["red_flag_stats"]
        suggestions = {}

        for flag, stats in red_flag_stats.items():
            rejection_probability = stats["rejection_probability"]
            current_weight = 1.0  # Assume current weight is 1.0

            # Suggest weight based on rejection probability
            if rejection_probability > 0.80:
                # Very high rejection rate: increase weight significantly
                suggested_weight = current_weight * 1.5
            elif rejection_probability > 0.60:
                # High rejection rate: increase weight moderately
                suggested_weight = current_weight * 1.25
            elif rejection_probability < 0.30:
                # Low rejection rate: decrease weight (false positive)
                suggested_weight = current_weight * 0.75
            else:
                # Normal range: keep current weight
                suggested_weight = current_weight

            if suggested_weight != current_weight:
                suggestions[flag] = {
                    "current_weight": current_weight,
                    "suggested_weight": round(suggested_weight, 2),
                    "rejection_probability": rejection_probability,
                    "sample_size": stats["total_occurrences"],
                }

        return suggestions

    def discover_new_red_flags(self, days: int = 90) -> List[Dict]:
        """
        Discover potential new red flag patterns from rejection reasons.

        Analyzes user-provided rejection reasons to identify common themes
        that could become new automated red flags.

        Args:
            days: Number of days to analyze

        Returns:
            List of potential new red flag patterns
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get learning records with user feedback
        records = (
            self.db.query(LearningRecord)
            .filter(
                and_(
                    LearningRecord.user_id == self.user_id,
                    LearningRecord.learning_type == "classification",
                    LearningRecord.created_at >= cutoff_date,
                    LearningRecord.user_feedback.isnot(None),
                )
            )
            .all()
        )

        if not records:
            return []

        # Extract common themes from rejection reasons
        rejection_reasons = [r.user_feedback.lower() for r in records if r.user_feedback]

        # Count word frequencies (simple keyword extraction)
        keywords = Counter()
        for reason in rejection_reasons:
            words = reason.split()
            keywords.update([w for w in words if len(w) > 4])  # Words longer than 4 chars

        # Identify most common keywords not in known flags
        potential_flags = []
        for keyword, count in keywords.most_common(10):
            if count >= 3:  # Appeared at least 3 times
                # Check if not already covered by known flags
                is_new = all(keyword not in flag for flag in self.KNOWN_RED_FLAGS)
                if is_new:
                    potential_flags.append(
                        {
                            "keyword": keyword,
                            "occurrences": count,
                            "percentage": round(count / len(rejection_reasons), 2),
                        }
                    )

        return potential_flags

    def _extract_red_flags(self, opportunities: List[FreelanceOpportunity]) -> List[List[str]]:
        """Extract red flags from list of opportunities."""
        red_flags_list = []
        for opp in opportunities:
            if opp.risk_analysis and "red_flags" in opp.risk_analysis:
                red_flags_list.append(opp.risk_analysis["red_flags"])
            else:
                red_flags_list.append([])
        return red_flags_list

    def _calculate_red_flag_stats(
        self,
        rejection_flags: List[List[str]],
        acceptance_flags: List[List[str]],
        rejection_count: int,
        acceptance_count: int,
    ) -> Dict:
        """Calculate statistics for each red flag."""
        stats = {}

        # Count occurrences in each group
        rejection_counter = Counter()
        for flags in rejection_flags:
            rejection_counter.update(flags)

        acceptance_counter = Counter()
        for flags in acceptance_flags:
            acceptance_counter.update(flags)

        # Get all unique flags
        all_flags = set(rejection_counter.keys()) | set(acceptance_counter.keys())

        for flag in all_flags:
            in_rejections = rejection_counter[flag]
            in_acceptances = acceptance_counter[flag]
            total = in_rejections + in_acceptances

            # Calculate rejection probability (Bayes-like)
            if total > 0:
                rejection_prob = in_rejections / total
            else:
                rejection_prob = 0.0

            stats[flag] = {
                "in_rejections": in_rejections,
                "in_acceptances": in_acceptances,
                "total_occurrences": total,
                "rejection_probability": round(rejection_prob, 3),
                "rejection_rate_with_flag": (
                    round(in_rejections / rejection_count, 3) if rejection_count > 0 else 0.0
                ),
            }

        return stats

    def _identify_high_risk_flags(self, red_flag_stats: Dict) -> List[Dict]:
        """Identify red flags with high rejection probability."""
        high_risk = []

        for flag, stats in red_flag_stats.items():
            if stats["rejection_probability"] > 0.70 and stats["total_occurrences"] >= 3:
                high_risk.append(
                    {
                        "flag": flag,
                        "rejection_probability": stats["rejection_probability"],
                        "occurrences": stats["total_occurrences"],
                    }
                )

        # Sort by rejection probability
        high_risk.sort(key=lambda x: x["rejection_probability"], reverse=True)
        return high_risk

    def _identify_false_positives(self, red_flag_stats: Dict) -> List[Dict]:
        """Identify red flags that don't strongly predict rejection."""
        false_positives = []

        for flag, stats in red_flag_stats.items():
            if stats["rejection_probability"] < 0.40 and stats["total_occurrences"] >= 5:
                false_positives.append(
                    {
                        "flag": flag,
                        "rejection_probability": stats["rejection_probability"],
                        "occurrences": stats["total_occurrences"],
                        "note": "Low rejection correlation - may be false positive",
                    }
                )

        return false_positives
