<#
.SYNOPSIS
    {{SCRIPT_PURPOSE}}

.DESCRIPTION
    {{SCRIPT_DESCRIPTION}}

.PARAMETER Configuration
    Build configuration to use (Debug or Release). Default: Release

.PARAMETER {{PARAMETER_NAME}}
    {{PARAMETER_DESCRIPTION}}

.EXAMPLE
    .\{{SCRIPT_NAME}}.ps1

    Runs with default settings

.EXAMPLE
    .\{{SCRIPT_NAME}}.ps1 -Configuration Debug -{{PARAMETER_NAME}} "{{PARAMETER_VALUE}}"

    Runs with custom configuration and parameters

.NOTES
    File Name      : {{SCRIPT_NAME}}.ps1
    Author         : {{AUTHOR}}
    Prerequisite   : {{PREREQUISITES}}

.LINK
    {{DOCUMENTATION_URL}}
#>

param(
    [Parameter(Mandatory=$false, HelpMessage="Build configuration (Debug or Release)")]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter(Mandatory=$false, HelpMessage="{{PARAMETER_DESCRIPTION}}")]
    [ValidateSet("{{VALID_VALUE_1}}", "{{VALID_VALUE_2}}")]
    [string]${{PARAMETER_NAME}} = "{{PARAMETER_DEFAULT}}"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== {{SCRIPT_NAME}} ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration: $Configuration"
Write-Host "{{PARAMETER_NAME}}: ${{PARAMETER_NAME}}"
Write-Host ""

try {
    # ======================================
    # Main script logic here
    # ======================================

    Write-Host "Processing..." -ForegroundColor Yellow

    # TODO: Replace with actual logic

    Write-Host ""
    Write-Host "✅ Script completed successfully!" -ForegroundColor Green
    Write-Host ""
    exit 0
}
catch {
    Write-Host "##vso[task.logissue type=error]$($_.Exception.Message)"
    Write-Host "❌ Script failed. See error above." -ForegroundColor Red
    Write-Host ""
    exit 1
}
