"""
Basic Company Research Example

Demonstrates the simplest way to research a company using the Phase 4
parallel multi-agent system.

Usage:
    python examples/basic_research.py
"""

from src.company_researcher.workflows.parallel_agent_research import research_company


def main():
    """Run basic research on a single company."""
    print("=== Basic Company Research Example ===\n")

    # Research a company
    company_name = "Tesla"
    print(f"Researching: {company_name}")
    print("-" * 50)

    # Execute research
    result = research_company(company_name)

    # Display results
    print("\n=== Research Complete ===")
    print(f"Quality Score: {result['quality_score']:.1f}/100")
    print(f"Total Cost: ${result['total_cost']:.4f}")
    print(f"Total Tokens: {result['total_tokens']}")
    print(f"Report saved: {result['report_path']}")

    # Show report preview
    print("\n=== Report Preview ===")
    print(result['report'][:500] + "...")

    return result


if __name__ == "__main__":
    result = main()
