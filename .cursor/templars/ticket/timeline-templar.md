---
id: templar.timeline.v1
kind: templar
version: 1.0.0
description: Template structure for timeline.md files - timestamp-focused work event tracking
globs: ""
governs: ""
implements: timeline.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Timeline

## Conversation Timeline

{{#conversations}}
- **{{conversation_timestamp}}**: {{conversation_filename}} - **{{conversation_type}}** - {{conversation_description}}
{{/conversations}}

## Git Commit Timeline

{{#commits}}
- **{{commit_timestamp}}**: `{{commit_hash}}` - {{commit_message}}
{{/commits}}

## Daily Event Timeline

### {{event_date}}

{{#daily_events}}
**{{event_time}}** - **{{event_type}}** - {{event_description}}
{{/daily_events}}

## Daily Summary

### {{summary_date}} ({{work_type}})

**Total Verified Events**: {{event_count}}
**Work Hours**: {{start_time}} to {{end_time}} ({{duration}})

**Key Milestones**:
{{#milestones}}
- **{{milestone_time}}**: {{milestone_description}}
{{/milestones}}
