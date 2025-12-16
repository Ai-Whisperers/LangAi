---
name: validate-test-quality
description: "Analyze unit test quality against best practices and recommend improvements"
category: unit-testing
tags: unit-testing, quality-analysis, test-validation, best-practices
argument-hint: "Test file path(s) to validate"
---

# Validate Unit Test Quality

Please analyze the quality of unit tests in:

**Test File(s)**: `[REPLACE WITH TEST FILE PATH(S)]`

## Quality Assessment

1. **Test Structure**:
   - Do tests follow AAA (Arrange, Act, Assert) pattern?
   - Are tests focused on single behaviors?
   - Is test setup clear and minimal?
   - Are assertions meaningful and specific?

2. **Test Independence**:
   - Can tests run in any order?
   - Are tests isolated from each other?
   - Do tests avoid shared mutable state?
   - Is each test self-contained?

3. **Test Coverage**:
   - Do tests cover happy paths?
   - Are edge cases tested?
   - Are error conditions tested?
   - Are all code paths exercised?

4. **Test Naming**:
   - Are test names descriptive and clear?
   - Do names indicate what is being tested?
   - Do names indicate expected outcomes?
   - Is naming convention consistent?

5. **Mock Usage**:
   - Are mocks used appropriately?
   - Are only external dependencies mocked?
   - Are mock setups clear and minimal?
   - Are mock verifications necessary and correct?

6. **Test Maintainability**:
   - Are tests easy to understand?
   - Is there excessive duplication?
   - Would test data builders help?
   - Are magic values explained?

7. **Assertion Quality**:
   - Are assertions specific (not just Assert.IsTrue)?
   - Do assertions check the right things?
   - Are error messages helpful?
   - Are multiple assertions in one test justified?

## Red Flags to Check

- Tests with no assertions
- Tests that test multiple unrelated things
- Tests that depend on execution order
- Tests with complex logic (tests testing tests)
- Overly brittle tests (testing implementation details)
- Tests with unclear names like "Test1", "TestMethod"

## Deliverable

Provide:
1. Overall quality score/assessment
2. Specific issues found with examples
3. Recommendations for improvement
4. Suggested refactorings (show before/after)

Apply standards from `.cursor/rules/unit-testing/` rules.
