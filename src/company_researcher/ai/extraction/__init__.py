"""AI-powered data extraction module.

This module provides AI-driven data extraction capabilities that replace
regex-based extraction and static classification lists with semantic AI
extraction that understands context, handles multiple languages, and
resolves contradictions intelligently.

Features:
- Context-aware company classification
- Semantic fact extraction
- Universal entity recognition
- Intelligent contradiction resolution
- Multi-language data extraction

Usage:
    from company_researcher.ai.extraction import (
        get_data_extractor,
        AIDataExtractor,
        CompanyType,
        CompanyClassification,
        ExtractedFact,
        FinancialData,
        ExtractionResult
    )

    # Get the extractor
    extractor = get_data_extractor()

    # Classify a company
    classification = await extractor.classify_company(
        company_name="Grupo Bimbo",
        context="Mexican multinational bakery company..."
    )

    # Extract facts from text
    facts = await extractor.extract_facts(
        text="Revenue reached $20 billion in 2023...",
        company_name="Grupo Bimbo"
    )

    # Complete extraction pipeline
    result = await extractor.extract_all(
        company_name="Grupo Bimbo",
        search_results=[{"url": "...", "content": "..."}]
    )
"""

from .extractor import (
    AIDataExtractor,
    get_data_extractor,
    reset_data_extractor,
)
from .models import (
    # Enums
    CompanyType,
    FactCategory,
    FactType,
    ContradictionSeverity,
    # Models
    CompanyClassification,
    ExtractedFact,
    FinancialData,
    ContradictionAnalysis,
    ExtractionResult,
    CountryDetectionResult,
)

__all__ = [
    # Main class and factory
    "AIDataExtractor",
    "get_data_extractor",
    "reset_data_extractor",
    # Enums
    "CompanyType",
    "FactCategory",
    "FactType",
    "ContradictionSeverity",
    # Models
    "CompanyClassification",
    "ExtractedFact",
    "FinancialData",
    "ContradictionAnalysis",
    "ExtractionResult",
    "CountryDetectionResult",
]
