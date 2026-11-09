$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$engine = 'D:/Electronic/Latex/MikTeX/miktex/bin/x64/pdflatex.exe'
$source = Join-Path $root 'templates/upstream/cvpr2026'
$output = Join-Path $root '_work/cvpr-template-check'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$include = Get-ChildItem -LiteralPath (Join-Path $root 'third_party/texmf/tex') -Recurse -Directory |
    ForEach-Object { '-include-directory=' + $_.FullName }
$argsTex = @('--disable-installer', '--disable-write18', '-interaction=nonstopmode', '-halt-on-error', "-output-directory=$output") + $include + @('main.tex')
$argsTex | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'logs/cvpr-compile-arguments.json') -Encoding utf8
Push-Location -LiteralPath $source
try {
    & $engine @argsTex *> (Join-Path $root 'logs/cvpr-template-local-compile.log')
    $code = $LASTEXITCODE
} finally { Pop-Location }
Get-Content -LiteralPath (Join-Path $root 'logs/cvpr-template-local-compile.log') -Tail 20
exit $code
