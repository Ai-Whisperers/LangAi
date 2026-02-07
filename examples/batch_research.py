"""
Batch Company Research Example

Demonstrates how to research multiple companies and compare results.

Usage:
    python examples/batch_research.py
"""

from typing import Dict, List

from src.company_researcher.workflows.parallel_agent_research import research_company


def batch_research(companies: List[str]) -> Dict[str, dict]:
    """
    Research multiple companies and collect results.

    Args:
        companies: List of company names to research

    Returns:
        Dictionary mapping company name to research result
    """
    results = {}

    print(f"=== Batch Research: {len(companies)} companies ===\n")

    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] Researching: {company}")
        print("-" * 50)

        try:
            result = research_company(company)
            results[company] = result

            print(f"  Quality: {result['quality_score']:.1f}/100")
            print(f"  Cost: ${result['total_cost']:.4f}")
            print(f"  Report: {result['report_path']}\n")

        except Exception as e:
            print(f"  ERROR: {e}\n")
            results[company] = {"error": str(e)}

    return results


def compare_results(results: Dict[str, dict]):
    """Display comparison of batch research results."""
    print("\n=== Batch Research Summary ===\n")

    # Calculate statistics
    successful = {k: v for k, v in results.items() if "error" not in v}
    failed = {k: v for k, v in results.items() if "error" in v}

    print(f"Total Companies: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}\n")

    if successful:
        # Quality comparison
        print("Quality Scores:")
        for company, result in sorted(
            successful.items(), key=lambda x: x[1]["quality_score"], reverse=True
        ):
            score = result["quality_score"]
            status = "✅" if score >= 85 else "⚠️"
            print(f"  {status} {company}: {score:.1f}/100")

        # Cost analysis
        total_cost = sum(r["total_cost"] for r in successful.values())
        avg_cost = total_cost / len(successful)

        print(f"\nCost Analysis:")
        print(f"  Total Cost: ${total_cost:.4f}")
        print(f"  Average Cost per Company: ${avg_cost:.4f}")

        # Token usage
        total_input_tokens = sum(r["total_tokens"]["input"] for r in successful.values())
        total_output_tokens = sum(r["total_tokens"]["output"] for r in successful.values())

        print(f"\nToken Usage:")
        print(f"  Total Input Tokens: {total_input_tokens:,}")
        print(f"  Total Output Tokens: {total_output_tokens:,}")
        print(f"  Total Tokens: {total_input_tokens + total_output_tokens:,}")

    if failed:
        print(f"\nFailed Companies:")
        for company, result in failed.items():
            print(f"  ❌ {company}: {result['error']}")


def main():
    """Run batch research on multiple companies."""
    # Define companies to research
    companies = ["Microsoft", "Tesla", "Stripe", "OpenAI", "Anthropic"]

    # Execute batch research
    results = batch_research(companies)

    # Compare results
    compare_results(results)

    return results


if __name__ == "__main__":
    results = main()
