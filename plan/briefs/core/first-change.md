# Brief: `core/first-change`

| Field | Value |
| --- | --- |
| Title | Your first engine change: build from source, change one thing, test it |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `core/map`, `basics/cpp-classes`, `basics/git` |
| From | new; build-test "Building Strata: CMake, presets and configurations" (the source build in short, with tabs per OS; the full options stay in `engineering`); one change; build-test "Testing an engine: doctest, CTest and Strata's test program" (one test case written and run; testing's home is `engineering`) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/first-change` — Your first engine change: build from source, change one thing, test it

**Covers.** What the reader makes: Strata built from source on their own computer, with one small change and the test
that proves it. Four sections, each ending in a checkpoint of the patch. First, the source: the repository cloned at the
book's pin, then its submodules (`git submodule update --init --recursive --depth 1`), and why the configure step
refuses to run without them. Second, the build: what a source build needs first, in a box (the compilers' minimum
versions, CMake 3.25, the network for Slang's download at the first configure, the Vulkan SDK as optional, for the
validation layer only; in the Linux tab, the X11, Wayland and GTK development packages without which GLFW's and nfd's
configure stops), the configure preset of the reader's OS (`windows`, `linux` or `macos`, in tabs per OS), the Debug
build, where the binaries land (`build/<preset>/bin/Debug/`), and the editor built from source started once; Debug,
Release and Dist in one paragraph (Dist, the shipping configuration, compiles the asserts out; this page is the term's
home, and `engineering/building` teaches every configuration). Third, the change: a `ToUpper` beside
`StringUtils::ToLower` in `Strata/src/Strata/Core/StringUtils.h`; the function lives in a header, so the build needs no
new configure step (one is needed after adding or removing a file, and the page says why). Fourth, the test: a test case
in `StrataTests/src/Core/StringUtilsTests.cpp`, in its suite `Core.StringUtils`, built and run alone with doctest's
`--test-suite` filter; then run once more with the change undone, to see it fail (a test that cannot fail proves
nothing); then the core shards with `ctest --preset <os>-debug -L core`. Every "You should see" is the build's or the
test's output as a text capture. The exercises make the change the reader's own: more `CHECK`s, `StartsWithIgnoreCase`
beside `EqualsIgnoreCase`, and the tests in Dist. At the end the reader can build Strata from source on their OS, change
engine code and prove the change with a test. The brief may choose another first change; it must be small, need no new
configure step and have a test that fails without it.

**Leaves out.**

- Every preset, configuration and option, the validation layer and compiler caches → `engineering/building`
- How the test program works: its main, shards, labels and helpers → `engineering/test-program`
- What tests are for, the kinds of tests and flaky tests → `engineering/testing`
- Debugging a test that fails or crashes → `core/debugging`
- The CMake inside the build → `engineering/cmake`
- The way a change is reviewed and lands → `engineering/contributing`

**Fit.** `fits`: about 5,050 words against L (5,000). The twelve steps in four sections, with the tabs per OS of every
terminal step, take the most; the box of what a source build needs takes about 150 and the three exercises about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:612` | term | home | Dist, Strata's shipping configuration with the asserts compiled out, met here beside Debug and Release; the term's one entry (R31, D33), which `engineering/building` uses and links |
| `scripting:578` | term | home | Dist, the same entry as `foundation:612`, with the scripting side: Dist builds also drop the host functions' call counters |
| `new:18` | feature | home | What a source build needs, in a box before the first configure: MSVC 19.40, GCC 13, Clang 17 or Apple Clang 15 at least, CMake 3.25, the network for Slang's download at the first configure (or `STRATA_SLANG_ROOT`), the Vulkan SDK as optional (the validation layer only); in the Linux tab the packages `libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev libwayland-dev libxkbcommon-dev libgtk-3-dev`, without which GLFW's and nfd's configure stops with an error; about 150 words. Evidence: `Docs/DeveloperGuide.md:153-161`; `CMakeLists.txt:1`; `Strata/vendor/glfw/src/CMakeLists.txt:186-216` (`FATAL_ERROR` for each missing X11 header); `Strata/vendor/nfd/src/CMakeLists.txt:21` (`pkg_check_modules(GTK3 REQUIRED gtk+-3.0)`); `.github/workflows/ci.yml:78-85` |
| `new:2` | code | home | `Strata/src/Strata/Core/StringUtils.h:12-19`: `ToLower`, the function the change mirrors; it lives in a header, so the change needs no new configure step |
| `new:3` | code | home | `StrataTests/src/Core/StringUtilsTests.cpp:9-20`: a test suite and a test case with `CHECK`s, the shape the reader's test copies |
| `foundation:160` | feature | use | `StringUtils`, the file the change goes into; its catalogue is `reference/core`'s |
| `build-test:91` | feature | use | The pinned submodules, fetched in the first section |
| `build-test:55`, `build-test:56`, `build-test:57` | feature | use | The configure, build and test presets of the reader's OS, and no others |
| `build-test:39` | feature | use | Debug, Release and Dist in one paragraph |
| `build-test:43` | feature | use | Where the binaries land |
| `build-test:49` | feature | use | Sources are found by globbing: why adding a file needs a new configure step and changing one does not |
| `build-test:478` | rule | use | Configure again after adding or removing sources, stated where the change avoids it |
| `build-test:105` | feature | use | The `StrataTests` program that the test case runs in |
| `build-test:508` | rule | use | Every test case belongs to a `TEST_SUITE`: the reader's case goes into `Core.StringUtils` |
| `build-test:520` | rule | use | A new test is checked to fail without its change |
| `build-test:551` | hands-on | use | "Build from scratch on your OS": the first two sections walk this exercise step by step |
| `gamedev:522` | rule | home | Rebuilding the engine while an editor runs fails, because the running executable is locked: the "If you do not see it" of the rebuild step |
| `new:19` | hands-on | home | Exercises that make the change the reader's own, each with a hint and a patch against the pin as its worked solution: Basic, `CHECK`s for the empty string and for UTF-8 text, which `ToUpper` leaves unchanged as `ToLower`'s comment promises; Medium, `StringUtils::StartsWithIgnoreCase` beside `EqualsIgnoreCase`, with its test case (`InputActionSet.cpp` keeps a copy of its own in an unnamed namespace); Hard, an `ST_CORE_ASSERT` put into `ToUpper` on purpose (the text is not empty), which stops the empty-string test in Debug and does nothing in Dist, built and run with both presets. Evidence: `Strata/src/Strata/Core/StringUtils.h:12-31`; `Strata/src/Strata/Input/InputActionSet.cpp:28-31`; `Strata/src/Strata/Core/Assert.h:63-70` and `Strata/src/Strata/Core/Base.h:10-12` (no `ST_ENABLE_ASSERTS` with `ST_DIST`); `CMakePresets.json:53`, `:62`, `:65` (the Dist build presets) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: change folder, run a program with arguments, quote a path | `basics/tools` | must |
| git: clone and submodules | `basics/git` | must |
| Compiling and linking; CMake's configure and build steps | `basics/build` | must |
| Classes, member functions, header and source files | `basics/programming-3` | must |
| Functions and `std::string` | `basics/programming-2` | must |
| The C++ build tools of the reader's OS, installed | `start/install` | must |
| Strata's programs and its libraries | `core/map` | must |
| Inheritance and virtual calls, enough to read the test framework's macros | `basics/cpp-classes` | helps |

**Starting state.** No checkpoint of an earlier tutorial: the reader's computer with the C++ build tools and CMake of
`start/install`, git from `basics/git` and a Vulkan 1.2 driver. The first step clones the engine's source at the
commit the book is written against.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dist` | Dist | - |
