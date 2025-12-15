---
name: Create PowerShell Script
description: "Create new reusable PowerShell script from template following standards"
category: script
tags: [powershell, creation, automation, templates]
---

# Create New Reusable PowerShell Script

## Context

Use this prompt when creating a new PowerShell script that needs to meet Standard quality level (production-ready) requirements. This prompt guides you through template selection, customization, and validation.

## Target Audience

- Script authors creating new PowerShell automation
- DevOps engineers building CI/CD scripts
- Developers needing reusable PowerShell utilities

## Instructions

### Step 1: Choose Template

Select template based on script complexity:
- **Minimal Template**: Scripts with <5 parameters, simple logic
- **Full Template**: Scripts with 5+ parameters, config file support, environment detection

Use template files:
- Minimal: `./templars/powershell-script-minimal.templar.ps1`
- Full: `./templars/powershell-script-full.templar.ps1`

### Step 2: Replace Placeholders

Replace all `{{PLACEHOLDER}}` values in template:
- `{{SCRIPT_NAME}}`: Script file name (e.g., "analyze-coverage")
- `{{SCRIPT_PURPOSE}}`: One-line purpose for .SYNOPSIS
- `{{SCRIPT_DESCRIPTION}}`: Detailed description for .DESCRIPTION
- `{{AUTHOR}}`: Your name or team name
- `{{PREREQUISITES}}`: Required tools (e.g., ".NET SDK 9.x")
- `{{PARAMETER_NAME}}`: Each parameter name
- `{{PARAMETER_DESCRIPTION}}`: Each parameter's help text
- `{{PARAMETER_DEFAULT}}`: Default value for parameters

### Step 3: Implement Logic

Replace `# TODO: Replace with actual logic` sections with your implementation.

### Step 4: Validate Against Standard Quality Level

Use `validate-script-standards.prompt.md` to verify script meets Standard level:
- [ ] Comprehensive documentation (Get-Help works)
- [ ] Strong parameter validation
- [ ] Robust error handling
- [ ] Portability (works locally and in CI/CD)
- [ ] Proper exit codes
- [ ] Config file support (if 5+ parameters)

### Step 5: Test

Test script in both environments:
```powershell
# Test locally
.\script-name.ps1 -Verbose

# Test help
Get-Help .\script-name.ps1 -Full

# Test in simulated CI/CD (set Azure Pipelines env var)
$env:AGENT_TEMPDIRECTORY = "C:\temp"
.\script-name.ps1
```

## Placeholder Conventions

- `{{ALL_CAPS_WITH_BRACES}}`: Must be replaced
- Keep braces and capitalization to make unreplaced placeholders obvious
- Script will fail if placeholders not replaced (intentional)

## References

### Templars
- [PowerShell Minimal Template](../templars/powershell-script-minimal.templar.ps1)
- [PowerShell Full Template](../templars/powershell-script-full.templar.ps1)
- [PowerShell Config File Template](../templars/powershell-config-file.templar.json)

### Exemplars
- [Parameters](../../exemplars/script/powershell/parameters.exemplar.md) - Parameter validation patterns
- [Error Handling](../../exemplars/script/powershell/error-handling.exemplar.md) - Robust error handling
- [Portability](../../exemplars/script/powershell/portability.exemplar.md) - Environment detection

### Rules
- [PowerShell Standards](../powershell-standards-rule.mdc)
- [Core Principles](../core-principles-rule.mdc)
- [Quality Levels](../script-quality-levels-rule.mdc)

## Quality Checklist

- [ ] All placeholders replaced with actual values
- [ ] Comment-based help complete (.SYNOPSIS, .DESCRIPTION, .PARAMETER, .EXAMPLE)
- [ ] Parameters have ValidateSet/ValidateRange attributes
- [ ] $ErrorActionPreference = "Stop" at script start
- [ ] Try/catch/finally for error handling
- [ ] Script works locally without modification
- [ ] Script works in Azure Pipelines without modification
- [ ] Proper exit codes (0 = success, non-zero = failure)
- [ ] Config file support added (if 5+ parameters)
- [ ] Script tested with Get-Help

---
Produced-by: prompt.scripts.create-powershell.v1 | ts=2025-12-07T00:00:00Z

