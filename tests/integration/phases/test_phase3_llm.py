#!/usr/bin/env python3
"""
Test script for Phase 3: Multi-Agent Workflow.
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from company_researcher.workflows.multi_agent_research import research_company


def main():
    """Run Phase 3 multi-agent workflow test."""
    if len(sys.argv) < 2:
        print("Usage: python test_phase3.py <company_name>")
        sys.exit(1)

    company_name = sys.argv[1]

    print("\n" + "=" * 60)
    print("PHASE 3: MULTI-AGENT WORKFLOW TEST")
    print("=" * 60)
    print(f"Company: {company_name}")
    print("Agents: Researcher -> Analyst")
    print("=" * 60 + "\n")

    try:
        result = research_company(company_name)

        print("\n[SUCCESS] Phase 3 multi-agent workflow completed successfully!")
        print(f"\nAgent Metrics:")
        print(f"  Quality Score: {result['metrics'].get('quality_score', 'N/A')}/100")
        print(f"  Iterations: {result['metrics'].get('iterations', 'N/A')}")
        print(f"  Total Cost: ${result['metrics'].get('cost_usd', 0):.4f}")
        print(f"  Sources: {result['metrics'].get('sources_count', 0)}")

    except KeyboardInterrupt:
        print("\n\n[ERROR] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
