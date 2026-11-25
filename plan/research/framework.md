# Web framework for "Strata Engine Docs"

Research date: 2026-11-10. Every version and date below was read that day from the package registry (npm, PyPI,
crates.io), the project's GitHub releases or its official documentation. The sources are listed at the end. Where
something could not be verified, the text says so and the [spike](#7-spike-before-writing-content) checks it.

## 1. Decision in one paragraph

Build the book with **Astro Starlight 0.42.10 on Astro 7.4.8**, with Markdown processed by Astro's **`unified()`**
(remark/rehype) pipeline rather than the new default Sätteri one, content written as **plain `.md` files**
(CommonMark + GFM + math + `:::` directives, never MDX), search by **Pagefind 1.6.0** (part of Starlight), code blocks by
**Expressive Code 0.44.3** (part of Starlight), math rendered at build time by **KaTeX**, Mermaid diagrams rendered at
build time to SVG, and images run through **our own sharp pipeline** (AVIF/WebP at fixed widths, lossless originals kept
out of the site). Node **26.13.0 LTS**, unpacked from the official zip into a per-user folder, is the only runtime the
build needs. The project's own checks are small scripts plus **lychee 0.24.2** (links, anchors, images),
**markdownlint-cli2 0.24.0** and **typos 1.52.1**. Code excerpts are kept in sync with a pinned engine commit by
`tools/excerpts.py`, which uses only the Python standard library. **Fallback: Quarto 1.11.9.** It is the only candidate
with PDF and EPUB built in, and its weak points (search at this size, line highlighting, the slider) can be fixed with
the same Pagefind and custom pieces.

## 2. Candidates as of 2026-11-10

| Candidate | Current version (date) | Maintained? | Needs installed | Verdict |
| --- | --- | --- | --- | --- |
| **Astro Starlight** | `@astrojs/starlight` 0.42.10 (2026-11-06) on `astro` 7.4.8 (2026-11-09) | Yes. Astro core team; patch releases every few days. Still 0.x: minors break things (0.39 changed sidebar `autogenerate`, 0.41 moved to Astro 7, 0.42 changed menu markup). Astro majors came fast: 6.0 on 2026-03-10, 7.0 on 2026-06-22. | Node ≥ 22.23.4 (`astro` engines); npm. Playwright Chromium only for build-time Mermaid and PDF. | **Chosen** |
| **VitePress** | 1.6.4 (2025-08-05) stable; 2.0.0-alpha.21 (2026-10-25) on `next` | Commits are active (latest 2026-11-10), but there has been no stable release for 15 months and 2.0 is still an alpha with breaking changes. | Node (2.0 needs ≥ 22 and Vite 8, per a third-party guide; not checked on the official site) | Rejected: no stable line, search does not scale, no versioning |
| **Docusaurus** | `@docusaurus/core` 3.10.2 (2026-07-10); v4 only as canaries (`4.0.0-canary-7078`) | Yes (Meta). 3.10 is announced as the last 3.x, so a v4 migration is coming. | Node ≥ 20, React 18/19 | Rejected: MDX-first, React SPA weight, no local search in core |
| **Material for MkDocs** | 9.8.1 (2026-11-07) | **Feature-frozen** since 9.7.0. The 9.8.x release notes say it "reaches end of life on May 5, 2027", with critical fixes only until then. MkDocs itself: 1.6.1 (2024-08-30); 2.0 exists only as dev builds (2.0.dev6, 2026-09-15) that break plugins. | Python ≥ 3.11 | Rejected: end of life |
| **Zensical** (Material's successor) | 0.1.0 (2026-11-05) | Yes. Its release notes say 0.1.0 "enters beta for the next three months". The roadmap still lists versioning, i18n, a Python module API ("up next"), PDF/EPUB output and a Rust Markdown parser as not done. | Python ≥ 3.11 with native wheels (`win_amd64`, manylinux). **MSYS2's Python cannot install them** (its platform tag is `mingw_x86_64_msvcrt_gnu`), so this machine would need a uv-managed CPython. | Rejected for now: beta, missing versioning/i18n/extension API. Worth looking at again in 2027. |
| **mdBook** | 0.5.4 (2026-07-06) | Yes (Rust project). 0.5.0 broke the preprocessor API, so community preprocessors lag. | One binary | Rejected: math is MathJax 2.7.1 from cdnjs (not offline), no tabs, figures, image pipeline, i18n or versioning; single search index |
| **Quarto** | 1.11.9 (2026-10-30) stable; 1.12.1 pre-release (2026-11-06) | Yes (Posit) | One zip (bundles Pandoc, Typst, Deno, Dart Sass) | **Fallback**: best print/EPUB story, weakest web reading at this size |

### Requirement matrix

B = built in, P = plugin (named), C = our own custom work, ✗ = missing or impractical, ? = not verified.

| Requirement | Starlight 0.42 | VitePress 1.6 | Docusaurus 3.10 | Zensical 0.1 | mdBook 0.5 | Quarto 1.11 |
| --- | --- | --- | --- | --- | --- | --- |
| Static site, configurable base path | B (`astro` `base`, `trailingSlash`, `build.format`) | B (`base`) | B (`baseUrl`) | B (`site_url`) | B (`site-url`) | B |
| Offline: no CDN at run time | B (no external assets; fonts and KaTeX CSS self-hosted through npm) | B | B (KaTeX CSS must be self-hosted) | P (privacy replacement "available now"); Mermaid in Material came from a CDN unless localized | ✗ for math (cdnjs MathJax in `index.hbs`) | B with care (MathJax defaults to a CDN; KaTeX/local URL configurable) |
| Deep sidebar, prev/next, ToC per page | B (+ P `starlight-sidebar-topics` 0.9.0 for one sidebar per track) | B | B | B | B (sidebar heading nav new in 0.5) | B |
| Full-text search without a service, fast at 500k words | B **Pagefind 1.6.0**: chunked index; "10,000-page site … under 300kB" network payload | B MiniSearch: **one index module per locale**, loaded whole (`localSearchPlugin.ts`) | P `@easyops-cn/docusaurus-search-local` 0.55.3 (lunr, index loaded whole) | B (Zensical's own engine; scaling ?) | B elasticlunr, single `searchindex` file | B Fuse.js over a single `search.json` (`quarto-search.js`) |
| Code: C++, HLSL/Slang, CMake, JSON, Python, shell; title; line numbers; highlighted lines; diff | B Expressive Code (Shiki grammars `cpp`, `hlsl`, `cmake`, `json`, `python`, `shellscript`, `powershell`; Slang → alias of `hlsl`), `title=`, `{2-5}`, `ins=`/`del=`, `diff lang=`, P `@expressive-code/plugin-line-numbers` 0.44.3 | B (`{1,4-6}`, `// [!code ++]`, `:line-numbers`); single-block titles only in code groups | B (`title=`, `{1,3}`, `showLineNumbers`, magic comments) | B (`title`, `linenums`, `hl_lines`) | Partial (highlight.js; no titles, line marks) | Partial (`filename`, line numbers; line highlighting only in revealjs; no diff marks) |
| Math at build time | P `remark-math` 6.0.0 + `rehype-katex` 7.0.1 (unified) | B `markdown.math` (markdown-it-mathjax3, build time) | P remark-math + rehype-katex | Client side (arithmatex + KaTeX/MathJax) | ✗ (client side, CDN) | Client side |
| Diagrams: Mermaid at build time, plain SVG | P `rehype-mermaid` 3.0.0 / `mermaid-isomorphic` 3.1.0 (Playwright) or C pre-render; SVG as images | P `vitepress-plugin-mermaid` 2.0.17 (2024, client side) | P `@docusaurus/theme-mermaid` (client side) | B (client side) | P `mdbook-mermaid` (client side) | B (client side, bundled) |
| Figures with captions, zoom, before/after slider | Zoom P `starlight-image-zoom` 0.16.2 (dialog, no client deps); captions and slider C | C | C (React components) | Zoom P (glightbox in Material; Zensical ?) | Zoom B (0.5.4); rest ✗ | Captions + numbering B, lightbox B, slider C |
| Callouts: note, pitfall, why, exercise, folding solution | B `:::note/tip/caution/danger`; P `starlight-markdown-blocks` 0.1.1 for custom types (renderer gets `h()`, so `details` is possible) | B containers incl. `details` | B admonitions (custom keywords) | B admonitions, `???` folds | B admonitions (0.5) | B callouts with `collapse` |
| Tabs | B only in MDX/Markdoc → C directive for `.md` | B code groups | B (MDX) | B `===` | ✗ | B `panel-tabset` |
| Glossary with term links | C (remark directive + data file) | C | C | P (abbr/snippets) | ✗ | C (Lua filter) |
| Dark and light themes | B | B | B | B | B | B |
| Typography for long reading | C (custom CSS on a good base) | C | C | B good | Weak | Bootstrap look |
| Accessible | B (keyboard, landmarks, skip link; mobile menu works without JS since 0.42) | B | B | B | Fair | Fair |
| Print / PDF / EPUB | Print CSS B; whole-book PDF/EPUB C (see §5.9) | ✗ | P (community) | Roadmap | B `print.html` (whole book) | **B PDF (Typst/LaTeX) and EPUB** |
| Markdown safe for agents (not MDX) | B (`.md` is not MDX) | Vue `{{ }}` interpolation in prose | ✗ MDX by default (`markdown.format: 'detect'` helps) | B | B | B (Pandoc Markdown) |
| Build fails on broken links / anchors / images | P `starlight-links-validator` 0.27.0 (`errorOnInvalidHashes` default true); Astro fails on missing local images; plus lychee on output | Links B (dead links fail), anchors ✗ | B `onBrokenLinks`/`onBrokenAnchors: 'throw'` | MkDocs-style validation ? | ✗ | Warns only |
| Versioning by engine release | P `starlight-versions` 0.10.2 (folder copies, "early development"), or our build-per-release scheme (§5.10) | ✗ | B (folder copies) | Roadmap | ✗ | ✗ |
| Translations later | B (`locales`, fallback pages); Lunaria (`@lunariajs/core` 0.3.0) tracks them | B | B | Roadmap | ✗ | ✗ (one language per project) |
| Excerpts from engine source | C (`tools/excerpts.py`) | B `<<< @/file#region` | C | B snippets with line ranges | B `{{#include file:10:20}}` / anchors | B `include` shortcode |

### Weak points at this scale (150–300 pages, 500k+ words, ~1000 images, hundreds of diagrams, thousands of code blocks)

- **Starlight/Astro.** (1) Image processing: Astro's built-in optimizer would encode every 4K screenshot at many
  widths on the first build. It caches in `node_modules/.astro` only if that folder is kept between builds, and it emits
  AVIF only through `<Picture>`, not from Markdown. Hence our own pipeline (§5.6). (2) Markdown processing:
  Astro 7 made Sätteri (Rust) the default; it runs no remark/rehype plugins, and a published report shows it turning
  display math into a highlighted code block. The unified pipeline is slower (the Astro team says Sätteri "shaved over
  a minute" off the Astro and Cloudflare docs builds) but has mature plugins. At 300 pages that minute is acceptable.
  (3) Every page includes the full sidebar. Starlight 0.41.11/0.42.4 optimized large nested sidebars, and splitting the
  two tracks with `starlight-sidebar-topics` halves it. (4) Churn: 0.x minors and quarterly Astro majors. Pin exact
  versions; upgrade once per engine wave (§8). (5) Node heap: large content collections may need
  `NODE_OPTIONS=--max-old-space-size=8192` (measure in the spike).
- **VitePress.** One MiniSearch index per locale, downloaded whole on the first search. At half a million words that is
  several megabytes (estimate). No image pipeline, no versioning, and the stable line is 15 months old.
- **Docusaurus.** React/webpack (or Rspack via `future.faster`) builds of large sites need a lot of memory. Each page
  hydrates a React SPA. Versioning copies the whole docs folder (and its images) per version. A v4 migration is pending.
- **Zensical.** Beta; extension API not shipped; versioning, i18n and PDF on the roadmap. It cannot be installed into
  this machine's MSYS2 Python.
- **mdBook.** A single search index file; math loads from a CDN; no figures, tabs, i18n or versioning; preprocessor
  ecosystem disrupted by 0.5.
- **Quarto.** Pandoc renders each page, so a 300-page build takes minutes and needs `freeze` for incremental work. Fuse.js
  loads the whole `search.json`. Line highlighting and diff marks are missing in HTML. Broken links only warn.
  Bootstrap styling needs much custom SCSS to read like a book.

## 3. Why Starlight wins

1. **Search scales.** Pagefind indexes the built HTML in chunks and loads only what a query needs. It is the only
   candidate whose built-in search is designed for tens of thousands of pages, and it needs no service.
2. **Code blocks are the best of the field.** Expressive Code gives titles, line markers, inserted/deleted marks, diff
   blocks, frames, line numbers (with `startLineNumber`, so excerpts can show the engine's real line numbers),
   collapsible sections and text wrapping, all rendered at build time with zero client JS except the copy button.
3. **Plain Markdown with directives covers callouts and asides in `.md`.** Authors and agents never need MDX.
   Starlight's `:::note[Title]` syntax is the base for every custom block.
4. **It is an Astro site underneath.** Anything missing (the slider, the glossary, tabs in `.md`, the print book, a
   version menu) is a small remark/rehype plugin, a web component or a component override. No fork is needed.
5. **The build checks content.** The content-collection schema (Zod) rejects bad frontmatter,
   `starlight-links-validator` rejects broken internal links and anchors, and Astro rejects missing images.
6. **i18n is built in.** Locales, fallback pages with a notice, and the Lunaria tracker. Configuring the English locale
   now means later translations will not move any URL.
7. **Offline by default.** Starlight loads nothing from third parties. Fonts and KaTeX CSS come from npm packages and
   are bundled by Vite.

**Fallback: Quarto 1.11.9.** Switch to it if the spike (§7) shows that Starlight cannot meet the budgets, or if
whole-book PDF/EPUB becomes a hard requirement that the custom route (§5.9) cannot meet. The Book Markdown dialect
(§5.3) is kept close to Pandoc's fenced divs (`:::name` ↔ `::: {.name}`), so a converter script is mechanical.
Pagefind runs on any static HTML, so Quarto's search would be replaced by it.

## 4. Getting the tools without administrator rights

Everything goes into a per-user tools folder, here `%LOCALAPPDATA%\StrataDocsTools`. Nothing is installed system-wide,
and the PATH changes only in the shell that sources the bootstrap script. The pinned versions and SHA-256 sums live in
`tools/toolchain.json` in the book repository, so CI and the Dockerfile use the same values.

### 4.1 Node.js 26.13.0 LTS ("Lithium", released 2026-10-28)

Node 26 became Active LTS with 26.13.0. Node 24.22.2 ("Krypton", 2026-10-27) is the Maintenance-LTS fallback. Both
satisfy Astro's `node >= 22.23.4`. The SHA-256 sums below were taken from `https://nodejs.org/dist/v26.13.0/SHASUMS256.txt`
on 2026-11-10:

```
dcc60d59a0746999f99064a01c020445d54d84228c691cdbf25b49ac3b59150a  node-v26.13.0-win-x64.zip
d28a96af6c38596f6d9d97c0ee531c13d238d757742387d1928de822d959e997  node-v26.13.0-linux-x64.tar.xz
```

`tools/bootstrap.ps1` (Windows PowerShell 5.1, no admin):

```powershell
$ErrorActionPreference = 'Stop'
$version  = '26.13.0'
$expected = 'dcc60d59a0746999f99064a01c020445d54d84228c691cdbf25b49ac3b59150a'
$tools    = Join-Path $env:LOCALAPPDATA 'StrataDocsTools'
$nodeDir  = Join-Path $tools "node-v$version-win-x64"
if (-not (Test-Path (Join-Path $nodeDir 'node.exe'))) {
    New-Item -ItemType Directory -Force $tools | Out-Null
    $zip = Join-Path $tools "node-v$version-win-x64.zip"
    Invoke-WebRequest "https://nodejs.org/dist/v$version/node-v$version-win-x64.zip" -OutFile $zip
    $actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { Remove-Item $zip; throw "node zip SHA-256 mismatch: $actual" }
    Expand-Archive $zip -DestinationPath $tools -Force
    Remove-Item $zip
}
$env:Path = "$nodeDir;$tools\bin;$env:Path"
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $tools 'ms-playwright'
$env:npm_config_cache = Join-Path $tools 'npm-cache'
node --version
```

Use it with `. .\tools\bootstrap.ps1` in each new shell. Git Bash gets `tools/bootstrap.sh`, which does the same with
`curl` and `sha256sum`. Corepack was removed from Node 25+, so use the bundled **npm** with a committed
`package-lock.json` and `npm ci`. A `.node-version` file holds `26.13.0`.

### 4.2 Browser for build-time Mermaid and the PDF

`npx playwright install chromium` (Playwright 1.65.0) downloads Chromium into `PLAYWRIGHT_BROWSERS_PATH`. That is a user
folder, so no admin is needed. On Linux, `--with-deps` installs the system libraries; that needs root, which the
Docker build has.

### 4.3 Single-binary checkers

Download them from GitHub releases into `%LOCALAPPDATA%\StrataDocsTools\bin` and check their SHA-256 sums from
`tools/toolchain.json`:

- **lychee 0.24.2** (2026-05-01; nightly builds still appear, the latest on 2026-11-09):
  `lychee-x86_64-pc-windows-msvc.zip` with a published `.sha256`; Linux `lychee-x86_64-unknown-linux-gnu.tar.gz`.
- **typos 1.52.1** (2026-11-09): `typos-v1.52.1-x86_64-pc-windows-msvc.zip`, Linux
  `typos-v1.52.1-x86_64-unknown-linux-musl.tar.gz`. No `.sha256` files are published, so the first download's hash is
  recorded.
- **Pandoc 3.13** (2026-10-26), only for the EPUB: `pandoc-3.13-windows-x86_64.zip`, Linux
  `pandoc-3.13-linux-amd64.tar.gz`. GPL; it is used as a tool and does not affect the license of its output.

### 4.4 Python

The repository's own scripts (`tools/excerpts.py`, `tools/book_lint.py`) use only the standard library, as Strata's
`Tools/` do. They run on MSYS2's Python 3.13 (`/c/msys64/mingw64/bin/python3.exe`) with `-I`. No pip packages are
needed. (Python tools with native wheels, such as Zensical, would need a CPython from `uv` 0.13.7, because MSYS2's
Python rejects `win_amd64` wheels.)

## 5. Exact setup

> **Background only.** This section is a complete configuration written before the plan. Where it differs from
> `plan/site.md` or `plan/pipelines.md`, those files decide (`plan/site.md`, "Where this file overrides the
> research").

### 5.1 Packages (exact pins in `package.json`)

| Package | Version | Date | Role |
| --- | --- | --- | --- |
| `astro` | 7.4.8 | 2026-11-09 | site generator |
| `@astrojs/starlight` | 0.42.10 | 2026-11-06 | docs theme; brings Pagefind 1.x, Expressive Code 0.44, `@astrojs/mdx` (unused) |
| `@astrojs/markdown-remark` | 7.3.6 | 2026-11-05 | the `unified()` Markdown processor (no longer installed by default in Astro 7) |
| `pagefind` | 1.6.0 | 2026-11-01 | pin over Starlight's `^1.5.2` range to get 1.6 (`max_fragments`, sub-result titles, ICU segmentation) |
| `@expressive-code/plugin-line-numbers` | 0.44.3 | 2026-10-21 | line numbers, `startLineNumber` |
| `@expressive-code/plugin-collapsible-sections` | 0.44.3 | 2026-10-21 | fold long excerpts |
| `remark-math` | 6.0.0 | 2023-09-19 | `$…$`, `$$…$$` |
| `rehype-katex` | 7.0.1 | 2024-08-19 | KaTeX at build time |
| `katex` | **0.16.47** | 2026-05-16 | pinned to the 0.16 line that `rehype-katex` (`katex ^0.16.0`) and `mermaid-isomorphic` use, so the CSS we ship matches the renderer. KaTeX 0.19.1 is current but would load a second copy. |
| `mermaid-isomorphic` | 3.1.0 | 2026-02-19 | renders Mermaid to SVG through Playwright (pulls `mermaid` ^11; Mermaid 12.3.0 is current) |
| `playwright` | 1.65.0 | 2026-11-05 | Chromium for Mermaid and the PDF |
| `sharp` | 0.35.5 | 2026-09-27 | image pipeline |
| `svgo` | 4.1.0 | 2026-08-24 | optimize and prefix ids of authored SVGs |
| `starlight-links-validator` | 0.27.0 | 2026-10-09 | internal links and anchors fail the build |
| `starlight-image-zoom` | 0.16.2 | 2026-10-13 | zoom (native `<dialog>`, no client dependencies) |
| `starlight-markdown-blocks` | 0.1.1 | 2026-07-21 | custom `:::` block types (by Starlight's lead maintainer; young: the spike verifies it) |
| `starlight-sidebar-topics` | 0.9.0 | 2026-09-03 | one sidebar per track ("Build the engine" / "Make games") |
| `@fontsource-variable/source-serif-4` | 5.3.1 | 2026-10-11 | body text (OFL-1.1) |
| `@fontsource-variable/inter` | 5.3.0 | 2026-07-19 | headings and UI (OFL-1.1; the editor also uses Inter) |
| `@fontsource-variable/jetbrains-mono` | 5.3.0 | 2026-07-19 | code (OFL-1.1; the editor also uses it) |
| `markdownlint-cli2` | 0.24.0 | 2026-10-21 | Markdown lint (Node ≥ 22) |
| `@axe-core/playwright` | 4.14.0 | 2026-10-15 | accessibility check of sample pages in CI (MPL-2.0, test-only) |
| `unist-util-visit` 5.2.0, `hastscript` 9.0.3, `mdast-util-directive` 3.2.0, `remark-directive` 4.0.0 | | | for our own plugins |

Optional, only when the corresponding phase starts: `starlight-versions` 0.10.2 (not recommended, see §5.10),
`@lunariajs/core` 0.3.0 (translation tracking), `starlight-llms-txt` 0.12.0 (an `llms.txt` for agents that read the book),
`astro-d2` 0.14.1 with d2 0.9.0 (if Mermaid's layouts are not good enough for architecture diagrams),
`cspell` 10.4.1 (see §6.3).

Not used: `starlight-to-pdf` 1.4.0 (last release 2025-04-06, Puppeteer 23), `pagedjs-cli` 0.4.3 (last release 2023),
`rehype-mermaid` 3.0.0 (fine, but its `dark` option uses `prefers-color-scheme`, which ignores Starlight's theme toggle.
Our pre-render step calls `mermaid-isomorphic` directly and adds a cache).

### 5.2 Repository layout (`strata-engine-docs`)

```
strata-engine-docs/
├─ package.json, package-lock.json, .node-version      exact pins, npm ci
├─ astro.config.mjs                                    site, base, Starlight, processor, plugins
├─ ec.config.mjs                                       Expressive Code: themes, plugins, langAlias
├─ book.config.json                                    engine pin {repo, commit, release}, book version, media store
├─ src/
│  ├─ content.config.ts                                docs collection + glossary data collection, schemas
│  ├─ content/docs/                                    the book (.md only; English at the root locale)
│  │  ├─ index.md                                      landing: two tracks, how to read the book
│  │  ├─ engine/<part>/<chapter>/index.md + <section>.md
│  │  ├─ games/<part>/<chapter>/...
│  │  └─ reference/glossary.md                         rendered from the glossary data
│  ├─ content/glossary/terms.yaml                      id, term, aliases, short definition, defining page
│  ├─ plugins/                                         remark-book-*.mjs, rehype-book-*.mjs (§5.5)
│  ├─ components/                                      Starlight overrides (version menu, banner) + web components
│  │  ├─ BookTabs.js, BookCompare.js                   <book-tabs>, <book-compare> custom elements
│  ├─ pages/print/[track].astro                        the whole-book page for PDF/EPUB (§5.9)
│  └─ styles/ book.css, typography.css, print.css, katex.css (imports katex/dist/katex.min.css)
├─ media/                                              submodule: originals (Git LFS) + manifest.json (§5.6)
├─ diagrams/                                           authored .svg (currentColor palette), shared .mmd
├─ public/                                             favicon, robots.txt; generated media/ and diagrams/ (git-ignored)
├─ engine/                                             submodule: the Strata repo at the pinned commit (excerpts only)
├─ tools/
│  ├─ bootstrap.ps1, bootstrap.sh, toolchain.json      no-admin toolchain (§4)
│  ├─ media.mjs                                        sharp pipeline with content-hash cache
│  ├─ diagrams.mjs                                     Mermaid pre-render (light + dark) with cache
│  ├─ excerpts.py                                      check / update code excerpts (§5.8)
│  ├─ book_lint.py                                     dialect rules markdownlint cannot express (§5.4)
│  ├─ stage.mjs                                        copies dist/ into out/<base>/ for lychee and Docker
│  ├─ pdf.mjs, epub.mjs                                whole-book outputs (§5.9)
│  └─ versions.mjs                                     writes versions.json at deploy (§5.10)
├─ .markdownlint-cli2.jsonc, _typos.toml, lychee.toml, .gitattributes (LF, *.png → LFS in media/)
├─ docker/ Dockerfile, Caddyfile, nginx.conf
└─ .github/workflows/book.yml
```

URLs carry no numbers (`/engine/rendering/shadows/`). Reading order comes from `sidebar.order` in the frontmatter,
autogenerated groups and the explicit part list in `astro.config.mjs`.

### 5.3 The Book Markdown dialect (safe for agents and people)

All content is `.md`: CommonMark, GFM (tables, footnotes, task lists, strikethrough), YAML frontmatter, math, generic
directives, and fenced code with meta strings. **No MDX files.** `book_lint.py` fails on any `*.mdx` under
`src/content/`, and no `import`/JSX in content. Every construct the book needs:

| Need | Syntax |
| --- | --- |
| Callouts | `:::note[Optional title]` … `:::` (built in, also `tip`, `caution`, `danger`); `:::pitfall`, `:::why`, `:::exercise` (starlight-markdown-blocks, Aside-variant renderers) |
| Folding solution | `:::solution[Solution to exercise 3.2]` … `:::` → `<details><summary>`, via a custom renderer with `h('details', …)` |
| Tabs | `::::tabs{sync=os}` then `:::tab[Windows]` … `:::` … `::::` → `<book-tabs>` (ARIA tabs pattern; without JS all panels show in order with their labels) |
| Figure with caption | `![Alt text](media:render/ssao/on.png "Caption, numbered automatically")`: an image with a title becomes `<figure>` + `<figcaption>`, "Figure 12.3" in print |
| Before/after slider | `::compare{before="media:render/ssao/off.png" after="media:render/ssao/on.png" alt="…" caption="SSAO off and on"}` → `<book-compare>` built on `<input type="range">` (native keyboard and screen-reader support) |
| Diagram | a ` ```mermaid ` fence (rendered at build time) or `![Alt](diagram:frustum.svg "Caption")` for authored SVG (inlined, ids prefixed, themed with `currentColor`) |
| Math | `$E = mc^2$` inline, `$$ … $$` display; KaTeX `throwOnError: true`, `strict: 'error'` so bad TeX fails the build |
| Glossary link | `:term[draw call]` or `:term[draw calls]{id=draw-call}` → link to the glossary entry with the short definition as `title`; an unknown term fails the build |
| Code excerpt from the engine | a fence with `src="path#L120-L148"` (§5.8) |
| Cross-reference | root-relative links without the base: `[cascades](/engine/rendering/sun-shadows/#cascades)`; the base is added at build time (§5.5) |

**What breaks in MDX, and why the book avoids it.** MDX 3 parses Markdown as JSX + JavaScript. In a C++/graphics
textbook written by agents, these break:

1. `{` and `}` in prose start JavaScript expressions. `the set {a, b}`, `\frac{a}{b}` outside a math node, and C++
   initializer text outside backticks cause compile errors or silently evaluate.
2. `<` followed by a letter starts a JSX tag: `std::vector<int>` and `Ref<Scene>` in prose break the build.
3. HTML comments `<!-- -->` are syntax errors (MDX wants `{/* */}`).
4. Indented code blocks do not exist; four-space-indented code silently becomes a paragraph.
5. Autolinks `<https://…>` are not supported.
6. A line starting with `import` or `export` is parsed as an ES module statement.
7. HTML attributes must be JSX (`className`, `style={{…}}`), and void elements must self-close (`<br/>`).
8. Markdown inside a JSX element needs blank lines around it, or it stays literal text.

Avoid all of it by not using MDX. The plain-`.md` pitfalls that remain are caught by the linters:

- `<word` in prose starts raw HTML even in CommonMark. markdownlint MD033 (no inline HTML) allows only `details`,
  `summary`, `kbd`, `sub`, `sup` and `br`, so `std::vector<int>` outside backticks fails the lint. **Rule: identifiers,
  types, paths and shell variables are always in backticks.**
- `remark-directive` reads `:name` in text as a text directive, so `std::vector` written outside backticks can lose
  `:vector`. Starlight restores unhandled text directives, but `book_lint.py` still flags `::` and `\b\w+:\w` outside code.
  (The exact restoration behavior under `unified()` is a spike item.)
- `remark-math` reads `$5 and $10` as inline math. Write `\$`, or put shell variables in backticks. `book_lint.py` flags
  `$` followed by a digit.
- Our plugins fail the build on unknown container or leaf directives, so a typo like `:::pitfal` cannot silently render
  as text.

Frontmatter schema (`docsSchema({ extend: … })`): `title`, `description`, `sidebar.order`, `track: engine | games | both`,
`requires: [slug…]` (pages the reader must have read; `book_lint.py` checks that each comes earlier in reading order,
which enforces "nothing assumed that the book has not taught"), `engineVersion` (the release the page was last checked
against), `status: draft | review | done` (`draft: true` pages are left out of production builds).

### 5.4 Configuration outline

`astro.config.mjs`:

```js
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import starlightLinksValidator from 'starlight-links-validator';
import starlightImageZoom from 'starlight-image-zoom';
import starlightMarkdownBlocks from 'starlight-markdown-blocks';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import { remarkBook } from './src/plugins/remark-book.mjs';   // tabs, compare, figure, media:, diagram:, term, mermaid, excerpt meta
import { rehypeBook } from './src/plugins/rehype-book.mjs';   // base prefix for root links, figure numbering, svg inlining
import { bookBlocks } from './src/plugins/blocks.mjs';        // pitfall, why, exercise, solution renderers

const base = process.env.BOOK_BASE ?? '/';                       // e.g. '/strata-book/v0.8/'
const site = process.env.BOOK_SITE ?? 'http://localhost:4321';

export default defineConfig({
	site,
	base,
	trailingSlash: 'always',
	build: { format: 'directory' },
	compressHTML: true,               // Astro 7 defaults to 'jsx', which can drop spaces between inline elements
	markdown: {
		processor: unified({
			remarkPlugins: [remarkMath, remarkBook],
			rehypePlugins: [[rehypeKatex, { throwOnError: true, strict: 'error', output: 'htmlAndMathml' }], [rehypeBook, { base }]],
		}),
	},
	integrations: [
		starlight({
			title: 'Strata Engine Docs',
			locales: { root: { label: 'English', lang: 'en' } },   // translations later add e.g. de: { … }
			tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 4 },
			pagination: true,
			lastUpdated: true,
			markdown: { headingLinks: true },
			pagefind: { /* ranking tuned in the spike */ },
			customCss: ['./src/styles/typography.css', './src/styles/book.css', './src/styles/katex.css', './src/styles/print.css'],
			components: { /* SiteTitle: version menu, Banner: old-version notice */ },
			plugins: [
				starlightSidebarTopics([ /* Build the engine, Make games, Reference */ ]),
				starlightMarkdownBlocks({ blocks: bookBlocks }),
				starlightImageZoom(),
				starlightLinksValidator({ errorOnInvalidHashes: true, errorOnRelativeLinks: true }),
			],
		}),
	],
});
```

`ec.config.mjs`:

```js
import { defineEcConfig } from '@astrojs/starlight/expressive-code';
import { pluginLineNumbers } from '@expressive-code/plugin-line-numbers';
import { pluginCollapsibleSections } from '@expressive-code/plugin-collapsible-sections';

export default defineEcConfig({
	plugins: [pluginLineNumbers(), pluginCollapsibleSections()],
	defaultProps: { showLineNumbers: false, overridesByLang: { 'cpp,hlsl,slang,cmake,python': { showLineNumbers: true } } },
	shiki: { langAlias: { slang: 'hlsl' } },   // Shiki has no Slang grammar; Strata's Slang is HLSL syntax
	themes: ['github-dark', 'github-light'],   // final choice is a design decision
});
```

An authored fence then reads:

````md
```cpp title="Strata/src/Strata/Scene/Scene.cpp" src="Strata/src/Strata/Scene/Scene.cpp#L120-L148" startLineNumber=120 {4-6} ins={9}
…exact engine lines…
```
````

Line markers (`{4-6}`) count from the block's first line, not the file's (verify in the spike). Because they are
relative to the excerpt, they stay valid when the excerpt moves.

### 5.5 Our own plugins (custom work, all small)

| Piece | Kind | What it does | Fails the build when |
| --- | --- | --- | --- |
| `remark-book` media | remark | `media:` images → `<picture>` with AVIF `srcset` + WebP fallback, `width`/`height`, `loading="lazy"`, `decoding="async"`, `sizes`; the image node is replaced before Astro collects images | a manifest entry is missing; alt text is empty |
| figure | remark | image with title → `<figure>`, caption, per-chapter number | caption missing on a `media:` image |
| compare | remark + web component | `::compare` → `<book-compare>` with two aligned pictures and a range input | sizes of the pair differ |
| tabs | remark + web component | `::::tabs` / `:::tab` → `<book-tabs>`; `sync` key remembers the choice (like Starlight's `syncKey`) | a tab has no label |
| term | remark | `:term[…]` → glossary link + `title` | unknown term |
| mermaid | remark | ` ```mermaid ` fence → `<figure>` with light and dark `<img>` (SVG files from `tools/diagrams.mjs`), switched by `:root[data-theme]` CSS. This runs in remark, so Expressive Code never sees the fence as code. | a rendered SVG is missing (`npm run diagrams` not run) |
| svg diagrams | rehype | inlines authored SVG (svgo `prefixIds`) so `currentColor` follows the theme | file missing |
| base links | rehype | prefixes `base` to root-relative links (Markdown links are not rewritten by Astro) | n/a (lychee checks the result) |
| blocks | config | pitfall / why / exercise (Aside variants), solution (`<details>`) | unknown directive (remark-book) |
| version menu + banner | component overrides | reads `../versions.json`; banner on non-latest versions | n/a |
| print book | Astro page | §5.9 | n/a |

### 5.6 Image pipeline

- **Originals** (lossless PNG, up to 3840×2160, on/off pairs) live in a separate repository, `strata-engine-docs-media`,
  with Git LFS, checked out as the `media/` submodule. Expect roughly 10–20 GB of 4K PNGs (estimate). Keeping them out
  of the book repository's history leaves it cloneable in seconds. `media/manifest.json` records, per image, its SHA-256,
  size and capture metadata (engine commit, project, scene, preset). The capture plan is a separate document.
- **`tools/media.mjs`** (sharp 0.35.5) produces, per original, AVIF at widths 960, 1920 and 3840 (quality ≈ 55,
  effort 4) and one WebP at 1920 as the fallback and for PDF/EPUB. Pairs share their widths, so the slider aligns.
  Outputs go to `.cache/media/<sha256>-<settings-hash>/…` and are copied into `public/media/` (git-ignored). A change of
  original or settings re-encodes only that image. The script runs with a worker pool (half the cores) and writes
  `src/data/media.json` (paths, widths, intrinsic size) for the remark plugin.
- AVIF works in every browser Starlight 0.42 supports (Chromium ≥ 116, Safari ≥ 17, Firefox ≥ 125), so the WebP is only
  a fallback. Zoom opens the 3840 variant. Lossless originals are never copied into the site.
- First full encode: on the order of tens of minutes for ~1000 4K images (estimate, measured in the spike). Later builds
  take seconds. CI caches `.cache/` by the hash of `media/manifest.json`, and the Dockerfile uses a BuildKit cache
  mount.

### 5.7 Search

Starlight runs Pagefind after `astro build`. Settings to tune in the spike: weights for headings and the glossary;
`data-pagefind-ignore` on line-number gutters and long generated tables (code stays searchable, because readers search
for function names); `max_fragments` if the server limits file counts. Each published version has its own index, so
search stays within the version being read. Pagefind segments by the page's `lang`, so a later translation gets its
own index automatically.

### 5.8 Keeping code excerpts in sync with the engine (`tools/excerpts.py`)

- **Pin.** `book.config.json` holds `engine.commit` (full SHA, now `822a7a46…` on `main`) and `engine.release`. The
  `engine/` submodule is pinned to the same commit and is used only by this tool. **The site build itself does not need
  the engine**, because excerpt bodies are committed in the Markdown. Pages stay readable on GitHub, are searchable, and
  Docker builds do not clone the engine.
- **Syntax.** Fence meta `src="<path>#L<a>-L<b>"`, optionally several ranges `#L120-L130,L150-L160` (joined by a
  language-appropriate `// …` elision line), or `#region=<Name>` if the engine later adopts `// docs-region: <Name>` /
  `// docs-endregion` comments (not required now; changing the engine is a separate decision).
- **`excerpts.py check`** (CI, and before every commit): for each fence it reads the file with
  `git -C engine show <commit>:<path>` (no checkout state involved), compares the lines byte for byte after normalizing
  tabs to the engine's tab width, and checks that `title` equals the path and `startLineNumber` equals the range start.
  Any difference fails with a diff.
- **`excerpts.py update --to <commit>`** (when the book moves to a new engine release): for each excerpt it looks for
  the old text in the new file. A unique exact match updates only the line numbers. Otherwise the tool maps the range
  through `git diff <old> <new> -- <path>` hunks. If the excerpted lines themselves changed, it rewrites the body and
  adds the page to a review list printed at the end, because the prose around a changed excerpt must be re-read. It
  never guesses silently.
- **Also checked:** every path named in prose in backticks that looks like an engine path (`Strata/src/…`,
  `StrataEditor/…`) must exist at the pin, and every `ST_*` macro or `Class::Method` the glossary links to must still
  exist (a `git grep` at the pin).

### 5.9 Print, PDF and EPUB

- **Per-page print:** Starlight's print styles plus `print.css` (hide chrome, show link URLs for external links, expand
  `<details>` and all tab panels, light theme forced).
- **Whole book:** `src/pages/print/[track].astro` renders every entry of a track in reading order (`getCollection` +
  `render()`), one chapter per page break. A post-build step rewrites cross-page links to in-document anchors.
- **PDF:** `tools/pdf.mjs` opens that page in Playwright Chromium and calls `page.pdf({ format: 'A4', printBackground:
  true, outline: true, tagged: true })`. `outline` and `tagged` (an accessible PDF) are documented Playwright options.
  Running heads and page numbers come from CSS `@page` margin boxes with `counter(page)`, which Chrome supports since
  131. Chromium cannot print ToC page numbers (`target-counter`). If that is wanted, Vivliostyle CLI 11.4.0 (AGPL-3.0
  tool; the PDF it produces is not affected) renders the same HTML with full paged-media CSS. Risk: one HTML page with
  half a million words and ~1000 images may exhaust Chromium. The plan is then one PDF per part, merged.
- **EPUB:** `tools/epub.mjs` prepares the print HTML (KaTeX MathML kept and HTML spans dropped, pictures replaced by
  the 1920 WebP, which EPUB 3.3 allows, SVG diagrams as files) and runs `pandoc --to epub3 --toc --split-level=2`.
  This is phase 2. It is feasible, but how faithfully Pandoc's HTML reader handles MathML must be checked first.

### 5.10 Versioning by engine release

Simple scheme, no plugin:

- `main` of the book tracks the engine pin of the release being written. At each engine release, tag the book
  `book-v<release>`, then build that tag with `BOOK_BASE=/<root>/v<release>/`. Published versions are immutable folders
  on the server, rebuilt only for a fix (from their tag, with the same Dockerfile).
- `/<root>/latest/` is a server-side alias (a rewrite or symlink) to the newest version. `/<root>/` redirects to it.
  `/<root>/versions.json` (written by `tools/versions.mjs` at deploy) lists versions. The version menu override reads it,
  and pages of older versions show a banner and `<link rel="canonical">` to the same page under `latest` when it exists.
- Why not `starlight-versions` 0.10.2: it copies the whole docs tree per version into the repository (its own guide
  names the cost: many files, harder change tracking, slower builds), says it is "still in early development", and
  would multiply ~1000 images per version.

### 5.11 Translations later

Configure `locales: { root: { lang: 'en' } }` now (done above). A translation adds `src/content/docs/<lang>/` mirroring
the tree. Untranslated pages fall back to English with Starlight's notice (`starlight-links-validator`
`errorOnFallbackPages` stays `true` until a translation is complete), Lunaria tracks staleness, Pagefind indexes per
language, glossary YAML gains per-language fields, and media captions live in Markdown, not in images.

### 5.12 Typography, theme and accessibility

Body in Source Serif 4 at ~1.125rem/1.6 with a measure of ~70ch (`--sl-content-width`). Headings and UI in Inter, code
in JetBrains Mono. All three are self-hosted through `@fontsource-variable`, OFL-1.1, and credited in the book's
`ThirdPartyNotices.md`. Dark and light come from Starlight's toggle. Diagrams and SVG follow it (§5.5). Accessibility:
alt text is required by the media plugin, the tabs and slider follow WAI-ARIA patterns, math is MathML for screen
readers, and CI runs `@axe-core/playwright` on a fixed sample of pages (one per component type), failing on serious or
critical violations.

### 5.13 Commands

`package.json` scripts:

```json
{
  "scripts": {
    "media": "node tools/media.mjs",
    "diagrams": "node tools/diagrams.mjs",
    "dev": "npm run media && npm run diagrams && astro dev",
    "build": "npm run media && npm run diagrams && astro build",
    "lint": "markdownlint-cli2 \"src/content/**/*.md\" && typos && python -I tools/book_lint.py",
    "excerpts": "python -I tools/excerpts.py check",
    "links": "node tools/stage.mjs && lychee --config lychee.toml --offline --include-fragments --root-dir out \"out/**/*.html\"",
    "a11y": "node tools/a11y.mjs",
    "pdf": "node tools/pdf.mjs",
    "epub": "node tools/epub.mjs",
    "check": "npm run lint && npm run excerpts && npm run build && npm run links && npm run a11y"
  }
}
```

On the authoring machine (PowerShell):

```powershell
git clone --recurse-submodules <book-repo> ; cd strata-engine-docs
. .\tools\bootstrap.ps1                  # Node 26.13.0, lychee, typos into %LOCALAPPDATA%\StrataDocsTools
npm ci
npx playwright install chromium
npm run dev                              # http://localhost:4321
npm run check                            # what CI runs
```

On a Linux server (Ubuntu 24.04 or Debian 13, no Docker):

```sh
git clone --recurse-submodules <book-repo> && cd strata-engine-docs
./tools/bootstrap.sh                     # same pins, ~/.local/share/strata-docs-tools
. ./tools/env.sh
npm ci
npx playwright install --with-deps chromium   # needs sudo for the system libraries
BOOK_BASE=/strata-book/v0.8/ BOOK_SITE=https://example.org npm run build
node tools/stage.mjs                     # out/strata-book/v0.8/…
rsync -a --delete out/strata-book/v0.8/ /srv/www/strata-book/v0.8/
```

`docker/Dockerfile` (multi-stage; the build context is the book repository with its `media/` submodule checked out):

```dockerfile
# syntax=docker/dockerfile:1
FROM node:26.13.0-trixie-slim AS build
WORKDIR /book
COPY package.json package-lock.json ./
RUN npm ci
RUN npx playwright install --with-deps chromium
COPY . .
ARG BOOK_BASE=/
ARG BOOK_SITE=http://localhost
ENV BOOK_BASE=${BOOK_BASE} BOOK_SITE=${BOOK_SITE}
RUN --mount=type=cache,target=/book/.cache npm run build && node tools/stage.mjs

FROM caddy:2.11.9-alpine
COPY docker/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /book/out /srv
```

`docker/Caddyfile`:

```
:80 {
	root * /srv
	encode zstd gzip
	@immutable path */_astro/*
	header @immutable Cache-Control "public, max-age=31536000, immutable"
	try_files {path} {path}/index.html
	file_server
	handle_errors {
		rewrite * {$BOOK_BASE}404.html
		file_server
	}
}
```

`docker/nginx.conf` (alternative to Caddy; base `/strata-book/` shown):

```nginx
server {
	listen 80;
	root /srv;
	gzip on; gzip_types text/css application/javascript image/svg+xml application/json;
	location /strata-book/ { try_files $uri $uri/ $uri/index.html =404; }
	location ~ /_astro/ { add_header Cache-Control "public, max-age=31536000, immutable"; }
	error_page 404 /strata-book/latest/404.html;
}
```

(`nginx:1.30-alpine` is the current stable image line, 1.30.6.) Pagefind's `.pf_*` files are already compressed; serving
them as `application/octet-stream` with no extra encoding is correct.

## 6. Quality tools

### 6.1 Links, anchors and images: lychee 0.24.2 (+ the build's own checks)

Three layers. (1) `starlight-links-validator` fails `astro build` on broken internal links and missing anchors.
(2) Our plugins and Astro fail on missing media, diagrams and glossary terms. (3) **lychee** on the staged output
(`out/<base>/…`) with `--offline --include-fragments --root-dir out` checks every `href` and `src` in the real HTML,
with the real base path. This last layer does not depend on the framework and is the final gate; it also catches
problems in our own generated markup. External links are checked by a weekly scheduled job without `--offline`,
reporting rather than blocking, because third-party sites fail transiently. Fallback: `linkinator` 8.1.0 (npm).

### 6.2 Markdown lint: markdownlint-cli2 0.24.0

`.markdownlint-cli2.jsonc`: MD033 with `allowed_elements: [details, summary, kbd, sub, sup, br]`, MD040 (fences need a
language), MD045 (images need alt text), MD024 `siblings_only`, MD013 off (one sentence per line is recommended for
diffs, but not enforced), MD046 `fenced`. Dialect rules markdownlint cannot express (no MDX, `::`/`:x` outside code,
`$` + digit, `requires` order, heading depth ≤ 4, frontmatter `track`) are in `tools/book_lint.py`.

### 6.3 Spelling: typos 1.52.1 as the gate

typos has a very low false-positive rate, so it can fail CI without a dictionary of engine identifiers. It is
configured in `_typos.toml` (exclude `public/`, `media/`, excerpt bodies via `extend-ignore-re` on `src=` fences).
cspell 10.4.1 is optional, run by authors with a project dictionary (`Strata`, `NVRHI`, `EnTT`, `box3d`, `Slang`, …),
and advisory because its false positives at 500k words would block agents. Prose style tools (Vale) are not
recommended now: no maintained style package fits a textbook voice, and rules would need writing first.

### 6.4 CI (`.github/workflows/book.yml`)

Jobs: `lint` (markdownlint, typos, book_lint), `excerpts` (needs the `engine` submodule at the pin), `build` (cache
`.cache/` and `node_modules/.astro`; Playwright cache), `links` (lychee offline), `a11y`, then `budgets`, which fails if
the measured numbers exceed §7's limits (build time, largest page weight, Pagefind payload for a fixed query). The
weekly job checks external links. All versions come from `package-lock.json` and `tools/toolchain.json`.

## 7. Spike before writing content

Build a throwaway branch with synthetic content at full scale: 300 pages × 1,800 words (generated prose), 3,000 code
blocks (half of them real engine excerpts through `excerpts.py`), 300 Mermaid diagrams, 1,000 4K PNGs in 500 pairs,
200 formulas, every custom block, a glossary of 400 terms, `BOOK_BASE=/strata-book/v0.0/`. Measure and accept:

| Measure | Budget |
| --- | --- |
| Cold build, media cache empty (authoring machine) | record; media encode dominates, run once |
| Warm build, media and diagram caches full | ≤ 5 min |
| Peak Node RSS during `astro build` | ≤ 6 GB (else set `--max-old-space-size` and record) |
| Pagefind network payload for a 2-word query | ≤ 300 KB |
| Largest HTML page (gzip) | ≤ 250 KB; sidebar share recorded |
| Lighthouse performance / accessibility, mobile, a 6,000-word chapter | ≥ 95 / 100 |
| Things to confirm work | starlight-markdown-blocks under `unified()`; `<details>` solution renderer; text-directive restoration (`std::vector` outside code); Expressive Code line markers relative to `startLineNumber`; image zoom on our `<picture>`; links-validator with base-less root links + our base rehype step; KaTeX `throwOnError` failing the build; Mermaid fences reaching our remark step before Expressive Code; whole-book PDF memory and time; Pandoc EPUB with MathML |

If Starlight misses the warm-build or payload budgets after tuning, or two "confirm" items need a fork, fall back to
Quarto (§3) before content is written.

## 8. Risks and how they are handled

- **Framework churn** (Starlight 0.x breaking minors; Astro 6 → 7 in about three months): exact pins, a lockfile, and
  one deliberate upgrade per engine wave with `npx @astrojs/upgrade` (0.8.1), then the full `npm run check`. Custom code
  uses only remark/rehype, web components and documented component overrides.
- **Sätteri becoming the only processor:** Astro keeps `unified()` as an option in 7.x. If it is ever deprecated, port
  our plugins to Sätteri's MDAST/HAST plugin API (`satteri-katex` 0.3.0 already exists for math).
- **Young plugins** (`starlight-markdown-blocks` 0.1.1, `starlight-image-zoom`): each could be replaced by about 150
  lines of our own remark/rehype code. Neither is load-bearing for the content syntax.
- **Media size:** a separate LFS repository. If LFS hosting is unwanted, use a plain object store keyed by the
  manifest's SHA-256.
- **Whole-book PDF:** may need per-part rendering or Vivliostyle. It is "if feasible", so it does not block the site.
- **katex/mermaid version lag** behind `rehype-katex` and `mermaid-isomorphic`: pinned on purpose so the CSS and the
  renderer match. Revisit at each upgrade.

## 9. Sources (all read 2026-11-10)

Registries and releases (versions, dates, engines, licenses):

- npm registry metadata: https://registry.npmjs.org/@astrojs/starlight, https://registry.npmjs.org/astro,
  https://registry.npmjs.org/@astrojs/markdown-remark, https://registry.npmjs.org/@astrojs/mdx,
  https://registry.npmjs.org/vitepress, https://registry.npmjs.org/@docusaurus/core, https://registry.npmjs.org/pagefind,
  https://registry.npmjs.org/astro-expressive-code, https://registry.npmjs.org/starlight-links-validator,
  https://registry.npmjs.org/starlight-image-zoom, https://registry.npmjs.org/starlight-markdown-blocks,
  https://registry.npmjs.org/starlight-versions, https://registry.npmjs.org/starlight-sidebar-topics,
  https://registry.npmjs.org/rehype-katex, https://registry.npmjs.org/katex, https://registry.npmjs.org/remark-math,
  https://registry.npmjs.org/mermaid, https://registry.npmjs.org/mermaid-isomorphic, https://registry.npmjs.org/rehype-mermaid,
  https://registry.npmjs.org/playwright, https://registry.npmjs.org/sharp, https://registry.npmjs.org/svgo,
  https://registry.npmjs.org/markdownlint-cli2, https://registry.npmjs.org/cspell, https://registry.npmjs.org/satteri-katex,
  https://registry.npmjs.org/@vivliostyle/cli, https://registry.npmjs.org/starlight-to-pdf, https://registry.npmjs.org/pagedjs-cli,
  https://registry.npmjs.org/@easyops-cn/docusaurus-search-local, https://registry.npmjs.org/@axe-core/playwright,
  https://registry.npmjs.org/@fontsource-variable/source-serif-4, https://registry.npmjs.org/tm-grammars
- PyPI: https://pypi.org/pypi/zensical/json, https://pypi.org/pypi/mkdocs-material/json, https://pypi.org/pypi/mkdocs/json
- crates.io: https://crates.io/api/v1/crates/mdbook
- GitHub releases: https://github.com/withastro/starlight/releases, https://github.com/pagefind/pagefind/releases/tag/v1.6.0,
  https://github.com/zensical/zensical/releases/tag/v0.1.0, https://github.com/squidfunk/mkdocs-material/releases/tag/9.8.1,
  https://github.com/rust-lang/mdBook/releases, https://github.com/quarto-dev/quarto-cli/releases/tag/v1.11.9,
  https://github.com/vuejs/vitepress/releases/tag/v2.0.0-alpha.21, https://github.com/lycheeverse/lychee/releases/tag/lychee-v0.24.2,
  https://github.com/crate-ci/typos/releases/tag/v1.52.1, https://github.com/jgm/pandoc/releases/tag/3.13,
  https://github.com/astral-sh/uv/releases
- Node.js: https://nodejs.org/dist/index.json, https://nodejs.org/dist/v26.13.0/SHASUMS256.txt
- Docker images: https://hub.docker.com/_/node (tag `26.13.0-trixie-slim`), https://hub.docker.com/_/caddy (2.11.9),
  https://hub.docker.com/_/nginx (1.30.6), https://mcr.microsoft.com/v2/playwright/tags/list (`v1.65.0-noble`)

Documentation and announcements:

- Starlight changelog (0.39–0.42 breaking changes): https://github.com/withastro/starlight/blob/main/packages/starlight/CHANGELOG.md
- Starlight configuration: https://starlight.astro.build/reference/configuration/
- Starlight authoring (asides, code block syntax): https://starlight.astro.build/guides/authoring-content/
- Astro 7 upgrade guide (Sätteri default, `unified()`): https://docs.astro.build/en/guides/upgrade-to/v7/
- Astro Markdown guide (Sätteri options, plugins): https://docs.astro.build/en/guides/markdown-content/
- Astro images (cache dir, responsive, `public/`): https://docs.astro.build/en/guides/images/
- Astro 6.4 post (Sätteri introduced, speed claim): https://astro.build/blog/astro-640/
- Sätteri display-math pitfall: https://dev.to/ashish-codejourney/astro-7-renders-your-display-maths-as-a-code-block-and-wont-tell-you-cp0
- Expressive Code syntax highlighting (`langs`, `langAlias`): https://expressive-code.com/key-features/syntax-highlighting/
- Expressive Code configuration: https://expressive-code.com/reference/configuration/
- Pagefind: https://pagefind.app/
- starlight-links-validator options: https://starlight-links-validator.vercel.app/configuration/
- starlight-markdown-blocks: https://delucis.github.io/starlight-markdown-blocks/getting-started/,
  https://delucis.github.io/starlight-markdown-blocks/custom-blocks/
- starlight-versions strategy: https://starlight-versions.vercel.app/guides/about-versioning/
- Zensical roadmap: https://zensical.org/roadmap/ ; FAQ: https://zensical.org/docs/community/faqs/
- Material maintenance announcement: https://github.com/squidfunk/mkdocs-material/issues/8523
- Docusaurus 3.10 (last 3.x, Node 18 dropped): https://docusaurus.io/blog/releases/3.10 ; changelog: https://docusaurus.io/changelog
- VitePress local search: https://vitepress.dev/reference/default-theme-search ; implementation:
  https://github.com/vuejs/vitepress/blob/v1.6.4/src/node/plugins/localSearchPlugin.ts
- Quarto search: https://quarto.org/docs/websites/website-search.html ; implementation:
  https://github.com/quarto-dev/quarto-cli/blob/v1.11.9/src/resources/projects/website/search/quarto-search.js
- mdBook changelog: https://github.com/rust-lang/mdBook/blob/master/CHANGELOG.md ; MathJax from cdnjs:
  https://github.com/rust-lang/mdBook/blob/v0.5.4/crates/mdbook-html/front-end/templates/index.hbs
- rehype-mermaid strategies: https://github.com/remcohaszing/rehype-mermaid
- Playwright `page.pdf` (`outline`, `tagged`): https://playwright.dev/docs/api/class-page#page-pdf
- Chrome page margin boxes (Chrome 131): https://developer.chrome.com/blog/print-margins
