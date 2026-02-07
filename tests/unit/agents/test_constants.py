"""Tests for centralized agent constants."""

from __future__ import annotations

from company_researcher.agents.constants import (
    AgentDefaults,
    DisplayConstants,
    ExtractionConstants,
    FormattingConstants,
    QualityConstants,
    SearchConstants,
)


def test_constants_have_expected_types_and_invariants() -> None:
    """Constants should be importable and provide sane, stable defaults."""
    assert isinstance(FormattingConstants.CONTENT_TRUNCATE_LENGTH, int)
    assert FormattingConstants.CONTENT_TRUNCATE_SHORT < FormattingConstants.CONTENT_TRUNCATE_LENGTH
    assert FormattingConstants.CONTENT_TRUNCATE_LENGTH < FormattingConstants.CONTENT_TRUNCATE_LONG

    assert isinstance(FormattingConstants.MAX_SOURCES_DEFAULT, int)
    assert FormattingConstants.MAX_SOURCES_QUICK < FormattingConstants.MAX_SOURCES_DEFAULT
    assert FormattingConstants.MAX_SOURCES_DEFAULT <= FormattingConstants.MAX_SOURCES_DETAILED

    assert isinstance(ExtractionConstants.MIN_CONTENT_LENGTH, int)
    assert isinstance(ExtractionConstants.MIN_ITEM_LENGTH, int)
    assert ExtractionConstants.MIN_ITEM_LENGTH <= ExtractionConstants.MIN_CONTENT_LENGTH

    assert isinstance(ExtractionConstants.DEFAULT_SCORE, float)
    assert 0.0 <= ExtractionConstants.DEFAULT_SCORE <= ExtractionConstants.MAX_SCORE

    assert isinstance(AgentDefaults.DEFAULT_MAX_TOKENS, int)
    assert AgentDefaults.DEFAULT_MAX_TOKENS > 0
    assert isinstance(AgentDefaults.DEFAULT_TEMPERATURE, float)
    assert AgentDefaults.DEFAULT_TEMPERATURE <= AgentDefaults.CREATIVE_TEMPERATURE

    assert isinstance(QualityConstants.QUALITY_PASS_THRESHOLD, float)
    assert 0.0 <= QualityConstants.QUALITY_PASS_THRESHOLD <= 100.0
    assert (
        0.0
        <= QualityConstants.MEDIUM_CONFIDENCE_THRESHOLD
        <= QualityConstants.HIGH_CONFIDENCE_THRESHOLD
        <= 1.0
    )

    assert isinstance(SearchConstants.MAX_RESULTS_PER_QUERY, int)
    assert SearchConstants.MAX_RESULTS_PER_QUERY > 0
    assert SearchConstants.MAX_QUERIES_DEFAULT < SearchConstants.MAX_QUERIES_DEEP

    assert DisplayConstants.STATUS_OK
    assert DisplayConstants.STATUS_ERROR
    assert DisplayConstants.PREFIX_FORMAT.count("{") == 1
