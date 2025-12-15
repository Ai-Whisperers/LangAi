---
name: Analyze C++ Component for Migration
description: Analyze C++ component for migration to C# using systematic data collection
category: migration
tags: [migration, analysis, c++, data-collection]
argument-hint: "[component-name]"
---

# Analyze C++ Component for Migration

Please analyze the following C++ component for migration to C#:

**Component Name**: `[REPLACE WITH COMPONENT/MODULE NAME]`
**Source Path**: `[REPLACE WITH C++ SOURCE PATH]`
**Analysis Scope**: `[REPLACE WITH: Full Analysis/Quick Assessment/Specific Aspect]`

## Phase 1: Data Collection

1. **Source Code Analysis**:
   - Identify all classes and their purposes
   - Map inheritance hierarchies
   - Document public APIs
   - Find configuration files
   - List dependencies (internal and external)

2. **Domain Model Extraction**:
   - Identify domain entities
   - Find enumerations with exact values
   - Map relationships between entities
   - Document data structures

3. **Business Logic Identification**:
   - Find calculation algorithms
   - Identify validation rules
   - Document state machines
   - Map workflow processes
   - Extract decision logic

4. **Database Schema**:
   - Identify database tables used
   - Document table relationships
   - Find stored procedures
   - Map data access patterns
   - Note any ORMs or data layers

5. **Integration Points**:
   - External systems called
   - APIs exposed
   - File I/O operations
   - Network communications
   - Message queues or events

6. **Complexity Assessment**:
   - Lines of code
   - Cyclomatic complexity
   - Number of dependencies
   - Business rule complexity
   - Technical debt indicators

## Analysis Output

Provide:

1. **Component Overview**:
   - Purpose and responsibilities
   - Business value
   - Current architecture
   - Key technologies used

2. **Domain Model**:
   - List of domain entities
   - List of enumerations (with values!)
   - Entity relationships diagram (Mermaid)
   - Data flow diagrams

3. **Business Logic Catalog**:
   - List of algorithms with complexity
   - List of validation rules
   - State machines or workflows
   - Decision tables

4. **Technical Architecture**:
   - Component dependencies
   - Integration points
   - Database schema
   - External interfaces

5. **Migration Complexity**:
   - Estimated effort (T-shirt size: S/M/L/XL)
   - Key challenges
   - Risks and unknowns
   - Prerequisites

6. **Recommended Next Steps**:
   - Specification priorities
   - Areas needing deeper analysis
   - Questions for domain experts
   - POC or spike recommendations

## Migration Quality Gates

Ensure:
- 100% of enumerations captured with exact values
- All public APIs documented
- Business logic extracted, not assumed
- Integration points fully mapped
- No invention or assumptions

## Deliverable

1. Comprehensive analysis document
2. Visual diagrams (architecture, ER, flow)
3. Migration estimate and complexity
4. Specification outline (what specs to write)
5. Questions/gaps requiring clarification

Save document to: `docs/technical/migration-analysis/[component-name]-analysis.md`

Follow standards from:
- `.cursor/rules/migration/phase-1-data-collection.mdc`
- `.cursor/rules/migration/migration-overview.mdc`

