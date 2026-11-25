# Walk of track G, segment 11, at v0.8.0

Persona: G0 (game maker). Entries walked, in order: `make/designing-a-game`, `make/project-tetris`,
`make/project-platformer`. Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`), driven with
StrataCLI against a headless StrataEditor (one editor session per perf-lock hold, none left running). Work folder:
`.worktrees/docs-work/walk-G-final-11/` (projects `Tetris`, `Platformer`, exports `Tetris-export`, `Platformer-export`).
Preferences were not changed; `STRATA_SESSION_DIR`, `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` were set per run.

What was walked: designing-a-game read in full, exercises answered; project-tetris stages 1 to 8 through the commands
of each step (script files taken from the stage downloads), the play-test run three times (209, then 210 with the 101
edit and exit code 1, then 209 again), export and the exported game run with a screenshot; project-platformer stages 1
to 9 the same way, export (pruned) and the exported game run with a screenshot.

What was not walked, and why: everything that needs eyes, ears or a person (playtest with a friend, sounds, a
human pressing keys in a window, clicking Play in the exported menu); the Check yourself questions were answered in
the head and matched their answers; the exercises of Tetris and the platformer were read, not built; the Coin Run
project is not in the book as a download (WK1).

## Entries

### WK1. designing-a-game, Before you start, and Exercises (Medium)
Kind: left the book. The page offers no stage download for a reader who arrives here, only the worked-solution ZIP of
exercise 2. Exercise 2 says "Copy your finished Coin Run folder", and neither the page nor its prerequisite offers a
Coin Run project to a reader who did not build it. I went on without it. The solution's commands (floor and wall cubes)
could not be checked against `CoinPlacer` and the `TimeLimit` field of `CoinRunGame`, which the solution names. The
exercise also asks for a person to play the level; an agent persona cannot do that.

### WK2. project-tetris, Build the well, step 1 and the rest of the stage, "You should see: no ground"
Kind: did not match. After deleting Ground, a capture of the scene shows a beige plane to the horizon (the same in the
Platformer, stage 2). The page says "no ground" and, for the platformer, "a sky and a sun, and no floor". I could not
tell whether that plane is the sky's ground colour or a leftover.

### WK3. project-tetris, Build the well, step 5 (move the camera), "You should see: in the Game view the whole well"
Kind: did not match. The command tab has only `component.set`, so no capture is offered. A plain `viewport.capture` in
Edit mode shows the Scene view (the editor camera), not the Game view. I found `camera: "scene"` in the command's
description and that showed the well as the page says.

### WK4. project-tetris, Write the rules, step "Copy the rules into the project" (and every later "Copy ...step N.cpp")
Kind: did not match. The page names `TetrisBoard.step2.cpp`, `step3`, ... "of the checkpoint download". The downloads
are whole projects (`ProjectTetris/Scripts/TetrisBoard.cpp`, `TetrisGame.h`, `TetrisGame.cpp`); no file has a step
name, so I guessed to take `Scripts/TetrisBoard.cpp` of each stage's ZIP. The stage ZIPs also hold `Spinner.cpp` and a
`.gitignore`, so "You should see: three files in Scripts" is four (the template's Spinner.cpp stays).

### WK5. project-tetris, Draw the well, last step (Play for a moment), "You should see: a blue piece ... a pale ghost"
Kind: did not match. With the tab's commands (`play.start` with `paused: true`, then `viewport.capture`) the capture
equals the edit view: an empty well, because a paused game has run no fixed step and the board has drawn nothing. After
`play.step` with 2 steps the capture matched the text (blue J on top, ghost on the floor, light blue I in the preview).

### WK6. project-tetris, Play: keys and gravity, "Play, and move the piece" and the next two steps
Kind: guessed. The command tabs say "run input.sequence as stage 7 does" or "play in the editor". I used `input.key`
(Left, then Space) while the game was paused and stepped; the answer says `seen: false` but the capture showed the J
one column left and dropped, with the ghost, as the text says. The gravity step (0.8 s per row) and the soft drop were
not exercised.

### WK7. project-tetris, Show the score, "Add the controls text and the label of the next piece"
Kind: guessed. The command tab says "Make ControlsText with ui.create as the three texts above, anchor bottomLeft" and
gives no text, size or font size (the text and `FontSize 18` are in the editor tab only). I sent the sentence on one line
with spaces; it wrapped to the three lines of the picture on its own. The score panel and NEXT label matched ("Score: 36
after the hard drop" matched exactly).

### WK8. project-tetris, Finish the game, "Make the message panel and its text"
Kind: guessed. The tab says "Set the anchors, the layout and the text's size with component.set as in stage 5". The
editor tab says anchor 0.5 and 0.42; the command shows `anchor: middleCenter`, and the layout property names
(`ChildAlignment`, `Padding`) are not shown for the command. I used `UILayout` with `Type`, `ChildAlignment: MiddleCenter`,
`Padding`; it was accepted. The pause and game-over messages came out as the page says.

### WK9. project-tetris, Finish the game, "Play, pause and lose" and "Check the hot reload"
Kind: left the book. Sounds cannot be heard (null audio device, no ears); I checked the fields were set, not that "a
short sound" plays. Pause text, game over text and the empty text after R matched. After `script.build` during play
the log restarted the game and `Cells` stayed a single entity (the 204 children were not counted).

### WK10. project-tetris, Prove it with a play-test, third run of the editor
Kind: failed (a test setup effect). I edited `TetrisGame.cpp` (100 to 101) and started the editor less than two
seconds after the previous run: it did not rebuild, played the old module and gave 209 with exit code 0. Run again
after a pause it printed "Building the scripts before playing" and the page's `Score: 210` error with exit code 1. Not
a page error; a reader who types slowly will not see it.

### WK11. project-platformer, Import the assets, step 3
Kind: guessed. The tab shows one model and one sound and says "Run the command once for each file". I took the folders
from What you need (`Models/Platformer`, `Sounds`, `Sounds/Footsteps`); the models landed in `Models/Platformer/<name>/`
as the page says. CREDITS.md I copied from the release's `Samples/ThirdPerson/` (the page says only "the sample's").

### WK12. project-platformer, Make the player walk and jump, "Make the project's Gameplay map"
Kind: guessed. Only Move is shown. For Look, Jump, Run, Respawn and Pause I wrote the commands from the table (kind
Button or Vector2, the binding strings as listed); all were accepted.

### WK13. project-platformer, Lay out the course and Make the player, "You should see" with a wire outline, wire capsule and robot position
Kind: left the book. I could not look at the Scene view's green collider outline, the wire capsule or the robot's
facing in a picture of the editor window. A scene capture showed the four islands (island D higher) and the player
moved along the course as the text says (W for 60 steps moved 3 m along -Z; yaw 90 walked along -X).

### WK14. project-platformer, Bring the robot to life, "Play and walk, run and jump"
Kind: left the book. Walk (speed 3), Run (6.5 with LeftShift) and the footstep count (Steps counted up) matched. I did
not catch the Jump state in the air with a single poll; the answer after the jump showed Walk. Sounds not heard.

### WK15. project-platformer, Make a course to finish, coins, pads, checkpoints
Kind: left the book. The count 0 / 0 at the start of play matched, and at the goal "A new best time!" and the time line
matched. I did not play a coin pick-up, the pad launch, or the return to a checkpoint after a fall.

### WK16. project-platformer, Add menus
Kind: guessed. Only the first two `ui.create` calls of the menu are shown ("Run ui.create for each element"); the
layout, title and buttons (`type: button`, `text`) and the pause and completion buttons I wrote from the schema's
error message listing the types. The scripts `MainMenu.cpp` and `PauseMenu.cpp` I took from the stage 8 ZIP (the page
points to the Menus page). Pause (Escape held) showed `Paused: true` and the panel over the HUD. In the exported menu
the buttons sit at the left of the panel, not centred.

### WK17. project-platformer, Ship the game, step 4 (run the exported game)
Kind: left the book. The exported game started (loading scene, then the main menu in a screenshot after 8 s). "Play,
finish the course and see your best time again after you restart the game" was not played (no way to click).

### Checks that matched (not entries)
Sample size claims of designing-a-game (829 lines in three files, 18 files of 1,720 lines) match the package. The
Tetris play-test matched the page in all three runs (209; 210 with exit code 1; 209), and the final `TetrisBoard.cpp` of
stage 6 is identical to the sample's. Tetris and Platformer exports have the file lists the pages give.

## Answers

No patches are listed under "## Built by the integrator". Every changed page passes `tools/pagecheck.py`; the changed
tutorial files pass `tools/tutorials.py run` with the pin build and with the official v0.8.0 package (work folders
`docs-work/tutorial-runs/make-tetris-wf11-pin`, `-pkg`, `make-plat-wf11-pin`, `-pkg`). The page claims were seen with
the package in `docs-work/wf11`: captures of Tetris stages 3 and 4 and of platformer stage 3, play-test runs with fast
edits, and a headless run of the walker's platformer export.
Commits: make/designing-a-game e198a0b4, make/project-tetris 39d7f7f9, make/project-platformer 54ed1d8e.

### make/designing-a-game

- **WK1** fixed (page). Exercise 2 now points a reader without a Coin Run of their own to checkpoint 4 at the end of
  Ship the finished game and says how to open its `CoinRun.stproj`. The worked solution names the coin list
  (`c_CoinPositions` at the top of `Scripts/CoinPlacer.cpp`, a code change and a build) and `TimeLimit` (40 s), both
  present in that download. The playtest with a person stays a person's step: the solution now says that no command
  replaces it, as the page's section on what the approach cannot do says.

### make/project-tetris

- **WK2** fixed (page). The beige plane is the Atmosphere sky's picture of its planet's ground below the horizon
  (`Strata/shaders/IBL/AtmosphereSkyView.comp.slang`), visible in the `well-built` picture too. "You should see" now
  says: no `Ground` in the Hierarchy, and a pale brown plain below the horizon that the sky draws, with nothing to stand
  on. The platformer's stage 2 says the same.
- **WK3** fixed (page). Stage 1 step 5's tab adds `viewport.capture` with `camera` `scene` and says that outside play
  the capture looks through the editor camera, with `scene` through `Main Camera` as the Game view does.
- **WK4** fixed (page). What you need says each download is a whole project `ProjectTetris` and that its folder
  `Scripts` holds `TetrisGame.h`, `TetrisGame.cpp` and the stage's `TetrisBoard.cpp` (checkpoint 2 the first version,
  checkpoint 6 the final one). Every copy step names `Scripts/TetrisBoard.cpp` of checkpoint N's download at the end of
  its section; no step names a `stepN` file. "You should see" lists the three files beside the template's `Spinner.cpp`
  and `CMakeLists.txt`, and its "If you do not see it" no longer asks for only three files.
- **WK5** fixed (page, file). The tab runs `play.step` with 2 steps before the capture and says why: a game started
  paused has run no fixed step, so the board has drawn nothing (a package capture at 0 steps shows the empty well, at
  2 steps the J, its ghost and the I in the preview). The file steps 2, as the page.
- **WK6** fixed (page, file). Stage 4's three play steps have commands: `input.sequence` taps **Left** and **Space**
  (the J lands one column left, the I appears), holds **Down** for 24 steps (the I about ten rows lower, seen in a
  capture), runs 48 steps (one row) and then fills the well with fast rows through `script.setField`, ending with the
  log line `Tetris: game over after`. The tab says why `input.key` answers `seen` false while paused. The file runs the
  same commands and checks the second piece, the game-over line and that `play.stop` restores `StartInterval` 0.8.
- **WK7** fixed (page). The tab gives `ControlsText` whole: its `ui.create` with the three-line text (`\n`), anchor and
  position, and the `component.set` of `FontSize` 18 and `Alignment` `Left`, as the file. Step 6's tab gives the score
  commands (one step, `Score: 0`, a hard drop, `Score: 36`), as the file.
- **WK8** fixed (page). The tab gives every command of the message panel: the `UIRect` anchors 0.5, 0.42 with **Fit
  Content**, the `UILayout` with `ChildAlignment` `MiddleCenter` and its padding, and the text's size, alignment and
  colour, as the file; it says how `middleCenter` and the anchors combine. The editor tab names **Anchor Min** and
  **Anchor Max**.
- **WK9** fixed (page, file) for what a command can show; rejected for hearing the sounds. The pause, game-over and
  **R** step has commands (pause and continue, fast rows to the end, **R**, `Score: 0`); a command cannot hear, so the
  tab points to `script.get`, whose four sound fields the file checks. The hot reload step's tab adds `entity.find` and
  `entity.get` for the one `Cells` and its 204 children, and tells the reader to set the number back and build again,
  so that the file stays the sample's. The hot reload itself stays out of the file: a file change splits the reader's
  copy into new editors, so play cannot reach across it (notes, `## Tutorial run`).
- **WK10** fixed (page; engine). Reproduced with the package on this machine's exFAT drive, where every file time is an
  even second: after a build, an edit made within two seconds is not newer than the module, and the editor plays the
  old one (run D played the 101 module after 100 was restored at once, score 210, exit 1).
  `EditorContext::GetPlayBuildReason` compares write times (`StrataEditor/src/Editor/EditorContext.cpp:2300-2343`).
  Steps 3 and 4's "If you do not see it" say that some drives keep file times in steps of two seconds and to save the
  file again after a moment. The same runs showed that a fresh download fails the play-test (`script.setField failed:
  No script module is loaded`, level 1), because the fields are set before play builds: step 2 says to build once
  first. Both are in the page's notes under `## Engine`.

### make/project-platformer

- **WK2** fixed (page), as for Tetris: stage 2 step 1 names the sky's picture of its planet's ground.
- **WK11** fixed (page, file). The tab imports all fifteen files in four commands, one `files` list per folder, with
  `<A>` for the release's `Samples/ThirdPerson/Assets`; the file does the same and asks `asset.info` for
  `Models/Platformer/block-grass-large-tall/block-grass-large-tall.glb`. Step 3 names the release's
  `Samples/ThirdPerson/CREDITS.md`, which the copy of the sample also holds.
- **WK12** fixed (page). The tab shows all six `inputActions.setAction` calls of the table, as the file runs them.
- **WK13** fixed (page, file). The Scene view and `viewport.capture` draw collider shapes only for the selection
  (`viewport.setSettings` `allColliders` is off by default). Stage 2 step 2 and stage 3 steps 2 and 3 now select the
  block's mesh child or the player (with `camera.focus`) and capture; a package capture showed the green outline of
  the block, the wire capsule and the robot's back, so "You should see" adds that the robot faces away from the editor
  camera. The file selects as the page.
- **WK14** fixed (page, file). The tab catches the Jump state paused (tap **Space**, run 10 steps, `animation.info`),
  then holds **W** and the `Shift` key for Walk and Run, with callouts and the fade of 0.15 to 0.2 s that may need a
  second read. The file checks Jump, Walk, `Steps` and Run. Hearing the steps stays a person's (rejected part): `Steps`
  counts them.
- **WK15** fixed (page, file). Stage 6 step 9's tab moves the paused player to the coin and first checkpoint (`Coins`
  1), below the fall height (back near (2, 0, -12)), onto the pad (about 5 m up after 30 steps) and onto the goal
  (`Completed` true); the file checks each.
- **WK16** fixed (page). The menu tabs give every `ui.create`: the main menu's `verticalLayout`, title and two buttons,
  the pause panel and its three buttons, and the completion panel's two buttons with their event target, as the file.
  The walker's buttons sat at the panel's left because a `UILayout` added with `component.add` keeps `TopLeft` without
  stretch; the `verticalLayout` of `ui.create` is `TopCenter` and stretches
  (`StrataEditor/src/Editor/GameUIPresets.cpp:219-224`), which the tab and "If you do not see it" say.
  `MainMenu.cpp`, `PauseMenu.cpp` and `LoadingScreen.cpp` are named in the folder `Scripts` of checkpoints 8 and 9.
- **WK17** rejected. Playing the exported game to the flag and again after a restart needs a person at the window; no
  command drives an exported game. What a run can show matched: the loading scene, then the main menu, and a headless
  run of the walker's export (`--headless --frames 600`) exits 0.

## Confirm

Persona G0, confirming the fixes of segment 11 as a reader of the book as it is now. Package: official Strata 0.8.0
Windows package, driven with StrataCLI against headless editors (one per perf-lock hold, none left running). Work
folder: `.worktrees/docs-work/walk-G-final-11/confirm/` (projects `Tetris` and `Platformer`, the stage downloads
`t1` to `t8`, `p1` to `p8`, `cr4`, `T7`, `P5` to `P8`).

Setup note (not a page error): the preview server at port 4329 still served the book from before the fixes (the Tetris
page said "no ground" and had no `camera` `scene` capture). I merged `book/write` into the `docs-site` worktree,
rebuilt its `dist` and served it on port 4332; every quote below is from that build.

Result: all sixteen entries are confirmed. Two small remarks follow the list (R1, R2); neither blocks a reader.

- **WK1** confirmed. Exercise 2 sends a reader without a Coin Run to checkpoint 4 at the end of Ship the finished game
  of `make/project-coin-run` (the link `#ship-the-finished-game` works; the zip holds `ProjectCoinRun/CoinRun.stproj`).
  That download has `c_CoinPositions` at line 7 of `Scripts/CoinPlacer.cpp` (five positions) and `TimeLimit = 40.0f` in
  `CoinRunGame.cpp`, set to 40 in `Main.stscene`. (Checkpoint 4 of `make/export` is another project, with `CoinHud` and
  60 s; the page names the coin-run one, so a reader who follows the link gets the right file.)
- **WK2** confirmed. From a new Basic 3D project, deleting `Ground` and capturing shows a sky and a pale brown plain
  below the horizon with the axis lines; the step now says exactly that.
- **WK3** confirmed. Step 5's tab has `viewport.capture` with `camera` `scene`; the capture shows the well (gray U, dark
  panel, smaller preview panel) and the sky behind, as the text says.
- **WK4** confirmed. "Copy ... from the folder Scripts of checkpoint 2's download": `t2/ProjectTetris/Scripts` holds
  `TetrisGame.h`, `TetrisGame.cpp` and `TetrisBoard.cpp` beside `Spinner.cpp` and `CMakeLists.txt`, as the page says;
  the build was green and the log read `new game with seed 60` and `piece 1 is J, next I`.
- **WK5** confirmed. Stage 3 step 4 (`play.start` paused, `play.step` 2, capture): the capture before the steps is the
  empty well, as the added sentence explains; after 2 steps a blue J on top, a pale gray ghost on the floor and a light
  blue I in the preview.
- **WK6** confirmed. Stage 4 step 2: `input.sequence` (Left tap at 0, Space tap at 2, 4 steps) leaves the J on the floor
  one column left of its start and the I at the top. Step 3: Down held for 24 steps puts the I about ten rows lower with
  its ghost on the J. Step 4: `play.step` 48 drops it one more row; with both intervals at 0.01 and 600 steps the well
  fills and the log has `Tetris: game over after 12 pieces; score 46`.
- **WK7** confirmed. Stage 5 step 4: the `ui.create` text with the three-line sentence and the `component.set` calls give
  the controls at the bottom left (three lines) and NEXT above the preview; `component.get` shows the text with its
  `\n`. Step 6: `Score: 0`, then `Score: 36` after the hard drop. The font sizes (36, 30, 30) are in the table.
- **WK8** confirmed. Stage 6 step 2's tab gives every command; the panel is hidden (`active` false) and shows the yellow
  two-line text over the well in the game-over capture.
- **WK9** confirmed. Step 4: `PAUSED\nPress P to continue`, then `GAME OVER\nPress R or Enter to play again`; after R the
  text is empty, the panel inactive and `Score: 0`. Step 5: a source edit (0.92f to 0.9f) built during play reloads
  (`moduleChanged` and `reloaded` true); `entity.get` of Cells lists its 204 children; after the second build the file
  equals checkpoint 6's `TetrisBoard.cpp`. Sounds were not heard (the page says a command cannot hear).
- **WK10** confirmed. A fresh download of checkpoint 7 run at once: `script.setField failed: No script module is
  loaded`, the page's text for it (the editor then builds and plays; exit 1). After building once, the play-test gave
  209 and exit 0. Edit 100 to 101 and run at once: the editor logged `Building the scripts before playing:
  'Scripts/TetrisGame.cpp' changed after the scripts were built`, `Score: 210` and exit 1; again after a moment: the
  same 210 and exit 1. Restoring 100 at once rebuilt and gave 209, exit 0. The two-second case did not occur on this
  drive (file times in whole seconds: an edit one second after the last build counted as newer), so the page's text for
  it could be read but not seen.
- **WK11** confirmed. The four `asset.import` commands (one `file`, three `files` lists) imported all fifteen files into
  the folders the page names (the kit models into `Models/Platformer/<name>/`); `asset.info` of
  `Models/Platformer/block-grass-large-tall/block-grass-large-tall.glb` answered; `CREDITS.md` of `Samples/ThirdPerson`
  went beside the `.stproj`.
- **WK12** confirmed. The six `inputActions.setAction` calls of the table ran as written (all accepted).
- **WK13** confirmed. Stage 2 step 1: no Ground, a pale brown plain remains, as the step says. Step 2: with the block's
  child selected, the capture shows its green outline following the block's shape. Stage 3: after `selection.set` and
  `camera.focus` the capture shows the wire capsule on island A with its bottom on the grass; with the robot placed and
  parented the capture shows the robot from behind (its back toward the editor camera) inside the capsule.
- **WK14** confirmed. Stage 5 step 6: paused, Space tap, 10 steps: `animation.info` says `Jump`; unpaused and W held:
  `Walk` (Speed 3); with `LeftShift`: `Run` (Speed 6.5); `Steps` of Footsteps counts up (4). See R1.
- **WK15** confirmed. Stage 6 step 9 from the stage 6 download: at (0, 0.1, -12) `Coins` is 1; at (2, -20, -12) the
  player is back at (2, 0.009, -12) after 5 steps; at (2, 0.1, -29) it is at y 4.7 after 30 steps (the pad); at
  (2, 6.1, -40) `Completed` is true.
- **WK16** confirmed. Stage 8 step 2's six `ui.create` calls: the panel is 320 by 240 px at screen 1280 by 720 and the
  title and both buttons are 309 px wide inside it, so the buttons span the panel. Step 5: the pause panel and its
  three buttons; step 7: the completion panel's two buttons side by side at its bottom (each 187 px wide). The two
  scripts were copied from checkpoint 8 as steps 3 and 6 say.

Remarks:

- **R1** (small, `make/project-platformer` stage 5 step 6). The tab's commands are right, but timing matters: an agent
  that sends `play.pause` false, W and `animation.info` back to back still reads `Jump` (the jump lasts about 1.1 s of
  game time; the page's sentence about reading again covers it). With about a second between the commands the states
  were Walk, then Run. With 5 s of waiting the player had walked off island A and the state was neither. A sentence
  "wait about a second after each command" would remove the guess.
- **R2** (not a page error, `make/project-tetris` stage 3 step 3). Twice, a `script.build` right after copying
  checkpoint 3's `TetrisBoard.cpp` over the stage 2 one answered `moduleChanged` false, so the new fields were missing
  and `script.setField` said `TetrisBoard has no field 'MaterialI'`. With a `touch` of the file and three seconds
  before the build it built and reloaded (as at stages 4, 5, 6 and 8, where a plain copy had worked). I did not find the
  cause. A reader who does not see the new fields should save the file again and build again, as stage 7 step 3 says;
  stage 3's "If you do not see it" does not name this.
