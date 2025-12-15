# CRITICAL: YAML Format Issues Across All Rules

**Generated**: 2025-11-04
**Severity**: 🚨 **CRITICAL**
**Scope**: **46 out of 47 rules (98%)**

## Executive Summary

### 🚨 **CRITICAL FINDING**

Almost **ALL rules use incorrect YAML syntax** for `globs` and `governs` fields. They're using **JSON array format** instead of **proper YAML format**.

### Impact

**Functional**: Rules may not trigger correctly in Cursor
**Correctness**: 98% of rules have malformed front-matter
**Severity**: CRITICAL - affects core rule invocation

---

## The Problem

### ❌ **Current (WRONG) Format**

```yaml
---
id: rule.technical-specifications.domain-object.v1
globs: ["**/docs/technical/**/domain-objects/*.md", "**/docs/technical/**/*-domain-object.md"]
governs: ["**/docs/technical/**/domain-objects/*-domain-object.md"]
---
```

**Problems**:
- Using JSON array syntax `["..."]` in YAML file
- Mixing JSON with YAML (inconsistent)
- Quoted strings not necessary in YAML
- Flow-style arrays harder to read

### ✅ **Correct Format**

**Single pattern**:
```yaml
---
id: rule.example.v1
globs: **/pattern.md
governs: **/pattern.md
---
```

**Multiple patterns (YAML block-style array)**:
```yaml
---
id: rule.example.v1
globs:
  - **/docs/technical/**/domain-objects/*.md
  - **/docs/technical/**/*-domain-object.md
governs:
  - **/docs/technical/**/domain-objects/*-domain-object.md
---
```

---

## Evidence

### ✅ The ONE Rule That's Correct

**File**: `.cursor/rules/ticket/ticket-rule.mdc`

```yaml
---
globs: tickets/*.md
alwaysApply: false
---
```

**Why correct**: Plain YAML, no JSON arrays, no unnecessary quotes

### ❌ All Other Rules (46/47)

**Example**: `.cursor/rules/technical-specifications/domain-object-rule.mdc`

```yaml
---
globs: ["**/docs/technical/**/domain-objects/*.md", "**/docs/technical/**/*-domain-object.md"]
governs: ["**/docs/technical/**/domain-objects/*-domain-object.md"]
---
```

**Why wrong**: JSON array syntax in YAML file

---

## Affected Rules by Domain

### Domain: rule-authoring (11/11 rules)

ALL use JSON array format:

| Rule File | globs Format | governs Format |
|-----------|--------------|----------------|
| rule-file-structure.mdc | ❌ JSON array | ❌ JSON array |
| rule-naming-conventions.mdc | ❌ JSON array | ❌ JSON array |
| rule-contracts-and-scope.mdc | ❌ JSON array | ❌ JSON array |
| rule-cross-references.mdc | ❌ JSON array | ❌ JSON array |
| rule-templars-and-exemplars.mdc | ❌ JSON array | ❌ JSON array |
| rule-provenance-and-versioning.mdc | ❌ JSON array | ❌ JSON array |
| rule-validation-and-checklists.mdc | ❌ JSON array | ❌ JSON array |
| rule-extraction-from-practice.mdc | ❌ JSON array | ❌ JSON array |
| rule-authoring-overview.mdc | ❌ JSON array | ❌ JSON array |
| rule-invocation-strategies.mdc | ❌ JSON array | ❌ JSON array |
| agent-application-rule.mdc | N/A (Strategy 2) | N/A (Strategy 2) |

**Domain Compliance**: 0/11 (0%)

### Domain: agile (5/6 rules)

| Rule File | globs Format | governs Format |
|-----------|--------------|----------------|
| epic-documentation-rule.mdc | ❌ JSON array | ❌ JSON array |
| business-feature-documentation-rule.mdc | ❌ JSON array | ❌ JSON array |
| technical-feature-documentation-rule.mdc | ❌ JSON array | ❌ JSON array |
| user-story-documentation-rule.mdc | ❌ JSON array | ❌ JSON array |
| story-splitting-rule.mdc | ❌ JSON array | ❌ JSON array |
| agent-application-rule.mdc | N/A (Strategy 2) | N/A (Strategy 2) |

**Domain Compliance**: 0/6 (0%)

### Domain: migration (5/5 rules)

| Rule File | globs Format | governs Format |
|-----------|--------------|----------------|
| migration-overview.mdc | ❌ JSON array | ❌ JSON array |
| phase-1-data-collection.mdc | ❌ JSON array | ❌ JSON array |
| phase-2-specification-creation.mdc | ❌ JSON array | ❌ JSON array |
| phase-2b-specification-review.mdc | ❌ JSON array | ❌ JSON array |
| phase-3-migration-planning.mdc | ❌ JSON array | ❌ JSON array |

**Domain Compliance**: 0/5 (0%)

### Domain: technical-specifications (10/11 rules)

| Rule File | globs Format | governs Format |
|-----------|--------------|----------------|
| README.md (overview) | ❌ JSON array | ❌ JSON array |
| domain-object-rule.mdc | ❌ JSON array | ❌ JSON array |
| enumeration-rule.mdc | ❌ JSON array | ❌ JSON array |
| business-rules-rule.mdc | ❌ JSON array | ❌ JSON array |
| entity-relationship-rule.mdc | ❌ JSON array | ❌ JSON array |
| domain-overview-rule.mdc | ❌ JSON array | ❌ JSON array |
| integration-points-rule.mdc | ❌ JSON array | ❌ JSON array |
| documentation-architecture-rule.mdc | ❌ JSON array | ❌ JSON array |
| hybrid-documentation-architecture-rule.mdc | ❌ JSON array | ❌ JSON array |
| specification-anti-duplication-rule.mdc | ❌ JSON array | ❌ JSON array |
| agent-application-rule.mdc | N/A (Strategy 2) | N/A (Strategy 2) |

**Domain Compliance**: 0/11 (0%)

### Domain: ticket (13/14 rules)

| Rule File | globs Format | governs Format |
|-----------|--------------|----------------|
| **ticket-rule.mdc** | ✅ **Plain YAML** | N/A |
| ticket-rules-index.mdc | ❌ JSON array | ❌ JSON array |
| ticket-workflow-rule.mdc | ❌ JSON array | ❌ JSON array |
| plan-rule.mdc | ❌ JSON array | ❌ JSON array |
| context-rule.mdc | ❌ JSON array | ❌ JSON array |
| progress-rule.mdc | ❌ JSON array | ❌ JSON array |
| recap-rule.mdc | ❌ JSON array | ❌ JSON array |
| rca-rule.mdc | ❌ JSON array | ❌ JSON array |
| complexity-assessment-rule.mdc | ❌ JSON array | ❌ JSON array |
| switching-discipline.mdc | ❌ JSON array | ❌ JSON array |
| ai-completion-discipline.mdc | ❌ JSON array | ❌ JSON array |
| validation-before-completion-rule.mdc | ❌ JSON array | ❌ JSON array |
| timeline-tracking-rule.mdc | ❌ JSON array | ❌ JSON array |
| timeline-workflow-integration.mdc | ⚠️ Empty | N/A |
| agent-application-rule.mdc | N/A (Strategy 2) | N/A (Strategy 2) |

**Domain Compliance**: 1/14 (7%)

---

## Overall Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Rules Validated | 47 | 100% |
| Rules with Strategy 2 (no globs/governs) | 4 | 8.5% |
| Rules that SHOULD have globs/governs | 43 | 91.5% |
| **Rules with CORRECT format** | **1** | **2%** |
| **Rules with WRONG format** | **42** | **98%** |

**Note**: 1 rule (timeline-workflow-integration.mdc) has empty globs field, not counted as either correct or wrong.

---

## Root Cause Analysis

### Why JSON Arrays Were Used

Likely causes:

1. **JSON familiarity**: Developers more familiar with JSON than YAML
2. **Initial template**: First rule used this format, others copied it
3. **No validation**: No automated check for proper YAML format
4. **YAML flexibility**: YAML accepts JSON as subset, so it "works" (maybe)
5. **No examples**: `ticket-rule.mdc` (the correct one) was created later

### Why It Matters

**YAML vs JSON in YAML files**:

YAML is a superset of JSON, so JSON arrays are technically *valid* YAML. However:

1. **Style Inconsistency**: Mixing JSON in YAML is bad practice
2. **Readability**: YAML block style is more readable
3. **Cursor Expectations**: Cursor may expect pure YAML, not JSON-in-YAML
4. **Parsing Issues**: Some YAML parsers handle this differently
5. **Professional Standards**: Production YAML should use YAML syntax

---

## Impact Assessment

### Functional Impact: 🚨 **CRITICAL - UNKNOWN**

**Potential Issues**:
- ❓ Rules may not trigger at all
- ❓ Rules may trigger incorrectly
- ❓ Cursor may not parse front-matter correctly
- ❓ File pattern matching may fail

**Testing Needed**:
- Verify if rules actually work with current format
- Test if Cursor parses JSON arrays in globs/governs
- Check if any rules are failing to trigger

### Code Quality Impact: ❌ **HIGH**

- **Style Violation**: JSON syntax in YAML files
- **Inconsistency**: 46 rules use JSON, 1 uses YAML
- **Maintainability**: Mixed styles confusing for contributors
- **Best Practices**: Violates YAML coding standards

### Documentation Impact: ❌ **HIGH**

- **Bad Examples**: 46 rules show wrong format
- **Learning**: New rule authors will copy wrong format
- **Framework Integrity**: Rule-authoring framework shows wrong examples
- **Validation Reports**: Don't mention this issue at all

---

## Recommended Fix

### Approach: Systematic YAML Conversion

Convert all rules from JSON array format to proper YAML format.

### Single Pattern Conversion

**Before** (JSON array):
```yaml
globs: ["**/plan.md"]
governs: ["**/plan.md"]
```

**After** (YAML):
```yaml
globs: **/plan.md
governs: **/plan.md
```

### Multiple Patterns Conversion

**Before** (JSON array):
```yaml
globs: ["**/plan.md", "**/context.md", "**/timeline.md"]
governs: ["**/plan.md"]
```

**After** (YAML block-style):
```yaml
globs:
  - **/plan.md
  - **/context.md
  - **/timeline.md
governs: **/plan.md
```

### Empty Array Conversion

**Before** (JSON empty array):
```yaml
governs: []
```

**After** (YAML empty array or omit):
```yaml
governs: []  # Keep as-is, this is valid YAML
# OR omit entirely if semantically appropriate
```

**Note**: Empty array `[]` is valid YAML and commonly used for read-only rules.

---

## Combined Remediation Plan

### Issues Discovered

1. ❌ Missing `alwaysApply` field (45/47 rules - 96%)
2. ❌ Wrong `globs` format - JSON arrays instead of YAML (42/43 rules with globs - 98%)
3. ❌ Wrong `governs` format - JSON arrays instead of YAML (42/43 rules with governs - 98%)

### Remediation Phases

#### Phase 1: Update Rule Authoring Framework

**File**: `rule.authoring.file-structure.v1`

**Actions**:
1. Add `alwaysApply` as 11th required field
2. Update canonical schema to show proper YAML format for globs/governs
3. Add examples with both single and multiple patterns
4. Add explicit "DON'T USE JSON ARRAYS" warning

**Example canonical schema**:
```yaml
---
id: rule.[domain].[action].v[major]
kind: rule
version: [semver]
description: [one sentence]
globs: **/[pattern].md  # Single pattern (no quotes, no brackets)
# OR for multiple patterns:
# globs:
#   - **/[pattern1].md
#   - **/[pattern2].md
governs: **/[pattern].md  # Same format as globs
implements: [action]
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: [team], last_review: [date] }
alwaysApply: false  # Explicit invocation control
---
```

**Version**: 1.0.0 → 1.1.0 (MINOR - adds field + clarifies format)

#### Phase 2: Fix All Rules Systematically

For EACH of the 42 affected rules:

1. **Convert globs format**:
   - Single pattern: Remove `[""]` → plain value
   - Multiple patterns: Convert to YAML block-style array

2. **Convert governs format**:
   - Same as globs

3. **Add alwaysApply field**:
   - Add `alwaysApply: false` after provenance

4. **Version bump**:
   - PATCH: x.y.z → x.y.z+1 (non-behavioral formatting fix)
   - Update provenance.last_review to 2025-11-04

#### Phase 3: Update Documentation

1. Update all validation reports
2. Update rule-authoring examples
3. Create migration guide showing before/after
4. Document lessons learned

---

## Effort Estimate

### Per-Rule Effort

**Each rule requires**:
- Convert globs format (1-2 min)
- Convert governs format (1-2 min)
- Add alwaysApply field (30 sec)
- Update version + provenance (30 sec)
- Validate correct YAML (30 sec)

**Total per rule**: ~5 minutes

### Domain Breakdown

| Domain | Rules to Fix | Effort |
|--------|--------------|--------|
| rule-authoring | 10 | 50 min |
| agile | 5 | 25 min |
| migration | 5 | 25 min |
| technical-specifications | 10 | 50 min |
| ticket | 12 | 60 min |
| **TOTAL** | **42** | **210 min (3.5 hours)** |

### Additional Tasks

- Update file-structure.v1: 15 min
- Update validation reports: 30 min
- Testing/validation: 30 min

**Grand Total**: ~4.5 hours

---

## Priority and Urgency

### Priority: 🚨 **CRITICAL**

**Rationale**:
1. Affects 98% of all rules
2. May cause functional failures (rules not triggering)
3. Framework integrity compromised
4. Bad examples propagating to new rules

### Urgency: **HIGH**

**Recommended Timeline**:
- **Immediate**: Verify if current format causes functional issues
- **This week**: Fix all rules if functional issues confirmed
- **This sprint**: Fix all rules even if no immediate functional issues (code quality)

---

## Testing Strategy

### Before Mass Update

**Test current format**:
1. Pick 3 rules with JSON array format
2. Trigger them in Cursor
3. Verify they actually work
4. Check Cursor logs for parsing warnings

**If they work**: Lower urgency (style issue only)
**If they don't work**: Maximum urgency (functional issue)

### After Update

**Test YAML format**:
1. Convert 3 test rules to proper YAML
2. Trigger them in Cursor
3. Verify they work correctly
4. Compare behavior to pre-conversion

### Rollout Strategy

1. **Pilot**: Fix rule-authoring domain first (10 rules)
2. **Test**: Verify rule-authoring rules work
3. **Rollout**: Fix remaining domains
4. **Validate**: Full regression test

---

## Lessons Learned

### What Went Wrong ❌

1. **No Format Validation**: No automated check for YAML style
2. **Bad Template**: Initial rules used JSON format, propagated via copy-paste
3. **No Review**: Code reviews didn't catch style inconsistency
4. **Missing Documentation**: file-structure.v1 didn't specify YAML vs JSON

### How to Prevent ✅

1. **Automated Validation**: Add YAML linter checking for JSON arrays
2. **Clear Examples**: file-structure.v1 must show correct format explicitly
3. **Pre-commit Hooks**: Validate YAML format before allowing commits
4. **Documentation**: Add "Common Mistakes" section showing wrong formats
5. **Template Files**: Provide correct template files for new rules

---

## Decision Required

### Option A: Fix Immediately (Recommended)

**Pros**:
- Eliminates technical debt
- Ensures all rules follow standards
- Professional code quality
- Prevents propagation

**Cons**:
- 4.5 hours effort
- 42 file changes
- Risk of introducing errors

**Recommendation**: ✅ **DO THIS**

### Option B: Fix Only If Broken

**Pros**:
- Lower immediate effort
- If it works, don't fix it

**Cons**:
- Technical debt remains
- Bad examples continue
- Eventually must fix anyway
- Style inconsistency persists

**Recommendation**: ❌ **DON'T DO THIS**

### Option C: Fix Gradually

**Pros**:
- Spread effort over time
- Fix as you touch files

**Cons**:
- Inconsistency persists long-term
- New rules may copy old format
- Framework lacks integrity

**Recommendation**: ❌ **DON'T DO THIS**

---

## Conclusion

**Status**: 🚨 **CRITICAL CODE QUALITY ISSUE**

**Scope**: 42 out of 43 rules with globs/governs use wrong format (98%)

**Recommendation**: **Systematic conversion to proper YAML format**

**Effort**: 4.5 hours total

**Priority**: HIGH

**Next Action**: **Approve systematic fix and begin implementation**

---

**Validation Date**: 2025-11-04
**Validator**: AI Assistant (Cursor/Claude)
**Discovery**: User identified format issue, validation confirmed scope
**Status**: Awaiting approval to implement systematic fix

