---
type: exemplar
artifact-type: prompt
demonstrates: prompt-creation
domain: prompt meta-work
quality-score: exceptional
version: 1.0.0
illustrates: prompt.create
use: critic-only
notes: "Pattern extraction only. Do not copy exemplar content into outputs."
extracted-from: .cursor/prompts/prompt/create-new-prompt.prompt.md
referenced-by:
  - .cursor/prompts/prompt/create-new-prompt.prompt.md
---

# Prompt Creation Exemplar

## Why This Is Exemplary
- Minimal, registry-ready YAML
- Clear purpose/scope and concise steps
- Short, targeted examples that match the expected output
- Quality checks mapped to correctness and clarity

## Exemplar Content (abridged)
```markdown
---
name: validate-openapi
description: "Please validate an OpenAPI spec for structure and linting issues"
category: api-testing
tags: api, openapi, validation
argument-hint: "Path or pasted OpenAPI YAML"
---

# Validate OpenAPI Spec

Use to quickly sanity-check an OpenAPI document for structural issues and common lint findings.

## Required Context
- OpenAPI YAML or JSON
- Optional: lint rule set

## Process
1) Load spec; fail fast on invalid YAML/JSON
2) Check top-level fields (info, paths, components)
3) Run lint rules (naming, response codes, schema refs)
4) Report issues with severities and fixes

## Examples
### Example 1: Happy Path
Input: minimal valid spec
Expected Output: PASS summary + zero issues

### Example 2: Edge (Missing Responses)
Input: spec missing 2xx/4xx on an operation
Expected Output: FAIL with two issues and suggested fixes

## Expected Output
- Pass/Fail summary
- Issues (if any) with severity, location, fix
- Counts: errors/warnings

## Quality Criteria
- [ ] YAML valid; polite description
- [ ] Process is 3–5 actionable steps
- [ ] Examples cover happy + edge
- [ ] Expected Output matches examples
- [ ] Tags specific; argument-hint present
```

## Learning Points
- Keep examples brief; show the format, not prose
- Output spec must mirror the example shape
- Quality criteria enforce the core promises

## When to Reference
Use this when designing new prompts to see a concise, production-ready structure that meets registry and quality standards without unnecessary bulk.
