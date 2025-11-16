"""Collector Agent - Platform monitoring and project collection.

This agent is responsible for:
- Monitoring freelance platforms (Upwork, Freelancer.com, etc.)
- Collecting new project opportunities
- Normalizing data from different platforms
- Detecting and avoiding duplicates
- Saving opportunities to database
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from database.models import FreelancePlatform, FreelanceOpportunity

logger = logging.getLogger(__name__)


class CollectorAgent(Agent):
    """
    Agent that collects project opportunities from freelance platforms.

    Monitors configured platforms and automatically collects new opportunities
    for analysis and evaluation.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize CollectorAgent.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id

        super().__init__(
            name="Project Collector",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are a project collector agent for freelance platforms.",
                "You monitor platforms like Upwork, Freelancer.com, and collect new opportunities.",
                "You normalize data from different platforms into a standard format.",
                "You detect duplicates and only save new opportunities.",
                "You extract key information like title, description, budget, deadline, and required skills.",
            ],
            tools=[
                self.collect_from_all_platforms,
                self.collect_from_platform,
                self.get_active_platforms,
                self.manual_add_opportunity,
            ],
        )

    def get_active_platforms(self) -> str:
        """
        Get all active platforms for the user.

        Returns:
            JSON string with active platforms
        """
        try:
            platforms = (
                self.db.query(FreelancePlatform)
                .filter(
                    FreelancePlatform.user_id == self.user_id,
                    FreelancePlatform.active == True,  # noqa: E712
                )
                .all()
            )

            result = {
                "count": len(platforms),
                "platforms": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "type": p.platform_type,
                        "last_collection": (
                            p.last_collection_at.isoformat() if p.last_collection_at else None
                        ),
                        "total_collected": p.total_projects_collected,
                        "auto_collect": p.auto_collect,
                    }
                    for p in platforms
                ],
            }

            return f"Active platforms: {result}"

        except Exception as e:
            logger.error(f"Error getting active platforms: {e}")
            return f"Error: {str(e)}"

    def collect_from_all_platforms(self) -> str:
        """
        Collect projects from all active platforms.

        Returns:
            Summary of collection results
        """
        try:
            platforms = (
                self.db.query(FreelancePlatform)
                .filter(
                    FreelancePlatform.user_id == self.user_id,
                    FreelancePlatform.active == True,  # noqa: E712
                )
                .all()
            )

            if not platforms:
                return "No active platforms configured. Please add a platform first."

            total_collected = 0
            results = []

            for platform in platforms:
                try:
                    count = self._collect_from_single_platform(platform)
                    total_collected += count
                    results.append(f"{platform.name}: {count} new opportunities")

                    # Update platform statistics
                    platform.last_collection_at = datetime.now(timezone.utc)
                    platform.last_collection_count = count
                    platform.total_projects_collected += count
                    self.db.commit()

                except Exception as e:
                    logger.error(f"Error collecting from {platform.name}: {e}")
                    results.append(f"{platform.name}: Error - {str(e)}")

            summary = f"Collected {total_collected} new opportunities\n" + "\n".join(results)
            return summary

        except Exception as e:
            logger.error(f"Error in collect_from_all_platforms: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"

    def collect_from_platform(self, platform_id: int) -> str:
        """
        Collect projects from a specific platform.

        Args:
            platform_id: Platform ID to collect from

        Returns:
            Collection results
        """
        try:
            platform = (
                self.db.query(FreelancePlatform)
                .filter(
                    FreelancePlatform.id == platform_id,
                    FreelancePlatform.user_id == self.user_id,
                )
                .first()
            )

            if not platform:
                return f"Platform {platform_id} not found or access denied."

            if not platform.active:
                return f"Platform {platform.name} is not active."

            count = self._collect_from_single_platform(platform)

            # Update platform statistics
            platform.last_collection_at = datetime.now(timezone.utc)
            platform.last_collection_count = count
            platform.total_projects_collected += count
            self.db.commit()

            return f"Collected {count} new opportunities from {platform.name}"

        except Exception as e:
            logger.error(f"Error collecting from platform {platform_id}: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"

    def _collect_from_single_platform(self, platform: FreelancePlatform) -> int:
        """
        Internal method to collect from a single platform.

        Args:
            platform: Platform model instance

        Returns:
            Number of new opportunities collected
        """
        try:
            # Get platform-specific collector
            if platform.name.lower() == "upwork":
                opportunities = self._collect_upwork(platform)
            elif platform.name.lower() in ["freelancer.com", "freelancer"]:
                opportunities = self._collect_freelancer(platform)
            else:
                logger.warning(f"Unsupported platform: {platform.name}")
                return 0

            # Save opportunities (avoiding duplicates)
            saved_count = 0
            for opp_data in opportunities:
                if self._save_opportunity(platform, opp_data):
                    saved_count += 1

            return saved_count

        except Exception as e:
            logger.error(f"Error in _collect_from_single_platform: {e}")
            return 0

    def _collect_upwork(self, platform: FreelancePlatform) -> List[Dict[str, Any]]:
        """
        Collect opportunities from Upwork.

        Args:
            platform: Platform configuration

        Returns:
            List of opportunity data dictionaries

        Note:
            This is a placeholder. Real implementation would use Upwork API.
        """
        # TODO: Implement real Upwork API integration
        # For now, return empty list
        # In production, this would:
        # 1. Use OAuth credentials from platform.api_config
        # 2. Call Upwork API endpoint
        # 3. Parse response
        # 4. Return normalized data

        logger.info(f"Upwork collection not yet implemented for platform {platform.id}")
        return []

    def _collect_freelancer(self, platform: FreelancePlatform) -> List[Dict[str, Any]]:
        """
        Collect opportunities from Freelancer.com.

        Args:
            platform: Platform configuration

        Returns:
            List of opportunity data dictionaries

        Note:
            This is a placeholder. Real implementation would use Freelancer.com API.
        """
        # TODO: Implement real Freelancer.com API integration
        # For now, return empty list

        logger.info(f"Freelancer.com collection not yet implemented for platform {platform.id}")
        return []

    def _save_opportunity(self, platform: FreelancePlatform, data: Dict[str, Any]) -> bool:
        """
        Save an opportunity to database (avoiding duplicates).

        Args:
            platform: Platform the opportunity came from
            data: Opportunity data

        Returns:
            True if saved (new), False if duplicate
        """
        try:
            # Check for duplicate
            external_id = data.get("external_id")
            if external_id:
                existing = (
                    self.db.query(FreelanceOpportunity)
                    .filter(
                        FreelanceOpportunity.user_id == self.user_id,
                        FreelanceOpportunity.platform_id == platform.id,
                        FreelanceOpportunity.external_id == external_id,
                    )
                    .first()
                )

                if existing:
                    logger.debug(f"Duplicate opportunity found: {external_id}")
                    return False

            # Create new opportunity
            opportunity = FreelanceOpportunity(
                user_id=self.user_id,
                platform_id=platform.id,
                external_id=data.get("external_id"),
                title=data["title"],
                description=data["description"],
                client_name=data.get("client_name"),
                client_rating=data.get("client_rating"),
                client_country=data.get("client_country"),
                client_projects_count=data.get("client_projects_count"),
                required_skills=data.get("required_skills"),
                client_budget=data.get("budget"),
                client_currency=data.get("currency", "USD"),
                client_deadline_days=data.get("deadline_days"),
                contract_type=data.get("contract_type"),
                expires_at=data.get("expires_at"),
                status="new",
                collected_at=datetime.now(timezone.utc),
            )

            self.db.add(opportunity)
            self.db.commit()
            logger.info(f"Saved new opportunity: {opportunity.title[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
            self.db.rollback()
            return False

    def manual_add_opportunity(
        self,
        title: str,
        description: str,
        client_name: Optional[str] = None,
        budget: Optional[float] = None,
        deadline_days: Optional[int] = None,
        skills: Optional[str] = None,
    ) -> str:
        """
        Manually add an opportunity (for testing or direct input).

        Args:
            title: Project title
            description: Project description
            client_name: Client name
            budget: Budget amount
            deadline_days: Deadline in days
            skills: Comma-separated skills

        Returns:
            Confirmation message
        """
        try:
            # Parse skills
            required_skills = None
            if skills:
                required_skills = [s.strip() for s in skills.split(",")]

            opportunity = FreelanceOpportunity(
                user_id=self.user_id,
                platform_id=None,  # Manual entry, no platform
                title=title,
                description=description,
                client_name=client_name,
                required_skills=required_skills,
                client_budget=budget,
                client_deadline_days=deadline_days,
                status="new",
                collected_at=datetime.now(timezone.utc),
            )

            self.db.add(opportunity)
            self.db.commit()

            return f"✅ Manually added opportunity: '{title}' (ID: {opportunity.id})"

        except Exception as e:
            logger.error(f"Error adding manual opportunity: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"


def create_collector_agent(db: Session, user_id: int) -> CollectorAgent:
    """
    Factory function to create a CollectorAgent instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured CollectorAgent instance
    """
    return CollectorAgent(db=db, user_id=user_id)
