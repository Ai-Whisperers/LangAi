#Requires -Version 7.2
#Requires -PSEdition Core
<#
.SYNOPSIS
    Shared utilities for housekeeping scripts.

.DESCRIPTION
    Provides reusable helpers for status glyph output with Unicode/ASCII fallback
    and path normalization used across housekeeping scripts.

.NOTES
    Exported functions:
      - Get-StatusGlyph
      - Normalize
#>

function Get-StatusGlyph {
    <#
    .SYNOPSIS
        Returns status glyph with Unicode or ASCII fallback.
    .PARAMETER Kind
        Status kind: success | warning | error | info
    .OUTPUTS
        [string] Glyph appropriate for console capabilities.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][ValidateSet('success','warning','error','info')][string]$Kind)

    $supportsUnicode = ($PSVersionTable.PSVersion.Major -ge 7) -or ($env:AGENT_TEMPDIRECTORY) -or ([Console]::OutputEncoding.CodePage -eq 65001)
    if ($supportsUnicode) {
        return @{
            success = '✅'
            warning = '⚠️'
            error   = '❌'
            info    = 'ℹ️'
        }[$Kind]
    }

    return @{
        success = '[OK]'
        warning = '[WARN]'
        error   = '[ERR]'
        info    = '[INFO]'
    }[$Kind]
}

function Normalize {
    <#
    .SYNOPSIS
        Normalizes a path to use forward slashes.
    .PARAMETER Path
        Path string to normalize.
    .OUTPUTS
        [string] Normalized path.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)

    return ($Path -replace '\\','/')
}

Export-ModuleMember -Function Get-StatusGlyph, Normalize
