# Brief: `core/first-frame`

| Field | Value |
| --- | --- |
| Title | From main to the first frame |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/conventions` |
| From | foundation "From `main` to the first frame" (§1.1: entry point, launch, `ProgramRun`; §1.2: the specification, startup, `ReportFatalError`, exit codes, `CommandLine`) |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `application` | Application | - |
| `headless` | Headless | - |
