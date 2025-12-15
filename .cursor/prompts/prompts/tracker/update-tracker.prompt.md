---
name: update-tracker
description: "Please update a tracker by reconciling tasks with the latest ticket evidence and status changes"
category: ticket
tags: ticket, tracker, update, reconciliation
argument-hint: "Tracker filename (e.g., tracker.md) plus sources to reconcile"
---

# Update Tracker (Reconcile Tasks & Status)

Use this to refresh an existing tracker so it reflects the latest work: detect completions, add new tasks, surface blockers, and keep progress math accurate.

---

## Purpose

- Keep an existing tracker aligned with current reality by reconciling against fresh evidence.
- Prevent silent status drift by requiring evidence-backed ✅ and explicit ⏭️ for deferrals.
-,Maintain an accurate snapshot (progress, blockers, next priorities) ready for the next working session.

---

## Usage Modes

- **Quick sync** (latest progress only):  
  `/update-tracker tracker.md progress.md`

- **Full reconciliation** (plan + progress + timeline):  
  `/update-tracker tracker.md progress.md plan.md timeline.md`

- **Windowed sync** (recent activity only):  
  `/update-tracker tracker.md progress.md plan.md timeline.md "since last commit"`

---

## Required Context

- **Tracker file**: `[TRACKER_FILE]` (e.g., `tracker.md`, `roadmap.md`)
- **Evidence sources**: `[SOURCE_FILES]` (progress.md entries, plan.md changes, timeline.md, code/task lists)
- **Session goal**: `[GOAL]` (e.g., “sync with today’s work”, “push to 100%”)
- **Time window (optional)**: `[SINCE]` (e.g., “last 2 days”, “since last commit”)

---

## Process

1. **Load current tracker**
   - Parse statuses (✅ 🔄 ⏳ ⏭️), priorities, blockers, and progress totals.
2. **Gather new evidence**
   - Scan `[SOURCE_FILES]` for new tasks, completions, and blockers since `[SINCE]` (or most recent entries).
   - Normalize task wording; link to evidence where useful (file/section/timestamp).
3. **Reconcile**
   - Mark tasks ✅ only when evidence supports completion; otherwise keep or set 🔄/⏳.
   - Add net-new tasks with ⏳ and a priority; remove or mark ⏭️ items explicitly if truly dropped/deferred.
   - Update blockers with owners/next step.
4. **Refresh metrics**
   - Recompute progress ([done]/[total], %) and refresh Last Updated (UTC).
   - Update “Next Priority” list based on remaining work and blockers.
5. **Output**
   - Summarize deltas (Added, Completed, Updated, Blockers) in bullets.
   - Provide the full updated tracker in a fenced markdown block ready to write back to `[TRACKER_FILE]`.

---

## Output Format

```
Changes Applied:
- Added: [n] tasks — [...]
- Completed: [n] tasks — [...]
- Updated: [n] tasks — [...]
- Blockers: [list or “None”]

# [TRACKER_FILE] — [GOAL]
Last Updated: 2025-12-09T00:00:00Z
Progress: [X%] ([done]/[total]) | Next Priority: [items]
Blockers: [list or “None”]

## Workstream/Phase
- [ ] ⏳ [PRIORITY] Task (source: plan.md §Acceptance Criteria)
- [ ] 🔄 [PRIORITY] Task (source: progress.md @2025-12-09)
- [ ] ⏭️ [PRIORITY] Deferred task (reason)
- [x] ✅ [PRIORITY] Completed task (evidence)
```

---

## Usage

```
/update-tracker tracker.md progress.md plan.md timeline.md
```

Optional time window:
```
/update-tracker tracker.md progress.md plan.md timeline.md "since last commit"
```

---

## Quality Checks

- [ ] Evidence-backed updates only; no speculative ✅.
- [ ] Progress math matches task counts.
- [ ] New tasks are clearly sourced and prioritized.
- [ ] Blockers updated with owner/next step.
- [ ] “Next Priority” list is current and actionable.
- [ ] Tracker stays concise (no narrative progress log).

---

## Examples

### Example 1: Quick Sync
**Input**:  
`/update-tracker tracker.md progress.md`

**Expected Output (excerpt)**:
```
Changes Applied:
- Added: 1 task — Add tests for ValidationService
- Completed: 1 task — RepositoryBase tests
- Updated: 1 task — Reprioritized ProfileService tests to High
- Blockers: None

# tracker.md — reach 100% coverage
Last Updated: 2025-12-09T00:00:00Z
Progress: 60% (3/5) | Next Priority: ValidationService tests
```

### Example 2: Windowed Sync
**Input**:  
`/update-tracker tracker.md progress.md plan.md timeline.md "since last commit"`

**Expected Output (excerpt)**:
```
Changes Applied:
- Added: 2 tasks — Clean up feature flags; Add rollback checklist
- Completed: 1 task — Publish RC build
- Updated: 1 task — Blocker resolved (OAuth cert rotated)
- Blockers: None

# tracker.md — stabilize release
Last Updated: 2025-12-09T00:00:00Z
Progress: 50% (4/8) | Next Priority: Validate RC across tenants
Blockers: None
```

---

## Related Prompts

- `tracker/create-tracker.prompt.md` — Build a tracker from scratch using ticket evidence.
- `ticket/resume-tracker-work.prompt.md` — Continue systematic work using the tracker.

