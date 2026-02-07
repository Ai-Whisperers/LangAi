#!/usr/bin/env python
"""
LangFlow Visual Workflow Builder Launcher.

Starts the LangFlow server with Company Researcher custom components.

Usage:
    python start_langflow.py
    python start_langflow.py --port 7861
    python start_langflow.py --no-browser

Access the UI at: http://localhost:7860 (default)
"""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def check_langflow_installed():
    """Check if LangFlow is installed."""
    try:
        import langflow

        return True, getattr(langflow, "__version__", "unknown")
    except ImportError:
        return False, None


def start_langflow(port: int = 7860, host: str = "127.0.0.1", open_browser: bool = True):
    """Start LangFlow server with custom components."""

    installed, version = check_langflow_installed()

    if not installed:
        print("\n" + "=" * 60)
        print("LangFlow is not installed!")
        print("=" * 60)
        print("\nInstall with:")
        print("  pip install langflow")
        print("\nOr for full installation:")
        print("  pip install langflow[all]")
        print("=" * 60 + "\n")
        return False

    print("\n" + "=" * 60)
    print(f"Starting LangFlow v{version}")
    print("=" * 60)
    print(f"\n  Host: {host}")
    print(f"  Port: {port}")
    print(f"  URL:  http://{host}:{port}")
    print("\n  Custom Components: Company Researcher Agents")
    print("  - ResearcherAgent")
    print("  - FinancialAgent")
    print("  - MarketAgent")
    print("  - ProductAgent")
    print("  - SynthesizerAgent")
    print("  - CompetitorScout")
    print("  - QualityChecker")
    print("\n  Pre-built Flows (import from LangFlow UI):")

    flows_dir = project_root / "src" / "company_researcher" / "langflow" / "flows"
    if flows_dir.exists():
        for flow_file in flows_dir.glob("*.json"):
            print(f"    - {flow_file.name}")

    print("\n" + "=" * 60)
    print("Starting server... (Ctrl+C to stop)")
    print("=" * 60 + "\n")

    # Set environment variables
    os.environ.setdefault("LANGFLOW_HOST", host)
    os.environ.setdefault("LANGFLOW_PORT", str(port))

    # Components path
    components_path = project_root / "src" / "company_researcher" / "langflow" / "components.py"

    try:
        from langflow.__main__ import main

        # Build arguments
        sys.argv = [
            "langflow",
            "run",
            "--host",
            host,
            "--port",
            str(port),
        ]

        if components_path.exists():
            sys.argv.extend(["--components-path", str(components_path)])

        if not open_browser:
            sys.argv.append("--no-open-browser")

        # Run LangFlow
        main()

    except KeyboardInterrupt:
        print("\n\nLangFlow server stopped.")
    except Exception as e:
        print(f"\nError starting LangFlow: {e}")
        print("\nTry running directly with:")
        print(f"  langflow run --port {port}")
        return False

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start LangFlow with Company Researcher components"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=7860, help="Port to run LangFlow on (default: 7860)"
    )
    parser.add_argument(
        "--host", "-H", type=str, default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    args = parser.parse_args()

    start_langflow(port=args.port, host=args.host, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
