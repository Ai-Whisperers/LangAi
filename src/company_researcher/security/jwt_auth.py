"""
JWT Authentication - Token-based authentication.

Provides:
- Token creation and verification
- Token refresh
- Claim management
- Expiration handling
"""

import base64
import hashlib
import hmac
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from ..utils import get_config, get_logger

logger = get_logger(__name__)


@dataclass
class TokenPayload:
    """JWT token payload (claims)."""
    sub: str  # Subject (user ID)
    iat: int  # Issued at
    exp: int  # Expiration
    jti: Optional[str] = None  # JWT ID
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sub": self.sub,
            "iat": self.iat,
            "exp": self.exp,
            "jti": self.jti,
            "roles": self.roles,
            "permissions": self.permissions,
            **self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenPayload":
        """Create from dictionary."""
        return cls(
            sub=data.get("sub", ""),
            iat=data.get("iat", 0),
            exp=data.get("exp", 0),
            jti=data.get("jti"),
            roles=data.get("roles", []),
            permissions=data.get("permissions", []),
            metadata={k: v for k, v in data.items()
                     if k not in ("sub", "iat", "exp", "jti", "roles", "permissions")}
        )

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return time.time() > self.exp


class JWTSecurityError(Exception):
    """Raised when JWT security requirements are not met."""


# Minimum key lengths (in bytes) for HMAC algorithms
MIN_KEY_LENGTHS = {
    "HS256": 32,  # 256 bits
    "HS384": 48,  # 384 bits
    "HS512": 64,  # 512 bits
}

# Allowed algorithms (security: explicitly allowlist to prevent algorithm confusion)
ALLOWED_ALGORITHMS = frozenset(["HS256", "HS384", "HS512"])

# Common weak/default secrets to reject
WEAK_SECRETS = frozenset([
    "secret", "password", "changeme", "your-secret-key",
    "secret-key", "supersecret", "change-me", "test",
    "development", "dev", "prod", "production",
])


def validate_secret_key(
    secret_key: str,
    algorithm: str = "HS256",
    strict: bool = True
) -> None:
    """
    Validate JWT secret key meets security requirements.

    Args:
        secret_key: The secret key to validate
        algorithm: The HMAC algorithm being used
        strict: If True, raise exception; if False, log warning

    Raises:
        JWTSecurityError: If key doesn't meet requirements in strict mode
    """

    logger = get_logger(__name__)
    issues = []

    # Check minimum length
    min_length = MIN_KEY_LENGTHS.get(algorithm, 32)
    if len(secret_key) < min_length:
        issues.append(
            f"Secret key too short for {algorithm}. "
            f"Minimum: {min_length} bytes, actual: {len(secret_key)} bytes"
        )

    # Check for weak/common secrets
    if secret_key.lower() in WEAK_SECRETS:
        issues.append(
            f"Secret key '{secret_key[:4]}...' is a known weak/default value. "
            "Use a cryptographically random key."
        )

    # Check for low entropy (simple patterns)
    if len(set(secret_key)) < 8:
        issues.append(
            "Secret key has very low entropy (few unique characters). "
            "Use a cryptographically random key."
        )

    # Check if it looks like an env var placeholder
    if secret_key.startswith("${") or secret_key.startswith("$"):
        issues.append(
            "Secret key appears to be an unresolved environment variable. "
            "Ensure JWT_SECRET_KEY environment variable is set."
        )

    # Log or raise issues
    if issues:
        message = "JWT security issues found:\n" + "\n".join(f"  - {issue}" for issue in issues)
        if strict and get_config("ENVIRONMENT", default="development") == "production":
            raise JWTSecurityError(message)
        else:
            logger.warning(message)


@dataclass
class JWTConfig:
    """JWT configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: Optional[str] = None
    audience: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        validate_secret_key(self.secret_key, self.algorithm, strict=False)


class JWTManager:
    """
    JWT token management.

    Usage:
        jwt = JWTManager(secret_key="your-secret-key")

        # Create token
        token = jwt.create_token(user_id="user123", roles=["analyst"])

        # Verify token
        payload = jwt.verify_token(token)

        # Refresh token
        new_token = jwt.refresh_token(token)
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        validate_key: bool = True
    ):
        # Security: Validate algorithm is in allowlist
        if algorithm not in ALLOWED_ALGORITHMS:
            raise JWTSecurityError(
                f"Algorithm '{algorithm}' not allowed. "
                f"Allowed algorithms: {', '.join(sorted(ALLOWED_ALGORITHMS))}"
            )

        # Validate secret key on initialization
        if validate_key:
            validate_secret_key(secret_key, algorithm, strict=False)

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_expire = timedelta(days=refresh_token_expire_days)
        self.issuer = issuer
        self.audience = audience

        # Revoked tokens: jti -> expiration_timestamp
        # This allows TTL-based cleanup of expired revocations
        self._revoked_tokens: Dict[str, int] = {}
        self._revoked_lock = threading.RLock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

    def create_token(
        self,
        user_id: str,
        roles: List[str] = None,
        permissions: List[str] = None,
        expires_delta: timedelta = None,
        **metadata
    ) -> str:
        """
        Create a new JWT token.

        Args:
            user_id: User identifier
            roles: List of user roles
            permissions: List of permissions
            expires_delta: Custom expiration time
            **metadata: Additional claims

        Returns:
            Encoded JWT token
        """
        import uuid

        now = datetime.now(timezone.utc)
        expire = now + (expires_delta or self.access_expire)

        payload = TokenPayload(
            sub=user_id,
            iat=int(now.timestamp()),
            exp=int(expire.timestamp()),
            jti=str(uuid.uuid4()),
            roles=roles or [],
            permissions=permissions or [],
            metadata=metadata
        )

        return self._encode(payload)

    def create_refresh_token(
        self,
        user_id: str,
        roles: List[str] = None
    ) -> str:
        """Create a refresh token with longer expiration."""
        return self.create_token(
            user_id=user_id,
            roles=roles,
            expires_delta=self.refresh_expire,
            token_type="refresh"
        )

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenPayload if valid, None otherwise
        """
        try:
            # Trigger cleanup if needed
            self._maybe_cleanup_revoked()

            payload = self._decode(token)

            if payload is None:
                return None

            # Check if revoked (thread-safe)
            if payload.jti:
                with self._revoked_lock:
                    if payload.jti in self._revoked_tokens:
                        return None

            # Check expiration
            if payload.is_expired():
                return None

            return payload

        except Exception:
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh a token if valid.

        Args:
            token: Current token

        Returns:
            New token or None if invalid
        """
        payload = self.verify_token(token)
        if payload is None:
            return None

        # Revoke old token with its expiration time
        if payload.jti:
            with self._revoked_lock:
                self._revoked_tokens[payload.jti] = payload.exp

        # Create new token
        return self.create_token(
            user_id=payload.sub,
            roles=payload.roles,
            permissions=payload.permissions,
            **payload.metadata
        )

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked successfully
        """
        payload = self._decode(token)
        if payload and payload.jti:
            with self._revoked_lock:
                # Store with expiration time for TTL-based cleanup
                self._revoked_tokens[payload.jti] = payload.exp
            return True
        return False

    def _maybe_cleanup_revoked(self) -> None:
        """
        Clean up expired revoked tokens if cleanup interval has passed.

        This prevents unbounded memory growth from revoked tokens.
        """
        now = time.time()

        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._revoked_lock:
            # Double-check inside lock
            if now - self._last_cleanup < self._cleanup_interval:
                return

            # Remove tokens that have expired
            # Once a token expires, we no longer need to track it as revoked
            expired_jtis = [
                jti for jti, exp_time in self._revoked_tokens.items()
                if exp_time < now
            ]

            for jti in expired_jtis:
                del self._revoked_tokens[jti]

            if expired_jtis:
                logger.debug(f"Cleaned up {len(expired_jtis)} expired revoked tokens")

            self._last_cleanup = now

    def get_revoked_count(self) -> int:
        """Get count of currently tracked revoked tokens."""
        with self._revoked_lock:
            return len(self._revoked_tokens)

    def force_cleanup(self) -> int:
        """
        Force cleanup of expired revoked tokens.

        Returns:
            Number of tokens cleaned up
        """
        now = time.time()
        cleaned = 0

        with self._revoked_lock:
            expired_jtis = [
                jti for jti, exp_time in self._revoked_tokens.items()
                if exp_time < now
            ]

            for jti in expired_jtis:
                del self._revoked_tokens[jti]
                cleaned += 1

            self._last_cleanup = now

        return cleaned

    def _encode(self, payload: TokenPayload) -> str:
        """Encode payload to JWT token."""
        header = {"alg": self.algorithm, "typ": "JWT"}
        if self.issuer:
            payload.metadata["iss"] = self.issuer
        if self.audience:
            payload.metadata["aud"] = self.audience

        # Encode header and payload
        header_b64 = self._base64url_encode(json.dumps(header))
        payload_b64 = self._base64url_encode(json.dumps(payload.to_dict()))

        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = self._sign(message)
        signature_b64 = self._base64url_encode(signature)

        return f"{message}.{signature_b64}"

    def _decode(self, token: str) -> Optional[TokenPayload]:
        """Decode JWT token to payload with algorithm validation."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            # Security: Validate algorithm in header matches expected
            # This prevents algorithm confusion attacks
            header_json = self._base64url_decode(header_b64).decode('utf-8')
            header = json.loads(header_json)

            token_algorithm = header.get("alg")
            if token_algorithm != self.algorithm:
                # Algorithm mismatch - potential attack
                return None

            # Security: Reject disallowed algorithms
            if token_algorithm not in ALLOWED_ALGORITHMS:
                return None

            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = self._sign(message)
            actual_signature = self._base64url_decode(signature_b64)

            if not hmac.compare_digest(expected_signature, actual_signature):
                return None

            # Decode payload
            payload_json = self._base64url_decode(payload_b64).decode('utf-8')
            payload_dict = json.loads(payload_json)

            return TokenPayload.from_dict(payload_dict)

        except Exception:
            return None

    def _sign(self, message: str) -> bytes:
        """Sign message with secret key."""
        if self.algorithm == "HS256":
            return hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        elif self.algorithm == "HS384":
            return hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha384
            ).digest()
        elif self.algorithm == "HS512":
            return hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha512
            ).digest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def _base64url_encode(self, data: str | bytes) -> str:
        """Base64url encode data."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    def _base64url_decode(self, data: str) -> bytes:
        """Base64url decode data."""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)


# Convenience functions


def create_jwt_manager(
    secret_key: str,
    config: JWTConfig = None
) -> JWTManager:
    """Create a JWT manager."""
    if config:
        return JWTManager(
            secret_key=config.secret_key,
            algorithm=config.algorithm,
            access_token_expire_minutes=config.access_token_expire_minutes,
            refresh_token_expire_days=config.refresh_token_expire_days,
            issuer=config.issuer,
            audience=config.audience
        )
    return JWTManager(secret_key=secret_key)


def encode_token(
    user_id: str,
    secret_key: str,
    roles: List[str] = None,
    expire_minutes: int = 30
) -> str:
    """Quick token encoding."""
    jwt = JWTManager(secret_key=secret_key, access_token_expire_minutes=expire_minutes)
    return jwt.create_token(user_id=user_id, roles=roles)


def decode_token(
    token: str,
    secret_key: str
) -> Optional[TokenPayload]:
    """Quick token decoding."""
    jwt = JWTManager(secret_key=secret_key)
    return jwt.verify_token(token)
