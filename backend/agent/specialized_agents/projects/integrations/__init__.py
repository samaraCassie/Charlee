"""Platform integrations for freelance job collection.

This module provides integrations with popular freelance platforms:
- Upwork (API client)
- Freelancer.com (API client)
- LinkedIn Jobs (web scraping)
- Generic RSS feed parser

All integrations respect platform ToS and rate limits.
"""

from .base_platform import BasePlatformIntegration, PlatformConfig
from .freelancer_com import FreelancerComIntegration
from .linkedin_jobs import LinkedInJobsIntegration
from .rss_feed import RSSFeedIntegration
from .upwork import UpworkIntegration

__all__ = [
    "BasePlatformIntegration",
    "PlatformConfig",
    "UpworkIntegration",
    "FreelancerComIntegration",
    "LinkedInJobsIntegration",
    "RSSFeedIntegration",
]
