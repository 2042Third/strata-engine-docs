# Status of the edition (2026-11-25, pin v0.8.0, 319075e3)

## Pages

All 335 outline pages and the 34 part pages are `status: final`. Each page has its part review (335 of 335) and
passes `tools/pagecheck.py`; the final walks of tracks G and E were answered and confirmed.

## Checks

Release build of 6dc9885f (`book-v0.8.0-r2`). Passing, with `--release` where it applies: pages, outline, notices A
to C, typos, markdownlint, actionlint, both unit suites, the lint, quotes, sketches (`CXX` and `--slangc` as full
paths: not on this shell's PATH), figures, tutorials, the reference, names, `pin.py report`, diagrams,
drawings. The builds at `/`, `/x/y` and `/strata-engine-docs` with gate (a); gates (a), (b) and (c) through nginx
1.30.6 and 1.20.1 (copied, container, hostile, proxy, with and without host headers); axe on 396 pages in both
themes; keyboard; Lighthouse accessibility 100.

Check 12, budgets as committed (R59 still a draft): 0 of 15 over. Site 398.8 MB (row 9: 400), chapter
HTML 102.5 MB, print views 82.4 MB, largest page 177.2 KB gzip and 1,547 KB raw, search index 11.7 MB, peak memory
3,732 MB. Check 11: first query 207.4 KB, next 91.9 KB (row 12: 300, 100); 55 of 60 queries (row 13: 54).

Open:

- the crawl took 117.8 s against 48 s, not judged (other load 2.5); for the planner (R59);
- row 14 on this machine: `image/spatial-aa` performance 79, LCP 4.5 s (CI's runner is row 14's machine).

## Figures

550 recipes; 45 made by no take at the pin keep `waitsFor` (32, for 30 tier 3 requests) or `blocked` (13), and
their pages show stand-ins (R55).

## Release

`book-v0.8.0-r2` in `docs-work/release/out/book-v0.8.0-r2/`, replacing r1: site (266.8 MB), deploy folder,
`SHA256SUMS`, PNG originals (588.5 MB) with their `.sha256`, and a copy of `deploy/README.md`. No token or path of
this machine's user folders ships; the only e-mail addresses are Pagefind's translators' and `you@example.com`.

## Repository

Local `main` is at 90d8017d (r1), behind `book/write`; nothing is pushed. A push needs a credential that may write
contents and workflows: first `ci/site`, then `main` by fast-forward once its CI is green (R56).

## For a later edition

- The 30 tier 3 requests and the 13 blocked figures.
- Engine findings (`## Engine` of the notes): `play.step` ignores the time scale; `script.create {open: true}`
  without an external editor; `asset.moveFolder` during imports; where `asset.import` puts a model; `world.status`
  cells and entity counts; `editor.status` offers `automation` under `--no-automation`.
