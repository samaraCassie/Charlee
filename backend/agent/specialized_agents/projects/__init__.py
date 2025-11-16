"""Projects Intelligence System - AI-powered freelance career management.

This module contains specialized agents for:
- Platform monitoring and project collection
- Semantic analysis and opportunity scoring
- Strategic pricing and negotiation
- Career insights and portfolio management
"""

from agent.specialized_agents.projects.collector_agent import CollectorAgent
from agent.specialized_agents.projects.semantic_analyzer_agent import (
    SemanticAnalyzerAgent,
)
from agent.specialized_agents.projects.project_evaluator_agent import (
    ProjectEvaluatorAgent,
)

__all__ = [
    "CollectorAgent",
    "SemanticAnalyzerAgent",
    "ProjectEvaluatorAgent",
]
