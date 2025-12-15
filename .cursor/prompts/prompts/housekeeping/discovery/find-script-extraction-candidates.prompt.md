---
name: find-script-extraction-candidates
description: "Find scripts that should be extracted into templars or exemplars"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags:
  - housekeeping
  - scripts
  - templars
  - exemplars
  - extraction
  - maintenance
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
  - .cursor/rules/scripts/core-principles-rule.mdc
---

# Find Script Extraction Candidates

Identify scripts that should become templars or exemplars so common patterns are reusable and duplication drops.

## Purpose

- Surface high-value scripts whose structure or implementation should be reused.
- Reduce duplication across PowerShell/Python automation.
- Prep inputs for extraction into templars/exemplars with clear destinations.

## Required Context

- Target root(s) to scan (e.g., `.cursor/scripts`, `scripts/`, `.github/workflows/`).
- Signals to prioritize (duplication, reusable scaffolding, repeated plumbing).
- Language focus (PowerShell, Python).

## Inputs

- **Targets**: One or more roots to scan.
- **Signals**:
  - Repeated scaffolding (argument parsing, logging, configuration).
  - Shared patterns across scripts (retry, pagination, API wrappers).
  - High line count or many similar functions.
  - Comments indicating “template”, “pattern”, or “reuse”.
  - Multiple variants of the same task across teams.
- **Thresholds**: Line-count and similarity thresholds (define before scanning).

## Reasoning Process (for AI Agent)

1. Confirm scope/roots and thresholds to avoid scanning the wrong area.
2. Rank candidates by reuse potential and duplication risk.
3. Distinguish **Templar** (structure/boilerplate) vs **Exemplar** (idiomatic full sample) vs **Both**.
4. Map each candidate to destination folders (templars vs exemplars) and note trim plan.
5. Produce report in the Output Format with rationale.

## Process

1. **Scan (fast)**
   - Traverse target roots; note large scripts and clusters of similar filenames.
   - Flag repeated helpers (config loading, logging, retry) that should be centralized.
2. **Detect Signals**
   - Look for near-duplicate functions across scripts.
   - Find TODOs mentioning “template”, “boilerplate”, “refactor later”.
   - Identify scripts that bundle multiple responsibilities that could be modularized.
3. **Triage**
   - Rank by reuse impact: frequency, breadth of applicability, maintenance cost.
   - Exclude one-off scripts tightly bound to a single workflow.
4. **Classify**
   - **Templar**: Good skeleton (parameters, logging, error handling) with replaceable business logic.
   - **Exemplar**: Clean, end-to-end implementation illustrating best practices.
   - **Both**: Strong skeleton plus strong idiomatic example; extract both views.
   - **Skip**: Legacy or highly specific; document why.
5. **Plan Extraction**
   - Define destinations (repo-specific templar/exemplar folders) and filenames.
   - Note what to trim (environment-specific config, secrets, org-specific IDs).
6. **Document Output**
   - Produce the table and action list per Output Format.

## Output Format

```markdown
## Script Extraction Candidates (Root: [ROOT])

| Rank | File | Lines | Signals | Recommendation | Notes |
|------|------|-------|---------|----------------|-------|
| 1 | [path] | [n] | [dup helpers, scaffold, comments] | [Templar/Exemplar/Both/Skip] | [Why] |

### Actions
- [path] → [templar/exemplar destination], trim [list], keep [list]
- ...
```

## Validation Checklist

- [ ] Targets and thresholds confirmed
- [ ] Signals collected (duplication, scaffold, reuse hints)
- [ ] Each candidate classified with rationale
- [ ] Destinations and trim plan defined
- [ ] Report generated in requested format

## Usage

```
@find-script-extraction-candidates scripts/
@find-script-extraction-candidates .cursor/scripts -MinLines 150
```

## Related Prompts

- `housekeeping/extract-templar-exemplar.prompt.md`
- `housekeeping/find-extraction-candidates.prompt.md`
- `script/validate-script-standards.prompt.md`

