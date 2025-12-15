---
type: exemplar
artifact-type: prompt
demonstrates: ticket-catchup
domain: ticket workflow
quality-score: exceptional
version: 1.0.0
---

# Ticket Catch-up Exemplar

## Why This Is Exemplary
- Fast rehydration: minimal reading, maximal clarity
- Explicit blockers/unknowns, ordered next steps
- Calls out missing artifacts (timeline) instead of guessing

## Exemplar Content (abridged)
```markdown
# Catch Up on Ticket

Use to get current on a ticket after a pause.

## Required Context
- ticket ID
- context.md, progress.md (timeline.md optional)

## Process
1) Read context.md: current focus, components
2) Read progress.md (latest first): actions, decisions
3) Read timeline.md if present; note if absent
4) Summarize state, blockers, decisions, risks
5) Propose next 3 steps; flag unknowns/missing info

## Expected Output
- Catch-up summary (bullets)
- Blockers/unknowns
- Next 3 steps (ordered)
- Sources used; missing artifacts noted
```

## Example Output
```
Summary:
- Icing patterns identified; condensation targets chosen.
- Meta templars/exemplars created for enhance/improve/create.
Blockers: None; timeline.md not present.
Next Steps:
1) Finish ticket templars (status, catch-up, closure).
2) Add exemplars for ticket patterns.
3) Validate YAML and update references if needed.
Sources: context.md, progress.md (no timeline.md).
```

## Learning Points
- Lead with a short summary; keep history out
- Missing data is explicit; no inventions
- Next steps are concrete and ordered

## When to Reference
Use when resuming tickets or onboarding reviewers who need a crisp, source-backed snapshot and immediate plan.

