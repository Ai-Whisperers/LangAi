"""Unit tests for the Researcher agent."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from company_researcher.agents.core import researcher as researcher_module


@pytest.mark.unit
def test_detect_company_region_from_company_name_latam_indicator() -> None:
    """Region detection should pick up LATAM hints directly from the company name."""
    assert researcher_module._detect_company_region("Acme México S.A.") == "mexico"
    assert researcher_module._detect_company_region("Empresa Brasil LTDA") == "brazil"


@pytest.mark.unit
def test_detect_company_region_from_initial_results_needs_multiple_hits() -> None:
    """Region detection from results should require multiple indicator matches."""
    initial_results: List[Dict[str, Any]] = [
        {"title": "Brasil - B3 listing", "content": "B3 Bovespa SA company profile"},
        {"title": "Relatório anual", "content": "brasileiro brasil"},
    ]
    assert researcher_module._detect_company_region("UnknownCo", initial_results) == "brazil"


@pytest.mark.unit
def test_identify_company_domains_prefers_company_domain_and_official_paths() -> None:
    """Company domain identification should return up to 2 likely official URLs."""
    results = [
        {
            "title": "About TestCorp",
            "url": "https://www.testcorp.com/about",
            "content": "About page",
        },
        {
            "title": "Investors | TestCorp",
            "url": "https://www.testcorp.com/investors",
            "content": "Investor relations",
        },
        {
            "title": "TestCorp overview",
            "url": "https://example.com/company/testcorp",
            "content": "Third-party overview",
        },
        # Duplicate domain should be ignored
        {
            "title": "Duplicate domain",
            "url": "https://testcorp.com/company",
            "content": "Duplicate",
        },
    ]

    domains = researcher_module._identify_company_domains(results, "TestCorp Inc.")
    assert len(domains) <= 2
    assert any("testcorp.com" in d for d in domains)


@pytest.mark.unit
def test_generate_multilingual_queries_falls_back_without_enhancements(mocker: Any) -> None:
    """If enhancement modules are missing, multilingual query generation should fall back to basic queries."""
    mocker.patch.object(researcher_module, "ENHANCEMENTS_AVAILABLE", False)
    queries = researcher_module._generate_multilingual_queries(
        "TestCo", "mexico", topics=["revenue"]
    )
    assert isinstance(queries, list)
    assert len(queries) == 5
    assert any("company overview" in q for q in queries)


@pytest.mark.unit
def test_researcher_node_uses_fallback_queries_and_dedupes_sources(mocker: Any) -> None:
    """The node should work deterministically with mocked Tavily/LLM clients and dedupe source URLs."""
    mocker.patch.object(researcher_module, "ENHANCEMENTS_AVAILABLE", False)
    mocker.patch.object(researcher_module, "_detect_company_region", return_value="united_states")

    mock_config = SimpleNamespace(
        llm_model="mock-model",
        researcher_max_tokens=111,
        researcher_temperature=0.0,
        enable_domain_exploration=False,
    )
    mocker.patch.object(researcher_module, "get_config", return_value=mock_config)

    fake_llm_client = SimpleNamespace(
        messages=SimpleNamespace(create=mocker.Mock(return_value=object()))
    )
    mocker.patch.object(researcher_module, "get_anthropic_client", return_value=fake_llm_client)

    # Force fallback queries by returning a non-list from safe_extract_json
    mocker.patch.object(researcher_module, "safe_extract_json", return_value={"not": "a list"})

    fake_tavily = SimpleNamespace(search=mocker.Mock())
    fake_tavily.search.side_effect = [
        # Initial search (1 result)
        {
            "results": [
                {"title": "Init", "url": "https://example.com", "score": 0.9, "content": "init"}
            ]
        },
        # Query 1: includes duplicate + new
        {
            "results": [
                {"title": "Dup", "url": "https://example.com", "score": 0.8, "content": "dup"},
                {"title": "New", "url": "https://new.com", "score": 0.7, "content": "new"},
            ]
        },
        # Query 2: one more
        {
            "results": [
                {"title": "Another", "url": "https://another.com", "score": 0.6, "content": "a"}
            ]
        },
        # Query 3-5: empty
        {"results": []},
        {"results": []},
        {"results": []},
    ]
    mocker.patch.object(researcher_module, "get_tavily_client", return_value=fake_tavily)

    result = researcher_module.researcher_agent_node({"company_name": "TestCo", "missing_info": []})

    assert result["company_region"] == "united_states"
    assert result["agent_outputs"]["researcher"]["queries_generated"] == 5
    assert result["agent_outputs"]["researcher"]["sources_found"] == 3

    urls = [s["url"] for s in result["sources"]]
    assert urls.count("https://example.com") == 1
    assert "https://new.com" in urls
    assert "https://another.com" in urls
