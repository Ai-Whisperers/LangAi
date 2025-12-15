---
name: Create Entity Relationship Spec
description: Create Entity Relationship documentation (Database Schema) for C++ to C# migration
category: technical
tags: [migration, database, entity-relationship, technical-docs]
argument-hint: "[domain-name]"
---

# Create Entity Relationship Spec for [Domain]

Create Entity Relationship documentation (Database Schema) for C++ to C# migration.

**Required Context**:
- `[DOMAIN_NAME]`: The functional domain.
- `[DB_SCHEMA_FILES]`: Source database DDL or schema definitions.
- `[TABLE_LIST]`: List of relevant tables.

## Reasoning Process
1.  **Analyze Database**: Review source schema (Oracle/MSSQL).
2.  **Identify Entities**: Map tables to logical entities.
3.  **Map Relationships**: Identify FKs and logical connections.
4.  **Define Constraints**: constraints, indexes, defaults.
5.  **Visualize**: Generate Mermaid ERD code.

## Process

1.  **File Set Creation** (3-File Pattern):
    - `[domain]-database-schema.md` (Tables)
    - `[domain]-database-constraints.md` (Relationships/Keys)
    - `[domain]-database-analysis.md` (Context)

2.  **Schema File**:
    - Markdown tables or code blocks for table definitions.
    - Column types, nullability.

3.  **Constraints File**:
    - Primary Keys, Foreign Keys.
    - Unique constraints.
    - Check constraints.

4.  **Analysis File**:
    - Business meaning of the data structure.
    - Migration complexity assessment.
    - Oracle vs MSSQL differences.

5.  **Mermaid ERD**:
    - Visual diagram of the schema.

## Examples (Few-Shot)

**Input**:
Table `CUST` (ID, NAME) and `ADDR` (ID, CUST_ID, CITY).

**Output**:
> **ERD**:
> ```mermaid
> erDiagram
>    CUSTOMER ||--|{ ADDRESS : has
> ```
> **Relationship**: Customer (1) has many Addresses (N).
> **Constraint**: `ADDR.CUST_ID` FK to `CUST.ID`.

## Expected Output

**Deliverables**:
1.  Content for Schema file.
2.  Content for Constraints file.
3.  Content for Analysis file.
4.  Mermaid ERD diagram.

**Format**: Markdown files following `docs/technical` standards.

## Quality Criteria

- [ ] 100% accurate to source schema.
- [ ] Includes Mermaid ERD.
- [ ] Splits content into Schema/Constraints/Analysis files.
- [ ] No sensitive data (passwords, production IPs).

---

**Applies Rules**:
- `.cursor/rules/technical-specifications/entity-relationship-rule.mdc`
- `.cursor/rules/technical-specifications/hybrid-documentation-architecture-rule.mdc`

