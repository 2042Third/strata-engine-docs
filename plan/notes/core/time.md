# Notes: `core/time`

## New terms

- **backlog**: the whole steps that are still due when the cap stops a frame's loop; Strata drops them and keeps one step in the accumulator. Home: `core/time`. Aliases: none. (The page defines it in bold in "A cap stops a long frame from owing too much"; its word-list finding stays until the term exists.)

## Requests

- `tools/data/extra-words.txt`: "extrapolate" (two uses in "Drawing between steps hides the step's rhythm" and "What Strata's choice cannot do"). The brief's Covers names "interpolate or extrapolate"; the page avoids "interpolate" (it writes "interpolation") but keeps "extrapolate". The word-list finding is left until the word is added.
- Hosts: none new; the further reading links only `gafferongames.com`, `gameprogrammingpatterns.com`, `docs.unity3d.com` and `docs.godotengine.org`, which are on the list.

## Since

`since: 0.3.0`. At `v0.3.0` the scene already had `FixedTimestep` and `MaxFixedStepsPerFrame` in `Strata/src/Strata/Scene/Scene.h`, `Scene::SetTimeDilation`, and the script callbacks `OnUpdate`, `OnFixedUpdate` and `OnLateUpdate` (`StrataScriptCore/Include/StrataScript/Script.h` lines 33 to 35). The unscaled time came in `v0.5.0` (`Scene::GetUnscaledDeltaTime` is in its `Scene.h`); the project's `Scene.Timing` section is newer (0.8.0).

## Not verified

- The comparison with other engines (the table's "Used by" column, "Unity calls its cap the maximum allowed timestep", "Godot calls its cap the maximum physics steps per frame", Fiedler's "semi-fixed step", loops locked to the display on consoles) comes from general knowledge. The four Further reading URLs were not opened.
- Exercise 3 (Physics Playground at `FixedRate` 30 and 240) was not run in the editor: its prediction follows the field's description in `Strata/src/Strata/Scene/ProjectSceneTiming.cpp` (soft contacts at 30, four times the steps of 60 at 240). That the first sample station is the crate tower is not checked; the README says only that the keys 1 to 6 fly to the stations.
- Exercise 2 (frame caps 60 and 240 through the editor's `Editor.FrameRate` preference) was not run. The preference's own description says a cap above the display's refresh rate shows nothing more, and the answer says so.
- The sketches are toys: they model the accumulator, the cap, the backlog and time dilation of `Scene::OnUpdateRuntime` in whole milliseconds, not the engine's `float` seconds. The step-cost numbers (20 ms of game time for 30 ms of work) are an invented example, as the page says.
- The stability limit of about 33 ms for the spring (a step shorter than 2 divided by the spring's rate of 60 per second) is the textbook limit of the semi-implicit Euler step, not something taken from the engine.

## Findings not applied

- The brief lists no open findings.
- `foundation:406` and `scene-ecs:436` ask for the figure to show the interpolation's alpha and the case of time dilation; the figure `accumulator-timeline` shows uneven frames, the steps that fall out, the cap's dropped steps and the kept step. The alpha (one step behind the clock) is told in the text only, and time dilation is told in a table.
- The `:::rule` box of `editor-core:580` (R31) is not placed: the `:::why` aside carries the rule, with the editor's exception linked to `editor/stepping`.
- The entry "timestep" of `foundation:571` is not defined here: the glossary homes it elsewhere, and the page uses "delta time" for the frame's time.
- `GameRuntime`'s `KeepEveryFixedStep` and the runtime's `--frames` and `--seconds` are left to `worlds/runtime`, as the brief says; the page mentions only that scripted runs keep time dilation off.
- The old sample page's figure `interpolation-off-on` (a live capture, tier 3) and its two images under `src/assets/figures/core/time/` are removed: `world/interpolation` owns the interpolation picture.

## Clerk

- Admitted: backlog.
- "extrapolate" is an alias of the term extrapolation, homed on `world/interpolation` (asked by both pages), so it passes `word-list` as a glossary word (R54); no extra word.

## Track walk E-final-6

Checks in `docs-work/walkfix-E6`, 2026-11-24, with the official 0.8.0 package and the pin clone's `build/docs-patch`, under the perf lock; no editor left running, the clone clean afterwards.

- WK2: both statements were true of different marks, and the first called the clock "the simulation". At the pin the
  drawn moment is T + a - h for the newest step T and the accumulator a (`Scene.cpp:2316-2320`): one step behind the
  clock, and h - a behind the newest step, half a step on average. Both sections and exercise 3's answer (which said
  "halves"; 17 ms at 30, 2 ms at 240) now count it the same way.
- WK4: the Frame Rate preferences apply only to an editor with a window ("headless, --frames and command-script runs
  ignore it", `StrataEditor/src/Editor/EditorFrameRate.cpp`), default Active frame rate Unlimited. Exercise 2 now asks
  for the prediction first and says that its check needs the windowed editor, has no command, and how to restore it.
- WK5: exercise 3 now has an editor tab (Physics category, Timing page) and a command tab. Run with the package on a
  copy made by `project.openSample` (`timing.ps1`, `timing.txt`): the page's pipe line answers `FixedRate` "30",
  `isDefault` false; `scene.info` gives `source` project, 30 steps, cap 4 (240: 32); 60 frames of play gave 34 and 259
  fixed steps, mean frame time 2.7 ms and 7.7 ms; `"reset": true` gives `Scene`; the number 30 fails with
  `'FixedRate' must be one of 'Scene', '30', '60', '120', '240'`.
- WK1: a paragraph after the introduction names what the page uses.
