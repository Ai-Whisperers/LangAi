#!/usr/bin/env python3
"""
Basic Company Researcher - Phase 1 CLI

Usage:
    python src/basic_researcher.py "Tesla"
    python src/basic_researcher.py "OpenAI"
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from company_researcher.config import get_config
from company_researcher.workflows.basic_research import research_company


def main():
    """Main CLI entrypoint."""

    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python src/basic_researcher.py <company_name>")
        print("\nExamples:")
        print("  python src/basic_researcher.py Tesla")
        print("  python src/basic_researcher.py OpenAI")
        print("  python src/basic_researcher.py 'Stripe Inc'")
        sys.exit(1)

    company_name = " ".join(sys.argv[1:])

    # Validate config (API keys)
    try:
        config = get_config()
    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        sys.exit(1)

    # Run research
    try:
        result = research_company(company_name)

        # Exit with success code
        sys.exit(0 if result["success"] else 1)

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
