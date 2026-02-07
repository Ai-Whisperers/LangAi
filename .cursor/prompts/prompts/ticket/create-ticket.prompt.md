---
name: create-ticket
description: "Please create a new ticket folder with initial documentation and classification"
agent: cursor-agent
model: GPT-4
category: ticket
tags: ticket, creation, workflow, planning
argument-hint: "Ticket ID and summary (e.g., EPP-123: short title)"
---

# Create Ticket

Please create a new ticket skeleton with required documentation, classify complexity, and prepare the folder for immediate work.

---

## Purpose

Stand up a new ticket workspace with structured docs, complexity classification, and an actionable starting plan so work can begin immediately.

---

## Required Context

```xml
<ticket>
  <id>[TICKET_ID]</id>
  <summary>[TICKET_SUMMARY]</summary>
  <requirements>[OPTIONAL_DETAILED_REQUIREMENTS]</requirements>
</ticket>
```

**Placeholders**
- `[TICKET_ID]`: Full ticket identifier (e.g., EPP-192)
- `[TICKET_SUMMARY]`: 1–2 sentence description of the ticket objective
- `[OPTIONAL_DETAILED_REQUIREMENTS]`: Structured acceptance criteria or spec link (optional)

---

## Process

1. **Confirm Inputs**
   - Parse `<ticket>` data.
   - If requirements missing, note as pending questions.
2. **Decide Complexity Track**
   - Classify as `Simple Fix` vs `Complex Implementation` using ticket rules (scope, files touched, risk).
   - Capture rationale and estimated effort.
3. **Create Folder and Files**
   - Path: `tickets/[TICKET_ID]/`
   - Files: `plan.md`, `context.md`, `progress.md`
   - If Complex Implementation: also create `tracker.md`
   - Optional: `references.md` when links/artefacts provided
4. **Seed Documents**
   - `plan.md`: Objective, acceptance criteria, constraints, complexity assessment, implementation approach, testing strategy, risks, questions.
   - `context.md`: Current state, components, dependencies, integration points, constraints, patterns, immediate next steps.
   - `progress.md`: First entry noting ticket initialization and decisions.
   - `tracker.md` (if present): Phases/tasks with checkboxes.
5. **Set Active Ticket**
   - Update `tickets/current.md` with `[TICKET_ID]`.
6. **Summarize Output**
   - Report folder/files created, complexity classification, rationale, initial next steps, and branch suggestion.

---

## Reasoning Process

1. Understand scope and constraints from the ticket summary/requirements.
2. Choose Simple Fix vs Complex Implementation; justify with scope, risk, and effort.
3. Shape docs to make the next actions obvious.
4. Prefer vertical, testable slices in the initial plan.
5. Surface unknowns and risks early.

---

## Output Format

```markdown
## ✅ Ticket Created: [TICKET_ID]

**Ticket**: [TICKET_ID]
**Summary**: [TICKET_SUMMARY]
**Complexity**: [Simple Fix | Complex Implementation]
**Rationale**: [Why this track]

---

### 📁 Folder Structure
```
tickets/[TICKET_ID]/
  ├── plan.md          ✅ Created
  ├── context.md       ✅ Created
  ├── progress.md      ✅ Created
  ├── tracker.md       ✅ Created (if complex)
  └── references.md    ✅ Created (if provided)
```

---

### 📊 Complexity Assessment
- Classification: [Simple Fix | Complex Implementation]
- Effort: [X days/hours]
- Risk: [Low | Medium | High]
- Components: [List]

---

### 📋 Next Steps
1. [First actionable step]
2. [Second step]
3. [Third step]

### 🌿 Branch Suggestion
```bash
git checkout -b [type]/[TICKET_ID]-[slug] develop
```
```

### 🔗 Rules Applied
- `.cursor/rules/ticket/complexity-assessment-rule.mdc`
- `.cursor/rules/ticket/plan-rule.mdc`
- `.cursor/rules/ticket/context-rule.mdc`
- `.cursor/rules/ticket/progress-rule.mdc`

---

## Validation

- [ ] Folder `tickets/[TICKET_ID]/` exists with required files
- [ ] Complexity classification provided with rationale
- [ ] plan.md seeded with objectives, acceptance criteria, approach, risks, questions
- [ ] context.md seeded with components, dependencies, constraints, next steps
- [ ] progress.md has initialization entry
- [ ] tracker.md added for complex tickets (skipped for simple)
- [ ] tickets/current.md updated to `[TICKET_ID]`

---

## Usage

```
/create-ticket EPP-250: Refactor data layer for billing
```

Optionally include requirements:
```xml
<ticket>
  <id>EPP-250</id>
  <summary>Refactor data layer for billing</summary>
  <requirements>
    - Support multi-tenant isolation
    - Add integration tests for billing pipelines
  </requirements>
</ticket>
```

---

## Usage Modes

- **Quick**: Minimal summary only (uses defaults for requirements)
  `/create-ticket EPP-251: Patch audit logging`
- **With Requirements**: Include acceptance criteria in `<requirements>` for richer seeding
  (recommended for Complex)
- **Re-run (refresh)**: Re-run with same ID to update docs when scope/requirements change

---

## Examples

### Example 1: Simple Fix
**Input**
```
/create-ticket EPP-260: Fix null ref in Meter sync
```
**Expected Outcome**
- Complexity: Simple Fix; Effort: 0.5–1d; Risk: Low
- Files: plan/context/progress created; tracker skipped
- Next steps cover reproduction, fix, targeted regression test

### Example 2: Complex Implementation with Requirements
**Input**
```xml
<ticket>
  <id>EPP-275</id>
  <summary>Introduce retryable messaging for billing events</summary>
  <requirements>
    - Support exponential backoff with jitter
    - Persist DLQ with operator replay
    - Emit metrics: success/fail/retry counts
  </requirements>
</ticket>
```
**Expected Outcome**
- Complexity: Complex Implementation; Effort: 3–5d; Risk: Medium
- Files: plan/context/progress + tracker
- Plan phases: infra, integration, observability; risks and questions noted

---

## Troubleshooting

- **Missing files**: Ensure working directory is repo root; re-run prompt.
- **Wrong complexity**: Provide clearer scope/constraints in `<requirements>`.
- **No branch suggestion**: Replace `[type]` with `feature/fix/hotfix` and supply `[slug]`.
