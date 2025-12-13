"""
Enhanced Market Analyst Agent (Phase 8).

Provides comprehensive market analysis including:
- TAM/SAM/SOM market sizing
- Industry trends and growth trajectories
- Regulatory landscape
- Competitive dynamics
- Customer intelligence
"""

from typing import Dict, Any, Optional, Callable
from ...utils import get_logger

logger = get_logger(__name__)

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ...state import OverallState


class EnhancedMarketAgent:
    """Enhanced market analysis agent with TAM/SAM/SOM sizing."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(self, company_name: str, search_results: list = None) -> Dict[str, Any]:
        """Perform enhanced market analysis for a company."""
        if search_results is None:
            search_results = []
        state = {"company_name": company_name, "search_results": search_results}
        return enhanced_market_agent_node(state)


def create_enhanced_market_agent(search_tool: Callable = None, llm_client: Any = None) -> EnhancedMarketAgent:
    """Factory function to create an EnhancedMarketAgent."""
    return EnhancedMarketAgent(search_tool=search_tool, llm_client=llm_client)


# ==============================================================================
# Prompts
# ==============================================================================

ENHANCED_MARKET_PROMPT = """You are an expert market analyst with deep expertise in industry analysis and market sizing.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide comprehensive market analysis covering all critical strategic dimensions.

**STRUCTURE YOUR ANALYSIS:**

### 1. Market Sizing (TAM/SAM/SOM)
Estimate or cite market size at three levels:

**TAM (Total Addressable Market)**:
- Global market size for the entire industry
- Total potential if company captured 100% of all customers
- Example: "Global automotive market: $8.0T"

**SAM (Serviceable Available Market)**:
- Portion of TAM the company's product/service addresses
- Market segment company actually targets
- Example: "Electric vehicle market: $2.5T (31% of automotive)"

**SOM (Serviceable Obtainable Market)**:
- Realistic market share company can capture
- Based on current position, competition, resources
- Example: "Tesla addressable: $150B (6% of EV market)"

**Market Penetration**:
- Current market share percentage
- Growth runway remaining

### 2. Industry Trends
Identify and categorize key trends:

**Growing Trends** (use indicator: [GROWING]):
- Trends with positive momentum
- Growth rates (CAGR) if available
- Drivers and catalysts

**Declining Trends** (use indicator: [DECLINING]):
- Trends losing momentum
- Decline rates if available
- Replacement trends

**Emerging Opportunities** (use indicator: [EMERGING]):
- New market segments
- Technological shifts
- Business model innovations

### 3. Regulatory Landscape
Analyze regulatory environment:

**Current Regulations**:
- Existing laws and compliance requirements
- Impact on operations
- Compliance costs

**Upcoming Changes**:
- Proposed regulations
- Expected timeline
- Potential impact (positive/negative)

**Regional Variations**:
- Differences by geography
- Regulatory arbitrage opportunities

### 4. Competitive Dynamics

**Market Structure**:
- Number of competitors
- Market concentration (fragmented vs consolidated)
- Competitive intensity (LOW/MODERATE/HIGH/INTENSE)

**Key Players**:
- Top 3-5 competitors
- Market share estimates if available
- Positioning differences

**Competitive Moats**:
- Barriers to entry
- Defensibility of position
- Switching costs

### 5. Customer Intelligence

**Target Demographics**:
- Primary customer segments
- Geographic distribution
- Demographic characteristics

**Buyer Personas**:
- Key decision-makers
- Purchase motivations
- Pain points addressed

**Market Dynamics**:
- Customer acquisition trends
- Churn/retention patterns
- Lifetime value indicators

**REQUIREMENTS:**
- Use specific numbers and percentages wherever possible
- Cite sources for market size estimates
- Clearly indicate estimates vs verified data
- Highlight any data gaps
- Provide context and strategic implications

Begin your market analysis:"""


# ==============================================================================
# Enhanced Market Analyst Agent
# ==============================================================================

def enhanced_market_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Enhanced Market Analyst Agent Node: Comprehensive market analysis.

    Analyzes:
    1. Market sizing (TAM/SAM/SOM)
    2. Industry trends (growing/declining/emerging)
    3. Regulatory landscape
    4. Competitive dynamics
    5. Customer intelligence

    Args:
        state: Current workflow state

    Returns:
        State update with enhanced market analysis
    """
    logger.info("Enhanced Market agent starting - comprehensive market analysis")

    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        logger.warning("No search results available for market analysis")
        return {
            "agent_outputs": {
                "market": {
                    "analysis": "No search results available for market analysis",
                    "data_extracted": False,
                    "cost": 0.0
                }
            }
        }

    logger.info(f"Analyzing market for {company_name}")
    logger.debug(f"Processing {len(search_results)} sources")

    # Create comprehensive analysis prompt
    prompt = create_market_analysis_prompt(company_name, search_results)

    # Call LLM for analysis
    client = get_anthropic_client()
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.enhanced_market_max_tokens,
        temperature=config.market_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    market_analysis = safe_extract_text(response, agent_name="enhanced_market")
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    logger.info(f"Enhanced Market analysis complete - cost: ${cost:.4f}")

    # Create agent output
    agent_output = {
        "analysis": market_analysis,
        "data_extracted": True,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    return {
        "agent_outputs": {"market": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }


# ==============================================================================
# Helper Functions
# ==============================================================================

def create_market_analysis_prompt(
    company_name: str,
    search_results: list
) -> str:
    """
    Create comprehensive market analysis prompt.

    Args:
        company_name: Name of company
        search_results: Web search results

    Returns:
        Formatted prompt string
    """
    # Format search results with focus on market/industry content
    formatted_results = format_market_search_results(search_results)

    # Create prompt
    prompt = ENHANCED_MARKET_PROMPT.format(
        company_name=company_name,
        search_results=formatted_results
    )

    return prompt


def format_market_search_results(search_results: list) -> str:
    """
    Format search results with emphasis on market-relevant content.

    Args:
        search_results: List of search result dictionaries

    Returns:
        Formatted string
    """
    # Prioritize results with market/industry keywords
    market_keywords = [
        "market", "industry", "TAM", "SAM", "growth", "trend",
        "competitive", "regulation", "customer", "segment"
    ]

    # Score results by relevance
    scored_results = []
    for result in search_results:
        content = result.get("content", "").lower()
        title = result.get("title", "").lower()

        # Count market keyword matches
        relevance_score = sum(
            1 for keyword in market_keywords
            if keyword in content or keyword in title
        )

        scored_results.append((relevance_score, result))

    # Sort by relevance (descending)
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Format top results
    formatted = []
    for i, (score, result) in enumerate(scored_results[:15], 1):
        formatted.append(
            f"Source {i} [Relevance: {score}]: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')[:500]}...\n"
        )

    return "\n".join(formatted) if formatted else "No market-specific results available."


def extract_market_indicators(analysis_text: str) -> Dict[str, any]:
    """
    Extract structured market indicators from analysis text.

    Args:
        analysis_text: Market analysis text from LLM

    Returns:
        Dictionary with extracted indicators:
        - market_size_estimates: TAM/SAM/SOM if mentioned
        - trends_identified: List of trends
        - competitive_intensity: Assessment
        - regulatory_impact: Summary
    """
    indicators = {
        "market_size_estimates": {},
        "trends_identified": [],
        "competitive_intensity": None,
        "regulatory_impact": None
    }

    # Extract TAM/SAM/SOM (simple pattern matching)
    # In production, would use more sophisticated NLP
    text_upper = analysis_text.upper()

    # Look for TAM mentions
    if "TAM" in text_upper or "TOTAL ADDRESSABLE MARKET" in text_upper:
        # Extract value (simplified)
        indicators["market_size_estimates"]["tam"] = "Mentioned in analysis"

    # Look for trend indicators
    if "[GROWING]" in analysis_text:
        indicators["trends_identified"].append("growing_trends_present")

    if "[DECLINING]" in analysis_text:
        indicators["trends_identified"].append("declining_trends_present")

    if "[EMERGING]" in analysis_text:
        indicators["trends_identified"].append("emerging_opportunities_present")

    # Look for competitive intensity keywords
    for intensity in ["INTENSE", "HIGH", "MODERATE", "LOW"]:
        if intensity in text_upper and "COMPETI" in text_upper:
            indicators["competitive_intensity"] = intensity.lower()
            break

    # Look for regulatory mentions
    if any(keyword in text_upper for keyword in ["REGULATION", "COMPLIANCE", "REGULATORY"]):
        indicators["regulatory_impact"] = "regulatory_factors_identified"

    return indicators


def infer_industry_category(company_name: str) -> str:
    """
    Infer industry category from company name.

    This is a simple heuristic. In production, would use:
    - Company database with industry classifications
    - SIC/NAICS code lookup
    - ML-based classification

    Args:
        company_name: Company name

    Returns:
        Industry category string
    """
    company_lower = company_name.lower()

    # Technology companies
    tech_keywords = [
        "tech", "software", "ai", "cloud", "data", "cyber",
        "microsoft", "google", "apple", "meta", "amazon",
        "salesforce", "adobe", "oracle", "ibm"
    ]
    if any(kw in company_lower for kw in tech_keywords):
        return "Technology / Software"

    # Automotive
    auto_keywords = ["tesla", "automotive", "vehicle", "car", "motor"]
    if any(kw in company_lower for kw in auto_keywords):
        return "Automotive / Transportation"

    # Fintech / Payments
    fintech_keywords = [
        "stripe", "paypal", "square", "bank", "payment",
        "financial", "fintech", "credit"
    ]
    if any(kw in company_lower for kw in fintech_keywords):
        return "Financial Technology / Payments"

    # Healthcare / Biotech
    health_keywords = [
        "health", "medical", "pharma", "biotech", "therapeutics",
        "clinical", "drug"
    ]
    if any(kw in company_lower for kw in health_keywords):
        return "Healthcare / Biotechnology"

    # E-commerce / Retail
    ecommerce_keywords = ["shop", "commerce", "retail", "marketplace"]
    if any(kw in company_lower for kw in ecommerce_keywords):
        return "E-commerce / Retail"

    # Default
    return "General Industry"


def get_industry_context(industry: str) -> Dict[str, str]:
    """
    Get industry-specific context for analysis.

    Args:
        industry: Industry category

    Returns:
        Dictionary with industry context:
        - typical_tam_range: Typical TAM size
        - growth_benchmark: Typical CAGR
        - competitive_intensity: Typical intensity
        - key_trends: Notable trends
    """
    industry_contexts = {
        "Technology / Software": {
            "typical_tam_range": "$100B - $5T",
            "growth_benchmark": "15-40% CAGR",
            "competitive_intensity": "HIGH to INTENSE",
            "key_trends": "AI/ML, Cloud, SaaS, Cybersecurity"
        },
        "Automotive / Transportation": {
            "typical_tam_range": "$2T - $8T",
            "growth_benchmark": "3-8% CAGR (ICE), 25-40% (EV)",
            "competitive_intensity": "HIGH",
            "key_trends": "Electrification, Autonomous, Shared Mobility"
        },
        "Financial Technology / Payments": {
            "typical_tam_range": "$500B - $2T",
            "growth_benchmark": "10-20% CAGR",
            "competitive_intensity": "INTENSE",
            "key_trends": "Digital Payments, Blockchain, Embedded Finance"
        },
        "Healthcare / Biotechnology": {
            "typical_tam_range": "$500B - $3T",
            "growth_benchmark": "5-12% CAGR",
            "competitive_intensity": "MODERATE to HIGH",
            "key_trends": "Precision Medicine, Telehealth, Gene Therapy"
        },
        "E-commerce / Retail": {
            "typical_tam_range": "$3T - $10T",
            "growth_benchmark": "10-15% CAGR",
            "competitive_intensity": "INTENSE",
            "key_trends": "Omnichannel, D2C, Social Commerce"
        }
    }

    return industry_contexts.get(industry, {
        "typical_tam_range": "Varies",
        "growth_benchmark": "Varies",
        "competitive_intensity": "Varies",
        "key_trends": "Industry-specific"
    })
