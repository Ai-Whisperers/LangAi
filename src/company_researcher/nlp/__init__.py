"""
Natural Language Processing Module (UX-001).

NLP capabilities for company research:
- Natural language query processing
- Intent classification
- Entity extraction
- Response formatting

Usage:
    from src.company_researcher.nlp import (
        NaturalLanguageQueryProcessor,
        process_natural_query,
        QueryIntent
    )

    # Parse a query
    processor = NaturalLanguageQueryProcessor()
    parsed = processor.parse("What is Apple's revenue?")
    print(parsed.intent)  # QueryIntent.FINANCIAL_INFO
    print(parsed.companies)  # ["Apple"]

    # Quick processing
    response = await process_natural_query("Show me Tesla's competitors")
"""

from .query_processor import (
    NaturalLanguageQueryProcessor,
    ParsedQuery,
    QueryResponse,
    QueryIntent,
    EntityType,
    Entity,
    create_query_processor,
    process_natural_query,
)

__all__ = [
    "NaturalLanguageQueryProcessor",
    "ParsedQuery",
    "QueryResponse",
    "QueryIntent",
    "EntityType",
    "Entity",
    "create_query_processor",
    "process_natural_query",
]
