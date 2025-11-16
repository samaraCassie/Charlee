"""Projects Intelligence System API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.specialized_agents.projects.career_insights_agent import (
    create_career_insights_agent,
)
from agent.specialized_agents.projects.collector_agent import create_collector_agent
from agent.specialized_agents.projects.negotiation_engine import (
    create_negotiation_engine,
)
from agent.specialized_agents.projects.portfolio_builder_agent import (
    create_portfolio_builder_agent,
)
from agent.specialized_agents.projects.project_evaluator_agent import (
    create_project_evaluator_agent,
)
from agent.specialized_agents.projects.semantic_analyzer_agent import (
    create_semantic_analyzer_agent,
)
from api.auth.dependencies import get_current_user
from api.cache import invalidate_pattern
from database import crud, schemas
from database.config import get_db
from database.models import User

router = APIRouter()


# ==================== FreelancePlatform Routes ====================


@router.get("/platforms/", response_model=schemas.FreelancePlatformListResponse)
def get_platforms(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of freelance platforms for the authenticated user."""
    platforms = crud.get_platforms(
        db, user_id=current_user.id, skip=skip, limit=limit, active_only=active_only
    )
    return {"total": len(platforms), "platforms": platforms}


@router.get("/platforms/{platform_id}", response_model=schemas.FreelancePlatformResponse)
def get_platform(
    platform_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single freelance platform by ID for the authenticated user."""
    platform = crud.get_platform(db, platform_id, user_id=current_user.id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.post("/platforms/", response_model=schemas.FreelancePlatformResponse, status_code=201)
def create_platform(
    platform: schemas.FreelancePlatformCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new freelance platform for the authenticated user."""
    result = crud.create_platform(db, platform, user_id=current_user.id)
    invalidate_pattern("projects:platforms:*")
    return result


@router.patch("/platforms/{platform_id}", response_model=schemas.FreelancePlatformResponse)
def update_platform(
    platform_id: int,
    platform_update: schemas.FreelancePlatformUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a freelance platform for the authenticated user."""
    platform = crud.update_platform(db, platform_id, platform_update, user_id=current_user.id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    invalidate_pattern("projects:platforms:*")
    return platform


@router.delete("/platforms/{platform_id}", status_code=204)
def delete_platform(
    platform_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a freelance platform for the authenticated user."""
    success = crud.delete_platform(db, platform_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Platform not found")
    invalidate_pattern("projects:platforms:*")
    return None


# ==================== FreelanceOpportunity Routes ====================


@router.get("/opportunities/", response_model=schemas.FreelanceOpportunityListResponse)
def get_opportunities(
    status: str | None = None,
    platform_id: int | None = None,
    min_score: float | None = None,
    recommendation: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of freelance opportunities for the authenticated user with filters."""
    opportunities = crud.get_opportunities(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        platform_id=platform_id,
        min_score=min_score,
        recommendation=recommendation,
    )
    return {"total": len(opportunities), "opportunities": opportunities}


@router.get(
    "/opportunities/{opportunity_id}",
    response_model=schemas.FreelanceOpportunityResponse,
)
def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single freelance opportunity by ID for the authenticated user."""
    opportunity = crud.get_opportunity(db, opportunity_id, user_id=current_user.id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.post(
    "/opportunities/",
    response_model=schemas.FreelanceOpportunityResponse,
    status_code=201,
)
def create_opportunity(
    opportunity: schemas.FreelanceOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new freelance opportunity for the authenticated user."""
    try:
        result = crud.create_opportunity(db, opportunity, user_id=current_user.id)
        invalidate_pattern("projects:opportunities:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/opportunities/{opportunity_id}",
    response_model=schemas.FreelanceOpportunityResponse,
)
def update_opportunity(
    opportunity_id: int,
    opportunity_update: schemas.FreelanceOpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a freelance opportunity for the authenticated user."""
    opportunity = crud.update_opportunity(
        db, opportunity_id, opportunity_update, user_id=current_user.id
    )
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    invalidate_pattern("projects:opportunities:*")
    return opportunity


@router.delete("/opportunities/{opportunity_id}", status_code=204)
def delete_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a freelance opportunity for the authenticated user."""
    success = crud.delete_opportunity(db, opportunity_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    invalidate_pattern("projects:opportunities:*")
    return None


# ==================== Agent Action Routes ====================


@router.post("/collect", status_code=202)
def collect_opportunities(
    platform_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger collection of opportunities from platforms using CollectorAgent."""
    try:
        agent = create_collector_agent(db=db, user_id=current_user.id)

        if platform_id:
            result = agent.collect_from_platform(platform_id)
        else:
            result = agent.collect_from_all_platforms()

        invalidate_pattern("projects:opportunities:*")
        return {"message": "Collection started", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")


@router.post(
    "/opportunities/{opportunity_id}/analyze",
    response_model=schemas.FreelanceOpportunityResponse,
)
def analyze_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze an opportunity using SemanticAnalyzerAgent."""
    try:
        agent = create_semantic_analyzer_agent(db=db, user_id=current_user.id)
        agent.analyze_opportunity(opportunity_id)

        # Refresh opportunity from database
        opportunity = crud.get_opportunity(db, opportunity_id, user_id=current_user.id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        invalidate_pattern("projects:opportunities:*")
        return opportunity

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/opportunities/analyze-batch", status_code=202)
def batch_analyze_opportunities(
    status: str = "new",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Batch analyze multiple opportunities using SemanticAnalyzerAgent."""
    try:
        agent = create_semantic_analyzer_agent(db=db, user_id=current_user.id)
        result = agent.batch_analyze_opportunities(status=status, limit=limit)

        invalidate_pattern("projects:opportunities:*")
        return {"message": "Batch analysis started", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.post(
    "/opportunities/{opportunity_id}/evaluate",
    response_model=schemas.FreelanceOpportunityResponse,
)
def evaluate_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate an opportunity using ProjectEvaluatorAgent."""
    try:
        agent = create_project_evaluator_agent(db=db, user_id=current_user.id)
        agent.evaluate_opportunity(opportunity_id)

        # Refresh opportunity from database
        opportunity = crud.get_opportunity(db, opportunity_id, user_id=current_user.id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        invalidate_pattern("projects:opportunities:*")
        return opportunity

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/opportunities/evaluate-batch", status_code=202)
def batch_evaluate_opportunities(
    status: str = "analyzed",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Batch evaluate multiple opportunities using ProjectEvaluatorAgent."""
    try:
        agent = create_project_evaluator_agent(db=db, user_id=current_user.id)
        result = agent.batch_evaluate(status=status, limit=limit)

        invalidate_pattern("projects:opportunities:*")
        return {"message": "Batch evaluation started", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")


# ==================== PricingParameter Routes ====================


@router.get("/pricing-parameters/", response_model=schemas.PricingParameterListResponse)
def get_pricing_parameters(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of pricing parameters for the authenticated user."""
    params = crud.get_pricing_parameters(
        db, user_id=current_user.id, skip=skip, limit=limit, active_only=active_only
    )
    return {"total": len(params), "pricing_parameters": params}


@router.get("/pricing-parameters/active", response_model=schemas.PricingParameterResponse)
def get_active_pricing_parameter(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current active pricing parameter for the authenticated user."""
    param = crud.get_active_pricing_parameter(db, user_id=current_user.id)
    if not param:
        raise HTTPException(status_code=404, detail="No active pricing parameter found")
    return param


@router.get("/pricing-parameters/{param_id}", response_model=schemas.PricingParameterResponse)
def get_pricing_parameter(
    param_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single pricing parameter by ID for the authenticated user."""
    param = crud.get_pricing_parameter(db, param_id, user_id=current_user.id)
    if not param:
        raise HTTPException(status_code=404, detail="Pricing parameter not found")
    return param


@router.post(
    "/pricing-parameters/",
    response_model=schemas.PricingParameterResponse,
    status_code=201,
)
def create_pricing_parameter(
    pricing_param: schemas.PricingParameterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new pricing parameter version for the authenticated user."""
    result = crud.create_pricing_parameter(db, pricing_param, user_id=current_user.id)
    invalidate_pattern("projects:pricing:*")
    return result


@router.patch("/pricing-parameters/{param_id}", response_model=schemas.PricingParameterResponse)
def update_pricing_parameter(
    param_id: int,
    pricing_update: schemas.PricingParameterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a pricing parameter for the authenticated user."""
    param = crud.update_pricing_parameter(db, param_id, pricing_update, user_id=current_user.id)
    if not param:
        raise HTTPException(status_code=404, detail="Pricing parameter not found")
    invalidate_pattern("projects:pricing:*")
    return param


@router.delete("/pricing-parameters/{param_id}", status_code=204)
def delete_pricing_parameter(
    param_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a pricing parameter for the authenticated user (only if not active)."""
    try:
        success = crud.delete_pricing_parameter(db, param_id, user_id=current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Pricing parameter not found")
        invalidate_pattern("projects:pricing:*")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ProjectExecution Routes ====================


@router.get("/executions/", response_model=schemas.ProjectExecutionListResponse)
def get_project_executions(
    status: str | None = None,
    opportunity_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of project executions for the authenticated user with filters."""
    executions = crud.get_project_executions(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        opportunity_id=opportunity_id,
    )
    return {"total": len(executions), "executions": executions}


@router.get("/executions/{execution_id}", response_model=schemas.ProjectExecutionResponse)
def get_project_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single project execution by ID for the authenticated user."""
    execution = crud.get_project_execution(db, execution_id, user_id=current_user.id)
    if not execution:
        raise HTTPException(status_code=404, detail="Project execution not found")
    return execution


@router.post("/executions/", response_model=schemas.ProjectExecutionResponse, status_code=201)
def create_project_execution(
    execution: schemas.ProjectExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project execution for the authenticated user."""
    try:
        result = crud.create_project_execution(db, execution, user_id=current_user.id)
        invalidate_pattern("projects:executions:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/executions/{execution_id}", response_model=schemas.ProjectExecutionResponse)
def update_project_execution(
    execution_id: int,
    execution_update: schemas.ProjectExecutionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project execution for the authenticated user."""
    execution = crud.update_project_execution(
        db, execution_id, execution_update, user_id=current_user.id
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Project execution not found")
    invalidate_pattern("projects:executions:*")
    return execution


@router.delete("/executions/{execution_id}", status_code=204)
def delete_project_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project execution for the authenticated user."""
    success = crud.delete_project_execution(db, execution_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project execution not found")
    invalidate_pattern("projects:executions:*")
    return None


# ==================== Negotiation Routes ====================


@router.get("/negotiations/", response_model=schemas.NegotiationListResponse)
def get_negotiations(
    opportunity_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of negotiations for the authenticated user with filters."""
    negotiations = crud.get_negotiations(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        opportunity_id=opportunity_id,
        status=status,
    )
    return {"total": len(negotiations), "negotiations": negotiations}


@router.get("/negotiations/{negotiation_id}", response_model=schemas.NegotiationResponse)
def get_negotiation(
    negotiation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single negotiation by ID for the authenticated user."""
    negotiation = crud.get_negotiation(db, negotiation_id, user_id=current_user.id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return negotiation


@router.post("/negotiations/", response_model=schemas.NegotiationResponse, status_code=201)
def create_negotiation(
    negotiation: schemas.NegotiationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new negotiation record for the authenticated user."""
    try:
        result = crud.create_negotiation(db, negotiation, user_id=current_user.id)
        invalidate_pattern("projects:negotiations:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/negotiations/{negotiation_id}", response_model=schemas.NegotiationResponse)
def update_negotiation(
    negotiation_id: int,
    negotiation_update: schemas.NegotiationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a negotiation for the authenticated user."""
    negotiation = crud.update_negotiation(
        db, negotiation_id, negotiation_update, user_id=current_user.id
    )
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    invalidate_pattern("projects:negotiations:*")
    return negotiation


@router.delete("/negotiations/{negotiation_id}", status_code=204)
def delete_negotiation(
    negotiation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a negotiation for the authenticated user."""
    success = crud.delete_negotiation(db, negotiation_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    invalidate_pattern("projects:negotiations:*")
    return None


# ==================== Intelligent Negotiation Routes (NegotiationEngine) ====================


@router.post("/opportunities/{opportunity_id}/generate-counter-proposal")
def generate_counter_proposal(
    opportunity_id: int,
    original_budget: float | None = None,
    justification_style: str = "value_based",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an intelligent counter-proposal using NegotiationEngine.

    Args:
        opportunity_id: Opportunity ID
        original_budget: Client's original budget (optional, uses opportunity.client_budget if not provided)
        justification_style: value_based, market_based, or effort_based
    """
    try:
        agent = create_negotiation_engine(db=db, user_id=current_user.id)
        result = agent.generate_counter_proposal(
            opportunity_id=opportunity_id,
            original_budget=original_budget,
            justification_style=justification_style,
        )

        invalidate_pattern("projects:negotiations:*")
        return {"message": "Counter-proposal generated", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Counter-proposal generation failed: {str(e)}")


@router.post("/negotiations/{negotiation_id}/generate-message")
def generate_negotiation_message(
    negotiation_id: int,
    tone: str = "professional",
    include_alternatives: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a diplomatic negotiation message using NegotiationEngine.

    Args:
        negotiation_id: Negotiation record ID
        tone: professional, friendly, or firm
        include_alternatives: Include scope/timeline alternatives
    """
    try:
        agent = create_negotiation_engine(db=db, user_id=current_user.id)
        result = agent.generate_negotiation_message(
            negotiation_id=negotiation_id,
            tone=tone,
            include_alternatives=include_alternatives,
        )

        invalidate_pattern(f"projects:negotiations:{negotiation_id}")
        return {"message": "Negotiation message generated", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation failed: {str(e)}")


@router.get("/opportunities/{opportunity_id}/scope-adjustments")
def suggest_scope_adjustments(
    opportunity_id: int,
    target_budget: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Suggest scope adjustments to match a target budget using NegotiationEngine.

    Args:
        opportunity_id: Opportunity ID
        target_budget: Target budget to match
    """
    try:
        agent = create_negotiation_engine(db=db, user_id=current_user.id)
        result = agent.suggest_scope_adjustments(
            opportunity_id=opportunity_id,
            target_budget=target_budget,
        )

        return {"message": "Scope adjustments suggested", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scope adjustment analysis failed: {str(e)}")


@router.get("/opportunities/{opportunity_id}/negotiation-gap-analysis")
def analyze_negotiation_gap(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze the gap between client budget and suggested pricing using NegotiationEngine.

    Args:
        opportunity_id: Opportunity ID
    """
    try:
        agent = create_negotiation_engine(db=db, user_id=current_user.id)
        result = agent.analyze_negotiation_gap(opportunity_id=opportunity_id)

        return {"message": "Gap analysis completed", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")


@router.get("/negotiations/history")
def get_negotiation_history(
    opportunity_id: int | None = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get negotiation history for learning using NegotiationEngine.

    Args:
        opportunity_id: Optional opportunity ID to filter by
        limit: Maximum number of records
    """
    try:
        agent = create_negotiation_engine(db=db, user_id=current_user.id)
        result = agent.get_negotiation_history(
            opportunity_id=opportunity_id,
            limit=limit,
        )

        return {"message": "Negotiation history retrieved", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


# ==================== Career Insights Routes ====================


@router.get("/insights/career-summary")
def get_career_summary(
    days: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive career summary for recent period.

    Args:
        days: Number of days to analyze (default: 90)
    """
    try:
        agent = create_career_insights_agent(db=db, user_id=current_user.id)
        result = agent.get_career_summary(days=days)
        return {"message": "Career summary generated", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Career summary failed: {str(e)}")


@router.get("/insights/skills-progression")
def analyze_skills_progression(
    skill_name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze skills development over time.

    Args:
        skill_name: Optional specific skill to analyze
    """
    try:
        agent = create_career_insights_agent(db=db, user_id=current_user.id)
        result = agent.analyze_skills_progression(skill_name=skill_name)
        return {"message": "Skills progression analyzed", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skills analysis failed: {str(e)}")


@router.get("/insights/top-performing-projects")
def identify_top_performing_projects(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Identify top-performing projects based on multiple criteria.

    Args:
        limit: Number of top projects to return (default: 10)
    """
    try:
        agent = create_career_insights_agent(db=db, user_id=current_user.id)
        result = agent.identify_top_performing_projects(limit=limit)
        return {"message": "Top projects identified", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top projects analysis failed: {str(e)}")


@router.get("/insights/income-trends")
def get_income_trends(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze income trends over time.

    Args:
        months: Number of months to analyze (default: 6)
    """
    try:
        agent = create_career_insights_agent(db=db, user_id=current_user.id)
        result = agent.get_income_trends(months=months)
        return {"message": "Income trends analyzed", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Income trends analysis failed: {str(e)}")


@router.get("/insights/career-recommendations")
def generate_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate strategic career recommendations based on data analysis."""
    try:
        agent = create_career_insights_agent(db=db, user_id=current_user.id)
        result = agent.generate_career_recommendations()
        return {"message": "Career recommendations generated", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


# ==================== Portfolio Builder Routes ====================


@router.get("/portfolio/full")
def build_full_portfolio(
    include_in_progress: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Build a complete portfolio from all completed projects.

    Args:
        include_in_progress: Whether to include in-progress projects (default: False)
    """
    try:
        agent = create_portfolio_builder_agent(db=db, user_id=current_user.id)
        result = agent.build_full_portfolio(include_in_progress=include_in_progress)
        return {"message": "Portfolio built successfully", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio build failed: {str(e)}")


@router.get("/portfolio/projects/{project_execution_id}/description")
def generate_project_description(
    project_execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a professional description for a specific project.

    Args:
        project_execution_id: Project execution ID
    """
    try:
        agent = create_portfolio_builder_agent(db=db, user_id=current_user.id)
        result = agent.generate_project_description(project_execution_id=project_execution_id)
        return {"message": "Project description generated", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Description generation failed: {str(e)}")


@router.get("/portfolio/categorized")
def categorize_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Categorize all projects by type and skill."""
    try:
        agent = create_portfolio_builder_agent(db=db, user_id=current_user.id)
        result = agent.categorize_projects()
        return {"message": "Projects categorized", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")


@router.get("/portfolio/by-skill/{skill_name}")
def get_portfolio_by_skill(
    skill_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get portfolio filtered by specific skill.

    Args:
        skill_name: Skill to filter by
    """
    try:
        agent = create_portfolio_builder_agent(db=db, user_id=current_user.id)
        result = agent.get_portfolio_by_skill(skill_name=skill_name)
        return {"message": "Skill portfolio retrieved", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill portfolio retrieval failed: {str(e)}")


@router.get("/portfolio/achievements")
def get_top_achievements(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get top achievements and highlights for portfolio.

    Args:
        limit: Number of achievements to return (default: 5)
    """
    try:
        agent = create_portfolio_builder_agent(db=db, user_id=current_user.id)
        result = agent.get_top_achievements(limit=limit)
        return {"message": "Top achievements retrieved", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Achievements retrieval failed: {str(e)}")
