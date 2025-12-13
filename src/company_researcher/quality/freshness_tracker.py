"""
Source Freshness Tracking - Monitor and flag outdated information.

Provides:
- Source date extraction
- Staleness thresholds by data type
- Freshness indicators
- Auto-refresh suggestions
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class FreshnessLevel(str, Enum):
    """Freshness level indicators."""
    FRESH = "fresh"
    RECENT = "recent"
    AGING = "aging"
    STALE = "stale"
    OUTDATED = "outdated"
    UNKNOWN = "unknown"


class DataType(str, Enum):
    """Types of data with different freshness requirements."""
    STOCK_PRICE = "stock_price"
    FINANCIAL_REPORT = "financial_report"
    NEWS = "news"
    COMPANY_INFO = "company_info"
    MARKET_DATA = "market_data"
    EMPLOYEE_COUNT = "employee_count"
    LEADERSHIP = "leadership"
    PRODUCT_INFO = "product_info"
    GENERAL = "general"


@dataclass
class FreshnessThreshold:
    """Threshold configuration for a data type."""
    data_type: DataType
    fresh_hours: float  # Fresh if younger than this
    recent_hours: float  # Recent if younger than this
    aging_hours: float  # Aging if younger than this
    stale_hours: float  # Stale if younger than this
    # Older than stale_hours = outdated

    def get_level(self, age_hours: float) -> FreshnessLevel:
        """Get freshness level for given age."""
        if age_hours < 0:
            return FreshnessLevel.UNKNOWN
        if age_hours <= self.fresh_hours:
            return FreshnessLevel.FRESH
        if age_hours <= self.recent_hours:
            return FreshnessLevel.RECENT
        if age_hours <= self.aging_hours:
            return FreshnessLevel.AGING
        if age_hours <= self.stale_hours:
            return FreshnessLevel.STALE
        return FreshnessLevel.OUTDATED


# Default thresholds by data type
DEFAULT_THRESHOLDS = {
    DataType.STOCK_PRICE: FreshnessThreshold(
        data_type=DataType.STOCK_PRICE,
        fresh_hours=1,
        recent_hours=4,
        aging_hours=24,
        stale_hours=48
    ),
    DataType.FINANCIAL_REPORT: FreshnessThreshold(
        data_type=DataType.FINANCIAL_REPORT,
        fresh_hours=24 * 30,  # 30 days
        recent_hours=24 * 90,  # 90 days
        aging_hours=24 * 180,  # 6 months
        stale_hours=24 * 365  # 1 year
    ),
    DataType.NEWS: FreshnessThreshold(
        data_type=DataType.NEWS,
        fresh_hours=6,
        recent_hours=24,
        aging_hours=72,
        stale_hours=168  # 1 week
    ),
    DataType.COMPANY_INFO: FreshnessThreshold(
        data_type=DataType.COMPANY_INFO,
        fresh_hours=24 * 7,  # 1 week
        recent_hours=24 * 30,  # 1 month
        aging_hours=24 * 90,  # 3 months
        stale_hours=24 * 180  # 6 months
    ),
    DataType.MARKET_DATA: FreshnessThreshold(
        data_type=DataType.MARKET_DATA,
        fresh_hours=24,
        recent_hours=24 * 7,
        aging_hours=24 * 30,
        stale_hours=24 * 90
    ),
    DataType.EMPLOYEE_COUNT: FreshnessThreshold(
        data_type=DataType.EMPLOYEE_COUNT,
        fresh_hours=24 * 30,
        recent_hours=24 * 90,
        aging_hours=24 * 180,
        stale_hours=24 * 365
    ),
    DataType.LEADERSHIP: FreshnessThreshold(
        data_type=DataType.LEADERSHIP,
        fresh_hours=24 * 7,
        recent_hours=24 * 30,
        aging_hours=24 * 90,
        stale_hours=24 * 180
    ),
    DataType.PRODUCT_INFO: FreshnessThreshold(
        data_type=DataType.PRODUCT_INFO,
        fresh_hours=24 * 7,
        recent_hours=24 * 30,
        aging_hours=24 * 90,
        stale_hours=24 * 180
    ),
    DataType.GENERAL: FreshnessThreshold(
        data_type=DataType.GENERAL,
        fresh_hours=24 * 7,
        recent_hours=24 * 30,
        aging_hours=24 * 90,
        stale_hours=24 * 180
    ),
}


@dataclass
class FreshnessAssessment:
    """Assessment of data freshness."""
    data_type: DataType
    level: FreshnessLevel
    source_date: Optional[datetime]
    assessed_at: datetime
    age_hours: float
    age_description: str
    needs_refresh: bool
    refresh_priority: float  # 0-1, higher = more urgent
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data_type": self.data_type.value,
            "freshness_level": self.level.value,
            "source_date": self.source_date.isoformat() if self.source_date else None,
            "assessed_at": self.assessed_at.isoformat(),
            "age_hours": round(self.age_hours, 1),
            "age_description": self.age_description,
            "needs_refresh": self.needs_refresh,
            "refresh_priority": round(self.refresh_priority, 2),
            "warnings": self.warnings
        }


class DateExtractor:
    """Extracts dates from text and metadata."""

    # Common date patterns
    DATE_PATTERNS = [
        # ISO format
        r'(\d{4}-\d{2}-\d{2})',
        # US format
        r'(\d{1,2}/\d{1,2}/\d{4})',
        # Written format
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})',
        # Quarter references
        r'(Q[1-4] \d{4})',
        r'(Q[1-4]\'\d{2})',
        # Year references
        r'FY(\d{4})',
        r'fiscal year (\d{4})',
    ]

    # Relative date patterns
    RELATIVE_PATTERNS = [
        (r'today', 0),
        (r'yesterday', 1),
        (r'(\d+) days? ago', None),
        (r'(\d+) weeks? ago', None),
        (r'(\d+) months? ago', None),
        (r'last week', 7),
        (r'last month', 30),
        (r'this week', 3),
        (r'this month', 15),
    ]

    def extract_date(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[datetime]:
        """
        Extract date from text or metadata.

        Args:
            text: Text to search for dates
            metadata: Optional metadata dict

        Returns:
            Extracted datetime or None
        """
        # Check metadata first
        if metadata:
            for key in ['published_at', 'date', 'timestamp', 'published_date', 'created_at']:
                if key in metadata:
                    parsed = self._parse_date_value(metadata[key])
                    if parsed:
                        return parsed

        # Try text patterns
        if text:
            return self._extract_from_text(text)

        return None

    def _parse_date_value(self, value: Any) -> Optional[datetime]:
        """Parse various date value formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value)
            except Exception as e:
                logger.debug(f"Failed to parse timestamp {value}: {e}")
        if isinstance(value, str):
            try:
                from dateutil import parser
                return parser.parse(value)
            except Exception as e:
                logger.debug(f"Failed to parse date string '{value[:50]}': {e}")
        return None

    def _extract_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text."""
        # Try standard patterns
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    from dateutil import parser
                    return parser.parse(match.group(1))
                except Exception as e:
                    logger.debug(f"Date pattern match failed to parse: {e}")
                    continue

        # Try relative patterns
        text_lower = text.lower()
        now = utc_now()

        for pattern, days in self.RELATIVE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                if days is not None:
                    return now - timedelta(days=days)
                else:
                    # Extract number from match
                    try:
                        num = int(match.group(1))
                        if 'week' in pattern:
                            return now - timedelta(weeks=num)
                        elif 'month' in pattern:
                            return now - timedelta(days=num * 30)
                        else:
                            return now - timedelta(days=num)
                    except Exception as e:
                        logger.debug(f"Relative date extraction failed: {e}")
                        continue

        return None


class FreshnessTracker:
    """
    Tracks and assesses data freshness.

    Usage:
        tracker = FreshnessTracker()

        # Assess freshness of data
        assessment = tracker.assess(
            data_type=DataType.NEWS,
            source_date=article_date,
            content=article_text
        )

        if assessment.needs_refresh:
            print(f"Warning: {assessment.level.value}")

        # Get batch assessments
        report = tracker.get_freshness_report(research_result)
    """

    def __init__(
        self,
        thresholds: Dict[DataType, FreshnessThreshold] = None,
        date_extractor: DateExtractor = None
    ):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS
        self.date_extractor = date_extractor or DateExtractor()

    def assess(
        self,
        data_type: DataType,
        source_date: datetime = None,
        content: str = None,
        metadata: Dict[str, Any] = None
    ) -> FreshnessAssessment:
        """
        Assess freshness of data.

        Args:
            data_type: Type of data
            source_date: Known source date
            content: Text content to extract date from
            metadata: Additional metadata

        Returns:
            FreshnessAssessment object
        """
        now = utc_now()
        warnings = []

        # Determine source date
        if source_date is None:
            source_date = self.date_extractor.extract_date(content or "", metadata)

        # Calculate age
        if source_date:
            age_hours = (now - source_date).total_seconds() / 3600
            age_description = self._format_age(age_hours)
        else:
            age_hours = -1
            age_description = "Unknown"
            warnings.append("Source date could not be determined")

        # Get threshold
        threshold = self.thresholds.get(data_type, self.thresholds[DataType.GENERAL])

        # Determine level
        level = threshold.get_level(age_hours)

        # Determine if refresh needed
        needs_refresh = level in [FreshnessLevel.STALE, FreshnessLevel.OUTDATED, FreshnessLevel.UNKNOWN]

        # Calculate refresh priority
        if level == FreshnessLevel.OUTDATED:
            refresh_priority = 1.0
        elif level == FreshnessLevel.STALE:
            refresh_priority = 0.8
        elif level == FreshnessLevel.UNKNOWN:
            refresh_priority = 0.6
        elif level == FreshnessLevel.AGING:
            refresh_priority = 0.3
        else:
            refresh_priority = 0.0

        # Add warnings based on level
        if level == FreshnessLevel.OUTDATED:
            warnings.append(f"Data is significantly outdated ({age_description})")
        elif level == FreshnessLevel.STALE:
            warnings.append(f"Data may be stale ({age_description})")

        return FreshnessAssessment(
            data_type=data_type,
            level=level,
            source_date=source_date,
            assessed_at=now,
            age_hours=age_hours,
            age_description=age_description,
            needs_refresh=needs_refresh,
            refresh_priority=refresh_priority,
            warnings=warnings
        )

    def assess_multiple(
        self,
        items: List[Tuple[DataType, Optional[datetime], str]]
    ) -> List[FreshnessAssessment]:
        """
        Assess multiple items.

        Args:
            items: List of (data_type, source_date, content) tuples

        Returns:
            List of FreshnessAssessment objects
        """
        return [
            self.assess(data_type, source_date, content)
            for data_type, source_date, content in items
        ]

    def get_freshness_report(
        self,
        research_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate freshness report for research result.

        Args:
            research_result: Research result dictionary

        Returns:
            Report dictionary
        """
        assessments = []

        # Assess different sections
        agent_outputs = research_result.get("agent_outputs", {})

        # Map agents to data types
        agent_data_types = {
            "financial": DataType.FINANCIAL_REPORT,
            "enhanced_financial": DataType.FINANCIAL_REPORT,
            "market": DataType.MARKET_DATA,
            "competitor": DataType.MARKET_DATA,
            "news": DataType.NEWS,
            "product": DataType.PRODUCT_INFO,
            "leadership": DataType.LEADERSHIP,
        }

        for agent_name, output in agent_outputs.items():
            if not isinstance(output, dict):
                continue

            data_type = agent_data_types.get(agent_name, DataType.GENERAL)
            source_date = output.get("source_date") or output.get("data_date")

            if isinstance(source_date, str):
                try:
                    source_date = datetime.fromisoformat(source_date)
                except Exception:
                    source_date = None

            assessment = self.assess(
                data_type=data_type,
                source_date=source_date,
                metadata=output
            )
            assessments.append({
                "section": agent_name,
                "assessment": assessment
            })

        # Calculate overall freshness
        if assessments:
            avg_priority = sum(
                a["assessment"].refresh_priority for a in assessments
            ) / len(assessments)
            stale_count = sum(
                1 for a in assessments
                if a["assessment"].level in [FreshnessLevel.STALE, FreshnessLevel.OUTDATED]
            )
            overall_level = (
                FreshnessLevel.STALE if stale_count > len(assessments) / 2
                else FreshnessLevel.FRESH if avg_priority < 0.2
                else FreshnessLevel.AGING
            )
        else:
            avg_priority = 0.5
            stale_count = 0
            overall_level = FreshnessLevel.UNKNOWN

        return {
            "overall_freshness": overall_level.value,
            "refresh_priority": round(avg_priority, 2),
            "stale_sections": stale_count,
            "total_sections": len(assessments),
            "sections": [
                {
                    "name": a["section"],
                    **a["assessment"].to_dict()
                }
                for a in assessments
            ],
            "refresh_recommendations": self._get_refresh_recommendations(assessments)
        }

    def _format_age(self, hours: float) -> str:
        """Format age in human-readable format."""
        if hours < 0:
            return "Unknown"
        if hours < 1:
            return f"{int(hours * 60)} minutes"
        if hours < 24:
            return f"{int(hours)} hours"
        if hours < 24 * 7:
            return f"{int(hours / 24)} days"
        if hours < 24 * 30:
            return f"{int(hours / (24 * 7))} weeks"
        if hours < 24 * 365:
            return f"{int(hours / (24 * 30))} months"
        return f"{int(hours / (24 * 365))} years"

    def _get_refresh_recommendations(
        self,
        assessments: List[Dict]
    ) -> List[str]:
        """Generate refresh recommendations."""
        recommendations = []

        for item in assessments:
            assessment = item["assessment"]
            section = item["section"]

            if assessment.refresh_priority >= 0.8:
                recommendations.append(
                    f"URGENT: Refresh {section} data immediately "
                    f"(last updated: {assessment.age_description})"
                )
            elif assessment.refresh_priority >= 0.5:
                recommendations.append(
                    f"Recommend refreshing {section} data soon "
                    f"(last updated: {assessment.age_description})"
                )

        return recommendations


# Convenience functions

def create_freshness_tracker() -> FreshnessTracker:
    """Create a freshness tracker."""
    return FreshnessTracker()


def assess_data_freshness(
    data_type: DataType,
    source_date: datetime = None,
    content: str = None
) -> FreshnessAssessment:
    """Assess freshness of data."""
    tracker = FreshnessTracker()
    return tracker.assess(data_type, source_date, content)
