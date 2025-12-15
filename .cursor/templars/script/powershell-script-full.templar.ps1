<#
.SYNOPSIS
    {{SCRIPT_PURPOSE}}

.DESCRIPTION
    {{SCRIPT_DESCRIPTION}}
    
    This script supports both local execution and Azure Pipelines environments.
    Configuration can be provided via parameters or external config file.

.PARAMETER Configuration
    Build configuration to use (Debug or Release). Default: Release

.PARAMETER OutputPath
    Directory to write output files. 
    Default: $env:TEMP/{{SCRIPT_NAME}} (local) or $env:BUILD_ARTIFACTSTAGINGDIRECTORY/{{SCRIPT_NAME}} (Azure Pipelines)

.PARAMETER ConfigFile
    Path to configuration file (JSON). Default: ./{{SCRIPT_NAME}}-config.json

.PARAMETER {{PARAMETER_NAME}}
    {{PARAMETER_DESCRIPTION}}

.PARAMETER Verbose
    Enable verbose output for debugging

.EXAMPLE
    .\{{SCRIPT_NAME}}.ps1
    
    Runs with default settings

.EXAMPLE
    .\{{SCRIPT_NAME}}.ps1 -Configuration Debug -OutputPath "C:\temp\output"
    
    Runs with custom configuration and output path

.EXAMPLE
    .\{{SCRIPT_NAME}}.ps1 -ConfigFile "custom-config.json"
    
    Runs with custom configuration file

.EXAMPLE
    # Azure Pipelines usage
    - task: PowerShell@2
      inputs:
        filePath: 'scripts/{{SCRIPT_NAME}}.ps1'
        arguments: '-{{PARAMETER_NAME}} "{{PARAMETER_VALUE}}"'

.NOTES
    File Name      : {{SCRIPT_NAME}}.ps1
    Author         : {{AUTHOR}}
    Prerequisite   : {{PREREQUISITES}}
    Quality Level  : Standard (Production-Ready)
    
.LINK
    {{DOCUMENTATION_URL}}
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false, HelpMessage="Build configuration (Debug or Release)")]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    
    [Parameter(Mandatory=$false, HelpMessage="Output directory for results")]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false, HelpMessage="Configuration file path")]
    [string]$ConfigFile = "$PSScriptRoot/{{SCRIPT_NAME}}-config.json",
    
    [Parameter(Mandatory=$false, HelpMessage="{{PARAMETER_DESCRIPTION}}")]
    [ValidateRange(0, 100)]
    [int]${{PARAMETER_NAME}} = {{PARAMETER_DEFAULT}}
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== {{SCRIPT_NAME}} ===" -ForegroundColor Cyan
Write-Host ""

# ======================================
# Environment Detection
# ======================================

$isAzurePipeline = [bool]$env:AGENT_TEMPDIRECTORY

if ($isAzurePipeline) {
    Write-Host "Running in Azure Pipelines" -ForegroundColor Yellow
} else {
    Write-Host "Running locally" -ForegroundColor Yellow
}

# ======================================
# Set Portable Defaults
# ======================================

if (-not $OutputPath) {
    if ($isAzurePipeline) {
        $OutputPath = "$env:BUILD_ARTIFACTSTAGINGDIRECTORY/{{SCRIPT_NAME}}"
    } else {
        $OutputPath = "$env:TEMP/{{SCRIPT_NAME}}"
    }
}

# ======================================
# Load Configuration File (if exists)
# ======================================

if (Test-Path $ConfigFile) {
    Write-Host "Loading configuration from: $ConfigFile" -ForegroundColor Cyan
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    
    # Override parameters with config values if not explicitly set
    if (-not $PSBoundParameters.ContainsKey('{{PARAMETER_NAME}}')) {
        ${{PARAMETER_NAME}} = $config.{{PARAMETER_NAME}}
    }
    
    Write-Host "Configuration loaded successfully" -ForegroundColor Green
} else {
    Write-Host "No config file found, using parameter defaults" -ForegroundColor Yellow
}

# ======================================
# Create Output Directory
# ======================================

if (-not (Test-Path $OutputPath)) {
    Write-Host "Creating output directory: $OutputPath"
    New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
}

# ======================================
# Display Configuration
# ======================================

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Configuration: $Configuration"
Write-Host "  Output Path: $OutputPath"
Write-Host "  {{PARAMETER_NAME}}: ${{PARAMETER_NAME}}"
Write-Host ""

try {
    # ======================================
    # Main Script Logic
    # ======================================
    
    Write-Host "Starting processing..." -ForegroundColor Yellow
    
    # TODO: Replace with actual logic
    # Example: Process items, call external tools, generate reports
    
    Write-Host "Processing complete" -ForegroundColor Green
    
    # ======================================
    # Output Results
    # ======================================
    
    $resultFile = Join-Path $OutputPath "results.json"
    
    $results = @{
        Timestamp = Get-Date -Format "o"
        Configuration = $Configuration
        {{PARAMETER_NAME}} = ${{PARAMETER_NAME}}
        Status = "Success"
        # TODO: Add actual result data
    }
    
    $results | ConvertTo-Json -Depth 10 | Set-Content $resultFile
    
    Write-Host ""
    Write-Host "✅ Script completed successfully!" -ForegroundColor Green
    Write-Host "Output saved to: $OutputPath"
    Write-Host ""
    exit 0
}
catch {
    # ======================================
    # Error Handling
    # ======================================
    
    Write-Host "##vso[task.logissue type=error]$($_.Exception.Message)"
    Write-Host "❌ Script failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Stack Trace:" -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace
    Write-Host ""
    exit 1
}
finally {
    # ======================================
    # Cleanup
    # ======================================
    
    Write-Verbose "Cleaning up temporary files..."
    
    # TODO: Add cleanup logic for temp files if needed
    # Example: Remove-Item -Path "$env:TEMP/temp-{{SCRIPT_NAME}}-*" -Force -ErrorAction SilentlyContinue
}

