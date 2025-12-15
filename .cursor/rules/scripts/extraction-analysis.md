# Script Rules Extraction Analysis

## Overview

This document analyzes the current script rules and identifies opportunities to extract:
1. **Templars** - Structural templates for output generation
2. **Exemplars** - Pattern examples for learning
3. **Prompts** - Task-oriented instructions for common script operations

## Current State

### Rule Files and Sizes
- `powershell-standards-rule.mdc`: 1,180 lines (large)
- `python-standards-rule.mdc`: 1,334 lines (large)
- `core-principles-rule.mdc`: ~500 lines (moderate)
- `agent-application-rule.mdc`: ~150 lines (small)
- `scripts-rules-index.mdc`: ~200 lines (small)

### Problem
- PowerShell and Python rules are too large
- Examples are embedded inline, making rules harder to read
- No separation between structural templates (templars) and pattern examples (exemplars)
- No reusable prompts for common script tasks

---

## Proposed Extractions

### 1. TEMPLARS (Structural Templates)

Templars define the *structure* of generated scripts. Load during write phase only.

#### PowerShell Templars

**`powershell-script-minimal.templar.ps1`**
- Location: `eneve.domain/.cursor/rules/scripts/templars/`
- Source: Lines 997-1045 in `powershell-standards-rule.mdc`
- Content: Minimal PowerShell script template with:
  - Comment-based help skeleton
  - Parameter block
  - Error handling
  - Basic structure
- Usage: Creating new simple scripts

**`powershell-script-full.templar.ps1`**
- Location: `eneve.domain/.cursor/rules/scripts/templars/`
- Source: Lines 1047-1161 in `powershell-standards-rule.mdc`
- Content: Full-featured PowerShell script template with:
  - Comprehensive comment-based help
  - Advanced parameter validation
  - Environment detection
  - Configuration file support
  - Error handling with cleanup
- Usage: Creating new complex scripts

**`powershell-config-file.templar.json`**
- Location: `eneve.domain/.cursor/rules/scripts/templars/`
- Source: Lines 228-238 in `powershell-standards-rule.mdc`
- Content: JSON configuration file template
- Usage: Adding config file support to scripts

#### Python Templars

**`python-script-full.templar.py`**
- Location: `eneve.domain/.cursor/rules/scripts/templars/`
- Source: Lines 52-116 in `python-standards-rule.mdc` (module docstring example)
- Content: Full Python script template with:
  - Module docstring
  - Type hints
  - argparse CLI
  - Logging setup
  - Main function structure
- Usage: Creating new Python scripts

**`python-config-file.templar.yaml`**
- Location: `eneve.domain/.cursor/rules/scripts/templars/`
- Source: Lines 1112-1137 in `python-standards-rule.mdc`
- Content: YAML configuration file template
- Usage: Adding config file support to Python scripts

---

### 2. EXEMPLARS (Pattern Examples)

Exemplars illustrate *patterns* and *anti-patterns*. Load during planning/critique phases only.

#### PowerShell Exemplars

**`powershell-parameters.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 88-132 in `powershell-standards-rule.mdc`
- Content:
  - ✅ Good: Strongly typed params with validation attributes
  - ❌ Bad: Untyped params, hardcoded Azure variables
- Usage: Teaching parameter best practices

**`powershell-error-handling.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 164-196 in `powershell-standards-rule.mdc`
- Content:
  - Error handling with try/catch
  - Exit code checking ($LASTEXITCODE)
  - Azure Pipelines error logging
  - Cleanup in finally block
- Usage: Teaching robust error handling

**`powershell-portability.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 133-162 in `powershell-standards-rule.mdc`
- Content:
  - Environment detection pattern
  - Portable path defaults
  - CI/CD vs local adaptations
- Usage: Teaching portability patterns

**`powershell-parallel.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 318-354 in `powershell-standards-rule.mdc`
- Content:
  - Sequential vs parallel comparison
  - ForEach-Object -Parallel pattern
  - Throttle limit usage
  - Performance gains
- Usage: Teaching parallel processing

**`powershell-logging.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 386-437 in `powershell-standards-rule.mdc`
- Content:
  - Write-Log function with levels
  - Azure Pipelines integration
  - Console coloring
  - File logging
- Usage: Teaching structured logging

**`powershell-caching.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 494-554 in `powershell-standards-rule.mdc`
- Content:
  - File hash computation
  - Cache management (load/save)
  - Skip unchanged detection
- Usage: Teaching smart caching

**`powershell-retry.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 558-610 in `powershell-standards-rule.mdc`
- Content:
  - Invoke-WithRetry function
  - Exponential backoff
  - Network failure handling
- Usage: Teaching retry logic

**`powershell-webhooks.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 776-854 in `powershell-standards-rule.mdc`
- Content:
  - Send-TeamsNotification function
  - Message card format
  - Status color mapping
- Usage: Teaching webhook notifications

**`powershell-progress.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 355-385 in `powershell-standards-rule.mdc`
- Content:
  - Write-Progress pattern
  - Percent complete calculation
  - Completion notification
- Usage: Teaching progress reporting

**`powershell-pipeline.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 273-317 in `powershell-standards-rule.mdc`
- Content:
  - ValueFromPipeline pattern
  - begin/process/end blocks
  - Pipeline usage examples
- Usage: Teaching pipeline support

#### Python Exemplars

**`python-type-hints.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 118-173 in `python-standards-rule.mdc`
- Content:
  - Pydantic BaseModel examples
  - Field validation
  - Custom validators
  - Root validators
- Usage: Teaching type hints and validation

**`python-logging.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 175-248 in `python-standards-rule.mdc`
- Content:
  - setup_logging function
  - Console and file handlers
  - Azure Pipelines handler
  - Log levels
- Usage: Teaching structured logging

**`python-retry.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 250-320 in `python-standards-rule.mdc`
- Content:
  - @retry decorator
  - Exponential backoff
  - Exception handling
- Usage: Teaching retry patterns

**`python-async.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 322-374 in `python-standards-rule.mdc`
- Content:
  - async/await pattern
  - asyncio.gather
  - I/O-bound optimization
- Usage: Teaching async programming

**`python-multiprocessing.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 376-421 in `python-standards-rule.mdc`
- Content:
  - multiprocessing.Pool
  - functools.partial
  - CPU-bound optimization
- Usage: Teaching parallel processing

**`python-rich-ui.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 423-502 in `python-standards-rule.mdc`
- Content:
  - Rich Console usage
  - Tables, panels, progress bars
  - Colored output
- Usage: Teaching terminal UI

**`python-context-managers.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 504-570 in `python-standards-rule.mdc`
- Content:
  - @contextmanager decorator
  - Resource cleanup
  - temporary_workspace pattern
- Usage: Teaching resource management

**`python-sqlite.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 572-717 in `python-standards-rule.mdc`
- Content:
  - CoverageHistory class
  - Database schema
  - CRUD operations
  - Trend analysis
- Usage: Teaching SQLite for history tracking

**`python-caching.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 719-841 in `python-standards-rule.mdc`
- Content:
  - CoverageCache class
  - File hashing
  - @lru_cache usage
- Usage: Teaching smart caching

**`python-webhooks.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 942-1032 in `python-standards-rule.mdc`
- Content:
  - send_teams_notification function
  - requests usage
  - NotificationStatus enum
- Usage: Teaching webhook notifications

**`python-yaml-config.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 1034-1137 in `python-standards-rule.mdc`
- Content:
  - YAML loading
  - Pydantic validation
  - Nested configuration models
- Usage: Teaching YAML configuration

**`python-exceptions.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 1139-1209 in `python-standards-rule.mdc`
- Content:
  - Custom exception hierarchy
  - Exception usage patterns
  - Error handling
- Usage: Teaching exception design

**`python-pytest.exemplar.md`**
- Location: `eneve.domain/.cursor/rules/scripts/exemplars/`
- Source: Lines 1211-1315 in `python-standards-rule.mdc`
- Content:
  - pytest fixtures
  - Test patterns
  - Parametrized tests
  - Mocking
- Usage: Teaching unit testing

---

### 3. PROMPTS (Task Instructions)

Prompts are task-oriented instructions following the prompt-creation-rule standards.

**Location**: `eneve.domain/.cursor/rules/scripts/prompts/`

#### Script Creation Prompts

**`create-powershell-script.prompt.md`**
- Title: Create New Reusable PowerShell Script
- Category: Creation
- Complexity: Intermediate
- Triggers: New script creation, PowerShell automation
- Placeholder conventions: `{{SCRIPT_NAME}}`, `{{SCRIPT_PURPOSE}}`, etc.
- Quality checklist items
- References: powershell-script-minimal.templar.ps1, powershell-script-full.templar.ps1

**`create-python-script.prompt.md`**
- Title: Create New Reusable Python Script
- Category: Creation
- Complexity: Intermediate
- Triggers: New script creation, Python automation
- Placeholder conventions: `{{SCRIPT_NAME}}`, `{{SCRIPT_PURPOSE}}`, etc.
- Quality checklist items
- References: python-script-full.templar.py

#### Enhancement Prompts

**`add-retry-logic.prompt.md`**
- Title: Add Retry Logic with Exponential Backoff
- Category: Enhancement
- Complexity: Simple
- Triggers: Network operations, external dependencies, transient failures
- Language-agnostic approach (references both PowerShell and Python exemplars)
- Quality checklist: configurable attempts, exponential backoff, meaningful errors

**`add-parallel-processing.prompt.md`**
- Title: Add Parallel/Concurrent Processing
- Category: Enhancement
- Complexity: Intermediate
- Triggers: Performance optimization, multiple independent items
- Separate guidance for PowerShell (ForEach-Object -Parallel) vs Python (multiprocessing/async)
- Quality checklist: thread safety, appropriate use cases, performance validation

**`add-config-file-support.prompt.md`**
- Title: Add Configuration File Support
- Category: Enhancement
- Complexity: Simple
- Triggers: 5+ parameters, environment-specific settings
- Format guidance (JSON for PowerShell, YAML for Python)
- Quality checklist: schema validation, defaults, override logic

**`add-webhook-notifications.prompt.md`**
- Title: Add Webhook Notifications (Teams/Slack)
- Category: Enhancement
- Complexity: Simple
- Triggers: CI/CD integration, team notifications
- Status mapping, fact formatting
- Quality checklist: error handling, environment variables, graceful degradation

**`add-progress-reporting.prompt.md`**
- Title: Add Progress Reporting
- Category: Enhancement
- Complexity: Simple
- Triggers: Long-running operations, user feedback
- PowerShell: Write-Progress
- Python: Rich Progress bars
- Quality checklist: meaningful updates, completion handling, percentage calculation

**`add-structured-logging.prompt.md`**
- Title: Add Structured Logging with Levels
- Category: Enhancement
- Complexity: Intermediate
- Triggers: Debugging needs, production monitoring
- Log levels (INFO, WARN, ERROR, DEBUG)
- Azure Pipelines integration
- Quality checklist: consistent formatting, appropriate levels, file logging option

**`add-caching.prompt.md`**
- Title: Add Smart Caching for Unchanged Items
- Category: Enhancement
- Complexity: Intermediate
- Triggers: Performance optimization, unchanged detection
- File hashing approach
- Cache invalidation strategy
- Quality checklist: cache persistence, hash algorithm, skip logic

**`add-unit-tests.prompt.md`**
- Title: Add Unit Tests for Script
- Category: Testing
- Complexity: Intermediate
- Triggers: Quality assurance, CI/CD requirements
- PowerShell: Pester framework
- Python: pytest framework
- Quality checklist: 80%+ coverage, fixtures, parametrized tests

#### Validation Prompts

**`validate-script-standards.prompt.md`**
- Title: Validate Script Against Standards
- Category: Validation
- Complexity: Simple
- Triggers: Code review, pre-commit checks
- Checklist-based validation
- References all relevant rules
- Quality checklist: core principles, language-specific features, documentation

**`convert-to-reusable-script.prompt.md`**
- Title: Convert One-Off Script to Reusable Script
- Category: Refactoring
- Complexity: Intermediate
- Triggers: Script reuse, standardization
- Migration checklist
- Common issues to fix
- Quality checklist: portability, parameterization, error handling, documentation

---

## Benefits of Extraction

### For Rules
- **Shorter, more focused** - Rules focus on principles and requirements
- **Easier to read** - Less clutter from examples
- **Easier to maintain** - Update examples without changing rules
- **Versioning** - Exemplars and templars can evolve independently

### For Exemplars
- **Reusable** - Reference from multiple rules and prompts
- **Searchable** - Dedicated files easier to find
- **Testable** - Can be tested for correctness
- **Prevention of content leakage** - Only loaded during planning/critique, never during write

### For Templars
- **Single source of truth** - Script templates in one place
- **Consistent structure** - All scripts follow same template
- **Easy updates** - Update template, all future scripts benefit

### For Prompts
- **Actionable** - Direct task instructions for common operations
- **Discoverable** - Organized by category and complexity
- **Consistent** - Follow prompt-creation-rule standards
- **Cross-referenced** - Link to relevant exemplars and templars

---

## Next Steps

1. ✅ Create templars folder structure
2. ✅ Extract script templates to templars
3. ✅ Create exemplars folder structure
4. ✅ Extract pattern examples to exemplars
5. ✅ Create prompts folder structure
6. ✅ Create standard prompts
7. ✅ Update PowerShell and Python rules to reference exemplars/templars instead of inline examples
8. ✅ Update scripts-rules-index with new structure
9. ✅ Validate all references work correctly

---

## File Structure After Extraction

```
eneve.domain/.cursor/rules/scripts/
├── agent-application-rule.mdc          (existing, minor updates)
├── core-principles-rule.mdc            (existing, minor updates)
├── powershell-standards-rule.mdc       (existing, heavily refactored)
├── python-standards-rule.mdc           (existing, heavily refactored)
├── scripts-rules-index.mdc             (existing, updated with new structure)
│
├── templars/                            (NEW)
│   ├── powershell-script-minimal.templar.ps1
│   ├── powershell-script-full.templar.ps1
│   ├── powershell-config-file.templar.json
│   ├── python-script-full.templar.py
│   └── python-config-file.templar.yaml
│
├── exemplars/                           (NEW)
│   ├── powershell/
│   │   ├── parameters.exemplar.md
│   │   ├── error-handling.exemplar.md
│   │   ├── portability.exemplar.md
│   │   ├── parallel.exemplar.md
│   │   ├── logging.exemplar.md
│   │   ├── caching.exemplar.md
│   │   ├── retry.exemplar.md
│   │   ├── webhooks.exemplar.md
│   │   ├── progress.exemplar.md
│   │   └── pipeline.exemplar.md
│   │
│   └── python/
│       ├── type-hints.exemplar.md
│       ├── logging.exemplar.md
│       ├── retry.exemplar.md
│       ├── async.exemplar.md
│       ├── multiprocessing.exemplar.md
│       ├── rich-ui.exemplar.md
│       ├── context-managers.exemplar.md
│       ├── sqlite.exemplar.md
│       ├── caching.exemplar.md
│       ├── webhooks.exemplar.md
│       ├── yaml-config.exemplar.md
│       ├── exceptions.exemplar.md
│       └── pytest.exemplar.md
│
└── prompts/                             (NEW)
    ├── create-powershell-script.prompt.md
    ├── create-python-script.prompt.md
    ├── add-retry-logic.prompt.md
    ├── add-parallel-processing.prompt.md
    ├── add-config-file-support.prompt.md
    ├── add-webhook-notifications.prompt.md
    ├── add-progress-reporting.prompt.md
    ├── add-structured-logging.prompt.md
    ├── add-caching.prompt.md
    ├── add-unit-tests.prompt.md
    ├── validate-script-standards.prompt.md
    └── convert-to-reusable-script.prompt.md
```

---

## Estimated Impact

### Line Reduction in Rules
- `powershell-standards-rule.mdc`: ~1180 → ~400 lines (66% reduction)
- `python-standards-rule.mdc`: ~1334 → ~450 lines (66% reduction)

### New Files Created
- **Templars**: 5 files (~200 lines total)
- **Exemplars**: 23 files (~2300 lines total)
- **Prompts**: 12 files (~1200 lines total)

### Total Lines Impact
- Before: ~2900 lines in 2 large files
- After: ~850 lines in rules + ~3700 lines in 40 organized, focused files
- **Net increase**: ~1650 lines (justified by improved organization and reusability)

---

## Questions for Review

1. Should we create sub-folders for exemplars (powershell/, python/) or keep flat?
   - **Recommendation**: Use sub-folders for better organization
2. Should prompts be language-specific or language-agnostic where possible?
   - **Recommendation**: Language-agnostic where possible, with language-specific guidance inside
3. Should we extract ALL examples or keep some simple ones inline?
   - **Recommendation**: Extract advanced patterns, keep very simple examples inline
4. Should config file exemplars be JSON/YAML files or markdown?
   - **Recommendation**: Use actual file formats (.json, .yaml) for templars, markdown for documentation


