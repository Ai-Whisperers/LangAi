#!/usr/bin/env python3
"""
Repository entrypoint for running research from the command line.

This file exists so documentation can use a stable command:
  python run_research.py --company "Microsoft"
"""

from scripts.research.cli import main

if __name__ == "__main__":
    main()
