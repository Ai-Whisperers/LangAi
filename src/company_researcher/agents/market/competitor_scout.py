"""
Competitor Scout Agent (Phase 9).

Provides comprehensive competitive intelligence including:
- Competitor identification and classification
- Tech stack analysis and comparison
- Threat level assessment
- Competitive positioning (SWOT-style)
- GitHub activity metrics (for tech companies)
- Patent portfolio analysis
- Customer sentiment comparison
"""

from typing import Dict, Any, List, Optional
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState
from ..tools.competitor_analysis_utils import (
    CompetitorType,
    ThreatLevel,
    classify_competitor,
    assess_threat_level,
    TechStackAnalyzer,
    GitHubMetrics,
    analyze_competitive_positioning,
    analyze_patent_portfolio,
    aggregate_review_sentiment
)


# ==============================================================================
# Prompts
# ==============================================================================

COMPETITOR_SCOUT_PROMPT = """You are an expert competitive intelligence analyst specializing in deep competitor research.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide comprehensive competitive intelligence covering all key competitors and their positioning.

**STRUCTURE YOUR ANALYSIS:**

### 1. Competitor Identification
For each major competitor, provide:

**Competitor Name**: [Company Name]
- **Type**: DIRECT | INDIRECT | SUBSTITUTE | POTENTIAL
- **Description**: Brief overview of the competitor
- **Products/Services**: Key offerings that compete
- **Market Overlap**: HIGH | MODERATE | LOW

Identify at least 3-5 key competitors.

### 2. Competitive Landscape Overview

**Market Structure**:
- Number of major competitors
- Market concentration (fragmented/moderate/concentrated)
- Market leaders and their approximate shares

**Competitive Intensity**:
- Overall intensity: LOW | MODERATE | HIGH | INTENSE
- Key battleground areas
- Differentiation factors

### 3. Competitor Profiles (Top 3)

For each top competitor:

**[Competitor Name]**

**Company Overview**:
- Founded/Headquarters
- Size (employees, revenue if known)
- Funding status

**Products & Technology**:
- Key products
- Technology approach
- Recent innovations

**Market Position**:
- Market share estimate
- Target segments
- Pricing strategy

**Strengths**:
- List 3-5 key strengths

**Weaknesses**:
- List 2-3 known weaknesses

**Threat Level**: CRITICAL | HIGH | MODERATE | LOW | EMERGING
- Reasoning for assessment

### 4. Tech Stack Comparison (if applicable)

Compare technology choices:
- Frontend technologies
- Backend/infrastructure
- Data/analytics tools
- Key differentiators

### 5. Competitive Positioning Matrix

How does {company_name} compare to competitors on:

| Factor | {company_name} | Competitor A | Competitor B |
|--------|----------------|--------------|--------------|
| Price | ... | ... | ... |
| Features | ... | ... | ... |
| Brand | ... | ... | ... |
| Innovation | ... | ... | ... |
| Support | ... | ... | ... |

### 6. Strategic Implications

**Opportunities**:
- Gaps in competitor offerings
- Underserved segments
- Competitive advantages to leverage

**Threats**:
- Competitor moves to watch
- Potential new entrants
- Disruptive risks

**Recommendations**:
- How to differentiate
- Competitive response strategies
- Areas requiring defensive investment

**REQUIREMENTS:**
- Be specific about competitor names and details
- Use verifiable information where possible
- Clearly indicate estimates vs confirmed data
- Provide actionable strategic insights
- Focus on the most relevant competitors

Begin your competitive intelligence analysis:"""


# ==============================================================================
# Competitor Scout Agent
# ==============================================================================

def competitor_scout_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Competitor Scout Agent Node: Comprehensive competitive intelligence.

    Analyzes:
    1. Competitor identification and classification
    2. Competitive landscape overview
    3. Detailed competitor profiles
    4. Tech stack comparison
    5. Competitive positioning matrix
    6. Strategic implications

    Args:
        state: Current workflow state

    Returns:
        State update with competitive intelligence analysis
    """
    print("\n" + "=" * 70)
    print("[AGENT: Competitor Scout] Competitive intelligence analysis...")
    print("=" * 70)

    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Competitor] WARNING: No search results available!")
        return {
            "agent_outputs": {
                "competitor": {
                    "analysis": "No search results available for competitor analysis",
                    "data_extracted": False,
                    "competitors_found": 0,
                    "cost": 0.0
                }
            }
        }

    print(f"[Competitor] Analyzing competitors for {company_name}...")
    print(f"[Competitor] Processing {len(search_results)} sources...")

    # Create comprehensive analysis prompt
    prompt = create_competitor_analysis_prompt(company_name, search_results)

    # Call LLM for analysis
    client = Anthropic(api_key=config.anthropic_api_key)
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=1500,  # Comprehensive competitor analysis
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    competitor_analysis = response.content[0].text
    cost = config.calculate_llm_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    # Extract structured data from analysis
    extracted_data = extract_competitor_data(competitor_analysis)

    print(f"[Competitor] Found {extracted_data['competitor_count']} competitors")
    print(f"[Competitor] Analysis complete - ${cost:.4f}")
    print("=" * 70)

    # Create agent output
    agent_output = {
        "analysis": competitor_analysis,
        "data_extracted": True,
        "competitors_found": extracted_data["competitor_count"],
        "threat_summary": extracted_data["threat_summary"],
        "competitive_intensity": extracted_data["competitive_intensity"],
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    return {
        "agent_outputs": {"competitor": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }


# ==============================================================================
# Helper Functions
# ==============================================================================

def create_competitor_analysis_prompt(
    company_name: str,
    search_results: list
) -> str:
    """
    Create comprehensive competitor analysis prompt.

    Args:
        company_name: Name of company
        search_results: Web search results

    Returns:
        Formatted prompt string
    """
    # Format search results with focus on competitor-relevant content
    formatted_results = format_competitor_search_results(search_results)

    # Create prompt
    prompt = COMPETITOR_SCOUT_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    return prompt


def format_competitor_search_results(search_results: list) -> str:
    """
    Format search results with emphasis on competitor-relevant content.

    Args:
        search_results: List of search result dictionaries

    Returns:
        Formatted string
    """
    # Prioritize results with competitor-related keywords
    competitor_keywords = [
        "competitor", "alternative", "versus", "vs", "compare",
        "rival", "competition", "market share", "similar",
        "against", "better than", "switch from"
    ]

    # Score results by relevance
    scored_results = []
    for result in search_results:
        content = result.get("content", "").lower()
        title = result.get("title", "").lower()

        # Count competitor keyword matches
        relevance_score = sum(
            1 for keyword in competitor_keywords
            if keyword in content or keyword in title
        )

        # Boost for explicit competitor mentions
        if "competitor" in content or "alternative" in content:
            relevance_score += 3

        scored_results.append((relevance_score, result))

    # Sort by relevance (descending)
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Format top results
    formatted = []
    for i, (score, result) in enumerate(scored_results[:15], 1):
        formatted.append(
            f"Source {i} [Competitor Relevance: {score}]: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')[:500]}...\n"
        )

    return "\n".join(formatted) if formatted else "No competitor-specific results available."


def extract_competitor_data(analysis_text: str) -> Dict[str, Any]:
    """
    Extract structured competitor data from analysis text.

    Args:
        analysis_text: Competitor analysis text from LLM

    Returns:
        Dictionary with extracted data:
        - competitor_count: Number of competitors identified
        - threat_summary: Summary of threat levels
        - competitive_intensity: Overall market intensity
    """
    data = {
        "competitor_count": 0,
        "threat_summary": {},
        "competitive_intensity": None
    }

    text_upper = analysis_text.upper()

    # Count competitor mentions (look for "Competitor Name" patterns)
    # Simple heuristic: count major section headers
    competitor_markers = ["**COMPETITOR", "### COMPETITOR", "COMPETITOR A", "COMPETITOR B", "COMPETITOR C"]
    for marker in competitor_markers:
        if marker in text_upper:
            data["competitor_count"] += 1

    # More robust counting: look for threat level assignments
    threat_levels = ["CRITICAL", "HIGH", "MODERATE", "LOW", "EMERGING"]
    for level in threat_levels:
        pattern = f"THREAT LEVEL: {level}"
        count = text_upper.count(pattern)
        if count > 0:
            data["threat_summary"][level.lower()] = count
            data["competitor_count"] = max(data["competitor_count"], sum(data["threat_summary"].values()))

    # Extract competitive intensity
    intensity_keywords = {
        "INTENSE": ["INTENSE COMPETITION", "HIGHLY COMPETITIVE", "INTENSE RIVALRY"],
        "HIGH": ["HIGH COMPETITION", "HIGHLY CONTESTED", "FIERCE COMPETITION"],
        "MODERATE": ["MODERATE COMPETITION", "MODERATELY COMPETITIVE"],
        "LOW": ["LOW COMPETITION", "LIMITED COMPETITION", "FEW COMPETITORS"]
    }

    for intensity, keywords in intensity_keywords.items():
        if any(kw in text_upper for kw in keywords):
            data["competitive_intensity"] = intensity.lower()
            break

    # Default competitor count if not found via threat levels
    if data["competitor_count"] == 0:
        # Count numbered competitors or named sections
        for i in range(1, 10):
            if f"COMPETITOR {i}" in text_upper or f"#{i}" in text_upper:
                data["competitor_count"] = i

    # Minimum of 3 if analysis seems complete
    if data["competitor_count"] == 0 and len(analysis_text) > 1000:
        data["competitor_count"] = 3  # Assume at least 3 were discussed

    return data


def assess_competitors_from_data(
    competitors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Assess competitors using the competitor analysis utilities.

    Args:
        competitors: List of competitor data dictionaries with:
            - name: Competitor name
            - market_overlap: 0-100%
            - product_similarity: 0-100%
            - customer_overlap: 0-100%
            - market_share: %
            - growth_rate: %
            - funding_strength: 0-10
            - product_quality: 0-10
            - brand_strength: 0-10

    Returns:
        List of competitors with added classification and threat assessment
    """
    assessed = []

    for comp in competitors:
        # Classify competitor type
        comp_type = classify_competitor(
            market_overlap=comp.get("market_overlap", 50),
            product_similarity=comp.get("product_similarity", 50),
            target_customer_overlap=comp.get("customer_overlap", 50)
        )

        # Assess threat level
        threat = assess_threat_level(
            market_share=comp.get("market_share", 10),
            growth_rate=comp.get("growth_rate", 10),
            funding_strength=comp.get("funding_strength", 5),
            product_quality=comp.get("product_quality", 5),
            brand_strength=comp.get("brand_strength", 5)
        )

        assessed.append({
            **comp,
            "competitor_type": comp_type.value,
            "threat_level": threat.value
        })

    return assessed


def compare_tech_stacks(
    company_stack: List[str],
    competitor_stack: List[str]
) -> Dict[str, Any]:
    """
    Compare technology stacks between company and competitor.

    Args:
        company_stack: List of company's technologies
        competitor_stack: List of competitor's technologies

    Returns:
        Comparison results from TechStackAnalyzer
    """
    analyzer = TechStackAnalyzer()

    company_categorized = analyzer.analyze_stack(company_stack)
    competitor_categorized = analyzer.analyze_stack(competitor_stack)

    comparison = analyzer.compare_stacks(company_categorized, competitor_categorized)

    return {
        "company_stack": company_categorized,
        "competitor_stack": competitor_categorized,
        "comparison": comparison
    }


def generate_competitive_positioning(
    company_name: str,
    company_strengths: List[str],
    company_weaknesses: List[str],
    competitors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate competitive positioning analysis.

    Args:
        company_name: Name of the company
        company_strengths: Company's strengths
        company_weaknesses: Company's weaknesses
        competitors: List of competitor data with strengths/weaknesses

    Returns:
        Comprehensive positioning analysis
    """
    positioning_results = []

    for comp in competitors:
        positioning = analyze_competitive_positioning(
            company_strengths=company_strengths,
            company_weaknesses=company_weaknesses,
            competitor_strengths=comp.get("strengths", []),
            competitor_weaknesses=comp.get("weaknesses", [])
        )

        positioning_results.append({
            "competitor": comp.get("name", "Unknown"),
            "positioning": positioning
        })

    return {
        "company": company_name,
        "positioning_vs_competitors": positioning_results
    }


# ==============================================================================
# Integration with Traced LLM (Optional)
# ==============================================================================

def competitor_scout_agent_node_traced(state: OverallState) -> Dict[str, Any]:
    """
    Competitor Scout Agent with LangSmith tracing.

    Same functionality as competitor_scout_agent_node but uses
    the traced LLM client for full LangSmith observability.

    Args:
        state: Current workflow state

    Returns:
        State update with competitive intelligence analysis
    """
    print("\n" + "=" * 70)
    print("[AGENT: Competitor Scout] Competitive intelligence analysis (traced)...")
    print("=" * 70)

    # Try to use traced LLM
    try:
        from ..llm import invoke_with_tracing

        company_name = state["company_name"]
        search_results = state.get("search_results", [])

        if not search_results:
            return {
                "agent_outputs": {
                    "competitor": {
                        "analysis": "No search results available",
                        "data_extracted": False,
                        "competitors_found": 0,
                        "cost": 0.0
                    }
                }
            }

        prompt = create_competitor_analysis_prompt(company_name, search_results)

        # Use traced invocation
        response = invoke_with_tracing(
            prompt=prompt,
            run_name="competitor_scout_analysis",
            tags=[company_name, "competitor", "phase9"],
            metadata={
                "agent": "competitor_scout",
                "company": company_name,
                "source_count": len(search_results)
            }
        )

        # Extract data
        extracted_data = extract_competitor_data(response.content)

        print(f"[Competitor] Found {extracted_data['competitor_count']} competitors")
        print(f"[Competitor] Analysis complete - ${response.cost_usd:.4f}")
        if response.trace_url:
            print(f"[Competitor] Trace: {response.trace_url}")
        print("=" * 70)

        return {
            "agent_outputs": {
                "competitor": {
                    "analysis": response.content,
                    "data_extracted": True,
                    "competitors_found": extracted_data["competitor_count"],
                    "threat_summary": extracted_data["threat_summary"],
                    "competitive_intensity": extracted_data["competitive_intensity"],
                    "cost": response.cost_usd,
                    "tokens": {
                        "input": response.input_tokens,
                        "output": response.output_tokens
                    },
                    "trace_url": response.trace_url
                }
            },
            "total_cost": response.cost_usd,
            "total_tokens": {
                "input": response.input_tokens,
                "output": response.output_tokens
            }
        }

    except ImportError:
        # Fall back to non-traced version
        print("[Competitor] LLM tracing not available, using direct API")
        return competitor_scout_agent_node(state)
