"""Unit tests for the Analyst agent."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from company_researcher.agents.core import analyst as analyst_module


def _make_usage(input_tokens: int, output_tokens: int) -> Any:
    return SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens)


def _make_llm_response(input_tokens: int, output_tokens: int) -> Any:
    return SimpleNamespace(usage=_make_usage(input_tokens, output_tokens))


@pytest.mark.unit
def test_analyst_node_returns_defaults_when_no_search_results(mocker: Any) -> None:
    """When no search results are present, the node should return a safe default payload."""
    mocker.patch.object(analyst_module, "QUALITY_MODULES_AVAILABLE", False)
    mocker.patch.object(analyst_module, "get_anthropic_client")

    result = analyst_module.analyst_agent_node(
        {
            "company_name": "TestCo",
            "search_results": [],
            "sources": [],
        }
    )

    assert result["notes"] == ["No search results available for analysis."]
    assert result["company_overview"] == "Not available in research"
    assert result["data_quality"]["passes_threshold"] is False
    assert result["agent_outputs"]["analyst"]["sources_analyzed"] == 0
    assert result["agent_outputs"]["analyst"]["data_extracted"] is False
    assert result["agent_outputs"]["analyst"]["cost"] == 0.0


@pytest.mark.unit
def test_analyst_node_runs_without_quality_modules(mocker: Any) -> None:
    """Without optional quality modules, the node should still run using default quality results."""
    mocker.patch.object(analyst_module, "QUALITY_MODULES_AVAILABLE", False)

    mock_config = SimpleNamespace(llm_model="mock-model", llm_max_tokens=123, llm_temperature=0.0)
    mocker.patch.object(analyst_module, "get_config", return_value=mock_config)

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=mocker.Mock()))
    fake_client.messages.create.side_effect = [
        _make_llm_response(10, 20),  # analysis
        _make_llm_response(30, 40),  # extraction
    ]
    mocker.patch.object(analyst_module, "get_anthropic_client", return_value=fake_client)

    mocker.patch.object(
        analyst_module,
        "safe_extract_text",
        side_effect=["NOTES_TEXT", "EXTRACTED_DATA_TEXT"],
    )
    mocker.patch.object(analyst_module, "calculate_cost", side_effect=[0.01, 0.02])
    mocker.patch.object(
        analyst_module, "format_search_results_for_analysis", return_value="FORMATTED"
    )
    mocker.patch.object(analyst_module, "format_sources_for_extraction", return_value="SOURCES")

    state: Dict[str, Any] = {
        "company_name": "TestCo",
        "search_results": [{"title": "t", "url": "u", "content": "c"}],
        "sources": [{"title": "t", "url": "u"}],
    }

    result = analyst_module.analyst_agent_node(state)

    assert result["company_overview"] == "EXTRACTED_DATA_TEXT"
    assert result["notes"] == ["NOTES_TEXT"]
    assert result["data_quality"]["note"].startswith("Quality modules not available")

    analyst_out = result["agent_outputs"]["analyst"]
    assert analyst_out["sources_analyzed"] == 1
    assert analyst_out["data_extracted"] is True
    assert analyst_out["cost"] == pytest.approx(0.03)
    assert analyst_out["tokens"]["input"] == 40
    assert analyst_out["tokens"]["output"] == 60
    # In the fallback branch, quality_result defaults are used, but the numeric tracking value stays 0.
    assert analyst_out["quality_score"] == 0
    assert result["data_quality"]["score"] == 50.0


@pytest.mark.unit
def test_analyst_node_runs_with_quality_modules(mocker: Any) -> None:
    """With quality modules enabled, the node should populate the data_quality payload from validators."""
    mocker.patch.object(analyst_module, "QUALITY_MODULES_AVAILABLE", True)

    mock_config = SimpleNamespace(llm_model="mock-model", llm_max_tokens=123, llm_temperature=0.0)
    mocker.patch.object(analyst_module, "get_config", return_value=mock_config)

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=mocker.Mock()))
    fake_client.messages.create.side_effect = [
        _make_llm_response(5, 6),  # analysis
        _make_llm_response(7, 8),  # extraction
    ]
    mocker.patch.object(analyst_module, "get_anthropic_client", return_value=fake_client)

    mocker.patch.object(
        analyst_module,
        "safe_extract_text",
        side_effect=["NOTES_TEXT", "EXTRACTED_DATA_TEXT"],
    )
    mocker.patch.object(analyst_module, "calculate_cost", side_effect=[0.1, 0.2])
    mocker.patch.object(
        analyst_module, "format_search_results_for_analysis", return_value="FORMATTED"
    )
    mocker.patch.object(analyst_module, "format_sources_for_extraction", return_value="SOURCES")

    validation_result = SimpleNamespace(
        score=42.0,
        warnings=["warn-1", "warn-2"],
        retry_recommended=True,
        recommended_queries=["q1"],
        is_valid=False,
        metrics_found={"revenue": "1B"},
        metrics_missing=["profit"],
        critical_missing=["cash"],
        company_type=SimpleNamespace(value="public"),
    )
    quality_gate = SimpleNamespace(can_generate=False, status=SimpleNamespace(value="blocked"))

    metrics_validator = SimpleNamespace(
        validate_metrics=mocker.Mock(return_value=validation_result)
    )
    quality_enforcer = SimpleNamespace(check_quality=mocker.Mock(return_value=quality_gate))

    mocker.patch.object(analyst_module, "create_metrics_validator", return_value=metrics_validator)
    mocker.patch.object(analyst_module, "create_quality_enforcer", return_value=quality_enforcer)

    result = analyst_module.analyst_agent_node(
        {
            "company_name": "TestCo",
            "search_results": [{"title": "t", "url": "u", "content": "c"}],
            "sources": [{"title": "t", "url": "u"}],
        }
    )

    assert result["company_overview"] == "EXTRACTED_DATA_TEXT"
    assert "**Data Quality Warnings:**" in result["notes"][0]

    quality = result["data_quality"]
    assert quality["score"] == 42.0
    assert quality["passes_threshold"] is False
    assert quality["can_generate_report"] is False
    assert quality["retry_recommended"] is True
    assert quality["recommended_queries"] == ["q1"]
    assert quality["metrics_found"] == ["revenue"]
    assert quality["critical_missing"] == ["cash"]
    assert quality["quality_gate_status"] == "blocked"

    analyst_out = result["agent_outputs"]["analyst"]
    assert analyst_out["cost"] == pytest.approx(0.3)
    assert analyst_out["can_generate_report"] is False
    assert analyst_out["retry_recommended"] is True
    assert analyst_out["tokens"]["input"] == 12
    assert analyst_out["tokens"]["output"] == 14
