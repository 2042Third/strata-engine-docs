# Status of the edition (2026-11-25, pin v0.8.0, 319075e3)

## Pages

All 335 outline pages and the 34 part pages are `status: final`. Each page has its part review (335 of 335) and
passes `tools/pagecheck.py`; the final walks of tracks G and E were answered and confirmed.

## Checks

Release build of 768efd13 (`book-v0.8.0-r3`; its tree is that of the published commit 47dcdd8c). Passing, with
`--release` where it applies: pages, outline, notices A to C, typos, markdownlint, actionlint, both unit suites, the
lint, quotes, sketches (`CXX` and `--slangc` as full paths), figures, tutorials, the reference, names, `pin.py
report`, diagrams, drawings. The builds at `/`, `/x/y` and `/strata-engine-docs` with gate (a); gates (a), (b) and
(c) through nginx 1.30.6 and 1.20.1; keyboard; Lighthouse accessibility 100. Axe: 791 of 792 page-themes; the one,
`print/editor-ui/` (a link with text reported as empty), flakes: reruns of every print view pass; r2's page flakes
alike.

Check 12: 0 of 12 budgets over (R59, R60). Site 398.8 MB, largest page 177.2 KB gzip, search index 11.7 MB, peak
memory 3,700 MB; the crawl took 119.1 s (recorded). Check 11: first query 207.4 KB, next 91.9 KB; 55 of 60 queries.

Open:

- row 14 on this machine: `image/spatial-aa` performance 79, LCP 4.2 s;
- the axe flake on the large print views.

## Figures

550 recipes; 45 made by no take at the pin keep `waitsFor` (32, for 30 tier 3 requests) or `blocked` (13), and
their pages show stand-ins (R55).

## Release

`book-v0.8.0-r3` in `docs-work/release/out/book-v0.8.0-r3/`, replacing r2: site (266.8 MB), deploy folder,
`SHA256SUMS`, PNG originals (588.5 MB) with their `.sha256`, and a copy of `deploy/README.md`. No token or path of
this machine's user folders ships; the only e-mail addresses are Pagefind's translators' and `you@example.com`.

## Repository

The book is on GitHub as `ci/site` (47dcdd8c); `main` there is still the repository's first commit. CI of 47dcdd8c
fails: on Linux `sketches/draw-batching-passes.cpp` converts its lambda to `uint64_t (*)(uint32_t)` only where
`uint64_t` is `unsigned long long`, two sketch fences differ, and a unit suite fails. `main` moves by fast-forward once
CI is green (R56).

## For a later edition

- The 30 tier 3 requests and the 13 blocked figures.
- Engine findings (`## Engine` of the notes): `play.step` ignores the time scale; `script.create {open: true}`
  without an external editor; `asset.moveFolder` during imports; where `asset.import` puts a model; `world.status`
  cells and entity counts; `editor.status` offers `automation` under `--no-automation`.
