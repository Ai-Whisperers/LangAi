---
name: create-update-roadmap
description: "Please create or update a roadmap for a ticket folder with subtickets"
category: ticket
argument-hint: "Ticket folder path, ticket IDs, key artifacts"
tags:
  - ticket
  - roadmap
  - planning
  - update
---

# Create or Update Ticket Roadmap

Use this when a ticket folder or a single ticket with multiple subtickets/tasks needs a clear roadmap with milestones, owners, dependencies, and dates.

## Purpose
- Produce a single, current roadmap covering the ticket folder and its subtickets.
- Align milestones to owners, dates, dependencies, and risks.
- Capture near-term actions and unknowns to unblock delivery.
- Offer usage modes for quick draft vs. full planning.

## Required Context
- Target scope: `[TICKET_FOLDER_PATH]` # e.g., `tickets/EPP-1234/`
- Ticket ID(s): `[TICKET_IDS]` # primary ticket and any subtickets
- Current artifacts: `[ARTIFACTS]` # e.g., `plan.md, progress.md, tracker.md, status.md`
- Known tasks/subtickets with status: `[TASK_LIST]` # list with status/owner/due
- Milestones/dates: `[MILESTONES]` # release windows, key checkpoints
- Constraints/dependencies: `[DEPENDENCIES]` # cross-team or external
- Owners/roles: `[OWNERS]` # primary and secondary

## Optional Context
- Delivery cadence or sprints: `[CADENCE]`
- Risk register or known blockers: `[RISKS]`
- Definition of done for roadmap items: `[DOD]`
- Staging/production release windows: `[RELEASE_WINDOWS]`
- Critical dependencies: `[CRITICAL_DEPS]`

## Reasoning Process
1. Confirm scope, artifacts, and subtickets.
2. Normalize tasks with owners/status/dates.
3. Build milestone ladder and map tasks to milestones.
4. Add dependencies, risks, and near-term actions.
5. Render roadmap in target file and validate completeness.

## Process
1. **Ingest Inputs**
   - Load `[TICKET_FOLDER_PATH]` artifacts: plan/status/progress/trackers.
   - Normalize task list with IDs, titles, status, owners, due dates.
2. **Define Goals & Scope**
   - State objective(s) for the roadmap and what is out of scope.
   - Map subtickets/tasks to the objective(s).
3. **Structure Milestones**
   - Draft milestone ladder (Now/Next/Later or dated milestones).
   - Align each milestone to subtickets/tasks and owners.
   - Capture dependencies and unblockers per milestone.
4. **Plan Delivery**
   - Create dated timeline with buffer; flag critical path.
   - Add acceptance/DOD per milestone.
5. **Surface Risks & Actions**
   - List risks/blockers with owner + mitigation.
   - Call out unknowns that need discovery tasks.
6. **Output Roadmap**
   - Render to the format below; prefer updating `roadmap.md` in `[TICKET_FOLDER_PATH]`.

## Output Format
```
# Roadmap – [TICKET_IDS] @ [TICKET_FOLDER_PATH]

## Objective
- [objective(s)]
- Out of scope: [items]

## Milestones
- [Milestone 1] (date or window)
  - Scope: [tasks/subtickets]
  - Owner(s): [names]
  - Dependencies: [list or "none"]
  - DOD: [criteria]
- [Milestone 2] ...

## Timeline
- [date] : [milestone/task] (owner) [status]
- [date] : [dependency/decision] (owner)

## Risks & Blockers
- [risk] — impact, mitigation, owner, due

## Open Questions / Unknowns
- [question] — owner, expected answer date

## Actions (Next 48h)
- [action] — owner, due
```

## Examples
- **Input**: `[TICKET_FOLDER_PATH]=tickets/EPP-1234/, [TICKET_IDS]=EPP-1234,EPP-1235, [ARTIFACTS]=plan.md,progress.md`
- **Expected**:
  - Roadmap with milestones aligned to subtickets
  - Dependencies and risks filled
  - Actions list covering next 48h with owners and due dates

## Usage Modes
- **Quick Draft**: `/create-update-roadmap tickets/EPP-1234/ "EPP-1234" "plan.md,tracker.md"`
- **Full Plan** (with subtickets, risks, cadence): `/create-update-roadmap tickets/EPP-1234/ "EPP-1234,EPP-1235" "plan.md,progress.md,tracker.md,status.md" --cadence "2w sprints" --risks "RISKS.md"`
- **Refresh Existing Roadmap**: `/create-update-roadmap tickets/EPP-1234/ "EPP-1234" "roadmap.md,progress.md" --deps "API-Gateway,Payments"`

## Troubleshooting
- **Missing artifacts**: Verify `[ARTIFACTS]` paths; if absent, note gaps and proceed with available data.
- **No subticket mapping**: Ensure `[TASK_LIST]` includes IDs; otherwise mark items as unmapped.
- **Date conflicts**: If milestones overlap with `[RELEASE_WINDOWS]`, flag in Risks & Blockers.

## Usage
- `/create-update-roadmap tickets/EPP-1234/ "EPP-1234,EPP-1235" "plan.md,progress.md,tracker.md"`

## Validation
- [ ] Uses latest status from `[TICKET_FOLDER_PATH]` artifacts
- [ ] Every subticket/task mapped to a milestone or explicitly out of scope
- [ ] Owners and dates present for milestones and near-term actions
- [ ] Dependencies and risks captured with mitigations
- [ ] Roadmap stored/updated at `roadmap.md` in `[TICKET_FOLDER_PATH]`

## Related
- `.cursor/rules/ticket/plan-rule.mdc`
- `.cursor/rules/ticket/status-rule.mdc`
- `.cursor/rules/ticket/timeline-tracking-rule.mdc`
- `.cursor/prompts/roadmap/catalog-roadmaps.prompt.md`
