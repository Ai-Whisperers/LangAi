"""
External API Response Validation.

Provides validation and safe parsing of responses from external APIs
(Anthropic, Tavily, etc.) to prevent crashes from unexpected data.

Usage:
    from company_researcher.llm.response_validation import (
        validate_anthropic_response,
        validate_tavily_response,
        safe_get,
        ValidationError
    )

    # Validate Anthropic response
    try:
        validated = validate_anthropic_response(response)
        content = validated.content
    except ValidationError as e:
        logger.error(f"Invalid response: {e}")

    # Safe nested access
    value = safe_get(data, "nested.path.to.value", default="fallback")
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from ..utils import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ValidationError(Exception):
    """Raised when API response validation fails."""

    def __init__(self, message: str, field: str = None, received: Any = None):
        self.field = field
        self.received = received
        super().__init__(message)


class ResponseValidationWarning(Warning):
    """Warning for non-critical validation issues."""


# ============================================================================
# Generic Validation Utilities
# ============================================================================

def safe_get(
    data: Union[Dict, Any],
    path: str,
    default: T = None,
    expected_type: Type[T] = None
) -> T:
    """
    Safely get a nested value from a dict or object.

    Args:
        data: Dictionary or object to traverse
        path: Dot-separated path (e.g., "usage.input_tokens")
        default: Default value if path not found
        expected_type: Optional type to validate against

    Returns:
        Value at path or default

    Example:
        value = safe_get(response, "usage.input_tokens", default=0)
    """
    if data is None:
        return default

    keys = path.split(".")
    current = data

    for key in keys:
        try:
            if isinstance(current, dict):
                current = current.get(key)
            elif hasattr(current, key):
                current = getattr(current, key)
            else:
                return default

            if current is None:
                return default
        except (KeyError, AttributeError, TypeError):
            return default

    if expected_type is not None and current is not None:
        if not isinstance(current, expected_type):
            logger.warning(
                f"Type mismatch at '{path}': expected {expected_type.__name__}, "
                f"got {type(current).__name__}"
            )
            return default

    return current if current is not None else default


def validate_required_fields(
    data: Dict[str, Any],
    required_fields: List[str],
    context: str = "response"
) -> None:
    """
    Validate that required fields exist in a dictionary.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context for error messages

    Raises:
        ValidationError: If any required field is missing
    """
    if not isinstance(data, dict):
        raise ValidationError(
            f"{context} must be a dictionary, got {type(data).__name__}",
            field=None,
            received=type(data).__name__
        )

    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValidationError(
            f"{context} missing required fields: {', '.join(missing)}",
            field=missing[0],
            received=list(data.keys())
        )


def validate_type(
    value: Any,
    expected_type: Type,
    field_name: str,
    allow_none: bool = False
) -> None:
    """
    Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Field name for error messages
        allow_none: Whether None is acceptable

    Raises:
        ValidationError: If type doesn't match
    """
    if value is None:
        if not allow_none:
            raise ValidationError(
                f"Field '{field_name}' is None but required",
                field=field_name,
                received=None
            )
        return

    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Field '{field_name}' expected {expected_type.__name__}, "
            f"got {type(value).__name__}",
            field=field_name,
            received=type(value).__name__
        )


def validate_positive_int(value: Any, field_name: str) -> int:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        field_name: Field name for error messages

    Returns:
        Validated integer

    Raises:
        ValidationError: If not a positive integer
    """
    if not isinstance(value, int):
        raise ValidationError(
            f"Field '{field_name}' must be an integer, got {type(value).__name__}",
            field=field_name,
            received=value
        )

    if value < 0:
        raise ValidationError(
            f"Field '{field_name}' must be non-negative, got {value}",
            field=field_name,
            received=value
        )

    return value


def validate_string_not_empty(value: Any, field_name: str) -> str:
    """
    Validate that a value is a non-empty string.

    Args:
        value: Value to validate
        field_name: Field name for error messages

    Returns:
        Validated string

    Raises:
        ValidationError: If not a non-empty string
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Field '{field_name}' must be a string, got {type(value).__name__}",
            field=field_name,
            received=value
        )

    if not value.strip():
        raise ValidationError(
            f"Field '{field_name}' must not be empty",
            field=field_name,
            received=value
        )

    return value


# ============================================================================
# Anthropic Response Validation
# ============================================================================

@dataclass
class ValidatedAnthropicResponse:
    """Validated Anthropic API response."""
    content: str
    model: str
    stop_reason: Optional[str]
    input_tokens: int
    output_tokens: int
    raw_response: Any


def validate_anthropic_response(
    response: Any,
    require_content: bool = True,
    max_content_length: int = 1_000_000
) -> ValidatedAnthropicResponse:
    """
    Validate an Anthropic API response.

    Args:
        response: Raw Anthropic response object
        require_content: Whether content is required
        max_content_length: Maximum allowed content length

    Returns:
        ValidatedAnthropicResponse with extracted data

    Raises:
        ValidationError: If response is invalid
    """
    if response is None:
        raise ValidationError("Anthropic response is None")

    # Validate content blocks
    content_blocks = safe_get(response, "content", default=[])
    if not isinstance(content_blocks, list):
        raise ValidationError(
            "Response content must be a list",
            field="content",
            received=type(content_blocks).__name__
        )

    # Extract text content
    content = ""
    for block in content_blocks:
        if safe_get(block, "type") == "text":
            text = safe_get(block, "text", default="")
            if isinstance(text, str):
                content += text

    if require_content and not content.strip():
        raise ValidationError(
            "Response contains no text content",
            field="content",
            received=content_blocks
        )

    if len(content) > max_content_length:
        logger.warning(
            f"Response content exceeds max length ({len(content)} > {max_content_length}), truncating"
        )
        content = content[:max_content_length]

    # Validate model
    model = safe_get(response, "model", default="unknown")
    if not isinstance(model, str):
        model = str(model)

    # Validate stop reason
    stop_reason = safe_get(response, "stop_reason")
    if stop_reason is not None and not isinstance(stop_reason, str):
        stop_reason = str(stop_reason)

    # Validate usage
    usage = safe_get(response, "usage", default={})
    input_tokens = safe_get(usage, "input_tokens", default=0)
    output_tokens = safe_get(usage, "output_tokens", default=0)

    # Ensure tokens are valid integers
    try:
        input_tokens = validate_positive_int(input_tokens, "usage.input_tokens")
    except ValidationError:
        input_tokens = 0
        logger.warning("Invalid input_tokens in response, defaulting to 0")

    try:
        output_tokens = validate_positive_int(output_tokens, "usage.output_tokens")
    except ValidationError:
        output_tokens = 0
        logger.warning("Invalid output_tokens in response, defaulting to 0")

    return ValidatedAnthropicResponse(
        content=content,
        model=model,
        stop_reason=stop_reason,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        raw_response=response
    )


def extract_anthropic_content(response: Any, default: str = "") -> str:
    """
    Safely extract text content from an Anthropic response.

    Args:
        response: Raw Anthropic response
        default: Default value if extraction fails

    Returns:
        Extracted text content or default
    """
    try:
        validated = validate_anthropic_response(response, require_content=False)
        return validated.content or default
    except ValidationError as e:
        logger.warning(f"Failed to extract Anthropic content: {e}")
        return default


# ============================================================================
# Tavily Response Validation
# ============================================================================

@dataclass
class ValidatedTavilyResult:
    """A validated Tavily search result."""
    title: str
    url: str
    content: str
    score: float
    raw_result: Dict


@dataclass
class ValidatedTavilyResponse:
    """Validated Tavily API response."""
    query: str
    results: List[ValidatedTavilyResult]
    answer: Optional[str]
    raw_response: Dict


def validate_tavily_response(
    response: Dict[str, Any],
    max_results: int = 100,
    require_results: bool = False
) -> ValidatedTavilyResponse:
    """
    Validate a Tavily search API response.

    Args:
        response: Raw Tavily response dictionary
        max_results: Maximum results to process
        require_results: Whether at least one result is required

    Returns:
        ValidatedTavilyResponse with extracted data

    Raises:
        ValidationError: If response is invalid
    """
    if not isinstance(response, dict):
        raise ValidationError(
            f"Tavily response must be a dictionary, got {type(response).__name__}",
            received=type(response).__name__
        )

    # Extract query
    query = safe_get(response, "query", default="")
    if not isinstance(query, str):
        query = str(query) if query is not None else ""

    # Validate and extract results
    raw_results = safe_get(response, "results", default=[])
    if not isinstance(raw_results, list):
        logger.warning("Tavily results is not a list, using empty list")
        raw_results = []

    results = []
    for i, result in enumerate(raw_results[:max_results]):
        if not isinstance(result, dict):
            logger.warning(f"Skipping non-dict result at index {i}")
            continue

        try:
            validated_result = ValidatedTavilyResult(
                title=safe_get(result, "title", default=""),
                url=safe_get(result, "url", default=""),
                content=safe_get(result, "content", default=""),
                score=float(safe_get(result, "score", default=0.0)),
                raw_result=result
            )
            results.append(validated_result)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to validate Tavily result at index {i}: {e}")

    if require_results and not results:
        raise ValidationError(
            "Tavily response contains no valid results",
            field="results",
            received=raw_results
        )

    # Extract answer if present
    answer = safe_get(response, "answer")
    if answer is not None and not isinstance(answer, str):
        answer = str(answer)

    return ValidatedTavilyResponse(
        query=query,
        results=results,
        answer=answer,
        raw_response=response
    )


def extract_tavily_results(
    response: Dict[str, Any],
    default: List[Dict] = None
) -> List[Dict[str, str]]:
    """
    Safely extract search results from a Tavily response.

    Args:
        response: Raw Tavily response
        default: Default value if extraction fails

    Returns:
        List of result dictionaries with title, url, content
    """
    if default is None:
        default = []

    try:
        validated = validate_tavily_response(response, require_results=False)
        return [
            {
                "title": r.title,
                "url": r.url,
                "content": r.content,
                "score": r.score
            }
            for r in validated.results
        ]
    except ValidationError as e:
        logger.warning(f"Failed to extract Tavily results: {e}")
        return default


# ============================================================================
# Generic JSON Response Validation
# ============================================================================

def validate_json_response(
    response: Any,
    schema: Dict[str, Type],
    context: str = "JSON response"
) -> Dict[str, Any]:
    """
    Validate a JSON response against a simple schema.

    Args:
        response: Response to validate (should be dict)
        schema: Dict mapping field names to expected types
        context: Context for error messages

    Returns:
        Validated response dictionary

    Raises:
        ValidationError: If validation fails

    Example:
        schema = {
            "status": str,
            "data": dict,
            "count": int
        }
        validated = validate_json_response(response, schema)
    """
    if not isinstance(response, dict):
        raise ValidationError(
            f"{context} must be a dictionary, got {type(response).__name__}",
            received=type(response).__name__
        )

    validated = {}
    for field, expected_type in schema.items():
        value = response.get(field)
        if value is None:
            validated[field] = None
            continue

        if not isinstance(value, expected_type):
            raise ValidationError(
                f"{context} field '{field}' expected {expected_type.__name__}, "
                f"got {type(value).__name__}",
                field=field,
                received=type(value).__name__
            )
        validated[field] = value

    return validated


# ============================================================================
# Response Size Limits
# ============================================================================

def enforce_response_limits(
    content: str,
    max_length: int = 500_000,
    truncate: bool = True
) -> str:
    """
    Enforce size limits on response content.

    Args:
        content: Content to check
        max_length: Maximum allowed length
        truncate: Whether to truncate or raise error

    Returns:
        Content (possibly truncated)

    Raises:
        ValidationError: If content exceeds limit and truncate=False
    """
    if not isinstance(content, str):
        return str(content)[:max_length] if truncate else str(content)

    if len(content) <= max_length:
        return content

    if truncate:
        logger.warning(
            f"Response content truncated from {len(content)} to {max_length} characters"
        )
        return content[:max_length]
    else:
        raise ValidationError(
            f"Response content exceeds maximum length ({len(content)} > {max_length})",
            field="content",
            received=len(content)
        )
