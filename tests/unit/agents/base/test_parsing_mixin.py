"""
Unit tests for ParsingMixin extraction utilities.

Tests all extraction methods in the ParsingMixin class used by specialist agents.
"""

from src.company_researcher.agents.base import ParsingMixin

# Sample analysis texts for testing
SAMPLE_ANALYSIS = """
### Brand Overview
**Brand Score:** 75
**Brand Strength:** STRONG

### 1. Brand Perception Metrics
| Metric | Score | Trend |
|--------|-------|-------|
| Brand Awareness | 80 | improving |
| Brand Trust | 65 | stable |
| Brand Loyalty | 70 | declining |

### 2. Strengths
1. Strong market presence in key segments
2. Excellent customer service reputation
3. Innovative product lineup

### 3. Weaknesses
- Limited international expansion
- Higher price point than competitors

Overall Sentiment: POSITIVE

Followers: 1.2M
Engagement Rate: 3.5%
Revenue: $2.5B
Employees: 15,000
"""

SAMPLE_TABLE_ANALYSIS = """
### Pain Points Analysis
| Pain Point | Severity | Evidence |
|------------|----------|----------|
| Slow response time | HIGH | Customer complaints |
| Limited integrations | MEDIUM | Feature requests |
| Price concerns | LOW | Sales feedback |

### Buying Signals
| Signal Type | Description | Strength |
|-------------|-------------|----------|
| Hiring | New CTO hired | STRONG |
| Technology | Migration to cloud | MODERATE |
"""


class TestExtractScore:
    """Tests for extract_score method."""

    def test_extract_basic_score(self):
        """Test extracting score with colon separator."""
        result = ParsingMixin.extract_score(SAMPLE_ANALYSIS, "Brand Score")
        assert result == 75.0

    def test_extract_score_from_table(self):
        """Test extracting score from table context."""
        result = ParsingMixin.extract_score(SAMPLE_ANALYSIS, "Brand Awareness")
        assert result == 80.0

    def test_extract_score_not_found(self):
        """Test default when score not found."""
        result = ParsingMixin.extract_score(SAMPLE_ANALYSIS, "NonExistent")
        assert result == 50.0  # Default

    def test_extract_score_custom_default(self):
        """Test custom default value."""
        result = ParsingMixin.extract_score(SAMPLE_ANALYSIS, "NonExistent", default=0.0)
        assert result == 0.0

    def test_extract_score_with_max_value(self):
        """Test score capped at max value."""
        text = "Score: 150"
        result = ParsingMixin.extract_score(text, "Score", max_value=100.0)
        assert result == 100.0


class TestExtractEnumValue:
    """Tests for extract_enum_value method."""

    def test_extract_basic_enum(self):
        """Test extracting enum value."""
        result = ParsingMixin.extract_enum_value(
            SAMPLE_ANALYSIS, "Brand Strength", ["STRONG", "MODERATE", "WEAK"], "MODERATE"
        )
        assert result == "strong"

    def test_extract_enum_not_found(self):
        """Test default when enum not found."""
        result = ParsingMixin.extract_enum_value(
            SAMPLE_ANALYSIS, "NonExistent", ["HIGH", "MEDIUM", "LOW"], "LOW"
        )
        assert result == "low"

    def test_extract_enum_case_insensitive(self):
        """Test case insensitive matching."""
        text = "Severity: high"
        result = ParsingMixin.extract_enum_value(text, "Severity", ["HIGH", "MEDIUM", "LOW"], "LOW")
        assert result == "high"


class TestExtractListItems:
    """Tests for extract_list_items method."""

    def test_extract_numbered_list(self):
        """Test extracting numbered list items."""
        result = ParsingMixin.extract_list_items(SAMPLE_ANALYSIS, "Strength")
        assert len(result) == 3
        assert "Strong market presence" in result[0]

    def test_extract_bulleted_list(self):
        """Test extracting bulleted list items."""
        result = ParsingMixin.extract_list_items(SAMPLE_ANALYSIS, "Weakness")
        assert len(result) == 2
        assert "Limited international" in result[0]

    def test_extract_list_max_items(self):
        """Test max_items parameter."""
        result = ParsingMixin.extract_list_items(SAMPLE_ANALYSIS, "Strength", max_items=2)
        assert len(result) == 2

    def test_extract_list_not_found(self):
        """Test empty list when section not found."""
        result = ParsingMixin.extract_list_items(SAMPLE_ANALYSIS, "NonExistent")
        assert result == []


class TestExtractTableRows:
    """Tests for extract_table_rows method."""

    def test_extract_basic_table(self):
        """Test extracting table rows."""
        result = ParsingMixin.extract_table_rows(SAMPLE_TABLE_ANALYSIS, "Pain Point")
        assert len(result) == 3
        assert result[0][0] == "Slow response time"
        assert result[0][1] == "HIGH"

    def test_extract_table_max_rows(self):
        """Test max_rows parameter."""
        result = ParsingMixin.extract_table_rows(SAMPLE_TABLE_ANALYSIS, "Pain Point", max_rows=2)
        assert len(result) == 2

    def test_extract_table_min_columns(self):
        """Test min_columns filtering."""
        result = ParsingMixin.extract_table_rows(SAMPLE_TABLE_ANALYSIS, "Pain Point", min_columns=3)
        assert len(result) == 3  # All rows have 3 columns

    def test_extract_table_not_found(self):
        """Test empty list when table not found."""
        result = ParsingMixin.extract_table_rows(SAMPLE_TABLE_ANALYSIS, "NonExistent")
        assert result == []


class TestExtractKeywordList:
    """Tests for extract_keyword_list method."""

    def test_extract_by_keyword(self):
        """Test extracting lines containing keyword."""
        result = ParsingMixin.extract_keyword_list(SAMPLE_TABLE_ANALYSIS, "Hiring")
        assert len(result) >= 1

    def test_extract_keyword_max_items(self):
        """Test max_items parameter."""
        result = ParsingMixin.extract_keyword_list(SAMPLE_ANALYSIS, "Brand", max_items=2)
        assert len(result) <= 2


class TestExtractMetricsTable:
    """Tests for extract_metrics_table method."""

    def test_extract_metrics(self):
        """Test extracting metrics with scores and trends."""
        metrics = ParsingMixin.extract_metrics_table(
            SAMPLE_ANALYSIS, ["Brand Awareness", "Brand Trust", "Brand Loyalty"]
        )
        assert "Brand Awareness" in metrics
        assert metrics["Brand Awareness"]["score"] == 80.0
        assert metrics["Brand Awareness"]["trend"] == "improving"
        assert metrics["Brand Trust"]["trend"] == "stable"
        assert metrics["Brand Loyalty"]["trend"] == "declining"

    def test_extract_metrics_not_found(self):
        """Test empty dict for missing metrics."""
        metrics = ParsingMixin.extract_metrics_table(SAMPLE_ANALYSIS, ["NonExistent"])
        assert "NonExistent" not in metrics


class TestExtractCount:
    """Tests for extract_count method."""

    def test_extract_count_millions(self):
        """Test extracting count with M suffix."""
        result = ParsingMixin.extract_count(SAMPLE_ANALYSIS, "Followers")
        assert result == 1200000

    def test_extract_count_billions(self):
        """Test extracting count with B suffix."""
        result = ParsingMixin.extract_count(SAMPLE_ANALYSIS, "Revenue")
        assert result == 2500000000

    def test_extract_count_thousands(self):
        """Test extracting count with comma separator."""
        result = ParsingMixin.extract_count(SAMPLE_ANALYSIS, "Employees")
        assert result == 15000

    def test_extract_count_not_found(self):
        """Test zero when count not found."""
        result = ParsingMixin.extract_count(SAMPLE_ANALYSIS, "NonExistent")
        assert result == 0


class TestExtractSentiment:
    """Tests for extract_sentiment method."""

    def test_extract_positive_sentiment(self):
        """Test extracting positive sentiment."""
        result = ParsingMixin.extract_sentiment(SAMPLE_ANALYSIS)
        assert result == "positive"

    def test_extract_negative_sentiment(self):
        """Test extracting negative sentiment."""
        text = "Overall Sentiment: NEGATIVE. Many concerns about quality."
        result = ParsingMixin.extract_sentiment(text)
        assert result == "negative"

    def test_extract_mixed_sentiment(self):
        """Test extracting mixed sentiment."""
        text = "The sentiment is MIXED with both positives and negatives."
        result = ParsingMixin.extract_sentiment(text)
        assert result == "mixed"

    def test_extract_neutral_sentiment(self):
        """Test neutral as default."""
        text = "No clear sentiment indicated in this analysis."
        result = ParsingMixin.extract_sentiment(text)
        assert result == "neutral"


class TestExtractBoolean:
    """Tests for extract_boolean method."""

    def test_extract_boolean_true(self):
        """Test extracting true value."""
        text = "Feature Active: Yes"
        result = ParsingMixin.extract_boolean(text, "Active")
        assert result is True

    def test_extract_boolean_false(self):
        """Test extracting false value."""
        text = "Feature Active: No"
        result = ParsingMixin.extract_boolean(text, "Active")
        assert result is False

    def test_extract_boolean_default(self):
        """Test default when not found."""
        text = "Some unrelated text"
        result = ParsingMixin.extract_boolean(text, "Active", default=True)
        assert result is True

    def test_extract_boolean_custom_indicators(self):
        """Test custom true/false indicators."""
        text = "Status: enabled"
        result = ParsingMixin.extract_boolean(
            text, "Status", true_indicators=["enabled"], false_indicators=["disabled"]
        )
        assert result is True


class TestExtractPercentage:
    """Tests for extract_percentage method."""

    def test_extract_percentage(self):
        """Test extracting percentage value."""
        result = ParsingMixin.extract_percentage(SAMPLE_ANALYSIS, "Engagement Rate")
        assert result == 3.5

    def test_extract_percentage_not_found(self):
        """Test default when percentage not found."""
        result = ParsingMixin.extract_percentage(SAMPLE_ANALYSIS, "NonExistent")
        assert result == 0.0

    def test_extract_percentage_custom_default(self):
        """Test custom default value."""
        result = ParsingMixin.extract_percentage(SAMPLE_ANALYSIS, "NonExistent", default=50.0)
        assert result == 50.0


class TestExtractSection:
    """Tests for extract_section method."""

    def test_extract_section(self):
        """Test extracting section content."""
        text = """
Recommended Approach:
Use a consultative selling methodology.
Focus on value proposition.
"""
        result = ParsingMixin.extract_section(text, "Recommended Approach")
        assert "consultative" in result.lower()

    def test_extract_section_not_found(self):
        """Test empty string when section not found."""
        result = ParsingMixin.extract_section(SAMPLE_ANALYSIS, "NonExistent")
        assert result == ""


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_analysis(self):
        """Test with empty analysis string."""
        assert ParsingMixin.extract_score("", "Score") == 50.0
        assert ParsingMixin.extract_list_items("", "Items") == []
        assert ParsingMixin.extract_sentiment("") == "neutral"

    def test_special_characters_in_keyword(self):
        """Test keywords with special regex characters."""
        text = "Score (final): 85"
        result = ParsingMixin.extract_score(text, "Score (final)")
        assert result == 85.0

    def test_unicode_content(self):
        """Test handling of unicode characters."""
        text = "Brand Score: 75 ★★★★"
        result = ParsingMixin.extract_score(text, "Brand Score")
        assert result == 75.0

    def test_multiline_content(self):
        """Test extracting from multiline content."""
        text = """
Brand
Score: 75
"""
        result = ParsingMixin.extract_score(text, "Score")
        assert result == 75.0
