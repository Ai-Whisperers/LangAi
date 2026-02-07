# PowerShell Parallel Processing Pattern Exemplar

## Overview

`ForEach-Object -Parallel` (PowerShell 7+) processes multiple items concurrently, providing 3-10x performance improvement for independent operations.

## When to Use

- **Use for**: Processing 10+ independent items, each taking >1 second
- **Critical for**: Large datasets, API calls, file processing, performance-critical scripts
- **Skip for**: <10 items, items with shared state, sequential dependencies

## Good Pattern ✅

```powershell
# Parallel (3-10x faster)
$results = $packages | ForEach-Object -Parallel {
    param($pkg = $_)

    # Each iteration runs in separate runspace
    $lineCoverage = [double]$pkg.'line-rate' * 100
    $branchCoverage = [double]$pkg.'branch-rate' * 100

    [PSCustomObject]@{
        Name = $pkg.name
        LineCoverage = $lineCoverage
        BranchCoverage = $branchCoverage
    }
} -ThrottleLimit 10  # Max 10 concurrent operations

Write-Host "Analyzed $($results.Count) packages in parallel"
```

**Why this is good:**
- **Concurrent execution**: Each item processed independently in parallel
- **Throttle limit**: Controls resource usage (10 concurrent max)
- **No shared state**: Each runspace is isolated
- **Performance gain**: 3-10x faster for I/O or CPU-bound operations

## Bad Pattern (Sequential) ❌

```powershell
# Sequential (slow for many items)
$results = @()
foreach ($package in $packages) {
    $lineCoverage = [double]$package.'line-rate' * 100
    $branchCoverage = [double]$package.'branch-rate' * 100

    $results += [PSCustomObject]@{
        Name = $package.name
        LineCoverage = $lineCoverage
        BranchCoverage = $branchCoverage
    }
}
```

**Why this is bad (when parallel is appropriate):**
- **Sequential processing**: Items processed one at a time
- **Wasted time**: CPU/cores idle while waiting for I/O
- **Poor scalability**: Processing time grows linearly with item count

## Parallel Processing Best Practices

### Pass Parameters Explicitly

```powershell
# ✅ Good: Explicit parameter passing
$threshold = 80
$results = $items | ForEach-Object -Parallel {
    param($item, $minThreshold)

    if ($item.Value -ge $minThreshold) {
        [PSCustomObject]@{ Name = $item.Name; Status = "Pass" }
    }
} -ArgumentList $_,$threshold -ThrottleLimit 5

# ❌ Bad: Using $using: for mutable variables (can cause issues)
```

### Error Handling in Parallel Blocks

```powershell
$results = $files | ForEach-Object -Parallel {
    param($file = $_)

    try {
        $content = Get-Content $file -ErrorAction Stop
        return @{ File = $file; Lines = $content.Count; Status = "Success" }
    }
    catch {
        return @{ File = $file; Error = $_.Exception.Message; Status = "Failed" }
    }
} -ThrottleLimit 10

# Check for failures
$failures = $results | Where-Object { $_.Status -eq "Failed" }
if ($failures.Count -gt 0) {
    Write-Warning "Failed to process $($failures.Count) files"
}
```

### When NOT to Use Parallel

```powershell
# ❌ Don't use parallel for:

# 1. Sequential dependencies
foreach ($step in $buildSteps) {
    # Each step depends on previous step completing
    Invoke-BuildStep $step
}

# 2. Shared mutable state
$counter = 0
foreach ($item in $items) {
    $counter++  # Shared variable - would cause race conditions in parallel
}

# 3. Very fast operations (<100ms each)
foreach ($num in 1..10) {
    $result = $num * 2  # Too fast for parallel overhead to be worthwhile
}
```

## Performance Characteristics

- **Speedup**: 3-10x for I/O-bound (file, network), 2-4x for CPU-bound
- **Overhead**: ~50-100ms setup cost for runspaces
- **Memory**: Each runspace uses ~10-20MB
- **Best for**: 10+ items, each taking >1 second

**Benchmarks**:
- 100 items @ 500ms each: Sequential=50s, Parallel (10 threads)=5-7s
- 50 API calls @ 2s each: Sequential=100s, Parallel (10 threads)=10-12s

## Related Patterns

- [Performance](../../python/multiprocessing.exemplar.md) - Python equivalent with multiprocessing
- [Progress](./progress.exemplar.md) - Can combine with progress reporting
- See also: `rule.scripts.powershell-standards.v1` section "Parallel Processing"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
