[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$arisProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $arisProjectRoot
try {
    $arisManifest = Get-Content '.aris/installed-skills-codex.txt' -Encoding UTF8
    $arisSkillRows = @($arisManifest | Where-Object { $_.StartsWith("skill`t") })
    if ($arisSkillRows.Count -ne 33) { throw "Expected 33 skills, found $($arisSkillRows.Count)" }
    foreach ($arisRow in $arisSkillRows) {
        $arisFields = $arisRow.Split("`t")
        if (-not (Test-Path -LiteralPath (Join-Path $arisFields[3] 'SKILL.md') -PathType Leaf)) {
            throw "Missing skill: $($arisFields[1])"
        }
    }
    & './.conda/python.exe' -B -X utf8 -c "import pathlib,sys; assert pathlib.Path(sys.prefix).resolve() == pathlib.Path('.conda').resolve(); print('CONDA_INTERPRETER_OK',sys.version.split()[0])"
    if ($LASTEXITCODE -ne 0) { throw 'Conda interpreter validation failed' }
    & './scripts/Invoke-ArisTool.ps1' research_wiki.py stats research-wiki
    if (-not (Test-Path -LiteralPath 'research-wiki/papers/bourtsoulatze2019_deep_joint_sourcechannel.md')) {
        throw 'Seed paper is missing'
    }
    if (-not (Test-Path -LiteralPath 'research-wiki/query_pack.md')) { throw 'Query pack is missing' }
    $arisPaperCount = @(Get-ChildItem -LiteralPath 'research-wiki/papers' -Filter '*.md' -File).Count
    Write-Output "ARIS_DEPLOYMENT_SMOKE_PASS skills=33 papers=$arisPaperCount scope=bootstrap_only"
} finally {
    Pop-Location
}
