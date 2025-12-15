#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Find templars/exemplars with no consumers and missing metadata.

.DESCRIPTION
Scans templars and exemplars under a prompts root, checks frontmatter fields,
and searches consumer roots for references. Reports dead candidates (no
references and missing consumed-by/illustrates) plus metadata gaps.

.PARAMETER PromptsRoot
Root folder containing prompts/templars/exemplars. Default: repo/.cursor/prompts

.PARAMETER SearchRoots
Folders to scan for references (Select-String). Default: repo root (.)

.PARAMETER Json
Output report as JSON (progress suppressed).

.PARAMETER PassThru
Return report object instead of console summary.

.EXAMPLE
.\find-dead-templars-exemplars.ps1
Console summary for .cursor/prompts using repo root as search scope.

.EXAMPLE
.\find-dead-templars-exemplars.ps1 -PromptsRoot ".cursor/prompts" -SearchRoots "."
Scan default prompts root and repo for references.

.EXAMPLE
.\find-dead-templars-exemplars.ps1 -Json
Emit JSON for automation.
#>
[CmdletBinding()]
param(
    [Parameter()][ValidateScript({ Test-Path $_ })][string]$PromptsRoot = $(if ($PSScriptRoot) { Join-Path $PSScriptRoot "..\\.cursor\\prompts" } else { Join-Path (Get-Location).Path ".cursor\\prompts" }),
    [Parameter()][ValidateScript({ ($_ | ForEach-Object { Test-Path $_ }) -notcontains $false })][string[]]$SearchRoots = @("."),
    [Parameter()][switch]$Json,
    [Parameter()][switch]$PassThru
)

$ErrorActionPreference = 'Stop'
if ($Json) { $ProgressPreference = 'SilentlyContinue' }

# Import shared utilities
$ModulePath = Join-Path $PSScriptRoot "..\\modules\\Common.psm1"
Import-Module $ModulePath -Force

function Load-Frontmatter {
    param([string]$FilePath)
    $data = @{
        Implements   = @()
        Illustrates  = @()
        ConsumedBy   = @()
        ExtractedFrom= @()
    }
    $lines = Get-Content -Path $FilePath -TotalCount 120 -ErrorAction Stop
    $inHeader = $false
    foreach ($line in $lines) {
        if ($line -match '^---\s*$') {
            $inHeader = -not $inHeader
            if (-not $inHeader) { break }
            continue
        }
        if ($inHeader) {
            if ($line -match '^\s*implements:\s*(.+)$')   { $data.Implements += $Matches[1].Trim() }
            if ($line -match '^\s*illustrates:\s*(.+)$')  { $data.Illustrates += $Matches[1].Trim() }
            if ($line -match '^\s*consumed-by:\s*(.+)$')  { $data.ConsumedBy += $Matches[1].Trim() }
            if ($line -match '^\s*extracted-from:\s*(.+)$'){ $data.ExtractedFrom += $Matches[1].Trim() }
        }
    }
    return $data
}

try {
    $root = Resolve-Path -Path $PromptsRoot -ErrorAction Stop
    $templars = Get-ChildItem -Path (Join-Path $root.Path "templars") -Recurse -Filter '*.md' -File -ErrorAction SilentlyContinue
    $exemplars = Get-ChildItem -Path (Join-Path $root.Path "exemplars") -Recurse -Filter '*.md' -File -ErrorAction SilentlyContinue

    $items = @()
    foreach ($f in $templars) {
        $meta = Load-Frontmatter -FilePath $f.FullName
        $items += [pscustomobject]@{
            Path          = Normalize($f.FullName.Substring($root.Path.Length + 1))
            Kind          = 'templar'
            Meta          = $meta
        }
    }
    foreach ($f in $exemplars) {
        $meta = Load-Frontmatter -FilePath $f.FullName
        $items += [pscustomobject]@{
            Path          = Normalize($f.FullName.Substring($root.Path.Length + 1))
            Kind          = 'exemplar'
            Meta          = $meta
        }
    }

    # Build search patterns
    $results = @()
    foreach ($item in $items) {
        $basename = [IO.Path]::GetFileNameWithoutExtension($item.Path)
        $needFields = @()
        if ($item.Kind -eq 'templar' -and ($item.Meta.ConsumedBy.Count -eq 0)) { $needFields += 'consumed-by' }
        if ($item.Kind -eq 'exemplar' -and ($item.Meta.Illustrates.Count -eq 0)) { $needFields += 'illustrates' }
        if ($item.Meta.Implements.Count -eq 0 -and $item.Kind -eq 'templar') { $needFields += 'implements' }
        if ($item.Meta.ExtractedFrom.Count -eq 0 -and $item.Kind -eq 'exemplar') { $needFields += 'extracted-from' }

        $matches = @()
        foreach ($sr in $SearchRoots) {
            $scope = Resolve-Path -Path $sr -ErrorAction Stop
            $hit = Select-String -Path (Join-Path $scope.Path '*') -Pattern $basename -SimpleMatch -ErrorAction SilentlyContinue
            $matches += $hit
            if ($item.Meta.Implements) {
                foreach ($id in $item.Meta.Implements) {
                    $matches += Select-String -Path (Join-Path $scope.Path '*') -Pattern $id -SimpleMatch -ErrorAction SilentlyContinue
                }
            }
            if ($item.Meta.Illustrates) {
                foreach ($id in $item.Meta.Illustrates) {
                    $matches += Select-String -Path (Join-Path $scope.Path '*') -Pattern $id -SimpleMatch -ErrorAction SilentlyContinue
                }
            }
        }

        $refCount = @($matches).Count
        $isDead = $false
        if ($refCount -eq 0) {
            if ($item.Kind -eq 'templar' -and ($item.Meta.ConsumedBy.Count -eq 0)) { $isDead = $true }
            if ($item.Kind -eq 'exemplar' -and ($item.Meta.Illustrates.Count -eq 0)) { $isDead = $true }
        }

        $results += [pscustomobject]@{
            Path            = $item.Path
            Kind            = $item.Kind
            References      = $refCount
            MissingMetadata = $needFields
            DeadCandidate   = $isDead
        }
    }

    $dead = $results | Where-Object { $_.DeadCandidate }
    $missingMeta = $results | Where-Object { $_.MissingMetadata.Count -gt 0 }

    $report = [pscustomobject]@{
        PromptsRoot    = $root.Path
        TotalTemplars  = @($templars).Count
        TotalExemplars = @($exemplars).Count
        DeadCount      = @($dead).Count
        MissingMeta    = $missingMeta
        Dead           = $dead
    }

    if ($Json) {
        $report | ConvertTo-Json -Depth 5
        if (($dead.Count -gt 0) -or ($missingMeta.Count -gt 0)) { exit 1 } else { exit 0 }
    }

    Write-Host "Prompts root: $($root.Path)" -ForegroundColor Gray
    Write-Host "Templars: $(@($templars).Count)  Exemplars: $(@($exemplars).Count)" -ForegroundColor Gray
    if ($dead.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'error') Dead candidates: $($dead.Count)" -ForegroundColor Red
        $dead | ForEach-Object { Write-Host " - $($_.Path) (refs=$($_.References))" -ForegroundColor Red }
    } else {
        Write-Host "$(Get-StatusGlyph 'success') No dead templars/exemplars detected." -ForegroundColor Green
    }
    if ($missingMeta.Count -gt 0) {
        Write-Host "$(Get-StatusGlyph 'warning') Missing metadata: $($missingMeta.Count)" -ForegroundColor Yellow
        $missingMeta | ForEach-Object { Write-Host " - $($_.Path): $(@($_.MissingMetadata) -join ', ')" -ForegroundColor Yellow }
    } else {
        Write-Host "$(Get-StatusGlyph 'success') Metadata present for all checked fields." -ForegroundColor Green
    }

    if ($PassThru) { $report }

    if (($dead.Count -gt 0) -or ($missingMeta.Count -gt 0)) { exit 1 } else { exit 0 }
}
catch {
    Write-Host "$(Get-StatusGlyph 'error') Failure: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}


