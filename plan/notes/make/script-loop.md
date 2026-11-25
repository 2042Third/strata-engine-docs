# Notes: make/script-loop

## New terms

None proposed. The page defines fixed update, callback, accumulator, fixed step, time dilation and time scale as the brief lists them; it also defines frame, delta time, physics, cap and sine in passing (common words or defined in bold without a glossary home).

## Since

0.3.0: the fixed step, time dilation, the lifecycle callbacks and `Time` exist since 0.3.0 per `gamedev:126`, `gamedev:158`; the Timing page (FixedRate) is wave 8 but the page's concept is the loop.

## Requests

- Figures: none (two Mermaid diagrams: the frame timeline and the lifecycle state machine). The brief's accumulator at 30, 60 and 144 Hz is a table.
- Sketches `make-script-loop-accumulator.cpp` and `make-script-loop-rate.cpp` (exercise 3).
- Tutorial `tutorials/make/script-loop/exercise-2.tutorial.json` (sets `Scene.Timing` with `project.setSettings`; the value shape `{"FixedRate": "120"}` and the `expect` pointer `/value/FixedRate` were confirmed by the tutorial run).
- The page links pages that do not exist yet: `make/physics`, `make/menus`, `make/timers-events`, `make/scripting-scene`, `make/characters-cameras`, `core/time`, `world/interpolation`, `scripting/script-system`, `appendix/not-in-strata`.
- The brief says the `Coin` script is taught on `make/first-script`; that page has the `Spinner` script on a cube. The page cites it as the cube and calls the bobbing coin "the coin of the Coin Run game".

## Not verified

- The exact menu path to open Project Settings (the page names the category **Physics** and page **Timing** from the registered section's title and category).
- Whether the editor's Play mode enables time dilation in every session (`EditorContext.h` says interactive and automation sessions; the runtime enables it unless a run ends by itself).

## Findings not applied

- critic-make-a-13 names `make/project-coin-run` and `make/timers-events`, not this page; the page only teaches `Time::SetTimeScale(0)` as the brief asks (a negative or non-finite value is rejected, at 0 game time stops).
- critic-make-a-17 applied: interpolation is on by default (Timing ▸ Interpolation); a script reads the simulated position, a camera the drawn one.

## Clerk

- No term or word asked.
- Left for the planner: the sketches, exercise 2's settings shape, the links to unwritten pages, the brief's Coin script.

## Tutorial run

- Round 1 (2026-11-18): exercise 2 passed. The file was thinner than the answer (it checked only the stored value); it now also checks with `scene.info` that the scene runs the project's step (`settings.fixedRate`: source project, 120 steps each second, 1/120 s, cap 16), and the answer says so.
- Round 1 at the pin 319075e3 (v0.8.0, 2026-11-23): exercise 2 passed as written; the 0.8.0 Timing page (Fixed Rate 120, cap 16) answers as before. The solution download `exercise-2.zip`, left out of the earlier commit, goes in with the stamp.
- 2026-11-24, track G walk segment 5 (WK2): exercise 2 ends by resetting `Scene.Timing` with `project.setSettings`
  `reset: true` and checks with `scene.info` that the scene's own step (60, cap 8) applies again; the answer says to
  choose **Scene** afterwards. Passed with the pin build and the 0.8.0 package.
