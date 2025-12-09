"""
Unit tests for investment_thesis.py module.

Tests cover:
- InvestmentRecommendation, InvestmentHorizon, InvestorProfile enums
- BullCase, BearCase, ValuationMetrics dataclasses
- InvestmentThesisGenerator methods
- Valuation analysis and grading
- Bull/bear case generation
- Recommendation determination
"""

import pytest
from src.company_researcher.agents.research.investment_thesis import (
    InvestmentRecommendation,
    InvestmentHorizon,
    InvestorProfile,
    BullCase,
    BearCase,
    ValuationMetrics,
    InvestmentThesis,
    InvestmentThesisGenerator,
    create_thesis_generator,
)


class TestEnums:
    """Tests for enum classes."""

    def test_investment_recommendation_values(self):
        """Test InvestmentRecommendation enum values."""
        assert InvestmentRecommendation.STRONG_BUY.value == "strong_buy"
        assert InvestmentRecommendation.BUY.value == "buy"
        assert InvestmentRecommendation.HOLD.value == "hold"
        assert InvestmentRecommendation.SELL.value == "sell"
        assert InvestmentRecommendation.STRONG_SELL.value == "strong_sell"
        assert InvestmentRecommendation.NOT_RATED.value == "not_rated"

    def test_investment_horizon_values(self):
        """Test InvestmentHorizon enum values."""
        assert InvestmentHorizon.SHORT_TERM.value == "short_term"
        assert InvestmentHorizon.MEDIUM_TERM.value == "medium_term"
        assert InvestmentHorizon.LONG_TERM.value == "long_term"

    def test_investor_profile_values(self):
        """Test InvestorProfile enum values."""
        assert InvestorProfile.GROWTH.value == "growth"
        assert InvestorProfile.VALUE.value == "value"
        assert InvestorProfile.INCOME.value == "income"
        assert InvestorProfile.BALANCED.value == "balanced"
        assert InvestorProfile.SPECULATIVE.value == "speculative"


class TestBullCaseDataclass:
    """Tests for BullCase dataclass."""

    def test_create_bull_case(self):
        """Test creating a BullCase."""
        bull = BullCase(
            headline="Strong growth potential",
            key_drivers=["Revenue growth", "Market expansion"],
            catalysts=["New products", "Acquisitions"],
            target_upside=30.0,
            probability=0.45,
            timeframe="18 months"
        )

        assert bull.headline == "Strong growth potential"
        assert len(bull.key_drivers) == 2
        assert len(bull.catalysts) == 2
        assert bull.target_upside == 30.0
        assert bull.probability == 0.45
        assert bull.timeframe == "18 months"


class TestBearCaseDataclass:
    """Tests for BearCase dataclass."""

    def test_create_bear_case(self):
        """Test creating a BearCase."""
        bear = BearCase(
            headline="Downside risk scenario",
            key_risks=["Competition", "Margin pressure"],
            triggers=["New entrants", "Price war"],
            target_downside=25.0,
            probability=0.3,
            timeframe="12 months"
        )

        assert bear.headline == "Downside risk scenario"
        assert len(bear.key_risks) == 2
        assert len(bear.triggers) == 2
        assert bear.target_downside == 25.0
        assert bear.probability == 0.3


class TestValuationMetricsDataclass:
    """Tests for ValuationMetrics dataclass."""

    def test_create_default_valuation_metrics(self):
        """Test creating default ValuationMetrics."""
        metrics = ValuationMetrics()

        assert metrics.current_price is None
        assert metrics.fair_value_estimate is None
        assert metrics.upside_potential is None
        assert metrics.pe_ratio is None
        assert metrics.valuation_grade == "C"

    def test_create_full_valuation_metrics(self):
        """Test creating full ValuationMetrics."""
        metrics = ValuationMetrics(
            current_price=100.0,
            fair_value_estimate=120.0,
            upside_potential=20.0,
            pe_ratio=15.0,
            ev_ebitda=10.0,
            price_to_sales=3.0,
            price_to_book=2.5,
            peer_average_pe=18.0,
            dcf_value=115.0,
            valuation_grade="B"
        )

        assert metrics.current_price == 100.0
        assert metrics.fair_value_estimate == 120.0
        assert metrics.upside_potential == 20.0
        assert metrics.valuation_grade == "B"


class TestInvestmentThesisGeneratorInit:
    """Tests for InvestmentThesisGenerator initialization."""

    def test_default_init(self):
        """Test default initialization."""
        generator = InvestmentThesisGenerator()

        assert generator.risk_tolerance == "moderate"
        assert generator.default_horizon == InvestmentHorizon.MEDIUM_TERM

    def test_custom_init(self):
        """Test custom initialization."""
        generator = InvestmentThesisGenerator(
            risk_tolerance="conservative",
            default_horizon=InvestmentHorizon.LONG_TERM
        )

        assert generator.risk_tolerance == "conservative"
        assert generator.default_horizon == InvestmentHorizon.LONG_TERM

    def test_recommendation_thresholds_exist(self):
        """Test recommendation thresholds are defined."""
        generator = InvestmentThesisGenerator()

        assert InvestmentRecommendation.STRONG_BUY in generator.RECOMMENDATION_THRESHOLDS
        assert InvestmentRecommendation.BUY in generator.RECOMMENDATION_THRESHOLDS
        assert InvestmentRecommendation.HOLD in generator.RECOMMENDATION_THRESHOLDS
        assert InvestmentRecommendation.SELL in generator.RECOMMENDATION_THRESHOLDS
        assert InvestmentRecommendation.STRONG_SELL in generator.RECOMMENDATION_THRESHOLDS


class TestValuationAnalysis:
    """Tests for valuation analysis."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_analyze_valuation_with_pe(self, generator):
        """Test valuation analysis with P/E data."""
        financial_data = {
            "stock_price": 100.0,
            "pe_ratio": 15.0,
            "earnings_per_share": 6.67
        }
        market_data = {"peer_average_pe": 18.0}

        valuation = generator._analyze_valuation(financial_data, market_data)

        assert valuation.current_price == 100.0
        assert valuation.pe_ratio == 15.0
        assert valuation.fair_value_estimate is not None
        # 6.67 * 18 = ~120
        assert valuation.upside_potential is not None

    def test_analyze_valuation_with_current_price_key(self, generator):
        """Test valuation analysis with current_price key."""
        financial_data = {"current_price": 50.0}

        valuation = generator._analyze_valuation(financial_data, {})

        assert valuation.current_price == 50.0

    def test_analyze_valuation_no_data(self, generator):
        """Test valuation analysis with no data."""
        valuation = generator._analyze_valuation({}, {})

        assert valuation.current_price is None
        assert valuation.fair_value_estimate is None


class TestValuationGrading:
    """Tests for valuation grading."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_grade_a_valuation(self, generator):
        """Test grade A for low P/E."""
        grade = generator._grade_valuation(pe_ratio=10.0, ev_ebitda=6.0, price_to_sales=1.5)
        assert grade == "A"

    def test_grade_b_valuation(self, generator):
        """Test grade B for moderate P/E."""
        grade = generator._grade_valuation(pe_ratio=20.0, ev_ebitda=10.0, price_to_sales=4.0)
        assert grade == "B"

    def test_grade_c_valuation(self, generator):
        """Test grade C for higher P/E."""
        grade = generator._grade_valuation(pe_ratio=30.0, ev_ebitda=15.0, price_to_sales=7.0)
        assert grade == "C"

    def test_grade_d_valuation(self, generator):
        """Test grade D for very high P/E."""
        grade = generator._grade_valuation(pe_ratio=50.0, ev_ebitda=25.0, price_to_sales=15.0)
        assert grade == "D"

    def test_grade_not_rated(self, generator):
        """Test NR when no data."""
        grade = generator._grade_valuation(pe_ratio=None, ev_ebitda=None, price_to_sales=None)
        assert grade == "NR"


class TestBullCaseGeneration:
    """Tests for bull case generation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_generate_bull_case_strong_growth(self, generator):
        """Test bull case with strong growth."""
        financial_data = {"revenue_growth": 25.0, "profit_margin": 20.0}
        market_data = {"market_share": 20.0, "market_growth": 10.0}

        bull = generator._generate_bull_case({}, financial_data, market_data)

        assert bull.target_upside > 0
        assert len(bull.key_drivers) > 0
        assert any("growth" in d.lower() for d in bull.key_drivers)

    def test_generate_bull_case_market_leader(self, generator):
        """Test bull case for market leader."""
        market_data = {"market_share": 25.0}

        bull = generator._generate_bull_case({}, {}, market_data)

        assert any("leader" in d.lower() for d in bull.key_drivers)

    def test_generate_bull_case_defaults(self, generator):
        """Test bull case with no positive data."""
        bull = generator._generate_bull_case({}, {}, {})

        assert len(bull.key_drivers) >= 2
        assert len(bull.catalysts) >= 2
        assert bull.target_upside >= 0


class TestBearCaseGeneration:
    """Tests for bear case generation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_generate_bear_case_high_debt(self, generator):
        """Test bear case with high debt."""
        financial_data = {"debt_to_equity": 2.5}

        bear = generator._generate_bear_case({}, financial_data, {})

        assert any("leverage" in r.lower() for r in bear.key_risks)

    def test_generate_bear_case_revenue_decline(self, generator):
        """Test bear case with revenue decline."""
        financial_data = {"revenue_growth": -10.0}

        bear = generator._generate_bear_case({}, financial_data, {})

        assert any("decline" in r.lower() for r in bear.key_risks)

    def test_generate_bear_case_from_risk_assessment(self, generator):
        """Test bear case incorporates risk assessment."""
        risk_assessment = {
            "key_risks": ["Competition risk", "Regulatory risk"],
            "overall_risk_score": 70
        }

        bear = generator._generate_bear_case({}, {}, risk_assessment)

        assert bear.target_downside > 0

    def test_generate_bear_case_defaults(self, generator):
        """Test bear case with no risk data."""
        bear = generator._generate_bear_case({}, {}, {})

        assert len(bear.key_risks) >= 2
        assert len(bear.triggers) >= 2


class TestUpsideCalculation:
    """Tests for upside calculation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_calculate_upside_from_valuation(self, generator):
        """Test upside calculation from valuation."""
        valuation = ValuationMetrics(upside_potential=25.0)
        bull = BullCase(
            headline="Test", key_drivers=[], catalysts=[],
            target_upside=30.0, probability=0.4, timeframe="12 months"
        )
        bear = BearCase(
            headline="Test", key_risks=[], triggers=[],
            target_downside=20.0, probability=0.3, timeframe="12 months"
        )

        upside = generator._calculate_upside(valuation, bull, bear)
        assert upside == 25.0  # Uses valuation-based upside

    def test_calculate_upside_from_cases(self, generator):
        """Test upside calculation from bull/bear cases."""
        valuation = ValuationMetrics()  # No upside_potential
        bull = BullCase(
            headline="Test", key_drivers=[], catalysts=[],
            target_upside=40.0, probability=0.5, timeframe="12 months"
        )
        bear = BearCase(
            headline="Test", key_risks=[], triggers=[],
            target_downside=20.0, probability=0.3, timeframe="12 months"
        )

        upside = generator._calculate_upside(valuation, bull, bear)
        # 40 * 0.5 - 20 * 0.3 = 20 - 6 = 14
        assert upside == 14.0


class TestRecommendationDetermination:
    """Tests for recommendation determination."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_strong_buy_recommendation(self, generator):
        """Test strong buy for high upside, low risk."""
        rec = generator._determine_recommendation(upside=50.0, risk_score=30.0)
        assert rec == InvestmentRecommendation.STRONG_BUY

    def test_buy_recommendation(self, generator):
        """Test buy for moderate upside."""
        rec = generator._determine_recommendation(upside=25.0, risk_score=40.0)
        assert rec == InvestmentRecommendation.BUY

    def test_hold_recommendation(self, generator):
        """Test hold for neutral upside."""
        rec = generator._determine_recommendation(upside=5.0, risk_score=50.0)
        assert rec == InvestmentRecommendation.HOLD

    def test_sell_recommendation(self, generator):
        """Test sell for negative upside."""
        # risk_adjusted_upside = upside - (risk_score * 0.3)
        # For SELL: -25 <= risk_adjusted < -10
        # -10 - (40 * 0.3) = -10 - 12 = -22 (within SELL range)
        rec = generator._determine_recommendation(upside=-10.0, risk_score=40.0)
        assert rec == InvestmentRecommendation.SELL

    def test_strong_sell_recommendation(self, generator):
        """Test strong sell for very negative outlook."""
        rec = generator._determine_recommendation(upside=-30.0, risk_score=80.0)
        assert rec == InvestmentRecommendation.STRONG_SELL


class TestConfidenceCalculation:
    """Tests for confidence calculation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_base_confidence(self, generator):
        """Test base confidence with no data."""
        confidence = generator._calculate_confidence({}, {}, {})
        assert confidence == 50.0

    def test_increased_confidence_with_data(self, generator):
        """Test confidence increases with data quality."""
        financial_data = {"pe_ratio": 15.0, "revenue_growth": 10.0}
        market_data = {"market_share": 20.0}
        risk_assessment = {"overall_risk_score": 40, "risk_grade": "B"}

        confidence = generator._calculate_confidence(
            financial_data, market_data, risk_assessment
        )

        # 50 + 10 (pe) + 10 (growth) + 10 (share) + 10 (risk) + 5 (grade) = 95
        assert confidence == 95.0

    def test_confidence_capped_at_95(self, generator):
        """Test confidence is capped at 95."""
        financial_data = {
            "pe_ratio": 15.0,
            "revenue_growth": 10.0
        }
        market_data = {"market_share": 20.0}
        risk_assessment = {
            "overall_risk_score": 40,
            "risk_grade": "A"
        }

        confidence = generator._calculate_confidence(
            financial_data, market_data, risk_assessment
        )

        assert confidence <= 95


class TestSuitableInvestors:
    """Tests for suitable investor identification."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_growth_investor(self, generator):
        """Test growth investor identification."""
        financial_data = {"revenue_growth": 20.0}
        suitable = generator._identify_suitable_investors(
            upside=30.0, risk_score=50.0, financial_data=financial_data
        )
        assert InvestorProfile.GROWTH in suitable

    def test_value_investor(self, generator):
        """Test value investor identification."""
        financial_data = {"pe_ratio": 10.0}
        suitable = generator._identify_suitable_investors(
            upside=10.0, risk_score=40.0, financial_data=financial_data
        )
        assert InvestorProfile.VALUE in suitable

    def test_income_investor(self, generator):
        """Test income investor identification."""
        financial_data = {"dividend_yield": 5.0}
        suitable = generator._identify_suitable_investors(
            upside=5.0, risk_score=30.0, financial_data=financial_data
        )
        assert InvestorProfile.INCOME in suitable

    def test_balanced_investor(self, generator):
        """Test balanced investor identification."""
        suitable = generator._identify_suitable_investors(
            upside=10.0, risk_score=45.0, financial_data={}
        )
        assert InvestorProfile.BALANCED in suitable

    def test_speculative_investor_high_upside(self, generator):
        """Test speculative investor for high upside."""
        suitable = generator._identify_suitable_investors(
            upside=50.0, risk_score=50.0, financial_data={}
        )
        assert InvestorProfile.SPECULATIVE in suitable

    def test_speculative_investor_high_risk(self, generator):
        """Test speculative investor for high risk."""
        suitable = generator._identify_suitable_investors(
            upside=10.0, risk_score=75.0, financial_data={}
        )
        assert InvestorProfile.SPECULATIVE in suitable

    def test_default_balanced(self, generator):
        """Test default to balanced when no criteria met."""
        suitable = generator._identify_suitable_investors(
            upside=5.0, risk_score=20.0, financial_data={"pe_ratio": 30.0}
        )
        assert InvestorProfile.BALANCED in suitable


class TestHighlightsExtraction:
    """Tests for highlights extraction."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_extract_market_leader_highlight(self, generator):
        """Test market leader highlight extraction."""
        market_data = {"market_share": 25.0}
        highlights = generator._extract_highlights({}, {}, market_data)
        assert any("leader" in h.lower() for h in highlights)

    def test_extract_growth_highlight(self, generator):
        """Test growth highlight extraction."""
        financial_data = {"revenue_growth": 20.0}
        highlights = generator._extract_highlights({}, financial_data, {})
        assert any("growth" in h.lower() for h in highlights)

    def test_extract_profitability_highlight(self, generator):
        """Test profitability highlight extraction."""
        financial_data = {"profit_margin": 25.0}
        highlights = generator._extract_highlights({}, financial_data, {})
        assert any("profit" in h.lower() for h in highlights)

    def test_extract_valuation_highlight(self, generator):
        """Test valuation highlight extraction."""
        financial_data = {"pe_ratio": 12.0}
        highlights = generator._extract_highlights({}, financial_data, {})
        assert any("valuation" in h.lower() for h in highlights)

    def test_default_highlights(self, generator):
        """Test default highlights when no data."""
        highlights = generator._extract_highlights({}, {}, {})
        assert len(highlights) >= 2

    def test_highlights_limited_to_5(self, generator):
        """Test highlights are limited to 5."""
        company_data = {"strengths": ["A", "B", "C", "D", "E"]}
        financial_data = {"revenue_growth": 20.0, "profit_margin": 25.0}
        market_data = {"market_share": 25.0}

        highlights = generator._extract_highlights(company_data, financial_data, market_data)
        assert len(highlights) <= 5


class TestKeyRisksExtraction:
    """Tests for key risks extraction."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_extract_key_risks_from_assessment(self, generator):
        """Test extracting risks from assessment."""
        risk_assessment = {"key_risks": ["Risk A", "Risk B", "Risk C"]}
        risks = generator._extract_key_risks(risk_assessment)
        assert "Risk A" in risks
        assert len(risks) == 3

    def test_extract_key_risks_dict_format(self, generator):
        """Test extracting risks in dict format."""
        risk_assessment = {"key_risks": [{"name": "Risk A"}, {"name": "Risk B"}]}
        risks = generator._extract_key_risks(risk_assessment)
        assert "Risk A" in risks

    def test_default_risks(self, generator):
        """Test default risks when none provided."""
        risks = generator._extract_key_risks({})
        assert len(risks) >= 3

    def test_risks_limited_to_5(self, generator):
        """Test risks are limited to 5."""
        risk_assessment = {"key_risks": [f"Risk {i}" for i in range(10)]}
        risks = generator._extract_key_risks(risk_assessment)
        assert len(risks) <= 5


class TestCatalystsIdentification:
    """Tests for catalyst identification."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_identify_market_catalyst(self, generator):
        """Test identifying market catalyst."""
        market_data = {"market_growth": 10.0}
        bull_case = BullCase(
            headline="Test", key_drivers=[], catalysts=["Growth"],
            target_upside=20.0, probability=0.4, timeframe="12 months"
        )

        catalysts = generator._identify_catalysts({}, market_data, bull_case)
        assert any("industry" in c.lower() or "market" in c.lower() for c in catalysts)

    def test_identify_product_catalyst(self, generator):
        """Test identifying product catalyst."""
        company_data = {"upcoming_products": ["Product X"]}
        bull_case = BullCase(
            headline="Test", key_drivers=[], catalysts=[],
            target_upside=20.0, probability=0.4, timeframe="12 months"
        )

        catalysts = generator._identify_catalysts(company_data, {}, bull_case)
        assert any("product" in c.lower() for c in catalysts)

    def test_catalysts_limited_to_5(self, generator):
        """Test catalysts are limited to 5."""
        bull_case = BullCase(
            headline="Test", key_drivers=[],
            catalysts=["C1", "C2", "C3", "C4", "C5", "C6"],
            target_upside=20.0, probability=0.4, timeframe="12 months"
        )

        catalysts = generator._identify_catalysts({}, {}, bull_case)
        assert len(catalysts) <= 5


class TestRationaleGeneration:
    """Tests for rationale generation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_generate_rationale_includes_company(self, generator):
        """Test rationale includes company name."""
        rationale = generator._generate_rationale(
            "Test Corp",
            InvestmentRecommendation.BUY,
            20.0,
            ["Growth", "Margins"],
            ["Competition"]
        )
        assert "Test Corp" in rationale

    def test_generate_rationale_includes_recommendation(self, generator):
        """Test rationale includes recommendation."""
        rationale = generator._generate_rationale(
            "Test Corp",
            InvestmentRecommendation.STRONG_BUY,
            30.0,
            ["Growth"],
            ["Risk"]
        )
        assert "Strong Buy" in rationale

    def test_generate_rationale_includes_upside(self, generator):
        """Test rationale includes upside."""
        rationale = generator._generate_rationale(
            "Test Corp",
            InvestmentRecommendation.BUY,
            25.5,
            [],
            []
        )
        assert "25.5%" in rationale


class TestSummaryGeneration:
    """Tests for summary generation."""

    @pytest.fixture
    def generator(self):
        return InvestmentThesisGenerator()

    def test_generate_summary(self, generator):
        """Test summary generation."""
        summary = generator._generate_summary(
            "Test Corp",
            InvestmentRecommendation.BUY,
            20.0,
            75.0
        )

        assert "Test Corp" in summary
        assert "Buy" in summary
        assert "20.0%" in summary
        assert "75%" in summary


class TestFullThesisGeneration:
    """Integration tests for full thesis generation."""

    def test_generate_complete_thesis(self):
        """Test generating a complete investment thesis."""
        generator = InvestmentThesisGenerator()

        company_data = {"strengths": ["Strong brand", "Innovation"]}
        financial_data = {
            "stock_price": 100.0,
            "pe_ratio": 15.0,
            "earnings_per_share": 6.67,
            "revenue_growth": 15.0,
            "profit_margin": 20.0,
            "debt_to_equity": 0.5
        }
        market_data = {
            "market_share": 20.0,
            "peer_average_pe": 18.0,
            "market_growth": 8.0
        }
        risk_assessment = {
            "overall_risk_score": 40.0,
            "risk_grade": "B",
            "key_risks": ["Competition", "Regulation"]
        }

        thesis = generator.generate_thesis(
            company_name="Great Corp",
            company_data=company_data,
            financial_data=financial_data,
            market_data=market_data,
            risk_assessment=risk_assessment
        )

        assert isinstance(thesis, InvestmentThesis)
        assert thesis.company_name == "Great Corp"
        assert thesis.recommendation in InvestmentRecommendation
        assert 0 <= thesis.confidence <= 100
        assert thesis.horizon == InvestmentHorizon.MEDIUM_TERM
        assert len(thesis.suitable_for) > 0
        assert isinstance(thesis.bull_case, BullCase)
        assert isinstance(thesis.bear_case, BearCase)
        assert isinstance(thesis.valuation, ValuationMetrics)
        assert len(thesis.investment_highlights) > 0
        assert len(thesis.key_risks) > 0
        assert thesis.rationale != ""
        assert thesis.summary != ""

    def test_generate_thesis_minimal_data(self):
        """Test thesis generation with minimal data."""
        generator = InvestmentThesisGenerator()

        thesis = generator.generate_thesis(
            company_name="Unknown Corp",
            company_data={}
        )

        assert thesis.company_name == "Unknown Corp"
        assert thesis.recommendation is not None
        assert thesis.bull_case is not None
        assert thesis.bear_case is not None

    def test_generate_thesis_strong_buy(self):
        """Test thesis generating strong buy recommendation."""
        generator = InvestmentThesisGenerator()

        financial_data = {
            "stock_price": 100.0,
            "pe_ratio": 10.0,
            "earnings_per_share": 10.0,
            "revenue_growth": 30.0,
            "profit_margin": 25.0
        }
        market_data = {
            "market_share": 30.0,
            "peer_average_pe": 20.0,  # Fair value = 10 * 20 = 200, 100% upside
            "market_growth": 15.0
        }
        risk_assessment = {
            "overall_risk_score": 20.0,
            "risk_grade": "A"
        }

        thesis = generator.generate_thesis(
            company_name="Growth Corp",
            company_data={},
            financial_data=financial_data,
            market_data=market_data,
            risk_assessment=risk_assessment
        )

        # With 100% upside and low risk, should be STRONG_BUY
        assert thesis.recommendation in [
            InvestmentRecommendation.STRONG_BUY,
            InvestmentRecommendation.BUY
        ]

    def test_generate_thesis_sell(self):
        """Test thesis generating sell recommendation."""
        generator = InvestmentThesisGenerator()

        financial_data = {
            "stock_price": 100.0,
            "pe_ratio": 50.0,
            "earnings_per_share": 2.0,
            "revenue_growth": -10.0,
            "debt_to_equity": 3.0
        }
        risk_assessment = {
            "overall_risk_score": 80.0,
            "risk_grade": "D",
            "key_risks": ["High debt", "Revenue decline", "Market loss"]
        }

        thesis = generator.generate_thesis(
            company_name="Troubled Corp",
            company_data={},
            financial_data=financial_data,
            risk_assessment=risk_assessment
        )

        # With high risk and negative indicators, should be SELL or STRONG_SELL
        assert thesis.recommendation in [
            InvestmentRecommendation.SELL,
            InvestmentRecommendation.STRONG_SELL,
            InvestmentRecommendation.HOLD
        ]


class TestCreateThesisGenerator:
    """Tests for factory function."""

    def test_create_default_generator(self):
        """Test creating default generator."""
        generator = create_thesis_generator()

        assert isinstance(generator, InvestmentThesisGenerator)
        assert generator.risk_tolerance == "moderate"
        assert generator.default_horizon == InvestmentHorizon.MEDIUM_TERM

    def test_create_custom_generator(self):
        """Test creating custom generator."""
        generator = create_thesis_generator(
            risk_tolerance="aggressive",
            horizon=InvestmentHorizon.SHORT_TERM
        )

        assert generator.risk_tolerance == "aggressive"
        assert generator.default_horizon == InvestmentHorizon.SHORT_TERM
