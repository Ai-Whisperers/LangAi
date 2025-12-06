"""
Pytest Configuration and Fixtures.

Central configuration for all tests in the Company Researcher project.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src to path for imports
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(ROOT_DIR))


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("DEBUG", "true")

    # Disable external API calls in tests by default
    os.environ.setdefault("MOCK_EXTERNAL_APIS", "true")

    yield

    # Cleanup if needed


@pytest.fixture
def mock_llm_response():
    """Provide mock LLM responses for testing."""
    return {
        "content": "This is a mock LLM response for testing.",
        "model": "mock-model",
        "tokens_used": 100,
        "cost": 0.001
    }


@pytest.fixture
def mock_search_results():
    """Provide mock search results for testing."""
    return [
        {
            "title": "Test Company Overview",
            "url": "https://example.com/test",
            "content": "Test company information..."
        },
        {
            "title": "Test Company News",
            "url": "https://example.com/news",
            "content": "Recent news about test company..."
        }
    ]


@pytest.fixture
def sample_company_data():
    """Provide sample company data for testing."""
    return {
        "company_name": "TestCorp Inc.",
        "ticker": "TEST",
        "industry": "Technology",
        "founded": 2010,
        "employees": 5000,
        "revenue": 1000000000,
        "headquarters": "San Francisco, CA"
    }


@pytest.fixture
def sample_research_state():
    """Provide sample research state for testing."""
    return {
        "company_name": "TestCorp Inc.",
        "search_results": [],
        "agent_outputs": {},
        "errors": [],
        "total_cost": 0.0
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_anthropic_client(mocker):
    """Mock Anthropic client for testing."""
    mock = mocker.MagicMock()
    mock.messages.create.return_value = mocker.MagicMock(
        content=[mocker.MagicMock(text="Mock response")]
    )
    return mock


@pytest.fixture
def mock_tavily_client(mocker):
    """Mock Tavily client for testing."""
    mock = mocker.MagicMock()
    mock.search.return_value = {
        "results": [
            {"title": "Result 1", "url": "https://example.com", "content": "Content 1"}
        ]
    }
    return mock


# ============================================================================
# Test Categories Markers
# ============================================================================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "requires_api: Tests requiring external API")
    config.addinivalue_line("markers", "requires_llm: Tests requiring LLM access")
