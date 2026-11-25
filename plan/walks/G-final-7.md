# Walk log: track G (persona G0), segment 7, at v0.8.0

Entries walked: `basics/math-vectors`, `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/patterns`,
`make/recipes`.
Package: official Strata 0.8.0 Windows package (`Strata-0.8.0-windows-x64`); one StrataEditor session (1280x720) driven
by StrataCLI under one perf-lock hold; projects in `walk-G-final-7/proj` (GameplayMath, ShotRange, TimersEvents,
ScriptFields, Patterns, a ThirdPerson copy, Recipes). No page of the segment offers a stage download for a reader who
arrives there (see WK1), so each page that needs a project started from a new Basic 3D project.

Not walked: clicks, menus, drags and the Inspector (all done through commands and read back with `script.get`,
`component.get`, `entity.get`, `log.read`; pictures through `viewport.capture`); the editor overlay of the Coin trigger (wire
sphere); the sounds (I read how many sounds the budget lets through from a log line, I did not hear them); the click-to-shoot
of the `make/gameplay-math` Hard exercise (its solution's commands instantiate the ball instead); the Medium and Hard
exercises of `make/script-fields` and the Hard one of `make/patterns` (answered by reading, not run); the sketches of
`basics/math-vectors` (no compiler is offered on the page: I computed them by hand and compared). I compiled the three
sketches of `make/patterns` and `make/recipes` with a compiler of my own machine, which a G0 reader does not have.

## WK1
- Entry: `make/gameplay-math` (first entry that needs a project); page: same; section: "Before you start" (there is no
  "What you need").
- Kind: guessed.
- `basics/math-vectors` has no project and no stage download. `make/gameplay-math` asks for "a new project from the Basic 3D
  template" and gives neither a command nor a download. I found `project.create` with `StrataCLI list` and guessed its
  parameters (`directory`, `name`, `template: "basic3d"`); it worked at once.

## WK2
- Entry: `basics/math-vectors`; section: the sketches (steps, length, angles, dot, cross) and "Practice, Hard".
- Kind: left the book.
- The page shows programs with `#include`, `int main` and glm but says nowhere how a G0 reader compiles and runs one; the Hard
  exercise says "in a program of your own". I did all the sketch outputs and the exercises by hand and they matched every
  printed output and every answer. I tested the optional CoinMagnet in a script of my own project (WK3): it compiled as written
  and the coin followed the ball.

## WK3
- Entry: `basics/math-vectors`; section: "Practice, Hard (optional, in Coin Run as Coin Run leaves it)".
- Kind: left the book.
- No stage of Coin Run is named; I used my own project with a ball named Ball and a coin without children. The listing is
  labelled "Pseudocode" although it compiled unchanged as a real script.

## WK4
- Entry: `make/gameplay-math`; section: "Place the turret and the ball", command tab, Barrel.
- Kind: failed.
- `entity.create` with `"parent": "Turret"` (a name) answers -32602 "Parameter 'parent' must be an ID (16 hexadecimal
  digits)". The other command tabs of the segment use `<id>` placeholders; this one uses a name. Repeating it with the id of
  Turret worked.

## WK5
- Entry: `make/gameplay-math`; section: same, "You should see".
- Kind: did not match.
- The picture of the editor camera shows a cylinder and only a thin tab of the barrel at its top edge; the barrel is mostly
  inside and behind the cylinder, not "a block that sticks out of its side". The numbers (Z -0.8, scale 0.2, 0.2, 1) are as
  the page says. Seen from above (a capture I made from a custom position) the barrel sticks out as expected.

## WK6
- Entry: `make/gameplay-math`; section: "Turn toward the ball with atan2", "You should see".
- Kind: did not match.
- The page says the log reads "Ahead 1, side 0, with a rounding error in the last digit". The lines read, for example,
  "Ahead 1, side -5.96046e-08" and "side 8.9407e-08": the Console prints the small error in exponent form, not as a last-digit
  error of 0.
- All other "You should see" lines of the page matched: "The ball is 7 metres away" falling toward 1; "Distance 7, direction
  1 0 0"; "Ahead 0, side 1" and Ahead first negative then positive; the barrel toward the ball, tilted down at Y 3; the aim
  trailing the ball; the barrel following the cursor (checked with `input.mouseMove` and the rotation).

## WK7
- Entry: `make/gameplay-math`; section: "Aim through the cursor", the replacement of the whole Turret script.
- Kind: did not match.
- The scene still stores the field Target after the new class has no field; the Console says "script 'Turret' has no field
  'Target'; the stored value is ignored". The page does not mention the warning or say to clear the field.

## WK8
- Entry: `make/gameplay-math`; section: "Exercises", Hard, "Download the worked solution".
- Kind: guessed.
- The page says the ZIP holds "the editor commands of the solution ... to run on your own project" and does not say how to run
  a `stage-1.commands.json`. I found `editor.batch` (it refuses the `script.build` and `play.*` steps that the file holds) and
  wrote a small runner that calls each step with StrataCLI and resolves `bind` and `$ref`. Run that way, with the two scripts
  copied to `Scripts/`, every step passed and the log read "Goal: 1". The Basic exercise (by hand) and the Medium one
  (TurnSpeed: a half turn at 90 degrees took 2 s) matched the answers.

## WK9
- Entry: `make/timers-events`; section: "Read the clocks and set the time scale", "You should see".
- Kind: did not match.
- The page says "a delta near 0.004 and an unscaled near 0.017". On this machine the frame lasted about 8 ms, so the line read
  "scale 0.25 delta 0.00206428 unscaled 0.0082571" and, frozen, "scale 0 delta 0 unscaled 0.0082955". Both fit the rule, but
  the numbers assume 60 frames per second.

## WK10
- Entry: `make/timers-events`; section: "Give the dash a cooldown".
- Kind: guessed.
- The page shows only lines 27-32 of Player.cpp. "Write OnUpdate so that it moves the cube" gives no listing for the move
  or the fields. I wrote A/D movement, `Speed`, `DashDistance` 3, `DashCooldown` 1.5, `m_Facing` and an early return at scale 0.
  The behaviour then matched ("a second press within 1.5 s does nothing"). The complete file is only in the zip of the Basic
  exercise further down the page.

## WK11
- Entry: `make/timers-events`; section: "Let scripts call each other", Pickup and the Dropper call.
- Kind: failed.
- Pickup.h, the registration of Pickup and the line in Dropper.cpp are only described in words. I wrote
  `const Entity crate = Scene::Instantiate(...); crate.AddScript<Pickup>();` as the previous page's Spawner does, and the build
  failed with C2662 "cannot convert 'this' pointer from 'const Strata::Entity' to 'Strata::Entity &'". Without `const` it
  built and the score reached 1.
- Also, for the Dropper listing, the field `Period` and the members are not in the shown lines; I guessed them from the prose.

## WK12
- Entry: `make/script-fields`; section: "Write the spawner", crate prefab step.
- Kind: guessed.
- The command tab holds only `prefab.create` with `<id of Crate>` and no command that makes the Crate or the Spawn Point. I
  made them with `entity.create` (a cube with a Rigid Body, an empty at 0, 3, 0).

## WK13
- Entry: `make/script-fields`; section: "Play, and change values while playing", "You should see".
- Kind: did not match.
- The crate of the page has a Rigid Body but no collider (editor tab: "add a Rigid Body and keep its type dynamic"). In play
  the three crates appeared 1 m above the spawn point and stayed in the air at y 4; none fell, so no stack formed. The page
  expects "a crate falls every 2 s ... the three form a stack". A Box Collider is missing from the Crate step.

## WK14
- Entry: `make/script-fields`; section: "What the spawner does with them".
- Kind: guessed.
- Spawner.cpp lines 41-46 (the private members) are not shown: I added `m_Waited` and `m_Spawned` from the code that uses
  them. The rest (ten fields, registration, rename of a field and of the class, reset with null, prefab Apply and Revert, a
  Spawn Point per instance) behaved as the page says, including "no field 'MaxCrates'; the stored value is ignored" and the
  class default 5 for CrateLimit.

## WK15
- Entry: `make/patterns`; section: "Exercises", Medium, "Download the worked solution".
- Kind: failed.
- I replaced the generated BulletPool.cpp with the file of the ZIP and ran the file's steps. `script.build` answered
  "the module was up to date" and the playing scene held no Bullet (the page says 20). The ZIP's files carry the date
  1980-01-01, older than the template I replaced, so the build kept the old module. After I touched the file and built again,
  20 bullets existed in play and 0 after stop, as the page says. A reader who copies the file with File Explorer may keep that
  date too.
- Everything else matched: the guard trace and output, the pool sketch "fired 75, skipped 25, made 3".

## WK16
- Entry: `make/recipes`; section: "Recipe 4: impact sounds with a budget", copy three clips.
- Kind: guessed.
- "Copy three short clips into Sounds/Impacts ... named Wood.ogg, Metal.ogg and Soft.ogg" says no source. I took them from
  `Samples/PhysicsPlayground/Assets/Sounds/Impacts` of the package. The editor imported them within a moment (`asset.list`
  showed three AudioClip assets).

## WK17
- Entry: `make/recipes`; section: "Recipe 4", write the Impact script from the two excerpts.
- Kind: failed.
- With the SDK include line only, the build fails: error C2039 "'clamp': is not a member of 'std'" (the line `std::clamp` of
  the excerpt). The excerpts start at line 13 and 48 and leave out the includes; `#include <algorithm>` fixed it. The
  OnCreate that loads the clip and the fields are not shown either; I guessed OnCreate (`Assets::Find` by `c_SoundPaths[Kind]`,
  then `RequestLoad`). With it, a pour of 32 balls played 8 sounds in the first frames, as the budget says.

## WK18
- Entry: `make/recipes`; section: "Recipe 1: the coin" and "Recipe 2: the seeded pour", the scripts "from the excerpts".
- Kind: guessed.
- The excerpts of Coin.cpp skip the fields and members (SpinSpeed 180, BobHeight 0.12, Collected, m_Time, m_VisualTranslation,
  m_Phase); I took the values from the "You should see" line. Playground's `c_BallScale` is not defined in the excerpt of
  SpawnBalls; I used 0.5. Results matched: "Coin collected" once and the field Collected true; the same pile for Seed 5 twice
  (equal positions) and another for 6; DiceRoller gave 4 3 1 for seed 1 in both runs, 3 6 1 for seed 2, and continued with
  roll 3 after a hot reload; the grab followed the cursor and let go of the box when E was released; the Medium coin exercise
  hid the model and brought it back after 10 s.

## Answers

Checks were run with the official 0.8.0 package under the perf lock, in `docs-work/walkfix-G7` (`verify.py` with its
folder `run/`; `verify2.py` with `run2/`). No tutorial file changed, so no tutorial was run again.

### WK1
- Fixed on `make/gameplay-math`. Why: the page has no tutorial file of its own steps (only exercise 3 has one), so it
  offers no stage download, and "Before you start" asked for a new Basic 3D project without saying how.
- Change: the first item of "Before you start" names **New Project** in the launcher, as `make/editor-tour` made Coin
  Run, gives the `project.create` line with the template `basic3d`, and says that the page offers no download: each
  section adds to the scene and the script of the one before.

### WK2
- Fixed on `basics/math-vectors`. Why: the page showed programs with `main` and their outputs, but no way for a G0
  reader to run one, and the Hard exercise said "in a program of your own". The playground of `basics/programming-1`,
  a script, is where track G runs code, and the page already used it for one `Log::Info` line.
- Change: the aside at the start (now "What are the programs' first lines, and how do I run them?") says that a reader
  need not run them, since each output stands below its program, and that the lines inside `main` run in `OnCreate` of
  the `Playground` script with `Log::Info` in place of `std::printf`. Practice 5 is done in the `Playground` script
  (the function above the class, five frames logged in `OnCreate`); its answer says that the sketch prints what
  `Log::Info` writes there. The walker's hand results matched every output.

### WK3
- Fixed on `basics/math-vectors`. Why: practice 6 said "Coin Run as Coin Run leaves it" without naming the checkpoint,
  and did not say that Coin Run's coins are made at play by `CoinPlacer` from `Prefabs/Coin.stprefab`, so "add it to
  each coin" had no coin to add it to in the edited scene. The listings are fenced as pseudocode because the sketch
  check builds only programs that stand alone, not scripts; the page did not say so.
- Change: the exercise names the reader's Coin Run or the last checkpoint of `make/project-coin-run`, the ball `Ball`,
  and the prefab steps (a copy dragged into the scene, the script added, applied to the prefab, the copy deleted). The
  answer says why the listings are marked pseudocode, that they are the whole class and build in
  `Scripts/CoinMagnet.cpp` below `MagnetStep`, and that Coin Run's `Coin` sets only the height, so the two scripts share
  the position. Checked in checkpoint 4 with the 0.8.0 package (`run2/`, `files/CoinMagnet.cpp`, the page's listings with `MagnetStep` above them): it built without a diagnostic; after `prefab.apply` and 240 fixed steps of play, the two coins within 3 m of the resting ball, at (-2, 0.8, 2) and (2, 0.8, 2), were collected and three coins were left at their places, against five without the magnet. The checkpoint's play also logs `script 'BallControl' has no field 'Speed'; the stored value is ignored`: a matter of `make/project-coin-run`'s checkpoint, left to its fixer.
- To keep the page within its size (L, 6,500 words) a few sentences went: the three links of "Why you will need this"
  (the list at the end names the same pages), shorter items of "Where the book uses it" and of four common mistakes.

### WK4
- Fixed on `make/gameplay-math`. Why: the command tab gave `"parent": "Turret"`, a name, where `entity.create` takes an
  entity ID ("Parameter 'parent' must be an ID (16 hexadecimal digits)", reproduced in `run/`): the page's error.
- Change: the tab uses `<id of Turret>` and says that a parent is named by the `id` that the first command answered;
  "If you do not see it" names the error.

### WK5
- Fixed on `make/gameplay-math`. Why: the editor camera of a new Basic 3D project stands at (0, 2, 6) and looks along
  -Z (`camera.get` in `run/`), so the barrel, which points away from it at Z -0.8, stands behind the cylinder. The
  capture `run/turret-editor.png` shows the cylinder and a thin edge of the barrel above its top, as the walker saw; a
  capture from (-3, 6, 2), `run/turret-above.png`, shows the block sticking out of the far side.
- Change: "You should see" names the row in the Hierarchy and what the editor camera shows, then says how to look from
  above (the Alt key and the left button, or `camera.set` with that position and target) and what shows there; "If you
  do not see it" speaks of the view from above.

### WK6
- Fixed on `make/gameplay-math`. Why: the SDK writes a `float` to the log through a standard stream
  (`StrataScriptCore/Include/StrataScript/Log.h`), which prints a tiny number with an exponent, so the rounding error
  reads `-5.96046e-08`, not an error in a last digit of 0.
- Change: "You should see" says "Ahead 1", with a side of 0 or a tiny error such as `side -5.96046e-08`, and reads
  `e-08` as times 10 to the -8, which is 0 for every use.

### WK7
- Fixed on `make/gameplay-math`. Why: replacing the class leaves the scene's stored `Target`, which each play reports
  (`ScriptSystem::ApplyFieldOverrides`, `Strata/src/Strata/Scripting/ScriptSystem.cpp:760`). Checked in `run2/`: with `Turret-8.cpp` built and `Target` set, then `Turret-9.cpp` built, play logged `Script fields: script 'Turret' has no field 'Target'; the stored value is ignored`; after `script.remove` and `script.add`, none.
- Change: both tabs of the step remove the `Turret` script from `Turret` and add it again (the **X** of its entry and
  **Add Script...**; `script.remove` and `script.add`), and a paragraph says why and quotes the warning a reader meets
  without it, which does no harm.

### WK8
- Fixed on `make/gameplay-math`. Why: the download's words come from the site ("the editor commands of the solution
  and the files they copy, to run on your own project"), and the answer of exercise 3 did not say how. `editor.batch`
  refuses builds and play steps, while the engine's own runner, `StrataEditor --commands`, runs such a file (it is how
  `tutorials.py run` runs every reader copy).
- Change: the answer says what the download holds and how to run it: a new Basic 3D project, the `Scripts` files copied
  in, then `StrataEditor --project . --commands stage-1.commands.json --quit-after-commands --no-gpu` from the
  project's folder (the Windows line as `make/automated-playtests` writes it), with a link to that page and the exit
  code 0 when every step passed.

### WK9
- Fixed on `make/timers-events`. Why: the numbers were those of 60 frames per second; the walker's frame lasted about
  8 ms, and its line held the rule exactly (0.00206 is a quarter of 0.00826).
- Change: "You should see" says that `delta` is a quarter of `unscaled`, which is the frame's length, about 0.017 at
  60 frames per second.

### WK10
- Fixed on `make/timers-events`. Why: step 5 showed lines 27-32 of `Player.cpp` and asked the reader to write the
  rest; the whole file is the tutorial's, which the page did not quote.
- Change: both tabs say to replace the new file's text with the listing; the page quotes lines 6-23 and 25-40 of the
  tutorial's `Player.cpp` (two fences under the limit of 25 lines), names lines 1-3 and the registration, and has
  callouts on the fields, the frozen game, and the cooldown's `Start` and `Update`. To keep the page within its size
  (M, 4,000 words) a few sentences went (the notes list them).

### WK11
- Fixed on `make/timers-events`. Why: `Pickup.h` and the change to `Dropper` were only described.
  `Entity::AddScript<T>()` is not `const` (`StrataScriptCore/Include/StrataScript/Entity.h:89-92`), like every function
  that changes an entity, so a `const Entity` refuses it with C2662; the tutorial's `Dropper.cpp` uses a plain `Entity`.
  Not an engine fault.
- Change: step 9 quotes `Pickup.h` (lines 6-12, its first two lines named) and lines 27-29 of `Dropper.cpp`, and says
  why `crate` is no `const Entity`, with the error a reader would meet.

### WK12
- Fixed on `make/script-fields`. Why: the command tab of the crate step held only `prefab.create`.
- Change: the tab creates `Crate` (`MeshRenderer`, `BoxCollider`, `RigidBody: {}`), makes the prefab, deletes the
  entity and creates `Spawn Point` at 0, 3, 0.

### WK13
- Fixed on `make/script-fields`. Why: the editor tab's **Cube** comes with a Box Collider
  (`StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-77`), so the page's stack holds for a reader of that tab; a
  command adds only the components it names, and a body without a shape hangs where it was made. Checked in `run/`:
  with a Box Collider three crates stood at y 0.5, 1.5 and 2.5 under the spawn point; without one at y 4, 4 and 4, as
  the walker saw.
- Change: the command tab adds the Box Collider and says why it matters, the editor tab says that the cube comes with
  one, and "If you do not see it" names crates that stay in the air at 4 m.

### WK14
- Fixed on `make/script-fields`. Why: the page said "the whole file of this page" but omitted lines 41-46.
- Change: the page quotes lines 42-45 of `Spawner.cpp`, the two members, after the update's callouts.

### WK15
- Fixed on `make/patterns`. Why: the solution zips carry the date 1980-01-01 (`tools/tutorials.py compile`), and the
  script build compiles only sources newer than their objects, so a file copied over the template's is skipped while
  `script.build` reports success with "(the module was up to date)". Reproduced in `run/`: no bullet with the 1980
  date, 20 after the date was set to now.
- Change: the answer of exercise 2 says to create `BulletPool`, paste the download's text into it and save, why a
  copied file is skipped, what the Console says then, and to save the file once and build again. Notes: `## Engine`
  (the build that keeps the old module) and a request to the tool builder (the dates in the zips).

### WK16
- Fixed on `make/recipes`. Why: the step named no source for the three clips.
- Change: step 1 of Recipe 4 names the Physics Playground's own clips in the Strata folder, their author and license,
  and its command tab imports them with `asset.import` (run in `run/`: three clips at `Sounds/Impacts/`).

### WK17
- Fixed on `make/recipes`. Why: the excerpts omitted the includes and the lookup of the sound, so `std::clamp` had no
  `<algorithm>` and `OnCreate` had to be guessed.
- Change: the page quotes `Impact.cpp` lines 6-11 (the includes, with the C2039 that a missing `<algorithm>` gives),
  38-46 (the fields, `OnCreate`, `OnReload`) and 63-87 (`FindSound`, the member, the registration), and step 2 lists
  the excerpts in the file's order. The walker's result (8 sounds for 32 balls) matches the budget.

### WK18
- Fixed on `make/recipes`. Why: the fields and members of `Coin` and the sample's `c_BallScale` were not on the page.
- Change: the page quotes `Coin.cpp` lines 10-15 and 47-59, says to keep the SDK's include in place of
  `CourseState.h` and to add `<cmath>`, and gives `c_BallScale` (0.5) with `<algorithm>` for the pour. The walker's
  values were these, and its results matched.

### Steps for the confirming walker
- `make/gameplay-math`: "Before you start" (the project by the command); "Place the turret and the ball" step 1 with
  the command tab (parent by ID) and its "You should see" from the editor camera and from above; "Turn toward the ball
  with atan2" (the log's side); "Aim through the cursor" (remove and add the script, no warning at play); exercise 3's
  download run with `StrataEditor --commands`.
- `basics/math-vectors`: one sketch's lines in the `Playground` script; practice 5 in the playground; practice 6 in
  checkpoint 4 of Coin Run with the prefab steps.
- `make/timers-events`: steps 3 (the clocks), 5 (`Player` from the listings) and 9 (`Pickup.h` and the `Dropper` lines).
- `make/script-fields`: "Write the spawner" with the command tab, then "Play, and change values while playing".
- `make/patterns`: exercise 2 with the download's text pasted.
- `make/recipes`: Recipes 1 and 2 from the excerpts; Recipe 4, steps 1 and 2.

## Confirm

Confirming walk, G0, with the official 0.8.0 package (`Strata-0.8.0-windows-x64`), one headless editor per perf-lock hold,
driven with StrataCLI (`project.create`, `entity.create`, `script.*`, `play.*`, `input.*`, `viewport.capture`, `log.read`),
projects in `docs-work/walk-G-final-7/proj7`. Not done: clicks, menus, the launcher's **New Project**, the Inspector, the
editor tabs of the steps (only the command tabs); the sounds were not heard; the cursor aim of WK7 was not seen move the
barrel (a headless editor has no game view, `Game::GetWindowSize()` is 0 and the script returns), only built and played.

**The served book is older than the fixes.** The book at http://127.0.0.1:4329/strata-engine-docs/ is the preview build of
`site/preview` (built 13:39); the answers of this segment are commit c2e23555 and later on `book/write` and are not merged
there. The served `make/gameplay-math` still says "a block that sticks out of its side" and "a rounding error in the last
digit", and has no `project.create` line. I read the fixed text from `src/content/docs/<page>.md` of `book/write` and walked
that. A reader of the preview as served would meet every mismatch again until the preview is merged and rebuilt.

| Id | Reader now gets through without guessing, leaving the book or a mismatch? |
| --- | --- |
| WK1 | Yes. The `project.create` line of "Before you start" ran as written (template `basic3d`) and the project opened. |
| WK2 | Yes. The `length` sketch's lines and `MagnetStep` with its five frames ran in `Playground`'s `OnCreate` with `Log::Info`; every value of the page's output came out (5, 5, 3, unit vector 0.6 0 0.8; frames 1.5, 1, 0.5, 0, 0; x = 5). |
| WK3 | Yes. In checkpoint 4 (the page's own download), `CoinMagnet` and `MagnetStep` built without a diagnostic; the prefab steps (instantiate, add script, apply, delete the copy) worked; after 240 steps two coins within 3 m of the ball were gone and three stayed. |
| WK4 | Yes. `entity.create` with `"parent": "<id of Turret>"` (the `id` of the first answer) made the barrel under the turret. |
| WK5 | Yes. The capture from the editor camera shows the cylinder with a thin edge of the barrel above its top right; from `camera.set` position [-3,6,2], target [-3,0.5,0] the block sticks out of the far side. Both match the new text. |
| WK6 | Yes. The log read `Ahead 1, side 0`, `side 5.96046e-08` and `side -1.19209e-07`, as the new text explains. |
| WK7 | Yes. With a stored `Target` and `Turret-9` built, play wrote `Script fields: script 'Turret' has no field 'Target'; the stored value is ignored`; after `script.remove` and `script.add` the next play wrote none. |
| WK8 | Yes. New Basic 3D project, the download's two scripts copied to `Scripts`, then `StrataEditor.exe --project . --commands stage-1.commands.json --quit-after-commands --no-gpu` from the project folder: 21 commands ran, the log read `Goal: 1`, exit code 0. |
| WK9 | Yes. After **2** and **L** the line read `scale 0.25 delta 0.00415545 unscaled 0.0166218`: a quarter, as the text says; after **P** `delta 0`. |
| WK10 | Yes, with one small guess. `Player.cpp` made from lines 6-23 and 25-40 and the template's first lines built; the three field lines of `ST_SCRIPT_CLASS(Player)` are named only in words, which a reader who did `make/script-fields` writes. |
| WK11 | Yes. `Pickup.h`, the `Pickup` method and the `Dropper` change (`Entity crate`, not `const`) built without C2662; `Scoreboard.Score` reached 1 and then 2 (my dash moved the player next to a second crate). |
| WK12 | Yes. The command tab made `Crate` with the Box Collider, the prefab and `Spawn Point` at 0, 3, 0. One small guess left: "Set the two references" shows `script.setField` only for `CratePrefab`; `SpawnPoint` takes `"value": "<id of Spawn Point>"`, which I guessed and which worked. |
| WK13 | Yes. In play with `MaxCrates` 3 the three crates stood at y 0.50, 1.50 and 2.50 under the spawn point; `Interval` set to 0.5 in play changed the copy only and read 2 after **Stop**. |
| WK14 | Yes. Lines 1-17, 19-40, 42-45 and 47-59 together are the whole file; it built and ran as the page says. |
| WK15 | Yes. `BulletPool` created, the download's text written into it and saved, built, `Gun` with the script: 20 `Bullet` entities after 60 steps and 0 after stop. |
| WK16 | Yes. `asset.import` with the three package paths gave three AudioClips under `Sounds/Impacts/`. |
| WK17 | Yes. `Impact.cpp` from the excerpts in the page's order (lines 6-11, 13-36, 38-46, 48-61, 63-87) built with no diagnostic; added to the ball prefab and applied. |
| WK18 | Yes. `Coin` from the excerpts (SDK include kept, `<cmath>` added, `Log::Info("Coin collected")`) showed Spin Speed 180, Bob Height 0.12, Collected off, then logged "Coin collected" once with `Collected` true; `Pourer` with `c_BallScale` and `<algorithm>` built and gave 16 balls and the same pile for Seed 5 twice, another for Seed 6. |

Smaller remarks, not mismatches of the fixes: in `make/timers-events` the `ui.create` command answers `canvas` and `entity`
and no `id`, where the tab says `<HUD id>`; I took `entity`. A walker who runs the editor headless needs `play.start` with
`"paused": true` before `play.step`; the book's tabs already do that.
