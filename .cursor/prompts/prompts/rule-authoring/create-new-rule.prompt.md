---
name: create-new-rule
description: "Please create a new rule file following the rule-authoring framework and best practices"
category: rule-authoring
tags: rules, creation, new, template, framework, rule-authoring
argument-hint: "Rule name and purpose"
templar: .cursor/prompts/templars/rule/rule-creation-templar.md
exemplar: .cursor/prompts/exemplars/rule/rule-creation-exemplar.md
rules:
  - .cursor/rules/rule-authoring/rule-authoring-overview.mdc
  - .cursor/rules/rule-authoring/rule-file-structure.mdc
  - .cursor/rules/rule-authoring/rule-naming-conventions.mdc
  - .cursor/rules/rule-authoring/rule-contracts-and-scope.mdc
---

# Create New Rule

Please create a new rule file following the rule-authoring framework standards and best practices.

**Pattern**: Rule Creation Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for maintaining rule library quality and consistency
**Use When**: Creating new operational rules, templars, or exemplars for the framework

---

## Purpose

This prompt helps create high-quality rule files by:
- Guiding through systematic rule creation process
- Enforcing rule-authoring framework standards
- Ensuring YAML front-matter compliance (rule-file-structure standards)
- Providing ready-to-use templates and exemplars
- Validating against quality criteria and framework requirements

Use this when you need to formalize a new operational rule or create a rule from scratch following the rule-authoring framework.

---

## Required Context

- **Rule Name**: What the rule will be called (kebab-case domain-action format)
- **Purpose**: What the rule does (clear, specific operational behavior)
- **Domain**: Which domain it belongs in (e.g., `ticket`, `migration`, `git`)
- **Optional**: Examples of when it should activate or what it produces

---

## Process

Follow these steps to create a new rule:

### Step 1: Define Rule Requirements
Gather information about what the rule needs to do:
- Specific behavior/task the rule governs
- Target audience (agents, tools, developers)
- Use cases/scenarios where rule applies
- Expected outputs or constraints enforced

### Step 2: Choose Domain and Name
Determine appropriate domain folder and kebab-case name (see Creation Process below for guidelines).

### Step 3: Create Rule File
Generate complete `.mdc` file with valid YAML front-matter and structured content following rule-file-structure.mdc.

### Step 4: Validate Framework Compliance
Verify YAML front-matter follows rule-file-structure.mdc standards (proper front-matter schema, no JSON arrays).

### Step 5: Add to Rule Registry (Optional)
If creating for a domain, ensure rule follows cross-references and implements appropriate capabilities.

### Step 6: Test Usage
Try the rule in a context where it should activate to verify it works as expected.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Understand Scope**: What operational behavior does this rule govern? What problem does it solve?
2. **Identify Domain**: Where does this rule fit in the domain taxonomy? (ticket, migration, git, etc.)
3. **Define Contracts**: What are the explicit inputs and outputs? What files does it govern?
4. **Plan Structure**: What sections will make this rule most effective? (Purpose, Contracts, Steps, Checklist)
5. **Create Content**: Generate complete rule file with front-matter and body following framework standards
6. **Validate Quality**: Check against rule-authoring framework requirements (structure, contracts, checklist)

---

## Creation Process

### Step 1: Define Purpose

Answer these questions:
- **What operational behavior does this rule govern?** (specific action or constraint)
- **Who will use this rule?** (target agents, tools, or developers)
- **When does it activate?** (use cases/scenarios, file patterns)
- **What does it enforce or produce?** (expected outputs or constraints)

### Step 2: Choose Location

Determine the appropriate domain folder following the existing taxonomy:

**Existing Domains**:
- `agile/` - Agile artifacts (epics, stories, features)
- `cicd/` - CI/CD and automation
- `code-quality/` - Code quality and refactoring
- `database-standards/` - Database development
- `documentation/` - Documentation generation/validation
- `git/` - Git workflows and operations
- `migration/` - System migration tasks
- `quality/` - Quality standards and enforcement
- `rule-authoring/` - Rule creation and management
- `setup/` - Project setup and bootstrapping
- `technical-specifications/` - Technical specifications
- `ticket/` - Ticket workflow management
- `unit-testing/` - Testing tasks

**New Domain?**: Create if no existing domain fits, following naming conventions.

### Step 3: Name the Rule

**Naming Rules** (from rule-naming-conventions.mdc):
- Use kebab-case (lowercase with hyphens)
- Start with domain (e.g., `ticket-plan-update`)
- Follow verb-noun pattern where applicable
- Avoid redundancy (domain already in folder)
- Keep reasonably short (2-5 words)

**Examples**:
- ✅ `ticket-plan-update.mdc`
- ✅ `git-branch-naming.mdc`
- ✅ `migration-data-collection.mdc`
- ❌ `ticket.mdc` (too vague)
- ❌ `TicketPlanUpdate.mdc` (wrong case, no hyphens)
- ❌ `ticket-ticket-plan-update.mdc` (redundant domain)

### Step 4: Write Front-Matter

**Required Fields** (from rule-file-structure.mdc):
```yaml
---
id: rule.[domain].[action].v[major]
kind: rule | templar | exemplar
version: [semver]
description: [One-sentence purpose/overview]
globs: **/[pattern]              # Cursor custom format - NO brackets, NO quotes
governs: **/[pattern]            # Cursor custom format - NO brackets, NO quotes
implements: [action]             # What capability this provides
requires: []                     # Array of rule IDs needed
model_hints: { temp: 0.2, top_p: 0.9 }  # Determinism controls
provenance: { owner: [team/user], last_review: [YYYY-MM-DD] }
alwaysApply: false               # Explicit invocation control
---
```

**Critical**: `globs` and `governs` use Cursor's comma-delimited format (plain string, NOT YAML arrays!)

**Correct format**:
```yaml
globs: **/tickets/*/plan.md
governs: **/tickets/*/plan.md
```

**WRONG format** (will break Cursor):
```yaml
globs: ["**/tickets/*/plan.md"]     # JSON array - WRONG!
governs:
  - **/tickets/*/plan.md            # YAML array - WRONG!
```

### Step 5: Write Content Structure

**Canonical Section Ordering** (from rule-file-structure.mdc):

1. **Purpose & Scope**
2. **Inputs (Contract)**
3. **Outputs (Contract)**
4. **Deterministic Steps**
5. **Formatting Requirements**
6. **OPSEC and Leak Control**
7. **Integration Points**
8. **Failure Modes and Recovery**
9. **Provenance Footer Specification**
10. **Related Rules**
11. **FINAL MUST-PASS CHECKLIST** (always last)

**Minimum Structure**:
```markdown
# [Rule Title]

## Purpose & Scope

[Why this rule exists and what it applies to]

**Applies to**: [Specific contexts]
**Does not apply to**: [Exclusions]

## Inputs (Contract)

- [Input requirement 1]
- [Input requirement 2]

## Outputs (Contract)

- [Output guarantee 1]
- [Output guarantee 2]

## Deterministic Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## FINAL MUST-PASS CHECKLIST

- [ ] [Critical validation 1]
- [ ] [Critical validation 2]
- [ ] [Critical validation 3]
```

### Step 6: Validate & Test

1. **Validate format**: Check YAML front-matter is valid and follows rule-file-structure.mdc
2. **Test activation**: Try the rule in a context where it should trigger
3. **Check quality**: Verify against framework requirements
4. **Fix issues**: Address any validation errors/warnings

---

## Rule Template

Use this as starting point for new rules:

```markdown
---
id: rule.domain.action.v1
kind: rule
version: 1.0.0
description: "One-sentence description of what this rule does"
globs: **/specific-pattern.md
governs: **/specific-pattern.md
implements: action
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-name, last_review: 2025-12-13 }
alwaysApply: false
---

# Rule Title

## Purpose & Scope

This rule [purpose statement].

**Applies to**: [what it governs]
**Does not apply to**: [explicit exclusions]

## Inputs (Contract)

- [What must be available for rule to execute]

## Outputs (Contract)

- [What rule will produce or guarantee]

## Deterministic Steps

1. [First operational step]
2. [Second operational step]
3. [Third operational step]

## Formatting Requirements

Output must follow [templar reference if applicable].

## OPSEC and Leak Control

- NO secrets, tokens, or credentials
- NO internal URLs or paths
- NO email addresses

## Integration Points

- [How this rule coordinates with others]

## Failure Modes and Recovery

**[Failure scenario]**: [Detection method]
- Recovery: [Recovery actions]

## Provenance Footer Specification

Append to generated files:
```
Produced-by: {{rule_id}} | {{templar_id}} | model={{model}} | ts={{timestamp}} | hash={{input_hash}}
```

## Related Rules

- `rule.authoring.file-structure.v1` - Framework structure requirements
- `rule.authoring.contracts.v1` - Contract writing patterns

## FINAL MUST-PASS CHECKLIST

- [ ] OPSEC clean (no secrets/tokens/URLs/emails)
- [ ] Output matches required structure
- [ ] All required fields present
- [ ] Only governed files modified
```

---

## Examples (Few-Shot)

### Example 1: Creating a Ticket Plan Rule

**Input**:
```
Create a rule to update ticket plan.md files with structured sections
```

**Reasoning**:
Ticket workflow task (domain: `ticket`), action is updating plan files (action: `plan-update`), governs plan.md files. Should enforce structured sections and OPSEC.

**Expected Output**:

**Complete Rule File**: `.cursor/rules/ticket/plan-rule.mdc`

```yaml
---
id: rule.ticket.plan.update.v1
kind: rule
version: 1.0.0
description: "Updates plan.md files with required sections for ticket planning"
globs: **/tickets/*/plan.md
governs: **/tickets/*/plan.md
implements: plan.update
requires:
  - templar.plan.v1
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-12-13 }
alwaysApply: false
---

# Ticket Plan Update Rule

## Purpose & Scope

This rule ensures all plan.md files in ticket directories follow a consistent structure with required sections for effective ticket planning and execution.

**Applies to**: All `plan.md` files in `tickets/` subdirectories at any depth.
**Does not apply to**: Template files, archives, or plan.md files outside ticket directories.

## Inputs (Contract)

- Existing `plan.md` file or directory where it should be created
- Ticket objective and acceptance criteria information
- Complexity assessment details

## Outputs (Contract)

- Updated or created `plan.md` file with required sections
- Provenance footer appended to track generation
- Only the plan.md file modified (no other ticket files affected)

## Deterministic Steps

1. Validate input parameters (objective, criteria, complexity)
2. Locate or create plan.md file in correct ticket directory
3. Load templar.plan.v1 for required section structure
4. Update plan.md with provided information
5. Append provenance footer with rule ID and timestamp

## Formatting Requirements

Output must follow `templar.plan.v1` structure:
- Section "## Objective" (required)
- Section "## Acceptance Criteria" (required)
- Section "## Complexity" (required)
- Section "## Dependencies" (optional)

## OPSEC and Leak Control

- NO secrets, tokens, or credentials in plan content
- NO internal URLs or system paths
- NO email addresses or personal information
- NO exemplar content copied verbatim

## Integration Points

- Coordinates with `rule.ticket.timeline.update.v1` for timeline tracking
- Uses `templar.plan.v1` for consistent formatting
- Integrates with ticket workflow validation

## Failure Modes and Recovery

**Missing required input**: Objective or criteria not provided
- Detection: Input validation fails at step 1
- Recovery: Return error with specific missing requirements

**File access denied**: Cannot write to plan.md
- Detection: File system error during write operation
- Recovery: Check permissions, suggest alternative location

## Provenance Footer Specification

Append to generated/updated plan.md files:

```
---
Produced-by: rule.ticket.plan.update.v1 | templar.plan.v1 | model=cursor-agent | ts=2025-12-13T14:30:00Z | hash=sha256:a3f5d9e2b8c1
```

## Related Rules

- `rule.authoring.file-structure.v1` - Rule framework requirements
- `rule.authoring.contracts.v1` - Input/output contract patterns
- `rule.ticket.timeline.update.v1` - Timeline coordination
- `templar.plan.v1` - Output structure template

## FINAL MUST-PASS CHECKLIST

- [ ] OPSEC clean (no secrets/tokens/URLs/emails)
- [ ] Output matches templar.plan.v1 structure
- [ ] Provenance footer present with rule ID
- [ ] Only governed files modified (plan.md only)
- [ ] Required sections present (Objective, Criteria, Complexity)
```

**Validation**: ✅ PASS
- Frontmatter valid YAML (proper comma-delimited globs/governs)
- Name follows naming conventions
- Domain and structure correct
- Content has clear contracts and steps
- Checklist is binary and covers critical validations

### Example 2: Creating a Git Branch Naming Rule

**Input**:
```
Create a rule to validate Git branch names against project conventions
```

**Reasoning**:
Git workflow task (domain: `git`), action is validation (action: `branch-naming`), read-only validation so governs empty. Should check branch name format and provide corrections.

**Expected Output**:

**Complete Rule File**: `.cursor/rules/git/branch-naming-rule.mdc`

```yaml
---
id: rule.git.branch.naming.v1
kind: rule
version: 1.0.0
description: "Validates Git branch names against established naming conventions"
globs: **/.git/HEAD
governs: ""
implements: branch.naming.validate
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-devops, last_review: 2025-12-13 }
alwaysApply: false
---

# Git Branch Naming Validation Rule

## Purpose & Scope

This rule validates Git branch names against project conventions to ensure consistent naming and proper ticket traceability.

**Applies to**: Git branch creation and validation operations.
**Does not apply to**: Existing branches, merge operations, or deletion.

## Inputs (Contract)

- Branch name to validate (string)
- Optional: Ticket ID for cross-reference validation

## Outputs (Contract)

- Validation result (pass/fail)
- Specific issues found (if failed)
- Suggested corrected name (if failed)
- Error message with guidance

## Deterministic Steps

1. Parse branch name into components (type/ticket/description)
2. Validate type (feature, fix, hotfix)
3. Validate ticket ID format (PROJ-1234 pattern)
4. Validate description format (kebab-case)
5. Return validation result with details

## Formatting Requirements

Validation messages must follow standard error format:
```
❌ ERROR: Branch name invalid
Issue: [specific problem]
Solution: Use format: [type]/[TICKET]-[description]
Example: feature/PROJ-123-add-validation
```

## OPSEC and Leak Control

- NO secrets in branch names (automatically flagged)
- NO internal system references
- NO personal information in branch names

## Integration Points

- Used by `rule.git.branch.lifecycle.v1` for branch creation validation
- Coordinates with JIRA integration for ticket validation
- Provides suggestions for branch name correction

## Failure Modes and Recovery

**Invalid branch name format**: Name doesn't match pattern
- Detection: Regex validation fails
- Recovery: Provide corrected format with examples

**Ticket ID not found**: Referenced ticket doesn't exist in JIRA
- Detection: JIRA API validation fails
- Recovery: Suggest valid ticket ID or allow override

## Provenance Footer Specification

No provenance footer (validation rule, no file generation).

## Related Rules

- `rule.git.branch.lifecycle.v1` - Branch creation workflow
- `rule.git.branch.structure.v1` - Branch type definitions
- `rule.authoring.naming-conventions.v1` - Naming pattern standards

## FINAL MUST-PASS CHECKLIST

- [ ] Branch name format validated correctly
- [ ] Clear error messages with specific issues
- [ ] Suggested corrections provided
- [ ] No OPSEC violations in validation logic
- [ ] Integration with branch lifecycle rules
```

---

## Quick Start

**Interactive Creation**:
```
@create-new-rule

AI: What should this rule do?
You: [Describe operational behavior]

AI: What domain does it belong to?
You: [Choose from existing domains]

AI: What should it be named?
You: [Provide kebab-case name]

[AI generates complete rule file]
```

**Direct Creation**:
```
@create-new-rule "validate-git-branch-names" in git domain
```

---

## Quality Checklist

Before finalizing new rule:

- [ ] **Frontmatter**:
  - [ ] Valid YAML (proper comma-delimited globs/governs, no JSON arrays)
  - [ ] ID follows `rule.[domain].[action].v[major]` pattern
  - [ ] Description is clear and actionable (one sentence)
  - [ ] Domain matches existing taxonomy or justified new domain
  - [ ] `globs` and `governs` use Cursor format (comma-separated strings)
- [ ] **Content**:
  - [ ] Clear purpose and scope with explicit applies-to/does-not-apply-to
  - [ ] Contracts are explicit and testable (inputs/outputs)
  - [ ] Steps are deterministic and verifiable
  - [ ] Checklist covers OPSEC, structure, and contracts (3-7 items)
  - [ ] Related rules referenced by ID
- [ ] **File**:
  - [ ] Saved as `[domain]-[action]-rule.mdc` in correct domain folder
  - [ ] Tested in Cursor context (actually works when activated)
  - [ ] Follows rule-file-structure.mdc canonical ordering

---

## Related Prompts

- `rule-authoring/find-recently-added-rules.prompt.md` - Find newly added rules
- `rule-authoring/find-rules-needing-review.prompt.md` - Find rules requiring attention
- `rule-authoring/validate-rule.prompt.md` - Validate rule format and quality
- `rule-authoring/improve-rule.prompt.md` - Fix rule issues and enhance quality
- `rule-authoring/enhance-rule.prompt.md` - Add advanced features to existing rules
- `templars/rule/rule-creation-templar.md` - Reusable rule creation structure
- `exemplars/rule/rule-creation-exemplar.md` - Reference rule creation examples

---

## Related Rules

- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Rule structure requirements (content quality)
- `.cursor/rules/rule-authoring/rule-naming-conventions.mdc` - Naming standards
- `.cursor/rules/rule-authoring/rule-contracts-and-scope.mdc` - Contract writing patterns
- `.cursor/rules/rule-authoring/rule-cross-references.mdc` - Reference patterns
- `.cursor/rules/rule-authoring/rule-provenance-and-versioning.mdc` - Versioning requirements

---

## Extracted Patterns

This prompt demonstrates exceptional quality in systematic rule creation and has been extracted into:

**Templar**:
- `.cursor/prompts/templars/rule/rule-creation-templar.md` - Abstract pattern for guided multi-step rule creation

**Exemplar**:
- `.cursor/prompts/exemplars/rule/rule-creation-exemplar.md` - Reference standard for framework-compliant rule creation (Quality Score: 95/100)

**Why Extracted**: Demonstrates outstanding framework compliance, comprehensive examples, step-by-step guidance, quality validation, and integration with rule-authoring framework.

**Reuse**: Use the templar when creating operational rules, validation rules, or any framework-compliant rule. Reference the exemplar to understand what makes rules framework-compliant and effective.

---

**Created**: 2025-12-13
**Follows**: `.cursor/rules/rule-authoring/rule-authoring-overview.mdc` v1.0.0
**Enhanced**: 2025-12-13 (RULES-CREATION initiative)

