---
name: request-feature
description: "Request new features or enhancements with clear requirements"
category: code-quality
tags: code-quality, features, enhancements, requirements, functionality
argument-hint: "Feature description in <feature_request> tags"
---

# Request Feature (Pattern-Based)

This prompt requests new features or enhancements by providing clear description, rationale, and examples.

**Pattern**: Feature Request Pattern ⭐⭐⭐⭐  
**Effectiveness**: 4-5 stars with examples and constraints  
**Use When**: Requesting new features, enhancements, functionality changes

---

## Required Context

- **Need Description**: What functionality is missing or needs improvement
- **Rationale**: Why this feature is needed (use case)
- **Examples/Constraints**: How it should work, with concrete examples

---

## Reasoning Process

The AI should:
1. **Understand Need**: Parse what functionality is being requested
2. **Clarify Scope**: Ask questions if requirements are ambiguous
3. **Propose Approach**: Suggest implementation strategy
4. **Consider Edge Cases**: Think through potential issues
5. **Confirm Understanding**: Summarize proposal before implementing
6. **Implement**: Build the feature systematically

---

## Basic Structure

```
<feature_request>
[DESCRIPTION_OF_NEED]

[CONTEXT_ABOUT_WHY]

[EXAMPLES_OR_CONSTRAINTS]
</feature_request>
```

**Note**: XML delimiters help separate feature description from other context.

---

## Example: Add New Export Capability

```
We export the EntityID from parent relations.

Please adjust to also include the Code of these entries.

The idea is that we can with parameters tell to pass parent relations by ID(Nr) or Code, or both (default)

Place the code export after the ID column.

Besides this, we can then upload based on code, to update fields, without adjusting their number.

also we could regenerate links when uploading.

Some core fields actually have an ID column and an NR column, where the ID is a hardcoded nr (most <1000)

anyway, please add the code support
```

---

## Template Options

### Option 1: Problem-Solution Format

```
**Problem**: [What doesn't work or is missing]

**Solution**: [What you want implemented]

**Details**: [How it should work]

**Constraints**: [Any limitations or requirements]
```

#### Example
```
**Problem**: EntityID exports aren't stable across environments

**Solution**: Export Code values alongside EntityID

**Details**: Add configurable mode (ID only / Code only / Both)

**Constraints**: Must maintain backwards compatibility
```

---

### Option 2: Goal-Oriented Format

```
I want to be able to [GOAL]

[EXPLANATION OF USE CASE]

[OPTIONAL: EXAMPLES OF HOW IT SHOULD WORK]
```

#### Example
```
I want to be able to export by Code or ID, with both as default

This will allow cross-environment data migration without ID adjustment.

For example:
- --export-mode=id → Only EntityID (current behavior)
- --export-mode=code → Only Code values
- --export-mode=both → Both (default, new feature)
```

---

### Option 3: Example-Driven Format

```
Like how [EXISTING FEATURE] works, but for [NEW USE CASE]

[DESCRIBE THE PARALLEL]

[KEY DIFFERENCES]
```

#### Example
```
Like how we export Market entity to Excel, but for the entire domain in one file

Same formatting and metadata approach, but consolidate all related entities into sheets within one workbook

Key difference: Multiple sheets instead of multiple files
```

---

### Option 4: Constraint-First Format

```
Must [REQUIREMENT 1]
Should [REQUIREMENT 2]
Must Not [CONSTRAINT 3]

[FEATURE DESCRIPTION]
```

#### Example
```
Must support backwards compatibility
Should export Code after ID column
Must not break existing import functionality

Add Code value export for all parent references with configurable modes
```

---

## Enhancement Tips

### Basic (3★)
```
Add Code support to exports
```

### Better (4★)
```
Add Code support to exports.

This will allow cross-environment data migration.

Add parameter to control ID/Code/Both export modes.
```

### Best (5★)
```
We export the EntityID from parent relations.

Please adjust to also include the Code of these entries.

The idea is that we can with parameters tell to pass parent relations by ID(Nr) or Code, or both (default)

Place the code export after the ID column.

Examples:
- Country EntityID=1 Code="US" → Export both
- Market EntityID=5 Code="DA" CountryEntityID=1 CountryCode="US"

Constraints:
- Code column appears immediately after ID column
- Default mode exports both (backwards compatible)
- Must work for all parent reference properties
```

---

## What Makes Features Clear

### ✅ Include:
- **Why** you need it (use case)
- **What** it should do (functionality)
- **How** it should behave (examples)
- **Where** it fits (context)
- **Constraints** to respect

### ❌ Avoid:
- Too vague ("make it better")
- No use case explanation
- Missing examples for complex features
- Assuming AI knows domain details
- No constraints mentioned

---

## For Complex Features

Break into phases:

```
Phase 1: Add Code export (basics)
- Export Code value for parent references
- Place after ID column

Phase 2: Make it configurable
- Add export mode parameter
- Support ID/Code/Both modes

Phase 3: Import support
- Update import to accept Code values
- Add Code-based link regeneration
```

---

## Expected AI Response

AI will typically:
1. **Clarify** understanding with questions
2. **Propose** implementation approach
3. **Ask** about edge cases
4. **Suggest** alternatives if applicable
5. **Implement** after confirmation

---

## Follow-up Patterns

### After Feature Request

**If AI asks clarifying questions:**
```
[Answer the questions]
```

**If AI proposes approach:**
```
Looks good, please proceed
```
or
```
Good, but adjust [ASPECT] to [ALTERNATIVE]
```

**After implementation:**
```
please test this feature
```

---

## Domain-Specific Examples

### Data Export/Import
```
Add support for exporting [ENTITY] relationships using [IDENTIFIER_TYPE]
```

### UI Enhancement
```
Add [COMPONENT] to [SCREEN] that allows users to [ACTION]
```

### API Addition
```
Create endpoint that [FUNCTIONALITY] and returns [RESPONSE_FORMAT]
```

### Configuration
```
Add configuration option to control [BEHAVIOR] with values [OPTIONS]
```

---

## Tips

- **Start broad** - Describe the need first
- **Add details** - Then explain specifics
- **Give examples** - Show what you mean
- **State constraints** - Mention limitations upfront
- **Reference similar** - "Like X but for Y"

---

## Anti-Pattern (Don't Do This)

❌ **Too vague**:
```
Make the export better
```

❌ **No context**:
```
Add Code column
```

❌ **Assumes knowledge**:
```
Do the Code thing we discussed
```

✅ **Clear and complete**:
```
We export EntityID from parent relations.

Please add Code values alongside EntityID.

Parameters should control export mode: ID only, Code only, or Both (default).

This enables cross-environment data migration.
```

---

## Expected AI Response

When you request a feature, the AI should:

1. **Acknowledge Request**
   ```
   Feature request understood: [Brief summary]
   ```

2. **Ask Clarifying Questions** (if needed)
   ```
   Questions:
   - Should this apply to X or also Y?
   - What should happen in edge case Z?
   - Any performance constraints?
   ```

3. **Propose Approach**
   ```
   Proposed Implementation:
   - Phase 1: [Basic functionality]
   - Phase 2: [Enhancements]
   - Affected files: [List]
   ```

4. **Confirm Before Implementing**
   ```
   Does this approach meet your needs?
   Please confirm before I proceed.
   ```

5. **Implement** (after approval)
   - Build feature systematically
   - Test as you go
   - Document changes

---

## Quality Criteria

For effective feature requests, include:

- [ ] Clear description of what's needed
- [ ] Rationale (why/use case)
- [ ] Concrete examples showing desired behavior
- [ ] Constraints or requirements
- [ ] Edge cases or special scenarios (if known)

For AI implementation, verify:

- [ ] AI understood the request correctly
- [ ] AI asked questions for ambiguities
- [ ] Proposed approach is sound
- [ ] Implementation matches request
- [ ] Feature tested before claiming complete

---

## Related Prompts

- `code-quality/iterative-refinement.md` - After implementation, for adjustments
- `ticket/validate-before-action.md` - For complex features needing validation
- `code-quality/architectural-question.md` - If unclear about design approach

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)  
**Pattern ID**: #8 Feature Request Pattern  
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0

