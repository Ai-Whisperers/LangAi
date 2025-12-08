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

from .circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    create_circuit_breaker,
)

from .retry import (
    RetryPolicy,
    RetryConfig,
    retry,
    retry_async,
    create_retry_policy,
)

from .health import (
    HealthChecker,
    HealthStatus,
    HealthCheck,
    create_health_checker,
    run_health_checks,
)

from .shutdown import (
    GracefulShutdown,
    ShutdownHandler,
    create_shutdown_handler,
)

from .config import (
    ProductionConfig,
    load_config,
    get_config,
    validate_config,
)

from .service_registry import (
    ServiceRegistry,
    ServiceInstance,
    ServiceStatus,
    ServiceClient,
    LoadBalanceStrategy,
    create_service_registry,
)

from .log_aggregation import (
    LogAggregator,
    LogEntry,
    LogLevel,
    LogShipper,
    AsyncLogShipper,
    FileShipper,
    HTTPShipper,
    ElasticsearchShipper,
    StructuredFormatter,
    create_log_aggregator,
    setup_structured_logging,
)

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
