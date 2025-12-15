---
name: find-condense-candidates
description: "Find prompts or rules that are too long or example-heavy and should be condensed"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, condensation, prompts, maintenance
argument-hint: "Root path to scan (e.g., .cursor/prompts, .cursor/rules, tickets/)"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Find Condense Candidates

Identify artifacts that have grown too large or verbose so they can be shortened with `condense-prompts`.

## Purpose

Surface prompts/rules that should be condensed by checking size, example density, code fences, and long lines, so trimming work targets the highest-value files first.

## Required Context

- Target root path(s) to scan (prompts/rules/tickets)
- Thresholds to use (lines, examples, code fences, long lines) or accept defaults
- Access to `.cursor/scripts/housekeeping/find-condense-candidates.ps1`

## Inputs

- **Targets**: One or more roots (default: `.cursor/prompts`)
- **Signals**: High line count, many examples, many code fences, numerous >120-char lines
- **Thresholds**: See script defaults or override via parameters

## Reasoning Process (for AI Agent)

1. Confirm scan roots and thresholds to avoid noise.
2. Run the script and capture ranked results.
3. For each top candidate, note which signals triggered and why condensation is warranted.
4. Map follow-up to `condense-prompts` (or templar/exemplar extraction if more appropriate).
5. Produce the report in the Output Format with clear rationales.

## Process

1. **Scan (fast)**
   - Run the script:
     ```powershell
     ./.cursor/scripts/housekeeping/find-condense-candidates.ps1 `
       -Root ".cursor/prompts" `
       -MinLines 160 `
       -ExampleThreshold 5 `
       -CodeBlockThreshold 4 `
       -LongLineThreshold 12 `
       -AsJson
     ```
   - Add `-IncludeRules` or `-IncludeTickets` if scanning rules/tickets.

2. **Triage Results**
   - Sort by score, then lines.
   - Validate signals: size, example density, code fences, long-line count.

3. **Decide Action**
   - Mark each candidate: **Condense**, **Extract to Exemplar/Templar**, or **Skip**.
   - Prefer **Condense** when the issue is verbosity, not structure duplication.

4. **Plan Condensation**
   - Choose whether to keep inline examples (≤5) or move to exemplar.
   - Capture target paths for any extracted exemplar/templar.

5. **Document Output**
   - Use the Output Format so follow-up work is actionable.

## Output Format

```markdown
## Condense Candidates (Root: [ROOT])

| Rank | File | Lines | Examples | CodeFences | LongLines | Score | Signals | Recommendation | Notes |
|------|------|-------|----------|------------|-----------|-------|---------|----------------|-------|
| 1 | [path] | [n] | [n] | [n] | [n] | [n] | [signals] | [Condense/Extract/Skip] | [Why] |

### Actions
- [path] → Condense (keep 3–5 examples; move overflow to exemplar)
- [path] → Extract exemplar for examples; condense reasoning sections
```

## Validation Checklist

- [ ] Script executed on intended roots; thresholds recorded
- [ ] Top candidates reviewed with signal rationale captured
- [ ] Each candidate classified (Condense/Extract/Skip) with reason
- [ ] Action plan noted (condense vs exemplar/templar path)
- [ ] Report saved/linked for follow-up work

## Usage

```text
@find-condense-candidates .cursor/prompts
@find-condense-candidates .cursor/rules -IncludeRules -MinLines 140
```

## Related Prompts

- `housekeeping/condense-prompts.prompt.md`
- `housekeeping/find-extraction-candidates.prompt.md`
- `housekeeping/extract-templar-exemplar.prompt.md`

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc`
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc`

