#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Finds prompts/rules that are strong candidates for condensation.

.DESCRIPTION
Scans artifacts and scores them by size and verbosity signals: line count, number of examples, code fences, and long lines. Higher scores indicate better candidates for `condense-prompts`.

.PARAMETER Root
Root path to scan. Defaults to `.cursor/prompts`.

.PARAMETER MinLines
Minimum line count to flag. Default: 160.

.PARAMETER ExampleThreshold
Example count threshold. Default: 5.

.PARAMETER CodeBlockThreshold
Code fence (```) block threshold. Default: 4.

.PARAMETER LongLineThreshold
Count of lines longer than 120 characters to flag. Default: 12.

.PARAMETER IncludeRules
Include `.mdc` rule files.

.PARAMETER IncludeTickets
Include `.md` ticket/docs files.

.PARAMETER AsJson
Return results as JSON instead of a table.

.EXAMPLE
./.cursor/scripts/housekeeping/find-condense-candidates.ps1 -Root ".cursor/prompts" -AsJson

.EXAMPLE
./.cursor/scripts/housekeeping/find-condense-candidates.ps1 -Root ".cursor/rules" -IncludeRules -MinLines 140

.NOTES
File: find-condense-candidates.ps1
Purpose: Identify verbosity hotspots for condensation.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Root = ".cursor/prompts",

    [Parameter(Mandatory = $false)]
    [int]$MinLines = 160,

    [Parameter(Mandatory = $false)]
    [int]$ExampleThreshold = 5,

    [Parameter(Mandatory = $false)]
    [int]$CodeBlockThreshold = 4,

    [Parameter(Mandatory = $false)]
    [int]$LongLineThreshold = 12,

    [Parameter(Mandatory = $false)]
    [switch]$IncludeRules,

    [Parameter(Mandatory = $false)]
    [switch]$IncludeTickets,

    [Parameter(Mandatory = $false)]
    [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-SignalScore {
    param(
        [int]$Lines,
        [int]$Examples,
        [int]$CodeFences,
        [int]$LongLines
    )

    $score = 0
    if ($Lines -ge $MinLines) { $score++ }
    if ($Examples -ge $ExampleThreshold) { $score++ }
    if ($CodeFences -ge $CodeBlockThreshold) { $score++ }
    if ($LongLines -ge $LongLineThreshold) { $score++ }
    return $score
}

function Get-SignalReasons {
    param(
        [int]$Lines,
        [int]$Examples,
        [int]$CodeFences,
        [int]$LongLines
    )

    $reasons = @()
    if ($Lines -ge $MinLines) { $reasons += "lines>=$MinLines" }
    if ($Examples -ge $ExampleThreshold) { $reasons += "examples>=$ExampleThreshold" }
    if ($CodeFences -ge $CodeBlockThreshold) { $reasons += "codeFences>=$CodeBlockThreshold" }
    if ($LongLines -ge $LongLineThreshold) { $reasons += "longLines>=$LongLineThreshold" }
    return $reasons
}

try {
    $resolvedRoot = Resolve-Path -Path $Root

    $patterns = @("*.prompt.md")
    if ($IncludeRules) { $patterns += "*.mdc" }
    if ($IncludeTickets) { $patterns += "*.md" }

    $excludePattern = "(\\\.git|\\node_modules|\\bin|\\obj|\\dist|\\coverage|\\.cursor\\scripts)"

    $results = Get-ChildItem -Path $resolvedRoot -Recurse -File -Include $patterns |
        Where-Object { $_.FullName -notmatch $excludePattern } |
        ForEach-Object {
            $content = Get-Content -Path $_.FullName -Raw
            $lines = ($content -split "`n").Count
            $exampleCount = [regex]::Matches($content, '(?im)^\s*###\s+Example').Count
            $codeFenceMatches = [regex]::Matches($content, '```').Count
            $codeBlocks = [math]::Floor($codeFenceMatches / 2)
            # Wrap in array to avoid null Count under StrictMode when there are no long lines.
            $longLineCount = @($content -split "`n" | Where-Object { $_.Length -gt 120 }).Count

            $score = Get-SignalScore -Lines $lines -Examples $exampleCount -CodeFences $codeBlocks -LongLines $longLineCount
            $reasons = Get-SignalReasons -Lines $lines -Examples $exampleCount -CodeFences $codeBlocks -LongLines $longLineCount

            [pscustomobject]@{
                Score      = $score
                Lines      = $lines
                Examples   = $exampleCount
                CodeFences = $codeBlocks
                LongLines  = $longLineCount
                Signals    = ($reasons -join "; ")
                Path       = $_.FullName
            }
        } |
        Sort-Object -Property Score, Lines -Descending

    if ($AsJson) {
        $results | ConvertTo-Json -Depth 4
    } else {
        $results | Format-Table -AutoSize
    }

    exit 0
}
catch {
    Write-Error "Failed to find condense candidates: $($_.Exception.Message)`nSolution: verify the root path exists and adjust thresholds if needed. Script: .cursor/scripts/housekeeping/find-condense-candidates.ps1"
    exit 1
}

