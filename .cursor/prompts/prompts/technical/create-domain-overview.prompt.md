---
name: Create Domain Overview
description: Create Domain Overview navigation hub for C++ to C# migration documentation
category: technical
tags: [migration, domain-overview, navigation, technical-docs]
argument-hint: "[domain-name]"
---

# Create Domain Overview for [Domain]

Create the Domain Overview navigation hub for C++ to C# migration documentation.

**Required Context**:
- `[DOMAIN_NAME]`: The functional domain.
- `[SUB_DOMAINS]`: Key functional areas.
- `[KEY_ENTITIES]`: Primary business objects.

## Reasoning Process
1.  **Synthesize Context**: Combine business purpose with technical scope.
2.  **Map Hierarchy**: Define the entity/component hierarchy (3-tier).
3.  **Structure Navigation**: Create paths to all child documents (DB, Rules, Objects).
4.  **Define Stakeholder Paths**: Guide Developers, BAs, and Architects.
5.  **Visualize**: Create High-level Context Diagram (Mermaid).

## Process

1.  **File Header**:
    - Location: `docs/technical/[domain]/[domain]-domain-overview.md`

2.  **Purpose & Scope**:
    - Executive summary of the domain.

3.  **Domain Architecture**:
    - High-level block diagram.
    - Entity Hierarchy list.

4.  **Navigation Hub**:
    - Links to `database/` (Schema, Constraints).
    - Links to `domain/` (Objects, Enums).
    - Links to `business-rules.md`, `integration-points.md`.

5.  **Processing Model**:
    - Description of main workflows.

6.  **Reading Paths**:
    - "For Developers: Start here..."
    - "For Analysts: Start here..."

## Examples (Few-Shot)

**Input**:
Domain: Invoicing. Key Entities: Invoice, LineItem, Tax.

**Output**:
> **Domain**: Invoicing
> **Purpose**: Generate and manage customer billing.
> **Navigation**:
> - [Database Schema](database/invoicing-database-schema.md)
> - [Business Rules](invoicing-business-rules.md)
> **Key Entities**: Invoice (Root) -> LineItem (Child).

## Expected Output

**Deliverables**:
1.  Complete Domain Overview markdown file.

**Format**: Markdown file following `docs/technical` standards.

## Quality Criteria

- [ ] Acts as the root/index for the domain folder.
- [ ] Links to ALL other specification files in the domain.
- [ ] Includes high-level Mermaid diagram.
- [ ] OPSEC clean.

---

**Applies Rules**:
- `.cursor/rules/technical-specifications/domain-overview-rule.mdc`
- `.cursor/rules/technical-specifications/hybrid-documentation-architecture-rule.mdc`

