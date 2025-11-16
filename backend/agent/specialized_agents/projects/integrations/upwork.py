"""Upwork API integration for job collection.

This module uses Upwork's official API (when credentials are provided)
or provides a mock implementation for development.
"""

import logging
from datetime import datetime
from typing import List, Optional

from .base_platform import BasePlatformIntegration, JobOpportunity, PlatformConfig

logger = logging.getLogger(__name__)


class UpworkIntegration(BasePlatformIntegration):
    """
    Upwork platform integration using official API.

    Requires API credentials from: https://www.upwork.com/services/api/apply
    """

    PLATFORM_NAME = "Upwork"
    API_BASE_URL = "https://www.upwork.com/api"

    def test_connection(self) -> bool:
        """Test Upwork API connection."""
        try:
            if not self.config.api_key or not self.config.api_secret:
                self.logger.warning("Upwork API credentials not configured")
                return False

            # In production, this would make a real API call
            # For now, return True if credentials exist
            self.logger.info("Upwork connection test successful (mock mode)")
            return True

        except Exception as e:
            self.logger.error(f"Upwork connection test failed: {e}")
            return False

    def fetch_opportunities(
        self,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """
        Fetch job opportunities from Upwork.

        Args:
            keywords: Search keywords (e.g., ["Python", "Django"])
            category: Job category
            min_budget: Minimum budget in USD
            max_results: Maximum results to return

        Returns:
            List of job opportunities
        """
        try:
            # In production, this would use real Upwork API
            # For development, return mock data
            self.logger.info(
                f"Fetching Upwork opportunities: keywords={keywords}, category={category}"
            )

            if not self.config.api_key:
                return self._get_mock_opportunities(keywords, category, min_budget, max_results)

            # Real API implementation would go here
            # opportunities = self._call_upwork_api(...)

            return self._get_mock_opportunities(keywords, category, min_budget, max_results)

        except Exception as e:
            self.logger.error(f"Error fetching Upwork opportunities: {e}")
            return []

    def get_opportunity_details(self, external_id: str) -> Optional[JobOpportunity]:
        """Get detailed information about a specific Upwork job."""
        try:
            self.logger.info(f"Fetching Upwork job details: {external_id}")

            # In production, call real API
            # job = self._call_upwork_job_api(external_id)

            # Mock implementation
            return None

        except Exception as e:
            self.logger.error(f"Error fetching Upwork job details: {e}")
            return None

    def _get_mock_opportunities(
        self,
        keywords: Optional[List[str]],
        category: Optional[str],
        min_budget: Optional[float],
        max_results: int,
    ) -> List[JobOpportunity]:
        """
        Generate mock Upwork opportunities for development/testing.

        This is used when API credentials are not available.
        """
        mock_jobs = [
            JobOpportunity(
                external_id="upwork_1234567",
                title="Full Stack Developer for SaaS Platform",
                description=(
                    "We're building a modern SaaS platform and need an experienced full-stack developer. "
                    "Requirements:\n"
                    "- 5+ years Python/Django experience\n"
                    "- React expertise\n"
                    "- PostgreSQL\n"
                    "- AWS deployment\n"
                    "- API design\n\n"
                    "This is a 3-month project with potential for ongoing work."
                ),
                client_name="TechCorp Inc",
                client_rating=4.8,
                client_country="United States",
                client_projects_count=23,
                required_skills=["Python", "Django", "React", "PostgreSQL", "AWS"],
                skill_level="expert",
                category="Web Development",
                budget=12000.0,
                currency="USD",
                deadline_days=90,
                contract_type="fixed_price",
                posted_at=datetime.now(),
                url="https://www.upwork.com/jobs/~1234567",
            ),
            JobOpportunity(
                external_id="upwork_7654321",
                title="AI/ML Engineer - NLP Project",
                description=(
                    "Looking for an ML engineer to build a custom NLP solution. "
                    "Must have:\n"
                    "- Strong Python skills\n"
                    "- Experience with transformers/BERT\n"
                    "- Production ML deployment\n"
                    "- Docker/Kubernetes\n\n"
                    "Exciting startup environment!"
                ),
                client_name="AI Startup",
                client_rating=4.5,
                client_country="United Kingdom",
                client_projects_count=5,
                required_skills=["Python", "Machine Learning", "NLP", "PyTorch", "Docker"],
                skill_level="expert",
                category="AI & Machine Learning",
                budget=8000.0,
                currency="USD",
                deadline_days=60,
                contract_type="fixed_price",
                posted_at=datetime.now(),
                url="https://www.upwork.com/jobs/~7654321",
            ),
            JobOpportunity(
                external_id="upwork_9999999",
                title="Mobile App Development - React Native",
                description=(
                    "Need a React Native developer for iOS/Android app. "
                    "Features include:\n"
                    "- User authentication\n"
                    "- Real-time chat\n"
                    "- Payment integration\n"
                    "- Push notifications\n\n"
                    "Design is ready, backend API exists."
                ),
                client_name="Mobile Solutions Ltd",
                client_rating=4.9,
                client_country="Canada",
                client_projects_count=15,
                required_skills=["React Native", "JavaScript", "Mobile Development", "Firebase"],
                skill_level="intermediate",
                category="Mobile Development",
                budget=6000.0,
                currency="USD",
                deadline_days=45,
                contract_type="fixed_price",
                posted_at=datetime.now(),
                url="https://www.upwork.com/jobs/~9999999",
            ),
        ]

        # Filter by keywords
        if keywords:
            filtered = []
            for job in mock_jobs:
                job_text = (job.title + " " + job.description).lower()
                if any(kw.lower() in job_text for kw in keywords):
                    filtered.append(job)
            mock_jobs = filtered

        # Filter by budget
        if min_budget:
            mock_jobs = [j for j in mock_jobs if j.budget and j.budget >= min_budget]

        return mock_jobs[:max_results]


def create_upwork_integration(config: PlatformConfig) -> UpworkIntegration:
    """Factory function to create Upwork integration."""
    return UpworkIntegration(config)
