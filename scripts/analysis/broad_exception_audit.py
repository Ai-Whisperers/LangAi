"""
Broad exception audit.

Scans Python files for:
- `except Exception:` and `except Exception as e:`
- bare `except:` (catch-all)

This supports P0 quality work: progressively reducing broad exception handling
and improving diagnostic quality (WHAT/WHY/HOW).
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str  # "except_exception" | "bare_except"


def _iter_py_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        # Skip obvious generated/third-party dirs
        parts = {x.lower() for x in p.parts}
        if any(x in parts for x in ("venv", ".venv", "__pycache__", ".git", ".archive")):
            continue
        yield p


def _find_broad_excepts(path: Path) -> List[Finding]:
    try:
        src = path.read_text(encoding="utf-8")
    except OSError:
        return []
    except UnicodeError:
        return []

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return []

    findings: List[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            # bare except:
            if handler.type is None:
                findings.append(Finding(str(path), int(handler.lineno or 0), "bare_except"))
                continue
            # except Exception:
            if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                findings.append(Finding(str(path), int(handler.lineno or 0), "except_exception"))
                continue
    return findings


def _summarize(findings: List[Finding]) -> List[Tuple[str, int]]:
    counts = {}
    for f in findings:
        counts[f.path] = counts.get(f.path, 0) + 1
    return sorted(counts.items(), key=lambda t: t[1], reverse=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit broad exception handling in Python files")
    parser.add_argument("--path", type=str, default="src", help="Root path to scan")
    parser.add_argument("--top", type=int, default=30, help="Show top N files")
    parser.add_argument("--json", dest="json_out", type=str, default="", help="Write JSON report")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")

    findings: List[Finding] = []
    for py in _iter_py_files(root):
        findings.extend(_find_broad_excepts(py))

    summary = _summarize(findings)
    total = len(findings)
    except_exception = sum(1 for f in findings if f.kind == "except_exception")
    bare_except = sum(1 for f in findings if f.kind == "bare_except")

    print(f"Broad exception audit: path={root}")
    print(f"  total_findings={total} except Exception={except_exception} bare except={bare_except}")
    print("")
    print(f"Top {min(args.top, len(summary))} files:")
    for path, cnt in summary[: max(0, int(args.top))]:
        print(f"  {cnt:5d}  {path}")

    if args.json_out:
        out_path = Path(args.json_out).resolve()
        payload = {
            "path": str(root),
            "total": total,
            "except_exception": except_exception,
            "bare_except": bare_except,
            "summary": [{"path": p, "count": c} for p, c in summary],
            "findings": [f.__dict__ for f in findings],
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
