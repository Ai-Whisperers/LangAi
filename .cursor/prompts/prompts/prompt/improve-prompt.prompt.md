---
name: improve-prompt
description: "Please improve an existing prompt according to prompt creation rules and best practices"
category: prompt
tags: prompts, improvement, quality, standards, best-practices
argument-hint: "Prompt file path or content"
templar: .cursor/prompts/templars/prompt/prompt-quality-improvement-templar.md
exemplar: .cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Improve Prompt

Please analyze and improve the provided prompt according to prompt creation rules and best practices.

**Pattern**: Quality Improvement Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Essential for systematic prompt optimization  
**Use When**: Prompt has issues, inconsistencies, or doesn't follow standards

---

## Purpose

This prompt identifies issues in existing prompts and provides concrete improvements with rationale. Use this when a prompt has problems that need fixing:
- Works but has issues (unclear instructions, missing examples, incomplete)
- Doesn't follow prompt creation standards
- Inconsistent format or structure
- Missing critical sections

This is the **first step** in prompt optimization - fix issues before enhancing with advanced features.

---

## Required Context

- **Prompt File**: Path to existing `.prompt.md` file or raw content to analyze
- **Standards**: Access to `.cursor/rules/prompts/prompt-creation-rule.mdc`
- **Registry Format**: Understanding of Prompt Registry `.prompt.md` format

---

## Process

Follow these steps to improve a prompt:

### Step 1: Read Prompt
Load the prompt file or content to analyze.

### Step 2: Analyze Quality
Review against 5 quality standards (Frontmatter, Structure, Clarity, Reusability, Documentation).

### Step 3: Identify Issues
Note specific problems with examples and severity (critical, important, nice-to-have).

### Step 4: Generate Improved Version
Create complete improved prompt fixing all issues.

### Step 5: Document Changes
Explain what was changed and why for traceability.

---

## Reasoning Process (for AI Agent)

Before improving, the AI should:

1. **Understand Intent**: What is this prompt trying to achieve? What's its core purpose?
2. **Identify Issues**: What prevents it from being maximally effective?
3. **Prioritize Fixes**: Critical issues first (broken functionality, missing required sections), then improvements (clarity, examples)
4. **Preserve Value**: Keep what works well, improve what doesn't - don't throw away good content
5. **Apply Standards**: Ensure compliance with prompt-creation-rule.mdc and prompt-registry-integration-rule.mdc
6. **Validate**: Check that improved version actually fixes issues and doesn't break existing functionality

---

## What to Analyze

Review the prompt against these quality standards:

### 1. Frontmatter Quality
- **Required fields**: `name`, `description` present
- **Description quality**: Clear, concise, action-oriented, starts with "Please"
- **Tags**: Relevant, specific keywords (3-6 tags recommended)
- **Argument hints**: Present if prompt expects input
- **Category**: Specified for organization
- **YAML format**: Proper format, no JSON arrays (EPP-192 compliance)

### 2. Content Structure
- **Clear objective**: What the prompt accomplishes (Purpose section)
- **Context setting**: Sufficient background information (Required Context)
- **Instructions**: Specific, actionable steps (Process or Instructions section)
- **Examples**: Included where helpful (Few-Shot pattern)
- **Constraints**: Limitations clearly stated
- **Reasoning Process**: Guidance for AI agent behavior

### 3. Clarity & Specificity
- **Language**: Clear, unambiguous instructions
- **Scope**: Well-defined boundaries
- **Output format**: Expected result format specified (Expected Output section)
- **Edge cases**: Addressed where relevant

### 4. Reusability
- **Generic enough**: Works across similar scenarios
- **Parameterized**: Accepts variable inputs via argument-hint
- **Modular**: Can be composed with other prompts

### 5. Documentation Quality
- **Usage examples**: Shows how to use the prompt (Usage section)
- **Prerequisites**: Required context documented
- **Related prompts**: References to complementary prompts with `.prompt.md` extensions
- **Related rules**: References to applicable rule files

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md`

## Quality Criteria

- [ ] Branch name follows naming convention (type/TICKET-ID-description)
- [ ] Ticket ID format validated
- [ ] Branch type appropriate (feature, fix, hotfix)
- [ ] Description is kebab-case
- [ ] Remote branch created and tracked

---

## Usage

```
@create-branch EPP-192 "Add XML documentation validation"
```

---

## Related Prompts

- `git/validate-branch-name.prompt.md` - Validate branch naming before creation
- `git/switch-branch.prompt.md` - Switch between existing branches
- `git/delete-branch.prompt.md` - Clean up completed branches

---

## Related Rules

- `.cursor/rules/git/branch-naming-rule.mdc` - Branch naming conventions
- `.cursor/rules/git/branch-structure-rule.mdc` - Branch types and purposes
```

**Changes Made**:
1. **Enhanced frontmatter**: Added polite "Please", category, better tags, argument-hint
2. **Added Purpose section**: Explains when/why to use
3. **Added Process section**: 5-step user workflow
4. **Added Required Context**: What user needs to provide
5. **Added Expected Output**: What AI will produce
6. **Improved Instructions**: Specific steps with git commands
7. **Added complete examples**: 2 Few-Shot examples with input → output
8. **Added Quality Criteria**: Validation checklist
9. **Added Usage section**: How to invoke
10. **Added Related Prompts**: References to complementary prompts with `.prompt.md` extensions
11. **Added Pattern metadata**: Pattern/Effectiveness/Use When line

**Result**: Improved from minimal to production-ready with complete structure, examples, and validation.

### Example 2: Missing Examples Fix

**User Input**:
```
Prompt has no examples section, instructions are clear otherwise
```

**Before**:
```markdown
## Instructions
1. **Scan code** for naming convention violations
2. **Identify** functions exceeding 50 lines
3. **Check** for DRY principle violations
4. **Report** findings with specific line numbers
```

**Issue**: Instructions clear but no concrete examples showing what output looks like.

**After**:
```markdown
## Instructions
1. **Scan code** for naming convention violations
2. **Identify** functions exceeding 50 lines
3. **Check** for DRY principle violations
4. **Report** findings with specific line numbers

## Examples

### Example 1: Code Quality Issues Found

**Input**: `PaymentService.cs`

**Expected Output**:
```
## Code Quality Report

### Naming Convention Violations
- Line 23: Variable `temp_val` should be `tempValue` (camelCase)
- Line 45: Method `process_payment` should be `ProcessPayment` (PascalCase)

### Long Functions
- Lines 67-145: Method `ProcessTransaction` (78 lines, threshold: 50)
  Recommendation: Extract validation logic to separate method

### DRY Violations
- Lines 12-18 duplicated in lines 89-95
  Recommendation: Extract common logic to `ValidateInput()` method
```
```

**Changes Made**:
- Added Examples section with 1 complete scenario
- Showed realistic output format
- Demonstrated findings reporting style

---

## Output Format

```markdown
## Analysis

### Strengths
- [What the prompt does well]

### Issues Found
1. **[Issue Category]**: [Specific problem]
2. **[Issue Category]**: [Specific problem]

### Improvement Opportunities
- [Suggestions for enhancement]

## Improved Version

[Complete improved prompt content]

## Changes Made
1. [Change 1 with rationale]
2. [Change 2 with rationale]
```

---

## Quality Criteria

- [ ] All critical issues fixed (broken functionality, missing required sections)
- [ ] Structure follows prompt creation standards
- [ ] Examples are complete (input → reasoning → output)
- [ ] Related prompts referenced with `.prompt.md` extensions
- [ ] YAML frontmatter properly formatted
- [ ] Description is polite ("Please...")
- [ ] Improved version tested and works

---

## Usage

**With file path**:
```
@improve-prompt .cursor/prompts/category/my-prompt.prompt.md
```

**With inline content**:
```
@improve-prompt

[Paste prompt content here]
```

---

## Related Prompts

- `prompt/enhance-prompt.prompt.md` - Add advanced features after fixing issues
- `prompt/validate-prompt.prompt.md` - Check quality after improvements
- `prompt/create-new-prompt.prompt.md` - Create prompts from scratch
- `templars/prompt/prompt-quality-improvement-templar.md` - Reusable improvement flow
- `exemplars/prompt/prompt-quality-improvement-exemplar.md` - Reference improved prompt

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

## Extracted Patterns

- **Templar**: `.cursor/prompts/templars/prompt/prompt-quality-improvement-templar.md`
- **Exemplar**: `.cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md`

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket - meta-improvement!)

