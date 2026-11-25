# Rulings 6: closed source, nginx, and `https://pdm.pw`

On 2026-11-10 the owner answered the two open questions of `plan/README.md`:

> It is going to be closed source, and it will be served by nginx. For now it will be served in https://pdm.pw

Three readers then went through the plan (97 places), the tree (56 places) and the sources on the web (licenses of
what the site ships, GitHub's rules, and what `https://pdm.pw` answers today). This file rules on what they found.

Where this file differs from an earlier ruling or from `site.md`, `style.md`, `pipelines.md`, `process.md`, `book.md`
or `README.md` as committed before it, this file wins; those files are changed with it. Earlier rulings stay as
records.

## R20 — The book is closed source: all rights reserved

The book is the owner's work and no open license covers it. That holds for its text, pictures, diagrams, sketches,
tutorial files, labs, downloads and the site's own code and tools.

- **One statement, in one place.** The holder's name and the year of first publication are two values of `site.json`
  (R24): `copyright.holder` and `copyright.year`. Until the owner names another holder it is `2042Third`, the name on
  the repository; the year is 2026. The statement reads "Copyright © 2026 2042Third. All rights reserved.", followed
  by "Except where otherwise noted" and the two exceptions: what a reader may do with the book's code (R21), and
  third-party material (R22).
- **Where it stands:**

  | Place | What it holds | Checked by |
  | --- | --- | --- |
  | `LICENSE` at the repository's root | the full statement, R21's permission, a pointer to the notices | `tools/pages.py check`: its first line equals the one built from `site.json` |
  | `<base>/license.txt` | the same text, served | the build writes it from `LICENSE`; gate (a) finds it |
  | the footer of every page and every print view | "© 2026 2042Third. All rights reserved.", a link "License" to `<base>/license.txt` and a link "Third-party notices" to `<base>/third-party-notices.txt` | gate (a): every HTML file holds the line and both links |
  | `README.md` of the repository | one paragraph: closed source, all rights reserved, no contributions asked for | read by the verifier |
  | `package.json` | `"private": true` and `"license": "UNLICENSED"` | `tools/pages.py check` |
  | `appendix/credits` | the statement, R21's permission in the reader's words, the credits (R22) | the page's brief |

  The footer is a Starlight `Footer` override, so a printed page carries the line too.
- **No way into the book's repository.** The site has no "edit this page" link, no link to the repository's files,
  issues or releases, and no badge. `editUrl` stays a refused key. Gate (a) fails on any link to the book's repository
  in a built page. The tree already links nowhere there (commit `563af6d`); this makes it a rule.
- **No invitation to reuse or to contribute.** No page and no file of the repository asks for pull requests,
  translations or copies. `book.md`'s fourth reader is a contributor to the engine, not to the book.
- **No text for agents.** The site still publishes no `llms.txt`. The old reason ("the Markdown sources are public")
  is gone; the reason is now that the book is written for people and is not offered as a corpus. An agent that works
  on the engine has the engine's own guide and skills.
- **Word lists and other data** committed into the repository must be public domain or permissively licensed, so that
  they put no terms on the book (`style.md`'s common-word list is: 12dicts, public domain).

## R21 — What a reader may do with the book's code

The book teaches by having the reader build things, and `book.md` says the reader owns the game they export. A strict
"all rights reserved" over the examples would contradict that. So the statement carries one permission. It is a
permission, not an open license, and the owner may change its wording before the first release.

> **Using the code in this book.** You may use the code and the project files this book gives you (the listings
> written for the book, the tutorial files, the command scripts, the lab files, the worked solutions and the
> checkpoint projects) in your own programs and games, and ship them, also commercially, without asking and without
> naming the book. You may not publish them as a collection of examples, a course or a book of your own. Everything
> else (the text, the pictures, the diagrams and this site) is for you to read, and to print for your own use.

- **Excerpts of the engine are the engine's.** A quote of the engine's source belongs to the engine and its terms
  apply; the book grants nothing over it. The engine's repository has no license file today: what its users may do
  with the engine is a question for the owner (below), and `start/install` and `appendix/credits` say only what the
  engine's repository says at the pin.
- **Third-party files keep their own terms** (R22). A checkpoint or lab download that holds a CC BY file holds its
  `CREDITS.md`.
- **Homes.** `appendix/credits` teaches the permission; `start/how-to-read` names it in one sentence with a link. The
  settlement of the allocation gives both pages the item.

## R22 — Third-party material and its notices

The site ships other people's files (fonts, scripts, WebAssembly), quotes other people's code (the engine's vendored
libraries) and shows and redistributes other people's assets (the samples' models and textures). Each keeps its
notice.

- **One served file: `<base>/third-party-notices.txt`.** `tools/notices.py write` generates it into
  `public/third-party-notices.txt`, which is committed, so a change of a dependency shows in a diff. It has three
  sections:

  | Section | Holds | Read from |
  | --- | --- | --- |
  | A. What this site ships | every component whose files or code are in `dist/`: the three font families, KaTeX and its fonts, Starlight (with its Night Owl theme), Astro's and Vite's runtime parts, Expressive Code, Pagefind and its default UI with the WebAssembly's crates, and whatever else a build puts into `dist/` | the list `tools/data/notices.json`, kept by hand: per component its package, license id and copyright lines; the license's text from `node_modules` |
  | B. What this book quotes | every vendored library a page quotes with `vendor:<lib>`, and every project a page's code is derived from | the engine's `ThirdPartyNotices.md` and the library's license file, at the pin |
  | C. What this book shows and gives out | every third-party asset in a picture, a lab or a download | the samples' `CREDITS.md` at the pin, and `labs/` and `tutorials/` credits |

  Each license's text appears once; each component names its copyright holders exactly as its own notice does
  (Source Serif 4 is Adobe's).
- **`tools/notices.py check`** runs in CI's `lint` job and fails when the committed file is stale; when a component of
  the list has another version in `package-lock.json` than the list records (so an upgrade is read by a person); when
  a license is outside the allowlist (`MIT`, `MIT-0`, `ISC`, `0BSD`, `BSD-2-Clause`, `BSD-3-Clause`, `Apache-2.0`,
  `OFL-1.1`, `CC0-1.0`, `BlueOak-1.0.0`, `Unicode-3.0`, `Zlib`); and, after a build, when `dist/` holds a font
  family, a script package or a WebAssembly file that no component of the list claims.
- **Fonts are served as their packages ship them.** The build never subsets, converts or renames a font file: the
  Open Font License lets a changed font keep neither its name nor, without the notice, its license.
- **Packages that only build or test** (axe-core, sharp's libvips, lightningcss, Playwright and the like) are never
  shipped: the final stage of `deploy/Dockerfile` and of `deploy/Dockerfile.build` holds the built site and nginx's
  files, and no `node_modules`. `tools/servertest.py` fails when the image holds one.
- **CC BY assets are credited where they are seen.** A figure that shows a CC BY file names its author and license in
  its caption, and `appendix/credits` holds the full entry. At the pin there is one such file, the fox of the Open
  World sample, from the Khronos glTF sample assets at commit `edc7c9e67c639d230715049ee31f9a96a6babbbe`. Its entry
  is copied from the license file beside the model at that commit, with its two copyright lines ("© 2014,
  tomkranis." and "© 2017, @AsoboStudio and @scurest.") and the link to that commit. The engine's own credit line
  leaves the two copyright lines out; that is an erratum of the engine (`process.md`'s table), and the book states
  the full credit.
- **A quote of a vendored library** names, in its header, the library, the path, the version the pin records and the
  license's id. The library's notice is in section B; `appendix/credits` lists the libraries with their licenses and
  links the file. The page stays of size S: it holds no license text itself.
- **Reserved names at the base** gain `license.txt` and `third-party-notices.txt`.

## R23 — nginx is the one server

Caddy leaves the plan and the tree: `deploy/Caddyfile`, the generated `csp.caddy` and `redirects.caddy`, Caddy's pin
in `tools/toolchain.json`, its download in `tools/bootstrap.py`, its runs in `tools/servertest.py` and `book.yml`, its
item in `deploy/README.md`, and every Caddy clause of `site.md`'s requirements and gates. Requirement 10 keeps only
"`proxy_pass` without a URI part".

- **Compression is gzip.** No stock nginx, and no official nginx image, serves brotli. The release holds a `.gz`
  beside every text file of 1 KB or more and no `.br`; `scripts/precompress.mjs` writes none, and gate (a) no longer
  exempts them. Rows 10 and 11 of the budget table are measured in gzip, which is what a reader's browser receives,
  with their pass marks unchanged: largest page ≤ 300 KB, median page ≤ 60 KB, scripts per page ≤ 40 KB. The first
  spike measured 121.7 KB and 44 KB in gzip. An owner whose nginx has the brotli module may turn it on; the book
  neither needs nor tests it.
- **Gate (c)** asks for 301 (not 308), for `Content-Encoding: gzip` on pages, and, in the container, for a 404 that
  is not the book's page on a path outside the prefix. Against a host that serves other things (`--url`), a path
  outside the prefix must only not be the book's 404 page.
- **Two versions of nginx are tested**, with the same gates (a) to (c):

  | Version | Why | Where it runs |
  | --- | --- | --- |
  | 1.30.6 | the container's image (`nginxinc/nginx-unprivileged:1.30.6-alpine`), and the version the plan pinned | CI: the container, the hostile-regex variant, the proxy. The authoring machine: `nginx-1.30.6.zip` |
  | 1.20.1 | what `https://pdm.pw` answers with on 2026-11-10 | CI: the official `nginx:1.20.1` image with the release's files copied in the way `deploy/README.md` says, inside a server block that also serves another site at the root. The authoring machine: `nginx-1.20.1.zip` |

  Requirement 8 becomes: "tested with nginx 1.20.1 and 1.30.6; `root`, never `alias`". `deploy/nginx.conf`'s first
  line and `deploy/README.md` name both versions. The README still tells the owner that a current nginx is the safer
  host; it does not make the book wait for an upgrade.
- **The book's files do not lean on the host's `mime.types`.** 1.20.1's file knows no `avif`. The book's `location`
  sets the types of what it serves and the host's file may lack: `image/avif`, `image/webp`, `font/woff2`,
  `application/manifest+json`, `application/wasm`. Gate (c) already checks each but the last (R26, point 1).
- **The book's responses carry the book's headers, and only those.** A `location` with an `add_header` drops every
  `add_header` of the server block around it (nginx before 1.29.3 has no switch for this). So:
  - every `add_header` of the book carries `always`, so that its 404 page has the headers too;
  - the book sends no `Strict-Transport-Security`: that header binds the whole host and is the host's decision;
  - `deploy/nginx.conf` ends its header lines with an `include` whose name holds a wildcard
    (`/etc/nginx/snippets/strata-engine-docs-host-headers*.conf`), which may match no file. An owner whose host sets
    headers that must also reach the book's pages puts them there. `tools/servertest.py` runs with and without such
    a file.
- **No font is inlined.** The policy keeps `font-src 'self'`. Vite inlines small files as `data:` URLs, and two font
  files were small enough (a KaTeX size font and one subset of JetBrains Mono); a page that needed them would have
  broken the policy. The build's settings inline no font, and gate (a) fails on a `data:` URL of a font in a built
  style sheet.
- **Two ways to deploy, both tested; `deploy/README.md` gives them in this order:**
  1. *Copied files into the host's nginx.* The recommended way for `https://pdm.pw`, which already serves a static
     site with nginx: no other program runs. The README shows the lines for the host's `http` context and server
     block as complete text to paste.
  2. *The container behind the host's nginx* (`deploy/nginx-proxy.conf`), for an owner who prefers to keep the book's
     server apart. The host's nginx then only forwards, which 1.20.1 does.
- `tools/bootstrap.py --servers` fetches the two nginx builds for Windows, each by its SHA-256.

## R24 — The address is `https://pdm.pw/strata-engine-docs/`, written in one file

The owner said "for now", so the address must stay one setting. Today its default stands in three files
(`src/lib/settings.mjs`, `tools/crawl.py`, `book.yml`), and the release value was to be a fourth place, a repository
variable.

- **`site.json`** at the repository's root holds the deployment's values:

  ```json
  {
    "base": "/strata-engine-docs",
    "origin": "https://pdm.pw",
    "copyright": { "holder": "2042Third", "year": 2026 }
  }
  ```

  `src/lib/settings.mjs` reads it for the build and `tools/booklib/settings.py` reads it for the tools; both apply
  `site.md`'s rules for a base and an origin, and one table of cases (`tools/tests/fixtures/settings-cases.json`)
  tests both. `DOCS_BASE` and `DOCS_SITE` still override the two values for one build (the three bases of row 17,
  a test server, a preview).
- **No other file holds the origin.** `tools/lint.py` fails on the literal origin outside `site.json`,
  `deploy/README.md`, the repository's `README.md` and `plan/`. `book.yml` sets no `DOCS_SITE`, and the repository
  variable is not used: a tagged build is a release build for the committed address.
- **The release guard** (`DOCS_RELEASE=1`) fails when the origin is not `https`, names `localhost`, `127.0.0.1` or
  `example.com`, or carries a path. `example.com` stays the origin that tests pass explicitly.
- **The deploy files are written for the default base.** `tools/release.py assemble --base` rewrites them for another
  one, as before; a test fails when `site.json`'s base and the prefix in `deploy/` differ.
- **The host, as seen from outside on 2026-11-10** (plain requests, no login): nginx 1.20.1 over HTTP/1.1; a Hugo
  site at the root, whose 404 page answers `/strata-engine-docs/` today; its own `robots.txt` with its own `Sitemap`
  line; `X-Frame-Options` and `X-Content-Type-Options` without `always`; no `Strict-Transport-Security` and no
  `Content-Security-Policy`.
- **`deploy/README.md` gives the owner** the line for the host's `robots.txt`,
  `Sitemap: https://pdm.pw/strata-engine-docs/sitemap-index.xml`, and says where a Hugo site keeps that file.
- **A deployment is accepted by the gates against the live address:**
  `python tools/crawl.py --url https://pdm.pw/strata-engine-docs/` and
  `python tools/servertest.py --url https://pdm.pw/strata-engine-docs/`, which only read. Two faults stand in the way
  and are fixed first: `servertest.py` builds `https:/` as the origin of an `https` URL, and the crawl fails when the
  host's root answers 200, which a host with a site of its own always does.
- **Moving.** When the book leaves this address: change `site.json`, tag a release, deploy it at the new place, and
  let the old host answer every path under the old prefix with a 301 to the same path at the new address (the README
  gives the nginx lines). Canonical links and the sitemap follow from the rebuild. What a reader's browser kept for
  the old origin (theme, track) is lost; that is accepted.
- CI still deploys nowhere.

## R25 — The repository, and how CI is read

The GitHub repository is public today and holds only the owner's first commit. A public repository without a license
is still readable, and forkable on GitHub, by anyone. Whether "closed source" means that the sources are private is
the owner's decision, and a push cannot be taken back.

- **Nothing is pushed until the owner has said which.** R16's first push of `ci/site` waits for that answer. The
  planner recommends a private repository. (The owner has answered: R27.)
- **CI's result is read through git, in either case.** A last job of `book.yml`, `report`, runs whatever the others
  did (not on pull requests) and commits one file, `runs/<commit>-<attempt>.json`, to the branch `ci-results`: every
  job's conclusion and every `::error` annotation. It is the only job besides `release` with `contents: write`.
  `tools/cistatus.py <commit>` fetches that branch and prints the result. This needs no token on the authoring
  machine, has no hourly limit, and works for a private repository as for a public one. The git credential is used
  for git and for nothing else. This replaces R16's "from GitHub's public API"; the rest of R16 holds.
- **Until CI can run:** rows 8, 15 and 16 are measured on the authoring machine (Windows, both nginx versions) and
  again on `ubuntu-latest` after the first push; rows 2, 3 and 14 stay open. By R12 none of them holds the pilot
  back.
- **If the repository becomes private,** Actions and artifact storage count against the account's quota. Then the
  build's artifact is kept one day, the integrator pushes batches to `ci/<name>` and not single pages, and the
  planner sizes the jobs before wave 1. The owner fetches a release with their own login.
- **The engine's repository stays public.** The book links to it, CI fetches it without a login, and `start/install`
  sends the reader to its releases. Every engine link is built by one helper from `engine.pin`'s `repository` line;
  the plan's lines that spell the owner and the name mean that setting.
- **Nothing a reader needs lives only in the repository.** A file the book tells a reader to run or open is either
  quoted in full on its page or published under `<base>/downloads/`: checkpoint projects and stage scripts
  (`pipelines.md` already does this), and now also lab scripts with their files (`downloads/labs/<name>.zip`),
  worked solutions (`downloads/solutions/…`) and tutorial patches (`downloads/tutorials/…/<chapter>.patch`). The
  header of a quote from `book:<path>` names the path; it links the download when there is one, and never the
  repository.

## R26 — What the revision left open

Four agents changed the plan to match R20 to R25, and two of them checked the result against this file. They and the
two builders left sixteen points for the planner. This section decides them. Points 1 to 13 change the plan with this
section; points 14 to 16 change nothing and are recorded.

1. **No `.wasm` file is served.** Pagefind's WebAssembly is `pagefind/wasm.<language>.pagefind`. Pagefind fetches it
   as bytes and compiles it itself, so its type does not matter: it takes `default_type`, as Pagefind's other files
   do. The table of types keeps `application/wasm` for a file that a later version may add. Gate (c) has no row for
   it, so R23's "Gate (c) already checks each" holds for the other four types.
2. **The lint rule on the literal origin has the id `literal-origin`** (R24), as the tool builder named it.
3. **`downloads` is a reserved first segment** (base path rule 8), beside `print`, `pagefind`, `_astro` and
   `_figures`: R25 put the labs', the tutorials' and the solutions' files under `<base>/downloads/`.
4. **The `node_modules` test is two tests** (R22). `tools/servertest.py` reads `deploy/Dockerfile` and
   `deploy/Dockerfile.build`, and fails when a `COPY` of the final stage brings anything but the built site and
   nginx's files; this test runs on every machine. CI's `serve-test` also searches the image it builds, that of
   `deploy/Dockerfile`, for a folder named `node_modules`. CI does not build `deploy/Dockerfile.build`: its final
   stage is the same text, and the first test reads it.
5. **A check runs in the job that has what it reads.** `tools/lint.py` reads the engine at the pin (its rule
   `copied-text` compares the pages with the engine's own documents), so it takes `--engine <clone>` and runs in the
   `excerpts` job, the one that fetches the engine. `tools/notices.py check` is split with `--sections`: `A` needs
   `package-lock.json` and `node_modules`, and runs in `lint`; `BC` needs `--engine`, and runs in `excerpts`;
   `--dist <built site>` runs in `build`, with `--sections A`. Without `--sections` the check covers the whole file
   and needs everything: that is the form for the authoring machine, before a commit that changes the file. A check
   of some sections compares those sections of the committed file, and the license texts they name, with what
   `write` would write. How the file is laid out so that sections can be compared apart is the tool builder's
   choice.
6. **Who builds which tool.** A tool belongs to the builder whose plan file specifies it. The tool builder builds
   the tools of pipelines.md (`excerpts.py`, `sketches.py`, `figures.py`, `tutorials.py`, `reference.py`, `names.py`,
   `lint.py`, `pin.py`, `wordlists.py`, `notices.py`), `pages.py`, `tools/data/` and `tools/schemas/`. The site
   builder builds the tools of site.md (`crawl.py`, `servertest.py`, `release.py`, `budgets.py`, `measure.py`,
   `bootstrap.py`, `deployfiles.py`, `cistatus.py`, `toolchain.json`). Each owns the modules of `tools/booklib/`
   that its tools use; a module both use (`settings.py`) is the tool builder's. `tools/data/notices.json` is written
   first by the tool builder; afterwards whoever changes `package-lock.json` changes it in the same commit, because
   `check` fails otherwise. process.md's table of files gets the rows that pipelines.md §12 has and it lacked.
7. **Tutorial assets** are written by the asset's owner page, named in the brief, and `tutorials/assets/CREDITS.md`
   by the integrator, from the `## Requests` of the notes. process.md said so already; pipelines.md §12 said "the
   writer" and now says the same.
8. **Through the proxy no header arrives twice.** The host of `https://pdm.pw` sends `X-Frame-Options` and
   `X-Content-Type-Options` from its server block. A proxy `location` without an `add_header` inherits them, and the
   container sends its own: the reader would get each twice. Gate (c) fails when a response under the prefix
   carries one of the book's four headers more than once, and CI's proxy runs inside a server block that sends
   those two headers, as the real host does. How `deploy/nginx-proxy.conf` prevents the doubling is the site
   builder's choice (one `add_header` in the proxy's `location` ends the inheritance; `proxy_hide_header` drops the
   container's); `deploy/README.md` says which and why. The copied-files way is not affected: there the book's
   `location` has `add_header` lines of its own.
9. **`gzip_static` needs its module.** In the copied-files way, `deploy/README.md` tells the owner to look for
   `--with-http_gzip_static_module` in what `nginx -V` prints, before the first `nginx -t`. Without the module,
   `gzip_static` is an unknown directive. The README then says to remove that one line: nginx compresses while it
   serves (`gzip on` is already there), and the `.gz` files lie unused. Gate (c)'s gzip row passes either way.
10. **A folder without an index answers the book's 404 page.** The spike's line is right and the plan's was short:
    `error_page 403 404 =404 /strata-engine-docs/404.html;`. Without it `_astro/` answers nginx's bare 403 page.
    Gate (c)'s row for `<base>/_astro/` becomes "404 with the book's 404 page".
11. **No `gh` on the authoring machine.** There is no login there, and the git credential is never used as a token
    (R25). `figures.py archive` writes the originals' archive and its SHA-256; the integrator moves both to
    `G:/GameEngineAI/.worktrees/docs-originals/`, outside the clone, and tells the owner, who attaches them to the
    release or keeps them with their backups. A machine that lacks an original reads it from that archive. In CI,
    where `gh` has the job's own token, the repository is `$GITHUB_REPOSITORY`, never a spelled name.
12. **Three texts say what they meant.** pipelines.md §1.1: the engine's address that its commands spell is the
    `repository` line of `engine.pin`. pipelines.md §6.2: `stages[].step` is the number of the stage, counted from 1
    in page order and equal to the `stage` of the section's `::checkpoint`; it is not the number of a list item,
    because every section's list of steps counts from 1 again. process.md: the erratum of the fox's credit reaches
    every part whose brief plans a picture of the Open World sample, not only `animation` and `appendix`.
13. **The header of a vendor quote** names the library's version and license id, and the build does not read the
    engine. `tools/excerpts.py fill` writes them into one committed JSON file, `check` fails when the file is stale,
    and the build reads it. The tool builder names the file and its form in the handover.
14. **Choices of the revision that stand:** `labs/CREDITS.md`; `figures.py labs` for the labs' downloads; a
    solution as `exercise-<n>.zip` (a project) or `exercise-<n>.patch` (the engine), and a sketch's solution in full
    on its page without a download; section C from the `CREDITS.md` of each sample that a recipe or a tutorial uses;
    the notices as pipelines.md §15, so that no section is renumbered; the longer table of types, in which a
    `.patch` takes `default_type` so that a browser saves it; the footer's line kept out of the search index
    (`data-pagefind-ignore`).
15. **Left for the allocation's settlement:** the sentence of `allocation/animation.md` that puts the fox into the
    Showcase (it is the Open World sample's), together with the row of `appendix/credits`.
16. **Checked and right as written:** `dispositions.md` names two headings of site.md, "Where the site is served: the
    settings" and "Deployment", and both exist.

## R27 — The owner's answer: public for now, and pushing is allowed

On 2026-11-10 the owner answered the first question of this file: "The repo currently is public for easy pushing for
you." The planner reads it so: the repository stays public for the present, on purpose, and may become private later.

- **R25's wait ends.** Pushing to the docs repository is allowed. The order of pushes does not change: the first is
  R16's, of the branch `ci/site`, by the CI stage; `main` moves only by fast-forward to a commit whose CI is green;
  nothing is forced.
- **What is pushed is published.** While the repository is public, anyone can read and copy every pushed commit, the
  `plan/` folder included, and a copy made then stays when the repository becomes private. So the first push waits
  for two things in the tree, both the fixer's work after the two builders: `LICENSE` and the footer's line (R20).
  Before it the planner also searches the commits it would publish for what must not be public: a token, a person's
  e-mail address in a file, a path into the user folder of the authoring machine. The search of 2026-11-10 found
  none.
- **CI runs on every pushed branch:** `book.yml` starts on `push` without a list of branches. A branch pushed only
  as a copy of the work would run CI too, so no such branch is pushed. The copy of the work is `ci/site` itself.
- **Nothing depends on which the repository is.** CI's result is read through the branch `ci-results` (R25). From
  the day the repository becomes private, R25's point "If the repository becomes private" holds.

## For the owner

None of these holds the work back. The first is answered (R27).

| Question | Until answered |
| --- | --- |
| Is the docs repository private or public? | answered on 2026-11-10: public for now, and pushing is allowed (R27) |
| Whose name stands in the copyright line? | `2042Third`, in `site.json` (R20) |
| Is R21's permission for the book's code the one the owner wants? | R21 as written |
| Copied files or the container on `https://pdm.pw`; and what does `nginx -V` print there? | both ways are tested; copied files are recommended (R23) |
| Under what terms may people use the engine? Its repository has no license file. | the book says only what the engine's repository says |

## What changes

**The plan** (applied with this file):

| File | Change |
| --- | --- |
| `README.md` | the two open questions become decisions; "Open questions for the owner" holds the table above; the state names nginx and the address |
| `book.md` | the fourth reader's `llms.txt` reason (R20); the reader's rights over the exported game point at R21; what a move of the address is (R24) |
| `site.md` | settings (`site.json`, the guard); reserved names; the footer; every Caddy line; gzip for rows 10 and 11 and for the release; gate (a)'s new failures; gate (c)'s rows; requirements 1 to 10; the deploy folder and README; the two nginx versions; headers; fonts; CI (`report`, no repository variable, no Caddy); the `llms.txt` row; "Where this file overrides the research"; the spike's list |
| `pipelines.md` | `book:` links (R25); labs, solutions and patches as downloads; `tools/notices.py`; the vendor quote's header; CC BY captions and download credits; engine links from `engine.pin` |
| `style.md` | the solution file's place (R25); the caption credit (R22); the word list's license (R20) |
| `process.md` | the erratum of the fox's credit; the push that waits (R25); `tools/cistatus.py` through git |
| `critique/dispositions.md` | the license and the server are decided, with this file as "where" |

R26 adds to these: in `site.md`, base path rule 8, the rule id `literal-origin`, the `error_page` line, the tests
of requirements 3, 6 and 10 and of `node_modules`, the README's items 2 and 3, the jobs of the CI table and where
the originals' archive goes; in `pipelines.md`, §1.1, §3.2, §5.7, §6.2, §12, §13 and §15; in `process.md`, the
table of files, step 5 and the briefs of the fox's erratum.

`outline-4.md`'s row for `appendix/credits` and the unit `allocation/appendix.md` change in the allocation's
settlement, not here, because the allocation's critics are reading them.

**The tree** is the site builder's and the tool builder's: the stages of the running chains that have not started
take this file as their plan, and what an ended stage built against the old plan is the fixer's work. Their lists
are in `.tools/handover/`.
