---
name: Create Business Rules for Domain
description: Create a Business Rules specification document for C++ to C# migration
category: technical
tags: [migration, business-rules, specification, technical-docs]
argument-hint: "[domain-name]"
---

# Create Business Rules for [Domain]

Create a Business Rules specification document for C++ to C# migration.

**Required Context**:
- `[DOMAIN_NAME]`: The functional domain (e.g., Billing, Rating).
- `[SOURCE_FILES]`: C++ source files being analyzed.
- `[KEY_ALGORITHMS]`: List of identified algorithms or logic blocks.

## Reasoning Process
1.  **Analyze Source**: Extract logic from C++ source (focus on WHAT, not HOW).
2.  **Identify Categories**: Group into Algorithms, Validation, Decision Trees, Workflows.
3.  **Define Rules**: Write descriptive rules using business terminology.
4.  **Preserve Precision**: Note mathematical formulas and precision requirements.
5.  **Map to Migration**: Define strict requirements for the C# implementation.

## Process

1.  **File Header**:
    - Location: `docs/technical/[domain]/[domain]-business-rules.md`
    - Provenance info.

2.  **Overview**:
    - Context and scope of these rules.

3.  **Algorithms**:
    - Step-by-step logic in English.
    - Inputs/Outputs.
    - Mathematical formulas (if applicable).
    - Example scenarios.

4.  **Validation Rules**:
    - Trigger conditions.
    - Valid/Invalid states.
    - Error messages/responses.

5.  **Decision Logic**:
    - IF/THEN/ELSE trees.
    - Matrixes or Tables for complex decisions.

6.  **Migration Requirements**:
    - "Must produce identical output to C++ for input X".
    - Precision/Rounding rules.

## Examples (Few-Shot)

**Input**:
C++: `double calc_tax(amt) { if (amt > 100) return amt * 0.2; return 0; }`

**Output**:
> **Rule**: TAX-01 High Value Tax
> **Logic**: IF output amount > 100.00 THEN apply 20% tax rate. ELSE tax is 0.
> **Precision**: 2 decimal places, round half up.
> **Source**: `tax_calc.cpp:45`

## Expected Output

**Deliverables**:
1.  Complete Business Rules markdown file.

**Format**: Markdown file following `docs/technical` standards.

## Quality Criteria

- [ ] Focus on WHAT (Business Logic), not HOW (C++ implementation).
- [ ] No C++ code snippets in the final doc (use pseudocode/text).
- [ ] Includes source file references.
- [ ] Defines mathematical precision clearly.

---

**Applies Rules**:
- `.cursor/rules/technical-specifications/business-rules-rule.mdc`

