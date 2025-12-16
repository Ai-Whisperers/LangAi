# Cursor Configuration Completion Analysis

**Date**: 2025-12-12
**Project**: Company Researcher - Multi-Agent Research System
**Tech Stack**: Python 3.11+, LangGraph, LangChain, Pydantic, FastAPI, pytest

---

## Executive Summary

Your `.cursor` directory has a **comprehensive rules/prompts framework** inherited from a C#/.NET project, but it's **missing Python/LangGraph-specific configurations** needed for this AI agent research system. This document outlines everything needed to make `.cursor` complete for this project.

---

## Current State Analysis

### ✅ What You Have (Strong Foundation)

1. **Rules Framework** (`.cursor/rules/`)
   - ✅ Core development rules (clean-code, DRY, naming conventions)
   - ✅ Git workflow rules
   - ✅ Ticket management system
   - ✅ Agile documentation standards
   - ✅ Rule authoring framework
   - ✅ CI/CD patterns
   - ✅ Documentation standards

2. **Prompts System** (`.cursor/prompts/`)
   - ✅ Task workflows for common operations
   - ✅ Collections for organizing prompts
   - ✅ Housekeeping and maintenance prompts

3. **Templars & Exemplars**
   - ✅ Output structure templates
   - ✅ Pattern examples

### ❌ What's Missing (Python/LangGraph Specific)

1. **Python-Specific Rules**
   - Type hints and type safety
   - Async/await patterns
   - Context managers
   - Decorators
   - Exception handling
   - Import organization

2. **LangGraph/LangChain Rules**
   - Agent development patterns
   - State management
   - Node/edge definitions
   - Tool integration
   - Workflow orchestration

3. **Pydantic Model Rules**
   - Model definition standards
   - Validation patterns
   - Serialization/deserialization

4. **Testing Rules** (pytest)
   - Test structure
   - Fixtures and mocks
   - Async testing
   - Coverage requirements

5. **API Development Rules** (FastAPI)
   - Route definitions
   - Dependency injection
   - Response models
   - Error handling

6. **AI Agent-Specific Rules**
   - Agent design patterns
   - Prompt engineering
   - Cost tracking
   - Quality assurance
   - Iteration patterns

7. **Research Workflow Rules**
   - Research schema standards
   - Report generation
   - Data validation
   - Quality scoring

---

## Recommended Additions

### 1. Python Development Rules

#### `.cursor/rules/python/`

**Files to Create:**

- `python-type-hints-rule.mdc`
  - Enforce type hints for all functions
  - Use `typing` module appropriately
  - Handle `Optional`, `Union`, `Dict`, `List`
  - Async function typing

- `python-async-patterns-rule.mdc`
  - Async/await best practices
  - Context managers for async resources
  - Proper exception handling in async code
  - When to use `asyncio.gather()` vs sequential

- `python-import-organization-rule.mdc`
  - Import order (stdlib, third-party, local)
  - Absolute vs relative imports
  - `__all__` declarations
  - Circular dependency prevention

- `python-exception-handling-rule.mdc`
  - Specific exception types
  - Exception chaining (`raise from`)
  - Logging exceptions
  - Custom exception classes

- `python-context-managers-rule.mdc`
  - When to use context managers
  - `@contextmanager` decorator
  - Resource cleanup patterns

- `python-decorators-rule.mdc`
  - Decorator patterns
  - `functools.wraps`
  - Parameterized decorators

**Prompts to Create:**

- `.cursor/prompts/python/`
  - `add-type-hints.prompt.md` - Add type hints to existing code
  - `refactor-to-async.prompt.md` - Convert sync to async
  - `fix-imports.prompt.md` - Organize imports
  - `create-exception-class.prompt.md` - Create custom exception

---

### 2. LangGraph/LangChain Rules

#### `.cursor/rules/langgraph/`

**Files to Create:**

- `langgraph-workflow-rule.mdc`
  - State schema definition
  - Node function structure
  - Edge conditions
  - Compilation patterns
  - Error handling in workflows

- `langgraph-state-management-rule.mdc`
  - State schema design
  - State updates (additive vs replacement)
  - State validation
  - State persistence

- `langgraph-node-patterns-rule.mdc`
  - Node function signatures
  - Return value patterns
  - Error handling in nodes
  - Logging and observability

- `langgraph-tool-integration-rule.mdc`
  - Tool binding patterns
  - Tool error handling
  - Tool result processing
  - Tool validation

- `langchain-prompt-templates-rule.mdc`
  - Prompt template structure
  - Variable substitution
  - Prompt versioning
  - Prompt testing

**Prompts to Create:**

- `.cursor/prompts/langgraph/`
  - `create-workflow.prompt.md` - Create new LangGraph workflow
  - `add-node.prompt.md` - Add node to workflow
  - `debug-workflow.prompt.md` - Debug workflow issues
  - `optimize-workflow.prompt.md` - Optimize workflow performance

---

### 3. Pydantic Model Rules

#### `.cursor/rules/pydantic/`

**Files to Create:**

- `pydantic-model-definition-rule.mdc`
  - Model structure
  - Field definitions
  - Validators and validators
  - Model configuration
  - Nested models

- `pydantic-validation-patterns-rule.mdc`
  - Field validators
  - Model validators
  - Custom validators
  - Validation error handling

- `pydantic-serialization-rule.mdc`
  - `model_dump()` vs `dict()`
  - JSON serialization
  - Excluding fields
  - Custom serializers

**Prompts to Create:**

- `.cursor/prompts/pydantic/`
  - `create-model.prompt.md` - Create new Pydantic model
  - `add-validation.prompt.md` - Add validation to model
  - `migrate-model.prompt.md` - Migrate model version

---

### 4. Testing Rules (pytest)

#### `.cursor/rules/testing/`

**Files to Create:**

- `pytest-test-structure-rule.mdc`
  - Test file organization
  - Test class vs function structure
  - Test naming conventions
  - Test markers

- `pytest-fixtures-rule.mdc`
  - Fixture organization
  - Scope management
  - Parametrized fixtures
  - Fixture dependencies

- `pytest-async-testing-rule.mdc`
  - Async test patterns
  - `pytest-asyncio` usage
  - Async fixtures
  - Async mocking

- `pytest-mocking-rule.mdc`
  - `unittest.mock` patterns
  - `pytest-mock` usage
  - Mocking external APIs
  - Mocking LangGraph workflows

- `pytest-coverage-rule.mdc`
  - Coverage targets (85%+)
  - Coverage exclusions
  - Coverage reporting

**Prompts to Create:**

- `.cursor/prompts/testing/`
  - `generate-tests.prompt.md` - Generate tests for code
  - `add-fixture.prompt.md` - Create new fixture
  - `mock-external-api.prompt.md` - Mock external API calls
  - `check-coverage.prompt.md` - Analyze test coverage

---

### 5. FastAPI Rules

#### `.cursor/rules/api/`

**Files to Create:**

- `fastapi-route-definition-rule.mdc`
  - Route decorators
  - Path parameters
  - Query parameters
  - Request body models
  - Response models

- `fastapi-dependency-injection-rule.mdc`
  - Dependency patterns
  - Shared dependencies
  - Database dependencies
  - Authentication dependencies

- `fastapi-error-handling-rule.mdc`
  - Exception handlers
  - HTTP exception patterns
  - Error response models
  - Validation error handling

- `fastapi-websocket-rule.mdc`
  - WebSocket patterns
  - Streaming responses
  - Connection management

**Prompts to Create:**

- `.cursor/prompts/api/`
  - `create-endpoint.prompt.md` - Create new API endpoint
  - `add-authentication.prompt.md` - Add auth to endpoint
  - `create-websocket.prompt.md` - Create WebSocket endpoint

---

### 6. AI Agent Rules

#### `.cursor/rules/agents/`

**Files to Create:**

- `agent-design-patterns-rule.mdc`
  - Agent responsibilities
  - Agent communication
  - Agent state management
  - Agent error handling

- `agent-prompt-engineering-rule.mdc`
  - Prompt structure for agents
  - System prompts
  - Few-shot examples
  - Prompt versioning

- `agent-cost-tracking-rule.mdc`
  - Token counting
  - Cost calculation
  - Cost optimization
  - Cost reporting

- `agent-quality-assurance-rule.mdc`
  - Quality scoring
  - Quality thresholds
  - Iteration patterns
  - Quality metrics

- `agent-iteration-patterns-rule.mdc`
  - When to iterate
  - Iteration limits
  - Quality improvement strategies
  - Cost vs quality tradeoffs

**Prompts to Create:**

- `.cursor/prompts/agents/`
  - `create-agent.prompt.md` - Create new agent
  - `optimize-agent-cost.prompt.md` - Optimize agent costs
  - `improve-agent-quality.prompt.md` - Improve agent quality
  - `debug-agent.prompt.md` - Debug agent issues

---

### 7. Research Workflow Rules

#### `.cursor/rules/research/`

**Files to Create:**

- `research-schema-rule.mdc`
  - Research schema structure
  - Schema versioning
  - Schema validation
  - Schema migration

- `research-report-generation-rule.mdc`
  - Report structure
  - Markdown formatting
  - Section organization
  - Report templates

- `research-data-validation-rule.mdc`
  - Data validation patterns
  - Data quality checks
  - Data completeness
  - Data accuracy

- `research-quality-scoring-rule.mdc`
  - Quality metrics
  - Scoring algorithms
  - Threshold definitions
  - Quality reporting

**Prompts to Create:**

- `.cursor/prompts/research/`
  - `create-research-schema.prompt.md` - Create research schema
  - `generate-report.prompt.md` - Generate research report
  - `validate-research-data.prompt.md` - Validate research data
  - `calculate-quality-score.prompt.md` - Calculate quality score

---

## Tooling Recommendations

### 1. Cursor Rules Configuration

Create `.cursorrules` file in project root:

```markdown
# Company Researcher - Cursor Rules

## Project Context
This is a LangGraph-based multi-agent research system for company intelligence.

## Key Technologies
- Python 3.11+
- LangGraph for workflow orchestration
- LangChain for LLM abstractions
- Pydantic for data validation
- FastAPI for API layer
- pytest for testing

## Code Style
- Follow PEP 8
- Use type hints everywhere
- Prefer async/await for I/O operations
- Use Pydantic models for data structures
- Write tests for all new code (85%+ coverage)

## Agent Development
- Each agent should have a single responsibility
- Agents should be testable in isolation
- Use LangGraph state for agent communication
- Track costs and quality metrics

## Testing
- All tests in `tests/` directory
- Use pytest fixtures for setup
- Mock external APIs
- Target 85%+ coverage

## Documentation
- Docstrings for all public functions
- Type hints required
- Update README.md for user-facing changes
```

### 2. Cursor ignore + indexing ignore (must-have)

Cursor supports two repo-level ignore files (created in this repo):

- `.cursorignore` - blocks AI access *and* indexing (use for secrets)
- `.cursorindexingignore` - blocks indexing/search only (use for large generated folders like `outputs/`)

These are critical for keeping search fast and preventing accidental exposure of sensitive data.

### 3. Cursor Agent CLI permissions (optional)

If you use the Cursor CLI/Agent runner, project permissions can be configured via:

- `.cursor/cli.json`

This repo includes a minimal, safe starter file.

### 4. Prompt Registry collections (optional but recommended)

If you want `/` slash commands in Cursor chat, use Prompt Registry and `.collection.yml` manifests (this repo already has many under `.cursor/prompts/collections/`).

Collection manifests in this repo use the expected schema:

```yaml
id: example-bundle
name: "Example Bundle"
description: "What this bundle is for"
tags:
  - example
version: 1.0.0
owner: team-prompts
items:
  - path: prompts/cicd/implement-tag-based-cicd.prompt.md
    kind: prompt
```

The prompt files now live under `.cursor/prompts/prompts/` to match the `path:` convention above.

### 5. MCP servers (optional)

Cursor can load MCP servers from `.cursor/mcp.json`. This repo includes:

- `.cursor/mcp.template.json` (copy to `.cursor/mcp.json` locally)
- `.cursor/MCP_SETUP.md` (step-by-step)

---

## Integration with .claude

### Synergy Opportunities

1. **Cost Tracking**
   - `.claude` has `/cost` command
   - `.cursor` should have rules for agent cost tracking
   - Integrate: Use `.claude` command, enforce via `.cursor` rules

2. **Testing**
   - `.claude` has `/run-tests` command
   - `.cursor` should have pytest rules
   - Integrate: Use `.claude` command, follow `.cursor` test patterns

3. **Documentation**
   - Both have documentation rules
   - Align: Use `.cursor` rules for structure, `.claude` for generation

4. **Code Quality**
   - `.claude` has code quality skills
   - `.cursor` has code quality rules
   - Integrate: Use `.claude` skills, enforce `.cursor` standards

---

## Priority Implementation Order

### Phase 1: Core Python (Week 1)
1. Python type hints rule
2. Python async patterns rule
3. Python import organization rule
4. Python exception handling rule

### Phase 2: LangGraph (Week 2)
1. LangGraph workflow rule
2. LangGraph state management rule
3. LangGraph node patterns rule
4. LangGraph tool integration rule

### Phase 3: Testing & API (Week 3)
1. Pytest test structure rule
2. Pytest fixtures rule
3. Pytest async testing rule
4. FastAPI route definition rule

### Phase 4: Agents & Research (Week 4)
1. Agent design patterns rule
2. Agent cost tracking rule
3. Agent quality assurance rule
4. Research schema rule

---

## Example Rule Template

Here's a template for creating new rules:

```markdown
---
id: rule.python.type-hints.v1
name: Python Type Hints
version: 1.0.0
description: Enforce type hints for all Python functions
globs: ["**/*.py"]
governs: ["**/*.py"]
alwaysApply: false
requires: []
---

# Python Type Hints Rule

## Purpose
Ensure all Python functions have proper type hints for better code clarity and IDE support.

## Standards

### Function Signatures
- All functions MUST have type hints for parameters
- All functions MUST have return type annotations
- Use `-> None` for functions that don't return values
- Use `Optional[T]` for nullable types
- Use `Union[T1, T2]` for multiple types

### Examples

**Good:**
```python
def calculate_total(items: List[float], tax_rate: float) -> float:
    """Calculate total with tax."""
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

**Bad:**
```python
def calculate_total(items, tax_rate):
    """Calculate total with tax."""
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

## Validation Checklist
- [ ] All function parameters have type hints
- [ ] All functions have return type annotations
- [ ] Complex types use `typing` module appropriately
- [ ] Type hints are accurate and specific
- [ ] No `Any` types without justification
```

---

## Next Steps

1. **Review this analysis** with your team
2. **Prioritize** which rules to implement first
3. **Create** the first rule using the template above
4. **Test** the rule with real code
5. **Iterate** based on feedback
6. **Document** usage patterns

---

## Questions?

- How do rules interact with `.claude` commands?
- Should rules be project-specific or reusable?
- How do we version rules?
- How do we test rules?

See `.cursor/rules/rule-authoring/` for guidance on creating rules.

---

**Last Updated**: 2025-12-12
**Status**: Analysis Complete - Ready for Implementation
