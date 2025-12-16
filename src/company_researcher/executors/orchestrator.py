"""
Disk-first batch orchestrator (Ray-style).

Goal:
    Run research jobs asynchronously and store everything to the output folder
    so the repo itself (or a synced Drive folder) is the "database".

Design:
    - Local-first: works without Ray by using a background thread pool.
    - Ray-style: if Ray is installed and enabled, runs one task per company in Ray
      and tracks status through an actor-like progress tracker.
    - Output-first: every task writes a stable folder structure and MANIFEST.json.

This is intentionally independent of Celery/Redis so local usage is simple and
cloud migration can map to Ray cluster later.
"""

from __future__ import annotations

import json
import os
import re
import threading
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple

from ..utils import get_logger, utc_now

logger = get_logger(__name__)

TASK_MANIFEST_FILENAME = "MANIFEST.json"
BATCH_MANIFEST_FILENAME = "BATCH_MANIFEST.json"


try:
    import ray  # type: ignore

    RAY_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    ray = None
    RAY_AVAILABLE = False


TaskStatus = str  # "pending" | "running" | "completed" | "failed"

TaskStatusLiteral = Literal["pending", "running", "completed", "failed", "cancelled"]


def _slugify(value: str, max_len: int = 80) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value[:max_len] or "company"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON file path=%s error=%s", str(path), str(exc))
        return None
    except OSError as exc:
        logger.warning("Failed to read JSON file path=%s error=%s", str(path), str(exc))
        return None
    except Exception as exc:  # noqa: BLE001 - defensive; return None but keep context
        logger.warning("Unexpected error reading JSON file path=%s error=%s", str(path), str(exc))
        return None


def _manifest_path_for_company_dir(company_dir: Path) -> Path:
    return company_dir / TASK_MANIFEST_FILENAME


@dataclass(frozen=True)
class OrchestratorConfig:
    outputs_dir: Path
    max_workers: int
    enable_ray: bool
    ray_local_mode: bool
    store_page_content: bool
    max_pages: int

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        outputs_dir = Path(os.environ.get("COMPANY_RESEARCH_OUTPUTS_DIR", "outputs")).resolve()
        max_workers = int(os.environ.get("COMPANY_RESEARCH_MAX_WORKERS", "4"))
        enable_ray = os.environ.get("COMPANY_RESEARCH_EXECUTOR", "").strip().lower() == "ray"
        ray_local_mode = (
            os.environ.get("COMPANY_RESEARCH_RAY_LOCAL_MODE", "true").strip().lower() == "true"
        )
        store_page_content = (
            os.environ.get("COMPANY_RESEARCH_STORE_PAGE_CONTENT", "false").strip().lower() == "true"
        )
        max_pages = int(os.environ.get("COMPANY_RESEARCH_MAX_PAGES", "25"))
        return cls(
            outputs_dir=outputs_dir,
            max_workers=max_workers,
            enable_ray=enable_ray,
            ray_local_mode=ray_local_mode,
            store_page_content=store_page_content,
            max_pages=max_pages,
        )


class InMemoryProgressTracker:
    """Thread-safe status store (Ray-style actor replacement for local mode)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._batches: Dict[str, Dict[str, Any]] = {}

    def set_task(self, task_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._tasks[task_id] = payload

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        with self._lock:
            existing = self._tasks.get(task_id, {})
            self._tasks[task_id] = {**existing, **updates}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            value = self._tasks.get(task_id)
            return dict(value) if value else None

    def set_batch(self, batch_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._batches[batch_id] = payload

    def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> None:
        with self._lock:
            existing = self._batches.get(batch_id, {})
            self._batches[batch_id] = {**existing, **updates}

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            value = self._batches.get(batch_id)
            return dict(value) if value else None


class DiskBatchOrchestrator:
    """
    Orchestrates batch research runs and persists everything to disk.

    Public API is intentionally dict-based to integrate smoothly with the existing
    FastAPI responses without introducing new schemas yet.
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None) -> None:
        self.config = config or OrchestratorConfig.from_env()
        self._tracker = InMemoryProgressTracker()
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self._futures: Dict[str, Future] = {}
        self._futures_lock = threading.Lock()
        self._task_index: Dict[str, str] = {}  # task_id -> manifest_path
        self._task_index_lock = threading.Lock()
        self._ray_initialized = False

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def start_batch(
        self,
        companies: Iterable[str],
        *,
        depth: str = "standard",
        force: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        companies_list = [c.strip() for c in companies if c and c.strip()]
        if not companies_list:
            raise ValueError("companies must contain at least one non-empty company name")

        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        created_at = utc_now().isoformat()
        batch_dir = self._batch_dir(batch_id)

        batch_manifest: Dict[str, Any] = {
            "batch_id": batch_id,
            "created_at": created_at,
            "status": "pending",
            "depth": depth,
            "force": force,
            "companies": companies_list,
            "task_ids": [],
            "tasks": [],
            "metadata": metadata or {},
            "outputs_dir": str(batch_dir),
        }

        _write_json(batch_dir / BATCH_MANIFEST_FILENAME, batch_manifest)

        tasks: List[Dict[str, Any]] = []
        task_ids: List[str] = []
        used_slugs: Dict[str, int] = {}
        for company_name in companies_list:
            base_slug = _slugify(company_name)
            suffix = used_slugs.get(base_slug, 0)
            used_slugs[base_slug] = suffix + 1
            company_slug = base_slug if suffix == 0 else f"{base_slug}-{suffix}"

            task_id = f"task_{uuid.uuid4().hex[:12]}"
            task_ids.append(task_id)
            company_dir, manifest_path = self._init_company_folder(
                batch_id=batch_id,
                task_id=task_id,
                company_name=company_name,
                company_slug=company_slug,
                depth=depth,
                force=force,
                metadata=metadata,
            )
            tasks.append(
                {
                    "task_id": task_id,
                    "company_name": company_name,
                    "company_slug": company_slug,
                    "outputs_dir": str(company_dir),
                    "manifest_path": str(manifest_path),
                }
            )
            with self._task_index_lock:
                self._task_index[task_id] = str(manifest_path)

        batch_manifest["task_ids"] = task_ids
        batch_manifest["tasks"] = tasks
        _write_json(batch_dir / BATCH_MANIFEST_FILENAME, batch_manifest)
        self._tracker.set_batch(batch_id, dict(batch_manifest))

        for task in tasks:
            self._submit_company_task(
                batch_id=batch_id,
                task_id=task["task_id"],
                company_name=task["company_name"],
                company_slug=task["company_slug"],
                depth=depth,
                force=force,
                metadata=metadata,
            )

        self._tracker.update_batch(batch_id, {"status": "running"})
        _write_json(batch_dir / BATCH_MANIFEST_FILENAME, {**batch_manifest, "status": "running"})

        return {
            "batch_id": batch_id,
            "task_ids": task_ids,
            "status": "running",
            "created_at": created_at,
            "outputs_dir": str(batch_dir),
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        # In Ray mode, the work runs in separate processes and updates disk manifests.
        # Prefer disk so status progresses correctly even when the API process can't
        # receive in-memory updates.
        if self.config.enable_ray:
            manifest = self._find_task_manifest(task_id)
            if manifest:
                self._tracker.update_task(task_id, manifest)
                return manifest

        task = self._tracker.get_task(task_id)
        if task:
            return task

        manifest_path = self._get_task_manifest_path(task_id)
        if manifest_path:
            manifest = _read_json(Path(manifest_path))
            if manifest:
                return manifest

        manifest = self._find_task_manifest(task_id)  # last resort (legacy / migrated data)
        if manifest:
            with self._task_index_lock:
                self._task_index[task_id] = str(
                    Path(manifest["outputs_dir"]) / TASK_MANIFEST_FILENAME
                )
            return manifest
        return None

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        manifest = self.get_task_status(task_id)
        if not manifest:
            return None
        result_path = manifest.get("result_path")
        if result_path:
            result = _read_json(Path(result_path))
        else:
            result = None
        return {**manifest, "result": result}

    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        batch = self._tracker.get_batch(batch_id)
        if not batch:
            batch = _read_json(self._batch_dir(batch_id) / BATCH_MANIFEST_FILENAME)
        if not batch:
            return None

        task_ids = self._extract_task_ids_from_batch(batch)
        counts, progress, status = self._summarize_batch(task_ids)

        return {
            **batch,
            "status": status,
            "completed": counts["completed"],
            "failed": counts["failed"],
            "running": counts["running"],
            "pending": counts["pending"],
            "progress": progress,
        }

    def _extract_task_ids_from_batch(self, batch: Dict[str, Any]) -> List[str]:
        tasks = batch.get("tasks") or []
        if isinstance(tasks, list) and tasks:
            task_ids = [t.get("task_id") for t in tasks if isinstance(t, dict) and t.get("task_id")]
            return [tid for tid in task_ids if isinstance(tid, str) and tid]
        task_ids = batch.get("task_ids", []) or []
        return [tid for tid in task_ids if isinstance(tid, str) and tid]

    def _summarize_batch(
        self, task_ids: List[str]
    ) -> Tuple[Dict[str, int], float, TaskStatusLiteral]:
        counts = {"completed": 0, "failed": 0, "running": 0, "pending": 0}
        for tid in task_ids:
            task = self.get_task_status(tid) or {}
            raw_status = task.get("status") or "pending"
            status = str(raw_status).lower()
            if status in counts:
                counts[status] += 1
            else:
                counts["pending"] += 1

        total = len(task_ids)
        progress = (counts["completed"] / total) if total else 0.0
        overall = self._derive_batch_status(counts, total)
        return counts, progress, overall

    def _derive_batch_status(self, counts: Dict[str, int], total: int) -> TaskStatusLiteral:
        if total <= 0:
            return "running"
        failed = counts.get("failed", 0)
        completed = counts.get("completed", 0)
        if failed > 0:
            return "failed" if (completed + failed) == total else "running"
        return "completed" if completed == total else "running"

    def cancel_task(self, task_id: str) -> bool:
        """
        Best-effort cancellation for local thread-pool tasks.

        Notes:
            - If the task is already running, Python futures cannot be force-killed safely.
            - In Ray mode, cancellation requires Ray task tracking; this method returns False.
        """
        if self.config.enable_ray:
            return False

        with self._futures_lock:
            future = self._futures.get(task_id)
        if not future:
            return False

        cancelled = future.cancel()
        if not cancelled:
            return False

        manifest = self._find_task_manifest(task_id)
        if manifest:
            manifest_path = Path(manifest["outputs_dir"]) / TASK_MANIFEST_FILENAME
            self._update_manifest(
                manifest_path,
                {"status": "cancelled", "cancelled_at": utc_now().isoformat()},
            )
        self._tracker.update_task(
            task_id, {"status": "cancelled", "cancelled_at": utc_now().isoformat()}
        )
        return True

    def list_tasks(
        self,
        *,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List tasks by scanning MANIFEST.json files under outputs/batches.

        This is disk-first by design so results survive API restarts.
        """
        root = self.config.outputs_dir / "batches"
        if not root.exists():
            return []

        wanted_status = status.lower() if status else None
        wanted_company = company.lower().strip() if company else None

        items: List[Dict[str, Any]] = []
        for manifest_path in root.glob(f"**/{TASK_MANIFEST_FILENAME}"):
            data = _read_json(manifest_path)
            if not data:
                continue
            if wanted_status and (data.get("status") or "").lower() != wanted_status:
                continue
            if wanted_company and wanted_company not in (data.get("company_name") or "").lower():
                continue
            items.append(data)

        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset : offset + limit]

    # ---------------------------------------------------------------------
    # Internals
    # ---------------------------------------------------------------------

    def _batch_dir(self, batch_id: str) -> Path:
        return self.config.outputs_dir / "batches" / batch_id

    def _company_dir(self, batch_id: str, company_slug: str) -> Path:
        return self._batch_dir(batch_id) / "companies" / company_slug

    def _init_company_folder(
        self,
        *,
        batch_id: str,
        task_id: str,
        company_name: str,
        company_slug: str,
        depth: str,
        force: bool,
        metadata: Optional[Dict[str, Any]],
    ) -> Tuple[Path, Path]:
        company_dir = self._company_dir(batch_id, company_slug)
        _ensure_dir(company_dir)
        _ensure_dir(company_dir / "02_search")
        _ensure_dir(company_dir / "03_pages" / "content")
        _ensure_dir(company_dir / "06_reports")

        manifest = {
            "task_id": task_id,
            "batch_id": batch_id,
            "company_name": company_name,
            "company_slug": company_slug,
            "depth": depth,
            "force": force,
            "status": "pending",
            "created_at": utc_now().isoformat(),
            "outputs_dir": str(company_dir),
            "result_path": str(company_dir / "06_reports" / "result.json"),
            "report_path": None,
            "error": None,
            "metadata": metadata or {},
        }
        manifest_path = company_dir / TASK_MANIFEST_FILENAME
        manifest["manifest_path"] = str(manifest_path)
        _write_json(manifest_path, manifest)
        self._tracker.set_task(task_id, dict(manifest))
        return company_dir, manifest_path

    def _submit_company_task(
        self,
        *,
        batch_id: str,
        task_id: str,
        company_name: str,
        company_slug: str,
        depth: str,
        force: bool,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        if self.config.enable_ray:
            self._submit_company_task_ray(
                batch_id=batch_id,
                task_id=task_id,
                company_name=company_name,
                company_slug=company_slug,
                depth=depth,
                force=force,
                metadata=metadata,
            )
            return

        future = self._executor.submit(
            self._run_company_task,
            batch_id=batch_id,
            task_id=task_id,
            company_name=company_name,
            company_slug=company_slug,
            depth=depth,
            force=force,
            metadata=metadata,
        )
        with self._futures_lock:
            self._futures[task_id] = future

    def _submit_company_task_ray(
        self,
        *,
        batch_id: str,
        task_id: str,
        company_name: str,
        company_slug: str,
        depth: str,
        force: bool,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        if not RAY_AVAILABLE:
            raise RuntimeError(
                "❌ ERROR: Ray execution requested but Ray is not installed\n\n"
                "Explanation: COMPANY_RESEARCH_EXECUTOR=ray requires the 'ray' Python package.\n\n"
                "Solution: Install Ray and restart the API:\n"
                "  pip install ray\n\n"
                "Help: See docs/ for local-first execution (thread pool) by unsetting COMPANY_RESEARCH_EXECUTOR."
            )
        if not self._ray_initialized:
            ray.init(ignore_reinit_error=True, local_mode=self.config.ray_local_mode)
            self._ray_initialized = True

        # In Ray mode we still write to disk; progress is written to disk and
        # mirrored in the in-memory tracker on the API process as best-effort.
        _run_company_task_ray.remote(
            batch_id=batch_id,
            task_id=task_id,
            company_name=company_name,
            company_slug=company_slug,
            depth=depth,
            force=force,
            metadata=metadata or {},
            outputs_dir=str(self.config.outputs_dir),
            store_page_content=self.config.store_page_content,
            max_pages=self.config.max_pages,
        )

    def _run_company_task(
        self,
        *,
        batch_id: str,
        task_id: str,
        company_name: str,
        company_slug: str,
        depth: str,
        force: bool,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        company_dir = self._company_dir(batch_id, company_slug)
        manifest_path = _manifest_path_for_company_dir(company_dir)

        self._update_manifest(
            manifest_path,
            {"status": "running", "started_at": utc_now().isoformat()},
        )

        try:
            output, final_state = _run_research_with_state(company_name=company_name, force=force)

            self._write_provenance_artifacts(company_dir, final_state)
            self._write_result(company_dir, output, final_state)
            self._maybe_store_page_content(
                manifest_path, task_id, company_name, company_dir, final_state
            )
            self._mark_task_completed(manifest_path, output)
        except Exception as exc:
            self._mark_task_failed(manifest_path, exc)
            logger.exception(
                "Research task failed task_id=%s company_name=%s", task_id, company_name
            )

    def _write_provenance_artifacts(self, company_dir: Path, final_state: Dict[str, Any]) -> None:
        """
        Persist provenance artifacts (queries, traces, sources) so runs are auditable.

        Keep this disk-first and schema-light; callers treat these as optional artifacts.
        """
        _write_json(
            company_dir / "01_queries.json",
            {"search_queries": final_state.get("search_queries", [])},
        )
        _write_json(
            company_dir / "02_search" / "search_trace.json",
            {"search_trace": final_state.get("search_trace", [])},
        )
        _write_json(
            company_dir / "02_search" / "search_stats.json",
            {"search_stats": final_state.get("search_stats", {})},
        )
        _write_json(
            company_dir / "02_search" / "search_results.json",
            {"search_results": final_state.get("search_results", [])},
        )
        _write_json(
            company_dir / "02_search" / "sources.json", {"sources": final_state.get("sources", [])}
        )

    def _write_result(
        self, company_dir: Path, output: Dict[str, Any], final_state: Dict[str, Any]
    ) -> None:
        _write_json(
            company_dir / "06_reports" / "result.json", {"output": output, "state": final_state}
        )

    def _maybe_store_page_content(
        self,
        manifest_path: Path,
        task_id: str,
        company_name: str,
        company_dir: Path,
        final_state: Dict[str, Any],
    ) -> None:
        if not self.config.store_page_content:
            return
        try:
            self._store_page_content(company_dir, final_state.get("sources", []) or [])
            self._update_manifest(manifest_path, {"page_content_status": "completed"})
        except Exception as exc:  # noqa: BLE001 - page content is best-effort
            self._update_manifest(
                manifest_path,
                {
                    "page_content_status": "failed",
                    "page_content_error": str(exc),
                },
            )
            logger.warning(
                "Page content storage failed (non-fatal) task_id=%s company_name=%s error=%s",
                task_id,
                company_name,
                str(exc),
            )

    def _mark_task_completed(self, manifest_path: Path, output: Dict[str, Any]) -> None:
        self._update_manifest(
            manifest_path,
            {
                "status": "completed",
                "completed_at": utc_now().isoformat(),
                "report_path": output.get("report_path"),
            },
        )

    def _mark_task_failed(self, manifest_path: Path, exc: Exception) -> None:
        self._update_manifest(
            manifest_path,
            {
                "status": "failed",
                "failed_at": utc_now().isoformat(),
                "error": str(exc),
            },
        )

    def _store_page_content(self, company_dir: Path, sources: List[Dict[str, Any]]) -> None:
        """
        Fetch and store page markdown for top sources.

        Uses Jina Reader (free) for predictable markdown conversion.
        """
        from ..integrations.jina_reader import get_jina_reader

        reader = get_jina_reader()
        pages_dir = company_dir / "03_pages"
        content_dir = pages_dir / "content"
        _ensure_dir(content_dir)

        pages_log_path = pages_dir / "pages.jsonl"
        max_pages = max(0, int(self.config.max_pages))

        urls = self._select_source_urls(sources, max_pages)

        with pages_log_path.open("a", encoding="utf-8") as f:
            for url in urls:
                try:
                    result = reader.read_url(url)
                    record: Dict[str, Any] = {
                        "url": url,
                        "success": result.success,
                        "error": result.error,
                        "response_time_ms": result.response_time_ms,
                        "token_count_estimate": result.token_count,
                        "title": result.title,
                    }
                    if result.success and result.content:
                        file_name = f"{uuid.uuid4().hex}.md"
                        out_path = content_dir / file_name
                        out_path.write_text(result.content, encoding="utf-8")
                        record["content_path"] = str(out_path)
                except Exception as exc:  # noqa: BLE001 - per-URL best-effort
                    record = {
                        "url": url,
                        "success": False,
                        "error": str(exc),
                    }
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _select_source_urls(self, sources: List[Dict[str, Any]], max_pages: int) -> List[str]:
        if max_pages <= 0:
            return []
        urls: List[str] = []
        seen: set[str] = set()
        for source in sources:
            url = (source.get("url") or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            urls.append(url)
            if len(urls) >= max_pages:
                break
        return urls

    def _update_manifest(self, manifest_path: Path, updates: Dict[str, Any]) -> None:
        current = _read_json(manifest_path) or {}
        merged = {**current, **updates}
        _write_json(manifest_path, merged)

        task_id = merged.get("task_id")
        if isinstance(task_id, str) and task_id:
            self._tracker.update_task(task_id, merged)
            manifest_path_str = str(manifest_path)
            with self._task_index_lock:
                self._task_index[task_id] = manifest_path_str

    def _get_task_manifest_path(self, task_id: str) -> Optional[str]:
        with self._task_index_lock:
            path = self._task_index.get(task_id)
        if path:
            return path
        self._rebuild_task_index_from_batches()
        with self._task_index_lock:
            return self._task_index.get(task_id)

    def _rebuild_task_index_from_batches(self) -> None:
        root = self.config.outputs_dir / "batches"
        if not root.exists():
            return
        rebuilt = self._build_task_index_from_batch_manifests(root)
        if not rebuilt:
            return
        with self._task_index_lock:
            self._task_index.update(rebuilt)

    def _build_task_index_from_batch_manifests(self, batches_root: Path) -> Dict[str, str]:
        rebuilt: Dict[str, str] = {}
        for batch_manifest_path in batches_root.glob(f"*/{BATCH_MANIFEST_FILENAME}"):
            data = _read_json(batch_manifest_path) or {}
            for tid, manifest_path in self._iter_task_index_entries(data):
                rebuilt[tid] = manifest_path
        return rebuilt

    def _iter_task_index_entries(self, batch_manifest: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
        tasks = batch_manifest.get("tasks") or []
        if not isinstance(tasks, list):
            return []
        out: List[Tuple[str, str]] = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            tid = task.get("task_id")
            mpath = task.get("manifest_path")
            if isinstance(tid, str) and tid and isinstance(mpath, str) and mpath:
                out.append((tid, mpath))
        return out

    def _find_task_manifest(self, task_id: str) -> Optional[Dict[str, Any]]:
        root = self.config.outputs_dir / "batches"
        if not root.exists():
            return None
        # Legacy fallback: scan manifests. Avoid in hot paths; prefer batch index-based lookup.
        for manifest_path in root.glob(f"*/companies/*/{TASK_MANIFEST_FILENAME}"):
            data = _read_json(manifest_path)
            if data and data.get("task_id") == task_id:
                return data
        return None


def _run_research_with_state(
    *, company_name: str, force: bool
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Run the cache-aware workflow and return (output, final_state).

    Kept as a tiny wrapper so the orchestrator can be tested/mocked cleanly.
    """
    from ..workflows.cache_aware_workflow import run_cache_aware_workflow_with_state

    return run_cache_aware_workflow_with_state(company_name=company_name, force=force)


if RAY_AVAILABLE:  # pragma: no cover - exercised only when Ray is installed

    @ray.remote
    def _run_company_task_ray(
        *,
        batch_id: str,
        task_id: str,
        company_name: str,
        company_slug: str,
        depth: str,
        force: bool,
        metadata: Dict[str, Any],
        outputs_dir: str,
        store_page_content: bool,
        max_pages: int,
    ) -> None:
        # Minimal Ray-side runner: reuse DiskBatchOrchestrator logic but avoid
        # sharing Python objects across processes.
        orchestrator = DiskBatchOrchestrator(
            OrchestratorConfig(
                outputs_dir=Path(outputs_dir),
                max_workers=1,
                enable_ray=False,
                ray_local_mode=True,
                store_page_content=store_page_content,
                max_pages=max_pages,
            )
        )
        orchestrator._run_company_task(
            batch_id=batch_id,
            task_id=task_id,
            company_name=company_name,
            company_slug=company_slug,
            depth=depth,
            force=force,
            metadata=metadata,
        )


_orchestrator: Optional[DiskBatchOrchestrator] = None
_orchestrator_lock = threading.Lock()


def get_orchestrator() -> DiskBatchOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        with _orchestrator_lock:
            if _orchestrator is None:
                _orchestrator = DiskBatchOrchestrator()
    return _orchestrator
