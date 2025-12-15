---
name: organize-prompts
description: "Please organize prompts into appropriate categories and ensure proper folder structure"
category: prompt
tags: prompts, organization, structure, categories, cleanup
argument-hint: "Folder path or 'all' for complete organization"
templar: .cursor/prompts/templars/prompt/categorization-workflow-templar.md
exemplar: .cursor/prompts/exemplars/prompt/guided-creation-workflow-exemplar.md
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Organize Prompts

Please analyze and organize prompts into appropriate category folders following a logical structure.

**Pattern**: Categorization Workflow Pattern ⭐⭐⭐⭐  
**Effectiveness**: Essential for maintaining organized prompt library  
**Use When**: Prompts are misplaced, uncategorized, or library needs cleanup

---

## Purpose

This prompt categorizes uncategorized or miscategorized prompts, moves them to correct folders, updates their frontmatter, and ensures the prompt library stays well-organized.

Use this when:
- New prompts in `extracted/` folder need proper homes
- Prompts are in wrong categories
- Library structure needs cleanup
- After bulk prompt creation or extraction

---

## Required Context

- **Target Scope**: Folder path to organize (e.g., `extracted/`) or `all` for complete audit
- **Prompt Library Structure**: Understanding of category folders
- **File System Access**: Ability to read prompt files and move them

---

## Process

Follow these steps to organize prompts:

### Step 1: Inventory Current State
Scan for misplaced or uncategorized prompts in target scope.

### Step 2: Categorize Prompts
For each prompt, determine appropriate category using decision tree.

### Step 3: Plan Moves and Updates
Create organization plan showing what moves where and why.

### Step 4: Execute Organization
Move files, update frontmatter, and validate results.

### Step 5: Generate Report
Document what was organized and final structure.

---

## Reasoning Process (for AI Agent)

Before organizing, the AI should:

1. **Inventory Current State**: What prompts exist and where? Which are uncategorized or misplaced?
2. **Understand Purpose**: What does each prompt do? Read prompt content to understand intent.
3. **Match to Category**: Which category best fits each prompt based on its primary purpose?
4. **Plan Moves**: What needs to move and what frontmatter updates are needed?
5. **Validate Organization**: Does final structure make sense? Are all prompts in logical homes?
6. **Generate Report**: Document actions taken and recommendations.

---

## Organization Principles

### 1. Category-Based Organization

**Standard Categories**:
- `agile/` - Agile development artifacts (epics, stories, features)
- `cicd/` - Continuous integration and deployment
- `code-quality/` - Code quality and refactoring
- `database-standards/` - Database development
- `documentation/` - Documentation tasks (XML docs, README, API docs)
- `git/` - Version control operations (branching, merging, commits)
- `migration/` - System migration work
- `package/` - Package management (NuGet, npm)
- `prompt/` - Prompt meta-operations (create, improve, organize)
- `rule-authoring/` - Rule creation and management
- `script/` - Script development (PowerShell, Python, bash)
- `setup/` - Project initialization and bootstrapping
- `technical/` - General technical tasks
- `technical-specifications/` - Domain documentation and specs
- `ticket/` - Ticket workflow management
- `unit-testing/` - Testing operations (coverage, generation, validation)

### 2. Special Folders

**Support Folders**:
- `exemplars/` - Example prompts showing patterns (permanent reference)
- `extracted/` - Prompts extracted from conversations (temporary staging)
- `templars/` - Template prompts for common patterns (reusable abstractions)

**Purpose**:
- Exemplars: Reference implementations demonstrating best practices
- Extracted: Staging area before categorization (should stay empty after organization)
- Templars: Reusable template abstractions

### 3. Naming Consistency

**File Naming**:
- Format: `action-subject.prompt.md`
- Example: `create-user-story.prompt.md`
- Avoid category prefix (folder already indicates category)

**Internal Name**:
- Must match filename (without `.prompt.md`)
- Example: `name: create-user-story`

---

## Categorization Decision Tree

```
Does it create/manage tickets? → ticket/
Does it work with Git? → git/
Does it create agile artifacts? → agile/
Does it improve code quality? → code-quality/
Does it handle testing? → unit-testing/
Does it manage documentation? → documentation/
Does it work with CI/CD? → cicd/
Does it manage prompts? → prompt/
Does it create rules? → rule-authoring/
Does it work with database? → database-standards/
Does it handle migration? → migration/
Does it manage packages? → package/
Does it create specs? → technical-specifications/
Is it about project setup? → setup/
Is it about scripts? → script/
Is it a general technical task? → technical/

None of above? → Create new category or put in technical/
```

---

## Examples (Few-Shot)

### Example 1: Complete Organization Workflow (5 Prompts)

**User Input**:
```
@organize-prompts extracted/
```

**AI Reasoning**:
- Need to organize 5 prompts in extracted/ folder
- Read each prompt to understand purpose
- Match to appropriate category using decision tree
- Plan file moves with proper renaming
- Update frontmatter category fields
- Validate after organization

**Scenario**: 5 prompts in `extracted/` folder need organization

**Prompts to Organize**:
```
extracted/
├── check-test-coverage.md
├── create-git-branch.md
├── improve-documentation.md
├── validate-spec.md
└── refactor-legacy-code.md
```

**Step 1: Analysis**

Reading prompt contents and determining categories:

1. **check-test-coverage.md**
   - **Purpose**: Analyze test coverage percentage and identify gaps
   - **Primary Function**: Testing operations
   - **Decision Tree Match**: "Does it handle testing?" → YES
   - **→ Category**: `unit-testing/`
   - **New Name**: `analyze-test-coverage.prompt.md`

2. **create-git-branch.md**
   - **Purpose**: Create branch following naming conventions
   - **Primary Function**: Git version control
   - **Decision Tree Match**: "Does it work with Git?" → YES
   - **→ Category**: `git/`
   - **New Name**: `create-branch.prompt.md`

3. **improve-documentation.md**
   - **Purpose**: Enhance XML documentation quality
   - **Primary Function**: Documentation improvement
   - **Decision Tree Match**: "Does it manage documentation?" → YES
   - **→ Category**: `documentation/`
   - **New Name**: `improve-xml-documentation.prompt.md`

4. **validate-spec.md**
   - **Purpose**: Validate technical specification completeness
   - **Primary Function**: Technical specification validation
   - **Decision Tree Match**: "Does it create specs?" → YES
   - **→ Category**: `technical-specifications/`
   - **New Name**: `validate-specification.prompt.md`

5. **refactor-legacy-code.md**
   - **Purpose**: Refactor code for clean code principles
   - **Primary Function**: Code quality improvement
   - **Decision Tree Match**: "Does it improve code quality?" → YES
   - **→ Category**: `code-quality/`
   - **New Name**: `refactor-for-clean-code.prompt.md`

**Step 2: Organization Plan**

```markdown
## Organization Plan

### Prompts to Move (5 total)

1. `extracted/check-test-coverage.md` 
   → `unit-testing/analyze-test-coverage.prompt.md`
   **Reason**: Primary purpose is testing coverage analysis

2. `extracted/create-git-branch.md`
   → `git/create-branch.prompt.md`
   **Reason**: Git version control operation

3. `extracted/improve-documentation.md`
   → `documentation/improve-xml-documentation.prompt.md`
   **Reason**: Documentation improvement task

4. `extracted/validate-spec.md`
   → `technical-specifications/validate-specification.prompt.md`
   **Reason**: Technical specification validation

5. `extracted/refactor-legacy-code.md`
   → `code-quality/refactor-for-clean-code.prompt.md`
   **Reason**: Code quality refactoring

### Actions Required
- Move 5 files to appropriate categories
- Rename files with `.prompt.md` extension
- Update frontmatter category fields in all 5
- Validate organized prompts
```

**Step 3: Execute Moves** (PowerShell commands):
```powershell
Move-Item "extracted/check-test-coverage.md" `
          "unit-testing/analyze-test-coverage.prompt.md"

Move-Item "extracted/create-git-branch.md" `
          "git/create-branch.prompt.md"

Move-Item "extracted/improve-documentation.md" `
          "documentation/improve-xml-documentation.prompt.md"

Move-Item "extracted/validate-spec.md" `
          "technical-specifications/validate-specification.prompt.md"

Move-Item "extracted/refactor-legacy-code.md" `
          "code-quality/refactor-for-clean-code.prompt.md"
```

**Step 4: Update Frontmatter** (Example for one file):
```markdown
Before (check-test-coverage.md):
---
name: check-test-coverage
description: "Check test coverage"
---

After (analyze-test-coverage.prompt.md):
---
name: analyze-test-coverage
description: "Please analyze unit test coverage and identify gaps"
category: unit-testing
tags: testing, coverage, analysis, quality, gaps
argument-hint: "File or folder path to analyze"
---
```

**Step 5: Validate**:
```
validate-prompt.prompt.md unit-testing/analyze-test-coverage.prompt.md
✅ PASS (95%)

validate-prompt.prompt.md git/create-branch.prompt.md
✅ PASS (92%)

[All 5 prompts validated successfully]
```

**Final Structure**:
```
.cursor/prompts/
├── unit-testing/analyze-test-coverage.prompt.md ✅
├── git/create-branch.prompt.md ✅
├── documentation/improve-xml-documentation.prompt.md ✅
├── technical-specifications/validate-specification.prompt.md ✅
├── code-quality/refactor-for-clean-code.prompt.md ✅
└── extracted/ [empty - all organized] ✅
```

**Organization Report**:
```markdown
# Prompt Organization Report

**Date**: 2025-12-08
**Scope**: extracted/ folder

## Summary
- **Total prompts analyzed**: 5
- **Successfully organized**: 5
- **Categories used**: 5 (unit-testing, git, documentation, technical-specifications, code-quality)
- **Validation**: All prompts pass quality checks

## Actions Taken
1. Moved 5 prompts from extracted/ to appropriate categories
2. Renamed all files with `.prompt.md` extension
3. Updated frontmatter (category, tags, argument-hint) in all 5
4. Validated all organized prompts

## Final State
- ✅ extracted/ folder is empty (all prompts organized)
- ✅ All prompts in appropriate category folders
- ✅ All prompts pass validation checks
```

### Example 2: Quick Single-Prompt Organization

**User Input**:
```
New prompt in extracted/ called "generate-unit-tests.md" needs organization
```

**AI Reasoning**:
- Single prompt to organize
- Read content to understand it generates unit tests
- Decision tree: "Does it handle testing?" → YES → unit-testing/
- Simple rename and frontmatter update

**Expected Output**:
```markdown
## Quick Organization

**Prompt**: `extracted/generate-unit-tests.md`
**Purpose**: Generate unit tests for untested code
**Category Match**: unit-testing/ (handles testing operations)

**Action**: 
Move to: `unit-testing/generate-unit-tests.prompt.md`

**PowerShell Command**:
```powershell
Move-Item "extracted/generate-unit-tests.md" `
          "unit-testing/generate-unit-tests.prompt.md"
```

**Frontmatter Update**:
Add category field: `category: unit-testing`

**Validation**: Run `validate-prompt.prompt.md unit-testing/generate-unit-tests.prompt.md`

✅ Organization complete
```

---

## Expected Output

```markdown
## Organization Plan

### Uncategorized Prompts Found
1. `extracted/prompt1.md` → Suggested: `category1/`
   - **Reason**: [Why this category]
2. `extracted/prompt2.md` → Suggested: `category2/`
   - **Reason**: [Why this category]

### Miscategorized Prompts
1. `wrong-category/prompt3.prompt.md` → Move to: `correct-category/`
   - **Reason**: [Why it should move]

### New Categories Needed (if applicable)
- `new-category/` - For [purpose]

### Actions

#### Phase 1: Move Files
[PowerShell commands to move files]

#### Phase 2: Update Metadata
[List of files needing frontmatter updates with specific changes]

#### Phase 3: Validation
[Validation checks to run]

## Validation Checklist

After organization:
- [ ] All prompts in appropriate categories
- [ ] No prompts in extracted/ (or all are WIP)
- [ ] Category folders have consistent naming
- [ ] All prompts pass validation
- [ ] INDEX files updated (if they exist)
```

---

## Organization Checklist

- [ ] Inventory completed (all prompts found and read)
- [ ] All prompts categorized using decision tree
- [ ] Files moved to correct folders
- [ ] Files renamed with `.prompt.md` extension
- [ ] Frontmatter category fields updated
- [ ] All prompts validated
- [ ] No duplicates between folders
- [ ] Special folders cleaned up (extracted/ empty)
- [ ] Documentation updated (if INDEX files exist)

---

## Best Practices

### DO
- ✅ Keep categories focused and clear
- ✅ Use existing categories when possible
- ✅ Update frontmatter when moving files
- ✅ Rename files with `.prompt.md` extension
- ✅ Validate after moving
- ✅ Document organization decisions in report

### DON'T
- ❌ Create too many categories (use existing when possible)
- ❌ Put prompts in multiple categories (choose one primary)
- ❌ Leave extracted/ folder full indefinitely
- ❌ Forget to update category in frontmatter
- ❌ Break existing prompt references
- ❌ Skip validation after organizing

---

## Quality Criteria

- [ ] All prompts analyzed and categorized correctly
- [ ] File moves executed successfully
- [ ] Frontmatter updated with category field
- [ ] All organized prompts pass validation
- [ ] Organization report generated
- [ ] extracted/ folder cleaned (or only WIP remains)

---

## Usage

**Quick organization** (extracted folder):
```
@organize-prompts extracted/
```

**Full audit** (entire library):
```
@organize-prompts all --audit
```

**Check specific folder**:
```
@organize-prompts technical/
```

**Interactive mode**:
```
@organize-prompts --interactive
```

---

## Related Prompts

- `prompt/create-new-prompt.prompt.md` - Create properly categorized prompts from start
- `prompt/validate-prompt.prompt.md` - Validate prompts after organizing
- `prompt/improve-prompt.prompt.md` - Improve prompt quality
- `prompt/enhance-prompt.prompt.md` - Add advanced features to prompts
- `templars/prompt/prompt-quality-improvement-templar.md` - Structure for pre-validation fixes
- `exemplars/prompt/prompt-quality-improvement-exemplar.md` - Reference for quality bar

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt quality standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

## Extracted Patterns

This prompt demonstrates exceptional quality and has been extracted into:

**Templar**:
- `.cursor/prompts/templars/prompt/categorization-workflow-templar.md` - Abstract pattern for inventory → categorize → move → validate workflows

**Why Extracted**: Demonstrates outstanding organization workflow (4 phases: Inventory → Categorize → Move → Validate), comprehensive decision tree covering all categorization cases, batch operation patterns, metadata update guidance, and organization report generation.

**Reuse**: Use the templar when creating organization prompts for file systems, code restructuring, documentation categorization, artifact cleanup, or any migration/reorganization task where items need systematic categorization and movement.

---

## Organization Report Template

```markdown
# Prompt Organization Report

**Date**: YYYY-MM-DD
**Scope**: [Folder or 'All']

## Summary
- **Total prompts analyzed**: [N]
- **Properly organized**: [N]
- **Needing organization**: [N]
- **Categories used**: [N]

## Actions Taken
1. Moved [N] prompts to correct categories
2. Created [N] new categories (if any)
3. Updated [N] frontmatter fields
4. Cleaned [N] files from extracted/

## Current Structure
[Tree view of organized structure]

## Recommendations
1. [Recommendation]
2. [Recommendation]
```

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
