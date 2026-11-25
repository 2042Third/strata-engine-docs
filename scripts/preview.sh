#!/usr/bin/env bash
# Builds the preview of the book written so far and serves it at http://127.0.0.1:$PORT/strata-engine-docs/ (PREVIEW.md).
# ./scripts/preview.sh [--serve-only]; PORT (4329), TOOLS (the clone's .tools) and PYTHON may be set.
set -euo pipefail
cd "$(dirname "$0")/.."
TOOLS="${TOOLS:-/g/GameEngineAI/.worktrees/strata-engine-docs/.tools}"
. "$TOOLS/env.sh"
export PYTHON="${PYTHON:-C:/msys64/mingw64/bin/python.exe}"
export DOCS_PREVIEW=1
DOCS_PREVIEW_OMIT="$(grep -v -e '^#' -e '^[[:space:]]*$' scripts/preview-omit.txt | paste -sd, -)"
export DOCS_PREVIEW_OMIT
if [ "${1:-}" != "--serve-only" ]; then
	# The written pages into the sidebar, the outline's data and the diagrams' drawings, for this build only: the tree
	# is put back afterwards, so that the next git merge book/write finds it clean.
	restore() {
		git checkout -q -- src/sidebar.json src/generated/outline.json src/generated/diagrams
		git clean -fq -- src/generated/diagrams
	}
	trap restore EXIT
	"$PYTHON" -I scripts/preview-sidebar.py .
	npm run diagrams
	npm run build || { echo 'preview: the build failed; node scripts/preview-scan.mjs lists every page problem' >&2; exit 1; }
	restore
	trap - EXIT
fi
node scripts/serve.mjs --port "${PORT:-4329}"
