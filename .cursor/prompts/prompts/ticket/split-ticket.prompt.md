---
name: split-ticket
description: "Please split a ticket into well-scoped sub-tickets with clear ownership and dependencies"
agent: cursor-agent
model: GPT-4
category: ticket
tags: ticket, split, workflow, planning, decomposition
argument-hint: "Parent ticket ID and summary (e.g., EPP-250: refactor data layer)"
---

# Split Ticket into Sub-Tickets

Please split a parent ticket into sub-tickets with crisp scopes, acceptance criteria, and dependency ordering.

---

## Purpose

Decompose a parent ticket into actionable sub-tickets that together deliver the parent objective, with clear ordering, ownership, and acceptance criteria.

---

## Required Context

```xml
<ticket>
  <id>[PARENT_TICKET_ID]</id>
  <summary>[PARENT_SUMMARY]</summary>
  <objective>[PARENT_OBJECTIVE]</objective>
  <constraints>[CONSTRAINTS]</constraints> <!-- optional -->
  <known_risks>[RISKS]</known_risks> <!-- optional -->
  <due>[DUE_DATE]</due> <!-- optional -->
</ticket>
```

**Placeholders**
- `[PARENT_TICKET_ID]`: Parent ticket identifier (e.g., EPP-250)
- `[PARENT_SUMMARY]`: Brief description
- `[PARENT_OBJECTIVE]`: Desired outcome
- `[CONSTRAINTS]`: Deadlines, compliance, tech constraints (optional)
- `[RISKS]`: Known risks (optional)
- `[DUE_DATE]`: Target milestone (optional)

---

## Process

1. **Understand Scope**
   - Parse parent ticket objective, constraints, risks, and due date (if any).
   - Identify major workstreams or deliverable slices.
2. **Define Splitting Criteria**
   - Each sub-ticket must have: single clear outcome, testable acceptance criteria, minimal cross-team overlap.
   - Prefer vertical slices over layer-only tasks unless constrained.
3. **Propose Sub-Tickets**
   - 3–8 sub-tickets typical; adjust to scope.
   - For each: ID suggestion, title, scope, acceptance criteria, ownership hint, effort, and risk.
4. **Order and Dependencies**
   - Map dependencies and ordering (e.g., blockers vs parallelizable).
   - Call out milestones and checkpoints.
5. **Check for Completeness**
   - Ensure combined scope covers parent objective.
   - Surface open questions and risks that require clarification.
6. **Ready-to-Create Guidance**
   - Provide command snippets to create each sub-ticket (using `start-ticket` or `create-ticket` prompts).

---

## Reasoning Process

1. Understand the desired outcome and constraints of the parent.
2. Prefer vertical slices that can be delivered and tested independently.
3. Minimize coupling between sub-tickets; make dependencies explicit.
4. Balance workload: similar effort and risk across sub-tickets when possible.
5. Preserve traceability back to the parent objective.

---

## Output Format

```markdown
## 🧩 Proposed Sub-Tickets for [PARENT_TICKET_ID]

**Parent Summary**: [PARENT_SUMMARY]  
**Objective**: [PARENT_OBJECTIVE]  
**Due**: [DUE_DATE or "Not provided"]

### 📋 Sub-Tickets
| ID Suggestion | Title | Scope | Acceptance Criteria | Effort | Risk | Depends On |
| --- | --- | --- | --- | --- | --- | --- |
| TICKET-1 | ... | ... | ... | S/M/L | Low/Med/High | None/ID |
| TICKET-2 | ... | ... | ... | S/M/L | Low/Med/High | TICKET-1 |

### 🛠️ Ownership Hints
- [Sub-ticket]: [Suggested team/role]

### 🔗 Dependencies & Order
- Blockers: [...]
- Parallelizable: [...]
- Milestones: [...]

### ❓ Open Questions
- [ ] Question 1
- [ ] Question 2

### ⚠️ Risks
- Risk: [description] → Mitigation: [plan]

### ▶️ Create Commands
```xml
<ticket>
  <id>[ID_SUGGESTION]</id>
  <summary>[TITLE]</summary>
</ticket>
<action>start ticket</action>
```
```

---

## Validation

- [ ] Sub-tickets cover the parent objective without overlap
- [ ] Each sub-ticket has clear, testable acceptance criteria
- [ ] Dependencies and ordering are explicit
- [ ] Risks and open questions are listed
- [ ] Suggested IDs/titles are concise and slash-command friendly

---

## Usage

```
/split-ticket EPP-320: Modernize notification service
```

Or with richer context:
```xml
<ticket>
  <id>EPP-320</id>
  <summary>Modernize notification service</summary>
  <objective>Enable multi-channel notifications with retry and observability</objective>
  <constraints>Must keep current SMS SLA; ship by end of Q2</constraints>
  <known_risks>Legacy Twilio integration; unknown email bounce handling</known_risks>
  <due>2026-06-30</due>
</ticket>
```

---

## Usage Modes

- **Quick**: Parent ID + short summary only (auto-deduces scope from summary)  
  `/split-ticket EPP-400: Improve audit exports`
- **Guided**: Provide objective/constraints/risks/due date in XML for better slicing
- **Re-plan**: Re-run with updated constraints to adjust dependencies and ordering

---

## Examples

### Example 1: Service Modernization
**Input**
```xml
<ticket>
  <id>EPP-320</id>
  <summary>Modernize notification service</summary>
  <objective>Enable multi-channel notifications with retry and observability</objective>
  <constraints>Keep SMS SLA; ship by end of Q2</constraints>
  <known_risks>Legacy Twilio integration; unknown email bounce handling</known_risks>
</ticket>
```
**Expected Outcome**
- 4–6 sub-tickets (e.g., channel abstraction, retry pipeline, DLQ, metrics/dashboards)
- Dependencies captured (infra before channels; observability parallel)
- Ownership hints by platform vs product squads

### Example 2: Data Layer Migration
**Input**
```
/split-ticket EPP-365: Migrate billing data layer to new repository pattern
```
**Expected Outcome**
- Sub-tickets per domain slice (pricing, invoicing, reconciliation), plus infrastructure
- Acceptance criteria per sub-ticket (CRUD + tests, performance budget, rollback plan)
- Dependencies: infra before domain repositories; reconciliation after invoicing

---

## Troubleshooting

- **Too many sub-tickets**: Constrain scope; aim for 3–8 well-defined slices.
- **Overlapping scopes**: Rephrase titles/scopes to avoid duplication; prefer vertical slices.
- **Weak acceptance criteria**: Add measurable outcomes (tests, SLAs, artifacts).

---

## Related Prompts

- `ticket/create-ticket.prompt.md` — create each sub-ticket skeleton
- `ticket/start-ticket.prompt.md` — initialize ticket documentation and plan
- `ticket/update-progress.prompt.md` — log work sessions

