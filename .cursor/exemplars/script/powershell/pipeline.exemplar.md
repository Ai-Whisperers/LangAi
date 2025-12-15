# PowerShell Pipeline Support Pattern Exemplar

## Overview

PowerShell pipeline support with `ValueFromPipeline` enables scripts to accept input from other cmdlets, following PowerShell best practices.

## When to Use

- **Use for**: Reusable utilities, advanced quality level scripts, cmdlet-style scripts
- **Critical for**: Integration with other PowerShell cmdlets, composable workflows
- **Skip for**: Simple one-off scripts, non-interactive automation

## Good Pattern ✅

```powershell
[CmdletBinding()]
param(
    [Parameter(ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
    [string[]]$ProjectPath,
    
    [Parameter(Mandatory=$false)]
    [string]$Configuration = "Release"
)

begin {
    # Setup once before pipeline starts
    Write-Host "Initializing analysis..."
    $results = @()
}

process {
    # Executes for EACH pipeline input
    foreach ($path in $ProjectPath) {
        Write-Host "Analyzing project: $path"
        $result = Analyze-Project -Path $path -Configuration $Configuration
        $results += $result
    }
}

end {
    # Cleanup after all pipeline inputs processed
    Write-Host "Analyzed $($results.Count) projects"
    return $results
}
```

**Usage Examples**:

```powershell
# Pipeline input from Get-ChildItem
Get-ChildItem -Path src -Directory | .\analyze-coverage.ps1

# Array input via pipeline
@("Project1", "Project2", "Project3") | .\analyze-coverage.ps1

# Direct parameter
.\analyze-coverage.ps1 -ProjectPath "Project1"
```

**Why this is good:**
- **Pipeline support**: Accepts input from other cmdlets via pipeline
- **begin/process/end blocks**: Proper pipeline processing structure
- **Multiple input modes**: Works with pipeline, arrays, or single values
- **ValueFromPipelineByPropertyName**: Can bind to object properties

## Bad Pattern ❌

```powershell
param(
    # ❌ No pipeline support
    [string[]]$ProjectPath
)

# ❌ No begin/process/end structure
foreach ($path in $ProjectPath) {
    Analyze-Project -Path $path
}

# ❌ Can't accept pipeline input
# Get-ChildItem | .\script.ps1  # Won't work!
```

**Why this is bad:**
- **No pipeline support**: Can't compose with other PowerShell cmdlets
- **Less flexible**: Must specify parameters explicitly
- **Not idiomatic**: Doesn't follow PowerShell conventions
- **Poor integration**: Can't chain with Select-Object, Where-Object, etc.

## Pipeline Pattern Best Practices

### ValueFromPipelineByPropertyName

```powershell
[CmdletBinding()]
param(
    [Parameter(ValueFromPipelineByPropertyName=$true)]
    [string]$Name,
    
    [Parameter(ValueFromPipelineByPropertyName=$true)]
    [string]$Path
)

process {
    Write-Host "Processing $Name at $Path"
}

# Usage with objects
$projects = @(
    [PSCustomObject]@{ Name = "ProjectA"; Path = "C:\ProjectA" }
    [PSCustomObject]@{ Name = "ProjectB"; Path = "C:\ProjectB" }
)

$projects | .\analyze-projects.ps1
```

### Mandatory Pipeline Input

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [string]$InputFile
)

begin {
    if (-not $InputFile) {
        throw "InputFile is required"
    }
}

process {
    # Process each file
}
```

### Pipeline with PassThru

```powershell
[CmdletBinding()]
param(
    [Parameter(ValueFromPipeline=$true)]
    [PSObject]$InputObject,
    
    [switch]$PassThru
)

process {
    # Process input
    $result = Process-Object $InputObject
    
    # Return original object if PassThru specified
    if ($PassThru) {
        $InputObject
    } else {
        $result
    }
}

# Usage:
Get-ChildItem | .\process.ps1 -PassThru | Where-Object { $_.Length -gt 1MB }
```

## Performance Characteristics

- **Streaming**: Items processed as they arrive (memory efficient)
- **Composability**: Can chain multiple pipeline stages
- **Lazy evaluation**: Only processes items as needed

**Memory Benefits**:
- Non-pipeline: Loads all items into memory first
- Pipeline: Processes one item at a time (constant memory)

## Related Patterns

- [Parallel](./parallel.exemplar.md) - Pipeline and parallel don't mix well
- [Progress](./progress.exemplar.md) - Can combine pipeline with progress reporting
- See also: `rule.scripts.powershell-standards.v1` section "Pipeline Support"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

