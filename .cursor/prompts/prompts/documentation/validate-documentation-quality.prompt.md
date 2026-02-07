---
name: validate-documentation-quality
description: "Deep quality analysis of XML documentation with detailed improvement recommendations"
category: documentation
tags: documentation, xml, quality-analysis, validation, csharp
argument-hint: "File or folder path to validate"
---

# Validate Documentation Quality

Please perform a deep quality analysis of XML documentation in:

**Target**: `[REPLACE WITH FILE/FOLDER PATH]`

## Quality Checks

1. **Generic Documentation Detection**:
   - Flag summaries like "Gets or sets the X"
   - Find placeholders like "TODO", "FIXME", "Description"
   - Identify copy-pasted documentation across similar methods

2. **Accuracy Verification**:
   - Check parameter names match method signatures
   - Verify return type documentation matches actual return type
   - Ensure exception documentation matches thrown exceptions
   - Validate that remarks reflect actual behavior

3. **Completeness Audit**:
   - Missing `<param>` tags
   - Missing `<returns>` tags for non-void methods
   - Missing `<exception>` tags for thrown exceptions
   - Public APIs without `<summary>` tags

4. **Style Consistency**:
   - Inconsistent summary verb usage
   - Inconsistent formatting or structure
   - Missing cross-references where appropriate
   - Lack of examples for complex APIs

5. **Business Context**:
   - Does documentation explain business purpose?
   - Are domain concepts clearly explained?
   - Are constraints and validations documented?

## Deliverable

Provide:

1. Quality score summary (by category)
2. Specific examples of issues found
3. Prioritized list of improvements
4. Suggested documentation improvements (show before/after)

Apply standards from `.cursor/rules/documentation/documentation-standards-rule.mdc`.
