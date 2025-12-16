"""
Observability module for Company Researcher (Phase 4).

This module provides comprehensive monitoring and debugging capabilities:
- AgentOps: Agent monitoring with session replay
- LangSmith: Full LangChain/LangGraph trace visibility (FULLY INTEGRATED)
- Cost Tracking: Per-agent cost attribution
- Performance Metrics: Latency and throughput tracking

Usage:
    from company_researcher.observability import init_observability, track_research_session

    # Initialize at startup (includes LangSmith)
    init_observability()

    # Track a research session
    with track_research_session(company_name="Tesla"):
        # Run research workflow - all LLM calls auto-traced to LangSmith
        result = research_company("Tesla")

LangSmith Integration:
    The observability module now fully integrates with the LLM module for
    automatic LangSmith tracing. All LLM calls made through the LangChain
    client will be traced automatically.

    To view traces: https://smith.langchain.com
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from .config import get_config
from .utils import get_logger, utc_now

# Optional imports (gracefully handle if not installed)
try:
    import agentops

    AGENTOPS_AVAILABLE = True
except ImportError:
    AGENTOPS_AVAILABLE = False
    agentops = None

# Import LangSmith integration from LLM module
try:
    from .llm.langsmith_setup import (
        create_run_tree,
        flush_traces,
        get_langsmith_url,
        get_trace_stats,
    )
    from .llm.langsmith_setup import init_langsmith as _init_langsmith_module
    from .llm.langsmith_setup import is_langsmith_enabled as _is_langsmith_enabled

    LLM_MODULE_AVAILABLE = True
except ImportError:
    LLM_MODULE_AVAILABLE = False
    _init_langsmith_module = None
    _is_langsmith_enabled = lambda: False
    get_langsmith_url = lambda **kwargs: None
    get_trace_stats = lambda **kwargs: None
    flush_traces = lambda **kwargs: True
    create_run_tree = None

logger = get_logger(__name__)

# ============================================================================
# Global State
# ============================================================================

_agentops_initialized = False
_langsmith_initialized = False
_current_session_id: Optional[str] = None


# ============================================================================
# Initialization
# ============================================================================


def init_observability() -> Dict[str, Any]:
    """
    Initialize observability tools (AgentOps + LangSmith).

    This should be called once at application startup.

    Returns:
        Dictionary indicating which tools were initialized:
        {
            "agentops": bool,
            "langsmith": bool,
            "langsmith_url": Optional[str]
        }
    """
    global _agentops_initialized, _langsmith_initialized

    config = get_config()
    results = {"agentops": False, "langsmith": False, "langsmith_url": None}

    # Initialize AgentOps
    if config.agentops_api_key and AGENTOPS_AVAILABLE:
        try:
            agentops.init(
                api_key=config.agentops_api_key,
                default_tags=["production", "company-researcher", "phase-4"],
                auto_start_session=False,  # We'll manually start sessions
            )
            _agentops_initialized = True
            results["agentops"] = True
            logger.info("[OBSERVABILITY] AgentOps initialized successfully")
        except Exception as e:
            logger.warning(f"[OBSERVABILITY] AgentOps initialization failed: {e}")
    elif config.agentops_api_key and not AGENTOPS_AVAILABLE:
        logger.warning("[OBSERVABILITY] AgentOps API key provided but agentops not installed")

    # Initialize LangSmith using the new LLM module
    if config.langsmith_api_key:
        try:
            if LLM_MODULE_AVAILABLE and _init_langsmith_module:
                # Use the new comprehensive LangSmith initialization
                langsmith_result = _init_langsmith_module(
                    api_key=config.langsmith_api_key,
                    project=config.langchain_project,
                    endpoint=config.langchain_endpoint,
                )
                _langsmith_initialized = langsmith_result.get("enabled", False)
                results["langsmith"] = _langsmith_initialized
                results["langsmith_url"] = get_langsmith_url()
                if _langsmith_initialized:
                    logger.info(
                        f"[OBSERVABILITY] LangSmith tracing enabled (project: {config.langchain_project})"
                    )
                    logger.info(f"[OBSERVABILITY] View traces at: {results['langsmith_url']}")
            else:
                # Fallback to environment variables only
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
                os.environ["LANGCHAIN_PROJECT"] = config.langchain_project
                os.environ["LANGCHAIN_ENDPOINT"] = config.langchain_endpoint
                _langsmith_initialized = True
                results["langsmith"] = True
                logger.info(
                    f"[OBSERVABILITY] LangSmith tracing enabled (project: {config.langchain_project})"
                )
        except Exception as e:
            logger.warning(f"[OBSERVABILITY] LangSmith initialization failed: {e}")

    # Summary
    if results["agentops"] or results["langsmith"]:
        logger.info("[OBSERVABILITY] Observability initialized successfully")
    else:
        logger.info("[OBSERVABILITY] No observability tools configured")

    return results


# ============================================================================
# Session Management
# ============================================================================


@contextmanager
def track_research_session(company_name: str, tags: Optional[List[str]] = None):
    """
    Context manager for tracking a research session.

    Usage:
        with track_research_session(company_name="Tesla"):
            result = research_company("Tesla")

    Args:
        company_name: Company being researched
        tags: Optional additional tags for the session

    Yields:
        Session ID (if AgentOps enabled, otherwise None)
    """
    global _current_session_id

    session_id = None
    session_tags = [company_name, "research"]
    if tags:
        session_tags.extend(tags)

    # Start AgentOps session
    if _agentops_initialized and AGENTOPS_AVAILABLE:
        try:
            session_id = agentops.start_session(tags=session_tags)
            _current_session_id = session_id
            agentops.record_action(
                action_type="research_start",
                params={"company": company_name, "timestamp": utc_now().isoformat()},
            )
            logger.info(f"[OBSERVABILITY] AgentOps session started: {session_id}")
        except Exception as e:
            logger.warning(f"[OBSERVABILITY] Failed to start AgentOps session: {e}")

    try:
        yield session_id
    except Exception as e:
        # End session with error
        if _agentops_initialized and AGENTOPS_AVAILABLE:
            try:
                agentops.end_session(end_state="Fail", end_state_reason=str(e))
                logger.info(f"[OBSERVABILITY] AgentOps session ended with error: {e}")
            except Exception as end_error:
                logger.warning(f"[OBSERVABILITY] Failed to end AgentOps session: {end_error}")
        raise
    else:
        # End session successfully
        if _agentops_initialized and AGENTOPS_AVAILABLE:
            try:
                agentops.end_session(end_state="Success")
                logger.info("[OBSERVABILITY] AgentOps session ended successfully")
            except Exception as e:
                logger.warning(f"[OBSERVABILITY] Failed to end AgentOps session: {e}")
    finally:
        _current_session_id = None


def record_agent_event(agent_name: str, event_type: str, data: Optional[Dict[str, Any]] = None):
    """
    Record an agent event to AgentOps.

    Args:
        agent_name: Name of the agent (e.g., "financial", "market")
        event_type: Type of event (e.g., "analysis_start", "analysis_complete")
        data: Optional event data
    """
    if not _agentops_initialized or not AGENTOPS_AVAILABLE:
        return

    try:
        agentops.record_action(action_type=f"{agent_name}_{event_type}", params=data or {})
    except Exception as e:
        logger.warning(f"[OBSERVABILITY] Failed to record agent event: {e}")


def record_llm_call(
    agent_name: str,
    prompt: str,
    response: str,
    model: str,
    tokens: Dict[str, int],
    cost: float,
    latency_ms: float,
):
    """
    Record an LLM call to AgentOps.

    Args:
        agent_name: Name of the agent making the call
        prompt: Input prompt
        response: LLM response
        model: Model name
        tokens: Token usage {"input": int, "output": int}
        cost: Cost in USD
        latency_ms: Latency in milliseconds
    """
    if not _agentops_initialized or not AGENTOPS_AVAILABLE:
        return

    try:
        agentops.record_action(
            action_type="llm_call",
            params={
                "agent": agent_name,
                "model": model,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "tokens_input": tokens.get("input", 0),
                "tokens_output": tokens.get("output", 0),
                "cost_usd": cost,
                "latency_ms": latency_ms,
            },
        )
    except Exception as e:
        logger.warning(f"[OBSERVABILITY] Failed to record LLM call: {e}")


def record_quality_check(quality_score: float, missing_info: List[str], iteration: int):
    """
    Record quality check results to AgentOps.

    Args:
        quality_score: Quality score (0-100)
        missing_info: List of missing information items
        iteration: Current iteration number
    """
    if not _agentops_initialized or not AGENTOPS_AVAILABLE:
        return

    try:
        agentops.record_action(
            action_type="quality_check",
            params={
                "quality_score": quality_score,
                "missing_count": len(missing_info),
                "iteration": iteration,
                "passed": quality_score >= 85.0,
            },
        )
    except Exception as e:
        logger.warning(f"[OBSERVABILITY] Failed to record quality check: {e}")


# ============================================================================
# Cost Tracking Enhancement (Phase 4.5)
# ============================================================================


class CostTracker:
    """
    Enhanced cost tracking with per-agent attribution.

    This class provides detailed cost tracking beyond the basic
    token counting in state.py. It tracks costs per agent, per
    iteration, and provides budget alerts.
    """

    def __init__(self):
        """Initialize cost tracker."""
        self.session_costs: List[Dict[str, Any]] = []
        self.agent_costs: Dict[str, float] = {}
        self.total_cost: float = 0.0

    def track_agent_cost(
        self, agent_name: str, model: str, tokens: Dict[str, int], cost: float, iteration: int = 1
    ):
        """
        Track cost for a specific agent call.

        Args:
            agent_name: Name of the agent
            model: Model used
            tokens: Token usage
            cost: Cost in USD
            iteration: Iteration number
        """
        cost_entry = {
            "agent": agent_name,
            "model": model,
            "tokens": tokens,
            "cost": cost,
            "iteration": iteration,
            "timestamp": utc_now().isoformat(),
        }

        self.session_costs.append(cost_entry)
        self.agent_costs[agent_name] = self.agent_costs.get(agent_name, 0.0) + cost
        self.total_cost += cost

        # Log if cost exceeds threshold
        config = get_config()
        if self.total_cost > config.target_cost_usd:
            logger.warning(
                f"[COST] Session cost ${self.total_cost:.4f} exceeds "
                f"target ${config.target_cost_usd:.2f}"
            )

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed cost breakdown.

        Returns:
            Dictionary with cost breakdown by agent and iteration
        """
        return {
            "total_cost": self.total_cost,
            "by_agent": self.agent_costs.copy(),
            "calls": len(self.session_costs),
            "average_per_call": (
                self.total_cost / len(self.session_costs) if self.session_costs else 0.0
            ),
        }


# ============================================================================
# Utility Functions
# ============================================================================


def is_observability_enabled() -> bool:
    """Check if any observability tool is enabled."""
    return _agentops_initialized or _langsmith_initialized


def get_current_session_id() -> Optional[str]:
    """Get the current AgentOps session ID."""
    return _current_session_id


def get_observability_status() -> Dict[str, Any]:
    """
    Get observability status.

    Returns:
        Dictionary with observability status:
        {
            "enabled": bool,
            "agentops": bool,
            "langsmith": bool,
            "langsmith_url": Optional[str],
            "session_id": Optional[str]
        }
    """
    return {
        "enabled": is_observability_enabled(),
        "agentops": _agentops_initialized,
        "langsmith": _langsmith_initialized,
        "langsmith_url": get_langsmith_url() if _langsmith_initialized else None,
        "session_id": _current_session_id,
    }


# ============================================================================
# LangSmith Re-exports (for convenience)
# ============================================================================

# Re-export LangSmith functions for direct access from observability module
__all__ = [
    # Initialization
    "init_observability",
    "is_observability_enabled",
    "get_observability_status",
    # Session Management
    "track_research_session",
    "record_agent_event",
    "record_llm_call",
    "record_quality_check",
    "get_current_session_id",
    # Cost Tracking
    "CostTracker",
    # LangSmith (re-exported from llm module)
    "get_langsmith_url",
    "get_trace_stats",
    "flush_traces",
    "create_run_tree",
]
