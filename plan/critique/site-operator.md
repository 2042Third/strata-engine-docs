# Critique of the plan: the site operator and build engineer

Key: `site-operator`. Lens: `site.md` read as the specification an engineer builds from and the owner deploys from;
`pipelines.md`, `process.md` and `research/framework.md` where they feed the build.

## How this was checked

- Read fully: the nine plan files and `research/framework.md`; `research/captures.md` searched for sizes and formats;
  the inventories searched for the sizes of the generated reference (151 commands, 165 host functions, 1,592 terms).
- Versions: read on 2026-11-10 from the npm registry (`/latest` of every named package), `nodejs.org/dist/index.json`,
  the GitHub releases API (Caddy, Quarto, lychee), `nginx.org/en/CHANGES-1.30`, Docker Hub tags.
- Behavior: read from the shipped code of the pinned packages (tarballs unpacked into a scratch folder:
  `@astrojs/starlight` 0.42.10, `starlight-links-validator` 0.27.0, `starlight-markdown-blocks` 0.1.1,
  `astro-rehype-relative-markdown-links` 0.19.2, `@astrojs/sitemap` 3.7.4) and from `rehype-katex` 7.0.1 and
  `mermaid-isomorphic` 3.1.0 in the worktree's `node_modules`; from the docs of Astro (configuration reference),
  Expressive Code (text markers, line numbers), Pagefind (releases, hosting), Caddy (`handle_errors`), GitHub
  (runners, caching, LFS, large files).
- An untracked smoke build already exists in the worktree (`astro.config.mjs` with `base: '/strata-engine-docs'`,
  `dist/`, `package-lock.json`). Its `dist/index.html`, `dist/404.html`, sitemap and Pagefind output were read as
  evidence. Nothing was built or run.
- The engine was only read (`git ls-tree`, `git show` at `822a7a46`, `git remote`); both GitHub repositories
  (`2042Third/GameEngine`, `2042Third/strata-engine-docs`) are public (GitHub API, unauthenticated).

## Versions: they exist and fit together (2026-11-10)

| Piece | Plan says | Registry today | Fits? |
| --- | --- | --- | --- |
| `astro` | 7.4.8 | 7.4.8 (latest), engines `node >=22.23.4` | yes |
| `@astrojs/starlight` | 0.42.10 | 0.42.10 (latest), peers `astro ^7.2.10`, `@astrojs/markdown-remark ^7.3.0` | yes; `@astrojs/markdown-remark` is a **peer**, so it must be listed (site.md's table omits it; the smoke `package.json` has 7.3.6) |
| `pagefind` | 1.6.0 | 1.6.0 (2026-11-01); Starlight depends `^1.5.2` and `@pagefind/default-ui ^1.3.0` (lock: 1.6.0) | yes; note Pagefind 1.5 says its Component UI "replaces the Default UI", which Starlight still uses |
| Expressive Code | 0.44.3 | `astro-expressive-code` 0.44.3; plugins 0.44.3; Starlight depends `^0.44.0` | yes |
| KaTeX | 0.16.47 | 0.16.47 exists (2026-05-16); latest is 0.19.1; `rehype-katex` 7.0.1 wants `^0.16.0` | yes, pinned on purpose |
| Mermaid | not named in site.md | `mermaid-isomorphic` 3.1.0 depends on `mermaid ^11.0.0` (lock overrides to 11.17.2); Mermaid latest is 12.3.0 | works, but the book's diagrams are Mermaid 11 while every live editor shows 12 |
| `sharp` | not versioned in site.md | 0.35.5, `node >=20.9.0`; lock has linux-x64, linuxmusl and win32 binaries | yes |
| Node | 26.13.0 LTS | 26.13.0 "Lithium", 2026-10-28 (24.22.2 "Krypton" is maintenance LTS) | yes |
| Quarto (fallback) | 1.11.9 | 1.11.9 stable 2026-10-30 (1.12.1 pre-release) | yes |
| nginx | not versioned | stable 1.30.6 (2026-10-14, five CVE fixes incl. one in `alias` after `rewrite`); `nginxinc/nginx-unprivileged:1.30.6-alpine*` tags exist | use ≥ 1.30.6 |
| Caddy | not versioned | 2.11.9 (2026-11-05) | yes |
| lychee | not named in site.md (framework.md: 0.24.2) | 0.24.2 (2026-05-01) is the latest release | yes |

Nothing named is fictional or incompatible. The problems are below.

## Findings, most severe first

### 1. Blocker — the spike has no pass or fail line (site.md:102, 118-123)

`site.md` check 9 says the budgets are "set by the spike", and the spike "reports build time and memory … The budgets
of check 9 are set from it. If Starlight cannot meet them, the fallback is tried". A budget derived from the
measurement it judges can never fail, so the only framework decision the plan makes before 282 pages are written
has no criterion. `framework.md` §7 had numbers (warm build ≤ 5 min, RSS ≤ 6 GB, 300 KB search payload, 250 KB
largest page, Lighthouse 95/100); `site.md` dropped them. The fallback is also only real before content exists:
`:::why`, `:term[x]`, `::compare{…}` and fence meta `src="…"` have no Pandoc spelling (`::: {.why}`,
`[x]{.term}`, `{.cpp src="…"}`), and every plugin would have to be rewritten as a Lua filter, so "the move would not
rewrite pages" (site.md:21-22) means a converter plus a rewrite of the machine.

**Change:** replace check 9's "(set by the spike)" with the budget table of [appendix E](#e-spike-what-to-measure-and-the-budgets),
written into `site.md` before the spike starts, each row with its machine (i7-13700K and GitHub `ubuntu-latest`) and
what happens on failure. Add: "the spike's verdict is final; after the pilot starts, the framework is not revisited
before 0.8.0".

### 2. Major — `site.md` and `research/framework.md` contradict each other on the things a builder copies (site.md:8)

`site.md` sends the builder to `framework.md` "for the comparison and the reasons", but `framework.md` §5 is a full
configuration that differs from the plan in at least these places:

| Topic | `framework.md` | The plan |
| --- | --- | --- |
| Environment variables | `BOOK_BASE`, `BOOK_SITE` (326-327) | `DOCS_BASE`, `DOCS_SITE` (site.md:29) |
| Content tree and URLs | `engine/<part>/<chapter>/index.md`, `games/…` (228-229) | `<part>/<chapter>.md`, `/<part>/<chapter>/` (site.md:47, book.md:129) |
| Cross-page links | root-relative without base (275) and `errorOnRelativeLinks: true` (356) | relative `.md` paths; absolute links fail (site.md:31-33) |
| Pictures | lossless PNG originals in an LFS submodule `media/` (407-410) | one lossy published file in this repository, no lossless archive (README.md:38-40, pipelines.md:87-88) |
| Derived images | AVIF at 960/1920/3840 + one WebP at 1920 (411-415) | AVIF and WebP at 960/1920/3840 (site.md:18) |
| Versions | every version in `/<root>/v<release>/`, `latest/` alias, root redirects (472-477) | current book at the root of the base, old ones under `/v0.8/` (site.md:88-90) |
| Front matter | `track`, `requires`, `engineVersion`, `status: draft\|review\|done` (303-306) | `tracks`, `prerequisites`, `engine`, `kind`, `level`, `learn`, `status: draft\|reviewed\|final` (style.md:37-48) |
| Deployment folder and server | `docker/`, Dockerfile serving with Caddy (251, 559-561) | `deploy/`, container "serves it with nginx" (site.md:55, 114) |
| Tools folder | `%LOCALAPPDATA%\StrataDocsTools` (109) | `.tools/` in the repository (site.md:19) |
| Glossary file | `src/content/glossary/terms.yaml` (236) | `src/content/glossary.json` (pipelines.md:139) |
| Engine pin | `book.config.json` + `engine/` submodule (224, 241) | `engine.pin` + `--engine <clone>` (site.md:56, pipelines.md:7-11) |
| Sidebar | `starlight-sidebar-topics` per track (353) | the sidebar follows the parts (site.md:79) |
| Site title | "Strata Engine Docs" (343) | "The Strata Engine Book" (book.md:3) |

**Change:** add to `site.md` a section "Where this file overrides `research/framework.md`" with this table, and a
banner on `framework.md` §5: "Background only; `plan/site.md` and `plan/pipelines.md` decide." Fix the plan's own
gaps the table shows: `labs/` and `diagrams/` are missing from the layout (site.md:42-59; pipelines.md:82 uses
`labs/`).

### 3. Major — the image pipeline upscales, re-encodes lossy files and destroys the pixel crops the book teaches with (site.md:18, pipelines.md:84-88)

- Most figures are 1920×1080 (pipelines.md:84; captures.md:420-423 keeps 3840×2160 "only where detail is the point").
  A 3840 width "from one published original" is therefore an upscale for nearly every picture: bytes with no detail.
- The published file is already lossy WebP q92 (pipelines.md:87). AVIF and WebP derived from it are a second lossy
  generation, and the 1920 WebP output re-encodes the 1920 WebP input for nothing.
- Crops "are enlarged by whole factors without smoothing" (pipelines.md:85-86) so that single pixels show. Deriving
  960 (a 0.75 or 0.5 resample with sharp's default Lanczos kernel) and lossy AVIF smooth exactly the stair-steps,
  crawl and shadow acne those crops exist to show. The same applies to the slider pairs of anti-aliasing, TAA and
  shadow filters: a quality-55 AVIF (framework.md:411) removes high-frequency aliasing on its own, so "off" can look
  like "on".
- Two formats double encode time and storage for no reader: AVIF works in every browser Starlight supports
  (framework.md:416).
- Size: 600 pictures × (AVIF 960/1920/3840 ≈ 60+200+400 KB, WebP 960/1920/3840 ≈ 120+350+1,000 KB) ≈ 1.2-1.5 GB per
  deployed version (estimate); with the change below ≈ 0.2-0.3 GB.

**Change (site.md:18 and pipelines.md:84-88):** "Renders: the published 1920 file is served unchanged and one 960
AVIF (quality ≥ 80) is derived; 3840 only when the capture is 3840. Crops and editor pictures: lossless, served at
their exact pixel size, never resampled or re-encoded; publish crops at capture size (320×180) and enlarge in CSS with
`image-rendering: pixelated` instead of in the file. Slider pairs: both sides encoded with identical settings at
quality ≥ 90, or lossless. One format per picture (AVIF for renders, lossless WebP for crops and UI). Derived file
names carry a content hash (`<id>.<hash8>.<width>.avif`) so they can be cached for a year." Add to the spike: encode
time per picture and dist size, measured on the engine's own renders (see finding 16).

### 4. Major — "KaTeX errors fail the build" is not true with the named packages (site.md:16, check 4)

`rehype-katex` 7.0.1 removes `throwOnError` from its options (`lib/index.js` line 8:
`Omit<KatexOptions, 'displayMode' | 'throwOnError'>`), always catches KaTeX's exception, records a
`file.message('Could not render math with KaTeX', …)` (a warning, lines 92-102) and renders a red error span
(lines 108-120). Astro does not fail a build on such messages. `framework.md`'s
`[rehypeKatex, { throwOnError: true, strict: 'error' }]` (338) is therefore silently ignored, and bad TeX ships.

**Change:** add a `math` row to the plugin table: "a rehype step after `rehype-katex` fails the build when the file
has a message with `source: 'rehype-katex'` or the tree contains `.katex-error`"; and to check 4: "the built HTML
contains no `katex-error` and no Mermaid error SVG". Same pattern for Mermaid parse errors (finding 11).

### 5. Major — the excerpt fence's `mark="L2251"` collides with Expressive Code's own `mark` (pipelines.md:22, 33)

In Expressive Code a quoted value of `mark` is text to search for: `mark="L2251"` highlights every occurrence of the
string `L2251` (none), silently. Line markers (`{12}`, `mark={12}`) count the block's own lines; the line-numbers
plugin's `startLineNumber` "is purely visual" and "Text Markers are not aware of the shifted line numbers"
(expressive-code.com, Line Numbers plugin). So every engine-line mark in the book would render nothing and no check
would notice. A second problem: the GitHub link "at the pin" (pipelines.md:32) must use the full 40-character SHA;
`822a7a46` is a short id that stops resolving once another object shares the prefix.

**Change (pipelines.md "Code excerpts"):** "File line numbers are written in a book-only key, `lines="L2239-L2262"
marks="L2251,L2255"`. `excerpts.py fill` writes the Expressive Code props itself: `startLineNumber=2239` and the
block-relative `{13,17}`. `excerpts.py check` fails on any `mark`, `ins` or `del` value that is a quoted string
starting with `L`, and on a block whose `{…}` markers do not equal `marks` minus the start line. `engine.pin` holds the
full SHA." Write the header with path and GitHub link as an Expressive Code plugin (it sees `metaOptions`), not as a
remark plugin, so it cannot drift from the code block it labels.

### 6. Major — the crawl misses what breaks under a prefix at run time (site.md:35-38, check 2)

What a link crawler over static files cannot see, with the leak each hides:

| Misses | Why it matters here |
| --- | --- |
| Requests made by scripts: Pagefind's `pagefind-entry.json`, `pagefind.js`, `pagefind-worker.js`, `wasm.en.pagefind`, `.pf_meta`, `.pf_index`, `.pf_fragment` (all in the smoke `dist/pagefind/`), dynamic imports, `versions.json`, the track navigation's data | A wrong `bundlePath` or a fetch of `/versions.json` passes the crawl and breaks search or the menu |
| `srcset` and `<source srcset>` candidates other than the one a browser picks; CSS `url()` (fonts, KaTeX fonts) | Half the derived pictures and every font are never requested |
| `<head>` metadata: `canonical`, `og:url` (the smoke build emits `https://example.com/strata-engine-docs/`; its 404 page's canonical is `…/404/`, a URL that does not exist) | Canonical and sitemap point at the placeholder host |
| `Location` headers | `/strata-engine-docs/core/time` redirects to `http://<container>:8080/…` behind a proxy unless `absolute_redirect off` |
| Response headers: MIME, `Cache-Control`, `Content-Encoding`, CSP | A CSP without `'wasm-unsafe-eval'` and `worker-src` breaks Pagefind (pagefind.app hosting docs); an `immutable` rule on `pagefind.js` keeps a stale search after redeploy |
| Case | G: is exFAT (case-insensitive) and the staging server is Python on Windows: `/Core/Time/` answers 200 locally and 404 on Linux |
| The 404 behaviour | A "small static server" returns its own 404, not `404.html`; asking it for `/` and a missing page (site.md:37-38) proves nothing about nginx or Caddy |
| Orphans | Starlight's sidebar links every page from every page, so "never reached" can never fire for a page; what can be orphaned are files (unreferenced pictures) and track sequences |
| Links built only by script | Track "next/previous" chosen from `localStorage` (site.md:80-81) are invisible unless all tracks' links are in the HTML |

**Change (replace site.md:35-38):** three gates. (a) **Static**: lychee 0.24.2 over the staged folder (`--offline
--root-dir stage --include-fragments`, HTML, CSS and XML files), plus `tools/crawl.py` checks lychee cannot make:
every URL path is lowercase ASCII and matches a file byte for byte; every file in `dist/` is referenced or on an
allowlist (Pagefind, 404, sitemap); `canonical`/`og:url` equal `DOCS_SITE + DOCS_BASE + path` and exist (404 page
exempt); external links only to allowlisted hosts, engine links only at the full pin SHA. (b) **Runtime**: Playwright
against the real nginx and Caddy configurations in containers (CI only; see finding 10) loads one page per kind,
opens the 404 page at a three-level missing path, runs two searches and follows a result, toggles theme and track,
and records every request: all must stay under the prefix and answer 2xx, the 404 must answer status 404 with its
assets loaded. (c) **Headers**: the same run asserts MIME types (`image/avif`, `font/woff2`, `application/wasm` where
used), `Cache-Control` per path class, `Content-Encoding` on HTML, CSP present. Track navigation links for every track
are in the HTML (`data-track-next-g` …), the script only shows one.

### 7. Major — base-path leak channels that the plan does not configure or check (site.md:29-34)

The smoke build shows Starlight handles its own links, assets, favicon, sitemap link and Pagefind under the base
(`Search.astro` passes `baseUrl: import.meta.env.BASE_URL` and `bundlePath`). What it does not handle:

| Channel | Evidence | Rule to add |
| --- | --- | --- |
| `head` entries from config or front matter (preloads, icons, manifest, `og:image`) | `utils/head.js` prefixes only the favicon and `/sitemap-index.xml` (`fileWithBase`); user `head` entries pass through `createHead` unchanged | every `head` href is built in `astro.config.mjs` from `DOCS_BASE`; `og:image` absolute from `DOCS_SITE` |
| Our plugins' `href`, `src`, `srcset` (figures, diagrams, glossary, excerpt links) | Astro does not rewrite Markdown or `public/` URLs (Astro reference: "all of your static asset imports and URLs should add the base") | one helper `withBase()` used by every plugin; unit tests build with base `/` and `/a/b/` |
| `<script is:inline>` | Inline scripts are not processed by Vite, so `import.meta.env.BASE_URL` stays literal | pass the base through `data-` attributes or `define:vars`; lint fails on `import.meta.env` inside `is:inline` |
| `versions.json` | `framework.md` reads `../versions.json`, which resolves differently per page depth | absolute `DOCS_ROOT + versions.json` (see finding 9) |
| `robots.txt` | Crawlers read only `https://<host>/robots.txt`; a file at `/strata-engine-docs/robots.txt` is ignored | ship no `robots.txt`; `deploy/README.md` tells the owner the `Sitemap:` line to add to the host's root file |
| Web manifest (site.md:34) | Starlight emits none; nginx's `mime.types` has no `webmanifest` entry | drop it from site.md:34, or specify relative `start_url`/`scope`/icons and a `types` line |
| `site` placeholder | `DOCS_SITE` defaults to `https://example.com`; the smoke build's canonical, `og:url` and sitemap all say `https://example.com/strata-engine-docs/` | a release build fails when `DOCS_SITE` is the default or contains a path; the owner's real origin becomes an open question in README.md |
| Astro `redirects` | The Astro reference does not say whether redirect destinations get the base | never use Astro redirects for moved pages; a `redirects.json` generates nginx/Caddy rules and base-prefixed fallback pages, checked by gate (a) |
| Hard-coded prefix anywhere | — | the spike and CI build twice more, with `DOCS_BASE=/` and `DOCS_BASE=/x/y/`; both pass the crawl, and the `/x/y/` build contains no `strata-engine-docs` outside text |

### 8. Major — the deployment section names features instead of giving configurations, and misses the ones that fail (site.md:107-116)

What the plan forgets for a site that lives under a prefix of the owner's existing server:

1. **Location precedence.** In nginx, regex locations beat prefix locations. Owners' servers commonly carry
   `location ~* \.(css|js|png|svg|woff2)$ { … }` or `location ~ \.php$`; such a block captures
   `/strata-engine-docs/_astro/x.css` and serves it from the wrong root. Use `location ^~ /strata-engine-docs/`.
2. **Redirects.** `/strata-engine-docs` and `/strata-engine-docs/core/time` need 301s to the slashed form (Astro:
   "trailing slashes on prerendered pages are handled by the hosting platform"); with `absolute_redirect` on, nginx
   puts its own host and port in `Location`, which behind a proxy is the container's.
3. **404 under the prefix.** `error_page 404 /strata-engine-docs/404.html;` inside the location (keeps status 404);
   in Caddy, `handle_errors 404` with a `path` matcher (a bare `handle_errors` is site-wide and would take over the
   owner's other 404s).
4. **Cache by name, not by folder.** `_astro/*`, `pagefind/index/*`, `pagefind/fragment/*` and
   `pagefind.<hash>.pf_meta` are hashed; `pagefind.js`, `pagefind-worker.js`, `wasm.en.pagefind`,
   `pagefind-entry.json`, HTML, `404.html`, sitemaps and `versions.json` are not and must revalidate; pictures only
   if their names carry a hash (finding 3).
5. **Compression.** Precompress text files at build (`.gz`, and `.br` for Caddy) and serve them with `gzip_static` /
   `precompressed`; keep `application/octet-stream` out of `gzip_types` (Pagefind compresses its own files).
6. **Security headers.** The book shares the owner's origin, so its scripts could read the owner's other apps'
   `localStorage` and non-`HttpOnly` cookies; and the generated reference embeds engine-sourced text (command
   descriptions, schemas) that must be escaped. Headers: `X-Content-Type-Options`, `Referrer-Policy`,
   `X-Frame-Options`/`frame-ancestors`, and a CSP with `script-src 'self' 'wasm-unsafe-eval'` plus the hashes of
   Starlight's inline scripts (the smoke page has several: theme, sidebar persistence), `worker-src 'self' blob:`
   (Pagefind runs in a worker since 1.5). Generate the CSP snippet from the built HTML; Astro 6+'s `security.csp`
   (meta tag) is a spike item because its compatibility with Starlight is unverified.
7. **nginx `add_header` inheritance.** A nested location with its own `add_header` drops all outer ones; use one
   `map` for `Cache-Control` (no nested locations), or `add_header_inherit merge` (nginx ≥ 1.29.3).
8. **Version and `alias`.** nginx ≥ 1.30.6 (CVE-2026-15176 concerns `alias` after `rewrite`); use `root`, never
   `alias`, so URL and path are the same string.
9. **Deploy order.** Copy new files first without deleting, then delete old ones (two `rsync` passes), so a reader
   mid-session never gets HTML that points at removed hashed assets; and exclude `/v[0-9]*/` (finding 9).
10. **Container under the prefix.** Files at `<root>/strata-engine-docs/`, non-root image, `absolute_redirect off`,
    a health check; the host proxy uses `proxy_pass http://127.0.0.1:8080;` with **no URI part** (a trailing `/`
    strips the prefix) and Caddy `handle`, never `handle_path`.

**Change:** `deploy/` ships the blocks of [appendix C](#c-the-blocks-to-ship), and site.md:111-116 lists the ten
points above as requirements of those files, each asserted by the runtime gate of finding 6.

### 9. Major — the version scheme cannot be done by "keeping static files", and its parts must exist in the 0.8.0 tag (site.md:86-90)

- Every URL in a build embeds its base (smoke build: `/strata-engine-docs/_astro/…`). Copying the 0.8 build into
  `v0.8/` leaves every link and asset pointing at the root, which then holds 0.9 (hashed 0.8 assets are gone after
  the 0.9 deploy). The 0.8 book must be **rebuilt from its tag** with `DOCS_BASE=/strata-engine-docs/v0.8/`.
- That rebuild needs an "archived" mode: banner, `<meta name="robots" content="noindex">`, canonical to the current
  page where it exists, no sitemap, and the version menu reading `versions.json` from the **root** base. A build whose
  base is `/strata-engine-docs/v0.8/` cannot derive the root, so a second variable `DOCS_ROOT` is needed. All of this
  must be in the code at tag `v0.8.0`, otherwise the rebuild needs a patched tag. "Nothing of this is built before a
  second release exists" (site.md:90) is therefore wrong for these pieces.
- Deploying the current book into `…/strata-engine-docs/` with a deleting copy wipes `v0.8/`. The current build's
  crawl must treat `/strata-engine-docs/v*/` as outside its own build. No part slug may start with `v` + digit.
- `localStorage` is per origin, not per path: the track key and Starlight's `starlight-theme` are shared by all
  versions and by any other Starlight site of the owner. Namespace the book's own keys by `DOCS_ROOT`.

**Change (site.md "Versions"):** add `DOCS_ROOT` and `DOCS_ARCHIVED` now; state "old versions are rebuilt from their
tag with their own base"; the deploy instructions exclude `/v[0-9]*/` and `versions.json`; reserve `v[0-9]*` slugs
(the sidebar check enforces it); search stays per version (one Pagefind index per build is already the case).

### 10. Major — the container is told to build the site, and container tests cannot run on the authoring machine (site.md:114, 120-123)

A build inside `docker build` needs Node, Playwright's Chromium with `--with-deps` (for Mermaid), sharp encoding of
600 pictures, and an estimated 3-4 GB of RAM for 10-30 minutes cold (appendix B); the owner's server size is unknown.
The authoring machine has no administrator rights, no Docker and no WSL (environment notes), so "the nginx and
container deployments" of the spike can only be tested in GitHub Actions.

**Change:** `deploy/Dockerfile` serves an already built folder (CI artifact or local `npm run build`), and builds
nothing; a separate, optional `deploy/Dockerfile.build` for owners who want to build on the server, with its RAM need
stated. The spike's deployment tests and the runtime gate run in CI (`ubuntu-latest` has Docker). Ship the artifact
with a top folder `strata-engine-docs/` and attach release builds to a GitHub Release with a SHA-256 file (workflow
artifacts expire after 90 days by default).

### 11. Major — Mermaid: no renderer named, a browser in every build, fonts that differ between render and reader, no alt text (site.md:17, check 4)

- `site.md` does not name the renderer. The candidate in `framework.md` (`mermaid-isomorphic` 3.1.0) runs Chromium
  through Playwright, so every CI run and the container build download and start a browser, and it pins Mermaid 11
  (lock: 11.17.2) while 12.3.0 is current.
- Its default font is `arial,sans-serif` ("If you wish to use a custom font, you need to specify both
  `mermaidConfig.fontFamily` and `css`", README). Labels are measured with the font Chromium has (Linux CI: a
  metric substitute) and shown as `<img>` SVG, which cannot use the page's web fonts, so readers without Arial
  (Android, many Linux desktops) get other metrics and clipped labels; output also differs between Windows and Linux
  renders, which defeats a cache keyed by source.
- An `<img>` hides the SVG's `accTitle`/`accDescr`; site.md requires alt text on every picture (check 8) but a
  Mermaid fence has no place for it. axe cannot check contrast inside an `<img>`.
- 400 diagrams × 2 themes = 800 renders; an estimated 2-4 minutes cold plus 1-2 minutes of browser install per CI run.

**Change (site.md:17):** "Mermaid 11.17.2 through `mermaid-isomorphic` 3.1.0, `htmlLabels: false`, one font
(Inter, from the same `@fontsource` file) loaded through the `css` option and embedded in the SVG as a subset
`@font-face` data URI; rendered by `npm run diagrams` on one platform and **committed** as
`src/generated/diagrams/<hash>-{light,dark}.svg`, like the generated reference, so the site build needs no browser.
Each fence must contain `accTitle` and `accDescr`; the plugin copies them into `alt` and a visible caption.
Theme colors are checked once against 4.5:1. A check fails when a fence has no committed SVG for its hash."

### 12. Major — automatic glossary linking is the riskiest plugin, and a `title` tooltip is not accessible (site.md:71, pipelines.md:137-142)

"First use of a glossary term on a page links to its entry" means matching 1,592 terms (with plurals and other names)
over about 1.1 million words, skipping headings, code, link text, alt text, captions and the table of contents, with
overlapping terms ("shadow" inside "shadow map", "frame" inside "frame graph"). Every miss or false match is silent.
`framework.md` (273) instead used explicit `:term[…]` markup. A `title` attribute shows nothing to keyboard and touch
users (WCAG 1.4.13 requires hover content to be reachable and dismissible). A glossary page of 1,592 headings also
gives Starlight a table of contents of 1,592 entries, rendered twice (desktop and mobile).

**Change (site.md:71):** "`:term[text]{id=…}` marks a term explicitly; the style linter reports the first unmarked use
of a known term per page (it already flags terms before their definition). The link shows the definition in a
`popover` opened by the link's button, with the plain link as the no-script form. `reference/glossary` is one
`<dl>`: each `<dt>` has an `id` and `data-pagefind-title` (Pagefind 1.6 makes such elements explicit sub-results),
and the page sets `tableOfContents: false`."

### 13. Major — most of "our" plugins already exist as maintained packages; the list hides which ones are risky (site.md:61-72)

| Row | Existing piece | Use |
| --- | --- | --- |
| links | `starlight-links-validator` 0.27.0 (HiDeoo; peers `astro >=7.2.10`, `@astrojs/starlight >=0.42.0`) validates pages **and other pages' anchors** after the build; it appends its rehype plugin to the end of `unified().rehypePlugins` (`libs/processor.js`), so our link rewrite runs before it. `astro-rehype-relative-markdown-links` 0.19.2 rewrites `../x.md#a` with `base` and `trailingSlash` (its README says "tested with Astro >=2 <6"; peer `<8`) | rewrite: the package or 50 lines of ours; validation: the package with `errorOnRelativeLinks: true` as the net for links our rewrite missed. Cross-page anchor checking is not "small" to write: one page's plugin cannot see another page's headings |
| excerpts | Expressive Code plugin API, `@expressive-code/plugin-line-numbers` (`startLineNumber`), `plugin-collapsible-sections` | an Expressive Code plugin, not remark (finding 5) |
| asides, answers | Starlight's own `note/tip/caution/danger`; `starlight-markdown-blocks` 0.1.1 (Starlight's lead maintainer; renderer gets `h()`, so `details` works; unified only, registers through `updateConfig({ markdown: { remarkPlugins } })`) | use it; spike checks it under `markdown.processor: unified()` |
| strips' schema | `docsSchema({ extend })` (Zod) rejects bad front matter natively | no plugin; only the prerequisite-exists and no-cycle check is ours |
| zoom | `starlight-image-zoom` 0.16.2 | use |
| compare | `img-comparison-slider` 8.0.7 (MIT, 2026-01-29) | optional; ours is fine if it stays an `<input type="range">` |
| tabs, glossary, figures, top strip, track navigation | none for `.md` | ours: these are the real custom work and the risk |
| agents as readers (book.md:20, "Contributor or agent") | `starlight-llms-txt` 0.12.0 | consider; agents read Markdown better than HTML |

Two facts the custom rows must respect: Starlight restores unhandled **text and leaf** directives but not container
directives (`remarkDirectivesRestoration` in `integrations/remark-asides.js`), so `:::pitfal` silently becomes a
`<div>` unless our checker fails on it, and the checker must allow `note|tip|caution|danger` because Starlight's
asides plugin runs after user plugins. A remark plugin cannot import a component's script, so the scripts of
`book-tabs`, `book-compare` and the track navigation must be loaded by a component override (for example
`MarkdownContent`), once per page.

**Change:** rewrite the table at site.md:61-72 with a "package or ours" column as above, and mark figures, tabs,
glossary and track navigation as the items the spike must exercise first.

### 14. Major — the generated reference lands at the wrong URLs, and its "differs from the pin" check cannot run in CI (pipelines.md:120-135, outline-4.md:125-149)

- Starlight's `docsLoader` pattern is `**/[^_]*.{md,mdx,…}` (`dist/loaders.js` line 42): it skips files whose
  **name** starts with `_`, not folders. `src/content/docs/reference/_generated/commands.md` becomes a page at
  `/strata-engine-docs/reference/_generated/commands/`, in addition to `reference/commands`: a duplicate in search,
  a page outside the outline (check 1 "every page listed once" fails), and an "edit" link to a file that is
  overwritten on the next generation.
- "The check fails when they differ from what the pin generates" (pipelines.md:135) needs a built headless editor;
  the docs CI builds no engine.
- Weight: `reference/commands` holds 151 commands (automation inventory, line 20; editor-core 1.2.1 counts 153) with
  full JSON Schemas; the compact MCP definitions alone are about 99 KB (automation inventory, line 213). Rendered as
  Expressive Code blocks this is an estimated 1-3 MB of HTML on one page, and it will dominate search results.

**Change:** generate into `src/generated/reference/*.md` (outside the collection) and include it through a
`::include{file=…}` directive in the hand-written page, or generate the whole page including its front matter with
`editUrl: false`. Each generated file starts with a stamp (pin SHA, generator version, sha256 of the content); CI
checks the stamp's pin equals `engine.pin`; regeneration and the diff run locally when the pin moves. Render
parameters as tables and keep each schema in a collapsed block; split `reference/commands` into one page per command
group when the spike's page budget is exceeded (the XL no-split rule of outline-1.md:9 is for prose pages). The
generator HTML-escapes all engine text.

### 15. Major — search: the promised result display needs an override, and nothing measures result quality (site.md:83)

- Starlight's search uses Pagefind's Default UI with `showImages: false` and exposes only `ranking`, `indexWeight`
  and `mergeIndex` (`schemas/pagefind.js`, `components/Search.astro` lines 130-147). "Results show the kind and part
  of each page" needs a `Search` override, or putting them into the result title with
  `data-pagefind-meta="title:…"`.
- Starlight indexes Pagefind through the Node API with no configuration (`integrations/pagefind.js`), so CLI options
  such as `exclude_selectors` are unavailable; exclusions must be `data-pagefind-ignore` in the HTML.
- At this size the noise sources are known: about 1,500 quoted excerpts of up to 60 lines, generated reference tables,
  KaTeX's duplicated HTML+MathML text, the top strip repeated on every page. Starlight's search does not run in
  `astro dev` (`if (import.meta.env.DEV) return;`), so writers never see search results.

**Change (site.md:83):** "Each page sets `data-pagefind-meta` title `<title> · <part> · <kind>` and
`data-pagefind-filter` for part, kind and track; code blocks carry `data-pagefind-weight="0.5"`, generated reference
`0.3`, headings stay at the default; line-number gutters, the top strip and `.katex-html` carry
`data-pagefind-ignore`. A search test (Playwright on the built site) runs 60 fixed queries (30 glossary terms, 20 API
names such as `SceneRenderer`, `ST_CORE_ASSERT`, `viewport.capture`, 10 questions) and requires the term's home page
(book.md 'One home per concept') in the first three results for 90 % of them, 100 % for API names." Note the risk that
Starlight moves to Pagefind's Component UI, which would change any override.

### 16. Major — the spike's "realistic length" is half the book, and fake pictures would mismeasure (site.md:120-123)

The outline's sizes give 9 S, 127 M, 111 L and 17 XL pages plus 18 reference pages: 9×1,500 + 127×3,000 +
111×5,000 + 17×8,000 ≈ **1.09 million words** before the generated reference. `framework.md`'s spike assumed
300 × 1,800 = 540,000. Noise or flat-color pictures encode many times faster and smaller than renders. The engine
already has real renders at the pin: twelve `Samples/*/Screenshots/*.png`, 960×540, 0.65-1.2 MB each.

**Change (site.md:120):** "Fake content follows the outline exactly: 282 pages at their listed sizes (≈ 1.1 M words),
the reference pages generated from the inventories at their real sizes (151 commands with schemas, 165 host
functions, the 1,592-term glossary), one print view per part. Pictures: the twelve sample screenshots read from the
pin (`git show 822a7a46:<path>`), upscaled once to 1920×1080 and varied by crop and noise, in the published formats
of pipelines.md, plus crops and UI shots. Measured on the authoring machine and on GitHub `ubuntu-latest`." Sizes on
the authoring machine are reported as apparent sizes (finding 22).

### 17. Major — CI is one sentence; the parts that cost time or break are unspecified (site.md:104-105, pipelines.md:11)

- **Engine at the pin.** The tree at `822a7a46` is 134.7 MB, of which `Samples/` is 107.3 MB; the excerpt tool needs
  only `Strata*`, `StrataTests`, `Tools`, `CMake`, `Docs` (≈ 27 MB). Use `git fetch --depth 1 --filter=blob:none
  origin <full-sha>` with a sparse checkout of those folders, cached by pin SHA; `pin.py move` fetches both commits.
  A partial clone fetches each missing blob on first `git show`, so the tool should read through one
  `git cat-file --batch`.
- **Caches.** GitHub evicts caches unused for 7 days and caps a repository at 10 GB by default, so a pause between
  waves means a cold image and diagram build; budget it (appendix E). Cache `node_modules/.astro` (content-layer
  and image cache) keyed by lockfile and config, derived pictures keyed by the published files' hashes, Playwright
  browsers by Playwright version.
- **Checkout weight.** With about 300 MB of published pictures in the repository, five jobs that each check out the
  repository fetch it five times; use one build job, or `sparse-checkout` for lint and excerpt jobs.
- **Runners and cost.** The docs repository is public, so standard runners (4 vCPU, 16 GB, 14 GB SSD) cost nothing.
  "One commit per page, pushed to main" (process.md:52-53) means 300+ runs: set
  `concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }`.
- **Other needs.** Starlight's `lastUpdated`, if enabled, needs `fetch-depth: 0`; sketches compile with the runner's
  g++ only if they include nothing from the engine's vendor folder (state this in pipelines.md:34).

**Change:** a `site.md` section "CI" listing jobs, caches with keys, the engine fetch command, the container gates
(finding 6), the release upload, and the concurrency rule.

### 18. Minor — the per-part print view collides ids and leaks into search and the sitemap (site.md:84)

Every page has the same bottom headings (style.md:50-54: Summary, Check yourself, Exercises, Where it lives, Further
reading), so a part on one page has dozens of duplicate `id`s (broken in-page links, an axe failure). Starlight adds
`@astrojs/sitemap` without a filter unless one is configured (`index.js` line 55; the sitemap skips only 404 and 500),
so print pages enter the sitemap. Pages that use `StarlightPage` get `data-pagefind-body` and would double every
search hit. Lazy images may not load before printing.

**Change:** "Print views prefix every id with the chapter id, rewrite links inside the part to anchors and others to
absolute URLs, set `pagefind: false`, are excluded by a configured sitemap `filter`, open all `details`, and load
images eagerly; `noindex`. The spike measures the largest part (`make`, 33 pages) for time and memory."

### 19. Minor — offline reading does not work from the files as described (site.md:3-4, 104-105)

Root-absolute URLs (`/strata-engine-docs/_astro/…`) do not resolve from `file://`, and Pagefind's `fetch` of its
wasm and index fails there. **Change:** `deploy/README.md` "Reading offline": unpack the artifact (top folder
`strata-engine-docs/`), run `python -m http.server 8000` in the folder that contains it, open
`http://localhost:8000/strata-engine-docs/`; search works, nothing reaches the network.

### 20. Minor — the accessibility check samples pages and cannot see the custom components' failure modes (site.md:101)

axe on all pages in both themes is cheap (282 × 2 × ~1.5 s ≈ 15 min on one worker, ~4 min on four; estimate).
**Change:** "axe on every page, light and dark, zero serious or critical; Playwright keyboard tests for tabs (arrow
keys, ARIA tabs pattern), the slider (arrow keys, label), answers (`details`), the glossary popover (Escape closes)
and track navigation; Lighthouse accessibility 100 on one page per kind; badges `G`/`E` have accessible names;
diagram contrast checked at render time (finding 11)."

### 21. Minor — repository growth from retaken pictures is unbounded (README.md:38-40, pipelines.md:89)

At ≈ 0.5 MB per published picture, 600 pictures are ≈ 300 MB in the first take (estimate). Whole-editor pictures are
"retaken per release and compared by eye, not by hash", so each release adds them again even when nothing visible
changed. GitHub recommends repositories "ideally less than 1 GB". Git LFS on the free plan allows 10 GiB of storage and
10 GiB of bandwidth a month, and every CI clone that pulls LFS counts. **Change:** "A retaken picture is committed only
when a perceptual difference against the committed one exceeds a threshold; check 9 includes the repository's pack
size (≤ 1 GB before the 0.9 book); CI never fetches LFS objects if LFS is ever adopted."

### 22. Minor — the authoring drive changes the numbers and the rules for parallel agents (site.md:19, process.md:95-100)

G: is exFAT with 256 KB clusters, case-insensitive, without symlinks (environment notes). The smoke install's
`node_modules` is 321 MB apparent but 6.2 GB on disk (24,353 files measured). **Change:** budgets of check 9 use
apparent sizes; only the integrator builds (writers and reviewers never `npm ci` in their own worktrees, which would
cost 6 GB each); the `latest` symlink idea of framework.md:475 is server-only; case checks run on Linux in CI.

### 23. Minor — what is lost without MDX is not listed, so tutorials and internals pages lose their usual shapes (site.md:13, style.md:64-66)

In `.md`, Starlight's `<Steps>`, `<FileTree>`, `<Badge>`, `<CardGrid>`/`<LinkCard>`, `<Tabs>` and `<Code>` are not
available. Tutorials are numbered steps (style.md:64-66) and internals pages start with "a map of files"
(style.md:60-62). **Change:** site.md lists the replacements: `:::steps` (Starlight's `sl-steps` markup and CSS),
`:::files` (a tree rendered from an indented list), badges from front matter only, the start page's three doors as a
plain list; and lists the component overrides the book depends on (`PageTitle`, `Pagination`, `Footer`,
`MarkdownContent`), each re-checked at every Starlight upgrade because 0.x minors change their markup
(framework.md:25).

### 24. Minor — `compressHTML` and other Astro 7 defaults are unstated (site.md:12)

Astro 7 defaults `compressHTML` to `'jsx'` ("JSX whitespace rules", Astro reference); framework.md:334 sets `true`
because the default can drop spaces between inline elements, site.md is silent. **Change:** site.md:12 lists the
Astro settings the book depends on (`base`, `site`, `trailingSlash: 'always'`, `build.format: 'directory'`,
`compressHTML`, `markdown.processor: unified()`) and the spike checks a sentence that wraps between two inline code
spans keeps its space.

## A. Every way the site can leave the base, and its check

| Channel | Handled by | Configure | Check |
| --- | --- | --- | --- |
| Pages, sidebar, pagination, ToC | Starlight | `base` | gate (a) |
| `_astro/` CSS, JS, fonts (`@fontsource`, KaTeX CSS through Vite) | Astro/Vite | import fonts and CSS from npm only, never from `public/` with absolute URLs | gate (a) CSS `url()`; gate (b) network |
| Pagefind UI, index, worker, wasm | Starlight `Search.astro` (`baseUrl`, `bundlePath` from `BASE_URL`) | any `Search` override keeps both | gate (b): two searches, follow a result |
| Favicon | Starlight (`fileWithBase`) | `favicon` relative to `public/` | gate (a) |
| Other `head` entries | nobody | build hrefs from `DOCS_BASE` in config | gate (a) parses `<link>`, `<meta content>` |
| Canonical, `og:url`, sitemap | `site` + path | `DOCS_SITE` origin only; release guard | gate (a) compares with `DOCS_SITE + DOCS_BASE` |
| 404 page | Starlight writes `404.html` with base-absolute assets | server `error_page` / `handle_errors 404` inside the prefix | gate (b) deep missing path → status 404 + assets |
| Figures, diagrams, glossary, excerpt links from our plugins | our `withBase()` | unit tests with `/` and `/x/y/` | multi-base build |
| `srcset`, `<source>` | our figure plugin | same helper | lychee parses `srcset` (spike confirms) + unused-file check |
| Inline scripts | nobody | `data-` attributes, no `import.meta.env` in `is:inline` | lint + gate (b) |
| `versions.json`, version menu | ours | `DOCS_ROOT` | gate (b) in an archived build |
| Redirects | server | `redirects.json` → server rules | gate (b) `Location` headers |
| Trailing slash | server | `try_files $uri $uri/ =404` + `absolute_redirect off`; Caddy `file_server` (no `try_files`) | gate (b) slashless requests → 301 relative |
| Case | file names | lowercase slugs; lint | gate (a) on Linux |
| `robots.txt`, web manifest | owner / none | documented in `deploy/README.md` | — |

## B. Build scale (estimates, to be replaced by the spike's measurements)

| Item | Count | Cost estimate |
| --- | --- | --- |
| Markdown source | ≈ 1.1 M words prose + ≈ 1,500 excerpts × ~30 lines + generated reference | 12-15 MB |
| Expressive Code blocks | ~3,000 (excerpts + others); Shiki's C++ grammar is slow | 1-2 min |
| KaTeX | ~3,000 formulas | seconds |
| Page rendering with a 282-entry sidebar | 282 pages | sidebar ≈ 50-60 KB raw, 8-10 KB gzip per page |
| Pagefind | ≈ 15-25 MB of HTML | 15-40 s; index on disk 10-20 MB |
| Derived pictures (plan as written) | 600 × 6 files | ≈ 60 core-minutes → 15-20 min on 4 vCPU; ≈ 1.2-1.5 GB output |
| Derived pictures (finding 3) | ≈ 600 × 1 file | ≈ 3-5 min on 4 vCPU; ≈ 0.2-0.3 GB output |
| Mermaid | 800 renders | 2-4 min + browser install; 0 if committed |
| Warm build total | | 2-4 min (13700K), 4-8 min (4-vCPU runner) |
| Cold build total | | 20-35 min on the runner as planned; ≈ 10 min with findings 3 and 11 |
| Peak memory | | 2-3 GB Node + Pagefind's process |
| `node_modules` | 615 packages, 24,353 files | 321 MB apparent (6.2 GB on the exFAT drive) |

## C. The blocks to ship

`deploy/nginx/strata-engine-docs.http.conf` (http context, for example a `conf.d` file):

```nginx
# Cache policy by name. Only names that carry a content hash may be cached for a year.
map $uri $strata_docs_cache {
	default                                                 "no-cache";
	~^/strata-engine-docs/_astro/                           "public, max-age=31536000, immutable";
	~^/strata-engine-docs/figures/.+\.[0-9a-f]{8}\.         "public, max-age=31536000, immutable";
	~^/strata-engine-docs/pagefind/(index|fragment)/        "public, max-age=31536000, immutable";
	~^/strata-engine-docs/pagefind/pagefind\..+\.pf_meta$   "public, max-age=31536000, immutable";
}
```

`deploy/nginx/strata-engine-docs.location.conf` (server context):

```nginx
location = /strata-engine-docs { return 301 /strata-engine-docs/; }

# ^~ stops the owner's regex locations (for example "location ~* \.(css|js)$") from taking these files.
location ^~ /strata-engine-docs/ {
	root /srv/www;                       # files in /srv/www/strata-engine-docs/; root, never alias
	index index.html;
	try_files $uri $uri/ =404;
	error_page 404 /strata-engine-docs/404.html;
	absolute_redirect off;               # Location: /strata-engine-docs/x/, never an internal host or port
	autoindex off;
	charset utf-8;

	gzip_static on;                      # the build writes .gz beside every text file
	gzip on;
	gzip_vary on;
	gzip_types text/css application/javascript application/json image/svg+xml application/xml text/xml;
	# Pagefind compresses its own files; application/octet-stream stays out of gzip_types.

	# No nested locations: a nested add_header would drop all of these.
	add_header Cache-Control $strata_docs_cache always;
	add_header X-Content-Type-Options "nosniff" always;
	add_header Referrer-Policy "strict-origin-when-cross-origin" always;
	add_header X-Frame-Options "SAMEORIGIN" always;
	include /etc/nginx/snippets/strata-engine-docs.csp.conf;   # written by the build, see below
}
```

`strata-engine-docs.csp.conf`, generated from the built HTML (hashes of every inline script):

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'wasm-unsafe-eval' 'sha256-…'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'" always;
```

Caddy (inside the owner's site block):

```caddy
redir /strata-engine-docs /strata-engine-docs/ 308

handle /strata-engine-docs/* {
	root * /srv/www
	@immutable path /strata-engine-docs/_astro/* /strata-engine-docs/pagefind/index/* /strata-engine-docs/pagefind/fragment/* /strata-engine-docs/pagefind/*.pf_meta
	header @immutable Cache-Control "public, max-age=31536000, immutable"
	header ?Cache-Control "no-cache"
	header {
		X-Content-Type-Options nosniff
		Referrer-Policy strict-origin-when-cross-origin
		X-Frame-Options SAMEORIGIN
	}
	import strata-engine-docs-csp        # snippet written by the build: header Content-Security-Policy "…"
	file_server {
		precompressed br gzip            # no try_files: file_server redirects /x to /x/ itself
	}
}

handle_errors 404 {
	@docs path /strata-engine-docs/*
	handle @docs {
		root * /srv/www
		rewrite * /strata-engine-docs/404.html
		file_server                      # keeps status 404
	}
}
```

Container, `deploy/Dockerfile` (serves a built site; builds nothing):

```dockerfile
FROM nginxinc/nginx-unprivileged:1.30.6-alpine
COPY deploy/nginx/strata-engine-docs.http.conf /etc/nginx/conf.d/00-strata-engine-docs.conf
COPY deploy/nginx/container.conf /etc/nginx/conf.d/default.conf
COPY deploy/nginx/strata-engine-docs.location.conf deploy/nginx/strata-engine-docs.csp.conf /etc/nginx/snippets/
COPY --chown=101:101 site/strata-engine-docs/ /srv/www/strata-engine-docs/
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://127.0.0.1:8080/strata-engine-docs/ || exit 1
```

`deploy/nginx/container.conf`:

```nginx
server {
	listen 8080;
	server_name _;
	server_tokens off;
	include /etc/nginx/snippets/strata-engine-docs.location.conf;
	location / { return 404; }
}
```

Run: `docker run -d --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 127.0.0.1:8080:8080 strata-engine-docs:0.8.0`.
The host's proxy:

```nginx
location = /strata-engine-docs { return 301 /strata-engine-docs/; }
location ^~ /strata-engine-docs/ {
	proxy_pass http://127.0.0.1:8080;    # no URI part: the prefix reaches the container unchanged
	proxy_set_header Host $host;
	proxy_set_header X-Forwarded-Proto $scheme;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Caddy as the proxy: `handle /strata-engine-docs/* { reverse_proxy 127.0.0.1:8080 }` (`handle`, not `handle_path`).

Copying files (no container):

```sh
tar -xzf strata-engine-docs-site.tar.gz -C /tmp/new           # contains strata-engine-docs/
rsync -a /tmp/new/strata-engine-docs/ /srv/www/strata-engine-docs/                                  # 1: add new files
rsync -a --delete --exclude '/v[0-9]*/' --exclude '/versions.json' \
	/tmp/new/strata-engine-docs/ /srv/www/strata-engine-docs/                                           # 2: remove old ones
```

Owner's root `robots.txt`: `Sitemap: https://<host>/strata-engine-docs/sitemap-index.xml`.

## D. CI outline

1. `lint` (sparse checkout without pictures): markdownlint, typos, style linter, front matter schema, no MDX.
2. `excerpts`: engine fetched at the full pin SHA (`--depth 1 --filter=blob:none`, sparse to source folders, cached
   by SHA); `excerpts.py check`; generated-file stamps equal `engine.pin`; sketches compile.
3. `build` (Node 26.13.0; caches: npm, `node_modules/.astro`, derived pictures): `astro build` three times
   (`DOCS_BASE` = `/strata-engine-docs/`, `/`, `/x/y/`), budgets, stage, precompress, CSP snippet, tarball + SHA-256.
4. `serve-test` (needs build; Docker): nginx container and Caddy container from `deploy/`, gates (a), (b), (c),
   search test, axe on all pages in both themes, Lighthouse on one page per kind.
5. `release` (tags `book-v*`): upload the tarball to a GitHub Release.
6. Weekly: external links with lychee online, reporting only; engine links verified by `git cat-file -e`, not HTTP.

`concurrency` cancels superseded runs of the same branch.

## E. Spike: what to measure, and the budgets

| Measure | Machine | Pass | If it fails |
| --- | --- | --- | --- |
| Warm full build (all caches) | i7-13700K | ≤ 4 min | tune; > 8 min → try the fallback |
| Warm full build | GitHub `ubuntu-latest` | ≤ 8 min | tune |
| Cold build incl. pictures and diagrams | GitHub `ubuntu-latest` | ≤ 30 min | fewer derived files |
| Rebuild after editing one page | i7-13700K | ≤ 90 s | content-layer cache settings |
| `astro dev` start; refresh after an edit | i7-13700K | ≤ 60 s; ≤ 3 s | — |
| Peak memory of the build process tree | both | ≤ 4 GB | ≤ 6 GB with `--max-old-space-size` recorded; more → fallback |
| Two builds of one commit | Linux | identical `dist/` except time stamps | find the source of difference |
| `dist/` apparent size, one version | — | ≤ 400 MB; HTML+CSS+JS ≤ 80 MB; ≤ 15,000 files | finding 3 |
| Largest page (brotli) | — | ≤ 300 KB; median ≤ 60 KB; sidebar share recorded | split generated reference |
| JavaScript per page without search (brotli) | — | ≤ 40 KB | — |
| Search transfer, first two-word query | — | ≤ 300 KB; next query ≤ 100 KB | weights, ignores |
| Search quality, 60 fixed queries | — | home page in top 3 for ≥ 90 %, API names 100 % | weights, meta |
| Lighthouse mobile, heaviest figure page | — | performance ≥ 90, accessibility 100, CLS ≤ 0.05, LCP ≤ 2.5 s | — |
| axe, all pages, both themes | — | 0 serious or critical | — |
| Crawl and network gates | CI containers | 0 non-2xx under the prefix, 0 requests outside it, 0 unreferenced files | — |
| Base portability | CI | `/`, `/strata-engine-docs/`, `/x/y/` all pass | — |
| Mermaid | — | 0 clipped labels (text box inside node box, Playwright), every diagram has alt text | font settings |
| Print view of `make` | i7-13700K | ≤ 5 min, ≤ 4 GB, 0 duplicate ids | per-chapter PDF |
| Confirm items | — | each of framework.md §7's "things to confirm", plus `security.csp` with Starlight, `starlight-markdown-blocks` under `unified()`, lychee `srcset` parsing, `compressHTML` spaces | a fork of any → fallback trial |

## Not checked

- Actual build times, memory and sizes: nothing was built; every number marked "estimate" is reasoning from counts,
  to be replaced by the spike.
- Whether `astro-rehype-relative-markdown-links` 0.19.2 works on Astro 7 (its README says tested below 6).
- Whether Astro 6+'s `security.csp` hashes Starlight's inline scripts; whether lychee 0.24.2 extracts `<source
  srcset>` candidates.
- Whether Astro 7's `compressHTML: 'jsx'` touches Markdown-rendered content.
- Whether Astro's `redirects` add the base in static output.
- Search ranking behavior of Pagefind 1.6 on C++ identifiers containing `::`.
- The owner's server (nginx or Caddy, version, other locations, RAM): unknown; the blocks assume nginx ≥ 1.30.6 or
  Caddy 2.11.
