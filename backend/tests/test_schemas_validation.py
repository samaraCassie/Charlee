"""Tests for schema validation and sanitization."""

import pytest
from pydantic import ValidationError
from database.schemas import BigRockCreate, BigRockUpdate, TaskCreate, TaskUpdate


class TestBigRockSchemaValidation:
    """Test BigRock schema validation."""

    def test_create_big_rock_valid(self):
        """Should accept valid Big Rock data."""
        big_rock = BigRockCreate(name="Health & Wellness", color="#22c55e", active=True)
        assert big_rock.name == "Health &amp; Wellness"  # HTML escaped
        assert big_rock.color == "#22c55e"
        assert big_rock.active is True

    def test_create_big_rock_sanitizes_xss(self):
        """Should sanitize XSS attempts in name."""
        big_rock = BigRockCreate(name="<script>alert('xss')</script>Career", color="#3b82f6")
        # Should escape HTML entities
        assert "&lt;script&gt;" in big_rock.name
        assert "<script>" not in big_rock.name

    def test_create_big_rock_invalid_color(self):
        """Should reject invalid hex colors."""
        with pytest.raises(ValidationError) as exc_info:
            BigRockCreate(name="Test", color="red")  # Not a hex color
        assert "Invalid hex color format" in str(exc_info.value)

    def test_create_big_rock_valid_short_hex(self):
        """Should accept 3-character hex colors."""
        big_rock = BigRockCreate(name="Test", color="#fff")
        assert big_rock.color == "#fff"

    def test_create_big_rock_empty_name(self):
        """Should reject empty names."""
        with pytest.raises(ValidationError) as exc_info:
            BigRockCreate(name="", color="#000000")
        # Either Pydantic's min_length or our validator catches it
        assert exc_info.value is not None

    def test_create_big_rock_whitespace_only_name(self):
        """Should reject whitespace-only names."""
        with pytest.raises(ValidationError) as exc_info:
            BigRockCreate(name="   ", color="#000000")
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_update_big_rock_partial(self):
        """Should allow partial updates."""
        update = BigRockUpdate(name="New Name")
        assert update.name is not None
        assert update.color is None
        assert update.active is None


class TestTaskSchemaValidation:
    """Test Task schema validation."""

    def test_create_task_valid(self):
        """Should accept valid task data."""
        task = TaskCreate(description="Complete project documentation", type="task", big_rock_id=1)
        assert "Complete project documentation" in task.description
        assert task.type == "task"
        assert task.big_rock_id == 1

    def test_create_task_sanitizes_description(self):
        """Should sanitize XSS in description."""
        task = TaskCreate(description='<img src=x onerror="alert(1)">Task', type="task")
        # Should escape HTML
        assert "&lt;img" in task.description or "onerror" not in task.description

    def test_create_task_preserves_newlines(self):
        """Should preserve newlines in description."""
        task = TaskCreate(description="Line 1\nLine 2\nLine 3", type="task")
        # Newlines should be preserved (allow_newlines=True)
        # But HTML should be escaped
        assert "Line 1" in task.description
        assert "Line 2" in task.description

    def test_create_task_invalid_big_rock_id(self):
        """Should reject negative big_rock_id."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(description="Test task", type="task", big_rock_id=-1)
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_zero_big_rock_id(self):
        """Should reject zero big_rock_id."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(description="Test task", type="task", big_rock_id=0)
        assert "positive integer" in str(exc_info.value).lower()

    def test_create_task_valid_types(self):
        """Should accept all valid task types."""
        for task_type in ["fixed_appointment", "task", "continuous"]:
            task = TaskCreate(description=f"Test {task_type}", type=task_type)
            assert task.type == task_type

    def test_create_task_invalid_type(self):
        """Should reject invalid task types."""
        with pytest.raises(ValidationError):
            TaskCreate(description="Test", type="invalid_type")

    def test_create_task_long_description(self):
        """Should truncate very long descriptions."""
        long_desc = "a" * 6000
        task = TaskCreate(description=long_desc, type="task")
        # Should be truncated to max_length (5000)
        assert len(task.description) <= 5000

    def test_update_task_partial(self):
        """Should allow partial task updates."""
        update = TaskUpdate(status="in_progress")
        assert update.status == "in_progress"
        assert update.description is None
        assert update.type is None

    def test_update_task_valid_statuses(self):
        """Should accept all valid statuses."""
        for status in ["pending", "in_progress", "completed", "cancelled"]:
            update = TaskUpdate(status=status)
            assert update.status == status

    def test_update_task_invalid_status(self):
        """Should reject invalid statuses."""
        with pytest.raises(ValidationError):
            TaskUpdate(status="invalid_status")
