---
name: run-housekeeping-orchestrator
description: "Please discover and execute all housekeeping tasks automatically as a single-entry point"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Execution mode (monthly, quarterly, full, discovery-only, execute-only)"
category: housekeeping
tags: housekeeping, maintenance, automation, discovery, execution, quality
---

# Run Housekeeping Orchestrator

Single-entry point to discover and execute all housekeeping tasks automatically.

**Pattern**: Orchestration Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for automated maintenance workflows
**Use When**: Need comprehensive housekeeping without manual prompt cycling

## Purpose

This prompt eliminates the need to manually cycle through individual housekeeping prompts by providing a single entry point that:

- **Discovers** what housekeeping tasks are needed
- **Prioritizes** tasks by urgency and dependency
- **Executes** appropriate prompts in the correct order
- **Reports** comprehensive results with next steps

Use this instead of running individual prompts like `@find-recently-added-prompts`, `@update-cross-references`, etc.

## Required Context

- **Repository Path**: `[REPO_PATH]` (defaults to current working directory)
- **Execution Mode**: `[MODE]` - One of: `full`, `monthly`, `quarterly`, `discovery-only`, `execute-only`

## Optional Parameters

- **Target Folders**: `[TARGET_FOLDERS]` (comma-separated, defaults to `.cursor/`)
- **Skip Categories**: `[SKIP_CATEGORIES]` (comma-separated: `maintenance,cleanup,discovery,extraction,sync`)
- **Dry Run Mode**: `[DRY_RUN]` (true/false, defaults to false)

## Reasoning Process

1. **Assess Scope**: Determine which housekeeping categories and prompts to run based on mode
2. **Discovery Phase**: Run discovery prompts to identify what needs attention
3. **Prioritization**: Sort findings by urgency (broken links > duplicates > extraction opportunities)
4. **Execution Planning**: Create execution plan based on findings and mode constraints
5. **Safe Execution**: Execute prompts in dependency order, with error handling
6. **Reporting**: Provide comprehensive summary of actions taken and recommendations

## Process

### Phase 1: Initialization and Discovery

1. **Validate Environment**:
   - Confirm repository structure exists
   - Check for required housekeeping prompt files
   - Verify write permissions for target folders

2. **Run Discovery Suite**:
   - Execute all discovery category prompts
   - Collect findings in structured format
   - Identify urgent issues (broken links, security issues)

3. **Analyze Current State**:
   - Check last housekeeping run timestamp
   - Review pending tasks from previous runs
   - Assess repository health metrics

### Phase 2: Planning and Prioritization

1. **Categorize Findings**:
```text
🔴 Critical: Must fix immediately (broken links, security issues)
🟡 Important: Should fix soon (duplicates, missing patterns)
🔵 Optional: Nice to have (optimizations, cleanup)
```

2. **Create Execution Plan**:
   - Order tasks by dependency (fix links before extraction)
   - Group related tasks (consolidate duplicates together)
   - Estimate time requirements

3. **Apply Mode Filters**:
   - `monthly`: Maintenance + recent discovery + extraction
   - `quarterly`: Full cleanup + sync + archival
   - `full`: All categories
   - `discovery-only`: Discovery phase only
   - `execute-only`: Skip discovery, use previous findings

### Phase 3: Safe Execution

1. **Execute by Priority**:
   - Critical issues first
   - Create backups before destructive operations
   - Batch related operations

2. **Error Handling**:
   - Continue on individual prompt failures
   - Log errors for manual review
   - Provide rollback guidance for failed operations

3. **Progress Tracking**:
   - Real-time status updates
   - Pause/resume capability
   - Detailed execution logs

### Phase 4: Validation and Reporting

1. **Validate Results**:
   - Re-run discovery to confirm improvements
   - Check quality metrics against baselines
   - Verify no regressions introduced

2. **Generate Reports**:
   - Execution summary with before/after metrics
   - Recommendations for next run
   - Identified issues requiring manual attention

3. **Schedule Next Run**:
   - Update housekeeping schedule
   - Set reminders for follow-up tasks

## Usage

**Monthly Maintenance**:
```
@run-housekeeping-orchestrator --mode monthly
```

**Quarterly Comprehensive Cleanup**:
```
@run-housekeeping-orchestrator --mode quarterly --dry-run true
```

**Full Repository Audit**:
```
@run-housekeeping-orchestrator --mode full --target-folders .cursor/rules,.cursor/prompts
```

**Discovery Only (Planning)**:
```
@run-housekeeping-orchestrator --mode discovery-only
```

## Examples

### Monthly Maintenance Run

**Input**:
```bash
@run-housekeeping-orchestrator \
  --mode monthly \
  --repo-path /path/to/eneve.domain \
  --target-folders .cursor/rules,.cursor/prompts
```

**Reasoning**:
Monthly mode focuses on regular upkeep and incremental improvements. This includes checking for broken links, reviewing recent additions, and extracting any new patterns found.

**Expected Execution**:
1. Run `find-recently-added-prompts` (30d)
2. Run `update-cross-references` on target folders
3. Run `find-extraction-candidates` on target folders
4. Execute `extract-templar-exemplar` for identified candidates
5. Run `validate-prompt-collections`
6. Generate monthly housekeeping report

### Quarterly Cleanup Run

**Input**:
```bash
@run-housekeeping-orchestrator \
  --mode quarterly \
  --repo-path /path/to/eneve.domain \
  --dry-run true
```

**Reasoning**:
Quarterly mode includes comprehensive cleanup operations. Dry run allows review of planned actions before execution.

**Expected Execution**:
1. Run all discovery prompts
2. Execute `consolidate-duplicates` on all target folders
3. Execute `archive-obsolete-artifacts` on entire `.cursor/` folder
4. Execute `find-dead-templars-exemplars` for cleanup
5. Run sync operations if multi-repo setup detected
6. Generate quarterly housekeeping report with metrics

### Full Comprehensive Run

**Input**:
```bash
@run-housekeeping-orchestrator \
  --mode full \
  --repo-path /path/to/eneve.domain \
  --skip-categories sync \
  --target-folders .cursor/
```

**Reasoning**:
Full mode runs everything except explicitly skipped categories. This is comprehensive maintenance.

**Expected Execution**:
All prompts from all non-skipped categories, executed in dependency order with comprehensive reporting.

### Real-World Example: Monthly Repository Maintenance

**Scenario**: Developer needs to perform routine monthly housekeeping without spending hours manually running individual prompts.

**Input**:
```bash
@run-housekeeping-orchestrator --mode monthly --target-folders .cursor/rules,.cursor/prompts
```

**What Happens**:
1. **Discovery Phase**: Automatically finds 3 recently added prompts, 2 broken cross-references, and 5 potential extraction candidates
2. **Planning Phase**: Prioritizes broken links as critical, schedules extraction for remaining time
3. **Execution Phase**: Fixes broken links, extracts 3 new templars from recent artifacts
4. **Reporting Phase**: Generates report showing improved quality metrics

**Result**: 45-minute comprehensive maintenance completed automatically, with full traceability and next-steps recommendations.

### Real-World Example: Quarterly Deep Cleanup

**Scenario**: Team lead needs to perform comprehensive cleanup before major release, but wants to review actions first.

**Input**:
```bash
@run-housekeeping-orchestrator --mode quarterly --dry-run true
```

**What Happens**:
1. **Discovery Phase**: Scans entire repository, identifies 15 duplicates, 8 obsolete artifacts, and 12 extraction opportunities
2. **Planning Phase**: Creates detailed execution plan with time estimates and dependency ordering
3. **Dry Run Report**: Shows exactly what would be done without making changes
4. **Review Opportunity**: Team can review plan before executing with `--dry-run false`

**Result**: Safe planning phase allows informed decision-making, prevents surprises during actual cleanup.

## Usage Modes

### Automated Mode (Default)
**Use**: Regular maintenance schedules
```
@run-housekeeping-orchestrator --mode monthly
```
- Discovers issues automatically
- Executes fixes immediately
- Generates comprehensive reports

### Planning Mode (Dry Run)
**Use**: Before major changes or team reviews
```
@run-housekeeping-orchestrator --mode quarterly --dry-run true
```
- Shows what would be done without changes
- Provides time estimates and risk assessment
- Enables informed decision-making

### Discovery Only Mode
**Use**: Assessment and planning
```
@run-housekeeping-orchestrator --mode discovery-only
```
- Only runs discovery prompts
- No changes made to repository
- Generates assessment reports

### Execute Only Mode
**Use**: When you already know what needs doing
```
@run-housekeeping-orchestrator --mode execute-only --target-folders .cursor/rules
```
- Skips discovery phase
- Uses previous findings or manual specification
- Executes specified maintenance tasks

### Selective Mode
**Use**: Focus on specific areas
```
@run-housekeeping-orchestrator --mode full --skip-categories sync --target-folders .cursor/prompts
```
- Customize which categories to run
- Target specific folders
- Exclude categories not needed

## Expected Output

### Execution Report Format

```text
# Housekeeping Execution Report
**Date**: 2025-12-13
**Mode**: [MODE]
**Repository**: [REPO_PATH]
**Duration**: [X minutes]

## Discovery Results

### Critical Issues Found
- 🔴 [Count] broken cross-references
- 🔴 [Count] security vulnerabilities
- 🔴 [Count] missing critical files

### Important Findings
- 🟡 [Count] duplicate artifacts
- 🟡 [Count] extraction candidates
- 🟡 [Count] outdated patterns

### Optional Improvements
- 🔵 [Count] condensation candidates
- 🔵 [Count] workflow optimizations

## Actions Taken

### ✅ Completed Successfully
- Fixed [X] broken links in [folder]
- Consolidated [Y] duplicate artifacts
- Extracted [Z] new patterns
- Archived [W] obsolete items

### ⚠️ Completed with Warnings
- [Item]: [Warning details]

### ❌ Failed Operations
- [Item]: [Error details] - [Recovery steps]

## Quality Metrics

### Before/After Comparison
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Broken Links | 15 | 0 | ✅ Fixed |
| Duplicate Artifacts | 8 | 3 | 🟡 Reduced |
| Pattern Coverage | 75% | 82% | ✅ Improved |

## Recommendations for Next Run

### Immediate (< 1 week)
- [Specific recommendations]

### Soon (< 1 month)
- [Monthly recommendations]

### Later (< 3 months)
- [Quarterly recommendations]

## Files Modified
- [List of all files changed with brief descriptions]

---
**Next Scheduled Run**: [Date based on mode]
**Report Saved To**: housekeeping/reports/[timestamp]-report.md
```

### Execution Log Format

```text
🔍 PHASE 1: Discovery
├── ✅ find-recently-added-prompts: Found 3 new prompts
├── ✅ update-cross-references: Found 2 broken links
├── ✅ find-extraction-candidates: Found 5 candidates
└── ✅ find-workflow-candidates: Found 2 optimizations

🔧 PHASE 2: Planning
├── 📋 Created execution plan with 12 tasks
├── ⏱️ Estimated duration: 45 minutes
└── 🎯 Prioritized: critical > important > optional

⚡ PHASE 3: Execution
├── ✅ Fixed 2 broken links
├── ✅ Extracted 3 templars from new artifacts
├── ✅ Consolidated 2 duplicate prompts
└── ✅ Updated prompt collection validation

📊 PHASE 4: Validation
├── ✅ Re-verification passed
├── 📈 Quality metrics improved by 15%
└── 📋 Report generated
```

## Quality Criteria

### Execution Quality
- [ ] All discovery prompts executed without errors
- [ ] Critical issues addressed first
- [ ] No destructive operations without backups
- [ ] Comprehensive execution logging
- [ ] Clear error messages with recovery steps

### Output Quality
- [ ] Detailed execution report generated
- [ ] Before/after metrics provided
- [ ] Next steps clearly recommended
- [ ] All modified files documented
- [ ] Report saved to standard location

### Safety Quality
- [ ] Dry run mode works correctly
- [ ] Individual prompt failures don't stop execution
- [ ] Rollback procedures provided for failed operations
- [ ] No data loss from operations
- [ ] Repository remains in working state

## Quality Criteria

- [ ] All discovery prompts executed without critical errors
- [ ] Critical issues addressed before optional improvements
- [ ] No destructive operations performed without backups
- [ ] Comprehensive execution logs generated
- [ ] Clear error messages with actionable recovery steps
- [ ] Execution report saved to standard location
- [ ] Quality metrics show measurable improvements
- [ ] Next steps clearly recommended
- [ ] Repository state preserved throughout execution

## Error Handling

### Common Error Scenarios

**Prompt File Missing**:
```text
❌ ERROR: Required housekeeping prompt not found: @find-recently-added-prompts

Solution:
1. Check if housekeeping collection is installed
2. Run: /install-housekeeping-collection
3. Or manually execute: @prompts/housekeeping/discovery/find-recently-added-prompts.prompt.md
```

**Permission Denied**:
```text
❌ ERROR: Cannot write to target folder: .cursor/rules/

Solution:
1. Check file system permissions
2. Run terminal as administrator/sudo
3. Or specify different target folder with write access
```

**Discovery Failure**:
```text
⚠️ WARNING: Discovery phase incomplete - find-extraction-candidates failed

Impact: May miss extraction opportunities
Recovery: Run manually after completion: @find-extraction-candidates [folder]
```

## Troubleshooting

### Common Issues and Solutions

**"No housekeeping prompts found"**:
- **Cause**: Housekeeping collection not installed or prompts missing
- **Solution**:
  1. Install housekeeping collection: `/install-housekeeping-collection`
  2. Verify prompt files exist in `.cursor/prompts/housekeeping/`
  3. Check Prompt Registry sidebar shows housekeeping collection

**"Permission denied" during execution**:
- **Cause**: Repository is read-only or insufficient file system permissions
- **Solution**:
  1. Check if repository is in read-only mode (detached HEAD, etc.)
  2. Ensure write permissions on target folders
  3. Run in administrator/sudo mode if needed
  4. Specify different target folder with write access

**"Discovery phase hangs or takes too long"**:
- **Cause**: Large repository or too many files to scan
- **Solution**:
  1. Use targeted folders: `--target-folders .cursor/rules`
  2. Run discovery-only first to identify scope
  3. Consider breaking into smaller runs

**"Quality metrics don't improve"**:
- **Cause**: Issues are deeper than automated fixes can handle
- **Solution**:
  1. Review execution report for manual intervention items
  2. Some issues require human judgment (duplicate consolidation)
  3. Consider running specific prompts individually for complex cases

### Recovery Strategies

**After Failed Run**:
1. Check execution logs for specific failure point
2. Run individual failed prompts manually
3. Use `--skip-categories` to exclude problematic areas
4. Start with `discovery-only` mode to reassess

**Repository State Issues**:
- All operations create backups before destructive changes
- Use git to revert if needed: `git checkout -- .`
- Check housekeeping/reports/ for detailed change logs

## Integration Points

### With Prompt Registry
- Automatically installs housekeeping collection if missing
- Uses slash commands for all sub-prompts
- Updates collection manifests after changes

### With Git Workflow
- Creates housekeeping branch for changes
- Generates commits with descriptive messages
- Supports PR/MR workflow for review

### With Quality Gates
- Runs before commits in CI/CD
- Enforces zero-warnings-zero-errors policy
- Provides quality metrics for dashboards

## Performance Considerations

### Time Estimates by Mode
- **discovery-only**: 5-10 minutes
- **monthly**: 30-60 minutes
- **quarterly**: 2-3 hours
- **full**: 4-6 hours

### Optimization Strategies
- Parallel execution of independent discovery prompts
- Incremental processing for large repositories
- Caching of discovery results between runs
- Progress saving for long-running operations

---

**Related**:
- `housekeeping/README.md` - Complete housekeeping guide
- `rule.quality.zero-warnings-zero-errors-rule.mdc` - Quality enforcement
- `rule.git.branch-lifecycle-rule.mdc` - Branch management for housekeeping

**Save Results To**: `housekeeping/reports/[timestamp]-[mode]-report.md`
**Estimated Time**: 30min - 6hrs (depending on mode and repository size)

## Related Prompts

**Core Housekeeping Suite**:
- `housekeeping/maintenance/update-cross-references.prompt.md` - Fix broken links
- `housekeeping/cleanup/consolidate-duplicates.prompt.md` - Merge duplicates
- `housekeeping/extraction/extract-templar-exemplar.prompt.md` - Extract patterns
- `housekeeping/sync/sync-improvements.prompt.md` - Cross-repo sync

**Quality Assurance**:
- `quality/validate-code-quality-enforcement.prompt.md` - Quality checks
- `git/validate-branch-naming.prompt.md` - Branch validation
- `documentation/validate-xml-documentation.prompt.md` - Docs validation

**Advanced Operations**:
- `rule-authoring/extract-prompts-from-conversation.prompt.md` - Extract patterns
- `prompts/enhance-prompt.prompt.md` - Enhance individual prompts
- `prompts/create-new-prompt.prompt.md` - Create prompts from scratch

**Manual Follow-up** (when orchestrator identifies issues):
- `housekeeping/cleanup/archive-obsolete-artifacts.prompt.md` - Archive old content
- `housekeeping/cleanup/find-dead-templars-exemplars.prompt.md` - Find unused patterns
- `housekeeping/discovery/find-workflow-candidates.prompt.md` - Identify improvements
