---
name: Add Webhook Notifications
description: "Add webhook notifications to Teams or Slack for script events"
category: script
tags: [webhooks, notifications, teams, slack, enhancement]
---

# Add Webhook Notifications (Teams/Slack)

## Context

Add webhook notifications to Teams or Slack for script completion status, failures, and metrics.

## Instructions

### PowerShell

Use `Send-TeamsNotification` from [webhooks exemplar](../../exemplars/script/powershell/webhooks.exemplar.md):
```powershell
if ($env:TEAMS_WEBHOOK_URL) {
    Send-TeamsNotification `
        -WebhookUrl $env:TEAMS_WEBHOOK_URL `
        -Title "Script Complete" `
        -Message "Results ready" `
        -Facts @{ "Status" = "Success"; "Duration" = "5m" } `
        -Status "Good"
}
```

### Python

Use `send_teams_notification` from [webhooks exemplar](../../exemplars/script/python/webhooks.exemplar.md).

## Quality Checklist

- [ ] Webhook URL from environment variable (not hardcoded)
- [ ] Graceful degradation if webhook fails (script continues)
- [ ] Color-coded by status (green/yellow/red)
- [ ] Includes useful facts (duration, counts, metrics)
- [ ] Only sends if webhook URL configured

---
Produced-by: prompt.scripts.add-webhooks.v1 | ts=2025-12-07T00:00:00Z
