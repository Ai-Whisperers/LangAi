"""
Research Configuration Models.

Dataclasses for company profiles, market configuration, and research results.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class ResearchDepth(str, Enum):
    """Research depth levels."""
    QUICK = "quick"           # 6 queries, faster
    STANDARD = "standard"     # 9 queries, balanced
    COMPREHENSIVE = "comprehensive"  # 12 queries, thorough


@dataclass
class CompanyProfile:
    """Company research profile from YAML."""
    name: str
    legal_name: str = ""
    ticker: str = ""
    exchange: str = ""
    website: str = ""
    industry: str = ""
    country: str = ""
    region: str = ""
    parent_company: str = ""
    parent_ticker: str = ""
    founded: str = ""
    headquarters: str = ""
    ceo: str = ""
    employees: str = ""
    market_position: Dict[str, Any] = field(default_factory=dict)
    services: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    research_focus: List[str] = field(default_factory=list)
    priority_queries: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    @classmethod
    def from_yaml(cls, yaml_data: Dict[str, Any]) -> "CompanyProfile":
        """Create profile from YAML data."""
        company = yaml_data.get("company", yaml_data)
        research = yaml_data.get("research", {})
        competitors_data = yaml_data.get("competitors", {})

        # Handle nested services structure
        services_raw = company.get("services", [])
        services = []

        def extract_service_text(item):
            """Extract meaningful text from various service data formats."""
            if isinstance(item, str):
                return item
            elif isinstance(item, dict):
                if 'type' in item:
                    service_type = item.get('type', '')
                    share = item.get('share', '')
                    if share:
                        return f"{service_type} ({share})"
                    return service_type
                elif 'name' in item:
                    return item.get('name', '')
                elif 'service' in item:
                    return item.get('service', '')
                else:
                    values = [str(v) for v in item.values() if v]
                    return ', '.join(values[:2]) if values else None
            elif isinstance(item, list):
                return ', '.join(str(x) for x in item[:3])
            return None

        for item in services_raw:
            text = extract_service_text(item)
            if text:
                services.append(text)

        # Extract competitor names
        competitors = []
        if isinstance(competitors_data, dict):
            for comp_key, comp_value in competitors_data.items():
                if isinstance(comp_value, dict):
                    comp_name = comp_value.get("name", comp_key)
                    competitors.append(comp_name)
                elif isinstance(comp_value, str):
                    competitors.append(comp_value)
        elif isinstance(competitors_data, list):
            for comp in competitors_data:
                if isinstance(comp, str):
                    competitors.append(comp)
                elif isinstance(comp, dict):
                    competitors.append(comp.get("name", ""))

        # Extract details (nested company info like CEO, headquarters, employees)
        details = company.get("details", {})

        # Extract values from details if present, otherwise from top-level
        ceo = details.get("ceo", "") if details else ""
        employees = details.get("employees", "") if details else ""
        hq = details.get("headquarters", company.get("headquarters", "")) if details else company.get("headquarters", "")
        founded_val = details.get("founded", company.get("founded", "")) if details else company.get("founded", "")

        return cls(
            name=company.get("name", ""),
            legal_name=company.get("legal_name", ""),
            ticker=company.get("ticker", ""),
            exchange=company.get("exchange", ""),
            website=company.get("website", ""),
            industry=company.get("industry", ""),
            country=company.get("country", ""),
            region=company.get("region", ""),
            parent_company=company.get("parent_company", ""),
            parent_ticker=company.get("parent_ticker", ""),
            founded=str(founded_val),
            headquarters=hq,
            ceo=ceo,
            employees=str(employees),
            market_position=company.get("market_position", {}),
            services=services,
            competitors=competitors,
            research_focus=research.get("focus_areas", []),
            priority_queries=research.get("priority_queries", []),
            details=details,
            notes=company.get("notes", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "legal_name": self.legal_name,
            "website": self.website,
            "industry": self.industry,
            "country": self.country,
            "region": self.region,
            "parent_company": self.parent_company,
            "parent_ticker": self.parent_ticker,
            "founded": self.founded,
            "headquarters": self.headquarters,
            "market_position": self.market_position,
            "services": self.services,
            "competitors": self.competitors,
            "research_focus": self.research_focus,
            "priority_queries": self.priority_queries,
            "notes": self.notes
        }


@dataclass
class MarketConfig:
    """Market configuration for batch research."""
    name: str
    country: str = ""
    region: str = ""
    industry: str = ""
    market_size: str = ""
    growth_rate: str = ""
    notes: str = ""
    key_metrics: List[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_data: Dict[str, Any]) -> "MarketConfig":
        """Create config from YAML data."""
        market = yaml_data.get("market", yaml_data)
        return cls(
            name=market.get("name", ""),
            country=market.get("country", ""),
            region=market.get("region", ""),
            industry=market.get("industry", ""),
            market_size=market.get("market_size", ""),
            growth_rate=market.get("growth_rate", ""),
            notes=market.get("notes", ""),
            key_metrics=market.get("key_metrics", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "country": self.country,
            "region": self.region,
            "industry": self.industry,
            "market_size": self.market_size,
            "growth_rate": self.growth_rate,
            "notes": self.notes,
            "key_metrics": self.key_metrics
        }


@dataclass
class ResearchResult:
    """Result of a company research operation."""
    company_name: str
    success: bool
    profile: Optional[CompanyProfile] = None
    summary: str = ""
    analysis: Dict[str, Any] = field(default_factory=dict)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    report_paths: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "success": self.success,
            "profile": self.profile.to_dict() if self.profile else None,
            "summary": self.summary,
            "sources_count": len(self.sources),
            "report_paths": self.report_paths,
            "metrics": self.metrics,
            "quality_score": self.quality_score,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }
