<#
.SYNOPSIS
    Convenience alias for start.ps1
#>
[CmdletBinding()]
param(
    [switch]$RunPipeline,
    [switch]$RunTests,
    [switch]$Dashboard,
    [switch]$OpenExcel,
    [switch]$Notebook
)

& "$PSScriptRoot\start.ps1" @PSBoundParameters
