---
name: fix-release-tag-workflow
description: "Guide for fixing incorrect release tags and following proper workflow"
category: git
tags: git, release, tags, workflow, CI/CD, versioning
argument-hint: "Describe the tag issue or ask for workflow guidance"
---

# Fix Release Tag Workflow Issues

## Purpose

Resolve CI/CD pipeline failures caused by creating release tags on incorrect branches, and guide proper release workflow according to tag-based versioning strategy.

## When to Use

- Pipeline fails: "Release tag is NOT on a stable branch"
- Created `release-*` tag on feature/fix/develop branch
- Need guidance on proper RC and release workflow
- Confusion about when to use `test-*` vs `release-*` tags

## Common Scenarios

### Scenario 1: Tag Created on Wrong Branch

**Problem**: Created `release-0.1.0-rc1` on `feature/my-feature` branch

**Solution**:

```bash
# 1. Delete the incorrect tag
git tag -d release-0.1.0-rc1
git push origin :refs/tags/release-0.1.0-rc1

# 2. Follow correct workflow (see below)
```

### Scenario 2: Skipped RC Testing Phase

**Problem**: Trying to release directly to production without RC testing

**Solution**: Always use two-stage RC workflow:
1. Internal testing with `test-*` tags
2. Pre-production testing with `release-*-rcN` tags
3. Production release with `release-*` (no suffix)

### Scenario 3: Wrong Tag Type for Branch

**Problem**: Used `release-*` tag on `release/X.Y` branch (should use `test-*`)

**Solution**: RC testing on release branches uses `test-*` tags; `release-*` tags go on `main`

## Complete Release Workflow

### Phase 1: Development
```
feature branches → develop
├─ CI runs on every push
├─ Build, test, coverage validation
└─ NO TAGS on feature or develop branches
```

**Actions**:
```bash
# Work on feature
git checkout -b feature/EPP-123-add-cache develop
# ... make changes ...
git commit -m "feat: Add cache implementation"
git push origin feature/EPP-123-add-cache

# Create PR to develop
# Merge after approval
```

### Phase 2: Internal RC Testing (test-* tags)

**Purpose**: Internal QA testing before external release

**Workflow**:
```
develop → release/X.Y branch → test-X.Y.Z-rcN tags
```

**Actions**:
```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/0.1 develop
git push origin release/0.1

# 2. Tag for internal RC testing
git tag -a test-0.1.0-rc1 -m "Internal RC1 for version 0.1.0"
git push origin test-0.1.0-rc1

# Pipeline publishes to TEST feed (internal only)
# QA team tests in test environment

# 3. If issues found, fix on release/0.1
git checkout release/0.1
# ... fix bugs ...
git commit -m "fix: Resolve validation issue"
git push origin release/0.1

# 4. Tag next RC
git tag -a test-0.1.0-rc2 -m "Internal RC2 with fixes"
git push origin test-0.1.0-rc2

# Repeat until test-* RC passes internal QA
```

**Key Rules**:
- ✅ `test-*` tags go on `release/X.Y` branches
- ✅ Published to TEST feed (internal only)
- ✅ Can iterate quickly (rc1, rc2, rc3...)
- ✅ Forward-merge fixes to `develop`

### Phase 3: Pre-Production RC Testing (release-*-rcN tags)

**Purpose**: External/consumer testing before GA release

**Workflow**:
```
SAME COMMIT as passing test-* RC → release-X.Y.Z-rcN tag on release/X.Y
Then merge to main for final tag
```

**Actions**:
```bash
# After test-0.1.0-rcN passes internal QA:

# 1. Tag for pre-production testing (SAME COMMIT, no code changes!)
git checkout release/0.1
# Ensure you're on the commit that passed test-* RC
git tag -a release-0.1.0-rc1 -m "Pre-production RC1 for version 0.1.0"
git push origin release-0.1.0-rc1

# Pipeline publishes to PROD feed as NuGet prerelease
# Consumers can opt-in: dotnet add package MyPackage --prerelease
# Test in staging/pre-production environments

# 2. If issues found, fix and re-tag
git checkout release/0.1
# ... fix bugs ...
git commit -m "fix: Resolve pre-prod issue"
git push origin release/0.1

git tag -a release-0.1.0-rc2 -m "Pre-production RC2 with fixes"
git push origin release-0.1.0-rc2

# Repeat until release-*-rcN passes consumer testing
```

**Key Rules**:
- ✅ First `release-*-rcN` uses SAME COMMIT as last passing `test-*-rcN`
- ✅ Published to PROD feed as NuGet prerelease
- ✅ Consumers opt-in with `--prerelease` flag
- ✅ Can iterate if issues found (rc1, rc2...)

### Phase 4: Production Release (release-* without suffix)

**Purpose**: General availability stable release

**Workflow**:
```
SAME COMMIT as passing release-*-rcN → merge to main → release-X.Y.Z tag on main
```

**Actions**:
```bash
# After release-0.1.0-rcN passes all testing:

# 1. Merge release branch to main
git checkout main
git pull origin main
git merge --no-ff release/0.1 -m "Merge release/0.1 for version 0.1.0"
git push origin main

# 2. Tag GA release on main (NO -rcN suffix = stable)
git tag -a release-0.1.0 -m "Production release 0.1.0"
git push origin release-0.1.0

# Pipeline publishes to PROD feed as stable NuGet package
# Consumers get it by default: dotnet add package MyPackage

# 3. Forward-merge to develop
git checkout develop
git merge --no-ff main -m "Merge main to develop after 0.1.0 release"
git push origin develop
```

**Key Rules**:
- ✅ `release-*` (no suffix) MUST be on `main` branch
- ✅ SAME COMMIT as last passing `release-*-rcN`
- ✅ Published to PROD feed as stable
- ✅ No code changes between last RC and GA
- ✅ Always forward-merge to develop

## Version Progression Examples

### Example 1: First Release
```
develop
 ↓
release/0.1
 ├─ test-0.1.0-rc1 (fix bugs)
 ├─ test-0.1.0-rc2 (passes QA) ✓
 ├─ release-0.1.0-rc1 (SAME COMMIT, passes pre-prod) ✓
 ↓
main
 └─ release-0.1.0 (SAME COMMIT, GA) ✓
```

### Example 2: Patch Release
```
release/0.1 (still exists)
 ├─ test-0.1.1-rc1 (hotfix, passes QA) ✓
 ├─ release-0.1.1-rc1 (SAME COMMIT, passes pre-prod) ✓
 ↓
main
 └─ release-0.1.1 (SAME COMMIT, GA) ✓
```

### Example 3: Major Version (Multiple Iterations)
```
release/1.0
 ├─ test-1.0.0-rc1 (issues found)
 ├─ test-1.0.0-rc2 (issues found)
 ├─ test-1.0.0-rc3 (passes QA) ✓
 ├─ release-1.0.0-rc1 (SAME COMMIT, issues in pre-prod)
 ├─ release-1.0.0-rc2 (passes pre-prod) ✓
 ↓
main
 └─ release-1.0.0 (SAME COMMIT, GA) ✓
```

## Tag Naming Reference

### Test Tags (Internal QA)
```
test-X.Y.Z-rcN
├─ test-0.1.0-rc1   ✓ Valid
├─ test-0.1.0-rc2   ✓ Valid
├─ test-1.0.0-rc1   ✓ Valid
└─ test-0.1.0       ❌ Must have -rcN suffix
```

### Release Tags (Pre-Production & GA)
```
release-X.Y.Z[-rcN]
├─ release-0.1.0-rc1   ✓ Valid (prerelease)
├─ release-0.1.0-rc2   ✓ Valid (prerelease)
├─ release-0.1.0       ✓ Valid (stable GA)
├─ release-1.0.0-rc1   ✓ Valid (prerelease)
└─ release-1.0.0       ✓ Valid (stable GA)
```

### Coverage Tags (Analysis Only)
```
coverage-X.Y.Z
└─ coverage-0.1.0   ✓ Valid (no publishing)
```

## Branch and Tag Matrix

| Branch Type | test-* Tags | release-*-rcN Tags | release-* Tags (GA) |
|------------|-------------|-------------------|---------------------|
| `main` | ❌ | ❌ | ✅ (GA only) |
| `develop` | ❌ | ❌ | ❌ |
| `release/X.Y` | ✅ | ✅ | ❌ (merge to main first) |
| `feature/*` | ❌ | ❌ | ❌ |
| `fix/*` | ❌ | ❌ | ❌ |
| `hotfix/*` | ❌ | ❌ | ❌ |

## Quick Decision Tree

```
┌─ Do you have code to release?
│
├─ YES → Where is the code?
│   │
│   ├─ On feature/fix branch?
│   │   └─ Create PR → Merge to develop → Continue below
│   │
│   ├─ On develop branch?
│   │   └─ Create release/X.Y branch → Tag test-X.Y.Z-rc1
│   │
│   ├─ On release/X.Y branch?
│   │   ├─ Still in internal QA? → Tag test-X.Y.Z-rcN
│   │   ├─ Passed internal QA? → Tag release-X.Y.Z-rc1 (SAME COMMIT)
│   │   └─ Passed pre-prod? → Merge to main → Tag release-X.Y.Z on main
│   │
│   └─ Already on main?
│       └─ Tag release-X.Y.Z (if all RCs passed)
│
└─ NO → Keep working on feature branch
```

## Common Mistakes and Fixes

### Mistake 1: Tagging develop branch
```bash
# ❌ Wrong
git checkout develop
git tag release-0.1.0-rc1  # DON'T DO THIS

# ✅ Correct
git checkout -b release/0.1 develop
git tag test-0.1.0-rc1  # Start with test-* tags
```

### Mistake 2: Skipping test-* phase
```bash
# ❌ Wrong
git checkout release/0.1
git tag release-0.1.0-rc1  # Skipped internal testing

# ✅ Correct
git checkout release/0.1
git tag test-0.1.0-rc1      # Internal QA first
# ... QA passes ...
git tag release-0.1.0-rc1   # Then pre-prod (SAME COMMIT)
```

### Mistake 3: GA tag on release branch
```bash
# ❌ Wrong
git checkout release/0.1
git tag release-0.1.0  # GA tag on release branch

# ✅ Correct
git checkout main
git merge --no-ff release/0.1
git tag release-0.1.0  # GA tag on main
```

### Mistake 4: Code changes between RC and GA
```bash
# ❌ Wrong
git tag release-0.1.0-rc1
# ... make more commits ...
git tag release-0.1.0  # Different code!

# ✅ Correct
git tag release-0.1.0-rc1
# ... testing passes, NO code changes ...
git tag release-0.1.0  # SAME COMMIT as rc1
```

## Checklist Before Tagging

**Before tagging `test-X.Y.Z-rcN`**:
- [ ] On `release/X.Y` branch
- [ ] All features for version complete
- [ ] Tests passing locally
- [ ] Ready for internal QA testing

**Before tagging `release-X.Y.Z-rcN`**:
- [ ] Latest `test-*-rcN` passed internal QA
- [ ] Using SAME COMMIT as passing test RC
- [ ] CHANGELOG.md updated
- [ ] Ready for consumer/staging testing

**Before tagging `release-X.Y.Z`** (GA):
- [ ] Latest `release-*-rcN` passed all testing
- [ ] Using SAME COMMIT as passing release RC
- [ ] Merged to `main` branch
- [ ] Currently on `main` branch
- [ ] CHANGELOG.md has entry for this version
- [ ] All required documentation updated

## Related Documentation

- **Tag-Based Versioning**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc`
- **Branch Lifecycle**: `.cursor/rules/git/branch-lifecycle-rule.mdc`
- **Branch Naming**: `.cursor/rules/git/branch-naming-rule.mdc`
- **CHANGELOG Prompt**: `.cursor/prompts/changelog/quick-changelog-update.md`

## Need Help?

Ask Cursor AI:
- "Help me create release tag X.Y.Z-rcN following proper workflow"
- "I created a tag on the wrong branch, how do I fix it?"
- "Explain the difference between test-* and release-* tags"
- "What's the correct workflow for releasing version X.Y.Z?"

---

**Version**: 1.0.0
**Last Updated**: 2025-12-06
**Triggered by**: `validate-tag-context.ps1` failures
