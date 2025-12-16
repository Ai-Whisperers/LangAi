---
name: archive-obsolete-artifacts
description: "Please identify and properly archive obsolete, outdated, or superseded artifacts with redirects"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, archive, cleanup, obsolete, deprecation, maintenance
argument-hint: "Folder path to check for obsolete artifacts (e.g., .cursor/rules/)"
---

# Archive Obsolete Artifacts

Please scan for obsolete, outdated, or superseded artifacts and create proper archival process with redirects to replacements.

**Pattern**: Obsolescence Detection and Archival Pattern ⭐⭐⭐⭐
**Effectiveness**: Essential for maintaining clean, current artifact library
**Use When**: Quarterly cleanup, after major refactoring, or when noticing obsolete artifacts

---

## Purpose

Over time, artifacts become obsolete:
- **Superseded**: Replaced by better version
- **Outdated**: No longer reflects current practices
- **Deprecated**: Intentionally phased out
- **Unused**: No references, no usage
- **Consolidated**: Merged into other artifacts

Proper archival maintains history while preventing confusion from obsolete content.

## Supported Artifact Types

- **Rules** (`.cursor/rules/**/*.mdc`)
- **Prompts** (`.cursor/prompts/**/*.prompt.md`)
- **Tickets** (`tickets/**/`) - Completed tickets
- **Documentation** (`docs/**/*.md`)
- **Scripts** (`scripts/**/*.{ps1,sh,py}`)

## Expected Output

1. **Obsolescence analysis** identifying candidates for archival
2. **Archival recommendations** with reasons
3. **Redirect content** for archived artifacts
4. **Migration plan** for updating references

## Reasoning Process (for AI Agent)

Before archiving, the AI should:

1. **Identify Obsolescence**: Why is this artifact obsolete? (superseded, outdated, deprecated, unused, experimental)
2. **Check Usage**: Is it still referenced or used? Run grep to find references
3. **Find Replacement**: What replaces this artifact? Does replacement cover same use cases?
4. **Assess Impact**: What breaks if we archive it? How many active references?
5. **Choose Strategy**: Which archival strategy fits? (redirect, context-only, deprecate-first, merge, delete)
6. **Plan Migration**: How to update references? What's the migration timeline?
7. **Validate**: Does this genuinely warrant archival or should it stay active?

---

## Process

Follow these steps to archive obsolete artifacts:

### Step 1: Identify Obsolete Artifacts

Analyze `[FOLDER_PATH]` for artifacts that are:

**Superseded** (replaced by better version):
- [ ] Newer version exists (v1 → v2)
- [ ] Similar artifact with improvements exists
- [ ] Merged into comprehensive artifact
- [ ] Framework evolved, artifact no longer fits

**Outdated** (no longer accurate):
- [ ] References old practices/tools
- [ ] Based on obsolete technology
- [ ] Contradicts current standards
- [ ] Last modified > 1 year ago with no usage

**Deprecated** (intentionally phased out):
- [ ] Marked as deprecated in documentation
- [ ] Replacement recommended elsewhere
- [ ] No longer maintained
- [ ] Team decided to retire

**Unused** (no active usage):
- [ ] Zero references in current codebase
- [ ] No recent access (if trackable)
- [ ] Similar alternatives exist and are used
- [ ] Created but never adopted

**Experimental** (failed experiment):
- [ ] Proof-of-concept that didn't work
- [ ] Alternative approach chosen
- [ ] Never completed
- [ ] Superseded by different solution

### Step 2: Verify Obsolescence

Before marking for archival, verify:

**Check References**:
```bash
# Search for references
grep -r "artifact-name" .cursor/
grep -r "rule-id" .cursor/
grep -r "@prompt-name" .
```

**Check Git History**:
```bash
# Check last modification
git log -- path/to/artifact

# Check usage over time
git log -S "artifact-name" --oneline
```

**Check Usage Patterns**:
- [ ] Last referenced: [date]
- [ ] Reference count: [count]
- [ ] Active users: [count]
- [ ] Ticket references: [count]

**Verify Replacement Exists**:
- [ ] Replacement artifact identified
- [ ] Replacement covers same use cases
- [ ] Replacement is better quality
- [ ] Replacement is documented

### Step 3: Categorize by Archival Strategy

**Strategy 1: Archive with Redirect**
- Use when: Artifact has clear replacement
- Action: Move to archive/, add redirect document
- Benefit: Preserves history, guides to replacement

**Strategy 2: Archive with Context**
- Use when: No direct replacement but historical value
- Action: Move to archive/, add context about why archived
- Benefit: Preserves knowledge for future reference

**Strategy 3: Deprecate First, Archive Later**
- Use when: Still in use but should be phased out
- Action: Mark as deprecated, add sunset date, then archive
- Benefit: Gradual migration reduces disruption

**Strategy 4: Merge and Archive**
- Use when: Content worth preserving in another artifact
- Action: Migrate valuable content, then archive original
- Benefit: Consolidate knowledge, reduce clutter

**Strategy 5: Delete Completely**
- Use when: Failed experiment with no value
- Action: Delete with commit message explaining why
- Benefit: Clean slate (use sparingly)

### Step 4: Create Archival Package

For each artifact to archive:

**Archive Structure**:
```
archive/
  [artifact-type]/
    [year]/
      [artifact-name]/
        original-artifact.ext
        README.md (redirect/context)
        archived-date.txt
```

**Redirect Document Template**:
```markdown
# [Artifact Name] - ARCHIVED

**Archived**: [Date]
**Reason**: [Superseded | Outdated | Deprecated | Unused | Merged]

---

## ⚠️ This Artifact is Obsolete

This [rule/prompt/doc/script] is no longer maintained and should not be used.

### Reason for Archival

[Detailed explanation of why this was archived]

### Replacement

**Use Instead**: `[path-to-replacement]`

**What Changed**:
- [Key difference 1]
- [Key difference 2]
- [Key difference 3]

### Migration Guide

If you were using this [artifact]:

1. **Update references** to point to `[replacement]`
2. **Review differences** listed above
3. **Test** that replacement works for your use case
4. **Remove** bookmarks/shortcuts to this archived artifact

### Historical Context

**Original Purpose**: [What this artifact was meant to do]

**Why It's Archived**: [What made it obsolete]

**Valuable Lessons**:
- [Lesson 1]
- [Lesson 2]

### Need Help?

If you believe this archival was a mistake or need assistance migrating:
- Review replacement: `[path]`
- Check related artifacts: [list]
- Contact: [team/owner]

---

**Original Artifact Below** (for historical reference only)

---

[Original content preserved]
```

### Step 5: Execute Archival

**For Archive with Redirect**:

1. **Create archive location**:
   ```bash
   mkdir -p archive/[type]/[year]/[artifact-name]/
   ```

2. **Move artifact**:
   ```bash
   git mv path/to/artifact archive/[type]/[year]/[artifact-name]/
   ```

3. **Create redirect**:
   - Use template above
   - Add to original location or archive folder

4. **Update references**:
   - Find all references: `grep -r "artifact-name"`
   - Update to replacement
   - Or update to point to archive (if no replacement)

5. **Commit with context**:
   ```bash
   git commit -m "Archive [artifact-name]: [reason]

   Superseded by: [replacement]
   Last used: [date]
   References updated: [count]

   Archival reason: [detailed explanation]"
   ```

**For Deprecation First**:

1. **Add deprecation notice** to artifact:
   ```markdown
   # [Artifact Name]

   > **⚠️ DEPRECATED**: This [artifact] is deprecated as of [date].
   > Use `[replacement]` instead.
   > This artifact will be archived on [sunset-date].
   ```

2. **Update all references** with deprecation warnings

3. **Set sunset date** (e.g., 3 months)

4. **After sunset date**, execute full archival

### Step 6: Verify Archival

After archiving:
- [ ] Artifact moved to archive/ folder
- [ ] Redirect document created
- [ ] All references updated or documented
- [ ] Git history preserved
- [ ] Commit message explains archival
- [ ] Team notified
- [ ] No broken links created

## Output Format

```markdown
## Obsolescence Analysis Report

### Scan Summary
**Folder Scanned**: [path]
**Artifacts Analyzed**: [count]
**Obsolete Candidates**: [count]

**Breakdown**:
- Superseded: [count]
- Outdated: [count]
- Deprecated: [count]
- Unused: [count]
- Experimental: [count]

---

## Archival Recommendations

### High Priority: Superseded Artifacts

#### 1. [Artifact Name]
**Path**: [path]
**Type**: [rule/prompt/doc/script]
**Status**: Superseded
**Last Modified**: [date]
**References**: [count]

**Reason for Archival**:
[Why this is obsolete]

**Superseded By**: `[path-to-replacement]`

**What Changed**:
- [Improvement 1]
- [Improvement 2]

**References to Update**: [count]
- [file:line]
- [file:line]

**Archival Strategy**: Archive with Redirect

**Action Plan**:
1. Create redirect document
2. Move to `archive/[type]/2025/[name]/`
3. Update [count] references to replacement
4. Commit with context

**Apply Archival?**: [YES/NO]

---

### Medium Priority: Outdated Artifacts

#### 2. [Artifact Name]
**Path**: [path]
**Status**: Outdated
**Last Modified**: [date] (18 months ago)
**References**: [count]

**Reason for Archival**:
- Based on old framework version
- Contradicts current standards
- Better alternatives exist

**Replacement**: `[path]` (covers same use cases better)

**Archival Strategy**: Deprecate First, Archive in 90 days

**Action Plan**:
1. Add deprecation notice
2. Update references with warnings
3. Set sunset date: [date]
4. Archive after sunset

**Apply Archival?**: [YES/NO]

---

### Low Priority: Unused Artifacts

[Summary table]

| Artifact | Last Modified | References | Recommendation |
|----------|--------------|-----------|----------------|
| [name] | [date] | 0 | Archive immediately |
| [name] | [date] | 2 (old tickets) | Archive with context |

---

## Archival Packages

### Package 1: [Artifact Name]

**Archive Location**: `archive/rules/2025/old-validation-rule/`

**README.md** (redirect document):
```markdown
[Full redirect content as per template]
```

**Files to Archive**:
- `old-validation-rule.mdc` (original)
- `README.md` (redirect)
- `archived-2025-12-08.txt` (metadata)

---

## Migration Impact

### References Requiring Updates

#### High Impact (active artifacts)
1. **`.cursor/rules/ticket/plan-rule.mdc`** - Line 145
   - Current: References old-validation-rule
   - Update to: new-validation-rule

2. **`.cursor/prompts/validate-ticket.prompt.md`** - Line 78
   - Current: References old-validation-rule
   - Update to: new-validation-rule

#### Low Impact (archived tickets)
- `tickets/EPP-100/progress.md` - Line 23 (historical reference, can keep)
- `tickets/EPP-105/context.md` - Line 45 (historical reference, can keep)

### Estimated Effort
**References to Update**: [count]
**Estimated Time**: [hours]
**Risk Level**: [Low/Medium/High]

---

## Archival Timeline

### Immediate (Archive Now)
- [Artifact 1] - No active usage, clear replacement
- [Artifact 2] - Experimental, never adopted

### Short-term (Deprecate, Archive in 30 days)
- [Artifact 3] - Few references, easy migration
- [Artifact 4] - Outdated, better alternatives exist

### Long-term (Deprecate, Archive in 90 days)
- [Artifact 5] - Heavily referenced, needs gradual migration
- [Artifact 6] - Part of active workflow, replacement being validated

---

---

## Quality Criteria

- [ ] All obsolete artifacts identified with clear reasons
- [ ] Replacements verified for superseded artifacts
- [ ] References counted accurately (grep results documented)
- [ ] Archival strategy appropriate for each artifact
- [ ] Redirect documents complete and helpful
- [ ] Migration plan clear with timeline
- [ ] Team aware and agrees with archival plans
- [ ] Sunset dates set (if deprecating first)
- [ ] Git history preserved
- [ ] No critical functionality lost
```

## Examples (Few-Shot)

### Example 1: Archive Superseded Rule

**Input**: Analyze `.cursor/rules/ticket/validation-rule.mdc`

**Reasoning**:
- Created in 2023, last modified 8 months ago
- Superseded by `validation-before-completion-rule.mdc` (2025)
- New version has comprehensive checklist, old one was basic
- 5 references found (3 active, 2 in archived tickets)
- Should archive with redirect

**Output**:
```markdown
## Archival Recommendation

**Artifact**: `.cursor/rules/ticket/validation-rule.mdc`
**Status**: Superseded
**Replacement**: `.cursor/rules/ticket/validation-before-completion-rule.mdc`

**Reason**:
Superseded by comprehensive validation rule with multi-level checklist,
better examples, and integration with ticket workflow.

**Archival Strategy**: Archive with Redirect

**Archive Location**: `archive/rules/2025/validation-rule/`

**Redirect Content**:
```markdown
# Ticket Validation Rule - ARCHIVED

**Archived**: 2025-12-08
**Reason**: Superseded

This rule has been replaced by a more comprehensive version.

**Use Instead**: `.cursor/rules/ticket/validation-before-completion-rule.mdc`

**What Changed**:
- Multi-level validation checklist (Critical/Standard/Quality/Best)
- Comprehensive examples added
- Integrated with ticket workflow
- Better cross-referencing

[Rest of redirect template]
```

**References to Update**: 3
1. `.cursor/rules/ticket/plan-rule.mdc:145` → Update reference
2. `.cursor/prompts/validate-ticket.prompt.md:78` → Update reference
3. `docs/ticket-workflow.md:234` → Update reference

**Apply Archival**: YES
```

### Example 2: Deprecate Then Archive

**Input**: Check `.cursor/prompts/old-test-generator.prompt.md`

**Reasoning**:
- Still has 12 active references
- Superseded by `generate-tests.prompt.md` with better quality
- Heavy usage requires gradual migration
- Should deprecate first, archive after 90 days

**Output**:
```markdown
## Archival Recommendation

**Artifact**: `.cursor/prompts/old-test-generator.prompt.md`
**Status**: Outdated but still in use
**Replacement**: `.cursor/prompts/testing/generate-tests.prompt.md`

**Archival Strategy**: Deprecate First, Archive in 90 days

**Phase 1: Deprecation (Now)**

Add to top of file:
```markdown
> **⚠️ DEPRECATED**: This prompt is deprecated as of 2025-12-08.
> Use `@generate-tests` instead for improved test generation.
> This prompt will be archived on 2026-03-08.
```

**Phase 2: Migration (30 days)**
- Update documentation to reference new prompt
- Notify team of deprecation
- Provide migration guide

**Phase 3: Archival (90 days)**
- After 2026-03-08, move to archive/
- Create redirect document
- Update remaining references

**References to Update**: 12 (can be done gradually)

**Apply Deprecation**: YES
**Archive Date**: 2026-03-08
```

### Example 3: Archive Failed Experiment

**Input**: Check `docs/experiments/new-workflow-proposal.md`

**Reasoning**:
- Experimental workflow that was tried but not adopted
- Alternative approach chosen instead
- No active references
- Historical value only
- Can archive immediately with context

**Output**:
```markdown
## Archival Recommendation

**Artifact**: `docs/experiments/new-workflow-proposal.md`
**Status**: Failed Experiment
**Replacement**: None (alternative approach taken)

**Archival Strategy**: Archive with Context

**Archive Location**: `archive/docs/2025/experiments/new-workflow-proposal/`

**Context Document**:
```markdown
# New Workflow Proposal - ARCHIVED

**Archived**: 2025-12-08
**Reason**: Experimental workflow not adopted

This document proposed an alternative ticket workflow that was
tested but ultimately not adopted by the team.

**Why Not Adopted**:
- Too complex for daily use
- Required significant tooling changes
- Alternative simpler approach worked better

**Alternative Chosen**:
Current ticket workflow (see `.cursor/rules/ticket/`)

**Historical Value**:
Preserved for reference. Some ideas from this proposal were
incorporated into the final workflow design:
- Multi-file ticket structure ✓
- Automated validation ✓
- Timeline tracking ✓

**Lessons Learned**:
- Start simple, add complexity only when needed
- Validate with team before full implementation
- Incremental improvements beat big rewrites
```

**References**: 0 (no updates needed)

**Apply Archival**: YES
```

## Detection Criteria

### Signs of Obsolescence

**Age Indicators**:
- Last modified > 1 year ago
- Created before major framework changes
- References old versions/tools
- Frontmatter has old version number

**Usage Indicators**:
- Zero references in current codebase
- Only referenced by archived tickets
- Similar artifact exists with more usage
- Comments say "see [new-artifact] instead"

**Quality Indicators**:
- Contradicts current standards
- Missing required sections
- Lower quality than alternatives
- Incomplete or abandoned

**Context Indicators**:
- Marked as "experimental" or "draft"
- Deprecation notice exists
- Superseded-by field in frontmatter
- Team consensus to retire

## Troubleshooting

### Issue: Unsure if Still Needed

**Symptom**: Artifact looks old but might still be useful

**Solution**:
1. Check references: `grep -r "artifact-name" .`
2. Ask team: "Anyone still using X?"
3. Check git history for recent access
4. If uncertain, deprecate first (don't archive immediately)

### Issue: No Clear Replacement

**Symptom**: Artifact is obsolete but no replacement exists

**Solution**:
- Archive with context (not redirect)
- Explain why obsolete and what changed
- Document lessons learned
- Note if replacement is planned

### Issue: Heavy Usage Despite Obsolescence

**Symptom**: Artifact is clearly obsolete but has 50+ references

**Solution**:
- Deprecate first with clear timeline
- Provide migration guide
- Update documentation to reference replacement
- Gradual migration over 3-6 months
- Don't rush archival if still in heavy use

### Issue: Valuable Content in Obsolete Artifact

**Symptom**: Artifact is obsolete but contains useful information

**Solution**:
- Extract valuable content first
- Merge into current artifacts
- Then archive original
- Redirect to where content moved

## Anti-Patterns

### ❌ Delete Without Archive

**Bad**: Permanently delete obsolete file

**Impact**: Lose history, context, and lessons learned

**Better**: Archive with context document

### ❌ Archive Too Aggressively

**Bad**: Archive anything not used in last month

**Impact**: Disrupt active work, lose useful artifacts

**Better**: Be selective, verify obsolescence first

### ❌ Archive Without Redirect

**Bad**: Move file, leave broken links

**Impact**: 404 errors, confused users

**Better**: Always create redirect document

### ❌ Leave Deprecated Artifacts Forever

**Bad**: Mark as deprecated but never archive

**Impact**: Clutter, confusion about which to use

**Better**: Deprecate with sunset date, then archive

## Quality Checklist

Before archiving:

- [ ] Obsolescence reason clear and documented
- [ ] Replacement identified (if superseded)
- [ ] All references found and counted
- [ ] Archival strategy appropriate
- [ ] Redirect document complete
- [ ] Migration plan clear
- [ ] Team aware and agrees
- [ ] Git history will be preserved
- [ ] No critical functionality lost

## Best Practices

### DO
- ✅ Archive with clear context
- ✅ Create redirect documents
- ✅ Preserve git history
- ✅ Update references before archiving
- ✅ Deprecate first if heavily used
- ✅ Document lessons learned
- ✅ Notify team of archival plans

### DON'T
- ❌ Delete without archiving
- ❌ Archive without checking usage
- ❌ Leave broken links
- ❌ Archive prematurely
- ❌ Lose valuable context/knowledge
- ❌ Archive silently (communicate changes)

---

## Related Prompts

- `housekeeping/consolidate-duplicates.prompt.md` - May identify candidates for archival
- `housekeeping/update-cross-references.prompt.md` - Update references after archival
- `housekeeping/extract-templar-exemplar.prompt.md` - Extract patterns before archiving

---

## Related Rules

- `.cursor/rules/rule-authoring/rule-provenance-and-versioning.mdc` - Versioning strategy

---

## Usage

**Scan for obsolete artifacts**:
```
@archive-obsolete-artifacts .cursor/rules/
@archive-obsolete-artifacts .cursor/prompts/
@archive-obsolete-artifacts docs/
```

**Check specific artifact**:
```
@archive-obsolete-artifacts .cursor/rules/old-rule.mdc
```

**Find unused artifacts**:
```
@archive-obsolete-artifacts .cursor/ --unused-only
```

**Generate archival plan**:
```
@archive-obsolete-artifacts .cursor/ --plan-only
```

## Script
- `.cursor/scripts/housekeeping/archive-obsolete-artifacts.ps1`
  - Console summary: `pwsh -File .cursor/scripts/housekeeping/archive-obsolete-artifacts.ps1 -Folder ".cursor" -AgeDays 180`
  - JSON: `pwsh -File .cursor/scripts/housekeeping/archive-obsolete-artifacts.ps1 -Folder ".cursor" -AgeDays 180 -Json`
  - PassThru object: `pwsh -File .cursor/scripts/housekeeping/archive-obsolete-artifacts.ps1 -Folder ".cursor" -AgeDays 180 -PassThru`

---

**Note**: Run quarterly to prevent accumulation of obsolete artifacts. Better to archive proactively than leave clutter.

---

**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
