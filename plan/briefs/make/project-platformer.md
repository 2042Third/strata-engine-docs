# Brief: `make/project-platformer`

| Field | Value |
| --- | --- |
| Title | Project: a third-person platformer |
| Kind | T |
| Size | XL |
| Tracks | G |
| Needs | `make/designing-a-game`, `make/animation`, `make/levels-saves`, `make/commands` |
| From | gamedev "Tutorial: a third-person platformer" (hands-on G11: a skinned character whose controller `animation.createController` makes, a follow camera with a raycast arm, jump pads, checkpoints, a moving platform in `OnFixedUpdate`, footstep events, menus, a loading scene, a pruned export); `Samples/ThirdPerson` |
| Unit | `plan/allocation/make-c.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/project-platformer` — Project: a third-person platformer

**Covers.** The page builds a smaller Sky Islands from a new Basic 3D project, with a copy of `Samples/ThirdPerson` open
beside it, and opens with its one-paragraph design (an animated robot runs and jumps over floating islands, bounces on
jump pads, collects coins, rides a moving platform and races for the best time to a flag; a main menu, a pause menu and
a loading screen) and its cut list (lanterns, probes, the settings screen, the crate and the attract mode are left for
later). It is the page where the toolbox of block B works together: the reader learns to give a skinned model a
character controller and camera-relative controls, to drive its animator from the movement, to let triggers report to
one state of the course, to reuse the follow camera and the moving platform of an earlier page, to split a game into
scenes that pass nothing but save files, and to ship it pruned with a loading scene. At the end the reader owns a
multi-scene third-person game and its exported folder.

Stage 1, the plan and the assets: the design paragraph, a Basic 3D project named Platformer, the robot, a few Platformer
Kit models and the sounds imported from the release's `Samples/ThirdPerson/Assets/` with a `CREDITS.md`
(`platformer-1`). Stage 2, the course: prefabs of kit blocks at twice their size, each static with a mesh collider, laid
out as islands on a 4 m grid at three heights with gaps to jump, under a `Course` entity; the template's Ground deleted
(`platformer-2`). Stage 3, the player: a `Player` entity tagged "Player" with a character controller and the robot as
its child, turned 180 degrees because glTF models face +Z; the project's Gameplay map (Move, Run, Jump, Respawn, Look,
Pause); `ThirdPersonPlayer`, which walks where the camera looks, turns the body toward its walk with `std::remainder`,
jumps with a short coyote time and goes back to the start when it falls; the robot slides in its rest pose
(`platformer-3`). Stage 4, the camera: two files of `make/characters-cameras` copied into the project from the book's
tutorial files (`book:tutorials/make/characters-cameras/`), `FollowCamera.cpp` and the platform script beside it, never
taught again; the follow camera pointed at the player, orbiting with the mouse and the Look action, its arm shortened by
a raycast, following the drawn position (`platformer-4`). Stage 5, the robot comes alive: the controller made by one
command, then edited in the Asset tab (Speed, Grounded and Jump; Idle, Walk, Run and Jump with their transitions;
Footstep events in Walk and Run), the Animator on the robot, the player script setting Speed and Grounded every update
and Jump when it jumps, and `Footsteps` playing a step at a random pitch on each event (`platformer-5`). Stage 6, a
course to finish: a `Game` entity whose `CourseState` counts coins and time on a HUD; a coin prefab (a sphere trigger
whose child spins), a jump pad prefab (a box trigger that calls the player's `Launch`), checkpoints as marker entities
`Checkpoint1`, `Checkpoint2` found by name, and the goal, which completes the course, shows the time and keeps the best
one in a save file (`platformer-6`). Stage 7, a moving platform, which the sample does not have: a kinematic body with a
box collider across a gap of the course, given the platform script copied in stage 4 (the book's own code, which moves
it between two points in `OnFixedUpdate`); the robot rides it and the camera does not judder, for the reasons
`make/characters-cameras` taught, said in two sentences with a link (`platformer-7`). Stage 8, menus: a `MainMenu` scene
saved with Save Scene As, with Play and Quit, set as the start scene; the course as an asset field of the menu; a pause
menu at time scale 0 with Resume, Restart and Main Menu, the cursor freed while paused; the completion panel's Play
Again and Menu buttons (`platformer-8`). Stage 9, shipping: a `Loading` scene with the loading bar of
`make/levels-saves` (its `LoadingScreen` script linked, not shown again), chosen as the Export dialog's Loading scene;
an export with "Leave out unused assets"; the exported game run from its folder, the loading scene shown while the main
menu loads (`platformer-9`, the end state). The exercises: a lantern that casts shadows (Basic), the settings screen's
Graphics row (Medium) and a regression play-test of the course (Hard).

**Leaves out.**

- Lanterns: point lights that cast shadows → `make/lamps`
- Reflection probes and their bake → `make/reflections`
- The HDR sky and the sun extracted from it → `make/lighting`
- The settings screen (volume, mouse sensitivity, window and vsync) and credits scrolling in a mask → `make/menus`
- The settings screen's Graphics row → `make/quality`
- The attract mode, and state the script module keeps across scene switches → `make/levels-saves`
- The crate the controller pushes into the pit → `make/characters-cameras`
- The menu robot holding a flag with `AttachToJoint` → `make/animation`
- The robot's faces, morph targets that the importer skips → `animation/limits`
- Laying out many prefabs with one command → `make/commands`
- A regression play-test of the course → `make/automated-playtests`
- Why the loading scene plays only while the start scene loads → `worlds/runtime`

**Fit.** `over`: about 10,100 words against XL (8,000). Counted again from the sections: nine stages of four to eight
steps with their results (about 5,800 words), four excerpts explained (1,000), one state for the course, the diagram,
the scene field and the erratum (560), six rules and nine checkpoints (750), three exercises (750), What you will make
and What you need with the design and its cut list (530), the platform's two sentences (60) and the fixed parts (600).
At or over XL's top of 10,000, the page splits after stage 5 (S3; past 10,000 words a page splits into pages, R7) into
"Project: a third-person platformer, the course and the character" (stages 1 to 5 and the lantern exercise, about
5,200 words, L) and "Project: a third-person platformer, a game to finish and ship" (stages 6 to 9 and the other two
exercises, about 5,600 words, L), which the second size pass decides.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:255` | feature | home | Sky Islands as the model of the project: the controller with camera-relative movement, coyote time, checkpoints and respawn; the follow camera; the skinned robot and its controller with Footstep events; coins, jump pads and the goal as trigger prefabs; the course of kit blocks with mesh colliders on a 4 m grid; three scenes; the menus, pause at time scale 0 and save files; what the page leaves out of it |
| `gamedev:377` | code | home | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:54-137`: the player's update: the walk measured, the ground state read, landing sounds, movement along the camera's view, the body turned toward it with `std::remainder` and a turn rate, the jump with coyote time, the animator's Speed and Grounded, checkpoints and the fall back |
| `new:17` | code | home | `Samples/ThirdPerson/Scripts/JumpPad.cpp:38-51`: a trigger that checks the tag "Player", finds the player's script on the other entity and calls its `Launch`, then plays the bounce at its position |
| `new:18` | code | home | `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:212-225`: checkpoints reached on the ground within 3 m, in order; with lines 19-30 (markers found by name, `Checkpoint1`, `Checkpoint2`) and 144-157 (`Respawn` teleports the controller to the last one) |
| `new:19` | code | home | `Samples/ThirdPerson/Scripts/CourseState.cpp:68-92`: the course completed once, the best time kept in a save file, the completion panel's texts and its first button focused, the cursor freed |
| `new:20` | code | use | The loading screen's script, whose excerpt `make/levels-saves` holds and teaches: stage 9 links it and shows only what it changes here (the `Loading` scene's own bar and label, the scene chosen as the Export dialog's Loading scene). Evidence: `Samples/ThirdPerson/Scripts/LoadingScreen.cpp:18-27` |
| `new:21` | concept | use | A moving platform, which the sample does not have: stage 7 gives a kinematic body the platform script copied in stage 4 (the book's own code under `tutorials/`, moved in `OnFixedUpdate`). Why the robot rides it (physics follows a kinematic body with a velocity that reaches the new place in one step; a controller on the ground takes on that velocity and keeps it when it walks off) is taught by `make/characters-cameras`, which the page links. Evidence: `git grep -n OnFixedUpdate 822a7a46 -- Samples/ThirdPerson` finds nothing; `Strata/src/Strata/Physics/PhysicsWorld.cpp:3402-3409`; `Strata/src/Strata/Physics/CharacterControllers.cpp:39-41, 653-654`; `Docs/Manual/Scripting.md:174-175` |
| `new:22` | concept | home | One state for the course: a `Game` entity whose `CourseState` the coins and the goal find by name and report to, found again at each event, never kept. Evidence: `Samples/ThirdPerson/Scripts/CourseState.h:7-9`; `Samples/ThirdPerson/Scripts/Coin.cpp:43-44`; `Samples/ThirdPerson/Scripts/Goal.cpp:15-16` |
| `new:23` | figure | home | Diagram: the entities of the reader's course and their scripts: `Player` (controller, `ThirdPersonPlayer`) with the robot (Animator, `Footsteps`), the camera (`FollowCamera`), `Game` (`CourseState`, `PauseMenu`), the coins, jump pads and goal reporting to it, the moving platform. Evidence: `grep -o '"Class":"[^"]*"' Samples/ThirdPerson/Assets/Scenes/Course.stscene` lists the sample's classes |
| `new:24` | rule | home | A scene the game loads is an asset field of a script, not a path, so that a pruned export keeps it. Evidence: `.claude/skills/strata-make-a-game/SKILL.md:509-510`; `Samples/ThirdPerson/Scripts/MainMenu.cpp:16`; `Samples/ThirdPerson/Scripts/CourseState.h:13` |
| `new:31` | erratum | home | A menu works with a gamepad without a script's focus: with nothing focused, the first direction press or Submit focuses the topmost input canvas's `FirstSelected`, else its top-left selectable, and only focuses. The sample's `Focus()` calls (the main menu's Play, the completion panel's Play Again) save that first press; the page never says that a menu without them is unusable with a gamepad, as `plan/inventory/gameui.md:369-370` does. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:526-531, 539-542, 769-807`; `Samples/ThirdPerson/Scripts/MainMenu.cpp:44-45`; `Samples/ThirdPerson/Scripts/CourseState.cpp:88-89` |
| `new:32` | hands-on | home | Exercise (Basic): a lantern that casts shadows, a point light under a tree of the course with a glowing material, as the sample's two lanterns are. Evidence: `Samples/ThirdPerson/README.md:28` |
| `new:33` | hands-on | home | Exercise (Medium): the settings screen's Graphics row, four toggles in one group that set the quality preset with `Graphics::SetPreset` and keep it with `Graphics::Save`, as the sample's settings menu does. Evidence: `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:28-36`, `:114-118` |
| `new:34` | hands-on | home | Exercise (Hard): a regression play-test of the reader's course, a command script that drives the player with `input.sequence` on the Gameplay actions, places it at a coin and at the goal, and expects the coin counted and the course completed, waiting with `until` in steps, as the sample's own script does. Evidence: `StrataTests/Editor/ThirdPersonCommands.json.in:41`, `:74-75`, `:91-93` |
| `gamedev:470` | figure | home | The sample's course with a coin and a jump pad (its `Screenshots/Course.png` and `JumpPad.png`) and its main and pause menus, as the game the page follows; the settings menu's Graphics row is `make/quality`'s |
| `gamedev:544` | hands-on | home | G11, the page's whole path: the skinned character whose controller `animation.createController` makes, the follow camera with a raycast arm, jump pads, checkpoints, a moving platform in `OnFixedUpdate`, footstep events, menus, a loading scene and a pruned export |
| `gamedev:378` | code | use | The follow camera: the book's own `FollowCamera.cpp` of `make/characters-cameras`, copied in stage 4 from `book:tutorials/make/characters-cameras/`, of which the sample's file is the finished form (its home is `make/characters-cameras`) |
| `gamedev:381` | code | use | The robot's controller as data, of which stage 5 builds a smaller one (its home is `make/animation`) |
| `gamedev:427` | figure | use | The sample's scene flow, of which the page builds the menu, course and loading scenes without the attract mode |
| `gamedev:301` | concept | use | A model that walks backwards: glTF faces +Z while forward is -Z, so the robot child turns 180 degrees |
| `gamedev:331`, `gamedev:333` | concept | use | Characters and cameras that follow, as stages 3 and 4 apply them |
| `gamedev:335` | concept | use | Animation for makers, as stage 5 applies it |
| `gamedev:342` | concept | use | Game flow: the menu, the course and the loading scene; state passed only through save files |
| `gamedev:348` | concept | use | Shipping: the pruned export and the exported game |
| `gamedev:490`, `gamedev:492` | rule | use | The camera follows the drawn position in `OnLateUpdate`; the respawn uses `Teleport` |
| `gamedev:496` | rule | use | `GetScript<T>` found again at each event, never kept across frames |
| `gamedev:498` | rule | use | Controls read as the Gameplay map's actions |
| `gamedev:500-501` | rule | use | The player has a controller and no rigid body; the coins and pads are convex triggers, because triggers do not see the course's mesh colliders |
| `gamedev:504` | rule | use | Entities do not survive `Game::LoadScene`: the best time goes through a save file |
| `gamedev:511` | rule | use | Pruned exports drop what is loaded by path: why stage 8 makes the scenes asset fields |
| `gamedev:519` | rule | use | The imported assets are CC0 and credited |
| `gamedev:628-629`, `gamedev:631`, `gamedev:633`, `gamedev:647`, `gamedev:651` | term | link | Character controller, coyote time, the animator's words, animation event, save file, pruned export |
| `gamedev:661` | term | link | Attract mode, named as left out |
| `gamedev:379-380` | code | link | Module state across scenes and the Graphics row, named as left out |
| `animation:185` | feature | use | `animation.createController`, the one step of stage 5 that only a command can do |
| `animation:363` | code | use | `Footsteps.cpp` and the lines that set the animator's parameters, written again in stage 5 (its home is `make/animation`) |
| `animation:212` | feature | link | The sample's robot, the running example of part `animation` |
| `scripting:385` | code | use | The coin script of stage 6 (its home is `make/recipes`) |
| `scripting:122`, `scripting:123`, `scripting:125`, `scripting:126`, `scripting:127`, `scripting:128`, `scripting:129`, `scripting:131`, `scripting:133` | feature | use | The SDK the page calls: input actions and the cursor, `Time::SetTimeScale` and unscaled time, `Collision` and `RigidBody`, `CharacterController`, `Audio::PlayOneShotAt`, `Animator`, `Game` (`LoadScene`, `ReloadScene`, `Quit`, save files, load progress), `UIElement`, `Random` |
| `physics:42` | feature | use | A kinematic body follows its entity with a velocity that reaches the target in one step: the moving platform |
| `physics:134` | feature | use | A controller carries the velocity of the platform it stands on, and keeps it when it leaves |
| `physics:408` | rule | use | Triangle meshes only on static bodies, and triggers do not see them: the course is static, the platform a box |
| `physics:425` | rule | use | Move what others ride in `OnFixedUpdate` |
| `gameui:226` | feature | use | The sample's main menu, of which stage 8 builds a smaller one |
| `audio-input:183` | feature | use | The sample's Gameplay map, which stage 3 builds again |
| `worlds-runtime:127` | feature | use | The loading scene, which plays while the start scene loads |
| `worlds-runtime:160` | feature | use | Pruning: the export keeps only what the scenes reference |
| `worlds-runtime:168` | feature | use | The Export dialog's Loading scene and "Leave out unused assets" |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Stage 1: the one-paragraph design and a cut list | `make/designing-a-game` | must |
| Stage 1: a project from the Basic 3D template; Save Scene As | `make/project-files` | must |
| Stage 1: importing glTF models and sounds; the import scale; licenses and a `CREDITS.md` | `make/assets` | must |
| Stage 2: prefabs, their instances, placing them by drop | `make/prefabs` | must |
| Stage 2: positions typed in the Inspector | `make/transforms-units` | must |
| Stage 2: static bodies with mesh colliders | `make/physics` | must |
| Stage 3: a model that faces +Z while forward is -Z | `make/transforms-units` | must |
| Stage 3: input actions, the Gameplay map, `IsActionPressed` and `GetActionValue` | `make/input` | must |
| Stage 3: a vector's length and `normalize`, the cross product, `atan2`, the camera's forward on the ground | `make/gameplay-math` | must |
| Stage 3: a character controller: `Move`, `Jump`, `IsGrounded`, `Teleport`; coyote time | `make/characters-cameras` | must |
| Stage 3: a class in a header and its source file; calling a public method of another class | `basics/programming-3` | must |
| Stages 3 and 6: entity and asset fields | `make/script-fields` | must |
| Stage 4: the follow camera with its raycast arm; `GetDrawnPosition` in `OnLateUpdate`; the locked cursor | `make/characters-cameras` | must |
| Stage 5: running a command with StrataCLI | `make/commands` | must |
| Stage 5: a controller's parameters, states, transitions and events in the Asset tab; the Animator; `OnAnimationEvent` | `make/animation` | must |
| Stage 5: a random pitch from `Random` | `make/recipes` | helps |
| Stage 6: triggers, tags and `OnTriggerEnter` | `make/physics` | must |
| Stage 6: finding another script with `GetScript<T>` at each event | `make/timers-events` | must |
| Stage 6: HUD texts on a canvas | `make/hud` | must |
| Stage 6: one-shot sounds at a position, requested in `OnCreate` | `make/sound` | must |
| Stage 6: save files with `Game::WriteSaveFile` and `Game::ReadSaveText` | `make/levels-saves` | must |
| Stage 7: `OnFixedUpdate` and the fixed step | `make/script-loop` | must |
| Stage 7: platforms moved in `OnFixedUpdate`; kinematic bodies | `make/characters-cameras` | must |
| Stage 8: buttons, `OnUIClick`, focus; a pause menu at time scale 0 | `make/menus` | must |
| Stage 8: `Game::LoadScene`, `ReloadScene` and `Quit`; entities do not survive a scene switch | `make/levels-saves` | must |
| Stage 9: a loading screen that shows progress | `make/levels-saves` | must |
| Stage 9: the export, the Export dialog, pruning, running the exported game | `make/export` | must |
| Exercises: a regression play-test of the course | `make/automated-playtests` | helps |
| Exercises: the settings screen's Graphics row | `make/quality` | helps |
| Exercises: a lantern with shadows | `make/lamps` | helps |

**Starting state.** A new project made in the launcher from the Basic 3D template (`startsFrom {"template":
"basic3d"}`), named Platformer, with the template's Main Camera, Sun, Sky, Ground and Post Process
(`StrataEditor/src/Editor/ProjectTemplates.cpp:51-87`); stage 2 deletes the Ground and stage 4 replaces the camera's
script setup. The page starts from no checkpoint of an earlier page. Stage 4 copies two files of
`make/characters-cameras`, `FollowCamera.cpp` and the platform script, from `book:tutorials/make/characters-cameras/`
(the stage's `files` in the tutorial file, pipelines.md §6.2), so that the two pages agree by construction. Beside
it the reader opens a copy of the sample (Open Sample > Third-Person Adventure) to compare. The files imported in
stage 1 come from the release's
`Samples/ThirdPerson/Assets/`: `Models/Robot/RobotExpressive.glb`, a few models of `Models/Platformer/` with their
`Textures/colormap.png`, and the sounds `Jump.ogg`, `Land.ogg`, `Coin.ogg`, `Bounce.ogg`, `Complete.ogg` and
`Footsteps/Grass1.ogg` to `Grass4.ogg`, all CC0 (`Samples/ThirdPerson/CREDITS.md`). Each stage starts from the
checkpoint of the stage before (`platformer-1` to `platformer-8`); `platformer-9` is the end state.

**Command-only steps.**

- Stage 5, making the animation controller: no menu or button creates one (the Content Browser's New menu holds
  Folder, Material, World and Script: `StrataEditor/src/Panels/ContentBrowserPanel.cpp:564-580`), only
  `animation.createController` (`StrataEditor/src/Editor/EditorAnimationCommands.cpp:153`). The step says so in its
  first sentence, lists the robot's clips with `animation.info` and creates the controller with its states through
  StrataCLI; its parameters, transitions and events are then edited in the Asset tab, as `make/animation` taught. A
  step that calls a command needs `make/commands`, which is in the page's Needs and teaches StrataCLI.
- Not command-only: laying out the course. The editor tab drops each prefab and types its position; the command tab
  places them all with one `prefab.instantiate {instances}`, a command called through StrataCLI as in stage 5.
- No step runs a command script. The Hard exercise does, as `make/automated-playtests` teaches; that page is in the
  page's Needs closure through `make/commands`.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-c-1 | must | shape | `make/project-tetris` stages 2 to 6, `make/project-platformer` stages 3, 6 and 8 | The steps cannot be followed from the lists. About 470 of the 829 lines of the reader's Tetris are in no row: the shapes, moves, drops, `Fits` and `SpawnNext` of `TetrisGame.cpp`, and the board's fields, `ST_SCRIPT_CLASS` block, `SetupInput`, `CreateCells`, `FindCells`, `NewGame` and `HandleStep`. On the platformer, `ThirdPersonPlayer.h`, the player's helpers, `CourseState.h`, `Goal`, the main menu's script and the pause menu's script have no row. Neither page says whether the reader types these lines or copies them. Pages of track G show at most 25 lines per fence, and a stage's `files` may copy only from `book:tutorials/` or `Samples/*/Assets/`, not from `Samples/*/Scripts/`. | Each page's What you need names its script files under `book:tutorials/make/project-tetris/` and `book:tutorials/make/project-platformer/` (the book's copies of the samples' scripts, quoted with `src="book:…"`), with their downloads. Each stage names the files it adds, copies them through its `files`, and walks through the excerpts its rows name. The pause menu reuses the script that `make/menus` built. About 150 words per page. The other way, every part quoted on the page, does not fit XL (forPlanner). | `allocation/make-c.md:97-101`, `:141-145`, `:304-308`; `pipelines.md:879`, `:894-896`; `style.md:646`; `allocation/make-b1.md:831` (`make/menus` homes `PauseMenu.cpp:97-122`); pin: `Samples/Tetris/Scripts/TetrisGame.h:1-108`, `TetrisGame.cpp:1-269`, `TetrisBoard.cpp:1-452`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.h:1-70`, `PauseMenu.cpp:1-138`, `CourseState.h:1-48` |
| critic-make-c-2 | must | missing-item | `make/project-tetris` stages 2 and 3 (`gamedev:372`, `new:8` to `new:10`, `gamedev:373`); `make/project-platformer` stage 3 | The code the reader writes uses C++ that no page of track G teaches and no row names. These are `constexpr` constants (`TetrisGame.h:14-18`), an enum with a fixed type and `static_cast` to and from it (`h:21`, `cpp:37`, `:261`), `using` for a type's second name (`h:34`), the unnamed namespace (`cpp:8`), `return {}` (`cpp:126`) and `std::swap` (`cpp:263`). There is also a lambda given to `std::none_of` (`cpp:224`), a lambda kept in an `auto` variable (`TetrisBoard.cpp:291`), and `static constexpr` members and `std::pow` (`TetrisBoard.cpp:106-107`, `:192`). Their homes, `basics/cpp-modern` and `basics/cpp-generic`, are not on track G. The page's only C++ rows name `basics/programming-1` to `-3`. | Add a new concept item on `make/project-tetris`. It explains each of these where it is first used, at the use level, in one to three sentences, with a link to its home (about 400 words). Add Assumes rows of depth `helps` that name `basics/cpp-modern` and `basics/cpp-generic` (N2). `make/project-platformer` gets a `helps` row naming `make/project-tetris`, and says what `std::clamp` does where `ThirdPersonPlayer.cpp:100` uses it (about 30 words). With critic-make-c-1, -4 and -5, the Tetris estimate passes 10,000 words, so the page splits by S3 (the second size pass). | `allocation/make-c.md:190-192`; `allocation/basics-a.md:156-384` (programming-1 to -3: no `constexpr`, lambda or `static_cast`), `:875` (lambdas on `basics/cpp-generic`), `:943` (`static_cast` on `basics/cpp-modern`); `style.md:653-659`; `tracks.md`, track G; pin: `Samples/Tetris/Scripts/TetrisGame.h:14-34`, `TetrisGame.cpp:8`, `:126`, `:224`, `:263`, `TetrisBoard.cpp:106-107`, `:192`, `:291`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:97-100` |
| critic-make-c-6 | should | missing-item | `make/project-platformer` stage 2 and `new:34` | The course is 35 static bodies with triangle-mesh colliders. When play starts, the simulation holds its steps until these meshes are loaded and cooked: at most `MeshWaitTimeout` (10 s), and after that a warning names what is missing. Nothing moves during the hold. The page does not say this. The Hard exercise's play-test has no wait, so its input steps could run while physics holds. The sample's script first waits for `physics.stats` to report `/waitingForMeshes` false. `physics:63` is homed on `physics/building-bodies`, which is not on track G. | Add a `use` row of `physics:63`. Stage 2's You should see gets one sentence: Play holds for a moment while the course's colliders are cooked. The Hard exercise's solution pauses and waits with `until` for `/waitingForMeshes` false before its first input (about 60 words). How long the hold lasts was read from the code, not run (R39); the check of the pending window of mesh colliders could list this page too (forPlanner). | `allocation/make-c.md:247-249`, `:316`, `:344`; `allocation/physics.md:329`; `inventory/physics.md:63`; pin: `Strata/src/Strata/Physics/PhysicsWorld.h:73-78`; `Strata/src/Strata/Physics/PhysicsTypes.h:51`, `:185`; `StrataTests/Editor/ThirdPersonCommands.json.in:21-22`; `Samples/ThirdPerson/README.md:20` |
| critic-make-c-7 | should | missing-item | `make/project-platformer` stage 3 | The sample's robot is a child of the player, turned 180 degrees and scaled to 0.4, inside a controller of Height 1.8. At scale 1 the robot is about 4.1 m tall: its `Head_end` joint stands 4.08 m above its feet in the file's rest pose. The page turns the robot but never scales it. `make/animation`, which places the same robot under a player, does not scale it either. The reader's robot would stand more than twice as tall as its capsule. | Stage 3 sets the robot child's scale to 0.4 and says why in one sentence: the model is larger than a person at the import scale of 1 (about 30 words). `make/animation` step 1 does the same (unit make-b1). | `allocation/make-c.md:249-250`; `allocation/make-b1.md:616-618`, `:741-745`; pin: `Samples/ThirdPerson/Assets/Scenes/Course.stscene:151-152` (Player: Height 1.8; Robot: Scale 0.4, rotation 180 degrees about Y); `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb.meta` (Scale 1.0); the joints' heights computed from the glb's node transforms by `docs-work/C2/critic-make-c/glb_height.py` |
| critic-make-c-12 | should | duplicate | `make/project-platformer` stage 5 (`animation:363`) | Stage 5 builds again, from the same angle, what sections 2 to 6 of `make/animation` built on the same robot under the same kind of player. These are the parameters Speed, Grounded and Jump; the states Idle, Walk, Run and Jump; the Footstep events in the Asset tab; the `Footsteps` script; and the player setting Speed and Grounded (Rule D). Stage 4 already copies the camera of `make/characters-cameras` instead of teaching it again. | Stage 5 makes the whole controller in one `animation.createController` call: parameters, states with their Footstep events, and transitions, with the parameters read from a file (`@file`, taught on `make/commands`). The command accepts all of this. The stage copies `Footsteps.cpp` from the tutorial files of `make/animation`, as stage 4 copies the camera, and one sentence links `make/animation` for the Asset tab. G11's "controller made with `animation.createController`" still holds. This applies Rule D; it is not a cut to make the page fit. The page loses about 400 words (forPlanner). | `allocation/make-c.md:256-259`, `:338`, `:370`, `:402-407`; `allocation/make-b1.md:619-638`; pin: `StrataEditor/src/Editor/EditorAnimationCommands.cpp:29-41`, `:153-157`; `Samples/ThirdPerson/Assets/Animations/Robot.stanimator` |
| critic-make-c-17 | could | missing-item | `make/project-platformer` stage 6 (`new:19`) | Stage 6 shows the course's time on the HUD and in the completion panel. The sample formats the time with `std::snprintf` and `std::lround` ("1:05.3"), which no page of track G teaches. The page's list does not say how the time is written. | The page writes minutes and seconds with its own small function: integer division, `%` and `std::to_string`, from `basics/programming-1` and `-2`, shown as a sketch (about 80 words). The other way: the page shows `ThirdPerson::FormatTime` with a two-sentence aside on `std::snprintf`. | `allocation/make-c.md:259-262`, `:307`; pin: `Samples/ThirdPerson/Scripts/ThirdPerson.cpp:153-159`; `Samples/ThirdPerson/Scripts/CourseState.cpp:85`, `:109-111` |
| critic-make-c-18 | could | other | `make/characters-cameras` (unit make-b1), for stage 4 of `make/project-platformer` | Stage 4 copies `FollowCamera.cpp` and the platform script from `book:tutorials/make/characters-cameras/`. The section of `make/characters-cameras` names neither file as something its tutorial leaves, nor the platform script's class, nor the fields that stage 4 sets. The two pages agree only if the briefs say so. | The Covers or Starting state of `make/characters-cameras` names the two files under its tutorial folder, the platform script's class and the fields that the platformer sets (about 30 words). The make-b1 packet's answer to make-c-q3 asks the same. | `allocation/make-c.md:253-256`, `:391-392`; `allocation/make-b1.md:502-511`, `:522`; `docs-work/C/packets/make-b1/answers.md:241-252` |
