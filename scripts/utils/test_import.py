#!/usr/bin/env python
"""Simple import test script."""
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    print("Testing utils import...")
    from src.company_researcher.utils import get_logger

    print("  utils import: SUCCESS")
except Exception as e:
    print(f"  utils import FAILED: {e}")

try:
    print("Testing ESG agent import...")
    from src.company_researcher.agents.esg.agent import ESGAgent

    print("  ESG agent import: SUCCESS")
except Exception as e:
    print(f"  ESG agent import FAILED: {e}")

try:
    print("Testing workflow import...")
    from src.company_researcher.workflows import research_company_comprehensive

    print("  workflow import: SUCCESS")
except Exception as e:
    print(f"  workflow import FAILED: {e}")

print("\nImport test complete.")
