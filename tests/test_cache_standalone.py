"""
Standalone test for Research Cache.

Tests the research cache system including:
- URL registry for tracking useful/useless URLs
- Data completeness checking
- Research cache storage and retrieval
"""

import os
import sys

# Setup path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


def test_cache_functionality():
    """Test the research cache functionality."""
    # Import using standard package imports
    from src.company_researcher.cache.data_completeness import CompletenessChecker
    from src.company_researcher.cache.research_cache import ResearchCache, get_cache
    from src.company_researcher.cache.url_registry import URLRegistry, URLStatus

    print("Testing Research Cache...")
    print()

    print("[OK] All modules loaded")
    print()

    # Test URL Registry
    print("1. Testing URL Registry...")
    registry = URLRegistry()
    print(f"   [OK] Registry created at: {registry.storage_path}")

    # Mark useful URL
    registry.mark_useful(
        url="https://reuters.com/article/apple",
        quality_score=0.85,
        content_summary="Apple Q3 earnings report",
        company_name="Apple Inc",
        title="Apple Reports Record Q3",
    )
    print("   [OK] Marked URL as useful")

    # Mark useless URL
    registry.mark_useless(
        url="https://paywall-site.com/blocked",
        reason="Subscription required",
        status=URLStatus.PAYWALL,
    )
    print("   [OK] Marked URL as useless")

    # Test filtering
    test_urls = [
        "https://reuters.com/article/apple",
        "https://paywall-site.com/blocked",
        "https://new-site.com/article",
    ]
    filtered = registry.filter_urls(test_urls)
    print(f"   [OK] Filtered URLs:")
    print(f"       - New: {len(filtered['new'])}")
    print(f"       - Useful: {len(filtered['useful'])}")
    print(f"       - Useless: {len(filtered['useless'])}")

    # Test is_known_useless
    assert registry.is_known_useless("https://paywall-site.com/blocked") == True
    assert registry.is_known_useless("https://reuters.com/article/apple") == False
    print("   [OK] Useless detection works")

    print()
    print("2. Testing Completeness Checker...")

    checker = CompletenessChecker()

    # Check completeness for empty data
    empty_report = checker.check_completeness("Test Company", {})
    print(f"   [OK] Empty data completeness: {empty_report.overall_completeness:.1f}%")
    assert empty_report.overall_completeness == 0
    assert empty_report.needs_research == True

    # Check completeness with partial data
    partial_data = {
        "overview": {
            "company_name": "Test Company",
            "description": "A test company",
            "industry": "Technology",
        },
        "financials": {
            "revenue": 1000000,
            "revenue_year": 2023,
        },
    }
    partial_report = checker.check_completeness("Test Company", partial_data)
    print(f"   [OK] Partial data completeness: {partial_report.overall_completeness:.1f}%")
    assert partial_report.overall_completeness > 0
    print(f"       - Gaps found: {len(partial_report.gaps)}")

    # Get priority
    priority = checker.get_research_priority(partial_report)
    print(f"   [OK] Research priority:")
    print(f"       - High: {priority['high_priority'][:3]}")
    print(f"       - Sources: {priority['sources_to_use'][:3]}")

    print()
    print("3. Testing Research Cache...")

    cache = get_cache()
    print(f"   [OK] Cache created at: {cache.storage_path}")

    # Store company data
    cache.store_company_data(
        company_name="Microsoft Corporation",
        section="overview",
        data={
            "company_name": "Microsoft Corporation",
            "description": "Technology company specializing in software",
            "industry": "Technology",
            "founded": "1975",
            "headquarters": "Redmond, WA",
        },
        sources=[
            {
                "url": "https://microsoft.com",
                "title": "Microsoft",
                "score": 0.95,
                "quality": "primary",
            },
        ],
    )
    print("   [OK] Stored overview data")

    cache.store_company_data(
        company_name="Microsoft Corporation",
        section="financials",
        data={
            "revenue": 211915000000,
            "revenue_year": 2023,
            "net_income": 72361000000,
            "market_cap": 2800000000000,
        },
    )
    print("   [OK] Stored financials data")

    # Retrieve data
    retrieved = cache.get_company_data("Microsoft Corporation")
    assert retrieved is not None
    print(f"   [OK] Retrieved: {retrieved.company_name}")
    print(f"       - Completeness: {retrieved.completeness.value}")
    print(f"       - Revenue: ${retrieved.financials.get('revenue', 0):,}")

    # Test gap identification
    gaps = cache.identify_gaps("Microsoft Corporation")
    print(f"   [OK] Gap analysis: {gaps.overall_completeness:.1f}% complete")
    print(f"       - Needs research: {gaps.needs_research}")
    print(f"       - Priority sections: {gaps.priority_sections[:3]}")

    # Test should_research
    decision = cache.should_research("Microsoft Corporation")
    print(f"   [OK] Should research: {decision['needs_research']}")
    print(f"       - Reason: {decision['reason']}")

    # Test for unknown company
    decision2 = cache.should_research("Unknown Company XYZ")
    assert decision2["needs_research"] == True
    print(f"   [OK] Unknown company needs research: {decision2['needs_research']}")

    print()
    print("4. Testing Persistence...")

    # Create new cache instance (should load from disk)
    cache2 = ResearchCache()
    retrieved2 = cache2.get_company_data("Microsoft Corporation")
    assert retrieved2 is not None
    assert retrieved2.company_name == "Microsoft Corporation"
    print("   [OK] Data persists across cache instances")

    # Check URL registry persists
    assert cache2.url_registry.is_known_useless("https://paywall-site.com/blocked") == True
    print("   [OK] URL registry persists")

    print()
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)

    # Print cache summary
    print()
    cache.print_summary()


if __name__ == "__main__":
    test_cache_functionality()
