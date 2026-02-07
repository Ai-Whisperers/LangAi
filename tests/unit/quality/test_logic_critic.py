"""
Unit Tests for Logic Critic Agent (Phase 10).

Tests comprehensive quality assessment including fact extraction,
contradiction detection, gap identification, and quality scoring.
"""

from unittest.mock import MagicMock, patch

import pytest

from company_researcher.agents.quality.logic_critic import (
    REQUIRED_SECTIONS,
    ResearchGap,
    calculate_comprehensive_quality,
    extract_recommendations,
    identify_gaps,
    logic_critic_agent_node,
    quick_logic_critic_node,
)

# Use the AI extraction ExtractedFact which is what logic_critic.py uses
from company_researcher.ai.extraction import ExtractedFact, FactCategory, FactType
from company_researcher.quality.contradiction_detector import (
    ContradictionReport,
    ContradictionSeverity,
)


@pytest.mark.unit
@pytest.mark.quality
class TestResearchGap:
    """Test ResearchGap model."""

    def test_create_research_gap(self):
        """Test creating a ResearchGap instance."""
        gap = ResearchGap(
            section="Financial Analysis",
            field="revenue",
            severity="high",
            recommendation="Add revenue information",
        )

        assert gap.section == "Financial Analysis"
        assert gap.field == "revenue"
        assert gap.severity == "high"
        assert gap.recommendation == "Add revenue information"

    def test_gap_to_dict(self):
        """Test converting gap to dictionary."""
        gap = ResearchGap(
            section="Market Analysis",
            field="market_size",
            severity="medium",
            recommendation="Include TAM/SAM/SOM data",
        )

        gap_dict = gap.to_dict()

        assert isinstance(gap_dict, dict)
        assert gap_dict["section"] == "Market Analysis"
        assert gap_dict["field"] == "market_size"
        assert gap_dict["severity"] == "medium"


@pytest.mark.unit
@pytest.mark.quality
class TestIdentifyGaps:
    """Test gap identification functionality."""

    def test_identify_gaps_with_sufficient_coverage(self):
        """Test gap identification when coverage is good."""
        facts = []

        # Create sufficient facts for each section
        # Map section_id to FactCategory values
        category_map = {
            "company_overview": FactCategory.COMPANY_INFO,
            "financial": FactCategory.FINANCIAL,
            "market": FactCategory.MARKET,
            "product": FactCategory.PRODUCT,
            "competitive": FactCategory.MARKET,
            "leadership": FactCategory.LEADERSHIP,
        }
        for section_id, section_info in REQUIRED_SECTIONS.items():
            category = category_map.get(section_id, FactCategory.NEWS)
            for i in range(5):  # 5 facts per section (above minimum of 3)
                fact = ExtractedFact(
                    category=category,
                    fact_type=FactType.OTHER,
                    value=f"Fact about {section_id} - {i}",
                    source_text=f"Source text for {section_id} fact {i}",
                    confidence=0.8,
                )
                facts.append(fact)

        gaps = identify_gaps(facts, {})

        # Should have minimal gaps with good coverage
        assert isinstance(gaps, list)
        # Some gaps might still exist for specific fields not mentioned

    def test_identify_gaps_with_insufficient_facts(self):
        """Test gap identification when section has too few facts."""
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.REVENUE,
                value="$1B",
                source_text="Company revenue is $1B",
                confidence=0.8,
            )
            # Only 1 fact (< minimum of 3)
        ]

        gaps = identify_gaps(facts, {})

        # Should identify gaps for sections with insufficient facts
        high_severity_gaps = [g for g in gaps if g.severity == "high"]
        assert len(high_severity_gaps) > 0

    def test_identify_gaps_for_missing_fields(self):
        """Test gap identification for specific missing fields."""
        # Create facts that don't mention specific required fields
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.OTHER,
                value="The company is doing well",
                source_text="The company is doing well",
                confidence=0.7,
            ),
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.OTHER,
                value="The market is growing",
                source_text="The market is growing",
                confidence=0.7,
            ),
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.OTHER,
                value="Good performance overall",
                source_text="Good performance overall",
                confidence=0.7,
            ),
        ]

        gaps = identify_gaps(facts, {})

        # Should identify missing fields
        assert len(gaps) > 0
        field_gaps = [g for g in gaps if g.field != "general"]
        assert len(field_gaps) > 0


@pytest.mark.unit
@pytest.mark.quality
class TestCalculateComprehensiveQuality:
    """Test comprehensive quality scoring."""

    def test_calculate_quality_with_good_research(self):
        """Test quality calculation with high-quality research."""
        # Create 50+ facts (high fact score)
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.OTHER,
                value=f"High quality fact {i}",
                source_text=f"Source text for high quality fact {i}",
                confidence=0.9,
            )
            for i in range(50)
        ]

        # No contradictions
        contradiction_report = ContradictionReport(contradictions=[], total_facts_analyzed=50)

        # No gaps
        gaps = []

        quality = calculate_comprehensive_quality(facts, contradiction_report, gaps)

        assert quality["overall_score"] >= 85
        assert quality["fact_score"] == 100
        assert quality["contradiction_score"] == 100
        assert quality["gap_score"] == 100
        assert quality["passed"] is True

    def test_calculate_quality_with_contradictions(self):
        """Test quality calculation with contradictions."""
        from company_researcher.quality.contradiction_detector import Contradiction

        facts = [
            ExtractedFact(
                category=FactCategory.COMPANY_INFO,
                fact_type=FactType.OTHER,
                value=f"Fact {i}",
                source_text=f"Source text for fact {i}",
                confidence=0.8,
            )
            for i in range(30)
        ]

        # Create critical contradiction
        contradiction = Contradiction(
            id="C1",
            topic="revenue",
            severity=ContradictionSeverity.CRITICAL,
            fact_a="Revenue is $1B",
            fact_b="Revenue is $3B",
            agent_a="a1",
            agent_b="a2",
            explanation="Critical disagreement",
        )

        contradiction_report = ContradictionReport(
            contradictions=[contradiction], total_facts_analyzed=30
        )

        gaps = []

        quality = calculate_comprehensive_quality(facts, contradiction_report, gaps)

        # Critical contradictions should significantly lower score
        assert quality["contradiction_score"] < 100
        assert quality["critical_contradictions"] == 1
        assert quality["overall_score"] < 90

    def test_calculate_quality_with_gaps(self):
        """Test quality calculation with research gaps."""
        facts = [
            ExtractedFact(
                category=FactCategory.COMPANY_INFO,
                fact_type=FactType.OTHER,
                value=f"Fact {i}",
                source_text=f"Source text for fact {i}",
                confidence=0.8,
            )
            for i in range(30)
        ]

        contradiction_report = ContradictionReport(contradictions=[], total_facts_analyzed=30)

        # Create high-severity gaps
        gaps = [
            ResearchGap("Financial", "revenue", "high", "Add revenue"),
            ResearchGap("Market", "market_size", "high", "Add TAM"),
            ResearchGap("Product", "products", "high", "Add products"),
            ResearchGap("Leadership", "ceo", "high", "Add CEO"),
        ]

        quality = calculate_comprehensive_quality(facts, contradiction_report, gaps)

        # High-severity gaps should lower score
        assert quality["gap_score"] < 100
        assert quality["high_gaps"] == 4
        assert quality["overall_score"] < 85

    def test_calculate_quality_with_low_confidence(self):
        """Test quality calculation with low-confidence facts."""
        # Create facts with low confidence
        facts = [
            ExtractedFact(
                category=FactCategory.COMPANY_INFO,
                fact_type=FactType.OTHER,
                value=f"Uncertain fact {i}",
                source_text=f"Source text for uncertain fact {i}",
                confidence=0.3,  # Low confidence
            )
            for i in range(30)
        ]

        contradiction_report = ContradictionReport(contradictions=[], total_facts_analyzed=30)
        gaps = []

        quality = calculate_comprehensive_quality(facts, contradiction_report, gaps)

        # Low confidence should lower confidence score
        assert quality["confidence_score"] < 50
        assert quality["overall_score"] < 85


@pytest.mark.unit
@pytest.mark.quality
class TestExtractRecommendations:
    """Test recommendation extraction from analysis."""

    def test_extract_recommendations_from_text(self):
        """Test extracting recommendations from analysis text."""
        analysis = """
        ## Analysis Summary
        The research is comprehensive but has some gaps.

        ## Recommendations
        1. Add more financial details about revenue and profitability
        2. Include product roadmap information
        3. Gather competitive intelligence data
        - Verify contradictory revenue figures
        - Add TAM/SAM/SOM market analysis
        """

        recommendations = extract_recommendations(analysis)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 5  # Max 5 recommendations
        assert any("financial" in rec.lower() for rec in recommendations)

    def test_extract_no_recommendations(self):
        """Test when no recommendation section exists."""
        analysis = "This is just analysis without any recommendations section."

        recommendations = extract_recommendations(analysis)

        # Should return empty list or minimal recommendations
        assert isinstance(recommendations, list)


@pytest.mark.unit
@pytest.mark.quality
class TestQuickLogicCriticNode:
    """Test quick logic critic (no LLM)."""

    def test_quick_logic_critic_node(self, sample_agent_outputs):
        """Test quick logic critic without LLM."""
        state = {"company_name": "TestCorp", "agent_outputs": sample_agent_outputs}

        result = quick_logic_critic_node(state)

        assert "agent_outputs" in result
        assert "logic_critic" in result["agent_outputs"]
        assert "quality_score" in result

        logic_critic_output = result["agent_outputs"]["logic_critic"]
        assert "quality_metrics" in logic_critic_output
        assert "facts_analyzed" in logic_critic_output
        assert logic_critic_output["cost"] == 0.0  # No LLM = no cost

    def test_quick_logic_critic_quality_metrics(self, sample_agent_outputs):
        """Test quality metrics from quick logic critic."""
        state = {"company_name": "TestCorp", "agent_outputs": sample_agent_outputs}

        result = quick_logic_critic_node(state)
        metrics = result["agent_outputs"]["logic_critic"]["quality_metrics"]

        assert "overall_score" in metrics
        assert "fact_score" in metrics
        assert "contradiction_score" in metrics
        assert "gap_score" in metrics
        assert "passed" in metrics
        assert isinstance(metrics["passed"], bool)


@pytest.mark.unit
@pytest.mark.quality
@patch("company_researcher.agents.quality.logic_critic.get_anthropic_client")
class TestLogicCriticAgent:
    """Test full logic critic agent (with mocked LLM)."""

    def test_logic_critic_node_basic_execution(self, mock_get_client, sample_agent_outputs):
        """Test basic execution of logic critic node."""
        # Mock the LLM response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Analysis complete. Research quality is good.")]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        state = {"company_name": "TestCorp", "agent_outputs": sample_agent_outputs}

        result = logic_critic_agent_node(state)

        assert "agent_outputs" in result
        assert "logic_critic" in result["agent_outputs"]
        assert "quality_score" in result
        assert "total_cost" in result

    def test_logic_critic_node_output_structure(self, mock_get_client, sample_agent_outputs):
        """Test output structure of logic critic."""
        # Mock LLM
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Quality assessment complete.")]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        state = {"company_name": "TestCorp", "agent_outputs": sample_agent_outputs}

        result = logic_critic_agent_node(state)
        output = result["agent_outputs"]["logic_critic"]

        # Check all required fields
        assert "analysis" in output
        assert "quality_metrics" in output
        assert "facts_analyzed" in output
        assert "contradictions" in output
        assert "gaps" in output
        assert "recommendations" in output
        assert "passed" in output
        assert "cost" in output
        assert "duration_seconds" in output
        assert "tokens" in output

    def test_logic_critic_node_contradiction_details(self, mock_get_client):
        """Test contradiction details in output."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Found contradictions in revenue data.")]
        mock_response.usage.input_tokens = 1000
        mock_response.usage.output_tokens = 500
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Create agent outputs with contradictory information
        agent_outputs = {
            "financial": {"financial_analysis": "Revenue is $1.5 billion with strong margins."},
            "market": {"market_analysis": "Company revenue reached $2.1 billion last year."},
        }

        state = {"company_name": "TestCorp", "agent_outputs": agent_outputs}

        result = logic_critic_agent_node(state)
        contradictions = result["agent_outputs"]["logic_critic"]["contradictions"]

        assert "total" in contradictions
        assert "critical" in contradictions
        assert "high" in contradictions
        assert "details" in contradictions


@pytest.mark.unit
@pytest.mark.quality
class TestRequiredSections:
    """Test REQUIRED_SECTIONS configuration."""

    def test_required_sections_structure(self):
        """Test that REQUIRED_SECTIONS is properly configured."""
        assert isinstance(REQUIRED_SECTIONS, dict)
        assert len(REQUIRED_SECTIONS) > 0

        for section_id, section_info in REQUIRED_SECTIONS.items():
            assert "name" in section_info
            assert "fields" in section_info
            assert "weight" in section_info
            assert isinstance(section_info["fields"], list)
            assert isinstance(section_info["weight"], float)

    def test_required_sections_weights_sum(self):
        """Test that section weights sum to approximately 1.0."""
        total_weight = sum(info["weight"] for info in REQUIRED_SECTIONS.values())
        assert 0.99 <= total_weight <= 1.01  # Allow small floating point error
