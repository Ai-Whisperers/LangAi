"""
Enhanced Researcher Agent - Advanced web scraping with Firecrawl/ScrapeGraph.

This enhanced researcher builds on the base researcher by adding:
- Firecrawl integration for LLM-ready markdown extraction
- ScrapeGraph integration for AI-powered smart extraction
- Automatic fallback to basic scraping if APIs unavailable
- Enhanced company website crawling
- Structured data extraction from company pages
"""

from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse
from ...utils import get_logger

logger = get_logger(__name__)

from ...config import get_config
from ...llm.client_factory import get_tavily_client
from ...llm.smart_client import smart_completion
from ...state import OverallState
from ...prompts import GENERATE_QUERIES_PROMPT
from ...crawling import (
    WebScraper,
    create_web_scraper,
    ScrapingBackend,
)


def _get_extraction_schemas():
    """
    Lazy import of extraction schemas to avoid circular imports.

    Returns tuple: (CompanyBasicInfo, CompanyLeadership, CompanyProducts, FinancialHighlights)
    """
    from ...integrations.scrapegraph_client import (
        CompanyBasicInfo,
        CompanyLeadership,
        CompanyProducts,
        FinancialHighlights,
    )
    return CompanyBasicInfo, CompanyLeadership, CompanyProducts, FinancialHighlights


class EnhancedResearcherAgent:
    """
    Enhanced Researcher agent with advanced web scraping.

    Uses Firecrawl and ScrapeGraph for better data extraction:
    - Cleaner, LLM-ready markdown
    - Smart AI-powered extraction
    - Deep website crawling
    - Structured data output

    Falls back to basic scraping if APIs unavailable.
    """

    def __init__(
        self,
        search_tool: Optional[Callable] = None,
        llm_client: Optional[Any] = None,
        firecrawl_api_key: Optional[str] = None,
        scrapegraph_api_key: Optional[str] = None,
    ):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()
        self.web_scraper = create_web_scraper(
            firecrawl_key=firecrawl_api_key,
            scrapegraph_key=scrapegraph_api_key,
        )

    def research(self, company_name: str, missing_info: List[str] = None) -> Dict[str, Any]:
        """
        Research a company with enhanced scraping.

        Note: This method is sync because the LangGraph workflow is sync.
        """
        state = {
            "company_name": company_name,
            "missing_info": missing_info or []
        }
        return enhanced_researcher_node(state, self.web_scraper)


def create_enhanced_researcher_agent(
    search_tool: Callable = None,
    llm_client: Any = None,
    firecrawl_api_key: str = None,
    scrapegraph_api_key: str = None,
) -> EnhancedResearcherAgent:
    """Factory function to create an EnhancedResearcherAgent."""
    return EnhancedResearcherAgent(
        search_tool=search_tool,
        llm_client=llm_client,
        firecrawl_api_key=firecrawl_api_key,
        scrapegraph_api_key=scrapegraph_api_key,
    )


def _identify_company_domains(results: List[Dict], company_name: str) -> List[str]:
    """
    Identify potential company official websites from search results.

    Args:
        results: Search results from Tavily
        company_name: Name of the company being researched

    Returns:
        List of URLs that might be official company websites
    """
    company_domains = []
    company_name_lower = company_name.lower().replace(" ", "").replace("-", "")

    # Patterns that suggest official company sites
    official_patterns = [
        "about", "company", "corporate", "oficial", "official",
        "who-we-are", "quienes-somos", "nosotros"
    ]

    seen_domains: Set[str] = set()

    for result in results:
        url = result.get("url", "")
        if not url:
            continue

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Skip if already seen this domain
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        # Check if domain contains company name
        domain_clean = domain.replace("www.", "").replace("-", "").replace(".", "")
        if company_name_lower[:5] in domain_clean:
            # High confidence - domain contains company name
            # Return base URL for better crawling
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            company_domains.append(base_url)
            continue

        # Check if URL path suggests official company page
        path_lower = parsed.path.lower()
        if any(pattern in path_lower for pattern in official_patterns):
            title = result.get("title", "").lower()
            if company_name_lower[:5] in title.replace(" ", ""):
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                if base_url not in company_domains:
                    company_domains.append(base_url)

    return company_domains[:2]  # Limit to top 2 domains


def _deep_scrape_company_website(
    domain_url: str,
    company_name: str,
    web_scraper: WebScraper,
    config: Any,
) -> Dict[str, Any]:
    """
    Perform deep scraping of a company website.

    Uses Firecrawl/ScrapeGraph for enhanced extraction.

    Args:
        domain_url: Company website URL
        company_name: Company name for context
        web_scraper: WebScraper instance
        config: Research configuration

    Returns:
        Dict with scraped content and extracted data
    """
    results = {
        "pages": [],
        "extracted_data": {},
        "urls_discovered": [],
    }

    backends = web_scraper.get_available_backends()
    logger.info(f"Deep scraping {domain_url} - available backends: {backends}")

    # Step 1: Discover URLs on the site
    try:
        discovered_urls = web_scraper.map_urls(domain_url, limit=50)
        results["urls_discovered"] = discovered_urls
        logger.info(f"Discovered {len(discovered_urls)} URLs on {domain_url}")
    except Exception as e:
        logger.warning(f"URL mapping failed: {e}")
        discovered_urls = [domain_url]

    # Step 2: Crawl the website with intelligent page selection
    try:
        crawl_result = web_scraper.crawl(
            url=domain_url,
            max_pages=config.domain_exploration_max_pages,
            max_depth=2,
            include_paths=["/about", "/team", "/products", "/services", "/investors"],
            exclude_paths=["/blog/", "/news/2", "/careers/", "/privacy", "/terms"],
        )

        for page in crawl_result.pages:
            if page.success:
                results["pages"].append(page.to_research_format())

        logger.info(f"Crawled {len(results['pages'])} pages from {domain_url}")

    except Exception as e:
        logger.warning(f"Website crawl failed: {e}")

    # Step 3: Smart extraction for specific data types (if ScrapeGraph available)
    if ScrapingBackend.SCRAPEGRAPH in backends:
        # Get schemas via lazy import to avoid circular imports
        CompanyBasicInfo, CompanyLeadership, CompanyProducts, _ = _get_extraction_schemas()

        extraction_tasks = [
            ("/about", "Extract company description, founding year, headquarters, and mission", CompanyBasicInfo),
            ("/team", "Extract names and titles of executives and leadership team", CompanyLeadership),
            ("/products", "Extract product names, descriptions, and categories", CompanyProducts),
        ]

        for path_hint, prompt, schema in extraction_tasks:
            # Find relevant URL
            target_url = None
            for url in discovered_urls:
                if path_hint in url.lower():
                    target_url = url
                    break

            if not target_url:
                target_url = domain_url

            try:
                extract_result = web_scraper.smart_extract(
                    url=target_url,
                    prompt=f"For {company_name}: {prompt}",
                    output_schema=schema,
                )

                if extract_result.success and extract_result.extracted_data:
                    key = path_hint.strip("/") or "general"
                    results["extracted_data"][key] = extract_result.extracted_data
                    logger.info(f"Smart extraction successful for {path_hint}")

            except Exception as e:
                logger.warning(f"Smart extraction failed for {path_hint}: {e}")

    return results


def _explore_with_enhanced_scraping(
    domains: List[str],
    company_name: str,
    web_scraper: WebScraper,
    config: Any,
) -> List[Dict[str, Any]]:
    """
    Explore company domains with enhanced scraping.

    Args:
        domains: List of domain URLs to explore
        company_name: Company name for context
        web_scraper: WebScraper instance
        config: Research configuration

    Returns:
        List of research-formatted results
    """
    all_results = []

    for domain_url in domains:
        try:
            logger.info(f"Enhanced exploration of: {domain_url}")

            scrape_data = _deep_scrape_company_website(
                domain_url=domain_url,
                company_name=company_name,
                web_scraper=web_scraper,
                config=config,
            )

            # Add scraped pages to results
            all_results.extend(scrape_data["pages"])

            # Convert extracted structured data to research format
            for key, data in scrape_data.get("extracted_data", {}).items():
                if data:
                    # Convert structured data to readable content
                    if hasattr(data, "dict"):
                        content_dict = data.dict()
                    elif isinstance(data, dict):
                        content_dict = data
                    else:
                        content_dict = {"data": str(data)}

                    content = "\n".join(
                        f"**{k}**: {v}" for k, v in content_dict.items()
                        if v and v != [] and v != {}
                    )

                    all_results.append({
                        "title": f"{company_name} - {key.replace('_', ' ').title()}",
                        "url": domain_url,
                        "content": content,
                        "score": 0.95,  # High score for structured extraction
                        "source": "enhanced_scraper",
                        "extraction_type": key,
                    })

            logger.info(
                f"Enhanced exploration added {len(scrape_data['pages'])} pages "
                f"and {len(scrape_data['extracted_data'])} extractions"
            )

        except Exception as e:
            logger.warning(f"Enhanced exploration failed for {domain_url}: {e}")

    return all_results


def enhanced_researcher_node(
    state: OverallState,
    web_scraper: WebScraper = None
) -> Dict[str, Any]:
    """
    Enhanced Researcher Agent Node with Firecrawl/ScrapeGraph (cost-optimized).

    Extends base researcher with:
    - LLM-ready markdown from Firecrawl
    - Smart AI extraction from ScrapeGraph
    - Deep website crawling
    - Structured data extraction
    - Smart model routing to DeepSeek V3 ($0.14/1M)

    Args:
        state: Current workflow state
        web_scraper: Optional WebScraper instance (creates one if not provided)

    Returns:
        State update with enhanced sources and agent metrics
    """
    logger.info("Enhanced Researcher agent starting")

    config = get_config()
    company_name = state["company_name"]

    # Create web scraper if not provided
    if web_scraper is None:
        web_scraper = create_web_scraper()

    backends = web_scraper.get_available_backends()
    logger.info(f"Available scraping backends: {backends}")

    # Step 1: Generate search queries (cost-optimized)
    logger.debug("Generating targeted queries")

    missing_info = state.get("missing_info", [])
    if missing_info:
        num_queries = 3
        query_context = f"""
Previous research had gaps. Focus queries on:
{chr(10).join(f'- {info}' for info in missing_info[:3])}
"""
    else:
        num_queries = 5
        query_context = ""

    prompt = GENERATE_QUERIES_PROMPT.format(
        company_name=company_name,
        num_queries=num_queries
    )
    if query_context:
        prompt += f"\n\n{query_context}"

    # Use smart_completion - routes to DeepSeek V3 for extraction
    result = smart_completion(
        prompt=prompt,
        task_type="extraction",  # Routes to DeepSeek V3 ($0.14/1M)
        max_tokens=config.researcher_max_tokens,
        temperature=config.researcher_temperature
    )

    fallback_queries = [
        f"{company_name} company overview",
        f"{company_name} revenue financial performance",
        f"{company_name} products services",
        f"{company_name} competitors market position",
        f"{company_name} recent news developments"
    ]

    # Parse the JSON response
    try:
        import json
        queries = json.loads(result.content)
        if not isinstance(queries, list):
            queries = fallback_queries
    except json.JSONDecodeError:
        queries = fallback_queries

    query_cost = result.cost

    logger.info(f"Generated {len(queries)} queries")

    # Step 2: Execute searches via Tavily
    logger.debug("Searching for sources via Tavily")

    tavily_client = get_tavily_client()
    all_results = []
    sources = []

    for query in queries:
        logger.debug(f"Executing search: {query}")
        search_response = tavily_client.search(
            query=query,
            max_results=3
        )

        for result in search_response.get("results", []):
            all_results.append(result)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0.0)
            })

    search_cost = len(queries) * 0.001
    logger.info(f"Found {len(all_results)} results from Tavily search")

    # Step 3: Enhanced Domain Exploration with Firecrawl/ScrapeGraph
    exploration_results = []
    extraction_count = 0

    if config.enable_domain_exploration and not missing_info:
        logger.debug("Identifying company domains for enhanced exploration")
        company_domains = _identify_company_domains(all_results, company_name)

        if company_domains:
            logger.info(f"Enhanced exploration of {len(company_domains)} domains")

            exploration_results = _explore_with_enhanced_scraping(
                domains=company_domains,
                company_name=company_name,
                web_scraper=web_scraper,
                config=config,
            )

            # Count structured extractions
            extraction_count = sum(
                1 for r in exploration_results
                if r.get("source") == "enhanced_scraper"
            )

            logger.info(
                f"Enhanced exploration added {len(exploration_results)} results "
                f"({extraction_count} structured extractions)"
            )

            # Add exploration results
            for exp_result in exploration_results:
                all_results.append(exp_result)
                sources.append({
                    "title": exp_result.get("title", ""),
                    "url": exp_result.get("url", ""),
                    "score": exp_result.get("score", 0.0),
                    "source": exp_result.get("source", "enhanced_scraper")
                })

    logger.info(f"Total sources after enhanced exploration: {len(all_results)}")

    # Calculate total cost
    total_cost = query_cost + search_cost

    # Track agent output with enhanced metrics
    agent_output = {
        "queries_generated": len(queries),
        "queries": queries,
        "sources_found": len(sources),
        "tavily_results": len(all_results) - len(exploration_results),
        "exploration_results": len(exploration_results),
        "structured_extractions": extraction_count,
        "domains_explored": len(company_domains) if config.enable_domain_exploration else 0,
        "scraping_backends": [b.value for b in backends],
        "cost": total_cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    logger.info(f"Enhanced Researcher complete - cost: ${total_cost:.4f}")

    return {
        "search_results": all_results,
        "sources": sources,
        "agent_outputs": {"enhanced_researcher": agent_output},
        "total_cost": total_cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
