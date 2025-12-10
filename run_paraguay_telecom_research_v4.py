#!/usr/bin/env python3
"""
Paraguay Telecom Comprehensive Research V4

PROPERLY USES THE FULL BUILT-IN WORKFLOW SYSTEM:
- Uses research_company_comprehensive() from comprehensive_research.py
- Leverages all 15+ specialized agents (Researcher, Financial, Market, ESG, Brand, etc.)
- Uses SearchRouter with fallback chains (40+ integrations)
- Applies quality modules (contradiction detection, confidence scoring)
- Implements fallback logic when searches return 0 results
- Uses LLM routing with cost optimization

Unlike V3 which manually reimplemented everything, V4 uses the existing
infrastructure that was already built in the codebase.
"""

import os
import sys
import logging
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ParaguayResearchV4")

# ============================================================================
# Import from EXISTING comprehensive workflow system
# ============================================================================
from src.company_researcher.workflows import (
    research_company_comprehensive,
    research_with_cache,
    create_comprehensive_workflow,
)
from src.company_researcher.config import get_config
from src.company_researcher.state import (
    create_initial_state,
    create_output_state,
    OverallState,
)
from src.company_researcher.llm.smart_client import smart_completion
from src.company_researcher.integrations.search_router import SearchRouter

# ============================================================================
# Configuration
# ============================================================================
OUTPUT_BASE = Path("outputs/research")
QUALITY_TARGET = 90
SOURCE_TARGET = 200

# ============================================================================
# Fallback System - When searches fail, use LLM knowledge
# ============================================================================

FALLBACK_PROMPTS = {
    "overview": """You are a research analyst. Based on your training knowledge, provide a comprehensive company overview for {company_name}.

Include:
1. Company background and history
2. Parent company/ownership structure
3. Key business segments and services
4. Geographic presence and market coverage
5. Key leadership and organizational structure
6. Recent major developments or milestones

{context_hint}

Note: This analysis is based on training data. Verify with current sources for the most up-to-date information.""",

    "financial": """You are a financial analyst. Based on your training knowledge, analyze the financial profile of {company_name}.

Include:
1. Revenue scale and growth trends
2. Profitability indicators (margins, EBITDA if known)
3. Financial structure and debt levels
4. Key financial metrics for the industry
5. Investment considerations
6. Financial outlook

{context_hint}

Note: Financial figures should be verified with current filings and official sources.""",

    "market": """You are a market analyst. Based on your training knowledge, analyze the market position of {company_name}.

Include:
1. Market share and competitive position
2. Target customer segments
3. Product/service portfolio
4. Geographic market coverage
5. Growth opportunities
6. Market challenges

{context_hint}

Provide industry-specific context for the telecommunications/telecom sector in Paraguay.""",

    "esg": """You are an ESG analyst. Based on your training knowledge, analyze the ESG profile of {company_name}.

Include:
1. Environmental initiatives and sustainability efforts
2. Social responsibility programs
3. Corporate governance practices
4. Industry ESG benchmarks
5. Potential improvement areas
6. ESG-related opportunities or risks

{context_hint}

Consider regional and industry context for telecommunications companies in Latin America.""",

    "risk": """You are a risk analyst. Based on your training knowledge, assess the risk profile of {company_name}.

Include:
1. Market risks (competition, market saturation)
2. Regulatory risks (telecom regulations, government policies)
3. Operational risks (network, technology)
4. Financial risks (currency, debt)
5. Strategic risks (digital transformation, new entrants)
6. Overall risk assessment and grade

{context_hint}

Provide a risk score (0-100) and letter grade (A-F).""",

    "investment": """You are an investment analyst. Based on your training knowledge, create an investment thesis for {company_name}.

Include:
1. Investment recommendation (Strong Buy/Buy/Hold/Sell)
2. Bull case scenario and upside potential
3. Bear case scenario and downside risk
4. Key catalysts to watch
5. Suitable investor profiles
6. Target time horizon

{context_hint}

Consider the broader Latin American telecom market dynamics.""",

    "competitive": """You are a competitive intelligence analyst. Based on your training knowledge, analyze the competitive landscape for {company_name}.

Primary competitors: {competitors}

Include:
1. Competitive positioning vs main rivals
2. Competitive advantages and moats
3. Competitive vulnerabilities
4. Market share comparison
5. Strategic differentiation
6. Future competitive outlook

{context_hint}""",

    "brand": """You are a brand analyst. Based on your training knowledge, analyze the brand and reputation of {company_name}.

Include:
1. Brand perception and awareness
2. Customer satisfaction indicators
3. Brand strengths and differentiators
4. Areas for improvement
5. Digital presence assessment
6. Brand positioning vs competitors

{context_hint}""",
}


class ComprehensiveResearcherV4:
    """
    V4 Research System - Uses full built-in infrastructure.

    Key differences from V3:
    - Uses existing comprehensive workflow instead of reimplementing
    - Implements fallback logic when searches return zero results
    - Properly calculates quality based on source count and content
    - Uses all quality modules (contradiction detection, confidence)
    """

    def __init__(self):
        self.config = get_config()
        self.search_router = SearchRouter()

    def load_profile(self, profile_path: str) -> Dict[str, Any]:
        """Load company profile from YAML."""
        with open(profile_path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_fallback_content(
        self,
        company_name: str,
        section: str,
        context_hint: str = "",
        competitors: List[str] = None
    ) -> str:
        """Generate content using LLM knowledge when searches fail."""
        logger.info(f"[FALLBACK] Generating {section} using LLM knowledge...")

        prompt_template = FALLBACK_PROMPTS.get(section, FALLBACK_PROMPTS["overview"])
        prompt = prompt_template.format(
            company_name=company_name,
            context_hint=context_hint,
            competitors=", ".join(competitors) if competitors else "Unknown"
        )

        try:
            result = smart_completion(
                prompt=prompt,
                task_type="synthesis",
                max_tokens=4000
            )
            content = result.content if hasattr(result, 'content') else str(result)

            # Add fallback disclaimer
            disclaimer = "\n\n---\n*Note: This section was generated using AI knowledge due to limited search results. Verify with current official sources.*\n"
            return content + disclaimer

        except Exception as e:
            logger.error(f"Fallback generation failed for {section}: {e}")
            return f"*Analysis unavailable for {section}*"

    def run_with_fallback(self, company_name: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive research with fallback support.

        This method:
        1. First tries the full comprehensive workflow
        2. If zero sources are retrieved, uses LLM knowledge fallback
        3. Adjusts quality scores to reflect actual content quality
        """
        start_time = datetime.now()
        competitors = [c.get("name", "") for c in profile.get("competitors", [])]

        logger.info("=" * 70)
        logger.info(f"  V4 COMPREHENSIVE RESEARCH: {company_name}")
        logger.info(f"  Using FULL built-in workflow system")
        logger.info("=" * 70)

        # Try the comprehensive workflow first
        try:
            logger.info("[PHASE 1] Running comprehensive workflow...")
            result = research_company_comprehensive(company_name)

            # Check if we got meaningful results
            sources_count = result.get("metrics", {}).get("sources_count", 0)

            if sources_count >= 10:
                # Good results - return as is
                logger.info(f"[OK] Comprehensive workflow succeeded with {sources_count} sources")
                return self._enhance_result(result, company_name, profile)
            else:
                # Low sources - supplement with fallback
                logger.warning(f"[WARNING] Only {sources_count} sources retrieved, applying fallback...")
                return self._apply_fallback(result, company_name, profile, competitors)

        except Exception as e:
            logger.error(f"[ERROR] Comprehensive workflow failed: {e}")
            logger.info("[FALLBACK] Using LLM knowledge generation...")
            return self._full_fallback_research(company_name, profile, competitors, start_time)

    def _enhance_result(
        self,
        result: Dict[str, Any],
        company_name: str,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance successful results with additional metadata."""
        # Recalculate quality score based on actual content
        sources_count = result.get("metrics", {}).get("sources_count", 0)

        # Quality factors
        source_quality = min(40, sources_count * 0.2)  # Max 40 points for sources
        content_quality = 60 if sources_count >= 50 else (sources_count / 50) * 60

        adjusted_quality = int(source_quality + content_quality)

        result["metrics"]["quality_score"] = adjusted_quality
        result["metrics"]["sources_target_met"] = sources_count >= SOURCE_TARGET
        result["metrics"]["quality_target_met"] = adjusted_quality >= QUALITY_TARGET

        return result

    def _apply_fallback(
        self,
        result: Dict[str, Any],
        company_name: str,
        profile: Dict[str, Any],
        competitors: List[str]
    ) -> Dict[str, Any]:
        """Apply fallback generation for sections with missing content."""
        logger.info("[PHASE 2] Supplementing with fallback content...")

        output_dir = Path(result.get("report_path", "")).parent
        if not output_dir.exists():
            output_dir = OUTPUT_BASE / company_name.lower().replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

        company_info = profile.get("company", profile)
        context_hint = f"This is a {company_info.get('industry', 'telecom')} company in {company_info.get('country', 'Paraguay')}."

        # Generate fallback content for each section
        sections_to_fallback = [
            ("02_company_overview.md", "overview", "Company Overview"),
            ("03_financials.md", "financial", "Financial Analysis"),
            ("04_market_position.md", "market", "Market Analysis"),
            ("05_competitive_analysis.md", "competitive", "Competitive Landscape"),
            ("06_strategy.md", "brand", "Brand & Strategy"),
            ("08_esg_analysis.md", "esg", "ESG Analysis"),
            ("09_risk_assessment.md", "risk", "Risk Assessment"),
            ("10_investment_thesis.md", "investment", "Investment Thesis"),
        ]

        fallback_content = {}
        for filename, section_key, title in sections_to_fallback:
            filepath = output_dir / filename

            # Check if file is empty or has placeholder content
            needs_fallback = True
            if filepath.exists():
                content = filepath.read_text(encoding='utf-8')
                if len(content) > 500 and "don't see any search results" not in content.lower():
                    needs_fallback = False

            if needs_fallback:
                logger.info(f"  Generating fallback for: {section_key}")
                fallback = self.generate_fallback_content(
                    company_name,
                    section_key,
                    context_hint,
                    competitors
                )
                fallback_content[section_key] = fallback

                # Write fallback content
                filepath.write_text(
                    f"# {company_name} - {title}\n\n{fallback}",
                    encoding='utf-8'
                )

        # Regenerate full report with fallback content
        self._regenerate_full_report(output_dir, company_name, fallback_content)

        # Adjust metrics for fallback usage
        result["metrics"]["used_fallback"] = True
        result["metrics"]["fallback_sections"] = list(fallback_content.keys())

        # Penalize quality score for using fallback
        original_quality = result.get("metrics", {}).get("quality_score", 75)
        fallback_penalty = len(fallback_content) * 5  # -5 per fallback section
        result["metrics"]["quality_score"] = max(30, original_quality - fallback_penalty)

        return result

    def _full_fallback_research(
        self,
        company_name: str,
        profile: Dict[str, Any],
        competitors: List[str],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Full fallback research when workflow completely fails."""
        logger.info("[FULL FALLBACK] Generating complete report from LLM knowledge...")

        output_dir = OUTPUT_BASE / company_name.lower().replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)

        company_info = profile.get("company", profile)
        context_hint = f"This is a {company_info.get('industry', 'telecom')} company in {company_info.get('country', 'Paraguay')}."

        # Generate all sections
        sections = {}
        section_configs = [
            ("overview", "02_company_overview.md", "Company Overview"),
            ("financial", "03_financials.md", "Financial Analysis"),
            ("market", "04_market_position.md", "Market Analysis"),
            ("competitive", "05_competitive_analysis.md", "Competitive Landscape"),
            ("brand", "06_strategy.md", "Brand & Strategy"),
            ("esg", "08_esg_analysis.md", "ESG Analysis"),
            ("risk", "09_risk_assessment.md", "Risk Assessment"),
            ("investment", "10_investment_thesis.md", "Investment Thesis"),
        ]

        for section_key, filename, title in section_configs:
            logger.info(f"  Generating: {section_key}")
            content = self.generate_fallback_content(
                company_name,
                section_key,
                context_hint,
                competitors
            )
            sections[section_key] = content

            filepath = output_dir / filename
            filepath.write_text(
                f"# {company_name} - {title}\n\n{content}",
                encoding='utf-8'
            )

            # Small delay to avoid rate limits
            time.sleep(1)

        # Generate executive summary
        logger.info("  Generating: executive summary")
        summary_prompt = f"""Create an executive summary for {company_name} synthesizing this research:

Company Overview: {sections.get('overview', '')[:1000]}

Financial Analysis: {sections.get('financial', '')[:800]}

Market Position: {sections.get('market', '')[:800]}

Create a comprehensive executive summary (500-800 words)."""

        try:
            result = smart_completion(
                prompt=summary_prompt,
                task_type="synthesis",
                max_tokens=2000
            )
            executive_summary = result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            executive_summary = f"*Executive summary unavailable: {e}*"

        sections["executive_summary"] = executive_summary

        # Save executive summary
        (output_dir / "01_executive_summary.md").write_text(
            f"# {company_name} - Executive Summary\n\n{executive_summary}",
            encoding='utf-8'
        )

        # Save sources (empty since fallback)
        (output_dir / "07_sources.md").write_text(
            f"# {company_name} - Sources\n\n*Note: This report was generated using AI knowledge due to search limitations. No external sources were available.*",
            encoding='utf-8'
        )

        # Generate full report
        self._regenerate_full_report(output_dir, company_name, sections)

        duration = (datetime.now() - start_time).total_seconds()

        # Save metrics
        import json
        metrics = {
            "company_name": company_name,
            "quality_score": 40,  # Low score for full fallback
            "sources_count": 0,
            "used_fallback": True,
            "fallback_sections": list(sections.keys()),
            "duration_seconds": duration,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "warning": "Report generated using AI knowledge only - verify with official sources"
        }
        (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding='utf-8')

        logger.info(f"[OK] Fallback report saved to {output_dir}")

        return {
            "company_name": company_name,
            "report_path": str(output_dir / "00_full_report.md"),
            "output_dir": str(output_dir),
            "metrics": metrics
        }

    def _regenerate_full_report(
        self,
        output_dir: Path,
        company_name: str,
        sections: Dict[str, str]
    ):
        """Regenerate the full report combining all sections."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Read existing sections if available
        def read_section(filename: str) -> str:
            filepath = output_dir / filename
            if filepath.exists():
                content = filepath.read_text(encoding='utf-8')
                # Remove the header line
                lines = content.split('\n')
                return '\n'.join(lines[2:]) if len(lines) > 2 else content
            return "*Section not available*"

        full_report = f"""# {company_name} - Comprehensive Research Report

*Generated on {timestamp}*
*Research Mode: V4 Comprehensive with Fallback Support*

---

## Executive Summary

{sections.get('executive_summary', read_section('01_executive_summary.md'))}

---

## Company Overview

{sections.get('overview', read_section('02_company_overview.md'))}

---

## Financial Analysis

{sections.get('financial', read_section('03_financials.md'))}

---

## Market Position

{sections.get('market', read_section('04_market_position.md'))}

---

## Competitive Landscape

{sections.get('competitive', read_section('05_competitive_analysis.md'))}

---

## Brand & Strategy

{sections.get('brand', read_section('06_strategy.md'))}

---

## ESG Analysis

{sections.get('esg', read_section('08_esg_analysis.md'))}

---

## Risk Assessment

{sections.get('risk', read_section('09_risk_assessment.md'))}

---

## Investment Thesis

{sections.get('investment', read_section('10_investment_thesis.md'))}

---

## Sources

{read_section('07_sources.md')}

---

*This report was generated by Company Researcher V4 (Comprehensive with Fallback)*
"""

        (output_dir / "00_full_report.md").write_text(full_report, encoding='utf-8')

    def research_company(self, profile_path: str) -> Dict[str, Any]:
        """Main entry point for researching a company."""
        profile = self.load_profile(profile_path)
        company = profile.get("company", profile)
        company_name = company.get("name", "Unknown")

        return self.run_with_fallback(company_name, profile)


def main():
    """Main entry point."""
    print("=" * 70)
    print("  PARAGUAY TELECOM COMPREHENSIVE RESEARCH V4")
    print("  Using FULL Built-in Workflow System")
    print("  With Fallback Support for Zero-Source Scenarios")
    print("=" * 70)
    print()
    print("V4 Improvements over V3:")
    print("  - Uses existing research_company_comprehensive() workflow")
    print("  - Leverages all 15+ specialized agents")
    print("  - Applies quality modules (contradiction detection, confidence)")
    print("  - Implements fallback when searches return 0 results")
    print("  - Properly calculates quality based on actual content")
    print()
    print("=" * 70)

    # Company profiles
    profiles = [
        "research_targets/paraguay_telecom/tigo_paraguay.yaml",
        "research_targets/paraguay_telecom/personal_paraguay.yaml",
    ]

    researcher = ComprehensiveResearcherV4()
    results = []

    for profile_path in profiles:
        if Path(profile_path).exists():
            try:
                print(f"\n{'='*60}")
                print(f"Starting research: {profile_path}")
                print(f"{'='*60}")
                result = researcher.research_company(profile_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Research failed for {profile_path}: {e}")
                import traceback
                traceback.print_exc()
        else:
            logger.error(f"Profile not found: {profile_path}")

    # Final summary
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY - V4 COMPREHENSIVE RESEARCH")
    print("=" * 70)

    for r in results:
        metrics = r.get("metrics", {})
        print(f"\n  {r.get('company_name', 'Unknown')}:")
        print(f"    Quality Score: {metrics.get('quality_score', 0)}/100")
        print(f"    Sources: {metrics.get('sources_count', 0)}")
        print(f"    Used Fallback: {metrics.get('used_fallback', False)}")
        if metrics.get('fallback_sections'):
            print(f"    Fallback Sections: {len(metrics.get('fallback_sections', []))}")
        print(f"    Duration: {metrics.get('duration_seconds', 0):.1f}s")
        print(f"    Output: {r.get('output_dir', 'N/A')}")

    if results:
        avg_quality = sum(r.get("metrics", {}).get("quality_score", 0) for r in results) / len(results)
        total_sources = sum(r.get("metrics", {}).get("sources_count", 0) for r in results)
        print(f"\n  Totals:")
        print(f"    Average Quality: {avg_quality:.1f}/100")
        print(f"    Total Sources: {total_sources}")
        print(f"    Companies Researched: {len(results)}")

    print("\n" + "=" * 70)
    print("  V4 Research Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
