# Brief: `start/coming-from`

| Field | Value |
| --- | --- |
| Title | Coming from Unity, Unreal or Godot |
| Kind | H |
| Size | M |
| Tracks | G, E |
| Needs | `start/what-an-engine-is` |
| From | new; curricula 5.2; gamedev concepts 4, 7 (GameObject and entity, prefab variants and Strata's overrides, Blueprints and C++ scripts); optional on both tracks |
| Unit | `plan/allocation/start.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `start/coming-from` — Coming from Unity, Unreal or Godot

**Covers.** The goal: find in Strata what the reader used in Unity, Unreal or Godot, and the page that teaches it. What
must be true first: the reader has made something in one of those engines (the page is written for that reader, and
optional on both its tracks), has made the first game and has read `start/what-an-engine-is`. The page opens with the
map of names as one table per idea, a column per engine and one for Strata, each Strata cell linking its page: the thing
in a scene (GameObject, Actor, Node: entity); its parts (Component, ActorComponent, child nodes: component); reusable
groups (Prefab, Blueprint class, PackedScene: prefab, with per-property overrides and no variants or nested prefabs);
game code (C#, Blueprints and C++, GDScript: C++ script classes, no visual scripting); the callbacks (`Update`, `Tick`,
`_process`: `OnUpdate`; `FixedUpdate`, `_physics_process`: `OnFixedUpdate`); levels (Scene, Level, scene: scene); the
project's settings and input (Input System, Enhanced Input, the input map: input actions); assets and their folder;
building a game for players (Build, Package, Export: export). The steps then find each row in a copy of the Third-Person
Adventure: open its Course scene; select `Player` in the Hierarchy (an entity); read its components in the Inspector (a
CharacterController and a Script with `ThirdPersonPlayer`); find the Coin prefab in the Content Browser and a placed
coin whose overridden values show in bold; open `ThirdPersonPlayer.cpp` from the Content Browser's **Scripts** and find
its `OnUpdate`; open **File ▸ Project Settings...** and its Input Actions. Units and axes get a section of their own,
because imported content breaks there first: Strata is right-handed, Y up, -Z forward, in metres, with Euler angles in
degrees, as Godot is and unlike Unity (left-handed) and Unreal (Z up, centimetres); glTF models face +Z. `## Result`:
the reader's own map of names. Variations: a reader who knows a code-first engine (entities and components as in Strata,
an editor as in Unity); and what to look for elsewhere because Strata does not have it, each linked to the page that
says so through `appendix/not-in-strata` (nested prefabs and variants, visual scripting, mobile and web targets,
particles, terrain). The exercise is done in the sample's copy: the reader finds the camera that follows the player,
names its components in Strata's words against their old engine's, and finds the callback that moves it, `OnLateUpdate`,
against Unity's `LateUpdate`. At the end the reader can name Strata's word for each idea of their old engine and open
the page that teaches it.

**Leaves out.**

- Entities and components as a game maker builds with them → `make/scenes-entities`
- Prefabs, overrides, Apply and Revert → `make/prefabs`
- Axes, units and rotations → `make/transforms-units`
- The script's parts and the C++ they need → `make/first-script`, `basics/programming-3`
- The script's callbacks and their order → `make/script-loop`
- Input actions → `make/input`
- Exporting a game → `make/export`
- How object models differ inside an engine → `world/what-a-world-is`
- Everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 2,950 words against M (3,000). The map of names (about ten rows of four columns), six steps on
the sample's copy, the section on units and axes, two variations and the exercise take about 2,350 words; the fixed
parts take the rest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:20` | concept | home | Strata's names for other engines' ideas (GameObject and entity, prefab variants and Strata's overrides, Blueprints and C++ scripts, the callbacks, the axes and units), the one-home table's row for this page; the other engines' side has its sources in Further reading. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-45` (Strata's callbacks); `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (a prefab made from linked entities keeps no inner links); `Docs/Architecture.md:250` (right-handed, +Y up, -Z forward, degrees) |
| `gamedev:298` | concept | use | Entities and components from the user's side, against GameObject subclasses and actor hierarchies; the use home is `make/scenes-entities` |
| `gamedev:306` | concept | use | Prefabs with per-property overrides, set against Unity's nested prefabs and variants and Unreal's Blueprints; the use home is `make/prefabs` |
| `gamedev:71` | feature | use | The conventions a maker must know (Y up, -Z forward, glTF models facing +Z, degrees, metres), set against each engine's; the use home is `make/transforms-units` |
| `gamedev:317` | concept | use | Scripts in C++ for a reader who wrote C#, GDScript or Blueprints: a class built into a module, `override`, fields registered by a macro; taught by `basics/programming-3` and `make/first-script` |
| `gamedev:255` | feature | use | The Third-Person Adventure, whose player, coin prefab, script and input actions the steps open |
| `gamedev:144` | feature | link | Input actions, linked to `make/input` |
| `scene-ecs:271` | concept | link | Object models (inheritance, components, ECS), linked to `world/what-a-world-is` for track E |
| `scripting:243` | concept | link | How other engines script and why Strata uses C++ modules, linked to `scripting/why-scripts` |
| `new:27` | hands-on | home | The exercise (**Basic.**, done in the copy of the Third-Person Adventure): the entity `Camera` of the Course scene is found, with its Camera component (Primary) and a Script with `FollowCamera` whose `Target` field names `Player`; the reader names what their old engine uses for it, and finds in `FollowCamera.cpp` that it moves in `OnLateUpdate`, which runs every frame after the fixed updates, as Unity's `LateUpdate` runs after `Update`. Evidence: `Samples/ThirdPerson/Assets/Scenes/Course.stscene:2` (the `Camera` entity, its components and the `Target` field); `Samples/ThirdPerson/Scripts/FollowCamera.cpp:43` (`OnLateUpdate`); `StrataScriptCore/Include/StrataScript/Script.h:33-35` (the callbacks' order) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, components, a scene, a script and Play, as the first game showed them | `start/first-game` | must |
| Opening a copy of a sample from the launcher | `start/first-game` | must |
| The engine, the editor and the runtime; the frame and delta time | `start/what-an-engine-is` | must |

**Starting state.** A copy of the Third-Person Adventure made with **Open Sample...** as `start/first-game` made the
Tetris copy, with its Course scene opened (the sample starts in its main menu scene). No checkpoint of an earlier
tutorial.

**Command-only steps.** none

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
| critic-start-2 | must | missing-item | `start/first-game` (sections 3 to 5, "What next") | The tutorial never saves the scene and never opens a project again. The cubes and the Spinner on the third cube live only in the open scene, and closing the editor asks Save, Don't Save or Cancel, which the page does not show. Three later pages reopen what this page made: the frame pill exercise of `start/what-an-engine-is` plays the Tetris copy again, `start/coming-from` opens another sample's copy, and on track E `basics/programming-1` uses this project's Spinner as its playground. Track E never reads `make/editor-tour`, where saving and recent projects are taught. | Sections 3 to 5 each end with **File ▸ Save Scene** (Ctrl+S; the item is off while the game plays), and the last says what closing the editor asks. "What next" shows how a project is opened again: the launcher's Recent projects card or **File ▸ Open Recent**. New `use` rows of `gamedev:36` and `gamedev:513` (homed on `make/editor-tour`) and of `editor-core:131` (homed on `editor/saving` with `editor-core:130-137`). About 250 words. | `allocation/start.md:227-261`, `:416`, `:505-506`; `allocation/basics-a.md:158-159`, `:229-230`; `allocation/make-a.md:121-125`, `:159`, `:168`, `:174`; `allocation/editor.md:376` (`editor-core:130-137`); `book.md:66-67`; `StrataEditor/src/EditorLayer.cpp:1464`, `:1493`; `StrataEditor/src/Panels/WelcomePanel.cpp:468-490`; `StrataEditor/src/Editor/EditorContext.cpp:694` |
| critic-start-3 | must | stale-item | `gamedev:306` and `new:20` on `start/coming-from` (step 4) | The step "a placed coin whose overridden values show in bold" cannot be done. None of the 24 coins of the Course scene differs from `Coin.stprefab` outside the root's transform and name, which are never overrides, and no other prefab instance of the scene holds an override. The Inspector shows nothing in bold. | The step makes an override and undoes it: select a placed coin, change its Sphere Collider's Radius, see the label turn bold with the accent bar, then right-click it and choose **Revert**. One sentence names **Apply to Prefab** and links `make/prefabs`. About 80 words. | `allocation/start.md:453-454`; `Samples/ThirdPerson/Assets/Scenes/Course.stscene:106` (`Coin 1`; the 24 instances of the prefab `7F22E66F836406A6` compared by `docs-work/C2/critic-start/coinov.py`); `Samples/ThirdPerson/Assets/Prefabs/Coin.stprefab:2-3`; `Strata/src/Strata/Scene/PrefabOverrides.h:25`; `Docs/Manual/Prefabs.md:36-41` |
| critic-start-4 | should | stale-item | `start/first-game` (section 4, `new:25`), `start/coming-from` (step 3) | Four UI labels in the rows are the names in the code, not what the editor shows. The Add Component menu lists **Rigid Body** under Physics; the Inspector shows **Gravity Scale** and the Spinner's field as **Degrees Per Second**; the Player of `start/coming-from` has a **Character Controller**. A reader looks for "RigidBody" in the menu and does not find it. | Write the labels as the editor shows them: **Add Component ▸ Rigid Body**; **Gravity Scale** in `new:25`; **Degrees Per Second** wherever the Inspector is meant (`DegreesPerSecond` stays for the code); **Character Controller** on `start/coming-from`. One sentence on `start/first-game` says that the Inspector writes a name of the code with spaces. About 30 words. | `allocation/start.md:242`, `:258`, `:326`, `:453`; `Strata/src/Strata/Physics/PhysicsComponents.cpp:121-122`, `:168`; `Strata/src/Strata/Reflection/PropertyBuilder.cpp:25`; `StrataEditor/src/Panels/InspectorPanel.cpp:141`, `:1192` |
| critic-start-13 | should | missing-item | `new:20` on `start/coming-from` | The map of names leaves out what a reader from another engine looks for first: `OnCreate` (Unity's `Start` and `Awake`, Unreal's `BeginPlay`, Godot's `_ready`) and `OnDestroy`; the contact callbacks, which keep Unity's names `OnCollisionEnter` and `OnTriggerEnter`; the rule that setup goes in `OnCreate`, not in the constructor; the editor's panels (Unity's Project window is the Content Browser); physics bodies and the Character Controller that step 3 reads; and tags, which the Player carries. | Add these rows to the map, each Strata cell linking its page (`make/script-loop`, `make/physics`, `make/editor-tour`, `make/scenes-entities`), and widen `new:20`'s evidence. About 250 words. | `allocation/start.md:445-451`, `:486`; `StrataScriptCore/Include/StrataScript/Script.h:31-38`, `:69`, `:81-91`; `Samples/ThirdPerson/Assets/Scenes/Course.stscene:151` (the Player: CharacterController, Script, Tag) |
| critic-start-20 | could | missing-item | `start/coming-from` (step 5) | In `ThirdPersonPlayer.cpp` the reader does not find `OnUpdate` as `Spinner` showed it. The class is declared in `ThirdPersonPlayer.h`, and the source file defines `void ThirdPersonPlayer::OnUpdate(float deltaTime)` outside the class. A reader who wrote C# or GDScript has not met that form. | The step says in one sentence that the header declares the class and the source file defines its functions with the class's name before `::`, and links `basics/programming-3`. About 30 words. | `allocation/start.md:454-455`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.h:45`; `Samples/ThirdPerson/Scripts/ThirdPersonPlayer.cpp:54` |
