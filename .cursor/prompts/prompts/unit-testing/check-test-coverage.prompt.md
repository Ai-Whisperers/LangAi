---
name: check-test-coverage
description: "Analyze unit test coverage for a component and identify gaps with prioritized action plan"
category: unit-testing
tags: unit-testing, test-coverage, gap-analysis, quality-assurance
argument-hint: "Component or folder path to analyze"
---

# Check Unit Test Coverage

Please analyze unit test coverage for:

**Target**: `[REPLACE WITH COMPONENT/FOLDER PATH]`

## Coverage Analysis

1. **Identify All Testable Units**:
   - List all public classes and methods
   - List all public properties with logic
   - Identify complex internal methods that should be tested
   - Note any static methods or extension methods

2. **Map Existing Tests**:
   - Find all test files for this component
   - Map tests to the methods they cover
   - Identify test gaps (untested methods)
   - Check for edge cases and error paths

3. **Quality Assessment**:
   - Are tests testing behavior or just implementation?
   - Do tests have meaningful assertions?
   - Are tests independent and isolated?
   - Are test names descriptive?

4. **Coverage Gaps**:
   - Methods with no tests
   - Methods with insufficient test cases
   - Missing edge case tests
   - Missing error/exception tests
   - Missing integration points tests

5. **Test Coverage Report**:
   - % of methods with tests
   - % of public API covered
   - Critical gaps (high-risk uncovered code)
   - Recommended test additions

## Priority Matrix

Categorize gaps by:
- **Critical**: Public API, business logic, data validation
- **High**: Error handling, edge cases, complex logic
- **Medium**: Helper methods, utilities
- **Low**: Simple getters/setters, trivial logic

## Deliverable

1. Coverage summary with statistics
2. Detailed gap analysis
3. Prioritized list of tests to add
4. Suggested test cases for top 5-10 gaps

Apply standards from `.cursor/rules/unit-testing/unit-test-coverage-rule.mdc`.
