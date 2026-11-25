# CI

## How CI is read

`book.yml` runs on every pushed branch and tag, on pull requests and by hand (R27). Its last job, `report`, commits
`runs/<commit>-<attempt>.json` to the branch `ci-results`: every job's conclusion, its failed steps and every
`::error` annotation (R25). Read it with `python -I tools/cistatus.py <commit>` (git alone, no token): exit 0
green, 1 failed, 3 no record yet. `links.yml` runs weekly and by hand only.

## The jobs

- `lint`: front matter, outline, sidebar, page shape, the notices of what the site ships, spelling, Markdown and the
  workflows, the budgets' rule, the search queries' file, the unit tests of the build and the tools.
- `excerpts`: the engine at the pin, the language lint, quotes, sketches, figures, tutorials, the generated reference
  and names.
- `build` (after `lint`): three builds (root, `/x/y`, `/strata-engine-docs`) with gate (a), diagrams and drawings,
  the notices of the built site, the budgets.
- `serve-test` (after `build`): nginx, the container, gates (a) to (c), search, axe, keyboard, Lighthouse.
- `release`: on `book-v*` tags only. `report`: always, except on pull requests.

## What a draft branch is exempt from

Only a `book-v*` tag runs the checks with `--release` (`RELEASE_TAG` in `book.yml`). On any other ref, pictures not
taken yet, placeholders, missing stamps and stale or missing generated files are notes, not errors
(pipelines.md, the `--release` lines of figures, tutorials and names, and §13). No check a draft can pass is skipped.

## State left (2026-11-17)

The scan of origin/main..00a65d0c (tree and every commit's patch: tokens, e-mail addresses, user-folder paths)
found nothing; LICENSE and the footer are in the tree. Pushing `ci/site` failed with 403 ("Permission ... denied"):
the stored credential cannot write here. Nothing is pushed, CI never ran, `main` is GitHub's first commit.
