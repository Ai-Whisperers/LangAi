---
name: sync-rules-between-repos
description: "Please systematically sync rules between repositories with automated comparison and validation"
category: rule-authoring
tags: rules, sync, repositories, consistency
argument-hint: "[source-repo] [target-repo]"
---

# Sync Rules Between Repositories

Systematically synchronize rule files between repositories to propagate improvements and maintain consistency.

**Required Context**:
<source_repository>
[SOURCE_REPO_PATH]  # e.g., eneve.ebase.foundation
</source_repository>

<target_repository>
[TARGET_REPO_PATH]  # e.g., eneve.domain
</target_repository>

**Sync Parameters**:
- **Scope**: [SYNC_SCOPE]  # all | domain-specific | selective
- **Strategy**: [SYNC_STRATEGY]  # full-domain | selective | incremental | bidirectional
- **Domain** (if domain-specific): [DOMAIN_NAME]  # e.g., ticket, migration, authoring

**Follows Standards From**:
- `.cursor/rules/rule-authoring/rule-sync-rule.mdc` - Complete 8-step sync process
- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Rule structure validation
- `.cursor/rules/rule-authoring/provenance-and-versioning.mdc` - Version comparison logic

**Automation Scripts** (for efficiency):
- `.cursor/prompts/rule-authoring/scripts/compare-rules.ps1` - Automated rule comparison and analysis
- `.cursor/prompts/rule-authoring/scripts/validate-sync.ps1` - Post-sync validation and integrity checks

**Usage**:
```powershell
# Step 1: Run comparison analysis
cd [SOURCE_REPO_ROOT]
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\compare-rules.ps1

# Step 2: Review generated report and CSV
# Opens: rule-sync-analysis.csv

# Step 3: Execute sync (manual file copies based on analysis)

# Step 4: Run validation
cd [TARGET_REPO_ROOT]
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\validate-sync.ps1
```

## Reasoning Process

Before executing sync:
1. **Understand repositories**: Identify which is authoritative/newer
2. **Assess sync scope**: Determine if full domain or selective sync is appropriate
3. **Plan conflict resolution**: Decide strategy for Category C conflicts
4. **Validate safety**: Ensure no OPSEC violations or broken dependencies
5. **Plan rollback**: Know how to revert if sync causes issues

## Sync Process

### Step 1: Discover Rules in Both Repositories

**Automated Option** (Recommended):
```powershell
cd [SOURCE_REPO_ROOT]
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\compare-rules.ps1
```

This script automatically:
- Scans both source and target repositories
- Extracts all rule files (`**/*.mdc`)
- Parses front-matter (ID, version, last_review)
- Generates categorized analysis report
- Exports detailed CSV for review

**Manual Option** (if automation unavailable):
1. **Scan Source Repository**:
   - Directory: `.cursor/rules/` in source repo
   - Extract all rule files (`**/*-rule.mdc`)
   - Parse front-matter: ID, version, provenance
   - Build source rule registry

2. **Scan Target Repository**:
   - Directory: `.cursor/rules/` in target repo
   - Extract all rule files (`**/*-rule.mdc`)
   - Parse front-matter: ID, version, provenance
   - Build target rule registry

### Step 2: Compare and Categorize

Analyze differences and categorize each rule:

**Category A: Rules to Add** (missing in target)
- Present in source, not in target
- Action: Copy entire rule file

**Category B: Rules to Update** (version differences)
- Source version > Target version
- No local modifications in target
- Action: Replace target with source

**Category C: Rules to Review** (conflicts)
- Both modified since last sync
- Different `last_review` dates
- Action: Manual review required

**Category D: Rules in Sync** (already current)
- Same version or target newer
- Action: No sync needed

### Step 3: Generate Sync Analysis Report

Create comprehensive report:

```markdown
# Rule Sync Analysis

**Source**: [source repo path]
**Target**: [target repo path]
**Analysis Date**: [YYYY-MM-DD HH:MM UTC]

## Summary

- Rules to Add: [count]
- Rules to Update: [count]
- Rules to Review: [count]
- Rules in Sync: [count]

## Rules to Add (Category A)

| Rule ID | Source Version | Domain | Action |
|---------|----------------|--------|--------|
| [list each] | [version] | [domain] | Add |

## Rules to Update (Category B)

| Rule ID | Source Version | Target Version | Last Modified | Action |
|---------|----------------|----------------|---------------|--------|
| [list each] | [src ver] | [tgt ver] | [date] | Update |

## Rules to Review (Category C)

| Rule ID | Source Version | Target Version | Source Modified | Target Modified |
|---------|----------------|----------------|-----------------|-----------------|
| [list each] | [src ver] | [tgt ver] | [src date] | [tgt date] |

## Rules in Sync (Category D)

[count] rules are already in sync.
```

### Step 4: Execute Sync (After Review)

For each rule in Categories A and B:

1. **Validate Source Rule**:
   - Check front-matter completeness
   - Verify canonical structure
   - Run validation checklist

2. **Prepare Target**:
   - Create directory structure if needed
   - Backup existing file (if updating)

3. **Copy Rule File**:
   - Copy entire file from source to target
   - Preserve structure and content exactly

4. **Validate in Target Context**:
   - Check dependencies resolve
   - Verify globs/governs patterns
   - Check for ID conflicts

5. **Log Sync Action**:
   - Record in sync log

### Step 5: Handle Conflicts (Category C)

For conflicting rules:

1. **Present Both Versions**:
   - Show source version changes
   - Show target version changes
   - Highlight differences

2. **Request Decision**:
   - Option 1: Keep source (overwrite)
   - Option 2: Keep target (skip)
   - Option 3: Manual merge
   - Option 4: Create v2 (both coexist)

3. **Execute Decision**:
   - Perform chosen action
   - Document in sync log

### Step 6: Sync Related Assets

After syncing rules:

- **Templars**: Sync if referenced by rules
- **Exemplars**: Sync if referenced by rules
- **Dependencies**: Ensure all required rules present

### Step 7: Validate Sync Integrity

**Automated Validation** (Recommended):
```powershell
cd [TARGET_REPO_ROOT]
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\validate-sync.ps1
```

This script automatically:
- Verifies all synced files exist
- Validates front-matter presence and syntax
- Checks version numbers match expected values
- Confirms total rule count (100 rules)
- Reports PASS/FAIL for each validation

**Manual Validation** (if automation unavailable):

1. **Validate All Synced Rules**:
   - Parse front-matter
   - Check structure
   - Resolve dependencies

2. **Check References**:
   - Verify ID-based references resolve
   - Flag broken dependencies

3. **Generate Validation Report**

### Step 8: Document Sync

Create sync log in target repository:

```markdown
# Rule Sync Log

## Sync Session: [YYYY-MM-DD HH:MM UTC]

**Source**: [source repo]
**Target**: [target repo]
**Performed by**: [user/agent]

### Rules Added

- `rule.x.y.v1` (1.0.0) - Added to [domain]/
- [list all added]

### Rules Updated

- `rule.p.q.v1` - Updated from 1.0.0 to 1.2.0
- [list all updated]

### Rules Reviewed/Merged

- `rule.c.d.v1` - [decision and rationale]
- [list all reviewed]

### Validation Status

- ✅ All synced rules validated successfully
- ✅ No broken dependencies
- ✅ No ID conflicts

### Next Review

Recommended next sync: [YYYY-MM-DD] (30 days)
```

## Sync Strategies

**Choose one based on needs:**

### Strategy 1: Full Domain Sync
- **Use when**: Initial sync of entire domain
- **Process**: Compare all rules in domain folder
- **Time**: 1-2 hours

### Strategy 2: Selective Rule Sync
- **Use when**: Syncing specific improved rules
- **Process**: Identify and compare specific rules only
- **Time**: 15-30 minutes per rule

### Strategy 3: Incremental Sync
- **Use when**: Regular maintenance updates
- **Process**: Compare only modified rules since last sync
- **Frequency**: Weekly or monthly

### Strategy 4: Bidirectional Sync
- **Use when**: Both repos actively developing rules
- **Process**: Sync both directions based on latest versions
- **Complexity**: Higher, requires conflict resolution

## Validation Checklist

Before executing sync:

- [ ] Source rules validated (pass rule.authoring.file-structure.v1)
- [ ] Version comparison uses semantic versioning
- [ ] Category C conflicts require manual review (not auto-resolved)
- [ ] All dependencies will be present in target
- [ ] OPSEC validated (no secrets/tokens/URLs/emails)
- [ ] Repository-specific rules excluded (respect sync: local-only)
- [ ] Backup created of target rules (if updating)

## OPSEC Checks

Before syncing, verify:

- [ ] NO repository-specific paths (use relative paths only)
- [ ] NO credentials or tokens
- [ ] NO email addresses
- [ ] NO internal URLs
- [ ] NO sensitive example data in exemplars

## Deliverables

1. **Sync Analysis Report** (before executing sync)
2. **Updated Target Repository** (with synced rules)
3. **Sync Log** (documenting what was synced)
4. **Validation Report** (confirming compliance)

Save sync log to: `[target-repo]/.cursor/rules/sync-log.md` (append-only)

## Notes

- **Review before executing**: Always review sync analysis report before proceeding
- **Test in target context**: Synced rules may behave differently in different repos
- **Maintain audit trail**: Log all sync actions for traceability
- **Repository-specific exclusions**: Some rules should not be synced (marked with `sync: local-only`)
- **Conflict resolution**: Category C requires explicit human decision

## Related Resources

- `.cursor/rules/rule-authoring/rule-sync-rule.mdc` - Complete 8-step sync process with strategies
- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Rule structure validation
- `.cursor/rules/rule-authoring/rule-provenance-and-versioning.mdc` - Version comparison logic
- `.cursor/rules/rule-authoring/rule-validation-and-checklists.mdc` - Post-sync validation
- `.cursor/prompts/rule-authoring/create-new-rule.md` - Creating rules (if needed during merge)
- `.cursor/prompts/rule-authoring/validate-rule-compliance.md` - Validating synced rules

**Save Results To**:
- Sync analysis: Present in conversation or save to temp file
- Sync log: `[TARGET_REPO]/.cursor/rules/sync-log.md` (append-only)
- Updated rules: `[TARGET_REPO]/.cursor/rules/[domain]/` (in-place update)

---

**Estimated Time**:
- Full domain sync: 1-2 hours
- Selective sync: 15-30 minutes per rule
- Incremental sync: 30-60 minutes

**Note**: This sync workflow ensures consistency across repositories while respecting local modifications and preventing data leaks.
