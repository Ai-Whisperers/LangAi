from __future__ import annotations

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
