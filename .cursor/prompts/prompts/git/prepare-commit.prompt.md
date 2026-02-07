---
name: prepare-commit
description: "Prepare a conventional commit message"
category: git
tags: git, commit, conventional-commits, workflow, standards
argument-hint: "Brief description of changes"
---

# Prepare Git Commit

Please help me prepare a proper Git commit for the current changes:

**Context**: `[REPLACE WITH BRIEF DESCRIPTION OF CHANGES]`

## Commit Preparation

1. **Review Changes**:
   - Show current git status
   - List all modified/added/deleted files
   - Identify what changes belong in this commit
   - Flag any files that should not be committed

2. **Generate Commit Message**:
   - Follow conventional commit format
   - Structure: `<type>(<scope>): <subject>`
   - Types: feat, fix, docs, refactor, test, chore, perf, style
   - Include ticket reference if applicable
   - Subject: Imperative mood, under 72 characters
   - Body: Explain WHAT and WHY (not HOW)

3. **Commit Message Template**:
   ```
   <type>(<scope>): <subject>

   <body explaining what and why>

   Refs: [TICKET-ID]
   ```

4. **Stage Files Properly**:
   - Provide commands to stage relevant files
   - Exclude debug/temp files
   - Exclude generated files
   - Exclude IDE-specific files

5. **Pre-Commit Validation**:
   - Are there any linter errors?
   - Do all tests pass?
   - Is code formatted correctly?
   - Are there debug statements to remove?

## Conventional Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies
- **perf**: Performance improvements
- **style**: Code style/formatting changes

## Deliverable

Provide:
1. List of files to stage (with reasons)
2. Proposed commit message following standards
3. Git commands to execute:
   ```bash
   # Stage specific files
   git add [file1] [file2]

   # Commit with message
   git commit -m "[commit message]"

   # Or commit with editor for multi-line message
   git commit
   ```
4. Pre-commit checklist status

Apply commit standards from:
- `.cursor/rules/development-commit-message.mdc`
- `.cursor/rules/git/branch-lifecycle-rule.mdc`
