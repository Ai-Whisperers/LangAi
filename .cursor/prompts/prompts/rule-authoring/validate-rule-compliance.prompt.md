---
name: validate-rule-compliance
description: "Please validate rule file against authoring framework standards and requirements"
category: rule-authoring
tags: rules, validation, quality-check, compliance
argument-hint: "[rule-file-path]"
---

# Validate Rule Compliance

Please validate the following rule file against the rule authoring framework:

**Rule File Path**: `eneve.domain/.cursor/rules/podcast/` (entire folder)

## Validation Checklist

1. **File Structure**:
   - Front-matter present and well-formed?
   - Required YAML fields present (rule_id, title, version)?
   - Sections in correct order?
   - Markdown formatting correct?

2. **Front Matter Validation**:
   ```yaml
   Required fields:
   - rule_id: [category]-[name]-rule format?
   - title: Clear and descriptive?
   - version: Semantic versioning (X.Y.Z)?
   - created: Valid date (YYYY-MM-DD)?
   - status: active/draft/deprecated?
   
   Optional but recommended:
   - tags: Relevant keywords?
   - governs: File patterns (if file-mask rule)?
   - applies_to: File types?
   ```

3. **Rule ID Validation**:
   - Follows naming convention?
   - Pattern: `[category]-[descriptive-name]-rule`
   - Lowercase with hyphens?
   - Ends with `-rule`?

4. **Invocation Strategy**:
   - Clear strategy defined (file-mask/agentic/always)?
   - If file-mask: `governs` field present with glob patterns?
   - If agentic: Description clearly states when to use?
   - If always-apply: Documented in always-applied rules?

5. **Content Structure**:
   - Purpose section clearly states what rule does?
   - Scope section defines boundaries?
   - When to Apply section provides clear conditions?
   - Rule Definition section has concrete rules?

6. **Contracts and Scope**:
   - Input expectations documented?
   - Output specifications documented?
   - Preconditions stated?
   - Postconditions stated?
   - Boundaries clear (what's in/out of scope)?

7. **Quality Checklist**:
   - Validation checklist present?
   - Checklist items specific and verifiable?
   - Checklist comprehensive?
   - Items have clear pass/fail criteria?

8. **Examples**:
   - Good examples provided?
   - Bad examples (anti-patterns) provided?
   - Examples are realistic and relevant?
   - Examples clearly show compliance vs violation?

9. **Cross-References**:
   - References to related rules?
   - Links to templars (if applicable)?
   - Links to exemplars (if applicable)?
   - Links are valid and working?

10. **Templar/Exemplar Alignment**:
    - If rule references templars, do they exist?
    - If rule references exemplars, do they exist?
    - Are references using stable IDs?

## Validation Severity

Categorize issues:
- **Critical**: Breaks rule framework, must fix
- **High**: Missing key requirements, should fix
- **Medium**: Reduces quality, nice to fix
- **Low**: Suggestions for improvement

## Deliverable

Provide:
1. Overall compliance status (Pass/Fail/Pass with Issues)
2. Detailed validation report by checklist item
3. List of issues found, categorized by severity
4. Specific recommendations for fixes
5. Suggested improvements for quality
6. Updated rule content (if fixes needed)

Follow validation standards from:
- `.cursor/rules/rule-authoring/rule-validation-and-checklists.mdc`
- `.cursor/rules/rule-authoring/rule-file-structure.mdc`
- `.cursor/rules/rule-authoring/rule-contracts-and-scope.mdc`
- `.cursor/rules/rule-authoring/rule-invocation-strategies.mdc`
- `.cursor/rules/rule-authoring/rule-naming-conventions.mdc`

