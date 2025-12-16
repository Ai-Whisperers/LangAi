---
name: extract-script-templars-exemplars
description: "Convert candidate scripts into templars and exemplars with placeholders"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags:
  - scripting
  - templars
  - exemplars
  - refactor
  - maintenance
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
  - .cursor/rules/scripts/core-principles-rule.mdc
---

# Extract Script Templars and Exemplars

Transform a selected script into reusable templar/exemplar assets with clear placeholders and minimal duplication.

## Purpose

- Create a reusable templar (skeleton) and exemplar (reference implementation) from a candidate script.
- Standardize parameterization, logging, error handling, and configuration patterns.
- Document destinations and trimming so future updates stay DRY.

## Required Context

- Candidate script path and language (PowerShell/Python).
- Intended consumers and recurring tasks the script supports.
- Target destinations for templar/exemplar storage in this repo.

## Reasoning Process (for AI Agent)

1. Understand the script’s responsibilities and cross-cutting concerns.
2. Decide Templar vs Exemplar vs Both; justify the choice.
3. Preserve patterns that should be reused; replace tenant-specific details with placeholders.
4. Keep exemplar runnable with safe defaults and documented prerequisites.
5. Produce a concise extraction plan plus ready-to-use artifacts.

## Process

1. **Collect Context**
   - Script path, purpose, dependencies, entry points, and current parameters.
   - Confirm language and standards to apply (PowerShell or Python rule set).
2. **Choose Extraction Type**
   - **Templar**: Keep structure, parameters, logging, error handling; replace business logic with placeholders.
   - **Exemplar**: Provide idiomatic, runnable example showing best practices.
   - **Both**: When the script has strong structure and a solid end-to-end example.
3. **Design the Templar**
   - Normalize parameter parsing, config loading, logging, retry, exit codes.
   - Introduce placeholders for environment-specific values (URIs, secrets, IDs, file paths).
   - Keep TODO markers minimal and action-oriented.
4. **Design the Exemplar**
   - Produce a trimmed, runnable sample that references the templar for structure.
   - Include minimal test data and safe defaults; avoid secrets.
   - Document prerequisites and how to swap in real values.
5. **Publish Plan**
   - Specify destination paths (templar + exemplar).
   - List trims performed (what was removed/masked) and remaining open items.
   - Provide follow-up tasks (tests, validation, docs).

## Output Format

```markdown
## Extraction Plan
- Source: [path]
- Language: [PowerShell/Python]
- Type: [Templar/Exemplar/Both] (Why)
- Destinations: [templar path], [exemplar path]
- Trims: [list]

### Templar (Skeleton)
- Purpose: [what it covers]
- Placeholders: [list with meaning]
- Core blocks: [parameters, config, logging, error handling, retries]

### Exemplar (Runnable Reference)
- Scenario: [what it demonstrates]
- Defaults: [safe values]
- How to run: [command]
- How to adapt: [steps]

### Actions
- [ ] Save templar to [path]
- [ ] Save exemplar to [path]
- [ ] Add docs/tests/metadata
```

## Validation Checklist

- [ ] Extraction type justified (Templar/Exemplar/Both)
- [ ] Placeholders replace tenant-specific details
- [ ] Logging, error handling, and configuration standardized
- [ ] Exemplar runnable with safe defaults
- [ ] Destinations and trims documented

## Usage

```
@extract-script-templars-exemplars scripts/utilities/backup.ps1
```

## Related Prompts

- `housekeeping/find-script-extraction-candidates.prompt.md`
- `script/validate-script-standards.prompt.md`
