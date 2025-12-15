---
type: exemplar
artifact-type: prompt
demonstrates: prompt-enhancement-workflow
domain: prompt meta-work
quality-score: exceptional
version: 1.0.0
illustrates: prompt.enhance
use: critic-only
notes: "Pattern extraction only. Do not copy exemplar content into outputs."
extracted-from: .cursor/prompts/prompt/enhance-prompt.prompt.md
referenced-by:
  - .cursor/prompts/prompt/enhance-prompt.prompt.md
---

# Prompt Enhancement Workflow Exemplar

## Why This Is Exemplary
- Shows end-to-end enhancement without bloat: clear inputs, decisioning, small targeted edits
- Keeps core value intact while adding only necessary structure, examples, and validation
- Demonstrates lean, YAML-compliant frontmatter and concise sections

## Key Quality Elements
1. Minimal, correct frontmatter (no optional noise)
2. Tight Purpose + When to Use combined; avoids “Effectiveness ⭐” fluff
3. Required Context is short and actionable
4. Process is 5 decisive steps, each outcome-oriented
5. Reasoning guidance is a checklist, not narrative
6. Examples: two focused scenarios (happy + edge), short and testable
7. Quality Criteria map to actual gaps being fixed

## Pattern Demonstrated
Apply the enhancement workflow to a working but thin prompt:
- Gap: missing examples and validation
- Action: add 2 examples, add concise Expected Output, add 5-item Quality Criteria
- Constraint: no extra horizontal rules or subjective ratings

## Exemplar Content (abridged)
```markdown
---
name: sample-api-validator
description: "Please validate an API response against schema and business rules"
category: api-testing
tags: api, validation, testing
argument-hint: "API response JSON or file path"
---

# Validate API Response (Enhanced)

Use when a JSON API response needs quick schema/business-rule validation.

## Required Context
- API response JSON
- Optional: schema definition, business rules

## Process
1) Parse response; fail fast on invalid JSON
2) Validate schema (required fields, types)
3) Validate business rules
4) Report findings with severities

## Examples
### Example 1: Valid
Input: minimal valid JSON  
Expected Output: PASS summary + checked items

### Example 2: Invalid
Input: missing field + bad type  
Expected Output: FAIL with two specific issues and severities

## Expected Output
- Pass/Fail header
- Issues (if any) with JSON path and severity
- Fix recommendations

## Quality Criteria
- [ ] YAML valid; no JSON arrays
- [ ] At least 1 happy + 1 edge example
- [ ] Expected Output lists pass/fail + issues + fixes
- [ ] Process steps actionable and minimal
- [ ] No redundant sections or star ratings
```

## Learning Points
- Enhancement is additive but minimal: add only what fixes the gaps
- Examples stay short; demonstrate format, not prose
- Quality checklist enforces the exact gaps you addressed

## When to Reference
Use as a reference when enhancing prompts that already work but need clarity, examples, or validation without growing large. Suitable for quick/medium/deep passes; scale the number of examples and checks to the gap, not habit.

