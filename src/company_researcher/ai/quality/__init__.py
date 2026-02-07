"""AI-powered quality assessment module.

This module provides AI-driven quality assessment that replaces rule-based
scoring with semantic understanding of content quality, source reliability,
and information completeness.

Usage:
    from company_researcher.ai.quality import (
        get_quality_assessor,
        AIQualityAssessor,
        QualityLevel,
        ContentQualityAssessment,
        SourceQualityAssessment,
        OverallQualityReport,
    )

    # Get assessor instance
    assessor = get_quality_assessor()

    # Assess content quality
    content_quality = await assessor.assess_content_quality(
        content="Tesla reported $81.5B revenue...",
        section_name="financial",
        company_name="Tesla"
    )

    # Assess source quality
    source_quality = await assessor.assess_source_quality(
        url="https://reuters.com/article/tesla",
        title="Tesla Reports Record Revenue",
        snippet="Tesla Inc reported...",
        company_name="Tesla"
    )

    # Generate overall report
    report = await assessor.generate_overall_report(
        company_name="Tesla",
        section_assessments=[content_quality],
        source_assessments=[source_quality]
    )

    if report.ready_for_delivery:
        print("Report meets quality bar!")
    else:
        print(f"Focus areas: {report.focus_areas_for_iteration}")
"""

from .assessor import AIQualityAssessor, get_quality_assessor, reset_quality_assessor
from .models import (
    ConfidenceAssessment,
    ContentQualityAssessment,
    OverallQualityReport,
    QualityLevel,
    SectionRequirements,
    SourceQualityAssessment,
    SourceType,
)

__all__ = [
    # Main class
    "AIQualityAssessor",
    "get_quality_assessor",
    "reset_quality_assessor",
    # Models
    "QualityLevel",
    "SourceType",
    "ContentQualityAssessment",
    "SourceQualityAssessment",
    "ConfidenceAssessment",
    "SectionRequirements",
    "OverallQualityReport",
]
