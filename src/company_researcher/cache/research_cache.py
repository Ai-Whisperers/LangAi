"""
Research Cache - Persistent storage for all research data.

Core functionality:
- Store research data by company (NEVER DELETE)
- Track data freshness and quality
- Prevent redundant searches
- Enable incremental research
- Merge new data with existing data

Storage structure:
    .research_cache/
        url_registry.json       # All URLs encountered
        domain_stats.json       # Domain-level statistics
        companies/
            apple_inc/
                data.json       # All cached data
                sources.json    # Source tracking
                history.json    # Research history
            microsoft/
                ...

This module now serves as a backward-compatible entry point.
The actual implementations are in:
- cache/models.py: Enums and dataclasses
- cache/storage.py: ResearchCache service class

Usage:
    from company_researcher.cache.research_cache import ResearchCache, get_cache

    # Get global instance
    cache = get_cache()

    # Check existing data
    has_data = cache.has_company_data("Tesla Inc")
    data = cache.get_company_data("Tesla Inc")
    gaps = cache.identify_gaps("Tesla Inc")

    # Store new data
    cache.store_company_data("Tesla Inc", "financials", {...})
"""

# Import from modular structure for backward compatibility
from .models import CachedCompanyData, CachedSource, DataCompleteness, SourceQuality
from .storage import ResearchCache, create_cache, get_cache

# Re-export all public APIs
__all__ = [
    # Enums
    "SourceQuality",
    "DataCompleteness",
    # Dataclasses
    "CachedSource",
    "CachedCompanyData",
    # Service
    "ResearchCache",
    # Factory functions
    "get_cache",
    "create_cache",
]


# ============================================================================
# Demo and Testing
# ============================================================================

if __name__ == "__main__":
    from pathlib import Path

    print("Research Cache Demo")
    print("=" * 60)

    # 1. Initialize cache
    print("\n1. Initialize Cache")
    print("-" * 60)
    cache = create_cache(Path(".demo_cache"))
    print(f"   ✓ Cache initialized at: {cache.storage_path}")
    print(f"   ✓ Companies indexed: {len(cache._company_index)}")

    # 2. Store company data
    print("\n2. Store Company Data")
    print("-" * 60)
    cache.store_company_data(
        "Tesla Inc",
        "overview",
        {
            "name": "Tesla, Inc.",
            "ticker": "TSLA",
            "industry": "Electric Vehicles",
            "founded": "2003",
        },
        sources=[
            {
                "url": "https://www.tesla.com",
                "title": "Tesla Official Website",
                "quality": "primary",
                "score": 1.0,
            }
        ],
    )
    print("   ✓ Stored overview for Tesla Inc")

    cache.store_company_data(
        "Tesla Inc",
        "financials",
        {
            "revenue": "96.8B",
            "market_cap": "800B",
            "year": "2023",
        },
        sources=[
            {
                "url": "https://sec.gov/tesla",
                "title": "Tesla 10-K",
                "quality": "primary",
                "score": 0.95,
            }
        ],
    )
    print("   ✓ Stored financials for Tesla Inc")

    # 3. Retrieve data
    print("\n3. Retrieve Data")
    print("-" * 60)
    has_data = cache.has_company_data("Tesla Inc")
    print(f"   ✓ Has Tesla data: {has_data}")

    data = cache.get_company_data("Tesla Inc")
    if data:
        print(f"   ✓ Company: {data.company_name}")
        print(f"   ✓ Completeness: {data.completeness.value}")
        print(f"   ✓ Research count: {data.research_count}")
        print(f"   ✓ Sections: {list(data.section_updated.keys())}")
        print(f"   ✓ Sources: {len(data.sources)}")

    # 4. Identify gaps
    print("\n4. Identify Data Gaps")
    print("-" * 60)
    gaps = cache.identify_gaps("Tesla Inc")
    print(f"   ✓ Overall completeness: {gaps.overall_completeness:.1%}")
    print(f"   ✓ Needs research: {gaps.needs_research}")
    print(f"   ✓ Critical gaps: {len([g for g in gaps.gaps if g.severity == 'critical'])}")
    print(f"   ✓ High priority gaps: {len([g for g in gaps.gaps if g.severity == 'high'])}")

    # 5. Research priority
    print("\n5. Get Research Priority")
    print("-" * 60)
    priority = cache.get_research_priority("Tesla Inc")
    print(f"   ✓ High priority sections: {len(priority['high_priority'])}")
    print(f"   ✓ Medium priority sections: {len(priority['medium_priority'])}")
    if priority["high_priority"]:
        print(f"   ✓ Next to research: {', '.join(priority['high_priority'][:3])}")

    # 6. Should research check
    print("\n6. Should Research Check")
    print("-" * 60)
    should = cache.should_research("Tesla Inc")
    print(f"   ✓ Needs research: {should['needs_research']}")
    print(f"   ✓ Reason: {should['reason']}")
    print(f"   ✓ Priority sections: {len(should['priority_sections'])}")

    # 7. New company (no data)
    print("\n7. New Company (No Data)")
    print("-" * 60)
    should_new = cache.should_research("Apple Inc")
    print(f"   ✓ Needs research: {should_new['needs_research']}")
    print(f"   ✓ Reason: {should_new['reason']}")
    print(f"   ✓ All sections needed: {len(should_new['priority_sections'])}")

    # 8. Cache statistics
    print("\n8. Cache Statistics")
    print("-" * 60)
    stats = cache.get_statistics()
    print(f"   ✓ Total companies: {stats['companies']['total_companies']}")
    print(f"   ✓ Total URLs: {stats['urls']['total_urls']}")
    print(f"   ✓ Useful URLs: {stats['urls']['useful_urls']}")
    print(f"   ✓ Useless URLs: {stats['urls']['useless_urls']}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Cache initialization with custom storage path")
    print("  ✓ Store company data by section (overview, financials)")
    print("  ✓ Source tracking with quality ratings")
    print("  ✓ Data retrieval with completeness assessment")
    print("  ✓ Gap identification and research prioritization")
    print("  ✓ 'Should research' decision logic")
    print("  ✓ Statistics and monitoring")
    print("  ✓ URL registry integration")
