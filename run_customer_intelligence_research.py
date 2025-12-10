#!/usr/bin/env python3
"""
Customer Intelligence Platform - Batch Research Runner

Runs comprehensive research on all targets from the Customer Intelligence Platform
prospect list, prioritized by tier score.

Uses the new Cost-First routing to minimize API costs.
"""

import os
import sys
import yaml
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/customer_intel_research_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Import the research workflow
from src.company_researcher.workflows import research_company_comprehensive
from src.company_researcher.config import get_config
from src.company_researcher.integrations.search_router import get_search_router


# =============================================================================
# CONFIGURATION
# =============================================================================

# Targets directory
TARGETS_DIR = Path("research_targets_v2/customer_intelligence_platform")

# Output directory
OUTPUT_DIR = Path("outputs/research/customer_intelligence")

# Research configuration
RESEARCH_CONFIG = {
    "max_companies_per_run": 5,      # Limit per run to avoid timeouts
    "min_priority_score": 85,        # Only research Tier 1 (score >= 85)
    "delay_between_companies": 10,   # Seconds between companies
    "skip_existing": True,           # Skip if report already exists
}


def load_targets_from_yaml() -> List[Dict[str, Any]]:
    """Load all targets from the YAML prioritization file."""
    priority_file = TARGETS_DIR / "_prospect_prioritization.yaml"

    if not priority_file.exists():
        logger.error(f"Priority file not found: {priority_file}")
        return []

    with open(priority_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    targets = []

    # Extract Tier 1 targets (highest priority)
    tier_1 = data.get("tier_1_immediate", {}).get("targets", [])
    for t in tier_1:
        targets.append({
            "company": t.get("company"),
            "vertical": t.get("vertical"),
            "country": t.get("country"),
            "score": t.get("score", 90),
            "tier": 1,
            "rationale": t.get("rationale", ""),
            "entry_approach": t.get("entry_approach", ""),
        })

    # Extract Tier 2 targets
    tier_2 = data.get("tier_2_high", {}).get("targets", [])
    for t in tier_2:
        targets.append({
            "company": t.get("company"),
            "vertical": t.get("vertical", "Unknown"),
            "country": t.get("country", "LATAM"),
            "score": t.get("score", 75),
            "tier": 2,
        })

    # Sort by score descending
    targets.sort(key=lambda x: x.get("score", 0), reverse=True)

    logger.info(f"Loaded {len(targets)} targets from prioritization file")
    return targets


def get_output_path(company_name: str) -> Path:
    """Generate output path for a company."""
    safe_name = company_name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    return OUTPUT_DIR / safe_name


def check_existing_research(company_name: str) -> bool:
    """Check if research already exists for a company."""
    output_path = get_output_path(company_name)
    full_report = output_path / "00_full_report.md"
    return full_report.exists()


def run_research_for_company(company_name: str, context: Dict[str, Any]) -> Optional[Dict]:
    """
    Run comprehensive research for a single company.

    Args:
        company_name: Name of company to research
        context: Additional context (vertical, country, etc.)

    Returns:
        Research results dict or None on failure
    """
    logger.info(f"{'='*60}")
    logger.info(f"Starting research for: {company_name}")
    logger.info(f"Context: {context}")
    logger.info(f"{'='*60}")

    try:
        # Run comprehensive research
        result = research_company_comprehensive(company_name)

        if result:
            logger.info(f"Research completed for {company_name}")
            logger.info(f"  Report: {result.get('report_path', 'N/A')}")
            logger.info(f"  Duration: {result.get('metrics', {}).get('duration_seconds', 0):.1f}s")
            logger.info(f"  Cost: ${result.get('metrics', {}).get('cost_usd', 0):.4f}")
            return result
        else:
            logger.warning(f"Research returned empty result for {company_name}")
            return None

    except Exception as e:
        logger.error(f"Research failed for {company_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_batch_summary(results: List[Dict], start_time: datetime):
    """Save summary of batch research run."""
    summary = {
        "run_timestamp": start_time.isoformat(),
        "total_companies": len(results),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "total_duration_seconds": (datetime.now() - start_time).total_seconds(),
        "total_cost_usd": sum(r.get("cost", 0) for r in results if r.get("success")),
        "companies": results,
    }

    summary_path = OUTPUT_DIR / f"_batch_summary_{start_time:%Y%m%d_%H%M%S}.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Batch summary saved to: {summary_path}")
    return summary


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("CUSTOMER INTELLIGENCE PLATFORM - BATCH RESEARCH RUNNER")
    print("="*70 + "\n")

    start_time = datetime.now()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load targets
    targets = load_targets_from_yaml()
    if not targets:
        logger.error("No targets found!")
        return

    # Filter by minimum score
    min_score = RESEARCH_CONFIG["min_priority_score"]
    filtered_targets = [t for t in targets if t.get("score", 0) >= min_score]

    print(f"Total targets loaded: {len(targets)}")
    print(f"Targets with score >= {min_score}: {len(filtered_targets)}")
    print(f"Max companies per run: {RESEARCH_CONFIG['max_companies_per_run']}")
    print()

    # Show search router status
    router = get_search_router()
    print("Search Router Status:")
    print(f"  Available providers: {router._get_available_providers()}")
    print(f"  Cost-First routing: Enabled")
    print()

    # List targets to research
    print("TARGETS TO RESEARCH:")
    print("-" * 50)
    for i, t in enumerate(filtered_targets[:RESEARCH_CONFIG["max_companies_per_run"]], 1):
        existing = "EXISTS" if check_existing_research(t["company"]) else "NEW"
        print(f"  {i}. {t['company']} (Score: {t['score']}, {t['vertical']}, {t['country']}) [{existing}]")
    print()

    # Confirm execution
    if len(sys.argv) < 2 or sys.argv[1] != "--run":
        print("To execute research, run with: python run_customer_intelligence_research.py --run")
        print("\nTarget files can be modified in:")
        print(f"  {TARGETS_DIR}/_prospect_prioritization.yaml")
        return

    # Execute research
    results = []
    max_companies = RESEARCH_CONFIG["max_companies_per_run"]

    for i, target in enumerate(filtered_targets[:max_companies], 1):
        company = target["company"]

        # Check if should skip existing
        if RESEARCH_CONFIG["skip_existing"] and check_existing_research(company):
            logger.info(f"[{i}/{max_companies}] Skipping {company} (already researched)")
            results.append({
                "company": company,
                "success": True,
                "skipped": True,
                "reason": "Already exists"
            })
            continue

        print(f"\n[{i}/{max_companies}] Researching: {company}")

        result = run_research_for_company(company, target)

        if result:
            results.append({
                "company": company,
                "success": True,
                "report_path": result.get("report_path"),
                "duration": result.get("metrics", {}).get("duration_seconds", 0),
                "cost": result.get("metrics", {}).get("cost_usd", 0),
            })
        else:
            results.append({
                "company": company,
                "success": False,
                "error": "Research failed"
            })

        # Delay between companies
        if i < max_companies:
            delay = RESEARCH_CONFIG["delay_between_companies"]
            logger.info(f"Waiting {delay}s before next company...")
            time.sleep(delay)

    # Save summary
    summary = save_batch_summary(results, start_time)

    # Print final summary
    print("\n" + "="*70)
    print("BATCH RESEARCH COMPLETE")
    print("="*70)
    print(f"Total companies: {len(results)}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total duration: {summary['total_duration_seconds']:.1f}s")
    print(f"Total cost: ${summary['total_cost_usd']:.4f}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
