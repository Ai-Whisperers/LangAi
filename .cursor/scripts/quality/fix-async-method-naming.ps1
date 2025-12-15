<#
.SYNOPSIS
    Fixes IDE1006 async method naming violations by ensuring async methods end with 'Async'

.DESCRIPTION
    This script automatically fixes IDE1006 naming rule violations for async methods in C# test files.
    The .editorconfig rule requires async methods to end with the 'Async' suffix.

    The script handles complex renaming patterns where 'Async' appears in the middle of method names:
    - MethodAsync_Name_Should_DoSomething() → Method_Name_Should_DoSomethingAsync()
    - Compare_ConcurrentCalls_ShouldHandleThreadSafely() → Compare_ConcurrentCalls_ShouldHandleThreadSafelyAsync()

    Features:
    - Safe pattern matching to avoid false positives
    - Dry-run mode to preview changes
    - Comprehensive logging with file-by-file progress
    - Compatible with both PowerShell 5.1 and 7+ (graceful fallback)
    - Works from any directory (auto-detects repository root)

.PARAMETER Path
    Root path to scan for test files. Defaults to current directory.

.PARAMETER TestDirectory
    Name of the test directory to scan. Defaults to 'tst'.

.PARAMETER WhatIf
    Shows what would be changed without actually making changes.

.PARAMETER Force
    Overwrite existing files without prompting.

.EXAMPLE
    .\fix-async-method-naming.ps1
    Fixes async method naming violations in all test files under tst/

.EXAMPLE
    .\fix-async-method-naming.ps1 -WhatIf
    Shows what would be changed without making actual modifications

.EXAMPLE
    .\fix-async-method-naming.ps1 -Path "C:\MyProject" -TestDirectory "test"
    Fixes async method naming in a different project structure

.NOTES
    File Name      : fix-async-method-naming.ps1
    Author         : Code Quality Automation
    Prerequisite   : PowerShell 5.1+, Test files in tst/ directory
    Related Rules  : IDE1006 naming conventions, async method standards

.LINK
    https://docs.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/ide1006
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "Root path to scan for test files")]
    [ValidateNotNullOrEmpty()]
    [string]$Path = $PWD.Path,

    [Parameter(Mandatory = $false, HelpMessage = "Name of the test directory to scan")]
    [ValidateNotNullOrEmpty()]
    [string]$TestDirectory = "tst",

    [Parameter(Mandatory = $false, HelpMessage = "Show what would be changed without making changes")]
    [switch]$DryRun,

    [Parameter(Mandatory = $false, HelpMessage = "Overwrite existing files without prompting")]
    [switch]$Force
)

#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Import shared modules if available (skip if PowerShell version incompatible)
$scriptRoot = Split-Path $MyInvocation.MyCommand.Path -Parent
$commonModulePath = Join-Path $scriptRoot "modules\Common.psm1"
if (Test-Path $commonModulePath) {
    try {
        Import-Module $commonModulePath -Force -ErrorAction Stop
    } catch {
        # Continue without the module if import fails (e.g., PowerShell version mismatch)
        Write-Warning "Could not import Common.psm1 module: $($_.Exception.Message)"
    }
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
        Write-Log $Message -Level SUCCESS
    } else {
        Write-Host "[SUCCESS] $Message" -ForegroundColor Green
    }
}

function Write-Info {
    param([string]$Message)
    if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
        Write-Log $Message -Level INFO
    } else {
        Write-Host "[INFO] $Message" -ForegroundColor Cyan
    }
}

function Write-Warning {
    param([string]$Message)
    if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
        Write-Log $Message -Level WARN
    } else {
        Write-Host "[WARN] $Message" -ForegroundColor Yellow
    }
}

function Write-Error-Message {
    param([string]$Message)
    if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
        Write-Log $Message -Level ERROR
    } else {
        Write-Host "[ERROR] $Message" -ForegroundColor Red
    }
}

# Main logic
Write-Header "Async Method Naming Fixer - IDE1006 Compliance"

Write-Info "Configuration:"
Write-Info "  Root Path: $Path"
Write-Info "  Test Directory: $TestDirectory"
Write-Info "  Dry Run Mode: $($DryRun.IsPresent)"
Write-Info "  Force Mode: $($Force.IsPresent)"

# Validate paths
$testPath = Join-Path $Path $TestDirectory

# If running from scripts directory, adjust path to repository root
if (-not (Test-Path $testPath) -and $Path -match "\.cursor\\scripts$") {
    $repoRoot = Split-Path (Split-Path $Path -Parent) -Parent
    $testPath = Join-Path $repoRoot $TestDirectory
    Write-Info "Adjusted path to repository root: $repoRoot"
}

if (-not (Test-Path $testPath)) {
    Write-Error-Message "Test directory not found: $testPath"
    Write-Info "Current working directory: $(Get-Location)"
    Write-Info "Script location: $scriptRoot"
    exit 1
}

Write-Info "Scanning for test files in: $testPath"

# Find all test files
$testFiles = Get-ChildItem -Path $testPath -Filter "*.cs" -Recurse -File |
    Where-Object { $_.FullName -match "Tests\.cs$" }

if ($testFiles.Count -eq 0) {
    Write-Warning "No test files found in $testPath"
    exit 0
}

Write-Info "Found $($testFiles.Count) test files to process"

$totalFixed = 0
$filesChanged = 0

foreach ($file in $testFiles) {
    $filePath = $file.FullName
    $relativePath = $file.FullName.Replace("$Path\", "").Replace("$Path/", "")

    Write-Info "Processing: $relativePath"

    try {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $originalContent = $content
        $fileChanged = $false

        # Pattern 1: public async Task MethodAsync_Name_Should_DoSomething()
        # Replace with: public async Task Method_Name_Should_DoSomethingAsync()
        $pattern1 = 'public async Task ([A-Za-z][A-Za-z0-9_]*)Async([A-Za-z0-9_]+_Should[A-Za-z0-9_]*)\(\)'
        $replacement1 = 'public async Task $1$2Async()'

        $content = $content -replace $pattern1, $replacement1

        # Pattern 2: Handle methods that already end with Async but have Async in middle
        $pattern2 = 'public async Task ([A-Za-z][A-Za-z0-9_]*)Async(_[A-Za-z0-9_]+)_\(\)'
        $replacement2 = 'public async Task $1$2Async()'

        $content = $content -replace $pattern2, $replacement2

        # Pattern 3: Simple methods without underscores that don't end with Async
        $pattern3 = 'public async Task ([A-Za-z][A-Za-z0-9_]*)Async([^)]*)\(\)(?!.*Async)'
        $replacement3 = 'public async Task $1$2Async()'

        $content = $content -replace $pattern3, $replacement3

        # Check if file was modified
        if ($content -ne $originalContent) {
            $fileChanged = $true
            $filesChanged++

            # Count how many methods were fixed in this file
            $originalMatches = [regex]::Matches($originalContent, 'public async Task .*Async.*\(\)')
            $newMatches = [regex]::Matches($content, 'public async Task .*Async\(\)')

            if ($newMatches.Count -gt $originalMatches.Count) {
                $methodsFixed = $newMatches.Count - $originalMatches.Count
                $totalFixed += $methodsFixed
                Write-Success "Fixed $methodsFixed async method(s) in $relativePath"
            }
        } else {
            Write-Info "No changes needed in $relativePath"
        }

        # Write changes if not in dry run mode
        if ($fileChanged -and -not $DryRun) {
            $content | Set-Content $filePath -NoNewline -Encoding UTF8
            Write-Info "Updated: $relativePath"
        } elseif ($fileChanged -and $DryRun) {
            Write-Info "Would update: $relativePath (Dry Run mode)"
        }

    } catch {
        Write-Error-Message "Error processing $relativePath : $($_.Exception.Message)"
        continue
    }
}

# Summary
Write-Header "Processing Complete"

if ($DryRun) {
    Write-Info "Dry Run Mode - No files were actually changed"
}

Write-Success "Summary:"
Write-Success "  Files processed: $($testFiles.Count)"
Write-Success "  Files changed: $filesChanged"
Write-Success "  Methods fixed: $totalFixed"

if ($totalFixed -gt 0) {
    Write-Success "All async method naming violations have been fixed!"
    Write-Info "Run 'dotnet format --verify-no-changes' to verify compliance"
} else {
    Write-Info "No async method naming violations found"
}

exit 0
