"""Career Insights Agent - Analytics and strategic insights for freelance career.

This agent provides:
- Career performance analytics
- Skills progression tracking
- Project success pattern analysis
- Strategic recommendations for growth
- Income and project trend analysis
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import (
    FreelanceOpportunity,
    ProjectExecution,
    Negotiation,
)

logger = logging.getLogger(__name__)


class CareerInsightsAgent(Agent):
    """
    Agent that provides career analytics and strategic insights.

    Analyzes completed projects, success patterns, skill development,
    and provides recommendations for career growth.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize CareerInsightsAgent.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

        super().__init__(
            name="Career Insights Analyst",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are a career insights analyst for freelancers.",
                "You analyze completed projects to identify success patterns.",
                "You track skills development and project performance over time.",
                "You provide strategic recommendations for career growth.",
                "You generate actionable insights based on data analysis.",
            ],
            tools=[
                self.get_career_summary,
                self.analyze_skills_progression,
                self.identify_top_performing_projects,
                self.get_income_trends,
                self.generate_career_recommendations,
            ],
        )

    def get_career_summary(self, days: int = 90) -> str:
        """
        Get a comprehensive career summary for recent period.

        Args:
            days: Number of days to analyze (default: 90)

        Returns:
            Formatted career summary report
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            # Get completed projects
            completed_projects = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                    ProjectExecution.created_at >= cutoff_date,
                )
                .all()
            )

            if not completed_projects:
                return f"No completed projects found in the last {days} days."

            # Calculate metrics
            total_projects = len(completed_projects)
            total_revenue = sum(p.negotiated_value for p in completed_projects)
            avg_project_value = total_revenue / total_projects if total_projects > 0 else 0

            # Client satisfaction
            projects_with_rating = [
                p for p in completed_projects if p.client_satisfaction is not None
            ]
            avg_satisfaction = (
                sum(p.client_satisfaction for p in projects_with_rating) / len(projects_with_rating)
                if projects_with_rating
                else None
            )

            # Skills frequency
            all_skills = []
            for project in completed_projects:
                if project.opportunity and project.opportunity.required_skills:
                    all_skills.extend(project.opportunity.required_skills)

            skill_counts = {}
            for skill in all_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # Build report
            report = f"=== Career Summary ({days} days) ===\n\n"
            report += f"Projects Completed: {total_projects}\n"
            report += f"Total Revenue: ${total_revenue:,.2f}\n"
            report += f"Average Project Value: ${avg_project_value:,.2f}\n"

            if avg_satisfaction:
                report += f"Average Client Satisfaction: {avg_satisfaction:.1f}/5.0\n"

            report += "\nTop Skills Used:\n"
            for skill, count in top_skills:
                report += f"  - {skill}: {count} projects\n"

            return report

        except Exception as e:
            logger.error(f"Error generating career summary: {e}")
            return f"Error: {str(e)}"

    def analyze_skills_progression(self, skill_name: Optional[str] = None) -> str:
        """
        Analyze skills development over time.

        Args:
            skill_name: Optional specific skill to analyze

        Returns:
            Skills progression analysis
        """
        try:
            # Get all completed projects with opportunities
            completed_projects = (
                self.db.query(ProjectExecution)
                .join(FreelanceOpportunity)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                )
                .order_by(ProjectExecution.created_at)
                .all()
            )

            if not completed_projects:
                return "No completed projects found for skills analysis."

            # Track skill usage over time
            skill_timeline = {}
            for project in completed_projects:
                if project.opportunity and project.opportunity.required_skills:
                    month_key = project.created_at.strftime("%Y-%m")
                    if month_key not in skill_timeline:
                        skill_timeline[month_key] = {}

                    for skill in project.opportunity.required_skills:
                        if skill_name is None or skill.lower() == skill_name.lower():
                            skill_timeline[month_key][skill] = (
                                skill_timeline[month_key].get(skill, 0) + 1
                            )

            # Build report
            if skill_name:
                report = f"=== Skills Progression: {skill_name} ===\n\n"
            else:
                report = "=== Overall Skills Progression ===\n\n"

            for month in sorted(skill_timeline.keys()):
                report += f"\n{month}:\n"
                for skill, count in sorted(
                    skill_timeline[month].items(), key=lambda x: x[1], reverse=True
                ):
                    report += f"  - {skill}: {count} projects\n"

            return report

        except Exception as e:
            logger.error(f"Error analyzing skills progression: {e}")
            return f"Error: {str(e)}"

    def identify_top_performing_projects(self, limit: int = 10) -> str:
        """
        Identify top-performing projects based on multiple criteria.

        Args:
            limit: Number of top projects to return

        Returns:
            Top performing projects analysis
        """
        try:
            # Get completed projects
            projects = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                )
                .all()
            )

            if not projects:
                return "No completed projects found."

            # Score projects based on multiple factors
            scored_projects = []
            for project in projects:
                score = 0

                # Client satisfaction (0-50 points)
                if project.client_satisfaction:
                    score += project.client_satisfaction * 10

                # Project value (0-50 points based on percentile)
                if project.negotiated_value:
                    value_percentile = sum(
                        1 for p in projects if p.negotiated_value < project.negotiated_value
                    ) / len(projects)
                    score += value_percentile * 50

                scored_projects.append((project, score))

            # Sort by score
            scored_projects.sort(key=lambda x: x[1], reverse=True)
            top_projects = scored_projects[:limit]

            # Build report
            report = f"=== Top {limit} Performing Projects ===\n\n"
            for idx, (project, score) in enumerate(top_projects, 1):
                report += f"{idx}. {project.opportunity.title if project.opportunity else 'Manual Entry'}\n"
                report += f"   Score: {score:.1f}/100\n"
                report += f"   Value: ${project.negotiated_value:,.2f}\n"
                if project.client_satisfaction:
                    report += f"   Client Satisfaction: {project.client_satisfaction}/5\n"
                if project.opportunity and project.opportunity.required_skills:
                    report += f"   Skills: {', '.join(project.opportunity.required_skills[:3])}\n"
                report += "\n"

            return report

        except Exception as e:
            logger.error(f"Error identifying top projects: {e}")
            return f"Error: {str(e)}"

    def get_income_trends(self, months: int = 6) -> str:
        """
        Analyze income trends over time.

        Args:
            months: Number of months to analyze

        Returns:
            Income trend analysis
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=months * 30)

            # Get completed projects
            projects = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                    ProjectExecution.created_at >= cutoff_date,
                )
                .order_by(ProjectExecution.created_at)
                .all()
            )

            if not projects:
                return f"No completed projects found in the last {months} months."

            # Group by month
            monthly_income = {}
            for project in projects:
                month_key = project.created_at.strftime("%Y-%m")
                if month_key not in monthly_income:
                    monthly_income[month_key] = {"revenue": 0, "count": 0}

                monthly_income[month_key]["revenue"] += project.negotiated_value
                monthly_income[month_key]["count"] += 1

            # Calculate trend
            total_revenue = sum(m["revenue"] for m in monthly_income.values())
            total_projects = sum(m["count"] for m in monthly_income.values())
            avg_monthly_revenue = total_revenue / len(monthly_income) if monthly_income else 0

            # Build report
            report = f"=== Income Trends ({months} months) ===\n\n"
            report += f"Total Revenue: ${total_revenue:,.2f}\n"
            report += f"Total Projects: {total_projects}\n"
            report += f"Average Monthly Revenue: ${avg_monthly_revenue:,.2f}\n\n"

            report += "Monthly Breakdown:\n"
            for month in sorted(monthly_income.keys()):
                data = monthly_income[month]
                report += f"  {month}: ${data['revenue']:,.2f} ({data['count']} projects)\n"

            return report

        except Exception as e:
            logger.error(f"Error analyzing income trends: {e}")
            return f"Error: {str(e)}"

    def generate_career_recommendations(self) -> str:
        """
        Generate strategic career recommendations based on data analysis.

        Returns:
            Career recommendations report
        """
        try:
            # Get recent data (last 90 days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

            completed_projects = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                    ProjectExecution.created_at >= cutoff_date,
                )
                .all()
            )

            # Analyze negotiation success rate
            negotiations = (
                self.db.query(Negotiation)
                .filter(
                    Negotiation.user_id == self.user_id,
                    Negotiation.created_at >= cutoff_date,
                )
                .all()
            )

            successful_negotiations = [n for n in negotiations if n.outcome == "agreed"]
            negotiation_success_rate = (
                len(successful_negotiations) / len(negotiations) * 100 if negotiations else 0
            )

            # Identify high-value skills
            skill_values = {}
            for project in completed_projects:
                if project.opportunity and project.opportunity.required_skills:
                    for skill in project.opportunity.required_skills:
                        if skill not in skill_values:
                            skill_values[skill] = {"total": 0, "count": 0}
                        skill_values[skill]["total"] += project.negotiated_value
                        skill_values[skill]["count"] += 1

            avg_skill_values = {
                skill: data["total"] / data["count"] for skill, data in skill_values.items()
            }
            top_value_skills = sorted(avg_skill_values.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]

            # Build recommendations
            report = "=== Career Recommendations ===\n\n"

            # Recommendation 1: High-value skills
            if top_value_skills:
                report += "1. Focus on High-Value Skills:\n"
                report += (
                    "   Based on your completed projects, these skills command the highest rates:\n"
                )
                for skill, avg_value in top_value_skills[:3]:
                    report += f"   - {skill}: avg ${avg_value:,.2f} per project\n"
                report += "\n"

            # Recommendation 2: Negotiation improvement
            if negotiation_success_rate < 70:
                report += "2. Improve Negotiation Success Rate:\n"
                report += f"   Current success rate: {negotiation_success_rate:.1f}%\n"
                report += "   Consider refining your proposal strategy and value justification.\n\n"
            else:
                report += "2. Negotiation Performance:\n"
                report += f"   Strong success rate: {negotiation_success_rate:.1f}%\n"
                report += "   Continue current negotiation strategies.\n\n"

            # Recommendation 3: Project volume
            if len(completed_projects) < 3:
                report += "3. Increase Project Volume:\n"
                report += "   Consider expanding your platform presence and bidding frequency.\n\n"
            else:
                report += "3. Project Volume:\n"
                report += (
                    f"   Good activity level with {len(completed_projects)} completed projects.\n\n"
                )

            # Recommendation 4: Client satisfaction
            projects_with_rating = [
                p for p in completed_projects if p.client_satisfaction is not None
            ]
            if projects_with_rating:
                avg_satisfaction = sum(p.client_satisfaction for p in projects_with_rating) / len(
                    projects_with_rating
                )
                if avg_satisfaction < 4.0:
                    report += "4. Client Satisfaction:\n"
                    report += f"   Current average: {avg_satisfaction:.1f}/5.0\n"
                    report += "   Focus on communication and delivery quality.\n\n"
                else:
                    report += "4. Client Satisfaction:\n"
                    report += f"   Excellent rating: {avg_satisfaction:.1f}/5.0\n"
                    report += "   Maintain current service standards.\n\n"

            return report

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"Error: {str(e)}"


def create_career_insights_agent(db: Session, user_id: int) -> CareerInsightsAgent:
    """
    Factory function to create a CareerInsightsAgent instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured CareerInsightsAgent instance
    """
    return CareerInsightsAgent(db=db, user_id=user_id)
