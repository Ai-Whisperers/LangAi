#!/usr/bin/env python3
"""
Test script for Firecrawl and ScrapeGraph integrations.

Run this script to verify the scraping integrations are working correctly.

Usage:
    python scripts/test_scraping_integrations.py
    python scripts/test_scraping_integrations.py --url https://example.com
    python scripts/test_scraping_integrations.py --test-all
"""

import argparse
import logging
import os
import sys
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported."""
    print("\n=== Testing Imports ===\n")

    try:
        from company_researcher.integrations import (
            FirecrawlClient,
            ScrapeGraphClient,
            create_firecrawl_client,
            create_scrapegraph_client,
        )

        print("✓ Firecrawl and ScrapeGraph clients imported successfully")
    except ImportError as e:
        print(f"✗ Import error for clients: {e}")
        return False

    try:
        from company_researcher.crawling import ScrapingBackend, WebScraper, create_web_scraper

        print("✓ WebScraper imported successfully")
    except ImportError as e:
        print(f"✗ Import error for WebScraper: {e}")
        return False

    try:
        from company_researcher.agents.research import (
            EnhancedResearcherAgent,
            create_enhanced_researcher_agent,
        )

        print("✓ EnhancedResearcherAgent imported successfully")
    except ImportError as e:
        print(f"✗ Import error for EnhancedResearcherAgent: {e}")
        return False

    return True


def test_api_keys():
    """Test that API keys are configured."""
    print("\n=== Checking API Keys ===\n")

    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    scrapegraph_key = os.getenv("SCRAPEGRAPH_API_KEY")

    if firecrawl_key and firecrawl_key != "your_firecrawl_key_here":
        print("✓ FIRECRAWL_API_KEY is set")
    else:
        print("⚠ FIRECRAWL_API_KEY not set (Firecrawl features will be disabled)")

    if scrapegraph_key and scrapegraph_key != "your_scrapegraph_key_here":
        print("✓ SCRAPEGRAPH_API_KEY is set")
    else:
        print("⚠ SCRAPEGRAPH_API_KEY not set (ScrapeGraph features will be disabled)")

    return True


def test_web_scraper_backends():
    """Test WebScraper backend detection."""
    print("\n=== Testing WebScraper Backends ===\n")

    from company_researcher.crawling import ScrapingBackend, create_web_scraper

    scraper = create_web_scraper()
    backends = scraper.get_available_backends()

    print(f"Available backends: {[b.value for b in backends]}")

    if ScrapingBackend.FIRECRAWL in backends:
        print("✓ Firecrawl backend available")
    else:
        print("⚠ Firecrawl backend not available (need API key)")

    if ScrapingBackend.SCRAPEGRAPH in backends:
        print("✓ ScrapeGraph backend available")
    else:
        print("⚠ ScrapeGraph backend not available (need API key)")

    if ScrapingBackend.BASIC in backends:
        print("✓ Basic backend available (always available)")

    return True


def test_basic_scrape(url: str = "https://example.com"):
    """Test basic scraping functionality."""
    print(f"\n=== Testing Basic Scrape: {url} ===\n")

    from company_researcher.crawling import create_web_scraper

    scraper = create_web_scraper()
    result = scraper.scrape(url)

    if result.success:
        print(f"✓ Scrape successful using backend: {result.backend_used}")
        print(f"  Title: {result.title or '(no title)'}")
        print(f"  Markdown length: {len(result.markdown)} chars")
        print(f"  First 200 chars: {result.markdown[:200]}...")
    else:
        print(f"✗ Scrape failed: {result.error}")

    return result.success


def test_firecrawl_client(url: str = "https://example.com"):
    """Test Firecrawl client directly."""
    print(f"\n=== Testing Firecrawl Client: {url} ===\n")

    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_key or firecrawl_key == "your_firecrawl_key_here":
        print("⚠ Skipping Firecrawl test (no API key)")
        return True

    from company_researcher.integrations import create_firecrawl_client

    client = create_firecrawl_client()

    # Test scrape
    print("Testing scrape_url...")
    result = client.scrape(url)
    if result.success:
        print(f"✓ Firecrawl scrape successful")
        print(f"  Title: {result.title}")
        print(f"  Markdown: {len(result.markdown)} chars")
    else:
        print(f"✗ Firecrawl scrape failed: {result.error}")
        return False

    # Test map (if it's a real website)
    if url != "https://example.com":
        print("\nTesting map_url...")
        map_result = client.map_url(url, limit=10)
        if map_result.success:
            print(f"✓ Firecrawl map found {len(map_result.urls)} URLs")
        else:
            print(f"⚠ Firecrawl map failed: {map_result.error}")

    return True


def test_scrapegraph_client(url: str = "https://example.com"):
    """Test ScrapeGraph client directly."""
    print(f"\n=== Testing ScrapeGraph Client: {url} ===\n")

    scrapegraph_key = os.getenv("SCRAPEGRAPH_API_KEY")
    if not scrapegraph_key or scrapegraph_key == "your_scrapegraph_key_here":
        print("⚠ Skipping ScrapeGraph test (no API key)")
        return True

    from company_researcher.integrations import create_scrapegraph_client

    client = create_scrapegraph_client()

    # Test markdownify
    print("Testing markdownify...")
    result = client.markdownify(url)
    if result.success:
        print(f"✓ ScrapeGraph markdownify successful")
        print(f"  Markdown: {len(result.markdown)} chars")
    else:
        print(f"✗ ScrapeGraph markdownify failed: {result.error}")
        return False

    # Test smart extraction (if it's a real website)
    if url != "https://example.com":
        print("\nTesting smart_scrape...")
        extract_result = client.smart_scrape(
            url=url, prompt="Extract the main heading and first paragraph"
        )
        if extract_result.success:
            print(f"✓ ScrapeGraph smart_scrape successful")
            print(f"  Extracted: {extract_result.extracted_data}")
        else:
            print(f"⚠ ScrapeGraph smart_scrape failed: {extract_result.error}")

    return True


def test_smart_extract(url: str = "https://microsoft.com/en-us/about"):
    """Test smart extraction with real company website."""
    print(f"\n=== Testing Smart Extraction: {url} ===\n")

    from company_researcher.crawling import create_web_scraper

    scraper = create_web_scraper()

    if not any(
        k
        for k in [os.getenv("FIRECRAWL_API_KEY"), os.getenv("SCRAPEGRAPH_API_KEY")]
        if k and k != "your_firecrawl_key_here" and k != "your_scrapegraph_key_here"
    ):
        print("⚠ Skipping smart extraction test (no API keys)")
        return True

    result = scraper.smart_extract(
        url=url, prompt="Extract company name, headquarters, and a brief description"
    )

    if result.success:
        print(f"✓ Smart extraction successful using backend: {result.backend_used}")
        print(f"  Extracted data: {result.extracted_data}")
    else:
        print(f"✗ Smart extraction failed: {result.error}")
        return False

    return True


def run_all_tests(url: Optional[str] = None):
    """Run all integration tests."""
    print("=" * 60)
    print("FIRECRAWL & SCRAPEGRAPH INTEGRATION TESTS")
    print("=" * 60)

    test_url = url or "https://example.com"
    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test API keys
    results.append(("API Keys", test_api_keys()))

    # Test WebScraper backends
    results.append(("WebScraper Backends", test_web_scraper_backends()))

    # Test basic scrape
    results.append(("Basic Scrape", test_basic_scrape(test_url)))

    # Test Firecrawl
    results.append(("Firecrawl Client", test_firecrawl_client(test_url)))

    # Test ScrapeGraph
    results.append(("ScrapeGraph Client", test_scrapegraph_client(test_url)))

    # Test smart extraction (only with real URL)
    if url and url != "https://example.com":
        results.append(("Smart Extraction", test_smart_extract(url)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


def main():
    parser = argparse.ArgumentParser(description="Test Firecrawl and ScrapeGraph integrations")
    parser.add_argument("--url", help="URL to test scraping against")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    parser.add_argument("--test-imports", action="store_true", help="Test imports only")
    parser.add_argument("--test-backends", action="store_true", help="Test backend detection")
    parser.add_argument("--test-firecrawl", action="store_true", help="Test Firecrawl only")
    parser.add_argument("--test-scrapegraph", action="store_true", help="Test ScrapeGraph only")

    args = parser.parse_args()

    if args.test_imports:
        test_imports()
    elif args.test_backends:
        test_imports()
        test_web_scraper_backends()
    elif args.test_firecrawl:
        test_imports()
        test_firecrawl_client(args.url or "https://example.com")
    elif args.test_scrapegraph:
        test_imports()
        test_scrapegraph_client(args.url or "https://example.com")
    else:
        success = run_all_tests(args.url)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
