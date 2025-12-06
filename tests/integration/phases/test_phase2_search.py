#!/usr/bin/env python3
"""
Test script for Phase 2 workflow.
"""
import sys
from src.company_researcher.workflows.basic_research import research_company


def main():
    """Run Phase 2 workflow test."""
    if len(sys.argv) < 2:
        print("Usage: python test_phase2.py <company_name>")
        sys.exit(1)

    company_name = sys.argv[1]
    result = research_company(company_name)

    print("\n[SUCCESS] Phase 2 workflow completed successfully!")
    print(f"Quality Score: {result['metrics'].get('quality_score', 'N/A')}")
    print(f"Iterations: {result['metrics'].get('iterations', 'N/A')}")


if __name__ == "__main__":
    main()
