"""
Search Nodes for Research Workflow

This module contains nodes responsible for data gathering:
- generate_queries_node: Generate multilingual search queries
- search_node: Execute web searches via Tavily
- sec_edgar_node: Fetch SEC EDGAR filings (FREE)
- website_scraping_node: Scrape Wikipedia and company websites (FREE)
"""

from typing import Any, Dict, List

# Date-aware query generation
from ...agents.base.query_generation import get_leadership_queries, get_market_data_queries
from ...agents.research.multilingual_search import Region, create_multilingual_generator
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
        "search_queries": all_queries,
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
    search_trace: List[Dict[str, Any]] = []
    total_search_cost = 0.0

    search_queries = state.get("search_queries", []) or []
    for query in search_queries[:5]:  # Limit to 5 queries for cost control
        try:
            # Use premium tier for automatic fallback: Tavily → Serper → DuckDuckGo
            response = router.search(query=query, quality="premium", max_results=5)

            # Always record per-query provenance (provider/cost/cache/errors)
            try:
                search_trace.append(response.to_dict())
            except Exception:
                search_trace.append(
                    {
                        "query": query,
                        "provider": getattr(response, "provider", ""),
                        "quality_tier": getattr(response, "quality_tier", ""),
                        "cost": getattr(response, "cost", 0.0),
                        "cached": getattr(response, "cached", False),
                        "success": getattr(response, "success", False),
                        "error": getattr(response, "error", None),
                        "results": [],
                    }
                )

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
    print(f"[OK] Found {len(search_results)} results from {len(search_queries[:5])} queries")
    print(f"[STATS] Providers used: {stats['by_provider']}")

    return {
        "search_results": search_results,
        "sources": sources,
        "search_trace": search_trace,
        "search_stats": stats,
        "total_cost": state.get("total_cost", 0.0) + total_search_cost,
    }


def _should_skip_sec_edgar(detected_region: str) -> bool:
    return bool(detected_region and detected_region not in ["north_america", "global", ""])


def _add_sec_filing_entries(
    sec_data: Dict[str, Any],
    filings: List[Any],
    *,
    description: str,
    limit: int,
) -> int:
    added = 0
    for filing in filings[:limit]:
        sec_data["filings"].append(
            {
                "type": getattr(filing, "form_type", ""),
                "date": getattr(filing, "filing_date", ""),
                "url": getattr(filing, "file_url", ""),
                "description": getattr(filing, "description", None) or description,
            }
        )
        added += 1
    return added


def _populate_sec_filings(edgar: Any, ticker_or_cik: str, sec_data: Dict[str, Any]) -> None:
    annual_result = edgar.get_10k_filings(ticker_or_cik, years=2)
    if annual_result.success and annual_result.filings:
        added = _add_sec_filing_entries(
            sec_data,
            annual_result.filings,
            description="Annual Report",
            limit=2,
        )
        print(f"  [10-K] Found {len(annual_result.filings)} annual reports (saved {added})")

    quarterly_result = edgar.get_10q_filings(ticker_or_cik, quarters=4)
    if quarterly_result.success and quarterly_result.filings:
        added = _add_sec_filing_entries(
            sec_data,
            quarterly_result.filings,
            description="Quarterly Report",
            limit=2,
        )
        print(f"  [10-Q] Found {len(quarterly_result.filings)} quarterly reports (saved {added})")

    events_result = edgar.get_8k_filings(ticker_or_cik, max_results=5)
    if events_result.success and events_result.filings:
        added = _add_sec_filing_entries(
            sec_data,
            events_result.filings,
            description="Material Event",
            limit=3,
        )
        print(f"  [8-K] Found {len(events_result.filings)} material events (saved {added})")


def _build_sec_sources(sec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    sec_sources: List[Dict[str, Any]] = []
    for filing in sec_data.get("filings", [])[:5]:
        sec_sources.append(
            {
                "title": f"SEC {filing.get('type')}: {filing.get('description')} ({filing.get('date')})",
                "url": filing.get("url", ""),
                "score": 0.95,
                "source_type": "sec_filing",
            }
        )
    return sec_sources


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
    detected_region = state.get("detected_region", "") or ""

    # Only fetch SEC data for US/North American companies or if no region detected
    if _should_skip_sec_edgar(detected_region):
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

        _populate_sec_filings(edgar, ticker_or_cik, sec_data)
        sec_sources = _build_sec_sources(sec_data)

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


def _scrape_wikipedia(company_name: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if not WIKIPEDIA_AVAILABLE:
        return {}, []
    try:
        wiki = get_wikipedia_client()
        wiki_result = wiki.get_company_info(company_name)
        if not (wiki_result.success and wiki_result.summary):
            return {}, []

        content = {
            "wikipedia": {
                "title": wiki_result.title,
                "summary": wiki_result.summary[:3000],
                "url": wiki_result.url,
                "categories": wiki_result.categories[:5],
                "infobox": wiki_result.infobox.to_dict() if wiki_result.infobox else None,
            }
        }
        sources = [
            {
                "title": f"Wikipedia: {wiki_result.title}",
                "url": wiki_result.url,
                "score": 0.85,
                "source_type": "wikipedia",
            }
        ]
        return content, sources
    except Exception:
        return {}, []


def _select_company_urls(company_name: str, search_results: List[Dict[str, Any]]) -> List[str]:
    urls: List[str] = []
    company_lc = company_name.lower()
    for result in search_results:
        url = (result.get("url") or "").strip()
        title = (result.get("title") or "").lower()
        if not url:
            continue
        url_lc = url.lower()
        if any(s in url_lc for s in ["linkedin.com", "facebook.com", "twitter.com", "x.com"]):
            continue
        if any(
            term in url_lc for term in ["/about", "/company", "/who-we-are", "/our-story"]
        ) or any(term in title for term in ["about us", "company", "who we are", company_lc]):
            urls.append(url)

    deduped: List[str] = []
    for u in urls:
        if u not in deduped:
            deduped.append(u)
        if len(deduped) >= 2:
            break
    return deduped


def _scrape_urls_with_jina(urls: List[str]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if not (JINA_AVAILABLE and urls):
        return {}, []

    from ...integrations.jina_reader import get_jina_reader

    reader = get_jina_reader()
    scraped: Dict[str, Any] = {}
    sources: List[Dict[str, Any]] = []

    for url in urls:
        result = reader.read_url(url)
        if not result.success:
            continue
        if not result.content or len(result.content) <= 500:
            continue

        url_key = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        scraped[f"website_{url_key}"] = {
            "url": url,
            "content": result.content[:5000],
            "length": len(result.content),
            "title": result.title,
        }
        sources.append(
            {
                "title": f"Company Website: {url[:50]}...",
                "url": url,
                "score": 0.90,
                "source_type": "company_website",
            }
        )

    return scraped, sources


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

    wiki_content, wiki_sources = _scrape_wikipedia(company_name)
    if wiki_content:
        scraped_content.update(wiki_content)
        sources.extend(wiki_sources)
        print("  [WIKI] Added Wikipedia content")
    else:
        print(f"  [WIKI] No Wikipedia article found for '{company_name}'")

    search_results = state.get("search_results", []) or []
    company_urls = _select_company_urls(company_name, search_results)
    if not company_urls:
        print("  [JINA] No company website URLs found in search results")
    else:
        jina_content, jina_sources = _scrape_urls_with_jina(company_urls)
        scraped_content.update(jina_content)
        sources.extend(jina_sources)
        if jina_sources:
            print(f"  [JINA] Added {len(jina_sources)} company pages")
        else:
            print("  [JINA] No content scraped from selected URLs")

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
