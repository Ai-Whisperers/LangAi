"""
Production Hardening Module (Phase 20).

Production-ready utilities:
- Configuration management
- Circuit breakers
- Retry mechanisms
- Health checks
- Graceful shutdown
- Error handling

Usage:
    from src.company_researcher.production import (
        CircuitBreaker,
        RetryPolicy,
        HealthChecker,
        GracefulShutdown,
        ProductionConfig
    )

    # Use circuit breaker
    breaker = CircuitBreaker(failure_threshold=5)

    @breaker
    def call_external_api():
        ...

    # Use retry policy
    @retry(max_attempts=3, backoff=2.0)
    def flaky_operation():
        ...
"""

from .circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState, create_circuit_breaker
from .config import ProductionConfig, get_config, load_config, validate_config
from .health import (
    HealthCheck,
    HealthChecker,
    HealthStatus,
    create_health_checker,
    run_health_checks,
)
from .log_aggregation import (
    AsyncLogShipper,
    ElasticsearchShipper,
    FileShipper,
    HTTPShipper,
    LogAggregator,
    LogEntry,
    LogLevel,
    LogShipper,
    StructuredFormatter,
    create_log_aggregator,
    setup_structured_logging,
)
from .retry import RetryConfig, RetryPolicy, create_retry_policy, retry, retry_async
from .service_registry import (
    LoadBalanceStrategy,
    ServiceClient,
    ServiceInstance,
    ServiceRegistry,
    ServiceStatus,
    create_service_registry,
)
from .shutdown import GracefulShutdown, ShutdownHandler, create_shutdown_handler

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "CircuitOpenError",
    "create_circuit_breaker",
    # Retry
    "RetryPolicy",
    "RetryConfig",
    "retry",
    "retry_async",
    "create_retry_policy",
    # Health
    "HealthChecker",
    "HealthStatus",
    "HealthCheck",
    "create_health_checker",
    "run_health_checks",
    # Shutdown
    "GracefulShutdown",
    "ShutdownHandler",
    "create_shutdown_handler",
    # Config
    "ProductionConfig",
    "load_config",
    "get_config",
    "validate_config",
    # Service Registry
    "ServiceRegistry",
    "ServiceInstance",
    "ServiceStatus",
    "ServiceClient",
    "LoadBalanceStrategy",
    "create_service_registry",
    # Log Aggregation
    "LogAggregator",
    "LogEntry",
    "LogLevel",
    "LogShipper",
    "AsyncLogShipper",
    "FileShipper",
    "HTTPShipper",
    "ElasticsearchShipper",
    "StructuredFormatter",
    "create_log_aggregator",
    "setup_structured_logging",
]
