---
type: templar
artifact-type: prompt
pattern-name: ticket-catchup
version: 1.0.0
applies-to: ticket prompts
---

# Ticket Catch-up Templar

## Pattern Purpose
Rehydrate context quickly after a pause: rebuild mental model, surface blockers, and set immediate next steps.

## When to Use
- Returning to a ticket after time away
- Onboarding a reviewer or pair partner

## Inputs
- Ticket ID
- Files: context.md, progress.md; optional timeline.md, references.md

## Deterministic Steps
1) Read context.md for current focus and components
2) Read progress.md (latest entries first) for recent actions/decisions
3) Read timeline.md if present for sequence; note if missing
4) Summarize: current state, blockers, decisions, risks
5) Propose next 3 steps; call out unknowns/missing artifacts

## Expected Output
- Catch-up summary (2–3 bullets)
- Blockers/unknowns
- Next 3 steps with priority
- Sources used; missing files noted

## Quality Criteria
- [ ] Sources cited; missing artifacts flagged
- [ ] Next steps specific and ordered
- [ ] Blockers/risks explicit
- [ ] Concise; no restating whole history

## Usage Example
```
@catchup-on-ticket PROMPTS-EXTRACT
```
