---
name: Document Breaking API Changes
description: Document breaking API changes with comprehensive migration guidance for package consumers
category: breaking-changes
tags: [breaking-changes, api, migration, documentation]
---

# Document Breaking API Changes

## Purpose

Generate comprehensive documentation for breaking API changes detected by the CI/CD pipeline, including migration guidance for package consumers.

## Input Requirements

Provide one of the following:

1. **API Compatibility Report**: Output from `check-breaking-changes.ps1`
2. **Specific Breaking Changes**: Description of what changed
3. **Commit Range**: Git commits containing breaking changes

## Instructions

### Step 1: Analyze Breaking Changes

Review the breaking changes and categorize them:

**Categories**:
- **Signature Changes**: Method parameters, return types modified
- **Removals**: Public APIs removed
- **Renames**: Classes, methods, or properties renamed
- **Behavior Changes**: Functionality changed in incompatible ways
- **Dependency Changes**: Required dependency versions changed

### Step 2: Document in CHANGELOG.md

For each breaking change, add to CHANGELOG.md under the version being released:

```markdown
## [X.Y.0] - YYYY-MM-DD

**⚠️ BREAKING CHANGES - Major Version Release**

### Breaking Changes

#### API Change Title

**What Changed**: Clear description of the breaking change

**Reason**: Why this change was necessary
- Business justification
- Technical necessity
- Long-term benefit

**Before** (v1.x):
```csharp
// Old API usage
public void OldMethod(string param1)
{
    // Implementation
}
```

**After** (v2.0):
```csharp
// New API usage
public void NewMethod(string param1, int param2 = 0)
{
    // Implementation
}
```

**Migration Steps**:
1. Update all calls to `OldMethod`
2. Add second parameter (default value: 0)
3. Review behavior for edge cases
4. Test thoroughly

**Impact**: Who is affected and how
- Direct consumers of this API
- Indirect consumers via dependencies

**Timeline**: When this change takes effect
- Deprecated since: v1.5.0
- Removed in: v2.0.0
```

### Step 3: Version Number Requirements

Breaking changes require MAJOR version increment:

**Semantic Versioning**:
- Current: `1.5.2`
- Required: `2.0.0`

**Tag Pattern**:
- RC: `release-2.0.0-rc1`
- GA: `release-2.0.0`

### Step 4: Update README.md

Add migration guide section:

```markdown
## Upgrading from v1.x to v2.0

### Breaking Changes Summary

See [CHANGELOG.md](CHANGELOG.md) for complete details.

**Quick Migration Checklist**:
- [ ] Update package reference to v2.0.0
- [ ] Review breaking changes list
- [ ] Update API calls following migration steps
- [ ] Run tests and verify behavior
- [ ] Update any documentation
```

## Quality Checklist

- [ ] All breaking changes documented
- [ ] Migration steps are actionable and tested
- [ ] Before/after code examples included
- [ ] Reason/justification provided
- [ ] Impact assessment included
- [ ] Timeline clearly stated
- [ ] Version number incremented to MAJOR
- [ ] README updated with migration guide

## Related Documentation

- **CHANGELOG Prompt**: `.cursor/prompts/changelog/quick-changelog-update.md`
- **Versioning Rules**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc`
- **Documentation Standards**: `.cursor/rules/documentation/documentation-standards-rule.mdc`

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-06  
**Triggered by**: `check-breaking-changes.ps1` failures

