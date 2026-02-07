---
name: close-ticket
description: "Please close a ticket by validating completion, creating recap, and finalizing documentation"
category: ticket
tags: ticket, workflow, closure, completion, recap, validation
argument-hint: "Ticket ID or 'current ticket'"
---

# Close Ticket

Please close the specified ticket by validating completion, creating a recap summary, and finalizing all documentation.

**Pattern**: Ticket Closure Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Ensures clean, documented ticket closure
**Use When**: Work complete and ready to formalize closure

---

## Purpose

This prompt ensures proper ticket closure by:
- Validating all acceptance criteria met
- Creating comprehensive recap documentation
- Finalizing progress and context
- Preparing commit message
- Cleaning up current ticket reference

Use this when work is complete and you're ready to formally close a ticket.

---

## Required Context

- **Ticket ID**: Ticket to close (or "current ticket" to close active ticket)
- **Ticket Documentation**: plan.md, progress.md, context.md, tracker.md must exist
- **Completion State**: All work items must be complete

---

## Process

Follow these steps to close a ticket:

### Step 1: Verify Readiness
Ensure ticket work is complete:
- All acceptance criteria met
- No open blockers
- Tests passing
- Documentation complete

### Step 2: Formulate Closure Request
Use pattern with XML delimiters:
```
<ticket>@[TICKET-ID]</ticket> <action>close ticket</action>
```

Or for current ticket:
```
<action>close current ticket</action>
```

### Step 3: Review Validation Report
AI will validate completion and report status (ready to close or blockers found).

### Step 4: Review Generated Artifacts
Check AI-created artifacts:
- `recap.md` summary
- Final progress entry
- Git commit message

### Step 5: Commit and Archive
Use provided commit message to commit ticket documentation and close ticket.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI **MUST** follow this strict process:

### Step 0: Self-Validation (MANDATORY FIRST STEP)

**Before proceeding with closure, AI MUST validate**:

```markdown
## Pre-Closure Self-Check

Before I close this ticket, I MUST verify:

- [ ] I have READ plan.md and identified ALL acceptance criteria
- [ ] I have VERIFIED each acceptance criterion is met with evidence
- [ ] I have CHECKED for blockers in context.md
- [ ] I have CONFIRMED all tests pass (if applicable)
- [ ] I have REVIEWED code quality meets standards
- [ ] I would feel confident handing this to a colleague saying "it's done"

**If ANY checkbox is unchecked, I MUST NOT proceed with closure.**
**If ANY acceptance criteria is not met, I MUST BLOCK closure and report remaining work.**
```

### Step 1: Validate Completion

Read and verify:
```
tickets/[TICKET-ID]/plan.md         → Check ALL acceptance criteria
tickets/[TICKET-ID]/tracker.md      → Verify 100% completion (if exists)
tickets/[TICKET-ID]/context.md      → Confirm no blockers
tickets/[TICKET-ID]/progress.md     → Review work completion
```

**Critical**: If ANY acceptance criteria not met, STOP and BLOCK closure.

### Step 2: Create Recap

Generate `tickets/[TICKET-ID]/recap.md` (see Recap Template below).

### Step 3: Final Progress Entry

Append to `tickets/[TICKET-ID]/progress.md`:

```markdown
### [TIMESTAMP] - Ticket Closed

#### Final Status
- ✅ All acceptance criteria met
- ✅ All deliverables completed
- ✅ Documentation finalized
- ✅ Quality targets achieved

#### Closure Summary
[Brief summary of what was accomplished]

#### Metrics
- Duration: [Time spent]
- Completion: 100%
- Quality: [Meets/Exceeds standards]

**Ticket CLOSED**: Ready for commit and archival
```

### Step 4: Generate Commit Message

Create commit message following standards (see Commit Message Template below).

### Step 5: Cleanup

If this is the current ticket:
- Clear `tickets/current.md` (or update to next ticket)
- Confirm ticket folder is complete

---

## Closure Checklist

### Pre-Closure Validation

- [ ] **All acceptance criteria met** (from plan.md) - **MANDATORY**
- [ ] **No open blockers** or issues
- [ ] **Tests pass** (if applicable)
- [ ] **Documentation complete** (plan, context, progress, tracker)
- [ ] **Quality standards met** (no warnings/errors)
- [ ] **Code ready for commit** (if code changes involved)

### Documentation Requirements

- [ ] **plan.md**: Objectives achieved
- [ ] **progress.md**: Final entry added
- [ ] **context.md**: Final state documented
- [ ] **tracker.md**: 100% completion (if exists)
- [ ] **recap.md**: Created with outcomes summary

### Optional Items

- [ ] **RCA completed** (if defect/issue ticket)
- [ ] **Follow-up tickets created** (if needed)
- [ ] **Timeline documented** (hours.md generated if applicable)

---

## Recap Template

Generate `tickets/[TICKET-ID]/recap.md`:

```markdown
# [TICKET-ID]: Recap

## Ticket Summary

**Ticket**: [TICKET-ID]
**Title**: [Title from plan.md]
**Status**: ✅ Complete
**Completion Date**: [Date]

## Objectives Achieved

[List objectives from plan.md with completion status]

## Key Accomplishments

1. [Major accomplishment]
2. [Major accomplishment]
3. [Major accomplishment]

## Technical Changes

**Files Modified**: [Count]

**Key Changes**:
- [File/component]: [What changed]
- [File/component]: [What changed]

## Challenges & Solutions

**Challenge**: [Problem encountered]
**Solution**: [How it was resolved]

## Quality Metrics

- **Completion**: [X]%
- **Quality Score**: [If applicable]
- **Time Spent**: [Estimated hours]

## Key Learnings

1. [Learning 1]
2. [Learning 2]

## Follow-up Actions

- [ ] [Follow-up task if any]
- [ ] [Future improvement idea]

## Related Tickets

- [Related ticket]: [Relationship]
```

---

## Commit Message Template

```
[type]([scope]): [Brief description]

[Detailed description of changes]

[List of key changes]
- Change 1
- Change 2
- Change 3

[Optional sections]
Quality: [Quality notes]
Testing: [Testing notes]

Closes [TICKET-ID]
```

---

## Output Format

### If Ready to Close

```markdown
## Ticket Closure Report

**Ticket**: [TICKET-ID]
**Status**: ✅ READY TO CLOSE

### ✅ Validation Results

**Acceptance Criteria**: [X/X] met (100%)
- [x] [Criterion 1]
- [x] [Criterion 2]
- [x] [Criterion 3]

**Quality Checks**: All passed
**Documentation**: Complete
**Blockers**: None

### 📝 Recap Created

Recap file generated at: `tickets/[TICKET-ID]/recap.md`

**Key Accomplishments**:
1. [Accomplishment 1]
2. [Accomplishment 2]
3. [Accomplishment 3]

### 💾 Git Commit Message

```
[Generated commit message ready to use]
```

### 🧹 Cleanup

- [x] Final progress entry added
- [x] Recap.md created
- [x] current.md cleared (if applicable)
- [x] All documentation finalized

### ✨ Ticket Closed Successfully

Ready for:
1. Git commit (use message above)
2. Ticket archival
3. Next ticket (if any)
```

### If Blocked (Incomplete Work)

```markdown
## ❌ Ticket Closure BLOCKED: [TICKET-ID]

**Ticket**: [TICKET-ID]
**Title**: [Title]
**Status**: ❌ NOT READY TO CLOSE

### ⚠️ Validation FAILED

**Acceptance Criteria**: [X/Y] met ([Z]%)
- [x] [Met criterion 1]
- [ ] ❌ BLOCKER: [Unmet criterion 1]
- [ ] ❌ BLOCKER: [Unmet criterion 2]

**Additional Issues**:
- [ ] ❌ BLOCKER: [Issue description]
- [ ] 🟡 MUST-FIX: [Quality issue]

### 🚫 Cannot Close Ticket

**Remaining Work**:
1. 🔴 [Work item 1] (est. [time])
2. 🔴 [Work item 2] (est. [time])
3. 🟡 [Work item 3] (est. [time])

**Estimated Time to Completion**: ~[total hours]

### 📋 Next Steps

1. [Complete specific work item]
2. [Fix specific issue]
3. Re-run validation: `<ticket>@[TICKET-ID]</ticket> <action>validate completion</action>`
4. Only after validation passes: `<ticket>@[TICKET-ID]</ticket> <action>close ticket</action>`

### ⚠️ Completion Discipline

**Reminder**: This ticket cannot be closed until ALL acceptance criteria are met and ALL blockers resolved. Acting as a responsible colleague means ensuring work is truly complete.

**Do not proceed with closure until validation passes.**
```

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-closure-exemplar.md`

## Anti-Patterns

### ❌ DON'T: Close with incomplete work

```
Acceptance criteria: 3/5 met
- [x] Feature implemented
- [x] Tests added
- [ ] Documentation missing  ← BLOCKER
- [ ] Performance issue unresolved  ← BLOCKER
- [ ] Code review not done  ← BLOCKER
```

**Why bad**: Incomplete tickets create technical debt, confusion for future work, and violate completion discipline.

**Fix**: Complete all acceptance criteria OR update plan.md if requirements changed legitimately.

### ❌ DON'T: Skip recap

**Why bad**: Future reference lost, learnings not captured, handoff difficult, no record of outcomes.

**Fix**: Always create recap.md before closing. No exceptions.

### ❌ DON'T: Close without validation

**Why bad**: May miss incomplete work, quality issues, or blockers.

**Fix**: Always run validation checklist first (Step 0: Self-Validation).

### ❌ DON'T: Rush closure

**Why bad**: Premature "done" claims damage trust and create rework.

**Fix**: Act as responsible colleague. Would you confidently hand this off saying "it's complete"?

---

## Quality Criteria

A proper ticket closure should have:

- [ ] **All acceptance criteria validated**: 100% met with evidence
- [ ] **No blockers remaining**: All issues resolved
- [ ] **Recap.md created**: Comprehensive outcomes summary
- [ ] **Final progress entry added**: Closure documented
- [ ] **Commit message generated**: Following standards
- [ ] **Cleanup completed**: current.md cleared if applicable
- [ ] **Self-validation performed**: AI verified completion before proceeding
- [ ] **RCA completed** (if bug fix ticket): Root cause analysis documented
- [ ] **Follow-up tickets created** (if needed): Future work captured

---

## Usage

**Close current ticket**:
```
<action>close current ticket</action>
```

**Close specific ticket**:
```
<ticket>@EBASE-12345</ticket> <action>close ticket</action>
```

**Close with validation check first**:
```
<ticket>@EBASE-12345</ticket> <action>validate completion, then close</action>
```

---

## Related Prompts

- `ticket/validate-completion.prompt.md` - Validate before closing (recommended first step)
- `ticket/create-jira-recap.prompt.md` - Create JIRA-formatted recap for external tracking
- `ticket/check-status.prompt.md` - Check status before deciding to close
- `ticket/update-progress.prompt.md` - Add final progress entry
- `templars/ticket/ticket-closure-templar.md` - Reusable closure structure
- `exemplars/ticket/ticket-closure-exemplar.md` - Reference closure output

---

## Extracted Patterns

- **Templar**: `.cursor/prompts/templars/ticket/ticket-closure-templar.md`
- **Exemplar**: `.cursor/prompts/exemplars/ticket/ticket-closure-exemplar.md`

## Related Rules

- `.cursor/rules/ticket/recap-rule.mdc` - Recap documentation standards
- `.cursor/rules/ticket/validation-before-completion-rule.mdc` - Validation requirements
- `.cursor/rules/ticket/ai-completion-discipline.mdc` - Completion discipline (CRITICAL)
- `.cursor/rules/ticket/ticket-workflow-rule.mdc` - Overall workflow integration

---

**Pattern**: Ticket Closure Pattern
**Effectiveness**: Ensures clean, documented ticket closure with validation
**Use When**: Work complete and ready to formalize closure
**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
