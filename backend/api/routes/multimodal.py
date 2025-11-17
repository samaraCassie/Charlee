"""Multimodal API routes for audio and image processing."""

import logging
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_user
from database.config import get_db
from database.models import Task, User
from multimodal.audio_service import get_audio_service
from multimodal.vision_service import get_vision_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Response Models ====================


class TranscriptionResponse(BaseModel):
    """Response model for audio transcription."""

    text: str
    language: str
    success: bool = True


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis."""

    analysis: str
    tasks: list[dict[str, str]]
    success: bool = True


class MultimodalProcessResponse(BaseModel):
    """Response model for unified multimodal processing."""

    success: bool
    message: str
    transcription: str | None = None
    analysis: str | None = None
    tasks_created: list[int] = []  # List of created task IDs


# ==================== Audio Endpoints ====================


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio to text",
    description="Upload audio file and receive text transcription using OpenAI Whisper",
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (mp3, wav, m4a, webm, ogg, flac)"),
    language: str | None = Form(None, description="Optional language code (e.g., 'en', 'pt')"),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe audio file to text using OpenAI Whisper API.

    Supported formats: mp3, wav, m4a, webm, ogg, flac
    Max file size: 25 MB

    Args:
        file: Audio file upload
        language: Optional language code for better accuracy
        current_user: Authenticated user

    Returns:
        Transcription result with text and detected language
    """
    try:
        logger.info(
            "Audio transcription requested",
            extra={
                "user_id": current_user.id,
                "file_name": file.filename,
                "content_type": file.content_type,
            },
        )

        # Read file content
        content = await file.read()
        audio_file = BytesIO(content)

        # Get audio service and transcribe
        audio_service = get_audio_service()
        result = audio_service.transcribe_audio(
            audio_file=audio_file, filename=file.filename or "audio.mp3", language=language
        )

        return TranscriptionResponse(text=result["text"], language=result["language"])

    except ValueError as e:
        logger.warning(
            "Invalid audio file",
            extra={"user_id": current_user.id, "error": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(
            "Error transcribing audio",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio. Please try again.",
        )


# ==================== Vision Endpoints ====================


@router.post(
    "/analyze-image",
    response_model=ImageAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze image for tasks and information",
    description="Upload image and receive AI analysis with extracted tasks",
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (png, jpg, jpeg, heic, webp)"),
    prompt: str | None = Form(
        None, description="Custom analysis prompt (uses default task extraction if not provided)"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze image using GPT-4o Vision API.

    Use cases:
    - Extract tasks from handwritten planner
    - Analyze screenshot of email and create tasks
    - Read scribbled notes and add to inbox

    Supported formats: png, jpg, jpeg, heic, webp
    Max file size: 20 MB

    Args:
        file: Image file upload
        prompt: Optional custom analysis prompt
        current_user: Authenticated user

    Returns:
        Analysis result with extracted tasks
    """
    try:
        logger.info(
            "Image analysis requested",
            extra={
                "user_id": current_user.id,
                "file_name": file.filename,
                "content_type": file.content_type,
                "has_custom_prompt": bool(prompt),
            },
        )

        # Read file content
        content = await file.read()
        image_file = BytesIO(content)

        # Get vision service and analyze
        vision_service = get_vision_service()
        result = vision_service.analyze_image(
            image_file=image_file, filename=file.filename or "image.png", prompt=prompt
        )

        return ImageAnalysisResponse(analysis=result["analysis"], tasks=result["tasks"])

    except ValueError as e:
        logger.warning(
            "Invalid image file",
            extra={"user_id": current_user.id, "error": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(
            "Error analyzing image",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze image. Please try again.",
        )


# ==================== Unified Processing Endpoint ====================


@router.post(
    "/process",
    response_model=MultimodalProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process multimodal input and create tasks",
    description="Upload audio or image, process it, and automatically create tasks in inbox",
)
async def process_multimodal(
    file: UploadFile = File(..., description="Audio or image file"),
    auto_create_tasks: bool = Form(
        True, description="Automatically create tasks from extracted content"
    ),
    big_rock_id: int | None = Form(None, description="Optional Big Rock ID for created tasks"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unified endpoint for processing audio or image files.

    Automatically detects file type, processes it, and optionally creates tasks
    in the user's inbox.

    Workflow:
    1. Detect file type (audio or image)
    2. Process with appropriate service (Whisper or Vision)
    3. Extract tasks from content
    4. Create tasks in database if auto_create_tasks=True
    5. Return processing result with created task IDs

    Args:
        file: Audio or image file
        auto_create_tasks: Whether to automatically create tasks
        big_rock_id: Optional Big Rock ID to associate tasks with
        current_user: Authenticated user
        db: Database session

    Returns:
        Processing result with created task IDs
    """
    try:
        logger.info(
            "Multimodal processing requested",
            extra={
                "user_id": current_user.id,
                "file_name": file.filename,
                "content_type": file.content_type,
                "auto_create": auto_create_tasks,
            },
        )

        # Read file content
        content = await file.read()
        file_buffer = BytesIO(content)

        # Determine file type
        filename = file.filename or "file"
        file_ext = filename.lower().split(".")[-1]

        transcription = None
        analysis = None
        tasks_to_create = []

        # Process based on file type
        audio_formats = {"mp3", "wav", "m4a", "webm", "ogg", "flac"}
        image_formats = {"png", "jpg", "jpeg", "heic", "webp"}

        if file_ext in audio_formats:
            # Process as audio
            audio_service = get_audio_service()
            result = audio_service.transcribe_audio(audio_file=file_buffer, filename=filename)
            transcription = result["text"]

            # Create single task from transcription
            if transcription.strip():
                tasks_to_create.append({"description": transcription, "source": "audio"})

        elif file_ext in image_formats:
            # Process as image
            vision_service = get_vision_service()
            result = vision_service.analyze_image(image_file=file_buffer, filename=filename)
            analysis = result["analysis"]
            tasks_to_create = result["tasks"]

        else:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(sorted(audio_formats | image_formats))}"
            )

        # Create tasks if requested
        created_task_ids = []
        if auto_create_tasks and tasks_to_create:
            for task_data in tasks_to_create:
                task = Task(
                    user_id=current_user.id,
                    description=task_data["description"],
                    type="task",
                    status="pending",
                    big_rock_id=big_rock_id,
                )
                db.add(task)
                db.flush()  # Get ID without committing
                created_task_ids.append(task.id)

            db.commit()

            logger.info(
                "Tasks created from multimodal input",
                extra={
                    "user_id": current_user.id,
                    "task_count": len(created_task_ids),
                    "source": "audio" if transcription else "image",
                },
            )

        return MultimodalProcessResponse(
            success=True,
            message=f"Processed successfully. {'Created ' + str(len(created_task_ids)) + ' task(s).' if created_task_ids else 'No tasks created.'}",
            transcription=transcription,
            analysis=analysis,
            tasks_created=created_task_ids,
        )

    except ValueError as e:
        logger.warning(
            "Invalid multimodal file",
            extra={"user_id": current_user.id, "error": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(
            "Error processing multimodal input",
            extra={"user_id": current_user.id, "error": str(e)},
            exc_info=True,
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process file. Please try again.",
        )
