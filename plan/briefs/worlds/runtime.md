# Brief: `worlds/runtime`

| Field | Value |
| --- | --- |
| Title | The runtime |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `worlds/game-identity`, `core/engine-modules`, `core/windows-events`, `scripting/script-system`, `image/quality-settings` |
| From | worlds-runtime ch. 9 (`StrataRuntime` startup, options and exit codes, `GameRuntime`, `GameRenderer` fallbacks, the window and graphics services, headless runs, no tooling); home of scene switches in a shipped game (`GameRuntime` carries out `Game::LoadScene` with the `SceneLoader` of `world/sub-scenes`, which is the home of loading scenes; the editor's switches are `editor/play-mode`'s) |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `worlds/runtime` — The runtime

**Covers.** How a shipped game runs without the editor: the same engine under another composition root, with no tooling,
no importers, no hot reload, and a headless mode for servers and CI. The map shows `StrataRuntime`'s `RuntimeLayer` over
`GameRuntime`, `GameRenderer`, `GameWindowService` and `FramePerfLog`, and which of them a headless run leaves out. The
start comes in the order it happens: `CreateApplication` checks the command line before a log, a module or a window
exists (a mistake ends the run with exit code 3 and the usage), finds the manifest next to the executable or takes
`--game`, decides the presentation, and chooses the modules (no Graphics module headless, audio on a null device);
`GetProgramRun` makes runs that end by themselves Console runs, and the Windows build is a GUI program entered at
`mainCRTStartup` with its icon and version resource. A table sets out the three kinds of run and what each gets: a
windowed game runs with time dilation, interpolation and render proxies prepared; runs that end by themselves
(`--frames`, `--seconds`) keep every fixed step, without interpolation or dilation; headless runs are capped at 60
frames a second, have no GPU and refuse `--quality` and `--screenshot`; every game has two background threads. Two
sentences give the failures: a screenshot that shows the missing-camera message or a frame still loading fails the run,
and a failed scene switch is logged while the running scene goes on. `GameRuntime::Create` then brings the game up in an
order where every failure is an error: the manifest, its settings validated, the pack and its patch packs, the script
module in its own `ScriptEngine` (loaded in place, since nothing reloads it, made active before the start scene plays,
and the host's engine restored when the game ends), the save directory, the players' bindings, the graphics options, and
the loading and start scenes' loads.

The middle is scene switching without blocking: the loading scene plays while the start scene loads with
`PrepareSystems`, a switch keeps the running scene playing until the next one is ready, a second request for the scene
that is loading keeps its load, the old scene is released in the background and unused assets are trimmed frames later,
one `SceneWorkBudget` serves the frame's loading work, and the frame is capped at 60 per second while nothing plays. The
per-frame loop follows: update, the start error, the headless crash policy (a crash, logged once and again with its
location once symbolized, disables the scripts for the session: exit code 2 headless, while a windowed game runs on
without its scripts), a quit with the game's own code, the window's requests, and the render; `GameRenderer` draws the
primary camera, a UI-only scene over black, or a "No camera to show" message, and resets exposure and TAA history when
the scene changes, so a window is never black or stale. Window and graphics options apply between frames and only when
they change something; the engine stores only the graphics options (`GraphicsOptions.json`), so window options last for
the session unless the game writes them to a save file, as `make/levels-saves` shows. The last section measures a
shipped game: game time counted in fixed steps from the start, runs that keep every fixed step (`--frames`, `--seconds`)
so that their last frame is the same on every machine, and the perf log, whose row is captured when a frame ends and
written when its GPU times arrive. The not-done paragraph says that an exported game runs no command scripts or
simulated input. An exercise runs a game headless with `--frames 300` and with `--seconds 5` and explains why the first
run's game time and the second run's frame count depend on the machine. At the end the reader can run an exported game
headless with `--frames` and a perf log, read its exit code and its CSV, and add a runtime option.

**Leaves out.**

- `SceneLoader`, prepared loads and slices in general → `world/sub-scenes`
- Players' graphics options and `GameGraphicsService` → `image/quality-settings`
- Keeping a game's display settings in a save file, as a game maker writes it → `make/levels-saves`
- The layer table and "no tooling in games" → `core/layers-registries`
- The editor's play mode and its scene switches → `editor/play-mode`
- Measuring a game as a game maker → `make/performance`
- The renderer's passes → `gpu/frame-tour`
- Script crashes and how they are contained → `scripting/crash-containment`
- Every runtime option and perf-log column in one table → `reference/worlds-runtime`
- The runtime's install rule and the release packages → `engineering/releasing`

**Fit.** `fits`: about 8,200 words against XL (8,000). Nine excerpts and four concepts (a runtime that is not the
editor, scene switches, players' options, measuring a shipped game) take the most words, in anchored sections: the
start, scene switches, the frame and measuring.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:284` | concept | home | A runtime that is not the editor: one engine, another composition root, no tooling, no importers, no hot reload, headless runs; the mistake of calling editor-only code from game code |
| `worlds-runtime:378` | figure | home | The runtime's composition, windowed and headless |
| `worlds-runtime:137-139` | feature | home | The `StrataRuntime` executable, its options and exit codes (1, 2, 3, or the game's); the manifest found next to it (`Strata/src/Strata/Project/GameManifest.h:76-78`); its Windows build (`StrataRuntime/CMakeLists.txt:1-42`, `StrataRuntime.rc.in`); the three kinds of run as a table (critic-worlds-runtime-11): headless runs capped at 60 frames a second, without a GPU, refusing `--quality` and `--screenshot`; two background threads in every game; a screenshot that shows the missing-camera message or a frame still loading fails the run, and a failed scene switch is logged while the running scene goes on (`StrataRuntime/src/RuntimeApplication.cpp:39`, `:42`, `:273-312`, `:378-410`, `:473-488`; `Strata/src/Strata/Runtime/GameRuntime.cpp:281`) |
| `worlds-runtime:334` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:378-410`: `CheckOptions`, the command line validated before anything starts; with lines 424-533, `CreateApplication` choosing the modules |
| `worlds-runtime:124-125` | feature | home | `GameRuntime`, the windowless core, and `GameRuntimeOptions` (`Strata/src/Strata/Runtime/GameRuntime.h:30-60`); how `StrataRuntime` sets them for each kind of run, in the page's table (critic-worlds-runtime-11): a windowed game with time dilation, interpolation and render proxies prepared; runs that end by themselves keeping every fixed step, without interpolation or dilation; headless runs without render proxies or interpolation (`StrataRuntime/src/RuntimeApplication.cpp:75-91`) |
| `worlds-runtime:329` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:45-156`: `Create`: manifest, settings, pack, patches, scripts, saves, bindings, graphics, loads; every failure returns an error |
| `worlds-runtime:288` | concept | home | Startup and scene switching: loading screens, progress, preparation before the swap, background release, trimming later; the mistake of a black window while loading |
| `worlds-runtime:126-127` | feature | home | Non-blocking scene loads with `SceneLoader::LoadAsync`, the same scene asked again, `ScheduleTrim`, `ReleaseInBackground`; the loading scene and its restart (`GameRuntime.cpp:178-224`) |
| `worlds-runtime:93` | feature | home | `Scene::RequestSceneLoad`, `RequestQuit` and `Game::GetSceneLoadProgress` honored by the runtime (`GameRuntime.cpp:339-362`) |
| `worlds-runtime:129` | feature | home | 60 frames per second while nothing plays (`c_LoadingFrameRate`, `GameRuntime.h:143-147`) |
| `worlds-runtime:330` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:226-282`: `UpdateSceneLoads`; with lines 296-314, `Update` and one budget per frame |
| `worlds-runtime:333` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:138-198`: the per-frame loop: update, start error, headless crash policy, quit, window requests, render, the run's last frame |
| `worlds-runtime:131` | feature | home | `GameRenderer`: the primary camera, UI over black, the message scene, history reset on a new scene, `RenderEmpty` (`Strata/src/Strata/Runtime/GameRenderer.h:23-90`) |
| `worlds-runtime:332` | code | home | `Strata/src/Strata/Runtime/GameRenderer.cpp:95-152`: never a black or stale window |
| `worlds-runtime:404` | figure | home | The "No camera to show" frame of a scene without a primary camera |
| `worlds-runtime:403` | figure | home | The exported Open World game: its loading scene with the progress bar, then the island; the island's shot may show the Wildlife layer's foxes (the cells of `Samples/OpenWorld/Assets/Worlds/Island/Wildlife/` hold instances of the `Fox` prefab), and when it does its caption names the fox's authors and the license (R32, D18) |
| `worlds-runtime:298` | concept | home | Players' options: window mode, resolution and vsync here, applied between frames; the engine stores only the graphics options (`GraphicsOptions.json`, linked to `image/quality-settings`), so window options last for the session unless the game writes them to a save file (a link to `make/levels-saves`; critic-worlds-runtime-1); the mistake of changing the window mid-frame |
| `worlds-runtime:91` | feature | home | `Game::SetWindowMode`, `SetResolution`, `SetVSync` through `IGameWindow` (`StrataScriptCore/Include/StrataScript/Game.h:75-91`) |
| `worlds-runtime:134` | feature | home | `GameWindowService`: requests stored and applied once per frame after the update; headless runs report what was asked |
| `worlds-runtime:337` | code | home | `Strata/src/Strata/Runtime/GameWindowService.cpp:95-161`: `ApplyRequests`, at a frame boundary and only when something changes |
| `worlds-runtime:449` | rule | home | Window changes apply between frames, and only when they change something |
| `new:25` | erratum | home | Concept 19 of the worlds-runtime inventory (lines 298-300) says that the window mode, resolution and vsync the player chooses are kept in the save directory; the engine keeps only the graphics options, in `GraphicsOptions.json`, and the page states that (process.md's table, kind `inventory`; critic-worlds-runtime-1). Evidence: `Strata/src/Strata/Runtime/GameGraphicsService.h:22-28`; `Strata/src/Strata/Runtime/GameWindowService.h:15-18` (requests applied between frames, no file written); `Samples/ThirdPerson/Scripts/ThirdPerson.cpp:81`, `:97-98` (a game that keeps its display settings saves them itself) |
| `worlds-runtime:295` | concept | home | Measuring a shipped game: per-frame CSV logs, deterministic runs and screenshots; the mistake of comparing runs whose game time depended on the frame rate |
| `worlds-runtime:128` | feature | home | `GetPlayedSeconds` counts fixed steps after the start; `KeepEveryFixedStep` for runs that end by themselves |
| `worlds-runtime:331` | code | home | `Strata/src/Strata/Runtime/GameRuntime.cpp:28-41`: `LimitToFixedSteps`, so that no fixed step is dropped |
| `worlds-runtime:457` | rule | home | Deterministic runs keep every fixed step; normal play follows the wall clock with time dilation |
| `worlds-runtime:136` | feature | home | `FramePerfLog`: the built-in columns and the column groups, captured at frame end and written once GPU times arrive (`Strata/src/Strata/Runtime/FramePerfLog.h:18-155`) |
| `worlds-runtime:130`, `worlds-runtime:132` | feature | home | The runtime's world, physics capacity and step columns (`GameRuntime.cpp:364-432`) and the renderer's columns (`GameRenderer.cpp:178-203`) |
| `new:11` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:200-249`: `StartPerfLog`, one listener that captures a frame when it ends and one that writes its row with the GPU's times; an incomplete log fails the run |
| `worlds-runtime:382` | figure | home | Frame N captured at its end, its row written when its GPU times arrive frames later |
| `worlds-runtime:408` | figure | home | A perf log of an Open World drive with the World and Physics columns plotted (dataviz rules) |
| `new:12` | not-done | home | Automating an exported game: command scripts, simulated input and expectations run in the editor only. Evidence: `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` (checked again at the pin: it holds) |
| `worlds-runtime:481` | hands-on | home | Exercise, one with `foundation:537` below, so that the page holds four exercises (style.md §6.3): measure a run with `--frames 600 --perf-log run.csv --resolution 1280x720` and compare `--quality low` and `ultra` |
| `worlds-runtime:502-506` | hands-on | home | Exercises: add a runtime option to `c_Arguments` and `CheckOptions`; add a perf-log column group and make it write the wrong count; trace a scene switch, as the page's trace it yourself (D27): a breakpoint in `GameRuntime::HandleSceneRequests` catches a script's `Game::LoadScene`, one in `StartScene` shows the swap once the load is ready, and a Tracy capture shows the `Scene.Load` stage on the frames between (`Strata/src/Strata/Runtime/GameRuntime.cpp:339-362`, `:226-282`, `:211-224`, `:296-314`) |
| `gamedev:559` | hands-on | home | The same exercise as router-gamedev words it (`--mute`, with tests of the exit codes), merged with worlds-runtime:502 (taken from `router-gamedev`) |
| `gamedev:388` | code | home | `StrataRuntime/src/RuntimeApplication.cpp:339-354`: `c_Arguments`, every option the runtime understands, which `CheckOptions`, the usage and `reference/worlds-runtime` read; the excerpt's second half, the export's states (`StrataEditor/src/Editor/GameExport.h:65-75`), is shown on `worlds/export` (taken from `router-gamedev`) |
| `worlds-runtime:554-556`, `worlds-runtime:561-562` | term | home | Loading scene, start scene, runtime, perf log, column group |
| `worlds-runtime:557` | term | use | Headless, as `core/first-frame`'s one entry of the word defines it (the merge "Headless"); this page keeps headless runs as a feature (`book.md`'s row of the runtime) |
| `worlds-runtime:135` | feature | use | `GameGraphicsService` as the graphics half of the players' options (home `image/quality-settings`) |
| `worlds-runtime:140` | feature | use | The runtime links no tooling, and `StrataRuntime.NoTooling` reads its linker map (home `core/layers-registries`) |
| `worlds-runtime:161` | feature | use | Patch packs mounted in `Create` (home `assets/packs-export`) |
| `worlds-runtime:146` | feature | use | The manifest's fields the runtime reads (home `worlds/game-identity`) |
| `worlds-runtime:133` | feature | use | `GamePresentation` applied to the window before anything starts (home `worlds/game-identity`) |
| `worlds-runtime:191` | feature | use | `Runtime.Game` (`StrataTests/src/Runtime/GameRuntimeTests.cpp:162-1068`), `Runtime.PerfLog`, `Runtime.FramePerfLog`, `Runtime.GameGraphics`, `GPU.Runtime.GameRenderer` and the `StrataRuntime.*` CTests |
| `render-core:193` | feature | use | `GameRenderer` as the render-core inventory lists it |
| `scripting:198` | feature | home | The exported game's script engine: `GameRuntime` loads the module in place (no hot reload) and makes it active before the start scene plays; a crash disables the scripts for the session, a headless run exits with code 2 (`StrataRuntime/src/RuntimeApplication.cpp:150-159`); taught with worlds-runtime:329 and 333 above (taken from `scripting`) |
| `scripting:685` | open | home | Settled at the pin: `GameRuntime`'s script handling is `Strata/src/Strata/Runtime/GameRuntime.cpp:100-115` (an engine of its own, the module next to the manifest, active before the start scene), `147-154` (the classes counted in the log), `166-168` (the host's engine restored) and `CheckScriptFault` at `316-337` (the crash logged once, its location when symbolized); the page reads it with scripting:198 (taken from `scripting`) |
| `scripting:199` | feature | use | The engine services a host provides |
| `foundation:56` | feature | use | `CommandLine` and `CommandLineOptions` |
| `build-test:123` | feature | use | The runtime option tests |
| `foundation:537` | hands-on | home | Exercise: run `StrataRuntime --game <file> --headless --frames 300` and `--seconds 5`, and explain from `GetPlayedSeconds` and the kept fixed steps why one run's game time and the other's frame count differ across machines (`StrataRuntime/src/RuntimeApplication.cpp:186-197`); it needs an exported game; the second half of the exercise of `worlds-runtime:481` (taken from `core`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The manifest, `GamePresentation` and the game's identity | `worlds/game-identity` | must |
| Engine modules and engine services (`ApplicationSpecification::Modules`, scoped providers) | `core/engine-modules` | must |
| Console and GUI programs, exit codes, fatal error dialogs | `core/platform` | must |
| From `main` to the first frame: `CreateApplication`, `ApplicationLaunch`, `GetProgramRun`, the specification, `CommandLine` | `core/first-frame` | must |
| Layers and the application's frame (`Layer::OnAttach`, `OnUpdate`) | `core/windows-events` | must |
| The frame loop and its pacing | `core/frame-loop` | must |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The fixed step's code in `Scene` (`GetMaxFixedSteps`, `GetFixedStepCount`) | `world/systems` | must |
| Loading scenes: `SceneLoader`, prepared loads, `ReleaseInBackground`, the frame's `SceneWorkBudget` | `world/sub-scenes` | must |
| Residency and trimming after a switch | `assets/residency` | must |
| Asset packs and patch packs | `assets/packs-export` | must |
| The script system and a crashed module | `scripting/script-system` | must |
| Players' graphics options (`IGameGraphics`) and presets | `image/quality-settings` | must |
| The frame profiler and its stages | `core/profiling` | must |
| GPU timestamps and stages | `gpu/readback-timing` | must |
| The layer table and no tooling in games | `core/layers-registries` | must |
| Interpolation of fixed steps | `world/interpolation` | helps |
| The renderer's frame | `gpu/frame-tour` | helps |
| Exposure adaptation | `image/exposure` | helps |
| TAA history | `image/taa` | helps |
| Overlay passes: screen-space UI over an empty frame | `gpu/debug-drawing` | helps |
| Swapchains | `gpu/vulkan-nvrhi` | helps |
| Crash containment of scripts | `scripting/crash-containment` | helps |
| Players' bindings | `input/rebinding` | helps |
| The audio engine and its null device | `audio/engine` | helps |
| Text in a scene (`TextComponent`) | `gpu/text` | helps |
| Where a game's saves and log go | `worlds/game-identity` | helps |
| The save service of a game (`IGameSaves`) as scripts use it | `scripting/host-api` | helps |
| Command scripts and simulated input in the editor | `editor/command-scripts` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `column-group` | Column group | - |
| `loading-scene` | Loading scene | - |
| `perf-log` | Perf log | - |
| `start-scene` | Start scene | - |
