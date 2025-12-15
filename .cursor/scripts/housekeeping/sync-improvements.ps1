#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Compare artifacts between source and target roots to plan a sync.

.DESCRIPTION
Builds relative inventories for source/target roots, identifies new/removed
files, and detects modified files by hash. Produces a summary to guide manual
sync (no copying performed).

.PARAMETER SourceRoot
Root of source repository artifacts.

.PARAMETER TargetRoot
Root of target repository artifacts.

.PARAMETER Json
Output report as JSON.

.PARAMETER PassThru
Return report object.

.EXAMPLE
.\sync-improvements.ps1 -SourceRoot "E:/WPG/Git/E21/GitRepos/eneve.ebase.datamigrator" -TargetRoot "E:/WPG/Git/E21/GitRepos/eneve.domain"
Summarize differences for manual sync.

.EXAMPLE
.\sync-improvements.ps1 -SourceRoot "srcA/.cursor/rules" -TargetRoot "srcB/.cursor/rules" -Json
Emit JSON diff summary.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateScript({ Test-Path $_ })][string]$SourceRoot,
    [Parameter(Mandatory)][ValidateScript({ Test-Path $_ })][string]$TargetRoot,
    [Parameter()][switch]$Json,
    [Parameter()][switch]$PassThru
)

$ErrorActionPreference = 'Stop'
if ($Json) { $ProgressPreference = 'SilentlyContinue' }

# Import shared utilities
$ModulePath = Join-Path $PSScriptRoot "..\\modules\\Common.psm1"
Import-Module $ModulePath -Force

function Get-Inventory {
    param([string]$Root)
    $resolved = Resolve-Path -Path $Root -ErrorAction Stop
    $files = Get-ChildItem -Path $resolved.Path -Recurse -File
    $map = @{}
    foreach ($f in $files) {
        $rel = Normalize($f.FullName.Substring($resolved.Path.Length + 1))
        $hash = (Get-FileHash -Path $f.FullName -Algorithm SHA256).Hash
        $map[$rel] = $hash
    }
    return ,@($resolved.Path),$map
}

try {
    $sourcePath, $sourceMap = Get-Inventory -Root $SourceRoot
    $targetPath, $targetMap = Get-Inventory -Root $TargetRoot

    $allKeys = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($k in $sourceMap.Keys) { $allKeys.Add($k) | Out-Null }
    foreach ($k in $targetMap.Keys) { $allKeys.Add($k) | Out-Null }

    $added = @()
    $removed = @()
    $modified = @()

    foreach ($k in $allKeys) {
        $inSrc = $sourceMap.ContainsKey($k)
        $inTgt = $targetMap.ContainsKey($k)
        if ($inSrc -and -not $inTgt) {
            $added += $k
        } elseif (-not $inSrc -and $inTgt) {
            $removed += $k
        } else {
            if ($sourceMap[$k] -ne $targetMap[$k]) {
                $modified += $k
            }
        }
    }

    $report = [pscustomobject]@{
        SourceRoot = $sourcePath
        TargetRoot = $targetPath
        Added      = $added
        Removed    = $removed
        Modified   = $modified
        AddedCount    = $added.Count
        RemovedCount  = $removed.Count
        ModifiedCount = $modified.Count
    }

    if ($Json) {
        $report | ConvertTo-Json -Depth 5
        if ((($added.Count + $removed.Count + $modified.Count) -gt 0)) { exit 1 } else { exit 0 }
    }

    Write-Host "Source: $sourcePath" -ForegroundColor Gray
    Write-Host "Target: $targetPath" -ForegroundColor Gray
    if ($added.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'info') Added (source only): $($added.Count)" -ForegroundColor Yellow
        $added | Select-Object -First 30 | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
        if ($added.Count -gt 30) { Write-Host " ... truncated ..." -ForegroundColor Yellow }
    } else { Write-Host "No new files in source." -ForegroundColor Green }

    if ($removed.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'warning') Removed (target only): $($removed.Count)" -ForegroundColor Yellow
        $removed | Select-Object -First 30 | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
        if ($removed.Count -gt 30) { Write-Host " ... truncated ..." -ForegroundColor Yellow }
    } else { Write-Host "No files missing from source." -ForegroundColor Green }

    if ($modified.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'warning') Modified (content differs): $($modified.Count)" -ForegroundColor Yellow
        $modified | Select-Object -First 30 | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
        if ($modified.Count -gt 30) { Write-Host " ... truncated ..." -ForegroundColor Yellow }
    } else { Write-Host "No content differences." -ForegroundColor Green }

    if ($PassThru) { $report }
    if (($added.Count + $removed.Count + $modified.Count) -gt 0) { exit 1 } else { exit 0 }
}
catch {
    Write-Host "$(Get-StatusGlyph 'error') Failure: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}


