<#
.SYNOPSIS
    Analyze prompt library for size, complexity, and example metrics

.DESCRIPTION
    Scans all .prompt.md files in the prompts directory and generates reports on:
    - Largest prompts (by line count)
    - Most example-rich prompts
    - Prompts combining large size with many examples
    - Category-level statistics

.PARAMETER PromptsPath
    Path to prompts directory (defaults to .cursor/prompts relative to script location)

.PARAMETER TopN
    Number of top results to show in each category (default: 10)

.PARAMETER MinExamples
    Minimum example count to include in example-rich report (default: 3)

.PARAMETER MinLinesForSweetSpot
    Minimum line count for "sweet spot" analysis (default: 500)

.PARAMETER OutputFormat
    Output format: Console, Markdown, CSV, or Json (default: Console)

.PARAMETER OutputFile
    File path for non-console output formats

.EXAMPLE
    .\analyze-prompt-library.ps1

    Analyze prompts with default settings (console output)

.EXAMPLE
    .\analyze-prompt-library.ps1 -TopN 20 -OutputFormat Markdown -OutputFile analysis-report.md

    Generate markdown report with top 20 results

.EXAMPLE
    .\analyze-prompt-library.ps1 -MinExamples 5 -OutputFormat Json

    Show only prompts with 5+ examples, output as JSON

.NOTES
    Version: 1.0.0
    Created: 2025-12-08
    Part of: PROMPTS-OPTIMIZE ticket
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$PromptsPath = (Join-Path $PSScriptRoot "."),

    [Parameter()]
    [ValidateRange(1, 50)]
    [int]$TopN = 10,

    [Parameter()]
    [ValidateRange(1, 20)]
    [int]$MinExamples = 3,

    [Parameter()]
    [ValidateRange(100, 1000)]
    [int]$MinLinesForSweetSpot = 500,

    [Parameter()]
    [ValidateSet('Console', 'Markdown', 'CSV', 'Json')]
    [string]$OutputFormat = 'Console',

    [Parameter()]
    [string]$OutputFile
)

$ErrorActionPreference = 'Stop'

#region Helper Functions

function Get-PromptMetrics {
    <#
    .SYNOPSIS
        Extract metrics from a single prompt file
    #>
    param(
        [Parameter(Mandatory)]
        [System.IO.FileInfo]$File
    )

    $content = Get-Content $File.FullName -Raw
    $lines = (Get-Content $File.FullName | Measure-Object -Line).Lines

    # Count examples using multiple patterns
    $examplePatterns = @(
        '(?m)^### Example',           # H3 examples
        '(?m)^## Examples',            # H2 examples section
        '(?m)^\*\*Example \d+',        # Bold numbered examples
        '(?m)^Example \d+:',           # Plain numbered examples
        '(?im)^\*\*Input\*\*:\s*$'     # Input/Output pattern
    )

    $exampleCount = 0
    foreach ($pattern in $examplePatterns) {
        $exampleCount += ([regex]::Matches($content, $pattern)).Count
    }

    # Get relative path from prompts root
    $relativePath = $File.FullName.Replace("$PromptsPath\", '').Replace("$PromptsPath/", '')

    [PSCustomObject]@{
        Name = $File.Name
        Category = $File.Directory.Name
        RelativePath = $relativePath
        Lines = $lines
        Examples = $exampleCount
        SizeKB = [math]::Round($File.Length / 1KB, 1)
        ExampleDensity = if ($lines -gt 0) { [math]::Round(($exampleCount / $lines) * 100, 1) } else { 0 }
        FullPath = $File.FullName
    }
}

function Write-ConsoleReport {
    param($Data, $Statistics)

    Write-Host ''
    Write-Host ('=' * 80) -ForegroundColor Cyan
    Write-Host 'PROMPT LIBRARY ANALYSIS' -ForegroundColor Cyan
    Write-Host ('=' * 80) -ForegroundColor Cyan
    Write-Host ''

    # Overall stats
    Write-Host 'Overall Statistics' -ForegroundColor Yellow
    Write-Host "  Total Prompts: $($Statistics.TotalPrompts)"
    Write-Host "  Total Lines: $($Statistics.TotalLines)"
    Write-Host "  Total Size: $($Statistics.TotalSizeMB) MB"
    Write-Host "  Average Lines per Prompt: $($Statistics.AvgLines)"
    Write-Host "  Prompts with Examples: $($Statistics.PromptsWithExamples) ($($Statistics.PercentWithExamples)%)"
    Write-Host ''

    # Largest prompts
    Write-Host "Top $TopN Largest Prompts (by line count)" -ForegroundColor Yellow
    $Data.LargestPrompts | Format-Table -AutoSize Name, Category, Lines, Examples, @{Label='Size(KB)';Expression={$_.SizeKB}}
    Write-Host ''

    # Most examples
    Write-Host "Top $TopN Prompts with Most Examples" -ForegroundColor Yellow
    $Data.MostExamples | Format-Table -AutoSize Name, Category, Examples, Lines, @{Label='Density%';Expression={$_.ExampleDensity}}
    Write-Host ''

    # Sweet spot
    Write-Host "Large Prompts with Many Examples ($MinLinesForSweetSpot+ lines, $MinExamples+ examples)" -ForegroundColor Yellow
    if ($Data.SweetSpot.Count -gt 0) {
        $Data.SweetSpot | Format-Table -AutoSize Name, Category, Lines, Examples, @{Label='Size(KB)';Expression={$_.SizeKB}}
    } else {
        Write-Host "  (none found)" -ForegroundColor Gray
    }
    Write-Host ''

    # Category breakdown
    Write-Host 'Category Breakdown' -ForegroundColor Yellow
    $Data.CategoryStats | Format-Table -AutoSize Category, Count, @{Label='Avg Lines';Expression={$_.AvgLines}}, @{Label='Avg Examples';Expression={$_.AvgExamples}}, @{Label='Total Size(KB)';Expression={$_.TotalSizeKB}}
    Write-Host ''

    Write-Host ('=' * 80) -ForegroundColor Cyan
}

function Write-MarkdownReport {
    param($Data, $Statistics, $OutputPath)

    $generatedDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    $content = @()
    $content += '# Prompt Library Analysis Report'
    $content += ''
    $content += "**Generated**: $generatedDate"
    $content += "**Location**: ``$PromptsPath``"
    $content += ''
    $content += '---'
    $content += ''
    $content += '## Overall Statistics'
    $content += ''
    $content += "- **Total Prompts**: $($Statistics.TotalPrompts)"
    $content += "- **Total Lines**: $($Statistics.TotalLines)"
    $content += "- **Total Size**: $($Statistics.TotalSizeMB) MB"
    $content += "- **Average Lines per Prompt**: $($Statistics.AvgLines)"
    $content += "- **Prompts with Examples**: $($Statistics.PromptsWithExamples) ($($Statistics.PercentWithExamples)%)"
    $content += ''
    $content += '---'
    $content += ''
    $content += "## Top $TopN Largest Prompts (by line count)"
    $content += ''
    $content += '| Prompt | Category | Lines | Examples | Size (KB) |'
    $content += '|--------|----------|-------|----------|-----------|'

    foreach ($prompt in $Data.LargestPrompts) {
        $content += "| ``$($prompt.Name)`` | $($prompt.Category) | $($prompt.Lines) | $($prompt.Examples) | $($prompt.SizeKB) |"
    }

    $content += ''
    $content += '---'
    $content += ''
    $content += "## Top $TopN Prompts with Most Examples"
    $content += ''
    $content += '| Prompt | Category | Examples | Lines | Density % |'
    $content += '|--------|----------|----------|-------|-----------|'

    foreach ($prompt in $Data.MostExamples) {
        $content += "| ``$($prompt.Name)`` | $($prompt.Category) | **$($prompt.Examples)** | $($prompt.Lines) | $($prompt.ExampleDensity)% |"
    }

    $content += ''
    $content += '---'
    $content += ''
    $content += '## Large Prompts with Many Examples'
    $content += ''
    $content += "Prompts with $MinLinesForSweetSpot+ lines AND $MinExamples+ examples:"
    $content += ''

    if ($Data.SweetSpot.Count -gt 0) {
        $content += '| Prompt | Category | Lines | Examples | Size (KB) |'
        $content += '|--------|----------|-------|----------|-----------|'
        foreach ($prompt in $Data.SweetSpot) {
            $content += "| ``$($prompt.Name)`` | $($prompt.Category) | $($prompt.Lines) | $($prompt.Examples) | $($prompt.SizeKB) |"
        }
    } else {
        $content += '(none found)'
    }

    $content += ''
    $content += '---'
    $content += ''
    $content += '## Category Breakdown'
    $content += ''
    $content += '| Category | Count | Avg Lines | Avg Examples | Total Size (KB) |'
    $content += '|----------|-------|-----------|--------------|-----------------|'

    foreach ($cat in $Data.CategoryStats) {
        $content += "| $($cat.Category) | $($cat.Count) | $($cat.AvgLines) | $($cat.AvgExamples) | $($cat.TotalSizeKB) |"
    }

    $content += ''
    $content += '---'
    $content += ''
    $content += '## Optimization Opportunities'
    $content += ''
    $content += '### High Example Density'
    $content += 'Prompts with >5% example density (lots of examples relative to size):'
    $content += ''

    $highDensity = $Data.AllPrompts | Where-Object { $_.ExampleDensity -gt 5 -and $_.Examples -gt 0 } | Sort-Object -Property ExampleDensity -Descending | Select-Object -First 5
    if ($highDensity.Count -gt 0) {
        foreach ($prompt in $highDensity) {
            $content += "- ``$($prompt.Name)`` - $($prompt.ExampleDensity)% density ($($prompt.Examples) examples in $($prompt.Lines) lines)"
        }
    } else {
        $content += '(none found)'
    }

    $content += ''
    $content += '### Potential for Modularization'
    $content += 'Large prompts (>400 lines) that might benefit from splitting:'
    $content += ''

    $largeCandidates = $Data.AllPrompts | Where-Object { $_.Lines -gt 400 } | Sort-Object -Property Lines -Descending | Select-Object -First 5
    if ($largeCandidates.Count -gt 0) {
        foreach ($prompt in $largeCandidates) {
            $content += "- ``$($prompt.Name)`` - $($prompt.Lines) lines, $($prompt.Examples) examples"
        }
    } else {
        $content += '(none found)'
    }

    $content -join "`n" | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "Report saved to: $OutputPath" -ForegroundColor Green
}

function Write-CsvReport {
    param($Data, $OutputPath)

    $Data.AllPrompts | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    Write-Host "CSV data exported to: $OutputPath" -ForegroundColor Green
}

function Write-JsonReport {
    param($Data, $Statistics, $OutputPath)

    $report = @{
        GeneratedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        Location = $PromptsPath
        Statistics = $Statistics
        LargestPrompts = $Data.LargestPrompts
        MostExamples = $Data.MostExamples
        SweetSpot = $Data.SweetSpot
        CategoryStats = $Data.CategoryStats
        AllPrompts = $Data.AllPrompts
    }

    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "JSON report saved to: $OutputPath" -ForegroundColor Green
}

#endregion

#region Main Execution

Write-Host "Scanning prompt library at: $PromptsPath" -ForegroundColor Cyan

# Validate path
if (-not (Test-Path $PromptsPath)) {
    Write-Error "Prompts path not found: $PromptsPath"
    exit 1
}

# Collect all prompt files
$promptFiles = Get-ChildItem -Path $PromptsPath -Filter '*.prompt.md' -Recurse -File

if ($promptFiles.Count -eq 0) {
    Write-Warning "No .prompt.md files found in $PromptsPath"
    exit 0
}

Write-Host "Found $($promptFiles.Count) prompt files" -ForegroundColor Cyan

# Extract metrics from all prompts
$allPrompts = @()
$current = 0
foreach ($file in $promptFiles) {
    $current++
    Write-Progress -Activity 'Analyzing prompts' -Status "Processing $($file.Name)" -PercentComplete (($current / $promptFiles.Count) * 100)
    $allPrompts += Get-PromptMetrics -File $file
}
Write-Progress -Activity 'Analyzing prompts' -Completed

# Calculate statistics
$stats = @{
    TotalPrompts = $allPrompts.Count
    TotalLines = ($allPrompts | Measure-Object -Property Lines -Sum).Sum
    TotalSizeMB = [math]::Round(($allPrompts | Measure-Object -Property SizeKB -Sum).Sum / 1024, 2)
    AvgLines = [math]::Round(($allPrompts | Measure-Object -Property Lines -Average).Average, 0)
    PromptsWithExamples = ($allPrompts | Where-Object { $_.Examples -gt 0 }).Count
}
$stats.PercentWithExamples = [math]::Round(($stats.PromptsWithExamples / $stats.TotalPrompts) * 100, 1)

# Prepare report data
$reportData = @{
    AllPrompts = $allPrompts
    LargestPrompts = $allPrompts | Sort-Object -Property Lines -Descending | Select-Object -First $TopN
    MostExamples = $allPrompts | Where-Object { $_.Examples -ge $MinExamples } | Sort-Object -Property Examples -Descending | Select-Object -First $TopN
    SweetSpot = $allPrompts | Where-Object { $_.Lines -ge $MinLinesForSweetSpot -and $_.Examples -ge $MinExamples } | Sort-Object -Property Lines -Descending
    CategoryStats = $allPrompts | Group-Object -Property Category | ForEach-Object {
        [PSCustomObject]@{
            Category = $_.Name
            Count = $_.Count
            AvgLines = [math]::Round(($_.Group | Measure-Object -Property Lines -Average).Average, 0)
            AvgExamples = [math]::Round(($_.Group | Measure-Object -Property Examples -Average).Average, 1)
            TotalSizeKB = [math]::Round(($_.Group | Measure-Object -Property SizeKB -Sum).Sum, 1)
        }
    } | Sort-Object -Property TotalSizeKB -Descending
}

# Output report in requested format
switch ($OutputFormat) {
    'Console' {
        Write-ConsoleReport -Data $reportData -Statistics $stats
    }
    'Markdown' {
        if (-not $OutputFile) {
            $OutputFile = "prompt-library-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
        }
        Write-MarkdownReport -Data $reportData -Statistics $stats -OutputPath $OutputFile
    }
    'CSV' {
        if (-not $OutputFile) {
            $OutputFile = "prompt-library-data-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
        }
        Write-CsvReport -Data $reportData -OutputPath $OutputFile
    }
    'Json' {
        if (-not $OutputFile) {
            $OutputFile = "prompt-library-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
        }
        Write-JsonReport -Data $reportData -Statistics $stats -OutputPath $OutputFile
    }
}

exit 0

#endregion
