#Requires -Version 7.2
#Requires -PSEdition Core
# Finds artifacts likely to be good templar/exemplar extraction targets.
# Heuristics: line count, example density, templar/exemplar language, star/ratings.
[CmdletBinding()]
param(
    [Parameter()][ValidateScript({ Test-Path $_ })][string]$Root = ".cursor/prompts",
    [Parameter()][ValidateRange(0, 100000)][int]$MinLines = 200,
    [Parameter()][Alias('Json')][switch]$AsJson,
    [Parameter()][ValidateRange(0, 100000)][int]$ExampleThreshold = 5,
    [switch]$IncludeRules,
    [switch]$IncludeTickets
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedRoot = Resolve-Path -Path $Root

$patterns = @("*.prompt.md")
if ($IncludeRules) { $patterns += "*.mdc" }
if ($IncludeTickets) { $patterns += "*.md" }

$excludePattern = "(\\\.git|\\node_modules|\\bin|\\obj|\\dist|\\coverage|\\.cursor\\scripts)"

function Get-SignalScore {
    param(
        [int]$Lines,
        [int]$ExampleCount,
        [int]$TemplarRefs,
        [bool]$HasStars
    )

    $score = 0
    if ($Lines -ge $MinLines) { $score++ }
    if ($ExampleCount -ge $ExampleThreshold) { $score++ }
    if ($TemplarRefs -ge 3) { $score++ }
    if ($HasStars) { $score++ }
    return $score
}

$results = Get-ChildItem -Path $resolvedRoot -Recurse -File -Include $patterns |
    Where-Object { $_.FullName -notmatch $excludePattern } |
    ForEach-Object {
        $content = Get-Content -Path $_.FullName -Raw
        $lines = ($content -split "`n").Count
        $exampleCount = [regex]::Matches($content, '(?im)^\s*###\s+Example').Count
        $templarRefs = [regex]::Matches($content, 'templar|exemplar|template', 'IgnoreCase').Count
        $hasStars = $content -match '[\u2605⭐]'
        $score = Get-SignalScore -Lines $lines -ExampleCount $exampleCount -TemplarRefs $templarRefs -HasStars $hasStars

        [pscustomobject]@{
            Score        = $score
            Lines        = $lines
            Examples     = $exampleCount
            TemplarRefs  = $templarRefs
            Stars        = $hasStars
            Path         = $_.FullName
        }
    } |
    Sort-Object -Property Score, Lines -Descending

if ($AsJson) {
    $results | ConvertTo-Json -Depth 4
} else {
    $results | Format-Table -AutoSize
}
