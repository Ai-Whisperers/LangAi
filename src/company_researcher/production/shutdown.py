"""
Graceful Shutdown (Phase 20.4).

Handle shutdown gracefully:
- Signal handling
- Resource cleanup
- In-flight request handling
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import signal
import threading
import time
import logging
import atexit


# ============================================================================
# Enums and Data Models
# ============================================================================

class ShutdownPhase(str, Enum):
    """Shutdown phases."""
    RUNNING = "running"
    DRAINING = "draining"    # Stop accepting new requests
    TERMINATING = "terminating"  # Waiting for in-flight
    CLEANUP = "cleanup"      # Running cleanup handlers
    STOPPED = "stopped"


@dataclass
class ShutdownConfig:
    """Shutdown configuration."""
    drain_timeout: float = 10.0  # Seconds to wait for drain
    termination_timeout: float = 30.0  # Seconds to wait for in-flight
    cleanup_timeout: float = 5.0  # Seconds for cleanup handlers
    force_after: float = 60.0  # Force shutdown after total timeout


# ============================================================================
# Shutdown Handler
# ============================================================================

class ShutdownHandler:
    """
    Handle graceful shutdown.

    Features:
    - Signal handling (SIGTERM, SIGINT)
    - Cleanup callbacks
    - In-flight request tracking
    - Timeout handling

    Usage:
        handler = ShutdownHandler()

        # Register cleanup
        handler.on_shutdown(cleanup_database)
        handler.on_shutdown(close_connections)

        # Track in-flight work
        with handler.track_request():
            do_work()

        # Check if shutting down
        if handler.is_shutting_down:
            return "Service unavailable"
    """

    def __init__(
        self,
        config: Optional[ShutdownConfig] = None,
        install_signals: bool = True
    ):
        """
        Initialize shutdown handler.

        Args:
            config: Shutdown configuration
            install_signals: Install signal handlers
        """
        self._config = config or ShutdownConfig()
        self._phase = ShutdownPhase.RUNNING
        self._shutdown_requested = threading.Event()
        self._shutdown_complete = threading.Event()

        # In-flight tracking
        self._in_flight = 0
        self._in_flight_lock = threading.Lock()

        # Cleanup handlers
        self._cleanup_handlers: List[Callable] = []

        # Logger
        self._logger = logging.getLogger("shutdown")

        # Install signal handlers
        if install_signals:
            self._install_signal_handlers()

        # Register atexit
        atexit.register(self._atexit_handler)

    def _install_signal_handlers(self):
        """Install signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except (ValueError, OSError):
            # Can't install signals in some contexts (e.g., non-main thread)
            self._logger.warning("Could not install signal handlers")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signal."""
        self._logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown()

    def _atexit_handler(self):
        """Handle exit."""
        if self._phase == ShutdownPhase.RUNNING:
            self.shutdown()

    # ==========================================================================
    # Shutdown Process
    # ==========================================================================

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been requested."""
        return self._shutdown_requested.is_set()

    @property
    def phase(self) -> ShutdownPhase:
        """Get current shutdown phase."""
        return self._phase

    def shutdown(self, wait: bool = True, force: bool = False):
        """
        Initiate graceful shutdown.

        Args:
            wait: Wait for shutdown to complete
            force: Force immediate shutdown
        """
        if self._shutdown_requested.is_set():
            return

        self._shutdown_requested.set()
        self._logger.info("Initiating graceful shutdown")

        if force:
            self._phase = ShutdownPhase.STOPPED
            self._shutdown_complete.set()
            return

        # Run shutdown in background
        shutdown_thread = threading.Thread(
            target=self._shutdown_sequence,
            daemon=True
        )
        shutdown_thread.start()

        if wait:
            self._shutdown_complete.wait(timeout=self._config.force_after)

    def _shutdown_sequence(self):
        """Execute shutdown sequence."""
        start_time = time.time()

        # Phase 1: Draining
        self._phase = ShutdownPhase.DRAINING
        self._logger.info("Phase 1: Draining - Stop accepting new requests")
        time.sleep(min(self._config.drain_timeout, 2.0))

        # Phase 2: Terminating
        self._phase = ShutdownPhase.TERMINATING
        self._logger.info(f"Phase 2: Terminating - Waiting for {self._in_flight} in-flight requests")

        wait_start = time.time()
        while self._in_flight > 0:
            if time.time() - wait_start > self._config.termination_timeout:
                self._logger.warning(
                    f"Termination timeout - {self._in_flight} requests still in-flight"
                )
                break
            time.sleep(0.1)

        # Phase 3: Cleanup
        self._phase = ShutdownPhase.CLEANUP
        self._logger.info(f"Phase 3: Cleanup - Running {len(self._cleanup_handlers)} handlers")

        for handler in self._cleanup_handlers:
            try:
                elapsed = time.time() - start_time
                remaining = self._config.force_after - elapsed
                if remaining <= 0:
                    break

                handler()
            except Exception as e:
                self._logger.error(f"Cleanup handler error: {e}")

        # Complete
        self._phase = ShutdownPhase.STOPPED
        self._shutdown_complete.set()
        self._logger.info(f"Shutdown complete in {time.time() - start_time:.2f}s")

    # ==========================================================================
    # In-Flight Tracking
    # ==========================================================================

    def track_request(self):
        """
        Context manager for tracking in-flight requests.

        Usage:
            with handler.track_request():
                process_request()
        """
        return _RequestTracker(self)

    def increment_in_flight(self):
        """Increment in-flight counter."""
        with self._in_flight_lock:
            self._in_flight += 1

    def decrement_in_flight(self):
        """Decrement in-flight counter."""
        with self._in_flight_lock:
            self._in_flight = max(0, self._in_flight - 1)

    @property
    def in_flight_count(self) -> int:
        """Get current in-flight count."""
        return self._in_flight

    # ==========================================================================
    # Cleanup Registration
    # ==========================================================================

    def on_shutdown(self, handler: Callable, priority: int = 0):
        """
        Register a cleanup handler.

        Args:
            handler: Cleanup function
            priority: Higher priority runs first (default 0)
        """
        self._cleanup_handlers.append(handler)
        # Sort by priority (could be enhanced)

    def add_cleanup(self, handler: Callable):
        """Alias for on_shutdown."""
        self.on_shutdown(handler)

    # ==========================================================================
    # Status
    # ==========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get shutdown status."""
        return {
            "phase": self._phase.value,
            "is_shutting_down": self.is_shutting_down,
            "in_flight": self._in_flight,
            "cleanup_handlers": len(self._cleanup_handlers)
        }

    def wait_for_shutdown(self, timeout: Optional[float] = None):
        """Wait for shutdown to complete."""
        self._shutdown_complete.wait(timeout=timeout)


# ============================================================================
# Request Tracker Context Manager
# ============================================================================

class _RequestTracker:
    """Context manager for tracking requests."""

    def __init__(self, handler: ShutdownHandler):
        self._handler = handler

    def __enter__(self):
        self._handler.increment_in_flight()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._handler.decrement_in_flight()
        return False


# ============================================================================
# Graceful Shutdown Helper
# ============================================================================

class GracefulShutdown:
    """
    Simplified graceful shutdown context.

    Usage:
        with GracefulShutdown() as shutdown:
            run_server()

            if shutdown.is_requested:
                break
    """

    def __init__(
        self,
        drain_timeout: float = 10.0,
        termination_timeout: float = 30.0
    ):
        self._handler = ShutdownHandler(
            config=ShutdownConfig(
                drain_timeout=drain_timeout,
                termination_timeout=termination_timeout
            )
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._handler.is_shutting_down:
            self._handler.shutdown(wait=True)
        return False

    @property
    def is_requested(self) -> bool:
        """Check if shutdown requested."""
        return self._handler.is_shutting_down

    def request_shutdown(self):
        """Request shutdown."""
        self._handler.shutdown(wait=False)

    def on_shutdown(self, handler: Callable):
        """Register cleanup handler."""
        self._handler.on_shutdown(handler)


# ============================================================================
# Factory Functions
# ============================================================================

def create_shutdown_handler(
    drain_timeout: float = 10.0,
    termination_timeout: float = 30.0
) -> ShutdownHandler:
    """Create a shutdown handler instance."""
    return ShutdownHandler(
        config=ShutdownConfig(
            drain_timeout=drain_timeout,
            termination_timeout=termination_timeout
        )
    )


# ============================================================================
# Global Instance
# ============================================================================

_global_handler: Optional[ShutdownHandler] = None


def get_shutdown_handler() -> ShutdownHandler:
    """Get global shutdown handler."""
    global _global_handler
    if _global_handler is None:
        _global_handler = ShutdownHandler()
    return _global_handler
