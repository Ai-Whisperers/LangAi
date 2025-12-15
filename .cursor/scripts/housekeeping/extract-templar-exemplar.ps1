#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Extracts the “Examples (Few-Shot)” section from a prompt into an exemplar and replaces it with a pointer (DRY).

.DESCRIPTION
Takes a prompt file, slices out its Examples section, writes that content to a separate exemplar file, and rewrites the source to point to the exemplar. Protects against overwrite unless -Force is specified and supports dry-run via -WhatIf.

.PARAMETER Source
Path to the source prompt (.prompt.md).

.PARAMETER ExemplarPath
Path to write the exemplar (.md).

.PARAMETER NextHeading
The heading that marks the end of the Examples section. Default: '## Output Format'.

.PARAMETER Force
Overwrite existing exemplar if it already exists.

.EXAMPLE
.\extract-templar-exemplar.ps1 -Source ".cursor\prompts\prompt\improve-prompt.prompt.md" -ExemplarPath ".cursor\prompts\exemplars\prompt\improve-prompt-exemplar.md"

.EXAMPLE
.\extract-templar-exemplar.ps1 -Source ".cursor\prompts\ticket\close-ticket.prompt.md" -ExemplarPath ".cursor\prompts\exemplars\ticket\ticket-closure-exemplar.md" -NextHeading "## Anti-Patterns" -Force

.NOTES
Quality: Standard (per scripts standards). Portability: uses UTF-8, no hardcoded CI vars.
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ExemplarPath,

    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string]$NextHeading = '## Output Format',

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Write-ErrorAndExit {
    param([string]$Message, [int]$Code = 1)
    Write-Host "❌ $Message" -ForegroundColor Red
    exit $Code
}

try {
    if (-not (Test-Path -Path $Source -PathType Leaf)) {
        Write-ErrorAndExit "Source file not found: $Source"
    }

    $content = Get-Content -Path $Source -Raw -ErrorAction Stop

    $pattern = "(?s)## Examples \(Few-Shot\)(.*?)(?=$([regex]::Escape($NextHeading)))"
    $match = [regex]::Match($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

    if (-not $match.Success) {
        Write-ErrorAndExit "Examples section not found in $Source using end marker '$NextHeading'." 4
    }

    $examplesBlock = $match.Value.Trim()

    if ((Test-Path -Path $ExemplarPath -PathType Leaf) -and -not $Force) {
        Write-ErrorAndExit "Exemplar already exists at $ExemplarPath. Use -Force to overwrite." 2
    }

    $exemplarOut = "# Extracted Examples Exemplar`r`n`r`n$examplesBlock`r`n"
    $exemplarDir = Split-Path -Path $ExemplarPath
    if (-not [string]::IsNullOrWhiteSpace($exemplarDir) -and -not (Test-Path $exemplarDir)) {
        if ($PSCmdlet.ShouldProcess($exemplarDir, "Create directory")) {
            New-Item -ItemType Directory -Path $exemplarDir | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($ExemplarPath, "Write exemplar")) {
        Set-Content -Path $ExemplarPath -Value $exemplarOut -Encoding utf8
    }

    $pointer = @"
## Examples (Few-Shot)

See exemplar for complete worked examples:
- $ExemplarPath

$NextHeading
"@

    $newContent = $content -replace $pattern, $pointer

    if ($PSCmdlet.ShouldProcess($Source, "Replace examples with pointer")) {
        Set-Content -Path $Source -Value $newContent -Encoding utf8
    }

    Write-Host "✅ Extraction complete." -ForegroundColor Green
    Write-Host "Source updated: $Source" -ForegroundColor Gray
    Write-Host "Exemplar saved to: $ExemplarPath" -ForegroundColor Gray
    exit 0
}
catch {
    Write-ErrorAndExit "Extraction failed: $($_.Exception.Message)" 1
}