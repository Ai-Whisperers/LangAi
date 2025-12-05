# Task: Hello Research Script - Build Core Research Workflow

**Phase:** 0
**Estimated Time:** 4 hours
**Dependencies:** 01-setup-environment.md, 02-api-integration.md
**Status:** [ ] Not Started

## Context

This is the main deliverable of Phase 0: a working Python script that researches any company and generates a markdown report. We build the simplest possible version that demonstrates value - no LangGraph, no database, just straight Python code that proves the concept works.

## Prerequisites

- [x] Task 1 complete (environment setup)
- [x] Task 2 complete (API integration tested)
- [x] Understand how Claude and Tavily APIs work
- [x] Know approximate costs and timings

## Implementation Steps

### Step 1: Design the Workflow

**Goal:** Clear understanding of what the script does

**Workflow Design:**
```
1. INPUT: Company name (e.g., "Tesla")
   ↓
2. GENERATE QUERIES: Claude creates 5 search queries
   ↓
3. SEARCH WEB: Tavily executes searches (parallel)
   ↓
4. TAKE NOTES: Claude summarizes each search result
   ↓
5. EXTRACT DATA: Claude extracts structured information
   ↓
6. GENERATE REPORT: Create markdown file
   ↓
7. OUTPUT: Save to outputs/{company}/report.md
```

**Actions:**
- [ ] Sketch workflow on paper or in comments
- [ ] Identify inputs and outputs for each step
- [ ] Plan error handling points
- [ ] Estimate token usage per step

### Step 2: Create `hello_research.py` - Basic Structure

**Goal:** File structure with placeholder functions

**Actions:**
- [ ] Create `hello_research.py` in project root:

```python
#!/usr/bin/env python3
"""
Hello Research - Simple company research script

Usage:
    python hello_research.py "Tesla"
    python hello_research.py "OpenAI"
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from tavily import TavilyClient

# Load environment
load_dotenv()

# Initialize clients
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Configuration
MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 2048
NUM_QUERIES = 5
RESULTS_PER_QUERY = 3

def main():
    """Main research workflow"""
    if len(sys.argv) < 2:
        print("Usage: python hello_research.py 'Company Name'")
        sys.exit(1)

    company_name = sys.argv[1]
    print(f"\n🔬 Researching: {company_name}")
    print("=" * 60)

    start_time = time.time()

    # Step 1: Generate search queries
    print("\n📝 Step 1: Generating search queries...")
    queries = generate_queries(company_name)
    print(f"Generated {len(queries)} queries")

    # Step 2: Search web
    print("\n🔍 Step 2: Searching web...")
    search_results = search_web(queries)
    print(f"Found {len(search_results)} results")

    # Step 3: Take notes
    print("\n📝 Step 3: Analyzing results...")
    notes = take_notes(company_name, search_results)

    # Step 4: Extract structured data
    print("\n📊 Step 4: Extracting structured data...")
    company_data = extract_company_data(company_name, notes, search_results)

    # Step 5: Generate report
    print("\n📄 Step 5: Generating report...")
    report_path = generate_report(company_name, company_data, search_results)

    elapsed = time.time() - start_time
    print(f"\n✅ Research complete in {elapsed:.1f} seconds")
    print(f"📁 Report saved to: {report_path}")

def generate_queries(company_name: str) -> list[str]:
    """Generate search queries for company research"""
    # TODO: Implement
    pass

def search_web(queries: list[str]) -> list[dict]:
    """Search web with Tavily"""
    # TODO: Implement
    pass

def take_notes(company_name: str, search_results: list[dict]) -> str:
    """Summarize search results into research notes"""
    # TODO: Implement
    pass

def extract_company_data(company_name: str, notes: str, sources: list[dict]) -> dict:
    """Extract structured company data"""
    # TODO: Implement
    pass

def generate_report(company_name: str, data: dict, sources: list[dict]) -> str:
    """Generate markdown report"""
    # TODO: Implement
    pass

if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python hello_research.py "Tesla"  # Should show "TODO: Implement"
```

### Step 3: Implement Query Generation

**Goal:** Claude generates good search queries

**Actions:**
- [ ] Implement `generate_queries()`:

```python
def generate_queries(company_name: str) -> list[str]:
    """Generate search queries for company research"""

    prompt = f"""Generate 5 specific search queries to research {company_name}.

The queries should find:
1. Company overview and basic information
2. Financial metrics (revenue, funding, valuation)
3. Products and services
4. Competitors and market position
5. Recent news and developments

Return ONLY a Python list of strings, like:
["query 1", "query 2", "query 3", "query 4", "query 5"]

Be specific and actionable. Good query: "Tesla revenue 2023 annual report"
Bad query: "Tesla information"
"""

    message = claude.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    response_text = message.content[0].text.strip()

    # Extract list (handle various formats)
    import ast
    try:
        queries = ast.literal_eval(response_text)
        if not isinstance(queries, list):
            raise ValueError("Response is not a list")
    except:
        # Fallback: manual parsing
        import re
        queries = re.findall(r'"([^"]+)"', response_text)

    print(f"Queries generated:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")

    return queries[:NUM_QUERIES]  # Ensure we don't exceed limit
```

**Verification:**
```bash
python hello_research.py "Tesla"
# Should print 5 queries, then fail on next step (not implemented)
```

### Step 4: Implement Web Search

**Goal:** Parallel search execution with Tavily

**Actions:**
- [ ] Implement `search_web()`:

```python
def search_web(queries: list[str]) -> list[dict]:
    """Search web with Tavily (sequential for now)"""

    all_results = []

    for i, query in enumerate(queries, 1):
        print(f"  Searching: {query}")

        try:
            response = tavily.search(
                query=query,
                max_results=RESULTS_PER_QUERY
            )

            for result in response.get('results', []):
                all_results.append({
                    'query': query,
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"    ⚠️  Search failed: {e}")
            continue

    print(f"  Collected {len(all_results)} search results")
    return all_results
```

**Verification:**
```bash
python hello_research.py "Tesla"
# Should show searches happening, then fail on next step
```

### Step 5: Implement Note Taking

**Goal:** Summarize search results into cohesive notes

**Actions:**
- [ ] Implement `take_notes()`:

```python
def take_notes(company_name: str, search_results: list[dict]) -> str:
    """Summarize search results into research notes"""

    # Combine all search results
    combined_content = ""
    for result in search_results[:10]:  # Top 10 results
        combined_content += f"\n\nSource: {result['title']}\n"
        combined_content += f"URL: {result['url']}\n"
        combined_content += f"Content: {result['content'][:500]}\n"

    # Ask Claude to take notes
    prompt = f"""You are researching {company_name}. Read these search results and take comprehensive notes.

Search Results:
{combined_content[:5000]}  # Limit to ~5000 chars to save tokens

Focus on:
- Company basics (founded, HQ, industry)
- Financial information (revenue, funding, growth)
- Products and services
- Key people
- Competitors
- Recent news

Write clear, factual notes. Include specific numbers and dates.
"""

    message = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    notes = message.content[0].text

    # Save notes for debugging
    notes_dir = Path("outputs") / company_name.replace(" ", "_")
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "research_notes.txt").write_text(notes)

    print(f"  Saved notes to: {notes_dir}/research_notes.txt")

    return notes
```

### Step 6: Implement Data Extraction

**Goal:** Extract structured company information

**Actions:**
- [ ] Implement `extract_company_data()`:

```python
def extract_company_data(company_name: str, notes: str, sources: list[dict]) -> dict:
    """Extract structured company data from notes"""

    prompt = f"""Extract structured information about {company_name} from these research notes.

Research Notes:
{notes}

Extract the following fields. If information is not available, use "Unknown" or null:

Return JSON with this exact structure:
{{
  "name": "Official company name",
  "industry": "Industry sector",
  "founded": "Year founded",
  "headquarters": "HQ location",
  "description": "One-sentence description",
  "revenue": "Latest revenue with year (e.g., '$96.7B (2023)')",
  "employees": "Number of employees",
  "funding": "Total funding if private company",
  "valuation": "Valuation if available",
  "ceo": "CEO name",
  "products": ["Product 1", "Product 2", ...],
  "competitors": ["Competitor 1", "Competitor 2", ...],
  "key_facts": ["Fact 1", "Fact 2", ...]
}}

Return ONLY valid JSON, no other text.
"""

    message = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON
    response_text = message.content[0].text.strip()

    # Extract JSON from response (might have ```json wrapper)
    import re
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        company_data = json.loads(json_str)
    else:
        raise ValueError("Could not parse JSON from response")

    # Add metadata
    company_data['research_date'] = datetime.now().isoformat()
    company_data['sources_count'] = len(sources)

    # Save JSON for debugging
    data_dir = Path("outputs") / company_name.replace(" ", "_")
    (data_dir / "company_data.json").write_text(
        json.dumps(company_data, indent=2)
    )

    return company_data
```

### Step 7: Implement Report Generation

**Goal:** Beautiful markdown report

**Actions:**
- [ ] Implement `generate_report()`:

```python
def generate_report(company_name: str, data: dict, sources: list[dict]) -> str:
    """Generate markdown report"""

    report = f"""# {data.get('name', company_name)} - Research Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Company Overview

**Industry:** {data.get('industry', 'Unknown')}
**Founded:** {data.get('founded', 'Unknown')}
**Headquarters:** {data.get('headquarters', 'Unknown')}
**CEO:** {data.get('ceo', 'Unknown')}

{data.get('description', 'No description available.')}

---

## Financial Metrics

- **Revenue:** {data.get('revenue', 'Unknown')}
- **Employees:** {data.get('employees', 'Unknown')}
- **Funding:** {data.get('funding', 'N/A for public companies')}
- **Valuation:** {data.get('valuation', 'Unknown')}

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
        domain = urlparse(source['url']).netloc
        if domain not in source_domains:
            source_domains[domain] = []
        source_domains[domain].append(source)

    for domain, domain_sources in source_domains.items():
        report += f"\n### {domain}\n\n"
        for source in domain_sources[:3]:  # Top 3 per domain
            report += f"- [{source['title']}]({source['url']})\n"

    report += "\n---\n\n"
    report += f"**Total Sources:** {len(sources)}\n"
    report += f"**Research Date:** {data.get('research_date')}\n"

    # Save report
    output_dir = Path("outputs") / company_name.replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.md"
    report_path.write_text(report)

    return str(report_path)
```

**Verification:**
```bash
python hello_research.py "Tesla"
# Should complete fully and generate report
```

### Step 8: Add Error Handling and Polish

**Goal:** Robust script with good UX

**Actions:**
- [ ] Add try/except around main():

```python
def main():
    """Main research workflow"""
    try:
        # ... existing code ...

    except KeyboardInterrupt:
        print("\n\n⚠️  Research interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Research failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

- [ ] Add token/cost tracking:

```python
# At top of file
total_tokens_in = 0
total_tokens_out = 0

# After each Claude call
total_tokens_in += message.usage.input_tokens
total_tokens_out += message.usage.output_tokens

# At end of main()
total_cost = (total_tokens_in * 0.000003) + (total_tokens_out * 0.000015)
print(f"\n💰 Cost Breakdown:")
print(f"  Tokens: {total_tokens_in} in, {total_tokens_out} out")
print(f"  Total: ${total_cost:.4f}")
```

- [ ] Add progress indicators with better formatting

**Verification:**
```bash
python hello_research.py "Tesla"
# Should show nice progress, complete successfully, show cost
```

## Acceptance Criteria

- [ ] `hello_research.py` exists and runs
- [ ] Takes company name as argument
- [ ] Generates 5 search queries with Claude
- [ ] Searches web with Tavily (15 total searches)
- [ ] Takes research notes with Claude
- [ ] Extracts structured data
- [ ] Generates markdown report
- [ ] Saves to `outputs/{company}/report.md`
- [ ] Completes in < 5 minutes
- [ ] Costs < $0.50
- [ ] Includes error handling
- [ ] Shows cost breakdown
- [ ] Report is readable and useful

## Testing Instructions

Test with multiple companies:

```bash
# 1. Test with Tesla (well-known public company)
python hello_research.py "Tesla"

# 2. Test with OpenAI (private company)
python hello_research.py "OpenAI"

# 3. Test with smaller company
python hello_research.py "Anthropic"

# Verify:
# - All complete successfully
# - Reports are in outputs/{company}/report.md
# - Reports contain good information
# - Costs are < $0.50 each
# - Time is < 5 minutes each
```

## Success Metrics

- **Time per research:** < 5 minutes (target: 2-3 min)
- **Cost per research:** < $0.50 (target: $0.25-$0.35)
- **Report quality:** 80%+ usable information
- **Success rate:** 100% (no crashes)
- **Code complexity:** < 300 lines total

## Common Issues & Solutions

**Issue 1: JSON parsing fails**
- **Solution:** Better regex extraction, handle markdown code blocks
- **Fallback:** Manual parsing of Claude output

**Issue 2: No results from Tavily**
- **Solution:** Broaden search queries, try alternative phrasings
- **Check:** Company name spelling, alternative names

**Issue 3: Report is incomplete**
- **Solution:** Iterate on prompts, add more search queries
- **Check:** Notes file - did we get good search results?

**Issue 4: Costs too high**
- **Solution:** Reduce MAX_TOKENS, limit context length
- **Optimize:** Fewer searches, better prompts

## Next Steps

After completing this task:
1. Mark status as [x] Complete
2. Test with 5+ companies
3. Document actual performance metrics
4. Move to Task 4: [Validation & Testing](04-validation.md)
5. Commit working code:

```bash
git add hello_research.py outputs/
git commit -m "feat(phase-0): implement hello_research.py - working company research script"
```

---

**Completed By:** TBD
**Time Spent:** TBD
**Issues Encountered:** TBD
**Actual Performance:**
- Time: TBD
- Cost: TBD
- Quality: TBD
