# Notes: start/first-game

## New terms

The page defines these in bold once; the glossary homes them on later pages (`make/physics`, `make/first-script`, `make/scenes-entities`), so the page links the home where the brief asks (collider, field) and otherwise defines them in one sentence. Add them to the glossary or move the definitions if the planner settles other homes.

- **scene**: one place of the game, a list of things and where they stand. Home: `make/scenes-entities` (used here first). Aliases: scenes.
- **entity**: a named object that holds nothing but the components you give it. Home: `make/scenes-entities`. Aliases: entities.
- **component**: one piece of data and behavior on an entity. Home: `make/scenes-entities`. Aliases: components.
- **template**: a ready-made starting point for a project. Home: `start/first-game` if the glossary has no other. Aliases: templates.
- **rigid body**: a component that says an entity is a solid object, with mass, that forces can move. Home: `make/physics`. Aliases: Rigid Body.
- **collider**: an invisible shape that tells physics where an entity is solid. Home: `make/physics`. Aliases: colliders.
- **script class**: a class of a script, of which every entity that uses it has its own copy. Home: `make/first-script`.
- **field**: a value the Inspector shows and each entity keeps for itself (`ST_SCRIPT_FIELD`). Home: `make/first-script`. Aliases: script field.
- Plain-sentence definitions (not bold, so no term): launcher, Play, Scene view, Game view, toast.

## Requests

- `tools/data/names.txt`: **Tetris** (the sample's name; the only `word-list` failure left, 10 uses).
- Layout file `layouts/first-game.ini` (named by the figure recipes of `src/content/figures/start/first-game.json`): the editor layout of the pictures, with Hierarchy, Scene and Game views, Inspector, Content Browser and Console open.
- Figures `launcher` and `new-project` wait for `tier 2: editor screenshot`: the pin's recipes cannot open the launcher or a dialog. The brief's launcher recipe also serves the Open Sample dialog (`editor-ui/launcher-dialogs`); no separate figure of that dialog is on this page.
- Figure recipes were not run: the `Cube`, `Ramp` and `Top` setups use `entity.create`, `component.add`, `component.set`, `script.add`, `selection.set`, `editor.showPanel` as other pages' recipes do; `editor.showPanel` with the panel `Console` is not checked.
- The tutorial file has one `startsFrom` (a Basic 3D project named `FirstGame`), but section 1 works on a copy of the Tetris sample. Stage 1 is therefore empty (no commands) and only the later stages run. The planner may split section 1 into its own file or let the runner start a stage from a sample.
- `tools/external-hosts.txt`: gameprogrammingpatterns.com for the Further reading entry on the game loop (cited without a link now).
- Passive-voice warnings (14) are left: they describe states of the editor ("is selected", "is open") and a rewrite would name no actor.

## Not verified

- The physics runs were run (see "Tutorial run"); only the bounces stay unseen.
- The editor's layout: the Hierarchy, Inspector, Content Browser, Console and Problems panels are named as they are in the code, but their default positions ("on the left", "on the right") come from the brief and the usual layout, not from a layout file at the pin.
- A double-click on a number in the Inspector enters text: the widgets use `ImGui::DragScalar`, whose double-click and Ctrl+click behavior is ImGui's own, not checked in the editor.
- The green arrow of the Move gizmo points up: from the brief, not from the gizmo code (ImGuizmo's defaults).
- F2 renames the selected entity in the Hierarchy: the Edit menu and `EditorLayer::RenameEntity` show it; the page assumes the Hierarchy has the keyboard focus after **+ ▸ Cube**.
- After the first Play of a new project that uses no script, no build runs (`EditorContext::GetPlayBuildReason` returns nothing when no scene uses scripts); only read in code, not run.
- The status bar's "Building to play" is shown only while a build that Play started runs (`EditorLayer::DrawScriptsPill`); how long it lasts depends on the machine.
- The toast's wording for a missing toolchain is quoted from `ScriptToolchain.cpp` for Windows ("Desktop development with C++"); the Linux and macOS texts differ and the page names only the Windows one as an example.
- The cube at height 3 may start above the Game view's top edge (the camera's field of view is 60 degrees at 6 units; computed, not seen).
- `log.read` returns the log lines as `messages`, each with `message`: the tutorial checks the Spinner line (run).
- Hot reload keeps the running value (90) and runs `OnReload` instead of `OnCreate`: stated in `Script.h` lines 49-52; the build-while-playing behavior was not run.

## Findings not applied

- critic-start-2: applied (sections 3, 4 and 5 end with **File ▸ Save Scene**; the close dialog and **Recent projects** or **File ▸ Open Recent** are told in section 5). `gamedev:36`, `gamedev:513` and `editor-core:131` are not linked, because their homes (`make/editor-tour`, `editor/saving`) come later.
- critic-start-4: applied (**Rigid Body**, **Gravity Scale**, "Degrees Per Second", the sentence about names with spaces). The **Character Controller** part belongs to `start/coming-from`.
- critic-start-5: applied (two choices, **Add Component ▸ Script** then **Add Script...**, and the "No script module is loaded" note).
- critic-start-6: applied (save, stop the game, then **Ctrl+B**; the three causes; the reset arrow).
- critic-start-7: applied with a 35 degree ramp typed into the Inspector, the mixing rules with numbers, and a link to `make/physics` (the home `physics/new:27` is on `physics/bodies-colliders`, which this page does not link).
- critic-start-8: applied (**Scripts ▸ External Editor...**, the list, **Apply**).
- critic-start-9: applied (rigid body, collider and field each in one sentence; links to `make/physics` and `make/first-script`).
- critic-start-14: applied (Cmd on macOS once in "What you need").
- critic-start-18: applied (the Escape row of the key table).
- Brief item `new:25`: the three exercises are present; exercise 2 has a worked solution file. Exercises 1 and 3 have no solution file: an answer in words only.
- Brief: "Play" and "Stop" are icon buttons without a label at the pin (`EditorLayer::DrawPlayControls`), so the page names them by their shape and **Ctrl+P**, not as bold labels.
- Brief: the Tetris copy is opened with **Open Sample... ▸ Tetris**; at the pin the button opens a menu of the five samples, then the **Open Sample** dialog with **Copy and Open**.

## Figures

- `result` (published, three rounds). Round 1, `camera: "scene"` (the template's camera at 0, 2, 6 looking at the
  origin): both cubes sat at camera height near the top edge and showed only their flat front faces, the ground filled
  the lower two thirds. Round 2, a camera from the front right and above (3.5, 4.5, 7.5, fov 32): solid cubes, but the
  ramp was cut by the bottom edge and the sky left the frame. Round 3 (4.5, 3.2, 10 toward -0.8, 1.3, 0, fov 32): the
  falling cube hangs just above the ramp's high end with its shadow on the ramp, the Top cube floats to the left, sky
  above. Caption, alt and shows now say the picture is a moment into play (the cube is about to land), since a still
  cannot show the slide or the turn.
- Editor figures, taken with the provisional build (5b975ad2831e, `--provisional`) in three rounds and looked at;
  nothing published, every editor recipe has `waitsFor: tier 2: editor screenshot`. Whole-window figures use
  `layouts/first-game-960.ini` (960 × 540, a copy of `make-scenes-entities.ini`); the panel figures use
  `layouts/first-game-tall.ini` (1280 × 800, Inspector column 380 px, bottom tabs 200 px so that the Console shows six
  lines; from `materials.ini`). `layouts/first-game.ini` (1280 × 720) is left for the other pages that name it.
  - `launcher`: cannot. `take` always opens a project, so no command shows the launcher; the recipe is left as it was.
    The page needs a take that starts the editor without a project, or a diagram of the launcher's parts.
  - `tetris-playing` (good, round 2): round 1 left the Scene view in front after `play.start`; the recipe now builds
    with `wait`, plays, waits 600 frames (the build toast leaves) and shows the Game view. Caption: the play button
    is green and the status bar reads Playing (the stop button is not lit).
  - `new-project`: cannot be published as taken. `editor.showDialog {dialog: "newProject"}` opens the dialog with
    Basic 3D chosen, but its Location and "Creates" lines show the user's home folder with the user name, and no
    command or preference sets the default location. The name reads "My Project" (typed text cannot be shown), so
    the shows no longer name FirstGame. The page needs a default location outside the home folder for the take (an
    option of `editor.showDialog`, or a take that gives the editor its own home folder).
  - `project-created` (good, round 1): the five entities and the ground under the sky; the alt says grey-brown,
    since the ground does not read dark in the Scene view.
    Viewer's report (2026-11-18): the page calls the ground dark (step 2: "a scene with a dark ground under a sky";
    the entity list: "a flat 20 by 20 area of dark stone"), but the picture shows a mid-tone grey-brown ground (sRGB
    about 122, 115, 109) under a blue sky. The fault stands, in the page's words, not in the picture: the template's
    ground is a dark stone material (linear base color 0.16, 0.15, 0.14 in `ProjectTemplates.cpp`), but its Post
    Process has automatic exposure on (+0.25), so the view meters the ground near middle grey; the reader's own editor
    shows the same default Scene view, so a recipe that framed more sky to darken the ground would show the reader
    something the editor does not. Recipe, caption, alt and shows are left as they are (they already say grey-brown);
    nothing retaken. The page's words need: step 2 "a scene with a grey-brown ground under a blue sky", and **Ground**
    "a flat 20 by 20 area of grey-brown stone".
  - `cube-inspector` (good, round 1): the recipe placed the cube at height 3; the page's step puts it at 0.5 (resting
    on the ground), as the recipe now does.
  - `cube-placed` (good, round 3): round 1 had the cube at the view's top edge with its gizmo cut; round 2 framed it
    with `camera.set` but showed the Main Camera's view lines over the ground; round 3 hides scene gizmos
    (`viewport.setSettings`), sets the Translate gizmo and a closer camera (2.5, 3.5, 5.5 toward -0.5, 1.8, 0).
  - `rigid-body` (good, round 1): the Inspector panel at 1:1 (Type Dynamic, Mass, Friction 0.5, Restitution 0).
  - `cube-falls` (good, round 3): a still cannot show motion; the recipe starts play paused and runs 32 fixed steps
    (half a second): the cube has landed on the ramp's high end. Same camera and hidden gizmos as `cube-placed`.
    Caption and alt say the game is paused half a second after Play.
  - `script-attached` (good, round 1): the Inspector panel: Script, the class and Degrees Per Second at 90. The
    captions avoid the class's name (not on the word lists).
  - `spinner-console` (good, round 3): the recipe copies the tutorial's `Spinner.cpp` (360 and `OnCreate`). Every
    command the take runs writes a Console line, and round 2's taller Console also showed the build lines with the
    work folder's path; round 3 adds an `editor.wait` after the build and a Console six lines high, so the Spinner
    line sits among command lines only. The caption says the lines around it record the commands.
- Pin v0.8.0 (319075e3), 2026-11-23, one hold, one round: the `waitsFor` lines are gone (`check` named them), and
  every figure was taken at the pin's Release build without `--provisional`.
  - `result`: taken again and compared with the published file: 0 pixels differ, so `publish` kept it as unchanged
    (same original; its stamp still names 822a7a46, which the tool keeps for a bit-identical picture).
  - Published after a look: `tetris-playing` (Game view in front, piece falling, score, green play button, Playing in
    the status bar), `project-created`, `cube-inspector` (cube at 0.5 on the ground, Transform, Mesh Renderer, Box
    Collider), `cube-placed` (green arrow up, shadow below), `rigid-body` (Type Dynamic, Mass 1, Friction 0.5,
    Restitution 0), `cube-falls` (paused, cube on the ramp's high end, yellow Paused notes), `script-attached`
    (Spinner, Degrees Per Second 90), `spinner-console` (the Spinner line at 360 among command lines, no path).
    Recipes, captions and alt unchanged: each claim is in the picture.
  - `launcher`: still cannot. The take opened the Basic 3D project, so the shot is the editor, not the launcher; not
    published. Nearest honest picture: none by commands; the page needs a take that starts the editor without a
    project, or a diagram of the launcher's parts.
  - `new-project`: still cannot be published. The dialog is right (Basic 3D chosen, Empty beside it, Name "My
    Project", Location, the "Creates" line, Cancel and Create), but Location and "Creates" show the user's home folder
    with the user name. `editor.showDialog` has no location parameter at the pin. The pin's dialog reads a remembered
    location from the layout's ini (section `[StrataLauncher]`, `ProjectDialogs::SettingsReadLine`) and the editor
    option `DefaultProjectLocation`; a `[StrataLauncher]` location in `layouts/first-game-960.ini` (a neutral path such
    as `C:\StrataProjects`), or a `take` that passes that option, would make the picture publishable. The layout is
    not this card's to change.
- Last figures at the pin (2026-11-24, the tool's launcher take and neutral paths), both published after a look:
  - `launcher`: the recipe drops `project` and sets `editorWindow.launcher: true`. Round 1 at 960 × 540
    (`first-game-960.ini`): the three buttons, "No recent projects yet" and the two template cards, but no sample card.
    Round 2 at 960 × 640 (`make-performance-result.ini`; the launcher ignores the docking): the two template cards and
    the first two sample cards (High Desert Outpost, Third-Person Adventure) show. The card that connects an agent sits
    below the cards, out of any window that still reads at the column's width, so the caption says it lies further
    down; the page's paragraph names it only as a part of the launcher. Shows, caption and alt follow the picture.
  - `new-project`: the take's editor sees its copy as `S:\Projects`, so Location reads `S:\Projects` and the last line
    "Creates S:\Projects\My Project"; no path of this machine shows. The name is the dialog's own "My Project" (typed
    text cannot be shown). The pin first offers `StrataProjects` in the home folder (`ProjectDialogs::GetDefaultLocation`,
    `c_DefaultLocationName`), so the caption says the picture shows the folder it was taken in, not the reader's.
- Page text the pictures contradict (page words not changed): "a scene with a dark ground" (line 180) and "dark
  stone" (line 190): the ground reads grey-brown in the Scene view. "the Game view comes forward" (lines 103, 296):
  after `play.start` the Scene view stayed in front (the Play button was not tried). "one line in the Console" (line
  707): the Console holds other lines too (build and command lines).

## Clerk

- Not admitted: scene, entity, component, template, rigid body, collider, script class and field are glossary entries
  homed on other pages (`make/scenes-entities`, `world/ecs`, `editor/projects`, `physics/bodies-colliders`,
  `make/first-script`); only a home page words its terms.
- `tools/data/names.txt`: Tetris added. `tools/external-hosts.txt`: `gameprogrammingpatterns.com` added.
- The layout file, the figures and the tutorial's two starting points are the planner's.

## Tutorial run

Run 2026-11-18 at the pin's Release build, four rounds; the tutorial and exercise 2 pass.

- Round 1 passed as written. The file was thinner than the page: stage 4 played once, after the ramp and the new
  Friction and Restitution, and checked nothing; stage 5 copied the 360 version at the stage's start, so the 90 of
  the template was never built, attached or seen.
- The file now follows the page's order and checks its "You should see" values: the Ground's 20 by 20 scale and its
  collider one meter thick with its top at 0; the cube's three components; Rigid Body's Type Dynamic; the cube resting
  at (-0.5, 0.5) after 180 steps and back at height 3 after Stop; on the ramp, (0.65, 1.08) after 60 steps and at rest
  on the ground at x 1.91 after 300 (turned 90 degrees about Z: it tips over once; the quaternion's sign varies, so
  only the place is checked); with Friction 0.05 and Restitution 0.7, x 1.17 after 60 steps and x 8.6 on the ground
  after 300. Stage 5 builds the template's Spinner (field 90 by `script.get`, a quarter turn in 60 steps), then
  `Spinner-360.cpp` (a half turn in 30 steps), then the page's final listing with `OnCreate` (the line in the log).
- The bounces the page promised were not seen: sampled every 5 steps, the cube meets the ramp at about step 27 without
  rising, and on the ground its height goes from 0.525 to 0.599 once while it tumbles. The page's step 5 now says
  what is seen (faster down the ramp, far across the ground), and the intro no longer names a bounce. A run that
  samples every step could show whether a small bounce happens; the Restitution text (the pair takes the larger) is
  from box3d's mixing and stays.
- The command tabs now stop what they play (`play.stop` after each `play.start`, as the editor tabs press Stop), so a
  reader of the tabs builds with the game stopped as the page asks; the last step's tab builds and plays before
  `log.read`. Step 5 of "Make it fall" gains `play.start` and `play.stop`.
- `scene.save` after the `play.stop` before each build that carries a file: each part of the reader's copy starts a
  fresh editor, and without the save the second part found no `Top` (round 2). The page has no save there, because a
  reader keeps the editor open.
- Not run: `script.setExternalEditor` and `script.open` (they change the user's setting and start a program).
- Final run 2026-11-24 with the official v0.8.0 package (`Strata-0.8.0-windows-x64.zip`): the tutorial and exercise 2
  pass as written; the pin-build run of 2026-11-23 was still current. `tutorials.py check --release` finds nothing.
- Walk G-final-1 (2026-11-24): the listings now quote the reader's file. `Spinner-90.cpp` is the text of
  `MakeExampleScript` (`StrataEditor/src/Editor/ScriptProject.cpp:231-257`) byte for byte, made from the pin's source;
  `Spinner.cpp` and `exercise-2/Spinner.cpp` gained the template's five-line comment and blank line, so the page's line
  numbers are those of the file on disk. The "Attach the script" tab now runs `script.get`, as the file did.
  Run 2026-11-24 after the change: the tutorial and exercise 2 pass at the pin's Release build and with the official
  v0.8.0 package (`--package Strata-0.8.0-windows-x64.zip`).
