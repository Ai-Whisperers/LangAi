"""
Cost Analysis Example

Demonstrates how to track and analyze costs during research, including:
- Per-agent cost breakdown
- Token usage analysis
- Cost optimization strategies
- Budget monitoring

Usage:
    python examples/cost_analysis.py
"""

from typing import Dict, List
from src.company_researcher.workflows.parallel_agent_research import research_company
from src.company_researcher.config import config


def analyze_research_costs(company_name: str) -> Dict:
    """
    Research a company and perform detailed cost analysis.

    Args:
        company_name: Company to research

    Returns:
        Dictionary with cost analysis details
    """
    print(f"=== Cost Analysis: {company_name} ===\n")

    # Execute research
    result = research_company(company_name)

    # Extract cost data
    total_cost = result["total_cost"]
    total_tokens = result["total_tokens"]
    quality_score = result["quality_score"]

    # Calculate metrics
    input_tokens = total_tokens["input"]
    output_tokens = total_tokens["output"]
    total_token_count = input_tokens + output_tokens

    # Cost per token
    cost_per_token = total_cost / total_token_count if total_token_count > 0 else 0

    # Cost per quality point
    cost_per_quality_point = total_cost / quality_score if quality_score > 0 else 0

    # Estimate agent breakdown (based on typical distribution)
    # In Phase 4, costs are distributed across:
    # - Researcher: ~20% (search + query generation)
    # - Specialists (3x): ~50% (financial, market, product)
    # - Synthesizer: ~20% (combining outputs)
    # - Quality Check: ~10%
    estimated_breakdown = {
        "researcher": total_cost * 0.20,
        "specialists": {
            "financial": total_cost * 0.17,
            "market": total_cost * 0.17,
            "product": total_cost * 0.16,
        },
        "synthesizer": total_cost * 0.20,
        "quality_check": total_cost * 0.10
    }

    analysis = {
        "company": company_name,
        "total_cost": total_cost,
        "quality_score": quality_score,
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_token_count
        },
        "metrics": {
            "cost_per_token": cost_per_token,
            "cost_per_quality_point": cost_per_quality_point,
            "tokens_per_dollar": 1 / cost_per_token if cost_per_token > 0 else 0
        },
        "estimated_breakdown": estimated_breakdown
    }

    # Display analysis
    print_cost_analysis(analysis)

    return analysis


def print_cost_analysis(analysis: Dict):
    """Display formatted cost analysis."""
    print("=" * 70)
    print(f"Company: {analysis['company']}")
    print(f"Quality Score: {analysis['quality_score']:.1f}/100")
    print("=" * 70)

    # Total cost
    print(f"\nTotal Cost: ${analysis['total_cost']:.4f}")

    # Token breakdown
    tokens = analysis['tokens']
    print(f"\nToken Usage:")
    print(f"  Input Tokens:  {tokens['input']:>8,} ({tokens['input']/tokens['total']*100:.1f}%)")
    print(f"  Output Tokens: {tokens['output']:>8,} ({tokens['output']/tokens['total']*100:.1f}%)")
    print(f"  Total Tokens:  {tokens['total']:>8,}")

    # Cost metrics
    metrics = analysis['metrics']
    print(f"\nCost Metrics:")
    print(f"  Cost per Token:         ${metrics['cost_per_token']:.6f}")
    print(f"  Tokens per Dollar:      {metrics['tokens_per_dollar']:,.0f}")
    print(f"  Cost per Quality Point: ${metrics['cost_per_quality_point']:.5f}")

    # Estimated breakdown
    breakdown = analysis['estimated_breakdown']
    print(f"\nEstimated Cost Breakdown:")
    print(f"  Researcher:    ${breakdown['researcher']:.4f} ({breakdown['researcher']/analysis['total_cost']*100:.0f}%)")
    print(f"  Specialists:   ${sum(breakdown['specialists'].values()):.4f} ({sum(breakdown['specialists'].values())/analysis['total_cost']*100:.0f}%)")
    for name, cost in breakdown['specialists'].items():
        print(f"    - {name.capitalize()}: ${cost:.4f}")
    print(f"  Synthesizer:   ${breakdown['synthesizer']:.4f} ({breakdown['synthesizer']/analysis['total_cost']*100:.0f}%)")
    print(f"  Quality Check: ${breakdown['quality_check']:.4f} ({breakdown['quality_check']/analysis['total_cost']*100:.0f}%)")


def batch_cost_analysis(companies: List[str]) -> Dict:
    """
    Analyze costs across multiple companies.

    Args:
        companies: List of company names

    Returns:
        Aggregated cost analysis
    """
    print("=== Batch Cost Analysis ===\n")

    analyses = []

    for company in companies:
        print(f"\nAnalyzing: {company}")
        print("-" * 70)
        analysis = analyze_research_costs(company)
        analyses.append(analysis)
        print()

    # Aggregate statistics
    print("\n" + "=" * 70)
    print("AGGREGATE STATISTICS")
    print("=" * 70)

    total_cost = sum(a["total_cost"] for a in analyses)
    avg_cost = total_cost / len(analyses)
    total_tokens = sum(a["tokens"]["total"] for a in analyses)
    avg_quality = sum(a["quality_score"] for a in analyses) / len(analyses)

    print(f"\nCompanies Analyzed: {len(companies)}")
    print(f"\nCost Summary:")
    print(f"  Total Cost:     ${total_cost:.4f}")
    print(f"  Average Cost:   ${avg_cost:.4f}")
    print(f"  Min Cost:       ${min(a['total_cost'] for a in analyses):.4f}")
    print(f"  Max Cost:       ${max(a['total_cost'] for a in analyses):.4f}")

    print(f"\nToken Summary:")
    print(f"  Total Tokens:   {total_tokens:,}")
    print(f"  Average Tokens: {int(total_tokens / len(analyses)):,}")

    print(f"\nQuality Summary:")
    print(f"  Average Quality: {avg_quality:.1f}/100")
    print(f"  Min Quality:     {min(a['quality_score'] for a in analyses):.1f}/100")
    print(f"  Max Quality:     {max(a['quality_score'] for a in analyses):.1f}/100")

    print(f"\nCost Efficiency:")
    avg_cost_per_quality = avg_cost / avg_quality if avg_quality > 0 else 0
    print(f"  Average Cost per Quality Point: ${avg_cost_per_quality:.5f}")

    return {
        "companies": companies,
        "analyses": analyses,
        "aggregate": {
            "total_cost": total_cost,
            "avg_cost": avg_cost,
            "total_tokens": total_tokens,
            "avg_quality": avg_quality
        }
    }


def cost_optimization_tips():
    """Display cost optimization strategies."""
    print("\n" + "=" * 70)
    print("COST OPTIMIZATION TIPS")
    print("=" * 70)

    tips = [
        {
            "title": "1. Use Haiku for Simple Tasks",
            "description": "Claude 3.5 Haiku is 10x cheaper than Sonnet for similar tasks"
        },
        {
            "title": "2. Reduce Search Results",
            "description": "Fewer search results = less input tokens to analyze"
        },
        {
            "title": "3. Optimize Prompts",
            "description": "Shorter, focused prompts reduce both input and output tokens"
        },
        {
            "title": "4. Adjust Quality Target",
            "description": "Lower quality threshold (75 vs 85) means fewer iterations"
        },
        {
            "title": "5. Cache Configuration",
            "description": "Enable prompt caching for repeated research patterns"
        },
        {
            "title": "6. Selective Agent Execution",
            "description": "Only run agents needed for specific use case"
        }
    ]

    for tip in tips:
        print(f"\n{tip['title']}")
        print(f"  {tip['description']}")

    print(f"\n" + "=" * 70)


def main():
    """Run cost analysis examples."""
    # Single company analysis
    print("=" * 70)
    print("EXAMPLE 1: Single Company Cost Analysis")
    print("=" * 70)
    analysis = analyze_research_costs("Stripe")

    # Batch analysis
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 2: Batch Cost Analysis")
    print("=" * 70)
    batch_analysis = batch_cost_analysis([
        "Microsoft",
        "Tesla",
        "OpenAI"
    ])

    # Optimization tips
    cost_optimization_tips()

    return {
        "single": analysis,
        "batch": batch_analysis
    }


if __name__ == "__main__":
    results = main()
