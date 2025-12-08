"""
Telemetry Decorators Module.

Decorators for tracing and metrics.
"""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, TypeVar

from .tracing import Tracer
from .metrics import Meter

# Type for generic function
F = TypeVar('F', bound=Callable[..., Any])


def trace(
    tracer: Tracer,
    name: str = None,
    kind: str = "INTERNAL",
    attributes: Dict[str, Any] = None
) -> Callable[[F], F]:
    """
    Decorator to trace a function.

    Usage:
        @trace(tracer, "fetch_data")
        def fetch_company_data(company: str):
            ...
    """
    def decorator(func: F) -> F:
        span_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_span(span_name, kind=kind, attributes=attributes) as span:
                span.set_attribute("function", func.__name__)
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_span(span_name, kind=kind, attributes=attributes) as span:
                span.set_attribute("function", func.__name__)
                return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore

    return decorator


def timed(
    meter: Meter,
    metric_name: str,
    attributes: Dict[str, str] = None
) -> Callable[[F], F]:
    """
    Decorator to time function execution.

    Usage:
        @timed(meter, "research_duration")
        def do_research(company: str):
            ...
    """
    histogram = meter.create_histogram(metric_name, "Function execution time", "ms")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration_ms = (time.time() - start) * 1000
                histogram.record(duration_ms, attributes)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration_ms = (time.time() - start) * 1000
                histogram.record(duration_ms, attributes)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore

    return decorator


def counted(
    meter: Meter,
    metric_name: str,
    attributes: Dict[str, str] = None
) -> Callable[[F], F]:
    """
    Decorator to count function calls.

    Usage:
        @counted(meter, "research_calls")
        def do_research(company: str):
            ...
    """
    counter = meter.create_counter(metric_name, "Function call count", "1")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            counter.add(1, attributes)
            return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            counter.add(1, attributes)
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore

    return decorator
