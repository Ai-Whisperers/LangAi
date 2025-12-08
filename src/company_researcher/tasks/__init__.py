"""
Tasks Package - Celery Task Queue Integration.

Provides asynchronous task processing for:
- Background research jobs
- Batch company processing
- Scheduled research updates
- Report generation

Usage:
    from company_researcher.tasks import research_single_company

    # Queue a research task
    result = research_single_company.delay("Tesla")

    # Check status
    print(result.status)

    # Get result when ready
    data = result.get(timeout=300)
"""

from .research_tasks import (
    app,
    research_single_company,
    research_batch_companies,
    update_company_data,
    generate_report,
    CELERY_AVAILABLE,
)

__all__ = [
    "app",
    "research_single_company",
    "research_batch_companies",
    "update_company_data",
    "generate_report",
    "CELERY_AVAILABLE",
]
