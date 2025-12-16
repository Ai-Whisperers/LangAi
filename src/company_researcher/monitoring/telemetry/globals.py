"""
Global Telemetry Instances Module.

Global instances and factory functions for telemetry.
"""

from typing import Dict, Optional

from .exporters import ConsoleSpanExporter, OTLPSpanExporter
from .metrics import Meter, MeterProvider
from .tracing import Tracer, TracerProvider

# Global instances for convenience
_global_tracer_provider: Optional[TracerProvider] = None
_global_meter_provider: Optional[MeterProvider] = None


def set_tracer_provider(provider: TracerProvider) -> None:
    """Set the global tracer provider."""
    global _global_tracer_provider
    _global_tracer_provider = provider


def get_tracer_provider() -> TracerProvider:
    """Get the global tracer provider."""
    global _global_tracer_provider
    if _global_tracer_provider is None:
        _global_tracer_provider = TracerProvider("default")
    return _global_tracer_provider


def get_tracer(name: str) -> Tracer:
    """Get a tracer from the global provider."""
    return get_tracer_provider().get_tracer(name)


def set_meter_provider(provider: MeterProvider) -> None:
    """Set the global meter provider."""
    global _global_meter_provider
    _global_meter_provider = provider


def get_meter_provider() -> MeterProvider:
    """Get the global meter provider."""
    global _global_meter_provider
    if _global_meter_provider is None:
        _global_meter_provider = MeterProvider()
    return _global_meter_provider


def get_meter(name: str) -> Meter:
    """Get a meter from the global provider."""
    return get_meter_provider().get_meter(name)


# Factory functions


def create_tracer_provider(
    service_name: str, otlp_endpoint: str = None, console_export: bool = False
) -> TracerProvider:
    """
    Create a configured tracer provider.

    Args:
        service_name: Name of the service
        otlp_endpoint: OTLP collector endpoint
        console_export: Whether to export to console

    Returns:
        Configured TracerProvider
    """
    exporters = []

    if otlp_endpoint:
        exporters.append(OTLPSpanExporter(endpoint=otlp_endpoint))

    if console_export:
        exporters.append(ConsoleSpanExporter())

    return TracerProvider(service_name=service_name, exporters=exporters)


def create_meter_provider(resource: Dict[str, str] = None) -> MeterProvider:
    """
    Create a configured meter provider.

    Args:
        resource: Resource attributes

    Returns:
        Configured MeterProvider
    """
    return MeterProvider(resource=resource)
