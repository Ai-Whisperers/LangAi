---
id: templar.context.v1
kind: templar
version: 1.0.0
description: Template structure for context.md files - maintains current technical state and focus
globs: ""
governs: ""
implements: context.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Context

**Last Updated**: {{last_updated_timestamp}}

## Technical Background

{{technical_background}}

## Current Focus

{{current_focus}}

## Key Components

{{#key_components}}
- `{{component_name}}` - {{component_description}}
{{/key_components}}

## Outstanding Issues

{{#outstanding_issues}}
- **{{issue_type}}**: {{issue_description}}
{{/outstanding_issues}}

## Next Steps

{{#next_steps}}
{{step_number}}. {{action_description}}
{{/next_steps}}

## Active Constraints

{{#constraints}}
- {{constraint_description}}
{{/constraints}}

## Current Hypotheses

{{#hypotheses}}
- {{hypothesis_description}}
{{/hypotheses}}

