# PowerShell Webhook Notifications Pattern Exemplar

## Overview

Webhook notifications to Microsoft Teams or Slack provide team awareness of script execution status, failures, and metrics.

## When to Use

- **Use for**: Production quality level scripts, CI/CD pipelines, critical automation
- **Critical for**: Team notifications, failure alerts, deployment status
- **Skip for**: Development-only scripts, single-user tools

## Good Pattern ✅

```powershell
function Send-TeamsNotification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$WebhookUrl,

        [Parameter(Mandatory=$true)]
        [string]$Title,

        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$false)]
        [hashtable]$Facts,

        [Parameter(Mandatory=$false)]
        [ValidateSet("Good", "Warning", "Error")]
        [string]$Status = "Good"
    )

    $color = switch ($Status) {
        "Good"    { "00FF00" }  # Green
        "Warning" { "FFA500" }  # Orange
        "Error"   { "FF0000" }  # Red
    }

    $factsSections = if ($Facts) {
        @(
            @{
                facts = ($Facts.GetEnumerator() | ForEach-Object {
                    @{name = $_.Key; value = $_.Value.ToString()}
                })
            }
        )
    } else { @() }

    $body = @{
        "@type" = "MessageCard"
        "@context" = "https://schema.org/extensions"
        themeColor = $color
        title = $Title
        text = $Message
        sections = $factsSections
    } | ConvertTo-Json -Depth 10

    try {
        Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body $body -ContentType "application/json" | Out-Null
        Write-Verbose "Teams notification sent successfully"
    }
    catch {
        Write-Warning "Failed to send Teams notification: $($_.Exception.Message)"
    }
}

# Usage:
if ($env:TEAMS_WEBHOOK_URL) {
    $status = if ($failed) { "Error" } else { "Good" }

    Send-TeamsNotification `
        -WebhookUrl $env:TEAMS_WEBHOOK_URL `
        -Title "Coverage Analysis: $env:BUILD_REPOSITORY_NAME" `
        -Message "Build #$env:BUILD_BUILDNUMBER completed" `
        -Facts @{
            "Line Coverage" = "$([Math]::Round($lineRate, 2))%"
            "Branch Coverage" = "$([Math]::Round($branchRate, 2))%"
            "Status" = if($failed) {"Failed ❌"} else {"Passed ✅"}
            "Build" = "$env:BUILD_BUILDNUMBER"
            "Commit" = (git rev-parse --short HEAD)
        } `
        -Status $status
}
```

**Why this is good:**
- **Graceful degradation**: Continues if webhook fails (try/catch with warning)
- **Environment variable config**: Webhook URL from `$env:TEAMS_WEBHOOK_URL` (secure)
- **Rich formatting**: Color-coded cards with structured facts
- **Status mapping**: Good/Warning/Error maps to green/orange/red
- **Conditional sending**: Only sends if webhook URL configured

## Bad Pattern ❌

```powershell
# ❌ Hardcoded webhook URL (security risk)
$webhookUrl = "https://outlook.office.com/webhook/abc123/..."

# ❌ No error handling - script fails if webhook fails
Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body

# ❌ Plain text message (no structure)
$body = "Build completed: $status"

# ❌ Always sends (no conditional logic)
```

**Why this is bad:**
- **Security risk**: Hardcoded webhook URL in source code
- **Script failure**: Webhook failure causes script failure (not graceful)
- **Poor formatting**: Plain text, no structure or color coding
- **No flexibility**: Can't disable notifications without editing script

## Webhook Best Practices

### Multiple Webhook Support

```powershell
$webhooks = @()
if ($env:TEAMS_WEBHOOK_URL) { $webhooks += $env:TEAMS_WEBHOOK_URL }
if ($env:SLACK_WEBHOOK_URL) { $webhooks += $env:SLACK_WEBHOOK_URL }

foreach ($webhook in $webhooks) {
    Send-Notification -WebhookUrl $webhook -Title $title -Message $message
}
```

### Notification Throttling

```powershell
# Only notify on failure or significant changes
$shouldNotify = $false

if ($failed) {
    $shouldNotify = $true  # Always notify on failure
}
elseif ($coverageDelta -gt 5) {
    $shouldNotify = $true  # Notify if coverage improved >5%
}

if ($shouldNotify -and $env:TEAMS_WEBHOOK_URL) {
    Send-TeamsNotification -WebhookUrl $env:TEAMS_WEBHOOK_URL -Title "..."
}
```

### Adaptive Card Format (Advanced)

```powershell
$adaptiveCard = @{
    type = "message"
    attachments = @(
        @{
            contentType = "application/vnd.microsoft.card.adaptive"
            content = @{
                type = "AdaptiveCard"
                version = "1.2"
                body = @(
                    @{
                        type = "TextBlock"
                        size = "Large"
                        weight = "Bolder"
                        text = $Title
                    }
                    @{
                        type = "FactSet"
                        facts = $Facts.GetEnumerator() | ForEach-Object {
                            @{ title = $_.Key; value = $_.Value }
                        }
                    }
                )
            }
        }
    )
} | ConvertTo-Json -Depth 20
```

## Performance Characteristics

- **Latency**: 100-500ms per webhook call
- **Async recommended**: For multiple webhooks, consider background jobs
- **Failure tolerance**: Graceful degradation ensures script continues

## Related Patterns

- [Logging](./logging.exemplar.md) - Log webhook send attempts
- [Error Handling](./error-handling.exemplar.md) - Graceful failure handling
- See also: `rule.scripts.powershell-standards.v1` section "Webhook Notifications"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
