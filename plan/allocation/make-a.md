# Allocation: make-a

## `make/editor-tour` — A tour of the editor

**Covers.** The page creates Coin Run's project and walks the editor in the order a game maker meets it. It starts at
the launcher that `start/first-game` showed: **New Project**, the name `CoinRun`, the **Basic 3D** template and the
default location, so the editor opens on `Scenes/Main.stscene`; the launcher's way to go on without a project, and
**File ▸ Show Launcher** to come back. Then the default layout, labelled panel by panel: the Scene and Game tabs in the
middle, the Hierarchy on the left, the Inspector and Asset tabs on the right, the Console, Problems and Content Browser
at the bottom, the main toolbar (the gizmo tools Q, W, E and R, World and Local, Snap, Play, Simulate, Pause, Step and
Stop, the build and export buttons) and the status bar, whose pills each lead to the panel that explains them. Each
menu (File, Edit, View, Entity, Scripts, Help) in one sentence, with **View ▸ Reset Layout** for a panel that went
missing and **File ▸ Preferences ▸ Interface** for a screen that needs a larger interface; the Bedrock theme named
once. Then moving in the Scene view, one step each: select the Ground by clicking it
in the view and in the Hierarchy, orbit (Alt and the left button), pan (the middle button), dolly (the wheel), fly (the
right button held with W, A, S, D, Q and E, Shift for speed), **F** to frame the selection and **Home** to frame all.
The five entities of Basic 3D are read in the Hierarchy, one sentence each (Main Camera, Sun, Sky, Ground, Post
Process); what they hold is for later pages. Then the Game view: **Play** (Ctrl+P) shows what the Main Camera sees;
the Game tab dragged beside the Scene tab; the resolution menu; the notice "no primary camera" when the camera's
**Primary** box is cleared (and Ctrl+Z to bring it back); the Game camera chip (F8) in the Scene view; **Stop**, and
the scene as it was. Keyboard focus in one step: the panel under focus gets the keys, a few shortcuts work everywhere
(Ctrl+S, Ctrl+Z, Ctrl+P), and while the game plays in a focused Game view its keys go to the game (Shift+F1 frees a
locked cursor). The Content Browser shows the project's `Assets` folder, `Scenes/Main.stscene` and
`Materials/Ground.stmat`: an asset is a file the game uses (importing is `make/assets`'). Last, every click ran a
command: **View ▸ Activity** lists the commands the reader's steps ran, and one paragraph says that commands are the
API, used by three clients (the editor's UI, `StrataCLI` with agents, and command scripts); that is why every step of
the book has a tab "With a command", read as `start/how-to-read` taught and optional on this track. The page never
types the number of commands (`new:14`). What Strata does not do here: the editor's shortcuts cannot be rebound,
because their chords are written in the code (`new:13`). The exercises (`new:15`) are two editor tasks. At the end the
reader can find every panel, move the view, play and stop, and read a step's command tab. The checkpoint is Coin Run's
fresh project.

**Leaves out.**

- The launcher's model, templates and recent projects as data → `editor/projects`
- Samples opened as copies → `make/samples`
- The project folder, saving, undo and recovery → `make/project-files`
- The Hierarchy's tree, the "+" menu and the Inspector's editing → `make/scenes-entities`
- The gizmos and the Transform's numbers → `make/scenes-entities`, `make/transforms-units`
- Play, Simulate, Pause and Step, and the running copy → `make/play-test-debug`
- The Scene view's chips (debug views, quality, preview lighting) → `make/lighting`, `make/quality`
- The Activity panel and the journal → `make/with-an-agent`
- Running commands yourself → `make/commands`
- How the shell, its docking and its panels are built → `editor-ui/shell`
- The editor camera's math and picking → `editor-ui/scene-view`, `editor/camera-viewport`
- The Game view's resolutions, letterboxing and input ownership inside → `editor-ui/game-view`
- Commands as the editor's API, inside → `editor/commands`

**Fit.** `fits`: about 3,500 words against M (3,000). Eleven steps at B0's length (the view's controls in one step, the
Game view's notice and chip in another) take most of it, with the labelled layout, the figure of the three clients, five
pictures and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:31` | feature | home | Going on without a project, and **File ▸ Show Launcher** back |
| `gamedev:43-46` | feature | home | The panel set, the menus in one sentence each, the Bedrock look named once, the status pills |
| `gamedev:48-49` | feature | home | The Scene view's navigation (orbit, pan, dolly, fly, F, Home) and the Game view (primary camera, resolution menu, the notice without a camera); the chips named only |
| `gamedev:246` | feature | home | Commands are the API, for game makers: three clients, one set of commands; the "With a command" tab of every tutorial. The page writes no count of commands (`process.md`, errata) |
| `gamedev:400` | figure | home | The default layout with every panel, the toolbar and the pills labelled |
| `gamedev:440` | figure | home | The fresh Basic 3D scene in the default layout: the page's opening picture |
| `gamedev:441` | figure | home | The Scene and Game views side by side during Play, the Game camera chip on |
| `gamedev:442` | figure | home | The Game view's resolution menu; the notice when no camera is primary |
| `gamedev:584` | term | home | Asset: a file the game uses, seen in the Content Browser |
| `gamedev:704` | open | home | The writer checks every **Menu ▸ Item** of the page in the tutorial run and by the names lint (`pipelines.md` §6.5). The Entity menu is built at run time: it draws the Hierarchy's create menu (`StrataEditor/src/EditorLayer.cpp:1580-1584`, `SceneHierarchyPanel::DrawCreateMenu`) |
| `editor-ui:112` | feature | use | The default layout's proportions and View ▸ Reset Layout |
| `editor-ui:114-116` | feature | use | The menu bar, the main toolbar and the status bar pills, as the steps name them |
| `editor-ui:142-154` | feature | use | The panels by id and title: the eight docked by default are shown, the rest named |
| `editor-ui:200` | feature | use | The editor camera's controls, as the steps use them |
| `editor-ui:203` | feature | use | The view's shortcuts: Q, W, E, R, F, Home and F8 |
| `editor-ui:207-208` | feature | use | The Game view, and who gets the keys while the game plays (Shift+F1) |
| `editor-ui:238-240` | feature | use | Global and focused shortcuts: the use home of shortcuts and focus (`book.md`, "The editor and automation") |
| `editor-ui:544` | figure | use | The recipe of the whole-editor picture in its default layout |
| `editor-ui:570` | figure | use | The Game view in Play at a fixed aspect, and its notice |
| `editor-ui:572` | figure | use | The status bar with its pills |
| `editor-ui:685` | hands-on | home | First launch: a Basic 3D project, every panel found, the layout reset; Preferences ▸ Interface named for a reader whose screen needs a larger interface |
| `editor-ui:687` | hands-on | home | Moving around the Scene view (orbit, pan, dolly, fly, F, Home); the gizmo tools are pointed out on the toolbar and used from `make/scenes-entities` on |
| `new:13` | not-done | home | Rebinding the editor's shortcuts: the chords are written in the code, and Preferences has three sections (the external editor, the interface, the frame rate). Evidence: `StrataEditor/src/EditorLayer.cpp:951-985`; `StrataEditor/src/Editor/EditorPreferences.cpp:69-74`; `Docs/Roadmap.md:993` (run at the pin) |
| `new:14` | erratum | home | The router's `gamedev:246` counts 153 registered commands, and the inventories count 151, 153 and 154. At the pin `StrataEditorCore` registers 151 (63 Edit, 46 Query, 42 Session), and the editor's window adds `editor.showPanel` and `editor.showDialog`. The page types no count. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164`, the three lists, and `:234`, which checks their sum; `StrataEditor/src/EditorLayer.cpp:177`, `:233` (read at the pin) |
| `new:15` | hands-on | home | Exercises, two editor tasks: **Basic.** close the Hierarchy and the Console, open each again from the View menu, then **View ▸ Reset Layout**; **Medium.** click each pill of the status bar and name the panel it opens (the frame pill the Performance panel, an error pill the Console). Evidence: `StrataEditor/src/EditorLayer.cpp:1575` (Reset Layout), `:1872-1935` (`DrawStatusBar`; the error pill focuses the Console), `:1979-1980` (the frame pill focuses Performance) |
| `editor-ui:763` | term | use | Viewport, Scene view and Game view |
| `editor-ui:766` | term | use | The editor camera: orbit, pan, dolly, fly |
| `editor-core:251` | feature | use | The editor camera, saved with each scene |
| `editor-core:299` | concept | use | The command pattern and one API, in one paragraph for game makers |
| `editor-core:463` | figure | use | Three clients, one registry: redrawn for game makers with the UI, `StrataCLI` and a command script |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Starting the editor, the launcher, a Basic 3D project and pressing Play once | `start/first-game` | must |
| What an engine and an editor are; one frame | `start/what-an-engine-is` | must |
| How to read a command and its JSON in the "With a command" tab | `start/how-to-read` | helps |

**Starting state.** No checkpoint: the editor's launcher, as `start/first-game` left the reader (`startsFrom
{"template": "basic3d"}` in the tutorial file). The page's first step creates Coin Run's project from Basic 3D; its
end state is the first checkpoint of Coin Run, the template unchanged.

**Command-only steps.** none

## `make/project-files` — Projects, saving, undo and recovery

**Covers.** The goal: know what Coin Run's project folder holds, and never lose work. What must be true first: the
Coin Run project of `make/editor-tour` is open. Nine steps, each with what to see and the way back. (1) The launcher's
card of the project: **File ▸ Show Launcher**, the recent projects as cards (and **File ▸ Open Recent**; missing
projects are hidden), then right-click the CoinRun card for **Show in Folder** and **Copy Path**; the path is pasted
and read in its parts (the drive or the home folder, the folders, the separators `\` and `/`). (2) Make the system's
file browser show file extensions and hidden files (tabs per OS: File Explorer's View menu, Finder's Cmd+Shift+., the
Files app's Ctrl+H), with one paragraph from zero on what an extension is (`.stproj`, `.stscene`, `.stmat`) and why
some names start with a dot and hide. (3) Read the folder with the anatomy diagram: `CoinRun.stproj`, `Assets/` with a
`.meta` file beside every asset, `Scripts/` with `CMakeLists.txt` and the example `Spinner.cpp`, the `.strata/` folder
the editor rebuilds (cache, script builds, saves, thumbnail) and `.gitignore`, which keeps `.strata/` out of version
control; what the reader needs of git is one sentence (git keeps every version of the folder's files that one saves
with it, and `.gitignore` names what it leaves out), with `basics/git` linked as a side step. The rule in a `:::rule`
aside: never edit `.stscene`, `.stmat`, `.stproj` or `.meta` files by hand, and move, rename and delete them only in the
editor, because the editor indexes handles and references and a hand edit bypasses undo. (4) Open `CoinRun.stproj` in a
text editor only to look: its `Project` part (Name, StartScene, AssetDirectory, Scripts, Game, Export) and its
`Settings` part, read as JSON the way `start/how-to-read` taught. (5) **File ▸ Project Settings**: the pages Game,
Export, Collision Layers, Simulation, Timing, Graphics Quality and Input Actions, each named with the page of the book
that uses it; a settings change is one undo step and is written to the `.stproj`. (6) Save the scene with Ctrl+S (**File
▸ Save Scene**) and watch the saving pill: saves are written in the background and quitting waits for them; **Save Scene
As** for a copy. (7) Undo and redo: rename the Ground, move the Sun, then **Edit ▸ Undo** (the menu names each step),
Ctrl+Z and Ctrl+Y (or Ctrl+Shift+Z); one step per action, a whole drag is one step. (8) The question before changes are
lost: with an unsaved change, **File ▸ Open Scene** asks Save, Don't Save or Cancel. (9) Recover after a crash: make a
change, wait a few seconds, end the editor from the system (Task Manager, Force Quit, `kill`, in OS tabs), start it
again and open Coin Run: the **Recover Unsaved Changes** dialog (also **File ▸ Recover Unsaved Changes**) applies or
discards what the recovery journal kept; the step discards it, so Coin Run stays as `make/editor-tour` left it. `##
Result`: the reader knows every file of the folder and keeps work with save, undo and recovery; the page changes nothing
in Coin Run, so it has no end-state download. `## Variations`: opening a project made by an older release (0.5.0
projects get their collision layers moved into the project and are saved in the new format; make a copy first; the
release notes' "Upgrading" sections); a project kept in a folder that a cloud drive syncs; the scene file under version
control: a `.stscene` holds one entity per line, so after one entity is moved in the editor and the scene saved, a diff
of the file shows the one entity that moved, read in a text editor and never edited. The exercises (`new:16`) are two
editor tasks.

**Leaves out.**

- How undo steps are recorded and merged → `editor/undo`
- How saves run off the main thread, and the unsaved-changes guard inside → `editor/saving`
- The recovery journal's file and its folding → `editor/recovery`
- The recovery dialog's drawing → `editor-ui/launcher-dialogs`
- Settings sections, their versions and validation → `world/projects-settings`
- Templates and samples as data → `editor/projects`
- Each settings page in use → `make/input`, `make/physics`, `make/script-loop`, `make/quality`, `make/export`
- Moving, renaming and deleting assets, the trash → `make/assets`
- The terminal and paths in commands → `basics/tools`
- Git and version control, a side step that track G does not read in its order → `basics/git`

**Fit.** `fits`: about 3,900 words against M (3,000). Nine steps, two of them with OS tabs, take most of it, with the
paragraph from zero on extensions, hidden files and paths, three Variations, the folder diagram, six pictures and two
exercises. It is near M's top: a tenth step would not fit.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:33-34` | feature | home | What a new project writes, and the `.stproj` file's parts, read but not edited |
| `gamedev:36` | feature | home | Recent projects: the launcher's cards and **File ▸ Open Recent**; missing projects are hidden |
| `gamedev:37` | feature | home | The Variation: a project of an older release, migrated and saved in the new format |
| `gamedev:57` | feature | home | Undo and redo for every change: one step per action, project settings included |
| `gamedev:58` | feature | home | Autosave into the recovery journal a few seconds after an edit; **File ▸ Recover Unsaved Changes** |
| `gamedev:59` | feature | home | Saves written in the background; the saving pill; quitting waits |
| `gamedev:294` | concept | home | Projects and files: one folder of text documents with `.meta` handles beside them, edited only through the editor; the mistake of editing or moving files by hand |
| `gamedev:398` | figure | home | The project folder's anatomy |
| `gamedev:451` | figure | home | Project Settings: the page list with the Game page open; each other page is shown on its own page of the book |
| `gamedev:481` | rule | home | Never edit `.stscene`, `.stmat`, `.stproj` or `.meta` by hand; move, rename and delete in the editor |
| `gamedev:513` | rule | home | An unsaved scene stops opening another scene, closing the project and quitting until the person answers |
| `gamedev:659` | term | home | Recovery journal |
| `editor-core:604` | hands-on | home | Undo is your friend: changes, undone and redone, named in the Edit menu |
| `editor-core:614` | hands-on | home | Recover after a crash: the editor ended from the system, the dialog on the next open |
| `new:16` | hands-on | home | Exercises, two editor tasks: **Basic.** rename the Ground, move the Sun and change the Timing page's FixedRate, predict the three names that **Edit ▸ Undo** shows in turn, and undo all three to check; **Medium.** with a change unsaved, predict which of **File ▸ New Scene**, **File ▸ Open Scene** and closing the window ask Save, Don't Save or Cancel first, try each and answer Cancel. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:387` (`edit.history`, the named steps); `StrataEditor/src/Editor/EditorContext.cpp:694` (the unsaved-changes dialog's Don't Save) |
| `editor-core:124` | feature | use | `edit.undo`, `edit.redo` and `edit.history` in the command tabs |
| `editor-core:131` | feature | use | Saving a scene, in the steps' command tab (`scene.save`) |
| `editor-core:134` | feature | use | The unsaved-changes guard, as the person meets it |
| `editor-core:145` | feature | use | The recovery journal, a few seconds after an edit |
| `editor-core:153-154` | feature | use | `scene.recoveryStatus` and `scene.recover` in the command tab; the Recover dialog |
| `editor-core:210` | feature | use | Recent projects |
| `editor-core:310` | concept | use | Undo and redo, at the user's level: a history of named steps |
| `editor-core:330` | concept | use | No silent data loss, as the person meets it: the question, the saving pill |
| `editor-core:333` | concept | use | Autosave and crash recovery, at the user's level |
| `editor-core:515-517` | figure | use | The Edit menu with named steps; the unsaved-changes dialog; the saving pill |
| `editor-core:519` | figure | use | The Recover Unsaved Changes dialog after a simulated crash |
| `editor-core:671` | term | use | Undo step |
| `editor-ui:120` | feature | use | The unsaved-changes question: Save, Don't Save, Cancel |
| `editor-ui:218` | feature | use | The Recover Unsaved Changes dialog |
| `editor-ui:228` | feature | use | The Project Settings panel and its pages |
| `scene-ecs:212` | feature | use | The `.stproj` and the project's layout on disk |
| `scene-ecs:464` | figure | use | The project on disk, the source of the anatomy diagram |
| `scene-ecs:605` | hands-on | use | The Variation of a scene under version control: one entity moved, the scene saved, and the diff shows the one entity that moved, because a `.stscene` holds one entity per line. Evidence: `Strata/src/Strata/Scene/SceneDocumentWriter.h:77-78` (read at the pin) |
| `scene-ecs:685-686` | term | use | Project; the intermediate folder `.strata/` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's panels, menus and the launcher | `make/editor-tour` | must |
| Reading JSON: objects, names and values | `start/how-to-read` | helps |
| The Basic 3D project and its five entities | `start/first-game` | helps |
| The terminal and paths in commands (the `kill` of step 9's Linux tab) | `basics/tools` | helps |
| Git and version control | `basics/git` | helps |

**Starting state.** The end state of `make/editor-tour`: Coin Run's fresh project from Basic 3D (`startsFrom
{"tutorial": "make/editor-tour"}`). Every change the steps make is undone, discarded or not saved, so the project ends
as it began and `make/scenes-entities` starts from the same checkpoint.

**Command-only steps.** none

## `make/scenes-entities` — Scenes, entities and components

**Covers.** The page builds Coin Run's level and, while doing it, teaches what a scene, an entity and a component are
from the user's side. The idea first, in one paragraph and the figure "an entity is an ID and its components": a scene
is a document of entities; an entity is a thing with a name and an identity and nothing else; what it is and does
comes from the components on it (a Transform for where it is, a Mesh Renderer for what is drawn, a Box Collider for
what it bumps into), and behaviour comes from systems and scripts, not from a class of its own. The common mistake of
looking for an "enemy class" is named, and the inheritance tree is drawn beside the entity as the approach Strata does
not take. Then about ten steps. (1) Select the template's Ground and read its components in the Inspector: Name,
Transform, Mesh Renderer (its Mesh, its Material and Cast Shadows), Box Collider; each property's tooltip gives its unit
and its range, because one description
of every property drives the Inspector, the files, the commands and the scripts. (2) Add a wall with the Hierarchy's
**+ ▸ Cube** (a cube with a matching box collider), rename it with F2, and type its Position and Scale from the page
(the numbers are explained by `make/transforms-units`); drag it once with the Move gizmo (W) to see the numbers change.
(3) Duplicate it with Ctrl+D into four walls, edit their numbers, and drag them onto an empty entity **Walls** (**+ ▸
Empty**) to make them its children. (4) The ball: **+ ▸ Sphere**, named `Ball`. (5) The first coin: **+ ▸ Mesh only ▸
Cylinder** (no collider: the ball must pass through it), flattened and stood up, named `Coin`; a placeholder until
`make/assets` brings the coin's model. (6) **Add Component ▸ Tag** on the coin with the tag `Coin`, which scripts use
later; the component menu (Reset, Copy Values, Paste Values, Remove). (7) Edit several entities at once: select the four
walls and change their height together; mixed values show as "--"; then find them again with the Hierarchy's search
(`Wall`, `t:Coin` for the tag, `c:BoxCollider` for a component; `l:` and `cell:` named for worlds). (8) Click empty
space: with nothing selected the
Inspector shows the scene's settings (the Sky section and the timing are later pages'). (9) Clear the active box of
**Walls**: its children stop drawing and colliding; set it again. (10) Save, then see that a project holds several
scenes: **File ▸ New Scene** makes an empty one (a level or a menu would be one), saved as `Scenes/Test.stscene`, and
**File ▸ Open Scene** goes back to `Main`; the start scene stays `Main`. The built-in meshes are listed (Cube,
Sphere, Plane, Quad, Cylinder, Capsule, Cone, Torus, and the default material), and the Add Component popup's
categories show that the engine's modules register the components a scene can hold; the page writes no count of
them. The exercises (`new:17`) are two editor tasks. At the end the reader can compose an entity from components,
parent entities, edit many at once and switch a group off; the checkpoint holds the walled ground, the ball and the
placeholder coin.

**Leaves out.**

- What the three numbers of a position, a rotation and a scale mean; the gizmos in depth → `make/transforms-units`
- Colliders and bodies; why a collider without a rigid body stands still → `make/physics`
- The ground's material and new materials → `make/materials`
- Reusing the coin → `make/prefabs`
- GameObjects and other engines' names for entities → `start/coming-from`
- Object models compared: inheritance, components, ECS → `world/what-a-world-is`
- The registry, storages and handles inside → `world/ecs`
- Property metadata and registration → `world/reflection`
- How the Inspector is generated → `editor-ui/inspectors`
- Every component and its properties → `reference/components`

**Fit.** `fits`: about 3,550 words against M (3,000). Ten steps at B0's length take most of it, with the idea taught
from zero and its figure, five pictures of the menus, the Hierarchy and the Inspector, and two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:50-51` | feature | home | The Hierarchy (tree, rename, drag to parent, the "+" menu) and the Inspector (every selected entity at once, Add Component, scene settings with nothing selected) |
| `gamedev:67` | feature | home | The registered components, met by category in the Add Component popup; the count is not typed (see `new:1`) |
| `gamedev:68` | feature | home | One description per property (range, tooltip with unit, category) behind the Inspector, files, commands and scripts |
| `gamedev:69` | feature | home | The built-in meshes and the default material |
| `gamedev:298` | concept | home | Scenes, entities and components from the user's side; the "enemy class" mistake |
| `gamedev:402` | figure | home | An entity as an ID and its components, beside an inheritance tree |
| `gamedev:443` | figure | home | The Hierarchy's "+" menu: meshes with colliders, Mesh only, lights, UI |
| `gamedev:444` | figure | home | The Inspector with the four walls selected (mixed values) and with nothing selected |
| `gamedev:580` | term | home | Transform |
| `gamedev:588` | term | home | Built-in mesh |
| `scene-ecs:597` | hands-on | home | Step 9: the **Walls** parent switched off and on |
| `new:1` | erratum | home | `plan/inventory/gamedev.md:67` and `:272` count 40 registered components; the engine registers 42 (the list of `gamedev:67` holds 42 names), and `component.list` returns 39 of them, leaving out the hidden `ID`, `Relationship` and `Inactive`. The page names the categories and types no count; `process.md`'s table of errata holds the row. Evidence: `StrataTests/Architecture/ComponentSchema.json` at the pin, 42 entries under `Components`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:619-620` skips the hidden ones, which are the three of `Strata/src/Strata/Scene/ComponentRegistration.cpp:72`, `:90`, `:100` (counted and read at the pin) |
| `scene-ecs:29-30` | feature | use | An entity's lasting identity, and the components every entity is made with |
| `scene-ecs:33` | feature | use | Duplicating with fresh identities (Ctrl+D) |
| `scene-ecs:51-55` | feature | use | The ID, Name, Tag, Inactive and Transform components, as the Inspector shows them |
| `scene-ecs:72` | feature | use | Parenting by drag keeps where the child is in the world |
| `scene-ecs:82` | feature | use | Activity in the hierarchy: a switched-off parent switches off its children |
| `scene-ecs:281` | concept | use | Components as plain data, at the user's level |
| `scene-ecs:311` | concept | use | Activity, at the user's level |
| `scene-ecs:472` | figure | use | The Hierarchy panel |
| `scene-ecs:477-478` | figure | use | The Inspector's sections; the Add Component menu |
| `scene-ecs:483` | figure | use | The Inspector with nothing selected |
| `scene-ecs:611` | term | use | Entity |
| `scene-ecs:613` | term | use | Component |
| `scene-ecs:624` | term | use | Scene |
| `scene-ecs:634` | term | use | Active in hierarchy |
| `editor-ui:144-145` | feature | use | The Hierarchy and the Inspector panels |
| `editor-ui:175` | feature | use | Component sections for what every selected entity has |
| `editor-ui:177` | feature | use | Mixed values across entities |
| `editor-ui:183` | feature | use | The component menu and the Add Component popup |
| `editor-ui:187` | feature | use | Scene settings with nothing selected, named only |
| `editor-ui:239` | feature | use | Delete, Ctrl+D, F2 and the other selection shortcuts |
| `editor-ui:551` | figure | use | The Hierarchy with a group expanded and an entity switched off |
| `editor-ui:555` | figure | use | The Inspector on one entity and on three with mixed values |
| `editor-ui:693` | hands-on | home | Step 7's search of the Hierarchy by name, `t:` and `c:`; `l:` and `cell:` named for `make/large-worlds` |
| `editor-ui:686` | hands-on | home | A small scene built with the Hierarchy and the Inspector: create, rename with F2, reparent by drag, multi-edit; the page's steps on Coin Run's level |
| `new:17` | hands-on | home | Exercises, two editor tasks in `Scenes/Test.stscene`: **Basic.** a table made of a flattened Cube top and four Cube legs under an empty **Table**, switched off and on by its parent's active box; **Medium.** predict which entities the Hierarchy's search `c:BoxCollider` finds in Coin Run's level (the ground and the four walls, not the ball's sphere or the coin's collider-less cylinder), then search to check. Evidence: `StrataEditor/src/Editor/ProjectTemplates.cpp:83-85` (the Ground's box collider); `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:76-79` (Cube with a box collider, Sphere with a sphere collider); `StrataEditor/src/Editor/HierarchyView.cpp:95-100` (the `c:` and `t:` prefixes) |
| `editor-core:74-76` | feature | use | `scene.*`, `entity.*` and `component.*`, the commands of the steps' command tabs |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The panels, selecting and moving the view | `make/editor-tour` | must |
| A position, a rotation and a scale as numbers to type | `make/transforms-units` | helps |
| A scene as a document the engine plays | `start/what-an-engine-is` | helps |

**Starting state.** The end state of `make/editor-tour` (`startsFrom {"tutorial": "make/editor-tour"}`): Coin Run's
fresh Basic 3D project; `make/project-files` changed nothing in it. The page ends with Coin Run's level: the ground,
four walls under **Walls**, the ball and the placeholder coin tagged `Coin`, and the empty `Scenes/Test.stscene` of step
10 (later pages use it as a scratch scene).

**Command-only steps.** none

## `make/transforms-units` — Positions, rotations and units

**Covers.** A concept page for a reader who cannot read code yet: every idea is shown first with the Inspector's
numbers and the gizmo on Coin Run's level, and the code forms come only in the last section. The problem as the reader
met it: the walls of `make/scenes-entities` took numbers like (0, 0.5, -10), and the coin needed a turn of 90 degrees
to stand up; what do the numbers mean? The naive answer (x is right, y is up, done) and where it breaks: which way is
forward, which way does a turn go, what does a child's position count from. The ideas, in this order: a position as
three numbers (x, y, z) along the three axes shown by the Move gizmo's red, green and blue arrows, y up, in metres
(the ball is 1 m across, the ground 20 m); adding numbers moves a thing, multiplying them scales a distance; a
direction as three numbers, and forward as -Z for cameras, lights and a script's forward, while glTF models face +Z;
handedness shown with the right hand; scale as three factors, and a negative scale that mirrors an object and still
draws and lights it correctly; a rotation in degrees, the Rotate gizmo's rings and the Inspector's three angles (pitch,
yaw, roll) in degrees; a rotation as an axis and an angle (the coin's spin about the vertical axis); degrees and
radians from zero (a full turn is 360 degrees or 2π radians, about 6.283); a rotation stored as a quaternion of four
numbers that nobody types, and two rotations combined by multiplying, in an order that matters (shown with two turns
in the Inspector, done in both orders); parent and child, local against world position, with the solar-system exercise
(Sun, Earth and Moon in the Hierarchy: turn the Sun and its children follow) and the gizmo's World and Local switch.
The approaches engines use, in a short table with sources: which axis is up, left- or right-handed, metres or
centimetres, angles stored as Euler angles or quaternions. Strata's choice and its reason: y up, right-handed, -Z
forward and metres as glTF has them, quaternions stored and angles shown. What it cannot do: the Inspector's angles are
the ones typed, and a rotation read back as angles may show other numbers that mean the same turn. Common mistakes: a
model that walks backwards (+Z against -Z), adding angles to a stored rotation, a model in centimetres a hundred times
too large (fixed by `make/assets`). The last section, "The same ideas in code", shows a position and a direction as
`glm::vec3`, `glm::radians`, the `Spinner`'s turn (`glm::angleAxis` and `turn * transform.GetRotation()`), and the
Transform's local and world positions in the SDK; it says that `make/scripting-scene` sends the reader back to it.
At the end the reader can read and set any Transform in the Inspector, predict where a child goes when its parent
turns, and convert between degrees and radians.

**Leaves out.**

- The mathematics of vectors: length, dot and cross products → `basics/math-vectors`
- Matrices, spaces and matrix order → `basics/math-matrices`
- Euler angles, quaternions and slerp as mathematics → `basics/math-rotations`
- Vectors, `normalize`, `atan2` and smoothing as recipes for game code → `make/gameplay-math`
- Strata's clip space and depth conventions → `gpu/coordinates`
- World transforms, their caches and the transform contract → `world/scene-graph`
- How mirrored instances are drawn → `draw/mirrors-camera-relative`
- A model's import scale → `make/assets`

**Fit.** `fits`: about 5,750 words against L (5,000). Ten ideas taught from zero at B0's length take most of it, each
shown with the gizmo or the Inspector, with the conventions figure, the approaches table, the solar-system exercise and
two short code excerpts in the last section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:71` | feature | home | The conventions a maker must know: -Z forward, glTF's +Z, Euler degrees in commands and the Inspector but radians in `SetEulerAngles`, metres, y up |
| `gamedev:301` | concept | home | Transforms and the hierarchy: local and world, parent and child, units, axes, Euler against quaternions; the mistakes (backwards models, angles added to a quaternion) |
| `gamedev:404` | figure | home | The coordinate conventions: y up, -Z forward, glTF's +Z, yaw, pitch and roll |
| `gamedev:581` | term | home | World position and local position |
| `gamedev:582` | term | home | Quaternion |
| `gamedev:583` | term | home | Forward (-Z) |
| `render-scene:559` | hands-on | home | Mirroring safely: a negative scale mirrors the ball, and it still draws and lights correctly |
| `scene-ecs:596` | hands-on | home | The solar system in the Hierarchy: local against world |
| `gamedev:359` | code | use | The `Spinner`'s two lines of the turn, `StrataEditor/src/Editor/ScriptProject.cpp:249-250`, in "The same ideas in code" |
| `scene-ecs:55` | feature | use | The Transform component: translation, rotation, scale relative to the parent |
| `scene-ecs:292` | concept | use | Transforms and the scene graph, at the user's level |
| `scene-ecs:628-629` | term | use | Local and world transform; translation, rotation and scale |
| `editor-ui:177` | feature | use | Rotations edited as the angles the person typed |
| `editor-ui:202` | feature | use | The gizmo: move, rotate and scale, World and Local, snapping |
| `editor-ui:563` | figure | use | The three gizmos on a selected object, World against Local |
| `editor-ui:769-771` | term | use | Gizmo; world and local space; snapping |
| `scripting:120` | feature | use | The SDK's `TransformComponent`, local and world, in the last section |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, the Transform component, the Hierarchy and the Inspector | `make/scenes-entities` | must |
| Moving the Scene view and selecting | `make/editor-tour` | must |
| How to read code you do not understand yet (for the last section) | `start/how-to-read` | helps |
| Vectors as mathematics | `basics/math-vectors` | helps |
| Rotations and quaternions as mathematics | `basics/math-rotations` | helps |

## `make/assets` — Bringing in assets

**Covers.** The goal: bring Coin Run's coin model into the project and put it where the placeholder coin stands.
What must be true first: Coin Run at the end of `make/scenes-entities`, and the release folder of Strata at hand (its
`Samples/` hold the file). First, where assets come from: one paragraph on licenses (CC0 is free to use with no
conditions, CC-BY asks for credit, anything unclear stays out), places that give CC0 assets (Kenney, Poly Haven,
Quaternius, ambientCG), keeping downloads in a folder of their own, and a `CREDITS.md` table in the project (files,
source, author, license, changes) as the samples keep it. The steps. (1) In the Content Browser, **New ▸ Folder**
`Models`, then drag `Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb` (Kenney's Platformer Kit, CC0) onto it
(or **Import**; files dropped on the editor's window import into the shown folder): the import runs in the background
and the status bar's assets pill counts it. The formats in a small table: glTF 2.0 models (a `.gltf` brings its `.bin`
and its images), PNG, JPEG, TGA, BMP, PSD, GIF and HDR images, WAV, MP3, FLAC and Ogg sounds, TrueType and OpenType
fonts (`.ttf`, `.otf`), and `.cube` color lookup tables for a grade (`make/look`); OBJ and FBX are not read (`new:2`).
One line links the table of what the glTF importer supports and what it skips or clamps, each with the warning the
Asset tab shows, on `assets/models-gltf`. If you do not see it: a failed import (a broken file, an image the importer
refuses) posts one **Import failed** toast that names the file and the reason, with **Show Asset** and the Console's
line, and the Asset tab shows the reason above the import settings that may fix it (`assets:144`). (2) Expand the model
in the Content Browser: its sub-assets (meshes, materials, textures) are assets of their own; the Asset tab shows the
model's summary (meshes, triangles, materials, textures) and its import settings. (3) The `.meta` file beside
`coin-gold.glb` in the file browser (shown as `make/project-files` taught): one paragraph on handles, a stable identity
kept in that file, so that a scene names the asset by its handle and a rename or a move in the editor breaks nothing.
(4) Drag the model from the Content Browser into the Scene view: it places as a linked group of entities resting on the
ground (the drop's ghost and linked groups are `make/prefabs`'). (5) Check its size against the 1 m ball and set the
model's **Scale** import setting with Apply until the coin is the size the page gives; a model made in centimetres needs
0.01. A model's bounds have no menu or button (the Asset tab's summary shows no size,
`StrataEditor/src/Panels/AssetInspectorPanel.cpp:570-590`), so the editor tab compares the coin with the ball, and
`asset.info` with the bounds in metres stands only in the command tab. (6) The other import settings a maker uses, each
in a sentence: `BaseColorFactorsAreSRGB` for models whose exporter writes colors as sRGB (Kenney's), a texture's usage
guessed from its name (`_normal`, `_rough`), a texture's **Quality** Fast or High (the look, the stored size, the import
time), `RemoveSun` for skies (`make/lighting`). (7) Replace the placeholder: move the `Coin` tag to the model's root,
delete the Cylinder coin, name the model's root `Coin`. (8) Rename and move safely: rename the `Models` folder with F2
and see the `.meta` files follow. (9) Delete safely: **Delete...** on the coin model is refused while the scene uses it
(the Delete Asset dialog lists who uses it); an unused asset goes to the project's trash, and Ctrl+Z brings it back. `##
Result`: the coin model in the project and in the level, credited in `CREDITS.md`; it ends with the download of the
page's end state. `## Variations`: a model in centimetres; a texture whose source file changes on disk (the editor
imports it again in the background, hot reload of assets); a model from a downloaded pack. A paragraph of G4 points
forward: making a material with the imported texture is `make/materials`'. The exercises (`new:18`) are two editor
tasks.

**Leaves out.**

- What an asset is inside: sources and cooked forms → `assets/what-is-an-asset`
- Handles, `.meta` files and sub-assets inside → `assets/handles-meta`
- Import records, cache validity and background imports → `assets/importing`
- Textures for the GPU, mips and compression → `assets/textures`, `assets/texture-cooking`
- glTF and models as entity templates; the table of what the glTF importer supports and skips → `assets/models-gltf`
- The trash and references inside → `editor/trash-references`
- Linked groups, drops and their ghost → `make/prefabs`
- Materials from the imported textures → `make/materials`
- Sounds and fonts → `make/sound`, `make/hud`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,900 words against M (3,000). Nine steps take most of it, with the formats table, the paragraphs
on licenses and handles, three Variations, four pictures and two exercises. It is near M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:52-53` | feature | home | The Asset tab (import settings, the model's summary) and the Content Browser (folders, grid, thumbnails, drag and drop) |
| `gamedev:77` | feature | home | Importing by dropping files or with **Import**; background imports; a `.gltf` brings its `.bin` and images |
| `gamedev:78` | feature | home | The formats the importers read, `.otf` fonts and `.cube` lookup tables among them, which the item leaves out. The importers live in `Strata/src/Strata/Asset/` (`AssetPipeline` is a layer of `StrataTests/Architecture/Layers.json:113-117`, not a folder): writers cite `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` (read at the pin) |
| `gamedev:79` | feature | home | The asset types, named as the Content Browser shows them |
| `gamedev:80` | feature | home | `.meta` files and handles; never edited by hand |
| `gamedev:81` | feature | home | The import settings a maker uses: Scale, `BaseColorFactorsAreSRGB`, usage from names, `RemoveSun` named |
| `gamedev:82` | feature | home | Deletes to the project's trash, refused while used, undone by Ctrl+Z |
| `gamedev:83` | feature | home | The policy for downloads: CC0 or CC-BY, a folder of their own, `CREDITS.md` |
| `gamedev:304` | concept | home | Assets and import: sources against imported data, stable handles, background imports, import settings; the mistakes (centimetre models, sRGB factors, a normal map as color) |
| `gamedev:351` | concept | home | Licenses of assets: CC0, CC-BY's credit, unclear licenses kept out |
| `gamedev:445` | figure | home | The Content Browser's grid with thumbnails and an expanded model; its Scripts root is shown again by `make/first-script` |
| `gamedev:519` | rule | home | Asset licenses: CC0 or CC-BY only, credited |
| `gamedev:537` | hands-on | home | G4, its import and scale half: a model and a texture imported, the model's scale fixed; its material half is `make/materials`' |
| `gamedev:585` | term | home | Asset handle |
| `gamedev:586` | term | home | Import and import settings |
| `gamedev:587` | term | home | Sub-asset |
| `gamedev:665` | term | home | CC0 and CC-BY |
| `new:18` | hands-on | home | Exercises, two editor tasks: **Basic.** import `barrel.glb` from the same folder of the ThirdPerson sample (Kenney's Platformer Kit, CC0), place it beside the ball and check its size; **Medium.** place one barrel, predict whether **Delete...** on `barrel.glb` is refused, try it and read who uses it in the Delete Asset dialog, then delete the barrel entity, delete the model and bring it back with Ctrl+Z. Evidence: `Samples/ThirdPerson/Assets/Models/Platformer/barrel.glb`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-903` (`asset.delete`: the trash, one undo step, refused while a scene uses it) |
| `new:2` | not-done | home | OBJ and FBX import: models are glTF only. Evidence: `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` registers no OBJ or FBX importer (run at the pin); `Docs/Releases/0.7.0.md:414-415` |
| `assets:38` | feature | use | The asset handle |
| `assets:44-45` | feature | use | `.meta` sidecars; sub-assets |
| `assets:136-137` | feature | use | Import settings; background imports and hot reload of assets |
| `assets:144` | feature | use | Step 1's "If you do not see it": a failed import's one **Import failed** toast with **Show Asset** and the Console's line, and the reason in the Asset tab above the import settings. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2872-2895` (`NotifyImportFailures`); `StrataEditor/src/Panels/AssetInspectorPanel.cpp:143`, `:757-774` (`DrawImportOutcome`, drawn before the settings) (read at the pin) |
| `assets:141` | feature | use | Moves, renames and deletes as the editor does them |
| `assets:215` | feature | use | The Content Browser and the Asset tab |
| `assets:246` | concept | use | What an asset is: the source and what the game reads, at the user's level |
| `assets:253` | concept | use | Identity by handle, not by path, in one paragraph |
| `assets:496` | figure | use | The Content Browser with an import running |
| `assets:513-514` | figure | use | The refused delete; the status bar's assets pill |
| `assets:520` | rule | use | Reference assets by handle, never by path |
| `assets:522` | rule | use | Move, rename and delete through the editor |
| `assets:613` | hands-on | use | Import a model and its textures, read the sub-assets, place it |
| `assets:617` | hands-on | use | Fast against High, in step 6 |
| `assets:642` | term | use | Import and importer |
| `assets:644` | term | use | `.meta` file |
| `assets:733-734` | term | use | Referencers; trash |
| `editor-core:161-162` | feature | use | Delete to the trash; the check for users |
| `editor-core:338` | concept | use | Files are part of the history: deletes undone |
| `editor-core:521` | figure | use | The Delete Asset dialog listing the scene that uses the coin |
| `editor-ui:121` | feature | use | Files dropped on the window import into the shown folder |
| `editor-ui:146-147` | feature | use | The Asset tab and the Content Browser panels |
| `editor-ui:219` | feature | use | The Delete Asset confirmation |
| `editor-ui:554` | figure | use | The Content Browser's grid with an expanded model |
| `editor-ui:688` | hands-on | home | Import assets, browse thumbnails, drag a model into the view; making a material is `make/materials`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The project folder, `.meta` files, extensions and hidden files; undo | `make/project-files` | must |
| Sizes in metres and the scale of a Transform | `make/transforms-units` | must |
| Entities, the Hierarchy, the Inspector and tags | `make/scenes-entities` | must |

**Starting state.** The end state of `make/scenes-entities` (`startsFrom {"tutorial": "make/scenes-entities"}`):
the ground, four walls under **Walls**, the ball and the placeholder coin. The file comes from the release's
`Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb` (credited in that sample's `CREDITS.md`), copied by the
tutorial file's `files` (its import is a `setup` step, shown as dragging the file into the Content Browser). The page
ends with the coin model placed and tagged; `make/materials` starts there.

**Command-only steps.** none

## `make/materials` — Materials

**Covers.** The page gives Coin Run a gold coin and a ball with a textured metal material, and teaches the material
model at the maker's level. The idea first, in one paragraph and the grid of spheres from rough to smooth, metal and
not: a material says how a surface answers light, with a base color, a metallic value and a roughness, and the rest
(maps, emission, alpha) builds on them; physically based means the values mean the same under any light. Colors as
three numbers from 0 to 1 are explained from zero beside the color picker. The steps. (1) **New ▸ Material** in a
`Materials` folder of the Content Browser: `Materials/Gold.stmat`, open in the Asset tab's material editor. (2) Base
color: a gold color from the page's table of plausible values; metallic 1 (metals take their color from the base
color); roughness 0.3. (3) Give the coin the material (the Mesh Renderer's **Material** in the Inspector, or a drop of
the material on the coin in the view). (4) Drag the roughness from 0 to 1 and watch the sun's highlight spread; set
metallic to 0 and see painted gold, the mistake of a metallic value on paint. (5) The ball's material: import
`Metal032_Color.jpg`, `Metal032_MetallicRoughness.jpg` and `Metal032_NormalGL.jpg` from
`Samples/PhysicsPlayground/Assets/Textures/Metal/` (ambientCG, CC0); each texture's usage is guessed from its name;
make `Materials/Ball.stmat` with the three maps and a UV tiling. (6) Normal maps from zero: bumps drawn without
geometry, read as data and never as color; set a normal map's usage to Color on purpose and see the material editor's
warning with **Fix**; the import setting `FlipGreen` for maps made the DirectX way (a name with `dx` turns it on), seen
by turning it on and back. (7) Emission as a color and a strength, on the coin, faint; its value in nits is
`make/lighting`'s. (8) Alpha modes on a scratch cube, deleted afterwards: Opaque, Mask with its cutoff, Blend with an
alpha of 0.4; glass with Transmission and IOR 1.5; clear coat, Unlit and Double Sided in one sentence each. (9) The
albedo audit: the Scene view's debug view chip ▸ **Albedo** marks base colors outside the plausible range; a wall set to
pure white is marked, and the reader fixes it to the value the view accepts. (10) Save. The table of guidance for
makers: water and wet surfaces IOR 1.33 with roughness 0.02 to 0.06, glass 1.5, painted surfaces roughness 0.15 to 0.45,
base colors above 0.85 look like plastic. What Strata does not do here (`new:3`): no shaders as assets and no material
graphs, because every surface uses the one physically based model; and (`new:19`) no material parameters per entity,
such as a tint or a hit flash, and no material changes from scripts: a loaded material never changes, so a game gives
the Mesh Renderer another material, as the Tetris sample does. Common mistakes: near-white base colors, metallic on
paint, a normal map imported as color. At the end the reader can make, assign and audit materials; the checkpoint
holds the gold coin and the metal ball.

**Leaves out.**

- The material model as physics: the BRDF, Fresnel and energy → `light/materials`, `light/reflectance`
- The material's GPU record and the normal decode → `light/material-data`
- Clear coat and transmission in depth → `light/clearcoat-transmission`
- Textures for the GPU: color spaces and compression → `assets/textures`
- The albedo view and the other measuring views inside → `light/measuring-light`
- Emission in nits and light units → `make/lighting`
- Reflections that make metals look right → `make/reflections`
- Colors and color spaces as a subject → `basics/color`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 4,400 words against L (5,000). Ten steps at B0's length take most of it, with the material idea,
colors as numbers and normal maps taught from zero, the guidance table, the sphere grid, five pictures and the albedo
exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:89` | feature | home | Material documents: **New ▸ Material**, the material editor, the properties a maker sets |
| `gamedev:90` | feature | home | The guidance table of plausible values |
| `gamedev:309` | concept | home | Materials and physically based shading at the maker's level; the mistakes (near-white colors, metallic paint) |
| `gamedev:448` | figure | home | The material editor in the Asset tab; the normal-map warning with **Fix** |
| `gamedev:589` | term | home | Material |
| `gamedev:590` | term | home | PBR |
| `render-indirect:539` | hands-on | home | Step 9: the albedo audit, fixing what the Albedo view marks |
| `new:3` | not-done | home | Shaders as assets and material graphs: shaders are compiled at build time and embedded. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31` has no shader type (run at the pin); `strata_add_shaders` in `Strata/CMakeLists.txt:80` |
| `new:19` | not-done | home | Material parameters per entity, such as a tint or a hit flash, and material changes from scripts: a loaded material never changes, and a game gives `MeshRenderer.Material` another asset. Evidence: `Strata/src/Strata/Renderer/Material.h:87-90`; `git grep -ni material 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds nothing (run at the pin); `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| `gamedev:537` | hands-on | use | G4's material half: a material made with the imported texture |
| `render-direct:35-37` | feature | use | The metallic-roughness material, the alpha modes, emission as a color and a strength |
| `render-direct:39` | feature | use | The texture maps a material takes |
| `render-direct:44` | feature | use | Normal maps read as two channels |
| `render-direct:46-47` | feature | use | Clear coat and glass, named |
| `render-direct:50` | feature | use | `material.create`, `material.get`, `material.set` in the steps' command tabs |
| `render-direct:300` | concept | use | The surface description, at the maker's level |
| `render-direct:307` | concept | use | Textures as color or data; normal maps |
| `render-direct:526` | figure | use | The metallic-roughness grid of spheres |
| `render-direct:531` | figure | use | A normal map on and off |
| `render-direct:541` | figure | use | The Albedo view marking out-of-range albedos |
| `render-direct:563` | figure | use | Glass at IOR 1.5 |
| `render-direct:641` | hands-on | use | A material set audited in the Albedo view, as an exercise |
| `assets:165-166` | feature | use | Normal map conventions; the texture-usage warnings |
| `assets:498` | figure | use | The same texture as color, as a normal map and as data |
| `assets:615` | hands-on | use | A normal map fixed by its name: tokens, `FlipGreen`, the warning |
| `assets:714` | term | use | Normal map |
| `editor-ui:185-186` | feature | use | The Mesh Renderer's material section; the material editor with its **Fix** |
| `editor-ui:561` | figure | use | The Asset tab with a material being edited |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importing textures, the Asset tab and import settings | `make/assets` | must |
| Components and the Inspector | `make/scenes-entities` | must |
| The Scene view's chips | `make/editor-tour` | helps |
| Colors and color spaces as a subject | `basics/color` | helps |

**Starting state.** The end state of `make/assets` (`startsFrom {"tutorial": "make/assets"}`): the level with the coin
model placed, scaled and tagged. The three texture files come from the release's
`Samples/PhysicsPlayground/Assets/Textures/Metal/` (credited in that sample's `CREDITS.md`). The page ends with
`Materials/Gold.stmat` on the coin and `Materials/Ball.stmat` on the ball.

**Command-only steps.** none

## `make/prefabs` — Prefabs

**Covers.** The page turns Coin Run's coin into a prefab and fills the level with coins. The idea first, in one
paragraph and the override figure: one coin saved as an asset, many linked copies in the scene, one place to change
them all, and each copy keeping values of its own. The steps. (1) Right-click the coin in the Hierarchy ▸ **Create
Prefab** (or drag it into the Content Browser): `Prefabs/Coin.stprefab`; the coin in the scene becomes its first
instance, with a prefab badge in the Hierarchy and the prefab bar in the Inspector. (2) Place four more: drag the
prefab into the Scene view; the box ghost rests on the surface under the pointer with its label ("Coin on 'Ground'"),
dimmed over empty space; Escape cancels; Snap puts it on the grid; End drops a selection to the ground. (3) An
override: give one coin a silver material; its overridden property is drawn bold with an accent bar, and the root's
own position and name never count as overrides. (4) Change the prefab: change another coin's emission and **Apply to
Prefab**; every coin takes it except where it overrides. (5) Revert: right-click the overridden property ▸ **Revert**,
or the prefab bar's Overrides menu ▸ **Revert All**; unpack an instance into plain entities, then undo the unpack. (6)
Save. Outdated instances in one paragraph: an instance whose prefab changed in another scene since it last took the
prefab's values is marked, and applying it over those newer changes asks first. Models as prefabs: the coin model of
`make/assets` was already placed as a linked group, and a model's instance offers only Revert. What Strata does not do
here: nested prefabs and prefab variants (a prefab made from linked entities keeps no inner links, so `Coin.stprefab`
no longer follows `coin-gold.glb`; `new:4`), and a prefab edit mode (a prefab changes through an instance and Apply;
`new:5`). At the end the reader can make, place, override, apply, revert and unpack prefabs; the checkpoint has five
coins, all instances of `Prefabs/Coin.stprefab`.

**Leaves out.**

- Prefabs as data: prototypes, instantiation, propagation → `world/prefabs`
- Keeping instances exact while editing, baselines and catch-up → `editor/prefab-instances`
- How a drop finds its surface → `editor/placement`
- Unity's prefab variants and Unreal's Blueprints compared → `start/coming-from`
- Placing many instances with one command → `make/commands`
- Instantiating prefabs from a script → `make/scripting-scene`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 2,700 words against M (3,000). Six steps at B0's length take most of it, with the idea and its
override figure, the paragraph on outdated instances and its exercise, two pictures and the two absences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:60` | feature | home | Placement and the drop ghost: the label, the dimmed ghost, Escape, Snap, a material dropped on a mesh, End to the ground |
| `gamedev:96` | feature | home | Creating a prefab and placing instances |
| `gamedev:97` | feature | home | Overrides, Apply, Revert, Unpack, outdated instances; models offer Revert only |
| `gamedev:98` | feature | home | Models as prefabs: the imported coin placed as a linked group |
| `gamedev:306` | concept | home | Prefabs and instances: reuse with overrides; the mistakes (editing every copy by hand, expecting a moved root to count) |
| `gamedev:416` | figure | home | The override model: the prefab, its instances, values per property, Apply and Revert |
| `gamedev:446` | figure | home | The drop ghost "Coin on 'Ground'" and a dimmed ghost over empty space |
| `gamedev:447` | figure | home | The prefab bar, the overridden properties and the Overrides menu |
| `gamedev:538` | hands-on | home | G5 on Coin Run: the coin made a prefab, five placed, one overridden, another's change applied |
| `gamedev:591` | term | home | Prefab, instance, override |
| `gamedev:592` | term | home | Apply, Revert, Unpack |
| `gamedev:593` | term | home | Outdated instance |
| `editor-core:184` | feature | home | No prefab edit mode; the page's paragraph is `new:5` |
| `editor-core:606` | hands-on | home | The prefab round trip: create, place, override, apply, revert |
| `scene-ecs:599` | hands-on | home | Overrides, propagation, revert and unpack in the editor, as steps 3 to 5 |
| `new:4` | not-done | home | Nested prefabs and prefab variants: a prefab made from linked entities stores no inner links. Evidence: `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` (run at the pin) |
| `new:5` | not-done | home | A prefab edit mode: a prefab changes through an instance and Apply. Evidence: `Docs/Releases/0.7.0.md:380` (run at the pin); the inventory's twin is `editor-core:184` |
| `editor-core:174-178` | feature | use | The `prefab.*` commands in the steps' command tabs |
| `editor-core:191` | feature | use | One placement for the drop and its ghost |
| `editor-core:194` | feature | use | The placement ghost while dragging |
| `editor-core:196-197` | feature | use | `asset.place` and `entity.dropToGround` in the command tabs |
| `editor-core:340` | concept | use | Prefabs as reusable templates with linked instances, at the user's level |
| `editor-core:363` | concept | use | Placing objects in 3D, at the user's level |
| `editor-core:522` | figure | use | The prefab bar with overrides marked |
| `editor-core:526` | figure | use | The placement ghost on a surface and over empty space |
| `editor-core:609` | hands-on | use | Outdated instances, as the paragraph's exercise |
| `editor-core:723` | term | use | Outdated |
| `editor-core:729` | term | use | Placement ghost |
| `scene-ecs:174-175` | feature | use | Per-property overrides; the root's transform and name are the instance's own |
| `scene-ecs:349` | concept | use | Prefabs, at the user's level |
| `scene-ecs:564` | rule | use | The root's transform and name are the instance's own |
| `scene-ecs:666` | term | use | Prefab |
| `scene-ecs:669` | term | use | Instance and instance root |
| `scene-ecs:671-672` | term | use | Override; Apply, Revert, Unpack and propagation |
| `editor-ui:184` | feature | use | The prefab bar and the override marks |
| `editor-ui:205` | feature | use | The drop and its ghost in the Scene view |
| `editor-ui:568` | figure | use | A prefab dragged over the Scene view with its ghost |
| `editor-ui:690` | hands-on | home | A prefab made, values overridden on an instance, applied and reverted through the Inspector |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, the Hierarchy and the Inspector | `make/scenes-entities` | must |
| The Content Browser and models placed as linked groups | `make/assets` | must |
| Materials and assigning them | `make/materials` | must |
| Undo | `make/project-files` | must |

**Starting state.** The end state of `make/materials` (`startsFrom {"tutorial": "make/materials"}`): the level, the
gold coin and the metal ball. The silver material of step 3 is made in the step from the gold one. The page ends with
five instances of `Prefabs/Coin.stprefab`.

**Command-only steps.** none

## `make/lighting` — Lighting a scene: sun, sky and exposure

**Covers.** The page lights Coin Run for play and teaches light at the maker's level. It starts with what Basic 3D
already holds, because this page is the home of the default template's lighting: a Sun of 120,000 lux 40 degrees up
with soft shadows, a Sky with the physical atmosphere of the Clear preset, a Post Process with the Filmic tone curve,
automatic exposure and a compensation of +0.25, and why each value is real. Then, in this order, each idea with a step
and what to see. Light in real units, from zero: lux for the sun's light on the ground, candela for a lamp, nits for
the sky and for emission, with the reference values table (a sunny day, an office, a candle). Exposure in EV stops from
zero: each stop doubles or halves the light, so a table of powers of two stands in for logarithms. (1) Change the Sun to
60,000 lux: little changes, because automatic exposure follows. (2) Turn **Auto Exposure** off: at an **Exposure** of 0
the image is white; set it near -15 and back, which is G7's "break it and fix it"; turn Auto Exposure on again. (3) The
washed-out gray failure: turn the Sun off and see automatic exposure brighten the dark scene to gray; the fix with the
Auto Exposure limits; why a real sun needs **Auto Exposure Max EV** 16. (4) The sky's three sources on the Sky entity:
Atmosphere, Procedural, and Environment Map with an HDR sky from
`Samples/ThirdPerson/Assets/Environment/kloofendal_48d_partly_cloudy_puresky_1k.hdr` (Poly Haven, CC0), its **Extract
Sun** and **Remove Sun**, so the sun is not counted twice. (5) The presets in the Inspector's Sky section (nothing
selected): Clear, Hazy, Overcast and Golden Hour, one undo step each, which keep the sun's direction and set exposure
safely; the sun-to-sky ratio table explained (6 to 10 on a clear noon, below 0.3 overcast). What Strata does not do
here (`new:20`): no clouds, stars or moon; the atmosphere's haze is clear aerosol, and Overcast is a nearly uniform
procedural sky. (6) Turn the Sun with the
Rotate gizmo and watch the shadows follow. (7) Sun shadows at the maker's level: Cast Shadows, Shadow Distance (enough
for the 20 m level), Shadow Softness (the sun's size), Cascade Blend; point and spot shadows are `make/lamps`'. (8)
Preview lighting: in a new, unsaved scene with no light the Scene view still shows the objects lit while the Game view
is black; the rule that a scene with no light is unlit in the game. (9) The Luminance debug view: read the ground's EV
band; the Albedo view is `make/materials`' audit. (10) The coin's emission strength in nits, set against the reference
values. (11) Coin Run lit for play: the chosen preset, the sun turned so that coins cast readable shadows; save. At the
end the reader can read and set light in real units, choose a sky and its preset, set exposure on purpose and tell
preview lighting from real light; G7's lantern is `make/lamps`', fog is `make/look`'s.

**Leaves out.**

- Light units as physics: radiometry, photometry, conversions → `light/units-exposure`
- Metering, adaptation and the exposure key inside → `image/exposure`
- Pre-exposure → `image/pre-exposure`
- Tone mapping and the Filmic curve → `image/tone-mapping`
- The sky as a light inside, `HDRSun` and the atmosphere → `light/sky`, `light/atmosphere`
- Shadow mapping, cascades and the shadows view → `light/shadow-basics`, `light/sun-shadows-1`
- The lights, preview lighting inside → `light/lights`
- Measuring light and the other debug views → `light/measuring-light`
- Point and spot lights, their shadows and source radius → `make/lamps`
- Fog, the camera's image and post effects → `make/look`
- Reflections, probes and ambient occlusion → `make/reflections`
- Powers and logarithms from zero → `basics/numbers`

**Fit.** `fits`: about 5,100 words against L (5,000). Eleven steps at B0's length take most of it, with the template's
values read first, light units and EV stops taught from zero with their tables, the units map, nine pictures and two
exercises. The shadows stay at the maker's four controls and the debug views at one.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-direct:106` | feature | home | The balanced default template: Basic 3D's sun, sky and exposure, read first; the home of the default template's lighting |
| `gamedev:106` | feature | home | Light units: lux for the sun, candela for lamps, nits for the sky and emission; Source Radius named for `make/lamps` |
| `gamedev:107` | feature | home | The sky's three sources, Extract Sun and Remove Sun |
| `gamedev:108` | feature | home | The four sky presets in the Inspector's Sky section |
| `gamedev:110` | feature | home | Sun shadows at the maker's level; point and spot shadows left to `make/lamps` |
| `gamedev:114` | feature | home | The Luminance debug view in EV; the Albedo view named for `make/materials` |
| `gamedev:118` | feature | home | Preview lighting: editor views light a scene with no light; the game does not |
| `gamedev:311` | concept | home | Light, units and exposure: real units, EV like a camera, automatic exposure; the two mistakes |
| `gamedev:461` | figure | home | Basic 3D under each sky preset |
| `gamedev:462` | figure | home | Auto Exposure on and off; the washed-out gray failure and its fix |
| `gamedev:463` | figure | home | Preview lighting in the Scene view against the black Game view |
| `gamedev:464` | figure | home | The Luminance view on Coin Run's level (the Albedo view is shown by `make/materials`) |
| `gamedev:506` | rule | home | A scene with no light is unlit in the game, though editor views show preview lighting |
| `gamedev:508` | rule | home | Automatic exposure brightens dark scenes to gray; a real sun needs Max EV 16 |
| `gamedev:540` | hands-on | home | G7's sky and exposure half: each preset, exposure broken at -15 and fixed; the lantern is `make/lamps`' |
| `gamedev:597` | term | home | Preview lighting |
| `gamedev:598` | term | home | Lux, candela, nits |
| `gamedev:599` | term | home | Exposure (EV) |
| `render-indirect:531` | hands-on | home | Step 4: each sky source, the HDR map with Extract Sun, the atmosphere |
| `render-indirect:532` | hands-on | home | Step 5: the four presets and the ratio table |
| `new:20` | not-done | home | Clouds, stars and a moon: the atmosphere's haze is clear aerosol, and the Overcast preset is a nearly uniform procedural sky. Evidence: `Strata/src/Strata/Renderer/SkyPresets.cpp:35-37`; `git grep -niw -e moon -e stars -e starfield -e cloud -e clouds 822a7a46 -- Strata/src Strata/shaders` finds only that comment, a tooltip's full-moon illuminance (`Strata/src/Strata/Renderer/RendererComponents.cpp:289`) and two comments on cloud placeholder files (`Strata/src/Platform/Windows/WindowsFileSecurity.h:28`, `Strata/src/Strata/Core/Platform.h:104`) (run at the pin) |
| `render-direct:37` | feature | use | Emission in nits, for the coin's glow |
| `render-direct:84` | feature | use | Preview lighting |
| `render-direct:101-102` | feature | use | Photometric units on one scale; the exposure model, at the maker's level |
| `render-direct:105` | feature | use | The table of reference values |
| `render-direct:120` | feature | use | Cascade Blend, as a maker's control |
| `render-direct:159-161` | feature | use | The presets; Extract Sun and Remove Sun; the sun-to-sky ratio |
| `render-direct:178` | feature | use | The lighting debug views, Luminance among them |
| `render-direct:278` | concept | use | Light as a quantity, at the maker's level |
| `render-direct:293` | concept | use | Exposure and EV, at the maker's level |
| `render-direct:480` | figure | use | The light units map |
| `render-direct:539-540` | figure | use | The same scene at two lights and two exposures; the Luminance view |
| `render-direct:555` | figure | use | The three sky sources side by side |
| `render-direct:564-565` | figure | use | Extract Sun before and after; preview lighting |
| `render-direct:571` | rule | use | Every intensity has a unit |
| `render-direct:616` | rule | use | Only one directional light shines |
| `render-direct:624` | rule | use | A real sun needs automatic exposure with Max EV 16 |
| `render-direct:639` | hands-on | use | Each preset with its ground illuminance and ratio, as an exercise |
| `render-direct:648` | hands-on | use | Extract Sun and the shadows that appear, as an exercise |
| `render-image:66` | feature | use | Manual exposure |
| `render-image:88` | feature | use | The Min and Max EV limits of automatic exposure |
| `render-image:95` | feature | use | EV100 and its reference table |
| `render-image:99` | feature | use | Presets that set exposure safely |
| `render-image:101` | feature | use | The Luminance view |
| `render-image:334` | concept | use | Automatic exposure's intent, at the maker's level |
| `render-image:486-487` | figure | use | The manual exposure sweep; automatic exposure on and off |
| `render-image:587` | hands-on | use | Find your exposure |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Components, the Inspector and scene settings | `make/scenes-entities` | must |
| Turning things with the Rotate gizmo; degrees | `make/transforms-units` | must |
| Materials and emission as a color and a strength | `make/materials` | must |
| The Scene view's chips and the Game view | `make/editor-tour` | must |
| Powers and logarithms | `basics/numbers` | helps |

**Starting state.** The end state of `make/prefabs` (`startsFrom {"tutorial": "make/prefabs"}`): the level with five
coin instances, the gold and metal materials, and Basic 3D's own lighting. The HDR sky comes from the release's
`Samples/ThirdPerson/Assets/Environment/` (credited in that sample's `CREDITS.md`); the scene with no light of step 8
is not saved. The page ends with Coin Run lit for play.

**Command-only steps.** none

## `make/first-script` — Your first script

**Covers.** The page makes Coin Run's coins spin with a script of the reader's own, and is the reader's first meeting
with code: on tracks G and B the reader has never programmed (`basics/programming-1` comes next), so every line the
page shows gets a sentence on what it does, at the level of names, as `start/how-to-read` taught for code one does not
understand yet. The steps. (1) Choose the code editor: **File ▸ Preferences ▸ External Editor** lists the editors found
(VS Code, Visual Studio, CLion); the page tells why the editor opens files without a shell. (2) **Scripts ▸ New
Script...**: the class name `Coin` (the dialog refuses names the SDK or the project already use); `Scripts/Coin.cpp`
opens in the code editor and the scripts start building ("Building" in the status bar). The template is read line by
line: the SDK's include, `using namespace Strata`, `class Coin : public Script` (a script class is built on the
SDK's `Script`), a field with its default, `OnCreate` and `OnUpdate` marked `override`, `deltaTime` as the frame's game
time in seconds, and `ST_SCRIPT_CLASS` with `ST_SCRIPT_FIELD` at the end. (3) Replace the template's body with the
spin: a field `DegreesPerSecond` and the two lines of the `Spinner` of `start/first-game` (the turn, from
`make/transforms-units`), shown whole as the generated `Spinner` has them. (4) Build with **Ctrl+B** (**Scripts ▸ Build
Scripts**): the first build configures CMake, later ones are quick; the Problems panel stays empty; IntelliSense works
once a build ran. (5) Attach: on one coin, **Add Component ▸ Script** and pick `Coin`, then **Apply to Prefab** so every
coin spins (`make/prefabs`); the Content Browser's **Scripts** root lists `Coin.cpp` with the class it registers. (6)
**Play**: Play builds changed sources first ("Building to play"); the coins spin; change `DegreesPerSecond` in the
Inspector for one coin, which is what a field is for. (7) One line of `Log::Info` in `OnCreate`, read in the Console.
(8) A build error on purpose: delete a `;`, build, read the toast and the Problems panel (file and line), double-click
to open the line, fix it. (9) Hot reload: while the game plays, change the spin (another axis), build again: the
coins change without stopping; each instance is made again, fields keep their values, `OnReload` runs instead of
`OnCreate`, and a plain member starts over. (10) A crash on purpose: a line the page gives, a write through a null
pointer as in `scripting/crash-containment`'s example, which faults on every platform (a division by zero would not:
on ARM64, the Apple silicon of Strata's macOS releases, integer division by zero gives 0); build and play: the script's
module is switched off, play stops, the toast and the Problems panel show the crash and its stack, and the editor goes
on; remove the line. One warning sentence: on Linux and macOS, `abort()`, a failed `assert()` or `std::terminate` in a
script ends the whole editor with its unsaved work (Windows contains them in the modules the editor builds), so a script
reports a broken state with `Log::Error`, not `assert`. Three rules in `:::rule` asides, each with its reason: do the
game's setup in `OnCreate`, not the constructor (the module makes one instance without an entity to read the defaults);
`ST_SCRIPT_CLASS` once per class, in a `.cpp`, never in a header; only members registered with `ST_SCRIPT_FIELD` survive
hot reload. The other field types are named in one sentence for `make/script-fields`. At the end the reader can write,
build, attach and change a script, read a build error and a crash, and use hot reload; the next four pages teach
programming from zero on this script.

**Leaves out.**

- Values, variables, decisions, loops, functions, classes and the rest of C++ from zero → `basics/programming-1`, `basics/programming-2`, `basics/programming-3`
- Finding bugs with a debugger attached to the editor → `basics/debugging`
- The lifecycle: when each callback runs, fixed updates → `make/script-loop`
- Fields of every type, references and prefab overrides of fields → `make/script-fields`
- Building outside the editor, the `strata` preset, what a module is → `make/script-builds`
- How the editor builds scripts → `editor/script-builds`
- What `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` do inside → `scripting/abi-sdk`
- Hot reload inside → `scripting/hot-reload`
- Crash containment and symbolization inside → `scripting/crash-containment`, `scripting/symbolization`

**Fit.** `fits`: about 3,950 words against M (3,000). Ten steps at B0's length take most of it, with the template read
line by line, the `Spinner` excerpt, three rules with their reasons, six pictures and the hot reload exercise. B0 meets
code here for the first time, so no line goes unexplained, and the page is near M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:359` | code | home | `StrataEditor/src/Editor/ScriptProject.cpp:230-257`: the generated `Spinner`, the smallest complete script (class, field, `OnUpdate`, the turn, the registration) |
| `gamedev:360` | code | home | `Docs/Manual/Scripting.md:14-37`: what **New Script...** writes, with a comment on when each callback runs |
| `gamedev:47` | feature | home | The toasts of a failed build and of a crash, with **Show Problems** |
| `gamedev:54` | feature | home | The Console's clickable file and line; the Problems panel's build errors and crashes |
| `gamedev:61` | feature | home | Preferences: the External Editor page |
| `gamedev:125` | feature | home | The script class and its fields: `class X : public Script`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`; the field types named |
| `gamedev:129` | feature | home | **Scripts ▸ New Script...** and its validation |
| `gamedev:130` | feature | home | **Ctrl+B**; Play builds changed sources first |
| `gamedev:132` | feature | home | Hot reload: instances made again, fields kept, `OnReload` |
| `gamedev:133` | feature | home | Crash containment as the maker sees it: the module switched off, play stopped, the report |
| `gamedev:323` | concept | home | Hot reload and state: fields survive, plain members do not |
| `gamedev:449` | figure | home | The New Script dialog; the generated file in the code editor |
| `gamedev:450` | figure | home | The Problems panel with a build error; the crash toast and the crash with its stack |
| `gamedev:453` | figure | home | Preferences: the External Editor page with the editors found |
| `gamedev:484` | rule | home | Do setup in `OnCreate`, not the constructor |
| `gamedev:486` | rule | home | Only public members registered with `ST_SCRIPT_FIELD` survive hot reload |
| `gamedev:523` | rule | home | `ST_SCRIPT_CLASS` once per class, in a `.cpp` |
| `gamedev:539` | hands-on | home | G6 on Coin Run: the script attached, its field changed, the code changed during Play |
| `gamedev:605` | term | home | SDK |
| `gamedev:608` | term | home | Field |
| `gamedev:609` | term | home | Hot reload (the meaning of scripts) |
| `gamedev:610` | term | home | Crash containment |
| `gamedev:612` | term | home | External editor |
| `gamedev:613` | term | home | Problems panel |
| `scripting:208` | feature | home | The Scripts menu (New Script..., Build Scripts, External Editor..., Open Scripts Folder, Show Problems), the Script component's class picker, the build pills |
| `scripting:509` | hands-on | home | Hello script: the steps of the page are this exercise on Coin Run |
| `scripting:584` | term | home | Field, as the scripting inventory defines it (`ST_SCRIPT_FIELD`'s home) |
| `scripting:105` | feature | use | The `Script` base class |
| `scripting:114-115` | feature | use | `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`; the field types |
| `scripting:124` | feature | use | `Log` |
| `scripting:154` | feature | use | The Script component that holds the class |
| `scripting:190` | feature | use | An exception switches off one instance, a crash the module |
| `scripting:205` | feature | use | The `script.*` commands in the steps' command tabs |
| `scripting:303` | concept | use | Crash containment, at the maker's level; step 10's warning: on Linux and macOS `abort()`, a failed `assert()` or `std::terminate` ends the editor, so a script reports a broken state with `Log::Error`. Evidence: `Strata/src/Strata/Scripting/ScriptEngine.h:40-44`; `StrataScriptCore/CMake/StrataScriptModule.cmake:104` (the modules link the C runtime statically on Windows); `.claude/skills/strata-scripting/SKILL.md:654-655` (read at the pin) |
| `scripting:319` | concept | use | Hot reload, at the maker's level |
| `scripting:326` | concept | use | Fields shown and saved by the editor |
| `scripting:435` | figure | use | The Problems panel with a compiler error and with a crash |
| `scripting:437-438` | figure | use | The crash in the Console with its toast; hot reload in action |
| `scripting:467` | rule | use | Constructors without side effects |
| `scripting:470` | rule | use | One `ST_SCRIPT_CLASS` per class, in a `.cpp` |
| `scripting:472` | rule | use | Only fields survive hot reload |
| `scripting:476` | rule | use | Exceptions disable an instance; crashes fault the module |
| `scripting:511` | hands-on | use | Hot reload a running game, as an exercise on a ThirdPerson copy |
| `scripting:525` | hands-on | use | Crash on purpose: step 10 writes through a null pointer, which faults on every platform (integer division by zero does not trap on ARM64), and its exercise with an exception. Evidence: `StrataTests/Scripts/Faults/FaultScripts.cpp:57-60`; `StrataTests/src/Scripting/ScriptFaultTests.cpp:31-33` (read at the pin) |
| `editor-ui:149` | feature | use | The Problems panel |
| `editor-ui:220` | feature | use | The New Script dialog and the External Editor page |
| `editor-ui:232` | feature | use | The Preferences dialog |
| `editor-ui:573` | figure | use | Toasts with their action buttons |
| `editor-ui:692` | hands-on | use | A broken build followed through the pills and toasts to Problems |
| `editor-ui:748` | term | use | Toast |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The C++ build tools and a code editor installed and checked | `start/install` | must |
| The `Spinner` built and attached once; Play and the Console | `start/first-game` | must |
| Components, Add Component and the Inspector | `make/scenes-entities` | must |
| A rotation as an axis and an angle; degrees and radians | `make/transforms-units` | must |
| Applying an instance's change to its prefab | `make/prefabs` | must |
| How to read code you do not understand yet | `start/how-to-read` | must |
| Frame time: one frame's seconds | `start/what-an-engine-is` | helps |
| Values, variables, classes and members as programming | `basics/programming-3` | helps |

**Starting state.** The end state of `make/lighting` (`startsFrom {"tutorial": "make/lighting"}`): Coin Run lit for
play with five coin instances. The script `Coin.cpp` of each stage is a file of the tutorial
(`tutorials/make/first-script/`), copied by the runner and typed by the reader. The page ends with the coins spinning;
this checkpoint is the start of the Coin Run practice items of `basics/programming-1` to `basics/debugging`
(`critique/rulings-4.md`, R11).

**Command-only steps.** none

## `make/script-loop` — The game loop from a script's side

**Covers.** A concept page, home of the script lifecycle and its callbacks and use home of the fixed step. The
problem as the reader meets it: the coins spin at the same speed on a fast and a slow computer because the turn is
multiplied by `deltaTime`; the ball of `make/physics` will need more than that. The naive answer, a constant amount
moved each frame, and where it breaks (twice the frame rate, twice the speed). The idea, in one paragraph and the
frame timeline: a frame of variable length runs `OnUpdate` once; game time advances in fixed steps (1/60 s by default)
that run zero, one or several times per frame, each with physics and `OnFixedUpdate`; then `OnLateUpdate`; an
accumulator holds the time not yet simulated, capped so a long frame does not snowball, and when steps cannot keep up
the game slows (time dilation) instead of freezing. The approaches engines use, each brought in by the flaw of the one
before: a fixed loop tied to the display, a variable delta for everything, a fixed simulation with variable drawing,
in a table of costs with sources. Strata's choice and its reason, with the design decision in a `:::why` aside (game
time counts fixed steps, never frames, home `core/time`): `OnUpdate` per frame, `OnFixedUpdate` per step, the
project's **FixedRate** (Scene, 30, 60, 120 or 240 on the Timing page of Project Settings) over the scene's own fixed
step, time scale as a multiplier of game time (0 pauses it), and `Time`'s delta and fixed delta. The lifecycle: the
base class's comment read whole, then each callback in order (constructed, fields applied, `OnCreate` once all
existing scripts are constructed, the update callbacks, `OnDestroy`; `OnReload` after a hot reload), with the contact
and UI callbacks named with the pages that use them; instances update parents first, then in the order of the
scripts on an entity; inactive entities get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, and no new contacts or
animation events, while `OnCreate` and `OnDestroy` run anyway and a contact that began still ends with its Exit (the
inventory's slip, `new:22`); a destroyed entity goes at the end of the frame. What Strata does not do here
(`new:21`): no callback when an entity is activated or deactivated (no `OnEnable` or `OnDisable`; `OnCreate` is the
only start). The page's example, with no Coin Run stage: the `Coin` script also bobs, its height from a sine of
`Time::GetElapsedTime()` in `OnUpdate`, with the sine given as a recipe (a value that swings between -1 and 1);
`make/scripting-scene` builds it as its first step. What the choice cannot do: drawing between two steps is the
interpolation that `make/characters-cameras` turns on in code. Common mistakes: constant per-frame moves; putting in
`OnFixedUpdate` what must happen once a frame, since fixed updates run zero, one or several times a frame (the presses
of a key are that case, and `make/physics` shows it); blocking a script or starting threads in it, which stops the
whole frame. At the end the reader can say which callback runs when, why physics needs fixed steps,
and what time scale and FixedRate change.

**Leaves out.**

- The clock, the accumulator and time dilation as the engine runs them → `core/time`
- The fixed step's code in `Scene` → `world/systems`
- The script system's dispatch and order inside → `scripting/script-system`
- Drawing between steps, `GetDrawnPosition` → `make/characters-cameras`, `world/interpolation`
- Timers, unscaled time and the clocks of `Time` → `make/timers-events`
- Pausing a game with a menu at time scale 0 → `make/menus`
- Pausing and stepping in the editor → `make/play-test-debug`
- Sine and cosine as mathematics → `basics/math-vectors`

**Fit.** `over`: about 4,050 words against M (3,000). Five ideas taught from zero at B0's length, the approaches table,
the base class's comment, the bob's code, two figures, three mistakes and the exercise take it over M's top. L (5,000)
by S2: the page is the home of the lifecycle and the use home of the fixed step at once, and neither half can move to
another page of track B.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:361` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:30-47`: the base class's comment, every callback and when it runs, update order and inactive entities |
| `gamedev:70` | feature | use | Scene settings: the fixed timestep and the steps per frame, greyed when the project's FixedRate rules; the item's home, with the Physics section, is `make/physics` |
| `gamedev:126` | feature | home | The 15 lifecycle callbacks; only those a class overrides are called |
| `gamedev:156` | feature | home | Timing: FixedRate; its Interpolation switch named for `make/characters-cameras` |
| `gamedev:158` | feature | home | Time dilation: the game slows instead of spiralling |
| `gamedev:286` | concept | home | What a game is to a computer: a loop of frames and fixed steps; the mistakes (per-frame amounts; what must happen once a frame put in `OnFixedUpdate`, which runs zero to N times a frame). The press half of the second mistake is `make/physics`' with its rule `gamedev:488` |
| `gamedev:321` | concept | home | The script lifecycle and its order: `OnCreate` after construction, parents first, destruction at the end of the frame; inactive entities get no update callbacks, while `OnCreate` and `OnDestroy` run anyway (`new:22`) |
| `gamedev:405` | figure | home | The frame timeline from a script's side, with the accumulator at 30, 60 and 144 Hz |
| `gamedev:412` | figure | home | The script lifecycle as a state machine, with the hot reload branch |
| `gamedev:497` | rule | home | Never block or start threads in a script |
| `gamedev:615` | term | home | Fixed step |
| `gamedev:616` | term | home | Accumulator |
| `gamedev:617` | term | home | Time scale |
| `gamedev:620` | term | home | Time dilation |
| `scripting:289` | concept | home | The script lifecycle: the callbacks, their order and the instance's states; what an inactive entity still gets (`OnCreate`, `OnDestroy`, the Exit of a contact that began) and what it does not (update callbacks, new contacts, animation events) |
| `new:21` | not-done | home | Callbacks when an entity is activated or deactivated: no `OnEnable` or `OnDisable`; `OnCreate` is the only start. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:83-97`, the 15 callbacks; `git grep -n -e OnEnable -e OnDisable 822a7a46 -- StrataScriptCore Strata/src` finds nothing (run at the pin) |
| `new:22` | erratum | home | `plan/inventory/gamedev.md:322` says that inactive entities get nothing. At the pin they get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate`, but `OnCreate` and `OnDestroy` run regardless, and a contact that began before the entity was deactivated still ends with its Exit. The page states the code's facts; its brief says that no test covers the `OnCreate` half (the test of inactive entities deactivates them after the start: `StrataTests/src/Scripting/ScriptLifecycleTests.cpp:131-158`). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:276-280`, `:347-352` (contacts begin for active entities only), `:394` (animation events), `:664-679`; `Strata/src/Strata/Scripting/ScriptSystem.h:55-56`; `StrataScriptCore/Include/StrataScript/Script.h:57-58` (read at the pin) |
| `scripting:570` | term | home | Callback, in the meaning of scripts |
| `scripting:587` | term | home | Fixed update |
| `foundation:184-185` | feature | use | The accumulator and time dilation as Strata runs them, at the maker's level |
| `foundation:187` | feature | use | The project's FixedRate |
| `foundation:228` | concept | use | The fixed timestep, the accumulator and time scale, at the maker's level |
| `foundation:406` | figure | use | The fixed step on a time axis |
| `foundation:539` | hands-on | use | One object moved in `OnUpdate` and one in `OnFixedUpdate`, as an exercise |
| `scene-ecs:112-113` | feature | use | The project's rate over `SceneSettings` |
| `scene-ecs:222` | feature | use | The `Scene.Timing` section on the Timing page |
| `scene-ecs:316` | concept | use | Game loop time, at the maker's level |
| `scripting:92` | feature | use | The 15 class callbacks |
| `scripting:123` | feature | use | The SDK's `Time` |
| `scripting:165` | feature | use | Update order: parents first, then script order |
| `scripting:294` | concept | use | Deferred destruction at the end of the frame |
| `scripting:411` | figure | use | The instance lifecycle state machine |
| `scripting:414` | figure | use | A frame timeline for scripts |
| `scripting:462` | rule | use | The engine calls scripts on one thread; never call it from threads of your own |
| `scripting:479` | rule | use | Never block in a script |
| `scripting:483` | rule | use | The root of the rule: what must happen once a frame goes in `OnUpdate`; the press and release edges themselves are `make/physics`' |
| `editor-ui:187` | feature | use | The scene settings' fixed rate link with nothing selected |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The `Coin` script, `OnUpdate` and `deltaTime`, building and hot reload | `make/first-script` | must |
| Variables, `if`, loops, functions, classes and members | `basics/programming-3` | must |
| The frame map and frame time | `start/what-an-engine-is` | must |
| Project Settings and its pages | `make/project-files` | must |
| Sine as a wave between -1 and 1 | `basics/math-vectors` | helps |
| Breakpoints and the log | `basics/debugging` | helps |

## `make/scripting-scene` — Scripts and the scene: finding, spawning and changing entities

**Covers.** The goal: the coins bob, a script places Coin Run's coins, and a coin the ball reaches is hidden or
destroyed. What must be true first: Coin Run at the end of `make/first-script` (the coins spin), `make/script-loop`
read (its example is the bob), and "The same ideas in code" of `make/transforms-units` read again. First a table of
the SDK's namespaces, each with the page that teaches it (`Entity`, the `Component` proxy, `TransformComponent`,
`Scene` and `Assets` here, the home of their use; `SubScene` on `make/levels-saves`; `Input` on `make/input`;
`Physics` and `RigidBody` on `make/physics`; `AudioSource` and `Audio` on `make/sound`; `UIElement` on `make/hud`;
`Time` on `make/script-loop` and `make/timers-events`; `Game` on `make/levels-saves`; the rest in block B); the facts of
every class are `reference/script-api`'s. The steps, each with its code from the tutorial's files and what to see.
(1) The bob, as `make/script-loop`'s example: the `Coin` script sets the coin's height from a sine of
`Time::GetElapsedTime()` in `OnUpdate`, built and played, so every instance of the prefab bobs. (2) An empty entity
`Coins` with a new script `CoinPlacer`. (3) Ask for the coin
prefab early: `Assets::Find("Prefabs/Coin.stprefab")` and `Assets::RequestLoad` in `OnCreate`; the page's rule in a
`:::rule` aside: request assets early, because `Instantiate` never waits and gives back an empty entity for what is not
loaded (no frame waits for the disk). (4) Place the coins once the prefab is loaded (`Assets::IsLoaded`, then
`Scene::Instantiate` with a position, as a parent of `Coins`), in a loop over a list of positions, so the five
hand-placed coins of `make/prefabs` can go; `Assets::GetLoadProgress` and `Release` named, with a gotcha line: the
requests are the scene's, not each script's, and do not add up, so one `Release` ends a request that two scripts
made. (5) Find entities: the
ball with `Scene::FindEntityByName("Ball")`, every coin with `Scene::FindEntitiesByTag("Coin")` (the tag of
`make/scenes-entities`); `IsValid`, and storing an `Entity` rather than anything that outlives a frame. (6) Read and
write a transform: local and world positions, rotation and scale through `TransformComponent`. (7) Components by name:
`HasComponent`, `GetProperty` and `SetProperty` with the Inspector's names (a coin's emission raised as it is
collected), and the `Component` proxy. (8) Collect a coin: when the ball comes near (a distance with `glm::distance`,
given as a recipe), first hide it with `SetActive(false)`, then destroy it with `Destroy()` (it goes at the end of the
frame); during Play the ball is dragged onto a coin with the gizmo, since moving it is `make/input`'s. (9) Entities in
the hierarchy: `GetParent`, `GetChildren`, `SetParent`, `Scene::GetRootEntities`, `Scene::CreateEntity` and the primary
camera with `Scene::GetPrimaryCamera`, each in a short step on the `Coins` group. `## Result`: coins that bob, placed by
a script and collected by the ball; it ends with the download of the page's end state. `## Variations`: destroying
every entity of a tag at once (the scene inventory's exercise); placing many copies in one call is
`make/performance`'s `InstantiateMany`; a prefab chosen in a field is `make/script-fields`'. The exercises
(`new:23`) are done in a script.

**Leaves out.**

- Asset fields and `Instantiate` by a handle in a field → `make/script-fields`
- `InstantiateMany` → `make/performance`
- Scripts that find and call each other (`GetScript<T>`) → `make/timers-events`
- Residency, pins and eviction inside → `assets/residency`
- Vectors, distances and directions as recipes → `make/gameplay-math`
- Triggers that replace the distance test → `make/physics`
- The SDK's classes as facts → `reference/script-api`
- How a host call crosses into the engine → `scripting/host-api`

**Fit.** `fits`: about 4,650 words against L (5,000). Nine steps, several with two or three calls, and four code
excerpts from the tutorial's files take most of it, with the namespace table, the rule, three Variations and two
exercises; a how-to keeps theory to two sentences a section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:127` | feature | home | The SDK's namespaces, each sent to the page that teaches it |
| `gamedev:128` | feature | home | Components by their Inspector names: `GetProperty` and `SetProperty` |
| `gamedev:494` | rule | home | Request assets early; `Instantiate` never waits |
| `scene-ecs:598` | hands-on | home | Coins found by their tag and destroyed, as step 8 and a Variation |
| `scripting:118` | feature | home | The SDK's `Entity`, the use the steps teach: `IsValid`, name and tag, `SetActive`, `Destroy` at the end of the frame, the hierarchy (`GetParent`, `GetChildren`, `SetParent`), components by their Inspector names (`HasComponent`, `GetProperty`, `SetProperty`); the typed accessors and `GetScript<T>` named with the pages that use them; the facts are `reference/script-api`'s link |
| `scripting:119` | feature | home | The SDK's `Component` proxy: `GetComponent("<name>")` and its `Get` and `Set` by property name, in step 7 |
| `scripting:120` | feature | home | The SDK's `TransformComponent` in use: local and world position, rotation and scale read and written (step 6), as "The same ideas in code" of `make/transforms-units` showed them |
| `scripting:121` | feature | home | The SDK's `Scene` and `Assets` in use: `CreateEntity`, `FindEntityByName`, `FindEntitiesByTag`, `GetRootEntities`, `GetPrimaryCamera`, `Instantiate` with a position; `Assets::Find`, `RequestLoad`, `IsLoaded`, `GetLoadProgress` and `Release`. `SubScene` is named in the table with `make/levels-saves`, which loads one, and `InstantiateMany` with `make/performance` |
| `scripting:123` | feature | use | The SDK's `Time`: `Time::GetElapsedTime` in step 1's bob |
| `new:23` | hands-on | home | Exercises, done in a script: **Basic.** log the number of coins left (`Scene::FindEntitiesByTag("Coin").size()`) once a second, and predict the count after two coins are collected; **Medium.** switch the whole `Coins` group off from `CoinPlacer` with `SetActive(false)` five seconds after the start, predict whether the coins still bob (they do not: inactive entities get no updates), and switch it on again. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:123` (`FindEntitiesByTag`); `StrataScriptCore/Include/StrataScript/Entity.h:51` (`SetActive`); `StrataScriptCore/Include/StrataScript/Script.h:46` (inactive entities receive no updates) |
| `scripting:169` | feature | use | A script's asset requests; step 4's gotcha line: they belong to the scene and do not add up, so one `Assets::Release` ends a request that two scripts made. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.h:131-132`; `StrataScriptCore/Include/StrataScript/Scene.h:44-46` (read at the pin) |
| `scripting:334` | concept | use | Asynchronous assets from game code, at the maker's level |
| `scripting:481` | rule | use | Request assets early; `Instantiate` never waits |
| `scene-ecs:92` | feature | use | Finding entities by name and by tag |
| `scene-ecs:514` | rule | use | Destruction during an update is deferred |
| `scene-ecs:516` | rule | use | Do not hold an entity's data across frames; hold the `Entity` and check it |
| `assets:67` | feature | use | Asking for an asset never blocks |
| `assets:537` | rule | use | Handle "not loaded yet" every frame |
| `assets:539` | rule | use | Hold handles across frames and request what you use |
| `gamedev:359` | code | use | The `Spinner`'s transform calls, read again from `make/transforms-units` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The lifecycle: `OnCreate`, `OnUpdate`, destruction at the end of the frame; the bob of its example | `make/script-loop` | must |
| The `Coin` script, building and attaching it, and the coins' spin | `make/first-script` | must |
| Variables, loops, functions, lists, classes, `std::optional` and template arguments | `basics/programming-3` | must |
| Positions, rotations, local and world, and the same ideas in code | `make/transforms-units` | must |
| Names, tags, activity and the hierarchy | `make/scenes-entities` | must |
| The coin prefab and instances | `make/prefabs` | must |
| Assets, handles and paths in the project | `make/assets` | must |
| A distance between two points | `basics/math-vectors` | helps |

**Starting state.** The end state of `make/first-script` (`startsFrom {"tutorial": "make/first-script"}`): Coin Run
lit for play with five hand-placed coin instances that spin; `make/script-loop` has no stage. The page's step 1 makes
the coins bob, step 4 removes the five, and its end state, downloaded from `## Result`, has bobbing coins placed by
`CoinPlacer` and the distance test that collects them.

**Command-only steps.** none

## `make/input` — Input and input actions

**Covers.** The page gives Coin Run its Move action and teaches devices against actions. The idea first, in one
paragraph and the input actions figure: a game can read keys and sticks directly, but players want to choose their
controls and to use a keyboard or a gamepad alike, so games name actions (Move, Jump) and bind controls to them; the
project holds the actions in maps, and a player's own bindings override the project's. Then the steps. (1) Read the
keyboard: a new script `BallControl` on the ball moves it with W, A, S and D through `Input::IsKeyDown`, by writing its
position (the ball has no rigid body yet), scaled by `deltaTime`; press, hold and release with `IsKeyPressed`,
`IsKeyDown` and `IsKeyReleased`, read in `OnUpdate`. (2) Keys reach the game only while the Game view has the focus
and the game plays; clicking the Inspector takes them away. (3) Read a gamepad: `IsGamepadConnected`, the left stick
with `Input::GetGamepadStick(GamepadStick::Left)` and its round dead zone (from zero: the small movement a resting
stick reports, ignored in every direction, with the round dead zone drawn; the vector's length is at most 1), and
`GetGamepadAxis` named for one axis or a trigger, whose dead zone works per axis; buttons, the Xbox layout. (4) Make
the action: **File ▸ Project Settings ▸ Input Actions**, the
map **Gameplay** and the action **Move** of kind Vector2, with a `2D:` composite of W, A, S and D, another of the
arrows, and the gamepad's left stick; bind a key by pressing it (the page's binding capture). (5) Read it:
`Input::GetActionValue("Gameplay/Move")` gives a vector of length at most 1 with the dead zone applied; the ball's
script uses it, and the keyboard and gamepad code of steps 1 and 3 goes. (6) Two Button actions: **Jump** (Space and
the gamepad's A), read once per press with `IsActionPressed` (it only logs here; `make/physics` makes the ball jump),
and **Boost** (Shift), held with `IsActionDown`; a toggle made from presses; hold and toggle compared. (7) Edit the
actions while the game plays: the change applies at once and keeps the state of the other actions. (8) Look around:
a Vector2 action **Look** bound to the gamepad's right stick, and the mouse read beside it, because mouse motion is no
binding: the camera turns from `Input::GetMouseDelta()` while the right button is held, with the cursor **Locked** by
`SetCursorMode`; Shift+F1 gives the cursor back to the editor (an optional section, its camera script left out of the
checkpoint; the Look action stays). (9) Several maps, one short section of about 200 words: why a project has several
(walking and driving, a menu over the game); a second map **Vehicle** with one action, which the ball's script
switches on, and **Gameplay** off, with `Input::SetActionMapEnabled` (read back with `IsActionMapEnabled`); the change
applies from the next input frame, and an action held at that moment reports `IsActionReleased` once, as a key let go
would; maps start as the project says in every session; and every gamepad drives an action, so two local players read
their own pads by index (`IsGamepadButtonDown(button, 1)`). The section is optional and its map is left out of the
checkpoint. The binding grammar in a small table (`Key/Space`,
`Gamepad/LeftStick`, `Gamepad/LeftX+`, `1D:`, `2D:`), the reserved map `UI` named for `make/menus`. The rule in a
`:::rule` aside: read the player's controls as input actions, never as fixed keys, because players rebind them. What
Strata does not do here, each in a sentence or two: touch input (`new:24`); action modifiers, chords, processors and
interactions, and mouse motion or scroll as action sources (`new:25`); force feedback (`new:26`); devices assigned to
players for local multiplayer (`new:27`); controllers missing from GLFW's gamepad database, more than four gamepads,
and mappings that a game adds (`new:28`). The exercises (`new:29`) are done in the editor and in a script. At the
end the reader can define actions, bind them, read them from a script and tell when to read devices directly.

**Leaves out.**

- How input reaches a game: events, polling and edges → `input/how-input-works`
- Device state, keyboard capture and the enabled flag → `input/devices-state`
- Gamepads inside: mappings and layouts → `input/gamepads`
- Mouse spaces and cursor modes inside → `input/mouse-cursor`
- Actions inside: evaluation, thresholds, combining → `input/actions`
- Players' bindings, binding capture in a game, saving them, the rebinding screen → `make/menus`
- Typed text in a text field → `make/menus`
- Simulated input for play-tests → `make/automated-playtests`
- The Game view's input ownership inside → `editor-ui/game-view`

**Fit.** `fits`: about 5,250 words against L (5,000). Nine steps, most with code, take most of it, with the idea and the
round dead zone taught from zero, the grammar table, the dead zone plots, four pictures, the five absences and two
exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:143` | feature | home | Device input: keys, mouse, gamepads 0 to 3 with round dead zones, cursor modes, only while the Game view has the focus; Shift+F1 |
| `gamedev:144` | feature | home | Input actions: maps of Button, Axis and Vector2 actions, bindings and composites, dead zones; the reserved `UI` map named |
| `gamedev:325` | concept | home | Input: devices against actions; the mistakes (fixed keys, ignored dead zones, mouse look through an action) |
| `gamedev:414` | figure | home | The input actions pipeline: devices, bindings, the strongest binding, dead zone, value; the player's bindings over the project's |
| `gamedev:498` | rule | home | Read controls as input actions; mouse motion is no action |
| `gamedev:645` | term | home | Input action, map, binding, composite, dead zone |
| `audio-input:563` | hands-on | home | Steps 1 and 3: the keyboard and a gamepad read directly, the left stick with `GetGamepadStick` (a round dead zone, length at most 1) and `GetGamepadAxis` named for one axis or a trigger (a dead zone per axis). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:326-353` (read at the pin) |
| `audio-input:565` | hands-on | home | Step 8: mouse look with a locked cursor |
| `audio-input:567` | hands-on | home | Steps 4 and 5: the direct reads converted to the Move action; step 9: the Vehicle map switched on and off from a script (`SetActionMapEnabled`, `IsActionMapEnabled`), with what disabling does to a held action |
| `new:24` | not-done | home | Touch input. Evidence: `git grep -ni touch 822a7a46 -- Strata/src/Strata/Input Strata/src/Platform/GLFW` finds nothing (run at the pin) |
| `new:25` | not-done | home | Action modifiers, chords, processors and interactions; mouse motion and scroll as action sources (they stay on the raw API). Evidence: `Docs/DeveloperGuide.md:1464-1465`; `Docs/Releases/0.7.0.md:361`, `:412`; `Strata/src/Strata/Input/InputActionSet.cpp:102` refuses every binding but `Key/`, `Mouse/<button>`, `Gamepad/`, `1D:` and `2D:` (read at the pin) |
| `new:26` | not-done | home | Force feedback (rumble, vibration). Evidence: `git grep -ni -e rumble -e vibrat -e haptic 822a7a46 -- Strata/src StrataScriptCore` finds nothing (run at the pin) |
| `new:27` | not-done | home | Devices assigned to players for local multiplayer: gamepad bindings read every gamepad, and all players share one set of actions; a game reads each player's pad by index. Evidence: `Docs/DeveloperGuide.md:1460`; `Docs/Releases/0.7.0.md:361-362`, `:412`; `Docs/Roadmap.md:1707`; `StrataScriptCore/Include/StrataScript/Input.h:301-312` (read at the pin) |
| `new:28` | not-done | home | Controllers missing from GLFW's gamepad database, more than four gamepads, and gamepad mappings that a game adds: an unmapped controller reads as not connected and keeps its slot. Evidence: `Strata/src/Platform/GLFW/GLFWWindow.cpp:416-442`; `Strata/src/Strata/Input/GamepadCodes.h:42` (`c_MaxGamepads = 4`); `git grep -n glfwUpdateGamepadMappings 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src` finds nothing (run at the pin) |
| `new:29` | hands-on | home | Exercises: **Basic.** predict what `Input::GetActionValue("Gameplay/Move")` reads while W and D are held together (a diagonal of length at most 1, not 1.41), then log it to check; **Medium.** a Button action **Pause** (P and the gamepad's Start) whose press sets the time scale to 0 and back with `Time::SetTimeScale`, and a prediction of what the ball and the coins' bob do meanwhile. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:402-404` (a Vector2 action's length at most 1); `StrataScriptCore/Include/StrataScript/Time.h:28-33` (elapsed time is simulation time), `:43-53` (`GetTimeScale`, `SetTimeScale`) |
| `editor-ui:691` | hands-on | home | Step 4's binding of an action by pressing its key; the exercise's collision layers and quality preset are `make/physics`' and `make/quality`'s |
| `audio-input:107-109` | feature | use | Key, mouse and gamepad codes |
| `audio-input:122` | feature | use | Cursor modes |
| `audio-input:148-152` | feature | use | The action model, the binding grammar, kinds, names and the reserved `UI` map |
| `audio-input:153-157` | feature | use | The settings section, evaluation, combining bindings, thresholds and the radial dead zone, at the maker's level |
| `audio-input:158-159` | feature | use | Step 9: every gamepad drives an action, so two local players read their own pads by index; maps switched off and on, applied from the next input frame, a held action released once |
| `audio-input:160` | feature | use | Live edits of the actions while playing |
| `audio-input:162` | feature | use | Players' bindings over the project's, named for `make/menus` |
| `audio-input:180-181` | feature | use | The `inputActions.*` commands; the Input Actions page |
| `audio-input:315` | concept | use | Mouse spaces and cursor modes, at the maker's level |
| `audio-input:321` | concept | use | Gamepads, at the maker's level |
| `audio-input:339` | concept | use | Actions instead of keys |
| `audio-input:451-452` | figure | use | The gamepad's conventions; the dead zone plots, step 3's showing the round zone of `GetGamepadStick` |
| `audio-input:474` | figure | use | Project Settings ▸ Input Actions |
| `audio-input:476-477` | figure | use | The add-binding popup; binding by pressing a key |
| `audio-input:479` | figure | use | The Game view with a locked cursor |
| `audio-input:525` | rule | use | Gameplay reads rebindable controls as input actions |
| `audio-input:537` | rule | use | The game's cursor mode applies only while it has the input |
| `scripting:122` | feature | use | The SDK's `Input` |
| `scripting:483` | rule | use | Press and release edges read in `OnUpdate` |
| `scripting:487` | rule | use | Input actions for what a player might rebind |
| `editor-ui:208` | feature | use | Who gets the keys in play mode; Shift+F1 |
| `editor-ui:231` | feature | use | The Input Actions page and binding a key by pressing it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Writing positions and rotations from a script | `make/scripting-scene` | must |
| `OnUpdate`, `deltaTime`, and why what must happen once a frame goes in `OnUpdate` | `make/script-loop` | must |
| Project Settings and its pages | `make/project-files` | must |
| A direction as (x, y), scaled by a number | `make/transforms-units` | must |
| `if`, names in a namespace such as `Key::W`, and scoped enum values such as `CursorMode::Locked` | `basics/programming-1` | must |
| Functions, and static member functions called as `Input::IsKeyDown` | `basics/programming-2` | must |
| The Game view and keyboard focus | `make/editor-tour` | must |

**Starting state.** The end state of `make/scripting-scene` (`startsFrom {"tutorial": "make/scripting-scene"}`): coins
placed by `CoinPlacer` and collected by the distance test. The page ends with the ball moved by the Move action
(by writing its position) and the Gameplay map (Move, Jump, Boost, Look) saved in the project; step 8's camera script
and step 9's Vehicle map are left out of the checkpoint.

**Command-only steps.** none

## `make/physics` — Physics for game makers

**Covers.** The page makes Coin Run's ball roll by a force and turns the coins into triggers, and is the use home of
rigid bodies, colliders, triggers, contacts, queries, collision layers and the maker's half of tuning. The ideas from
zero first, each in a paragraph: what a physics engine does for a game (bodies that fall, collide and rest, stepped in
the fixed steps of `make/script-loop`); the body types with the choice figure (a collider alone is a static body,
Dynamic is simulated, Kinematic is moved by code and pushes others, a trigger reports overlaps and pushes nothing);
colliders are shapes, not meshes (Box, Sphere, Capsule, Mesh as convex or, on static bodies only, triangles); force,
mass, velocity and impulse at the use level (a velocity is a speed with a direction; a force changes the velocity a
little every step and less for a heavier body; an impulse changes it at once). The steps. (1) **Add Component ▸
RigidBody** on the ball (Dynamic, Mass 1) and Play from 3 m up: it falls onto the template's ground collider and rests;
the collider gizmos shown. Gravity is the scene's: with nothing selected, the Inspector's scene settings show the
Physics section with its summary ("Gravity 9.81 m/s² · 60 steps/s"), Gravity in m/s² (set there, or with
`scene.setSettings` in the command tab; changing it wakes every body), and a script cannot change it, only a body's
**Gravity Scale** (0 for a body that floats); Max Bodies and Max Contacts stay Auto at 0 and are set only for scenes
that create many bodies while they play. (2) Roll it: `BallControl` stops writing the position; it reads the Move action
in `OnUpdate` and pushes with `GetRigidBody().AddForce` in `OnFixedUpdate`, because forces act during the next step
only; a field for the strength; its speed read back with `GetLinearVelocity` and capped. (3) Tune the ball: friction,
restitution (a bounce needs more than 1 m/s), linear and angular damping so it slows, Continuous Collision named for
fast bodies. (4) A reset key: `Teleport` puts the ball back at the start, never a written transform, which takes effect
only at the next step and slides. (5) The coins as triggers: on the coin prefab a Sphere Collider and a RigidBody,
Kinematic with **Is Trigger** (they spin and bob, so they are moved by code), applied to the prefab; the `Coin` script's
`OnTriggerEnter` checks that the other entity is the ball and collects the coin, which replaces the distance test of
`make/scripting-scene`; triggers never see triangle-mesh colliders, so the coin keeps a sphere; `OnCollisionEnter` and
`OnCollisionExit` for bodies that touch, with the contact's point and normal (`make/sound` uses them). (6) Jump: a
raycast down from the ball with `Physics::Raycast` tells whether it is on the ground, and the Jump action of
`make/input` then gives it an impulse upward with `AddImpulse`, which changes the velocity at once; the press is read in
`OnUpdate`, because fixed updates run zero to N times a frame and a press read in `OnFixedUpdate` is missed or counted
twice (the rule, with `make/script-loop`'s root of it). (7) Collision layers: **File ▸ Project Settings ▸ Collision
Layers**, layers `Ball` and `Coin` named and a `Ghost` wall the ball passes through. The gotcha line of the step: the
wall needs a RigidBody of type Static, because a collider alone is a static body on layer 0 with the default material
(friction 0.5, restitution 0), and a RigidBody with no collider gets no body at all (it does not fall, and the Console
warns). The layers are the project's, not the scene's; a script turns the pair on and off with
`Physics::SetLayersCollide`, and the change holds until the scene ends or the project's table changes (an exercise opens
the gate when every coin is taken). (8) Measure and tune in a scratch scene that is not saved: a pile of balls, the
Streaming panel's Physics section ("awake N of M", the step's time), **Physics ▸ Simulation**'s Sleep Threshold changed
until the pile sleeps; `physics.stats` in the command tab. The gotchas in one list: spawn bodies apart (overlapping
bodies are pushed out at 3 m/s), `Instantiate` with a position gives scale 1, a moving dynamic body is never moved by
writing its transform. What Strata does not do here, each in a sentence or two: joints, ragdolls and vehicles (`new:6`);
height-field and cylinder colliders, where the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their
own mesh (`new:30`); cloth, soft bodies, destruction, fluids and buoyancy (`new:31`); stay events and a contact's
impulse or impact speed, so a script reads the bodies' velocities for a hit's strength (`new:32`); rolling resistance
and conveyor belts, so a rolling ball slows only through its damping (`new:33`). The exercises: a toppled stack of ten
crates with `AddImpulseAtPosition`, four balls of wood, metal, rubber and ice, whose pairs mix as box3d does by default
(friction the square root of the two frictions' product, restitution the larger of the two, so an ice ball slides on
wood and a rubber ball bounces on a floor of restitution 0), a trigger that counts balls and a launch pad (as the
Physics Playground's `GoalBasket` and `LaunchPad`), a gun that pushes what its ray hits. At the end the reader can
choose a body, push it the right way, react to triggers, cast rays, filter with layers and read the physics numbers; the
checkpoint has the rolling ball and the trigger coins.

**Leaves out.**

- Rigid bodies and colliders inside → `physics/bodies-colliders`
- How bodies are built from entities → `physics/building-bodies`
- Integration and Newton's laws → `physics/dynamics`, `basics/math-change`
- Collision detection → `physics/collision-detection`
- Collision layers inside → `physics/collision-layers`
- Contacts and triggers inside → `physics/contacts-triggers`
- Queries inside; why there are no shape sweeps → `physics/queries`
- Tuning inside: contact recycling, the solver → `physics/tuning`
- Character controllers → `make/characters-cameras`
- Balls shot through the cursor along a ray from the camera → `make/gameplay-math`
- Impact sounds → `make/sound`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `over`: about 7,000 words against L (5,000). A page of track B is at most L, so it splits by S3:
`make/physics`, "Physics for game makers" (the four ideas, steps 1 to 6, the gotchas, the absences, the crates, the four
balls and the trigger counter, about 5,650 words, L), then a how-to after it on tracks G and B, "Queries, collision
layers and tuning physics" (`RaycastAll` and the overlaps, steps 7 and 8, the gun and the ghost gate, about 2,400 words,
M). The new page keeps the use homes of collision layers and tuning on track B, and the Assumes rows that name
`make/physics` for collision layers would name it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:152` | feature | home | Bodies and colliders: the RigidBody's properties, the four collider shapes, a collider without a body is static |
| `gamedev:153` | feature | home | The script API: velocities, forces, impulses, `Teleport`; `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` with masks; contact callbacks |
| `gamedev:154` | feature | home | Collision layers: 32 project layers and their matrix; `Physics::SetLayersCollide` |
| `gamedev:155` | feature | home | Simulation tuning: the five fields, live while playing |
| `gamedev:70` | feature | home | Scene settings, step 1's Physics section with nothing selected: its summary, Gravity in m/s² (the scene's, set in the Inspector or with `scene.setSettings`; scripts set only a body's Gravity Scale), Max Bodies and Max Contacts at Auto 0, set only for scenes that create many bodies while they play; the fixed timestep and the steps per frame are used on `make/script-loop`. Evidence: `Strata/src/Strata/Scene/Scene.h:42-66`; `StrataEditor/src/Panels/InspectorPanel.cpp:256-266`, `:322-353`; `StrataEditor/src/Editor/EditorSceneCommands.cpp:569-579`; `git grep -ni gravity 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds only the character controller's GravityScale (`:542`) (read at the pin) |
| `gamedev:159` | feature | home | The gotchas: triggers and triangle meshes, overlapping spawns, `Instantiate`'s scale, bounces above 1 m/s |
| `gamedev:328` | concept | home | Rigid-body physics for makers; the mistakes (moving a dynamic body by its transform, triggers on triangle meshes, overlapping spawns) |
| `gamedev:418` | figure | home | The body choices: static, dynamic, kinematic, trigger, character controller; which shapes a trigger sees |
| `gamedev:488` | rule | home | Read presses in `OnUpdate`, apply forces in `OnFixedUpdate`: step 2's Move and step 6's Jump, with the press half of the mistake that `make/script-loop` roots (a press read in `OnFixedUpdate` is missed or counted twice) |
| `gamedev:492` | rule | home | Teleport with `Teleport`, not by writing a transform |
| `gamedev:501` | rule | home | Triggers do not see triangle-mesh colliders |
| `gamedev:502` | rule | home | Spawn bodies apart; `Instantiate` with a position sets scale 1 |
| `gamedev:503` | rule | home | Collision layers are the project's, not the scene's |
| `gamedev:621` | term | home | Rigid body (static, dynamic, kinematic) |
| `gamedev:622` | term | home | Collider (box, sphere, capsule, mesh; convex, triangle) |
| `gamedev:623` | term | home | Trigger |
| `gamedev:624` | term | home | Collision layer, layer matrix, mask |
| `gamedev:625` | term | home | Raycast and overlap |
| `gamedev:626` | term | home | Continuous collision |
| `gamedev:627` | term | home | Sleeping |
| `physics:445` | hands-on | home | Step 1: a body falling onto a floor that has only a collider |
| `physics:446` | hands-on | home | Exercise: ten crates toppled with `AddImpulseAtPosition` |
| `physics:447` | hands-on | home | Exercise: four balls of wood, metal, rubber and ice, predicted with box3d's default mixing of a pair (friction the square root of the product, restitution the larger value; the rule's home is `physics/bodies-colliders`). Evidence: `Strata/vendor/box3d/src/physics_world.c:155-165`, `:341-347`; `git grep -n -e frictionCallback -e restitutionCallback 822a7a46 -- Strata/src` finds nothing, so Strata keeps the defaults (run at the pin) |
| `physics:448` | hands-on | home | Exercise: a trigger that counts balls and a launch pad |
| `physics:449` | hands-on | home | Exercise: a gun that shoots with `Physics::Raycast` and pushes what it hits |
| `physics:451` | hands-on | home | Step 7 and its exercise: a Ghost layer switched at run time, on a wall with a Static RigidBody; the gotcha line: a collider alone is a static body on layer 0 with the default material, and a RigidBody with no collider gets no body and does not fall. Evidence: `Strata/src/Strata/Physics/PhysicsWorld.cpp:1997-2004` (the layer comes only from a RigidBody), `:2009-2010`, `:2017-2018` (the defaults without one), `:2503` (the warning); `Strata/src/Strata/Physics/PhysicsComponents.h:34-35` (friction 0.5, restitution 0) (read at the pin) |
| `physics:455` | hands-on | home | Step 8: the Sleep Threshold tuned on a pile of balls |
| `scene-ecs:603` | hands-on | home | Step 7: collision layers named and changed from a script during play; the change holds until the scene ends or the project's table changes (the scene's working copy against the project's table). Evidence: `Strata/src/Strata/Scene/Scene.h:647-648`, `:660-665` (read at the pin) |
| `new:6` | not-done | home | Joints, ragdolls and vehicles. Evidence: `git grep -n "b3Create.*Joint" 822a7a46 -- Strata/src` finds nothing (run at the pin); `Docs/Roadmap.md:1716-1718` |
| `new:30` | not-done | home | Height-field and cylinder colliders: Box, Sphere, Capsule and Mesh only; the Hierarchy's Cylinder, Cone and Torus get a convex mesh collider of their own mesh, a hull of at most 64 vertices, and the torus's hull fills its hole. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.h:44-68`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:65-69`, `:83-88`; `Strata/src/Strata/Physics/PhysicsMeshShapes.h:47-49`, `:57` (read at the pin) |
| `new:31` | not-done | home | Cloth, soft bodies, destruction, fluids and buoyancy. Evidence: `git grep -niE -e cloth -e "soft ?bod" -e fluid -e buoyan -e fractur -e destructible 822a7a46 -- Strata/src` finds nothing (run at the pin; the word "destruction" matches only the destruction of entities and objects) |
| `new:32` | not-done | home | Stay events, and the impulse or impact speed of a contact: contacts begin and end, and a script that needs a hit's strength reads the bodies' velocities. Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188` (a contact holds the other entity, a point and a normal); `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `new:33` | not-done | home | Rolling resistance and tangent velocity (conveyor belts) of box3d's surface material: a rolling ball slows only through its damping. Evidence: `git grep -n -e rollingResistance -e tangentVelocity 822a7a46 -- Strata/src` finds nothing (run at the pin); `Strata/vendor/box3d/include/box3d/types.h:417-431` |
| `physics:28-32` | feature | use | The RigidBody and the four collider components, as the Inspector shows them |
| `physics:34-35` | feature | use | The collider gizmos; how a body is made of an entity's colliders |
| `physics:41` | feature | use | Static, dynamic and kinematic bodies |
| `physics:46-50` | feature | use | Friction and restitution, mass, rotation locks, continuous collision, triggers as sensors |
| `physics:93-94` | feature | use | Forces act in the next step, impulses at once; `Teleport` |
| `physics:95` | feature | use | Step 1: gravity from the scene's settings, and a change of it wakes every body |
| `physics:107` | feature | use | The scripts' trigger and collision callbacks |
| `physics:114` | feature | use | `Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox` |
| `physics:122-123` | feature | use | Layers, the matrix and the project's section |
| `physics:125-126` | feature | use | Layers changed at run time; the Collision Layers page |
| `physics:146` | feature | use | The `Physics.Simulation` section's fields |
| `physics:172` | feature | use | `physics.stats` and the Streaming panel's Physics row |
| `physics:229` | concept | use | Body types, at the maker's level |
| `physics:233` | concept | use | Colliders and shapes, at the maker's level |
| `physics:255` | concept | use | Sleeping, at the maker's level |
| `physics:261` | concept | use | Triggers, at the maker's level |
| `physics:265` | concept | use | Spatial queries, at the maker's level |
| `physics:369` | figure | use | Collider gizmos shown in the editor |
| `physics:371-372` | figure | use | The RigidBody's Inspector; the Collision Layers page |
| `physics:374-375` | figure | use | The Simulation page; the Streaming panel's Physics row |
| `physics:392` | rule | use | Use `Teleport` for instant moves |
| `physics:394` | rule | use | Apply forces in `OnFixedUpdate`, every step they should act |
| `physics:406` | rule | use | Do not spawn bodies overlapping |
| `physics:408` | rule | use | Triangle meshes only on static bodies; triggers do not see them |
| `physics:433` | rule | use | Restitution needs more than 1 m/s to bounce |
| `scripting:125` | feature | use | The SDK's `RigidBody`, `Physics`, `RaycastHit` and `Collision` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Move action and reading it in `OnUpdate` | `make/input` | must |
| `OnFixedUpdate` and the fixed step | `make/script-loop` | must |
| Components, colliders on the presets, the prefab and Apply | `make/prefabs` | must |
| Writing transforms and finding entities from a script | `make/scripting-scene` | must |
| Project Settings and its pages | `make/project-files` | must |
| A direction as three numbers, scaled | `make/transforms-units` | must |
| Rates, accumulation and Newton's laws as mathematics | `basics/math-change` | helps |

**Starting state.** The end state of `make/input` (`startsFrom {"tutorial": "make/input"}`): the ball moved by the
Move action through its position, the coins placed by `CoinPlacer`, the Jump action defined. Step 8's pile of balls is
built in the scratch scene `Scenes/Test.stscene` and not saved. The page ends with the ball rolling by a force and
jumping, and the coins collected as triggers.

**Command-only steps.** none

## `make/sound` — Sound

**Covers.** The page gives Coin Run its coin sound and teaches sound at the maker's level. The ideas from zero, in
short paragraphs: a sound file becomes a clip; an Audio Source plays a clip from an entity, with a volume, a pitch, a
loop and a 3D switch; a listener is the ears (Basic 3D's Main Camera has one); a 3D source gets quieter with distance
and moves from ear to ear; a one-shot is a sound fired once and forgotten. The steps. (1) Import
`Samples/ThirdPerson/Assets/Sounds/Coin.ogg` (Kenney, CC0) and play it in the Asset tab's waveform preview. (2) A first
sound: **+ ▸ Audio Source**, its clip, **Play On Start**, then Volume, Pitch and Loop; it plays only in Play mode;
changing a source's **Clip**, in the Inspector or from a script, stops it and drops a Play that had not started yet,
and Play then starts the new clip. (3)
Hear space: the source made spatial and moved while the game plays; Min and Max distance and the rolloff; the listener
moved from the camera to the ball. (4) The coin's sound: the `Coin` script asks for the clip with `Assets::RequestLoad`
in `OnCreate` and plays it with `Audio::PlayOneShotAt` where the coin is collected; the rule in a `:::rule` aside:
request a clip before it is needed, because a one-shot whose clip is not loaded within 0.25 s is dropped with a warning
in the Console, shown by a step that skips the request. (5) Impact sounds: the ball's `OnCollisionEnter` plays a bump
(`Samples/PhysicsPlayground/Assets/Sounds/Impacts/Soft.ogg`, credited in that sample) louder for a harder hit, the
speed taken from the two bodies' velocities along the contact's normal as the Physics Playground's `Impact.cpp` does,
given as a recipe. (6) Music and a volume option: a looping music source, not spatial, its clip **Streamed** (decoded
while it plays) against **Decompressed**; `Audio::SetMasterVolume` from two keys, and the editor restoring its volume at
Stop; the music file comes from the book's tutorial assets with its credit. A Streamed clip holds its encoded bytes in
memory and decodes them while it plays: nothing streams from the disk or a pack (`new:37`). (7) Save. What Strata does
not do here, each in a sentence or two: buses, effects, reverb and HRTF (`new:7`); music systems and ducking
(`new:8`); stay events and a contact's impulse, which is why step 5 reads the velocities (`new:34`); occlusion and
reverb zones (`new:35`); virtual voices and voice priorities (`new:36`); streaming from disk or packs (`new:37`);
listeners per world (`new:38`). At the end the reader can place sounds in space, fire one-shots that never drop, scale
them by impact and set the game's volume.

**Leaves out.**

- Sound inside a computer: samples, channels, decibels, the pull model → `audio/sound-in-a-computer`
- Clips, voices, sources and load modes inside → `audio/clips-voices-sources`
- Panning, attenuation and Doppler inside → `audio/spatial`
- The audio engine and the scene system → `audio/engine`, `audio/scene-system`
- Residency and pins inside → `assets/residency`
- A volume slider in a settings screen → `make/menus`
- Footsteps from animation events → `make/animation`
- A budget of voices for many impacts → `make/recipes`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,700 words against M (3,000). Seven steps take most of it, with the sound ideas from zero in
short paragraphs, two code excerpts (the coin's one-shot, the impact), the rule, the seven absences, three pictures and
the exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:178` | feature | home | `AudioSource` and `AudioListener`; the scripts' `AudioSource` and `Audio`; early requests; the waveform preview; `audio.state` in a command tab |
| `gamedev:337` | concept | home | Audio for makers: sources, the listener, 3D attenuation, one-shots, loading before use; the dropped one-shot |
| `gamedev:636` | term | home | Audio source, listener, one-shot |
| `audio-input:552` | hands-on | home | Steps 1 and 2: a first sound |
| `audio-input:554` | hands-on | home | Step 3: hearing space |
| `audio-input:556` | hands-on | home | Step 5: impact sounds |
| `audio-input:561` | hands-on | home | Step 6: music and a volume option |
| `physics:454` | hands-on | home | Step 5's loudness from the hit, as `Impact.cpp` computes it |
| `new:7` | not-done | home | Buses, effects, reverb and HRTF: a voice sets only its own output volume. Evidence: `git grep -niE "ma_sound_group\|reverb\|hrtf\|filter_node" 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin); `Strata/src/Strata/Audio/AudioVoice.cpp:308` |
| `new:8` | not-done | home | Music systems and ducking. Evidence: `git grep -niE "music\|duck" 822a7a46 -- Strata/src/Strata/Audio` finds only comments that name music as a use of streamed or 2D clips (`AudioClip.h:19`, `AudioEngine.h:85`, `AudioSource.h:33`; run at the pin) |
| `new:34` | not-done | home | Stay events, and the impulse or impact speed of a contact: contacts begin and end, and the impact sound of step 5 reads the bodies' velocities. Evidence: `Strata/src/Strata/Scene/SceneServices.h:41-45`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:181-188`; `git grep -n enableHitEvents 822a7a46 -- Strata/src` finds nothing (run at the pin); `Samples/PhysicsPlayground/Scripts/Impact.cpp:53-55` |
| `new:35` | not-done | home | Occlusion and reverb zones. Evidence: `git grep -ni -e occlu -e reverb -e zone 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin) |
| `new:36` | not-done | home | Virtual voices and voice priorities. Evidence: `git grep -ni -e virtual -e priorit 822a7a46 -- Strata/src/Strata/Audio` finds nothing (run at the pin) |
| `new:37` | not-done | home | Streaming from disk or packs: a Streamed clip holds its encoded bytes in memory and decodes them while it plays. Evidence: `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1712` (read at the pin) |
| `new:38` | not-done | home | Listeners per world: the audio engine has one listener. Evidence: `Docs/Roadmap.md:1707`; `Strata/src/Strata/Audio/AudioSystem.h:84-86` (read at the pin) |
| `audio-input:30` | feature | use | The master volume |
| `audio-input:33` | feature | use | The listener |
| `audio-input:46` | feature | use | Load modes: Decompressed and Streamed |
| `audio-input:76` | feature | use | Clips that load in the background |
| `audio-input:77` | feature | use | Step 2: plain writes apply, and a changed clip stops the source and drops its pending Play; Play starts the new clip. Evidence: `Strata/src/Strata/Audio/AudioSystem.cpp:538-546` (`ResolveClip`); `Strata/src/Strata/Audio/AudioSystem.h:75-77` (read at the pin) |
| `audio-input:80` | feature | use | Which listener is used |
| `audio-input:84` | feature | use | One-shots in a scene |
| `audio-input:94` | feature | use | The SDK's `AudioSource` |
| `audio-input:261` | concept | use | 3D sound, at the maker's level |
| `audio-input:469` | figure | use | The Inspector of an Audio Source |
| `audio-input:471` | figure | use | The Asset tab's audio preview |
| `audio-input:481` | figure | use | The Console's warning of a dropped one-shot |
| `audio-input:505` | rule | use | Request clips before you need them |
| `scripting:127` | feature | use | The SDK's `AudioSource` and `Audio` |
| `scripting:481` | rule | use | Request assets early |
| `assets:624` | hands-on | use | Keep a sound loaded, as an exercise |
| `physics:107` | feature | use | `OnCollisionEnter` for the impact |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Collisions, triggers and the coin's `OnTriggerEnter` | `make/physics` | must |
| Requesting assets early; `Assets::RequestLoad` | `make/scripting-scene` | must |
| Importing a file and the Asset tab | `make/assets` | must |
| A sum of products along a direction, given as a recipe | `basics/math-vectors` | helps |

**Starting state.** The end state of `make/physics` (`startsFrom {"tutorial": "make/physics"}`): the rolling ball and
the trigger coins. The sounds come from the release's `Samples/ThirdPerson/Assets/Sounds/` and
`Samples/PhysicsPlayground/Assets/Sounds/Impacts/`, the music from `tutorials/assets/` with its credit. The page ends
with the coin sound, the bump and the music.

**Command-only steps.** none

## `make/hud` — HUDs: text, score and bars

**Covers.** The page gives Coin Run its coin count and timer on the screen, and teaches the game's UI at the maker's
level. The ideas from zero, in short paragraphs with the anchoring figure: a canvas is the root of a UI drawn over the
screen (or placed in the world); it scales with the screen from a reference resolution, so the HUD keeps its look on
any window; every element is a rect with anchors (where it attaches to its parent), a pivot and a size; text and
images are elements on rects. The steps. (1) **+ ▸ UI ▸ Canvas**: Screen Space, **Scale With Screen** at 1920 x 1080.
(2) The viewport's **2D** chip and the **Game UI** chip: the canvas drawn flat at its reference aspect, with handles to
drag rects. (3) **+ ▸ UI ▸ Text** for the coin count, anchored to the top-left corner with the anchor presets, a font
size and a left alignment, because a UIText is centred by default and a centred count is cut at the edge. (4) A second
text for the timer anchored top-right. (5) A panel behind them (**+ ▸ UI ▸ Panel**) with a sliced image, so its corners
keep their size as it stretches. Then one paragraph: an image is hit by the pointer by default, so the panel would take
the game's mouse clicks in its corner; the HUD's canvas turns **Receives Input** off, which keeps it drawn but never hit
or navigated (the menus' canvases of `make/menus` keep it on). (6) A bar along the bottom for the time left, stretched
between two anchors: an image of type **Filled**, whose **Fill Amount** (0 to 1) shows the part left; along a stretched
axis **Size** is added to the span between the anchors, so Size 0 fills it and a negative Size leaves margins. (7) The
script: a `CoinHud` script finds the texts and writes `GetUI().SetText` with the count of coins left (it counts the
entities tagged `Coin`) and the time from `Time`, every frame, which costs nothing while a text stays the same
(`new:49`); it sets the bar with `SetProperty("UIImage", "FillAmount", ...)`, never `SetValue`, which moves only a
slider or a toggle, and changes colors with `SetColor` when time runs low. (8) Check every screen: the Game
view's resolution menu at 16:9, 4:3 and 21:9; the corner texts stay in their corners and the bar stretches. (9) Text
without a canvas: a `TextComponent` (**+ ▸ 3D Text**) floating over the start, in the world and facing the camera, and
why a HUD is never built from screen-space text: it does not scale with the screen. The exercises (`new:39`) are done
in the editor and in a script. At the end the reader can lay out a HUD that survives every screen and drive it from a
script; buttons, focus and menus are `make/menus`'.

**Leaves out.**

- What a game UI must do; retained against immediate UIs → `ui/what-game-ui-does`
- Rects, anchors and layout inside → `ui/layout`
- Text in game UI inside: shaping, overflow → `ui/text`
- Fonts, the glyph atlas and signed distance fields → `gpu/text`
- How the UI is drawn → `ui/drawing`
- Buttons, toggles, sliders that take input, focus and navigation, menus → `make/menus`
- UI events and the UI action map → `make/menus`
- Testing a UI through commands → `make/automated-playtests`

**Fit.** `over`: about 4,050 words against M (3,000). Nine steps at B0's length, canvases and anchors taught from zero
with the anchoring figure, the script, the two HUD mistakes, three pictures and two exercises take it over M's top. L
(5,000) by S2; no split, because steps 1 to 9 build and check one layout.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:339` | concept | home | UI for makers: canvas scaling, anchors and pivots, nine-slice; the HUD mistakes (screen-space text, the centred default) |
| `gamedev:424` | figure | home | UI anchoring: a corner count, a stretched bar and a centred panel at two resolutions |
| `gamedev:456` | figure | home | The viewport's 2D canvas mode with the Game UI chip on |
| `gamedev:509` | rule | home | Do not build HUDs from screen-space `Text`; use a UI canvas |
| `gamedev:510` | rule | home | UIText alignment defaults to Center |
| `gamedev:637` | term | home | Canvas (screen space, world space) |
| `gamedev:638` | term | home | Reference resolution and scale mode |
| `gamedev:639` | term | home | Rect, anchor, pivot |
| `gamedev:640` | term | home | Nine-slice (sliced image) |
| `gameui:215` | feature | home | The presets of **+ ▸ UI**: Canvas, Panel, Image, Text and the widgets, as a maker makes them |
| `gameui:480` | figure | home | A score anchored top-right and a bar stretched along the bottom at two aspect ratios |
| `gameui:574` | hands-on | home | Step 8: a HUD checked at three screens. The item's health bar "driven by SetValue/FillAmount" is set with `SetProperty("UIImage", "FillAmount", ...)`, never `SetValue`, which fails on an image. Evidence: `StrataScriptCore/Include/StrataScript/UI.h:113-119` (`SetValue`: a slider or a toggle only) (read at the pin) |
| `new:49` | feature | home | Step 7: setting a text to what it already shows costs nothing, so a HUD may set its texts every frame: `SetText` changes the component only when the text differs. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:988-990`; `StrataScriptCore/Include/StrataScript/UI.h:54` (read at the pin) |
| `render-core:665` | hands-on | home | Step 9: world and screen text with `TextComponent`; the use home of text without a canvas |
| `scripting:513` | hands-on | home | Pickup and score, ending in the HUD's coin count (the trigger and the sound came on the two pages before) |
| `new:39` | hands-on | home | Exercises: **Basic.** move the timer to the top centre with the anchor presets and check it at 4:3 and 21:9 in the Game view's resolution menu; **Medium.** a second Filled bar that shows the part of the coins collected, its `FillAmount` set from the script with `SetProperty("UIImage", "FillAmount", ...)`, with a prediction of its value after two of five coins. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:94`, `:115` (Filled and `FillAmount`, 0 to 1) |
| `gameui:53-58` | feature | use | The canvas, its scale and render modes, the rect, the image and the text components; step 5's paragraph: an image is a raycast target by default, so the HUD's canvas turns **Receives Input** off (drawn, never hit or navigated). Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:60`, `:121`; `Docs/Manual/GameUI.md:57-58` (read at the pin) |
| `gameui:77` | feature | use | The scale per screen and the size in canvas units |
| `gameui:100` | feature | use | Anchor, pivot, position and size, at the maker's level; step 6: along a stretched axis Size is added to the span, so 0 fills it and a negative Size leaves margins. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:74-78`, `:85` (read at the pin) |
| `gameui:118` | feature | use | Wrapping and overflow from the rect |
| `render-core:536` | figure | use | Text in the world and on the screen |
| `scripting:131` | feature | use | The SDK's `UIElement`: text, image and color; a slider's value named for `make/menus` |
| `editor-ui:155` | feature | use | The canvas mode inside the Scene view |
| `editor-ui:569` | figure | use | Canvas mode on a UI canvas |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Finding entities and counting the coins left from a script | `make/scripting-scene` | must |
| `Time` and `OnUpdate` | `make/script-loop` | must |
| The Game view's resolution menu | `make/editor-tour` | must |
| `std::string` and numbers turned into text | `basics/programming-2` | must |
| Importing a font or an image | `make/assets` | helps |

**Starting state.** The end state of `make/sound` (`startsFrom {"tutorial": "make/sound"}`): the rolling ball, trigger
coins with their sound, the bump and the music. The sliced image of step 5 comes from the release's
`Samples/ThirdPerson/Assets/UI/` (Kenney's UI Pack, CC0, credited in that sample). The page ends with the coin count,
the timer and the time bar on the screen.

**Command-only steps.** none

## `make/play-test-debug` — Playing, testing and debugging

**Covers.** The goal: play Coin Run on purpose, freeze it, step it, change it while it runs, and find a bug in one of
its scripts. What must be true first: Coin Run at the end of `make/hud`, and the debugger that `basics/debugging`
attached to the editor. The steps. (1) **Play** and **Stop** again, with the figure of the running copy: Play runs a
copy of the edited scene and Stop throws the copy away, which is why the coins come back. (2) **Simulate**: physics
without the game's scripts, for trying bodies without playing; the sentence on what else Simulate leaves out (no
sound, no animation, characters in their bind pose) waits for the check of `new:40`. (3) **Pause** and **Step**: Pause
freezes the game; Step runs one fixed update, and the status bar counts the steps; a coin's turn per step read in the
Inspector. (4) Edits while playing: drag the ball in the Scene view and change a script's field; they change the running
copy and are gone at Stop, while a change in Project Settings applies at once and stays. (5) Watch values: the Inspector
shows a script's fields live while the game plays. (6) The editor's feedback and the log: the status bar's pills and the
toasts each lead to the panel that explains (a failed build to Problems, a warning to the Console); `Log::Info`, `Warn`
and `Error` lines in the Console with their file and line, and the editor's log file in the user's data folder; the
exported game writes its own `Game.log`, which `make/export`'s run reads. If you do not see the lines of a run that
crashed: every start empties the program's log file, and every editor of the user writes the same `StrataEditor.log`, so
read or copy the log before starting the editor again. (7) The debugger: a breakpoint in the `Coin` script's
`OnTriggerEnter`, roll into a coin, step and read the call stack, as `basics/debugging` taught; the Linux and macOS tabs
say what the pin does: a Release or Dist editor builds scripts with GCC or Clang without debug information, so the
breakpoint very likely does not bind, and the log and the Inspector stand in; the page says in one sentence that this
was read from the build files, not run (`new:41`, `new:42`). (8) A planted bug in the tutorial's file (the HUD counts a
coin that was destroyed in the same frame) found with the breakpoint and the rule of `make/script-loop` that destruction
happens at the end of the frame, and fixed. (9) "Same inputs, same game": the game counts time in fixed steps and every
body moves the same way for the same steps, so a bug seen after 200 steps is seen again; Pause and Step reproduce it,
and play-tests by command are `make/automated-playtests`'. `## Result`: Coin Run free of the bug, and a way to stop and
look at any moment of a game; it ends with the download of the page's end state. `## Variations`: the debugger of each
system (Visual Studio, VS Code, lldb) in OS tabs; Simulate for tuning physics. What Strata does not do here: no debug
drawing from scripts (`new:9`), no in-game console or console variables (`new:10`), no debug information in the script
modules that a released editor builds with GCC or Clang (`new:42`); the log and the Inspector stand in for them. The
exercises (`new:43`) are done in the editor and in a script.

**Leaves out.**

- The running copy, the game shell and edits while playing inside → `editor/play-mode`
- Pausing and stepping inside; holds counted in fixed steps → `editor/stepping`
- A debugger, breakpoints and the call stack from zero → `basics/debugging`
- Simulated input, command scripts and captures → `make/automated-playtests`
- Measuring the frame → `make/performance`
- Deterministic parallel work inside → `core/jobs`
- The Game view's resolutions and input ownership inside → `editor-ui/game-view`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,450 words against M (3,000). Nine steps take most of it, with the Linux and macOS tabs of the
debugger, the paragraph on determinism, the figure of the running copy, two pictures, the three absences and two
exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:222` | feature | home | Play, Simulate, Stop, Pause and Step; the toolbar's play color |
| `gamedev:223` | feature | home | Edits while playing go to the running copy; project settings apply live and stay |
| `gamedev:408` | figure | home | The running copy: the edited scene copied at Play, thrown away at Stop |
| `gamedev:596` | term | home | Play, Simulate, Pause, Step |
| `editor-core:611` | hands-on | home | Steps 1 to 3: play, pause, step on Coin Run |
| `editor-ui:692` | hands-on | home | Step 6's feedback: a failed build followed from its pill and toast to Problems, as `make/first-script` first did; the Activity panel's Undo to here and Copy as script are named for `make/with-an-agent` |
| `foundation:542` | hands-on | home | Step 6: the log files, the editor's now and the exported game's `Game.log` with a script's warning after `make/export`; its "If you do not see it": every start empties the log file and every editor of the user writes the same `StrataEditor.log`, so the log of a crashed run is read or copied before the editor starts again. Evidence: `Strata/src/Strata/Core/Log.cpp:224` (the file sink truncates); `StrataEditor/src/EditorApplication.cpp:283-287`; `StrataRuntime/src/RuntimeApplication.cpp:458` (read at the pin) |
| `new:9` | not-done | home | Debug drawing from scripts. Evidence: `git grep -niE "DebugDraw\|DrawLine\|DrawDebug\|Gizmo" 822a7a46 -- StrataScriptCore/Include/StrataScript` finds nothing (run at the pin) |
| `new:40` | open | home | Check: Simulate and skinned meshes. In Simulate the running copy has no scripts, no sound and no Animation system, and the editor's animation preview serves only the edited scene, so skinned characters draw in their bind pose (read from the code, not run; the photographer's capture in the pin's editor settles it, and the page's sentence on Simulate replaces this item). Evidence: `Strata/src/Strata/Scene/SceneSystem.h:23`; `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-35`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:2697-2704`; `StrataEditor/src/Editor/EditorContext.h:313`, `:823`; `Strata/src/Strata/Renderer/RenderScene.cpp:1286`, `:1374-1384` |
| `new:41` | open | home | Check: Script breakpoints on Linux and macOS. A breakpoint in a script very likely does not bind on Linux and macOS with a Release or Dist editor, because script modules built with GCC or Clang get no `-g` there (read from the build files, not run; the page is written from the code and says so in one sentence). Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133` (a program database for MSVC only); `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52` (Dist takes Release's flags); `StrataEditor/src/Editor/ScriptBuild.cpp:402` (scripts are built in the editor's own configuration) |
| `new:42` | not-done | home | Debug information in script modules that a Release or Dist editor builds with GCC or Clang: only MSVC builds get it in every configuration, and the editor builds scripts in its own configuration, whose Release and Dist flags hold no `-g`. Evidence: `StrataScriptCore/CMake/StrataScriptModule.cmake:110-133`; `StrataScriptCore/CMake/StrataScriptCoreConfig.cmake:37-52`; `StrataEditor/src/Editor/ScriptBuild.cpp:402` (read at the pin, not run; the check is `new:41`) |
| `new:43` | hands-on | home | Exercises: **Basic.** in Simulate, drop the ball from 3 m and predict whether the coins spin and bob (they do not: Simulate runs no scripts); **Medium.** log the ball's height with `Log::Info` in an `OnFixedUpdate`, Pause, Step ten times, and match the ten new lines of the Console with the steps the status bar counts. Evidence: `Strata/src/Strata/Scene/SceneSystem.h:23` (Simulate: physics only, no scripts or audio); `StrataEditor/src/Editor/Commands/PlayCommands.cpp:191-196` (`play.step`: fixed steps while paused) |
| `new:10` | not-done | home | In-game consoles and console variables. Evidence: `git grep -niE "cvar\|console ?variable\|ConsoleVariable" 822a7a46 -- Strata/src StrataRuntime/src StrataScriptCore` finds nothing (run at the pin) |
| `editor-core:217` | feature | use | Play, the running copy and Stop |
| `editor-core:219` | feature | use | Edits while playing |
| `editor-core:222-224` | feature | use | Pause and step; `play.start` and `play.step` in the command tabs |
| `editor-core:347` | concept | use | Play-in-editor, at the maker's level |
| `editor-core:352` | concept | use | Fixed steps, pausing and stepping, at the maker's level |
| `editor-core:494` | figure | use | The play mode state machine, simplified |
| `editor-core:530` | figure | use | A paused game after steps, with the step count |
| `editor-core:573` | rule | use | Edits while playing are not recorded and go at Stop |
| `editor-core:688` | term | use | Running copy |
| `editor-core:693` | term | use | Stepping |
| `editor-ui:189` | feature | use | Script fields shown live while playing |
| `editor-ui:689` | hands-on | home | Play, the Game view's resolutions, Pause and Step, Shift+F1 and the Game camera (F8), as steps 1 to 4 |
| `scene-ecs:109` | feature | use | Pause and steps, the game's own time base |
| `scene-ecs:643` | term | use | Simulate mode |
| `scripting:124` | feature | use | `Log` |
| `physics:149` | feature | use | Physics gives the same results for the same steps |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A debugger attached to the editor: breakpoints, stepping, the call stack | `basics/debugging` | must |
| The fixed step and destruction at the end of the frame | `make/script-loop` | must |
| The HUD's count and the `Coin` script's trigger | `make/hud` | must |
| The Console and `Log::Info` | `make/first-script` | must |
| Edits through the Inspector and the gizmo | `make/scenes-entities` | must |

**Starting state.** The end state of `make/hud` (`startsFrom {"tutorial": "make/hud"}`), with the bug of step 8
planted by the tutorial's file in `CoinHud`. The page ends with the bug fixed; `make/export` starts there.

**Command-only steps.** none

## `make/export` — Exporting and shipping

**Covers.** The page exports Coin Run and runs it as a player would, and is the use home of the export. The idea
first, in one paragraph and the export figure: an export writes a folder that plays without the editor: the runtime
renamed after the game, the game's manifest (`.stgame`), one pack of its assets (`.stpak`) in the order the game first
uses them, the script module, the icon and, on Linux, a desktop entry. The steps. (1) The game's identity on **File ▸
Project Settings ▸ Game**: title, version, company, copyright and an icon (an image from the book's tutorial assets);
a script cannot read the title or the version (`new:44`); the start scene is `Scenes/Main.stscene` since Basic 3D set
it (**File ▸ Set as Start Scene**), and a loading scene is named in one sentence, with `make/levels-saves`, which
teaches it. (2) **File ▸ Export Game...**: a folder outside the project; the stages in the progress bar
(waiting for imports, cooking worlds, packing, copying) and **Open Folder** at the end. (3) The export refuses when a
build is running, when the scripts are not built or changed since they were loaded, or when the folder is inside the
project: one refusal shown by exporting while a build runs. (4) The folder in the file browser: each file named, and
the shipped `ThirdPartyNotices.md`. (5) Run the game by double-clicking it, with what each system asks first (tabs per
OS: Windows SmartScreen's **More info ▸ Run anyway** for an unsigned program; macOS's quarantine removed with `xattr
-dr com.apple.quarantine <folder>` in the terminal; on Linux the `.desktop` file copied into the hidden folder
`~/.local/share/applications` to list the game, with a caution: the export writes the entry but does not install it,
and the entry names the export folder's absolute paths, so a moved or shipped folder needs its `Exec` and `Icon`
lines edited). (6) Run it from the terminal with options: `--windowed`,
`--resolution 1280x720`, `--seconds 10 --screenshot shot.png`, `--headless --frames 600`, `--quality low` and `--help`,
with the exit codes (on Windows the output piped to `Write-Output` so PowerShell waits). (7) The game's log and save
folders in the player's data folder, named after the game; `Game.log` read for a script's warning. (8) A pruned
export: tick **Prune** and run it: no coins appear, because `CoinPlacer` loads the coin prefab and the `Coin` script its
sound by path, and a pruned pack keeps only what the scenes use; add them under **Project Settings ▸ Export ▸ Always
Include** and export again. (9) What the exported game does differently: no hot reload, scripts switched off after a
crash, project settings and graphics options as the game reads them. "Giving your game to players": a credits screen
built from `CREDITS.md`, the notices file kept beside the game, one sentence that an exported streamed world waits
for its ground, which `make/large-worlds` checks, and one sentence on the processor: on Windows and Linux on x86-64 the
game needs a processor with AVX2, and nothing checks it at start, so an older processor stops without a message
(`new:46`). What Strata does not do here: exports for another platform, macOS app bundles, signed exports, crash
reports from shipped games (`new:11`); a tool that writes patch packs (`new:45`); a check at startup for AVX2
(`new:46`). The exercises (`new:47`) run the exported game from the terminal. At the end the reader has Coin Run as a
folder that plays without the editor, and knows what to check before giving it away.

**Leaves out.**

- The export as a whole inside: `GameExport`, its states, its checks → `worlds/export`
- The pack: format, planning, pruning → `assets/packs-export`
- The manifest and the game's identity inside → `worlds/game-identity`
- The runtime, its options and exit codes inside → `worlds/runtime`
- The Export dialog's drawing → `editor-ui/launcher-dialogs`
- Measuring a shipped run with `--perf-log` → `make/performance`
- Players' graphics options → `make/quality`
- A loading scene with a progress bar → `make/levels-saves`
- Exported streamed worlds → `make/large-worlds`
- The terminal, paths and exit codes → `basics/tools`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `over`: about 4,250 words against M (3,000). Nine steps, three of them with OS tabs, the runtime's options and
exit codes, the export taught from zero with its figure, "Giving your game to players", four pictures, the three
absences and two exercises take it over M's top. L (5,000) by S2: shrinking step 6's options to a table would cut
content (S4).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:206` | feature | home | The game's identity: title, version, company, copyright, icon; stamped into the Windows program, the macOS Dock icon, the Linux entry |
| `gamedev:236` | feature | home | **File ▸ Export Game...**: its stages, what the folder holds |
| `gamedev:237` | feature | home | Pruned exports and **Always Include** |
| `gamedev:238` | feature | home | The export's refusals |
| `gamedev:239` | feature | home | The runtime's options and exit codes |
| `gamedev:240` | feature | home | What `GameRuntime` does differently from the editor |
| `gamedev:348` | concept | home | Shipping: what an export holds, pruning and assets loaded by path, identity, unsigned programs; the mistake of a pruned export that misses what scripts load |
| `gamedev:429` | figure | home | The export's stages and the folder it writes, pruned against full |
| `gamedev:454` | figure | home | The Export dialog with its progress; the exported folder with the icon |
| `gamedev:475` | figure | home | Coin Run running in a window with its title in the bar |
| `gamedev:511` | rule | home | Pruned exports drop assets loaded by path; list them under Always Include |
| `gamedev:512` | rule | home | The export refuses while a build runs, when the module changed since load, or when scripts are unbuilt |
| `gamedev:577` | term | home | Start scene and loading scene: the start scene's entry is taught here; the loading scene's entry is `make/levels-saves`', which teaches it (`gamedev:202`), and the glossary step splits the two |
| `gamedev:651` | term | home | Export, pruned export, always include |
| `gamedev:652` | term | home | Manifest (`.stgame`) and pack (`.stpak`) |
| `gamedev:653` | term | home | Headless |
| `gamedev:654` | term | home | Game identity |
| `new:11` | not-done | home | Exports for another platform, macOS app bundles, signed exports, crash reports in shipped games: the export copies the runtime next to the editor. Evidence: `Docs/Releases/0.7.0.md:411-412`; `StrataEditor/src/Editor/GameExport.h:30`; `Docs/Roadmap.md:1684-1685` (run at the pin) |
| `new:12` | erratum | home | `.claude/skills/strata-make-a-game/SKILL.md:470`, which `make/project-coin-run` reads, says an exported game has no `--help` and ignores unknown arguments; at the pin it prints its usage for `--help` or `-h` and exits 0, and a command line it does not understand prints the problem and the usage and ends with the usage exit code (3). The page states the code's facts; `process.md`'s table of errata holds the row. Evidence: `StrataRuntime/src/RuntimeApplication.cpp:354`, `:372-375`, `:409`, `:429-440`; `Strata/src/Strata/Core/CommandLineOptions.h:27` (`c_UsageExitCode = 3`) (read at the pin) |
| `new:44` | not-done | home | Reading the game's title or version from a script. Evidence: `Docs/Releases/0.7.0.md:363`; `git grep -ni -e title -e gameinfo 822a7a46 -- StrataScriptCore` finds only the graphics options' `Title` (`StrataScriptCore/Include/StrataScript/Graphics.h:46`, `:125`; `ScriptABI.h:289`, `:299`) (run at the pin) |
| `new:45` | not-done | home | A tool that writes patch packs: the export writes none, and a patch is a pack written from code and named in the manifest's `PatchPacks` by hand. Evidence: `git grep -n PatchPacks 822a7a46 -- StrataEditor StrataCLI Tools` finds nothing (run at the pin); `Strata/src/Strata/Project/GameManifest.h:26`, `:51-53` |
| `new:46` | not-done | home | A check at startup for the processor's AVX2: the release builds compile every engine object for AVX2 on x86-64, so an older processor stops at an illegal instruction without a message; the one sentence of "Giving your game to players" says what processor the game needs (critic-build-test-5). Evidence: `CMake/StrataCompilerOptions.cmake:30`, `:50-51`, `:61-62`; the only processor check in `Strata/src` is `Strata/src/Strata/Core/Hash.cpp:109-119` (SSE 4.2, for CRC32; `git grep -ni cpuid 822a7a46 -- Strata/src StrataRuntime/src StrataEditor/src` finds only that file) (run at the pin) |
| `new:47` | hands-on | home | Exercises, run from the terminal: **Basic.** run the exported game with `--windowed --resolution 800x600 --seconds 5 --screenshot shot.png` and open the picture; **Medium.** predict the exit code of the game run with an option it does not know (`--speed 2`) and with `--help`, then run both and read the code (`$?`, or `$LASTEXITCODE` in PowerShell). Evidence: `StrataRuntime/src/RuntimeApplication.cpp:354`, `:409`, `:429-440`; `Strata/src/Strata/Core/CommandLineOptions.h:27` (`c_UsageExitCode = 3`) |
| `build-test:601` | hands-on | home | Step 6: the exported game checked headless (`--headless --frames`), with a windowed `--screenshot`; `--perf-log` named for `make/performance` |
| `worlds-runtime:125` | feature | use | The runtime's options, at the maker's level |
| `worlds-runtime:146` | feature | use | The `.stgame` manifest |
| `worlds-runtime:149` | feature | use | The save and log folders named after the game |
| `worlds-runtime:155-156` | feature | use | The export and its checks before it starts |
| `worlds-runtime:159-160` | feature | use | The asset pack and pruning |
| `worlds-runtime:162-166` | feature | use | The script module, the icon, the Windows version resources, the Linux entry, the macOS Dock icon; step 5's Linux caution: the export does not install the entry, and the entry names the folder's absolute paths. Evidence: `StrataEditor/src/Editor/DesktopEntry.h:11-13`, `:20-21`; `StrataEditor/src/Editor/GameExport.cpp:714-720` (read at the pin) |
| `worlds-runtime:168` | feature | use | The Export dialog |
| `worlds-runtime:292` | concept | use | Game identity and the platforms, at the maker's level |
| `worlds-runtime:374` | figure | use | The exported game's folder |
| `worlds-runtime:400-401` | figure | use | The Export dialog before, during and after; the folder in the file browser |
| `worlds-runtime:407` | figure | use | Project Settings ▸ Game |
| `worlds-runtime:448` | rule | use | Saves are keyed by the manifest's name, not the title |
| `worlds-runtime:479` | hands-on | use | Export and ship: identity, export, run, the log and save folders |
| `worlds-runtime:483` | hands-on | use | Prune safely: step 8 |
| `assets:626` | hands-on | use | Export pruned with Always Include, the same exercise as `worlds-runtime:483` |
| `assets:725` | term | use | Pruning and `AlwaysInclude` |
| `scene-ecs:214-216` | feature | use | The export settings, the game's info and the manifest in the project |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Project Settings, the project folder and paths as text | `make/project-files` | must |
| Coin Run's scripts that load assets by path | `make/scripting-scene` | must |
| The HUD and the finished level | `make/hud` | must |
| Opening a terminal, changing folder and running a program with options | `start/install` | must |
| Exit codes and the standard streams | `basics/tools` | helps |

**Starting state.** The end state of `make/play-test-debug` (`startsFrom {"tutorial": "make/play-test-debug"}`): Coin
Run with its HUD, its sounds and the bug fixed. The icon is an image of `tutorials/assets/` with its credit. The page
ends with Coin Run exported (full, then pruned with **Always Include**) into a folder outside the project; the runner's
check of the exported game is a headless run of the folder.

**Command-only steps.** none

## `make/project-coin-run` — Project: Coin Run, a first finished game

**Covers.** The page turns Coin Run into a finished game and ships it again, closing block A. It starts with the plan
of a small game, written as a list of what makes a round (collect every coin before the time runs out) and what is
still missing (a way to win, a way to lose, a way to start again, polish). The steps, in sections that each end in a
checkpoint. (1) A game state in one script: a `CoinRunGame` script on an empty entity holds the round's state
(playing, won, lost) as a small `enum class`, the time left as a field, and reads the coins left. (2) Win: when no coin
is left, a centred panel "You win" appears (a UI panel and text, shown with `SetActive`), the ball stops, and the
complete sound plays (`Samples/ThirdPerson/Assets/Sounds/Complete.ogg`). (3) Lose: when the time runs out, a "Time's up"
panel. (4) Restart: a Button action **Restart** in the Gameplay map; `Game::ReloadScene()` starts the round again in
one step, and why entities do not survive a scene load (game flow's home is `make/levels-saves`). (5) Polish, each a
small step: the camera framed so that the whole level reads; a difficulty field for the time; the coins' bob and spin
tuned in the Inspector; a short glow and sound when a coin goes; the HUD's colors when time runs low. (6) Check the
game by playing it: a list of what to try (collect all, let the time run out, restart twice, play at 4:3 and 21:9),
and the Console free of warnings. (7) Ship it again: version 1.0.0 on the Game page, a pruned export with **Always
Include**, the exported game run windowed and headless as `make/export` taught. (8) Credits: `CREDITS.md` complete
(the coin model, the sounds, the textures, the music) and the notices file in the folder; one sentence says that the
reader may ship the game with the book's code in it, by the permission that `appendix/credits` states, and links it.
The exercises (`new:48`) are open extensions done in the editor and in scripts. The skill
`strata-make-a-game` sections 4 to 8 are the model for the order (scripts, scene, check by playing, export); its
command-only parts (play-tests by command, viewport captures) are left to `make/automated-playtests`. "What next" for
both tracks: track G goes on at `make/gameplay-math`; a track B reader may take track G at once, from
`make/gameplay-math`, and read the rest of `basics` later, or go on with `basics/numbers`; the Tetris and platformer
projects of block C and `make/designing-a-game` are named. At the end the reader owns a finished, exported game.

**Leaves out.**

- Game flow: levels, loading screens, saves, state passed between scenes → `make/levels-saves`
- Menus, buttons and a pause screen → `make/menus`
- A player character with a controller and a follow camera → `make/characters-cameras`
- Play-tests by command and a regression script for Coin Run → `make/automated-playtests`
- Planning a game: core loop, scope, prototype, playtest → `make/designing-a-game`
- Scene switches inside → `worlds/runtime`, `editor/play-mode`
- State machines and managers as patterns → `make/patterns`

**Fit.** `fits`: about 5,300 words against L (5,000). Eight steps in four sections with their checkpoints and four short
scripts or changes from the tutorial's files take most of it, with the plan and checking lists, "what next" and three
open exercises with worked solutions.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:541` | hands-on | home | G8 as a rolling ball (block A has no character page): actions, coins as trigger prefabs that spin, the HUD, the coin sound, a win panel, a restart with `Game::ReloadScene`, title and icon, the export and its run |
| `new:48` | hands-on | home | Exercises, open extensions ("make it yours") with worked solutions: **Basic.** a field `Points` on the coin prefab, overridden on one gold coin, and the HUD's score summed from it; **Medium.** a sixth coin on a platform that the ball reaches only with a jump; **Hard.** a kinematic obstacle moved in `OnFixedUpdate` that sends the ball back to the start with `Teleport` when it touches it. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:85` (`OnFixedUpdate`), `:89-92` (the contact callbacks); `StrataScriptCore/Include/StrataScript/Physics.h:120` (`Teleport`) |
| `gamedev:198` | feature | use | `Game::ReloadScene`, in one step; its home is `make/levels-saves` |
| `gamedev:342` | concept | use | Game flow: entities do not survive a scene load |
| `gamedev:506` | rule | use | The checking list's "a scene with no light" reminder |
| `scripting:129` | feature | use | The SDK's `Game` |
| `scripting:513` | hands-on | use | Pickup and score, finished into a round |
| `editor-core:220` | feature | use | Scene reloads asked by a script, carried out by the editor in play mode |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Exporting, pruning and running the exported game | `make/export` | must |
| The HUD: canvases, texts and their script | `make/hud` | must |
| One-shots and early requests | `make/sound` | must |
| Playing, pausing and debugging a script | `make/play-test-debug` | must |
| Input actions and adding a Button action | `make/input` | must |
| Scoped enums, `if` and classes | `basics/programming-3` | must |
| Game flow and scene loads | `make/levels-saves` | helps |

**Starting state.** The end state of `make/export` (`startsFrom {"tutorial": "make/export"}`): Coin Run with its HUD,
sounds and a first export; the project's Always Include list set. The page ends with the finished, exported Coin Run.

**Command-only steps.** none

## Passed on

none

## Not taken

none

## Questions for the planner

none
