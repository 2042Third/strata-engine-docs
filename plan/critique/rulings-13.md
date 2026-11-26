# Rulings 13: the released book's size

Written after the release `book-v0.8.0-r1` (2026-11-25), whose checks failed check 12: the site was 491.3 MB against
budget row 9's pass mark of 400 MB, and five regression budgets of `tools/budgets.json` were exceeded. The planner
approved R59 and ruled R60 on 2026-11-25, before the first push. Where this file differs from an earlier file, this file wins.

## R59 — What the 491 MB was made of, what the remedies took out, and the budgets the real book needs

**Measured composition before** (the release build at `/strata-engine-docs`, `tools/crawl.py`'s apparent sizes before
precompression, 2026-11-25):

| Kind | Size | What it is |
| --- | --- | --- |
| Pictures, lossless WebP | 160.8 MB, 384 files | 150 scene renders that their recipes publish lossless (125.2 MB, 6 of them 3840 wide at 7.3 MB each), 181 editor pictures (22.3 MB), 8 live captures (9.6 MB), crops; 13 files published twice with the same bytes (10.6 MB) |
| Chapter HTML | 143.8 MB, 371 pages | code blocks 42.4 MB (their token spans 35 MB), the sidebar 32.5 MB (88 KB on every page), diagrams 25.6 MB (two themes each), heading links 5.2 MB (a 500-byte inline icon per heading) |
| Print views' HTML | 107.3 MB, 25 views | the chapters again: code blocks 42.4 MB, diagrams 33.5 MB, heading links 5.3 MB |
| Downloads | 59.6 MB, 377 files | 193 stage and solution zips; 58.0 MB of their members are files that other zips hold too (one 954 KB sky HDR of the `basic3d` template in 38 zips, the Metal032 textures in 49), 2.2 MB unique |
| Search index | 11.7 MB, 535 files | Pagefind over 1.92 million words of prose (the spike's book had 1.38 million) and 3,146 code blocks |
| Pictures, AVIF | 6.3 MB, 226 files | renders published lossy and their 960-pixel derivations |
| Fonts | 1.6 MB, 79 files | KaTeX's 20 fonts as WOFF2, WOFF and TrueType; the three text fonts as WOFF2 |

What grew against the spike: the spike's 600 pictures were 450 AVIF renders, 100 crops and 50 interface pictures; the
book publishes 150 renders lossless at 1920 or 3840 pixels because they exist to show pixels (aliasing, noise,
banding, sharpness: `site.md`, "Pictures"), 125 MB that the spike counted at about a tenth. The spike had no
downloads; the book has 59 MB of them. The book's prose is 39 % longer than the spike's fake pages, and its search
index 38 % larger.

**Remedies applied** (each keeps the pages' content as it was; the release's checks pass after them: gates (a), (b)
and (c) through nginx 1.30.6 and 1.20.1, axe on all 396 pages in both themes, the keyboard, the figures, lint and
notices checks, `npm test` and the tools suite):

1. Pictures with the same bytes are served once, under the name of the first in path order (`src/lib/images.mjs`,
   `servedAs`): 10.6 MB. `site.md`'s "Served names" says so.
2. Editor pictures that are mostly the engine's image are published as AVIF at quality 90, chroma 4:4:4, encoded from
   their PNG originals: 90 recipes, 94 pictures, 20.2 MB to 5.0 MB. A recipe qualifies when its AVIF is at most half its
   lossless file; side-by-sides at 1:1 of the chips strip, the Stats overlay's small monospaced text, a game HUD, the
   recovery dialog and a settings panel show the text as sharp as the lossless file. Pictures that are mostly
   interface stay lossless: there AVIF is as large or larger. Crops stay lossless WebP. `site.md` and `pipelines.md`
   §5.7 say that an editor or tool picture is lossless unless its recipe says `publish: "lossy"`; `tools/figures.py`
   encodes those at quality 90 (`c_InterfaceQuality`). Lossless WebP at effort 6 instead of 4 was measured too: 0 to
   2 % smaller, some files larger, so the encoder setting stays.
3. The sidebar (`src/components/Sidebar.astro`, `SidebarList.astro`): Starlight's own persister and markup, without a
   scoped class on every element, with the caret drawn by the style sheet and links relative to the page: 88 KB to
   37.5 KB on every page. Groups still open and close, and the reader's open groups still persist from page to page.
4. Diagrams are inlined without what they never paint with (`compactDrawing`): style rules whose selectors need a
   class or id the drawing lacks, unused keyframes and markers, data attributes no selector reads. The committed
   drawings are unchanged; all 950 rasterize to identical pixels before and after (librsvg). 35 % of their bytes.
5. Code blocks leave out the token spans whose colors are the themes' code foreground (`src/lib/ec-compact.mjs`):
   about half of all tokens. No visible text of any code line stood outside a token span, so the print style sheet
   prints the plain text in the color those spans printed (`#403f53`).
6. The heading links' icon is drawn once per page and used by every other link (`<use>`).
7. KaTeX's fonts are served as WOFF2 only (every browser that shows AVIF loads WOFF2): 0.8 MB.

**Measured after** (the same build, 2026-11-25, reference machine): site 398.2 MB and 1,962 files (row 9 passes);
chapter HTML 102.3 MB (budget 140), print views 82.1 MB (budget 97); median page 42.8 KB gzip; the sidebar 37.5 KB.

**Not applied, because the reader would lose something:** publishing the lossless renders lossy (their recipes say
lossless because a lossy encoder smears what they show); rounding the diagrams' coordinates (0.9 MB; it moves edge
pixels by up to a full level); stage zips that leave out the files another zip or the template holds (a stage zip is
a whole project a reader opens to catch up); dropping the copy buttons or the anchor links from the print views.

**What still exceeds, and the budgets the real book needs.** Each new budget is the measurement plus at most 10 per
cent, and within `tools/budgets.py`'s ceiling (the smaller of the pass mark and 1.5 times the measurement); the
pass marks of `site.md`'s table do not change.

| Budget | Was | Measured | New | What grew |
| --- | --- | --- | --- | --- |
| `largest_page_gzip_kilobytes` (row 10; pass mark 300) | 170 | 177.2 (`gpu/text`) | 190 | one diagram of the font pipeline drawn in Mermaid's hand-drawn look: 235 KB per theme, 142 KB of the page's 181 KB gzipped; its paths are curves at 15 digits, which only a change of the diagram's text (the classic look) or rounding (which moves pixels) would shrink |
| `largest_page_kilobytes` (no pass mark) | 770 | 1,546.8 (`reference/commands`) | 1,700 | the generated reference of every editor command with its full parameter schema, 1.55 MB raw but 136 KB gzipped; row 10's remedy, splitting the generated reference, makes one page of the reference many, which changes the book's pages |
| `search_index_megabytes` (no pass mark) | 9.5 | 11.7 | 12.5 | the prose: 1.92 million words against the spike's 1.38 million (+39 %), the index +38 %; leaving code out of the index would lose the whole names that confirm item 9 requires search to find |

`tools/budgets.json` takes these three budgets and their measurements in its `measured` block, with this ruling named
in its comment (`ruling_13_comment`); every other budget and measurement stays the scale test's, and all are within
`tools/budgets.py --check-file`'s ceilings. Two couplings for the planner: `tools/reference.py render` splits the
commands table by the largest page's budget, from an estimate that puts the built page under 770 KB while it builds to
1,547 KB; with 1,700 KB the render still does not split it, and if the planner prefers row 10's remedy, the budget
stays 770 KB and the estimate (`tools/booklib/tables.py`, fitted with the old 74 KB sidebar) is fitted again, which
turns one reference page into one page per command group.

**Not ruled: the crawl's time.** `crawl_seconds` (budget 48 s, no pass mark) measured 116.6 s with lychee, as CI and
the release run it, and 95.5 s without it, on a quiet machine (other load 1.26). The budget was set from the spike's
staged crawl without lychee (31 to 37 s), while CI times the crawl with lychee, so the two never measured the same
thing. And the crawl's time is not explained by the book's size: it made 1,428 requests against the spike's 2,816,
over a similar volume of HTML (184 MB against the spike's 194 MB), and a profile shows `tools/crawl.py` spending most
of its time in Python's `html.parser` (3 million start tags handled). That is the tool's cost, not something the book
grew, and a ruling about content cannot justify it: the budget is left as it is, over, for the planner to decide
between a budget for the crawl CI runs (with lychee) and a faster crawl.

**Peak memory**, which passed: full renders of the final code peaked at 3,761 and 3,993 MB (two bases); one earlier
sample, with a deep copy of every heading's icon that the final code no longer makes, reached 4,323 MB. Row 7's
budget of 4,096 MB stays.

**The planner's approval (2026-11-25).** R59 stands as written: the remedies took out what the reader does not need,
and what remains is the book's real content. The three budgets are approved. `reference/commands` stays one page (a
reader looks a command up on it; it is 136 KB gzipped, under row 10's pass mark of 300): the split by row 10's remedy is
not wanted. `tools/booklib/tables.py`'s size estimate, which puts that page at under 770 KB while it builds to
1,547 KB, is fitted again to the current markup, so that the estimate and the build agree when the reference grows.

## R60 — The crawl's time is recorded, not judged

The crawl's budget (48 s) was set from the spike's crawl without lychee, while CI and the release time the crawl with
lychee: the budget never measured what it judges, and the book did not grow into it (R59: fewer requests than the
spike, a similar volume of HTML). The time is the tool's own cost, most of it in Python's `html.parser`. Until the
crawl is made faster, `crawl_seconds` is recorded with every run as CI runs it (lychee included), on the machine that
ran it, and is not judged: `tools/budgets.py` prints it as a measurement without a limit and never fails or holds a
run on it. A faster crawl is later work; its first measurements on the reference machine and on `ubuntu-latest` then
set a budget per machine, by a ruling.

## R61 — Row 7 passes by its own remedy at 6 GB

Budget row 7 of `site.md` reads: peak memory of the build's process tree, on both machines, at most 4 GB; remedy:
set `--max-old-space-size`, "then ≤ 6 GB passes, with the value written into `package.json`'s build script". The
remedy is applied: the build script runs `node --max-old-space-size=4096 …/astro.mjs build`, and CI's measured step
runs the same command. The real book's cold builds then peak at 4,276.7 MB and 4,828.0 MB on `ubuntu-latest` and at
4,051.6 MiB on the reference machine, all in the Node process and above its heap (native memory: images, the content
store), with Pagefind at 711.8 MB on its own. So row 7's pass mark is 6,144 MiB, as its row says, and
`tools/budgets.json` takes it; the regression budget follows the rule of "Pass marks and budgets": the smaller of
6,144 and 1.5 times the latest full-scale measurement, which is now the real book's (the committed measurements were
the scale test's of 2026-11-11 and are replaced by the book's). This changes no pass mark: it reads the row as
written. A build that passes 6 GB fails, and its remedy is work on the build's memory.
