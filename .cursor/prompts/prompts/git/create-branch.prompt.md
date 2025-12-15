---
name: create-branch
description: "Create a standard-compliant Git branch"
category: git
tags: git, branch, workflow, naming, standards
argument-hint: "Ticket ID and branch type (e.g., EPP-1234, feature)"
---

# Create Git Branch

Please help me create a new Git branch for this work:

**Ticket/Task**: `[REPLACE WITH TICKET ID OR TASK DESCRIPTION]`
**Branch Type**: `[REPLACE WITH: feature/fix/hotfix]`

## Branch Creation

1. **Validate Branch Name**:
   - Ensure it follows the naming convention
   - Pattern: `(feature|fix|hotfix)/[A-Z]+-\d+(-[a-z0-9-]+)?`
   - Examples: `feature/EPP-1234-add-validation`, `fix/EPP-5678-null-check`
   - Verify ticket ID is valid

2. **Determine Source Branch**:
   - Features: Branch from `develop`
   - Fixes: Branch from `develop`
   - Hotfixes: Branch from `main`
   - Release candidates: Branch from `release/X.Y.Z`

3. **Check Current State**:
   - What branch am I currently on?
   - Are there uncommitted changes?
   - Is the source branch up to date?
   - Any conflicts to be aware of?

4. **Provide Commands**:
   - Command to update source branch
   - Command to create new branch
   - Command to push branch to remote

## Deliverable

Provide:
1. Validated branch name
2. Source branch determination
3. Step-by-step commands to execute:
   ```bash
   # Ensure source is up to date
   git checkout [source-branch]
   git pull origin [source-branch]
   
   # Create and checkout new branch
   git checkout -b [branch-name]
   
   # Push to remote (after first commit)
   git push -u origin [branch-name]
   ```
4. Confirmation that branch name follows standards

Apply branch naming standards from:
- `.cursor/rules/git/branch-naming-rule.mdc`
- `.cursor/rules/git/branch-structure-rule.mdc`
- `.cursor/rules/git/branch-lifecycle-rule.mdc`

