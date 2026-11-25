---
id: reference/worlds-runtime
title: "Worlds, export, runtime options, manifest"
description: "The world document, project file, game manifest, players' files, runtime options, exit codes, perf log and exported files, in tables."
kind: reference
size: M
tracks: []
needs: [worlds/runtime]
status: final
---

This page holds the files and options that a large world, an export and the :term[runtime]{id=runtime} read or write. Each table has an introduction that names the page teaching its subject. The tables follow the path of a game: the world document, its limits, the project file, the manifest, the players' files, the runtime's :term[command line]{id=terminal-command} and :term[perf log]{id=perf-log}, the commands and the exported folder. A :term[file format]{id=file-format} is a table whose rows are keys: the first column is the key, the others say its type, its default and what it does. Unless a table says otherwise, a key that the engine reads and finds invalid makes the whole file fail to load, with a message that names the key.

## The world document

A world is a scene that streams its content in squares called cells; [Grids, keys and layers](../worlds/grids.md) teaches the idea. Its document has the extension `.stworld`. The file starts with the :term[header]{id=header} `{"Strata": {"Format": "World", "Version": 1}}` and holds one `World` object. The rows below come from `Strata/src/Strata/World/WorldAsset.cpp` and `Strata/src/Strata/World/WorldAsset.h`, and are written by hand: the generator has no table for them.

| Key | Type | Default | What it does |
| --- | --- | --- | --- |
| `Name` | string | empty | The world's name: at most 256 characters, no control characters |
| `PersistentScene` | scene handle | none | The scene that holds what is always loaded; no cell may use it |
| `GridOrigin` | two numbers, X and Z | 0, 0 | The corner of cell (0, 0) of every layer, in metres, within 1,000 km of the origin |
| `Layers` | array of layers | required | One to 32 layers |
| `Cells` | array of cells | empty | The cells that have content, at most 1,048,576 |
| `Index` | object | none | The cook's measurements; present after `world.cook` |

A layer is a grid of its own, so one world can stream terrain in large squares and props in small ones. A layer row is an object inside `Layers`.

| Layer key | Type | Default | What it does |
| --- | --- | --- | --- |
| `ID` | whole number, 1 to 255 | required | Names the layer in cells; unique in the world |
| `Name` | string | required | One to 64 characters; unique; no commas, control characters or space at either end |
| `CellSize` | number, metres | required | The side of the layer's square cells, 1 to 65,536 |
| `StreamingDistance` | number, metres | required | Cells within this distance of a source load, 0 to 1,000,000 |
| `EnabledByDefault` | :term[boolean]{id=boolean} | true | Whether the layer streams until a game disables it |
| `LoadBeforeStart` | boolean | false | Whether the world waits for this layer's cells around the sources before it starts |

A cell row has four keys. `Layer` is the identifier (ID) of a layer of the world. `X` and `Z` are whole numbers: the cell's square starts at `GridOrigin` plus `X` times `CellSize`. `Scene` is the handle of the scene that holds the cell's entities. Two cells never share a scene, a :term[cell key]{id=cell-key} appears once, and no cell uses the :term[persistent scene]{id=persistent-scene}.

Each cell has its own scene document, so an editor edit of one cell never rewrites another. The editor writes it to `<world folder>/<world name>/<layer name>/<X>_<Z>.stscene`. The scene's handle is not random: the editor derives it as the :term[sub-asset]{id=sub-asset} `Cell/<layer ID>/<X>/<Z>` of the world, so that an undo step can refer to a cell before its file is written.

The `Index` object is the cook's result, and `GetRecommendedMaxBodies` reads it. It holds `Version` (1), `MaxBodiesInRadius` and `PersistentBodies` (counts), and `Cells`. `Cells` has one summary per cell, with `Layer`, `X`, `Z` and `Stamp` (the cell document's :term[content stamp]{id=content-stamp} when measured; the index is stale once it differs). Each summary also has `Entities`, `Bodies`, `Bounds` (`Min` and `Max`, each three numbers) and `ClosureBytes`.

`GetRecommendedMaxBodies` turns the index into the number of physics bodies to make room for: 1.25 × `MaxBodiesInRadius`, rounded up, and never more than the physics limit. A worked case: 1,000 bodies in the busiest radius ask for 1,250; the extra quarter leaves room for bodies a game creates while it plays.

## World limits

The :term[loader]{id=loader} rejects a document that breaks a limit, and `Validate` applies the same rules to a world built in code. The values come from `WorldData` in `Strata/src/Strata/World/WorldAsset.h` and `WorldCellKey` in `Strata/src/Strata/World/WorldGrid.h`. The reasons are in [Grids, keys and layers](../worlds/grids.md).

| Constant | Value | Meaning |
| --- | --- | --- |
| `WorldData::c_MaxLayers` | :value{key="limits.WorldData.c_MaxLayers"} | Layers in a world |
| `WorldData::c_MaxCells` | :value{key="limits.WorldData.c_MaxCells"} | Cells with content in a world |
| `WorldData::c_MinCellSize` | :value{key="limits.WorldData.c_MinCellSize"} | Smallest `CellSize`, in metres |
| `WorldData::c_MaxCellSize` | :value{key="limits.WorldData.c_MaxCellSize"} | Largest `CellSize`, in metres |
| `WorldData::c_MaxStreamingDistance` | :value{key="limits.WorldData.c_MaxStreamingDistance"} | Largest `StreamingDistance`, in metres |
| `WorldData::c_MaxExtent` | :value{key="limits.WorldData.c_MaxExtent"} | Every cell lies within this distance of the origin in X and in Z, in metres (1,000 km) |
| `WorldData::c_SupportedExtent` | :value{key="limits.WorldData.c_SupportedExtent"} | The distance the engine supports, in metres (20 km); `world.cook` warns about cells beyond it |
| `WorldCellKey::c_MaxCoordinate` | :value{key="limits.WorldCellKey.c_MaxCoordinate"} | Largest cell `X` or `Z`, plus or minus, that a packed key holds |

The gap between 1,000 km and 20 km has a reason. A 32-bit :term[floating-point number]{id=floating-point-number} has fewer steps the farther it lies from the origin: at 20 km, a position can only move in steps of 2 to 4 mm, and beyond that, objects visibly :term[jitter]{id=jitter}. The document still loads, because a later version of the engine may move the origin along with the player. The cost is that you must keep a world inside 20 km today.

## The project file

The project file, `.stproj`, names the game's folders and identity; [Projects and settings](../world/projects-settings.md) teaches it. The header is `{"Strata": {"Format": "Project", "Version": 3}}`. Versions 1 and 2 still load, and a save writes version 3; version 1 has no `Scripts` object, and versions 1 and 2 have no `Settings`. The rows are checked against `Strata/src/Strata/Project/Project.cpp`.

| Object | Key | Type | What it does |
| --- | --- | --- | --- |
| `Project` | `Name` | string | The project's name, which also keys the game's save and log folders; no control characters |
| `Project` | `AssetDirectory` | relative path | The asset folder, inside the project |
| `Project` | `StartScene` | scene handle | The scene the game starts with |
| `Scripts` of `Project` | `SourceDirectory`, `ModuleName` | strings | Where the scripts live and the name of the module; the module name is stored even when derived |
| `Export` of `Project` | `AlwaysInclude` | array of asset paths | Assets and folders a pruned export keeps, relative to the asset folder |
| `Export` of `Project` | `LoadingScene` | scene handle or null | The scene shown while its :term[start scene]{id=start-scene} loads |
| `Game` | `Title`, `Version`, `Company`, `Copyright`, `Icon` | strings; `Icon` a texture handle or null | The game's identity ([game identity](../worlds/game-identity.md)); written only when it differs from the default |
| top level | `Settings` | object of sections | The :term[settings sections]{id=settings-section-world}, listed in [Settings](../reference/settings.md) |

Members the engine does not know are kept and written back. The file may take at most 1 MiB, and a save that would write more fails with a message. The identity has its own rules. A title, a company and a copyright line take at most 128 characters without control characters. A version is one to four whole numbers from 0 to 65535 separated by dots, such as `1.2.0`.

## The game manifest

An export writes `<File>.stgame` next to the program, and the runtime reads it first; [Game identity](../worlds/game-identity.md) teaches it. The header is `{"Strata": {"Format": "Game", "Version": 5}}`, and an engine that finds a higher version refuses the file and says which versions it reads (1 to 5). The rows are checked against `Strata/src/Strata/Project/GameManifest.cpp`.

| Object | Key | Type | Default | What it does |
| --- | --- | --- | --- | --- |
| `Game` | `Name` | string | `Game` | The project's name; keys the save and log folders, so a new title never moves players' saves |
| `Game` | `Title` | string | empty | What the window shows; empty shows `Name` |
| `Game` | `Version` | string | `1.0.0` | The game's version, one to four numbers |
| `Game` | `Company`, `Copyright` | strings | empty | Optional identity text, at most 128 characters |
| `Game` | `Icon` | file name | empty | A 256 × 256 PNG next to the manifest; empty means none |
| `Game` | `AssetPack` | file name | required | The pack of assets |
| `Game` | `PatchPacks` | array of file names | empty | Packs mounted over the :term[asset pack]{id=asset-pack} in this order, at most 256; their entries replace those with the same handles |
| `Game` | `StartScene` | scene handle | required | The first scene |
| `Game` | `LoadingScene` | scene handle or null | null | Played while the start scene loads |
| `Game` | `ScriptModule` | file name | empty | The script module; empty without scripts |
| `Game` | `Window` | object | 1280 × 720, windowed, :term[vsync]{id=vsync} on | `Width` and `Height` (clamped to 1 to 16,384), `Fullscreen`, `VSync` |
| top level | `Settings` | object of sections | empty | The project's settings, stored as they were; the runtime checks their values later, and the manifest size check is the only one at load |

The plain file-name rule keeps a manifest from pointing the runtime elsewhere: every file the manifest names must lie next to it. A name with a folder part, an :term[absolute path]{id=absolute-path}, `.` or `..` is refused, and so is an empty asset pack name. Without the rule, a manifest someone passes you could make the runtime load a file from anywhere on the disk.

The format grew in five steps, and the older ones still load.

| Version | What it added | What an older file lacks |
| --- | --- | --- |
| 1 | Name, asset pack, start scene, window | The script module: such a game has no scripts |
| 2 | `ScriptModule` | `PatchPacks` |
| 3 | `PatchPacks` | `LoadingScene` |
| 4 | `LoadingScene` | The identity and `Settings` |
| 5 | `Title`, `Version`, `Company`, `Copyright`, `Icon` and `Settings` | Nothing |

For a file older than 5, the title is the name, the version is empty and the settings are absent. An empty version names none in any version, so such a file saved again still loads.

## The players' files

A player's choices live in the game's save folder, which the runtime puts under the player's data folder, `<Game>/Saves`, or in the folder that `--save-directory` names. Two files hold them, and each is read within 64 KiB; the folder map of a whole project is on [the editor reference](../reference/editor.md). [The runtime](../worlds/runtime.md) teaches how the game uses them. Only `GameGraphicsService` writes the first file, and `InputActions` writes the second one.

| File | Header | Keys | What it holds |
| --- | --- | --- | --- |
| `GraphicsOptions.json` | `Format` `GraphicsOptions` and `Version` 1, in `Strata` | `Section` (`Id`, `Version`), `Options` | The player's choices of the fields of the graphics section `Renderer.Quality`, in the :term[stored form]{id=stored-form} of each field |
| `InputBindings.json` | `Format` `InputBindings` and `Version` 1, in `Strata` | `Actions` | For each action by its qualified name, such as `Gameplay/Jump`, the list of bindings that replaces the project's, such as `Key/Space` |

A graphics file written by a later game version is refused, and a field the section now refuses is dropped while the others stay. A file larger than 64 KiB is refused whole.

Three services hand these files to a game. A service is an interface the engine finds by type, so engine code that may not include the module still reaches it. [The script host](../scripting/host-api.md) and [The runtime](../worlds/runtime.md) teach them. The runtime and the editor's play mode provide them (`Strata/src/Strata/Core/EngineServices.h`).

| Service | What it offers |
| --- | --- |
| `IGameWindow` | Requests for the window's mode, resolution (1 to 16,384 pixels) and vsync, and its state |
| `IGameSaves` | The game's save folder, or nothing while there is none |
| `IGameGraphics` | The value in effect of each graphics option, its source (project, player or command line), the player's choices, and set, reset and save |

`IWorldStreaming`, which a running scene offers (`Strata/src/Strata/Scene/SceneServices.h`), asks cells around a position, tells whether they have loaded, enables a layer by name and reports the cell counts that the perf log writes. Its component and script functions are in [Components](../reference/components.md) (`World`, `StreamingSource`) and [the script reference](../reference/script-api.md).

## The runtime's command line

`StrataRuntime` plays an exported game, and [The runtime](../worlds/runtime.md) teaches its start. Run it from a terminal for an option to apply ([A command line with options](../basics/tools.md)). Without `--game`, the runtime looks beside itself for `<executable name>.stgame`, and otherwise for the only `.stgame` file in its folder; two files or none end the start.

::include{file="options-runtime.md"}

An unknown option prints the usage and ends the process. The :term[exit codes]{id=exit-code} below are the process's own.

| Code | When |
| --- | --- |
| 0 | The game ended normally, or `--help` printed the usage |
| 1 | The game cannot start; an exception from a library ends a frame, unless the run had failed before; the perf log cannot be written or comes out incomplete; a screenshot fails, shows the missing-camera message, or shows a cleared frame because the start scene still loads |
| 2 | A headless run, where a script crashed |
| 3 | An option the runtime does not understand, or an option with a wrong value |
| 130 | The run was interrupted (**Ctrl+C**), unless it had failed before |
| any other | The code the game chose when it quit |

## The runtime's perf log

`--perf-log` writes a file of comma-separated values with one row per frame; [Measuring performance](../make/performance.md) shows how to read it. The generated table lists the columns in the order the file writes them, and its descriptions are those of the source: several columns share one. A frame that was not captured leaves its engine and :term[renderer]{id=renderer} columns empty.

::include{file="perf-log.md"}

A column name ends in its unit. `Ms` is milliseconds, `MB` counts 2^20 :term[bytes]{id=byte}, `Percent` is a share of 100, and a name with no unit, such as `DrawCalls` or `PhysicsContacts`, is a count. `Frame` is the frame's index.

`WorldCellsWanted`, `WorldCellsLoading`, `WorldCellsLoaded` and `WorldCellsUnloading` are the cell counts of `IWorldStreaming`. The `Physics...` columns are bodies, contacts and the last step's times, and `PhysicsMaxBodySpeed` is in metres per second. The log enables the physics detail counters when it starts, so the two contact columns fill from the scene's next step.

## The commands

Every command is a method of the editor's automation interface; the full rows are in [Commands](../reference/commands.md), and [Export](../worlds/export.md) teaches the steps.

| Group | Commands |
| --- | --- |
| `world.*` | `world.create`, `world.cook`, `world.setLayers`, `world.status`, `world.info`, `world.edit`, `world.loadCells`, `world.moveEntities` |
| Export | `project.export`, `project.exportStatus`, `project.cancelExport`, `project.setExportSettings` |
| Game info and start | `project.setGameInfo`, `project.setStartScene`, `project.info` |
| Templates | `project.templates`, `project.create` |

`world.create` makes four layers, `Terrain`, `Buildings`, `Props` and `Gameplay`, each with `cellSize` 64 m by default and a :term[streaming distance]{id=streaming-distance} of four cells, and the first loads before the start. The world files are `<path>.stworld` and its persistent scene `<path>.stscene`.

## The exported folder

`project.export` writes a folder of plain files; it is not an installer. `<File>` is the project's name with only letters, digits, spaces, `-` and `_` kept. The list comes from `StrataEditor/src/Editor/GameExport.cpp`.

| File | What it is |
| --- | --- |
| `<File>.exe` on Windows, `<File>` elsewhere | The copy of the runtime, made unless the export omits it; on Windows its version and icon are written into it |
| `<File>.stgame` | The manifest |
| `<File>.stpak` | The asset pack |
| the script module and, when the export asks for them, its symbols | The scripts, when the project has a loaded module; editors that are not shipping builds include the symbols by default |
| `<File>.png` | The icon, 256 × 256, when the project has one |
| `ThirdPartyNotices.md` | The notices of the engine's libraries, copied with the runtime |
| `<File>.desktop` | A :term[desktop entry]{id=desktop-entry}; only on Linux, and only with the runtime |
| :term[patch packs]{id=patch-pack} | Not written by the export: you add them next to the manifest and list them in `PatchPacks` of `Game` |

## Where it lives in Strata

- `Strata/src/Strata/World/WorldAsset.h` and `Strata/src/Strata/World/WorldAsset.cpp`: the world document, its limits and its validation.
- `Strata/src/Strata/World/WorldGrid.h`: the packed :term[cell key]{id=cell-key}.
- `StrataEditor/src/Editor/EditorWorld.cpp`: the cell files' layout and :term[derived handles]{id=derived-handle}.
- `Strata/src/Strata/Project/GameManifest.cpp`: the manifest and the plain file-name rule.
- `Strata/src/Strata/Project/Project.cpp`: the project file.
- `Strata/src/Strata/Project/GameInfo.h`: the identity rules.
- `Strata/src/Strata/Runtime/GameGraphicsService.cpp`: `GraphicsOptions.json`.
- `Strata/src/Strata/Input/InputActionSet.h`: `InputBindings.json`.
- `Strata/src/Strata/Core/EngineServices.h`: the three :term[engine services]{id=scene-service}.
- `StrataRuntime/src/RuntimeApplication.cpp`: `c_Arguments` and the exit codes.
- `Strata/src/Strata/Runtime/FramePerfLog.cpp`, `Strata/src/Strata/Runtime/GameRuntime.cpp` and `Strata/src/Strata/Runtime/GameRenderer.cpp`: the perf log's columns.
- `StrataEditor/src/Editor/GameExport.cpp`: the files of an export.
