---
name: Migrate to Shared Modules
description: "Extract duplicated functions from scripts into shared modules"
category: script
tags: [migration, dry-principle, shared-modules, refactoring]
---

# Migrate Scripts to Use Shared Modules

## Purpose

Guide the systematic migration of scripts to extract duplicated functions into shared modules, promoting DRY principle and consistent behavior.

## When to Use This Prompt

Use this prompt when:
- Multiple scripts contain duplicate function definitions
- Common utility functions (Unicode detection, logging, formatting) are copied across scripts
- You want to centralize shared logic for easier maintenance
- Scripts need consistent behavior (e.g., status indicators, error handling)

## Prerequisites

- [ ] PowerShell 5.1+ or Python 3.9+ environment
- [ ] Multiple scripts with duplicated functions identified
- [ ] Understanding of module structure for target language

## Process

### Step 1: Analyze Current Scripts

**Instructions for AI:**

1. Scan all scripts in `scripts/` directory
2. Identify functions that appear in 2+ scripts
3. List duplicated functions with their locations
4. Categorize functions by purpose:
   - **Formatting/Output**: Unicode detection, status indicators, section headers
   - **Validation**: Command checks, path validation, config validation
   - **Utilities**: Path helpers, git operations, file operations
   - **Error Handling**: Consistent error messages, logging wrappers

**Output Format:**

```markdown
## Duplicated Functions Found

### Formatting/Output Functions
- `Test-Unicode` (or `supports_unicode`)
  - Found in: validate-code-quality.ps1, generate-changelog.ps1, run-tests.ps1
  - Lines: 25-40 in each file
  - Purpose: Detect Unicode support in environment

- `Get-StatusEmoji` (or `get_status_emoji`)
  - Found in: validate-code-quality.ps1, generate-changelog.ps1
  - Lines: 42-58
  - Purpose: Get status indicator (emoji or ASCII)

### Validation Functions
- `Test-CommandExists` (or `command_exists`)
  - Found in: validate-code-quality.ps1, run-tests.ps1
  - Lines: 60-70
  - Purpose: Check if command exists in PATH

### Recommendation
Extract 3 functions to shared module: Test-Unicode, Get-StatusEmoji, Test-CommandExists
```

### Step 2: Design Module Structure

**Instructions for AI:**

Based on identified duplicates, design the module structure:

**PowerShell:**
```powershell
# Proposed: scripts/modules/Common.psm1

<#
.SYNOPSIS
    Common utility functions for scripts

.DESCRIPTION
    Shared module providing [list functions]
#>

# Function definitions...

Export-ModuleMember -Function @(
    'Test-Unicode',
    'Get-StatusEmoji',
    'Test-CommandExists'
)
```

**Python:**
```python
# Proposed: scripts/modules/common.py

"""
Common utility functions for scripts.

Functions:
    supports_unicode() -> bool
    get_status_emoji(status: str) -> str
    command_exists(cmd: str) -> bool
"""

# Function definitions...

__all__ = ['supports_unicode', 'get_status_emoji', 'command_exists']
```

### Step 3: Create Shared Module

**Instructions for AI:**

1. Create `scripts/modules/` directory if it doesn't exist
2. Create module file (`Common.psm1` or `common.py`)
3. Extract the most complete/correct version of each function
4. Add comprehensive comment-based help (PowerShell) or docstrings (Python)
5. Add parameter validation and type hints
6. Add verbose logging for debugging
7. Export only public functions
8. Include module header with version and description

**For PowerShell:**
- Use `.psm1` extension
- Include `<# .SYNOPSIS .DESCRIPTION #>` header
- Use `Export-ModuleMember -Function @(...)`
- Organize with `#region` blocks

**For Python:**
- Create `__init__.py` (can be empty)
- Use module-level docstring
- Define `__all__` for public API
- Use type hints on all signatures

### Step 4: Update Each Script

**Instructions for AI:**

For each script that uses the duplicated functions:

1. Add module import at the top (after parameters):

   **PowerShell:**
   ```powershell
   # Import shared module
   $ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
   Import-Module $ModulePath -Force
   ```

   **Python:**
   ```python
   # Import shared module
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent / "modules"))
   from common import get_status_emoji, supports_unicode
   ```

2. Remove the duplicated function definitions
3. Keep function calls unchanged (functions now come from module)
4. Test the script to ensure it works

### Step 5: Verification

**Instructions for AI:**

After migration, verify:

1. **Module exists**: `scripts/modules/Common.psm1` or `scripts/modules/common.py`
2. **Module imports successfully**: No import errors
3. **All scripts updated**: No scripts contain old function definitions
4. **Scripts still work**: Test each script to ensure functionality
5. **Consistent behavior**: All scripts use same module functions

**Verification Commands:**

```powershell
# PowerShell: Test module import
Import-Module "./scripts/modules/Common.psm1" -Force
Get-Command -Module Common  # Should list exported functions

# Test each script
.\scripts\validate-code-quality.ps1 -Verbose
.\scripts\generate-changelog.ps1 -Verbose
```

```bash
# Python: Test module import
cd scripts
python -c "from modules.common import *; print(get_status_emoji('success'))"

# Test each script
python scripts/validate-code-quality.py --verbose
python scripts/generate-changelog.py --verbose
```

### Step 6: Documentation

**Instructions for AI:**

Update documentation:

1. **Add module README** (optional): `scripts/modules/README.md`
   - Describe module purpose
   - List exported functions
   - Show usage examples

2. **Update script documentation**:
   - Add "Uses shared module: Common" note to each script's help
   - Update examples if needed

3. **Create unit tests** (recommended):
   - PowerShell: `scripts/modules/Common.Tests.ps1` (Pester)
   - Python: `scripts/modules/test_common.py` (pytest)

## Example: Complete Migration

### Before Migration

**File: `scripts/validate-code-quality.ps1`**
```powershell
#!/usr/bin/env pwsh
param()

# Duplicated function (also in generate-changelog.ps1, run-tests.ps1)
function Test-Unicode {
    $psVersion = $PSVersionTable.PSVersion.Major
    return ($psVersion -ge 7) -or ($env:AGENT_TEMPDIRECTORY -ne $null)
}

# Duplicated function
function Get-StatusEmoji {
    param([string]$Status)
    if (Test-Unicode) {
        return @{'success'='✅'; 'error'='❌'}[$Status]
    } else {
        return @{'success'='[OK]'; 'error'='[ERR]'}[$Status]
    }
}

# Script logic
$checkmark = Get-StatusEmoji 'success'
Write-Host "$checkmark Tests passed!" -ForegroundColor Green
```

**Problem**: Same functions duplicated in 3+ scripts, hard to maintain.

### After Migration

**File: `scripts/modules/Common.psm1` (NEW)**
```powershell
<#
.SYNOPSIS
    Common utility functions for scripts
#>

function Test-Unicode {
    <#
    .SYNOPSIS
        Detects if the environment supports Unicode output.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $psVersion = $PSVersionTable.PSVersion.Major
    $inAzure = $env:AGENT_TEMPDIRECTORY -ne $null
    $isUtf8Console = [Console]::OutputEncoding.CodePage -eq 65001

    return ($psVersion -ge 7) -or $inAzure -or $isUtf8Console
}

function Get-StatusEmoji {
    <#
    .SYNOPSIS
        Gets status indicator emoji or ASCII fallback.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('success', 'warning', 'error', 'info')]
        [string]$Status
    )

    if (Test-Unicode) {
        $emojis = @{
            'success' = '✅'; 'warning' = '⚠️'
            'error' = '❌'; 'info' = 'ℹ️'
        }
    } else {
        $emojis = @{
            'success' = '[OK]'; 'warning' = '[WARN]'
            'error' = '[ERR]'; 'info' = '[INFO]'
        }
    }

    return $emojis[$Status]
}

Export-ModuleMember -Function Test-Unicode, Get-StatusEmoji
```

**File: `scripts/validate-code-quality.ps1` (UPDATED)**
```powershell
#!/usr/bin/env pwsh
param()

# Import shared module
$ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
Import-Module $ModulePath -Force

# Script logic (unchanged)
$checkmark = Get-StatusEmoji 'success'
Write-Host "$checkmark Tests passed!" -ForegroundColor Green
```

**Benefits:**
- ✅ Function written once, used everywhere
- ✅ Bug fixes benefit all scripts
- ✅ Consistent behavior guaranteed
- ✅ Faster to write new scripts

## Quality Checklist

After migration, ensure:

- [ ] **Module created**: `scripts/modules/Common.psm1` or `common.py` exists
- [ ] **Functions extracted**: Duplicated functions removed from individual scripts
- [ ] **Module imported**: All scripts import the shared module
- [ ] **Tests pass**: All scripts still function correctly
- [ ] **Documentation updated**: Module and scripts have complete help/docstrings
- [ ] **Exports correct**: Only public functions exported (`Export-ModuleMember` or `__all__`)
- [ ] **Portability maintained**: Relative imports work in all environments
- [ ] **Unit tests added**: Module has unit tests (Pester or pytest)

## Common Issues and Solutions

### Issue: "Module not found" Error

**PowerShell:**
```powershell
# Problem: Wrong path
Import-Module "./modules/Common.psm1"

# Solution: Use $PSScriptRoot for relative path
$ModulePath = Join-Path $PSScriptRoot "modules\Common.psm1"
Import-Module $ModulePath -Force
```

**Python:**
```python
# Problem: Module not in sys.path
from common import get_status_emoji  # ModuleNotFoundError

# Solution: Add modules directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "modules"))
from common import get_status_emoji
```

### Issue: Module Changes Not Reflected

**PowerShell:**
```powershell
# Problem: Module cached from previous import
Import-Module "./modules/Common.psm1"

# Solution: Use -Force flag to reload
Import-Module $ModulePath -Force
```

**Python:**
```python
# Problem: Module cached by Python
import common

# Solution: Use importlib.reload in development
import importlib
importlib.reload(common)
```

### Issue: Function Not Exported

**PowerShell:**
```powershell
# Problem: Function not in Export-ModuleMember
function Get-StatusEmoji { ... }
# Missing: Export-ModuleMember

# Solution: Explicitly export
Export-ModuleMember -Function Get-StatusEmoji
```

**Python:**
```python
# Problem: Function not in __all__
def get_status_emoji(): ...
# Missing: __all__

# Solution: Define public API
__all__ = ['get_status_emoji']
```

## Related Resources

- **Rule**: `rule.scripts.core-principles.v1` - Core Principle 7: Reusability Through Modules
- **Rule**: `rule.scripts.powershell-standards.v1` - Shared Modules (Best Practice)
- **Rule**: `rule.scripts.python-standards.v1` - Shared Modules (Best Practice)
- **Exemplar**: `.cursor/exemplars/script/powershell/shared-module.exemplar.md`
- **Exemplar**: `.cursor/exemplars/script/python/shared-module.exemplar.md`

## Summary

This prompt guides:
1. **Analysis**: Identify duplicated functions across scripts
2. **Design**: Plan module structure and exports
3. **Create**: Build shared module with documentation
4. **Update**: Migrate scripts to import and use module
5. **Verify**: Test all scripts work correctly
6. **Document**: Update help/docstrings and add tests

**Goal**: Eliminate code duplication, centralize common logic, ensure consistent behavior.
