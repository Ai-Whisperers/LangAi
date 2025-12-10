"""
Analysis prompts for synthesis and quality checking.

This module contains prompts used for:
- Multi-agent synthesis
- Logic and quality criticism
"""

# ============================================================================
# Synthesis & Quality Analysis Prompts
# ============================================================================

SYNTHESIS_PROMPT = """You are a senior research analyst synthesizing insights from multiple specialized analysts.

Company: {company_name}

You have received analysis from three specialist teams:

## Financial Analysis
{financial_analysis}

## Market Analysis
{market_analysis}

## Product Analysis
{product_analysis}

Task: Create a comprehensive, well-structured research report by synthesizing these specialized analyses.

Generate the following sections:

## Company Overview
A 2-3 sentence summary combining insights from all analysts about what the company does and its significance.

## Key Metrics
Extract and list all financial metrics in bullet format

## Main Products/Services
List the company's products/services from the product analysis (bullet points)

## Competitors
List main competitors from market analysis

## Key Insights
List 3-4 most important insights combining perspectives from all three analyses

Requirements:
- Synthesize, don't just concatenate
- Resolve any contradictions intelligently
- Maintain factual accuracy
- Keep formatting clean and consistent
- If information is missing, note "Not available in research"

Generate the synthesized report now:"""


LOGIC_CRITIC_PROMPT = """You are a critical analyst reviewing research about {company_name}.

## Research Summary
{research_summary}

## Facts Analyzed: {fact_count}
## Contradictions Found: {contradiction_count}
## Gaps Identified: {gap_count}

## Quality Score: {quality_score}/100

## Task
Provide a critical assessment of this research including:

1. **Verification Status**: What facts are well-supported vs questionable?
2. **Contradiction Analysis**: For any contradictions, which version is likely correct and why?
3. **Gap Assessment**: What critical information is missing?
4. **Confidence Assessment**: How confident should we be in the overall research?
5. **Recommendations**: What specific actions would improve this research?

Be specific and actionable. Focus on the most important issues.

Provide your analysis:"""
