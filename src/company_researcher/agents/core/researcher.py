"""
Researcher Agent - Finds and gathers sources.

This agent is responsible for:
- Generating targeted search queries (including multilingual for regional companies)
- Executing web searches
- Exploring company domains for additional content (HTML link extraction)
- Collecting and ranking results
- Checking data quality thresholds before proceeding
- Returning quality sources for analysis

Enhanced with multilingual search support for LATAM and international companies.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse
from ...utils import get_logger

logger = get_logger(__name__)

from ...config import get_config
from ...llm.client_factory import (
    get_anthropic_client, get_tavily_client, safe_extract_json
)
from ...state import OverallState
from ...prompts import GENERATE_QUERIES_PROMPT
from ...crawling.domain_explorer import DomainExplorer, format_exploration_for_research

# Import enhancement modules
try:
    from ..research.multilingual_search import (
        create_multilingual_generator
    )
    from ..research.data_threshold import (
        create_threshold_checker
    )
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    logger.warning("Research enhancement modules not available - using basic search")


class ResearcherAgent:
    """Researcher agent for finding and gathering quality sources."""

    def __init__(
        self,
        search_tool: Optional[Callable] = None,
        llm_client: Optional[Any] = None
    ):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    def research(self, company_name: str, missing_info: List[str] = None) -> Dict[str, Any]:
        """
        Research a company by generating queries and gathering sources.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        state = {
            "company_name": company_name,
            "missing_info": missing_info or []
        }
        return researcher_agent_node(state)


def create_researcher_agent(
    search_tool: Callable = None,
    llm_client: Any = None
) -> ResearcherAgent:
    """Factory function to create a ResearcherAgent."""
    return ResearcherAgent(search_tool=search_tool, llm_client=llm_client)


def _detect_company_region(company_name: str, initial_results: List[Dict] = None) -> str:
    """
    Detect the likely region/country of a company.

    Args:
        company_name: Name of the company
        initial_results: Optional initial search results to analyze

    Returns:
        Country code (e.g., "mexico", "brazil", "paraguay", "united_states")
    """
    # LATAM company indicators
    latam_indicators = {
        "mexico": ["mexicano", "mexico", "méxico", "mx", "bmv", "bolsa mexicana"],
        "brazil": ["brasil", "brazil", "brasileiro", "b3", "bovespa", "sa", "s.a."],
        "paraguay": ["paraguay", "paraguayo", "asuncion", "asunción"],
        "argentina": ["argentina", "argentino", "buenos aires"],
        "colombia": ["colombia", "colombiano", "bogota", "bogotá"],
        "chile": ["chile", "chileno", "santiago"],
        "peru": ["peru", "perú", "peruano", "lima"],
    }

    company_lower = company_name.lower()

    # Check company name for indicators
    for country, indicators in latam_indicators.items():
        for indicator in indicators:
            if indicator in company_lower:
                return country

    # Check initial search results for location hints
    if initial_results:
        all_text = " ".join([
            r.get("content", "") + " " + r.get("title", "")
            for r in initial_results[:5]
        ]).lower()

        for country, indicators in latam_indicators.items():
            matches = sum(1 for ind in indicators if ind in all_text)
            if matches >= 2:
                return country

    # Default to US for unknown companies
    return "united_states"


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
        "who-we-are", "quienes-somos", "nosotros", "sobre-nos",
        "empresa", "institucional", "investors", "inversionistas"
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
            company_domains.append(url)
            continue

        # Check if URL path suggests official company page
        path_lower = parsed.path.lower()
        if any(pattern in path_lower for pattern in official_patterns):
            # Check title for company name match
            title = result.get("title", "").lower()
            if company_name_lower[:5] in title.replace(" ", ""):
                company_domains.append(url)

    return company_domains[:2]  # Limit to top 2 domains


def _explore_company_domains(
    domains: List[str],
    config: Any
) -> List[Dict[str, Any]]:
    """
    Explore identified company domains for additional content.

    Args:
        domains: List of domain URLs to explore
        config: Research configuration

    Returns:
        List of additional results from domain exploration
    """
    if not config.enable_domain_exploration or not domains:
        return []

    explorer = DomainExplorer(
        max_pages=config.domain_exploration_max_pages,
        timeout=config.domain_exploration_timeout,
        max_content_length=config.domain_exploration_max_content,
    )

    all_exploration_results = []

    for domain_url in domains:
        try:
            logger.info(f"Exploring domain: {domain_url}")
            result = explorer.explore_sync(domain_url)

            # Convert to research format
            formatted = format_exploration_for_research(result)
            all_exploration_results.extend(formatted)

            logger.info(
                f"Domain exploration found {len(formatted)} pages "
                f"from {result.domain}"
            )
        except Exception as e:
            logger.warning(f"Domain exploration failed for {domain_url}: {e}")

    return all_exploration_results


def _generate_multilingual_queries(
    company_name: str,
    country: str,
    topics: List[str] = None
) -> List[str]:
    """
    Generate multilingual search queries for a company.

    Args:
        company_name: Name of the company
        country: Country code for regional adaptation
        topics: Specific topics to search for

    Returns:
        List of search queries in multiple languages
    """
    if not ENHANCEMENTS_AVAILABLE:
        # Fallback to basic queries
        return [
            f"{company_name} company overview",
            f"{company_name} revenue financial performance",
            f"{company_name} products services",
            f"{company_name} competitors market position",
            f"{company_name} recent news developments"
        ]

    generator = create_multilingual_generator()

    if topics is None:
        topics = ["revenue", "annual_report", "market_share", "competitors", "leadership", "news"]

    # Generate queries
    query_dict = generator.generate_queries(
        company_name=company_name,
        country=country,
        topics=topics
    )

    # Flatten into list
    all_queries = []
    for topic_queries in query_dict.values():
        all_queries.extend(topic_queries)

    # Also add parent company queries if this is a known subsidiary
    parent_queries = generator.get_parent_company_queries(company_name)
    all_queries.extend(parent_queries)

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in all_queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique_queries.append(q)

    return unique_queries[:15]  # Limit to 15 queries


def _check_data_threshold(
    results: List[Dict],
    company_name: str,
    company_type: str = "public"
) -> Dict[str, Any]:
    """
    Check if search results meet minimum data thresholds.

    Args:
        results: Search results to analyze
        company_name: Name of the company
        company_type: Type of company (public, private, subsidiary)

    Returns:
        Dictionary with threshold check results
    """
    if not ENHANCEMENTS_AVAILABLE:
        return {
            "passes_threshold": True,
            "coverage": 50.0,
            "recommendations": [],
            "retry_strategies": []
        }

    checker = create_threshold_checker()

    # Combine content from results
    combined_content = "\n\n".join([
        f"Title: {r.get('title', '')}\n{r.get('content', '')}"
        for r in results
    ])

    # Import CompanyType
    from ...research.metrics_validator import CompanyType
    type_map = {
        "public": CompanyType.PUBLIC,
        "private": CompanyType.PRIVATE,
        "subsidiary": CompanyType.SUBSIDIARY,
    }
    ctype = type_map.get(company_type.lower(), CompanyType.PUBLIC)

    result = checker.check_threshold(
        content=combined_content,
        company_name=company_name,
        company_type=ctype
    )

    return {
        "passes_threshold": result.passes_threshold,
        "coverage": result.overall_coverage,
        "recommendations": result.recommendations,
        "retry_strategies": [s.value for s in result.retry_strategies],
        "section_coverage": {k: v for k, v in result.section_coverage.items()}
    }


def researcher_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Researcher Agent Node: Find and gather quality sources.

    This agent combines query generation and search execution into
    a single specialized agent focused on finding the best sources.

    Enhanced features:
    - Multilingual search for LATAM and international companies
    - Data quality threshold checking
    - Automatic retry with different strategies if initial search fails
    - Domain exploration for company websites

    Args:
        state: Current workflow state

    Returns:
        State update with sources and agent metrics
    """
    logger.info("Researcher agent starting - gathering sources")

    config = get_config()
    client = get_anthropic_client()
    company_name = state["company_name"]

    # Check if we're iterating with missing info
    missing_info = state.get("missing_info", [])

    # =========================================================================
    # Step 1: Initial search to detect company region
    # =========================================================================
    logger.debug("Running initial search to detect company region")

    tavily_client = get_tavily_client()

    # Quick initial search
    initial_query = f"{company_name} company"
    initial_response = tavily_client.search(query=initial_query, max_results=3)
    initial_results = initial_response.get("results", [])

    # Detect company region
    company_region = _detect_company_region(company_name, initial_results)
    logger.info(f"Detected company region: {company_region}")

    # =========================================================================
    # Step 2: Generate search queries (multilingual if needed)
    # =========================================================================
    logger.debug("Generating targeted queries")

    if missing_info:
        # Generate queries based on gaps
        num_queries = 5
        query_topics = []
        for info in missing_info[:5]:
            info_lower = info.lower()
            if "revenue" in info_lower or "financial" in info_lower:
                query_topics.append("revenue")
            elif "market" in info_lower:
                query_topics.append("market_share")
            elif "competitor" in info_lower:
                query_topics.append("competitors")
            elif "leader" in info_lower or "ceo" in info_lower:
                query_topics.append("leadership")
            else:
                query_topics.append("news")
    else:
        query_topics = ["revenue", "annual_report", "market_share", "competitors", "leadership", "news"]

    # Generate multilingual queries
    if ENHANCEMENTS_AVAILABLE and company_region != "united_states":
        queries = _generate_multilingual_queries(company_name, company_region, query_topics)
        logger.info(f"Generated {len(queries)} multilingual queries for {company_region}")
    else:
        # Use LLM to generate queries
        prompt = GENERATE_QUERIES_PROMPT.format(
            company_name=company_name,
            num_queries=5
        )

        if missing_info:
            query_context = f"""
Previous research had gaps. Focus queries on:
{chr(10).join(f'- {info}' for info in missing_info[:3])}
"""
            prompt += f"\n\n{query_context}"

        response = client.messages.create(
            model=config.llm_model,
            max_tokens=config.researcher_max_tokens,
            temperature=config.researcher_temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        fallback_queries = [
            f"{company_name} company overview",
            f"{company_name} revenue financial performance",
            f"{company_name} products services",
            f"{company_name} competitors market position",
            f"{company_name} recent news developments"
        ]

        queries = safe_extract_json(
            response,
            default=fallback_queries,
            agent_name="researcher"
        )

        if not isinstance(queries, list):
            queries = fallback_queries

    query_cost = 0.001  # Minimal cost for query generation

    logger.info(f"Generated {len(queries)} queries")
    for i, query in enumerate(queries[:5], 1):
        logger.debug(f"  Query {i}: {query}")

    # =========================================================================
    # Step 3: Execute searches via Tavily
    # =========================================================================
    logger.debug("Searching for sources via Tavily")

    all_results = list(initial_results)  # Include initial results
    sources = []

    # Add initial results to sources
    for result in initial_results:
        sources.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "score": result.get("score", 0.0)
        })

    # Execute remaining queries
    for query in queries:
        logger.debug(f"Executing search: {query}")
        try:
            search_response = tavily_client.search(
                query=query,
                max_results=3
            )

            for result in search_response.get("results", []):
                # Avoid duplicate URLs
                result_url = result.get("url", "")
                if not any(s.get("url") == result_url for s in sources):
                    all_results.append(result)
                    sources.append({
                        "title": result.get("title", ""),
                        "url": result_url,
                        "score": result.get("score", 0.0)
                    })
        except Exception as e:
            logger.warning(f"Search failed for query '{query}': {e}")

    # Calculate Tavily cost (approximate)
    search_cost = (len(queries) + 1) * 0.001

    logger.info(f"Found {len(all_results)} results from Tavily search")

    # =========================================================================
    # Step 4: Check data quality threshold
    # =========================================================================
    threshold_result = None
    retry_performed = False

    if ENHANCEMENTS_AVAILABLE and not missing_info:
        logger.debug("Checking data quality threshold")
        threshold_result = _check_data_threshold(all_results, company_name)

        if not threshold_result["passes_threshold"]:
            logger.warning(
                f"Data threshold not met (coverage: {threshold_result['coverage']:.1f}%). "
                f"Retry strategies: {threshold_result['retry_strategies']}"
            )

            # Try retry strategies
            retry_strategies = threshold_result["retry_strategies"]

            if "multilingual" in retry_strategies and company_region == "united_states":
                # Try Spanish queries for potentially LATAM company
                logger.info("Retrying with Spanish queries")
                spanish_queries = _generate_multilingual_queries(
                    company_name, "mexico", query_topics
                )[:5]

                for query in spanish_queries:
                    try:
                        search_response = tavily_client.search(query=query, max_results=2)
                        for result in search_response.get("results", []):
                            result_url = result.get("url", "")
                            if not any(s.get("url") == result_url for s in sources):
                                all_results.append(result)
                                sources.append({
                                    "title": result.get("title", ""),
                                    "url": result_url,
                                    "score": result.get("score", 0.0)
                                })
                    except Exception as e:
                        logger.warning(f"Retry search failed: {e}")

                retry_performed = True
                search_cost += len(spanish_queries) * 0.001

            if "parent_company" in retry_strategies:
                # Try parent company queries
                logger.info("Retrying with parent company queries")
                generator = create_multilingual_generator()
                parent_queries = generator.get_parent_company_queries(company_name)

                for query in parent_queries[:3]:
                    try:
                        search_response = tavily_client.search(query=query, max_results=2)
                        for result in search_response.get("results", []):
                            result_url = result.get("url", "")
                            if not any(s.get("url") == result_url for s in sources):
                                all_results.append(result)
                                sources.append({
                                    "title": result.get("title", ""),
                                    "url": result_url,
                                    "score": result.get("score", 0.0)
                                })
                    except Exception as e:
                        logger.warning(f"Parent company search failed: {e}")

                retry_performed = True
                search_cost += len(parent_queries) * 0.001

            # Re-check threshold after retries
            if retry_performed:
                threshold_result = _check_data_threshold(all_results, company_name)
                logger.info(
                    f"After retry: coverage {threshold_result['coverage']:.1f}%, "
                    f"passes: {threshold_result['passes_threshold']}"
                )

    # =========================================================================
    # Step 5: Domain Exploration - Find and crawl company websites
    # =========================================================================
    exploration_results = []
    company_domains = []

    if config.enable_domain_exploration and not missing_info:
        logger.debug("Identifying company domains for exploration")
        company_domains = _identify_company_domains(all_results, company_name)

        if company_domains:
            logger.info(f"Exploring {len(company_domains)} company domains")
            exploration_results = _explore_company_domains(company_domains, config)
            logger.info(f"Domain exploration added {len(exploration_results)} pages")

            # Add exploration results to all_results
            for exp_result in exploration_results:
                all_results.append(exp_result)
                sources.append({
                    "title": exp_result.get("title", ""),
                    "url": exp_result.get("url", ""),
                    "score": exp_result.get("score", 0.0),
                    "source": "domain_explorer"
                })

    logger.info(f"Total sources after exploration: {len(all_results)}")

    # =========================================================================
    # Step 6: Compile results
    # =========================================================================
    total_cost = query_cost + search_cost

    # Track agent output
    agent_output = {
        "queries_generated": len(queries),
        "queries": queries[:10],  # Limit for output
        "sources_found": len(sources),
        "tavily_results": len(all_results) - len(exploration_results),
        "exploration_results": len(exploration_results),
        "domains_explored": len(company_domains),
        "company_region": company_region,
        "multilingual_search": ENHANCEMENTS_AVAILABLE and company_region != "united_states",
        "retry_performed": retry_performed,
        "cost": total_cost,
    }

    # Add threshold data if available
    if threshold_result:
        agent_output["data_coverage"] = threshold_result["coverage"]
        agent_output["passes_threshold"] = threshold_result["passes_threshold"]
        agent_output["threshold_recommendations"] = threshold_result["recommendations"][:3]

    logger.info(f"Researcher agent complete - cost: ${total_cost:.4f}")

    # Return results
    return {
        "search_results": all_results,
        "sources": sources,
        "agent_outputs": {"researcher": agent_output},
        "total_cost": total_cost,
        "total_tokens": {"input": 0, "output": 0},
        # Pass region info for downstream agents
        "company_region": company_region,
    }
