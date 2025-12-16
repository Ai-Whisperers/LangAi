"""
Default entrypoint for `python -m scripts.analysis`.

Runs the repo audit to keep a single standard command for diagnostics.
"""

from __future__ import annotations

import runpy


def main() -> None:
    runpy.run_module("scripts.analysis.repo_audit", run_name="__main__")


if __name__ == "__main__":
    main()
