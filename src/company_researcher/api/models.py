"""
API Request/Response Models (Phase 18.1).

Pydantic models for API validation:
- Request models
- Response models
- Error models
"""

import ipaddress
import re
import socket
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from ..utils import utc_now

try:
    from pydantic import BaseModel, Field, field_validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback to dataclass-like behavior
    from dataclasses import dataclass as BaseModel

    def Field(*args, **kwargs):
        return kwargs.get("default")


# ============================================================================
# Enums
# ============================================================================


class ResearchDepthEnum(str, Enum):
    """Research depth levels."""

    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class TaskStatusEnum(str, Enum):
    """Task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Request Models
# ============================================================================

if PYDANTIC_AVAILABLE:
    # Pattern for valid company names (alphanumeric, spaces, common punctuation)
    COMPANY_NAME_PATTERN = re.compile(r"^[\w\s\.\,\&\-\(\)\'\"]+$", re.UNICODE)
    # Pattern for valid URLs
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    # Error message constants
    ERR_INVALID_URL_FORMAT = "Invalid webhook URL format. Must be a valid HTTP/HTTPS URL."
    ERR_HTTPS_REQUIRED = "Webhook URL must use HTTPS for security (localhost exceptions allowed)"
    ERR_SSRF_BLOCKED = "Webhook URL points to internal/private network (SSRF protection)"
    HTTPS_PREFIX = "https://"

    # SSRF Protection: Private/internal IP ranges to block
    BLOCKED_IP_NETWORKS = [
        ipaddress.ip_network("10.0.0.0/8"),  # Private Class A
        ipaddress.ip_network("172.16.0.0/12"),  # Private Class B
        ipaddress.ip_network("192.168.0.0/16"),  # Private Class C
        ipaddress.ip_network("127.0.0.0/8"),  # Loopback
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local (AWS metadata)
        ipaddress.ip_network("0.0.0.0/8"),  # Current network
        ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
        ipaddress.ip_network("192.0.0.0/24"),  # IETF Protocol Assignments
        ipaddress.ip_network("192.0.2.0/24"),  # TEST-NET-1
        ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
        ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
        ipaddress.ip_network("224.0.0.0/4"),  # Multicast
        ipaddress.ip_network("240.0.0.0/4"),  # Reserved
    ]

    # Blocked hostnames (case-insensitive)
    BLOCKED_HOSTNAMES = frozenset(
        [
            "metadata.google.internal",
            "metadata.google",
            "metadata",
            "instance-data",
        ]
    )

    def _is_internal_ip(ip_str: str) -> bool:
        """Check if an IP address is in a blocked internal range."""
        try:
            ip = ipaddress.ip_address(ip_str)
            return any(ip in network for network in BLOCKED_IP_NETWORKS)
        except ValueError:
            return False

    def _is_ssrf_target(url: str) -> bool:
        """
        Check if URL points to internal/private network (SSRF protection).

        Returns True if the URL should be blocked.
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname

            if not hostname:
                return True  # Block URLs without hostname

            # Check blocked hostnames
            if hostname.lower() in BLOCKED_HOSTNAMES:
                return True

            # Check if hostname is an IP address
            try:
                if _is_internal_ip(hostname):
                    return True
            except ValueError:
                pass  # Not an IP address, continue

            # Resolve hostname and check resolved IPs
            # Note: This adds latency but is necessary for complete SSRF protection
            try:
                resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
                for family, _, _, _, sockaddr in resolved_ips:
                    ip = sockaddr[0]
                    if _is_internal_ip(ip):
                        return True
            except socket.gaierror:
                pass  # DNS resolution failed, allow for now (will fail at request time)

            return False
        except Exception:
            return True  # Block on any parsing error

    def _validate_webhook_url(url: Optional[str]) -> Optional[str]:
        """Shared webhook URL validation logic with SSRF protection."""
        if url is None:
            return url
        url = url.strip()
        if not url:
            return None
        if not URL_PATTERN.match(url):
            raise ValueError(ERR_INVALID_URL_FORMAT)

        # SSRF Protection: Block internal networks
        # Allow localhost only in development (for testing)
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        is_localhost = hostname in ("localhost", "127.0.0.1", "::1")

        if not is_localhost and _is_ssrf_target(url):
            raise ValueError(ERR_SSRF_BLOCKED)

        # Require HTTPS for non-localhost URLs
        if not url.startswith(HTTPS_PREFIX) and not is_localhost:
            raise ValueError(ERR_HTTPS_REQUIRED)

        return url

    class ResearchRequest(BaseModel):
        """Request to start company research."""

        company_name: str = Field(
            ..., min_length=1, max_length=200, description="Company name to research"
        )
        depth: ResearchDepthEnum = Field(
            default=ResearchDepthEnum.STANDARD, description="Research depth level"
        )
        include_financial: bool = Field(default=True, description="Include financial analysis")
        include_market: bool = Field(default=True, description="Include market analysis")
        include_competitive: bool = Field(default=True, description="Include competitive analysis")
        include_news: bool = Field(default=True, description="Include news analysis")
        include_brand: bool = Field(default=False, description="Include brand audit")
        include_social: bool = Field(default=False, description="Include social media analysis")
        include_sales: bool = Field(default=False, description="Include sales intelligence")
        include_investment: bool = Field(default=False, description="Include investment analysis")
        webhook_url: Optional[str] = Field(
            default=None, description="Webhook URL for completion notification"
        )
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

        @field_validator("company_name")
        @classmethod
        def validate_company_name(cls, v: str) -> str:
            """Validate and sanitize company name."""
            # Strip whitespace
            v = v.strip()
            if not v:
                raise ValueError("Company name cannot be empty")
            # Check for valid characters
            if not COMPANY_NAME_PATTERN.match(v):
                raise ValueError(
                    "Company name contains invalid characters. "
                    "Only alphanumeric, spaces, and common punctuation allowed."
                )
            # Prevent potential injection patterns
            suspicious_patterns = ["<script", "javascript:", "data:", "{{", "{%", "${{"]
            v_lower = v.lower()
            for pattern in suspicious_patterns:
                if pattern in v_lower:
                    raise ValueError("Company name contains suspicious content")
            return v

        @field_validator("webhook_url")
        @classmethod
        def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
            """Validate webhook URL format."""
            return _validate_webhook_url(v)

        class Config:
            json_schema_extra = {
                "example": {
                    "company_name": "Tesla",
                    "depth": "standard",
                    "include_financial": True,
                    "include_market": True,
                    "include_competitive": True,
                    "include_news": True,
                }
            }

    class BatchRequest(BaseModel):
        """Request for batch research."""

        companies: List[str] = Field(
            ..., min_length=1, max_length=100, description="List of company names"
        )
        depth: ResearchDepthEnum = Field(default=ResearchDepthEnum.STANDARD)
        priority: int = Field(default=3, ge=1, le=5, description="Priority (1=highest)")
        webhook_url: Optional[str] = None
        metadata: Dict[str, Any] = Field(default_factory=dict)

        @field_validator("companies")
        @classmethod
        def validate_companies(cls, v: List[str]) -> List[str]:
            """Validate list of company names."""
            if not v:
                raise ValueError("Companies list cannot be empty")
            validated = []
            for i, company in enumerate(v):
                company = company.strip()
                if not company:
                    raise ValueError(f"Company at index {i} cannot be empty")
                if len(company) > 200:
                    raise ValueError(f"Company name at index {i} exceeds 200 characters")
                if not COMPANY_NAME_PATTERN.match(company):
                    raise ValueError(
                        f"Company name at index {i} contains invalid characters. "
                        "Only alphanumeric, spaces, and common punctuation allowed."
                    )
                # Check for duplicates
                if company.lower() in [c.lower() for c in validated]:
                    raise ValueError(f"Duplicate company name: {company}")
                validated.append(company)
            return validated

        @field_validator("webhook_url")
        @classmethod
        def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
            """Validate webhook URL format."""
            return _validate_webhook_url(v)

        class Config:
            json_schema_extra = {
                "example": {
                    "companies": ["Tesla", "Apple", "Microsoft"],
                    "depth": "standard",
                    "priority": 2,
                }
            }

    class WebhookConfig(BaseModel):
        """Webhook configuration."""

        url: str = Field(..., description="Webhook URL")
        events: List[str] = Field(default=["completed", "failed"], description="Events to notify")
        secret: Optional[str] = Field(default=None, description="Webhook signing secret")
        retry_count: int = Field(default=3, ge=0, le=10)

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate webhook URL."""
            v = v.strip()
            if not v:
                raise ValueError("Webhook URL cannot be empty")
            # Use shared validation (returns None for empty, but we already checked)
            result = _validate_webhook_url(v)
            if result is None:
                raise ValueError("Webhook URL cannot be empty")
            return result

        @field_validator("events")
        @classmethod
        def validate_events(cls, v: List[str]) -> List[str]:
            """Validate webhook events."""
            valid_events = {"completed", "failed", "started", "progress", "cancelled"}
            for event in v:
                if event not in valid_events:
                    raise ValueError(
                        f"Invalid event: {event}. "
                        f'Valid events: {", ".join(sorted(valid_events))}'
                    )
            return v

    # ============================================================================
    # Response Models
    # ============================================================================

    class ResearchResponse(BaseModel):
        """Response for research request."""

        task_id: str = Field(..., description="Unique task identifier")
        company_name: str
        status: TaskStatusEnum
        depth: ResearchDepthEnum
        created_at: datetime
        estimated_duration_seconds: Optional[int] = None
        message: str = "Research task created"

        class Config:
            json_schema_extra = {
                "example": {
                    "task_id": "task_1234567890",
                    "company_name": "Tesla",
                    "status": "pending",
                    "depth": "standard",
                    "created_at": "2024-01-15T10:30:00Z",
                    "estimated_duration_seconds": 120,
                    "message": "Research task created",
                }
            }

    class ResearchResult(BaseModel):
        """Complete research result."""

        task_id: str
        company_name: str
        status: TaskStatusEnum
        created_at: datetime
        completed_at: Optional[datetime] = None
        duration_seconds: float = 0
        total_cost: float = 0
        agent_outputs: Dict[str, Any] = Field(default_factory=dict)
        synthesis: Optional[Dict[str, Any]] = None
        quality_score: Optional[float] = None
        error: Optional[str] = None

    class BatchResponse(BaseModel):
        """Response for batch request."""

        batch_id: str
        total_companies: int
        status: TaskStatusEnum
        created_at: datetime
        task_ids: List[str]
        message: str = "Batch research started"

    class BatchResult(BaseModel):
        """Complete batch result."""

        batch_id: str
        total_companies: int
        completed: int
        failed: int
        cancelled: int
        success_rate: float
        total_cost: float
        duration_seconds: float
        results: Dict[str, Any]
        errors: Dict[str, str]

    class TaskStatus(BaseModel):
        """Task status response."""

        task_id: str
        company_name: str
        status: TaskStatusEnum
        progress: float = Field(default=0, ge=0, le=100)
        current_stage: Optional[str] = None
        stages_completed: List[str] = Field(default_factory=list)
        created_at: datetime
        started_at: Optional[datetime] = None
        estimated_completion: Optional[datetime] = None

    class HealthResponse(BaseModel):
        """Health check response."""

        status: str = "healthy"
        version: str = "1.0.0"
        timestamp: datetime
        services: Dict[str, str] = Field(default_factory=dict)

        class Config:
            json_schema_extra = {
                "example": {
                    "status": "healthy",
                    "version": "1.0.0",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "services": {
                        "database": "connected",
                        "cache": "connected",
                        "search": "connected",
                    },
                }
            }

    class ErrorResponse(BaseModel):
        """Error response."""

        error: str
        detail: Optional[str] = None
        code: str = "UNKNOWN_ERROR"
        timestamp: datetime = Field(default_factory=utc_now)

        class Config:
            json_schema_extra = {
                "example": {
                    "error": "Company not found",
                    "detail": "No data available for the requested company",
                    "code": "NOT_FOUND",
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            }

    class RateLimitResponse(BaseModel):
        """Rate limit exceeded response."""

        error: str = "Rate limit exceeded"
        retry_after: int = Field(..., description="Seconds until rate limit resets")
        limit: int = Field(..., description="Request limit")
        remaining: int = Field(default=0, description="Remaining requests")

    # ============================================================================
    # WebSocket Models
    # ============================================================================

    class WSMessage(BaseModel):
        """WebSocket message."""

        type: str  # "subscribe", "unsubscribe", "ping"
        task_id: Optional[str] = None
        data: Dict[str, Any] = Field(default_factory=dict)

    class WSUpdate(BaseModel):
        """WebSocket update message."""

        type: str  # "status", "progress", "completed", "error"
        task_id: str
        timestamp: datetime
        data: Dict[str, Any]

else:
    # Fallback when Pydantic not available
    from dataclasses import dataclass
    from dataclasses import field as dc_field

    @dataclass
    class ResearchRequest:
        company_name: str
        depth: str = "standard"
        include_financial: bool = True
        include_market: bool = True
        include_competitive: bool = True
        include_news: bool = True
        include_brand: bool = False
        include_social: bool = False
        include_sales: bool = False
        include_investment: bool = False
        webhook_url: Optional[str] = None
        metadata: Dict[str, Any] = dc_field(default_factory=dict)

    @dataclass
    class ResearchResponse:
        task_id: str
        company_name: str
        status: str
        depth: str
        created_at: datetime
        estimated_duration_seconds: Optional[int] = None
        message: str = "Research task created"

    @dataclass
    class BatchRequest:
        companies: List[str]
        depth: str = "standard"
        priority: int = 3
        webhook_url: Optional[str] = None
        metadata: Dict[str, Any] = dc_field(default_factory=dict)

    @dataclass
    class BatchResponse:
        batch_id: str
        total_companies: int
        status: str
        created_at: datetime
        task_ids: List[str]
        message: str = "Batch research started"

    @dataclass
    class HealthResponse:
        status: str = "healthy"
        version: str = "1.0.0"
        timestamp: datetime = dc_field(default_factory=utc_now)
        services: Dict[str, str] = dc_field(default_factory=dict)
