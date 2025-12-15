# Complete Sync Validation Script
# Validates that all rules AND prompts are synced between repositories
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File validate-complete-sync.ps1
#   .\validate-complete-sync.ps1 -SourceRepo "path\to\source" -TargetRepo "path\to\target"
#   .\validate-complete-sync.ps1 -RulesMask "*.mdc" -PromptsMask "*.md" -ScriptsMask "*.ps1"
#
# Validates:
#   - All rule files in source exist in target
#   - All prompt files in source exist in target
#   - All script files in source exist in target
#   - Reports missing files and sync status

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

Write-Host "`n=== COMPLETE SYNC VALIDATION REPORT ===" -ForegroundColor Cyan
Write-Host "Source: $SourceRepo" -ForegroundColor Gray
Write-Host "Target: $TargetRepo" -ForegroundColor Gray
Write-Host "Rules Mask: $RulesMask" -ForegroundColor DarkGray
Write-Host "Prompts Mask: $PromptsMask" -ForegroundColor DarkGray
Write-Host "Scripts Mask: $ScriptsMask`n" -ForegroundColor DarkGray

$allValid = $true

# ======================================
# PART 1: Validate Rules
# ======================================
Write-Host "=== VALIDATING RULES ($RulesMask files) ===" -ForegroundColor Yellow

$sourceRulesPath = Join-Path $SourceRepo $RulesPath
$targetRulesPath = Join-Path $TargetRepo $RulesPath

if (Test-Path $sourceRulesPath) {
    $sourceRules = Get-ChildItem -Path $sourceRulesPath -Recurse -Filter $RulesMask | 
        ForEach-Object { $_.FullName.Replace($sourceRulesPath, "").TrimStart('\') }

    $targetRules = Get-ChildItem -Path $targetRulesPath -Recurse -Filter $RulesMask -ErrorAction SilentlyContinue | 
        ForEach-Object { $_.FullName.Replace($targetRulesPath, "").TrimStart('\') }

    $missingRules = $sourceRules | Where-Object { $_ -notin $targetRules }
    $extraRules = $targetRules | Where-Object { $_ -notin $sourceRules }

    Write-Host "Source Rules: $($sourceRules.Count)" -ForegroundColor Gray
    Write-Host "Target Rules: $($targetRules.Count)" -ForegroundColor Gray

    if ($missingRules.Count -eq 0) {
        Write-Host "[PASS] All rules present in target" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing $($missingRules.Count) rules in target:" -ForegroundColor Red
        $missingRules | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        $allValid = $false
    }

    if ($extraRules.Count -gt 0) {
        Write-Host "[INFO] $($extraRules.Count) extra rules in target (not in source):" -ForegroundColor Yellow
        $extraRules | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
} else {
    Write-Host "[WARN] Source rules path not found: $sourceRulesPath" -ForegroundColor Yellow
    $sourceRules = @()
    $missingRules = @()
}

# ======================================
# PART 2: Validate Prompts
# ======================================
Write-Host "`n=== VALIDATING PROMPTS ($PromptsMask files) ===" -ForegroundColor Yellow

$sourcePromptsPath = Join-Path $SourceRepo $PromptsPath
$targetPromptsPath = Join-Path $TargetRepo $PromptsPath

if (Test-Path $sourcePromptsPath) {
    # Get all prompt files from source
    $sourcePrompts = Get-ChildItem -Path $sourcePromptsPath -Recurse -Filter $PromptsMask | 
        ForEach-Object { $_.FullName.Replace($sourcePromptsPath, "").TrimStart('\') }

    # Get all prompt files from target
    $targetPrompts = Get-ChildItem -Path $targetPromptsPath -Recurse -Filter $PromptsMask -ErrorAction SilentlyContinue | 
        ForEach-Object { $_.FullName.Replace($targetPromptsPath, "").TrimStart('\') }

    $missingPrompts = $sourcePrompts | Where-Object { $_ -notin $targetPrompts }
    $extraPrompts = $targetPrompts | Where-Object { $_ -notin $sourcePrompts }

    Write-Host "Source Prompts: $($sourcePrompts.Count)" -ForegroundColor Gray
    Write-Host "Target Prompts: $($targetPrompts.Count)" -ForegroundColor Gray

    if ($missingPrompts.Count -eq 0) {
        Write-Host "[PASS] All prompts present in target" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing $($missingPrompts.Count) prompts in target:" -ForegroundColor Red
        $missingPrompts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        $allValid = $false
    }

    if ($extraPrompts.Count -gt 0) {
        Write-Host "[INFO] $($extraPrompts.Count) extra prompts in target (not in source):" -ForegroundColor Yellow
        $extraPrompts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
} else {
    Write-Host "[WARN] Source prompts path not found: $sourcePromptsPath" -ForegroundColor Yellow
    $sourcePrompts = @()
    $missingPrompts = @()
}

# ======================================
# PART 3: Validate Scripts
# ======================================
Write-Host "`n=== VALIDATING SCRIPTS ($ScriptsMask files) ===" -ForegroundColor Yellow

# Scripts are in prompts folder by default
$sourceScriptsPath = Join-Path $SourceRepo $PromptsPath
$targetScriptsPath = Join-Path $TargetRepo $PromptsPath

if (Test-Path $sourceScriptsPath) {
    # Get all script files from source
    $sourceScripts = Get-ChildItem -Path $sourceScriptsPath -Recurse -Filter $ScriptsMask | 
        ForEach-Object { $_.FullName.Replace($sourceScriptsPath, "").TrimStart('\') }

    # Get all script files from target
    $targetScripts = Get-ChildItem -Path $targetScriptsPath -Recurse -Filter $ScriptsMask -ErrorAction SilentlyContinue | 
        ForEach-Object { $_.FullName.Replace($targetScriptsPath, "").TrimStart('\') }

    $missingScripts = $sourceScripts | Where-Object { $_ -notin $targetScripts }
    $extraScripts = $targetScripts | Where-Object { $_ -notin $sourceScripts }

    Write-Host "Source Scripts: $($sourceScripts.Count)" -ForegroundColor Gray
    Write-Host "Target Scripts: $($targetScripts.Count)" -ForegroundColor Gray

    if ($missingScripts.Count -eq 0) {
        Write-Host "[PASS] All scripts present in target" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing $($missingScripts.Count) scripts in target:" -ForegroundColor Red
        $missingScripts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        $allValid = $false
    }

    if ($extraScripts.Count -gt 0) {
        Write-Host "[INFO] $($extraScripts.Count) extra scripts in target (not in source):" -ForegroundColor Yellow
        $extraScripts | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
} else {
    Write-Host "[WARN] Source scripts path not found: $sourceScriptsPath" -ForegroundColor Yellow
    $sourceScripts = @()
    $missingScripts = @()
}

# ======================================
# FINAL SUMMARY
# ======================================
Write-Host "`n=== FINAL VALIDATION SUMMARY ===" -ForegroundColor Cyan

$summary = @"

RULES ($RulesMask):
  Source: $($sourceRules.Count) files
  Target: $($targetRules.Count) files
  Missing: $($missingRules.Count) files
  Status: $(if ($missingRules.Count -eq 0) { "✅ SYNCED" } else { "❌ NOT SYNCED" })

PROMPTS ($PromptsMask):
  Source: $($sourcePrompts.Count) files
  Target: $($targetPrompts.Count) files
  Missing: $($missingPrompts.Count) files
  Status: $(if ($missingPrompts.Count -eq 0) { "✅ SYNCED" } else { "❌ NOT SYNCED" })

SCRIPTS ($ScriptsMask):
  Source: $($sourceScripts.Count) files
  Target: $($targetScripts.Count) files
  Missing: $($missingScripts.Count) files
  Status: $(if ($missingScripts.Count -eq 0) { "✅ SYNCED" } else { "❌ NOT SYNCED" })

"@

Write-Host $summary

if ($allValid) {
    Write-Host "[PASS] ✅ REPOSITORIES FULLY SYNCHRONIZED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[FAIL] ❌ SYNC INCOMPLETE - See missing files above" -ForegroundColor Red
    exit 1
}
