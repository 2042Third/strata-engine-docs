# Notes: make/project-tetris

## New terms

- rules (of a game): what the game is: where a piece may go, when a row is full, how many points a row gives; home this page.
- rotation box: the square a piece's four cells sit in, which a quarter turn works inside; home this page.
- kick: a small shift a game tries when a turned piece does not fit; home this page.
- canvas: a UI entity that the engine draws over the game in screen space, holding UI elements (only if the glossary lacks it: `make/hud` homes the HUD canvas).

## Since

0.3.0: the sample, KeyRepeat, the HUD canvas, `input.sequence` and export are all in the first-tag manual and the pin's sample.

## Requests

- Layout `layouts/project-tetris.ini` for the editor figures `well-built`, `rules-log`, `drawn`, `playing`, `hud-shown`, `game-over` and `passed`. All seven use `waitsFor: tier 2: editor screenshot`, because their project is this tutorial's state, which no template or sample holds.
- Figure `result` uses the sample project and `waitsFor: tier 2: editor screenshot`; `exported` is a runtime run of the sample.
- Diagram `well-coordinates` is an SVG under `src/assets/figures/make/project-tetris/`.
- Tutorial: `startsFrom` is the template; stage 7 has no commands (the play-test runs from a terminal); stages 2 and 3 to 6 copy their script files from `book:tutorials/make/project-tetris/`. Stage 6 copies the sounds from `Samples/Tetris/Assets/Sounds/`, stage 8 the icon.
- Words used as plain prose that the lists may lack are all removed; none is requested.

## Tutorial run

Run at the pin's Release build on 2026-11-18: the tutorial (8 stages) and exercise 1 passed as written in round 1. The
files were thinner than the page, so round 2 added the page's own values as checks and commands, and passed:

- Stage 2: `script.get` reads `Seed` 60; `log.read` holds `Tetris: new game with seed 60` and `Tetris: piece 1 is J, next I`.
- Stage 4: after the build `StartInterval` is 0.8, `SoftDropInterval` 0.04, and `MaterialI` and `GhostMaterial` keep their handles.
- Stage 5: play, one hard drop: `ScoreText` reads `Score: 0`, then `Score: 36` (18 rows, two points each); the page's
  "a score above 0, about 18 rows" now names 36.
- Stage 6: **P** shows `PAUSED\nPress P to continue` with `MessagePanel` active, **P** again clears it; `Board` has one
  `Cells` with 204 children.
- Stage 7: the commands of `Playtest.json` run inline (the reader's copy of the stage is the play-test), with `log.read`
  holding `Tetris: cleared 1 line; score 209, lines 1, level 2` and `Tetris: game over after`; both rectangles,
  `Score: 209`, `Level: 2`, the game over, **R** and `/modified` false hold at the pin.
- Exercise 1: `Best: 0` at the start, `Best: 36` after a hard drop and a game over, and `Best: 36` again in a new play
  (the save is read in `NewGame`; the editor keeps saves in the project's intermediate folder).
- Re-run at the pin v0.8.0 (319075e3) on 2026-11-23: the tutorial (8 stages) and exercise 1 passed as written in
  round 1. Pagecheck's only failures are the figure manifest's 8 `waitsFor "tier 2: editor screenshot"`: the pin now
  has `editor.screenshot`, so the figures can be taken (figure work, not the run's).
- Not run: stage 6 step 5 (hot reload while playing: a file change splits the reader's copy into new editors, so play
  mode cannot reach across it) and stage 7 step 3 (the broken score expects exit code 1, which a stage cannot expect).

## Not verified

- The exact editor labels of the Inspector rows (`Fit Content`, `Anchors`, the `Vertical Layout` rows, `Cell Mesh`, `Material I`) and of the menu `Create Child` for UI items; the steps follow the HUD and menus pages.
- That `ui.create` with `anchor` `topLeft` sets the pivot to 0 and 0 (the steps set it explicitly); the rectangles of the play-test hold for the HUD the steps build (tutorial run).
- That the editor tab of stage 2 finds new files in `Scripts` after **Ctrl+B** without a configure step.
- The Tetris Wiki page named in Further reading.

## Findings not applied

- critic-make-c-1: applied. What you need names the script files and the page copies them from the checkpoint downloads; excerpts of 25 lines at most walk through the lines.
- critic-make-c-2: applied in part. `constexpr`, the enum with a fixed type, `static_cast`, `using`, the unnamed namespace, `std::swap`, lambdas are each explained in a callout or a sentence where they first appear, with a question linking `cpp-modern`, `cpp-memory` and `cpp-generic`. `return {}` and `std::pow` are not quoted, so they are not explained.
- critic-make-c-3: applied. Stage 7 gives the line of `make/automated-playtests` with `--project .`, `--quit-after-commands` and `--no-gpu`, and the exit codes.
- critic-make-c-4: applied. The play-test ends with `play.stop`, two `edit.undo` and `scene.info` expecting `/modified` false, with the reason; stage 5 gives the HUD values the rectangles need.
- critic-make-c-5: applied. `entity.find` with `bind` of `/entities/0` is explained under the first excerpt of stage 7.
- critic-make-c-11: applied. The errata rows are not shown as errata; the page says the cells are made once, and its play-test waits with `until` and counts fixed steps.
- critic-make-c-14: applied. What you need names `Icon.png` of the release's `Samples/Tetris/Assets/` and its credit.
- Brief items not on the page: the exercise rows `new:29` (hold piece) and `new:30` (gamepad) are exercises 2 and 3 with answers but no solution files; `gamedev:456` (the viewport's canvas mode) appears as the two chips of stage 5; the Medium exercise does not run the play-test again.

## Clerk

- Admitted terms homed here: rotation box, kick.
- Refused rules: a common word (tools/data/common-words.txt) in its everyday sense; the bold may stay. Refused canvas: the glossary homes it on ui/what-game-ui-does (only its home words it).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Editor figures, taken with the provisional build (2026-11-18); every recipe keeps `waitsFor: tier 2: editor screenshot`.

- The recipes rebuild each stage's state: `files: [{"stage": n}]` copies the stage files, and `editorWindow.steps` run the commands of stages 1 to n from the tutorial file, with one waited `script.build` before the first `script.add` and the earlier stages' play steps left out. Names made by `ui.create` are found with `entity.find` and `bind`, because `check` cannot see them in the template's scene.
- `layouts/project-tetris.ini` (1280 × 720) is `first-game.ini` with the bottom tabs 181 px tall, so that the Console shows the script's two lines; the Game view is 797 × 459 at 1:1.
- well-built: round 1 good. The whole window at 960 × 540 on `layouts/dialogs.ini`: the Hierarchy lists Well with its five cubes (a child selected opens the group), and the Game tab is in front. Caption rewritten: the old "stands under the camera" is not what the picture shows.
- rules-log: round 1 good. The Console panel alone, in play: the lines `Tetris: new game with seed 60` and `Tetris: piece 1 is J, next I` between the editor's command lines.
- well-built and rules-log, round 3 (2026-11-18): round 2 emptied the take folder and left no picture of either for a viewer, so both were retaken with the recipes unchanged (provisional build) into `make-project-tetris/round3/`, then copied into `make-project-tetris/shots/` beside the others. well-built (960 × 540, `dialogs.ini`) shows Hierarchy with Well open over LeftWall, RightWall, Floor, Backdrop and PreviewBackdrop, and in the Game view a gray U around a dark panel, with a smaller dark panel at its upper right, against the sky. rules-log (Console, `project-tetris.ini`) reads `[Script] Tetris: new game with seed 60` and `[Script] Tetris: piece 1 is J, next I` at 1:1, between `script.add` and `play.start`. Both match their caption and alt; no recipe changed.
- drawn, playing, hud-shown, game-over: the Game panel alone. Round 1 showed the right state, but the "Scripts built" message covered the lower right of the view; round 2 waits 600 frames before the picture. playing plays the play-test's 13 taps and six more (six pieces locked, a square piece falling); hud-shown hard-drops once (Score: 36); game-over sets both gravity intervals to 0.01 s, as the play-test does, and waits for the panel's text. The ghost is pale gray, not white: alts say so.
- passed: cannot be shown. The figure shows a terminal with the play-test's log lines and the exit code; editor commands picture only the editor's window. The recipe stays; its round-1 take is an empty editor. What the page gets instead: a `text` figure of the command `StrataEditor --project . --commands Playtest.json --quit-after-commands --no-gpu` and its exit code, taken by the text pipeline, or the Console panel after the play-test's steps run in the editor (the lines `Tetris: cleared 1 line; score 209, lines 1, level 2` and `Tetris: game over after`), with a caption that names the Console instead of a terminal.

At the pin v0.8.0 (319075e3, 2026-11-23), Release build, no `--provisional`; `check` named every `waitsFor: tier 2: editor screenshot` as met, so those lines are gone. Nothing of this page was published before, so nothing was compared.

- result (scene, sample Tetris, camera "scene"): the recipe only built the scripts, so the picture would have shown an empty well without the HUD's values. It now waits for the build (`wait: true`) and plays 60 fixed steps with the play-test's taps (`play.input`). Round 1 good: score panel (Score: 315, Level: 1, Lines: 1) at the top left, the controls at the bottom left, a yellow square piece at the top with its gray ghost on the stack, and an L in the preview under NEXT. Published.
- well-built, rules-log, drawn, playing, hud-shown: round 1 good, as the provisional rounds described; published. The tutorial's camera (5.5, 9.5, 30) leaves the well about a sixth of the Game view's width; the pieces still read at the column's width, and the page's steps set that camera, so the recipes keep it.
- game-over: round 1 stopped at the four `script.setField` steps of the sounds (`no asset 'Sounds/Move.wav'`): stage 6 imports them with `asset.import` from the release folder, which a recipe's `files` cannot copy (only `book:` files). The sounds do not change the picture, so those four steps are gone; round 2 retaken.
- passed: still cannot be shown (above). Its `waitsFor` is now `tier 3: a terminal beside the editor; …`, so that `check` stops asking for a take; not published.

Last figures at the pin v0.8.0 (319075e3, 2026-11-24), Release build, one hold for both:

- passed: still waits (`tier 3: a terminal beside the editor`), kept as the request for a later edition; its `standIn` is
  `playtest-console`, which the page places after stage 7's checkpoint. A program text figure cannot stand in: a
  program's `files` are staged into an empty run folder, so `--project .` finds no project of stage 7.
- playtest-console (new, editor, Console panel): the steps of `game-over` up to its `play.start`, then `scene.save` (the
  play-test's last expectation is `/modified` false, and the reader's project is saved before the editor is closed),
  then the 26 commands of `Playtest.json` as they are; `files: [{"stage": 7}]`. Layout
  `layouts/project-tetris-playtest.ini` (1280 × 800): `console-panel.ini` with the Scene and Game views 140 px tall, so
  that the Console is 876 × 580 and holds the tail of the run. Round 1 good: pieces 5 to 13, `Tetris: game over after 14
  pieces; score 209, lines 1, level 2`, the new game with seed 61 after **R**, `play.stop` in Edit, two `edit.undo`
  and `scene.info` with `modified` false, no failed step. The line `Tetris: cleared 1 line; …` has scrolled above the
  panel; the caption names only what shows. The page's sentence before the checkpoint now says that the picture is the
  Console of a run in an editor window and that only the terminal reports the exit code. Published.
- exported (runtime, sample Tetris, 10 s at 1280 × 720, quality high): round 1 good. The screenshot is the game's last
  frame, not its window, so the old caption ("a window of its own", "titled Tetris") was rewritten to the frame: score
  panel at Score 0, Level 1, Lines 0, a blue J halfway down with its pale ghost on the floor, a long piece as the next
  one, the keys at the bottom left. Published.

## Engine

- `EditorContext::GetPlayBuildReason` (`StrataEditor/src/Editor/EditorContext.cpp:2300-2343`) builds before play when a
  script file is newer than the module; for a module of an earlier session it compares write times only. On a drive
  whose file times count in steps of two seconds (exFAT here: every time ends in an even second), an edit within two
  seconds of the last build is not newer, and the editor plays the old module. Seen on 2026-11-24 with the package:
  run C rebuilt after the edit to 101, then run D, with 100 restored at once, played the 101 module (210, exit 1)
  without a build. The page's play-test steps 3 and 4 say what the reader meets and does (save again after a moment).
- A play-test run on a project whose scripts were never built (a fresh checkpoint download) fails its two
  `script.setField` calls before play (`No script module is loaded`), so the level stays 1; `play.start` builds only
  after them. The engine says what to do; the page's step 2 says it too.

## Track walk G-final-11 (2026-11-24)

Answers to WK2 to WK10 of `plan/walks/G-final-11.md`:

- The "no ground" checks name the sky's picture of its planet's ground (the Atmosphere sky draws it below the horizon,
  `Strata/shaders/IBL/AtmosphereSkyView.comp.slang`), seen in the `well-built` picture and a capture.
- Stage 1 step 5's tab captures with `camera` `scene`; stage 3's tab steps twice before the capture (a capture right
  after a paused start shows an empty well, seen at the package).
- The checkpoint files are named by download (`Scripts/TetrisBoard.cpp` of checkpoint 2 to 6); the folder `Scripts`
  also holds the template's `Spinner.cpp` and `CMakeLists.txt`.
- Stage 4's tabs give commands for the move, the soft drop (24 steps held: about ten rows, seen in a capture), gravity
  (48 steps: one row) and the full well (fast rows, as the play-test); the file runs them and checks `Tetris: game over
  after` and that `play.stop` restores `StartInterval`.
- Stage 5's tab gives `ControlsText` whole and the score commands; stage 6's tab gives the message panel's components,
  the pause, game over and **R**, and the hot reload's `entity.find` and `entity.get`. The file checks the game over,
  **R**, `Score: 0` and the sound fields; the hot reload itself stays unrun (above).
