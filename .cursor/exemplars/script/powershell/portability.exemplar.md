# PowerShell Portability Pattern Exemplar

## Overview

Portable scripts work in both local development environments AND CI/CD pipelines without modification. Environment detection and portable defaults are key to Standard quality level.

## When to Use

- **Use for**: All shared scripts (Standard quality level required)
- **Critical for**: CI/CD automation, team-shared utilities, reusable libraries
- **Skip for**: Scripts explicitly designed for one environment only

## Good Pattern ✅

```powershell
# Auto-detect environment and use appropriate defaults
$isAzurePipeline = [bool]$env:AGENT_TEMPDIRECTORY

if ($isAzurePipeline) {
    Write-Host "Running in Azure Pipelines"
    $defaultOutput = "$env:BUILD_ARTIFACTSTAGINGDIRECTORY/coverage"
} else {
    Write-Host "Running locally"
    $defaultOutput = "$env:TEMP/coverage"
}

# Use detected default if no parameter provided
if (-not $OutputPath) {
    $OutputPath = $defaultOutput
}

# Use script-relative paths
$configFile = Join-Path $PSScriptRoot "config.json"
$templatesDir = Join-Path $PSScriptRoot "templates"
```

**Why this is good:**
- **Environment detection**: `$env:AGENT_TEMPDIRECTORY` indicates Azure Pipelines
- **Portable defaults**: Uses `$env:TEMP` locally, `$env:BUILD_ARTIFACTSTAGINGDIRECTORY` in CI/CD
- **Script-relative paths**: `$PSScriptRoot` resolves relative to script location
- **No modification needed**: Same script works in both environments

## Bad Pattern ❌

```powershell
# ❌ Hardcoded Azure Pipelines variable in default
$OutputPath = "$(Build.ArtifactStagingDirectory)/report"

# ❌ Hardcoded absolute path
$configFile = "C:\Projects\MyScript\config.json"

# ❌ Assumes current directory
$templatesDir = ".\templates"
```

**Why this is bad:**
- **Not portable**: `$(Build.*)` syntax only works in Azure Pipelines YAML, fails locally
- **Hardcoded paths**: Breaks on other machines, different drive letters, Linux
- **Current directory assumption**: Breaks if script called from different directory
- **Requires modification**: User must edit script to run locally

## Portability Checklist

### Environment-Specific Variables

```powershell
# Detect common CI/CD environments
$isBuildServer = $false
$isBuildServer = $isBuildServer -or [bool]$env:AGENT_TEMPDIRECTORY     # Azure Pipelines
$isBuildServer = $isBuildServer -or [bool]$env:GITHUB_ACTIONS          # GitHub Actions
$isBuildServer = $isBuildServer -or [bool]$env:GITLAB_CI               # GitLab CI
$isBuildServer = $isBuildServer -or [bool]$env:JENKINS_HOME            # Jenkins

if ($isBuildServer) {
    Write-Host "Running in CI/CD environment"
} else {
    Write-Host "Running in local development environment"
}
```

### Portable Path Construction

```powershell
# ✅ Good: Script-relative
$configPath = Join-Path $PSScriptRoot "config.json"

# ✅ Good: User-agnostic temp
$tempDir = Join-Path $env:TEMP "my-script-$([Guid]::NewGuid())"

# ✅ Good: Cross-platform home directory
$cacheDir = Join-Path ([Environment]::GetFolderPath('UserProfile')) ".my-script-cache"

# ❌ Bad: Hardcoded
$configPath = "C:\Scripts\config.json"

# ❌ Bad: Current directory dependent
$configPath = ".\config.json"
```

### Tool Availability Detection

```powershell
# Check if required tool is available
$dotnetPath = Get-Command dotnet -ErrorAction SilentlyContinue

if (-not $dotnetPath) {
    Write-Host "##vso[task.logissue type=error].NET SDK not found"
    Write-Host "Please install .NET SDK: https://dot.net"
    exit 1
}

Write-Host ".NET SDK found at: $($dotnetPath.Source)"
```

## Performance Characteristics

- **No overhead**: Environment detection happens once at script start
- **Faster debugging**: Same script runs locally for testing before CI/CD
- **Reduced maintenance**: No separate local and CI/CD versions

## Related Patterns

- [Parameters](./parameters.exemplar.md) - Portable default values for parameters
- [Error Handling](./error-handling.exemplar.md) - Clear errors when environment requirements not met
- See also: `rule.scripts.core-principles.v1` section "Scripts Must Be Portable"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

