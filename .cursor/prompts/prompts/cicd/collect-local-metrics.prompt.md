---
name: collect-local-metrics
description: "Run local metrics collection to populate historical data for trending"
category: cicd
tags: cicd, metrics, quality, coverage, tracking
argument-hint: "MaxHistoryEntries limit (optional, default: infinite)"
---

# Local Metrics Collection Prompt

You are tasked with running the local metrics collection script to gather data for historical trending (archived in `.history`).

## Context
We want to collect code metrics (complexity, maintainability) and coverage data (line, branch, API) locally to build a history over time. This history allows us to visualize trends without relying solely on CI/CD pipelines.

## Script: `cicd/scripts/collect-local-metrics.ps1`

This orchestration script runs:
1. `calculate-code-metrics.ps1`
2. `enhanced-coverage-analysis.ps1`

### Configuration

The script accepts parameters to configure all underlying thresholds and settings.

**Key Parameters:**
- `-MaxHistoryEntries`: Controls history rotation. **Default is 0 (Infinite)**. Set to a positive integer (e.g., 100) to limit the number of entries kept.
- `-EnableHistoryTracking`: Defaults to `$true`.
- `-Configuration`: `Debug` or `Release` (Default: `Release`).

### Usage Examples

**Run with default settings (Infinite history):**
```powershell
./cicd/scripts/collect-local-metrics.ps1
```

**Run and limit history to last 50 entries:**
```powershell
./cicd/scripts/collect-local-metrics.ps1 -MaxHistoryEntries 50
```

**Run with custom quality thresholds:**
```powershell
./cicd/scripts/collect-local-metrics.ps1 -MinLineCoverage 85 -MaxComplexity 10
```

## Instructions for the Agent

1. **Verify Prerequisites**: Ensure `.NET SDK` and `ReportGenerator` are available (the scripts handles some tool checks).
2. **Execute Script**: Run the script using the parameters requested by the user.
3. **Verify Output**: Check that `.history/` folder is populated/updated.
4. **Report**: Summarize the run status and the location of the generated history files.

## Important Notes
- This process is designed for **local** execution but follows the same standards as CI/CD scripts.
- The history files (`.history/*.jsonl`, `.history/*.csv`) should be committed to git if you want to share trends with the team.

