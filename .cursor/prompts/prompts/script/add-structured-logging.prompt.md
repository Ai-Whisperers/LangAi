---
name: Add Structured Logging
description: "Add structured logging with log levels and file output"
category: script
tags: [logging, observability, debugging, enhancement]
---

# Add Structured Logging with Levels

## Context

Add structured logging with severity levels (INFO, WARN, ERROR, DEBUG) for production visibility.

## Instructions

### PowerShell

Add `Write-Log` function from [logging exemplar](../../exemplars/script/powershell/logging.exemplar.md):
```powershell
Write-Log "Starting analysis" -Level INFO
Write-Log "Coverage low" -Level WARN
Write-Log "Build failed" -Level ERROR
Write-Log "Debug info" -Level DEBUG
```

### Python

Use `setup_logging()` from [logging exemplar](../../exemplars/script/python/logging.exemplar.md):
```python
logger = setup_logging(verbose=args.verbose)
logger.info("Starting analysis")
logger.warning("Coverage low")
logger.error("Build failed")
logger.debug("Debug info")
```

## Quality Checklist

- [ ] Timestamps on all log messages
- [ ] Color-coded by level (red=error, yellow=warn, green=success)
- [ ] Azure Pipelines integration (##vso commands)
- [ ] Optional file logging
- [ ] DEBUG level only shown with --verbose/-Verbose

---
Produced-by: prompt.scripts.add-logging.v1 | ts=2025-12-07T00:00:00Z
