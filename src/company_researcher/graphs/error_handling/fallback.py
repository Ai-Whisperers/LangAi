"""
Fallback Module - Phase 16

Provides fallback capabilities for graceful degradation.

Features:
- Primary/fallback node chaining
- Error boundary wrapping
- Default value providers
- Partial result handling

Usage:
    # Create node with fallback
    safe_search = with_fallback(
        tavily_search_node,
        duckduckgo_search_node
    )

    # Create error boundary
    bounded_node = create_error_boundary(
        risky_node,
        fallback_value={"status": "degraded"}
    )
"""

from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass, field
import functools

from ...state.workflow import OverallState
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""

    # Fallback chain
    fallback_nodes: List[Callable] = field(default_factory=list)

    # Error handling
    catch_exceptions: tuple = (Exception,)
    ignore_exceptions: tuple = ()

    # Default values
    default_value: Optional[Dict[str, Any]] = None

    # Logging
    log_fallbacks: bool = True

    # Partial results
    allow_partial_results: bool = True


def with_fallback(
    primary_node: Callable,
    fallback_node: Callable,
    config: Optional[FallbackConfig] = None,
) -> Callable:
    """
    Wrap a node with a fallback node.

    If the primary node fails, the fallback is executed.

    Args:
        primary_node: Primary node function
        fallback_node: Fallback node function
        config: Optional fallback configuration

    Returns:
        Wrapped function with fallback logic

    Usage:
        safe_search = with_fallback(
            primary_search_node,
            backup_search_node
        )
    """
    if config is None:
        config = FallbackConfig()

    @functools.wraps(primary_node)
    def wrapper(state: OverallState) -> Dict[str, Any]:
        try:
            result = primary_node(state)

            # Check if result indicates failure
            if _is_failed_result(result):
                raise RuntimeError("Primary node returned failed result")

            return result

        except config.ignore_exceptions:
            raise

        except config.catch_exceptions as e:
            if config.log_fallbacks:
                logger.warning(
                    f"[FALLBACK] {primary_node.__name__} failed: {e}. "
                    f"Falling back to {fallback_node.__name__}"
                )

            try:
                fallback_result = fallback_node(state)

                # Mark result as from fallback
                if isinstance(fallback_result, dict):
                    fallback_result["_fallback_used"] = True
                    fallback_result["_primary_error"] = str(e)

                return fallback_result

            except Exception as fallback_error:
                logger.error(
                    f"[FALLBACK] Both primary and fallback failed. "
                    f"Primary: {e}, Fallback: {fallback_error}"
                )

                if config.default_value is not None:
                    return {
                        **config.default_value,
                        "_fallback_used": True,
                        "_both_failed": True,
                        "_primary_error": str(e),
                        "_fallback_error": str(fallback_error),
                    }

                raise

    return wrapper


def with_fallback_chain(
    nodes: List[Callable],
    config: Optional[FallbackConfig] = None,
) -> Callable:
    """
    Create a node with multiple fallbacks.

    Tries each node in order until one succeeds.

    Args:
        nodes: List of node functions to try in order
        config: Optional fallback configuration

    Returns:
        Wrapped function with fallback chain

    Usage:
        search_chain = with_fallback_chain([
            tavily_search,
            serper_search,
            duckduckgo_search,
        ])
    """
    if not nodes:
        raise ValueError("At least one node required")

    if config is None:
        config = FallbackConfig()

    primary = nodes[0]

    @functools.wraps(primary)
    def wrapper(state: OverallState) -> Dict[str, Any]:
        errors = []

        for i, node in enumerate(nodes):
            try:
                result = node(state)

                if not _is_failed_result(result):
                    if i > 0 and config.log_fallbacks:
                        logger.info(
                            f"[FALLBACK] Succeeded with fallback #{i}: {node.__name__}"
                        )

                    if isinstance(result, dict):
                        result["_fallback_index"] = i

                    return result

            except config.ignore_exceptions:
                raise

            except config.catch_exceptions as e:
                errors.append((node.__name__, str(e)))

                if config.log_fallbacks:
                    logger.warning(
                        f"[FALLBACK] Node {i+1}/{len(nodes)} ({node.__name__}) failed: {e}"
                    )

        # All nodes failed
        logger.error(f"[FALLBACK] All {len(nodes)} nodes failed")

        if config.default_value is not None:
            return {
                **config.default_value,
                "_all_failed": True,
                "_errors": errors,
            }

        # Raise the last error
        raise RuntimeError(f"All fallback nodes failed: {errors}")

    return wrapper


def _is_failed_result(result: Any) -> bool:
    """Check if a result indicates failure."""
    if result is None:
        return True

    if isinstance(result, dict):
        # Check for error indicators
        if result.get("error"):
            return True
        if result.get("status") == "error":
            return True
        if result.get("_failed"):
            return True

    return False


# ============================================================================
# Error Boundary
# ============================================================================

def create_error_boundary(
    node: Callable,
    fallback_value: Optional[Dict[str, Any]] = None,
    catch_exceptions: tuple = (Exception,),
    error_handler: Optional[Callable[[Exception], Dict[str, Any]]] = None,
) -> Callable:
    """
    Create an error boundary around a node.

    The error boundary catches exceptions and returns a default value
    or calls an error handler, preventing the exception from propagating.

    Args:
        node: Node function to wrap
        fallback_value: Value to return on error
        catch_exceptions: Exceptions to catch
        error_handler: Optional function to handle errors

    Returns:
        Wrapped function with error boundary

    Usage:
        safe_node = create_error_boundary(
            risky_node,
            fallback_value={"status": "skipped", "reason": "node failed"}
        )
    """
    if fallback_value is None:
        fallback_value = {}

    @functools.wraps(node)
    def wrapper(state: OverallState) -> Dict[str, Any]:
        try:
            return node(state)

        except catch_exceptions as e:
            logger.error(f"[ERROR_BOUNDARY] {node.__name__} failed: {e}")

            if error_handler:
                return error_handler(e)

            return {
                **fallback_value,
                "_error_boundary_triggered": True,
                "_error": str(e),
                "_error_type": type(e).__name__,
            }

    return wrapper


def safe_node(
    default_value: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to make a node safe (catches all exceptions).

    Args:
        default_value: Value to return on error

    Returns:
        Decorator function

    Usage:
        @safe_node(default_value={"status": "skipped"})
        def my_node(state):
            ...
    """
    def decorator(func: Callable) -> Callable:
        return create_error_boundary(func, fallback_value=default_value)

    return decorator


# ============================================================================
# Partial Result Handling
# ============================================================================

def with_partial_results(
    node: Callable,
    required_fields: Optional[List[str]] = None,
) -> Callable:
    """
    Wrap a node to handle partial results gracefully.

    If some fields fail to extract, the node still returns
    successful fields and marks failed fields.

    Args:
        node: Node function to wrap
        required_fields: Fields that must be present

    Returns:
        Wrapped function with partial result handling

    Usage:
        @with_partial_results(required_fields=["company_name"])
        def extraction_node(state):
            ...
    """
    @functools.wraps(node)
    def wrapper(state: OverallState) -> Dict[str, Any]:
        try:
            result = node(state)

            # Check required fields
            if required_fields:
                missing = [f for f in required_fields if f not in result or result[f] is None]
                if missing:
                    result["_partial_result"] = True
                    result["_missing_required_fields"] = missing
                    logger.warning(
                        f"[PARTIAL] {node.__name__} missing required fields: {missing}"
                    )

            return result

        except Exception as e:
            logger.error(f"[PARTIAL] {node.__name__} failed: {e}")

            # Return minimal partial result
            return {
                "_partial_result": True,
                "_failed": True,
                "_error": str(e),
            }

    return wrapper


# ============================================================================
# Graceful Degradation
# ============================================================================

class GracefulDegradation:
    """
    Context manager for graceful degradation.

    Tracks which components are degraded and provides
    summary information.

    Usage:
        with GracefulDegradation() as gd:
            try:
                gd.try_component("search", search_node, state)
            except Exception:
                gd.degrade("search", "search failed")

            if gd.is_degraded:
                print(f"Running in degraded mode: {gd.degraded_components}")
    """

    def __init__(self):
        self.degraded_components: Dict[str, str] = {}
        self.successful_components: List[str] = []
        self.results: Dict[str, Any] = {}

    def __enter__(self) -> "GracefulDegradation":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.degraded_components:
            logger.warning(
                f"[DEGRADED] {len(self.degraded_components)} components degraded: "
                f"{list(self.degraded_components.keys())}"
            )
        return False

    def try_component(
        self,
        name: str,
        component: Callable,
        state: OverallState,
        fallback_value: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Try to execute a component, degrade on failure."""
        try:
            result = component(state)
            self.successful_components.append(name)
            self.results[name] = result
            return result

        except Exception as e:
            self.degrade(name, str(e))

            if fallback_value is not None:
                self.results[name] = fallback_value
                return fallback_value

            return {}

    def degrade(self, component: str, reason: str) -> None:
        """Mark a component as degraded."""
        self.degraded_components[component] = reason
        logger.warning(f"[DEGRADED] Component {component}: {reason}")

    @property
    def is_degraded(self) -> bool:
        """Check if any components are degraded."""
        return len(self.degraded_components) > 0

    def get_summary(self) -> Dict[str, Any]:
        """Get degradation summary."""
        return {
            "is_degraded": self.is_degraded,
            "degraded_count": len(self.degraded_components),
            "degraded_components": self.degraded_components,
            "successful_components": self.successful_components,
        }
