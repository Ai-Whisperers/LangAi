---
name: Create Integration Points Spec
description: Create Integration Points specification detailing external interfaces for C++ to C# migration
category: technical
tags: [migration, integration, external-systems, technical-docs]
argument-hint: "[domain-name]"
---

# Create Integration Points Spec for [Domain]

Create Integration Points specification detailing external interfaces for C++ to C# migration.

**Required Context**:
- `[DOMAIN_NAME]`: The functional domain.
- `[EXTERNAL_SYSTEMS]`: List of connected systems.
- `[INTERFACE_TYPES]`: API, File, DB Link, Script Functions.

## Reasoning Process
1.  **Identify Boundaries**: What crosses the domain boundary?
2.  **Catalog Interfaces**: List APIs, File transfers, DB Links.
3.  **Analyze Script Functions**: Identify `DBCREATE`, `DBGET`, `DBSET` usage.
4.  **Define Contracts**: Data formats (JSON, XML, CSV), protocols.
5.  **Assess Migration Impact**: How must these change or be preserved?

## Process

1.  **File Header**:
    - Location: `docs/technical/[domain]/[domain]-integration-points.md`

2.  **External System Catalog**:
    - System Name, Purpose, Direction (In/Out).

3.  **Interface Specifications**:
    - **APIs**: Endpoints, Payloads.
    - **Files**: Naming conventions, formats, locations.
    - **Script Functions**: Catalog of automation hooks.

4.  **Data Flow**:
    - Sequence diagrams (Mermaid) for key flows.

5.  **Migration Strategy**:
    - Compatibility requirements (must maintain legacy interface?).
    - Modernization candidates (Script -> REST API).

## Examples (Few-Shot)

**Input**:
System reads `orders.csv` from FTP and calls `DBCREATE_ORDER`.

**Output**:
> **System**: Logistics Provider (FTP).
> **Flow**: Inbound Order Creation.
> **Mechanism**: File Polling -> Script Function.
> **Legacy Function**: `DBCREATE_ORDER(cust_id, items)`.
> **Target State**: REST API `POST /api/orders`.

## Expected Output

**Deliverables**:
1.  Complete Integration Points markdown file.

**Format**: Markdown file following `docs/technical` standards.

## Quality Criteria

- [ ] Captures all external I/O.
- [ ] Documents legacy script functions.
- [ ] Defines data formats exactly (no assumptions).
- [ ] Includes migration/compatibility strategy.

---

**Applies Rules**:
- `.cursor/rules/technical-specifications/integration-points-rule.mdc`

