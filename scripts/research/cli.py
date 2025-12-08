"""
Research CLI Module.

Command-line interface for the comprehensive research runner.
"""

import argparse
import asyncio
import sys
import yaml
from pathlib import Path
from typing import Optional

from .config import CompanyProfile


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the research CLI."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Company Research Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research single company
  python run_research.py --company "Tesla"

  # Research from YAML profile
  python run_research.py --profile research_targets/company.yaml

  # Research all companies in a market folder
  python run_research.py --market research_targets/paraguay_telecom/

  # Research with specific output formats
  python run_research.py --market research_targets/telecom/ --formats md,pdf,excel

  # Generate comparison report
  python run_research.py --market research_targets/telecom/ --compare
"""
    )

    # Input options (mutually exclusive group)
    input_group = parser.add_argument_group("Input Options")
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

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output", "-o",
        type=str,
        default="outputs/research",
        help="Output directory for reports (default: outputs/research)"
    )
    output_group.add_argument(
        "--formats", "-f",
        type=str,
        default="md",
        help="Output formats (comma-separated): md,pdf,excel (default: md)"
    )

    # Research options
    research_group = parser.add_argument_group("Research Options")
    research_group.add_argument(
        "--depth", "-d",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="comprehensive",
        help="Research depth (default: comprehensive)"
    )
    research_group.add_argument(
        "--compare",
        action="store_true",
        help="Generate comparison report for market research"
    )
    research_group.add_argument(
        "--no-compare",
        action="store_true",
        help="Skip comparison report for market research"
    )

    # Cache options
    cache_group = parser.add_argument_group("Cache Options")
    cache_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable search result caching"
    )
    cache_group.add_argument(
        "--cache-ttl",
        type=int,
        default=7,
        help="Cache TTL in days (default: 7)"
    )
    cache_group.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh of cached data"
    )
    cache_group.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics and exit"
    )
    cache_group.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the research cache and exit"
    )

    return parser


async def run_research_cli(args: argparse.Namespace) -> int:
    """
    Run research based on CLI arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Import here to avoid circular imports
    from .researcher import ComprehensiveResearcher

    # Handle cache operations
    if args.cache_stats or args.clear_cache:
        try:
            from src.company_researcher.cache import create_cache
            cache = create_cache(
                cache_dir=Path(args.output) / ".cache",
                ttl_days=args.cache_ttl,
                enabled=True
            )

            if args.cache_stats:
                stats = cache.get_stats()
                print("\n[CACHE STATISTICS]")
                print(f"  Total entries: {stats.get('total_entries', 0)}")
                print(f"  Cache size: {stats.get('size_mb', 0):.2f} MB")
                print(f"  Hit rate: {stats.get('hit_rate', 0):.1%}")
                return 0

            if args.clear_cache:
                removed = cache.clear_all()
                print(f"[CACHE] Cleared {removed} cached entries")
                if not (args.company or args.profile or args.market):
                    return 0

        except ImportError:
            print("[WARNING] Cache module not available")
            if args.cache_stats or args.clear_cache:
                return 1

    # Require input option
    if not (args.company or args.profile or args.market):
        print("[ERROR] One of --company, --profile, or --market is required")
        print("       Use --cache-stats or --clear-cache for cache-only operations")
        return 1

    # Parse formats
    formats = [f.strip() for f in args.formats.split(",")]

    # Determine cache settings
    use_cache = not args.no_cache

    # Create researcher
    researcher = ComprehensiveResearcher(
        output_base=args.output,
        formats=formats,
        depth=args.depth,
        use_cache=use_cache,
        cache_ttl_days=args.cache_ttl,
        force_refresh=args.force_refresh
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
        generate_comparison = args.compare or not args.no_compare
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
