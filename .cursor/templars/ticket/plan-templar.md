---
id: templar.plan.v1
kind: templar
version: 1.0.0
description: Template structure for plan.md files - defines ticket objectives, requirements, and implementation strategy
globs: ""
governs: ""
implements: plan.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Plan Template

## Objective

{{ticket_objective}}

## Requirements

{{#requirements}}
- {{requirement}}
{{/requirements}}

## Acceptance Criteria

{{#acceptance_criteria}}
- [ ] {{criterion}}
{{/acceptance_criteria}}

## Implementation Strategy

{{#implementation_steps}}
{{step_number}}. {{step_description}}
{{/implementation_steps}}

## Complexity Assessment

**Track**: {{complexity_track}}  
(Simple Fix | Complex Implementation)

**Rationale**: {{complexity_rationale}}

**Criteria Met**:
{{#criteria_met}}
- {{criterion}}
{{/criteria_met}}

## Status

{{status}}  
(Planning | Ready | In Progress | Complete)

## Testing Strategy

{{#testing_strategy}}
{{testing_approach}}
{{/testing_strategy}}

## Notes

{{#notes}}
- {{note}}
{{/notes}}

