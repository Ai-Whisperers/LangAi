---
name: find-rules-needing-review
description: "Please find rules that need review based on quality criteria and maintenance needs"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Review criteria focus (optional: all, quality, integration, maintenance)"
category: rule-authoring
tags: rules, rule-authoring, review, quality, maintenance, validation, analysis, framework, compliance
---

# Find Rules Needing Review

Please scan the rule library and identify rules that need review based on quality criteria, framework compliance, and maintenance requirements.

**Pattern**: Quality Assurance Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Critical for maintaining rule library quality and preventing framework drift
**Use When**: Need to identify rules requiring attention or improvement

---

## Enhancement Decision Tree

```
Need to assess rule library health?
├─ YES → Continue with this prompt
└─ NO → Use specific rule improvement tools

What type of assessment needed?
├─ Quality standards compliance → @find-rules-needing-review quality
├─ Framework integration status → @find-rules-needing-review integration
├─ Maintenance and updates → @find-rules-needing-review maintenance
└─ Complete health check → @find-rules-needing-review all

Planning improvements?
├─ YES → Use results to prioritize improvement tickets
├─ NO → Use for monitoring only

Found issues to fix?
├─ Critical (YAML, missing fields) → Fix immediately, then commit
├─ Important (examples, structure) → Create improvement tickets
└─ Maintenance (consistency) → Address in next maintenance cycle
```

---

## Purpose

Identify rules requiring review to ensure the rule library maintains high quality and framework compliance. This includes:
- Framework compliance checks
- Quality standards validation
- Integration verification
- Maintenance and update needs
- Technical debt identification
- Improvement opportunities

---

## Required Context

- **Review Focus** (optional): Specific area to focus on
  - `quality`: Front-matter and content standards
  - `integration`: Cross-references and dependencies
  - `maintenance`: Updates, fixes, and technical debt
  - `all`: Comprehensive review (default)

---

## Process

1. **Scan Rule Library**
   - Examine all `.mdc` files in `.cursor/rules/`
   - Parse front-matter and content structure

2. **Apply Review Criteria**
   - Check front-matter completeness and format
   - Validate content structure and framework compliance
   - Verify cross-references and dependencies
   - Assess maintenance status

3. **Categorize Issues**
   - **Critical**: Breaking framework violations requiring immediate fix
   - **Important**: Quality issues affecting usability
   - **Maintenance**: Updates and improvements needed

4. **Prioritize Findings**
   - Sort by severity and impact
   - Group by domain and type
   - Identify quick wins vs major efforts

5. **Generate Report**
   - Detailed findings with specific issues
   - Actionable recommendations
   - Priority assignments

---

## Reasoning Process (for AI Agent)

When evaluating rules for review:

1. **Framework First**: Critical issues (missing front-matter, invalid YAML) take priority
2. **Impact Assessment**: Consider how issues affect rule effectiveness and library consistency
3. **Effort Estimation**: Balance severity with fix complexity
4. **Standards Compliance**: Ensure alignment with rule-authoring framework requirements
5. **Maintenance Burden**: Identify rules causing ongoing maintenance overhead

---

## Review Criteria

### Quality Issues
- **Front-matter**: Missing required fields, invalid YAML, incorrect format
- **Content**: Missing sections, unclear contracts, poor structure
- **Standards**: Not following rule-file-structure.mdc requirements
- **Documentation**: Missing references, outdated information

### Integration Issues
- **Cross-references**: Broken `requires` or `implements` fields
- **Dependencies**: Referenced rules that don't exist
- **Domains**: Rules in wrong domain folders
- **Naming**: IDs not following naming conventions

### Maintenance Issues
- **Age**: Long time since last review (stale provenance)
- **Versions**: Outdated major versions or missing patches
- **Consistency**: Not aligned with current framework standards
- **Completeness**: Missing required sections or contracts

---

## Examples (Few-Shot)

### Example 1: Comprehensive Quality Review

**Input**:
```
@find-rules-needing-review all
```

**Expected Output**:
```markdown
## Rules Needing Review Report

**Review Focus**: All criteria
**Total Rules Analyzed**: 89
**Rules Needing Attention**: 15 (17%)

### 🔴 Critical Issues (Fix Immediately - 3)

1. **incomplete-frontmatter-rule.mdc**
   - **Issue**: Missing required 'description' field in YAML front-matter
   - **Impact**: Rule cannot be properly referenced or discovered
   - **Fix**: Add description field: `description: "One-sentence rule purpose"`

2. **broken-yaml-rule.mdc**
   - **Issue**: Invalid YAML front-matter (incorrect indentation)
   - **Impact**: Rule cannot be parsed by framework tools
   - **Fix**: Fix YAML indentation and format

### 🟡 Important Issues (Fix Soon - 8)

1. **missing-examples-rule.mdc**
   - **Issue**: No clear examples in contracts or steps
   - **Impact**: Rules are harder to understand and apply
   - **Fix**: Add specific examples to inputs/outputs contracts

2. **outdated-references-rule.mdc**
   - **Issue**: References old rule IDs that were renamed
   - **Impact**: Broken cross-references in Related Rules section
   - **Fix**: Update to current rule IDs following provenance

3. **vague-contracts-rule.mdc**
   - **Issue**: Input/output contracts are ambiguous ("files", "data")
   - **Impact**: Rules cannot be reliably applied or validated
   - **Fix**: Make contracts specific and testable

### 🔵 Maintenance Issues (Address When Convenient - 4)

1. **old-provenance-rule.mdc**
   - **Issue**: Last review date over 6 months old
   - **Impact**: Rule may be stale or non-compliant with current standards
   - **Fix**: Review rule and update `last_review` date

## Summary by Domain

| Domain | Total | Need Review | Percentage |
|--------|-------|-------------|------------|
| ticket | 15 | 4 | 27% |
| git | 12 | 3 | 25% |
| rule-authoring | 10 | 2 | 20% |

## Quick Wins (5-10 min fixes)
- Fix 3 YAML front-matter issues
- Add 4 missing description fields
- Update 2 broken references

## Recommended Actions
1. **Immediate**: Fix 3 critical YAML/front-matter issues
2. **This Week**: Address 6 important quality issues
3. **This Month**: Tackle maintenance improvements
4. **Create Tickets**: Major refactoring (2 rules need significant rework)
```

### Example 2: Focused Quality Check

**Input**:
```
@find-rules-needing-review quality
```

**Expected Output**:
```markdown
## Rules Needing Review Report

**Review Focus**: Quality criteria only
**Total Rules Analyzed**: 89
**Rules Needing Attention**: 11 (12%)

### 🔴 Critical Issues (Fix Immediately - 2)

1. **invalid-globs-rule.mdc**
   - **Issue**: `globs` field uses JSON array syntax instead of Cursor comma-delimited format
   - **Impact**: Rule cannot be properly activated by Cursor
   - **Fix**: Change `globs: ["**/pattern.md"]` to `globs: **/pattern.md`

### 🟡 Important Issues (Fix Soon - 9)

1. **unclear-purpose-rule.mdc**
   - **Issue**: Purpose & Scope section is vague ("handles files")
   - **Impact**: Unclear when and how to apply the rule
   - **Fix**: Make purpose specific with applies-to/does-not-apply-to statements

2. **missing-checklist-rule.mdc**
   - **Issue**: No FINAL MUST-PASS CHECKLIST section
   - **Impact**: No quality assurance for rule outputs
   - **Fix**: Add checklist with 3-7 binary validation items
```

### Example 3: Integration Focus

**Input**:
```
@find-rules-needing-review integration
```

**Expected Output**:
```markdown
## Rules Needing Review Report

**Review Focus**: Integration criteria only
**Total Rules Analyzed**: 89
**Rules Needing Attention**: 7 (8%)

### 🟡 Important Issues (Fix Soon - 7)

1. **orphaned-rule.mdc**
   - **Issue**: Not referenced by any other rules (no inbound references)
   - **Impact**: Rule may be unused or poorly integrated
   - **Fix**: Add to Related Rules sections of relevant rules or deprecate

2. **broken-requires-rule.mdc**
   - **Issue**: `requires` field references non-existent rule ID
   - **Impact**: Rule cannot load dependencies, may fail execution
   - **Fix**: Update to correct rule ID or remove invalid reference

3. **wrong-domain-rule.mdc**
   - **Issue**: Rule placed in wrong domain folder (ticket rule in git folder)
   - **Impact**: Poor organization, harder to discover
   - **Fix**: Move to correct domain folder
```

---

## Expected Output

```markdown
## Rules Needing Review Report

**Review Focus**: All criteria
**Total Rules Analyzed**: 147
**Rules Needing Attention**: 28 (19%)

### 🔴 Critical Issues (Fix Immediately - 5)

1. **broken-frontmatter-rule.mdc**
   - **Issue**: Invalid YAML front-matter (missing quotes around description)
   - **Impact**: Rule cannot be loaded by framework tools
   - **Fix**: Add quotes around description field

2. **missing-id-rule.mdc**
   - **Issue**: No `id` field in front-matter
   - **Impact**: Rule cannot be referenced or discovered
   - **Fix**: Add unique ID following `rule.[domain].[action].v[major]` pattern

### 🟡 Important Issues (Fix Soon - 15)

1. **incomplete-contracts-rule.mdc**
   - **Issue**: Input/output contracts are missing or placeholder-only
   - **Impact**: Rules cannot be reliably applied or validated
   - **Fix**: Add specific, testable contracts for inputs and outputs

2. **outdated-cross-references-rule.mdc**
   - **Issue**: References old rule IDs that were superseded
   - **Impact**: Broken links in Related Rules sections
   - **Fix**: Update to current rule IDs

### 🔵 Maintenance Issues (Address When Convenient - 8)

1. **stale-provenance-rule.mdc**
   - **Issue**: `last_review` date over 90 days old
   - **Impact**: Rule may not reflect current standards or practices
   - **Fix**: Review rule content and update `last_review` date

## Summary by Domain

| Domain | Total | Need Review | Percentage |
|--------|-------|-------------|------------|
| agile | 12 | 3 | 25% |
| code-quality | 18 | 5 | 28% |
| documentation | 8 | 1 | 13% |
| git | 15 | 4 | 27% |
| housekeeping | 9 | 2 | 22% |

## Quick Wins (5-10 min fixes)
- Fix 4 YAML formatting issues
- Add missing `id` fields (3 rules)
- Update 3 broken references

## Recommended Actions
1. **Immediate**: Fix 5 critical front-matter issues
2. **This Week**: Address 10 important quality issues
3. **This Month**: Tackle maintenance improvements
4. **Create Tickets**: Major refactoring (3 rules need significant rework)
5. **Monitor**: Set up regular reviews for high-change domains
```

---

## Validation Checklist

Before claiming review is complete:

- [ ] All `.mdc` files in `.cursor/rules/` scanned
- [ ] Front-matter validation completed (YAML format, required fields)
- [ ] Content structure analysis performed against rule-file-structure.mdc
- [ ] Issues categorized by severity (Critical/Important/Maintenance)
- [ ] Specific file paths and line numbers provided for all issues
- [ ] Actionable recommendations with effort estimates included
- [ ] Priority assignments based on impact and implementation complexity
- [ ] Report format matches expected output structure

---

## Usage Modes

### Comprehensive Review (Default)
For complete quality assessment across all criteria:
```
@find-rules-needing-review
```
or explicitly:
```
@find-rules-needing-review all
```

### Focused Reviews
Target specific areas of concern:

**Quality Standards Check**:
```
@find-rules-needing-review quality
```
*Checks front-matter, content structure, clarity, and framework compliance*

**Integration Verification**:
```
@find-rules-needing-review integration
```
*Validates cross-references, dependencies, and domain organization*

**Maintenance Assessment**:
```
@find-rules-needing-review maintenance
```
*Identifies outdated patterns and technical debt*

### Advanced Usage

**With Custom Context**:
```
@find-rules-needing-review quality --include-drafts
```
*Include draft rules in review (future enhancement)*

**Batch Processing**:
```
@find-rules-needing-review all --output-format json
```
*Generate machine-readable output for automation (future enhancement)*

---

## Troubleshooting

**Issue**: No rules found needing review
**Cause**: Very high quality standards or recent cleanup
**Solution**: Lower threshold or check if review criteria are too strict

**Issue**: Too many rules flagged
**Cause**: Review criteria too broad or standards too high
**Solution**: Focus on specific domains or adjust criteria

**Issue**: Inconsistent results
**Cause**: Review criteria not applied uniformly
**Solution**: Document specific standards and ensure consistent application

---

## Success Metrics

### Framework Health Indicators

**Excellent** (Target: <10% need review):
- <10% of rules need attention
- 0 critical framework violations
- <15% important issues
- Maintenance issues <25%

**Good** (Acceptable: 10-20% need review):
- 10-20% of rules need attention
- 0 critical framework violations
- 15-25% important issues
- Maintenance issues <35%

**Needs Attention** (>20% need review):
- >20% of rules need attention
- Critical framework violations present
- >25% important issues
- Maintenance issues >35%

### Improvement Velocity

**Track Progress**:
- Critical issues: Fix within 24 hours
- Important issues: Address within 1 week
- Maintenance issues: Ongoing improvement

**Measure Success**:
- **Time to fix**: Average time from identification to resolution
- **Framework compliance**: % of rules passing all quality checks
- **Review coverage**: % of rules reviewed within maintenance windows

---

## Integration with Quality Workflow

This prompt is part of the **Rule Quality Assurance Pipeline**:

1. **Discovery**: `find-recently-added-rules.prompt.md` - Identify new rules requiring initial review
2. **Assessment**: `find-rules-needing-review.prompt.md` - Evaluate quality and framework compliance gaps
3. **Improvement**: `improve-rule.prompt.md` - Fix critical issues and basic problems
4. **Enhancement**: `enhance-rule.prompt.md` - Add advanced features after basic fixes
5. **Validation**: `validate-rule.prompt.md` - Confirm improvements work correctly

### Quality Gates
- **Gate 1**: No critical framework violations (YAML, missing IDs) - Must pass before commit
- **Gate 2**: No important issues (contracts, structure) - Should fix within 1 week
- **Gate 3**: Maintenance issues addressed - Ongoing improvement process

---

## Related Prompts

- `rule-authoring/find-recently-added-rules.prompt.md` - Find new rules requiring initial review
- `rule-authoring/create-new-rule.prompt.md` - Create new rules following framework
- `rule-authoring/improve-rule.prompt.md` - Fix critical issues identified by this review
- `rule-authoring/enhance-rule.prompt.md` - Add advanced features after basic fixes
- `rule-authoring/validate-rule.prompt.md` - Verify individual rule compliance

---

## Related Rules

- `.cursor/rules/rule-authoring/rule-authoring-overview.mdc` - Framework overview and standards
- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Structure requirements
- `.cursor/rules/rule-authoring/rule-naming-conventions.mdc` - Naming standards
- `.cursor/rules/rule-authoring/rule-contracts-and-scope.mdc` - Contract writing patterns
- `.cursor/rules/rule-authoring/rule-validation-and-checklists.mdc` - Checklist patterns

---

## Extracted Patterns

This prompt demonstrates exceptional quality in systematic quality assurance and has been analyzed for reusable patterns:

**Templar Opportunity**:
- `.cursor/prompts/templars/rule-authoring/systematic-rule-quality-review-templar.md` - Multi-criteria assessment workflow with severity-based prioritization for rule libraries

**Exemplar Value**:
- `.cursor/prompts/exemplars/rule-authoring/comprehensive-rule-quality-assessment-exemplar.md` - Reference implementation of thorough framework compliance scanning with actionable reporting

**Why Valuable**: Demonstrates advanced quality assurance patterns including multi-dimensional assessment (quality/integration/maintenance), severity-based issue categorization, effort estimation for prioritization, decision tree for appropriate usage, and integration with broader rule-authoring quality workflows. Especially useful for any systematic quality assessment process beyond just rules.

**Reuse Applications**: Framework compliance scanning, documentation assessment, configuration validation, security audits, or any domain requiring comprehensive quality evaluation with prioritized remediation.

---

**Created**: 2025-12-13
**Follows**: `.cursor/rules/rule-authoring/rule-authoring-overview.mdc` v1.0.0
**Enhanced**: 2025-12-13 (RULES-MAINTENANCE initiative)


