# Contributing to Company Researcher System

Thank you for your interest in contributing! This document provides guidelines and standards for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Commit Conventions](#commit-conventions)
7. [Pull Request Process](#pull-request-process)
8. [Documentation](#documentation)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize project goals over personal preferences

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- PostgreSQL 14+
- Docker
- API keys (Anthropic, Tavily)

### Initial Setup

```bash
# Fork and clone
git clone https://github.com/your-username/company-researcher.git
cd company-researcher

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start dependencies
docker-compose up -d

# Run tests to verify setup
pytest
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Always branch from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

**Examples:**
- `feature/memory-system`
- `fix/financial-agent-timeout`
- `docs/api-specification`
- `refactor/supervisor-logic`

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards below
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_financial_agent.py

# Check coverage report
open htmlcov/index.html
```

### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add financial agent implementation"

# See "Commit Conventions" section below
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Fill out the PR template
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications.

#### Formatting

**Tool:** [Black](https://black.readthedocs.io/) (line length: 88)

```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/ tests/
```

#### Linting

**Tool:** [Ruff](https://github.com/astral-sh/ruff)

```bash
# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

#### Type Hints

**Tool:** [mypy](https://mypy-lang.org/)

```python
# Always use type hints
def research_company(name: str, deep: bool = False) -> dict[str, Any]:
    """Research a company and return structured data."""
    ...

# For complex types, use typing module
from typing import Optional, List, Dict, Any

def get_past_research(
    company: str,
    limit: int = 10
) -> Optional[List[Dict[str, Any]]]:
    ...
```

```bash
# Check types
mypy src/
```

### Code Organization

```python
# Standard library imports
import asyncio
from datetime import datetime
from typing import Any, Optional

# Third-party imports
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
import anthropic

# Local imports
from src.agents.base import BaseAgent
from src.state import ResearchState
from src.utils import logger

# Constants
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Classes and functions
class FinancialAgent(BaseAgent):
    """Agent for financial analysis."""

    def __init__(self, config: dict) -> None:
        """Initialize financial agent."""
        super().__init__(config)
        self.model = "claude-3-5-sonnet-20241022"
```

### Naming Conventions

```python
# Classes: PascalCase
class FinancialAgent:
    pass

# Functions/methods: snake_case
def research_company(name: str) -> dict:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods/attributes: _leading_underscore
def _internal_helper(self) -> None:
    pass

# Type variables: PascalCase with T prefix
from typing import TypeVar
TState = TypeVar('TState', bound=ResearchState)
```

### Docstrings

Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

```python
def research_company(
    name: str,
    deep: bool = False,
    include_agents: Optional[list[str]] = None
) -> dict[str, Any]:
    """Research a company using multi-agent system.

    Args:
        name: Company name to research (e.g., "Tesla").
        deep: Whether to perform deep research with all agents.
        include_agents: Optional list of specific agents to use.
            If None, uses default agent set.

    Returns:
        Dictionary containing research results:
            - company_name: str
            - overview: dict
            - financial: dict
            - competitive: dict
            - sources: list[dict]

    Raises:
        ValueError: If company name is empty.
        APIError: If API calls fail after retries.

    Example:
        >>> research = research_company("Tesla", deep=True)
        >>> print(research["company_name"])
        Tesla
    """
    ...
```

### Error Handling

```python
# Specific exceptions
try:
    result = await api_call()
except anthropic.APIError as e:
    logger.error(f"API call failed: {e}")
    raise ResearchError(f"Failed to research company: {e}") from e
except TimeoutError:
    logger.warning("Request timed out, retrying...")
    return await retry_with_backoff(api_call)

# Don't catch generic Exception unless re-raising
# Bad:
try:
    risky_operation()
except Exception:
    pass  # Silent failure!

# Good:
try:
    risky_operation()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/               # Unit tests (isolated, fast)
│   ├── test_agents.py
│   ├── test_state.py
│   └── test_utils.py
├── integration/        # Integration tests (API calls, DB)
│   ├── test_workflow.py
│   └── test_api.py
└── conftest.py         # Shared fixtures
```

### Writing Tests

```python
import pytest
from src.agents import FinancialAgent
from src.state import ResearchState

class TestFinancialAgent:
    """Test suite for Financial Agent."""

    @pytest.fixture
    def agent(self):
        """Create a financial agent for testing."""
        config = {"model": "claude-3-5-sonnet-20241022"}
        return FinancialAgent(config)

    @pytest.fixture
    def sample_state(self):
        """Create sample research state."""
        return ResearchState(
            company_name="Tesla",
            industry="Automotive"
        )

    def test_extract_financial_data(self, agent, sample_state):
        """Test financial data extraction."""
        # Arrange
        mock_data = {...}

        # Act
        result = agent.extract_financials(sample_state, mock_data)

        # Assert
        assert result["revenue"] > 0
        assert "currency" in result
        assert len(result["sources"]) > 0

    @pytest.mark.asyncio
    async def test_async_research(self, agent, sample_state):
        """Test async research workflow."""
        result = await agent.research(sample_state)
        assert result is not None
```

### Test Coverage

- **Minimum:** 70% overall coverage
- **Target:** 80%+ coverage
- **Critical paths:** 90%+ coverage (agents, orchestration)

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View report
open htmlcov/index.html
```

### Mocking

```python
from unittest.mock import Mock, patch, AsyncMock

# Mock API calls
@patch('src.agents.financial.anthropic_client')
def test_with_mocked_api(mock_client):
    mock_client.messages.create.return_value = Mock(
        content=[Mock(text="Mock response")]
    )
    # Test code here

# Mock async functions
@pytest.mark.asyncio
async def test_async_with_mock():
    with patch('src.research.search_web', new_callable=AsyncMock) as mock:
        mock.return_value = {"results": []}
        # Test async code
```

---

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code restructuring without behavior change
- `perf:` - Performance improvement
- `test:` - Adding tests
- `chore:` - Maintenance tasks, dependencies

### Examples

```bash
# Feature
git commit -m "feat(agents): add memory search capability"

# Bug fix
git commit -m "fix(supervisor): resolve agent timeout issue"

# Documentation
git commit -m "docs(api): update WebSocket examples"

# Breaking change
git commit -m "feat(state)!: change state schema structure

BREAKING CHANGE: ResearchState now requires 'version' field"
```

---

## Pull Request Process

### Before Creating PR

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation
- [ ] No console.log or debug statements
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe tests added/modified

## Checklist
- [ ] Tests pass
- [ ] Code formatted (black)
- [ ] Linted (ruff)
- [ ] Type-checked (mypy)
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks:** CI/CD must pass
2. **Code Review:** At least 1 approval required
3. **Testing:** Reviewer should test locally if needed
4. **Merge:** Squash and merge to main

### After Merge

- Delete branch
- Update related issues
- Update CHANGELOG.md for significant changes

---

## Documentation

### When to Update Docs

- Adding new features → Update relevant .md files
- Changing APIs → Update [docs/api-specification.md](docs/api-specification.md)
- New agent → Update [docs/agent-specifications.md](docs/agent-specifications.md)
- Architecture changes → Update [docs/architecture.md](docs/architecture.md)

### Documentation Standards

- Clear, concise language
- Code examples for new features
- Screenshots/diagrams where helpful
- Keep README.md up to date

---

## Questions?

- **Documentation:** Check [docs/](docs/) first
- **Issues:** Search existing issues on GitHub
- **Discussions:** Use GitHub Discussions for questions
- **Contact:** [Maintainer email/contact]

---

Thank you for contributing! 🎉
