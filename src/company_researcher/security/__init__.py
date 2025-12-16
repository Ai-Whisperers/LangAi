"""
Security Module for Company Researcher.

Provides comprehensive security features:
- JWT authentication and token management
- Role-Based Access Control (RBAC)
- Content redaction for sensitive data
- Audit logging
- Input sanitization
- Rate limiting

Usage:
    from src.company_researcher.security import (
        JWTManager,
        RBACManager,
        ContentRedactor,
        AuditLogger,
        RateLimiter,
        sanitize_input
    )

    # JWT authentication
    jwt = JWTManager(secret_key="your-secret")
    token = jwt.create_token(user_id="123", roles=["analyst"])
    claims = jwt.verify_token(token)

    # RBAC authorization
    rbac = RBACManager()
    rbac.add_role("analyst", permissions=["read:research", "write:notes"])
    if rbac.has_permission(user, "read:research"):
        # allow access

    # Content redaction
    redactor = ContentRedactor()
    safe_text = redactor.redact(text, patterns=["email", "phone", "ssn"])

    # Audit logging
    audit = AuditLogger()
    audit.log_action(user_id="123", action="research_access", resource="Tesla")
"""

from .audit import (  # Security audit singleton and convenience functions
    AuditConfig,
    AuditEntry,
    AuditEventType,
    AuditLogger,
    AuditSeverity,
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
from .jwt_auth import (
    ALLOWED_ALGORITHMS,
    MIN_KEY_LENGTHS,
    JWTConfig,
    JWTManager,
    JWTSecurityError,
    TokenPayload,
    create_jwt_manager,
    decode_token,
    encode_token,
    validate_secret_key,
)
from .rate_limit import RateLimitConfig, RateLimiter, RateLimitExceeded, create_rate_limiter
from .rbac import Permission, RBACManager, Role, User, check_permission, create_rbac_manager
from .redaction import ContentRedactor, RedactionConfig, RedactionPattern, redact_dict, redact_text
from .sanitization import (
    InputSanitizer,
    escape_special_chars,
    sanitize_html,
    sanitize_input,
    sanitize_sql,
)

__all__ = [
    # JWT
    "JWTManager",
    "JWTConfig",
    "TokenPayload",
    "JWTSecurityError",
    "validate_secret_key",
    "MIN_KEY_LENGTHS",
    "ALLOWED_ALGORITHMS",
    "create_jwt_manager",
    "decode_token",
    "encode_token",
    # RBAC
    "RBACManager",
    "Role",
    "Permission",
    "User",
    "create_rbac_manager",
    "check_permission",
    # Redaction
    "ContentRedactor",
    "RedactionPattern",
    "RedactionConfig",
    "redact_text",
    "redact_dict",
    # Audit
    "AuditLogger",
    "AuditEntry",
    "AuditConfig",
    "AuditEventType",
    "AuditSeverity",
    "create_audit_logger",
    "log_action",
    # Security audit singleton and convenience functions
    "get_security_audit_logger",
    "log_rate_limit_exceeded",
    "log_rate_limit_ban",
    "log_input_validation_failed",
    "log_ssrf_blocked",
    "log_request_size_exceeded",
    "log_websocket_blocked",
    "log_authentication_failed",
    "log_authorization_denied",
    "log_suspicious_activity",
    # Sanitization
    "InputSanitizer",
    "sanitize_input",
    "sanitize_html",
    "sanitize_sql",
    "escape_special_chars",
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitExceeded",
    "create_rate_limiter",
]
