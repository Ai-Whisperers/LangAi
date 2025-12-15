---
id: templar.recap.v1
kind: templar
version: 1.0.0
description: Template structure for recap.md files - ticket outcomes and learnings summary
globs: ""
governs: ""
implements: recap.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Recap

## Summary

{{recap_summary}}

## What Was Accomplished

{{#accomplishments}}
- {{accomplishment}}
{{/accomplishments}}

## How It Was Accomplished

{{#approaches}}
- {{approach_description}}
{{/approaches}}

## Key Learnings

{{#learnings}}
- {{learning}}
{{/learnings}}

## What's Next

{{#follow_ups}}
- {{follow_up_action}}
{{/follow_ups}}

## Value Delivered

**Business Impact**: {{business_impact}}

**Technical Impact**: {{technical_impact}}

## Success Criteria Assessment

{{#success_criteria}}
- [ ] {{criterion}} - {{status}}
{{/success_criteria}}

## Recommendations

{{#recommendations}}
- {{recommendation}}
{{/recommendations}}

