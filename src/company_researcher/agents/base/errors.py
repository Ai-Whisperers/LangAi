"""
Agent Errors - Standardized exception hierarchy and error handling.

Provides consistent error handling patterns across all agents:
- Custom exception classes for different error types
- Error result creation helpers
- Retry logic with configurable policies
- Error logging utilities

Usage:
    from company_researcher.agents.base.errors import (
        AgentError,
        ParsingError,
        LLMError,
        SearchError,
        handle_agent_error,
        create_error_result,
    )

    try:
        result = agent.analyze(company_name, search_results)
    except ParsingError as e:
        return handle_agent_error(e, agent_name="financial")
    except LLMError as e:
        return handle_agent_error(e, agent_name="financial", retry=True)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps
import time
from ...utils import get_logger

logger = get_logger(__name__)


# ==============================================================================
# Exception Hierarchy
# ==============================================================================

class AgentError(Exception):
    """Base exception for all agent-related errors."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/reporting."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "agent_name": self.agent_name,
            "details": self.details
        }


class ParsingError(AgentError):
    """Error during LLM response parsing."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        raw_response: Optional[str] = None,
        expected_format: Optional[str] = None
    ):
        details = {
            "raw_response_preview": raw_response[:200] if raw_response else None,
            "expected_format": expected_format
        }
        super().__init__(message, agent_name, details)
        self.raw_response = raw_response
        self.expected_format = expected_format


class LLMError(AgentError):
    """Error from LLM API call."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        model: Optional[str] = None,
        status_code: Optional[int] = None,
        retryable: bool = True
    ):
        details = {
            "model": model,
            "status_code": status_code,
            "retryable": retryable
        }
        super().__init__(message, agent_name, details)
        self.model = model
        self.status_code = status_code
        self.retryable = retryable


class SearchError(AgentError):
    """Error during search operations."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        query: Optional[str] = None,
        provider: Optional[str] = None
    ):
        details = {
            "query": query,
            "provider": provider
        }
        super().__init__(message, agent_name, details)
        self.query = query
        self.provider = provider


class ConfigurationError(AgentError):
    """Error in agent configuration."""


class ValidationError(AgentError):
    """Error in input validation."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {
            "field": field,
            "value": str(value)[:100] if value else None
        }
        super().__init__(message, agent_name, details)
        self.field = field
        self.value = value


class ExtractionError(AgentError):
    """Error during data extraction from analysis."""

    def __init__(
        self,
        message: str,
        agent_name: str = "unknown",
        field: Optional[str] = None,
        analysis_preview: Optional[str] = None
    ):
        details = {
            "field": field,
            "analysis_preview": analysis_preview[:200] if analysis_preview else None
        }
        super().__init__(message, agent_name, details)
        self.field = field


# ==============================================================================
# Error Severity
# ==============================================================================

class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"  # Agent cannot continue
    HIGH = "high"          # Significant functionality lost
    MEDIUM = "medium"      # Partial results available
    LOW = "low"            # Minor issue, workaround applied
    WARNING = "warning"    # Not an error, but noteworthy


# ==============================================================================
# Error Result Creation
# ==============================================================================

def create_error_result(
    agent_name: str,
    error: Exception,
    severity: ErrorSeverity = ErrorSeverity.HIGH,
    partial_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error result for agent output.

    Args:
        agent_name: Name of the agent that errored
        error: The exception that occurred
        severity: Severity level of the error
        partial_result: Any partial results that were obtained

    Returns:
        Standardized error result dictionary
    """
    error_info = {
        "error": True,
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "severity": severity.value,
    }

    if isinstance(error, AgentError):
        error_info["details"] = error.details

    agent_output = {
        "analysis": f"Error: {str(error)}",
        "data_extracted": False,
        "cost": 0.0,
        **error_info
    }

    if partial_result:
        agent_output["partial_result"] = partial_result

    return {
        "agent_outputs": {agent_name: agent_output},
        "total_cost": 0.0,
        "total_tokens": {"input": 0, "output": 0}
    }


def create_empty_result_with_reason(
    agent_name: str,
    reason: str,
    status: str = "no_data"
) -> Dict[str, Any]:
    """
    Create an empty result with a specific reason.

    Args:
        agent_name: Name of the agent
        reason: Reason for empty result
        status: Status code for the result

    Returns:
        Empty result dictionary with reason
    """
    return {
        "agent_outputs": {
            agent_name: {
                "analysis": reason,
                "data_extracted": False,
                "status": status,
                "cost": 0.0
            }
        },
        "total_cost": 0.0,
        "total_tokens": {"input": 0, "output": 0}
    }


# ==============================================================================
# Error Handler
# ==============================================================================

def handle_agent_error(
    error: Exception,
    agent_name: str,
    logger: Optional[logging.Logger] = None,
    reraise: bool = False,
    severity: ErrorSeverity = ErrorSeverity.HIGH
) -> Dict[str, Any]:
    """
    Handle an agent error with logging and result creation.

    Args:
        error: The exception that occurred
        agent_name: Name of the agent
        logger: Optional logger instance
        reraise: Whether to reraise after handling
        severity: Error severity level

    Returns:
        Error result dictionary

    Raises:
        The original exception if reraise=True
    """
    log = logger or logging.getLogger(f"agent.{agent_name}")

    # Log based on severity
    if severity in (ErrorSeverity.CRITICAL, ErrorSeverity.HIGH):
        log.error(f"Agent error: {error}", exc_info=True)
    elif severity == ErrorSeverity.MEDIUM:
        log.warning(f"Agent warning: {error}")
    else:
        log.info(f"Agent notice: {error}")

    # Create result
    result = create_error_result(agent_name, error, severity)

    if reraise:
        raise error

    return result


# ==============================================================================
# Retry Decorator
# ==============================================================================

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple = field(default_factory=lambda: (LLMError, SearchError))
    on_retry: Optional[Callable[[Exception, int], None]] = None


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to agent methods.

    Args:
        config: Retry configuration

    Usage:
        @with_retry(RetryConfig(max_retries=3))
        def call_llm(self, prompt):
            return self.client.messages.create(...)
    """
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except cfg.retryable_exceptions as e:
                    last_error = e

                    if attempt < cfg.max_retries:
                        delay = cfg.delay * (cfg.backoff_factor ** attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{cfg.max_retries} "
                            f"after {delay:.1f}s: {e}"
                        )

                        if cfg.on_retry:
                            cfg.on_retry(e, attempt)

                        time.sleep(delay)
                    else:
                        logger.error(f"All {cfg.max_retries} retries failed")
                        raise

            # Should not reach here, but just in case
            if last_error:
                raise last_error
            raise RuntimeError("Retry logic error")

        return wrapper
    return decorator


# ==============================================================================
# Error Context Manager
# ==============================================================================

class AgentErrorContext:
    """
    Context manager for standardized error handling in agents.

    Usage:
        with AgentErrorContext("financial", logger) as ctx:
            result = agent.analyze(company_name, search_results)
            if not result:
                ctx.set_warning("No results found")

        if ctx.has_error:
            return ctx.error_result
    """

    def __init__(
        self,
        agent_name: str,
        logger: Optional[logging.Logger] = None
    ):
        self.agent_name = agent_name
        self.logger = logger or logging.getLogger(f"agent.{agent_name}")
        self.error: Optional[Exception] = None
        self.warning: Optional[str] = None
        self.severity = ErrorSeverity.MEDIUM

    def __enter__(self) -> "AgentErrorContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_val is not None:
            self.error = exc_val
            self.logger.error(f"Agent error: {exc_val}", exc_info=True)
            # Don't suppress the exception
            return False
        return True

    @property
    def has_error(self) -> bool:
        """Check if an error occurred."""
        return self.error is not None

    @property
    def error_result(self) -> Dict[str, Any]:
        """Get error result if error occurred."""
        if self.error:
            return create_error_result(
                self.agent_name,
                self.error,
                self.severity
            )
        return {}

    def set_warning(self, message: str) -> None:
        """Set a warning message."""
        self.warning = message
        self.logger.warning(message)

    def set_severity(self, severity: ErrorSeverity) -> None:
        """Set error severity."""
        self.severity = severity


# ==============================================================================
# Validation Helpers
# ==============================================================================

def validate_search_results(
    results: Any,
    agent_name: str,
    min_results: int = 1
) -> List[Dict[str, Any]]:
    """
    Validate search results input.

    Args:
        results: Search results to validate
        agent_name: Agent name for error messages
        min_results: Minimum required results

    Returns:
        Validated search results list

    Raises:
        ValidationError: If validation fails
    """
    if results is None:
        raise ValidationError(
            "Search results cannot be None",
            agent_name=agent_name,
            field="search_results",
            value=None
        )

    if not isinstance(results, list):
        raise ValidationError(
            f"Search results must be a list, got {type(results).__name__}",
            agent_name=agent_name,
            field="search_results",
            value=type(results).__name__
        )

    if len(results) < min_results:
        raise ValidationError(
            f"Need at least {min_results} search results, got {len(results)}",
            agent_name=agent_name,
            field="search_results",
            value=len(results)
        )

    return results


def validate_company_name(
    name: Any,
    agent_name: str
) -> str:
    """
    Validate company name input.

    Args:
        name: Company name to validate
        agent_name: Agent name for error messages

    Returns:
        Validated company name

    Raises:
        ValidationError: If validation fails
    """
    if not name:
        raise ValidationError(
            "Company name cannot be empty",
            agent_name=agent_name,
            field="company_name",
            value=name
        )

    if not isinstance(name, str):
        raise ValidationError(
            f"Company name must be a string, got {type(name).__name__}",
            agent_name=agent_name,
            field="company_name",
            value=type(name).__name__
        )

    return name.strip()
