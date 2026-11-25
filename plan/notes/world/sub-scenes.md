# Notes: `world/sub-scenes`

## New terms

None proposed. The page defines in bold the glossary's own terms homed here: additive load, slice, work budget,
prepared scene, sub-scene, prepared start, `SceneWorkBudget` (as "scene work budget"), chunk. "Prepared state" (the
typed per-scene slot) and "pin" are used in plain words, not defined as terms.

## Requests

- Host for Further reading, cited without a link: `dev.epicgames.com` (Unreal Engine documentation, "Level
  Streaming" and sublevels). `docs.unity3d.com` is already allowed; the page names it in the entry without a link.
- Tool gap: the glossary entries `subscenecomponent` (term written in backticks) and `sub-scene-additive-load` (the
  qualified name "Sub-scene (additive load)", which shares its base name "sub-scene" with the entry `sub-scene`) can
  never be satisfied by a bold definition: `term-defined` reports "never uses it" for both. The page defines
  **`SubSceneComponent`** and **sub-scene** in bold as the card asks. The same finding stands on `core/conventions`
  for `ST_CORE_ASSERT`. The planner may merge `sub-scene-additive-load` into `sub-scene` and let the matcher read
  code-named terms.
- `tools/data/names.txt`, `extra-words.txt`: nothing; every word of the page is listed.

## Since

`since: 0.3.0`: `Docs/Releases/0.3.0.md` (line 82) says scenes load in the background and additive sub-scenes come
in slices of entities per frame; `Docs/Releases/0.4.0.md` (line 186) adds unloads in slices and cancelling.

## Not verified

- The figure `load-status` was not taken: the recipe plays the ThirdPerson sample, loads its `Scenes/Loading.stscene`
  into the running scene with `scene.loadAdditive` and keeps `/subScenes` of `scene.loadStatus`; that this scene loads
  additively without an ID collision with the Course scene was not run (no engine program was started).
- The statements about Unity (additive scene loading) and Unreal Engine (level streaming, sublevels) come from public
  documentation as I know it; no page was fetched.
- The Unity address of the scripting reference is cited by host only; no page was fetched.
- The "Who uses it" column of the alternatives table (tools and small games, frame loops) is general knowledge, not
  checked against any engine.
- The frame-by-frame example of a level switch (frames 1 to 91) is an invented illustration with round numbers, not a
  measurement.
- The cost of 2 microseconds per entity in the problem section is the engine's own starting estimate (2,000 ns in
  `Scene.h`), used as an illustration, not measured.
- The toy's output comes from a compiled run of the sketch (a simulated clock); the 20,000-entity example is computed
  by hand from `FitChunk` and `RecordChunkCost` and matches the toy's frames 3 and 4 (1,356 and 1,361 entities).

## Findings not applied

The brief lists no open findings. Left out by the brief and by this page's budget:

- A section "What went wrong before": the history holds no bug with a named regression test that this page could
  verify at the pin.
- The skipped assets of a load (`GetSkippedAssetCount`) and the pool fitting: `assets/references` by the brief.
- Loading screens, `GameRuntime`'s switch and the editor's play mode: their own pages by the brief; the page names
  the owners' calls only.

## Clerk

- Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm).
- Tool: a bold code span of an entry's code name now defines it (**`SubSceneComponent`**).
- Left for the planner: "Sub-scene (additive load)" beside "sub-scene" on this page: the lint now matches the qualified entry only by its whole name (as "Luminance (Y)" on `basics/color`), so the page must write it whole or the planner merges the two entries.
- The mender: "Sub-scene (additive load)" (gamedev:648, scene-ecs:676) and "Sub-scene / additive load"
  (worlds-runtime:527) are one meaning, the sub-scene: `merge.py`'s SPLITS join the three lines into "Sub-scene", and
  `admitted.json` gives "Sub-scene" and "additive load" this page's wordings (the inventory's half line "a loaded cell
  is one" defined nothing).

## Figures

- `load-status` (text, round 1, published): ThirdPerson, `play.start` then `scene.loadAdditive` of
  `Scenes/Loading.stscene`; `scene.loadStatus` kept to `/subScenes` shows one entry, `Loaded`, progress 1.0, 7 of 7
  entities created, none skipped, 1 slice, error null. The alt now names those values; caption and page hold.
- `load-status` (text, v0.8.0 pin 319075e3, round 1): the same recipe taken again gives a text byte for byte equal to
  the one published at 822a7a46 (same handle `43FD467DF4593C28`, 7 of 7 entities, 1 slice). `publish` leaves it
  unchanged; `taken.json` records the new pin under `checkedAt`, as `publish` does for a picture that matches.

## Walk E-final-9

Track walk E-final-9 (2026-11-24; `docs-work/walkfix-E9`, `measure2.py` to `measure4.py` and `pagelines.ps1`, the
official 0.8.0 package, `--no-gpu`). In a new copy of `ThirdPerson`, `play.start` built the scripts (17 to 18 s, reason
"the project's scripts are not built yet"), `scene.loadAdditive` of `Scenes/Loading.stscene` and `scene.loadStatus`
gave the capture's entry exactly (sub-scene 1, 7 of 7, 1 slice). The walker's run in `OpenWorld` (a world) gave
sub-scene 9 and the eight loaded cells in `subScenes`, which the page now says.

## Engine

- Not reproduced, for the record: in the first measuring run, one long editor session (OpenWorld, then a prefab
  scene, `project.setSettings`, then `project.openSample` of ThirdPerson with `force`), `play.start` answered "The
  connection failed during 'play.start'" and the editor was gone. Three fresh sessions (with and without a separate
  `script.build`, and with the project switch) played normally. No crash report was kept; the page says nothing of it.
