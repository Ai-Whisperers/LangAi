---
name: document-enumeration
description: "Create comprehensive enumeration specification with exact numeric values from C++ source for migration compatibility"
category: technical-specifications
tags: enumeration, technical-specs, migration, cpp-to-csharp, data-types
argument-hint: "Enum name and source location"
---

# Document Enumeration

Please create comprehensive technical specification for this enumeration:

**Enum Name**: `[REPLACE WITH ENUM NAME]`
**Source Location**: `[REPLACE WITH C++ SOURCE FILE PATH]`
**Domain**: `[REPLACE WITH DOMAIN AREA]`

## Documentation Requirements

1. **Overview**:
   - What this enumeration represents
   - Where and how it's used
   - Business purpose and context

2. **Complete Value List**:

   For each enum value, document:
   ```markdown
   ### [ValueName] = [NumericValue]

   - **Business Meaning**: [What this value represents]
   - **When Used**: [Conditions for this value]
   - **Usage Frequency**: [Common/Rare/Deprecated]
   - **Examples**: [Real-world scenarios]
   ```

3. **Critical Requirements**:
   - **EXACT numeric values** from C++ source (non-negotiable)
   - **Complete list** - no values omitted
   - **Source verification** - line-by-line reference
   - **Deprecation status** - note any unused values

4. **Usage Patterns**:
   - Where is this enum used in the system?
   - What classes/methods reference it?
   - How is it persisted (integer value in DB)?
   - Any conversions or mappings?

5. **Validation Logic**:
   - Valid range of values
   - Any validation rules
   - Invalid or reserved values
   - Default values

6. **State Transitions** (if applicable):
   - Can values change over time?
   - What transitions are valid?
   - What triggers transitions?

7. **Migration Preservation**:
   - C# enum must use identical numeric values
   - Database compatibility requirements
   - Legacy data considerations

## Source Analysis

Analyze:

1. C++ enum definition (exact line numbers)
2. All usages in codebase
3. Database storage (verify numeric values)
4. Any related lookup tables
5. String representations or display names

## Critical Rule

**NUMERIC VALUES MUST MATCH C++ SOURCE EXACTLY**

- Migration requires identical values
- Database compatibility depends on this
- Any mismatch breaks data integrity

## Deliverable

Provide:

1. Complete enumeration specification document
2. Exact source references (file:line)
3. Complete value list with numeric values
4. Usage analysis
5. Migration checklist
6. C# enum code template (with correct values)

Save document to: `docs/technical/domains/[domain-name]/enumerations/[enum-name].md`

Follow standards from:

- `.cursor/rules/technical-specifications/enumeration-rule.mdc`
- `.cursor/rules/technical-specifications/specification-anti-duplication-rule.mdc`
