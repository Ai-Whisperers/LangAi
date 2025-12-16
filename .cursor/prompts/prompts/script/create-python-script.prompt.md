---
name: Create Python Script
description: "Create new reusable Python script from template following standards"
category: script
tags: [python, creation, automation, templates]
---

# Create New Reusable Python Script

## Context

Use this prompt when creating a new Python script that needs to meet Standard quality level (production-ready) requirements. This prompt guides you through template usage, customization, and validation.

## Target Audience

- Script authors creating new Python automation
- DevOps engineers building CI/CD scripts
- Developers needing reusable Python utilities

## Instructions

### Step 1: Use Full Template

Start with full Python template:
- Template: `./templars/python-script-full.templar.py`
- Config template: `./templars/python-config-file.templar.yaml`

### Step 2: Replace Placeholders

Replace all `{{PLACEHOLDER}}` values:
- `{{SCRIPT_NAME}}`: Script file name
- `{{SCRIPT_DESCRIPTION}}`: Multi-line description
- `{{AUTHOR}}`: Your name or team name
- `{{ADDITIONAL_REQUIREMENTS}}`: Required packages
- `{{PARAMETER_NAME}}`: Each parameter name
- `{{PARAMETER_DESCRIPTION}}`: Each parameter description
- `{{DEFAULT_VALUE}}`, `{{MIN_VALUE}}`, `{{MAX_VALUE}}`: Parameter constraints

### Step 3: Implement Logic

Replace `# TODO: Replace with actual logic` sections with implementation.

### Step 4: Validate Against Standard Quality Level

- [ ] Module docstring complete (help() works)
- [ ] Type hints on all functions
- [ ] argparse CLI with comprehensive help
- [ ] Pydantic config validation
- [ ] Structured logging
- [ ] Portability (works locally and CI/CD)
- [ ] Proper exit codes
- [ ] YAML config support

### Step 5: Test

```bash
# Test locally
python script-name.py --verbose

# Test help
python script-name.py --help

# Test in simulated CI/CD
export AGENT_TEMPDIRECTORY=/tmp
python script-name.py
```

## Quality Checklist

- [ ] All placeholders replaced
- [ ] Module docstring complete with Usage and Examples
- [ ] Type hints on all functions and parameters
- [ ] argparse with proper help text
- [ ] Pydantic models for configuration
- [ ] Logging configured with levels
- [ ] Script works locally and in CI/CD
- [ ] Proper exit codes (0 = success, non-zero = failure)
- [ ] YAML config file support
- [ ] Script tested with --help

---
Produced-by: prompt.scripts.create-python.v1 | ts=2025-12-07T00:00:00Z
