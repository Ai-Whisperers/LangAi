---
name: add-support-scripts
description: "Propose and add supporting scripts when gaps or repeats are detected"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags:
  - housekeeping
  - scripts
  - automation
  - support
  - maintenance
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
  - .cursor/rules/scripts/core-principles-rule.mdc
---

# Add Support Scripts

Detect missing helper scripts and recommend additions or references to existing shared utilities to keep automation DRY and consistent.

## Purpose

- Identify recurring manual steps or duplicated logic that should be scripted.
- Recommend existing shared scripts when they already cover the need.
- Propose new support scripts with destinations, owners, and standards alignment.

## Required Context

- Target area or workflow (e.g., build, release, validation, housekeeping).
- Existing script inventory locations (e.g., `.cursor/scripts`, `scripts/`, `.github/workflows/`).
- Languages allowed/preferred (PowerShell, Python).

## Inputs

- **Signals**:
  - Repeated manual commands in docs/PRs/tickets.
  - Duplicate code blocks across scripts.
  - Frequent reminders/checklists that could be automated.
  - Missing pre-checks (lint, format, security) before main flows.
  - Environment/bootstrap gaps (venv creation, module restore).
- **Constraints**:
  - Runtime environment (Windows/PowerShell vs cross-platform Python).
  - CI/CD availability and permissions.
  - Artifact locations and naming conventions.

## Reasoning Process (for AI Agent)

1. Map the workflow and locate friction points or duplication.
2. Check for existing scripts that solve the need; prefer reuse and linking over new creation.
3. If new script needed, define scope, inputs/outputs, and quality level (Basic/Standard/Advanced/Production).
4. Ensure standards: parameterization, logging, error handling, config support, retries where applicable.
5. Produce actionable add-plan with destinations and follow-ups.

## Process

1. **Assess Needs**
   - List repeated manual steps or duplicated code.
   - Identify missing pre-flight checks (format, lint, tests, secrets scan).
2. **Reuse First**
   - Search existing script catalog and shared modules.
   - If coverage exists, recommend linkage and small extensions instead of new script.
3. **Propose New Support Scripts (if needed)**
   - Define purpose, entry point, parameters, and outputs.
   - Choose language and quality level (see script-quality-levels rule).
   - Include config file support when parameters ≥ 5.
4. **Plan Implementation**
   - Destination paths (e.g., `.cursor/scripts/housekeeping/`, `scripts/ops/`).
   - Dependencies and bootstrap steps.
   - Testing approach (unit or smoke).
5. **Document and Track**
   - Outline tasks to add, validate, and register in collections/catalogs.
   - Note owners and follow-up tickets if required.

## Output Format

```markdown
## Support Script Recommendations (Scope: [scope])

### Candidates
| Need | Recommendation | Reuse Existing? | Destination | Quality Level | Notes |
|------|----------------|-----------------|-------------|---------------|-------|
| [task] | [script name/purpose] | [Yes/No + ref] | [path] | [Basic/Std/Adv/Prod] | [why] |

### Actions
- [ ] Reuse [existing script] for [need]; add doc link at [location]
- [ ] Create [new script] at [path] with params [list]
- [ ] Add tests/validation: [plan]
- [ ] Register in catalog/collection: [where]
```

## Validation Checklist

- [ ] Reuse evaluated before creating new scripts
- [ ] Language and quality level selected
- [ ] Parameters, logging, and error handling defined
- [ ] Destination and owners assigned
- [ ] Tests/validation steps noted

## Usage

```
@add-support-scripts build-pipeline
@add-support-scripts housekeeping -Language PowerShell
```

## Related Prompts

- `housekeeping/find-script-extraction-candidates.prompt.md`
- `housekeeping/extract-script-templars-exemplars.prompt.md`
- `script/validate-script-standards.prompt.md`

