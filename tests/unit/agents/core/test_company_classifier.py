"""Unit tests for the company classifier."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from company_researcher.agents.core.company_classifier import (
    CompanyClassification,
    CompanyClassifier,
    CompanyType,
    Region,
    classify_company_node,
)


@pytest.mark.unit
def test_detect_region_from_latam_keyword(mocker: Any) -> None:
    """Region detection should identify LATAM conglomerate keywords."""
    mocker.patch.object(CompanyClassifier, "_init_integrations", lambda self: None)
    classifier = CompanyClassifier()
    assert classifier._detect_region_from_name("Grupo Bimbo") == Region.LATIN_AMERICA


@pytest.mark.unit
def test_detect_region_from_suffix(mocker: Any) -> None:
    """Region detection should identify region-specific legal suffixes."""
    mocker.patch.object(CompanyClassifier, "_init_integrations", lambda self: None)
    classifier = CompanyClassifier()
    assert classifier._detect_region_from_name("Acme GmbH") == Region.EUROPE


@pytest.mark.unit
def test_extract_country_from_location(mocker: Any) -> None:
    """Country extraction should map common location strings to ISO-ish codes."""
    mocker.patch.object(CompanyClassifier, "_init_integrations", lambda self: None)
    classifier = CompanyClassifier()
    assert classifier._extract_country("Paris, France") == "FR"
    assert classifier._extract_country("São Paulo, Brasil") == "BR"
    assert classifier._extract_country("Ciudad de México") == "MX"


@pytest.mark.unit
def test_determine_data_sources_public_north_america_with_ticker(mocker: Any) -> None:
    """Data sources should include public-market sources for NA public companies with a ticker."""
    mocker.patch.object(CompanyClassifier, "_init_integrations", lambda self: None)
    classifier = CompanyClassifier()

    result = CompanyClassification(
        company_name="TestCo",
        is_public=True,
        ticker="TEST",
        region=Region.NORTH_AMERICA,
        company_type=CompanyType.PUBLIC,
    )
    classifier._determine_data_sources(result)

    assert "tavily" in result.data_sources
    assert "wikipedia" in result.data_sources
    assert "yfinance" in result.data_sources
    assert "sec_edgar" in result.data_sources
    assert "polygon" in result.data_sources
    assert len(result.data_sources) == len(set(result.data_sources))


@pytest.mark.unit
def test_classify_company_node_cache_hit(mocker: Any) -> None:
    """If cache returns data, the node should avoid classification and return cached payload."""
    cached: Dict[str, Any] = {
        "company_name": "CachedCo",
        "is_public": True,
        "ticker": "CCH",
        "region": "north_america",
        "data_sources": ["wikipedia"],
    }

    mocker.patch(
        "company_researcher.cache.result_cache.get_cached_classification", return_value=cached
    )
    mocker.patch("company_researcher.cache.result_cache.cache_classification")
    mocker.patch("company_researcher.agents.core.company_classifier.get_company_classifier")

    result = classify_company_node({"company_name": "CachedCo"})

    assert result["company_classification"] == cached
    assert result["is_public_company"] is True
    assert result["stock_ticker"] == "CCH"
    assert result["detected_region"] == "north_america"
    assert result["available_data_sources"] == ["wikipedia"]


@pytest.mark.unit
def test_classify_company_node_cache_miss_caches_result(mocker: Any) -> None:
    """On cache miss, the node should classify and then store the result."""
    mocker.patch(
        "company_researcher.cache.result_cache.get_cached_classification", return_value=None
    )
    cache_mock = mocker.patch("company_researcher.cache.result_cache.cache_classification")

    fake_classifier = mocker.Mock()
    classification = CompanyClassification(
        company_name="TestCo",
        is_public=False,
        ticker=None,
        region=Region.EUROPE,
        company_type=CompanyType.PRIVATE,
        data_sources=["wikipedia", "tavily"],
        confidence=0.6,
    )
    fake_classifier.classify.return_value = classification
    mocker.patch(
        "company_researcher.agents.core.company_classifier.get_company_classifier",
        return_value=fake_classifier,
    )

    result = classify_company_node({"company_name": "TestCo"})

    assert result["is_public_company"] is False
    assert result["stock_ticker"] is None
    assert result["detected_region"] == Region.EUROPE.value
    assert "wikipedia" in result["available_data_sources"]

    cache_mock.assert_called_once()
    cached_name, cached_payload = cache_mock.call_args.args
    assert cached_name == "TestCo"
    assert cached_payload["company_name"] == "TestCo"
