---
name: create-new-prompt
description: "Please create a new prompt file following Prompt Registry format and best practices"
category: prompt
tags: prompts, creation, new, template, standards
argument-hint: "Prompt name and purpose"
templar: .cursor/prompts/templars/prompt/prompt-creation-templar.md
exemplar: .cursor/prompts/exemplars/prompt/prompt-creation-exemplar.md
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Create New Prompt

Please create a new prompt file following Prompt Registry format standards and best practices.

**Pattern**: Prompt Creation Pattern ⭐⭐⭐⭐  
**Effectiveness**: Essential for maintaining prompt library quality  
**Use When**: Creating new reusable prompts for the library

---

## Purpose

This prompt helps create high-quality, reusable prompt files by:
- Guiding through systematic creation process
- Enforcing Prompt Registry format standards
- Ensuring YAML frontmatter compliance (EPP-192 standards)
- Providing ready-to-use templates
- Validating against quality criteria

Use this when you need to formalize an ad-hoc prompt into a reusable library prompt or create a new prompt from scratch.

---

## Required Context

- **Prompt Name**: What the prompt will be called (kebab-case)
- **Purpose**: What the prompt does (clear, specific)
- **Category**: Which category folder it belongs in (e.g., `ticket`, `testing`, `agile`)
- **Optional**: Examples of how it should be used

---

## Process

Follow these steps to create a new prompt:

### Step 1: Define Prompt Requirements
Gather information about what the prompt needs to do:
- Specific action/task
- Target audience
- Use cases/scenarios
- Expected output

### Step 2: Choose Category and Name
Determine appropriate category folder and kebab-case name (see Creation Process below for guidelines).

### Step 3: Create Prompt File
Generate complete `.prompt.md` file with valid YAML frontmatter and structured content.

### Step 4: Validate Format
Verify YAML frontmatter follows EPP-192 standards (no JSON arrays, proper YAML lists).

### Step 5: Add to Collection (Optional)
If creating for a collection, update appropriate `.collection.yml` manifest.

### Step 6: Test Usage
Try the prompt in Cursor chat to verify it works as expected.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Understand Request**: What specific need does this prompt address? What task will it perform?
2. **Identify Category**: Where does it fit in the prompt library? (ticket, testing, agile, etc.)
3. **Define Scope**: What should it do (and NOT do)? Clear boundaries.
4. **Plan Structure**: What sections will make it most effective? (Purpose, Process, Examples, Validation)
5. **Create Content**: Generate complete prompt file with frontmatter and body
6. **Validate Quality**: Check against quality criteria (clear, actionable, validated)

---

## Creation Process

### Step 1: Define Purpose

Answer these questions:
- **What does this prompt do?** (specific action)
- **Who will use it?** (target audience)
- **When is it used?** (use cases/scenarios)
- **What output does it produce?** (expected result)

### Step 2: Choose Location

Determine the appropriate category folder:

**Existing Categories**:
- `agile/` - Agile artifacts (epics, stories, features)
- `code-quality/` - Code quality and refactoring
- `cicd/` - CI/CD and automation
- `database-standards/` - Database development
- `documentation/` - Documentation generation/validation
- `git/` - Git workflows and operations
- `migration/` - System migration tasks
- `package/` - Package management
- `prompt/` - Prompt meta-tasks
- `rule-authoring/` - Rule creation and management
- `setup/` - Project setup and bootstrapping
- `script/` - Script creation and enhancement
- `technical/` - Technical specifications
- `technical-specifications/` - Domain documentation
- `ticket/` - Ticket workflow management
- `unit-testing/` - Testing tasks

**New Category?**: Create if no existing category fits

### Step 3: Name the Prompt

**Naming Rules**:
- Use kebab-case (lowercase with hyphens)
- Start with action verb (create, validate, generate, analyze, etc.)
- Be specific and descriptive
- Avoid category redundancy
- Keep reasonably short (2-5 words)

**Examples**:
- ✅ `create-user-story.prompt.md`
- ✅ `validate-test-coverage.prompt.md`
- ✅ `analyze-xml-documentation.prompt.md`
- ❌ `story.prompt.md` (too vague)
- ❌ `CreateUserStory.prompt.md` (wrong case)
- ❌ `agile-create-user-story.prompt.md` (redundant category)

### Step 4: Write Frontmatter

**Required Fields**:
```yaml
---
name: prompt-name
description: "Clear, action-oriented one-sentence description"
---
```

**Recommended Fields**:
```yaml
---
name: prompt-name
description: "Clear, action-oriented one-sentence description"
category: category-name
tags: keyword1, keyword2, keyword3, keyword4
argument-hint: "What input this prompt expects (optional)"
---
```

**YAML Format Rules** (EPP-192 Standards):
- ✅ Use YAML list format for arrays (with `- ` prefix on separate lines)
- ✅ Quote all string values (especially description)
- ✅ Use 2-space indentation
- ❌ NO JSON arrays: `tools: ["item"]`
- ❌ NO single-line arrays: `tags: [tag1, tag2]`
- ❌ NO empty arrays: `tools: []`

**Correct multi-line YAML array**:
```yaml
tags:
  - keyword1
  - keyword2
  - keyword3
```

**Or comma-separated for simple values**:
```yaml
tags: keyword1, keyword2, keyword3
```

### Step 5: Write Content

**Minimum Structure**:
```markdown
# [Prompt Title]

[Brief description of what this prompt does]

## Purpose

[Detailed explanation of purpose and use cases]

## Instructions

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Output

[Description of expected output format]

## Usage

[Usage examples]
```

**Enhanced Structure** (Recommended):
```markdown
# [Prompt Title]

[Brief description]

**Pattern**: [Pattern Name] ⭐⭐⭐⭐⭐  
**Effectiveness**: [Effectiveness statement]  
**Use When**: [Use cases]

---

## Purpose

[Detailed purpose and what problem it solves]

## Required Context

- [Context item 1]
- [Context item 2]

## Process

### Step 1: [First Step]
[Detailed instructions]

### Step 2: [Second Step]
[Detailed instructions]

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-creation-exemplar.md`

## Expected Output

[Output format specification]

---

## Quality Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

---

## Usage

[Usage examples]

---

## Related Prompts

- `category/related-prompt.prompt.md` - [When to use]

---

## Related Rules

- `.cursor/rules/path/rule.mdc` - [Relevance]
```

### Step 6: Validate & Test

1. **Validate format**: Check YAML frontmatter is valid
2. **Test usage**: Try the prompt in Cursor chat
3. **Check quality**: Verify against quality checklist
4. **Fix issues**: Address any validation errors/warnings

---

## Prompt Template

Use this as starting point for new prompts:

```markdown
---
name: your-prompt-name
description: "What this prompt does in one clear sentence"
category: appropriate-category
tags: tag1, tag2, tag3, tag4
argument-hint: "What input it expects (if applicable)"
---

# Your Prompt Title

Brief introduction explaining what this prompt accomplishes and when to use it.

**Pattern**: [Pattern Name if applicable]  
**Effectiveness**: [Effectiveness statement]  
**Use When**: [Use cases]

---

## Purpose

Detailed explanation of:
- What problem it solves
- When to use it
- What it produces

---

## Required Context

- [Context requirement 1]
- [Context requirement 2]

---

## Process

Follow these steps to use this prompt:

### Step 1: [Step Name]
[Clear instructions]

### Step 2: [Step Name]
[Clear instructions]

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **[First reasoning step]**: [Description]
2. **[Second reasoning step]**: [Description]

---

## Instructions

1. [Clear, actionable step]
2. [Clear, actionable step]
3. [Clear, actionable step]

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-creation-exemplar.md`

## Expected Output

Description of what this prompt will produce:
- Output format
- Key sections/elements
- Quality standards

---

## Quality Criteria

- [ ] [Quality criterion 1]
- [ ] [Quality criterion 2]
- [ ] [Quality criterion 3]

---

## Usage

Basic usage:
```
@your-prompt-name [argument]
```

With context:
```
@your-prompt-name [argument] with [context]
```

---

## Related Prompts

- `category/related-prompt.prompt.md` - [When to use instead/in addition]

---

## Related Rules

- `.cursor/rules/category/rule.mdc` - [Relevance]

---

**Created**: [Date]  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
```

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-creation-exemplar.md`

## Expected Output

Coverage report showing:

```markdown
## Coverage Summary
- Overall Coverage: [X]%
- Files Analyzed: [count]
- Untested Functions: [count]

## Missing Coverage

### [FileName.cs]
- **Method**: `MethodName()` - No tests found
- **Edge Cases**: Missing null input test
- **Error Paths**: Exception handling not tested

## Priority Recommendations

1. 🔴 HIGH: [Critical missing tests]
2. 🟡 MEDIUM: [Important missing tests]
3. 🟢 LOW: [Nice-to-have tests]
```

---

## Quality Criteria

- [ ] All source files scanned
- [ ] Test files identified
- [ ] Coverage percentage calculated
- [ ] Specific gaps listed with file/method names
- [ ] Priorities assigned
- [ ] Actionable recommendations provided

---

## Usage

Basic usage:
```
@analyze-test-coverage src/Domain/
```

Specific file:
```
@analyze-test-coverage src/Domain/Entity.cs
```

---

## Related Prompts

- `unit-testing/generate-tests.prompt.md` - Generate missing tests identified
- `unit-testing/validate-test-quality.prompt.md` - Validate existing test quality

---

## Related Rules

- `.cursor/rules/unit-testing/unit-test-coverage-rule.mdc` - Coverage standards
- `.cursor/rules/unit-testing/unit-test-quality-rule.mdc` - Quality requirements
```

**Final File**: `.cursor/prompts/unit-testing/analyze-test-coverage.prompt.md`

**Validation**: ✅ PASS
- Frontmatter valid YAML (no JSON arrays)
- Name is kebab-case and descriptive
- Category specified
- Content has clear structure
- Instructions actionable
- Examples provided
- Usage shown

### Example 2: Creating a Git Workflow Prompt

**Input**:
```
Create a prompt to help with branch naming validation
```

**Reasoning**:
Git workflow task (category: `git`), action is validation (verb: `validate`), target is branch names. Should check against naming conventions and suggest corrections.

**Expected Output**:

**Complete Prompt File**: `.cursor/prompts/git/validate-branch-name.prompt.md`

```markdown
---
name: validate-branch-name
description: "Please validate Git branch names against naming conventions"
category: git
tags: git, branching, naming, validation, conventions
argument-hint: "Branch name to validate"
---

# Validate Branch Name

Please validate Git branch names against established naming conventions and suggest corrections if needed.

**Pattern**: Validation Pattern  
**Effectiveness**: Prevents non-compliant branch names  
**Use When**: Before creating new Git branches

---

## Purpose

Validate branch names to ensure they follow project conventions, preventing naming inconsistencies and enabling proper branch tracking.

---

## Required Context

- **Branch Name**: Name to validate (e.g., `feature/EPP-192-add-validation`)
- **Optional**: Ticket ID for validation

---

## Process

### Step 1: Parse Branch Name
Extract branch type, ticket ID, and description from name.

### Step 2: Validate Format
Check against naming convention:
```
[type]/[TICKET-ID]-[brief-description]
```

### Step 3: Validate Components
- **Type**: Must be `feature`, `fix`, or `hotfix`
- **Ticket ID**: Must match pattern (e.g., `EPP-192`, `EBASE-12345`)
- **Description**: Must be kebab-case, descriptive

### Step 4: Report Results
Provide validation results with suggestions if invalid.

---

## Expected Output

**If Valid**:
```markdown
✅ Branch name is valid: `feature/EPP-192-add-validation`

- Type: feature ✅
- Ticket ID: EPP-192 ✅
- Description: add-validation ✅

**Ready to create**: `git checkout -b feature/EPP-192-add-validation`
```

**If Invalid**:
```markdown
❌ Branch name is invalid: `Feature/EPP192_Add_Validation`

**Issues Found**:
- Type: "Feature" should be lowercase → "feature"
- Ticket ID: "EPP192" missing hyphen → "EPP-192"
- Description: "Add_Validation" uses underscores → "add-validation"

**Suggested Fix**: `feature/EPP-192-add-validation`

**Create with**: `git checkout -b feature/EPP-192-add-validation`
```

---

## Quality Criteria

- [ ] Branch type validated (feature, fix, hotfix)
- [ ] Ticket ID format validated
- [ ] Description format validated (kebab-case)
- [ ] Clear pass/fail indication
- [ ] Specific issues identified (if invalid)
- [ ] Corrected suggestion provided (if invalid)

---

## Usage

Validate proposed name:
```
@validate-branch-name feature/EPP-192-add-validation
```

Check before creating:
```
@validate-branch-name Feature/EPP192_Add_Validation
```

---

## Related Prompts

- `git/create-branch.prompt.md` - Create branch after validation

---

## Related Rules

- `.cursor/rules/git/branch-naming-rule.mdc` - Branch naming conventions
- `.cursor/rules/git/branch-structure-rule.mdc` - Branch structure requirements
```

---

## Quick Start

**Interactive Creation**:
```
@create-new-prompt

AI: What should this prompt do?
You: [Describe purpose]

AI: What category does it belong to?
You: [Choose category]

AI: What should it be named?
You: [Provide name]

[AI generates complete prompt file]
```

**Direct Creation**:
```
@create-new-prompt "validate-api-response" in api-testing category
```

---

## Quality Checklist

Before finalizing new prompt:

- [ ] **Frontmatter**:
  - [ ] Valid YAML (no JSON arrays, proper YAML lists)
  - [ ] Name is kebab-case and descriptive
  - [ ] Description is clear and quoted
  - [ ] Category specified
  - [ ] Tags relevant and specific (3-6 tags)
- [ ] **Content**:
  - [ ] Clear structure (Purpose, Process, Examples, Output)
  - [ ] Instructions are actionable
  - [ ] Examples provided (Few-Shot pattern)
  - [ ] Usage syntax shown
  - [ ] Related prompts/rules referenced
- [ ] **File**:
  - [ ] Saved as `name.prompt.md` in correct category folder
  - [ ] Tested in Cursor chat (actually works)

---

## Related Prompts

- `prompt/validate-prompt.prompt.md` - Validate the new prompt format and quality
- `prompt/improve-prompt.prompt.md` - Improve prompt quality and effectiveness
- `prompt/enhance-prompt.prompt.md` - Add advanced features to existing prompts
- `rule-authoring/extract-prompts-from-conversation.prompt.md` - Extract prompts from conversations
- `templars/prompt/prompt-creation-templar.md` - Reusable creation structure
- `exemplars/prompt/prompt-creation-exemplar.md` - Reference creation prompt

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards (content quality)
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Prompt Registry format requirements

---

## Extracted Patterns

This prompt demonstrates exceptional quality and has been extracted into:

**Templar**:
- `.cursor/prompts/templars/prompt/prompt-creation-templar.md` - Abstract pattern for guided multi-step prompt creation

**Exemplar**:
- `.cursor/prompts/exemplars/prompt/prompt-creation-exemplar.md` - Reference standard for concise, registry-ready prompt creation (Quality Score: 96/100)

**Why Extracted**: Demonstrates outstanding decision trees, complete walkthrough examples, good/bad patterns, ready-to-use templates, progressive disclosure, and multiple invocation modes.

**Reuse**: Use the templar when creating setup wizards, artifact creation workflows, or any multi-step guided process. Reference the exemplar to understand what makes comprehensive guidance exceptional.

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)


