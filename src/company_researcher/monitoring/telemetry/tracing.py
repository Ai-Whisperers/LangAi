"""
Tracing Module.

TracerProvider and Tracer for distributed tracing.
"""

import uuid
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from ...utils import get_logger, utc_now
from .exporters import SpanExporter
from .models import Span, SpanContext

logger = get_logger(__name__)


class TracerProvider:
    """
    OpenTelemetry-compatible tracer provider.

    Usage:
        provider = TracerProvider(service_name="company-researcher")
        tracer = provider.get_tracer("research")

        with tracer.start_span("fetch_company_data") as span:
            span.set_attribute("company", "Tesla")
            # do work
    """

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        exporters: List[SpanExporter] = None,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.exporters = exporters or []
        self._tracers: Dict[str, "Tracer"] = {}
        self._resource = {
            "service.name": service_name,
            "service.version": service_version,
            "telemetry.sdk.name": "company-researcher-otel",
            "telemetry.sdk.version": "1.0.0",
        }

    def get_tracer(self, name: str, version: str = "") -> "Tracer":
        """Get or create a tracer."""
        key = f"{name}:{version}"
        if key not in self._tracers:
            self._tracers[key] = Tracer(name, version, self)
        return self._tracers[key]

    def add_exporter(self, exporter: SpanExporter) -> None:
        """Add a span exporter."""
        self.exporters.append(exporter)

    def export_span(self, span: Span) -> None:
        """Export a completed span."""
        for exporter in self.exporters:
            try:
                exporter.export([span])
            except Exception as e:
                logger.error(f"Failed to export span: {e}")


class Tracer:
    """Creates spans for distributed tracing."""

    def __init__(self, name: str, version: str, provider: TracerProvider):
        self.name = name
        self.version = version
        self.provider = provider
        self._current_span: Optional[Span] = None

    @contextmanager
    def start_span(
        self,
        name: str,
        kind: str = "INTERNAL",
        attributes: Dict[str, Any] = None,
        links: List[SpanContext] = None,
    ) -> Iterator[Span]:
        """Start a new span as a context manager."""
        # Create span context
        context = SpanContext(
            trace_id=(
                self._current_span.context.trace_id if self._current_span else uuid.uuid4().hex
            ),
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=self._current_span.context.span_id if self._current_span else None,
        )

        span = Span(
            name=name,
            context=context,
            start_time=utc_now(),
            kind=kind,
            attributes=attributes or {},
            links=links or [],
        )

        # Set as current span
        previous_span = self._current_span
        self._current_span = span

        try:
            yield span
            span.set_status("OK")
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            span.end_time = utc_now()
            self._current_span = previous_span
            self.provider.export_span(span)

    def start_as_current_span(
        self, name: str, kind: str = "INTERNAL", attributes: Dict[str, Any] = None
    ) -> Span:
        """Start a span and set it as current (must be ended manually)."""
        context = SpanContext(
            trace_id=(
                self._current_span.context.trace_id if self._current_span else uuid.uuid4().hex
            ),
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=self._current_span.context.span_id if self._current_span else None,
        )

        span = Span(
            name=name, context=context, start_time=utc_now(), kind=kind, attributes=attributes or {}
        )

        self._current_span = span
        return span

    def get_current_span(self) -> Optional[Span]:
        """Get the current active span."""
        return self._current_span
