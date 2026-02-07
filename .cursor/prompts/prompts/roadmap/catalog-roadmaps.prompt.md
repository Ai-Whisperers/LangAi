---
name: catalog-roadmaps
description: "Please catalog ticket-level and folder-level roadmaps, including gaps"
category: ticket
argument-hint: "Tickets root path, roadmap patterns, optional focus tickets"
tags:
  - ticket
  - roadmap
  - catalog
  - tracking
---

# Catalog Ticket Roadmaps

Create a concise catalog of all roadmap files at the ticket-folder level and individual ticket level, and call out missing/placeholder entries that need creation.

## Purpose
- Make a complete inventory of existing roadmaps.
- Highlight missing or placeholder roadmaps per folder/ticket.
- Surface quick actions to create or link missing items.
- Provide multiple usage modes: quick scan or scoped focus.

## Required Context
- Root folder for tickets: `[TICKETS_ROOT]` # e.g., `tickets/` or `tickets/PROMPTS-CONDENSE-CANDS/`
- Roadmap filename patterns: `[ROADMAP_FILENAMES]` # e.g., `roadmap.md, roadmap.prompt.md, roadmap*.md`
- Ticket ID scope to highlight (optional): `[FOCUS_TICKET_IDS]` # CSV or list
- Current status source (optional): `[STATUS_SOURCES]` # e.g., tracker.md, status.md

## Optional Context
- Exclude patterns: `[EXCLUDES]` # e.g., `*/archive/*`
- Default roadmap target filename: `[TARGET_FILENAME]` # e.g., `roadmap.md`
- Owners or teams to flag: `[OWNER_FILTER]`
- Recency threshold (days) to flag stale roadmaps: `[STALE_DAYS]`

## Reasoning Process
1. Confirm target scope and patterns.
2. Enumerate matching files and identify gaps.
3. Extract key signals (scope, milestones, owners, freshness).
4. Produce catalog + gap list with next actions.

## Process
1. **Discover Files**
   - Walk `[TICKETS_ROOT]` and list any file matching `[ROADMAP_FILENAMES]`.
   - For folders without a roadmap, note them as gaps.
2. **Extract Signals**
   - For each roadmap, capture: ticket/folder, purpose, horizons/milestones, owners, dates, and linkage to sub-tickets.
   - Pull last-modified timestamp and presence of open TODOs.
3. **Assess Coverage**
   - Mark folders/tickets lacking a roadmap or containing placeholder content.
   - Note if status sources exist but are disconnected from a roadmap.
4. **Report**
   - Produce a catalog and a gap list (ready-made checklist to create/update).

## Output Format
```
## Roadmap Catalog
- Root: [TICKETS_ROOT]

### Entries
| Path | Scope | Last Updated | Milestones | Owners | Notes |
|------|-------|--------------|------------|--------|-------|
| [file path] | [folder|ticket [ID]] | [date/time] | [comma milestones] | [names] | [status/gaps] |

### Gaps / Actions
- [ticket/folder]: Missing roadmap (create)
- [ticket/folder]: Placeholder only (needs detail)
- [ticket/folder]: Has status tracker but no roadmap (link or merge)
- [ticket/folder]: Roadmap stale (> [STALE_DAYS]d) (refresh)
```

## Examples
- **Input**: `[TICKETS_ROOT]=tickets/, [ROADMAP_FILENAMES]=roadmap.md, [FOCUS_TICKET_IDS]=EPP-1234`
- **Expected**:
  - Catalog table with entries for each `roadmap.md`
  - Gap list for tickets/folders without roadmaps
  - Notes showing last-updated and TODO presence

## Usage Modes
- **Quick Scan** (default): `/catalog-roadmaps tickets/ "roadmap.md,roadmap.prompt.md"`
- **Scoped Focus** (highlight specific tickets): `/catalog-roadmaps tickets/ "roadmap*.md" "EPP-1234,EPP-5678"`
- **Filtered** (exclude archives, flag stale): `/catalog-roadmaps tickets/ "roadmap.md" "" --excludes "*/archive/*" --stale 30`

## Troubleshooting
- **No entries found**: Confirm `[TICKETS_ROOT]` and `[ROADMAP_FILENAMES]` patterns.
- **Too many results**: Add `[EXCLUDES]` or narrow `[FOCUS_TICKET_IDS]`.
- **Stale dates missing**: Ensure filesystem timestamps accessible; otherwise skip staleness flag.

## Usage
- `/catalog-roadmaps tickets/ "roadmap.md,roadmap.prompt.md" EPP-1234`
- `/catalog-roadmaps tickets/PROMPTS-CONDENSE-CANDS/ "roadmap*.md"`

## Validation
- [ ] All roadmap files under `[TICKETS_ROOT]` listed
- [ ] Missing/placeholder roadmaps called out
- [ ] Owners/milestones captured where present
- [ ] Paths are clickable/relative to repo
- [ ] Actions list is specific and actionable

## Related
- `.cursor/rules/ticket/plan-rule.mdc`
- `.cursor/rules/ticket/status-rule.mdc`
- `.cursor/rules/ticket/timeline-tracking-rule.mdc`
- `.cursor/prompts/roadmap/create-update-roadmap.prompt.md`
