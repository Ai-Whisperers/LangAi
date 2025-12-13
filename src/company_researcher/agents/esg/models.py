"""
ESG Models Module.

Enums, dataclasses, and indicator frameworks for ESG analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from ...utils import utc_now


class ESGCategory(str, Enum):
    """ESG categories."""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"


class ESGRating(str, Enum):
    """ESG rating levels."""
    AAA = "AAA"  # Leader
    AA = "AA"
    A = "A"
    BBB = "BBB"  # Average
    BB = "BB"
    B = "B"
    CCC = "CCC"  # Laggard
    CC = "CC"
    C = "C"


class ControversySeverity(str, Enum):
    """Controversy severity levels."""
    SEVERE = "severe"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NONE = "none"


@dataclass
class ESGMetric:
    """An ESG metric."""
    name: str
    category: ESGCategory
    value: Any
    unit: str = ""
    year: int = 0
    trend: str = ""  # improving, stable, declining
    benchmark: Optional[float] = None
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "value": self.value,
            "unit": self.unit,
            "year": self.year,
            "trend": self.trend,
            "benchmark": self.benchmark,
            "source": self.source
        }


@dataclass
class Controversy:
    """An ESG controversy."""
    title: str
    description: str
    category: ESGCategory
    severity: ControversySeverity
    date: Optional[datetime] = None
    resolved: bool = False
    impact: str = ""
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "severity": self.severity.value,
            "date": self.date.isoformat() if self.date else None,
            "resolved": self.resolved,
            "impact": self.impact,
            "sources": self.sources
        }


@dataclass
class ESGScore:
    """ESG score breakdown."""
    overall_score: float  # 0-100
    overall_rating: ESGRating
    environmental_score: float
    social_score: float
    governance_score: float
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "overall_rating": self.overall_rating.value,
            "environmental_score": self.environmental_score,
            "social_score": self.social_score,
            "governance_score": self.governance_score,
            "confidence": self.confidence
        }


@dataclass
class ESGAnalysis:
    """Complete ESG analysis result."""
    company_name: str
    score: ESGScore
    metrics: List[ESGMetric]
    controversies: List[Controversy]
    environmental_summary: str
    social_summary: str
    governance_summary: str
    strengths: List[str]
    risks: List[str]
    recommendations: List[str]
    data_sources: List[str]
    analysis_date: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "score": self.score.to_dict(),
            "metrics": [m.to_dict() for m in self.metrics],
            "controversies": [c.to_dict() for c in self.controversies],
            "environmental_summary": self.environmental_summary,
            "social_summary": self.social_summary,
            "governance_summary": self.governance_summary,
            "strengths": self.strengths,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "data_sources": self.data_sources,
            "analysis_date": self.analysis_date.isoformat()
        }


# ============================================================================
# ESG Indicator Frameworks
# ============================================================================

ENVIRONMENTAL_INDICATORS = {
    "carbon_emissions": {
        "name": "Carbon Emissions",
        "unit": "tCO2e",
        "description": "Scope 1 + 2 greenhouse gas emissions"
    },
    "carbon_intensity": {
        "name": "Carbon Intensity",
        "unit": "tCO2e/M revenue",
        "description": "Emissions relative to revenue"
    },
    "renewable_energy": {
        "name": "Renewable Energy Usage",
        "unit": "%",
        "description": "Percentage of energy from renewable sources"
    },
    "water_usage": {
        "name": "Water Usage",
        "unit": "megalitres",
        "description": "Total water consumption"
    },
    "waste_recycled": {
        "name": "Waste Recycled",
        "unit": "%",
        "description": "Percentage of waste diverted from landfill"
    },
    "environmental_fines": {
        "name": "Environmental Fines",
        "unit": "$",
        "description": "Environmental regulatory penalties"
    }
}

SOCIAL_INDICATORS = {
    "employee_turnover": {
        "name": "Employee Turnover",
        "unit": "%",
        "description": "Annual voluntary turnover rate"
    },
    "diversity_leadership": {
        "name": "Leadership Diversity",
        "unit": "%",
        "description": "Women and minorities in leadership"
    },
    "gender_pay_gap": {
        "name": "Gender Pay Gap",
        "unit": "%",
        "description": "Pay difference between genders"
    },
    "safety_incidents": {
        "name": "Safety Incidents",
        "unit": "TRIR",
        "description": "Total recordable incident rate"
    },
    "community_investment": {
        "name": "Community Investment",
        "unit": "$",
        "description": "Annual community giving"
    },
    "customer_satisfaction": {
        "name": "Customer Satisfaction",
        "unit": "NPS",
        "description": "Net Promoter Score"
    }
}

GOVERNANCE_INDICATORS = {
    "board_independence": {
        "name": "Board Independence",
        "unit": "%",
        "description": "Independent board members"
    },
    "board_diversity": {
        "name": "Board Diversity",
        "unit": "%",
        "description": "Women on board"
    },
    "ceo_pay_ratio": {
        "name": "CEO Pay Ratio",
        "unit": "x",
        "description": "CEO to median employee pay"
    },
    "ethics_violations": {
        "name": "Ethics Violations",
        "unit": "count",
        "description": "Reported ethics violations"
    },
    "data_breaches": {
        "name": "Data Breaches",
        "unit": "count",
        "description": "Significant data security incidents"
    },
    "political_contributions": {
        "name": "Political Contributions",
        "unit": "$",
        "description": "Political spending and lobbying"
    }
}
