---
name: generate-missing-tests
description: "Generate comprehensive unit tests with AAA pattern and FluentAssertions for high coverage"
category: unit-testing
tags: unit-testing, test-generation, test-automation, aaa-pattern, fluentassertions
argument-hint: "Target class or method to test"
---

# Generate Missing Unit Tests for [Class/Method]

Create comprehensive unit tests for a specific target, ensuring high coverage and quality.

**Required Context**:
- `[TARGET_CODE]`: The Class or Method to be tested. (Wrap in XML tags if pasting code)
- `[TEST_PROJECT_PATH]`: Path to the existing test project (to match namespace/conventions).

**Optional Parameters**:
- `[EXISTING_TESTS]`: Path to existing tests (to avoid duplication).

## Reasoning Process
1. **Analyze Logic**: Understand the branching logic, loops, and edge cases of `[TARGET_CODE]`.
2. **Identify Scenarios**: List all Happy Path, Edge Case, and Error Case scenarios.
3. **Plan Structure**: Decide on test method names and `AAA` (Arrange-Act-Assert) setup.
4. **Mock Dependencies**: Identify external dependencies that need mocking (Moq/NSubstitute).
5. **Draft Tests**: Write the code.

## Process

1. **Test Coverage Scenarios**:
   - Happy path (expected successful execution)
   - Edge cases (boundaries, empty inputs, nulls)
   - Error cases (invalid inputs, exceptions)
   - State transitions (for stateful objects)
   - Integration points (dependencies, mocks)

2. **Test Structure**:
   - Use AAA pattern (Arrange, Act, Assert)
   - One logical assertion per test
   - Descriptive test method names following convention
   - Proper setup and teardown if needed

3. **Test Quality**:
   - Tests should be independent (no test interdependencies)
   - Mock external dependencies appropriately
   - Use test data builders or fixtures for complex objects
   - Include both positive and negative test cases

4. **Documentation**:
   - Add XML documentation to test classes
   - Comment complex test setups or assertions
   - Document what behavior is being tested

5. **Naming Convention**:
   - Follow pattern: `MethodName_StateUnderTest_ExpectedBehavior`
   - Or: `Given_Precondition_When_Action_Then_Outcome`

## Examples (Few-Shot)

**Input Code**:
```csharp
public int Divide(int a, int b) {
    if (b == 0) throw new DivideByZeroException();
    return a / b;
}
```

**Reasoning**:
- Needs happy path (10/2).
- Needs error case (10/0) -> Expect Exception.

**Output**:
```csharp
[Fact]
public void Divide_WhenDivisorIsZero_ThrowsDivideByZeroException()
{
    // Arrange
    var calculator = new Calculator();

    // Act
    Action act = () => calculator.Divide(10, 0);

    // Assert
    act.Should().Throw<DivideByZeroException>();
}
```

## Expected Output

**Deliverables**:
1. Complete test file(s) code.
2. List of scenarios covered.

**Format**: C# Code Block

## Quality Criteria

- [ ] All public methods covered.
- [ ] At least one negative test case per method.
- [ ] Uses `FluentAssertions` (if available).
- [ ] Mocks are used for interfaces.

---

**Applies Rules**:
- `.cursor/rules/unit-testing/unit-test-coverage-rule.mdc`
