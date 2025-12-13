#!/usr/bin/env python
"""
Comprehensive Research Runner for Personal Paraguay.

Uses ALL available features:
- Autonomous Discovery (learns from previous research)
- Multilingual Search Generator
- Multiple analysis agents (Core, Financial, Market, ESG, Brand, News)
- Quality checks with contradiction detection, confidence scoring
- Competitive matrix generation
- Risk assessment and investment thesis
- Comprehensive report generation
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set comprehensive research parameters
os.environ['NUM_SEARCH_QUERIES'] = '25'  # More queries
os.environ['SEARCH_RESULTS_PER_QUERY'] = '10'  # More results per query
os.environ['MAX_SEARCH_RESULTS'] = '150'  # Higher cap
os.environ['MAX_RESEARCH_TIME_SECONDS'] = '600'  # 10 minutes
os.environ['QUALITY_TARGET'] = '85'  # Target quality score
os.environ['MAX_ITERATIONS'] = '2'  # Quality iterations

from dotenv import load_dotenv
load_dotenv()

def main():
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE PERSONAL PARAGUAY RESEARCH")
    print("  Using ALL Features & Latest Implementations")
    print("=" * 70)
    print(f"  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Check for required API keys (check for alternatives to Anthropic)
    has_groq = bool(os.getenv('GROQ_API_KEY'))
    has_deepseek = bool(os.getenv('DEEPSEEK_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_tavily = bool(os.getenv('TAVILY_API_KEY'))
    has_serper = bool(os.getenv('SERPER_API_KEY'))

    print("API Keys Status:")
    print(f"  - Groq:     {'OK' if has_groq else 'Missing'}")
    print(f"  - DeepSeek: {'OK' if has_deepseek else 'Missing'}")
    print(f"  - OpenAI:   {'OK' if has_openai else 'Missing'}")
    print(f"  - Tavily:   {'OK' if has_tavily else 'Missing'}")
    print(f"  - Serper:   {'OK' if has_serper else 'Missing'}")

    if not (has_groq or has_deepseek or has_openai):
        print("\nERROR: No LLM provider configured (need GROQ_API_KEY, DEEPSEEK_API_KEY, or OPENAI_API_KEY)")
        sys.exit(1)

    if not (has_tavily or has_serper):
        print("\nWARNING: No search API configured - using DuckDuckGo fallback")

    print("\n" + "-" * 70)
    print("Starting comprehensive research workflow...")
    print("-" * 70 + "\n")

    try:
        # Import the comprehensive workflow
        from src.company_researcher.workflows.comprehensive_research import research_company_comprehensive

        # Run comprehensive research for Personal Paraguay
        result = research_company_comprehensive("Personal Paraguay")

        # Print results
        print("\n" + "=" * 70)
        print("  RESEARCH COMPLETE")
        print("=" * 70)
        print(f"\nReport saved to: {result.get('report_path', 'N/A')}")
        print(f"\nMetrics:")
        metrics = result.get('metrics', {})
        print(f"  - Duration:      {metrics.get('duration_seconds', 0):.1f} seconds")
        print(f"  - Quality Score: {metrics.get('quality_score', 0):.1f}/100")
        print(f"  - Total Cost:    ${metrics.get('cost_usd', 0):.4f}")
        print(f"  - Sources Used:  {metrics.get('sources_count', 0)}")

        # Show any errors
        if result.get('error'):
            print(f"\nErrors: {result['error']}")

        print("\n" + "=" * 70)
        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
