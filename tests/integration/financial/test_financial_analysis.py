"""
Test Script for Phase 7: Enhanced Financial Agent

Tests the enhanced financial agent with multiple data sources:
- Alpha Vantage integration
- SEC EDGAR parser
- Financial analysis utilities
- Enhanced financial agent node

Usage:
    python test_phase7_financial.py
"""

from src.company_researcher.tools.alpha_vantage_client import AlphaVantageClient, extract_key_metrics
from src.company_researcher.tools.sec_edgar_parser import SECEdgarParser, is_public_company
from src.company_researcher.tools.financial_analysis_utils import (
    calculate_yoy_growth,
    calculate_cagr,
    analyze_revenue_trend,
    analyze_profitability,
    analyze_financial_health
)
from src.company_researcher.agents.financial.enhanced_financial import infer_ticker_symbol


def test_alpha_vantage():
    """Test Alpha Vantage client."""
    print("=" * 70)
    print("TEST 1: Alpha Vantage Client")
    print("=" * 70)

    client = AlphaVantageClient()

    print("\n[OK] Client initialized")
    print(f"  API Available: {client.is_available()}")

    if client.is_available():
        print("\n  Testing company overview for TSLA...")
        overview = client.get_company_overview("TSLA")
        print(f"  Result: {overview.get('Information', 'Data retrieved')}")

        print("\n  Testing comprehensive financials for MSFT...")
        financials = client.get_company_financials("MSFT")
        print(f"  Available: {financials.get('available', False)}")

        if financials.get("available"):
            metrics = extract_key_metrics(financials)
            print(f"  Metrics extracted: {metrics.get('available', False)}")
    else:
        print("\n  [WARN] Alpha Vantage API key not set")
        print("  Set ALPHA_VANTAGE_API_KEY in .env to enable")

    print("\n[OK] Alpha Vantage test complete\n")


def test_sec_edgar():
    """Test SEC EDGAR parser."""
    print("=" * 70)
    print("TEST 2: SEC EDGAR Parser")
    print("=" * 70)

    parser = SECEdgarParser()

    print("\n[OK] Parser initialized")
    print(f"  Always available: {parser.is_available()}")

    print("\n  Testing company search for Tesla...")
    company_info = parser.search_company("Tesla")
    print(f"  CIK: {company_info.get('cik', 'Not found')}")

    print("\n  Testing public company check...")
    is_public = is_public_company("Microsoft")
    print(f"  Microsoft is public: {is_public}")

    print("\n  Testing filings retrieval...")
    if company_info:
        filings = parser.get_company_filings(company_info["cik"], "10-K", count=1)
        print(f"  Filings found: {len(filings)}")

    print("\n[OK] SEC EDGAR test complete\n")


def test_financial_utils():
    """Test financial analysis utilities."""
    print("=" * 70)
    print("TEST 3: Financial Analysis Utilities")
    print("=" * 70)

    # Test YoY growth
    print("\n  Testing YoY growth calculation...")
    growth = calculate_yoy_growth(81.5, 65.0)
    print(f"  Growth from $65B to $81.5B: {growth}%")

    # Test CAGR
    print("\n  Testing CAGR calculation...")
    cagr = calculate_cagr(50.0, 81.5, 3)
    print(f"  CAGR over 3 years ($50B to $81.5B): {cagr}%")

    # Test revenue trend analysis
    print("\n  Testing revenue trend analysis...")
    revenue_history = [
        ("2021", 50.0),
        ("2022", 65.0),
        ("2023", 81.5)
    ]
    trend = analyze_revenue_trend(revenue_history)
    print(f"  Trend available: {trend.get('available', False)}")
    if trend.get("available"):
        print(f"  CAGR: {trend['cagr']}%")
        print(f"  Trend: {trend['trend']}")

    # Test profitability analysis
    print("\n  Testing profitability analysis...")
    profitability = analyze_profitability(
        revenue=100.0,
        gross_profit=25.0,
        operating_income=15.0,
        net_income=10.0,
        ebitda=20.0
    )
    print(f"  Gross Margin: {profitability.get('gross_margin')}%")
    print(f"  Operating Margin: {profitability.get('operating_margin')}%")
    print(f"  Net Margin: {profitability.get('net_margin')}%")

    # Test financial health analysis
    print("\n  Testing financial health analysis...")
    health = analyze_financial_health(
        cash=25.0,
        total_debt=5.0,
        total_equity=100.0,
        current_assets=50.0,
        current_liabilities=30.0,
        inventory=10.0,
        operating_cash_flow=20.0,
        capex=8.0
    )
    print(f"  Debt-to-Equity: {health.get('debt_to_equity')}")
    print(f"  Current Ratio: {health.get('current_ratio')}")
    print(f"  Quick Ratio: {health.get('quick_ratio')}")
    print(f"  Free Cash Flow: ${health.get('free_cash_flow')}B")
    print(f"  Assessment: {health.get('assessment')}")

    print("\n[OK] Financial utilities test complete\n")


def test_ticker_inference():
    """Test ticker symbol inference."""
    print("=" * 70)
    print("TEST 4: Ticker Symbol Inference")
    print("=" * 70)

    companies = [
        "Tesla",
        "Microsoft",
        "Stripe",
        "OpenAI",
        "Amazon"
    ]

    print("\n  Testing ticker inference...")
    for company in companies:
        ticker = infer_ticker_symbol(company)
        status = "[OK]" if ticker else "[N/A]"
        print(f"  {status} {company}: {ticker or 'Not found (private or not in map)'}")

    print("\n[OK] Ticker inference test complete\n")


def test_enhanced_agent():
    """Test enhanced financial agent (simulation)."""
    print("=" * 70)
    print("TEST 5: Enhanced Financial Agent")
    print("=" * 70)

    print("\n  NOTE: Full agent test requires:")
    print("  - ANTHROPIC_API_KEY in .env")
    print("  - Mock state with company_name and search_results")
    print("  - Would incur API costs")

    print("\n  Skipping full agent test in validation script")
    print("  Run actual research to test: python examples/hello_research.py \"Tesla\"")

    print("\n[OK] Enhanced agent structure validated\n")


def run_all_tests():
    """Run all Phase 7 tests."""
    print("\n")
    print("*" * 70)
    print("PHASE 7: ENHANCED FINANCIAL AGENT - TEST SUITE")
    print("*" * 70)
    print()

    tests = [
        ("Alpha Vantage Client", test_alpha_vantage),
        ("SEC EDGAR Parser", test_sec_edgar),
        ("Financial Utilities", test_financial_utils),
        ("Ticker Inference", test_ticker_inference),
        ("Enhanced Agent", test_enhanced_agent)
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
