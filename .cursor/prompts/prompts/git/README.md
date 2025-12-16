# Git Workflow Prompts

Prompts for Git operations, branching strategy, and release workflow.

## When These Prompts Are Used

### Automatic Triggers

**Tag Validation Failure** (`validate-tag-context.ps1`):
```
Use prompt: .cursor/prompts/git/fix-release-tag-workflow.prompt.md
```

**General Git Operations**:
- Creating branches following naming conventions
- Preparing commits with proper messages
- Creating merge/pull requests

## Available Prompts

### [`fix-release-tag-workflow.prompt.md`](./fix-release-tag-workflow.prompt.md) ⭐
**Purpose**: Fix incorrect release tags and understand proper release workflow

**Use when**:
- Pipeline fails: "Release tag is NOT on a stable branch"
- Created tag on wrong branch (feature/develop instead of main/release)
- Need guidance on test-* vs release-* tags
- Confused about RC testing phases
- Planning a release and want to follow correct workflow

**Provides**:
- Complete 4-phase release workflow
- Tag naming conventions and rules
- Branch and tag compatibility matrix
- Step-by-step fix instructions
- Common mistakes and corrections

### [`create-branch.prompt.md`](./create-branch.prompt.md)
**Purpose**: Create branches following project naming conventions

**Use when**:
- Starting new feature work
- Creating hotfix or bugfix branches
- Need to follow branch naming standards

### [`prepare-commit.prompt.md`](./prepare-commit.prompt.md)
**Purpose**: Create well-formatted, conventional commit messages

**Use when**:
- Making commits that follow conventional commits spec
- Need help writing clear commit messages
- Want to ensure commits are useful for CHANGELOG generation

### [`create-merge-request.prompt.md`](./create-merge-request.prompt.md)
**Purpose**: Create merge/pull requests with proper description and context

**Use when**:
- Ready to merge feature to develop
- Creating PR for code review
- Need structured PR description

## Quick Use Examples

### Fix Wrong Release Tag
```
Tell Cursor AI:
"I created release-0.1.0-rc1 on feature branch, help me fix it"

Or:
"Use the fix-release-tag-workflow prompt"
```

### Create Proper Release
```
Tell Cursor AI:
"Guide me through releasing version 0.1.0 following proper workflow"

Or:
"What's the correct workflow for test vs release tags?"
```

### Create Branch
```
Tell Cursor AI:
"Create feature branch for EPP-123 following naming conventions"
```

## Release Workflow Summary

### Phase 1: Development
```
feature/* → develop
```
- No tags on feature or develop branches
- CI validation only

### Phase 2: Internal Testing
```
develop → release/X.Y → test-X.Y.Z-rcN
```
- Tag `test-*` on release branches
- Published to TEST feed (internal only)
- QA testing phase

### Phase 3: Pre-Production Testing
```
release/X.Y → release-X.Y.Z-rcN
```
- Tag `release-*-rcN` on same commit as passing test RC
- Published to PROD feed as NuGet prerelease
- Consumer/staging testing

### Phase 4: Production Release
```
release/X.Y → main → release-X.Y.Z
```
- Merge to main
- Tag `release-*` (no -rcN suffix) on main
- Published to PROD feed as stable
- General availability

## Common Issues Solved

| Issue | Prompt to Use |
|-------|--------------|
| Wrong branch for tag | `fix-release-tag-workflow.prompt.md` |
| Skipped RC phase | `fix-release-tag-workflow.prompt.md` |
| test-* vs release-* confusion | `fix-release-tag-workflow.prompt.md` |
| Branch naming | `create-branch.prompt.md` |
| Commit message format | `prepare-commit.prompt.md` |
| PR description | `create-merge-request.prompt.md` |

## Related Documentation

- **Versioning Rules**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc`
- **Branch Lifecycle**: `.cursor/rules/git/branch-lifecycle-rule.mdc`
- **Branch Naming**: `.cursor/rules/git/branch-naming-rule.mdc`
- **Branch Structure**: `.cursor/rules/git/branch-structure-rule.mdc`
- **Branching Strategy**: `.cursor/rules/git/branching-strategy-overview.mdc`

## Tag and Branch Rules

### Allowed Tag Locations

| Tag Pattern | Allowed On | Purpose |
|------------|------------|---------|
| `test-*-rcN` | `release/X.Y` | Internal QA testing |
| `release-*-rcN` | `release/X.Y` | Pre-production testing |
| `release-*` (GA) | `main` | Production stable release |
| `coverage-*` | Any | Coverage analysis only |

### Branch Types

| Branch | Lifespan | Purpose |
|--------|----------|---------|
| `main` | Permanent | Production releases only |
| `develop` | Permanent | Integration branch |
| `release/X.Y` | Long-lived | Release line maintenance |
| `feature/*` | Temporary | Feature development |
| `fix/*` | Temporary | Bug fixes |
| `hotfix/*` | Temporary | Emergency production fixes |

---

**Last Updated**: 2025-12-06
