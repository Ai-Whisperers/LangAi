---
name: review-code-quality
description: "Comprehensive code quality review across multiple dimensions"
category: code-quality
tags: code-quality, review, analysis, standards, assessment
argument-hint: "File/folder path to review"
---

# Review Code Quality in [Target]

Please perform a comprehensive code quality review of the target code.

**Required Context**:
- `[TARGET_PATH]`: File or folder path to review (e.g., `src/Domain/Entities/`)
- `[CODE_CONTEXT]`: (Optional) Paste specific code snippet here if not using a path.

**Optional Parameters**:
- `[FOCUS_AREA]`: Specific concern (e.g., "Performance", "Security")

## Reasoning Process
1. **Analyze Context**: Scan the provided code/path to understand its purpose and architecture.
2. **Select Rules**: Identify which specific `.cursor/rules` apply (Clean Code, DRY, etc.).
3. **Step-by-Step Scan**:
   - Check Naming & Style.
   - Check Logic & Complexity.
   - Check Security & Performance.
4. **Prioritize**: Group issues by severity (Critical vs. Nitpick).
5. **Formulate Recommendations**: Write actionable fixes, not just complaints.

## Process

1. **Clean Code Principles**:
   - Are names meaningful and descriptive?
   - Are functions small and focused (Single Responsibility)?
   - Is code DRY (Don't Repeat Yourself)?
   - Is complexity reasonable (cyclomatic complexity)?
   - Are magic numbers/strings avoided?

2. **Code Structure**:
   - Is the code well-organized and logical?
   - Are dependencies properly managed?
   - Is coupling loose and cohesion high?
   - Are abstractions appropriate?
   - Is the code testable?

3. **Error Handling**:
   - Are exceptions used appropriately?
   - Is error handling comprehensive?
   - Are resource cleanups proper (using statements)?
   - Are edge cases handled?

4. **Performance Considerations**:
   - Are there obvious performance issues?
   - Is resource usage efficient?
   - Are collections used appropriately?
   - Are there N+1 query problems?

5. **Security**:
   - Are inputs validated?
   - Is SQL injection prevented?
   - Are secrets/credentials hardcoded?
   - Is sensitive data properly handled?

6. **Comments & Documentation**:
   - Is XML documentation complete and accurate?
   - Are complex algorithms explained?
   - Are "why" comments present where needed?
   - Are there obsolete or misleading comments?

7. **Standards Compliance**:
   - Does code follow C# conventions?
   - Are naming conventions consistent?
   - Is formatting consistent?
   - Are code smells present?

## Examples (Few-Shot)

**Input**:
```csharp
public void do_thing(string x) {
    if(x!=null) {
       // 500 lines of code
    }
}
```

**Reasoning**:
- Naming `do_thing` violates PascalCase.
- Parameter `x` is non-descriptive.
- Method length > 50 lines (Clean Code violation).

**Output**:
> **Issue**: Method `do_thing` violates naming conventions and Single Responsibility Principle.
> **Severity**: High
> **Fix**: Rename to `ProcessTransaction()` and extract inner logic into `ValidateInput()` and `ExecuteLogic()`.

## Expected Output

**Deliverables**:
1. Overall quality assessment summary
2. Issues categorized by severity (Critical/High/Medium/Low)
3. Specific examples with line numbers
4. Refactoring recommendations
5. Prioritized action items

**Format**: Markdown Report

## Quality Criteria

- [ ] All "Critical" issues have a proposed fix.
- [ ] Line numbers are cited for every issue.
- [ ] Tone is constructive, not harsh.
- [ ] References specific rules (e.g., "Violates DRY principle").

---

**Applies Rules**:
- `.cursor/rules/clean-code.mdc`
- `.cursor/rules/code-quality-and-best-practices.mdc`
- `.cursor/rules/dry-principle.mdc`
