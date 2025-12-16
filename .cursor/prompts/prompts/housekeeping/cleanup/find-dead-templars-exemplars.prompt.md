---
name: find-dead-templars-exemplars
description: "Please detect unused templars/exemplars and report dead nodes with fixes"
category: housekeeping
tags: housekeeping, prompts, templars, exemplars, hygiene
argument-hint: "root folder (optional, defaults to .cursor/prompts)"
---

# Find Dead Templars/Exemplars

Please scan for templars/exemplars that are no longer referenced by any prompt, rule, or consumer and produce a remediation plan.

## Purpose
Keep the prompt library lean by identifying “dead nodes” (templars/exemplars with no consumers) and proposing fixes (add cross-links, archive, or delete).

## Required Context
- Root path to scan (default: `.cursor/prompts`)
- Known consumer folders (prompts, rules, scripts) if not default
- Inclusion/exclusion globs if needed (optional)

## Process
1. **Discover**: List all templars/exemplars under `.cursor/prompts/templars` and `.cursor/prompts/exemplars`.
2. **Parse Metadata**: For each, read frontmatter fields: `implements`/`illustrates`, `extracted-from`, `consumed-by`.
3. **Build Links**: Search prompts/rules/scripts for references to each templar/exemplar (by filename and by ID fields like `consumed-by`, `illustrates`, `implements`).
4. **Detect Dead Nodes**:
   - Templars with no `consumed-by` and no textual references.
   - Exemplars with no `illustrates` and no textual references.
   - Missing or empty `implements`/`illustrates`.
5. **Report**:
   - Dead candidates with path, missing fields, and suggested action.
   - Missing metadata (fill in `implements`/`illustrates`, `consumed-by`).
   - Collisions/duplicates (same `implements`/`illustrates` across multiple files).
6. **Recommend Fix**:
   - If truly unused: mark for archive/delete.
   - If needed: add frontmatter references (`consumed-by`, `extracted-from`), or link from prompts/rules.
7. **Output**: Summarize counts; provide per-item action list.

## Expected Output
- Summary counts: total templars, total exemplars, dead candidates, missing metadata, duplicates.
- Table of dead candidates: path, reason (no consumers / missing fields), proposed action.
- Table of metadata issues: path, missing fields, suggested values.
- Optional: suggested `Select-String`/`rg` commands to confirm absence of references.

## Script
- `.cursor/scripts/housekeeping/find-dead-templars-exemplars.ps1`
  - Console summary (default): `pwsh -File .cursor/scripts/housekeeping/find-dead-templars-exemplars.ps1`
  - JSON: `pwsh -File .cursor/scripts/housekeeping/find-dead-templars-exemplars.ps1 -Json`
  - PassThru object: `pwsh -File .cursor/scripts/housekeeping/find-dead-templars-exemplars.ps1 -PassThru`

## Quality Criteria
- [ ] No path-based assumptions beyond provided root.
- [ ] Flags both missing references and missing metadata.
- [ ] Does not propose deletion without a remediation note.
- [ ] References use file paths, not guesses.
- [ ] Output is concise and actionable.

## Related
- `.cursor/prompts/housekeeping/extract-templar-exemplar.prompt.md`
- `scripts/housekeeping/extract-templar-exemplar.ps1`
