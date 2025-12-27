"""Semantic Analyzer Agent - Deep AI analysis of project opportunities.

This agent is responsible for:
- Semantic analysis of project descriptions
- Generating embeddings for similarity search
- Estimating complexity and technical level
- Detecting red flags and opportunities
- Classifying client intent
- Finding similar historical projects
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from openai import OpenAI
from sqlalchemy.orm import Session

from database.models import FreelanceOpportunity

logger = logging.getLogger(__name__)


class SemanticAnalyzerAgent(Agent):
    """
    Agent that performs deep semantic analysis of project opportunities.

    Uses AI to understand project requirements, detect patterns,
    and provide intelligent insights about opportunities.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize SemanticAnalyzerAgent.

        Args:
            db: Database session
            user_id: User ID for multi-tenancy
        """
        self.db = db
        self.user_id = user_id
        self.openai_client = OpenAI()  # For embeddings

        super().__init__(
            name="Semantic Analyzer",
            model=OpenAIChat(id="gpt-4o"),  # Use stronger model for analysis
            instructions=[
                "You are an expert technical project analyzer.",
                "You analyze freelance project descriptions to extract key information.",
                "You identify project complexity (1-10), technical level (junior/mid/senior/expert), and category.",
                "You detect red flags like unrealistic budgets, vague requirements, or suspicious clients.",
                "You identify opportunities like portfolio value, skill development, or networking potential.",
                "You classify client intent as 'serious_project', 'test', or 'exploration'.",
                "You estimate realistic hours needed based on requirements.",
                "Always provide detailed justifications for your analysis.",
            ],
            tools=[
                self.analyze_opportunity,
                self.batch_analyze_opportunities,
                self.find_similar_projects,
                self.get_analysis_summary,
            ],
        )

    def analyze_opportunity(self, opportunity_id: int) -> str:
        """
        Perform comprehensive semantic analysis on an opportunity.

        Args:
            opportunity_id: Opportunity ID to analyze

        Returns:
            Analysis results
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.id == opportunity_id,
                    FreelanceOpportunity.user_id == self.user_id,
                )
                .first()
            )

            if not opportunity:
                return f"Opportunity {opportunity_id} not found or access denied."

            if opportunity.status != "new":
                return f"Opportunity already analyzed (status: {opportunity.status})"

            # Perform analysis
            analysis = self._perform_analysis(opportunity)

            # Generate embedding
            embedding = self._generate_embedding(opportunity.description)

            # Find similar historical projects
            similar_projects = self._find_similar_historical_projects(embedding, limit=5)

            # Update opportunity with analysis results
            opportunity.estimated_complexity = analysis["complexity"]
            opportunity.skill_level = analysis["skill_level"]
            opportunity.category = analysis["category"]
            opportunity.estimated_hours = analysis["estimated_hours"]
            opportunity.client_intent = analysis["client_intent"]
            opportunity.red_flags = analysis["red_flags"]
            opportunity.opportunities = analysis["opportunities"]
            opportunity.extracted_context = analysis
            opportunity.description_embedding = embedding
            opportunity.analyzed_at = datetime.now(timezone.utc)
            opportunity.status = "analyzed"

            self.db.commit()

            # Format response
            result = {
                "opportunity_id": opportunity_id,
                "title": opportunity.title,
                "analysis": {
                    "complexity": f"{analysis['complexity']}/10",
                    "skill_level": analysis["skill_level"],
                    "category": analysis["category"],
                    "estimated_hours": analysis["estimated_hours"],
                    "client_intent": analysis["client_intent"],
                    "red_flags_count": len(analysis["red_flags"]),
                    "opportunities_count": len(analysis["opportunities"]),
                },
                "red_flags": analysis["red_flags"],
                "opportunities": analysis["opportunities"],
                "similar_projects_found": len(similar_projects),
                "status": "✅ Analysis complete",
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error analyzing opportunity {opportunity_id}: {e}")
            self.db.rollback()
            return f"Error: {str(e)}"

    def _perform_analysis(self, opportunity: FreelanceOpportunity) -> Dict[str, Any]:
        """
        Use AI to analyze the opportunity in depth.

        Args:
            opportunity: Opportunity to analyze

        Returns:
            Analysis results dictionary
        """
        # Build comprehensive prompt for analysis
        prompt = f"""
Analyze this freelance project opportunity in depth:

TITLE: {opportunity.title}

DESCRIPTION:
{opportunity.description}

CLIENT INFORMATION:
- Name: {opportunity.client_name or 'Unknown'}
- Rating: {opportunity.client_rating or 'N/A'}
- Country: {opportunity.client_country or 'Unknown'}
- Previous projects: {opportunity.client_projects_count or 0}

COMMERCIAL CONDITIONS:
- Budget: ${opportunity.client_budget or 'Not specified'} {opportunity.client_currency}
- Deadline: {opportunity.client_deadline_days or 'Not specified'} days
- Contract type: {opportunity.contract_type or 'Not specified'}

REQUIRED SKILLS:
{', '.join(opportunity.required_skills) if opportunity.required_skills else 'Not specified'}

Provide a comprehensive analysis in JSON format with:
1. complexity: Integer 1-10 (1=very simple, 10=very complex)
2. skill_level: One of: "junior", "mid", "senior", "expert"
3. category: One of: "full_stack", "backend", "frontend", "ai_ml", "devops", "mobile", "data", "other"
4. estimated_hours: Realistic hours needed (float)
5. client_intent: One of: "serious_project", "test", "exploration"
6. red_flags: Array of warning signs (e.g., "unrealistic_budget", "vague_requirements", "suspicious_client", "impossible_deadline")
7. opportunities: Array of positive aspects (e.g., "portfolio_value", "skill_development", "networking", "recurring_potential", "well_defined_scope")
8. technical_requirements: Array of key technical requirements
9. scope_clarity: "clear", "moderate", or "vague"
10. risk_level: "low", "medium", or "high"

Return ONLY valid JSON, no markdown formatting.
"""

        try:
            # Call OpenAI for analysis
            response = self.model.response(messages=[{"role": "user", "content": prompt}])

            # Parse JSON response
            analysis_text = response.content
            # Remove markdown code blocks if present
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

            analysis = json.loads(analysis_text)

            # Validate and ensure all required fields exist
            required_fields = [
                "complexity",
                "skill_level",
                "category",
                "estimated_hours",
                "client_intent",
                "red_flags",
                "opportunities",
            ]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            return analysis

        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Return safe default values
            return {
                "complexity": 5,
                "skill_level": "mid",
                "category": "other",
                "estimated_hours": 40.0,
                "client_intent": "serious_project",
                "red_flags": ["analysis_error"],
                "opportunities": [],
                "error": str(e),
            }

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None on error
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002", input=text[:8000]  # Limit to 8K chars
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _find_similar_historical_projects(
        self, embedding: Optional[List[float]], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar projects from execution history using vector similarity.

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results

        Returns:
            List of similar projects with metadata
        """
        if not embedding:
            return []

        try:
            from database.models import FreelanceOpportunity
            from sqlalchemy import text

            # Query for similar projects using pgvector
            # Note: This requires the vector extension to be installed in PostgreSQL

            # Convert embedding list to pgvector format
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

            # Use pgvector's <-> operator for L2 distance (or <#> for inner product, <=> for cosine)
            # Lower distance = more similar
            query = text(
                """
                SELECT
                    id,
                    title,
                    description,
                    category,
                    skill_level,
                    client_budget,
                    status,
                    (embedding <-> :query_embedding::vector) as distance
                FROM freelance_opportunities
                WHERE user_id = :user_id
                    AND embedding IS NOT NULL
                    AND status = 'completed'
                ORDER BY embedding <-> :query_embedding::vector
                LIMIT :limit
            """
            )

            result = self.db.execute(
                query,
                {
                    "query_embedding": embedding_str,
                    "user_id": self.user_id,
                    "limit": limit,
                },
            )

            similar_projects = []
            for row in result:
                similar_projects.append(
                    {
                        "id": row.id,
                        "title": row.title,
                        "description": (
                            row.description[:200] + "..."
                            if row.description and len(row.description) > 200
                            else row.description
                        ),
                        "category": row.category,
                        "skill_level": row.skill_level,
                        "client_budget": row.client_budget,
                        "status": row.status,
                        "similarity_distance": round(float(row.distance), 4),
                    }
                )

            logger.info(f"Found {len(similar_projects)} similar projects using vector search")
            return similar_projects

        except Exception as e:
            # If pgvector is not installed or embedding column doesn't exist,
            # fall back to simple category matching
            logger.warning(f"Vector similarity search failed, using fallback: {e}")

            try:
                from database.models import FreelanceOpportunity

                # Fallback: Get completed projects from same category
                # This is a simple fallback when pgvector is not available
                similar = (
                    self.db.query(FreelanceOpportunity)
                    .filter(
                        FreelanceOpportunity.user_id == self.user_id,
                        FreelanceOpportunity.status == "completed",
                    )
                    .order_by(FreelanceOpportunity.created_at.desc())
                    .limit(limit)
                    .all()
                )

                return [
                    {
                        "id": opp.id,
                        "title": opp.title,
                        "description": (
                            opp.description[:200] + "..."
                            if opp.description and len(opp.description) > 200
                            else opp.description
                        ),
                        "category": opp.category,
                        "skill_level": opp.skill_level,
                        "client_budget": opp.client_budget,
                        "status": opp.status,
                        "similarity_distance": None,  # No distance in fallback
                    }
                    for opp in similar
                ]

            except Exception as fallback_error:
                logger.error(f"Fallback similarity search also failed: {fallback_error}")
                return []

    def batch_analyze_opportunities(self, status: str = "new", limit: int = 10) -> str:
        """
        Analyze multiple opportunities in batch.

        Args:
            status: Status filter (default: "new")
            limit: Maximum number to analyze

        Returns:
            Batch analysis results
        """
        try:
            opportunities = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.status == status,
                )
                .limit(limit)
                .all()
            )

            if not opportunities:
                return f"No opportunities found with status '{status}'"

            results = []
            for opp in opportunities:
                try:
                    self.analyze_opportunity(opp.id)
                    results.append(f"✅ {opp.title[:50]}...")
                except Exception as e:
                    logger.error(f"Error analyzing opportunity {opp.id}: {e}")
                    results.append(f"❌ {opp.title[:50]}... - Error: {str(e)}")

            summary = f"Analyzed {len(results)} opportunities:\n" + "\n".join(results)
            return summary

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return f"Error: {str(e)}"

    def find_similar_projects(self, opportunity_id: int, limit: int = 5) -> str:
        """
        Find similar projects to the given opportunity.

        Args:
            opportunity_id: Opportunity ID
            limit: Maximum number of similar projects

        Returns:
            Similar projects information
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.id == opportunity_id,
                    FreelanceOpportunity.user_id == self.user_id,
                )
                .first()
            )

            if not opportunity:
                return f"Opportunity {opportunity_id} not found"

            if not opportunity.description_embedding:
                return "Opportunity not yet analyzed. Please analyze first."

            similar = self._find_similar_historical_projects(
                opportunity.description_embedding, limit=limit
            )

            if not similar:
                return "No similar projects found in history."

            result = {
                "opportunity": opportunity.title,
                "similar_projects_found": len(similar),
                "projects": similar,
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error finding similar projects: {e}")
            return f"Error: {str(e)}"

    def get_analysis_summary(self, days: int = 7) -> str:
        """
        Get summary of recent analysis activity.

        Args:
            days: Number of days to look back

        Returns:
            Analysis summary
        """
        try:
            from datetime import timedelta

            since_date = datetime.now(timezone.utc) - timedelta(days=days)

            opportunities = (
                self.db.query(FreelanceOpportunity)
                .filter(
                    FreelanceOpportunity.user_id == self.user_id,
                    FreelanceOpportunity.analyzed_at >= since_date,
                )
                .all()
            )

            if not opportunities:
                return f"No opportunities analyzed in the last {days} days."

            # Calculate statistics
            total = len(opportunities)
            by_complexity = {}
            by_category = {}
            total_red_flags = 0
            total_opportunities_count = 0

            for opp in opportunities:
                # Complexity distribution
                complexity = opp.estimated_complexity or 0
                by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

                # Category distribution
                category = opp.category or "unknown"
                by_category[category] = by_category.get(category, 0) + 1

                # Red flags and opportunities
                if opp.red_flags:
                    total_red_flags += len(opp.red_flags)
                if opp.opportunities:
                    total_opportunities_count += len(opp.opportunities)

            avg_complexity = (
                sum(o.estimated_complexity for o in opportunities if o.estimated_complexity) / total
            )

            summary = {
                "period": f"Last {days} days",
                "total_analyzed": total,
                "average_complexity": round(avg_complexity, 1),
                "complexity_distribution": by_complexity,
                "category_distribution": by_category,
                "total_red_flags": total_red_flags,
                "total_opportunities": total_opportunities_count,
                "avg_red_flags_per_project": round(total_red_flags / total, 1),
                "avg_opportunities_per_project": round(total_opportunities_count / total, 1),
            }

            return json.dumps(summary, indent=2)

        except Exception as e:
            logger.error(f"Error getting analysis summary: {e}")
            return f"Error: {str(e)}"


def create_semantic_analyzer_agent(db: Session, user_id: int) -> SemanticAnalyzerAgent:
    """
    Factory function to create a SemanticAnalyzerAgent instance.

    Args:
        db: Database session
        user_id: User ID for multi-tenancy

    Returns:
        Configured SemanticAnalyzerAgent instance
    """
    return SemanticAnalyzerAgent(db=db, user_id=user_id)
