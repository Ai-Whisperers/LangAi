"""
Research CLI Module.

Command-line interface for the comprehensive research runner.
Settings are loaded from research_config.yaml - edit that file to change defaults.
"""

import argparse
import asyncio
import sys
import yaml
from pathlib import Path

from .config import CompanyProfile
from .config_loader import load_config, get_config


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the research CLI."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Company Research Runner (settings from research_config.yaml)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Settings:
  All settings are loaded from scripts/research/research_config.yaml
  Edit that file to change defaults (search strategy, output folder, etc.)

Examples:
  # Research single company (uses config file settings)
  python run_research.py --company "Tesla"

  # Research from YAML profile
  python run_research.py --profile research_targets/company.yaml

  # Research all companies in a market folder
  python run_research.py --market research_targets/paraguay_telecom/

  # Override depth for this run only
  python run_research.py --company "Apple" --depth quick

  # Force refresh (ignore cache and previous research)
  python run_research.py --company "Microsoft" --force-refresh

  # Use Tavily-first strategy for this run
  python run_research.py --company "Google" --tavily-first
"""
    )

    # Input options
    input_group = parser.add_argument_group("Input Options (required)")
    input_group.add_argument(
        "--company", "-c",
        type=str,
        help="Company name to research (or path to YAML file)"
    )
    input_group.add_argument(
        "--profile", "-p",
        type=str,
        help="Path to company YAML profile"
    )
    input_group.add_argument(
        "--market", "-m",
        type=str,
        help="Path to market folder with YAML files"
    )

    # Override options (optional - uses config file by default)
    override_group = parser.add_argument_group("Override Options (optional - config file is default)")
    override_group.add_argument(
        "--depth", "-d",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        help="Override research depth (default from config)"
    )
    override_group.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh (ignore cache and previous research)"
    )
    override_group.add_argument(
        "--tavily-first",
        action="store_true",
        help="Use Tavily-first strategy (original behavior)"
    )
    override_group.add_argument(
        "--no-gap-fill",
        action="store_true",
        help="Disable iterative gap-filling"
    )
    override_group.add_argument(
        "--compare",
        action="store_true",
        help="Generate comparison report for market research"
    )

    # Utility options
    util_group = parser.add_argument_group("Utility Options")
    util_group.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration and exit"
    )
    util_group.add_argument(
        "--show-previous",
        action="store_true",
        help="Show previous research status and exit"
    )

    return parser


async def run_research_cli(args: argparse.Namespace) -> int:
    """
    Run research based on CLI arguments.

    Settings are loaded from research_config.yaml with optional CLI overrides.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Import here to avoid circular imports
    from .researcher import ComprehensiveResearcher
    from .research_memory import create_research_memory

    # Load config file
    cfg = get_config()

    # Handle utility options
    if args.show_config:
        print("\n[CONFIGURATION] Current settings from research_config.yaml:")
        print("=" * 60)
        print(f"  Output directory: {cfg.output.base_dir}")
        print(f"  Output formats: {cfg.output.formats}")
        print(f"  Research depth: {cfg.depth}")
        print(f"  Search strategy: {cfg.search.strategy}")
        print(f"  Min free sources: {cfg.search.min_free_sources}")
        print(f"  Tavily refinement: {cfg.search.tavily_refinement}")
        print(f"  Gap-filling enabled: {cfg.gap_filling.enabled}")
        print(f"  Max iterations: {cfg.gap_filling.max_iterations}")
        print(f"  Min quality score: {cfg.gap_filling.min_quality_score}")
        print(f"  Cache enabled: {cfg.cache.enabled}")
        print(f"  Reuse previous research: {cfg.cache.reuse_previous_research}")
        print(f"  Max previous age (days): {cfg.cache.max_previous_age_days}")
        print("=" * 60)
        return 0

    if args.show_previous:
        memory = create_research_memory(
            output_base=cfg.output.base_dir,
            max_age_days=cfg.cache.max_previous_age_days,
        )
        memory.print_status()
        return 0

    # Require input option
    if not (args.company or args.profile or args.market):
        print("[ERROR] One of --company, --profile, or --market is required")
        print("       Use --show-config to see current settings")
        print("       Use --show-previous to see previous research status")
        return 1

    # Apply CLI overrides to config
    search_strategy = cfg.search.strategy
    if args.tavily_first:
        search_strategy = "auto"  # Original Tavily-first behavior

    fill_gaps = cfg.gap_filling.enabled
    if args.no_gap_fill:
        fill_gaps = False

    force_refresh = cfg.cache.force_refresh or args.force_refresh

    # Show config info
    print(f"\n[CONFIG] Settings from research_config.yaml:")
    print(f"         Output: {cfg.output.base_dir}")
    print(f"         Strategy: {search_strategy.upper()}")
    print(f"         Min sources: {cfg.search.min_free_sources}")
    print(f"         Reuse previous: {cfg.cache.reuse_previous_research}")

    # Create researcher (uses config file automatically)
    researcher = ComprehensiveResearcher(
        depth=args.depth,  # CLI override if provided
        force_refresh=force_refresh,
        fill_gaps=fill_gaps,
        search_strategy=search_strategy,
    )

    # Execute based on input type
    import os

    if args.company:
        # Single company - check if it's a YAML file path or plain name
        if args.company.endswith(('.yaml', '.yml')) and os.path.exists(args.company):
            with open(args.company) as f:
                data = yaml.safe_load(f)
            profile = CompanyProfile.from_yaml(data)
            result = await researcher.research_company(profile.name, profile)
        else:
            result = await researcher.research_company(args.company)
        return 0 if result.success else 1

    elif args.profile:
        with open(args.profile) as f:
            data = yaml.safe_load(f)
        profile = CompanyProfile.from_yaml(data)
        result = await researcher.research_company(profile.name, profile)
        return 0 if result.success else 1

    elif args.market:
        generate_comparison = args.compare or cfg.output.generate_comparison
        results = await researcher.research_market(
            args.market,
            generate_comparison=generate_comparison
        )
        successful = sum(1 for r in results if r.success)
        return 0 if successful == len(results) else 1

    return 1


async def main() -> int:
    """Main entry point for the research CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()
    return await run_research_cli(args)


def run():
    """Synchronous entry point."""
    try:
        exit_code = asyncio.run(main())
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
    run()
