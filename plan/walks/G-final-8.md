# Walk log: track G (persona G0), segment 8, at v0.8.0

Entries walked: `make/script-builds`, `make/characters-cameras`, `make/animation`, `make/menus`, `make/levels-saves`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`); one StrataEditor session (headless) driven by
StrataCLI under one perf-lock hold (it waited behind another walker once); projects in `walk-G-final-8/proj` (CoinRun-s4,
and CharactersCameras, which carried Characters and cameras, Animation, Menus and Levels in turn).

Not walked: clicks, menus, drags and the Inspector (everything through commands, read back with `script.get`, `component.get`,
`animation.info`, `ui.layout`, `log.read`; pictures through `viewport.capture`, two looked at). Each tutorial's checkpoints were
replayed by copying a checkpoint's files and running its commands file, in place of typing every step's command; the
"With a command" tabs were used directly only where noted. Not done: the Medium and Hard exercises (answered by reading;
only the Basic exercise of `make/script-builds`, the Medium one of `make/characters-cameras` and the Basic one of
`make/animation` were run), the exercises of `make/menus` and `make/levels-saves`, the loading bar and the `SubScene` room
(compiled only, the room did not run), the IDE half of `make/script-builds`, sounds (not heard), the pictures of the pause
menu (state read, not looked at).

## WK1
- Entry: `make/script-builds`; page: same; section: "Before you start".
- Kind: left the book.
- The page needs "a project whose scripts the editor built once" and offers no download or stage. I took Project: Coin Run,
  checkpoint 4 (`make/project-coin-run`, a side step), opened it with `project.open` and ran `script.build` once (14 s) so that
  `CMakePresets.json` and `.strata/Scripts` existed. Without that build `cmake --preset strata` would say there is no preset.

## WK2
- Entry: `make/script-builds`; section: "Build from a terminal".
- Kind: did not match (small).
- All "You should see" lines matched (cmake 4.2.2, `Build files have been written to ... .strata/Scripts/IDE`, the dll in
  `.strata/Scripts/Bin`, Console `Reloaded script module 'CoinRunScripts' (9 classes)`). But the compile output names a
  folder `Dist` (the library goes to `.strata/Scripts/IDE/Dist/`): the page never says that the preset builds the
  configuration Dist, so it looked unexplained.

## WK3
- Entry: `make/script-builds`; section: "Exercises, Basic" and its worked solution.
- Kind: did not match.
- The page says the Console shows `Triple of 14 is 42` first and `56` after the change to 4. I copied the solution's folders
  into the project and ran its `stage-1.commands.json`: its `Triple.cpp` already holds `value * 4`, so the first play already
  printed `Triple of 14 is 56` and the "predict 42, then change" part could not be seen. The commands file ran without a failure.

## WK4
- Entry: `make/characters-cameras`; page: same; section: "What you need".
- Kind: guessed.
- "The starting checkpoint Course" has no download on the page; the only downloads are Checkpoints 1 to 10, and Checkpoint 1
  already includes the player. I made a project with `project.create` (template `basic3d`; the page does not name the
  command, and it first refused because the Coin Run project had unsaved changes, so I passed `force`) and ran the commands of
  Checkpoint 1, which build the course (steps, ramps, wall, ledge, crate, platform), the `Gameplay` input map and the player.
  It worked, but the page never says that these commands make the course. The ground is the template's grey, not the "dark
  stone" of the page's pictures (the zip carries a `Ground.stmat` that the commands do not apply).

## WK5
- Entry: `make/characters-cameras`; sections "Make the player" to "Look from a second camera"; Checkpoints 2 to 10.
- Kind: did not match (once), failed (once).
- To run a stage I had to copy `Scripts/` from the checkpoint zip first, then run its commands file; the page says only
  "Copy Scripts/... from the checkpoint". All "You should see" lines I could read back matched: player at height 0 after 60
  steps; W moved it away from the camera and S turned the body 180 degrees; a jump to about 1.22 m with GroundStateNumber 0 on
  the ground and 3 in the air; Step03 climbed (y 0.295), ramp 40 climbed, the foot of ramp 50 stopped it with state 0;
  FollowCamera fields `ArmReturnSharpness 6`, `Distance 6.5`; Platform `Travel (6, 0, 0)` and `Period 8`.
- Checkpoint 9: the first time I ran its commands file, `script.setField` for `Loop` on Platform answered a -32602 parameter
  error (I did not read the message); the same call by hand, and the whole file run again, worked. I could not reproduce it.
- The "With a command" tab of the play steps only starts play (`play.start`); a reader who reads only the tab has no command
  that presses a key. The commands files use `input.key`, which the tab does not name.

## WK6
- Entry: `make/characters-cameras`; section: "Make the camera follow", step "Slow the steps to see the problem".
- Kind: did not match.
- "At the start the camera stands 7 m behind the player": the script put it at z 8.58, y 3.89 with the player at z 2 (an arm
  of 6.5 m, the later section says 6.5; this section's text says 7).

## WK7
- Entry: `make/characters-cameras`; exercises.
- Kind: guessed (not run).
- The Hard answer by hand (0.56 s and 0.28 s) matched the page; I did not play it. The Medium worked solution
  (`exercise-2.zip`: a `PlayerController.cpp` and a commands file) ran: the player rose to 2.15 m on a second press and a third
  press did nothing, as the page says ("about 2.2 m").

## WK8
- Entry: `make/animation`; page: same; section: "What you need".
- Kind: guessed.
- The page says "the checkpoint download of this page adds the robot model ... the sounds and the controller", but its first
  steps (`animation.info`, `asset.place`) need those files in the project already, and the page does not say which zip to
  open. I took Checkpoint 1's zip, copied only its `Models`, `Sounds` and `Animations` folders into my project (not its
  scene, which would have replaced my course) and ran Checkpoint 1's commands.
- The first `animation.info` listed `Dance` first, as the page says; `Idle`, `Walking`, `Running` and `Jump` exist.

## WK9
- Entry: `make/animation`; section: "Hold a flag", Checkpoint 7.
- Kind: failed (once).
- The page says to import `flag.glb` from the release's `Samples/ThirdPerson/Assets/Models/Platformer/` with its Textures
  folder. I used the zip's copy; `asset.place` on `Models/flag/flag.glb` right after the copy answered a -32602 error (the
  asset was not scanned yet) and the commands file went on with a missing id and stopped. I deleted the extra entities and ran
  it again a little later; it worked. The page says "wait for the import bar" only for the editor, and names no way for a
  command user to wait. In a capture the robot held the flag in its hand (the pole is tilted, not upright, in that pose).

## WK10
- Entry: `make/animation`; sections "Give it a controller" to "Add footsteps" and the Basic exercise.
- Kind: did not match (small).
- Values matched: state `Idle` with `normalizedTime` past 1 ("Time counts up past 1.00"), `Speed 3.0` and state `Walk` while W
  was held, `Jump` after Space and back to `Idle`, parameters `Grounded` and `Jump`, Footsteps `Steps` 6 after 150 steps of
  walking. The page's "Time" is `normalizedTime` in `animation.info`, and `animation.info` still shows `clip` as the old
  Clip while a controller plays; a reader may take that for a mistake.
- The Crouch exercise's commands file contains `edit.undo`; on a project with a long undo history that undoes an earlier step
  of the course, not only the exercise's change (its history list began with "Create 'Step03'").

## WK11
- Entry: `make/menus`; page: same; section: "What you need".
- Kind: guessed.
- "Download the checkpoint of its last step, or continue your own project": I continued my project. The page names six script
  files "which come with the checkpoints of this page"; I copied each stage's `Scripts/` and `Assets/` (except scenes) from its
  zip before running its commands file. Checkpoint 1's commands then failed at `script.create` ("The project's scripts declare
  'MainMenu' already"), and Checkpoint 4's at `prefab.create` ("already exists", the zip held the prefab) and then at
  `prefab.apply` ("not part of a prefab instance"). A reader who copies the zip's files and also runs the commands file gets
  these errors; the page does not say to do one or the other.

## WK12
- Entry: `make/menus`; sections "Make a main menu that works" to "Add credits and a sign" (Checkpoints 1 to 7).
- Kind: failed (once).
- Checkpoint 2's commands start with `scene.open` of the menu and failed (-32005, unsaved changes) because Checkpoint 1's
  commands end with unsaved changes (they do not save at the end); I saved by hand and ran it again. Every other stage ran.
- Matches: the Play and Quit clicks changed the running scene to Main and ended play; Down, Down, Enter ended the game;
  `Gameplay/Pause` was created; the window toggles `IsOn` false and true after a click; the slider value 0.5; the rebinding row
  text went `Key/Space, Gamepad/A`, then `Press a control...`, then `Key/K` (checked by hand).
- The "Play the scene" step names `input.click` and `play.step` but not their parameters; I found them with `StrataCLI list`.

## WK13
- Entry: `make/levels-saves`; page: same; section: "Before you start" (there is no "What you need").
- Kind: guessed.
- It says "Download the checkpoint of its last step" and gives no link; I used my project from Menus (Checkpoint 7's files).
  The page has no commands file and no stage: only the worked solution.

## WK14
- Entry: `make/levels-saves`; section: "Build it", steps 1 and 2.
- Kind: did not match.
- Step 1 says "move a few coins and the goal"; step 2 says "The goal is a box trigger at the end of the course". The course
  of Menus has no coins and no entity named Goal (`entity.find` returned nothing), and the Player has no Tag component, so
  the listing's `GetTag() == "Player"` can never be true. I made a Goal (BoxCollider and a static Rigid Body with Is Trigger)
  and a Tag `Player` myself, a guess, before the switch worked.
- The `NextLevel` listing has no `#include`, `using namespace Strata;` or `ST_SCRIPT_CLASS`/`ST_SCRIPT_FIELD`, so the field
  `Next` it speaks of cannot exist as shown; I added the lines from MainMenu.cpp and it compiled, `script.add` took `Next`,
  and walking into the goal switched play to MainMenu (`play.state`).
- `scene.saveAs` took `path` as the page shows; `scene.open` wants `scene`, not `path` (I tried `path` first).

## WK15
- Entry: `make/levels-saves`; section: "Build it", last step ("Save a best time ...").
- Kind: did not match.
- "You should see ... a file `best-time.txt` in `.strata/Saves`": the folder holds `best-time.txt.save` and
  `checkpoint.txt.save`. The values were right: 1250 read back; the checkpoint came back as 12.5, 0.4, -3.1 with 7 coins; the
  texts `abc` and `12:30` gave 0 with no crash. The listings needed `#include <optional>` and `<string>` added.

## WK16
- Entry: `make/levels-saves`; section: "Build it", the loading bar and the room.
- Kind: left the book.
- `project.setExportSettings` with `loadingScene` took the scene's path and answered with its handle. The door listing
  compiled (with includes and registration added) but I did not run the room or the bar: the page names no commands to make
  the Filled image bar or the door's trigger.

## Answers

Checks were run with the official 0.8.0 package under the perf lock, in `docs-work/walkfix-G8` (`verify.py`, results in
`results.json`, projects in `run/`, made from the checkpoint zips of `characters-cameras` 9, `animation` 9 and `menus` 7).
The changed tutorial files (`script-builds` exercise 1, `animation`, `menus`) were run with the pin build and with the
package (`runs/`). The log lists no patches under "## Built by the integrator".

### WK1
- Fixed on `make/script-builds`. Why: the page has no tutorial of its own and "Before you start" named no project to
  download.
- Change: the first item names the reader's Coin Run or Checkpoint 4 of `make/project-coin-run` (linked to "Ship the
  finished game"), opened with **File ▸ Open Project...**, and one **Ctrl+B** so that the editor writes
  `Scripts/CMakePresets.json`.

### WK2
- Fixed on `make/script-builds`. Why: the editor builds the scripts in the configuration the engine was built with
  (`settings.Configuration = ST_SCRIPT_BUILD_CONFIGURATION`, `StrataEditor/src/Editor/ScriptBuild.cpp:402`); the release
  package is the shipping build, so the preset builds `Dist`. The page never said so.
- Change: "Build from a terminal" says that the preset builds the engine's configuration, `Dist` for the installed
  Strata, so the compile lines name a folder `Dist` inside `.strata/Scripts/IDE` (an engine built in `Release` builds
  `Release`); step 4's "You should see" names the `Dist` lines.

### WK3
- Fixed on `make/script-builds`, its tutorial file and the tool. Why: the solution's download held each path once, with
  its last copy (`solution_files`), so `Libraries/Triple/Triple.cpp` already multiplied by 4 when the reader's commands
  started, and the one commands file built and played twice with no point between at which a reader could change it.
- Change: `exercise-1.tutorial.json` has two stages: stage 1 copies the factor 3, builds, plays and checks
  `Triple of 14 is 42`; stage 2 copies `TripleFour.cpp` over `Triple.cpp`, plays the old module (42), builds while
  playing (`reloaded` true), starts again and checks `Triple of 14 is 56`. `solution_files`
  (`tools/booklib/tutorials.py`) now keeps the first stage's copy of a path that a later stage copies again and puts the
  later copy under `stage-<step>/` (test in `tools/tests/test_tutorials.py`, seen failing first; this is the only
  exercise of the book that copies a path twice). The zip now holds `Libraries/Triple/Triple.cpp` (factor 3),
  `stage-2/Libraries/Triple/Triple.cpp` (factor 4) and the two commands files; the answer says what to copy before
  each. Passed with the pin build and the package.

### WK4
- Fixed on `make/characters-cameras`. Why: "What you need" named a starting checkpoint "Course" that has no download;
  the tutorial starts from the Basic 3D template and Checkpoint 1's commands build the course, the input map and the
  player. The "dark stone" of the pictures' alts is the template's own `Ground.stmat` (base colour 0.16, 0.15, 0.14),
  which every Basic 3D project has: the walker's capture shows the same dark grey ground, with no stone.
- Change: the course item says it is a Basic 3D project with its dark grey ground and that Checkpoint 1 holds it with
  the first section's player; a paragraph says what each checkpoint's two downloads are and how to build the course
  yourself (**New Project**, or `project.create` with `basic3d`, then Checkpoint 1's commands). The five alts of
  `src/content/figures/make/characters-cameras.json` say "dark grey ground".

### WK5
- Fixed on `make/characters-cameras` (copying, `input.key`); the `-32602` of `script.setField` was not reproduced.
- Why: the page did not say that a commands file writes no file, and the play steps' tabs only started play.
- Change: the paragraph after "What you need" says that the commands write no file, so the scripts a section names are
  copied from that checkpoint's project first. The walk and jump steps' tabs give the commands the file runs:
  `play.start` paused, `input.key` with its `key` and `steps`, `play.step`, and what `component.get` and `script.get`
  then show.
- `script.setField` of `Loop` right after `play.stop`, twelve times on checkpoint 9, and right after a fresh
  `script.build`, all answered without an error (`results.json`, `cc-setField-*`). The step's "If you do not see it"
  now says: if `script.setField` answers that the field is unknown, run `script.build` and the command again.

### WK6
- Fixed on `make/characters-cameras`. Why: the arm of `step5/FollowCamera.cpp` is 7 m long and slopes down by 20
  degrees (`Pitch` -20), so the camera stands 6.58 m behind and 2.39 m above the pivot: Z 8.58 and Y 3.89 for a player
  at Z 2, as the walker read. "7 m behind the player" was the arm's length, not the distance along the ground; the
  6.5 m arm is the later section's.
- Change: "You should see" says the camera stands at the end of its 7 m arm, which slopes down by 20 degrees: 6.6 m
  behind the player (Z 8.6 for a player at Z 2) and 3.9 m above its feet.

### WK7
- Rejected. The walker's Hard answer by hand matched the page (0.56 s and 0.28 s), and the Medium solution ran as the
  page says (2.15 m, "about 2.2 m"; a third press did nothing). Nothing failed or differed; the Hard exercise's "Check
  by playing" is the reader's own play.

### WK8
- Fixed on `make/animation` and its tutorial file. Why: stage 1 imported the robot and the step sounds in `setup`,
  which the reader's copy leaves out, and the page said only that "the checkpoint download of this page adds" them.
- Change: the first section starts with a new step 1 that imports the release's `Models/Robot` and `Sounds/Footsteps`
  folders (editor tab: as in Assets; command tab: two `asset.import` lines with `<release folder>`); the stage's
  commands now hold the same two imports. "What you need" says that only this page's downloads hold
  `Animations/Player.stanimator` and to copy the folder `Assets/Animations` of Checkpoint 1's project (with the `.meta`
  file) and nothing else; a paragraph says what the two downloads are, that a commands file writes no file, and to
  replace `<release folder>`. The later steps of the section moved by one.

### WK9
- Fixed on `make/animation` and its tutorial file. Why: stage 7 imported `flag.glb` in `setup`, so the reader's copy
  started with `asset.place` on a model the reader had to copy by hand. A file copied into `Assets` is found a moment
  later: checked, `asset.place` at once answered `Parameter 'asset': no asset 'Models/flag2/flag.glb'`; `asset.info`
  answered the same once and found the file 0.6 s later, and the place then worked.
- Change: the command tab imports the file from the release with `asset.import` (it answers once the import is done)
  before `asset.place`, and says that a file copied by hand is placed once `asset.info` with its path answers without
  an error. Stage 7's commands hold the import.

### WK10
- Fixed on `make/animation`. Why: the page named the Inspector's **Time** and **State** but not the fields of
  `animation.info`; its `clip` is the component's **Clip** (checked while the controller plays: `clip`
  `D2261DDA1C78AC15`, the component's, with `state` `Idle` and `normalizedTime` 0.59 after 120 steps).
- Change: the command tab of "Press Play" says that `animation.info` with the Robot's `entity` answers `state`, and
  `normalizedTime` for **Time**, and that `clip` still names the unused **Clip**.
- The `edit.undo` of the Crouch solution: `animation.setController` records one undo step ("Edit Player"), and
  `edit.undo` undid that step only; the controller was back at 3 parameters, 4 states and 7 transitions
  (`results.json`, `an-history-*`, `an-undo`). The answer now says that the file's one `setController` is one undo
  step, that its `edit.undo` removes only that latest step, and that `edit.history` still lists the earlier steps.

### WK11
- Fixed on `make/menus` and its tutorial file. Why: a checkpoint's zip and its commands make the same things, and the
  page did not say to use one or the other; stage 1's commands also could not run as one file, since they ran
  `script.create` and then needed `MainMenu.cpp` copied in the middle.
- Change: a paragraph after "What you need" says to use one download or the other, and with the commands to copy only
  the section's one script file, since the commands refuse a scene or prefab that already exists. Stage 1 copies
  `MainMenu.cpp` before its commands and no longer runs `script.create`; the page's command tab says to save the
  listing as `Scripts/MainMenu.cpp`, then `scene.save` and `script.build`. "What you need" links Checkpoint 9 of
  `make/animation`.

### WK12
- Fixed on `make/menus` and its tutorial file. Why: the runner saves between stages, the reader's commands did not, so
  Checkpoint 1's commands left the menu unsaved and Checkpoint 2's `scene.open` failed; the play steps named the input
  commands without their parameters.
- Change: every stage's commands end with `scene.save`. The play steps' tabs of the main menu, the keyboard, the
  settings screen, the rebinding screen and the name field give the commands with their parameters (`input.click` with
  the `entity`, `input.key` with the `key`, `input.type` with the `text`, `play.step` with the `steps`) and the
  read-back. Passed with the pin build and the package. To keep the page within its size (L, 6,500 words) a few
  sentences went (a worked fade example, two lead-in sentences, the keyboard-layout aside's last sentence).

### WK13
- Fixed on `make/levels-saves`. Why: "Before you start" asked for "the checkpoint of its last step" with no link, and
  the page did not say that it has no downloads of its own.
- Change: the first item links Checkpoint 7 at the end of "Add credits and a sign" of `make/menus`; a line says that
  the page offers no downloads and that each step says what to make and gives the code.

### WK14
- Fixed on `make/levels-saves`. Why: the page was written for Coin Run's coins and goal, but it follows `make/menus`,
  whose course has neither a goal nor a tagged player; the `NextLevel` listing was a pseudocode fragment; and the tab
  did not show that `scene.open` takes `scene`.
- Change: "Build it" now starts with a step that makes the goal (an entity `Goal` at (0, 1, -8), scale 2, a cube mesh, a
  Box Collider and a static Rigid Body with Is Trigger) and gives `Player` the tag `Player`; step 2 saves `Level2` and
  moves its goal to (6, 1, 2); step 3 shows the whole `NextLevel.cpp` (the exercise's file, as an excerpt with
  callouts) and attaches it to both goals (Level2's to the main menu, Main's to `Level2`), with `scene.open` and its
  `scene`. The description, the scene-flow sentence and the Result say "the course", not Coin Run.
- Checked on Menus' checkpoint 7 with the page's commands: holding W for 240 steps in `Main` switched play to
  `Level2`, and holding D for 180 steps in `Level2` switched it to `MainMenu`; `scene.open` with `path` answers
  `Unknown parameter 'path' for scene.open (parameters: force, scene)`.

### WK15
- Fixed on `make/levels-saves`. Why: a save file is stored as its name plus `.save`
  (`Strata/src/Strata/Core/SaveFiles.cpp:18` and `:52`), which the page did not say; the step did not say where the
  functions go and which headers they need.
- Change: the section "Save files" says that `best-time.txt` is the file `best-time.txt.save` on the disk; "You should
  see" names `best-time.txt.save`; the step says the functions stand above the script's class, `ParseWhole` first, with
  `#include <optional>` and `#include <string>` below the include of `StrataScript/StrataScript.h`. Checked with the
  page's functions in one script built that way (`files/SaveTest.cpp`): `best 1250`, checkpoint 12.5, 0.4, -3.1 with 7
  coins, `abc` and `12:30` gave 0; the folder held `best-time.txt.save` and `checkpoint.txt.save`.

### WK16
- Fixed on `make/levels-saves`. Why: the loading bar and the room had no commands to make the scene, the image, the
  trigger or the door script, and the door was a pseudocode fragment.
- Change: the loading-bar step copies the release's `Samples/ThirdPerson/Scripts/LoadingScreen.cpp` and gives the
  editor path and the commands for `Scenes/Loading.stscene` (canvas, a `Filled` image `Bar`, a text `Label`, the script
  with its fields, `project.setExportSettings`). The room step shows the new file
  `tutorials/make/levels-saves/RoomDoor.cpp` in two excerpts (enter loads once, exit unloads, the bar, the tag test) and
  gives the commands for `Scenes/Room.stscene` with a cube `RoomBlock` and a door trigger in `Main`.
- Checked with these commands: the image read back `Type` Filled with `FillAmount` 0, the script attached with both
  fields, `project.setExportSettings` answered the loading scene's handle; holding A for 60 steps put the player in the
  door and `RoomBlock` existed, holding D for 90 steps took it out and `RoomBlock` was gone, with no warning. The bar
  during an export's first load was not watched.

## Confirm

Walked again as G0 with the official 0.8.0 package under the perf lock (one editor per hold, all quit), in
`docs-work/walk-G-final-8/confirm/`, through StrataCLI only (no clicks; pictures not looked at). Before the walk the served
book (port 4329) was older than `book/write` and showed none of the fixes (no "Dist", no Checkpoint 4 link); I merged
`book/write` into `docs-site`, rebuilt its `dist` and read the pages from a second server (port 4330). The downloads were
fetched from that build. Starts: Coin Run Checkpoint 4; a new `basic3d` project; Characters Checkpoint 10; Animation
Checkpoint 9; Menus Checkpoint 7. Results for the fixed entries:

### WK1
- Gets through. "Before you start" names Coin Run or Checkpoint 4 (linked) and one Ctrl+B; after `script.build` the file
  `Scripts/CMakePresets.json` existed and `cmake --preset strata` worked. Opened with `StrataCLI launch --project`, not
  File > Open Project (not walked).

### WK2
- Gets through. `cmake --preset strata` ended with `Build files have been written to: ...IDE`, the build printed
  `Creating library ...IDE/Dist/CoinRunScripts.lib` and `CoinRunScripts.vcxproj -> ...Bin\CoinRunScripts.dll`, and the
  Console read `Reloaded script module 'CoinRunScripts' (9 classes)` (the page says "(1 class)", "with the number of
  classes you have"). The page now says the lines name `Dist`, and they do.

### WK3
- Not through in practice, one trap left. Stage 1 gave `Triple of 14 is 42` as the page says. Stage 2: I copied `stage-2/`
  over the project and ran `stage-2.commands.json`; its `script.build` reported success and both plays printed
  `Triple of 14 is 42`, never 56. The cause: the copied `Triple.cpp` kept the file time it had in the unpacked ZIP (every
  ZIP entry is stamped 1980-01-01; my unpack stamped the unpack time), which is older than the stage-1 build, so MSBuild
  did not compile it (`Script build ... (the module was up to date)`). After touching `Triple.cpp` (saving it again), the
  same commands file printed 42, then reloaded, then 56. A reader whose copy keeps the ZIP's old date (a copy in the file
  browser keeps it) and who unpacked before the stage-1 build gets 42 twice and no hint why. Suggest: the answer says to
  save `Triple.cpp` again after the copy, or the ZIP carries a current time stamp.

### WK4
- Gets through. "What you need" says Basic 3D project plus Checkpoint 1's commands; `project.create` with `basic3d` (its
  schema read with `StrataCLI list --json`) then `cc-1.commands.json` ran without a failure: course, `Gameplay` map, player
  at Z 2 resting at about 0 after 60 steps. The ground is the template's dark grey, as the page says now.

### WK5
- Gets through. Checkpoints 2 to 10 each ran with no failure when the stage's scripts were copied first and the file was
  newer than the last build (fields `JumpSpeed`, `CoyoteSeconds`, `GroundStateNumber` appeared; jump to 1.22 m, state 3 in
  the air and 0 after; step and ramp values as before; `Distance 6.5`, `ArmReturnSharpness 6`; platform `Travel (6, 0, 0)`,
  `Period 8`; `script.setField` of `Loop` answered). The walk and jump tabs name `play.start` paused, `input.key` with `key`
  and `steps`, and `play.step`, which are what the files run. One catch, the same as WK3: when I copied the next script
  within the same 2 s as the previous build (this drive stamps files to 2 s) or kept an old file time, `script.build`
  answered "up to date", the new fields did not appear, and later steps failed (`input.sequence`: "'field' must name a
  field of PlayerController"; `script.setField`: "MovingPlatform has no field 'Loop' (see script.status)"; the page's "run
  script.build again" does not help then). A person copying by hand is slower than 2 s; the old-time-stamp case is WK3's.

### WK6
- Gets through. The camera's Translation was (0, 3.889, 8.578) for the player at Z 2: the page's Z 8.6 and Y 3.9. After 15
  steps of W it was Z 6.08; after the Checkpoint 7 change (6.5 m arm) (0, 2.946, 6.465).

### WK8
- Gets through, with a duplicate. I copied only `Assets/Animations` from Checkpoint 1, did the new step 1 by hand
  (`asset.import` of Robot and Footsteps with `<release folder>` replaced; the handles of the release's `.meta` files matched
  the controller's clip ids), then ran `an-1.commands.json`: its first two lines import the same folders again, so the
  project got `Models/Robot (1)` and `Sounds/Footsteps (1)` with no error (the placed robot is the first import). "Use one
  or the other" covers it, but a reader who does step 1 and then runs the file ends with copies; a note in step 1's command
  tab ("the commands file does this itself") would stop it. Stages 2 to 9: no failure.

### WK9
- Gets through. Stage 7's file imports `flag.glb` (`Models/flag/flag.glb`, with its `Textures`) and `asset.place` answered
  at once; the flag followed the hand while the robot walked 60 steps.

### WK10
- Gets through. `animation.info` of the Robot answered `state` and `normalizedTime` (0.59, then 1.19: past 1), `Speed 3`
  and the parameters `Grounded` and `Jump`; `clip` still names the unused Clip; Footsteps `Steps` 6 after 150 steps. The
  Crouch exercise file's one `animation.setController` and its `edit.undo` ran, and the history listed the earlier steps.

### WK11
- Gets through. I copied only the section's one script file (MainMenu, PauseMenu, SettingsMenu, RebindMenu, NameField,
  Credits; stage 2 has none) and ran each commands file: no failure, including `prefab.create` and `prefab.apply` of stage 4.

### WK12
- Gets through. Each file ended with `scene.save`, so the next `scene.open` found no unsaved changes. Play steps through
  their tabs' commands: the Play click moved play to Main, Quit and Down, Down, Enter ended play, `Gameplay/Pause` was
  made, the toggle `IsOn` went false then true, the slider `Value` was 0.5, `K` went into the rebinding text, and
  `input.type` "Ana" with Enter was read back.

### WK13
- Gets through. "Before you start" links Checkpoint 7 and says the page has no downloads; I started from that project.

### WK14
- Gets through. Step 1 (the Goal and the tag `Player`), step 2 (`scene.saveAs` with `path`, then moving the goal), step 3
  (the listed `NextLevel.cpp` compiled as printed; `script.add` took `Next` as a path): holding W 240 steps in `Main` put
  play in `Level2`, holding D 180 steps in `Level2` put it in `MainMenu`. `scene.open` with `scene` as the page shows.
  Steps 4 and 5 have only `script.build` as their tab; it succeeded, but no code from the tab is built, so it checks nothing.

### WK15
- Gets through. The functions above the class with `<optional>` and `<string>` compiled; `.strata/Saves` held
  `best-time.txt.save` and `checkpoint.txt.save`; read back `best 1250`, coins 7, x 12.5; the text `abc` gave 0.

### WK16
- Gets through, with assembly. The commands made `Scenes/Loading.stscene` (canvas, Filled `Bar` with `FillAmount` 0,
  `Label`, `LoadingScreen` copied from the release with both fields) and `project.setExportSettings` answered the scene's
  handle. `RoomDoor.cpp` has no download: I put the include and `using` lines, the two excerpts and the registration
  together as the page says and it compiled; holding A 60 steps put `RoomBlock` in the playing scene, D 90 steps took it
  out. The bar of an export's first load was not watched.

## Answers (after confirm)

Measured with the 0.8.0 package in a headless editor (`docs-work/walk-final-fix/drive.py`, `results.json`): checkpoint 4
of make/project-coin-run, the solution zip of exercise 1, its two commands files run as the reader runs them.

### WK3 make/script-builds, Exercises, Basic
- The confirmer is right, and the cause holds whatever the reader unpacks with: every entry of the zip is stamped
  1980-01-01. Stage 1 printed `Triple of 14 is 42`. The `stage-2` file copied over the project's with that old time:
  stage 2's build answered `Script build 10 finished in 0.7 s (the module was up to date)` and both starts printed 42.
  The same file saved again (written with a new time), then the stage-2 commands: 42 from the old module, a build while
  playing, then `Triple of 14 is 56`.
- Decision: the page changes, not the download. A zip cannot carry a time newer than the reader's own first build, so
  only a save after the copy works in every case. The answer now has the reader open `Libraries/Triple/Triple.cpp` in
  the code editor, change the 3 to 4 and save (the `stage-2` folder holds the file as it then reads), then run
  `stage-2.commands.json`; a second paragraph says that a copied file must be saved once in the editor too, because it
  keeps the archive's older time and the Console then says the module was up to date, with 42 twice. The tutorial file
  is unchanged (the run copies the file with a new time).
- `tutorials.py run make/script-builds/exercise-1` passed with the pin build and with the package, after a stale check
  in `make/project-coin-run`'s file, which the exercise starts from, was dropped (commit "Drop project-coin-run's check
  of a warning Physics now clears": since the answer on make/physics no play warns about `Speed` any more). pagecheck
  PASS.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK3 make/script-builds, Exercise 1 answer
- Holds. Checkpoint 4 of project-coin-run plus the solution zip's Libraries and Scripts: stage-1.commands.json gave `Triple of 14 is 42`. A copy of stage-2's file that kept the archive's 1980 time and was not saved: stage-2.commands.json said the module was up to date and showed 42 (again), as the answer says. After saving the file again, the run showed a reload and `Triple of 14 is 56`. The answer's instruction (edit the factor in your editor and save; a copied file must be saved too) gets a reader to 56.
