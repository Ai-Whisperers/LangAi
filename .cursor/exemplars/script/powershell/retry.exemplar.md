# PowerShell Retry Logic Pattern Exemplar

## Overview

Retry logic with exponential backoff automatically handles transient failures for network operations, API calls, and external services.

## When to Use

- **Use for**: Advanced quality level scripts, network operations, API calls, external services
- **Critical for**: Production scripts, unreliable networks, cloud services
- **Skip for**: Local file operations, deterministic errors, user-cancellable operations

## Good Pattern ✅

```powershell
function Invoke-WithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$ScriptBlock,
        
        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 3,
        
        [Parameter(Mandatory=$false)]
        [int]$DelaySeconds = 5,
        
        [Parameter(Mandatory=$false)]
        [int]$BackoffMultiplier = 2
    )
    
    $attempt = 1
    $currentDelay = $DelaySeconds
    
    while ($attempt -le $MaxRetries) {
        try {
            return & $ScriptBlock
        }
        catch {
            if ($attempt -eq $MaxRetries) {
                Write-Log "All $MaxRetries retry attempts failed" -Level ERROR
                throw
            }
            
            Write-Log "Attempt $attempt failed: $($_.Exception.Message). Retrying in ${currentDelay}s..." -Level WARN
            Start-Sleep -Seconds $currentDelay
            
            $currentDelay *= $BackoffMultiplier
            $attempt++
        }
    }
}

# Usage:
Invoke-WithRetry {
    dotnet tool install --global dotnet-reportgenerator-globaltool --version 5.3.11
} -MaxRetries 3 -DelaySeconds 5

Invoke-WithRetry {
    Invoke-RestMethod -Uri $apiEndpoint -Method Post -Body $data
} -MaxRetries 5 -DelaySeconds 10
```

**Why this is good:**
- **Exponential backoff**: Delays increase (5s, 10s, 20s) reducing server load
- **Configurable**: MaxRetries, initial delay, backoff multiplier
- **Transient failure handling**: Network glitches, rate limits, timeouts
- **Final error propagation**: Throws after exhausting retries
- **Logging**: Warns on retry, errors on final failure

## Bad Pattern ❌

```powershell
# ❌ No retry - fails on first transient error
try {
    Invoke-RestMethod -Uri $apiEndpoint -Method Post -Body $data
}
catch {
    Write-Error "API call failed"
    throw
}

# ❌ Fixed delay retry (hammers server)
$retries = 3
foreach ($i in 1..$retries) {
    try {
        Invoke-RestMethod -Uri $apiEndpoint -Method Post -Body $data
        break
    }
    catch {
        Start-Sleep -Seconds 5  # Always 5 seconds - not exponential
    }
}
```

**Why this is bad:**
- **No retry**: Transient network errors cause permanent failure
- **Fixed delay**: Doesn't reduce load on overloaded servers
- **Server hammering**: Retries immediately or at fixed interval
- **No max attempts**: Could retry forever
- **Poor logging**: Doesn't indicate retry attempts

## Retry Best Practices

### Selective Retry (Only Transient Errors)

```powershell
function Invoke-WithRetry {
    param($ScriptBlock, $MaxRetries = 3)
    
    $attempt = 1
    $delay = 5
    
    while ($attempt -le $MaxRetries) {
        try {
            return & $ScriptBlock
        }
        catch {
            $isTransient = $false
            
            # Check if error is transient
            if ($_.Exception -is [System.Net.WebException]) {
                $status = $_.Exception.Response.StatusCode
                # Retry on timeout, rate limit, server errors
                $isTransient = $status -in @(408, 429, 500, 502, 503, 504)
            }
            
            if (-not $isTransient -or $attempt -eq $MaxRetries) {
                throw
            }
            
            Write-Log "Transient error, retrying..." -Level WARN
            Start-Sleep -Seconds $delay
            $delay *= 2
            $attempt++
        }
    }
}
```

### Jittered Exponential Backoff

```powershell
# Add randomness to prevent thundering herd
$jitter = Get-Random -Minimum 0 -Maximum ($currentDelay * 0.3)
$delayWithJitter = $currentDelay + $jitter

Write-Log "Retrying in $([Math]::Round($delayWithJitter, 1))s..." -Level WARN
Start-Sleep -Seconds $delayWithJitter
```

### Timeout Configuration

```powershell
Invoke-WithRetry {
    $timeoutMs = 30000  # 30 seconds
    Invoke-RestMethod -Uri $url -TimeoutSec ($timeoutMs / 1000)
} -MaxRetries 3
```

## Performance Characteristics

- **Total retry time**: With 3 retries at 5s, 10s, 20s = 35s max overhead
- **Success on retry**: Most transient errors resolve in 1-2 retries
- **Reduced failures**: 90%+ reduction in transient failure rate

**Retry Timing Examples**:
- 3 retries, 5s delay, 2x multiplier: 5s, 10s, 20s = 35s total
- 5 retries, 10s delay, 2x multiplier: 10s, 20s, 40s, 80s, 160s = 310s total

## Related Patterns

- [Error Handling](./error-handling.exemplar.md) - Retry integrates with error handling
- [Logging](./logging.exemplar.md) - Log retry attempts
- See also: `rule.scripts.powershell-standards.v1` section "Retry Logic"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

