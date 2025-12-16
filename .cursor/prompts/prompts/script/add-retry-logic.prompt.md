---
name: Add Retry Logic
description: "Add retry logic with exponential backoff for resilient scripts"
category: script
tags: [retry, resilience, error-handling, enhancement]
---

# Add Retry Logic with Exponential Backoff

## Context

Add retry logic with exponential backoff for network operations, API calls, or external services that may experience transient failures.

## Instructions

### PowerShell

1. Add `Invoke-WithRetry` function from [retry exemplar](../../exemplars/script/powershell/retry.exemplar.md)
2. Wrap network/API calls:
```powershell
Invoke-WithRetry {
    Invoke-RestMethod -Uri $apiUrl -Method Post -Body $data
} -MaxRetries 3 -DelaySeconds 5
```

### Python

1. Add `@retry` decorator from [retry exemplar](../../exemplars/script/python/retry.exemplar.md)
2. Decorate functions:
```python
@retry(max_attempts=3, delay=5, exceptions=(requests.RequestException,))
def fetch_data(url: str) -> Dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

## Quality Checklist

- [ ] Exponential backoff implemented (delays: 5s, 10s, 20s)
- [ ] Configurable max attempts
- [ ] Only retries transient errors (not permanent failures)
- [ ] Logs retry attempts at WARN level
- [ ] Final error thrown after exhausting retries

---
Produced-by: prompt.scripts.add-retry.v1 | ts=2025-12-07T00:00:00Z
