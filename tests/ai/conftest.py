"""Pytest fixtures for AI component tests."""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from company_researcher.ai.config import AIComponentConfig, AIConfig, reset_ai_config, set_ai_config


@pytest.fixture
def ai_config_enabled():
    """AI config with all components enabled."""
    config = AIConfig(
        global_enabled=True,
        sentiment=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        query_generation=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        quality_assessment=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        data_extraction=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        classification=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        contradiction_detection=AIComponentConfig(enabled=True, fallback_to_legacy=True),
    )
    set_ai_config(config)
    yield config
    # Reset after test
    reset_ai_config()


@pytest.fixture
def ai_config_disabled():
    """AI config with all components disabled."""
    config = AIConfig(
        global_enabled=False,
    )
    set_ai_config(config)
    yield config
    reset_ai_config()


@pytest.fixture
def ai_config_sentiment_only():
    """AI config with only sentiment enabled."""
    config = AIConfig(
        global_enabled=True,
        sentiment=AIComponentConfig(enabled=True, fallback_to_legacy=True),
        query_generation=AIComponentConfig(enabled=False),
        quality_assessment=AIComponentConfig(enabled=False),
        data_extraction=AIComponentConfig(enabled=False),
    )
    set_ai_config(config)
    yield config
    reset_ai_config()


@pytest.fixture
def mock_smart_client():
    """Mock smart LLM client."""
    with patch("company_researcher.llm.get_smart_client") as mock:
        client = MagicMock()
        client.complete = MagicMock(
            return_value=MagicMock(
                content='{"result": "test"}', cost=0.01, input_tokens=100, output_tokens=50
            )
        )
        mock.return_value = client
        yield client


@pytest.fixture
def mock_async_smart_client():
    """Mock async smart LLM client."""
    with patch("company_researcher.llm.get_smart_client") as mock:
        client = AsyncMock()
        client.complete = AsyncMock(
            return_value=MagicMock(
                content='{"result": "test"}', cost=0.01, input_tokens=100, output_tokens=50
            )
        )
        mock.return_value = client
        yield client


@pytest.fixture
def sample_company_context() -> Dict[str, Any]:
    """Sample company context for testing."""
    return {
        "company_name": "Tesla",
        "known_industry": "Automotive",
        "known_region": "North America",
        "is_public": True,
        "stock_ticker": "TSLA",
    }


@pytest.fixture
def sample_latam_company_context() -> Dict[str, Any]:
    """Sample LATAM company context for testing."""
    return {
        "company_name": "Grupo Bimbo",
        "known_industry": "Food & Beverage",
        "known_region": "Latin America",
        "country": "Mexico",
        "is_public": True,
        "stock_ticker": "BIMBOA",
    }


@pytest.fixture
def sample_search_results() -> list:
    """Sample search results for testing."""
    return [
        {
            "url": "https://example.com/tesla-revenue",
            "title": "Tesla Reports Record Revenue",
            "snippet": "Tesla reported $81.5 billion in revenue for 2023, a 19% increase.",
            "content": "Tesla Inc. reported record revenue of $81.5 billion for fiscal year 2023...",
        },
        {
            "url": "https://news.example.com/tesla-growth",
            "title": "Tesla Growth Analysis",
            "snippet": "Tesla's market share in EVs continues to grow despite competition.",
            "content": "Analysis shows Tesla maintains 20% market share in global EV market...",
        },
    ]


@pytest.fixture
def sample_article_text() -> str:
    """Sample news article text for sentiment testing."""
    return """
    Tesla Reports Record Q4 Earnings, Stock Surges

    Tesla Inc. announced record fourth-quarter earnings on Wednesday,
    beating analyst expectations and sending shares up 12% in after-hours trading.

    Revenue reached $25.2 billion, up 3% year-over-year, while net income
    came in at $7.9 billion. CEO Elon Musk called the results "a testament
    to our incredible team and the growing demand for sustainable transportation."

    However, some analysts expressed concern about margin compression,
    noting that gross margins fell to 17.6% from 23.8% a year ago due to
    aggressive price cuts.

    Competitor BYD reported declining sales in the same quarter, which
    analysts say helped Tesla maintain its market leadership position.
    """


@pytest.fixture
def sample_negative_article() -> str:
    """Sample negative news article for sentiment testing."""
    return """
    Tesla Faces Mounting Challenges as Sales Decline

    Tesla Inc. reported disappointing quarterly results, with sales falling
    5% year-over-year amid increasing competition and economic headwinds.

    The company announced layoffs affecting 10% of its workforce, raising
    concerns about its growth trajectory. Analysts downgraded the stock
    following the announcement, citing margin pressures and slowing demand.

    Quality issues continue to plague the automaker, with multiple recalls
    announced in recent months. Customer satisfaction scores have declined
    significantly according to recent surveys.
    """


@pytest.fixture
def sample_mixed_article() -> str:
    """Sample mixed sentiment article for testing."""
    return """
    Tesla Q3 Results Show Mixed Picture

    Tesla delivered strong revenue growth of 15% this quarter, but profits
    fell short of expectations due to rising costs and price cuts.

    The company's energy business showed promising growth, while the core
    automotive segment faced increasing competition. Management remains
    optimistic about long-term prospects despite near-term challenges.

    Analysts are divided on the outlook, with some seeing opportunity
    in the recent stock decline while others remain cautious about
    margin sustainability.
    """


class MockLLMResponse:
    """Mock LLM response for testing."""

    def __init__(
        self, content: str, cost: float = 0.01, input_tokens: int = 100, output_tokens: int = 50
    ):
        self.content = content
        self.cost = cost
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


def create_mock_response(json_data: Dict[str, Any], cost: float = 0.01) -> MockLLMResponse:
    """Create a mock LLM response with JSON data."""
    import json

    return MockLLMResponse(content=json.dumps(json_data), cost=cost)


@pytest.fixture
def mock_sentiment_response():
    """Mock sentiment analysis response."""
    return create_mock_response(
        {
            "overall_sentiment": "positive",
            "overall_score": 0.75,
            "confidence": 0.85,
            "key_factors": [
                "Record revenue growth",
                "Strong market position",
                "Positive executive commentary",
            ],
            "entity_sentiments": [
                {"entity": "Tesla", "sentiment": "positive", "score": 0.8},
                {"entity": "BYD", "sentiment": "negative", "score": -0.3},
            ],
        }
    )


@pytest.fixture
def mock_query_generation_response():
    """Mock query generation response."""
    return create_mock_response(
        {
            "queries": [
                {
                    "query": "Tesla revenue 2023 financial results",
                    "purpose": "financials",
                    "language": "en",
                    "priority": 1,
                },
                {
                    "query": "Tesla market share electric vehicles",
                    "purpose": "market_position",
                    "language": "en",
                    "priority": 2,
                },
            ]
        }
    )


@pytest.fixture
def mock_quality_assessment_response():
    """Mock quality assessment response."""
    return create_mock_response(
        {
            "overall_score": 0.72,
            "ready_for_delivery": False,
            "iteration_needed": True,
            "section_assessments": [
                {
                    "section_name": "financials",
                    "quality_level": "good",
                    "score": 0.8,
                    "issues": [],
                    "missing_topics": [],
                },
                {
                    "section_name": "competitive_analysis",
                    "quality_level": "needs_improvement",
                    "score": 0.55,
                    "issues": ["Lacks specific competitor data"],
                    "missing_topics": ["Market share comparison", "Competitor financials"],
                },
            ],
            "focus_areas_for_iteration": ["competitive_analysis", "market_position"],
        }
    )
