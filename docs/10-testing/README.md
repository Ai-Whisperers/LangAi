# Testing Guide

This section documents the testing strategy and test suites for Company Researcher.

## Overview

```
tests/
├── unit/                  # Unit tests (fast, no external deps)
├── integration/           # Integration tests
├── conftest.py            # Pytest configuration
├── test_quality_modules.py
├── test_enhanced_workflow_integration.py
├── test_investment_thesis.py
├── test_risk_quantifier.py
└── test_competitive_matrix.py
```

## Test Categories

| Category | Description | Speed | External Deps |
|----------|-------------|-------|---------------|
| **Unit** | Single function/class | Fast | None |
| **Integration** | Multiple components | Medium | Some |
| **E2E** | Full workflow | Slow | All |
| **API** | External API tests | Slow | API keys |

## Running Tests

### All Tests

```bash
# Run all tests
PYTHONPATH=".:$PYTHONPATH" pytest tests/

# With coverage
PYTHONPATH=".:$PYTHONPATH" pytest tests/ --cov=src/company_researcher

# Verbose output
PYTHONPATH=".:$PYTHONPATH" pytest tests/ -v
```

### By Category

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests
pytest tests/ -m integration

# Slow tests
pytest tests/ -m slow

# Tests requiring API keys
pytest tests/ -m requires_api
```

### Specific Tests

```bash
# Single test file
pytest tests/test_quality_modules.py

# Single test function
pytest tests/test_quality_modules.py::test_quality_score_calculation

# Pattern matching
pytest tests/ -k "quality"
```

## Test Configuration

### pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (may use external services)",
    "slow: Slow tests",
    "requires_api: Requires API keys",
    "requires_llm: Requires LLM access"
]
asyncio_mode = "auto"
filterwarnings = [
    "ignore::DeprecationWarning"
]
```

### conftest.py

```python
import pytest
from company_researcher.config import ResearchConfig

@pytest.fixture
def config():
    """Default test configuration."""
    return ResearchConfig(
        anthropic_api_key="test-key",
        tavily_api_key="test-key",
        llm_model="claude-3-haiku-20240307",
        max_iterations=1
    )

@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "title": "Microsoft Q3 2024 Results",
            "url": "https://example.com/msft",
            "content": "Microsoft reported revenue of $198B..."
        }
    ]

@pytest.fixture
def sample_state():
    """Sample workflow state."""
    return {
        "company_name": "Microsoft",
        "search_results": [],
        "agent_outputs": {},
        "iteration_count": 0
    }
```

## Writing Tests

### Unit Tests

```python
# tests/unit/test_quality_checker.py

import pytest
from company_researcher.quality import calculate_quality_score

class TestQualityChecker:

    def test_quality_score_complete_data(self, sample_state):
        """Test quality score with complete data."""
        sample_state["agent_outputs"] = {
            "financial": {"revenue": "$198B"},
            "market": {"market_share": "35%"},
            "product": {"products": ["Azure"]}
        }

        score = calculate_quality_score(sample_state)

        assert score >= 80
        assert score <= 100

    def test_quality_score_missing_data(self, sample_state):
        """Test quality score with missing data."""
        score = calculate_quality_score(sample_state)

        assert score < 50

    def test_quality_score_partial_data(self, sample_state):
        """Test quality score with partial data."""
        sample_state["agent_outputs"] = {
            "financial": {"revenue": "$198B"}
        }

        score = calculate_quality_score(sample_state)

        assert 30 <= score <= 70
```

### Integration Tests

```python
# tests/integration/test_workflow.py

import pytest
from company_researcher.workflows import app

@pytest.mark.integration
@pytest.mark.requires_api
async def test_full_workflow(config):
    """Test complete research workflow."""
    result = await app.ainvoke({
        "company_name": "Microsoft"
    })

    assert result["quality_score"] >= 0
    assert "report_path" in result
    assert result["iteration_count"] >= 1

@pytest.mark.integration
async def test_workflow_with_mock_search(config, mocker):
    """Test workflow with mocked search."""
    mocker.patch(
        "company_researcher.integrations.tavily_search",
        return_value=sample_search_results
    )

    result = await app.ainvoke({
        "company_name": "TestCorp"
    })

    assert result is not None
```

### Agent Tests

```python
# tests/unit/test_financial_agent.py

import pytest
from company_researcher.agents.financial import FinancialAgent

class TestFinancialAgent:

    def test_parse_revenue(self):
        """Test revenue parsing from text."""
        agent = FinancialAgent(config)

        result = agent._parse_revenue("Revenue was $198 billion")

        assert result == "$198B"

    def test_parse_growth(self):
        """Test growth rate parsing."""
        agent = FinancialAgent(config)

        result = agent._parse_growth("grew 7% year-over-year")

        assert result == "7%"

    def test_analyze_complete(self, sample_search_results):
        """Test complete financial analysis."""
        agent = FinancialAgent(config)

        result = agent.analyze("Microsoft", sample_search_results)

        assert "revenue" in result
        assert "analysis" in result
```

### Quality Tests

```python
# tests/test_quality_modules.py

import pytest
from company_researcher.quality import (
    ContradictionDetector,
    detect_gaps
)

class TestContradictionDetector:

    def test_detect_numeric_contradiction(self):
        """Test detection of numeric contradictions."""
        detector = ContradictionDetector()

        agent_outputs = {
            "financial": {"employees": "220,000"},
            "analyst": {"employees": "200,000"}
        }

        contradictions = detector.detect(agent_outputs)

        assert len(contradictions) >= 1
        assert any(c.type == "numeric" for c in contradictions)

    def test_no_contradiction(self):
        """Test no false positives."""
        detector = ContradictionDetector()

        agent_outputs = {
            "financial": {"revenue": "$198B"},
            "analyst": {"revenue": "$198B"}
        }

        contradictions = detector.detect(agent_outputs)

        assert len(contradictions) == 0

class TestGapDetector:

    def test_detect_missing_revenue(self, sample_state):
        """Test detection of missing revenue."""
        gaps = detect_gaps(sample_state)

        assert "revenue" in " ".join(gaps).lower()

    def test_no_gaps_complete_data(self, sample_state):
        """Test no gaps with complete data."""
        sample_state["agent_outputs"] = {
            "financial": {"revenue": "$198B", "growth": "7%"},
            "market": {"market_share": "35%"},
            "product": {"products": ["Azure"]}
        }
        sample_state["products_services"] = ["Azure"]
        sample_state["competitors"] = ["AWS"]

        gaps = detect_gaps(sample_state)

        assert len(gaps) == 0
```

## Mocking External Services

### Mock LLM Responses

```python
@pytest.fixture
def mock_anthropic(mocker):
    """Mock Anthropic client."""
    mock_response = mocker.Mock()
    mock_response.content = [mocker.Mock(text="Analysis result")]
    mock_response.usage = mocker.Mock(input_tokens=100, output_tokens=50)

    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = mock_response

    mocker.patch(
        "company_researcher.llm.get_anthropic_client",
        return_value=mock_client
    )

    return mock_client
```

### Mock Search

```python
@pytest.fixture
def mock_search(mocker):
    """Mock search provider."""
    mocker.patch(
        "company_researcher.integrations.tavily_search",
        return_value=[
            {"title": "Test", "url": "https://test.com", "content": "Test content"}
        ]
    )
```

### Mock Financial Data

```python
@pytest.fixture
def mock_yfinance(mocker):
    """Mock yfinance."""
    mock_ticker = mocker.Mock()
    mock_ticker.info = {
        "totalRevenue": 198000000000,
        "marketCap": 2800000000000
    }

    mocker.patch(
        "yfinance.Ticker",
        return_value=mock_ticker
    )
```

## Test Coverage

### Generate Coverage Report

```bash
# HTML report
pytest tests/ --cov=src/company_researcher --cov-report=html

# Terminal report
pytest tests/ --cov=src/company_researcher --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=src/company_researcher --cov-report=xml
```

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Agents | 80% | - |
| Workflows | 70% | - |
| Quality | 90% | - |
| Integrations | 60% | - |
| Config | 90% | - |

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          pytest tests/ --cov=src/company_researcher --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

**Related Documentation**:
- [Quality System](../08-quality-system/)
- [Agent Documentation](../03-agents/)
- [Configuration](../06-configuration/)

---

**Last Updated**: December 2024
