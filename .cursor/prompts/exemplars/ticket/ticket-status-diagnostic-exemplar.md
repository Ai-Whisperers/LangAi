---
type: exemplar
artifact-type: prompt
demonstrates: ticket-status-diagnostic
domain: ticket workflow
quality-score: exceptional
version: 1.0.0
---

# Ticket Status Diagnostic Exemplar

## Why This Is Exemplary
- Pulls only from available sources; flags missing ones
- Delivers terse status + blockers + ordered next steps
- Cites sources for traceability

## Exemplar Content (abridged)
```markdown
# Check Ticket Status (Diagnostic)

Use to summarize a ticket from its docs.

## Required Context
- ticket ID
- context.md, progress.md (timeline.md optional)

## Process
1) Read context.md and progress.md (timeline.md if present)
2) Extract current focus, blockers, latest actions
3) Summarize status; list blockers; propose next 3 steps
4) Cite sources; note missing files

## Expected Output
- Status (1–2 sentences)
- Blockers (or “None”)
- Next 3 steps (ordered)
- Sources noted
```

## Example Output
```
Status: In progress on condensing prompts; icing patterns identified.
Blockers: None.
Next Steps:
1) Draft templars for status, catch-up, closure.
2) Add exemplars for ticket patterns.
3) Validate YAML and link paths.
Sources: context.md, progress.md (no timeline.md found).
```

## Learning Points
- Keep status tight; move details to sources
- Always cite sources; declare missing artifacts
- Next steps must be actionable and ordered

## When to Reference
Use as a model for lean, source-backed status checks before reviews or handoffs.
