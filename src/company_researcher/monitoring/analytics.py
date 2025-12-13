"""
Analytics Aggregator (Phase 19.4).

Aggregate and analyze operational data:
- Usage analytics
- Trend analysis
- Dashboard data
- Reporting
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from ..utils import utc_now


# ============================================================================
# Enums and Data Models
# ============================================================================

class TimeRange(str, Enum):
    """Time range for analytics."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"


@dataclass
class UsageStats:
    """Usage statistics."""
    total_researches: int = 0
    completed: int = 0
    failed: int = 0
    total_companies: int = 0
    unique_companies: int = 0
    avg_duration_seconds: float = 0.0
    total_cost: float = 0.0
    avg_cost: float = 0.0
    period: str = ""

    @property
    def success_rate(self) -> float:
        if self.total_researches == 0:
            return 0.0
        return self.completed / self.total_researches

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_researches": self.total_researches,
            "completed": self.completed,
            "failed": self.failed,
            "success_rate": round(self.success_rate, 2),
            "total_companies": self.total_companies,
            "unique_companies": self.unique_companies,
            "avg_duration_seconds": round(self.avg_duration_seconds, 2),
            "total_cost": round(self.total_cost, 4),
            "avg_cost": round(self.avg_cost, 4),
            "period": self.period
        }


@dataclass
class AgentStats:
    """Statistics for an agent."""
    agent_name: str
    call_count: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    total_tokens: int = 0
    avg_tokens: float = 0.0
    total_cost: float = 0.0
    success_rate: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "call_count": self.call_count,
            "avg_duration": round(self.avg_duration, 2),
            "avg_tokens": round(self.avg_tokens, 0),
            "total_cost": round(self.total_cost, 4),
            "success_rate": round(self.success_rate, 2)
        }


@dataclass
class TrendPoint:
    """A single point in a trend."""
    timestamp: datetime
    value: float
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": round(self.value, 4),
            "label": self.label
        }


@dataclass
class DashboardData:
    """Complete dashboard data."""
    usage: UsageStats
    agent_stats: List[AgentStats]
    cost_trend: List[TrendPoint]
    research_trend: List[TrendPoint]
    top_companies: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "usage": self.usage.to_dict(),
            "agent_stats": [a.to_dict() for a in self.agent_stats],
            "cost_trend": [t.to_dict() for t in self.cost_trend],
            "research_trend": [t.to_dict() for t in self.research_trend],
            "top_companies": self.top_companies,
            "performance_summary": self.performance_summary,
            "alerts": self.alerts,
            "generated_at": self.generated_at.isoformat()
        }


# ============================================================================
# Analytics Aggregator
# ============================================================================

class AnalyticsAggregator:
    """
    Aggregate and analyze operational data.

    Features:
    - Usage statistics
    - Agent performance analysis
    - Cost trends
    - Dashboard data generation

    Usage:
        aggregator = AnalyticsAggregator()

        # Record events
        aggregator.record_research_completed(
            company_name="Tesla",
            duration=45.2,
            cost=0.05,
            agent_stats=agent_data
        )

        # Get analytics
        usage = aggregator.get_usage_stats(TimeRange.DAY)
        dashboard = aggregator.get_dashboard_data()
    """

    def __init__(self):
        """Initialize analytics aggregator."""
        # Raw event storage
        self._research_events: List[Dict[str, Any]] = []
        self._agent_events: List[Dict[str, Any]] = []
        self._cost_events: List[Dict[str, Any]] = []

        # Company tracking
        self._company_research_counts: Dict[str, int] = {}

    # ==========================================================================
    # Event Recording
    # ==========================================================================

    def record_research_completed(
        self,
        company_name: str,
        duration_seconds: float,
        cost: float,
        depth: str = "standard",
        agent_stats: Optional[Dict[str, Any]] = None
    ):
        """Record a completed research."""
        event = {
            "type": "completed",
            "company_name": company_name,
            "duration": duration_seconds,
            "cost": cost,
            "depth": depth,
            "timestamp": utc_now()
        }

        self._research_events.append(event)
        self._company_research_counts[company_name] = (
            self._company_research_counts.get(company_name, 0) + 1
        )

        # Record agent stats
        if agent_stats:
            for agent_name, stats in agent_stats.items():
                self._agent_events.append({
                    "agent_name": agent_name,
                    "duration": stats.get("duration", 0),
                    "tokens": stats.get("tokens", 0),
                    "cost": stats.get("cost", 0),
                    "success": stats.get("success", True),
                    "timestamp": utc_now()
                })

        # Record cost
        self._cost_events.append({
            "amount": cost,
            "timestamp": utc_now()
        })

    def record_research_failed(
        self,
        company_name: str,
        error: str,
        duration_seconds: float = 0
    ):
        """Record a failed research."""
        event = {
            "type": "failed",
            "company_name": company_name,
            "error": error,
            "duration": duration_seconds,
            "timestamp": utc_now()
        }
        self._research_events.append(event)

    # ==========================================================================
    # Usage Statistics
    # ==========================================================================

    def get_usage_stats(
        self,
        time_range: TimeRange = TimeRange.DAY
    ) -> UsageStats:
        """Get usage statistics for a time range."""
        cutoff = self._get_cutoff(time_range)
        events = [e for e in self._research_events if e["timestamp"] >= cutoff]

        stats = UsageStats(period=time_range.value)
        stats.total_researches = len(events)
        stats.completed = sum(1 for e in events if e["type"] == "completed")
        stats.failed = sum(1 for e in events if e["type"] == "failed")

        companies = [e["company_name"] for e in events]
        stats.total_companies = len(companies)
        stats.unique_companies = len(set(companies))

        completed_events = [e for e in events if e["type"] == "completed"]
        if completed_events:
            durations = [e["duration"] for e in completed_events]
            costs = [e["cost"] for e in completed_events]
            stats.avg_duration_seconds = statistics.mean(durations)
            stats.total_cost = sum(costs)
            stats.avg_cost = statistics.mean(costs)

        return stats

    def _get_cutoff(self, time_range: TimeRange) -> datetime:
        """Get cutoff datetime for time range."""
        now = utc_now()
        if time_range == TimeRange.HOUR:
            return now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            return now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            return now - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            return now - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return now - timedelta(days=90)
        return now - timedelta(days=1)

    # ==========================================================================
    # Agent Statistics
    # ==========================================================================

    def get_agent_stats(
        self,
        time_range: TimeRange = TimeRange.DAY
    ) -> List[AgentStats]:
        """Get statistics for all agents."""
        cutoff = self._get_cutoff(time_range)
        events = [e for e in self._agent_events if e["timestamp"] >= cutoff]

        # Group by agent
        by_agent: Dict[str, List[Dict]] = {}
        for event in events:
            name = event["agent_name"]
            if name not in by_agent:
                by_agent[name] = []
            by_agent[name].append(event)

        # Calculate stats
        stats = []
        for agent_name, agent_events in by_agent.items():
            durations = [e["duration"] for e in agent_events]
            tokens = [e["tokens"] for e in agent_events]
            costs = [e["cost"] for e in agent_events]
            successes = sum(1 for e in agent_events if e["success"])

            stats.append(AgentStats(
                agent_name=agent_name,
                call_count=len(agent_events),
                total_duration=sum(durations),
                avg_duration=statistics.mean(durations) if durations else 0,
                total_tokens=sum(tokens),
                avg_tokens=statistics.mean(tokens) if tokens else 0,
                total_cost=sum(costs),
                success_rate=successes / len(agent_events) if agent_events else 1.0
            ))

        # Sort by call count
        stats.sort(key=lambda s: s.call_count, reverse=True)
        return stats

    # ==========================================================================
    # Trends
    # ==========================================================================

    def get_cost_trend(
        self,
        time_range: TimeRange = TimeRange.WEEK,
        interval: str = "day"
    ) -> List[TrendPoint]:
        """Get cost trend over time."""
        cutoff = self._get_cutoff(time_range)
        events = [e for e in self._cost_events if e["timestamp"] >= cutoff]

        # Group by interval
        points = self._group_by_interval(
            events,
            interval,
            value_key="amount"
        )

        return [
            TrendPoint(timestamp=ts, value=val, label=interval)
            for ts, val in points.items()
        ]

    def get_research_trend(
        self,
        time_range: TimeRange = TimeRange.WEEK,
        interval: str = "day"
    ) -> List[TrendPoint]:
        """Get research count trend over time."""
        cutoff = self._get_cutoff(time_range)
        events = [e for e in self._research_events if e["timestamp"] >= cutoff]

        # Group by interval
        counts: Dict[datetime, int] = {}
        for event in events:
            key = self._get_interval_key(event["timestamp"], interval)
            counts[key] = counts.get(key, 0) + 1

        return [
            TrendPoint(timestamp=ts, value=float(count), label=interval)
            for ts, count in sorted(counts.items())
        ]

    def _group_by_interval(
        self,
        events: List[Dict],
        interval: str,
        value_key: str
    ) -> Dict[datetime, float]:
        """Group events by time interval."""
        grouped: Dict[datetime, float] = {}

        for event in events:
            key = self._get_interval_key(event["timestamp"], interval)
            grouped[key] = grouped.get(key, 0) + event.get(value_key, 0)

        return dict(sorted(grouped.items()))

    def _get_interval_key(self, timestamp: datetime, interval: str) -> datetime:
        """Get interval key for a timestamp."""
        if interval == "hour":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif interval == "day":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif interval == "week":
            days_since_monday = timestamp.weekday()
            return (timestamp - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    # ==========================================================================
    # Top Companies
    # ==========================================================================

    def get_top_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most researched companies."""
        sorted_companies = sorted(
            self._company_research_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"company": company, "research_count": count}
            for company, count in sorted_companies[:limit]
        ]

    # ==========================================================================
    # Dashboard Data
    # ==========================================================================

    def get_dashboard_data(
        self,
        time_range: TimeRange = TimeRange.DAY
    ) -> DashboardData:
        """Get complete dashboard data."""
        return DashboardData(
            usage=self.get_usage_stats(time_range),
            agent_stats=self.get_agent_stats(time_range),
            cost_trend=self.get_cost_trend(TimeRange.WEEK, "day"),
            research_trend=self.get_research_trend(TimeRange.WEEK, "day"),
            top_companies=self.get_top_companies(10),
            performance_summary=self._get_performance_summary(),
            alerts=self._get_active_alerts()
        )

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self._research_events:
            return {"status": "no_data"}

        completed = [e for e in self._research_events if e["type"] == "completed"]
        if not completed:
            return {"status": "no_completed_research"}

        durations = [e["duration"] for e in completed]

        return {
            "avg_duration": round(statistics.mean(durations), 2),
            "min_duration": round(min(durations), 2),
            "max_duration": round(max(durations), 2),
            "total_researches": len(self._research_events)
        }

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts (placeholder)."""
        alerts = []

        # Check for high failure rate
        stats = self.get_usage_stats(TimeRange.HOUR)
        if stats.success_rate < 0.9 and stats.total_researches > 5:
            alerts.append({
                "type": "high_failure_rate",
                "severity": "warning",
                "message": f"High failure rate: {1 - stats.success_rate:.1%}"
            })

        return alerts


# ============================================================================
# Convenience Functions
# ============================================================================

_global_aggregator: Optional[AnalyticsAggregator] = None


def get_analytics_aggregator() -> AnalyticsAggregator:
    """Get global analytics aggregator."""
    global _global_aggregator
    if _global_aggregator is None:
        _global_aggregator = AnalyticsAggregator()
    return _global_aggregator


def get_dashboard_data(time_range: TimeRange = TimeRange.DAY) -> Dict[str, Any]:
    """Get dashboard data from global aggregator."""
    return get_analytics_aggregator().get_dashboard_data(time_range).to_dict()


def create_analytics_aggregator() -> AnalyticsAggregator:
    """Create a new analytics aggregator."""
    return AnalyticsAggregator()
