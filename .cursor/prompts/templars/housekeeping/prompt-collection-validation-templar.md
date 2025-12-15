---
type: templar
applies-to: prompt-governance
pattern-name: prompt-collection-validation
version: 1.0.0
---

# [Asset Collection] Coverage Validation

## Purpose
Validate that every asset folder has a collection manifest and every asset file is referenced, proposing stubs where missing.

## Required Context
- Assets root (e.g., `[ASSET_ROOT]`)
- Collections root (e.g., `[COLLECTIONS_ROOT]`)

## Process
1. **List Folders**: Enumerate child folders under `[ASSET_ROOT]` (exclude `collections`, `templars`, `exemplars`, `extracted`). Identify folders containing `[FILE_PATTERN]` (e.g., `*.prompt.md`).
2. **Map Assets to Folders**: Collect asset files per folder.
3. **Read Manifests**: Load all `*.collection.yml` under `[COLLECTIONS_ROOT]`.
4. **Cross-Check Coverage**:
   - Folder coverage: each asset-containing folder should have a matching collection manifest.
   - Asset coverage: every asset file appears in at least one manifest `items.path`.
   - Path validity: each referenced path exists.
5. **Handle Missing Collections**:
   - For folders without collections, propose minimal manifest stubs (id/name/description/tags/version/owner/items).
   - Keep one unified output; avoid splitting creation vs validation flows.
6. **Report Gaps**: List missing collections, missing asset entries, broken paths.
7. **Recommend Fixes**: Provide `items:` additions and stub manifests.

## Output Format
```
## Validation Summary
- Assets root: [ASSET_ROOT]
- Collections root: [COLLECTIONS_ROOT]
- Folders with assets: [N]
- Collections found: [N]

## Missing Collections
- [folder] → create [folder].collection.yml
... or "None"

## Missing Asset Entries
- [folder/file] → add to [collection-file]
... or "None"

## Broken Paths in Collections
- [collection-file] -> [path] (not found on disk)
... or "None"

## New Collection Stubs (if missing)
- [folder] -> propose [folder].collection.yml
```yaml
id: [folder]-bundle
name: "[Folder Title]"
description: "[Short purpose]"
tags: [tag1, tag2]
version: 1.0.0
owner: team-prompts
items:
  - path: [relative-path-to-asset]
    kind: prompt
```
... or "None"

## Suggested Fixes
- [Actionable steps or patch list]
```

## Validation Checklist
- [ ] All asset folders have a collection manifest
- [ ] Every asset file is listed in at least one collection
- [ ] All `items.path` entries exist
- [ ] Missing collections have stub manifests proposed
- [ ] Suggested fixes included for every gap

