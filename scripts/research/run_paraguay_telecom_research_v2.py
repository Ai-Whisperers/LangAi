#!/usr/bin/env python
"""
Paraguay Telecom Research V2 - Using Smart Search Router
=========================================================

Research Tigo Paraguay and Personal Paraguay with:
- 200+ sources per company
- 90% quality target
- Multi-provider search (DuckDuckGo FREE fallback)

Uses the search_router for automatic fallback when APIs hit limits.

Usage:
    python run_paraguay_telecom_research_v2.py
"""

import os
import sys
import json
import yaml
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()


def load_company_profile(profile_path: str) -> Dict[str, Any]:
    """Load company profile from YAML file."""
    with open(profile_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_comprehensive_queries(company_data: Dict[str, Any]) -> List[str]:
    """Generate comprehensive search queries from profile."""
    queries = []

    company = company_data.get('company', {})
    research = company_data.get('research', {})
    competitors = company_data.get('competitors', [])

    company_name = company.get('name', '')
    legal_name = company.get('legal_name', '')
    parent_company = company.get('details', {}).get('parent_company', '')
    country = company.get('country', '')
    website = company.get('website', '')
    sectors = company.get('sectors', [])
    services = company.get('services', [])

    # 1. Priority queries from profile
    priority_queries = research.get('priority_queries', [])
    queries.extend(priority_queries)

    # 2. Company overview queries (Spanish + English)
    queries.extend([
        f"{company_name} empresa información general",
        f"{company_name} company overview profile",
        f"{company_name} historia fundación",
        f"{company_name} history founded",
        f"{company_name} sede oficinas",
        f"{company_name} headquarters locations",
    ])

    # 3. Financial queries
    queries.extend([
        f"{company_name} ingresos revenue 2024",
        f"{company_name} ingresos revenue 2023",
        f"{company_name} financial results earnings",
        f"{company_name} resultados financieros",
        f"{company_name} annual report informe anual",
        f"{company_name} EBITDA profit margins",
        f"{company_name} inversiones investments",
    ])

    # 4. Market position queries
    queries.extend([
        f"{company_name} market share {country}",
        f"{company_name} participación de mercado",
        f"{company_name} position ranking {country}",
        f"{company_name} subscribers usuarios abonados",
        f"{company_name} customer base clientes",
        f"telecommunications {country} market analysis 2024",
        f"telecomunicaciones {country} estadísticas",
    ])

    # 5. Network/infrastructure queries
    queries.extend([
        f"{company_name} network coverage cobertura",
        f"{company_name} 4G LTE red",
        f"{company_name} 5G rollout plan",
        f"{company_name} fiber optic fibra óptica",
        f"{company_name} infrastructure investments",
    ])

    # 6. Competitive queries
    for competitor in competitors:
        comp_name = competitor.get('name', competitor) if isinstance(competitor, dict) else competitor
        queries.append(f"{company_name} vs {comp_name} comparison")
        queries.append(f"{company_name} {comp_name} competencia mercado")

    # 7. Parent company queries
    if parent_company:
        queries.extend([
            f"{parent_company} {country} operations",
            f"{parent_company} annual report {country} segment",
            f"{parent_company} {company_name} financial results",
            f"{parent_company} strategy {country}",
        ])

    # 8. Legal name queries
    if legal_name and legal_name != company_name:
        queries.extend([
            f"{legal_name} financial results",
            f"{legal_name} annual report",
            f'"{legal_name}" company',
        ])

    # 9. Services/products queries
    for service in services[:5]:  # Top 5 services
        queries.append(f"{company_name} {service}")

    # 10. Sector queries
    for sector in sectors[:3]:  # Top 3 sectors
        queries.append(f"{company_name} {sector} market")

    # 11. News queries
    queries.extend([
        f"{company_name} news noticias 2024",
        f"{company_name} latest news recent",
        f"{company_name} announcements press releases",
    ])

    # 12. Leadership queries
    queries.extend([
        f"{company_name} CEO director general",
        f"{company_name} management team executives",
        f"{company_name} board directors",
    ])

    # 13. Regulatory queries
    queries.extend([
        f"CONATEL {country} telecommunications statistics",
        f"{country} telecommunications regulator report",
        f"{company_name} regulatory compliance",
    ])

    # 14. Industry reports
    queries.extend([
        f"GSMA {country} mobile market report",
        f"telecommunications {country} industry analysis",
        f"mobile operators {country} market 2024",
    ])

    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        q_lower = q.lower().strip()
        if q_lower not in seen and len(q_lower) > 10:
            seen.add(q_lower)
            unique_queries.append(q)

    return unique_queries


def search_with_router(queries: List[str], max_results_per_query: int = 10) -> List[Dict]:
    """
    Execute searches using the smart search router with fallback support.

    Uses: DuckDuckGo (FREE) -> Serper ($0.001) -> Tavily ($0.005)
    """
    from src.company_researcher.integrations.search_router import get_search_router

    router = get_search_router()
    all_results = []

    logger.info(f"Starting search with {len(queries)} queries...")
    logger.info(f"Available providers: {router._get_available_providers()}")

    for i, query in enumerate(queries):
        try:
            # Use standard tier which tries Serper first, then DuckDuckGo
            # This provides fallback when paid APIs are exhausted
            response = router.search(
                query=query,
                quality="standard",  # Will fallback to free if needed
                max_results=max_results_per_query,
                use_cache=True
            )

            if response.success:
                for result in response.results:
                    all_results.append({
                        'query': query,
                        'title': result.title,
                        'url': result.url,
                        'content': result.snippet,
                        'source': response.provider,
                        'score': result.score
                    })

                logger.info(f"[{i+1}/{len(queries)}] {response.provider}: {len(response.results)} results for: {query[:50]}...")
            else:
                logger.warning(f"[{i+1}/{len(queries)}] Failed: {response.error}")

            # Small delay to avoid rate limits
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error searching '{query[:50]}...': {e}")

    # Get stats
    stats = router.get_stats()
    logger.info(f"\nSearch complete. Stats: {json.dumps(stats, indent=2)}")

    return all_results


def deduplicate_sources(sources: List[Dict]) -> List[Dict]:
    """Remove duplicate sources by URL."""
    seen_urls = set()
    unique = []

    for source in sources:
        url = source.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(source)

    return unique


def extract_data_from_sources(company_name: str, sources: List[Dict]) -> Dict[str, Any]:
    """Extract structured data from sources using LLM."""
    from src.company_researcher.llm.smart_client import smart_completion

    # Format sources for extraction
    sources_text = ""
    for i, source in enumerate(sources[:50]):  # Limit to 50 sources for context
        sources_text += f"\n[{i+1}] {source.get('title', 'N/A')}\n"
        sources_text += f"URL: {source.get('url', 'N/A')}\n"
        sources_text += f"Content: {source.get('content', 'N/A')[:500]}\n"
        sources_text += "-" * 40

    prompt = f"""Extract key information about {company_name} from these sources:

{sources_text}

Extract and organize:
1. Company Overview (founding, headquarters, employees)
2. Financial Metrics (revenue, profit, growth)
3. Market Position (market share, ranking, subscribers)
4. Products/Services (main offerings)
5. Competitors (main competitors)
6. Recent News (key developments)
7. Leadership (CEO, key executives)
8. Strategic Initiatives (expansion, investments)

Return as JSON with these sections. Use "unknown" if information not found.
"""

    try:
        result = smart_completion(
            prompt=prompt,
            task_type="extraction",
            max_tokens=2000,
            temperature=0.0
        )

        # Parse JSON from response
        content = result.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Find JSON
        start = content.find('{')
        end = content.rfind('}')
        if start >= 0 and end >= 0:
            extracted = json.loads(content[start:end+1])
        else:
            extracted = {"raw_text": content}

        return {
            "extracted_data": extracted,
            "cost": result.cost,
            "tokens": result.input_tokens + result.output_tokens
        }

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {"error": str(e), "cost": 0, "tokens": 0}


def generate_report(
    company_name: str,
    extracted_data: Dict,
    sources: List[Dict],
    profile_data: Dict
) -> str:
    """Generate comprehensive research report."""
    from src.company_researcher.llm.smart_client import smart_completion

    company = profile_data.get('company', {})

    # Build context
    context = f"""
Company: {company_name}
Legal Name: {company.get('legal_name', 'N/A')}
Industry: {company.get('industry', 'N/A')}
Country: {company.get('country', 'N/A')}
Parent Company: {company.get('details', {}).get('parent_company', 'N/A')}
Sectors: {', '.join(company.get('sectors', []))}
Services: {', '.join(company.get('services', [])[:5])}

Extracted Data:
{json.dumps(extracted_data.get('extracted_data', {}), indent=2)}

Number of Sources: {len(sources)}
"""

    prompt = f"""Generate a comprehensive research report for {company_name}.

{context}

Create a detailed markdown report with these sections:
# {company_name} - Company Research Report

## Executive Summary
(2-3 paragraph overview)

## Company Overview
- Basic information
- History and founding
- Ownership structure

## Financial Analysis
- Revenue and growth
- Profitability metrics
- Investment trends

## Market Position
- Market share
- Competitive positioning
- Customer base

## Products and Services
- Main offerings
- Key differentiators

## Competitive Landscape
- Key competitors
- Competitive advantages/disadvantages

## Strategic Initiatives
- Recent developments
- Future plans

## Risk Factors
- Key risks and challenges

## Sources
List key sources used.

Make it comprehensive and professional.
"""

    try:
        result = smart_completion(
            prompt=prompt,
            task_type="synthesis",
            max_tokens=4000,
            temperature=0.1
        )
        return result.content
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        return f"# {company_name} Research Report\n\nError generating report: {e}"


def check_quality(company_name: str, report: str, sources: List[Dict]) -> Dict[str, Any]:
    """Check quality of research."""
    from src.company_researcher.llm.smart_client import smart_completion

    prompt = f"""Evaluate the quality of this research report for {company_name}.

Report length: {len(report)} characters
Number of sources: {len(sources)}

Report preview (first 2000 chars):
{report[:2000]}

Evaluate on 0-100 scale:
1. Completeness (all sections covered)
2. Data quality (specific numbers, facts)
3. Source diversity (variety of sources)
4. Depth of analysis
5. Professional presentation

Return JSON:
{{
    "quality_score": <0-100>,
    "completeness_score": <0-100>,
    "data_quality_score": <0-100>,
    "source_diversity_score": <0-100>,
    "missing_information": ["list of gaps"],
    "strengths": ["list of strengths"],
    "recommendations": ["improvements needed"]
}}
"""

    try:
        result = smart_completion(
            prompt=prompt,
            task_type="classification",
            max_tokens=1000,
            temperature=0.0
        )

        content = result.content
        start = content.find('{')
        end = content.rfind('}')
        if start >= 0 and end >= 0:
            return json.loads(content[start:end+1])
        return {"quality_score": 50, "error": "Could not parse quality response"}

    except Exception as e:
        logger.error(f"Quality check error: {e}")
        return {"quality_score": 50, "error": str(e)}


def save_report(
    company_name: str,
    report: str,
    sources: List[Dict],
    extracted_data: Dict,
    quality: Dict,
    profile_data: Dict,
    output_dir: Path
) -> Path:
    """Save all research outputs."""
    safe_name = company_name.lower().replace(" ", "_").replace("/", "_")
    company_dir = output_dir / safe_name
    company_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Save full report
    report_path = company_dir / "00_full_report.md"
    report_path.write_text(report, encoding='utf-8')

    # 2. Save metrics
    metrics = {
        "company_name": company_name,
        "timestamp": timestamp,
        "total_sources": len(sources),
        "quality_score": quality.get('quality_score', 0),
        "completeness_score": quality.get('completeness_score', 0),
        "profile_data": {
            "industry": profile_data.get('company', {}).get('industry', ''),
            "country": profile_data.get('company', {}).get('country', ''),
            "parent_company": profile_data.get('company', {}).get('details', {}).get('parent_company', ''),
        }
    }
    (company_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding='utf-8')

    # 3. Save sources
    sources_md = f"# Sources for {company_name}\n\n"
    sources_md += f"**Total Sources**: {len(sources)}\n\n"

    # Group by domain
    domains = {}
    for source in sources:
        url = source.get('url', '')
        if url:
            try:
                domain = urlparse(url).netloc
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(source)
            except:
                pass

    sources_md += f"**Unique Domains**: {len(domains)}\n\n"

    for domain, domain_sources in sorted(domains.items(), key=lambda x: -len(x[1])):
        sources_md += f"\n## {domain} ({len(domain_sources)} sources)\n\n"
        for source in domain_sources[:15]:
            title = source.get('title', 'Untitled')[:80]
            url = source.get('url', '')
            sources_md += f"- [{title}]({url})\n"

    (company_dir / "07_sources.md").write_text(sources_md, encoding='utf-8')

    # 4. Save extracted data
    (company_dir / "extracted_data.json").write_text(
        json.dumps(extracted_data, indent=2), encoding='utf-8'
    )

    # 5. Save quality assessment
    quality_md = f"# Quality Assessment: {company_name}\n\n"
    quality_md += f"**Overall Score**: {quality.get('quality_score', 0)}/100\n\n"
    quality_md += f"| Metric | Score |\n|--------|-------|\n"
    quality_md += f"| Completeness | {quality.get('completeness_score', 0)}/100 |\n"
    quality_md += f"| Data Quality | {quality.get('data_quality_score', 0)}/100 |\n"
    quality_md += f"| Source Diversity | {quality.get('source_diversity_score', 0)}/100 |\n\n"

    quality_md += "## Strengths\n"
    for s in quality.get('strengths', []):
        quality_md += f"- {s}\n"

    quality_md += "\n## Missing Information\n"
    for m in quality.get('missing_information', []):
        quality_md += f"- {m}\n"

    quality_md += "\n## Recommendations\n"
    for r in quality.get('recommendations', []):
        quality_md += f"- {r}\n"

    (company_dir / "quality_assessment.md").write_text(quality_md, encoding='utf-8')

    # 6. Create README
    readme = f"""# {company_name} Research Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

| Metric | Value |
|--------|-------|
| Quality Score | {quality.get('quality_score', 0)}/100 |
| Total Sources | {len(sources)} |
| Unique Domains | {len(domains)} |

## Files

- [00_full_report.md](00_full_report.md) - Complete research report
- [07_sources.md](07_sources.md) - All sources used ({len(sources)} total)
- [metrics.json](metrics.json) - Research metrics
- [extracted_data.json](extracted_data.json) - Structured data
- [quality_assessment.md](quality_assessment.md) - Quality analysis
"""
    (company_dir / "README.md").write_text(readme, encoding='utf-8')

    return company_dir


def research_company(
    company_name: str,
    profile_data: Dict,
    output_dir: Path,
    target_quality: float = 90.0,
    target_sources: int = 200,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Research a company comprehensively.

    Args:
        company_name: Name of company
        profile_data: Profile data from YAML
        output_dir: Output directory
        target_quality: Target quality score
        target_sources: Target number of sources
        max_iterations: Max improvement iterations

    Returns:
        Research result dict
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"  RESEARCHING: {company_name}")
    logger.info(f"  Target: {target_sources}+ sources, {target_quality}% quality")
    logger.info(f"{'='*70}\n")

    start_time = time.time()
    all_sources = []
    total_cost = 0.0
    total_tokens = 0

    for iteration in range(1, max_iterations + 1):
        logger.info(f"\n--- Iteration {iteration}/{max_iterations} ---")

        # Generate queries
        queries = create_comprehensive_queries(profile_data)
        logger.info(f"Generated {len(queries)} search queries")

        # If we need more sources, add more specific queries
        if len(all_sources) < target_sources and iteration > 1:
            extra_queries = [
                f"{company_name} telecommunications statistics",
                f"{company_name} market report PDF",
                f"{company_name} investor presentation",
                f"{company_name} quarterly results",
                f"{company_name} growth strategy",
                f"{company_name} digital services",
                f"{company_name} employee count",
                f"{company_name} network infrastructure",
            ]
            queries = extra_queries + queries

        # Search
        results = search_with_router(queries, max_results_per_query=10)
        all_sources.extend(results)
        all_sources = deduplicate_sources(all_sources)

        logger.info(f"Total unique sources: {len(all_sources)}")

        # Check if we have enough sources
        if len(all_sources) >= target_sources:
            logger.info(f"Source target ({target_sources}) reached!")
            break

        if iteration < max_iterations:
            logger.info(f"Need {target_sources - len(all_sources)} more sources...")
            time.sleep(2)  # Brief pause between iterations

    # Extract data
    logger.info("\nExtracting structured data...")
    extraction_result = extract_data_from_sources(company_name, all_sources)
    extracted_data = extraction_result.get('extracted_data', {})
    total_cost += extraction_result.get('cost', 0)
    total_tokens += extraction_result.get('tokens', 0)

    # Generate report
    logger.info("Generating comprehensive report...")
    report = generate_report(company_name, extraction_result, all_sources, profile_data)

    # Check quality
    logger.info("Checking research quality...")
    quality = check_quality(company_name, report, all_sources)
    quality_score = quality.get('quality_score', 0)

    logger.info(f"\nQuality Score: {quality_score}/100")
    logger.info(f"Total Sources: {len(all_sources)}")

    # Save results
    report_dir = save_report(
        company_name=company_name,
        report=report,
        sources=all_sources,
        extracted_data=extraction_result,
        quality=quality,
        profile_data=profile_data,
        output_dir=output_dir
    )

    duration = time.time() - start_time

    return {
        "company_name": company_name,
        "success": True,
        "quality_score": quality_score,
        "total_sources": len(all_sources),
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "duration_seconds": duration,
        "report_dir": str(report_dir),
        "quality_details": quality
    }


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  PARAGUAY TELECOM COMPREHENSIVE RESEARCH V2")
    print("  Using Smart Search Router with Fallback")
    print("  Target: 200+ sources, 90% quality per company")
    print("="*70 + "\n")

    # Check for API key (at least need Anthropic for LLM)
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("API Keys configured")

    # Paths
    profiles_dir = project_root / "research_targets" / "paraguay_telecom"
    output_dir = project_root / "outputs" / "research"

    # Companies to research
    companies = [
        ("Tigo Paraguay", profiles_dir / "tigo_paraguay.yaml"),
        ("Personal Paraguay", profiles_dir / "personal_paraguay.yaml"),
    ]

    results = []

    for company_name, profile_path in companies:
        try:
            profile_data = load_company_profile(str(profile_path))
            logger.info(f"Loaded profile: {profile_path}")

            result = research_company(
                company_name=company_name,
                profile_data=profile_data,
                output_dir=output_dir,
                target_quality=90.0,
                target_sources=200,
                max_iterations=3
            )

            results.append(result)

            print(f"\n{'='*50}")
            print(f"  {company_name}")
            print(f"  Quality: {result['quality_score']}/100")
            print(f"  Sources: {result['total_sources']}")
            print(f"  Duration: {result['duration_seconds']:.1f}s")
            print(f"  Output: {result['report_dir']}")
            print(f"{'='*50}")

        except Exception as e:
            logger.error(f"Failed to research {company_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "company_name": company_name,
                "success": False,
                "error": str(e)
            })

    # Final summary
    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)

    successful = [r for r in results if r.get('success')]

    for r in results:
        status = "" if r.get('success') else ""
        print(f"\n{status} {r['company_name']}:")
        if r.get('success'):
            print(f"   Quality: {r['quality_score']}/100")
            print(f"   Sources: {r['total_sources']}")
            meets_quality = "" if r['quality_score'] >= 90 else ""
            meets_sources = "" if r['total_sources'] >= 200 else ""
            print(f"   Quality Target (90%): {meets_quality}")
            print(f"   Sources Target (200): {meets_sources}")
        else:
            print(f"   Error: {r.get('error', 'Unknown')}")

    if successful:
        total_sources = sum(r['total_sources'] for r in successful)
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        print(f"\nTotals:")
        print(f"  Total Sources: {total_sources}")
        print(f"  Average Quality: {avg_quality:.1f}/100")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
