"""Tests for audio transcription service."""

import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from multimodal.audio_service import AudioService, get_audio_service


class TestAudioService:
    """Test suite for AudioService."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch("multimodal.audio_service.OpenAI") as mock:
            # Mock transcription response
            mock_response = MagicMock()
            mock_response.text = "This is a test transcription"
            mock_response.language = "en"

            mock_instance = mock.return_value
            mock_instance.audio.transcriptions.create.return_value = mock_response

            yield mock_instance

    @pytest.fixture
    def audio_service(self, mock_openai_client):
        """Create AudioService instance with mocked OpenAI client."""
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        service = AudioService()
        service.client = mock_openai_client
        return service

    def test_audio_service_initialization(self):
        """Test AudioService initialization."""
        os.environ["OPENAI_API_KEY"] = "test_key"
        service = AudioService()
        assert service is not None

    def test_audio_service_missing_api_key(self):
        """Test AudioService raises error when API key is missing."""
        os.environ.pop("OPENAI_API_KEY", None)

        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
            AudioService()

        # Restore API key for other tests
        os.environ["OPENAI_API_KEY"] = "test_key"

    def test_transcribe_audio_success(self, audio_service, mock_openai_client):
        """Test successful audio transcription."""
        # Create mock audio file
        audio_data = b"fake audio data"
        audio_file = BytesIO(audio_data)

        # Transcribe
        result = audio_service.transcribe_audio(audio_file, "test.mp3")

        # Assertions
        assert result["text"] == "This is a test transcription"
        assert result["language"] == "en"
        mock_openai_client.audio.transcriptions.create.assert_called_once()

    def test_transcribe_audio_with_language(self, audio_service, mock_openai_client):
        """Test audio transcription with language specified."""
        audio_file = BytesIO(b"fake audio data")

        audio_service.transcribe_audio(audio_file, "test.mp3", language="pt")

        # Verify language was passed to API
        call_args = mock_openai_client.audio.transcriptions.create.call_args
        assert "language" in call_args[1]
        assert call_args[1]["language"] == "pt"

    def test_unsupported_audio_format(self, audio_service):
        """Test error for unsupported audio format."""
        audio_file = BytesIO(b"fake data")

        with pytest.raises(ValueError, match="Unsupported audio format"):
            audio_service.transcribe_audio(audio_file, "test.xyz")

    def test_file_too_large(self, audio_service):
        """Test error when file size exceeds limit."""
        # Create a large file (26 MB)
        large_data = b"x" * (26 * 1024 * 1024)
        audio_file = BytesIO(large_data)

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            audio_service.transcribe_audio(audio_file, "test.mp3")

    def test_supported_formats(self, audio_service):
        """Test all supported audio formats are accepted."""
        supported_formats = ["mp3", "wav", "m4a", "webm", "ogg", "flac"]

        for fmt in supported_formats:
            audio_file = BytesIO(b"fake data")
            # Should not raise error for format validation
            try:
                audio_service.transcribe_audio(audio_file, f"test.{fmt}")
            except Exception as e:
                # Only format errors should fail here
                if "Unsupported audio format" in str(e):
                    pytest.fail(f"Format {fmt} should be supported")

    def test_transcription_api_error(self, audio_service, mock_openai_client):
        """Test handling of OpenAI API errors."""
        # Mock API error
        mock_openai_client.audio.transcriptions.create.side_effect = Exception("API Error")

        audio_file = BytesIO(b"fake data")

        with pytest.raises(Exception, match="Failed to transcribe audio"):
            audio_service.transcribe_audio(audio_file, "test.mp3")

    def test_get_audio_service_singleton(self):
        """Test get_audio_service returns singleton instance."""
        os.environ["OPENAI_API_KEY"] = "test_key"

        service1 = get_audio_service()
        service2 = get_audio_service()

        assert service1 is service2


class TestAudioServiceIntegration:
    """Integration tests for AudioService (require real API key)."""

    @pytest.mark.skip(reason="Requires real OpenAI API key")
    def test_real_transcription(self):
        """Test real transcription with OpenAI API."""
        # This test should only be run manually with a real API key
        os.environ["OPENAI_API_KEY"] = "your_real_api_key"

        service = AudioService()

        # Load a real audio file
        with open("path/to/test/audio.mp3", "rb") as f:
            audio_data = f.read()

        audio_file = BytesIO(audio_data)
        result = service.transcribe_audio(audio_file, "test.mp3")

        assert "text" in result
        assert len(result["text"]) > 0
