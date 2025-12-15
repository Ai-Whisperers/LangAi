# Rule Sync Analysis Script
# Compares rule versions between two repositories
#
# Usage:
#   .\compare-rules.ps1 -SourceRepo "path\to\source" -TargetRepo "path\to\target"
#   .\compare-rules.ps1 -SourceRepo "E:\WPG\Git\E21\GitRepos\eneve.ebase.foundation" -TargetRepo "E:\WPG\Git\E21\GitRepos\eneve.domain"
#   .\compare-rules.ps1 -SourceRepo "E:\WPG\Git\E21\GitRepos\eneve.ebase.foundation" -TargetRepo "E:\WPG\Git\E21\GitRepos\eneve.ebase.datamigrator"
#
# Output:
#   - Console report with categorized rules (ADD, UPDATE, REVIEW, IN-SYNC)
#   - CSV file: rule-sync-analysis-[target-repo-name].csv
#
# Categories:
#   [A] Rules to ADD: Missing in target repository
#   [B] Rules to UPDATE: Source has newer version
#   [C] Rules to REVIEW: Conflicts or version issues
#   [D] Rules IN SYNC: Matching versions

param(
    [Parameter(Mandatory=$false, HelpMessage="Path to source repository")]
    [ValidateScript({Test-Path $_})]
    [string]$SourceRepo = "e:\WPG\Git\E21\GitRepos\eneve.ebase.foundation",
    
    [Parameter(Mandatory=$false, HelpMessage="Path to target repository")]
    [ValidateScript({Test-Path $_})]
    [string]$TargetRepo = "e:\WPG\Git\E21\GitRepos\eneve.domain",
    
    [Parameter(Mandatory=$false, HelpMessage="Path for output CSV file")]
    [string]$OutputPath = ""
)

# Normalize paths
$sourceRepo = $SourceRepo.TrimEnd('\')
$targetRepo = $TargetRepo.TrimEnd('\')

# Generate output path if not provided
if ([string]::IsNullOrEmpty($OutputPath)) {
    $targetRepoName = Split-Path $targetRepo -Leaf
    $OutputPath = Join-Path (Split-Path $sourceRepo -Parent) "rule-sync-analysis-$targetRepoName.csv"
}

$results = @()

# Get all rules from source
$sourceRules = Get-ChildItem -Path "$sourceRepo\.cursor\rules" -Recurse -Filter "*.mdc"

foreach ($sourceRule in $sourceRules) {
    # Calculate relative path correctly
    $sourceBase = "$sourceRepo\.cursor\rules\"
    $relativePath = $sourceRule.FullName.Substring($sourceBase.Length)
    $targetPath = Join-Path "$targetRepo\.cursor\rules" $relativePath
    
    # Extract front-matter from source
    $sourceContent = Get-Content $sourceRule.FullName -Raw
    if ($sourceContent -match '(?s)^---\s*\n(.*?)\n---') {
        $sourceFrontMatter = $matches[1]
        
        # Extract version from source
        if ($sourceFrontMatter -match 'version:\s*([^\s]+)') {
            $sourceVersion = $matches[1]
        } else {
            $sourceVersion = "N/A"
        }
        
        # Extract id from source
        if ($sourceFrontMatter -match 'id:\s*([^\s]+)') {
            $sourceId = $matches[1]
        } else {
            $sourceId = "N/A"
        }
        
        # Extract last_review from source
        if ($sourceFrontMatter -match 'last_review:\s*([^\s]+)') {
            $sourceLastReview = $matches[1]
        } else {
            $sourceLastReview = "N/A"
        }
    } else {
        $sourceVersion = "NO-FM"
        $sourceId = "NO-FM"
        $sourceLastReview = "NO-FM"
    }
    
    # Check if target exists
    if (Test-Path $targetPath) {
        # Extract front-matter from target
        $targetContent = Get-Content $targetPath -Raw
        if ($targetContent -match '(?s)^---\s*\n(.*?)\n---') {
            $targetFrontMatter = $matches[1]
            
            # Extract version from target
            if ($targetFrontMatter -match 'version:\s*([^\s]+)') {
                $targetVersion = $matches[1]
            } else {
                $targetVersion = "N/A"
            }
            
            # Extract last_review from target
            if ($targetFrontMatter -match 'last_review:\s*([^\s]+)') {
                $targetLastReview = $matches[1]
            } else {
                $targetLastReview = "N/A"
            }
        } else {
            $targetVersion = "NO-FM"
            $targetLastReview = "NO-FM"
        }
        
        # Compare versions
        if ($sourceVersion -eq $targetVersion) {
            $status = "IN-SYNC"
        } else {
            # Parse semantic versions
            $srcParts = $sourceVersion.Split('.')
            $tgtParts = $targetVersion.Split('.')
            
            if ($srcParts.Count -eq 3 -and $tgtParts.Count -eq 3) {
                $srcMajor = [int]$srcParts[0]
                $srcMinor = [int]$srcParts[1]
                $srcPatch = [int]$srcParts[2]
                $tgtMajor = [int]$tgtParts[0]
                $tgtMinor = [int]$tgtParts[1]
                $tgtPatch = [int]$tgtParts[2]
                
                if ($srcMajor -gt $tgtMajor -or 
                    ($srcMajor -eq $tgtMajor -and $srcMinor -gt $tgtMinor) -or 
                    ($srcMajor -eq $tgtMajor -and $srcMinor -eq $tgtMinor -and $srcPatch -gt $tgtPatch)) {
                    $status = "UPDATE"
                } elseif ($srcMajor -lt $tgtMajor -or 
                         ($srcMajor -eq $tgtMajor -and $srcMinor -lt $tgtMinor) -or 
                         ($srcMajor -eq $tgtMajor -and $srcMinor -eq $tgtMinor -and $srcPatch -lt $tgtPatch)) {
                    $status = "REVIEW-TARGET-NEWER"
                } else {
                    $status = "VERSION-MISMATCH"
                }
            } else {
                $status = "REVIEW"
            }
        }
    } else {
        $targetVersion = "MISSING"
        $targetLastReview = "MISSING"
        $status = "ADD"
    }
    
    $results += [PSCustomObject]@{
        Rule = $relativePath
        SourceId = $sourceId
        SourceVersion = $sourceVersion
        SourceLastReview = $sourceLastReview
        TargetVersion = $targetVersion
        TargetLastReview = $targetLastReview
        Status = $status
    }
}

# Output results grouped by status
Write-Host "`n=== SYNC ANALYSIS REPORT ===" -ForegroundColor Cyan
Write-Host "Source: $sourceRepo" -ForegroundColor Gray
Write-Host "Target: $targetRepo" -ForegroundColor Gray
Write-Host ""

$categoryA = $results | Where-Object { $_.Status -eq "ADD" }
$categoryB = $results | Where-Object { $_.Status -eq "UPDATE" }
$categoryC = $results | Where-Object { $_.Status -like "REVIEW*" -or $_.Status -eq "VERSION-MISMATCH" }
$categoryD = $results | Where-Object { $_.Status -eq "IN-SYNC" }

Write-Host "`n[Category A: Rules to ADD] ($($categoryA.Count) rules)" -ForegroundColor Green
$categoryA | Format-Table Rule, SourceVersion, SourceLastReview -AutoSize

Write-Host "`n[Category B: Rules to UPDATE] ($($categoryB.Count) rules)" -ForegroundColor Yellow
$categoryB | Format-Table Rule, SourceVersion, TargetVersion, SourceLastReview, TargetLastReview -AutoSize

Write-Host "`n[Category C: Rules to REVIEW] ($($categoryC.Count) rules)" -ForegroundColor Magenta
$categoryC | Format-Table Rule, SourceVersion, TargetVersion, Status -AutoSize

Write-Host "`n[Category D: Rules IN SYNC] ($($categoryD.Count) rules)" -ForegroundColor Gray
$categoryD | Select-Object -First 10 | Format-Table Rule, SourceVersion -AutoSize
if ($categoryD.Count -gt 10) {
    Write-Host "... and $($categoryD.Count - 10) more rules in sync" -ForegroundColor DarkGray
}

# Export full results to CSV
$results | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "`nFull results exported to: $OutputPath" -ForegroundColor Green

