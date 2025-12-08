"""
Audit Logging - Security event tracking.

Provides:
- Structured audit logs
- Event categorization
- Compliance-ready logging
- Log export and querying
"""

import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


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


class AuditLogger:
    """
    Audit logging for security and compliance.

    Usage:
        audit = AuditLogger(log_file="audit.log")

        # Log authentication
        audit.log_auth(user_id="user123", event=AuditEventType.LOGIN)

        # Log data access
        audit.log_data_access(
            user_id="user123",
            action="read",
            resource="research",
            resource_id="Tesla"
        )

        # Log with decorator
        @audit.audited(event_type=AuditEventType.DATA_READ)
        def get_research(user_id, company):
            ...

        # Query logs
        entries = audit.query(user_id="user123", event_type=AuditEventType.LOGIN)
    """

    def __init__(
        self,
        config: AuditConfig = None,
        log_file: str = None
    ):
        self.config = config or AuditConfig(log_file=log_file)
        self._entries: List[AuditEntry] = []
        self._lock = threading.RLock()
        self._handlers: List[Callable[[AuditEntry], None]] = []
        self._logger = logging.getLogger("audit")

        if self.config.log_file:
            self._setup_file_handler()

        if self.config.log_to_console:
            self._setup_console_handler()

    def _setup_file_handler(self) -> None:
        """Setup file handler for audit logs."""
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(str(log_path))
        handler.setFormatter(logging.Formatter('%(message)s'))
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    def _setup_console_handler(self) -> None:
        """Setup console handler for audit logs."""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[AUDIT] %(message)s'
        ))
        self._logger.addHandler(handler)

    def log(
        self,
        event_type: AuditEventType,
        user_id: str = None,
        action: str = "",
        resource: str = "",
        resource_id: str = None,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.INFO,
        details: Dict[str, Any] = None,
        **kwargs
    ) -> AuditEntry:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            user_id: User who performed the action
            action: Action performed
            resource: Resource type affected
            resource_id: Specific resource identifier
            outcome: success, failure, or error
            severity: Event severity
            details: Additional details
            **kwargs: Additional fields (ip_address, user_agent, etc.)

        Returns:
            Created AuditEntry
        """
        if not self.config.enabled:
            return None

        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=_utcnow(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            outcome=outcome,
            details=details or {},
            **kwargs
        )

        self._store_entry(entry)
        self._notify_handlers(entry)

        return entry

    def _store_entry(self, entry: AuditEntry) -> None:
        """Store entry in memory and file."""
        with self._lock:
            self._entries.append(entry)

            # Enforce max entries
            if len(self._entries) > self.config.max_entries:
                self._entries = self._entries[-self.config.max_entries:]

        # Log to file
        if self.config.log_file:
            self._logger.info(entry.to_json())

    def _notify_handlers(self, entry: AuditEntry) -> None:
        """Notify registered handlers."""
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception as e:
                # Log but don't let handler errors break audit logging
                self._logger.warning(f"Audit handler error: {e}")

    def add_handler(self, handler: Callable[[AuditEntry], None]) -> None:
        """Add a custom audit handler."""
        self._handlers.append(handler)

    # Convenience logging methods

    def log_auth(
        self,
        user_id: str,
        event: AuditEventType,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log authentication event."""
        severity = AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING
        return self.log(
            event_type=event,
            user_id=user_id,
            action=event.value.split(".")[-1],
            resource="auth",
            outcome=outcome,
            severity=severity,
            **kwargs
        )

    def log_data_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        resource_id: str = None,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log data access event."""
        event_map = {
            "read": AuditEventType.DATA_READ,
            "create": AuditEventType.DATA_CREATE,
            "update": AuditEventType.DATA_UPDATE,
            "delete": AuditEventType.DATA_DELETE,
            "export": AuditEventType.DATA_EXPORT
        }
        event_type = event_map.get(action.lower(), AuditEventType.DATA_READ)

        return self.log(
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            outcome=outcome,
            **kwargs
        )

    def log_research(
        self,
        user_id: str,
        company: str,
        event: AuditEventType,
        outcome: str = "success",
        **kwargs
    ) -> AuditEntry:
        """Log research operation."""
        return self.log(
            event_type=event,
            user_id=user_id,
            action=event.value.split(".")[-1],
            resource="research",
            resource_id=company,
            outcome=outcome,
            **kwargs
        )

    def log_security(
        self,
        event: AuditEventType,
        severity: AuditSeverity = AuditSeverity.WARNING,
        user_id: str = None,
        **kwargs
    ) -> AuditEntry:
        """Log security event."""
        return self.log(
            event_type=event,
            severity=severity,
            user_id=user_id,
            resource="security",
            **kwargs
        )

    # Query methods

    def query(
        self,
        user_id: str = None,
        event_type: AuditEventType = None,
        resource: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        severity: AuditSeverity = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit logs.

        Args:
            user_id: Filter by user
            event_type: Filter by event type
            resource: Filter by resource
            start_time: Filter by start time
            end_time: Filter by end time
            severity: Filter by minimum severity
            limit: Maximum entries to return

        Returns:
            List of matching AuditEntry objects
        """
        with self._lock:
            results = []
            severity_order = list(AuditSeverity)

            for entry in reversed(self._entries):
                if len(results) >= limit:
                    break

                if user_id and entry.user_id != user_id:
                    continue
                if event_type and entry.event_type != event_type:
                    continue
                if resource and entry.resource != resource:
                    continue
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                if severity:
                    if severity_order.index(entry.severity) < severity_order.index(severity):
                        continue

                results.append(entry)

            return results

    def get_user_activity(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[AuditEntry]:
        """Get activity for a specific user."""
        return self.query(user_id=user_id, limit=limit)

    def get_recent(self, limit: int = 100) -> List[AuditEntry]:
        """Get most recent audit entries."""
        with self._lock:
            return list(reversed(self._entries[-limit:]))

    def export(self, filepath: str) -> int:
        """Export audit logs to file."""
        with self._lock:
            with open(filepath, 'w') as f:
                for entry in self._entries:
                    f.write(entry.to_json() + "\n")
            return len(self._entries)

    # Decorator

    def audited(
        self,
        event_type: AuditEventType,
        resource: str = None,
        include_args: bool = False
    ) -> Callable:
        """
        Decorator to automatically audit function calls.

        Usage:
            @audit.audited(event_type=AuditEventType.DATA_READ)
            def get_data(user_id, company):
                ...
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                user_id = kwargs.get('user_id') or (args[0] if args else None)
                details = {}

                if include_args:
                    details['args'] = str(args)
                    details['kwargs'] = str(kwargs)

                try:
                    result = func(*args, **kwargs)
                    self.log(
                        event_type=event_type,
                        user_id=str(user_id) if user_id else None,
                        action=func.__name__,
                        resource=resource or func.__name__,
                        outcome="success",
                        details=details
                    )
                    return result
                except Exception as e:
                    details['error'] = str(e)
                    self.log(
                        event_type=event_type,
                        user_id=str(user_id) if user_id else None,
                        action=func.__name__,
                        resource=resource or func.__name__,
                        outcome="error",
                        severity=AuditSeverity.ERROR,
                        details=details
                    )
                    raise

            return wrapper
        return decorator


# Convenience functions


def create_audit_logger(
    log_file: str = None,
    config: AuditConfig = None
) -> AuditLogger:
    """Create an audit logger."""
    return AuditLogger(config=config, log_file=log_file)


def log_action(
    audit: AuditLogger,
    user_id: str,
    action: str,
    resource: str,
    **kwargs
) -> AuditEntry:
    """Quick action logging."""
    event_type = AuditEventType.DATA_READ  # Default
    if "create" in action.lower():
        event_type = AuditEventType.DATA_CREATE
    elif "update" in action.lower() or "edit" in action.lower():
        event_type = AuditEventType.DATA_UPDATE
    elif "delete" in action.lower():
        event_type = AuditEventType.DATA_DELETE

    return audit.log(
        event_type=event_type,
        user_id=user_id,
        action=action,
        resource=resource,
        **kwargs
    )


# ============================================================================
# Global Security Audit Logger Singleton
# ============================================================================

_security_audit_logger: Optional[AuditLogger] = None
_security_audit_lock = threading.Lock()


def get_security_audit_logger(
    log_file: str = "logs/security_audit.log"
) -> AuditLogger:
    """
    Get the global security audit logger singleton.

    Thread-safe singleton pattern for application-wide security logging.

    Args:
        log_file: Path to audit log file (only used on first call)

    Returns:
        Shared AuditLogger instance
    """
    global _security_audit_logger

    if _security_audit_logger is None:
        with _security_audit_lock:
            if _security_audit_logger is None:
                config = AuditConfig(
                    enabled=True,
                    log_file=log_file,
                    log_to_console=False,
                    min_severity=AuditSeverity.INFO,
                    include_details=True,
                    max_entries=10000,
                    retention_days=90
                )
                _security_audit_logger = AuditLogger(config=config)

    return _security_audit_logger


# ============================================================================
# Security Event Logging Convenience Functions
# ============================================================================

def log_rate_limit_exceeded(
    key: str,
    limit: int,
    ip_address: str = None,
    user_id: str = None,
    **kwargs
) -> AuditEntry:
    """Log rate limit exceeded event."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
        severity=AuditSeverity.WARNING,
        user_id=user_id,
        action="rate_limit_check",
        resource="rate_limiter",
        resource_id=key,
        outcome="failure",
        details={"limit": limit, "key_type": "user" if user_id else "ip"},
        ip_address=ip_address,
        **kwargs
    )


def log_rate_limit_ban(
    key: str,
    violations: int,
    ip_address: str = None,
    user_id: str = None,
    **kwargs
) -> AuditEntry:
    """Log rate limit ban event."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.RATE_LIMIT_BAN,
        severity=AuditSeverity.ERROR,
        user_id=user_id,
        action="rate_limit_ban",
        resource="rate_limiter",
        resource_id=key,
        outcome="failure",
        details={"violations": violations},
        ip_address=ip_address,
        **kwargs
    )


def log_input_validation_failed(
    field: str,
    reason: str,
    ip_address: str = None,
    user_id: str = None,
    request_id: str = None,
    **kwargs
) -> AuditEntry:
    """Log input validation failure."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.INPUT_VALIDATION_FAILED,
        severity=AuditSeverity.WARNING,
        user_id=user_id,
        action="input_validation",
        resource="api",
        outcome="failure",
        details={"field": field, "reason": reason},
        ip_address=ip_address,
        request_id=request_id,
        **kwargs
    )


def log_ssrf_blocked(
    url: str,
    reason: str,
    ip_address: str = None,
    user_id: str = None,
    **kwargs
) -> AuditEntry:
    """Log blocked SSRF attempt."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.SSRF_ATTEMPT_BLOCKED,
        severity=AuditSeverity.ERROR,
        user_id=user_id,
        action="ssrf_check",
        resource="url_validator",
        outcome="blocked",
        details={"url": url, "reason": reason},
        ip_address=ip_address,
        **kwargs
    )


def log_request_size_exceeded(
    content_length: int,
    max_size: int,
    content_type: str = None,
    ip_address: str = None,
    **kwargs
) -> AuditEntry:
    """Log request size limit exceeded."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.REQUEST_SIZE_EXCEEDED,
        severity=AuditSeverity.WARNING,
        action="request_size_check",
        resource="api",
        outcome="blocked",
        details={
            "content_length": content_length,
            "max_size": max_size,
            "content_type": content_type
        },
        ip_address=ip_address,
        **kwargs
    )


def log_websocket_blocked(
    connection_id: str,
    reason: str,
    message_type: str = None,
    ip_address: str = None,
    **kwargs
) -> AuditEntry:
    """Log blocked WebSocket message."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.WEBSOCKET_MESSAGE_BLOCKED,
        severity=AuditSeverity.WARNING,
        action="websocket_message",
        resource="websocket",
        resource_id=connection_id,
        outcome="blocked",
        details={"reason": reason, "message_type": message_type},
        ip_address=ip_address,
        **kwargs
    )


def log_authentication_failed(
    username: str = None,
    reason: str = None,
    ip_address: str = None,
    **kwargs
) -> AuditEntry:
    """Log failed authentication attempt."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.LOGIN_FAILED,
        severity=AuditSeverity.WARNING,
        user_id=username,
        action="login",
        resource="auth",
        outcome="failure",
        details={"reason": reason} if reason else {},
        ip_address=ip_address,
        **kwargs
    )


def log_authorization_denied(
    user_id: str,
    resource: str,
    action: str,
    required_permission: str = None,
    ip_address: str = None,
    **kwargs
) -> AuditEntry:
    """Log authorization denial."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.ACCESS_DENIED,
        severity=AuditSeverity.WARNING,
        user_id=user_id,
        action=action,
        resource=resource,
        outcome="denied",
        details={"required_permission": required_permission} if required_permission else {},
        ip_address=ip_address,
        **kwargs
    )


def log_suspicious_activity(
    description: str,
    severity: AuditSeverity = AuditSeverity.WARNING,
    user_id: str = None,
    ip_address: str = None,
    details: Dict[str, Any] = None,
    **kwargs
) -> AuditEntry:
    """Log suspicious activity detected."""
    audit = get_security_audit_logger()
    return audit.log(
        event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
        severity=severity,
        user_id=user_id,
        action="security_check",
        resource="security",
        outcome="alert",
        details={"description": description, **(details or {})},
        ip_address=ip_address,
        **kwargs
    )
