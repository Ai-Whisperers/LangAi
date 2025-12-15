---
name: Validate Script Standards
description: "Validate script against quality standards and best practices"
category: script
tags: [validation, quality, standards, compliance]
---

# Validate Script Against Standards

## Context

Systematically validate a script against core principles, language standards, and quality levels.

## Instructions

### Step 1: Determine Target Quality Level

Based on script purpose (see [quality levels rule](../script-quality-levels-rule.mdc)):
- **Basic**: Personal use, prototypes
- **Standard**: Shared scripts, CI/CD
- **Advanced**: Performance-critical, complex workflows
- **Production**: Mission-critical, SLA-bound

### Step 2: Core Principles Validation

Check [core principles rule](../core-principles-rule.mdc):
- [ ] Portable (works locally and CI/CD)
- [ ] Parameterized (no hardcoded values)
- [ ] Error handling (try/catch, exit codes)
- [ ] Configuration file support (if 5+ parameters)
- [ ] Documentation (help system works)

### Step 3: Language-Specific Validation

**PowerShell**: Check [PowerShell standards](../powershell-standards-rule.mdc)  
- Enforce runtime baseline: `#Requires -Version 7.2` and `#Requires -PSEdition Core` at top of every script/module.
**Python**: Check [Python standards](../python-standards-rule.mdc)

### Step 4: Quality Level Validation

Apply quality level checklist from [quality levels rule](../script-quality-levels-rule.mdc):
- Basic: 5 criteria
- Standard: 11 criteria (Basic + 6)
- Advanced: 14 criteria (Standard + 3)
- Production: 18 criteria (Advanced + 4)

### Step 5: Report Gaps

List missing criteria for next quality level.

## Quality Checklist

- [ ] Target quality level determined
- [ ] Core principles validated
- [ ] Language-specific standards checked
- [ ] Quality level criteria assessed
- [ ] Gaps identified and documented

---
Produced-by: prompt.scripts.validate-standards.v1 | ts=2025-12-07T00:00:00Z

