---
name: create-user-story
description: "Create a well-structured User Story following INVEST principles with Given-When-Then acceptance criteria"
category: agile
tags: agile, user-story, INVEST, acceptance-criteria, story-writing
argument-hint: "Feature context and user role"
---

# Create User Story for [Feature]

Create a well-structured Agile User Story following INVEST principles.

**Required Context**:

- `[FEATURE_CONTEXT]`: Description of the feature or Epic.
- `[USER_ROLE]`: The persona (e.g., "System Admin").
- `[USER_NEED]`: What they want to achieve.
- `[BUSINESS_VALUE]`: Why this matters.

## Reasoning Process

1. **Identify Value**: Determine the "So That" clause (Business Value).
2. **Draft Narrative**: Create the "As a... I want... So that..." statement.
3. **Define Scope**: List what is IN scope and OUT of scope.
4. **Draft Acceptance Criteria**: Write Given-When-Then scenarios covering happy/edge cases.
5. **Review INVEST**: Check if it's Independent, Negotiable, Valuable, Estimable, Small, Testable.

## Process

1. **Story Identifier**:
   - Format: `US-[Feature]-[Number]`
   - Example: `US-AUTH-001`

2. **Story Statement**:
   ```text
   As a [user role]
   I want to [goal/need]
   So that [benefit/value]
   ```

3. **Acceptance Criteria**:
   - Given-When-Then format
   - 3-7 specific, testable criteria
   - Cover happy path and key edge cases
   - Clear pass/fail determination

4. **Story Details**:
   - Description: Detailed context and background
   - Business value: Why this matters
   - User impact: Who benefits and how
   - Dependencies: Related stories or prerequisites
   - Assumptions: What we're assuming is true

5. **Technical Considerations**:
   - Affected components
   - API or integration impacts
   - Data model changes
   - Performance considerations
   - Security considerations

6. **Size Estimation**:
   - Story points (Fibonacci: 1, 2, 3, 5, 8)
   - Complexity assessment
   - Risk factors
   - Split recommendation if too large (>8 points)

7. **Definition of Done**:
   - Code complete and reviewed
   - Unit tests written and passing
   - Integration tests passing
   - Documentation updated
   - Acceptance criteria met

## Examples (Few-Shot)

**Input**:
Role: User. Need: Reset password.

**Reasoning**:

- Value: Regain access to account.
- Criteria: Email sent, link validity, new password enforcement.

**Output**:
> **Story**: As a User, I want to reset my password, So that I can regain access if I forget it.
> **AC1**: Given I am on login page, When I click 'Forgot Password', Then I receive an email.
> **AC2**: Given I have a valid link, When I enter a weak password, Then the system rejects it.

## Expected Output

**Deliverables**:

1. Complete User Story markdown.
2. Acceptance Criteria list.
3. Technical Impact analysis.

**Format**: Agile Story Markdown.

## Quality Criteria

- [ ] Follows "As a... I want... So that..." format.
- [ ] ACs use Given-When-Then.
- [ ] Includes Technical Considerations.
- [ ] Meets INVEST principles.

---

**Applies Rules**:

- `.cursor/rules/agile/user-story-documentation-rule.mdc`
- `.cursor/rules/agile/story-splitting-rule.mdc`
