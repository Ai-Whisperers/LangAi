"""
Agent Logger - Centralized logging for all agents.

Replaces 444 print statements with proper structured logging.
Provides consistent formatting and log levels.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class AgentLogContext:
    """Context for agent logging."""
    agent_name: str
    company_name: str
    start_time: datetime
    metadata: Dict[str, Any]


class AgentLogger:
    """
    Structured logger for agent operations.

    Provides consistent logging across all agents, replacing
    print statements with proper log levels and formatting.

    Usage:
        logger = AgentLogger("financial")
        with logger.agent_run("Tesla") as ctx:
            logger.info("Analyzing financial data")
            # ... agent work ...
            logger.complete(cost=0.0123)
    """

    # Class-level configuration
    SEPARATOR = "=" * 60
    LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        agent_name: str,
        logger: Optional[logging.Logger] = None,
        log_level: int = logging.INFO,
        show_separator: bool = True
    ):
        """
        Initialize agent logger.

        Args:
            agent_name: Name of the agent (e.g., "financial", "market")
            logger: Optional existing logger to use
            log_level: Logging level (default INFO)
            show_separator: Whether to show separators (default True)
        """
        self.agent_name = agent_name
        self.show_separator = show_separator
        self._context: Optional[AgentLogContext] = None

        # Set up logger
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(f"company_researcher.agents.{agent_name}")
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
                self._logger.addHandler(handler)
            self._logger.setLevel(log_level)

    @contextmanager
    def agent_run(self, company_name: str, **metadata):
        """
        Context manager for an agent run.

        Args:
            company_name: Name of the company being analyzed
            **metadata: Additional context metadata

        Yields:
            AgentLogContext for the run
        """
        self._context = AgentLogContext(
            agent_name=self.agent_name,
            company_name=company_name,
            start_time=datetime.now(),
            metadata=metadata
        )

        try:
            self.start()
            yield self._context
        finally:
            self._context = None

    def start(self, message: Optional[str] = None):
        """Log the start of agent execution."""
        if self.show_separator:
            self._logger.info("")
            self._logger.info(self.SEPARATOR)

        default_msg = f"Starting analysis..."
        if self._context:
            default_msg = f"Analyzing {self._context.company_name}..."

        self._logger.info(f"[AGENT: {self.agent_name.title()}] {message or default_msg}")

        if self.show_separator:
            self._logger.info(self.SEPARATOR)

    def info(self, message: str, **kwargs):
        """Log an info message."""
        self._logger.info(f"[{self.agent_name.title()}] {message}", **kwargs)

    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self._logger.debug(f"[{self.agent_name.title()}] {message}", **kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self._logger.warning(f"[{self.agent_name.title()}] WARNING: {message}", **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log an error message."""
        self._logger.error(f"[{self.agent_name.title()}] ERROR: {message}", exc_info=exc_info, **kwargs)

    def complete(self, cost: float = 0.0, message: str = "Analysis complete"):
        """Log successful completion of agent."""
        self._logger.info(f"[{self.agent_name.title()}] {message}")
        self._logger.info(f"[{self.agent_name.title()}] Agent complete - ${cost:.4f}")

        if self.show_separator:
            self._logger.info(self.SEPARATOR)

    def no_data(self, message: str = "No search results to analyze"):
        """Log when no data is available."""
        self.warning(message)

    def analyzing(self, source_count: int, data_type: str = "sources"):
        """Log analysis start with source count."""
        self.info(f"Analyzing {source_count} {data_type}...")

    def progress(self, current: int, total: int, message: str = "Processing"):
        """Log progress through items."""
        percent = (current / total * 100) if total > 0 else 0
        self._logger.debug(f"[{self.agent_name.title()}] {message}: {current}/{total} ({percent:.0f}%)")


# Module-level loggers for convenience
_agent_loggers: Dict[str, AgentLogger] = {}


def get_agent_logger(agent_name: str, **kwargs) -> AgentLogger:
    """
    Get or create an agent logger.

    Args:
        agent_name: Name of the agent
        **kwargs: Additional arguments for AgentLogger

    Returns:
        AgentLogger instance
    """
    if agent_name not in _agent_loggers:
        _agent_loggers[agent_name] = AgentLogger(agent_name, **kwargs)
    return _agent_loggers[agent_name]


def configure_agent_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    show_separators: bool = True
):
    """
    Configure logging for all agents.

    Args:
        level: Log level for agent loggers
        format_string: Custom format string
        show_separators: Whether to show separators
    """
    logging.getLogger("company_researcher.agents").setLevel(level)

    if format_string:
        AgentLogger.LOG_FORMAT = format_string

    # Update existing loggers
    for logger in _agent_loggers.values():
        logger._logger.setLevel(level)
        logger.show_separator = show_separators
