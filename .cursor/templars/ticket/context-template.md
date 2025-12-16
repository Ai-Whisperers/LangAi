---
id: templar.context.v1
kind: templar
version: 1.0.0
description: Structure template for context.md files
implements: context.update
globs: ""
governs: ""
requires: []
provenance: { owner: team-ticket, last_review: 2025-12-06 }
---

# {{ticket_id}} Context

## Current State

**Status**: {{Active | Paused | Blocked | Review | Complete}}
**Last Updated**: {{timestamp}}

{{current_state_summary}}

## Focus Areas

- [ ] {{focus_area_1}}
- [ ] {{focus_area_2}}

## Immediate Next Steps

1. {{next_step_1}}
2. {{next_step_2}}

## Open Questions / Blockers

- {{question_or_blocker_1}}

## Recent Decisions

- {{decision_1}}

## Environment State

- **Branch**: {{git_branch}}
- **Last Commit**: {{commit_hash}}
- **Build Status**: {{passing | failing}}
