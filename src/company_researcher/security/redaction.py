"""
Content Redaction - Sensitive data protection.

Provides:
- PII detection and redaction
- Configurable redaction patterns
- Format-preserving redaction
- Audit trail for redactions
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern, Tuple


class RedactionType(str, Enum):
    """Types of sensitive data to redact."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "dob"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    API_KEY = "api_key"
    PASSWORD = "password"
    CUSTOM = "custom"


@dataclass
class RedactionPattern:
    """A pattern for detecting sensitive data."""

    name: str
    pattern: str
    replacement: str = "[REDACTED]"
    redaction_type: RedactionType = RedactionType.CUSTOM
    case_sensitive: bool = False
    _compiled: Optional[Pattern] = field(default=None, repr=False)

    def __post_init__(self):
        flags = 0 if self.case_sensitive else re.IGNORECASE
        self._compiled = re.compile(self.pattern, flags)

    def find_matches(self, text: str) -> List[Tuple[int, int, str]]:
        """Find all matches in text. Returns (start, end, matched_text)."""
        if self._compiled is None:
            return []
        matches = []
        for match in self._compiled.finditer(text):
            matches.append((match.start(), match.end(), match.group()))
        return matches

    def redact(self, text: str) -> Tuple[str, int]:
        """Redact matches in text. Returns (redacted_text, count)."""
        if self._compiled is None:
            return text, 0
        count = len(self._compiled.findall(text))
        redacted = self._compiled.sub(self.replacement, text)
        return redacted, count


@dataclass
class RedactionConfig:
    """Configuration for content redaction."""

    patterns: List[RedactionPattern] = field(default_factory=list)
    preserve_format: bool = False  # Use format-preserving redaction
    log_redactions: bool = True
    redaction_char: str = "X"


# Built-in redaction patterns
BUILTIN_PATTERNS = {
    RedactionType.EMAIL: RedactionPattern(
        name="email",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        replacement="[EMAIL]",
        redaction_type=RedactionType.EMAIL,
    ),
    RedactionType.PHONE: RedactionPattern(
        name="phone",
        pattern=r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
        replacement="[PHONE]",
        redaction_type=RedactionType.PHONE,
    ),
    RedactionType.SSN: RedactionPattern(
        name="ssn",
        pattern=r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        replacement="[SSN]",
        redaction_type=RedactionType.SSN,
    ),
    RedactionType.CREDIT_CARD: RedactionPattern(
        name="credit_card",
        pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        replacement="[CREDIT_CARD]",
        redaction_type=RedactionType.CREDIT_CARD,
    ),
    RedactionType.IP_ADDRESS: RedactionPattern(
        name="ip_address",
        pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        replacement="[IP]",
        redaction_type=RedactionType.IP_ADDRESS,
    ),
    RedactionType.DATE_OF_BIRTH: RedactionPattern(
        name="dob",
        pattern=r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b",
        replacement="[DOB]",
        redaction_type=RedactionType.DATE_OF_BIRTH,
    ),
    RedactionType.API_KEY: RedactionPattern(
        name="api_key",
        pattern=r"\b(?:sk[-_]|api[-_]?key[-_]?|apikey[-_]?|key[-_]?)[a-zA-Z0-9]{20,}\b",
        replacement="[API_KEY]",
        redaction_type=RedactionType.API_KEY,
        case_sensitive=False,
    ),
    RedactionType.PASSWORD: RedactionPattern(
        name="password",
        pattern=r'(?:password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]+)["\']?',
        replacement="password=[REDACTED]",
        redaction_type=RedactionType.PASSWORD,
        case_sensitive=False,
    ),
}


@dataclass
class RedactionResult:
    """Result of a redaction operation."""

    original_length: int
    redacted_length: int
    redaction_count: int
    redacted_types: Dict[str, int] = field(default_factory=dict)


class ContentRedactor:
    """
    Content redaction for sensitive data.

    Usage:
        redactor = ContentRedactor()

        # Add built-in patterns
        redactor.add_pattern(RedactionType.EMAIL)
        redactor.add_pattern(RedactionType.PHONE)
        redactor.add_pattern(RedactionType.SSN)

        # Redact text
        safe_text = redactor.redact(text)

        # Get detailed results
        safe_text, result = redactor.redact_with_details(text)

        # Redact dictionary
        safe_data = redactor.redact_dict(data)
    """

    def __init__(self, config: RedactionConfig = None):
        self.config = config or RedactionConfig()
        self._patterns: List[RedactionPattern] = []
        self._redaction_log: List[Dict[str, Any]] = []

    def add_pattern(
        self, pattern_type: RedactionType = None, pattern: RedactionPattern = None
    ) -> None:
        """
        Add a redaction pattern.

        Args:
            pattern_type: Built-in pattern type
            pattern: Custom pattern
        """
        if pattern:
            self._patterns.append(pattern)
        elif pattern_type and pattern_type in BUILTIN_PATTERNS:
            self._patterns.append(BUILTIN_PATTERNS[pattern_type])

    def add_custom_pattern(self, name: str, pattern: str, replacement: str = "[REDACTED]") -> None:
        """Add a custom redaction pattern."""
        self._patterns.append(
            RedactionPattern(
                name=name,
                pattern=pattern,
                replacement=replacement,
                redaction_type=RedactionType.CUSTOM,
            )
        )

    def redact(self, text: str) -> str:
        """
        Redact sensitive data from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        redacted, _ = self.redact_with_details(text)
        return redacted

    def redact_with_details(self, text: str) -> Tuple[str, RedactionResult]:
        """
        Redact with detailed results.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, RedactionResult)
        """
        original_length = len(text)
        total_count = 0
        type_counts: Dict[str, int] = {}

        for pattern in self._patterns:
            text, count = pattern.redact(text)
            if count > 0:
                total_count += count
                type_counts[pattern.name] = type_counts.get(pattern.name, 0) + count

                if self.config.log_redactions:
                    self._redaction_log.append({"pattern": pattern.name, "count": count})

        result = RedactionResult(
            original_length=original_length,
            redacted_length=len(text),
            redaction_count=total_count,
            redacted_types=type_counts,
        )

        return text, result

    def redact_dict(self, data: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
        """
        Redact sensitive data from a dictionary.

        Args:
            data: Dictionary to redact
            recursive: Whether to redact nested structures

        Returns:
            Redacted dictionary
        """
        return self._redact_value(data, recursive)

    def _redact_value(self, value: Any, recursive: bool) -> Any:
        """Recursively redact a value."""
        if isinstance(value, str):
            return self.redact(value)
        elif isinstance(value, dict) and recursive:
            return {k: self._redact_value(v, recursive) for k, v in value.items()}
        elif isinstance(value, list) and recursive:
            return [self._redact_value(item, recursive) for item in value]
        return value

    def find_sensitive(self, text: str) -> List[Dict[str, Any]]:
        """
        Find sensitive data without redacting.

        Args:
            text: Text to scan

        Returns:
            List of found sensitive items
        """
        findings = []
        for pattern in self._patterns:
            matches = pattern.find_matches(text)
            for start, end, matched in matches:
                findings.append(
                    {
                        "type": pattern.name,
                        "start": start,
                        "end": end,
                        "preview": matched[:3] + "..." if len(matched) > 3 else matched,
                    }
                )
        return findings

    def get_redaction_log(self) -> List[Dict[str, Any]]:
        """Get the redaction log."""
        return self._redaction_log.copy()

    def clear_log(self) -> None:
        """Clear the redaction log."""
        self._redaction_log.clear()

    @classmethod
    def create_default(cls) -> "ContentRedactor":
        """Create a redactor with common patterns."""
        redactor = cls()
        redactor.add_pattern(RedactionType.EMAIL)
        redactor.add_pattern(RedactionType.PHONE)
        redactor.add_pattern(RedactionType.SSN)
        redactor.add_pattern(RedactionType.CREDIT_CARD)
        redactor.add_pattern(RedactionType.API_KEY)
        return redactor


# Format-preserving redaction


def format_preserving_redact(text: str, pattern: Pattern, redaction_char: str = "X") -> str:
    """
    Redact while preserving format (same length, similar structure).

    Args:
        text: Text to redact
        pattern: Compiled regex pattern
        redaction_char: Character to use for redaction

    Returns:
        Redacted text with preserved format
    """

    def replacer(match):
        original = match.group()
        redacted = ""
        for char in original:
            if char.isdigit():
                redacted += "0"
            elif char.isalpha():
                redacted += redaction_char
            else:
                redacted += char
        return redacted

    return pattern.sub(replacer, text)


# Convenience functions


def redact_text(
    text: str, patterns: List[RedactionType] = None, custom_patterns: List[RedactionPattern] = None
) -> str:
    """
    Quick text redaction.

    Args:
        text: Text to redact
        patterns: List of built-in pattern types
        custom_patterns: Custom patterns

    Returns:
        Redacted text
    """
    redactor = ContentRedactor()

    for pattern_type in patterns or []:
        redactor.add_pattern(pattern_type)

    for pattern in custom_patterns or []:
        redactor.add_pattern(pattern=pattern)

    if not redactor._patterns:
        redactor = ContentRedactor.create_default()

    return redactor.redact(text)


def redact_dict(data: Dict[str, Any], patterns: List[RedactionType] = None) -> Dict[str, Any]:
    """
    Quick dictionary redaction.

    Args:
        data: Dictionary to redact
        patterns: Pattern types to use

    Returns:
        Redacted dictionary
    """
    redactor = ContentRedactor()
    for pattern_type in patterns or []:
        redactor.add_pattern(pattern_type)

    if not redactor._patterns:
        redactor = ContentRedactor.create_default()

    return redactor.redact_dict(data)
