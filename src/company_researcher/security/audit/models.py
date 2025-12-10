"""
Audit Models and Data Structures.

This module contains all data models for the audit logging system:
- AuditEventType enum
- AuditSeverity enum
- AuditEntry dataclass
- AuditConfig dataclass
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_ISSUED = "auth.token_issued"
    TOKEN_REVOKED = "auth.token_revoked"

    # Authorization
    ACCESS_GRANTED = "authz.access_granted"
    ACCESS_DENIED = "authz.access_denied"
    PERMISSION_CHANGED = "authz.permission_changed"

    # Data Access
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"

    # Research Operations
    RESEARCH_START = "research.start"
    RESEARCH_COMPLETE = "research.complete"
    RESEARCH_FAILED = "research.failed"

    # Administration
    CONFIG_CHANGED = "admin.config_changed"
    USER_CREATED = "admin.user_created"
    USER_MODIFIED = "admin.user_modified"
    USER_DELETED = "admin.user_deleted"

    # Security
    SECURITY_ALERT = "security.alert"
    SENSITIVE_ACCESS = "security.sensitive_access"
    REDACTION_APPLIED = "security.redaction"
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    RATE_LIMIT_BAN = "security.rate_limit_ban"
    INPUT_VALIDATION_FAILED = "security.input_validation_failed"
    SSRF_ATTEMPT_BLOCKED = "security.ssrf_blocked"
    REQUEST_SIZE_EXCEEDED = "security.request_size_exceeded"
    WEBSOCKET_MESSAGE_BLOCKED = "security.websocket_blocked"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"

    # System
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    ERROR = "system.error"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """
    A single audit log entry.

    Follows structured logging best practices for compliance.
    """
    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str] = None
    action: str = ""
    resource: str = ""
    resource_id: Optional[str] = None
    outcome: str = "success"  # success, failure, error
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "outcome": self.outcome,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "request_id": self.request_id
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Create from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        else:
            timestamp = _utcnow()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp,
            event_type=AuditEventType(data.get("event_type", "system.error")),
            severity=AuditSeverity(data.get("severity", "info")),
            user_id=data.get("user_id"),
            action=data.get("action", ""),
            resource=data.get("resource", ""),
            resource_id=data.get("resource_id"),
            outcome=data.get("outcome", "success"),
            details=data.get("details", {}),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            session_id=data.get("session_id"),
            request_id=data.get("request_id")
        )


@dataclass
class AuditConfig:
    """Configuration for audit logging."""
    enabled: bool = True
    log_file: Optional[str] = None
    log_to_console: bool = False
    min_severity: AuditSeverity = AuditSeverity.INFO
    include_details: bool = True
    max_entries: int = 10000  # In-memory limit
    retention_days: int = 90
