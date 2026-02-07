---
name: refactor-for-clean-code
description: "Refactor code to improve quality and maintainability"
category: code-quality
tags: code-quality, refactoring, clean-code, maintainability, SOLID
argument-hint: "File path to refactor"
---

# Refactor for Clean Code

Please refactor the following code to improve quality and maintainability:

**Target**: `[REPLACE WITH FILE PATH]`

## Refactoring Goals

1. **Extract Methods**:
   - Break down long methods into smaller, focused methods
   - Each method should do one thing well
   - Extract complex conditions into well-named methods
   - Target: Methods under 20 lines

2. **Improve Names**:
   - Replace unclear variable names
   - Use intention-revealing names
   - Avoid abbreviations and single letters (except loop counters)
   - Make boolean variables read like questions

3. **Reduce Complexity**:
   - Simplify complex conditionals
   - Reduce nesting levels (use early returns)
   - Replace nested loops with LINQ where appropriate
   - Simplify boolean expressions

4. **Remove Duplication**:
   - Extract common code into methods
   - Use inheritance or composition for repeated patterns
   - Consider creating utility methods for repeated logic

5. **Improve Testability**:
   - Extract dependencies to interfaces
   - Reduce static method usage
   - Make implicit dependencies explicit
   - Avoid tight coupling

6. **Apply SOLID Principles**:
   - Single Responsibility: Each class/method does one thing
   - Open/Closed: Open for extension, closed for modification
   - Liskov Substitution: Subtypes must be substitutable
   - Interface Segregation: Small, focused interfaces
   - Dependency Inversion: Depend on abstractions

## Refactoring Approach

1. Show current issues and their impact
2. Propose refactoring strategy
3. Make changes incrementally (one refactoring at a time)
4. Explain each refactoring and its benefits
5. Ensure behavior is preserved

## Constraints

- Preserve existing behavior (no functional changes)
- Maintain backward compatibility (unless explicitly allowed)
- Keep existing tests passing
- Add tests for new extracted methods if needed

## Deliverable

For each refactoring:
1. Show before/after comparison
2. Explain the improvement
3. Highlight the clean code principle applied
4. Note any follow-up refactorings needed

Process file-by-file, showing complete refactored files.

Apply principles from:
- `.cursor/rules/clean-code.mdc`
- `.cursor/rules/dry-principle.mdc`
- `.cursor/rules/function-length-and-responsibility.mdc`
