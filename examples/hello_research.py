#!/usr/bin/env python3
"""
Phase 0: Hello World - Company Researcher Prototype

This is the simplest possible version to validate:
1. Can we call Claude API? ✓
2. Can we search web with Tavily? ✓
3. Can we get a summary of a company? ✓

Usage:
    python hello_research.py "Tesla"
    python hello_research.py "OpenAI"
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def hello_research(company_name: str) -> dict:
    """
    Phase 0 research: Simple search + summarization.

    Args:
        company_name: Name of company to research

    Returns:
        Dictionary with research results
    """

    print(f"\n{'='*60}")
    print(f"[RESEARCH] Researching: {company_name}")
    print(f"{'='*60}\n")

    # Import here to fail fast if dependencies missing
    try:
        from anthropic import Anthropic
        from tavily import TavilyClient
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install anthropic tavily-python python-dotenv")
        sys.exit(1)

    # Check API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not anthropic_key:
        print("[ERROR] Missing ANTHROPIC_API_KEY in .env file")
        print("\nGet your key at: https://console.anthropic.com/")
        sys.exit(1)

    if not tavily_key:
        print("[ERROR] Missing TAVILY_API_KEY in .env file")
        print("\nGet your key at: https://tavily.com/")
        sys.exit(1)

    # Initialize clients
    anthropic_client = Anthropic(api_key=anthropic_key)
    tavily_client = TavilyClient(api_key=tavily_key)

    start_time = datetime.now()

    # Step 1: Search the web
    print("[STEP 1] Searching the web...")

    search_queries = [
        f"{company_name} company overview",
        f"{company_name} revenue 2024",
        f"{company_name} products services"
    ]

    all_results = []
    for query in search_queries:
        print(f"  [SEARCH] Searching: {query}")
        results = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            max_results=3
        )
        all_results.append(results)

    # Collect sources
    sources = []
    search_content = []

    for result_set in all_results:
        for item in result_set.get("results", []):
            sources.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "score": item.get("score", 0)
            })
            search_content.append(f"Title: {item.get('title')}\nContent: {item.get('content')}\n")

    print(f"  [OK] Found {len(sources)} sources\n")

    # Step 2: Summarize with Claude
    print("[STEP 2] Analyzing with Claude...")

    combined_content = "\n---\n".join(search_content[:10])  # Limit to first 10 results

    prompt = f"""Analyze this information about {company_name} and provide a concise research summary.

Search Results:
{combined_content}

Please provide:
1. Company Overview (2-3 sentences)
2. Key Metrics (revenue, employees, founded, etc.)
3. Main Products/Services (bullet points)
4. Key Insights (2-3 most important facts)

Format as clean markdown."""

    response = anthropic_client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=2000,
        temperature=0.0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    summary = response.content[0].text

    # Calculate cost (approximate)
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    # Claude 3.5 Sonnet pricing (per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    total_cost = input_cost + output_cost

    # Add Tavily cost (approximate)
    tavily_cost = len(search_queries) * 0.001
    total_cost += tavily_cost

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Analysis complete\n")

    # Print results
    print(f"{'='*60}")
    print(f"[RESULTS] RESEARCH RESULTS")
    print(f"{'='*60}\n")
    print(summary)
    print(f"\n{'='*60}")
    print(f"[METRICS] METRICS")
    print(f"{'='*60}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Cost: ${total_cost:.4f}")
    print(f"Tokens: {input_tokens:,} in, {output_tokens:,} out")
    print(f"Sources: {len(sources)}")
    print(f"{'='*60}\n")

    # Print top sources
    print(f"{'='*60}")
    print(f"[SOURCES] TOP SOURCES")
    print(f"{'='*60}")
    for i, source in enumerate(sources[:5], 1):
        print(f"{i}. {source['title']}")
        print(f"   {source['url']}")
        print(f"   Relevance: {source['score']:.0%}\n")
    print(f"{'='*60}\n")

    # Success criteria check
    print(f"{'='*60}")
    print(f"[SUCCESS CHECK] SUCCESS CRITERIA CHECK")
    print(f"{'='*60}")

    checks = {
        "Duration < 5 minutes": duration < 300,
        "Cost < $0.50": total_cost < 0.50,
        "Found sources": len(sources) > 0,
        "Generated summary": len(summary) > 100
    }

    for criterion, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {criterion}")

    all_passed = all(checks.values())

    if all_passed:
        print(f"\n[SUCCESS] ALL CRITERIA PASSED! Phase 0 successful!")
    else:
        print(f"\n[WARNING] Some criteria failed. Review results above.")

    print(f"{'='*60}\n")

    return {
        "company_name": company_name,
        "summary": summary,
        "sources": sources,
        "metrics": {
            "duration_seconds": duration,
            "cost_usd": total_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "source_count": len(sources)
        },
        "success": all_passed
    }


def main():
    """Main entry point."""

    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python hello_research.py <company_name>")
        print("\nExamples:")
        print("  python hello_research.py Tesla")
        print("  python hello_research.py OpenAI")
        print("  python hello_research.py 'Stripe Inc'")
        sys.exit(1)

    company_name = " ".join(sys.argv[1:])

    # Run async research
    try:
        result = asyncio.run(hello_research(company_name))

        # Exit with success code
        sys.exit(0 if result["success"] else 1)

    except KeyboardInterrupt:
        print("\n\n[ERROR] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
