---
name: check-naming-conventions
description: "Analyze naming conventions compliance"
category: code-quality
tags: code-quality, naming, conventions, analysis, standards
argument-hint: "File/folder path to analyze"
---

# Check Naming Conventions

Please analyze naming conventions in:

**Target**: `[REPLACE WITH FILE/FOLDER PATH]`

## Naming Analysis

1. **Classes and Interfaces**:
   - PascalCase used correctly?
   - Names are nouns or noun phrases?
   - Interface names start with 'I'?
   - Names are descriptive and meaningful?
   - Avoid generic names (Manager, Helper, Utility)?

2. **Methods**:
   - PascalCase used correctly?
   - Names are verbs or verb phrases?
   - Intention-revealing names?
   - Async methods end with 'Async'?
   - Boolean methods ask questions (Is, Has, Can, Should)?

3. **Properties and Fields**:
   - Properties: PascalCase
   - Private fields: _camelCase with underscore
   - Boolean properties read like questions
   - Collection names are plural
   - Avoid abbreviations

4. **Variables and Parameters**:
   - camelCase used correctly?
   - Names are meaningful (not x, y, temp, data)?
   - Loop counters are acceptable (i, j, k)
   - Names reflect purpose, not type
   - Avoid Hungarian notation

5. **Constants and Enums**:
   - Constants: PascalCase
   - Enum types: PascalCase (singular)
   - Enum values: PascalCase
   - Names clearly indicate their purpose

6. **Namespaces**:
   - Follow company.product.feature pattern
   - PascalCase
   - Logical organization
   - No abbreviations

## Specific Checks

- Unclear abbreviations (btn, txt, mgr, svc)
- Single-letter names (except loops)
- Type information in names (strName, intValue)
- Generic names (data, info, temp, obj)
- Inconsistent casing
- Misleading names (name doesn't match behavior)
- Overly long names (>30 characters)
- Overly short names (<3 characters)

## Deliverable

Provide:
1. Summary of naming issues by category
2. Specific examples of poor names with suggestions
3. Patterns of naming inconsistency
4. Recommended renamings (show before/after)
5. Priority order for renames

Apply standards from `.cursor/rules/naming-conventions.mdc`.

Note: Do not make changes yet, provide the analysis first.
