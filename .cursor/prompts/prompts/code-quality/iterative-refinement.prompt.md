---
name: iterative-refinement
description: "Requests focused fixes for specific issues without rebuilding everything"
category: code-quality
tags: code-quality, refinement, iteration, fixes, focused
argument-hint: "Specific issue description in <issue> tags"
---

# Iterative Refinement (Pattern-Based)

This prompt requests focused fixes for specific issues without rebuilding everything.

**Pattern**: Iterative Refinement Pattern ⭐⭐⭐⭐  
**Effectiveness**: Fast iteration, focused fixes  
**Use When**: Fixing specific issues, adjusting details, correcting previous implementation

---

## Required Context

- **Issue Description**: Specific problem to fix (values, ordering, format, behavior)
- **Current Behavior**: What's happening now (optional but helpful)
- **Desired Behavior**: What should happen instead

---

## Reasoning Process

The AI should:
1. **Identify Scope**: Understand exactly what needs fixing (not everything)
2. **Locate Problem**: Find the code/logic causing the issue
3. **Propose Minimal Fix**: Change only what's needed to resolve issue
4. **Preserve Working Code**: Don't touch unrelated functionality
5. **Verify Fix**: Test that issue is resolved
6. **Report Result**: Confirm what was changed

---

## Basic Usage

```
<issue>
[SPECIFIC_ISSUE_DESCRIPTION]

[WHAT_NEEDS_TO_CHANGE]
</issue>
```

**Note**: XML delimiters help isolate the issue description from other context.

---

## Examples

### Fix Field Value Issue
```
Country EntityID is 0

same for Market, MarketParty, and I think all of them

also EntityID should be first field
```

### Fix Field Ordering
```
EntityID should be the first field in all exports

Currently it's appearing after other fields
```

### Correct Data Issues
```
Parent reference columns are generating but showing no data

The columns exist with correct headers but all values are empty
```

### Adjust Format
```
Date fields are exporting with time component

Should be date-only format: YYYY-MM-DD
```

---

## Refinement Types

### 1. Value Corrections
```
[FIELD/PROPERTY] is showing [WRONG_VALUE], should be [CORRECT_VALUE]
```

**Example:**
```
EntityID is showing 0, should show actual database ID values
```

---

### 2. Ordering Changes
```
[ITEM] should be [POSITION], currently it's [CURRENT_POSITION]
```

**Example:**
```
EntityID should be first column, currently it's appearing after Name
```

---

### 3. Behavior Adjustments
```
[FEATURE] is doing [CURRENT_BEHAVIOR], should do [DESIRED_BEHAVIOR]
```

**Example:**
```
Export is creating separate files, should consolidate into one workbook
```

---

### 4. Addition Requests
```
Also add [FEATURE/FIELD]

[OPTIONAL: WHERE/HOW]
```

**Example:**
```
Also add Country Name column

Place it after Country Code
```

---

### 5. Removal Requests
```
Remove [FEATURE/FIELD] from [LOCATION]

[OPTIONAL: REASON]
```

**Example:**
```
Remove the Debug column from export

It's not needed in production exports
```

---

## Multiple Issues

When reporting multiple related issues:

```
Issue 1: [FIRST ISSUE]
Issue 2: [SECOND ISSUE]  
Issue 3: [THIRD ISSUE]

These are all in [LOCATION/FILE]
```

### Example
```
Issue 1: EntityID showing as 0
Issue 2: EntityID should be first field
Issue 3: Name field has trailing spaces

These are all in the Market export
```

---

## What This Pattern Does

✅ Focused scope - fix X, not rebuild everything  
✅ Builds on previous work  
✅ Specific problem statement  
✅ Fast iteration cycle  
✅ Preserves working features  

---

## With Examples

Include examples of wrong vs. right:

```
[ISSUE DESCRIPTION]

Current output:
[SHOW WRONG BEHAVIOR]

Expected output:
[SHOW RIGHT BEHAVIOR]
```

### Example
```
Date format is incorrect

Current output: 2025-11-30T14:23:45.123Z
Expected output: 2025-11-30
```

---

## With Context

If issue appeared after a change:

```
After [RECENT CHANGE], [ISSUE OBSERVED]

[WHAT NEEDS FIXING]
```

### Example
```
After adding Code support, EntityID values are all 0

Need to fix EntityID population while keeping Code export working
```

---

## Scoped to Files

```
In [FILE/COMPONENT]: [ISSUE]

[FIX NEEDED]
```

### Example
```
In ExcelExportService.cs: EntityID column always exports 0

Need to use entity.EntityID instead of default value
```

---

## Expected AI Response

AI will:
1. **Identify** the affected code
2. **Propose** targeted fix
3. **Implement** minimal change needed
4. **Preserve** working functionality
5. **Test** if requested

---

## Follow-up Workflow

### Round 1: Report Issue
```
EntityID is 0, should show actual values
```

### Round 2: Verify Fix
```
Good! Now also fix the field ordering - EntityID should be first
```

### Round 3: Test
```
Perfect! Please test the export to verify all fields correct
```

---

## Tips for Effective Refinement

- **Be specific** - "EntityID is 0" > "Data is wrong"
- **One scope at a time** - Fix values, then ordering, then formatting
- **Provide examples** - Show wrong vs. right
- **State locations** - Name the file/component if known
- **Verify each** - Test after each refinement
- **Iterate quickly** - Don't try to fix everything at once

---

## Anti-Pattern (Don't Do This)

❌ **Too vague**:
```
The data doesn't look right
```

❌ **Too many issues at once**:
```
Fix EntityID, reorder columns, change date format, update validation, add logging, refactor service
```

✅ **Specific and focused**:
```
EntityID is showing 0, should show actual database ID values
```
[Fix applied]
```
Now EntityID should be first column
```
[Fix applied]
```
Now date format should be YYYY-MM-DD only
```

---

## Refinement Cycle

```
1. Initial Implementation
   ↓
2. Refinement 1: Fix values
   ↓
3. Refinement 2: Adjust ordering
   ↓  
4. Refinement 3: Polish formatting
   ↓
5. Final: Test and validate
```

---

## Multi-Entity Refinement

```
This issue affects multiple entities:
- Country: [ISSUE]
- Market: [ISSUE]
- MarketParty: [ISSUE]

Appears to be same pattern across all of them
```

---

## Priority Refinements

```
Critical: [MUST FIX]

Nice to have: [OPTIONAL IMPROVEMENT]
```

### Example
```
Critical: EntityID must have actual values (currently 0)

Nice to have: Add tooltips to column headers
```

---

## Expected AI Response

When you report an issue for refinement:

1. **Acknowledge Issue**
   ```
   Issue understood: [Brief restatement]
   ```

2. **Identify Location**
   ```
   Found in: [File/method/component]
   ```

3. **Propose Fix**
   ```
   Fix: [Specific change to make]
   ```

4. **Implement Minimal Change**
   - Change only what's needed
   - Preserve working functionality
   - Test the fix

5. **Confirm Result**
   ```
   ✅ Fixed: [Issue is now resolved]
   [Brief explanation of change made]
   ```

---

## Quality Criteria

For effective refinement requests:

- [ ] Issue is specific (not vague like "data is wrong")
- [ ] Scope is focused (one issue at a time)
- [ ] Desired outcome is clear
- [ ] Examples provided (current vs expected)

For AI fixes:

- [ ] Only affected code changed (minimal scope)
- [ ] Working features preserved (no collateral damage)
- [ ] Issue actually resolved (not just shifted)
- [ ] Change explained clearly
- [ ] Ready for next refinement if needed

---

## Refinement Cycle

Fast iteration pattern:

```
Round 1: Report issue → AI fixes → Verify
Round 2: Report next issue → AI fixes → Verify
Round 3: Report formatting tweak → AI adjusts → Done
```

**Key**: One focused change per round = fast, clean iterations

---

## Effective vs Ineffective Refinement

❌ **Too vague**:
```
The data doesn't look right
```
→ AI doesn't know what to fix

❌ **Too broad**:
```
Fix EntityID, reorder columns, change date format, update validation, add logging
```
→ Too many changes at once, hard to verify

✅ **Focused and specific**:
```
EntityID is showing 0, should show actual database ID values
```
→ AI knows exactly what to fix

✅ **One thing at a time**:
```
First fix: EntityID values
[Fixed]
Second fix: EntityID should be first column
[Fixed]
Third fix: Date format should be YYYY-MM-DD only
```
→ Clean, verifiable iterations

---

## Related Prompts

- `code-quality/report-errors.md` - For compilation/runtime errors (not refinements)
- `code-quality/request-feature.md` - For new functionality (not fixes)
- `ticket/activate-ticket.md` - Return to ticket after refinements

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)  
**Pattern ID**: #9 Iterative Refinement Pattern  
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0

