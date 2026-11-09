[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[A-Za-z0-9_-]+\.py$')]
    [string]$Tool,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArguments
)
$ErrorActionPreference = 'Stop'
$arisProjectRoot = Split-Path -Parent $PSScriptRoot
$arisPython = Join-Path $arisProjectRoot '.conda/python.exe'
$arisToolPath = Join-Path $arisProjectRoot ('ARIS/tools/' + $Tool)
if (-not (Test-Path -LiteralPath $arisPython -PathType Leaf)) {
    throw 'The project Conda environment is missing. See DEPLOYMENT.md.'
}
if (-not (Test-Path -LiteralPath $arisToolPath -PathType Leaf)) {
    throw "ARIS helper not found: $Tool"
}
Push-Location $arisProjectRoot
try {
    & $arisPython -B -X utf8 $arisToolPath @ToolArguments
    if ($LASTEXITCODE -ne 0) { throw "ARIS helper exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}
