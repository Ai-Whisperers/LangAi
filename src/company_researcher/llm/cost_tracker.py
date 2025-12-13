"""
Enhanced Cost Tracking with Detailed Metrics.

Provides comprehensive tracking of API costs across all agents,
including cache savings, per-agent breakdown, and export capabilities.

Usage:
    from company_researcher.llm.cost_tracker import get_cost_tracker

    tracker = get_cost_tracker()
    cost = tracker.record_call(
        model="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=500,
        agent_name="financial",
        company_name="Tesla"
    )

    # Get summary
    summary = tracker.get_summary()
    print(f"Total cost: ${summary['total_cost']:.4f}")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from threading import Lock
from enum import Enum
import asyncio
import json
from ..utils import utc_now


class CostModel(str, Enum):
    """Supported cost models."""
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    CLAUDE_SONNET_35 = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_OPUS = "claude-3-opus-20240229"


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    cost: float = 0.0
    agent_name: str = ""
    company_name: str = ""
    research_run_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "cost": self.cost,
            "agent_name": self.agent_name,
            "company_name": self.company_name,
            "research_run_id": self.research_run_id,
            "metadata": self.metadata
        }


@dataclass
class CostSummary:
    """Summary of costs over a period."""
    total_cost: float
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_cached_tokens: int
    cache_savings: float
    by_agent: Dict[str, Dict[str, Any]]
    by_company: Dict[str, Dict[str, Any]]
    by_model: Dict[str, Dict[str, Any]]
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_cost": self.total_cost,
            "total_calls": self.total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cached_tokens": self.total_cached_tokens,
            "cache_savings": self.cache_savings,
            "by_agent": self.by_agent,
            "by_company": self.by_company,
            "by_model": self.by_model,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None
        }


class CostTracker:
    """
    Tracks API costs across all agents with detailed metrics.

    Thread-safe implementation for concurrent access.
    """

    # Pricing per 1M tokens (as of late 2024)
    PRICING = {
        # Latest models (December 2024) - Most cost-effective
        "claude-opus-4-5-20250929": {
            "input": 5.0,
            "output": 25.0,
            "cached_input": 0.50,
            "cache_write": 6.25,
            "batch_input": 2.5,
            "batch_output": 12.5
        },
        "claude-sonnet-4-5-20250929": {
            "input": 3.0,
            "output": 15.0,
            "cached_input": 0.30,
            "cache_write": 3.75,
            "batch_input": 1.5,
            "batch_output": 7.5
        },
        "claude-haiku-4-5-20250929": {
            "input": 1.0,
            "output": 5.0,
            "cached_input": 0.10,
            "cache_write": 1.25,
            "batch_input": 0.5,
            "batch_output": 2.5
        },
        # Legacy 4.x models
        "claude-opus-4-1-20250514": {
            "input": 15.0,
            "output": 75.0,
            "cached_input": 1.50,
            "cache_write": 18.75,
            "batch_input": 7.5,
            "batch_output": 37.5
        },
        "claude-sonnet-4-20250514": {
            "input": 3.0,
            "output": 15.0,
            "cached_input": 0.30,
            "cache_write": 3.75,
            "batch_input": 1.5,
            "batch_output": 7.5
        },
        # Legacy 3.5 models
        "claude-3-5-sonnet-20241022": {
            "input": 3.0,
            "output": 15.0,
            "cached_input": 0.30,
            "cache_write": 3.75,
            "batch_input": 1.5,
            "batch_output": 7.5
        },
        "claude-3-5-haiku-20241022": {
            "input": 0.80,
            "output": 4.0,
            "cached_input": 0.08,
            "cache_write": 1.0,
            "batch_input": 0.40,
            "batch_output": 2.0
        },
        # Legacy 3.0 models
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25,
            "cached_input": 0.03,
            "cache_write": 0.30,
            "batch_input": 0.125,
            "batch_output": 0.625
        },
        "claude-3-opus-20240229": {
            "input": 15.0,
            "output": 75.0,
            "cached_input": 1.50,
            "cache_write": 18.75,
            "batch_input": 7.5,
            "batch_output": 37.5
        },
        # Web search tool pricing (per search, not per token)
        "web_search": {
            "per_search": 0.01  # $10 per 1,000 searches = $0.01 each
        }
    }

    # Default pricing for unknown models
    DEFAULT_PRICING = {
        "input": 3.0,
        "output": 15.0,
        "cached_input": 0.30,
        "batch_input": 1.5,
        "batch_output": 7.5
    }

    def __init__(self, max_history: int = 10000):
        """
        Initialize the cost tracker.

        Args:
            max_history: Maximum number of calls to retain in memory
        """
        self.calls: List[APICall] = []
        self.max_history = max_history
        self._lock = Lock()
        self._async_lock: Optional[asyncio.Lock] = None
        self._current_research_run: Optional[str] = None

    def _get_async_lock(self) -> asyncio.Lock:
        """Get or create async lock (must be created in event loop context)."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    def set_research_run(self, run_id: str) -> None:
        """
        Set current research run ID for tracking.

        Args:
            run_id: Research run identifier
        """
        with self._lock:
            self._current_research_run = run_id

    def clear_research_run(self) -> None:
        """Clear current research run ID."""
        with self._lock:
            self._current_research_run = None

    def record_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        agent_name: str = "",
        company_name: str = "",
        is_batch: bool = False,
        metadata: Dict[str, Any] = None
    ) -> float:
        """
        Record an API call and return calculated cost.

        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_tokens: Number of cached tokens (reduces cost)
            agent_name: Name of agent making the call
            company_name: Company being researched
            is_batch: Whether this was a batch API call
            metadata: Additional metadata

        Returns:
            Calculated cost in USD
        """
        pricing = self.PRICING.get(model, self.DEFAULT_PRICING)

        # Calculate cost
        if is_batch:
            input_cost = (input_tokens / 1_000_000) * pricing["batch_input"]
            output_cost = (output_tokens / 1_000_000) * pricing["batch_output"]
            cache_cost = 0  # Batch doesn't support caching
        else:
            # Non-cached input tokens
            regular_input = max(0, input_tokens - cached_tokens)
            input_cost = (regular_input / 1_000_000) * pricing["input"]

            # Cached input tokens (90% cheaper)
            cached_cost = (cached_tokens / 1_000_000) * pricing["cached_input"]

            # Output cost
            output_cost = (output_tokens / 1_000_000) * pricing["output"]

            input_cost = input_cost + cached_cost

        total_cost = input_cost + output_cost

        # Calculate what we would have paid without caching
        full_input_cost = (input_tokens / 1_000_000) * pricing["input"]
        cache_savings = full_input_cost - input_cost if cached_tokens > 0 else 0

        call = APICall(
            timestamp=utc_now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost=total_cost,
            agent_name=agent_name,
            company_name=company_name,
            research_run_id=self._current_research_run,
            metadata=metadata or {}
        )

        with self._lock:
            self._append_call(call)

        return total_cost

    async def record_call_async(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        agent_name: str = "",
        company_name: str = "",
        is_batch: bool = False,
        metadata: Dict[str, Any] = None
    ) -> float:
        """
        Record an API call asynchronously (non-blocking).

        Same as record_call but uses asyncio.Lock to avoid blocking the event loop.
        Use this from async FastAPI handlers.
        """
        pricing = self.PRICING.get(model, self.DEFAULT_PRICING)

        # Calculate cost (same logic as sync version)
        if is_batch:
            input_cost = (input_tokens / 1_000_000) * pricing["batch_input"]
            output_cost = (output_tokens / 1_000_000) * pricing["batch_output"]
        else:
            regular_input = max(0, input_tokens - cached_tokens)
            input_cost = (regular_input / 1_000_000) * pricing["input"]
            cached_cost = (cached_tokens / 1_000_000) * pricing["cached_input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            input_cost = input_cost + cached_cost

        total_cost = input_cost + output_cost

        call = APICall(
            timestamp=utc_now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost=total_cost,
            agent_name=agent_name,
            company_name=company_name,
            research_run_id=self._current_research_run,
            metadata=metadata or {}
        )

        async with self._get_async_lock():
            self._append_call(call)

        return total_cost

    def _append_call(self, call: APICall) -> None:
        """Append a call and trim history (must be called with lock held)."""
        self.calls.append(call)
        if len(self.calls) > self.max_history:
            self.calls = self.calls[-self.max_history:]

    def get_summary(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        agent_name: Optional[str] = None,
        company_name: Optional[str] = None,
        research_run_id: Optional[str] = None
    ) -> CostSummary:
        """
        Get cost summary with optional filtering.

        Args:
            since: Start of time period
            until: End of time period
            agent_name: Filter by agent
            company_name: Filter by company
            research_run_id: Filter by research run

        Returns:
            CostSummary with aggregated metrics
        """
        with self._lock:
            filtered_calls = self._filter_calls(
                since=since,
                until=until,
                agent_name=agent_name,
                company_name=company_name,
                research_run_id=research_run_id
            )

        total_cost = sum(c.cost for c in filtered_calls)
        total_input = sum(c.input_tokens for c in filtered_calls)
        total_output = sum(c.output_tokens for c in filtered_calls)
        total_cached = sum(c.cached_tokens for c in filtered_calls)

        # By agent breakdown
        by_agent: Dict[str, Dict[str, Any]] = {}
        for call in filtered_calls:
            name = call.agent_name or "unknown"
            if name not in by_agent:
                by_agent[name] = {"cost": 0, "calls": 0, "input_tokens": 0, "output_tokens": 0}
            by_agent[name]["cost"] += call.cost
            by_agent[name]["calls"] += 1
            by_agent[name]["input_tokens"] += call.input_tokens
            by_agent[name]["output_tokens"] += call.output_tokens

        # By company breakdown
        by_company: Dict[str, Dict[str, Any]] = {}
        for call in filtered_calls:
            name = call.company_name or "unknown"
            if name not in by_company:
                by_company[name] = {"cost": 0, "calls": 0}
            by_company[name]["cost"] += call.cost
            by_company[name]["calls"] += 1

        # By model breakdown
        by_model: Dict[str, Dict[str, Any]] = {}
        for call in filtered_calls:
            model = call.model
            if model not in by_model:
                by_model[model] = {"cost": 0, "calls": 0, "input_tokens": 0, "output_tokens": 0}
            by_model[model]["cost"] += call.cost
            by_model[model]["calls"] += 1
            by_model[model]["input_tokens"] += call.input_tokens
            by_model[model]["output_tokens"] += call.output_tokens

        # Estimate cache savings
        cache_savings = self._estimate_cache_savings(filtered_calls)

        return CostSummary(
            total_cost=total_cost,
            total_calls=len(filtered_calls),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_cached_tokens=total_cached,
            cache_savings=cache_savings,
            by_agent=by_agent,
            by_company=by_company,
            by_model=by_model,
            period_start=since,
            period_end=until
        )

    def _filter_calls(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        agent_name: Optional[str] = None,
        company_name: Optional[str] = None,
        research_run_id: Optional[str] = None
    ) -> List[APICall]:
        """Filter calls by criteria."""
        filtered = self.calls

        if since:
            filtered = [c for c in filtered if c.timestamp >= since]
        if until:
            filtered = [c for c in filtered if c.timestamp <= until]
        if agent_name:
            filtered = [c for c in filtered if c.agent_name == agent_name]
        if company_name:
            filtered = [c for c in filtered if c.company_name == company_name]
        if research_run_id:
            filtered = [c for c in filtered if c.research_run_id == research_run_id]

        return filtered

    def _estimate_cache_savings(self, calls: List[APICall]) -> float:
        """Estimate savings from caching."""
        total_savings = 0.0
        for call in calls:
            if call.cached_tokens > 0:
                pricing = self.PRICING.get(call.model, self.DEFAULT_PRICING)
                # What we would have paid
                full_cost = (call.cached_tokens / 1_000_000) * pricing["input"]
                # What we paid
                cached_cost = (call.cached_tokens / 1_000_000) * pricing["cached_input"]
                total_savings += full_cost - cached_cost
        return total_savings

    def get_today_summary(self) -> CostSummary:
        """Get summary for today."""
        today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_summary(since=today)

    def get_week_summary(self) -> CostSummary:
        """Get summary for the past 7 days."""
        week_ago = utc_now() - timedelta(days=7)
        return self.get_summary(since=week_ago)

    def get_research_run_summary(self, run_id: str) -> CostSummary:
        """Get summary for a specific research run."""
        return self.get_summary(research_run_id=run_id)

    def export_to_json(self, filepath: str) -> None:
        """
        Export call history to JSON file.

        Args:
            filepath: Path to output file
        """
        with self._lock:
            data = {
                "exported_at": utc_now().isoformat(),
                "total_calls": len(self.calls),
                "calls": [call.to_dict() for call in self.calls]
            }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def reset(self) -> None:
        """Reset all tracking data."""
        with self._lock:
            self.calls = []
            self._current_research_run = None

    def print_summary(self, summary: Optional[CostSummary] = None) -> None:
        """
        Print formatted cost summary to console.

        Args:
            summary: Summary to print (default: overall summary)
        """
        if summary is None:
            summary = self.get_summary()

        print("\n" + "=" * 60)
        print("COST TRACKER SUMMARY")
        print("=" * 60)
        print(f"Total Cost: ${summary.total_cost:.4f}")
        print(f"Total API Calls: {summary.total_calls}")
        print(f"Total Input Tokens: {summary.total_input_tokens:,}")
        print(f"Total Output Tokens: {summary.total_output_tokens:,}")
        print(f"Total Cached Tokens: {summary.total_cached_tokens:,}")
        print(f"Estimated Cache Savings: ${summary.cache_savings:.4f}")

        if summary.by_agent:
            print("\nBy Agent:")
            for agent, stats in sorted(summary.by_agent.items(), key=lambda x: x[1]["cost"], reverse=True):
                print(f"  {agent}: ${stats['cost']:.4f} ({stats['calls']} calls)")

        if summary.by_model:
            print("\nBy Model:")
            for model, stats in sorted(summary.by_model.items(), key=lambda x: x[1]["cost"], reverse=True):
                print(f"  {model}: ${stats['cost']:.4f} ({stats['calls']} calls)")

        print("=" * 60)


# Singleton instance
_cost_tracker: Optional[CostTracker] = None
_tracker_lock = Lock()


def get_cost_tracker() -> CostTracker:
    """
    Get singleton cost tracker instance.

    Returns:
        CostTracker instance
    """
    global _cost_tracker
    if _cost_tracker is None:
        with _tracker_lock:
            if _cost_tracker is None:
                _cost_tracker = CostTracker()
    return _cost_tracker


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet-4-20250514",
    cached_tokens: int = 0
) -> float:
    """
    Convenience function to calculate cost without tracking.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model used
        cached_tokens: Number of cached tokens

    Returns:
        Calculated cost in USD
    """
    pricing = CostTracker.PRICING.get(model, CostTracker.DEFAULT_PRICING)

    regular_input = max(0, input_tokens - cached_tokens)
    input_cost = (regular_input / 1_000_000) * pricing["input"]
    cached_cost = (cached_tokens / 1_000_000) * pricing["cached_input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + cached_cost + output_cost
