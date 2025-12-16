---
name: generate-missing-docs
description: "Add comprehensive XML documentation to C# files following quality standards"
category: documentation
tags: documentation, xml, code-generation, csharp, api-documentation
argument-hint: "File path(s) to document"
---

# Generate Missing XML Documentation

Please add comprehensive XML documentation to the following file(s):

**File Path(s)**: `[REPLACE WITH FILE PATH(S)]`

## Requirements

1. **Add XML Comments** for all:
   - Public classes, interfaces, structs, enums
   - Public methods and constructors
   - Public properties and fields
   - Protected members (if part of inheritance API)

2. **Quality Standards**:
   - Write clear, meaningful summaries (not generic placeholders)
   - Include `<param>` descriptions for all parameters
   - Add `<returns>` descriptions for non-void methods
   - Document `<exception>` tags for thrown exceptions
   - Add `<remarks>` for complex behavior or usage notes
   - Include `<example>` for complex APIs or non-obvious usage

3. **Style Guidelines**:
   - Start summaries with a verb in third person (e.g., "Represents", "Gets", "Calculates")
   - Be concise but complete
   - Explain the "why" and "what", not just the "how"
   - Reference related types using `<see cref=""/>` tags

4. **Validation**:
   - Ensure all XML is well-formed
   - Verify documentation matches actual implementation
   - Check that parameter names match method signatures

## Context

Follow the standards defined in `.cursor/rules/documentation/documentation-standards-rule.mdc`.

Process files one at a time, showing each complete file with documentation added.
