# Python Webhook Notifications Pattern Exemplar

## Overview

Webhook notifications to Microsoft Teams or Slack provide team awareness of script execution status (Production quality level feature).

## When to Use

- **Use for**: Production quality level scripts, critical automation, team notifications
- **Skip for**: Development-only scripts, single-user tools

## Good Pattern ✅

```python
import requests
from typing import Dict, Optional
from enum import Enum

class NotificationStatus(Enum):
    """Notification status levels."""
    SUCCESS = ("00FF00", "✅")
    WARNING = ("FFA500", "⚠️")
    ERROR = ("FF0000", "❌")

def send_teams_notification(
    webhook_url: str,
    title: str,
    message: str,
    facts: Optional[Dict[str, str]] = None,
    status: NotificationStatus = NotificationStatus.SUCCESS
) -> bool:
    """Send notification to Microsoft Teams."""
    color, icon = status.value
    
    sections = []
    if facts:
        sections.append({
            "facts": [{"name": k, "value": str(v)} for k, v in facts.items()]
        })
    
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": color,
        "title": f"{icon} {title}",
        "text": message,
        "sections": sections
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.debug("Teams notification sent successfully")
        return True
    except requests.RequestException as e:
        logger.warning(f"Failed to send Teams notification: {e}")
        return False

# Usage:
webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

if webhook_url:
    status = NotificationStatus.SUCCESS if all_passed else NotificationStatus.ERROR
    
    send_teams_notification(
        webhook_url=webhook_url,
        title="Coverage Analysis Complete",
        message=f"Build #{build_number} coverage analysis",
        facts={
            "Line Coverage": f"{line_coverage:.2f}%",
            "Status": "Passed" if all_passed else "Failed",
            "Build": build_number
        },
        status=status
    )
```

**Why this is good:**
- Environment variable config (secure)
- Enum for status types
- Graceful degradation
- Color-coded cards

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

