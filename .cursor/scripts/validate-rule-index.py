#!/usr/bin/env python3
"""
Validate `.cursor/rules/rule-index.yml`.

Checks:
- YAML parses
- Top-level sections exist
- All mapped file paths exist

Usage:
  python .cursor/scripts/validate-rule-index.py
  python .cursor/scripts/validate-rule-index.py --path .cursor/rules/rule-index.yml
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Issue:
    key: str
    message: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate Cursor rule-index.yml file.")
    p.add_argument("--path", default=".cursor/rules/rule-index.yml", help="Path to rule-index.yml.")
    return p.parse_args(argv)


def _iter_mappings(data: dict) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    for section in ("rules", "templars", "exemplars", "prompts"):
        raw = data.get(section)
        if isinstance(raw, dict):
            out.append((section, raw))
    return out


def validate_rule_index(rule_index_path: Path) -> tuple[list[Issue], int]:
    issues: list[Issue] = []

    try:
        data = yaml.safe_load(rule_index_path.read_text(encoding="utf-8"))
    except Exception as ex:  # noqa: BLE001
        return [Issue("rule-index", f"Invalid YAML: {ex}")], 0

    if not isinstance(data, dict):
        return [Issue("rule-index", "Root YAML must be a mapping/object.")], 0

    mappings = _iter_mappings(data)
    if not mappings:
        issues.append(Issue("rule-index", "No recognized sections found (expected one of: rules/templars/exemplars/prompts)."))
        return issues, 0

    base = rule_index_path.parent  # `.cursor/rules/`
    repo_root = rule_index_path.parents[2]
    checked = 0
    for section, mapping in mappings:
        for key, rel_path in mapping.items():
            checked += 1
            if not isinstance(rel_path, str) or not rel_path.strip():
                issues.append(Issue(key, f"{section}: path must be a non-empty string."))
                continue

            # Conventions in this repo:
            # - `rules:` entries are usually relative to `.cursor/rules/`
            # - `templars/exemplars/prompts:` entries are often absolute-from-repo-root
            #   and start with `.cursor/...`
            if rel_path.startswith(".cursor/") or rel_path.startswith(".cursor\\"):
                resolved = (repo_root / rel_path).resolve()
            else:
                resolved = (base / rel_path).resolve()
            if not resolved.exists():
                issues.append(Issue(key, f"{section}: missing file at '{resolved}'."))

    return issues, checked


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    rule_index_path = Path(args.path)
    if not rule_index_path.exists():
        sys.stderr.write(f"ERROR: rule-index.yml not found: {rule_index_path}\n")
        return 1

    issues, checked = validate_rule_index(rule_index_path)
    if issues:
        print(f"ERROR: rule-index validation failed ({len(issues)} issue(s), {checked} entry(ies) checked).\n")
        for issue in issues:
            print(f"- {issue.key}: {issue.message}")
        return 1

    print(f"OK: rule-index is valid ({checked} entry(ies) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
