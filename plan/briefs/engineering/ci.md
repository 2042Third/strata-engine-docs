# Brief: `engineering/ci`

| Field | Value |
| --- | --- |
| Title | Continuous integration |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `engineering/flags-portability`, `engineering/test-program` |
| From | build-test ch. 12 (the CI matrix, caches and eviction, shader steps, annotations, the Dist job, `ci/<name>` branches, CIStatus) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/ci` — Continuous integration

**Covers.** The job: what runs on every push to `main`, every pull request and every push to a `ci/<name>` branch, and
how a failure is read. The problem: continuous integration; matrix builds; caches and their eviction; builds that keep
going after an error; logs against annotations; the limits of runners; which tests a hosted runner can run (no GPU,
not the reference machine); the mistake of merging a large integration without green CI on the oldest compilers. The
map: the CI matrix (each job against what it builds and tests: configurations, compilers, caches, shader steps, the
labels it leaves out). The contract: CI always builds with warnings as errors; the test step leaves out `gpu` and
`perf`; a branch that lands many changes goes through `ci/<name>` and waits for green CI before it moves `main`. The
toy: a workflow of ten lines with one job; the workflow format (jobs, steps, a matrix, `if`) is taught as the page
needs it. The real code: the triggers and the concurrency group that cancels a superseded run; the matrix (Windows
Release and Debug with `windows-ninja` and sccache, Linux with GCC 14, macOS on `macos-15` with Apple Clang 17, and
Linux without Audio, Physics and GLFW, without the editor and without the package tests); the Visual Studio developer
environment imported on Windows; the compiler cache in GitHub Actions (a key per job and commit, restored by prefix
from the branch or `main`, saved even when tests fail, size caps, and the superseded entries of a branch deleted so
that `main`'s set survives GitHub's 10 GB eviction); the build with `-k 0`, so one run reports every compile error;
the shader steps (`spirv-val` for Vulkan 1.2 on Linux, after StrataShaderTool's patch; the Metal conversion and Apple's
compiler on macOS, whose list of known failures only shrinks); the test step (labels, four at a time, a 900-second
timeout, `STRATA_TEST_TRACE=1`, Linux `ulimit`s so that a runaway test fails alone, and tests that run even after a
failed shader step); the failure annotations of `annotate_failures.py`, because job logs need admin rights and
annotations are public; the Windows Dist job with the Visual Studio generator and the package tests, added after a
change broke Dist unnoticed in wave 3, and kept for a second reason: script builds use the generator the editor was
built with, so its package tests are the only ones that build scripts through the Visual Studio generator (the cached
jobs build with Ninja; linked to `editor/script-builds`); `Tools/CIStatus.py`, which reads a commit's runs, jobs and annotations through
GitHub's API and never prints the token. Strata runs no sanitizer builds, and nothing runs a format check: neither CI
nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them (about 40
words). Pictures of CI's pages need access to
GitHub; where the brief gives none, the page uses text captures and its figures. Exercises: read a failure from its
annotations alone with `CIStatus.py`; trace it yourself: follow one job of the matrix by a search in
`.github/workflows/ci.yml`, from its `preset`, `config` and `exclude` to the test step's `ctest` command line, and say
which labels it leaves out. At the end the reader can say what CI checks for a push, read a failure without
the log, and land a large change through a `ci/<name>` branch.

**Leaves out.**

- The compilers' traps and `CompatLint.py`, run before a push → `engineering/flags-portability`
- The labels and shards the test step selects → `engineering/test-program`
- Why perf budgets are measured on the reference machine, not in CI → `engineering/perf-lab`
- The release workflow → `engineering/releasing`
- How a script build takes the generator the editor was built with → `editor/script-builds`
- The shader dialect and its checks → `gpu/shaders`
- How MoltenVK runs shaders at run time → `gpu/vulkan-nvrhi`

**Fit.** `fits`: about 4,005 words against L (5,000). One concept, two excerpts, three figures and the workflow's
features (the matrix, the cache, the shader and test steps, the annotations, the Dist job) take the most. The count puts
the page at the bottom of L's range.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:362` | concept | home | Continuous integration: matrices, caches and eviction, keep-going builds, logs and annotations, runners' limits, what hosted runners can test; the `ci/<name>` gate; the mistake of merging without green CI |
| `build-test:192-201`, `build-test:221` | feature | home | The triggers; the matrix; the developer environment; the compiler cache in Actions; `-k 0`; the shader steps; the test step; the annotations; the Windows Dist job and its two reasons (the wave-3 Dist break; its package tests are the only ones that build scripts through the Visual Studio generator, linked to `editor/script-builds`); `Tools/CIStatus.py`, which the inventory lists twice |
| `build-test:238` | feature | home | `.github/scripts`: `annotate_failures.py`, `validate_shaders.sh`, `convert_shaders_to_metal.sh` |
| `build-test:408` | code | home | `.github/workflows/ci.yml:19-60`: a CI matrix, each job with its preset, configuration, cache and key |
| `new:18` | code | home | `.github/workflows/ci.yml:195-215`: the test step with its labels, trace, `ulimit`s and timeout, and the comment that says why |
| `build-test:445` | figure | home | The CI matrix: jobs against what each builds and tests |
| `build-test:446` | figure | home | The compiler cache's keys in GitHub Actions: restore by prefix, deletion of superseded entries, why `main`'s set would otherwise be evicted |
| `build-test:467` | figure | home | GitHub's pages: a CI run, an annotation in a pull request, a release page with its archives and `SHA256SUMS.txt` (see `build-test:774`) |
| `build-test:500` | rule | home | Push large integrations as `ci/<name>` and wait for green: older compilers and libraries reject what local ones accept |
| `build-test:539` | rule | home | Annotations, not logs, carry CI's failures; `known failure:` lines are not error lines |
| `build-test:591` | hands-on | home | Read a CI failure from its annotations alone with `Tools/CIStatus.py annotations <commit>` |
| `new:39` | hands-on | home | Trace it yourself, by a search in `.github/workflows/ci.yml`: one job of the matrix (the Linux job without modules) from its `preset`, `config`, `options` and `exclude` to the test step's `ctest` command line; which labels it leaves out and why (about 150 words). Evidence: `.github/workflows/ci.yml:50-60`, `:213-215` |
| `build-test:646` | term | home | spirv-val |
| `build-test:685-689` | term | home | CI; runner (GitHub Actions); matrix; annotation; `ci/<name>` branch |
| `build-test:772` | open | home | The page names the macOS step's list of known failures as the script's and leaves MoltenVK's run time to `gpu/vulkan-nvrhi` |
| `build-test:774` | open | home | Pictures of CI's pages need GitHub access; the brief decides their source, or the page uses text captures |
| `new:19` | not-done | home | No sanitizer builds (AddressSanitizer, UndefinedBehaviorSanitizer). Evidence: `git grep -niE "fsanitize" 822a7a46 -- CMakeLists.txt CMake StrataTests/CMakeLists.txt .github CMakePresets.json` finds nothing; `.github/scripts/annotate_failures.py:40` only recognizes the word "Sanitizer" in a log |
| `new:38` | not-done | home | No format check: neither CI nor a test runs clang-format, so `.clang-format` and `.editorconfig` act only in editors that read them, although `AGENTS.md` calls the formatting enforced (about 40 words; book.md, "What Strata does not do"). Evidence: `git grep -n -i "clang-format" 822a7a46 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` |
| `build-test:202` | feature | link | `Tools/CompatLint.py`, run before a push |
| `build-test:118` | feature | use | The labels the test step leaves out |
| `build-test:483` | rule | use | Warnings as errors in every CI build |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Test labels, shards and `STRATA_TEST_TRACE` | `engineering/test-program` | must |
| Compiler caches, warnings as errors and the three compilers | `engineering/flags-portability` | must |
| git branches and pushes to a remote | `basics/git` | must |
| The Dist configuration | `core/first-change` | must |
| The shader build's outputs and `ShaderEntries.txt` | `engineering/generated-code` | helps |
| MoltenVK | `gpu/vulkan-nvrhi` | helps |
| Shell scripts in bash | `basics/tools` | helps |
| Script builds and the generator they take from the editor | `editor/script-builds` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ci-name-branch` | `ci/<name>` branch | - |
| `annotation` | Annotation | - |
| `ci` | CI | continuous integration |
| `runner-github-actions` | Runner (GitHub Actions) | - |
| `spirv-val` | spirv-val | - |
