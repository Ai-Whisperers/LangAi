"""
Company Research LangGraph Workflow

Visualizes the complete company research process:
1. Generate search queries
2. Search web with Tavily
3. Extract company data
4. Generate markdown report
"""

import json
import logging
import re
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END
import operator

from ..llm.client_factory import get_tavily_client
from ..llm.smart_client import smart_completion
from ..config import get_config

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """State for company research workflow"""
    # Input
    company_name: str

    # Step 1: Query Generation
    queries: Annotated[List[str], operator.add]

    # Step 2: Search Results
    search_results: Annotated[List[Dict], operator.add]

    # Step 3: Extracted Data
    extracted_data: Dict

    # Step 4: Final Report
    report: str

    # Metadata
    total_cost: float
    total_tokens: int
    error: str | None


def node_generate_queries(state: ResearchState) -> dict:
    """
    Node 1: Generate search queries (cost-optimized)

    Takes company name and generates 5 targeted search queries.
    Uses smart_completion to route to cheapest model (DeepSeek V3 $0.14/1M).
    """
    company = state.get("company_name", "Unknown Company")

    logger.info(f"Generating queries for: {company}")

    try:
        prompt = f"""Generate 5 specific search queries to research {company}.

The queries should find:
1. Company overview and basic information
2. Financial metrics (revenue, funding, valuation)
3. Products and services
4. Competitors and market position
5. Recent news and developments

Return ONLY a JSON array of strings:
["query 1", "query 2", "query 3", "query 4", "query 5"]"""

        # Use smart_completion - routes to DeepSeek V3 for extraction
        result = smart_completion(
            prompt=prompt,
            task_type="extraction",  # Routes to DeepSeek V3 ($0.14/1M)
            max_tokens=512,
            temperature=0.0
        )

        # Parse queries using safe JSON parsing
        queries_text = result.content.strip()

        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', queries_text, re.DOTALL)
        if json_match:
            queries = json.loads(json_match.group())
        else:
            # Fallback if JSON extraction fails
            raise ValueError("Could not extract JSON array from response")

        logger.info(f"Generated {len(queries)} queries")

        return {
            "queries": queries,
            "total_tokens": result.input_tokens + result.output_tokens,
            "total_cost": result.cost
        }

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing error for queries: {e}")
        return {
            "queries": [
                f"{company} company overview",
                f"{company} revenue financials",
                f"{company} products services"
            ],
            "error": f"JSON parsing error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error generating queries: {e}", exc_info=True)
        return {
            "queries": [
                f"{company} company overview",
                f"{company} revenue financials",
                f"{company} products services"
            ],
            "error": str(e)
        }


def node_search_web(state: ResearchState) -> dict:
    """
    Node 2: Search web using Tavily

    Executes all generated queries in parallel and collects results.
    """
    queries = state.get("queries", [])
    config = get_config()

    logger.info(f"Searching web with {len(queries)} queries...")

    try:
        client = get_tavily_client()

        all_results = []
        for query in queries:
            logger.debug(f"Searching: {query[:50]}...")

            response = client.search(
                query=query,
                max_results=config.search_results_per_query
            )

            for result in response.get('results', []):
                all_results.append({
                    'query': query,
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })

        logger.info(f"Found {len(all_results)} search results")

        return {
            "search_results": all_results
        }

    except Exception as e:
        logger.error(f"Error searching web: {e}", exc_info=True)
        return {
            "search_results": [],
            "error": str(e)
        }


def node_extract_data(state: ResearchState) -> dict:
    """
    Node 3: Extract structured company data (cost-optimized)

    Uses smart_completion to extract structured information from search results.
    Routes to DeepSeek V3 ($0.14/1M) for extraction tasks.
    """
    results = state.get("search_results", [])
    company = state.get("company_name", "Unknown")

    logger.info(f"Extracting data from {len(results)} results...")

    try:
        # Combine top results
        combined_content = "\n\n".join([
            f"Source: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\n{r.get('content', '')[:500]}"
            for r in results[:10]
        ])

        prompt = f"""Extract structured information about {company} from these search results.

Search Results:
{combined_content[:5000]}

Return JSON with this structure:
{{
  "name": "Official company name",
  "industry": "Industry sector",
  "founded": "Year founded",
  "headquarters": "HQ location",
  "description": "One-sentence description",
  "revenue": "Latest revenue with year",
  "employees": "Number of employees",
  "products": ["Product 1", "Product 2"],
  "competitors": ["Competitor 1", "Competitor 2"],
  "key_facts": ["Fact 1", "Fact 2"]
}}

Return ONLY valid JSON."""

        # Use smart_completion - routes to DeepSeek V3 for extraction
        result = smart_completion(
            prompt=prompt,
            task_type="extraction",  # Routes to DeepSeek V3 ($0.14/1M)
            max_tokens=2048,
            temperature=0.0
        )

        # Parse JSON safely
        response_text = result.content.strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

        if json_match:
            extracted = json.loads(json_match.group())
        else:
            extracted = {"error": "Could not parse JSON"}

        logger.info(f"Extracted data for: {extracted.get('name', company)}")

        return {
            "extracted_data": extracted,
            "total_tokens": state.get("total_tokens", 0) + result.input_tokens + result.output_tokens,
            "total_cost": state.get("total_cost", 0) + result.cost
        }

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing error for extracted data: {e}")
        return {
            "extracted_data": {"error": f"JSON parsing error: {str(e)}"},
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error extracting data: {e}", exc_info=True)
        return {
            "extracted_data": {"error": str(e)},
            "error": str(e)
        }


def _format_list_section(items: List[Any], empty_message: str) -> str:
    """Format a list of items as markdown bullet points."""
    if not items:
        return f"{empty_message}\n"
    return "".join(f"- {item}\n" for item in items)


def _format_overview_section(data: Dict[str, Any], company_name: str) -> str:
    """Format the company overview section."""
    return f"""# {data.get('name', company_name)}

## Company Overview

**Industry:** {data.get('industry', 'Unknown')}
**Founded:** {data.get('founded', 'Unknown')}
**Headquarters:** {data.get('headquarters', 'Unknown')}

{data.get('description', 'No description available.')}

---

## Financial Metrics

- **Revenue:** {data.get('revenue', 'Unknown')}
- **Employees:** {data.get('employees', 'Unknown')}

---

## Products & Services

"""


def _format_sources_section(sources: List[Dict[str, Any]], sources_per_domain: int = 3) -> str:
    """Format the sources section, grouped by domain."""
    from urllib.parse import urlparse

    # Group sources by domain
    source_domains: Dict[str, List[Dict]] = {}
    for source in sources:
        url = source.get('url', '')
        if not url:
            continue
        try:
            domain = urlparse(url).netloc
            if domain not in source_domains:
                source_domains[domain] = []
            source_domains[domain].append(source)
        except (ValueError, KeyError) as e:
            logger.debug(f"Could not parse URL from source: {e}")

    # Format sources by domain
    section = ""
    for domain, domain_sources in source_domains.items():
        section += f"\n### {domain}\n\n"
        for source in domain_sources[:sources_per_domain]:
            title = source.get('title', 'Untitled')
            url = source.get('url', '#')
            section += f"- [{title}]({url})\n"

    section += f"\n---\n\nTotal Sources: {len(sources)}\n"
    return section


def node_generate_report(state: ResearchState) -> dict:
    """
    Node 4: Generate markdown report

    Creates a formatted markdown report from extracted data.
    """
    config = get_config()
    data = state.get("extracted_data", {})
    sources = state.get("search_results", [])
    company_name = state.get('company_name', 'Unknown Company')

    logger.info("Generating report...")

    # Build report from sections
    report = _format_overview_section(data, company_name)
    report += _format_list_section(data.get('products', []), "No products listed.")
    report += "\n---\n\n## Competitors\n\n"
    report += _format_list_section(data.get('competitors', []), "No competitors listed.")
    report += "\n---\n\n## Key Facts\n\n"
    report += _format_list_section(data.get('key_facts', []), "No key facts extracted.")
    report += "\n---\n\n## Sources\n\n"
    report += _format_sources_section(sources, config.report_sources_per_domain)

    logger.info(f"Report generated ({len(report)} characters)")

    return {
        "report": report
    }


# Build the workflow graph
workflow = StateGraph(ResearchState)

# Add all nodes
workflow.add_node("generate_queries", node_generate_queries)
workflow.add_node("search_web", node_search_web)
workflow.add_node("extract_data", node_extract_data)
workflow.add_node("generate_report", node_generate_report)

# Define the flow
workflow.add_edge(START, "generate_queries")
workflow.add_edge("generate_queries", "search_web")
workflow.add_edge("search_web", "extract_data")
workflow.add_edge("extract_data", "generate_report")
workflow.add_edge("generate_report", END)

# Compile the graph
graph = workflow.compile()


# Test function (for CLI testing)
if __name__ == "__main__":
    print("=" * 60)
    print("  Company Research Graph Test")
    print("=" * 60)

    result = graph.invoke({
        "company_name": "Tesla",
        "queries": [],
        "search_results": [],
        "extracted_data": {},
        "report": "",
        "total_cost": 0.0,
        "total_tokens": 0,
        "error": None
    })

    print("\n" + "=" * 60)
    print("  Research Complete!")
    print("=" * 60)
    print(f"\nCompany: {result['company_name']}")
    print(f"Queries Generated: {len(result.get('queries', []))}")
    print(f"Search Results: {len(result.get('search_results', []))}")
    print(f"Total Cost: ${result.get('total_cost', 0):.4f}")
    print(f"Total Tokens: {result.get('total_tokens', 0)}")

    if result.get('report'):
        print(f"\n✅ Report generated ({len(result['report'])} chars)")
        print("\nFirst 500 characters of report:")
        print("-" * 60)
        print(result['report'][:500])
        print("-" * 60)
