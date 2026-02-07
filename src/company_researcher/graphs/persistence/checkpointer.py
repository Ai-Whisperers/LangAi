"""
Checkpointer Configuration - Phase 12

Provides LangGraph checkpointer setup for workflow persistence.

Supported backends:
- SQLite (default, for development)
- PostgreSQL (for production)
- In-memory (for testing)

Usage:
    from company_researcher.graphs.persistence import get_checkpointer

    # Get default SQLite checkpointer
    checkpointer = get_checkpointer()

    # Get PostgreSQL checkpointer for production
    checkpointer = get_checkpointer(
        backend="postgres",
        connection_string=os.getenv("DATABASE_URL")
    )

    # Create checkpointed workflow
    workflow = create_checkpointed_workflow(
        create_research_workflow(),
        checkpointer
    )
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from ...utils import get_logger

logger = get_logger(__name__)

# Type alias for checkpointer backends
CheckpointerBackend = Literal["sqlite", "postgres", "memory"]


@dataclass
class CheckpointerConfig:
    """Configuration for checkpointer."""

    # Backend selection
    backend: CheckpointerBackend = "sqlite"

    # SQLite settings
    sqlite_path: str = "data/checkpoints.db"

    # PostgreSQL settings
    postgres_url: Optional[str] = None

    # Connection pool settings (PostgreSQL)
    pool_size: int = 5
    max_overflow: int = 10

    # Checkpoint retention
    max_checkpoints_per_thread: int = 100
    auto_cleanup: bool = True


def get_checkpointer(
    backend: CheckpointerBackend = "sqlite",
    connection_string: Optional[str] = None,
    config: Optional[CheckpointerConfig] = None,
) -> Any:
    """
    Get a checkpointer instance for workflow persistence.

    Args:
        backend: Checkpointer backend ("sqlite", "postgres", "memory")
        connection_string: Database connection string (optional)
        config: Full configuration object (overrides other args)

    Returns:
        Configured checkpointer instance
    """
    if config:
        backend = config.backend
        if backend == "postgres":
            connection_string = config.postgres_url
        elif backend == "sqlite":
            connection_string = config.sqlite_path

    logger.info(f"[CHECKPOINT] Initializing {backend} checkpointer")

    if backend == "memory":
        return get_memory_checkpointer()

    elif backend == "sqlite":
        return _get_sqlite_checkpointer(connection_string)

    elif backend == "postgres":
        return _get_postgres_checkpointer(connection_string)

    else:
        raise ValueError(f"Unknown checkpointer backend: {backend}")


def get_memory_checkpointer() -> MemorySaver:
    """
    Get an in-memory checkpointer for testing.

    Note: Data is lost when process exits.

    Returns:
        MemorySaver instance
    """
    logger.info("[CHECKPOINT] Using in-memory checkpointer (data not persisted)")
    return MemorySaver()


def _get_sqlite_checkpointer(db_path: Optional[str] = None) -> Any:
    """
    Get a SQLite checkpointer.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SqliteSaver instance
    """
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        logger.warning(
            "[CHECKPOINT] langgraph.checkpoint.sqlite not available, "
            "falling back to memory checkpointer"
        )
        return get_memory_checkpointer()

    if db_path is None:
        db_path = "data/checkpoints.db"

    # Ensure directory exists
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[CHECKPOINT] SQLite database: {db_path}")

    try:
        checkpointer = SqliteSaver.from_conn_string(db_path)
        return checkpointer
    except Exception as e:
        logger.error(f"[CHECKPOINT] Failed to create SQLite checkpointer: {e}")
        logger.warning("[CHECKPOINT] Falling back to memory checkpointer")
        return get_memory_checkpointer()


def _get_postgres_checkpointer(connection_string: Optional[str] = None) -> Any:
    """
    Get a PostgreSQL checkpointer.

    Args:
        connection_string: PostgreSQL connection URL

    Returns:
        PostgresSaver instance
    """
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
    except ImportError:
        logger.warning(
            "[CHECKPOINT] langgraph.checkpoint.postgres not available, " "falling back to SQLite"
        )
        return _get_sqlite_checkpointer()

    if connection_string is None:
        connection_string = os.getenv("DATABASE_URL")

    if not connection_string:
        logger.warning(
            "[CHECKPOINT] No PostgreSQL connection string provided, " "falling back to SQLite"
        )
        return _get_sqlite_checkpointer()

    logger.info("[CHECKPOINT] Using PostgreSQL checkpointer")

    try:
        checkpointer = PostgresSaver.from_conn_string(connection_string)
        return checkpointer
    except Exception as e:
        logger.error(f"[CHECKPOINT] Failed to create PostgreSQL checkpointer: {e}")
        logger.warning("[CHECKPOINT] Falling back to SQLite")
        return _get_sqlite_checkpointer()


def create_checkpointed_workflow(
    workflow: StateGraph,
    checkpointer: Optional[Any] = None,
    interrupt_before: Optional[list] = None,
    interrupt_after: Optional[list] = None,
) -> StateGraph:
    """
    Compile a workflow with checkpointing enabled.

    Args:
        workflow: Uncompiled StateGraph workflow
        checkpointer: Checkpointer instance (creates default if None)
        interrupt_before: List of node names to interrupt before
        interrupt_after: List of node names to interrupt after

    Returns:
        Compiled StateGraph with checkpointing
    """
    if checkpointer is None:
        checkpointer = get_checkpointer()

    compile_kwargs = {
        "checkpointer": checkpointer,
    }

    if interrupt_before:
        compile_kwargs["interrupt_before"] = interrupt_before

    if interrupt_after:
        compile_kwargs["interrupt_after"] = interrupt_after

    logger.info("[CHECKPOINT] Compiling workflow with checkpointing")

    return workflow.compile(**compile_kwargs)


# ============================================================================
# Async Checkpointer Support
# ============================================================================


async def get_async_checkpointer(
    backend: CheckpointerBackend = "sqlite",
    connection_string: Optional[str] = None,
) -> Any:
    """
    Get an async checkpointer for async workflow execution.

    Args:
        backend: Checkpointer backend
        connection_string: Database connection string

    Returns:
        Async checkpointer instance
    """
    if backend == "memory":
        return get_memory_checkpointer()

    elif backend == "sqlite":
        try:
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

            if connection_string is None:
                connection_string = "data/checkpoints.db"

            # Ensure directory exists
            db_dir = Path(connection_string).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            return AsyncSqliteSaver.from_conn_string(connection_string)
        except ImportError:
            logger.warning("[CHECKPOINT] Async SQLite not available")
            return get_memory_checkpointer()

    elif backend == "postgres":
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            if connection_string is None:
                connection_string = os.getenv("DATABASE_URL")

            if not connection_string:
                raise ValueError("PostgreSQL connection string required")

            return AsyncPostgresSaver.from_conn_string(connection_string)
        except ImportError:
            logger.warning("[CHECKPOINT] Async PostgreSQL not available")
            return get_memory_checkpointer()

    return get_memory_checkpointer()
