#!/usr/bin/env python3
"""
Validate YAML files.

Usage:
  python .cursor/scripts/validate-yaml.py [paths...] [--recurse] [--fail-fast]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def gather_files(paths: list[str], recurse: bool) -> list[Path]:
    files: list[Path] = []
    for raw in paths or ["."]:
        path = Path(raw)
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}:
            files.append(path.resolve())
        elif path.is_dir():
            globber = path.rglob if recurse else path.glob
            for f in globber("*.yml"):
                files.append(f.resolve())
            for f in globber("*.yaml"):
                files.append(f.resolve())
        else:
            raise FileNotFoundError(f"Path not found: {path}")
    # Remove duplicates while preserving order
    seen = set()
    unique: list[Path] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def validate_file(file_path: Path) -> tuple[bool, str | None]:
    try:
        text = file_path.read_text(encoding="utf-8")

        # Some YAML files in this repo are "templars" and intentionally contain
        # placeholders (e.g., {{PLACEHOLDER}}) that are not valid YAML. For those,
        # validate only the optional front-matter (if present) and skip the body.
        if "{{" in text or "}}" in text:
            if text.startswith("---\n"):
                end = text.find("\n---\n", 4)
                if end != -1:
                    front_matter = text[4:end]
                    yaml.safe_load(front_matter)
            return True, None

        # Support multi-document YAML streams (common when using front-matter-like
        # delimiters `---` plus a second YAML document body).
        list(yaml.safe_load_all(text))
        return True, None
    except Exception as ex:  # noqa: BLE001 - we want to report any parse error
        return False, str(ex)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate YAML files.")
    parser.add_argument(
        "paths", nargs="*", help="Files or directories to check (default: current directory)."
    )
    parser.add_argument("--recurse", action="store_true", help="Recurse into subdirectories.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after first failure.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        files = gather_files(args.paths, args.recurse)
    except FileNotFoundError as ex:
        sys.stderr.write(f"ERROR: {ex}\n")
        return 1

    if not files:
        print("INFO: No YAML files found.")
        return 0

    failures = 0
    for file_path in files:
        ok, message = validate_file(file_path)
        if ok:
            print(f"ok    {file_path}")
        else:
            failures += 1
            print(f"FAIL  {file_path}: {message}")
            if args.fail_fast:
                break

    if failures:
        print(
            f"\nERROR: YAML validation failed ({failures} invalid file{'s' if failures != 1 else ''})."
        )
        return 1

    print(f"\nOK: All YAML files are valid ({len(files)} checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
