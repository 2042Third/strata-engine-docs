# Walk G-final-2: track G, segment 2, at v0.8.0

Persona G0 (game maker). Entries walked: `make/editor-tour`, `make/project-files`, `make/scenes-entities`, `make/transforms-units`, `make/assets`.
Package: official Strata 0.8.0 Windows package (docs-package-0.8.0). All steps done through StrataCLI against one editor (a second one after the crash step), under the perf lock. Pages are the built book at 127.0.0.1:4329.

## Entries

### WK1 (make/editor-tour, "What you need") left the book
The page offers no stage download for a reader who arrives here, only "the launcher of an installed editor". I made the CoinRun project with project.create as step 1 says. Nothing failed, but a reader who lands here with no project from earlier pages has no checkpoint to fetch.

### WK2 (make/editor-tour, "Create the project", steps 1-2) guessed
The launcher dialog (template cards, Name, Location, "Creates ..." line) cannot be seen through a command. The one command did both steps and the editor opened Scenes/Main.stscene with 5 entities. I could not check "You should see" of step 1 or the grey Create button.

### WK3 (make/editor-tour, "Find the eight panels") did not match
A screenshot (editor.screenshot, 1280x720, ui-scale 1) did not look like the page's figure. A Project Settings tab already stood beside Scene and Game, though the page says it starts closed. The Console, Problems, Content Browser and Performance tabs sat in a strip that filled the whole middle column under the views; the figure shows a short bottom area. The Game view was hidden behind it. I could not tell whether editor.showPanel (Console, Performance) caused this, and I did not change the preferences. The same layout came back after the restart.

### WK4 (make/editor-tour, "Read the button strip") did not match
The tab's command is editor.status. Its answer holds project, play, assets and errors data, and says nothing about the Select/Move/Rotate/Scale buttons, their keys, World/Local or Snap, which "You should see" lists. I saw the buttons only in a screenshot I took myself; the book does not tell a command-line reader to take one.

### WK5 (make/editor-tour, "Read the status bar") did not match
editor.showPanel Performance opens the panel, as the page says. The "You should see" is about the pill, though, and a command reader sees no pill. I found it only in the screenshot.

### WK6 (make/editor-tour, "Play the scene...", first step) left the book
The step drags the Game tab to the edge of the Scene view and clicks the Game camera chip (F8). These are mouse actions with no command. I ran play.start (state "Play") and play.stop. I did not see the side-by-side views or the "Playing" pill.

### WK7 (make/editor-tour, "Stop, then clear the camera's Primary box") did not match
component.set Primary:false worked. I could not see the Game view's "No camera to show" text, because the Game tab was hidden (WK3). viewport.capture with camera "scene" failed with "The scene has no active entity with a Camera component marked Primary". That is the same fact, but the page does not name this command.

### WK8 (make/editor-tour, "Undo the change and read the journal") did not match
The journal rows for play.start and component.set are there. editor.activity with source Automation lists every command of the session, including queries, showPanel and screenshots (24 rows). The page speaks of a "Changes only" box and, in the Hard exercise, says the result "lists the first two"; it does not say the answer holds many more rows.

### WK9 (make/editor-tour, Hard exercise) guessed
The solution says editor.activity "with the parameter source set to Automation". I wrote {"source":"Automation"} and it worked, but the page shows no call shape.

### WK10 (make/editor-tour, Basic and Medium exercises) left the book
Closing panels, the View menu, Reset Layout and clicking pills have no command (editor.showPanel only opens). I did not do them, and I found no command that resets the layout.

### WK11 (make/project-files, "Look at the project and keep your work", step 1) guessed
editor.recentProjects works and lists CoinRun with its path and lastOpened. The launcher card, the right-click menu (Copy Path) and the pasted path cannot be done through commands. I read the path from the command's answer instead.

### WK12 (make/project-files, "Read the folder against this tree") did not match
The editor made Assets/Materials/Ground.stmat(+.meta), Assets/Scenes/Main.stscene(+.meta), .strata/ (Cache, Recovery, EditorSession.json, Thumbnail.png), Scripts/CMakeLists.txt and Spinner.cpp, a root .gitignore and CoinRun.stproj. There was no Scripts/CMakePresets.json and no .gitignore inside Scripts/ (the page's tree lists both; the root .gitignore holds only "/.strata/"). The tree does not list the Materials folder. CoinRun.stproj is indented with tabs, the Tetris excerpt with two spaces. The page's "If you do not see it" explains only CMakePresets.json.

### WK13 (make/project-files, "Open the settings pages") did not match
project.settings answers sections Input.Actions, Scene.CollisionLayers, Scene.Timing, Renderer.Quality and Physics.Simulation, with categories Input, Physics (three) and Rendering. No "Game" or "Export" page and no "Graphics Quality" name appear, so a command reader cannot see the four groups of "You should see".

### WK14 (make/project-files, "Save the scene") guessed
scene.save worked and answered with bytes and seconds. The "Saving 'Main'" pill was not visible.

### WK15 (make/project-files, "Change two things, then undo them") did not match
I renamed Ground with entity.rename and moved the Sun with component.set. edit.history showed "Rename 'Ground' to 'Floor'" and "Set Translation of 'Sun'", not "Undo Move Entity" (the page explains this only in the Basic exercise's solution). I did not undo the two changes before the next step, which the step's last line asks for. I then ran scene.open with force:true to go on, which discarded my change; the page does not say to use force there. The unsaved change became recovery data ("discarded on purpose").

### WK16 (make/project-files, Basic exercise) failed
The solution names entity.rename, component.set and project.setSettings without parameters. My guess {"section":"Scene.Timing","values":{"FixedRate":120}} failed: "Unknown parameter 'values'" (the name is `value`). With `value` and FixedRate 120 as a number: "'FixedRate' must be one of 'Scene', '30', '60', '120', '240'". The string "120" worked. edit.history then listed "Set Timing" last, and scene.info showed stepsPerSecond 120 with source "project". Three edit.undo calls brought everything back.

### WK17 (make/project-files, "Meet the question") matched in substance
scene.open without force refused: "The scene 'Main' has unsaved changes, which opening the scene ... would discard: save them first (scene.save) or pass force: true ...". The dialog "Save changes to 'Main'?" cannot be seen by command.

### WK18 (make/project-files, recovery) did not match
The Windows way given is Task Manager, or `taskkill /F /IM StrataEditor.exe`. My tooling refused the second form (it ends every editor on the machine); I ended my own editor by its process id. The page does not warn that the command ends all editors. After the restart (StrataCLI launch --project) the Recover Unsaved Changes dialog came up by itself (screenshot), but with two entries: the crash one ("left when the editor closed unexpectedly", 1 entity) and the earlier "discarded on purpose" one from WK15. The page's figure shows one entry. scene.recover takes `scene` (an entry id) and `action`; my guess `id` failed with "Unknown parameter 'id'". After discard, Ground had its old name.

### WK19 (make/scenes-entities, "What you need") left the book
The page needs "the project that Your first look at the editor ended with" (the tour's title is "A tour of the editor"). No stage download is offered for arrival here. I went on in the same CoinRun project.

### WK20 (make/scenes-entities, "Read the Ground's components") did not match
component.get Transform of the Ground gives Rotation as four numbers (0, 0, 0, 1), a quaternion. The page says it reads "the same values the Inspector shows", which are three angles. After component.set Rotation [-55,0,0] on the Main Camera the answer was [-0.4617, 0, 0, 0.887]. Setting takes degrees; reading gives a quaternion.

### WK21 (make/scenes-entities, "Build the walls") guessed
The Wall command worked and returned the id. entity.duplicate three times gave "Wall (1)", "Wall (2)", "Wall (3)", each result with its id. The page gives no command for "+ Empty / Walls": I guessed entity.create with only a name, and it worked. For the copies' numbers I used component.set, copied from the step before.

### WK22 (make/scenes-entities, "Make a parent") matched
entity.setParent worked for all four walls and scene.hierarchy showed them at depth 1 under Walls. entity.create takes a `parent` parameter (I used it on the next page); this page does not mention it.

### WK23 (make/scenes-entities, "Find entities again") did not match
entity.find {"tag":"Coin"} returned the Coin. {"component":"BoxCollider"} (my guess from the c: prefix) returned the Ground and four walls. {"name":"Wall*"} returned nothing and {"name":"Wall"} only the entity named Wall. The page says "Wall lists the four walls and their parent": true for the Hierarchy search, not for the command in the tab.

### WK24 (make/scenes-entities, "Keep more than one scene") matched
scene.save, scene.new, scene.saveAs {"path":"Scenes/Test.stscene"} and scene.open worked in that order; Main came back with 12 entities, and Test was empty. The start scene in CoinRun.stproj stayed Main.

### WK25 (make/scenes-entities, figures) guessed
viewport.capture with camera "scene" showed four walls, the ball near the front and the coin near the back, as the text of the figure says. The result figure is an AVIF file that my picture tool cannot read, so I compared against its caption only.

### WK26 (make/transforms-units, whole page) walked partly
Matched: the Main Camera Translation (0, 2, 6); Ball Scale (-1,1,1) accepted, entity.get with world:true shows scale -1 and euler angles; Pivot (0,90,0) + Marker (90,0,0) gives forward (0,1,0) and the swapped case (-1,0,0) (I computed forward from the world quaternion entity.get returned); Sun/Earth/Moon gives the Moon world position (0, 0, -12) with local (2,0,0) unchanged. Not walked: gizmos, Snap, the keys W/E/R, World/Local, Hierarchy drags; the read-back of a typed (0,150,0) (no command shows angles for it, see WK20); the C++ sketches (the page does not say before the Hard exercise that they need build tools).

### WK27 (make/transforms-units and make/assets, link names) did not match
make/assets calls the earlier page "Units and transforms" (twice); its title is "Positions, rotations and units". The lead of make/transforms-units says "On the page about scenes and entities you typed numbers into the Inspector", which I could only do by command.

### WK28 (make/assets, "Before you start") matched
The package held Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb.

### WK29 (make/assets, "Import the coin") matched
asset.createFolder {"path":"Models"} and asset.import worked. The result held Models/coin-gold/coin-gold.glb and Models/coin-gold/Textures/colormap.png. The Content Browser tiles were not seen.

### WK30 (make/assets, "Open the model's folder") did not match
asset.info lists subAssets: Texture "colormap (Color)", Material "colormap", Mesh "coin-gold". The page says the material and the texture are "named after the image file"; the texture is named "colormap (Color)". With "bounds": false the answer still holds subAssets and settings; the page says it "lists the same handle", and the key is `asset`.

### WK31 (make/assets, "Place the model") failed
The page's command has a `"bind": { "coin": "/id" }` key. With StrataCLI call, inside the parameters: "Unknown parameter 'bind' for asset.place". Without it the call worked (id C557BDE0B25988DA, bounds size 0.4, 0.4, 0.175). The page does not say that bind belongs only in a batch or command script. The Hierarchy then held "coin-gold" with one child "coin-gold". The page says the parent "holds only a Transform" (and its tree shows Transform, Tag): both have Name, Transform and PrefabInstance, and the child also has MeshRenderer.

### WK32 (make/assets, size check) matched
bounds.size 0.4, 0.4, 0.175 as the page says. The comparison with the ball by eye was not done.

### WK33 (make/assets, "Replace the placeholder") matched
entity.delete {"entities":[id]}, component.add Tag Coin and entity.rename Coin worked; entity.find tag Coin returned one entity.

### WK34 (make/assets, "Rename the folder") matched
asset.moveFolder Models to Props answered {"assets":2}; asset.info on Props/... showed state Ready, importing false at once; moving back worked. I did not meet the "rename back fails while importing" case.

### WK35 (make/assets, "Try to delete the model, then credit it") matched
asset.findReferences listed Scenes/Main.stscene with three entities. asset.delete without force failed with a message naming the scene. I wrote CREDITS.md at the project root with the row of the page.

### WK36 (make/assets, Basic exercise) matched
barrel.glb import worked; bounds.size 0.5176, 0.4762, 0.5176 (page: about 0.52, 0.48, 0.52). The Medium exercise (delete dialog) was not walked.

### WK37 (make/assets, "step 9" and "step 7") guessed
The text says "you will write this row in step 9" and "after step 7"; the steps are not numbered on the page. I counted the steps of the "Import the coin" section: the credits step is the 10th and the placing step the 4th, so neither number fits.

## Answers

Answered 2026-11-24 by the page fixer at v0.8.0 (319075e3). Why the walker went wrong, in most entries: it drove the
editor by command only, and the command tabs said nothing of what their answers hold or of what shows only in the
window. The tabs now say both; `make/editor-tour`'s What you need names `editor.screenshot` for the window. Facts were
read at the pin and checked against the package with a `--no-gpu` editor (`docs-work/walkfix-G2`).

| Entry | Page | Outcome | What changed, or why no fault |
| --- | --- | --- | --- |
| WK1 | make/editor-tour | fixed | What you need links the install page for a reader who arrives here and says that step 1 makes the project, so nothing is to download. |
| WK2 | make/editor-tour | fixed | Step 1's tab says the command opens no dialog and does step 2 too; step 2's tab says what the answer and the editor show. |
| WK3 | make/editor-tour | fixed | The layout comes from the user's `EditorLayout.ini`, which the walker shared with an editor used before. Step 3's If you do not see it says the layout is kept per user and that **Reset Layout** restores it; the tab says no command closes panels or resets the layout. |
| WK4 | make/editor-tour | fixed | Step 4's tab says what `editor.status` answers and that the buttons show only in the window (`editor.screenshot`). |
| WK5 | make/editor-tour | fixed | Step 5's tab says the command opens the pill's panel and the pill shows only in the window. |
| WK6 | make/editor-tour | fixed | Step 9's tab says docking and the Game camera chip have no command. |
| WK7 | make/editor-tour | fixed | Step 10's tab names `viewport.capture` with `"camera": "scene"`, whose failure message says what the Game view's text says. |
| WK8 | make/editor-tour | fixed | Step 11's tab runs `editor.activity {"source": "Automation"}` and says it lists every command of the client, queries too; If you do not see it says **Changes only** keeps only Edit commands and so hides `play.start`. The tutorial file calls it. |
| WK9 | make/editor-tour | fixed | Exercise 3's solution shows the call and says what it lists, with the `command` filter; its file checks the filter. |
| WK10 | make/editor-tour | fixed | The exercises say that 1 and 2 have no command. Engine gap noted in the notes' `## Engine`. |
| WK11 | make/project-files | fixed | Step 1's tab says the command closes nothing and that its `path` replaces **Copy Path**. |
| WK12 | make/project-files | fixed | The tree lists `Materials/Ground.stmat`; `CMakePresets.json` and `Scripts/.gitignore` are written once the build tools are found (`ScriptBuild.cpp:582-622`), at the latest at the first script build, as If you do not see it says; step 4 says the book draws tabs as two spaces. |
| WK13 | make/project-files | fixed | Step 5's tab says the answer's sections carry `title` and `category` (`Graphics Quality` for `Renderer.Quality`) and that **Game** and **Export** show its `project` fields. |
| WK14 | make/project-files | fixed | Step 6's tab says the command answers once the file is written and the pill shows only in the window. |
| WK15 | make/project-files | fixed | Step 7's tab gives the two changes, `edit.history` and the two `edit.undo` calls, with the command steps' names. |
| WK16 | make/project-files | fixed | Exercise 1's solution shows `project.setSettings` with `section`, `value` and `"FixedRate": "120"` as text, and says a bare number is refused. |
| WK17 | make/project-files | fixed | Step 8's tab says the command opens no dialog, names its two ways on and says not to pass `force` here. |
| WK18 | make/project-files | fixed | Step 9 says `taskkill /IM` and `pkill` end every editor and gives the PID form; it names `scene.recover`'s `scene` (the entry's `id`) and `action`; You should see says changes discarded on purpose stand as more entries. |
| WK19 | make/scenes-entities | fixed | What you need offers the tour's last checkpoint. The link already reads "A tour of the editor" in the source and the built page; no "first look" title exists. |
| WK20 | make/scenes-entities | fixed | Step 1's and step 5's tabs say `component.get` returns the stored four numbers and `entity.get` with `world` the angles; the file checks the four numbers. |
| WK21 | make/scenes-entities | fixed | Step 3's tab says to set each copy with `component.set`; step 4's tab creates `Walls` with `entity.create`. |
| WK22 | make/scenes-entities | fixed | Step 4's tab names `entity.create`'s `parent`. |
| WK23 | make/scenes-entities | fixed | The search tab says `name` is exact, gives the component form and names `editor.showPanel` with `search` for the field's own matching; the file checks `{"name": "Wall"}`. |
| WK24 | make/scenes-entities | rejected | Matched: every step worked as the page says. |
| WK25 | make/scenes-entities | rejected | The figure is an AVIF that browsers show; the walker's picture tool could not read it, and the capture matched the caption. |
| WK26 | make/transforms-units | fixed | The section on Strata's choice says how `entity.get` with `world` reads the worked-out angles (the Inspector's function); the exercises say what running a sketch needs. Gizmos, keys and drags are window steps of a page without command tabs. |
| WK27 | make/project-platformer | fixed | The name "Units and transforms" stood on `make/project-platformer`, not on `make/assets` (whose link has the title); fixed there. The lead of `make/transforms-units` speaks of the Inspector, the track's main tab: no change. |
| WK28 | make/assets | rejected | Matched. |
| WK29 | make/assets | rejected | Matched; the tiles are a window view. |
| WK30 | make/assets | fixed | Step 2 names the three sub-assets as imported (`colormap (Color)`) and `subAssets`; step 3 names the `asset` field and what `"bounds": false` omits; step 6 names the texture. |
| WK31 | make/assets | fixed | Step 4's tab drops `bind`, says the answer's `id` is the root's; You should see says what the Inspector shows and that commands also list `Name` and `PrefabInstance`. |
| WK32 | make/assets | rejected | Matched. |
| WK33 | make/assets | rejected | Matched. |
| WK34 | make/assets | rejected | Matched. |
| WK35 | make/assets | rejected | Matched. |
| WK36 | make/assets | rejected | Matched. |
| WK37 | make/assets | fixed | The steps are numbered on screen by the style sheet, and the walker read the text. The text now names the steps it points at ("the last step of the next section", "the step that replaces the placeholder"). |

Checked with the package (`--no-gpu` editor): `project.settings` titles and categories, the new project's files (no
`Scripts/CMakePresets.json` or `Scripts/.gitignore`), `component.get` Rotation (0, 0, 0, 1), `entity.get` world euler
(180, 30, 180) for a typed 150 and (180, 60, 180) for 120, `asset.info`'s `asset` and `subAssets` names, the placed
root's and child's components, and `editor.activity` listing queries.

Tutorial runs, 2026-11-24, both passed with the pin build and with the official package (`--package` the release zip):
`make/editor-tour` (tutorial and exercise 3, which now call `editor.activity`) and `make/scenes-entities` (tutorial,
with checks of the four stored numbers and of `entity.find {"name": "Wall"}`, and exercises 1 and 2). The other pages'
tutorial files did not change. `tools/pagecheck.py` passes for the six changed pages.

## Confirm

Confirmed 2026-11-24 by a second reader (persona G0), segment 2, with the official 0.8.0 package (windowed editor, 1600x900,
under the perf lock, one session per hold; `docs-work/walk-G-final-2`). Method notes:

- The built book at 127.0.0.1:4329 was stale: it still lacked the fixed sentences (for example "The command opens no dialog"
  of editor-tour step 1). I read the fixed pages from `src/content/docs/make/*.md` instead. Nothing was rebuilt.
- Starting states were made by the pages' own commands in a new CoinRun, not by stage downloads. No preference was changed.
- The editor opened with the user's inherited `EditorLayout.ini`: the screenshot shows Project Settings beside Scene and Game
  and Performance in the bottom tabs, as editor-tour step 3's If you do not see it now says. I did not press Reset Layout
  (no command exists, as the tab says).

| Entry | Gets through? | What I saw |
| --- | --- | --- |
| WK1 | yes | What you need says no file is to be downloaded; step 1 makes the project. |
| WK2 | yes | `project.create` answered `projectFile`, `startScene`, `template`; `editor.status` then showed project open, scene `Main`, 5 entities. Matches the step 1 and 2 tabs. |
| WK3 | yes | Inherited layout noted; the screenshot matches the new If you do not see it text. |
| WK4 | yes | `editor.status` answers project, play state, assets, errors (also scene, selection, undo); the tab says the buttons need `editor.screenshot`, which answered a 1600x900 PNG. |
| WK5 | yes | `editor.showPanel Performance` answered; the screenshot shows the panel and the pills. |
| WK6 | yes | Step 9's tab says docking and the Game camera chip have no command; `play.start` answered state Play. |
| WK7 | yes | After `component.set Primary false`, `viewport.capture {"camera":"scene"}` failed with "The scene has no active entity with a Camera component marked Primary". |
| WK8 | yes | `editor.activity {"source":"Automation"}` listed queries too (`editor.status` id 1 first) and `play.start`, `component.set`. |
| WK9 | yes | The `command` filter (`component.set`) listed the one row, with `undoStep`. |
| WK10 | yes | The exercises say 1 and 2 have no command; nothing to guess. |
| WK11 | yes | `editor.recentProjects` closed nothing and listed cards with `path` of the `.stproj`. |
| WK12 | yes | Tree matches: `Materials/Ground.stmat`; `Scripts` held only `CMakeLists.txt` and `Spinner.cpp` (no `CMakePresets.json`, no `Scripts/.gitignore`); `.strata` and root `.gitignore` present. |
| WK13 | yes | `project.settings` sections carry `title` and `category` (`Renderer.Quality`: Graphics Quality, Rendering); `project` holds `game`, `alwaysInclude`, `loadingScene`, `name`, `startScene`. |
| WK14 | yes | `scene.save` answered with `bytes` after the write. |
| WK15 | yes | `edit.history` listed `Rename 'Ground' to 'Floor'` and `Set Translation of 'Sun'`; two `edit.undo` calls undid both. |
| WK16 | yes | `project.setSettings` with `"FixedRate":"120"` worked (undo name `Set Timing`); the bare number 120 was refused. |
| WK17 | yes | `scene.open` without `force` opened no dialog and refused, naming `scene.save` and `force: true`. |
| WK18 | yes | The recovery file existed after 13 s; I ended my editor by PID; `scene.recoveryStatus` listed one entry; `scene.recover {scene: <id>, action: discard}` answered `discarded`; Ground had its old name. Only one entry, as the step 8 note predicts. |
| WK19 | yes | What you need names the tour and offers its last checkpoint. |
| WK20 | yes | `component.get` Rotation gave (0, 0, 0, 1); `entity.get` with `world` gave euler (0, 0, 0) for Ground and (-55, 0, 0) for the camera. |
| WK21 | yes | `component.set` per copy and `entity.create Walls` worked as the tabs say. |
| WK22 | yes | `entity.create` with `parent` made Earth under SolSun. |
| WK23 | yes | `entity.find {"name":"Wall"}` gave the first wall only, `{"component":"BoxCollider"}` five ids, `{"tag":"Coin"}` the coin; `editor.showPanel` with `search` was accepted. After stage 5 (Test scene made, Main reopened) 12 entities. |
| WK26 | yes | `component.set Rotation [0,120,0]` on the Ball stored (0, 0.866, 0, 0.5); `entity.get world:true` read (180, 60, 180); 150 read (180, 30, 180). The Exercises note on running a sketch is clear. |
| WK27 | yes | The robot step's link reads "Positions, rotations and units" (source of `make/project-platformer`). |
| WK30 | yes | `asset.info` `subAssets` names: `colormap (Color)`, `colormap`, `coin-gold`; the `asset` field is the handle; `"bounds": false` omits `bounds` (size 0.4, 0.4, 0.175 with it). |
| WK31 | yes | `asset.place` without `bind`: `id` is the root; root has Name, PrefabInstance, Transform; child has MeshRenderer, Name, PrefabInstance, Transform. Matches You should see. |
| WK37 | yes | "the last step of the next section" is the credits step, "the step that replaces the placeholder" is step 7; both fit. |

Residual, not blocking: assets step 3 says "where `make/project-files` taught you to look": the page id in code type, not
the page title ("Projects, saving, undo and recovery"). A reader may stop at it; it names no page they can find by that name.
