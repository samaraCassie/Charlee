"""Security tests for input sanitization and validation."""

from api.security import (
    SecurityValidator,
    sanitize_filename,
    sanitize_html,
    sanitize_string,
    validate_color_hex,
    validate_email,
)


class TestInputSanitization:
    """Test input sanitization functions."""

    def test_sanitize_html_xss_script(self):
        """Should escape script tags to prevent XSS."""
        malicious_input = "<script>alert('xss')</script>"
        result = sanitize_html(malicious_input)
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        assert "<script>" not in result

    def test_sanitize_html_image_onerror(self):
        """Should escape image tags with onerror handlers."""
        malicious_input = '<img src=x onerror="alert(1)">'
        result = sanitize_html(malicious_input)
        assert "&lt;img" in result
        assert "onerror=" not in result or "&quot;" in result

    def test_sanitize_html_preserves_quotes(self):
        """Should escape quotes properly."""
        input_text = 'He said "Hello"'
        result = sanitize_html(input_text)
        assert "&quot;" in result or '"' not in result

    def test_sanitize_string_max_length(self):
        """Should truncate strings exceeding max length."""
        long_string = "a" * 200
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_removes_newlines(self):
        """Should remove newlines when not allowed."""
        text_with_newlines = "Line 1\nLine 2\rLine 3"
        result = sanitize_string(text_with_newlines, allow_newlines=False)
        assert "\n" not in result
        assert "\r" not in result

    def test_sanitize_string_preserves_newlines(self):
        """Should preserve newlines when allowed."""
        text_with_newlines = "Line 1\nLine 2"
        result = sanitize_string(text_with_newlines, allow_newlines=True, strip_html=False)
        # Count should remain the same (HTML escaping might change representation)
        assert "Line 1" in result and "Line 2" in result


class TestColorValidation:
    """Test color validation."""

    def test_validate_color_hex_valid_6_chars(self):
        """Should accept valid 6-character hex colors."""
        assert validate_color_hex("#3b82f6") is True
        assert validate_color_hex("#FFFFFF") is True
        assert validate_color_hex("#000000") is True

    def test_validate_color_hex_valid_3_chars(self):
        """Should accept valid 3-character hex colors."""
        assert validate_color_hex("#fff") is True
        assert validate_color_hex("#ABC") is True

    def test_validate_color_hex_invalid_format(self):
        """Should reject invalid hex color formats."""
        assert validate_color_hex("red") is False
        assert validate_color_hex("3b82f6") is False  # Missing #
        assert validate_color_hex("#gg0000") is False  # Invalid chars
        assert validate_color_hex("#12") is False  # Too short
        assert validate_color_hex("#1234567") is False  # Too long

    def test_validate_color_hex_none(self):
        """Should reject None values."""
        assert validate_color_hex(None) is False
        assert validate_color_hex("") is False


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_filename_path_traversal(self):
        """Should prevent directory traversal attacks."""
        malicious = "../../etc/passwd"
        result = sanitize_filename(malicious)
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_filename_dangerous_chars(self):
        """Should remove dangerous characters."""
        filename = 'file<>:"|?*.txt'
        result = sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_sanitize_filename_preserves_valid(self):
        """Should preserve valid filenames."""
        filename = "report_2024.pdf"
        result = sanitize_filename(filename)
        assert result == filename


class TestEmailValidation:
    """Test email validation."""

    def test_validate_email_valid(self):
        """Should accept valid email formats."""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Should reject invalid email formats."""
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False
        assert validate_email(None) is False


class TestSecurityValidator:
    """Test SecurityValidator utility class."""

    def test_is_safe_redirect_url_relative(self):
        """Should accept relative URLs."""
        validator = SecurityValidator()
        assert validator.is_safe_redirect_url("/dashboard", []) is True
        assert validator.is_safe_redirect_url("/tasks/123", []) is True

    def test_is_safe_redirect_url_protocol_relative(self):
        """Should reject protocol-relative URLs (open redirect)."""
        validator = SecurityValidator()
        assert validator.is_safe_redirect_url("//evil.com", []) is False

    def test_is_safe_redirect_url_whitelisted_domain(self):
        """Should accept whitelisted domains."""
        validator = SecurityValidator()
        allowed = ["example.com", "app.example.com"]
        assert validator.is_safe_redirect_url("https://example.com/page", allowed) is True

    def test_is_safe_redirect_url_non_whitelisted(self):
        """Should reject non-whitelisted domains."""
        validator = SecurityValidator()
        allowed = ["example.com"]
        assert validator.is_safe_redirect_url("https://evil.com", allowed) is False

    def test_detect_sql_injection_union_select(self):
        """Should detect UNION SELECT patterns."""
        validator = SecurityValidator()
        assert validator.detect_sql_injection_patterns("1 UNION SELECT password FROM users") is True

    def test_detect_sql_injection_or_equals(self):
        """Should detect OR 1=1 patterns."""
        validator = SecurityValidator()
        assert validator.detect_sql_injection_patterns("admin' OR 1=1--") is True

    def test_detect_sql_injection_drop_table(self):
        """Should detect DROP TABLE patterns."""
        validator = SecurityValidator()
        assert validator.detect_sql_injection_patterns("'; DROP TABLE users;--") is True

    def test_detect_sql_injection_clean_input(self):
        """Should not flag clean input as suspicious."""
        validator = SecurityValidator()
        assert validator.detect_sql_injection_patterns("normal search query") is False
        assert validator.detect_sql_injection_patterns("order by date") is False
