# Brief: `worlds/export`

| Field | Value |
| --- | --- |
| Title | Shipping a game: the export |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `worlds/physics-scripts`, `assets/packs-export`, `world/projects-settings`, `core/files` |
| From | worlds-runtime ch. 8, the internals half (the export's state machine, up-front checks, "fail before writing", planning, world cooking at export, what the folder holds); the pack is `assets/packs-export`, the use side `make/export` |
| Unit | `plan/allocation/worlds.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `worlds/export` — Shipping a game: the export

**Covers.** How `GameExport` turns the open project into a folder a player can run, without blocking a frame. The
problem: what the editor keeps (sources, imports, a project file, a loaded script module) is not what a game ships, and
engines answer with a build step (Unity's player build, Unreal's cook and pak); Strata's export writes an asset pack, a
manifest, the script module, an icon and a renamed runtime. The map shows the main thread and the I/O job and the state
machine WaitingForImports → CookingWorlds → Packing → Copying → Succeeded, Failed or Cancelled, with the progress in
bytes and the stage text that the Export dialog and `project.exportStatus` show. Then the work in the order data flows.
`Start` checks what it can without reading the project's files and fails without side effects: a project, no Play, the
scene saved or its save in flight, an export directory that is absolute, local, outside the project and free of device
names, a start scene, the runtime and its notices beside the editor, the loaded script module unchanged, the loading
scene, valid settings sections, the title and the icon's source. Four of its decisions are told with them: without a
start scene in the project the open scene is the start scene; the loading scene may not be the start scene; a pruned
pack keeps the loading scene and every asset that the settings sections name, and a section that names an asset the
project lacks fails the export; the manifest's window (1280 by 720, windowed, vsync on) comes from the export's options,
not from a project setting. `Update` waits for background imports and saves, scans the documents whose reference search
had not run on a job, starts the cooks of stale worlds, writes their indexes like import results (no undo step) and
records the physics room each persistent scene needs, then plans the pack once on the main thread (the pack itself is
`assets/packs-export`'s).

The I/O job follows the rule "fail before writing": the icon is decoded and the Windows runtime stamped in memory before
the pack is written, so that a failed export never leaves a new pack beside an old executable; the packed persistent
scene gets the cooked physics capacity; then the script module exactly as loaded, named in the manifest's
`ScriptModule`, with its PDB outside Dist, the icon, the manifest, the executable, the third-party notices and the Linux
desktop entry. The folder it leaves, the commands that drive it, and the not-done paragraph (no exports for another
platform, no macOS app bundle, no signed exports, no crash reports in shipped games) close the page. At the end the
reader can name every file of an exported game and the check that guards it, and can add a check to the state where it
belongs.

**Leaves out.**

- The pack: its format, planning, pruning, `AlwaysInclude`, patches and cooked documents → `assets/packs-export`
- The manifest, the icon, the version resources and the desktop entry → `worlds/game-identity`
- The Export dialog → `editor-ui/launcher-dialogs`
- Exporting a game step by step → `make/export`
- Saves in flight and the `DocumentSaver` → `editor/saving`
- The engine's installed layout and its releases → `engineering/releasing`
- Running the exported game → `worlds/runtime`

**Fit.** `over`: about 4,900 words against M (3,000). The next size is L (S2), the size the page had before the first
size pass: five excerpts of `Start`, `Update` and the I/O job, the up-front checks with four decisions of `Start`, and
two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:279` | concept | home | Shipping, from project to product: editor data against runtime data; the player build and cook and pak compared; Strata's export; the mistake that assets a script loads by path vanish from a pruned pack |
| `worlds-runtime:155` | feature | home | `GameExport`, the non-blocking state machine with progress in bytes and stage text (`StrataEditor/src/Editor/GameExport.h:65-189`; `GameExport.cpp:165-862`) |
| `worlds-runtime:372` | figure | home | The export's state machine, which thread does what, and where each check happens |
| `worlds-runtime:156` | feature | home | The up-front checks, and `CheckExportDirectory` (`GameExport.h:191-193`); four decisions of `Start` with them (critic-worlds-runtime-14): without a start scene in the project the open scene is the start scene; the loading scene may not be the start scene; a pruned pack keeps the loading scene and every asset that the settings sections name, and the export fails when a section names an asset the project lacks; the manifest's window (1280 by 720, windowed, vsync on) comes from the export's options, not from a project setting (`StrataEditor/src/Editor/GameExport.cpp:187-191`, `:222-227`, `:257-276`, `:314-316`; `GameExport.h:39-41`; `Strata/src/Strata/Project/GameManifest.h:58-61`) |
| `new:3` | code | home | `StrataEditor/src/Editor/GameExport.cpp:165-228`: the first checks of `Start`: no project, playing, unsaved scene, the directory, the start scene, the runtime and its notices, the script module, the loading scene |
| `new:4` | code | home | `StrataEditor/src/Editor/GameExport.cpp:129-163`: `CheckExportDirectory`: network and device paths, relative paths, reserved device names, inside the project, a file |
| `worlds-runtime:157` | feature | home | Waiting and planning: imports and saves polled, pending reference searches scanned on a job, the plan made once on the main thread, the writing on an I/O job |
| `assets:217` | feature | home | The export as the asset inventory lists it: `GameExport` polls `HasPendingImports`, plans, writes the pack on an I/O thread; taught with worlds-runtime:155 and 157 above (taken from `assets`) |
| `new:5` | code | home | `StrataEditor/src/Editor/GameExport.cpp:335-409`: `Update` while waiting: cancellation, imports and saves, the awaited save, the document scan on a job, then cooking or planning |
| `worlds-runtime:158` | feature | home | World cooking at export: stale worlds cooked, indexes written like import results, `RecommendedMaxBodies` passed through `AdjustSceneSettings` |
| `new:6` | code | home | `StrataEditor/src/Editor/GameExport.cpp:491-525`: `FinishCooking`: the index as derived data without an undo step, written only when it changed; the capacity per persistent scene |
| `worlds-runtime:446` | rule | home | Fail before writing: decode the icon and stamp the executable before the pack, so that a failed export never leaves a half-new folder |
| `worlds-runtime:336` | code | home | `StrataEditor/src/Editor/GameExport.cpp:595-650`: the icon first, the Windows stamp before the pack, the packed scene settings adjusted |
| `worlds-runtime:162` | feature | home | The script module exactly as the editor loaded it, its PDB unless Dist or `includeScriptSymbols: false`; a failure when scenes use scripts without a module (`GameExport.cpp:585-593`, `663-675`) |
| `scripting:212` | feature | home | The module and its PDB next to the game, named by its file name in the manifest's `ScriptModule` (`StrataEditor/src/Editor/GameExport.cpp:313`; the field since manifest version 2, `Docs/DeveloperGuide.md:2105-2108`); taught with worlds-runtime:162 above (taken from `scripting`) |
| `worlds-runtime:374` | figure | home | The exported folder: executable, `.stgame`, `.stpak`, the module and its PDB, the 256-pixel PNG, `ThirdPartyNotices.md`, the `.desktop` file on Linux, with arrows to what reads what |
| `worlds-runtime:167` | feature | home | `project.export`, `project.exportStatus`, `project.cancelExport`, `project.setExportSettings`, `project.setGameInfo`, `project.setStartScene`, each as a line to paste with a link to `editor/commands` |
| `new:7` | not-done | home | Exports for another platform, macOS app bundles, signed exports and crash reports in shipped games (the export copies the runtime next to the editor). Evidence: `Docs/Releases/0.7.0.md:411-412`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1684-1685` (checked again at the pin: it holds) |
| `worlds-runtime:479` | hands-on | home | Exercise: set the identity and icon, choose a loading scene, export, run the executable, find the log and save folders |
| `new:21` | hands-on | home | Trace it yourself (D27): a breakpoint in `GameExport::Update` follows one export from `WaitingForImports` through `CookingWorlds` and `Packing` to `Copying`, and a search for `fail(` in `Start` lists every up-front check with its message, in the order the page gives them. Evidence: `StrataEditor/src/Editor/GameExport.cpp:165-322` (`Start`), `:335-463` (`Update`); `StrataEditor/src/Editor/GameExport.h:65-75` (`GameExportState`) |
| `worlds-runtime:548` | term | home | Export |
| `worlds-runtime:159-161` | feature | use | The asset pack, pruning and patch packs, one paragraph each with links (home `assets/packs-export`) |
| `worlds-runtime:442` | rule | use | Pruning is off by default (home `assets/packs-export`) |
| `worlds-runtime:110` | feature | use | The cook that the export runs (home `worlds/physics-scripts`) |
| `worlds-runtime:163-165` | feature | link | The icon, the version resources and the desktop entry the I/O job writes (home `worlds/game-identity`) |
| `worlds-runtime:168` | feature | use | The Export dialog follows an export an agent started (home `editor-ui/launcher-dialogs`) |
| `worlds-runtime:400` | figure | use | The Export dialog during an export, showing the stage text (home `editor-ui/launcher-dialogs`) |
| `worlds-runtime:169` | feature | link | The installed layout that puts the runtime beside the editor (home `engineering/releasing`) |
| `worlds-runtime:191` | feature | use | `Editor.Export` (`StrataTests/src/Editor/EditorExportTests.cpp:167-864`, `WorldGameExportTests.cpp`) for How it is tested |
| `assets:177`, `assets:179` | feature | use | Pack planning and cooked documents, as the asset inventory lists them |
| `build-test:123` | feature | use | The export chain's CTests |
| `editor-ui:217` | feature | link | The Export Game dialog as the editor-ui inventory lists it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The cook and the physics room it records | `worlds/physics-scripts` | must |
| Asset packs: format, planning, pruning, `AlwaysInclude`, patches, cooked documents | `assets/packs-export` | must |
| Projects and settings sections, and their validation | `world/projects-settings` | must |
| Files you can trust: paths, atomic writes | `core/files` | must |
| Jobs on I/O threads and what stays on the main thread | `core/jobs` | must |
| Atomics and a mutex shared by two threads | `basics/threads` | must |
| Background imports and when they are done | `assets/importing` | must |
| Reference searches of documents | `assets/references` | helps |
| Saves off the main thread (`DocumentSaver`) and saves in flight | `editor/saving` | helps |
| The editor's core and its context (`EditorContext`) | `editor/program` | helps |
| Building scripts from the editor, and the loaded module | `editor/script-builds` | helps |
| Shared libraries and their debug symbols | `scripting/shared-libraries` | helps |
| Commands are the API (`project.export`) | `editor/commands` | helps |
| Exceptions of third-party code caught at the call site | `core/conventions` | helps |
| Running a command from a terminal | `start/how-to-read` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
