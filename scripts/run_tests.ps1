#Requires -Version 7.2
#Requires -PSEdition Core

<#
.SYNOPSIS
Runs the Company Researcher test suite from the repository root.

.DESCRIPTION
This script exists to make test execution consistent on Windows/PowerShell:
- Always runs from the repo root (avoids accidentally collecting tests from other folders).
- Uses the repo's pytest configuration (`pytest.ini`).

.PARAMETER Suite
Which suite to run:
  - all: tests/
  - unit: tests/unit/
  - integration: tests/integration/

.PARAMETER Coverage
If set, enables coverage reporting for src/company_researcher.

.PARAMETER Marker
Optional pytest marker expression (e.g. "not slow", "unit", "requires_api").

.PARAMETER PytestArgs
Additional arguments forwarded to pytest.

.EXAMPLE
.\scripts\run_tests.ps1

.EXAMPLE
.\scripts\run_tests.ps1 -Suite unit -Coverage

.EXAMPLE
.\scripts\run_tests.ps1 -Marker "not slow"
#>
[CmdletBinding()]
param(
    [ValidateSet('all', 'unit', 'integration')]
    [string]$Suite = 'all',
    [switch]$Coverage,
    [string]$Marker,
    [string[]]$PytestArgs = @()
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

Push-Location $repoRoot
try {
    $target = switch ($Suite) {
        'unit' { 'tests/unit' }
        'integration' { 'tests/integration' }
        default { 'tests' }
    }

    $args = @('-m', 'pytest', $target)

    if ($Coverage) {
        # Keep coverage artifacts out of the repo root to avoid corrupted/locked `.coverage` files on Windows.
        $coverageDir = Join-Path $repoRoot ".cache\coverage"
        New-Item -ItemType Directory -Force -Path $coverageDir | Out-Null
        $env:COVERAGE_FILE = (Join-Path $coverageDir ".coverage")

        $args += @(
            '--cov=src/company_researcher',
            '--cov-branch',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml'
        )
    }

    if ($Marker) {
        $args += @('-m', $Marker)
    }

    if ($PytestArgs.Count -gt 0) {
        $args += $PytestArgs
    }

    Write-Host ("Running: python " + ($args -join ' '))
    & python @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
