#!/usr/bin/env pwsh
#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
Validates prompt collection manifests against prompt files with a progress bar.

.DESCRIPTION
Scans a prompts root (default: .cursor/prompts) to verify:
- Every prompt folder with *.prompt.md files has a matching collection manifest.
- Every *.prompt.md is referenced by at least one collection item path.
- Every collection item path points to an existing prompt file.

Emits a summary to the console, exits 1 when gaps exist, and optionally returns the report object with -PassThru.

.PARAMETER PromptsRoot
Root folder containing prompts and collections (default: repo/.cursor/prompts).

.PARAMETER PassThru
Return the report object to the pipeline instead of console-only.

.PARAMETER Json
Output the report as JSON (suppresses console summary). Useful for automation.

.EXAMPLE
.\validate-prompt-collections.ps1
Runs validation against .cursor/prompts using defaults.

.EXAMPLE
.\validate-prompt-collections.ps1 -PromptsRoot "..\other\.cursor\prompts" -PassThru
Validates an alternate prompts root and returns the report object.

.EXAMPLE
.\validate-prompt-collections.ps1 -Json
Outputs the validation report as JSON for scripts/automation.

.NOTES
Quality: Standard (per script standards). Uses Write-Progress for visibility.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    # Script lives in `.cursor/scripts/housekeeping/`; default prompts root is `.cursor/prompts/`.
    [string]$PromptsRoot = $(if ($PSScriptRoot) { Join-Path $PSScriptRoot "..\\..\\prompts" } else { Join-Path (Get-Location).Path ".cursor\\prompts" }),

    [Parameter(Mandatory = $false)]
    [switch]$PassThru,

    [Parameter(Mandatory = $false)]
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Write-Section {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $false)][ConsoleColor]$Color = 'Cyan'
    )
    Write-Host $Message -ForegroundColor $Color
}

function Normalize-PathForKey {
    param([string]$Path)
    return ($Path -replace '\\', '/')
}

try {
    if ($Json) {
        $ProgressPreference = 'SilentlyContinue'
    }
    $totalSteps = 4
    $activity = 'Validate prompt collections'
    $step = 0

    $resolvedRoot = Resolve-Path -Path $PromptsRoot -ErrorAction Stop
    $promptsRootPath = $resolvedRoot.Path

    $step++
    Write-Progress -Activity $activity -Status 'Scanning prompt files' -PercentComplete (($step / $totalSteps) * 100)
    $promptFiles = Get-ChildItem -Path $promptsRootPath -Recurse -Filter '*.prompt.md' | Where-Object { $_.FullName -notmatch '\\collections\\' }
    $promptPaths = @{}
    $promptKeyList = @()
    foreach ($p in $promptFiles) {
        $relative = Normalize-PathForKey($p.FullName.Substring($promptsRootPath.Length + 1))
        $promptKeyList += $relative
        $promptPaths[$relative] = $true
        $promptPaths[$(Normalize-PathForKey("prompts/$relative"))] = $true
    }

    $step++
    Write-Progress -Activity $activity -Status 'Reading collection manifests' -PercentComplete (($step / $totalSteps) * 100)
    $collectionDir = Join-Path $promptsRootPath 'collections'
    if (-not (Test-Path $collectionDir -PathType Container)) {
        throw "Collections folder not found: $collectionDir"
    }

    $collections = Get-ChildItem -Path $collectionDir -Filter '*.collection.yml'
    $collectionEntries = @()
    foreach ($c in $collections) {
        $lines = Get-Content -Path $c.FullName
        foreach ($line in $lines) {
            if ($line -match '^\s*-\s*path:\s*(.+)$' -or $line -match '^\s*path:\s*(.+)$') {
                $path = $Matches[1].Trim().Trim('"').Trim("'")
                $collectionEntries += [pscustomobject]@{
                    Collection = $c.Name
                    Path       = Normalize-PathForKey($path)
                }
            }
        }
    }

    $step++
    Write-Progress -Activity $activity -Status 'Cross-checking coverage' -PercentComplete (($step / $totalSteps) * 100)
    $collectionPaths = @{}
    foreach ($entry in $collectionEntries) {
        $collectionPaths[$entry.Path] = $entry.Collection
        $collectionPaths[$(Normalize-PathForKey(($entry.Path -replace '^prompts/', '')))] = $entry.Collection
    }

    $missingPromptEntries = $promptKeyList | Where-Object { -not $collectionPaths.ContainsKey($_) } | Sort-Object
    $brokenCollectionPaths = @()
    foreach ($entry in $collectionEntries) {
        $candidate = Join-Path $promptsRootPath $entry.Path
        if (-not (Test-Path $candidate -PathType Leaf) -and -not $promptPaths.ContainsKey($entry.Path)) {
            $brokenCollectionPaths += $entry
        }
    }
    $brokenCollectionPaths = $brokenCollectionPaths | Sort-Object Path

    $foldersWithPrompts = $promptKeyList | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique
    $foldersMissingCollection = @()
    foreach ($folder in $foldersWithPrompts) {
        $expected = Join-Path $collectionDir "$folder.collection.yml"
        if (-not (Test-Path $expected -PathType Leaf)) {
            $foldersMissingCollection += $folder
        }
    }
    $foldersMissingCollection = $foldersMissingCollection | Sort-Object

    $step++
    Write-Progress -Activity $activity -Status 'Reporting' -PercentComplete (($step / $totalSteps) * 100)

    $report = [pscustomobject]@{
        PromptsRoot              = $promptsRootPath
        PromptCount              = $promptPaths.Count
        CollectionItemCount      = $collectionEntries.Count
        MissingPromptEntries     = $missingPromptEntries
        BrokenCollectionPaths    = $brokenCollectionPaths
        FoldersWithPrompts       = $foldersWithPrompts
        FoldersMissingCollection = $foldersMissingCollection
    }

    if (-not $Json) {
        Write-Section "Prompts root: $promptsRootPath" 'Gray'
        Write-Section "Prompt files: $($promptPaths.Count)" 'Gray'
        Write-Section "Collection items: $($collectionEntries.Count)" 'Gray'

        if ($missingPromptEntries.Count -gt 0) {
            Write-Section "❌ Prompts missing collection entries: $($missingPromptEntries.Count)" 'Red'
            $missingPromptEntries | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
        } else {
            Write-Section "✅ All prompts are covered by collection entries." 'Green'
        }

        if ($brokenCollectionPaths.Count -gt 0) {
            Write-Section "❌ Collection paths that do not exist: $($brokenCollectionPaths.Count)" 'Red'
            $brokenCollectionPaths | ForEach-Object { Write-Host " - $($_.Collection): $($_.Path)" -ForegroundColor Red }
        } else {
            Write-Section "✅ All collection paths point to existing prompt files." 'Green'
        }

        if ($foldersMissingCollection.Count -gt 0) {
            Write-Section "⚠ Folders with prompts but no collection manifest: $($foldersMissingCollection.Count)" 'Yellow'
            $foldersMissingCollection | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
        } else {
            Write-Section "✅ Every prompt folder has a collection manifest." 'Green'
        }
    }

    $hasIssues = ($missingPromptEntries.Count -gt 0) -or ($brokenCollectionPaths.Count -gt 0) -or ($foldersMissingCollection.Count -gt 0)

    if ($Json) {
        $json = $report | ConvertTo-Json -Depth 5
        Write-Output $json
        if ($hasIssues) { exit 1 } else { exit 0 }
    } elseif ($PassThru) {
        $report
    } else {
        # console already emitted
    }

    if ($hasIssues) { exit 1 }
    exit 0
}
catch {
    Write-Section "❌ Validation failed: $($_.Exception.Message)" 'Red'
    exit 1
}
