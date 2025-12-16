---
name: activate-ticket
description: "Activate a ticket by loading its context and executing the requested action"
category: ticket
tags: ticket, workflow, activation, context-loading, pattern
argument-hint: "Ticket ID and action (e.g., @EPP-192 please start)"
---

# Activate Ticket (Pattern-Based)

This prompt activates a ticket by loading its context and executing the requested action.

**Pattern**: Ticket Activation Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: 95% first-attempt success rate
**Use When**: Starting work on a specific ticket, switching tickets, requesting ticket-specific actions

---

## Required Context

- **Ticket ID**: Valid ticket identifier (e.g., EBASE-12345, EPP-192)
- **Action**: What you want to do with the ticket (see Common Actions below)
- **Optional**: Additional context files or specifications (use `@filename` to attach)

---

## Process

Follow these steps when activating a ticket:

### Step 1: Verify Ticket Exists
Ensure `tickets/[TICKET-ID]/` folder exists with required files (plan.md, context.md, progress.md).

### Step 2: Formulate Activation Command
Use pattern:
```
<ticket>@[TICKET-ID]</ticket> <action>[ACTION_VERB]</action>
```

### Step 3: Add Optional Context (if needed)
Attach specifications or related files:
```
<ticket>@[TICKET-ID]</ticket> <context>@[SPEC_FILE]</context> <action>[ACTION]</action>
```

### Step 4: Execute Command
Submit to AI agent and wait for context loading confirmation.

### Step 5: Review AI Response
Check that AI:
- Loaded ticket context
- Understood objective
- Identified current state
- Executed or clearly blocked with reason

### Step 6: Proceed with Work
Continue with follow-up commands or refinements as needed.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Parse Activation**: Extract ticket ID and action from command
2. **Load Context**: Read plan.md, context.md, progress.md from ticket folder
3. **Understand Requirements**: Parse objectives, acceptance criteria, current state
4. **Validate Preconditions**: Check if prerequisites are met
5. **Execute Action**: Perform requested action with full context
6. **Update Documentation**: Log action in progress.md if significant
7. **Respond Structured**: Follow Output Format below

---

## Basic Usage

```
<ticket>@[TICKET-ID]</ticket> <action>[ACTION_VERB]</action>
```

**Placeholder Conventions**:
- `[TICKET-ID]` - Your ticket identifier in format PROJ-NUMBER (e.g., EBASE-12345, EPP-192)
- `[ACTION_VERB]` - Imperative verb describing what to do (see Common Actions below)

---

## Common Actions

### Start Work (`please start`)
**When**: Beginning new ticket
**Links to**: `start-ticket.prompt.md`
**AI should**: Initialize context, load plan, propose first steps

### Create Documentation (`please make the [TYPE] md`)
**When**: Need to generate ticket artifacts
**Links to**: `update-progress.prompt.md`
**AI should**: Generate requested documentation following templates

### Test Implementation (`please test`)
**When**: Implementation complete, needs validation
**Links to**: `validate-completion.prompt.md`
**AI should**: Execute tests, verify acceptance criteria, report results

### Continue Work (`please continue`)
**When**: Resuming work after break
**Links to**: `catchup-on-ticket.prompt.md`
**AI should**: Review context, identify next steps, proceed

### Check Progress (`check the progress`)
**When**: Need status update
**Links to**: `check-status.prompt.md`
**AI should**: Review progress.md, summarize state, identify blockers

### Validate and Execute (`please validate and execute`)
**When**: Complex change needing pre-execution validation
**Links to**: `validate-before-action.prompt.md`
**AI should**: Validate preconditions, confirm approach, execute if valid

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-activation-exemplar.md`

## Output Format

When activating a ticket, AI must respond with:

```markdown
## Activating Ticket [TICKET-ID]

**Loaded Context**:
- ✓/✗ Plan: [Brief summary from plan.md]
- ✓/✗ Complexity: [Simple Fix | Complex Implementation]
- ✓/✗ Current State: [From context.md]

**[Action-Specific Section]**:
[Varies by action type - see Examples above]

**Next Steps** (if applicable):
1. [Step 1]
2. [Step 2]
```

---

## Quality Criteria

### General Validation (All Actions)
- [ ] Ticket context loaded (plan.md, context.md, progress.md read)
- [ ] Requirements understood (can summarize objective)
- [ ] Current state confirmed
- [ ] Action executed or clearly blocked with reason
- [ ] No assumptions made (asked for clarification if needed)

### Action-Specific Validation

**For `please start`**:
- [ ] Proposed approach aligns with plan objectives
- [ ] Complexity assessment considered
- [ ] Initial steps identified

**For `please test`**:
- [ ] All acceptance criteria checked
- [ ] Test results documented
- [ ] Pass/fail status clear

**For `please validate and execute`**:
- [ ] Validation completed before execution
- [ ] Preconditions explicitly confirmed
- [ ] Execution results documented

**For `please continue`**:
- [ ] Progress reviewed
- [ ] Next immediate steps identified
- [ ] No context loss from previous session

---

## Related Prompts

- `ticket/start-ticket.prompt.md` - For initial ticket setup and planning
- `ticket/check-status.prompt.md` - Review ticket status before activating
- `ticket/validate-before-action.prompt.md` - For complex implementations needing validation
- `ticket/catchup-on-ticket.prompt.md` - For resuming multi-session work
- `ticket/validate-completion.prompt.md` - For final ticket validation
- `ticket/update-progress.prompt.md` - For documenting work progress
- `templars/ticket/ticket-activation-templar.md` - Reusable activation structure

---

## Extracted Patterns

- **Templar**: `.cursor/prompts/templars/ticket/ticket-activation-templar.md`

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)
**Pattern ID**: #1 Ticket Activation
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
