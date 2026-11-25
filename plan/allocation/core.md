# Allocation: core

## `core/map` — How Strata is put together: programs, libraries, modules and layers

**Covers.** The page starts from what the reader did in `start/first-game`: they started the editor, played a copy of
Tetris and built the `Spinner` script. It asks where "the engine" was in all that. The naive picture, that the editor
is the engine and everything is one big program, breaks at once: a shipped game runs without the editor. The idea: an
engine is a set of libraries, programs are built on them, and game code is a module of its own. The approaches engines
use, with a table of their costs: one program with the tools inside; engine libraries under several programs; modules
and plugins loaded while the program runs. Strata's choice: one static library per architecture layer
(`Strata_<Layer>`), under three programs (`StrataEditor`, `StrataRuntime`, `StrataCLI`) and the test program
`StrataTests`; game code in script modules built against `StrataScriptCore` alone; and a runtime that holds no editor
code, which a test proves (named in one sentence). The repository's top folders are drawn onto that picture. Then the
four words with two meanings each: "module" (the code of an engine module and its `Register<Module>Module`, against
the `EngineModule` service that lives as long as the program; and the script module, a third use), "layer" (a row of
the layer table and a static library, against an application `Layer` in the `LayerStack`), "registry" (Strata's tables
that modules fill at startup, of which the component and settings registries then freeze, against EnTT's registry of
a scene's entities) and "service" (an engine service of `EngineServices`, against a scene service of `Scene`), each
with the page that teaches it. The common mistakes: taking the editor for the engine, and reading one meaning of a word
where the other is meant. The exercises: files placed in their program and library from the layer table, and the
installed programs' `--help` compared in a terminal. At the end the reader can say which program and which library a
piece of Strata belongs to, and uses the four words without mixing their meanings.

**Leaves out.**

- How the layer table is enforced and what each layer may include → `core/layers-registries`
- The CMake that makes one library per layer, and the proof that games hold no tooling → `engineering/cmake`
- What the `EngineModule` hooks do and in which order → `core/engine-modules`
- How a script module is loaded and called → `scripting/loading`
- The tree below the top folders → `core/reading-code`
- Compiling, linking and libraries in general → `basics/build`

**Fit.** `fits`: about 3,700 words against M (3,000). The four words with their two meanings take the most, about 800,
then the approaches with their table and Strata's choice; the two exercises take about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:208` | concept | home | What a program is and what an engine adds, the Strata half: three programs over one set of static layer libraries, game code in separately loaded script modules, the runtime without editor code; the general half (process, `main`, static and shared libraries) comes from `basics/build` |
| `foundation:385` | figure | home | The diagram of executables and layer libraries: the editor, the runtime, the CLI and the tests over `Strata_<Layer>`, the tooling layers to the side, script modules linking only `StrataScriptCore` |
| `foundation:555` | term | home | Engine module registration (`Register<Module>Module`), the meaning of "module" that is set against the `EngineModule` object; the page adds the script module as a third use |
| `foundation:558` | term | home | Two glossary entries: layer (application), a slice of a program in the `LayerStack`, and architecture layer, a row of `Layers.json` and a static library |
| `scene-ecs:648` | term | home | Architecture layer, the same entry as the second term of `foundation:558` |
| `build-test:651` | term | home | Layer (Strata), the build's name for the architecture layer: a group of engine folders in `Layers.json` with the layers it may include; the same entry as the second term of `foundation:558` |
| `foundation:554` | term | use | Engine module, the other meaning of "module", defined here in one sentence; its entry's home is `core/engine-modules` |
| `foundation:551` | term | use | Registry in Strata's meaning, set against EnTT's registry (`world/ecs`); its entry's home is `core/layers-registries` |
| `foundation:565` | term | use | Service and engine service, set against the scene service of `world/systems`; the entry's home is `core/engine-modules` |
| `foundation:173` | feature | link | The layer table, named as what turns the folders into libraries |
| `foundation:177` | feature | link | The check that the runtime links no tooling, named in one sentence |
| `new:1` | feature | use | The repository's top folders (`Strata/`, `StrataEditor/`, `StrataRuntime/`, `StrataScriptCore/`, `StrataCLI/`, `StrataTests/`), drawn onto the programs and libraries |
| `new:17` | hands-on | home | Exercises: Basic, six files (`EntryPoint.h`, a panel of `StrataEditor/src/Panels/`, a Tetris script, `GLFWWindow.cpp`, `JobSystem.cpp`, a test) each placed in its program and its layer's library from the `Paths` of `Layers.json`; Medium, done in a terminal: the installed `StrataEditor --help` and `StrataRuntime --help` compared, and which program holds the editor's tools. Evidence: `StrataTests/Architecture/Layers.json:5-24`; `StrataEditor/src/EditorApplication.cpp:64-80`; `StrataRuntime/src/RuntimeApplication.cpp:340-354`; `CMake/StrataPackaging.cmake:55` (the three programs installed) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Executables, static and shared libraries, linking | `basics/build` | must |
| What a game engine is, and one frame from start to finish | `start/what-an-engine-is` | must |
| The editor, a project, a script built and attached | `start/first-game` | helps |
| A process: a running program | `basics/computer` | helps |

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

## `core/conventions` — Ownership, errors and logging in Strata

**Covers.** The job: the rules every engine file keeps about who owns what, what happens when something goes wrong, what
is logged and how the code looks, each with its reason. Ownership first, Strata's half of it (the language is
`basics/cpp-memory`'s): `Scope` for one owner, `Ref` for shared ownership, raw pointers and references for borrowing;
registries own what they make through `Scope` and hand out raw pointers (the module registry is the example); assets are
held across frames by handle, not by `Ref` (one sentence and a link). Then errors: exceptions as the language has them
are `basics/cpp-modern`'s (`throw`, `try`, `catch` and unwinding, named in one sentence with a link), and this page
keeps Strata's rule for them; programmer errors against failures a program must survive; `ST_CORE_ASSERT`, compiled out
of Dist, so its condition must have no side effects, against `ST_CORE_VERIFY`, which every build keeps; recoverable
failures return `bool`, `std::optional` or a result struct and log; engine code does not throw, exceptions of
third-party code are caught where it is called (`JsonUtils` wraps nlohmann's JSON, which throws on ordinary data:
dumping a string that is no valid UTF-8, whose bytes `Dump` and `AppendString` replace with U+FFFD), and the frame loop
catches what still escapes. Then logging as a convention: levels, the three loggers (Strata, App and Script) and their
macros, fmt formatting with glm types, warnings written at once; never a message per frame (`ErrorThrottle`) and never a
secret. Last the code style and why: names with `m_`, `s_`, `t_` and `c_`, tabs, braces on their own lines,
`#include "stpch.h"` first, and no names that Windows headers define as macros; `.clang-format` and `.editorconfig`
guide code editors and reviewers, and nothing runs a format check. The toy is a 30-line assert macro and a logger with
two levels; the real code is `Base.h`'s aliases and macros, `Assert.h`'s macros and `JsonUtils` or `ErrorThrottle` as
the error policy at work. The page's example is a loader that meets a broken file, decided three ways: assert, verify or
a returned error. The exercises: three failures sorted into assert, verify and returned error; a trace of
`ST_CORE_VERIFY` from its macro to the log line; an assert with a side effect that the Dist build removes. At the end
the reader chooses between an assert, a verify and a returned error, logs as the engine does, and writes code the review
accepts.

**Leaves out.**

- RAII, smart pointers and move semantics as C++ → `basics/cpp-memory`
- C++ exceptions as the language has them: `throw`, `try`, `catch` and unwinding → `basics/cpp-modern`
- How the log is written: the buffer, the background writer and its flushes → `core/debugging`
- Reading asserts and the log while debugging, and the assert handler → `core/debugging`
- Precompiled headers and what they cost → `engineering/flags-portability`
- The review checklist and how a change lands → `engineering/contributing`
- Platform headers and Windows macros in full → `core/platform`
- UTF-8 strings and paths → `core/files`

**Fit.** `fits`: about 4,950 words against L (5,000). The error policy (asserts, verifies, returned errors and the catch
at the call site) and the code style with its reasons take the most; the three exercises take about 750, and exceptions
as the language has them are `basics/cpp-modern`'s (about 300 fewer).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:270` | concept | home | Ownership in Strata: `Scope`, `Ref`, borrowed raw pointers, registries that own through `Scope`; the mistakes (`Ref`s to assets across frames, a lambda that holds the last reference); the language half is `basics/cpp-memory`'s |
| `foundation:275` | concept | home | Asserts, verifies, returned errors and exceptions, and the rule that chooses between them |
| `foundation:280` | concept | home | Logging: levels, loggers, sinks, the flush policy, why not per frame and never a secret; how the writer works is `core/debugging`'s |
| `foundation:90` | feature | home | `Log`: the loggers Strata, App and Script, the macros `ST_CORE_*` and `ST_*`, fmt formatting with glm formatters, flush on warning |
| `foundation:93` | feature | home | Asserts and verifies (`ST_CORE_ASSERT`, `ST_ASSERT`, `ST_CORE_VERIFY`, `ST_VERIFY`), compiled out of Dist or kept; `core/debugging` reads the handler and the debugger detection again |
| `foundation:94` | feature | home | `ErrorThrottle`: a repeating error logged once until it is cleared |
| `foundation:153` | feature | home | The base macros `ST_DEBUGBREAK`, `ST_BIT`, `ST_BIND_EVENT_FN`, `ST_DEFINE_ENUM_FLAG_OPERATORS` and `ST_ENABLE_ASSERTS` |
| `foundation:159` | feature | home | `JsonUtils`: parsing and dumping nlohmann JSON without exceptions, the catch at the call site in practice, with the header's own case in one sentence: nlohmann's JSON throws when it dumps a string that is no valid UTF-8, and `Dump` and `AppendString` replace those bytes with U+FFFD (`Strata/src/Strata/Core/JsonUtils.h:24-36`); its SAX half, `JsonEvents`, is used by `world/serialization` |
| `new:4` | feature | home | The code style: the naming table with its prefixes, the formatting rules that `.clang-format` and `.editorconfig` hold for code editors and reviewers, the include order, the conventions, and the reason for each; nothing runs a format check (no CI job and no test runs clang-format, though `AGENTS.md:144` calls the formatting "enforced"). Evidence: `AGENTS.md:128-181`; `Docs/DeveloperGuide.md:919-937`; `.clang-format` and `.editorconfig` at the repository's root; `git grep -n -i "clang-format" 822a7a46 -- . ":!Strata/vendor" ":!Docs/Plans"` finds only `AGENTS.md:144` |
| `foundation:353` | code | home | `Strata/src/Strata/Core/Base.h:10-61`: the `Scope` and `Ref` aliases, `ST_BIND_EVENT_FN` and the flag operators for `enum class` |
| `foundation:354` | code | home | `Strata/src/Strata/Core/Assert.h:53-74`: the assert and verify macros (`do { } while (false)`, `[[unlikely]]`, compiled out without `ST_ENABLE_ASSERTS`); the handler in `Assert.cpp` is quoted on `core/debugging`, which teaches it |
| `foundation:475` | rule | home | Engine code does not throw; third-party exceptions are caught at the call site; recoverable failures return errors and log; asserts only for programmer errors |
| `foundation:478` | rule | home | Asserted conditions have no side effects, because Dist removes them |
| `foundation:485` | rule | home | Do not log per frame; throttle repeating errors |
| `foundation:611` | term | home | Two entries: assert and verify |
| `build-test:628` | term | home | `ST_CORE_ASSERT` and `ST_CORE_VERIFY`, the build's entry for the two checks, compiled out of Dist and kept in it: the same entries as `foundation:611` |
| `foundation:613` | term | home | Three entries: logger, sink and level |
| `foundation:152` | feature | use | The `Ref`, `Scope` and `WeakRef` aliases, taught by `basics/cpp-memory`; this page states Strata's rules for them |
| `foundation:617` | term | link | `Scope`, `Ref` and `WeakRef`, whose entry is `basics/cpp-memory`'s |
| `foundation:167` | feature | use | `stpch.h` first in every engine `.cpp`, as a rule of the style; what a precompiled header is and costs is `engineering/flags-portability`'s |
| `new:20` | hands-on | home | Exercises: Basic, three failures sorted into an assert, a verify and a returned error (a project file that does not parse, an index past the end of an engine array, a registry used before registration) with the reason for each; Medium, trace it yourself: `ST_CORE_VERIFY` followed with a search or the debugger from its macro to `HandleAssertFailure` and the critical log line; Hard, done on the source build: a test whose `ST_CORE_ASSERT` has a side effect, passing in Debug and failing in Dist, and the fix. Evidence: `Strata/src/Strata/Core/Assert.h:53-74`; `Strata/src/Strata/Core/Assert.cpp:32-66`; `Strata/src/Strata/Core/Base.h:10-12` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Pointers, references, lifetimes, RAII, `unique_ptr`, `shared_ptr` and `weak_ptr`; `Scope` and `Ref` | `basics/cpp-memory` | must |
| Move semantics, `std::optional`, `enum class`, `constexpr` and macros | `basics/cpp-modern` | must |
| C++ exceptions: `throw`, `try`, `catch`, and the unwinding that runs destructors | `basics/cpp-modern` | must |
| Templates with several arguments (fmt's `{}` and its arguments) | `basics/cpp-generic` | helps |
| Debug, Release and Dist, and a build with a preset | `core/first-change` | must |
| JSON | `basics/data-formats` | helps |
| `glm` vectors | `basics/math-vectors` | helps |

## `core/reading-code` — Finding your way in a large codebase

**Covers.** The goal: find the file and line where something happens in a codebase too large to read whole. What must
be true first: the source build of `core/first-change`, and a code editor that reads `compile_commands.json` or the
Visual Studio solution. The steps: (1) read the map, the repository's tree: the top folders, the engine's modules in
`Strata/src/Strata/<Module>/`, the platform code in `Strata/src/Platform/<OS>/`, the editor's `Editor/`, `UI/` and
`Panels/`, the tests in `StrataTests/src/<Module>/`, and the names that say where a module's registration, components
and tests are; (2) read the documents as maps: `AGENTS.md` and its table "Where the details are", `Docs/README.md`,
then the matching section of `Docs/DeveloperGuide.md` and `Docs/Architecture.md`; (3) search for a name or a message
with `git grep` or the code editor's search in files; (4) jump with "go to definition" and "find references"; (5) the
worked trail: the editor's `--frames` option followed from its usage line and `GetIntOption("--frames")` in
`StrataEditor/src/EditorApplication.cpp`, to `ApplicationSpecification::MaxFrames`, to the frame count that ends
`Application::Run`; (6) read the tests of what was found, as its most exact description; (7) ask the history why, with
`git log -S` and `git blame`. The result is the trail written down as files and lines. Variations: from a log message
to the code that logs it; from a label in the editor's UI to the command it runs; from a runtime option
(`StrataRuntime --seconds`) to its effect; a call stack in the debugger as a trail. At the end the reader can find,
for a name, an option or a message, where in the code it acts. The exercises are three more trails, each written down
as files and lines: a startup log line to the code that logs it, the editor's `--idle-timeout` to where it closes the
editor, and `git log -S` on the headless frame cap to the commit that set it. Following a click to a pixel needs the
later parts; it is an exercise of `capstone/plan`.

**Leaves out.**

- What `CommandLine`, `ApplicationSpecification` and the frame count do → `core/first-frame`
- Breakpoints and the call stack as a way to read code → `core/debugging`
- Following a click to a pixel → `capstone/plan`
- The terminal in general → `basics/tools`
- git in general → `basics/git`

**Fit.** `fits`: about 3,450 words against M (3,000). The seven steps and the worked trail take the most; the three
exercises, each a trail of its own, take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | feature | home | The repository's tree: the top folders, the engine's module folders, the platform folders, the editor's three folders, the tests' folders by module. Evidence: `AGENTS.md:33-47`; `Docs/DeveloperGuide.md:127-147` |
| `new:5` | feature | home | The engine's own documents as maps: `AGENTS.md` with its digests and its table "Where the details are", `Docs/README.md`, `Docs/DeveloperGuide.md` and `Docs/Architecture.md`. Evidence: `Docs/README.md:1-16`; `AGENTS.md:446-455` |
| `foundation:56` | feature | use | `CommandLine` and `CommandLineOptions` as the start of the trail; what they do in full is `core/first-frame`'s |
| `foundation:43` | feature | use | `ApplicationSpecification::MaxFrames`, the middle of the trail |
| `foundation:46` | feature | use | The frame count that ends `Application::Run`, the end of the trail |
| `build-test:40` | feature | use | `compile_commands.json`, which code editors read to jump to definitions |
| `new:21` | hands-on | home | Exercises, each done in the reader's clone and written down as a trail of files and lines: Basic, the startup line "Engine modules: ..." found with `git grep` and followed to `RegisterBuiltinModules`; Medium, the editor's `--idle-timeout` from its usage line to the automation's idle close; Hard, `git log -S c_HeadlessFrameRate` and `git blame` asked why headless runs are capped, down to the commit that set the cap. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:172`; `StrataEditor/src/EditorApplication.cpp:41`, `:77`, `:113-115`; `StrataEditor/src/Editor/EditorAutomation.h:39`; `git log --oneline -S c_HeadlessFrameRate 822a7a46 -- StrataEditor/src/EditorApplication.cpp` prints `d9116fc5 Pace the frames of headless applications` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The source build and the test program | `core/first-change` | must |
| The code style and its naming prefixes | `core/conventions` | must |
| A terminal and git | `basics/git` | must |
| A code editor | `basics/tools` | must |
| Breakpoints and the call stack | `basics/debugging` | helps |
| `std::optional` | `basics/cpp-modern` | helps |

**Starting state.** The end state of `core/first-change`: the repository at the pin, configured with the OS's preset
and built in Debug. No project and no editor run are needed.

**Command-only steps.** none

## `core/first-frame` — From main to the first frame

**Covers.** The job: how a Strata program goes from `main` to its first frame, and how a start that fails ends cleanly
and tells the person why. The problem in a short section: how engines start (init calls written out in `main`,
singletons with start and stop functions, static constructors); the full treatment of subsystems is
`core/engine-modules`'. The map is the start sequence, from `main` to `Run`. The contract, in the order data flows:
`main` in `EntryPoint.h`, the only one the editor and the runtime have; `GetProgramRun`, which decides Console or
Interactive before anything prints (the Windows side is `core/platform`'s); `CreateApplication`, which returns an
`ApplicationLaunch` (registration options and a factory), so that registration happens before the application exists;
the composition root, named in one sentence; `ApplicationSpecification` and each field (name, working directory, window,
`WindowFactory`, `Headless`, `Modules`, `Jobs`, `MaxFrames`, `MaxTimestep`, `MaxFrameRate`; the editor sets `Headless`
for `--headless`, which runs without a window and keeps the graphics device, so captures still work, and for `--no-gpu`,
which drops the device and implies `--headless`); one `Application` at a time; the startup order (power throttling,
working directory, `JobSystem::Init`, the window, `Input::Reset`, the modules made, ordered and started); the failure
paths, which unwind only what started and then report through `ReportFatalError` (the log, and for an Interactive run a
dialog with advice and the log's path; `STRATA_ERROR_DIALOG_FILE` for tests); `CommandLine` and `CommandLineOptions`
(UTF-8 arguments, `--name value`, `--name=value`, flags, sizes `WxH`, unknown arguments and the usage text); the exit
codes 0, 1, 3 and 130, with the note that an exception that leaves the frame loop still ends with 0 (`core/frame-loop`),
and one sentence on the programs' own codes: the runtime's 2 after a script crash in a headless run and a game's quit
code (`worlds/runtime`), the editor's 1 when a command script fails or a headless editor has no automation
(`editor/command-scripts`). The toy is a `main`, an application and a loop in 40 lines; the real code is `EntryPoint.h`,
the constructor, `StartModules` and `ReportFatalError`. The page's example: the editor built in `core/first-change`,
started from a terminal with `--headless --frames 120`, followed to its first frame; then a start that fails, whose
dialog text the test variable writes to a file. The exercises: the exit codes of four runs predicted, then run; a trace
of `--no-gpu` from its usage line to the modules the editor then leaves out; a startup step that fails cleanly. At the
end the reader can trace any Strata program from `main` to its first frame, and add a startup step that fails cleanly.

**Leaves out.**

- The composition root and its registries → `core/layers-registries`
- What engine modules are, their hooks and their order → `core/engine-modules`
- The frame loop that `Run` starts → `core/frame-loop`
- Console and GUI programs on Windows, the standard streams and interrupts → `core/platform`
- The job system that startup creates → `core/jobs`
- The window and its backends → `core/windows-events`
- The editor's options, as a table → `reference/editor`
- The runtime's options → `worlds/runtime`

**Fit.** `fits`: about 4,980 words against L (5,000). The contract of the startup (the specification's fields, the
startup order, the failure paths and the exit codes) with its four quotes takes the most; the three exercises take about
750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:30` | feature | home | The entry point: the one `main` of the editor and the runtime, from the command line to the exit code |
| `foundation:31` | feature | home | `ApplicationLaunch`: registration options and a factory, so that registration happens before the application exists |
| `foundation:32` | feature | home | `GetProgramRun` and `ProgramRun`: Console or Interactive, decided before anything prints; how Windows attaches the streams is `core/platform`'s |
| `foundation:43` | feature | home | `ApplicationSpecification` and each of its fields |
| `foundation:44` | feature | home | The `Application` singleton and what it owns |
| `foundation:45` | feature | home | The startup order |
| `foundation:50` | feature | home | `ReportFatalError`: the log, a dialog for Interactive runs, `STRATA_ERROR_DIALOG_FILE` for tests |
| `foundation:51` | feature | home | The exit codes 0, 1, 3 and 130; how an interrupt sets 130 is `core/platform`'s; a note that an exception that leaves the frame loop still exits with 0 (`core/frame-loop`'s `new:24`); one sentence after the list on the programs' own codes, linking `worlds/runtime` and `editor/command-scripts`: the runtime ends a headless run with 2 after a script crash and exits with a game's quit code (`StrataRuntime/src/RuntimeApplication.cpp:34-35`, `:150-164`), the editor with 1 when a command script fails or a headless editor without `--frames` gets no automation (`StrataEditor/src/EditorLayer.cpp:519-523`, `:541-546`) |
| `foundation:56` | feature | home | `CommandLine` and `CommandLineOptions`: the forms of an option, sizes, unknown arguments and the usage text |
| `foundation:342` | code | home | `Strata/src/Strata/Engine/EntryPoint.h:16-41`: the whole life of a program in 25 lines |
| `foundation:346` | code | home | `Strata/src/Strata/Core/Application.cpp:64-112`: the constructor's startup with its failure path; with `Application.cpp:126-160` (`StartModules`), the unwinding of what started and the report to the person; `ReportFatalError` itself is `Application.cpp:42-62` |
| `foundation:391` | figure | home | The program start sequence, from `main` to `Run` |
| `foundation:439` | figure | home | The fatal-error dialog as an Interactive run shows it; its text can be produced through `STRATA_ERROR_DIALOG_FILE` |
| `foundation:500` | rule | home | One `Application` at a time; tests run several in sequence and never create GPU devices themselves |
| `foundation:548` | term | home | Application |
| `foundation:583` | term | home | Headless: running without a window; the editor's `--headless` keeps the graphics device, so captures still work, and `--no-gpu` drops it and implies `--headless` (`StrataEditor/src/EditorApplication.cpp:70-71`, `:323-324`); the one entry of the word (R33, D34); "no-gpu" is `automation/sessions`' second entry |
| `build-test:670` | term | home | Headless, the same entry as `foundation:583`, with the editor's `--no-gpu`, a run without a graphics device that sets `Headless` too |
| `editor-core:739` | term | home | Headless, the same entry as `foundation:583`, passed by `editor` (the merge "Headless"); the inventory's "without a window or GPU (`--no-gpu`)" is corrected to the two options |
| `worlds-runtime:557` | term | home | Headless, the same entry as `foundation:583`, passed by `worlds` (the merge "Headless"); a run without a window, as servers and CI run games, while `worlds/runtime` keeps headless runs as a feature |
| `new:22` | erratum | home | `plan/inventory/editor-core.md:739` defines headless as running without a window or GPU (`--no-gpu`): these are two options, and the page states both (process.md's row of kind `inventory`). Evidence: `StrataEditor/src/EditorApplication.cpp:70-71` (`--headless` runs without a window, rendering stays available for captures; `--no-gpu` implies `--headless`), `:323-324` |
| `foundation:623` | term | home | Two entries: Console run and Interactive run |
| `foundation:33` | feature | link | The composition root, called by `main` before the application exists |
| `foundation:57` | feature | use | `InstallInterruptHandler`, called by `main`; `core/platform` teaches it |
| `foundation:58` | feature | use | `ConnectStandardStreams`, called first by `main`; `core/platform` teaches it |
| `foundation:59` | feature | use | The power-throttling opt-out as the first step of startup; what it does is `core/platform`'s |
| `build-test:123` | feature | use | `StrataRuntime.Arguments.Help` and `.Unknown`, as how the command line is tested |
| `new:23` | hands-on | home | Exercises: Basic, predict then run: the exit codes of `StrataEditor --help`, of an unknown option, of `--headless --frames 10` and of a headless run stopped with Ctrl+C (0, 3, 0, 130); Medium, trace it yourself: `--no-gpu` from its usage line to `Headless`, the null audio device and the Graphics module left out; Hard, done on the source build: a startup step that fails cleanly in a test application, its dialog text read through `STRATA_ERROR_DIALOG_FILE`. Evidence: `Strata/src/Strata/Core/Application.h:60-71`; `StrataEditor/src/EditorApplication.cpp:70-71`, `:322-333`; `Strata/src/Strata/Core/Application.cpp:42-62`; `StrataTests/src/Editor/StandardStreamsProcessTests.cpp:152` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Asserts, verifies, the log macros and returned errors | `core/conventions` | must |
| `Scope`, `unique_ptr` and object lifetimes | `basics/cpp-memory` | must |
| `std::optional` | `basics/cpp-modern` | must |
| `std::function` and lambdas | `basics/cpp-generic` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| Processes, exit codes and the standard streams | `basics/tools` | must |
| "Module", "layer", "registry" and "service" in their two meanings | `core/map` | must |
| The editor built from source | `core/first-change` | must |
| The composition root and its registries | `core/layers-registries` | helps |
| Engine modules and their hooks | `core/engine-modules` | helps |
| The job system | `core/jobs` | helps |

## `core/frame-loop` — The frame loop

**Covers.** The job: what one turn of Strata's main loop does, in what order, what it counts and how it waits. The
problem section is the part's full one for the loop: why games loop instead of waiting for events as a desktop program
does (the world changes without input); the stages of a frame and why their order matters (input before the update, the
UI after it, presenting last); frame pacing (vsync and the FIFO present mode, caps for headless runs, bursts that catch
up, and why a frame's time must not include its waits). The map is one frame on a time line. The contract, in order:
`Run` (the wall clock, the step clamped to `MaxTimestep`, whose reason is `core/time`'s, a `try` and `catch` around the
frame, in which an escaping exception logs a critical line and ends the loop in order while nothing sets the exit code,
so the program exits with 0, an absence of "What Strata does not do"; the frame counted only when it ran, `MaxFrames`,
the interrupt polled, the pacer's wait); `RunFrame` (the main-thread queue drained; the Input stage, in which the
window's events arrive; a minimized window's frame skipped with a 16 ms sleep and not counted; the modules'
`OnBeginFrame` with Continue, Skip or Close; the layers' `OnUpdate`, then the modules' `OnUpdate` and `OnRenderUI`; the
work time measured; `OnEndFrame` in reverse, where the image is presented, the term Present linked to
`gpu/how-a-gpu-frame-works`); the work time (`GetLastFrameWorkTime`: the frame without what modules wait for and without
stages outside the work time, with its term) and the rule that modules report their waits; `SubmitToMainThread` (a queue
under a mutex, drained at the start of every frame and once after the last); `FramePacer` and `SetMaxFrameRate` (a fixed
schedule without bursts, changed while running; the editor's idle throttling uses it) and the promise of
`Platform::SleepUntil`; `Timer`, `Time::GetTime` and `Timestep`; the shutdown order in `Run` and in the destructor. The
module hooks and the layers are named as what the loop calls; their contracts follow on `core/windows-events` and
`core/engine-modules`. The toy is a loop of 50 lines; the real code is `Run`, `RunFrame` and `FramePacer`. The exercise
traces one frame of the editor with breakpoints. At the end the reader can say what runs in a frame and in which order,
why a frame is skipped or not counted, and what the frame's work time leaves out.

**Leaves out.**

- Delta time, the fixed step and time scale → `core/time`
- Events, the window and the layer stack → `core/windows-events`
- The module hooks' contracts and their order → `core/engine-modules`
- How the GPU frame is begun, waited for and presented → `gpu/vulkan-nvrhi`
- Frames in flight, and the term Present → `gpu/how-a-gpu-frame-works`
- How each OS sleeps until a deadline → `core/platform`
- The frame profiler and its stages → `core/profiling`
- The editor's idle throttling and its preferences → `editor-ui/status`

**Fit.** `fits`: about 4,400 words against L (5,000). The problem section's three concepts and the contract of `Run` and
`RunFrame` with three quotes take the most; the missing failure exit code takes one paragraph.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:214` | concept | home | The game loop: why games loop, and its general forms |
| `foundation:220` | concept | home | The stages of a frame and why their order matters |
| `foundation:234` | concept | home | Frame pacing and vsync: present modes, caps for headless runs, schedules without catch-up bursts, a frame's time without its waits; the precision of sleeping is named, and taught on `core/platform` |
| `foundation:46` | feature | home | `Run` and `RunFrame`; with the `Run` excerpt, one sentence on an exception that escapes a frame: the critical line, the ordered end, and exit code 0, since nothing sets another (`new:24`) |
| `foundation:47` | feature | home | Frame skipping: a minimized window or a module's Skip sleeps 16 ms and is not counted |
| `foundation:48` | feature | home | The frame's work time and what it leaves out |
| `editor-ui:779` | term | home | Frame work time, the CPU time a frame costs without its waits: one entry with `foundation:582` (work time), beside its feature `foundation:48`, passed by `editor-ui` (the merge "Frame work time"); `editor-ui/status` links it |
| `foundation:49` | feature | home | `SubmitToMainThread` and its queue |
| `foundation:52` | feature | home | The shutdown order, in `Run` and in the destructor |
| `foundation:54` | feature | home | `FramePacer` and `SetMaxFrameRate`; the editor's idle throttling as one user |
| `foundation:55` | feature | home | `Timer`, `Time::GetTime` (double seconds since the start) and `Timestep` (float seconds) |
| `foundation:344` | code | home | `Strata/src/Strata/Core/Application.cpp:226-283`: `Run`: the clamped step, the `try` and `catch`, the frame count, the interrupt, the pacer and the ordered end |
| `foundation:345` | code | home | `Strata/src/Strata/Core/Application.cpp:285-344`: `RunFrame`: the queue, the Input stage, the skipped frame, the hooks' order, the work time |
| `foundation:363` | code | home | `Strata/src/Strata/Core/Timer.h:51-104`: `FramePacer`, a fixed schedule without catch-up bursts |
| `foundation:395` | figure | home | One frame on a time line, the waits shaded, a brace over what `GetLastFrameWorkTime` counts |
| `foundation:463` | rule | home | Report waits in `EngineFrame::WaitSeconds`, and time waits outside the work time as stages outside it |
| `foundation:514` | hands-on | home | Trace a frame: breakpoints in `Application::RunFrame` and in the built-in modules' hooks, the order written down and compared with the code |
| `foundation:570` | term | home | Frame loop, also called game loop |
| `foundation:578` | term | home | Two entries: frame pacing and frame-rate cap |
| `foundation:579` | term | home | Two entries: vsync and the FIFO present mode |
| `foundation:582` | term | home | Work time |
| `foundation:588` | term | home | Main thread |
| `foundation:589` | term | home | Main-thread queue |
| `render-core:55` | feature | home | The frame's order as the renderer's inventory states it (the Graphics module's `OnBeginFrame`, ImGui's `OnRenderUI` with `PrepareBackBuffer`, the present in `OnEndFrame`), taught with the loop that runs it |
| `foundation:183` | feature | use | The clamp of the step to 0.25 s, seen in `Run`; why it exists is `core/time`'s |
| `foundation:112` | feature | use | `Platform::SleepUntil`, as the pacer's promise; its implementations are `core/platform`'s |
| `foundation:569` | term | link | Frame, whose entry is `start/what-an-engine-is`' |
| `foundation:581` | term | link | Present, named where `OnEndFrame` presents the image; its entry is `gpu/how-a-gpu-frame-works`' (R31, Present) |
| `new:24` | not-done | home | No failure exit code after an exception leaves the frame loop: `Run` catches it, logs a critical line and ends in order, and nothing sets the exit code, so the program exits with 0 unless a layer set another code; no test covers the path. One paragraph by book.md's rule 1, beside the sentence of `foundation:46`; the page says what the pin does, and the fix asked of the engine (pipelines.md §11; R34, R47) is not the page's. Evidence: `Strata/src/Strata/Core/Application.cpp:243-253`; `Strata/src/Strata/Engine/EntryPoint.h:35-36`; `git grep -n "Unhandled exception" 822a7a46 -- StrataTests` finds nothing |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The startup, `ApplicationSpecification` and the `Application` | `core/first-frame` | must |
| Threads and mutexes | `basics/threads` | must |
| `std::function` and lambdas | `basics/cpp-generic` | must |
| `std::span` | `basics/cpp-modern` | helps |
| Reverse iterators | `basics/cpp-generic` | helps |
| The frame map: the CPU prepares a frame while the GPU draws the one before | `start/what-an-engine-is` | must |
| Breakpoints and stepping, for the exercise | `basics/debugging` | must |
| Events and the layer stack | `core/windows-events` | helps |
| The module hooks | `core/engine-modules` | helps |
| Frames in flight and the wait for vsync | `gpu/how-a-gpu-frame-works` | helps |

## `core/time` — Time: delta time, the fixed step and time scale

**Covers.** The problem as the reader meets it: a ball moved by a fixed distance each frame crosses the screen twice as
fast on a computer twice as fast, and a physics step that changes with the frame's length makes bodies jitter or fly
apart. The naive answer, multiplying by the frame's delta time, and where it breaks: a breakpoint or a loading hitch
makes one huge step, physics needs equal steps to stay stable, and no run repeats another. Clocks first: the wall clock,
which jumps, against the monotonic clock; double for absolute time and float for short steps; the clamp against long
frames. The idea: simulate in fixed steps that an accumulator pays out of the frames' time; the spiral of death when
steps cost more than they simulate; time scale and unscaled time; interpolation in one paragraph (draw between the last
two steps at one step of latency, or extrapolate; Strata's interpolated set is `world/interpolation`'s). The approaches,
with a table of their costs: a fixed frame rate in lockstep, a variable step, a semi-fixed step, the accumulator with a
cap, and time dilation. Strata's choice: a variable step clamped to 0.25 s for the frame's work; the scene's
accumulator, capped by `GetMaxFixedSteps` (steps of 2/15 s at the project's rate) with the backlog dropped; time
dilation in programs that run on the wall clock, and never in runs that must repeat; the project's `Scene.Timing`
`FixedRate` (30, 60, 120 or 240 steps per second) over every scene's own step; `OnUpdate`, the steps' `OnFixedUpdate`,
then `OnLateUpdate`; time scale and unscaled time; pausing and `Step`. The design decision as a `:::why`: game time
counts fixed steps (`Scene::GetFixedStepCount`), never frames, and so do the tools (the rule's home; the editor's
exception, input holds that also count frozen frames, is `editor/stepping`'s). The accumulator's code is
`world/systems`' walk-through; this page shows its behaviour as numbers, in a table of uneven frames as `SceneTests.cpp`
checks it. What the choice cannot do: one step serves scripts, physics and animation together, and no system runs at a
rate of its own. The common mistakes: physics in `OnUpdate`, multiplying by the frame's delta in `OnFixedUpdate`,
counting frames in tests, `system_clock` for game time, float absolute time after hours, a teleport that does not break
the interpolation. The exercises: the accumulator written in a toy loop and compared with the engine's; the Physics
Playground at `FixedRate` 30 and 240, with its steps in the editor written out; one object moved in `OnUpdate` and one
in `OnFixedUpdate` at two frame caps. At the end the reader can predict how many fixed steps a frame runs, why the
backlog is dropped and when time dilates.

**Leaves out.**

- The accumulator's code in `Scene` → `world/systems`
- Interpolation: the interpolated set, its roles and drawn transforms → `world/interpolation`
- Pausing and stepping in the editor, and holds counted in fixed steps → `editor/stepping`
- The `Scene.Timing` section's validation and its hand-over to scenes → `world/projects-settings`
- Integrating bodies inside a step → `physics/dynamics`
- Time from a script's side: the callbacks and `Time`'s clocks → `make/script-loop`
- The runtime's `--frames` and `--seconds` → `worlds/runtime`

**Fit.** `fits`: about 4,650 words against L (5,000). The two concepts with the approaches table take the most, then
Strata's choice with the design decision's `:::why`, which now also holds the rule that tools count fixed steps; three
exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:224` | concept | home | Time: the wall clock and the monotonic clock, double and float, the clamp, frames against game time |
| `foundation:228` | concept | home | The fixed step, the accumulator, the spiral of death, time scale, interpolation in one paragraph; the approaches and their costs |
| `foundation:183` | feature | home | The variable step: the wall time since the previous frame, clamped to 0.25 s (`MaxTimestep`) |
| `foundation:184` | feature | home | The accumulator as Strata runs it: `OnUpdate`, the due `OnFixedUpdate` steps up to `GetMaxFixedSteps`, the backlog dropped, `OnLateUpdate`; time scale and unscaled time; its code is `world/systems`' |
| `foundation:185` | feature | home | Time dilation: catch-up steps stop once they take longer in wall time than they simulate |
| `foundation:187` | feature | home | The project's `Scene.Timing` `FixedRate` over the scenes' own steps, and the cap of `ceil(rate * 2 / 15)` steps; the section's mechanism is `world/projects-settings`' |
| `foundation:406` | figure | home | The fixed step on a time axis: uneven frames filling the accumulator, steps falling out, the cap dropping the backlog, the interpolation's alpha one step behind |
| `foundation:489` | rule | home | Steps are clamped (0.25 s) and fixed-step backlogs dropped |
| `foundation:491` | rule | home | Read the step through `Scene::GetFixedTimestep` and `GetMaxFixedSteps`; count game time in fixed steps, never frames (the design decision's `:::why`) |
| `foundation:524` | hands-on | home | The accumulator written in a toy loop (uneven frames, the cap, the dropped backlog, the alpha), then compared with the engine's |
| `foundation:538` | hands-on | home | The Physics Playground at `FixedRate` 30 and 240: what changes in contacts and smoothness |
| `foundation:539` | hands-on | home | One object moved in `OnUpdate` and one in `OnFixedUpdate`, played at two frame caps |
| `foundation:571` | term | home | Two entries: timestep and delta time |
| `foundation:572` | term | home | Fixed timestep |
| `foundation:573` | term | home | Accumulator |
| `foundation:574` | term | home | Spiral of death |
| `foundation:575` | term | home | Time dilation |
| `foundation:577` | term | home | Two entries: time scale and unscaled time |
| `scene-ecs:316` | concept | home | Game loop time from the scene's side, the same concept as `foundation:228`: the accumulator, the cap, the dropped backlog, time scale, pausing and single steps, `GetFixedStepCount` as the tools' time base |
| `scene-ecs:436` | figure | home | The accumulator's timeline, the same figure as `foundation:406`, with the case of time dilation drawn in |
| `scene-ecs:541` | rule | home | Tools count game time in fixed steps, never frames: the design decision's `:::why`, with `foundation:491` |
| `editor-core:580` | rule | home | Tools count game time in fixed steps, never frames, as the editor's guide states it (frames differ per machine; steps make tests exact): one rule box with `scene-ecs:541` and `foundation:491`, passed by `editor` (R31, "Fixed steps, never frames"); `editor/stepping` keeps the exception (input holds also count frozen frames) and links |
| `scene-ecs:637-641` | term | home | Fixed timestep, accumulator, spiral of death, time dilation, and time scale with unscaled time: the same entries as this page's own |
| `audio-input:690`, `editor-core:691`, `worlds-runtime:564` | term | home | Fixed step, the same entry as `foundation:572` |
| `editor-core:692`, `worlds-runtime:563` | term | home | Time dilation, the same entry as `foundation:575` |
| `scripting:617` | term | home | Time scale, the same entry as `foundation:577` |
| `foundation:186` | feature | use | Pausing, `Step` and `GetFixedStepCount` as the clock tools count by; the mechanism is `editor/stepping`'s |
| `foundation:188` | feature | link | Interpolation of drawn transforms, named in its one paragraph |
| `foundation:576` | term | link | Interpolation (render), whose entry is `world/interpolation`'s |
| `foundation:369` | code | use | The accumulator's excerpt, placed with `scene-ecs:388` and linked, not quoted |
| `scene-ecs:107` | feature | use | `OnUpdateRuntime`'s order of phases, as the scene runs them |
| `scene-ecs:111` | feature | use | Time dilation and `GetDroppedFixedStepCount` |
| `scene-ecs:113` | feature | use | `SceneSettings`' fixed step and maximum steps, which the project's rate overrides |
| `scene-ecs:222` | feature | use | The `Scene.Timing` section |
| `scene-ecs:388` | code | use | The accumulator's code, linked to its walk-through on `world/systems` |
| `scene-ecs:389` | code | use | The accumulator's behaviour as numbers: the source of the page's table of uneven frames |
| `scene-ecs:539` | rule | use | Read the step through `Scene`, from the scene's side |
| `physics:156`, `physics:158` | feature | use | The accumulator and `Scene.Timing` from physics' side |
| `physics:241` | concept | use | Why physics needs a fixed step: stability, determinism and repeatable runs |
| `physics:396`, `physics:398` | rule | use | Read the step through `Scene`; tools count fixed steps |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop, `Timestep` and the clamp in `Run` | `core/frame-loop` | must |
| Rates, accumulation and Euler steps | `basics/math-change` | must |
| Floating-point precision | `basics/numbers` | must |
| A script's `OnUpdate` and its delta time | `start/first-game` | helps |
| Opening a sample from the launcher | `start/first-game` | helps |
| Lerp | `basics/math-interpolation` | helps |
| A scene and its systems | `world/systems` | helps |
| Rigid bodies and their integration | `physics/dynamics` | helps |

## `core/windows-events` — Windows, events and layers

**Covers.** The job: how what happens to a window reaches the engine as events, how the polled input state is filled
first, and how a program is cut into layers. The problem in a short section: events against polling (callbacks from the
window system, an object per happening, dispatch by type, a flag that stops it; polling for keys held down), and stacked
layers with overlays (updates from the bottom up, events from the top down). The map is the path of an event. The
contract: the `Window` interface and `WindowSpecification` (events, the framebuffer's size, the content scale taught
from zero as its home: the OS's factor of display density, 2 on a Retina display, whose window of 1600 by 900 points has
3200 by 1800 pixels, one value for both axes, which the window reports and raises an event for; vsync; the Windowed,
Fullscreen and Borderless modes and what each does: Fullscreen switches the display to the resolution asked for,
Borderless covers the display at the desktop's mode, Windowed restores the last windowed place and size, and a window
made with `WindowSpecification::Fullscreen` starts Borderless; the resolution, which sets the framebuffer in Windowed
and the display mode in Fullscreen; the cursor's shape, the clipboard, layout keys, the icon, and the Vulkan
presentation it hands the device); the GLFW backend (GLFW started with the first window, with the engine's Vulkan
loader; each callback feeds `Input::Process*` first and then makes an event; `ProcessEvents` is `glfwPollEvents`, so
events run inside it, at once, never queued); the backend without a window (`STRATA_WITH_GLFW` off: `Window::Create`
returns null with an error) and a window handed in (`WindowFactory`, `Tests::StubWindow`); the event classes (15 types,
the categories as bit flags in a plain enum that avoids X11's `None`, the macros, `Handled`); `EventDispatcher`;
propagation (the application's own bookkeeping, the modules in their order, the layers from the top down with overlays
first, stopping at `Handled`; a window close that nobody handles ends the loop, so a layer can veto it, as the editor
does to ask about unsaved changes); `Layer` and `LayerStack` (one insert index between layers and overlays; the stack
owns the raw `Layer*` it is given and deletes them from the top down). The toy is an event type, a dispatcher and a
stack of two layers in 40 lines; the real code is `Event.h`, the GLFW callbacks of the window's size and close (the key
callback is named and linked to `input/devices-state`, which quotes it), `Application::OnEvent` and `LayerStack.cpp`.
The page's example: a key press followed from GLFW to the editor's layer, and a window close that the editor's layer
vetoes. The exercises: who sees an event first, predicted; a close followed from GLFW's callback to the veto; a test
layer fed by `Tests::StubWindow`. At the end the reader can add an event type or a layer and predict who sees an event
first.

**Leaves out.**

- Input devices, key states and edges → `input/devices-state`
- How input reaches a game: events, polling and intents → `input/how-input-works`
- The cursor and the game view's mouse → `input/mouse-cursor`
- The swapchain and presentation → `gpu/vulkan-nvrhi`
- ImGui's overlay and its backends → `editor-ui/imgui-backends`
- The editor's layer and its unsaved-changes question → `editor-ui/shell`
- The module hooks other than `OnEvent` → `core/engine-modules`

**Fit.** `fits`: about 4,950 words against L (5,000). The window's contract, now with the modes and content scale taught
from zero, and the path of an event with four quotes take the most; the key callback's quote left for
`input/devices-state` (about 120 fewer), and the three exercises take about 750.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:239` | concept | home | Events against polling: callbacks, an event hierarchy, dispatch by type, `Handled`; Strata's events run at once, beside the polled `Input` that the window fills first; the mistakes (game input through events, events thought to be queued) |
| `foundation:245` | concept | home | Layers and overlays: updates from the bottom up, events from the top down; the editor and the runtime each push one layer, ImGui's module an overlay; the stack deletes the raw pointers it was given |
| `foundation:77` | feature | home | The event classes |
| `foundation:78` | feature | home | `EventDispatcher` |
| `foundation:79` | feature | home | Event propagation and the close veto |
| `foundation:80` | feature | home | The `Window` interface and `WindowSpecification`, with the modes' contract (about 120 words): Fullscreen switches the display to the resolution asked for, Borderless covers the display at the desktop's mode without a switch, Windowed restores the last windowed place and size; a window made with `WindowSpecification::Fullscreen` starts Borderless, so a game whose manifest says `Fullscreen` starts borderless; `SetResolution` sets the framebuffer in Windowed and the display mode in Fullscreen (`Strata/src/Strata/Core/Window.h:45-51`, `:93-99`); `make/menus` uses one sentence of it |
| `foundation:81` | feature | home | The GLFW backend, with how it carries out the modes: the Borderless start of a Fullscreen specification and the switches between modes (`Strata/src/Platform/GLFW/GLFWWindow.cpp:180-188`, `:466-513`) |
| `gameui:624` | term | home | Content scale (DPI scale): the display's density as a factor, 2 on a Retina display (`Docs/Architecture.md:543`); taught from zero in the window's contract (`GetContentScale`, one value for both axes, the larger, and `WindowContentScaleEvent`: `Strata/src/Strata/Core/Window.h:86-87`, `Strata/src/Platform/GLFW/GLFWWindow.cpp:277-283`), passed by `ui` (R31, D33); `ui/layout` says it in one sentence and links |
| `editor-ui:721` | term | home | Content scale, the OS's factor for display density: one entry with `gameui:624`, passed by `editor-ui` (R31, D33); `editor-ui/ui-scale` uses it with a link |
| `foundation:82` | feature | home | The backend without a window |
| `foundation:83` | feature | home | `WindowFactory` and `Tests::StubWindow` |
| `foundation:53` | feature | home | `Layer` and `LayerStack` |
| `audio-input:187` | feature | home | The event classes of `Strata/src/Strata/Events/` that the GLFW callbacks emit beside the polled state, the same classes as `foundation:77`; `input/how-input-works` uses them to set events against polling |
| `foundation:350` | code | home | `Strata/src/Strata/Events/Event.h:15-81`: types without RTTI, categories as bit flags, the templated dispatcher |
| `foundation:352` | code | home | `Strata/src/Platform/GLFW/GLFWWindow.cpp:230-249`: C callbacks with a user pointer turned into engine events (the window's size and close); the key callback, which feeds the polled `Input` before its event (286-319), is named and linked to `input/devices-state`, which quotes it (the merge "GLFW key callback", about 120 words fewer) |
| `audio-input:379` | code | link | The key callback, `GLFWWindow.cpp:286-319`, named where the polled `Input` is fed first; its excerpt is `input/devices-state`'s |
| `foundation:347` | code | home | `Strata/src/Strata/Core/Application.cpp:202-224`: propagation with `Handled`, and the close veto |
| `foundation:351` | code | home | `Strata/src/Strata/Core/LayerStack.cpp:7-54`: layers and overlays with one insert index; detaching from the top down |
| `foundation:404` | figure | home | The path of an event from the window's callback to the layers, with the veto's branch |
| `foundation:560` | term | home | Overlay |
| `foundation:584` | term | home | Event |
| `foundation:585` | term | home | Dispatcher |
| `foundation:586` | term | home | Handled flag |
| `foundation:620` | term | home | GLFW |
| `foundation:621` | term | home | Window backend |
| `foundation:710` | open | home | The page does not say where the design of `Layer`, `LayerStack`, `Event` and `ST_BIND_EVENT_FN` came from: no document of the engine says so, and `AGENTS.md` names "Hazel conventions" for the code style only |
| `foundation:84` | feature | use | `VulkanLoader` and `VulkanPresentation`, as what `GetVulkanPresentation` hands the device; their home is `gpu/vulkan-nvrhi` |
| `foundation:587` | term | link | Polling input, whose entry is `input/how-input-works`' |
| `new:25` | hands-on | home | Exercises: Basic, predict who sees a key press first, the editor's layer or ImGui's overlay, and where it stops when one sets `Handled`; Medium, trace it yourself: a window close from GLFW's close callback through `Application::OnEvent` to the editor's veto, with breakpoints; Hard, done on the source build: a test layer that counts resize and content-scale events, fed by `Tests::StubWindow` through `WindowFactory`. Evidence: `Strata/src/Strata/Core/Application.cpp:202-224`; `Strata/src/Platform/GLFW/GLFWWindow.cpp:243-249`; `StrataTests/src/StubWindow.h:20-37`; `StrataTests/src/Core/WindowBackendTests.cpp:64-74` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop and its Input stage | `core/frame-loop` | must |
| Virtual functions, inheritance and interfaces | `basics/cpp-classes` | must |
| Templates and lambdas | `basics/cpp-generic` | must |
| Bit flags and masks | `basics/numbers` | must |
| Raw pointers and who deletes them | `basics/cpp-memory` | must |
| Macros | `basics/cpp-modern` | must |
| C callbacks: function pointers and a user pointer | `basics/cpp-generic` | helps |
| How input reaches a game | `input/how-input-works` | helps |
| X11's `None` and the rule that keeps platform headers in their folders | `core/platform` | helps |

## `core/engine-modules` — Engine modules

**Covers.** The job: how the services that live as long as the program (the graphics device, audio, ImGui, the
project) start in order, run their hooks every frame, stop in reverse, fail cleanly, and are found by other code. The
problem in the part's full section on it: subsystems and their lifecycles (init calls written out in `main`, singleton
managers with start and stop functions, module systems such as Unreal's `IModuleInterface`, service locators), the
order problem, and a module that frees GPU resources after the device is gone. Then the topological sort from zero, as
its home: a graph of "starts after", in-degrees, Kahn's algorithm worked on the test's four modules (C needs A; A; B
after C, optional; D after a missing module, optional: the order A, C, B, D), stability (the first ready module in the
program's listing order) and cycles reported by their members only. The map is the hook order of two modules where B
depends on A. The contract: the `EngineModule` hooks (`OnInit`, `GetStartFailure`, `OnBeginFrame` with Continue, Skip
or Close, `OnUpdate`, `OnRenderUI`, `OnEndFrame`, `OnEvent`, `OnStop`, `OnRelease`, `OnShutdown`), `c_Name` and
`GetDependencies` with `Required`; `EngineContext`, `EngineFrame`, `EngineFrameAction` and `EngineModuleStartFailure`;
`EngineModuleRegistry` (made from factories; it refuses null factories, duplicate names, missing required dependencies
and cycles; `Find<T>()` finds by `T::c_Name`, without RTTI); the rules (`Application` never names a module, and
`Find<T>()` may return null; a module that fails `OnInit` cleans up and describes the failure; `OnRelease` comes before
`JobSystem::Shutdown`, `OnShutdown` after). The built-in modules (Graphics, Audio, ImGui and Project) and the programs'
module lists (the editor with a window, headless and without a GPU; the runtime with a window and headless); where the
device is made, in one paragraph. Engine services, as their home: typed slots for the whole process (`Register<T>`,
`Get<T>`, `ScopedProvider<T>`) for what a module cannot include (`IGameWindow`, `IGameSaves`, `IGameGraphics`,
`IProjectSettings`, `IAudioOutput`, `IAssetGraphics`), a minimal service locator. The toy is Kahn's sort in 30 lines;
the real code is the hook interface, the registry's sort and its cycle report, `EngineServices.h`, and `ProjectModule`,
the smallest real module. The required exercise: write a `FrameCounterModule` (`c_Name`, `Factory`, `OnUpdate`
counting frames, `OnStop` logging), find it with `Find<T>()`, and test it in the style of `EngineModuleTests.cpp`'s
journaling module; two more exercises: a module that depends on "Graphics" and one whose optional dependency is
missing, with a cycle's message; a module that skips every tenth frame; and a trace of the editor's module list from
`EditorApplication.cpp` through the registry's sort to `StartModules`, with breakpoints. At the end the reader can
write, order and test an engine module, and find a service without naming its module.

**Leaves out.**

- How the graphics device and the swapchain are made → `gpu/vulkan-nvrhi`
- The audio engine behind the Audio module → `audio/engine`
- ImGui's module and backends → `editor-ui/imgui-backends`
- Projects and their settings, behind the Project module → `world/projects-settings`
- Registration into registries and the composition root → `core/layers-registries`
- Scene services → `world/systems`
- Graphs and their costs in general → `basics/trees-graphs`

**Fit.** `fits`: about 5,150 words against L (5,000). The two concepts taught from zero (Kahn's algorithm has its home
here) and the hooks' contract with four quotes take the most; the four exercises, the required one with a patch as its
worked solution, take about 1,000.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:249` | concept | home | Subsystems and their lifecycles: the approaches engines use and their costs; the module that frees GPU resources too late |
| `foundation:256` | concept | home | Topological sorting from zero: graphs, in-degrees, Kahn's algorithm, stability, cycles and their report |
| `foundation:65` | feature | home | The `EngineModule` interface and its hooks |
| `foundation:66` | feature | home | `EngineContext`, `EngineFrame`, `EngineFrameAction` and `EngineModuleStartFailure` |
| `foundation:67` | feature | home | `EngineModuleRegistry`: the stable sort, the refusals, `Find<T>()` without RTTI |
| `foundation:68` | feature | home | The built-in modules Graphics, Audio, ImGui and Project, a paragraph each; each module's details are its part's |
| `foundation:69` | feature | home | The programs' module lists |
| `foundation:71` | feature | home | `EngineServices`: typed provider slots, scoped providers and the interfaces they hold |
| `foundation:348` | code | home | `Strata/src/Strata/Core/EngineModule.h:22-106`: a lifecycle interface whose comments state the hooks' contract |
| `foundation:349` | code | home | `Strata/src/Strata/Core/EngineModule.cpp:49-186`: the registry's `Create`, with Kahn's sort taking the first ready module in listing order and a report that names only a cycle's members |
| `foundation:371` | code | home | `Strata/src/Strata/Core/EngineServices.h:21-69`: a minimal typed service locator with variable templates and scoped providers |
| `foundation:399` | figure | home | The hook order in two lanes, A and B where B depends on A, as `EngineModuleTests.cpp` proves it |
| `foundation:402` | figure | home | Kahn's algorithm worked on the test's four modules |
| `foundation:456` | rule | home | `Application` never names a module; `GetModules().Find<T>()` may return null |
| `foundation:458` | rule | home | A module that fails `OnInit` cleans up what it started and describes the failure |
| `foundation:461` | rule | home | `OnRelease` comes before `JobSystem::Shutdown`, `OnShutdown` after |
| `foundation:515` | hands-on | home | The required exercise: a `FrameCounterModule`, found with `Find<T>()` and tested in the style of `EngineModuleTests.cpp`; its worked solution is a patch against the pin |
| `foundation:516` | hands-on | home | A module that depends on "Graphics", one whose optional dependency is missing, and a cycle's message |
| `foundation:517` | hands-on | home | A module that skips every tenth frame, and the frame count that results |
| `new:26` | hands-on | home | Trace it yourself: the editor's modules followed with breakpoints from the list `EditorApplication.cpp` builds (Graphics unless `--no-gpu`, Audio, ImGui with a window, Project) through `EngineModuleRegistry::Create`'s sort to `StartModules`, the order written down and compared with the dependencies. Evidence: `StrataEditor/src/EditorApplication.cpp:330-345`; `Strata/src/Strata/Core/EngineModule.cpp:49-186`; `Strata/src/Strata/Core/Application.cpp:126-160` |
| `foundation:557` | term | home | Hook |
| `foundation:566` | term | home | Service locator |
| `foundation:567` | term | home | Topological sort |
| `foundation:568` | term | home | Kahn's algorithm |
| `foundation:554` | term | home | Engine module (`EngineModule`): a service that lives as long as the program; `core/map` sets it against the module's registration |
| `foundation:565` | term | home | Engine service (`EngineServices::Get<T>`), the engine's meaning of "service"; `core/map` sets it against the scene service |
| `scene-ecs:646`, `scripting:580` | term | home | Engine service, the same entry as `foundation:565`'s second term |
| `foundation:373` | code | use | Its pieces about modules: `Strata/src/Strata/Project/ProjectModule.cpp` 10-24 (the smallest real module, the exercise's model), `Strata/src/Strata/Renderer/GraphicsModule.cpp` 26-85 (a module that reports waits and start failures) and `StrataTests/src/Core/EngineModuleTests.cpp` 62-120 and 289-334 (the journaling test module); the item's home is `core/math` |
| `foundation:70` | feature | use | Where the device is made, in one paragraph; the detail is `gpu/vulkan-nvrhi`'s |
| `render-core:52` | feature | use | `GraphicsModule`, the module with the most hooks, as the example of a real module's frame |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Graphs and dependency graphs | `basics/trees-graphs` | must |
| Virtual functions and interfaces | `basics/cpp-classes` | must |
| `Scope`, `unique_ptr` and factories | `basics/cpp-memory` | must |
| Templates and `std::function` | `basics/cpp-generic` | must |
| The startup that makes, orders and starts the modules | `core/first-frame` | must |
| The frame loop that calls the hooks | `core/frame-loop` | must |
| Writing and running one test case | `core/first-change` | must |
| Events and `Handled`, for `OnEvent` | `core/windows-events` | helps |
| The graphics device | `gpu/vulkan-nvrhi` | helps |

## `core/layers-registries` — Layers, registries and the composition root

**Covers.** The job: how Strata keeps lower code from depending on higher code, and how every module registers once, in
one place, before anything reads a registry. The problem in the part's full section on it: layered architecture and why
lower code must not call higher code; dependency inversion (interfaces below and implementations above, registries
filled from above, services); self-registration through static constructors, common and fragile (the linker drops
objects of a static library that nothing references, and the order of static initialization is undefined), against an
explicit composition root. The map is the layer DAG: 19 layers, the arrows of `MayInclude`, the tooling layers to the
side. The contract, the layers first: `Layers.json` (each layer's `Paths`, `Exclude`, `MayInclude`, `Tooling`, `Option`
and `Notes`; `ExternalOwners`, which keeps GLFW, Vulkan and OS headers in their Platform folders; `MaxAllowlistEntries`
0 and an empty allowlist); the `Architecture.Layering` test, which reads every include and also fails on an allowlist
line that matches no forbidden include, with `Architecture.Libraries` beside it, which checks that every engine source
is in the library of its one layer and that each library links exactly the built layers its layer may include; and the
rule: never widen `MayInclude` or add an allowlist line, invert the dependency. Then the composition root:
`Engine::RegisterBuiltinModules` (it opens the registries, runs the nine modules' registrations from a table in layer
order, refuses to exclude Input, Scene and Renderer, runs the asset pipeline and the `Extra` registrations, freezes the
component and settings registries, logs the order of the scene systems; a second call does nothing but log an error);
`ModuleRegistrationOptions` (`AssetPipeline`, handed in so that games never link the importers; `Extra`; `Exclude`); the
functions that report what registered; the registration state machine (atomic; a registry used before registration fails
a verify that names the root); the two kinds of registry: the component and settings registries open, accept and then
freeze, and a frozen registry needs no lock; the asset loader, asset-manager extension, built-in asset, mesh geometry
and scene-system registries, which the root opens, and the importer registry, which the asset pipeline opens, never
freeze, each with its own lock or rule (tools and tests register more later, a later loader or importer overrides the
built-in one, the loader registry locks on every lookup, a scene system is refused only while a scene runs); optional
modules (`ST_WITH_PHYSICS`, `_AUDIO`, `_ANIMATION`) with `#if` only in the root, the asset pipeline, the runtime and
tests; "no tooling in games" as a rule (its proof in CMake is `engineering/cmake`'s). What Strata does not do here:
engine plugins loaded while the program runs, and a build without scripting. The errata the page must not repeat are
listed below. The toy is a composition root with two registries in 40 lines; the real code is the module table, the body
of `RegisterBuiltinModules` and the start of `Layers.json`. The page's example is the editor's own registration as its
startup log reports it. The exercises: a GLFW include in a Scene file, read from the test's failure and fixed by
inversion; a game component registered through `Extra`, then once more after the freeze; a test helper with
`Exclude = {"Physics"}`; a trace of `RegisterBuiltinModules` from `main` with breakpoints, which writes down which
registries it opens and which two it freezes. At the end the reader can say which layer may include which, fix a
forbidden include by inverting the dependency, and register a game's component or settings section in the right place.

**Leaves out.**

- The CMake that makes the layer libraries and proves that games hold no tooling → `engineering/cmake`
- Precompiled headers and the weight of headers → `engineering/flags-portability`
- `ComponentRegistry`'s builder → `world/reflection`
- The scene-system registry and the order of systems → `world/systems`
- The importer and loader registries → `assets/importing`
- Settings sections and their validation → `world/projects-settings`
- Platform headers in their folders, as a rule of platform code → `core/platform`
- Script modules, the one kind of code loaded while the program runs → `scripting/loading`

**Fit.** `fits`: about 5,800 words against L (5,000). The composition root with the two kinds of registry, and the layer
table with its tests, take the most; four errata, two absences and four exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:259` | concept | home | Layered architecture and dependency inversion: interfaces below, registries filled from above, services; the layer table that is the build; the mistake of widening `MayInclude` |
| `foundation:264` | concept | home | The composition root against self-registration through static constructors (dropped by linkers, run in undefined order); the two kinds of registry, those that open, accept and freeze (components and settings, which need no lock once frozen) and those the root opens and leaves open, each with its own lock or rule (asset loaders, importers, built-in assets, manager extensions, mesh geometry, scene systems); the mistakes (registering a component or a settings section after the freeze, or registering from a static constructor) |
| `foundation:173` | feature | home | The layer table and its fields, and the empty allowlist |
| `foundation:175` | feature | home | The `Architecture.*` tests: `Layering`'s include analyzer and `Libraries`; the precompiled-header and header-weight tests are named and left to `engineering/flags-portability` |
| `foundation:176` | feature | home | `ExternalOwners`: GLFW, Vulkan and OS headers only in their Platform folders |
| `foundation:33` | feature | home | The composition root `Engine::RegisterBuiltinModules` |
| `foundation:34` | feature | home | `ModuleRegistrationOptions`: `AssetPipeline`, `Extra` and `Exclude` |
| `foundation:35` | feature | home | `GetBuiltinModuleNames`, `GetRegisteredModules` and `AreBuiltinModulesRegistered` |
| `foundation:36` | feature | home | The optional modules `ST_WITH_PHYSICS`, `_AUDIO` and `_ANIMATION` |
| `foundation:37` | feature | home | The registration state machine and the verify that names the root |
| `foundation:343` | code | home | `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77`: the table of registration functions in layer order, with `#if ST_WITH_*` only here; with `BuiltinModules.cpp:118-174`, open, register and freeze |
| `new:11` | code | home | `StrataTests/Architecture/Layers.json:1-24`: the table's description, `MaxAllowlistEntries` and its first three layers (Core, Input and App) with their `Paths`, `Exclude` and `MayInclude` |
| `foundation:388` | figure | home | The layer DAG: 19 layers, the arrows of `MayInclude`, tooling to the side, the dependencies of Audio and Project on App marked |
| `scene-ecs:447` | figure | home | The registration lifecycle as a state machine, labelled as the component registry's (the settings registry freezes too; the other registries stay open): closed, open (the modules in table order, then the asset pipeline, then `Extra`), frozen, and what fails in each state |
| `worlds-runtime:140` | feature | home | No tooling in games: the runtime links no editor, asset-pipeline or network layer, as the rule this page states |
| `worlds-runtime:453` | rule | home | Games link no tooling: shipped games read cooked packs only |
| `scripting:693` | open | home | Whether a build without scripting is possible: it is not, as `new:10` states with its evidence |
| `foundation:465` | rule | home | Registration only through the composition root, before anything reads a registry; nothing after the freeze of the component and settings registries, the two that freeze (the others stay open, and tools and tests register more into them later) |
| `foundation:468` | rule | home | `#if ST_WITH_<MODULE>` only in the composition root, the asset pipeline, the runtime and tests |
| `foundation:470` | rule | home | Never widen `MayInclude` or add an allowlist line to let a sideways or upward include pass; invert the dependency |
| `foundation:526` | hands-on | home | A GLFW include in a Scene file: the `Architecture.Layering` failure read, then fixed by inversion |
| `foundation:527` | hands-on | home | A game component registered through `ModuleRegistrationOptions::Extra`, then once after the freeze, and the error read |
| `foundation:528` | hands-on | home | `Exclude = {"Physics"}` in a test helper: unknown components and the scripts' message |
| `foundation:549` | term | home | Composition root |
| `scene-ecs:647` | term | home | Composition root, the same entry as `foundation:549` |
| `foundation:551` | term | home | Registry: a table that modules fill at startup; the component and settings registries then freeze, and the others stay open (the definition corrected, R33, D34); `core/map` sets it against EnTT's registry |
| `foundation:553` | term | home | Freeze |
| `foundation:561` | term | home | Layer table (`Layers.json`) |
| `foundation:562` | term | home | Allowlist |
| `foundation:563` | term | home | Tooling layer |
| `foundation:564` | term | home | Dependency inversion |
| `foundation:702` | open | home | The drift the survey saw in the comments of `Engine/BuiltinModules.h`, stated as `new:6`; its other half, the roadmap's count of built-in stages, is `new:15` on `core/profiling` |
| `new:6` | erratum | home | The comment at `BuiltinModules.h:26-27` names six modules (Scene, Renderer, Physics, Audio, Animation, Scripting); the table registers nine, with Input, World and GameUI; `BuiltinModules.cpp:80` refuses to exclude Input, Scene and Renderer, while `BuiltinModules.h:21-22` names only Scene and Renderer. The page states the table's facts. Evidence: `Strata/src/Strata/Engine/BuiltinModules.h:21-27`; `Strata/src/Strata/Engine/BuiltinModules.cpp:61-80` |
| `new:7` | erratum | home | `SceneRegistration.h:6-8` names one settings section, the collision layers; `SceneRegistration.cpp:22` also registers `Scene.Timing`. Where the page shows a module's registration, it names both. Evidence: `Strata/src/Strata/Scene/SceneRegistration.h:6-8`; `Strata/src/Strata/Scene/SceneRegistration.cpp:22` |
| `new:8` | erratum | home | The foundation inventory counts 21 layers (its line 173); the table has 19, three of them tooling. Evidence: `StrataTests/Architecture/Layers.json:5-125`, which holds 19 `"Name"` entries (`grep -c '"Name"' StrataTests/Architecture/Layers.json` prints 19) |
| `new:9` | not-done | home | No engine plugins loaded while the program runs: modules are chosen when the engine is compiled (`ST_WITH_*`), and only script modules load at run time. Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:61-77`, a table fixed at compile time; `git grep -lw DynamicLibrary 822a7a46 -- Strata/src` finds it only in its own files (`Core/DynamicLibrary.*`, `Platform/*/*DynamicLibrary.cpp`), in the script modules' code (`Scripting/ScriptModule.cpp`, `Scripting/ScriptModule.h`, `Scripting/ScriptEngine.cpp`, `Project/Project.cpp`) and in the Vulkan loader (`Platform/Vulkan/VulkanLoader.cpp`) |
| `new:10` | not-done | home | No build without scripting: physics, audio and animation can be left out, scripting cannot. Evidence: `Docs/Releases/0.7.0.md:404`; `Strata/src/Strata/Engine/BuiltinModules.cpp:74`, Scripting outside every `#if` |
| `new:27` | erratum | home | `plan/inventory/foundation.md:264-266`, `:465-466` and `:551-552` say that Strata's registries open, accept and then freeze: only the component and settings registries freeze; the asset loader, asset-manager extension, built-in asset, mesh geometry and scene-system registries, which the root opens beside the component registry, and the importer registry, which the asset pipeline opens, stay open. The page teaches the two kinds (process.md's row of kind `inventory`). Evidence: `Strata/src/Strata/Engine/BuiltinModules.cpp:134-139`, `:159-160`; `Strata/src/Strata/Asset/AssetImporters.cpp:161`; `Strata/src/Strata/Asset/AssetManager.cpp:105-124` (the loader registry locks on every lookup); `Strata/src/Strata/Scene/SceneSystem.cpp:166-178`; `Docs/Architecture.md:703-705`; `git grep -n "void Freeze\|::Freeze()" 822a7a46 -- Strata/src` finds only `ComponentRegistry` and `SettingsRegistry` |
| `new:28` | hands-on | home | Trace it yourself: `Engine::RegisterBuiltinModules` followed with breakpoints from `main`, the registries it opens, the modules in table order, the asset pipeline and `Extra`, and the two registries it freezes, written down and compared with the startup log's line of modules and scene systems. Evidence: `Strata/src/Strata/Engine/EntryPoint.h:29-30`; `Strata/src/Strata/Engine/BuiltinModules.cpp:118-174` |
| `foundation:174` | feature | use | `strata_add_layer_libraries`, named as what makes a library of each layer; `engineering/cmake` teaches it |
| `foundation:177` | feature | use | The link closure and the linker-map check, named as the proof of "no tooling in games"; `engineering/cmake` teaches them |
| `build-test:180` | feature | home | `Architecture.Layering`, as the build's inventory describes it: includes checked against `Layers.json`, a stale allowlist line fails, `ExternalOwners`; taught with `foundation:175` |
| `build-test:181` | feature | home | `Architecture.Libraries`: every engine source in the library of its one layer, and each library linking exactly the built layers its layer may include, read from the `LayerLibraries.json` that the configure step writes (`engineering/cmake` teaches the writing) |
| `build-test:494` | rule | home | Never widen `MayInclude` or add an allowlist line to make an include pass; invert the dependency: the same rule as `foundation:470`, with the build's reason that the table is the build |
| `build-test:652` | term | home | Four entries: layer table, `MayInclude`, `Tooling` and `Option` (the CMake option that builds a layer); the first and the third are the entries of `foundation:561` and `foundation:563` |
| `build-test:654` | term | home | Composition root, the same entry as `foundation:549` |
| `build-test:32` | feature | use | The CMake options that leave the optional modules out |
| `build-test:491` | rule | use | `ST_WITH_*` are compile definitions, never macros of a header |
| `build-test:496` | rule | use | Games link no tooling, the same rule from the build's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Engine modules: `EngineModule` against `Register<Module>Module` | `core/engine-modules` | must |
| "Module", "layer", "registry" and "service" in their two meanings | `core/map` | must |
| Static libraries and linking | `basics/build` | must |
| `#include`, `#if` and macros | `basics/cpp-modern` | must |
| Interfaces and virtual calls | `basics/cpp-classes` | must |
| Atomics, acquire and release | `basics/threads` | must |
| JSON | `basics/data-formats` | must |
| Writing and running one test case | `core/first-change` | must |
| Function pointers | `basics/cpp-generic` | helps |
| Static initialization and its order | `basics/build` | helps |
| Components, asset loaders and scene systems, as what the registries hold | `world/ecs` | helps |
| The test program's helpers, for the third exercise | `engineering/test-program` | helps |

## `core/jobs` — Threads and the job system

**Covers.** The job: how Strata runs work on other threads without making the frame wait for what it does not need, and
who owns what across threads. The problem in the part's full section on it: job systems (thread pools, task graphs, work
stealing and fibers, priorities, pools for blocking reads) and the threading model of an engine (one thread owns the
world's changing state, or every system runs in parallel; results handed back through queues and polling, never through
callbacks). The map: the three pools and who submits to which, then the threads of the editor's process and their
hand-offs into the main thread. The contract: the pools (workers, one fewer than the hardware threads, at normal
priority; two I/O threads; background threads below normal priority, which leave four hardware threads to the frame);
`Submit`, `SubmitIO`, `SubmitBackgroundPart` and `JobPriority` (High, Normal, Low, Background; work started from
background stays background); `JobHandle`, `Wait` and `WaitAll` (whoever claims a job first runs it, by an atomic
exchange; a waiter runs the job it waits for when no thread has started it, and never another job, so waiting inside a
job cannot deadlock); `ParallelFor` (an atomic counter of batches, the caller takes batches too, helpers that have not
started are dropped once every batch is taken, shared state keeps it alive); jobs that run on the caller before `Init`
and after `Shutdown`; a `try` and `catch` around every job and batch; `GetStats` and `ThreadActivity`, read without
stopping the pool; `SequenceLockedValue<T>`, one writer and one reader that never wait (the audio thread's hand-off).
The rules with their reasons: the main thread owns the scene, input, scripts and rendering submission, and workers hand
results back; never block a frame on long work, and never let a waiter run other jobs; the main thread's frame work
touches no file, because a blocking read stalls the frame, so reads go to the I/O pool and their results come back by
polling (`core/files` shows the counter that tests prove it with); long work at `JobPriority::Background` (the measured
stalls: frames of about 3 ms stretched to 10-30 ms while an import compressed textures); what a job captures is released
where it runs (libc++ copies small callables when they are moved). Then deterministic parallel work, as its home: jobs
write only their own records, the main thread publishes them in order afterwards, and the result does not depend on the
number of threads (the design decision's `:::why`, with the places that keep it: animation, physics and the scene's
parallel writer). What Strata does not do: work stealing, fibers and a task graph of the frame. The toy is a pool with
one queue and a `Wait` that runs the job itself, in 60 lines; the real code is the claim and the wait, the pool's
thread, `ParallelFor`, the emptied `std::function` and the sequence lock. The exercises: `ParallelFor` at batch sizes 1,
64 and 4096, measured with the workers' busy share; a job that waits on a job, traced with breakpoints into `Wait` and
`TryRunJob`, and why it cannot deadlock; the captured last `Ref`; a hand-off through `SequenceLockedValue`. At the end
the reader can put work on the right pool, wait for it safely, and keep its result the same on any number of threads.

**Leaves out.**

- Threads, races, mutexes, atomics and memory order in general → `basics/threads`
- Thread priorities and how each OS sets them → `core/platform`
- The deterministic step of physics in detail → `physics/world-step`
- The animation system's ordered publish → `animation/system`
- The parallel writer's identical bytes → `world/serialization`
- The audio thread and its mixer → `audio/engine`
- The RPC server's thread → `automation/rpc-server`
- The profiler's view of the pools → `core/profiling`

**Fit.** `fits`: about 5,950 words against L (5,000). The pools, the wait and `ParallelFor`, with five quotes and four
figures, take the most, then the threading model and deterministic parallel work; four exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:288` | concept | home | Job systems: pools, task graphs, work stealing, fibers, priorities, pools for blocking reads; Strata's three pools and why; the mistakes (a job that waits and deadlocks a naive pool, a waiter that picks up long jobs, a moved `std::function` that is not empty) |
| `foundation:296` | concept | home | The threading model of an engine: one owner of the world's state, or full parallelism; hand-offs through queues and polling; Strata's table of producers and consumers |
| `new:13` | concept | home | Deterministic parallel work: jobs write only their own records, the main thread publishes them in order, and runs with different numbers of threads agree bit for bit; the design decision's `:::why`. Evidence: `AGENTS.md:308-309`; `Docs/DeveloperGuide.md:2209-2212` |
| `foundation:103` | feature | home | The three pools, workers, I/O and background, their sizes and priorities |
| `foundation:104` | feature | home | `Submit`, `SubmitIO`, `SubmitBackgroundPart` and `JobPriority` |
| `foundation:105` | feature | home | `JobHandle`, `Wait` and `WaitAll`: the claim by exchange, no deadlock, never another job |
| `foundation:106` | feature | home | `ParallelFor` |
| `foundation:107` | feature | home | Jobs run on the caller before `Init` and after `Shutdown` |
| `foundation:108` | feature | home | A `try` and `catch` around every job and batch |
| `foundation:109` | feature | home | `GetStats` and `ThreadActivity`, read without stopping the pool |
| `foundation:110` | feature | home | `SequenceLockedValue<T>`, the hand-off of one writer to one reader |
| `foundation:113` | feature | home | The threading model: what the main thread owns, and the hand-offs |
| `foundation:357` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:33-81`: `ExecuteJob`, `TryRunJob` and `DropJob`, whoever claims first runs the job; with `JobSystem.cpp:502-514`, `Wait` |
| `foundation:358` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:165-313`: `JobPool`, a pool with queues by priority and a shutdown that drains them (`ThreadMain` at 274-304) |
| `foundation:359` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:357-401`: `ParallelFor`'s shared batches; with `JobSystem.cpp:522-566`, the caller's part and the dropped helpers |
| `foundation:360` | code | home | `Strata/src/Strata/Core/JobSystem.cpp:335-342`: a `std::function` emptied after the move, so that captures die where the job runs; with `JobSystem.cpp:460-474`, `Submit` |
| `foundation:361` | code | home | `Strata/src/Strata/Core/SequenceLock.h:13-66`: the sequence lock (odd while writing, fences, retry); `ThreadActivity` in `JobSystem.cpp` 88-163 is the same idea inside the pool |
| `foundation:408` | figure | home | The job system: three pools with their queues, who submits to which, the threads' priorities, the four hardware threads left to the frame |
| `foundation:410` | figure | home | A job's states: queued, claimed by a pool thread or by a waiter, completed; dropped for `ParallelFor`'s helpers |
| `foundation:412` | figure | home | `ParallelFor`: batches, the atomic next batch, the caller and its helpers taking batches, helpers dropped, the wait for the finished count |
| `foundation:414` | figure | home | The threads of the editor's process and their hand-offs into the main thread's polled queues |
| `foundation:447` | rule | home | The main thread owns the scene, input, scripts and rendering submission; workers hand results back through queues or `SubmitToMainThread` |
| `foundation:450` | rule | home | Never block a frame on a job that may run long, and never let a waiting thread run other jobs |
| `new:29` | rule | home | The main thread's frame work does no file I/O: a blocking read there stalls the frame, so reads go to the I/O pool (`SubmitIO`) and their results come back by polling or `SubmitToMainThread`; stated with `foundation:450` (about 60 words); `core/files` keeps the per-thread operation counter as the proof tests use. Evidence: `AGENTS.md:188-190`; `AGENTS.md:353` (saves never serialize on the main thread); `Docs/DeveloperGuide.md:1698` (registering and applying touch no file on the main thread); `Strata/src/Strata/Core/FileSystem.h:70-74`; `StrataTests/src/Asset/AssetRegistrationTests.cpp:123-125`; `Strata/src/Strata/Core/JobSystem.h:113` |
| `foundation:452` | rule | home | Long work goes to `JobPriority::Background`; frame work stays on workers of normal priority |
| `foundation:454` | rule | home | What a job captures is released where it runs |
| `foundation:520` | hands-on | home | A loop through `ParallelFor` at batch sizes 1, 64 and 4096, measured with the workers' busy share |
| `foundation:521` | hands-on | home | Trace it yourself, the page's trace exercise: a test whose job waits on another job, followed with breakpoints into `JobSystem::Wait` (`Strata/src/Strata/Core/JobSystem.cpp:502-514`) and `TryRunJob` (`:60-67`), where the waiter claims the job that no thread has started by an atomic exchange and runs it; the reason it cannot deadlock |
| `foundation:522` | hands-on | home | The captured last reference: a job holding the last `Ref` of an object whose destructor records its thread |
| `foundation:523` | hands-on | home | A lock-free hand-off with `SequenceLockedValue<T>` between a thread and the main loop |
| `foundation:590` | term | home | Thread pool |
| `foundation:591` | term | home | Two entries: job and job handle |
| `foundation:592` | term | home | Three entries: worker thread, I/O thread and background thread |
| `foundation:593` | term | home | ParallelFor |
| `foundation:594` | term | home | Batch, a slice of a `ParallelFor`'s range (the other meaning, batching draws, is `draw/batching`'s) |
| `foundation:595` | term | home | Claim |
| `foundation:600` | term | home | Sequence lock |
| `audio-input:633` | term | home | Sequence lock, one entry with `foundation:600` (a writer bumps a counter around a write, readers retry if it changed), passed by `audio-input` (R31, "The sequence lock"); the excerpt `SequenceLock.h` stays here, and `audio/engine` quotes only its use |
| `new:12` | not-done | home | No work stealing, no fibers and no task graph of the frame: three pools with central queues. Evidence: `Docs/Roadmap.md:1704-1705` lists "JobSystem v2 with work stealing and a frame task graph" under "Further"; `git grep -ni fiber 822a7a46 -- Strata/src` finds nothing; `git grep -ni steal 822a7a46 -- Strata/src` finds only voice stealing (`Strata/src/Strata/Audio/AudioEngine.cpp:147`, `Strata/src/Strata/Audio/AudioSystem.cpp:895`) |
| `foundation:284` | concept | link | Threads and synchronization in general, `basics/threads`' |
| `foundation:596`, `foundation:597`, `foundation:598`, `foundation:599`, `foundation:601` | term | link | Deadlock, data race, mutex and condition variable, atomics and memory order, thread-local, whose entries are `basics/threads`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Threads, races, mutexes, condition variables, atomics and memory order | `basics/threads` | must |
| `std::function`, lambdas and captures | `basics/cpp-generic` | must |
| Move semantics | `basics/cpp-modern` | must |
| `shared_ptr` and shared state | `basics/cpp-memory` | must |
| Queues and priority queues | `basics/trees-graphs` | must |
| The frame loop and `SubmitToMainThread` | `core/frame-loop` | must |
| Writing and running one test case | `core/first-change` | must |
| Processor cores and hardware threads | `basics/computer` | helps |
| Thread priorities | `core/platform` | helps |
| The frame profiler's busy shares, for the first exercise | `core/profiling` | helps |

## `core/platform` — Talking to the operating system

**Covers.** The job: how engine code reaches the operating system through one seam, and what Strata asks of Windows,
Linux and macOS. The problem in the part's full section on it: platform abstraction (detection by the preprocessor; one
interface with one implementation per OS chosen when linking, against virtual backends; window libraries such as GLFW
and SDL; where OS headers may appear). The map: `Core/Platform.h` above `Platform/Windows/` and `Platform/Posix/`, the
window backends beside them. The contract: platform detection (exactly one `ST_PLATFORM_*`, an `#error` for 32-bit
Windows, other Apple systems and every other target) and the absence of mobile, console and web targets; the `Platform`
class by group (paths and the user's folders, fallback fonts, processes and their times, memory, secure random numbers,
environment variables, opening a file with its program, `FindProgram`, error dialogs, binary standard streams; its
debugger and memory functions are read again on `core/debugging`); `Process`, the seam for child processes, as its home
(the output captured, merged or as two streams, inherited or discarded; piped input; `Wait` with a timeout and `Run` to
completion; the whole tree ended as one, through a job object on Windows and a process group on POSIX; its users: the
editor's script builds, the external editor, StrataCLI's launcher and the tests' helper processes); the rule for headers
(platform, window and graphics headers only in their Platform folders; never `<Windows.h>` in a header; no X11 headers;
no names that Windows defines as macros; no `None` in an unscoped enum); `WindowsUtils` at Win32's boundary of wide
strings. Then programs on Windows: the console and GUI subsystems, why the editor and the runtime are GUI programs,
`ConnectStandardStreams` keeping the pipes it was given or attaching to the parent's console for a Console run, the
decision as a table, and why PowerShell waits for a GUI program only when its output is piped. Then interrupts: Ctrl+C,
Ctrl+Break and closing the console on Windows, SIGINT and SIGTERM on POSIX, each turned into a request the loop honours;
a handler that only counts, because a signal handler may do only async-signal-safe work; a second request ends the
process at once; exit code 130. Then scheduling and power: priorities and scheduling quanta, processors with two kinds
of cores, Windows 11's power throttling of programs in the background and the opt-out at startup; thread names and
priorities; precise sleep (`SleepUntil` through a high-resolution waitable timer on Windows, because the default tick is
15.6 ms and `timeBeginPeriod` changes the whole system). The toy is a seam with two implementations that the build
chooses, in 40 lines; the real code is the POSIX interrupt handler, `ConnectStandardStreams` and Windows' `SleepUntil`.
The page's example: the editor run headless from a terminal and stopped with Ctrl+C. The exercises add a `Platform::`
function for every OS and its test, and trace Ctrl+C from the handler to the end of `Run`. At the end the reader can add
a function to the platform seam on every OS, and explain how a Strata program talks to its terminal and stops when
asked.

**Leaves out.**

- Files, paths and private files → `core/files`
- The editor's script builds, which run CMake and the compilers through `Process` → `editor/script-builds`
- Shared libraries and how script modules are loaded → `scripting/loading`
- Containing crashes with structured exceptions and signals → `scripting/crash-containment`
- The window backends → `core/windows-events`
- Sockets → `automation/json-rpc`
- The debugger and memory functions in use → `core/debugging`
- The pools whose priorities this page sets → `core/jobs`

**Fit.** `fits`: about 5,300 words against L (5,000). The three concepts (platform abstraction, programs on Windows,
scheduling and power) and the `Platform` class take the most; `Process` takes about 250 and the trace exercise about
250.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:308` | concept | home | Platform abstraction: detection by the preprocessor, one interface with an implementation per OS chosen when linking, against virtual backends; window libraries; where OS headers may appear; the mistakes (`<Windows.h>` in a header, X11's `None`) |
| `foundation:313` | concept | home | Programs on Windows: console and GUI subsystems, attaching to a parent's console, why PowerShell does not wait, signals and console control handlers, async-signal safety, exit codes |
| `foundation:300` | concept | home | Scheduling and power: priorities, scheduling quanta, processors with two kinds of cores, Windows 11's power throttling |
| `foundation:119` | feature | home | Platform detection |
| `foundation:120` | feature | home | The `Platform` class, by group; its debugger and memory functions are read again on `core/debugging` |
| `foundation:133` | feature | home | `WindowsUtils`: `Utf8ToWide` and `WideToUtf8` at Win32's boundary |
| `foundation:58` | feature | home | The GUI subsystem and `ConnectStandardStreams` |
| `foundation:57` | feature | home | Interrupt handling on Windows and POSIX |
| `foundation:59` | feature | home | The power-throttling opt-out |
| `foundation:112` | feature | home | `SetCurrentThreadName`, `SetCurrentThreadPriority` and `SleepUntil` |
| `foundation:364` | code | home | `Strata/src/Platform/Windows/WindowsPlatform.cpp:337-380`: precise sleep through a high-resolution waitable timer of the thread's own |
| `foundation:365` | code | home | `Strata/src/Platform/Posix/PosixPlatform.cpp:903-920`: an async-signal-safe handler that counts, and re-raises on the second request; with `PosixPlatform.cpp:981-995`, its installation (the inventory's 900-922 starts three lines early) |
| `foundation:366` | code | home | `Strata/src/Platform/Windows/WindowsPlatform.cpp:755-793`: console against GUI subsystem, the pipes kept and the parent's console attached |
| `foundation:420` | figure | home | The decision of a Windows run as a table: streams given, a Console run, a parent's console to attach, a dialog to show |
| `foundation:437` | figure | home | A terminal running `StrataEditor --headless --frames 120`: a Console run's output, and the message after Ctrl+C |
| `foundation:472` | rule | home | Platform, window and graphics headers only in their Platform folders; never `<Windows.h>` in a header; no X11 headers; no names Windows defines as macros; no `None` in an unscoped enum |
| `foundation:494` | rule | home | Sleeps on Windows are coarse; never call `timeBeginPeriod` |
| `foundation:496` | rule | home | GUI programs and PowerShell: pipe their output, or use `Start-Process -Wait`, to get the exit code |
| `foundation:498` | rule | home | A second Ctrl+C ends the process at once; the signal handler only counts |
| `audio-input:539` | rule | home | Unscoped enums never use `None`, because X11 defines it as a macro: part of `foundation:472`, with `AudioAttenuationModel::NoAttenuation` as the example of the name it forces (taken here rather than on `core/conventions`, whose page leaves the platform rules to this one) |
| `foundation:525` | hands-on | home | A new `Platform::` function: declared in `Core/Platform.h`, implemented in `WindowsPlatform.cpp` and `PosixPlatform.cpp`, tested in `PlatformTests.cpp`, checked with `Architecture.Layering` |
| `new:30` | hands-on | home | Trace it yourself: Ctrl+C in the terminal of a headless editor followed from the handler of the reader's OS (the console control handler on Windows, `OnInterruptSignal` on POSIX) to `Platform::IsInterruptRequested` in `Run`, the warning line and exit code 130, with breakpoints or a search; then what a second Ctrl+C does. Evidence: `Strata/src/Platform/Posix/PosixPlatform.cpp:903-920`, `:981-995`; `Strata/src/Strata/Core/Application.cpp:261-269` |
| `foundation:602` | term | home | Two entries: thread priority and scheduling quantum |
| `foundation:603` | term | home | Power throttling (EcoQoS) |
| `foundation:619` | term | home | Two entries: platform layer and seam |
| `foundation:622` | term | home | Two entries: console subsystem and GUI subsystem |
| `foundation:624` | term | home | Two entries: signal (SIGINT, SIGTERM) and console control handler |
| `foundation:625` | term | home | Async-signal-safe |
| `scripting:609` | term | home | Signal, the same entry as `foundation:624`'s first term |
| `new:14` | not-done | home | No mobile, console or web targets: 64-bit Windows, Linux and macOS only. Evidence: `Strata/src/Strata/Core/PlatformDetection.h:5-22`, an `#error` for every other target |
| `foundation:128` | feature | home | `Process`, the platform's seam for child processes (about 250 words, R31, D12): `ProcessOutputMode`'s captured output (merged, or stdout and stderr apart), inherited or discarded; piped input; `Wait` with a timeout and `Run` to completion, which ends the child on timeout; `TerminateTree`, which ends the child and every process it starts as one unit, through a job object on Windows and a process group on POSIX; its users named: the editor's script builds and toolchain discovery, the external editor, StrataCLI's `LaunchEditor` and the tests' helper processes (`Strata/src/Strata/Core/Process.h:18-96`); `editor/script-builds` and `automation/sessions` use it and link here |
| `foundation:129` | feature | use | `DynamicLibrary`, named as the seam for shared libraries; its home is `scripting/loading` |
| `foundation:626` | term | link | Exit code, whose entry is `basics/tools`' |
| `build-test:541` | rule | use | The same rule about PowerShell from the build's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| `#if`, `#error` and macros | `basics/cpp-modern` | must |
| Processes, environment variables, the standard streams and exit codes | `basics/tools` | must |
| PowerShell, and piping a program's output | `basics/tools` | must |
| Static member functions | `basics/programming-2` | helps |
| The pools and their threads | `core/jobs` | must |
| Atomics | `basics/threads` | must |
| The frame loop, which polls the interrupt, and the pacer, which sleeps | `core/frame-loop` | must |
| Console and Interactive runs | `core/first-frame` | must |
| UTF-8 and UTF-16 | `basics/bytes` | must |
| Writing and running one test case | `core/first-change` | must |
| The layer table and `ExternalOwners` | `core/layers-registries` | helps |
| Processor cores and hardware threads | `basics/computer` | helps |

## `core/files` — Files you can trust

**Covers.** The job: how engine code names, reads and writes files so that no crash, no other program and no other user
leaves it with half a file, a wrong file or a planted one. The problem in a short section: what goes wrong (partial
writes and crashes, readers that see half a file, a rename on Windows that fails while another program holds the file,
the time between checking a file and using it, permissions, links and junctions) and the approaches (writing in place, a
temporary file and a rename, a journal); the rename also makes a folder whole, filled under another name and renamed
into place, as the build's Slang cache is. The map: `FileSystem`, `AtomicFileWriter`, `FileReader`, `FileLock`,
`FileWatcher` and `BoundedRead` in Core, the private-file functions on `Platform`, and their halves per OS. The
contract, text and paths first: strings are UTF-8 `std::string` everywhere; a `std::filesystem::path` made from a narrow
string on Windows uses the process's code page, so paths go through `FromUTF8` and `ToUTF8`, which convert through
`char8_t` and write `/`; the application manifest makes UTF-8 the code page of Strata's programs, as a second line of
defence. Then `FileSystem` (reads without exceptions, whole, a prefix or a range; atomic writes by a temporary file and
a rename; copies that follow no link; containment with `IsInside` and `IsInsideResolved`; `GetUniquePath`; a count of
operations per thread that lets tests prove the main thread did no file I/O); `AtomicFileWriter` and `DocumentOutput` (a
streaming atomic writer with a 1 MB buffer for huge documents written on background threads, `Commit` or `Abort`);
`FileReader` (one open file read at given offsets by many threads); `FileLock` (an exclusive lock between processes,
released when the process ends); `FileWatcher` and `FileChangeNotifier` (a thread that rescans a tree after the OS's
notifications on Windows and by polling elsewhere, and `PollChanges` on the caller's thread); `BoundedRead` (read to the
end with a cap, never trusting a size read earlier); the private-file contract (directories only the user may change,
created for the owner alone and checked when they exist; `WritePrivateFile` through an exclusive temporary file and a
rename; `IsTrustedFile`, and `ReadTrustedFile`, which checks and reads through one handle; `RenameNoReplace`;
`GetUserRuntimeDirectory`). The rules: strings are UTF-8 and convert at `std::filesystem`'s boundary; every write is
atomic; files only the user may change go through the private-file functions. The toy is an atomic write in 30 lines,
with a crash at each point; the real code is the atomic write, the UTF-8 conversion and the private-directory contract
in `Platform.h`. The page's example: a document saved while the process is killed at each step leaves the old file or
the new one, never half of either. The exercises kill a writing process in a loop, and trace `WriteText` to its rename
on the reader's OS. `FileLock` comes with its term, file lock, and the build's users of such locks (Slang's fetch,
`PerfLock.py`). At the end the reader can write a file that survives a crash, read a file someone else could have
changed, and convert a path without mangling its name.

**Leaves out.**

- Text encodings and bytes in general → `basics/bytes`
- Untrusted contents: validation, checksums and bounded sizes → `assets/robustness`
- Scene documents written as a stream → `world/serialization`
- Saves that never stall the editor → `editor/saving`
- Asset hot reload from file changes → `assets/importing`
- Session files and the token's private files → `automation/security`
- Save files of games → `scripting/host-api`

**Fit.** `fits`: about 4,550 words against L (5,000). The contract of `FileSystem`, the atomic writers and the
private-file functions, with three quotes, takes the most, then the two concepts (text and paths, safe writing and
trust); two exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:317` | concept | home | Text and paths: UTF-8 against UTF-16 and Windows' wide calls, a path made from a narrow string on Windows, `char8_t`, generic separators; the mistake `path(std::string)` |
| `foundation:321` | concept | home | Safe writing and trust: partial writes, a temporary file and a rename, Windows' retried rename, TOCTOU, POSIX modes and Windows DACLs, links and junctions |
| `foundation:122` | feature | home | `FileSystem` |
| `foundation:123` | feature | home | `AtomicFileWriter` and `DocumentOutput` |
| `foundation:124` | feature | home | `FileReader` |
| `foundation:125` | feature | home | `FileWatcher` and `FileChangeNotifier`; how the asset manager acts on their changes is `assets/importing`'s |
| `foundation:126` | feature | home | `FileLock` |
| `build-test:642` | term | home | File lock: an OS lock on a file that serializes processes, the term of `FileLock`, with the build's users named (Slang's fetch at the first configure, `PerfLock.py`); passed by `engineering` (the merge "File lock"); `engineering/third-party` links it |
| `foundation:127` | feature | home | `BoundedRead` |
| `foundation:121` | feature | home | Private directories and files: one contract on every OS |
| `foundation:367` | code | home | `Strata/src/Strata/Core/FileSystem.cpp:102-135`: the atomic write (temporary file, flush, rename, clean-up); with `FileSystem.cpp:341-350`, the UTF-8 conversion through `char8_t` |
| `foundation:368` | code | home | `Strata/src/Strata/Core/Platform.h:92-129`: a security contract written as the interface's comment (private directories) |
| `foundation:422` | figure | home | The atomic write with a crash at each point (the old file or the new one), and the check and read through one handle |
| `foundation:479` | rule | home | Strings are UTF-8; convert at `std::filesystem`'s boundary with `FromUTF8` and `ToUTF8` |
| `foundation:481` | rule | home | Files only the current user may change go through the private-file functions; trusted files are checked and read through one handle |
| `foundation:483` | rule | home | Every write is atomic (a temporary file and a rename) |
| `foundation:529` | hands-on | home | A file written atomically with `FileSystem::WriteText` while the process is killed in a loop: always the old file or the new one |
| `new:31` | hands-on | home | Trace it yourself: `FileSystem::WriteText` followed with the debugger or a search to the temporary file, its flush and the `std::filesystem::rename` that replaces the old file, and `WritePrivateFile` on the reader's OS to its own rename (`MoveFileExW` on Windows); the steps written down with what a crash between each leaves. Evidence: `Strata/src/Strata/Core/FileSystem.cpp:102-146`; `Strata/src/Platform/Windows/WindowsPlatform.cpp:658` |
| `foundation:628` | term | home | Atomic write |
| `editor-core:702` | term | home | Atomic write, the same entry as `foundation:628` |
| `foundation:629` | term | home | TOCTOU |
| `foundation:630` | term | home | Two entries: DACL and file mode 0700 |
| `foundation:631` | term | home | Three entries: reparse point, junction and symbolic link |
| `automation:757` | term | home | Two entries: private directory and owner-only file (POSIX modes 0700 and 0600, a protected DACL on Windows); the session files kept in them are `automation/security`'s |
| `build-test:643` | term | home | Atomic rename: the step that makes a write atomic, for a file or for a folder filled under another name, as the build's Slang cache is (`engineering/third-party`) |
| `foundation:699` | open | home | Checked at the pin: `Strata/src/Strata/Core/Log.cpp:224` hands spdlog the log's path as a narrow string, and `CMake/Strata.manifest:2-3, 7` makes UTF-8 the code page of the editor, the runtime, the CLI and the tests, so the narrow path is UTF-8 there; the page tells the manifest's part in the UTF-8 rule and calls nothing a defect |
| `foundation:627` | term | link | UTF-8, UTF-16 and code page, whose entries are `basics/bytes`' |
| `build-test:48` | feature | use | The Windows application manifest: UTF-8 as the process's code page, long paths |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| UTF-8 and text encodings | `basics/bytes` | must |
| The platform seam and the `Platform` class | `core/platform` | must |
| Threads and the job system's pools | `core/jobs` | must |
| The rule that the main thread does no file I/O | `core/jobs` | must |
| Writing and running one test case | `core/first-change` | must |
| `std::filesystem::path` | `basics/cpp-modern` | helps |
| Folders, paths and permissions as a user meets them | `basics/tools` | helps |

## `core/profiling` — Measuring the frame: the frame profiler, Tracy and the method

**Covers.** The job: how Strata measures where a frame's time goes, all the time and at almost no cost, and how a person
reads the numbers. The problem in the part's full section on measuring, as the home of the method: instrumenting against
sampling profilers; zones and frame markers; Tracy; stage timers that are always on; self time against inclusive time;
percentiles taught from the average the reader knows (the median as P50, P95, by nearest rank; why P50 alone hides the
stutter that P95 shows); "CPU, GPU or capped", from the frame map's CPU and GPU working on different frames; GPU times
that arrive frames late. The map: stages on the main thread, the ring of 600 frames, the summaries, the pools' busy
shares, the GPU stages attached later, listeners and snapshots. The contract: the Tracy macros (`ST_PROFILE_FRAME`,
`ST_PROFILE_FUNCTION`, `ST_PROFILE_SCOPE`, `ST_PROFILE_THREAD`), compiled out unless `STRATA_ENABLE_TRACY`;
`ST_PROFILE_STAGE` and `FrameProfiler` (twelve built-in stages, each named in a list, with one sentence that points
forward to `gpu/upload-queue` for the Present stage; the stages that scene systems, the game UI and the editor add, in
the generated table of every CPU stage on `reference/performance`, which the page links; nested self time; a stage
that counts only on the frame thread, inside a frame, so a stage written inside a job records nothing; the mean, P50,
P95 and maximum, the busy shares from `JobSystem::GetStats`, GPU stages attached late, the classification CPU, GPU or
Capped by its 90% rule on the summarized frames' medians, with one frame at 60 Hz worked through, snapshots while
paused); the rule that a stage wraps a unit of frame work, never calls of nanoseconds (self-time accounting, and a limit
of 64 stages). The toy is a stage timer with a fixed-depth stack of nested scopes, in 50 lines; the real code is
`BeginStage`, the scope class and the macro with its static stage id. The readers of the numbers: the editor's
Performance panel, the status bar's frame pill and `editor.perf`, given as one complete line to paste with one sentence
on what it does (a query that answers in its own frame from the frames the profiler recorded, at most 600) and a link
forward to `editor/commands`. The page's example: a stage added to a layer, nested inside another, read in the panel.
The exercises: that stage and its self time; the editor built with Tracy, its zones compared with the stages; a search
for where each stage beyond the twelve is registered. At the end the reader can add a stage, read a frame's stages and
percentiles, and say whether a frame is CPU-bound, GPU-bound or capped.

**Leaves out.**

- Benchmarks, noise, budgets and the perf lab → `engineering/perf-lab`
- GPU timestamps and readback → `gpu/readback-timing`
- How the Performance panel draws and keeps its own cost low → `editor-ui/instrument-panels`
- Measuring a game, for game makers → `make/performance`
- Every budget and the reference machine, and the generated table of every CPU stage → `reference/performance`
- The Present stage and the display wait it counts → `gpu/upload-queue`

**Fit.** `fits`: about 4,750 words against L (5,000). The measuring method taught from zero (percentiles from the
average; CPU, GPU or capped) and the contract of `FrameProfiler` with its 90% rule take the most; five figures and three
exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:303` | concept | home | Profiling: instrumentation and sampling, zones, frame markers, stage timers that are always on, self time, percentiles by nearest rank, CPU, GPU or capped, GPU times that arrive late; the mistakes (P50 read as the frame time while P95 stutters, stages around calls of nanoseconds) |
| `foundation:95` | feature | home | The Tracy macros, compiled out unless `STRATA_ENABLE_TRACY` |
| `foundation:96` | feature | home | `ST_PROFILE_STAGE` and `FrameProfiler`: the twelve built-in stages, with one sentence that points forward to `gpu/upload-queue` for the Present stage (R31, Present); a link to the generated table of every CPU stage on `reference/performance` (pipelines.md §7.1, `tools/reference.py`; R34, D42; R48), which holds the five that scene systems, the game UI and the editor add (`Scene.UI`, `Scene.Animation`, `World.Streaming`, `Render.UI`, `Editor.Commands`); one sentence that a stage counts only on the frame thread, inside a frame, so a stage inside a job records nothing (`Strata/src/Strata/Core/FrameProfiler.h:158-165`, `:203-205`); self time, the ring of 600 frames, the summaries, the busy shares, GPU stages attached late, listeners, snapshots; the bound classification with its rule (about 100 words): on the medians of the summarized frames, GPU when the GPU's busy time is at least 90% of the frame interval and longer than the work time, CPU when the work time is at least 90% of it, Capped otherwise (vsync, a cap or idle throttling), Unknown without GPU times; why medians (one slow frame does not flip the verdict); one frame at 60 Hz worked through (an interval of 16.7 ms, a bound at 15 ms) (`Strata/src/Strata/Core/FrameProfiler.h:49-56`, `:229-232`; `Strata/src/Strata/Core/FrameProfiler.cpp:152`, `:603-612`) |
| `foundation:362` | code | home | `Strata/src/Strata/Core/FrameProfiler.cpp:409-434`: self-time accounting of nested scopes on a fixed-depth stack; with `Core/Profiling.h` 39-42 (the macro, a static stage id per call site) and `Core/FrameProfiler.h` 386-406 (the scope class) |
| `foundation:418` | figure | home | Nested stages on a time bar, the outer one paused while the inner runs; the ring of 600 frames; GPU times attached frames later |
| `foundation:431` | figure | home | The editor's Performance panel with the stacked stages, while the Physics Playground plays and while it is paused |
| `foundation:433` | figure | home | The status bar's frame pill and its tooltip (CPU, GPU or Capped) |
| `foundation:434` | figure | home | A Tracy capture of the editor built with `STRATA_ENABLE_TRACY`: stage zones on the main thread, job zones on the workers |
| `foundation:441` | figure | home | `editor.perf`'s JSON beside the panel: the same numbers through a command |
| `foundation:487` | rule | home | `ST_PROFILE_STAGE` around a unit of frame work, never around calls that take nanoseconds |
| `foundation:518` | hands-on | home | A custom `ST_PROFILE_STAGE("Game.MyWork")` in a layer, then nested, its self time read in the Performance panel or through `editor.perf` |
| `foundation:519` | hands-on | home | The editor built with `-DSTRATA_ENABLE_TRACY=ON`, captured with Tracy, its `ST_PROFILE_SCOPE` zones compared with the stages |
| `new:32` | hands-on | home | Trace it yourself: with `git grep` for `ProfileStage`, `RegisterStage` and `ST_PROFILE_STAGE`, where each stage beyond the twelve built-in ones is registered or timed (`Scene.UI`, `Scene.Animation`, `World.Streaming`, `Render.UI`, `Editor.Commands`), checked against the generated table and `editor.perf`'s stages. Evidence: `Strata/src/Strata/GameUI/GameUIRegistration.cpp:23`; `Strata/src/Strata/Animation/AnimationRegistration.cpp:39`; `Strata/src/Strata/World/WorldRegistration.cpp:63`; `Strata/src/Strata/GameUI/GameUIRenderer.cpp:72`; `StrataEditor/src/Editor/EditorCommands.cpp:110` |
| `foundation:604` | term | home | Two entries: instrumenting profiler and sampling profiler |
| `foundation:605` | term | home | Tracy |
| `foundation:606` | term | home | Frame stage |
| `foundation:607` | term | home | Two entries: self time and inclusive time |
| `foundation:608` | term | home | Two entries: percentile (P50, P95) and nearest rank |
| `build-test:679` | term | home | Three entries: median, p95 and nearest rank, as the build's inventory words them; the same entries as `foundation:608`, which the perf lab uses (`engineering/perf-lab`) |
| `foundation:609` | term | home | Three entries: CPU-bound, GPU-bound and capped |
| `new:15` | erratum | home | `Docs/Roadmap.md:106` speaks of eleven built-in stages; there are twelve, `Present` among them, outside the work time. Evidence: `Strata/src/Strata/Core/FrameProfiler.h:67-81` (`c_BuiltinFrameStages`, an array of 12) |
| `foundation:109` | feature | use | `JobSystem::GetStats`, the source of the pools' busy shares |
| `editor-core:239` | feature | use | `editor.perf`, the one line to paste: a Query with session results that answers in its own frame, not deferred, from the frames the profiler already recorded (at most 600); the home of the commands stays on `editor/deferred-commands`, which names `editor.wait` alone as the smallest deferred command (`StrataEditor/src/Editor/EditorStateCommands.cpp:912-975`) |
| `build-test:30` | feature | use | The `STRATA_ENABLE_TRACY` switch in CMake |
| `foundation:610` | term | link | GPU timestamp, whose entry is `gpu/readback-timing`'s |
| `foundation:541` | hands-on | link | Reading the Performance panel while a game plays, `make/performance`'s exercise for game makers |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The frame loop, its stages and the work time | `core/frame-loop` | must |
| The pools and `GetStats` | `core/jobs` | must |
| RAII and `static` locals | `basics/cpp-memory` | must |
| The CPU and the GPU working on different frames | `start/what-an-engine-is` | must |
| A build with a CMake option | `core/first-change` | must |
| Reading and running a command | `start/how-to-read` | helps |
| GPU timestamps | `gpu/readback-timing` | helps |
| The Performance panel | `editor-ui/instrument-panels` | helps |

## `core/debugging` — Debugging the engine: debuggers, asserts, the log and crash reports

**Covers.** The job: how to find a bug in the engine itself with a debugger, the asserts, the log and what a crash
leaves behind. The method is `basics/debugging`'s; this page applies it to Strata, and its problem section is one
paragraph on why engines are harder to debug (optimized builds, threads, the GPU, crashes in code the reader did not
write). The map: where each tool hooks in. The contract and its use: the debugger on the engine built from source, in
tabs per OS (the Visual Studio solution the `windows` preset writes; `compile_commands.json` for other code editors; gdb
on Linux and lldb on macOS with the Ninja presets; Debug for stepping, Release when a bug shows only optimized); asserts
while debugging (the default handler logs, breaks when a debugger is attached and aborts otherwise; `SetAssertHandler`
with Break, Abort and Continue; `Platform::IsDebuggerAttached`; `ST_DEBUGBREAK`); the log as a tool, its machinery as
its home: `LogBuffer`, the ring that the Console panel and `log.read` read at once; `BackgroundLogSink`, which writes
the console and the file in order on a thread of its own; warnings and errors that wait for it, so they are on disk if
the process dies next; its bounded queue, and `FlushFor` for console control handlers; where the log file is (every
start empties it, and every editor of the user writes the same `StrataEditor.log`, a game its `Game.log`: read or copy
the log before starting again), and what a Console run prints; the asserts' handler quoted (`Assert.cpp`: the log line,
the handler, the abort); what a crash leaves: in a test, doctest's "test case CRASHED", the crash reporter's line that
names the test, and `STRATA_TEST_TRACE`; in a script, a contained crash reported with file and line (named,
`scripting/crash-containment`); in engine code nothing of Strata's own, an absence of "What Strata does not do" (no
crash handler and no dump: the log up to its last flushed line and the OS's report are what is left, and running under
the debugger or turning on the OS's crash dumps is what to do); one test debugged alone (doctest's `--test-case` and
`--test-suite` filters, the test program under the debugger, temporary checkpoints on standard error for a crash);
memory as a clue (`GetProcessMemory` and the peaks). The toy is a log sink that queues messages for a thread of its own,
in 40 lines; the real code is `Log::Init`, which builds the loggers from their sinks, and `BackgroundLogSink`'s
contract. The page's example: a test made to assert on purpose, found and fixed with the debugger, in tabs per OS. The
trace exercise follows one `ST_CORE_WARN` to the log file with the debugger. At the end the reader can debug the engine
and its tests on their OS, read an assert and the log, and find which test crashed.

**Leaves out.**

- A method for finding bugs; breakpoints and stepping in general → `basics/debugging`
- Debugging a game's scripts with a debugger attached to the editor → `make/play-test-debug`
- Debugging the GPU: the validation layer and frame captures → `gpu/debugging`
- Containing the crashes of scripts → `scripting/crash-containment`
- From an address to a file and line → `scripting/symbolization`
- The test program's crash reporter and helpers in full → `engineering/test-program`
- How to log: levels, macros and throttling → `core/conventions`

**Fit.** `fits`: about 4,400 words against L (5,000). The debugger set-ups in tabs per OS and the log's machinery take
the most; the assert handler's quote, the missing crash handler and the trace exercise follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:16` | feature | home | The engine under a debugger, per OS: the Visual Studio solution the `windows` preset writes, `compile_commands.json` for other code editors, gdb and lldb with the Ninja presets; Debug and Release for debugging. Evidence: `CMakePresets.json:10-48`; `CMake/StrataConfigurations.cmake:31` (`CMAKE_EXPORT_COMPILE_COMMANDS`) |
| `foundation:91` | feature | home | `LogBuffer`: the ring of recent messages with their sequence numbers, read by the Console panel and `log.read` |
| `foundation:92` | feature | home | `BackgroundLogSink`: the console and the file written on a thread of their own; warnings flush before the call returns; the bounded queue; `FlushFor`; one sentence next to where the log is (about 60 words, with `make/play-test-debug`'s line): every program start empties its log file, every editor of the user writes the same `StrataEditor.log` and a game writes its `Game.log`, so the log of a run that crashed is read or copied before the next start (`Strata/src/Strata/Core/Log.cpp:224`, the file sink opened with truncation; `StrataEditor/src/EditorApplication.cpp:283-287`; `StrataRuntime/src/RuntimeApplication.cpp:457-458`) |
| `foundation:355` | code | home | `Strata/src/Strata/Core/Log.cpp:193-268`: loggers built from sinks (the ring, the background writer, the file), flush on warning, the three loggers; the inventory's 193-265 stops before the Script logger |
| `foundation:356` | code | home | `Strata/src/Strata/Core/BackgroundLogSink.h:21-89`: asynchronous logging as a contract: order, flushes, the bounded queue, stopping |
| `foundation:416` | figure | home | The log's path: a log call to the ring at once and to the queue, the writer thread to the console and the file, the flush barrier of warnings |
| `foundation:436` | figure | home | The editor's Console panel, backed by `LogBuffer`, with the Strata, App and Script loggers and their levels |
| `foundation:615` | term | home | Asynchronous logging |
| `foundation:93` | feature | use | The assert handler and the debugger detection in use: what a failed assert does with and without a debugger |
| `foundation:354` | code | use | `Strata/src/Strata/Core/Assert.cpp:32-66`, quoted here and not on `core/conventions`: the log line, the handler that can be replaced, the abort, read while debugging |
| `foundation:120` | feature | use | `Platform::IsDebuggerAttached`, `GetProcessMemory` and the peaks |
| `foundation:97` | feature | link | `CrashGuard` and `Symbolizer`, named as what reports a script's crash |
| `foundation:614` | term | link | Ring buffer, whose entry is `basics/data-structures`' |
| `build-test:112` | feature | use | The crash reporter that names the test that crashed, and `STRATA_TEST_TRACE` |
| `build-test:249` | feature | home | Debugging a crashing test: temporary checkpoints on standard error, flushed, between statements, the one test case run alone, a copy of the file kept and the checkpoints removed afterwards |
| `build-test:105` | feature | use | The test program, run alone under the debugger with doctest's filters |
| `new:33` | not-done | home | No crash handler and no crash dumps for the engine's own crashes: only guarded script calls are contained; a crash in engine code ends the process with no report or dump of Strata's own, and the log keeps every warning and error but loses the info and trace lines still queued. What is left (the log up to its last flushed line, the OS's report) and what to do (run under the debugger, or turn on the OS's crash dumps; the writer checks each OS's tool), about 100 words, by book.md's rule 1. Evidence: `git grep -n -e MiniDumpWriteDump -e SetUnhandledExceptionFilter -e set_terminate 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:92-109` (outside a guarded call a signal goes where it would have gone without the guard); `Strata/src/Strata/Core/BackgroundLogSink.h:29-32` |
| `new:34` | hands-on | home | Trace it yourself, the page's trace exercise: one `ST_CORE_WARN` followed with the debugger from the macro to the ring of `LogBuffer`, the queue of `BackgroundLogSink`, its writer thread and the log file, and the flush that makes the warning reach the file before the call returns. Evidence: `Strata/src/Strata/Core/Log.cpp:193-268`; `Strata/src/Strata/Core/BackgroundLogSink.h:21-32` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A method, breakpoints, stepping, the call stack, attaching a debugger | `basics/debugging` | must |
| The source build in Debug, and one test case run alone | `core/first-change` | must |
| Asserts, verifies and the log macros | `core/conventions` | must |
| The `Platform` class and signals | `core/platform` | must |
| Threads, mutexes and condition variables | `basics/threads` | must |
| The threads of a process | `core/jobs` | must |
| Ring buffers | `basics/data-structures` | helps |
| Containing the crashes of scripts | `scripting/crash-containment` | helps |

## `core/math` — Strata's math toolkit

**Covers.** The job: the small set of math types and functions that every part of the engine shares, the conventions
they follow and the rule they enforce. The mathematics is the primers'; this page is Strata's code, and its problem
section is one paragraph that links the primers. The map: `Math/Math.h`, `AABB`, `Frustum`, `Ray` and `Random` over glm.
The contract: the conventions stated once in `Math.h` (right-handed, +Y up, −Z forward as in glTF; NDC with +Y up and
depth from 0 to 1, reversed), in one paragraph, since their home is `gpu/coordinates`; transforms (`DecomposeTransform`,
which refuses matrices that are not finite or are degenerate and folds a reflection into X; `ComposeTransform`;
`ComposeWorldTransform`, one compiled multiply, so that fused multiply-adds cannot make the scene's paths disagree, with
its rule); projections (`PerspectiveReverseZ` by swapping near and far, `PerspectiveReverseZInfinite` with depth = near
/ −z, whose infinite far plane is said in one sentence and linked to `gpu/coordinates`, the term's home,
`OrthographicReverseZ`); rotations (Euler degrees to and from quaternions, the forward, right and up directions,
`LookRotation` with its fallback for up, and `IsNearlyEqual`, which knows that q and −q are one rotation); `AABB` (empty
by default, expand, contains, intersects, `Transformed` by Arvo's method); `Ray` (`FromNDC`, which works with an
infinite reversed-Z projection because it takes depths 1 and 0.5; tests against boxes by slabs, spheres, planes, and
triangles by Möller and Trumbore); `Random` (a `mt19937_64` per thread, seeded from `random_device`, with `Seed` for
repeatable runs; the scripts' `Random` is the SDK's own). The mistakes the choices prevent: row against column major,
quaternions compared by their components, a depth from 0 to 1 treated like OpenGL's from −1 to 1, and FMA making one
product two. The toy is a ray from the mouse through an infinite reversed-Z projection, in 30 lines; the real code is
the projections, `Ray::FromNDC`, the decomposition and `ComposeWorldTransform` (the code of `AABB::Transformed` is
quoted on `draw/bounds-culling`, which book.md gives the box tests). The page's example: a ray from a pixel into the
scene, as picking and the camera's ray build it. The exercises: a frustum test of a grid of boxes with `Frustum` and
`AABB::Transformed`; `PerspectiveReverseZInfinite` derived on paper and checked against `MathTests.cpp`; a trace of the
editor's placement ray from the view to `Ray::FromNDC`. At the end the reader can use the toolkit's types, build a ray
from a pixel and say why world matrices are composed in one place.

**Leaves out.**

- Vectors, matrices and transforms as mathematics → `basics/math-matrices`
- Decomposing a matrix into translation, rotation and scale, as mathematics → `basics/math-bases`
- Projection and reversed Z as mathematics → `basics/math-projection`
- Strata's clip space, depth conventions and precision, the camera → `gpu/coordinates`
- Frustum planes, the positive vertex and culling → `draw/bounds-culling`
- FMA contraction and determinism across compilers → `engineering/flags-portability`
- The scripts' `Random` and `Motion` → `make/recipes`
- The transform contract and the scene's world matrices → `world/scene-graph`

**Fit.** `fits`: about 3,550 words against M (3,000). The contract of the toolkit's types (transforms, projections,
rotations, `AABB`, `Ray` and `Random`) and its quotes take the most; three exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:325` | concept | home | Math for engines as Strata chose it: glTF's axes, reversed Z with an infinite far plane; the mistakes (row and column major, quaternions compared by components, a 0-to-1 depth taken for OpenGL's, FMA); the mathematics itself is the primers' |
| `foundation:140` | feature | home | Transforms: `DecomposeTransform`, `ComposeTransform` and `ComposeWorldTransform` |
| `foundation:141` | feature | home | Projections: `PerspectiveReverseZ`, `PerspectiveReverseZInfinite` and `OrthographicReverseZ` |
| `foundation:142` | feature | home | Rotations: Euler degrees and quaternions, forward, right and up, `LookRotation`, `IsNearlyEqual` |
| `foundation:143` | feature | home | `AABB`, the type and its operations; how `Transformed` serves culling is `draw/bounds-culling`'s |
| `foundation:145` | feature | home | `Ray`: `FromNDC` and the intersection tests |
| `foundation:146` | feature | home | `Random`: one generator per thread, seeded, with `Seed` for repeatable runs |
| `foundation:370` | code | home | `Strata/src/Strata/Math/Math.cpp:71-91`: the reversed-Z projections (near and far swapped; the infinite far plane); the item's second half, `Frustum.cpp`'s plane extraction and positive-vertex test, is quoted on `draw/bounds-culling` |
| `foundation:373` | code | home | `Strata/src/Strata/Math/Ray.cpp:7-16`: the ray from NDC with reversed Z; also `Math/Math.cpp` 9-54 (decomposition with the reflection folded into X); `Math/AABB.cpp` 7-25 (Arvo's box) is not quoted here: `draw/bounds-culling` uses it (book.md gives it the box tests; draw-q3, D43); the item's pieces about modules are used by `core/engine-modules` |
| `foundation:502` | rule | home | Compose world matrices only through `Math::ComposeWorldTransform` |
| `foundation:530` | hands-on | home | A frustum test of a grid of boxes with `Frustum` and `AABB::Transformed` under an infinite reversed-Z projection |
| `foundation:531` | hands-on | home | `PerspectiveReverseZInfinite` derived on paper and checked against `MathTests.cpp` 79-93 |
| `new:35` | hands-on | home | Trace it yourself: the editor's placement ray followed with a search or the debugger from the camera's rotation-only view to `Ray::FromNDC` and back to world space, and why the camera's position is added only once. Evidence: `StrataEditor/src/Editor/EditorPlacement.cpp:97-104`; `Strata/src/Strata/Math/Ray.cpp:7-16` |
| `foundation:635` | term | link | Infinite far plane, said in one sentence where `PerspectiveReverseZInfinite` is shown; its entry is `gpu/coordinates`' (R31, D33) |
| `foundation:139` | feature | use | The conventions comment of `Math.h`, in one paragraph; their home is `gpu/coordinates` |
| `foundation:144` | feature | use | `Frustum`, named as a type of the toolkit; its home is `draw/bounds-culling` |
| `foundation:425` | figure | use | Its second sketch, the ray from NDC through the near plane and depth 0.5, drawn here; the frustum half is `draw/bounds-culling`'s |
| `foundation:424`, `foundation:426` | figure | link | Reversed Z's depth precision and the coordinate conventions, drawn on `gpu/coordinates` |
| `foundation:632`, `foundation:633`, `foundation:634`, `foundation:636`, `foundation:637`, `foundation:638`, `foundation:639`, `foundation:640`, `foundation:641` | term | link | The terms the page uses, whose entries are the primers' and the later pages' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Vectors, matrices, TRS, spaces and matrix order | `basics/math-matrices` | must |
| Quaternions and Euler angles | `basics/math-rotations` | must |
| Projection, homogeneous coordinates, NDC and reversed Z | `basics/math-projection` | must |
| Rays, planes, boxes and intersection tests | `basics/math-geometry` | must |
| Floating-point rounding | `basics/numbers` | must |
| The code style | `core/conventions` | must |
| `glm` | `basics/math-vectors` | helps |
| Strata's clip space and the infinite far plane | `gpu/coordinates` | helps |
| FMA contraction across compilers | `engineering/flags-portability` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `foundation:70` | feature | `gpu/vulkan-nvrhi` | Where the device is made: the outline gives device creation in detail to that page (it is also `render-core:52`'s); `core/engine-modules` names it in one paragraph |
| `foundation:84` | feature | `gpu/vulkan-nvrhi` | The window's half of presentation, the same seam as `render-core:38` and `render-core:39`; `core/windows-events` names it |
| `foundation:97` | feature | `scripting/crash-containment` | `CrashGuard` belongs to the scripting area, as the inventory says; `Symbolizer` is `scripting/symbolization`'s in the same unit |
| `foundation:111` | feature | `reference/core` | `ParallelClone`, a small helper the render scene uses, which a reader looks up |
| `foundation:129` | feature | `scripting/loading` | `DynamicLibrary` loads script modules; it repeats `scripting:187` |
| `foundation:130` | feature | `scripting/host-api` | `SaveFiles` implements `IGameSaves`, which the host API's save functions reach |
| `foundation:131` | feature | `world/projects-settings` | Settings sections and `IProjectSettings` (book.md's one-home table) |
| `foundation:132` | feature | `automation/json-rpc` | Sockets belong to the tooling layer Network (book.md: "Sockets, framing and JSON-RPC") |
| `foundation:139` | feature | `gpu/coordinates` | Strata's conventions are that page's (the outline's row of `core/math`); `core/math` gives them one paragraph |
| `foundation:144` | feature | `draw/bounds-culling` | `Frustum`'s plane extraction and its positive-vertex test are that page's (book.md); `core/math` names the type |
| `foundation:152` | feature | `basics/cpp-memory` | `Scope` and `Ref` are taught there (the outline's row and the seed of the C++ features); `core/conventions` states the rules for them |
| `foundation:154` | feature | `world/ecs` | UUIDs as stable identities (book.md); Strata's UUID is 64 bits, random and never zero (`Strata/src/Strata/Core/UUID.h:13-14`) |
| `foundation:155` | feature | `basics/data-formats` | `Hash`: FNV-1a, `Combine` and CRC-32C, which that page teaches from `Hash.h`'s own lines (R36's judgment: a teaching page explains the header further); `reference/core` keeps a `link` row and the generated table of the header |
| `foundation:156` | feature | `automation/security` | SHA-256, HMAC and the constant-time compare serve the automation's challenge and response |
| `foundation:157` | feature | `reference/core` | Base64, a utility looked up |
| `foundation:158` | feature | `assets/robustness` | Bounds-checked binary reading with a sticky failure: the pattern for untrusted cooked data |
| `foundation:160` | feature | `reference/core` | `StringUtils`, a utility looked up; `core/first-change` changes it |
| `foundation:161` | feature | `draw/batching` | The radix sort sorts the renderer's keys |
| `foundation:162` | feature | `gpu/geometry-pool` | The range allocator places meshes in the geometry pool |
| `foundation:163` | feature | `world/scene-graph` | `AmortizedCheck` paces the Debug validation of the scene's caches (the render scene's too) |
| `foundation:164` | feature | `reference/core` | `Prefetch`, a one-line hint that the script system uses |
| `foundation:165` | feature | `engineering/generated-code` | Embedded files are made by `strata_embed_file` |
| `foundation:166` | feature | `engineering/generated-code` | The version header is generated by CMake |
| `foundation:167` | feature | `engineering/flags-portability` | Precompiled headers and compile time are that page's; `core/conventions` states the include rule |
| `foundation:174` | feature | `engineering/cmake` | The CMake that enforces the layers (book.md) |
| `foundation:177` | feature | `engineering/cmake` | The link closure and the linker map (book.md); `core/layers-registries` states the rule |
| `foundation:186` | feature | `editor/stepping` | Pausing and stepping a game (book.md); `core/time` uses the step count as the game's clock |
| `foundation:188` | feature | `world/interpolation` | Interpolation's home (book.md); `core/time` gives it one paragraph |
| `foundation:284` | concept | `basics/threads` | Threads and synchronization in general (book.md; the outline's row names foundation concept 16) |
| `foundation:332` | concept | `basics/data-formats` | The outline's row of `basics/bytes` named foundation concept 26, and the split gave its half to `basics/data-formats` (R43's list of teacher cells); its radix sort and range allocator are used by `draw/batching` and `gpu/geometry-pool` |
| `foundation:369` | code | `nowhere` | It repeats `scene-ecs:388`: the same accumulator in `Scene::OnUpdateRuntime`, whose code is `world/systems`' (book.md) |
| `foundation:424` | figure | `gpu/coordinates` | Depth precision and reversed Z are that page's (book.md) |
| `foundation:425` | figure | `draw/bounds-culling` | Frustum planes and the positive vertex are that page's; `core/math` draws the second sketch, the ray from NDC |
| `foundation:426` | figure | `gpu/coordinates` | Strata's conventions are that page's |
| `foundation:537` | hands-on | `worlds/runtime` | It needs an exported game and the runtime's options, which track E meets there and not at `core/time` |
| `foundation:540` | hands-on | `make/menus` | A pause menu at time scale 0 is that page's (book.md) |
| `foundation:541` | hands-on | `make/performance` | Reading the Performance panel while a game plays, for game makers |
| `foundation:542` | hands-on | `make/play-test-debug` | The game's log file, for game makers who debug their scripts |
| `foundation:569` | term | `start/what-an-engine-is` | The frame for people is that page's (book.md) |
| `foundation:576` | term | `world/interpolation` | Interpolation's home |
| `foundation:580` | term | `nowhere` | It repeats `render-core:692` (Swapchain) |
| `foundation:581` | term | `gpu/how-a-gpu-frame-works` | Present: one entry with `render-core:696` on the page of the swap chain and present modes (R31, Present; the merge "Present"); `core/frame-loop` links it |
| `foundation:587` | term | `input/how-input-works` | Events and polling for input are that page's (book.md) |
| `foundation:596`, `foundation:597`, `foundation:598`, `foundation:599`, `foundation:601` | term | `basics/threads` | Deadlock, data race, mutex and condition variable, atomics, memory order and fences, thread-local: threads in general (book.md) |
| `foundation:610` | term | `gpu/readback-timing` | GPU timestamps are that page's (book.md) |
| `foundation:614` | term | `basics/data-structures` | A ring buffer is a data structure; Strata's rings (`LogBuffer`, the profiler's 600 frames) use the general entry |
| `foundation:616`, `foundation:617` | term | `basics/cpp-memory` | RAII, and `Scope`, `Ref` and `WeakRef` (the outline's row and the seed of the C++ features) |
| `foundation:618` | term | `engineering/flags-portability` | Precompiled headers; the term also repeats `build-test:629` |
| `foundation:626` | term | `basics/tools` | Exit codes in general (book.md) |
| `foundation:627` | term | `basics/bytes` | Text encodings (book.md) |
| `foundation:632` | term | `gpu/coordinates` | Strata's world axes are that page's conventions |
| `foundation:633`, `foundation:634` | term | `basics/math-projection` | NDC and reversed Z as mathematics (book.md) |
| `foundation:635` | term | `gpu/coordinates` | Infinite far plane: one entry with `render-core:731`, where Strata's depth conventions are taught (R31, D33; the merge "Infinite far plane"); `core/math` says it in one sentence with a link |
| `foundation:636` | term | `draw/bounds-culling` | Frustums and frustum culling as Strata tests them |
| `foundation:637` | term | `basics/math-geometry` | Boxes as mathematics |
| `foundation:638`, `foundation:639` | term | `basics/math-rotations` | Quaternions and Euler angles |
| `foundation:640` | term | `basics/math-matrices` | Translation, rotation and scale |
| `foundation:641` | term | `engineering/flags-portability` | FMA contraction's home (book.md) |
| `foundation:642` | term | `world/ecs` | UUIDs as stable identities; Strata's are 64 bits |
| `foundation:643` | term | `basics/data-formats` | Hashes (book.md), on the half of the split that takes CRC-32C and HMAC (R29); HMAC is used by `automation/security` |
| `foundation:644` | term | `draw/batching` | Goes with `foundation:161` |
| `foundation:645` | term | `gpu/geometry-pool` | Goes with `foundation:162` |
| `foundation:688` | open | `nowhere` | A note about files the survey only skimmed |
| `foundation:695` | open | `nowhere` | A note that the tests were read by their names |
| `foundation:696` | open | `nowhere` | A note that the documents date few of the area's features; `appendix/history` reads the release notes itself |
| `foundation:707` | open | `nowhere` | A naming slip in engine code (`UUID.cpp`'s thread-local `s_Engine`, checked at the pin); no page quotes it as an example of the style |
| `foundation:708` | open | `nowhere` | A question of placement that book.md answers: idle throttling is `editor-ui/status`'s, the runtime's frame-rate cap `worlds/runtime`'s |

## Not taken

none

## Questions for the planner

none
