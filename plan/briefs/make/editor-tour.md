# Brief: `make/editor-tour`

| Field | Value |
| --- | --- |
| Title | A tour of the editor |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `start/how-to-read`, `start/what-an-engine-is` |
| From | gamedev "A tour of the editor" (§1.3); editor-ui "A tour of the Strata editor"; use home of editor commands (the command tab of every tutorial, read as `start/how-to-read` teaches); Coin Run's project starts here from Basic 3D |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `asset` | asset (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-1 | must | stale-item | `make/project-files` (step 1) | Step 1 opens the launcher with **File ▸ Show Launcher** while Coin Run is open. At the pin that item is greyed whenever a project is open; only **File ▸ Close Project** (after the unsaved-changes question) leads to the launcher and its cards. | Step 1 closes the project with **File ▸ Close Project**, reads the CoinRun card there (right-click: **Show in Folder**, **Copy Path**), and opens Coin Run again by clicking its card. **File ▸ Show Launcher** stays only on `make/editor-tour`, for the way back after "Continue without a project" (about 40 words more). | `allocation/make-a.md:105-108`; `StrataEditor/src/EditorLayer.cpp:1476-1484` (the comment at `:1481`: "with a project open, Close Project leads there"); `StrataEditor/src/Panels/WelcomePanel.cpp:630-637` |
