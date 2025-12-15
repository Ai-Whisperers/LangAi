---
name: quick-changelog-update
description: "Please quickly generate a CHANGELOG entry for the current release"
category: changelog
tags: changelog, quick-update, release-notes, single-entry
argument-hint: "Version number (e.g., 0.1.0-rc35)"
---

# Quick CHANGELOG Update

Please quickly generate a CHANGELOG entry for a single release by analyzing recent commits.

**Pattern**: Quick Single-Entry Pattern ⭐⭐⭐⭐  
**Effectiveness**: Essential for fast CHANGELOG updates  
**Use When**: Single release needs documentation, CI/CD failure, or quick fix needed

---

## Purpose

Generate a single CHANGELOG entry quickly by analyzing git commits since last release. This is the fast path for:
- **CI/CD failures**: Pipeline blocked due to missing CHANGELOG entry
- **Single release**: Just need current release documented
- **Time-sensitive**: Need immediate fix without comprehensive analysis
- **Clear version**: Version number known and provided

For multiple releases or comprehensive rebuilds, use `generate-changelog-from-git.prompt.md` instead.

---

## Required Context

- **Version Number**: Release version to document (e.g., 0.1.0-rc35)
- **Last Release Tag**: Previous release tag to compare against
- **Git History**: Commits between last release and HEAD
- **Today's Date**: For CHANGELOG entry timestamp

---

## Process

Follow these steps for quick CHANGELOG update:

### Step 1: Identify Version
Get version number from user or detect from context.

### Step 2: Find Last Release
Identify previous release tag for comparison.

### Step 3: Extract Recent Commits
Run git log to get commits since last release.

### Step 4: Categorize Commits
Quick categorization: Added, Changed, Fixed, Breaking.

### Step 5: Generate Entry
Format as CHANGELOG entry with today's date.

### Step 6: Provide Next Steps
Show commit command and tagging order.

---

## Reasoning Process (for AI Agent)

When generating quick CHANGELOG entry, the AI should:

1. **Verify Version**: Is version provided? Format correct? (X.Y.Z or X.Y.Z-rcN)
2. **Find Last Tag**: What's the previous release to compare against?
3. **Extract Commits**: What commits exist between last tag and HEAD?
4. **Quick Categorize**: Fast sort into Added/Changed/Fixed/Breaking (don't overthink)
5. **Format**: Follow Keep a Changelog format with links
6. **Validate**: Date correct? Links valid? Format proper?
7. **Guide**: Provide commit-before-tag workflow

---

## Quick Use

**"I need a CHANGELOG entry for my current release candidate"**

### Quick Command to See Commits
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Then Request
```
Generate CHANGELOG entry for version X.Y.Z-rcN based on these commits
```

---

## Common Scenarios

### Scenario 1: New RC After Previous RC
**Use Case**: Incremental RC release

```
Generate CHANGELOG.md entry for version 0.1.0-rc35 by analyzing 
commits between release-0.1.0-rc34 and current HEAD.
```

### Scenario 2: CI/CD Pipeline Failure
**Use Case**: Missing CHANGELOG entry blocking pipeline

```
Pipeline failed: "CHANGELOG.md missing entry for 0.1.0-rc35"
Generate the missing entry quickly.
```

### Scenario 3: Multiple RCs to Consolidate
**Use Case**: Consolidate several test releases into one entry

```
Generate CHANGELOG.md entry that consolidates releases 
0.1.0-rc30 through 0.1.0-rc34 into a single entry for 0.1.0-rc35.

Focus on user-facing changes, skip internal test iterations.
```

### Scenario 4: First GA Release
**Use Case**: Summarize all RCs into GA release entry

```
Generate CHANGELOG.md entry for version 0.1.0 (GA release) that 
summarizes all RC releases from 0.1.0-rc1 to 0.1.0-rc35.

Create "Archived Releases" section for early experimental RCs.
```

---

## Examples (Few-Shot)

### Example 1: Quick Single RC Entry (CI/CD Fix)

**User Input**:
```
Pipeline failed - need CHANGELOG for 0.1.0-rc35 ASAP
Last release was rc34
```

**AI Reasoning**:
- **Scenario**: CI/CD pipeline failure (urgent)
- **Version**: 0.1.0-rc35 (provided)
- **Last Tag**: release-0.1.0-rc34
- **Commits**: Run git log between tags
- **Speed**: Fast categorization, no deep analysis
- **Output**: Single entry, ready to commit

**Expected Output**:
```markdown
## Quick CHANGELOG Entry Generated

**Version**: 0.1.0-rc35
**Commits Since rc34**: 12 commits
**Analysis Time**: ~30 seconds

**Generated Entry**:

---
## [0.1.0-rc35] - 2025-12-08

**Release Tag**: [release-0.1.0-rc35](https://github.com/org/repo/releases/tag/release-0.1.0-rc35)

**NuGet Package**: `Eneve.Domain.*.0.1.0-rc35`

### Added
- Pre-commit validation scripts
- Documentation quality checks

### Changed
- Prompt format migration to `.prompt.md`
- YAML frontmatter standardization

### Fixed
- Memory leak in unit conversion service
- YAML parsing errors (EPP-192)
- CI/CD pipeline validation failures

[0.1.0-rc35]: https://github.com/org/repo/compare/release-0.1.0-rc34...release-0.1.0-rc35

---

**URGENT - Next Steps**:
```bash
# 1. Insert entry into CHANGELOG.md (at top, below Unreleased)

# 2. Commit IMMEDIATELY (unblock pipeline)
git add CHANGELOG.md
git commit -m "Doc: Add CHANGELOG entry for 0.1.0-rc35"

# 3. Push to trigger pipeline
git push

# Pipeline will now pass ✅
```
```

### Example 2: Consolidate Multiple RCs

**User Input**:
```
Generate entry for 0.1.0-rc35 consolidating rc30-rc34
Too many internal test releases, need clean summary
```

**AI Reasoning**:
- **Scenario**: Consolidation (multiple RCs → single entry)
- **Version**: 0.1.0-rc35 (target)
- **Range**: rc30 through rc34 (5 releases)
- **Approach**: Summarize user-facing changes, skip test iterations
- **Output**: Single consolidated entry

**Expected Output**:
```markdown
## Consolidated CHANGELOG Entry

**Version**: 0.1.0-rc35 (consolidates rc30-34)
**Releases Consolidated**: 5 (rc30, rc31, rc32, rc33, rc34)
**Total Commits**: 47 commits
**Focus**: User-facing changes only

**Generated Entry**:

---
## [0.1.0-rc35] - 2025-12-08

**Release Tag**: [release-0.1.0-rc35](https://github.com/org/repo/releases/tag/release-0.1.0-rc35)

**NuGet Package**: `Eneve.Domain.*.0.1.0-rc35`

**Note**: This release consolidates internal test releases rc30-rc34

### Added
- XML documentation validation pipeline
- Unit test coverage analysis
- Pre-commit validation framework
- Documentation quality standards
- Quality criteria checklists

### Changed
- Prompt format migrated to Prompt Registry (all 100+ prompts)
- YAML frontmatter standardization (EPP-192 compliance)
- Commit message standards enhanced
- CI/CD workflow optimized

### Fixed
- Memory leak in unit conversion service
- YAML parsing errors in frontmatter
- Test failures in conversion logic (6 tests)
- CI/CD pipeline validation issues
- Documentation broken links (15 instances)

### Breaking Changes
- JSON array syntax no longer supported in YAML frontmatter
  - **Migration**: Convert `tags: ["a", "b"]` to `tags: a, b, c`

[0.1.0-rc35]: https://github.com/org/repo/compare/release-0.1.0-rc29...release-0.1.0-rc35

---

**Archived Internal Test Releases**:
- release-0.1.0-rc30 (2025-11-25) - Test iteration
- release-0.1.0-rc31 (2025-11-28) - Test iteration
- release-0.1.0-rc32 (2025-12-02) - Test iteration
- release-0.1.0-rc33 (2025-12-04) - Test iteration
- release-0.1.0-rc34 (2025-12-06) - Test iteration

---

**Next Steps**:
```bash
# 1. Review consolidated entry

# 2. Insert into CHANGELOG.md

# 3. Commit
git add CHANGELOG.md
git commit -m "Doc: Add CHANGELOG entry for 0.1.0-rc35 (consolidates rc30-rc34)"

# 4. Create tag and push
git tag release-0.1.0-rc35
git push origin --tags
```
```

---

## Output Format

```markdown
## [X.Y.Z-rcN] - YYYY-MM-DD

**Release Tag**: [release-X.Y.Z-rcN](link-to-tag)

**NuGet Package**: `Eneve.Domain.*.X.Y.Z-rcN`

### Added
- Feature description

### Changed  
- Change description

### Fixed
- Bug fix description

### Breaking Changes
- Breaking change with migration guidance

[X.Y.Z-rcN]: repository-url/compare/previous-tag...release-X.Y.Z-rcN
```

---

## Quick Commands Reference

```bash
# See all release tags
git tag -l "release-*" --sort=version:refname

# Compare two tags
git log release-0.1.0-rc34..release-0.1.0-rc35 --oneline

# Commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%h %s"

# Today's date (for CHANGELOG)
date +%Y-%m-%d                    # Linux/Mac
Get-Date -Format "yyyy-MM-dd"     # PowerShell
```

---

## Quality Criteria

- [ ] Version number provided or detected
- [ ] Last release tag identified
- [ ] Commits since last release extracted
- [ ] Commits categorized (Added, Changed, Fixed, Breaking)
- [ ] Entry follows Keep a Changelog format
- [ ] Release tag link correct
- [ ] Date is today (YYYY-MM-DD)
- [ ] Empty sections removed
- [ ] Comparison link generated
- [ ] Next steps provided (commit before tag)

---

## Usage

**Basic quick entry**:
```
@quick-changelog-update 0.1.0-rc35
```

**With explicit last tag**:
```
@quick-changelog-update 0.1.0-rc35 --since rc34
```

**CI/CD urgent fix**:
```
@quick-changelog-update 0.1.0-rc35 --urgent
```

---

## Related Prompts

- `changelog/generate-changelog-from-git.prompt.md` - Comprehensive multi-release CHANGELOG generation
- `changelog/agent-application-rule.prompt.md` - Determines when to use quick vs comprehensive

---

## Related Rules

- `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Tag requirements and CI/CD workflow
- `.cursor/rules/development-commit-message.mdc` - Commit message standards

---

## Related Documentation

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) - Format standard
- [Semantic Versioning](https://semver.org/) - Version numbering

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
