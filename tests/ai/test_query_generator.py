"""Tests for AI query generator."""

import json
from unittest.mock import patch

import pytest

from company_researcher.ai.query import (
    AIQueryGenerator,
    CompanyContext,
    GeneratedQuery,
    QueryGenerationResult,
    QueryPurpose,
    get_query_generator,
)


class TestCompanyContext:
    """Test CompanyContext model."""

    def test_infer_languages_latam(self):
        """Test language inference for LATAM companies."""
        context = CompanyContext(company_name="Grupo Bimbo", known_region="LATAM")
        languages = context.get_inferred_languages()
        assert "en" in languages
        assert "es" in languages
        assert "pt" in languages

    def test_infer_languages_brazil(self):
        """Test language inference for Brazil."""
        context = CompanyContext(company_name="Petrobras", known_country="Brazil")
        languages = context.get_inferred_languages()
        assert "en" in languages
        assert "pt" in languages

    def test_infer_languages_mexico(self):
        """Test language inference for Mexico."""
        context = CompanyContext(company_name="FEMSA", known_country="Mexico")
        languages = context.get_inferred_languages()
        assert "en" in languages
        assert "es" in languages

    def test_infer_languages_default(self):
        """Test default language inference."""
        context = CompanyContext(company_name="Unknown Corp")
        languages = context.get_inferred_languages()
        assert languages == ["en"]

    def test_infer_languages_custom(self):
        """Test custom language list."""
        context = CompanyContext(company_name="SAP", languages=["en", "de"])
        languages = context.get_inferred_languages()
        assert languages == ["en", "de"]


class TestQueryPurpose:
    """Test QueryPurpose enum."""

    def test_required_purposes_public(self):
        """Test required purposes for public companies."""
        required = QueryPurpose.get_required_for_type("public")
        assert QueryPurpose.FINANCIAL in required
        assert QueryPurpose.OVERVIEW in required
        assert QueryPurpose.NEWS in required

    def test_required_purposes_startup(self):
        """Test required purposes for startups."""
        required = QueryPurpose.get_required_for_type("startup")
        assert QueryPurpose.FUNDING in required
        assert QueryPurpose.TECHNOLOGY in required

    def test_required_purposes_private(self):
        """Test required purposes for private companies."""
        required = QueryPurpose.get_required_for_type("private")
        assert QueryPurpose.OVERVIEW in required
        assert QueryPurpose.NEWS in required

    def test_required_purposes_conglomerate(self):
        """Test required purposes for conglomerates."""
        required = QueryPurpose.get_required_for_type("conglomerate")
        assert QueryPurpose.STRATEGY in required
        assert QueryPurpose.MARKET in required


class TestGeneratedQuery:
    """Test GeneratedQuery model."""

    def test_create_query(self):
        """Test creating a generated query."""
        query = GeneratedQuery(
            query="Tesla revenue 2024", purpose=QueryPurpose.FINANCIAL, language="en", priority=1
        )
        assert query.query == "Tesla revenue 2024"
        assert query.purpose == QueryPurpose.FINANCIAL.value
        assert query.priority == 1

    def test_query_defaults(self):
        """Test query defaults."""
        query = GeneratedQuery(query="Test query", purpose=QueryPurpose.OVERVIEW)
        assert query.language == "en"
        assert query.priority == 3
        assert query.is_fallback is False


class TestQueryGenerationResult:
    """Test QueryGenerationResult model."""

    def test_filter_by_purpose(self):
        """Test filtering queries by purpose."""
        result = QueryGenerationResult(
            queries=[
                GeneratedQuery(
                    query="Q1", purpose=QueryPurpose.FINANCIAL, language="en", priority=1
                ),
                GeneratedQuery(
                    query="Q2", purpose=QueryPurpose.FINANCIAL, language="es", priority=2
                ),
                GeneratedQuery(
                    query="Q3", purpose=QueryPurpose.PRODUCTS, language="en", priority=3
                ),
            ],
            total_queries=3,
        )

        financial = result.get_queries_by_purpose(QueryPurpose.FINANCIAL)
        assert len(financial) == 2

        products = result.get_queries_by_purpose(QueryPurpose.PRODUCTS)
        assert len(products) == 1

    def test_filter_by_language(self):
        """Test filtering queries by language."""
        result = QueryGenerationResult(
            queries=[
                GeneratedQuery(
                    query="Q1", purpose=QueryPurpose.FINANCIAL, language="en", priority=1
                ),
                GeneratedQuery(
                    query="Q2", purpose=QueryPurpose.FINANCIAL, language="es", priority=2
                ),
                GeneratedQuery(
                    query="Q3", purpose=QueryPurpose.PRODUCTS, language="en", priority=3
                ),
            ],
            total_queries=3,
        )

        english = result.get_queries_by_language("en")
        assert len(english) == 2

        spanish = result.get_queries_by_language("es")
        assert len(spanish) == 1

    def test_high_priority_queries(self):
        """Test getting high priority queries."""
        result = QueryGenerationResult(
            queries=[
                GeneratedQuery(
                    query="Q1", purpose=QueryPurpose.FINANCIAL, language="en", priority=1
                ),
                GeneratedQuery(
                    query="Q2", purpose=QueryPurpose.FINANCIAL, language="en", priority=2
                ),
                GeneratedQuery(
                    query="Q3", purpose=QueryPurpose.PRODUCTS, language="en", priority=3
                ),
            ],
            total_queries=3,
        )

        high_priority = result.get_high_priority_queries(max_priority=2)
        assert len(high_priority) == 2

    def test_to_query_list(self):
        """Test converting to simple query list."""
        result = QueryGenerationResult(
            queries=[
                GeneratedQuery(
                    query="Q3", purpose=QueryPurpose.PRODUCTS, language="en", priority=3
                ),
                GeneratedQuery(
                    query="Q1", purpose=QueryPurpose.FINANCIAL, language="en", priority=1
                ),
                GeneratedQuery(
                    query="Q2", purpose=QueryPurpose.FINANCIAL, language="en", priority=2
                ),
            ],
            total_queries=3,
        )

        query_list = result.to_query_list()
        # Should be sorted by priority
        assert query_list[0] == "Q1"
        assert query_list[1] == "Q2"
        assert query_list[2] == "Q3"


class TestAIQueryGenerator:
    """Test AI query generator."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return AIQueryGenerator()

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for query generation."""
        return json.dumps(
            {
                "queries": [
                    {
                        "query": "Tesla Inc annual report 2024",
                        "purpose": "financial",
                        "expected_sources": ["sec", "official"],
                        "language": "en",
                        "priority": 1,
                        "reasoning": "Official financial information",
                    },
                    {
                        "query": "Tesla revenue earnings Q4",
                        "purpose": "financial",
                        "expected_sources": ["news"],
                        "language": "en",
                        "priority": 2,
                        "reasoning": "Recent financial performance",
                    },
                    {
                        "query": "Tesla vs BYD market share",
                        "purpose": "competitors",
                        "expected_sources": ["industry_report"],
                        "language": "en",
                        "priority": 2,
                        "reasoning": "Competitive positioning",
                    },
                ],
                "company_context_inferred": {
                    "likely_industry": "Automotive",
                    "likely_type": "public",
                    "likely_region": "North America",
                },
                "suggested_follow_ups": ["Tesla SEC 10-K filing", "Tesla investor presentation"],
                "estimated_coverage": {"financial": 0.8, "products": 0.3, "competitors": 0.6},
            }
        )

    def test_generate_queries_success(self, generator, mock_llm_response):
        """Test successful query generation with mocked _call_llm."""
        # Use 'new=' instead of 'return_value=' for async method replacement
        with patch.object(generator, "_call_llm", new=lambda *args, **kwargs: mock_llm_response):
            context = CompanyContext(
                company_name="Tesla", is_public=True, known_industry="Automotive"
            )

            result = generator.generate_queries(context, num_queries=5)

            assert len(result.queries) == 3
            assert result.queries[0].purpose == QueryPurpose.FINANCIAL.value
            assert result.queries[0].priority == 1
            assert "Tesla" in result.queries[0].query

    def test_generate_queries_latam(self, generator):
        """Test query generation for LATAM company includes Spanish."""
        mock_response = json.dumps(
            {
                "queries": [
                    {
                        "query": "Grupo Bimbo informe anual",
                        "purpose": "financial",
                        "expected_sources": ["official"],
                        "language": "es",
                        "priority": 1,
                        "reasoning": "Spanish financial report",
                    },
                    {
                        "query": "Grupo Bimbo annual report",
                        "purpose": "financial",
                        "expected_sources": ["official"],
                        "language": "en",
                        "priority": 2,
                        "reasoning": "English financial report",
                    },
                ],
                "company_context_inferred": {"likely_region": "LATAM"},
                "suggested_follow_ups": [],
                "estimated_coverage": {"financial": 0.7},
            }
        )

        with patch.object(generator, "_call_llm", new=lambda *args, **kwargs: mock_response):
            context = CompanyContext(company_name="Grupo Bimbo", known_region="LATAM")

            result = generator.generate_queries(context)

            # Should have queries in multiple languages
            languages = {q.language for q in result.queries}
            assert "es" in languages or "en" in languages

    def test_fallback_on_llm_failure(self, generator, mock_smart_client):
        """Test that generator falls back to legacy queries when LLM fails."""
        mock_smart_client.complete.side_effect = Exception("LLM error")

        context = CompanyContext(company_name="Test Corp")
        # Generator should fall back to legacy templates, not raise
        result = generator.generate_queries(context, num_queries=5)

        # Verify we got fallback results
        assert isinstance(result, QueryGenerationResult)
        assert len(result.queries) > 0
        # All fallback queries should be marked as fallback
        assert all(q.is_fallback for q in result.queries)
        # All fallback queries should contain the company name
        assert any("Test Corp" in q.query for q in result.queries)

    def test_parse_generation_result(self, generator):
        """Test parsing of generation result."""
        data = {
            "queries": [
                {"query": "Test query", "purpose": "overview", "language": "en", "priority": 1}
            ],
            "company_context_inferred": {"likely_industry": "Tech"},
            "estimated_coverage": {"overview": 0.8},
        }

        result = generator._parse_generation_result(data, ["en"])

        assert len(result.queries) == 1
        assert result.queries[0].query == "Test query"
        assert result.company_context_inferred["likely_industry"] == "Tech"


class TestQueryGeneratorSingleton:
    """Test singleton behavior."""

    def test_get_query_generator_returns_same_instance(self):
        """Test that get_query_generator returns singleton."""
        # Reset the singleton first
        import company_researcher.ai.query.generator as gen_module

        gen_module._generator_instance = None

        gen1 = get_query_generator()
        gen2 = get_query_generator()
        assert gen1 is gen2


class TestQueryGenerationIntegration:
    """Integration tests for query generation."""

    def test_full_workflow(self, mock_smart_client):
        """Test full query generation workflow."""
        mock_response = json.dumps(
            {
                "queries": [
                    {
                        "query": "Tesla financial report 2024",
                        "purpose": "financial",
                        "expected_sources": ["sec"],
                        "language": "en",
                        "priority": 1,
                        "reasoning": "Financial data",
                    },
                    {
                        "query": "Tesla competitors electric vehicles",
                        "purpose": "competitors",
                        "expected_sources": ["news"],
                        "language": "en",
                        "priority": 2,
                        "reasoning": "Competitive analysis",
                    },
                ],
                "company_context_inferred": {},
                "suggested_follow_ups": [],
                "estimated_coverage": {},
            }
        )

        mock_smart_client.complete.return_value.content = mock_response

        generator = get_query_generator()
        context = CompanyContext(
            company_name="Tesla", known_industry="Automotive", is_public=True, stock_ticker="TSLA"
        )

        result = generator.generate_queries(context, num_queries=5)

        # Verify result structure
        assert isinstance(result, QueryGenerationResult)
        assert len(result.queries) > 0

        # Verify queries are valid
        for query in result.queries:
            assert query.query
            assert query.purpose
            assert query.language

        # Verify query list generation
        query_list = result.to_query_list()
        assert isinstance(query_list, list)
        assert all(isinstance(q, str) for q in query_list)
