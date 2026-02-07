# PowerShell Code Quality Enforcement Exemplar

## Overview

Complete code quality enforcement automation for .NET projects using automated fix scripts, gradual tightening policies, and CI/CD integration. This exemplar demonstrates the full workflow from baseline assessment through strict enforcement.

**Based on templar**: `manage-code-quality-enforcement.templar.ps1`

## When to Use

- **Use for**: Comprehensive .NET code quality management in enterprise environments
- **Critical for**: Teams requiring automated quality gates, gradual improvement, and CI/CD integration
- **Skip for**: Simple projects, one-off scripts, or manual quality checks

## Good Pattern ✅

### Script Structure

```powershell
# Based on manage-code-quality-enforcement.templar.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = "Root path to scan for projects")]
    [ValidateNotNullOrEmpty()]
    [string]$TargetPath,

    [Parameter(Mandatory = $false, HelpMessage = "Enforcement phase")]
    [ValidateSet("baseline", "auto-fix", "enforce", "suppress", "gradual", "strict")]
    [string]$CurrentPhase = "baseline",

    [Parameter(Mandatory = $false, HelpMessage = "JSON array of fix scripts")]
    [string]$FixScripts = '[
        {"errorCode": "IDE1006", "scriptPath": ".cursor/scripts/quality/fix-async-method-naming.ps1", "description": "Fix async method naming"},
        {"errorCode": "CA1304", "scriptPath": ".cursor/scripts/quality/fix-culture-info.ps1", "description": "Fix culture info issues"}
    ]',

    [Parameter(Mandatory = $false, HelpMessage = "Store successful scripts")]
    [switch]$StoreSuccessfulScripts = $true
)

# Import shared modules
$commonModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
if (Test-Path $commonModulePath) {
    Import-Module $commonModulePath -Force
}

# Implement concrete functions (replace templar TODOs)
function Get-ProjectFiles {
    param([string]$Path)
    Get-ChildItem -Path $Path -Filter "*.csproj" -Recurse -File
}

function Test-BuildWithWarningsAsErrors {
    param([string]$Path)
    $result = dotnet build --configuration Release /p:TreatWarningsAsErrors=true 2>&1
    @{
        Success = $LASTEXITCODE -eq 0
        Errors = ($result | Select-String "error").Count
        Warnings = ($result | Select-String "warning").Count
    }
}

# Main phase logic
switch ($CurrentPhase) {
    "baseline" {
        $projects = Get-ProjectFiles -Path $TargetPath
        $build = Test-BuildWithWarningsAsErrors -Path $TargetPath
        Write-Host "Found $($projects.Count) projects, $($build.Errors) errors, $($build.Warnings) warnings"
    }

    "auto-fix" {
        $scripts = $FixScripts | ConvertFrom-Json
        foreach ($script in $scripts) {
            Write-Host "Running: $($script.description)"
            & $script.scriptPath -Path $TargetPath
        }
    }

    "enforce" {
        # Update .csproj files to enable warnings as errors
        Get-ChildItem -Path $TargetPath -Filter "*.csproj" -Recurse | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            if ($content -notmatch "<TreatWarningsAsErrors>true</TreatWarningsAsErrors>") {
                $content = $content -replace "</PropertyGroup>", "  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>`n  </PropertyGroup>"
                $content | Set-Content $_.FullName
            }
        }
    }

    "suppress" {
        # Add temporary suppressions
        $editorConfig = Join-Path $TargetPath ".editorconfig"
        $content = if (Test-Path $editorConfig) { Get-Content $editorConfig -Raw } else { "[*.cs]`n" }
        $content += "`ndotnet_diagnostic.CA1304.severity = warning`n"
        $content += "dotnet_diagnostic.IDE1006.severity = warning`n"
        $content | Set-Content $editorConfig
    }

    "gradual" {
        # Remove suppressions gradually
        $editorConfig = Join-Path $TargetPath ".editorconfig"
        if (Test-Path $editorConfig) {
            $content = Get-Content $editorConfig -Raw
            $content = $content -replace "dotnet_diagnostic\.CA1304\.severity = warning`n", ""
            $content | Set-Content $editorConfig
        }
    }

    "strict" {
        # Remove all suppressions
        $editorConfig = Join-Path $TargetPath ".editorconfig"
        if (Test-Path $editorConfig) {
            $content = Get-Content $editorConfig -Raw
            $content = $content -replace "dotnet_diagnostic\.\w+\.severity = warning`n", ""
            $content | Set-Content $editorConfig
        }
    }
}
```

**Why this is good:**
- **Phased approach**: Systematic progression from assessment to strict enforcement
- **Automated fixes first**: Tries scripts before manual intervention
- **Gradual tightening**: Prevents overwhelming teams with too many changes at once
- **Registry system**: Learns and reuses successful fix scripts
- **CI/CD ready**: Integrates with automated pipelines
- **WhatIf support**: Safe testing without side effects

## Usage Examples

### Basic Assessment

```bash
# Run baseline assessment
.\manage-code-quality-enforcement.ps1 -TargetPath "C:\MyProject" -CurrentPhase baseline

# Output:
# Found 5 projects, 12 errors, 8 warnings
# Recommendation: Run auto-fix phase first
```

### Automated Fixes

```bash
# Run automated fix scripts
.\manage-code-quality-enforcement.ps1 -TargetPath "C:\MyProject" -CurrentPhase auto-fix

# Output:
# Running: Fix async method naming
# Fixed 3 async method naming violations
# Running: Fix culture info issues
# Fixed 2 culture violations
# Fix scripts: 2 successful, 0 failed
```

### Safe Testing

```bash
# Test what would happen without making changes
.\manage-code-quality-enforcement.ps1 -TargetPath "C:\MyProject" -CurrentPhase enforce -WhatIf

# Output:
# WhatIf: Would update project configurations for enforce phase
# WhatIf: Would add <TreatWarningsAsErrors>true</TreatWarningsAsErrors> to 5 .csproj files
```

## Key Implementation Details

### Phase Workflow

1. **Baseline**: Assess current state, count projects/errors/warnings
2. **Auto-fix**: Run automated scripts for known issues
3. **Enforce**: Enable warnings-as-errors in all projects
4. **Suppress**: Add temporary suppressions for remaining issues
5. **Gradual**: Remove suppressions incrementally over time
6. **Strict**: Achieve zero-tolerance policy

### Script Registry System

```json
{
  "scripts": [
    {
      "errorCode": "IDE1006",
      "scriptPath": ".cursor/scripts/quality/fix-async-method-naming.ps1",
      "description": "Fix async method naming violations",
      "successCount": 15,
      "lastSuccess": "2025-12-13"
    }
  ],
  "lastUpdated": "2025-12-13"
}
```

### CI/CD Integration

```yaml
# azure-pipelines.yml
- task: PowerShell@2
  displayName: 'Code Quality Auto-Fix'
  inputs:
    targetType: 'inline'
    script: |
      $fixScripts = '[...fix scripts JSON...]'
      .\scripts\manage-code-quality-enforcement.ps1 -Phase auto-fix -FixScripts $fixScripts

- task: PowerShell@2
  displayName: 'Code Quality Enforcement'
  inputs:
    targetType: 'inline'
    script: |
      .\scripts\manage-code-quality-enforcement.ps1 -Phase $(QualityPhase)
```

## Benefits

- **Scalable**: Works from single projects to enterprise monorepos
- **Automated**: Reduces manual quality enforcement work
- **Progressive**: Teams can adopt gradually without disruption
- **Learning**: System improves over time by tracking successful scripts
- **Integrated**: Works in both local development and CI/CD pipelines
- **Safe**: WhatIf mode and gradual phases prevent breaking changes

## Common Pitfalls to Avoid

### Pitfall 1: Skipping Auto-Fix Phase

**Bad**: Jumping straight to enforcement without trying automated fixes

**Consequence**: Manual work for issues that could be automated

**Good**: Always run auto-fix first, then handle remaining issues manually

### Pitfall 2: No Gradual Tightening

**Bad**: Enabling strict mode immediately

**Consequence**: Teams overwhelmed with too many errors at once

**Good**: Use gradual phase to remove suppressions incrementally

### Pitfall 3: Not Storing Successful Scripts

**Bad**: Not using `-StoreSuccessfulScripts` parameter

**Consequence**: System doesn't learn and improve over time

**Good**: Always store successful scripts for future reuse

## Metrics and Success Indicators

- **Reduction in manual work**: Percentage of issues fixed automatically
- **Time to compliance**: Days from baseline to strict enforcement
- **Registry growth**: Number of successful scripts in registry
- **CI/CD stability**: Reduction in pipeline failures due to quality issues
- **Team satisfaction**: Developer feedback on quality enforcement process

## Adaptation for Your Project

### Customize Fix Scripts

```json
[
  {"errorCode": "IDE1006", "scriptPath": "scripts/fix-async.ps1", "description": "Async naming"},
  {"errorCode": "CA1304", "scriptPath": "scripts/fix-culture.ps1", "description": "Culture info"},
  {"errorCode": "CS8618", "scriptPath": "scripts/fix-nullables.ps1", "description": "Null reference"}
]
```

### Adjust Phase Timing

```powershell
# Customize suppression duration
$SuppressionDays = 14  # Instead of 30

# Customize gradual removal levels
$RemovalLevels = @("CA1304", "IDE1006", "CA1062")  # Remove in this order
```

### Extend for Other Languages

The pattern works for any language with linters/warnings:

```powershell
# Python example
$FixScripts = '[
  {"errorCode": "E501", "scriptPath": "scripts/fix-line-length.py", "description": "Line too long"},
  {"errorCode": "F401", "scriptPath": "scripts/fix-unused-imports.py", "description": "Unused imports"}
]'
```

---

**Extracted from**: `manage-code-quality-enforcement.prompt.md`
**Templar**: `.cursor/scripts/quality/manage-code-quality-enforcement.templar.ps1`
**Use**: Pattern extraction only - adapt concrete implementations for your project
