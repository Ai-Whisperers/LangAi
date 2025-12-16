---
id: templar.progress.v1
kind: templar
version: 1.0.0
description: Template structure for progress.md files - chronological log with append-only discipline
globs: ""
governs: ""
implements: progress.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Progress Log

## {{entry_date}} - {{entry_summary}}

**Time**: {{timestamp}}

**Action/Decision/Milestone**: {{entry_type_and_description}}

**Details**:
{{entry_details}}

**Links**:
{{#links}}
- {{link_description}}: {{link_reference}}
{{/links}}

**Outcome**:
{{entry_outcome}}

**Next Steps**:
{{#next_steps}}
- {{next_step}}
{{/next_steps}}
