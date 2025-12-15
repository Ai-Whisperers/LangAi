---
name: find-recently-added-prompts
description: "Please find prompts that have been recently added to the prompt library"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Time period to check (e.g., 7d, 30d, 90d)"
category: housekeeping
tags: prompts, housekeeping, recently-added, tracking, maintenance, monitoring, analysis, quality
---

# Find Recently Added Prompts

Please scan the prompt library and identify prompts that have been recently added or modified within the specified time period.

**Pattern**: Maintenance Tracking Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for tracking prompt library evolution and identifying new additions
**Use When**: Need to review recent prompt additions or track library growth

---

## Purpose

Identify prompts that have been recently added to the prompt library to:
- Track new prompt development and contributions
- Review recent additions for quality and consistency
- Monitor prompt library growth and activity
- Ensure new prompts follow standards and are properly integrated

---

## Required Context

- **Time Period**: How far back to check (e.g., `7d`, `30d`, `90d`)
- **Optional**: Specific categories to focus on
- **Optional**: Include/exclude certain types of changes (additions vs modifications)
**Optional**: Filter by category, author, or complexity level
**Optional**: Output format preference (markdown, json, csv)

---

## Process

1. **Scan Prompt Directory**
   - Examine `.cursor/prompts/` folder structure
   - Identify all `.prompt.md` files recursively
   - **Include uncommitted changes**: Check git status for staged/unstaged prompt files

2. **Check Modification Times**
   - Get file modification timestamps from filesystem
   - Check git commit history for committed changes
   - **Prioritize uncommitted files**: Files not yet in git are "most recent"
   - Filter by specified time period (filesystem timestamps for uncommitted, git timestamps for committed)
   - Sort by most recent first

3. **Analyze Changes**
   - Determine if additions vs modifications
   - Check for proper integration (collections, references)
   - Identify potential quality concerns

4. **Categorize Findings**
   - Group by category/type
   - Flag potential review candidates
   - Prioritize critical items

5. **Report Results**
   - List recently added/modified prompts
   - Provide actionable insights
   - Suggest next steps

## Decision Tree for Complex Analysis

```
Found recent prompts?
├─ YES → Continue to categorization
│   ├─ Include uncommitted? → Flag as "very recent" (not yet in git)
│   └─ Only committed → Proceed normally
└─ NO → Check uncommitted changes first
    ├─ Uncommitted files exist → Include them as recent additions
    ├─ No uncommitted files → Check time period
    │   ├─ Too short? → Extend period (try 90d)
    │   └─ Library inactive? → Check git activity
    │       ├─ No recent commits → Library maintenance needed
    │       └─ Commits exist → Check file patterns
    └─ Time period OK → No recent activity

Prompts need review?
├─ YES → Prioritize by category
│   ├─ Critical (missing collections) → Immediate action required
│   ├─ High (new workflows) → Schedule review within 1 week
│   ├─ Medium (enhancements) → Review within 2 weeks
│   └─ Low (minor updates) → Optional review
└─ NO → Generate summary report
    ├─ Export available? → Choose format (markdown/json/csv)
    └─ Automation needed? → Configure monitoring mode

Integration issues found?
├─ YES → Create remediation plan
│   ├─ Critical issues → Immediate fixes required
│   ├─ Multiple issues → Batch processing approach
│   └─ Structural issues → Comprehensive review needed
└─ NO → Quality assessment complete
    ├─ High quality → Consider as exemplars
    ├─ Standard quality → No action needed
    └─ Quality issues → Improvement recommended
```

---

## Reasoning Process (for AI Agent)

When analyzing recent prompt additions:

1. **Understand Scope**: What constitutes "recent" based on the time period
2. **Prioritize Quality**: New prompts need immediate review for standards compliance
3. **Track Integration**: Ensure new prompts are properly added to collections and referenced
4. **Identify Patterns**: Look for trends in prompt development and potential gaps
5. **Suggest Actions**: Provide clear next steps for review and integration

---

## Expected Output

```markdown
## Recently Added Prompts Report

**Time Period**: Last 30 days
**Total Prompts Found**: 12

### New Additions (8)
- **agile/create-user-story.prompt.md** (2 days ago)
  - Category: agile
  - Status: ✅ Added to collection
  - Review: Recommended - new agile workflow

### Uncommitted Additions (3)
- **code-quality/new-validation.prompt.md** (uncommitted)
  - Category: code-quality
  - Status: ⚠️ Not yet committed to git
  - Review: Requires commit + collection integration

- **code-quality/validate-clean-code.prompt.md** (5 days ago)
  - Category: code-quality
  - Status: ⚠️ Missing from collection
  - Review: Required - collection integration needed

### Recent Modifications (4)
- **documentation/create-readme.prompt.md** (1 day ago)
  - Category: documentation
  - Change: Enhanced with examples
  - Review: Optional - enhancement review

## Summary
- **New Prompts**: 8 (67%)
- **Modified Prompts**: 4 (33%)
- **Uncommitted Additions**: 3 (not yet in git)
- **Integration Issues**: 2 prompts need collection updates
- **Review Priority**: 6 prompts recommended for review
- **Critical Note**: Uncommitted prompts require git commit before team visibility

## Next Steps
1. **Handle uncommitted prompts first**:
   - Commit uncommitted additions to git
   - Update collection manifests for new prompts
   - Test Prompt Registry integration
2. Review 2 prompts missing from collections
3. Quality check 4 high-priority new prompts
4. Update collection manifests as needed
5. Consider creating review tickets for major additions
```

---

## Examples (Few-Shot)

### Example 1: Basic 30-Day Check

**Input**: `30d`

**Expected Output**:
```markdown
## Recently Added Prompts Report

**Time Period**: Last 30 days
**Total Prompts Found**: 8

### New Additions (6)
- **git/create-branch.prompt.md** (3 days ago)
  - Category: git
  - Status: ✅ Added to collection
  - Review: Recommended - new workflow addition

- **code-quality/validate-style.prompt.md** (7 days ago)
  - Category: code-quality
  - Status: ⚠️ Missing from collection
  - Review: Required - collection integration needed

### Recent Modifications (2)
- **documentation/create-readme.prompt.md** (1 day ago)
  - Category: documentation
  - Change: Enhanced with examples
  - Review: Optional - enhancement review

## Summary
- **New Prompts**: 6 (75%)
- **Modified Prompts**: 2 (25%)
- **Integration Issues**: 1 prompt needs collection updates
- **Review Priority**: 4 prompts recommended for review

## Next Steps
1. Add missing prompt to git-workflows.collection.yml
2. Quality check 3 high-priority new prompts
3. Update collection manifest
4. Consider review tickets for complex additions
```

### Example 2: Quick 7-Day Scan

**Input**: `7d`

**Expected Output**:
```markdown
## Recently Added Prompts Report

**Time Period**: Last 7 days
**Total Prompts Found**: 3

### New Additions (2)
- **testing/generate-unit-tests.prompt.md** (2 days ago)
  - Category: testing
  - Status: ✅ Added to collection
  - Review: Recommended - expands testing capabilities

### Recent Modifications (1)
- **housekeeping/find-recently-added-prompts.prompt.md** (now)
  - Category: housekeeping
  - Change: Added examples and improved structure
  - Review: Self-review completed

## Summary
- **New Prompts**: 2 (67%)
- **Modified Prompts**: 1 (33%)
- **Integration Issues**: 0
- **Review Priority**: 2 prompts recommended for review

## Next Steps
1. Test new unit test generation prompt
2. Update team documentation with new capabilities
```

---

## Usage Modes

### Quick Scan Mode (Default)
For rapid assessment of recent activity:
```
@find-recently-added-prompts 7d
```
- Fast execution (< 10 seconds)
- Basic categorization
- Essential integration checks only

### Comprehensive Analysis Mode
For detailed review and planning:
```
@find-recently-added-prompts 30d --comprehensive
```
- Deep analysis of all prompts
- Quality assessment scoring
- Integration status validation
- Change impact analysis
- Review priority recommendations

### Category Focus Mode
For domain-specific monitoring:
```
@find-recently-added-prompts 90d --category agile
```
- Filter by specific categories (agile, testing, documentation, etc.)
- Cross-category analysis
- Category-specific recommendations

### Batch Processing Mode
For large libraries or automated workflows:
```
@find-recently-added-prompts 30d --batch --output json
```
- Optimized for automation
- JSON/CSV export formats
- Integration with CI/CD pipelines
- Minimal human-readable output

### Monitoring Mode
For ongoing library health tracking:
```
@find-recently-added-prompts 7d --monitor --threshold 5
```
- Alert when threshold exceeded
- Trend analysis
- Automated reporting
- Integration health scoring

---

## Configuration Options

### Filtering Options
- `--category <name>`: Filter by prompt category
- `--author <name>`: Filter by author/owner
- `--complexity <level>`: Filter by complexity (basic/standard/advanced)
- `--status <type>`: Filter by integration status (added/missing/needs-review)

### Output Options
- `--output <format>`: Output format (markdown/json/csv)
- `--comprehensive`: Include detailed analysis
- `--quiet`: Minimal output for automation
- `--verbose`: Include debug information

### Analysis Options
- `--batch`: Optimize for batch processing
- `--monitor`: Enable monitoring alerts
- `--threshold <n>`: Alert threshold for monitoring mode
- `--include-git`: Include git metadata analysis

---

## Quality Criteria

- [ ] All prompt files scanned within time period
- [ ] File modification times accurately retrieved
- [ ] Proper categorization by addition vs modification
- [ ] Collection integration status verified
- [ ] Clear prioritization for review needs
- [ ] Actionable recommendations provided

---

## Usage

**Basic usage** (last 30 days):
```
@find-recently-added-prompts 30d
```

**Specific time period**:
```
@find-recently-added-prompts 7d
```

**With category focus**:
```
@find-recently-added-prompts 90d --category agile
```

---

## Troubleshooting

**Issue**: No prompts found in time period
**Cause**: Time period too short, no recent activity, or only uncommitted changes
**Solution**: Extend time period (try 90d instead of 7d), check git status for uncommitted files, or verify if prompt library has recent commits

**Issue**: File access errors
**Cause**: Permission issues or git repository problems
**Solution**: Ensure proper access to `.cursor/prompts/` directory and verify git repository is clean

**Issue**: Incorrect timestamps
**Cause**: System clock differences or git operations affecting file timestamps
**Solution**: Use git log timestamps as backup verification: `git log --since="30 days ago" --name-only --pretty=format: .cursor/prompts/`

**Issue**: Missing collection integration status
**Cause**: Collection manifest not found or parsing error
**Solution**: Verify `.cursor/prompts/collections/` exists and manifests use `.collection.yml` extension

**Issue**: Performance issues with large time periods
**Cause**: Scanning too many files or deep directory traversal
**Solution**: Limit to specific categories with `--category` flag or reduce time period scope

**Issue**: False positives in modification detection
**Cause**: File timestamps changed by non-content operations (permissions, moves)
**Solution**: Cross-reference with git log to verify actual content changes

---

## Validation Checklist

Before finalizing the analysis report:

- [ ] **Time period validation**: Specified period produces meaningful results (not too short/long)
- [ ] **File scanning completeness**: All `.prompt.md` files in scope were examined
- [ ] **Timestamp accuracy**: File modification times are reliable (cross-checked with git if needed)
- [ ] **Categorization accuracy**: Prompts correctly classified as additions vs modifications
- [ ] **Integration status verified**: Collection membership checked for all prompts
- [ ] **Prioritization logic**: Critical items flagged appropriately based on impact
- [ ] **Output format consistency**: Report structure matches expected format
- [ ] **Actionable recommendations**: Next steps are specific and achievable
- [ ] **Performance optimized**: Large libraries processed efficiently
- [ ] **Error handling**: Edge cases (permissions, missing files) handled gracefully

---

## Performance Considerations

### For Large Prompt Libraries (>100 prompts)

**Optimization Strategies**:
- Use `--batch` mode for parallel processing
- Limit time periods to recent activity (7-30 days)
- Filter by category to reduce scope
- Use `--output json` for faster processing
- Consider incremental scanning for monitoring

**Expected Performance**:
- Small library (<50 prompts): <5 seconds
- Medium library (50-200 prompts): 10-30 seconds
- Large library (>200 prompts): 30-60 seconds with batch mode

**Memory Usage**: Linear scaling with prompt count, typically <50MB for 1000 prompts

---

## Related Prompts

- `housekeeping/find-prompts-needing-review.prompt.md` - Find prompts requiring quality review
- `housekeeping/validate-prompt-collections.prompt.md` - Verify collection integrity
- `housekeeping/condense-prompts.prompt.md` - Merge duplicate prompts

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt quality standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Collection integration requirements
- `.cursor/rules/housekeeping/workflow-link-rule.mdc` - Maintenance workflow standards

---

**Created**: 2025-12-13
**Enhanced**: 2025-12-13 (Added usage modes, decision tree, validation checklist, performance considerations)
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Complexity**: Advanced (Multiple operational modes, comprehensive analysis capabilities)
