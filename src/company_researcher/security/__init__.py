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

from .jwt_auth import (
    JWTManager,
    JWTConfig,
    TokenPayload,
    create_jwt_manager,
    decode_token,
    encode_token,
)

from .rbac import (
    RBACManager,
    Role,
    Permission,
    User,
    create_rbac_manager,
    check_permission,
)

from .redaction import (
    ContentRedactor,
    RedactionPattern,
    RedactionConfig,
    redact_text,
    redact_dict,
)

from .audit import (
    AuditLogger,
    AuditEntry,
    AuditConfig,
    create_audit_logger,
    log_action,
)

from .sanitization import (
    InputSanitizer,
    sanitize_input,
    sanitize_html,
    sanitize_sql,
    escape_special_chars,
)

from .rate_limit import (
    RateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
    create_rate_limiter,
)

__all__ = [
    # JWT
    "JWTManager",
    "JWTConfig",
    "TokenPayload",
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
    "create_audit_logger",
    "log_action",
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
