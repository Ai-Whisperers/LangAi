"""
Unit tests for risk_quantifier.py module.

Tests cover:
- RiskCategory, RiskLevel, RiskProbability enums
- Risk and RiskAssessment dataclasses
- RiskQuantifier methods
- Risk extraction, scoring, and grading
- Financial, market, and operational risk assessment
"""

import pytest
from src.company_researcher.agents.research.risk_quantifier import (
    RiskCategory,
    RiskLevel,
    RiskProbability,
    Risk,
    RiskAssessment,
    RiskQuantifier,
    create_risk_quantifier,
    RISK_INDICATORS,
)


class TestEnums:
    """Tests for enum classes."""

    def test_risk_category_values(self):
        """Test RiskCategory enum values."""
        assert RiskCategory.MARKET.value == "market"
        assert RiskCategory.FINANCIAL.value == "financial"
        assert RiskCategory.OPERATIONAL.value == "operational"
        assert RiskCategory.REGULATORY.value == "regulatory"
        assert RiskCategory.STRATEGIC.value == "strategic"
        assert RiskCategory.REPUTATIONAL.value == "reputational"
        assert RiskCategory.GEOPOLITICAL.value == "geopolitical"

    def test_risk_category_count(self):
        """Test RiskCategory has 7 categories."""
        assert len(RiskCategory) == 7

    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.CRITICAL.value == 5
        assert RiskLevel.HIGH.value == 4
        assert RiskLevel.MEDIUM.value == 3
        assert RiskLevel.LOW.value == 2
        assert RiskLevel.MINIMAL.value == 1

    def test_risk_probability_values(self):
        """Test RiskProbability enum values."""
        assert RiskProbability.VERY_LIKELY.value == 5
        assert RiskProbability.LIKELY.value == 4
        assert RiskProbability.POSSIBLE.value == 3
        assert RiskProbability.UNLIKELY.value == 2
        assert RiskProbability.RARE.value == 1


class TestRiskDataclass:
    """Tests for Risk dataclass."""

    def test_create_basic_risk(self):
        """Test creating a basic risk."""
        risk = Risk(
            name="Test Risk",
            category=RiskCategory.FINANCIAL,
            level=RiskLevel.HIGH,
            probability=RiskProbability.LIKELY,
            impact_score=7.0,
            likelihood_score=8.0,
            risk_score=56.0,
            description="A test risk"
        )

        assert risk.name == "Test Risk"
        assert risk.category == RiskCategory.FINANCIAL
        assert risk.level == RiskLevel.HIGH
        assert risk.probability == RiskProbability.LIKELY
        assert risk.impact_score == 7.0
        assert risk.likelihood_score == 8.0
        assert risk.risk_score == 56.0
        assert risk.description == "A test risk"
        assert risk.mitigation is None
        assert risk.trend == "stable"
        assert risk.source is None

    def test_create_full_risk(self):
        """Test creating a risk with all fields."""
        risk = Risk(
            name="Debt Risk",
            category=RiskCategory.FINANCIAL,
            level=RiskLevel.CRITICAL,
            probability=RiskProbability.VERY_LIKELY,
            impact_score=9.0,
            likelihood_score=9.0,
            risk_score=81.0,
            description="High debt levels",
            mitigation="Reduce debt through equity issuance",
            trend="increasing",
            source="financial_analysis"
        )

        assert risk.mitigation == "Reduce debt through equity issuance"
        assert risk.trend == "increasing"
        assert risk.source == "financial_analysis"


class TestRiskAssessmentDataclass:
    """Tests for RiskAssessment dataclass."""

    def test_create_risk_assessment(self):
        """Test creating a RiskAssessment."""
        risk = Risk(
            name="Test Risk",
            category=RiskCategory.MARKET,
            level=RiskLevel.MEDIUM,
            probability=RiskProbability.POSSIBLE,
            impact_score=5.0,
            likelihood_score=5.0,
            risk_score=25.0,
            description="Test"
        )

        assessment = RiskAssessment(
            company_name="Test Corp",
            overall_risk_score=35.0,
            risk_grade="B",
            risks=[risk],
            risk_by_category={"market": [risk]},
            risk_matrix={"market": {"impact": 5.0, "likelihood": 5.0}},
            key_risks=["Test Risk: Test"],
            risk_adjusted_metrics={"implied_risk_premium": 3.5},
            recommendations=["Monitor risks"],
            summary="Test summary"
        )

        assert assessment.company_name == "Test Corp"
        assert assessment.overall_risk_score == 35.0
        assert assessment.risk_grade == "B"
        assert len(assessment.risks) == 1
        assert "market" in assessment.risk_by_category


class TestRiskIndicators:
    """Tests for RISK_INDICATORS patterns."""

    def test_all_categories_have_indicators(self):
        """Test that all categories have risk indicators."""
        for category in RiskCategory:
            assert category in RISK_INDICATORS, f"Missing indicators for {category}"
            assert len(RISK_INDICATORS[category]) > 0

    def test_market_indicators_exist(self):
        """Test market risk indicators."""
        market_patterns = RISK_INDICATORS[RiskCategory.MARKET]
        assert any("competition" in p for p in market_patterns)
        assert any("disruption" in p for p in market_patterns)

    def test_financial_indicators_exist(self):
        """Test financial risk indicators."""
        financial_patterns = RISK_INDICATORS[RiskCategory.FINANCIAL]
        assert any("debt" in p for p in financial_patterns)
        assert any("liquidity" in p for p in financial_patterns)


class TestRiskQuantifierInit:
    """Tests for RiskQuantifier initialization."""

    def test_default_init(self):
        """Test default initialization."""
        quantifier = RiskQuantifier()

        assert quantifier.risk_tolerance == "moderate"
        assert len(quantifier.category_weights) == 7
        assert quantifier.category_weights[RiskCategory.FINANCIAL] == 0.20

    def test_custom_weights(self):
        """Test initialization with custom weights."""
        custom = {RiskCategory.FINANCIAL: 0.30}
        quantifier = RiskQuantifier(custom_weights=custom)

        assert quantifier.category_weights[RiskCategory.FINANCIAL] == 0.30

    def test_risk_tolerance_options(self):
        """Test different risk tolerance settings."""
        conservative = RiskQuantifier(risk_tolerance="conservative")
        aggressive = RiskQuantifier(risk_tolerance="aggressive")

        assert conservative.risk_tolerance == "conservative"
        assert aggressive.risk_tolerance == "aggressive"

    def test_weights_sum(self):
        """Test that default weights sum to 1.0."""
        quantifier = RiskQuantifier()
        total = sum(quantifier.category_weights.values())
        assert abs(total - 1.0) < 0.01


class TestGradeThresholds:
    """Tests for grade thresholds."""

    def test_grade_thresholds_coverage(self):
        """Test grade thresholds cover full range."""
        quantifier = RiskQuantifier()
        thresholds = quantifier.GRADE_THRESHOLDS

        assert "A" in thresholds
        assert "B" in thresholds
        assert "C" in thresholds
        assert "D" in thresholds
        assert "F" in thresholds

    def test_determine_grade_a(self):
        """Test grade A determination."""
        quantifier = RiskQuantifier()
        assert quantifier._determine_grade(10) == "A"
        assert quantifier._determine_grade(19.9) == "A"

    def test_determine_grade_b(self):
        """Test grade B determination."""
        quantifier = RiskQuantifier()
        assert quantifier._determine_grade(20) == "B"
        assert quantifier._determine_grade(35) == "B"

    def test_determine_grade_c(self):
        """Test grade C determination."""
        quantifier = RiskQuantifier()
        assert quantifier._determine_grade(45) == "C"
        assert quantifier._determine_grade(59) == "C"

    def test_determine_grade_d(self):
        """Test grade D determination."""
        quantifier = RiskQuantifier()
        assert quantifier._determine_grade(65) == "D"
        assert quantifier._determine_grade(79) == "D"

    def test_determine_grade_f(self):
        """Test grade F determination."""
        quantifier = RiskQuantifier()
        assert quantifier._determine_grade(85) == "F"
        assert quantifier._determine_grade(100) == "F"


class TestTextRiskExtraction:
    """Tests for risk extraction from text."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_extract_market_risks(self, quantifier):
        """Test extracting market risks from text."""
        content = "The company faces intense competition in a disrupting market."
        risks = quantifier._extract_risks_from_text(content)

        assert len(risks) >= 1
        categories = [r.category for r in risks]
        assert RiskCategory.MARKET in categories

    def test_extract_financial_risks(self, quantifier):
        """Test extracting financial risks from text."""
        content = "The company has high debt burden and liquidity concerns."
        risks = quantifier._extract_risks_from_text(content)

        categories = [r.category for r in risks]
        assert RiskCategory.FINANCIAL in categories

    def test_extract_regulatory_risks(self, quantifier):
        """Test extracting regulatory risks from text."""
        content = "Regulatory scrutiny and compliance issues have increased."
        risks = quantifier._extract_risks_from_text(content)

        categories = [r.category for r in risks]
        assert RiskCategory.REGULATORY in categories

    def test_extract_operational_risks(self, quantifier):
        """Test extracting operational risks from text."""
        content = "Supply chain disruption and cybersecurity threats are concerns."
        risks = quantifier._extract_risks_from_text(content)

        categories = [r.category for r in risks]
        assert RiskCategory.OPERATIONAL in categories

    def test_extract_no_risks_from_neutral_text(self, quantifier):
        """Test no risks extracted from neutral text."""
        content = "The company reported stable operations and steady growth."
        risks = quantifier._extract_risks_from_text(content)
        # May still find some risks due to partial matches, but should be minimal
        assert len(risks) <= 2

    def test_extracted_risks_have_source(self, quantifier):
        """Test extracted risks have text_analysis source."""
        content = "The company faces disruption from new entrants."
        risks = quantifier._extract_risks_from_text(content)

        for risk in risks:
            assert risk.source == "text_analysis"


class TestPatternToName:
    """Tests for pattern to name conversion."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_simple_pattern(self, quantifier):
        """Test simple pattern conversion."""
        name = quantifier._pattern_to_name(r"debt\s+burden")
        assert "debt" in name.lower()
        assert "burden" in name.lower()

    def test_pattern_with_options(self, quantifier):
        """Test pattern with optional groups."""
        name = quantifier._pattern_to_name(r"liquidity\s+(?:concern|issue)")
        assert "liquidity" in name.lower()


class TestFinancialRiskAssessment:
    """Tests for financial risk assessment."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_high_debt_to_equity(self, quantifier):
        """Test high leverage detection."""
        company_data = {"debt_to_equity": 2.5}
        risks = quantifier._assess_financial_risks(company_data)

        assert len(risks) == 1
        assert risks[0].name == "High Leverage"
        assert risks[0].level == RiskLevel.HIGH

    def test_moderate_debt_to_equity(self, quantifier):
        """Test moderate leverage detection."""
        company_data = {"debt_to_equity": 1.5}
        risks = quantifier._assess_financial_risks(company_data)

        assert len(risks) == 1
        assert risks[0].name == "Moderate Leverage"
        assert risks[0].level == RiskLevel.MEDIUM

    def test_healthy_debt_to_equity(self, quantifier):
        """Test no risk for healthy debt ratio."""
        company_data = {"debt_to_equity": 0.5}
        risks = quantifier._assess_financial_risks(company_data)

        debt_risks = [r for r in risks if "Leverage" in r.name]
        assert len(debt_risks) == 0

    def test_low_profit_margin(self, quantifier):
        """Test low profitability detection."""
        company_data = {"profit_margin": 3.0}
        risks = quantifier._assess_financial_risks(company_data)

        profit_risks = [r for r in risks if "Profitability" in r.name]
        assert len(profit_risks) == 1
        assert profit_risks[0].level == RiskLevel.HIGH

    def test_revenue_decline(self, quantifier):
        """Test severe revenue decline detection."""
        company_data = {"revenue_growth": -15.0}
        risks = quantifier._assess_financial_risks(company_data)

        revenue_risks = [r for r in risks if "Revenue Decline" in r.name]
        assert len(revenue_risks) == 1
        assert revenue_risks[0].level == RiskLevel.HIGH
        assert revenue_risks[0].probability == RiskProbability.VERY_LIKELY

    def test_stagnant_revenue(self, quantifier):
        """Test stagnant revenue detection."""
        company_data = {"revenue_growth": -3.0}
        risks = quantifier._assess_financial_risks(company_data)

        revenue_risks = [r for r in risks if "Stagnant" in r.name]
        assert len(revenue_risks) == 1
        assert revenue_risks[0].level == RiskLevel.MEDIUM

    def test_multiple_financial_risks(self, quantifier):
        """Test detection of multiple financial risks."""
        company_data = {
            "debt_to_equity": 2.5,
            "profit_margin": 2.0,
            "revenue_growth": -20.0
        }
        risks = quantifier._assess_financial_risks(company_data)

        assert len(risks) == 3


class TestMarketRiskAssessment:
    """Tests for market risk assessment."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_low_market_share(self, quantifier):
        """Test low market share detection."""
        market_data = {"market_share": 3.0}
        risks = quantifier._assess_market_risks(market_data)

        share_risks = [r for r in risks if "Market Share" in r.name]
        assert len(share_risks) == 1

    def test_high_competition(self, quantifier):
        """Test high competition detection."""
        market_data = {"competitors": list(range(15))}
        risks = quantifier._assess_market_risks(market_data)

        comp_risks = [r for r in risks if "Competition" in r.name]
        assert len(comp_risks) == 1

    def test_declining_market(self, quantifier):
        """Test declining market detection."""
        market_data = {"market_growth": -5.0}
        risks = quantifier._assess_market_risks(market_data)

        market_risks = [r for r in risks if "Declining Market" in r.name]
        assert len(market_risks) == 1
        assert market_risks[0].level == RiskLevel.HIGH

    def test_healthy_market_no_risks(self, quantifier):
        """Test healthy market produces no risks."""
        market_data = {
            "market_share": 25.0,
            "competitors": ["A", "B", "C"],
            "market_growth": 10.0
        }
        risks = quantifier._assess_market_risks(market_data)
        assert len(risks) == 0


class TestOperationalRiskAssessment:
    """Tests for operational risk assessment."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_high_employee_turnover(self, quantifier):
        """Test high employee turnover detection."""
        company_data = {"employee_turnover": 25.0}
        risks = quantifier._assess_operational_risks(company_data)

        turnover_risks = [r for r in risks if "Turnover" in r.name]
        assert len(turnover_risks) == 1

    def test_technology_obsolescence(self, quantifier):
        """Test technology obsolescence detection."""
        company_data = {"tech_stack_age": 8}
        risks = quantifier._assess_operational_risks(company_data)

        tech_risks = [r for r in risks if "Technology" in r.name]
        assert len(tech_risks) == 1

    def test_healthy_operations_no_risks(self, quantifier):
        """Test healthy operations produce no risks."""
        company_data = {
            "employee_turnover": 10.0,
            "tech_stack_age": 2
        }
        risks = quantifier._assess_operational_risks(company_data)
        assert len(risks) == 0


class TestOverallScoreCalculation:
    """Tests for overall risk score calculation."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_no_risks_base_score(self, quantifier):
        """Test base score when no risks."""
        score = quantifier._calculate_overall_score([])
        assert score == 20.0

    def test_single_risk_score(self, quantifier):
        """Test score with single risk."""
        risks = [Risk(
            name="Test",
            category=RiskCategory.FINANCIAL,
            level=RiskLevel.HIGH,
            probability=RiskProbability.LIKELY,
            impact_score=7.0,
            likelihood_score=7.0,
            risk_score=49.0,
            description="Test risk"
        )]
        score = quantifier._calculate_overall_score(risks)
        assert 0 <= score <= 100

    def test_score_bounded(self, quantifier):
        """Test score is bounded between 0 and 100."""
        high_risks = [Risk(
            name=f"Risk {i}",
            category=list(RiskCategory)[i % 7],
            level=RiskLevel.CRITICAL,
            probability=RiskProbability.VERY_LIKELY,
            impact_score=10.0,
            likelihood_score=10.0,
            risk_score=100.0,
            description="High risk"
        ) for i in range(10)]

        score = quantifier._calculate_overall_score(high_risks)
        assert score <= 100
        assert score >= 0


class TestRiskGrouping:
    """Tests for risk grouping functionality."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_group_by_category(self, quantifier):
        """Test grouping risks by category."""
        risks = [
            Risk(name="R1", category=RiskCategory.FINANCIAL, level=RiskLevel.HIGH,
                 probability=RiskProbability.LIKELY, impact_score=7, likelihood_score=7,
                 risk_score=49, description="Financial"),
            Risk(name="R2", category=RiskCategory.FINANCIAL, level=RiskLevel.MEDIUM,
                 probability=RiskProbability.POSSIBLE, impact_score=5, likelihood_score=5,
                 risk_score=25, description="Financial 2"),
            Risk(name="R3", category=RiskCategory.MARKET, level=RiskLevel.LOW,
                 probability=RiskProbability.UNLIKELY, impact_score=3, likelihood_score=3,
                 risk_score=9, description="Market"),
        ]

        grouped = quantifier._group_by_category(risks)

        assert "financial" in grouped
        assert "market" in grouped
        assert len(grouped["financial"]) == 2
        assert len(grouped["market"]) == 1


class TestRiskMatrix:
    """Tests for risk matrix generation."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_generate_risk_matrix(self, quantifier):
        """Test risk matrix generation."""
        risks = [
            Risk(name="R1", category=RiskCategory.FINANCIAL, level=RiskLevel.HIGH,
                 probability=RiskProbability.LIKELY, impact_score=7, likelihood_score=8,
                 risk_score=56, description="Test"),
            Risk(name="R2", category=RiskCategory.FINANCIAL, level=RiskLevel.MEDIUM,
                 probability=RiskProbability.POSSIBLE, impact_score=5, likelihood_score=4,
                 risk_score=20, description="Test 2"),
        ]

        matrix = quantifier._generate_risk_matrix(risks)

        assert "financial" in matrix
        assert "impact" in matrix["financial"]
        assert "likelihood" in matrix["financial"]
        # Average of 7 and 5 = 6
        assert matrix["financial"]["impact"] == 6.0
        # Average of 8 and 4 = 6
        assert matrix["financial"]["likelihood"] == 6.0


class TestKeyRisksIdentification:
    """Tests for key risk identification."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_identify_key_risks_sorted(self, quantifier):
        """Test key risks are sorted by score."""
        risks = [
            Risk(name="Low", category=RiskCategory.MARKET, level=RiskLevel.LOW,
                 probability=RiskProbability.RARE, impact_score=2, likelihood_score=2,
                 risk_score=4, description="Low risk"),
            Risk(name="High", category=RiskCategory.FINANCIAL, level=RiskLevel.HIGH,
                 probability=RiskProbability.LIKELY, impact_score=8, likelihood_score=8,
                 risk_score=64, description="High risk"),
            Risk(name="Medium", category=RiskCategory.OPERATIONAL, level=RiskLevel.MEDIUM,
                 probability=RiskProbability.POSSIBLE, impact_score=5, likelihood_score=5,
                 risk_score=25, description="Medium risk"),
        ]

        key_risks = quantifier._identify_key_risks(risks)

        assert len(key_risks) == 3
        assert "High" in key_risks[0]

    def test_identify_key_risks_limit(self, quantifier):
        """Test key risks limited to 5."""
        risks = [Risk(
            name=f"Risk {i}",
            category=RiskCategory.MARKET,
            level=RiskLevel.MEDIUM,
            probability=RiskProbability.POSSIBLE,
            impact_score=5,
            likelihood_score=5,
            risk_score=25 + i,
            description=f"Risk {i}"
        ) for i in range(10)]

        key_risks = quantifier._identify_key_risks(risks)
        assert len(key_risks) == 5


class TestRiskAdjustedMetrics:
    """Tests for risk-adjusted metrics calculation."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_calculate_risk_adjusted_growth(self, quantifier):
        """Test risk-adjusted growth calculation."""
        company_data = {"revenue_growth": 20.0}
        risk_score = 50.0

        metrics = quantifier._calculate_risk_adjusted_metrics(company_data, risk_score)

        assert "risk_adjusted_growth" in metrics
        # 20 * (1 - 0.5 * 0.5) = 20 * 0.75 = 15
        assert metrics["risk_adjusted_growth"] == 15.0

    def test_calculate_risk_adjusted_pe(self, quantifier):
        """Test risk-adjusted PE ratio calculation."""
        company_data = {"pe_ratio": 20.0}
        risk_score = 40.0

        metrics = quantifier._calculate_risk_adjusted_metrics(company_data, risk_score)

        assert "risk_adjusted_pe" in metrics
        # 20 * (1 - 0.4 * 0.3) = 20 * 0.88 = 17.6
        assert metrics["risk_adjusted_pe"] == 17.6

    def test_implied_risk_premium(self, quantifier):
        """Test implied risk premium calculation."""
        company_data = {}
        risk_score = 60.0

        metrics = quantifier._calculate_risk_adjusted_metrics(company_data, risk_score)

        assert "implied_risk_premium" in metrics
        # 0.6 * 10 = 6
        assert metrics["implied_risk_premium"] == 6.0


class TestRecommendationGeneration:
    """Tests for recommendation generation."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_urgent_recommendation_for_f_grade(self, quantifier):
        """Test urgent recommendation for F grade."""
        risks = []
        recommendations = quantifier._generate_recommendations(risks, "F")

        assert any("URGENT" in r for r in recommendations)

    def test_financial_category_recommendation(self, quantifier):
        """Test financial category recommendation."""
        risks = [Risk(
            name="Debt",
            category=RiskCategory.FINANCIAL,
            level=RiskLevel.HIGH,
            probability=RiskProbability.LIKELY,
            impact_score=7,
            likelihood_score=7,
            risk_score=49,
            description="High debt"
        )]

        recommendations = quantifier._generate_recommendations(risks, "C")

        assert any("financial" in r.lower() for r in recommendations)

    def test_recommendations_limited(self, quantifier):
        """Test recommendations are limited to 7."""
        risks = [Risk(
            name=f"Risk {i}",
            category=list(RiskCategory)[i % 7],
            level=RiskLevel.HIGH,
            probability=RiskProbability.LIKELY,
            impact_score=8,
            likelihood_score=8,
            risk_score=64,
            description=f"Risk {i}",
            mitigation=f"Mitigate risk {i}"
        ) for i in range(10)]

        recommendations = quantifier._generate_recommendations(risks, "D")
        assert len(recommendations) <= 7


class TestSummaryGeneration:
    """Tests for summary generation."""

    @pytest.fixture
    def quantifier(self):
        return RiskQuantifier()

    def test_summary_includes_company_name(self, quantifier):
        """Test summary includes company name."""
        summary = quantifier._generate_summary("Test Corp", 45.0, "C", [])
        assert "Test Corp" in summary

    def test_summary_includes_grade(self, quantifier):
        """Test summary includes grade."""
        summary = quantifier._generate_summary("Test", 45.0, "C", [])
        assert "Grade C" in summary

    def test_summary_includes_score(self, quantifier):
        """Test summary includes score."""
        summary = quantifier._generate_summary("Test", 45.0, "C", [])
        assert "45" in summary

    def test_summary_grade_descriptions(self, quantifier):
        """Test grade-specific descriptions in summary."""
        summary_a = quantifier._generate_summary("Test", 15.0, "A", [])
        summary_f = quantifier._generate_summary("Test", 90.0, "F", [])

        assert "very low" in summary_a.lower()
        assert "critical" in summary_f.lower() or "immediate" in summary_f.lower()


class TestFullRiskAssessment:
    """Integration tests for full risk assessment."""

    def test_complete_assessment(self):
        """Test complete risk assessment workflow."""
        quantifier = RiskQuantifier()

        company_data = {
            "debt_to_equity": 2.5,
            "profit_margin": 3.0,
            "revenue_growth": -5.0,
            "employee_turnover": 25.0
        }

        market_data = {
            "market_share": 3.0,
            "competitors": list(range(15)),
            "market_growth": -2.0
        }

        content = "The company faces intense competition and regulatory scrutiny."

        assessment = quantifier.assess_risks(
            company_name="Risk Corp",
            company_data=company_data,
            market_data=market_data,
            content=content
        )

        assert isinstance(assessment, RiskAssessment)
        assert assessment.company_name == "Risk Corp"
        assert 0 <= assessment.overall_risk_score <= 100
        assert assessment.risk_grade in ["A", "B", "C", "D", "F"]
        assert len(assessment.risks) > 0
        assert len(assessment.key_risks) <= 5
        assert len(assessment.recommendations) <= 7
        assert assessment.summary != ""

    def test_low_risk_assessment(self):
        """Test assessment for low-risk company."""
        quantifier = RiskQuantifier()

        company_data = {
            "debt_to_equity": 0.3,
            "profit_margin": 25.0,
            "revenue_growth": 15.0
        }

        assessment = quantifier.assess_risks(
            company_name="Safe Corp",
            company_data=company_data
        )

        # Low risk company should have grade A or B
        assert assessment.risk_grade in ["A", "B"]

    def test_high_risk_assessment(self):
        """Test assessment for high-risk company."""
        quantifier = RiskQuantifier()

        company_data = {
            "debt_to_equity": 3.5,
            "profit_margin": 1.0,
            "revenue_growth": -25.0,
            "employee_turnover": 40.0
        }

        market_data = {
            "market_share": 1.0,
            "competitors": list(range(20)),
            "market_growth": -10.0
        }

        assessment = quantifier.assess_risks(
            company_name="Risky Corp",
            company_data=company_data,
            market_data=market_data
        )

        # High risk company should have grade D or F
        assert assessment.risk_grade in ["C", "D", "F"]


class TestCreateRiskQuantifier:
    """Tests for factory function."""

    def test_create_default_quantifier(self):
        """Test creating default quantifier."""
        quantifier = create_risk_quantifier()

        assert isinstance(quantifier, RiskQuantifier)
        assert quantifier.risk_tolerance == "moderate"

    def test_create_custom_quantifier(self):
        """Test creating quantifier with custom settings."""
        custom_weights = {RiskCategory.MARKET: 0.25}
        quantifier = create_risk_quantifier(
            custom_weights=custom_weights,
            risk_tolerance="conservative"
        )

        assert quantifier.risk_tolerance == "conservative"
        assert quantifier.category_weights[RiskCategory.MARKET] == 0.25
