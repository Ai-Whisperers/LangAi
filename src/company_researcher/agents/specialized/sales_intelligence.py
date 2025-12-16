"""
Sales Intelligence Agent (Phase 15.1).

Sales-focused intelligence capabilities:
- Lead qualification signals
- Decision maker identification
- Pain point analysis
- Buying intent signals
- Competitive displacement opportunities
- Account-based intelligence

This agent generates actionable sales intelligence for B2B targeting.

Refactored to use BaseSpecialistAgent for:
- Reduced code duplication
- Consistent agent interface
- Centralized LLM calling and cost tracking
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...config import get_config
from ...llm.client_factory import calculate_cost
from ...state import OverallState
from ...types import BuyingStage, CompanySize, LeadScore  # Centralized enums
from ..base import create_empty_result, get_agent_logger
from ..base.specialist import BaseSpecialistAgent, ParsingMixin

# ============================================================================
# Data Models
# ============================================================================
# Note: LeadScore, BuyingStage, CompanySize imported from types.py


@dataclass
class DecisionMaker:
    """A potential decision maker or influencer."""

    title: str
    department: str
    influence_level: str  # HIGH/MEDIUM/LOW
    likely_concerns: List[str] = field(default_factory=list)
    engagement_approach: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "department": self.department,
            "influence_level": self.influence_level,
            "concerns": self.likely_concerns,
            "approach": self.engagement_approach,
        }


@dataclass
class PainPoint:
    """An identified pain point."""

    description: str
    severity: str  # HIGH/MEDIUM/LOW
    evidence: str
    solution_fit: str
    urgency: str  # IMMEDIATE/SHORT_TERM/LONG_TERM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "solution_fit": self.solution_fit,
            "urgency": self.urgency,
        }


@dataclass
class BuyingSignal:
    """A detected buying signal."""

    signal_type: str
    description: str
    strength: str  # STRONG/MODERATE/WEAK
    source: str
    action_required: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.signal_type,
            "description": self.description,
            "strength": self.strength,
            "source": self.source,
            "action": self.action_required,
        }


@dataclass
class SalesIntelligenceResult:
    """Complete sales intelligence result."""

    company_name: str
    lead_score: LeadScore = LeadScore.COLD
    buying_stage: BuyingStage = BuyingStage.UNKNOWN
    company_size: CompanySize = CompanySize.MID_MARKET
    decision_makers: List[DecisionMaker] = field(default_factory=list)
    pain_points: List[PainPoint] = field(default_factory=list)
    buying_signals: List[BuyingSignal] = field(default_factory=list)
    competitive_displacement: List[str] = field(default_factory=list)
    key_triggers: List[str] = field(default_factory=list)
    recommended_approach: str = ""
    talking_points: List[str] = field(default_factory=list)
    objection_handlers: Dict[str, str] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    analysis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "lead_score": self.lead_score.value,
            "buying_stage": self.buying_stage.value,
            "company_size": self.company_size.value,
            "decision_makers": [d.to_dict() for d in self.decision_makers],
            "pain_points": [p.to_dict() for p in self.pain_points],
            "buying_signals": [s.to_dict() for s in self.buying_signals],
            "competitive_displacement": self.competitive_displacement,
            "key_triggers": self.key_triggers,
            "recommended_approach": self.recommended_approach,
            "talking_points": self.talking_points,
            "objection_handlers": self.objection_handlers,
            "next_steps": self.next_steps,
        }


# ============================================================================
# Prompts
# ============================================================================

SALES_INTELLIGENCE_PROMPT = """You are an expert sales intelligence analyst generating actionable B2B sales insights.

**TARGET COMPANY:** {company_name}

**AVAILABLE DATA:**
{search_results}

**TASK:** Generate comprehensive sales intelligence for prospecting and account planning.

**STRUCTURE YOUR ANALYSIS:**

### 1. Account Overview
- **Company Size:** [ENTERPRISE/MID_MARKET/SMB/STARTUP]
- **Industry:** [Primary industry]
- **Estimated Revenue:** [If available]
- **Growth Stage:** [Growing/Stable/Declining]
- **Tech Stack Indicators:** [Relevant technologies]

### 2. Lead Qualification
- **Lead Score:** [HOT/WARM/COLD/NOT_QUALIFIED]
- **Buying Stage:** [AWARENESS/CONSIDERATION/DECISION/UNKNOWN]
- **Qualification Rationale:** [Why this score]

### 3. Decision Makers & Influencers
For each key stakeholder:

**[Title/Role]:**
- Department: [Department]
- Influence Level: [HIGH/MEDIUM/LOW]
- Likely Concerns: [List concerns]
- Engagement Approach: [How to approach]

Identify at least 3-5 relevant stakeholders.

### 4. Pain Points Analysis
| Pain Point | Severity | Evidence | Solution Fit | Urgency |
|------------|----------|----------|--------------|---------|
| [Pain 1] | [H/M/L] | [Evidence] | [Fit description] | [Immediate/Short/Long] |
...

### 5. Buying Signals
Detected signals indicating purchase readiness:

| Signal Type | Description | Strength | Source | Action Required |
|-------------|-------------|----------|--------|-----------------|
| [Type] | [Description] | [STRONG/MODERATE/WEAK] | [Source] | [Action] |
...

Signal types: Hiring, Technology Change, Funding, Expansion, Leadership Change, Pain Expression

### 6. Competitive Intelligence
- **Current Solutions:** [What they might be using]
- **Displacement Opportunities:** [Why they might switch]
- **Competitive Weaknesses to Exploit:** [Competitor gaps]

### 7. Key Triggers
Events or situations that could trigger a buying decision:
1. [Trigger 1]
2. [Trigger 2]
...

### 8. Recommended Sales Approach
- **Primary Strategy:** [Approach description]
- **Entry Point:** [Best way to initiate contact]
- **Value Proposition Focus:** [What to emphasize]

### 9. Talking Points
Key messages for sales conversations:
1. [Talking point 1]
2. [Talking point 2]
...

### 10. Objection Handlers
| Objection | Response Strategy |
|-----------|------------------|
| "[Objection 1]" | [Response] |
| "[Objection 2]" | [Response] |
...

### 11. Recommended Next Steps
Prioritized action items:
1. [Step 1] - Priority: [HIGH/MEDIUM]
2. [Step 2] - Priority: [HIGH/MEDIUM]
...

**REQUIREMENTS:**
- Focus on actionable intelligence
- Be specific about stakeholders and approaches
- Identify concrete buying signals
- Provide realistic objection handlers
- Make recommendations data-driven

Begin your sales intelligence analysis:"""


# ============================================================================
# Sales Intelligence Agent
# ============================================================================


class SalesIntelligenceAgent(BaseSpecialistAgent[SalesIntelligenceResult], ParsingMixin):
    """
    Sales Intelligence Agent for B2B prospecting.

    Inherits from:
    - BaseSpecialistAgent: Common agent functionality (LLM calls, formatting, cost tracking)
    - ParsingMixin: Standardized extraction methods

    Generates:
    - Lead qualification
    - Decision maker mapping
    - Pain point analysis
    - Buying signals
    - Sales strategy recommendations

    Usage:
        agent = SalesIntelligenceAgent()
        result = agent.analyze(  # Uses base class analyze() method
            company_name="Tesla",
            search_results=results
        )
    """

    # Class attributes for BaseSpecialistAgent
    agent_name = "sales_intelligence"

    def _get_prompt(self, company_name: str, formatted_results: str) -> str:
        """Build the sales intelligence prompt."""
        return SALES_INTELLIGENCE_PROMPT.format(
            company_name=company_name, search_results=formatted_results
        )

    def _parse_analysis(self, company_name: str, analysis: str) -> SalesIntelligenceResult:
        """Parse analysis into structured result."""
        result = SalesIntelligenceResult(company_name=company_name)

        # Extract lead score
        result.lead_score = self._extract_lead_score(analysis)

        # Extract buying stage
        result.buying_stage = self._extract_buying_stage(analysis)

        # Extract company size
        result.company_size = self._extract_company_size(analysis)

        # Extract decision makers
        result.decision_makers = self._extract_decision_makers(analysis)

        # Extract pain points
        result.pain_points = self._extract_pain_points(analysis)

        # Extract buying signals
        result.buying_signals = self._extract_buying_signals(analysis)

        # Extract lists
        result.competitive_displacement = self._extract_list(analysis, "Displacement")
        result.key_triggers = self._extract_list(analysis, "Trigger")
        result.talking_points = self._extract_list(analysis, "Talking")
        result.next_steps = self._extract_list(analysis, "Step")

        # Extract approach
        result.recommended_approach = self._extract_approach(analysis)

        return result

    def _extract_lead_score(self, analysis: str) -> LeadScore:
        """Extract lead score."""
        analysis_upper = analysis.upper()
        if "LEAD SCORE" in analysis_upper:
            if "HOT" in analysis_upper:
                return LeadScore.HOT
            elif "WARM" in analysis_upper:
                return LeadScore.WARM
            elif "NOT_QUALIFIED" in analysis_upper or "NOT QUALIFIED" in analysis_upper:
                return LeadScore.NOT_QUALIFIED
        return LeadScore.COLD

    def _extract_buying_stage(self, analysis: str) -> BuyingStage:
        """Extract buying stage."""
        analysis_upper = analysis.upper()
        if "DECISION" in analysis_upper and "STAGE" in analysis_upper:
            return BuyingStage.DECISION
        elif "CONSIDERATION" in analysis_upper:
            return BuyingStage.CONSIDERATION
        elif "AWARENESS" in analysis_upper:
            return BuyingStage.AWARENESS
        return BuyingStage.UNKNOWN

    def _extract_company_size(self, analysis: str) -> CompanySize:
        """Extract company size."""
        analysis_upper = analysis.upper()
        if "ENTERPRISE" in analysis_upper:
            return CompanySize.ENTERPRISE
        elif "MID_MARKET" in analysis_upper or "MID-MARKET" in analysis_upper:
            return CompanySize.MID_MARKET
        elif "SMB" in analysis_upper:
            return CompanySize.SMB
        elif "STARTUP" in analysis_upper:
            return CompanySize.STARTUP
        return CompanySize.MID_MARKET

    def _extract_decision_makers(self, analysis: str) -> List[DecisionMaker]:
        """Extract decision makers."""
        makers = []
        common_titles = [
            "CEO",
            "CTO",
            "CFO",
            "CIO",
            "VP",
            "Director",
            "Head of",
            "Manager",
            "Chief",
        ]

        lines = analysis.split("\n")
        for line in lines:
            for title in common_titles:
                if title in line and (":" in line or "**" in line):
                    makers.append(
                        DecisionMaker(
                            title=title,
                            department="Executive" if "C" == title[0] else "Operations",
                            influence_level="HIGH" if "C" == title[0] else "MEDIUM",
                        )
                    )
                    break

        return makers[:5]

    def _extract_pain_points(self, analysis: str) -> List[PainPoint]:
        """Extract pain points."""
        points = []
        if "Pain Point" in analysis:
            # Look for table rows
            lines = analysis.split("\n")
            for line in lines:
                if "|" in line and not "Pain Point" in line and not "---" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 3:
                        points.append(
                            PainPoint(
                                description=parts[0],
                                severity=parts[1] if len(parts) > 1 else "MEDIUM",
                                evidence=parts[2] if len(parts) > 2 else "",
                                solution_fit=parts[3] if len(parts) > 3 else "",
                                urgency=parts[4] if len(parts) > 4 else "SHORT_TERM",
                            )
                        )
        return points[:5]

    def _extract_buying_signals(self, analysis: str) -> List[BuyingSignal]:
        """Extract buying signals."""
        signals = []
        signal_types = ["Hiring", "Technology", "Funding", "Expansion", "Leadership"]

        for signal_type in signal_types:
            if signal_type.lower() in analysis.lower():
                signals.append(
                    BuyingSignal(
                        signal_type=signal_type,
                        description=f"{signal_type} activity detected",
                        strength="MODERATE",
                        source="research",
                        action_required="Follow up",
                    )
                )

        return signals[:5]

    def _extract_list(self, analysis: str, keyword: str) -> List[str]:
        """Extract items containing keyword using ParsingMixin."""
        # Delegate to ParsingMixin.extract_keyword_list
        return self.extract_keyword_list(analysis, keyword, max_items=5)

    def _extract_approach(self, analysis: str) -> str:
        """Extract recommended approach using ParsingMixin."""
        # Use ParsingMixin.extract_section for standardized extraction
        result = self.extract_section(analysis, "Recommended", max_length=500)
        return result if result else "Consultative selling approach recommended"


# ============================================================================
# Agent Node Function
# ============================================================================


def sales_intelligence_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Sales Intelligence Agent Node.

    Args:
        state: Current workflow state

    Returns:
        State update with sales intelligence
    """
    logger = get_agent_logger("sales_intelligence")
    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    with logger.agent_run(company_name):
        if not search_results:
            logger.no_data()
            return create_empty_result("sales")

        logger.analyzing(len(search_results))

        agent = SalesIntelligenceAgent(config)
        result = agent.analyze(company_name, search_results)
        cost = calculate_cost(500, 1500)

        logger.info(f"Lead Score: {result.lead_score.value}")
        logger.info(f"Buying Stage: {result.buying_stage.value}")
        logger.info(f"Decision Makers: {len(result.decision_makers)}")
        logger.complete(cost=cost)

        return {
            "agent_outputs": {
                "sales": {**result.to_dict(), "analysis": result.analysis, "cost": cost}
            },
            "total_cost": cost,
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_sales_intelligence_agent() -> SalesIntelligenceAgent:
    """Create a Sales Intelligence Agent instance."""
    return SalesIntelligenceAgent()
