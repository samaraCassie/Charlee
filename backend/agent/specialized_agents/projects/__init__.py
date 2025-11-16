"""Projects Intelligence System - AI-powered freelance career management.

This module contains specialized agents for:
- Platform monitoring and project collection
- Semantic analysis and opportunity scoring
- Strategic pricing and evaluation
- Intelligent negotiation and counter-proposals
- Career insights and portfolio management
"""

from .collector_agent import CollectorAgent, create_collector_agent
from .negotiation_engine import NegotiationEngine, create_negotiation_engine
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
    "create_collector_agent",
    "create_semantic_analyzer_agent",
    "create_project_evaluator_agent",
    "create_negotiation_engine",
]
