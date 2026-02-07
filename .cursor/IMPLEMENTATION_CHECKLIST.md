# Cursor Configuration Implementation Checklist

**Project**: Company Researcher
**Date**: 2025-12-12
**Status**: Planning Phase

---

## Overview

This checklist provides a complete list of all rules, prompts, templars, and configurations needed to make `.cursor` complete for this Python/LangGraph project.

---

## 📋 Complete Item List

### 1. Python Development Rules

#### Rules to Create

- [ ] `.cursor/rules/python/python-type-hints-rule.mdc`
  - Enforce type hints for all functions
  - Handle `Optional`, `Union`, `Dict`, `List`
  - Async function typing
  - Type checking with mypy

- [ ] `.cursor/rules/python/python-async-patterns-rule.mdc`
  - Async/await best practices
  - Context managers for async resources
  - Exception handling in async code
  - `asyncio.gather()` vs sequential patterns

- [ ] `.cursor/rules/python/python-import-organization-rule.mdc`
  - Import order (stdlib, third-party, local)
  - Absolute vs relative imports
  - `__all__` declarations
  - Circular dependency prevention

- [ ] `.cursor/rules/python/python-exception-handling-rule.mdc`
  - Specific exception types
  - Exception chaining (`raise from`)
  - Logging exceptions
  - Custom exception classes

- [ ] `.cursor/rules/python/python-context-managers-rule.mdc`
  - When to use context managers
  - `@contextmanager` decorator
  - Resource cleanup patterns

- [ ] `.cursor/rules/python/python-decorators-rule.mdc`
  - Decorator patterns
  - `functools.wraps`
  - Parameterized decorators

#### Prompts to Create

- [ ] `.cursor/prompts/python/add-type-hints.prompt.md`
  - Add type hints to existing code
  - Handle complex types
  - Update function signatures

- [ ] `.cursor/prompts/python/refactor-to-async.prompt.md`
  - Convert sync to async
  - Update callers
  - Handle async context

- [ ] `.cursor/prompts/python/fix-imports.prompt.md`
  - Organize imports
  - Fix circular dependencies
  - Add `__all__` declarations

- [ ] `.cursor/prompts/python/create-exception-class.prompt.md`
  - Create custom exception
  - Add error codes
  - Document exception usage

#### Collection

- [ ] `.cursor/prompts/collections/python.collection.yml`
  - Group all Python prompts

---

### 2. LangGraph/LangChain Rules

#### Rules to Create

- [ ] `.cursor/rules/langgraph/langgraph-workflow-rule.mdc`
  - State schema definition
  - Node function structure
  - Edge conditions
  - Compilation patterns
  - Error handling in workflows

- [ ] `.cursor/rules/langgraph/langgraph-state-management-rule.mdc`
  - State schema design
  - State updates (additive vs replacement)
  - State validation
  - State persistence

- [ ] `.cursor/rules/langgraph/langgraph-node-patterns-rule.mdc`
  - Node function signatures
  - Return value patterns
  - Error handling in nodes
  - Logging and observability

- [ ] `.cursor/rules/langgraph/langgraph-tool-integration-rule.mdc`
  - Tool binding patterns
  - Tool error handling
  - Tool result processing
  - Tool validation

- [ ] `.cursor/rules/langgraph/langchain-prompt-templates-rule.mdc`
  - Prompt template structure
  - Variable substitution
  - Prompt versioning
  - Prompt testing

#### Prompts to Create

- [ ] `.cursor/prompts/langgraph/create-workflow.prompt.md`
  - Create new LangGraph workflow
  - Define state schema
  - Add initial nodes

- [ ] `.cursor/prompts/langgraph/add-node.prompt.md`
  - Add node to workflow
  - Define node function
  - Add edges

- [ ] `.cursor/prompts/langgraph/debug-workflow.prompt.md`
  - Debug workflow issues
  - Trace execution
  - Fix state issues

- [ ] `.cursor/prompts/langgraph/optimize-workflow.prompt.md`
  - Optimize workflow performance
  - Reduce costs
  - Improve quality

#### Collection

- [ ] `.cursor/prompts/collections/langgraph.collection.yml`
  - Group all LangGraph prompts

---

### 3. Pydantic Model Rules

#### Rules to Create

- [ ] `.cursor/rules/pydantic/pydantic-model-definition-rule.mdc`
  - Model structure
  - Field definitions
  - Validators and validators
  - Model configuration
  - Nested models

- [ ] `.cursor/rules/pydantic/pydantic-validation-patterns-rule.mdc`
  - Field validators
  - Model validators
  - Custom validators
  - Validation error handling

- [ ] `.cursor/rules/pydantic/pydantic-serialization-rule.mdc`
  - `model_dump()` vs `dict()`
  - JSON serialization
  - Excluding fields
  - Custom serializers

#### Prompts to Create

- [ ] `.cursor/prompts/pydantic/create-model.prompt.md`
  - Create new Pydantic model
  - Define fields
  - Add validators

- [ ] `.cursor/prompts/pydantic/add-validation.prompt.md`
  - Add validation to model
  - Create custom validators
  - Handle validation errors

- [ ] `.cursor/prompts/pydantic/migrate-model.prompt.md`
  - Migrate model version
  - Handle breaking changes
  - Update consumers

#### Collection

- [ ] `.cursor/prompts/collections/pydantic.collection.yml`
  - Group all Pydantic prompts

---

### 4. Testing Rules (pytest)

#### Rules to Create

- [ ] `.cursor/rules/testing/pytest-test-structure-rule.mdc`
  - Test file organization
  - Test class vs function structure
  - Test naming conventions
  - Test markers

- [ ] `.cursor/rules/testing/pytest-fixtures-rule.mdc`
  - Fixture organization
  - Scope management
  - Parametrized fixtures
  - Fixture dependencies

- [ ] `.cursor/rules/testing/pytest-async-testing-rule.mdc`
  - Async test patterns
  - `pytest-asyncio` usage
  - Async fixtures
  - Async mocking

- [ ] `.cursor/rules/testing/pytest-mocking-rule.mdc`
  - `unittest.mock` patterns
  - `pytest-mock` usage
  - Mocking external APIs
  - Mocking LangGraph workflows

- [ ] `.cursor/rules/testing/pytest-coverage-rule.mdc`
  - Coverage targets (85%+)
  - Coverage exclusions
  - Coverage reporting

#### Prompts to Create

- [ ] `.cursor/prompts/testing/generate-tests.prompt.md`
  - Generate tests for code
  - Create test structure
  - Add test cases

- [ ] `.cursor/prompts/testing/add-fixture.prompt.md`
  - Create new fixture
  - Define fixture scope
  - Add fixture dependencies

- [ ] `.cursor/prompts/testing/mock-external-api.prompt.md`
  - Mock external API calls
  - Create mock responses
  - Handle edge cases

- [ ] `.cursor/prompts/testing/check-coverage.prompt.md`
  - Analyze test coverage
  - Identify gaps
  - Generate coverage report

#### Collection

- [ ] `.cursor/prompts/collections/testing.collection.yml`
  - Group all testing prompts

---

### 5. FastAPI Rules

#### Rules to Create

- [ ] `.cursor/rules/api/fastapi-route-definition-rule.mdc`
  - Route decorators
  - Path parameters
  - Query parameters
  - Request body models
  - Response models

- [ ] `.cursor/rules/api/fastapi-dependency-injection-rule.mdc`
  - Dependency patterns
  - Shared dependencies
  - Database dependencies
  - Authentication dependencies

- [ ] `.cursor/rules/api/fastapi-error-handling-rule.mdc`
  - Exception handlers
  - HTTP exception patterns
  - Error response models
  - Validation error handling

- [ ] `.cursor/rules/api/fastapi-websocket-rule.mdc`
  - WebSocket patterns
  - Streaming responses
  - Connection management

#### Prompts to Create

- [ ] `.cursor/prompts/api/create-endpoint.prompt.md`
  - Create new API endpoint
  - Define route
  - Add request/response models

- [ ] `.cursor/prompts/api/add-authentication.prompt.md`
  - Add auth to endpoint
  - Create auth dependencies
  - Handle auth errors

- [ ] `.cursor/prompts/api/create-websocket.prompt.md`
  - Create WebSocket endpoint
  - Handle connections
  - Stream data

#### Collection

- [ ] `.cursor/prompts/collections/api.collection.yml`
  - Group all API prompts

---

### 6. AI Agent Rules

#### Rules to Create

- [ ] `.cursor/rules/agents/agent-design-patterns-rule.mdc`
  - Agent responsibilities
  - Agent communication
  - Agent state management
  - Agent error handling

- [ ] `.cursor/rules/agents/agent-prompt-engineering-rule.mdc`
  - Prompt structure for agents
  - System prompts
  - Few-shot examples
  - Prompt versioning

- [ ] `.cursor/rules/agents/agent-cost-tracking-rule.mdc`
  - Token counting
  - Cost calculation
  - Cost optimization
  - Cost reporting

- [ ] `.cursor/rules/agents/agent-quality-assurance-rule.mdc`
  - Quality scoring
  - Quality thresholds
  - Iteration patterns
  - Quality metrics

- [ ] `.cursor/rules/agents/agent-iteration-patterns-rule.mdc`
  - When to iterate
  - Iteration limits
  - Quality improvement strategies
  - Cost vs quality tradeoffs

#### Prompts to Create

- [ ] `.cursor/prompts/agents/create-agent.prompt.md`
  - Create new agent
  - Define agent responsibilities
  - Add agent to workflow

- [ ] `.cursor/prompts/agents/optimize-agent-cost.prompt.md`
  - Optimize agent costs
  - Reduce token usage
  - Improve efficiency

- [ ] `.cursor/prompts/agents/improve-agent-quality.prompt.md`
  - Improve agent quality
  - Enhance prompts
  - Add validation

- [ ] `.cursor/prompts/agents/debug-agent.prompt.md`
  - Debug agent issues
  - Trace execution
  - Fix errors

#### Collection

- [ ] `.cursor/prompts/collections/agents.collection.yml`
  - Group all agent prompts

---

### 7. Research Workflow Rules

#### Rules to Create

- [ ] `.cursor/rules/research/research-schema-rule.mdc`
  - Research schema structure
  - Schema versioning
  - Schema validation
  - Schema migration

- [ ] `.cursor/rules/research/research-report-generation-rule.mdc`
  - Report structure
  - Markdown formatting
  - Section organization
  - Report templates

- [ ] `.cursor/rules/research/research-data-validation-rule.mdc`
  - Data validation patterns
  - Data quality checks
  - Data completeness
  - Data accuracy

- [ ] `.cursor/rules/research/research-quality-scoring-rule.mdc`
  - Quality metrics
  - Scoring algorithms
  - Threshold definitions
  - Quality reporting

#### Prompts to Create

- [ ] `.cursor/prompts/research/create-research-schema.prompt.md`
  - Create research schema
  - Define structure
  - Add validation

- [ ] `.cursor/prompts/research/generate-report.prompt.md`
  - Generate research report
  - Format markdown
  - Organize sections

- [ ] `.cursor/prompts/research/validate-research-data.prompt.md`
  - Validate research data
  - Check completeness
  - Verify accuracy

- [ ] `.cursor/prompts/research/calculate-quality-score.prompt.md`
  - Calculate quality score
  - Apply metrics
  - Generate report

#### Collection

- [ ] `.cursor/prompts/collections/research.collection.yml`
  - Group all research prompts

---

### 8. Configuration Files

#### Root Configuration

- [ ] `.cursorrules` (project root)
  - Project context
  - Key technologies
  - Code style
  - Agent development guidelines
  - Testing requirements

- [ ] `.cursorignore` (project root)
  - Block AI access to secrets (e.g., `.env`, credentials files)

- [ ] `.cursorindexingignore` (project root)
  - Exclude large generated folders (e.g., `outputs/`, `logs/`) from indexing/search

- [ ] `.cursor/cli.json` (optional)
  - Project-level permissions for Cursor CLI/Agent runner (if you use it)

- [ ] `.cursor/mcp.json` (optional, local-only recommended)
  - MCP server configuration for Cursor (copy from `.cursor/mcp.template.json`)

#### Rule Index Updates

- [ ] Update `.cursor/rules/rule-index.yml`
  - Add Python rules
  - Add LangGraph rules
  - Add Pydantic rules
  - Add Testing rules
  - Add API rules
  - Add Agent rules
  - Add Research rules

---

### 9. Exemplars

#### Python Exemplars

- [ ] `.cursor/exemplars/python/type-hints-good.md`
- [ ] `.cursor/exemplars/python/type-hints-bad.md`
- [ ] `.cursor/exemplars/python/async-good.md`
- [ ] `.cursor/exemplars/python/async-bad.md`

#### LangGraph Exemplars

- [ ] `.cursor/exemplars/langgraph/workflow-good.md`
- [ ] `.cursor/exemplars/langgraph/workflow-bad.md`
- [ ] `.cursor/exemplars/langgraph/node-good.md`
- [ ] `.cursor/exemplars/langgraph/node-bad.md`

#### Pydantic Exemplars

- [ ] `.cursor/exemplars/pydantic/model-good.md`
- [ ] `.cursor/exemplars/pydantic/model-bad.md`

#### Testing Exemplars

- [ ] `.cursor/exemplars/testing/test-good.md`
- [ ] `.cursor/exemplars/testing/test-bad.md`
- [ ] `.cursor/exemplars/testing/fixture-good.md`

#### Agent Exemplars

- [ ] `.cursor/exemplars/agents/agent-good.md`
- [ ] `.cursor/exemplars/agents/agent-bad.md`
- [ ] `.cursor/exemplars/agents/prompt-good.md`

---

### 10. Templars

#### Python Templars

- [ ] `.cursor/templars/python/function-template.md`
- [ ] `.cursor/templars/python/class-template.md`
- [ ] `.cursor/templars/python/async-function-template.md`

#### LangGraph Templars

- [ ] `.cursor/templars/langgraph/workflow-template.md`
- [ ] `.cursor/templars/langgraph/node-template.md`
- [ ] `.cursor/templars/langgraph/state-template.md`

#### Pydantic Templars

- [ ] `.cursor/templars/pydantic/model-template.md`
- [ ] `.cursor/templars/pydantic/validator-template.md`

#### Testing Templars

- [ ] `.cursor/templars/testing/test-template.md`
- [ ] `.cursor/templars/testing/fixture-template.md`

#### Agent Templars

- [ ] `.cursor/templars/agents/agent-template.md`
- [ ] `.cursor/templars/agents/prompt-template.md`

#### Research Templars

- [ ] `.cursor/templars/research/schema-template.md`
- [ ] `.cursor/templars/research/report-template.md`

---

## 📊 Summary Statistics

### Rules
- **Python**: 6 rules
- **LangGraph**: 5 rules
- **Pydantic**: 3 rules
- **Testing**: 5 rules
- **API**: 4 rules
- **Agents**: 5 rules
- **Research**: 4 rules
- **Total**: 32 rules

### Prompts
- **Python**: 4 prompts
- **LangGraph**: 4 prompts
- **Pydantic**: 3 prompts
- **Testing**: 4 prompts
- **API**: 3 prompts
- **Agents**: 4 prompts
- **Research**: 4 prompts
- **Total**: 26 prompts

### Collections
- **Total**: 7 collections

### Exemplars
- **Total**: ~15 exemplars

### Templars
- **Total**: ~15 templars

### Configuration Files
- **Total**: 3 files

---

## 🎯 Implementation Priority

### Phase 1: Foundation (Week 1)
1. `.cursorrules` file
2. Python type hints rule
3. Python async patterns rule
4. Pytest test structure rule
5. Basic exemplars

### Phase 2: Core Framework (Week 2)
1. LangGraph workflow rule
2. LangGraph state management rule
3. Pydantic model definition rule
4. Agent design patterns rule
5. Basic prompts

### Phase 3: Advanced Patterns (Week 3)
1. Remaining Python rules
2. Remaining LangGraph rules
3. Testing rules
4. API rules
5. Research rules

### Phase 4: Polish (Week 4)
1. All prompts
2. All exemplars
3. All templars
4. Collections
5. Documentation

---

## ✅ Completion Criteria

- [ ] All rules created and tested
- [ ] All prompts created and validated
- [ ] All collections organized
- [ ] Exemplars demonstrate good/bad patterns
- [ ] Templars provide starting points
- [ ] Configuration files complete
- [ ] Rule index updated
- [ ] Documentation updated

---

## 📝 Notes

- Rules should follow the structure defined in `.cursor/rules/rule-authoring/`
- Prompts should reference relevant rules
- Exemplars should show clear good/bad contrasts
- Templars should be minimal but complete
- Collections should group related prompts

---

**Last Updated**: 2025-12-12
**Next Review**: After Phase 1 completion
