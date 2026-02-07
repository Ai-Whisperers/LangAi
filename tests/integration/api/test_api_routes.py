# pyright: reportMissingImports=false
"""Deterministic integration tests for the FastAPI layer (no network/LLM)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest


@pytest.mark.integration
def test_create_app_root_and_health() -> None:
    from company_researcher.api import app as api_app

    if not api_app.FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed")

    from fastapi.testclient import TestClient

    app = api_app.create_app(enable_cors=False, enable_rate_limiting=False, enable_logging=False)
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "running"
    assert body["docs"] == "/docs"

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.integration
def test_start_research_disk_backend_submits_to_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from company_researcher.api import app as api_app
    from company_researcher.api import routes as api_routes

    if not api_app.FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed")

    from fastapi.testclient import TestClient

    @dataclass
    class StubOrchestrator:
        last_call: Optional[Dict[str, Any]] = None

        def start_batch(
            self, items, *, depth: str, force: bool, metadata: Dict[str, Any], research_type: str
        ):
            self.last_call = {
                "items": items,
                "depth": depth,
                "force": force,
                "metadata": metadata,
                "research_type": research_type,
            }
            return {"task_ids": ["task_1"]}

    orch = StubOrchestrator()

    monkeypatch.setattr(api_routes, "_use_disk_backend", lambda: True)
    monkeypatch.setattr(api_routes, "get_orchestrator", lambda: orch)

    app = api_app.create_app(enable_cors=False, enable_rate_limiting=False, enable_logging=False)
    client = TestClient(app)

    r = client.post(
        "/api/v1/research",
        json={
            "research_type": "company",
            "company_name": "TestCo",
            "depth": "standard",
            "metadata": {"k": "v"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["task_id"] == "task_1"
    assert body["status"] == "pending"
    assert "disk-first runner" in body["message"]

    assert orch.last_call is not None
    assert orch.last_call["items"] == ["TestCo"]
    assert orch.last_call["depth"] == "standard"
    assert orch.last_call["research_type"] == "company"


@pytest.mark.integration
def test_start_research_task_storage_backend_does_not_execute_real_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from company_researcher.api import app as api_app
    from company_researcher.api import routes as api_routes

    if not api_app.FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed")

    from fastapi.testclient import TestClient

    class StubStorage:
        def __init__(self) -> None:
            self.saved: Dict[str, Any] = {}

        async def save_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
            await asyncio.sleep(0)
            self.saved[task_id] = task_data

        async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
            await asyncio.sleep(0)
            return self.saved.get(task_id)

    storage = StubStorage()

    def _noop_execute_research(*_a: Any, **_k: Any) -> None:
        return

    monkeypatch.setattr(api_routes, "_use_disk_backend", lambda: False)
    monkeypatch.setattr(api_routes, "get_task_storage", lambda: storage)
    monkeypatch.setattr(api_routes, "_execute_research", _noop_execute_research)

    app = api_app.create_app(enable_cors=False, enable_rate_limiting=False, enable_logging=False)
    client = TestClient(app)

    r = client.post("/api/v1/research", json={"research_type": "company", "company_name": "TestCo"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "pending"
    assert "Research task created successfully" == body["message"]
    assert body["task_id"] in storage.saved
