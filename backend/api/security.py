"""Security utilities for input sanitization and validation."""

import re
import html
from typing import Optional


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML input to prevent XSS attacks.

    Args:
        text: Input text that may contain HTML

    Returns:
        Sanitized text with HTML entities escaped

    Examples:
        >>> sanitize_html("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not text:
        return text
    return html.escape(text, quote=True)


def sanitize_sql_like(text: str) -> str:
    """
    Sanitize LIKE clause input to prevent SQL injection.

    Args:
        text: Input text for LIKE clause

    Returns:
        Sanitized text with special characters escaped

    Examples:
        >>> sanitize_sql_like("test%")
        "test\\\\%"
    """
    if not text:
        return text
    # Escape SQL LIKE wildcards
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def sanitize_string(
    text: str,
    max_length: Optional[int] = None,
    allow_newlines: bool = True,
    strip_html: bool = True,
) -> str:
    """
    General purpose string sanitization.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (None for no limit)
        allow_newlines: Whether to allow newline characters
        strip_html: Whether to escape HTML entities

    Returns:
        Sanitized string

    Examples:
        >>> sanitize_string("<b>Test</b>", max_length=10)
        "&lt;b&gt;Test&lt;/b&gt;"
    """
    if not text:
        return text

    # Strip leading/trailing whitespace
    sanitized = text.strip()

    # Remove or replace newlines if not allowed
    if not allow_newlines:
        sanitized = sanitized.replace("\n", " ").replace("\r", " ")
        # Collapse multiple spaces
        sanitized = re.sub(r"\s+", " ", sanitized)

    # Escape HTML if requested
    if strip_html:
        sanitized = sanitize_html(sanitized)

    # Enforce max length
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_color_hex(color: str) -> bool:
    """
    Validate hex color code format.

    Args:
        color: Hex color code (e.g., "#3b82f6")

    Returns:
        True if valid hex color, False otherwise

    Examples:
        >>> validate_color_hex("#3b82f6")
        True
        >>> validate_color_hex("red")
        False
    """
    if not color:
        return False
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, color))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Safe filename without path separators

    Examples:
        >>> sanitize_filename("../../etc/passwd")
        "etcpasswd"
        >>> sanitize_filename("report.pdf")
        "report.pdf"
    """
    if not filename:
        return filename

    # Remove path separators
    sanitized = filename.replace("/", "").replace("\\", "")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>:"|?*]', "", sanitized)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email format (basic validation).

    Args:
        email: Email address to validate

    Returns:
        True if valid format, False otherwise

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email:
        return False

    # Basic email pattern (RFC 5322 simplified)
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_json_input(data: dict, allowed_keys: set[str]) -> dict:
    """
    Sanitize JSON input by filtering allowed keys.

    Args:
        data: Input dictionary
        allowed_keys: Set of allowed keys

    Returns:
        Dictionary with only allowed keys

    Examples:
        >>> sanitize_json_input({"name": "Test", "evil": "payload"}, {"name"})
        {"name": "Test"}
    """
    return {k: v for k, v in data.items() if k in allowed_keys}


class SecurityValidator:
    """Utility class for common security validations."""

    @staticmethod
    def is_safe_redirect_url(url: str, allowed_domains: list[str]) -> bool:
        """
        Validate if redirect URL is safe (prevents open redirect).

        Args:
            url: URL to validate
            allowed_domains: List of allowed domains

        Returns:
            True if URL is safe, False otherwise
        """
        from urllib.parse import urlparse

        if not url:
            return False

        # Relative URLs are safe
        if url.startswith("/") and not url.startswith("//"):
            return True

        # Check domain whitelist for absolute URLs
        parsed = urlparse(url)
        return parsed.netloc in allowed_domains

    @staticmethod
    def detect_sql_injection_patterns(text: str) -> bool:
        """
        Detect common SQL injection patterns (additional safety layer).

        Args:
            text: Input text to check

        Returns:
            True if suspicious patterns detected, False otherwise

        Note:
            This is NOT a replacement for parameterized queries!
            Always use SQLAlchemy's built-in protection.
        """
        if not text:
            return False

        # Common SQL injection patterns
        suspicious_patterns = [
            r"(\bOR\b|\bAND\b)\s+[\d\w]+\s*=\s*[\d\w]+",  # OR 1=1, AND 1=1
            r";\s*DROP\s+TABLE",  # ; DROP TABLE
            r";\s*DELETE\s+FROM",  # ; DELETE FROM
            r"UNION\s+SELECT",  # UNION SELECT
            r"--",  # SQL comments
            r"/\*.*\*/",  # SQL block comments
        ]

        text_upper = text.upper()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True

        return False
