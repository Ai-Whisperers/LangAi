"""
Cost Tracker (Phase 19.2).

Track and analyze costs:
- LLM API costs
- Search API costs
- Cost budgeting
- Cost alerts
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


# ============================================================================
# Enums and Data Models
# ============================================================================


class CostCategory(str, Enum):
    """Cost categories."""

    LLM = "llm"  # Language model API
    SEARCH = "search"  # Search API
    EMBEDDING = "embedding"  # Embedding API
    STORAGE = "storage"  # Storage costs
    COMPUTE = "compute"  # Compute resources
    OTHER = "other"


@dataclass
class CostEntry:
    """A single cost entry."""

    amount: float
    category: CostCategory
    description: str
    timestamp: datetime = field(default_factory=utc_now)
    task_id: Optional[str] = None
    company_name: Optional[str] = None
    agent_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": round(self.amount, 6),
            "category": self.category.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "company_name": self.company_name,
            "agent_name": self.agent_name,
        }


@dataclass
class Budget:
    """Cost budget configuration."""

    name: str
    limit: float
    period: str  # "daily", "weekly", "monthly"
    current: float = 0.0
    start_date: datetime = field(default_factory=utc_now)
    alert_threshold: float = 0.8  # Alert at 80%

    @property
    def remaining(self) -> float:
        return max(0, self.limit - self.current)

    @property
    def utilization(self) -> float:
        return self.current / self.limit if self.limit > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "limit": round(self.limit, 2),
            "current": round(self.current, 4),
            "remaining": round(self.remaining, 4),
            "utilization": round(self.utilization, 2),
            "period": self.period,
        }


@dataclass
class CostSummary:
    """Cost summary for a period."""

    total: float = 0.0
    by_category: Dict[str, float] = field(default_factory=dict)
    by_agent: Dict[str, float] = field(default_factory=dict)
    by_company: Dict[str, float] = field(default_factory=dict)
    entry_count: int = 0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": round(self.total, 4),
            "by_category": {k: round(v, 4) for k, v in self.by_category.items()},
            "by_agent": {k: round(v, 4) for k, v in self.by_agent.items()},
            "by_company": {k: round(v, 4) for k, v in self.by_company.items()},
            "entry_count": self.entry_count,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
        }


# ============================================================================
# Cost Tracker
# ============================================================================


class CostTracker:
    """
    Track and analyze API costs.

    Features:
    - Real-time cost tracking
    - Budget management
    - Cost breakdowns
    - Trend analysis

    Usage:
        tracker = CostTracker()

        # Track costs
        tracker.record_llm_cost(
            tokens_in=1000,
            tokens_out=500,
            model="claude-3-sonnet",
            agent_name="financial"
        )

        # Check budget
        if tracker.is_over_budget():
            print("Budget exceeded!")

        # Get summary
        summary = tracker.get_daily_summary()
    """

    # Default pricing (per 1M tokens)
    DEFAULT_PRICING = {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    }

    def __init__(
        self,
        daily_budget: float = 10.0,
        monthly_budget: float = 300.0,
        pricing: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize cost tracker.

        Args:
            daily_budget: Daily budget limit
            monthly_budget: Monthly budget limit
            pricing: Custom pricing per model
        """
        self._pricing = pricing or self.DEFAULT_PRICING
        self._entries: List[CostEntry] = []
        self._lock = threading.RLock()

        # Budgets
        self._budgets: Dict[str, Budget] = {
            "daily": Budget(name="daily", limit=daily_budget, period="daily"),
            "monthly": Budget(name="monthly", limit=monthly_budget, period="monthly"),
        }

        # Callbacks
        self._on_budget_alert: List[callable] = []

    # ==========================================================================
    # Recording Costs
    # ==========================================================================

    def record_cost(
        self,
        amount: float,
        category: CostCategory,
        description: str,
        task_id: Optional[str] = None,
        company_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CostEntry:
        """Record a cost entry."""
        entry = CostEntry(
            amount=amount,
            category=category,
            description=description,
            task_id=task_id,
            company_name=company_name,
            agent_name=agent_name,
            metadata=metadata or {},
        )

        with self._lock:
            self._entries.append(entry)
            self._update_budgets(amount)

        return entry

    def record_llm_cost(
        self,
        tokens_in: int,
        tokens_out: int,
        model: str = "claude-3-sonnet",
        task_id: Optional[str] = None,
        company_name: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> CostEntry:
        """Record LLM API cost."""
        pricing = self._pricing.get(model, {"input": 3.0, "output": 15.0})

        cost = (tokens_in / 1_000_000) * pricing["input"] + (tokens_out / 1_000_000) * pricing[
            "output"
        ]

        return self.record_cost(
            amount=cost,
            category=CostCategory.LLM,
            description=f"{model}: {tokens_in} in, {tokens_out} out",
            task_id=task_id,
            company_name=company_name,
            agent_name=agent_name,
            metadata={"model": model, "tokens_in": tokens_in, "tokens_out": tokens_out},
        )

    def record_search_cost(
        self,
        query_count: int,
        provider: str = "tavily",
        task_id: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> CostEntry:
        """Record search API cost."""
        # Typical search API pricing
        cost_per_query = 0.01  # $0.01 per query estimate
        cost = query_count * cost_per_query

        return self.record_cost(
            amount=cost,
            category=CostCategory.SEARCH,
            description=f"{provider}: {query_count} queries",
            task_id=task_id,
            company_name=company_name,
            metadata={"provider": provider, "queries": query_count},
        )

    def record_embedding_cost(
        self,
        tokens: int,
        model: str = "text-embedding-3-small",
        task_id: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> CostEntry:
        """Record embedding API cost."""
        # Embedding pricing (per 1M tokens)
        pricing = {"text-embedding-3-small": 0.02, "text-embedding-3-large": 0.13}
        rate = pricing.get(model, 0.02)
        cost = (tokens / 1_000_000) * rate

        return self.record_cost(
            amount=cost,
            category=CostCategory.EMBEDDING,
            description=f"{model}: {tokens} tokens",
            task_id=task_id,
            company_name=company_name,
            metadata={"model": model, "tokens": tokens},
        )

    # ==========================================================================
    # Budget Management
    # ==========================================================================

    def _update_budgets(self, amount: float):
        """Update budget trackers."""
        for budget in self._budgets.values():
            budget.current += amount

            # Check for alerts
            if budget.utilization >= budget.alert_threshold:
                self._trigger_budget_alert(budget)

    def _trigger_budget_alert(self, budget: Budget):
        """Trigger budget alert callbacks."""
        for callback in self._on_budget_alert:
            try:
                callback(budget)
            except Exception as e:
                logger.debug(f"Budget alert callback failed for {budget.name}: {e}")

    def set_budget(
        self, name: str, limit: float, period: str = "daily", alert_threshold: float = 0.8
    ):
        """Set or update a budget."""
        self._budgets[name] = Budget(
            name=name, limit=limit, period=period, alert_threshold=alert_threshold
        )

    def get_budget(self, name: str) -> Optional[Budget]:
        """Get budget by name."""
        return self._budgets.get(name)

    def is_over_budget(self, budget_name: str = "daily") -> bool:
        """Check if over budget."""
        budget = self._budgets.get(budget_name)
        return budget.utilization >= 1.0 if budget else False

    def get_remaining_budget(self, budget_name: str = "daily") -> float:
        """Get remaining budget."""
        budget = self._budgets.get(budget_name)
        return budget.remaining if budget else 0.0

    def reset_budget(self, budget_name: str):
        """Reset a budget."""
        if budget_name in self._budgets:
            self._budgets[budget_name].current = 0.0
            self._budgets[budget_name].start_date = utc_now()

    def on_budget_alert(self, callback: callable):
        """Register budget alert callback."""
        self._on_budget_alert.append(callback)

    # ==========================================================================
    # Cost Analysis
    # ==========================================================================

    def get_total_cost(
        self, since: Optional[datetime] = None, until: Optional[datetime] = None
    ) -> float:
        """Get total cost for a period."""
        with self._lock:
            entries = self._filter_entries(since, until)
            return sum(e.amount for e in entries)

    def get_summary(
        self, since: Optional[datetime] = None, until: Optional[datetime] = None
    ) -> CostSummary:
        """Get cost summary for a period."""
        with self._lock:
            entries = self._filter_entries(since, until)

            summary = CostSummary(period_start=since, period_end=until, entry_count=len(entries))

            for entry in entries:
                summary.total += entry.amount

                # By category
                cat = entry.category.value
                summary.by_category[cat] = summary.by_category.get(cat, 0) + entry.amount

                # By agent
                if entry.agent_name:
                    summary.by_agent[entry.agent_name] = (
                        summary.by_agent.get(entry.agent_name, 0) + entry.amount
                    )

                # By company
                if entry.company_name:
                    summary.by_company[entry.company_name] = (
                        summary.by_company.get(entry.company_name, 0) + entry.amount
                    )

            return summary

    def get_daily_summary(self) -> CostSummary:
        """Get today's cost summary."""
        today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_summary(since=today)

    def get_weekly_summary(self) -> CostSummary:
        """Get this week's cost summary."""
        today = utc_now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_summary(since=week_start)

    def get_monthly_summary(self) -> CostSummary:
        """Get this month's cost summary."""
        today = utc_now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_summary(since=month_start)

    def get_cost_by_company(self, company_name: str, since: Optional[datetime] = None) -> float:
        """Get total cost for a specific company."""
        with self._lock:
            entries = self._filter_entries(since)
            return sum(e.amount for e in entries if e.company_name == company_name)

    def get_cost_by_task(self, task_id: str) -> float:
        """Get total cost for a specific task."""
        with self._lock:
            return sum(e.amount for e in self._entries if e.task_id == task_id)

    def get_entries(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        category: Optional[CostCategory] = None,
    ) -> List[CostEntry]:
        """Get filtered cost entries."""
        with self._lock:
            entries = self._filter_entries(since, until)
            if category:
                entries = [e for e in entries if e.category == category]
            return entries

    def _filter_entries(
        self, since: Optional[datetime] = None, until: Optional[datetime] = None
    ) -> List[CostEntry]:
        """Filter entries by time range."""
        entries = self._entries
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        if until:
            entries = [e for e in entries if e.timestamp <= until]
        return entries

    # ==========================================================================
    # Export
    # ==========================================================================

    def export_json(self) -> Dict[str, Any]:
        """Export cost data as JSON."""
        return {
            "total": round(self.get_total_cost(), 4),
            "budgets": {k: v.to_dict() for k, v in self._budgets.items()},
            "daily_summary": self.get_daily_summary().to_dict(),
            "monthly_summary": self.get_monthly_summary().to_dict(),
            "entry_count": len(self._entries),
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_cost_tracker(daily_budget: float = 10.0, monthly_budget: float = 300.0) -> CostTracker:
    """Create a cost tracker instance."""
    return CostTracker(daily_budget=daily_budget, monthly_budget=monthly_budget)
