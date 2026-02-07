---
name: generate-changelog-from-git
description: "Please analyze git history between releases and generate CHANGELOG entries"
category: changelog
tags: changelog, git, release-notes, automation, semantic-versioning
argument-hint: "Version number or 'auto' for automatic detection"
---

# Generate CHANGELOG from Git History

Please analyze git commit history between release tags and generate accurate CHANGELOG.md entries following Keep a Changelog format.

**Pattern**: Git History Analysis Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for comprehensive CHANGELOG generation
**Use When**: Multiple releases need documentation, CHANGELOG rebuild, or catching up on undocumented releases

---

## Purpose

Analyze git commit history between release tags and generate accurate, well-structured CHANGELOG.md entries following Keep a Changelog format.

**Build Optimization Strategy**:
- **Old workflow**: Merge→Build #1, Changelog→Build #2, Tag RC (2 builds)
- **New workflow**: Merge→Changelog→Build #1, Tag RC (1 build)
- **Timing**: Run AFTER merging to release branch but BEFORE tagging RC
- **Result**: Single build trigger instead of multiple, optimizing CI/CD

---

## Required Context

- **Git Repository**: With tagged releases (`release-*`, `rc-*`, etc.)
- **Release Branch**: On `release/X.Y` branch (for automatic version detection) or provide version
- **Commit History**: Conventional commits preferred but not required
- **Existing CHANGELOG**: CHANGELOG.md file exists with structure

---

## Process

Follow these steps to generate CHANGELOG from git:

### Step 1: Detect Version (Automatic or Manual)
If on release branch, auto-detect version; otherwise use provided version.

### Step 2: Analyze Git Tags
List all release tags and identify last documented version.

### Step 3: Extract Commit History
Get commits since last release tag with details.

### Step 4: Categorize Commits
Sort commits into Added, Changed, Fixed, Breaking Changes, etc.

### Step 5: Generate CHANGELOG Entry
Format entries following Keep a Changelog standard and **always include** the mandatory sections `### Added`, `### Changed`, and `### Fixed` (use `- None` if no items). Include `### Breaking Changes`, `### Deprecated`, `### Removed`, and `### Security` only when there is content.

### Step 6: Validate and Finalize
Ensure format correct, links valid, and mandatory sections present. Verify Markdown renders cleanly and that comparison links and tag links are valid.

---

## Reasoning Process (for AI Agent)

Before generating CHANGELOG, the AI should:

1. **Detect Context**: Am I on a release branch? What's the current branch name?
2. **Extract Version**: Can I auto-detect version from branch? Or was version provided?
3. **Find Last Release**: What's the last documented release in CHANGELOG? What tags exist?
4. **Analyze History**: What commits exist between last release and HEAD?
5. **Categorize**: Which category does each commit belong to? (Added, Changed, Fixed, Breaking)
6. **Format**: How should this be structured per Keep a Changelog?
7. **Validate**: Are all sections populated? Are links correct? Format valid?

---

## Automatic Version Detection (Release Branch Context)

### Context
This prompt is typically run on a `release/X.Y` branch after merging from develop, but BEFORE tagging any RCs.

### Automatic Version Extraction

```bash
# 1. Detect current release branch
RELEASE_BRANCH=$(git rev-parse --abbrev-ref HEAD)
# Example: release/0.1, release/1.2, release/2.0

# 2. Extract MAJOR.MINOR from branch name
MAJOR_MINOR=$(echo $RELEASE_BRANCH | sed 's/release\///')
# Example: 0.1, 1.2, 2.0

# 3. Get last release version from tags
LAST_RELEASE=$(git tag -l "release-*" --sort=-version:refname | head -1)
# Example: release-0.1.0-rc34, release-1.2.5, release-2.0.0

# 4. Determine new PATCH version
# - If last release is on same MAJOR.MINOR → increment patch
# - If last release is on different MAJOR.MINOR → start at .0
```

**AI Task**: Based on release branch and last release tag:
- **Last Release Version**: Extract from `LAST_RELEASE` tag
- **New Version**: Apply semantic versioning rules based on branch name
- **Version Type**: Major bump, minor bump, patch bump, or RC finalization

---

## Git Commands for Analysis

### List All Release Tags
```bash
# Chronologically ordered tags
git tag -l "release-*" "rc-*" --sort=version:refname
```

### Get Commits Since Last Release
```bash
# Detailed commit history
git log <last-release-tag>..HEAD --pretty=format:"%h|%ad|%s|%b" --date=short
```

### Check Current Branch
```bash
# For automatic version detection
git rev-parse --abbrev-ref HEAD
```

---

## Commit Categorization Patterns

### Added (New Features)
- `feat:`, `feature:` commits
- New classes, methods, or significant functionality
- New capabilities or APIs

### Changed (Modifications)
- `refactor:`, `chore:`, `perf:` commits
- Performance improvements
- Internal restructuring
- Updates to existing functionality

### Fixed (Bug Fixes)
- `fix:`, `bugfix:` commits
- Error corrections
- Bug resolutions

### Breaking Changes (API Changes)
- Commits with `BREAKING CHANGE:` in body
- API signature changes
- Removed functionality
- Changed behavior of existing features

### Removed (Deprecations)
- `remove:`, `deprecate:` commits
- Deleted features or APIs

### Security (Vulnerabilities)
- `security:` commits
- Security patches
- Vulnerability fixes

---

## CHANGELOG Entry Format

```markdown
## [X.Y.Z-rcN] - YYYY-MM-DD

**Release Tag**: [release-X.Y.Z-rcN](repository-url/releases/tag/release-X.Y.Z-rcN)

**NuGet Package**: `Eneve.Domain.*.X.Y.Z-rcN`

### Added
- **Feature Name**: Brief description of new functionality
- **Component**: What was added

### Changed
- **Component Name**: Description of what changed and why
- **Performance**: Improvements made

### Fixed
- **Bug Description**: What was broken and how it's fixed
- **Issue**: Resolution details

### Breaking Changes
- **API Change**: Clear description and migration path
- **Behavior Change**: What changed and how to adapt

### Security
- **Vulnerability**: What was fixed (if applicable)

[X.Y.Z-rcN]: repository-url/compare/previous-tag...release-X.Y.Z-rcN
```

---

## Examples (Few-Shot)

### Example 1: Single Release Generation (Automatic Version)

**User Input**:
```
Generate CHANGELOG for current release
[Currently on branch: release/0.1]
```

**AI Reasoning**:
- **Branch Detected**: release/0.1
- **MAJOR.MINOR**: 0.1
- **Last Tag**: release-0.1.0-rc34
- **New Version**: 0.1.0-rc35 (increment RC)
- **Commits**: 15 commits since rc34
- **Categories**: 5 Added, 7 Fixed, 2 Changed, 1 Breaking

**Expected Output**:
```markdown
## CHANGELOG Entry Generated

**Auto-Detected Version**: 0.1.0-rc35 (from release/0.1 branch + last tag analysis)

**Analysis**:
- Last Release: 0.1.0-rc34 (2025-11-28)
- Commits Since: 15
- Date Range: 2025-11-29 to 2025-12-08

**Generated Entry**:

---
## [0.1.0-rc35] - 2025-12-08

**Release Tag**: [release-0.1.0-rc35](https://github.com/org/repo/releases/tag/release-0.1.0-rc35)

**NuGet Package**: `Eneve.Domain.*.0.1.0-rc35`

### Added
- **XML Documentation Pipeline**: Automated validation for public APIs
- **Pre-commit Validation**: Local quality checks before push
- **Documentation Standards**: Comprehensive XML doc requirements
- **Quality Criteria**: Checklists for completion validation
- **Unit Test Discipline**: Strict test maintenance rules

### Changed
- **Prompt Format**: Migrated all prompts to `.prompt.md` registry format
- **YAML Frontmatter**: Removed JSON arrays per EPP-192 standards

### Fixed
- **Memory Leak**: Fixed conversion service memory leak in unit calculations
- **YAML Parsing**: Resolved frontmatter parsing errors
- **Test Failures**: Corrected 3 failing unit tests in conversion logic
- **Null Reference**: Fixed null handling in measurement service
- **CI/CD Pipeline**: Resolved CHANGELOG validation failures
- **Documentation**: Fixed broken links in technical specs
- **Build Warnings**: Eliminated 12 compiler warnings

### Breaking Changes
- **YAML Format**: JSON array syntax no longer supported in frontmatter (use YAML lists)
  - **Migration**: Convert `tags: ["a", "b"]` to `tags: a, b, c`

[0.1.0-rc35]: https://github.com/org/repo/compare/release-0.1.0-rc34...release-0.1.0-rc35

---

**Next Steps**:
```bash
# 1. Review generated entry and adjust if needed

# 2. Insert into CHANGELOG.md at top (below ## [Unreleased])

# 3. Commit CHANGELOG (BEFORE tagging)
git add CHANGELOG.md
git commit -m "Doc: Update CHANGELOG for 0.1.0-rc35"

# 4. THEN create release tag
git tag release-0.1.0-rc35
git push origin release/0.1 --tags

# CI/CD will validate CHANGELOG entry exists ✅
```
```

### Example 2: Multiple Missing Releases (Catch-Up)

**User Input**:
```
Rebuild CHANGELOG - we have 7 undocumented releases
Tags: rc28 through rc34 are missing
```

**AI Reasoning**:
- **Scope**: Multiple releases (7 missing entries)
- **Last Documented**: 0.1.0-rc27
- **Latest Tag**: 0.1.0-rc34
- **Gap**: rc28, rc29, rc30, rc31, rc32, rc33, rc34
- **Complexity**: Need to analyze 7 tag pairs

**Expected Output**:
```markdown
## Comprehensive CHANGELOG Rebuild

**Gap Identified**: 7 undocumented releases between rc27 and rc34

**Analysis Summary**:
| Release | Date | Commits | Categories |
|---------|------|---------|------------|
| rc28 | 2025-11-15 | 12 | 4 Added, 6 Fixed, 2 Changed |
| rc29 | 2025-11-18 | 8 | 2 Added, 5 Fixed, 1 Changed |
| rc30 | 2025-11-21 | 15 | 6 Added, 7 Fixed, 2 Breaking |
| rc31 | 2025-11-24 | 10 | 3 Added, 6 Fixed, 1 Changed |
| rc32 | 2025-11-26 | 9 | 2 Added, 5 Fixed, 2 Changed |
| rc33 | 2025-11-28 | 11 | 4 Added, 6 Fixed, 1 Changed |
| rc34 | 2025-11-30 | 14 | 5 Added, 7 Fixed, 2 Changed |

**Total**: 79 commits categorized across 7 releases

**Generated CHANGELOG** (all 7 entries):

---
## [0.1.0-rc34] - 2025-11-30

[Full entry for rc34...]

---
## [0.1.0-rc33] - 2025-11-28

[Full entry for rc33...]

---
[Entries for rc32, rc31, rc30, rc29, rc28...]

---

**Insertion Point**: Insert ALL 7 entries after rc27 in CHANGELOG.md

**Next Steps**:
```bash
# 1. Review all 7 generated entries

# 2. Insert into CHANGELOG.md in chronological order

# 3. Commit the comprehensive update
git add CHANGELOG.md
git commit -m "Doc: Rebuild CHANGELOG for rc28-rc34 (7 missing releases)"
git push

# CHANGELOG is now complete and up to date ✅
```
```

---

## Expected Output

```markdown
## CHANGELOG Generation Complete

**Version**: [Auto-detected or provided version]
**Commits Analyzed**: [Count]
**Categories**: [Added: N, Changed: N, Fixed: N, Breaking: N]

**Generated Entry**:
[Complete CHANGELOG.md entry in Keep a Changelog format]

**Next Steps**:
1. Review generated entry
2. Insert into CHANGELOG.md at appropriate position
3. Commit CHANGELOG BEFORE tagging
4. Create release tag
5. Push to trigger CI/CD validation
```

---

## Quality Criteria

- [ ] Version correctly detected or provided
- [ ] All commits since last release analyzed
- [ ] Commits categorized appropriately (Added, Changed, Fixed, Breaking)
- [ ] Mandatory sections present: Added, Changed, Fixed (use `- None` if empty)
- [ ] Optional sections (Breaking Changes, Deprecated, Removed, Security) included only when applicable
- [ ] Entry follows Keep a Changelog format
- [ ] Release tag link included and correct
- [ ] NuGet package version matches
- [ ] Date is current (YYYY-MM-DD)
- [ ] No missing or blank mandatory sections
- [ ] Comparison link generated correctly
- [ ] Next steps provided (commit before tag)

---

## Usage

**Automatic version detection** (on release branch):
```
@generate-changelog-from-git
```

**Specific version**:
```
@generate-changelog-from-git 0.1.0-rc35
```

**Multiple releases catch-up**:
```
@generate-changelog-from-git --rebuild-all
```

---

## Related Prompts

- `changelog/quick-changelog-update.prompt.md` - Quick single-release entry
- `changelog/agent-application-rule.prompt.md` - Determines when to use this prompt

---

## Related Rules

- `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Tag and versioning requirements
- `.cursor/rules/development-commit-message.mdc` - Commit message standards

---

## Related Documentation

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) - CHANGELOG format standard
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message convention
- [Semantic Versioning](https://semver.org/) - Versioning rules

---

**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
**Changelog**: Added automatic version detection from release branch to optimize CI/CD workflow
