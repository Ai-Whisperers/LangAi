---
name: find-extraction-candidates
description: "Find artifacts that should be extracted into templars or exemplars for reuse"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, templars, exemplars, extraction, patterns, maintenance
argument-hint: "Root path to scan (e.g., .cursor/prompts, .cursor/rules, tickets/)"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Find Extraction Candidates

Identify artifacts likely to benefit from templar or exemplar extraction so `extract-templar-exemplar` can be applied efficiently.

## Purpose

Quickly surface high-value prompt/rule/ticket artifacts that should be turned into templars or exemplars, so downstream extractions stay focused on the best leverage points.

## Required Context

- Target root path(s) to scan (prompts, rules, tickets, docs, scripts)
- Extraction signals to prioritize (size, examples, pattern indicators)
- Access to `.cursor/scripts/housekeeping/find-extraction-candidates.ps1`

## Inputs

- **Targets**: One or more roots to scan (default: `.cursor/prompts`, `.cursor/rules`, `tickets/`)
- **Signals**: High line count, many examples, templar/exemplar language, stars/ratings, repeated separators, verbose reasoning
- **Thresholds**: Line and example thresholds (see script defaults or override)

## Reasoning Process (for AI Agent)

1. Confirm the target roots and thresholds to avoid scanning the wrong scope.
2. Interpret script output: rank by score and flag signals that justify extraction.
3. Classify each candidate with a clear rationale; prefer Both when structure and examples are both reusable.
4. Map each candidate to the correct destination (templar vs exemplar) and note any trimming needed.
5. Produce the report using the specified Output Format so follow-up work is actionable.

## Process

1. **Scan (fast)**
   - Run the script:

     ```powershell
     ./.cursor/scripts/housekeeping/find-extraction-candidates.ps1 `
       -Root ".cursor/prompts" `
       -MinLines 200 `
       -ExampleThreshold 5 `
       -AsJson
     ```

   - Repeat for rules or tickets if needed (adjust `-Root`).

2. **Triage Results**
   - Sort by score (script output) and check top candidates.
   - Validate signals: size, example density, templar/exemplar language, duplication of sections.

3. **Classify**
   - Mark each candidate: **Templar**, **Exemplar**, **Both**, or **Skip**.
   - Prefer **Both** when structure is reusable and implementation is exemplary.

4. **Plan Extraction**
   - For each candidate: define destination paths under `.cursor/prompts/templars/` or `.cursor/prompts/exemplars/` (or rules/tickets equivalents).
   - Note any trimming required in the source (move bulk examples to exemplar, keep concise pointers).

5. **Document Output**
   - Produce a concise report per Output Format.
   - Attach the script JSON/CSV snippet for traceability.

## Output Format

```markdown
## Extraction Candidates (Root: [ROOT])

| Rank | File | Lines | Examples | Signals | Recommendation | Notes |
|------|------|-------|----------|---------|----------------|-------|
| 1 | [path] | [n] | [n] | [e.g., stars, templar refs, dense examples] | [Templar/Exemplar/Both/Skip] | [Why] |

### Actions
- [path] → [templar/exemplar destination], trim sections [list]
- ...
```

## Validation Checklist

- [ ] Script executed on intended roots with thresholds recorded
- [ ] Top candidates reviewed (score rationale captured)
- [ ] Each candidate classified (Templar/Exemplar/Both/Skip) with reason
- [ ] Destinations selected using correct folders and naming conventions
- [ ] Trim plan noted (what to move out, what to keep)
- [ ] Report saved/linked for follow-up work

## Usage

```text
@find-extraction-candidates .cursor/prompts
@find-extraction-candidates .cursor/rules -MinLines 150 -ExampleThreshold 3
```

## Related Prompts

- `prompt/improve-prompt.prompt.md`
- `prompt/enhance-prompt.prompt.md`
- `housekeeping/validate-prompt-collections.prompt.md`

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc`
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc`
