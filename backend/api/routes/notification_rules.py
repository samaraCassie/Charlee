"""API routes for managing notification filtering rules."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database import crud, schemas
from database.config import get_db
from database.models import User
from services.rule_engine import RuleEngine

router = APIRouter()


@router.get("/", response_model=schemas.NotificationRuleListResponse)
def get_notification_rules(
    enabled_only: bool = Query(False),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all notification rules for the current user.

    Args:
        enabled_only: If True, only return enabled rules

    Returns:
        List of notification rules ordered by priority
    """
    rules = crud.get_notification_rules(
        db, user_id=current_user.id, enabled_only=enabled_only, skip=skip, limit=limit
    )
    return {"total": len(rules), "rules": rules}


@router.get("/{rule_id}", response_model=schemas.NotificationRuleResponse)
def get_notification_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific notification rule by ID.

    Args:
        rule_id: ID of the rule

    Returns:
        Notification rule details

    Raises:
        404: Rule not found
    """
    rule = crud.get_notification_rule(db, rule_id=rule_id, user_id=current_user.id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification rule {rule_id} not found",
        )
    return rule


@router.post(
    "/", response_model=schemas.NotificationRuleResponse, status_code=status.HTTP_201_CREATED
)
def create_notification_rule(
    rule: schemas.NotificationRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new notification rule.

    Args:
        rule: Rule configuration (conditions, actions, priority)

    Returns:
        Created notification rule

    Example rule:
    {
        "name": "Archive recruiter emails",
        "description": "Auto-archive job opportunity emails",
        "enabled": true,
        "priority": 10,
        "conditions": {
            "all": [
                {"field": "extra_data.sender", "operator": "contains", "value": "recruiter"},
                {"field": "extra_data.subject", "operator": "contains", "value": "job opportunity"}
            ]
        },
        "actions": [
            {"type": "classify", "categoria": "spam"},
            {"type": "archive"}
        ]
    }
    """
    db_rule = crud.create_notification_rule(db, rule=rule, user_id=current_user.id)
    return db_rule


@router.patch("/{rule_id}", response_model=schemas.NotificationRuleResponse)
def update_notification_rule(
    rule_id: int,
    rule_update: schemas.NotificationRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a notification rule.

    Args:
        rule_id: ID of the rule to update
        rule_update: Fields to update

    Returns:
        Updated notification rule

    Raises:
        404: Rule not found
    """
    db_rule = crud.update_notification_rule(
        db, rule_id=rule_id, user_id=current_user.id, rule_update=rule_update
    )
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification rule {rule_id} not found",
        )
    return db_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a notification rule.

    Args:
        rule_id: ID of the rule to delete

    Raises:
        404: Rule not found
    """
    success = crud.delete_notification_rule(db, rule_id=rule_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification rule {rule_id} not found",
        )


@router.post("/{rule_id}/test", response_model=dict)
def test_notification_rule(
    rule_id: int,
    notification_id: int = Query(..., description="Notification ID to test the rule against"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Test a rule against a specific notification without executing actions.

    Args:
        rule_id: ID of the rule to test
        notification_id: ID of the notification to test against

    Returns:
        Test results showing if rule matches and what actions would execute

    Raises:
        404: Rule or notification not found
    """
    # Verify rule exists
    rule = crud.get_notification_rule(db, rule_id=rule_id, user_id=current_user.id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification rule {rule_id} not found",
        )

    # Test rule
    engine = RuleEngine(db, user_id=current_user.id)
    try:
        result = engine.test_rule(rule_id, notification_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing rule: {str(e)}",
        )


@router.post("/apply-to-existing", response_model=dict)
def apply_rules_to_existing(
    notification_ids: list[int] = Query(..., description="List of notification IDs to process"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply all enabled rules to existing notifications.

    Args:
        notification_ids: List of notification IDs to process

    Returns:
        Processing results

    Note:
        This is useful for retroactively applying new rules to existing notifications
    """
    engine = RuleEngine(db, user_id=current_user.id)
    try:
        result = engine.process_batch(notification_ids)
        return {
            "success": True,
            "processed": result["processed"],
            "actions_executed": result["actions_executed"],
            "errors": result["errors"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying rules: {str(e)}",
        )
