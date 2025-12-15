---
name: resume-tracker-work
description: "Resume systematic work using a progress tracker file"
category: ticket
tags: ticket, tracker, continuation, systematic, multi-session
argument-hint: "Tracker filename (e.g., @tracker.md lets continue)"
---

# Resume Tracker Work (Pattern-Based)

This prompt resumes systematic work using a progress tracker file to maintain continuity across sessions.

**Pattern**: Tracker-Based Continuation Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Perfect for multi-session systematic work  
**Use When**: Resuming work tracked in progress files (tests, coverage, multi-phase implementations)

---

## Required Context

- **Tracker File**: Progress tracking file with status indicators (e.g., UNIT-TEST-IMPLEMENTATION-TRACKER.md, roadmap.md)
- **Status Format**: Tracker must have clear COMPLETE/PENDING/IN PROGRESS markers
- **Continuation Goal**: What you want to achieve (continue to next, push to 100%, etc.)

---

## Process

Follow these steps to resume tracker-based work:

### Step 1: Locate Your Tracker File
Find the tracker file (e.g., `UNIT-TEST-IMPLEMENTATION-TRACKER.md`, `roadmap.md`, `progress.md`).

### Step 2: Formulate Resume Request
Use pattern with XML delimiters:
```
<tracker>@[TRACKER_FILE].md</tracker> <action>[CONTINUATION_SIGNAL]</action>
```

### Step 3: AI Loads and Reports Status
AI reads tracker, reports current state (completed/remaining), identifies next work.

### Step 4: AI Executes Batch
AI systematically works through next items, updating tracker as it goes.

### Step 5: Review Progress
Check updated tracker for new status, what was completed, what remains for next session.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Load Tracker**: Read tracker file to understand current state and format
2. **Identify Progress**: Parse what's COMPLETE vs PENDING vs IN PROGRESS
3. **Find Next Work**: Determine next logical item(s) to work on based on priority
4. **Resume Context**: Recall approach/patterns from completed work (consistency)
5. **Execute Batch**: Work on next N items systematically (don't skip around)
6. **Update Tracker**: Mark completed items, update progress percentages, timestamp
7. **Report Status**: Summarize what was done, new progress percentage, what remains

---

## Basic Usage

```
<tracker>@[TRACKER_FILE].md</tracker> <action>[CONTINUATION_SIGNAL]</action>
```

**Placeholder Conventions**:
- `[TRACKER_FILE]` - Name of your tracker file (e.g., UNIT-TEST-IMPLEMENTATION-TRACKER, roadmap, IMPLEMENTATION-STATUS)
- `[CONTINUATION_SIGNAL]` - Continuation instruction (see Common Signals below)

---

## Common Continuation Signals

- `lets continue` - Resume where left off
- `lets continue with the remaining tasks` - Explicit continuation
- `lets get all to 100%` - Goal-oriented (push to completion)
- `continue with high-priority items` - Priority-based
- `continue` - Simplest form
- `continue until [GOAL]` - With explicit goal (e.g., "continue until 100% coverage")

---

## Tracker File Requirements

Your tracker should include:

- ✅ **Clear status indicators**: COMPLETE (✅), PENDING (⏳), IN PROGRESS (🔄)
- ✅ **Progress metrics**: Percentages or counts (e.g., "15/20 complete = 75%")
- ✅ **List of remaining work**: Clear enumeration of pending items
- ✅ **Priority ordering**: High-priority items listed first
- ✅ **Last updated timestamp**: When tracker was last modified
- ✅ **Next priority section**: Explicit "Next Priority" or "Next Steps" section

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-resume-tracker-work-exemplar.md`

## Output Format

When resuming tracker work, AI must respond with:

```markdown
## Resuming Work from [TRACKER_FILE].md

**Current Progress**:
- Completed: [N] items ([X]%)
- Remaining: [N] items ([Y]%)
- Next Priority: [Item 1], [Item 2], [Item 3]

---

### Continuing with [Next Item]

[Work on item systematically]

✅ **[Item] Complete**
- [What was accomplished]
- [Metrics/evidence]

---

### Updated Progress

**[TRACKER_FILE].md updated**:

```markdown
[Updated tracker content showing new status]
```

---

### Next Session

**To continue**:
```
<tracker>@[TRACKER_FILE].md</tracker> <action>lets continue</action>
```

**Next Priority**: [What to work on next] ([remaining count])
```

---

## Common Tracker Files

- `UNIT-TEST-IMPLEMENTATION-TRACKER.md` - Test coverage work
- `IMPLEMENTATION-STATUS.md` - Feature implementation progress
- `roadmap.md` - Project-level progress
- `progress.md` - Ticket-specific progress
- `tracker.md` - General purpose tracker

---

## Multi-Session Strategy

**Session 1** (Start):
```
<tracker>@tracker.md</tracker> <action>lets continue</action>
```
→ Work on batch 1 (e.g., 3-5 items), update tracker

**Session 2** (Days later):
```
<tracker>@tracker.md</tracker> <action>lets continue with the remaining tasks</action>
```
→ Load tracker, resume where left off, work on batch 2

**Session 3** (More progress):
```
<tracker>@tracker.md</tracker> <action>lets continue</action>
```
→ Work on batch 3

**Session N** (Final push):
```
<tracker>@tracker.md</tracker> <action>lets get all to 100%</action>
```
→ Complete all remaining items in final batch

---

## Quality Criteria

Before claiming batch complete, verify:

- [ ] Tracker file read and current state understood
- [ ] Next work items identified correctly based on priority
- [ ] Work completed systematically (not skipping around)
- [ ] Tracker updated with new status for all completed items
- [ ] Progress percentages recalculated accurately
- [ ] "Last Updated" timestamp refreshed
- [ ] Clear indication of what remains for next session
- [ ] No items marked complete prematurely (all work actually done)
- [ ] Consistent approach maintained across batch (follow established patterns)

---

## Tips

- **Keep tracker updated** after each session (don't let it get stale)
- **Use consistent status markers** (✅ COMPLETE, ⏳ PENDING, 🔄 IN PROGRESS, ⏭️ SKIPPED)
- **Include "Next Priority" section** in tracker (helps AI resume efficiently)
- **Update "Last Updated" timestamp** (shows tracker is current)
- **Works best for work spanning multiple days** (maintains continuity)
- **Break large goals into batches** (don't try to do everything in one session)
- **Use goal-oriented signals** when pushing to completion ("lets get all to 100%")

---

## Anti-Pattern (Don't Do This)

❌ **Without tracker reference**:
```
continue with the remaining tasks
```
→ AI doesn't know what tracker or what tasks you're referring to

✅ **With tracker reference**:
```
<tracker>@UNIT-TEST-IMPLEMENTATION-TRACKER.md</tracker> <action>continue with the remaining tasks</action>
```
→ AI knows exactly what to load and resume

---

## Follow-up Patterns

After each batch:
- **Update tracker progress** (mark completed items, update percentages)
- **Use same pattern for next session** (consistency across sessions)
- **For completion validation**: Use `validate-completion.prompt.md`
- **For status check**: Use `check-status.prompt.md` to review overall progress

---

## Related Prompts

- `ticket/activate-ticket.prompt.md` - When tracker is tied to a ticket, activate ticket first
- `ticket/check-status.prompt.md` - Review overall status before or after continuing
- `ticket/validate-completion.prompt.md` - Validate when tracker reaches 100%
- `ticket/catchup-on-ticket.prompt.md` - If returning after long break, catch up on context first

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)  
**Pattern ID**: #2 Tracker-Based Continuation  
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)


