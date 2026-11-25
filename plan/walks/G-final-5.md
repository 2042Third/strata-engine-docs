# Walk log: track G (persona G0), segment 5, at v0.8.0

Entries walked: `make/script-loop`, `make/scripting-scene`, `make/input`, `make/physics`, `make/sound`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`), headless StrataEditor driven by StrataCLI,
one editor session under the perf lock. One project, `walk-G-final-5/proj/CoinRun`, started from the stage-4 download
of `make/first-script` and carried through all five entries (the checkpoint downloads were used for the script files,
as the pages tell a reader to).

Not walked: the pictures (not fetched); every "In the editor" tab (no window); listening (sound checked through
`audio.state` only: voices, one-shots played and dropped, listener, master volume); the standalone sketches' compile and
run (script-loop Hard, scripting-scene Medium: predicted by hand, the printed outputs agree); the hierarchy-walk and
transform snippets of scripting-scene (no place in a file is named for them); the optional LookCamera and Vehicle
sections of `make/input` (see WK13); the waveform preview of `make/sound`.

## WK1
- Entry: `make/script-loop`; page: same; section: "Before you start" (where the track starts).
- Kind: left the book.
- The page has no "What you need" section and offers no stage download. "Before you start" only links to Your first
  script and Programming from zero III. A reader has no project. I opened `make/first-script`, took its stage-4
  download (project `FirstScript`) and renamed it CoinRun. The command-script files of the downloads are not explained
  on this page: I ran each of their steps through StrataCLI with a small runner of my own (`bind` and `$ref` need
  resolving by hand).

## WK2
- Entry: `make/script-loop`; section: Exercises, Medium.
- Kind: guessed.
- The exercise gives only the mouse path (File, Project Settings, Physics, Timing). The commands are only in the
  solution ZIP (`project.setSettings` with `Scene.Timing`, then `scene.info`). With them the answers match the page
  (120 steps a second, cap 16, step 0.00833 s). The solution leaves the project at 120, so I reset it with the value
  "Scene" - a guess; the page names that value only in the list of choices.

## WK3
- Entry: `make/script-loop`; section: Exercises, Hard (the sketch).
- Kind: left the book.
- "Change it, predict, then run it": the page does not say how to compile and run a single `.cpp` file (the project
  build runs script modules, not programs). I did not run it. My hand prediction (2, 4, 0, 1, 1, 16, 3 steps) equals
  the page's printed output.

## WK4
- Entry: `make/scripting-scene`; section: "Before you start" and the page's first steps.
- Kind: did not match.
- No "What you need" section and no start download. The stage-4 Coin Run differs from the numbers the page uses: the
  Ball sits at (0, 0.5, 6), not (0, 0.8, 2.6) ("Suppose you stored the ball's position at the start, (0, 0.8, 2.6)";
  step 8 moves the ball to (0, 0.8, 1.5) and (0, 0.8, 2.6)), and the hand-placed coins stand at y = 0, not 0.8. The
  steps still work because they set the ball's position with `component.set`.

## WK5
- Entry: `make/scripting-scene`; section: "Place the coins from a script", step "Delete the five hand-placed coins".
- Kind: failed.
- "Run `entity.find` with `{ "tag": "Coin" }` ... and delete them with `entity.delete`" gives no parameters. I tried
  `{"entity": id}`: "Unknown parameter 'entity' for entity.delete (parameters: entities)". Not knowing that, the first
  Play printed "Coins placed: 10" (5 old and 5 new). With `{"entities": [..]}` it printed "Coins placed: 5".

## WK6
- Entry: `make/scripting-scene`; sections "Make the coins bob" to "Collect a coin".
- Kind: guessed.
- Coin.cpp and CoinPlacer.cpp are built from fragments (lines 16-33, 19-24, 26-37, 48-68 and prose such as "add private:
  and the member"). The only whole files are in the final stage-9 download. I assembled the files myself: whether to keep
  the template's `Speed` field in CoinPlacer, where the `FindMeshEntity` helper goes (I made it a private static member),
  and that `ST_SCRIPT_CLASS(CoinPlacer) {}` may stay empty. All built and behaved as the page says (bob 0.092 m at 1 s,
  five coins placed, GoldGlow swapped in within 2 m, the coin gone within 0.7 m). The "Walk the hierarchy" and
  transform snippets say nothing of where they go; I did not run them.

## WK7
- Entry: `make/input`; section: "What you need".
- Kind: left the book.
- It says the start is the end state of Scripts and the scene and "Nothing to import"; no stage download is offered for a
  reader who arrives here. I carried on with my own project.

## WK8
- Entry: `make/input`; section: "Move the ball with the keyboard", step "Play and move the ball".
- Kind: did not match.
- First run of the page's sequence (`play.start`, `input.key W` 60 steps, `component.get`) right after the first build and
  `script.add`: the two Space lines appeared in the log but the ball stayed at (0, 0.5, 6). Three later runs of the same
  commands moved it to z = 2.00 (4 m), as the page says. I could not repeat the first result.

## WK9
- Entry: `make/input`; section: "Add Jump and Boost", step "Add the actions".
- Kind: guessed.
- No command shows how to hold Boost and a direction together. `input.key` taps one key. I found `input.sequence`
  (`"action": "hold"` is refused: "must be press, release or tap") and used two `press` events: the ball went 8 m in 60
  steps, twice the 4 m of walking, as the page says.

## WK10
- Entry: `make/input`; checkpoints 5 and 6, "Look around" and "Switch maps".
- Kind: left the book.
- "Paste the code" for LookCamera and the Vehicle version: the page shows only OnUpdate bodies (lines 19-37 and
  11-28). The fields (`DegreesPerPixel`, `StickDegreesPerSecond`, `m_Yaw`, `m_Pitch`, `Speed`) and the class frame are
  missing and no download holds LookCamera. The download of checkpoint 6 has commands `[]` and a BallControl.cpp equal to
  checkpoint 4. I ran only the `Gameplay/Look` action command (created true) and did not write either script.

## WK11
- Entry: `make/physics`; section: "What you need".
- Kind: did not match.
- "No downloads: you type the scripts", but every script is quoted in pieces (for the first BallControl lines 12-25
  without the fields `PushStrength`, `MaxSpeed`, `m_Push`; later `m_StartPosition`, `JumpImpulse`, `GroundReach`,
  `IsOnGround` placement). A reader cannot type the whole file from the page. The checkpoint ZIPs hold the files; I used
  them.

## WK12
- Entry: `make/physics`; sections "Let the ball fall", "Roll the ball", "Turn the coins into triggers", "Let the ball
  pass a ghost wall", the With a command tabs.
- Kind: failed.
- The commands are written with a step-level `"entityName": "Ball"` (for example `{ "command": "component.set",
  "entityName": "Ball", "parameters": {...} }`). Through StrataCLI `call` this fails: `entityName` inside the
  parameters gives "Unknown parameter 'entityName' for component.set (parameters: component, entities, entity, values)",
  and `"entity": "Ball"` gives "Parameter 'entity' must be an ID (16 hexadecimal digits)". The checkpoint JSON files
  find the entity first and use `$ref`; I ran those. Nothing on the page says the `entityName` form is for command
  scripts only.

## WK13
- Entry: `make/physics`; section: "Let the ball fall", step "Open the scene and select the ball".
- Kind: did not match.
- The editor text sets only the Y position to 3; the command sets `Translation [0, 3, 0]`, which also moves the ball from
  (0, 0.5, 6) to x = 0, z = 0. The later reset key (R) returns to that start, so every run starts at (0, 3, 0).

## WK14
- Entry: `make/physics`; section: "Turn the coins into triggers", step "Replace Scripts/Coin.cpp".
- Kind: guessed.
- The checkpoint's Coin.cpp is another script than the one of the scene page (no glow, fields `BobSpeed`,
  `GlowDistance` gone, spin 120, bob 0.15). The page says "If your Coin differs, keep your own spin and bob and add only
  the function below" and "remove the distance test", but my Coin uses the distance for the glow too. I removed only the
  collect line and the `CollectDistance` field, kept the glow, added `OnTriggerEnter`. Teleporting the ball into the coin
  (0, 1.5, 2.9) removed that coin only, so it works. The stage JSON also adds a Sphere Collider without checking for one.

## WK15
- Entry: `make/physics`; section: "Roll the ball with a force", step "Build and attach" (and later builds).
- Kind: did not match.
- "You should see: the build finish without problems". The Console also holds "Script fields: script 'BallControl' has no
  field 'Speed'; the stored value is ignored" on every play after BallControl lost `Speed`. Nothing on the page says to
  remove the old field value from the Script component.

## WK16
- Entry: `make/sound`; section: "Add music and a volume option", step "Add a VolumeKeys script".
- Kind: guessed.
- Only the OnUpdate body is given ("Code it with the lines below"). I wrote the class frame, the include and an empty
  `ST_SCRIPT_CLASS(VolumeKeys) {}` myself; it built, `Minus` took `masterVolume` from 1 to 0.9 and two `Equal` taps gave
  1.1 as the page says (the checkpoint file differs only by a comment).

## WK17
- Entry: `make/sound`; section: "Hear your first sounds".
- Kind: left the book.
- The "You should see" lines are about hearing (a chime that repeats, fading with distance, left and right speaker) and a
  waveform picture. Through the CLI I could check only `audio.state`: voice playing true, the listener is the Ball after
  the Audio Listener step, one-shots played 1 and dropped 0 after collecting a coin and 1 thud from the Bump script.
  With `RequestLoad` commented out the first coin still sounded (played 1, dropped 0), as the page allows.

## Answers

### WK1
- Fixed on `make/script-loop`. Why: a concept page needs no project to read, but exercise 2 uses one and the page did
  not say which; a walker who starts the segment here has none. The command files of the downloads are the subject of
  `start/how-to-read` ("To run a command yourself"), not of this page.
- Change: the Exercises open with a paragraph: only exercise 2 uses a project, Coin Run or the project at the last
  checkpoint of `make/first-script` (its box offers it as a download).

### WK2
- Fixed on `make/script-loop` and its exercise file. Why: the answer named the commands only through the solution, and
  nothing said to return the project to the scene's own rate, which the later pages assume (60 steps, cap 8).
- Change: the answer says to choose **Scene** for **Fixed Rate** afterwards, and that the file does the same with
  `project.setSettings` `{ "section": "Scene.Timing", "reset": true }`. The file now ends with that reset and checks
  with `scene.info` that the source is `scene` again, at 60 steps and a cap of 8.

### WK3
- Fixed on `make/script-loop`. Why: the page asked to run a sketch without saying what that needs; `make/transforms-units`
  says it (WK26 of segment 2) and this page did not.
- Change: the Exercises' opening paragraph says that exercise 3 needs a C++ compiler (`start/install`), links
  `basics/build` for compiling one file, and says to work the steps out by hand without one. The walker's hand
  prediction equals the page's output. The same sentence went into the Exercises of `make/scripting-scene` (its
  exercise 3 is a sketch too).

### WK4
- Fixed on `make/scripting-scene`. Why: the page's start state named no download, and its example of a stored position
  used (0, 0.8, 2.6), which is no position the ball has: Coin Run's ball starts at (0, 0.5, 6) (the input page's file
  checks the same start). The coins' 0.8 is the height `CoinPlacer` places them at, so it stays; the steps that move
  the ball set its height by command.
- Change: "Before you start" gives the ball's start (0, 0.5, 6) and the download at the last checkpoint of
  `make/first-script`; step 5's example stores (0, 0.5, 6) and moves the ball to (3, 0.5, 6).

### WK5
- Fixed on `make/scripting-scene`. Why: the tab named `entity.delete` without parameters; its one parameter is the list
  `entities` (the tutorial file already used it).
- Change: the tab gives `{ "entities": [ "<ID 1>", ... ] }`, says that `entity.find` answers the IDs as a list and
  that the answer names them under `deleted`; "If you do not see it" names `Coins placed: 10` and its cause.

### WK6
- Fixed on `make/scripting-scene`. Why: the steps showed only functions and described the rest in prose; the stage files
  hold the whole scripts. The walker's assembly built and behaved as the page says.
- Change: step 1 quotes `Coin.step1.cpp` whole in two parts (lines 1-20, 22-43); step 3 quotes the whole
  `CoinPlacer.step3.cpp` and says to replace the template's text, `Speed` field included, and that the empty
  `ST_SCRIPT_CLASS` block is right; step 4 quotes the positions (lines 7-14) and the rest of the file (26-43) with
  where each part goes; step 7 says that `FindMeshEntity` is a `static` function below `private:`. Steps 6 and 9 say
  that their snippets show the calls only and go into no file, and step 9's "You should see" is the five children of
  `Coins` while the game plays, which its tab reads (`entity.get`). The Result says that its download holds both files.

### WK7
- Fixed on `make/input`. Why: "What you need" offered no download for a reader who arrives without the project.
- Change: the first item gives the ball's start (0, 0.5, 6) and points to the download in the box under the Result of
  `make/scripting-scene` (a how-to offers its end state there).

### WK8
- Fixed on `make/input`. Why: the tab ended with `play.stop` and read nothing, so a reader adds the read where the tab
  ends; after `play.stop` the playing copy is gone and `component.get` reads the edited scene, z = 6. That is the
  walker's first result; reading during play gave z = 2.0 every time, as the tutorial file's check does (z 1.999 in the
  stamped runs). The walker's log puts `component.get` after the tap but does not say where `play.stop` stood, so this
  is the cause that fits what it saw, not one it showed.
- Change: the tab reads the ball with `component.get` before `play.stop`, and `log.read` after the Space tap, in the
  file's order; it says why a read after **Stop** gives z = 6. "You should see" gives about (0, 0.5, 2), and "If you do
  not see it" names a ball back at z = 6.

### WK9
- Fixed on `make/input` and its tutorial file. Why: the section had no play step for Jump and Boost at all, and no
  build step for its file.
- Change: a new steps block builds the stage's file and plays: the tab holds LeftShift with `input.key`
  `"action": "press"`, taps W for 60 steps, releases Shift with `"action": "release"`, reads the ball, taps Space and
  stops. "You should see": about 8 m, z from 6 to about -2, and one `Jump pressed`. The quote of `BallControl-4.cpp`
  now starts at line 1 (the field `BoostFactor`), and the text names the end of the file. Stage 4 of the file runs the
  same and checks `BoostFactor` 2, z within 0.6 of -2 and `Jump pressed`.
  In the pin build's run the ball ended at z = -2.001.

### WK10
- Fixed on `make/input`. Why: the two optional sections showed only `OnUpdate` and gave no steps for the Vehicle map;
  by design neither script is in a checkpoint, so the page is the only source.
- Change: `LookCamera.cpp` is quoted whole in three parts (lines 1-17, 19-37, 39-48), with a command tab that builds,
  attaches the class to `Main Camera`, holds the right stick for 30 steps and reads `entity.get` with `world`. The
  Vehicle section quotes `BallControl-vehicle.cpp` from line 5 to 28 and names lines 1-3 and the end; a new steps block
  adds the map with `"enabled": false` (a map enabled at start adds Drive to Move and runs the ball at three times the
  speed) and its action, builds and plays V then W (8 m). The text says the checkpoint's `BallControl.cpp` is the Boost
  version to put back. Both scripts were run with the pin build from the input end state (a scratch exercise file,
  removed afterwards): the camera's `world.rotation.euler` went from (-55.0, 0, 0) to (-55.0, -60.0, 0) after 30
  steps of the right stick at 1; the vehicle version moved the ball to z = 2.000 in 60 steps of W, and to z = -2.001
  after V. To stay within size L (6,500 words) some sentences elsewhere were shortened (the
  gamepad's opening, the mistakes paragraph, the hold or toggle choice, the device-or-action paragraph).

### WK11
- Fixed on `make/physics`. Why: "No downloads: you type the scripts" was wrong twice: every checkpoint has downloads, and
  the quotes left out the fields and members.
- Change: the item says that the page quotes the scripts whole, in parts, and that each checkpoint offers the project
  and the editor commands. Step 2's `BallControl.cpp` is quoted whole (lines 1-25, 26-34); step 3's in its parts (lines
  1-17, `OnUpdate` 19-33, the unchanged `OnFixedUpdate` 35-42 named, 43-61), and the editor tab names the order. The
  page's `time` is 70 (the reading floor with the longer code).

### WK12
- Fixed on `make/physics` (and the same tabs of `make/sound`). Why: `entityName` is a key of the book's tutorial files,
  which `tutorials.py` turns into an `entity.find` and an ID; no engine program reads it, and the page showed it to
  readers (segment 3's WK7 named these pages for their fixers).
- Change: every tab passes `"entity": "<the ID of Ball>"` in the parameters, and the first one says to take the ID from
  `entity.find` with `{ "name": "Ball" }`. On `make/sound` the Hum and Ball tabs do the same.

### WK13
- Fixed on `make/physics`. Why: the editor tab set only Y; the command and the tutorial file set (0, 3, 0), from which
  the page's later places (the wall at x = 4 "to the right of the ball", the reset) follow.
- Change: the editor tab sets the Translation to 0, 3, 0 and says that the ball moves from z = 6 to the middle of the
  level, 3 m up.

### WK14
- Fixed on `make/physics`. Why: the checkpoint's `Coin.cpp` is a shorter coin than the scene page's (no glow, turn 120,
  bob 0.15), and the page offered only a vague "keep your own".
- Change: the step quotes the checkpoint's `Coin.cpp` whole (lines 1-17, 19-42), says how it differs from the scene
  page's coin, and gives the three edits that keep the glow instead: delete `CollectDistance` and its field line, delete
  the collect test's two lines, add `OnTriggerEnter`. That is what the walker did, and its coin was collected by the
  trigger. The checkpoint keeps the shorter coin, which the later pages' files build on.

### WK15
- Fixed on `make/physics` and its tutorial file; engine fault noted. Why: the input page's `script.add` stored `Speed` 4
  on the ball; the new class has no `Speed`, so each play warns
  (`Strata/src/Strata/Scripting/ScriptSystem.cpp:756-761`). The Inspector draws only the class's fields and
  `script.setField` refuses a field the class lacks, so only removing the script clears the value. The earlier runs'
  reader copies of stages 2 and 3 logged the same warning.
- Change: step 2 is "Build, then attach the script to the ball again": it says why the warning comes, the editor tab
  removes `BallControl` with the cross and adds it with **Add Script...**, the tab runs `script.remove` and
  `script.add`, and "You should see" says a play logs no warning. Stage 2 of the file does the same and checks that a
  120-step play logs no warning. Notes: `## Engine`.
  In the pin build's run the play logged no warning.

### WK16
- Fixed on `make/sound`. Why: the page showed `OnUpdate` as pseudocode; the tutorial's `VolumeKeys.cpp` is 22 lines.
- Change: the step quotes the whole file (lines 1-22, with callouts on the steps and the empty registration), and both
  tabs say to replace the new file's text with it.

### WK17
- Rejected: no fault of the page. The walker had no listening and no window; the page lists a sound output under What
  you need, and its "You should see" lines are what a reader with speakers hears. The command tabs give the checks a
  command can make (`audio.state`: the voice playing, the listener, one-shots played and dropped), and every value the
  walker read matched them, also the allowed case with `RequestLoad` commented out.

### Runs
- Pin build (`build/windows/bin/Release`) and the official 0.8.0 package (`Strata-0.8.0-windows-x64.zip`), work folder
  `docs-work/walkfix-G5/runs/`: `make/script-loop` (exercise 2), `make/scripting-scene` (9 stages, exercise 2),
  `make/input` (6 stages, exercise 2), `make/physics` (5 stages, exercise 1) and `make/sound` (4 stages, exercise 1) all
  passed.
- The package's first run of `make/scripting-scene` failed in the reader's copy of stage 6: from a fresh editor, the 47
  paused steps ran before the coin prefab had loaded, so `entity.find` found no coin (`Coins placed: 5` came after).
  The file now starts stages 6, 8 and 9 with a play that waits for `Coins placed: 5`; both builds then passed. The
  pages that start from it were run again for current stamps.
- No integrator patches are listed in this log.

## Confirm

Reader G0, headless package editor 0.8.0 driven by StrataCLI, one editor session under the perf lock, work folder
`docs-work/walk-G-final-5/c`. The built book at port 4329 is older than the book: its pages of `make/scripting-scene`,
`make/input`, `make/physics` and `make/sound` still show the text before the fixes (no "Coins placed: 10", no
`component.get` before `play.stop`, no "has no field"), only `make/script-loop` is current. I read the fixed pages from
`src/content/docs/make/*.md` (the checkout's source, code quotes included) and walked from them; the preview needs a
rebuild before a reader of it sees the fixes. Not walked: pictures, "In the editor" tabs, listening.

| ID | Result | What I did |
| --- | --- | --- |
| WK1 | Fixed | The Exercises' opening names the project (Coin Run, or the last checkpoint of first-script, offered as a download). Opened it from that download, nothing else needed. |
| WK2 | Fixed | The solution's `project.setSettings` gave 120 steps a second, cap 16, step 0.00833 s; the page's reset (`"reset": true`, or Scene for Fixed Rate) gave source `scene`, 60 steps, cap 8, as the page says. |
| WK3 | Fixed | The paragraph says a C++ compiler is needed (links to the install and build pages) and that the steps can be worked out by hand; my hand result (2, 4, 0, 1, 1, 16, 3) equals the page's output. I did not compile the sketch. |
| WK4 | Fixed | "Before you start" names the ball's start (0, 0.5, 6) and the download; the project at that download has the ball there and five hand-placed coins. The step 5 example (0, 0.5, 6) to (3, 0.5, 6) matches. |
| WK5 | Fixed | `entity.find` with the tag, then `entity.delete` with `{ "entities": [ ... ] }`: the answer names the five IDs under `deleted`; the play printed `Coins placed: 5`. |
| WK6 | Fixed | Coin.cpp (two parts) and CoinPlacer.cpp (step 3 whole file, step 4 positions and second part) assembled without guessing; both built with no warning. Five coins placed, GoldGlow swapped in at 1.5 m (not at the start, 3 m away), the coin gone at 0.4 m. One small gap: the Coin of steps 5, 7 and 8 is still assembled from fragments (field lines, three `OnCreate` lines, `FindMeshEntity` below `private:`, the test's lines); the page's words say where each goes and it built the first time. |
| WK7 | Fixed | "What you need" gives the ball's start and the download under the Result of the scene page; the Result's project holds both scripts and the ball at (0, 0.5, 6). |
| WK8 | Fixed | Step 5's tab with `component.get` before `play.stop`: z = 2.001 (page: about 2), the two Space lines in the log; a read after Stop gave z = 6, as the page says. |
| WK9 | Fixed | Stage 4's file built; the Boost tab (press LeftShift, W for 60 steps, release, read, Space): z = -2.002, one `Jump pressed`. |
| WK10 | Fixed | LookCamera built from the page's three parts and attached to `Main Camera`; `entity.get` with `world` read rotation.euler (-55.0, -62.0, 0) after 30 steps of RightX 1 (page: about -60; a hair over). The Vehicle version (lines 5 to 28 with lines 1 to 3 and the end) with the map added with `"enabled": false`: W gave z = 2.00 (4 m) and V then W gave z = -2.00 (8 m). |
| WK11 | Fixed | I typed BallControl (step 2, two parts; step 3, three parts plus the named unchanged `OnFixedUpdate`) and Coin (two parts) from the page; all built first time. |
| WK12 | Fixed | Every tab ran with the Ball's ID from `entity.find`: no parameter error. |
| WK13 | Fixed | The tab sets the Translation to 0, 3, 0; after the fall the ball rests at (0, 0.5, 0); R teleports to the start and the ball falls from there. |
| WK14 | Fixed | The page's shorter Coin (two parts) built; a coin placed by CoinPlacer was collected by `OnTriggerEnter` when the ball rolled into it (5 coins to 4). `component.add SphereCollider` on the instance gave no error. |
| WK15 | Fixed | `script.remove` and `script.add` of `BallControl` in step 2: no `has no field 'Speed'` warning in any later play. |
| WK16 | Fixed | VolumeKeys.cpp from the page's whole listing built; `Minus` took `masterVolume` from 1 to 0.9 and two `Equal` taps to 1.1. |

Side notes (not WK entries):
- Stale preview, above: it hides every fix from a reader of the served build.
- Replacing a script by copying the download's file over an existing one keeps its 1980 date, and the build then does
  not compile it (`script.build` answers success with `reloaded: false`; the old code ran, so the Boost tab gave 4 m and
  no `Jump pressed`). Pasting the text, or touching the file, builds it. The pages say "paste", so a reader who pastes
  is fine; one who copies the file in a file browser can hit this.
- The first play of physics step 1 (`"build": false`, project not yet built) logs the warning that the scene has Script
  components and no module is loaded; the page does not mention it.
