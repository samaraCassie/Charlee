"""Platform integrations for freelance job collection.

This module provides integrations with popular freelance platforms:
- Upwork (API client)
- Freelancer.com (API client)
- LinkedIn Jobs (web scraping)
- Generic RSS feed parser

All integrations respect platform ToS and rate limits.
"""

from .base_platform import BasePlatformIntegration, JobOpportunity, PlatformConfig
from .freelancer_com import (
    FreelancerComIntegration,
    create_freelancer_com_integration,
)
from .linkedin_jobs import LinkedInJobsIntegration, create_linkedin_jobs_integration
from .rss_feed import RSSFeedIntegration, create_rss_feed_integration
from .upwork import UpworkIntegration, create_upwork_integration

__all__ = [
    "BasePlatformIntegration",
    "PlatformConfig",
    "JobOpportunity",
    "UpworkIntegration",
    "FreelancerComIntegration",
    "LinkedInJobsIntegration",
    "RSSFeedIntegration",
    "create_upwork_integration",
    "create_freelancer_com_integration",
    "create_linkedin_jobs_integration",
    "create_rss_feed_integration",
]
