---
type: templar
artifact-type: prompt
pattern-name: ticket-status-diagnostic
version: 1.0.0
applies-to: ticket prompts
---

# Ticket Status Diagnostic Templar

## Pattern Purpose
Produce a concise, source-backed status snapshot from ticket artifacts, surfacing blockers and next actions.

## When to Use
- Need a fast, reliable status readout
- Before handoff, review, or planning

## Inputs
- Ticket ID
- Files: context.md, progress.md; optional timeline.md, references.md

## Deterministic Steps
1) Gather sources: context.md, progress.md, timeline.md (if present)
2) Extract: current focus, latest actions, blockers, decisions
3) Synthesize: status summary + blockers + next 3 steps
4) Cite sources used; note any missing artifacts

## Expected Output
- Status: 1–2 sentences
- Blockers: explicit or “None”
- Next 3 steps: specific, ordered
- Sources cited (context/progress/timeline)

## Quality Criteria
- [ ] Uses only available sources; missing files called out
- [ ] Status concise; blockers explicit
- [ ] Next steps actionable/ordered
- [ ] Sources cited for traceability
- [ ] No fluff or redundant sections

## Usage Example
```
@check-status PROMPTS-EXTRACT
```
