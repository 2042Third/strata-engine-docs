# Brief: `reference/worlds-runtime`

| Field | Value |
| --- | --- |
| Title | Worlds, export, runtime options, manifest |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `worlds/runtime` |
| From | worlds-runtime ch. 12 (`.stworld`, `.stgame` v1-v5, `GraphicsOptions.json`, `world.*` and `project.*` commands, the runtime's command line from `c_Arguments` in `StrataRuntime/src/RuntimeApplication.cpp`); the runtime perf log's columns, generated from `FramePerfLog` and `GameRenderer::MakePerfLogColumns` |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/worlds-runtime` — Worlds, export, runtime options, manifest

**Covers.** The paragraph on top says what the page is: the formats, options and outputs of large worlds, the export
and the runtime, parsed at the pin. The tables, in this order. (1) The world document (`.stworld`, `{"Strata":
{"Format": "World", "Version": 1}}`): its keys (name, persistent scene, grid origin, layers, cells, the optional cooked
index), as a hand-checked table checked against `WorldAsset.cpp`, with the cell files' layout and derived handles. (2)
The world limits, parsed: `c_MaxLayers`, `c_MaxCells`, `c_MaxCellSize`, `c_MaxStreamingDistance`, `c_MaxExtent` and
`WorldData::c_SupportedExtent` (20 km). (3) The game manifest (`.stgame`, `c_FormatVersion` 5): every key with its
type, and the versions 1 to 4 that still load, each with what it added; checked against `GameManifest.cpp`. (4)
`GraphicsOptions.json`, the players' options file that only `GameGraphicsService` writes, and the players' bindings
file. (5) The runtime's command line, generated from `c_Arguments` of `RuntimeApplication.cpp` (every option, its
value and help text), with its exit codes. (6) The columns of the runtime's perf log, generated from `FramePerfLog`,
`GameRenderer::MakePerfLogColumns` and the runtime's own columns (`GameRuntime.cpp`), each with its unit. (7) The
`world.*` commands and the `project.*` commands of export, game info and templates, as names linking
`reference/commands`. (8) The installed layout of an exported game (the executable, the manifest, the pack, patch
packs, the script module, the icon), as a hand-checked list. Hand-written: one introduction per table, the plain
file-name rule of the manifest, and `## Where it lives in Strata` (`Strata/src/Strata/World/`,
`Strata/src/Strata/Runtime/`, `Strata/src/Strata/Project/`, `StrataRuntime/src/RuntimeApplication.cpp`,
`StrataEditor/src/Editor/GameExport.*`). The tools are `tools/reference.py parse` (routes "program options", "runtime
perf log", "scene and world limits") and the catalogue dumps.

**Leaves out.**

- Why levels stream; grids, keys and layers → `worlds/why-streaming`, `worlds/grids`
- The streamer → `worlds/streamer`
- The export and its steps → `worlds/export`
- The manifest, icons and platform files, as a design → `worlds/game-identity`
- The runtime and its headless runs → `worlds/runtime`
- Exporting and running a game, for game makers → `make/export`
- Reading a perf log to make a game fast → `make/performance`

**Fit.** `fits`: about 1,900 words against M (3,000). The generated tables give the page its size: the world limits, the
runtime's command line with its exit codes and the columns of the perf log, about 1,500 words. The prose is the
paragraph on top, eight introductions, the world-document and manifest tables (about 30 keys, with the manifest's
versions 1 to 4), the installed layout, one rule and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:23-29` | feature | link | The world document, layers, cells, the cell files' layout, the cooked index, validation and the limits |
| `worlds-runtime:34` | feature | link | Cell keys |
| `worlds-runtime:41-42` | feature | link | `World` and `StreamingSource`, as names linking `reference/components` |
| `worlds-runtime:46` | feature | link | `IWorldStreaming` |
| `worlds-runtime:57` | feature | link | The cell states that `world.status` reports |
| `worlds-runtime:90` | feature | link | The world host functions, as names linking `reference/script-api` |
| `worlds-runtime:110-112` | feature | link | `world.cook`, the world commands and `world.create`'s defaults |
| `worlds-runtime:125` | feature | link | `GameRuntimeOptions` behind the command line |
| `worlds-runtime:130` | feature | link | The runtime's perf-log columns |
| `worlds-runtime:132` | feature | link | The render perf columns |
| `worlds-runtime:135-138` | feature | link | `GameGraphicsService` and `GraphicsOptions.json`, `FramePerfLog`, the `StrataRuntime` executable with its options and exit codes, manifest discovery |
| `worlds-runtime:146-149` | feature | link | The `.stgame` manifest v5, the plain file-name rule, the game info and the save and log identity |
| `worlds-runtime:167` | feature | link | The export commands |
| `worlds-runtime:169` | feature | link | The installed layout |
| `scene-ecs:214-216` | feature | link | The export settings, the game info and `GameManifest` from the project's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Worlds, cells and layers | `worlds/grids` | must |
| The export | `worlds/export` | helps |
| The runtime and its options | `worlds/runtime` | must |
| A command line with options | `basics/tools` | helps |
| JSON values and objects | `basics/data-formats` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-1 | must | missing-item | new item on `reference/worlds-runtime`; the Leaves out of `reference/settings` | No page of the unit lists the keys of the project file `.stproj`. `reference/settings` sends "the project file's other keys (game info, export settings)" to `reference/worlds-runtime`, whose eight tables do not hold them, and `reference/scene` gives the file one row (format v3), so the link leads to a table that does not exist. | `reference/worlds-runtime` adds a hand-checked table of the project file, checked against `Project.cpp`: the header (Format "Project", Version 3; versions 1 and 2 still read and migrated); `Project` with `Name`, `AssetDirectory`, `StartScene`, `Scripts` (`SourceDirectory`, `ModuleName`), `Export` (`AlwaysInclude`, `LoadingScene`) and `Game` (`Title`, `Version`, `Company`, `Copyright`, `Icon`); `Settings`, whose sections are `reference/settings`'; unknown members kept; the 1 MiB cap. Its introduction names `world/projects-settings`. The row `scene-ecs:214-216` widens its take to this table, and `reference/scene`'s row links it. About 150 words. | `allocation/reference.md:277`, `:788-801`, `:326-328`, `:840`; `allocation/world.md:848-853`; `Strata/src/Strata/Project/Project.cpp:22-23`, `:229-310`, `:388-415`; `Strata/src/Strata/Project/Project.h:71-73`, `:101-103` |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-7 | should | missing-item | new item on `reference/editor` | No page lists the files Strata keeps outside a project's assets. In `<project>/.strata/`: `Cache` with `ImportRecords.log`, `Scripts/Build`, `Scripts/IDE` and `Scripts/Bin`, `Saves` with `GraphicsOptions.json` and `InputBindings.json`, `Trash` (kept 30 days), `Recovery`, `Bake`, `Thumbnails`, `Thumbnail.png`, `EditorSession.json` and `EditorViewport.json`; in the user data folder `Strata/`: `Logs/StrataEditor.log`, `Preferences.json`, `EditorSettings.json`, `RecentProjects.json`, `Sessions/`, `Builds/` and `Projects/`; and a game's `<Name>/Logs/Game.log` and `<Name>/Saves`. Teaching pages name them one at a time, and `RecentProjects.json` on no page. | `reference/editor` adds a hand-checked table "Files outside the assets": the path (with the user data folder of each system), who writes it, what it holds, the variable that moves it (`STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR`, `STRATA_RUNTIME_DIR`), whether it may be deleted, and the page that teaches it. `reference/worlds-runtime`'s table (4) and `reference/game-makers`' project folder link it. About 250 words. | `allocation/reference.md:855-871`, `:795-796`, `:1166-1168`; `Strata/src/Strata/Core/Platform.h:71-77`, `:115-129`; `StrataEditor/src/EditorApplication.cpp:283-286`; `StrataEditor/src/Editor/EditorPreferences.cpp:61-67`; `StrataEditor/src/Editor/ExternalEditor.cpp:207-213`; `StrataEditor/src/Editor/RecentProjects.cpp:21`, `:57-63`; `Strata/src/Strata/Network/EditorSession.cpp:146-156`; `StrataEditor/src/Editor/ScriptBuild.cpp:490-492`, `:509`; `StrataEditor/src/UI/ProjectDialogs.cpp:138`; `Strata/src/Strata/Project/Project.h:109-117`; `StrataEditor/src/Editor/EditorContext.cpp:71-75`, `:1647`; `StrataRuntime/src/RuntimeApplication.cpp:458`; `Strata/src/Strata/Core/SaveFiles.cpp:222` |
| critic-reference-10 | should | thin-home | `reference/editor`, table (1); `reference/worlds-runtime`, table (5) | `reference/editor` gives one exit code, 3 for a bad argument. At the pin the editor also exits with 1 when its command script cannot be read, fails, or has not finished at `--frames` or at `editor.quit`, when a screenshot fails, and when a headless editor without `--frames` has no automation; every program exits with 130 after an interrupt. CI runs and agents read these codes. | Table (1) lists every exit code of the editor with its causes, hand-checked against `EditorLayer.cpp` (about 80 words); the runtime's exit codes on `reference/worlds-runtime` name 3 and 130 beside 1, 2 and the game's own. This is the reference side of critic-foundation-11, which changes `core/first-frame`. | `allocation/reference.md:859-860`, `:796-797`; `allocation/completeness.md:184`; `StrataEditor/src/EditorLayer.cpp:521`, `:544`, `:557`, `:589`, `:679`, `:697`; `Strata/src/Strata/Core/CommandLineOptions.h:27`; `Strata/src/Strata/Core/Application.h:71`; `StrataRuntime/src/RuntimeApplication.cpp:36`, `:432-438` |
| critic-reference-12 | should | missing-item | `reference/audio-input`, `reference/ui`, `reference/worlds-runtime` | `reference/physics` and `reference/animation` list their scene services with each function's comment; the other area pages do not. So `IAudioPlayback` and `IAudioOutput`, `IUIControl` (beside the event types of `IUIEvents`), `IWorldStreaming` (a link row with no table) and the engine services `IGameWindow`, `IGameSaves` and `IGameGraphics` are on no reference page, though engine code reaches those modules only through them. | Each of the three pages adds the parsed table of its services, as `reference/physics` (4) does (about 30 words each); `reference/worlds-runtime` also takes the three engine services of `EngineServices.h`, which the runtime and the editor provide, with an introduction that names `scripting/host-api` and `worlds/runtime`. | `allocation/reference.md:564-566`, `:627-628`, `:679-691`, `:736-746`, `:788-801`, `:829`; `Strata/src/Strata/Scene/SceneServices.h:242`, `:485`, `:538`, `:552`, `:584`; `Strata/src/Strata/Core/EngineServices.h:103`, `:125`, `:152` |
