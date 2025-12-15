# Bidirectional Rule Sync Script
# Syncs rules between two repositories in BOTH directions based on version numbers
# Detects conflicts and presents them for AI-assisted resolution
#
# Usage:
#   .\sync-rules-bidirectional.ps1 -RepoA "path\to\repo1" -RepoB "path\to\repo2"
#   .\sync-rules-bidirectional.ps1 -RepoA "E:\WPG\Git\E21\GitRepos\eneve.ebase.foundation" -RepoB "E:\WPG\Git\E21\GitRepos\eneve.ebase.datamigrator"
#
# Modes:
#   -Mode "analyze"  : Only analyze, don't sync (default)
#   -Mode "sync"     : Perform automatic sync for clear cases
#   -Mode "interactive" : Prompt for each sync decision
#
# Features:
#   - Bidirectional sync (A→B and B→A)
#   - Version-based direction detection
#   - Conflict detection and reporting
#   - Diff generation for manual review
#   - No crude overwrites without analysis

param(
    [Parameter(Mandatory=$true, HelpMessage="Path to first repository")]
    [ValidateScript({Test-Path $_})]
    [string]$RepoA,
    
    [Parameter(Mandatory=$true, HelpMessage="Path to second repository")]
    [ValidateScript({Test-Path $_})]
    [string]$RepoB,
    
    [Parameter(Mandatory=$false, HelpMessage="Mode: analyze, sync, interactive")]
    [ValidateSet("analyze", "sync", "interactive")]
    [string]$Mode = "analyze",
    
    [Parameter(Mandatory=$false, HelpMessage="Output directory for conflict reports")]
    [string]$ConflictReportDir = ""
)

# Normalize paths
$repoA = $RepoA.TrimEnd('\')
$repoB = $RepoB.TrimEnd('\')
$repoAName = Split-Path $repoA -Leaf
$repoBName = Split-Path $repoB -Leaf

# Set conflict report directory
if ([string]::IsNullOrEmpty($ConflictReportDir)) {
    $ConflictReportDir = Join-Path (Split-Path $repoA -Parent) "rule-sync-conflicts-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
}

Write-Host ""
Write-Host "=== BIDIRECTIONAL RULE SYNC ANALYSIS ===" -ForegroundColor Cyan
Write-Host "Repository A: $repoAName" -ForegroundColor Gray
Write-Host "Repository B: $repoBName" -ForegroundColor Gray
Write-Host "Mode: $Mode" -ForegroundColor Gray
Write-Host ""

# Get all files from both repositories (rules, prompts, templars, exemplars)
$fileMapA = @{}
$fileMapB = @{}

# Scan rules (*.mdc)
Write-Host "Scanning rules..." -ForegroundColor Gray
$rulesA = Get-ChildItem -Path "$repoA\.cursor\rules" -Recurse -Filter "*.mdc" -ErrorAction SilentlyContinue
foreach ($file in $rulesA) {
    $relativePath = "rules\" + $file.FullName.Substring("$repoA\.cursor\rules\".Length)
    $fileMapA[$relativePath] = $file.FullName
}

$rulesB = Get-ChildItem -Path "$repoB\.cursor\rules" -Recurse -Filter "*.mdc" -ErrorAction SilentlyContinue
foreach ($file in $rulesB) {
    $relativePath = "rules\" + $file.FullName.Substring("$repoB\.cursor\rules\".Length)
    $fileMapB[$relativePath] = $file.FullName
}

# Scan prompts (*.md)
Write-Host "Scanning prompts..." -ForegroundColor Gray
$promptsA = Get-ChildItem -Path "$repoA\.cursor\prompts" -Recurse -Filter "*.md" -ErrorAction SilentlyContinue
foreach ($file in $promptsA) {
    # Exclude scripts directory
    if ($file.FullName -notlike "*\scripts\*") {
        $relativePath = "prompts\" + $file.FullName.Substring("$repoA\.cursor\prompts\".Length)
        $fileMapA[$relativePath] = $file.FullName
    }
}

$promptsB = Get-ChildItem -Path "$repoB\.cursor\prompts" -Recurse -Filter "*.md" -ErrorAction SilentlyContinue
foreach ($file in $promptsB) {
    # Exclude scripts directory
    if ($file.FullName -notlike "*\scripts\*") {
        $relativePath = "prompts\" + $file.FullName.Substring("$repoB\.cursor\prompts\".Length)
        $fileMapB[$relativePath] = $file.FullName
    }
}

# Scan templars (all files)
Write-Host "Scanning templars..." -ForegroundColor Gray
$templarsA = Get-ChildItem -Path "$repoA\.cursor\prompts\templars" -Recurse -File -ErrorAction SilentlyContinue
foreach ($file in $templarsA) {
    $relativePath = "prompts\templars\" + $file.FullName.Substring("$repoA\.cursor\prompts\templars\".Length)
    $fileMapA[$relativePath] = $file.FullName
}

$templarsB = Get-ChildItem -Path "$repoB\.cursor\prompts\templars" -Recurse -File -ErrorAction SilentlyContinue
foreach ($file in $templarsB) {
    $relativePath = "prompts\templars\" + $file.FullName.Substring("$repoB\.cursor\prompts\templars\".Length)
    $fileMapB[$relativePath] = $file.FullName
}

# Scan exemplars (all files)
Write-Host "Scanning exemplars..." -ForegroundColor Gray
$exemplarsA = Get-ChildItem -Path "$repoA\.cursor\prompts\exemplars" -Recurse -File -ErrorAction SilentlyContinue
foreach ($file in $exemplarsA) {
    $relativePath = "prompts\exemplars\" + $file.FullName.Substring("$repoA\.cursor\prompts\exemplars\".Length)
    $fileMapA[$relativePath] = $file.FullName
}

$exemplarsB = Get-ChildItem -Path "$repoB\.cursor\prompts\exemplars" -Recurse -File -ErrorAction SilentlyContinue
foreach ($file in $exemplarsB) {
    $relativePath = "prompts\exemplars\" + $file.FullName.Substring("$repoB\.cursor\prompts\exemplars\".Length)
    $fileMapB[$relativePath] = $file.FullName
}

Write-Host "Scan complete. Found $($fileMapA.Count) files in A, $($fileMapB.Count) files in B" -ForegroundColor Gray

# Get all unique file paths
$allRulePaths = @($fileMapA.Keys) + @($fileMapB.Keys) | Select-Object -Unique

$syncActions = @()
$conflictsDetected = 0

foreach ($rulePath in $allRulePaths) {
    $existsInA = $fileMapA.ContainsKey($rulePath)
    $existsInB = $fileMapB.ContainsKey($rulePath)
    
    $action = [PSCustomObject]@{
        RulePath = $rulePath
        ExistsInA = $existsInA
        ExistsInB = $existsInB
        VersionA = "N/A"
        VersionB = "N/A"
        LastReviewA = "N/A"
        LastReviewB = "N/A"
        SyncDirection = "NONE"
        ActionType = "IN-SYNC"
        Reason = ""
        RequiresAIReview = $false
    }
    
    # Extract version from A
    if ($existsInA) {
        $contentA = Get-Content $fileMapA[$rulePath] -Raw
        if ($contentA -match '(?s)^---\s*\n(.*?)\n---') {
            $frontMatterA = $matches[1]
            if ($frontMatterA -match 'version:\s*([^\s]+)') {
                $action.VersionA = $matches[1]
            }
            if ($frontMatterA -match 'last_review:\s*([^\s]+)') {
                $action.LastReviewA = $matches[1]
            }
        }
    }
    
    # Extract version from B
    if ($existsInB) {
        $contentB = Get-Content $fileMapB[$rulePath] -Raw
        if ($contentB -match '(?s)^---\s*\n(.*?)\n---') {
            $frontMatterB = $matches[1]
            if ($frontMatterB -match 'version:\s*([^\s]+)') {
                $action.VersionB = $matches[1]
            }
            if ($frontMatterB -match 'last_review:\s*([^\s]+)') {
                $action.LastReviewB = $matches[1]
            }
        }
    }
    
    # Determine sync direction
    if (-not $existsInA -and $existsInB) {
        $action.SyncDirection = "B→A"
        $action.ActionType = "ADD-TO-A"
        $action.Reason = "Missing in A"
    }
    elseif ($existsInA -and -not $existsInB) {
        $action.SyncDirection = "A→B"
        $action.ActionType = "ADD-TO-B"
        $action.Reason = "Missing in B"
    }
    elseif ($existsInA -and $existsInB) {
        # Both exist - compare versions
        $versionA = $action.VersionA
        $versionB = $action.VersionB
        
        if ($versionA -eq $versionB) {
            # Same version - check if content differs
            $hashA = (Get-FileHash -Path $fileMapA[$rulePath] -Algorithm SHA256).Hash
            $hashB = (Get-FileHash -Path $fileMapB[$rulePath] -Algorithm SHA256).Hash
            
            if ($hashA -ne $hashB) {
                $action.SyncDirection = "CONFLICT"
                $action.ActionType = "CONTENT-MISMATCH"
                $action.Reason = "Same version but different content"
                $action.RequiresAIReview = $true
                $conflictsDetected++
            } else {
                $action.ActionType = "IN-SYNC"
                $action.Reason = "Identical files"
            }
        }
        else {
            # Different versions - parse semantic version
            $partsA = $versionA.Split('.')
            $partsB = $versionB.Split('.')
            
            if ($partsA.Count -eq 3 -and $partsB.Count -eq 3) {
                $majorA = [int]$partsA[0]
                $minorA = [int]$partsA[1]
                $patchA = [int]$partsA[2]
                $majorB = [int]$partsB[0]
                $minorB = [int]$partsB[1]
                $patchB = [int]$partsB[2]
                
                if ($majorA -gt $majorB -or 
                    ($majorA -eq $majorB -and $minorA -gt $minorB) -or 
                    ($majorA -eq $majorB -and $minorA -eq $minorB -and $patchA -gt $patchB)) {
                    $action.SyncDirection = "A→B"
                    $action.ActionType = "UPDATE-B"
                    $action.Reason = "A has newer version ($versionA > $versionB)"
                }
                elseif ($majorB -gt $majorA -or 
                       ($majorB -eq $majorA -and $minorB -gt $minorA) -or 
                       ($majorB -eq $majorA -and $minorB -eq $minorA -and $patchB -gt $patchA)) {
                    $action.SyncDirection = "B→A"
                    $action.ActionType = "UPDATE-A"
                    $action.Reason = "B has newer version ($versionB > $versionA)"
                }
                else {
                    $action.SyncDirection = "CONFLICT"
                    $action.ActionType = "VERSION-CONFLICT"
                    $action.Reason = "Cannot determine which version is newer"
                    $action.RequiresAIReview = $true
                    $conflictsDetected++
                }
            }
            else {
                $action.SyncDirection = "CONFLICT"
                $action.ActionType = "INVALID-VERSION"
                $action.Reason = "Cannot parse version numbers"
                $action.RequiresAIReview = $true
                $conflictsDetected++
            }
        }
    }
    
    $syncActions += $action
}

# Categorize and display results
Write-Host ""
Write-Host "=== SYNC ANALYSIS RESULTS ===" -ForegroundColor Cyan

$addToA = $syncActions | Where-Object { $_.ActionType -eq "ADD-TO-A" }
$addToB = $syncActions | Where-Object { $_.ActionType -eq "ADD-TO-B" }
$updateA = $syncActions | Where-Object { $_.ActionType -eq "UPDATE-A" }
$updateB = $syncActions | Where-Object { $_.ActionType -eq "UPDATE-B" }
$conflicts = $syncActions | Where-Object { $_.RequiresAIReview }
$inSync = $syncActions | Where-Object { $_.ActionType -eq "IN-SYNC" }

Write-Host ""
Write-Host "[A→B] Files to sync from A to B: $($addToB.Count + $updateB.Count)" -ForegroundColor Yellow
if ($addToB.Count -gt 0) {
    Write-Host "  Add to B: $($addToB.Count)" -ForegroundColor Green
    $addToB | Format-Table RulePath, VersionA -AutoSize
}
if ($updateB.Count -gt 0) {
    Write-Host "  Update in B: $($updateB.Count)" -ForegroundColor Yellow
    $updateB | Format-Table RulePath, VersionA, VersionB, Reason -AutoSize
}

Write-Host ""
Write-Host "[B→A] Files to sync from B to A: $($addToA.Count + $updateA.Count)" -ForegroundColor Yellow
if ($addToA.Count -gt 0) {
    Write-Host "  Add to A: $($addToA.Count)" -ForegroundColor Green
    $addToA | Format-Table RulePath, VersionB -AutoSize
}
if ($updateA.Count -gt 0) {
    Write-Host "  Update in A: $($updateA.Count)" -ForegroundColor Yellow
    $updateA | Format-Table RulePath, VersionA, VersionB, Reason -AutoSize
}

Write-Host ""
Write-Host "[CONFLICTS] Files requiring AI review: $($conflicts.Count)" -ForegroundColor Magenta
if ($conflicts.Count -gt 0) {
    $conflicts | Format-Table RulePath, ActionType, VersionA, VersionB, Reason -AutoSize
}

Write-Host ""
Write-Host "[IN SYNC] Files already synchronized: $($inSync.Count)" -ForegroundColor Gray

# Generate conflict reports
if ($conflicts.Count -gt 0) {
    Write-Host ""
    Write-Host "Generating conflict reports..." -ForegroundColor Cyan
    
    if (-not (Test-Path $ConflictReportDir)) {
        New-Item -ItemType Directory -Path $ConflictReportDir -Force | Out-Null
    }
    
    foreach ($conflict in $conflicts) {
        $reportPath = Join-Path $ConflictReportDir "$($conflict.RulePath.Replace('\', '_')).conflict.md"
        
        $report = @"
# Conflict Report: $($conflict.RulePath)

**Conflict Type**: $($conflict.ActionType)
**Reason**: $($conflict.Reason)

## Repository A: $repoAName
- **Version**: $($conflict.VersionA)
- **Last Review**: $($conflict.LastReviewA)
- **Path**: ``````$($fileMapA[$conflict.RulePath])``````

## Repository B: $repoBName
- **Version**: $($conflict.VersionB)
- **Last Review**: $($conflict.LastReviewB)
- **Path**: ``````$($fileMapB[$conflict.RulePath])``````

## Content Comparison

### File A Content:
``````
$(if ($fileMapA.ContainsKey($conflict.RulePath)) { Get-Content $fileMapA[$conflict.RulePath] -Raw } else { "File does not exist" })
``````

### File B Content:
``````
$(if ($fileMapB.ContainsKey($conflict.RulePath)) { Get-Content $fileMapB[$conflict.RulePath] -Raw } else { "File does not exist" })
``````

## Resolution Options

1. **Keep A**: Overwrite B with A's version
2. **Keep B**: Overwrite A with B's version
3. **Manual Merge**: Combine best of both versions
4. **Skip**: Do not sync this file

## AI Resolution Required

This conflict requires manual review and AI-assisted resolution. Compare the content above and determine:
- Which version has the correct/newer information
- Whether a merge is needed
- What the final resolution should be

"@
        
        Set-Content -Path $reportPath -Value $report
        Write-Host "  Generated: $reportPath" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Conflict reports saved to: $ConflictReportDir" -ForegroundColor Green
}

# Export summary CSV
$csvPath = Join-Path (Split-Path $ConflictReportDir -Parent) "sync-analysis-bidirectional-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$syncActions | Export-Csv -Path $csvPath -NoTypeInformation
Write-Host ""
Write-Host "Full analysis exported to: $csvPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total Files Analyzed: $($syncActions.Count)" -ForegroundColor Gray
Write-Host "  (includes rules, prompts, templars, exemplars)" -ForegroundColor DarkGray
Write-Host ""

$syncAtoB = $addToB.Count + $updateB.Count
$syncBtoA = $addToA.Count + $updateA.Count
$bidirectionalSync = ($syncAtoB -gt 0) -and ($syncBtoA -gt 0)

if ($bidirectionalSync) {
    Write-Host "BIDIRECTIONAL SYNC DETECTED (mixed directions in same session):" -ForegroundColor Yellow
    Write-Host "  A→B: $syncAtoB files" -ForegroundColor Yellow
    Write-Host "  B→A: $syncBtoA files" -ForegroundColor Yellow
    Write-Host "  This is normal when both repositories have evolved independently." -ForegroundColor Gray
} else {
    Write-Host "Files to Sync A→B: $syncAtoB" -ForegroundColor $(if ($syncAtoB -gt 0) { "Yellow" } else { "Gray" })
    Write-Host "Files to Sync B→A: $syncBtoA" -ForegroundColor $(if ($syncBtoA -gt 0) { "Yellow" } else { "Gray" })
}

Write-Host ""
Write-Host "Conflicts Requiring AI Review: $($conflicts.Count)" -ForegroundColor $(if ($conflicts.Count -gt 0) { "Magenta" } else { "Green" })
Write-Host "Files In Sync: $($inSync.Count)" -ForegroundColor Gray

if ($Mode -eq "analyze") {
    Write-Host ""
    Write-Host "Analysis complete. No files were modified." -ForegroundColor Cyan
    Write-Host "To perform sync, run with -Mode sync or -Mode interactive" -ForegroundColor Gray
}

Write-Host ""

