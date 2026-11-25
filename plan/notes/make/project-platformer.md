# Notes: make/project-platformer

## New terms

- capsule: a cylinder with round ends, the shape of a character controller; this page is home; aliases: none.
- mesh collider: a collider that follows the triangles of a mesh, allowed only on static bodies; this page is home; aliases: triangle-mesh collider.
- asset field: a script field that holds a reference to an asset (here a scene), which a pruned export follows; this page is home; aliases: none.

## Requests

- Layout `layouts/first-script.ini` is a placeholder for the nine editor figures s1-assets to s9-export (waitsFor tier 2: editor screenshot). Each needs the layout that shows the panel named in its caption: Content Browser (s1), Scene view and Hierarchy (s2), Inspector (s3, s4), Asset tab (s5), Scene view (s6, s7, s8), Export dialog (s9). Their project is the sample ThirdPerson as a stand-in: the tutorial's own state cannot be a figure project.
- The `result` figure is a scene capture of the sample, as the sample's course is the game the page follows.
- Tutorial file: `startsFrom` is the basic3d template. The stage commands for stages 2 to 9 were never run: the ids bound from `asset.place` (`/id`) and the field `Target` set from a bound id are unchecked. Stage 1 imports use the placeholder `<release folder>`, as the coin run tutorial does.
- Stage files: the tutorial folder holds its own copies of `FollowCamera.cpp` (the final step of make/characters-cameras), `MovingPlatform.cpp` (its step 9), `Footsteps.cpp` (make/animation) and `MainMenu.cpp` (make/menus), because the tutorial check requires the files of a stage to lie in the page's own folder. If those pages change their files, these copies change with them.
- Words used that the lint accepted as code or names: none proposed.

## Since

0.5.0: `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp` was added on 2026-10-20 and `v0.5.0-rc1` is the first tag that holds the sample (`git cat-file -e v0.5.0-rc1:Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp`).

## Not verified

- The editor labels of the Inspector fields **Convex**, **Type**, **Is Trigger**, **Half Extents**, **Offset**, **Sort Order**, **Receives Input**, **Event Target** and the page names **Input Actions** and **Game** are taken from sibling pages and the component fields; the `names` check accepted them.
- The block model's size (2 m wide, origin at its base): derived from the sample's block positions (4 m grid at scale 2, top at y = 0 for a block at y = -4), not measured on the glTF file.
- That a collider without a rigid body is static for a mesh collider: the page keeps the explicit static Rigid Body as the sample does.
- The exported program's name `Platformer` and the `--windowed` option on all three systems: taken from the coin run page's export step.
- The scripts of `tutorials/make/project-platformer/` were written from the sample's scripts, shortened (no attract mode, wave, dance, crate, settings); never compiled.
- Whether `play.step` counts 60 fixed steps a second at the project's `Scene.Timing`: the default `Scene::FixedTimestep` is 1/60 s at the pin.

## Findings not applied

- critic-make-c-1 (files with no row): applied as the brief proposes: every stage copies its script files from the page's tutorial folder and quotes the parts that matter.
- critic-make-c-2 (`std::clamp`, 30 words): not applied in prose; the Move/turn quote has a callout on the turn limit (`Lines 59-61`), and the callout names the clamp's use. The `helps` row for `make/project-tetris` is not linked (that page was not in the Needs).
- critic-make-c-6 (waiting for meshes): applied in stage 2 (one sentence, 10 s) and in the Hard exercise (`physics.stats` and `until`). The duration was read from `PhysicsTypes.h` (`MeshWaitTimeout`), not run.
- critic-make-c-7 (robot scale 0.4): applied in stage 3 step 3 with the 4.08 m figure of the finding.
- critic-make-c-12 (one command for the controller): applied in stage 5 as one `animation.createController` call; `@file` is explained as a CLI call in the editor tab. The Asset tab edit is not repeated: the page links make/animation.
- critic-make-c-17 (time format): applied as an own function with a sketch.
- critic-make-c-18 (camera and platform files named): the page copies `FollowCamera.cpp` and `MovingPlatform.cpp`; the fields set are `Target` (camera) and `Travel`, `Period` (platform).
- The exercises: Basic (lantern) and Hard (play-test) as briefed; the Medium exercise answer is pseudocode, not a worked solution file.
- The lantern exercise does not link `make/lamps`, which is not written at this commit.

## Figures

- result: round 1 played the project's start scene, the main menu (title, Play, Settings, Credits and Quit over the robot), not the course. Round 2 adds `"scene": "Scenes/Course.stscene"`: the robot from behind on the first island, gold coins up the steps to the higher islands, and the HUD reading Coins 0/12 and Time 0:00.5. Published. The alt and caption now say what the picture shows: the coins are farther up the path, not spinning nearby, and the count and clock are both at the top left.
- s1-assets to s9-export (editor, 2026-11-18): recipes written from the page's steps and taken with the provisional build
  (`--provisional`); nothing published, `waitsFor` kept. The project is the sample ThirdPerson: a recipe copies sample
  assets only through a tutorial stage's files, and stage 1 of the tutorial imports from `<release folder>`, so the
  reader's own state at stage 1 cannot be a figure project. Whole-window figures use the new
  `layouts/project-platformer.ini` (960 × 540, `layouts/dialogs.ini` with the Inspector widened to 300 px); panel
  figures use `layouts/content-browser.ini` and `layouts/materials.ini` (1280 × 800).
  - s1-assets: round 1 good. The Content Browser panel shows only the top folder (no command opens a folder), so it
    pictures the sample's ten folders, Models and Sounds among them, not the reader's two folders nor the model's
    texture inside Models. Caption and alt rewritten to that.
  - s2-course: round 1 used `camera.focus` on Course, which looks along -Z and stacks the islands into one pile. Round 2
    builds the page's stage 2 in a new basic3d scene (Ground deleted, ten `BlockTall` instances of the sample's prefab
    under `Course`) and sets the camera with `camera.set` (yaw 65, pitch -22, 50 m): four islands with gaps, the last
    higher. Good.
  - s3-player: round 1 showed raw handles ("No script module is loaded"); round 2 builds first: the sample's Player with
    Tag, Character Controller (1.8, 0.4) and the script with Walk Speed 3, Run Speed 6.5, Jump Speed 5.5, as the page's
    step 5 says. The old caption ("the robot comes in stage five") contradicted the page (the robot is added in stage 3,
    step 3): rewritten.
  - s4-camera: round 1 had the Scripts built toast over the Game view; round 2 waits 600 frames. The Game view from
    behind the robot in paused play, Camera selected. The FollowCamera script sits below the Camera component, outside
    the Inspector's height: the alt names only Transform and Camera.
  - s5-robot: round 1 good. The sample's controller has five parameters, six states and fourteen transitions, the
    page's three, four and seven: the caption says both.
  - s6-course: round 2 builds the scripts so Game's Inspector shows its fields, not handles. The view frames coins 9 and
    10 and Jump Pad 1; the flag and the HUD are not in it (the goal is 20 m farther), so caption and alt name the coins,
    the pad, the prefab instances in blue and Game.
  - s7-platform: round 1 good. The page's stage 2 course plus a `Platform` (cube 4 × 0.5 × 4, box collider, kinematic
    body) at (2, -0.25, -18), between islands B and C; the Inspector shows Rigid Body Type Kinematic. The sample has no
    moving platform, and the MovingPlatform script is not attached (the tutorial's copy was never compiled).
  - s8-menus: round 1 good. The sample's MainMenu in canvas mode has four buttons (Play, Settings, Credits, Quit), two
    more than the page's menu: the caption says so.
  - s9-export: round 1. No command ticks a box in the dialog, so "Leave out unused assets" stays unticked; the loading
    scene comes from the sample's project setting. Caption now tells the reader to tick the box. The Directory field
    shows the take's folder under `G:\GameEngineAI\.worktrees\docs-work\...` (no user name, but a machine path): retake
    from a neutral folder, or crop the field, before publishing when the pin moves.
- Round 3 (2026-11-18, a viewer's faults on the provisional takes; provisional build, nothing published):
  - s4-camera: the sample's scripts call `Game::SetWindowMode` and `Game::SetVSync` at every start (ThirdPerson.cpp,
    `ApplySettings`), so the Game view always shows "The game asked for a window with vsync on; play mode keeps the
    editor's window." (any vsync value asks). The recipe now pictures the Game panel alone at 1280 × 720
    (`layouts/first-game.ini`, 797 px wide): the notice is whole and covers only a strip of grass; the alt names it and
    the mouse hint at the top. Camera selection dropped (out of the picture).
  - s6-course: the sample's Game holds SettingsMenu, CourseState and PauseMenu, and SettingsMenu filled the Inspector.
    The recipe removes SettingsMenu and PauseMenu (`script.remove`) before selecting Game, as the reader's stage 6 has
    it: the Inspector shows CourseState's fields. Caption and alt say so without the class name (not on the word list).
  - s7-platform: caption only, no retake: the 4 m platform at z = -18 stands in the gap from -14 to -26; it does not
    fill it. The gap's 12 m stays out of the caption (the figure check refuses a number without a source).
  - s8-menus: the Scene panel alone at 1280 × 720 (797 px wide, about the column's 768): title, subtitle, the four
    buttons and the line about the controls read. Canvas selection dropped; shows and alt rewritten to the Scene view.
  - s9-export: alt now counts four boxes (Fullscreen and the pruning box unticked). The folder stands: the dialog fills
    it with `<project folder> Build` (ExportDialog::Open) and only the native folder picker changes it, and the take's
    project lives in the work folder, so the field and the footer print the take's path. A crop needs `crop=` on the
    page's `::figure` line (words not mine to change) or a take option that places the project copy under a neutral
    folder; until one of these, s9-export must not be published.
- Pin v0.8.0 (319075e3, 2026-11-23), one take of all ten in one hold, pin Release build, no `--provisional`; the
  `waitsFor` lines removed as `check` asked.
  - result: compared with the 822a7a46 original (`figures.py compare`: max mean 0.013) and kept by publish (mean 0.229,
    largest block 2.75): the stamp records the new pin. The picture is the same course, HUD at Coins 0/12, Time 0:01.0.
  - s1-assets to s8-menus: published as taken; each shows what its caption and alt say. s6-course: the Hierarchy also
    lists Camera, Sun, Sky, Post Process, Course, Crate, HUD, Menus and Reflection Probes, so the alt now says its rows
    "include" the named ones (same word count: the page is at its 10,000-word limit).
  - s9-export: blocked, not published. The take shows the dialog as the alt says, but the Directory field and the
    footer print `G:\GameEngineAI\.worktrees\docs-work\photo\make-project-platformer\projects\10 Build`, the take
    machine's path and a project copy named 10. Same cause as make/export's export-dialog: no recipe field names the
    project copy's folder and no command sets the dialog's folder. Needs a `figures.py take` option for a neutral
    project folder (for example `Platformer` under a short root), or an editor command that sets the export folder.
    Nearest honest picture meanwhile: this take with the field and the footer's path masked at publishing.
- Last figure (2026-11-24, pin v0.8.0 Release build, one hold): the take tool now maps the editor's project copy to
  `S:\Projects\<name>`. s9-export retaken: the Directory field and the footer read `S:\Projects\ThirdPerson Build`, no
  path of the machine. The dialog shows what caption and alt say: 1280 by 720, Fullscreen unticked, the loading scene
  `Scenes/Loading.stscene`, the runtime and the script symbols ticked, "Leave out unused assets" unticked. Published; the
  page's words unchanged. Every figure of the page is now published.

## Clerk

- Admitted terms homed here: mesh collider (alias triangle-mesh collider), asset field.
- Refused capsule: a common word (tools/data/common-words.txt) in its everyday sense, the shape; its bold may stay. A physics home for it is the planner's.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run (2026-11-18)

Four rounds on the pin's Release build (work folders `docs-work/tutorial-runs/make-project-platformer-1` to `-4`).

- The file was thinner than the page: it now does every command tab of the nine stages (scene names, the start scene,
  the Ground and first-block deletes, the robot, the Robot field, the controller with the page's values, the HUD, the
  coins, pad, checkpoints and goal, the platform, both menus with their event targets, the loading scene and its
  export setting) and checks the "You should see" values: the ten static bodies, the 3/6.5/5.5 defaults, W walking
  along -Z and, at yaw 90, along -X, Idle then Walk and a counted footstep, `0 / 0` then `0 / 8`, a coin and checkpoint
  1, `A new best time!`, the platform at z = -24 after 240 steps, `Paused` after Escape.
- Faults of the file and the page, mended in both: `<release folder>` for `@RELEASE@`; a kit model lands at
  `Models/Platformer/<name>/<name>.glb`; `entity.delete` takes `entities`; `entity.create` binds `/id`; the block's
  Rigid Body and Mesh Collider sat on the model's root, which has no Mesh Renderer, so play had no static body and the
  player fell through the islands (now on the child `block-grass-large-tall`); the first coin was a ninth coin (now
  deleted, as the first block is); the pad had no position or prefab in its tab; the Run binding `Key/RightShift` was
  not the page's; `scene.open` of the course needed a `scene.save` of the menu first; an `input.key` tap of Escape
  would wait for fixed steps that the paused game no longer runs (now `press`, then `release`).
- A fresh editor opens the project's start scene (`EditorContext.cpp:428-447`), so stage 1 now makes `Course` the start
  scene until stage 8; the exercise opens the course, as the start scene is then the main menu.
- Not in the file: copying `CREDITS.md` (a file outside `Assets/`), `project.export` (an absolute folder, which only
  `setup` may hold) and running the exported game.
- For runners: a reader copy runs part by part in new editors that quit without saving, so a scene edit made before a
  command with `files` is gone in the next part; stage 5 therefore copies its two files at the stage's start.
- The prose grew by the mended tabs; cuts elsewhere keep the page at 10,000 words, the size's limit.

## Engine

- `asset.import` of one glTF file that reads a texture puts the model itself into the new folder named after it
  (`Models/Platformer/coin-gold/coin-gold.glb`); its description reads as if only the files it reads go there.

## Settled with the editor (2026-11-18)

- `s3-player` (caption fixed by the photographer), `s4-camera` (the sample's own notice) and `s9-export` (the folder field shows the take's path): the page's words are true; no change. `s9-export` needs a crop or a neutral take folder before it is published.

## Track walk G-final-2 (2026-11-24)

WK27 of `plan/walks/G-final-2.md`: the link to `make/transforms-units` named it "Units and transforms"; it now has the
page's title, and one "so" went to keep the page at 10,000 words.

## Track walk G-final-11 (2026-11-24)

Answers to WK2 and WK11 to WK17 of `plan/walks/G-final-11.md`:

- Stage 2's "no floor" names the sky's picture of its planet's ground below the horizon.
- Stage 1's import tab imports every file in four commands (`files` per folder); the file does the same and asks
  `asset.info` for the block's folder. `CREDITS.md` is the release's `Samples/ThirdPerson/CREDITS.md`.
- The Gameplay map's tab shows all six actions. What you need says that a stage's files are in the folder `Scripts`
  of the download at the end of its section; the menu steps name checkpoint 8 and 9 for their scripts.
- Collider shapes show only for the selection (`viewport.setSettings` `allColliders`, default off): stage 2 and 3
  select the block's child and the player before the capture; a package capture showed the green outline, the wire
  capsule and the robot's back to the editor camera (it faces -Z).
- Stage 5's tab catches the Jump state paused (tap **Space**, 10 steps) before the walk and the run; the file checks
  Jump, Walk, `Steps` and Run.
- Stage 6's tab moves the player to the coin, below the fall height, onto the pad and to the goal; the file checks the
  return to checkpoint 1 near (2, 0, -12) and the pad's launch (about 5 m up after 30 steps).
- The menu tabs give every `ui.create`. The walker's buttons sat at the left because a `UILayout` added with
  `component.add` keeps `TopLeft` and no stretch; the `verticalLayout` of `ui.create` is `TopCenter` and stretches
  (`StrataEditor/src/Editor/GameUIPresets.cpp:219-224`). The page says so.
- The exported game's play needs a person; the walker's run showed the menu, and a headless run of its export exits 0.
- The prose stays at 10,000 words: cuts in the course's trigger, scene-switch, menu-gamepad and summary text.
