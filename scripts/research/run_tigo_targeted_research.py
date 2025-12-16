#!/usr/bin/env python
"""
Targeted Research for Tigo Paraguay - Fixing Known Gaps.

This script addresses specific research failures:
1. Leadership data extraction
2. Current year market data (2024)
3. Subscriber counts
4. Regulatory environment (CONATEL)
5. Business segments (Tigo Sports, Tigo Money)
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
    print("  TARGETED TIGO PARAGUAY RESEARCH")
    print("  Fixing Known Data Gaps")
    print("=" * 70)

    # Import required modules
    from src.company_researcher.integrations.search_router import get_search_router
    from src.company_researcher.llm.smart_client import SmartLLMClient

    router = get_search_router()
    llm = SmartLLMClient()

    # TARGETED QUERIES - Specific gaps to fill
    targeted_queries = {
        "leadership_2024": [
            "Roberto Laratro Tigo Paraguay CEO director general 2024",
            "Tigo Paraguay nuevo gerente general nombrado 2024",
            "Millicom Paraguay management team executives 2024",
            "Tigo Paraguay directivos equipo ejecutivo actual",
        ],
        "market_2024": [
            "Tigo Paraguay market share 2024 cuota mercado",
            "Paraguay telecommunications market share Q1 Q2 Q3 2024",
            "CONATEL Paraguay estadisticas telecomunicaciones 2024",
            "Tigo Personal Claro Paraguay participacion mercado 2024",
        ],
        "subscribers_2024": [
            "Tigo Paraguay suscriptores abonados 2024",
            "Tigo Paraguay lineas activas usuarios 2024",
            "Paraguay mobile subscribers by operator 2024",
            "Millicom Paraguay subscriber base 2024",
        ],
        "regulatory": [
            "CONATEL Paraguay Tigo licencia espectro",
            "Tigo Paraguay 5G licitacion espectro 2024",
            "CONATEL regulacion telecomunicaciones Paraguay 2024",
            "Tigo Paraguay frecuencias bandas asignadas",
        ],
        "business_segments": [
            "Tigo Sports Paraguay derechos transmision futbol",
            "Tigo Sports Paraguay ingresos revenue",
            "Tigo Money Paraguay usuarios transacciones 2024",
            "Tigo Business Paraguay corporativo empresas ingresos",
        ],
        "financial_2024": [
            "Tigo Paraguay ingresos revenue 2024",
            "Millicom Paraguay financial results Q1 Q2 Q3 2024",
            "Telefonica Celular Paraguay estados financieros",
            "Tigo Paraguay EBITDA margen 2024",
        ],
    }

    all_results = {}
    total_sources = 0

    for category, queries in targeted_queries.items():
        print(f"\n--- Searching: {category} ---")
        category_results = []

        for query in queries:
            try:
                response = router.search(
                    query=query, quality="premium", max_results=10, min_results=5
                )

                if response.success and response.results:
                    for r in response.results:
                        result_dict = r.to_dict()
                        result_dict["query"] = query
                        result_dict["category"] = category
                        category_results.append(result_dict)
                    print(
                        f"  [OK] '{query[:50]}...' -> {len(response.results)} results via {response.provider}"
                    )
                else:
                    print(f"  [WARN] '{query[:50]}...' -> No results")

            except Exception as e:
                print(f"  [ERR] '{query[:50]}...' -> {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for r in category_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        all_results[category] = unique_results
        total_sources += len(unique_results)
        print(f"  Total unique for {category}: {len(unique_results)}")

    print(f"\n--- Total Sources Collected: {total_sources} ---")

    # Now extract data from these results using LLM
    print("\n" + "=" * 70)
    print("  EXTRACTING STRUCTURED DATA")
    print("=" * 70)

    extracted_data = {}

    for category, results in all_results.items():
        if not results:
            continue

        print(f"\n--- Extracting: {category} ---")

        # Prepare context from search results
        context = ""
        for r in results[:15]:  # Limit to top 15
            context += f"\nSource: {r.get('url', 'N/A')}\n"
            context += f"Title: {r.get('title', 'N/A')}\n"
            content = r.get("content", r.get("snippet", ""))
            if content:
                context += f"Content: {content[:1000]}\n"
            context += "---\n"

        # Category-specific extraction prompts
        prompts = {
            "leadership_2024": """Extract leadership information for Tigo Paraguay from these sources.
Return JSON with:
{
  "ceo_name": "full name or null",
  "ceo_appointed_date": "date or null",
  "ceo_source_url": "url where found",
  "other_executives": [{"name": "", "title": "", "source_url": ""}],
  "confidence": "high/medium/low"
}
Only include information explicitly stated in the sources. Do not fabricate.""",
            "market_2024": """Extract market share data for Paraguay telecom market from these sources.
Return JSON with:
{
  "tigo_market_share": "percentage or null",
  "tigo_market_share_year": "year of data",
  "tigo_market_share_source": "url",
  "competitor_shares": {"Personal": "X%", "Claro": "Y%"},
  "total_market_value_usd": "amount or null",
  "data_date": "most recent date found",
  "confidence": "high/medium/low"
}
Only use 2023 or 2024 data. Flag if data is older.""",
            "subscribers_2024": """Extract subscriber/user count data for Tigo Paraguay from these sources.
Return JSON with:
{
  "mobile_subscribers": "number or null",
  "mobile_subscribers_date": "date of data",
  "broadband_subscribers": "number or null",
  "tv_subscribers": "number or null",
  "tigo_money_users": "number or null",
  "source_urls": ["list of urls"],
  "confidence": "high/medium/low"
}
Only include numbers explicitly stated. Do not estimate.""",
            "regulatory": """Extract regulatory information about Tigo Paraguay from these sources.
Return JSON with:
{
  "regulator": "CONATEL or other",
  "licenses_held": ["list of licenses/spectrum bands"],
  "5g_status": "description of 5G plans/timeline",
  "recent_regulatory_actions": ["list of recent actions"],
  "spectrum_holdings_mhz": "amount or null",
  "source_urls": ["list of urls"],
  "confidence": "high/medium/low"
}""",
            "business_segments": """Extract business segment information for Tigo Paraguay from these sources.
Return JSON with:
{
  "tigo_sports": {
    "description": "what it is",
    "broadcasting_rights": "what sports/leagues",
    "revenue_usd": "amount or null",
    "source_url": ""
  },
  "tigo_money": {
    "description": "mobile money service",
    "users": "number or null",
    "transaction_volume": "amount or null",
    "source_url": ""
  },
  "tigo_business": {
    "description": "B2B services",
    "revenue_contribution": "percentage or null",
    "source_url": ""
  },
  "confidence": "high/medium/low"
}""",
            "financial_2024": """Extract financial data for Tigo Paraguay from these sources.
Return JSON with:
{
  "revenue_usd": "amount or null",
  "revenue_year": "year of data",
  "revenue_growth_pct": "percentage or null",
  "ebitda_usd": "amount or null",
  "ebitda_margin_pct": "percentage or null",
  "capex_usd": "amount or null",
  "source_urls": ["list of urls"],
  "confidence": "high/medium/low"
}
Note: Distinguish between Tigo Paraguay specifically vs Millicom group totals.""",
        }

        if category not in prompts:
            continue

        prompt = prompts[category]
        full_prompt = f"""Analyze these search results about Tigo Paraguay:

{context}

{prompt}

IMPORTANT:
- Only extract information explicitly stated in the sources
- Include source URLs for every data point
- If information is not available, use null
- Set confidence based on source quality and recency"""

        try:
            result = llm.complete(
                prompt=full_prompt,
                system="You are a data extraction specialist. Extract only factual information with sources. Return valid JSON only.",
                task_type="extraction",
                max_tokens=2000,
                json_mode=True,
            )

            if result and result.get("content"):
                try:
                    extracted = json.loads(result["content"])
                    extracted_data[category] = extracted
                    print(f"  [OK] Extracted {category}")
                    print(f"  Provider: {result.get('provider', 'unknown')}")
                except json.JSONDecodeError:
                    print(f"  [WARN] Invalid JSON for {category}")
                    extracted_data[category] = {"raw": result["content"]}
            else:
                print(f"  [WARN] No extraction result for {category}")

        except Exception as e:
            print(f"  [ERR] Extraction failed for {category}: {e}")

    # Save extracted data
    output_dir = project_root / "outputs" / "tigo_paraguay"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw extracted data
    extracted_path = output_dir / "targeted_extraction.json"
    with open(extracted_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved extracted data to: {extracted_path}")

    # Generate gap-filled report section
    print("\n" + "=" * 70)
    print("  GENERATING GAP-FILLED REPORT")
    print("=" * 70)

    report = f"""# Tigo Paraguay - Targeted Research Update
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Purpose: Fill data gaps from comprehensive research*

---

## 1. Leadership (2024 Update)
"""

    leadership = extracted_data.get("leadership_2024", {})
    if leadership.get("ceo_name"):
        report += f"""
**CEO:** {leadership['ceo_name']}
- Appointed: {leadership.get('ceo_appointed_date', 'N/A')}
- Source: {leadership.get('ceo_source_url', 'N/A')}
"""
    else:
        report += "\n*CEO information not found in search results*\n"

    if leadership.get("other_executives"):
        report += "\n**Other Executives:**\n"
        for exec in leadership["other_executives"]:
            report += f"- {exec.get('name', 'N/A')} - {exec.get('title', 'N/A')}\n"

    report += f"""
## 2. Market Position (Current Data)
"""
    market = extracted_data.get("market_2024", {})
    if market.get("tigo_market_share"):
        report += f"""
**Tigo Paraguay Market Share:** {market['tigo_market_share']}
- Data Year: {market.get('tigo_market_share_year', 'N/A')}
- Source: {market.get('tigo_market_share_source', 'N/A')}

**Competitor Shares:**
"""
        for comp, share in market.get("competitor_shares", {}).items():
            report += f"- {comp}: {share}\n"
    else:
        report += "\n*Current market share data not found*\n"

    report += f"""
## 3. Subscriber Data
"""
    subs = extracted_data.get("subscribers_2024", {})
    if any([subs.get("mobile_subscribers"), subs.get("broadband_subscribers")]):
        report += f"""
- **Mobile Subscribers:** {subs.get('mobile_subscribers', 'N/A')} ({subs.get('mobile_subscribers_date', 'N/A')})
- **Broadband Subscribers:** {subs.get('broadband_subscribers', 'N/A')}
- **TV Subscribers:** {subs.get('tv_subscribers', 'N/A')}
- **Tigo Money Users:** {subs.get('tigo_money_users', 'N/A')}
"""
    else:
        report += "\n*Subscriber data not found in search results*\n"

    report += f"""
## 4. Regulatory Environment
"""
    reg = extracted_data.get("regulatory", {})
    if reg.get("regulator") or reg.get("5g_status"):
        report += f"""
**Regulator:** {reg.get('regulator', 'CONATEL')}
**5G Status:** {reg.get('5g_status', 'N/A')}
**Spectrum Holdings:** {reg.get('spectrum_holdings_mhz', 'N/A')} MHz

**Licenses:**
"""
        for lic in reg.get("licenses_held", []):
            report += f"- {lic}\n"
    else:
        report += "\n*Regulatory data not found*\n"

    report += f"""
## 5. Business Segments
"""
    segments = extracted_data.get("business_segments", {})

    tigo_sports = segments.get("tigo_sports", {})
    if tigo_sports:
        report += f"""
### Tigo Sports
- **Description:** {tigo_sports.get('description', 'N/A')}
- **Broadcasting Rights:** {tigo_sports.get('broadcasting_rights', 'N/A')}
- **Revenue:** {tigo_sports.get('revenue_usd', 'N/A')}
"""

    tigo_money = segments.get("tigo_money", {})
    if tigo_money:
        report += f"""
### Tigo Money
- **Description:** {tigo_money.get('description', 'N/A')}
- **Users:** {tigo_money.get('users', 'N/A')}
- **Transaction Volume:** {tigo_money.get('transaction_volume', 'N/A')}
"""

    report += f"""
## 6. Financial Data (2024)
"""
    fin = extracted_data.get("financial_2024", {})
    if fin.get("revenue_usd"):
        report += f"""
- **Revenue:** {fin['revenue_usd']} ({fin.get('revenue_year', 'N/A')})
- **Revenue Growth:** {fin.get('revenue_growth_pct', 'N/A')}
- **EBITDA:** {fin.get('ebitda_usd', 'N/A')}
- **EBITDA Margin:** {fin.get('ebitda_margin_pct', 'N/A')}
- **CapEx:** {fin.get('capex_usd', 'N/A')}
"""
    else:
        report += "\n*2024 financial data not found*\n"

    report += f"""
---

## Data Quality Assessment

| Category | Status | Confidence |
|----------|--------|------------|
| Leadership | {'Found' if leadership.get('ceo_name') else 'Missing'} | {leadership.get('confidence', 'N/A')} |
| Market Share | {'Found' if market.get('tigo_market_share') else 'Missing'} | {market.get('confidence', 'N/A')} |
| Subscribers | {'Found' if subs.get('mobile_subscribers') else 'Missing'} | {subs.get('confidence', 'N/A')} |
| Regulatory | {'Found' if reg.get('5g_status') else 'Missing'} | {reg.get('confidence', 'N/A')} |
| Business Segments | {'Found' if segments else 'Missing'} | {segments.get('confidence', 'N/A')} |
| Financials | {'Found' if fin.get('revenue_usd') else 'Missing'} | {fin.get('confidence', 'N/A')} |

---

## Raw Extraction Data

```json
{json.dumps(extracted_data, indent=2, ensure_ascii=False)}
```
"""

    report_path = output_dir / "targeted_gaps_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nSaved gap report to: {report_path}")
    print("\n" + "=" * 70)
    print("  TARGETED RESEARCH COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
