---
name: validate-before-action
description: "Enforce validation before execution for complex tasks"
category: ticket
tags: ticket, validation, two-phase, safety, risk-mitigation
argument-hint: "Specification file and optional ticket ID (e.g., @spec.md please validate and execute)"
---

# Validate Before Action (Pattern-Based)

This prompt enforces a two-phase workflow: validate understanding first, then execute after confirmation.

**Pattern**: Validation-Before-Action Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Reduces errors by ~80%, prevents costly mistakes
**Use When**: Complex implementations, risky changes, detailed specifications

---

## Required Context

- **Specification File**: Detailed requirements, technical specs, or prompt file
- **Ticket ID** (Optional): Associated ticket for additional context
- **Validation Criteria**: What must be understood before proceeding

---

## Process

Follow these steps for safe two-phase execution:

### Step 1: Prepare Specification
Ensure detailed specification file exists with requirements, constraints, success criteria.

### Step 2: Formulate Validation Request
Use pattern with XML delimiters:
```xml
<spec>@[SPECIFICATION_FILE]</spec>
<ticket>@[TICKET-ID]</ticket> <!-- optional -->
<action>validate and when ok, execute</action>
```

### Step 3: Review AI Validation
AI presents understanding, approach, files to modify, risks, questions. **REVIEW CAREFULLY**.

### Step 4: Approve or Correct
- ✅ Approve: "Looks good, please proceed"
- 🔄 Clarify: "Good, but adjust [specific aspect]"
- ❌ Stop: "No, that's not right. [explanation]"

### Step 5: AI Executes (if approved)
AI implements following validated approach, references specification throughout.

---

## Reasoning Process

### Phase 1 - Validation (AI MUST Do)

1. **Read Specification**: Load and parse all requirements thoroughly
2. **Identify Key Elements**: Extract objectives, constraints, success criteria
3. **Plan Approach**: Think step-by-step through implementation
4. **Surface Questions**: Identify ambiguities or missing information
5. **Present Understanding**: Demonstrate comprehension for user review
6. **WAIT**: Do not proceed until user confirms

### Phase 2 - Execution (After User Approval ONLY)

1. **Implement Plan**: Follow validated approach
2. **Reference Specification**: Check against requirements throughout
3. **Track Progress**: Log major steps
4. **Validate Output**: Verify against success criteria
5. **Report Completion**: Provide evidence of success

---

## Basic Usage

```xml
<spec>@[SPECIFICATION_FILE]</spec>
<ticket>@[TICKET-ID]</ticket> <!-- optional -->
<action>validate and when ok, execute</action>
```

**Placeholder Conventions**:
- `[SPECIFICATION_FILE]` - Path to detailed requirements (e.g., PROMPT-FEATURE.md, technical-spec.md)
- `[TICKET-ID]` - Ticket identifier for context (e.g., EBASE-12345) - OPTIONAL

---

## Variations

### Standard Validation-Then-Execute
```xml
<spec>@PROMPT-DATAMIGRATOR.md</spec>
<ticket>@EBASE-12263</ticket>
<action>validate and when ok, execute</action>
```

### Validation Only (No Execution)
```xml
<spec>@specification.md</spec>
<action>validate your understanding before implementing</action>
```

### Conditional Execution
```xml
<spec>@detailed-requirements.md</spec>
<action>implement this if you understand it completely</action>
```

### Phase-by-Phase Validation
```xml
<spec>@plan.md</spec>
<action>validate Phase 1 requirements and confirm before starting</action>
```

---

## Validation Checklist

AI must demonstrate understanding of:
- [ ] Core requirements (what must be delivered)
- [ ] Success criteria (how to verify correctness)
- [ ] Constraints and limitations (technical/business boundaries)
- [ ] Implementation approach (step-by-step plan)
- [ ] Files to create/modify (specific paths and changes)
- [ ] Testing strategy (how to validate)
- [ ] Risks and mitigations (potential issues and solutions)
- [ ] Questions (ambiguities needing clarification)

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-validate-before-action-exemplar.md`

## Output Format

### Phase 1: Validation Response

```markdown
## ✅ Validation Summary: [TICKET-ID or SPEC-NAME]

### Understanding
[Clear statement of what will be implemented]

### Approach
[Step-by-step breakdown by phase]

### Files to Modify/Create
[Specific paths with descriptions]

### Success Criteria
[How to verify correctness]

### Risks & Mitigations
[Potential issues with solutions]

### Dependencies
[External libraries, services, setup needed]

### Questions/Clarifications
[Ambiguities needing resolution]

---

**Ready to proceed?** Please confirm approach or provide corrections.
```

### Phase 2: Execution (After Approval)

```markdown
## Executing [TICKET-ID or SPEC-NAME]

[Systematic implementation following validated approach]
[Progress updates for each phase]
[Final validation report with evidence]

### ✅ Implementation Complete

**Success Criteria Validation**: [Checklist with evidence]
**Files Created/Modified**: [List]
**Next Steps**: [What to do next]
```

---

## Quality Criteria

### Validation Phase

- [ ] All requirements understood and stated clearly
- [ ] Implementation approach planned step-by-step
- [ ] Files and changes identified specifically
- [ ] Success criteria defined and testable
- [ ] Risks identified with mitigation plans
- [ ] Questions surfaced for ambiguous areas
- [ ] Dependencies and prerequisites identified
- [ ] AI explicitly waits for user approval

### Execution Phase (After Approval)

- [ ] Follows validated approach exactly
- [ ] References specification throughout
- [ ] Tracks progress on major milestones
- [ ] Validates output against success criteria
- [ ] Reports completion with concrete evidence
- [ ] Documents any deviations from plan with rationale

---

## When to Use

### ✅ Good Use Cases

- Complex multi-file changes
- Risky migrations or refactors
- Detailed specifications (>500 lines)
- Cross-repo coordination
- First-time implementations of patterns
- Critical production changes
- Security-sensitive implementations

### ❌ Skip For

- Simple, obvious tasks (<5 min work)
- Single-line fixes
- Continuing established patterns (already validated once)
- Trivial changes (typo fixes, formatting)

---

## Benefits

✅ **Catch Misunderstandings Early** - Before any code is written
✅ **Build Confidence** - See AI understands requirements
✅ **Reduce Rework** - Fewer correction cycles
✅ **Learn Together** - Discussion reveals assumptions
✅ **Risk Mitigation** - Prevent costly mistakes (especially for critical operations)

---

## Anti-Patterns

### ❌ DON'T: Skip validation for complex work
```
@COMPLEX-SPEC.md just implement it
```
**Why bad**: Risk of major misunderstanding, costly rework, potential production issues

✅ **DO: Validate first**
```xml
<spec>@COMPLEX-SPEC.md</spec>
<action>validate and when ok, execute</action>
```
**Why good**: Catches errors before they happen, builds confidence

### ❌ DON'T: Vague validation response
```markdown
## Validation
I understand the requirements. Ready to proceed?
```
**Why bad**: No evidence of understanding, can't catch misunderstandings

✅ **DO: Detailed validation**
```markdown
## Validation Summary
Understanding: [Specific details]
Approach: [Step-by-step]
Files: [Specific paths]
Risks: [Identified with mitigations]
Ready to proceed?
```
**Why good**: Clear evidence of understanding, opportunity to correct

---

## Tips

- **Read AI's validation carefully** - it's your safety checkpoint
- **Ask questions if validation unclear** - don't assume AI understood
- **For very complex work, validate phase-by-phase** - don't try to validate entire implementation at once
- **Don't skip validation for critical implementations** - the 5 minutes saved isn't worth the risk
- **Use for first instance of pattern, then repeat without validation** - efficiency after pattern established

---

## Related Prompts

- `ticket/activate-ticket.prompt.md` - For simpler actions not needing validation
- `ticket/start-ticket.prompt.md` - Ticket initialization with planning
- `ticket/close-ticket.prompt.md` - Final validation before closure
- `ticket/validate-completion.prompt.md` - Validate work completion

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)
**Pattern ID**: #4 Validation-Before-Action
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
