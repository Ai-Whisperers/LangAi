"""
Company Research LangGraph Workflow

Visualizes the complete company research process:
1. Generate search queries
2. Search web with Tavily
3. Extract company data
4. Generate markdown report
"""

import os
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END
import operator


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
    Node 1: Generate search queries using Claude

    Takes company name and generates 5 targeted search queries
    to find comprehensive information about the company.
    """
    company = state.get("company_name", "Unknown Company")

    # In Studio, you'll see this step execute
    print(f"📝 Generating queries for: {company}")

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        prompt = f"""Generate 5 specific search queries to research {company}.

The queries should find:
1. Company overview and basic information
2. Financial metrics (revenue, funding, valuation)
3. Products and services
4. Competitors and market position
5. Recent news and developments

Return ONLY a Python list of strings:
["query 1", "query 2", "query 3", "query 4", "query 5"]"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse queries
        import ast
        queries_text = response.content[0].text.strip()
        queries = ast.literal_eval(queries_text)

        print(f"✅ Generated {len(queries)} queries")

        return {
            "queries": queries,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "total_cost": (response.usage.input_tokens * 0.000003) + (response.usage.output_tokens * 0.000015)
        }

    except Exception as e:
        print(f"❌ Error generating queries: {e}")
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
    print(f"🔍 Searching web with {len(queries)} queries...")

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        all_results = []
        for query in queries:
            print(f"  Searching: {query[:50]}...")

            response = client.search(
                query=query,
                max_results=3
            )

            for result in response.get('results', []):
                all_results.append({
                    'query': query,
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })

        print(f"✅ Found {len(all_results)} search results")

        return {
            "search_results": all_results
        }

    except Exception as e:
        print(f"❌ Error searching web: {e}")
        return {
            "search_results": [],
            "error": str(e)
        }


def node_extract_data(state: ResearchState) -> dict:
    """
    Node 3: Extract structured company data

    Uses Claude to extract structured information from search results.
    """
    results = state.get("search_results", [])
    company = state.get("company_name", "Unknown")

    print(f"📊 Extracting data from {len(results)} results...")

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Combine top results
        combined_content = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['url']}\n{r['content'][:500]}"
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

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON
        import json
        import re

        response_text = response.content[0].text.strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

        if json_match:
            extracted = json.loads(json_match.group())
        else:
            extracted = {"error": "Could not parse JSON"}

        print(f"✅ Extracted data for: {extracted.get('name', company)}")

        return {
            "extracted_data": extracted,
            "total_tokens": state.get("total_tokens", 0) + response.usage.input_tokens + response.usage.output_tokens,
            "total_cost": state.get("total_cost", 0) + (response.usage.input_tokens * 0.000003) + (response.usage.output_tokens * 0.000015)
        }

    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        return {
            "extracted_data": {"error": str(e)},
            "error": str(e)
        }


def node_generate_report(state: ResearchState) -> dict:
    """
    Node 4: Generate markdown report

    Creates a formatted markdown report from extracted data.
    """
    data = state.get("extracted_data", {})
    sources = state.get("search_results", [])

    print(f"📄 Generating report...")

    report = f"""# {data.get('name', state.get('company_name', 'Unknown Company'))}

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

    products = data.get('products', [])
    if products:
        for product in products:
            report += f"- {product}\n"
    else:
        report += "No products listed.\n"

    report += "\n---\n\n## Competitors\n\n"

    competitors = data.get('competitors', [])
    if competitors:
        for comp in competitors:
            report += f"- {comp}\n"
    else:
        report += "No competitors listed.\n"

    report += "\n---\n\n## Key Facts\n\n"

    facts = data.get('key_facts', [])
    if facts:
        for fact in facts:
            report += f"- {fact}\n"
    else:
        report += "No key facts extracted.\n"

    report += "\n---\n\n## Sources\n\n"

    # Group sources by domain
    from urllib.parse import urlparse
    source_domains = {}
    for source in sources:
        try:
            domain = urlparse(source['url']).netloc
            if domain not in source_domains:
                source_domains[domain] = []
            source_domains[domain].append(source)
        except:
            pass

    for domain, domain_sources in source_domains.items():
        report += f"\n### {domain}\n\n"
        for source in domain_sources[:3]:
            report += f"- [{source['title']}]({source['url']})\n"

    report += f"\n---\n\nTotal Sources: {len(sources)}\n"

    print(f"✅ Report generated ({len(report)} characters)")

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
