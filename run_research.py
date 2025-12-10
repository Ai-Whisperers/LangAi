#!/usr/bin/env python3
"""
Comprehensive Company Research Runner.

This is the main entry point for the research system.
The implementation has been modularized into scripts/research/.

Full-featured research runner that utilizes all system capabilities:
- Batch processing from YAML input files
- All analysis agents (financial, market, competitive, news, brand, etc.)
- Multiple output formats (Markdown, PDF, Excel, PowerPoint)
- Comparison reports for market analysis
- Organized output structure with separate folders

Usage:
    # Research single company
    python run_research.py --company "Tesla"

    # Research from YAML profile
    python run_research.py --profile research_targets/paraguay_telecom/tigo_paraguay.yaml

    # Research all companies in a market folder
    python run_research.py --market research_targets/paraguay_telecom/

    # Research with specific output formats
    python run_research.py --market research_targets/paraguay_telecom/ --formats md,pdf,excel

    # Generate comparison report
    python run_research.py --market research_targets/paraguay_telecom/ --compare

For more options:
    python run_research.py --help

Author: AI Research System
Version: 2.0.0 (Modularized)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run from modular structure
from scripts.research.cli import main

if __name__ == "__main__":
    main()
