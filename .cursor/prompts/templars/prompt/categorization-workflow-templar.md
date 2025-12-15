---
type: templar
applies-to: organization, categorization, cleanup, migration, restructuring
pattern-name: categorization-workflow
version: 1.0.0
implements: prompt.organize
extracted-from: .cursor/prompts/prompt/organize-prompts.prompt.md
consumed-by:
  - .cursor/prompts/prompt/organize-prompts.prompt.md
---

# Categorization Workflow Templar

## Pattern Purpose

This template provides a structured approach to organizing, categorizing, and moving artifacts into appropriate locations. It includes inventory, decision trees for categorization, batch operations, and validation to ensure proper organization.

## When to Use

Use this pattern when creating organization/categorization prompts for:
- **File organization** - Moving files into proper folder structures
- **Code refactoring** - Reorganizing code into appropriate modules/packages
- **Documentation organization** - Categorizing documentation by topic/audience
- **Artifact cleanup** - Moving items from staging/temp to permanent locations
- **Migration tasks** - Restructuring legacy systems into new organization

**Criteria for This Pattern**:
- ✅ Multiple artifacts need categorization
- ✅ Clear category system exists (or needs definition)
- ✅ Decision criteria for categorization can be articulated
- ✅ Batch operations more efficient than one-by-one
- ✅ Validation confirms proper organization

## Template Structure

```markdown
# Organize [Artifact Type]

Please analyze and organize [artifacts] into appropriate [category structure] following [organizational principles].

## Purpose

This prompt categorizes [uncategorized/miscategorized artifacts], moves them to correct [locations], updates their [metadata], and ensures the [system] stays well-organized.

## Expected Output

This prompt will produce:
1. **Organization plan** showing what needs to move where and why
2. **[Operation type] operations** (or commands to execute)
3. **[Metadata] updates** for [metadata fields]
4. **Validation report** confirming proper organization

## Reasoning Process

Before organizing:
1. **Inventory Current State**: What [artifacts] exist and where?
2. **Understand Purpose**: What does each [artifact] do?
3. **Match to [Category]**: Which [category] best fits each [artifact]?
4. **Plan Moves**: What needs to move and what updates are needed?
5. **Validate Organization**: Does final structure make sense?

## Organization Principles

### 1. [Category System Name]

**[Category Type] Categories**:
- `[category-1]/` - [Description and criteria]
- `[category-2]/` - [Description and criteria]
- `[category-3]/` - [Description and criteria]
- `[category-4]/` - [Description and criteria]
- `[category-5]/` - [Description and criteria]
- `[category-6]/` - [Description and criteria]
[... more categories]

### 2. Special [Locations]

**[Special Location Type]**:
- `[special-1]/` - [Purpose and when to use]
- `[special-2]/` - [Purpose and when to use]
- `[special-3]/` - [Purpose and when to use]

**Purpose**:
- [Special location 1]: [Why it exists]
- [Special location 2]: [Why it exists]
- [Special location 3]: [Why it exists]

### 3. [Naming/Identification] Consistency

**[Naming Aspect 1]**:
- Format: `[naming-pattern]`
- Example: `[example-name]`
- Avoid: [Anti-patterns]

**[Naming Aspect 2]**:
- Must match [other field]
- Example: `[example]`

## Organization Process

### Step 1: Inventory

Scan for [misplaced/uncategorized artifacts]:

1. **Check [location 1]**:
   - Review [artifacts] awaiting [action]
   - Identify their [purpose/type]
   - Determine appropriate [category]

2. **Check [location 2]**:
   - Identify [artifacts] not in [proper location]
   - Assess if they should be [categorized]

3. **Check [category fit]**:
   - Verify [artifacts] are in correct [category]
   - Identify [miscategorized artifacts]

### Step 2: Categorize

For each [uncategorized artifact]:

**Decision Tree**:
```
[Question 1]? → [category-1]/
[Question 2]? → [category-2]/
[Question 3]? → [category-3]/
[Question 4]? → [category-4]/
[Question 5]? → [category-5]/
[Question 6]? → [category-6]/
[Question 7]? → [category-7]/
[Question 8]? → [category-8]/
[Question 9]? → [category-9]/
[Question 10]? → [category-10]/

None of above? → [Default action or new category]
```

### Step 3: Move & Update

For each [artifact] to move:

1. **Move [artifact]** to target [category location]
2. **Update [metadata field]** in [metadata location]
3. **Update [related fields]** if needed
4. **Validate** with `@[validation-prompt]`

### Step 4: Clean [Special Locations]

**[Special Location 1] [Location]**:
- Should be [purpose/status]
- All [artifacts] should be [final state]
- Keep only those [exception criteria]

**[Special Location 2] [Location]**:
- Keep only [criteria]
- Each should [requirement]
- Document [what aspect]

**[Special Location 3] [Location]**:
- Keep only [criteria]
- Each should [requirement]
- Document [what aspect]

## Organization Output

```markdown
## Organization Plan

### [Uncategorized Type] Found
1. `[location]/[artifact-1]` → Suggested: `[category-1]/`
   - **Reason**: [Why this category]
2. `[location]/[artifact-2]` → Suggested: `[category-2]/`
   - **Reason**: [Why this category]

### [Miscategorized Type]
1. `[wrong-location]/[artifact-3]` → Move to: `[correct-location]/`
   - **Reason**: [Why it should move]

### New [Categories] Needed
- `[new-category]/` - For [purpose]

### Actions

#### Phase 1: [Move Operation Type]
[Commands or operations to execute]

#### Phase 2: [Update Operation Type]
[List of items needing updates]

#### Phase 3: Validation
[Validation checks to run]

## Validation

After organization:
- [ ] All [artifacts] in appropriate [categories]
- [ ] No [artifacts] in [staging location] (or all are WIP)
- [ ] [Category] [locations] have consistent [naming]
- [ ] All [artifacts] pass [validation]
- [ ] [Index/manifest] updated (if applicable)
```

## Batch Organization

**Organize [specific location]**:
```
@[prompt-name] [location]/
```

**Full [system] organization**:
```
@[prompt-name] all
```

**Check specific [location]**:
```
@[prompt-name] [location]/
```

## Organization Checklist

- [ ] Inventory completed
- [ ] All [artifacts] categorized
- [ ] [Artifacts] moved to correct [locations]
- [ ] [Metadata] [fields] updated
- [ ] All [artifacts] validated
- [ ] No duplicates between [locations]
- [ ] [Special locations] cleaned up
- [ ] [Documentation] updated

## Best Practices

### DO
- ✅ Keep [categories] focused and clear
- ✅ Use existing [categories] when possible
- ✅ Update [metadata] when moving [artifacts]
- ✅ Validate after moving
- ✅ Document organization decisions

### DON'T
- ❌ Create too many [categories]
- ❌ Put [artifacts] in multiple [categories] (choose one)
- ❌ Leave [staging location] full
- ❌ Forget to update [metadata] in [metadata location]
- ❌ Break existing [artifact] references

## Examples (Few-Shot)

### Example 1: Complete Organization Workflow

**Scenario**: [N] [artifacts] in `[staging-location]/` need organization

**[Artifacts] to Organize**:
```
[staging-location]/
├── [artifact-1]
├── [artifact-2]
├── [artifact-3]
├── [artifact-4]
└── [artifact-5]
```

**Step 1: Analysis**

1. **[artifact-1]**
   - Purpose: [Description]
   - → Category: `[category-1]/`

2. **[artifact-2]**
   - Purpose: [Description]
   - → Category: `[category-2]/`

3. **[artifact-3]**
   - Purpose: [Description]
   - → Category: `[category-3]/`

4. **[artifact-4]**
   - Purpose: [Description]
   - → Category: `[category-4]/`

5. **[artifact-5]**
   - Purpose: [Description]
   - → Category: `[category-5]/`

**Step 2: Execute Moves** ([Shell/Command Format]):
```[shell]
[Command to move artifact-1 to category-1]
[Command to move artifact-2 to category-2]
[Command to move artifact-3 to category-3]
[Command to move artifact-4 to category-4]
[Command to move artifact-5 to category-5]
```

**Step 3: Update [Metadata]** (Example):
```[format]
Before:
[metadata-before]

After:
[metadata-after with category updated]
```

**Step 4: Validate**:
```
@[validation-prompt] [category-1]/[artifact-1]
✅ PASS ([score]%)

@[validation-prompt] [category-2]/[artifact-2]
✅ PASS ([score]%)
```

**Final Structure**:
```
[root]/
├── [category-1]/[artifact-1]
├── [category-2]/[artifact-2]
├── [category-3]/[artifact-3]
├── [category-4]/[artifact-4]
├── [category-5]/[artifact-5]
└── [staging-location]/ [empty - all organized]
```

## Related [Prompts]

- `@[creation-prompt]` - Create properly categorized [artifacts]
- `@[validation-prompt]` - Validate after organizing
- `@[improvement-prompt]` - Improve [artifact] quality

## Usage

**Quick organization**:
```
@[prompt-name] [staging-location]/
```

**Full audit**:
```
@[prompt-name] all --audit
```

**Interactive**:
```
@[prompt-name] --interactive
```

## Migration Helper

When moving [artifacts]:

```[shell]
# Move [artifact]
[Move command syntax]

# Update [metadata field]
# Validate
@[validation-prompt] [target-location]/[artifact-name]
```

## Organization Report Template

```markdown
# [Artifact Type] Organization Report

**Date**: YYYY-MM-DD
**Scope**: [[Location] or 'All']

## Summary
- **Total [artifacts] analyzed**: [N]
- **Properly organized**: [N]
- **Needing organization**: [N]
- **[Categories] used**: [N]

## Actions Taken
1. Moved [N] [artifacts] to correct [categories]
2. Created [N] new [categories]
3. Updated [N] [metadata fields]
4. Cleaned [N] [artifacts] from [staging location]

## Current Structure
[Tree view of organized structure]

## Recommendations
1. [Recommendation]
2. [Recommendation]
```
```

## Customization Points

### Category System
**Placeholder**: `[category-1]`, `[category-2]`, etc.  
**Guidance**: Define the category structure for your domain. List all standard categories with clear descriptions and criteria.

### Decision Tree
**Placeholder**: `[Question N]? → [category-N]/`  
**Guidance**: Create questions that map artifacts to categories. Questions should be yes/no or clear criteria checks.

### Special Locations
**Placeholder**: `[special-1]/`, `[staging-location]/`, etc.  
**Guidance**: Identify temporary/special locations in your system (staging, extracted, templates, etc.).

### Move Operations
**Placeholder**: `[Command to move...]`, `[Move command syntax]`  
**Guidance**: Provide actual commands for your platform (PowerShell, bash, Git, etc.).

### Metadata Updates
**Placeholder**: `[metadata field]`, `[metadata-before]`, `[metadata-after]`  
**Guidance**: Show what metadata fields need updating when artifacts move (category field, tags, paths, etc.).

## Example Usage (Applying This Templar)

### Creating "Organize Test Files" Prompt

**Categories**: `unit/`, `integration/`, `e2e/`, `fixtures/`, `mocks/`

**Decision Tree**: 
- Tests single function? → `unit/`
- Tests multiple services? → `integration/`
- Tests full system? → `e2e/`
- Test data? → `fixtures/`
- Mock objects? → `mocks/`

**Special Locations**: `temp-tests/` (staging), `archived-tests/` (deprecated)

**Result**: Organization prompt that scans test files, categorizes by type, moves to correct folders, updates import paths.

## Related Templars

- `guided-creation-workflow-templar.md` - Creates properly categorized artifacts
- `multi-level-validation-templar.md` - Validates organization quality
- `enhancement-workflow-templar.md` - Improves organization structure

## Best Practices

### DO
- ✅ Provide comprehensive decision tree covering all cases
- ✅ Show example workflow from start to finish
- ✅ Include validation after moves
- ✅ Update metadata when moving artifacts
- ✅ Clean staging areas after organization
- ✅ Generate organization report

### DON'T
- ❌ Create overlapping categories (causes confusion)
- ❌ Skip metadata updates (causes inconsistency)
- ❌ Forget to validate after moves
- ❌ Leave staging full (defeats organization purpose)
- ❌ Break references when moving (causes errors)

## Success Metrics

Good application of this pattern achieves:
- **Clarity**: Clear category definitions and decision criteria
- **Completeness**: All artifacts categorized, none left in staging
- **Consistency**: Metadata matches locations
- **Efficiency**: Batch operations faster than one-by-one
- **Maintainability**: Organization system easy to understand and maintain

---

**Pattern Provenance**: Extracted from `organize-prompts.prompt.md` which demonstrates exceptional categorization workflow with comprehensive decision trees, batch operations, validation, and complete workflow examples from inventory to final structure.
