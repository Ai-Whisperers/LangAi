#!/usr/bin/env python
"""
Batch Company Research CLI

Research multiple companies in parallel with caching and comparative analysis.

Usage:
    # Research companies from command line
    python scripts/batch_research.py Tesla Apple Microsoft Amazon

    # Research from file
    python scripts/batch_research.py --file companies.txt

    # Custom output directory
    python scripts/batch_research.py --output outputs/my_batch Tesla Apple

    # Control parallel workers
    python scripts/batch_research.py --workers 10 Tesla Apple Microsoft

Examples:
    # Quick comparison of tech giants
    python scripts/batch_research.py Apple Microsoft Google Amazon

    # Batch research from list
    echo "Tesla\nRivian\nLucid Motors" > ev_companies.txt
    python scripts/batch_research.py --file ev_companies.txt
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.company_researcher.batch import BatchResearcher


def load_companies_from_file(file_path: str) -> list:
    """Load company names from text file (one per line)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        companies = [line.strip() for line in f if line.strip()]
    return companies


def main():
    parser = argparse.ArgumentParser(
        description="Batch Company Research - Research multiple companies in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s Tesla Apple Microsoft Amazon
  %(prog)s --file companies.txt
  %(prog)s --workers 10 --output results/ Tesla Apple
        """
    )

    parser.add_argument(
        'companies',
        nargs='*',
        help='Company names to research (space-separated)'
    )
    parser.add_argument(
        '-f', '--file',
        help='Load company names from file (one per line)'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='Maximum parallel workers (default: 5)'
    )
    parser.add_argument(
        '-o', '--output',
        default='outputs/batch',
        help='Output directory (default: outputs/batch)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout per company in seconds (default: 300)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to disk'
    )
    parser.add_argument(
        '--enhanced',
        action='store_true',
        help='Use enhanced research workflow (if available)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    parser.add_argument(
        '--no-quality-check',
        action='store_true',
        help='Disable quality checking (faster but no quality metrics)'
    )
    parser.add_argument(
        '--quality-threshold',
        type=float,
        default=70.0,
        help='Quality score threshold for flagging low quality (default: 70)'
    )

    args = parser.parse_args()

    # Get company list
    companies = []

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        companies = load_companies_from_file(args.file)
        print(f"Loaded {len(companies)} companies from {args.file}")

    if args.companies:
        companies.extend(args.companies)

    if not companies:
        parser.print_help()
        print("\nError: No companies specified. Use either positional arguments or --file")
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    companies = [c for c in companies if not (c in seen or seen.add(c))]

    print("=" * 60)
    print("  Batch Company Research")
    print("=" * 60)
    print(f"\nCompanies to research: {len(companies)}")
    print(f"Parallel workers: {args.workers}")
    print(f"Output directory: {args.output}")
    print(f"Enhanced workflow: {'Yes' if args.enhanced else 'No'}")
    print(f"Quality checking: {'Yes' if not args.no_quality_check else 'No'}")
    if not args.no_quality_check:
        print(f"Quality threshold: {args.quality_threshold}/100")
    print("\n" + "=" * 60 + "\n")

    # Initialize researcher
    researcher = BatchResearcher(
        max_workers=args.workers,
        timeout_per_company=args.timeout,
        enable_quality_check=not args.no_quality_check,
        quality_threshold=args.quality_threshold
    )

    # Execute batch research
    try:
        result = researcher.research_batch(
            companies=companies,
            use_enhanced_workflow=args.enhanced,
            show_progress=not args.quiet
        )

        print("\n" + "=" * 60)
        print("  Batch Research Complete!")
        print("=" * 60)

        # Print summary
        summary = result.get_summary()
        print(f"\n✅ Successful: {summary['successful']}/{summary['total_companies']}")
        print(f"❌ Failed: {summary['failed']}/{summary['total_companies']}")
        print(f"\n💰 Total Cost: ${summary['total_cost']}")
        print(f"   Avg Cost/Company: ${summary['avg_cost_per_company']}")
        print(f"\n⚡ Total Duration: {summary['duration_seconds']:.1f}s")
        print(f"   Avg Duration/Company: {summary['avg_duration_per_company']:.1f}s")
        print(f"\n📦 Cache Hit Rate: {summary['cache_hit_rate']:.1%} ({summary['cache_hits']}/{summary['total_companies']})")

        # Quality metrics
        if not args.no_quality_check and summary.get('avg_quality_score', 0) > 0:
            print(f"\n📊 Avg Quality Score: {summary['avg_quality_score']:.1f}/100")
            if summary['low_quality_count'] > 0:
                print(f"⚠️  Low Quality Reports: {summary['low_quality_count']}/{summary['successful']}")

        # Save results
        if not args.no_save:
            output_dir = researcher.save_batch_results(result, output_dir=args.output)
            print(f"\n📁 Results saved to: {output_dir}")
            print(f"   - Comparison report: {output_dir}/00_comparison.md")
            print(f"   - Individual reports: {output_dir}/<company_name>.md")
            print(f"   - Summary JSON: {output_dir}/summary.json")
            if not args.no_quality_check and summary.get('low_quality_count', 0) > 0:
                print(f"   - Quality issues report: {output_dir}/quality_issues.md")

        print("\n" + "=" * 60 + "\n")

        # Return exit code based on success rate
        if result.failure_count > 0:
            sys.exit(1)  # Partial failure
        else:
            sys.exit(0)  # Full success

    except KeyboardInterrupt:
        print("\n\n⚠️  Batch research interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error during batch research: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
