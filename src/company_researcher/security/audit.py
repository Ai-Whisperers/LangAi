"""
Audit Logging - Security event tracking.

This module provides security and compliance audit logging with:
- Structured audit logs
- Event categorization (30+ event types)
- Compliance-ready logging
- Log export and querying
- Decorator for automatic function auditing

Modules:
    - audit.models: Data models (AuditEventType, AuditSeverity, AuditEntry, AuditConfig)
    - audit.logger: AuditLogger class with logging and querying methods
    - audit.__init__: Convenience functions and singleton pattern

Usage:
    from company_researcher.security.audit import (
        AuditLogger,
        AuditEventType,
        AuditSeverity,
        get_security_audit_logger,
        log_rate_limit_exceeded,
    )

    # Use singleton logger
    audit = get_security_audit_logger()
    audit.log_auth(user_id="user123", event=AuditEventType.LOGIN)

    # Or create custom logger
    audit = AuditLogger(log_file="audit.log")

    # Use convenience functions
    log_rate_limit_exceeded(key="user123", limit=100, ip_address="192.168.1.1")

    # Use decorator
    @audit.audited(event_type=AuditEventType.DATA_READ)
    def get_data(user_id, company):
        ...
"""

import logging

# Import from audit package
from .audit import (  # Models; Logger; Factory functions; Convenience logging functions
    AuditConfig,
    AuditEntry,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
    _utcnow,
    create_audit_logger,
    get_security_audit_logger,
    log_action,
    log_authentication_failed,
    log_authorization_denied,
    log_input_validation_failed,
    log_rate_limit_ban,
    log_rate_limit_exceeded,
    log_request_size_exceeded,
    log_ssrf_blocked,
    log_suspicious_activity,
    log_websocket_blocked,
)

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


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create audit logger
    audit = get_security_audit_logger(log_file="logs/demo_audit.log")

    print("Audit Logging Demo")
    print("=" * 50)

    # Test authentication events
    print("\n1. Testing authentication events...")
    audit.log_auth(user_id="demo_user", event=AuditEventType.LOGIN, ip_address="192.168.1.100")

    log_authentication_failed(
        username="bad_user", reason="Invalid password", ip_address="192.168.1.101"
    )

    # Test data access events
    print("2. Testing data access events...")
    audit.log_data_access(
        user_id="demo_user",
        action="read",
        resource="research",
        resource_id="Tesla",
        details={"query": "financial data"},
    )

    # Test security events
    print("3. Testing security events...")
    log_rate_limit_exceeded(
        key="user:demo_user", limit=100, user_id="demo_user", ip_address="192.168.1.100"
    )

    log_ssrf_blocked(
        url="http://169.254.169.254/latest/meta-data/",
        reason="Blocked internal IP",
        user_id="demo_user",
        ip_address="192.168.1.100",
    )

    # Test research operations
    print("4. Testing research operations...")
    audit.log_research(
        user_id="demo_user",
        company="Apple Inc.",
        event=AuditEventType.RESEARCH_START,
        details={"research_type": "comprehensive"},
    )

    audit.log_research(
        user_id="demo_user",
        company="Apple Inc.",
        event=AuditEventType.RESEARCH_COMPLETE,
        outcome="success",
        details={"duration_seconds": 45.2, "sources": 12},
    )

    # Query logs
    print("\n5. Querying audit logs...")
    recent = audit.get_recent(limit=10)
    print(f"Total recent entries: {len(recent)}")

    user_activity = audit.get_user_activity("demo_user")
    print(f"Entries for demo_user: {len(user_activity)}")

    security_events = audit.query(resource="security", severity=AuditSeverity.WARNING)
    print(f"Security warnings: {len(security_events)}")

    # Export logs
    print("\n6. Exporting audit logs...")
    count = audit.export("logs/demo_audit_export.jsonl")
    print(f"Exported {count} entries to logs/demo_audit_export.jsonl")

    # Test decorator
    print("\n7. Testing decorator...")

    @audit.audited(event_type=AuditEventType.DATA_READ)
    def get_research(user_id: str, company: str):
        print(f"  Getting research for {company} (user: {user_id})")
        return {"company": company, "data": "..."}

    result = get_research(user_id="demo_user", company="Microsoft")

    print("\n" + "=" * 50)
    print("Demo completed. Check logs/demo_audit.log for details.")
    print("\nKey Features Demonstrated:")
    print("  ✓ Authentication event logging")
    print("  ✓ Data access event logging")
    print("  ✓ Security event logging")
    print("  ✓ Research operation logging")
    print("  ✓ Audit log querying")
    print("  ✓ Audit log export")
    print("  ✓ Function call decorator")


# NOTE: Old implementation has been moved to the audit/ package
# This file now serves as a backward-compatible entry point
# The actual implementation is in:
# - audit/models.py: Data models and enums
# - audit/logger.py: AuditLogger class with logging methods
# - audit/__init__.py: Package exports and convenience functions
