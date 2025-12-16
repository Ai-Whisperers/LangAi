---
id: templar.progress.v1
kind: templar
version: 1.0.0
description: Structure template for progress.md files
implements: progress.append
globs: ""
governs: ""
requires: []
provenance: { owner: team-ticket, last_review: 2025-12-06 }
---

# {{ticket_id}} Progress Log

## {{YYYY-MM-DD}} - {{Milestone/Summary}}

**Time**: {{timestamp}}
**Status**: {{status}}

### Actions
- {{action_1}}
- {{action_2}}

### Decisions
- {{decision_1}}

### Findings
- {{finding_1}}

### Validation
- {{validation_step_1}}: {{result}}
