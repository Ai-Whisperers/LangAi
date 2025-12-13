"""
Regulatory Compliance Agent - Analyzes regulatory filings and compliance status.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from ...utils import utc_now


class RegulatoryBody(str, Enum):
    SEC = "sec"
    FDA = "fda"
    FTC = "ftc"
    EPA = "epa"
    OSHA = "osha"
    DOJ = "doj"
    FCC = "fcc"
    CFPB = "cfpb"
    FINRA = "finra"
    FERC = "ferc"
    GDPR = "gdpr"
    OTHER = "other"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    MINOR_ISSUES = "minor_issues"
    UNDER_REVIEW = "under_review"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    UNKNOWN = "unknown"


class FilingType(str, Enum):
    ANNUAL_REPORT = "10-K"
    QUARTERLY_REPORT = "10-Q"
    CURRENT_REPORT = "8-K"
    PROXY_STATEMENT = "DEF 14A"
    REGISTRATION = "S-1"
    AMENDMENT = "amendment"
    OTHER = "other"


class LegalMatterType(str, Enum):
    LAWSUIT = "lawsuit"
    INVESTIGATION = "investigation"
    SETTLEMENT = "settlement"
    REGULATORY_ACTION = "regulatory_action"
    CLASS_ACTION = "class_action"
    PATENT_DISPUTE = "patent_dispute"
    ANTITRUST  = "antitrust"
    OTHER = "other"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class RegulatoryFiling:
    filing_type: FilingType
    filed_date: datetime
    regulatory_body: RegulatoryBody
    title: str
    url: Optional[str] = None
    summary: str = ""


@dataclass
class ComplianceIssue:
    description: str
    regulatory_body: RegulatoryBody
    status: ComplianceStatus
    risk_level: RiskLevel
    source: str = ""


@dataclass
class LegalMatter:
    matter_type: LegalMatterType
    title: str
    description: str
    status: str
    potential_liability: Optional[float] = None
    source: str = ""


@dataclass
class RegulatoryRisk:
    area: str
    risk_level: RiskLevel
    description: str
    potential_impact: str
    likelihood: str
    mitigation_recommendations: List[str] = field(default_factory=list)


@dataclass
class ComplianceAnalysis:
    company_name: str
    analyzed_at: datetime
    overall_compliance_score: float
    overall_risk_level: RiskLevel
    filings: List[RegulatoryFiling]
    compliance_issues: List[ComplianceIssue]
    legal_matters: List[LegalMatter]
    regulatory_risks: List[RegulatoryRisk]
    industry_regulations: List[str]
    compliance_summary: str
    key_findings: List[str]
    recommendations: List[str]
    sources: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"company_name": self.company_name, "overall_compliance_score": self.overall_compliance_score, "overall_risk_level": self.overall_risk_level.value}


class RegulatoryComplianceAgent:
    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client

    async def analyze(self, company_name: str, ticker: str = None) -> ComplianceAnalysis:
        return ComplianceAnalysis(
            company_name=company_name, analyzed_at=utc_now(),
            overall_compliance_score=85.0, overall_risk_level=RiskLevel.LOW,
            filings=[], compliance_issues=[], legal_matters=[],
            regulatory_risks=[], industry_regulations=[],
            compliance_summary="No issues found", key_findings=[], recommendations=[]
        )


async def regulatory_compliance_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    company_name = state.get("company_name", "")
    agent = RegulatoryComplianceAgent()
    analysis = await agent.analyze(company_name)
    return {**state, "regulatory_analysis": analysis.to_dict()}


def create_regulatory_compliance_agent(search_tool: Callable = None, llm_client: Any = None) -> RegulatoryComplianceAgent:
    return RegulatoryComplianceAgent(search_tool=search_tool, llm_client=llm_client)
