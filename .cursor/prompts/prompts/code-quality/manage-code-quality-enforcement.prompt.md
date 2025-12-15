---
name: manage-code-quality-enforcement
description: "Comprehensive code quality enforcement management - check, repair, and gradually tighten warnings-as-errors policies"
category: code-quality
tags: code-quality, warnings, errors, enforcement, gradual-tightening, ci-cd
argument-hint: "Target project path (e.g., src/MyProject/ or . for root)"
---

# Manage Code Quality Enforcement

## Purpose

Comprehensive management of code quality enforcement settings across .NET projects, including warnings-as-errors configuration, gradual tightening policies, and CI/CD integration. Handles the complete lifecycle from "warnings as errors" enforcement to temporary suppressions to systematic issue resolution.

## Required Context

- `[TARGET_PATH]`: Target project/directory path (e.g., `src/MyProject/` or `.` for root)
- `[CURRENT_PHASE]`: Current enforcement phase (optional):
  - `baseline` - Initial assessment
  - `auto-fix` - Run automated fix scripts first
  - `enforce` - Enable warnings-as-errors
  - `suppress` - Add temporary suppressions
  - `gradual` - Gradually remove suppressions
  - `strict` - Full enforcement

## Optional Parameters

- `[TOLERANCE_LEVEL]`: Warning tolerance (0-100, default 0 for zero-tolerance)
- `[SUPPRESSION_DAYS]`: Days suppressions are valid before review (default 30)
- `[CI_CD_INTEGRATION]`: Enable CI/CD step generation (`true`/`false`, default `false`)
- `[FIX_SCRIPTS]`: JSON array of available fix scripts with error codes:
  ```json
  [
    {"errorCode": "IDE1006", "scriptPath": ".cursor/scripts/quality/fix-async-method-naming.ps1", "description": "Fix async method naming violations"},
    {"errorCode": "CA1304", "scriptPath": ".cursor/scripts/quality/fix-culture-info.ps1", "description": "Fix string comparison culture issues"}
  ]
  ```
- `[STORE_SUCCESSFUL_SCRIPTS]`: Store successful fix scripts for reuse (`true`/`false`, default `true`)

## Reasoning Process

1. **Assess Current State**: Analyze project configurations, editorconfigs, and existing suppressions
2. **Check Available Fix Scripts**: Identify which automated fix scripts are available for detected errors
3. **Prioritize Fixes**: Run automated fix scripts first (fast, reliable), then manual fixes
4. **Identify Gaps**: Compare current settings against enforcement standards
5. **Plan Progression**: Determine appropriate phase based on current quality level
6. **Generate Actions**: Create specific commands and configuration changes
7. **Store Successful Scripts**: Save working fix scripts for future reuse
8. **Validate Safety**: Ensure changes won't break builds or introduce regressions

## Process

### Phase 1: Assessment & Analysis

#### Check Project Configurations

```bash
# Find all .csproj files in target
find "[TARGET_PATH]" -name "*.csproj" -type f

# Check current warning settings in each project
grep -n "TreatWarningsAsErrors\|WarningsAsErrors\|AnalysisLevel" "[TARGET_PATH]/**/*.csproj"
```

#### Analyze EditorConfig Settings

```bash
# Check .editorconfig files for severity settings
find "[TARGET_PATH]" -name ".editorconfig" -type f
cat "[TARGET_PATH]/.editorconfig" | grep -E "(warning|error|suggestion)"
```

#### Inventory Existing Suppressions

```bash
# Find all suppression files
find "[TARGET_PATH]" -name "*GlobalSuppressions.cs" -o -name "*.suppress" -type f

# Check for inline suppressions
grep -r "#pragma warning disable" "[TARGET_PATH]/src/" --include="*.cs" | wc -l
```

#### Analyze Current Build Status

```bash
# Test current build with warnings as errors
cd "[TARGET_PATH]"
dotnet build --configuration Release /p:TreatWarningsAsErrors=true 2>&1 | grep -E "(warning|error)" | head -20
```

### Phase 2: Automated Fix Scripts (NEW - Run First)

#### Identify Applicable Fix Scripts

For each reported error/warning, check if an automated fix script exists:

```powershell
# Parse fix scripts JSON and match against build errors
$fixScripts = $FixScripts | ConvertFrom-Json

foreach ($error in $buildErrors) {
    $matchingScript = $fixScripts | Where-Object { $_.errorCode -eq $error.Code }

    if ($matchingScript) {
        Write-Host "Found fix script for $($error.Code): $($matchingScript.description)"
        # Queue script for execution
    }
}
```

#### Execute Fix Scripts

Run available fix scripts before attempting manual fixes:

```powershell
# Execute each matching fix script
foreach ($script in $matchingScripts) {
    Write-Host "Running fix script: $($script.scriptPath)"

    try {
        # Run the fix script with appropriate parameters
        & $script.scriptPath -Path $TargetPath -WhatIf:$WhatIfMode

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Fix script succeeded: $($script.description)"
            $successfulScripts += $script
        } else {
            Write-Warning "Fix script failed, will try manual approach"
        }
    }
    catch {
        Write-Warning "Fix script error: $($_.Exception.Message)"
    }
}
```

#### Store Successful Scripts

Save working scripts for future reuse:

```powershell
# Store successful scripts in a reusable script registry
$registryPath = ".cursor/scripts/quality/script-registry.json"

$registry = if (Test-Path $registryPath) {
    Get-Content $registryPath | ConvertFrom-Json
} else {
    @{ scripts = @() }
}

foreach ($script in $successfulScripts) {
    $existingScript = $registry.scripts | Where-Object { $_.errorCode -eq $script.errorCode }

    if (-not $existingScript) {
        $registry.scripts += @{
            errorCode = $script.errorCode
            scriptPath = $script.scriptPath
            description = $script.description
            lastUsed = Get-Date -Format "yyyy-MM-dd"
            successCount = 1
        }
    } else {
        $existingScript.lastUsed = Get-Date -Format "yyyy-MM-dd"
        $existingScript.successCount++
    }
}

$registry | ConvertTo-Json -Depth 10 | Set-Content $registryPath
Write-Success "Stored $($successfulScripts.Count) successful scripts for reuse"
```

### Phase 3: Configuration Repair

#### Enable Warnings-as-Errors in Projects

```xml
<!-- Add to each .csproj file -->
<PropertyGroup>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <WarningsAsErrors />
  <AnalysisLevel>latest</AnalysisLevel>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
</PropertyGroup>
```

#### Configure EditorConfig for Strict Enforcement

```ini
# Add to .editorconfig
[*.cs]
dotnet_diagnostic.CA1304.severity = error
dotnet_diagnostic.CA1305.severity = error
dotnet_diagnostic.CA1062.severity = error
dotnet_diagnostic.CA1307.severity = error
dotnet_diagnostic.IDE1006.severity = error

# Culture/string issues
dotnet_diagnostic.CA1304.severity = error    # ToLower without culture
dotnet_diagnostic.CA1305.severity = error    # ToString without culture

# Null validation
dotnet_diagnostic.CA1062.severity = error    # null validation

# String comparison
dotnet_diagnostic.CA1307.severity = error    # StringComparison

# Naming conventions
dotnet_diagnostic.IDE1006.severity = error   # Missing underscore prefix
```

### Phase 3: Suppression Management

#### Create Global Suppressions File

```csharp
// GlobalSuppressions.cs (temporary, max [SUPPRESSION_DAYS] days)
using System.Diagnostics.CodeAnalysis;

[assembly: SuppressMessage("Naming", "IDE1006:Missing prefix: '_'", Justification = "Temporary suppression during gradual enforcement. Remove by [DATE]", Scope = "member", Target = "~M:MyClass.method")]
```

#### Inline Suppressions (Last Resort)

```csharp
#pragma warning disable CA1304 // ToLower without culture - TODO: Add CultureInfo.InvariantCulture
var lower = input.ToLower();
#pragma warning restore CA1304
```

### Phase 4: Gradual Tightening Strategy

#### Level 1: Culture/String Issues Only

- Enable: CA1304, CA1305
- Suppress: IDE1006, CA1062, CA1307
- Duration: 7 days

#### Level 2: Add Null Validation

- Keep: CA1304, CA1305
- Enable: CA1062
- Suppress: IDE1006, CA1307
- Duration: 14 days

#### Level 3: Add String Comparison

- Keep: CA1304, CA1305, CA1062
- Enable: CA1307
- Suppress: IDE1006
- Duration: 21 days

#### Level 4: Add Naming Conventions

- Enable: All (CA1304, CA1305, CA1062, CA1307, IDE1006)
- No suppressions
- Duration: Permanent

### Phase 5: CI/CD Integration

#### Generate CI/CD Validation Script

```powershell
# validate-code-quality.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('baseline','enforce','suppress','gradual','strict')]
    [string]$Phase,

    [Parameter(Mandatory=$false)]
    [int]$ToleranceLevel = 0
)

$ErrorActionPreference = 'Stop'

Write-Host "=== Code Quality Enforcement: $Phase Phase ===" -ForegroundColor Cyan

# Phase-specific validation logic
switch ($Phase) {
    'auto-fix' {
        # Run automated fix scripts first
        Write-Host "Running automated fix scripts..." -ForegroundColor Yellow

        $successfulFixes = 0
        $failedFixes = 0

        # Parse and execute fix scripts
        if ($FixScripts) {
            $scripts = $FixScripts | ConvertFrom-Json

            foreach ($script in $scripts) {
                Write-Host "  Executing: $($script.description)" -ForegroundColor Gray

                try {
                    & $script.scriptPath -Path $TargetPath -DryRun:$WhatIfMode

                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "  ✅ Success" -ForegroundColor Green
                        $successfulFixes++
                    } else {
                        Write-Host "  ❌ Failed" -ForegroundColor Red
                        $failedFixes++
                    }
                }
                catch {
                    Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
                    $failedFixes++
                }
            }

            # Store successful scripts for reuse
            if ($StoreSuccessfulScripts -and $successfulFixes -gt 0) {
                $registryPath = Join-Path $TargetPath ".cursor\scripts\quality\script-registry.json"

                $registry = if (Test-Path $registryPath) {
                    Get-Content $registryPath | ConvertFrom-Json
                } else {
                    @{ scripts = @(); lastUpdated = Get-Date -Format "yyyy-MM-dd" }
                }

                foreach ($script in $scripts) {
                    $existing = $registry.scripts | Where-Object { $_.errorCode -eq $script.errorCode }
                    if (-not $existing) {
                        $registry.scripts += @{
                            errorCode = $script.errorCode
                            scriptPath = $script.scriptPath
                            description = $script.description
                            successCount = 1
                            lastSuccess = Get-Date -Format "yyyy-MM-dd"
                        }
                    } else {
                        $existing.successCount++
                        $existing.lastSuccess = Get-Date -Format "yyyy-MM-dd"
                    }
                }

                $registry.lastUpdated = Get-Date -Format "yyyy-MM-dd"
                $registry | ConvertTo-Json -Depth 10 | Set-Content $registryPath

                Write-Host "Stored $successfulFixes successful scripts for reuse" -ForegroundColor Green
            }
        }

        Write-Host "Auto-fix phase complete: $successfulFixes succeeded, $failedFixes failed" -ForegroundColor Cyan

        if ($failedFixes -gt 0) {
            Write-Host "Some fixes failed - proceeding to manual enforcement phase" -ForegroundColor Yellow
            # Could automatically transition to 'enforce' phase here
        }
    }

    'baseline' {
        # Count current warnings/errors
        $result = dotnet build --configuration Release /p:TreatWarningsAsErrors=false 2>&1
        $warnings = ($result | Select-String "warning").Count
        $errors = ($result | Select-String "error").Count

        Write-Host "Current state: $warnings warnings, $errors errors" -ForegroundColor Yellow

        if ($warnings -eq 0 -and $errors -eq 0) {
            Write-Host "✅ Already at zero warnings/errors!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Need enforcement phase" -ForegroundColor Yellow
        }
    }

    'enforce' {
        # Enable warnings as errors
        Write-Host "Enabling warnings-as-errors..." -ForegroundColor Yellow

        # Update .csproj files
        Get-ChildItem -Recurse -Filter "*.csproj" | ForEach-Object {
            $content = Get-Content $_.FullName -Raw

            if ($content -notmatch "<TreatWarningsAsErrors>true</TreatWarningsAsErrors>") {
                $content = $content -replace "</PropertyGroup>", "  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>`n  </PropertyGroup>"
                Set-Content $_.FullName $content
                Write-Host "Updated: $($_.Name)" -ForegroundColor Green
            }
        }

        # Test build
        $result = dotnet build --configuration Release /p:TreatWarningsAsErrors=true 2>&1
        $errors = ($result | Select-String "error").Count

        if ($errors -eq 0) {
            Write-Host "✅ Enforcement successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ $errors errors found. Need suppression phase." -ForegroundColor Red
        }
    }

    'suppress' {
        # Add temporary suppressions
        Write-Host "Adding temporary suppressions..." -ForegroundColor Yellow

        $suppressions = @()

        # Scan for common patterns and create suppressions
        $result = dotnet build --configuration Release /p:TreatWarningsAsErrors=true 2>&1

        $result | Select-String "error (?<code>\w+):" | ForEach-Object {
            $code = $_.Matches.Groups['code'].Value
            $suppressions += "dotnet_diagnostic.$code.severity = warning"
        }

        # Update .editorconfig
        $editorConfig = ".editorconfig"
        if (Test-Path $editorConfig) {
            $content = Get-Content $editorConfig -Raw
        } else {
            $content = "[*.cs]`n"
        }

        foreach ($suppression in $suppressions) {
            if ($content -notmatch [regex]::Escape($suppression)) {
                $content += "`n$suppression"
            }
        }

        Set-Content $editorConfig $content
        Write-Host "Added $($suppressions.Count) temporary suppressions" -ForegroundColor Green
    }

    'gradual' {
        # Remove suppressions gradually
        Write-Host "Gradual tightening in progress..." -ForegroundColor Yellow

        $editorConfig = ".editorconfig"
        if (Test-Path $editorConfig) {
            $content = Get-Content $editorConfig -Raw

            # Remove culture-related suppressions first
            $content = $content -replace "dotnet_diagnostic\.CA1304\.severity = warning`n", ""
            $content = $content -replace "dotnet_diagnostic\.CA1305\.severity = warning`n", ""

            Set-Content $editorConfig $content
            Write-Host "Removed CA1304/CA1305 suppressions" -ForegroundColor Green
        }
    }

    'strict' {
        # Full enforcement, no suppressions
        Write-Host "Enforcing strict zero-tolerance policy..." -ForegroundColor Yellow

        $editorConfig = ".editorconfig"
        if (Test-Path $editorConfig) {
            $content = Get-Content $editorConfig -Raw

            # Remove all temporary suppressions
            $content = $content -replace "dotnet_diagnostic\.\w+\.severity = warning`n", ""

            Set-Content $editorConfig $content
        }

        # Test final build
        $result = dotnet build --configuration Release /p:TreatWarningsAsErrors=true 2>&1
        $errors = ($result | Select-String "error").Count

        if ($errors -eq 0) {
            Write-Host "✅ Strict enforcement achieved!" -ForegroundColor Green
        } else {
            Write-Host "❌ $errors errors remaining" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "=== Phase $Phase Complete ===" -ForegroundColor Cyan
```

#### CI/CD Pipeline Integration

```yaml
# Add to azure-pipelines.yml
- task: PowerShell@2
  displayName: 'Auto-Fix Known Code Quality Issues'
  inputs:
    targetType: 'inline'
    script: |
      $fixScripts = @'
      [
        {"errorCode":"IDE1006","scriptPath":".cursor/scripts/quality/fix-async-method-naming.ps1","description":"Fix async method naming"},
        {"errorCode":"CA1304","scriptPath":".cursor/scripts/quality/fix-culture-info.ps1","description":"Fix culture info issues"}
      ]
      '@
      ./scripts/validate-code-quality.ps1 -Phase auto-fix -FixScripts $fixScripts

- task: PowerShell@2
  displayName: 'Validate Code Quality Enforcement'
  inputs:
    targetType: 'inline'
    script: |
      ./scripts/validate-code-quality.ps1 -Phase $(QualityPhase) -ToleranceLevel $(WarningTolerance)

# Pipeline variables
variables:
  QualityPhase: 'enforce'  # Change gradually: auto-fix -> enforce -> suppress -> gradual -> strict
  WarningTolerance: 0
```

## Examples

### Example 1: Automated Fix Scripts

```text
@manage-code-quality-enforcement src/MyProject/ auto-fix --fix-scripts '[{"errorCode":"IDE1006","scriptPath":".cursor/scripts/quality/fix-async-method-naming.ps1","description":"Fix async method naming violations"}]'

Auto-Fix Phase Results:
✅ Found fix script for IDE1006: Fix async method naming violations
✅ Executed script: .cursor/scripts/quality/fix-async-method-naming.ps1
✅ Fixed 8 async method naming violations
✅ Stored successful script for reuse

Status: Automated fixes completed successfully
```

### Example 2: Initial Assessment

```text
@manage-code-quality-enforcement src/MyProject/
Current phase: baseline

Assessment Results:
- 15 warnings currently ignored
- 3 CA1304 culture issues
- 8 IDE1006 naming violations
- 4 CA1062 null validation issues

Recommendation: Run 'auto-fix' phase first to resolve known issues automatically
```

### Example 5: CI/CD Integration

```text
@manage-code-quality-enforcement src/MyProject/ --ci-cd

Generated Files:
✅ scripts/validate-code-quality.ps1 - PowerShell validation script
✅ .editorconfig - Updated with quality rules
✅ azure-pipelines.yml - Added quality validation step

Pipeline Variables Set:
- QualityPhase: enforce
- WarningTolerance: 0

Next: Configure pipeline to use generated scripts
```

### Example 6: Strict Mode (Production Ready)

```text
@manage-code-quality-enforcement src/MyProject/ strict

Final Validation Results:
✅ Build: SUCCESS (0 warnings, 0 errors)
✅ All suppressions removed
✅ Code analysis: PASSED
✅ Documentation: COMPLETE

Status: PRODUCTION READY - Zero tolerance achieved!
```

### Example 2: Enable Enforcement

```text
@manage-code-quality-enforcement src/MyProject/ enforce

Actions Taken:
✅ Updated MyProject.csproj: Added <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
✅ Updated .editorconfig: Set severity levels to 'error'
✅ Build test: 15 errors found

Next: Run 'suppress' phase to add temporary suppressions
```

### Example 3: Add Suppressions

```text
@manage-code-quality-enforcement src/MyProject/ suppress

Suppressions Added:
- dotnet_diagnostic.CA1304.severity = warning (3 instances)
- dotnet_diagnostic.IDE1006.severity = warning (8 instances)
- dotnet_diagnostic.CA1062.severity = warning (4 instances)

Build now passes with temporary suppressions.
Valid until: 2025-12-30 (30 days from now)
```

### Example 4: Gradual Tightening

```text
@manage-code-quality-enforcement src/MyProject/ gradual

Gradual Phase Applied:
- Removed CA1304 suppressions (culture issues)
- Kept IDE1006 suppressions (naming, more complex)
- Build: 3 errors remaining

Fix the 3 CA1304 issues, then advance to next level
```

## Output Format

### Assessment Report

```markdown
## Code Quality Enforcement Assessment

**Target**: [TARGET_PATH]
**Date**: [TIMESTAMP]
**Phase**: [CURRENT_PHASE]

### Current State
- **Projects**: [count] .csproj files found
- **Build Status**: [PASS/FAIL] with [X] warnings, [Y] errors
- **Suppressions**: [Z] active suppressions found

### Issues by Category
| Category | Count | Severity | Action |
|----------|-------|----------|--------|
| CA1304 (Culture) | 3 | High | Fix immediately |
| IDE1006 (Naming) | 8 | Medium | Gradual fix |
| CA1062 (Null) | 4 | High | Fix in batches |

### Recommendations
1. **Immediate**: Enable warnings-as-errors in all projects
2. **Short-term**: Add temporary suppressions for existing issues
3. **Medium-term**: Gradual removal of suppressions over 30 days
4. **Long-term**: Strict zero-tolerance policy

**Next Phase**: [RECOMMENDED_PHASE]
```

### Action Report

```markdown
## Code Quality Enforcement Actions

**Target**: [TARGET_PATH]
**Phase**: [EXECUTED_PHASE]
**Date**: [TIMESTAMP]

### Files Modified
- ✅ `MyProject.csproj`: Added `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
- ✅ `.editorconfig`: Updated severity settings
- ✅ `GlobalSuppressions.cs`: Added temporary suppressions

### Build Validation
- **Before**: 15 warnings, 0 errors
- **After**: 0 warnings, 15 errors (expected with enforcement)
- **With Suppressions**: 0 warnings, 0 errors (temporary)

### Next Steps
1. **Fix Issues**: Address suppressed warnings systematically
2. **Schedule Review**: Reassess suppressions in 30 days
3. **Advance Phase**: Move to 'gradual' phase when ready

**CI/CD Updated**: Added validation step to pipeline
```

## Validation Checklist

Before claiming code quality enforcement is properly configured:

- [ ] Automated fix scripts were attempted first for known error codes
- [ ] Successful fix scripts were stored in registry for future reuse
- [ ] All .csproj files have `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
- [ ] .editorconfig has appropriate severity settings for target enforcement phase
- [ ] Build passes in current enforcement level (warnings treated as errors)
- [ ] Temporary suppressions are documented with expiration dates and review schedules
- [ ] CI/CD pipeline includes quality validation step with appropriate phase
- [ ] Gradual tightening plan is documented with specific timelines and milestones
- [ ] GlobalSuppressions.cs file exists and contains only temporary suppressions
- [ ] AnalysisLevel is set to 'latest' in all project files
- [ ] EnableNETAnalyzers is set to true for comprehensive analysis
- [ ] Fix script registry is updated with successful scripts for team reuse

## Usage Modes

### Basic Mode (Quick Assessment)

For simple projects or when you just want to enable warnings-as-errors:

```text
@manage-code-quality-enforcement src/MyProject/
```

Runs baseline assessment and recommends next steps.

### Enforcement Mode (Enable Strict Checking)

For projects ready to enforce quality standards:

```text
@manage-code-quality-enforcement src/MyProject/ enforce
```

Enables warnings-as-errors and validates the change.

### Suppression Mode (Add Temporary Fixes)

When build fails after enforcement and you need temporary suppressions:

```text
@manage-code-quality-enforcement src/MyProject/ suppress
```

Adds temporary suppressions with automatic expiration.

### Gradual Mode (Progressive Improvement)

For systematic quality improvement over time:

```text
@manage-code-quality-enforcement src/MyProject/ gradual
```

Removes suppressions gradually based on the tightening schedule.

### Strict Mode (Zero Tolerance)

For production-ready code with no warnings or errors:

```text
@manage-code-quality-enforcement src/MyProject/ strict
```

Enforces absolute zero-tolerance policy.

## Troubleshooting

### Issue: Build Fails After Enforcement

**Symptoms**: `dotnet build` fails with many errors after enabling warnings-as-errors
**Cause**: Existing code has warnings that are now treated as errors
**Solutions**:

1. **Quick Fix**: Run suppression mode to add temporary suppressions
2. **Long-term Fix**: Run gradual mode to fix issues systematically
3. **Check Specific Errors**: Review error messages to identify patterns

### Issue: Suppressions Not Working

**Symptoms**: Build still fails even after adding suppressions
**Cause**: Suppressions may not match exact error codes or locations
**Solutions**:

1. **Verify Error Codes**: Check that suppression codes match actual warnings
2. **Check File Paths**: Ensure suppressions target correct files
3. **Use GlobalSuppressions.cs**: Add suppressions to global file instead of inline

### Issue: Too Many Suppressions

**Symptoms**: Hundreds of suppressions added, feels overwhelming
**Cause**: Trying to fix too much at once
**Solutions**:

1. **Use Gradual Mode**: Fix issues in phases over time
2. **Prioritize by Impact**: Focus on high-impact warnings first
3. **Set Tolerance Level**: Use `--tolerance-level 10` to allow some warnings

## Advanced Features

### Custom Phases

You can create custom enforcement phases by modifying the PowerShell script:

```powershell
# Add custom phase logic
switch ($Phase) {
    'custom' {
        # Your custom enforcement logic
        Write-Host "Applying custom quality rules..." -ForegroundColor Yellow
    }
}
```

### Quality Metrics Tracking

Generate comprehensive quality reports:

```powershell
# Quality metrics report
$metrics = @{
    TotalFiles = (Get-ChildItem -Recurse -Filter "*.cs").Count
    TotalWarnings = $currentWarnings
    SuppressionsActive = $activeSuppressions.Count
    BuildPassRate = if ($buildSuccess) { 100 } else { 0 }
    AverageFixTime = "2.5 days"
}

Write-Host "=== Quality Enforcement Metrics ===" -ForegroundColor Cyan
$metrics.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)" -ForegroundColor White
}
```

## Related Prompts

- `check-naming-conventions` - Specific naming convention validation
- `refactor-for-clean-code` - Code quality improvement
- `iterative-refinement` - Gradual improvement approach
- `report-errors` - Error analysis and reporting
- `fix-diag-warn-err.prompt.md` - Fix all analyzer diagnostics with zero tolerance

## Related Rules

- `rule.quality.zero-warnings-zero-errors.v1` - Zero tolerance policy
- `rule.quality.diagnostic-messages.v1` - Quality error reporting
- `rule.quality.code-quality-enforcement-rule.mdc` - Systematic enforcement patterns
- `rule.scripts.core-principles.v1` - Script portability and reusability standards
- `rule.scripts.powershell-standards.v1` - PowerShell script quality requirements
- `rule.cicd.pre-build-validation.v1` - CI/CD integration patterns
- `rule.cicd.tag-based-versioning-rule.mdc` - Version control integration
- `rule.ticket.workflow.v1` - Ticket-based gradual enforcement
- `rule.ticket.complexity-assessment-rule.mdc` - Implementation strategy selection
- `rule.development.commit-message.mdc` - Quality commit standards

## Fix Script Registry

### Script Storage Format

Successful fix scripts are stored in `.cursor/scripts/quality/script-registry.json`:

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

### Script Discovery

The prompt automatically discovers available fix scripts from:
1. **Explicit parameter**: `[FIX_SCRIPTS]` JSON array
2. **Registry file**: Previously successful scripts
3. **Standard locations**: `.cursor/scripts/quality/*.ps1` files with error code prefixes

### Best Practice: Proven Scripts First

**Always prefer proven scripts over creating new ones:**
- ✅ **Reuse existing**: Scripts that have worked multiple times
- ✅ **Test before trust**: New scripts should be validated before wide use
- ✅ **Collect successes**: Store working scripts in registry for team reuse
- ❌ **Avoid recreation**: Don't rewrite working scripts unless significantly improved
