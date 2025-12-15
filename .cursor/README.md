# Cursor Rules & Prompts System

## Overview

This directory contains a systematic framework for AI-assisted development, combining **rules** (how to work) with **prompts** (what to do). The system enables consistent, high-quality outputs across complex development workflows while maintaining traceability and automation.

## 🏆 Gold Standard Reference

This repository (`eneve.domain`) serves as the **Gold Standard Reference Implementation** (60/60 score). It demonstrates the complete, working integration of:
- Build Infrastructure (CPM, Shared Props)
- CI/CD Pipelines (Automated Publishing, Quality Gates)
- Documentation Architecture
- Ticket Management System
- AI Rules Framework

Use the **Bootstrap New Repository** prompt (`prompts/setup/bootstrap-new-repo.md`) to apply this standard to new projects.

## How Rules and Prompts Work Together

### The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REQUEST                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │  PROMPTS (What to Do)  │
          │  - Task templates      │
          │  - Workflows           │
          │  - Examples            │
          └────────┬───────────────┘
                   │ Invokes
                   ▼
          ┌────────────────────────┐
          │   RULES (How to Do)    │
          │  - Standards           │
          │  - Validations         │
          │  - Constraints         │
          └────────┬───────────────┘
                   │ Uses
                   ▼
          ┌────────────────────────┐
          │ TEMPLARS & EXEMPLARS   │
          │  - Output structures   │
          │  - Pattern examples    │
          └────────┬───────────────┘
                   │
                   ▼
          ┌────────────────────────┐
          │    OUTPUT/ACTION       │
          │  - Files created       │
          │  - Code modified       │
          │  - Documentation       │
          └────────────────────────┘
```

### The Relationship

**PROMPTS** are user-facing workflows that:
- Define specific tasks ("Create a user story", "Validate documentation", "Start a ticket")
- Provide step-by-step instructions for common operations
- Reference which rules apply to the task
- Include examples and context

**RULES** are system-level constraints that:
- Define standards and patterns (how code should be written, how files should be structured)
- Provide validation criteria (what makes output correct)
- Enforce consistency across all operations
- Are automatically invoked based on file patterns or agent decisions

**Together they enable**:
- **Prompts** tell you *what task* to perform
- **Rules** ensure you perform it *correctly and consistently*
- **Prompts** guide the workflow
- **Rules** enforce quality and standards

### Example: Creating a User Story

1. **User says**: "Create a user story for OAuth login"

2. **Prompt activates**: `prompts/agile/create-user-story.md`
   - Provides workflow steps
   - Asks relevant questions
   - References required format

3. **Rules auto-apply**:
   - `rules/agile/user-story-documentation-rule.mdc` → Enforces story structure
   - `rules/clean-code.mdc` → Ensures clarity
   - `rules/no-apologies-rule.mdc` → Keeps responses professional

4. **Output produced**: Well-structured user story following all standards

## Directory Structure

```
.cursor/
├── rules/              # How to do things (standards, validations)
│   ├── agile/         # Agile documentation standards
│   ├── database-standards/  # SQL and database rules
│   ├── documentation/ # XML documentation standards
│   ├── git/           # Branching strategy and workflow
│   ├── migration/     # C++ to C# migration framework
│   ├── prompts/       # Rules for prompt creation
│   ├── rule-authoring/# Meta-rules for creating rules
│   ├── technical-specifications/  # Spec documentation
│   ├── ticket/        # Ticket workflow management
│   └── [general rules]# Code quality, naming, DRY, etc.
│
├── prompts/           # What to do (task workflows)
│   ├── agile/         # Agile task workflows
│   ├── cicd/          # CI/CD setup and validation
│   ├── code-quality/  # Code review and refactoring
│   ├── database-standards/  # Database task workflows
│   ├── documentation/ # Documentation generation
│   ├── git/           # Git operations
│   ├── migration/     # Migration task workflows
│   ├── rule-authoring/# Rule creation and sync
│   ├── technical-specifications/  # Spec creation
│   ├── ticket/        # Ticket management workflows
│   └── unit-testing/  # Test generation and validation
│
├── templars/          # Output structure templates
│   └── [domain]/      # Templates by domain
│
└── exemplars/         # Pattern examples (read-only)
    └── [domain]/      # Examples by domain
```

## Rule Categories & How They Work Together

### 1. **Core Development Rules** (Foundation Layer)
*Location*: Root of `rules/`

**Purpose**: Universal standards that apply to all code and documentation

**Key Rules**:
- `clean-code.mdc` → Write readable, maintainable code
- `code-quality-and-best-practices.mdc` → Quality standards and paradigms
- `dry-principle.mdc` → Avoid code duplication
- `naming-conventions.mdc` → Use meaningful names
- `verify-information-rule.mdc` → Don't make assumptions

**How they work together**:
- These are **always-active** behavioral rules
- Applied automatically to all AI responses
- Form the foundation that domain-specific rules build upon
- Ensure consistency regardless of what domain you're working in

**Example**: When creating any file (ticket, spec, code), `naming-conventions.mdc` ensures names are clear, while `clean-code.mdc` ensures structure is readable.

---

### 2. **Rule Authoring Framework** (Meta Layer)
*Location*: `rules/rule-authoring/`

**Purpose**: Rules for creating and maintaining rules themselves

**Key Components**:
- **Extraction**: Create rules from real work (`rule-extraction-from-practice.mdc`)
- **Structure**: Define rule format (`rule-file-structure.mdc`)
- **Invocation**: Control when rules trigger (`rule-invocation-strategies.mdc`)
- **Versioning**: Track changes (`rule-provenance-and-versioning.mdc`)
- **Validation**: Ensure correctness (`rule-validation-and-checklists.mdc`)

**How they work together**:
1. **Extract** patterns from conversations/work
2. **Structure** them using canonical format
3. Define **invocation** strategy (file-mask or agentic)
4. Add **versioning** and provenance
5. Create **validation** checklist

**Special**: This is the "self-aware" layer—rules that define how to make rules.

**Prompts connection**:
- `prompts/rule-authoring/` provides workflows for using these meta-rules
- E.g., "Extract prompts from conversation" or "Sync rules between repos"

---

### 3. **Agile Documentation** (Business Layer)
*Location*: `rules/agile/` and `prompts/agile/`

**Purpose**: Structure business requirements and user stories

**Key Rules**:
- `epic-documentation-rule.mdc` → Large initiatives
- `business-feature-documentation-rule.mdc` → Features
- `user-story-documentation-rule.mdc` → User stories
- `story-splitting-rule.mdc` → When to split stories

**How they work together**:
- **Epic** → contains multiple **Features**
- **Features** → contain multiple **User Stories**
- **Stories** can be **split** if too large
- All follow consistent documentation format
- `agent-application-rule.mdc` coordinates which rule applies when

**Prompts connection**:
- `create-user-story.md` → Guides story creation
- `split-user-story.md` → Guides story splitting
- Both invoke the relevant rules automatically

---

### 4. **Ticket Management** (Workflow Layer)
*Location*: `rules/ticket/` and `prompts/ticket/`

**Purpose**: Track development work with structured documentation

**Key Rules**:
- `plan-rule.mdc` → Define ticket objectives
- `context-rule.mdc` → Track current state
- `progress-rule.mdc` → Log actions chronologically
- `timeline-tracking-rule.mdc` → Estimate hours worked
- `validation-before-completion-rule.mdc` → Prevent premature "done"

**How they work together**:
1. **Start ticket** → Create `plan.md`, `context.md`, `progress.md`
2. **During work** → Update `context.md`, append to `progress.md`
3. **Track time** → Log sessions in `timeline.md`
4. **Before completion** → Validate all requirements met
5. **Close ticket** → Create `recap.md` with learnings

**Agent-application pattern**:
- `ticket/agent-application-rule.mdc` decides which ticket rule to apply
- Triggered by phrases like "start ticket", "update progress", "validate completion"

**Prompts connection**:
- `start-ticket.md` → Initializes ticket structure
- `update-progress.md` → Logs work
- `validate-completion.md` → Pre-completion checks

---

### 5. **Git Workflow** (Version Control Layer)
*Location*: `rules/git/` and `prompts/git/`

**Purpose**: Enforce branching strategy and commit standards

**Key Rules**:
- `branch-structure-rule.mdc` → Define branch types (main, develop, feature, fix, hotfix)
- `branch-naming-rule.mdc` → Enforce naming with Jira tickets
- `branch-lifecycle-rule.mdc` → Creation, merge, promotion workflows
- `branch-protection-rule.mdc` → CI/CD integration

**How they work together**:
- **Structure** defines branch types and purposes
- **Naming** enforces ticket traceability (`feature/EPP-123-description`)
- **Lifecycle** defines how branches flow (feature → develop → release → main)
- **Protection** prevents direct commits to protected branches

**Prompts connection**:
- `create-branch.md` → Guide branch creation with correct naming
- `prepare-commit.md` → Create proper commit messages

---

### 6. **Database Standards** (Data Layer)
*Location*: `rules/database-standards/`

**Purpose**: SQL coding standards and database migration management

**Key Rules**:
- `general-standards-rule.mdc` → Repository structure, version control
- `sql-coding-standards-rule.mdc` → SQL style and safety
- `mssql-standards-rule.mdc` → MSSQL-specific patterns
- `template-usage-rule.mdc` → SQL script templates
- `tracking-standards-rule.mdc` → Excel tracking sheets

**How they work together**:
- **General** provides foundation (folder structure, naming)
- **SQL coding** ensures style consistency
- **MSSQL** adds database-specific guidance
- **Templates** provide starting points
- **Tracking** maintains change log in Excel

**Prompts connection**:
- `create-migration-script.md` → Generate migration using templates
- `review-sql-script.md` → Validate against standards

---

### 7. **Documentation Standards** (Communication Layer)
*Location*: `rules/documentation/` and `prompts/documentation/`

**Purpose**: XML documentation for .NET code and API documentation

**Key Rules**:
- `documentation-standards-rule.mdc` → XML comment requirements
- `documentation-testing-rule.mdc` → Validation framework
- `unit-test-documentation-rule.mdc` → Test documentation

**How they work together**:
- **Standards** define what must be documented (classes, methods, parameters)
- **Testing** validates documentation completeness
- **Unit test docs** ensure tests are understandable

**Prompts connection**:
- `generate-missing-docs.md` → Add XML comments where missing
- `validate-documentation-quality.md` → Check completeness

---

### 8. **Technical Specifications** (Migration Layer)
*Location*: `rules/technical-specifications/` and `prompts/technical-specifications/`

**Purpose**: Document C++ systems for C# migration

**Key Rules**:
- `domain-overview-rule.mdc` → High-level architecture
- `domain-object-rule.mdc` → Entity documentation
- `enumeration-rule.mdc` → Enum documentation
- `business-rules-rule.mdc` → Business logic
- `entity-relationship-rule.mdc` → Database schema

**How they work together**:
- **Overview** provides navigation hub
- **Objects** document individual entities
- **Enumerations** capture exact values and meanings
- **Business rules** preserve logic
- **Relationships** map database structure

**Architecture patterns**:
- `documentation-architecture-rule.mdc` → 3-folder pattern (technical/implementation/rfcs)
- `specification-anti-duplication-rule.mdc` → Reference, don't duplicate

**Prompts connection**:
- `document-domain-object.md` → Create entity spec
- `document-enumeration.md` → Document enum type

---

### 9. **Migration Process** (Transformation Layer)
*Location*: `rules/migration/`

**Purpose**: Systematic C++ to C# migration framework

**Key Rules** (4 Phases):
- `migration-overview.mdc` → Framework overview
- `phase-1-data-collection.mdc` → Analyze C++ system
- `phase-2-specification-creation.mdc` → Create specs
- `phase-2b-specification-review.mdc` → Validate specs
- `phase-3-migration-planning.mdc` → Design C# implementation

**How they work together**:
1. **Overview** defines 4-phase process
2. **Phase 1** collects data from C++ codebase
3. **Phase 2** transforms data into specs (uses technical-specifications rules)
4. **Phase 2b** validates specs (multi-stakeholder review)
5. **Phase 3** plans C# implementation

**Integration**: Migration rules reference technical-specification rules for documentation format.

---

### 10. **Prompts Domain** (Task Orchestration)
*Location*: `rules/prompts/` and `prompts/rule-authoring/`

**Purpose**: Create and manage reusable prompt workflows

**Key Rules**:
- `prompt-creation-rule.mdc` → Structure for prompts
- `prompt-extraction-rule.mdc` → Extract prompts from conversations

**How they work together**:
- **Creation** defines prompt structure (like rule structure but for tasks)
- **Extraction** creates prompts from real work (like rule extraction)
- Prompts live in `prompts/` directory, organized by domain

**Meta-connection**: Just as `rule-authoring/` defines how to make rules, `prompts/` defines how to make task workflows.

---

### 11. **Unit Testing** (Quality Assurance Layer)
*Location*: `rules/unit-testing/` (if exists) and `prompts/unit-testing/`

**Purpose**: Ensure code quality through automated testing

**Prompts**:
- `check-test-coverage.md` → Analyze coverage gaps
- `generate-missing-tests.md` → Create tests for uncovered code
- `validate-test-quality.md` → Ensure tests follow standards

**Integration**: Works with documentation rules (tests need XML docs too)

---

## Rule Invocation: How Rules Activate

### Strategy 1: File-Mask Triggered (80% of rules)
**Pattern**: Rules activate based on file patterns

```yaml
globs: **/plan.md
governs: **/plan.md
alwaysApply: false
```

**When working on `tickets/EPP-123/plan.md`**:
- `ticket/plan-rule.mdc` auto-activates
- Enforces structure, validation
- No manual invocation needed

---

### Strategy 2: Description-Triggered Agentic (Agent-Application Rules)
**Pattern**: Rules activate based on semantic intent

```yaml
# NO globs/governs fields
description: "Agent guidance for when and how to apply ticket rules..."
```

**When user says**: "Start working on ticket EPP-123"
- `ticket/agent-application-rule.mdc` activates
- Reads user intent
- Invokes correct operational rule (`plan-rule.mdc`, `context-rule.mdc`, etc.)

**One per domain**: Each domain has ONE agent-application rule that coordinates others.

---

### Strategy 3: Always-Apply (Rare)
**Pattern**: Rules always active

```yaml
globs: **/*
governs: ""
alwaysApply: true
```

**Used for**: Universal validations (OPSEC, redaction)
- Applied to every file
- Read-only (never writes)
- Idempotent (safe to run repeatedly)

---

## Templars and Exemplars

### Templars (Output Structures)
*Location*: `templars/`

**Purpose**: Define structure of generated files (like templates)

**Example**: `templars/ticket/plan-template.md`
```markdown
# {{ticket_id}} Plan

## Objective
{{objective}}

## Acceptance Criteria
{{criteria}}
```

**Usage**: Rules reference templars to ensure consistent output structure

---

### Exemplars (Pattern Examples)
*Location*: `exemplars/`

**Purpose**: Show good/bad examples for learning (NEVER copied to output)

**Example**: `exemplars/ticket/plan-good.md` (real example for pattern learning)

**Critical**: Marked with `use: critic-only` to prevent content leakage

---

## How to Use This System

### As a Developer

1. **Use Prompts** to invoke common tasks:
   - Browse `prompts/` to find workflows
   - Example: "@.cursor/prompts/ticket/start-ticket.md EPP-123"

2. **Rules activate automatically**:
   - When you edit files matching `globs` patterns
   - When you use keywords matching agent-application rules
   - You don't need to manually invoke them

3. **Ask the AI to explain rules**:
   - "Explain the ticket workflow rules"
   - "What are the agile documentation standards?"
   - "Show me how the branch naming rules work"
   - "What rules apply when I create a plan.md file?"
   - The AI can read and explain any rule in natural language

4. **Check compliance**:
   - Rules have checklists (final section)
   - Validation prompts help verify outputs

### As a Rule Author

1. **Extract from practice** (recommended):
   - Do real work 2-3 times
   - Notice patterns
   - Use `@.cursor/prompts/rule-authoring/extract-prompts-from-conversation.md`

2. **Follow framework**:
   - Use `rule-authoring/` rules as guide
   - Structure: Front-matter + canonical sections + checklist
   - Version properly (semantic versioning)

3. **Create supporting prompts**:
   - For each rule domain, create task workflows in `prompts/`
   - Prompts reference rules for enforcement

### As an Agent

1. **Read agent-application rules first**:
   - When user makes request, scan for matching agent-application rule
   - Example: "Start ticket" → Read `ticket/agent-application-rule.mdc`

2. **Apply operational rules automatically**:
   - File-mask rules trigger on file pattern match
   - Always-apply rules run on everything

3. **Use prompts as workflows**:
   - When user references prompt, follow its steps
   - Invoke rules as needed per prompt instructions

---

## Key Principles

### 1. **Extraction Over Design**
- Rules are extracted from real work, not designed theoretically
- Ensures rules are practical and battle-tested

### 2. **Explicit Over Implicit**
- Every rule declares what it reads (`globs`), writes (`governs`), needs (`requires`)
- No hidden side effects

### 3. **Stability Through IDs**
- Rules/prompts reference each other by stable IDs, not file paths
- Files can move, IDs stay same

### 4. **Separation of Concerns**
- **Rules**: Define standards (how)
- **Prompts**: Define workflows (what)
- **Templars**: Define structure
- **Exemplars**: Show patterns

### 5. **Dogfooding**
- AI uses rules to refine rules
- Rules improve through use
- Self-improving system

### 6. **One Agent-Application Per Domain**
- Each domain has exactly ONE coordination rule
- Keeps system simple and fast

---

## Quick Reference

### Common Workflows

| Task | Prompt | Rules Applied |
|------|--------|---------------|
| Start ticket | `prompts/ticket/start-ticket.md` | `ticket/plan-rule.mdc`, `ticket/context-rule.mdc` |
| Create user story | `prompts/agile/create-user-story.md` | `agile/user-story-documentation-rule.mdc` |
| Create branch | `prompts/git/create-branch.md` | `git/branch-naming-rule.mdc` |
| Document entity | `prompts/technical-specifications/document-domain-object.md` | `technical-specifications/domain-object-rule.mdc` |
| Generate tests | `prompts/unit-testing/generate-missing-tests.md` | `unit-testing/unit-test-organization-rule.mdc` |

### File Patterns

| Pattern | Rule Domain | Example |
|---------|-------------|---------|
| `**/plan.md` | Ticket | `tickets/EPP-123/plan.md` |
| `**/user-story-*.md` | Agile | `docs/agile/user-story-oauth-login.md` |
| `**/*-rule.mdc` | Rule Authoring | `.cursor/rules/ticket/plan-rule.mdc` |
| `**/domain-object-*.md` | Technical Specs | `docs/technical/billing/domain-object-Invoice.md` |

---

## Getting Help

### Ask the AI

**You can always ask the AI to explain any rule or prompt:**

```
"Explain the ticket management rules"
"How do the git branching rules work?"
"What's the difference between rules and prompts?"
"Show me the agile documentation standards"
"What rules apply to SQL scripts?"
"Explain rule invocation strategies"
```

The AI has full access to all rules and can:
- Explain rules in natural language
- Show examples from the rules
- Clarify when rules apply
- Guide you through workflows
- Help troubleshoot rule conflicts

### Browse Documentation

- **Rule Framework**: Start with `.cursor/rules/rule-authoring/rule-authoring-overview.mdc`
- **Prompt Framework**: See `.cursor/rules/prompts/` (if exists)
- **Invocation Strategies**: Read `.cursor/rules/rule-authoring/rule-invocation-strategies.mdc`
- **Extraction Guide**: Read `.cursor/rules/rule-authoring/rule-extraction-from-practice.mdc`

### Quick Help Commands

| Question | AI Response |
|----------|-------------|
| "What rules apply to this file?" | Lists relevant rules based on file pattern |
| "Explain rule X" | Detailed explanation of specific rule |
| "Show me the checklist for X" | Displays validation checklist |
| "What prompts are available?" | Lists prompts by domain |
| "How do I create a ticket?" | Guides through ticket workflow |

---

## Version & Provenance

**Created**: 2025-12-01  
**Purpose**: Central navigation and explanation of rules/prompts system  
**Audience**: Developers, AI agents, rule authors  
**Maintained by**: Team AI / Foundation Team

