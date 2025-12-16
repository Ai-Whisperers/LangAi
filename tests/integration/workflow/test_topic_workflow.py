"""
Integration tests for the topic workflow (free/offline via mocks).

Goal: validate that the topic workflow can run end-to-end without network access,
produce a report artifact, and return a final state with populated sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest


@dataclass
class _DummyLLMResult:
    content: str
    cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


class _DummyLLMClient:
    def complete(self, *, prompt: str, task_type: str) -> _DummyLLMResult:
        if "Return ONLY valid JSON" in prompt:
            # Minimal plan that triggers search/news/github nodes.
            return _DummyLLMResult(
                content=(
                    "{"
                    '"canonical_topic":"Test Topic",'
                    '"synonyms":["TT"],'
                    '"subtopics":["Basics","SOTA"],'
                    '"beginner_prereqs":["NLP"],'
                    '"key_terms":["RAG"],'
                    '"search_queries":["Test Topic overview","Test Topic tutorial","Test Topic survey 2024"],'
                    '"news_queries":["Test Topic"],'
                    '"github_queries":["test topic stars:>10"]'
                    "}"
                ),
                cost=0.0,
                input_tokens=10,
                output_tokens=10,
            )

        # Synthesis: include required sections + >= 10 citations + references.
        # The workflow provides sources; we only need citations to be in-range (we use [1]-[10]).
        report = "\n".join(
            [
                "## Beginner-friendly introduction",
                "Intro text [1] [2].",
                "",
                "## Core concepts",
                "Core text [3] [4].",
                "",
                "## Timeline of key milestones",
                "Timeline text [5].",
                "",
                "## Current state of the art (as of 2024-2025)",
                "SOTA text [6] [7].",
                "",
                "## Practical guidance",
                "Guidance text [8].",
                "",
                "## Open problems & research directions",
                "Open problems text [9].",
                "",
                "## References",
                "[1] Source - https://example.com/1",
                "[2] Source - https://example.com/2",
                "[3] Source - https://example.com/3",
                "[4] Source - https://example.com/4",
                "[5] Source - https://example.com/5",
                "[6] Source - https://example.com/6",
                "[7] Source - https://example.com/7",
                "[8] Source - https://example.com/8",
                "[9] Source - https://example.com/9",
                "[10] Source - https://example.com/10",
            ]
        )
        return _DummyLLMResult(content=report, cost=0.0, input_tokens=10, output_tokens=10)


class _FakeSearchResponse:
    def __init__(self, *, query: str, results: list, provider: str = "wikipedia"):
        self.query = query
        self.results = results
        self.provider = provider
        self.quality_tier = "free"
        self.cost = 0.0
        self.cached = False
        self.success = True
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "provider": self.provider,
            "quality_tier": self.quality_tier,
            "cost": self.cost,
            "cached": self.cached,
            "success": self.success,
            "error": self.error,
        }


class _FakeSearchRouter:
    def __init__(self):
        self._i = 0

    def search(
        self, *, query: str, quality: str, max_results: int, **_: Any
    ) -> _FakeSearchResponse:
        from company_researcher.integrations.search_router import SearchResult

        # Generate deterministic unique URLs; enough to exceed the ">=10 sources" quality gate.
        out: List[SearchResult] = []
        for _ in range(max_results):
            self._i += 1
            out.append(
                SearchResult(
                    title=f"Result {self._i}",
                    url=f"https://example.com/web/{self._i}",
                    snippet=f"Snippet {self._i}",
                    source="wikipedia",
                )
            )
        return _FakeSearchResponse(query=query, results=out)

    def get_stats(self) -> Dict[str, Any]:
        return {"provider": "fake", "tier": "free"}


@dataclass
class _FakeNewsArticle:
    title: str
    url: str
    source_name: str = "Example News"
    published_at: str = "2025-01-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "source_name": self.source_name,
            "published_at": self.published_at,
        }


@dataclass
class _FakeNewsResult:
    articles: List[_FakeNewsArticle]


class _FakeGitHubClient:
    def __init__(self, *_: Any, **__: Any):
        pass

    async def __aenter__(self) -> "_FakeGitHubClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def search_repos(self, *, query: str, per_page: int, page: int):
        from company_researcher.integrations.github_client import GitHubRepo

        _ = (query, per_page, page)
        return [
            GitHubRepo(
                name="repo",
                full_name="org/repo",
                description="desc",
                url="https://github.com/org/repo",
                homepage=None,
                stars=1000,
                forks=100,
                watchers=100,
                language="python",
                open_issues=1,
                created_at="2024-01-01",
                updated_at="2025-01-01",
                pushed_at="2025-01-01",
                topics=["rag"],
                is_fork=False,
                is_archived=False,
            )
        ]


class _FakeCache:
    def should_research_topic(self, topic: str, *, force: bool = False, max_age_days: int = 7):
        _ = (topic, force, max_age_days)
        return {"needs_research": True, "reason": "test"}

    def get_topic_data(self, topic: str):
        _ = topic
        return None

    def store_topic_run(self, *args: Any, **kwargs: Any) -> bool:
        _ = (args, kwargs)
        return True


@pytest.mark.integration
@pytest.mark.workflow
def test_topic_workflow_runs_offline_and_saves_report(tmp_path: Path):
    from company_researcher.workflows.topic_workflow import run_topic_workflow_with_state

    def _fake_news_search_sync(query: str, max_results: int, quality):
        _ = (query, max_results, quality)
        return _FakeNewsResult(
            articles=[
                _FakeNewsArticle(title="News 1", url="https://example.com/news/1"),
                _FakeNewsArticle(title="News 2", url="https://example.com/news/2"),
            ]
        )

    with (
        patch("company_researcher.workflows.topic_workflow.get_cache", return_value=_FakeCache()),
        patch(
            "company_researcher.workflows.nodes.topic_nodes.get_smart_client",
            return_value=_DummyLLMClient(),
        ),
        patch(
            "company_researcher.workflows.nodes.topic_nodes.get_search_router",
            return_value=_FakeSearchRouter(),
        ),
        patch(
            "company_researcher.workflows.nodes.topic_nodes.smart_news_search_sync",
            side_effect=_fake_news_search_sync,
        ),
        patch("company_researcher.workflows.nodes.topic_nodes.GitHubClient", _FakeGitHubClient),
    ):
        output, state = run_topic_workflow_with_state(
            topic="Test Topic",
            force=True,
            output_dir=str(tmp_path),
        )

    report_path = Path(output["report_path"])
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "References" in report_text

    assert isinstance(state.get("sources"), list)
    assert len(state.get("sources") or []) >= 10
