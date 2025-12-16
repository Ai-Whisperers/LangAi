---
name: document-domain-object
description: "Create comprehensive technical specification for a domain object with field details, relationships, and migration considerations"
category: technical-specifications
tags: domain-object, technical-specs, entity-documentation, migration, cpp-to-csharp
argument-hint: "Object name and source location"
---

# Document Domain Object

Please create comprehensive technical specification for this domain object:

**Object Name**: `[REPLACE WITH CLASS/ENTITY NAME]`
**Source Location**: `[REPLACE WITH C++ SOURCE FILE PATH OR DATABASE TABLE]`
**Domain**: `[REPLACE WITH DOMAIN AREA, e.g., Billing, Forecasting]`

## Documentation Requirements

1. **Overview Section**:
   - Clear description of what this object represents
   - Business purpose and context
   - Where and how it's used in the system
   - Relationships to other domain objects

2. **Field/Property Specifications**:

   For each field, document:
   ```markdown
   ### [FieldName]

   - **Type**: [Data type with precision]
   - **Purpose**: [What this field stores]
   - **Business Meaning**: [What it represents in business terms]
   - **Constraints**: [Required, nullable, range, format]
   - **Usage**: [How/where it's used]
   - **Source**: [C++ file:line or DB table.column]
   ```

3. **Relationships**:
   - Parent objects (foreign keys)
   - Child collections
   - Associated objects
   - Relationship cardinality (1:1, 1:N, N:M)

4. **Business Rules**:
   - Validation rules
   - Calculation logic
   - State transitions
   - Invariants that must hold

5. **Source References**:
   - C++ class definition location
   - Database table/view definition
   - Related configuration files
   - Any enumerations used

6. **Lifecycle**:
   - How objects are created
   - How they are modified
   - When they are deleted
   - Persistence mechanism

7. **Migration Considerations**:
   - Any complexity in migration
   - Data transformations needed
   - Potential issues to address
   - C# design recommendations

## Source Analysis

Please analyze:

1. C++ header/implementation files
2. Database schema (if persisted)
3. Usage in codebase
4. Related enumerations or types

## Quality Standards

- 100% accuracy to source system
- Complete field documentation
- Clear business context
- Explicit source references
- Real-world usage examples

## Deliverable

Provide:

1. Complete domain object specification document
2. Relationship diagram (Mermaid) if complex
3. List of related objects to document
4. Migration complexity assessment
5. Any questions or clarifications needed

Save document to: `docs/technical/domains/[domain-name]/[object-name].md`

Follow standards from:

- `.cursor/rules/technical-specifications/domain-object-rule.mdc`
- `.cursor/rules/technical-specifications/specification-anti-duplication-rule.mdc`
- `.cursor/rules/technical-specifications/documentation-architecture-rule.mdc`
