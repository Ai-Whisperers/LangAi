"""Custom exceptions for AI components."""
from typing import Optional


class AIComponentError(Exception):
    """
    Base exception for AI component errors.

    Provides structured error information including component name,
    original error, and context for debugging.
    """

    def __init__(
        self,
        component: str,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        self.component = component
        self.original_error = original_error
        self.context = context or {}
        super().__init__(f"[{component}] {message}")

    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging."""
        return {
            "component": self.component,
            "message": str(self),
            "original_error": str(self.original_error) if self.original_error else None,
            "original_error_type": type(self.original_error).__name__ if self.original_error else None,
            "context": self.context
        }


class AIExtractionError(AIComponentError):
    """Error during data extraction."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        super().__init__("extraction", message, original_error, context)


class AISentimentError(AIComponentError):
    """Error during sentiment analysis."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        super().__init__("sentiment", message, original_error, context)


class AIQueryGenerationError(AIComponentError):
    """Error during query generation."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        super().__init__("query_generation", message, original_error, context)


class AIQualityAssessmentError(AIComponentError):
    """Error during quality assessment."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        super().__init__("quality_assessment", message, original_error, context)


class AIClassificationError(AIComponentError):
    """Error during classification."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        super().__init__("classification", message, original_error, context)


class AIFallbackTriggered(AIComponentError):
    """
    AI component failed, falling back to legacy logic.

    This is raised when AI fails and fallback is disabled,
    or used internally to signal fallback occurred.
    """

    def __init__(
        self,
        component: str,
        message: str,
        original_error: Optional[Exception] = None,
        used_fallback: bool = True
    ):
        super().__init__(component, message, original_error)
        self.used_fallback = used_fallback


class AICostLimitExceeded(AIComponentError):
    """
    Cost limit exceeded for AI component.

    Raised when a single call or cumulative calls exceed cost limits.
    """

    def __init__(
        self,
        component: str,
        current_cost: float,
        limit: float,
        message: Optional[str] = None
    ):
        self.current_cost = current_cost
        self.limit = limit
        msg = message or f"Cost ${current_cost:.4f} exceeds limit ${limit:.4f}"
        super().__init__(component, msg)


class AIParsingError(AIComponentError):
    """Error parsing LLM response."""

    def __init__(
        self,
        component: str,
        raw_response: str,
        expected_format: str,
        original_error: Optional[Exception] = None
    ):
        self.raw_response = raw_response[:500]  # Truncate for logging
        self.expected_format = expected_format
        super().__init__(
            component,
            f"Failed to parse response. Expected {expected_format}",
            original_error,
            {"raw_response_preview": raw_response[:200]}
        )


class AITimeoutError(AIComponentError):
    """Timeout waiting for AI response."""

    def __init__(
        self,
        component: str,
        timeout_seconds: float,
        original_error: Optional[Exception] = None
    ):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            component,
            f"Timeout after {timeout_seconds}s",
            original_error
        )
