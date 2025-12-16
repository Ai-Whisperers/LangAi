# Housekeeping Prompts

Periodic maintenance prompts for keeping the artifact framework organized, consistent, and high-quality.

## Purpose

These prompts help maintain the health of your `.cursor/` framework over time by:
- Extracting reusable patterns
- Eliminating duplicates
- Fixing broken references
- Archiving obsolete content
- Syncing improvements across repositories

## Organization

Housekeeping prompts are organized into categories for better discoverability:

```
housekeeping/
├── maintenance/     # Regular upkeep tasks (monthly)
├── cleanup/         # Removal/consolidation tasks (quarterly)
├── discovery/       # Finding/analysis tasks (as needed)
├── extraction/      # Pattern extraction tasks (monthly)
└── sync/           # Cross-repository tasks (quarterly)
```

## When to Run

### Monthly (1-2 hours)
- **`@update-cross-references`** - Check for broken links
- **`@extract-templar-exemplar`** - Extract patterns from new artifacts
- **`@find-recently-added-prompts`** - Review recent additions

### Quarterly (3-4 hours)
- **`@consolidate-duplicates`** - Find and merge duplicate artifacts
- **`@archive-obsolete-artifacts`** - Clean up outdated content
- **`@sync-improvements`** - Sync changes across repositories

### As Needed
- After major refactoring
- When noticing confusion about which artifact to use
- When repositories diverge
- After creating many new artifacts

## Categories

### 🔧 Maintenance (`maintenance/`)
Regular upkeep tasks to keep the framework healthy.

#### Update Cross-References
**File**: `maintenance/update-cross-references.prompt.md`
**Command**: `@update-cross-references [folder-path]`

**Purpose**: Find and fix broken links, outdated references, and missing cross-references.

**Use When**: After moving/renaming files, refactoring, monthly maintenance.

**Example**: `@update-cross-references .cursor/rules/`


#### Validate Prompt Collections
**File**: `maintenance/validate-prompt-collections.prompt.md`
**Command**: `@validate-prompt-collections`

**Purpose**: Ensure prompt collections are properly structured and complete.

**Use When**: After collection changes, monthly validation.

---

### 🧹 Cleanup (`cleanup/`)
Tasks for removing duplicates and archiving obsolete content.

#### Archive Obsolete Artifacts
**File**: `cleanup/archive-obsolete-artifacts.prompt.md`
**Command**: `@archive-obsolete-artifacts [folder-path]`

**Purpose**: Identify and archive obsolete artifacts with redirects to replacements.

**Use When**: Quarterly cleanup, artifacts superseded by better versions.

**Example**: `@archive-obsolete-artifacts .cursor/rules/`

#### Consolidate Duplicates
**File**: `cleanup/consolidate-duplicates.prompt.md`
**Command**: `@consolidate-duplicates [folder-path]`

**Purpose**: Find and merge duplicate or overlapping artifacts.

**Use When**: Quarterly cleanup, confusion about which artifact to use.

**Example**: `@consolidate-duplicates .cursor/rules/ticket/`

#### Find Dead Templars/Exemplars
**File**: `cleanup/find-dead-templars-exemplars.prompt.md`
**Command**: `@find-dead-templars-exemplars [folder-path]`

**Purpose**: Identify unused templars and exemplars for cleanup.

**Use When**: Quarterly cleanup, maintaining clean pattern libraries.

#### Condense Prompts
**File**: `cleanup/condense-prompts.prompt.md`
**Command**: `@condense-prompts [prompt-path]`

**Purpose**: Reduce overly verbose prompts while preserving functionality.

**Use When**: Prompts become too long, preparing for maintenance.

---

### 🔍 Discovery (`discovery/`)
Tasks for finding and analyzing artifacts that need attention.

#### Find Extraction Candidates
**File**: `discovery/find-extraction-candidates.prompt.md`
**Command**: `@find-extraction-candidates [folder-path]`

**Purpose**: Identify artifacts with reusable patterns that should become templars/exemplars.

**Use When**: Monthly pattern extraction, after creating new artifacts.

#### Find Script Extraction Candidates
**File**: `discovery/find-script-extraction-candidates.prompt.md`
**Command**: `@find-script-extraction-candidates [folder-path]`

**Purpose**: Find scripts that contain reusable patterns for extraction.

**Use When**: Script maintenance, identifying reusable components.

#### Find Condense Candidates
**File**: `discovery/find-condense-candidates.prompt.md`
**Command**: `@find-condense-candidates [folder-path]`

**Purpose**: Spot oversized prompts that need condensation.

**Use When**: Preparing cleanup, identifying verbosity issues.

**Example**: `@find-condense-candidates .cursor/prompts`

#### Find Workflow Candidates
**File**: `discovery/find-workflow-candidates.prompt.md`
**Command**: `@find-workflow-candidates [folder-path]`

**Purpose**: Identify potential workflow improvements and automation opportunities.

**Use When**: Process optimization, workflow analysis.

#### Workflow Link Prompt
**File**: `discovery/workflow-link-prompt.prompt.md`
**Command**: `@workflow-link-prompt [workflow-description]`

**Purpose**: Create prompts that link workflow steps together.

**Use When**: Building complex multi-step workflows.

#### Find Prompts Needing Review
**File**: `discovery/find-prompts-needing-review.prompt.md`
**Command**: `@find-prompts-needing-review [criteria]`

**Purpose**: Identify prompts that need quality review or updates.

**Use When**: Quality assurance, prompt maintenance.

#### Find Recently Added Prompts
**File**: `discovery/find-recently-added-prompts.prompt.md`
**Command**: `@find-recently-added-prompts [time-period]`

**Purpose**: Identify prompts added recently to review for quality and consistency, then improve and enhance them.

**Use When**: Finding prompts that need improvement and enhancement.

**Example**: `@find-recently-added-prompts 30d`

---

### 📦 Extraction (`extraction/`)
Tasks for extracting reusable patterns and examples.

#### Extract Templar or Exemplar
**File**: `extraction/extract-templar-exemplar.prompt.md`
**Command**: `@extract-templar-exemplar [artifact-path]`

**Purpose**: Extract reusable patterns (templars) or reference examples (exemplars).

**Use When**: Finding excellent structure, capturing best practices.

**Example**: `@extract-templar-exemplar .cursor/rules/ticket/plan-rule.mdc`

#### Extract Script Templars/Exemplars
**File**: `extraction/extract-script-templars-exemplars.prompt.md`
**Command**: `@extract-script-templars-exemplars [script-path]`

**Purpose**: Extract reusable patterns from PowerShell/Python scripts.

**Use When**: Script pattern identification, creating reusable components.

---

### 🔄 Sync (`sync/`)
Tasks for synchronizing improvements across repositories.

#### Sync Improvements
**File**: `sync/sync-improvements.prompt.md`
**Command**: `@sync-improvements --source [repo] --target [repo]`

**Purpose**: Intelligently sync rule/prompt improvements across repositories.

**Use When**: Multi-repo alignment, propagating best practices.

**Example**:
```
@sync-improvements \
  --source /path/to/eneve.ebase.datamigrator \
  --target /path/to/eneve.domain
```

**⚠️ CRITICAL**: Always analyzes diffs - NO blind copying!

#### Add Support Scripts
**File**: `sync/add-support-scripts.prompt.md`
**Command**: `@add-support-scripts [script-type]`

**Purpose**: Add supporting scripts needed for prompt functionality.

**Use When**: After creating prompts that require custom scripts.

---

## Maintenance Schedule

### Suggested Routine

**Monthly** (1-2 hours):
```bash
# Check for broken links
@update-cross-references .cursor/

# Review recent additions
@find-recently-added-prompts 30d

# Extract any new patterns found (including uncommitted artifacts)
@extract-templar-exemplar [recently-created-artifacts]
```

**Quarterly** (3-4 hours):
```bash
# Find duplicates
@consolidate-duplicates .cursor/rules/
@consolidate-duplicates .cursor/prompts/

# Archive obsolete content
@archive-obsolete-artifacts .cursor/

# Sync across repos (if multi-repo)
@sync-improvements --source [source-repo] --target [target-repo]
```

**After Major Work**:
```bash
# After refactoring/moving files
@update-cross-references .cursor/

# After creating many artifacts
@consolidate-duplicates [new-artifact-folder]
@extract-templar-exemplar [new-artifacts]
```

## Best Practices

### DO ✅
- Run housekeeping regularly (prevents debt accumulation)
- Review recommendations before applying
- Document changes made
- Test after making changes
- Commit housekeeping work separately from feature work

### DON'T ❌
- Blindly accept all recommendations
- Skip verification steps
- Delete without archiving
- Ignore repository-specific differences
- Rush through analysis

## Integration with Prompt Registry

Install the housekeeping collection:

1. **Add Prompt Registry source** (if not already done):
   - Command Palette → `Prompt Registry: Add Source`
   - Path: `./.cursor/prompts`

2. **Install housekeeping collection**:
   - Prompt Registry sidebar → `Housekeeping & Maintenance` → Install

3. **Use via slash commands**:
   ```
   /extract-templar-exemplar .cursor/rules/ticket/plan-rule.mdc
   /consolidate-duplicates .cursor/rules/ticket/
   /update-cross-references .cursor/
   /archive-obsolete-artifacts .cursor/rules/
   /find-recently-added-prompts 30d
   /sync-improvements --source [source] --target [target]
   ```

## Output Locations

### Extract Templar/Exemplar
- **Templars** → `.cursor/rules/templars/[domain]/` or `.cursor/prompts/templars/[category]/`
- **Exemplars** → `.cursor/rules/exemplars/[domain]/` or `.cursor/prompts/exemplars/[category]/`

### Archive Obsolete
- **Archived artifacts** → `archive/[type]/[year]/[name]/`
- **Redirect documents** → `archive/[type]/[year]/[name]/README.md`

### Sync Improvements
- **Sync branch** → `sync/improvements-from-[source]-[date]`
- **Sync log** → `sync-log.md` (in target repo)

## Quality Metrics

Good housekeeping achieves:
- **Zero broken links** in framework
- **< 5% duplicate content** (measure by artifact count)
- **< 10% obsolete artifacts** unarchived
- **Monthly cross-repo sync** (if multi-repo)
- **Clear templar/exemplar library** growing over time

## Related Documentation

- `.cursor/rules/rule-authoring/` - Rule authoring standards
- `.cursor/rules/prompts/` - Prompt creation standards
- `.cursor/rules/rule-authoring/rule-sync-rule.mdc` - Sync workflow details
- `.cursor/rules/rule-authoring/rule-templars-and-exemplars.mdc` - Pattern concepts

---

**TL;DR**: Run these prompts periodically to keep your framework clean, organized, and high-quality. Monthly for links/extraction, quarterly for duplicates/archival/sync.
