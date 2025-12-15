# Complete Repository Sync Analysis Script
# Compares rules, prompts, and scripts between two repositories
#
# Usage:
#   .\compare-complete.ps1
#   .\compare-complete.ps1 -SourceRepo "path\to\source" -TargetRepo "path\to\target"
#   .\compare-complete.ps1 -RulesMask "*.mdc" -PromptsMask "*.md" -ScriptsMask "*.ps1"
#
# Output:
#   - Console report with categorized files (ADD, UPDATE, IN-SYNC)
#   - CSV files for each category (rules, prompts, scripts)
#
# Categories:
#   [A] Files to ADD: Missing in target repository
#   [B] Files to UPDATE: Different content/versions
#   [D] Files IN SYNC: Matching content

param(
    [Parameter(Mandatory=$false, HelpMessage="Path to source repository")]
    [string]$SourceRepo = "E:\WPG\Git\E21\GitRepos\eneve.ebase.foundation",
    
    [Parameter(Mandatory=$false, HelpMessage="Path to target repository")]
    [string]$TargetRepo = "E:\WPG\Git\E21\GitRepos\eneve.domain",
    
    [Parameter(Mandatory=$false, HelpMessage="File mask for rules (default: *.mdc)")]
    [string]$RulesMask = "*.mdc",
    
    [Parameter(Mandatory=$false, HelpMessage="File mask for prompts (default: *.md)")]
    [string]$PromptsMask = "*.md",
    
    [Parameter(Mandatory=$false, HelpMessage="File mask for scripts (default: *.ps1)")]
    [string]$ScriptsMask = "*.ps1",
    
    [Parameter(Mandatory=$false, HelpMessage="Rules folder relative path (default: .cursor\rules)")]
    [string]$RulesPath = ".cursor\rules",
    
    [Parameter(Mandatory=$false, HelpMessage="Prompts folder relative path (default: .cursor\prompts)")]
    [string]$PromptsPath = ".cursor\prompts"
)

# Normalize paths
$sourceRepo = $SourceRepo.TrimEnd('\')
$targetRepo = $TargetRepo.TrimEnd('\')
$targetRepoName = Split-Path $targetRepo -Leaf

Write-Host "`n=== COMPLETE REPOSITORY SYNC ANALYSIS ===" -ForegroundColor Cyan
Write-Host "Source: $sourceRepo" -ForegroundColor Gray
Write-Host "Target: $targetRepo" -ForegroundColor Gray
Write-Host "Rules Mask: $RulesMask" -ForegroundColor DarkGray
Write-Host "Prompts Mask: $PromptsMask" -ForegroundColor DarkGray
Write-Host "Scripts Mask: $ScriptsMask`n" -ForegroundColor DarkGray

# ============================================================
# PART 1: ANALYZE RULES
# ============================================================
Write-Host "=== ANALYZING RULES ($RulesMask files) ===" -ForegroundColor Yellow

$rulesResults = @()
$sourceRulesPath = Join-Path $sourceRepo $RulesPath
$targetRulesPath = Join-Path $targetRepo $RulesPath

if (Test-Path $sourceRulesPath) {
    $sourceRules = Get-ChildItem -Path $sourceRulesPath -Recurse -Filter $RulesMask

    foreach ($sourceRule in $sourceRules) {
        $relativePath = $sourceRule.FullName.Replace("$sourceRulesPath\", "")
        $targetPath = Join-Path $targetRulesPath $relativePath
        
        # Extract version from source (only for .mdc files with front-matter)
        $sourceContent = Get-Content $sourceRule.FullName -Raw
        if ($RulesMask -eq "*.mdc" -and $sourceContent -match '(?s)^---\s*\n(.*?)\n---') {
            $sourceFrontMatter = $matches[1]
            $sourceVersion = if ($sourceFrontMatter -match 'version:\s*([^\s]+)') { $matches[1] } else { "N/A" }
            $sourceId = if ($sourceFrontMatter -match 'id:\s*([^\s]+)') { $matches[1] } else { "N/A" }
        } else {
            $sourceVersion = "N/A"
            $sourceId = "N/A"
        }
        
        # Check target
        if (Test-Path $targetPath) {
            if ($RulesMask -eq "*.mdc") {
                $targetContent = Get-Content $targetPath -Raw
                if ($targetContent -match '(?s)^---\s*\n(.*?)\n---') {
                    $targetFrontMatter = $matches[1]
                    $targetVersion = if ($targetFrontMatter -match 'version:\s*([^\s]+)') { $matches[1] } else { "N/A" }
                } else {
                    $targetVersion = "NO-FM"
                }
                $status = if ($sourceVersion -eq $targetVersion) { "IN-SYNC" } else { "UPDATE" }
            } else {
                # Use hash comparison for non-.mdc files
                $sourceHash = (Get-FileHash -Path $sourceRule.FullName -Algorithm MD5).Hash
                $targetHash = (Get-FileHash -Path $targetPath -Algorithm MD5).Hash
                $targetVersion = $targetHash.Substring(0, 8)
                $status = if ($sourceHash -eq $targetHash) { "IN-SYNC" } else { "UPDATE" }
            }
        } else {
            $targetVersion = "MISSING"
            $status = "ADD"
        }
        
        $rulesResults += [PSCustomObject]@{
            File = $relativePath
            SourceId = $sourceId
            SourceVersion = $sourceVersion
            TargetVersion = $targetVersion
            Status = $status
        }
    }
} else {
    Write-Host "  [WARN] Source rules path not found: $sourceRulesPath" -ForegroundColor Yellow
    $sourceRules = @()
}

$rulesAdd = ($rulesResults | Where-Object { $_.Status -eq "ADD" }).Count
$rulesUpdate = ($rulesResults | Where-Object { $_.Status -eq "UPDATE" }).Count
$rulesSync = ($rulesResults | Where-Object { $_.Status -eq "IN-SYNC" }).Count

Write-Host "Rules to ADD: $rulesAdd" -ForegroundColor $(if ($rulesAdd -gt 0) { "Red" } else { "Green" })
Write-Host "Rules to UPDATE: $rulesUpdate" -ForegroundColor $(if ($rulesUpdate -gt 0) { "Yellow" } else { "Green" })
Write-Host "Rules IN SYNC: $rulesSync" -ForegroundColor Green

# ============================================================
# PART 2: ANALYZE PROMPTS
# ============================================================
Write-Host "`n=== ANALYZING PROMPTS ($PromptsMask files) ===" -ForegroundColor Yellow

$promptsResults = @()
$sourcePromptsPath = Join-Path $sourceRepo $PromptsPath
$targetPromptsPath = Join-Path $targetRepo $PromptsPath

if (Test-Path $sourcePromptsPath) {
    $sourcePrompts = Get-ChildItem -Path $sourcePromptsPath -Recurse -Filter $PromptsMask

    foreach ($sourcePrompt in $sourcePrompts) {
        $relativePath = $sourcePrompt.FullName.Replace("$sourcePromptsPath\", "")
        $targetPath = Join-Path $targetPromptsPath $relativePath
        
        # Get file hash for comparison
        $sourceHash = (Get-FileHash -Path $sourcePrompt.FullName -Algorithm MD5).Hash
        
        # Check target
        if (Test-Path $targetPath) {
            $targetHash = (Get-FileHash -Path $targetPath -Algorithm MD5).Hash
            $status = if ($sourceHash -eq $targetHash) { "IN-SYNC" } else { "UPDATE" }
        } else {
            $status = "ADD"
            $targetHash = "MISSING"
        }
        
        $promptsResults += [PSCustomObject]@{
            File = $relativePath
            SourceHash = $sourceHash.Substring(0, 8)
            TargetHash = if ($targetHash -eq "MISSING") { "MISSING" } else { $targetHash.Substring(0, 8) }
            Status = $status
        }
    }
} else {
    Write-Host "  [WARN] Source prompts path not found: $sourcePromptsPath" -ForegroundColor Yellow
    $sourcePrompts = @()
}

$promptsAdd = ($promptsResults | Where-Object { $_.Status -eq "ADD" }).Count
$promptsUpdate = ($promptsResults | Where-Object { $_.Status -eq "UPDATE" }).Count
$promptsSync = ($promptsResults | Where-Object { $_.Status -eq "IN-SYNC" }).Count

Write-Host "Prompts to ADD: $promptsAdd" -ForegroundColor $(if ($promptsAdd -gt 0) { "Red" } else { "Green" })
Write-Host "Prompts to UPDATE: $promptsUpdate" -ForegroundColor $(if ($promptsUpdate -gt 0) { "Yellow" } else { "Green" })
Write-Host "Prompts IN SYNC: $promptsSync" -ForegroundColor Green

# ============================================================
# PART 3: ANALYZE SCRIPTS
# ============================================================
Write-Host "`n=== ANALYZING SCRIPTS ($ScriptsMask files) ===" -ForegroundColor Yellow

$scriptsResults = @()
# Scripts are in prompts folder by default
$sourceScriptsPath = Join-Path $sourceRepo $PromptsPath
$targetScriptsPath = Join-Path $targetRepo $PromptsPath

if (Test-Path $sourceScriptsPath) {
    $sourceScripts = Get-ChildItem -Path $sourceScriptsPath -Recurse -Filter $ScriptsMask

    foreach ($sourceScript in $sourceScripts) {
        $relativePath = $sourceScript.FullName.Replace("$sourceScriptsPath\", "")
        $targetPath = Join-Path $targetScriptsPath $relativePath
        
        # Get file hash for comparison
        $sourceHash = (Get-FileHash -Path $sourceScript.FullName -Algorithm MD5).Hash
        
        # Check target
        if (Test-Path $targetPath) {
            $targetHash = (Get-FileHash -Path $targetPath -Algorithm MD5).Hash
            $status = if ($sourceHash -eq $targetHash) { "IN-SYNC" } else { "UPDATE" }
        } else {
            $status = "ADD"
            $targetHash = "MISSING"
        }
        
        $scriptsResults += [PSCustomObject]@{
            File = $relativePath
            SourceHash = $sourceHash.Substring(0, 8)
            TargetHash = if ($targetHash -eq "MISSING") { "MISSING" } else { $targetHash.Substring(0, 8) }
            Status = $status
        }
    }
} else {
    Write-Host "  [WARN] Source scripts path not found: $sourceScriptsPath" -ForegroundColor Yellow
    $sourceScripts = @()
}

$scriptsAdd = ($scriptsResults | Where-Object { $_.Status -eq "ADD" }).Count
$scriptsUpdate = ($scriptsResults | Where-Object { $_.Status -eq "UPDATE" }).Count
$scriptsSync = ($scriptsResults | Where-Object { $_.Status -eq "IN-SYNC" }).Count

Write-Host "Scripts to ADD: $scriptsAdd" -ForegroundColor $(if ($scriptsAdd -gt 0) { "Red" } else { "Green" })
Write-Host "Scripts to UPDATE: $scriptsUpdate" -ForegroundColor $(if ($scriptsUpdate -gt 0) { "Yellow" } else { "Green" })
Write-Host "Scripts IN SYNC: $scriptsSync" -ForegroundColor Green

# ============================================================
# SUMMARY REPORT
# ============================================================
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan

$summary = @"

RULES ($RulesMask):
  Files in Source: $($sourceRules.Count)
  To ADD: $rulesAdd
  To UPDATE: $rulesUpdate
  IN SYNC: $rulesSync
  Status: $(if ($rulesAdd -eq 0 -and $rulesUpdate -eq 0) { "✅ SYNCED" } else { "❌ NEEDS SYNC" })

PROMPTS ($PromptsMask):
  Files in Source: $($sourcePrompts.Count)
  To ADD: $promptsAdd
  To UPDATE: $promptsUpdate
  IN SYNC: $promptsSync
  Status: $(if ($promptsAdd -eq 0 -and $promptsUpdate -eq 0) { "✅ SYNCED" } else { "❌ NEEDS SYNC" })

SCRIPTS ($ScriptsMask):
  Files in Source: $($sourceScripts.Count)
  To ADD: $scriptsAdd
  To UPDATE: $scriptsUpdate
  IN SYNC: $scriptsSync
  Status: $(if ($scriptsAdd -eq 0 -and $scriptsUpdate -eq 0) { "✅ SYNCED" } else { "❌ NEEDS SYNC" })

OVERALL: $(if ($rulesAdd -eq 0 -and $rulesUpdate -eq 0 -and $promptsAdd -eq 0 -and $promptsUpdate -eq 0 -and $scriptsAdd -eq 0 -and $scriptsUpdate -eq 0) { "✅ FULLY SYNCHRONIZED" } else { "❌ SYNC REQUIRED" })
"@

Write-Host $summary

# ============================================================
# DETAILED OUTPUT (Files Needing Action)
# ============================================================

# Show files that need to be added
$allToAdd = @()
$allToAdd += $rulesResults | Where-Object { $_.Status -eq "ADD" } | Select-Object @{N='Type';E={'Rule'}}, File
$allToAdd += $promptsResults | Where-Object { $_.Status -eq "ADD" } | Select-Object @{N='Type';E={'Prompt'}}, File
$allToAdd += $scriptsResults | Where-Object { $_.Status -eq "ADD" } | Select-Object @{N='Type';E={'Script'}}, File

if ($allToAdd.Count -gt 0) {
    Write-Host "`n=== FILES TO ADD ($($allToAdd.Count)) ===" -ForegroundColor Red
    $allToAdd | Format-Table Type, File -AutoSize
}

# Show files that need to be updated
$allToUpdate = @()
$allToUpdate += $rulesResults | Where-Object { $_.Status -eq "UPDATE" } | Select-Object @{N='Type';E={'Rule'}}, File, SourceVersion, TargetVersion
$allToUpdate += $promptsResults | Where-Object { $_.Status -eq "UPDATE" } | Select-Object @{N='Type';E={'Prompt'}}, File, SourceHash, TargetHash
$allToUpdate += $scriptsResults | Where-Object { $_.Status -eq "UPDATE" } | Select-Object @{N='Type';E={'Script'}}, File, SourceHash, TargetHash

if ($allToUpdate.Count -gt 0) {
    Write-Host "`n=== FILES TO UPDATE ($($allToUpdate.Count)) ===" -ForegroundColor Yellow
    $allToUpdate | Format-Table -AutoSize
}

# ============================================================
# EXPORT TO CSV
# ============================================================

$outputDir = Split-Path $sourceRepo -Parent
$rulesResults | Export-Csv -Path "$outputDir\sync-analysis-rules-$targetRepoName.csv" -NoTypeInformation
$promptsResults | Export-Csv -Path "$outputDir\sync-analysis-prompts-$targetRepoName.csv" -NoTypeInformation
$scriptsResults | Export-Csv -Path "$outputDir\sync-analysis-scripts-$targetRepoName.csv" -NoTypeInformation

Write-Host "`nDetailed results exported to:" -ForegroundColor Green
Write-Host "  - $outputDir\sync-analysis-rules-$targetRepoName.csv" -ForegroundColor Gray
Write-Host "  - $outputDir\sync-analysis-prompts-$targetRepoName.csv" -ForegroundColor Gray
Write-Host "  - $outputDir\sync-analysis-scripts-$targetRepoName.csv" -ForegroundColor Gray
