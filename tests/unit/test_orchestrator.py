from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def outputs_dir(tmp_path: Path) -> Path:
    return tmp_path / "outputs"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_start_batch_writes_task_index_fields(
    outputs_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    config = OrchestratorConfig(
        outputs_dir=outputs_dir,
        max_workers=1,
        enable_ray=False,
        ray_local_mode=True,
        store_page_content=False,
        max_pages=1,
    )
    orch = DiskBatchOrchestrator(config)

    # Avoid actually running research in background threads.
    monkeypatch.setattr(orch, "_submit_company_task", lambda **_: None)

    result = orch.start_batch(["Acme Inc", "Acme Inc"])
    batch_id = result["batch_id"]

    manifest = _read_json(outputs_dir / "batches" / batch_id / "BATCH_MANIFEST.json")
    assert manifest["batch_id"] == batch_id
    assert isinstance(manifest["task_ids"], list) and len(manifest["task_ids"]) == 2
    assert isinstance(manifest["tasks"], list) and len(manifest["tasks"]) == 2

    task0 = manifest["tasks"][0]
    task1 = manifest["tasks"][1]
    assert task0["task_id"] != task1["task_id"]
    # Duplicate company names should not collide on slug/folder name.
    assert task0["company_slug"] != task1["company_slug"]
    assert Path(task0["manifest_path"]).exists()
    assert Path(task1["manifest_path"]).exists()


def test_get_task_status_after_restart_uses_batch_index(
    outputs_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from company_researcher.executors import orchestrator as orch_mod
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    # Make the research call deterministic/fast.
    def fake_run(*, company_name: str, force: bool) -> tuple[dict[str, Any], dict[str, Any]]:
        return {"report_path": "06_reports/report.md"}, {"sources": [], "search_queries": []}

    monkeypatch.setattr(orch_mod, "_run_research_with_state", fake_run)

    config = OrchestratorConfig(
        outputs_dir=outputs_dir,
        max_workers=1,
        enable_ray=False,
        ray_local_mode=True,
        store_page_content=False,
        max_pages=1,
    )

    orch = DiskBatchOrchestrator(config)
    batch = orch.start_batch(["ExampleCo"])
    task_id = batch["task_ids"][0]

    # Wait for background execution to complete (bounded).
    with orch._futures_lock:
        fut = orch._futures[task_id]
    fut.result(timeout=10)

    # Simulate a new API process: new orchestrator, empty in-memory tracker.
    orch2 = DiskBatchOrchestrator(config)
    status = orch2.get_task_status(task_id)
    assert status is not None
    assert status["task_id"] == task_id
    assert status["status"] == "completed"


def test_page_content_failures_are_non_fatal(
    outputs_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from company_researcher.executors import orchestrator as orch_mod
    from company_researcher.executors.orchestrator import DiskBatchOrchestrator, OrchestratorConfig

    def fake_run(*, company_name: str, force: bool) -> tuple[dict[str, Any], dict[str, Any]]:
        # Include sources so page-content storage would try to process them.
        return {"report_path": "06_reports/report.md"}, {
            "sources": [{"url": "https://example.com"}]
        }

    monkeypatch.setattr(orch_mod, "_run_research_with_state", fake_run)

    # Force _store_page_content to blow up.
    def boom(*_: Any, **__: Any) -> None:
        raise RuntimeError("boom")

    config = OrchestratorConfig(
        outputs_dir=outputs_dir,
        max_workers=1,
        enable_ray=False,
        ray_local_mode=True,
        store_page_content=True,
        max_pages=1,
    )
    orch = DiskBatchOrchestrator(config)
    monkeypatch.setattr(orch, "_store_page_content", boom)

    # Call internal runner directly to avoid scheduling noise.
    batch_id = "batch_test"
    task_id = "task_test"
    company_slug = "exampleco"
    orch._init_company_folder(
        batch_id=batch_id,
        task_id=task_id,
        company_name="ExampleCo",
        company_slug=company_slug,
        depth="standard",
        force=False,
        metadata=None,
    )
    orch._run_company_task(
        batch_id=batch_id,
        task_id=task_id,
        company_name="ExampleCo",
        company_slug=company_slug,
        depth="standard",
        force=False,
        metadata=None,
    )

    manifest_path = (
        outputs_dir / "batches" / batch_id / "companies" / company_slug / "MANIFEST.json"
    )
    manifest = _read_json(manifest_path)
    assert manifest["status"] == "completed"
    assert manifest["page_content_status"] == "failed"
    assert "page_content_error" in manifest
