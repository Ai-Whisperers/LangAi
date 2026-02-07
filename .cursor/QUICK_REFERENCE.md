# Cursor Configuration Quick Reference

**Quick guide to what should be in `.cursor` for this Python/LangGraph project**

---

## 🎯 What You Need

### 1. Root Configuration

**`.cursorrules`** (project root)
- Project context
- Tech stack overview
- Code style guidelines
- Testing requirements

**`.cursorignore`** (project root)
- Blocks AI access + indexing for secrets and private files

**`.cursorindexingignore`** (project root)
- Excludes large/noisy folders from indexing while keeping them readable when explicitly opened

**`.cursor/cli.json`** (optional)
- Project permissions for Cursor CLI/Agent runner (if you use it)

**`.cursor/mcp.template.json`** + `MCP_SETUP.md` (optional)
- Template and instructions for MCP server setup in Cursor

### 2. Rules Directory Structure

```
.cursor/rules/
├── python/              # Python-specific rules
│   ├── python-type-hints-rule.mdc
│   ├── python-async-patterns-rule.mdc
│   ├── python-import-organization-rule.mdc
│   ├── python-exception-handling-rule.mdc
│   ├── python-context-managers-rule.mdc
│   └── python-decorators-rule.mdc
│
├── langgraph/           # LangGraph workflow rules
│   ├── langgraph-workflow-rule.mdc
│   ├── langgraph-state-management-rule.mdc
│   ├── langgraph-node-patterns-rule.mdc
│   ├── langgraph-tool-integration-rule.mdc
│   └── langchain-prompt-templates-rule.mdc
│
├── pydantic/            # Pydantic model rules
│   ├── pydantic-model-definition-rule.mdc
│   ├── pydantic-validation-patterns-rule.mdc
│   └── pydantic-serialization-rule.mdc
│
├── testing/             # pytest rules
│   ├── pytest-test-structure-rule.mdc
│   ├── pytest-fixtures-rule.mdc
│   ├── pytest-async-testing-rule.mdc
│   ├── pytest-mocking-rule.mdc
│   └── pytest-coverage-rule.mdc
│
├── api/                 # FastAPI rules
│   ├── fastapi-route-definition-rule.mdc
│   ├── fastapi-dependency-injection-rule.mdc
│   ├── fastapi-error-handling-rule.mdc
│   └── fastapi-websocket-rule.mdc
│
├── agents/              # AI agent rules
│   ├── agent-design-patterns-rule.mdc
│   ├── agent-prompt-engineering-rule.mdc
│   ├── agent-cost-tracking-rule.mdc
│   ├── agent-quality-assurance-rule.mdc
│   └── agent-iteration-patterns-rule.mdc
│
└── research/            # Research workflow rules
    ├── research-schema-rule.mdc
    ├── research-report-generation-rule.mdc
    ├── research-data-validation-rule.mdc
    └── research-quality-scoring-rule.mdc
```

### 3. Prompts Directory Structure

```
.cursor/prompts/
├── collections/           # Prompt Registry bundles (*.collection.yml)
├── exemplars/             # Prompt exemplars (not installed as slash commands)
├── templars/              # Prompt templars (authoring helpers)
└── prompts/               # Prompt files (*.prompt.md)
    ├── python/
    ├── langgraph/
    ├── pydantic/
    ├── testing/
    ├── api/
    ├── agents/
    └── research/
```

### 4. Collections

```
.cursor/prompts/collections/
├── python.collection.yml
├── langgraph.collection.yml
├── pydantic.collection.yml
├── testing.collection.yml
├── api.collection.yml
├── agents.collection.yml
└── research.collection.yml
```

### 5. Exemplars

```
.cursor/exemplars/
├── python/
│   ├── type-hints-good.md
│   ├── type-hints-bad.md
│   ├── async-good.md
│   └── async-bad.md
│
├── langgraph/
│   ├── workflow-good.md
│   ├── workflow-bad.md
│   ├── node-good.md
│   └── node-bad.md
│
├── pydantic/
│   ├── model-good.md
│   └── model-bad.md
│
├── testing/
│   ├── test-good.md
│   ├── test-bad.md
│   └── fixture-good.md
│
└── agents/
    ├── agent-good.md
    ├── agent-bad.md
    └── prompt-good.md
```

### 6. Templars

```
.cursor/templars/
├── python/
│   ├── function-template.md
│   ├── class-template.md
│   └── async-function-template.md
│
├── langgraph/
│   ├── workflow-template.md
│   ├── node-template.md
│   └── state-template.md
│
├── pydantic/
│   ├── model-template.md
│   └── validator-template.md
│
├── testing/
│   ├── test-template.md
│   └── fixture-template.md
│
├── agents/
│   ├── agent-template.md
│   └── prompt-template.md
│
└── research/
    ├── schema-template.md
    └── report-template.md
```

---

## 🛠️ Tooling Recommendations

### 1. Cursor Rules Engine

**Purpose**: Enforce coding standards automatically

**Key Features**:
- File-pattern matching (globs)
- Automatic rule activation
- Validation checklists
- Cross-rule references

**Usage**:
- Rules activate based on file patterns
- Agent-application rules trigger on keywords
- Always-apply rules run on everything

### 2. Prompt System

**Purpose**: Provide reusable workflows for common tasks

**Key Features**:
- Step-by-step instructions
- Rule references
- Examples and context
- Collections for organization

**Usage**:
- Reference prompts: `@.cursor/prompts/python/add-type-hints.prompt.md`
- Use collections: `@.cursor/prompts/collections/python.collection.yml`
- Create new prompts following template

### 3. Exemplars

**Purpose**: Show good/bad patterns for learning

**Key Features**:
- Clear good/bad contrasts
- Real-world examples
- Pattern explanations
- Marked as `use: critic-only`

**Usage**:
- Reference in rules
- Show to AI for pattern learning
- Never copy directly to output

### 4. Templars

**Purpose**: Provide starting points for new code

**Key Features**:
- Minimal but complete
- Variable placeholders
- Structure templates
- Domain-specific

**Usage**:
- Reference in prompts
- Use as starting point
- Customize for specific needs

---

## 📋 Integration with .claude

### Synergy Points

1. **Cost Tracking**
   - `.claude`: `/cost` command
   - `.cursor`: Agent cost tracking rules
   - **Integration**: Use command, enforce via rules

2. **Testing**
   - `.claude`: `/run-tests` command
   - `.cursor`: Pytest rules
   - **Integration**: Use command, follow rules

3. **Code Quality**
   - `.claude`: Code quality skills
   - `.cursor`: Code quality rules
   - **Integration**: Use skills, enforce standards

4. **Documentation**
   - `.claude`: Documentation generation
   - `.cursor`: Documentation structure rules
   - **Integration**: Generate with `.claude`, structure with `.cursor`

---

## 🚀 Quick Start

### Step 1: Create Root Configuration

Create `.cursorrules` in project root:

```markdown
# Company Researcher - Cursor Rules

## Project Context
LangGraph-based multi-agent research system for company intelligence.

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
- Prefer async/await for I/O
- Use Pydantic models for data
- Write tests (85%+ coverage)

## Agent Development
- Single responsibility per agent
- Testable in isolation
- Use LangGraph state for communication
- Track costs and quality metrics
```

### Step 2: Create First Rule

Create `.cursor/rules/python/python-type-hints-rule.mdc`:

```markdown
---
id: rule.python.type-hints.v1
name: Python Type Hints
version: 1.0.0
description: Enforce type hints for all Python functions
globs: ["**/*.py"]
governs: ["**/*.py"]
alwaysApply: false
---

# Python Type Hints Rule

## Purpose
Ensure all Python functions have proper type hints.

## Standards
- All functions MUST have type hints for parameters
- All functions MUST have return type annotations
- Use `Optional[T]` for nullable types
- Use `Union[T1, T2]` for multiple types

## Examples
[Good/bad examples here]

## Validation Checklist
- [ ] All function parameters have type hints
- [ ] All functions have return type annotations
- [ ] Complex types use `typing` module appropriately
```

### Step 3: Create First Prompt

Create `.cursor/prompts/python/add-type-hints.prompt.md`:

```markdown
# Add Type Hints to Python Code

## Purpose
Add type hints to existing Python functions.

## Steps
1. Identify functions without type hints
2. Add parameter type hints
3. Add return type annotations
4. Use `typing` module for complex types
5. Verify with mypy

## Rules Applied
- `rule.python.type-hints.v1`

## Example
[Example here]
```

### Step 4: Update Rule Index

Add to `.cursor/rules/rule-index.yml`:

```yaml
rules:
  rule.python.type-hints.v1: python/python-type-hints-rule.mdc
```

---

## 📊 Summary

### What You Have
- ✅ Comprehensive rules framework
- ✅ Prompts system
- ✅ Templars and exemplars
- ✅ Rule authoring framework

### What You Need
- ❌ Python-specific rules (6 rules)
- ❌ LangGraph rules (5 rules)
- ❌ Pydantic rules (3 rules)
- ❌ Testing rules (5 rules)
- ❌ API rules (4 rules)
- ❌ Agent rules (5 rules)
- ❌ Research rules (4 rules)
- ❌ Root `.cursorrules` file
- ❌ Settings configuration

### Total Items Needed
- **32 rules**
- **26 prompts**
- **7 collections**
- **~15 exemplars**
- **~15 templars**
- **3 configuration files**

---

## 📚 Documentation

- **Full Analysis**: `.cursor/COMPLETION_ANALYSIS.md`
- **Implementation Checklist**: `.cursor/IMPLEMENTATION_CHECKLIST.md`
- **Rule Authoring Guide**: `.cursor/rules/rule-authoring/`
- **Main README**: `.cursor/README.md`

---

## 🎯 Next Steps

1. **Review** `.cursor/COMPLETION_ANALYSIS.md`
2. **Prioritize** using `.cursor/IMPLEMENTATION_CHECKLIST.md`
3. **Create** `.cursorrules` file
4. **Implement** Phase 1 rules (Python + Testing)
5. **Test** with real code
6. **Iterate** based on feedback

---

**Last Updated**: 2025-12-12
**Status**: Ready for Implementation
