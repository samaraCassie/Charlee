"""Audio transcription service using OpenAI Whisper API."""

import logging
import os
from typing import BinaryIO

from openai import OpenAI

logger = logging.getLogger(__name__)


class AudioService:
    """
    Audio Service - Speech-to-Text using OpenAI Whisper.

    Handles audio transcription for supported formats:
    - mp3, wav, m4a, webm, ogg, flac
    """

    SUPPORTED_FORMATS = {"mp3", "wav", "m4a", "webm", "ogg", "flac"}
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB limit for Whisper API

    def __init__(self):
        """Initialize AudioService with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(
        self, audio_file: BinaryIO, filename: str, language: str | None = None
    ) -> dict[str, str]:
        """
        Transcribe audio file using OpenAI Whisper API.

        Args:
            audio_file: Binary file object containing audio data
            filename: Original filename (used to determine format)
            language: Optional language code (e.g., 'en', 'pt', 'es')

        Returns:
            Dictionary with transcription result:
            {
                "text": "Transcribed text",
                "language": "detected_language"
            }

        Raises:
            ValueError: If file format is not supported or file is too large
            Exception: If transcription fails
        """
        # Validate file format
        file_ext = filename.lower().split(".")[-1]
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {file_ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Check file size
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Reset to beginning

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / 1024 / 1024} MB)"
            )

        try:
            logger.info(
                "Transcribing audio file",
                extra={
                    "file_name": filename,
                    "file_size_mb": file_size / 1024 / 1024,
                    "language": language,
                },
            )

            # Call Whisper API
            kwargs = {"file": (filename, audio_file), "model": "whisper-1"}

            if language:
                kwargs["language"] = language

            transcript = self.client.audio.transcriptions.create(**kwargs)

            logger.info(
                "Audio transcription successful",
                extra={
                    "file_name": filename,
                    "text_length": len(transcript.text),
                    "detected_language": getattr(transcript, "language", "unknown"),
                },
            )

            return {
                "text": transcript.text,
                "language": getattr(transcript, "language", language or "unknown"),
            }

        except Exception as e:
            logger.error(
                "Error transcribing audio",
                extra={"file_name": filename, "error": str(e)},
                exc_info=True,
            )
            raise Exception(f"Failed to transcribe audio: {str(e)}") from e


# Singleton instance
_audio_service: AudioService | None = None


def get_audio_service() -> AudioService:
    """Get or create AudioService singleton instance."""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
