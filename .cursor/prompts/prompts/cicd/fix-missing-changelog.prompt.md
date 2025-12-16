---
name: fix-missing-changelog
description: Generate missing CHANGELOG entries for releases following Keep a Changelog format
category: cicd
tags: changelog, release, documentation, versioning
---

# Fix Missing CHANGELOG Entry

**Pattern**: Error Resolution Helper | **Effectiveness**: High | **Use When**: CI/CD validation reports missing CHANGELOG entry for a release

## Purpose

Guide developers through creating missing CHANGELOG entries for releases, ensuring proper Keep a Changelog format, comprehensive documentation of changes, and user-focused descriptions for professional release notes.

## User Process

When CI/CD reports a missing CHANGELOG entry:

1. **Identify Version**: Note the version number requiring documentation
2. **Review Git History**: Examine commits since last release to understand changes
3. **Choose Fix Method**: Select automated (git analysis), AI-assisted (high quality), or manual (full control)
4. **Categorize Changes**: Group into Breaking/Added/Changed/Fixed/etc.
5. **Write User-Focused**: Describe what changed from end-user perspective
6. **Validate**: Run validation script to confirm entry format and completeness

## Context

CHANGELOG.md is missing an entry for version **`<VERSION>`**. All releases must be documented following [Keep a Changelog](https://keepachangelog.com) format.

## What's Wrong

When creating a release tag, CHANGELOG.md must contain a corresponding entry documenting what changed in that version.

## Automated Fix

Run this command to generate CHANGELOG entry from git history:

```powershell
cd cicd/scripts
.\fix-errors.ps1 -Fix MissingChangelog -Version "<VERSION>"
```

**What it does:**
- Analyzes git commits since last release
- Categorizes changes (Added/Changed/Fixed/Breaking)
- Generates formatted CHANGELOG entry
- **You should review and enhance descriptions!**

## AI-Assisted Fix (Recommended)

Ask me (Cursor AI) for a high-quality CHANGELOG entry:

### Prompt Template

```
Generate a CHANGELOG entry for version <VERSION> from git history.

Steps:
1. Run: git log <LAST_TAG>..HEAD --pretty=format:"%s"
2. Analyze all commits since last release
3. Categorize into Keep a Changelog sections:
   - Breaking Changes (if any)
   - Added (new features)
   - Changed (modifications to existing features)
   - Fixed (bug fixes)
   - Deprecated (features marked for removal)
   - Removed (features removed)
   - Security (security-related changes)

4. Write clear, user-focused descriptions
5. Add to CHANGELOG.md following Keep a Changelog format
6. Include release date: $(Get-Date -Format yyyy-MM-dd)
7. Add link to tag at bottom

Format:
```markdown
## [<VERSION>] - YYYY-MM-DD

### Breaking Changes
- Description of breaking change and migration path

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description

[<VERSION>]: https://github.com/yourorg/yourrepo/releases/tag/v<VERSION>
```

Use conventional commit prefixes as hints but write for end users.
```

## Manual Fix

1. **Review git history:**

```powershell
# Get commits since last release
git log <LAST_TAG>..HEAD --oneline

# Or use: git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

2. **Open CHANGELOG.md** and add new entry at top (after header, before previous releases)

3. **Use Keep a Changelog format:**

```markdown
## [<VERSION>] - 2025-12-07

### Breaking Changes
- **IMPORTANT**: Describe any breaking API changes
- Include migration instructions

### Added
- New feature 1: Clear description
- New feature 2: What it does and why

### Changed
- Modified behavior 1: What changed and why
- Improvement 2: Performance or UX improvement

### Fixed
- Bug fix 1: What was broken and how it's fixed
- Issue #123: Specific issue resolution

### Deprecated
- Feature X: Will be removed in next major version
- Use Feature Y instead

### Removed
- Old Feature Z: Removed as planned

### Security
- CVE-XXXX: Security vulnerability fix
```

4. **Add release link at bottom:**

```markdown
[<VERSION>]: https://github.com/yourorg/yourrepo/releases/tag/v<VERSION>
```

5. **Validate:**

```powershell
.\validate-release-notes.ps1 -Version "<VERSION>"
```

## CHANGELOG Best Practices

### Write for Users
- Describe **what changed** from user perspective
- Explain **why** it matters
- Don't just copy commit messages
- Use clear, non-technical language where possible

### Breaking Changes First
- Always list breaking changes first
- Explain impact clearly
- Provide migration guidance
- Link to migration documentation if extensive

### Group by Category
Follow Keep a Changelog categories:
1. **Breaking Changes** (if any)
2. **Added** - New features
3. **Changed** - Changes to existing functionality
4. **Fixed** - Bug fixes
5. **Deprecated** - Soon-to-be removed features
6. **Removed** - Now removed features
7. **Security** - Security improvements

### Each Entry Should
- Start with action verb (Added, Fixed, Changed, etc.)
- Be specific and clear
- Reference issues/PRs if applicable
- Highlight user impact

### Good Examples

✅ **Good**: "Added bulk import feature supporting CSV and Excel files up to 10MB"
❌ **Bad**: "feat: import stuff"

✅ **Good**: "Fixed memory leak in data processing causing crashes with large datasets"
❌ **Bad**: "fix: memory thing"

✅ **Good**: "Changed default timeout from 30s to 60s to prevent timeout errors on slow connections"
❌ **Bad**: "refactor: timeout"

## Conventional Commits Mapping

Use commit prefixes as hints:

| Commit Prefix | CHANGELOG Section |
|---------------|-------------------|
| `feat:` | **Added** |
| `fix:` | **Fixed** |
| `refactor:` | **Changed** (if user-visible) |
| `perf:` | **Changed** |
| `docs:` | Usually not in CHANGELOG |
| `style:` | Usually not in CHANGELOG |
| `test:` | Usually not in CHANGELOG |
| `chore:` | Usually not in CHANGELOG |
| `BREAKING CHANGE:` | **Breaking Changes** |

## Validation

After creating CHANGELOG entry:

```powershell
# Validate entry exists
cd cicd/scripts
.\validate-release-notes.ps1 -Version "<VERSION>"

# Full validation
.\pre-run-validation.ps1
```

## Quality Checklist

- [ ] Entry exists for `<VERSION>`
- [ ] Date is correct (YYYY-MM-DD format)
- [ ] All significant changes documented
- [ ] Breaking changes listed first (if any)
- [ ] Descriptions are user-focused and clear
- [ ] Issues/PRs referenced where applicable
- [ ] Release link added at bottom
- [ ] Follows Keep a Changelog format
- [ ] Validation passes
- [ ] Ready to tag and release

## Related Resources

- **Format Standard**: https://keepachangelog.com
- **Versioning**: https://semver.org
- **Validation**: `cicd/scripts/validate-release-notes.ps1`
- **Rules**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc`

## Success Criteria

✅ CHANGELOG entry complete
✅ All changes documented
✅ User-focused descriptions
✅ Validation passes
✅ Ready for release tag

## Related Prompts

- `generate-changelog-from-git.prompt.md` - Generate comprehensive changelog from git history
- `quick-changelog-update.prompt.md` - Quick changelog updates for minor changes
- `fix-incomplete-metadata.prompt.md` - Fix missing package metadata
- `fix-missing-documentation.prompt.md` - Fix missing XML documentation

## Related Rules

- `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Versioning and changelog standards
- `.cursor/rules/quality/zero-warnings-zero-errors-rule.mdc` - Quality enforcement

---

**Goal**: Zero Errors, Zero Warnings - Complete Release Documentation

---

**Created**: 2024-11-15 (Original prompt creation)
**Updated**: 2025-12-08 (PROMPTS-OPTIMIZE: Added Pattern metadata, Purpose, User Process, Related Prompts/Rules, Fixed frontmatter YAML)
**Rule**: `rule.prompts.creation.v1`, `rule.prompts.registry-integration.v1`
