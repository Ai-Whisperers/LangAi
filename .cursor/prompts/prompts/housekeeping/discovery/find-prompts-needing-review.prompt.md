---
name: find-prompts-needing-review
description: "Please find prompts that need review based on quality criteria and maintenance needs"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Review criteria focus (optional: all, quality, integration, maintenance)"
category: housekeeping
tags: prompts, housekeeping, review, quality, maintenance, validation, analysis, scanning
---

# Find Prompts Needing Review

Please scan the prompt library and identify prompts that need review based on quality criteria, integration status, and maintenance requirements.

**Pattern**: Quality Assurance Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Critical for maintaining prompt library quality and preventing technical debt
**Use When**: Need to identify prompts requiring attention or improvement

---

## Enhancement Decision Tree

```
Need to assess prompt library health?
├─ YES → Continue with this prompt
└─ NO → Use specific prompt improvement tools

What type of assessment needed?
├─ Quality standards compliance → @find-prompts-needing-review quality
├─ Collection integration status → @find-prompts-needing-review integration
├─ Maintenance and updates → @find-prompts-needing-review maintenance
└─ Complete health check → @find-prompts-needing-review all

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

Identify prompts requiring review to ensure the prompt library maintains high quality and standards. This includes:
- Quality compliance checks
- Integration verification
- Maintenance and update needs
- Technical debt identification
- Improvement opportunities

---

## Required Context

- **Review Focus** (optional): Specific area to focus on
  - `quality`: Frontmatter and content standards
  - `integration`: Collection and reference completeness
  - `maintenance`: Updates, fixes, and technical debt
  - `all`: Comprehensive review (default)
- **Include Uncommitted**: Always include uncommitted prompt files (highest priority for review)

---

## Process

1. **Scan Prompt Library**
   - Examine all `.prompt.md` files in `.cursor/prompts/`
   - **Include uncommitted changes**: Check `git status` for staged/unstaged prompt files
   - Parse frontmatter and content structure for all files (committed and uncommitted)

2. **Apply Review Criteria**
   - Check frontmatter completeness and format
   - Validate content structure and quality
   - Verify collection integration
   - Assess maintenance status

3. **Categorize Issues**
   - **Critical**: Breaking issues requiring immediate fix
   - **Important**: Quality issues affecting usability
   - **Maintenance**: Updates and improvements needed

4. **Prioritize Findings**
   - Sort by severity and impact
   - Group by category and type
   - Identify quick wins vs major efforts

5. **Generate Report**
   - Detailed findings with specific issues
   - Actionable recommendations
   - Priority assignments

---

## Reasoning Process (for AI Agent)

When evaluating prompts for review:

1. **Quality First**: Critical issues (missing frontmatter, broken YAML) take priority
2. **Impact Assessment**: Consider how issues affect usability and maintenance
3. **Effort Estimation**: Balance severity with fix complexity
4. **Standards Compliance**: Ensure alignment with prompt creation and registry rules
5. **Maintenance Burden**: Identify prompts causing ongoing maintenance overhead

---

## Review Criteria

### Quality Issues
- **Frontmatter**: Missing required fields, invalid YAML, incorrect format
- **Content**: Missing sections, unclear instructions, poor examples
- **Standards**: Not following prompt creation rules
- **Documentation**: Missing references, outdated information

### Integration Issues
- **Collections**: Not included in appropriate collection manifests
- **References**: Missing cross-references to related prompts/rules
- **Registry**: Incompatible with Prompt Registry format
- **Dependencies**: Broken links or invalid references

### Maintenance Issues
- **Age**: Long time since last update (potential staleness)
- **Usage**: Low usage indicators or outdated patterns
- **Technical Debt**: Accumulated issues not addressed
- **Consistency**: Not aligned with current standards

---

## Examples (Few-Shot)

### Example 1: Comprehensive Quality Review

**Input**:
```
@find-prompts-needing-review all
```

**Expected Output**:
```markdown
## Prompts Needing Review Report

**Review Focus**: All criteria
**Total Prompts Analyzed**: 89
**Prompts Needing Attention**: 12 (13%)

### 🔴 Critical Issues (Fix Immediately - 2)

1. **incomplete-frontmatter.prompt.md**
   - **Issue**: Missing required 'description' field in YAML frontmatter
   - **Impact**: Cannot be loaded by Prompt Registry extension
   - **Fix**: Add description field: `description: "Please [brief purpose]"`

### 🟡 Important Issues (Fix Soon - 6)

1. **missing-examples.prompt.md**
   - **Issue**: No Examples section, making usage unclear
   - **Impact**: Users cannot understand expected input/output format
   - **Fix**: Add Examples section with 2-3 concrete scenarios

### 🔵 Maintenance Issues (Address When Convenient - 4)

1. **old-pattern.prompt.md**
   - **Issue**: Uses deprecated placeholder format `[VAR]` instead of `{{var}}`
   - **Impact**: Inconsistent with current prompt creation standards
   - **Fix**: Update to modern placeholder format

## Summary by Category

| Category | Total | Need Review | Percentage |
|----------|-------|-------------|------------|
| prompt | 15 | 3 | 20% |
| git | 12 | 2 | 17% |
| testing | 8 | 1 | 13% |

## Quick Wins (5-10 min fixes)
- Fix 2 YAML frontmatter issues
- Add 3 missing Examples sections

## Recommended Actions
1. **Immediate**: Fix critical YAML frontmatter issues (2 prompts)
2. **This Week**: Add missing Examples sections (6 prompts)
3. **This Month**: Address maintenance consistency issues
```

### Example 2: Focused Quality Check

**Input**:
```
@find-prompts-needing-review quality
```

**Expected Output**:
```markdown
## Prompts Needing Review Report

**Review Focus**: Quality criteria only
**Total Prompts Analyzed**: 89
**Prompts Needing Attention**: 8 (9%)

### 🔴 Critical Issues (Fix Immediately - 1)

1. **broken-yaml.prompt.md**
   - **Issue**: Invalid YAML frontmatter (incorrect indentation)
   - **Impact**: Cannot be parsed by Prompt Registry
   - **Fix**: Fix YAML indentation and format

### 🟡 Important Issues (Fix Soon - 7)

1. **vague-description.prompt.md**
   - **Issue**: Description too generic: "Check code quality"
   - **Impact**: Unclear purpose in auto-complete
   - **Fix**: Make specific: "Please analyze code for naming violations and complexity issues"

2. **missing-validation.prompt.md**
   - **Issue**: No Validation Checklist section
   - **Impact**: No quality assurance for output completeness
   - **Fix**: Add Validation Checklist with specific criteria
```

### Example 3: Integration Focus

**Input**:
```
@find-prompts-needing-review integration
```

**Expected Output**:
```markdown
## Prompts Needing Review Report

**Review Focus**: Integration criteria only
**Total Prompts Analyzed**: 89
**Prompts Needing Attention**: 5 (6%)

### 🟡 Important Issues (Fix Soon - 5)

1. **orphaned-prompt.prompt.md**
   - **Issue**: Not included in any collection manifest
   - **Impact**: Not available in Prompt Registry
   - **Fix**: Add to appropriate `.collection.yml` file

2. **broken-references.prompt.md**
   - **Issue**: References old rule file paths that were renamed
   - **Impact**: Broken links in Related Rules section
   - **Fix**: Update to current rule file paths
```

---

## Expected Output

```markdown
## Prompts Needing Review Report

**Review Focus**: All criteria
**Total Prompts Analyzed**: 147
**Prompts Needing Attention**: 23 (16%)

### 🔴 Critical Issues (Fix Immediately - 4)

1. **broken-prompt.prompt.md**
   - **Issue**: Invalid YAML frontmatter (missing quotes)
   - **Impact**: Cannot be loaded by Prompt Registry
   - **Fix**: Add quotes around description field

2. **missing-frontmatter.prompt.md**
   - **Issue**: No YAML frontmatter at all
   - **Impact**: Not recognized as prompt file
   - **Fix**: Add complete frontmatter with name/description

### 🟡 Important Issues (Fix Soon - 12)

1. **incomplete-examples.prompt.md**
   - **Issue**: Examples section has placeholders only
   - **Impact**: Users cannot understand usage
   - **Fix**: Add 2-3 concrete examples

2. **outdated-references.prompt.md**
   - **Issue**: References old rule files that were renamed
   - **Impact**: Broken links in documentation
   - **Fix**: Update to current rule paths

### 🔵 Maintenance Issues (Address When Convenient - 7)

1. **legacy-pattern.prompt.md**
   - **Issue**: Uses deprecated pattern from 2024
   - **Impact**: Not following current best practices
   - **Fix**: Update to modern pattern

## Summary by Category

| Category | Total | Need Review | Percentage |
|----------|-------|-------------|------------|
| agile | 12 | 2 | 17% |
| code-quality | 18 | 4 | 22% |
| documentation | 8 | 1 | 13% |
| git | 15 | 3 | 20% |
| housekeeping | 9 | 2 | 22% |

## Quick Wins (5-10 min fixes)
- Fix 3 YAML formatting issues
- Add missing argument-hint fields (4 prompts)
- Update 2 broken references

## Recommended Actions
1. **Immediate**: Fix 4 critical YAML/frontmatter issues
2. **This Week**: Address 8 important quality issues
3. **This Month**: Tackle maintenance improvements
4. **Create Tickets**: Major refactoring (3 prompts need significant rework)
```

---

## Validation Checklist

Before claiming review is complete:

- [ ] All `.prompt.md` files in `.cursor/prompts/` scanned
- [ ] Frontmatter validation completed (YAML format, required fields)
- [ ] Content structure analysis performed against prompt creation standards
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
@find-prompts-needing-review
```
or explicitly:
```
@find-prompts-needing-review all
```

### Focused Reviews
Target specific areas of concern:

**Quality Standards Check**:
```
@find-prompts-needing-review quality
```
*Checks frontmatter, content structure, clarity, and reusability*

**Integration Verification**:
```
@find-prompts-needing-review integration
```
*Validates collection membership and reference completeness*

**Maintenance Assessment**:
```
@find-prompts-needing-review maintenance
```
*Identifies outdated patterns and technical debt*

### Advanced Usage

**With Custom Context**:
```
@find-prompts-needing-review quality --include-drafts
```
*Include draft prompts in review (future enhancement)*

**Batch Processing**:
```
@find-prompts-needing-review all --output-format json
```
*Generate machine-readable output for automation (future enhancement)*

---

## Troubleshooting

**Issue**: No prompts found needing review
**Cause**: Very high quality standards or recent cleanup
**Solution**: Lower threshold or check if review criteria are too strict

**Issue**: Too many prompts flagged
**Cause**: Review criteria too broad or standards too high
**Solution**: Focus on specific categories or adjust criteria

**Issue**: Inconsistent results
**Cause**: Review criteria not applied uniformly
**Solution**: Document specific standards and ensure consistent application

---

## Success Metrics

### Quality Health Indicators

**Excellent** (Target: <5% need review):
- <5% of prompts need attention
- 0 critical issues
- <10% important issues
- Maintenance issues <20%

**Good** (Acceptable: 5-15% need review):
- 5-15% of prompts need attention
- 0 critical issues
- 10-20% important issues
- Maintenance issues <30%

**Needs Attention** (>15% need review):
- >15% of prompts need attention
- Critical issues present
- >20% important issues
- Maintenance issues >30%

### Improvement Velocity

**Track Progress**:
- Critical issues: Fix within 24 hours
- Important issues: Address within 1 week
- Maintenance issues: Ongoing improvement

**Measure Success**:
- **Time to fix**: Average time from identification to resolution
- **Prevention rate**: % of issues caught before user reports
- **User satisfaction**: Reduction in prompt-related support requests

---

## Integration with Quality Workflow

This prompt is part of the **Prompt Quality Assurance Pipeline**:

1. **Discovery**: `find-recently-added-prompts.prompt.md` - Identify new prompts
2. **Assessment**: `find-prompts-needing-review.prompt.md` - Evaluate quality and gaps
3. **Improvement**: `improve-prompt.prompt.md` - Fix critical issues and basic problems
4. **Enhancement**: `enhance-prompt.prompt.md` - Add advanced features and examples
5. **Validation**: `validate-prompt.prompt.md` - Confirm improvements work correctly

### Quality Gates
- **Gate 1**: No critical issues (YAML, missing fields) - Must pass before commit
- **Gate 2**: No important issues (examples, structure) - Should fix within 1 week
- **Gate 3**: Maintenance issues addressed - Ongoing improvement process

---

## Related Prompts

- `housekeeping/find-recently-added-prompts.prompt.md` - Find new prompts requiring initial review
- `prompt/improve-prompt.prompt.md` - Fix critical issues identified by this review
- `prompt/enhance-prompt.prompt.md` - Add advanced features after basic fixes
- `prompt/validate-prompt.prompt.md` - Verify improvements work correctly
- `housekeeping/validate-prompt-collections.prompt.md` - Check collection manifest integrity

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Quality standards for prompts
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Integration requirements
- `.cursor/rules/quality/code-quality-enforcement-rule.mdc` - Quality enforcement patterns
- `.cursor/rules/housekeeping/workflow-link-rule.mdc` - Maintenance workflow standards

---

## Extracted Patterns

This prompt demonstrates exceptional quality in systematic quality assurance and has been analyzed for reusable patterns:

**Templar Opportunity**:
- `.cursor/prompts/templars/housekeeping/systematic-quality-review-templar.md` - Multi-criteria assessment workflow with severity-based prioritization

**Exemplar Value**:
- `.cursor/prompts/exemplars/housekeeping/comprehensive-quality-assessment-exemplar.md` - Reference implementation of thorough quality scanning with actionable reporting

**Why Valuable**: Demonstrates advanced quality assurance patterns including multi-dimensional assessment (quality/integration/maintenance), severity-based issue categorization, effort estimation for prioritization, decision tree for appropriate usage, and integration with broader quality workflows. Especially useful for any systematic quality assessment process beyond just prompts.

**Reuse Applications**: Code quality scanning, documentation assessment, configuration validation, security audits, or any domain requiring comprehensive quality evaluation with prioritized remediation.

---

**Created**: 2025-12-13
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Enhanced**: 2025-12-13 (PROMPTS-MAINTENANCE initiative)
