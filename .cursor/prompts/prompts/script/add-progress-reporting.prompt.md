---
name: Add Progress Reporting
description: "Add progress bars and status reporting to long-running scripts"
category: script
tags: [progress, reporting, user-experience, enhancement]
---

# Add Progress Reporting

## Context

Add progress reporting for long-running operations (>10 seconds) to provide user feedback.

## Instructions

### PowerShell

Use `Write-Progress` from [progress exemplar](../../exemplars/script/powershell/progress.exemplar.md):
```powershell
foreach ($item in $items) {
    $current++
    $percent = ($current / $total) * 100
    
    Write-Progress -Activity "Processing" `
                   -Status "$current of $total" `
                   -PercentComplete $percent
    
    # Process item
}

Write-Progress -Activity "Processing" -Completed
```

### Python

Use Rich Progress from [rich-ui exemplar](../../exemplars/script/python/rich-ui.exemplar.md).

## Quality Checklist

- [ ] Progress bar shows percent complete
- [ ] Status shows current item/count
- [ ] Progress cleared on completion (-Completed)
- [ ] Updated every iteration (for <1000 items) or every N iterations
- [ ] Only used for operations >10 seconds

---
Produced-by: prompt.scripts.add-progress.v1 | ts=2025-12-07T00:00:00Z

