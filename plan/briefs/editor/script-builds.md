# Brief: `editor/script-builds`

| Field | Value |
| --- | --- |
| Title | Building scripts from the editor: toolchains, CMake, diagnostics |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/play-mode`, `scripting/hot-reload`, `basics/build` |
| From | new; no inventory surveyed the editor's script builds: scripting §1.3 and §1.7, and `ScriptBuild*`, `ScriptToolchain*`, `ScriptProject*`, `ScriptSources*`, `ExternalEditor*` read at the pin (finding compilers, running CMake, diagnostics for the Problems panel, building before Play) |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/script-builds` — Building scripts from the editor: toolchains, CMake, diagnostics

**Covers.** The problem: a game maker presses Play after changing a script, and the editor must build the game's module
with a C++ toolchain it may have to find on this machine, without blocking a frame, and show every compiler error at its
file and line. The naive answers are named with their failure: build on the main thread (the editor freezes), always
reconfigure (slow), never reconfigure (a new file is missing from the module), show the raw log (the cause is lost). The
page follows one build. It runs on the engine's `Process` (child processes, their output, timeouts and the process tree
ended as one, taught on `core/platform` and linked): `ScriptBuilder` runs CMake in such child processes, polled once per
frame, one build at a time, in the phases FindingToolchain, Configuring and Building, streams the output to the log in
bounded lines, and ends the whole process tree when cancelled. The toolchain: by default the one the engine was
configured with (baked into `ScriptBuildConfig.h`), so modules match the engine; an installed editor (the
`StrataInstall.json` marker) builds against the installation's SDK and finds a toolchain on this machine on an I/O job
(on Windows Visual Studio 2022 17.10 or later or 2026 through vswhere, and a CMake 3.25 or later that knows its
generator by `cmake -E capabilities`; on Linux and macOS the system compiler, Ninja or Make and CMake), and without one
the build fails with what to install. Configuring only when needed: the tree's stamp records the toolchain and the
sorted list of source files; another toolchain removes the tree; an added, removed or renamed file configures it again
where it is, because a Visual Studio build compiles the projects as they were configured. Build trees too deep for
MSBuild's file tracker (259 characters) move to a private per-user build directory. `Scripts/CMakePresets.json` gives
IDEs the same toolchain. Diagnostics: errors and warnings of MSVC, GCC, Clang, MSBuild, the linkers and CMake parsed
into file, line, column, code and message, summaries told apart from causes, a failure always naming its cause, and the
Console finding a source line in a message. Building before Play: `GetPlayBuildReason` compares the sources with what
the last build compiled, file by file; `play.start` waits for the build, fails with its first errors and asks for the
Problems panel. After a build the module loads or hot-reloads (the file watcher paused during the editor's own build), a
crashed module loads again even when unchanged, and one toast changes from "Building scripts" to its outcome. The second
half: the script directory as the editor lists it (dot-folders and build trees left out, as the module's glob does;
bounded; classes read from `ST_SCRIPT_CLASS` lines; listed on an I/O thread with a version); the project's script files
(`CMakeLists.txt` through the `StrataScriptCore` package, the `Spinner` example, `script.init`, `script.create` with
validated class and field names); and the external editor, a command template started without a shell, the user's
setting or `STRATA_EXTERNAL_EDITOR`, never the project's, with `script.open` opening only code, CMake and text files of
the project or the engine. The rule: projects never choose what runs. The example: in a `basic3d` project,
`script.create` a class, break it on purpose, press Play, read the build's diagnostics in `script.status`, fix it and
Play again. The trace exercise follows Play after a changed source from `GetPlayBuildReason` through the build's phases.
Afterwards the reader can change the editor's build pipeline and predict when a build configures, where it builds and
what it reports.

**Leaves out.**

- `Process`: child processes, their output and the process tree → `core/platform`
- What a script's crash during play does → `editor/play-mode`
- Shared libraries and the module's binary interface → `scripting/shared-libraries`
- `strata_add_script_module` and building outside the editor → `make/script-builds`
- Loading a module and hot reload → `scripting/hot-reload`
- The Problems panel, the Console and the build pills as they are drawn → `editor-ui/instrument-panels`
- The Preferences window's External Editor page → `editor-ui/settings-windows`
- Building in the editor as a game maker → `make/first-script`

**Fit.** `over`: about 6,700 words against L (5,000). Counted again from the sections after `Process` left for
`core/platform` and the crash during play for `editor/play-mode`, with the trace exercise: eleven features, seven
excerpts and the internals shape stand over L's top. The next size is XL (8,000) (S2); the split that editor-q3 named
stays the other way: `editor/script-builds` "Building scripts from the editor: toolchains, CMake, diagnostics" (L) and a
new page after it, `editor/script-sources` "Script sources, new scripts and the external editor" (M, with its own fixed
parts and exercise) (S3).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:14` | feature | home | `ScriptBuilder`: CMake in child processes polled once per frame, one build at a time, its phases, output streamed in bounded lines, the process tree ended on cancel. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:192-283`; `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153`, `:1248-1262` |
| `new:15` | feature | home | The toolchain: the engine's own, baked at configure time; an installation's SDK and a toolchain found on this machine on an I/O job; what to install when none is found. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:23-53`; `StrataEditor/src/Editor/ScriptBuildConfig.h.in:1-13`; `StrataEditor/src/Editor/ScriptToolchain.h:18-133`; `StrataEditor/src/Editor/ScriptToolchain.cpp:564-603`, `:708-721` |
| `new:16` | feature | home | Configuring only when needed: the tree's stamp of toolchain and source files; removed for another toolchain, configured again where it is for added or removed files. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:206-219`; `StrataEditor/src/Editor/ScriptBuild.cpp:1021-1087` |
| `new:17` | feature | home | Build trees too deep for MSBuild's file tracker build in a private per-user directory; refused only when both are too deep. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:61-92`; `StrataEditor/src/Editor/ScriptBuild.cpp:468-528`, `:993-1000` |
| `new:18` | feature | home | `Scripts/CMakePresets.json` for IDEs, with the engine's toolchain, rewritten only when Strata wrote it. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:94-104`; `StrataEditor/src/Editor/ScriptBuild.cpp:530-623` |
| `new:19` | feature | home | Diagnostics of compilers, linkers and CMake; summaries; a failure that names its cause; source references in log messages; errors counted as the Problems panel counts them. Evidence: `StrataEditor/src/Editor/ScriptBuild.h:106-135`, `:179-180`; `StrataEditor/src/Editor/ScriptBuild.cpp:629-793`, `:1264-1268` |
| `new:20` | feature | home | Building before Play: why Play builds first, the build `play.start` waits for, its failure and cancellation, `build: false`. Evidence: `StrataEditor/src/Editor/EditorContext.h:576-591`; `StrataEditor/src/Editor/EditorContext.cpp:2288-2353`; `StrataEditor/src/Editor/Commands/PlayCommands.cpp:26-125` |
| `new:21` | feature | home | After a build: load or hot reload, the watcher paused during the build, a crashed module loaded again, one toast that changes; `script.build {wait}` and `script.status`. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2517-2544`, `:2562-2642`; `StrataEditor/src/Editor/EditorScriptCommands.cpp:247-256`, `:314-353` |
| `new:22` | feature | home | The script directory as the editor lists it: dot-folders and build trees left out, bounded listings, classes from `ST_SCRIPT_CLASS` lines, changes found file by file, a list kept on an I/O thread. Evidence: `StrataEditor/src/Editor/ScriptSources.h:16-124`; `StrataEditor/src/Editor/ScriptSources.cpp:198-324`, `:337-404` |
| `new:23` | feature | home | The project's script files: the `CMakeLists.txt`, the `Spinner` example, `script.init`, `script.create` with validated names. Evidence: `StrataEditor/src/Editor/ScriptProject.h:16-57`; `StrataEditor/src/Editor/ScriptProject.cpp:207-259`, `:307-370`; `StrataEditor/src/Editor/EditorScriptCommands.cpp:394-416` |
| `new:24` | feature | home | The external editor: a command template split into a program and its arguments and started without a shell; batch files refused but VS Code's launcher; the user's preference or `STRATA_EXTERNAL_EDITOR`; the default application otherwise; `script.open` limited to code, CMake and text files of the project or the engine. Evidence: `StrataEditor/src/Editor/ExternalEditor.h:20-117`; `StrataEditor/src/Editor/ExternalEditor.cpp:124-149`, `:215-257`, `:354-395`; `StrataEditor/src/Editor/EditorContext.cpp:2363-2404` |
| `new:25` | rule | home | Projects never choose what runs: a shared project must not start a program of its choosing when a file opens. Evidence: `AGENTS.md:362-363` |
| `new:26` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:1021-1087`: configure or build, the stamp, a tree reused, configured again or removed |
| `new:27` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:1177-1246`: `Update`, the child process polled, its output drained, configure then build |
| `new:28` | code | home | `StrataEditor/src/Editor/ScriptToolchain.cpp:234-341`: finding Visual Studio and a CMake that knows its generator, or saying what to install |
| `new:29` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:2300-2345`: `GetPlayBuildReason`, sources compared with what the last build compiled |
| `new:30` | code | home | `StrataEditor/src/Editor/Commands/PlayCommands.cpp:99-125`: `play.start` waiting for its build; with `:45-96`, how it ends |
| `new:31` | code | home | `StrataEditor/src/Editor/ExternalEditor.cpp:215-257`: `ExpandCommand`, a template made into a program and arguments, never a shell |
| `new:32` | code | home | `StrataEditor/src/Editor/ScriptBuild.cpp:629-708`: `ParseScriptBuildDiagnostics` |
| `new:33` | feature | home | How it is tested: `Editor.ScriptBuild`, `Editor.ScriptToolchain` (machines described by a `ScriptToolchainEnvironment`), `Editor.ScriptSources`, `Editor.ScriptWorkflow` and `Package.ScriptBuild`. Evidence: `StrataTests/src/Editor/ScriptBuildTests.cpp:98-787`; `StrataTests/src/Editor/ScriptToolchainTests.cpp:241-775`; `StrataTests/src/Editor/ScriptSourcesTests.cpp:57-282`; `StrataTests/src/Editor/ScriptWorkflowTests.cpp:173-739`; `StrataTests/src/Editor/ScriptBuildPackageTests.cpp:176-438` |
| `new:59` | hands-on | home | Trace it yourself (D27): change a script's source, press Play with a breakpoint in `GetPlayBuildReason` and name the file it found changed; then step through `ScriptBuilder::Update` and name the phase it is in when CMake configures and when it builds. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2300-2345`; `StrataEditor/src/Editor/ScriptBuild.cpp:1177-1246` |
| `foundation:128` | feature | use | `Process`, homed on `core/platform`: the page uses its child processes, captured output and `TerminateTree` for CMake and the toolchain's search, and links `core/platform` |
| `scripting:144-145` | feature | use | `strata_add_script_module` and the `StrataScriptCore` package the script directory's `CMakeLists.txt` uses |
| `scripting:147` | feature | home | The editor's build pipeline as the scripting survey lists it |
| `scripting:197` | feature | home | The editor's script engine: one per project, hot reload on, Play builds first; what a crash during play does is `editor/play-mode`'s, linked |
| `scripting:205` | feature | home | The `script.*` commands |
| `scripting:426` | figure | home | The editor's loop of edit, build, load, Play and Problems |
| `scripting:434` | figure | home | The status bar's build pills |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Configuring and building with CMake, generators | `basics/build` | must |
| Shared libraries and script modules | `scripting/shared-libraries` | must |
| Hot reload of scripts | `scripting/hot-reload` | must |
| `play.start` and the running copy | `editor/play-mode` | must |
| Deferred commands | `editor/deferred-commands` | must |
| `Process`: child processes, their output, timeouts and the process tree; exit codes; finding a program on PATH (`FindProgram`) | `core/platform` | must |
| The terminal, PATH and environment variables | `basics/tools` | must |
| Private directories and files you can trust | `core/files` | must |
| I/O jobs | `core/jobs` | must |
| The user's settings sections (preferences) | `world/projects-settings` | helps |
| A crash location as file and line | `scripting/symbolization` | helps |
| The Problems panel and the build pills | `editor-ui/instrument-panels` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
