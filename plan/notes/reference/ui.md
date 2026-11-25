# Notes: reference/ui

## New terms

None.

## Requests

- Names or words: none outstanding.
- Generator routes (planner): `tools/reference.py` at this commit has no routes for the UI enums, callbacks, events, limits or `GameUISceneStats`, and `tools/reference-limits.json` lists no GameUI constant. The page writes these tables by hand; each could become an `::include` once a route exists.
- `src/sidebar.json`: not touched.

## Hand-written tables

- Conventions (`GameUIComponents.h`, the comment at its top and the field comments; `GameUIRenderer`-independent).
- The enums: `Strata/src/Strata/GameUI/GameUIComponents.h` (all eleven enums; values without a comment are described from `GameUIQuads.cpp` and the component comments).
- Events and callbacks: `Strata/src/Strata/Scene/SceneServices.h` (`UIEventType`, `UIEventInfo`, `IUIEvents`), `StrataScriptCore/Include/StrataScript/ScriptABI.h` and `Script.h` (callbacks).
- `IUIControl` functions: `Strata/src/Strata/Scene/SceneServices.h`.
- The UI action map: `Strata/src/Strata/Input/UIActions.h`.
- Limits: `GameUIScene.h`, `GameUIRenderData.h`, `GameUIQuads.cpp`.
- `GameUISceneStats` and the two stages: `GameUIScene.h`, `GameUIRenderer.cpp`.

## Not verified

- The scale of 4/3 and 1 on a 2560 by 1080 screen follows from the comment of `MatchWidthOrHeight` (0 scales with the width, 1 with the height), not from running the code.
- The CPU stage `Render.UI` is described from the two `ST_PROFILE_STAGE` scopes (preparation and `DrawRuns`).
- That a canvas size change under `ScaleWithScreen` at the same aspect ratio reuses a layout is from the comment of `GameUIScene.h`.

## Pin move to v0.8.0

- Rechecked at `319075e3` row by row: the eleven enums and their defaults, the conventions, `UIEventType` and the four callbacks (`ScriptABI.h`, `Script.h`), `IUIEvents` and `IUIControl`, the UI map's bindings (now read from `MakeDefaultUIActions` in `Strata/src/Strata/Input/InputActionSet.cpp`) and repeat times, the four limits, `GameUISceneStats` and the stages `Render.UI` and `GPU.UI`. No GameUI, `SceneServices.h`, `UIActions.h` or script header line changed between `822a7a46` and `319075e3`; the page needed no change.
- Linked pages `reference/commands`, `reference/components`, `reference/performance`, `reference/script-api` and `reference/audio-input` exist and still hold the `ui.*` commands, the eleven UI components and the `Perf.GameUI` and `PerfGPU.GameUI` suites.

## Findings not applied

- critic-reference-2 (introductions name the teaching page): applied.
- critic-reference-12 (`IUIControl` beside `IUIEvents`): applied by hand as a table of functions.

## Clerk

- Left for the planner: the generator routes for the hand-written tables.
