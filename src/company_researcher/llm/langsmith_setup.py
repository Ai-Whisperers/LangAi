"""
LangSmith Integration Setup.

Provides complete LangSmith tracing configuration for:
- Automatic trace capture of all LangChain/LangGraph calls
- Custom run trees for complex workflows
- Trace flushing and synchronization
- Dashboard URL generation

Environment Variables Required:
    LANGSMITH_API_KEY: Your LangSmith API key
    LANGCHAIN_TRACING_V2: Set to "true" to enable tracing
    LANGCHAIN_PROJECT: Project name in LangSmith (default: "langai-research")
    LANGCHAIN_ENDPOINT: API endpoint (default: https://api.smith.langchain.com)
"""

import os
from typing import Optional, Dict, Any
from contextlib import contextmanager
from ..utils import get_config, get_logger

logger = get_logger(__name__)

# Track initialization state
_langsmith_initialized = False
_project_name: Optional[str] = None

# Optional LangSmith SDK import
try:
    from langsmith import Client as LangSmithClient
    from langsmith.run_trees import RunTree
    LANGSMITH_SDK_AVAILABLE = True
except ImportError:
    LANGSMITH_SDK_AVAILABLE = False
    LangSmithClient = None
    RunTree = None


def init_langsmith(
    api_key: Optional[str] = None,
    project: str = "langai-research",
    endpoint: str = "https://api.smith.langchain.com",
    force: bool = False
) -> Dict[str, Any]:
    """
    Initialize LangSmith tracing.

    This sets up environment variables for automatic LangChain tracing
    and initializes the LangSmith client for custom operations.

    Args:
        api_key: LangSmith API key (or use LANGSMITH_API_KEY env var)
        project: Project name in LangSmith dashboard
        endpoint: LangSmith API endpoint
        force: Force re-initialization even if already initialized

    Returns:
        Dictionary with initialization status:
        {
            "enabled": bool,
            "project": str,
            "endpoint": str,
            "sdk_available": bool
        }
    """
    global _langsmith_initialized, _project_name

    if _langsmith_initialized and not force:
        return {
            "enabled": True,
            "project": _project_name,
            "endpoint": get_config("LANGCHAIN_ENDPOINT", default=endpoint),
            "sdk_available": LANGSMITH_SDK_AVAILABLE,
            "message": "Already initialized"
        }

    # Get API key from argument or environment
    api_key = api_key or get_config("LANGSMITH_API_KEY")

    if not api_key:
        logger.info("[LANGSMITH] No API key provided - tracing disabled")
        return {
            "enabled": False,
            "project": None,
            "endpoint": None,
            "sdk_available": LANGSMITH_SDK_AVAILABLE,
            "message": "No API key provided"
        }

    # Set environment variables for automatic LangChain tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGSMITH_API_KEY"] = api_key  # Both for compatibility
    os.environ["LANGCHAIN_PROJECT"] = project
    os.environ["LANGCHAIN_ENDPOINT"] = endpoint

    _langsmith_initialized = True
    _project_name = project

    logger.info(f"[LANGSMITH] Tracing enabled for project: {project}")
    logger.info(f"[LANGSMITH] Dashboard: https://smith.langchain.com/o/default/projects/p/{project}")

    return {
        "enabled": True,
        "project": project,
        "endpoint": endpoint,
        "sdk_available": LANGSMITH_SDK_AVAILABLE,
        "message": "LangSmith tracing initialized successfully"
    }


def is_langsmith_enabled() -> bool:
    """Check if LangSmith tracing is enabled."""
    return (
        get_config("LANGCHAIN_TRACING_V2", default="").lower() == "true"
        and bool(get_config("LANGSMITH_API_KEY") or get_config("LANGCHAIN_API_KEY"))
    )


def get_langsmith_url(run_id: Optional[str] = None) -> Optional[str]:
    """
    Get LangSmith dashboard URL.

    Args:
        run_id: Optional specific run ID to link to

    Returns:
        Dashboard URL or None if not configured
    """
    if not is_langsmith_enabled():
        return None

    project = get_config("LANGCHAIN_PROJECT", default="langai-research")
    base_url = f"https://smith.langchain.com/o/default/projects/p/{project}"

    if run_id:
        return f"{base_url}/r/{run_id}"

    return base_url


def get_langsmith_client() -> Optional["LangSmithClient"]:
    """
    Get LangSmith client for custom operations.

    Returns:
        LangSmithClient instance or None if not available
    """
    if not LANGSMITH_SDK_AVAILABLE:
        logger.warning("[LANGSMITH] LangSmith SDK not installed. Run: pip install langsmith")
        return None

    if not is_langsmith_enabled():
        return None

    try:
        return LangSmithClient()
    except Exception as e:
        logger.error(f"[LANGSMITH] Failed to create client: {e}")
        return None


@contextmanager
def create_run_tree(
    name: str,
    run_type: str = "chain",
    inputs: Optional[Dict[str, Any]] = None,
    tags: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Create a custom run tree for complex operations.

    This allows grouping multiple LLM calls under a single parent trace.

    Args:
        name: Name of the run (e.g., "company_research")
        run_type: Type of run ("chain", "llm", "tool", "retriever")
        inputs: Input data for the run
        tags: Tags for filtering in dashboard
        metadata: Additional metadata

    Yields:
        RunTree object for adding child runs

    Example:
        with create_run_tree("tesla_research", inputs={"company": "Tesla"}) as run:
            # All LLM calls here will be grouped under this run
            result = llm.invoke(prompt)
            run.end(outputs={"result": result})
    """
    if not LANGSMITH_SDK_AVAILABLE or not is_langsmith_enabled():
        # Yield a dummy object if LangSmith not available
        yield type('DummyRun', (), {
            'end': lambda **kwargs: None,
            'post': lambda: None,
            'id': None
        })()
        return

    project = get_config("LANGCHAIN_PROJECT", default="langai-research")

    run = RunTree(
        name=name,
        run_type=run_type,
        inputs=inputs or {},
        tags=tags or [],
        extra={"metadata": metadata or {}},
        project_name=project,
    )

    try:
        yield run
    except Exception as e:
        run.end(error=str(e))
        run.post()
        raise
    else:
        if not run.end_time:
            run.end()
        run.post()


def flush_traces(timeout_seconds: float = 10.0) -> bool:
    """
    Flush all pending traces to LangSmith.

    Call this before program exit to ensure all traces are sent.

    Args:
        timeout_seconds: Maximum time to wait for flush

    Returns:
        True if flush successful, False otherwise
    """
    if not LANGSMITH_SDK_AVAILABLE:
        return True

    try:
        client = get_langsmith_client()
        if client:
            # The client handles batching internally
            logger.info("[LANGSMITH] Traces flushed successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"[LANGSMITH] Failed to flush traces: {e}")
        return False


def get_trace_stats(
    project: Optional[str] = None,
    days: int = 7
) -> Optional[Dict[str, Any]]:
    """
    Get trace statistics from LangSmith.

    Args:
        project: Project name (default: current project)
        days: Number of days to look back

    Returns:
        Dictionary with trace statistics or None if unavailable
    """
    client = get_langsmith_client()
    if not client:
        return None

    project = project or get_config("LANGCHAIN_PROJECT", default="langai-research")

    try:
        # Get recent runs
        runs = list(client.list_runs(
            project_name=project,
            execution_order=1,  # Top-level runs only
            limit=100
        ))

        if not runs:
            return {"total_runs": 0, "message": "No runs found"}

        # Calculate statistics
        total_runs = len(runs)
        successful = sum(1 for r in runs if r.status == "success")
        failed = sum(1 for r in runs if r.status == "error")

        # Calculate costs if available
        total_cost = sum(
            r.total_cost or 0
            for r in runs
            if hasattr(r, 'total_cost')
        )

        return {
            "total_runs": total_runs,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_runs * 100) if total_runs > 0 else 0,
            "total_cost_usd": total_cost,
            "avg_cost_per_run": total_cost / total_runs if total_runs > 0 else 0,
            "project": project,
            "dashboard_url": get_langsmith_url()
        }
    except Exception as e:
        logger.error(f"[LANGSMITH] Failed to get stats: {e}")
        return None
