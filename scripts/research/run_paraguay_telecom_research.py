#!/usr/bin/env python
"""
Paraguay Telecom Research - Comprehensive Analysis
===================================================

Research Tigo Paraguay and Personal Paraguay with:
- 200+ sources per company
- 90% quality target
- Comprehensive multi-agent analysis

Usage:
    python run_paraguay_telecom_research.py

Requirements:
    - ANTHROPIC_API_KEY in .env
    - TAVILY_API_KEY in .env
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Override configuration for comprehensive research
os.environ['NUM_SEARCH_QUERIES'] = '20'  # More queries for more sources
os.environ['SEARCH_RESULTS_PER_QUERY'] = '15'  # More results per query
os.environ['MAX_SEARCH_RESULTS'] = '300'  # Higher cap
os.environ['MAX_RESEARCH_TIME_SECONDS'] = '900'  # 15 minutes per company
os.environ['DOMAIN_EXPLORATION_MAX_PAGES'] = '20'  # More domain pages

from dotenv import load_dotenv
load_dotenv()

# Now import after env vars are set
from src.company_researcher import execute_research, ResearchDepth
from src.company_researcher.config import get_config, ResearchConfig
from src.company_researcher.graphs import research_graph
from src.company_researcher.quality.quality_checker import check_research_quality


def load_company_profile(profile_path: str) -> Dict[str, Any]:
    """Load company profile from YAML file."""
    with open(profile_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_enhanced_queries(company_data: Dict[str, Any]) -> List[str]:
    """Generate enhanced search queries from profile."""
    queries = []

    company = company_data.get('company', {})
    research = company_data.get('research', {})
    competitors = company_data.get('competitors', [])

    company_name = company.get('name', '')
    legal_name = company.get('legal_name', '')
    parent_company = company.get('details', {}).get('parent_company', '')
    country = company.get('country', '')

    # Add priority queries from profile
    priority_queries = research.get('priority_queries', [])
    queries.extend(priority_queries)

    # Add company-specific queries
    queries.extend([
        f"{company_name} ingresos revenue 2024",
        f"{company_name} market share {country}",
        f"{company_name} financial results",
        f"{company_name} subscribers users 2024",
        f"{company_name} network coverage 4G 5G",
        f"{company_name} CEO leadership management",
        f"{company_name} news noticias 2024",
        f"{company_name} competitors competition",
        f"{company_name} strategy expansion",
        f"{company_name} digital transformation",
    ])

    # Add legal name queries
    if legal_name and legal_name != company_name:
        queries.extend([
            f"{legal_name} financial results",
            f"{legal_name} annual report",
            f"{legal_name} revenue ingresos",
        ])

    # Add parent company queries
    if parent_company:
        queries.extend([
            f"{parent_company} {country} operations",
            f"{parent_company} annual report {country}",
            f"{parent_company} {company_name} results",
        ])

    # Add competitive queries
    for competitor in competitors:
        comp_name = competitor.get('name', competitor) if isinstance(competitor, dict) else competitor
        queries.append(f"{company_name} vs {comp_name} comparison")

    # Add regulatory queries
    queries.extend([
        f"CONATEL {country} telecommunications statistics",
        f"{country} telecommunications market 2024",
        f"GSMA {country} mobile market report",
    ])

    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique_queries.append(q)

    return unique_queries[:30]  # Cap at 30 queries


def run_comprehensive_research(
    company_name: str,
    profile_data: Dict[str, Any],
    output_dir: Path,
    target_quality: float = 90.0,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Run comprehensive research with quality iteration.

    Args:
        company_name: Name of the company
        profile_data: Company profile data from YAML
        output_dir: Directory for output files
        target_quality: Target quality score (0-100)
        max_iterations: Maximum quality iterations

    Returns:
        Research result dictionary
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"  COMPREHENSIVE RESEARCH: {company_name}")
    logger.info(f"  Target Quality: {target_quality}%")
    logger.info(f"  Max Iterations: {max_iterations}")
    logger.info(f"{'='*70}\n")

    # Generate enhanced queries
    queries = create_enhanced_queries(profile_data)
    logger.info(f"Generated {len(queries)} search queries")

    # Get configuration
    config = get_config()

    # Override config for comprehensive research
    # Note: These are accessed via the config object

    iteration = 0
    best_result = None
    best_quality = 0.0
    all_sources = []

    while iteration < max_iterations:
        iteration += 1
        logger.info(f"\n--- Iteration {iteration}/{max_iterations} ---")

        try:
            # Initialize state for LangGraph
            initial_state = {
                "company_name": company_name,
                "queries": queries,
                "search_results": [],
                "extracted_data": {},
                "report": "",
                "total_cost": 0.0,
                "total_tokens": 0,
                "error": None
            }

            # Run the research graph
            logger.info("Running research graph...")
            result = research_graph.invoke(initial_state)

            # Collect sources
            search_results = result.get('search_results', [])
            all_sources.extend(search_results)

            # Deduplicate sources by URL
            seen_urls = set()
            unique_sources = []
            for source in all_sources:
                url = source.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_sources.append(source)
            all_sources = unique_sources

            logger.info(f"Total unique sources collected: {len(all_sources)}")
            logger.info(f"Cost so far: ${result.get('total_cost', 0):.4f}")

            # Check quality
            extracted_data = result.get('extracted_data', {})
            extracted_str = json.dumps(extracted_data, indent=2) if extracted_data else ""

            if extracted_str and all_sources:
                quality_result = check_research_quality(
                    company_name=company_name,
                    extracted_data=extracted_str,
                    sources=all_sources
                )

                quality_score = quality_result.get('quality_score', 0)
                missing_info = quality_result.get('missing_information', [])
                recommended_queries = quality_result.get('recommended_queries', [])

                logger.info(f"Quality Score: {quality_score:.1f}/100")

                if quality_score > best_quality:
                    best_quality = quality_score
                    best_result = result
                    best_result['quality_score'] = quality_score
                    best_result['quality_result'] = quality_result

                if quality_score >= target_quality:
                    logger.info(f"Target quality {target_quality}% achieved!")
                    break

                if iteration < max_iterations:
                    # Add recommended queries for next iteration
                    if recommended_queries:
                        logger.info(f"Adding {len(recommended_queries)} recommended queries")
                        queries = recommended_queries + queries[:20]
                    elif missing_info:
                        # Generate queries from missing info
                        for info in missing_info[:5]:
                            queries.insert(0, f"{company_name} {info}")
            else:
                # No quality check possible yet
                best_result = result

        except Exception as e:
            logger.error(f"Error in iteration {iteration}: {e}")
            import traceback
            traceback.print_exc()
            if best_result is None:
                best_result = {"error": str(e)}

    # Prepare final result
    if best_result:
        best_result['all_sources'] = all_sources
        best_result['total_sources'] = len(all_sources)
        best_result['iterations'] = iteration
        best_result['final_quality'] = best_quality

    return best_result


def save_comprehensive_report(
    company_name: str,
    result: Dict[str, Any],
    profile_data: Dict[str, Any],
    output_dir: Path
) -> Path:
    """Save comprehensive research report."""
    # Create company directory
    safe_name = company_name.lower().replace(" ", "_").replace("/", "_")
    company_dir = output_dir / safe_name
    company_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save full report
    report_content = result.get('report', '')
    if report_content:
        report_path = company_dir / "00_full_report.md"
        report_path.write_text(report_content, encoding='utf-8')
        logger.info(f"Saved report: {report_path}")

    # Save metrics
    metrics = {
        "company_name": company_name,
        "timestamp": timestamp,
        "total_sources": result.get('total_sources', len(result.get('search_results', []))),
        "quality_score": result.get('final_quality', 0),
        "iterations": result.get('iterations', 1),
        "total_cost": result.get('total_cost', 0),
        "total_tokens": result.get('total_tokens', 0),
        "profile_data": {
            "industry": profile_data.get('company', {}).get('industry', ''),
            "country": profile_data.get('company', {}).get('country', ''),
            "parent_company": profile_data.get('company', {}).get('details', {}).get('parent_company', ''),
        }
    }
    metrics_path = company_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding='utf-8')

    # Save sources list
    sources = result.get('all_sources', result.get('search_results', []))
    if sources:
        sources_md = f"# Sources for {company_name}\n\n"
        sources_md += f"Total Sources: {len(sources)}\n\n"

        # Group by domain
        from urllib.parse import urlparse
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

        for domain, domain_sources in sorted(domains.items()):
            sources_md += f"\n## {domain} ({len(domain_sources)} sources)\n\n"
            for source in domain_sources[:10]:  # Max 10 per domain in listing
                title = source.get('title', 'Untitled')
                url = source.get('url', '')
                sources_md += f"- [{title}]({url})\n"

        sources_path = company_dir / "07_sources.md"
        sources_path.write_text(sources_md, encoding='utf-8')

    # Save extracted data
    extracted = result.get('extracted_data', {})
    if extracted:
        data_path = company_dir / "extracted_data.json"
        data_path.write_text(json.dumps(extracted, indent=2), encoding='utf-8')

    # Save quality assessment
    quality_result = result.get('quality_result', {})
    if quality_result:
        quality_md = f"# Quality Assessment for {company_name}\n\n"
        quality_md += f"**Quality Score**: {quality_result.get('quality_score', 0):.1f}/100\n\n"

        quality_md += "## Strengths\n"
        for strength in quality_result.get('strengths', []):
            quality_md += f"- {strength}\n"

        quality_md += "\n## Missing Information\n"
        for missing in quality_result.get('missing_information', []):
            quality_md += f"- {missing}\n"

        quality_path = company_dir / "quality_assessment.md"
        quality_path.write_text(quality_md, encoding='utf-8')

    # Create README
    readme = f"""# {company_name} Research Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

| Metric | Value |
|--------|-------|
| Quality Score | {result.get('final_quality', 0):.1f}/100 |
| Total Sources | {result.get('total_sources', 0)} |
| Iterations | {result.get('iterations', 1)} |
| Total Cost | ${result.get('total_cost', 0):.4f} |

## Files

- `00_full_report.md` - Complete research report
- `07_sources.md` - All sources used
- `metrics.json` - Research metrics
- `extracted_data.json` - Structured data
- `quality_assessment.md` - Quality analysis

## Company Profile

- **Industry**: {profile_data.get('company', {}).get('industry', 'N/A')}
- **Country**: {profile_data.get('company', {}).get('country', 'N/A')}
- **Parent Company**: {profile_data.get('company', {}).get('details', {}).get('parent_company', 'N/A')}
"""

    readme_path = company_dir / "README.md"
    readme_path.write_text(readme, encoding='utf-8')

    return company_dir


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  PARAGUAY TELECOM RESEARCH")
    print("  Tigo Paraguay & Personal Paraguay")
    print("  Target: 200+ sources, 90% quality")
    print("="*70 + "\n")

    # Check API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        sys.exit(1)
    if not os.getenv('TAVILY_API_KEY'):
        print("ERROR: TAVILY_API_KEY not set in environment")
        sys.exit(1)

    print("API Keys: Configured")

    # Define paths
    profiles_dir = project_root / "research_targets" / "paraguay_telecom"
    output_dir = project_root / "outputs" / "research"

    # Companies to research
    companies = [
        ("Tigo Paraguay", profiles_dir / "tigo_paraguay.yaml"),
        ("Personal Paraguay", profiles_dir / "personal_paraguay.yaml"),
    ]

    results = []

    for company_name, profile_path in companies:
        print(f"\n{'='*70}")
        print(f"  Starting Research: {company_name}")
        print(f"{'='*70}")

        try:
            # Load profile
            profile_data = load_company_profile(str(profile_path))
            print(f"Loaded profile from: {profile_path}")

            # Run comprehensive research
            result = run_comprehensive_research(
                company_name=company_name,
                profile_data=profile_data,
                output_dir=output_dir,
                target_quality=90.0,
                max_iterations=3
            )

            # Save report
            if result:
                report_dir = save_comprehensive_report(
                    company_name=company_name,
                    result=result,
                    profile_data=profile_data,
                    output_dir=output_dir
                )

                print(f"\n Results saved to: {report_dir}")
                print(f"   - Quality Score: {result.get('final_quality', 0):.1f}/100")
                print(f"   - Total Sources: {result.get('total_sources', 0)}")
                print(f"   - Total Cost: ${result.get('total_cost', 0):.4f}")

                results.append({
                    "company": company_name,
                    "success": True,
                    "quality": result.get('final_quality', 0),
                    "sources": result.get('total_sources', 0),
                    "cost": result.get('total_cost', 0)
                })
            else:
                results.append({
                    "company": company_name,
                    "success": False,
                    "error": "No result returned"
                })

        except Exception as e:
            print(f"\n ERROR researching {company_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "company": company_name,
                "success": False,
                "error": str(e)
            })

    # Print summary
    print("\n" + "="*70)
    print("  RESEARCH SUMMARY")
    print("="*70)

    total_sources = 0
    total_cost = 0.0

    for r in results:
        status = "" if r.get('success') else ""
        print(f"\n{status} {r['company']}:")
        if r.get('success'):
            print(f"   Quality: {r.get('quality', 0):.1f}/100")
            print(f"   Sources: {r.get('sources', 0)}")
            print(f"   Cost: ${r.get('cost', 0):.4f}")
            total_sources += r.get('sources', 0)
            total_cost += r.get('cost', 0)
        else:
            print(f"   Error: {r.get('error', 'Unknown')}")

    print(f"\n{'='*70}")
    print(f"  TOTALS")
    print(f"  Total Sources: {total_sources}")
    print(f"  Total Cost: ${total_cost:.4f}")
    print(f"{'='*70}\n")

    # Check if targets met
    successful = [r for r in results if r.get('success')]
    if successful:
        avg_quality = sum(r.get('quality', 0) for r in successful) / len(successful)
        avg_sources = sum(r.get('sources', 0) for r in successful) / len(successful)

        print(f"Average Quality: {avg_quality:.1f}/100 (target: 90)")
        print(f"Average Sources: {avg_sources:.0f} (target: 200)")

        if avg_quality >= 90 and avg_sources >= 200:
            print("\n TARGETS MET!")
        else:
            if avg_quality < 90:
                print(f"\n Quality target not met (need {90 - avg_quality:.1f} more points)")
            if avg_sources < 200:
                print(f"\n Sources target not met (need {200 - avg_sources:.0f} more sources)")


if __name__ == "__main__":
    main()
