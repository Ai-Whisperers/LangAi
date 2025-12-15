---
name: changelog-agent-application
description: "Please determine when and how to apply CHANGELOG generation prompts"
category: changelog
tags: changelog, automation, ci-cd, release-notes, agent-guidance
argument-hint: "User request or scenario description"
---

# CHANGELOG Agent Application Rule

Please determine when and how to apply CHANGELOG generation prompts based on user requests.

**Pattern**: Agent Decision Pattern ⭐⭐⭐⭐  
**Effectiveness**: Essential for routing CHANGELOG requests correctly  
**Use When**: User mentions CHANGELOG, release notes, or CI/CD validation failures

---

## Purpose

This prompt helps the AI agent decide:
- **When** to apply CHANGELOG generation prompts
- **Which** specific prompt to use (quick vs comprehensive)
- **How** to execute the chosen prompt automatically

Use this as meta-guidance for handling any CHANGELOG-related user request, ensuring the right prompt is applied in the right situation.

---

## Required Context

- **User Request**: What the user is asking for (explicit or implicit)
- **Current State**: Does CHANGELOG.md exist? Is it up to date?
- **Git State**: Recent tags, commits since last release
- **Situation Type**: Quick fix, comprehensive rebuild, or teaching moment

---

## Process

Follow these steps when user mentions CHANGELOG:

### Step 1: Identify Request Type
Determine what category the user's request falls into (see "When to Apply" below).

### Step 2: Choose Appropriate Prompt
Use decision tree to select quick-changelog-update or generate-changelog-from-git.

### Step 3: Gather Required Context
Check current CHANGELOG.md, git tags, recent commits.

### Step 4: Execute Selected Prompt
Apply the chosen prompt with gathered context.

### Step 5: Provide Guidance
Show next steps (commit commands, tagging order, CI/CD validation).

---

## Reasoning Process (for AI Agent)

When user mentions CHANGELOG, the AI should:

1. **Categorize Request**: What type of CHANGELOG request is this? (explicit, CI/CD failure, release prep, git analysis)
2. **Assess Scope**: Single entry or multiple? Simple or complex?
3. **Check State**: Does CHANGELOG.md exist? What's documented? What's missing?
4. **Select Prompt**: Quick update or comprehensive generation?
5. **Auto-Execute**: Gather context, run selected prompt, provide output
6. **Guide Next Steps**: Commit commands, tagging order, validation reminders

---

## When to Apply

Apply CHANGELOG generation prompts when user requests involve:

### Explicit CHANGELOG Requests
- "Update CHANGELOG"
- "Generate CHANGELOG entry"
- "Add release notes"
- "Document this release"
- "What should I put in CHANGELOG?"

### CI/CD Validation Failures
- Pipeline fails with "CHANGELOG.md missing entry for version X.Y.Z"
- Release notes validation error
- User asks "how do we make this work?" after CHANGELOG validation failure

### Release Preparation
- User creates or mentions a release tag (`release-*`, `rc-*`)
- User asks about publishing a release
- User mentions "preparing for release"
- User asks "what changed since last release?"

### Git History Analysis
- "What commits are in this release?"
- "Summarize changes since last tag"
- "What's different between rc34 and rc35?"
- "Generate release notes from git log"

---

## Which Prompt to Use

### Use `quick-changelog-update.prompt.md` when:
- **Single release entry** needed
- User wants **immediate/simple solution**
- **CI/CD pipeline failure** (quick fix needed)
- **Clear version number** provided

**Example Request**: "Generate CHANGELOG for 0.1.0-rc35"

### Use `generate-changelog-from-git.prompt.md` when:
- **Multiple releases** need documentation
- User wants **comprehensive CHANGELOG rebuild**
- **Complex consolidation** or archiving needed
- User wants to **understand the process**

**Example Request**: "Rebuild entire CHANGELOG from git history"

### Use Both (Sequential) when:
- User is **unfamiliar** with process
- **Teaching/documentation** moment
- **First time** setting up CHANGELOG
- **Complex requirements** need explanation

**Example Request**: "How do I maintain CHANGELOG going forward?"

---

## Automatic Actions

When CHANGELOG prompt is triggered, AI should automatically:

### Step 1: Check Current State
- Read existing `CHANGELOG.md` (if exists)
- Identify latest documented version
- Check git tags for undocumented releases

### Step 2: Gather Context
- Run `git log` to see commits since last release
- Identify patterns in commit messages
- Note any breaking changes or significant features

### Step 3: Generate Entry
- Categorize commits appropriately (Added, Changed, Fixed, etc.)
- Format according to Keep a Changelog standard
- Include release tag link
- Add date (use current date if today's release)

### Step 4: Validate Output
- Ensure version format matches tag format
- Verify all sections have content (remove empty sections)
- Check for duplicate information
- Ensure links are properly formatted

### Step 5: Provide Next Steps
- Show git commands to commit CHANGELOG
- Remind about tagging order (CHANGELOG first, then tag)
- Mention CI/CD validation will check for entry

---

## Examples (Few-Shot)

### Example 1: CI/CD Pipeline Failure (Quick Fix)

**User Request**:
```
Pipeline failed: "CHANGELOG.md missing entry for version 0.1.0-rc35"
How do I fix this?
```

**AI Reasoning**:
- **Category**: CI/CD Validation Failure
- **Scope**: Single release entry needed
- **Urgency**: High (pipeline blocked)
- **Selected Prompt**: quick-changelog-update.prompt.md
- **Why**: Need immediate fix, clear version number provided

**Expected AI Action**:
```markdown
## Quick Fix Required

**Situation**: Pipeline validation detected missing CHANGELOG entry for `0.1.0-rc35`

**Solution**: I'll generate the missing entry using quick-changelog-update

[AI automatically executes quick-changelog-update.prompt.md]

**Generated Entry**:
```markdown
## [0.1.0-rc35] - 2025-12-08

### Added
- XML documentation validation pipeline
- Pre-commit validation scripts

### Fixed
- Memory leak in unit conversion service
- YAML frontmatter format issues (EPP-192)

[0.1.0-rc35]: https://github.com/org/repo/releases/tag/0.1.0-rc35
```

**Next Steps**:
```bash
# 1. Commit the CHANGELOG update
git add CHANGELOG.md
git commit -m "Doc: Update CHANGELOG for 0.1.0-rc35"

# 2. Push to trigger pipeline again
git push

# Pipeline validation will now pass ✅
```
```

### Example 2: Comprehensive CHANGELOG Rebuild

**User Request**:
```
We have 10 release tags but CHANGELOG.md only has 3 entries. 
Can you rebuild it from git history?
```

**AI Reasoning**:
- **Category**: Git History Analysis + Comprehensive Request
- **Scope**: Multiple releases (10 tags, 7 missing entries)
- **Complexity**: High (needs git analysis across multiple tags)
- **Selected Prompt**: generate-changelog-from-git.prompt.md
- **Why**: Multiple releases, comprehensive rebuild needed

**Expected AI Action**:
```markdown
## Comprehensive CHANGELOG Rebuild

**Situation**: 7 releases missing from CHANGELOG (3/10 documented)

**Solution**: I'll rebuild complete CHANGELOG from git history

[AI automatically executes generate-changelog-from-git.prompt.md]

**Process**:
1. ✅ Scanned git tags: Found 10 release tags
2. ✅ Analyzed commit history between each tag
3. ✅ Categorized 247 commits across 7 missing releases
4. ✅ Generated complete CHANGELOG with all 10 releases
5. ✅ Validated format and links

**Preview** (first missing entry):
```markdown
## [0.1.0-rc28] - 2025-11-15

### Added
- Unit test coverage analysis
- Documentation pipeline setup

### Changed
- Improved commit message standards

### Fixed
- Test failures in conversion logic

[0.1.0-rc28]: https://github.com/org/repo/releases/tag/0.1.0-rc28
```

**Complete CHANGELOG**: [Shows full rebuilt CHANGELOG.md]

**Next Steps**:
```bash
# Review the generated CHANGELOG, then commit
git add CHANGELOG.md
git commit -m "Doc: Rebuild complete CHANGELOG from git history"
git push
```
```

### Example 3: First-Time Setup (Teaching Moment)

**User Request**:
```
How do I maintain CHANGELOG going forward? Never done this before.
```

**AI Reasoning**:
- **Category**: Teaching/Documentation Moment
- **Scope**: Process explanation + practical example
- **User Experience**: Unfamiliar with CHANGELOG
- **Selected Prompts**: Both (explain then demonstrate)
- **Why**: Need to teach process AND provide working example

**Expected AI Action**:
```markdown
## CHANGELOG Maintenance Guide

**I'll explain the process and set you up with a working example.**

### The Process (2 Options)

**Option 1: Quick Update (Most Common)**
When you're about to tag a release:
1. Use `quick-changelog-update.prompt.md`
2. Provide version number
3. AI generates entry from recent commits
4. Commit CHANGELOG BEFORE creating tag

**Option 2: Comprehensive Rebuild (Catch-Up)**
When you have multiple undocumented releases:
1. Use `generate-changelog-from-git.prompt.md`
2. AI analyzes all tags and commits
3. Generates complete CHANGELOG
4. Commit the rebuild

### Let's Set You Up

**Current State Analysis**:
- Last documented: 0.1.0-rc32
- Latest tag: 0.1.0-rc35
- Missing: 3 releases (rc33, rc34, rc35)

**I'll generate entries for all 3 missing releases:**

[AI executes generate-changelog-from-git for rc33-35]

[Shows generated entries]

### Going Forward

**Before each release**:
```bash
# 1. Generate CHANGELOG entry (I'll help)
@quick-changelog-update 0.1.0-rc36

# 2. Commit CHANGELOG first
git add CHANGELOG.md
git commit -m "Doc: Update CHANGELOG for 0.1.0-rc36"

# 3. THEN create release tag
git tag 0.1.0-rc36
git push --tags

# CI/CD will validate CHANGELOG entry exists ✅
```

**Need help?** Just say:
- "Update CHANGELOG for [version]" - I'll generate the entry
- "What changed since last release?" - I'll analyze git log
```
```

---

## Expected Output

```markdown
## CHANGELOG Action Required

**Request Type**: [Explicit/CI-CD/Release Prep/Git Analysis]
**Selected Prompt**: [quick-changelog-update.prompt.md | generate-changelog-from-git.prompt.md]
**Rationale**: [Why this prompt was chosen]

[AI automatically executes selected prompt]

[Generated CHANGELOG content]

**Next Steps**:
1. [Specific git commands]
2. [Validation reminders]
3. [CI/CD implications]
```

---

## Quality Criteria

- [ ] Request type correctly identified
- [ ] Appropriate prompt selected (quick vs comprehensive)
- [ ] Current CHANGELOG state checked
- [ ] Git tags and commits analyzed
- [ ] Selected prompt automatically executed
- [ ] Generated output follows Keep a Changelog format
- [ ] Next steps provided (commit commands, tagging order)
- [ ] CI/CD validation mentioned

---

## Usage

**When AI detects CHANGELOG request**:
```
[AI internally applies this rule]
→ Identifies request type
→ Selects appropriate prompt
→ Auto-executes with context
→ Provides guidance
```

**User doesn't invoke this directly** - it's automatic agent behavior.

---

## Related Prompts

- `changelog/quick-changelog-update.prompt.md` - Single release entry generation
- `changelog/generate-changelog-from-git.prompt.md` - Comprehensive CHANGELOG rebuild

---

## Related Rules

- `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Tag and release requirements
- `.cursor/rules/development-commit-message.mdc` - Commit message standards for categorization

---

## Related Scripts

- `cicd/scripts/validate-release-notes.ps1` - CI/CD CHANGELOG validation

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
