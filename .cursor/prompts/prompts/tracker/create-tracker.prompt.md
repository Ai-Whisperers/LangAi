---
name: create-tracker
description: "Please generate a tracker that sits between a TODO list and a progress report, auto-seeded from ticket evidence"
category: ticket
tags: ticket, tracker, setup, tasks
argument-hint: "Tracker filename (e.g., tracker.md) and sources to scan"
---

# Create Tracker (Tasks + Status)

Create a concise tracker that captures actionable tasks and status without becoming a verbose progress report. Use it when you need a structured list of work with checkboxes, priorities, and an upfront status snapshot.

---

## Purpose

- Build a lightweight, evidence-backed tracker for systematic work on a ticket.
- Provide a clear status snapshot (progress, blockers, next priority) without turning into a narrative progress log.
- Ensure every task traces to source evidence and is ready for multi-session continuation.

---

## Required Context

- **Tracker target**: `[TRACKER_FILE]` (e.g., `tracker.md`, `roadmap.md`)
- **Ticket folder**: `[TICKET_FOLDER]` (e.g., `tickets/EPP-1234/`)
- **Sources to mine**: `[SOURCE_FILES]` (plan.md, progress.md, context.md, timeline.md, requirements)
- **Goal/definition of done**: `[GOAL]` (e.g., “all critical tasks complete”, “reach 100% coverage”)

---

## Usage Modes

- **Basic**: Create a tracker from plan + progress  
  `/create-tracker tracker.md tickets/EPP-1234/ plan.md progress.md`

- **Comprehensive**: Include context/timeline for richer seeding  
  `/create-tracker tracker.md tickets/EPP-1234/ plan.md progress.md context.md timeline.md requirements.md`

- **Roadmap**: Use for higher-level cross-ticket tracking  
  `/create-tracker roadmap.md tickets/EPP-1234/ plan.md progress.md`

---

## Process

1. **Collect evidence**
   - Read `[SOURCE_FILES]` to pull objectives, acceptance criteria, open tasks, blockers, and recent progress.
   - Deduplicate tasks and normalize wording; keep links to their origin when useful.
2. **Classify and prioritize**
   - Assign each task a status: ✅ COMPLETE, 🔄 IN PROGRESS, ⏳ PENDING, ⏭️ SKIPPED/NOT NOW.
   - Group tasks into logical sections (e.g., Phases, Workstreams, Components) to keep the tracker scannable.
   - Note blockers separately with owner/next step.
3. **Build the tracker**
   - Include a header with Summary, Last Updated (UTC), Progress (% or counts), Next Priority, and Blockers.
   - Present tasks as checkboxes with priorities and short, verifiable descriptions.
   - Keep it lightweight—no narrative; reserve detail for progress.md.
4. **Validate**
   - Ensure every task traces back to a source (plan/progress/requirements).
   - Ensure no task is marked complete without evidence.
   - Confirm totals/percentages align with task counts.
5. **Output**
   - Provide the tracker in a fenced markdown block ready to write to `[TRACKER_FILE]`.
   - Provide a brief “Changes Applied” recap (added/merged tasks, inferred status) to explain how the tracker was built.

---

## Output Format

```markdown
# [TRACKER_FILE] — [GOAL]
Last Updated: 2025-12-09T00:00:00Z
Progress: [X%] ([done]/[total]) | Next Priority: [short list]
Blockers: [if any, else “None”]

## Phase/Workstream
- [ ] ⏳ [PRIORITY] Task description (source: plan.md §Acceptance Criteria)
- [ ] 🔄 [PRIORITY] Task description (source: progress.md @2025-12-09)
- [ ] ⏭️ [PRIORITY] Deferred task (reason)
- [x] ✅ [PRIORITY] Completed task (evidence)

## Blockers
- [BLOCKER] → Owner/Unblock step
```

---

## Usage

```text
/create-tracker tracker.md tickets/EPP-1234/ plan.md progress.md context.md
```

---

## Quality Checks

- [ ] Tasks are deduped, prioritized, and mapped to sources.
- [ ] Statuses use the standard set (✅ 🔄 ⏳ ⏭️) with evidence for ✅.
- [ ] Progress math matches counts; no silent status drift.
- [ ] Blockers and “Next Priority” are explicitly listed.
- [ ] Tracker remains concise (no progress-log prose).

---

## Examples

### Example 1: Basic Ticket Tracker

**Input**:  
`/create-tracker tracker.md tickets/EPP-1234/ plan.md progress.md`

**Expected Output (excerpt)**:

```markdown
# tracker.md — reach 100% coverage
Last Updated: 2025-12-09T00:00:00Z
Progress: 40% (2/5) | Next Priority: Add tests for ValidationService
Blockers: None

## Phase/Workstream
- [x] ✅ High Add unit tests for RepositoryBase (source: progress.md @2025-12-09)
- [ ] 🔄 High Add tests for ValidationService (source: plan.md §Acceptance Criteria)
- [ ] ⏳ Medium Add tests for ProfileService (source: plan.md §Acceptance Criteria)
- [ ] ⏭️ Low Defer UI smoke tests (reason: scheduled post-merge)
```

### Example 2: Roadmap Tracker

**Input**:  
`/create-tracker roadmap.md tickets/EPP-5555/ plan.md progress.md context.md`

**Expected Output (excerpt)**:

```markdown
# roadmap.md — stabilize release
Last Updated: 2025-12-09T00:00:00Z
Progress: 25% (1/4) | Next Priority: Finish migration tasks
Blockers: OAuth cert rotation pending

## Workstream: Migration
- [ ] 🔄 High Complete data migration scripts (source: progress.md @2025-12-08)
- [ ] ⏳ High Validate migrated data (source: plan.md §Acceptance Criteria)
- [x] ✅ Medium Prep migration dry run (source: progress.md @2025-12-07)
```

---

## Related Prompts

- `tracker/update-tracker.prompt.md` — Reconcile an existing tracker with new evidence.
- `ticket/resume-tracker-work.prompt.md` — Continue systematic work using an existing tracker.
- `ticket/check-status.prompt.md` — Summarize ticket/document status before or after tracker creation.

