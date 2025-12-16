"""
Search Nodes for Research Workflow

This module contains nodes responsible for data gathering:
- generate_queries_node: Generate multilingual search queries
- search_node: Execute web searches via Tavily
- sec_edgar_node: Fetch SEC EDGAR filings (FREE)
- website_scraping_node: Scrape Wikipedia and company websites (FREE)
"""

from typing import Any, Dict

# Date-aware query generation
from ...agents.base.query_generation import get_leadership_queries, get_market_data_queries
from ...agents.research.multilingual_search import Region, create_multilingual_generator
from ...config import get_config
from ...integrations.search_router import get_search_router
from ...llm.smart_client import TaskType, get_smart_client
from ...prompts import GENERATE_QUERIES_PROMPT
from ...state import OverallState

# SEC EDGAR integration (FREE - US public companies)
try:
    from ...integrations.sec_edgar import get_sec_edgar

    SEC_EDGAR_AVAILABLE = True
except ImportError:
    SEC_EDGAR_AVAILABLE = False

# Jina Reader integration (FREE - URL to Markdown)
try:
    JINA_AVAILABLE = True
except ImportError:
    JINA_AVAILABLE = False

# Wikipedia integration (FREE - Company overviews)
try:
    from ...integrations.wikipedia_client import get_wikipedia_client

    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False


def generate_queries_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 1: Generate search queries for the company using multilingual support.

    Uses SmartLLMClient with automatic provider fallback:
    - Primary: Anthropic Claude
    - Fallback 1: Groq (llama-3.3-70b-versatile) on rate limit
    - Fallback 2: DeepSeek on rate limit

    Args:
        state: Current workflow state

    Returns:
        State update with generated queries
    """
    config = get_config()
    smart_client = get_smart_client()

    print(f"\n[NODE] Generating search queries for: {state['company_name']}")

    # Get detected region from classification
    detected_region = state.get("detected_region", "")

    # Map detected region to Region enum
    # Region enum values: NORTH_AMERICA, LATAM_SPANISH, LATAM_BRAZIL, EUROPE, ASIA, UNKNOWN
    region_mapping = {
        "north_america": Region.NORTH_AMERICA,
        "latin_america": Region.LATAM_SPANISH,  # Default to Spanish for LATAM
        "latam_spanish": Region.LATAM_SPANISH,
        "latam_brazil": Region.LATAM_BRAZIL,
        "europe": Region.EUROPE,
        "asia_pacific": Region.ASIA,
        "asia": Region.ASIA,
        "middle_east": Region.UNKNOWN,  # No specific Middle East region
        "africa": Region.UNKNOWN,  # No specific Africa region
        "global": Region.UNKNOWN,
    }
    region = region_mapping.get(detected_region, Region.UNKNOWN)

    # Use multilingual generator for enhanced queries
    generator = create_multilingual_generator()
    multilingual_queries = generator.generate_queries(
        company_name=state["company_name"], region=region
    )

    # Extract query strings from MultilingualQuery objects
    multilingual_query_strings = [q.query for q in multilingual_queries[:10]]

    # Generate regional source queries (site:conatel.gov.py, site:bvpasa.com.py, etc.)
    regional_queries = generator.get_regional_source_queries(
        company_name=state["company_name"], max_queries=8
    )

    # Generate parent company and alternative name queries
    parent_queries = generator.get_parent_company_queries(state["company_name"])
    alt_name_queries = generator.get_alternative_name_queries(state["company_name"])

    # Generate date-aware queries for leadership and market data
    # Include Spanish for LATAM Spanish-speaking regions
    include_spanish = region in (Region.LATAM_SPANISH, Region.LATAM_BRAZIL)
    leadership_queries = get_leadership_queries(
        state["company_name"], include_spanish=include_spanish
    )
    market_queries = get_market_data_queries(state["company_name"], include_spanish=include_spanish)

    # Combine base queries with enhanced multilingual queries
    base_prompt = GENERATE_QUERIES_PROMPT.format(company_name=state["company_name"], num_queries=10)

    # Use SmartLLMClient with automatic provider fallback (Anthropic → Groq → DeepSeek)
    result = smart_client.complete(
        prompt=base_prompt,
        task_type=TaskType.SEARCH_QUERY,
        complexity="low",
        max_tokens=1000,
        temperature=0.3,
    )

    base_queries_text = result.content
    base_queries = [q.strip() for q in base_queries_text.strip().split("\n") if q.strip()]

    # Log which provider was used
    print(f"[INFO] LLM provider: {result.provider}/{result.model} ({result.routing_reason})")

    # Merge all queries (base + multilingual + regional + parent + alternatives + date-aware)
    all_queries = list(
        set(
            base_queries
            + multilingual_query_strings
            + regional_queries
            + parent_queries
            + alt_name_queries
            + leadership_queries
            + market_queries
        )
    )

    print(
        f"[OK] Generated {len(all_queries)} queries (region: {region.value}, date-aware: {len(leadership_queries) + len(market_queries)}, regional: {len(regional_queries)})"
    )

    # Get existing token counts with proper type handling
    existing_tokens = state.get("total_tokens") or {"input": 0, "output": 0}
    new_input_tokens = existing_tokens.get("input", 0) + result.input_tokens
    new_output_tokens = existing_tokens.get("output", 0) + result.output_tokens

    return {
        "queries": all_queries,
        "total_cost": state.get("total_cost", 0.0) + result.cost,
        "total_tokens": {"input": new_input_tokens, "output": new_output_tokens},
    }


def search_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 2: Execute web searches using SearchRouter with automatic fallback.

    Fallback chain (premium tier): Tavily → Serper → DuckDuckGo

    Args:
        state: Current workflow state

    Returns:
        State update with search results and sources
    """
    router = get_search_router()

    print(f"\n[NODE] Searching for: {state['company_name']}")
    print(f"[INFO] Available providers: {router._get_available_providers()}")

    # Execute searches for each query
    search_results = []
    sources = []
    total_search_cost = 0.0

    for query in state["queries"][:5]:  # Limit to 5 queries for cost control
        try:
            # Use premium tier for automatic fallback: Tavily → Serper → DuckDuckGo
            response = router.search(query=query, quality="premium", max_results=5)

            if response.success and response.results:
                for item in response.results:
                    result_dict = item.to_dict()
                    search_results.append(
                        {
                            "title": result_dict.get("title", ""),
                            "url": result_dict.get("url", ""),
                            "content": result_dict.get("snippet", ""),
                            "score": result_dict.get("score", 0.0),
                        }
                    )
                    sources.append(
                        {
                            "title": result_dict.get("title", ""),
                            "url": result_dict.get("url", ""),
                            "score": result_dict.get("score", 0.0),
                        }
                    )
                total_search_cost += response.cost
                print(
                    f"  [OK] '{query[:40]}...' via {response.provider}: {len(response.results)} results"
                )
            else:
                print(f"  [WARN] Search failed for '{query[:40]}...': {response.error}")
        except Exception as e:
            print(f"[WARN] Search error for query '{query}': {e}")
            continue

    # Log search stats
    stats = router.get_stats()
    print(f"[OK] Found {len(search_results)} results from {len(state['queries'][:5])} queries")
    print(f"[STATS] Providers used: {stats['by_provider']}")

    return {
        "search_results": search_results,
        "sources": sources,
        "total_cost": state.get("total_cost", 0.0) + total_search_cost,
    }


def sec_edgar_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 2b: Fetch SEC EDGAR filings for US public companies (FREE).

    This node runs after search and enriches data with official SEC filings
    including 10-K annual reports, 10-Q quarterly reports, and 8-K events.

    Args:
        state: Current workflow state

    Returns:
        State update with SEC filing data and sources
    """
    if not SEC_EDGAR_AVAILABLE:
        print("\n[NODE] SEC EDGAR not available (skipping)")
        return {}

    company_name = state["company_name"]
    detected_region = state.get("detected_region", "")

    # Only fetch SEC data for US/North American companies or if no region detected
    if detected_region and detected_region not in ["north_america", "global", ""]:
        print(f"\n[NODE] SEC EDGAR: Non-US region ({detected_region}), skipping")
        return {}

    print(f"\n[NODE] Fetching SEC EDGAR filings for: {company_name}")

    try:
        edgar = get_sec_edgar()

        # Search for company in SEC database
        search_result = edgar.search_company(company_name, max_results=3)

        if not search_result.success or not search_result.companies:
            print(f"  [INFO] No SEC filing found for '{company_name}'")
            return {}

        # Get the best match
        company = search_result.companies[0]
        print(f"  [FOUND] {company.name} (CIK: {company.cik}, Ticker: {company.ticker})")

        # Collect SEC data
        sec_data = {
            "cik": company.cik,
            "sec_name": company.name,
            "ticker": company.ticker,
            "sic": company.sic,
            "sic_description": company.sic_description,
            "state_of_incorporation": company.state,
            "fiscal_year_end": company.fiscal_year_end,
            "filings": [],
        }

        # Get recent filings
        ticker_or_cik = company.ticker or company.cik

        # Fetch 10-K (annual)
        annual_result = edgar.get_10k_filings(ticker_or_cik, years=2)
        if annual_result.success and annual_result.filings:
            for filing in annual_result.filings[:2]:
                sec_data["filings"].append(
                    {
                        "type": filing.form_type,
                        "date": filing.filing_date,
                        "url": filing.file_url,
                        "description": "Annual Report",
                    }
                )
            print(f"  [10-K] Found {len(annual_result.filings)} annual reports")

        # Fetch 10-Q (quarterly)
        quarterly_result = edgar.get_10q_filings(ticker_or_cik, quarters=4)
        if quarterly_result.success and quarterly_result.filings:
            for filing in quarterly_result.filings[:2]:
                sec_data["filings"].append(
                    {
                        "type": filing.form_type,
                        "date": filing.filing_date,
                        "url": filing.file_url,
                        "description": "Quarterly Report",
                    }
                )
            print(f"  [10-Q] Found {len(quarterly_result.filings)} quarterly reports")

        # Fetch 8-K (material events)
        events_result = edgar.get_8k_filings(ticker_or_cik, max_results=5)
        if events_result.success and events_result.filings:
            for filing in events_result.filings[:3]:
                sec_data["filings"].append(
                    {
                        "type": filing.form_type,
                        "date": filing.filing_date,
                        "url": filing.file_url,
                        "description": filing.description or "Material Event",
                    }
                )
            print(f"  [8-K] Found {len(events_result.filings)} material events")

        # Add SEC sources to the sources list
        sec_sources = []
        for filing in sec_data["filings"][:5]:
            sec_sources.append(
                {
                    "title": f"SEC {filing['type']}: {filing['description']} ({filing['date']})",
                    "url": filing["url"],
                    "score": 0.95,  # SEC filings are authoritative
                    "source_type": "sec_filing",
                }
            )

        # Get existing sources and merge
        existing_sources = list(state.get("sources", []))
        merged_sources = sec_sources + existing_sources

        print(f"  [OK] Added {len(sec_sources)} SEC sources (total: {len(merged_sources)})")

        return {
            "sec_data": sec_data,
            "sources": merged_sources,
        }

    except Exception as e:
        print(f"  [ERROR] SEC EDGAR error: {e}")
        return {}


def website_scraping_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 2c: Scrape company websites for direct information (FREE with Jina/Wikipedia).

    This node extracts data directly from:
    - Wikipedia (FREE - company overview, history, facts)
    - Company websites via Jina Reader (FREE - about page, team, products)

    Args:
        state: Current workflow state

    Returns:
        State update with scraped content and sources
    """
    company_name = state["company_name"]
    sources = list(state.get("sources", []))
    scraped_content = {}

    print(f"\n[NODE] Scraping company websites for: {company_name}")

    # 1. Wikipedia (always try - FREE and reliable)
    if WIKIPEDIA_AVAILABLE:
        try:
            wiki = get_wikipedia_client()
            wiki_result = wiki.get_company_info(company_name)

            if wiki_result.success and wiki_result.summary:
                scraped_content["wikipedia"] = {
                    "title": wiki_result.title,
                    "summary": wiki_result.summary[:3000],  # Limit for LLM context
                    "url": wiki_result.url,
                    "categories": wiki_result.categories[:5],
                    "infobox": wiki_result.infobox.to_dict() if wiki_result.infobox else None,
                }
                sources.append(
                    {
                        "title": f"Wikipedia: {wiki_result.title}",
                        "url": wiki_result.url,
                        "score": 0.85,
                        "source_type": "wikipedia",
                    }
                )
                print(f"  [WIKI] Found: {wiki_result.title} ({len(wiki_result.summary):,} chars)")
            else:
                print(f"  [WIKI] No Wikipedia article found for '{company_name}'")
        except Exception as e:
            print(f"  [WIKI] Error: {e}")

    # 2. Company website via Jina Reader (FREE - if we have a URL)
    if JINA_AVAILABLE:
        # Find company website URLs from search results
        company_urls = []
        search_results = state.get("search_results", [])

        for result in search_results:
            url = result.get("url", "")
            title = result.get("title", "").lower()

            # Look for official about pages or company info
            if any(
                term in url.lower() for term in ["/about", "/company", "/who-we-are", "/our-story"]
            ):
                company_urls.append(url)
            elif any(
                term in title
                for term in ["about us", "company", "who we are", company_name.lower()]
            ):
                if "linkedin" not in url and "facebook" not in url and "twitter" not in url:
                    company_urls.append(url)

        # Limit to first 2 URLs (avoid rate limits)
        company_urls = company_urls[:2]

        if company_urls:
            try:
                import requests

                jina_headers = {"Accept": "text/plain", "User-Agent": "CompanyResearcher/1.0"}

                for url in company_urls:
                    try:
                        jina_url = f"https://r.jina.ai/{url}"
                        resp = requests.get(jina_url, headers=jina_headers, timeout=20)

                        if resp.status_code == 200 and len(resp.text) > 500:
                            # Limit content for LLM context
                            content = resp.text[:5000]
                            url_key = (
                                url.replace("https://", "")
                                .replace("http://", "")
                                .replace("/", "_")[:50]
                            )

                            scraped_content[f"website_{url_key}"] = {
                                "url": url,
                                "content": content,
                                "length": len(resp.text),
                            }
                            sources.append(
                                {
                                    "title": f"Company Website: {url[:50]}...",
                                    "url": url,
                                    "score": 0.90,
                                    "source_type": "company_website",
                                }
                            )
                            print(f"  [JINA] Scraped: {url[:60]}... ({len(resp.text):,} chars)")
                        else:
                            print(f"  [JINA] Skip: {url[:60]}... (status: {resp.status_code})")
                    except Exception as e:
                        print(f"  [JINA] Error scraping {url[:40]}: {e}")

            except Exception as e:
                print(f"  [JINA] Import/setup error: {e}")
        else:
            print("  [JINA] No company website URLs found in search results")

    # Summary
    total_scraped = len(scraped_content)
    if total_scraped > 0:
        print(f"  [OK] Scraped {total_scraped} sources (FREE)")
    else:
        print("  [INFO] No content scraped (continuing with search results)")

    return {
        "scraped_content": scraped_content,
        "sources": sources,
    }
