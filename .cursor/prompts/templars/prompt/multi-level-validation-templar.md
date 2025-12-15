---
type: templar
applies-to: validation, quality-checking, compliance, audit, verification
pattern-name: multi-level-validation-checklist
version: 1.0.0
implements: prompt.validate
extracted-from: .cursor/prompts/prompt/validate-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/validate-prompt.prompt.md
---

# Multi-Level Validation Checklist Templar

## Pattern Purpose

This template provides a structured, weighted validation framework that categorizes checks by severity and calculates quality scores. It separates critical compliance from nice-to-have improvements, enabling clear pass/fail decisions with actionable feedback.

## When to Use

Use this pattern when creating validation/verification prompts for:
- **Code validation** - Linting, style, quality checks
- **Document validation** - Format, completeness, standards compliance
- **Configuration validation** - Settings, deployment configs, infrastructure-as-code
- **Data validation** - Schema compliance, business rules, integrity checks
- **Artifact validation** - Builds, packages, releases before publication

**Criteria for This Pattern**:
- ✅ Multiple validation criteria to check
- ✅ Different severity levels (critical vs nice-to-have)
- ✅ Need objective pass/fail determination
- ✅ Users need prioritized fix guidance
- ✅ Quality scoring helps track improvements

## Template Structure

```markdown
# Validate [Artifact Type]

Please perform comprehensive validation of [artifact] against [standards] requirements and quality standards.

## Purpose

This prompt checks [artifacts] for [compliance areas]. Use this [when to use it].

## Expected Output

This prompt will produce:
1. **Validation report** with pass/fail/warning status
2. **Categorized findings** (passed checks, warnings, errors)
3. **Quality score** across multiple dimensions
4. **Specific recommendations** for fixes with examples

## Reasoning Process

Before validating:
1. **[Reasoning Step 1]**: [What to check first]
2. **[Reasoning Step 2]**: [What to analyze]
3. **[Reasoning Step 3]**: [What standards to apply]
4. **[Reasoning Step 4]**: [How to prioritize issues]

## Quality Score Calculation

**Scoring Method**:
- Each validation level has weighted checks
- Level 1 ([Category Name]): [Importance] - [Weight]% weight
- Level 2 ([Category Name]): [Importance] - [Weight]% weight
- Level 3 ([Category Name]): [Importance] - [Weight]% weight
- Level 4 ([Category Name]): [Importance] - [Weight]% weight

**Status Determination**:
- **PASS**: Score ≥ [threshold]%, zero errors
- **WARNING**: Score [range]% OR has warnings but no errors
- **FAIL**: Score < [threshold]% OR has any errors

## Validation Checklist

### Level 1: [Critical Compliance Category] (REQUIRED)

**[Subcategory 1]**:
- [ ] [Critical check 1]
- [ ] [Critical check 2]
- [ ] [Critical check 3]

**[Subcategory 2]**:
- [ ] [Critical check 4]
- [ ] [Critical check 5]

**[Subcategory 3]**:
- [ ] [Critical check 6]
- [ ] [Critical check 7]

### Level 2: [Standard Requirements Category]

- [ ] [Standard check 1]
- [ ] [Standard check 2]
- [ ] [Standard check 3]
- [ ] [Standard check 4]

### Level 3: [Quality Standards Category]

**[Quality Aspect 1]**:
- [ ] [Quality check 1]
- [ ] [Quality check 2]
- [ ] [Quality check 3]

**[Quality Aspect 2]**:
- [ ] [Quality check 4]
- [ ] [Quality check 5]

**[Quality Aspect 3]**:
- [ ] [Quality check 6]
- [ ] [Quality check 7]

### Level 4: [Best Practices Category]

- [ ] [Best practice 1]
- [ ] [Best practice 2]
- [ ] [Best practice 3]
- [ ] [Best practice 4]
- [ ] [Best practice 5]

## Validation Process

1. **[Parse/Load]** - [What to parse/load]
2. **[Check Critical]** - [Required fields/structure]
3. **[Validate Standards]** - [Standard requirements]
4. **[Assess Quality]** - [Quality criteria]
5. **[Report]** - [Findings with severity]

## Output Format

```markdown
## Validation Report

**Status**: [PASS | FAIL | WARNING]

### ✅ Passed Checks
- [Check that passed]
- [Check that passed]

### ⚠️ Warnings
- **[Category]**: [Issue description]
  - **Fix**: [How to fix]
  - **Example**: [Correct format]

### ❌ Errors (Must Fix)
- **[Category]**: [Issue description]
  - **Fix**: [How to fix]
  - **Example**: [Correct format]
  - **Impact**: [Why this matters]

### 📊 Quality Score
- [Level 1 Name]: [X/Y] ([percentage]%)
- [Level 2 Name]: [X/Y] ([percentage]%)
- [Level 3 Name]: [X/Y] ([percentage]%)
- [Level 4 Name]: [X/Y] ([percentage]%)

**Overall**: [X/Y] ([percentage]%)

### 💡 Recommendations
1. [Specific improvement suggestion]
2. [Specific improvement suggestion]
3. [Specific improvement suggestion]
```

## Severity Levels

- **ERROR** (❌): Must fix - [what it blocks/breaks]
- **WARNING** (⚠️): Should fix - [what it affects]
- **INFO** (ℹ️): Consider fixing - [what it improves]

## Examples (Few-Shot)

### Example 1: All Checks Pass

**Input**: [Artifact description that passes all checks]

**Output**:
```markdown
## Validation Report

**Status**: PASS ✅

### ✅ Passed Checks
- [Specific check 1 passed]
- [Specific check 2 passed]
- [Specific check 3 passed]
- [Specific check 4 passed]
- [Specific check 5 passed]

### 📊 Quality Score
- [Level 1 Name]: [X/Y] (100%)
- [Level 2 Name]: [X/Y] (100%)
- [Level 3 Name]: [X/Y] (100%)
- [Level 4 Name]: [X/Y] (83%)

**Overall**: [23/24] (96%) - Excellent
```

### Example 2: Critical Errors Found (Must Fix)

**Input**: [Artifact description with critical errors]

**Output**:
```markdown
## Validation Report

**Status**: FAIL ❌

### ❌ Errors (Must Fix)
- **[Category]**: [Specific error]
  - **Fix**: [Exact steps to fix]
  - **Example**:
    ```[format]
    [Correct example]
    ```
  - **Impact**: [Why this is critical]

### ⚠️ Warnings
- **[Category]**: [Specific warning]
  - **Fix**: [How to improve]
  - **Example**: [Better approach]

### 📊 Quality Score
- [Level 1 Name]: [4/6] (67% - errors found)
- [Level 3 Name]: [5/8] (63% - warnings)

**Overall**: [9/24] (38%) - Must improve before use

### 💡 Priority Fixes
1. Fix [critical error 1] first - blocks [functionality]
2. Then address [warning 1] - improves [quality aspect]
```

### Example 3: Warnings Only (Should Fix)

**Input**: [Artifact description with warnings but no errors]

**Output**:
```markdown
## Validation Report

**Status**: WARNING ⚠️

### ✅ Passed Checks
- [Critical check 1] passed
- [Critical check 2] passed
- [Standard check 1] passed

### ⚠️ Warnings
- **[Category]**: [Issue description]
  - **Fix**: [How to address]
  - **Impact**: [Why it matters]
- **[Category]**: [Another issue]
  - **Fix**: [Specific guidance]

### 📊 Quality Score
- [Level 1 Name]: [6/6] (100%)
- [Level 2 Name]: [4/4] (100%)
- [Level 3 Name]: [7/8] (88%)
- [Level 4 Name]: [2/6] (33%)

**Overall**: [19/24] (79%) - Functional but should improve
```

## Customization Points

### Level Definitions
**Placeholders**: `[Critical Compliance Category]`, `[Standard Requirements Category]`, etc.  
**Guidance**: Define 4 validation levels that make sense for your domain:
- **Level 1**: What absolutely MUST be correct (blockers)
- **Level 2**: What should be correct (important but not blocking)
- **Level 3**: What indicates good quality (standards)
- **Level 4**: What represents best practices (nice-to-have)

### Weights
**Placeholders**: `[Weight]%`  
**Guidance**: Assign percentage weights summing to 100%. Typical:
- Critical: 40%
- Important: 20-25%
- Quality: 25-30%
- Best Practices: 10-15%

### Thresholds
**Placeholders**: `[threshold]%`, `[range]%`  
**Guidance**: Set pass/fail thresholds. Typical:
- PASS: ≥90% with zero errors
- WARNING: 70-89% OR has warnings only
- FAIL: <70% OR has any errors

### Checks
**Placeholders**: `[Critical check N]`, `[Standard check N]`, etc.  
**Guidance**: List specific checks for your artifact type. Be concrete, not vague.

### Examples
**Placeholders**: `[Artifact description]`  
**Guidance**: Provide 2-3 examples showing: all-pass, critical-fail, warning-only scenarios.

## Example Usage (Applying This Templar)

### Creating "Validate API Response" Prompt

**Level 1 (Critical)**: Valid JSON, required fields present  
**Level 2 (Standard)**: Field naming conventions, HTTP status codes  
**Level 3 (Quality)**: Schema compliance, business rules  
**Level 4 (Best Practice)**: Response timing, caching headers

**Weights**: 40% / 20% / 30% / 10%

**Result**: Validation prompt that fails on invalid JSON (critical), warns on poor naming (standard), scores quality on schema match, and suggests caching improvements (best practice).

## Related Templars

- `guided-creation-workflow-templar.md` - Use validation as Step 6
- `enhancement-workflow-templar.md` - Validation identifies enhancement needs
- `troubleshooting-guide-templar.md` - Validation errors feed into troubleshooting (if exists)

## Best Practices

### DO
- ✅ Separate critical (blocking) from nice-to-have (improvements)
- ✅ Provide specific fix instructions, not just "fix this"
- ✅ Include correct examples in error messages
- ✅ Calculate weighted scores for objective measurement
- ✅ Show passed checks, not just failures
- ✅ Prioritize fixes (errors before warnings)

### DON'T
- ❌ Make all checks same severity (loses prioritization)
- ❌ Give vague errors: "Invalid format" without details
- ❌ Skip examples in error messages
- ❌ Use arbitrary pass/fail without scoring
- ❌ Only show failures (acknowledge successes)
- ❌ Present errors in random order (prioritize)

## Success Metrics

Good application of this pattern achieves:
- **Clear Decisions**: Objective pass/fail based on scores and errors
- **Actionable Feedback**: Users know exactly what to fix and how
- **Prioritization**: Critical issues fixed first
- **Measurable Quality**: Scores track improvements over time
- **Completeness**: All validation aspects covered systematically

---

**Pattern Provenance**: Extracted from `validate-prompt.prompt.md` which demonstrates exceptional multi-level validation with weighted scoring, clear severity separation, and actionable feedback with examples.

