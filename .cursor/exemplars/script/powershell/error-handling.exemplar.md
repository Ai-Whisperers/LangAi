# PowerShell Error Handling Pattern Exemplar

## Overview

Robust error handling with try/catch/finally, proper error action preferences, and exit code checking ensures scripts fail gracefully with actionable error messages.

## When to Use

- **Use for**: All production scripts (Standard quality level and above)
- **Critical for**: Scripts calling external commands, file operations, network operations
- **Skip for**: Simple prototype scripts where failure is obvious

## Good Pattern ✅

```powershell
$ErrorActionPreference = "Stop"

try {
    Write-Host "Running tests..."
    dotnet test --configuration $Configuration

    if ($LASTEXITCODE -ne 0) {
        throw "Tests failed with exit code $LASTEXITCODE"
    }

    Write-Host "✅ Tests passed!" -ForegroundColor Green
}
catch {
    Write-Host "##vso[task.logissue type=error]$($_.Exception.Message)"
    Write-Host "Failed to run tests. Check build configuration and test projects."
    exit 1
}
finally {
    # Clean up temp files
    Remove-Item -Path "$env:TEMP/temp-coverage-*" -Force -ErrorAction SilentlyContinue
}
```

**Why this is good:**
- **ErrorActionPreference = "Stop"**: Treats all errors as terminating, prevents silent failures
- **Exit code checking**: `$LASTEXITCODE -ne 0` catches external command failures
- **Actionable error messages**: "Check build configuration and test projects" tells user what to investigate
- **Azure Pipelines integration**: `##vso[task.logissue type=error]` creates pipeline error
- **Resource cleanup**: `finally` block ensures temp files are removed even on error

## Bad Pattern ❌

```powershell
# ❌ No $ErrorActionPreference set (defaults to Continue - silent failures)

# ❌ No try/catch
dotnet test --configuration $Configuration

# ❌ No exit code check
Write-Host "Tests complete"

# ❌ No cleanup
# Temp files left behind on error
```

**Why this is bad:**
- **Silent failures**: Errors don't terminate script, continues with invalid state
- **No exit code handling**: External command fails but script reports success
- **Vague error info**: User doesn't know what went wrong or how to fix it
- **Resource leaks**: Temp files accumulate over time
- **Pipeline confusion**: CI/CD shows green even though tests failed

## Error Handling Best Practices

### Check File Operations

```powershell
try {
    $content = Get-Content $FilePath -ErrorAction Stop
}
catch [System.IO.FileNotFoundException] {
    Write-Host "##vso[task.logissue type=error]File not found: $FilePath"
    Write-Host "Ensure the file exists before running this script."
    exit 1
}
```

### Multiple External Commands

```powershell
try {
    dotnet build --configuration $Configuration
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }

    dotnet test --no-build
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }

    dotnet pack --no-build
    if ($LASTEXITCODE -ne 0) { throw "Pack failed" }
}
catch {
    Write-Host "##vso[task.logissue type=error]$($_.Exception.Message)"
    exit 1
}
```

### Detailed Error Context

```powershell
catch {
    $errorDetails = @{
        Message = $_.Exception.Message
        ScriptLine = $_.InvocationInfo.ScriptLineNumber
        Command = $_.InvocationInfo.MyCommand.Name
    }

    Write-Host "ERROR: $($errorDetails.Message)"
    Write-Host "  At: $($errorDetails.Command):$($errorDetails.ScriptLine)"

    # Log to file for debugging
    $errorDetails | ConvertTo-Json | Out-File "$env:TEMP/error.json"

    exit 1
}
```

## Performance Characteristics

- **Negligible overhead**: Error handling adds <1ms to execution time
- **Fail fast**: Script terminates immediately on error, doesn't waste time
- **Clear diagnostics**: Detailed error info accelerates troubleshooting

## Related Patterns

- [Parameters](./parameters.exemplar.md) - Validation prevents many errors at script start
- [Portability](./portability.exemplar.md) - Environment detection reduces error cases
- See also: `rule.scripts.core-principles.v1` section "Error Handling Must Be Robust"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
