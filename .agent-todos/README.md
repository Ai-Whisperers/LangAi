# Agent TODO System

**Purpose:** Break down project implementation into agent-ready, executable tasks.

## How to Use This System

### For Human Project Managers

1. **Review phase folders** to track overall progress
2. **Assign tasks** by updating task status in individual files
3. **Monitor completion** through status tracking
4. **Update estimates** based on actual implementation time

### For AI Agents

1. **Read phase README** to understand context
2. **Pick a task file** from the phase you're working on
3. **Follow step-by-step instructions** in the task
4. **Update status** as you progress through checkboxes
5. **Mark complete** when all acceptance criteria met

## Directory Structure

```
.agent-todos/
├── README.md                    # This file
├── phase-0/                     # Proof of Concept (Week 1)
│   ├── README.md               # Phase overview
│   ├── 01-setup-environment.md
│   ├── 02-api-integration.md
│   ├── 03-hello-research.md
│   └── 04-validation.md
├── phase-1/                     # Basic Research Loop (Weeks 2-3)
│   ├── README.md
│   ├── 01-state-management.md
│   ├── 02-langgraph-workflow.md
│   ├── 03-search-integration.md
│   ├── 04-extraction.md
│   ├── 05-quality-loop.md
│   └── 06-report-generation.md
├── phase-2/                     # Multi-Agent System (Weeks 4-6)
│   ├── README.md
│   ├── 01-supervisor-pattern.md
│   ├── 02-agent-base-class.md
│   ├── 03-deep-research-agent.md
│   ├── 04-financial-agent.md
│   ├── 05-market-analyst.md
│   ├── 06-competitor-scout.md
│   └── 07-synthesis.md
└── phase-3/                     # Production Features (Weeks 7-8)
    ├── README.md
    ├── 01-fastapi-setup.md
    ├── 02-websocket-streaming.md
    ├── 03-database-setup.md
    ├── 04-monitoring.md
    └── 05-deployment.md
```

## Task File Format

Each task file follows this structure:

```markdown
# Task: [Task Name]

**Phase:** [Phase Number]
**Estimated Time:** [Hours]
**Dependencies:** [List of prerequisite tasks]
**Status:** [ ] Not Started | [ ] In Progress | [x] Complete

## Context

[Why this task matters, how it fits into the bigger picture]

## Prerequisites

- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Implementation Steps

### Step 1: [Step Name]

**Goal:** [What this step achieves]

**Actions:**
- [ ] Specific action 1
- [ ] Specific action 2
- [ ] Specific action 3

**Code Example:**
\`\`\`python
# Example code to guide implementation
\`\`\`

**Verification:**
- [ ] Check 1
- [ ] Check 2

### Step 2: [Next Step]

[Repeat structure]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests pass
- [ ] Documentation updated

## Testing Instructions

\`\`\`bash
# Commands to test this implementation
\`\`\`

## Success Metrics

- **Performance:** [Target]
- **Quality:** [Target]
- **Cost:** [Target]

## Common Issues & Solutions

**Issue 1:** [Problem description]
- **Solution:** [How to fix]

**Issue 2:** [Problem description]
- **Solution:** [How to fix]

## Next Steps

After completing this task:
1. Update status to Complete
2. Move to [Next Task]
3. Update phase README with progress
```

## Status Tracking

### Status Indicators

- `[ ] Not Started` - Task hasn't been picked up
- `[~] In Progress` - Agent is actively working on this
- `[x] Complete` - All acceptance criteria met, tests passing
- `[!] Blocked` - Waiting on dependency or decision
- `[?] Need Help` - Agent needs human guidance

### Progress Updates

Agents should update:
1. **Task status** - At the top of each file
2. **Step checkboxes** - As actions complete
3. **Verification items** - After testing
4. **Acceptance criteria** - Before marking complete

## Best Practices

### For Agents

1. **Read thoroughly** before starting
2. **Follow steps sequentially** - Don't skip ahead
3. **Test frequently** - After each major step
4. **Document issues** - Add to "Common Issues" section
5. **Update status** - Keep the team informed
6. **Ask for help** - Use `[?]` status when stuck

### For Project Managers

1. **Keep tasks atomic** - Each file = one deliverable
2. **Update estimates** - Based on actual completion time
3. **Add examples** - Real code > pseudocode
4. **Review completions** - Verify acceptance criteria
5. **Unblock agents** - Respond quickly to `[?]` or `[!]` status

## Phase Progress Tracking

Current phase progress is tracked in each phase README:

- **Phase 0:** [0/4 tasks complete] (0%)
- **Phase 1:** [0/6 tasks complete] (0%)
- **Phase 2:** [0/7 tasks complete] (0%)
- **Phase 3:** [0/5 tasks complete] (0%)

**Overall Project:** 0/22 core tasks complete (0%)

## Quick Start for Agents

### Starting Phase 0

```bash
# 1. Navigate to phase
cd .agent-todos/phase-0

# 2. Read phase overview
cat README.md

# 3. Start with first task
# Open 01-setup-environment.md and follow steps

# 4. Update status as you progress
# Edit the file to check off boxes

# 5. Test your work
# Run the verification commands provided

# 6. Mark complete when done
# Change status to [x] Complete
```

## Support

- **Questions about tasks:** Check phase README for context
- **Technical blockers:** Mark task as `[!] Blocked` and document issue
- **Need clarification:** Mark as `[?] Need Help` and specify question
- **Found a bug in instructions:** Document in "Common Issues"

---

**Last Updated:** 2025-12-05
**Maintainer:** Project Lead
**Version:** 1.0
