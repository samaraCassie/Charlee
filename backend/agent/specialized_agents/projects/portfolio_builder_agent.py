"""Portfolio Builder Agent - Automated portfolio generation from completed projects.

This agent provides:
- Automatic portfolio generation from completed projects
- Professional project descriptions
- Skills categorization and showcase
- Client testimonials organization
- Export formats for various platforms
"""

import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import (
    FreelanceOpportunity,
    ProjectExecution,
)

logger = logging.getLogger(__name__)


class PortfolioBuilderAgent(Agent):
    """
    Agent that automatically builds and manages professional portfolio.

    Generates portfolio content from completed projects, organizes by
    skills and categories, and provides export formats.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize PortfolioBuilderAgent.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        super().__init__(
            name="Portfolio Builder",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are a portfolio builder agent for freelancers.",
                "You create professional portfolio content from completed projects.",
                "You organize projects by skills, categories, and achievements.",
                "You generate compelling project descriptions that showcase value delivered.",
                "You help freelancers present their work in the best possible light.",
            ],
            tools=[
                self.build_full_portfolio,
                self.generate_project_description,
                self.categorize_projects,
                self.get_portfolio_by_skill,
                self.get_top_achievements,
            ],
        )

        self.db = db
        self.user_id = user_id

    def build_full_portfolio(self, include_in_progress: bool = False) -> str:
        """
        Build a complete portfolio from all completed projects.

        Args:
            include_in_progress: Whether to include in-progress projects

        Returns:
            Formatted portfolio content
        """
        try:
            # Get projects
            query = self.db.query(ProjectExecution).filter(
                ProjectExecution.user_id == self.user_id,
            )

            if include_in_progress:
                query = query.filter(ProjectExecution.status.in_(["completed", "in_progress"]))
            else:
                query = query.filter(ProjectExecution.status == "completed")

            projects = query.order_by(ProjectExecution.created_at.desc()).all()

            if not projects:
                return "No projects found for portfolio."

            # Build portfolio
            portfolio = "=== PROFESSIONAL PORTFOLIO ===\n\n"

            # Summary statistics
            completed = [p for p in projects if p.status == "completed"]
            portfolio += "PROFILE SUMMARY\n"
            portfolio += f"Total Projects Completed: {len(completed)}\n"

            total_value = sum(p.negotiated_value for p in completed)
            portfolio += f"Total Project Value: ${total_value:,.2f}\n"

            # Average client satisfaction
            with_rating = [p for p in completed if p.client_satisfaction is not None]
            if with_rating:
                avg_rating = sum(p.client_satisfaction for p in with_rating) / len(with_rating)
                portfolio += f"Average Client Satisfaction: {avg_rating:.1f}/5.0\n"

            # Skills summary
            all_skills = set()
            for project in projects:
                if project.opportunity and project.opportunity.required_skills:
                    all_skills.update(project.opportunity.required_skills)

            portfolio += f"Technical Skills: {', '.join(sorted(all_skills))}\n"
            portfolio += "\n" + "=" * 50 + "\n\n"

            # Individual projects
            portfolio += "FEATURED PROJECTS\n\n"
            for idx, project in enumerate(projects[:10], 1):  # Top 10 projects
                portfolio += f"{idx}. {project.opportunity.title if project.opportunity else 'Confidential Project'}\n"
                portfolio += f"   Status: {project.status.replace('_', ' ').title()}\n"
                portfolio += f"   Value: ${project.negotiated_value:,.2f}\n"

                if project.opportunity:
                    if project.opportunity.required_skills:
                        portfolio += (
                            f"   Technologies: {', '.join(project.opportunity.required_skills)}\n"
                        )

                    # Generate brief description
                    desc = project.opportunity.description
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    portfolio += f"   Description: {desc}\n"

                if project.client_satisfaction:
                    portfolio += f"   Client Rating: {project.client_satisfaction}/5.0\n"

                if project.client_feedback:
                    feedback = project.client_feedback
                    if len(feedback) > 150:
                        feedback = feedback[:150] + "..."
                    portfolio += f'   Client Feedback: "{feedback}"\n'

                portfolio += "\n"

            return portfolio

        except Exception as e:
            logger.error(f"Error building portfolio: {e}")
            return f"Error: {str(e)}"

    def generate_project_description(self, project_execution_id: int) -> str:
        """
        Generate a professional description for a specific project.

        Args:
            project_execution_id: Project execution ID

        Returns:
            Professional project description
        """
        try:
            project = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.id == project_execution_id,
                    ProjectExecution.user_id == self.user_id,
                )
                .first()
            )

            if not project:
                return f"Project {project_execution_id} not found."

            # Build professional description
            description = ""

            if project.opportunity:
                description += f"PROJECT: {project.opportunity.title}\n\n"

                description += "OVERVIEW:\n"
                description += f"{project.opportunity.description}\n\n"

                if project.opportunity.required_skills:
                    description += "TECHNOLOGIES USED:\n"
                    description += f"{', '.join(project.opportunity.required_skills)}\n\n"

            description += "PROJECT DETAILS:\n"
            description += f"Value: ${project.negotiated_value:,.2f}\n"
            description += f"Status: {project.status.replace('_', ' ').title()}\n"

            if project.start_date:
                description += f"Started: {project.start_date.strftime('%B %Y')}\n"

            if project.planned_end_date:
                description += (
                    f"Duration: {(project.planned_end_date - project.start_date).days} days\n"
                )

            if project.client_satisfaction:
                description += f"\nCLIENT SATISFACTION: {project.client_satisfaction}/5.0\n"

            if project.client_feedback:
                description += f'\nCLIENT TESTIMONIAL:\n"{project.client_feedback}"\n'

            return description

        except Exception as e:
            logger.error(f"Error generating project description: {e}")
            return f"Error: {str(e)}"

    def categorize_projects(self) -> str:
        """
        Categorize all projects by type and skill.

        Returns:
            Categorized project listing
        """
        try:
            projects = (
                self.db.query(ProjectExecution)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                )
                .all()
            )

            if not projects:
                return "No completed projects to categorize."

            # Categorize by skill
            skill_categories = {}
            for project in projects:
                if project.opportunity and project.opportunity.required_skills:
                    for skill in project.opportunity.required_skills:
                        if skill not in skill_categories:
                            skill_categories[skill] = []
                        skill_categories[skill].append(project)

            # Build report
            report = "=== PROJECTS BY CATEGORY ===\n\n"

            for skill in sorted(skill_categories.keys()):
                projects_list = skill_categories[skill]
                report += f"{skill.upper()} ({len(projects_list)} projects)\n"
                report += "-" * 50 + "\n"

                for project in projects_list[:5]:  # Top 5 per category
                    title = project.opportunity.title if project.opportunity else "Confidential"
                    report += f"  - {title} (${project.negotiated_value:,.2f})\n"

                report += "\n"

            return report

        except Exception as e:
            logger.error(f"Error categorizing projects: {e}")
            return f"Error: {str(e)}"

    def get_portfolio_by_skill(self, skill_name: str) -> str:
        """
        Get portfolio filtered by specific skill.

        Args:
            skill_name: Skill to filter by

        Returns:
            Filtered portfolio content
        """
        try:
            # Get projects with the specified skill
            projects = (
                self.db.query(ProjectExecution)
                .join(FreelanceOpportunity)
                .filter(
                    ProjectExecution.user_id == self.user_id,
                    ProjectExecution.status == "completed",
                )
                .all()
            )

            # Filter by skill
            matching_projects = []
            for project in projects:
                if project.opportunity and project.opportunity.required_skills:
                    if any(
                        skill_name.lower() in skill.lower()
                        for skill in project.opportunity.required_skills
                    ):
                        matching_projects.append(project)

            if not matching_projects:
                return f"No projects found with skill: {skill_name}"

            # Build portfolio
            portfolio = f"=== PORTFOLIO: {skill_name.upper()} PROJECTS ===\n\n"
            portfolio += f"Total Projects: {len(matching_projects)}\n"

            total_value = sum(p.negotiated_value for p in matching_projects)
            portfolio += f"Total Value: ${total_value:,.2f}\n"
            portfolio += "\n" + "=" * 50 + "\n\n"

            for idx, project in enumerate(matching_projects, 1):
                portfolio += f"{idx}. {project.opportunity.title}\n"
                portfolio += f"   Value: ${project.negotiated_value:,.2f}\n"

                if project.client_satisfaction:
                    portfolio += f"   Client Rating: {project.client_satisfaction}/5.0\n"

                if project.opportunity.description:
                    desc = project.opportunity.description
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    portfolio += f"   {desc}\n"

                portfolio += "\n"

            return portfolio

        except Exception as e:
            logger.error(f"Error getting skill portfolio: {e}")
            return f"Error: {str(e)}"

    def get_top_achievements(self, limit: int = 5) -> str:
        """
        Get top achievements and highlights for portfolio.

        Args:
            limit: Number of achievements to return

        Returns:
            Top achievements listing
        """
        try:
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

            achievements = []

            # Achievement: Highest value project
            highest_value = max(projects, key=lambda p: p.negotiated_value)
            achievements.append(
                f"Highest Value Project: ${highest_value.negotiated_value:,.2f} - "
                f"{highest_value.opportunity.title if highest_value.opportunity else 'Confidential'}"
            )

            # Achievement: Best client rating
            with_rating = [p for p in projects if p.client_satisfaction is not None]
            if with_rating:
                best_rated = max(with_rating, key=lambda p: p.client_satisfaction)
                if best_rated.client_satisfaction >= 4.5:
                    achievements.append(
                        f"Perfect Client Satisfaction: {best_rated.client_satisfaction}/5.0 - "
                        f"{best_rated.opportunity.title if best_rated.opportunity else 'Confidential'}"
                    )

            # Achievement: Total projects completed
            achievements.append(f"Total Projects Delivered: {len(projects)}")

            # Achievement: Total revenue
            total_revenue = sum(p.negotiated_value for p in projects)
            achievements.append(f"Total Project Revenue: ${total_revenue:,.2f}")

            # Achievement: Most used skill
            all_skills = []
            for project in projects:
                if project.opportunity and project.opportunity.required_skills:
                    all_skills.extend(project.opportunity.required_skills)

            if all_skills:
                from collections import Counter

                skill_counts = Counter(all_skills)
                top_skill, count = skill_counts.most_common(1)[0]
                achievements.append(f"Primary Expertise: {top_skill} ({count} projects)")

            # Build report
            report = "=== TOP ACHIEVEMENTS ===\n\n"
            for idx, achievement in enumerate(achievements[:limit], 1):
                report += f"{idx}. {achievement}\n"

            return report

        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return f"Error: {str(e)}"


def create_portfolio_builder_agent(db: Session, user_id: int) -> PortfolioBuilderAgent:
    """
    Factory function to create a PortfolioBuilderAgent instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured PortfolioBuilderAgent instance
    """
    return PortfolioBuilderAgent(db=db, user_id=user_id)
