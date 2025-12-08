"""
Tests for agents.base.logger module.

Tests the centralized logging system for agents.
"""

import pytest
import logging
from io import StringIO

from src.company_researcher.agents.base.logger import (
    AgentLogger,
    AgentLogContext,
    get_agent_logger,
    configure_agent_logging,
)


class TestAgentLogger:
    """Tests for AgentLogger class."""

    def test_logger_creation(self):
        """Test creating an agent logger."""
        logger = AgentLogger("test_agent")
        assert logger.agent_name == "test_agent"
        assert logger.show_separator is True

    def test_logger_with_custom_settings(self):
        """Test logger with custom settings."""
        logger = AgentLogger(
            "custom_agent",
            log_level=logging.DEBUG,
            show_separator=False
        )
        assert logger.agent_name == "custom_agent"
        assert logger.show_separator is False

    def test_agent_run_context_manager(self):
        """Test agent_run context manager."""
        logger = AgentLogger("financial", show_separator=False)

        with logger.agent_run("Tesla", extra_info="test") as ctx:
            assert isinstance(ctx, AgentLogContext)
            assert ctx.agent_name == "financial"
            assert ctx.company_name == "Tesla"
            assert ctx.metadata.get("extra_info") == "test"
            assert ctx.start_time is not None

    def test_log_methods(self, caplog):
        """Test various log methods."""
        logger = AgentLogger("market", show_separator=False)

        with caplog.at_level(logging.INFO):
            logger.info("Test info message")
            logger.warning("Test warning")

        assert "Test info message" in caplog.text
        assert "WARNING" in caplog.text

    def test_analyzing_log(self, caplog):
        """Test analyzing log message."""
        logger = AgentLogger("product", show_separator=False)

        with caplog.at_level(logging.INFO):
            logger.analyzing(15, "sources")

        assert "Analyzing 15 sources" in caplog.text

    def test_complete_log(self, caplog):
        """Test complete log message."""
        logger = AgentLogger("financial", show_separator=False)

        with caplog.at_level(logging.INFO):
            logger.complete(cost=0.0523)

        assert "Analysis complete" in caplog.text
        assert "$0.0523" in caplog.text


class TestGetAgentLogger:
    """Tests for get_agent_logger function."""

    def test_get_logger(self):
        """Test getting a logger."""
        logger = get_agent_logger("test_agent_1")
        assert isinstance(logger, AgentLogger)
        assert logger.agent_name == "test_agent_1"

    def test_get_same_logger_twice(self):
        """Test that same logger is returned for same name."""
        logger1 = get_agent_logger("shared_agent")
        logger2 = get_agent_logger("shared_agent")
        assert logger1 is logger2

    def test_different_loggers(self):
        """Test that different names get different loggers."""
        logger1 = get_agent_logger("agent_a")
        logger2 = get_agent_logger("agent_b")
        assert logger1 is not logger2


class TestConfigureAgentLogging:
    """Tests for configure_agent_logging function."""

    def test_configure_level(self):
        """Test configuring log level."""
        # This test just ensures the function runs without error
        configure_agent_logging(level=logging.WARNING)
        # Reset to INFO
        configure_agent_logging(level=logging.INFO)

    def test_configure_separators(self):
        """Test configuring separator display."""
        configure_agent_logging(show_separators=False)
        # Get a fresh logger to check
        logger = AgentLogger("config_test", show_separator=True)
        # The configure function updates existing loggers, not new ones
        configure_agent_logging(show_separators=True)
