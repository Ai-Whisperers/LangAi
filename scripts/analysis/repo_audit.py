"""
Repository audit generator.

This script generates two deliverables inside `housekeeping/reports/<timestamp>/`:
1) A detailed file/folder tree (excluding large/generated/vendor directories).
2) A repo-grounded improvements backlog with 1,000+ numbered items.

Usage:
    python scripts/analysis/repo_audit.py
    python scripts/analysis/repo_audit.py --max-depth 12 --items 1200
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence


DEFAULT_EXCLUDE_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "htmlcov",
    "external",
    "outputs",
}

WORK_SCOPE_DIR_PREFIXES = (
    "src/",
    "tests/",
    "scripts/",
    "docs/",
    "deploy/",
)

WORK_SCOPE_ROOT_FILES = (
    "README.md",
    "QUICK_START.md",
    "INSTALLATION.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "Makefile",
    "pyproject.toml",
    "pytest.ini",
    "requirements.txt",
    "requirements-dev.txt",
    "run_research.py",
    "langgraph.json",
    "env.example",
    "start_langgraph_studio.bat",
)


@dataclass(frozen=True)
class RepoStats:
    root: Path
    total_files: int
    total_dirs: int
    extension_counts: dict[str, int]
    largest_files: list[dict[str, object]]
    python_files: int
    test_files: int
    todo_markers: int
    print_calls: int
    broad_except: int


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _is_excluded_dir(dir_path: Path, *, exclude_dir_names: set[str], exclude_paths: Sequence[Path]) -> bool:
    if dir_path.name in exclude_dir_names:
        return True
    try:
        resolved = dir_path.resolve()
    except OSError:
        resolved = dir_path
    for p in exclude_paths:
        try:
            p_resolved = p.resolve()
        except OSError:
            p_resolved = p
        if resolved == p_resolved:
            return True
        try:
            resolved.relative_to(p_resolved)
            return True
        except ValueError:
            continue
    return False


def _walk_repo(
    root: Path, *, exclude_dir_names: set[str], exclude_paths: Sequence[Path]
) -> Iterator[tuple[Path, list[Path], list[Path]]]:
    """
    Yield (dir_path, subdirs, files) where subdirs/files are Path objects.
    Subdirs are filtered in-place to enforce exclusions.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dir_path = Path(dirpath)
        if _is_excluded_dir(dir_path, exclude_dir_names=exclude_dir_names, exclude_paths=exclude_paths):
            dirnames[:] = []
            continue

        # Filter subdirs before descending.
        keep_dirs: list[str] = []
        for d in dirnames:
            candidate = dir_path / d
            if not _is_excluded_dir(candidate, exclude_dir_names=exclude_dir_names, exclude_paths=exclude_paths):
                keep_dirs.append(d)
        dirnames[:] = keep_dirs

        subdirs = [dir_path / d for d in sorted(dirnames)]
        files = [dir_path / f for f in sorted(filenames)]
        yield dir_path, subdirs, files


def _format_bytes(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{int(num_bytes)}B"


def _render_tree(
    root: Path,
    *,
    exclude_dir_names: set[str],
    exclude_paths: Sequence[Path] = (),
    max_depth: int | None,
    include_file_sizes: bool,
    max_entries_per_dir: int | None,
) -> str:
    """
    Render a unix-style tree.

    Note: This is deterministic (sorted) and respects exclusions.
    """

    def iter_children(dir_path: Path) -> tuple[list[Path], list[Path]]:
        try:
            entries = list(dir_path.iterdir())
        except OSError:
            return [], []

        dirs = sorted(
            [
                p
                for p in entries
                if p.is_dir()
                and not _is_excluded_dir(p, exclude_dir_names=exclude_dir_names, exclude_paths=exclude_paths)
            ]
        )
        files = sorted([p for p in entries if p.is_file()])

        if max_entries_per_dir is not None:
            total = len(dirs) + len(files)
            if total > max_entries_per_dir:
                # Keep a balanced sample: dirs first (structure), then files.
                remaining = max_entries_per_dir
                dirs = dirs[: min(len(dirs), remaining)]
                remaining -= len(dirs)
                files = files[: max(0, remaining)]
        return dirs, files

    lines: list[str] = []
    lines.append(f"{root.name}/")

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        if max_depth is not None and depth >= max_depth:
            return

        dirs, files = iter_children(dir_path)
        children: list[tuple[Path, bool]] = [(d, True) for d in dirs] + [(f, False) for f in files]
        for idx, (child, is_dir) in enumerate(children):
            is_last = idx == len(children) - 1
            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            if is_dir:
                lines.append(f"{prefix}{connector}{child.name}/")
                walk(child, next_prefix, depth + 1)
            else:
                suffix = ""
                if include_file_sizes:
                    try:
                        suffix = f" ({_format_bytes(child.stat().st_size)})"
                    except OSError:
                        suffix = ""
                lines.append(f"{prefix}{connector}{child.name}{suffix}")

    walk(root, "", 0)
    return "\n".join(lines) + "\n"


def _iter_tree_lines(
    root: Path,
    *,
    exclude_dir_names: set[str],
    exclude_paths: Sequence[Path],
    max_depth: int | None,
    include_file_sizes: bool,
    max_entries_per_dir: int | None,
) -> Iterator[str]:
    """
    Yield a unix-style tree (streaming), suitable for very large repos.
    """

    def iter_children(dir_path: Path) -> tuple[list[Path], list[Path]]:
        try:
            entries = list(dir_path.iterdir())
        except OSError:
            return [], []

        dirs = sorted(
            [
                p
                for p in entries
                if p.is_dir()
                and not _is_excluded_dir(p, exclude_dir_names=exclude_dir_names, exclude_paths=exclude_paths)
            ]
        )
        files = sorted([p for p in entries if p.is_file()])

        if max_entries_per_dir is not None:
            total = len(dirs) + len(files)
            if total > max_entries_per_dir:
                remaining = max_entries_per_dir
                dirs = dirs[: min(len(dirs), remaining)]
                remaining -= len(dirs)
                files = files[: max(0, remaining)]
        return dirs, files

    yield f"{root.name}/\n"

    def walk(dir_path: Path, prefix: str, depth: int) -> Iterator[str]:
        if max_depth is not None and depth >= max_depth:
            return

        dirs, files = iter_children(dir_path)
        children: list[tuple[Path, bool]] = [(d, True) for d in dirs] + [(f, False) for f in files]
        for idx, (child, is_dir) in enumerate(children):
            is_last = idx == len(children) - 1
            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            if is_dir:
                yield f"{prefix}{connector}{child.name}/\n"
                yield from walk(child, next_prefix, depth + 1)
            else:
                suffix = ""
                if include_file_sizes:
                    try:
                        suffix = f" ({_format_bytes(child.stat().st_size)})"
                    except OSError:
                        suffix = ""
                yield f"{prefix}{connector}{child.name}{suffix}\n"

    yield from walk(root, "", 0)


def _write_tree_file(
    output_path: Path,
    *,
    root: Path,
    exclude_dir_names: set[str],
    exclude_paths: Sequence[Path],
    max_depth: int | None,
    include_file_sizes: bool,
    max_entries_per_dir: int | None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for line in _iter_tree_lines(
            root,
            exclude_dir_names=exclude_dir_names,
            exclude_paths=exclude_paths,
            max_depth=max_depth,
            include_file_sizes=include_file_sizes,
            max_entries_per_dir=max_entries_per_dir,
        ):
            f.write(line)


def _first_non_empty_line(lines: Sequence[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def _py_has_module_docstring(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    head = text.splitlines()[:25]
    # Remove shebang / encoding comments.
    cleaned: list[str] = []
    for line in head:
        if line.startswith("#!") or re.match(r"^#\s*coding[:=]", line):
            continue
        cleaned.append(line)
    first = _first_non_empty_line(cleaned)
    if first is None:
        return False
    return first.startswith('"""') or first.startswith("'''")


def _scan_text_markers(path: Path) -> tuple[int, int, int, list[int]]:
    """
    Returns:
        todo_count, print_count, broad_except_count, todo_line_numbers
    """
    todo_count = 0
    print_count = 0
    broad_except_count = 0
    todo_lines: list[int] = []
    todo_pattern = re.compile(r"\b(TODO|FIXME|HACK)\b")
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                if todo_pattern.search(line):
                    todo_count += 1
                    todo_lines.append(i)
                if "print(" in line:
                    print_count += 1
                if "except Exception" in line:
                    broad_except_count += 1
    except OSError:
        return 0, 0, 0, []
    return todo_count, print_count, broad_except_count, todo_lines


def _collect_stats(
    repo_root: Path,
    *,
    exclude_dir_names: set[str],
    exclude_paths: Sequence[Path] = (),
    include_roots: Sequence[Path] | None = None,
) -> tuple[RepoStats, dict[str, object]]:
    extension_counts: Counter[str] = Counter()
    largest_files: list[tuple[int, Path]] = []

    total_files = 0
    total_dirs = 0
    python_files = 0
    test_files = 0
    todo_markers = 0
    print_calls = 0
    broad_except = 0

    file_notes: dict[str, dict[str, object]] = {}
    seen_files: set[Path] = set()
    seen_dirs: set[Path] = set()

    roots = list(include_roots) if include_roots is not None else [repo_root]
    for root in roots:
        if not root.exists():
            continue
        for dir_path, subdirs, files in _walk_repo(
            root, exclude_dir_names=exclude_dir_names, exclude_paths=exclude_paths
        ):
            if dir_path not in seen_dirs:
                total_dirs += 1
                seen_dirs.add(dir_path)

            for file_path in files:
                if file_path in seen_files:
                    continue
                seen_files.add(file_path)

                if file_path.name == ".DS_Store":
                    continue
                total_files += 1
                extension_counts[file_path.suffix.lower() or "<noext>"] += 1
                try:
                    size = file_path.stat().st_size
                except OSError:
                    size = 0
                largest_files.append((size, file_path))

                try:
                    rel = str(file_path.relative_to(repo_root)).replace("\\", "/")
                except ValueError:
                    rel = str(file_path).replace("\\", "/")
                note: dict[str, object] = {"path": rel, "size_bytes": size}

                if file_path.suffix.lower() == ".py":
                    python_files += 1
                    note["has_module_docstring"] = _py_has_module_docstring(file_path)
                    tc, pc, bec, todo_lines = _scan_text_markers(file_path)
                    if rel.startswith("tests/") or "/tests/" in rel:
                        test_files += 1
                    todo_markers += tc
                    print_calls += pc
                    broad_except += bec
                    if tc:
                        note["todo_lines"] = todo_lines
                    if pc:
                        note["print_calls"] = pc
                    if bec:
                        note["broad_except"] = bec

                file_notes[rel] = note

    largest_files_sorted = sorted(largest_files, key=lambda x: x[0], reverse=True)[:50]
    largest_files_payload: list[dict[str, object]] = []
    for size, path in largest_files_sorted:
        largest_files_payload.append(
            {
                "path": str(path.relative_to(repo_root)).replace("\\", "/"),
                "size_bytes": size,
                "size_human": _format_bytes(size),
            }
        )

    stats = RepoStats(
        root=repo_root,
        total_files=total_files,
        total_dirs=total_dirs,
        extension_counts=dict(extension_counts),
        largest_files=largest_files_payload,
        python_files=python_files,
        test_files=test_files,
        todo_markers=todo_markers,
        print_calls=print_calls,
        broad_except=broad_except,
    )
    extra: dict[str, object] = {"file_notes": file_notes}
    return stats, extra


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _generate_improvements(
    repo_root: Path,
    *,
    stats: RepoStats,
    file_notes: dict[str, dict[str, object]],
    items: int,
) -> str:
    """
    Produce a repo-grounded backlog. Items are generated deterministically and capped.

    Strategy:
      - Start with high-signal repo-level items (architecture / duplication patterns).
      - Add folder-level items for major packages present in this repo.
      - Add file-level items based on observed markers (TODO/print/broad except/missing docstring).
      - Fill remaining slots with per-file "quality hygiene" items to reach `items`.
    """
    out: list[str] = []
    out.append("# Improvements Backlog (Auto-Generated)\n")
    out.append(f"- Generated: `{datetime.now(timezone.utc).isoformat()}`\n")
    out.append(f"- Repo root: `{repo_root}`\n")
    out.append("- Excludes: `external/`, `outputs/`, `htmlcov/`, virtualenvs, caches, and prior reports\n")
    out.append(f"- Target items: **{items}** (this file contains at least that many)\n\n")
    out.append("## How to use this backlog\n")
    out.append("- Each item is numbered and tagged with **Area** and **Type**.\n")
    out.append("- Start with items tagged **P0** (highest impact / risk).\n")
    out.append("- Many items are *hygiene* tasks generated per-file; focus first on the cross-cutting ones.\n\n")

    next_id = 1

    def add(area: str, priority: str, kind: str, text: str) -> None:
        nonlocal next_id
        if next_id > items:
            return
        out.append(f"{next_id:04d}. **[{priority}] [{area}] [{kind}]** {text}\n")
        next_id += 1

    # Repo-level (grounded by observed structure).
    add(
        "Architecture",
        "P0",
        "Refactor",
        "Consolidate caching modules: repo contains both `src/company_researcher/cache/` and "
        "`src/company_researcher/caching/` plus cache logic in `integrations/` and `memory/`; "
        "define a single canonical cache interface + storage backends and migrate callers.",
    )
    add(
        "Architecture",
        "P0",
        "Design",
        "Define a clear boundary between `workflows/`, `graphs/`, and `orchestration/` "
        "to prevent duplicated orchestration logic (fan-out/fan-in appears in multiple places).",
    )
    add(
        "DX",
        "P0",
        "Tooling",
        "Add a single `make audit` / `python -m scripts.analysis.repo_audit` entry to standardize analysis runs "
        "and prevent drift between existing scripts under `scripts/analysis/`.",
    )
    add(
        "Quality",
        "P0",
        "Lint",
        f"Reduce broad exception handling: found **{stats.broad_except}** occurrences of `except Exception` in `src/` "
        "— replace with specific exceptions and add actionable error context.",
    )
    add(
        "Quality",
        "P1",
        "Logging",
        f"Replace remaining `print()` usage in library code: found **{stats.print_calls}** `print(` calls in `src/` "
        "— route through the project logger to keep output structured and controllable.",
    )
    add(
        "Documentation",
        "P1",
        "Docs",
        "Create `docs/KEY_PACKAGES.md` mapping top-level packages (agents/ai/api/graphs/workflows/...) to responsibilities "
        "and stable public entry points.",
    )

    # Folder-level items (based on known folders present).
    major_areas = [
        ("Agents", "src/company_researcher/agents/"),
        ("Workflows", "src/company_researcher/workflows/"),
        ("Graphs", "src/company_researcher/graphs/"),
        ("Orchestration", "src/company_researcher/orchestration/"),
        ("Integrations", "src/company_researcher/integrations/"),
        ("API", "src/company_researcher/api/"),
        ("Monitoring", "src/company_researcher/monitoring/"),
        ("Security", "src/company_researcher/security/"),
        ("Quality", "src/company_researcher/quality/"),
        ("LLM", "src/company_researcher/llm/"),
        ("Memory", "src/company_researcher/memory/"),
        ("Context", "src/company_researcher/context/"),
        ("Testing", "src/company_researcher/testing/"),
    ]
    for area, path in major_areas:
        add(
            area,
            "P1",
            "Docs",
            f"Add/refresh a README for `{path}` documenting its purpose, key modules, and extension points.",
        )
        add(
            area,
            "P1",
            "Tests",
            f"Add a focused test module under `tests/unit/` validating the most important behavior in `{path}` "
            "(happy path + 2 error cases).",
        )

    # File-level items driven by detected markers.
    python_files = sorted([p for p in file_notes.keys() if p.endswith(".py")])

    # Prioritize: TODOs, print, broad except, missing docstring.
    flagged: list[tuple[int, str, str]] = []
    for rel in python_files:
        note = file_notes[rel]
        score = 0
        reasons: list[str] = []
        if "todo_lines" in note:
            score += 100 + len(note["todo_lines"])  # type: ignore[arg-type]
            reasons.append("TODO")
        if note.get("print_calls"):
            score += 40
            reasons.append("print")
        if note.get("broad_except"):
            score += 30
            reasons.append("except Exception")
        if note.get("has_module_docstring") is False:
            score += 10
            reasons.append("no docstring")
        if score > 0:
            flagged.append((score, rel, ",".join(reasons)))
    flagged_sorted = [rel for _, rel, _ in sorted(flagged, key=lambda x: x[0], reverse=True)]

    for rel in flagged_sorted:
        note = file_notes[rel]
        if "todo_lines" in note:
            lines = note["todo_lines"]  # type: ignore[assignment]
            add(
                "Quality",
                "P1",
                "TechDebt",
                f"Resolve TODO/FIXME/HACK markers in `{rel}` (lines: {', '.join(map(str, lines[:12]))}"
                f"{'…' if len(lines) > 12 else ''}).",
            )
        if note.get("print_calls"):
            add("Quality", "P2", "Logging", f"Replace `print()` calls with structured logger in `{rel}`.")
        if note.get("broad_except"):
            add(
                "Quality",
                "P2",
                "Reliability",
                f"Narrow `except Exception` to specific exception types in `{rel}` and add actionable context.",
            )
        if note.get("has_module_docstring") is False:
            add(
                "Documentation",
                "P2",
                "Docs",
                f"Add a module docstring to `{rel}` explaining purpose, inputs/outputs, and key public API.",
            )

    # Fill remaining slots with per-file hygiene items (deterministic, repo-grounded by actual file list).
    for rel in python_files:
        if next_id > items:
            break
        add("Quality", "P3", "Typing", f"Ensure public functions/classes in `{rel}` have type hints and stable contracts.")
        if next_id > items:
            break
        add(
            "Testing",
            "P3",
            "Coverage",
            f"Add/verify unit tests for `{rel}` covering: happy path, empty input, and one failure scenario.",
        )

    # If still short (shouldn't happen), add generic repo items.
    while next_id <= items:
        add("Backlog", "P3", "Hygiene", "Run `ruff`, `pytest`, and `mypy` in CI with clear, actionable failure output.")

    return "".join(out)


def _parse_backlog_items(markdown: str) -> list[dict[str, str]]:
    """
    Parse lines like:
      0001. **[P0] [Architecture] [Refactor]** Text...
    """
    items: list[dict[str, str]] = []
    pattern = re.compile(r"^(?P<id>\d{4})\.\s+\*\*\[(?P<prio>[^\]]+)\]\s+\[(?P<area>[^\]]+)\]\s+\[(?P<kind>[^\]]+)\]\*\*\s+(?P<text>.*)$")
    for line in markdown.splitlines():
        m = pattern.match(line.strip())
        if not m:
            continue
        items.append(
            {
                "id": m.group("id"),
                "priority": m.group("prio"),
                "area": m.group("area"),
                "kind": m.group("kind"),
                "text": m.group("text"),
            }
        )
    return items


def _assign_agent(area: str) -> str:
    area_to_agent = {
        "Architecture": "agent_architecture",
        "Agents": "agent_agents_workflows",
        "Workflows": "agent_agents_workflows",
        "Graphs": "agent_agents_workflows",
        "Orchestration": "agent_agents_workflows",
        "Context": "agent_agents_workflows",
        "Integrations": "agent_integrations",
        "Crawling": "agent_integrations",
        "Retrieval": "agent_integrations",
        "LLM": "agent_integrations",
        "AI": "agent_integrations",
        "API": "agent_api_platform",
        "Production": "agent_api_platform",
        "Security": "agent_api_platform",
        "Monitoring": "agent_quality_observability",
        "Observability": "agent_quality_observability",
        "Quality": "agent_quality_observability",
        "Testing": "agent_testing_ci",
        "Documentation": "agent_docs_dx",
        "DX": "agent_docs_dx",
        "Backlog": "agent_docs_dx",
    }
    return area_to_agent.get(area, "agent_architecture")


def _write_agent_work_package(
    base_dir: Path,
    *,
    backlog_markdown: str,
    scope_name: str,
) -> None:
    """
    Create a folder with a task registry + per-agent workstream markdown files.
    """
    tasks = _parse_backlog_items(backlog_markdown)
    for t in tasks:
        t["agent"] = _assign_agent(t["area"])

    work_dir = base_dir / "agent_work" / scope_name
    work_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        work_dir / "task_registry.json",
        {"scope": scope_name, "generated_at": datetime.now(timezone.utc).isoformat(), "tasks": tasks},
    )

    agents: dict[str, list[dict[str, str]]] = defaultdict(list)
    for t in tasks:
        agents[t["agent"]].append(t)

    agent_order = [
        "agent_architecture",
        "agent_agents_workflows",
        "agent_integrations",
        "agent_api_platform",
        "agent_quality_observability",
        "agent_testing_ci",
        "agent_docs_dx",
    ]

    _write_text(
        work_dir / "AGENT_INDEX.md",
        "\n".join(
            [
                "# Agent Work Package",
                "",
                f"- Scope: **{scope_name}**",
                f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
                "",
                "## Agents",
                "",
                "Each agent gets a dedicated markdown file with its assigned tasks.",
                "",
                "\n".join([f"- `{agent}.md`" for agent in agent_order]),
                "",
            ]
        )
        + "\n",
    )

    for agent in agent_order:
        assigned = agents.get(agent, [])
        lines: list[str] = []
        lines.append(f"# {agent}\n")
        lines.append("## Assigned tasks\n")
        if not assigned:
            lines.append("- (none)\n")
        else:
            for t in assigned:
                lines.append(
                    f"- **{t['id']}**: [{t['priority']}] [{t['area']}] [{t['kind']}] {t['text']}\n"
                )
        _write_text(work_dir / f"{agent}.md", "".join(lines))


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate repo structure + improvements backlog.")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=40,
        help="Max depth for tree output. Use -1 for unlimited depth (can be huge).",
    )
    parser.add_argument(
        "--items",
        type=int,
        default=1000,
        help="Number of improvement items to generate (minimum is enforced to 1000).",
    )
    parser.add_argument(
        "--max-entries-per-dir",
        type=int,
        default=None,
        help="Optional cap on entries shown per directory (prevents huge trees).",
    )
    parser.add_argument(
        "--include-file-sizes",
        action="store_true",
        help="Include file sizes in the tree output.",
    )
    parser.add_argument(
        "--include-everything",
        action="store_true",
        help="Include `external/`, `outputs/`, `.archive/`, and `housekeeping/` (and other excluded dirs) in the full tree/stats.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    items = max(int(args.items), 1000)

    repo_root = Path(__file__).resolve().parents[2]
    reports_root = repo_root / "housekeeping" / "reports"
    suffix = "_repo_audit_full" if args.include_everything else "_repo_audit"
    report_dir = reports_root / f"{_utc_timestamp()}{suffix}"
    report_dir.mkdir(parents=True, exist_ok=True)

    max_depth = None if int(args.max_depth) < 0 else int(args.max_depth)
    exclude_paths: list[Path] = [report_dir]

    exclude_dir_names_all = set() if args.include_everything else set(DEFAULT_EXCLUDE_DIR_NAMES)

    # Work scope: focus on core project directories + root config/docs, avoid archives and generated artifacts.
    exclude_dir_names_work = set(DEFAULT_EXCLUDE_DIR_NAMES) | {
        ".archive",
        ".claude",
        ".specstory",
        "housekeeping",
        "outputs",
        "external",
        "logs",
        "htmlcov",
    }

    # Trees (streamed to disk; safe for huge repos)
    _write_tree_file(
        report_dir / "repo_tree_all.txt",
        root=repo_root,
        exclude_dir_names=exclude_dir_names_all,
        exclude_paths=exclude_paths,
        max_depth=max_depth,
        include_file_sizes=bool(args.include_file_sizes),
        max_entries_per_dir=args.max_entries_per_dir,
    )
    _write_tree_file(
        report_dir / "repo_tree_work.txt",
        root=repo_root,
        exclude_dir_names=exclude_dir_names_work,
        exclude_paths=exclude_paths,
        max_depth=max_depth,
        include_file_sizes=bool(args.include_file_sizes),
        max_entries_per_dir=args.max_entries_per_dir,
    )

    stats_all, extra_all = _collect_stats(
        repo_root, exclude_dir_names=exclude_dir_names_all, exclude_paths=exclude_paths
    )
    _write_json(
        report_dir / "repo_stats_all.json",
        {
            "root": str(stats_all.root),
            "total_files": stats_all.total_files,
            "total_dirs": stats_all.total_dirs,
            "extension_counts": stats_all.extension_counts,
            "python_files": stats_all.python_files,
            "test_files": stats_all.test_files,
            "todo_markers": stats_all.todo_markers,
            "print_calls": stats_all.print_calls,
            "broad_except": stats_all.broad_except,
            "largest_files": stats_all.largest_files,
        },
    )

    stats_work, extra_work = _collect_stats(
        repo_root, exclude_dir_names=exclude_dir_names_work, exclude_paths=exclude_paths
    )
    _write_json(
        report_dir / "repo_stats_work.json",
        {
            "root": str(stats_work.root),
            "total_files": stats_work.total_files,
            "total_dirs": stats_work.total_dirs,
            "extension_counts": stats_work.extension_counts,
            "python_files": stats_work.python_files,
            "test_files": stats_work.test_files,
            "todo_markers": stats_work.todo_markers,
            "print_calls": stats_work.print_calls,
            "broad_except": stats_work.broad_except,
            "largest_files": stats_work.largest_files,
        },
    )

    improvements_work = _generate_improvements(
        repo_root, stats=stats_work, file_notes=extra_work["file_notes"], items=items  # type: ignore[arg-type]
    )
    _write_text(report_dir / "improvements_backlog_work.md", improvements_work)
    _write_agent_work_package(report_dir, backlog_markdown=improvements_work, scope_name="work")

    if args.include_everything:
        improvements_all = _generate_improvements(
            repo_root, stats=stats_all, file_notes=extra_all["file_notes"], items=items  # type: ignore[arg-type]
        )
        _write_text(report_dir / "improvements_backlog_all.md", improvements_all)
        _write_agent_work_package(report_dir, backlog_markdown=improvements_all, scope_name="all")

    # Stable pointer for ongoing multi-agent work
    stable_work_dir = repo_root / "housekeeping" / "repo_improvements"
    stable_work_dir.mkdir(parents=True, exist_ok=True)
    _write_text(
        stable_work_dir / "LATEST_REPORT.md",
        "\n".join(
            [
                "# Latest Repo Audit",
                "",
                f"- Latest report: `{report_dir.relative_to(repo_root).as_posix()}`",
                "",
                "Use the `repo_tree_work.txt` + `agent_work/work/` files for coordinated work.",
                "",
            ]
        )
        + "\n",
    )

    _write_text(
        report_dir / "README.md",
        "\n".join(
            [
                "# Repo Audit Output",
                "",
                "Files:",
                "- `repo_tree_all.txt`: full directory tree (scope depends on flags; can be huge)",
                "- `repo_tree_work.txt`: focused tree (core project only; best for agent work)",
                "- `repo_stats_all.json`: counts and markers (same scope as repo_tree_all)",
                "- `repo_stats_work.json`: counts and markers (same scope as repo_tree_work)",
                "- `improvements_backlog_work.md`: 1,000+ improvements focused on core project areas",
                "- `improvements_backlog_all.md`: 1,000+ improvements across everything (only when --include-everything)",
                "- `agent_work/work/`: per-agent task files + task registry for core project work",
                "- `agent_work/all/`: per-agent task files + task registry for full-repo work (optional)",
                "",
                "Notes:",
                "- This audit always excludes its own output folder from trees/stats to avoid self-recursion.",
                "",
            ]
        )
        + "\n",
    )

    print(str(report_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
