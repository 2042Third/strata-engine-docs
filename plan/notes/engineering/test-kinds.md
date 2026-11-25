# Notes: engineering/test-kinds

## New terms

None proposed. The page defines `flicker-meter` (homed here) in bold and marks the other terms through the closure.

## Requests

- Figure `smoke-viewport` (kind tool, taken by the owner): the capture `SmokeViewport.png` that `StrataEditor.Smoke` writes; no recipe replays the test's own script.
- No new names, extra words or hosts. The page links no external host in its text; Further reading cites cmake.org, registry.khronos.org and gafferongames.com, all on the host list.

## Since

0.3.0: the GPU context, end-to-end suites and package tests exist from the first tags of the test program; the Tetris sample test is from 0.3.0 (inventory gamedev:229).

## Not verified

- How the editor picks its port (the page says only that the test reads it from the session).
- That the eye notices block-level change most (explanatory remark about the block statistics).
- The pairing of CPU and GPU suites in the light table follows the suite names and their test files, not a stated design rule.
- `ctest --preset windows-debug -L gpu` and `-R` forms follow AGENTS.md's examples and were not run.

## Findings not applied

The brief lists no open findings. `StrataEditor.Replay`, `LauncherSmoke` and `Icon` checks are not described (the page names the smoke, quit and failing scripts only).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `smoke-viewport` (kind tool) keeps its `waitsFor` as the request for a later edition: only the smoke test's own run
  writes `SmokeViewport.png`. Its stand-in `smoke-scene` (kind scene, 2026-11-24, pin 319075e3) runs the script's five
  `entity.create` steps in an empty project (the crate's 30 degree turn written into its Transform instead of the
  script's `component.set`) and captures 960 by 540 with overlays on, from a camera of the recipe's own (the script's
  `camera.focus` and `camera.set` framing is not replayed). One round: the crate renders almost white on every face,
  as the script's lights make it; the floor, grid and axis lines show. The page's lead-in says the picture is the same
  scene captured by the book's tool, not the test's file.
