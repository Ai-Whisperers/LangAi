# Task: API Integration & Testing

**Phase:** 0
**Estimated Time:** 3 hours
**Dependencies:** 01-setup-environment.md
**Status:** [ ] Not Started

## Context

Before building the full research workflow, we need to understand how Claude and Tavily APIs work individually. This task creates simple test scripts to validate our API integrations and understand their behavior, costs, and limitations.

## Prerequisites

- [x] Task 1 complete (environment setup)
- [x] Anthropic API key working
- [x] Tavily API key working
- [x] Virtual environment activated

## Implementation Steps

### Step 1: Create Test File Structure

**Goal:** Organized test files for each API

**Actions:**
- [ ] Create test directory structure:

```bash
mkdir -p tests/api_tests
touch tests/api_tests/__init__.py
touch tests/api_tests/test_claude.py
touch tests/api_tests/test_tavily.py
touch tests/api_tests/test_integration.py
```

### Step 2: Test Claude API Basics

**Goal:** Understand Claude API behavior and costs

**Actions:**
- [ ] Create `tests/api_tests/test_claude.py`:

```python
"""Test Claude API integration"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import time

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def test_basic_completion():
    """Test basic Claude completion"""
    print("\n=== Test 1: Basic Completion ===")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Say hello in exactly 5 words"}
        ]
    )

    print(f"Response: {message.content[0].text}")
    print(f"Tokens used - Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens}")
    print(f"Estimated cost: ${(message.usage.input_tokens * 0.000003 + message.usage.output_tokens * 0.000015):.6f}")

    assert message.content[0].text
    print("✅ Basic completion works!")

def test_structured_output():
    """Test Claude with structured output request"""
    print("\n=== Test 2: Structured Output ===")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": """Extract company information from this text:

"Tesla, Inc. is an American electric vehicle and clean energy company founded in 2003.
The company is headquartered in Austin, Texas and had revenue of $96.7 billion in 2023."

Return as JSON with fields: name, industry, founded, headquarters, revenue"""
        }]
    )

    print(f"Response: {message.content[0].text}")
    print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

    # Check if response looks like JSON
    response_text = message.content[0].text
    assert "{" in response_text and "}" in response_text
    print("✅ Structured output works!")

def test_query_generation():
    """Test Claude generating search queries"""
    print("\n=== Test 3: Query Generation ===")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": """Generate 5 search queries to research Tesla company.

Return ONLY a Python list of strings, like:
["query 1", "query 2", ...]"""
        }]
    )

    print(f"Queries: {message.content[0].text}")
    print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

    # Check if response looks like a list
    response_text = message.content[0].text
    assert "[" in response_text and "]" in response_text
    print("✅ Query generation works!")

def test_cost_estimation():
    """Estimate cost for full research workflow"""
    print("\n=== Test 4: Cost Estimation ===")

    # Simulate a research workflow
    steps = [
        ("Generate queries", 100, 50),         # ~100 input, 50 output tokens
        ("Take notes (5x)", 500, 200),         # ~500 in, 200 out per search (x5)
        ("Extract data", 2000, 500),           # ~2000 in, 500 out
        ("Quality check", 500, 100),           # ~500 in, 100 out
        ("Generate report", 2000, 1000),       # ~2000 in, 1000 out
    ]

    total_input = 0
    total_output = 0

    for step, input_tokens, output_tokens in steps:
        total_input += input_tokens
        total_output += output_tokens
        step_cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)
        print(f"{step}: ~${step_cost:.4f}")

    total_cost = (total_input * 0.000003) + (total_output * 0.000015)
    print(f"\nTotal estimated cost: ${total_cost:.4f}")
    print(f"Total tokens: {total_input} input + {total_output} output = {total_input + total_output}")

    assert total_cost < 0.50, f"Cost ${total_cost:.4f} exceeds budget!"
    print("✅ Cost is within budget!")

if __name__ == "__main__":
    print("Testing Claude API Integration...")
    print("=" * 60)

    test_basic_completion()
    time.sleep(1)  # Rate limiting courtesy

    test_structured_output()
    time.sleep(1)

    test_query_generation()
    time.sleep(1)

    test_cost_estimation()

    print("\n" + "=" * 60)
    print("✅ All Claude API tests passed!")
```

- [ ] Run Claude tests:

```bash
python tests/api_tests/test_claude.py
```

**Expected Output:**
```
=== Test 1: Basic Completion ===
Response: Hello, how are you today?
Tokens used - Input: 15, Output: 6
Estimated cost: $0.000135
✅ Basic completion works!

...

✅ All Claude API tests passed!
```

**Verification:**
- [ ] All tests pass
- [ ] Estimated cost for full workflow < $0.40
- [ ] Response times < 5 seconds per call

### Step 3: Test Tavily Search API

**Goal:** Understand Tavily search quality and performance

**Actions:**
- [ ] Create `tests/api_tests/test_tavily.py`:

```python
"""Test Tavily API integration"""
import os
from dotenv import load_dotenv
from tavily import TavilyClient
import json
import time

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def test_basic_search():
    """Test basic search functionality"""
    print("\n=== Test 1: Basic Search ===")

    response = client.search(
        query="Tesla company overview",
        max_results=5
    )

    print(f"Query: {response['query']}")
    print(f"Results found: {len(response['results'])}")

    for i, result in enumerate(response['results'][:3], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Score: {result['score']}")
        print(f"   Content: {result['content'][:100]}...")

    assert len(response['results']) > 0
    print("\n✅ Basic search works!")

def test_company_search_quality():
    """Test search quality for company research"""
    print("\n=== Test 2: Company Search Quality ===")

    queries = [
        "Tesla revenue 2023",
        "Tesla competitors electric vehicles",
        "Tesla Elon Musk CEO",
        "Tesla stock price market cap",
        "Tesla autopilot technology"
    ]

    all_urls = []

    for query in queries:
        print(f"\nQuery: {query}")
        response = client.search(query=query, max_results=3)

        for result in response['results']:
            print(f"  - {result['title']} (score: {result['score']:.2f})")
            all_urls.append(result['url'])

        time.sleep(0.5)  # Rate limiting

    # Check for diverse sources
    unique_domains = len(set([url.split('/')[2] for url in all_urls]))
    print(f"\nUnique domains found: {unique_domains}")
    print(f"Total results: {len(all_urls)}")

    assert unique_domains >= 5, "Not enough diverse sources"
    print("✅ Search quality is good!")

def test_search_with_context():
    """Test Tavily's context/summarization feature"""
    print("\n=== Test 3: Search with Context ===")

    response = client.search(
        query="Tesla financial performance",
        max_results=5,
        include_answer=True  # Get AI-generated summary
    )

    print(f"Answer: {response.get('answer', 'No answer')[:200]}...")
    print(f"Results: {len(response['results'])}")

    assert response.get('answer'), "No summary generated"
    print("✅ Context generation works!")

def test_cost_calculation():
    """Calculate search costs for research workflow"""
    print("\n=== Test 4: Cost Calculation ===")

    # Typical research workflow
    searches_per_research = 15  # ~3 queries x 5 searches each
    cost_per_search = 0.001     # $0.001 per search

    total_search_cost = searches_per_research * cost_per_search

    print(f"Searches per research: {searches_per_research}")
    print(f"Cost per search: ${cost_per_search}")
    print(f"Total search cost: ${total_search_cost:.4f}")

    assert total_search_cost < 0.05, "Search cost too high"
    print("✅ Cost is reasonable!")

def test_rate_limits():
    """Test rate limit behavior"""
    print("\n=== Test 5: Rate Limits ===")

    start_time = time.time()

    # Make 10 quick searches
    for i in range(10):
        try:
            client.search(query=f"test query {i}", max_results=1)
        except Exception as e:
            print(f"Error on request {i}: {e}")
            break

    elapsed = time.time() - start_time
    print(f"10 searches took: {elapsed:.2f} seconds")
    print(f"Rate: {10/elapsed:.1f} searches/second")

    print("✅ No rate limiting issues!")

if __name__ == "__main__":
    print("Testing Tavily API Integration...")
    print("=" * 60)

    test_basic_search()
    time.sleep(1)

    test_company_search_quality()
    time.sleep(1)

    test_search_with_context()
    time.sleep(1)

    test_cost_calculation()

    test_rate_limits()

    print("\n" + "=" * 60)
    print("✅ All Tavily API tests passed!")
```

- [ ] Run Tavily tests:

```bash
python tests/api_tests/test_tavily.py
```

**Verification:**
- [ ] All tests pass
- [ ] Search results are relevant
- [ ] Cost per research < $0.02 for searches
- [ ] No rate limit errors

### Step 4: Test Combined Workflow

**Goal:** Test Claude + Tavily working together

**Actions:**
- [ ] Create `tests/api_tests/test_integration.py`:

```python
"""Test Claude + Tavily integration"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from tavily import TavilyClient
import json
import time

load_dotenv()

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def test_query_generation_and_search():
    """Test: Claude generates queries, Tavily searches"""
    print("\n=== Test: Query Generation → Search ===")

    company = "Tesla"

    # Step 1: Generate queries with Claude
    print(f"\n1. Asking Claude to generate search queries for {company}...")

    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"""Generate 3 search queries to research {company}.

Return ONLY a Python list of strings:
["query 1", "query 2", "query 3"]"""
        }]
    )

    # Parse queries (in production, use structured output)
    queries_text = message.content[0].text
    # Extract list from response
    import ast
    queries = ast.literal_eval(queries_text.strip())

    print(f"Generated queries: {queries}")

    # Step 2: Search with Tavily
    print(f"\n2. Searching with Tavily...")

    all_results = []
    for query in queries:
        response = tavily.search(query=query, max_results=3)
        all_results.extend(response['results'])
        print(f"  '{query}' → {len(response['results'])} results")
        time.sleep(0.5)

    print(f"\nTotal results collected: {len(all_results)}")

    assert len(queries) == 3
    assert len(all_results) > 0
    print("✅ Query generation + search works!")

def test_search_and_extraction():
    """Test: Tavily searches, Claude extracts data"""
    print("\n=== Test: Search → Data Extraction ===")

    # Step 1: Search
    print("\n1. Searching for Tesla...")

    response = tavily.search(
        query="Tesla company overview revenue employees",
        max_results=5
    )

    # Combine search results
    combined_content = "\n\n".join([
        f"Source: {r['title']}\n{r['content']}"
        for r in response['results']
    ])

    print(f"Collected {len(response['results'])} sources")

    # Step 2: Extract with Claude
    print("\n2. Extracting structured data with Claude...")

    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Extract company information from these search results:

{combined_content[:2000]}

Return JSON with fields:
- name: company name
- industry: industry sector
- revenue: latest revenue (with year)
- employees: number of employees
- description: 1-sentence description

Return ONLY valid JSON."""
        }]
    )

    extracted = message.content[0].text
    print(f"\nExtracted data:\n{extracted}")

    # Verify it's JSON-like
    assert "{" in extracted and "}" in extracted
    print("✅ Search + extraction works!")

def test_full_mini_workflow():
    """Test complete mini research workflow"""
    print("\n=== Test: Full Mini Workflow ===")

    company = "OpenAI"
    start_time = time.time()

    print(f"\n🔬 Researching: {company}")
    print("=" * 60)

    # Step 1: Generate queries
    print("\n📝 Step 1: Generating search queries...")
    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"Generate 2 search queries for {company}. Return as Python list."
        }]
    )
    import ast
    queries = ast.literal_eval(message.content[0].text.strip())
    print(f"Queries: {queries}")

    # Step 2: Search
    print("\n🔍 Step 2: Searching web...")
    results = []
    for q in queries:
        r = tavily.search(query=q, max_results=2)
        results.extend(r['results'])
        time.sleep(0.3)
    print(f"Found {len(results)} results")

    # Step 3: Extract
    print("\n📊 Step 3: Extracting data...")
    content = "\n".join([r['content'][:200] for r in results])
    message = claude.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"Extract key facts about {company} from:\n{content}\n\nReturn 3 bullet points."
        }]
    )
    facts = message.content[0].text
    print(f"\nFacts:\n{facts}")

    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")

    assert elapsed < 30, "Workflow too slow"
    print("✅ Full mini workflow works!")

if __name__ == "__main__":
    print("Testing Claude + Tavily Integration...")
    print("=" * 60)

    test_query_generation_and_search()
    time.sleep(2)

    test_search_and_extraction()
    time.sleep(2)

    test_full_mini_workflow()

    print("\n" + "=" * 60)
    print("✅ All integration tests passed!")
    print("\n📌 Key Learnings:")
    print("  • Claude generates good search queries")
    print("  • Tavily returns relevant results")
    print("  • Extraction from search results works")
    print("  • End-to-end flow is fast enough (<30s)")
    print("  • Ready to build full research script!")
```

- [ ] Run integration tests:

```bash
python tests/api_tests/test_integration.py
```

**Verification:**
- [ ] All integration tests pass
- [ ] Full workflow completes in < 30 seconds
- [ ] Extracted data looks reasonable
- [ ] No API errors

## Acceptance Criteria

- [ ] Claude API tests pass (4/4)
- [ ] Tavily API tests pass (5/5)
- [ ] Integration tests pass (3/3)
- [ ] Cost estimates within budget
- [ ] Response times acceptable
- [ ] No rate limit issues
- [ ] Documented API behavior and quirks

## Testing Instructions

Run all API tests:

```bash
# Test each API individually
python tests/api_tests/test_claude.py
python tests/api_tests/test_tavily.py

# Test integration
python tests/api_tests/test_integration.py

# All should pass! ✅
```

## Success Metrics

- **Claude Cost:** < $0.40 per research
- **Tavily Cost:** < $0.02 per research
- **Total Cost:** < $0.50 per research
- **Response Time:** < 5 seconds per API call
- **Success Rate:** 100% of test calls succeed

## Common Issues & Solutions

**Issue 1: "Rate limit exceeded"**
- **Solution:** Add `time.sleep(1)` between requests
- **Prevention:** Track request counts, respect API limits

**Issue 2: "Invalid JSON in Claude response"**
- **Solution:** Use better prompts, add examples
- **Future:** Use Claude's structured output feature

**Issue 3: "Tavily returns no results"**
- **Solution:** Reformulate query, try broader terms
- **Check:** Verify company name spelling

**Issue 4: "Costs higher than expected"**
- **Solution:** Reduce `max_tokens`, optimize prompts
- **Monitor:** Track actual token usage

## Next Steps

After completing this task:
1. Mark status as [x] Complete
2. Document actual costs and timings
3. Note any API quirks or limitations
4. Move to Task 3: [Hello Research Script](03-hello-research.md)

---

**Completed By:** TBD
**Time Spent:** TBD
**Issues Encountered:** TBD
**Key Learnings:** TBD
