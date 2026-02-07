[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Path = ".",

    [switch]$Recurse,
    [switch]$FailFast
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command -Name ConvertFrom-Yaml -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ ERROR: ConvertFrom-Yaml is not available" -ForegroundColor Red
    Write-Host "`nExplanation: This script relies on the ConvertFrom-Yaml cmdlet (PowerShell 7+ or the powershell-yaml module)." -ForegroundColor Yellow
    Write-Host "`nSolution:" -ForegroundColor Green
    Write-Host "  1. Upgrade to PowerShell 7+ or" -ForegroundColor Green
    Write-Host "  2. Install the module: Install-Module powershell-yaml -Scope CurrentUser" -ForegroundColor Green
    Write-Host "  3. Re-run this script" -ForegroundColor Green
    exit 1
}

function Resolve-YamlFiles {
    param(
        [string[]]$InputPath,
        [switch]$Recurse
    )

    $files = @()
    foreach ($p in $InputPath) {
        $resolved = Resolve-Path -LiteralPath $p -ErrorAction Stop
        foreach ($r in $resolved) {
            if (Test-Path -LiteralPath $r -PathType Leaf) {
                if ($r -match '\.ya?ml$') {
                    $files += Get-Item -LiteralPath $r
                }
            } elseif (Test-Path -LiteralPath $r -PathType Container) {
                $files += Get-ChildItem -LiteralPath $r -File -Include *.yaml,*.yml -Recurse:$Recurse
            }
        }
    }

    return ($files | Sort-Object -Unique)
}

function Write-InvalidYaml {
    param(
        [string]$FilePath,
        [string]$Message
    )

    Write-Host "`n❌ ERROR: Invalid YAML in '$FilePath'" -ForegroundColor Red
    Write-Host "`nExplanation: $Message" -ForegroundColor Yellow
    Write-Host "`nSolution:" -ForegroundColor Green
    Write-Host "  1. Fix the YAML syntax in the file." -ForegroundColor Green
    Write-Host "  2. Re-run this script." -ForegroundColor Green
}

function Write-Summary {
    param(
        [int]$Checked,
        [int]$Failed
    )

    if ($Failed -gt 0) {
        Write-Host "`n❌ ERROR: YAML validation failed ($Failed of $Checked files invalid)" -ForegroundColor Red
        exit 1
    }

    Write-Host "`n✅ All YAML files are valid ($Checked checked)" -ForegroundColor Green
    exit 0
}

try {
    $yamlFiles = Resolve-YamlFiles -InputPath $Path -Recurse:$Recurse
} catch {
    Write-Host "`n❌ ERROR: Path resolution failed" -ForegroundColor Red
    Write-Host "`nExplanation: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "`nSolution:" -ForegroundColor Green
    Write-Host "  1. Verify the provided path(s) exist." -ForegroundColor Green
    Write-Host "  2. Re-run this script with valid path(s)." -ForegroundColor Green
    exit 1
}

if (-not $yamlFiles) {
    Write-Host "`nℹ INFO: No YAML files found for the provided path(s)." -ForegroundColor Cyan
    exit 0
}

$checked = 0
$failed = 0

foreach ($file in $yamlFiles) {
    $checked++
    try {
        $content = Get-Content -LiteralPath $file.FullName -Raw
        ConvertFrom-Yaml -Yaml $content | Out-Null
        Write-Host "✅ $($file.FullName)" -ForegroundColor Green
    } catch {
        $failed++
        Write-InvalidYaml -FilePath $file.FullName -Message $_.Exception.Message.Trim()
        if ($FailFast) {
            Write-Summary -Checked $checked -Failed $failed
        }
    }
}

Write-Summary -Checked $checked -Failed $failed
