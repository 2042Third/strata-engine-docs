# Brief: `make/export`

| Field | Value |
| --- | --- |
| Title | Exporting and shipping |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/project-files`, `make/hud` |
| From | gamedev "Exporting and shipping" (§1.18, concept 24); worlds-runtime "Shipping a Game: the Export" (use side; hands-on 7, 9); "Giving your game to players": a credits screen, the notices file, SmartScreen, quarantine, the `.desktop` file in a hidden folder; one sentence that an exported streamed world waits for its ground, which `make/large-worlds` checks; use home of the export; Coin Run exported and run |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/export` — Exporting and shipping

**Covers.** The page exports Coin Run and runs it as a player would, and is the use home of the export. The idea
first, in one paragraph and the export figure: an export writes a folder that plays without the editor: the runtime
renamed after the game, the game's manifest (`.stgame`), one pack of its assets (`.stpak`) in the order the game first
uses them, the script module, the icon and, on Linux, a desktop entry. The steps. (1) The game's identity on **File ▸
Project Settings ▸ Game**: title, version, company, copyright and an icon (an image from the book's tutorial assets);
a script cannot read the title or the version (`new:44`); the start scene is `Scenes/Main.stscene` since Basic 3D set
it (**File ▸ Set as Start Scene**), and a loading scene is named in one sentence, with `make/levels-saves`, which
teaches it. (2) **File ▸ Export Game...**: a folder outside the project; the stages in the progress bar
(waiting for imports, cooking worlds, packing, copying) and **Open Folder** at the end. (3) The export refuses when a
build is running, when the scripts are not built or changed since they were loaded, or when the folder is inside the
project: one refusal shown by exporting while a build runs. (4) The folder in the file browser: each file named, and
the shipped `ThirdPartyNotices.md`. (5) Run the game by double-clicking it, with what each system asks first (tabs per
OS: Windows SmartScreen's **More info ▸ Run anyway** for an unsigned program; macOS's quarantine removed with `xattr
-dr com.apple.quarantine <folder>` in the terminal; on Linux the `.desktop` file copied into the hidden folder
`~/.local/share/applications` to list the game, with a caution: the export writes the entry but does not install it,
and the entry names the export folder's absolute paths, so a moved or shipped folder needs its `Exec` and `Icon`
lines edited). (6) Run it from the terminal with options: `--windowed`,
`--resolution 1280x720`, `--seconds 10 --screenshot shot.png`, `--headless --frames 600`, `--quality low` and `--help`,
with the exit codes (on Windows the output piped to `Write-Output` so PowerShell waits). (7) The game's log and save
folders in the player's data folder, named after the game; `Game.log` read for a script's warning. (8) A pruned
export: tick **Prune** and run it: no coins appear, because `CoinPlacer` loads the coin prefab and the `Coin` script its
sound by path, and a pruned pack keeps only what the scenes use; add them under **Project Settings ▸ Export ▸ Always
Include** and export again. (9) What the exported game does differently: no hot reload, scripts switched off after a
crash, project settings and graphics options as the game reads them. "Giving your game to players": a credits screen
built from `CREDITS.md`, the notices file kept beside the game, one sentence that an exported streamed world waits
for its ground, which `make/large-worlds` checks, and one sentence on the processor: on Windows and Linux on x86-64 the
game needs a processor with AVX2, and nothing checks it at start, so an older processor stops without a message
(`new:46`). What Strata does not do here: exports for another platform, macOS app bundles, signed exports, crash
reports from shipped games (`new:11`); a tool that writes patch packs (`new:45`); a check at startup for AVX2
(`new:46`). The exercises (`new:47`) run the exported game from the terminal. At the end the reader has Coin Run as a
folder that plays without the editor, and knows what to check before giving it away.

**Leaves out.**

- The export as a whole inside: `GameExport`, its states, its checks → `worlds/export`
- The pack: format, planning, pruning → `assets/packs-export`
- The manifest and the game's identity inside → `worlds/game-identity`
- The runtime, its options and exit codes inside → `worlds/runtime`
- The Export dialog's drawing → `editor-ui/launcher-dialogs`
- Measuring a shipped run with `--perf-log` → `make/performance`
- Players' graphics options → `make/quality`
- A loading scene with a progress bar → `make/levels-saves`
- Exported streamed worlds → `make/large-worlds`
- The terminal, paths and exit codes → `basics/tools`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `over`: about 4,250 words against M (3,000). Nine steps, three of them with OS tabs, the runtime's options and
exit codes, the export taught from zero with its figure, "Giving your game to players", four pictures, the three
absences and two exercises take it over M's top. L (5,000) by S2: shrinking step 6's options to a table would cut
content (S4).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:206` | feature | home | The game's identity: title, version, company, copyright, icon; stamped into the Windows program, the macOS Dock icon, the Linux entry |
| `gamedev:236` | feature | home | **File ▸ Export Game...**: its stages, what the folder holds |
| `gamedev:237` | feature | home | Pruned exports and **Always Include** |
| `gamedev:238` | feature | home | The export's refusals |
| `gamedev:239` | feature | home | The runtime's options and exit codes |
| `gamedev:240` | feature | home | What `GameRuntime` does differently from the editor |
| `gamedev:348` | concept | home | Shipping: what an export holds, pruning and assets loaded by path, identity, unsigned programs; the mistake of a pruned export that misses what scripts load |
| `gamedev:429` | figure | home | The export's stages and the folder it writes, pruned against full |
| `gamedev:454` | figure | home | The Export dialog with its progress; the exported folder with the icon |
| `gamedev:475` | figure | home | Coin Run running in a window with its title in the bar |
| `gamedev:511` | rule | home | Pruned exports drop assets loaded by path; list them under Always Include |
| `gamedev:512` | rule | home | The export refuses while a build runs, when the module changed since load, or when scripts are unbuilt |
| `gamedev:577` | term | home | Start scene and loading scene: the start scene's entry is taught here; the loading scene's entry is `make/levels-saves`', which teaches it (`gamedev:202`), and the glossary step splits the two |
| `gamedev:651` | term | home | Export, pruned export, always include |
| `gamedev:652` | term | home | Manifest (`.stgame`) and pack (`.stpak`) |
| `gamedev:653` | term | home | Headless |
| `gamedev:654` | term | home | Game identity |
| `new:11` | not-done | home | Exports for another platform, macOS app bundles, signed exports, crash reports in shipped games: the export copies the runtime next to the editor. Evidence: `Docs/Releases/0.7.0.md:411-412`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1684-1685` (run at the pin) |
| `new:12` | erratum | home | `.claude/skills/strata-make-a-game/SKILL.md:470`, which `make/project-coin-run` reads, says an exported game has no `--help` and ignores unknown arguments; at the pin it prints its usage for `--help` or `-h` and exits 0, and a command line it does not understand prints the problem and the usage and ends with the usage exit code (3). The page states the code's facts; `process.md`'s table of errata holds the row. Evidence: `StrataRuntime/src/RuntimeApplication.cpp:354`, `:372-375`, `:409`, `:429-440`; `Strata/src/Strata/Core/CommandLineOptions.h:27` (`c_UsageExitCode = 3`) (read at the pin) |
| `new:44` | not-done | home | Reading the game's title or version from a script. Evidence: `Docs/Releases/0.7.0.md:363`; `git grep -ni -e title -e gameinfo 822a7a46 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46`, `:125`; `ScriptABI.h:289`, `:299`) (run at the pin) |
| `new:45` | not-done | home | A tool that writes patch packs: the export writes none, and a patch is a pack written from code and named in the manifest's `PatchPacks` by hand. Evidence: `git grep -n PatchPacks 822a7a46 -- StrataEditor StrataCLI Tools` finds nothing (run at the pin); `Strata/src/Strata/Project/GameManifest.h:26`, `:51-53` |
| `new:46` | not-done | home | A check at startup for the processor's AVX2: the release builds compile every engine object for AVX2 on x86-64, so an older processor stops at an illegal instruction without a message; the one sentence of "Giving your game to players" says what processor the game needs (critic-build-test-5). Evidence: `CMake/StrataCompilerOptions.cmake:30`, `:50-51`, `:61-62`; the only processor check in `Strata/src` is `Strata/src/Strata/Core/Hash.cpp:109-119` (SSE 4.2, for CRC32; `git grep -ni cpuid 822a7a46 -- Strata/src StrataRuntime/src StrataEditor/src` finds only that file) (run at the pin) |
| `new:47` | hands-on | home | Exercises, run from the terminal: **Basic.** run the exported game with `--windowed --resolution 800x600 --seconds 5 --screenshot shot.png` and open the picture; **Medium.** predict the exit code of the game run with an option it does not know (`--speed 2`) and with `--help`, then run both and read the code (`$?`, or `$LASTEXITCODE` in PowerShell). Evidence: `StrataRuntime/src/RuntimeApplication.cpp:354`, `:409`, `:429-440`; `Strata/src/Strata/Core/CommandLineOptions.h:27` (`c_UsageExitCode = 3`) |
| `build-test:601` | hands-on | home | Step 6: the exported game checked headless (`--headless --frames`), with a windowed `--screenshot`; `--perf-log` named for `make/performance` |
| `worlds-runtime:125` | feature | use | The runtime's options, at the maker's level |
| `worlds-runtime:146` | feature | use | The `.stgame` manifest |
| `worlds-runtime:149` | feature | use | The save and log folders named after the game |
| `worlds-runtime:155-156` | feature | use | The export and its checks before it starts |
| `worlds-runtime:159-160` | feature | use | The asset pack and pruning |
| `worlds-runtime:162-166` | feature | use | The script module, the icon, the Windows version resources, the Linux entry, the macOS Dock icon; step 5's Linux caution: the export does not install the entry, and the entry names the folder's absolute paths. Evidence: `StrataEditor/src/Editor/DesktopEntry.h:11-13`, `:20-21`; `StrataEditor/src/Editor/GameExport.cpp:714-720` (read at the pin) |
| `worlds-runtime:168` | feature | use | The Export dialog |
| `worlds-runtime:292` | concept | use | Game identity and the platforms, at the maker's level |
| `worlds-runtime:374` | figure | use | The exported game's folder |
| `worlds-runtime:400-401` | figure | use | The Export dialog before, during and after; the folder in the file browser |
| `worlds-runtime:407` | figure | use | Project Settings ▸ Game |
| `worlds-runtime:448` | rule | use | Saves are keyed by the manifest's name, not the title |
| `worlds-runtime:479` | hands-on | use | Export and ship: identity, export, run, the log and save folders |
| `worlds-runtime:483` | hands-on | use | Prune safely: step 8 |
| `assets:626` | hands-on | use | Export pruned with Always Include, the same exercise as `worlds-runtime:483` |
| `assets:725` | term | use | Pruning and `AlwaysInclude` |
| `scene-ecs:214-216` | feature | use | The export settings, the game's info and the manifest in the project |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Project Settings, the project folder and paths as text | `make/project-files` | must |
| Coin Run's scripts that load assets by path | `make/scripting-scene` | must |
| The HUD and the finished level | `make/hud` | must |
| Opening a terminal, changing folder and running a program with options | `start/install` | must |
| Exit codes and the standard streams | `basics/tools` | helps |

**Starting state.** The end state of `make/play-test-debug` (`startsFrom {"tutorial": "make/play-test-debug"}`): Coin
Run with its HUD, its sounds and the bug fixed. The icon is an image of `tutorials/assets/` with its credit. The page
ends with Coin Run exported (full, then pruned with **Always Include**) into a folder outside the project; the runner's
check of the exported game is a headless run of the folder.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `export` | export (use) | - |
| `always-include` | always include | - |
| `manifest` | Manifest | .stgame |
| `pack` | pack | - |
| `pruned-export` | pruned export | - |
| `headless` | Headless (use) | - |
| `game-identity` | Game identity (use) | - |
| `loading-scene` | Loading scene (use) | - |
| `start-scene` | Start scene (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-16 | should | stale-item | `make/lighting` (step 7), `make/physics` (steps 1, 7 and 8), `make/input` (step 4), `make/export` (step 8) | Labels the steps name differ at the pin. The sun's softness is **Angular Diameter** in the Inspector (stored as `ShadowSoftness`); the component is **Rigid Body**; the export's pruning box reads **Leave out unused assets**, not Prune; and Project Settings lists its pages under Physics (Collision Layers, Simulation, Timing), Input (Input Actions) and Rendering (Graphics Quality). | The steps use the pin's labels and paths (**Project Settings ▸ Physics ▸ Collision Layers**); `make/lighting` keeps "the sun's size" as the meaning of Angular Diameter (no words added). | `allocation/make-a.md:718`, `:1261-1262`, `:1280`, `:1148`, `:1707`; `StrataTests/Architecture/ComponentSchema.json:480`, `:2173`; `StrataEditor/src/UI/ExportDialog.cpp:311`; `Strata/src/Strata/Scene/ProjectCollisionLayers.cpp:59-60`; `Strata/src/Strata/Physics/PhysicsSimulationSettings.cpp:55-56`; `Strata/src/Strata/Scene/ProjectSceneTiming.cpp:78-80`; `Strata/src/Strata/Input/InputActionSet.cpp:627-628`; `Strata/src/Strata/Renderer/RendererQuality.cpp:712-713` |
| critic-make-a-27 | could | thin-home | `make/export` (step 2) | Step 2 names only the folder and the progress. The Export dialog also holds the window size, **Fullscreen** (off), **Copy the runtime**, **Copy the script symbols** (the module's PDB, so that a crash in a shipped script can be debugged) and a link to the game's identity in Project Settings; the reader meets each before pressing Export. | Step 2 names each field in a sentence, with what Coin Run leaves as it is (about 70 words). | `allocation/make-a.md:1694-1695`; `StrataEditor/src/UI/ExportDialog.cpp:280-312`, `:358`; `StrataEditor/src/Editor/GameExport.h:41` |
| critic-make-a-28 | could | thin-home | `make/export` (step 8), `make/project-coin-run` (step 7) | Step 8 names two assets that scripts load by path, the coin prefab and the coin sound. The bump of `make/sound` step 5, when its script finds the clip by path, and the complete sound of `make/project-coin-run` step 2 drop out of a pruned export the same way, and no page says how the reader finds what is missing: `Game.log` holds a warning "FindAsset (called by script ...): there is no asset at '<path>'" for each. | Step 8 lists every path that Coin Run's scripts find (or adds the folder `Sounds`, since Always Include takes folders) and reads that warning in its "If you do not see it"; `make/project-coin-run` step 7 adds `Complete.ogg` (about 50 words). | `allocation/make-a.md:1421-1423`, `:1707-1709`, `:1808-1809`, `:1815-1816`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:912-914`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:1546`, `:1555`; `StrataEditor/src/UI/SettingsPages.cpp:348-349` |
