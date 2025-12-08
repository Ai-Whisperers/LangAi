"""
Centralized Type Definitions for Company Researcher.

This module contains all shared enums, types, and data models used across
the company researcher system. Centralizing types:
- Eliminates duplicate enum definitions
- Ensures consistency across modules
- Provides a single source of truth for type definitions
- Simplifies imports and maintenance

Organization:
- Research Types: Research depth, data quality, reasoning
- Agent Types: Brand, sales, social media, investment
- Quality Types: Confidence, source quality, freshness
- Infrastructure Types: Events, status, audit
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


# ============================================================================
# Research Types
# ============================================================================

class ResearchDepth(str, Enum):
    """Depth levels for research operations.

    Used by: deep_research.py, conditional_router.py, research_workflow.py
    """
    SURFACE = "surface"        # Quick overview, minimal depth
    STANDARD = "standard"      # Normal research depth
    DEEP = "deep"              # Comprehensive research
    EXHAUSTIVE = "exhaustive"  # Maximum depth, all sources


class DataQuality(str, Enum):
    """Quality levels for extracted data.

    Used by: deep_research.py, quality checkers
    """
    VERIFIED = "verified"      # Cross-validated from multiple sources
    HIGH = "high"              # Single reliable source
    MEDIUM = "medium"          # Somewhat reliable
    LOW = "low"                # Uncertain reliability
    UNVERIFIED = "unverified"  # Not validated


class ReasoningType(str, Enum):
    """Types of reasoning operations.

    Used by: reasoning.py
    """
    CAUSAL = "causal"              # Cause-effect analysis
    COMPARATIVE = "comparative"    # Comparison between entities
    TEMPORAL = "temporal"          # Time-based analysis
    HYPOTHETICAL = "hypothetical"  # What-if scenarios
    STRATEGIC = "strategic"        # Strategic implications


class InsightType(str, Enum):
    """Types of research insights.

    Used by: reasoning.py
    """
    FINDING = "finding"            # Direct observation
    INFERENCE = "inference"        # Derived conclusion
    PREDICTION = "prediction"      # Future projection
    RECOMMENDATION = "recommendation"  # Action suggestion
    WARNING = "warning"            # Risk or concern


# ============================================================================
# Agent Types - Brand
# ============================================================================

class BrandStrength(str, Enum):
    """Brand strength levels.

    Used by: brand_auditor.py
    """
    DOMINANT = "dominant"    # Market-leading brand
    STRONG = "strong"        # Well-recognized
    MODERATE = "moderate"    # Moderate recognition
    WEAK = "weak"            # Low recognition
    EMERGING = "emerging"    # Building brand


class BrandHealth(str, Enum):
    """Brand health status.

    Used by: brand_auditor.py
    """
    EXCELLENT = "excellent"  # Strong across all dimensions
    GOOD = "good"            # Above average performance
    FAIR = "fair"            # Average performance
    POOR = "poor"            # Below average, needs attention
    CRITICAL = "critical"    # Severe issues requiring action


class SentimentCategory(str, Enum):
    """Sentiment categories.

    Used by: brand_auditor.py, social_media.py
    """
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


# ============================================================================
# Agent Types - Sales Intelligence
# ============================================================================

class LeadScore(str, Enum):
    """Lead scoring categories.

    Used by: sales_intelligence.py
    """
    HOT = "hot"              # High priority, ready to engage
    WARM = "warm"            # Good potential
    COOL = "cool"            # Lower priority
    COLD = "cold"            # Not ready
    NOT_QUALIFIED = "not_qualified"  # Not a fit
    DISQUALIFIED = "disqualified"    # Alias for not_qualified  # Not a fit


class BuyingStage(str, Enum):
    """B2B buying stages.

    Used by: sales_intelligence.py
    """
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    UNKNOWN = "unknown"  # When stage cannot be determined


class CompanySize(str, Enum):
    """Company size categories.

    Used by: sales_intelligence.py, conditional_router.py
    """
    STARTUP = "startup"          # < 50 employees
    SMB = "smb"                  # 50-500 employees
    MID_MARKET = "mid_market"    # 500-5000 employees
    ENTERPRISE = "enterprise"   # 5000+ employees
    FORTUNE_500 = "fortune_500"  # Fortune 500 company


# ============================================================================
# Agent Types - Social Media
# ============================================================================

class SocialPlatform(str, Enum):
    """Social media platforms.

    Used by: social_media.py
    """
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    REDDIT = "reddit"


class EngagementLevel(str, Enum):
    """Social media engagement levels.

    Used by: social_media.py
    """
    VIRAL = "viral"            # Exceptional engagement
    EXCEPTIONAL = "exceptional"  # Alias for viral
    HIGH = "high"              # Above average
    MODERATE = "moderate"      # Average engagement
    LOW = "low"                # Below average
    MINIMAL = "minimal"        # Very little engagement      # Very little engagement


class ContentStrategy(str, Enum):
    """Content strategy types.

    Used by: social_media.py
    """
    THOUGHT_LEADERSHIP = "thought_leadership"
    PRODUCT_FOCUSED = "product_focused"
    COMMUNITY_BUILDING = "community_building"
    SALES_DRIVEN = "sales_driven"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    MIXED = "mixed"


# ============================================================================
# Agent Types - Financial/Investment
# ============================================================================

class InvestmentRating(str, Enum):
    """Investment ratings.

    Used by: investment_analyst.py
    """
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    AVOID = "avoid"  # Alias for strong_sell


class RiskLevel(str, Enum):
    """Risk level categories.

    Used by: investment_analyst.py, regulatory_compliance.py
    """
    CRITICAL = "critical"      # Immediate attention required
    VERY_HIGH = "very_high"    # Very significant risk
    HIGH = "high"              # Significant risk
    MODERATE = "moderate"      # Moderate risk
    MEDIUM = "medium"          # Alias for moderate
    LOW = "low"                # Minimal risk
    VERY_LOW = "very_low"      # Negligible risk
    MINIMAL = "minimal"        # Alias for very_low      # Negligible risk


class MoatStrength(str, Enum):
    """Competitive moat strength.

    Used by: investment_analyst.py
    """
    WIDE = "wide"            # Strong sustainable advantage
    NARROW = "narrow"        # Some competitive advantage
    NONE = "none"            # No significant moat


class GrowthStage(str, Enum):
    """Company growth stages.

    Used by: investment_analyst.py
    """
    EARLY_STAGE = "early_stage"
    HYPERGROWTH = "hypergrowth"  # >50% growth
    HIGH_GROWTH = "high_growth"  # 20-50% growth
    GROWTH = "growth"            # 10-20% growth
    MATURE = "mature"            # <10% growth
    DECLINING = "declining"      # Negative growth
    TURNAROUND = "turnaround"    # Recovery phase


# ============================================================================
# Quality Types
# ============================================================================

class ConfidenceLevel(str, Enum):
    """Confidence level for extracted data.

    Used by: confidence_scorer.py, self_reflection.py, quality/models.py
    """
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"            # 75-90%
    MEDIUM = "medium"        # 50-75%
    LOW = "low"              # 25-50%
    VERY_LOW = "very_low"    # 0-25%


class SourceQuality(str, Enum):
    """Source quality levels.

    Used by: quality/models.py, citations.py
    """
    AUTHORITATIVE = "authoritative"  # Official sources
    HIGH = "high"                    # Reputable sources
    MEDIUM = "medium"                # Standard sources
    LOW = "low"                      # Less reliable
    UNVERIFIED = "unverified"        # Unknown reliability


class SourceType(str, Enum):
    """Types of information sources.

    Used by: confidence_scorer.py, citations.py
    """
    OFFICIAL = "official"            # Company website, SEC filings
    NEWS = "news"                    # News articles
    SOCIAL = "social"                # Social media
    ANALYST = "analyst"              # Analyst reports
    DATABASE = "database"            # Data providers
    USER_GENERATED = "user_generated"  # Reviews, forums


class FreshnessLevel(str, Enum):
    """Data freshness levels.

    Used by: freshness_tracker.py
    """
    CURRENT = "current"        # < 1 week
    RECENT = "recent"          # 1-4 weeks
    DATED = "dated"            # 1-6 months
    STALE = "stale"            # 6-12 months
    OUTDATED = "outdated"      # > 1 year


class ContradictionSeverity(str, Enum):
    """Severity of data contradictions.

    Used by: contradiction_detector.py
    """
    CRITICAL = "CRITICAL"      # Major conflicting data
    HIGH = "HIGH"              # Significant conflicts
    MEDIUM = "MEDIUM"          # Minor conflicts
    LOW = "LOW"                # Trivial differences                # Trivial differences


class ResolutionStrategy(str, Enum):
    """Strategies for resolving contradictions.

    Used by: contradiction_detector.py
    """
    USE_OFFICIAL = "use_official"       # Use official/authoritative source
    USE_RECENT = "use_recent"           # Use most recent information
    USE_MAJORITY = "use_majority"       # Use most commonly cited value
    INVESTIGATE = "investigate"         # Requires further investigation
    REPORT_BOTH = "report_both"         # Report both values with context
    AVERAGE = "average"                 # Use average (for numerical values)


class IssueSeverity(str, Enum):
    """Logic/quality issue severity.

    Used by: logic_critic.py
    """
    ERROR = "error"            # Must be fixed
    WARNING = "warning"        # Should be addressed
    INFO = "info"              # For information


# ============================================================================
# Infrastructure Types
# ============================================================================

class EventType(str, Enum):
    """Types of streaming events.

    Used by: api/streaming.py, streaming/event_streaming.py
    """
    STARTED = "started"
    PROGRESS = "progress"
    AGENT_OUTPUT = "agent_output"
    ERROR = "error"
    COMPLETED = "completed"


class TaskStatus(str, Enum):
    """Task execution status.

    Used by: api/models.py, scheduler.py
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuditEventType(str, Enum):
    """Types of audit events.

    Used by: audit_trail.py, security/audit.py
    """
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    AGENT_INVOKED = "agent_invoked"
    DATA_ACCESSED = "data_accessed"
    ERROR_OCCURRED = "error_occurred"
    QUALITY_CHECK = "quality_check"


class HealthStatus(str, Enum):
    """Service health status.

    Used by: health.py
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class CircuitState(str, Enum):
    """Circuit breaker states.

    Used by: circuit_breaker.py
    """
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


# ============================================================================
# Competitive Analysis Types
# ============================================================================

class CompetitorType(str, Enum):
    """Types of competitors.

    Used by: competitor_analysis_utils.py, competitor_scout.py
    """
    DIRECT = "direct"            # Same product/market
    INDIRECT = "indirect"        # Different product, same need
    POTENTIAL = "potential"      # Could enter market
    SUBSTITUTE = "substitute"    # Alternative solutions


class ThreatLevel(str, Enum):
    """Competitive threat levels.

    Used by: competitor_analysis_utils.py
    """
    CRITICAL = "critical"    # Major threat
    HIGH = "high"            # Significant threat
    MEDIUM = "medium"        # Moderate threat
    LOW = "low"              # Minor threat
    MINIMAL = "minimal"      # Negligible threat


class MarketTrend(str, Enum):
    """Market trend directions.

    Used by: market_sizing_utils.py
    """
    EXPLOSIVE_GROWTH = "explosive_growth"  # > 30% YoY
    HIGH_GROWTH = "high_growth"            # 15-30% YoY
    MODERATE_GROWTH = "moderate_growth"    # 5-15% YoY
    STABLE = "stable"                      # 0-5% YoY
    DECLINING = "declining"                # < 0% YoY


class CompetitiveIntensity(str, Enum):
    """Market competitive intensity.

    Used by: market_sizing_utils.py
    """
    MONOPOLY = "monopoly"                # Single dominant player
    OLIGOPOLY = "oligopoly"              # Few large players
    FRAGMENTED = "fragmented"            # Many small players
    HYPERCOMPETITIVE = "hypercompetitive"  # Intense rivalry


# ============================================================================
# Dataclasses for Common Structures
# ============================================================================

@dataclass
class TokenUsage:
    """Token usage tracking."""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "input": self.input_tokens,
            "output": self.output_tokens,
            "total": self.total
        }


@dataclass
class AgentMetrics:
    """Standard agent metrics."""
    cost: float = 0.0
    tokens: TokenUsage = field(default_factory=TokenUsage)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cost": self.cost,
            "tokens": self.tokens.to_dict(),
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SourceInfo:
    """Information about a data source."""
    url: str
    title: str = ""
    quality: SourceQuality = SourceQuality.MEDIUM
    freshness: FreshnessLevel = FreshnessLevel.RECENT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "quality": self.quality.value,
            "freshness": self.freshness.value
        }


# ============================================================================
# Type Aliases
# ============================================================================

# Common type aliases for better readability
SearchResults = List[Dict[str, Any]]
AgentOutput = Dict[str, Any]
StateUpdate = Dict[str, Any]
