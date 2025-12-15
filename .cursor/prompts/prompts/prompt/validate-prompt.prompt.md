---
name: validate-prompt
description: "Please validate a prompt file against Prompt Registry format and quality standards"
category: prompt
tags: prompts, validation, quality-check, standards, compliance
argument-hint: "Prompt file path"
templar: .cursor/prompts/templars/prompt/multi-level-validation-templar.md
exemplar: .cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Validate Prompt

Please perform comprehensive validation of a prompt file against Prompt Registry format requirements and quality standards.

**Pattern**: Multi-Level Validation Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Essential for ensuring prompt quality and standards compliance  
**Use When**: Before committing new prompts, after changes, or for quality audits

---

## Purpose

This prompt checks prompts for format compliance, naming conventions, quality standards, and best practices. Use this before committing new prompts or after making changes to ensure they meet all requirements.

Provides:
- Objective pass/fail determination
- Weighted quality scoring across 4 levels
- Specific fix recommendations with examples
- Prioritized issues (errors before warnings)

---

## Required Context

- **Prompt File**: Path to `.prompt.md` file to validate
- **Validation Standards**: Access to prompt creation and registry integration rules
- **YAML Parser**: Ability to parse and validate YAML frontmatter

---

## Process

Follow these steps to validate a prompt:

### Step 1: Parse Prompt File
Load and parse the prompt file including frontmatter and content.

### Step 2: Check Format Compliance
Validate YAML frontmatter structure and required fields (Level 1).

### Step 3: Check Naming Conventions
Verify filename matches name field and follows kebab-case (Level 2).

### Step 4: Assess Quality Standards
Check description quality, tags, content structure (Level 3).

### Step 5: Evaluate Best Practices
Review reusability, OPSEC, related references (Level 4).

### Step 6: Calculate Score and Generate Report
Compute weighted score, determine status, provide recommendations.

---

## Reasoning Process (for AI Agent)

Before validating, the AI should:

1. **Parse Structure**: Can the file be parsed correctly? Is YAML frontmatter valid?
2. **Check Required Elements**: Are all mandatory fields present (`name`, `description`)?
3. **Assess Quality**: Does it meet quality standards across 4 levels?
4. **Prioritize Issues**: Errors before warnings before suggestions (ERR
OR > WARNING > INFO)
5. **Calculate Score**: Weight checks appropriately (40% format, 20% naming, 30% quality, 10% best practices)
6. **Determine Status**: PASS (≥90%, zero errors), WARNING (70-89% or warnings only), FAIL (<70% or has errors)

---

## Quality Score Calculation

**Scoring Method**:
- Each validation level has weighted checks
- **Level 1 (Format)**: Critical - 40% weight (frontmatter, required fields)
- **Level 2 (Naming)**: Important - 20% weight (kebab-case, descriptive)
- **Level 3 (Quality)**: Important - 30% weight (description, tags, content)
- **Level 4 (Best Practices)**: Nice-to-have - 10% weight (reusability, OPSEC, references)

**Status Determination**:
- **PASS**: Score ≥ 90%, zero errors
- **WARNING**: Score 70-89% OR has warnings but no errors
- **FAIL**: Score < 70% OR has any errors

---

## Validation Checklist

### Level 1: Format Compliance (REQUIRED - 40% weight)

**Frontmatter Structure**:
- [ ] Valid YAML frontmatter present (--- delimiters)
- [ ] No JSON arrays (use YAML list format per EPP-192)
- [ ] Proper indentation (2 spaces)
- [ ] All strings properly quoted

**Required Fields**:
- [ ] `name`: Present and valid (kebab-case)
- [ ] `description`: Present and quoted string

**Recommended Fields**:
- [ ] `category`: Specified for organization
- [ ] `tags`: Comma-separated keywords present

**Content Structure**:
- [ ] Markdown body present after frontmatter
- [ ] H1 heading present
- [ ] Content is substantive (not just a title)

### Level 2: Naming Conventions (20% weight)

- [ ] Filename matches `name` field (name.prompt.md)
- [ ] Name is kebab-case (lowercase with hyphens)
- [ ] Name is descriptive and action-oriented
- [ ] Name avoids redundancy with category

### Level 3: Quality Standards (30% weight)

**Description Quality**:
- [ ] Clear and concise (one sentence)
- [ ] Action-oriented (starts with "Please" verb)
- [ ] Specific about what prompt does
- [ ] Properly quoted string

**Tags Quality**:
- [ ] Relevant to prompt purpose
- [ ] Specific (not too generic)
- [ ] Comma-separated format
- [ ] 3-6 tags optimal

**Content Quality**:
- [ ] Clear objective stated (Purpose section)
- [ ] Instructions are specific (Process or Instructions section)
- [ ] Examples provided where helpful (Few-Shot pattern)
- [ ] Output format specified (Expected Output section)
- [ ] Usage instructions included (Usage section)

### Level 4: Best Practices (10% weight)

- [ ] Reusable across similar scenarios
- [ ] Accepts variable inputs (argument-hint provided)
- [ ] Related prompts referenced (with `.prompt.md` extensions)
- [ ] Prerequisites documented (Required Context section)
- [ ] OPSEC clean (no sensitive info)

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md`

## Expected Output

```markdown
## Validation Report

**Status**: [PASS | FAIL | WARNING]

### ✅ Passed Checks
- [Check that passed with details]

### ⚠️ Warnings (Should Fix)
- **[Category]**: [Issue description]
  - **Fix**: [How to fix with specific steps]
  - **Example**: [Correct format]

### ❌ Errors (Must Fix)
- **[Category]**: [Issue description]
  - **Fix**: [How to fix with specific steps]
  - **Example**: [Correct format]

### 📊 Quality Score
- Format Compliance: [X/Y] ([percentage]%)
- Naming Conventions: [X/Y] ([percentage]%)
- Quality Standards: [X/Y] ([percentage]%)
- Best Practices: [X/Y] ([percentage]%)

**Overall**: [X/Y] ([percentage]%) - [Status text]

### 💡 Recommendations
1. [Priority] - [Specific improvement suggestion]
2. [Priority] - [Specific improvement suggestion]
```

---

## Severity Levels

- **ERROR** (❌): Must fix - prevents prompt from working or violates critical standards
- **WARNING** (⚠️): Should fix - affects quality but not core functionality
- **INFO** (ℹ️): Consider fixing - nice-to-have improvements

---

## Quality Criteria

- [ ] Validation report generated with clear status
- [ ] All 4 levels checked (Format, Naming, Quality, Best Practices)
- [ ] Issues categorized by severity (errors, warnings, info)
- [ ] Specific fix recommendations provided with examples
- [ ] Quality score calculated with breakdown
- [ ] Overall status determined objectively

---

## Usage

**Single file validation**:
```
@validate-prompt .cursor/prompts/category/my-prompt.prompt.md
```

**Batch validation** (folder):
```
@validate-prompt .cursor/prompts/category/*.prompt.md
```

**Or run validation script**:
```powershell
.\scripts\validate-all-prompts.ps1
```

---

## Related Prompts

- `prompt/improve-prompt.prompt.md` - Fix issues found by validation
- `prompt/enhance-prompt.prompt.md` - Add features after passing validation
- `prompt/create-new-prompt.prompt.md` - Create prompts that pass validation from start
- `templars/prompt/prompt-quality-improvement-templar.md` - Structure for fixing issues before validation
- `exemplars/prompt/prompt-quality-improvement-exemplar.md` - Reference improved prompt for quality bar

---

## Related Rules

- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format standards
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Content quality standards
- EPP-192 - YAML format standards (no JSON arrays)

---

## Extracted Patterns

This prompt demonstrates exceptional quality and has been extracted into:

**Templar**:
- `.cursor/prompts/templars/prompt/multi-level-validation-templar.md` - Abstract pattern for weighted validation with severity levels

**Why Extracted**: Demonstrates outstanding multi-level validation structure (4 levels with weights: 40%/20%/30%/10%), clear severity categorization (ERROR/WARNING/INFO), objective pass/fail determination based on weighted scoring, and actionable feedback with specific fix instructions and examples.

**Reuse**: Use the templar when creating validation prompts for code, documents, configurations, data, or any artifact requiring quality checks with prioritized feedback and objective scoring.

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)

