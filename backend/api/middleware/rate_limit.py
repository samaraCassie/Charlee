"""Rate limiting middleware for API protection."""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse

__all__ = ["limiter", "rate_limit_exceeded_handler", "SlowAPIMiddleware", "RateLimitExceeded"]


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: The incoming request
        exc: The RateLimitExceeded exception

    Returns:
        JSONResponse with 429 status code
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
        },
    )


def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key from request.

    Uses IP address as the primary identifier.
    Can be extended to use API keys or user IDs.

    Args:
        request: The incoming request

    Returns:
        Rate limit key string
    """
    # Get client IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return get_remote_address(request)


# Initialize rate limiter
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[
        f"{os.getenv('RATE_LIMIT_PER_MINUTE', '60')}/minute",
        "1000/hour",
        "10000/day",
    ],
    enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
    headers_enabled=True,  # Include rate limit headers in response
    swallow_errors=True,  # Don't crash if Redis is down
)
