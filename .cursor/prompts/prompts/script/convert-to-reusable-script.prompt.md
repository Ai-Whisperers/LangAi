---
name: Convert to Reusable Script
description: "Convert one-off script to reusable script following standards"
category: script
tags: [refactoring, reusability, standards, transformation]
---

# Convert One-Off Script to Reusable Script

## Context

Convert an existing one-off or prototype script to meet Standard quality level (production-ready) requirements.

## Instructions

### Step 1: Assess Current State

Use `validate-script-standards.prompt.md` to identify gaps.

### Step 2: Fix Core Issues

Apply [core principles](../core-principles-rule.mdc):
1. **Remove hardcoded values**: Convert to parameters
2. **Add portability**: Environment detection, portable paths
3. **Improve error handling**: try/catch, exit codes, actionable errors
4. **Add documentation**: Help system (Get-Help/help())

### Step 3: Meet Standard Quality Level

Apply Standard criteria:
- [ ] Comprehensive documentation
- [ ] Strong parameter validation (ValidateSet, ValidateRange, type hints)
- [ ] Robust error handling
- [ ] Portability (local + CI/CD)
- [ ] Exit codes
- [ ] Config file support (if 5+ parameters)

### Step 4: Clean Up

- Remove debug statements
- Remove commented-out code
- Consistent formatting
- Meaningful variable names

### Step 5: Test

Test in both local and CI/CD environments.

## Migration Checklist

- [ ] Hardcoded values converted to parameters
- [ ] Portable paths (no C:\hardcoded\paths)
- [ ] Environment detection added
- [ ] Error handling comprehensive
- [ ] Documentation complete
- [ ] Parameter validation added
- [ ] Config file support (if needed)
- [ ] Exit codes proper
- [ ] Tested locally and CI/CD

---
Produced-by: prompt.scripts.convert-reusable.v1 | ts=2025-12-07T00:00:00Z

