"""Deterministic integration tests for the basic LangGraph workflow."""

from __future__ import annotations

import builtins
from typing import Any, Dict, List

import pytest


def _make_stub_node(name: str, calls: List[str], payload: Dict[str, Any]):
    def _node(state: Dict[str, Any]) -> Dict[str, Any]:
        _ = state
        calls.append(name)
        if payload:
            return dict(payload)
        # LangGraph requires nodes to update at least one state key.
        return {"agent_outputs": {name: {"called": True}}}

    return _node


@pytest.mark.integration
@pytest.mark.workflow
def test_basic_workflow_runs_to_completion_with_stubbed_nodes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The workflow should compile and run end-to-end without network/LLM calls."""
    from company_researcher.workflows import basic_research as wf

    monkeypatch.setattr(builtins, "print", lambda *_a, **_k: None)

    calls: List[str] = []

    monkeypatch.setattr(
        wf,
        "classify_company_node",
        _make_stub_node(
            "classify_company",
            calls,
            {
                "company_classification": {"company_name": "TestCo", "region": "global"},
                "is_public_company": False,
                "stock_ticker": None,
                "available_data_sources": ["wikipedia"],
            },
        ),
    )
    monkeypatch.setattr(
        wf,
        "generate_queries_node",
        _make_stub_node("generate_queries", calls, {"search_queries": ["q1", "q2"]}),
    )
    monkeypatch.setattr(
        wf,
        "search_node",
        _make_stub_node(
            "search",
            calls,
            {
                "search_results": [{"title": "t", "url": "https://example.com", "content": "c"}],
                "sources": [{"title": "t", "url": "https://example.com"}],
                "search_trace": [
                    {"query": "q1", "provider": "duckduckgo", "success": True, "results": []}
                ],
                "search_stats": {"by_provider": {"duckduckgo": 1}},
            },
        ),
    )
    monkeypatch.setattr(wf, "sec_edgar_node", _make_stub_node("sec_edgar", calls, {"sec_data": {}}))
    monkeypatch.setattr(
        wf,
        "website_scraping_node",
        _make_stub_node("website_scraping", calls, {"scraped_content": {"pages": 0}}),
    )
    monkeypatch.setattr(
        wf,
        "analyze_node",
        _make_stub_node("analyze", calls, {"notes": ["note"], "company_overview": "overview"}),
    )
    monkeypatch.setattr(
        wf,
        "news_sentiment_node",
        _make_stub_node("news_sentiment", calls, {"news_sentiment": {"sentiment": "neutral"}}),
    )
    monkeypatch.setattr(
        wf,
        "extract_data_node",
        _make_stub_node("extract_data", calls, {"company_overview": "extracted"}),
    )

    def check_quality(state: Dict[str, Any]) -> Dict[str, Any]:
        calls.append("check_quality")
        return {"quality_score": 95.0, "iteration_count": state.get("iteration_count", 0) + 1}

    monkeypatch.setattr(wf, "check_quality_node", check_quality)
    monkeypatch.setattr(wf, "should_continue_research", lambda _s: "finish")

    monkeypatch.setattr(
        wf,
        "competitive_analysis_node",
        _make_stub_node("competitive_analysis", calls, {"competitive_matrix": {"ok": True}}),
    )
    monkeypatch.setattr(
        wf,
        "risk_assessment_node",
        _make_stub_node("risk_assessment", calls, {"risk_profile": {"level": "low"}}),
    )
    monkeypatch.setattr(
        wf,
        "investment_thesis_node",
        _make_stub_node("investment_thesis", calls, {"investment_thesis": {"thesis": "x"}}),
    )
    monkeypatch.setattr(
        wf,
        "save_report_node",
        _make_stub_node(
            "save_report",
            calls,
            {
                "report_path": "outputs/testco/report.md",
                "total_cost": 0.01,
                "total_tokens": {"input": 10, "output": 20},
            },
        ),
    )

    output = wf.research_company("TestCo")

    assert output["success"] is True
    assert output["company_name"] == "TestCo"
    assert output["report_path"] == "outputs/testco/report.md"
    assert output["metrics"]["iterations"] == 1
    assert output["metrics"]["sources_count"] == 1
    assert output["metrics"]["tokens"] == {"input": 10, "output": 20}

    assert calls[:3] == ["classify_company", "generate_queries", "search"]
    assert calls[-1] == "save_report"


@pytest.mark.integration
@pytest.mark.workflow
def test_basic_workflow_iteration_path_loops_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """The conditional edge should support iterating before finishing."""
    from company_researcher.workflows import basic_research as wf

    monkeypatch.setattr(builtins, "print", lambda *_a, **_k: None)

    calls: List[str] = []

    monkeypatch.setattr(wf, "classify_company_node", _make_stub_node("classify_company", calls, {}))
    monkeypatch.setattr(
        wf,
        "generate_queries_node",
        _make_stub_node("generate_queries", calls, {"search_queries": ["q"]}),
    )
    monkeypatch.setattr(
        wf,
        "search_node",
        _make_stub_node(
            "search",
            calls,
            {
                "search_results": [{"title": "t", "url": "https://example.com", "content": "c"}],
                "sources": [{"title": "t", "url": "https://example.com"}],
            },
        ),
    )
    monkeypatch.setattr(wf, "sec_edgar_node", _make_stub_node("sec_edgar", calls, {}))
    monkeypatch.setattr(wf, "website_scraping_node", _make_stub_node("website_scraping", calls, {}))
    monkeypatch.setattr(wf, "analyze_node", _make_stub_node("analyze", calls, {"notes": ["n"]}))
    monkeypatch.setattr(wf, "news_sentiment_node", _make_stub_node("news_sentiment", calls, {}))
    monkeypatch.setattr(wf, "extract_data_node", _make_stub_node("extract_data", calls, {}))

    def check_quality(state: Dict[str, Any]) -> Dict[str, Any]:
        calls.append("check_quality")
        return {"quality_score": 50.0, "iteration_count": state.get("iteration_count", 0) + 1}

    monkeypatch.setattr(wf, "check_quality_node", check_quality)
    monkeypatch.setattr(
        wf,
        "should_continue_research",
        lambda state: "iterate" if state.get("iteration_count", 0) < 2 else "finish",
    )

    monkeypatch.setattr(
        wf, "competitive_analysis_node", _make_stub_node("competitive_analysis", calls, {})
    )
    monkeypatch.setattr(wf, "risk_assessment_node", _make_stub_node("risk_assessment", calls, {}))
    monkeypatch.setattr(
        wf, "investment_thesis_node", _make_stub_node("investment_thesis", calls, {})
    )
    monkeypatch.setattr(
        wf, "save_report_node", _make_stub_node("save_report", calls, {"report_path": "p"})
    )

    output = wf.research_company("TestCo")
    assert output["success"] is True
    assert output["metrics"]["iterations"] == 2
    assert calls.count("generate_queries") == 2
    assert calls.count("check_quality") == 2
