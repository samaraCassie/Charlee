"""Global error handler middleware."""

import os
import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from api.middleware.logging_config import get_logger

logger = get_logger(__name__)


class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle all uncaught exceptions globally."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and catch any unhandled exceptions.

        Args:
            request: The incoming request
            call_next: The next middleware/route handler

        Returns:
            Response or error response
        """
        try:
            return await call_next(request)

        except ValidationError as exc:
            # Pydantic validation errors
            logger.warning(
                "Validation error",
                extra={
                    "path": request.url.path,
                    "error": str(exc),
                    "errors": exc.errors(),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                content={
                    "error": "Validation Error",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                },
            )

        except IntegrityError as exc:
            # Database constraint violations
            logger.error(
                "Database integrity error",
                extra={
                    "path": request.url.path,
                    "error": str(exc.orig) if hasattr(exc, "orig") else str(exc),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "Conflict",
                    "message": "Database constraint violation. The operation conflicts with existing data.",
                },
            )

        except SQLAlchemyError as exc:
            # Other database errors
            logger.error(
                "Database error",
                extra={
                    "path": request.url.path,
                    "error": str(exc),
                },
                exc_info=True,
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "Database Error",
                    "message": "A database error occurred. Please try again later.",
                },
            )

        except ValueError as exc:
            # Business logic errors (e.g., invalid big_rock_id)
            logger.warning(
                "Value error",
                extra={
                    "path": request.url.path,
                    "error": str(exc),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Bad Request",
                    "message": str(exc),
                },
            )

        except PermissionError as exc:
            # Permission/authorization errors
            logger.warning(
                "Permission denied",
                extra={
                    "path": request.url.path,
                    "error": str(exc),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Forbidden",
                    "message": "You don't have permission to access this resource.",
                },
            )

        except Exception as exc:
            # Catch-all for unexpected errors
            logger.error(
                "Unexpected error",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc() if self._should_log_traceback() else None,
                },
                exc_info=True,
            )

            # Return generic error in production, detailed in development
            if self._should_show_details():
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": "Internal Server Error",
                        "message": str(exc),
                        "type": type(exc).__name__,
                        "traceback": traceback.format_exc().split("\n"),
                    },
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred. Please try again later.",
                    },
                )

    @staticmethod
    def _should_show_details() -> bool:
        """Check if we should show detailed error messages."""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        debug = os.getenv("DEBUG", "false").lower() == "true"
        return environment == "development" or debug

    @staticmethod
    def _should_log_traceback() -> bool:
        """Check if we should log full tracebacks."""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        return log_level == "DEBUG"
