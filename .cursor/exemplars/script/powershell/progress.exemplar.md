# PowerShell Progress Reporting Pattern Exemplar

## Overview

`Write-Progress` displays a progress bar for long-running operations, providing user feedback and estimated time remaining.

## When to Use

- **Use for**: Advanced quality level scripts, long-running operations (>10 seconds)
- **Critical for**: User-facing tools, interactive scripts, batch processing
- **Skip for**: Fast operations (<10s), background/unattended scripts, parallel processing

## Good Pattern ✅

```powershell
$totalPackages = $packages.Count
$current = 0

foreach ($package in $packages) {
    $current++
    $percentComplete = ($current / $totalPackages) * 100

    Write-Progress -Activity "Analyzing Coverage" `
                   -Status "Package: $($package.name) ($current of $totalPackages)" `
                   -PercentComplete $percentComplete `
                   -CurrentOperation "Processing line coverage"

    # Analysis logic here
    $result = Analyze-Package -Package $package

    Start-Sleep -Milliseconds 100  # Simulate work
}

Write-Progress -Activity "Analyzing Coverage" -Completed
```

**Why this is good:**
- **Visual feedback**: User sees progress bar advancing
- **Percent complete**: Clear indication of how much work remains
- **Current item**: Status shows which package is being processed
- **Completion cleanup**: `-Completed` removes progress bar when done
- **Detailed operation**: CurrentOperation shows sub-task

## Bad Pattern ❌

```powershell
# ❌ No progress reporting
foreach ($package in $packages) {
    $result = Analyze-Package -Package $package
    # User has no idea how long this will take or what's happening
}

# ❌ Or spammy Write-Host
foreach ($package in $packages) {
    Write-Host "Processing $($package.name)"  # Clutters output
    $result = Analyze-Package -Package $package
}
```

**Why this is bad:**
- **No feedback**: User doesn't know if script is hung or working
- **No ETA**: Can't estimate completion time
- **Cluttered output**: Write-Host spam makes logs hard to read
- **No cancellation feedback**: User doesn't know if Ctrl+C will work

## Progress Reporting Best Practices

### Nested Progress (Parent/Child)

```powershell
$totalProjects = $projects.Count
$projectNum = 0

foreach ($project in $projects) {
    $projectNum++
    $projectPercent = ($projectNum / $totalProjects) * 100

    Write-Progress -Activity "Analyzing Projects" `
                   -Status "Project $projectNum of $totalProjects" `
                   -PercentComplete $projectPercent `
                   -Id 1

    $files = Get-ChildItem -Path $project.Path -Filter "*.cs"
    $fileNum = 0

    foreach ($file in $files) {
        $fileNum++
        $filePercent = ($fileNum / $files.Count) * 100

        Write-Progress -Activity "Analyzing Files" `
                       -Status "File $fileNum of $($files.Count)" `
                       -PercentComplete $filePercent `
                       -ParentId 1 `
                       -Id 2

        # Analyze file
    }

    Write-Progress -Activity "Analyzing Files" -Completed -Id 2
}

Write-Progress -Activity "Analyzing Projects" -Completed -Id 1
```

### Progress with Time Estimation

```powershell
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($item in $items) {
    $current++
    $percentComplete = ($current / $total) * 100

    $elapsed = $stopwatch.Elapsed.TotalSeconds
    $rate = $current / $elapsed
    $remaining = ($total - $current) / $rate
    $eta = [TimeSpan]::FromSeconds($remaining)

    Write-Progress -Activity "Processing Items" `
                   -Status "$current of $total (ETA: $($eta.ToString('mm\:ss')))" `
                   -PercentComplete $percentComplete
}
```

### Indeterminate Progress (Unknown Total)

```powershell
$current = 0

while ($condition) {
    $current++

    Write-Progress -Activity "Processing Stream" `
                   -Status "Processed $current items" `
                   -PercentComplete -1  # -1 = indeterminate

    # Process item
}
```

## Performance Characteristics

- **Overhead**: 1-5ms per `Write-Progress` call
- **Update frequency**: Update every iteration for <1000 items, every 10-100 iterations for larger sets
- **Visual impact**: Provides user confidence, reduces perceived wait time

**Best Practices**:
- Update progress every iteration for <100 items
- Update every 10 iterations for 100-1000 items
- Update every 100 iterations for 1000+ items

## Related Patterns

- [Parallel](./parallel.exemplar.md) - Progress doesn't work well with parallel processing
- [Logging](./logging.exemplar.md) - Combine progress with structured logging
- See also: `rule.scripts.powershell-standards.v1` section "Progress Reporting"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
