#!/usr/bin/env python3
"""
Validate Prompt Registry collection manifests.

Checks:
- YAML parses
- Required fields exist: id, name, description, items
- Each item has: path, kind
- Each referenced prompt file exists relative to `.cursor/prompts/`

Usage:
  python .cursor/scripts/validate-prompt-collections.py
  python .cursor/scripts/validate-prompt-collections.py --root .cursor/prompts
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Issue:
    file: Path
    message: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate Prompt Registry collection manifests.")
    p.add_argument(
        "--root",
        default=".cursor/prompts",
        help="Prompt library root (default: .cursor/prompts).",
    )
    return p.parse_args(argv)


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate_collection_file(collection_file: Path, prompts_root: Path) -> list[Issue]:
    issues: list[Issue] = []

    try:
        data = yaml.safe_load(collection_file.read_text(encoding="utf-8"))
    except Exception as ex:  # noqa: BLE001
        return [Issue(collection_file, f"Invalid YAML: {ex}")]

    if not isinstance(data, dict):
        return [Issue(collection_file, "Root YAML must be a mapping/object.")]

    for required in ("id", "name", "description", "items"):
        if required not in data:
            issues.append(Issue(collection_file, f"Missing required field '{required}'."))

    items = data.get("items", [])
    if not isinstance(items, list):
        issues.append(Issue(collection_file, "Field 'items' must be a YAML list."))
        return issues

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append(Issue(collection_file, f"items[{idx}] must be a mapping/object."))
            continue

        path = item.get("path")
        kind = item.get("kind")

        if not isinstance(path, str) or not path.strip():
            issues.append(Issue(collection_file, f"items[{idx}].path must be a non-empty string."))
            continue
        if not isinstance(kind, str) or not kind.strip():
            issues.append(Issue(collection_file, f"items[{idx}].kind must be a non-empty string."))
            continue

        resolved = (prompts_root / path).resolve()
        if not resolved.exists():
            issues.append(
                Issue(
                    collection_file,
                    f"Missing referenced file: items[{idx}].path='{path}' (expected at '{resolved}').",
                )
            )
            continue

        if kind == "prompt":
            if not resolved.name.endswith(".prompt.md"):
                issues.append(
                    Issue(
                        collection_file,
                        f"items[{idx}].path='{path}' should end with '.prompt.md' for kind=prompt.",
                    )
                )

    return issues


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    prompts_root = Path(args.root)
    collections_dir = prompts_root / "collections"

    if not collections_dir.exists():
        sys.stderr.write(f"ERROR: collections dir not found: {collections_dir}\n")
        return 1

    collection_files = sorted(collections_dir.glob("*.collection.yml"))
    if not collection_files:
        print(f"INFO: No collection files found under {collections_dir}")
        return 0

    all_issues: list[Issue] = []
    for f in collection_files:
        all_issues.extend(validate_collection_file(f, prompts_root))

    if all_issues:
        print(f"ERROR: Prompt collection validation failed ({len(all_issues)} issue(s)).\n")
        for issue in all_issues:
            print(f"- {issue.file}: {issue.message}")
        return 1

    print(f"OK: All prompt collections are valid ({len(collection_files)} collection file(s) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


