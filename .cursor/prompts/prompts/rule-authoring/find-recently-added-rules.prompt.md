---
name: find-recently-added-rules
description: "Please find rules that have been recently added to the rule library"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Time period to check (e.g., 7d, 30d, 90d)"
category: rule-authoring
tags: rules, rule-authoring, recently-added, tracking, maintenance, monitoring, analysis, quality
---

# Find Recently Added Rules

Please scan the rule library and identify rules that have been recently added or modified within the specified time period.

**Pattern**: Maintenance Tracking Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for tracking rule library evolution and identifying new additions
**Use When**: Need to review recent rule additions or track library growth

---

## Purpose

Identify rules that have been recently added to the rule library to:
- Track new rule development and contributions
- Review recent additions for quality and consistency
- Monitor rule library growth and activity
- Ensure new rules follow framework standards and are properly integrated
- Identify patterns in rule creation and domain coverage

---

## Required Context

- **Time Period**: How far back to check (e.g., `7d`, `30d`, `90d`)
- **Optional**: Specific domains to focus on
- **Optional**: Include/exclude certain types of changes (additions vs modifications)

---

## Process

1. **Scan Rule Directory**
   - Examine `.cursor/rules/` folder structure
   - Identify all `.mdc` rule files recursively

2. **Check Modification Times**
   - Get file modification timestamps
   - Filter by specified time period
   - Sort by most recent first

3. **Analyze Changes**
   - Determine if additions vs modifications
   - Check for proper framework compliance (front-matter, structure)
   - Identify potential quality concerns

4. **Categorize Findings**
   - Group by domain/type
   - Flag potential review candidates
   - Prioritize critical items

5. **Report Results**
   - List recently added/modified rules
   - Provide actionable insights
   - Suggest next steps

## Decision Tree for Complex Analysis

```
Found recent rules?
├─ YES → Continue to categorization
└─ NO → Check time period
    ├─ Too short? → Extend period (try 90d)
    └─ Library inactive? → Check git activity
        ├─ No recent commits → Rule maintenance needed
        └─ Commits exist → Check file patterns

Rules need review?
├─ YES → Prioritize by domain
│   ├─ Critical (broken front-matter) → Immediate action required
│   ├─ High (new domains/workflows) → Schedule review within 1 week
│   ├─ Medium (enhancements) → Review within 2 weeks
│   └─ Low (minor updates) → Optional review
└─ NO → Generate summary report
    ├─ Export available? → Choose format (markdown/json/csv)
    └─ Automation needed? → Configure monitoring mode

Framework compliance issues found?
├─ YES → Create remediation plan
│   ├─ Critical issues → Immediate fixes required
│   ├─ Multiple issues → Batch processing approach
│   └─ Structural issues → Comprehensive review needed
└─ NO → Quality assessment complete
    ├─ High compliance → Consider as exemplars
    ├─ Standard compliance → No action needed
    └─ Compliance issues → Improvement recommended
```

---

## Reasoning Process (for AI Agent)

When analyzing recent rule additions:

1. **Understand Scope**: What constitutes "recent" based on the time period
2. **Framework First**: New rules need immediate validation against rule-authoring framework
3. **Impact Assessment**: Consider how new rules affect existing workflows and dependencies
4. **Quality Assurance**: Ensure new rules follow canonical structure and contracts
5. **Integration Check**: Verify rules are properly integrated into domains and referenced
6. **Suggest Actions**: Provide clear next steps for review and integration

---

## Expected Output

```markdown
## Recently Added Rules Report

**Time Period**: Last 30 days
**Total Rules Found**: 15

### New Additions (10)
- **agile/create-user-story-rule.mdc** (3 days ago)
  - Domain: agile
  - Framework compliance: ✅ Valid front-matter and structure
  - Review: Recommended - new agile workflow addition

- **ticket/plan-update-rule.mdc** (7 days ago)
  - Domain: ticket
  - Framework compliance: ⚠️ Missing provenance footer specification
  - Review: Required - framework compliance fix needed

### Recent Modifications (5)
- **rule-authoring/file-structure-rule.mdc** (1 day ago)
  - Domain: rule-authoring
  - Change: Enhanced section ordering examples
  - Review: Optional - enhancement review

## Summary
- **New Rules**: 10 (67%)
- **Modified Rules**: 5 (33%)
- **Framework Compliance Issues**: 2 rules need fixes
- **Review Priority**: 7 rules recommended for review

## Next Steps
1. Review 2 rules with framework compliance issues
2. Quality check 5 high-priority new rules
3. Update rule cross-references as needed
4. Consider creating review tickets for major additions
```

---

## Examples (Few-Shot)

### Example 1: Basic 30-Day Check

**Input**: `30d`

**Expected Output**:
```markdown
## Recently Added Rules Report

**Time Period**: Last 30 days
**Total Rules Found**: 12

### New Additions (8)
- **git/branch-lifecycle-rule.mdc** (5 days ago)
  - Domain: git
  - Framework compliance: ✅ Valid front-matter and structure
  - Review: Recommended - new workflow addition

- **database/index-create-rule.mdc** (12 days ago)
  - Domain: database-standards
  - Framework compliance: ⚠️ Missing checklist section
  - Review: Required - critical framework violation

### Recent Modifications (4)
- **rule-authoring/naming-conventions-rule.mdc** (2 days ago)
  - Domain: rule-authoring
  - Change: Added new domain examples
  - Review: Optional - documentation enhancement

## Summary
- **New Rules**: 8 (67%)
- **Modified Rules**: 4 (33%)
- **Framework Compliance Issues**: 1 rule needs fixes
- **Review Priority**: 6 rules recommended for review

## Next Steps
1. Fix framework compliance issue in database rule
2. Quality check 5 high-priority new rules
3. Update cross-references for new rules
4. Consider review tickets for complex additions
```

### Example 2: Quick 7-Day Scan

**Input**: `7d`

**Expected Output**:
```markdown
## Recently Added Rules Report

**Time Period**: Last 7 days
**Total Rules Found**: 4

### New Additions (3)
- **migration/data-collection-rule.mdc** (2 days ago)
  - Domain: migration
  - Framework compliance: ✅ Valid front-matter and structure
  - Review: Recommended - expands migration capabilities

### Recent Modifications (1)
- **find-recently-added-rules.prompt.mdc** (now)
  - Domain: rule-authoring
  - Change: Added examples and improved structure
  - Review: Self-review completed

## Summary
- **New Rules**: 3 (75%)
- **Modified Rules**: 1 (25%)
- **Framework Compliance Issues**: 0
- **Review Priority**: 3 rules recommended for review

## Next Steps
1. Test new migration rule in context
2. Update team documentation with new capabilities
3. Ensure cross-references include new rule
```

---

## Usage Modes

### Quick Scan Mode (Default)
For rapid assessment of recent activity:
```
@find-recently-added-rules 7d
```
- Fast execution (< 15 seconds)
- Basic categorization
- Essential framework compliance checks

### Comprehensive Analysis Mode
For detailed review and planning:
```
@find-recently-added-rules 30d --comprehensive
```
- Deep analysis of all rules
- Framework compliance scoring
- Integration status validation
- Change impact analysis
- Review priority recommendations

### Domain Focus Mode
For domain-specific monitoring:
```
@find-recently-added-rules 90d --domain ticket
```
- Filter by specific domains (ticket, migration, git, etc.)
- Domain-specific analysis
- Domain-specific recommendations

### Batch Processing Mode
For large libraries or automated workflows:
```
@find-recently-added-rules 30d --batch --output json
```
- Optimized for automation
- JSON/CSV export formats
- Integration with CI/CD pipelines
- Minimal human-readable output

### Monitoring Mode
For ongoing library health tracking:
```
@find-recently-added-rules 7d --monitor --threshold 3
```
- Alert when threshold exceeded
- Trend analysis
- Automated reporting
- Integration health scoring

---

## Configuration Options

### Filtering Options
- `--domain <name>`: Filter by rule domain
- `--author <name>`: Filter by author/owner
- `--kind <type>`: Filter by rule kind (rule, templar, exemplar)
- `--status <type>`: Filter by compliance status (compliant, needs-review, critical)

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

- [ ] All rule files scanned within time period
- [ ] File modification times accurately retrieved
- [ ] Proper categorization by addition vs modification
- [ ] Framework compliance status verified for each rule
- [ ] Clear prioritization for review needs
- [ ] Actionable recommendations provided

---

## Usage

**Basic usage** (last 30 days):
```
@find-recently-added-rules 30d
```

**Specific time period**:
```
@find-recently-added-rules 7d
```

**With domain focus**:
```
@find-recently-added-rules 90d --domain agile
```

---

## Troubleshooting

**Issue**: No rules found in time period
**Cause**: Time period too short or no recent activity
**Solution**: Extend time period (try 90d instead of 7d) or check if rule library has recent commits

**Issue**: File access errors
**Cause**: Permission issues or git repository problems
**Solution**: Ensure proper access to `.cursor/rules/` directory and verify git repository is clean

**Issue**: Incorrect timestamps
**Cause**: System clock differences or git operations affecting file timestamps
**Solution**: Use git log timestamps as backup verification: `git log --since="30 days ago" --name-only --name-status -- .cursor/rules/`

**Issue**: Framework compliance status incorrect
**Cause**: Front-matter parsing errors or rule structure changes
**Solution**: Verify rules follow rule-file-structure.mdc and check YAML front-matter validity

**Issue**: Missing domain classification
**Cause**: Rules not following domain folder structure
**Solution**: Ensure rules are placed in appropriate domain folders under `.cursor/rules/`

---

## Validation Checklist

Before finalizing the analysis report:

- [ ] **Time period validation**: Specified period produces meaningful results (not too short/long)
- [ ] **File scanning completeness**: All `.mdc` files in `.cursor/rules/` scanned
- [ ] **Timestamp accuracy**: File modification times are reliable (cross-checked with git if needed)
- [ ] **Categorization accuracy**: Rules correctly classified as additions vs modifications
- [ ] **Framework compliance verified**: Front-matter and structure validation completed
- [ ] **Prioritization logic**: Critical framework violations flagged appropriately
- [ ] **Output format consistency**: Report structure matches expected format
- [ ] **Actionable recommendations**: Next steps are specific and achievable
- [ ] **Performance optimized**: Large libraries processed efficiently
- [ ] **Error handling**: Edge cases (permissions, missing files) handled gracefully

---

## Performance Considerations

### For Large Rule Libraries (>50 rules)

**Optimization Strategies**:
- Use `--batch` mode for parallel processing
- Limit time periods to recent activity (7-30 days)
- Filter by domain to reduce scope
- Use `--output json` for faster processing
- Consider incremental scanning for monitoring

**Expected Performance**:
- Small library (<25 rules): <10 seconds
- Medium library (25-100 rules): 15-45 seconds
- Large library (>100 rules): 45-90 seconds with batch mode

**Memory Usage**: Linear scaling with rule count, typically <100MB for 500 rules

---

## Related Prompts

- `rule-authoring/find-rules-needing-review.prompt.md` - Find rules requiring quality review
- `rule-authoring/create-new-rule.prompt.md` - Create new rules following framework
- `rule-authoring/validate-rule.prompt.md` - Verify individual rule compliance

---

## Related Rules

- `.cursor/rules/rule-authoring/rule-authoring-overview.mdc` - Rule framework overview
- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Rule structure requirements
- `.cursor/rules/rule-authoring/rule-naming-conventions.mdc` - Naming standards
- `.cursor/rules/rule-authoring/rule-provenance-and-versioning.mdc` - Version tracking

---

**Created**: 2025-12-13
**Enhanced**: 2025-12-13 (Added usage modes, decision tree, validation checklist, performance considerations)
**Follows**: `.cursor/rules/rule-authoring/rule-authoring-overview.mdc` v1.0.0
**Complexity**: Advanced (Multiple operational modes, comprehensive framework compliance analysis)
