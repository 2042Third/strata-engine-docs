# Notes: make/play-test-debug

## New terms

None. The page defines Play (glossary id `play`) and the running copy in bold.

## Requests

- Figures: none. Both pictures are Mermaid diagrams (the running copy, one step of a paused game). The brief's two
  pictures of the editor (a paused game, the Problems panel) are not drawn: the figure recipes need Coin Run projects
  that do not exist yet.
- Tutorial file `tutorials/make/play-test-debug.tutorial.json` starts from `make/hud`, which has no tutorial file yet.
  It copies `tutorials/make/play-test-debug/CoinHud.cpp`, which assumes a `CoinHud` class with an `Entity CoinText`
  field; the writer of `make/hud` must keep these names or change the file.
- The end state in the brief (bug fixed, `make/export` starts there) needs the two lines of step 8 in `Coin.cpp`
  (`SetTag("Collected")` before `Destroy()`); since the tutorial run the file writes them (`play-test-debug/Coin.cpp`).
  The page shows no download of the end state: the card names no directive for a how-to.
- Exercise 1's file starts from `make/play-test-debug`.

## Tutorial run

- 2026-11-18, four rounds, the tutorial (7 stages) and exercise 1 pass at the pin's Release build.
- The file had one stage (step 3's commands) and copied a `CoinHud.cpp` with an `Entity CoinText` field that the
  `make/hud` script does not have, dropping its timer. Now one stage per page step that commands can do (1, 2, 3, 4,
  6, 8, 9; 5 and 7 are Inspector and debugger), with the page's values as checks. Step 6 breaks the hud script
  (`CoinHudNoSemicolon.cpp`) and repairs it (`CoinHudRepaired.cpp`, the hud's file); step 8 plants the bug
  (`CoinHud.cpp`: the hud's script with the count in `OnLateUpdate`) and writes the fix (`Coin.cpp`: the sound page's
  coin with `SetTag("Collected")` before `Destroy()`), so the end state that `make/export` starts from has the fix.
- Page mended to the engine: the coins are placed by `CoinPlacer` at Play, so the edited scene has none after Stop and
  Simulate shows none (step 1, step 2, check 1, exercise 1); the coins turn 120 degrees per second (2 per step), not
  180; step 8 now tells the reader to move the count into `OnLateUpdate`; step 9 names its `input.sequence`.
- A timer check at exactly 1 s (60 steps) reads "Time: 30" (`ceil` of a float a hair above 29), so stage 4 steps 90.
- Stage 7 checks the step count and the coin count of both runs, not the ball's position (no literal known before the
  run); round 4 read the ball's height in the log.

## Track walk G, final, segment 6 (2026-11-24)

Answers to `plan/walks/G-final-6.md`, WK7 to WK11:

- WK7: Before you start links the HUD page's last checkpoint (its last section) and says how to open the zip. The page
  itself is a how-to: its own end state is the box at the end of Result (`stage-7.zip`), which `make/export` now names.
- WK8: the root `Coin` turns (`Coin::OnUpdate` rotates its own transform); its child `coin-gold` holds the mesh.
  `entity.get {"world": true}` answers `world.rotation.euler` in degrees (`EntityCommands.cpp:363-369` at the pin), so
  the tab reads 58, 60 and 80 degrees after 30, 31 and 41 steps, and explains the quaternion of `component.get`. Stage 3
  checks the three Euler angles (passed, pin build).
- WK9: a failed `script.build` answers a JSON-RPC error (code -32005) whose message is the build's error text; the
  diagnostics list is only in `script.status` (`build.last.diagnostics`: file, line, column, message, code, severity).
  The tab says both; step 6 says the compiler names the next statement's start (`CoinHudNoSemicolon.cpp` lacks the `;`
  of line 20, the error is at 22). See `## Engine`.
- WK10: a log of the count alone reads 5 then 4 with or without the fix; only the frame differs. The planted line now
  logs `Time::GetFrameIndex()`, and the reader adds `Log::Info("Coin collected in frame ", ...)` to `OnTriggerEnter`
  (`CoinLogged.cpp`, the sound page's `Coin.cpp` with that line; `Coin.cpp`, the fix, keeps it). Run with the pin build:
  before the fix `Coin collected in frame 36` and `HUD shows 4 coins in frame 37`, after it both 36; stage 6 checks the
  three lines. Step 8 now says which lines to delete, where the function, the member and the include go, and that the
  Result's download holds both files whole. The listing stays lines 17-23 (a 10-line fence would need callouts and a
  question on `override`).
- WK11: step 7 says a reader without a debugger reads it and continues; step 8 needs only the log.
- Runs, 2026-11-24: the tutorial and its exercises pass with the pin build (Release) and with the official v0.8.0 package.

## Engine

- `script.build`'s description says "Fails with the first compiler errors; the result and script.status list all
  diagnostics" (`StrataEditor/src/Editor/EditorScriptCommands.cpp:314-318` at the pin). A failed build answers only the
  error (code -32005, message "Building the scripts failed (exit code 1)" and the compiler's lines), with no result and
  no `diagnostics`; `script.status` has them. The page says what the reader meets (step 6's tab). For the engine's
  agents: put the result in the error's data, or say that only `script.status` lists them.

## Not verified

- Simulate leaves skinned characters in their rest pose: read from the code only (new:40).
- Linux and macOS: a Release or Dist editor builds scripts without debug information, so breakpoints very likely do not
  bind: read from the build files, not run (new:41, new:42). That a Debug editor's scripts carry `-g` is CMake's default,
  not checked.
- The toast of a failed build and the call stack below `OnTriggerEnter` were not run.
- Step 8's count after the fix: `FindEntitiesByTag` reads the tag index, which `SetTag` updates (read, not run).

## Findings not applied

- Brief step 3 says the status bar counts the steps: at the pin it shows only "Paused" (`EditorLayer::DrawStatusBar`).
  The page reads the count from `play.step`'s `fixedSteps` and `play.state`; exercise 2 matches Console lines with the
  presses instead.
- Brief step 6 says Console lines carry file and line: at the pin a log line shows time, source and text; only
  messages that name a script source, such as build errors, open the file when clicked.
- critic-make-a-29: its fix (count in `OnUpdate`) does not remove the lag: a count at the start of the frame is one
  frame stale the same way. The page keeps `OnLateUpdate` as planted, shows that `FindEntitiesByTag` still returns an
  entity after `Destroy()`, and fixes it by retagging before the destroy.

## Since

0.3.0: `gamedev:222` and `gamedev:223` give Play, Simulate, Stop and edits while playing as 0.3.0; pause and step came
with 0.4.0 ("Exact play-testing", `editor-core:222`).

## Clerk

- No term or word asked.
- Left for the planner: the editor pictures, the tutorial's start and its end state (the Coin.cpp lines of step 8).
