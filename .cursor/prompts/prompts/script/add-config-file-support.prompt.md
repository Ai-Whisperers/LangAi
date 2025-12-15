---
name: Add Configuration File Support
description: "Add JSON/YAML configuration file support for script settings"
category: script
tags: [configuration, json, yaml, enhancement]
---

# Add Configuration File Support

## Context

Add external configuration file support for scripts with 5+ parameters or environment-specific settings.

## Instructions

### PowerShell

1. Use JSON config template: `./templars/powershell-config-file.templar.json`
2. Add config loading:
```powershell
param([string]$ConfigFile = "$PSScriptRoot/script-config.json")

if (Test-Path $ConfigFile) {
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    if (-not $PSBoundParameters.ContainsKey('Parameter')) {
        $Parameter = $config.Parameter
    }
}
```

### Python

1. Use YAML config template: `./templars/python-config-file.templar.yaml`
2. Add config loading with Pydantic validation (see [yaml-config exemplar](../../exemplars/script/python/yaml-config.exemplar.md))

## Quality Checklist

- [ ] Config file is optional (script works without it)
- [ ] Command-line parameters override config file values
- [ ] Config file location documented in help
- [ ] Validation applied to config values
- [ ] Clear error message if config file is invalid

---
Produced-by: prompt.scripts.add-config.v1 | ts=2025-12-07T00:00:00Z

