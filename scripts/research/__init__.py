"""
Research CLI Package.

Thin CLI wrapper that uses src.company_researcher as the complete research engine.
This package only provides the command-line interface.

Usage:
    python -m scripts.research.cli --company "Tesla"
    python -m scripts.research.cli --help

All research logic, agents, workflows, and tools are in src/company_researcher.
"""

from .cli import create_argument_parser, main

__all__ = ["main", "create_argument_parser"]
