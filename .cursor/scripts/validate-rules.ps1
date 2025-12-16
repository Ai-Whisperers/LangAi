# .cursor/scripts/validate-rules.ps1
# Validates all rule files in .cursor/rules against the rule-authoring framework standards.

param(
    [string]$RulesDir = ".cursor/rules",
    [string]$IndexFile = ".cursor/rules/rule-index.yml"
)

$ErrorActionPreference = "Stop"

function Test-CursorFile {
    param([string]$FilePath)

    $content = Get-Content -Path $FilePath -Raw
    $fileName = Split-Path $FilePath -Leaf
    $dirName = Split-Path (Split-Path $FilePath -Parent) -Leaf # e.g., 'rules', 'templars'
    $errors = @()

    # 1. Validate Front-Matter
    # Allow for BOM or leading whitespace
    if ($content -notmatch '(?s)^\s*---\r?\n(.*?)\r?\n---') {
        $errors += "Missing YAML front-matter"
        return $errors
    }

    $frontMatter = $matches[1]

    # Extract ID and Kind for specific checks
    $id = ""
    $kind = ""
    if ($frontMatter -match 'id:\s*([^\s]+)') { $id = $matches[1].Trim() }
    if ($frontMatter -match 'kind:\s*([^\s]+)') { $kind = $matches[1].Trim() }

    # Common Required fields
    $requiredFields = @('id', 'kind', 'version', 'description', 'provenance')

    # Specific requirements based on Kind
    switch ($kind) {
        "rule" {
            $requiredFields += 'implements'
            $requiredFields += 'requires'

            # Strategy 2 exception: Agent application rules don't need globs/governs
            if ($fileName -notlike "*agent-application-rule.mdc") {
                $requiredFields += 'globs'
                $requiredFields += 'governs'
            }

            # Validate ID format: rule.[domain].[action].v[major]
            if ($id -notmatch '^rule\.[a-z0-9-]+\.[a-z0-9-]+\.v\d+$') {
                $errors += "Invalid Rule ID format: $id. Must be rule.[domain].[action].v[major]"
            }

            # Validate globs/governs syntax (comma-separated string, NOT array)
            if ($frontMatter -match 'globs:\s*\[') {
                $errors += "Invalid globs format: Found '['. Must be comma-separated string, NOT YAML array."
            }
            if ($frontMatter -match 'governs:\s*\[') {
                $errors += "Invalid governs format: Found '['. Must be comma-separated string, NOT YAML array."
            }

            # Validate Canonical Structure
            if ($content -notmatch '## FINAL MUST-PASS CHECKLIST') {
                $errors += "Missing '## FINAL MUST-PASS CHECKLIST' section"
            }

            # Check checklist position
            $lastSectionMatch = $content | Select-String -Pattern '(?m)^##\s+(.+)$' -AllMatches
            if ($lastSectionMatch) {
                $lastSection = $lastSectionMatch.Matches[$lastSectionMatch.Matches.Count - 1].Groups[1].Value.Trim()
                if ($lastSection -ne "FINAL MUST-PASS CHECKLIST") {
                    $errors += "Checklist is not the last section. Found: '$lastSection'"
                }
            }
        }
        "templar" {
            $requiredFields += 'implements'
            # Validate ID format: templar.[target].v[major]
            # Updated to allow dots in target part
            if ($id -notmatch '^templar\.[a-z0-9.-]+\.v\d+$') {
                $errors += "Invalid Templar ID format: $id. Must be templar.[target].v[major]"
            }
        }
        "exemplar" {
            $requiredFields += 'illustrates'
            $requiredFields += 'use'
            # Validate ID format: exemplar.[target].[qualifier].v[major]
            # Updated to allow dots in target part (e.g. agile.user-story)
            if ($id -notmatch '^exemplar\.[a-z0-9.-]+\.[a-z0-9-]+\.v\d+$') {
                $errors += "Invalid Exemplar ID format: $id. Must be exemplar.[target].[qualifier].v[major]"
            }
        }
        "prompt" {
             # Basic requirements for prompts if we standardize them
             # Currently no strict ID format defined in my context, but assuming rule.authoring.naming-conventions applies broadly
        }
        default {
             # If kind is missing or unknown, we just check common fields
        }
    }

    foreach ($field in $requiredFields) {
        if ($frontMatter -notmatch "(?m)^${field}:") {
            $errors += "Missing required field: $field"
        }
    }

    return $errors
}

function Validate-Index-Consistency {
    param([string]$IndexFile, [string]$RulesDir, [string]$TemplarsDir, [string]$ExemplarsDir)

    $indexContent = Get-Content -Path $IndexFile -Raw

    # Gather all files that SHOULD be indexed
    $filesToIndex = @()
    if (Test-Path $RulesDir) { $filesToIndex += Get-ChildItem -Path $RulesDir -Recurse -Filter "*-rule.mdc" }
    if (Test-Path $TemplarsDir) { $filesToIndex += Get-ChildItem -Path $TemplarsDir -Recurse -Include "*.md","*.yml" }
    if (Test-Path $ExemplarsDir) { $filesToIndex += Get-ChildItem -Path $ExemplarsDir -Recurse -Filter "*.md" }

    $missingFromIndex = @()

    # Parse index into a set for safe lookup
    $indexMap = @{}
    $indexLines = $indexContent -split "`r?`n"
    foreach ($line in $indexLines) {
        if ($line -match '^\s*([^:]+):') {
            $key = $matches[1].Trim()
            $indexMap[$key] = $true
        }
    }

    foreach ($file in $filesToIndex) {
        # Extract ID from file
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -match 'id:\s*([^\s]+)') {
            $id = $matches[1].Trim()

            # Check if ID is in index map
            if (-not $indexMap.ContainsKey($id)) {
                $relPath = $file.FullName.Substring($PWD.Path.Length + 1).Replace("\", "/")
                $missingFromIndex += "Entity '$id' ($relPath) is missing from $IndexFile"
            }
        }
    }

    # Check for references in index that don't exist on disk
    $indexLines = $indexContent -split "`r?`n"
    foreach ($line in $indexLines) {
        if ($line -match ':\s*(.+)$' -and $line -notmatch '^\s*#') {
            $path = $matches[1].Trim()

            # Logic to resolve path
            if ($path -like ".cursor*") {
                # Path is relative to repo root (e.g. .cursor/templars/...)
                $fullPath = Join-Path $PWD.Path $path
            } else {
                # Path is relative to rules dir (e.g. agile/foo.mdc)
                $fullPath = Join-Path (Join-Path $PWD.Path ".cursor/rules") $path
            }

            if (-not (Test-Path $fullPath)) {
                $missingFromIndex += "Index references missing file: '$path' (checked: $fullPath)"
            }
        }
    }

    return $missingFromIndex
}

Write-Host "Starting comprehensive validation..." -ForegroundColor Cyan

$baseDir = ".cursor"
$rulesDir = Join-Path $baseDir "rules"
$templarsDir = Join-Path $baseDir "templars"
$exemplarsDir = Join-Path $baseDir "exemplars"
$promptsDir = Join-Path $baseDir "prompts"

$filesToTest = @()
if (Test-Path $rulesDir) { $filesToTest += Get-ChildItem -Path $rulesDir -Recurse -Filter "*-rule.mdc" }
if (Test-Path $templarsDir) { $filesToTest += Get-ChildItem -Path $templarsDir -Recurse -Include "*.md","*.yml" }
if (Test-Path $exemplarsDir) { $filesToTest += Get-ChildItem -Path $exemplarsDir -Recurse -Filter "*.md" }
# Prompts validation - Optional strictness, but let's check
if (Test-Path $promptsDir) { $filesToTest += Get-ChildItem -Path $promptsDir -Recurse -Filter "*.md" }

$failedCount = 0
$passedCount = 0

foreach ($file in $filesToTest) {
    $relPath = $file.FullName.Substring($PWD.Path.Length + 1)
    $errors = Test-CursorFile -FilePath $file.FullName

    if ($errors.Count -gt 0) {
        Write-Host "FAIL: $relPath" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "  - $err" -ForegroundColor Yellow
        }
        $failedCount++
    } else {
        # Write-Host "PASS: $relPath" -ForegroundColor Green
        $passedCount++
    }
}

# Run Index Consistency Check
$IndexFile = ".cursor/rules/rule-index.yml"
Write-Host "`nChecking Index Consistency..." -ForegroundColor Cyan
if (Test-Path $IndexFile) {
    $indexErrors = Validate-Index-Consistency -IndexFile $IndexFile -RulesDir $rulesDir -TemplarsDir $templarsDir -ExemplarsDir $exemplarsDir
    if ($indexErrors.Count -gt 0) {
        $failedCount++
        Write-Host "FAIL: Index ($IndexFile) is incomplete" -ForegroundColor Red
        foreach ($err in $indexErrors) {
            Write-Host "  - $err" -ForegroundColor Yellow
        }
    } else {
        Write-Host "PASS: All entities are indexed" -ForegroundColor Green
    }
} else {
    Write-Host "WARN: Index file not found at $IndexFile" -ForegroundColor Yellow
}

Write-Host "`nValidation Complete." -ForegroundColor Cyan
Write-Host "Passed: $passedCount" -ForegroundColor Green
Write-Host "Failed: $failedCount" -ForegroundColor Red

if ($failedCount -gt 0) {
    exit 1
} else {
    exit 0
}
