# Builds the preview of the book written so far and serves it at http://127.0.0.1:<Port>/strata-engine-docs/
# (PREVIEW.md). .\scripts\preview.ps1 [-ServeOnly] [-Port 4329] [-Tools <the clone's .tools>]
param([switch]$ServeOnly, [int]$Port = 4329, [string]$Tools = 'G:\GameEngineAI\.worktrees\strata-engine-docs\.tools')
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
. (Join-Path $Tools 'env.ps1')
if (-not $env:PYTHON) { $env:PYTHON = 'C:\msys64\mingw64\bin\python.exe' }
$env:DOCS_PREVIEW = '1'
$env:DOCS_PREVIEW_OMIT = (Get-Content scripts\preview-omit.txt | Where-Object { $_.Trim() -and -not $_.StartsWith('#') }) -join ','
if (-not $ServeOnly) {
	# The written pages into the sidebar, the outline's data and the diagrams' drawings, for this build only: the tree
	# is put back afterwards, so that the next git merge book/write finds it clean.
	try {
		& $env:PYTHON -I scripts/preview-sidebar.py .
		if ($LASTEXITCODE) { throw 'preview-sidebar.py failed' }
		npm run diagrams
		if ($LASTEXITCODE) { throw 'npm run diagrams failed' }
		npm run build
		if ($LASTEXITCODE) { throw 'the build failed: node scripts/preview-scan.mjs lists every page problem' }
	} finally {
		git checkout -q -- src/sidebar.json src/generated/outline.json src/generated/diagrams
		git clean -fq -- src/generated/diagrams
	}
}
node scripts/serve.mjs --port $Port
