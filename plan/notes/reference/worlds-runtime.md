# Notes: reference/worlds-runtime

## New terms

None proposed.

## Requests

- Layout, names and words: none. The lint reports size against the outline row (known fault of the tool for reference pages).
- The links `../reference/commands.md`, `../reference/script-api.md`, `../reference/settings.md`, `../reference/editor.md`, `../scripting/host-api.md` and `../make/performance.md` point to pages other writers create.

## Hand-written tables

- World document, layer, cell and index keys; world limits (cells are :value keys of limits.* in values.json): `Strata/src/Strata/World/WorldAsset.cpp`, `WorldAsset.h`, `WorldGrid.h`.
- Project file keys: `Strata/src/Strata/Project/Project.cpp`, `Project.h`, `GameInfo.h` (critic-reference-1 applied).
- Manifest keys and versions 1 to 5: `Strata/src/Strata/Project/GameManifest.cpp`, `GameManifest.h` (version steps from the header comment and the `LoadingScene` "version 4" comment).
- Players' files: `Strata/src/Strata/Runtime/GameGraphicsService.cpp` and `.h`, `Strata/src/Strata/Input/InputActionSet.h`.
- Engine services and `IWorldStreaming`: `Strata/src/Strata/Core/EngineServices.h`, `Strata/src/Strata/Scene/SceneServices.h` (critic-reference-12).
- Exit codes: `StrataRuntime/src/RuntimeApplication.cpp`, `Strata/src/Strata/Core/CommandLineOptions.h`, `Strata/src/Strata/Core/Application.h` (critic-reference-10).
- Perf log unit suffixes: column names in `FramePerfLog.cpp`, `GameRuntime.cpp`.
- Commands list and `world.create` defaults: `StrataEditor/src/Editor/EditorWorldCommands.cpp` (inventory), generated command files.
- Exported folder: `StrataEditor/src/Editor/GameExport.cpp`, `GameExport.h`.

## Not verified

- That the cell's square starts at `GridOrigin` plus `X` times `CellSize` (read from the header comment of GridOrigin, not WorldGrid.cpp).
- `world.create` defaults (four layers, 64 m, four cells) come from the inventory, not read in the command's code.
- The `<File>.desktop` and the Windows resource stamp were read in the code, not run.
- The dropped graphics fields: not checked whether a log line is written.

## Findings not applied

- critic-reference-2: applied (each introduction names a teaching page).
- critic-reference-7: belongs to `reference/editor`; this page links it.

## Clerk

- Tool: the lint's size rule no longer fires on a kind R page (R37).
