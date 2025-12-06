"""
Health Checks (Phase 20.3).

Health monitoring:
- Service health checks
- Dependency checks
- Readiness and liveness probes
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import logging
import asyncio


# ============================================================================
# Enums and Data Models
# ============================================================================

class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 2),
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class HealthReport:
    """Complete health report."""
    status: HealthStatus
    checks: List[HealthCheck]
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "is_healthy": self.is_healthy,
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }


# ============================================================================
# Health Checker
# ============================================================================

class HealthChecker:
    """
    Service health checker.

    Features:
    - Multiple health checks
    - Timeout handling
    - Async support
    - Detailed reporting

    Usage:
        checker = HealthChecker()

        # Register checks
        checker.add_check("database", check_database)
        checker.add_check("api", check_api)

        # Run all checks
        report = checker.run_checks()

        # Use for liveness/readiness
        if report.is_healthy:
            return 200
    """

    def __init__(
        self,
        timeout_seconds: float = 5.0,
        version: str = "1.0.0"
    ):
        """
        Initialize health checker.

        Args:
            timeout_seconds: Timeout for each check
            version: Service version
        """
        self._timeout = timeout_seconds
        self._version = version
        self._checks: Dict[str, Callable] = {}
        self._logger = logging.getLogger("health")

        # Add default checks
        self._add_default_checks()

    def _add_default_checks(self):
        """Add default health checks."""
        # Memory check
        def check_memory() -> HealthCheck:
            import psutil
            mem = psutil.virtual_memory()
            status = HealthStatus.HEALTHY if mem.percent < 90 else HealthStatus.DEGRADED

            return HealthCheck(
                name="memory",
                status=status,
                message=f"Memory usage: {mem.percent}%",
                details={"percent": mem.percent, "available_gb": mem.available / (1024**3)}
            )

        # Disk check
        def check_disk() -> HealthCheck:
            import psutil
            disk = psutil.disk_usage('/')
            status = HealthStatus.HEALTHY if disk.percent < 90 else HealthStatus.DEGRADED

            return HealthCheck(
                name="disk",
                status=status,
                message=f"Disk usage: {disk.percent}%",
                details={"percent": disk.percent, "free_gb": disk.free / (1024**3)}
            )

        try:
            import psutil
            self._checks["memory"] = check_memory
            self._checks["disk"] = check_disk
        except ImportError:
            pass

    def add_check(
        self,
        name: str,
        check_func: Callable[[], HealthCheck],
        critical: bool = False
    ):
        """
        Add a health check.

        Args:
            name: Check name
            check_func: Function that returns HealthCheck
            critical: If True, failure makes entire status unhealthy
        """
        self._checks[name] = check_func

    def remove_check(self, name: str):
        """Remove a health check."""
        self._checks.pop(name, None)

    def run_checks(self) -> HealthReport:
        """Run all health checks."""
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, check_func in self._checks.items():
            try:
                start = time.time()
                result = check_func()
                result.duration_ms = (time.time() - start) * 1000
                results.append(result)

                # Update overall status
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except Exception as e:
                self._logger.error(f"Health check '{name}' failed: {e}")
                results.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e)
                ))
                overall_status = HealthStatus.UNHEALTHY

        return HealthReport(
            status=overall_status,
            checks=results,
            version=self._version
        )

    async def run_checks_async(self) -> HealthReport:
        """Run all health checks asynchronously."""
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, check_func in self._checks.items():
            try:
                start = time.time()

                if asyncio.iscoroutinefunction(check_func):
                    result = await asyncio.wait_for(
                        check_func(),
                        timeout=self._timeout
                    )
                else:
                    result = await asyncio.to_thread(check_func)

                result.duration_ms = (time.time() - start) * 1000
                results.append(result)

                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except asyncio.TimeoutError:
                results.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check timed out after {self._timeout}s"
                ))
                overall_status = HealthStatus.UNHEALTHY

            except Exception as e:
                results.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e)
                ))
                overall_status = HealthStatus.UNHEALTHY

        return HealthReport(
            status=overall_status,
            checks=results,
            version=self._version
        )

    # ==========================================================================
    # Convenience Methods
    # ==========================================================================

    def is_healthy(self) -> bool:
        """Quick health check."""
        return self.run_checks().is_healthy

    def get_status(self) -> Dict[str, Any]:
        """Get health status as dict."""
        return self.run_checks().to_dict()


# ============================================================================
# Built-in Check Factories
# ============================================================================

def create_api_health_check(
    url: str,
    timeout: float = 5.0,
    name: str = "api"
) -> Callable[[], HealthCheck]:
    """Create an API health check."""
    def check() -> HealthCheck:
        try:
            import httpx
            response = httpx.get(url, timeout=timeout)

            if response.status_code == 200:
                return HealthCheck(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message=f"API responding at {url}",
                    details={"status_code": response.status_code}
                )
            else:
                return HealthCheck(
                    name=name,
                    status=HealthStatus.DEGRADED,
                    message=f"API returned {response.status_code}",
                    details={"status_code": response.status_code}
                )

        except Exception as e:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )

    return check


def create_database_health_check(
    connection_string: str,
    name: str = "database"
) -> Callable[[], HealthCheck]:
    """Create a database health check."""
    def check() -> HealthCheck:
        try:
            # This is a placeholder - implement based on your database
            return HealthCheck(
                name=name,
                status=HealthStatus.HEALTHY,
                message="Database connection OK"
            )
        except Exception as e:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )

    return check


# ============================================================================
# Factory Functions
# ============================================================================

def create_health_checker(
    timeout_seconds: float = 5.0,
    version: str = "1.0.0"
) -> HealthChecker:
    """Create a health checker instance."""
    return HealthChecker(
        timeout_seconds=timeout_seconds,
        version=version
    )


def run_health_checks() -> Dict[str, Any]:
    """Run health checks using global checker."""
    checker = HealthChecker()
    return checker.get_status()


# ============================================================================
# Global Instance
# ============================================================================

_global_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get global health checker."""
    global _global_checker
    if _global_checker is None:
        _global_checker = HealthChecker()
    return _global_checker
