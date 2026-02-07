---
type: exemplar
artifact-type: prompt
demonstrates: ticket-closure
domain: ticket workflow
quality-score: exceptional
version: 1.0.0
---

# Ticket Closure Exemplar

## Why This Is Exemplary
- Verifies acceptance criteria and artifacts before closure
- Provides evidence and final actions; flags missing pieces
- Keeps output concise and actionable

## Exemplar Content (abridged)
```markdown
# Close Ticket

Use to finalize a ticket with evidence and required artifacts.

## Required Context
- ticket ID
- plan.md, context.md, progress.md
- Optional: timeline.md, recap.md, rca.md (if defect)

## Process
1) Verify acceptance criteria and validation evidence
2) Confirm recap (and rca if defect); note if missing
3) Ensure timeline is updated; note if absent
4) Summarize accomplishments and blockers resolved
5) List final actions (commit/review/release) with owners

## Expected Output
- Completion statement with evidence sources
- Artifacts status: recap/rca/timeline (done/missing)
- Final actions and owners
- Blockers resolved or remaining (should be none)
```

## Example Output
```
Completion: Ready to close; criteria met; validation done.
Artifacts: recap not yet written; rca not needed; timeline missing (note).
Accomplishments: Prompt templars/exemplars created for meta + ticket flows.
Blockers: None.
Final Actions:
1) Write recap.md (owner: me).
2) Update timeline.md or note absence (owner: me).
3) Prep final commit/review (owner: me).
Sources: plan.md, progress.md, context.md.
```

## Learning Points
- Evidence before “done”; artifacts explicit (present/missing)
- Final actions are specific and assigned
- Missing items are noted, not invented

## When to Reference
Use when closing tickets to ensure validation, documentation, and final steps are complete and explicitly stated.
