---
name: check-folder-documentation
description: "Analyze XML documentation coverage for a folder and generate detailed report"
category: documentation
tags: documentation, xml, coverage-analysis, csharp, quality-check
argument-hint: "Folder path to analyze"
---

# Check Folder Documentation Coverage

Please perform a comprehensive XML documentation check on the following folder:

**Folder Path**: `[REPLACE WITH YOUR FOLDER PATH]`

## Analysis Required

1. **Completeness Check**:
   - List all classes, interfaces, methods, and properties
   - Identify which items are missing XML documentation
   - Categorize by severity (public API vs internal)

2. **Quality Assessment**:
   - Check for generic/placeholder documentation (e.g., "Gets or sets the value")
   - Identify documentation that doesn't match the actual implementation
   - Flag documentation with TODO or FIXME comments

3. **Standards Compliance**:
   - Verify all `<summary>` tags are present and meaningful
   - Check for required `<param>`, `<returns>`, `<exception>` tags
   - Validate that XML is well-formed

4. **Generate Report**:
   - Summary statistics (% documented, items missing docs)
   - Prioritized list of items needing documentation
   - Specific examples of quality issues

5. **Action Plan**:
   - Recommend which files to document first
   - Suggest any patterns or templates for common cases

## Context

Apply the documentation standards from `.cursor/rules/documentation/documentation-standards-rule.mdc`.

Do not make any changes yet - provide the analysis report first.
