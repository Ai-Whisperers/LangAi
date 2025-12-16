"""
Research CLI Module.

Thin CLI wrapper that uses src.company_researcher as the engine.
All research logic is in src/company_researcher - this is just the CLI interface.

Settings are loaded from research_config.yaml.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Import the main engine from src
from src.company_researcher import ResearchDepth, execute_research
from src.company_researcher.config import get_config as get_src_config
from src.company_researcher.graphs import research_graph


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the research CLI."""
    parser = argparse.ArgumentParser(
        description="Company Research CLI (powered by src.company_researcher)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research single company
  python run_research.py --company "Tesla"

  # Research with specific depth
  python run_research.py --company "Apple" --depth comprehensive

  # Research from YAML profile
  python run_research.py --profile research_targets/company.yaml

  # Research all companies in a market folder
  python run_research.py --market research_targets/paraguay_telecom/

  # Use LangGraph workflow directly
  python run_research.py --company "Google" --use-graph

  # Show current configuration
  python run_research.py --show-config
""",
    )

    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--company", "-c", type=str, help="Company name to research")
    input_group.add_argument("--profile", "-p", type=str, help="Path to company YAML profile")
    input_group.add_argument(
        "--market", "-m", type=str, help="Path to market folder with YAML files"
    )

    # Research options
    research_group = parser.add_argument_group("Research Options")
    research_group.add_argument(
        "--depth",
        "-d",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Research depth level (default: standard)",
    )
    research_group.add_argument(
        "--use-graph",
        action="store_true",
        help="Use LangGraph workflow instead of orchestration engine",
    )
    research_group.add_argument(
        "--output", "-o", type=str, default="outputs/research", help="Output directory for reports"
    )
    research_group.add_argument(
        "--compare", action="store_true", help="Generate comparison report for market research"
    )

    # Utility options
    util_group = parser.add_argument_group("Utility Options")
    util_group.add_argument(
        "--show-config", action="store_true", help="Show current configuration and exit"
    )
    util_group.add_argument(
        "--dry-run", action="store_true", help="Preview what would happen without executing"
    )
    util_group.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    return parser


def get_depth_enum(depth_str: str) -> ResearchDepth:
    """Convert string depth to ResearchDepth enum."""
    mapping = {
        "quick": ResearchDepth.QUICK,
        "standard": ResearchDepth.STANDARD,
        "comprehensive": ResearchDepth.COMPREHENSIVE,
    }
    return mapping.get(depth_str, ResearchDepth.STANDARD)


def save_report(company_name: str, result: Dict[str, Any], output_dir: str) -> Path:
    """Save research report to file."""
    # Create output directory
    safe_name = company_name.lower().replace(" ", "_").replace("/", "_")
    company_dir = Path(output_dir) / safe_name
    company_dir.mkdir(parents=True, exist_ok=True)

    # Save full report
    report_content = result.get("report", "")
    if report_content:
        report_path = company_dir / "00_full_report.md"
        report_path.write_text(report_content, encoding="utf-8")
        print(f"  Report saved: {report_path}")

    # Save metrics
    metrics = {
        "company_name": company_name,
        "timestamp": datetime.now().isoformat(),
        "total_cost": result.get("total_cost", 0),
        "total_tokens": result.get("total_tokens", 0),
        "queries_count": len(result.get("queries", [])),
        "sources_count": len(result.get("search_results", [])),
    }
    metrics_path = company_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Save extracted data
    extracted = result.get("extracted_data", {})
    if extracted:
        data_path = company_dir / "extracted_data.json"
        data_path.write_text(json.dumps(extracted, indent=2), encoding="utf-8")

    return company_dir


def run_graph_research(company_name: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Run research using LangGraph workflow.

    This uses src.company_researcher.graphs.research_graph directly.
    """
    print(f"\n{'='*60}")
    print(f"  LangGraph Research: {company_name}")
    print(f"{'='*60}\n")

    # Initialize state
    initial_state = {
        "company_name": company_name,
        "queries": [],
        "search_results": [],
        "extracted_data": {},
        "report": "",
        "total_cost": 0.0,
        "total_tokens": 0,
        "error": None,
    }

    # Run the graph
    result = research_graph.invoke(initial_state)

    if verbose:
        print(f"\nQueries generated: {len(result.get('queries', []))}")
        print(f"Search results: {len(result.get('search_results', []))}")
        print(f"Total cost: ${result.get('total_cost', 0):.4f}")
        print(f"Total tokens: {result.get('total_tokens', 0)}")

    return result


def run_orchestration_research(
    company_name: str, depth: ResearchDepth, verbose: bool = False
) -> Dict[str, Any]:
    """
    Run research using orchestration engine.

    This uses src.company_researcher.orchestration.execute_research.
    """
    print(f"\n{'='*60}")
    print(f"  Orchestration Research: {company_name}")
    print(f"  Depth: {depth.value}")
    print(f"{'='*60}\n")

    # Execute research
    result = execute_research(company_name=company_name, depth=depth)

    # Convert WorkflowState to dict
    return {
        "company_name": company_name,
        "status": result.status.value,
        "duration_seconds": result.duration_seconds,
        "total_cost": result.total_cost,
        "completed_nodes": list(result.completed_nodes),
        "data": result.data,
        "report": result.data.get("synthesis", {}).get("summary", ""),
    }


def load_company_profile(profile_path: str) -> Dict[str, Any]:
    """Load company profile from YAML file."""
    with open(profile_path) as f:
        return yaml.safe_load(f)


def get_market_companies(market_path: str) -> List[Dict[str, Any]]:
    """Get all company profiles from a market directory."""
    market_dir = Path(market_path)
    companies = []

    for yaml_file in market_dir.glob("*.yaml"):
        if yaml_file.name.startswith("_"):  # Skip meta files
            continue
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                if data and "name" in data:
                    companies.append(data)
        except Exception as e:
            print(f"Warning: Could not load {yaml_file}: {e}")

    return companies


async def run_cli(args: argparse.Namespace) -> int:
    """Run the CLI with parsed arguments."""

    # Handle utility options
    if args.show_config:
        try:
            config = get_src_config()
            print("\n[CONFIGURATION] src.company_researcher config:")
            print("=" * 60)
            print(f"  LLM Model: {getattr(config, 'llm_model', 'default')}")
            print(f"  Max tokens: {getattr(config, 'max_tokens', 4096)}")
            print(f"  Results per query: {getattr(config, 'search_results_per_query', 5)}")
            print(f"  Anthropic API: {'configured' if config.anthropic_api_key else 'not set'}")
            print(f"  Tavily API: {'configured' if config.tavily_api_key else 'not set'}")
            print("=" * 60)
        except Exception as e:
            print(f"[WARNING] Could not load src config: {e}")
        return 0

    # Require input option
    if not (args.company or args.profile or args.market):
        print("[ERROR] One of --company, --profile, or --market is required")
        print("       Use --help for usage information")
        return 1

    # Determine research method
    use_graph = args.use_graph
    depth = get_depth_enum(args.depth)
    output_dir = args.output
    verbose = args.verbose

    # Handle single company
    if args.company:
        company_name = args.company

        if args.dry_run:
            print(f"[DRY-RUN] Would research: {company_name}")
            print(f"          Depth: {args.depth}")
            print(f"          Method: {'LangGraph' if use_graph else 'Orchestration'}")
            print(f"          Output: {output_dir}")
            return 0

        try:
            if use_graph:
                result = run_graph_research(company_name, verbose)
            else:
                result = run_orchestration_research(company_name, depth, verbose)

            # Save report
            report_dir = save_report(company_name, result, output_dir)
            print(f"\n✅ Research complete: {report_dir}")
            return 0

        except Exception as e:
            print(f"\n❌ Research failed: {e}")
            if verbose:
                import traceback

                traceback.print_exc()
            return 1

    # Handle profile
    elif args.profile:
        profile = load_company_profile(args.profile)
        company_name = profile.get("name", "Unknown")

        if args.dry_run:
            print(f"[DRY-RUN] Would research from profile: {args.profile}")
            print(f"          Company: {company_name}")
            return 0

        try:
            if use_graph:
                result = run_graph_research(company_name, verbose)
            else:
                result = run_orchestration_research(company_name, depth, verbose)

            report_dir = save_report(company_name, result, output_dir)
            print(f"\n✅ Research complete: {report_dir}")
            return 0

        except Exception as e:
            print(f"\n❌ Research failed: {e}")
            return 1

    # Handle market
    elif args.market:
        companies = get_market_companies(args.market)

        if not companies:
            print(f"[ERROR] No company profiles found in {args.market}")
            return 1

        if args.dry_run:
            print(f"[DRY-RUN] Would research {len(companies)} companies:")
            for c in companies:
                print(f"          - {c.get('name', 'Unknown')}")
            return 0

        print(f"\n📊 Market Research: {len(companies)} companies")
        print("=" * 60)

        results = []
        for company in companies:
            company_name = company.get("name", "Unknown")
            print(f"\n→ Researching: {company_name}")

            try:
                if use_graph:
                    result = run_graph_research(company_name, verbose)
                else:
                    result = run_orchestration_research(company_name, depth, verbose)

                save_report(company_name, result, output_dir)
                results.append({"company": company_name, "success": True})

            except Exception as e:
                print(f"  ❌ Failed: {e}")
                results.append({"company": company_name, "success": False, "error": str(e)})

        # Summary
        successful = sum(1 for r in results if r["success"])
        print(f"\n{'='*60}")
        print(f"  Market Research Complete")
        print(f"  Success: {successful}/{len(results)}")
        print(f"{'='*60}")

        return 0 if successful == len(results) else 1

    return 1


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        exit_code = asyncio.run(run_cli(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Research cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
