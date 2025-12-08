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
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


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


@dataclass
class JWTConfig:
    """JWT configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: Optional[str] = None
    audience: Optional[str] = None


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
        audience: Optional[str] = None
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_expire = timedelta(days=refresh_token_expire_days)
        self.issuer = issuer
        self.audience = audience
        self._revoked_tokens: set = set()

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

        now = datetime.utcnow()
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
            payload = self._decode(token)

            if payload is None:
                return None

            # Check if revoked
            if payload.jti and payload.jti in self._revoked_tokens:
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

        # Revoke old token
        if payload.jti:
            self._revoked_tokens.add(payload.jti)

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
            self._revoked_tokens.add(payload.jti)
            return True
        return False

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
        """Decode JWT token to payload."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

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
