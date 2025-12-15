---
type: templar
artifact-type: prompt
pattern-name: ticket-activation
version: 1.0.0
applies-to: ticket prompts
---

# Ticket Activation Templar

## Pattern Purpose
Activate/resume a ticket safely: align on the correct ticket, set ACTIVE status, load context, and surface next steps without drift.

## When to Use
- Switching into a ticket
- Resuming after pause
- Confirming current ticket alignment before work

## Inputs
- Ticket ID
- Files: context.md, progress.md, timeline.md (if present)
- Optional: references.md for conversations

## Deterministic Steps
1) Validate ticket ID (matches current.md if present)  
2) Read context.md + progress.md (+ timeline.md if exists)  
3) Summarize current focus, blockers, last actions  
4) Set status ACTIVE and record switch-in note  
5) Propose next 3 steps, with owners if known  
6) Highlight missing artifacts (e.g., timeline absent)  

## Expected Output
- Brief status snapshot (focus, blockers, last action)
- Next 3 prioritized steps
- Sources cited (context/progress/timeline)
- Note any missing files/data

## Quality Criteria
- [ ] Confirms ticket alignment (current.md) or flags mismatch
- [ ] Cites sources used
- [ ] Next steps are specific/actionable
- [ ] Blockers called out if present
- [ ] No unnecessary verbosity

## Usage Example
```
@activate-ticket PROMPTS-EXTRACT
```

