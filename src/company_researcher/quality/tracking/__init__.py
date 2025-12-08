"""
Quality Tracking Module.

Provides source and audit tracking:
- Source tracking
- Freshness tracking
- Audit trail
"""

from .source_tracker import (
    SourceTracker,
    TrackedSource,
    SourceUsage,
)

from .freshness_tracker import (
    FreshnessTracker,
    FreshnessScore,
    DataFreshness,
)

from .audit_trail import (
    AuditTrail,
    AuditEvent,
    AuditEventType,
)

__all__ = [
    # Source tracking
    "SourceTracker",
    "TrackedSource",
    "SourceUsage",
    # Freshness tracking
    "FreshnessTracker",
    "FreshnessScore",
    "DataFreshness",
    # Audit trail
    "AuditTrail",
    "AuditEvent",
    "AuditEventType",
]
