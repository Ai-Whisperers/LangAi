from __future__ import annotations

import json
from concurrent.futures import Future
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.mark.unit
def test_start_batch_writes_disk_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from company_researcher.executors import orchestrator as orchestrator_module
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    def fake_run_research_with_state(
        *, company_name: str, force: bool
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        output = {
            "company_name": company_name,
            "report_path": str(tmp_path / "reports" / f"{company_name}.md"),
            "metrics": {
                "duration_seconds": 1.0,
                "cost_usd": 0.0,
                "tokens": {"input": 0, "output": 0},
            },
            "success": True,
        }
        final_state: Dict[str, Any] = {
            "company_name": company_name,
            "search_queries": [f"{company_name} official website", f"{company_name} leadership"],
            "search_trace": [
                {"query": "q", "provider": "duckduckgo", "success": True, "results": []}
            ],
            "search_stats": {"by_provider": {"duckduckgo": 1}},
            "search_results": [
                {"title": "t", "url": "https://example.com", "content": "c", "score": 0.5}
            ],
            "sources": [{"title": "t", "url": "https://example.com", "score": 0.5}],
        }
        return output, final_state

    monkeypatch.setattr(
        orchestrator_module, "_run_research_with_state", fake_run_research_with_state
    )

    orch = DiskBatchOrchestrator(
        OrchestratorConfig(
            outputs_dir=tmp_path,
            max_workers=2,
            enable_ray=False,
            ray_local_mode=True,
            store_page_content=False,
            max_pages=0,
        )
    )

    job = orch.start_batch(
        ["Acme Inc", "Beta LLC"], depth="standard", force=False, metadata={"source": "test"}
    )
    assert job["batch_id"].startswith("batch_")
    assert len(job["task_ids"]) == 2

    for task_id in job["task_ids"]:
        orch._futures[task_id].result(timeout=5)
        status = orch.get_task_status(task_id)
        assert status is not None
        assert status["status"] == "completed"

        company_dir = Path(status["outputs_dir"])
        assert (company_dir / "MANIFEST.json").exists()
        assert (company_dir / "01_queries.json").exists()
        assert (company_dir / "02_search" / "search_trace.json").exists()
        assert (company_dir / "02_search" / "search_stats.json").exists()
        assert (company_dir / "02_search" / "search_results.json").exists()
        assert (company_dir / "02_search" / "sources.json").exists()
        assert (company_dir / "06_reports" / "result.json").exists()

    batch_manifest = tmp_path / "batches" / job["batch_id"] / "BATCH_MANIFEST.json"
    assert batch_manifest.exists()
    batch_status = orch.get_batch_status(job["batch_id"])
    assert batch_status is not None
    assert batch_status["completed"] == 2


@pytest.mark.unit
def test_start_topic_batch_writes_disk_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from company_researcher.executors import orchestrator as orchestrator_module
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    def fake_run_topic_with_state(
        *, topic: str, force: bool
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        _ = force
        output = {
            "company_name": topic,
            "research_type": "topic",
            "subject": topic,
            "report_path": str(tmp_path / "reports" / f"{topic}.md"),
            "metrics": {
                "duration_seconds": 1.0,
                "cost_usd": 0.0,
                "tokens": {"input": 0, "output": 0},
            },
            "success": True,
        }
        final_state: Dict[str, Any] = {
            "research_type": "topic",
            "subject": topic,
            "topic": topic,
            "search_queries": [f"{topic} overview", f"{topic} state of the art 2025"],
            "search_trace": [
                {"query": "q", "provider": "duckduckgo", "success": True, "results": []}
            ],
            "search_stats": {"by_provider": {"duckduckgo": 1}},
            "search_results": [
                {"title": "t", "url": "https://example.com", "content": "c", "score": 0.5}
            ],
            "sources": [{"title": "t", "url": "https://example.com", "score": 0.5}],
            "github_repos": [
                {"full_name": "org/repo", "url": "https://github.com/org/repo", "stars": 1}
            ],
            "topic_news": {"count": 0, "articles": []},
        }
        return output, final_state

    monkeypatch.setattr(orchestrator_module, "_run_topic_with_state", fake_run_topic_with_state)

    orch = DiskBatchOrchestrator(
        OrchestratorConfig(
            outputs_dir=tmp_path,
            max_workers=2,
            enable_ray=False,
            ray_local_mode=True,
            store_page_content=False,
            max_pages=0,
        )
    )

    job = orch.start_batch(["Retrieval Augmented Generation"], research_type="topic")
    assert job["batch_id"].startswith("batch_")
    assert len(job["task_ids"]) == 1

    task_id = job["task_ids"][0]
    orch._futures[task_id].result(timeout=5)

    status = orch.get_task_status(task_id)
    assert status is not None
    assert status["status"] == "completed"
    assert status.get("research_type") == "topic"
    assert status.get("topic")

    subject_dir = Path(status["outputs_dir"])
    assert (subject_dir / "MANIFEST.json").exists()
    assert (subject_dir / "01_queries.json").exists()
    assert (subject_dir / "02_search" / "sources.json").exists()
    assert (subject_dir / "04_github" / "repos.json").exists()
    assert (subject_dir / "05_news" / "news.json").exists()
    assert (subject_dir / "06_reports" / "result.json").exists()


@pytest.mark.unit
def test_cancel_task_marks_manifest_cancelled(tmp_path: Path) -> None:
    """Cancellation should mark the task as cancelled when the future can be cancelled."""
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    orch = DiskBatchOrchestrator(
        OrchestratorConfig(
            outputs_dir=tmp_path,
            max_workers=1,
            enable_ray=False,
            ray_local_mode=True,
            store_page_content=False,
            max_pages=0,
        )
    )

    batch_id = "batch_test"
    task_id = "task_test"
    company_slug = "exampleco"
    _, manifest_path = orch._init_company_folder(
        batch_id=batch_id,
        task_id=task_id,
        company_name="ExampleCo",
        company_slug=company_slug,
        depth="standard",
        force=False,
        metadata=None,
    )

    # Insert a pending future so cancel_task() can cancel it.
    pending = Future()
    with orch._futures_lock:
        orch._futures[task_id] = pending

    assert orch.cancel_task(task_id) is True

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "cancelled"
    assert "cancelled_at" in manifest


@pytest.mark.unit
def test_list_tasks_filters_by_status_and_company(tmp_path: Path) -> None:
    """list_tasks() should support disk-first filtering by status and company/topic."""
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    orch = DiskBatchOrchestrator(
        OrchestratorConfig(
            outputs_dir=tmp_path,
            max_workers=1,
            enable_ray=False,
            ray_local_mode=True,
            store_page_content=False,
            max_pages=0,
        )
    )

    # Create two manifests on disk.
    _, manifest_a = orch._init_company_folder(
        batch_id="batch_a",
        task_id="task_a",
        company_name="ExampleCo",
        company_slug="exampleco",
        depth="standard",
        force=False,
        metadata=None,
    )
    _, manifest_b = orch._init_company_folder(
        batch_id="batch_b",
        task_id="task_b",
        company_name="OtherCo",
        company_slug="otherco",
        depth="standard",
        force=False,
        metadata=None,
    )

    # Mark one as cancelled.
    orch._update_manifest(manifest_a, {"status": "cancelled"})

    all_tasks = orch.list_tasks(limit=50)
    assert {t["task_id"] for t in all_tasks} >= {"task_a", "task_b"}

    cancelled = orch.list_tasks(status="cancelled", limit=50)
    assert [t["task_id"] for t in cancelled] == ["task_a"]

    filtered_by_company = orch.list_tasks(company="exampleco", limit=50)
    assert [t["task_id"] for t in filtered_by_company] == ["task_a"]

    # Sanity: ensure the second manifest is still present and readable.
    assert json.loads(manifest_b.read_text(encoding="utf-8"))["task_id"] == "task_b"
