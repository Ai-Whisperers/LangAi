# CHANGELOG Generation Prompts

Automated prompts for generating and maintaining CHANGELOG.md from git commit history.

## Quick Start

**Need a CHANGELOG entry right now?**

```bash
# See what's changed since last release
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Then tell the AI:
> "Generate CHANGELOG entry for version 0.1.0-rc35 based on these commits"

See: [`quick-changelog-update.prompt.md`](./quick-changelog-update.prompt.md)

---

## Files in This Folder

### [`generate-changelog-from-git.prompt.md`](./generate-changelog-from-git.prompt.md)
**Comprehensive CHANGELOG generation process**

Use when:
- Building complete CHANGELOG from scratch
- Need to consolidate multiple releases
- Want to understand the full process
- Archiving old test releases

### [`quick-changelog-update.prompt.md`](./quick-changelog-update.prompt.md)
**Quick reference for common scenarios**

Use when:
- Single release entry needed
- Pipeline validation failure (urgent fix)
- Simple update with clear version

### [`agent-application-rule.prompt.md`](./agent-application-rule.prompt.md)
**AI agent guidance** (how AI knows when to use these prompts)

Reference for:
- Understanding automatic prompt application
- Troubleshooting prompt behavior
- Integration with CI/CD workflow

---

## Common Use Cases

### 1. Pipeline Failed - Missing CHANGELOG Entry

**Symptom**: 
```
❌ CHANGELOG.md missing entry for version 0.1.0-rc34!
```

**Fix**:
```
AI: Generate CHANGELOG entry for 0.1.0-rc34
[AI analyzes commits and creates entry]

Then run:
git add CHANGELOG.md
git commit -m "docs: Add release notes for 0.1.0-rc34"
git tag -d release-0.1.0-rc34
git push origin :refs/tags/release-0.1.0-rc34
git tag release-0.1.0-rc34
git push origin release-0.1.0-rc34
```

### 2. Multiple RCs Need Consolidation

**Scenario**: RC30 through RC34 were quick iterations, need one entry for RC35

```
AI: Generate consolidated CHANGELOG entry for 0.1.0-rc35 that 
summarizes all changes from 0.1.0-rc30 through 0.1.0-rc34. 
Archive intermediate test releases.
```

### 3. Setting Up CHANGELOG for First Time

```
AI: Create CHANGELOG.md for this project and generate entries 
for all existing release tags, archiving experimental early releases.
```

### 4. Preparing for GA Release

```
AI: Generate CHANGELOG entry for version 0.1.0 (GA release) that 
consolidates all RC releases with focus on user-facing changes.
```

---

## Workflow Integration

### Correct Order
1. **Make changes** → commit to branch
2. **Generate CHANGELOG** → commit CHANGELOG.md
3. **Create tag** → `release-X.Y.Z-rcN`
4. **Push tag** → triggers CI/CD pipeline
5. **Pipeline validates** → checks CHANGELOG has entry

### Pipeline Validation

The CI/CD pipeline runs `cicd/scripts/validate-release-notes.ps1` which:
- Extracts version from tag name
- Checks CHANGELOG.md for matching entry
- Fails build if entry missing

**Location**: `cicd/scripts/validate-release-notes.ps1`

---

## CHANGELOG Format

We follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to Eneve.Domain will be documented in this file.

## [X.Y.Z-rcN] - YYYY-MM-DD

**Release Tag**: [release-X.Y.Z-rcN](link-to-tag)

### Added
- New features and capabilities

### Changed
- Modifications to existing functionality

### Fixed
- Bug fixes

### Breaking Changes
- API changes that break compatibility
- Migration guidance

### Removed
- Removed features

### Deprecated
- Soon-to-be-removed features

### Security
- Vulnerability fixes
```

**Rules**:
- Most recent release at top
- Use ISO date format: `YYYY-MM-DD`
- Include release tag link
- Remove empty sections
- User-focused language (not implementation details)

---

## Git Command Reference

```bash
# List all release tags
git tag -l "release-*" --sort=version:refname

# Show commits between tags
git log release-0.1.0-rc34..release-0.1.0-rc35 --oneline

# Commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%h %s"

# Show tag details
git show release-0.1.0-rc34

# Delete local tag
git tag -d release-0.1.0-rc34

# Delete remote tag
git push origin :refs/tags/release-0.1.0-rc34

# Create new tag
git tag release-0.1.0-rc35

# Push tag
git push origin release-0.1.0-rc35

# Today's date for CHANGELOG
Get-Date -Format "yyyy-MM-dd"
```

---

## Categorization Guidelines

### Added (New Features)
**Indicators**: `feat:`, `feature:`, new public APIs, new capabilities

**Example Commits**:
- `feat: Add cache expiration strategies`
- `feat(domain): Implement validation framework`

**CHANGELOG Entry**:
```markdown
### Added
- **Cache Expiration**: Added sliding and absolute expiration strategies
  - Supports custom expiration policies
  - Automatic cleanup of expired entries
```

### Changed (Modifications)
**Indicators**: `refactor:`, `perf:`, improved behavior, dependency updates

**Example Commits**:
- `refactor: Simplify repository error handling`
- `perf: Optimize cache lookup performance`

**CHANGELOG Entry**:
```markdown
### Changed
- **Error Handling**: Improved exception messages and error context
  - More detailed error information for debugging
  - Better handling of edge cases
```

### Fixed (Bug Fixes)
**Indicators**: `fix:`, error corrections, regression fixes

**Example Commits**:
- `fix: Memory leak in cache disposal`
- `fix(validation): Null reference in validator`

**CHANGELOG Entry**:
```markdown
### Fixed
- **Memory Leak**: Cache entries now properly dispose resources
  - Fixed cleanup timer not releasing memory
  - Entries implement IDisposable pattern correctly
```

### Breaking Changes
**Indicators**: `BREAKING CHANGE:` in commit body, API signature changes

**Example Commits**:
- `feat!: Change cache key to strongly-typed value object`
- `refactor: Remove deprecated methods`

**CHANGELOG Entry**:
```markdown
### Breaking Changes
- **Cache Key API**: Changed from `string` to `CacheKey` value object
  - **Before**: `cache.Get("mykey")`
  - **After**: `cache.Get(CacheKey.Create("mykey"))`
  - **Migration**: Wrap all string keys with `CacheKey.Create()`
  - **Reason**: Type safety and validation
```

---

## Archiving Strategy

### When to Archive Releases

**Archive** (move to "Archived Releases" section):
- ✅ Test releases (`yesy-*` tags) that were experimental
- ✅ Rapid RC iterations (multiple RCs same day)
- ✅ Very old RCs from early development (>6 months)
- ✅ RCs with no significant changes

**Keep Individual Entries**:
- ✅ RCs deployed to staging/production
- ✅ RCs with significant features
- ✅ RCs that fixed critical bugs
- ✅ GA releases (always keep)

### Archived Releases Format

```markdown
## Archived Releases

### Test Releases (0.1.0-rc20 through 0.1.0-rc33) - 2025-11-15 to 2025-12-04
Brief summary of what this phase accomplished:
- CI/CD pipeline refinement
- Build optimization experiments  
- Azure DevOps configuration testing

View all tags: [releases](https://dev.azure.com/Energy21/NuGet%20Packages/_git/eneve.domain/tags)

### Early Development (0.1.0-rc1 through 0.1.0-rc19) - 2025-Q3
Initial project setup and foundation:
- Domain model design
- Project structure
- Basic build pipeline

View tags: [0.1.0-rc1](link) | [0.1.0-rc2](link) | ... [0.1.0-rc19](link)
```

---

## Troubleshooting

### Issue: "Can't categorize commits"
**Solution**: Provide explicit guidance
```
Categorize these commits for CHANGELOG:
- abc1234: Add cache feature → Added
- def5678: Fix null reference → Fixed  
- ghi9012: Refactor validation → Changed
```

### Issue: "Too many entries, CHANGELOG cluttered"
**Solution**: Use consolidation
```
Generate single consolidated entry for version 0.1.0-rc35 
that summarizes rc30-rc34, archiving intermediate releases.
```

### Issue: "Breaking changes not detected"
**Solution**: Manual review
```
Review these commits for breaking changes:
[paste commits]

Pay attention to:
- API signature changes
- Removed public methods
- Changed behavior
```

### Issue: "Git history too large"
**Solution**: Process in batches
```
Generate CHANGELOG entries for releases between 
2025-11-01 and 2025-12-06 only.
```

---

## Related Documentation

### Project Rules
- **Tag-Based Versioning**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc`
- **Commit Messages**: `.cursor/rules/development-commit-message.mdc`

### External Standards
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Pipeline Scripts
- `cicd/scripts/validate-release-notes.ps1` - CHANGELOG validation
- `cicd/azure-pipelines.yml` - CI/CD configuration

---

## Examples

See [`generate-changelog-from-git.prompt.md`](./generate-changelog-from-git.prompt.md) for complete examples including:
- Individual RC entries
- Consolidated entries
- Archived releases section
- Breaking changes with migration guidance
- Complete CHANGELOG.md structure

---

**Last Updated**: 2025-12-06  
**Maintainer**: Development Team  
**Questions**: See `agent-application-rule.md` or ask the AI

