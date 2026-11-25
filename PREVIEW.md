# Preview of the book written so far

Branch `site/preview` (worktree `G:/GameEngineAI/.worktrees/docs-site`) is `book/write` merged with the site's `main`,
built as a draft with two preview-only settings: `DOCS_PREVIEW=1` draws a link to a page not written yet as plain
text, and `DOCS_PREVIEW_OMIT` leaves out the pages listed in `scripts/preview-omit.txt`.

## Start it

PowerShell: `.\scripts\preview.ps1`

Git Bash: `./scripts/preview.sh`

Then read <http://127.0.0.1:4329/strata-engine-docs/>. Ctrl+C stops the server. `-ServeOnly` (or `--serve-only`)
serves the last build without building; `-Port` (or `PORT=`) picks another port.

## Rebuild after more pages land

```sh
git merge book/write
./scripts/preview.sh        # or .\scripts\preview.ps1
```

The script lists the written pages in the sidebar, draws new diagrams and builds, then puts those generated files
back, so the next merge finds a clean tree. Where a merge conflicts in a page, take the writers' version
(`git checkout --theirs <page>`). When the build fails on a page, `node scripts/preview-scan.mjs` lists every page's
problems in one run; add a page that cannot be mended in one line to `scripts/preview-omit.txt`.

`node_modules` is a copy of the clone's (the G: drive is exFAT, which has no junctions).

## What is unfinished

- Five pages are left out (`scripts/preview-omit.txt`): missing checkpoints, a missing worked example, a text figure
  drawn as a picture.
- No picture is taken yet: every figure shows its placeholder.
- Links to unwritten pages are plain text.
- `pseudocode` fences are not highlighted.
