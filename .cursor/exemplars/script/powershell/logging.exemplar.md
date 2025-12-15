# PowerShell Structured Logging Pattern Exemplar

## Overview

Structured logging with severity levels (INFO, WARN, ERROR, DEBUG, SUCCESS) provides consistent, colorized output with Azure Pipelines integration.

## When to Use

- **Use for**: Advanced quality level scripts, production scripts, complex workflows
- **Critical for**: Debugging, operational visibility, CI/CD diagnostics
- **Skip for**: Simple scripts where Write-Host is sufficient

## Good Pattern ✅

```powershell
function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG", "SUCCESS")]
        [string]$Level = "INFO",
        
        [Parameter(Mandatory=$false)]
        [string]$LogFile
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        "ERROR"   { Write-Host $logMessage -ForegroundColor Red }
        "WARN"    { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "DEBUG"   { Write-Verbose $logMessage }
        default   { Write-Host $logMessage }
    }
    
    # Azure Pipelines task logging
    if ($env:AGENT_TEMPDIRECTORY) {
        switch ($Level) {
            "ERROR" { Write-Host "##vso[task.logissue type=error]$Message" }
            "WARN"  { Write-Host "##vso[task.logissue type=warning]$Message" }
        }
    }
    
    # File logging (optional)
    if ($LogFile) {
        Add-Content -Path $LogFile -Value $logMessage
    }
}

# Usage:
Write-Log "Starting coverage analysis" -Level INFO
Write-Log "Coverage below threshold" -Level WARN
Write-Log "Build failed" -Level ERROR
Write-Log "All thresholds met!" -Level SUCCESS
Write-Log "Processing package: $packageName" -Level DEBUG
```

**Why this is good:**
- **Severity levels**: Clear distinction between INFO, WARN, ERROR
- **Timestamps**: Every message includes when it occurred
- **Colorized output**: Easy visual scanning of logs
- **Azure Pipelines integration**: Errors/warnings show in pipeline summary
- **File logging option**: Can persist logs for audit/debugging
- **DEBUG level**: Detailed output via -Verbose flag

## Bad Pattern ❌

```powershell
# ❌ Inconsistent, no structure
Write-Host "Starting analysis"
Write-Warning "Coverage is low"
Write-Error "Failed!"
Write-Host "Done"

# ❌ No timestamps
# ❌ No Azure Pipelines integration
# ❌ No file logging
# ❌ Inconsistent formatting
```

**Why this is bad:**
- **No timestamps**: Can't correlate events or measure duration
- **Inconsistent format**: Hard to parse or filter logs
- **No severity levels**: Can't filter by importance
- **CI/CD unfriendly**: Warnings/errors don't surface in pipeline UI

## Advanced Logging Patterns

### Log File Rotation

```powershell
function Get-LogFilePath {
    $date = Get-Date -Format "yyyy-MM-dd"
    $logDir = "$env:TEMP/script-logs"
    
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }
    
    return Join-Path $logDir "script-$date.log"
}

$logFile = Get-LogFilePath
Write-Log "Script started" -LogFile $logFile
```

### Performance Logging

```powershell
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# Do work...

$stopwatch.Stop()
Write-Log "Operation completed in $($stopwatch.Elapsed.TotalSeconds)s" -Level INFO
```

### Contextual Logging

```powershell
function Write-ContextLog {
    param($Message, $Level = "INFO", $Context = @{})
    
    $contextStr = ($Context.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ", "
    Write-Log "$Message | $contextStr" -Level $Level
}

Write-ContextLog "Processing package" -Context @{
    Package = "MyLib"
    Version = "1.2.3"
    Coverage = "85.5%"
}
# Output: [2025-12-07 14:30:15] [INFO] Processing package | Package=MyLib, Version=1.2.3, Coverage=85.5%
```

## Performance Characteristics

- **Minimal overhead**: <1ms per log statement
- **File I/O impact**: Async file writes recommended for high-volume logging
- **Verbosity control**: DEBUG level only outputs with -Verbose flag

## Related Patterns

- [Error Handling](./error-handling.exemplar.md) - Log errors with context
- [Progress](./progress.exemplar.md) - Combine with progress reporting
- See also: `rule.scripts.powershell-standards.v1` section "Structured Logging"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

