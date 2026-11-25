# Rulings 5: the planner's read of the first spike

The first spike finished on 2026-11-10. It built the whole web project against the plan as it stood before the
critique, two independent verifiers read it (32 findings, 31 fixed), and it measured a book of 300 pages, 1.26 million
words, 1,500 quotes of the engine at `822a7a46`, 400 diagrams and 600 pictures on the authoring machine, under
`Tools/PerfLock.py`. Its report is `plan/spike-report-1.md`; the last measurements are those of its fixing stage and
are the ones below.

The plan changed while the spike ran: `site.md` "The spike against this file" lists 14 changes the spike does not
have. So the verdict comes in two steps. This file gives the first, the verdict on the framework, and rules on what
the spike found. The second is the completed site's report (`process.md`, order step 4), which measures every row.

Where this file differs from `site.md`, `style.md` or `process.md` as committed before it, this file wins; the three
files are changed with it.

## R12 — The framework passes; the fallback is not built

Astro Starlight carries a book of this size with room to spare. Every row of `site.md`'s budget table that the first
spike could measure is inside its pass mark, with one exception that R13 withdraws:

| Row | Measure | Pass mark | Measured | |
| --- | --- | --- | --- | --- |
| 1 | Warm full build, i7-13700K | ≤ 4 min | 46.5 s and 47.0 s | pass |
| 5 | Rebuild after editing one page | ≤ 90 s | 49.0 s (69.9 to 75.4 s when every page renders again) | pass |
| 7 | Peak memory of the build | ≤ 4 GB | 3.1 to 3.2 GB | pass |
| 9 | `dist/`: size; files | ≤ 400 MB; ≤ 15,000 | 359.8 MB; 3,207 | pass |
| 9 | HTML, CSS and scripts | ≤ 80 MB | 157 MB (chapter pages 91.4, print views 64.2, assets 1.8) | withdrawn (R13) |
| 10 | Largest page; median page | ≤ 300 KB; ≤ 60 KB (brotli) | 121.7 KB; 44 KB (gzip, so brotli is smaller); the sidebar is 74 KB of every page, 9.9 KB gzipped | pass |
| 12 | Search, first two-word query | ≤ 300 KB | 176.6 to 223.8 KB | pass |
| 17 | Base portability | three bases pass the crawl | `/`, `/strata-engine-docs` and `/x/y` crawl clean (2,817 requests, 0 problems); nginx 1.30.6 and Caddy 2.11.9 pass at all three | pass on Windows |
| 20 | Confirm items 1, 2, 4, 5 | confirmed | line marks land on the engine's lines; `std::vector` and `a:b` stay text; a formula KaTeX cannot render fails the build; Mermaid fences reach the book's step first | confirmed |

No confirm item needed a fork of Astro or Starlight. The risks the research named were verified or answered
(`plan/spike-report-1.md` §3).

Not measured yet, because the thing to measure is not built or needs `ubuntu-latest`: rows 2, 3, 4, 6, 8, 11, the
second query of 12, 13, 14, 15 on every page, 16, 18, 19 and confirm items 3 and 6 to 13.

What follows:

- The fallback is not built. The book's markup, front matter and directives are those of `style.md` and `site.md`.
- The site builder completes the site (the 14 changes), builds the scale test from the outline's 332 rows, measures
  every row and writes the report. A row that fails after its remedy is the planner's to rule on.
- The allocation and the part briefs do not wait.
- The pilot's seven pages wait for the completed site's report, because a writer needs the directives, the front
  matter checks and the linter of `style.md`. If a row is still open then, a row about the content model or the build
  holds the pilot back; a row about deployment or CI does not.

## R13 — Row 9 loses its limit on HTML

"HTML, CSS and scripts ≤ 80 MB" was written before anything was measured, and it contradicts row 10. Row 10 lets the
median page be 60 KB after brotli, which is at least 400 KB of HTML; 332 such pages are 130 MB without a single print
view. The print views repeat every page once more by design.

What the limit was for is guarded elsewhere: a reader's cost by rows 10, 11 and 12, per page; the deployment's size
by the total of row 9. So row 9 reads: `dist/` ≤ 400 MB; ≤ 15,000 files; and the size of the chapter pages' HTML and
of the print views' HTML are each recorded. Both recorded sizes get a regression budget (R14), so growth is still
seen. Their remedy, when one is needed, is the sidebar's markup, which is 74 KB of every page.

## R14 — Pass marks and regression budgets

`site.md`'s table holds the pass marks. They are the design's, and no measurement changes them; only a ruling does.

`tools/budgets.json` holds regression budgets, which CI enforces. Each is the smaller of the table's pass mark and
1.5 times the latest full-scale measurement, rounded up to two digits. So in the completed site: the site's size is
400 MB, not 540; peak memory is 4 GB, not 4,800 MB. A budget goes down whenever a measurement allows it. It goes up
only by a ruling of the planner that names what grew.

Times and other load. A time is measured under `Tools/PerfLock.py`, but engine builds may run beside it. A time that
passes its mark although other work loaded the machine passes, because load only makes it slower. A time over its
mark while the load was above `quiet_other_load` is not judged: the row stays open and is measured again. The report
never counts "not judged" as a pass.

## R15 — AVIF effort

`site.md` named quality and chroma but not effort. Measured on 1920-pixel pictures: effort 4 takes 3.8 s a picture,
effort 2 takes 0.39 s and makes files about 15 % larger; a cold build at effort 4 took 26 minutes, at effort 2 under
three.

- **Published files** (`scripts/encode-figures.mjs`, encoded once, committed, served unchanged): effort 4.
- **Derived files** (the 960-pixel AVIF, and the 1920 one of a 3840 capture, made in a cold build): effort 2.

The tool builder encodes the twelve sample screenshots at quality 80 with efforts 4 and 6 and reports sizes and
times. The planner may change the published effort once, before the first picture of phase B is published. The stamp
records the effort with the other encoder settings.

## R16 — CI runs on `ci/<name>` branches, and `main` moves when it is green

Rows 2, 3, 8 and 14 to 17 need `ubuntu-latest`, and the container image is tested only there. Nothing has been
pushed yet, and no pull request can be opened from the authoring machine. So, as in the engine's repository:

- `book.yml` also runs on pushes to branches named `ci/<name>`.
- Before page work, the site builder pushes the branch `ci/site` to run CI and reads the result from GitHub's public
  API without a token (`tools/cistatus.py`, modelled on the engine's `Tools/CIStatus.py`). It adds commits and pushes
  again until CI is green. It never pushes `main` and never forces a push.
- The planner moves `main` (a fast-forward push, never forced over the owner's first commit) when `ci/site` is green
  and the report is read. `main` never receives a commit whose CI is red.
- During page work the integrator pushes, as `process.md` says. It may push a batch to `ci/<name>` first.

The steps that fail a job write their reason as an annotation (`::error`), so that it can be read without a token;
job logs cannot.

## R17 — What the spike found in the plan

| Finding | Ruling |
| --- | --- |
| `title: Time: delta time, …` is not valid YAML | Already quoted in `style.md` §6.1. The rule is now general: `title` and `description` are always written in double quotes, and `tools/pages.py check` names the page and the line of front matter that is not valid YAML or breaks this rule. |
| The outline's title "Just enough C++ for game scripts" uses a banned word | The page left the outline in the revision. `check_outline.py`'s move into `tools/booklib/outline.py` (R11) adds the check: no title holds a word of `style.md`'s `banned-word` list. |
| A Mermaid participant named `Loop` is read as the keyword | `style.md` §11: a name in a diagram that is a Mermaid keyword (`loop`, `end`, `alt`, `opt`, `par`, `note`, `class`, `state`, `graph`, `subgraph`) is given an alias (`participant L as Loop`) or quoted. The renderer's failure names the page and the line. |
| `style.md` §11 still says site.md asks for `accTitle` and `accDescr` | Stale since R10. A fence carries `caption="…"` and `alt="…"` (`site.md`, "Diagrams"). |
| The page id `draw/lod` fails the spelling gate | `_typos.toml` knows `lod`. Words of page ids and engine names enter `_typos.toml`; the tool builder generates that list from the outline and `tools/names.py`'s names, so no writer meets the gate for an id. |
| MSYS2's git expands braces (`<commit>^{commit}`) | Tools write `<commit>~0`. No file of the plan uses the brace form. |
| nginx on Windows leaves its worker running; Caddy answers an empty 200 outside its routes and has no type for `.webmanifest` | `tools/servertest.py` ends the whole process tree. The Caddyfile sets the manifest's type. Gate (c)'s row "a path outside the prefix: not the book's 404 page" already allows Caddy's answer. |
| Expressive Code's line numbers and Mermaid's dark edge labels were below 4.5:1 | Fixed in the spike; both overrides stay (R10). |

## R18 — The "(spike)" marks

A "(spike)" mark in `site.md`, `style.md` or `pipelines.md` says that a name or a version comes from the working
spike. The first spike confirmed its pinned versions and names (`plan/spike-report-1.md` §1 and §3). The completed
site's report lists every mark with its line and says whether the built site matches it. The planner then removes the
marks that hold and rewrites the lines that differ.

## R19 — No hold of the perf lock longer than 25 minutes while engine agents work

`Tools/PerfLock.py` waits 30 minutes for the lock and then fails (exit 75), and ends a command after 25 minutes
unless `--limit` says otherwise. The engine's agents rely on both defaults. `pipelines.md` gave the pin build
`--limit 180` and the tools 90 minutes; one such hold would fail every perf run an engine agent starts meanwhile.

- While engine agents work (all of phase A, and in phase B whenever the planner says one is running), every hold of
  the book's keeps PerfLock's default limit and is planned for 20 minutes at most. The book's own runs wait longer
  for the lock: `--wait 120`.
- The pin build makes only the programs the tools start (`StrataEditor`, `StrataCLI`, `StrataRuntime`), not the
  engine's tests, and runs in slices, each its own hold: the configure step, the third-party libraries, the engine's
  libraries, then each program. A slice the limit ended is run again; the build is incremental.
- A tool that would run longer (`reference.py dump`, `tutorials.py run` over many pages, the scale test's
  measurements) is run section by section or page by page, one hold each.
- The long limits of `pipelines.md` (90 and 180 minutes) are for phase B, when no engine agent measures.
