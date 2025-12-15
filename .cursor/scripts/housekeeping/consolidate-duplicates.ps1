#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Detect exact duplicate artifacts by hash and shared titles.

.DESCRIPTION
Scans a folder for markdown/prompt/rule files, groups by SHA256 hash (exact
duplicates) and by top-level title (potential conceptual duplicates).

.PARAMETER Folder
Folder to scan. Default: repo/.cursor

.PARAMETER Json
Output report as JSON (suppresses progress/console summary).

.PARAMETER PassThru
Return report object.

.EXAMPLE
.\consolidate-duplicates.ps1
Scan .cursor for duplicates.

.EXAMPLE
.\consolidate-duplicates.ps1 -Folder ".cursor/prompts" -Json
Emit JSON for automation.
#>
[CmdletBinding()]
param(
    [Parameter()][ValidateScript({ Test-Path $_ })][string]$Folder = $(Join-Path (Get-Location).Path ".cursor"),
    [Parameter()][switch]$Json,
    [Parameter()][switch]$PassThru
)

$ErrorActionPreference = 'Stop'
if ($Json) { $ProgressPreference = 'SilentlyContinue' }

# Import shared utilities
$ModulePath = Join-Path $PSScriptRoot "..\\modules\\Common.psm1"
Import-Module $ModulePath -Force

try {
    $root = Resolve-Path -Path $Folder -ErrorAction Stop
    $files = Get-ChildItem -Path $root.Path -Recurse -File -Include *.md,*.mdc,*.prompt.md

    $byHash = @{}
    $byTitle = @{}

    foreach ($f in $files) {
        $hash = (Get-FileHash -Algorithm SHA256 -Path $f.FullName).Hash
        $rel = Normalize($f.FullName.Substring($root.Path.Length + 1))
        if (-not $byHash.ContainsKey($hash)) { $byHash[$hash] = @() }
        $byHash[$hash] += $rel

        $firstHeading = (Select-String -Path $f.FullName -Pattern '^\s*#\s+(.+)$' -List -SimpleMatch -ErrorAction SilentlyContinue | Select-Object -First 1).Matches.Value
        if ($firstHeading) {
            $title = ($firstHeading -replace '^\s*#\s+','').Trim()
            if (-not $byTitle.ContainsKey($title)) { $byTitle[$title] = @() }
            $byTitle[$title] += $rel
        }
    }

    $exact = $byHash.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 } | ForEach-Object {
        [pscustomobject]@{
            Hash  = $_.Key
            Files = $_.Value
        }
    }

    $titleDupes = $byTitle.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 } | ForEach-Object {
        [pscustomobject]@{
            Title = $_.Key
            Files = $_.Value
        }
    }

    $report = [pscustomobject]@{
        Folder          = $root.Path
        Scanned         = @($files).Count
        ExactDuplicates = $exact
        TitleDuplicates = $titleDupes
    }

    if ($Json) {
        $report | ConvertTo-Json -Depth 5
        if ((@($exact).Count -gt 0) -or (@($titleDupes).Count -gt 0)) { exit 1 } else { exit 0 }
    }

    Write-Host "Folder: $($root.Path)" -ForegroundColor Gray
    Write-Host "Files scanned: $(@($files).Count)" -ForegroundColor Gray
    if (@($exact).Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'error') Exact duplicates: $(@($exact).Count)" -ForegroundColor Red
        $exact | ForEach-Object { Write-Host " - [$($_.Hash)] $(@($_.Files) -join ', ')" -ForegroundColor Red }
    } else {
        Write-Host "$(Get-StatusGlyph 'success') No exact duplicates found." -ForegroundColor Green
    }

    if (@($titleDupes).Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'warning') Title collisions: $(@($titleDupes).Count)" -ForegroundColor Yellow
        $titleDupes | ForEach-Object { Write-Host " - $($_.Title): $(@($_.Files) -join ', ')" -ForegroundColor Yellow }
    } else {
        Write-Host "$(Get-StatusGlyph 'success') No duplicate titles found." -ForegroundColor Green
    }

    if ($PassThru) { $report }
    if ((@($exact).Count -gt 0) -or (@($titleDupes).Count -gt 0)) { exit 1 } else { exit 0 }
}
catch {
    Write-Host "$(Get-StatusGlyph 'error') Failure: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}


