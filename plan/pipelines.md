# Pipelines: what keeps the book true

Five things in the book come from the engine and are checked against it: quoted code, pictures, tutorials, reference
tables and the engine names in the prose. Each has a tool in `tools/`. This file gives the formats the tools read and,
for every tool, its command line, what it reads, what it writes and what makes it fail.

**(spike)** marks a place where the site spike's working code in this repository (`tools/*.py`, `tools/booklib/`,
`tools/schemas/`, `src/plugins/*.mjs`, `engine.pin`, `tutorials/`) differs from this file. The tool builder changes the
spike to match this file, except where the place says that this file follows the spike.

Contents: 1 the engine at the pin · 2 rules every tool follows · 3 code excerpts · 4 sketches · 5 pictures ·
6 tutorials · 7 generated reference · 8 the names lint · 9 glossary · 10 moving the pin · 11 engine additions (v0.8.1)
· 12 files and who writes them · 13 when each check runs · 14 where the engine names of this file are defined ·
15 third-party notices.

Engine paths in this file are relative to the engine's root at the pin `822a7a46`; "file:line" is a line at that commit.

## 1. The engine at the pin

### 1.1 `engine.pin`

The format of the spike's `engine.pin` is kept:

```text
commit 822a7a46dbcdd86e8e2eafde7e41d003e27260c8
release 0.8.0
prerelease yes
repository https://github.com/2042Third/GameEngine
```

- `commit` is the full 40-hex SHA. Tools refuse a short one: a short SHA stops resolving once another object shares
  its prefix, and tags can move (rc tags exist, such as `v0.3.0-rc1`). (spike: `booklib/repo.py` `read_pin` already
  refuses it.)
- `release` is the engine release the book describes; `prerelease yes` while `commit` is not that release's tag.
- The pin moves twice: to the commit of tag `v0.8.0` (`release 0.8.0`, `prerelease no`), then to the commit of tag
  `v0.8.1` (`release 0.8.1`, `prerelease no`). v0.8.1 is the book's final pin (section 11).
- `repository` is the address of the engine's repository. Tools and CI read it from this line; where this file
  spells the address in a command (1.3), this line is what is meant (`critique/rulings-6.md`, R26).
- Only `tools/pin.py move` writes the file (section 10).
- (spike) The comment at the top of the spike's `engine.pin` says that the working tree of the engine clone does not
  matter. That is true only for excerpts and parsing; the comment changes to "the working tree must be at the pin and
  clean for pictures, tutorials and the reference dump (plan/pipelines.md §1)".

### 1.2 Two engine inputs

**`--engine <folder>`: the pin clone.** `G:/GameEngineAI/.worktrees/docs-pin`, a separate clone of the engine made with
`git clone`. It is never a worktree of `G:/GameEngineAI`, so nothing the engine's own agents do moves it. It is checked
out detached at the pin, with its submodules at the commits the pin records. Tools read its files through one
`git cat-file --batch` process at the full pin, never one `git show` per file. (spike: `booklib/repo.py` `Engine.read`
runs `git show` per file.)

**`--build <folder>`: the pin build.** `G:/GameEngineAI/.worktrees/docs-pin/build/windows/bin/Release`, a Release
build of exactly the pin, made in the pin clone. It holds `StrataEditor.exe`, `StrataCLI.exe`, `StrataRuntime.exe`,
`StrataTests.exe` and `Samples/`.

Why the working tree and a build of the pin are needed (facts at 822a7a46):

- `--headless` keeps the GPU; only `--no-gpu` runs without a device (`StrataEditor/src/EditorApplication.cpp:70-71`).
- `project.openSample` copies `<build>/Samples` (`StrataEditor/src/Editor/ProjectSamples.cpp:96`), which the build
  copies from the clone's `Samples/` at every build (`StrataEditor/CMakeLists.txt:97-103`).
- Script builds compile against `<engine directory>/StrataScriptCore` (`StrataEditor/src/Editor/ScriptToolchain.cpp:712`):
  in a build from source, the clone's working tree.
- `Tools/LookDev.py` and `Tools/GenerateShowcaseTerrain.py` read the clone's `Samples/` and `Tools/LookDev/`.
- `StrataEditor --version` prints no commit. `editor.status {sections: ["engine"]}` reports `engineCommit`: the first
  12 hex digits of the build's commit, `unknown` outside a git checkout, with no dirty flag
  (`CMake/StrataVersionCommit.cmake:11`, `StrataEditor/src/Editor/EditorStateCommands.cpp:780`).
- At a pre-release pin the programs report the previous release. At `822a7a46` the project's version is 0.7.0
  (`CMakeLists.txt:4`); `c_EngineVersion` takes it (`Strata/src/Strata/Core/Version.h.in:11`, `:17`), and so do the
  `engineVersion` of `editor.status` (`EditorStateCommands.cpp:777`), `--version` and every label that shows the
  version, while `engine.pin` says `release 0.8.0`. Tools check `engineCommit`, never `engineVersion`. Text figures
  leave the version out (`keep`, `redact`, 5.2), and `style.md` §13 says what a page that shows it writes. The move to
  `v0.8.0` (section 10) brings programs that report 0.8.0.
- No release package of 822a7a46 exists: GitHub releases end at v0.7.0.

### 1.3 Making the clone and the build

One agent (process.md names it: the tool builder) makes the clone once and the build once per pin, at a time the
planner chooses, with these commands and no others:

```sh
git clone https://github.com/2042Third/GameEngine G:/GameEngineAI/.worktrees/docs-pin   # once
cd G:/GameEngineAI/.worktrees/docs-pin
git fetch --tags origin                                                                # at a pin move
git checkout --detach <full pin>
git submodule update --init --recursive --depth 1
python Tools/PerfLock.py --label docs-pin-build --wait 120 -- cmake --preset windows
python Tools/PerfLock.py --label docs-pin-build --wait 120 -- cmake --build build/windows --config Release --parallel 2 --target <slice> -- /p:CL_MPCount=4
```

- The build makes only the programs the tools start: `StrataEditor`, `StrataCLI` and `StrataRuntime`. It runs in
  slices, each its own hold of the lock inside PerfLock's default limit of 25 minutes: the third-party libraries, the
  engine's libraries, then each program. An engine agent's perf run waits 30 minutes for the lock and then fails, so
  no hold of the book's comes near that while engine agents work (`critique/rulings-5.md`, R19). A slice the limit
  ended is run again; the build is incremental.

- The clone comes from `engine.pin`'s `repository`, so making it also proves that the pin is public (the book links to
  it).
- `--parallel 2 -- /p:CL_MPCount=4` is the form the engine's agents build with: at most two projects at a time and
  four compilers in each, which leaves most of the 24 hardware threads of the i7-13700K to them. `--parallel 8`
  alone would not bound the load: with the Visual Studio generator it counts projects, and each project starts a
  compiler per hardware thread. The perf lock keeps every perf measurement off the machine while the build runs.
- At a pin move the same commands run again in the same clone; the build is incremental in the same folder.
- The clone stays clean: `git status --porcelain` prints nothing and every line of `git submodule status` starts with a
  space (not `+`, `-` or `U`). Builds write only under `build/`, which the engine's `.gitignore` ignores; editors write
  only into copies under `--work`.

**The release package (phase B).** At each release pin (v0.8.0, v0.8.1), `tutorials.py run` also runs once with the
official Windows package of that release as `--build`: unpacked into `G:/GameEngineAI/.worktrees/docs-package-<version>/`
after its SHA-256 matched the `.sha256` file the release publishes beside it (`.github/workflows/release.yml:221-226`).
It is what readers install, and its script SDK is the package's own. Its runs are recorded in the same stamps (6.4).
Nothing is built for it.

### 1.4 What every run checks first

A tool that starts an engine program stops with exit code 2, before it starts anything, when:

1. `--engine` does not resolve the pin as a commit;
2. the clone's `HEAD` is not the pin, or the clone is not clean (1.3);
3. `--build` lacks `StrataEditor.exe` or `StrataCLI.exe` (or `StrataRuntime.exe` for runtime figures);
4. the first editor it starts answers `editor.status {sections: ["engine"]}` with an `engineCommit` that is `unknown`
   or is not a prefix of the pin. Every later editor of the run is checked the same way.

Tools that only read (excerpts, sketches, the offline checks, rendering the reference) need only check 1.

## 2. Rules every tool follows

- **Language.** Python 3.10 or later, standard library only, run as `python -I tools/<tool>.py`. Exit codes: 0 all is
  well, 1 problems were found, 2 usage or environment errors (the spike's convention).
- **Tests.** Every tool has unit tests in `tools/tests/` that run without an engine (fixtures in the test folder);
  `python -I -m unittest discover tools/tests` passes before a tool changes.
- **Settings.** The deployment's values (the base, the origin, the copyright holder and year) are those of `site.json`
  at the repository's root. Tools read them only through the shared library's `tools/booklib/settings.py`, which
  applies site.md's rules for a base and an origin and the overrides `DOCS_BASE` and `DOCS_SITE`, as the build's
  `src/lib/settings.mjs` does; one table of cases, `tools/tests/fixtures/settings-cases.json`, tests both. No tool
  holds the book's origin as a literal: `tools/lint.py` fails on it outside `site.json`, `deploy/README.md`, the
  repository's `README.md` and `plan/` (`critique/rulings-6.md`, R24).
- **Reading.** Tools read the engine only through `--engine` at the pin, and otherwise only this repository and the
  folders this file names under `G:/GameEngineAI/.worktrees/` (`docs-pin`, `docs-package-<version>`, `docs-work`,
  `docs-baselines`). They never read `G:/GameEngineAI` itself or a worktree of the engine's work.
- **Writing the clone.** Only two things write inside the pin clone: the pin build (`build/windows`) and the patch runner
  (6.6: `build/docs-patch` and a patch it reverts).
- **One engine program at a time, under the perf lock.** Every run that starts an engine program runs inside
  `python <engine>/Tools/PerfLock.py --label docs-<tool> --limit <minutes> -- python -I tools/<tool>.py …` (90 minutes
  unless a section says otherwise; while engine agents work, PerfLock's default of 25 minutes, with the run split by
  page or by section, and `--wait 120`: `critique/rulings-5.md`, R19). The lock is the file `StrataPerfLock/perf.lock` in the user's temporary folder
  (`Tools/PerfLock.py`), shared with every engine agent's perf run; PerfLock runs with the normal `TEMP`, never the
  book's `.tools/tmp`, or it would not see their lock. PerfLock exits 75 when it did not get the lock within 30 minutes
  and 124 when the run passed its limit; the tool's caller treats both as failures. The pin move's report names any
  change of `Tools/PerfLock.py` (10.2), since a moved lock would no longer keep the runs apart.
- **GPU.** Phase A: every editor runs with `--no-gpu`, except the four captures of the checks before writing (5.4).
  Phase B: only `figures.py take`, `tutorials.py run --pictures` and `tutorials.py patch` use the GPU, still one at a
  time.
- **Environment of every engine program a tool starts:**
  - `STRATA_SESSION_DIR`: a new folder `StrataDocs-<pid>-<seconds>` in the user's temporary folder, which the tool
    names but does not create: the editor and the CLI create it private (`Strata/src/Strata/Network/EditorSession.cpp:17`;
    `Tools/LookDev.py:580-583` does the same). It is never under `--work`: the authoring drive `G:` is exFAT, which keeps
    no permissions.
  - `STRATA_RECENT_PROJECTS`: `<work>/recent-projects.json` (`StrataEditor/src/Editor/RecentProjects.h:60`), so the
    owner's list is never read or changed and the launcher shows the same list in every picture.
  - `STRATA_SCRIPT_BUILDS_DIR`: `<work>/script-builds` (`StrataEditor/src/Editor/ScriptBuild.cpp:490`), so the book's
    script builds never mix with the owner's (`<user data>/Strata/Builds` by default).
  - `STRATA_EDITOR_PATH`: `<build>/StrataEditor.exe`, the editor `StrataCLI launch` starts.
- **Preferences.** Editors read the person's `<user data>/Strata/Preferences.json`; nothing at the pin moves that file
  (`StrataEditor/src/Editor/EditorPreferences.cpp:61-66`). No tool calls `preferences.set` or `preferences.save`, and
  the reference shows the preferences' schema defaults, never their values.
- **Driving editors.** As `Tools/LookDev.py` drives them (`Tools/LookDev.py:570-660`): `StrataCLI launch [--headless |
  --no-gpu] [--project <dir>] --idle-timeout 900`, then `StrataCLI call <command> @<params file> [--project <dir>]
  --timeout <ms>` per command, and `editor.quit {force: true}` at the end. Timeouts: 300 s per call, 900 s for opening
  a scene or a world. A whole command script runs as `StrataEditor --no-gpu --no-automation --project <dir> --commands
  <script> --quit-after-commands --frames 36000`; its exit code must be 0 (`Tools/LookDev.py:606-614`).
- **Copies.** Samples and projects are never opened in place: always copies under `--work`.
- **Work folders.** `--work <folder>`, default `G:/GameEngineAI/.worktrees/docs-work/<tool>`: copies, originals, logs.
  Never committed. A run keeps its folder until the next run of the same tool, so a person can look at what failed.
  Keep it short: script builds fail, naming the excess, when a project's paths are too long for MSBuild
  (`StrataEditor/src/Editor/ScriptBuild.cpp:482-486`).

## 3. Code excerpts

### 3.1 The fence

A quote has four parts that the book owns (Expressive Code never sees them): the source, its lines at the pin, an
anchor, and marks in the file's line numbers. The spike's `tools/excerpts.py` and `src/plugins/excerpts.mjs` already
work with names of their own for three of them, which the book keeps (this file follows the spike):

| Part | Name in the book | Notes |
| --- | --- | --- |
| source | `src="<path>#…"` | an engine path has no prefix (spike); other sources have a namespace prefix (3.2) |
| lines at the pin | `#L<first>-L<last>` at the end of `src` (spike) | written by `fill`; one line is `#L<n>` |
| marks | `mark="L<n>,L<a>-L<b>"` (spike) | the file's line numbers, inside the quoted lines |
| anchor | `symbol="<qualified name>"` | new: written by `fill` and kept, so that `relocate` finds the lines again after a pin move. (spike: the symbol exists only as `#<symbol>` before `fill`, which drops it) |

A filled quote, as a page holds it:

````md
```cpp src="Strata/src/Strata/Scene/Scene.cpp#L2267-L2292" symbol="Scene::OnUpdateRuntime" from="m_FixedTimeAccumulator += deltaTime;" to="m_FixedTimeAccumulator -= fixedTimestep;" mark="L2280,L2291-L2292"
…the lines, written by tools/excerpts.py fill…
```

`Scene::OnUpdateRuntime` spans `Scene.cpp:2199-2336`, 138 lines, more than a quote may hold, so the draft named the
piece with `from` and `to` (3.3); both texts occur once in the definition. Line 2280 is the `while` of the fixed steps,
2291-2292 the systems' fixed update and the accumulator's decrement.
````

The excerpts plugin (`src/plugins/excerpts.mjs`) turns `mark` into Expressive Code's block-relative `mark={…}` and sets
`showLineNumbers startLineNumber=<first>`, so the page shows the file's own line numbers. It writes a header above the
quote: the path, the line numbers and the link that 3.2 gives for the quote's source. (The plan follows the spike
here: the header is written by this remark plugin, not by an Expressive Code plugin.) Expressive Code's own `mark="…"`
marks text and its markers count the block's lines, so on a quote these are refused: Expressive Code's `{…}` markers,
`ins=`, `del=` and `title=`. A `mark="L…"` on a fence without `src` is refused. (spike: refuses `title=` and `mark`
without `src`; the other three refusals are new.)

### 3.2 Source namespaces

| `src` begins with | Reads | Links to |
| --- | --- | --- |
| an engine path (`Strata/`, `StrataEditor/`, `StrataRuntime/`, `StrataScriptCore/`, `StrataCLI/`, `StrataTests/`, `Samples/`, `CMake/`, `Tools/`, `Docs/` or another top-level entry of the engine at the pin) | the blob at the pin | `<repository>/blob/<pin>/<path>#L<a>-L<b>`, where `<repository>` is the `repository` line of `engine.pin` (1.1): one helper builds every engine link from that line (`critique/rulings-6.md`, R25) |
| `vendor:<lib>/<path>` | the submodule `Strata/vendor/<lib>` at the commit the pin records for it (`git ls-tree <pin> Strata/vendor/<lib>`, mode 160000), read from the clone's submodule repository with `git cat-file --batch` | the library's repository as `.gitmodules` at the pin names it, `/blob/<submodule commit>/<path>#L<a>-L<b>` |
| `book:<path>` | this repository's file (tutorial files, labs, patches) | never this repository: the header names the path, and links the file's download under `<base>/downloads/` when the site publishes one (5.7, 6.3). A file the book tells a reader to run or open is quoted in full on its page or published there (`critique/rulings-6.md`, R25) |
| `book:<path>.patch#hunk-<n>` | the n-th hunk of a tutorial's patch (6.6), with its `+` and `-` lines, language `diff` | the header names the patch's path, the engine file the hunk changes and its lines at the pin, and links the patch's download `<base>/downloads/tutorials/<part>/<chapter>.patch` (6.3) |

- All 19 libraries under `Strata/vendor/` are gitlinks at the pin (ImGuizmo, MikkTSpace, NVRHI, Vulkan-Headers,
  box3d, cgltf, doctest, entt, glfw, glm, imgui, json, meshoptimizer, miniaudio, nfd, spdlog, stb, tracy, zstd).
  `Strata/vendor/Implementations` is a folder of the engine and is quoted as an engine path.
- A page that quotes `vendor:<lib>` is accepted only when `<lib>` is listed in `ThirdPartyNotices.md` at the pin and
  named, with its license, on the page `appendix/credits`. The quote's header names the library, the path, the version
  that `ThirdPartyNotices.md` records for it at the pin and the license's id; the library's notice is in section B of
  the notices file (section 15), which `appendix/credits` links, and that page holds no license text itself
  (`critique/rulings-6.md`, R22). The build does not read the engine, so `excerpts.py fill` writes each quoted
  library's version and license id into one committed JSON file; `check` fails when that file is stale, and the
  build reads it for the header (R26).
- Files that exist only in builds (`Version.h`, made from `Version.h.in`; `VersionCommit.h`; the embedded shaders;
  `Package/StrataInstall.json`) are never quoted: the page quotes their template or generator.
- (spike) The spike knows no namespace: every `src` path is read from the engine.

### 3.3 Draft forms

While a page is written, an anchor stands in place of the lines. `fill` turns it into lines; `check` refuses a page
that still has one, so such a page cannot enter review.

| Draft form | Lines `fill` takes |
| --- | --- |
| `src="<path>#<symbol>"` (spike) | the whole definition of the symbol, with the comment just above it |
| plus `from="<text>" to="<text>"` | from the first line inside the definition that contains `from` to the first later line that contains `to`; each text must occur exactly once inside the definition |
| plus `overload="<n>"` | the n-th definition in file order, when the symbol has several (for example `ComponentRegistry::SetInactiveReason` at `Strata/src/Strata/Reflection/ComponentRegistry.h:253` and `:258`); without it, several definitions are an error (spike) |
| `src="<path>" command="<name>"` | the registration of an editor command: from the line holding `"<name>",` in a `Register(` call to the line that closes that call. Command handlers are lambdas inside `Register*Commands` functions of 400 lines and more (`StrataEditor/src/Editor/EditorViewportCommands.cpp:994-1399`) |

After `fill`, `src` ends with `#L<first>-L<last>` and the anchor attributes (`symbol`, `from`, `to`, `overload`,
`command`) stay on the fence. `fill` writes `symbol` from the draft's `#<symbol>`. (spike: `from`, `to`, `overload`
and `command` are new.)

### 3.4 Normalization

`fill` and `check` apply one normalization and nothing else:

- Remove the smallest number of leading tabs over the quoted lines that are not blank and are not preprocessor lines at
  column 0 (such as `#ifdef ST_DEBUG` inside `Scene::OnUpdateRuntime`, `Strata/src/Strata/Scene/Scene.cpp:2215-2217`).
  (spike: no dedent; `check` compares raw lines.)
- The page shows tabs 4 columns wide, as the engine's `.editorconfig` sets (`tab_width = 4`): the code blocks' CSS sets
  `tab-size: 4` (site.md). (spike: not set; browsers default to 8.)
- Long lines wrap with their indentation kept (`wrap: true, preserveIndent: true` in the spike's `ec.config.mjs`).
  The engine's `.clang-format` sets `ColumnLimit: 0`; lines reach 245 columns (with tabs as 4) in
  `StrataEditor/src/Editor/EditorViewportCommands.cpp`.

### 3.5 `tools/excerpts.py`

```text
python -I tools/excerpts.py fill     --engine <clone> [pages...]
python -I tools/excerpts.py check    --engine <clone> [pages...]
python -I tools/excerpts.py relocate --engine <clone> --from <old pin> [--to <new pin>] [--write] [pages...]
python -I tools/excerpts.py list     [--since <commit of this repository>] [pages...]
```

(spike: the four commands exist; `--since` is new.)

- **Reads:** the pages `src/content/docs/**/*.md`, `engine.pin`, the pin clone and its submodule repositories, the
  `book:` files.
- **`fill` writes** fence bodies, the `#L…` of `src` and `symbol` into pages. It refuses a fence, leaving it unchanged
  and exiting 1, when the range would exceed 60 lines, when an anchor matches no place or several, or when the path
  does not exist at the pin.
- **`check` fails** (exit 1) on: a body that differs from the normalized lines at the pin; a draft form; a quote over
  60 lines (`tools/lint.py`, spike, also refuses quotes under 5 lines); a page of kind internals with fewer than three
  quotes (spike); an engine path named in backticks in the prose that does not exist at the pin (spike); a refused
  marker (3.1); a `vendor:` quote whose library fails 3.2.
- **`relocate`**, per quote, in this order:
  1. the same lines hold the same text at the new pin: **same**;
  2. the same text is elsewhere in the same file: **moved** to the nearest place; `--write` updates `#L…`, the marks
     and the numbered callouts after the fence (`1. **Lines 5–10:**`, up to the next fence or heading) that name the
     quote's lines, by the quote's offset (step 3 too);
  3. the quote's most distinctive line (its longest line that occurs once in the old file) is found by `git grep -F`
     over the whole tree at the new pin, and the whole quote is there: **moved-file**; `--write` updates `src`. The page's
     prose may name the old path, so a reader checks it;
  4. the anchor finds its lines at the new pin, but the text differs: **changed**; a person reads the page again, then
     runs `fill`;
  5. otherwise **missing**.

  Exit 1 when any quote is moved-file, changed or missing. (spike: steps 1, 2 and 5, and step 4 through the function
  that encloses the old lines; step 3 and the stored anchors are new.)
- **`list`** prints every quote; with `--since <commit>`, only the fences whose `src` or anchor changed since that
  commit of this repository (a change after review needs the page's confirm, process.md).

## 4. Sketches

Code that is not the engine's is a sketch (`sketch="<file>"`), the output of a sketch (`output-of="<file>"`) or
pseudocode (the flag `pseudocode`), as the spike implements them. Sketch files are named
`sketches/<part>-<chapter>-<name>.<ext>`, so two pages never collide. (spike: `sketches/fixed-step.cpp` and
`sketches/interpolation.cpp` have no page prefix.)

```text
python -I tools/sketches.py fill  [pages...]
python -I tools/sketches.py check [--no-compile] [--engine <clone>] [--slangc <path>] [pages...]
```

- **C++:** compiled by `$CXX` (else the first of `g++`, `clang++`, `c++`) with `-std=c++20 -Wall -Wextra -Werror` and
  `-isystem <engine>/Strata/vendor/glm`, glm at the commit the pin records. A sketch whose output a page shows is run
  and its output compared with the `output-of` fence; a run may take 10 seconds. (spike: compiles and runs; the glm
  include is new.)
- **Slang:** compiled by the slangc of the release that `CMake/StrataSlang.cmake` pins (`STRATA_SLANG_VERSION`
  `2026.20` at 822a7a46, with a SHA-256 per platform): `slangc <file> -target spirv -entry main -stage <stage>
  -I <engine>/Strata/shaders -o <scratch file>`, where the file is named `<name>.<vert|frag|comp>.slang`. `check` first
  runs `slangc -version` and requires `STRATA_SLANG_VERSION` in its output. (spike: Slang is not compiled.)
- **Writes:** `fill` writes the copies and outputs into fences.
- **Fails** (exit 1): a fence differs from its file or output; a compile error or warning; a non-zero exit code; a run
  over 10 seconds. Exit 2: no compiler, or a slangc of another version.
- **CI** uses `g++`, glm fetched at the submodule commit, and slangc fetched and checked against the SHA-256 in
  `CMake/StrataSlang.cmake`.

## 5. Pictures

### 5.1 Kinds

| Kind | What it shows | Made by | Identity rule (5.6) |
| --- | --- | --- | --- |
| `scene` | a still render | `viewport.capture` in a headless editor with a GPU | the two captures are the same picture (5.6) |
| `live` | motion at exact fixed steps (motion blur, TAA in motion, level-of-detail fades) | `viewport.capture {live: true}` in a windowed editor | three takes with equal fixed steps; judged by eye |
| `editor` | the whole editor window | `StrataEditor --windowed … --screenshot` | judged by eye |
| `runtime` | an exported game | the game's executable with `--screenshot` | exit code 0; judged by eye |
| `text` | the output of a command or program, shown in a fence | `figures.py take --kinds text` | two runs give the same text |
| `reference` | a ground-truth image made by a book sketch (a path tracer) | `figures.py take --kinds reference` | two runs are byte-identical |
| `tool` | a program that is not Strata | Playwright, or the owner (5.5) | judged by eye |
| `diagram` | an SVG drawing the manifest lists | the writer | none |

Mermaid diagrams in pages are not manifest entries (site.md). (spike: the kinds are `scene`, `live`, `editor`, `game`
and `diagram`; `game` becomes `runtime`; `text`, `reference` and `tool` are new.)

**Text instead of a picture.** A figure is a `text` capture when what it shows is text the reader reads in a terminal,
a log or a command result: command results, `--help` output, `ctest` summaries, script build diagnostics, the numbers
of `renderStats`. A picture of a panel that shows the same text is made only when the page teaches where that panel is.

### 5.2 The recipe

The recipes of a chapter are `src/content/figures/<part>/<chapter>.json`, `{"figures": [ … ]}` (spike), checked
against `tools/schemas/figure-manifest.schema.json`. (spike: the schema describes an earlier format, with `taken`
inside the recipe, string `project` values, pixel crop rectangles and command steps as `[name, parameters]` pairs; it
is replaced by this one.)

An example; every engine name in it exists at 822a7a46 (section 14):

```json
{
  "id": "taa-thin",
  "shows": "Thin poles and a fence: without anti-aliasing their edges are stair-stepped, with TAA they are smooth",
  "caption": "The fence at shadow-map size {stats.taa.shadowMapSize}: TAA keeps the thin wires whole.",
  "alt": "Two pictures of grey poles and a wire fence in front of a pale sky, the first with jagged edges.",
  "kind": "scene",
  "project": { "lookdev": true },
  "shot": "lookdev.thin",
  "size": [1920, 1080],
  "quality": "high",
  "overlays": false,
  "setup": [
    { "command": "component.set", "entityName": "Sun",
      "parameters": { "component": "DirectionalLight", "values": { "Intensity": 120000 } } }
  ],
  "variants": { "off": { "antiAliasing": "off" }, "taa": { "antiAliasing": "taa" } },
  "expect": "complete",
  "record": { "shadowMapSize": "/renderStats/shadowMapSize" },
  "publish": "lossless"
}
```

The shot `lookdev.thin` of `Tools/LookDev/Shots.json` supplies the camera (position `[6, 1.5, 8]`, target
`[6, 0.8, 0]`, field of view 40), the scene (`Scenes/LookDev.stscene`, its project's scene) and the crops `poles` and
`fence`.

| Field | Required | Values | What the tool does with it |
| --- | --- | --- | --- |
| `id` | yes | lowercase words joined by `-`, unique in the chapter | the page writes `::figure{id=…}` or `::compare{id=…}` |
| `shows` | yes | one sentence | the photographer judges the picture against it; a picture that does not show it is retaken or its recipe changed |
| `caption`, `alt` | yes | text; numbers in `caption` as `{stats.<name>}` or `{stats.<variant>.<name>}`; a figure that shows a CC BY file names its author and license in `caption`, and `appendix/credits` holds the full entry (style.md §11; `critique/rulings-6.md`, R22) | filled from `record` |
| `kind` | yes | 5.1 | |
| `project` | all kinds that run an editor, except a figure of the launcher | `{"sample": "<id>"}` (an id `project.samples` lists), `{"template": "empty"}`, `{"template": "basic3d"}`, `{"lookdev": true}`, `{"lab": "labs/<name>.json", "template": "empty" or "basic3d"}` | 5.4, project copies |
| `scene` | no | an asset path of a scene of the project | `scene.open {scene}`; default: the shot's scene, else the project's start scene |
| `shot` | no | a `Name` of `Tools/LookDev/Shots.json` at the pin whose `Project` matches `project` | supplies the camera, scene, crops, `Setup`, `DebugView`; the recipe may not set `camera` or `crops` beside it |
| `station` | no | `Dawn`, `Golden` or `Dusk`, with `{"sample": "Showcase"}` only | the steps of `Tools/GenerateShowcaseTerrain.py setup --station <s> --format script` |
| `world` | no | `{"loadAll": true}` | `world.loadCells {region: {min: [-20000, -20000], max: [20000, 20000]}, wait: true}` |
| `camera` | `scene` kind, unless `shot` | `{"position": [x, y, z], "target": [x, y, z], "fov": degrees}` or `"scene"`; `"editor"` is refused | `viewport.capture` `position`, `target`, `fov`, or `camera: "scene"` (the two cannot be combined) |
| `size` | no | `[width, height]`, each 16 to 4096; default `[1920, 1080]` | `width`, `height`. Size is part of the recipe: High's automatic shadow-map size depends on it |
| `quality` | no | `low`, `medium`, `high` (default), `ultra`, or `{"custom": {<Renderer.Quality fields>}}` | a preset is passed to the capture; `custom` sets the section (5.4 step 2) and captures with `quality: "project"` |
| `antiAliasing` | no | `taa`, `fxaa`, `morph` or `off`; default: the scene's own setting | `component.set` on the scene's one PostProcess entity (5.4 step 4) |
| `postProcess` | no | property values of the `PostProcess` component | `component.set` on the same entity |
| `materials` | no | `{"<material asset path>": {<material properties>}}` | `material.set {material, properties, save: false}` (previews, writes no file) |
| `debugView` | no | `none` (default) or a value of the `debugView` enum of `viewport.capture` | `debugView` |
| `renderer` | no; `scene` kind | `{"<switch>": value}`: switches of the `renderer` parameter of `viewport.capture` at the pin (`DitherOutput`, `FXAASubpixel`, `SpecularEnergyCompensation` and the others the commands dump lists, with their values) | `renderer` of both captures of step 6; a variant's `renderer` replaces the recipe's; the result's echo must hold them, and the stamp records them (`renderer` in `taken.json`). A `setup` step `viewport.capture` takes a picture of its own, which the take throws away: `check` refuses one with `renderer` |
| `overlays` | no | default `false` | `overlays`. The capture's own camera draws the editor overlays unless told not to (`StrataEditor/src/Editor/EditorViewportCommands.cpp:1256`) |
| `waitForAssets` | no | default `true` | `waitForAssets` |
| `play` | no | `{"steps": n}` or `{"steps": n, "input": [<events of input.sequence>]}` | `play.start {paused: true}`, then `play.step {steps}` or `input.sequence {events, steps}` |
| `live` | `live` kind | `{"atFixedStep": n, "frames": 1 to 16}`, and `play` with at least `atFixedStep` steps | `viewport.capture {live: true, camera: "scene", atFixedStep, frames}` (5.4, live) |
| `runtime` | `runtime` kind | `{"resolution": [w, h], "seconds": n, "quality": "low" … "ultra"}`; `seconds` whole (the runtime's `--seconds <count>`) | the runtime's options (5.4, runtime). The game draws what the project saved, so a runtime recipe changes its copy only in `setup` steps that save it (`scene.save`); `check` refuses `shot`, `camera`, `scene`, `station`, `world`, `quality`, `antiAliasing`, `postProcess`, `materials`, `debugView`, `renderer`, `overlays`, `waitForAssets`, `play`, `live` and `editorWindow` on it |
| `automation` | no; `editor` kind | `true`, or `{"client": "<name>"}` (a short name, such as `claude-code`) | `true`: the window serves automation (5.5, "Automation figures"); with `client`, an agent named so sends the figure's steps and stays connected at the screenshot; `check` refuses it on other kinds, and `client` beside an `atStep` |
| `editorWindow` | `editor` kind | `{"layout": "layouts/<name>.ini", "steps": [<command steps>]}`, optionally `"windowSize": [w, h]` (default `[1280, 720]`, at least 640 × 360), `"panel"` (a name `editor.showPanel` takes) and `"launcher": true` (the editor starts without a project, so the window shows the launcher: the recipe has no `project`, `scene`, `station`, `world`, `setup`, `play` or `files`) | 5.4, editor |
| `text` | `text` kind | `{"command": {"command": "<name>", "parameters": {…}}, "keep": [<JSON pointers>]}` or `{"program": "StrataEditor", "StrataRuntime", "StrataCLI" or "ctest", "arguments": […], "redact": [<regular expressions>]}`; either may add `"measured"` (5.6) | 5.4, text |
| `reference` | `reference` kind | `{"sketch": "<sketch file>", "arguments": […]}` | 5.4, reference |
| `takenBy` | `tool` kind | `"playwright"` or `"owner"` | 5.5 |
| `setup` | no | command steps (below) | run after the station and shot steps |
| `files` | no; `editor` and `scene` kinds, and `text` figures of a `program` | `[{"from": "book:tutorials/…", "to": "<path in the project>"} or {"stage": n}]`, as a tutorial's stage names its files (6.2), each with an optional `"atStep": k` | copied into the project copy before the editor opens it, or before step k of `editorWindow.steps` (the window closes and a new one runs the rest) or of `setup`; `{"stage": n}` is what stages 1 to n of the page's tutorial copy, so that a build error, a script's log or a crash can be pictured. A program's files are staged, without `atStep`, in the folder it runs in (5.4, text), and its `arguments` name them by relative paths; `check` refuses a file the book lacks or outside `tutorials/`, one over 10 MB, and a target outside the project |
| `variants` | no | `{"<name>": {<fields>}}`, at least two | a variant may set any field except `kind`, `project`, `shot`, `camera`, `size`, `crops` and `publish` (so that the two sides of a slider line up and are encoded alike); it may also set `baseline` (5.5) |
| `crops` | no | `[{"name": "<word>", "rect": [x0, y0, x1, y1], "scale": 1 to 8}]`, normalized to the picture as Shots.json's are | cut from each picture at its own pixels; `scale` is the whole factor the page enlarges it by, without smoothing |
| `expect` | no | `"complete"` (default) | 5.3 |
| `expectAlso` | no | `{"<JSON pointer>": {"equals": v} or {"min": n} or {"max": n}}` | added to `complete` |
| `relax` | no | `{"<pointer of the complete set>": "<why>"}` | removes that condition |
| `record` | no | `{"<name>": "<JSON pointer into the result>"}` | values kept in `taken.json` and used by `{stats.…}` |
| `numbers` | when `caption` has a number not written as `{stats.…}` | one sentence: where the number comes from (a reference-machine measurement, a page, a test) | read by the technical reviewer |
| `publish` | renders of parts `image`, `indirect` and `light` | `lossy` or `lossless` | 5.7 |
| `waitsFor` | no | an engine addition of section 11, such as `"tier 2: debug view specular"` | `take` skips the figure; `check` fails when the pin already has the addition. (spike: `waits_for` with free text) |
| `blocked` | no | one sentence: why no take can make the figure at the pin, though it waits for no addition (the pin lacks the feature, a command cannot reach the state) | `take` skips it; `list` names its files `blocked`; `check` refuses it beside `waitsFor` |
| `standIn`, `noStandIn` | no; a figure that waits or is blocked | `standIn`: the `id` of the figure of the same manifest that the page places in this one's place (a drawing, or the nearest honest picture); `noStandIn`: one sentence, why the page shows nothing there | section 11, "Stand-ins" |

**Command steps** in `setup`, `variants.*.setup` and `editorWindow.steps` are the engine's command-script steps
(`command`, `parameters`, `expect`, `bind`, `until`: `StrataEditor/src/Editor/EditorCommandRunner.cpp:431-433`) plus
one key of the book's, `entityName`. The tool turns `entityName` into `entity.find {name}` and fails unless exactly
one entity matches (`Tools/LookDev.py:722-731` takes the first), then passes that entity as the step's `entity`. Values
a step binds are used as `{"$ref": "<name>"}` or `{"$ref": "<name>", "pointer": "<JSON pointer>"}`
(`StrataEditor/src/Editor/EditorCommandRunner.h:83-90`). Entities are named by `entityName`, never by ID: an entity
parameter is a hex ID (`StrataEditor/src/Editor/CommandUtils.cpp:73`), new in every copy for entities a
step creates.

**A figure that two pages plan** is made once: one recipe, in the manifest of the page that homes the figure. The
other page shows the same picture, with a caption that says what that page teaches. So the frame timeline of
`world/systems` is one drawing: `physics/world-step` shows it with an overlay of physics' three points (the changes
applied, the steps, the dispatch), and `worlds/physics-scripts` with an overlay of the World system and the
sub-scene slices that draw on one budget (`critique/rulings-7.md`, R31 and R34).

### 5.3 What "complete" means

`"expect": "complete"` requires these values in the result of `viewport.capture`
(`StrataEditor/src/Editor/EditorViewportCommands.cpp:956-988`):

```json
{ "/pendingAssets": {"equals": 0}, "/texturesBelowWanted": {"equals": 0}, "/stalePoses": {"equals": 0},
  "/pendingTextGlyphs": {"equals": 0}, "/ui/pendingGlyphs": {"equals": 0},
  "/localShadowViewsPending": {"equals": 0}, "/reflectionProbesPending": {"equals": 0},
  "/renderStats/deferredInstanceBytes": {"equals": 0},
  "/preExposureSettled": {"equals": true}, "/globalIlluminationSettled": {"equals": true},
  "/previewLighting": {"equals": false} }
```

and, depending on the variant:

- `"/temporalFrames": {"min": 8}` only when the variant's anti-aliasing is `taa`. Without TAA `temporalFrames` is 0
  (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3045`), and the capture waits for history only under TAA
  (`EditorViewportCommands.cpp:827`).
- `"/debugView/shadows/complete": {"equals": true}` with `debugView: "shadows"`.
- the result has no `notice`.

`globalIlluminationSettled` is true in a frame without GI (`Strata/src/Strata/Renderer/SceneRenderer.h:676`), so it is
always required. The tool checks these values itself because every wait of the capture is bounded in frames, and the
command still succeeds when a bound runs out (`EditorViewportCommands.cpp:808-847`). One wait is not reported at the
pin: a spatial screen-space reflection frame waiting for its previous color (`EditorViewportCommands.cpp:830`). From
v0.8.1, the result's own `complete` flag is required as well (section 11), and the pointer set stays as a cross-check.

A live capture returns only its images (`{live, camera, images: [{fixedSteps, temporalFrames, width, height, path}]}`,
`EditorViewportCommands.cpp:623-634`), so `complete` does not apply to `live` figures.

### 5.4 Taking pictures

```text
python <engine>/Tools/PerfLock.py --label docs-figures --limit 90 -- python -I tools/figures.py take
    --engine <clone> --build <bin> [--work <dir>] [--figures <glob of page/figure ids>]
    [--kinds scene,live,editor,runtime,text,reference,tool] [--baselines <dir>]
```

**Project copies.** One editor serves one project copy; the figures of a copy run in manifest order.

- `{"sample": "<id>"}`: `project.openSample {sample, directory: <work>/projects/<key>}`. It copies `<build>/Samples/<id>`
  without `.strata`, which also holds play-mode saves and the players' options (`EditorAssetCommands.cpp:388`).
- `{"template": …}`: `project.create {directory, name, template}`. Only `empty` and `basic3d` exist
  (`EditorAssetCommands.cpp:272-282`); basic3d's start scene is `Scenes/Main.stscene` with Main Camera, Sun, Sky, Ground
  and Post Process.
- `{"lookdev": true}`: once per run, `python -I <engine>/Tools/LookDev.py capture --build <bin> --projects LookDev
  --shots lookdev.overview --sizes 320x180 --aa off --repeat 1 --work <work>/lookdev --keep-work`, then a copy of
  `<work>/lookdev/projects/LookDev`. LookDev.py makes the project from `Tools/LookDev/LookDevScene.json` with its own
  placeholders, macros and generated leaf and grass textures (`Tools/LookDev.py:668-700`).
- `{"lab": …, "template": …}`: `project.create`, then the lab's files copied into the project, then the lab's script
  (5.5).
- A figure whose steps call `lighting.bakeProbes` gets a copy of its own: a bake moves the previous capture to the
  trash.

Before the first figure of a copy, the tool records `project.settings`: every section's `value` and `isDefault`.

**Still figures (`scene`)**, per figure and per variant, in this order:

1. `scene.open {scene, force: true}`, then `scene.loadStatus {wait: true}`; for `world`, `world.loadCells` as in 5.2
   (the extent is `WorldData::c_SupportedExtent`, 20,000 m: `Strata/src/Strata/World/WorldAsset.h:89`).
2. Quality: a preset waits for step 6. `{"custom": {…}}`: `project.setSettings {section: "Renderer.Quality",
   value: {"Preset": "Custom", <fields>}}`.
3. Steps, in this order: the station's (generated by the command in 5.2, never copied by hand), the shot's `Setup`
   (Shots.json at the pin), the recipe's `setup`, the variant's `setup`, then `materials`.
4. Anti-aliasing and `postProcess`: `entity.find {component: "PostProcess"}` must return exactly one entity; then
   `component.set {entity, component: "PostProcess", values}`, with the anti-aliasing values as `Tools/LookDev.py:49-54`
   maps them: `taa` `{"AntiAliasing": true, "AntiAliasingMethod": "TAA"}`, `fxaa` `{"AntiAliasing": true,
   "AntiAliasingMethod": "FXAA"}`, `morph` `{"AntiAliasing": true, "AntiAliasingMethod": "Morphological"}`, `off`
   `{"AntiAliasing": false}`.
5. `play`: `play.start {paused: true}`, then `input.sequence {events, steps}` or `play.step {steps}`.
6. Two `viewport.capture` calls with every parameter explicit: `width`, `height`, the camera (`position`, `target`,
   `fov`, or `camera: "scene"`), `overlays`, `quality` (the preset, or `"project"` for `custom`), `debugView`,
   `waitForAssets`, `path`, `overwrite: true`.
7. `play.stop`, when step 5 ran.
8. Restore: every settings section whose value now differs from the record is set back with `project.setSettings
   {section, value: <recorded value>}`, or `{section, reset: true}` when the record says `isDefault`. Samples store
   sections of their own (Showcase stores `Input.Actions`), and a figure's steps may set any section.

Nothing is saved, so the next `scene.open {force: true}` drops the scene's changes. Still figures never call
`viewport.setSettings`, whose values last for the editor's session.

**Live figures (`live`)** run in an editor in a window with a GPU that serves automation, as LookDev's live shots do
(`Tools/LookDev.py:771-790`); since `StrataCLI launch` takes no `--layout` (and an editor started without one reads and
writes the person's own layout), the tool starts it itself: `StrataEditor --window-size <the Game view's size plus
480 × 360, at most 3840 × 2100> --ui-scale 1 --layout <a new file in <work>/layouts> --project <copy> --idle-timeout
900`, with the take's private session folder, and drives it with `StrataCLI call` once `editor.status` answers. Each of
the three takes (5.6) makes its own copy, `<work>/projects/<picture>-take-<n>`, in a `--no-gpu` editor first. Live captures refuse `width`, `height`, `overlays`, `position`, `target`, `fov`, `debugView`, `quality` and
`waitForAssets` (`EditorViewportCommands.cpp:644`): they return what the Game view presented, drawn with the Game
view's quality, which is the project's with the players' options. So a live recipe has `camera: "scene"`, its `size`
becomes the Game view's size. Before each live figure the tool runs `project.setSettings {section:
"Renderer.Quality", value: {"Preset": "<the recipe's quality>"}}` and `graphics.resetPlayerOptions`. Then, as `Tools/LookDev.py:771-790` does: `editor.showPanel
{panel: "Game"}`, `viewport.setSettings {gameView: {mode: "custom", width, height}}`, steps 1, 3 and 4 above,
`play.start {paused: true}`, `viewport.capture {live: true, camera: "scene", atFixedStep, frames, path}` started without
waiting for its answer, `input.sequence` or `play.step`, the capture's answer, `play.stop`; the editor then quits, so
step 8 is not needed. The capture must return `frames` images of the Game view's size (a smaller one fails the take:
the window did not hold the view); each take's frames and answer stay in `<work>/live/<picture>/take-<n>/`.

**Whole-editor figures (`editor`)**: the project copy is made in a `--no-gpu` editor, then one program run per figure,
`StrataEditor --window-size <editorWindow.windowSize, default 1280x720> --ui-scale 1 --layout <work copy of
layouts/<name>.ini> --no-automation --project <copy> --commands <generated script> --quit-after-commands`. The
generated script opens the scene, runs the setup steps, `play` and `editorWindow.steps` (such as `selection.set` and
`editor.showPanel`; `entityName` becomes `entity.find` bound to the step's entity), `editor.wait {frames: 120}`, so
that thumbnails and the launcher settle, `editor.showPanel` of `editorWindow.panel` when the recipe pictures one panel,
and `editor.screenshot {panel, path, overwrite}` expecting `settled` (and the window's size). Without automation the
window shows none ("Automation off"); a driven editor shows "Agent connected" and the Scene view's "Agent: <command>".
The layout is copied first because the editor writes it; its first line names the window it was made for (`figures.py
layout`), and another window fails the figure. `figures.py layout <name> --window-size <w>x<h>` writes
`layouts/<name>.ini`, the editor's own first layout in a window of that size at UI scale 1 with that first line, and the
photographer edits its sizes. The recipe's `files` go into the copy before the window opens; before an `atStep` the
window closes and a new one opens the copy for the rest. `--provisional` takes with a build that is not the pin's (plan/card/
photo-editor.md); publish refuses such a take. What varies between takes is the UI scale and window size (fixed by these
options), the launcher's footer (GPU, startup time), the Console's time stamps, live statistics and background
thumbnails; the fonts do not vary (they are committed files). On Windows the editor is a GUI program; the tool waits for
the process to end. The figure of UI scaling and the figures of automation change two of these options (5.5, "Editor
figures" and "Automation figures"): a recipe's `automation` leaves `--no-automation` out.

**Neutral paths.** No picture, text or stamp names a folder of the machine. Each editor figure's folder,
`<work>/projects/<nn>`, is shown to its window as the root of a drive of its own: `subst` maps the first free letter of
S, P, Q, R, T to Z to it for the figure's windows and removes the mapping after them (mappings a stopped take left on
its work folder are removed first; on Linux and macOS a link `/tmp/strata-figures-<pid>` stands in). The window gets
its project copy as `S:\Projects\<name>` (the sample's id; `Figures`, `Lab` or `LookDev` for the others), so the
Export dialog suggests `S:\Projects\<name> Build` (`StrataEditor/src/UI/ExportDialog.cpp:120`); its layout, script and
screenshot in `S:\Editor`, with `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` there, so that the launcher's
recent projects are empty; and its layout copy remembers `S:\Projects` as the New Project and Open Sample dialogs'
location (`[StrataLauncher][Settings] ProjectLocation`, `StrataEditor/src/UI/ProjectDialogs.cpp:528-536`), which they
suggest in place of the user's home folder (`ProjectDialogs.cpp:134-139`). A take fails a figure whose recipe, stamp
(with the GPU and OS the editor's status gives), text or editor's log (what the Console can show) names the work
folder's real path or the user's home folder (also by its short name), and `check` refuses a recipe that names the
home folder.

**Runtime figures (`runtime`)**, per figure and variant: a copy of the project in a headless editor with the GPU (the
recipe's files in it, opened again), the recipe's and the variant's `setup` steps (which save what they change),
`script.build {wait: true}` when the copy has `Scripts/CMakeLists.txt` (the game runs the module the editor loaded),
`project.export {directory: <work>/export/<picture>}`, whose answer names the `executable`; then that executable
`--windowed --resolution <w>x<h> --seconds <n> --quality <preset> --save-directory <work>/saves/<picture> --screenshot
<png>`, in the export folder. `--screenshot` needs `--frames` or `--seconds` and a window; without `--save-directory`
the game would use the player's data (`StrataRuntime/src/RuntimeApplication.cpp:340-353`). The exit code must be 0,
and the screenshot must have the resolution. The pin's runtime has every option a recipe names: `--windowed`,
`--resolution`, `--seconds` (whole seconds of game time), `--quality`, `--save-directory`, `--screenshot`
(`RuntimeApplication.cpp:341-354`). The export needs `StrataRuntime` beside the editor in `--build`.

**Text figures (`text`)**: a `command` runs in a `--no-gpu` editor on the project copy, and only the `keep` pointers of
its result are kept; a `program` runs from `--build` with `arguments`, and every match of a `redact` expression is
replaced by `…`. A program with `files` (a command script, a project's file) runs each of its two runs in a fresh run
folder, `<work>/runs/<picture>-<n>`, with the files staged in it, which it sees as the root of a drive of its own and
as its working directory (neutral paths, below); its `arguments` are relative, and `check` refuses an absolute one in
any program's `arguments`, and one that leaves the run folder. Text figures may be taken in phase A.

**Reference figures (`reference`)**: the sketch is compiled as in section 4 and run without a time limit; it writes a
binary PPM image to its standard output, which the tool turns into a PNG. The sketch uses a fixed random seed.

**Checks before writing.** Four claims of the allocation rest on the code alone, and only a capture settles them. Each
page that will state one holds it as an item of type `open` labelled "Check:" with the check's name, and its brief is
written only when the result has replaced the item (`allocation/README.md`, "Checks before writing";
`critique/rulings-7.md`, R34). The photographer takes the four captures once the pin build exists (1.3), with the
GPU, one at a time under the perf lock (section 2), and reports each result to the planner:

| Check | What the capture settles | Pages that wait |
| --- | --- | --- |
| Simulate and skinned meshes | whether skinned characters stand in their bind pose while Simulate runs (`play.simulate`, `StrataEditor/src/Editor/Commands/PlayCommands.cpp:159`): the Animation system does not run in Simulate (`Strata/src/Strata/Animation/AnimationRegistration.cpp:33-36`, `Strata/src/Strata/Scene/Scene.cpp:2114-2115`) | `animation/editor`, `animation/system`, `make/play-test-debug` |
| A capture of the Game view without a camera | whether a capture of the Game view returns the game's UI over black when the scene has no primary camera (`StrataEditor/src/Panels/GameViewPanel.cpp:112`) | the figures of the UI over black (`ui`) |
| A capture step that opens the launcher's card | whether a capture step can open the launcher's card | the figures of the launcher's card (`automation`) |
| The recipe that sets WhenVisible on every fox | how a recipe sets `CullingMode` to `WhenVisible` on every fox of the Open World sample, while a step's `entityName` matches exactly one entity (5.2) | `animation/culling` (screenshot 11) |

### 5.5 Shots, stations, labs, options menus, "before" pictures, tool pictures

**Shots.** `Tools/LookDev/Shots.json` holds `Projects` and `Shots`. A shot has `Name`, `Project`, either `Camera`
(`"scene"` or `"editor"`) or `Position`, `Target` and `Fov`, and may have `Crops` (normalized `[x0, y0, x1, y1]`),
`Setup` (`{Command, Parameters}`), `Scene`, `AntiAliasing`, `DebugView`, `Live` and `Metrics`. Names look like
`showcase.shot6` or `lookdev.thin`. The file's own rule freezes only a shot's camera and crops; its setup steps and
anti-aliasing modes may change, and content appended to a scene can enter an old shot's frame, so reused shots are
re-judged at each pin move (10.2).

- Shots with `Camera: "editor"` (`tp.editor`, `pp.editor`, `ow.editor`, `basic3d.editor`) are refused: the editor
  camera's state is kept in `.strata`, which copies leave out.
- Shots whose `Setup` names entities by ID (`tp.dof` names `350D7DDD7ED21DD5`) work on copies of the same sample but
  depend on its content; the pin move lists them.
- Where Shots.json at the pin holds a shot made for a figure, the figure's row in the allocation and its recipe name
  it (`shot`): `tp.lut` and `tp.grain` for a color lookup and for grain with chromatic aberration on the Third-Person
  sample, `ow.sunward` and `ow.sunward.flare` for the lens flare off and on, the `lookdev.*` shots for the views and
  rooms of lighting and GI (`critique/rulings-7.md`, R34).
- Game pictures use `camera: "scene"` or play mode. The capture's own camera is an editor view: in edit mode a scene
  without a light of its own gets preview lighting, and the game's HUD and canvases are hidden
  (`EditorViewportCommands.cpp:1218-1221`).

**Stations.** `Dawn`, `Golden` and `Dusk` are the Showcase's times of day (`Tools/GenerateShowcaseTerrain.py:175-179`).

**Labs.** A lab builds a scene that no sample shows (spot lights, a tone-curve chart, a material ladder, mirrored
instances, orthographic cameras, far-from-origin scenes, an options menu), the way the engine's look-dev scene is
built. A lab is also what a reader can run: the reader gets it as its download, `<base>/downloads/labs/<name>.zip`
(5.7, `labs`), never from this repository (`critique/rulings-6.md`, R25).

- `labs/<name>.json` is an engine command script (only the keys of 5.2's command steps, no `entityName`), run in an open
  project: `StrataEditor --project <dir> --commands labs/<name>.json`. It never calls `project.create` and holds no
  absolute path and no placeholder.
- The files it needs are in `labs/<name>/`; the reader, and the tool, copy them into the project's asset folder first.
  Textures are generated (as `make_leaf_texture`, `Tools/LookDev.py:234`, does) or are committed CC0 or CC BY files,
  credited in `labs/CREDITS.md` and on `appendix/credits`.
- Each lab has one owner page, named in the part's brief; other pages ask for changes through their notes.

**Options menus.** No command sets the players' graphics options at the pin; only `graphics.resetPlayerOptions` exists
(`StrataEditor/src/Editor/EditorGraphicsCommands.cpp:16`). Figures of an options menu use a lab whose script class calls
`Graphics::Set(option, value)` (`StrataScriptCore/Include/StrataScript/Graphics.h:181`) while the game plays.

**"Before" pictures** (a feature at an older release) come from the engine's look-dev baseline sets, named with their
release tag. The sets are not committed in the engine repository: the Developer Guide places them on the reference
machine, outside the repository (`Docs/DeveloperGuide.md:769-773`): 0.6.0's set, taken with a Release build of
`bc6ee123` (tag `v0.6.0`), in `.worktrees/wave7-plan/lookdev/0.6.0/`, and 0.7.0's, taken with `76f28a21` (tag
`v0.7.0`), in `.worktrees/wave8-plan/lookdev/0.7.0/` with its Medium stills in `0.7.0-medium/`. Those folders are in
worktrees of the engine's work, which docs agents do not touch. The planner copies the three sets once, read-only, to
`G:/GameEngineAI/.worktrees/docs-baselines/v0.6.0/`, `v0.7.0/` and `v0.7.0-medium/`. Before the copy the planner
confirms that each source folder still exists and holds its `shots/` (at 2026-11-10, `git worktree list` no longer
names `wave7-plan` or `wave8-plan`, so the folders may be plain folders or gone). A set that is gone is reported to the
owner; the briefs then replace its "before" figures by diagrams, and `figures.py check --baselines` refuses a recipe
that names it.

- A variant `{"baseline": "v0.6.0"}`, `{"baseline": "v0.7.0"}` or `{"baseline": "v0.7.0-medium"}` takes the file
  `<baselines>/<set>/shots/<shot>-<width>x<height>-<aa>.png` (LookDev's name, `Tools/LookDev.py:707-708`) of the
  recipe's shot, size and anti-aliasing; no editor runs for it. Such a figure needs `shot`.
- `taken.json` records the set and the file's SHA-256; the caption names the release.

**Tool pictures** (`tool`): web pages (LookDev's `index.html`, a GitHub Actions run) are taken by the site's pinned
Playwright, headless (`"takenBy": "playwright"`), when `take --kinds tool` runs `node scripts/screenshot-page.mjs <url>
<png>`, a script the tool builder writes. Desktop programs (Tracy, Visual Studio, a file's properties in
Windows, a file browser) need a person's screen: `"takenBy": "owner"`. No agent controls the owner's screen; the owner
is invited to take them. Until then the page shows a diagram or text in the picture's place, and nothing waits for it.

**Reference figures.** `indirect/problem` has a sketch that path-traces the Cornell box by Monte Carlo integration; its
image is a `reference` figure. `indirect/ao`, `indirect/probes` and `indirect/gi-cascades` compare Strata's picture of
the same box against it in a slider: the look-dev project's `Scenes/Cornell.stscene` (made by
`Tools/LookDev/LookDevScene.json`), with the sketch's camera.

**Edit-mode poses** (`animation`). Still figures never call `viewport.setSettings` (5.4), so no recipe poses
characters through its view setting `editPose`. In a sample's copy or a new project, skinned characters stand in their
rest pose, `editPose`'s default, because both start without the `.strata/EditorViewport.json` that keeps the setting
(`StrataEditor/src/Editor/EditorViewportCommands.cpp:1152-1155`, `StrataEditor/src/Editor/EditorContext.cpp:387-391`).
Any other pose is a `setup` step per animator: `animation.preview` with `entityName` and a `state` or a `clip` at a
`time`. With `entityName` alone it shows, at time 0, what `editPose: "clipStart"` shows, and its requests win over
`editPose` (`StrataEditor/src/Editor/EditorAnimationCommands.cpp:286-290`, `EditorViewportCommands.cpp:1155`). It
fails while the scene plays (`EditorAnimationCommands.cpp:300`), so it comes before `play`, and the next `scene.open`
drops it with the scene (`EditorContext.cpp:702-706`).

**Editor figures** (`editor`, `editor-ui`, `make`). These steps of `editorWindow.steps` choose what the window shows:

| Step | What it brings into the picture | At the pin |
| --- | --- | --- |
| `editor.showPanel` | the panel `panel` in front; with `scripts: true` the Content Browser's Scripts root; with `search` the Hierarchy's search text (a name, `c:Light`, `t:Enemy`) | `StrataEditor/src/EditorLayer.cpp:177-192` |
| `editor.showDialog` | the dialog `dialog`: `export`, `newProject` (with `template`), `openSample` (with `sample`), `recovery`, `newScript`, `preferences` (with `section`), `externalEditor` or `about` | `StrataEditor/src/EditorLayer.cpp:233-243` |
| `selection.set` | the selected entities in the Inspector, or an asset in the Asset tab | `StrataEditor/src/Editor/EditorStateCommands.cpp:318-321` |
| `camera.set` | the Scene view's editor camera | `StrataEditor/src/Editor/EditorViewportCommands.cpp:1008-1011` |
| `viewport.setSettings` | the Scene view's overlays, debug view and canvas mode; the Game view's size | `StrataEditor/src/Editor/EditorViewportCommands.cpp:1109-1112` |

- `editor.showPanel` and `editor.showDialog` fail in an editor without a window, and `editor.showPanel` also while the
  launcher shows (`EditorLayer.cpp:212-215`, `:281-282`).
- The editor keeps its camera and the view settings in `<project>/.strata/EditorViewport.json`: it writes the file when
  the project closes and reads it when the project opens (`StrataEditor/src/Editor/EditorContext.cpp:387-391`,
  `:640-646`). A figure whose steps call `camera.set` or `viewport.setSettings` therefore gets a copy of its own, as a
  bake does (5.4), so that no later figure starts from its view.
- The `editor-ui` figure of UI scaling is the one editor figure at another scale: the same window at `--ui-scale 1` and
  at `--ui-scale 2` (the editor takes 0.5 to 4: `Strata/src/Strata/ImGui/ImGuiLayer.h:78-79`).

**Automation figures** (`automation`). Under 5.4's `--no-automation` the status bar's automation pill reads "Automation
off" in every editor figure (`StrataEditor/src/EditorLayer.cpp:2465-2468` at 319075e3). A recipe's `"automation": true`
leaves that option out, as a tutorial's `automation` does (6.2): the window serves on the free loopback port it picks
(`--automation-port` 0, `StrataEditor/src/EditorApplication.cpp:82`) and keeps its session file, with the token, in the
figure's new private session folder, which the tool never reads, prints or logs; the pill then reads "port <n> · no
agent" (`EditorLayer.cpp:2430-2434`). `"automation": {"client": "<name>"}` adds the agent the book's automation pages
teach: the tool starts the window without a script, then `StrataCLI mcp --project <copy> --timeout <ms>` with the same
session folder (and no `STRATA_EDITOR_PORT` or `STRATA_EDITOR_TOKEN`), sends it `initialize` with `clientInfo.name`
`<name>` (`StrataCLI/src/CLI/McpServer.cpp:410-415`), asks `tools/list` until the editor's tools appear, and sends every
step of the figure's script through the `strata_call` tool: `scene.loadStatus {wait: true}`, the scene opened, the
setup, `play`, the 120 frames waited for, `editorWindow.steps`, `editor.showPanel` of the panel, `editor.screenshot`,
then `editor.quit {force: true}`. The frames are waited for before `editorWindow.steps`, so that the Scene view's
outline of the agent's last edit, drawn for 0.6 s (`StrataEditor/src/Panels/ViewportPanel.h:57`), is still there at the
screenshot. The agent stays connected, so the pill reads "Agent connected · <name>" (`EditorLayer.cpp:2436-2440`), the
Activity panel lists its commands as the agent's, and the Scene view's chip names its last edit, "Agent: <command> ·
<age>" (`ViewportPanel.cpp:503-520`; queries leave the chip naming the edit, `CommandJournal.cpp:573-583`). An agent
drives one window, so `check` refuses `client` beside an `atStep`. No command opens the pill's tooltip, which needs the
pointer over it. `viewport.capture` draws the scene, not the editor's window, so these are `editor` figures.

**The samples' own pictures** (`make/samples`, `make/project-platformer`, `physics/why`). A sample commits
`Picture.png`, its project thumbnail at 480×270, and up to three PNGs in `Screenshots/`
(`Docs/DeveloperGuide.md:6461-6463`); the Showcase commits six. `publish` encodes only originals that `take` made
(5.7), so a figure that shows one of these views is a recipe like any other:

- The Showcase's `Screenshots/Shot1.png` to `Shot6.png` are the shots `showcase.shot1` to `showcase.shot6`. The
  generator's check holds its pictures to those shots' cameras (`Tools/GenerateShowcaseTerrain.py:2251-2265`); the
  scene is saved at Golden, and the `Setup` of shots 1 and 6, at Dawn and Dusk, begins with their station's steps
  (`:69-71`, `:2154`), so these recipes need no `station`. The committed files are 960×540 at High (`:87-88`).
- No script at the pin writes the other samples' pictures. Their recipes set the view, and the photographer judges
  each against the committed picture.

### 5.6 Identity rules and failures

- **`scene`:** the two captures of step 6 are the same picture: byte-identical, or (R57) no channel of any pixel differs
  by more than 1 level and at most 0.5 per cent of the pixels differ at all; the first capture is kept, and its stamp's
  `pairDifference` records the measured difference. On a larger mismatch the figure is taken once more in a fresh
  editor on a fresh copy. If the two captures differ again, the figure is **nondeterministic**: it is not published,
  `<work>/nondeterministic/<figure>/` keeps both pairs and their results, and the planner reports it to the engine with
  the images. Stills are deterministic by design: each capture releases its targets, history and GI
  (`SceneRenderer::ReleaseRenderTargets`). The Developer Guide records repeat differences of GTAO and the screen-space
  reflections after shader recompiles (`Docs/DeveloperGuide.md:5046-5062`); this rule catches them.
- **`live`:** three takes, each in a fresh editor on a fresh copy. For every image index, `fixedSteps` is equal across
  the takes, and so is `camera`. The first take's last frame is the original; the photographer judges it by eye beside
  the other takes' frames, kept in `<work>/live/<picture>/`, and takes the figure again when they disagree.
- **`editor`, `runtime`, `tool`:** judged by eye against `shows`. A runtime figure also needs exit code 0.
- **`text`:** two runs give the same text after `keep` and `redact`. A text of timings cannot repeat, so its recipe's
  `measured` names them (pointers inside `keep` of a command's answer, regular expressions of a program's output): the
  two runs are compared without them, the first run's values are published, and the caption says they are one run's
  measurements (R57; `check` refuses a caption without "one run").
- **`reference`:** two runs give byte-identical images.

`take` writes, under `--work`:

- `shots/<part>.<chapter>.<figure>[.<variant>].png`, the originals; `crops/<same>-<crop>.png`, cut at the original's
  own pixels, never resampled. The two folders follow LookDev's capture-set layout, so `LookDev.py compare` reads them.
- `results/<same>.json`: the capture's result without `Image`.
- `text/<same>.txt`; `log/`, every command the tool ran and every program's output.
- `taken-pending.json`: per picture, the SHA-256 of the original, the pin, the build (recorded as stamps record it,
  6.4), the GPU and OS that
  `editor.status {sections: ["editor"]}` and `["engine"]` report, and the values `record` names.

`take` fails (exit 1) when a figure fails a step, comes back incomplete or nondeterministic, or when the three live
takes differ in their fixed steps; it skips, and reports, figures with `waitsFor`. Preflight failures exit 2.

### 5.7 Publishing, comparing, archiving, filling

```text
python -I tools/figures.py compare --after <work dir> --output <dir>
python -I tools/figures.py publish --from <work dir> [--figures <glob>]
python -I tools/figures.py archive --tag <tag>
python -I tools/figures.py fill    [pages...]
python -I tools/figures.py list    [--waits]
python -I tools/figures.py labs    [labs...]
node scripts/encode-figures.mjs encode --publish <lossy|lossless> [--quality <n>] <png> <output>
node scripts/encode-figures.mjs diff <published file> <published file>
```

This section is the contract of the picture files; site.md "Pictures" repeats its names and decides what the site
serves.

- **`compare`** lays out the originals that the current stamps name (from `originals/`, below) as a LookDev capture set
  beside the new take in `<work dir>`, and runs `python -I <engine>/Tools/LookDev.py compare <before> <after> --output
  <dir>` on the two: differing pixels per picture, signed difference images and the crops side by side
  (`Tools/LookDev.py:1151`). The output must be outside the clone's tracked tree. The photographer reads it.
- **`publish`** encodes each original as its recipe's `publish` says: `lossy` as AVIF (quality 80, chroma 4:4:4; both
  sides of a `::compare` at quality 90), `lossless` as lossless WebP. Crops are always lossless WebP; `editor` and
  `tool` pictures are lossless WebP unless the recipe says `lossy`, then AVIF at quality 90 (`critique/rulings-13.md`,
  R59); renders (`scene`, `live`, `runtime`, `reference`) are `lossy` unless the recipe says `lossless`.
  Renders of parts `image`, `indirect` and `light` must state it, because dither, grain, banding, aliasing, crawl and
  noise are what lossy encoding smears. Nothing is resized, and a crop is never resampled. Python's standard library
  cannot encode AVIF or WebP, so `publish` calls the site's pinned `sharp` (0.35.5) through
  `node scripts/encode-figures.mjs encode`, which the tool builder writes; its `diff` mode decodes two published files
  and prints the mean absolute difference over all pixels and channels and the largest mean over a 16×16 block.
  (spike: the spike's build encodes AVIF and WebP in `src/lib/images.mjs` from a committed WebP; site.md decides the
  sizes the site serves.)
- `publish` writes into `src/assets/figures/<part>/<chapter>/`: the published files, `taken.json` and
  `<figure>[-<variant>].result.json` (the capture's result, for the reviewer and for the numbers in captions).
  `taken.json` records, per published file: the pin and the build (as stamps record them, 6.4), the GPU and the OS, the
  size, the SHA-256 of the PNG original the file was encoded from and of the published file, the encoder settings and
  sharp's version, the recorded values and, for a "before" picture, the baseline set (5.5).
- **Only what a page places is published.** A variant's picture is published when a `::figure{id=… variant=…}` or a
  side of a `::compare` shows it, a crop when a `::figure{id=… crop=…}` does; text figures and drawings are published
  whole. `publish` skips the others, a reader never meets them, and `check` refuses a published file, a stamp or a
  `.result.json` that no page places. `take` still cuts every crop, for the photographer to judge.
- **Names.** Published files are named `<figure>[-<variant>][-<crop>].<avif|webp>`, where `<crop>` is the crop's
  `name` in the recipe (5.2), and `taken.json` names them. A committed name carries no hash: the site's build serves
  each file under a name with the first 10 hex digits of its SHA-256 (site.md, "Pictures"; spike:
  `src/lib/images.mjs`). (spike: `taken` lives in the recipe, and a recipe has one crop, named `-crop`.)
- **Originals.** `publish` copies every PNG it encodes, the originals of `shots/` and the crops of `crops/`, into
  `originals/<sha256>.png` in the docs clone, named by the PNG's own SHA-256. The folder is ignored (site.md, "Layout of
  the repository"), never committed, and never emptied by a run: the work folder of a take is kept only until the next
  run (section 2), but the original of every published file stays.
- **Retakes.** A retake whose original has the SHA-256 that `taken.json` records keeps the published file and its hashes,
  and its stamp takes the retake's pin, build, OS, GPU, recorded values, pair difference and renderer (and the pin leaves
  `checkedAt`): the stamp says at which pin and on which machine the picture was last made and what that take measured,
  so a picture retaken equal at a new pin is current there (`publish` prints it as restamped). A retake that
  differs is encoded with the recipe's settings and compared with the committed file through `diff`; site.md
  ("Pictures") gives the threshold. Above it, the figure is a candidate: the photographer judges it, with `compare`'s
  images, and an accepted candidate replaces the published file and its stamp. Below it, the committed file and the
  stamp's hashes stay, and the stamp records the engine commit at which the picture was checked.
- `publish` fails when an original is missing, when its SHA-256 differs from `taken-pending.json`, or when the encoder
  is missing.
- Diagrams (`diagram`) are published as their SVG files, unchanged.
- **`archive --tag <tag>`** packs every original that a stamp names, from `originals/`, into
  `release/strata-engine-docs-originals-<tag>.tar`, and fails when one is missing or the archive is larger than 1 GB.
  It writes the archive's SHA-256 into a `.sha256` file beside it. The integrator moves both files out of the
  clone, and the owner attaches them to this repository's release (site.md, "Pictures" and "What a release
  holds"; `critique/rulings-6.md`, R26). A machine that lacks an original reads it from that archive. Originals
  are never committed.
- **`fill`** copies text figures into the fences that show them, ```` ```text capture="<figure id>" ````; `check`
  compares them (new: the spike has no text figures).
- **`list`** prints every figure and its state: taken, placeholder, missing, blocked, or waiting for an addition (spike: `list`
  exists). `--waits` groups the figures by the engine addition they wait for: the request list the engine's agents
  receive (section 11).
- **`labs`** writes each lab's download, `public/downloads/labs/<name>.zip`: `<name>.json`, the files of
  `labs/<name>/`, and, when it holds a file that `labs/CREDITS.md` credits, a `CREDITS.md` with those entries
  (`critique/rulings-6.md`, R21, R22, R25). The reader unpacks it, copies the files into the project's asset folder and
  runs the script, as 5.5 says.

### 5.8 `tools/figures.py check` (offline)

```text
python -I tools/figures.py check [--release] --engine <clone> --dumps reference/_dumps/<pin> [--baselines <dir>]
```

(spike: the command is `validate`; it becomes `check`, the name process.md's pilot uses.)

`check` runs without an editor. It reads the manifests, the pages, the dumps (section 7) and, through `--engine`,
Shots.json, `LookDevScene.json`, the lab scripts and the sample scenes at the pin. It fails (exit 1) on:

- a manifest against its schema; a duplicate `id`; a manifest without its page; a `::figure` or `::compare` that names
  no entry, or a variant that does not exist, or a `::compare` of a recipe without two variants (spike);
- a `shot` missing from Shots.json, or whose `Project` does not match `project`; a shot with `Camera: "editor"`; a
  `camera` of `"editor"`; `camera` or `crops` beside `shot`;
- a `scene` that does not exist at the pin: in the sample (`Samples/<id>/Assets/<scene>`), among the scenes
  `LookDevScene.json` saves, `Scenes/Main.stscene` for basic3d, or among the scenes a lab saves;
- an `entityName` that the scene document at the pin (or the script that makes the scene) does not hold exactly once as
  an entity's `Name`;
- a `debugView` outside the `debugView` enum of `viewport.capture` in the commands dump; a `quality` preset outside its
  `quality` enum; a `custom` field that the `Renderer.Quality` schema of the settings dump lacks; a `postProcess` key
  that is not a property of `PostProcess` in the components dump, or a value outside its options or range;
- `renderer` switches that the `renderer` parameter of `viewport.capture` in the commands dump lacks, or values its schema refuses;
  `renderer` on a figure that is no `scene` figure, or at a pin whose capture takes none; a `setup` step `viewport.capture`
  with `renderer`;
- `editorWindow.launcher` beside `project`, `scene`, `station`, `world`, `setup`, `play` or `files`; an editor figure with
  neither `project` nor `launcher`;
- an absolute path among a program's `arguments`, or one that leaves the run folder of a program with `files`; a recipe
  that names the user's home folder;
- a `live` recipe without `camera: "scene"`, or with `debugView`, `overlays`, `waitForAssets` or `renderer`, which live captures
  refuse; one without `play`, or whose `play` runs fewer steps than `live.atFixedStep`;
- a `runtime` recipe with a field the exported game cannot take (5.2), or `seconds` that are not whole;
- `automation` on a figure that is no `editor` figure, or `automation.client` beside an `atStep`; `blocked` beside
  `waitsFor`;
- a figure its page does not place (`::figure`, `:::figure`, `::compare` or a text fence), unless it waits or is blocked
  and the page places its `standIn` or its `noStandIn` says why the page shows none; a page that places a figure that
  waits or is blocked and has a stand-in; a `standIn` that is no figure of the manifest, is not made itself, or is not
  placed; `standIn` or `noStandIn` on a figure that a take makes;
- a `size` outside 16 to 4096; a crop outside 0 to 1, or with `x0 ≥ x1` or `y0 ≥ y1`; a `scale` outside 1 to 8;
- a variant that sets a field variants may not set; fewer than two variants;
- a `record` pointer that is not a pointer into the capture's result; a caption number written neither as
  `{stats.…}` nor explained by `numbers`; a `{stats.<name>}` that `record` lacks;
- a render of parts `image`, `indirect` or `light` without `publish`;
- a `relax` pointer outside the complete set, or without a reason;
- a `waitsFor` that names an addition the pin already has;
- a `baseline` without `shot`, a set other than the three of 5.5, or, with `--baselines`, a missing baseline file;
- `files` on a figure that is no `editor` or `scene` figure or `text` figure of a program (or with `atStep` on one), a file the book lacks or outside `tutorials/`, over 10 MB,
  a target outside the project, a `stage` the page's tutorial lacks, an `atStep` past the figure's steps or, in an editor
  figure, beside `play`;
- a lab that is missing, that holds keys other than the engine's, a command that the commands dump lacks, an absolute
  path or a placeholder; a lab whose download is missing or holds other files than `labs` writes;
- a published file that no recipe promises, or whose size or SHA-256 differs from `taken.json` (spike).

Pictures not taken yet, placeholders and missing stamps are notes in a draft and errors with `--release` (spike). So is
a missing layout (`editorWindow.layout`, made by `figures.py layout`), but not of a figure that is blocked or waits: no
take makes it at the pin, its stand-in stands in its place, and its layout is a note in a release too. A figure that is blocked or waits is
itself a note in a release, and so are its files not taken: at the final pin it keeps its `waitsFor` or `blocked`
(`critique/rulings-12.md`, R55).

`reference/figures` is generated from the manifests and `taken.json`: every picture, what it shows, its recipe, and the
GPU it was taken on. The GPU-driven path never ran on the CI's GPUs, and thumbnails force the CPU path
(`SceneRenderer.cpp:248-251`); a figure of the shadow cascade cache, which works on the GPU-driven path only, has
`"expectAlso": {"/renderStats/gpuDriven": {"equals": true}}`.

## 6. Tutorials

### 6.1 Why a book format

A tutorial cannot be a plain engine command script:

- the loader refuses every key but `command`, `parameters`, `expect`, `bind` and `until`
  (`EditorCommandRunner.cpp:431-433`), so step numbers, file copies and the book's checks cannot live in it;
- `project.create` and `asset.import` take absolute paths (`EditorAssetCommands.cpp:279`, `:765-768`);
- no command writes a script's source: `script.create` writes a template (`StrataEditor/src/Editor/EditorScriptCommands.cpp:417`);
- the only templates are `empty` and `basic3d`, and a tutorial often starts where an earlier one ended;
- `expect` knows only `equals`, `min` and `max` (`EditorCommandRunner.h:79-81`), and `log.read` has no text filter
  (`EditorStateCommands.cpp:981-992`), so "the console says Hello" cannot be checked by the engine.

### 6.2 The format

`tutorials/<part>/<chapter>.tutorial.json`, checked against `tools/schemas/tutorial.schema.json`:

```json
{
  "page": "make/first-script",
  "startsFrom": { "template": "basic3d" },
  "stages": [
    {
      "step": 3,
      "files": [ { "from": "book:tutorials/make/first-script/Spinner.cpp", "to": "Scripts/Spinner.cpp" } ],
      "commands": [
        { "command": "script.build", "expect": { "/success": { "equals": true } },
          "checks": [ { "pointer": "/diagnostics", "length": 0 } ] }
      ]
    },
    {
      "step": 4,
      "commands": [
        { "command": "entity.create", "bind": { "cube": "/id" },
          "parameters": { "name": "Cube", "components": { "MeshRenderer": { "Mesh": "Builtin/Cube" } } } },
        { "command": "script.add",
          "parameters": { "entity": { "$ref": "cube" }, "class": "Spinner", "fields": { "DegreesPerSecond": 45 } } },
        { "command": "play.start", "parameters": { "paused": true } },
        { "command": "play.step", "parameters": { "steps": 60 }, "expect": { "/stepsRun": { "equals": 60 } } },
        { "command": "component.get", "parameters": { "entity": { "$ref": "cube" }, "component": "Transform" },
          "checks": [ { "pointer": "/values/Rotation/1", "approx": 0.3827, "tolerance": 0.01 } ] },
        { "command": "play.stop" }
      ],
      "endState": true
    }
  ]
}
```

(`Rotation` reads back as a quaternion `[x, y, z, w]`, `Strata/src/Strata/Reflection/PropertyJson.cpp:350-354`: a
45° turn about the vertical axis gives `y = sin 22.5° ≈ 0.3827`.)

| Key | Values | Meaning |
| --- | --- | --- |
| `page` | the page's id | |
| `startsFrom` | `{"template": "empty" or "basic3d"}`, `{"sample": "<id>"}`, `{"tutorial": "<page id>"}`, `{"tutorial": "<page id>", "exercise": <n>}` (that tutorial, then its `exercise-<n>.patch`; `tutorials.py check` fails when the patch is missing), or `{"pin": true}` (patch tutorials, 6.6) | the runner makes the project with `project.create` or `project.openSample` in `@PROJECT@` (new projects have `Scripts/CMakeLists.txt`: `script.init`, `EditorScriptCommands.cpp:394`), or replays that tutorial first (its stages, from its own start) |
| `stages[].step` | the stage's number: 1, 2, 3 and so on in page order, equal to the `stage` of the `::checkpoint{stage=…}` that ends the stage's section (style.md §7.4) | not the number of a list item: every section's list of steps counts from 1 again |
| `stages[].files` | `[{"from": "<path>", "to": "<path in the project>"}]` | copied into the project before the stage's commands. `from` is `book:tutorials/…` (the tutorial's own files and `tutorials/assets/`) or an engine path under `Samples/*/Assets/` at the pin; `to` is relative to the project, without `..` |
| `stages[].setup` | command steps that need an absolute path: only `asset.import` | the runner fills the placeholders; the page shows them as UI steps (dragging a file into the Content Browser) |
| `stages[].commands` | command steps, as in 5.2, plus `checks` and `files` | run in order; a command's `files` (the form of `stages[].files`) are copied just before it, once the outputs of the commands before it are older, so a build error and its fix, a hot reload or a crash inside one stage runs step by step; the reader's copy then runs part by part in new editors, the files copied between the parts, so neither a `$ref` nor the editor's state (play mode, a crash) reaches across them: `checks`, which the reader's copy leaves out, test what does |
| `checks` on a command | `{"pointer", "contains": "<text>"}`, `{"pointer", "approx": n, "tolerance": t}`, `{"pointer", "length": n}`, `{"pointer", "equals": v}` | the book's checks on the command's full result; `contains` on an array means one element's text contains it (so `log.read` entries can be searched) |
| `stages[].endState` | `true` or absent | the runner publishes the project as it is after this stage (6.4) |
| `patch` | 6.6 | for tutorials that change the engine |

- Placeholders: `@PROJECT@` (the project's absolute folder), `@BOOK@` (the absolute folder of this repository),
  `@WORK@` (the run's work folder), `@RELEASE@` (the folder of the release the tutorial runs against, `--build`, which
  holds `Samples/`). They may appear only in `setup` and are filled by the runner.
- `commands` hold no placeholder and no absolute path; assets are named by their path in the project. The one exception
  is a file or folder `asset.import` takes from the release, `@RELEASE@/Samples/<sample>/Assets/…`, as the page's
  command imports it; the reader's copy writes `<release folder>` there, as pages do. A tutorial imports what its page
  imports, never copying it into `Assets/` behind the editor's back.
- `"automation": true` (that file only) runs its reader's copies in an editor without `--no-automation`, which serves on
  the free loopback port it picks and keeps its token in the run's private session folder, never read, printed or logged
  by the run, for pages that teach what an agent sees of the automation server (`automation/agents`).
- A `$ref` names a value bound earlier in the same stage. A stage that needs an entity of an earlier stage finds it
  again with `entityName`, so each stage runs on its own.
- Game time is counted in fixed steps: `play.step {steps}`, `input.sequence {steps}` or `until {steps}`; never
  `editor.wait` frames. A step with `until` is a query with an `expect` (`EditorCommandRunner.h:91-98`). In a run,
  `until` also asks again after a failing answer (`asset.info` of an asset not registered yet) and, out of time, fails
  with the last error; the engine's runner stops at one, so a reader's copy never relies on it.
- The assets a tutorial imports come from the release's `Samples/*/Assets` (CC0 or CC BY, credited in the sample's
  `CREDITS.md`) or from `tutorials/assets/`, which has its own `CREDITS.md`. Every page names the file it imports.
- Script code a tutorial shows lives in `tutorials/<part>/<chapter>/` as real files, built by the editor's own script
  build during the run; the page quotes them with `src="book:…"`.
- Exercise solutions are checked the same way: a sketch with its expected output (section 4), an editor exercise as
  `tutorials/<part>/<chapter>/exercise-<n>.tutorial.json`, an engine exercise as
  `tutorials/<part>/<chapter>/exercise-<n>.patch` (6.6). Code exercises are judged by these runs, not by a reviewer
  (process.md). The reader gets a sketch in full on the page and the other two as downloads (6.3, `compile`).
- (spike) The spike's `tutorials/make/first-script.commands.json` is a plain command script that calls `project.create`
  with a placeholder and binds across the whole script; it is rewritten in this format.

### 6.3 `tools/tutorials.py`

```text
python -I tools/tutorials.py check   [--release] --dumps reference/_dumps/<pin> [pages...]
python -I tools/tutorials.py compile [pages...]
python <engine>/Tools/PerfLock.py --label docs-tutorials --limit 90 -- python -I tools/tutorials.py run
    --engine <clone> --build <bin> [--work <dir>] [--record-examples] [--pictures] [pages...]
python <engine>/Tools/PerfLock.py --label docs-patch --limit 180 -- python -I tools/tutorials.py patch
    --engine <clone> --build-dir <clone>/build/docs-patch [pages...]
```

**`compile`** writes, per stage that a page offers, the reader's copy of its `commands` as an engine command script:
`public/downloads/tutorials/<part>/<chapter>/stage-<step>.commands.json`. A page offers the stages its `::checkpoint`
directives name; a how-to, which has none, its last stage, whose downloads the build draws at the end of its
`## Result` (site.md, "Directives"); no other page offers a stage. A reader never meets the other stages' downloads,
so `compile` and `run` make none (`run` zips only an offered stage with `endState`), `compile` removes them, `check`
refuses them, and a stamp's input that is such a download is no longer needed. `entityName` becomes an `entity.find` step
that binds the first match; `checks` are left out; `expect`, `bind` and `until` stay. A reader runs it on their project
after the stage's files and setup steps: `StrataEditor --project <their project> --commands <file>`.

`compile` also writes the downloads of the patches and the worked solutions, so that nothing a reader needs lives
only in this repository (`critique/rulings-6.md`, R25):

- per patch tutorial (6.6), a copy of its `patch.file`: `public/downloads/tutorials/<part>/<chapter>.patch`;
- per editor exercise whose answer names it (`solution="tutorials/<page>/exercise-<n>.tutorial.json"`, which links the
  download: `src/plugins/answers.mjs`), `public/downloads/solutions/<part>/<chapter>/exercise-<n>.zip`: the reader's copy of each
  stage, made as above, the files its stages copy, and, when one of them is a CC BY file, a `CREDITS.md` with its
  entry;
- per engine exercise whose answer names it, a copy of its patch: `public/downloads/solutions/<part>/<chapter>/exercise-<n>.patch`.

A solution no answer names gets no download (its file still runs as a check); `compile` removes one made before, and
`check` refuses it.

A sketch solution has no download: the answer shows it in full with its output (section 4; style.md §8).

**`run`**, per tutorial:

1. A new work folder; `StrataCLI launch --no-gpu --idle-timeout 900` (no project); preflight check 4.
2. `startsFrom`: `project.create {directory: @PROJECT@, name, template}`, `project.openSample {sample, directory:
   @PROJECT@}`, or the earlier tutorial's end state. End states are cached in `--work`, keyed by the SHA-256 of the
   tutorial files of the chain and the pin, so a chain of tutorials replays each one once.
3. Per stage: copy `files`; run `setup` with the placeholders filled; save a copy of the project (the stage's start
   state); run each command through `StrataCLI call`, after copying its `files`, with `@RELEASE@` filled. The runner
   applies the engine's step rules as `EditorCommandRunner.h:74-98` states them: `bind` and `$ref` with `pointer`; `expect` with `equals`, `min` and
   `max`; `until {steps, seconds}`, repeating the query, with one `play.step {steps: 1}` between attempts in a paused
   game and one `editor.wait {frames: 1}` otherwise, counting fixed steps by `play.state`'s `fixedSteps`. It checks
   that every `entityName` matches exactly one entity, and evaluates `checks` on each full result.
4. `endState`: zip the project without `.strata/` into `public/downloads/tutorials/<part>/<chapter>/stage-<step>.zip`.
   A zip that holds a CC BY file also holds a `CREDITS.md` with that file's entry, copied from the sample's
   `CREDITS.md` at the pin or from `tutorials/assets/CREDITS.md` (`critique/rulings-6.md`, R21, R22). Tutorials that
   start from a sample publish no zip (the reader has the sample).
5. `editor.quit {force: true}`; each stage's reader copy runs in the engine's runner on the stage's start state, part
   by part when commands carry `files`.
6. The reader's copies run in the engine's own runner: per stage, on the saved start state,
   `StrataEditor --no-gpu --no-automation --project <copy> --commands <reader copy> --quit-after-commands --frames
   36000`, which must exit 0.
7. The stamp (6.4).

With `--record-examples`, `run` also writes the first passing result of each command, with IDs and paths replaced by
`…`, to `reference/_examples/<command>.json`: the example results of the commands table (section 7).

`run` fails (exit 1) when a step fails, an `expect` or a check is not met, an `entityName` matches no entity or
several, a reader copy fails in the engine's runner, or the build's `engineCommit` is not the pin's.

**`check`** (offline) fails (exit 1) on: the schema; a `startsFrom` chain that loops or names a tutorial that does not
exist; a `files.from` that does not exist; a `to` outside the project; a command that the commands dump lacks, or
parameters that do not validate against its schema (a `$ref` is accepted for any value); an `until` on a command whose
kind is not `Query` or that has no `expect`; `editor.wait` in `commands`; a placeholder or absolute path in `commands`;
a `setup` step other than `asset.import`; a `$ref` to a name the stage has not bound; a malformed check; a reader copy,
a patch download or a solution download whose contents differ from what `compile` writes; a zip that holds a CC BY
file without its `CREDITS.md`; a zip over 10 MB, or zips of all tutorials over 150 MB together. A stamp that
is missing or not current is a note in a draft and an error with `--release` (spike: `tools/pages.py` checks the old
stamps).

### 6.4 Stamps

`tutorials/<part>/<chapter>.stamp.json`, written only by `tutorials.py`:

```json
{
  "page": "make/first-script",
  "runs": [
    { "build": { "kind": "pin-build", "configuration": "Release", "editorSha256": "<SHA-256 of StrataEditor.exe>" },
      "engineCommit": "<the full pin>", "reportedCommit": "<12 hex digits from editor.status>",
      "os": "<platform from editor.status>", "gpu": null,
      "inputs": { "tutorials/make/first-script.tutorial.json": "<SHA-256>",
                  "tutorials/make/first-script/Spinner.cpp": "<SHA-256>",
                  "public/downloads/tutorials/make/first-script/stage-4.commands.json": "<SHA-256>" },
      "stages": [ { "step": 3, "passed": true }, { "step": 4, "passed": true } ],
      "readerCopies": true,
      "passed": true }
  ]
}
```

- `inputs` holds the SHA-256 of the tutorial file, of every file it copies, of every reader copy, and of the patches
  for patch tutorials.
- `build.kind` is `pin-build`, `package` (with the archive's name and SHA-256) or `patch-build`.
- A stamp is **current** when a run with `build.kind` `pin-build` (or `patch-build`) passed at the pin with the inputs
  as they are now, and, at a release pin, a `package` run passed too.
- (spike: a stamp holds `engine`, `sha256` and `passed`; `tools/pages.py` reads that form.)

### 6.5 UI steps

Every tutorial step has a UI half and a command half (style.md). The commands are run by `tutorials.py run`. The UI
half is checked in two ways:

1. The names lint (section 8) checks every **Menu ▸ Item** path and every UI label of a step against the UI's names at
   the pin.
2. In phase B, `tutorials.py run --pictures` (with a GPU) makes a whole-editor picture after each stage, as 5.4 makes
   `editor` figures, from the stage's start state and the stage's reader copy, into `<work>/ui-steps/<page>/
   stage-<step>.png`. The photographer judges each picture against the step's text and writes the verdict in the
   page's review file. These pictures are published only when a recipe asks for them. A tutorial that changes the
   engine gets them from `tutorials.py patch`, with the patched editor, when its file sets `patch.pictures` (6.6).

No agent controls the owner's screen. The owner is invited to walk one tutorial by hand in a windowed editor; the book
does not wait for it. A step that only a command can do says so on the page, and the part's brief lists such steps.

### 6.6 The patch runner: tutorials that change the engine

Pages such as `core/first-change`, `world/tutorial-component`, `gpu/first-triangle`, `image/tutorial-post-effect`,
`scripting/tutorial-host-function`, `editor/tutorial-command`, `capstone/plan`, `capstone/build` and `capstone/land`
change the engine's tree. `capstone/plan`'s patch adds only the WindZone's spec, a document under `Docs/Plans/` in
the form of the engine's own specs (`Docs/Plans/Wave8/specs/`). Their tutorial file has a `patch` key:

```json
{
  "page": "world/tutorial-component",
  "startsFrom": { "pin": true },
  "patch": { "file": "tutorials/world/tutorial-component.patch", "tests": [ "Physics.WindZone" ] }
}
```

- `patch.file` is a unified diff against the pin (`git diff` format). `startsFrom` is `{"pin": true}` or
  `{"tutorial": "<page id>"}`, whose patch is applied first. The WindZone's chain is one line, each link starting
  from the one before: `world/tutorial-component`, the solution of `gpu/debug-drawing`'s exercise, which gives the
  WindZone its gizmo (its `exercise-<n>.patch`, 6.2; book.md, "Running examples"), `scripting/tutorial-host-function`,
  `editor/tutorial-command`, `capstone/plan`, `capstone/build`, `capstone/land` (`critique/rulings-7.md`, R30 and
  R32).
- `patch.tests` names the doctest suites the page names. The WindZone's suite is `Physics.WindZone`: the component
  is the Physics module's, and the engine names suites after their module (`AGENTS.md:103`).
  `editor/tutorial-command` names `CLI.McpToolsets` too, since it adds the `wind.` prefix to the MCP toolset table
  (`StrataCLI/src/CLI/McpToolsets.cpp:43-54`; the suite: `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:26`).
- `patch.pictures`, optional: `true` when the page shows the patched editor (`world/tutorial-component` opens it in
  its step 2). The runner then builds `StrataEditor` and makes the pictures of the page's UI steps with it (step 4
  and step 5 below).
- `patch.experiment`, optional: `{"file": "<patch>", "fails": "<doctest suite>"}`, a change that the page makes to
  show a failure and then takes back, such as `capstone/plan`'s include of `Strata/Physics/PhysicsComponents.h` from a
  file of the Scripting layer, which `Architecture.Layering` refuses. Its suite must fail, and its output is what the
  page shows.
- The page quotes hunks with `src="book:tutorials/<part>/<chapter>.patch#hunk-<n>"`; the reader applies the whole
  patch from its download (6.3, `compile`).

`tutorials.py patch` runs in phase B, on the machine with the GPU, under the perf lock with a 180-minute limit:

1. Preflight (1.4, checks 1 and 2).
2. `git -C <clone> apply --check <patch>`, then `git -C <clone> apply <patch>`, for every patch of the chain in order.
3. `cmake --preset windows -B build/docs-patch` in the clone, after every apply and, when the chain adds or removes
   files, again after the revert (step 6): the engine collects its sources with `CONFIGURE_DEPENDS` globs, and a build
   that reconfigured itself would do so after MSBuild loaded the old projects. The folder is kept, so later builds are
   incremental. It is never the pin build's folder, so the pin build never holds patched code.
4. `cmake --build build/docs-patch --config Release --parallel 2 --target StrataTests -- /p:CL_MPCount=4`, plus
   the targets `StrataEditor`, `StrataRuntime` and `StrataCLI` when the chain changes files under `StrataEditor/`,
   `StrataRuntime/` or `StrataCLI/`, and the target `StrataEditor` when the tutorial file has `patch.pictures`.
   `STRATA_WARNINGS_AS_ERRORS` is on by default (`CMakeLists.txt:24`), as in CI.
5. `build/docs-patch/bin/Release/StrataTests.exe --test-suite=Architecture.Layering`; the same with each suite of
   `patch.tests` (for an engine exercise: its page's, then those its page's tutorial file names for it,
   `"exercises": {"<n>": {"tests": [...]}}`); `ctest --test-dir build/docs-patch -C Release -R
   "^StrataTests\.FeatureTest$"`. With `patch.pictures`, the pictures of the page's UI steps, made as 6.5 makes them, with the editor of
   `build/docs-patch`. With `patch.experiment`: `git -C <clone> apply` its patch, build `StrataTests` again, run its
   suite, which must fail, keep the suite's output for the page, and `git -C <clone> apply -R` the experiment's patch.
6. `git -C <clone> apply -R <patch>` for every patch, in reverse order; then the clean check of 1.3.
7. The stamp, with `build.kind` `patch-build` and the doctest and CTest results.

- The runner never skips a test. So a patch that adds something the feature test counts (a component, a script API, a
  command) also adds its feature-test exercise, as the engine's own rules require; `world/tutorial-component` teaches
  that step for WindZone, and the capstone extends it.
- `patch` fails (exit 1) when a patch does not apply, the configure or a build fails, a test fails, or the suite of
  `patch.experiment` passes: it is the one run that must fail. When the revert fails, the clone stays dirty and every
  other tool's preflight refuses it until a person restores it; the runner says so and exits 2.

## 7. Generated reference

### 7.1 Routes

The engine has no listing for most tables, so each table has a route: a command dump, a parse of the source at the
pin, or both; the terms and the further reading are built from the book's own files. Commands run in a `--no-gpu`
editor (7.2); parsing reads the pin clone.

| Table | Route | Source at 822a7a46 |
| --- | --- | --- |
| commands | `editor.commands`: name, description, parameter schema, kind. Parsed: `MayDefer`, `WaitsForAssets` and `Results` of each registration, and the MCP toolset of each command. There is no result schema: the table shows the result as the description states it, with an example result recorded by a tutorial run (`reference/_examples/`) | `StrataEditor/src/Editor/EditorCommands.cpp:66-79`, `EditorCommands.h:87-106`; `StrataCLI/src/CLI/McpToolsets.cpp` |
| components | `component.list`: name, displayName, category, description, addable, and per property Name, DisplayName, Type, Description, Section, Min, Max, AssetType, Options, ReadOnly, PhysicsLayer. Defaults from the defaults dump (7.2). Inactive reasons parsed from the `SetInactiveReason` calls. Hidden and `NoSerialize` components, and hidden or transient properties, which `component.list` leaves out, are listed from the source | `StrataEditor/src/Editor/Commands/EntityCommands.cpp:613-626`; `Strata/src/Strata/Reflection/PropertyJson.cpp:488-517`; `ComponentRegistry.h:253-258` |
| settings | `project.settings` on a new `empty` project, using each field's `default`, never `value` | `StrataEditor/src/Editor/EditorProjectSettingsCommands.cpp:207`; `Strata/src/Strata/Core/SettingsRegistry.cpp:260` |
| preferences | `preferences.get`, using `default` only | `StrataEditor/src/Editor/EditorPreferencesCommands.cpp:77` |
| asset types and importers | parsed: the `AssetType` enum, and each importer's `GetVersion() const override { return N; }`; from v0.8.1, `asset.types` (section 11) | `Strata/src/Strata/Asset/AssetTypes.h:14-31`; `TextureImporter.h:89`, `GltfImporter.h:39`, `ColorLookupImporter.h:49`, `AssetImporters.cpp:47`, `:92`, `:146` |
| quality rows and presets | parsed: the lines `c_<Row>Row = { Low, Medium, High, Ultra }`, joined with the `Renderer.Quality` schema of the settings dump | `Strata/src/Strata/Renderer/RendererQuality.cpp:39-55`, `:728` |
| debug views | the `debugView` enum of `viewport.capture` in the commands dump | `EditorViewportCommands.cpp:147-151` |
| GPU stages | parsed: the names passed to `RegisterGPUStage` and to `RegisterStage(…, FrameStageKind::GPU)` | `Strata/src/Strata/Renderer/GPUProfiler.cpp:37-66`; `GameUIRenderer.cpp:62`; `ImGuiLayer.cpp:142` |
| CPU stages | parsed: the built-in stages, the names passed to `ST_PROFILE_STAGE` and to `RegisterStage` without `FrameStageKind::GPU`, and the `ProfileStage` of each scene system's descriptor, each with the file that times it | `Strata/src/Strata/Core/FrameProfiler.h:67-81`; `Strata/src/Strata/Core/Profiling.h:39-42`; `Strata/src/Strata/Scene/SceneSystem.h:88`; `GameUIRenderer.cpp:72` |
| render statistics | parsed: the keys of the `renderStats` object | `StrataEditor/src/Editor/EditorStateCommands.cpp:228-292` |
| renderer specification and statistics | parsed: the fields of `SceneRendererSpecification` and `SceneRendererStats` | `Strata/src/Strata/Renderer/SceneRenderer.h:127`, `:509` |
| runtime perf log | parsed: the columns of `FramePerfLog` and of `MakePerfLogColumns` | `Strata/src/Strata/Runtime/FramePerfLog.h`; `GameRenderer.cpp:178`; `GameRuntime.cpp:364` |
| program options | parsed: the `c_Arguments` arrays of the editor and the runtime, and the CLI's usage text | `StrataEditor/src/EditorApplication.cpp:64-80`; `StrataRuntime/src/RuntimeApplication.cpp:340-353`; `StrataCLI/src/CLI/CliApplication.cpp:570-625` |
| script API | parsed: the members of `StrataScriptHostAPI` in declaration order (the ABI's append order); the members of `StrataScriptClassDesc`; the SDK's classes and functions by the rules of `SDKReader` (its tokenizer and scope tracking), keeping the `//` comments; the macros `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`; "added in" for each host function from `git log -S<name>` and the first release tag that contains that commit. `ST_SCRIPT_HOST_FUNCTIONS` is the engine's list, not the SDK's | `StrataScriptCore/Include/StrataScript/ScriptABI.h:312`, `:772`; `StrataTests/src/FeatureTest/SDKReader.h`; `Script.h:852`, `:857`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3431` |
| perf budgets | parsed; each budget also gives its keys `perf.<name>.…` of `values.json` (7.3) | `StrataTests/Perf/Budgets.json` |
| scene and world limits | parsed: the constants that `tools/reference-limits.json` lists as (file, name), such as `Scene::c_MaxEntities`, `WorldData::c_SupportedExtent`, `c_MaxBodyCoordinate`; every entry must resolve at the pin | `Strata/src/Strata/Scene/Scene.h:140`; `World/WorldAsset.h:89`; `Physics/PhysicsWorld.cpp:73` |
| asset budgets and statistics | the asset settings sections of the settings dump; the statistics `asset.stats` reports, from its description in the commands dump | |
| build | parsed: `option(` in `CMakeLists.txt` and `CMake/*.cmake`, the presets of `CMakePresets.json`, the CTest names and labels of `StrataTests/CMakeLists.txt`, the shards of `StrataTests/CoreShards.json` | |
| figures | `reference/figures` (5.8) | |
| terms | built from the book's own files after `excerpts.py fill`, for `reference/term-index`: each glossary entry's term, aliases, `home` and `use`, and each quote's `symbol` with the pages that quote it | `src/content/glossary.json` (section 9); the `symbol` attributes of the pages' quotes (3.1) |
| further reading | built from the book's own files, for `appendix/further-reading`: the `## Further reading` sections of the pages (style.md §6.3), by part | the pages |

The renderer's tables (quality rows, debug views, GPU stages, render statistics, the renderer specification) exist only
generated; no page holds a hand-written copy of them. Counts in prose come from the generated values (7.3) or from a
test that pins them, named in the page's notes (for example, `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:113`
checks that the `core` toolset has 27 commands; `CommandJournalTests.cpp:99-164` lists every command by kind).

### 7.2 `tools/reference.py`

```text
python <engine>/Tools/PerfLock.py --label docs-reference --limit 90 -- python -I tools/reference.py dump
    --engine <clone> --build <bin> [--work <dir>]
python -I tools/reference.py parse  --engine <clone>
python -I tools/reference.py render
python -I tools/reference.py check  --engine <clone>
```

**`dump`** starts one `--no-gpu` editor without a project and runs: `editor.status {sections: ["engine"]}` (preflight),
`editor.commands`, `preferences.get`, `project.templates`, `project.samples`, `project.create {directory:
<work>/Empty, name: "Empty", template: "empty"}`, `project.settings`, `component.list`, `scene.new {name: "Defaults"}`,
and, for each component whose `addable` is true: `entity.create {name: "Defaults"}`, `component.add {entity,
component}`, `entity.get {entity}`, `entity.delete {entity}`; then `editor.quit {force: true}`. It writes
`reference/_dumps/<pin>/{commands, preferences, templates, samples, settings, components, component-defaults}.json`,
each `{"pin": "<full pin>", "engineCommit": "<12 hex>", "command": "<name>", "result": …}`. A component that
`component.add` refuses is recorded with its error in `component-defaults.json`, and the table says why it has no
defaults. `dump` fails (exit 1) when a command other than those per-component steps fails; exit 2 on preflight. It runs
in phase A as soon as the pin build exists, and at every pin move.

**`parse`** reads the pin clone and writes `reference/_dumps/<pin>/parsed/*.json`: one file per parsed route of 7.1,
plus `ui-literals.json`, `paths.json`, `macros.json`, `tests.json` and `options.json`, which the names lint reads
(section 8). It fails when a route finds nothing where the pin has something (for example no `c_<Row>Row` line, or a
row with no field of that name in the `Renderer.Quality` schema).

**`render`** is pure Python: it reads the dumps, the parsed tables, `reference/_examples/` and
`tools/data/game-makers.json`, and, for the terms and the further reading, `src/content/glossary.json` and the pages;
so it runs after `excerpts.py fill`. It writes `src/generated/reference/<table>.md` and
`src/generated/reference/values.json`. The files are outside the docs collection; the reference pages include them
(site.md). Each file starts with
`<!-- generated by tools/reference.py render from engine <full pin>; do not edit -->`. Engine text is HTML-escaped.
Parameters are tables, with each schema in a collapsed block. The commands table is one file per command group, which
the one page `reference/commands` includes with prose of its own between them; when that page's estimated size would
exceed the largest page's budget, the render fails instead of splitting the page (`critique/rulings-13.md`, R59).

**`tools/data/game-makers.json`** chooses the rows of `reference/game-makers`, the cheat sheet for game makers: a
list, kept by hand, of the ids it shows, per table (commands, components, SDK names, runtime options). `render` takes
their facts from the dumps and the parsed tables (`critique/rulings-7.md`, R34).

**`check`** runs `parse` and `render` into a temporary folder and fails (exit 1) when the result differs from the
committed `parsed/` and `src/generated/reference/`, when a dump's `pin` is not `engine.pin`'s commit, when its
`engineCommit` is not a prefix of it, or when an id of `tools/data/game-makers.json` is in no dump or parsed table,
as after a pin move that removed it. CI runs `check`; generated files are committed, so the site builds without an
engine.

### 7.3 Generated values in prose

`values.json` is a flat map of keys to numbers or strings: `commands.count`, `components.count`,
`hostFunctions.count`, `debugViews.count`, `quality.<field>.<Low|Medium|High|Ultra>`, `importer.<type>.version`,
`limits.<name>`, `perf.<name>.<Measured|Budget|Unit>` for each budget `<name>` of `StrataTests/Perf/Budgets.json`
(an entry marked `Provisional` has no budget and gives no key), and the other keys `render` lists in its output. A
page writes `:value{key="commands.count"}`; the site's plugin replaces it and fails on an unknown key (site.md; not in
the spike). Pages marked W8r state no preset value in prose except through such a key.

## 8. The names lint

```text
python -I tools/names.py check [--release] --dumps reference/_dumps/<pin> --engine <clone> [pages...]
```

It reads the pages' prose and their JSON fences, the dumps, the parsed tables, and the trees of the pin and of the
vendor submodules. It prints `<page>:<line>: <form>: <name>: <reason>` and exits 1 on any finding. It is a writer's exit
check, a site check, and part of what the technical reviewer receives, together with the tutorial run logs and the
figures' `result.json` files.

| Form in the page | Must be | Checked against |
| --- | --- | --- |
| `` `<group>.<action>` `` where `<group>` is a command group of the dump | a registered command | `commands.json` |
| `` `<command> {…}` `` (a command and its parameters) | the command exists; every key is a property of its parameter schema; every value of a property with an `enum` is in it (debug views, quality presets, cameras) | `commands.json` |
| a JSON fence holding a command step or a list of them | the same, for each step | `commands.json` |
| `` `<Component>.<Property>` `` where `<Component>` is a registered component | the property exists | `components.json` |
| `` `<Property> = <value>` `` | a property of a component; an `Enum` value is one of its `Options`; a `Bool` value is `true` or `false` | `components.json` |
| `` `<A>.<B>` `` of two capitalized words | a settings or preferences section id, a doctest suite, or a CTest name | `settings.json`, `preferences.json`, `parsed/tests.json` |
| `` `<A>.<B>.<C>` `` of three capitalized words | a field of section `<A>.<B>`, a doctest suite (`Editor.UI.Dialogs`) or a CTest name (`StrataTests.Core.Scene`) | `settings.json`, `parsed/tests.json` |
| `` `ST_…` `` | a macro defined at the pin | `parsed/macros.json` |
| `` `<A>::<B>` `` | some file at the pin contains `<A>::<B>`, or a file that declares the class, struct or namespace `<A>` contains the identifier `<B>`, or the page's own sketches or tutorial files define it | the engine; `sketches/`; `tutorials/` |
| `` `StrataEditor --<option>` ``, `` `StrataRuntime --<option>` ``, `` `StrataCLI <command> --<option>` `` | an option of that program | `parsed/options.json` |
| an engine path in backticks (its first part is a top-level entry of the engine) | a file or folder of `git ls-tree -r <pin>`, or of the submodule's tree for `Strata/vendor/<lib>/…` | `parsed/paths.json`, the submodules |
| **Menu ▸ Item ▸ …** (a bold span with `▸`) | each part is a UI name | `parsed/ui-literals.json` |
| a bold span in a numbered step of a tutorial or how-to page that is not a glossary term | a UI name | `parsed/ui-literals.json` |

**UI names** are the union of:

- the C++ string literals of `StrataEditor/src/UI/`, `StrataEditor/src/Panels/` and `StrataEditor/src/EditorLayer.cpp`
  at the pin (adjacent literals joined, ImGui ID suffixes after `##` removed), such as `BeginMenu("File")`
  (`EditorLayer.cpp:1456`), `"Add Component"` (`Panels/InspectorPanel.cpp:448`) and `BeginMenu("Create Child")`
  (`Panels/SceneHierarchyPanel.cpp:929`);
- the names the UI shows from registries, which are not literals of those folders: the components' `displayName`s, the
  properties' `DisplayName`s and enum `Options` (component dump), the sections' and fields' titles (settings and
  preferences dumps), the template and sample names (`project.templates`, `project.samples`). "Add Component ▸ Script"
  needs the second list: "Script" is a component's display name.

Names the reader makes (their own scripts, classes and entities) are written as code, not in bold (style.md), so the
lint does not read them as UI names.

## 9. Glossary

`src/content/glossary.json`, in the spike's format: `{"terms": [{"term", "definition", "home", "use", "aliases",
"avoid"}]}`. `definition` is one sentence; `home` is the page that defines the term; `use` is optional, in the seed
as in the glossary: a page id, the term's use home in part `make`, which defines the term in a game maker's words
(book.md, "One home per concept", rule 5; style.md §3; `critique/rulings-7.md`, R33); `aliases` are other accepted
names; `avoid` are names the style linter flags (`tools/lint.py`, rule `other-name`, spike). Glossary links in pages
are explicit (site.md). (spike: entries have neither `id` nor `use`; site.md's explicit links name an `id`, so each
entry gains one, its term in lowercase words joined by `-`.)

- **The seed comes first.** Before the allocation starts, one agent writes the seed, 400 entries of a beginner's base
  vocabulary: the words the personas G0 and B0 do not have (book.md) and the topics of the `basics` primers. Examples,
  each with its home: variable (`basics/programming-1`), function and array (`basics/programming-2`), terminal, folder
  and path (`basics/tools`), byte (`basics/computer`), integer and floating point (`basics/numbers`), debugger
  (`basics/debugging`), probability (`basics/math-probability`), integral (`basics/math-change`). Every seed entry's
  home is a page of `start` or `basics` in the outline. Until the spike's verdict the seed is
  `plan/glossary/seed.json`, in this format; it then becomes `src/content/glossary.json`.
- **Then the inventories.** Their terms, about 1,590, are merged after the allocation, which gives each
  term its home page (`plan/allocation/README.md`). The merge makes one entry per term, one name per thing, and takes
  each entry's home in this order (`critique/rulings-7.md`, R33):
  1. a term the seed has keeps the seed's entry;
  2. a term of a `make` page that has a twin, the same term homed on another page, is one entry with the twin's
     page as its `home` and the `make` page as its `use` (book.md, rule 5);
  3. otherwise the home is the page of `book.md`'s one-home row, or, where no row names the concept, the page in the
     Needs closure of every page that marks the term (the principle of `critique/rulings-7.md`, R28).
- **Two meanings, two entries.** A word with two meanings gets two entries qualified by a word each ("pack block" and
  "BC block"), never one entry with two definitions, and the unqualified word is never a term of its own.
- **New terms** come through a chapter's notes; one admitter at a time adds them (process.md).
- **Checks:** `tools/pages.py check` (spike) fails on a home page that does not exist and on a duplicate term or alias;
  `tools/lint.py` (spike) flags a term used before its definition on its home page, a home page that never defines its
  term, and an `avoid` name.

## 10. Moving the pin

### 10.1 `tools/pin.py`

```text
python -I tools/pin.py show
python -I tools/pin.py report --engine <clone> [--to <commit>] [--dumps-to reference/_dumps/<new pin>]
python -I tools/pin.py move   --engine <clone> <commit> [--release <x.y.z>] [--prerelease yes|no]
```

(spike: the three commands exist.) The integrator runs `move` during a freeze, when no page pipeline is open
(process.md). `move` runs `relocate --write`, writes `engine.pin`, and exits 1 when anything needs a person, so the move
is not mistaken for a finished one (spike).

### 10.2 What `report` and `move` print

Per chapter and for the whole book:

1. Quotes: same, moved (updated by `move`), moved-file, changed, missing (3.5).
2. Tutorials to run again: all of them, since every stamp names the old pin; and the patch tutorials and engine
   exercises whose patch no longer applies at the new pin, each applied after the patches its chain applies before it,
   in order, as `tutorials.py patch` does (6.6: `git apply --cached` in an index file and an object folder of the
   report's own, so the clone is not touched). A chain that breaks at an earlier patch names that patch once, and the
   patches after it as not checked.
3. Pictures: all are taken again and compared with `figures.py compare`; the report lists every figure whose recipe
   reuses a shot whose `Setup`, `Scene`, `AntiAliasing` or `DebugView` changed in Shots.json, and every shot that names
   entities by ID.
4. The pages marked W8 or W8r in the outline, each with its list of movable claims: the section `## Movable claims` of
   `plan/notes/<part>/<chapter>.md`, one line per claim that wave 8 can move (numbers of shadowed lights, views per
   frame, noise, quality values, GI views), with its source (a file and line at the pin, or a key of `values.json`). A
   W8 or W8r page without that section fails the report.
5. The pages whose prose numbers may be stale: every page that links to a reference page whose generated file changes
   between the old dumps and `--dumps-to`, with each number in its prose.
6. The engine files the tools depend on that changed: `Tools/PerfLock.py`, `Tools/LookDev.py`,
   `Tools/LookDev/Shots.json`, `Tools/LookDev/LookDevScene.json`, `Tools/GenerateShowcaseTerrain.py`,
   `CMake/StrataSlang.cmake`, `Strata/vendor/glm`, `ThirdPartyNotices.md`, `StrataEditor/src/Editor/EditorCommandRunner.h`,
   `StrataTests/src/FeatureTest/SDKReader.h`.
7. Text figures to take again.

After a move, in this order: the pin build (1.3); `reference.py dump`, `parse`, `render`; `names.py check` and
`excerpts.py check` on every page; `tutorials.py run`; in phase B, `figures.py take` of every figure,
`figures.py compare` against the originals the stamps name, and `figures.py publish`, whose candidates (5.7, "Retakes")
go to the photographer.

## 11. Engine additions (v0.8.1)

At the pin, the engine cannot capture a whole-editor picture by command, read back intermediate targets (depth,
normals, shadow maps, the HDR image before tone mapping, bloom's chain), switch the renderer features that only code
sets, show specular-only or diffuse-only light, or give stills of motion effects (`research/captures.md`, §5).

The additions come in three tiers. Tiers 1 and 2 land on the engine's `main` after 0.8.0, through the engine's CI and
review like any change, made by the engine's agents under the engine's rules (tests, feature test, layering). They ship
as **v0.8.1**, and the book's final pin is v0.8.1, for text and pictures alike: the book has one pin. The pin move from
v0.8.0 to v0.8.1 is reported like any move (section 10).

**Tier 1 (small):**

- the result of `viewport.capture` gains `complete` (true when nothing of 5.3 is pending), `incomplete` (the reasons)
  and `screenSpaceReflectionsPending`;
- `editor.commands` reports each command's `mayDefer`, `waitsForAssets` and `results`;
- a command `asset.types`: the asset types, their importers, the importers' versions and file extensions;
- the editor option `--window-size <width>x<height>`.

**Tier 2 (medium):**

- `editor.screenshot {path, overwrite, panel}`: a picture of the editor window or of one panel, reached through
  `EditorHost`, since `StrataEditorCore` reaches the UI only through it;
- `viewport.capture {renderer: {…}}`: switches of `SceneRendererSpecification` for one capture, refused outside
  captures: `FadeLevelsOfDetail`, `GPUDriven`, `BatchAcrossMaterials`, `TextureStreaming`, `SpecularAntiAliasing`,
  `VisibilityFeedback`, `OcclusionCulling`, `DitherOutput` (`SceneRenderer.h:127-288`), and the specular energy
  compensation (`GetSpecularEnergy`, `Strata/shaders/Include/PBR.slang:68`);
- the debug views `specular`, `diffuse`, `clusters` (the light clusters), `culled` (culled and occluded instances
  tinted) and `wireframe`.

**Tier 3, only where a figure cannot be made with a debug view:** captures of intermediate targets (depth, normals,
velocity, the shadow mask, cascades, the local shadow atlas, bloom levels, the glyph atlas) and stills of motion
effects. Each tier 3 item is requested with the figure that needs it and why no debug view (of the pin or of tier 2) shows it;
only items that ship in v0.8.1 are used. Until an addition exists, its figures carry `waitsFor` and the page shows a
diagram in their place.

**Stand-ins.** A figure that waits (`waitsFor`), or that no take can make at the pin (`blocked`, with its reason), names
in `standIn` the figure of the same manifest that the page places in its place: a drawing, or the nearest honest
picture, which a take or a writer makes. The page writes `::figure{id=<stand-in>}` there, never the waiting figure;
without a stand-in, `noStandIn` says in one sentence why the page shows nothing there. `check` accepts a figure that no
page places only so (5.8). A release build fails on any placeholder (`src/plugins/figures.mjs`: a picture not taken, a
file without its stamp, a placed figure that waits or is blocked); drafts keep placeholders. When the addition ships,
the figure loses `waitsFor` and `standIn`, and the page places it again.

**One request extends tier 2** with the capture switches that figures need and its list lacks: the horizon fade off
(`GetHorizonFade`, `Strata/shaders/Include/PBR.slang:95-100`), the screen-space reflections before their spatial
resolve (`Strata/shaders/Effects/ReflectionResolve.comp.slang:5-10`), one bounce of global illumination
(`GlobalIlluminationSettings::BounceGain` 0, `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h:29-32`), and
FXAA's subpixel amount at 0.75 beside the pin's 0.25 (`c_Subpixel`, `Strata/shaders/PostProcess/FXAA.frag.slang:37`).
Until the switches ship, those figures carry `waitsFor` and the pages show diagrams in their place
(`critique/rulings-7.md`, R34).

Additions change renderer code, so they are reviewed as rendering changes; a capture-only switch is refused outside
captures, so frames the game draws do not change. `figures.py list --waits` is the request list for the engine's
agents. In phase B, the steps of a frame capture on `gpu/debugging` and the section "Looking inside a frame" of
`gpu/frame-tour` are checked by running what they show on the GPU, as text figures.

**What the allocation found in the engine.** The table lists what the allocation found at the pin. The book states
what the pin does, never what the code ought to do, so each row says what the pin does, with the place that shows
it. The list goes to the engine's agents beside the additions. Two fixes are asked for v0.8.1, with tier 1; the
rest is for the engine's work after 0.8.0 (`critique/rulings-7.md`, R34).

| At 822a7a46 | Where | Asked for |
| --- | --- | --- |
| After an exception leaves a frame, the program ends in order and exits with code 0: the catch logs a critical line and stops the loop, nothing sets the exit code, and no test covers the path | `Strata/src/Strata/Core/Application.cpp:243-253`; `Strata/src/Strata/Core/Application.h:132`; `Strata/src/Strata/Engine/EntryPoint.h:35-36`; `git grep -n "Unhandled exception" -- StrataTests` finds nothing | v0.8.1, with tier 1: an exit code that says the program failed |
| By default every engine object is compiled for AVX2 on x86-64 (MSVC with the Visual Studio generators, GCC and Clang), so the released programs for x86-64 and every game exported from them need a processor with AVX2; nothing checks for it at startup, and the only processor check in `Strata/src` is SSE 4.2's, for CRC-32C | `CMake/StrataCompilerOptions.cmake:27-35`, `:47-84`; `Strata/src/Strata/Core/Hash.cpp:109-119` | the engine's work after 0.8.0 |
| `AGENTS.md` calls the formatting "enforced by `.clang-format` and `.editorconfig`", and neither CI nor a test runs clang-format | `AGENTS.md:144`; `git grep -n -i "clang-format" -- . ":!Strata/vendor" ":!Docs/Plans"` finds only that line | the engine's work after 0.8.0 |
| `PrefabSync` catches a prefab's instances up once per prefab and scene, the first time it looks at it, so a cell that streams in later may keep instances that missed a change of the prefab; the Manual says that prefab changes reach a cell's instances when the cell loads; no test covers prefabs in cells | `StrataEditor/src/Editor/PrefabSync.cpp:174-181`, `:205-241`; `Docs/Manual/Worlds.md:100`; `git grep -n -i prefab -- StrataTests/src/Editor/EditorWorldTests.cpp` finds nothing | the engine's work after 0.8.0 |
| The SDK's comment says that once `World::IsLoadedAround` is true the ground there has collision, but it reports loaded cells, and a mesh collider's body stays pending until its mesh data is in and its shape is cooked | `StrataScriptCore/Include/StrataScript/World.h:38-41`; `Strata/src/Strata/Physics/PhysicsWorld.h:41-43`, `:129-132` | the engine's work after 0.8.0 |
| Simulate draws skinned meshes in their bind pose: the Animation system does not run in Simulate, and the editor makes its animation preview for the edited scene only | `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-36`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:2697-2704` | the engine's work after 0.8.0 |
| Only the editor's Game view sets an input viewport, so an exported game reports mouse positions in the window's screen coordinates, while `Game::GetWindowSize` reports framebuffer pixels; on a scaled display the two differ | `StrataEditor/src/Panels/GameViewPanel.cpp:279`; `Strata/src/Strata/Input/Input.cpp:137-145`, `:364-369`; `Strata/src/Strata/Core/Window.h:74-75`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:576-577` | the engine's work after 0.8.0 |
| `AnimationSystem` and `AudioSystem` reach assets through `AssetManager`'s static functions, which `AGENTS.md` forbids for code that works for a scene | `Strata/src/Strata/Animation/AnimationSystem.cpp:42`, `:53`, `:64`, `:983`; `Strata/src/Strata/Audio/AudioSystem.cpp:141`, `:554`, `:613`, `:750`, `:908`; `AGENTS.md:205-206` | the engine's work after 0.8.0 |
| The Tetris sample's README says that its rules (`TetrisGame.h`) are tested on their own; no test does that: the rules are built and run only inside the whole game, which the CTest `StrataEditor.Tetris` plays through the sample's command script, and the only match of `TetrisGame` under `StrataTests` checks that a copy of the sample holds `Scripts/TetrisGame.cpp` | `Samples/Tetris/README.md:13`; `StrataTests/CMakeLists.txt:864-878`; `StrataTests/src/Editor/ProjectSamplesTests.cpp:203` | the engine's work after 0.8.0 |
| Script modules built with GCC or Clang carry no debug information in Release and Dist: the module's CMake function adds it only for MSVC, scripts are built in the editor's own configuration, and Dist takes Release's flags | `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`; `StrataEditor/src/Editor/ScriptBuild.cpp:402`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-53` | v0.8.1, with tier 1: `-g` for script modules built with GCC or Clang |
| The engine's documents and comments that are wrong at the pin | the rows of kind `engine` of process.md's table "Errata known at 822a7a46", each with its place | the engine's work after 0.8.0 |

Five rows hold claims that a run can settle, and the pages that state them hold each as a check before writing
(`allocation/README.md`, "Checks before writing"). The engine's agents settle four of them with a test or a run:
`PrefabSync` with cells, the pending window of mesh colliders, mouse units on a scaled display, and script breakpoints
on Linux and macOS. Simulate's bind pose is the photographer's check (5.4). Until a result is in, a page states only
what the code at the pin shows, and says that it was read, not run. Until a fix ships at the book's pin, the page says
what the pin does, and where a reader would expect otherwise, book.md's "What Strata does not do" has the row.

## 12. Files and who writes them

| Path | Holds | Written only by |
| --- | --- | --- |
| `engine.pin` | the pin | `pin.py move` (the integrator, during a freeze) |
| `src/content/docs/<part>/<chapter>.md` | pages | the writer, the fixer, the part editor; `excerpts.py fill`, `sketches.py fill` and `figures.py fill` write fence bodies and `src` |
| `src/content/figures/<part>/<chapter>.json` | recipes | the writer, the fixer |
| `src/assets/figures/<part>/<chapter>/` | published pictures, `taken.json`, `*.result.json`, text figures | `figures.py publish` |
| `originals/<sha256>.png` | the PNG originals of every published picture; ignored, never committed | `figures.py publish` |
| `release/strata-engine-docs-originals-<tag>.tar` | the archive of one book release's originals; ignored | `figures.py archive` |
| `labs/<name>.json`, `labs/<name>/` | labs | the lab's owner page (named in the brief) |
| `labs/CREDITS.md` | the credits of the labs' third-party files | the integrator, from the `## Requests` of the notes, as for `tutorials/assets/CREDITS.md` (process.md) |
| `public/downloads/labs/<name>.zip` | lab downloads | `figures.py labs` |
| `layouts/<name>.ini` | editor layouts for `editor` figures | the photographer |
| `sketches/<part>-<chapter>-<name>.<ext>` | sketches | that page's writer |
| `tutorials/<part>/<chapter>.tutorial.json`, `.patch`, `tutorials/<part>/<chapter>/` | tutorials, patches, their files, exercise solutions | the writer, the fixer |
| `tutorials/<part>/<chapter>.stamp.json` | stamps | `tutorials.py run` and `patch` |
| `tutorials/assets/`, `tutorials/assets/CREDITS.md` | tutorial assets | the asset's owner page (named in the brief); `CREDITS.md` by the integrator, from the `## Requests` of the notes (process.md) |
| `public/downloads/tutorials/<part>/<chapter>/`, `public/downloads/tutorials/<part>/<chapter>.patch` | reader copies, end-state zips, patches | `tutorials.py compile` and `run` |
| `public/downloads/solutions/<part>/<chapter>/` | worked solutions' downloads | `tutorials.py compile` |
| `public/third-party-notices.txt` | the notices the site serves as `<base>/third-party-notices.txt` | `notices.py write` |
| `tools/data/notices.json` | what the site ships: per component its package, version, license id and copyright lines | first the tool builder; afterwards whoever changes `package-lock.json`, in the same commit |
| `reference/_dumps/<pin>/`, `reference/_dumps/<pin>/parsed/` | dumps, parsed tables | `reference.py dump` and `parse` |
| `reference/_examples/<command>.json` | example results | `tutorials.py run --record-examples` |
| `src/generated/reference/` | rendered tables, `values.json` | `reference.py render` |
| `src/content/glossary.json` | the glossary | one admitter at a time |
| the tools this file specifies and `tools/pages.py`, with their modules in `tools/booklib/`; `tools/data/`, `tools/schemas/`, `tools/reference-limits.json`, `scripts/encode-figures.mjs`, `scripts/screenshot-page.mjs` | the tools | the tool builder; the tools that site.md specifies are the site builder's (process.md) |
| `plan/notes/<part>/<chapter>.md` | a page's notes, with its movable claims | the writer |

Outside the repository, never committed: `G:/GameEngineAI/.worktrees/docs-pin` (the clone and its builds, section 1),
`docs-package-<version>` (release packages), `docs-baselines` (5.5), `docs-work/<tool>` (work folders), and the
session folders in the user's temporary folder.

## 13. When each check runs

**A writer's exit checks**, before a page enters review (a page that fails one cannot):

```sh
python -I tools/excerpts.py fill <page> && python -I tools/excerpts.py check <page>
python -I tools/sketches.py check <page>
python -I tools/figures.py check --engine <clone> --dumps reference/_dumps/<pin>
python -I tools/tutorials.py check --dumps reference/_dumps/<pin> <page>     # tutorial pages
python -I tools/names.py check --dumps reference/_dumps/<pin> --engine <clone> <page>
python -I tools/lint.py --engine <clone> <page>
python -I tools/pages.py check
```

**CI** runs the checks that need no engine program, with the engine fetched at the full pin as site.md's CI section
states: `excerpts.py check`, `sketches.py check`, `figures.py check`, `tutorials.py check`, `reference.py check`,
`names.py check`, `notices.py check` (section 15), `lint.py --engine`, `pages.py check`, and `pin.py report` (which
must report nothing at the pin). Each runs in the job that has what it reads (site.md, "CI").
With `--release`, missing pictures and stamps are errors. Optionally, after 0.8.0, a CI job
re-runs every editor tutorial on the Linux package with `--no-gpu` on `ubuntu-24.04`, with CMake and GCC for the
script builds, instead of trusting the stamps.

**Phase A** (pin 822a7a46, every editor `--no-gpu` but the checks before writing): the pin build (1.3); the four
captures of the checks before writing, once the pin build exists and before the briefs of the pages that wait for them
(5.4); `reference.py dump`, `parse` and `render`; the writer's exit checks; `tutorials.py run` for tutorials that
render nothing, so their stamps exist in phase A (the pilot's `make/first-script` among them); `figures.py check`
offline for every recipe (the pilot's `image/tone-mapping` among them); `figures.py take --kinds text` for text
figures.

**Phase B**: the move to v0.8.0 (section 10); the additions (section 11); the move to v0.8.1; then, at the final pin,
with the GPU and one run at a time: `figures.py take` of every kind, `tutorials.py run --pictures` (6.5), `tutorials.py
patch`, `tutorials.py run` with the release package (1.3), and the check of the frame captures of `gpu/debugging` and
`gpu/frame-tour` (section 11). Stamps and pictures that count for the release are made at the final pin; runs at
earlier pins find problems early.

## 14. Where the engine names of this file are defined (822a7a46)

**Editor commands** (`StrataEditor/src/Editor/` unless named):

| Command | Defined at | Parameters this file uses |
| --- | --- | --- |
| `viewport.capture` | `EditorViewportCommands.cpp:1211` | `width`, `height`, `camera` (`editor`, `scene`), `overlays`, `position`, `target`, `fov`, `waitForAssets`, `debugView`, `quality` (`project`, `low`, `medium`, `high`, `ultra`: `:142-145`), `path`, `overwrite`, `live`, `atFixedStep`, `frames` (1 to 16: `:79`); sizes 16 to 4096 (`:34-35`) |
| `debugView` values | `EditorViewportCommands.cpp:147-151` | `none`, `streaming`, `lod`, `mip`, `motion`, `shadows`, `lighting`, `ao`, `indirect`, `luminance`, `albedo`, `voxels`, `gi`, `open`, `probes` |
| `viewport.setSettings` | `EditorViewportCommands.cpp:1109` | `gameView {mode, width, height}` |
| `scene.open` | `EditorSceneCommands.cpp:408` | `scene`, `force` |
| `scene.loadStatus` | `EditorSceneCommands.cpp:429` | `wait` |
| `scene.new` | `EditorSceneCommands.cpp:379` | `name` |
| `world.loadCells` | `EditorWorldCommands.cpp:888` | `region {min, max}`, `wait` |
| `project.create` | `EditorAssetCommands.cpp:272` | `directory` (absolute), `name`, `template` (`empty`, `basic3d`) |
| `project.openSample` | `EditorAssetCommands.cpp:388` | `sample`, `directory` |
| `project.samples`, `project.templates` | `EditorAssetCommands.cpp:369`, `:254` | |
| `project.export` | `EditorAssetCommands.cpp:457` | `directory` |
| `project.settings` | `EditorProjectSettingsCommands.cpp:207` | `section` |
| `project.setSettings` | `EditorProjectSettingsCommands.cpp:259` | `section`, `value`, `reset` |
| `asset.import` | `EditorAssetCommands.cpp:757` | `file`, `files`, `directories` (absolute), `directory` |
| `material.set` | `EditorAssetCommands.cpp:1147` | `material`, `properties`, `save` |
| `entity.find` | `Commands/EntityCommands.cpp:401` | `name`, `tag`, `component`, `box`, `limit`; result `{entities}` |
| `entity.create`, `entity.get`, `entity.delete`, `entity.setActive` | `Commands/EntityCommands.cpp:170`, `:363`, `:196`, `:530` | `name`, `components`; `entity` |
| `component.list`, `component.add`, `component.get`, `component.set` | `Commands/EntityCommands.cpp:613`, `:639`, `:700`, `:721` | `entity`, `entities`, `component`, `values`; result of `component.get`: `values` |
| `play.start`, `play.stop`, `play.step`, `play.state`, `play.simulate` | `Commands/PlayCommands.cpp:131`, `:168`, `:191`, `:258`, `:159` | `paused`; `steps`; results `stepsRun`, `fixedSteps` |
| `input.sequence` | `EditorInputCommands.cpp:679` | `events`, `steps` |
| `lighting.bakeProbes` | `EditorLightingCommands.cpp:872` | |
| `graphics.resetPlayerOptions` | `EditorGraphicsCommands.cpp:16` | |
| `editor.status` | `EditorStateCommands.cpp:733` | `sections` (`engine`, `editor`); result `engineCommit` |
| `editor.commands` | `EditorCommands.cpp:66` | result `{commands: [{name, description, parameters, kind}]}` |
| `editor.wait`, `editor.quit`, `log.read`, `editor.activity` | `EditorStateCommands.cpp:883`, `:856`, `:981`, `:397` | `frames`; `force` |
| `editor.showPanel` | `StrataEditor/src/EditorLayer.cpp:177` | `panel` |
| `script.build`, `script.add`, `script.create`, `script.init`, `script.status` | `EditorScriptCommands.cpp:314`, `:572`, `:417`, `:394`, `:247` | result of `script.build`: `success`, `errorCount`, `diagnostics` (`:105-122`) |
| `preferences.get`, `preferences.set`, `preferences.save` | `EditorPreferencesCommands.cpp:77`, `:121`, `:158` | |
| command-script keys | `EditorCommandRunner.cpp:431-433`; rules `EditorCommandRunner.h:74-98` | `command`, `parameters`, `expect` (`equals`, `min`, `max`), `bind`, `$ref`, `pointer`, `until` (`steps`, `seconds`) |

**Components, properties, settings:**

| Name | Defined at |
| --- | --- |
| `PostProcess`; `AntiAliasing` (bool); `AntiAliasingMethod` (`FXAA`, `TAA`, `Morphological`) | `Strata/src/Strata/Renderer/RendererComponents.cpp:447`, `:490`, `:491` |
| `DirectionalLight`; `Intensity` | `RendererComponents.cpp:280`, `:287` |
| `MeshRenderer`; `Mesh` | `RendererComponents.cpp:273`, `:276` |
| `Transform`; `Rotation` (a quaternion, edited as Euler degrees) | `Strata/src/Strata/Scene/ComponentRegistration.cpp:80`, `:85` |
| `Builtin/Cube` | `Strata/src/Strata/Asset/BuiltinAssets.cpp:16`, `:117` |
| `Renderer.Quality`; `Preset` (`Low`, `Medium`, `High`, `Ultra`, `Custom`) | `Strata/src/Strata/Renderer/RendererQuality.h:188`; `RendererQuality.cpp:200-201`, `:728` |

**Program options:**

| Program | Options this file uses | Defined at |
| --- | --- | --- |
| `StrataEditor` | `--project`, `--commands`, `--quit-after-commands`, `--frames`, `--screenshot`, `--headless`, `--no-gpu`, `--windowed` (1600×900), `--ui-scale`, `--layout`, `--no-automation`, `--idle-timeout`, `--version` | `StrataEditor/src/EditorApplication.cpp:64-80` |
| `StrataRuntime` and exported games | `--windowed`, `--resolution`, `--frames`, `--seconds`, `--screenshot`, `--save-directory`, `--quality` | `StrataRuntime/src/RuntimeApplication.cpp:340-353` |
| `StrataCLI` | `call <method> @<file> --project --timeout`, `launch --project --headless --no-gpu --idle-timeout`, `list --json` | `StrataCLI/src/CLI/CliApplication.cpp:573-576` |

**Environment variables:** `STRATA_SESSION_DIR` (`Strata/src/Strata/Network/EditorSession.cpp:17`),
`STRATA_RECENT_PROJECTS` (`StrataEditor/src/Editor/RecentProjects.h:60`), `STRATA_SCRIPT_BUILDS_DIR`
(`StrataEditor/src/Editor/ScriptBuild.cpp:490`), `STRATA_EDITOR_PATH` (`StrataCLI/src/CLI/CliApplication.cpp:616`).

**Engine tools:** `Tools/PerfLock.py` (`--label`, `--limit` in minutes with default 25, `--wait` with default 30,
exit codes 75 and 124); `Tools/LookDev.py` (`capture`, `compare`; `AA_MODES` `:49-54`; shot file names `:707-708`);
`Tools/LookDev/Shots.json`; `Tools/LookDev/LookDevScene.json` (saves `Scenes/LookDev.stscene`, `Furnace`, `Mirror`,
`Specular`, `Yard`, `Grass`, `SunRoom`, `SealedRoom` and `Cornell`); `Tools/GenerateShowcaseTerrain.py` (`setup
--station Dawn|Golden|Dusk --format lookdev|script`, usage line 18; `STATIONS` `:175-179`).

**Tests:** the doctest suites `Architecture.Layering` (`StrataTests/src/Architecture/LayeringTests.cpp:113`) and
`CLI.McpToolsets` (`StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:26`); the CTest `StrataTests.FeatureTest`
(`StrataTests/CMakeLists.txt:317`, suites `FeatureTest` and `Editor.FeatureTest` in `StrataTests/CoreShards.json`).

**SDK:** `Graphics::Set` (`StrataScriptCore/Include/StrataScript/Graphics.h:181`); `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`
(`Script.h:852`, `:857`); `StrataScriptHostAPI` (`ScriptABI.h:312`); `StrataScriptClassDesc` (`ScriptABI.h:772`).

## 15. Third-party notices

The site ships other people's files (fonts, scripts, WebAssembly), quotes other people's code (the engine's vendored
libraries) and shows and gives out other people's assets (the samples' models and textures). Each keeps its notice
(`critique/rulings-6.md`, R22). One file holds them: `public/third-party-notices.txt`, which the site serves as
`<base>/third-party-notices.txt` and links from the footer of every page (site.md). It is committed, so a change of a
dependency shows in a diff.

```text
python -I tools/notices.py write --engine <clone>
python -I tools/notices.py check --engine <clone> [--dist <built site>]
python -I tools/notices.py check --sections A [--dist <built site>]
python -I tools/notices.py check --sections BC --engine <clone>
```

- **Reads**, per section of the file:
  - A, *What this site ships*: `tools/data/notices.json`, kept by hand, which lists every component whose files or
    code are in `dist/` (the three font families, KaTeX and its fonts, Starlight with its Night Owl theme, Astro's and
    Vite's runtime parts, Expressive Code, Pagefind and its default UI with the WebAssembly's crates, and whatever else
    a build puts into `dist/`), each with its package, version, license id and copyright lines; the license texts from
    `node_modules`; `package-lock.json`;
  - B, *What this book quotes*: the pages' `vendor:` quotes (3.2), and, at the pin, `ThirdPartyNotices.md` and each
    quoted library's license file; every project a page's code is derived from (`ThirdPartyNotices.md`, "Code derived
    from other projects");
  - C, *What this book shows and gives out*: the `CREDITS.md` at the pin of each sample that a recipe or a tutorial
    uses, `labs/CREDITS.md` and `tutorials/assets/CREDITS.md`.
- **`write`** writes the three sections into `public/third-party-notices.txt`. Each license's text appears once; each
  component names its copyright holders exactly as its own notice does (Source Serif 4 is Adobe's).
- **`check` fails** (exit 1) when the committed file differs from what `write` writes; when a component of the list
  has another version in `package-lock.json` than the list records, so that a person reads every upgrade; or when a
  component's license is outside the allowlist: `MIT`, `MIT-0`, `ISC`, `0BSD`, `BSD-2-Clause`, `BSD-3-Clause`,
  `Apache-2.0`, `OFL-1.1`, `CC0-1.0`, `BlueOak-1.0.0`, `Unicode-3.0`, `Zlib`. With `--dist`, after a build, it also
  fails when the built site holds a font family, a script package or a WebAssembly file that no component of the list
  claims. Exit 2 when something that the asked sections read is missing: the pin that `--engine` must resolve,
  `package-lock.json` or `node_modules`.
- **`--sections`** names what one job can check (`critique/rulings-6.md`, R26): `A` reads `package-lock.json` and
  `node_modules` and no engine; `BC` reads the engine and no `node_modules`. Such a check compares those sections
  of the committed file, and the license texts they name, with what `write` would write. Without `--sections`,
  `check` covers the whole file: the form for the authoring machine, before a commit that changes the file. The
  file's layout lets sections be compared apart; the tool states the layout at its top.
- CI runs `check --sections A` in its `lint` job, `check --sections BC --engine engine` in its `excerpts` job, and
  `check --sections A --dist <built site>` in its `build` job, after the build (section 13; site.md, "CI").
