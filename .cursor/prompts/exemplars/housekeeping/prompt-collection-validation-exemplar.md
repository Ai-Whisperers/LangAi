---
type: exemplar
demonstrates: prompt-collection-validation
category: housekeeping/prompts
quality-score: exceptional
version: 1.0.0
---

# Validate Prompt Collections (Exemplar)

## Purpose
Ensure every prompt folder has a collection manifest and each `*.prompt.md` file is included in at least one collection entry. If a folder is missing a collection, propose (or create) a minimal manifest stub so creation is covered in the same run.

## Required Context
- Base folder containing prompts (e.g., `.cursor/prompts`)
- Collection manifests location (e.g., `.cursor/prompts/collections`)

## Quickstart
- Run with defaults (root at `.cursor/prompts`): `@validate-prompt-collections`
- Custom root: `@validate-prompt-collections path/to/prompts`
- Save the report and apply suggested stubs/additions in one pass.

## Process
1. **List Folders**: Enumerate immediate child folders under `[PROMPTS_ROOT]` (exclude `collections`, `exemplars`, `templars`, `extracted`). Identify folders containing `*.prompt.md`.
2. **Map Prompts to Folders**: For each folder, collect prompt files.
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

## Output Format
```
## Validation Summary
- Prompts root: [PROMPTS_ROOT]
- Collections root: [COLLECTIONS_ROOT]
- Folders with prompts: [N]
- Collections found: [N]

## Missing Collections
- [folder] → create [folder].collection.yml
... or "None"

## Missing Prompt Entries
- [folder/file.prompt.md] → add to [collection-file]
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
  - path: prompts/[folder]/[file].prompt.md
    kind: prompt
```
... or "None"

## Suggested Fixes
- [Actionable steps or patch list]
```

## Validation Checklist
- [ ] All prompt folders have a collection manifest
- [ ] Every `*.prompt.md` is listed in at least one collection
- [ ] All `items.path` entries exist
- [ ] Missing collections have stub manifests proposed
- [ ] Suggested fixes included for every gap

## Examples

### Example: Missing collection and missing entries
```
## Validation Summary
- Prompts root: .cursor/prompts
- Collections root: .cursor/prompts/collections
- Folders with prompts: 2
- Collections found: 1

## Missing Collections
- script → create script.collection.yml

## Missing Prompt Entries
- prompt/improve-prompt.prompt.md → add to prompt.collection.yml

## Broken Paths in Collections
- None

## New Collection Stubs (if missing)
- script -> propose script.collection.yml
```yaml
id: script-bundle
name: "Script Prompts"
description: "Prompts for building and improving scripts"
tags: [scripting, automation]
version: 1.0.0
owner: team-prompts
items:
  - path: prompts/script/add-caching.prompt.md
    kind: prompt
```

## Suggested Fixes
- Add `prompt/improve-prompt.prompt.md` to prompt.collection.yml
- Create script.collection.yml using stub above
```
