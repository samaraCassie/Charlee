"""Image analysis service using OpenAI GPT-4o Vision API."""

import base64
import logging
import os
from io import BytesIO
from typing import BinaryIO

from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)


class VisionService:
    """
    Vision Service - Image analysis using GPT-4o Vision.

    Handles image analysis for task extraction and information gathering.
    Supported formats: png, jpg, jpeg, heic, webp
    """

    SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "heic", "webp"}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB limit
    MAX_IMAGE_DIMENSION = 4096  # Max width/height

    DEFAULT_PROMPT = """
    Analyze this image and extract any tasks, to-dos, or important information.

    For each task or item found, provide:
    - Description (clear and actionable)
    - Priority (high/medium/low) if indicated
    - Deadline or time reference if mentioned
    - Category or context if clear

    Format your response as a structured list of tasks.
    If no tasks are found, describe what you see in the image.
    """

    def __init__(self):
        """Initialize VisionService with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)

    def _encode_image(self, image_file: BinaryIO, filename: str) -> str:
        """
        Encode image to base64 for API submission.

        Args:
            image_file: Binary file object containing image data
            filename: Original filename

        Returns:
            Base64 encoded image string

        Raises:
            ValueError: If image format is invalid or size exceeds limits
        """
        # Validate format
        file_ext = filename.lower().split(".")[-1]
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {file_ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Check file size
        image_file.seek(0, 2)
        file_size = image_file.tell()
        image_file.seek(0)

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / 1024 / 1024} MB)"
            )

        # Open and validate image
        try:
            img = Image.open(image_file)
            width, height = img.size

            # Resize if too large
            if width > self.MAX_IMAGE_DIMENSION or height > self.MAX_IMAGE_DIMENSION:
                logger.info(
                    "Resizing image",
                    extra={
                        "original_size": f"{width}x{height}",
                        "max_dimension": self.MAX_IMAGE_DIMENSION,
                    },
                )

                img.thumbnail((self.MAX_IMAGE_DIMENSION, self.MAX_IMAGE_DIMENSION))

            # Convert to bytes
            buffer = BytesIO()
            img_format = img.format or "PNG"
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # Encode to base64
            return base64.b64encode(buffer.read()).decode("utf-8")

        except Exception as e:
            logger.error("Error processing image", extra={"filename": filename, "error": str(e)})
            raise ValueError(f"Invalid image file: {str(e)}") from e

    def analyze_image(
        self, image_file: BinaryIO, filename: str, prompt: str | None = None
    ) -> dict[str, str | list]:
        """
        Analyze image using GPT-4o Vision API.

        Args:
            image_file: Binary file object containing image data
            filename: Original filename (used to determine format)
            prompt: Custom analysis prompt (uses default if not provided)

        Returns:
            Dictionary with analysis result:
            {
                "analysis": "AI-generated analysis text",
                "tasks": [...] # Extracted tasks if applicable
            }

        Raises:
            ValueError: If file format is not supported or file is invalid
            Exception: If analysis fails
        """
        try:
            logger.info("Analyzing image", extra={"filename": filename, "has_custom_prompt": bool(prompt)})

            # Encode image
            base64_image = self._encode_image(image_file, filename)

            # Use custom prompt or default
            analysis_prompt = prompt or self.DEFAULT_PROMPT

            # Call GPT-4o Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=1000,
            )

            analysis_text = response.choices[0].message.content

            logger.info(
                "Image analysis successful",
                extra={
                    "filename": filename,
                    "response_length": len(analysis_text) if analysis_text else 0,
                },
            )

            # Parse response for tasks (simple extraction)
            tasks = self._extract_tasks_from_analysis(analysis_text or "")

            return {"analysis": analysis_text or "", "tasks": tasks}

        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Error analyzing image",
                extra={"filename": filename, "error": str(e)},
                exc_info=True,
            )
            raise Exception(f"Failed to analyze image: {str(e)}") from e

    def _extract_tasks_from_analysis(self, analysis_text: str) -> list[dict[str, str]]:
        """
        Extract structured tasks from analysis text.

        This is a simple extraction - looks for bullet points and numbered lists.
        Can be enhanced with more sophisticated parsing.

        Args:
            analysis_text: AI-generated analysis

        Returns:
            List of task dictionaries
        """
        tasks = []
        lines = analysis_text.split("\n")

        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered items
            if line.startswith(("- ", "* ", "• ")) or (
                len(line) > 2 and line[0].isdigit() and line[1:3] in (". ", ") ")
            ):
                # Remove bullet/number prefix
                task_text = line.lstrip("0123456789.-*•) ").strip()

                if task_text and len(task_text) > 5:  # Min length check
                    tasks.append({"description": task_text, "source": "image_analysis"})

        return tasks


# Singleton instance
_vision_service: VisionService | None = None


def get_vision_service() -> VisionService:
    """Get or create VisionService singleton instance."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
