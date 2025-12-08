"""
Input Sanitization - Secure input handling.

Provides:
- HTML sanitization
- SQL injection prevention
- Command injection prevention
- Path traversal prevention
- Special character escaping
"""

import html
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class SanitizationConfig:
    """Configuration for input sanitization."""
    max_length: int = 10000
    allow_unicode: bool = True
    strip_whitespace: bool = True
    normalize_unicode: bool = True
    allowed_html_tags: Set[str] = None
    allowed_html_attrs: Set[str] = None


class InputSanitizer:
    """
    Input sanitization for security.

    Usage:
        sanitizer = InputSanitizer()

        # Basic sanitization
        safe_input = sanitizer.sanitize(user_input)

        # HTML sanitization
        safe_html = sanitizer.sanitize_html(html_content)

        # SQL-safe string
        safe_sql = sanitizer.sanitize_for_sql(value)

        # Path sanitization
        safe_path = sanitizer.sanitize_path(path)
    """

    def __init__(self, config: SanitizationConfig = None):
        self.config = config or SanitizationConfig()

        # Default allowed HTML tags and attributes
        self._allowed_tags = self.config.allowed_html_tags or {
            'p', 'br', 'b', 'i', 'u', 'strong', 'em', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
        }
        self._allowed_attrs = self.config.allowed_html_attrs or {
            'class', 'id'
        }

        # Dangerous patterns
        self._sql_patterns = [
            r"('|\")\s*;\s*",  # String termination with semicolon
            r"--",  # SQL comment
            r"/\*.*?\*/",  # Block comment
            r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b",
            r"\b(OR|AND)\s+\d+\s*=\s*\d+",  # Tautology
            r"xp_\w+",  # Extended stored procedures
        ]

        self._command_patterns = [
            r"[;&|`$]",  # Shell metacharacters
            r"\$\(.*\)",  # Command substitution
            r"`.*`",  # Backtick substitution
            r"\|\|",  # OR operator
            r"&&",  # AND operator
            r">\s*/",  # Redirect to root
            r"\.\./",  # Directory traversal
        ]

        self._xss_patterns = [
            r"<script[^>]*>",  # Script tags
            r"javascript:",  # JavaScript protocol
            r"vbscript:",  # VBScript protocol
            r"on\w+\s*=",  # Event handlers
            r"expression\s*\(",  # CSS expression
            r"url\s*\(",  # CSS url
        ]

    def sanitize(
        self,
        value: str,
        max_length: int = None
    ) -> str:
        """
        General-purpose sanitization.

        Args:
            value: Input to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)

        # Strip whitespace
        if self.config.strip_whitespace:
            value = value.strip()

        # Normalize unicode
        if self.config.normalize_unicode:
            value = unicodedata.normalize('NFKC', value)

        # Remove null bytes
        value = value.replace('\x00', '')

        # Enforce max length
        max_len = max_length or self.config.max_length
        if len(value) > max_len:
            value = value[:max_len]

        return value

    def sanitize_html(
        self,
        html_content: str,
        allowed_tags: Set[str] = None,
        allowed_attrs: Set[str] = None
    ) -> str:
        """
        Sanitize HTML content.

        Args:
            html_content: HTML to sanitize
            allowed_tags: Tags to allow (override defaults)
            allowed_attrs: Attributes to allow (override defaults)

        Returns:
            Sanitized HTML
        """
        tags = allowed_tags or self._allowed_tags
        attrs = allowed_attrs or self._allowed_attrs

        # Escape all HTML first
        safe_content = html.escape(html_content)

        # Re-enable allowed tags
        for tag in tags:
            # Opening tags
            safe_content = re.sub(
                rf'&lt;({tag})(&gt;|(\s[^&]*?)&gt;)',
                r'<\1\2>'.replace('&gt;', '>'),
                safe_content,
                flags=re.IGNORECASE
            )
            # Self-closing tags
            safe_content = re.sub(
                rf'&lt;({tag})\s*/&gt;',
                r'<\1/>',
                safe_content,
                flags=re.IGNORECASE
            )
            # Closing tags
            safe_content = re.sub(
                rf'&lt;/({tag})&gt;',
                r'</\1>',
                safe_content,
                flags=re.IGNORECASE
            )

        return safe_content

    def strip_html(self, html_content: str) -> str:
        """Remove all HTML tags."""
        # Remove tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Decode entities
        text = html.unescape(text)
        return text

    def sanitize_for_sql(self, value: str) -> str:
        """
        Sanitize value for SQL queries.

        Note: Always prefer parameterized queries over this.

        Args:
            value: Value to sanitize

        Returns:
            SQL-safe string
        """
        # Basic sanitization first
        value = self.sanitize(value)

        # Escape single quotes
        value = value.replace("'", "''")

        # Remove dangerous patterns
        for pattern in self._sql_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)

        return value

    def is_sql_injection(self, value: str) -> bool:
        """Check if value looks like SQL injection."""
        for pattern in self._sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def sanitize_for_command(self, value: str) -> str:
        """
        Sanitize value for shell commands.

        Note: Avoid using user input in commands when possible.

        Args:
            value: Value to sanitize

        Returns:
            Shell-safe string
        """
        # Basic sanitization first
        value = self.sanitize(value)

        # Remove dangerous characters
        for pattern in self._command_patterns:
            value = re.sub(pattern, '', value)

        # Only allow alphanumeric, dash, underscore, dot, space
        value = re.sub(r'[^a-zA-Z0-9\-_.\s]', '', value)

        return value

    def is_command_injection(self, value: str) -> bool:
        """Check if value looks like command injection."""
        for pattern in self._command_patterns:
            if re.search(pattern, value):
                return True
        return False

    def sanitize_path(self, path: str) -> str:
        """
        Sanitize file path to prevent traversal.

        Args:
            path: File path to sanitize

        Returns:
            Safe path string
        """
        # Basic sanitization
        path = self.sanitize(path)

        # Remove path traversal
        path = path.replace('..', '')

        # Remove absolute path indicators
        path = path.lstrip('/\\')

        # Remove drive letters (Windows)
        path = re.sub(r'^[a-zA-Z]:', '', path)

        # Only allow safe characters
        path = re.sub(r'[^a-zA-Z0-9\-_./\\]', '', path)

        # Normalize path separators
        path = path.replace('\\', '/')

        # Remove double slashes
        path = re.sub(r'/+', '/', path)

        return path

    def is_path_traversal(self, path: str) -> bool:
        """Check if path contains traversal attempt."""
        dangerous_patterns = [
            r'\.\.',
            r'^/',
            r'^[a-zA-Z]:',
            r'%2e%2e',  # URL encoded ..
            r'%252e',  # Double encoded .
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    def sanitize_for_xss(self, value: str) -> str:
        """
        Sanitize value to prevent XSS attacks.

        Args:
            value: Value to sanitize

        Returns:
            XSS-safe string
        """
        # HTML escape
        value = html.escape(value)

        # Remove dangerous patterns
        for pattern in self._xss_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)

        return value

    def is_xss_attempt(self, value: str) -> bool:
        """Check if value looks like XSS attempt."""
        for pattern in self._xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def sanitize_dict(
        self,
        data: Dict[str, Any],
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Sanitize all string values in a dictionary.

        Args:
            data: Dictionary to sanitize
            recursive: Whether to sanitize nested structures

        Returns:
            Sanitized dictionary
        """
        result = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = self.sanitize(str(key)) if isinstance(key, str) else key

            # Sanitize value
            if isinstance(value, str):
                result[safe_key] = self.sanitize(value)
            elif isinstance(value, dict) and recursive:
                result[safe_key] = self.sanitize_dict(value, recursive)
            elif isinstance(value, list) and recursive:
                result[safe_key] = [
                    self.sanitize(v) if isinstance(v, str)
                    else self.sanitize_dict(v, recursive) if isinstance(v, dict)
                    else v
                    for v in value
                ]
            else:
                result[safe_key] = value

        return result


# Convenience functions


def sanitize_input(value: str, max_length: int = 10000) -> str:
    """Quick input sanitization."""
    sanitizer = InputSanitizer()
    return sanitizer.sanitize(value, max_length)


def sanitize_html(html_content: str) -> str:
    """Quick HTML sanitization."""
    sanitizer = InputSanitizer()
    return sanitizer.sanitize_html(html_content)


def sanitize_sql(value: str) -> str:
    """Quick SQL sanitization."""
    sanitizer = InputSanitizer()
    return sanitizer.sanitize_for_sql(value)


def escape_special_chars(value: str) -> str:
    """Escape special characters."""
    return html.escape(value)


def validate_safe_path(user_path: str, base_directory: str) -> Optional[str]:
    """
    Validate that a user-provided path is safe and within the base directory.

    This is the recommended way to handle user-provided file paths to prevent
    path traversal attacks.

    Args:
        user_path: User-provided path (potentially unsafe)
        base_directory: Base directory that paths must be within

    Returns:
        Resolved absolute path if safe, None if path is unsafe

    Example:
        safe_path = validate_safe_path(user_input, "/app/uploads")
        if safe_path is None:
            raise ValueError("Invalid path")
        # Use safe_path for file operations
    """
    import os
    from pathlib import Path

    try:
        # Resolve the base directory to absolute path
        base = Path(base_directory).resolve()

        # Sanitize the user path first
        sanitizer = InputSanitizer()
        sanitized = sanitizer.sanitize_path(user_path)

        # Combine base with user path and resolve
        combined = (base / sanitized).resolve()

        # Security check: ensure the resolved path is within base directory
        # This prevents traversal attacks even with symlinks
        if not str(combined).startswith(str(base)):
            return None

        # Additional check: ensure path doesn't contain suspicious patterns
        if sanitizer.is_path_traversal(user_path):
            return None

        return str(combined)

    except (ValueError, OSError):
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for filesystem use.

    Args:
        filename: Original filename

    Returns:
        Safe filename with dangerous characters removed
    """
    # Remove path components (only keep filename)
    filename = filename.replace('\\', '/').split('/')[-1]

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Remove or replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Remove control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if ext:
            filename = name[:250] + '.' + ext[:4]
        else:
            filename = filename[:255]

    # Prevent empty filename
    if not filename or filename.strip() == '':
        filename = 'unnamed_file'

    return filename
