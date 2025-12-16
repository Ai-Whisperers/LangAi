---
name: catchup-on-ticket
description: "Get a narrative summary of ticket history, decisions, and current state for quick onboarding"
category: ticket
tags: ticket, narrative, history, context-reconstruction, onboarding
argument-hint: "Ticket ID and optional timeframe (e.g., @EPP-192 catch me up)"
---

# Catch Up on Ticket (Pattern-Based)

This prompt provides a narrative summary of ticket history, key decisions, and current state for quick onboarding after time away or when joining work in progress.

**Pattern**: Ticket Catchup Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for context continuity
**Use When**: Returning to ticket after time away, joining someone else's work, need quick orientation

---

## Required Context

- **Ticket ID**: Valid ticket identifier (e.g., EBASE-12345, EPP-192)
- **Ticket Documentation**: plan.md, progress.md, context.md must exist
- **Optional**: Intensity level (quick/standard/comprehensive)
- **Optional**: Focus area (decisions, implementations, blockers, timeline)

---

## Process

Follow these steps to get a ticket catchup:

### Step 1: Identify Your Catchup Need
Determine what intensity you need:
- **Quick**: 1-2 minute read, executive summary only
- **Standard**: 3-5 minute read, narrative with key points
- **Comprehensive**: 10+ minute read, full narrative with all details

### Step 2: Formulate Catchup Request
Use pattern with XML delimiters:
```
<ticket>@[TICKET-ID]</ticket> <intensity>[LEVEL]</intensity> <action>catch me up</action>
```

Or simplified:
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up</action>
```

### Step 3: Add Optional Focus (if needed)
Specify what aspect to emphasize:
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up on <focus>[ASPECT]</focus></action>
```

### Step 4: Provide Time Context (if helpful)
Mention how long you've been away:
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up - I've been away for [DURATION]</action>
```

### Step 5: Review Narrative Summary
Read the AI's catchup narrative to understand ticket history and current state.

### Step 6: Proceed with Work or Ask Questions
Either continue work or ask clarifying questions about specific aspects.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Load All Ticket Files**: Read plan.md, progress.md, context.md, timeline.md, references.md
2. **Extract Key Narrative**: Identify what happened chronologically (synthesize from progress.md)
3. **Highlight Decisions**: Surface important decisions and their rationale (why, not just what)
4. **Summarize Discoveries**: Note key findings and breakthroughs that changed approach
5. **Explain Current State**: Why are we where we are now? (context for current.md state)
6. **Orient for Next Steps**: What user needs to know before continuing
7. **Provide Reading Pointers**: Link to detailed sections if user wants to dig deeper
8. **Structure by Intensity**: Adjust detail level based on quick/standard/comprehensive request

---

## Basic Usage

```
<ticket>@[TICKET-ID]</ticket> <action>catch me up</action>
```

**Placeholder Conventions**:
- `[TICKET-ID]` - Ticket identifier in format PROJ-NUMBER (e.g., EBASE-12345, RULES-001, EPP-192)
- `[LEVEL]` - Intensity level: quick | standard | comprehensive
- `[ASPECT]` - Focus area: decisions | implementations | blockers | timeline
- `[DURATION]` - Time away: "a week", "2 weeks", "since Phase 1"

---

## Catchup Intensity Levels

### Quick Catchup (1-2 minutes to read)
```
<ticket>@[TICKET-ID]</ticket> <intensity>quick</intensity> <action>catchup</action>
```
**AI delivers**: Executive summary with 3 key points and next step

### Standard Catchup (3-5 minutes to read)
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up</action>
```
**AI delivers**: Narrative summary with key decisions, discoveries, and current state

### Comprehensive Catchup (10+ minutes to read)
```
<ticket>@[TICKET-ID]</ticket> <intensity>comprehensive</intensity> <action>catchup</action>
```
**AI delivers**: Full narrative with all phases, decisions, discoveries, and complete context

---

## Catchup Focus Areas

### Decision-Focused Catchup
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up on <focus>key decisions</focus></action>
```
**AI emphasizes**: Why choices were made, alternatives considered, rationale

### Implementation-Focused Catchup
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up on <focus>what's been implemented</focus></action>
```
**AI emphasizes**: Technical changes, code modifications, features completed

### Blocker-Focused Catchup
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up on <focus>any issues or blockers</focus></action>
```
**AI emphasizes**: Problems encountered, solutions applied, remaining obstacles

### Timeline-Focused Catchup
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up with <focus>timeline context</focus></action>
```
**AI emphasizes**: When things happened, session boundaries, work patterns

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-catchup-exemplar.md`

## Output Format

When providing catchup, AI must structure response by intensity level:

### Quick Catchup Format
```markdown
## Quick Catchup: [TICKET-ID]

**In 60 Seconds**:
[2-3 sentence summary of what happened and where we are]

**Key Points**:
- [Most important thing 1]
- [Most important thing 2]
- [Most important thing 3]

**Next**: [What to do next]

**Full Details**: tickets/[TICKET-ID]/context.md
```

### Standard Catchup Format
```markdown
## Ticket Catchup: [TICKET-ID]

**Objective**: [From plan.md]
**Started**: [From timeline]
**Last Activity**: [From progress.md]
**Current State**: [From context.md]

---

### What Happened (Narrative Summary)

[3-4 paragraph narrative organized by phases]

**Phase 1: [Name]**
[What was done, why, and key outcomes]

**Phase 2: [Name]**
[What was done, why, and key outcomes]

**Current Phase: [Name]**
[Where we are now, what's in progress]

---

### Key Decisions

1. **[Decision 1]**: [Rationale and context]
2. **[Decision 2]**: [Rationale and context]

---

### Important Discoveries

- **[Discovery 1]**: [What was found and impact]
- **[Discovery 2]**: [What was found and impact]

---

### Current State

**What's Complete**: [Summary]
**What's In Progress**: [Current work]
**What's Remaining**: [Pending items]

---

### What You Need to Know

- [Critical context point 1]
- [Critical context point 2]
- [Critical context point 3]

---

### Next Steps

1. [Most logical next action]
2. [Follow-up action]

---

### Detailed References

- **Plan**: tickets/[TICKET-ID]/plan.md
- **Current Context**: tickets/[TICKET-ID]/context.md
- **Full History**: tickets/[TICKET-ID]/progress.md
- **Timeline**: tickets/[TICKET-ID]/timeline.md
```

### Comprehensive Catchup Format
```markdown
## Comprehensive Catchup: [TICKET-ID]

[Complete narrative with ALL phases, ALL decisions with full rationale, ALL discoveries with impact, ALL technical approaches, COMPLETE context for understanding entire ticket lifecycle]

[Include timeline context, reference all key conversations, explain all major and minor decisions, surface all gotchas, provide complete technical landscape]

[Structure with clear phases, decision sections, discovery sections, technical approach summary, current state, and complete next steps]

[Provide everything needed for someone to fully take over the ticket]
```

---

## Common Catchup Requests

### After Time Away
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up - I've been away for [DURATION]</action>
```

### Joining Work in Progress
```
<ticket>@[TICKET-ID]</ticket> <intensity>comprehensive</intensity> <action>catch me up - I'm joining this work</action>
```

### Before Resuming
```
<ticket>@[TICKET-ID]</ticket> <action>quick catchup before I continue</action>
```

### Morning Routine
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up - starting work today</action>
```

### After Context Switch
```
<ticket>@[TICKET-ID]</ticket> <action>catch me up - I was working on TICKET-Y, what happened here?</action>
```

---

## Catchup vs Status Check

### Use **Catchup** When:
- ✅ You've been away from the ticket
- ✅ You need to understand what happened (the story)
- ✅ You want narrative context with decisions and why
- ✅ Joining someone else's work
- ✅ Need to understand rationale behind current state

### Use **Status Check** When:
- ✅ You're actively working on the ticket
- ✅ You need to know what's left to do
- ✅ You want structured progress report (not narrative)
- ✅ Preparing for next action
- ✅ Need completion percentages and remaining work

**Key Difference**:
- **Catchup** = storytelling (what happened and why)
- **Status** = reporting (where we are and what's left)

---

## Quality Criteria

A good catchup response should have:

- [ ] Narrative flow (tells the story, not just lists facts)
- [ ] Key decisions highlighted with rationale (why, not just what)
- [ ] Important discoveries noted with impact (what changed because of this)
- [ ] Current state explained (why we're here, not just that we are)
- [ ] Context for next steps provided (what to know before continuing)
- [ ] Blockers/issues surfaced with status
- [ ] Reading time appropriate to requested level (quick: 1-2min, standard: 3-5min, comprehensive: 10+min)
- [ ] References to detailed files provided for deep dives
- [ ] No need to ask follow-up "why" questions (context complete)
- [ ] Chronological clarity (when things happened in relation to each other)

---

## Tips

- Use "catch me up" as explicit trigger phrase
- Specify intensity level (quick/standard/comprehensive) if you have time constraints
- Mention how long you've been away for better context calibration
- Request focus areas if you only care about specific aspects
- Great for Monday mornings or after vacations
- Perfect when joining collaborative tickets
- Essential for handover situations
- Combine with status check after catchup: "Now check current status"

---

## Follow-up Patterns

After catchup, typically:

1. **Proceed with Work**
   ```
   <ticket>@[TICKET-ID]</ticket> <action>please continue</action>
   ```

2. **Ask Specific Questions**
   ```
   Why did we choose approach X over Y? [based on catchup understanding]
   ```

3. **Validate Understanding**
   ```
   Based on the catchup, I think next step is Y - correct?
   ```

4. **Transition to Status**
   ```
   <ticket>@[TICKET-ID]</ticket> <action>now check current status</action>
   ```
   → Transition from history (catchup) to current state (status)

---

## Related Prompts

- `ticket/check-status.prompt.md` - Current state and what's left (reporting focus)
- `ticket/activate-ticket.prompt.md` - Start/resume work (action focus)
- `ticket/resume-tracker-work.prompt.md` - Continue systematic work (tracker focus)
- `ticket/start-ticket.prompt.md` - Initial ticket setup
- `ticket/update-progress.prompt.md` - Document work progress
- `templars/ticket/ticket-catchup-templar.md` - Reusable catch-up structure
- `exemplars/ticket/ticket-catchup-exemplar.md` - Reference catch-up output

---

## Extracted Patterns

- **Templar**: `.cursor/prompts/templars/ticket/ticket-catchup-templar.md`
- **Exemplar**: `.cursor/prompts/exemplars/ticket/ticket-catchup-exemplar.md`

---

**Prompt Created**: 2025-12-06
**Category**: Ticket Management
**Pattern Type**: Context Reconstruction
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
