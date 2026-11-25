# Spike report: the machine of The Strata Engine Book

> The first spike's report, kept as it was written on 2026-11-10 against the plan before its critique. The
> planner's verdict on it is `critique/rulings-5.md`. The completed site's report is `spike-report.md`.

Date: 2026-11-10. Repository: strata-engine-docs, local branch main, 15 commits after the plan (not pushed).
Engine pin: 822a7a46. Machine: the reference machine (i7-13700K, 24 threads, 32 GB, Windows 11; the G: volume supports
no junctions or symbolic links). Every full-scale build and the crawl ran under the engine's Tools/PerfLock.py.

The spec was the committed plan (1174579: site.md, pipelines.md, style.md, book.md). Other agents rewrote style.md,
site.md, pipelines.md and the outlines during the work (uncommitted in plan/); see section 6.

## 1. What was built

| Area | Files |
| --- | --- |
| Toolchain | tools/toolchain.json, tools/bootstrap.py (Node 26.13.0, typos 1.52.1, and with --servers nginx 1.30.6 and Caddy 2.11.9 into .tools/, SHA-256 checked; Node also against nodejs.org's SHASUMS256.txt), package.json and package-lock.json with exact pins, .node-version |
| Site | astro.config.mjs (DOCS_BASE, DOCS_SITE, DOCS_RELEASE through src/lib/settings.mjs; trailingSlash always; unified(); sidebar from src/sidebar.json with the 23 parts and three tracks; cacheDir .cache/astro), ec.config.mjs, src/content.config.ts, src/components (PageTitle: breadcrumbs and the top strip; Pagination: track navigation; client/book.js: tabs, slider, tracks), src/styles, src/pages (print view per part, web manifest), public/favicon.svg |
| Plugins | src/plugins: links, excerpts, figures, asides, tabs, answers, glossary (automatic first use and :term marks), strips, navigation (track chooser), mermaid, report, rehype (math guard, bottom strip, code gutters); src/lib (settings, pages index, sidebar and tracks, glossary matcher, figures, images, diagrams); src/integrations/book.mjs (whole-book checks, diagram pre-render, picture encoding, dev server middleware). 52 node:test tests. |
| Tools | tools/excerpts.py (fill, check, relocate, list, symbol form, engine paths in prose), sketches.py, crawl.py, pin.py (show, report, move), lint.py, figures.py (validate, list) with schemas/figure-manifest.schema.json and booklib/jsonschema.py, pages.py, measure.py, budgets.py + budgets.json, servertest.py, booklib/. 42 unittest tests. |
| Checks in Node | scripts/a11y.mjs (axe, both themes), scripts/search-payload.mjs, scripts/serve.mjs |
| Content | five sample pages (start/install how-to, core/time concept, world/interpolation internals, make/first-script tutorial, reference/glossary reference) + landing (track chooser) + 404; 8 quotes of the engine; 2 sketches; 2 diagrams; 1 slider and 2 figures (placeholder pictures from scripts/placeholders.mjs, one recipe unshot); glossary of 19 terms; tutorial command script |
| Deploy | deploy/nginx.conf, deploy/nginx-container.conf, deploy/Caddyfile, deploy/Dockerfile, deploy/README.md, .dockerignore |
| CI | .github/workflows/book.yml (checks, excerpts against the public engine at the pin, build + crawl + a11y + search + budgets + artifact, deployments with nginx, Caddy and the container) |
| Scale | scripts/scale.mjs (writes .tools/scale/site) |

## 2. Measurements at full scale

The generated book: 300 pages (the outline's ids and titles plus extras), 1.25 million words (2,000 to 8,000 per page),
1,500 real quotes of the engine at the pin, 400 Mermaid diagrams (flowcharts, sequences, state diagrams), formulas on 100
pages (about 500 display formulas), 600 synthesized pictures of 1920 x 1080 (noise on gradients: the encoders' worst
case), 200 figure manifests with "taken" hashes, 1,600 glossary terms, tabs, asides, sketches, tutorials. Generating it
takes 70 s.

| Run | Wall time | Peak memory (process tree, 250 ms samples) | Notes |
| --- | --- | --- | --- |
| Cold, AVIF effort 4 | 1,566.8 s | 3,239 MB (Chromium 964, Pagefind 378 at their own peaks) | pictures 1,478 s of it |
| Cold, AVIF effort 2 | 234.2 s | 2,950 MB | pictures 147 s, diagrams 12.9 s, Pagefind 4.2 s |
| Cold, final run | 258.0 s | 2,040 MB | pictures 141 s, diagrams 14.0 s |
| Cached, nothing changed | 46.3 s, 42.6 s | 2,359, 2,714 MB | Astro writing 324 pages is about 35 s |
| One page's prose edited | 47.5 s | 1,867 MB | only that page rendered again; the change is in the output |
| One heading edited | 75.4 s | 2,626 MB | the inputs digest changed, every page rendered again (anchors may have moved) |
| Staged crawl | 31.3 to 37.1 s | 212 MB | 2,816 requests, 323 pages, 619 external links, 0 problems |

Output (final): 876 MB in 3,209 files: pictures 712 MB (2,400 files), chapter pages 91.4 MB (302), print views 64.2 MB
(22), Pagefind 6.5 MB (393 files), scripts and styles 1.8 MB. The published originals (WebP q92) of the noise pictures
are 515 MB; real renders are far smaller (below).

Pages: median chapter page 316 KB (44 KB gzipped); the largest is the glossary of 1,600 terms, 526 KB (116 KB gzipped).
The full sidebar is 74 KB of every page (14 to 18%, 9.9 KB gzipped). Largest print view: the part "Making games",
10.8 MB (1.41 MB gzipped).

Search (Chromium on the staged site, first query, bytes over the wire as nginx and Caddy serve them): "fixed step"
313 KB, "render pass" 232 KB, "shadow cascade" 215 KB, "texture" 210 KB (273 to 376 KB as files). About 95 KB is
Pagefind's script, worker and WebAssembly (loaded once); the rest is index chunks (40 to 90 KB) and the fragments of the
five results (one fragment, the 1,600-term glossary, is 97 KB). Results show kind and part as tags, URLs under the base.

Checks at full scale: pages.py 2.3 s, lint.py 10.6 s, figures.py validate --release 4.4 s, excerpts.py check 73 s and,
after reading through one git cat-file --batch process, 2 s; sketches.py check (compiling) 0.8 s; markdownlint 15.8 s;
typos 0.8 s; a11y 0 serious or critical violations on 6 pages (landing, glossary, the largest page, a page with math,
diagrams and figures, a print view, the 404 page) in both themes. All pass.

Real renders (the engine's Samples/Showcase/Screenshots, 960 x 540, scaled to 1920): published WebP q92 74 to 229 KB;
per 1920-pixel picture AVIF q60 effort 4 3.77 s / 62 KB, effort 2 0.39 s / 71 KB, WebP q85 0.13 s / 92 KB; at 960
pixels AVIF effort 4 0.99 s, effort 2 0.11 s. Hence effort 2 (commit 8e5b397). With real renders the picture share of
the site would be a fraction of the 712 MB measured with noise.

The repository's own book (5 pages): build 38.8 s (cold encode of 3 pictures), peak 776 MB; crawl 116 requests, 0
problems; search 125 KB over the wire.

Proposed budgets of check 9 (tools/budgets.json, about 1.5 x measured): cold build 390 s, cached 70 s, peak memory
4,800 MB, site 1,000 MB, largest page 170 KB gzipped / 770 KB raw, largest print view 2,060 KB gzipped, search index
10 MB, one two-word search 400 KB over the wire, crawl 55 s. Every one holds at full scale (tools/budgets.py: 0 of 9
over, cold and cached). CI applies --slower 2 to the times.

## 3. Risks and "not verified" items of research/framework.md

Verified:
- The pinned versions exist and work together: astro 7.4.8, @astrojs/starlight 0.42.10 (peer @astrojs/markdown-remark
  7.3.6), Expressive Code 0.44.3, pagefind 1.6.0 (Starlight's ^1.5.2 resolves to it; @pagefind/default-ui 1.6.0),
  KaTeX 0.16.47 as the only copy (an override), mermaid-isomorphic 3.1.0 with Playwright 1.65.0 (Mermaid 11.17.2 by
  override), sharp 0.35.5, the fontsource packages.
- Node 26.13.0's SHA-256 sums equal the research's and nodejs.org's SHASUMS256.txt; typos' release does publish digests
  (GitHub's asset digests), now pinned.
- unified() works in Astro 7.4.8; Starlight 0.42 and Expressive Code detect it and append their plugins after the book's,
  so the book's remark plugins see directives and fences first.
- Text-directive restoration under unified(): `std::vector` and `a:b` in prose stay text (smoke build, unit test).
- `<details>` answers work without scripts (axe clean).
- Expressive Code line marks count from the block's first line, not from startLineNumber: the excerpts plugin converts
  the engine's line numbers (mark="L2280" lands on line 2280; screenshot checked).
- Mermaid fences reach the book's remark step before Expressive Code (a rehype plugin).
- Shiki highlights `slang` through the hlsl alias exactly as hlsl; cmake, powershell, cpp, json grammars work.
- Nothing loads from another host: fonts, KaTeX CSS and fonts, scripts and the search are local (the crawl fails on
  any resource of another host).
- Pagefind works under the base path and indexes only data-pagefind-body; result tags for kind and part.
- Starlight 0.42's mobile menu works without scripts (the popover attribute).
- Playwright's Chromium installs into a user folder without administrator rights (--only-shell, 1254).
- Peak memory needs no --max-old-space-size: at most 3.2 GB.
- Warm build within 5 minutes: 43 to 48 s.
- The sidebar's share of every page: 74 KB raw, 9.9 KB gzipped, 14 to 18%.
- Largest chapter page well under 250 KB gzipped (116 KB).
- Pagefind's .pf_* files served as octet-stream without extra encoding (nginx config, crawl clean).
- The Docker image tags exist on Docker Hub (node:26.13.0-trixie-slim, nginx:1.30.6-alpine, caddy:2.11.9-alpine).
- The deployment configs, with real nginx 1.30.6 and Caddy 2.11.9 (tools/servertest.py: crawl and headers).
- The first full encode estimate ("tens of minutes for ~1000 4K images"): 25 minutes for 600 pictures at effort 4,
  2.5 minutes at effort 2.
- compressHTML: true is set; spacing between inline elements checked by eye in screenshots (the 'jsx' behaviour itself
  was not tried).

Refuted, and what was done instead:
- "KaTeX throwOnError fails the build": rehype-katex 7.0.1 catches every error, adds a warning and draws the formula in
  red. rehypeBookMath fails the build on those messages (unit test).
- Pagefind payload ≤ 300 KB for a two-word query: 210 to 313 KB over the wire at full scale, 273 to 376 KB counted as
  files; the budget is 400 KB.
- starlight-markdown-blocks, starlight-image-zoom, starlight-links-validator, starlight-sidebar-topics, lychee: not used.
  The book's own asides plugin (Starlight's aside markup), pictures that link to their largest WebP, the links plugin
  with relative .md links (site.md's choice) and crawl.py as the final gate, the sidebar and tracks from sidebar.json.
- The research's media submodule with LFS, book.config.json and pre-build npm steps: published WebP in the repository
  (site.md), engine.pin, and an Astro integration that draws diagrams before the pages and encodes pictures after.
- mermaid-isomorphic closes its browser whenever no render call is running, so rendering per page would start
  Chromium per page: all missing diagrams are drawn in one session (400 x 2 in 13 s).
- New risk found: Astro keeps rendered pages between builds keyed on the page's own file, so cross-page checks (links,
  anchors, glossary, figures) would go stale. An inputs digest in Astro's configuration renders every page again when
  anything pages read from each other changes; prose edits still render one page.

Still open:
- Whole-book PDF memory and time (print views per part exist; the largest is 10.8 MB of HTML; no PDF made).
- Pandoc EPUB with MathML (later step, Pandoc not fetched).
- Lighthouse performance and accessibility scores (not run; axe is the accessibility check).
- The container build and the CI workflow never ran (no Docker on this machine; nothing pushed).
- AVIF in Safari and Firefox (WebP fallback exists; only Chromium was used).
- A whole-book print to PDF of the largest part (1.4 MB gzipped HTML) in Chromium.

## 4. Deviations from site.md and pipelines.md

- Pictures: AVIF and WebP at the widths of 960, 1920 and 3840 that the original covers (1080p sources give 960 and
  1920); AVIF at effort 2 (measured); a crisp profile (lossless WebP, AVIF 4:4:4) for crops and editor pictures; files
  named by the picture's hash under /_figures/.
- Figure directives are leaf directives, `::figure{id=…}`, `::figure{id=… variant=…}`, `::compare{id=…}` (the container
  form `:::figure{id=…}` is accepted, its body adds to the caption). Manifests are `{"figures": [...]}`; recipes may add
  `capture` and `waits_for` (what the engine cannot capture yet); "taken" hashes are keyed default, <variant> and
  <key>-crop.
- Diagrams take caption="…" and alt="…" on the fence; they are drawn into .cache/diagrams by the build, not committed.
- Glossary entries may carry `avoid` (names the linter flags) besides `aliases`; first uses are linked automatically,
  and `:term[text]{id=…}` marks a use by hand.
- engine.pin holds key and value lines: commit, release, prerelease, repository.
- Node scripts (browser checks, the generator, placeholders) live in scripts/; tools/ stays Python. src/lib/ and
  src/integrations/ are new folders.
- Tracks are part of src/sidebar.json (`tracks`), with the beginner sequence written out.
- The front matter fields are optional in the Zod schema (the landing and 404 pages lack them) and required by the
  strips plugin and tools/pages.py on every other page.
- Print views at /print/<part>/, linked from each page's top strip; anchors prefixed per chapter.
- The toolchain lives in the repository's .tools/ (as the task says), not %LOCALAPPDATA% (research).
- Starlight logs a harmless warning for the book's own 404.md ("conflicts with higher priority route /404"); the 404
  page uses it.
- Unknown inline directives with a label or attributes fail the build (Starlight would print them as text).

## 5. Findings about the plan and the engine

- style.md's front matter example `title: Time: delta time, ...` is not valid YAML: a value with ": " must be quoted.
- The outline's title "Just enough C++ for game scripts" uses a word style.md bans.
- The page id draw/lod fails the spelling gate unless typos knows "lod" (_typos.toml now does).
- A Mermaid participant named "Loop" is read as the keyword loop; the build names the page and line.
- MSYS2's git expands braces in arguments native programs pass ("<commit>^{commit}"); tools use "<commit>~0".
- On Windows, nginx leaves its worker running when only the master is ended; Caddy answers an empty 200 outside its
  routes and has no type for .webmanifest.
- Expressive Code's default line-number colors and Mermaid's dark edge labels are below WCAG AA contrast (fixed here).

## 6. Not done

- The revised plan (site.md, pipelines.md, style.md and the outlines rewritten concurrently, uncommitted) lists 14
  rulings for the spike under "The spike against this file": one picture format per picture with a 960 AVIF and AVIF
  quality 80, committed diagrams with htmlLabels false, an explicit :term with a popover, new front matter keys
  (id, size, needs, B track, learn ids, since, time; kind primer), 25 parts in a new order and tracks from
  plan/tracks.md, the directives simplified, analogy, example, derivation, test-out, steps, files, checkpoint, include,
  since, a two-file deployment with nginx-unprivileged, security headers and a CSP, precompressed files, release and
  redirect tooling, lychee, runtime, keyboard, Lighthouse and search-quality checks, search weights, print views out of
  the index, badge names, a scale test from the outline's real sizes and the samples' screenshots, and links.yml. None of
  these were built: they arrived as the spike ended and change the plan the spike was given.
- tools/figures.py take, tools/tutorials.py and tools/reference.py need an engine build (after 0.8.0); figures.py has
  validate and list, pages.py checks tutorial stamps.
- PDF and EPUB files; the version menu (by design, later).
