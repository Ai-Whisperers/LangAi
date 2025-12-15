---
id: documentation.templar.index.v1
kind: documentation
version: 1.0.0
description: Index of Ticket Templars
provenance:
  owner: team-ticket
  last_review: 2025-12-06
---

# Ticket Templars Index

## Purpose

This index lists all templars (templates) used by ticket management rules. Templars define the structure and format of ticket documentation files.

## Ticket File Templars

### `templar.plan.v1`
**File**: `plan-templar.md`  
**Used by**: `rule.ticket.plan.v1`  
**Governs**: Structure of `plan.md` files  
**Sections**: Objective, Requirements, Acceptance Criteria, Implementation Strategy, Complexity Assessment, Status, Testing Strategy, Notes

### `templar.context.v1`
**File**: `context-templar.md`  
**Used by**: `rule.ticket.context.v1`  
**Governs**: Structure of `context.md` files  
**Sections**: Technical Background, Current Focus, Key Components, Outstanding Issues, Next Steps, Active Constraints, Current Hypotheses

### `templar.progress.v1`
**File**: `progress-templar.md`  
**Used by**: `rule.ticket.progress.v1`  
**Governs**: Structure of `progress.md` entries  
**Sections**: Entry date/summary, Time, Action/Decision/Milestone, Details, Links, Outcome, Next Steps

### `templar.timeline.v1`
**File**: `timeline-templar.md`  
**Used by**: `rule.ticket.timeline.v1`  
**Governs**: Structure of `timeline.md` files  
**Sections**: Conversation Timeline, Git Commit Timeline, Daily Event Timeline, Daily Summary

### `templar.recap.v1`
**File**: `recap-templar.md`  
**Used by**: `rule.ticket.recap.v1`  
**Governs**: Structure of `recap.md` files  
**Sections**: Summary, What Was Accomplished, How, Key Learnings, What's Next, Value Delivered, Success Criteria, Recommendations

### `templar.rca.v1`
**File**: `rca-templar.md`  
**Used by**: `rule.ticket.rca.v1`  
**Governs**: Structure of `rca.md` files  
**Sections**: Problem Statement, Impact Assessment, Timeline of Events, Investigation, Root Cause, Contributing Factors, Resolution, Prevention, Process Improvements, Lessons Learned

## Placeholder Syntax

All templars use Mustache-style placeholders:

- `{{variable}}` - Single value
- `{{#collection}}...{{/collection}}` - Repeated section
- `{{step_number}}.` - Numbered items

## Usage Pattern

1. Rule loads templar using `requires` field
2. Rule populates placeholder values from inputs
3. Rule generates or validates file structure against templar
4. Output file follows templar structure with actual content

## Related Rules

- `rule.authoring.templars-and-exemplars.v1` - Framework for templar creation
- `rule.ticket.overview.v1` - Ticket system overview

## Templar vs Template Files

**Templars** (`.cursor/templars/ticket/`):
- Formal structure definitions with front-matter
- Referenced by stable IDs in rule requires
- Version-controlled and managed

**Template Files** (`tickets/templates/`):
- User-facing example files
- May be copied as starting points
- Less formal, more practical examples

