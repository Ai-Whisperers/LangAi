"""
Custom LangFlow Components for Company Researcher.

These components can be loaded into LangFlow to use your existing
research graph functionality in the visual builder.

To use:
1. Start LangFlow with: langflow run --components-path path/to/this/file.py
2. Components will appear in the sidebar under "Custom"
"""

import json

from langflow.custom import Component
from langflow.io import IntInput, MessageTextInput, Output, SecretStrInput
from langflow.schema import Data

from ..llm.client_factory import safe_extract_text


class CompanyQueryGenerator(Component):
    """Generate search queries for company research."""

    display_name = "Company Query Generator"
    description = "Generates targeted search queries for researching a company"
    icon = "search"
    name = "CompanyQueryGenerator"

    inputs = [
        MessageTextInput(
            name="company_name",
            display_name="Company Name",
            info="Name of the company to research",
            required=True,
        ),
        SecretStrInput(
            name="anthropic_api_key",
            display_name="Anthropic API Key",
            info="Your Anthropic API key",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Queries", name="queries", method="generate_queries"),
    ]

    def generate_queries(self) -> Data:
        """Generate search queries using Claude."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        company = self.company_name

        prompt = f"""Generate 5 specific search queries to research {company}.

The queries should find:
1. Company overview and basic information
2. Financial metrics (revenue, funding, valuation)
3. Products and services
4. Competitors and market position
5. Recent news and developments

Return ONLY a JSON array of strings:
["query 1", "query 2", "query 3", "query 4", "query 5"]"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        import re

        queries_text = safe_extract_text(response, agent_name="query_generator").strip()
        json_match = re.search(r"\[.*\]", queries_text, re.DOTALL)

        if json_match:
            queries = json.loads(json_match.group())
        else:
            queries = [
                f"{company} company overview",
                f"{company} revenue financials",
                f"{company} products services",
                f"{company} competitors",
                f"{company} recent news",
            ]

        return Data(data={"queries": queries, "company_name": company})


class TavilyWebSearch(Component):
    """Search the web using Tavily API."""

    display_name = "Tavily Web Search"
    description = "Search the web for company information using Tavily"
    icon = "globe"
    name = "TavilyWebSearch"

    inputs = [
        MessageTextInput(
            name="queries_input",
            display_name="Queries (JSON)",
            info="JSON array of search queries",
            required=True,
        ),
        SecretStrInput(
            name="tavily_api_key",
            display_name="Tavily API Key",
            info="Your Tavily API key",
            required=True,
        ),
        IntInput(
            name="max_results",
            display_name="Max Results Per Query",
            info="Maximum results per query",
            value=5,
        ),
    ]

    outputs = [
        Output(display_name="Search Results", name="results", method="search_web"),
    ]

    def search_web(self) -> Data:
        """Execute web searches."""
        from tavily import TavilyClient

        client = TavilyClient(api_key=self.tavily_api_key)

        # Parse queries
        try:
            queries = json.loads(self.queries_input)
        except:
            queries = [self.queries_input]

        all_results = []
        for query in queries:
            response = client.search(query=query, max_results=self.max_results)

            for result in response.get("results", []):
                all_results.append(
                    {
                        "query": query,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                    }
                )

        return Data(data={"search_results": all_results})


class CompanyDataExtractor(Component):
    """Extract structured company data from search results."""

    display_name = "Company Data Extractor"
    description = "Extract structured company information using Claude"
    icon = "file-text"
    name = "CompanyDataExtractor"

    inputs = [
        MessageTextInput(
            name="search_results",
            display_name="Search Results (JSON)",
            info="JSON array of search results",
            required=True,
        ),
        MessageTextInput(
            name="company_name",
            display_name="Company Name",
            info="Name of the company",
            required=True,
        ),
        SecretStrInput(
            name="anthropic_api_key",
            display_name="Anthropic API Key",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Extracted Data", name="data", method="extract_data"),
    ]

    def extract_data(self) -> Data:
        """Extract structured data using Claude."""
        import re

        import anthropic

        client = anthropic.Anthropic(api_key=self.anthropic_api_key)

        try:
            results = json.loads(self.search_results)
        except:
            results = []

        # Combine search results
        combined_content = "\n\n".join(
            [
                f"Source: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\n{r.get('content', '')[:500]}"
                for r in results[:10]
            ]
        )

        prompt = f"""Extract structured information about {self.company_name} from these search results.

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
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = safe_extract_text(response, agent_name="data_extractor").strip()
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

        if json_match:
            extracted = json.loads(json_match.group())
        else:
            extracted = {"error": "Could not parse JSON"}

        return Data(data={"extracted_data": extracted})


class CompanyReportGenerator(Component):
    """Generate a markdown report from extracted company data."""

    display_name = "Company Report Generator"
    description = "Generate a formatted markdown report"
    icon = "file-output"
    name = "CompanyReportGenerator"

    inputs = [
        MessageTextInput(
            name="extracted_data",
            display_name="Extracted Data (JSON)",
            info="JSON object with extracted company data",
            required=True,
        ),
        MessageTextInput(
            name="company_name",
            display_name="Company Name",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Report", name="report", method="generate_report"),
    ]

    def generate_report(self) -> str:
        """Generate markdown report."""
        try:
            data = json.loads(self.extracted_data)
        except:
            data = {}

        company_name = self.company_name

        def format_list(items, empty_msg):
            if not items:
                return f"{empty_msg}\n"
            return "".join(f"- {item}\n" for item in items)

        report = f"""# {data.get('name', company_name)}

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

{format_list(data.get('products', []), 'No products listed.')}

---

## Competitors

{format_list(data.get('competitors', []), 'No competitors listed.')}

---

## Key Facts

{format_list(data.get('key_facts', []), 'No key facts extracted.')}
"""

        return report


# Registry for LangFlow to discover components
COMPONENT_REGISTRY = {
    "CompanyQueryGenerator": CompanyQueryGenerator,
    "TavilyWebSearch": TavilyWebSearch,
    "CompanyDataExtractor": CompanyDataExtractor,
    "CompanyReportGenerator": CompanyReportGenerator,
}
