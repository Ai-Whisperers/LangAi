---
name: validate-prompt-collections
description: "Validate prompt collections cover all prompt folders and items"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags:
  - housekeeping
  - prompts
  - collections
  - validation
argument-hint: "Root path to prompts folder (default: .cursor/prompts)"
---

# Validate Prompt Collections

Ensure every prompt folder has a collection manifest and that each prompt file is included in at least one collection entry. If a folder is missing a collection, propose (or create) a minimal manifest stub so creation is covered in the same run.

## Required Context

- Base folder containing prompts (e.g., `.cursor/prompts`)
- Collection manifests location (e.g., `.cursor/prompts/collections`)

## Quickstart

- Run with defaults (root at `.cursor/prompts`): `@validate-prompt-collections`
- Custom root: `@validate-prompt-collections path/to/prompts`
- Save the report and apply suggested stubs/additions in one pass.

## Pattern References

- Templar: `.cursor/prompts/templars/housekeeping/prompt-collection-validation-templar.md`
- Exemplar: `.cursor/prompts/exemplars/housekeeping/prompt-collection-validation-exemplar.md`

## Process

1. **List Folders**: Enumerate immediate child folders under `[PROMPTS_ROOT]` (exclude `collections`, `exemplars`, `templars`, `extracted`). Identify folders containing `*.prompt.md`.
2. **Map Prompts to Folders**: For each folder, collect prompt files (`*.prompt.md`).
3. **Read Manifests**: Load all `*.collection.yml` under `[PROMPTS_ROOT]/collections`.
4. **Cross-Check Coverage**:
   - Folder coverage: each prompt-containing folder should have a corresponding collection file.
   - Prompt coverage: every `*.prompt.md` should appear in at least one manifest `items.path`.
   - Path validity: verify referenced files exist.
5. **Handle Missing Collections (Creation Pass)**:
   - For each folder without a collection, propose a minimal manifest stub (id/name/description/tags/version/owner/items) that lists that folder’s prompt files.
   - Keep one unified output; avoid creating multiple prompts for creation vs validation.
6. **Report Gaps**: List missing collections, missing prompt entries, and broken paths.
7. **Recommend Fixes**: Provide `items:` additions and stub manifests where needed.

## Usage

```text
@validate-prompt-collections                    # default: .cursor/prompts
@validate-prompt-collections prompts            # explicit relative root
@validate-prompt-collections ../other/prompts   # alternate root

# Script alternative (with progress bar and exit code):
pwsh .cursor/scripts/housekeeping/validate-prompt-collections.ps1 -PromptsRoot ".cursor/prompts"
```
