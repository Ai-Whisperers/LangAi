---
type: templar
artifact-type: prompt
pattern-name: ticket-closure
version: 1.0.0
applies-to: ticket prompts
---

# Ticket Closure Templar

## Pattern Purpose
Close a ticket cleanly: validate, document outcomes, and ensure traceability.

## When to Use
- Ticket work is complete and validated
- Preparing for final commit/review/recap

## Inputs
- Ticket ID
- Files: plan.md, context.md, progress.md; optional timeline.md, rca.md (if defect), recap.md

## Deterministic Steps
1) Validate completion: acceptance criteria met; no open blockers  
2) Summarize outcomes and evidence; ensure recap (and rca if applicable)  
3) Update timeline if needed; cite sources  
4) List final next steps (handoff, merge, release)  
5) Call out missing artifacts if any  

## Expected Output
- Completion statement with evidence sources
- What was accomplished; blockers resolved
- Required artifacts status (recap, rca, timeline)
- Final actions (commit/review/release) and owners

## Quality Criteria
- [ ] Acceptance criteria verified; evidence noted
- [ ] Recap present; rca if defect
- [ ] Timeline updated or noted missing
- [ ] Final steps actionable and assigned
- [ ] No invented status; missing items flagged

## Usage Example
```
@close-ticket PROMPTS-EXTRACT
```

