"""Unit tests for the cost-first search router."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List

import pytest

from company_researcher.integrations.search_router import SearchResponse, SearchResult, SearchRouter


def _results(n: int, source: str) -> List[SearchResult]:
    return [
        SearchResult(
            title=f"t{i}",
            url=f"https://example.com/{i}",
            snippet="s",
            source=source,
            score=0.5,
        )
        for i in range(n)
    ]


@pytest.mark.unit
def test_search_returns_cached_response_when_sufficient_and_allowed(
    mocker: Any, tmp_path: Path
) -> None:
    """A cache hit with sufficient results should short-circuit provider execution."""
    mocker.patch("company_researcher.integrations.search_router.get_config", return_value="")

    router = SearchRouter(cache_dir=str(tmp_path / "cache"))
    cached = SearchResponse(
        query="q",
        provider="duckduckgo",
        quality_tier="free",
        results=_results(3, "duckduckgo"),
        success=True,
        cached=True,
    )

    router._persistent_cache = mocker.Mock()
    router._persistent_cache.get.return_value = cached

    # If we return cached, we should never compute provider order or call providers.
    router._get_provider_order = mocker.Mock()
    router._search_provider = mocker.Mock()

    result = router.search("q", quality="free", max_results=10, use_cache=True, min_results=3)

    assert result is cached
    assert router._cache_hits == 1
    router._get_provider_order.assert_not_called()
    router._search_provider.assert_not_called()


@pytest.mark.unit
def test_search_reuses_cached_results_even_if_from_paid_provider(
    mocker: Any, tmp_path: Path
) -> None:
    """Cached results should be reused regardless of provider (cache costs $0 at runtime)."""
    mocker.patch("company_researcher.integrations.search_router.get_config", return_value="")

    router = SearchRouter(cache_dir=str(tmp_path / "cache"))
    cached_paid = SearchResponse(
        query="q",
        provider="tavily",
        quality_tier="premium",
        results=_results(10, "tavily"),
        success=True,
        cached=True,
    )

    router._persistent_cache = mocker.Mock()
    router._persistent_cache.get.return_value = cached_paid

    result = router.search("q", quality="free", max_results=10, use_cache=True, min_results=3)

    assert result is cached_paid
    assert router._cache_hits == 1


@pytest.mark.unit
def test_get_provider_order_filters_to_available_providers(mocker: Any, tmp_path: Path) -> None:
    """Tier provider ordering should be filtered to providers that are actually available."""
    mocker.patch("company_researcher.integrations.search_router.get_config", return_value="")

    router = SearchRouter(cache_dir=str(tmp_path / "cache"))

    # With no API keys, only providers that don't require credentials should remain.
    assert router._get_provider_order("free") == ["duckduckgo", "wikipedia"]
    assert router._get_provider_order("premium") == ["duckduckgo", "wikipedia"]


@pytest.mark.unit
def test_search_skips_paid_provider_when_budget_is_zero(mocker: Any, tmp_path: Path) -> None:
    """Paid providers should be skipped when PAID_SEARCH_BUDGET_USD is 0."""
    mocker.patch("company_researcher.integrations.search_router.get_config", return_value="")

    router = SearchRouter(cache_dir=str(tmp_path / "cache"), paid_search_budget_usd=0.0)
    router._persistent_cache = mocker.Mock()
    router._persistent_cache.get.return_value = None

    router._get_provider_order = mocker.Mock(return_value=["duckduckgo", "serper"])
    ddg = SearchResponse(
        query="q",
        provider="duckduckgo",
        quality_tier="free",
        results=_results(1, "duckduckgo"),
        success=True,
    )
    router._safe_search_provider = mocker.Mock(return_value=ddg)

    result = router.search("q", quality="premium", max_results=10, use_cache=True, min_results=3)

    assert result.provider == "duckduckgo"
    assert router._safe_search_provider.call_count == 1
