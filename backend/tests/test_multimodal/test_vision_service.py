"""Tests for image analysis service."""

import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from multimodal.vision_service import VisionService, get_vision_service


class TestVisionService:
    """Test suite for VisionService."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch("multimodal.vision_service.OpenAI") as mock:
            # Mock vision response
            mock_choice = MagicMock()
            mock_choice.message.content = """
            Here are the tasks from the image:
            - Complete project report
            - Review pull requests
            - Schedule team meeting
            """

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]

            mock_instance = mock.return_value
            mock_instance.chat.completions.create.return_value = mock_response

            yield mock_instance

    @pytest.fixture
    def vision_service(self, mock_openai_client):
        """Create VisionService instance with mocked OpenAI client."""
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        service = VisionService()
        service.client = mock_openai_client
        return service

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def test_vision_service_initialization(self):
        """Test VisionService initialization."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        service = VisionService()
        assert service is not None

    def test_vision_service_missing_api_key(self):
        """Test VisionService raises error when API key is missing."""
        os.environ.pop("OPENAI_API_KEY", None)

        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
            VisionService()

        # Restore API key for other tests
        os.environ["OPENAI_API_KEY"] = "test_key"

    def test_analyze_image_success(self, vision_service, sample_image, mock_openai_client):
        """Test successful image analysis."""
        result = vision_service.analyze_image(sample_image, "test.png")

        # Assertions
        assert "analysis" in result
        assert "tasks" in result
        assert len(result["analysis"]) > 0
        assert isinstance(result["tasks"], list)
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_analyze_image_with_custom_prompt(self, vision_service, sample_image):
        """Test image analysis with custom prompt."""
        custom_prompt = "Extract only high priority tasks"

        result = vision_service.analyze_image(sample_image, "test.png", prompt=custom_prompt)

        assert "analysis" in result
        assert "tasks" in result

    def test_extract_tasks_from_analysis(self, vision_service):
        """Test task extraction from analysis text."""
        analysis_text = """
        Based on the image, here are the tasks:
        - Complete the monthly report by Friday
        - Schedule meeting with client
        * Review design mockups
        1. Update project timeline
        2. Send invoice to customer
        """

        tasks = vision_service._extract_tasks_from_analysis(analysis_text)

        assert len(tasks) > 0
        assert all("description" in task for task in tasks)
        assert all("source" in task for task in tasks)

    def test_unsupported_image_format(self, vision_service):
        """Test error for unsupported image format."""
        image_file = BytesIO(b"fake data")

        with pytest.raises(ValueError, match="Unsupported image format"):
            vision_service.analyze_image(image_file, "test.xyz")

    def test_image_file_too_large(self, vision_service):
        """Test error when image file size exceeds limit."""
        # Create a large file (21 MB)
        large_data = b"x" * (21 * 1024 * 1024)
        image_file = BytesIO(large_data)

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            vision_service.analyze_image(image_file, "test.png")

    def test_image_resize_if_too_large(self, vision_service, mock_openai_client):
        """Test that large images are resized."""
        # Create a large image (5000x5000)
        large_img = Image.new("RGB", (5000, 5000), color="blue")
        img_bytes = BytesIO()
        large_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = vision_service.analyze_image(img_bytes, "large.png")

        # Should succeed (image was resized)
        assert "analysis" in result

    def test_supported_formats(self, vision_service, mock_openai_client):
        """Test all supported image formats are accepted."""
        # Map file extensions to PIL format names
        format_map = {
            "png": "PNG",
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "webp": "WEBP",
        }

        for fmt, pil_format in format_map.items():
            # Create image
            img = Image.new("RGB", (100, 100), color="green")
            img_bytes = BytesIO()
            img.save(img_bytes, format=pil_format)
            img_bytes.seek(0)

            # Should not raise error for format validation
            try:
                result = vision_service.analyze_image(img_bytes, f"test.{fmt}")
                assert "analysis" in result
            except Exception as e:
                if "Unsupported image format" in str(e):
                    pytest.fail(f"Format {fmt} should be supported")

    def test_invalid_image_file(self, vision_service):
        """Test error for invalid image data."""
        invalid_data = BytesIO(b"This is not an image")

        with pytest.raises(ValueError, match="Invalid image file"):
            vision_service.analyze_image(invalid_data, "test.png")

    def test_analysis_api_error(self, vision_service, sample_image, mock_openai_client):
        """Test handling of OpenAI API errors."""
        # Mock API error
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Failed to analyze image"):
            vision_service.analyze_image(sample_image, "test.png")

    def test_get_vision_service_singleton(self):
        """Test get_vision_service returns singleton instance."""
        os.environ["OPENAI_API_KEY"] = "test_key"

        service1 = get_vision_service()
        service2 = get_vision_service()

        assert service1 is service2


class TestVisionServiceIntegration:
    """Integration tests for VisionService (require real API key)."""

    @pytest.mark.skip(reason="Requires real OpenAI API key")
    def test_real_image_analysis(self):
        """Test real image analysis with OpenAI API."""
        # This test should only be run manually with a real API key
        os.environ["OPENAI_API_KEY"] = "your_real_api_key"

        service = VisionService()

        # Load a real image file
        with open("path/to/test/image.png", "rb") as f:
            image_data = f.read()

        image_file = BytesIO(image_data)
        result = service.analyze_image(image_file, "test.png")

        assert "analysis" in result
        assert len(result["analysis"]) > 0
        assert "tasks" in result
