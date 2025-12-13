"""
Enhanced Workflow Integration Example.

This example demonstrates how to integrate the new enhanced modules
into your existing research workflow.

The improvements address 10 critical issues:
1. Semantic gap detection (not just pattern-based)
2. Gaming-resistant quality scoring
3. Diversified search queries
4. Enhanced contradiction detection
5. Ground truth validation
6. Typed state models
7. Unified quality scoring
8. Prompt management
9. Source selection with RAG
10. Integrated analysis pipeline

Run this example:
    python -m company_researcher.examples.enhanced_workflow_example
"""


# Import enhanced modules
from company_researcher.shared import (
    # Main pipeline
    EnhancedResearchPipeline,
    EnhancedAnalysisResult,

    # Individual pipelines
    run_quality_pipeline,
    run_gap_detection,
    run_contradiction_analysis,
    get_optimized_queries,
    select_best_sources,

    # Core components
    UnifiedQualityScorer,
    SemanticGapDetector,
    QueryDiversifier,
)

from company_researcher.validation import (
    GroundTruthValidator,
)

from company_researcher.quality import (
    EnhancedContradictionDetector,
)


from company_researcher.prompts import (
    get_prompt,
    get_prompt_registry,
)

from company_researcher.state import (
    TypedResearchState,
    FinancialMetrics,
    CompanyProfile,
)


# ============================================================================
# Example 1: Full Enhanced Pipeline
# ============================================================================

def example_full_pipeline():
    """
    Run the complete enhanced analysis pipeline.

    This is the recommended way to use all improvements together.
    """
    print("\n" + "="*60)
    print("Example 1: Full Enhanced Pipeline")
    print("="*60)

    # Sample research output (this would come from your existing workflow)
    research_output = {
        "company_name": "Apple Inc.",
        "agent_outputs": {
            "financial": {
                "summary": """Apple Inc. reported revenue of $383.3 billion for FY2023.
                Net income was $97 billion with a profit margin of 25.3%.
                The company has over 160,000 employees globally.
                Market capitalization exceeds $3 trillion.""",
                "analysis": "Strong financial performance with healthy margins.",
                "data_gaps": ["Specific R&D spending breakdown"]
            },
            "market": {
                "summary": """Apple holds approximately 20% of the global smartphone market.
                Main competitors include Samsung, Google, and Huawei.
                The company has been expanding in services and wearables.""",
                "analysis": "Dominant market position in premium segment.",
                "data_gaps": []
            },
            "product": {
                "summary": """Core products include iPhone, Mac, iPad, Apple Watch.
                Services include App Store, Apple Music, iCloud, Apple TV+.
                iPhone accounts for about 52% of revenue.""",
                "analysis": "Diversified product portfolio with services growth.",
                "data_gaps": ["Exact revenue by product line"]
            }
        },
        "sources": [
            {"url": "https://investor.apple.com/sec-filings", "title": "SEC Filings"},
            {"url": "https://www.apple.com/newsroom", "title": "Apple Newsroom"},
            {"url": "https://finance.yahoo.com/quote/AAPL", "title": "Yahoo Finance"},
        ],
        "company_overview": "Apple Inc. is a technology company headquartered in Cupertino, California."
    }

    # Create enhanced pipeline
    pipeline = EnhancedResearchPipeline(
        company_name="Apple Inc.",
        ticker="AAPL",
        use_embeddings=True
    )

    # Run full analysis
    result = pipeline.run_full_analysis(research_output)

    # Display results
    print(f"\nQuality Score: {result.quality_score:.1f}/100")
    print(f"Overall Confidence: {result.overall_confidence}")
    print(f"Critical Gaps: {len(result.critical_gaps)}")
    print(f"Contradictions: {result.has_critical_contradictions}")

    if result.validation_report:
        print(f"Verified Claims: {result.verified_claims}")
        print(f"Contradicted Claims: {result.contradicted_claims}")

    # Get improvement suggestions
    suggestions = pipeline.get_quality_improvements(result)
    print(f"\nImprovement Suggestions ({len(suggestions)}):")
    for s in suggestions[:5]:
        print(f"  - {s}")

    return result


# ============================================================================
# Example 2: Individual Components
# ============================================================================

def example_individual_components():
    """
    Use individual components separately for more control.
    """
    print("\n" + "="*60)
    print("Example 2: Individual Components")
    print("="*60)

    company_name = "Microsoft Corporation"

    # 1. Generate optimized search queries
    print("\n1. Query Diversification:")
    queries = get_optimized_queries(
        company_name,
        focus_areas=["financial", "market", "competitive"]
    )
    print(f"   Generated {len(queries)} diversified queries")
    for q in queries[:5]:
        print(f"   - {q}")

    # 2. Use prompt management
    print("\n2. Prompt Management:")
    registry = get_prompt_registry()

    # Get financial analysis prompt
    prompt = get_prompt(
        "financial_analysis",
        company_name=company_name,
        additional_context="Focus on cloud revenue growth."
    )
    print(f"   Generated prompt ({len(prompt)} chars)")
    print(f"   Preview: {prompt[:100]}...")

    # 3. Semantic gap detection
    print("\n3. Gap Detection:")
    detector = SemanticGapDetector()
    assessment = detector.detect_gaps(
        content="Revenue was $211 billion. The CEO is Satya Nadella.",
        sources=[{"url": "https://microsoft.com"}],
        company_name=company_name
    )
    print(f"   Coverage Score: {assessment.coverage_score:.2f}")
    print(f"   Detected Gaps: {len(assessment.gaps)}")
    for gap in assessment.gaps[:3]:
        print(f"   - {gap.field}: {gap.confidence.value}")


# ============================================================================
# Example 3: Typed State Models
# ============================================================================

def example_typed_models():
    """
    Use strongly-typed state models for better data validation.
    """
    print("\n" + "="*60)
    print("Example 3: Typed State Models")
    print("="*60)

    # Create validated financial metrics
    metrics = FinancialMetrics(
        revenue=383_000_000_000,  # $383B
        revenue_currency="USD",
        revenue_year=2023,
        revenue_growth_yoy=0.02,  # 2% growth
        net_income=97_000_000_000,
        profit_margin=0.253,
        market_cap=3_000_000_000_000,  # $3T
        employees=160000,
        pe_ratio=28.5
    )

    print(f"\nFinancial Metrics (validated):")
    print(f"  Revenue: {metrics.revenue_formatted}")
    print(f"  Market Cap: {metrics.market_cap_formatted}")
    print(f"  Profit Margin: {metrics.profit_margin:.1%}")
    print(f"  Revenue/Employee: ${metrics.revenue_per_employee:,.0f}")

    # Create company profile
    profile = CompanyProfile(
        name="Apple Inc.",
        ticker="AAPL",
        stock_exchange="NASDAQ",
        headquarters_city="Cupertino",
        headquarters_state="California",
        headquarters_country="USA",
        founded_year=1976,
        ceo_name="Tim Cook"
    )

    print(f"\nCompany Profile:")
    print(f"  Name: {profile.name} ({profile.ticker})")
    print(f"  HQ: {profile.headquarters_full}")
    print(f"  Founded: {profile.founded_year}")
    print(f"  CEO: {profile.ceo_name}")

    # Create full typed state
    state = TypedResearchState(
        company_name="Apple Inc.",
        financial_metrics=metrics
    )

    print(f"\nTyped State Created: {state.company_name}")
    print(f"  Duration: {state.duration_seconds:.2f}s")

    # Convert to legacy format if needed
    legacy = state.to_legacy_dict()
    print(f"  Legacy format keys: {list(legacy.keys())}")


# ============================================================================
# Example 4: Ground Truth Validation
# ============================================================================

def example_ground_truth():
    """
    Validate claims against ground truth from financial APIs.
    """
    print("\n" + "="*60)
    print("Example 4: Ground Truth Validation")
    print("="*60)

    validator = GroundTruthValidator()

    # Fetch ground truth for Apple
    print("\nFetching ground truth for AAPL...")
    ground_truth = validator.fetch_ground_truth("AAPL")

    if ground_truth:
        print(f"  Market Cap: ${ground_truth.market_cap:,.0f}")
        print(f"  Revenue: ${ground_truth.revenue:,.0f}")
        print(f"  Employees: {ground_truth.employees:,}")
        print(f"  P/E Ratio: {ground_truth.pe_ratio:.2f}")

        # Validate some claims
        claims_text = """
        Apple has a market cap of approximately $3 trillion.
        The company has 160,000 employees.
        Revenue in FY2023 was $383 billion.
        """

        report = validator.validate_claims({"text": claims_text}, ground_truth)
        print(f"\nValidation Report:")
        print(f"  Total Claims: {report.total_claims}")
        print(f"  Verified: {report.verified_count}")
        print(f"  Contradicted: {report.contradicted_count}")
        print(f"  Accuracy: {report.accuracy_rate:.1%}")
    else:
        print("  Could not fetch ground truth (API may be unavailable)")


# ============================================================================
# Example 5: Source Selection with RAG
# ============================================================================

def example_source_selection():
    """
    Use semantic source selection for better context.
    """
    print("\n" + "="*60)
    print("Example 5: Source Selection with RAG")
    print("="*60)

    # Sample sources (would come from search results)
    sources = [
        {
            "url": "https://investor.apple.com/financials",
            "title": "Apple Investor Relations - Financials",
            "snippet": "Quarterly earnings, annual reports, SEC filings for investors."
        },
        {
            "url": "https://www.bloomberg.com/apple",
            "title": "Apple News - Bloomberg",
            "snippet": "Latest Apple stock price, news, and analysis."
        },
        {
            "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193",
            "title": "Apple SEC Filings",
            "snippet": "Official SEC filings including 10-K, 10-Q, 8-K reports."
        },
        {
            "url": "https://techcrunch.com/tag/apple",
            "title": "Apple News - TechCrunch",
            "snippet": "Technology news and product announcements about Apple."
        },
        {
            "url": "https://www.apple.com/newsroom",
            "title": "Apple Newsroom",
            "snippet": "Official press releases and company announcements."
        },
        {
            "url": "https://www.reddit.com/r/apple",
            "title": "r/apple - Reddit",
            "snippet": "Community discussions about Apple products."
        },
        {
            "url": "https://finance.yahoo.com/quote/AAPL",
            "title": "AAPL Stock - Yahoo Finance",
            "snippet": "Real-time stock quotes, financials, and analysis."
        },
    ]

    # Select best sources for financial analysis
    print("\nSelecting sources for 'Apple financial performance'...")
    selected = select_best_sources(
        query="Apple financial performance revenue earnings",
        sources=sources,
        max_sources=4
    )

    print(f"\nSelected {len(selected)} sources:")
    for s in selected:
        score = s.get("combined_score", 0)
        print(f"  [{score:.2f}] {s['title']}")
        print(f"          {s['url'][:60]}...")


# ============================================================================
# Example 6: Contradiction Detection
# ============================================================================

def example_contradiction_detection():
    """
    Detect contradictions across multiple sources.
    """
    print("\n" + "="*60)
    print("Example 6: Contradiction Detection")
    print("="*60)

    detector = EnhancedContradictionDetector(use_embeddings=False)  # No embeddings for example

    # Two sources with conflicting info
    source_a = """
    Apple reported revenue of $383 billion in FY2023.
    The company has approximately 160,000 employees.
    Tim Cook has been CEO since 2011.
    Headquarters are in Cupertino, California.
    """

    source_b = """
    Apple's annual revenue was $395 billion.
    The workforce includes about 140,000 employees.
    Tim Cook became CEO in 2011.
    The company is based in Cupertino, CA.
    """

    report = detector.analyze(source_a, source_b, "sec_filing", "news_article")

    print(f"\nContradiction Report:")
    print(f"  Claims Analyzed: {report.total_claims_analyzed}")
    print(f"  Contradictions Found: {len(report.contradictions)}")
    print(f"  Has Critical: {report.has_critical}")

    for c in report.contradictions:
        print(f"\n  [{c.severity.value.upper()}] {c.contradiction_type.value}")
        print(f"    {c.explanation}")
        if c.resolution_suggestion:
            print(f"    Resolution: {c.resolution_suggestion}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "#"*60)
    print("# Enhanced Company Researcher - Usage Examples")
    print("#"*60)

    # Run examples
    example_full_pipeline()
    example_individual_components()
    example_typed_models()
    example_ground_truth()
    example_source_selection()
    example_contradiction_detection()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)

    # Summary of improvements
    print("""
SUMMARY OF IMPROVEMENTS:

1. QUALITY SCORING (Issue #2)
   - Multi-dimensional scoring (6 dimensions)
   - Gaming-resistant with weight adjustments
   - Integrated ground truth validation

2. GAP DETECTION (Issue #1)
   - Semantic analysis, not just pattern matching
   - Multi-signal detection (5 signals)
   - Confidence levels per gap

3. SEARCH (Issue #3)
   - Query diversification by category
   - Source selection with embeddings
   - Authority-weighted ranking

4. CONTRADICTION DETECTION (Issue #5)
   - Numeric normalization ($1.5B = 1500M)
   - Semantic comparison
   - Severity classification

5. GROUND TRUTH (Issue #6)
   - Yahoo Finance API integration
   - Claim extraction and validation
   - Tolerance-based matching

6. STATE MANAGEMENT (Issue #8)
   - Pydantic typed models
   - Runtime validation
   - Legacy compatibility

7. PROMPTS (Issue #10)
   - Versioned prompt templates
   - Performance metrics tracking
   - A/B testing support

All improvements are backward-compatible and can be adopted incrementally.
""")


if __name__ == "__main__":
    main()
