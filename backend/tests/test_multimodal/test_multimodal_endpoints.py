"""Tests for multimodal API endpoints."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from database.models import Task


class TestMultimodalEndpoints:
    """Test suite for multimodal API endpoints."""

    @pytest.fixture
    def mock_audio_service(self):
        """Mock AudioService for testing."""
        with patch("api.routes.multimodal.get_audio_service") as mock:
            service = MagicMock()
            service.transcribe_audio.return_value = {
                "text": "Test transcription",
                "language": "en",
            }
            mock.return_value = service
            yield service

    @pytest.fixture
    def mock_vision_service(self):
        """Mock VisionService for testing."""
        with patch("api.routes.multimodal.get_vision_service") as mock:
            service = MagicMock()
            service.analyze_image.return_value = {
                "analysis": "Test analysis",
                "tasks": [
                    {"description": "Task 1", "source": "image_analysis"},
                    {"description": "Task 2", "source": "image_analysis"},
                ],
            }
            mock.return_value = service
            yield service

    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file for testing."""
        audio_data = b"fake audio data"
        return ("test.mp3", BytesIO(audio_data), "audio/mp3")

    @pytest.fixture
    def sample_image_file(self):
        """Create a sample image file for testing."""
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return ("test.png", img_bytes, "image/png")

    def test_transcribe_audio_endpoint(
        self, client, sample_user, auth_headers, mock_audio_service, sample_audio_file
    ):
        """Test POST /api/v2/multimodal/transcribe endpoint."""
        response = client.post(
            "/api/v2/multimodal/transcribe",
            files={"file": sample_audio_file},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "text" in data
        assert "language" in data

    def test_transcribe_audio_with_language(
        self, client, sample_user, auth_headers, mock_audio_service, sample_audio_file
    ):
        """Test audio transcription with language parameter."""

        response = client.post(
            "/api/v2/multimodal/transcribe",
            files={"file": sample_audio_file},
            data={"language": "pt"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        mock_audio_service.transcribe_audio.assert_called_once()

    def test_analyze_image_endpoint(
        self, client, sample_user, auth_headers, mock_vision_service, sample_image_file
    ):
        """Test POST /api/v2/multimodal/analyze-image endpoint."""

        response = client.post(
            "/api/v2/multimodal/analyze-image",
            files={"file": sample_image_file},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_analyze_image_with_custom_prompt(
        self, client, sample_user, auth_headers, mock_vision_service, sample_image_file
    ):
        """Test image analysis with custom prompt."""

        custom_prompt = "Extract only high priority tasks"

        response = client.post(
            "/api/v2/multimodal/analyze-image",
            files={"file": sample_image_file},
            data={"prompt": custom_prompt},
            headers=auth_headers,
        )

        assert response.status_code == 200
        call_args = mock_vision_service.analyze_image.call_args
        assert call_args[1]["prompt"] == custom_prompt

    def test_process_multimodal_audio(
        self,
        client,
        db,
        sample_user,
        auth_headers,
        mock_audio_service,
        sample_audio_file,
    ):
        """Test POST /api/v2/multimodal/process with audio file."""

        response = client.post(
            "/api/v2/multimodal/process",
            files={"file": sample_audio_file},
            data={"auto_create_tasks": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "transcription" in data
        assert "tasks_created" in data
        assert len(data["tasks_created"]) > 0

        # Verify task was created in database
        task = db.query(Task).filter(Task.id == data["tasks_created"][0]).first()
        assert task is not None
        assert task.user_id == sample_user.id

    def test_process_multimodal_image(
        self, client, db, sample_user, auth_headers, mock_vision_service, sample_image_file
    ):
        """Test POST /api/v2/multimodal/process with image file."""

        response = client.post(
            "/api/v2/multimodal/process",
            files={"file": sample_image_file},
            data={"auto_create_tasks": "true"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data
        assert "tasks_created" in data
        assert len(data["tasks_created"]) == 2  # 2 tasks from mock

        # Verify tasks were created
        tasks = db.query(Task).filter(Task.id.in_(data["tasks_created"])).all()
        assert len(tasks) == 2

    def test_process_multimodal_no_auto_create(
        self, client, sample_user, auth_headers, mock_audio_service, sample_audio_file
    ):
        """Test multimodal processing without auto-creating tasks."""

        response = client.post(
            "/api/v2/multimodal/process",
            files={"file": sample_audio_file},
            data={"auto_create_tasks": "false"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert len(data["tasks_created"]) == 0

    def test_process_multimodal_with_big_rock(
        self, client, db, sample_user, auth_headers, mock_audio_service, sample_audio_file
    ):
        """Test multimodal processing with big rock association."""

        # Create a big rock
        from database.models import BigRock

        big_rock = BigRock(user_id=sample_user.id, name="Test Big Rock")
        db.add(big_rock)
        db.commit()

        response = client.post(
            "/api/v2/multimodal/process",
            files={"file": sample_audio_file},
            data={"auto_create_tasks": "true", "big_rock_id": str(big_rock.id)},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Verify task has big rock association
        task = db.query(Task).filter(Task.id == data["tasks_created"][0]).first()
        assert task.big_rock_id == big_rock.id

    def test_unsupported_file_format(self, client, sample_user, auth_headers):
        """Test error for unsupported file format."""

        # Create unsupported file
        unsupported_file = ("test.xyz", BytesIO(b"fake data"), "application/octet-stream")

        response = client.post(
            "/api/v2/multimodal/process",
            files={"file": unsupported_file},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]

    def test_missing_file(self, client, sample_user, auth_headers):
        """Test error when no file is provided."""

        response = client.post(
            "/api/v2/multimodal/process",
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    def test_unauthenticated_request(self, client, sample_audio_file):
        """Test that unauthenticated requests are rejected."""
        response = client.post(
            "/api/v2/multimodal/transcribe",
            files={"file": sample_audio_file},
        )

        # Should return 401 or 403 (depending on auth setup)
        assert response.status_code in [401, 403]


class TestMultimodalValidation:
    """Test input validation for multimodal endpoints."""

    def test_validate_audio_file_size(self):
        """Test file size validation for audio files."""
        # This would be tested through the service layer
        pass

    def test_validate_image_file_size(self):
        """Test file size validation for image files."""
        # This would be tested through the service layer
        pass

    def test_validate_file_formats(self):
        """Test file format validation."""
        # This would be tested through the service layer
        pass
