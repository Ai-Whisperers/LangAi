"""
Unit Tests for Contradiction Detector (Phase 10).

Tests contradiction detection (rule-based and LLM), severity assessment,
and resolution strategies.
"""

import pytest
from company_researcher.quality.contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    ContradictionReport,
    ContradictionSeverity,
    ResolutionStrategy,
    extract_topics,
    detect_contradictions,
    quick_contradiction_check
)
from company_researcher.quality.fact_extractor import (
    ExtractedFact,
    FactCategory,
    ClaimType
)


@pytest.mark.unit
@pytest.mark.quality
class TestContradictionDetector:
    """Test suite for ContradictionDetector class."""

    def test_initialization(self):
        """Test ContradictionDetector initialization."""
        detector = ContradictionDetector(use_llm=False)
        assert detector is not None
        assert detector.use_llm is False

        detector_llm = ContradictionDetector(use_llm=True)
        assert detector_llm.use_llm is True

    def test_detect_numerical_contradictions(self, sample_contradictory_facts):
        """Test detection of numerical contradictions."""
        detector = ContradictionDetector(use_llm=False)
        report = detector.detect(sample_contradictory_facts)

        # Should detect the contradiction between $1.5B and $2.1B
        assert report.total_count > 0
        assert any(c.severity in [ContradictionSeverity.HIGH, ContradictionSeverity.CRITICAL]
                   for c in report.contradictions)

    def test_detect_no_contradictions(self, sample_extracted_facts):
        """Test detection when no contradictions exist."""
        detector = ContradictionDetector(use_llm=False)
        report = detector.detect(sample_extracted_facts)

        # These facts don't contradict each other
        assert report.total_count == 0
        assert len(report.contradictions) == 0

    def test_extract_numbers(self):
        """Test number extraction from text."""
        detector = ContradictionDetector()

        # Test currency
        numbers = detector._extract_numbers("Revenue was $1.5B in 2023")
        assert len(numbers) > 0
        assert any(val == 1_500_000_000 for val, _ in numbers)

        # Test percentages
        numbers = detector._extract_numbers("Profit margin is 25.5%")
        assert len(numbers) > 0
        assert any(val == 25.5 for val, _ in numbers)

        # Test plain numbers
        numbers = detector._extract_numbers("5,000 employees")
        assert len(numbers) > 0

    def test_facts_are_comparable(self):
        """Test fact comparability check."""
        detector = ContradictionDetector()

        # Similar facts (about revenue)
        fact_a = "Company revenue was $1.5 billion"
        fact_b = "The company reported revenue of $2 billion"
        assert detector._facts_are_comparable(fact_a, fact_b) is True

        # Unrelated facts
        fact_c = "Company has 5000 employees"
        fact_d = "CEO is John Smith"
        assert detector._facts_are_comparable(fact_c, fact_d) is False

    def test_assess_numerical_severity(self):
        """Test severity assessment based on difference percentage."""
        detector = ContradictionDetector()

        # >50% difference = CRITICAL
        assert detector._assess_numerical_severity(60.0) == ContradictionSeverity.CRITICAL

        # 30-50% = HIGH
        assert detector._assess_numerical_severity(40.0) == ContradictionSeverity.HIGH

        # 20-30% = MEDIUM
        assert detector._assess_numerical_severity(25.0) == ContradictionSeverity.MEDIUM

        # <20% = LOW
        assert detector._assess_numerical_severity(10.0) == ContradictionSeverity.LOW

    def test_suggest_numerical_resolution(self):
        """Test resolution strategy suggestion."""
        detector = ContradictionDetector()

        # Fact with official source
        fact_official = ExtractedFact(
            content="According to SEC filing, revenue was $1.5B",
            category=FactCategory.FINANCIAL,
            source_agent="financial"
        )

        fact_unofficial = ExtractedFact(
            content="Revenue is estimated at $2B",
            category=FactCategory.FINANCIAL,
            source_agent="market"
        )

        strategy = detector._suggest_numerical_resolution(fact_official, fact_unofficial)
        assert strategy == ResolutionStrategy.USE_OFFICIAL

    def test_detect_from_agent_outputs(self, sample_agent_outputs):
        """Test detection from agent output dictionary."""
        detector = ContradictionDetector(use_llm=False)
        report = detector.detect_from_agent_outputs(sample_agent_outputs)

        assert isinstance(report, ContradictionReport)
        assert report.total_facts_analyzed > 0

    @pytest.mark.slow
    @pytest.mark.requires_llm
    def test_detect_semantic_contradictions_with_llm(self):
        """Test LLM-based semantic contradiction detection."""
        # Only run if API key is available
        import os
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        detector = ContradictionDetector(use_llm=True)

        facts = [
            ExtractedFact(
                content="The company is profitable with strong margins.",
                category=FactCategory.FINANCIAL,
                source_agent="financial"
            ),
            ExtractedFact(
                content="The company is losing money and burning cash.",
                category=FactCategory.FINANCIAL,
                source_agent="market"
            )
        ]

        report = detector.detect(facts)

        # Should detect semantic contradiction
        assert report.total_count > 0


@pytest.mark.unit
@pytest.mark.quality
class TestContradictionReport:
    """Test ContradictionReport model."""

    def test_create_report(self):
        """Test creating a ContradictionReport."""
        contradictions = [
            Contradiction(
                id="TEST-1",
                topic="revenue",
                severity=ContradictionSeverity.HIGH,
                fact_a="Revenue is $1.5B",
                fact_b="Revenue is $2.1B",
                explanation="Numerical disagreement",
                agent_a="financial",
                agent_b="market"
            )
        ]

        report = ContradictionReport(
            contradictions=contradictions,
            total_facts_analyzed=10,
            topics_analyzed=3
        )

        assert report.total_count == 1
        assert report.critical_count == 0
        assert report.high_count == 1
        assert report.has_critical is False

    def test_get_by_severity(self):
        """Test filtering contradictions by severity."""
        contradictions = [
            Contradiction(
                id="C1",
                topic="revenue",
                severity=ContradictionSeverity.CRITICAL,
                fact_a="A",
                fact_b="B",
                explanation="Critical issue",
                agent_a="a1",
                agent_b="a2"
            ),
            Contradiction(
                id="C2",
                topic="employees",
                severity=ContradictionSeverity.LOW,
                fact_a="C",
                fact_b="D",
                explanation="Minor issue",
                agent_a="a1",
                agent_b="a2"
            )
        ]

        report = ContradictionReport(contradictions=contradictions)

        critical = report.get_by_severity(ContradictionSeverity.CRITICAL)
        assert len(critical) == 1
        assert critical[0].id == "C1"

        low = report.get_by_severity(ContradictionSeverity.LOW)
        assert len(low) == 1
        assert low[0].id == "C2"

    def test_to_markdown_no_contradictions(self):
        """Test markdown formatting with no contradictions."""
        report = ContradictionReport(
            total_facts_analyzed=50,
            topics_analyzed=10
        )

        markdown = report.to_markdown()

        assert "No contradictions detected" in markdown
        assert "50" in markdown  # Total facts
        assert "10" in markdown  # Topics

    def test_to_markdown_with_contradictions(self):
        """Test markdown formatting with contradictions."""
        contradictions = [
            Contradiction(
                id="TEST-1",
                topic="revenue",
                severity=ContradictionSeverity.HIGH,
                fact_a="Revenue is $1.5B",
                fact_b="Revenue is $2.1B",
                explanation="Significant numerical disagreement",
                agent_a="financial",
                agent_b="market"
            )
        ]

        report = ContradictionReport(contradictions=contradictions)
        markdown = report.to_markdown()

        assert "Contradiction Analysis" in markdown
        assert "TEST-1" in markdown
        assert "revenue" in markdown
        assert "Revenue is $1.5B" in markdown


@pytest.mark.unit
@pytest.mark.quality
class TestContradiction:
    """Test Contradiction model."""

    def test_create_contradiction(self):
        """Test creating a Contradiction instance."""
        contradiction = Contradiction(
            id="C1",
            topic="revenue",
            severity=ContradictionSeverity.HIGH,
            fact_a="Fact A",
            fact_b="Fact B",
            agent_a="agent1",
            agent_b="agent2",
            explanation="They disagree",
            resolution_strategy=ResolutionStrategy.INVESTIGATE
        )

        assert contradiction.id == "C1"
        assert contradiction.severity == ContradictionSeverity.HIGH
        assert contradiction.resolution_strategy == ResolutionStrategy.INVESTIGATE

    def test_contradiction_to_markdown(self):
        """Test markdown formatting of contradiction."""
        contradiction = Contradiction(
            id="TEST-1",
            topic="revenue",
            severity=ContradictionSeverity.CRITICAL,
            fact_a="Revenue is $1B",
            fact_b="Revenue is $3B",
            agent_a="financial",
            agent_b="market",
            explanation="Major disagreement on revenue",
            resolution_strategy=ResolutionStrategy.USE_OFFICIAL,
            resolution_suggestion="Use SEC filing data"
        )

        markdown = contradiction.to_markdown()

        assert "🔴" in markdown  # Critical icon
        assert "TEST-1" in markdown
        assert "revenue" in markdown
        assert "Revenue is $1B" in markdown
        assert "Revenue is $3B" in markdown
        assert "Major disagreement" in markdown
        assert "use_official" in markdown


@pytest.mark.unit
@pytest.mark.quality
class TestTopicExtraction:
    """Test topic extraction functionality."""

    def test_extract_topics(self):
        """Test grouping facts by topic."""
        facts = [
            ExtractedFact(
                content="Revenue was $1.5 billion in 2023",
                category=FactCategory.FINANCIAL,
                source_agent="financial"
            ),
            ExtractedFact(
                content="The company has strong profit margins",
                category=FactCategory.FINANCIAL,
                source_agent="financial"
            ),
            ExtractedFact(
                content="Founded in 2010",
                category=FactCategory.COMPANY,
                source_agent="researcher"
            )
        ]

        topics = extract_topics(facts)

        assert isinstance(topics, dict)
        assert "revenue" in topics
        assert "profit" in topics

    def test_extract_topics_uses_category_fallback(self):
        """Test that category is used as fallback topic."""
        facts = [
            ExtractedFact(
                content="Some random company information",
                category=FactCategory.COMPANY,
                source_agent="researcher"
            )
        ]

        topics = extract_topics(facts)

        # Should use category as topic
        assert FactCategory.COMPANY.value in topics


@pytest.mark.unit
@pytest.mark.quality
class TestHelperFunctions:
    """Test convenience helper functions."""

    def test_detect_contradictions_function(self, sample_contradictory_facts):
        """Test the detect_contradictions convenience function."""
        report = detect_contradictions(sample_contradictory_facts, use_llm=False)

        assert isinstance(report, ContradictionReport)
        assert report.total_count >= 0

    def test_quick_contradiction_check(self, sample_agent_outputs):
        """Test the quick_contradiction_check function."""
        total, critical = quick_contradiction_check(sample_agent_outputs)

        assert isinstance(total, int)
        assert isinstance(critical, int)
        assert critical <= total
