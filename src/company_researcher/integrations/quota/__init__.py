"""
API Quota & Balance Checking Package.

This package provides tools for monitoring API quotas and balances
across all integrated APIs.

Modules:
    - models: Data models (QuotaStatus, QuotaInfo, QuotaReport)
    - checker: APIQuotaChecker class with all check methods

Usage:
    from company_researcher.integrations.quota import (
        QuotaStatus,
        QuotaInfo,
        QuotaReport,
        APIQuotaChecker,
        check_all_quotas,
        check_all_quotas_async,
    )

    # Check all quotas
    report = check_all_quotas()
    print(report.to_string())
"""

import asyncio

from .models import QuotaStatus, QuotaInfo, QuotaReport
from .checker import APIQuotaChecker


def check_all_quotas() -> QuotaReport:
    """Check quotas for all configured APIs (sync wrapper)."""
    checker = APIQuotaChecker()
    return asyncio.run(checker.check_all())


async def check_all_quotas_async() -> QuotaReport:
    """Check quotas for all configured APIs (async)."""
    checker = APIQuotaChecker()
    return await checker.check_all()


__all__ = [
    # Models
    "QuotaStatus",
    "QuotaInfo",
    "QuotaReport",
    # Checker
    "APIQuotaChecker",
    # Convenience functions
    "check_all_quotas",
    "check_all_quotas_async",
]
