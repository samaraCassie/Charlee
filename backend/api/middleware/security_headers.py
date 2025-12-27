"""Security headers middleware for HTTP response protection."""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all HTTP responses.

    Implements OWASP recommended security headers to prevent common attacks:
    - XSS (Cross-Site Scripting)
    - Clickjacking
    - MIME sniffing attacks
    - Man-in-the-middle attacks (via HSTS)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response.

        Args:
            request: The incoming request
            call_next: The next middleware/route handler

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # X-Frame-Options: Prevent clickjacking attacks
        # DENY = Page cannot be displayed in a frame
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options: Prevent MIME sniffing
        # nosniff = Browser must not override Content-Type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection: Enable browser XSS filter (legacy, but still good)
        # 1; mode=block = Enable filter and block page if attack detected
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        # strict-origin-when-cross-origin = Send origin only for cross-origin
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        # Disable unnecessary features to reduce attack surface
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        # Content-Security-Policy: Prevent XSS and injection attacks
        # Only load resources from same origin by default
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts for now
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles
            "img-src 'self' data: https:",  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URIs
            "connect-src 'self'",  # API calls only to same origin
            "frame-ancestors 'none'",  # Don't allow embedding (same as X-Frame-Options)
            "base-uri 'self'",  # Restrict <base> tag
            "form-action 'self'",  # Forms can only submit to same origin
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Strict-Transport-Security (HSTS): Force HTTPS
        # max-age=31536000 = 1 year
        # includeSubDomains = Apply to all subdomains
        # preload = Allow inclusion in HSTS preload list
        # Only set in production with HTTPS
        import os
        environment = os.getenv("ENVIRONMENT", "development").lower()
        if environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
