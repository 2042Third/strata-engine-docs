# Walk log: track G (persona G0), segment 6, at v0.8.0

Entries walked: `make/hud`, `make/play-test-debug`, `make/export`, `make/project-coin-run`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`), StrataEditor (window 1280x720) driven by
StrataCLI, one editor session under the perf lock; exported games run from PowerShell under the same hold. Started from
the stage download of the last step of Sound (`make/sound` stage-4) and continued the same project through all four
pages (projects in `walk-G-final-6/proj`, exports in `walk-G-final-6/Builds`). The checkpoint zips of `make/hud` and
`make/project-coin-run` were downloaded; the CoinRunGame files of the latter were taken from them.

Not walked: clicks in menus, Hierarchy, Inspector, Console and Problems panels, the Anchors button, Ctrl+D, the F8
camera chip and the resolution chip (all done through commands and read through `ui.layout`, `log.read`,
`viewport.capture`); the breakpoint, call-stack and watch steps of `make/play-test-debug` (no debugger); double-clicking
the exported game and Open Folder; rolling the ball into all five coins for a won round (I deleted the coins in the
running copy instead); the CREDITS.md rows (no file); the exercises of `make/play-test-debug` and
`make/project-coin-run`, the medium exercise of `make/export` (basic and medium done there) and the Medium exercise of
`make/hud` (the Basic one was done).

## WK1
- Entry: `make/hud`; page: same; section: "What you need".
- Kind: did not match.
- The page says to select one of your coins and read its Tag component. In the Sound checkpoint the Hierarchy holds no
  coin in Edit mode (`CoinPlacer` makes them while the game plays; the scene has only the entity Coins). I could only
  see the tag at work later: the script counted 5 entities tagged Coin in play.

## WK2
- Entry: `make/hud`; section: "What you need" (button_square_flat.png).
- Kind: guessed.
- "Import it as you did in Assets" gives no command and no folder. I ran `asset.import` with the file path in the release
  and no folder (the command is shown on `make/assets` and `make/export`); the asset landed at the top of Assets.

## WK3
- Entry: `make/hud`; section: "Make the canvas and the corner texts", the flat canvas.
- Kind: did not match.
- The command tab is only `viewport.setSettings {"canvasMode": true}`. The editor tab says select HUD and enable the 2D
  and Game UI chips. Run alone the command left `gameUI` false and nothing selected (I found `selection.set` and the
  `gameUI` setting with `StrataCLI list` and `viewport.getSettings`). `viewport.capture` then showed the editor camera
  with the texts, not "an empty rectangle of 16:9"; `editor.screenshot` showed a cramped window without the Scene tab.

## WK4
- Entry: `make/hud`; section: "Drive the HUD from a script".
- Kind: guessed.
- The listing shows lines 9-32 and 34-51 only; the first eight lines (the include of StrataScript.h, `using namespace
  Strata;`) are not shown. "Replace the file's text with the listing" would drop them. I kept the template's header and
  pasted the rest, with two spaces for the tab. `script.create` returns a file path and the page has no command that
  writes text into it; I wrote the file with a shell.

## WK5
- Entry: `make/hud`; section: "Check every screen".
- Kind: guessed.
- The command tab only sets `gameView.mode`; its answer still says width 1280, height 720 for 16:9, 4:3 and 21:9, and
  shows no picture. To compare with the table (scale, canvas units, the 24-unit margin in pixels) I used `ui.layout` with
  `screen` [1440,1080] and [2520,1080], found in `StrataCLI list`. The numbers matched the table.

## WK6
- Entry: `make/hud`; section: "Drive the HUD from a script", play step.
- Kind: guessed.
- "Roll the ball into a coin" has a command tab with only `play.start`. I rolled the ball with `input.key` (S for 1.2
  seconds), found in `StrataCLI list` (my first try with a `hold` parameter failed: the parameters are `seconds` or
  `steps`). The count fell to 4 and the timer turned red at 10 seconds, as the page says.

## WK7
- Entry: `make/play-test-debug`; page: same; section: "Before you start" (what the page offers a reader who arrives).
- Kind: left the book.
- The page has no checkpoint zip (only an exercise solution) and no "What you need": "Before you start" says you have
  Coin Run with its count. I continued my own project from `make/hud`.

## WK8
- Entry: `make/play-test-debug`; section: "Play, step and debug the game", Pause and Step.
- Kind: guessed.
- "Select the spinning part of a coin and read its rotation": the child coin-gold never changed (rotation stayed
  0,0,0,1); the root entity Coin spins. The entity ids change at every Play and the coins only exist after a few steps.
  The command tab does not say how to find them (`scene.hierarchy`, `entity.get`), and the rotation reads as a
  quaternion (y 0.0698 after 5 steps, 0.0872 after 6), not degrees, so I converted: 2 degrees per step, 20 more after
  ten. This matches the page.

## WK9
- Entry: `make/play-test-debug`; section: breaking CoinHud.cpp.
- Kind: did not match.
- The text says `script.build` "answers diagnostics with files and lines". It answers a JSON-RPC error (code -32005)
  whose message holds `CoinHud.cpp(28,7): error C2146: syntax error: missing ';' before identifier 'm_TimerText'`, a line
  after the deleted `;`. `play.start` gives the same error; `editor.status` has `scriptBuild.errors: 1`. No diagnostics
  list.

## WK10
- Entry: `make/play-test-debug`; section: "Find the planted bug".
- Kind: did not match.
- I moved the count into `OnLateUpdate` as told (the page shows only lines 17-23; where the member, the include and the
  removal from OnUpdate go I guessed). The log read `HUD shows 5 coins` then `HUD shows 4 coins` after one coin, before
  and after the `SetTag("Collected")` fix: a change-only log cannot show the one-frame error, so the promised "count
  includes the destroyed coin" was not visible without a debugger. The fixed-step run (two runs, fixedSteps 180, Coins
  left: 4, the same ball position) matched.

## WK11
- Entry: `make/play-test-debug`; section: breakpoint and watch steps.
- Kind: left the book.
- No debugger on a screenless walk; not walked.

## WK12
- Entry: `make/export`; page: same; section: "What you need".
- Kind: left the book.
- It says to download the checkpoint of the last step of Play, test and debug. That page has no stage zips (only
  `exercise-1.zip`), so a reader who arrives here has no download. I continued my own project.

## WK13
- Entry: `make/export`; section: "Export the game", command tab.
- Kind: failed.
- `project.export` with the page's parameters answered "The open scene has unsaved changes; save it first (the export
  uses the saved files)". My scene had the HUD edits. The command tab says nothing about saving (only the later "Why"
  paragraph lists the refusals); I ran `scene.save` and `project.save`, then it worked.

## WK14
- Entry: `make/export`; section: "Prune the export and fix what it loses".
- Kind: did not match.
- "You should see a message that ends with a count and unused assets were left out": `project.export` with `prune`
  answers JSON (`assetCount` 10 against 24, an `excludedAssets` list), with no such sentence.

## WK15
- Entry: `make/export`; section: "Read the warning in Game.log".
- Kind: did not match.
- The pruned game logged two FindAsset warnings: first for script 'Bump' on 'Ball' ('Sounds/Impacts/Soft.ogg'), then
  CoinPlacer's 'Prefabs/Coin.stprefab'. The page names only the coin prefab (and says the Coin script loads
  GoldGlow.stmat; no GoldGlow warning appeared because no coin was made). The `Sounds` entry fixed the first one. The
  runs, exit codes 0 and 3, `--help` and the 800x600 screenshot matched.

## WK16
- Entry: `make/project-coin-run`; page: same; section: "What you need".
- Kind: left the book.
- "Download the checkpoint of its last step" points to `make/export`, whose stage-4 zip I did not use; I continued my own
  project. The page's own stage scripts are in its zips (see WK17).

## WK17
- Entry: `make/project-coin-run`; section: "Keep the round in one script" and the later script steps.
- Kind: did not match.
- The page says to replace the script with "CoinRunGame.step1.cpp" (and `.step2.cpp`) "of this page's checkpoint
  download". No such file exists: each stage zip holds one `Scripts/CoinRunGame.cpp` (stage-1 the step 1 version, stage-2
  the step 2 version, stage-3 and stage-4 identical). I took them from the zips by guess. The page's listings are line
  ranges of files the reader never sees whole.

## WK18
- Entry: `make/project-coin-run`; section: "Win, lose and start again", the played rounds.
- Kind: guessed.
- Rolling the ball over all five coins needs keys the command tab does not give (it has `play.step 600` for the lost
  round only). For the won round I deleted the five Coin entities in the running copy with `entity.delete`: panel You
  win, Coins left: 0. Step 1's "Console shows Round won / Round lost" I did not see: I read `Time: 37` and `Coins left:
  4` in the HUD; the step 2 script no longer logs those lines. Enter restarted the round (Time: 8, both panels hidden).

## WK19
- Entry: `make/project-coin-run`; section: "Check the game by playing it", row Console.
- Kind: did not match.
- The row expects "no warning and no error". The Console (`log.read` with `minLevel` Warn) and the exported game's
  Game.log hold at every start: "Script fields: script 'BallControl' has no field 'Speed'; the stored value is ignored".
  It comes from the Sound checkpoint's scene and was there before this page.

## WK20
- Entry: `make/project-coin-run`; section: "Ship the finished game", command `project.export`.
- Kind: did not match.
- The page's command has `directory` and `prune` only. The game window opened at 1920 x 1080 and the screenshot is 1920
  x 1080; the Export dialog text on `make/export` says the default is 1280 by 720 (there I passed 1280 and 720). The
  windowed run, the headless run (exit 0) and the log without a FindAsset warning matched.

## WK21
- Entry: `make/project-coin-run`; section: "Credit every asset".
- Kind: did not match.
- "Open CREDITS.md in the project folder": the project (Sound checkpoint) has no CREDITS.md. I did not write the table.
  Also `Sounds/Music/Complete.ogg` (the music) shares its name with the win chime `Sounds/Complete.ogg`.

## WK22
- Entry: `make/project-coin-run`; section: closing paragraph and bottom strip.
- Kind: guessed.
- The paragraph says track G continues at Gameplay math; the bottom strip shows "Next on your track" twice, once "The
  math of moving things" and once "Version control with git". I took the paragraph and stopped.

## Answers

No patches are listed under "## Built by the integrator". Every changed page passes `tools/pagecheck.py`; the changed
tutorial files pass `tools/tutorials.py run` with the pin build and with the official v0.8.0 package (work folders `docs-work/tutorial-runs/make-hud-walkG6-pin`, `-pkg`, `make-ptd-walkG6-pin`, `make-coinrun-walkG6-pin`, `-pkg`); the exercises that start from Coin Run (`make/commands` 1, `make/designing-a-game` 2, `make/script-builds` 1) were stamped again with both, since their chain changed.
Commits: make/hud 7f1b7833, make/play-test-debug 8df90479, make/export 73bf82ba, make/project-coin-run 735489bc.

### make/hud

- **WK1** fixed (page). The coins exist only during play (`CoinPlacer`), so What you need has its own item for the tag:
  press **Play**, select a `Coin`, read **Tag**, press **Stop**.
- **WK2** fixed (page). The import names the folder `UI` (the asset `UI/button_square_flat.png`, as the tutorial file
  imports it) and gives the `asset.import` parameters with `directory`.
- **WK3** fixed (page, file). The tab now runs `selection.set` on `HUD` and sets `gameUI` with `canvasMode`, as the editor
  tab's selection and two chips do; it says the flat view shows only in the window, not in `viewport.capture`. "You
  should see" now describes the picture `canvas-2d`: the level through the game's camera in a 16:9 rectangle between
  dark bands, no element yet. The file selects `HUD` and checks both settings.
- **WK4** fixed (page). The listing now starts at line 1 (lines 1-8, then 9-32, then 34-51), the editor tab says to
  replace the new file's text with the three listings in a text editor, and the command tab says no command writes a
  file's text and that checkpoint 3's download holds the whole file.
- **WK5** fixed (page). The tab adds the four `ui.layout` calls the file runs, and says what `rect` holds and that
  `CoinText`'s x matches the table's last column; `gameView.mode` changes only the window's picture.
- **WK6** fixed (page, file). The tab plays paused, holds **S** with `input.sequence` (150 of 180 steps), reads
  `CoinText`, runs `play.step` 2910 to 51.5 s and reads `TimerText`; the editor tab names the key. The file checks
  `Coins left: 4`, `Time: 58`, fill 0.95, then `Time: 9` in the color 1, 0.3, 0.2.

### make/play-test-debug

- **WK7** fixed (page). Before you start links the checkpoint at the end of the HUD page's last section and says how to
  open the zip.
- **WK8** fixed (page, file). Step 3 says to select the root `Coin` (its child `coin-gold` keeps rotation 0), and the tab
  finds the coins with `entity.find {"tag": "Coin"}` after 30 steps, new at every Play, and reads degrees with
  `entity.get {"world": true}` (`world.rotation.euler`): 58, 60 and 80; the quaternion of `component.get` is explained
  (y is the sine of half the angle). The file checks the three Euler angles.
- **WK9** fixed (page). The tab says what a failed `script.build` answers (error -32005, the compiler's lines in its
  message) and that `script.status` lists `build.last.diagnostics` with file, line, column and message; step 6 says the
  compiler names the start of the next statement. Engine: `script.build`'s description promises diagnostics in "the
  result", which a failed build does not have (notes, `## Engine`).
- **WK10** fixed (page, files). The planted log line now names the frame (`Time::GetFrameIndex()`), and the reader adds
  the same to `Coin.cpp`'s `OnTriggerEnter`: before the fix the Console reads `Coin collected in frame 36` and `HUD
  shows 4 coins in frame 37`, after it both frame 36, so the one-frame error shows without a debugger. The step now
  says where each change goes (the lines to delete from `OnUpdate`, the function's place and signature, the member and
  the include) and that the Result's download holds both files. The file builds `CoinLogged.cpp` with the planted HUD
  and checks both frame numbers before and after the fix.
- **WK11** fixed (page). Step 7 says a reader without a debugger reads it and continues; step 8 finds the bug with the
  log alone.

### make/export

- **WK12** fixed (page). What you need says Play, test and debug is a how-to with no checkpoints, and links the download
  box at the end of its Result (its last stage, `stage-7.zip`).
- **WK13** fixed (page, file). The command tab starts with `scene.save` and says why; step 2 says **Ctrl+S** first, and
  "If you do not see it" quotes the refusal. The file's stage 2 runs `scene.save`.
- **WK14** fixed (page). The command tab says `project.export` answers no sentence but `assetCount` and `excludedAssets`;
  "You should see" names the sentence as the dialog's.
- **WK15** fixed (page). The section names two places that load by path now, `CoinPlacer`'s prefab and `Bump`'s
  `Sounds/Impacts/Soft.ogg`, and "You should see" the two `FindAsset` lines in the walker's order. The `Coin` of Physics
  no longer loads `GoldGlow.stmat` (only the Coin of Scripting the scene did), which the page now says; the material
  stays in the list for a Coin that glows again.

### make/project-coin-run

- **WK16** fixed (page). What you need names checkpoint 4 of the export page and its section, and how to open the zip.
- **WK17** fixed (page). What you need and the three replace steps name `Scripts/CoinRunGame.cpp` of checkpoints 1, 2
  and 3, which hold the three versions; the tabs say no command writes a file's text.
- **WK18** fixed (page, file). Both tabs play the ends of a round: the five coins of the running copy are deleted for the
  win, `play.step` waits out the loss, `log.read` shows `Round won` and `Round lost` in step 1, and `input.key` Enter
  restarts in step 5, with how to read a panel's `active`. The file checks all of it, the restarts included.
- **WK19** fixed (page, file). The warning is old: `make/input` stored `BallControl`'s `Speed`, and `make/physics`'s
  `BallControl` has none; the Inspector shows only the class's fields. A new polish step 5 removes and adds
  `BallControl` on `Ball`, and the Console row and the log step say no `Script fields` line is left. The file checks
  the warning before and the class default after; in its next play the run's log has no `Script fields` line (read by
  hand: a check cannot test that a line is absent). Engine note: nothing removes a stored value of a missing field; for
  physics's fixer: its step could clear it.
- **WK20** fixed (pages). Without `--resolution`, a windowed game scales its window with the display (1280 by 720 at
  100 %, 1920 by 1080 at 150 %). Step 3's "You should see" here and the dialog item on `make/export` say so; the ship
  step also saves the scene first, which the new step 5 needs.
- **WK21** fixed (page). The step says to create `CREDITS.md` beside `CoinRun.stproj` when the project has none (no
  download holds one). The table gains the sky and the metal textures, and says the music `Sounds/Music/Complete.ogg` is
  the win chime again under the same name.
- **WK22** fixed (page). Both strips are right for their tracks: the book's script shows the chosen track's, and a raw
  page holds both. The closing paragraph named Numbers and data for track B and Gameplay math by another name; it now
  names The math of moving things (G) and Version control with git (B), as the strips do, and says the strip follows the
  chosen track.

### For a fresh walker

Start each page from the download its What you need (or Before you start) now names, with the official package.

- `make/hud`: from `make/sound`'s last checkpoint. What you need (the tag during play, the import into `UI`); Make the
  canvas step 2 by its tab (`selection.set`, `canvasMode` and `gameUI`), compared with the picture; Drive the HUD steps
  1 and 2 by their tabs (the three listings typed into the file; `Coins left: 4`, then `Time: 9` in red); Check every
  screen step 1 with the `ui.layout` lines.
- `make/play-test-debug`: from the HUD page's last checkpoint. Step 3 by its tab (58, 60, 80 degrees); step 6's
  `script.build` answer and `script.status`; step 7 without a debugger; step 8, planting by the list, with step 9's
  commands for the play: frames 36 and 37 before the fix, 36 and 36 after.
- `make/export`: from the download box at the end of Play, test and debug's Result. Export the game steps 1 and 2 by
  the tab (save first); Prune steps 1 to 4 (the answer's `excludedAssets`, the two `FindAsset` lines, none after the
  list).
- `make/project-coin-run`: from the export page's checkpoint 4. The three script steps with the checkpoints' files;
  step 4 of the first section and step 5 of the second by their tabs (`Round won`, `Round lost`, both restarts); polish
  step 5 and the Console row (no `Script fields` line); Ship steps 2 to 5 (save, the window at your display scale, a
  new `CREDITS.md` with the table's rows); the closing paragraph against the strip.

## Confirm

Segment 6 confirmed by persona G0 with the official 0.8.0 package, StrataEditor (1280x720, ui-scale 1) driven by StrataCLI
under one perf-lock hold, in `docs-work/walk-G-final-6/confirm/`. Each page was started from the download it names:
Sound's stage 4 for `make/hud`, the HUD's stage 4 for `make/play-test-debug`, Play, test and debug's stage 7 for
`make/export`, the export page's stage 4 and Coin Run's stages 1 to 3 for `make/project-coin-run`.

Book used: the server at 127.0.0.1:4329 serves a build from 13:39 that still holds the old text of all four pages (the
site/preview branch lacks 7f1b7833 and the later fixes). I read the fixed pages as the sources on `book/write` and used
the fixed download zips of `public/downloads` (they hold what the pages say: `Hud/CoinRun.stproj`, `PlayTestDebug/`,
`ProjectCoinRun/Scripts/CoinRunGame.cpp`). Pictures of the served build are the old ones. Another walker needs the preview
merged and rebuilt before it can confirm from the served pages.

Result per entry: "gets through" means no guess, no leaving the book, no mismatch.

- **WK1** gets through. Play, `entity.find {"tag":"Coin"}`, `component.get` Tag answered `Coin`, Stop.
- **WK2** gets through. `asset.import` with the page's `directory` "UI" gave `UI/button_square_flat.png`.
- **WK3** gets through, one picture not compared. `selection.set` and `viewport.setSettings` (`canvasMode`, `gameUI`) made
  `viewport.getSettings` answer both true with HUD selected, and `viewport.capture` showed the level without the flat view,
  as the page now says. I could not compare the picture `canvas-2d`: in the 1280x720 window the Scene tab is a thin strip
  above the Problems panel, and `editor.screenshot` shows no canvas. The page does not say how to look at the window from a
  CLI (`editor.showPanel`, `editor.screenshot`).
- **WK4** gets through. The three listings joined in one file built at the first try (`errorCount` 0, `script.add` fine).
- **WK5** gets through. The four `ui.layout` calls gave scale 0.866 and 1.146, canvases 1663 by 1247 and 2200 by 943,
  `CoinText` x 20.8 and 27.5, `TimeBar` x 34.6 and 45.8 (40 units): the table.
- **WK6** gets through. Paused play, `input.sequence` (S, 150 of 180 steps): `Coins left: 4`; `play.step` 2910: `Time: 9`
  with Color 1, 0.3, 0.2.
- **WK7** gets through. The zip opens to `Hud/CoinRun.stproj`; `project.open` took it.
- **WK8** gets through. `entity.find {"tag":"Coin"}` after 30 steps, `entity.get {"world":true}`: euler Y 58, then 60 after
  one step, 80 after ten; `component.get` Rotation y 0.4848.
- **WK9** gets through. Deleting the `;` of line 20 gave error -32005 with `CoinHud.cpp(22,3): error C2143: ... missing ';'
  before 'const'`, exactly the page's example; `script.status` `build.last.diagnostics` listed file, line 22, column 3,
  message; `editor.status` `scriptBuild.errors` 1.
- **WK10** gets through. Planted by the list (it compiled): before the fix `Coin collected in frame 36` and `HUD shows 4
  coins in frame 37`, the same in a second run; after `SetTag("Collected")` both frame 36.
- **WK11** gets through. Step 7 says to read it and continue without a debugger; step 8 needs the log only.
- **WK12** gets through to the download, with one new mismatch. The box at the end of Result gives the project (`PlayTestDebug/CoinRun.stproj`).
  But the checkpoint holds no built script module, and the first command tab of "Export the game" (`scene.save`, then
  `project.export`) fails with "'Scenes/Main.stscene' uses scripts, but no script module is loaded: build the scripts
  (script.build) ...". A reader who arrives from the download must run `script.build` first; the tab does not say so (the
  Why of step 3 only says scripts never built fail the export). Built, the export wrote 23 assets.
- **WK13** gets through. `scene.save` first, then `project.export` with 1280 and 720 answered `assetCount` 23.
- **WK14** gets through. The pruned answer has `assetCount` 10 against 23 and an `excludedAssets` list of 13; the tab
  says it answers no sentence.
- **WK15** gets through. The pruned game wrote two lines: `FindAsset (called by script 'Bump' ...) 'Sounds/Impacts/Soft.ogg'`,
  then `CoinPlacer`'s `Prefabs/Coin.stprefab`, no GoldGlow line, no coins; after the list (`assetCount` 18) the headless run
  exited 0 with no `FindAsset` line and `Coins placed: 5`.
- **WK16** gets through. Checkpoint 4 of the export page opened as `Export/CoinRun.stproj`.
- **WK17** gets through. `Scripts/CoinRunGame.cpp` of checkpoints 1, 2 and 3 (each zip `ProjectCoinRun/Scripts/`) built
  without errors in turn.
- **WK18** gets through. Step 4: deleting the five coins gave `Round won` in `log.read`; 2490 steps gave `Round lost`.
  Section 2 step 5: `WinPanel` active true with `Coins left: 0`, Enter then 120 steps: both panels false, `Coins left: 5`,
  `Time: 39`; with `TimeLimit` 8, `LosePanel` active after 600 steps, Enter restarted with five coins.
- **WK19** gets through. Before polish step 5 the log held the `Script fields ... 'Speed'` warning at every play; after
  `script.remove` and `script.add` of `BallControl` a play of 120 steps logged no warning at all (read with `log.read`
  `after` the last sequence number). The Game.log of the shipped game has none either.
- **WK20** gets through. Without `--resolution` the windowed game opened at 1920 by 1080 and `shot.png` is 1920 by 1080;
  this machine's display scale is 150 % (AppliedDPI 144), as the page's "You should see" says. Exit codes 0 and 0.
- **WK21** gets through. No CREDITS.md in the checkpoint; the step says to create it beside `CoinRun.stproj`. The table's
  rows cover every file under Environment, Models, Sounds, Textures and UI plus `Icon.png`.
- **WK22** gets through. The closing paragraph names The math of moving things (G) and Version control with git (B); the
  built page's strip holds the same two ("Next on your track" once for each track). The site script that shows one of them
  by the chosen track was not run (no browser).

Left over: the stale preview build (above), the missing `script.build` before the first export of a downloaded checkpoint
(WK12), and the missing hint for looking at the window by CLI (WK3). Nothing is left running: the editor was quit and the
exported games ended by themselves.

## Answers (after confirm)

Measured with the 0.8.0 package in a headless editor (`docs-work/walk-final-fix/drive.py`, `results.json`).

### WK12 make/export, What you need
- The confirmer is right: the download of Play, test and debug (`stage-7.zip`, folder `PlayTestDebug`) holds the code
  but no built module. Opened, `script.status` showed no loaded module; `script.build` built it (10.5 s, `loaded` true);
  `scene.save`, then `project.export` with 1280 by 720 answered `assetCount` 23 and wrote `CoinRun.exe`,
  `CoinRun.stgame`, `CoinRun.stpak`, `CoinRunScripts.dll` and `ThirdPartyNotices.md`.
- Change: "What you need" has a new item, "Built scripts": the download holds no built script module and the export
  refuses a scene whose scripts were never built, so build once after opening (**Scripts ▸ Build Scripts** or
  `script.build`) and wait until it has finished. The command tab of the export says a project from the download needs
  `script.build` before `scene.save` and `project.export`.
- The tutorial file is unchanged: its run continues from play-test-debug's end and passed with the pin build and the
  package as it was. (A `script.build` added to its stage 1 also passed; it was taken out again because the reader's
  step is on the page.)
- `tutorials.py run make/export` passed with the pin build and with the package (the page and exercise 1); its stamps
  and downloads were written again, since the tutorials before it in the chain had changed. pagecheck PASS.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK12 make/export, What you need
- Holds. On the unzipped stage-7.zip, `CoinRun.stproj` opened with the scripts unbuilt; `script.build` (waited for) succeeded, `scene.save`, then `project.export` to an absolute folder outside the project at 1280x720 answered `assetCount` 23 and wrote `CoinRun.exe`, `CoinRun.stgame`, `CoinRun.stpak`, `CoinRunScripts.dll` and `ThirdPartyNotices.md`. The What you need item names the step before the export, so a reader needs no guess.
