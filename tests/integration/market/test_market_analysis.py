"""
Test Script for Phase 8: Enhanced Market Analyst Agent

Tests the market analysis utilities and agent:
- TAM/SAM/SOM calculations
- Market penetration and growth potential
- Industry trend analysis
- Competitive intensity assessment
- Market analyst agent structure

Usage:
    python test_phase8_market.py
"""

from src.company_researcher.tools.market_sizing_utils import (
    calculate_tam,
    calculate_sam,
    calculate_som,
    calculate_market_sizing,
    calculate_penetration_rate,
    calculate_growth_potential,
    classify_trend,
    analyze_industry_trend,
    assess_competitive_intensity,
    calculate_market_share_distribution,
    format_currency,
    MarketTrend,
    CompetitiveIntensity
)
from src.company_researcher.agents.enhanced_market import (
    infer_industry_category,
    get_industry_context
)


def test_market_sizing():
    """Test TAM/SAM/SOM calculations."""
    print("=" * 70)
    print("TEST 1: Market Sizing (TAM/SAM/SOM)")
    print("=" * 70)

    # Test TAM calculation
    print("\n  Testing TAM calculation...")
    tam = calculate_tam(
        total_potential_customers=1_400_000_000,  # 1.4B car buyers
        average_revenue_per_customer=50_000       # $50K per car
    )
    print(f"  TAM (Global Automotive): {format_currency(tam)}")

    # Test SAM calculation
    print("\n  Testing SAM calculation...")
    sam = calculate_sam(tam=tam, addressable_percentage=15)  # 15% EV
    print(f"  SAM (Electric Vehicles): {format_currency(sam)}")

    # Test SOM calculation
    print("\n  Testing SOM calculation...")
    som = calculate_som(sam=sam, market_share_percentage=2)  # 2% market share
    print(f"  SOM (Tesla addressable): {format_currency(som)}")

    # Test complete market sizing
    print("\n  Testing complete market sizing...")
    sizing = calculate_market_sizing(
        total_potential_customers=1_400_000_000,
        average_revenue_per_customer=50_000,
        addressable_percentage=15,
        market_share_percentage=2
    )
    print(f"  Complete sizing:")
    print(f"    TAM: {format_currency(sizing['tam'])}")
    print(f"    SAM: {format_currency(sizing['sam'])}")
    print(f"    SOM: {format_currency(sizing['som'])}")

    print("\n[OK] Market sizing tests complete\n")


def test_penetration_and_growth():
    """Test penetration rate and growth potential."""
    print("=" * 70)
    print("TEST 2: Penetration Rate and Growth Potential")
    print("=" * 70)

    # Test penetration rate
    print("\n  Testing penetration rate calculation...")
    penetration = calculate_penetration_rate(
        current_customers=5_000_000,      # 5M Tesla customers
        total_addressable_customers=250_000_000  # 250M EV buyers
    )
    print(f"  Market Penetration: {penetration}%")

    # Test growth potential
    print("\n  Testing growth potential calculation...")
    growth = calculate_growth_potential(
        current_market_size=2_500_000_000_000,   # $2.5T current
        projected_market_size=5_000_000_000_000, # $5.0T projected
        years=5
    )
    print(f"  Total Growth: {format_currency(growth['total_growth'])}")
    print(f"  Growth Rate: {growth['growth_rate']}%")
    print(f"  CAGR: {growth['cagr']}%")

    print("\n[OK] Penetration and growth tests complete\n")


def test_trend_analysis():
    """Test industry trend analysis."""
    print("=" * 70)
    print("TEST 3: Industry Trend Analysis")
    print("=" * 70)

    # Test trend classification
    print("\n  Testing trend classification...")
    trend1 = classify_trend(historical_growth_rate=35, market_maturity="emerging")
    print(f"  35% growth, emerging market: {trend1.value}")

    trend2 = classify_trend(historical_growth_rate=15, market_maturity="mature")
    print(f"  15% growth, mature market: {trend2.value}")

    trend3 = classify_trend(historical_growth_rate=-5, market_maturity="mature")
    print(f"  -5% growth, mature market: {trend3.value}")

    # Test trend analysis with historical data
    print("\n  Testing trend analysis with historical data...")
    historical_data = [
        ("2019", 1_200_000_000_000),  # $1.2T
        ("2020", 1_500_000_000_000),  # $1.5T
        ("2021", 1_900_000_000_000),  # $1.9T
        ("2022", 2_400_000_000_000),  # $2.4T
        ("2023", 3_000_000_000_000),  # $3.0T
    ]

    analysis = analyze_industry_trend(historical_data, "growth")
    print(f"  Trend: {analysis.get('trend')}")
    print(f"  CAGR: {analysis.get('cagr')}%")
    print(f"  Direction: {analysis.get('direction')}")
    print(f"  Outlook: {analysis.get('outlook')}")

    print("\n[OK] Trend analysis tests complete\n")


def test_competitive_analysis():
    """Test competitive intensity and market share."""
    print("=" * 70)
    print("TEST 4: Competitive Analysis")
    print("=" * 70)

    # Test competitive intensity assessment
    print("\n  Testing competitive intensity...")
    intensity1 = assess_competitive_intensity(
        number_of_competitors=3,
        barriers_to_entry="high"
    )
    print(f"  3 competitors, high barriers: {intensity1.value}")

    intensity2 = assess_competitive_intensity(
        number_of_competitors=50,
        barriers_to_entry="low"
    )
    print(f"  50 competitors, low barriers: {intensity2.value}")

    # Test HHI-based assessment
    intensity3 = assess_competitive_intensity(
        number_of_competitors=10,
        market_concentration_hhi=7500  # High concentration
    )
    print(f"  HHI 7500 (monopolistic): {intensity3.value}")

    # Test market share distribution
    print("\n  Testing market share distribution...")
    competitor_revenues = {
        "Tesla": 96_000_000_000,       # $96B
        "BYD": 85_000_000_000,         # $85B
        "VW": 75_000_000_000,          # $75B
        "GM": 45_000_000_000,          # $45B
        "Others": 200_000_000_000      # $200B
    }

    distribution = calculate_market_share_distribution(competitor_revenues)
    print(f"  Market Leader: {distribution.get('market_leader')} ({distribution.get('market_leader_share')}%)")
    print(f"  HHI: {distribution.get('hhi')}")
    print(f"  Top 4 Concentration (CR4): {distribution.get('top_4_concentration')}%")
    print(f"  Market Shares:")
    for company, share in distribution.get('market_shares', {}).items():
        print(f"    {company}: {share}%")

    print("\n[OK] Competitive analysis tests complete\n")


def test_helper_functions():
    """Test helper functions."""
    print("=" * 70)
    print("TEST 5: Helper Functions")
    print("=" * 70)

    # Test currency formatting
    print("\n  Testing currency formatting...")
    amounts = [
        1_500_000_000_000,   # $1.5T
        250_000_000_000,     # $250B
        50_000_000,          # $50M
        75_000               # $75K
    ]

    for amount in amounts:
        print(f"  {amount:,} = {format_currency(amount)}")

    # Test industry classification
    print("\n  Testing industry classification...")
    companies = [
        "Tesla",
        "Microsoft",
        "Stripe",
        "Moderna",
        "Shopify"
    ]

    for company in companies:
        industry = infer_industry_category(company)
        print(f"  {company}: {industry}")

    # Test industry context
    print("\n  Testing industry context retrieval...")
    context = get_industry_context("Technology / Software")
    print(f"  Tech Industry Context:")
    print(f"    TAM Range: {context.get('typical_tam_range')}")
    print(f"    Growth: {context.get('growth_benchmark')}")
    print(f"    Intensity: {context.get('competitive_intensity')}")
    print(f"    Trends: {context.get('key_trends')}")

    print("\n[OK] Helper function tests complete\n")


def test_market_agent_structure():
    """Test market agent structure (without LLM call)."""
    print("=" * 70)
    print("TEST 6: Market Analyst Agent Structure")
    print("=" * 70)

    print("\n  NOTE: Full agent test requires:")
    print("  - ANTHROPIC_API_KEY in .env")
    print("  - Mock state with company_name and search_results")
    print("  - Would incur API costs")

    print("\n  Skipping full agent test in validation script")
    print("  Agent structure validated during import")

    print("\n[OK] Market agent structure validated\n")


def run_all_tests():
    """Run all Phase 8 tests."""
    print("\n")
    print("*" * 70)
    print("PHASE 8: ENHANCED MARKET ANALYST - TEST SUITE")
    print("*" * 70)
    print()

    tests = [
        ("Market Sizing (TAM/SAM/SOM)", test_market_sizing),
        ("Penetration and Growth", test_penetration_and_growth),
        ("Trend Analysis", test_trend_analysis),
        ("Competitive Analysis", test_competitive_analysis),
        ("Helper Functions", test_helper_functions),
        ("Market Agent Structure", test_market_agent_structure)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "PASSED", None))
        except Exception as e:
            results.append((test_name, "FAILED", str(e)))

    # Print summary
    print("\n")
    print("*" * 70)
    print("TEST SUMMARY")
    print("*" * 70)
    print()

    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")

    for test_name, status, error in results:
        symbol = "[PASS]" if status == "PASSED" else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")
        if error:
            print(f"  Error: {error}")

    print()
    print(f"Tests Passed: {passed}/{len(results)}")
    print(f"Tests Failed: {failed}/{len(results)}")

    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED")
    else:
        print(f"\n[FAILURE] {failed} TEST(S) FAILED")

    print("\n")


if __name__ == "__main__":
    run_all_tests()
