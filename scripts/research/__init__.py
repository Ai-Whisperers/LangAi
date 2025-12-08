"""
Research Scripts Module.

Provides the comprehensive company research runner with:
- Batch processing from YAML input files
- Multiple analysis agents
- Multiple output formats (Markdown, PDF, Excel)
- Market comparison reports

Usage:
    from scripts.research import (
        ComprehensiveResearcher,
        CompanyProfile,
        MarketConfig,
        run_research_cli
    )
"""

from .config import (
    CompanyProfile,
    MarketConfig,
    ResearchResult,
    ResearchDepth,
)

from .researcher import ComprehensiveResearcher

from .cli import (
    create_argument_parser,
    run_research_cli,
    main,
)

__all__ = [
    # Configuration
    "CompanyProfile",
    "MarketConfig",
    "ResearchResult",
    "ResearchDepth",
    # Core
    "ComprehensiveResearcher",
    # CLI
    "create_argument_parser",
    "run_research_cli",
    "main",
]
