"""
Langfuse Integration - FREE LangSmith Alternative.

Full LLM observability with traces, metrics, and prompt management.
Free cloud tier (50K observations/month) or self-host for unlimited.

Features:
- Full trace logging
- Cost tracking
- Latency metrics
- Prompt management
- LangChain integration
- Model comparison
- User feedback
- FREE CLOUD TIER or SELF-HOST

Cost: $0 (free tier: 50K observations/month, self-host: unlimited)
Replaces: LangSmith ($39-100/mo)

Usage:
    from company_researcher.llm.langfuse_setup import get_langfuse, get_langchain_handler

    # Get Langfuse client
    langfuse = get_langfuse()

    # Create a trace
    trace = langfuse.trace(name="company_research", user_id="user123")

    # Get LangChain callback handler
    handler = get_langchain_handler()

    # Use with LangChain
    llm = ChatAnthropic(callbacks=[handler])
"""

from typing import Optional, Dict, Any, List
from threading import Lock
from dataclasses import dataclass
from ..utils import get_config, get_logger

logger = get_logger(__name__)


# Check if Langfuse is installed
LANGFUSE_AVAILABLE = False
try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    logger.info("Langfuse not installed. Run: pip install langfuse")
    Langfuse = None
    CallbackHandler = None


@dataclass
class LangfuseConfig:
    """Langfuse configuration."""
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    host: str = "https://cloud.langfuse.com"
    enabled: bool = True
    debug: bool = False
    release: Optional[str] = None


class LangfuseManager:
    """
    Langfuse integration manager.

    Provides centralized access to Langfuse observability.
    """

    def __init__(self, config: Optional[LangfuseConfig] = None):
        """
        Initialize Langfuse manager.

        Args:
            config: Langfuse configuration (uses env vars if not provided)
        """
        self.config = config or self._load_config_from_env()
        self._client: Optional["Langfuse"] = None
        self._handler: Optional["CallbackHandler"] = None
        self._lock = Lock()
        self._initialized = False

        # Stats tracking (fallback if Langfuse not configured)
        self._local_stats = {
            "traces": 0,
            "spans": 0,
            "generations": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

    def _load_config_from_env(self) -> LangfuseConfig:
        """Load configuration from environment variables."""
        return LangfuseConfig(
            public_key=get_config("LANGFUSE_PUBLIC_KEY"),
            secret_key=get_config("LANGFUSE_SECRET_KEY"),
            host=get_config("LANGFUSE_HOST", default="https://cloud.langfuse.com"),
            enabled=get_config("LANGFUSE_ENABLED", default="true").lower() == "true",
            debug=get_config("LANGFUSE_DEBUG", default="false").lower() == "true",
            release=get_config("LANGFUSE_RELEASE")
        )

    def _initialize(self) -> bool:
        """Initialize Langfuse client."""
        if self._initialized:
            return self._client is not None

        with self._lock:
            if self._initialized:
                return self._client is not None

            if not LANGFUSE_AVAILABLE:
                logger.warning("Langfuse not available. Install with: pip install langfuse")
                self._initialized = True
                return False

            if not self.config.enabled:
                logger.info("Langfuse disabled by configuration")
                self._initialized = True
                return False

            if not self.config.public_key or not self.config.secret_key:
                logger.info(
                    "Langfuse API keys not configured. "
                    "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
                )
                self._initialized = True
                return False

            try:
                self._client = Langfuse(
                    public_key=self.config.public_key,
                    secret_key=self.config.secret_key,
                    host=self.config.host,
                    debug=self.config.debug,
                    release=self.config.release
                )
                logger.info(f"Langfuse initialized: {self.config.host}")
                self._initialized = True
                return True

            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
                self._initialized = True
                return False

    @property
    def client(self) -> Optional["Langfuse"]:
        """Get Langfuse client."""
        self._initialize()
        return self._client

    @property
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and configured."""
        self._initialize()
        return self._client is not None

    def get_handler(
        self,
        trace_name: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional["CallbackHandler"]:
        """
        Get LangChain callback handler.

        Args:
            trace_name: Name for the trace
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional metadata
            tags: Tags for filtering

        Returns:
            CallbackHandler for LangChain or None if not configured
        """
        if not self.is_enabled or CallbackHandler is None:
            return None

        try:
            handler = CallbackHandler(
                public_key=self.config.public_key,
                secret_key=self.config.secret_key,
                host=self.config.host,
                trace_name=trace_name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
                tags=tags
            )
            return handler

        except Exception as e:
            logger.error(f"Failed to create Langfuse handler: {e}")
            return None

    def trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        input: Optional[Any] = None
    ):
        """
        Create a new trace.

        Args:
            name: Trace name
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional metadata
            tags: Tags for filtering
            input: Input data

        Returns:
            Trace object or None
        """
        if not self.is_enabled:
            self._local_stats["traces"] += 1
            return None

        try:
            trace = self._client.trace(
                name=name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
                tags=tags,
                input=input
            )
            self._local_stats["traces"] += 1
            return trace

        except Exception as e:
            logger.error(f"Failed to create trace: {e}")
            return None

    def log_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input: Any,
        output: Any,
        usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an LLM generation.

        Args:
            trace_id: Parent trace ID
            name: Generation name
            model: Model name
            input: Input prompt
            output: Model output
            usage: Token usage dict
            metadata: Additional metadata
        """
        if not self.is_enabled:
            if usage:
                self._local_stats["total_tokens"] += usage.get("total_tokens", 0)
            self._local_stats["generations"] += 1
            return

        try:
            self._client.generation(
                trace_id=trace_id,
                name=name,
                model=model,
                input=input,
                output=output,
                usage=usage,
                metadata=metadata
            )
            self._local_stats["generations"] += 1

        except Exception as e:
            logger.error(f"Failed to log generation: {e}")

    def log_span(
        self,
        trace_id: str,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a span within a trace.

        Args:
            trace_id: Parent trace ID
            name: Span name
            input: Span input
            output: Span output
            metadata: Additional metadata
        """
        if not self.is_enabled:
            self._local_stats["spans"] += 1
            return

        try:
            self._client.span(
                trace_id=trace_id,
                name=name,
                input=input,
                output=output,
                metadata=metadata
            )
            self._local_stats["spans"] += 1

        except Exception as e:
            logger.error(f"Failed to log span: {e}")

    def log_score(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None
    ):
        """
        Log a score for a trace.

        Args:
            trace_id: Trace ID to score
            name: Score name
            value: Score value (0-1)
            comment: Optional comment
        """
        if not self.is_enabled:
            return

        try:
            self._client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment
            )

        except Exception as e:
            logger.error(f"Failed to log score: {e}")

    def flush(self):
        """Flush any pending events."""
        if self._client:
            try:
                self._client.flush()
            except Exception as e:
                logger.error(f"Failed to flush Langfuse: {e}")

    def shutdown(self):
        """Shutdown Langfuse client."""
        if self._client:
            try:
                self._client.shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown Langfuse: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "enabled": self.is_enabled,
            "host": self.config.host if self.config else None,
            "local_stats": self._local_stats.copy(),
            "cost": 0.0  # FREE!
        }


# Singleton instance
_langfuse_manager: Optional[LangfuseManager] = None
_manager_lock = Lock()


def get_langfuse(config: Optional[LangfuseConfig] = None) -> LangfuseManager:
    """Get singleton Langfuse manager instance."""
    global _langfuse_manager
    if _langfuse_manager is None:
        with _manager_lock:
            if _langfuse_manager is None:
                _langfuse_manager = LangfuseManager(config)
    return _langfuse_manager


def reset_langfuse() -> None:
    """Reset Langfuse manager instance."""
    global _langfuse_manager
    if _langfuse_manager:
        _langfuse_manager.shutdown()
    _langfuse_manager = None


def get_langchain_handler(
    trace_name: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Optional["CallbackHandler"]:
    """
    Get LangChain callback handler for Langfuse.

    Args:
        trace_name: Name for the trace
        user_id: User identifier
        session_id: Session identifier

    Returns:
        CallbackHandler or None if not configured
    """
    manager = get_langfuse()
    return manager.get_handler(
        trace_name=trace_name,
        user_id=user_id,
        session_id=session_id
    )


# Convenience context manager
class LangfuseTrace:
    """Context manager for Langfuse tracing."""

    def __init__(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata
        self.trace = None
        self.manager = get_langfuse()

    def __enter__(self):
        self.trace = self.manager.trace(
            name=self.name,
            user_id=self.user_id,
            session_id=self.session_id,
            metadata=self.metadata
        )
        return self.trace

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.trace and exc_type:
            # Log error if exception occurred
            self.manager.log_span(
                trace_id=self.trace.id if hasattr(self.trace, 'id') else None,
                name="error",
                output={"error": str(exc_val), "type": exc_type.__name__}
            )
        self.manager.flush()
        return False


# Migration helper
def migrate_from_langsmith():
    """
    Instructions for migrating from LangSmith to Langfuse.

    Returns migration guide.
    """
    return """
    # Migration from LangSmith to Langfuse

    ## 1. Install Langfuse
    pip install langfuse

    ## 2. Update Environment Variables
    # Remove:
    LANGCHAIN_TRACING_V2=true
    LANGSMITH_API_KEY=xxx

    # Add:
    LANGFUSE_PUBLIC_KEY=pk-lf-xxx
    LANGFUSE_SECRET_KEY=sk-lf-xxx
    LANGFUSE_HOST=https://cloud.langfuse.com  # Or self-hosted URL

    ## 3. Update Code

    ### Before (LangSmith):
    from langchain.callbacks.tracers import LangChainTracer

    tracer = LangChainTracer(project_name="my-project")
    llm = ChatAnthropic(callbacks=[tracer])

    ### After (Langfuse):
    from company_researcher.llm.langfuse_setup import get_langchain_handler

    handler = get_langchain_handler(trace_name="my-project")
    llm = ChatAnthropic(callbacks=[handler])

    ## 4. Get API Keys
    - Free tier: https://cloud.langfuse.com (50K observations/month)
    - Self-host: https://github.com/langfuse/langfuse

    ## 5. Features Comparison
    | Feature | LangSmith | Langfuse |
    |---------|-----------|----------|
    | Tracing | Yes | Yes |
    | Prompts | Yes | Yes |
    | Datasets | Yes | Yes |
    | Scoring | Yes | Yes |
    | Cost tracking | Yes | Yes |
    | Self-host | No | Yes |
    | Free tier | Limited | 50K/month |
    | Price | $39/month+ | FREE |
    """
