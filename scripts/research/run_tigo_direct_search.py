#!/usr/bin/env python
"""Direct search using Tavily for Tigo Paraguay gaps."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\n" + "=" * 70)
    print("  DIRECT TAVILY SEARCH - Tigo Paraguay")
    print("=" * 70)

    tavily_key = os.getenv('TAVILY_API_KEY')
    if not tavily_key:
        print("ERROR: TAVILY_API_KEY not set")
        return 1

    from tavily import TavilyClient
    tavily = TavilyClient(api_key=tavily_key)

    # Targeted queries for known gaps
    queries = [
        # Leadership - this is the key gap
        "Roberto Laratro Tigo Paraguay CEO director general 2024",
        "Tigo Paraguay gerente general nombrado mayo 2024",

        # Market share current
        "Tigo Paraguay participacion mercado 2024 CONATEL",
        "Paraguay telecomunicaciones cuota mercado operadores 2024",

        # Subscribers
        "Tigo Paraguay cantidad suscriptores lineas 2024",
        "Millicom Paraguay subscriber base Q3 2024",

        # Regulatory
        "CONATEL Paraguay Tigo 5G licitacion espectro",
        "Tigo Paraguay licencias frecuencias asignadas",

        # Business segments
        "Tigo Sports Paraguay derechos futbol liga",
        "Tigo Money Paraguay usuarios billetera digital",

        # Financial
        "Tigo Paraguay ingresos revenue 2024 Millicom",
    ]

    all_results = []

    for query in queries:
        print(f"\nSearching: {query[:60]}...")
        try:
            response = tavily.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_raw_content=False
            )

            results = response.get('results', [])
            print(f"  Found {len(results)} results")

            for r in results:
                all_results.append({
                    'query': query,
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'content': r.get('content', '')[:500]
                })

        except Exception as e:
            print(f"  Error: {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r['url'] not in seen_urls:
            seen_urls.add(r['url'])
            unique_results.append(r)

    print(f"\n--- Total unique results: {len(unique_results)} ---")

    # Extract key information using LLM
    print("\n" + "=" * 70)
    print("  EXTRACTING KEY INFORMATION")
    print("=" * 70)

    from src.company_researcher.llm.smart_client import SmartLLMClient
    llm = SmartLLMClient()

    # Prepare context
    context = "\n\n".join([
        f"Source: {r['url']}\nTitle: {r['title']}\nContent: {r['content']}"
        for r in unique_results
    ])

    extraction_prompt = f"""Analyze these search results about Tigo Paraguay and extract the following information.
ONLY include information explicitly stated in the sources with the source URL.
If information is not found, say "NOT FOUND".

SEARCH RESULTS:
{context}

EXTRACT THE FOLLOWING (with source URLs):

1. CEO/Director General:
   - Name:
   - Appointment Date:
   - Source URL:

2. Market Share (2024 data preferred):
   - Tigo Paraguay %:
   - Data Date:
   - Source URL:

3. Subscriber Count:
   - Mobile subscribers:
   - Data Date:
   - Source URL:

4. Regulatory/5G:
   - 5G Status:
   - CONATEL actions:
   - Source URL:

5. Business Segments:
   - Tigo Sports details:
   - Tigo Money users:
   - Source URLs:

6. Financial (2024):
   - Revenue:
   - Source URL:

IMPORTANT: Do not fabricate any information. Only include what is explicitly stated in the sources."""

    try:
        result = llm.complete(
            prompt=extraction_prompt,
            system="You are a precise data extraction specialist. Extract only information explicitly stated in sources.",
            task_type="extraction",
            max_tokens=2000
        )

        # Handle CompletionResult dataclass
        if result:
            extraction = result.content if hasattr(result, 'content') else result.get('content', '')
            provider = result.provider if hasattr(result, 'provider') else result.get('provider', 'unknown')
            print(f"\nProvider: {provider}")
            print("\n" + "-" * 70)
            print("EXTRACTED DATA:")
            print("-" * 70)
            print(extraction)

            # Save results
            output_dir = project_root / "outputs" / "tigo_paraguay"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save search results
            with open(output_dir / "direct_search_results.json", 'w', encoding='utf-8') as f:
                json.dump(unique_results, f, indent=2, ensure_ascii=False)

            # Save extraction
            with open(output_dir / "direct_extraction.md", 'w', encoding='utf-8') as f:
                f.write(f"# Tigo Paraguay - Direct Search Extraction\n")
                f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(f"## Sources Searched: {len(unique_results)}\n\n")
                f.write("## Extracted Information\n\n")
                f.write(extraction)
                f.write(f"\n\n## All Sources\n\n")
                for i, r in enumerate(unique_results, 1):
                    f.write(f"{i}. [{r['title']}]({r['url']})\n")

            print(f"\nResults saved to: {output_dir}")

    except Exception as e:
        print(f"Extraction error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("  SEARCH COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
