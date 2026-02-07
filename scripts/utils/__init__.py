"""
Scripts Utilities Package.

Consolidated utilities for repository maintenance:
- cleanup: Repository cleanup and analysis
- imports: Import validation and fixing
"""

from pathlib import Path

__all__ = ["cleanup", "imports"]

# Package root
SCRIPTS_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = SCRIPTS_ROOT.parent
