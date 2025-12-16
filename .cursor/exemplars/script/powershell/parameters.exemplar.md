# PowerShell Parameter Validation Pattern Exemplar

## Overview

Proper parameter definition with strong typing and validation attributes ensures scripts are self-documenting, prevent invalid inputs, and fail fast with clear error messages.

## When to Use

- **Use for**: All reusable PowerShell scripts (Standard quality level and above)
- **Critical for**: Scripts with 3+ parameters, scripts accepting user input, CI/CD automation
- **Skip for**: Throwaway one-off scripts, scripts with no parameters

## Good Pattern ✅

```powershell
param(
    # Build configuration (Debug or Release)
    [Parameter(Mandatory=$false, HelpMessage="Build configuration to use")]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    # Output directory for reports (defaults to temp directory if not specified)
    [Parameter(Mandatory=$false, HelpMessage="Directory to write output files")]
    [string]$OutputPath = "$env:TEMP/coverage-report",

    # Minimum coverage threshold percentage
    [Parameter(Mandatory=$false, HelpMessage="Minimum line coverage percentage required")]
    [ValidateRange(0, 100)]
    [int]$MinLineCoverage = 80,

    # Whether to fail the script if threshold not met
    [Parameter(Mandatory=$false, HelpMessage="Fail script if coverage below threshold")]
    [switch]$FailOnThreshold
)
```

**Why this is good:**
- **Strongly typed**: `[string]`, `[int]`, `[switch]` prevent type errors
- **Validation attributes**: `ValidateSet` limits choices, `ValidateRange` enforces bounds
- **Help messages**: `HelpMessage` provides guidance for `Get-Help`
- **Portable defaults**: Uses `$env:TEMP` not hardcoded paths
- **Clear mandatory status**: Explicit `Mandatory=$false` with sensible defaults

## Bad Pattern ❌

```powershell
param(
    # ❌ No validation
    [string]$Configuration = "Release",

    # ❌ Hardcoded Azure Pipelines variable
    [string]$OutputPath = "$(Build.ArtifactStagingDirectory)/report",

    # ❌ No range validation
    [int]$MinLineCoverage = 80
)
```

**Why this is bad:**
- **No validation**: User can pass "Debugg" (typo) and script will silently fail
- **Not portable**: `$(Build.ArtifactStagingDirectory)` only works in Azure Pipelines
- **No bounds checking**: User can pass `-MinLineCoverage 150` (invalid percentage)
- **No help text**: `Get-Help` won't show parameter descriptions
- **Type-only validation**: Weak constraints allow many invalid values

## Additional Validation Patterns

### ValidatePattern (Regex)

```powershell
[Parameter(Mandatory=$true)]
[ValidatePattern("^[A-Z]{2,5}-\d{1,5}$")]
[string]$TicketId
# Only accepts formats like: ABC-123, PROJ-1, XY-99999
```

### ValidateScript (Custom Logic)

```powershell
[Parameter(Mandatory=$true)]
[ValidateScript({Test-Path $_ -PathType Container})]
[string]$ProjectPath
# Only accepts paths that exist and are directories
```

### ValidateLength (String Length)

```powershell
[Parameter(Mandatory=$true)]
[ValidateLength(1, 50)]
[string]$ProjectName
# Only accepts non-empty strings up to 50 characters
```

### ValidateNotNullOrEmpty

```powershell
[Parameter(Mandatory=$true)]
[ValidateNotNullOrEmpty()]
[string]$ApiKey
# Ensures string is not null or empty
```

## Performance Characteristics

- **Negligible overhead**: Validation happens at script start, before any processing
- **Fail fast**: Invalid inputs caught immediately, not deep in execution
- **Better UX**: Clear error messages guide users to fix issues quickly

## Related Patterns

- [Error Handling](./error-handling.exemplar.md) - Validation failures are handled gracefully
- [Portability](./portability.exemplar.md) - Portable defaults for parameters
- See also: `rule.scripts.powershell-standards.v1` section "Parameters Must Be Properly Defined"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
