# The site

The book is a static site. The build writes plain files that any web server can serve. There is no server code, no
database, and no request to another host at read time: fonts, math, search, diagrams and pictures are all files of the
site.

This file decides the web project: the framework, the base path, the Markdown the build reads, the plugins, the checks,
the budgets, the deployment, versions and CI. `research/framework.md` is background only; where it differs from this
file, this file wins ([Where this file overrides the research](#where-this-file-overrides-the-research)).
`pipelines.md` decides what the engine supplies (quotes, pictures, tutorials, reference dumps); `style.md` decides how
a writer fills the fields and directives this file makes the build enforce.

**(spike)** marks a name or version that this file takes from the working spike in this clone (2026-11-10) where the
earlier plan or the critique named it differently. The spike decides its own names and versions unless a ruling says
otherwise. [The spike against this file](#the-spike-against-this-file) lists what the spike must still change.

## Framework and versions

Astro Starlight. Every npm version is pinned exactly in `package.json` and `package-lock.json`. Tools outside npm are
pinned with the SHA-256 of their archives in `tools/toolchain.json` and downloaded into `.tools/` by
`python tools/bootstrap.py` (spike), which also writes `.tools/env.sh` and `.tools/env.ps1` to put them on the PATH.

| Piece | Version | Pinned in |
| --- | --- | --- |
| Node.js | 26.13.0 LTS, official archives `node-v26.13.0-win-x64.zip`, `node-v26.13.0-linux-x64.tar.xz`, also checked against nodejs.org's `SHASUMS256.txt` | `tools/toolchain.json`, `package.json` `engines` (spike) |
| `astro` | 7.4.8 | `package.json` |
| `@astrojs/starlight` | 0.42.10 | `package.json` |
| `@astrojs/markdown-remark` | 7.3.6, a peer of Starlight; gives `unified()` | `package.json` |
| `@astrojs/sitemap` | 3.7.4, a direct dependency: the book adds its own instance with a filter, and Starlight then adds none (`@astrojs/starlight/dist/index.js` adds its sitemap only when no `@astrojs/sitemap` integration is present) | `package.json` |
| Expressive Code | 0.44.3: `astro-expressive-code` through Starlight; `@expressive-code/plugin-line-numbers` and `@expressive-code/plugin-collapsible-sections` direct | `package.json` |
| `pagefind` | 1.6.0 (`@pagefind/default-ui` 1.6.0 through Starlight) | `package.json` |
| `katex` | 0.16.47, an `overrides` entry (`rehype-katex` 7.0.1 wants `^0.16.0`) | `package.json` |
| `rehype-katex`, `remark-math` | 7.0.1, 6.0.0 | `package.json` |
| `remark-directive`, `remark-gfm`, `remark-smartypants`, `unified` | 4.0.0, 4.0.1, 3.0.3, 11.0.5 (spike) | `package.json` |
| `mermaid-isomorphic` | 3.1.0, with `mermaid` 11.17.2 as an `overrides` entry | `package.json` |
| `playwright` | 1.65.0 (spike): Chromium for `npm run diagrams` and the browser checks | `package.json` |
| `@axe-core/playwright` | 4.14.0 (spike) | `package.json` |
| `sharp` | 0.35.5 | `package.json` |
| Fonts | `@fontsource-variable/source-serif-4` 5.3.1, `@fontsource-variable/inter` 5.3.0, `@fontsource-variable/jetbrains-mono` 5.3.0 (spike) | `package.json` |
| `markdownlint-cli2` | 0.24.0 | `package.json` |
| Lighthouse | the npm release current when the spike adds it, pinned exactly (spike) | `package.json` |
| typos | 1.52.1 (spike) | `tools/toolchain.json` |
| lychee | 0.24.2 (Windows and Linux archives with SHA-256; to add) | `tools/toolchain.json` |
| nginx | the one server, tested in two versions (`critique/rulings-6.md`, R23). 1.30.6: the container image `nginxinc/nginx-unprivileged:1.30.6-alpine`; the Windows test build `nginx-1.30.6.zip` (spike). 1.20.1, what `https://pdm.pw` runs: the official image `nginx:1.20.1`; the Windows test build `nginx-1.20.1.zip` | `deploy/Dockerfile`, `.github/workflows/book.yml`, `tools/toolchain.json` |
| Python | 3, standard library only | — |
| Quarto | 1.11.9, the fallback only | — |

Known risks of these versions:

- Starlight is 0.x: a minor release may change the markup of the components the book overrides. Every Starlight
  upgrade re-checks the overrides ([The Markdown the build reads](#the-markdown-the-build-reads)).
- Pagefind 1.5 announced its Component UI as the replacement of the Default UI, which Starlight 0.42 uses. If
  Starlight moves to it, the search display and the search test are checked again.
- Mermaid 12.3.0 is current; the book draws with 11.17.2 (`mermaid-isomorphic` 3.1.0 wants `^11`). Diagram syntax
  follows Mermaid 11.
- KaTeX 0.19.1 is current; the book stays on 0.16.47 so that the CSS and the renderer of `rehype-katex` 7.0.1 match.

**Upgrades.** Before the book of 0.8 is released, a version changes only to fix a security problem or a bug that
blocks the book: one package per commit, with budget rows 1 to 8 measured again and gates (a) to (c) passing.

**Fallback.** If the spike fails ([Budgets and the spike](#budgets-and-the-spike)), Quarto 1.11.9 with Pagefind is
built the same way, at the same scale, and measured against the same table. Moving is not free: the book's directives
(`:::why`, `:term[…]`, `::figure{…}`) and fence attributes (`src="…"`) have no Pandoc spelling, so a move needs a
converter of the dialect and every plugin written again as a Lua filter. That is affordable only while no content
exists. **The spike's verdict is final: after the pilot starts, the framework is not revisited before 0.8.0.**

### Astro and Starlight settings the book depends on

`astro.config.mjs` (spike):

| Setting | Value | Why |
| --- | --- | --- |
| `site` | the origin of `site.json`, or `DOCS_SITE` | canonical links and the sitemap |
| `base` | the base of `site.json`, or `DOCS_BASE` | every URL under the prefix |
| `trailingSlash` | `'always'` | one URL per page; servers redirect the slashless form |
| `build.format` | `'directory'` | a page is `<id>/index.html` |
| `compressHTML` | `true` | Astro 7's default `'jsx'` may drop the space between two inline elements |
| `markdown.processor` | `unified({ remarkPlugins, rehypePlugins })` | the book's plugins are unified plugins |
| `cacheDir` | `'./.cache/astro'` (spike) | the build's caches stay in one ignored folder, `.cache/` |
| `redirects` | not set, ever | moved pages go through `src/redirects.json` |
| `vite.build.assetsInlineLimit` | a function that answers `false` for a font file (`.woff2`, `.woff`, `.ttf`) | no font becomes a `data:` URL, which the policy's `font-src 'self'` would block; every font is a file of `_astro/` (`critique/rulings-6.md`, R23) |

Starlight: `title: 'The Strata Engine Book'`; no `editLink` and no `social`, so that no page links into the book's
repository (`critique/rulings-6.md`, R20); `lastUpdated: false` (so CI needs no full history);
`pagination: true`; `tableOfContents` from level 2 to 3; `favicon: '/favicon.svg'`; `defaultLocale: 'root'` with
English; `customCss` the three fonts, `katex/dist/katex.min.css`, `src/styles/book.css`, `src/styles/print.css`
(spike); component overrides `PageTitle` and `Pagination` (spike), and `Footer` (the copyright line,
[Navigation](#navigation)).

## Where the site is served: the settings

The deployment's values are written in one file, `site.json` at the repository's root (`critique/rulings-6.md`,
R24). The owner serves the book at `https://pdm.pw/strata-engine-docs/` "for now", so the address stays one setting:

```json
{
  "base": "/strata-engine-docs",
  "origin": "https://pdm.pw",
  "copyright": { "holder": "2042Third", "year": 2026 }
}
```

The build reads `site.json` and the environment in one module, `src/lib/settings.mjs` (spike); the tools read them in
one module, `tools/booklib/settings.py`. Both apply the rules of the table below, and one table of cases
(`tools/tests/fixtures/settings-cases.json`) tests both. No other module of the build or the tools reads these values
or variables. No other file holds the origin: `tools/lint.py` (rule `literal-origin`) fails on the literal origin
outside `site.json`, `deploy/README.md`, the repository's `README.md` and `plan/`.

| Setting | Value | What it is | Rules |
| --- | --- | --- | --- |
| `base`; `DOCS_BASE` overrides it for one build | `/strata-engine-docs` | the path prefix of every URL | starts with `/`; only letters, digits and `/ . _ ~ -`; no `.` or `..` segment; does not start with `//`; a trailing `/` is dropped; `/` means the root of the host (spike) |
| `origin`; `DOCS_SITE` overrides it for one build | `https://pdm.pw` | the origin of canonical links, `og:url` and the sitemap | `http` or `https`; no path, query or fragment: the path belongs in the base (spike) |
| `copyright.holder`, `copyright.year` | `2042Third`, `2026` | the holder's name and the year of first publication in the copyright line ([Navigation](#navigation)) and in `LICENSE` | the holder is `2042Third` until the owner names another (R20) |
| `DOCS_RELEASE` | unset | `1` makes a release build (spike) | see below |
| `DOCS_ROOT`, `DOCS_ARCHIVED` | — | reserved for archived versions ([Versions](#versions)) | a build with either set fails with "not implemented before the second release" |

`DOCS_BASE` and `DOCS_SITE` are for one build only: the three bases of budget row 17, a test server, a preview. A
release build (`DOCS_RELEASE=1`) fails when the origin is not `https`, names `localhost`, `127.0.0.1` or
`example.com`, or carries a path; and on any draft page, placeholder or unshot picture, unfilled excerpt, or tutorial
without a current stamp. `https://example.com` is the origin that tests pass explicitly. A tagged build is a release
build for the committed address.

## The base path

**Every URL of the site is under the base**, `site.json`'s `/strata-engine-docs` (the owner serves the book at
`https://pdm.pw/strata-engine-docs/`). Building for another place changes only the settings, never a page.

1. **Content never writes the prefix.** A link between pages is a relative path to the other page's `.md` file
   (`../core/time.md#the-accumulator`). The links plugin (`src/plugins/links.mjs`, spike) turns it into the page's URL
   and fails the build when the file or the anchor does not exist. A link that starts with `/`, a link to `//host`, a
   query string and a plain Markdown image also fail the build (spike).
2. **One helper builds every URL.** Our code builds URLs of the site only through `src/lib/settings.mjs`:
   `pageUrl(base, id)` (spike) for pages, `withBase(base, path)` for files (figures, diagrams, the manifest, print
   views). Unit tests in `src/plugins/tests/` run every plugin at the bases `/`, `/strata-engine-docs` and `/a/b`.
3. **No `import.meta.env` inside `<script is:inline>`.** Vite does not process inline scripts, so the expression would
   stay literal. The base reaches scripts through `data-` attributes or `define:vars`; `tools/lint.py` fails on
   `import.meta.env` inside an inline script.
4. **`head` entries** of `astro.config.mjs` build their `href` from the settings (spike: the manifest link). Pages set
   no `head` in their front matter; `tools/lint.py` fails on it.
5. **No `robots.txt`.** Crawlers read only `<host>/robots.txt`. `deploy/README.md` gives the owner the `Sitemap:` line
   for the host's own file, made of the origin, the base and `/sitemap-index.xml`:
   `Sitemap: https://pdm.pw/strata-engine-docs/sitemap-index.xml`. Gate (a) fails when the build contains a
   `robots.txt`.
6. **The web manifest is fully specified** (spike: `src/pages/manifest.webmanifest.ts`): `start_url` and `scope` are
   `<base>/`, the icon is `<base>/favicon.svg`; servers send it as `application/manifest+json`.
7. **No Astro redirects.** Whether Astro adds the base to a redirect's target is not documented. A moved page gets an
   entry in `src/redirects.json` ([Moved pages](#moved-pages)).
8. **Ids are lowercase ASCII and some are reserved.** Page ids and part slugs are segments of `[a-z0-9-]`. Reserved
   first segments: `v` followed by a digit (archived versions), `print`, `pagefind`, `downloads` (the files of
   pipelines.md that readers download), `_astro`, `_figures`, `404`.
   Reserved files at the base: `versions.json`, `robots.txt`, `manifest.webmanifest`, `favicon.svg`, `sitemap-*.xml`,
   `license.txt`, `third-party-notices.txt` (`critique/rulings-6.md`, R22). `tools/pages.py check` and the build's
   sidebar check fail on them.

### Every way the site can leave the base, and its test

| Channel | Handled by | Test |
| --- | --- | --- |
| Pages, sidebar, pagination, table of contents | Starlight with `base` | gate (a) at three bases |
| CSS, scripts and fonts under `_astro/` (the fonts and KaTeX's CSS come from npm) | Vite; nothing in `public/` is referenced by an absolute URL; no font inlined | gate (a) follows CSS `url()` and fails on a font's `data:` URL; gate (b) records every request |
| Pagefind's script, worker, WebAssembly and index | Starlight's `Search.astro` (`baseUrl` and `bundlePath` from `BASE_URL`); the book has no `Search` override | gate (b): two searches, a result followed |
| Favicon | Starlight (`favicon` relative to `public/`) | gate (a) |
| Other `head` entries | rule 4 | gate (a) reads every `<link href>` and `<meta content>` |
| Canonical, `og:url`, sitemap | `site` = the origin; the release guard | gate (a): equal to the origin + the base + path, and the page exists (the 404 page is exempt) |
| The 404 page | Starlight writes `404.html` with base-absolute assets; the server's error page inside the prefix | gate (b): a three-level missing path answers 404 with its assets 2xx |
| Links and files written by our plugins and overrides (figures, diagrams, glossary, excerpt headers, breadcrumbs, track links, print views, the footer's two links) | rule 2 | unit tests at three bases; the multi-base build |
| `srcset` candidates | the figures plugin, through `withBase` | gate (a): `tools/crawl.py` reads every candidate (spike), lychee too (a spike confirm item); the unreferenced-file check |
| Inline scripts | rule 3 | lint; gate (b) |
| Track links | written into the HTML ([Navigation](#navigation)) | gate (a) follows the links inside `<template data-book-track>` |
| `versions.json` and a version menu | not built while one version exists ([Versions](#versions)) | — |
| Moved pages | `src/redirects.json` → server rules and fallback pages | gate (a) follows the fallback pages; gate (b) checks `Location` |
| Trailing slash | the server: nginx `try_files $uri $uri/ =404` with `absolute_redirect off` | gate (c): a slashless request answers a redirect whose `Location` is a path |
| Case | rule 8 | gate (a) on Linux: every URL path is lowercase ASCII and matches a file byte for byte |
| `robots.txt`, the manifest | rules 5 and 6 | gate (a): no `robots.txt`; gate (c): the manifest's type |
| The prefix written into code | rule 2 | the builds at `/` and `/x/y/` pass gate (a); the `/x/y/` build has no URL, CSS, script or JSON string that starts with `/strata-engine-docs`; gate (a) fails on any link to the book's repository (`github.com/2042Third/strata-engine-docs`), which no page has (`critique/rulings-6.md`, R20) |
| `localStorage` | one store per origin, shared by every path of the host | the book's keys start with `strata-book:` (spike); keys per version come with versions |

## Layout of the repository

```
strata-engine-docs/
  README.md                           what this is, how to build, how to deploy; closed source, all rights reserved, no contributions asked for
  LICENSE                             the copyright statement, the permission for the book's code, a pointer to the notices
  site.json                           the deployment's values: base, origin, copyright holder and year
  astro.config.mjs                    settings, Starlight, the book's Markdown pipeline (spike)
  ec.config.mjs                       Expressive Code: line numbers, collapsible sections, "slang" as HLSL (spike)
  package.json, package-lock.json     exact versions; "private": true and "license": "UNLICENSED"
  engine.pin                          engine commit (40 hex digits), release, prerelease, repository (spike)
  _typos.toml, .markdownlint-cli2.jsonc    spelling and Markdown lint settings (spike)
  src/content.config.ts               the front matter schema (spike)
  src/content/docs/<part>/<chapter>.md     the book; <part>/index.md and <part>/review.md for parts of 8+ pages
  src/content/figures/<part>/<chapter>.json    figure recipes (spike)
  src/content/glossary.json           the glossary (spike)
  src/content/i18n/en.json            the interface's words (spike)
  src/assets/figures/<part>/<chapter>/     published pictures (spike)
  src/generated/diagrams/             prerendered Mermaid diagrams, committed
  src/generated/reference/            generated reference tables, committed
  src/sidebar.json                    the parts, their pages in order, the tracks (spike)
  src/redirects.json                  moved pages
  src/plugins/, src/lib/, src/integrations/    the build's own code; tests in src/plugins/tests/ (spike)
  src/components/, src/pages/, src/styles/     overrides and the client script, print views and the manifest, CSS (spike)
  public/                             favicon.svg; third-party-notices.txt, written by tools/notices.py and committed; downloads/ (pipelines.md)
  sketches/                           the book's own programs (pipelines.md)
  labs/                               command scripts that build lab scenes for figures (pipelines.md)
  tutorials/                          tutorial scripts and their stamps (pipelines.md)
  tools/                              Python, standard library only: checks, crawl, figures, excerpts, release (spike)
  tools/booklib/settings.py           the tools' reader of site.json and the environment
  tools/notices.py, tools/data/notices.json    the third-party notices: the tool and the list of what the site ships
  scripts/                            Node: browser checks, the scale test, diagrams, picture encoding (spike)
  deploy/                             nginx configurations, Dockerfiles, the deploy script, README
  .github/workflows/                  book.yml, links.yml
  plan/                               this plan (not published)
  .tools/ .cache/ dist/ stage/ release/ originals/ node_modules/      ignored
```

There is no `diagrams/` folder: hand-drawn drawings are published pictures (`src/assets/figures/…/<id>.svg`, spike) and
Mermaid output is `src/generated/diagrams/`. `originals/` holds PNG originals on the machine that takes pictures
([Pictures](#pictures)). `.gitignore` lists these seven folders, beside the spike's `.astro/` and Python caches.

**The copyright statement and the notices.** The book is closed source: its text, pictures, diagrams, sketches,
tutorial files, labs, downloads and the site's own code and tools are all rights reserved, with one permission for the
book's code (`critique/rulings-6.md`, R20 and R21). `LICENSE` holds the full statement. Its first line,
"Copyright © 2026 2042Third. All rights reserved.", is built from `site.json`; "Except where otherwise noted" and the
two exceptions follow: R21's permission for the book's code, and a pointer to the notices for third-party material
(R22). `tools/pages.py check` fails when the first line is not the one built from `site.json`, and when `package.json`
lacks `"private": true` or `"license": "UNLICENSED"`. The build writes `LICENSE` to `<base>/license.txt`.
`public/third-party-notices.txt`, served at `<base>/third-party-notices.txt`, is written by `tools/notices.py write` in
three sections (R22): what the site ships (read from `tools/data/notices.json`, kept by hand, with the license texts
from `node_modules`), what the book quotes (the engine's `ThirdPartyNotices.md` and the libraries' license files at the
pin) and what the book shows and gives out (the samples' `CREDITS.md` at the pin, and the credits of `labs/` and
`tutorials/`). Each license's text appears once, and each component names its copyright holders exactly as its own
notice does (Source Serif 4 is Adobe's). `tools/notices.py check` fails when the committed file is stale, when a
component of the list has another version in `package-lock.json` than the list records, when a license is outside
R22's allowlist, and, after a build, when `dist/` holds a font family, a script package or a WebAssembly file that no
component of the list claims. Fonts are served as their packages ship them: the build never subsets, converts or
renames a font file.

## The Markdown the build reads

Plain `.md`: CommonMark, GFM tables, smart punctuation, math and directives. `src/lib/markdown.mjs` parses with the same
extensions as the build, so a heading gets the same anchor in the page index as on the page (spike). No `.mdx` file
exists under `src/content/` (`tools/lint.py`, rule `mdx`, spike).

### Directives

This table is the complete list: the build fails on a container or leaf directive not in it, and on a text directive
with a label or attributes (`:name[…]`, `:name{…}`) other than `:term` and `:since` (spike); a bare `a:b` in prose
stays text. Starlight's own `:::note`, `:::tip`, `:::caution` and
`:::danger` pass through to Starlight. `style.md` §12 says when a writer uses each; the directives below that it does
not list are used by the integrator only.

| Directive | Form | Renders | State |
| --- | --- | --- | --- |
| `:::why`, `:::question`, `:::history`, `:::elsewhere`, `:::rule` | container, optional `[title]` | Starlight's aside markup | spike |
| `:::simplified`, `:::analogy`, `:::example` | container | asides; `analogy` ends with its "Where it breaks" paragraph | to write (spike) |
| `:::derivation` | container | a closed `<details>` titled "Where this comes from", whose first line the plugin writes | to write (spike) |
| `::::test-out` | container holding five questions, each followed by `:::answer` | the primer's "Test out" box, with its title and instruction | to write (spike) |
| `:::answer` | container, optional `[label]`, `{tests="<learn ids>" solution="<file>"}` | a closed `<details>`; printing opens it | spike; `tests` and `solution` to add (spike) |
| `::::tabs` holding `:::tab[Label]` | container, optional `sync=<key>` | one panel at a time; every panel without scripts | spike |
| `:::steps` | container holding one ordered list | Starlight's steps markup (`sl-steps`) | to write |
| `:::files` | container holding one nested list | a file tree | to write |
| `::figure{id=…}`, optional `variant=…`, `crop` | leaf | a picture of the chapter's recipes | spike |
| `::compare{id=… before=… after=…}` | leaf | a before and after slider | spike |
| `::checkpoint{stage=…}` | leaf, only on tutorials | the download of the tutorial's project at that stage (pipelines.md makes it) | to write (spike) |
| `::glossary` | leaf, only on `reference/glossary` | the glossary as one `<dl>` | spike |
| `::track-chooser` | leaf, only on pages of `start` | the reader's choice of track | spike |
| `::include{file=…}` | leaf, only on pages of `reference` | a file of `src/generated/reference/` | to write |
| `:term[text]{id=…}` | text | a link to the glossary entry with a popover | to write (spike) |
| `:since[0.8.0]` | text, at the start of a section's first paragraph | the "New in 0.8.0" badge | to write (spike) |

A how-to of block A of `make` that changes Coin Run has no `::checkpoint`: its tutorial file ends in a stage with
`endState` (pipelines.md §6.2), and the build draws that stage's downloads, as a checkpoint draws them, at the end of
the page's `## Result` (`style.md` §7.5; `critique/rulings-7.md`, R32).

### Code fences

| Fence info string | Meaning | State |
| --- | --- | --- |
| `cpp src="<path>#L<a>-L<b>" mark="L<n>,L<m>-L<k>"` | a quote of the engine; the attributes, the `vendor:` and `book:` prefixes and the tool that fills the lines are pipelines.md's | spike |
| `cpp sketch="<file>"`, `text output-of="<file>"`, `cpp pseudocode` | the book's own code, labelled | spike |
| `mermaid caption="…" alt="…"` | a diagram | spike |
| any other language | a code block with Expressive Code's own props (`{3-5}`, `title=`, `collapse=`) | — |

The excerpts plugin (`src/plugins/excerpts.mjs`, spike) replaces a quote's `src` and `mark` with Expressive Code's
`showLineNumbers`, `startLineNumber=<a>` and block-relative marks, and wraps the fence with its header (the path, the
lines and the link that pipelines.md §3.2 gives for the quote's source) in one element, so header and code cannot
drift apart. A `mark` with `L` values on a fence without `src` fails the build (spike).

Every link into the engine's repository (a quote's header, the pin on the top strip) is built by one helper from
`engine.pin`'s `repository` line (`critique/rulings-6.md`, R25); where this plan spells
`https://github.com/2042Third/GameEngine`, it means that setting. The engine's repository stays public. The book's
own code has no link into the book's repository: the header of a `sketch` or `output-of` fence names its file, and the
header of a quote from `book:<path>` names the path and links its download under `<base>/downloads/` when there is
one (pipelines.md).

### What MDX would have given, and the replacements

| MDX component | In the book |
| --- | --- |
| `<Steps>` | `:::steps` |
| `<FileTree>` | `:::files` |
| `<Badge>` | badges come only from front matter, on the top strip |
| `<Tabs>` | `::::tabs` |
| `<Card>`, `<CardGrid>`, `<LinkCard>` | plain lists of links; the track chooser on Start here |
| `<Code>` | fences; quotes are filled by `tools/excerpts.py` |
| `<Aside>` | `:::note` and the book's asides |

The book depends on three component overrides: `PageTitle` and `Pagination` (spike), and `Footer`. `PageTitle` holds
the breadcrumbs, the top strip, the search metadata and the client script `src/components/client/book.js`;
`Pagination` the track links; `Footer` the copyright line and its two links ([Navigation](#navigation)). At every
Starlight upgrade each override is compared with the new version's default component (its props and the markup it
wraps) and gates (a) to (c) run again. A new override is added to this list before it is merged.

## Plugins: package or ours

| What | Package that exists | Ours | Used |
| --- | --- | --- | --- |
| Link rewriting and validation, anchors of other pages included | `starlight-links-validator` 0.27.0 (validation); `astro-rehype-relative-markdown-links` 0.19.2 (rewriting; its README says tested below Astro 6) | `src/plugins/links.mjs` with the page index `src/lib/pages.mjs`, read before any page renders (spike) | ours (spike); gate (a) is the independent net; the packages are the fallback |
| Excerpts | — (Expressive Code's plugin API) | `src/plugins/excerpts.mjs`, a remark plugin that wraps fence and header in one element (spike) | ours (spike) |
| Asides | Starlight's `note`/`tip`/`caution`/`danger`; `starlight-markdown-blocks` 0.1.1 | `src/plugins/asides.mjs`, Starlight's aside markup (spike) | ours (spike); the package is the fallback |
| Answers | `starlight-markdown-blocks` 0.1.1 | `src/plugins/answers.mjs`, `<details>` (spike) | ours (spike) |
| Front matter schema | `docsSchema({ extend })` in `src/content.config.ts` | the cross-page rules: `src/plugins/strips.mjs`, `tools/pages.py` (spike) | both |
| Picture zoom | `starlight-image-zoom` 0.16.2 | the picture links its published file | ours (spike) |
| Before and after slider | `img-comparison-slider` 8.0.7 | `<book-compare>`: two pictures and an `<input type="range">` (spike) | ours (spike) |
| Math | `remark-math` 6.0.0, `rehype-katex` 7.0.1 | `rehypeBookMath` in `src/plugins/rehype.mjs` fails the build (spike) | both |
| Diagrams | `mermaid-isomorphic` 3.1.0 | `scripts/diagrams.mjs` (render, commit, check), `src/plugins/mermaid.mjs`, `src/lib/diagrams.mjs` (spike) | both |
| Code blocks | Expressive Code 0.44.3 with line numbers and collapsible sections | `ec.config.mjs` (spike) | package |
| Search | Pagefind 1.6.0 through Starlight | `data-pagefind-*` attributes written by `PageTitle` and our plugins | package |
| Sitemap | `@astrojs/sitemap` 3.7.4 | the filter | package |
| Tabs | — | `src/plugins/tabs.mjs`, `<book-tabs>` (spike) | ours |
| Figures | — | `src/plugins/figures.mjs`, `src/lib/figures.mjs`, `src/lib/images.mjs` (spike) | ours |
| Glossary | — | `src/plugins/glossary.mjs`, `src/lib/glossary.mjs` (spike) | ours |
| Top strip and page shape | — | the `PageTitle` override, `src/plugins/strips.mjs` (spike) | ours |
| Track navigation | — | `src/plugins/navigation.mjs`, the `Pagination` override (spike) | ours |
| Unknown directives | — | `src/plugins/report.mjs` (spike) | ours |
| Steps, file trees, include, part pages | — | to write | ours |
| Text for agents (`llms.txt`) | `starlight-llms-txt` 0.12.0 | — | not used: the book is written for people and is not offered as a corpus; an agent that works on the engine has the engine's own guide and skills (`critique/rulings-6.md`, R20) |

Two rules for our own plugins:

1. Starlight restores unknown text and leaf directives as text, but not container directives, and its asides plugin
   runs after ours. So `src/plugins/report.mjs` fails the build on every container or leaf directive it does not know
   and lets `note`, `tip`, `caution` and `danger` through.
2. A remark plugin cannot load a script. The scripts of tabs, the slider and the track navigation are one module,
   `src/components/client/book.js`, loaded once per page by the `PageTitle` override (spike).

Figures, tabs, the glossary and the track navigation have no package and carry the risk: the spike exercises them
first, at full scale.

## Front matter and the teaching checks

The front matter is the one of `style.md` §6.1; this file says what the build enforces. `src/content.config.ts`
(`docsSchema({ extend })`, spike) checks its shape:

| Key | Shape |
| --- | --- |
| `id` | the file's path under `src/content/docs/` without `.md` |
| `title`, `description` | strings; `description` at most 160 characters |
| `kind` | `primer`, `concept`, `internals`, `tutorial`, `how-to` or `reference` (the outline's P, C, I, T, H, R) |
| `size` | `S`, `M`, `L` or `XL` |
| `tracks` | a list of the letters `G`, `B`, `E` (spike); `[]` for a page on no track |
| `needs` | at most five page ids; `a\|b` means either page; `[]` for the outline's `-` (spike: renamed from `prerequisites`) |
| `time` | whole minutes; absent on reference pages |
| `learn` | two to five `{id, text}`, ids unique on the page; absent on reference pages |
| `since` | a release `X.Y.Z` |
| `status` | `draft`, `reviewed` or `final` |

The spike's `level` and `engine` keys are gone (spike): the level is computed from the Needs closure and the engine
release comes from `engine.pin` (`style.md` §6.2). The landing page (`index.md`) and `404.md` carry only `title` and
`description`. The part pages `<part>/index.md` and `<part>/review.md` carry `id`, `title`, `description`, `tracks`,
`status` and `generated: index` or `generated: review` (spike); the build draws their generated part
([Navigation](#navigation)).

### Outline rules on the pages

`plan/check_outline.py` checks the outline. Today it holds its rules itself and imports nothing. The tool builder
moves those rules into `tools/booklib/outline.py`, with unit tests, and makes `plan/check_outline.py` call that module;
`tools/pages.py check` (spike, extended) runs the same module on the pages' front matter. From then on there is one
implementation, so the plan's check and the site's check cannot disagree. Until then CI runs both (`lint` job). The
build's strips plugin checks what one page can.

| Rule | Fails when |
| --- | --- |
| O1 | an `id` is not unique, differs from the file's path, is not lowercase (`^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$`, spike), or starts with a reserved segment |
| O2 | a Need, or one alternative of `a\|b`, is not a page |
| O3 | a page's Needs name more than five page ids, alternatives included |
| O4 | for a track in the page's `tracks`, a Need (none of its alternatives) does not come earlier in that track's list |
| O5 | a track's list in `src/sidebar.json` (spike) holds anything but existing page ids, holds one twice, or differs from the track's list in `plan/tracks.md`; or a page's `tracks` does not name exactly the tracks whose list holds it. Then every page of a track is reached by following "next" from the track's first page |
| O6 | Needs form a cycle (spike) |
| O7 | a page's `title`, `kind`, `size`, `tracks` or `needs` differ from its row in `plan/outline-*.md`, or a page that is not a part page has no row: pages and plan cannot drift |
| O8 | a part with eight or more outline rows lacks `<part>/index.md` or `<part>/review.md` |
| O9 | the sidebar does not list the 25 parts of `book.md` in order, or does not list every page exactly once (spike) |

An outline row with Needs `-` has `needs: []`. The part's first page is not enforced as a Need, because a track may
enter a part in the middle (track G reads `basics/programming-1` without `basics/computer`); the top strip only shows
it ("Before you start").

### Page shape

The strips plugin (`src/plugins/strips.mjs`, spike, extended) checks every rule `style.md` §14 assigns to it. Those
that the critique asked the site to check:

| Rule | Fails when |
| --- | --- |
| P1 | the body's last section and the bottom strip are not the headings `style.md` §6.3 gives for the page's kind, in order, or their counts are wrong (Summary items, questions, exercises, practice) |
| P2 | a `learn` id is in the `tests` of no "Check yourself" answer, or a `tests` names an id that is not a `learn` id of the page |
| P3 | a primer does not open with `::::test-out` before any heading, the box does not hold exactly five questions each with an `:::answer{tests="…"}`, or the box's `tests` do not cover every `learn` id |
| P4 | a page of kind internals quotes the engine fewer than three times (spike) |

### Language

`tools/lint.py` (spike, extended) implements every rule id of `style.md` (§2.2 and the sections it names), with its
definitions of prose, word, sentence and paragraph, and its word lists in `tools/data/` (spike). Among them are the
measures the critique asked for: `sentence-mean` (at most 20 words on average), `sentence-max` (35), `paragraph-length`
(five sentences), `term-section` (four new terms per level-2 section), `word-list` (words outside the lists),
`acronym`, `banned-word` (with "it follows" and "it is easy to see") and `long-quote` (25 lines on pages of tracks G
or B and of level 1). `tools/names.py` checks names, paths and UI labels against the pin (pipelines.md).
`tools/lint.py` reads the pin too: its rule `copied-text` compares the pages with the engine's own documents, so it
takes `--engine <clone>` (`critique/rulings-6.md`, R26).

The site adds three rules of its own. Two are for its code and front matter: `inline-env` (`import.meta.env` inside
a `<script is:inline>`) and `front-matter-head` (a `head` key in a page's front matter) (base path rules 3 and 4). The
third is for its settings: `literal-origin`, the literal origin outside the files that may hold it
([the settings](#where-the-site-is-served-the-settings); `critique/rulings-6.md`, R24).

## Navigation

- **Sidebar**: the 25 parts in `book.md`'s order, each a collapsed group except the reader's current part. A part with
  an index page lists it first and its review page last.
- **Every page** shows breadcrumbs (book, part, page; spike), the top strip, "On this page", previous and next, and the
  footer. The top strip (the `PageTitle` override, spike) shows what `style.md` §6.2 lists: the kind badge; one badge
  per track, "G", "B", "E", whose accessible names "Game maker", "Beginner" and "Engine builder" are visually hidden
  text, not a `title`; the level, computed from the Needs closure, and what it means; "About N minutes"; "New in
  0.8.0" when `since` equals the pin's `release`; "Draft"; "After this page you can" with the `learn` texts; "Before
  you start" with the Needs as links (an alternative shows as "X or Y"; `needs: []` shows the part's first page);
  on the first page of a part with fewer than eight pages, which has no index page, "Before this part" with the part's
  Needs of the part from `plan/outline-*.md` (`style.md` §6.2); the engine release and commit of the pin, marked pre-release while `engine.pin` says `prerelease yes` (spike); and a link
  to the part's print view (spike).
- **Tracks** are G, B and E (spike: `src/sidebar.json` keys them `game`, `beginner` and `engine`, with the labels "Make
  games", "Learn from zero" and "Understand and change the engine"). The reader chooses on `start/how-to-read` with
  `::track-chooser` (spike); the choice is kept in `localStorage` under `strata-book:track` (spike). The `Pagination`
  override writes previous and next of **every** track that holds the page into the HTML, each set inside a
  `<template data-book-track="<track>">` (spike); the client script shows the chosen track's set. Without a choice or
  without scripts, previous and next follow the sidebar.
- **Part pages** for parts of eight or more pages (`generated: index` and `generated: review`, spike). The build draws
  the generated part, and the part editor's paragraph and questions stay where the editor wrote them. `<part>/index`
  (URL `<base>/<part>/`): the Needs graph of the part's pages as a diagram, the pages outside the part that they need
  ("Before this part"), what the reader can do afterwards (their `learn` texts) and the notation table.
  `reference/index` shows no "Before this part": the reference is on no track and readers reach its pages by links and
  search, so each reference page shows only its own Needs, in its top strip ("Before you start")
  (`critique/rulings-7.md`, R30). `<part>/review`: every "Check yourself" question of the part's pages, by page, with
  its answer, followed by the part editor's cumulative exercises.
- **Print views** (`src/pages/print/[part].astro`, spike) at `<base>/print/<part>/` hold every page of a part in
  sidebar order, for printing to PDF from a browser. Every id is prefixed with the chapter's id
  (`core--time--the-accumulator`, spike); links between the part's own pages become links within the page (spike);
  `pagefind: false` (spike); the sitemap filter leaves them out; `<meta name="robots" content="noindex">`; every
  `details` is open and every image loads eagerly; the footer line is printed. PDF and EPUB files are a later step.
- **Footer**: every page and every print view ends with the line "© 2026 2042Third. All rights reserved.", built from
  `site.json`'s `copyright`, a link "License" to `<base>/license.txt` and a link "Third-party notices" to
  `<base>/third-party-notices.txt` (`critique/rulings-6.md`, R20). It is a Starlight `Footer` override, so the print
  views carry it and the print style sheet does not hide it; it keeps Starlight's previous and next (the `Pagination`
  override) and draws no edit link. The fallback pages of moved pages and the 404 page carry it too: gate (a) fails on
  an HTML file without the line and its two links.
- **No way into the book's repository**: no page has an "edit this page" link, a link to the repository's files,
  issues or releases, or a badge, and no page and no file of the repository asks for pull requests, translations or
  copies. A page's front matter sets no `editUrl`: the schema and `tools/pages.py check` refuse the key (R20). Gate
  (a) fails on any link to the book's repository.
- **Without scripts** a page still shows everything: all tab panels, both pictures of a slider, answers in `details`
  that open, the glossary popover (native HTML), previous and next in sidebar order.

## Pictures

What the engine renders and how is pipelines.md's. This section decides what is committed, what is published and what
the site derives.

- **Committed**: the recipes (`src/content/figures/<part>/<chapter>.json`, spike), the stamps
  (`src/assets/figures/<part>/<chapter>/taken.json`, pipelines.md §5.7; spike: the recipe's `taken` block) and the
  published files `src/assets/figures/<part>/<chapter>/<figure>[-<variant>][-<crop>].<avif|webp|svg>`, where `<crop>`
  is the crop's name in the recipe (pipelines.md §5.2; spike: one crop per recipe, named `-crop`). A committed name has
  no hash; the build adds one (below). PNG originals are never committed.
- **One format per picture.** A recipe says `publish: "lossy"` or `publish: "lossless"`. Lossy pictures are AVIF;
  lossless pictures are lossless WebP; drawings are SVG. Crops are always lossless. Pictures of the editor's
  interface are lossless unless the recipe says `publish: "lossy"` (AVIF at quality 90), which it says for a picture
  that is mostly the engine's image and whose text a side-by-side at 1:1 shows as sharp as the lossless file's
  (`critique/rulings-13.md`, R59). Renders are lossy unless the recipe says otherwise; a figure that exists to show pixels (aliasing, noise,
  banding, shimmer, sharpness) is lossless. PNG is not a published format.
- **Encoding** happens once, when `tools/figures.py publish` publishes a picture (pipelines.md §5.7), in
  `node scripts/encode-figures.mjs`, which the tool builder writes (sharp 0.35.5; Python's standard library encodes
  neither AVIF nor WebP). Lossy: AVIF quality 80, chroma 4:4:4, effort 4; both sides of a
  `::compare` at quality 90. Lossless: WebP lossless. Nothing is resized: a published render has the capture's size (1920×1080
  unless the recipe says otherwise; 3840×2160 only where the recipe asks for it), and a crop is cut from the original
  at its native pixels (320×180 for the usual rectangle) and never resampled.
- **Derived at build** (`src/lib/images.mjs`, cached in `.cache/images/`, spike): a lossy picture is served unchanged
  at its own width, plus one 960-pixel-wide AVIF (quality 80, effort 2) made from it, plus a 1920-pixel-wide AVIF when the
  capture is 3840 wide. Lossless pictures get no derived file. SVG drawings are inlined into the page (spike).
- **Served names carry a content hash**: `<base>/_figures/<part>/<chapter>/<figure>[-<variant>][-<crop>].<hash>.<width>.<ext>`,
  where `<hash>` is the first 10 hex digits of the SHA-256 of the published file (spike: `src/lib/images.mjs`). This is
  the only hash in a picture's name. Servers cache them for a year. Published files with the same bytes (one capture
  that two figures show) are served once, under the name of the first of them in path order (R59).
- **HTML**: an `<img>` with `src` (the published file), `srcset` and `sizes` for lossy pictures, `width` and `height`
  (no layout shift), `alt` and a `<figcaption>` from the recipe (both required, spike), `decoding="async"`, and
  `loading="lazy"` except the page's first picture when it stands in the first screen (`loading="eager"`,
  `fetchpriority="high"`): at most 300 characters of text before it (`c_FirstScreenCharacters` in
  `src/plugins/figures.mjs`). A slider's second side is lazy. `sizes` is the content column's width as the layout
  gives it (`c_Sizes`, measured in the built site): `calc(100vw - 2rem)` below 50rem, beside the sidebar from 50rem,
  beside the sidebar and the table of contents from 72rem, at most 48rem; a phone of 412 pixels asks for 380 and takes
  the 960-pixel candidate. Budget row 14's remedy (2026-11-25): a picture below the first screen that loaded at once
  counted in Lighthouse's largest paint, by the whole of its download. The picture links its published file for a
  full-size view.
- **Crops** are shown with `image-rendering: pixelated` at the largest whole factor up to the recipe's `scale` that
  fits the column (container queries in `src/styles/book.css`), never at a fractional factor; a crop wider than the
  column scrolls. Gate (b) checks at viewports 375, 768 and 1280 pixels wide that every crop's rendered width is a
  whole multiple of its natural width.
- **Slider pairs**: both sides have the same size, the same `publish` value and the same encoder settings.
- **Checks** (`tools/figures.py check`, spike: `validate`, extended; pipelines.md §5.8): the extension follows `publish`; crops and interface
  pictures are lossless; a render has the capture's size and a crop its rectangle's size in capture pixels; slider
  pairs match; the published file's SHA-256 equals its stamp's; no published file is left that no recipe promises
  (spike).
- **Stamps** (`taken.json`, pipelines.md §5.7) record, per published file: the engine commit and the build, the GPU
  and the OS, the size, the SHA-256 of the PNG original it was encoded from, the SHA-256 of the published file, the
  encoder settings and sharp's version, the recorded values and, for a "before" picture, the baseline set.
- **Originals**: `tools/figures.py publish` copies every PNG it encodes into `originals/<sha256>.png` in the docs clone,
  named by its own SHA-256. `.gitignore` names the folder, and no run empties it (unlike the work folders of
  pipelines.md §2), so the original of every published file stays on the machine that takes pictures and a retake never
  overwrites it. At a book release, `python -I tools/figures.py archive --tag <tag>` packs every original a stamp names
  into `release/strata-engine-docs-originals-<tag>.tar`, and fails when one is missing or the archive is larger than
  1 GB; it writes the archive's SHA-256 into a `.sha256` file beside it. The authoring machine has no `gh` login,
  and the git credential is never used as a token (`critique/rulings-6.md`, R25 and R26): the integrator moves
  both files to `G:/GameEngineAI/.worktrees/docs-originals/`, outside the clone, and tells the owner, who attaches
  them to the GitHub Release or keeps them with their backups. A machine that lacks an original reads it from
  that archive.
- **Retakes** write a new PNG original. When its SHA-256 equals the stamp's, nothing changes. Otherwise `figures.py
  publish` encodes it with the recipe's settings (`node scripts/encode-figures.mjs encode`), decodes the new file and
  the committed one (`node scripts/encode-figures.mjs diff`), and the new file is a candidate only when the mean
  absolute difference over all pixels and channels is above 0.5 (of 255), or the mean over some 16×16 block is above 4.
  The photographer judges each candidate and accepts it or not; an accepted one replaces the committed file, and the
  stamp names the new original. Below the threshold, the committed file and the stamp's hashes stay; the stamp only
  records that the picture was checked at the new engine commit. Pictures of the whole editor follow the same rule. The
  thresholds are set here; the first pin move reports how many pictures each would replace, and the planner may change
  them once, before the first release.
- **Repository size**: at most 1 GB before the book of 0.9 starts (the weekly job reads it with
  `gh api "repos/$GITHUB_REPOSITORY" --jq .size`). Git LFS is not used; if it ever is, CI never fetches LFS
  objects. The estimate for one version is 0.2 to 0.3 GB of pictures.

## Diagrams

Mermaid diagrams are drawn once, committed, and read by the build. The site build starts no browser.

- A diagram is a fence `mermaid caption="…" alt="…"` (spike). `caption` says what to notice and is shown as a
  `<figcaption>`; `alt` says what the diagram shows and becomes the inline SVG's accessible name (`role="img"`,
  `aria-label` and `<title>`). Both are required (spike).
- `npm run diagrams` (`node scripts/diagrams.mjs`) renders every fence whose files are missing, with
  `mermaid-isomorphic` 3.1.0, Mermaid 11.17.2 and Playwright's Chromium, `htmlLabels: false`, `securityLevel: 'strict'`,
  and the font Inter Variable loaded from `@fontsource-variable/inter` into the rendering page (spike), once in the
  light theme (`neutral`) and once in the dark theme (`dark`, with edge labels on a darker background, spike). It
  writes `src/generated/diagrams/<hash>-light.svg` and `<hash>-dark.svg`, where `<hash>` is the first 16 hex digits of
  the SHA-256 of the diagram's text (LF line ends, trimmed) and the renderer's key (Mermaid's version and the
  settings). It runs on one machine, the integrator's, so every diagram is drawn by one platform's fonts.
- The page inlines both SVGs (spike) and the style sheet shows the one of the current theme. The diagram therefore uses
  the page's own Inter, and no font is embedded. Ids inside each SVG are prefixed with `<hash>-<theme>-`, so the two
  copies on one page share no id.
- `astro build` fails when a fence has no committed pair. `npm run diagrams -- --check` (CI) fails on a missing pair,
  on a committed file no fence uses, and on a file that is not the renderer's output for its text. A diagram with a
  syntax error is never written: the renderer fails. In `astro dev`, a missing diagram is rendered into
  `src/generated/diagrams/` so that the integrator sees it.
- Contrast: `npm run diagrams -- --contrast` renders a fixture diagram with every element type in both themes and
  fails when text and its background differ by less than 4.5:1. It runs once per change of the renderer's settings.
- Labels: gate (b) fails when a label's text box leaves its node's box.

## Math

`remark-math` 6.0.0 and `rehype-katex` 7.0.1 (KaTeX 0.16.47) render formulas at build time; readers' browsers run no
math code. `rehype-katex` 7.0.1 ignores `throwOnError` and reports a formula it cannot render only as a warning with a
red error span, so `rehypeBookMath` (`src/plugins/rehype.mjs`, spike), which runs after it, fails the build on any
message whose `source` is `rehype-katex` and on any element with the class `katex-error`. Gate (a) checks again that
the built HTML holds no `katex-error`. KaTeX's MathML stays for screen readers; `.katex-html` carries
`data-pagefind-ignore`. KaTeX's CSS and fonts come from npm through `customCss` (spike), so they are served under
`_astro/`. Math in a heading fails `tools/lint.py` (rule deep-heading, spike), and so does `$` followed by a digit in
prose (dollar-digit, spike).

## Glossary

`src/content/glossary.json` (spike) holds one entry per thing: the term, its one-sentence definition, its home page,
its use home in part `make` where it has one (the entry's `use`) and its other names. Its fields and how entries are
admitted are pipelines.md's; the build needs each entry's `id`, which the spike's entries do not have yet (it derives
one from the term).

- A writer marks a term's use explicitly: `:term[text]{id=<id>}`. There is no automatic matching in the build. The
  first marked use on a page renders a link to `<base>/reference/glossary/#<id>` followed by a small button with
  `popovertarget`, which opens a native `popover` holding the definition, a link to the term's home page and, where
  the entry has a `use`, a link to its use home. Escape closes it and focus returns to the button; without popover
  support, the link still leads to the entry.
- The linter finds the uses writers did not mark, and terms taught neither on the page nor in its Needs closure
  (`style.md` §3: `term-mark`, `term-source`, `term-defined`, `term-paragraph`, `term-section`).
- `reference/glossary` draws every entry with `::glossary` (spike) as one `<dl>`: each `<dt>` has `id="<id>"` and
  `data-pagefind-title`, each `<dd>` the definition, a link to the home page and, where the entry has a `use`, a link
  to its use home (`critique/rulings-7.md`, R33). The page sets `tableOfContents: false`.

## Search

Pagefind 1.6.0 indexes the built site through Starlight's integration (the Node API, with no configuration), so every
choice below is an attribute in the HTML, except the first two. Starlight's search does not run in `astro dev`;
`npm run preview` (spike: `python tools/crawl.py --serve-only`) serves the built site with search.

- **The index's chunk size.** A query downloads the chunk of Pagefind's index that holds each of its words. Pagefind
  closes a chunk at 20,000 word positions, about 40 KB in the released book, so the two words of the next query cost
  80 KB of budget row 12's 100 KB before a result loads. The book's integration sets
  `PAGEFIND_UNSTABLE_INDEX_CHUNK_SIZE` to 2,000 for the build (`c_SearchIndexChunkSize` in `src/lib/search.mjs`; Pagefind
  1.6 reads it from the environment only, and its name says Pagefind may change it: an upgrade measures row 12 again).
  Chunks are then about 5 KB; the first query's chunk list grows by about 10 KB and the site by about 750 files.
- **The ranking.** Starlight's search ranks with the weights it gives Pagefind's UI (`pageLength` 0.1, `termFrequency`
  0.1, `termSaturation` 2, `termSimilarity` 9, `diacriticSimilarity` 0.8, Starlight's defaults). `c_SearchRanking` in
  `src/lib/search.mjs` writes them out, `astro.config.mjs` gives them to Starlight, and the search test ranks with them,
  so that it judges the ranking readers get, not Pagefind's own defaults.
- Each page sets `data-pagefind-meta="title:<title> · <part label> · <kind label>"`, so Starlight's Default UI shows
  part and kind in every result without a `Search` override. The spike's separate `kind` and `part` meta keys stay
  (spike).
- `data-pagefind-filter` for `part`, `kind` and `track` (one value per track that holds the page).
- Weights: code blocks `data-pagefind-weight="0.5"`, generated reference `0.3`, headings the default.
- `data-pagefind-ignore` on line-number gutters (spike), the top strip, `.katex-html` and the MathML's `<annotation>`
  (the formula's TeX source), previous and next with the track templates (spike), the footer line, the glossary's
  popovers and the button that opens one ("Definition of <term>", which would count the term on every page that uses
  it), every theme's drawing of a diagram but the first (the drawings repeat the same words), and the hidden element
  that holds the metadata and filters (Pagefind still reads them there; as words, the part's and the kind's names would
  count on every page of the part). Print views (`pagefind: false`, spike) and the 404 page are not indexed.
- **The search test** (`scripts/search-quality.mjs`, Playwright on the built site, through Pagefind's script) runs the
  60 fixed queries of `scripts/search-queries.json`: 30 glossary terms, 20 engine names (such as `SceneRenderer`,
  `ST_CORE_ASSERT`, `viewport.capture`) and 10 questions, each with the page id expected (the term's home page in
  `book.md`'s one-home table or in the glossary). It passes when the expected page is among the first three results
  for at least 90 % of the queries and for every engine name.
- The transfer test (`scripts/search-payload.mjs`, spike) measures the bytes of the first two-word query and of the
  next query against the budget. In the released book (2026-11-25) the next query is two index chunks of about 5 KB
  and four fragments of 16 to 27 KB: a fragment holds its page's whole indexed text, so the chapters' length is most of
  what remains.

## Generated reference

The reference tables come from the engine (pipelines.md: the dumps at the pin, `tools/reference.py render`, pure
Python). This section decides where they land and how they render.

- Generated Markdown is written to `src/generated/reference/<table>.md`, outside the content collection, so Starlight
  never makes a page of it. (Starlight's loader skips files whose name starts with `_`, not folders:
  `src/content/docs/reference/_generated/x.md` would become a duplicate page.)
- The hand-written page `src/content/docs/reference/<table>.md` holds the front matter, one paragraph on what the table
  is and how to read it, and `::include{file="<table>.md"}`. The include plugin parses the file with the book's own
  Markdown pipeline at that place: its headings get anchors, the page index sees them for link checks, and the print
  view includes them. Its content is wrapped in an element with `data-pagefind-weight="0.3"`.
- Each generated file starts with a stamp: `<!-- generated by tools/reference.py <version>; engine <40 hex digits>;
  sha256 <hex of the rest of the file> -->`. CI fails when the commit is not `engine.pin`'s or the hash does not match
  the content (a hand edit).
- Rendering: parameters as tables (name, type, required, default, description); each JSON Schema in a closed
  `<details>` as a `json` fence; every string from the engine escaped for Markdown and HTML (`<`, `>`, `&`, `"`, `|`,
  backticks), never passed as raw HTML.
- `reference/commands` (about 150 commands with their schemas) stays one page, which includes one generated file per
  command group (`critique/rulings-13.md`, R59: a reader looks a command up on it). `tools/reference.py render`
  estimates the page's size from the Markdown (`tools/booklib/tables.py`, fitted to the built pages: 1,541 KB
  estimated, 1,547 KB built in book-v0.8.0-r2) and fails when it would exceed the largest-page budget of
  `tools/budgets.json`, for a ruling on the budget.

## Moved pages

Nothing is published yet, so ids may change freely until the first release. After it, a page whose id disappears gets
an entry in `src/redirects.json`: `{ "redirects": [{ "from": "<old id>", "to": "<new id>" }] }`.

- The book's integration writes a fallback page at `<base>/<old id>/index.html`: `<meta http-equiv="refresh">` to the
  new page, `rel="canonical"` to it, `noindex`, a plain link, and the footer line with its two links.
- `tools/release.py` writes the server rules, `nginx-redirects.conf`: an exact `location` returning 301 for the old URL
  with and without its slash.
- `tools/pages.py check` fails when a `from` is a current page, a `to` is not one, or an entry points at another
  `from`. At each release the integrator writes the list of page ids into `src/published-pages.json`
  (`python tools/pages.py published --write`); a page id of that list that is neither a page nor a `from` fails the
  check.
- Until the file has a real entry, the CI build at the base `/x/y/` adds the test entry of
  `tools/tests/fixtures/redirects.json`, so the redirect paths are tested.

## Checks

| # | Check | Tool | Fails on |
| --- | --- | --- | --- |
| 1 | Front matter, outline rules, sidebar, tracks, page shape; the copyright statement and the notices | `tools/pages.py check` (spike), `plan/check_outline.py`, the strips plugin in the build; `tools/notices.py check` | rules O1 to O9, P1 to P4 and the strips rules of `style.md` §14; the rules of `LICENSE`, `package.json` and the notices ([Layout of the repository](#layout-of-the-repository)) |
| 2 | Links and anchors | the links plugin (build); gate (a) | a missing page or anchor; an absolute or host-only link |
| 3 | Excerpts | `tools/excerpts.py check --engine <clone>` (spike; pipelines.md) | a quote that differs from the pin; a link to the engine repository whose commit or path does not exist |
| 4 | Math, diagrams, sketches | the build (`src/plugins/rehype.mjs`); `npm run diagrams -- --check`; `tools/sketches.py check` (spike) | a KaTeX message or `.katex-error`; a fence without its committed pair or a committed file without its fence; a sketch that does not compile or prints something else |
| 5 | Figures | `tools/figures.py validate [--release]` (spike) | the rules of [Pictures](#pictures); in a release, any placeholder |
| 6 | Tutorials | `tools/pages.py check --release` (spike; pipelines.md) | in a release, a tutorial without a current stamp |
| 7 | Generated reference | `tools/reference.py render --check` (pipelines.md) | a stamp whose commit is not the pin's; content that differs from its stamp's hash |
| 8 | Language | `tools/lint.py --engine <clone>` (spike), `markdownlint-cli2`, `typos`, `tools/names.py` | every rule id of `style.md`; `inline-env`, `front-matter-head`; `literal-origin`: the literal origin outside the files that may hold it ([the settings](#where-the-site-is-served-the-settings)) |
| 9 | Accessibility | `scripts/a11y.mjs --all` (spike, extended), `scripts/keyboard.mjs`, `scripts/lighthouse.mjs` | below |
| 10 | Base path and deployment | gates (a), (b) and (c) | [The three gates](#the-three-gates) |
| 11 | Search | `scripts/search-payload.mjs` (spike), `scripts/search-quality.mjs` | budget rows 12 and 13 |
| 12 | Budgets | `tools/budgets.py`, `tools/measure.py` (spike) | the rows CI measures |
| 13 | The build's own code | `npm test` (spike: `node --test src/plugins/tests/` and `python -m unittest discover -s tools/tests -t .`) | a failing test |

Accessibility:

- axe (`@axe-core/playwright` 4.14.0, rules tagged `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `best-practice`, spike)
  runs on every page of the build, print views and the 404 page included, in the light and the dark theme: 0 serious
  or critical violations. The spike's one exclusion (the label of Starlight's search button, which axe reports as
  `label-content-name-mismatch`) stays until Starlight changes the button (spike).
- Keyboard (`scripts/keyboard.mjs`): tabs follow the ARIA tabs pattern (arrow keys move between tabs, Home and End go
  to the first and the last, Tab leaves the list); the slider is an `<input type="range">` with a label, moved by the
  arrow keys; an answer opens with Enter and with Space; a glossary popover opens from its button, closes with Escape,
  and focus returns to the button; the track chooser's buttons are reachable, and after a choice "next" follows the
  track.
- Lighthouse accessibility 100 on one page of each of the six kinds, the landing page and the glossary.
- Badges have accessible names; every picture and diagram has alt text (the plugins require it, spike); diagram
  contrast is checked at render time.

## The three gates

The gates prove that the built site works under its prefix on the real servers. A crawl over static files alone
cannot see requests made by scripts, `srcset` candidates the browser does not pick, response headers, `Location`
headers, case on a case-sensitive disk or the server's 404 behaviour.

### (a) Static

On the staged folder: `tools/crawl.py` (spike) stages `dist/` as `stage/<base>/` and serves `stage/` with its own
static server, which behaves as the deployments do (index files for folders, a redirect to add the slash, the site's
`404.html` with status 404, no listings; spike).

1. **lychee 0.24.2**: `lychee --offline --root-dir <absolute path of stage> --include-fragments --no-progress
   'stage/**/*.html' 'stage/**/*.css'` reports 0 failures.
2. **`tools/crawl.py`** starts at `<base>/` and follows every link, `src`, `srcset` candidate, style sheet with its
   `url()`s, script and module import, the manifest, the sitemap, canonical links, and the links inside `<template>`.
   It fails when:
   - anything answers other than 200 (spike);
   - a URL of the site leaves the prefix, or a page requests the host's root (spike);
   - a resource (anything but `<a href>`) loads from another host (spike);
   - an `<a href>` names a host not listed in `tools/external-hosts.txt`;
   - a link into the engine's repository (`engine.pin`'s `repository` line followed by `/blob/` or `/tree/`) names a
     commit that is not 40 hex digits, or names another commit than the pin outside a `:::history` aside;
   - a link names the book's repository, `https://github.com/2042Third/strata-engine-docs`, with any path or none
     (`critique/rulings-6.md`, R20);
   - a link names an anchor its page lacks (spike);
   - a URL path holds a capital letter or a non-ASCII character, or does not match a file byte for byte (on Linux);
   - a file of the build is referenced by nothing, except `404.html`, `pagefind/**`, `sitemap-*.xml`,
     `manifest.webmanifest`, `favicon.svg` and the `.gz` files beside other files;
   - an HTML file lacks the footer line and its links to `<base>/license.txt` and `<base>/third-party-notices.txt`
     (R20);
   - a built style sheet holds a `data:` URL of a font (R23);
   - `canonical` or `og:url` is not the origin + the base + the page's path, or names a page that does not exist
     (the 404 page is exempt);
   - the build holds a `robots.txt`;
   - the HTML holds an element with the class `katex-error`;
   - a three-level missing path does not answer the 404 page with status 404 (spike).
3. **At the base `/x/y/`**, no URL, CSS, script or JSON string of the build starts with `/strata-engine-docs`.

`tools/crawl.py --url <server>/<base>/` runs the same crawl against a server that already runs: CI's servers, or the
live address. There the host's root may answer 200, as a host with a site of its own always does; a page that
requests it still fails (`critique/rulings-6.md`, R24).

### (b) Runtime

`scripts/runtime.mjs --url <server>/<base>/` runs Playwright's Chromium against real servers, all of them nginx
(`critique/rulings-6.md`, R23): nginx 1.30.6 as the container of `deploy/Dockerfile`, and the host proxy of
`deploy/nginx-proxy.conf` in front of it; nginx 1.20.1 as the official image `nginx:1.20.1` with the release's files
copied in the way `deploy/README.md` says, inside a server block that also serves another site at the root. In CI
these run on `ubuntu-latest`; on the authoring machine `tools/servertest.py` runs the Windows builds of nginx 1.30.6
(spike) and 1.20.1 from `.tools/`, with the copied files. The container image itself is tested only in CI.

It loads the landing page, one page of each kind, the glossary, a print view and the missing path `<base>/a/b/c/`;
runs two searches (a glossary term and an engine name) and follows the first result; switches the theme; chooses a
track and follows "next"; and records every request. It fails when a request leaves the prefix or the origin, when a
response is not 2xx (except the missing path, which must answer 404 with its assets 2xx), when the browser reports a
Content Security Policy violation or a console error, when a crop is shown at a fractional factor, when a diagram's
label leaves its box, or when the redirect test entry does not answer 301 to its target.

### (c) Headers

`tools/servertest.py` (spike, extended with `--url <server>/<base>/` for a server that already runs) through the same
servers:

| Request | Must answer |
| --- | --- |
| `<base>` | 301; `Location: <base>/`, a path: no scheme, host or port |
| `<base>/core/time` (a page without its slash) | 301; `Location: <base>/core/time/`, a path |
| any page | `Content-Type: text/html; charset=utf-8`; `Cache-Control: no-cache`; with `Accept-Encoding: gzip`, `Content-Encoding: gzip` |
| `<base>/_astro/*.css`, `*.js`, `*.woff2` | `text/css`; `text/javascript` or `application/javascript`; `font/woff2`; `Cache-Control: public, max-age=31536000, immutable` |
| `<base>/_figures/*.avif`, `*.webp` | `image/avif`, `image/webp`; immutable |
| `<base>/pagefind/pagefind.js`, `pagefind-worker.js`, `pagefind-entry.json`, `pagefind-ui.js`, `wasm.en.pagefind` | `no-cache` |
| `<base>/pagefind/index/*`, `fragment/*`, `filter/*`, `pagefind.*.pf_meta` | immutable; no `Content-Encoding` added (Pagefind compresses them itself) |
| `<base>/manifest.webmanifest` | `application/manifest+json` |
| `<base>/a/b/c/` | 404 with the book's 404 page |
| `<base>/_astro/` (a folder without an index) | 404 with the book's 404 page; no listing (spike) |
| a path outside the prefix | in the container: 404, and not the book's 404 page; on a host that serves other things (the 1.20.1 run, `--url`): not the book's 404 page |

Every response under the prefix, the 404 page included, carries `Content-Security-Policy`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` and
`X-Frame-Options: SAMEORIGIN`: every `add_header` of the book carries `always`. None of the four arrives twice,
directly or through the proxy, whose server block in the tests sends `X-Frame-Options` and
`X-Content-Type-Options` of its own, as the real host does (`critique/rulings-6.md`, R26). The book sends no
`Strict-Transport-Security`: that header binds the whole host and is the host's decision (`critique/rulings-6.md`,
R23). `tools/servertest.py` runs its servers once without and once with a host-headers file
([The deploy folder](#the-deploy-folder)): without it, no response under the prefix carries
`Strict-Transport-Security`; with it, every response under the prefix also carries the file's header.

A deployment is accepted by gates (a) and (c) against the live address, which only read (R24):
`python tools/crawl.py --url https://pdm.pw/strata-engine-docs/` and
`python tools/servertest.py --url https://pdm.pw/strata-engine-docs/`.

## Budgets and the spike

The spike builds the whole machine once with fake content at full scale, before any page is written. Every row below
passes or fails; none is set by the spike's own measurement. Machines: the authoring machine (Intel i7-13700K, Windows
11, measurements under the engine's `Tools/PerfLock.py` from the pin clone) and GitHub's `ubuntu-latest` runner. Time
and memory come from `tools/measure.py` (spike: the process tree's peak, sampled four times a second, a lower bound).
Sizes are apparent sizes, measured before precompression; gzip sizes are those of the `.gz` files the release step
writes, which is what a reader's browser receives (`critique/rulings-6.md`, R23).

| # | Measure | Machine | Pass | Remedy before measuring again |
| --- | --- | --- | --- | --- |
| 1 | Warm full build (all caches full) | i7-13700K | ≤ 4 min | caches and plugin costs |
| 2 | Warm full build | `ubuntu-latest` | ≤ 8 min | as row 1 |
| 3 | Cold build: empty `.cache/`, every derived picture encoded | `ubuntu-latest` | ≤ 30 min | fewer derived files |
| 4 | `npm run diagrams`, every diagram from an empty folder | i7-13700K | ≤ 10 min | several browser pages at once |
| 5 | Rebuild after editing one page | i7-13700K | ≤ 90 s | the content layer's cache settings |
| 6 | `astro dev`: start; refresh after an edit | i7-13700K | ≤ 60 s; ≤ 3 s | the page index re-reads only changed files (spike) |
| 7 | Peak memory of the build's process tree | both | ≤ 4 GB | set `--max-old-space-size`; then ≤ 6 GB passes, with the value written into `package.json`'s build script |
| 8 | Two builds of one commit | `ubuntu-latest` | identical `dist/`, except files the spike lists as carrying a time stamp | find and remove the source of the difference |
| 9 | `dist/` of one version | any | ≤ 400 MB; ≤ 15,000 files; the HTML of the chapter pages and of the print views each recorded | picture settings; the sidebar's markup |
| 10 | Largest page (gzip); median page | any | ≤ 300 KB; ≤ 60 KB; the sidebar's share recorded | split generated reference; collapse the sidebar's markup |
| 11 | Scripts per page without search (gzip) | any | ≤ 40 KB | drop or defer components |
| 12 | Search transfer: first two-word query; next query | any | ≤ 300 KB; ≤ 100 KB | weights and ignores |
| 13 | Search quality, the 60 fixed queries | any | expected page in the top three for ≥ 90 %, for 100 % of engine names | weights and metadata |
| 14 | Lighthouse, mobile, the heaviest figure page | `ubuntu-latest` | performance ≥ 90, accessibility 100, CLS ≤ 0.05, LCP ≤ 2.5 s | lazy pictures, sizes |
| 15 | axe, every page, both themes | `ubuntu-latest` | 0 serious or critical | fix the markup |
| 16 | Gates (a), (b), (c) | `ubuntu-latest` | 0 failures: 0 non-2xx under the prefix, 0 requests outside it, 0 unreferenced files | fix |
| 17 | Base portability | `ubuntu-latest` | the builds at `/`, `/strata-engine-docs/` and `/x/y/` all pass gate (a) | fix |
| 18 | Diagrams | i7-13700K | 0 labels outside their boxes; every diagram has alt text and a caption; contrast ≥ 4.5:1 | font and theme settings |
| 19 | Print view of `make` printed to PDF with Playwright | i7-13700K | ≤ 5 min, ≤ 4 GB, 0 duplicate ids | one PDF per chapter |
| 20 | Confirm items (below) | — | every item confirmed | the item's own fallback |

A row that still fails after its remedy fails the spike. A failed spike means: the fallback is built at the same scale
and measured against the same table, before any page is written.

**Confirm items** (row 20). Each is shown on a page of the spike's book, or the spike states how it was checked:

1. Expressive Code puts the excerpt's marks on the engine lines that `mark` names when `startLineNumber` is set.
2. `std::vector`, `a:b` and `10:30` in prose render unchanged (text-directive restoration).
3. An unknown container or leaf directive fails the build; Starlight's `note`, `tip`, `caution`, `danger` still render.
4. A formula KaTeX cannot render fails the build.
5. Mermaid fences reach the book's remark step before Expressive Code.
6. `compressHTML: true` keeps the space between two inline code spans and between a link and the next word.
7. The book's `@astrojs/sitemap` instance with its filter replaces Starlight's: one sitemap, without print views or
   the 404 page.
8. lychee 0.24.2 reads every `srcset` candidate and the links inside `<template>`; where it does not,
   `tools/crawl.py` covers them and the report says so.
9. Pagefind returns a glossary `<dt>` as a sub-result, and finds `ST_CORE_ASSERT`, `Scene::OnUpdateRuntime` and
   `viewport.capture` as whole names.
10. Under the Content Security Policy of the release step, every page runs with no violation and search works.
11. The glossary popover works with the keyboard and without scripts.
12. Crops show at whole factors at the three viewports.
13. The two inline SVGs of one diagram share no id.

Two confirm items that need a fork of Astro or Starlight fail the spike.

**The spike's content follows the book:**

- Every row of the revised outline at its size (S 1,500 words, M 3,000, L 5,000, XL 8,000), with its id, title, kind,
  tracks and Needs, so that the outline rules run at scale. The page count is the one `plan/check_outline.py`
  prints (the critique counted 282 pages and about 1.09 million words).
- The part pages of every part of eight or more pages; one print view per part.
- The reference generated from the inventories at real sizes: about 150 commands with their parameter schemas, 165
  host functions, the glossary of about 1,590 terms plus the beginner vocabulary of the seed's 400 entries.
- 1,500 real quotes of the engine at the pin, about 3,000 code blocks, 400 diagrams, math on a third of the pages
  (spike).
- 600 pictures made from the twelve sample screenshots at the pin (`git show 822a7a46:Samples/<sample>/Screenshots/<name>.png`,
  960×540), upscaled once to 1920×1080 and varied by crop and noise: 450 renders published as AVIF (60 of them in
  slider pairs), 100 crops of 320×180 and 50 interface pictures as lossless WebP.
- The spike's report gives every row's value, pass or fail and the remedy tried, and the verdict. It is written to
  `.tools/spike-report.md` (spike) and copied to `plan/spike-report.md` when the verdict is final, because `.tools/`
  is not committed.

**Pass marks and budgets.** The table's pass marks change only by a ruling. `tools/budgets.json` holds the regression
budgets CI enforces: each is the smaller of its row's pass mark and 1.5 times the latest full-scale measurement. A
budget goes down when a measurement allows it, and up only by a ruling that names what grew. A time that passes its
mark under other load passes; a time over its mark under other load is not judged and is measured again
(`critique/rulings-5.md`, R13 and R14). The crawl's time, lychee included as CI runs it, is recorded with every run as
a measurement of the machine that ran it, and not judged: `tools/budgets.py` prints it without a limit and never fails
or holds a run on it, and `tools/budgets.json` holds no budget for it, only R59's measurement as a record
(`critique/rulings-13.md`, R60). A faster crawl's first measurements set a budget per machine, by a ruling.

**After the spike**, rows 9 to 17 run in CI on every build of the default base and fail it. Rows 1 to 8, 18 and 19 are
measured again at every upgrade of a framework package. The repository's size (at most 1 GB) is read weekly.

## Deployment

The site is deployed from a release: built files, server configurations and checksums. CI builds and tests it; CI
deploys nowhere: the owner decides where the files go. Today they go to `https://pdm.pw/strata-engine-docs/`, a prefix
of a host that already serves a site of its own (`critique/rulings-6.md`, R24). Seen from outside on 2026-11-10, the
host runs nginx 1.20.1 over HTTP/1.1; a Hugo site at its root answers `/strata-engine-docs/` with its 404 page and
keeps its own `robots.txt` with its own `Sitemap` line; it sends `X-Frame-Options` and `X-Content-Type-Options`
without `always`, and no `Strict-Transport-Security` and no `Content-Security-Policy`.

### What a release holds

A release is a GitHub Release of the docs repository, tagged `book-v<engine release>-r<n>` (the first release of the
book of engine 0.8.1 is `book-v0.8.1-r1`). Workflow artifacts expire; releases stay. If the repository is private,
the owner fetches a release with their own login (`critique/rulings-6.md`, R25). `tools/release.py assemble --tag
<tag>` writes `release/<tag>/`; for a build that is not a release, `<tag>` is `main-<first 8 hex digits of the
commit>`:

| Asset | Holds |
| --- | --- |
| `strata-engine-docs-<tag>.tar.gz` | one top folder, `strata-engine-docs/`: the built site, `license.txt` and `third-party-notices.txt` included, with a `.gz` beside every text file of 1 KB or more (`node scripts/precompress.mjs`; `.html`, `.css`, `.js`, `.mjs`, `.json`, `.svg`, `.xml`, `.txt`, `.webmanifest`; not Pagefind's `.pf_*` and `.pagefind` files) and no `.br` file: no stock nginx serves brotli (R23). An owner whose nginx has the brotli module may turn it on; the book neither needs nor tests it |
| `strata-engine-docs-deploy-<tag>.tar.gz` | one top folder, `deploy/`: the committed files of `deploy/` plus the files the release step generates from the built HTML: `nginx-csp.conf` (one `add_header Content-Security-Policy "…" always;` line) and `nginx-redirects.conf` |
| `SHA256SUMS` | the SHA-256 of every asset (`sha256sum -c SHA256SUMS` verifies them) |
| `strata-engine-docs-originals-<tag>.tar` | the PNG originals, attached later by the owner ([Pictures](#pictures)) |

The tarballs are reproducible: entries sorted, time stamps 0, owner 0. The Content Security Policy is generated:
`tools/release.py` reads every HTML file, takes the SHA-256 (base64) of every inline script whose type is executable
(Starlight's theme and sidebar scripts), and writes them into the policy:

```
default-src 'self'; script-src 'self' 'wasm-unsafe-eval' 'sha256-…'; style-src 'self' 'unsafe-inline';
img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self' blob:; object-src 'none';
base-uri 'self'; form-action 'self'; frame-ancestors 'self'
```

`'wasm-unsafe-eval'` and `worker-src 'self' blob:` are what Pagefind needs; `'unsafe-inline'` for styles is what
Starlight and Expressive Code need. `font-src 'self'` holds because no font is inlined: the build's
`assetsInlineLimit` keeps every font a file, and gate (a) fails on a `data:` URL of a font in a built style sheet
(`critique/rulings-6.md`, R23). Astro's own `security.csp` is not used: one policy, sent by the server. The book
shares the origin `https://pdm.pw` with the owner's other site; a script on that origin could read what the origin's
other applications keep in the browser, so the policy lets only the book's own scripts run.

The committed deploy files are written for the base of `site.json`; a test fails when that base and the prefix in
`deploy/` differ (R24). For another base, `tools/release.py assemble --tag <tag> --base <base>` rewrites every deploy
file for that base (the spike's markers `(redirect: begin)`/`(redirect: end)` and `(outside: begin)`/`(outside: end)`
delimit the blocks that a book at the host's root drops) and names the top folder after the base's path.

### The deploy folder

| File | What it is |
| --- | --- |
| `deploy/nginx-http.conf` | http context: the `map` of `Cache-Control` by name |
| `deploy/nginx.conf` | server context: the book's `location` blocks (spike's name) |
| `deploy/nginx-container.conf` | the container's server block (spike) |
| `deploy/nginx-proxy.conf` | the host's server context, when the book runs in the container |
| `deploy/Dockerfile` | an nginx image that serves an already built site; builds nothing |
| `deploy/Dockerfile.build` | optional: builds the site on the server, then serves it like `deploy/Dockerfile` |
| `deploy/deploy-files.sh` | copies a new site over the served one in two passes |
| `deploy/README.md` | how to deploy, for the owner |

`deploy/nginx-http.conf`. A regular expression that holds `{` or `}` must be quoted in nginx's configuration.

```nginx
# The Strata Engine Book: Cache-Control by name (http context, for example /etc/nginx/conf.d/).
# Only names that carry a content hash are cached for a year; everything else is checked again.
map $uri $strata_docs_cache {
	default                                                                   "no-cache";
	~^/strata-engine-docs/_astro/                                             "public, max-age=31536000, immutable";
	"~^/strata-engine-docs/_figures/.+\.[0-9a-f]{10}\.[0-9]+\.(avif|webp)$"   "public, max-age=31536000, immutable";
	~^/strata-engine-docs/pagefind/(index|fragment|filter)/                   "public, max-age=31536000, immutable";
	~^/strata-engine-docs/pagefind/pagefind\..+\.pf_meta$                     "public, max-age=31536000, immutable";
}
```

`deploy/nginx.conf`:

```nginx
# The Strata Engine Book under /strata-engine-docs/, tested with nginx 1.20.1 and 1.30.6. Include this file in the
# server block of the site that hosts the book (include /etc/nginx/snippets/strata-engine-docs.conf;),
# deploy/nginx-http.conf in the http context, and the release's nginx-csp.conf and nginx-redirects.conf as the two
# snippets named below. The site is unpacked so that /srv/www/strata-engine-docs/index.html exists.

include /etc/nginx/snippets/strata-engine-docs-redirects.conf;

# (redirect: begin)
location = /strata-engine-docs {
	absolute_redirect off;
	return 301 /strata-engine-docs/;
}
# (redirect: end)

# ^~ keeps the host's regular-expression locations (such as "location ~* \.(css|js)$") from taking these files.
location ^~ /strata-engine-docs/ {
	root /srv/www;                    # root, never alias: the URL and the path are the same string
	index index.html;
	autoindex off;
	absolute_redirect off;            # Location: /strata-engine-docs/x/, never an internal host or port
	try_files $uri $uri/ =404;
	# A folder without an index.html (such as _astro/) would answer nginx's bare 403 page: it gets the 404 page too.
	error_page 403 404 =404 /strata-engine-docs/404.html;
	charset utf-8;

	# The book's own table of types. A types block replaces the host's mime.types inside this location, so it names
	# every type the book serves but the manifest's, which its own location sets below; nginx 1.20.1's mime.types
	# knows no avif. Pagefind's own files and a .patch take default_type; a browser saves a .patch.
	types {
		text/html                  html;
		text/css                   css;
		text/javascript            js mjs;
		application/json           json;
		application/xml            xml;
		text/plain                 txt;
		image/svg+xml              svg;
		image/avif                 avif;
		image/webp                 webp;
		font/woff2                 woff2;
		font/woff                  woff;
		font/ttf                   ttf;
		application/wasm           wasm;
		application/zip            zip;
	}
	default_type application/octet-stream;

	gzip_static on;                   # the release holds a .gz beside every text file
	gzip on;
	gzip_vary on;
	gzip_min_length 1024;
	gzip_types text/css text/javascript application/javascript application/json application/manifest+json
		application/xml text/xml image/svg+xml;
	# Pagefind compresses its own files: application/octet-stream stays out of gzip_types.

	# Every add_header of the book is here, each with "always", so that the 404 page carries it too. A nested location
	# with an add_header of its own would drop all of these, and these drop every add_header of the host's server
	# block: nginx before 1.29.3 cannot merge them. No Strict-Transport-Security: it binds the whole host, so it is
	# the host's decision.
	add_header Cache-Control $strata_docs_cache always;
	add_header X-Content-Type-Options "nosniff" always;
	add_header Referrer-Policy "strict-origin-when-cross-origin" always;
	add_header X-Frame-Options "SAMEORIGIN" always;
	include /etc/nginx/snippets/strata-engine-docs-csp.conf;
	# Headers of the host that must also reach the book's pages go into such a file. The name holds a wildcard, so
	# the include may match no file.
	include /etc/nginx/snippets/strata-engine-docs-host-headers*.conf;

	# Not every mime.types knows .webmanifest. No add_header here, so the headers above apply (spike).
	location = /strata-engine-docs/manifest.webmanifest {
		types { }
		default_type application/manifest+json;
	}
}
```

`deploy/nginx-container.conf` (spike):

```nginx
# The container's only server: the book on port 8080 (deploy/Dockerfile).
server {
	listen 8080;
	listen [::]:8080;
	server_name _;
	server_tokens off;

	include /etc/nginx/snippets/strata-engine-docs.conf;

	# Nothing else is served: the book does not need the host's root. (outside: begin)
	location / {
		return 404;
	}
	# (outside: end)
}
```

`deploy/nginx-proxy.conf`, in the host's server block when the book runs in the container:

```nginx
location = /strata-engine-docs {
	absolute_redirect off;
	return 301 /strata-engine-docs/;
}
location ^~ /strata-engine-docs/ {
	proxy_pass http://127.0.0.1:8080;         # no URI part: the prefix reaches the container unchanged
	proxy_set_header Host $host;
	proxy_set_header X-Forwarded-Proto $scheme;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

These lines are the file's core. A host whose server block sends headers of its own (as `https://pdm.pw` sends
`X-Frame-Options` and `X-Content-Type-Options`) would add them to the container's, so the file also keeps each of
the book's four headers from arriving twice. Its means is the site builder's choice, explained in
`deploy/README.md` (`critique/rulings-6.md`, R26).

`deploy/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
# The Strata Engine Book in a container: nginx serves an already built site under /strata-engine-docs/. It builds
# nothing. Build it in a folder that holds the unpacked release: strata-engine-docs/ (the site) and deploy/.
#
#     docker build -f deploy/Dockerfile -t strata-engine-docs:<tag> .
#     docker run -d --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 127.0.0.1:8080:8080 strata-engine-docs:<tag>
FROM nginxinc/nginx-unprivileged:1.30.6-alpine
COPY deploy/nginx-http.conf /etc/nginx/conf.d/00-strata-engine-docs-http.conf
COPY deploy/nginx-container.conf /etc/nginx/conf.d/default.conf
COPY deploy/nginx.conf /etc/nginx/snippets/strata-engine-docs.conf
COPY deploy/nginx-csp.conf /etc/nginx/snippets/strata-engine-docs-csp.conf
COPY deploy/nginx-redirects.conf /etc/nginx/snippets/strata-engine-docs-redirects.conf
COPY --chown=101:101 strata-engine-docs/ /srv/www/strata-engine-docs/
RUN nginx -t
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://127.0.0.1:8080/strata-engine-docs/ || exit 1
```

`deploy/Dockerfile.build` is for an owner who builds on the server. Its first stage is the spike's build stage
(`node:26.13.0-trixie-slim`, `npm ci`, `astro build` with `DOCS_BASE`, `DOCS_SITE` and `DOCS_RELEASE` as build
arguments, spike) plus Debian's `python3` for `tools/release.py assemble`; it installs no browser, because diagrams are
committed. The first two arguments have no default, so a build without them takes the values of `site.json`. Its
second stage is `deploy/Dockerfile`'s, with `COPY --from=build` of the built site only. Its header states the need:
about 4 GB of free memory (budget row 7) and up to 30 minutes on four cores without caches (row 3).

The final stage of `deploy/Dockerfile` and of `deploy/Dockerfile.build` holds the built site and nginx's files, and no
`node_modules`: packages that only build or test (axe-core, sharp's libvips, lightningcss, Playwright and the like) are
never shipped (`critique/rulings-6.md`, R22).

`deploy/deploy-files.sh`:

```sh
#!/bin/sh
# Copies a new build over the served book without breaking a reader's open page:
#     deploy/deploy-files.sh <unpacked strata-engine-docs/ folder> <served folder>
# Pass 1 adds new files and deletes nothing, so a page loaded before the copy still finds its hashed files.
# Pass 2 deletes old files, but never archived versions (v0.8/ ...) or versions.json.
set -eu
new="${1%/}/"
served="${2%/}/"
rsync -a "$new" "$served"
rsync -a --delete --exclude '/v[0-9]*/' --exclude '/versions.json' "$new" "$served"
```

### The ten requirements and their tests

| # | Requirement | Where | Test |
| --- | --- | --- | --- |
| 1 | `location ^~ /strata-engine-docs/`, so the host's regular-expression locations cannot take the files | `nginx.conf`, `nginx-proxy.conf` | CI runs the container with `tools/tests/fixtures/nginx-hostile.conf` as its server block: the book's include plus `location ~* \.(css\|js\|png\|svg\|woff2\|avif\|webp)$ { return 418; }`; gates (a) and (b) see no 418 |
| 2 | 301 to the slashed form; `absolute_redirect off` | `nginx.conf`, `nginx-proxy.conf` | gate (c): `Location` is a path, directly and through the proxy on another port |
| 3 | A 404 under the prefix keeps status 404; a folder without an index answers it too | `nginx.conf` (`error_page 403 404 =404`) | gate (b): `<base>/a/b/c/` answers 404 with its assets 2xx; gate (c): `<base>/_astro/` answers 404 with the book's 404 page; a path outside the prefix does not get the book's 404 page, and answers 404 in the container |
| 4 | Caching by name, not by folder | `nginx-http.conf` | gate (c), the table of path classes |
| 5 | Precompressed text files: a `.gz` beside every text file of 1 KB or more, and no `.br` | the release; `gzip_static` | gate (c): `Content-Encoding: gzip` on pages; none added to `.pf_*`; gate (a): a `.br` file is a file referenced by nothing |
| 6 | Security headers, every `add_header` with `always`, and a CSP generated from the built HTML; no `Strict-Transport-Security`; the host's own headers only through the wildcard include | `nginx.conf`, `nginx-csp.conf` | gate (c): the four headers on every response, the 404 page included, and none of them twice; `tools/servertest.py` runs without a host-headers file (no `Strict-Transport-Security` on any response under the prefix) and with one (the file's header on every response under the prefix); gate (b): no CSP violation, search works |
| 7 | No nested `add_header` | `nginx.conf` | `tools/servertest.py` fails when an `add_header` is inside a nested `location` of a deploy file; gate (c) checks the headers on the manifest too |
| 8 | Tested with nginx 1.20.1 and 1.30.6; `root`, never `alias` | `Dockerfile`, `nginx.conf`, `README.md` | the `FROM` tag; CI runs gates (a) to (c) against the official `nginx:1.20.1` image with the release's files copied in the way `deploy/README.md` says, inside a server block that also serves another site at the root, so gate (c) checks the book's own types where `mime.types` knows no `avif`; on the authoring machine, both Windows builds; `tools/servertest.py` fails on `alias` in a deploy file |
| 9 | Two copy passes; the second keeps `/v[0-9]*/` and `/versions.json` | `deploy-files.sh` | CI runs it into a folder that holds `v0.7/index.html`, `versions.json` and a stale `_astro/old.css`: after pass 1 the stale file is there, after pass 2 it is gone and the other two remain |
| 10 | Behind a proxy, `proxy_pass` without a URI part | `nginx-proxy.conf`, `README.md` | CI runs the proxy (a second nginx container on the host network, whose server block sends `X-Frame-Options` and `X-Content-Type-Options` of its own) in front of the book's container and runs gates (a) to (c) through it, so gate (c) fails on a header that arrives twice; `tools/servertest.py` fails on a `proxy_pass` with a path |

Two tests belong to no row (`critique/rulings-6.md`, R22 and R26). `tools/servertest.py` reads `deploy/Dockerfile`
and `deploy/Dockerfile.build`, and fails when a `COPY` of the final stage brings anything but the built site and
nginx's files. CI's `serve-test` searches the image it builds, that of `deploy/Dockerfile`, for a folder named
`node_modules`.

### `deploy/README.md`

It tells the owner, in this order (`critique/rulings-6.md`, R23 and R24):

1. What a release holds, and `sha256sum -c SHA256SUMS`. In a private repository the owner fetches the release with
   their own login (R25).
2. **Copied files into the host's nginx**, the recommended way for `https://pdm.pw`, which already serves a static
   site with nginx: no other program runs. It says where each file goes: `nginx-http.conf` into the http context
   (for example `/etc/nginx/conf.d/strata-engine-docs-http.conf`); `nginx.conf` to
   `/etc/nginx/snippets/strata-engine-docs.conf`, included in the server block; the release's `nginx-csp.conf` and
   `nginx-redirects.conf` to `/etc/nginx/snippets/strata-engine-docs-csp.conf` and `…-redirects.conf`. It shows the
   lines for the host's `http` context and for its server block as complete text to paste. Headers of the host that
   must also reach the book's pages go into
   `/etc/nginx/snippets/strata-engine-docs-host-headers.conf`, because the book's `location` drops the server block's
   `add_header` lines; the book sends no `Strict-Transport-Security`, which is the host's decision. Before the
   first `nginx -t`, `nginx -V` must list `--with-http_gzip_static_module`: without it `gzip_static` is an unknown
   directive, and the README says to remove that one line (nginx then compresses while it serves, and the `.gz`
   files lie unused). Then `nginx -t`;
   reload; then `deploy/deploy-files.sh /tmp/book-new/strata-engine-docs /srv/www/strata-engine-docs`. Tested with
   nginx 1.20.1 and 1.30.6; a current nginx is the safer host (1.30.6 fixes CVE-2026-15176, which concerns `alias`
   after `rewrite`), and the book does not wait for an upgrade.
3. **The container behind the host's nginx**, for an owner who prefers to keep the book's server apart: unpack both
   tarballs into one empty folder, `docker build -f deploy/Dockerfile -t strata-engine-docs:<tag> .`, run it
   read-only on `127.0.0.1:8080`, and paste `deploy/nginx-proxy.conf` into the host's server block. The host's nginx
   then only forwards, which 1.20.1 does. The README explains how the pasted lines keep the host's own headers
   from doubling the container's. `deploy/Dockerfile.build` builds on the server instead.
4. **robots.txt**: the line `Sitemap: https://pdm.pw/strata-engine-docs/sitemap-index.xml` goes into the host's own
   `robots.txt`. A Hugo site serves `static/robots.txt` as it is, or, when its configuration sets `enableRobotsTXT`,
   renders the template `layouts/robots.txt`; the line goes into the one the site uses.
5. **Accepting a deployment**: `python tools/crawl.py --url https://pdm.pw/strata-engine-docs/` and
   `python tools/servertest.py --url https://pdm.pw/strata-engine-docs/`, which only read, both pass.
6. **Moving the book**: change `site.json`, tag a release, deploy it at the new place, and let the old host answer
   every path under the old prefix with a 301 to the same path at the new address; the README gives the nginx lines.
   Canonical links and the sitemap follow from the rebuild. What a reader's browser kept for the old origin (theme,
   track) is lost. A build for another place that does not move the book (a copy elsewhere, a test) takes
   `DOCS_BASE` and `DOCS_SITE`, then `python tools/release.py assemble --tag <tag> --base <base>`.
7. **Reading offline**: unpack the site tarball, run `python -m http.server 8000` in the folder that holds
   `strata-engine-docs/`, and open `http://localhost:8000/strata-engine-docs/`. Search works and nothing reaches the
   network. Opening the files directly (`file://`) does not work: every URL starts with the prefix, and Pagefind
   fetches its files.

## Versions

One version is built: the book of the engine release in `engine.pin`. The URLs are chosen so that more versions change
no URL of the current book.

**Implemented now:**

- Page ids and part slugs whose first segment is `v` followed by a digit are rejected (base path rule 8).
- `deploy/deploy-files.sh` keeps `/v[0-9]*/` and `/versions.json` in its second pass.
- A build with `DOCS_ROOT` or `DOCS_ARCHIVED` set fails.

**Designed, built when the second release exists:**

- The current book stays at the base of `site.json`, `/strata-engine-docs`, and `DOCS_ROOT` names the same path.
- An older book is rebuilt from its tag with `DOCS_BASE=/strata-engine-docs/v<major>.<minor>` (for example
  `/strata-engine-docs/v0.8`), `DOCS_ROOT=/strata-engine-docs` and `DOCS_ARCHIVED=1`. Copying the old files does not
  work: every URL of a build holds its base, and the old book's hashed files are gone after the next deploy.
- Archived mode: a banner on every page naming the current book; `<meta name="robots" content="noindex">`; the
  canonical link points at the same page id in the current book when it exists, else at the current book's landing
  page; no sitemap; the version menu reads `DOCS_ROOT/versions.json`, an absolute path, never one relative to the page.
- `versions.json` at `DOCS_ROOT/versions.json` is written at deploy time, by no build:
  `[{ "version": "0.9", "path": "/strata-engine-docs/", "current": true }, { "version": "0.8", "path": "/strata-engine-docs/v0.8/" }]`.
- The current build's crawl treats `DOCS_ROOT/v[0-9]*/` as outside its own build.
- The book's `localStorage` keys become `strata-book:<DOCS_ROOT>:<key>`: versions share the reader's track and tab
  choices, other books on the host do not. Starlight's own `starlight-theme` key stays shared.
- Search stays per version: one Pagefind index per build.
- The book's tag of 0.8 does not contain the archived mode. Its rebuild is made from a branch `archive/v0.8` that
  starts at that tag and receives the commits that add the archived mode; that branch is built.

## CI

GitHub Actions in the docs repository: `.github/workflows/book.yml` and `.github/workflows/links.yml`. Every action is
pinned by its full commit SHA. The default permission is `contents: read`; only the `report` and `release` jobs have
`contents: write`. No repository variable and no secret is needed beyond the workflow's own token: a tagged build is a
release build for the address of `site.json`, and `book.yml` sets no `DOCS_SITE` (`critique/rulings-6.md`, R24).

`book.yml` runs on pushes to `main` and to branches named `ci/<name>`, on pull requests, on tags `book-v*` and by
hand. One commit per page means hundreds of runs, so superseded runs are cancelled, except for tags:

```yaml
concurrency:
  group: book-${{ github.ref }}
  cancel-in-progress: ${{ !startsWith(github.ref, 'refs/tags/') }}
```

| Job | Needs | Does |
| --- | --- | --- |
| `lint` | — | sparse checkout without `src/assets/figures/`; `tools/bootstrap.py`; `npm ci`; `tools/pages.py check`; `plan/check_outline.py`; `tools/notices.py check --sections A`; `markdownlint-cli2`; `typos`; `npm test` |
| `excerpts` | — | the engine at the pin (below), in the folder `engine`; `tools/lint.py --engine engine`; `tools/notices.py check --sections BC --engine engine`; `tools/excerpts.py check`; `tools/sketches.py check` (g++ with `-std=c++20`, the standard library and glm at the engine's gitlink commit only; for Slang, the slangc of the release `CMake/StrataSlang.cmake` pins, fetched and checked by its SHA-256); `tools/reference.py render --check`; `tools/names.py check` |
| `build` | `lint` | full checkout; `astro build` at `/strata-engine-docs`, `/` and `/x/y/` (the default last), each staged and passed through gate (a) and lychee; the `/x/y/` prefix check; `npm run diagrams -- --check`; `tools/figures.py validate`; `tools/notices.py check --sections A --dist <built site>`, after the build, for what the built site holds; `tools/budgets.py`; `tools/release.py assemble`; uploads `release/<tag>/` as a workflow artifact. On a `book-v*` tag the default build is a release build (`DOCS_RELEASE=1`) for the address of `site.json` |
| `serve-test` | `build` | Docker on `ubuntu-latest`: builds `deploy/Dockerfile` from the artifact; runs it (nginx 1.30.6), the hostile-regex variant and the proxy (whose server block sends two headers of its own); runs the official `nginx:1.20.1` image with the release's files copied in the way `deploy/README.md` says, inside a server block that also serves another site at the root; gates (a) (`tools/crawl.py --url`), (b) and (c) through each, (c) without and with a host-headers file; a search of the built image for a `node_modules` folder; the search tests; axe on every page in both themes; the keyboard tests; Lighthouse; the two-pass copy test |
| `release` | `excerpts`, `serve-test`; tags only | `gh release create <tag> --verify-tag` with the site tarball, the deploy tarball and `SHA256SUMS` |
| `report` | every other job; runs whatever they did, not on pull requests | commits one file, `runs/<commit>-<attempt>.json`, to the branch `ci-results`: every job's conclusion and every `::error` annotation |

**Reading CI's result.** CI's result is read through git, whether the repository is private or public
(`critique/rulings-6.md`, R25): `tools/cistatus.py <commit>` fetches the branch `ci-results` and prints the result
that `report` committed. This needs no token on the authoring machine and has no hourly limit; the git credential is
used for git and for nothing else. The repository is public for now, and the owner has allowed pushing (R27). If
it becomes private, Actions and artifact storage count against the account's quota: the build's artifact is then kept one day, the
integrator pushes batches to `ci/<name>` and not single pages, and the planner sizes the jobs before wave 1.

`links.yml` runs weekly (Mondays 06:00 UTC) and by hand. lychee checks the external links of
`src/content/docs/**/*.md` online and only reports, in the job summary, because other sites fail now and then. The
repository's size (`gh api "repos/$GITHUB_REPOSITORY" --jq .size`) fails the job above 1 GB. Links to the
engine are checked by `tools/excerpts.py check` with `git cat-file -e`, never over HTTP.

**The engine at the pin.** The whole tree at `822a7a46` is 134.7 MiB (141.2 MB), of which `Samples/` is 107.3 MiB,
most of it pictures, models and scenes; the tree outside `Samples/` is 27.4 MiB. The tools read it through one
`git cat-file --batch` process (pipelines.md). The engine's repository is public, so CI fetches it without a login,
from `engine.pin`'s `repository` line (R25):

```sh
pin=$(awk '$1 == "commit" { print $2 }' engine.pin)
repository=$(awk '$1 == "repository" { print $2 }' engine.pin)
git init -q engine
git -C engine remote add origin "$repository"
git -C engine sparse-checkout set --no-cone '/Strata*/' '/Tools/' '/CMake/' '/Docs/' '/.claude/' '/*.md' \
  '/.editorconfig' '/Samples/*/Scripts/' '/Samples/*/*.md'
git -C engine fetch --depth 1 --filter=blob:none origin "$pin"
git -C engine checkout -q FETCH_HEAD
```

`/Strata*/` covers `Strata`, `StrataEditor`, `StrataRuntime`, `StrataScriptCore`, `StrataCLI` and `StrataTests`;
`/*.md` covers `AGENTS.md` and `ThirdPartyNotices.md`, which the lint and the vendor rule of pipelines.md §3.2 read;
the samples' scripts and READMEs are quoted by pages of `make`. Any other blob a tool reads (a sample's scene for
`figures.py check`, a file of the tree's root) is not in the checkout: the clone is partial (`--filter=blob:none`), so
`git cat-file --batch` fetches each such blob from the remote when it first reads it. A vendor library that a page
quotes, and glm for the sketches, are fetched the same way at their gitlink commits
(`git -C engine ls-tree "$pin" Strata/vendor/<lib>`).

**Caches** (each restored by prefix when the exact key misses, so a cold build happens only after a cache was evicted,
and must then pass budget row 3):

| Cache | Path | Key |
| --- | --- | --- |
| Toolchain | `.tools/` without `ms-playwright` | `tools-<hash of tools/toolchain.json>` |
| npm | `.tools/npm-cache` (spike) | `npm-<hash of package-lock.json>` |
| Astro | `.cache/astro` | `astro-<hash of package-lock.json, astro.config.mjs, ec.config.mjs, src/plugins/**, src/lib/**>` |
| Derived pictures | `.cache/images` | `images-<hash of src/assets/figures/**, src/lib/images.mjs>` |
| Playwright's browsers | `.tools/ms-playwright` (spike) | `playwright-1.65.0-<runner OS>`; system libraries are installed on every run |
| The engine | `engine/.git` | `engine-<pin commit>` |

Every step sources `.tools/env.sh` (spike). Checkout depth is 1 (`lastUpdated` is off). Case checks run here, on Linux.

## The authoring machine

The authoring machine has no administrator rights, no Docker and no WSL. Its drive `G:` is exFAT: case-insensitive, no
symbolic links, 256 KB clusters (`node_modules`: 321 MB apparent, 6.2 GB on disk, 24,353 files). Therefore:

- Budgets use apparent sizes.
- Only the integrator runs `npm ci` and builds; writers and reviewers never install `node_modules` in their own folders.
- Case is checked on Linux, in CI; a local crawl cannot see a wrong case.
- The toolchain, npm's cache, Playwright's browsers and temporary files live in the clone's `.tools/` (spike).
- The nginx configuration runs locally through `tools/servertest.py` with the Windows builds of nginx 1.30.6 and
  1.20.1 in `.tools/` (spike), which `tools/bootstrap.py --servers` fetches, each by its SHA-256
  (`critique/rulings-6.md`, R23); the container runs only in CI.
- Until CI can run, budget rows 8, 15 and 16 are measured here, with both nginx versions, and again on
  `ubuntu-latest` after the first push; rows 2, 3 and 14 stay open (R25).
- Measurements run under the engine's `Tools/PerfLock.py`, so they never overlap another measurement (spike).

## Where this file overrides the research

`research/framework.md` §5 is a complete configuration written before the plan; it is background only. Where it or
`research/captures.md` says otherwise, this file and `pipelines.md` decide.

| Topic | Research | This plan |
| --- | --- | --- |
| Environment variables | `BOOK_BASE`, `BOOK_SITE` | `site.json` holds the base and the origin (`critique/rulings-6.md`, R24); `DOCS_BASE`, `DOCS_SITE` override them for one build; `DOCS_RELEASE` (spike); `DOCS_ROOT`, `DOCS_ARCHIVED` reserved |
| Content tree and URLs | `engine/<part>/<chapter>/index.md`, `games/…` | `src/content/docs/<part>/<chapter>.md` at `<base>/<part>/<chapter>/` |
| Links between pages | root-relative without the base; `errorOnRelativeLinks: true` | relative paths to `.md` files; absolute links fail the build |
| Pictures kept | lossless PNG originals in an LFS submodule `media/` | published AVIF and lossless WebP in this repository; PNG originals in an archive attached to each release; no LFS |
| Derived pictures | AVIF at 960, 1920 and 3840 plus one WebP at 1920 | one format per picture; lossy ones served at their own width plus a 960 AVIF (and 1920 from a 3840 capture); lossless ones not derived |
| Crops | enlarged 4 times by nearest neighbour in the file (`captures.md`) | published at capture size, enlarged in CSS at whole factors |
| Versions | every version in `/<root>/v<release>/`, a `latest/` alias, a root redirect | the current book at the base; older books rebuilt at `<base>/v<major>.<minor>/` (designed, not built) |
| Front matter | `track`, `requires`, `engineVersion`, `status: draft\|review\|done` | `style.md` §6.1: `id`, `title`, `description`, `kind`, `size`, `tracks` (letters), `needs`, `time`, `learn`, `since`, `status: draft\|reviewed\|final` |
| Deploy folder and server | `docker/`, a Dockerfile that serves with Caddy; nginx as the alternative | `deploy/`; nginx is the one server, as copied files in the host's nginx (recommended) or as an nginx container that serves a built site behind it; no Caddyfile (`critique/rulings-6.md`, R23) |
| Compression | Caddy's `encode zstd gzip`, at request time | gzip only: a `.gz` beside every text file of 1 KB or more (`gzip_static`) and no `.br`, because no stock nginx serves brotli; budget rows 10 and 11 in gzip (R23) |
| nginx versions | `nginx:1.30-alpine` (1.30.6) | 1.20.1 (what the owner's host runs) and 1.30.6 (the container), both tested (R23) |
| Tools folder | `%LOCALAPPDATA%\StrataDocsTools` | `.tools/` in the clone, ignored (spike) |
| Glossary file | `src/content/glossary/terms.yaml` | `src/content/glossary.json` (spike) |
| Glossary links | `:term[…]` | `:term[text]{id=…}`, with a popover |
| Engine pin | `book.config.json` and an `engine/` submodule | `engine.pin` (spike's `key value` lines, the full commit) and `--engine <clone>` |
| Sidebar | `starlight-sidebar-topics`, one per track | one sidebar of the parts; tracks change only previous and next |
| Site title | "Strata Engine Docs" | "The Strata Engine Book" |
| KaTeX errors | `throwOnError: true` | ignored by `rehype-katex` 7.0.1; a rehype step fails the build |
| Mermaid | rendered in every build by a browser | prerendered by `npm run diagrams` and committed |
| Picture zoom | `starlight-image-zoom` | the picture links its published file (spike) |
| Print | `print/[track].astro` | `print/[part].astro` (spike) |
| Budgets | warm build ≤ 5 min, ≤ 6 GB, page ≤ 250 KB gzip, Lighthouse 95/100 | the table of [Budgets and the spike](#budgets-and-the-spike) |
| Spike content | 300 pages of 1,800 words, 1,000 4K PNGs | the outline at its sizes; pictures from the samples' screenshots |
| Links tool | `starlight-links-validator` in the build | our links plugin (spike); lychee and `tools/crawl.py` after the build |

## The spike against this file

What the spike in this clone (2026-11-10) must change to meet this file. Each item is a ruling, not a name.

1. Pictures: one format per picture (AVIF lossy, WebP lossless) instead of AVIF and WebP at 960, 1920 and 3840; the
   published file served unchanged and one 960 AVIF derived; AVIF quality 80 (the spike uses 60); `.avif` accepted and
   `.png` refused as published files; crops published at capture size (`tools/figures.py` now expects rectangle times
   scale) and enlarged in CSS; named crops (`-<crop>`) and the stamps in `taken.json` (pipelines.md §5.7);
   `scripts/encode-figures.mjs` (written by the tool builder) and the ignored `originals/` folder.
2. Diagrams: committed to `src/generated/diagrams/` by `npm run diagrams` instead of drawn into `.cache/diagrams/` by
   every build; `htmlLabels: false` (the spike uses `true`); ids prefixed per theme; the checks.
3. Glossary: explicit `:term` with a popover instead of automatic linking with a `title` tooltip; `::glossary` as one
   `<dl>` with `data-pagefind-title`; `tableOfContents: false`.
4. Front matter: `style.md` §6.1's keys (`id`, `size`, `needs` for `prerequisites`, tracks as letters with B added,
   `tracks: []`, `learn` as `{id, text}`, `since`, `time`; no `level`, no `engine`); `kind: primer`; `a|b` and at most
   five Needs; rules O1, O4, O5, O7, O8; `:::answer{tests=…}`; the level computed from the Needs closure.
5. Parts: 25 in the order of `book.md` (the spike has 23, with `assets` before `gpu` and `indirect` before `image`);
   the track sequences as explicit page ids equal to `plan/tracks.md` (the spike's `beginner` sequence names removed
   pages such as `basics/cpp`, `make/cpp-for-scripts`, `basics/math-light`, `basics/reading-code`).
6. Directives to write: `simplified`, `analogy`, `example`, `derivation`, `test-out`, `steps`, `files`, `checkpoint`,
   `include`, `term`, `since`; the generated parts of the part pages.
7. Deployment: `deploy/Dockerfile` serves a built site (the spike's two-stage file becomes `deploy/Dockerfile.build`
   without Playwright); image `nginxinc/nginx-unprivileged:1.30.6-alpine`; `deploy/nginx.conf` with `^~`, no nested
   `add_header`, the security headers, the CSP include, `gzip_static`, Cache-Control by name (the spike caches
   `wasm.en.pagefind` for a year and `pagefind-entry.json` for an hour); `deploy/nginx-http.conf`,
   `deploy/nginx-proxy.conf`, `deploy/deploy-files.sh`, `deploy/README.md`; `.dockerignore` and
   `tools/servertest.py` for the new files.
8. `tools/release.py`, `scripts/precompress.mjs`, the CSP, `src/redirects.json`, the release guard on the origin, the
   refusal of `DOCS_ROOT` and `DOCS_ARCHIVED`, `@astrojs/sitemap` as a direct dependency with a filter.
9. Checks: lychee in `tools/toolchain.json`; `tools/crawl.py`'s new failures (external hosts, engine commits, case,
   unreferenced files with `.gz`, canonical, `robots.txt`, `katex-error`, links to the book's repository, an HTML file
   without the footer line, a font's `data:` URL in a style sheet); `scripts/runtime.mjs`; `tools/servertest.py --url`;
   `scripts/a11y.mjs` on every page; `scripts/keyboard.mjs`; `scripts/lighthouse.mjs`; `scripts/search-quality.mjs`;
   `tools/budgets.py`; the lint rule ids of `style.md`, `inline-env` and `front-matter-head`.
10. Search: the combined `title` meta, filters for part and track, the weights, `data-pagefind-ignore` on the top strip
    and `.katex-html`.
11. Print views: `noindex`, out of the sitemap, every `details` open, pictures loaded eagerly.
12. Badges: accessible names as visually hidden text, not `title`.
13. The scale test (`scripts/scale.mjs`): the outline's rows at their sizes instead of 300 pages of 2,000 to 8,000
    words; pictures from the samples' twelve screenshots instead of synthesized ones; the reference at real sizes; the
    part pages and a print view per part.
14. CI: `.github/workflows/book.yml` and `links.yml` as above.
15. Copyright and notices (`critique/rulings-6.md`, R20 to R22): `LICENSE` and `<base>/license.txt`; the `Footer`
    override with the copyright line and its two links on every page, print view, fallback page and the 404 page;
    `"license": "UNLICENSED"` in `package.json`; `editUrl` refused by `tools/pages.py` as by the schema;
    `public/third-party-notices.txt`, `tools/notices.py` (`write` and `check`) and `tools/data/notices.json`; no font
    inlined (`vite.build.assetsInlineLimit`).
16. One server (R23): no Caddy in `deploy/`, `tools/toolchain.json`, `tools/bootstrap.py`, `tools/servertest.py`,
    `book.yml`, either README or any other file of the tree; gzip only (`scripts/precompress.mjs` writes no `.br`);
    nginx 1.20.1 beside 1.30.6 in `tools/toolchain.json`, `tools/bootstrap.py --servers`, `tools/servertest.py` and
    `book.yml`; in `deploy/nginx.conf`, the first line naming both versions (the spike's says 1.24 or later), the
    table of types, `always` on every `add_header` and the host-headers include; `tools/servertest.py`'s run with a
    host-headers file and its reading of the two Dockerfiles' final stages (no `node_modules`).
17. The address (R24): `site.json`, read by `src/lib/settings.mjs` and `tools/booklib/settings.py`, with
    `tools/tests/fixtures/settings-cases.json`; no default origin in `src/lib/settings.mjs`, `tools/crawl.py`,
    `deploy/Dockerfile` or `book.yml`; the release guard as above; `tools/lint.py`'s rule `literal-origin`;
    `deploy/README.md` as above; the two faults that stand in the way of accepting a deployment, fixed first:
    `tools/servertest.py --url` builds `https:/` as the origin of an `https` URL, and `tools/crawl.py --url` fails when
    the host's root answers 200.
18. The repository and CI (R25): the `report` job, the branch `ci-results` and `tools/cistatus.py`; the engine fetched
    from `engine.pin`'s `repository` line; lab scripts with their files (`downloads/labs/<name>.zip`), worked solutions
    (`downloads/solutions/…`) and tutorial patches (`downloads/tutorials/…/<chapter>.patch`) published under
    `<base>/downloads/`, and the header of a `book:` quote linking its download, never the repository.
19. What R26 adds: `downloads` as a reserved first segment in `tools/pages.py` and the build; the `error_page`
    line kept as the spike has it; no header twice through the proxy, with a proxy server block that sends two
    headers of its own; the README's lines on `gzip_static` and on the proxy's headers; `tools/lint.py --engine`
    and `tools/notices.py check --sections` in the jobs of the CI table; `gh api "repos/$GITHUB_REPOSITORY"` in
    `links.yml`; the vendor quote's header read from the tool builder's file.
