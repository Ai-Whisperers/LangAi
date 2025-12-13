"""
Data models for API quota tracking.

This module contains:
- QuotaStatus: Enum for quota check status
- QuotaInfo: Information for a single API's quota
- QuotaReport: Complete report for all APIs
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from ...utils import utc_now


class QuotaStatus(Enum):
    """Quota check status."""
    OK = "ok"                    # Has remaining quota
    LOW = "low"                  # Below 20% remaining
    EXHAUSTED = "exhausted"     # No quota remaining
    UNKNOWN = "unknown"         # Couldn't determine quota
    ERROR = "error"             # API error
    NO_KEY = "no_key"           # API key not configured


@dataclass
class QuotaInfo:
    """Quota information for a single API."""
    api_name: str
    status: QuotaStatus

    # Quota details
    used: Optional[int] = None
    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset_at: Optional[datetime] = None
    period: Optional[str] = None  # daily, monthly, minute, etc.

    # Credit-based APIs
    credits_used: Optional[float] = None
    credits_remaining: Optional[float] = None
    credits_total: Optional[float] = None

    # Account info
    plan_name: Optional[str] = None
    account_email: Optional[str] = None

    # Rate limit headers
    rate_limit: Optional[int] = None
    rate_remaining: Optional[int] = None
    rate_reset: Optional[int] = None

    # Error info
    error_message: Optional[str] = None

    # Raw response
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @property
    def usage_percent(self) -> Optional[float]:
        """Calculate usage percentage."""
        if self.limit and self.limit > 0:
            if self.used is not None:
                return (self.used / self.limit) * 100
            elif self.remaining is not None:
                return ((self.limit - self.remaining) / self.limit) * 100
        if self.credits_total and self.credits_total > 0 and self.credits_used is not None:
            return (self.credits_used / self.credits_total) * 100
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "api_name": self.api_name,
            "status": self.status.value,
            "used": self.used,
            "limit": self.limit,
            "remaining": self.remaining,
            "usage_percent": round(self.usage_percent, 1) if self.usage_percent else None,
            "reset_at": self.reset_at.isoformat() if self.reset_at else None,
            "period": self.period,
            "credits_used": self.credits_used,
            "credits_remaining": self.credits_remaining,
            "credits_total": self.credits_total,
            "plan_name": self.plan_name,
            "rate_limit": self.rate_limit,
            "rate_remaining": self.rate_remaining,
            "error_message": self.error_message,
        }


@dataclass
class QuotaReport:
    """Complete quota report for all APIs."""
    timestamp: datetime = field(default_factory=utc_now)
    apis: List[QuotaInfo] = field(default_factory=list)

    def add(self, info: QuotaInfo):
        """Add API quota info."""
        self.apis.append(info)

    @property
    def summary(self) -> Dict[str, int]:
        """Get status summary."""
        counts = {s.value: 0 for s in QuotaStatus}
        for api in self.apis:
            counts[api.status.value] += 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "apis": [api.to_dict() for api in self.apis]
        }

    def to_string(self, show_raw: bool = False) -> str:
        """Format as readable string."""
        lines = [
            "=" * 70,
            "API QUOTA & BALANCE REPORT",
            f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            ""
        ]

        # Group by status
        status_order = [QuotaStatus.EXHAUSTED, QuotaStatus.LOW, QuotaStatus.ERROR,
                       QuotaStatus.NO_KEY, QuotaStatus.OK, QuotaStatus.UNKNOWN]

        for status in status_order:
            apis = [a for a in self.apis if a.status == status]
            if not apis:
                continue

            status_icon = {
                QuotaStatus.OK: "[OK]",
                QuotaStatus.LOW: "[LOW]",
                QuotaStatus.EXHAUSTED: "[EMPTY]",
                QuotaStatus.ERROR: "[ERR]",
                QuotaStatus.NO_KEY: "[--]",
                QuotaStatus.UNKNOWN: "[?]"
            }.get(status, "[?]")

            lines.append(f"\n[{status_icon}] {status.value.upper()}")
            lines.append("-" * 40)

            for api in apis:
                lines.append(f"\n  {api.api_name}")

                if api.status == QuotaStatus.NO_KEY:
                    lines.append("    Key not configured")
                    continue

                if api.error_message:
                    lines.append(f"    Error: {api.error_message}")
                    continue

                # Show quota info
                if api.limit is not None:
                    used = api.used or (api.limit - (api.remaining or 0))
                    remaining = api.remaining or (api.limit - (api.used or 0))
                    pct = api.usage_percent or 0
                    lines.append(f"    Usage: {used:,}/{api.limit:,} ({pct:.1f}%)")
                    lines.append(f"    Remaining: {remaining:,}")
                    if api.period:
                        lines.append(f"    Period: {api.period}")
                    if api.reset_at:
                        lines.append(f"    Resets: {api.reset_at.strftime('%Y-%m-%d %H:%M')}")

                # Show credits
                if api.credits_remaining is not None:
                    if api.credits_total:
                        lines.append(f"    Credits: ${api.credits_remaining:.2f} / ${api.credits_total:.2f}")
                    else:
                        lines.append(f"    Credits: ${api.credits_remaining:.2f}")

                # Show plan
                if api.plan_name:
                    lines.append(f"    Plan: {api.plan_name}")

                # Show rate limits
                if api.rate_limit:
                    lines.append(f"    Rate: {api.rate_remaining or '?'}/{api.rate_limit} per window")

        # Summary
        lines.extend([
            "",
            "=" * 70,
            "SUMMARY",
            "-" * 40,
        ])

        summary = self.summary
        total = len(self.apis)
        lines.append(f"  Total APIs: {total}")
        lines.append(f"  [OK] Available: {summary['ok']}")
        lines.append(f"  [LOW] Low quota: {summary['low']}")
        lines.append(f"  [EMPTY] Exhausted: {summary['exhausted']}")
        lines.append(f"  [ERR] Error: {summary['error']}")
        lines.append(f"  [--] No Key: {summary['no_key']}")
        lines.append(f"  [?] Unknown: {summary['unknown']}")
        lines.append("=" * 70)

        return "\n".join(lines)
