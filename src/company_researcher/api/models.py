"""
API Request/Response Models (Phase 18.1).

Pydantic models for API validation:
- Request models
- Response models
- Error models
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

try:
    from pydantic import BaseModel, Field
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
    class ResearchRequest(BaseModel):
        """Request to start company research."""
        company_name: str = Field(..., min_length=1, max_length=200, description="Company name to research")
        depth: ResearchDepthEnum = Field(default=ResearchDepthEnum.STANDARD, description="Research depth level")
        include_financial: bool = Field(default=True, description="Include financial analysis")
        include_market: bool = Field(default=True, description="Include market analysis")
        include_competitive: bool = Field(default=True, description="Include competitive analysis")
        include_news: bool = Field(default=True, description="Include news analysis")
        include_brand: bool = Field(default=False, description="Include brand audit")
        include_social: bool = Field(default=False, description="Include social media analysis")
        include_sales: bool = Field(default=False, description="Include sales intelligence")
        include_investment: bool = Field(default=False, description="Include investment analysis")
        webhook_url: Optional[str] = Field(default=None, description="Webhook URL for completion notification")
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

        class Config:
            json_schema_extra = {
                "example": {
                    "company_name": "Tesla",
                    "depth": "standard",
                    "include_financial": True,
                    "include_market": True,
                    "include_competitive": True,
                    "include_news": True
                }
            }


    class BatchRequest(BaseModel):
        """Request for batch research."""
        companies: List[str] = Field(..., min_items=1, max_items=100, description="List of company names")
        depth: ResearchDepthEnum = Field(default=ResearchDepthEnum.STANDARD)
        priority: int = Field(default=3, ge=1, le=5, description="Priority (1=highest)")
        webhook_url: Optional[str] = None
        metadata: Dict[str, Any] = Field(default_factory=dict)

        class Config:
            json_schema_extra = {
                "example": {
                    "companies": ["Tesla", "Apple", "Microsoft"],
                    "depth": "standard",
                    "priority": 2
                }
            }


    class WebhookConfig(BaseModel):
        """Webhook configuration."""
        url: str = Field(..., description="Webhook URL")
        events: List[str] = Field(default=["completed", "failed"], description="Events to notify")
        secret: Optional[str] = Field(default=None, description="Webhook signing secret")
        retry_count: int = Field(default=3, ge=0, le=10)


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
                    "message": "Research task created"
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
                        "search": "connected"
                    }
                }
            }


    class ErrorResponse(BaseModel):
        """Error response."""
        error: str
        detail: Optional[str] = None
        code: str = "UNKNOWN_ERROR"
        timestamp: datetime = Field(default_factory=datetime.now)

        class Config:
            json_schema_extra = {
                "example": {
                    "error": "Company not found",
                    "detail": "No data available for the requested company",
                    "code": "NOT_FOUND",
                    "timestamp": "2024-01-15T10:30:00Z"
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
    from dataclasses import dataclass, field as dc_field

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
        timestamp: datetime = dc_field(default_factory=datetime.now)
        services: Dict[str, str] = dc_field(default_factory=dict)
