"""
Audit Logging Package.

This package provides audit logging for security and compliance with:
- Structured audit logs
- Event categorization
- Compliance-ready logging
- Log export and querying

Modules:
    - models: Data models (AuditEventType, AuditSeverity, AuditEntry, AuditConfig)
    - logger: AuditLogger class with logging methods

Usage:
    from company_researcher.security.audit import (
        AuditLogger,
        AuditEventType,
        get_security_audit_logger,
        log_rate_limit_exceeded,
    )

    # Use singleton logger
    audit = get_security_audit_logger()
    audit.log_auth(user_id="user123", event=AuditEventType.LOGIN)

    # Or create custom logger
    audit = AuditLogger(log_file="audit.log")
"""

import threading
from typing import Any, Dict, Optional

from .models import (
    _utcnow,
    AuditEventType,
    AuditSeverity,
    AuditEntry,
    AuditConfig,
)
from .logger import AuditLogger

# Re-export all public APIs
__all__ = [
    # Models
    "_utcnow",
    "AuditEventType",
    "AuditSeverity",
    "AuditEntry",
    "AuditConfig",
    # Logger
    "AuditLogger",
    # Factory functions
    "create_audit_logger",
    "get_security_audit_logger",
    # Convenience logging functions
    "log_action",
    "log_rate_limit_exceeded",
    "log_rate_limit_ban",
    "log_input_validation_failed",
    "log_ssrf_blocked",
    "log_request_size_exceeded",
    "log_websocket_blocked",
    "log_authentication_failed",
    "log_authorization_denied",
    "log_suspicious_activity",
]


# ============================================================================
# Factory Functions
# ============================================================================

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
