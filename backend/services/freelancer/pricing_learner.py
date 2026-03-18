"""PricingLearner - Adaptive pricing parameter optimization.

This service learns from project execution outcomes to automatically adjust
pricing parameters, improving accuracy over time.

Learning Strategy:
- Analyzes completed projects to compare predicted vs. actual pricing
- Adjusts complexity, specialization, deadline, and client factors
- Creates versioned pricing parameters with auto_adjusted=True
- Maximizes both profitability and acceptance rate
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import (
    FreelanceOpportunity,
    LearningRecord,
    Negotiation,
    PricingParameter,
    ProjectExecution,
)

logger = logging.getLogger(__name__)


class PricingLearner:
    """
    Learns optimal pricing parameters from project execution feedback.

    Adjusts pricing factors based on:
    - Acceptance rates by complexity level
    - Negotiation outcomes (accepted/rejected/agreed)
    - Actual project profitability vs. estimated
    - Client satisfaction scores
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize PricingLearner.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

    def learn_from_execution(self, execution: ProjectExecution) -> Optional[LearningRecord]:
        """
        Learn from a completed project execution.

        Analyzes the project outcome and creates a learning record
        to inform future pricing adjustments.

        Args:
            execution: Completed ProjectExecution

        Returns:
            LearningRecord if learning was successful, None otherwise
        """
        try:
            # Get related opportunity
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.id == execution.opportunity_id)
                .first()
            )

            if not opportunity:
                logger.warning(f"Opportunity not found for execution {execution.id}")
                return None

            # Get negotiation record
            negotiation = (
                self.db.query(Negotiation)
                .filter(Negotiation.opportunity_id == opportunity.id)
                .first()
            )

            # Extract features (using actual model fields)
            input_features = {
                "complexity": opportunity.estimated_complexity or 5,
                "category": opportunity.category or "other",
                "client_budget": opportunity.client_budget or 0.0,
                "estimated_hours": opportunity.estimated_hours or 0.0,
                "client_rating": opportunity.client_rating or 0.0,
                "client_projects_count": opportunity.client_projects_count or 0,
            }

            # Calculate predicted vs actual (using actual model fields)
            predicted_value = opportunity.suggested_price
            actual_value = execution.negotiated_value

            # Calculate hourly rate from suggested_price and estimated_hours
            suggested_hourly_rate = None
            if opportunity.suggested_price and opportunity.estimated_hours:
                suggested_hourly_rate = opportunity.suggested_price / opportunity.estimated_hours
            elif opportunity.extracted_context:
                suggested_hourly_rate = opportunity.extracted_context.get("suggested_hourly_rate")

            predicted_output = {
                "suggested_value": predicted_value,
                "suggested_hourly_rate": suggested_hourly_rate,
            }

            actual_output = {
                "negotiated_value": actual_value,
                "outcome": negotiation.outcome if negotiation else "unknown",
                "client_satisfaction": execution.client_satisfaction,
                "actual_difficulty": execution.actual_difficulty,
                "completion_time_vs_estimate": self._calculate_time_variance(execution),
            }

            # Calculate accuracy
            accuracy_score = None
            error_margin = None
            if predicted_value and actual_value:
                error_margin = abs(predicted_value - actual_value) / predicted_value
                accuracy_score = max(0.0, 1.0 - error_margin)

            # Create learning record
            learning_record = LearningRecord(
                user_id=self.user_id,
                learning_type="pricing",
                input_features=input_features,
                predicted_output=predicted_output,
                actual_output=actual_output,
                accuracy_score=accuracy_score,
                error_margin=error_margin,
                related_opportunity_id=opportunity.id,
                related_execution_id=execution.id,
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(learning_record)
            self.db.commit()
            self.db.refresh(learning_record)

            logger.info(
                f"Created learning record {learning_record.id} for execution {execution.id}"
            )
            return learning_record

        except Exception as e:
            logger.error(f"Error learning from execution {execution.id}: {e}")
            self.db.rollback()
            return None

    def analyze_pricing_performance(self, days: int = 90) -> Dict:
        """
        Analyze pricing performance over recent period.

        Args:
            days: Number of days to analyze (default: 90)

        Returns:
            Performance analysis dictionary
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get learning records
        records = (
            self.db.query(LearningRecord)
            .filter(
                and_(
                    LearningRecord.user_id == self.user_id,
                    LearningRecord.learning_type == "pricing",
                    LearningRecord.created_at >= cutoff_date,
                    LearningRecord.accuracy_score.isnot(None),
                )
            )
            .all()
        )

        if not records:
            return {
                "total_records": 0,
                "message": f"No pricing learning records found in last {days} days",
            }

        # Calculate aggregate metrics
        total_records = len(records)
        avg_accuracy = sum(r.accuracy_score for r in records) / total_records
        avg_error_margin = sum(r.error_margin for r in records if r.error_margin) / len(
            [r for r in records if r.error_margin]
        )

        # Analyze by complexity
        complexity_analysis = self._analyze_by_dimension(records, "complexity")

        # Analyze by category
        category_analysis = self._analyze_by_dimension(records, "category")

        return {
            "total_records": total_records,
            "period_days": days,
            "avg_accuracy_score": round(avg_accuracy, 3),
            "avg_error_margin": round(avg_error_margin, 3),
            "complexity_performance": complexity_analysis,
            "category_performance": category_analysis,
            "needs_adjustment": avg_accuracy < 0.75,  # Flag if accuracy below 75%
        }

    def adjust_pricing_parameters(
        self,
        min_records: int = 10,
        adjustment_threshold: float = 0.75,
    ) -> Optional[PricingParameter]:
        """
        Automatically adjust pricing parameters based on learning records.

        Creates a new version of PricingParameter with adjusted factors
        if sufficient data exists and accuracy is below threshold.

        Args:
            min_records: Minimum learning records required (default: 10)
            adjustment_threshold: Accuracy threshold below which to adjust (default: 0.75)

        Returns:
            New PricingParameter if adjustment was made, None otherwise
        """
        try:
            # Analyze performance
            performance = self.analyze_pricing_performance(days=90)

            if performance["total_records"] < min_records:
                logger.info(
                    f"Insufficient records ({performance['total_records']}) for adjustment (need {min_records})"
                )
                return None

            if not performance["needs_adjustment"]:
                logger.info(
                    f"Accuracy {performance['avg_accuracy_score']} above threshold, no adjustment needed"
                )
                return None

            # Get current active pricing parameters
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
                logger.warning("No active pricing parameters found, cannot adjust")
                return None

            # Calculate adjusted factors
            adjusted_complexity_factors = self._adjust_complexity_factors(
                current_params.complexity_factors,
                performance["complexity_performance"],
            )

            adjusted_specialization_factors = self._adjust_specialization_factors(
                current_params.specialization_factors,
                performance["category_performance"],
            )

            # Deactivate current version
            current_params.active = False

            # Create new version with adjusted factors
            new_params = PricingParameter(
                user_id=self.user_id,
                version=current_params.version + 1,
                base_hourly_rate=current_params.base_hourly_rate,
                minimum_margin=current_params.minimum_margin,
                currency=current_params.currency,
                complexity_factors=adjusted_complexity_factors,
                specialization_factors=adjusted_specialization_factors,
                deadline_factors=current_params.deadline_factors,
                client_factors=current_params.client_factors,
                minimum_project_value=current_params.minimum_project_value,
                minimum_deadline_days=current_params.minimum_deadline_days,
                auto_adjusted=True,  # Mark as automatically adjusted
                based_on_executions_count=performance["total_records"],
                adjustment_reason=f"Auto-adjusted based on {performance['total_records']} executions. Avg accuracy: {performance['avg_accuracy_score']:.2%}",
                active=True,
                activated_at=datetime.now(timezone.utc),
            )

            self.db.add(new_params)
            self.db.commit()
            self.db.refresh(new_params)

            logger.info(f"Created auto-adjusted pricing parameters v{new_params.version}")
            return new_params

        except Exception as e:
            logger.error(f"Error adjusting pricing parameters: {e}")
            self.db.rollback()
            return None

    def _analyze_by_dimension(self, records: List[LearningRecord], dimension: str) -> Dict:
        """Analyze accuracy by a specific dimension (complexity or category)."""
        dimension_data = {}

        for record in records:
            value = record.input_features.get(dimension)
            if value is None:
                continue

            key = str(value)
            if key not in dimension_data:
                dimension_data[key] = {"count": 0, "total_accuracy": 0.0, "total_error": 0.0}

            dimension_data[key]["count"] += 1
            dimension_data[key]["total_accuracy"] += record.accuracy_score or 0.0
            dimension_data[key]["total_error"] += record.error_margin or 0.0

        # Calculate averages
        result = {}
        for key, data in dimension_data.items():
            result[key] = {
                "count": data["count"],
                "avg_accuracy": round(data["total_accuracy"] / data["count"], 3),
                "avg_error": round(data["total_error"] / data["count"], 3),
            }

        return result

    def _adjust_complexity_factors(
        self,
        current_factors: Dict,
        complexity_performance: Dict,
    ) -> Dict:
        """
        Adjust complexity factors based on performance.

        If a complexity level has low accuracy, adjust the factor to be more conservative.
        """
        adjusted_factors = current_factors.copy()

        for complexity_range, factor in current_factors.items():
            # Extract complexity number (e.g., "5-6" -> 5.5)
            try:
                parts = complexity_range.split("-")
                _ = (int(parts[0]) + int(parts[1])) / 2  # Validate range format
            except (ValueError, IndexError):
                continue

            # Check performance for this range
            perf = None
            for key in complexity_performance.keys():
                try:
                    comp_val = float(key)
                    if int(parts[0]) <= comp_val <= int(parts[1]):
                        perf = complexity_performance[key]
                        break
                except ValueError:
                    continue

            if perf and perf["avg_accuracy"] < 0.7:
                # Low accuracy: increase factor (charge more to be safe)
                adjustment = 1.0 + (0.7 - perf["avg_accuracy"])  # Max +30% increase
                adjusted_factors[complexity_range] = round(factor * adjustment, 2)
                logger.info(
                    f"Adjusted complexity {complexity_range}: {factor} -> {adjusted_factors[complexity_range]}"
                )

        return adjusted_factors

    def _adjust_specialization_factors(
        self,
        current_factors: Dict,
        category_performance: Dict,
    ) -> Dict:
        """
        Adjust specialization factors based on category performance.

        If a category has low accuracy, adjust the factor.
        """
        adjusted_factors = current_factors.copy()

        for category, factor in current_factors.items():
            perf = category_performance.get(category)

            if perf and perf["avg_accuracy"] < 0.7 and perf["count"] >= 3:
                # Low accuracy with sufficient data: adjust factor
                adjustment = 1.0 + (0.7 - perf["avg_accuracy"])
                adjusted_factors[category] = round(factor * adjustment, 2)
                logger.info(
                    f"Adjusted specialization {category}: {factor} -> {adjusted_factors[category]}"
                )

        return adjusted_factors

    def _calculate_time_variance(self, execution: ProjectExecution) -> Optional[float]:
        """Calculate how actual time compared to estimate."""
        if not execution.start_date or not execution.actual_end_date:
            return None

        actual_days = (execution.actual_end_date - execution.start_date).days
        planned_days = (execution.planned_end_date - execution.start_date).days

        if planned_days == 0:
            return None

        return (actual_days - planned_days) / planned_days  # Positive = took longer
