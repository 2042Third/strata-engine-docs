# strata-engine-docs

**The Strata Engine Book**: how a game engine works, and how to make games with one, taught with the
[Strata engine](https://github.com/2042Third/GameEngine). This repository is the book's web project: its pages, the
build that turns them into a static site, the tools that keep the book true to the engine's code, and the deployment
files. The plan of the book (what it contains, how it is written and checked) is in [`plan/`](plan/README.md); it is not
published.

The site is static files that any web server can serve. Every URL lives under one prefix, the base of
[`site.json`](site.json), `/strata-engine-docs`; nginx serves the book at `https://pdm.pw/strata-engine-docs/`, the
origin `site.json` names. Nothing is loaded from another host (fonts, math, diagrams and search are files of the site).

**Closed source.** The book is the copyright holder's work, and all rights are reserved: its text, pictures,
diagrams, sketches, tutorial files, labs, downloads and this site's own code and tools. [`LICENSE`](LICENSE) holds the
statement and the one permission it grants, to use the book's code in your own programs and games; the site serves it
as `<base>/license.txt`, beside the notices of third-party material. This repository asks for no contributions, pull
requests or translations.

**State**: the machine is built and measured at the size of the book (the scale test: a page for each of the outline's
rows, [below](#budgets-and-the-scale-test)), and the book's pages are being written: a draft, whose pictures not yet
taken show as placeholders.

## Quick start

Everything the build needs is downloaded into `.tools/` (git-ignored) by `tools/bootstrap.py`, checked against the
SHA-256 sums pinned in [`tools/toolchain.json`](tools/toolchain.json). Nothing is installed system-wide. Python 3.10 or
later (standard library only) and Git are the only things the machine must have.

```sh
python tools/bootstrap.py                # Node.js 26.13.0, typos, lychee and actionlint into .tools/; writes .tools/env.sh and env.ps1
. .tools/env.sh                          # PowerShell: . .tools/env.ps1
npm ci                                   # the exact versions of package-lock.json
npx playwright install --only-shell chromium     # for npm run diagrams and the browser checks (into .tools/)
npx astro build                          # the site, into dist/
python tools/crawl.py                    # stages dist/ under stage/strata-engine-docs/ and crawls it
python tools/crawl.py --serve-only --port 4321   # read it at http://127.0.0.1:4321/strata-engine-docs/
```

`npx astro dev` serves the book while you write (a derived picture is encoded when first asked for, and a diagram
without its committed drawings is drawn into `src/generated/diagrams/`, which you then commit), without
search, which runs only on a build: `npm run preview` (`node scripts/serve.mjs [--port 4321]`) serves `dist/` with search
at `http://127.0.0.1:4321/strata-engine-docs/`, through `tools/crawl.py --serve-only` (name Python in `PYTHON` where
`python` is not on the PATH).

Search reads what each page tells it: its title with its part and kind, its kind and part as metadata, and filters by
part, kind and track (`src/lib/search.mjs`). Code blocks weigh half as much as prose and the generated reference 0.3;
the top strip, previous and next, line numbers, KaTeX's drawn formulas, a term's popover and a glossary entry's
definition are left out. The print views and the 404 page are not indexed, and each glossary entry is a result of
its own.

Where the book is served is written in one file, [`site.json`](site.json): its `base` (the path prefix; `/` for the
root of a host), its `origin` (canonical links and the sitemap) and the copyright line's `holder` and `year`. The build
reads it through `src/lib/settings.mjs`, the tools through `tools/booklib/settings.py`, by the same rules
(`tools/tests/fixtures/settings-cases.json`); a build without the file fails. For one build at another place (another
base, a test server, a preview) set `DOCS_BASE` (an empty value is an error, never the root) and `DOCS_SITE`. A release
build (`DOCS_RELEASE=1`) is for `site.json`'s address: it refuses an origin that is not `https`, names `localhost`,
`127.0.0.1` or the placeholder `example.com` that tests use, or carries a path. `DOCS_EXTRA_REDIRECTS=<file>` adds the
moved pages of a test file to `src/redirects.json`'s (CI's build at `/x/y` adds `tools/tests/release-redirects.json`);
a release refuses it. `DOCS_ROOT` and `DOCS_ARCHIVED` are reserved for archived versions and refused. In Git
Bash or MSYS2 on Windows, source `.tools/env.sh` first and write options as `--base=/x/y`: these shells turn values that
start with `/` into Windows paths before Node or Python sees them, and `env.sh` exempts `DOCS_BASE` and `--base=`.

## Writing a page

How a page is written is decided in [`plan/style.md`](plan/style.md); this is what the build understands. Pages are
plain Markdown (`.md`, never MDX) in `src/content/docs/<part>/<chapter>.md`; the page's URL is
`/strata-engine-docs/<part>/<chapter>/` and never changes once published. Every page is a row of the outline
(`plan/outline-1.md` to `outline-4.md`), which the build reads as data from
[`src/generated/outline.json`](src/generated/outline.json): the tool chain writes it with
`python -I tools/pages.py outline --write` and checks it with `--check`; nobody edits it. A new page is listed in
[`src/sidebar.json`](src/sidebar.json), in its part, in the order of the outline's rows (a part's `<part>/index` first,
its `<part>/review` last). The sidebar's `tracks` (`game`, `beginner`, `engine`: tracks G, B and E) hold each track's
whole reading order as page ids, written or not, and its side steps (`sideSteps`, `{ "id", "before" }`); they must equal
`plan/tracks.md`, and "previous" and "next" pass over pages not written yet.

| You want | You write |
| --- | --- |
| The page's facts | Front matter (`plan/style.md` §6.1): `id` (the file's path without `.md`), `title` and `description` in double quotes, `kind` (primer, concept, internals, tutorial, how-to, reference), `size` (S, M, L, XL), `tracks` (letters G, B, E; `[]` on no track), `needs` (at most five page ids, `a\|b` for alternatives, `[]` for the outline's `-`), `time` (minutes), `learn` (two to five `- id: …` / `text: …`, each text starting with a verb of style.md's list), `since` (`0.3.0`…; concept, internals, tutorial and how-to pages of parts 1 and 3 to 21 only), `status` (draft, reviewed, final). Reference pages have no `time` and no `learn`. Any other key fails the build but Starlight's display keys (`template`, `hero`, `tableOfContents`, `pagefind`, `sidebar`, `banner`, `lastUpdated`); `editUrl` fails too, because the book's repository is not public and the site links nowhere in it (no edit links). Title, kind, size, tracks and Needs equal the page's row of the outline. A part's `index.md` and `review.md` carry `id`, `title`, `description`, `tracks` (the part's), `status` and `generated: index` or `generated: review`. The top strip is drawn from the front matter and the outline: the badges, the level (from the outline's data), the time, "New in" when `since` is the pin's release, the objectives, the Needs (a Need not written yet shows without a link), "Before this part" on the first page of a part without an index page, the pin's release and commit, and the print view. |
| A link to another page | A relative path to its `.md` file: `[time](../core/time.md#the-accumulator)`. Never a path starting with `/`: the build adds the prefix and fails on missing pages and anchors. |
| A quote of the engine | ` ```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2267-L2295" mark="L2280" ` with an empty body, then `python tools/excerpts.py fill --engine <clone>`. While writing, a symbol works too: `src="…/Scene.cpp#Scene::OnUpdateRuntime"`, or an editor command's registration: `src="StrataEditor/src/Editor/EditorViewportCommands.cpp" command="viewport.capture"` (a draft shows it labelled; a release refuses both until `fill` has run). The anchors `fill` keeps (`symbol`, `from`, `to`, `overload`, `command`) stay on the fence. Other sources: `src="book:<path>#L…"` (a file of this repository, named as text, or linking its download), `src="book:tutorials/<part>/<chapter>.patch#hunk-<n>"` (a ` ```diff ` hunk of a tutorial's patch; the header names the engine file and lines it changes) and `src="vendor:<library>/<path>#L…"` (its header names the library's version and license from `src/generated/vendor.json`, which the tool chain writes, and links the file at the commit of the library's submodule; a release needs that file). Only engine quotes count toward an internals page's three. A quote starts and ends on a line that holds code: Expressive Code draws no blank line at either end, so the build refuses one (a blank first line would put every line number and mark one line late). |
| The book's own code | ` ```cpp sketch="core-time-fixed-step.cpp" ` (a copy of `sketches/core-time-fixed-step.cpp`, compiled by the checks; a sketch's name starts with its page's id), then ` ```text output-of="core-time-fixed-step.cpp" ` (what it prints, after the sketch), or ` ```cpp pseudocode `. Any other attribute of a fence must be the book's (these, a text figure's `capture` and `variant`, and a quote's) or Expressive Code's own (`title=`, `{3-5}`, `ins=`, `collapse=`, `wrap` and the others): a name neither knows fails the build. |
| A picture | An entry in `src/content/figures/<part>/<chapter>.json` (the recipe of `plan/pipelines.md` §5.2; [schema](tools/schemas/figure-manifest.schema.json)), then `::figure{id=…}`, `::figure{id=… variant=on}`, `::figure{id=… crop=<name>}` (one of the recipe's named `crops`; a bare `crop` when it has one) or `::compare{id=…}` (a before/after slider whose sides are named after the variants). `:::figure{id=…}` … `:::` adds its text to the recipe's caption. Until the engine renders it, a draft shows a labelled placeholder, and a picture without its stamp in `taken.json` is labelled as a placeholder; a release refuses both ([Pictures and diagrams](#pictures-and-diagrams)). |
| What a command or a program printed | A recipe of kind `text` in the page's manifest, then ` ```text capture="<figure>" ` (with `variant="<name>"` when the recipe has variants) and `python -I tools/figures.py fill`, which copies the published `src/assets/figures/<part>/<chapter>/<figure>[-<variant>].txt` into the fence. It is drawn as a figure: a header that says the engine printed it and names the command or the program, the text, and the recipe's caption; its id is `fig-<figure>` as a picture's is. A fence that differs from the published text fails, and until the text is taken a draft labels the fence and a release fails. `::figure` refuses a text figure. |
| A diagram | A ` ```mermaid caption="what to notice" alt="what it shows" ` fence, then `npm run diagrams`, which draws it in the light and the dark theme into `src/generated/diagrams/` to be committed; the build fails on a fence without its drawings. `alt` is the drawing's accessible name (`accTitle` and `accDescr` fail); a name that is a Mermaid keyword (`loop`, `end`, `alt`, `opt`, `par`, `note`, `class`, `state`, `graph`, `subgraph`) gets an alias (`participant L as Loop`) or quotes. The types are flowchart, sequence, state, class and ER diagrams. |
| Math | `$a + b$` inline, `$$ … $$` on lines of their own (KaTeX at build time; a formula it cannot render fails the build). |
| An aside | `:::note`, `:::tip`, `:::caution`, `:::danger`, and the book's own `:::why`, `:::question`, `:::history`, `:::elsewhere`, `:::rule`, `:::simplified`, `:::analogy`, `:::example`; a title in brackets: `:::why[Why a fixed step?]`. An analogy's last paragraph starts with `**Where it breaks:**`. Primers, concept and internals pages hold at least one `:::example` before the bottom strip. |
| A derivation the reader may skip | `:::derivation` … `:::`: a closed box titled "Where this comes from"; the build writes its first line. |
| A primer's Test out box | `::::test-out`, five numbered questions each followed by `:::answer{tests="…"}`, then `::::`, as the first thing of the page. The build writes its title, its instruction and the next page of each track. |
| Steps | `:::steps`, one numbered list, `:::` (Starlight's steps markup). A block holds blocks with fewer colons: around steps that hold `::::tabs`, write `:::::steps` … `:::::`. |
| A file tree | `:::files[The project after step 3]`, one bulleted list (nested for what a folder holds), `:::`. An item starts with its name (a word, a name in backticks, or a **bold** name to highlight it); a name ending with `/` or holding a list is a folder; `…` stands for files left out; the rest of the line is a comment. |
| Tabs | `::::tabs{sync=os}`, then `:::tab[Windows]` … `:::` per tab, then `::::`. Without scripts every tab shows. `sync=how` holds exactly the tabs "In the editor" and "With a command", `sync=os` "Windows", "Linux" and "macOS", in that order. |
| A hidden answer | `:::answer` (or `:::answer[Worked solution]`) … `:::`. Under `## Check yourself`, `## Exercises` and `## Practice` it names the objectives it tests: `:::answer{tests="fixed-step step-count"}` (learn ids, separated by spaces or commas), and a worked solution its file. `solution="sketches/core-time-thirty-frames.cpp"`: a sketch of the page, which the answer shows in full, in its ` ```cpp sketch=… ` fence followed by its ` ```text output-of=… ` fence. `solution="tutorials/<part>/<chapter>/exercise-1.tutorial.json"` (an editor exercise) or `…/exercise-1.patch` (an engine exercise): a file of the page that must exist; the answer links its download, which `tools/tutorials.py compile` writes under `public/downloads/solutions/` (a draft shows a note until it exists). Every learn id is tested by an answer of Check yourself. |
| A glossary term | Mark its first use on the page: `:term[draw calls]{id=draw-call}`. It becomes a link to its entry and a button that opens the definition in a popover, with a link to the term's home page; later marks of the term are plain words. A mark stands in a sentence, not in a heading, a link or a title. The build links nothing on its own: a use you do not mark stays plain words (`tools/lint.py` reports it as `term-mark`). On the term's home page, define it in **bold** where it first appears. The entries are `src/content/glossary.json` (`plan/pipelines.md` §9): `{"terms": [{"id", "term", "definition", "home", "use", "aliases", "avoid", "known"}]}`, where `id` is the term in lowercase words joined by `-` (`fixed-step`), `home` the page that defines it and `use` the page of part `make` where a game maker uses it; the build refuses an entry without its `id`, and `python tools/pages.py check` checks the rest. `reference/glossary` holds `::glossary`, which draws every entry as one list (search finds each entry by its term), and sets `tableOfContents: false`. |
| A feature new in the book's release | The page's `since` when the whole page is new; else `:since[0.8.0]` at the start of the first paragraph of the section (the release of `engine.pin`). |
| A count the engine can change | Never type it: `:value{key="commands.count"}` in the sentence puts there the value of `src/generated/reference/values.json` (numbers and strings, written as the file writes them, but a number such as `20000.0` reads `20000`), which `tools/reference.py render` writes at the pin. A key the file does not have, a missing file, a file whose `engine.commit` is not `engine.pin`'s and a value in a heading fail the build. |
| A tutorial's checkpoint | `::checkpoint{stage=4}` at the end of each step section: the downloads `tools/tutorials.py` publishes for that step of `tutorials/<part>/<chapter>.tutorial.json` (`public/downloads/tutorials/<part>/<chapter>/stage-4.zip` and `stage-4.commands.json`); a draft shows a note until they exist. On the line after it, `::figure{id=…}` with the recipe of what the reader should now have: the box takes the picture in, under the heading "You should now have". |
| A generated table | `::include{file="performance.md"}` on a page of `reference`, after one paragraph on what the table is: `src/generated/reference/performance.md`, which `tools/reference.py render` writes, drawn in place (search weighs it at 0.3). The sample page `reference/performance` shows one, with a `:value`; `npm test` reads every committed table and `values.json` as the build does, so a change of `render` the build refuses fails there first. The file starts with the stamp `<!-- generated by tools/reference.py render <version>; engine <commit>; sha256 <hash>; do not edit -->`; the build fails when the commit is not `engine.pin`'s, when the hash is not that of the rest of the file (a hand edit), and on raw HTML other than the closed `<details>` and `<summary>` around a schema, which a print view opens ([`src/lib/reference.mjs`](src/lib/reference.mjs)). |
| The track chooser | `::track-chooser` (on a page of *Start here*: `start/how-to-read`). |

The build knows only these directives ([`src/lib/directives.mjs`](src/lib/directives.mjs) holds their forms and
attributes): an unknown one, one written in the wrong form (`::why` for `:::why`), a text in brackets where none belongs
and an attribute it does not take fail the build with the page and the line. Prose such as `a:b` stays text. A
directive added to the table gets its accessible name and its print form in
[`src/plugins/tests/forms.test.mjs`](src/plugins/tests/forms.test.mjs), which fails until it has both.

A part with eight or more pages has `<part>/index.md` and `<part>/review.md` (front matter above). Their writer writes
only a paragraph (the index page) or the cumulative exercises (the review page); the build draws the rest from the
outline and the written pages: on the index page after the paragraph, the part's Needs graph as a diagram and as a
list, the pages of other parts its pages need, what the reader can do after each page and, in `basics`, the first part
that needs each primer; on the review page before the exercises, every "Check yourself" question of the part's pages,
by page, with its answer.

Every part with a written page has a print view, `<base>/print/<part>/` (`src/pages/print/[part].astro`): its pages in
sidebar order on one page, each chapter's ids prefixed with its id (`core--time--summary`), links between the part's
pages turned into links within the view, every `<details>` (answers, derivations, a generated table's schemas) open and
every picture loaded at once. Print it to PDF from the browser. It is left out of search, carries
`<meta name="robots" content="noindex">`, and the book's own sitemap (`@astrojs/sitemap` with the filter of
`src/lib/sitemap.mjs`, so Starlight adds none) lists neither the print views nor the 404 page.

Every page ends with the bottom strip of its kind (`plan/style.md` §6.3, rule P1), its last level-2 sections in this
order: `## Summary` (one bulleted item per objective), `## Check yourself` (three to six numbered questions, each
followed by an answer), `## Exercises` (one to four numbered exercises, each with a worked solution),
`## Where it lives in Strata`, `## Further reading`. A primer has `## Practice` (three to eight) for Exercises and
`## Where the book uses it` for Where it lives in Strata, linking at least three pages that have the primer in their
Needs closure; a reference page has only `## Where it lives in Strata`. The section before the strip ends the body:
`## Common mistakes` on primers and concept pages, `## Changing it safely` (then `## What went wrong before`, when there
is one) on internals pages, `## Variations` on how-to pages, the last step section on tutorials. The body's other
exact headings (`plan/style.md` §7) are there too, in order: `## Why you will need this` first on primers; `## The
problem and how engines solve it`, `## Alternatives Strata did not choose` and `## How it is tested` on internals
pages; `## What you will make` first and `## What you need` on tutorials, whose step sections each end with their
checkpoint; `## Result` on how-to pages. A step that starts "This step has no menu or button" needs `make/commands`
(tracks G and B) or `editor/commands` (track E) in the page's Needs closure. The build fails when any of it is missing
or out of order. The build also checks the outline rules O1 to O9 that its data allows
(`plan/site.md`, "Outline rules on the pages"): a page must be its row, its Needs rows of the outline and earlier on
each of its tracks. A Need or a part page not written yet passes a draft build; a release build fails on it.

## Pictures and diagrams

What a picture shows is its recipe; the file is what the engine rendered, published by `python -I tools/figures.py
publish` into `src/assets/figures/<part>/<chapter>/` with its stamp in `taken.json` (`plan/site.md`, "Pictures";
`plan/pipelines.md` §5.7). One format per picture: a lossy render is `<figure>[-<variant>].avif` (quality 80, 90 for
both sides of a slider, chroma 4:4:4, effort 4), a lossless one and every picture of the interface
`<figure>[-<variant>].webp` (lossless), a crop `<figure>[-<variant>]-<crop>.webp` (lossless, cut at the picture's own
pixels), a drawing `<figure>.svg`. PNG is never published, and a file in another format than its recipe's fails the
build. Encoding is `node scripts/encode-figures.mjs encode --publish <lossy|lossless> [--quality <n>] <png> <output>`
(the tool chain's). The site serves each published file unchanged at `<base>/_figures/<page>/<name>.<hash>.<width>.<ext>`
(the first 10 hex digits of its SHA-256), and beside a lossy one an AVIF 960 pixels wide (and 1920 from a wider
capture) at effort 2, made in the build and kept in `.cache/images/`. The page's first picture loads at once
(`fetchpriority="high"`); a picture links its published file. A crop is drawn at the largest whole factor up to its
recipe's `scale` that the column holds, never smoothed (a crop wider than the column scrolls).

The sample pages' pictures are placeholders, drawn and published the way `figures.py publish` would publish them:
`npm run placeholders` (`node scripts/placeholders.mjs`) draws each as a PNG of its recipe's size in a temporary folder
and encodes it with `scripts/encode-figures.mjs`, with the crops of its recipe. Nothing stamps them, so a release build
refuses them. The PNG originals of real pictures stay in `originals/` (ignored), where `figures.py publish` puts them.

Diagrams are drawn once and committed: `npm run diagrams` (`node scripts/diagrams.mjs`) draws every fence of the book
(the part pages' generated Needs graphs included) whose drawings are missing or stale, with Mermaid 11.17.2 in
Playwright's Chromium and the page's Inter font, SVG labels (`htmlLabels: false`), and writes
`src/generated/diagrams/<hash>-light.svg` and `<hash>-dark.svg` (16 hex digits of the SHA-256 of the renderer's key and
the diagram's text), each with a stamp line; it removes drawings no fence uses. Run it on one machine (the
integrator's), so that one platform's fonts draw every diagram. The page inlines both, as an image named by the fence's
`alt` (`role="img"`, `aria-label` and `<title>`), with ids of its own (`dg-<hash>-<theme>…`; a print view puts the
chapter's name in front). The build starts no browser.

| Check | Command |
| --- | --- |
| Every fence has its two drawings, every drawing a fence, each drawing is the renderer's (its stamp), every fence a caption and alt text and a type the contrast fixture holds | `npm run diagrams -- --check` |
| The renderer's colors: every text of a fixture of each diagram type, in both themes, at 4.5:1 or more against what lies behind it; run it after a change of the settings in `src/lib/diagrams.mjs` | `npm run diagrams -- --contrast` |
| Budget row 18 on the built site, in both themes: each diagram has a caption and its name, no label's ink leaves its box, every text at 4.5:1 or more | `npm run check:diagrams` (`node scripts/diagram-checks.mjs [--url …] [--pages a/,b/]`) |
| Crops at whole factors at 375, 768 and 1280 pixels | `node scripts/crops.mjs [--url …] [--pages a/,b/]` |

The two browser checks serve the build with `tools/crawl.py` (name Python in `PYTHON`).

## Checks

| Check | Command | Needs |
| --- | --- | --- |
| 1. Front matter, outline rules, sidebar, tracks | `python tools/pages.py check` (and the build) | Python |
| 2. Links and anchors; gate (a), the staged crawl under the prefix (it also fails on a `robots.txt` in the build: [deploy/README.md](deploy/README.md), section 4, on a formula drawn as a `katex-error`, on a print view without `noindex`, on a `noindex` page the sitemap lists, on a 404 page that does not load every file it names from a missing address three levels deep, on a file of the build that nothing references: a `.br`, a `.gz` beside no file, a file no page, style sheet or script names; the 404 page, `pagefind/`, the sitemaps, the manifest, the favicon and a `.gz` beside its file are exempt; on a link to a host [`tools/external-hosts.txt`](tools/external-hosts.txt) does not list, which a page's first link to a new host adds; on a link into the engine's repository whose commit is not the pin's 40 hex digits, outside a `:::history` aside; on any link to the book's own repository; on a URL path with a capital letter outside `_astro/` or a character outside ASCII, or whose case differs from its file's; and, once the build holds `license.txt`, on a page without the footer's copyright line and its two links). `--lychee lychee` also runs lychee 0.24.2 offline over the staged folder (`--include-fragments --index-files index.html`), which reads every `srcset` candidate and the links inside `<template>` | the build; `python tools/crawl.py [--lychee lychee]` | a build |
| 3. Quotes match the engine at `engine.pin` | `python tools/excerpts.py check --engine <clone>` | an engine clone with the pinned commit |
| 4. Math compiles; every diagram has its committed drawings; sketches compile | the build; `npm run diagrams -- --check`; `python tools/sketches.py check` | a C++20 compiler (`CXX`) |
| 5. Figures: manifests, references, published pictures and their stamps | `python -I tools/figures.py check --engine <clone> --dumps reference/_dumps/<pin>` (`--release` for a release) | an engine clone with the pinned commit |
| 6. Tutorials have a current stamp | `python -I tools/tutorials.py check --engine <clone> --dumps reference/_dumps/<pin>` (`--release` for a release) | stamps from the tutorial tool |
| 7. The generated reference matches its stamps, and the engine | `python -I tools/reference.py render --check`; `python -I tools/reference.py check --engine <clone>` | an engine clone with the history and tags of the pin |
| 8. Spelling, Markdown lint, style, the names, the workflows | `typos`, `npx markdownlint-cli2`, `python tools/lint.py --engine <clone>`, `python -I tools/names.py check --dumps reference/_dumps/<pin> --engine <clone>`, `actionlint`, `node scripts/workflows.mjs` (the book's own rules for the two workflows, below; `npm test` runs them too) | the toolchain |
| 9. Accessibility (axe, both themes) | `node scripts/a11y.mjs --all` (every page of the build, print views, fallback pages and the 404 page; without `--all` the runtime gate's pages and the first page with each component). Like every browser check it serves the build with `tools/crawl.py` (name Python in `PYTHON` where `python` is not on the PATH), or checks `--url <server>` with `--dist <the served build>` | a build, Chromium |
| 9. The keyboard | `node scripts/keyboard.mjs` (`npm run check:keyboard`): tabs (arrows, Home, End, Tab leaves the list), the slider (a labelled range moved by the arrows), an answer (Enter and Space), a term's popover (Escape closes it, the focus goes back to its button), the track chooser (reached with Tab; Enter makes "next" the track's; a chooser page whose pagination holds no "next" of the chosen track fails), each on the first page that holds it | a build, Chromium |
| 9. Lighthouse | `node scripts/lighthouse.mjs` (`npm run check:lighthouse`, Lighthouse 13.6.0 as a phone): accessibility 100 on the landing page, a page of each kind and the glossary; on the heaviest figure page budget row 14 (performance 90, CLS 0.05, LCP 2.5 s), which is judged on `ubuntu-latest` only (`--not-row-14` elsewhere); `--heaviest <n>` measures the next figure pages beside it. Measure row 14 through a server that compresses as a deployment does (`--url`, `deploy/nginx.conf`): the built-in server sends every file uncompressed | a build, Chromium |
| 10. Gate (b), the runtime check | `node scripts/runtime.mjs --url <server><base>/ --dist <the served build>` (`npm run check:runtime`): the landing page, a page of each kind, the glossary, a print view and `<base>/a/b/c/`, two searches whose first result is followed, the theme switch, "next" on a chosen track, and a moved page's 301; it fails on a request outside the prefix or the origin, an answer that is not 2xx (a 304 passes only when the browser asked to revalidate a no-cache file it holds), a policy violation or a console error, a crop at a fractional factor, a diagram label outside its box. Through nginx with the release's policy: `python tools/servertest.py nginx … --runtime` (every run) or `url … --runtime` | a release; nginx; Chromium |
| 10. Gates (a) and (c) through the deployments | `python tools/servertest.py nginx --program <nginx> --release release/<tag> [--container-program <nginx>]`: the release served the two ways of `deploy/README.md`, the copied files and the container behind a proxy, each host with and without a host-headers file, and the container with a hostile server block, crawled and every header checked; a running server: `python tools/servertest.py url --url <origin><base>/ --release release/<tag> [--container] [--wait <seconds>]`; one server's files for a container that mounts them: `python tools/servertest.py layout --kind <copied\|container\|hostile\|proxy> --release release/<tag> --out <new folder>`; the deploy files alone: `python tools/servertest.py static` ([Deploying](#deploying)) | a release; nginx |
| 11. Search works under the prefix, within its transfer budgets | `node scripts/search-payload.mjs` (a two-word query, then a next one, each against its budget of `tools/budgets.json`; `--json` for `tools/budgets.py --search`) | a build, Chromium |
| 11. Search finds the right pages | `node scripts/search-quality.mjs` (`npm run check:search-quality`): the 60 fixed queries of `scripts/search-queries.json` (30 glossary terms, 20 engine names, 10 questions, each with its expected page) through Pagefind's own script; it passes when 90 % of the queries, and every engine name, find their page among the first three results. A query whose page is not written yet waits (`--release` requires every page); `--check` checks only the file against the outline and the glossary (`--glossary <file>` for another one) | a build, Chromium |
| 12. Budgets | `python tools/budgets.py --measure … --crawl … --search …`; `--check-file` checks `tools/budgets.json` against its pass marks ([below](#budgets-and-the-scale-test)) | the measurements of CI |
| 13. Unit tests | `npm test` (`node --test src/plugins/tests/`; the tests of the browser checks run Chromium against fixture pages with planted faults), `python -m unittest discover -s tools/tests -t tools` (or `-t .`, or `python -I -m unittest discover tools/tests`) | Chromium for `npm test` |
| CI's result | `python tools/cistatus.py <commit>`: fetches the branch `ci-results` with git and prints the newest run of the commit (every job's conclusion, its failed steps and its `::error` annotations); 0 passed, 1 failed, 3 not recorded yet. No token | git |

A release build (`DOCS_RELEASE=1`) also fails on draft pages, placeholder pictures, quotes not filled yet, checkpoints
and worked solutions whose downloads are missing, and tutorials without a current stamp
(`tutorials/<part>/<chapter>.stamp.json` with a passing run at the pin whose inputs are the files as they are now). The
build stops at the first page that fails; `python tools/pages.py check --release` and `python tools/figures.py check
--release` list every problem of every page at once, so run them first (CI runs the checks before the build).
[`.github/workflows/book.yml`](.github/workflows/book.yml) runs all of it on every push, tag and pull request, in the jobs of
plan/site.md's "CI": `lint` (without the pictures: checks 1, 8 and 13), `excerpts` (the engine at the pin, cloned from
`engine.pin`'s repository: the quotes, sketches, figures, tutorials, the generated reference, the language and names
lints, `pin.py report`), `build` (the site at `/`, `/x/y` and `/strata-engine-docs`, each through gate (a) with lychee;
the budgets; the three releases, uploaded as artifacts), `serve-test` (the releases in nginx: Ubuntu's, the container of
`deploy/Dockerfile` alone, with the hostile block and behind two proxies, and `nginx:1.20.1` with the copied files at
three bases, each through gates (a) to (c); search, axe on every page, the keyboard and Lighthouse against the
container; the two-pass copy with rsync), `release` (a `book-v*` tag's GitHub release) and `report`, which commits
`runs/<commit>-<attempt>.json` to the branch `ci-results` whatever the others did. A check that fails writes its reason
as an `::error` annotation (`python tools/cistatus.py step --title <what> -- <command>`), which `report` records, so
that `tools/cistatus.py` shows it without a token. [`links.yml`](.github/workflows/links.yml) checks the pages'
external links weekly, reporting them in its summary, and fails when the repository holds more than 1 GB. Neither
deploys anything. `node scripts/workflows.mjs` holds both files to plan/site.md's "CI": every action pinned by its
commit, `contents: read` by default and `contents: write` only in `report` and `release`, every push and tag run with
superseded runs cancelled except for tags, the jobs and their needs, no variable, no secret but the workflow's token and
no `DOCS_SITE`, every step after the bootstrap sourcing `.tools/env.sh`, every check of `book.yml` through
`cistatus.py step`, the caches' keys (Playwright's with `package.json`'s version), one-commit checkouts, and
`links.yml`'s schedule, report and size limit.

Moving the book to a new engine commit: `python tools/pin.py report --engine <clone> --to <commit>` lists, per page,
the quotes that moved (updated by `move`), the quotes whose text changed (a person reads the page again), the tutorials
to run again and the pictures to take again; `python tools/pin.py move --engine <clone> <commit>` does it.

## Budgets and the scale test

The budgets of check 12 are in [`tools/budgets.json`](tools/budgets.json), beside the pass marks of plan/site.md's
table and the measurements they were set from (plan/critique/rulings-5.md, R13 and R14). The pass marks are the design's
and change only by a ruling; each budget is at most the smaller of its pass mark and 1.5 times its latest full-scale
measurement, rounded up to two digits, and `python tools/budgets.py --check-file` (CI's `lint` job) fails on one above
that ceiling, so a budget goes down whenever a measurement allows it, and up only by a ruling that names what grew. The
measurements are the scale test's (below; 2026-11-11, the reference machine, i7-13700K, inside the engine's perf lock
while the engine's own builds and captures kept other processors busy, so its times are slow ones). Its report, with
every row of plan/site.md's table, is `.tools/spike-report.md`:

| Measure | Measured | Budget | Pass mark |
| --- | --- | --- | --- |
| Build, caches empty (pictures encoded, diagrams drawn) | 160–165 s | 250 s | 30 min on `ubuntu-latest` (row 3) |
| Build, caches full | 57–76 s | 70 s | 4 min (row 1) |
| Build after one page's prose changed / after a change that renders every page again | 76 s / 101–152 s | — | 90 s (row 5) |
| Peak memory of the build (all processes; `--max-old-space-size=4096`, as `npm run build` sets it) | 2,653–3,730 MiB | 4,096 MiB | 4 GB (row 7) |
| The built site | 325 MB in 2,018 files | 400 MB; 3,100 files | 400 MB; 15,000 files (row 9) |
| HTML of the chapter pages / of the print views | 115.4 MB / 78.9 MB | 140 MB / 97 MB | recorded (row 9) |
| Largest page (gzip) / raw; median page (gzip) | 146 KB (the glossary of 1,892 entries) / 1,774 KB (all 26 command tables on one page); 43 KB | 170 KB / 770 KB; 60 KB | 300 KB; 60 KB (row 10) |
| Scripts of a page without search (gzip) | 9.6 KB | 15 KB | 40 KB (row 11) |
| Largest print view of a part (gzip) | 1.3 MB (`make`) | 2,000 KB | — |
| Search index on disk | 8.5 MB | 9.5 MB | — |
| One two-word search, over the wire (four queries); the next query | 177–277 KB; 136–187 KB | 300 KB; 100 KB | 300 KB; 100 KB (row 12) |
| Staged crawl without lychee (1,538 requests) | 101 s | 48 s | — |

`tools/crawl.py --report` measures the sizes, the median page, the HTML of the chapter pages and of the print views,
the heaviest page's scripts (its inline scripts, the scripts it names and what they import statically, Pagefind's
files left out) and the sidebar's share of its page, which is recorded beside the budgets. Times and load:
`tools/measure.py` records how many processors other programs kept busy during the run (about 1.4 on the reference
machine with its desktop programs). A time within its budget passes whatever the load, because load only makes a build
slower; a time over its budget measured above `quiet_other_load` (2.0) is not judged, never counts as a pass, and makes
`tools/budgets.py` exit 2: measure it again on a quiet machine. The engine's builds and tests run without the perf lock
(a cached build beside StrataTests took 77–80 s). CI multiplies the time budgets by 2 until the hosted runner's own
times are known. A measurement over its budget is either not judged (the times above, taken under load) or waits for a
ruling (the raw size of the command catalogue on one page; the next search query), as the report says.

`.cache/` keeps derived pictures and Astro's rendered pages between builds; a page whose prose changed renders again
alone, and a change to anything pages read from each other (titles, headings, the glossary, figures, the drawings of
the diagrams, the plugins, `ec.config.mjs`, the packages) renders every page again.

The scale test's book is written by `scripts/scale.mjs` into `.tools/scale/site` (ignored, never committed): a page of
each of the outline's rows (`src/generated/outline.json`) at its size (S 1,500 words, M 3,000, L 5,000, XL 8,000), with
its row's front matter and in its kind's shape, the part pages, 1,500 quotes of the engine at the pin, 3,000 code
blocks, 400 diagrams, math on a third of the pages, 600 pictures made from the samples' twelve screenshots (450 AVIF
renders, 30 slider pairs among them, 100 crops and 50 pictures of the interface as lossless WebP, all stamped in
`taken.json`), the generated reference of `src/generated/reference/` at its real size, a glossary of
`plan/glossary/seed.json` and generated entries to 1,892, and the words of the search queries on the pages they expect.
Encoded pictures are kept in `.tools/scale/cache`, so a second run takes about 40 s. Each measuring step below keeps the
processors busy for minutes: run each inside the engine's perf lock (`Tools/PerfLock.py --wait 120 -- …`, one step per
hold, each under 20 minutes) and measure it with `python tools/measure.py --label <name> --json <file> -- <command>`
(`--env NAME=VALUE` gives the command the book's `TEMP` and `PATH` while the lock keeps the system's):

```sh
node scripts/scale.mjs --engine <pin clone>                # --fraction 0.1: every page and total smaller, for a look
node scripts/diagrams.mjs --root .tools/scale/site         # row 4: every diagram from an empty folder
node --max-old-space-size=4096 node_modules/astro/bin/astro.mjs build --root .tools/scale/site    # rows 1, 3, 5, 7, 8
python tools/crawl.py --root .tools/scale/site --lychee lychee --report crawl.json    # rows 9 to 11, gate (a); DOCS_BASE for row 17
node scripts/search-payload.mjs --root .tools/scale/site   # row 12 (--query, --next-query, --files)
node scripts/search-quality.mjs --root .tools/scale/site   # row 13
node scripts/a11y.mjs --root .tools/scale/site --pages <a/,b/,…>   # row 15, in parts: every page in two themes takes 30 minutes
node scripts/diagram-checks.mjs --root .tools/scale/site --pages <a/,b/,…>   # row 18, in parts
node scripts/print-pdf.mjs --root .tools/scale/site --part make     # row 19: the print view to PDF, its duplicated ids
node scripts/dev-timing.mjs --root .tools/scale/site --page core/time    # row 6: astro dev's start and its refresh
python tools/release.py assemble --root . --dist .tools/scale/site/dist --tag main-<8 hex>    # then servertest.py, row 16
python tools/pages.py check --root .tools/scale/site --plan plan   # and the tool chain's other checks, with --root
```

`node scripts/print-pdf.mjs` and `node scripts/dev-timing.mjs` work on this book too (without `--root`): the first
prints `<base>/print/<part>/` of the built site to PDF in Chromium and fails on an id that stands on two elements; the
second starts `astro dev`, times the first answer for a page, adds a marked paragraph to it and times until a request
shows it, then puts the page back and ends the server.

## Deploying

The book is deployed from a release, which nginx serves: [`deploy/README.md`](deploy/README.md) is the owner's guide,
and ships in every release. A release is made from a build in three steps:

```sh
npx astro build
node scripts/precompress.mjs                 # a .gz beside every text file of 1 KB or more, for gzip_static; no .br
python tools/release.py assemble --tag main-$(git rev-parse --short=8 HEAD)     # or book-v0.8.1-r1 for a release
```

`release/<tag>/` then holds `strata-engine-docs-<tag>.tar.gz` (the site in one folder, `strata-engine-docs/`),
`strata-engine-docs-deploy-<tag>.tar.gz` (`deploy/` with the two files written from the built HTML: `nginx-csp.conf`,
the Content Security Policy with the SHA-256 of every inline script, and `nginx-redirects.conf`, the moved pages) and
`SHA256SUMS`. The tarballs are reproducible: a second run on one build writes the same bytes. `assemble` refuses a site
built for another base, one that is not precompressed (or holds a `.br`), and inline code the policy would block (an
`on…=` handler, a `javascript:` URL); a release tag also needs `license.txt` and `third-party-notices.txt` at the site's
top, which other tags only note. For another base, `--base=<base>` rewrites every file of `deploy/` for it and names
the top folder after it (`x/y/`, or `site/` for the root of a host). `python tools/release.py csp` prints the policy,
and `python tools/release.py layout --dist dist --out <folder>` writes what the container copies, for
`deploy/Dockerfile.build`. `python tools/deployfiles.py --base=<base> --out <folder>` writes the committed files alone
for another base.

The committed files of `deploy/` are written for `site.json`'s base (a test fails when the two differ):
`nginx-http.conf` (the `Cache-Control` of each kind of file, in nginx's `http` context), `nginx.conf` (the book's
`location ^~ <base>/`: the book's own types, `gzip_static`, the four security headers with `always`, the policy, the
moved pages and the host's own headers through `strata-engine-docs-host-headers*.conf`), `nginx-container.conf` (the
container's server), `nginx-proxy.conf` (the host's lines in front of the container), `Dockerfile` (nginx 1.30.6
serving a release, `nginxinc/nginx-unprivileged:1.30.6-alpine`), `Dockerfile.build` (builds from a clone, then serves
the same way) and `deploy-files.sh` (copies a new site over the served one in two passes with `rsync`, keeping
archived versions and `versions.json`). The unit tests of `deploy-files.sh` check the two passes' arguments on every
machine and copy with the real `rsync` where there is one; CI's `checks` job installs it when the runner lacks it.

To test them: `python tools/bootstrap.py --servers` fetches the Windows builds of nginx 1.20.1 (what the owner's host
runs) and 1.30.6 into `.tools/`, each checked by its SHA-256; then
`python tools/servertest.py nginx --program .tools/nginx-1.20.1/nginx-1.20.1/nginx.exe --container-program
.tools/nginx-1.30.6/nginx-1.30.6/nginx.exe --release release/<tag>` serves the release the two ways and checks gates
(a) and (c), with `--runtime` also gate (b) (`scripts/runtime.mjs` in Chromium, under the release's policy; source
`.tools/env.sh` first, or name Node.js with `--node`), and it stops every nginx it started with its workers. Its six runs: the copied files in a host that serves
a site of its own (with a regular-expression location for static files that answers 418, and its own
`X-Frame-Options`, `X-Content-Type-Options` and `expires`), without and with a host-headers file; the container's
server; the container's server with that location beside the book's include; and the proxy in front of the container,
without and with a host-headers file. `--runs copied,proxy` picks some. CI runs the same configurations in containers:
`python tools/servertest.py layout --kind <kind> --release release/<tag> --out <new folder>` writes one server's files
under `<folder>/etc/nginx/` and `<folder>/srv/` with the paths they have there, from the code that writes the local runs'
files, and `.github/workflows/book.yml` mounts them into nginx's official 1.20.1 image (the copied files), the image of
`deploy/Dockerfile` (the hostile server block) and nginx images on the runner's network (the proxy), then checks each
with `python tools/servertest.py url --wait 30`.

**Moved pages.** After the first release, a page whose id disappears gets an entry in
[`src/redirects.json`](src/redirects.json), `{ "redirects": [{ "from": "<old id>", "to": "<new id>" }] }`. The build
checks each entry (the old id is not a page, the new one is, no chains) and writes a fallback page at
`<base>/<old id>/index.html` (a refresh to the new page, which is its canonical address, `noindex`, a plain link); the
release's `nginx-redirects.conf` answers the old address, with and without its slash, with a 301 to the new page's
path. The crawl starts at the fallback pages and checks them.

**Versions.** One version is built. Page ids and part slugs that start with `v` and a digit are refused,
`deploy-files.sh` keeps `v<digit>…/` and `versions.json`, and `DOCS_ROOT` and `DOCS_ARCHIVED` fail a build, so that
archived books can later live at `<base>/v<major>.<minor>/` without changing any URL of the current one.

## Layout

| Path | Holds |
| --- | --- |
| `src/content/docs/<part>/<chapter>.md` | the book's pages |
| `src/content/figures/<part>/<chapter>.json` | figure recipes |
| `src/assets/figures/<part>/<chapter>/` | published pictures (AVIF, lossless WebP, SVG) and their stamps, `taken.json` ([Pictures and diagrams](#pictures-and-diagrams)) |
| `src/generated/diagrams/` | the committed drawings of the diagrams, two per diagram, written by `npm run diagrams` |
| `src/content/glossary.json`, `src/sidebar.json` | the glossary; the parts, their pages and the reading tracks |
| `src/plugins/`, `src/lib/`, `src/integrations/` | the build's own Markdown plugins and their library, with tests in `src/plugins/tests/` |
| `src/components/`, `src/styles/`, `src/pages/` | the top strip and track navigation, the client script (tabs, slider, tracks), styles, print views, the web manifest |
| `sketches/`, `tutorials/` | the book's own programs; tutorial command scripts and their stamps |
| `tools/` | Python tools (standard library only) with tests in `tools/tests/` |
| `scripts/` | Node scripts: the browser checks, the diagrams' drawing and checks, the crops' check, the placeholder pictures, the scale test's generator, the dev server's timing and the print view's PDF; `encode-figures.mjs` and `screenshot-page.mjs` are the tool chain's |
| `site.json` | where the book is served (base and origin) and the copyright line's holder and year |
| `src/redirects.json` | moved pages |
| `deploy/`, `.github/workflows/` | deployment files (nginx, the container, the two-pass copy, the owner's guide); CI, which builds at three bases |
| `release/` (ignored) | releases written by `tools/release.py assemble` |
| `engine.pin` | the engine commit the book is checked against |

## Versions

All exact, from `package-lock.json` and `tools/toolchain.json`; upgrades are deliberate, once per engine wave.

| Piece | Version |
| --- | --- |
| Node.js | 26.13.0 (npm 11.20.0) |
| Astro / Starlight | 7.4.8 / 0.42.10, Markdown through `unified()` from `@astrojs/markdown-remark` 7.3.6 |
| Expressive Code | 0.44.3, with line numbers and collapsible sections; Slang shown as HLSL |
| Pagefind | 1.6.0 (and its UI 1.6.0) |
| KaTeX | 0.16.47 through `remark-math` 6.0.0 and `rehype-katex` 7.0.1 |
| Mermaid | 11.17.2 through `mermaid-isomorphic` 3.1.0 and Playwright 1.65.0 (Chromium headless shell) |
| sharp | 0.35.5 |
| Fonts | Source Serif 4 (5.3.1), Inter (5.3.0), JetBrains Mono (5.3.0), from `@fontsource-variable` |
| Checks | markdownlint-cli2 0.24.0, typos 1.52.1, lychee 0.24.2, actionlint 1.7.12, `@axe-core/playwright` 4.14.0, Lighthouse 13.6.0 |
| Test servers | nginx 1.20.1 and 1.30.6 (`tools/bootstrap.py --servers`; the container: `nginxinc/nginx-unprivileged:1.30.6-alpine`) |
