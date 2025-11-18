"""
RuleEngine - Automated notification filtering and action execution.

This engine processes custom user-defined rules to automatically classify,
archive, and take actions on incoming notifications.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database import crud
from database.models import Notification, NotificationRule

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Rule engine for automated notification processing.

    Evaluates user-defined rules against notifications and executes
    corresponding actions like archiving, classification, task creation, etc.
    """

    def __init__(self, db: Session, user_id: int):
        """
        Initialize rule engine.

        Args:
            db: Database session
            user_id: User ID
        """
        self.db = db
        self.user_id = user_id

    def evaluate_notification(self, notification: Notification) -> List[Dict]:
        """
        Evaluate all rules against a notification.

        Args:
            notification: Notification to evaluate

        Returns:
            List of actions executed
        """
        # Get enabled rules for user, ordered by priority
        rules = (
            self.db.query(NotificationRule)
            .filter_by(user_id=self.user_id, enabled=True)
            .order_by(NotificationRule.priority.desc())
            .all()
        )

        executed_actions = []

        for rule in rules:
            try:
                # Check if rule conditions match
                if self._evaluate_conditions(notification, rule.conditions):
                    logger.info(
                        f"Rule {rule.id} ({rule.name}) matched notification {notification.id}"
                    )

                    # Execute rule actions
                    actions = self._execute_actions(notification, rule.actions)
                    executed_actions.extend(actions)

                    # Update rule statistics
                    rule.times_triggered += 1
                    rule.last_triggered = datetime.now(timezone.utc)
                    self.db.commit()

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
                continue

        return executed_actions

    def _evaluate_conditions(self, notification: Notification, conditions: Dict) -> bool:
        """
        Evaluate rule conditions against notification.

        Conditions format:
        {
            "all": [  # All conditions must match (AND)
                {"field": "sender", "operator": "contains", "value": "recruiter"},
                {"field": "subject", "operator": "contains", "value": "job"}
            ],
            "any": [  # Any condition must match (OR)
                {"field": "priority", "operator": ">=", "value": 4}
            ]
        }

        Args:
            notification: Notification to check
            conditions: Conditions dict

        Returns:
            True if conditions match, False otherwise
        """
        # Handle "all" conditions (AND logic)
        if "all" in conditions:
            all_conditions = conditions["all"]
            if not all(self._check_condition(notification, cond) for cond in all_conditions):
                return False

        # Handle "any" conditions (OR logic)
        if "any" in conditions:
            any_conditions = conditions["any"]
            if not any(self._check_condition(notification, cond) for cond in any_conditions):
                return False

        return True

    def _check_condition(self, notification: Notification, condition: Dict) -> bool:
        """
        Check a single condition against notification.

        Args:
            notification: Notification to check
            condition: Single condition dict

        Returns:
            True if condition matches, False otherwise
        """
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Get field value from notification
        field_value = self._get_field_value(notification, field)

        if field_value is None:
            return False

        # Apply operator
        return self._apply_operator(field_value, operator, value)

    def _get_field_value(self, notification: Notification, field: str) -> Any:
        """
        Extract field value from notification.

        Supports dot notation for nested fields (e.g., "extra_data.sender")

        Args:
            notification: Notification object
            field: Field name (supports dot notation)

        Returns:
            Field value or None
        """
        # Handle direct fields
        if hasattr(notification, field):
            return getattr(notification, field)

        # Handle nested fields (e.g., extra_data.sender)
        if "." in field:
            parts = field.split(".")
            value = notification

            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None

                if value is None:
                    return None

            return value

        # Check in extra_data
        if notification.extra_data and field in notification.extra_data:
            return notification.extra_data[field]

        # Check in contexto
        if notification.contexto and field in notification.contexto:
            return notification.contexto[field]

        return None

    def _apply_operator(self, field_value: Any, operator: str, target_value: Any) -> bool:
        """
        Apply comparison operator.

        Supported operators:
        - equals, ==
        - not_equals, !=
        - contains
        - not_contains
        - starts_with
        - ends_with
        - regex
        - >, <, >=, <=
        - in, not_in

        Args:
            field_value: Value from notification
            operator: Operator string
            target_value: Target value to compare

        Returns:
            True if comparison passes, False otherwise
        """
        try:
            # Normalize operator
            operator = operator.lower().strip()

            # String operations
            if operator in ["equals", "=="]:
                return str(field_value).lower() == str(target_value).lower()

            if operator in ["not_equals", "!="]:
                return str(field_value).lower() != str(target_value).lower()

            if operator == "contains":
                return str(target_value).lower() in str(field_value).lower()

            if operator == "not_contains":
                return str(target_value).lower() not in str(field_value).lower()

            if operator == "starts_with":
                return str(field_value).lower().startswith(str(target_value).lower())

            if operator == "ends_with":
                return str(field_value).lower().endswith(str(target_value).lower())

            if operator == "regex":
                return bool(re.search(str(target_value), str(field_value), re.IGNORECASE))

            # Numeric operations
            if operator == ">":
                return float(field_value) > float(target_value)

            if operator == "<":
                return float(field_value) < float(target_value)

            if operator == ">=":
                return float(field_value) >= float(target_value)

            if operator == "<=":
                return float(field_value) <= float(target_value)

            # List operations
            if operator == "in":
                return field_value in target_value

            if operator == "not_in":
                return field_value not in target_value

            logger.warning(f"Unknown operator: {operator}")
            return False

        except Exception as e:
            logger.error(f"Error applying operator {operator}: {e}")
            return False

    def _execute_actions(self, notification: Notification, actions: List[Dict]) -> List[Dict]:
        """
        Execute rule actions on notification.

        Supported actions:
        - classify: Set categoria
        - set_priority: Set prioridade
        - archive: Mark as archived
        - mark_read: Mark as read
        - create_task: Create a task from notification
        - snooze: Snooze notification until time
        - delete: Delete notification

        Args:
            notification: Notification to act on
            actions: List of action dicts

        Returns:
            List of executed actions with results
        """
        executed = []

        for action in actions:
            try:
                action_type = action.get("type")

                if action_type == "classify":
                    categoria = action.get("categoria")
                    notification.categoria = categoria
                    executed.append({"type": "classify", "categoria": categoria})

                elif action_type == "set_priority":
                    prioridade = action.get("prioridade")
                    notification.prioridade = prioridade
                    executed.append({"type": "set_priority", "prioridade": prioridade})

                elif action_type == "archive":
                    notification.arquivada = True
                    executed.append({"type": "archive"})

                elif action_type == "mark_read":
                    notification.mark_as_read()
                    executed.append({"type": "mark_read"})

                elif action_type == "create_task":
                    # Create task from notification
                    task_title = action.get("title", notification.title)
                    task_description = action.get("description", notification.message)

                    # Note: This requires task creation logic
                    # For now, just mark the action
                    notification.acao_sugerida = "criar_tarefa"
                    executed.append(
                        {
                            "type": "create_task",
                            "title": task_title,
                            "description": task_description,
                        }
                    )

                elif action_type == "snooze":
                    # Snooze notification
                    snooze_until = action.get("until")
                    if snooze_until:
                        notification.snooze_until = snooze_until
                        executed.append({"type": "snooze", "until": snooze_until})

                elif action_type == "delete":
                    # Delete notification
                    self.db.delete(notification)
                    executed.append({"type": "delete"})

                else:
                    logger.warning(f"Unknown action type: {action_type}")

            except Exception as e:
                logger.error(f"Error executing action {action.get('type')}: {e}")
                continue

        # Commit changes
        self.db.commit()

        return executed

    def process_batch(self, notification_ids: List[int]) -> Dict:
        """
        Process rules for multiple notifications.

        Args:
            notification_ids: List of notification IDs

        Returns:
            Dict with summary of actions executed
        """
        results = {"processed": 0, "actions_executed": 0, "errors": []}

        for notification_id in notification_ids:
            try:
                notification = crud.get_notification(self.db, notification_id, self.user_id)
                if not notification:
                    continue

                actions = self.evaluate_notification(notification)
                results["processed"] += 1
                results["actions_executed"] += len(actions)

            except Exception as e:
                error_msg = f"Error processing notification {notification_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        return results

    def test_rule(self, rule_id: int, notification_id: int) -> Dict:
        """
        Test a rule against a specific notification without executing actions.

        Args:
            rule_id: Rule ID to test
            notification_id: Notification ID to test against

        Returns:
            Dict with test results
        """
        rule = self.db.query(NotificationRule).filter_by(id=rule_id, user_id=self.user_id).first()

        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        notification = crud.get_notification(self.db, notification_id, self.user_id)

        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        # Evaluate conditions
        matches = self._evaluate_conditions(notification, rule.conditions)

        # Determine what actions would be executed (without executing)
        actions_to_execute = rule.actions if matches else []

        return {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "notification_id": notification_id,
            "matches": matches,
            "actions_that_would_execute": actions_to_execute,
        }
