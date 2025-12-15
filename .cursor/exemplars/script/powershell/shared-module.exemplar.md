# Shared Module Pattern - PowerShell Exemplar

## Purpose

Demonstrates creating and using a PowerShell shared module (`.psm1`) to promote DRY principle, centralize common functionality, and ensure consistent behavior across multiple scripts.

## Pattern Overview

**When to Use:**
- Function is used in 2+ scripts
- Common utilities (logging, formatting, validation, Unicode detection)
- Consistent behavior needed across scripts

**Benefits:**
- Write once, use everywhere
- Centralized bug fixes
- Consistent behavior
- Faster development

---

## Complete Example: Common Utilities Module

### File Structure

```text
repository/
├── scripts/
│   ├── validate-code-quality.ps1       # Uses shared module
│   ├── generate-changelog.ps1          # Uses shared module
│   ├── run-tests.ps1                   # Uses shared module
│   └── modules/
│       └── Common.psm1                  # Shared module
```

---

## Module Implementation: `scripts/modules/Common.psm1`

```powershell
<#
.SYNOPSIS
    Common utility functions for scripts

.DESCRIPTION
    Shared module providing Unicode detection, status formatting,
    path utilities, and common helper functions used across multiple
    automation scripts.

    This module promotes DRY (Don't Repeat Yourself) by centralizing
    common functionality and ensuring consistent behavior.

.NOTES
    File Name   : Common.psm1
    Author      : DevOps Team
    Version     : 1.0.0
    Location    : scripts/modules/
    
    Functions Exported:
    - Test-Unicode
    - Get-StatusEmoji
    - Get-StatusMessage
    - Write-Section
    - Test-CommandExists
    - Get-GitRoot

.EXAMPLE
    Import-Module "$PSScriptRoot/modules/Common.psm1" -Force
    
    $checkmark = Get-StatusEmoji 'success'
    Write-Host "$checkmark All tests passed!" -ForegroundColor Green

.LINK
    https://docs.internal.com/scripting/shared-modules
#>

# Stop on first error
$ErrorActionPreference = 'Stop'

#region Unicode Detection

function Test-Unicode {
    <#
    .SYNOPSIS
        Detects if the environment supports Unicode output.
    
    .DESCRIPTION
        Checks multiple factors to determine Unicode support:
        - PowerShell version (7+ always supports Unicode)
        - Azure Pipelines environment (supports Unicode)
        - Console encoding (UTF-8 check)
    
    .OUTPUTS
        [bool] True if Unicode is supported, False otherwise.
    
    .EXAMPLE
        if (Test-Unicode) {
            Write-Host "✅ Unicode supported"
        } else {
            Write-Host "[OK] ASCII fallback"
        }
    
    .NOTES
        PowerShell 7+ and Azure Pipelines have full Unicode support.
        Windows PowerShell 5.1 depends on console encoding.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()
    
    # PowerShell 7+ always supports Unicode
    $psVersion = $PSVersionTable.PSVersion.Major
    if ($psVersion -ge 7) {
        Write-Verbose "Unicode supported: PowerShell $psVersion detected"
        return $true
    }
    
    # Azure Pipelines supports Unicode
    if ($env:AGENT_TEMPDIRECTORY -ne $null) {
        Write-Verbose "Unicode supported: Azure Pipelines environment detected"
        return $true
    }
    
    # Check if console encoding is UTF-8
    try {
        $isUtf8Console = [Console]::OutputEncoding.CodePage -eq 65001
        if ($isUtf8Console) {
            Write-Verbose "Unicode supported: UTF-8 console encoding detected"
            return $true
        }
    }
    catch {
        Write-Verbose "Unicode detection: Console encoding check failed"
    }
    
    Write-Verbose "Unicode not supported: Using ASCII fallback"
    return $false
}

#endregion

#region Status Formatting

function Get-StatusEmoji {
    <#
    .SYNOPSIS
        Gets status indicator emoji or ASCII fallback.
    
    .DESCRIPTION
        Returns appropriate Unicode emoji or ASCII text based on environment
        support detected by Test-Unicode. Automatically adapts output to
        environment capabilities.
    
    .PARAMETER Status
        Status type. Valid values: 'success', 'warning', 'error', 'info'
    
    .OUTPUTS
        [string] Emoji or ASCII representation of status.
    
    .EXAMPLE
        $checkmark = Get-StatusEmoji 'success'
        Write-Host "$checkmark Tests passed!" -ForegroundColor Green
        # Output: "✅ Tests passed!" or "[OK] Tests passed!"
    
    .EXAMPLE
        $error = Get-StatusEmoji 'error'
        Write-Host "$error Build failed!" -ForegroundColor Red
        # Output: "❌ Build failed!" or "[ERR] Build failed!"
    
    .NOTES
        Supports: success, warning, error, info
        Adapts based on Unicode support in current environment
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('success', 'warning', 'error', 'info')]
        [string]$Status
    )
    
    if (Test-Unicode) {
        $emojis = @{
            'success' = '✅'
            'warning' = '⚠️'
            'error'   = '❌'
            'info'    = 'ℹ️'
        }
    } else {
        $emojis = @{
            'success' = '[OK]'
            'warning' = '[WARN]'
            'error'   = '[ERR]'
            'info'    = '[INFO]'
        }
    }
    
    return $emojis[$Status]
}

function Get-StatusMessage {
    <#
    .SYNOPSIS
        Formats a complete status message with emoji/ASCII indicator.
    
    .DESCRIPTION
        Combines status emoji with message text and optional details.
        Provides consistent message formatting across all scripts.
    
    .PARAMETER Status
        Status type: 'success', 'warning', 'error', 'info'
    
    .PARAMETER Message
        Primary message text
    
    .PARAMETER Details
        Optional additional details (shown on new line)
    
    .OUTPUTS
        [string] Formatted status message
    
    .EXAMPLE
        $msg = Get-StatusMessage 'success' 'Build completed' 'Duration: 2m 34s'
        Write-Host $msg -ForegroundColor Green
        # Output:
        # ✅ Build completed
        # Duration: 2m 34s
    
    .EXAMPLE
        $msg = Get-StatusMessage 'error' 'Validation failed'
        Write-Host $msg -ForegroundColor Red
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('success', 'warning', 'error', 'info')]
        [string]$Status,
        
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [string]$Details
    )
    
    $emoji = Get-StatusEmoji $Status
    $output = "$emoji $Message"
    
    if ($Details) {
        $output += "`n$Details"
    }
    
    return $output
}

function Write-Section {
    <#
    .SYNOPSIS
        Writes a formatted section header.
    
    .DESCRIPTION
        Displays a visually distinct section header for script output.
        Improves readability of multi-step scripts.
    
    .PARAMETER Title
        Section title text
    
    .PARAMETER Color
        Console color for output (default: Cyan)
    
    .EXAMPLE
        Write-Section "Running Tests"
        # Output:
        # ================================================================================
        # Running Tests
        # ================================================================================
    
    .EXAMPLE
        Write-Section "Validation Complete" -Color Green
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,
        
        [Parameter(Mandatory = $false)]
        [ConsoleColor]$Color = 'Cyan'
    )
    
    $separator = "=" * 80
    Write-Host ""
    Write-Host $separator -ForegroundColor $Color
    Write-Host $Title -ForegroundColor $Color
    Write-Host $separator -ForegroundColor $Color
    Write-Host ""
}

#endregion

#region Utility Functions

function Test-CommandExists {
    <#
    .SYNOPSIS
        Checks if a command/executable exists in PATH.
    
    .DESCRIPTION
        Verifies that a required command is available before attempting to use it.
        Useful for checking prerequisites (dotnet, git, etc.)
    
    .PARAMETER Command
        Command name to check
    
    .OUTPUTS
        [bool] True if command exists, False otherwise
    
    .EXAMPLE
        if (-not (Test-CommandExists 'dotnet')) {
            Write-Error ".NET SDK not found. Install from https://dot.net"
            exit 3
        }
    
    .EXAMPLE
        Test-CommandExists 'git' -ErrorAction Stop
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    
    if ($exists) {
        Write-Verbose "Command '$Command' found in PATH"
    } else {
        Write-Verbose "Command '$Command' not found in PATH"
    }
    
    return $exists
}

function Get-GitRoot {
    <#
    .SYNOPSIS
        Gets the root directory of the current git repository.
    
    .DESCRIPTION
        Finds the git repository root by walking up the directory tree
        until .git directory is found.
    
    .OUTPUTS
        [string] Full path to git repository root
    
    .EXAMPLE
        $repoRoot = Get-GitRoot
        $scriptsPath = Join-Path $repoRoot "scripts"
    
    .NOTES
        Throws error if not in a git repository
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()
    
    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($gitRoot)) {
            throw "Not in a git repository"
        }
        
        # Convert Unix path to Windows path if needed
        if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) {
            $gitRoot = $gitRoot -replace '/', '\'
        }
        
        Write-Verbose "Git root: $gitRoot"
        return $gitRoot
    }
    catch {
        throw "Failed to determine git repository root: $($_.Exception.Message)"
    }
}

#endregion

#region Module Exports

# Export only public functions (not internal helpers)
Export-ModuleMember -Function @(
    'Test-Unicode',
    'Get-StatusEmoji',
    'Get-StatusMessage',
    'Write-Section',
    'Test-CommandExists',
    'Get-GitRoot'
)

#endregion
```

---

## Usage Example 1: Validation Script

### File: `scripts/validate-code-quality.ps1`

```powershell
#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Validates code quality standards

.DESCRIPTION
    Runs linting, formatting checks, and validation rules to ensure
    code meets quality standards before commit.

.EXAMPLE
    .\validate-code-quality.ps1
#>

[CmdletBinding()]
param()

# Import shared module
$ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
Import-Module $ModulePath -Force

try {
    Write-Section "Code Quality Validation"
    
    # Check prerequisites
    $info = Get-StatusEmoji 'info'
    Write-Host "$info Checking prerequisites..." -ForegroundColor Cyan
    
    if (-not (Test-CommandExists 'dotnet')) {
        $error = Get-StatusEmoji 'error'
        Write-Host "$error .NET SDK not found" -ForegroundColor Red
        Write-Host "Install from: https://dot.net" -ForegroundColor Yellow
        exit 3
    }
    
    $success = Get-StatusEmoji 'success'
    Write-Host "$success Prerequisites verified" -ForegroundColor Green
    Write-Host ""
    
    # Run linting
    Write-Host "$info Running linter..." -ForegroundColor Cyan
    dotnet format --verify-no-changes
    
    if ($LASTEXITCODE -ne 0) {
        $warning = Get-StatusEmoji 'warning'
        Write-Host "$warning Format issues found - run 'dotnet format' to fix" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "$success Linting passed" -ForegroundColor Green
    Write-Host ""
    
    # Build check
    Write-Host "$info Building solution..." -ForegroundColor Cyan
    dotnet build --no-restore
    
    if ($LASTEXITCODE -ne 0) {
        $error = Get-StatusEmoji 'error'
        Write-Host "$error Build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "$success Build successful" -ForegroundColor Green
    Write-Host ""
    
    # Final summary
    Write-Section "Validation Complete" -Color Green
    $msg = Get-StatusMessage 'success' 'All quality checks passed' 'Ready to commit'
    Write-Host $msg -ForegroundColor Green
    
    exit 0
}
catch {
    $error = Get-StatusEmoji 'error'
    Write-Host "$error Validation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

---

## Usage Example 2: Changelog Generator

### File: `scripts/generate-changelog.ps1`

```powershell
#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Generates changelog from git commits

.PARAMETER OutputFile
    Path to changelog file (default: CHANGELOG.md)

.EXAMPLE
    .\generate-changelog.ps1
    .\generate-changelog.ps1 -OutputFile docs/CHANGELOG.md
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$OutputFile = "CHANGELOG.md"
)

# Import shared module
$ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
Import-Module $ModulePath -Force

try {
    Write-Section "Changelog Generation"
    
    # Check git availability
    if (-not (Test-CommandExists 'git')) {
        $error = Get-StatusEmoji 'error'
        Write-Host "$error Git not found in PATH" -ForegroundColor Red
        exit 3
    }
    
    # Get repository root
    $repoRoot = Get-GitRoot
    $fullPath = Join-Path $repoRoot $OutputFile
    
    $info = Get-StatusEmoji 'info'
    Write-Host "$info Repository: $repoRoot" -ForegroundColor Cyan
    Write-Host "$info Output file: $fullPath" -ForegroundColor Cyan
    Write-Host ""
    
    # Generate changelog logic here...
    # (Simplified for exemplar)
    
    $success = Get-StatusEmoji 'success'
    $msg = Get-StatusMessage 'success' 'Changelog generated' "File: $fullPath"
    Write-Host $msg -ForegroundColor Green
    
    exit 0
}
catch {
    $error = Get-StatusEmoji 'error'
    Write-Host "$error Failed to generate changelog: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

---

## Benefits Demonstrated

### 1. **DRY Principle**
- `Test-Unicode` logic written once, used everywhere
- `Get-StatusEmoji` centralized status formatting
- All scripts get consistent behavior

### 2. **Centralized Fixes**
```powershell
# If Unicode detection logic needs updating:
# - Fix in Common.psm1 (1 place)
# - All scripts immediately benefit (10+ scripts)
```

### 3. **Consistent User Experience**
- All scripts use same emoji/ASCII indicators
- All scripts have same section formatting
- All scripts follow same error handling patterns

### 4. **Faster Development**
```powershell
# New script can immediately use proven utilities
Import-Module "$PSScriptRoot/modules/Common.psm1" -Force
$checkmark = Get-StatusEmoji 'success'
# No need to rewrite Unicode detection logic
```

### 5. **Testability**
```powershell
# Module can be tested independently
Import-Module "./modules/Common.psm1" -Force

Describe "Test-Unicode" {
    It "Returns boolean" {
        $result = Test-Unicode
        $result | Should -BeOfType [bool]
    }
}
```

---

## Best Practices Demonstrated

✅ **Complete comment-based help** - Every function documented  
✅ **Export-ModuleMember** - Only public functions exported  
✅ **Relative imports** - `$PSScriptRoot` for portability  
✅ **-Force flag** - Ensures fresh module load  
✅ **Verbose logging** - `Write-Verbose` for debugging  
✅ **Parameter validation** - `ValidateSet`, `Mandatory`  
✅ **Regions** - Organized function groups  
✅ **Error handling** - Try/catch with meaningful messages  

---

## Anti-Patterns Avoided

❌ **Giant module** - Focused on common utilities only  
❌ **No documentation** - All functions have full help  
❌ **Hardcoded paths** - Uses relative paths  
❌ **Missing exports** - Explicit `Export-ModuleMember`  
❌ **No versioning** - Module has version in header  

---

## Testing the Module

### Unit Test Example: `scripts/modules/Common.Tests.ps1`

```powershell
#Requires -Module Pester

BeforeAll {
    Import-Module "$PSScriptRoot/Common.psm1" -Force
}

Describe "Common Module" {
    Context "Test-Unicode" {
        It "Returns boolean" {
            $result = Test-Unicode
            $result | Should -BeOfType [bool]
        }
    }
    
    Context "Get-StatusEmoji" {
        It "Returns string for valid status" {
            $result = Get-StatusEmoji 'success'
            $result | Should -BeOfType [string]
            $result | Should -Not -BeNullOrEmpty
        }
        
        It "Throws error for invalid status" {
            { Get-StatusEmoji 'invalid' } | Should -Throw
        }
        
        It "Returns Unicode or ASCII" {
            $result = Get-StatusEmoji 'success'
            $result | Should -Match '^(✅|\[OK\])$'
        }
    }
    
    Context "Test-CommandExists" {
        It "Returns true for PowerShell" {
            Test-CommandExists 'pwsh' | Should -BeTrue
        }
        
        It "Returns false for non-existent command" {
            Test-CommandExists 'totally-fake-command-xyz' | Should -BeFalse
        }
    }
}
```

**Run tests:**
```powershell
Invoke-Pester scripts/modules/Common.Tests.ps1 -Output Detailed
```

---

## When to Create a Shared Module

### ✅ Create Module When:
- Function used in 2+ scripts
- Common utility (formatting, logging, validation)
- Consistent behavior needed
- Logic likely to be reused

### ❌ Keep in Script When:
- Function specific to one script
- Complex dependencies unique to script
- Only used once
- Highly specialized logic

---

## Migration Strategy

### Step 1: Identify Duplicated Code
```powershell
# Search for duplicated functions across scripts
Select-String -Path scripts/*.ps1 -Pattern "function Get-StatusEmoji"
```

### Step 2: Extract to Module
```powershell
# Create modules directory
New-Item -Path scripts/modules -ItemType Directory -Force

# Create Common.psm1 with extracted functions
```

### Step 3: Update Scripts to Import Module
```powershell
# Add to each script
$ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
Import-Module $ModulePath -Force
```

### Step 4: Remove Duplicated Code
```powershell
# Remove function definitions from individual scripts
# Keep only Import-Module and function calls
```

### Step 5: Test Thoroughly
```powershell
# Run all scripts to ensure they still work
# Add unit tests for module functions
```

---

## Related Resources

- **Rule**: `rule.scripts.core-principles.v1` - Core Principle 7: Reusability Through Modules
- **Rule**: `rule.scripts.powershell-standards.v1` - Shared Modules section
- **Prompt**: `.cursor/prompts/script/migrate-to-shared-module.prompt.md`
- **Templar**: `.cursor/templars/script/powershell-script-full.templar.ps1`

---

## Summary

This exemplar demonstrates:
- Complete PowerShell module structure (`.psm1`)
- Unicode detection and conditional output
- Status formatting utilities
- Path and command utilities
- Multiple scripts using the same module
- DRY principle in action
- Testability and maintainability
- Production-ready patterns

**Key Takeaway**: Extract shared functions to modules for DRY, consistency, and faster development.

