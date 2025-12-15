#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Identify candidate obsolete artifacts based on age and zero references.

.DESCRIPTION
Scans a folder for artifacts, checks last write time and reference count across
the repository. Reports candidates for archival (old + zero references).

.PARAMETER Folder
Folder to scan (default: repo/.cursor)

.PARAMETER ReferenceRoots
Roots to search for references (default: repo root ".")

.PARAMETER AgeDays
Minimum age in days to consider obsolete (default: 180).

.PARAMETER Json
Output report as JSON.

.PARAMETER PassThru
Return report object.

.EXAMPLE
.\archive-obsolete-artifacts.ps1
Scan .cursor with 180-day threshold.

.EXAMPLE
.\archive-obsolete-artifacts.ps1 -Folder ".cursor/rules" -AgeDays 365 -Json

#>
[CmdletBinding()]
param(
    [Parameter()][ValidateScript({ Test-Path $_ })][string]$Folder = $(Join-Path (Get-Location).Path ".cursor"),
    [Parameter()][ValidateScript({ ($_ | ForEach-Object { Test-Path $_ }) -notcontains $false })][string[]]$ReferenceRoots = @("."),
    [Parameter()][ValidateRange(1, 10000)][int]$AgeDays = 180,
    [Parameter()][ValidateScript({ -not $_ -or (Test-Path $_) })][string]$ConfigFile,
    [Parameter()][switch]$Json,
    [Parameter()][switch]$PassThru
)

$ErrorActionPreference = 'Stop'
if ($Json) { $ProgressPreference = 'SilentlyContinue' }

# Import shared utilities
$ModulePath = Join-Path $PSScriptRoot "../modules/Common.psm1"
Import-Module $ModulePath -Force

try {
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        $config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
        if (-not $PSBoundParameters.ContainsKey('Folder') -and $config.Folder) { $Folder = $config.Folder }
        if (-not $PSBoundParameters.ContainsKey('ReferenceRoots') -and $config.ReferenceRoots) { $ReferenceRoots = $config.ReferenceRoots }
        if (-not $PSBoundParameters.ContainsKey('AgeDays') -and $config.AgeDays) { $AgeDays = [int]$config.AgeDays }
        if (-not $PSBoundParameters.ContainsKey('Json') -and $null -ne $config.Json) { $Json = [bool]$config.Json }
        if (-not $PSBoundParameters.ContainsKey('PassThru') -and $null -ne $config.PassThru) { $PassThru = [bool]$config.PassThru }
    }

    $root = Resolve-Path -Path $Folder -ErrorAction Stop
    $files = Get-ChildItem -Path $root.Path -Recurse -File -Include *.md,*.mdc,*.prompt.md
    $cutoff = (Get-Date).AddDays(-1 * $AgeDays)

    $candidates = @()
    foreach ($f in $files) {
        if ($f.LastWriteTime -gt $cutoff) { continue }
        $name = [IO.Path]::GetFileNameWithoutExtension($f.Name)
        $refCount = 0
        foreach ($rr in $ReferenceRoots) {
            $scope = Resolve-Path -Path $rr -ErrorAction Stop
            $hits = Select-String -Path (Join-Path $scope.Path '*') -Pattern $name -SimpleMatch -ErrorAction SilentlyContinue
            $refCount += @($hits).Count
        }
        if ($refCount -eq 0) {
            $candidates += [pscustomobject]@{
                Path          = Normalize($f.FullName.Substring($root.Path.Length + 1))
                LastWriteTime = $f.LastWriteTime
                ReferenceCount= 0
            }
        }
    }

    $report = [pscustomobject]@{
        Folder     = $root.Path
        AgeDays    = $AgeDays
        Scanned    = @($files).Count
        Candidates = $candidates
        CandidateCount = @($candidates).Count
    }

    if ($Json) {
        $report | ConvertTo-Json -Depth 5
        if ($candidates.Count -gt 0) { exit 1 } else { exit 0 }
    }

    Write-Host "Folder: $($root.Path) | Threshold: $AgeDays days" -ForegroundColor Gray
    Write-Host "Files scanned: $(@($files).Count)" -ForegroundColor Gray
    if ($candidates.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'warning') Obsolete candidates: $($candidates.Count)" -ForegroundColor Yellow
        $candidates | Select-Object -First 50 | ForEach-Object { Write-Host " - $($_.Path) (Last: $($_.LastWriteTime))" -ForegroundColor Yellow }
        if ($candidates.Count -gt 50) { Write-Host " ... truncated ..." -ForegroundColor Yellow }
    } else {
        Write-Host "$(Get-StatusGlyph 'success') No obsolete candidates found." -ForegroundColor Green
    }

    if ($PassThru) { $report }
    if ($candidates.Count -gt 0) { exit 1 } else { exit 0 }
}
catch {
    Write-Host "$(Get-StatusGlyph 'error') Failure: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}


