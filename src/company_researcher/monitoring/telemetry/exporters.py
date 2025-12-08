"""
Span Exporters Module.

Exporters for sending spans to various backends.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List

from .models import Span

logger = logging.getLogger(__name__)


class SpanExporter:
    """Base class for span exporters."""

    def export(self, spans: List[Span]) -> None:
        """Export spans to backend."""
        raise NotImplementedError

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass


class ConsoleSpanExporter(SpanExporter):
    """Exports spans to console for debugging."""

    def export(self, spans: List[Span]) -> None:
        """Print spans to console."""
        for span in spans:
            duration_ms = 0
            if span.end_time and span.start_time:
                duration_ms = (span.end_time - span.start_time).total_seconds() * 1000

            print(f"[SPAN] {span.name} ({span.kind})")
            print(f"  trace_id: {span.context.trace_id}")
            print(f"  span_id: {span.context.span_id}")
            print(f"  duration: {duration_ms:.2f}ms")
            print(f"  status: {span.status}")
            if span.attributes:
                print(f"  attributes: {span.attributes}")
            print()


class OTLPSpanExporter(SpanExporter):
    """
    Export spans to OTLP endpoint (Jaeger, Zipkin, etc.).

    Usage:
        exporter = OTLPSpanExporter(
            endpoint="http://localhost:4318/v1/traces"
        )
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:4318/v1/traces",
        headers: Dict[str, str] = None,
        timeout: float = 10.0
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self._batch: List[Span] = []
        self._batch_size = 100

    def export(self, spans: List[Span]) -> None:
        """Export spans to OTLP endpoint."""
        try:
            # Build OTLP payload
            payload = {
                "resourceSpans": [{
                    "resource": {
                        "attributes": []
                    },
                    "scopeSpans": [{
                        "scope": {"name": "company-researcher"},
                        "spans": [span.to_dict() for span in spans]
                    }]
                }]
            }

            request = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    **self.headers
                },
                method="POST"
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status >= 400:
                    logger.error(f"OTLP export failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to export to OTLP: {e}")


class InMemorySpanExporter(SpanExporter):
    """Stores spans in memory for testing."""

    def __init__(self):
        self.spans: List[Span] = []

    def export(self, spans: List[Span]) -> None:
        """Store spans in memory."""
        self.spans.extend(spans)

    def get_finished_spans(self) -> List[Span]:
        """Get all exported spans."""
        return self.spans.copy()

    def clear(self) -> None:
        """Clear stored spans."""
        self.spans.clear()
