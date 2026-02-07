"""
API Quota & Balance Checker - Monitor usage across all integrated APIs.

This utility checks:
- Account balances and credits (where available)
- Rate limits and remaining calls
- API key validity
- Subscription tier information

Usage:
    python -m src.company_researcher.integrations.api_quota_checker

Or in code:
    from src.company_researcher.integrations.api_quota_checker import check_all_quotas
    report = check_all_quotas()
    print(report.to_string())
"""

import json

# Import from quota package
from .quota import (
    APIQuotaChecker,
    QuotaInfo,
    QuotaReport,
    QuotaStatus,
    check_all_quotas,
    check_all_quotas_async,
)

# Re-export for backward compatibility
__all__ = [
    "QuotaStatus",
    "QuotaInfo",
    "QuotaReport",
    "APIQuotaChecker",
    "check_all_quotas",
    "check_all_quotas_async",
]


# =========================================================================
# CLI Entry Point
# =========================================================================


def main():
    """Run quota check from command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check API quotas and balances for all integrations"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON instead of formatted text"
    )
    parser.add_argument("--output", "-o", type=str, help="Save report to file")

    args = parser.parse_args()

    print("Checking API quotas...\n")

    report = check_all_quotas()

    if args.json:
        output = json.dumps(report.to_dict(), indent=2, default=str)
    else:
        output = report.to_string()

    print(output)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
