---
id: templar.timeline.v1
kind: templar
version: 1.0.0
description: Structure template for timeline.md files
implements: timeline.track
globs: ""
governs: ""
requires: []
provenance: { owner: team-ticket, last_review: 2025-12-06 }
---

# {{ticket_id}} Timeline

## Conversation Timeline
- **{{YYYY-MM-DD_HH-MMZ}}**: {{filename}} - **{{TYPE}}** - {{description}}

## Git Commit Timeline
- **{{YYYY-MM-DD HH:MMZ}}**: `{{hash}}` - {{commit_message}}

## Daily Event Timeline

### {{YYYY-MM-DD}}
**{{HH:MM}}Z** - **{{Type}}** - {{Event Description}} ({{Source}})

## Daily Summary

### {{YYYY-MM-DD}} ({{Day Type}})
**Total Verified Events**: {{count}}
**Work Hours**: {{start_time}} to {{end_time}} ({{duration}})
**Key Milestones**:
- {{milestone_1}}

