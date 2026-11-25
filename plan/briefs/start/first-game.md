# Brief: `start/first-game`

| Field | Value |
| --- | --- |
| Title | Your first game |
| Kind | T |
| Size | L |
| Tracks | G, E, B |
| Needs | `start/install` |
| From | gamedev "The launcher and your first project" (§1.2; hands-on G1-G3, G6): the Tetris copy played within five minutes, a Basic 3D project with falling bodies, the generated `Spinner` script attached and built; then one change to it: `DegreesPerSecond` changed in the code editor, the scripts built again with **Ctrl+B**, one `Log::Info` line added and read in the **Console** panel (the playground of `basics/programming-1` on track E); the first build (Play on the Tetris copy) is the toolchain check, or a toast names what to install; "what next" names the tracks and `make/with-an-agent` |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/first-game` — Your first game

**Covers.** What you will make: after playing a finished game, a project of your own in which a cube falls onto a ramp,
slides and bounces, and another one spins, turned by a C++ script you changed. What you need: the editor, the C++ build
tools and the code editor of `start/install`. Five step sections, each a stage of the page's tutorial file and each
ending in a checkpoint with its "You should now have" picture; at most four new terms per section. 1, "Play a finished
game": start the editor and meet the launcher (its cards, **New Project**, **Open Sample...**); **Open Sample... ▸
Tetris** makes a copy in a folder the reader chooses (launcher and sample defined); **Play** builds the copy's scripts
first, the status bar saying "Building to play" (build and Play defined): this first build is the check of the build
tools that `start/install` installed, and its "If you do not see it" is the toast that names what to install; the game
runs in the Game view with the keys of the sample's README, after a click in the view; **Stop**. 2, "Make a project":
**File ▸ New Project...**, the Basic 3D template, a name and a folder; the template's scene and its five entities in the
Hierarchy (Main Camera, Sun, Sky, Ground, Post Process), with project, template, scene and entity defined (the Tetris
copy of section 1 was a project too, which this section says). 3, "Place and move a cube": **+ ▸ Cube** puts a cube on
the ground where the view looks; the Inspector lists its components (component defined); the Move, Rotate and Scale
gizmos (W, E, R) lift, turn and stretch it, the green arrow pointing up, and Ctrl+Z undoes a drag; the Scene view and
the Game view are told apart; **Play** shows the scene through the Main Camera, and **Stop** puts back what changed
while playing, because Play runs a copy of the scene. 4, "Make it fall": **Add Component ▸ RigidBody** on the lifted
cube (Dynamic is the default; the ground already has a collider), and Play: it falls and rests; a second cube, scaled
long and tilted, makes a ramp, and the falling cube slides down it; Friction (how much two surfaces grip) and
Restitution (how much it bounces) are changed, and a bounce is seen. 5, "Make it spin with a script": a third cube
without a RigidBody, placed above the scene (one sentence says why: a body that physics moves is not also turned by a
script); **Scripts ▸ Build Scripts** (Ctrl+B) builds the `Spinner.cpp` that every new project has; **Add Component ▸
Script** offers the built class `Spinner` (script and script class defined); Play: it turns. The file opens from the
Content Browser's **Scripts** in the code editor (or the system's application for `.cpp` files) and is read with the
method of `start/how-to-read`: its parts are named in a sentence each (a class built on `Script`, `OnUpdate` marked
`override`, the registration with `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`), which `make/first-script` and
`basics/programming-3` teach; `deltaTime` is named in one sentence with a link to `start/what-an-engine-is`.
`DegreesPerSecond` goes from 90 to 360, Ctrl+B, Play: it turns four times as fast (the entity holds no value of its own
for the field, so the code's default applies; the tutorial's run confirms it). Then an `OnCreate` with one `Log::Info`
line is added (in `OnCreate`, so that the line is written once and not every frame), built and played, and the line is
read in the **Console** panel; on track E this is the playground of `basics/programming-1`. "What next" names each
track's next page (`start/what-an-engine-is` for all three) and `make/with-an-agent`. Three exercises, done in the
project: the falling cube's GravityScale set to 0.2 (predict, then run); `DegreesPerSecond` set to -90 (predict, then
run: it turns the other way); the `Log::Info` line moved from `OnCreate` into `OnUpdate`, which fills the Console with a
line every frame, and moved back. At the end the reader can open and play a copy of a sample, make a project from a
template, place and move entities, give one a physics body, attach, build and change a script, and read what it writes.

**Leaves out.**

- The editor's panels, menus and navigation in full → `make/editor-tour`
- What a new project writes, and the project folder → `make/project-files`
- Entities and components as a game maker builds levels from them → `make/scenes-entities`
- Positions, rotations and units as numbers → `make/transforms-units`
- Bodies, colliders, layers and triggers → `make/physics`
- New Script, the script's parts, hot reload and the crash toast → `make/first-script`
- The template's lighting → `make/lighting`
- Samples as copies, and the other four samples → `make/samples`
- Play, Simulate, Pause and Step, and edits while playing → `make/play-test-debug`
- How the editor and the launcher work inside → `editor/projects`, `editor-ui/launcher-dialogs`

**Fit.** `fits`: about 5,550 words against L (5,000). Twenty steps for B0 at about 150 words each take about 3,000
words; the terms defined in the steps, the five checkpoints, the `Spinner` file and the three exercises take most of
the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:30` | feature | home | The launcher as the reader first meets it: its cards, New Project and Open Sample; the agent card is named and left to `make/with-an-agent` |
| `gamedev:32` | feature | home | The Basic 3D template: the five entities of its scene, the ground with its collider; its lighting is `make/lighting`'s |
| `gamedev:438`, `editor-ui:549` | figure | home | The launcher with its template and sample cards and the agent card, at the first step; one recipe for both items (start-q8), which `editor-ui/launcher-dialogs` uses. At a first start "Recent projects" shows its empty note (`StrataEditor/src/Panels/WelcomePanel.cpp:487-490`), so the recent projects and their pictures that `editor-ui:549` names appear once projects exist |
| `gamedev:439`, `editor-ui:550` | figure | home | The New Project dialog with Basic 3D chosen, and the Open Sample dialog; one recipe for both items (start-q8), which `editor-ui/launcher-dialogs` uses |
| `gamedev:534` | hands-on | home | G1 as section 1: a copy of Tetris opened, played and stopped, its README's keys (the install is `start/install`'s) |
| `gamedev:535` | hands-on | home | G2 as sections 2 and 3: a Basic 3D project, a cube from "+", the gizmos, Play and Stop, the scene put back |
| `gamedev:536` | hands-on | home | G3 as section 4: a dynamic RigidBody, a ramp, Friction and Restitution |
| `gamedev:572` | term | home | Launcher |
| `gamedev:573` | term | home | Project |
| `gamedev:574` | term | home | Template |
| `gamedev:575` | term | home | Sample, always opened as a copy |
| `gamedev:576` | term | home | Scene |
| `gamedev:578` | term | home | Entity |
| `gamedev:579` | term | home | Component |
| `gamedev:594` | term | home | Gizmo |
| `gamedev:595` | term | home | Scene view and Game view |
| `gamedev:604` | term | home | Script and script class; the entry's "script module" is named once in a link to `make/script-builds`, where the glossary step homes it (start-q6) |
| `gamedev:596` | term | use | Play, defined here in one sentence in section 1; the entry's home is `make/play-test-debug`, and the glossary step homes "Play mode" on this page (start-q6) |
| `gamedev:254` | feature | use | The Tetris sample: its copy played, its README's keys |
| `gamedev:35` | feature | use | Open Sample makes a copy in a folder the reader chooses |
| `gamedev:33` | feature | use | A new project comes with `Scripts/Spinner.cpp`, named in one sentence |
| `gamedev:130` | feature | use | Play builds the scripts first; Ctrl+B builds them; the first build finds the toolchain |
| `gamedev:131` | feature | use | Add Component ▸ Script and the classes of the built scripts |
| `gamedev:125` | feature | use | `DegreesPerSecond`: the number in the code is the value the cube uses |
| `gamedev:359` | code | use | The generated `Spinner.cpp`, shown as the reader's own file; its home is `make/first-script` |
| `gamedev:539` | hands-on | use | G6's first half: Spinner attached and `DegreesPerSecond` changed; changing it while playing is `make/first-script`'s |
| `gamedev:46` | feature | use | The status bar's "Building" and "Building to play" |
| `gamedev:47` | feature | use | The toast of a failed build, which names what to install when the toolchain is missing |
| `gamedev:54` | feature | use | The Console, where the `Log::Info` line appears; the Problems panel named for a failed build |
| `gamedev:61` | feature | use | Where a script file opens: the code editor, or the system's application for `.cpp` files |
| `gamedev:48`, `gamedev:49` | feature | use | The Scene view's navigation as far as the steps need (orbit, frame with F), and the Game view while playing |
| `gamedev:50`, `gamedev:51` | feature | use | The Hierarchy's "+" menu and the Inspector's Add Component |
| `gamedev:69` | feature | use | The built-in cube |
| `gamedev:57` | feature | use | Ctrl+Z after a gizmo drag |
| `gamedev:222` | feature | use | Play runs a copy of the scene, and Stop restores the edited scene |
| `gamedev:152` | feature | use | A dynamic body on the cube against the ground's static collider; Friction and Restitution |
| `gamedev:328` | concept | use | Why the spinning cube has no RigidBody: physics moves a dynamic body, a script does not write its transform (one sentence) |
| `physics:28` | feature | use | The RigidBody component, its Type, Friction and Restitution as the Inspector shows them |
| `scripting:124` | feature | use | `Log::Info`, one line to the Console |
| `editor-ui:115` | feature | use | The toolbar's gizmo tools: Move (W), Rotate (E), Scale (R) |
| `editor-ui:214`, `editor-ui:215` | feature | use | The launcher and the New Project and Open Sample dialogs, as the steps use them |
| `editor-ui:685` | hands-on | use | "First launch: New Project with Basic 3D": its first part, as section 2 |
| `new:25` | hands-on | home | Three exercises, done in the page's project: **Basic.** predict, then run: the falling cube's GravityScale set to 0.2 in the Inspector, and it falls more slowly; **Medium.** predict, then run: `DegreesPerSecond` set to -90 in `Spinner.cpp`, built with Ctrl+B and played: the cube turns the other way, at a quarter of the step's 360 degrees a second; **Medium.** predict, then run: the `Log::Info` line moved from `OnCreate` into `OnUpdate` writes one line every frame, which the Console shows, and is moved back. Evidence: `Strata/src/Strata/Physics/PhysicsComponents.cpp:128` (GravityScale, -100 to 100); `StrataEditor/src/Editor/ScriptProject.cpp:244-250` (the field and the turn about the Y axis by `DegreesPerSecond * deltaTime`); `StrataScriptCore/Include/StrataScript/Script.h:32-33` (`OnCreate` once, `OnUpdate` every frame) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor unpacked and started, the C++ build tools and a code editor installed | `start/install` | must |
| Where the editor's log is, for "If you do not see it" | `start/install` | helps |
| Reading code you do not understand yet, for `Spinner.cpp` | `start/how-to-read` | helps |
| Reading a step's two tabs and its "You should see" | `start/how-to-read` | helps |
| The frame and `deltaTime`, named once in a link | `start/what-an-engine-is` | helps |

**Starting state.** The editor, the C++ build tools and the code editor of `start/install`; no project and no
checkpoint of an earlier tutorial. Section 1 makes a copy of the Tetris sample in a folder the reader chooses (its
checkpoint is that copy, unchanged); section 2 makes a new project from the Basic 3D template, which sections 3 to 5
continue, each ending in a checkpoint of that project.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `build` | build | - |
| `gizmo-start` | Gizmo (start) | - |
| `project` | project | game project |
| `sample-start` | Sample (start) | - |
| `script` | script | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-start-2 | must | missing-item | `start/first-game` (sections 3 to 5, "What next") | The tutorial never saves the scene and never opens a project again. The cubes and the Spinner on the third cube live only in the open scene, and closing the editor asks Save, Don't Save or Cancel, which the page does not show. Three later pages reopen what this page made: the frame pill exercise of `start/what-an-engine-is` plays the Tetris copy again, `start/coming-from` opens another sample's copy, and on track E `basics/programming-1` uses this project's Spinner as its playground. Track E never reads `make/editor-tour`, where saving and recent projects are taught. | Sections 3 to 5 each end with **File ▸ Save Scene** (Ctrl+S; the item is off while the game plays), and the last says what closing the editor asks. "What next" shows how a project is opened again: the launcher's Recent projects card or **File ▸ Open Recent**. New `use` rows of `gamedev:36` and `gamedev:513` (homed on `make/editor-tour`) and of `editor-core:131` (homed on `editor/saving` with `editor-core:130-137`). About 250 words. | `allocation/start.md:227-261`, `:416`, `:505-506`; `allocation/basics-a.md:158-159`, `:229-230`; `allocation/make-a.md:121-125`, `:159`, `:168`, `:174`; `allocation/editor.md:376` (`editor-core:130-137`); `book.md:66-67`; `StrataEditor/src/EditorLayer.cpp:1464`, `:1493`; `StrataEditor/src/Panels/WelcomePanel.cpp:468-490`; `StrataEditor/src/Editor/EditorContext.cpp:694` |
| critic-start-4 | should | stale-item | `start/first-game` (section 4, `new:25`), `start/coming-from` (step 3) | Four UI labels in the rows are the names in the code, not what the editor shows. The Add Component menu lists **Rigid Body** under Physics; the Inspector shows **Gravity Scale** and the Spinner's field as **Degrees Per Second**; the Player of `start/coming-from` has a **Character Controller**. A reader looks for "RigidBody" in the menu and does not find it. | Write the labels as the editor shows them: **Add Component ▸ Rigid Body**; **Gravity Scale** in `new:25`; **Degrees Per Second** wherever the Inspector is meant (`DegreesPerSecond` stays for the code); **Character Controller** on `start/coming-from`. One sentence on `start/first-game` says that the Inspector writes a name of the code with spaces. About 30 words. | `allocation/start.md:242`, `:258`, `:326`, `:453`; `Strata/src/Strata/Physics/PhysicsComponents.cpp:121-122`, `:168`; `Strata/src/Strata/Reflection/PropertyBuilder.cpp:25`; `StrataEditor/src/Panels/InspectorPanel.cpp:141`, `:1192` |
| critic-start-5 | should | stale-item | `gamedev:131` on `start/first-game` (section 5) | Attaching Spinner takes two choices, not one. **Add Component ▸ Script** adds an empty Script component; the class is picked in that component's **Add Script...** list, which appears only once a build has loaded the module. The row says that Add Component ▸ Script offers the class. | Section 5 gives both clicks. Its "If you do not see it" names the Inspector's note "No script module is loaded: build the scripts (Scripts > Build Scripts) to edit their fields". About 40 words. | `allocation/start.md:247-248`, `:306`; `StrataEditor/src/Panels/InspectorPanel.cpp:1221-1227`, `:1268-1281`; `Docs/Manual/Scripting.md:57-58` |
| critic-start-6 | should | missing-item | `start/first-game` (section 5) and `new:25` | The change to `DegreesPerSecond` in the code shows only under conditions the page does not state. The file must be saved in the code editor before Ctrl+B. The game must be stopped: a build while it plays hot reloads the module and carries the running value (90) over, and `OnReload` runs instead of `OnCreate`, so neither the faster turn nor the `Log::Info` line appears. And once the reader has changed the field in the Inspector, the entity keeps its own value and changes of the code no longer apply. | The step says: save the file in the code editor, stop the game, then Ctrl+B and Play. Its "If you do not see it" names the three causes and the Inspector's reset arrow ("Reset to the class default"). Hot reload itself stays `make/first-script`'s. About 100 words. | `allocation/start.md:253-256`, `:326`; `StrataScriptCore/Include/StrataScript/Script.h:49-52`; `StrataEditor/src/Editor/ScriptProject.cpp:244`; `Strata/src/Strata/Scripting/ScriptingComponents.h:24`; `StrataEditor/src/Panels/InspectorPanel.cpp:170` |
| critic-start-7 | should | missing-item | `gamedev:152` and `physics:28` on `start/first-game` (section 4) | The ramp works only when it is steep enough, and the page gives no angle. The ramp has no Rigid Body, so its collider gets the default friction 0.5, and box3d takes the square root of the product of the two frictions. With the cube's default 0.5 the pair grips with 0.5, and the cube stays on any slope under about 27 degrees. A reader who tilts the ramp by 15 degrees sees nothing happen. Restitution takes the larger of the two values, so the bounce needs only the cube's. | The step gives the tilt as a number typed into the ramp's Rotation in the Inspector (35 degrees). Its "If you do not see it" says: tilt more, or lower the cube's Friction. One sentence links the mixing rule's home (`physics/new:27` on `physics/bodies-colliders`), which `make/physics` uses. About 60 words. | `allocation/start.md:243-245`; `Strata/src/Strata/Physics/PhysicsWorld.cpp:1995-2010`; `Strata/src/Strata/Physics/PhysicsComponents.h:34-35`; `Strata/vendor/box3d/src/physics_world.c:155-165`; `allocation/physics.md:108` |
| critic-start-8 | should | missing-item | `gamedev:61` on `start/first-game` (section 5) | Nothing makes Strata open `Spinner.cpp` in the code editor that `start/install` installed. Without an External Editor setting the file goes to the system's application for `.cpp` files, which may be none: then the editor fails with a message that names the command `script.setExternalEditor`, which the reader cannot run. Choosing the editor is left to `make/first-script`, which track E never reads, and track E edits this project's script on `basics/programming-1`. | The page's `use` row of `gamedev:61` widens: one step before the file is opened, **Scripts ▸ External Editor...**, a click on the code editor it lists (VS Code or Visual Studio), then **Apply**. `make/first-script` keeps the home and the whole page. About 80 words. | `allocation/start.md:180`, `:248-249`, `:313`; `allocation/make-a.md:809`; `book.md:66-67`; `StrataEditor/src/Editor/ExternalEditor.cpp:387-391`; `StrataEditor/src/EditorLayer.cpp:1603`; `Docs/Manual/Scripting.md:76-91` |
| critic-start-9 | should | order | `start/first-game` (sections 4 and 5) | The page uses three words that a reader of tracks G and B has never met, and does not define them: rigid body (the component it adds), collider (what the ground "already has") and field (`DegreesPerSecond`, `ST_SCRIPT_FIELD`). Their homes, `gamedev:621`, `gamedev:622` and `gamedev:608`, are on `make/physics` and `make/first-script`, after this page, and the page has no row for them. | Each gets one plain sentence where it is first used, with a link to its home (a forward mention), and a `link` row of `gamedev:621`, `gamedev:622` and `gamedev:608`. Section 4 then holds four new terms (rigid body, collider, Friction, Restitution), as the Covers allows. About 60 words. | `allocation/start.md:229-230`, `:242-253`; `allocation/make-a.md:884`, `:1321-1322`; `allocation/README.md:243-246`; `style.md:61-73` |
| critic-start-14 | should | missing-item | `start/first-game`; `new:7` on `start/how-to-read` | On macOS every Ctrl shortcut of the editor is pressed with Cmd, because ImGui swaps the two keys on Apple builds, while the menus still print "Ctrl+B" and "Ctrl+S". The rows give Ctrl+B and Ctrl+Z only, and the conventions of `start/how-to-read` do not warn that a Mac's menus name another key than the one to press. | The keys of `start/first-game` (Ctrl+B, Ctrl+Z, and Ctrl+S with critic-start-2) carry **Cmd** for macOS, as `style.md` §9.2 asks. `new:7` adds one sentence: on a Mac the editor's menus say Ctrl, and the key to press is Cmd. About 30 words. | `allocation/start.md:115`, `:240`, `:247`, `:253`; `Strata/vendor/imgui/imgui.cpp:1731-1735`, `:1933-1942`; `StrataEditor/src/EditorLayer.cpp:983`, `:1591`; `allocation/editor-ui.md:868`; `style.md:685-686` |
| critic-start-18 | could | missing-item | `gamedev:534` on `start/first-game` (section 1) | Tetris quits on Escape, and in the editor a script's quit stops Play, with the line "The game quit with exit code 0; play mode stopped". A reader who presses Escape to leave the game, as in many games, sees Play end without pressing Stop. | The table of keys in section 1 says that Escape ends the game, here as Stop does. About 25 words. | `allocation/start.md:234-235`, `:288`; `Samples/Tetris/README.md:30`; `Samples/Tetris/Scripts/TetrisBoard.cpp:86-89`; `StrataEditor/src/Editor/EditorContext.cpp:1439` |
