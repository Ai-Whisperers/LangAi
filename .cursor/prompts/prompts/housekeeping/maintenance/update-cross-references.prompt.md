---
name: update-cross-references
description: "Please find and fix broken links, outdated references, and cross-reference issues across artifacts"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, links, references, cross-references, maintenance, cleanup
argument-hint: "Folder path to check for broken references (e.g., .cursor/rules/ or docs/)"
---

# Update Cross-References

Please scan artifacts for broken links, outdated references, and missing cross-references, then fix or report issues found.

**Pattern**: Reference Integrity Maintenance Pattern ⭐⭐⭐⭐
**Effectiveness**: Essential for maintaining navigable, usable artifact library
**Use When**: After refactoring, quarterly maintenance, or noticing broken links

---

## Purpose

As artifacts evolve:
- Files get renamed or moved → broken links
- Rules/prompts reference old versions → outdated references
- Related artifacts exist but aren't cross-referenced → poor discoverability
- External links break → dead URLs

This prompt maintains reference integrity across the framework.

## Supported Artifact Types

- **Rules** (`.cursor/rules/**/*.mdc`)
- **Prompts** (`.cursor/prompts/**/*.prompt.md`)
- **Tickets** (`tickets/**/`)
- **Documentation** (`docs/**/*.md`)
- **Scripts** (`scripts/**/*.{ps1,sh,py}`)

## Expected Output

1. **Broken links report** with specific file:line locations
2. **Fix recommendations** or automated fixes
3. **Missing cross-reference suggestions** for discoverability
4. **External link validation** results

## Reasoning Process

Before fixing:
1. **Identify issue type**: Broken internal link? Outdated reference? Missing cross-ref?
2. **Find correct target**: Where should the link point?
3. **Assess impact**: How many artifacts affected?
4. **Determine fix**: Update link? Add redirect? Create missing cross-ref?
5. **Verify fix**: Does the corrected link work?

## Process

### Step 1: Scan for Reference Issues

Analyze `[FOLDER_PATH]` to find:

**Broken Internal Links**:
- [ ] File references pointing to non-existent files
- [ ] Section anchors linking to removed headings
- [ ] Relative paths that don't resolve
- [ ] Rule IDs that don't match actual rules

**Outdated References**:
- [ ] References to old rule/prompt versions
- [ ] Links to archived artifacts without redirect
- [ ] References using old naming conventions
- [ ] Deprecated rule IDs still in use

**Missing Cross-References**:
- [ ] Related artifacts not linked
- [ ] Rules not referencing relevant prompts
- [ ] Prompts not referencing rules they enforce
- [ ] Templars/exemplars not linked from artifacts

**External Link Issues**:
- [ ] HTTP 404 errors
- [ ] HTTPS certificate errors
- [ ] Redirect chains (multiple redirects)
- [ ] Slow/timeout links

### Step 2: Categorize by Severity

**Critical** (blocks usage):
- Broken links to primary references
- Missing links to required dependencies
- Incorrect rule ID references

**High** (reduces usability):
- Broken links in frequently-used artifacts
- Missing cross-references between related artifacts
- Outdated references to renamed files

**Medium** (minor inconvenience):
- Broken links in rarely-used sections
- External links with minor issues
- Missing "see also" references

**Low** (cosmetic):
- Formatting inconsistencies in links
- Redundant cross-references
- Link order could be improved

### Step 3: Determine Fix Strategy

**Strategy 1: Direct Fix**
- Use when: Target is clear, single artifact affected
- Action: Update link to correct path
- Benefit: Immediate resolution

**Strategy 2: Batch Fix**
- Use when: Same issue affects many artifacts
- Action: Bulk search/replace with validation
- Benefit: Efficient resolution at scale

**Strategy 3: Create Redirect**
- Use when: Many artifacts link to moved/renamed file
- Action: Keep old path with redirect note
- Benefit: Avoid breaking existing references

**Strategy 4: Add Missing Cross-Reference**
- Use when: Related artifacts should be linked
- Action: Add "Related" sections to both
- Benefit: Improved discoverability

**Strategy 5: Archive and Redirect**
- Use when: Referenced artifact is obsolete
- Action: Archive with clear redirect to replacement
- Benefit: Clean up while preserving references

### Step 4: Execute Fixes

For **Broken Internal Links**:

1. **Identify correct target**:
   - Search for file in new location
   - Check archive/ for moved artifacts
   - Verify file actually exists

2. **Update reference**:
   ```markdown
   # Before
   See `.cursor/rules/old-location/rule.mdc`

   # After
   See `.cursor/rules/new-location/rule.mdc`
   ```

3. **Verify link works**:
   - File exists at new path
   - Section anchor exists (if linking to heading)
   - Relative path resolves correctly

For **Missing Cross-References**:

1. **Find related artifacts**:
   - Same domain/category
   - References same concepts
   - Used in similar workflows

2. **Add bidirectional links**:
   ```markdown
   ## Related Rules
   - `rule.domain.specific-topic.v1` - [Brief description]

   ## Related Prompts
   - `@prompt-name` - [Brief description]
   ```

3. **Update both artifacts**:
   - Add reference in artifact A to B
   - Add reference in artifact B to A

For **External Links**:

1. **Validate link**:
   - Check if URL responds (200 OK)
   - Verify content still relevant
   - Check for permanent redirects

2. **Fix or replace**:
   ```markdown
   # If moved
   Update to new URL

   # If dead
   Replace with web.archive.org link or alternative source

   # If obsolete
   Remove or replace with current reference
   ```

### Step 5: Verify Fixes

After updating:
- [ ] All fixed links resolve correctly
- [ ] Cross-references are bidirectional
- [ ] No new broken links introduced
- [ ] External links return 200 OK
- [ ] Changes committed and pushed

## Output Format

```markdown
## Cross-Reference Health Report

### Scan Summary
**Folder Scanned**: [path]
**Artifacts Analyzed**: [count]
**Issues Found**: [count]

**Breakdown**:
- Critical: [count]
- High: [count]
- Medium: [count]
- Low: [count]

---

## Critical Issues (Must Fix)

### Issue 1: Broken Primary Reference
**Artifact**: [path]
**Line**: [line number]
**Issue**: Link to `[target]` - File not found

**Current Reference**:
```
[Link text](old/path/to/file.mdc)
```

**Fix Recommendation**:
```
[Link text](new/path/to/file.mdc)
```

**Reason**: File moved from `old/path/` to `new/path/` on [date]

**Apply Fix?**: [YES/NO]

---

### Issue 2: Missing Required Cross-Reference
**Artifact**: [path]
**Issue**: Rule references prompt but prompt doesn't reference rule back

**Recommendation**: Add to [prompt-file.prompt.md]:
```markdown
## Related Rules

- `.cursor/rules/domain/rule-name.mdc` - [Brief description]
```

**Apply Fix?**: [YES/NO]

---

## High Priority Issues

[Repeat structure for high-priority items]

---

## Medium Priority Issues

[Summary table format]

| Artifact | Line | Issue | Fix | Auto-Fix? |
|----------|------|-------|-----|-----------|
| [path] | [line] | [description] | [fix] | [YES/NO] |

---

## Low Priority Issues

[Brief list]

---

## Missing Cross-Reference Suggestions

### Suggestion 1: Link Related Rules

**Artifacts**:
- `.cursor/rules/ticket/plan-rule.mdc`
- `.cursor/rules/ticket/context-rule.mdc`

**Rationale**: Both part of ticket workflow, should reference each other

**Recommended Addition to plan-rule.mdc**:
```markdown
## Related Rules
- `rule.ticket.context.v1` - Maintains current technical state and focus areas
```

**Recommended Addition to context-rule.mdc**:
```markdown
## Related Rules
- `rule.ticket.plan.v1` - Defines ticket objectives and implementation strategy
```

---

## External Link Validation

### Working Links ✅
- [count] links responding correctly

### Broken Links ❌
| Artifact | Link | Status | Recommendation |
|----------|------|--------|----------------|
| [path] | [URL] | 404 | Replace with [alternative] |
| [path] | [URL] | Timeout | Remove or replace |

### Redirected Links ⚠️
| Artifact | Old URL | New URL | Action |
|----------|---------|---------|--------|
| [path] | [old] | [new] | Update to new URL |

---

## Automated Fixes Applied

[If auto-fix enabled]

### Files Modified: [count]

1. **[file-path]**
   - Line [X]: Updated `[old]` → `[new]`
   - Line [Y]: Added cross-reference to `[target]`

2. **[file-path]**
   [Repeat]

---

## Manual Fixes Required

### Fix 1: Ambiguous Reference
**File**: [path]
**Line**: [line]
**Issue**: Reference to "validation rule" but multiple validation rules exist

**Action Required**: Specify which validation rule:
- `rule.ticket.validation-before-completion.v1`
- `rule.quality.validate-code-quality.v1`
- `rule.documentation.validate-xml-docs.v1`

### Fix 2: External Link Requires Review
**File**: [path]
**Link**: [URL]
**Issue**: Content changed significantly since last check

**Action Required**: Review link and either:
- Confirm still relevant
- Update to better source
- Remove if obsolete

---

## Verification Checklist

- [ ] All critical issues fixed
- [ ] High-priority issues addressed
- [ ] Broken links resolved
- [ ] Missing cross-references added
- [ ] External links validated
- [ ] Changes tested (links work)
- [ ] Changes committed
- [ ] No new issues introduced
```

## Examples (Few-Shot)

### Example 1: Fix Broken Internal Link

**Input**: Scan `.cursor/rules/ticket/`

**Reasoning**:
- Found reference to `.cursor/rules/ticket/timeline-rule.mdc`
- File was renamed to `timeline-tracking-rule.mdc`
- Link is broken
- Simple fix: update path

**Output**:
```markdown
## Critical Issue: Broken Reference

**Artifact**: `.cursor/rules/ticket/plan-rule.mdc`
**Line**: 145
**Issue**: Reference to non-existent file

**Current**:
```
See `.cursor/rules/ticket/timeline-rule.mdc` for timestamp tracking
```

**Fix**:
```
See `.cursor/rules/ticket/timeline-tracking-rule.mdc` for timestamp tracking
```

**Apply Fix**: YES (auto-fixable)
```

### Example 2: Add Missing Cross-References

**Input**: Analyze `.cursor/rules/prompts/` and `.cursor/prompts/`

**Reasoning**:
- Rule `prompt-creation-rule.mdc` defines prompt standards
- Prompt `extract-prompts-from-conversation.prompt.md` implements those standards
- Should cross-reference each other but don't
- Add bidirectional links

**Output**:
```markdown
## Missing Cross-Reference Suggestion

**Artifacts**:
- `.cursor/rules/prompts/prompt-creation-rule.mdc`
- `.cursor/prompts/rule-authoring/extract-prompts-from-conversation.prompt.md`

**Rationale**: Rule defines standards, prompt implements them

**Add to prompt-creation-rule.mdc**:
```markdown
## Related Prompts
- `@extract-prompts-from-conversation` - Extracts reusable prompts from transcripts following these standards
```

**Add to extract-prompts-from-conversation.prompt.md**:
```markdown
## Related Rules
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Defines prompt quality standards applied during extraction
```

**Apply Fix**: YES
```

### Example 3: Fix External Link

**Input**: Check external links in `docs/technical/`

**Reasoning**:
- Link to Microsoft docs returns 404
- Page moved to new URL
- Update to new location

**Output**:
```markdown
## External Link Issue

**Artifact**: `docs/technical/entity-relationship.md`
**Line**: 78
**Status**: 404 Not Found

**Current Link**:
```
https://docs.microsoft.com/en-us/dotnet/csharp/old-path
```

**New URL** (verified working):
```
https://learn.microsoft.com/en-us/dotnet/csharp/new-path
```

**Apply Fix**: YES
```

## Detection Patterns

### Broken Internal Links

**Pattern 1: File Not Found**
```regex
\[.*\]\((\.cursor/rules/.*\.mdc)\)
# Check if file exists at path
```

**Pattern 2: Broken Section Anchor**
```regex
\[.*\]\(.*\.md#section-name\)
# Check if heading exists in target file
```

**Pattern 3: Incorrect Rule ID**
```regex
`rule\.[a-z]+\.[a-z-]+\.v\d+`
# Verify rule ID exists in frontmatter
```

### Missing Cross-References

**Pattern 1: Related Rules in Same Domain**
- Rules in same folder
- Rules referencing same concepts
- Rules in same workflow chain

**Pattern 2: Rule-Prompt Pairs**
- Rule defines standard
- Prompt implements standard
- Should cross-reference

**Pattern 3: Templar-Usage Pairs**
- Templar exists
- Artifact uses pattern
- Should reference templar

## Troubleshooting

### Issue: Can't Find Correct Target

**Symptom**: Broken link but can't determine where file moved

**Solution**:
1. Search entire `.cursor/` for filename
2. Check git history: `git log --all --full-history -- path/to/file`
3. Check archive/ folders
4. Ask team if file was intentionally removed
5. If truly gone, link to related alternative

### Issue: Too Many Broken Links to Fix Manually

**Symptom**: 100+ broken references after refactor

**Solution**:
- Use batch search/replace tools
- Script the fixes (PowerShell/Python)
- Apply fixes in stages with verification
- Use `@consolidate-duplicates` first to reduce duplicates

### Issue: Circular References

**Symptom**: Artifact A references B, B references C, C references A

**Solution**:
- Circular references are OK if intentional
- Ensure each provides unique value
- Add note explaining relationship
- Don't try to force hierarchy if naturally circular

### Issue: External Link Sometimes Works

**Symptom**: External link intermittently fails

**Solution**:
- Check if server is rate-limiting
- Verify URL is correct (typos?)
- Test from different network
- If unreliable, replace with stable alternative

## Anti-Patterns

### ❌ Break Links While "Fixing" Them

**Bad**: Update link without verifying target exists

**Impact**: Replace one broken link with another broken link

**Better**: Verify target exists before updating

### ❌ Remove Cross-References to "Simplify"

**Bad**: Remove "see also" links to reduce file size

**Impact**: Reduces discoverability, users miss related content

**Better**: Keep valuable cross-references even if many

### ❌ Use Absolute Paths

**Bad**: `https://github.com/org/repo/blob/main/.cursor/rules/file.mdc`

**Impact**: Breaks when repo moves or branch changes

**Better**: Use relative paths from workspace root

### ❌ Ignore External Link Issues

**Bad**: "External links aren't our problem"

**Impact**: Users get 404s, lose trust in documentation

**Better**: Keep external links current or replace with stable alternatives

## Quality Checklist

Before completing:

- [ ] All broken internal links fixed or reported
- [ ] Missing cross-references added
- [ ] External links validated
- [ ] Fixes verified (links actually work)
- [ ] No new broken links introduced
- [ ] Bidirectional cross-references maintained
- [ ] Changes documented
- [ ] Team notified of major changes

## Best Practices

### DO
- ✅ Check references after moving/renaming files
- ✅ Add bidirectional cross-references
- ✅ Verify links before committing
- ✅ Use relative paths from workspace root
- ✅ Keep external links current
- ✅ Add redirects when moving high-traffic files

### DON'T
- ❌ Break links during refactoring
- ❌ Remove cross-references without reason
- ❌ Use absolute file:// or http://localhost links
- ❌ Ignore external link rot
- ❌ Create one-way references (add return reference too)

---

## Related Prompts

- `housekeeping/consolidate-duplicates.prompt.md` - Run first to reduce duplicate references
- `housekeeping/archive-obsolete-artifacts.prompt.md` - Creates proper redirects in archived files
- `housekeeping/sync-improvements.prompt.md` - May introduce references needing updates

---

## Related Rules

- `.cursor/rules/rule-authoring/rule-cross-references.mdc` - Cross-reference standards

## Usage

**Scan specific folder**:
```
@update-cross-references .cursor/rules/ticket/
@update-cross-references .cursor/prompts/
@update-cross-references docs/
```

**Check all references**:
```
@update-cross-references .cursor/ --full-scan
```

**Fix specific artifact**:
```
@update-cross-references .cursor/rules/ticket/plan-rule.mdc --fix
```

**Validate external links only**:
```
@update-cross-references docs/ --external-only
```

## Script
- `.cursor/scripts/housekeeping/update-cross-references.ps1`
  - Console summary: `pwsh -File .cursor/scripts/housekeeping/update-cross-references.ps1 -Folder ".cursor/rules"`
  - JSON: `pwsh -File .cursor/scripts/housekeeping/update-cross-references.ps1 -Folder ".cursor/rules" -Json`
  - PassThru object: `pwsh -File .cursor/scripts/housekeeping/update-cross-references.ps1 -Folder ".cursor/rules" -PassThru`

---

**Note**: Run after refactoring, renaming, or moving files. Also run quarterly to catch external link rot.

---

**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
