# Notes: worlds/runtime

## New terms

- Composition root: the one place that decides which parts of the engine a program contains. Home: worlds/runtime. (Marked by markterms as `composition-root`, so it may be homed elsewhere already.)

## Requests

- Figures not drawn or taken: the "No camera to show" frame of a scene without a primary camera, the exported Open World loading scene with its progress bar, and a perf-log chart of an Open World drive with the World and Physics columns. Only `open-world-exported` is in `src/content/figures/worlds/runtime.json`.
- Further reading entries are cited without links (Gaffer On Games, Game Programming Patterns): hosts gafferongames.com and gameprogrammingpatterns.com, if not already allowed.

## Not verified

- That an export fills the version resource with the game's name (the page says only "a version resource").
- The perf-log row example uses invented numbers and says so.
- The 30 ms preparation in the scene-switch example is an assumption, stated as such.
- Window requests of a script reach `GameWindowService` through `IGameWindow`; the SDK side (`Game.h`) was not read.

## Since

0.3.0: Docs/Releases/0.3.0.md lines 85-88 name StrataRuntime, the loading scene, `--frames`, `--perf-log`.

## Findings not applied

- The brief's figures worlds-runtime:404 (no-camera frame), :403 (loading scene shot), :408 (perf-log chart): not drawn or captured here (see Requests).
- Exercise worlds-runtime:481 (compare `--quality low` and `ultra` with a perf log) and the `--mute` tests of gamedev:559 are folded into exercises 1 and 4 in shortened form; no `--quality` comparison exercise.
- The inventory-based `Runtime.*` test list is given by suite, not by every test.

## Clerk

- Refused composition root: the glossary homes it on core/layers-registries (only its home words it); its bold here may stay as a plain use.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `open-world-exported` (kind runtime): taken at the pin v0.8.0 in one round (export of the Open World copy, 1280x720, high quality, 10 s) and published. The frame shows the start scene's tour over the forest beside a dark hill, the clock and the controls line; caption, alt and shows rewritten to say so, and the sentence before the figure now introduces it.
