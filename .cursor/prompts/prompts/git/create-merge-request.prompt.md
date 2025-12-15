---
name: create-merge-request
description: "Create a comprehensive Merge Request description"
category: git
tags: git, merge-request, pull-request, documentation, workflow
argument-hint: "Ticket ID and summary of changes"
---

# Create Merge Request Description

Generate a structured and comprehensive description for a Git Merge Request / Pull Request.

**Required Context**:
- `[TICKET_ID]`: The Jira/Ticket ID (e.g., EPP-123).
- `[TITLE]`: Brief summary of changes.
- `[TYPE]`: Feature, Bugfix, Hotfix, Refactor.
- `[CHANGES]`: Summary of what was modified.

## Reasoning Process
1.  **Identify Type**: Determine if this is a Feature, Fix, or Hotfix to set the template.
2.  **Summarize Changes**: Group changes logically (New Features, Fixes, Technical Changes).
3.  **Verify Quality Gates**: Checklist for tests, documentation, and standards.
4.  **Assess Risk**: Identify potential impacts or regressions.
5.  **Provide Instructions**: Steps to test or validate the change.

## Process

1.  **Title Format**:
    - `[Ticket-ID]: [Short Description]`
    - Example: `EPP-123: Add User Authentication`

2.  **Overview**:
    - What does this MR do?
    - Why is it needed?
    - Link to Ticket.

3.  **Key Changes**:
    - Bulleted list of major modifications.

4.  **Technical Details**:
    - Database changes?
    - API changes?
    - Dependency updates?

5.  **Testing Steps**:
    - How can the reviewer verify this?
    - Specific test cases or data.

6.  **Checklist**:
    - Standard quality checks (Linting, Tests, Docs).

## Examples (Few-Shot)

**Input**:
Ticket: EPP-123. Title: Fix login bug. Changes: Updated auth service, added unit test.

**Output**:
> **Title**: EPP-123: Fix login timeout issue
> **Overview**: Fixes the session timeout bug where users were logged out after 5 minutes.
> **Changes**:
> - Increased token lifetime in `AuthService`.
> - Added unit tests for session duration.
> **Testing**: Login and wait 6 minutes. Verify session persists.

## Expected Output

**Deliverables**:
1.  Complete Merge Request description markdown.

**Format**: Markdown.

## Quality Criteria

- [ ] Starts with Ticket ID.
- [ ] Clear summary of changes.
- [ ] Includes "How to Test" section.
- [ ] Includes Quality Checklist.

---

**Applies Rules**:
- `.cursor/rules/git/branch-lifecycle-rule.mdc`
- `.cursor/rules/development-commit-message.mdc`

