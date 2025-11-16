"""Projects Intelligence System - AI-powered freelance career management.

This module contains specialized agents for:
- Platform monitoring and project collection
- Semantic analysis and opportunity scoring
- Strategic pricing and evaluation
- Intelligent negotiation and counter-proposals
- Career insights and portfolio management
"""

from .career_insights_agent import CareerInsightsAgent, create_career_insights_agent
from .collector_agent import CollectorAgent, create_collector_agent
from .negotiation_engine import NegotiationEngine, create_negotiation_engine
from .portfolio_builder_agent import (
    PortfolioBuilderAgent,
    create_portfolio_builder_agent,
)
from .project_evaluator_agent import (
    ProjectEvaluatorAgent,
    create_project_evaluator_agent,
)
from .semantic_analyzer_agent import (
    SemanticAnalyzerAgent,
    create_semantic_analyzer_agent,
)

__all__ = [
    "CollectorAgent",
    "SemanticAnalyzerAgent",
    "ProjectEvaluatorAgent",
    "NegotiationEngine",
    "CareerInsightsAgent",
    "PortfolioBuilderAgent",
    "create_collector_agent",
    "create_semantic_analyzer_agent",
    "create_project_evaluator_agent",
    "create_negotiation_engine",
    "create_career_insights_agent",
    "create_portfolio_builder_agent",
]
