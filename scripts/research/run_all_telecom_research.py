#!/usr/bin/env python3
"""
Telecommunications Vertical - Complete Research Runner

Runs comprehensive research on ALL telecommunications companies from the
Customer Intelligence Platform vertical definition.

Companies by Region:
- Paraguay: Tigo, Personal, Claro
- Brazil: Vivo, Claro, TIM
- Argentina: Personal, Claro, Movistar
- Chile: Entel, Movistar, Claro, WOM
- Central America: Tigo Guatemala, Claro Guatemala, Tigo El Salvador,
                   Tigo Honduras, Kolbi Costa Rica
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/telecom_research_{datetime.now():%Y%m%d_%H%M%S}.log"),
    ],
)
logger = logging.getLogger(__name__)

# =============================================================================
# TELECOMMUNICATIONS COMPANIES TO RESEARCH
# =============================================================================

TELECOM_COMPANIES = {
    "paraguay": {
        "region_name": "Paraguay",
        "companies": [
            {
                "name": "Tigo Paraguay",
                "parent": "Millicom International",
                "priority": "P1",
                "score": 95,
                "market_share": "45%",
                "competitors": ["Personal Paraguay", "Claro Paraguay"],
                "context": "Largest mobile operator in Paraguay, part of Millicom",
            },
            {
                "name": "Personal Paraguay",
                "parent": "Telecom Argentina",
                "priority": "P1",
                "score": 90,
                "market_share": "35%",
                "competitors": ["Tigo Paraguay", "Claro Paraguay"],
                "context": "Second largest mobile operator in Paraguay",
            },
            {
                "name": "Claro Paraguay",
                "parent": "America Movil",
                "priority": "P1",
                "score": 85,
                "market_share": "20%",
                "competitors": ["Tigo Paraguay", "Personal Paraguay"],
                "context": "Third mobile operator in Paraguay, part of America Movil",
            },
        ],
    },
    "brazil": {
        "region_name": "Brazil",
        "companies": [
            {
                "name": "Vivo Brazil",
                "parent": "Telefonica",
                "priority": "P1",
                "score": 95,
                "market_share": "33%",
                "competitors": ["Claro Brasil", "TIM Brasil", "Oi"],
                "context": "Largest telecom in Brazil with 15M+ social followers",
            },
            {
                "name": "Claro Brasil",
                "parent": "America Movil",
                "priority": "P1",
                "score": 92,
                "market_share": "25%",
                "competitors": ["Vivo Brazil", "TIM Brasil", "Oi"],
                "context": "Second largest telecom in Brazil, strong network",
            },
            {
                "name": "TIM Brasil",
                "parent": "TIM Italy",
                "priority": "P1",
                "score": 88,
                "market_share": "24%",
                "competitors": ["Vivo Brazil", "Claro Brasil", "Oi"],
                "context": "Third largest mobile operator in Brazil",
            },
        ],
    },
    "argentina": {
        "region_name": "Argentina",
        "companies": [
            {
                "name": "Personal Argentina",
                "parent": "Telecom Argentina",
                "priority": "P1",
                "score": 90,
                "market_share": "35%",
                "competitors": ["Claro Argentina", "Movistar Argentina"],
                "context": "Largest mobile operator in Argentina",
            },
            {
                "name": "Claro Argentina",
                "parent": "America Movil",
                "priority": "P1",
                "score": 88,
                "market_share": "30%",
                "competitors": ["Personal Argentina", "Movistar Argentina"],
                "context": "Second largest mobile operator in Argentina",
            },
            {
                "name": "Movistar Argentina",
                "parent": "Telefonica",
                "priority": "P1",
                "score": 85,
                "market_share": "25%",
                "competitors": ["Personal Argentina", "Claro Argentina"],
                "context": "Third mobile operator in Argentina",
            },
        ],
    },
    "chile": {
        "region_name": "Chile",
        "companies": [
            {
                "name": "Entel Chile",
                "parent": "Entel",
                "priority": "P1",
                "score": 88,
                "market_share": "30%",
                "competitors": ["Movistar Chile", "Claro Chile", "WOM Chile"],
                "context": "Largest telecom in Chile",
            },
            {
                "name": "Movistar Chile",
                "parent": "Telefonica",
                "priority": "P1",
                "score": 85,
                "market_share": "28%",
                "competitors": ["Entel Chile", "Claro Chile", "WOM Chile"],
                "context": "Second largest telecom in Chile",
            },
            {
                "name": "Claro Chile",
                "parent": "America Movil",
                "priority": "P2",
                "score": 80,
                "market_share": "22%",
                "competitors": ["Entel Chile", "Movistar Chile", "WOM Chile"],
                "context": "Third largest telecom in Chile",
            },
            {
                "name": "WOM Chile",
                "parent": "WOM",
                "priority": "P2",
                "score": 78,
                "market_share": "18%",
                "competitors": ["Entel Chile", "Movistar Chile", "Claro Chile"],
                "context": "Disruptor brand in Chilean telecom market",
            },
        ],
    },
    "central_america": {
        "region_name": "Central America",
        "companies": [
            {
                "name": "Tigo Guatemala",
                "parent": "Millicom",
                "priority": "P2",
                "score": 75,
                "country": "Guatemala",
                "competitors": ["Claro Guatemala"],
                "context": "Leading mobile operator in Guatemala",
            },
            {
                "name": "Claro Guatemala",
                "parent": "America Movil",
                "priority": "P2",
                "score": 72,
                "country": "Guatemala",
                "competitors": ["Tigo Guatemala"],
                "context": "Second mobile operator in Guatemala",
            },
            {
                "name": "Tigo El Salvador",
                "parent": "Millicom",
                "priority": "P2",
                "score": 70,
                "country": "El Salvador",
                "competitors": ["Claro El Salvador"],
                "context": "Mobile operator in El Salvador",
            },
            {
                "name": "Tigo Honduras",
                "parent": "Millicom",
                "priority": "P2",
                "score": 70,
                "country": "Honduras",
                "competitors": ["Claro Honduras"],
                "context": "Mobile operator in Honduras",
            },
        ],
    },
}

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR = Path("outputs/telecom_research")
RESEARCH_CONFIG = {
    "delay_between_companies": 15,  # Seconds between companies
    "skip_existing": False,  # Set True to skip already researched
    "min_score": 70,  # Minimum priority score to research
    "max_per_region": None,  # None = all companies
}


def get_output_path(company_name: str) -> Path:
    """Generate output path for a company."""
    safe_name = company_name.lower().replace(" ", "_").replace("/", "_")
    return OUTPUT_DIR / safe_name


def check_existing_research(company_name: str) -> bool:
    """Check if research already exists for a company."""
    output_path = get_output_path(company_name)
    full_report = output_path / "00_full_report.md"
    return full_report.exists()


def run_company_research(company: Dict[str, Any], region: str) -> Optional[Dict[str, Any]]:
    """
    Run comprehensive research for a single company.
    """
    from src.company_researcher.workflows import research_company_comprehensive

    company_name = company["name"]

    logger.info("=" * 70)
    logger.info(f"RESEARCHING: {company_name}")
    logger.info(f"  Region: {region}")
    logger.info(f"  Parent: {company.get('parent', 'Unknown')}")
    logger.info(f"  Priority: {company.get('priority', 'Unknown')}")
    logger.info(f"  Score: {company.get('score', 0)}")
    logger.info("=" * 70)

    start_time = datetime.now()

    try:
        # Run the comprehensive research workflow
        result = research_company_comprehensive(company_name)

        duration = (datetime.now() - start_time).total_seconds()

        if result:
            logger.info(f"[SUCCESS] {company_name}")
            logger.info(f"  Duration: {duration:.1f}s")
            logger.info(f"  Report: {result.get('report_path', 'N/A')}")

            return {
                "company": company_name,
                "region": region,
                "success": True,
                "duration": duration,
                "report_path": result.get("report_path"),
                "metrics": result.get("metrics", {}),
            }
        else:
            logger.warning(f"[EMPTY] {company_name} - No result returned")
            return {
                "company": company_name,
                "region": region,
                "success": False,
                "duration": duration,
                "error": "Empty result",
            }

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"[FAILED] {company_name}: {e}")
        import traceback

        traceback.print_exc()

        return {
            "company": company_name,
            "region": region,
            "success": False,
            "duration": duration,
            "error": str(e),
        }


def save_batch_summary(results: List[Dict], start_time: datetime):
    """Save summary of the batch research run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    summary = {
        "run_timestamp": start_time.isoformat(),
        "vertical": "Telecommunications",
        "total_companies": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "total_duration_seconds": (datetime.now() - start_time).total_seconds(),
        "results_by_region": {},
        "all_results": results,
    }

    # Group by region
    for r in results:
        region = r.get("region", "Unknown")
        if region not in summary["results_by_region"]:
            summary["results_by_region"][region] = {"total": 0, "successful": 0, "failed": 0}
        summary["results_by_region"][region]["total"] += 1
        if r.get("success"):
            summary["results_by_region"][region]["successful"] += 1
        else:
            summary["results_by_region"][region]["failed"] += 1

    # Save summary
    summary_path = OUTPUT_DIR / f"_batch_summary_{start_time:%Y%m%d_%H%M%S}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Summary saved to: {summary_path}")
    return summary


def print_companies_to_research():
    """Print all companies that will be researched."""
    print("\n" + "=" * 70)
    print("TELECOMMUNICATIONS VERTICAL - COMPANIES TO RESEARCH")
    print("=" * 70)

    total = 0
    for region_key, region_data in TELECOM_COMPANIES.items():
        region_name = region_data["region_name"]
        companies = region_data["companies"]

        # Filter by score
        filtered = [c for c in companies if c.get("score", 0) >= RESEARCH_CONFIG["min_score"]]

        print(f"\n{region_name} ({len(filtered)} companies):")
        print("-" * 50)

        for c in filtered:
            status = "EXISTS" if check_existing_research(c["name"]) else "NEW"
            print(
                f"  [{c.get('priority', 'P?')}] {c['name']:25} Score: {c.get('score', 0):3} [{status}]"
            )

        total += len(filtered)

    print(f"\n{'=' * 70}")
    print(f"TOTAL COMPANIES: {total}")
    print("=" * 70)

    return total


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("  TELECOMMUNICATIONS VERTICAL - COMPLETE RESEARCH RUNNER")
    print("  Customer Intelligence Platform Research System")
    print("=" * 70)

    # Show companies
    total_companies = print_companies_to_research()

    # Check for run flag
    if len(sys.argv) < 2 or sys.argv[1] != "--run":
        print("\n[INFO] This is a preview. To execute research, run:")
        print("  python run_all_telecom_research.py --run")
        print("\nOptions:")
        print("  --run           Execute research on all companies")
        print("  --region=NAME   Only research specific region (paraguay, brazil, etc.)")
        print("  --company=NAME  Research a single company by name")
        return

    # Parse region filter
    region_filter = None
    company_filter = None

    for arg in sys.argv[1:]:
        if arg.startswith("--region="):
            region_filter = arg.split("=")[1].lower()
        elif arg.startswith("--company="):
            company_filter = arg.split("=")[1]

    # Start research
    start_time = datetime.now()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    company_count = 0

    for region_key, region_data in TELECOM_COMPANIES.items():
        # Apply region filter
        if region_filter and region_key != region_filter:
            continue

        region_name = region_data["region_name"]
        companies = region_data["companies"]

        # Filter by score
        filtered = [c for c in companies if c.get("score", 0) >= RESEARCH_CONFIG["min_score"]]

        # Apply max per region limit
        if RESEARCH_CONFIG["max_per_region"]:
            filtered = filtered[: RESEARCH_CONFIG["max_per_region"]]

        print(f"\n{'#' * 70}")
        print(f"# REGION: {region_name} ({len(filtered)} companies)")
        print(f"{'#' * 70}")

        for company in filtered:
            # Apply company filter
            if company_filter and company["name"].lower() != company_filter.lower():
                continue

            company_count += 1

            # Check if should skip existing
            if RESEARCH_CONFIG["skip_existing"] and check_existing_research(company["name"]):
                logger.info(f"[SKIP] {company['name']} - Already researched")
                results.append(
                    {
                        "company": company["name"],
                        "region": region_name,
                        "success": True,
                        "skipped": True,
                    }
                )
                continue

            # Run research
            print(f"\n[{company_count}/{total_companies}] Starting: {company['name']}")
            result = run_company_research(company, region_name)
            results.append(result)

            # Delay between companies
            if company_count < total_companies:
                delay = RESEARCH_CONFIG["delay_between_companies"]
                logger.info(f"Waiting {delay}s before next company...")
                time.sleep(delay)

    # Save summary
    summary = save_batch_summary(results, start_time)

    # Print final summary
    print("\n" + "=" * 70)
    print("  TELECOMMUNICATIONS RESEARCH COMPLETE")
    print("=" * 70)
    print(f"\nOverall Results:")
    print(f"  Total Companies: {len(results)}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Duration: {summary['total_duration_seconds']:.1f}s")

    print(f"\nResults by Region:")
    for region, stats in summary["results_by_region"].items():
        print(f"  {region}: {stats['successful']}/{stats['total']} successful")

    print(f"\nOutput Directory: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
