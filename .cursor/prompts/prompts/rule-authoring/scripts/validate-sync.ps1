# Rule Sync Validation Script
# Validates that all synced rules exist and have correct front-matter
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File validate-sync.ps1
#
# Validates:
#   - File existence in target repository
#   - Front-matter presence and validity
#   - Version numbers match expected values
#   - Total rule count matches expected (100 rules)

$targetRepo = "e:\WPG\Git\E21\GitRepos\eneve.domain"

Write-Host "`n=== SYNC VALIDATION REPORT ===" -ForegroundColor Cyan
Write-Host "Target: $targetRepo`n" -ForegroundColor Gray

$syncedRules = @(
    "prompts\agent-application-rule.mdc",
    "prompts\prompt-creation-rule.mdc",
    "prompts\prompt-extraction-rule.mdc",
    "prompts\prompts-rules-index.mdc",
    "rule-authoring\rule-sync-rule.mdc",
    "rule-authoring\agent-application-rule.mdc"
)

$expectedVersions = @{
    "prompts\agent-application-rule.mdc" = "1.0.0"
    "prompts\prompt-creation-rule.mdc" = "1.0.0"
    "prompts\prompt-extraction-rule.mdc" = "1.0.0"
    "prompts\prompts-rules-index.mdc" = "1.0.0"
    "rule-authoring\rule-sync-rule.mdc" = "1.0.0"
    "rule-authoring\agent-application-rule.mdc" = "1.1.0"
}

$allValid = $true
$validationResults = @()

foreach ($rule in $syncedRules) {
    $rulePath = Join-Path "$targetRepo\.cursor\rules" $rule
    $result = [PSCustomObject]@{
        Rule = $rule
        Exists = $false
        HasFrontMatter = $false
        Version = "N/A"
        ExpectedVersion = $expectedVersions[$rule]
        VersionMatch = $false
        Status = "FAIL"
    }

    # Check if file exists
    if (Test-Path $rulePath) {
        $result.Exists = $true

        # Read content and check front-matter
        $content = Get-Content $rulePath -Raw
        if ($content -match '(?s)^---\s*\n(.*?)\n---') {
            $result.HasFrontMatter = $true
            $frontMatter = $matches[1]

            # Extract version
            if ($frontMatter -match 'version:\s*([^\s]+)') {
                $result.Version = $matches[1]

                # Check version match
                if ($result.Version -eq $result.ExpectedVersion) {
                    $result.VersionMatch = $true
                    $result.Status = "VALID"
                } else {
                    $result.Status = "VERSION MISMATCH"
                    $allValid = $false
                }
            } else {
                $result.Status = "NO VERSION"
                $allValid = $false
            }
        } else {
            $result.Status = "NO FRONT-MATTER"
            $allValid = $false
        }
    } else {
        $result.Status = "FILE MISSING"
        $allValid = $false
    }

    $validationResults += $result
}

# Display results
$validationResults | Format-Table Rule, Status, Version, ExpectedVersion -AutoSize

# Summary
Write-Host "`n=== VALIDATION SUMMARY ===" -ForegroundColor Cyan
$validCount = ($validationResults | Where-Object { $_.Status -eq "VALID" }).Count
$totalCount = $validationResults.Count

Write-Host "Total Rules Validated: $totalCount" -ForegroundColor Gray
Write-Host "Valid Rules: $validCount" -ForegroundColor Green
Write-Host "Failed Rules: $($totalCount - $validCount)" -ForegroundColor $(if ($validCount -eq $totalCount) { "Green" } else { "Red" })

if ($allValid) {
    Write-Host "`n[PASS] ALL RULES VALIDATED SUCCESSFULLY" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] VALIDATION FAILED - Some rules have issues" -ForegroundColor Red
}

# Count total rules in target
$totalRulesCount = (Get-ChildItem -Path "$targetRepo\.cursor\rules" -Recurse -Filter "*.mdc").Count
Write-Host "`nTotal Rules in Target Repository: $totalRulesCount" -ForegroundColor Gray
Write-Host "Expected: 100 rules" -ForegroundColor Gray
if ($totalRulesCount -eq 100) {
    Write-Host "[PASS] Rule count matches expected value" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[WARN] Rule count mismatch (expected 100, found $totalRulesCount)" -ForegroundColor Yellow
    exit 1
}
