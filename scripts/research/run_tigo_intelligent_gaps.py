#!/usr/bin/env python
"""
Intelligent Gap Filler Test - Tigo Paraguay

This script tests the AI-driven gap detection and filling system.
It uses AI to:
1. Analyze the existing research report and identify gaps
2. Generate targeted search queries dynamically
3. Execute searches and extract validated data

This is the solution to: "the targeted search queries should be generated
with AI with the discovery, not static hardcoded queries"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def main():
    print("\n" + "=" * 70)
    print("  INTELLIGENT GAP FILLER - AI-DRIVEN RESEARCH ENHANCEMENT")
    print("  Company: Tigo Paraguay")
    print("=" * 70)

    # Import the intelligent gap filler
    from src.company_researcher.research.intelligent_gap_filler import fill_research_gaps

    # Load existing research data
    output_dir = project_root / "outputs" / "tigo_paraguay"

    # Load the full report
    report_path = output_dir / "00_full_report.md"
    report_text = ""
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()
        print(f"[OK] Loaded report: {len(report_text)} chars")
    else:
        print("[WARN] No existing report found")

    # Load metrics/data if available
    metrics_path = output_dir / "metrics.json"
    research_data = {}
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            research_data = json.load(f)
        print(f"[OK] Loaded metrics: {research_data}")

    # Company context for better query generation
    company_context = {
        "company_name": "Tigo Paraguay",
        "legal_name": "Telefonica Celular del Paraguay S.A.E.",
        "parent_company": "Millicom International Cellular S.A.",
        "parent_ticker": "TIGO",
        "country": "Paraguay",
        "region": "Latin America",
        "industry": "Telecommunications",
        "regulator": "CONATEL",
        "competitors": ["Claro Paraguay", "Personal Paraguay"],
        "key_segments": ["Tigo Sports", "Tigo Money", "Tigo Business"],
        "year": datetime.now().year,
        "language_hints": ["Spanish", "Guarani region"],
    }

    print(f"\n[INFO] Company Context:")
    for key, value in company_context.items():
        print(f"  - {key}: {value}")

    print("\n" + "=" * 70)
    print("  STARTING AI-DRIVEN GAP ANALYSIS AND FILLING")
    print("=" * 70)

    # Run the intelligent gap filler
    # Using Tavily directly to avoid DuckDuckGo timeout issues
    result = fill_research_gaps(
        company_name="Tigo Paraguay",
        research_data=research_data,
        report_text=report_text,
        company_context=company_context,
        preferred_provider="tavily",  # Skip DuckDuckGo which is timing out
    )

    # Save results
    result_path = output_dir / "intelligent_gap_fill_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[OK] Saved results to: {result_path}")

    # Generate summary report
    print("\n" + "=" * 70)
    print("  GAP FILLING RESULTS SUMMARY")
    print("=" * 70)

    print(f"\nCompany: {result.get('company_name', 'N/A')}")
    print(f"Gaps Found: {result.get('gaps_found', 0)}")
    print(f"Gaps Filled: {result.get('gaps_filled', 0)}")
    print(f"High Confidence Fills: {result.get('high_confidence_fills', 0)}")

    filled_data = result.get("filled_data", {})
    if filled_data:
        print("\n--- FILLED DATA ---")
        for field, data in filled_data.items():
            print(f"\n{field}:")
            print(f"  Value: {data.get('value', 'N/A')}")
            print(f"  Source: {data.get('source', 'N/A')}")
            print(f"  Confidence: {data.get('confidence', 0):.0%}")
            print(f"  Category: {data.get('category', 'N/A')}")
            print(f"  Priority: {data.get('priority', 'N/A')}")

    unfilled = result.get("unfilled_gaps", [])
    if unfilled:
        print(f"\n--- UNFILLED GAPS ({len(unfilled)}) ---")
        for gap in unfilled[:5]:  # Show first 5
            print(
                f"\n{gap.get('field', 'N/A')} ({gap.get('category', 'N/A')}, {gap.get('priority', 'N/A')}):"
            )
            queries = gap.get("queries_tried", [])
            if queries:
                print(f"  Queries tried: {len(queries)}")
                for q in queries[:2]:
                    print(f"    - {q[:60]}...")

    # Generate markdown report
    report = f"""# Tigo Paraguay - Intelligent Gap Fill Results
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Method: AI-driven gap detection and targeted query generation*

---

## Summary

| Metric | Value |
|--------|-------|
| Gaps Identified | {result.get('gaps_found', 0)} |
| Gaps Successfully Filled | {result.get('gaps_filled', 0)} |
| High Confidence Fills | {result.get('high_confidence_fills', 0)} |
| Fill Rate | {result.get('gaps_filled', 0) / max(result.get('gaps_found', 1), 1) * 100:.1f}% |

---

## Filled Data Points

"""
    for field, data in filled_data.items():
        confidence_pct = data.get("confidence", 0) * 100
        report += f"""### {field}
- **Value:** {data.get('value', 'N/A')}
- **Source:** {data.get('source', 'N/A')}
- **Confidence:** {confidence_pct:.0f}%
- **Category:** {data.get('category', 'N/A')}
- **Priority:** {data.get('priority', 'N/A')}

"""

    if unfilled:
        report += """---

## Unfilled Gaps (Require Manual Research)

"""
        for gap in unfilled:
            report += f"""### {gap.get('field', 'N/A')}
- **Category:** {gap.get('category', 'N/A')}
- **Priority:** {gap.get('priority', 'N/A')}
- **Queries Attempted:** {len(gap.get('queries_tried', []))}

"""

    report += f"""---

## Methodology

This report was generated using the **Intelligent Gap Filler** system which:

1. **AI Gap Analysis**: Used AI to analyze the existing research report and identify specific missing data points
2. **Dynamic Query Generation**: Generated targeted search queries using AI based on the identified gaps and company context
3. **Multi-Provider Search**: Executed searches using premium search providers (Tavily)
4. **AI Data Extraction**: Used AI to extract and validate specific data points from search results

This approach addresses the limitation of static, hardcoded queries by dynamically generating queries based on what's actually missing from the research.

---

## Raw Results

```json
{json.dumps(result, indent=2, ensure_ascii=False, default=str)}
```
"""

    report_path = output_dir / "intelligent_gap_fill_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n[OK] Saved report to: {report_path}")

    print("\n" + "=" * 70)
    print("  INTELLIGENT GAP FILLING COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
