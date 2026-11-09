param([switch]$Render)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$paper = Join-Path $root 'paper'
$engine = 'D:/Electronic/Latex/MikTeX/miktex/bin/x64/pdflatex.exe'
$bib = 'D:/Electronic/Latex/MikTeX/miktex/bin/x64/bibtex.exe'
$style = Join-Path $root 'templates/upstream/cvpr2026'
foreach ($name in @('cvpr.sty','ieeenat_fullname.bst')) {
    if (!(Test-Path -LiteralPath (Join-Path $paper $name))) {
        Copy-Item -LiteralPath (Join-Path $style $name) -Destination $paper
    }
}
$include = Get-ChildItem -LiteralPath (Join-Path $root 'third_party/texmf/tex') -Recurse -Directory |
    ForEach-Object { '-include-directory=' + $_.FullName }
$texArgs = @('--disable-installer','--disable-write18','-interaction=nonstopmode','-halt-on-error') + $include + @('main.tex')
Push-Location -LiteralPath $paper
try {
    & $engine @texArgs *> compile-pass1.log
    if ($LASTEXITCODE -ne 0) { Get-Content compile-pass1.log -Tail 25; throw 'First LaTeX pass failed' }
    & $bib --disable-installer main *> compile-bibtex.log
    if ($LASTEXITCODE -ne 0) { Get-Content compile-bibtex.log -Tail 25; throw 'BibTeX failed' }
    & $engine @texArgs *> compile-pass2.log
    if ($LASTEXITCODE -ne 0) { Get-Content compile-pass2.log -Tail 25; throw 'Second LaTeX pass failed' }
    & $engine @texArgs *> compile-pass3.log
    if ($LASTEXITCODE -ne 0) { Get-Content compile-pass3.log -Tail 25; throw 'Final LaTeX pass failed' }
    Get-Content compile-pass3.log -Tail 12
    if ($Render) {
        $preview = Join-Path $paper 'preview'
        New-Item -ItemType Directory -Force -Path $preview | Out-Null
        Get-ChildItem -LiteralPath $preview -Filter 'page-*.png' -File | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName
        }
        & pdftoppm -scale-to 1500 -png main.pdf (Join-Path $preview 'page')
        if ($LASTEXITCODE -ne 0) { throw 'PDF rendering failed' }
    }
} finally { Pop-Location }
