---
name: split-user-story
description: "Split a large user story into smaller vertical slices using proven splitting patterns"
category: agile
tags: agile, story-splitting, vertical-slices, size-reduction
argument-hint: "Story ID and current size"
---

# Split User Story

The following user story is too large and needs to be split:

**Story ID**: `[REPLACE WITH STORY ID]`
**Story Title**: `[REPLACE WITH STORY TITLE]`
**Current Size**: `[REPLACE WITH CURRENT STORY POINTS]`

## Splitting Analysis

1. **Review Story**:
   - Identify all distinct functionalities
   - Find natural boundaries
   - Look for workflow steps
   - Identify CRUD operations
   - Find different user roles or scenarios

2. **Splitting Patterns**:
   - **Workflow Steps**: Split by sequential steps in a process
   - **Business Rules**: Split by different validation/business rules
   - **CRUD Operations**: Create, Read, Update, Delete as separate stories
   - **Data Variations**: Different types of data or inputs
   - **Operations**: Simple vs complex versions
   - **User Roles**: Different actors with different needs
   - **Acceptance Criteria**: Each criterion becomes a story
   - **Spike + Implementation**: Research story + implementation story

3. **Vertical Slices**:
   - Each split story should deliver end-to-end value
   - Each story should be independently deployable
   - Each story should have clear acceptance criteria
   - Avoid horizontal splits (e.g., just UI, just backend)

## Splitting Guidelines

- **Target Size**: Each split story should be 1-5 points
- **Maintain Value**: Each story delivers user value
- **Independent**: Stories can be done in any order (if possible)
- **Testable**: Each story has clear pass/fail criteria
- **Order**: Consider if there's a logical implementation sequence

## Deliverable

Provide:

1. Analysis of why story is too large
2. Recommended splitting strategy (which pattern)
3. List of split stories with:
   - New story IDs
   - Story statements (As a... I want... So that...)
   - Acceptance criteria for each
   - Size estimate for each
   - Dependencies between stories (if any)
4. Implementation sequence recommendation
5. Verification that each split is independently valuable

Follow guidelines from:

- `.cursor/rules/agile/story-splitting-rule.mdc`
- `.cursor/rules/agile/user-story-documentation-rule.mdc`

