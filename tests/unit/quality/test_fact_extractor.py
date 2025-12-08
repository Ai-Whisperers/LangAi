"""
Unit Tests for Fact Extractor (Phase 10).

Tests fact extraction, entity detection, categorization, and confidence assessment.
"""

import pytest
from company_researcher.quality.fact_extractor import (
    FactExtractor,
    ExtractedFact,
    FactCategory,
    ClaimType,
    extract_facts,
    extract_from_all_agents
)


@pytest.mark.unit
@pytest.mark.quality
class TestFactExtractor:
    """Test suite for FactExtractor class."""

    def test_initialization(self):
        """Test FactExtractor initialization."""
        extractor = FactExtractor()
        assert extractor is not None
        assert len(extractor._numerical_patterns) > 0

    def test_extract_numerical_facts(self):
        """Test extraction of numerical facts."""
        extractor = FactExtractor()
        text = "The company reported revenue of $1.5 billion in 2023 with 25% profit margin."

        result = extractor.extract(text, agent_name="test")

        assert result.total_facts > 0
        assert any(fact.claim_type == ClaimType.NUMERICAL for fact in result.facts)
        assert any("1.5 billion" in fact.content or "25%" in fact.content for fact in result.facts)

    def test_extract_temporal_facts(self):
        """Test extraction of temporal facts."""
        extractor = FactExtractor()
        text = "The company was founded in 2010 and launched its flagship product in 2015."

        result = extractor.extract(text, agent_name="test")

        assert result.total_facts > 0
        temporal_facts = [f for f in result.facts if f.claim_type == ClaimType.TEMPORAL]
        assert len(temporal_facts) > 0

    def test_extract_comparative_facts(self):
        """Test extraction of comparative claims."""
        extractor = FactExtractor()
        text = "Company A is larger than Company B and has better performance than the industry average."

        result = extractor.extract(text, agent_name="test")

        comparative_facts = [f for f in result.facts if f.claim_type == ClaimType.COMPARATIVE]
        assert len(comparative_facts) > 0

    def test_categorize_financial_facts(self):
        """Test categorization of financial facts."""
        extractor = FactExtractor()
        text = "The company's revenue grew to $500 million with EBITDA of $100 million."

        result = extractor.extract(text, agent_name="financial")

        financial_facts = [f for f in result.facts if f.category == FactCategory.FINANCIAL]
        assert len(financial_facts) > 0

    def test_categorize_market_facts(self):
        """Test categorization of market facts."""
        extractor = FactExtractor()
        text = "The TAM is estimated at $50 billion with 15% CAGR growth rate."

        result = extractor.extract(text, agent_name="market")

        market_facts = [f for f in result.facts if f.category == FactCategory.MARKET]
        assert len(market_facts) > 0

    def test_extract_entities(self):
        """Test entity extraction from facts."""
        extractor = FactExtractor()
        text = "Apple Inc. reported revenue of $365 billion in fiscal year 2023."

        result = extractor.extract(text, agent_name="test")

        assert len(result.entities) > 0
        # Should extract both the company name and numbers
        assert any(e.entity_type == "number" for e in result.entities)

    def test_confidence_assessment(self):
        """Test confidence score calculation."""
        extractor = FactExtractor()

        # High confidence: specific numbers + attribution
        high_conf_text = "According to the SEC filing, revenue was $1.5 billion."
        result_high = extractor.extract(high_conf_text, agent_name="test")
        high_conf_facts = [f for f in result_high.facts if f.confidence_hint > 0.7]
        assert len(high_conf_facts) > 0

        # Low confidence: hedging language
        low_conf_text = "The company might have approximately 5000 employees."
        result_low = extractor.extract(low_conf_text, agent_name="test")
        if result_low.facts:
            low_conf_facts = [f for f in result_low.facts if f.confidence_hint < 0.6]
            assert len(low_conf_facts) > 0

    def test_extract_from_agent_output(self):
        """Test extraction from structured agent output."""
        extractor = FactExtractor()
        agent_output = {
            "analysis": "TestCorp reported revenue of $100M in Q4 2023.",
            "financial_analysis": "The company has strong profitability with 30% margins.",
            "other_field": 12345  # Should be skipped
        }

        result = extractor.extract_from_agent_output(agent_output, "financial")

        assert result.total_facts > 0
        assert all(f.source_agent == "financial" for f in result.facts)

    def test_skip_short_sentences(self):
        """Test that very short sentences are skipped."""
        extractor = FactExtractor()
        text = "Yes. No. OK. The company reported revenue of $1 billion in 2023."

        result = extractor.extract(text, agent_name="test")

        # Should extract from the long sentence, not the short ones
        assert result.total_sentences >= 4
        assert result.total_facts < result.total_sentences  # Some sentences should be skipped

    def test_sentence_splitting(self):
        """Test sentence splitting preserves decimals and abbreviations."""
        extractor = FactExtractor()
        text = "Mr. Smith reported revenue of 1.5 billion. The company has Dr. Johnson as CTO."

        sentences = extractor._split_sentences(text)

        assert len(sentences) >= 2
        assert "1.5" in sentences[0]  # Decimal preserved
        assert "Mr. Smith" in sentences[0] or "Mr." in sentences[0]  # Abbreviation preserved

    def test_facts_by_category_property(self):
        """Test facts_by_category grouping."""
        extractor = FactExtractor()
        text = """
        The company reported revenue of $1B (financial fact).
        TAM is $50B with 15% CAGR (market fact).
        Founded in 2010 in SF (company fact).
        """

        result = extractor.extract(text, agent_name="test")
        categorized = result.facts_by_category

        assert isinstance(categorized, dict)
        assert len(categorized) > 0


@pytest.mark.unit
@pytest.mark.quality
class TestFactExtractionHelpers:
    """Test helper functions for fact extraction."""

    def test_extract_facts_convenience_function(self):
        """Test the extract_facts convenience function."""
        text = "The company has 5,000 employees and $500M revenue."
        facts = extract_facts(text, "test_agent")

        assert isinstance(facts, list)
        assert len(facts) > 0
        assert all(isinstance(f, ExtractedFact) for f in facts)
        assert all(f.source_agent == "test_agent" for f in facts)

    def test_extract_from_all_agents(self, sample_agent_outputs):
        """Test extraction from multiple agent outputs."""
        results = extract_from_all_agents(sample_agent_outputs)

        assert isinstance(results, dict)
        assert "researcher" in results
        assert "financial" in results
        assert "market" in results

        # Each should have extraction results
        for agent_name, result in results.items():
            assert result.total_facts >= 0
            if result.facts:
                assert all(f.source_agent == agent_name for f in result.facts)


@pytest.mark.unit
@pytest.mark.quality
class TestExtractedFact:
    """Test ExtractedFact model."""

    def test_create_extracted_fact(self):
        """Test creating an ExtractedFact instance."""
        fact = ExtractedFact(
            content="Test fact content",
            category=FactCategory.FINANCIAL,
            claim_type=ClaimType.NUMERICAL,
            source_agent="test",
            confidence_hint=0.85
        )

        assert fact.content == "Test fact content"
        assert fact.category == FactCategory.FINANCIAL
        assert fact.claim_type == ClaimType.NUMERICAL
        assert fact.source_agent == "test"
        assert fact.confidence_hint == 0.85
        assert fact.needs_verification is True  # Default

    def test_fact_defaults(self):
        """Test ExtractedFact default values."""
        fact = ExtractedFact(content="Minimal fact")

        assert fact.category == FactCategory.UNKNOWN
        assert fact.claim_type == ClaimType.ATTRIBUTIVE
        assert fact.source_agent == "unknown"
        assert 0 <= fact.confidence_hint <= 1
        assert fact.needs_verification is True

    def test_to_research_fact_conversion(self):
        """Test conversion to ResearchFact model."""
        from company_researcher.quality.models import Source, SourceQuality

        fact = ExtractedFact(
            content="Test content",
            category=FactCategory.FINANCIAL,
            source_agent="financial",
            confidence_hint=0.9
        )

        source = Source(
            url="https://example.com",
            title="Test Source",
            quality=SourceQuality.HIGH
        )

        research_fact = fact.to_research_fact(source)

        assert research_fact.content == "Test content"
        assert research_fact.source == source
        assert research_fact.extracted_by == "financial"
        # High confidence (>0.7) should map to HIGH confidence level
        from company_researcher.quality.models import ConfidenceLevel
        assert research_fact.confidence == ConfidenceLevel.HIGH
