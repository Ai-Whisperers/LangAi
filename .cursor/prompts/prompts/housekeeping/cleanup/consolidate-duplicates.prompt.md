---
name: consolidate-duplicates
description: "Please find and merge duplicate or overlapping rules, prompts, and other artifacts"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, duplicates, refactoring, consolidation, cleanup
argument-hint: "Folder path to scan for duplicates (e.g., .cursor/rules/ticket/)"
---

# Consolidate Duplicate Artifacts

Please scan for duplicate or overlapping artifacts (rules, prompts, tickets, docs) and recommend consolidation strategies to eliminate redundancy and improve maintainability.

**Pattern**: Duplicate Detection and Consolidation Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Essential for maintaining single source of truth  
**Use When**: Quarterly cleanup, after major refactoring, or when noticing confusion about which artifact to use

---

## Purpose

Over time, similar artifacts get created independently:
- Rules covering same topic from different angles
- Prompts solving same problem with different approaches
- Documentation duplicating content across files
- Scripts implementing similar logic

This prompt helps identify and consolidate these duplicates to maintain single source of truth.

## Supported Artifact Types

- **Rules** (`.cursor/rules/**/*.mdc`)
- **Prompts** (`.cursor/prompts/**/*.prompt.md`)
- **Documentation** (`docs/**/*.md`)
- **Scripts** (`scripts/**/*.{ps1,sh,py}`)
- **Tickets** (less common, but can find pattern duplicates)

## Expected Output

1. **Duplicate analysis report** with similarity scores
2. **Consolidation recommendations** (merge, keep both, archive)
3. **Merged artifact** (if merge recommended)
4. **Migration plan** for updating references

## Reasoning Process

Before consolidating:
1. **Identify duplicates**: What artifacts cover similar ground?
2. **Assess overlap**: How much redundancy exists?
3. **Compare quality**: Which version is better?
4. **Check dependencies**: What references each artifact?
5. **Plan merge**: How to combine without losing value?

## Process

### Step 1: Scan for Duplicates

Analyze `[FOLDER_PATH]` to identify:

**Exact Duplicates**:
- [ ] Same title/name
- [ ] Same or very similar content
- [ ] Same purpose/scope

**Partial Duplicates**:
- [ ] Similar purpose but different approaches
- [ ] Overlapping sections (e.g., 60%+ similar)
- [ ] Same problem, different details

**Conceptual Duplicates**:
- [ ] Same domain/category
- [ ] Address same problem from different angles
- [ ] Could be merged into comprehensive artifact

### Step 2: Analyze Each Duplicate Set

For each duplicate group, assess:

**Similarity Score**:
- **90-100%**: Exact duplicates (should merge immediately)
- **70-89%**: High overlap (strong merge candidate)
- **50-69%**: Moderate overlap (evaluate carefully)
- **30-49%**: Low overlap (likely keep separate)

**Quality Comparison**:
| Aspect | Artifact A | Artifact B | Winner |
|--------|-----------|-----------|---------|
| Completeness | [score] | [score] | [A/B/Tie] |
| Clarity | [score] | [score] | [A/B/Tie] |
| Examples | [score] | [score] | [A/B/Tie] |
| Up-to-date | [score] | [score] | [A/B/Tie] |
| References | [count] | [count] | [A/B] |

**Usage Analysis**:
- Artifact A: Referenced by [count] files
- Artifact B: Referenced by [count] files
- Active usage: [A > B / B > A / Equal]

### Step 3: Determine Consolidation Strategy

**Strategy 1: Merge into Single Artifact**
- Use when: 70%+ overlap, clear winner in quality
- Action: Combine best elements, archive duplicate
- Benefit: Single source of truth

**Strategy 2: Keep Both, Differentiate**
- Use when: 50-69% overlap, serve different use cases
- Action: Clarify distinct purposes, cross-reference
- Benefit: Preserve specialized value

**Strategy 3: Create Hierarchy**
- Use when: One is general, one is specific
- Action: Make specific artifact reference general one
- Benefit: Avoid duplication while keeping specializations

**Strategy 4: Extract Common Pattern**
- Use when: Multiple artifacts share pattern
- Action: Extract to templar, have artifacts reference it
- Benefit: Share pattern, reduce duplication

**Strategy 5: Archive Obsolete**
- Use when: One artifact clearly obsolete
- Action: Archive old version, migrate references
- Benefit: Eliminate dead code

### Step 4: Execute Consolidation

For **Merge** strategy:

1. **Create merged artifact**:
   - Start with better-quality version
   - Integrate valuable elements from duplicate
   - Remove redundancy
   - Add cross-references to related artifacts
   - Update frontmatter (version, provenance)

2. **Migrate references**:
   - Find all files referencing duplicate
   - Update to reference merged artifact
   - Test that links work

3. **Archive duplicate**:
   - Move to `archive/` folder
   - Add deprecation note with redirect
   - Document merge in changelog

For **Keep Both** strategy:

1. **Clarify differentiation**:
   - Add "Related" section to each
   - Explain when to use which
   - Cross-reference for discoverability

2. **Update names** (if needed):
   - Rename to clarify distinct purposes
   - Update all references

For **Extract Pattern** strategy:

1. **Create templar/exemplar**:
   - Extract common pattern
   - Save to appropriate templars/ folder
   - Document usage

2. **Update original artifacts**:
   - Add reference to templar
   - Remove duplicated pattern content
   - Show how they customize the pattern

### Step 5: Verify No Breakage

After consolidation:
- [ ] All references updated
- [ ] No broken links
- [ ] Archived artifacts have redirects
- [ ] Documentation updated
- [ ] Team notified of changes

## Output Format

```markdown
## Duplicate Analysis Report

### Scan Summary
**Folder Scanned**: [path]
**Artifact Type**: [rules/prompts/docs/scripts]
**Total Artifacts**: [count]
**Duplicate Sets Found**: [count]

---

## Duplicate Set 1: [Topic/Name]

### Artifacts Involved
1. **[Artifact A]**: [path]
   - Purpose: [brief description]
   - Size: [lines/KB]
   - Last modified: [date]
   - Referenced by: [count] files

2. **[Artifact B]**: [path]
   - Purpose: [brief description]
   - Size: [lines/KB]
   - Last modified: [date]
   - Referenced by: [count] files

### Similarity Analysis
**Overlap Score**: [percentage]%

**Common Elements**:
- [Element 1]
- [Element 2]

**Unique to A**:
- [Element]

**Unique to B**:
- [Element]

### Quality Comparison
| Aspect | Artifact A | Artifact B | Winner |
|--------|-----------|-----------|---------|
| Completeness | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | A |
| Clarity | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | B |
| Examples | ⭐⭐⭐ | ⭐⭐⭐⭐ | B |
| Up-to-date | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | A |

**Overall**: Artifact A is better foundation (4 vs 3 categories)

### Recommendation
**Strategy**: [Merge | Keep Both | Create Hierarchy | Extract Pattern | Archive]

**Rationale**: [Why this strategy is best]

**Action Plan**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Duplicate Set 2: [Topic/Name]
[Repeat structure]

---

## Consolidation Summary

### Recommended Actions

#### High Priority (Exact Duplicates - 90%+ overlap)
1. **Merge**: [Artifact A] + [Artifact B] → [New path]
2. **Archive**: [Artifact C] (obsolete)

#### Medium Priority (High Overlap - 70-89%)
1. **Merge**: [Artifact D] + [Artifact E]
2. **Differentiate**: [Artifact F] vs [Artifact G]

#### Low Priority (Moderate Overlap - 50-69%)
1. **Keep Both**: [Artifact H] and [Artifact I] (clarify distinction)
2. **Extract Pattern**: Common pattern from [J], [K], [L]

### Migration Impact
**Files Requiring Updates**: [count]
**References to Update**: [count]
**Estimated Effort**: [hours]

### Risk Assessment
**Low Risk**: [count] merges (clear winners, few references)
**Medium Risk**: [count] merges (multiple references to update)
**High Risk**: [count] merges (heavily referenced, subtle differences)

---

## Merged Artifacts

### [Artifact Name] (Merged)

[Full content of merged artifact]

**Save to**: [path]
**Replaces**: [list of archived artifacts]
**References to update**: [count]

---

## Migration Checklist

- [ ] Review all recommendations
- [ ] Approve consolidation plan
- [ ] Create merged artifacts
- [ ] Update all references
- [ ] Archive duplicates with redirects
- [ ] Test all links work
- [ ] Update documentation
- [ ] Commit changes
- [ ] Notify team

---

## Files Requiring Reference Updates

### [File 1]
**Path**: [path]
**Change**: Replace `[old-reference]` with `[new-reference]`
**Line**: [line number]

### [File 2]
[Repeat]
```

## Examples (Few-Shot)

### Example 1: Merge Exact Duplicate Rules

**Input**: Scan `.cursor/rules/ticket/` for duplicates

**Reasoning**:
- Found `validation-before-completion.mdc` and `completion-validation.mdc`
- 95% overlap - same checklist, different wording
- validation-before-completion.mdc is more complete and recent
- Should merge immediately

**Output**:
```markdown
## Duplicate Set 1: Completion Validation

### Artifacts Involved
1. **validation-before-completion-rule.mdc**: 450 lines, updated 2025-12-01, 12 references
2. **completion-validation-rule.mdc**: 380 lines, updated 2025-10-15, 3 references

### Similarity: 95%

**Common**: Same validation checklist, same intent
**Unique to A**: More examples, better checklist structure
**Unique to B**: Slightly different wording

### Recommendation: MERGE

**Action**:
1. Keep validation-before-completion-rule.mdc (better quality)
2. Archive completion-validation-rule.mdc
3. Update 3 references to point to validation-before-completion-rule.mdc

**Merged Artifact**: [Shows validation-before-completion.mdc with any valuable B elements integrated]
```

### Example 2: Keep Both with Clarification

**Input**: Analyze `.cursor/prompts/testing/`

**Reasoning**:
- Found `generate-tests.prompt.md` and `generate-unit-tests.prompt.md`
- 60% overlap but serve different purposes
- generate-tests is broader (unit + integration)
- generate-unit-tests is specialized (unit only, more detailed)
- Keep both but clarify distinction

**Output**:
```markdown
## Duplicate Set 2: Test Generation

### Artifacts Involved
1. **generate-tests.prompt.md**: General test generation (unit + integration)
2. **generate-unit-tests.prompt.md**: Specialized unit test generation

### Similarity: 60%

### Recommendation: KEEP BOTH (with clarification)

**Rationale**: Serve different purposes
- generate-tests: Quick test scaffolding for any test type
- generate-unit-tests: Comprehensive unit test suite with AAA pattern, FluentAssertions, etc.

**Action**:
1. Add "Related Prompts" section to each
2. Update descriptions to clarify scope
3. Cross-reference for discoverability

**Updates**:
- generate-tests.prompt.md: Add note "For detailed unit tests, see @generate-unit-tests"
- generate-unit-tests.prompt.md: Add note "For integration tests, see @generate-tests"
```

### Example 3: Extract Common Pattern

**Input**: Analyze `.cursor/rules/` for validation patterns

**Reasoning**:
- Found 5 rules with similar validation checklist structure
- All have Critical/Standard/Quality/Best Practice levels
- Same checklist pattern, different domains
- Should extract to templar

**Output**:
```markdown
## Duplicate Set 3: Validation Checklist Pattern

### Artifacts Involved
1. ticket/validation-before-completion-rule.mdc
2. documentation/validate-xml-docs-rule.mdc
3. quality/validate-code-quality-rule.mdc
4. prompts/validate-prompt-quality-rule.mdc
5. cicd/validate-build-rule.mdc

### Common Pattern: Multi-level validation checklist (80% similar)

### Recommendation: EXTRACT PATTERN

**Action**:
1. Create `.cursor/rules/templars/validation/multi-level-checklist-templar.mdc`
2. Update all 5 rules to reference the templar
3. Each rule keeps domain-specific validation items

**Templar Created**: [Shows extracted validation pattern]

**Artifact Updates**: [Shows how each rule now references templar]
```

## Detection Heuristics

### Filename Similarity
- Same base name: `validation-rule.mdc` vs `validate-rule.mdc`
- Synonyms: `check-*` vs `validate-*` vs `verify-*`
- Prefix/suffix variants: `*-validation` vs `validation-*`

### Content Similarity
- Same keywords in title/description (70%+ match)
- Same section structure
- Same examples or similar code snippets
- Same concepts explained differently

### Semantic Similarity
- Cover same domain/category
- Solve same problem
- Reference same standards
- Used in same contexts

## Troubleshooting

### Issue: Unsure Whether to Merge

**Symptom**: Two artifacts seem similar but have subtle differences

**Solution**:
1. List 3 concrete use cases for each artifact
2. If use cases overlap completely → Merge
3. If use cases differ → Keep both, clarify when to use which
4. Ask: "Would a new team member know which to use?"

### Issue: Merge Loses Valuable Content

**Symptom**: After merging, realize duplicate had unique value

**Solution**:
- Keep duplicates in archive/ (don't delete)
- Can restore valuable sections if needed
- Update merged artifact to incorporate missed value
- Lesson: Review both artifacts thoroughly before merge

### Issue: Many References to Update

**Symptom**: Consolidation would require updating 50+ files

**Solution**:
- Use search/replace tools for bulk updates
- Create redirect in archived artifact
- Staged migration: deprecate first, archive later
- Consider if keeping both is actually better

### Issue: Can't Decide Which Version is Better

**Symptom**: Both artifacts have strengths

**Solution**:
1. Create new merged version taking best from both
2. Don't feel bound to pick one - combine strengths
3. Get peer review if still unclear
4. Prototype merged version before committing

## Anti-Patterns

### ❌ Merge Everything with Any Similarity

**Bad**: "These two rules mention 'validation' so let's merge them"

**Why Bad**: May serve different purposes despite superficial similarity

**Better**: Analyze actual overlap and use cases before merging

### ❌ Keep Obvious Duplicates to Avoid Work

**Bad**: "Updating references is work, let's just keep both"

**Why Bad**: Duplicates cause confusion and diverge over time

**Better**: Invest time to consolidate properly

### ❌ Delete Without Archive

**Bad**: Delete duplicate file permanently

**Why Bad**: May lose valuable content or historical context

**Better**: Archive with clear redirect and reason

### ❌ Force-Fit Unrelated Artifacts

**Bad**: Merge artifacts just because they're in same folder

**Why Bad**: Creates bloated, unfocused artifacts

**Better**: Keep focused artifacts even if in same domain

## Best Practices

### DO
- ✅ Scan regularly (quarterly) to catch duplicates early
- ✅ Preserve valuable content from both duplicates
- ✅ Archive rather than delete
- ✅ Add redirects in archived artifacts
- ✅ Update all references immediately
- ✅ Document merge rationale
- ✅ Get peer review for major merges

### DON'T
- ❌ Merge without understanding both artifacts
- ❌ Delete duplicates permanently
- ❌ Leave broken references
- ❌ Merge unrelated artifacts just to reduce file count
- ❌ Ignore subtle but important differences
- ❌ Consolidate without team awareness

## Quality Criteria

Before finalizing consolidation:

- [ ] All duplicate sets identified and analyzed
- [ ] Similarity scores calculated accurately
- [ ] Quality comparison objective (not just preference)
- [ ] Strategy chosen matches overlap level
- [ ] Merged artifacts preserve all valuable content
- [ ] All references identified for migration
- [ ] Archived artifacts have clear redirects
- [ ] No information lost in consolidation
- [ ] Cross-references updated for discoverability
- [ ] Team aware of changes

---

## Related Prompts

- `housekeeping/extract-templar-exemplar.prompt.md` - Extract patterns when multiple artifacts share structure
- `housekeeping/update-cross-references.prompt.md` - Fix references after consolidation
- `housekeeping/archive-obsolete-artifacts.prompt.md` - Properly archive merged duplicates

## Related Rules

- `.cursor/rules/rule-authoring/rule-templars-and-exemplars.mdc` - Pattern extraction
- `.cursor/rules/rule-authoring/rule-cross-references.mdc` - Reference management

## Usage

**Scan specific folder**:
```
@consolidate-duplicates .cursor/rules/ticket/
@consolidate-duplicates .cursor/prompts/
@consolidate-duplicates docs/technical/
```

**Scan for specific artifact type**:
```
@consolidate-duplicates .cursor/ --type rules
@consolidate-duplicates .cursor/ --type prompts
```

**Analyze specific suspected duplicates**:
```
@consolidate-duplicates artifact-a.mdc artifact-b.mdc
```

## Script
- `.cursor/scripts/housekeeping/consolidate-duplicates.ps1`
  - Console summary: `pwsh -File .cursor/scripts/housekeeping/consolidate-duplicates.ps1 -Folder ".cursor"`
  - JSON: `pwsh -File .cursor/scripts/housekeeping/consolidate-duplicates.ps1 -Folder ".cursor" -Json`
  - PassThru object: `pwsh -File .cursor/scripts/housekeeping/consolidate-duplicates.ps1 -Folder ".cursor" -PassThru`

---

**Note**: Run this quarterly or when noticing confusion about which artifact to use. Early detection prevents duplication debt.

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
