---
id: reference/game-makers
title: "Cheat sheet for game makers"
description: "The editor, components, script calls, conventions, commands, runtime options and project folder a game maker uses every day, one line each."
kind: reference
size: M
tracks: []
needs: [make/first-script]
status: final
---

This page holds the names you use every day while you make a game, so that you can find one again without searching. You have made a first script, as in [Coin Run](../make/project-coin-run.md), and now you want a name back. A row gives the name, one line of what it does and, in the sentence above each table, the page that teaches it or holds the full entry. Nothing here is complete: the catalogue pages hold every property, call and command. Each table below comes by hand from the engine's code and the catalogue pages, and each section starts with the page that teaches its subject.

## The editor

[The editor tour](../make/editor-tour.md) teaches the windows; [the editor reference](../reference/editor.md) lists every menu and panel. Each panel of the first table opens from the **View** menu; **Project Settings** and the last three start closed.

| Panel | What you do there |
| --- | --- |
| **Scene** | Look at the scene, move things with the :term[gizmo]{id=gizmo-start} and pick entities |
| **Game** | See what the player sees, through the primary camera |
| **Hierarchy** | Create, rename, parent and delete entities |
| **Inspector** | Edit the components of the selection; with nothing selected, the scene's settings |
| **Asset** | Change an asset's :term[import settings]{id=import-settings}, edit a material |
| **Content Browser** | Browse folders, drag assets into the scene, find your scripts |
| **Console** | Read the log; a message with a file and line is a link |
| **Problems** | Read build errors and script crashes; a double click opens the line |
| **Project Settings** | Edit the settings that belong to the whole game |
| **Streaming** | Watch loads, uploads and the cells of a big world |
| **Performance** | Read the time of each stage of a frame |
| **Activity** | See every command and who ran it |

The shortcuts a maker uses most are in the next table. The gizmo keys work while the pointer is over the **Scene** panel.

| Keys | What happens |
| --- | --- |
| **Ctrl+P** | Starts play mode; in play mode it stops |
| **Ctrl+S**, **Ctrl+Shift+S** | Saves the scene; saves it under a new name |
| **Ctrl+Z**, **Ctrl+Y** | Undoes; redoes (**Ctrl+Shift+Z** redoes too) |
| **Ctrl+B** | Builds the scripts and reloads them |
| **Ctrl+D**, **F2** | Duplicates the selection; renames it |
| **Q**, **W**, **E**, **R** | No gizmo; move; rotate; scale |
| **F**, **Home** | Frames the selection; frames the whole scene |
| **F8** | Looks through the scene's primary camera |

The toolbar has the play buttons: **Play**, **Simulate** (physics only), **Pause**, **Step** (one fixed update while paused) and **Stop**. Play runs a copy of the scene, and stopping returns you to the scene you edited. The chips along the top of the **Scene** panel change how it draws; none of them changes the scene.

| Chip | What it does |
| --- | --- |
| **Camera** | Sets the editor camera's field of view, clip planes and fly speed |
| **Grid**, **Outline**, **Gizmos** | Show the ground grid, the selection's outline and the shapes of lights, cameras and colliders |
| **Preview lighting** | Lights a scene that has no light, in the editor view only |
| **Game UI**, **2D** | Show the user interface (UI) drawn on the screen; edit a canvas flat |
| **Game camera** | Looks through the primary camera with the editor overlays |
| **Cells** | Shows the cells of an open world |
| **Stats** | Shows :term[frame time]{id=frame-time}, draw calls and loading assets |

## The components you add most

[Scenes, entities and components](../make/scenes-entities.md) teaches them, and [the components reference](../reference/components.md) lists every property with its range. The Inspector shows a name with spaces (**Play On Start**); the file, the commands and the scripts write it without (`PlayOnStart`). The table gives the properties to look at first, with the default of a new component.

| Component | Properties that matter first |
| --- | --- |
| `Transform` | `Translation` (0, 0, 0), `Rotation`, `Scale` (1, 1, 1), all relative to the parent |
| `Camera` | `Projection` (`Perspective`), `PerspectiveFOV` (60 degrees), `Primary` (true) |
| `MeshRenderer` | `Mesh`, `Material`, `CastShadows` (true) |
| `DirectionalLight` | `Color`, `Intensity` (3), `CastShadows` (true); shines along its forward direction |
| `PointLight` | `Intensity` (10), `Range` (10 metres), `CastShadows` (false) |
| `SpotLight` | `Intensity` (20), `Range` (15), `InnerConeAngle` (20), `OuterConeAngle` (30) |
| `RectLight` | `Intensity` (25), `Width` (1), `Height` (0.5), `Range` (10), `CastShadows` (false); a glowing rectangle that shines along its forward direction |
| `SkyLight` | `Source` (`EnvironmentMap`, `Procedural` or `Atmosphere`), `Intensity` (1), `ShowBackground` |
| `PostProcess` | `Tonemapper` (`Filmic`), `Exposure` (0), `AutoExposure` (true), `Bloom`, `AntiAliasing` |
| `RigidBody` | `Type` (`Dynamic`; or `Static`, `Kinematic`), `Mass` (1), `Friction` (0.5), `Restitution` (0), `IsTrigger`, `Layer` |
| `BoxCollider` | `HalfExtents` (0.5, 0.5, 0.5: half of the size on each axis), `Offset` |
| `SphereCollider` | `Radius` (0.5), `Offset` |
| `CapsuleCollider` | `Radius` (0.5), `HalfHeight` (0.5), `Offset` |
| `MeshCollider` | `Mesh`, `Convex` (true) |
| `CharacterController` | `Height` (1.8), `Radius` (0.3), `StepHeight` (0.35), `MaxSlopeDegrees` (45) |
| `AudioSource` | `Clip`, `Volume` (1), `Loop` (false), `PlayOnStart` (true), `Spatial` (true), `MaxDistance` (50) |
| `AudioListener` | `Active` (true): the ears of the game |
| `Animator` | `Skeleton`, `Controller`, `Clip`, `Speed` (1), `Loop` (true), `PlayOnStart` (true) |
| `Script` | Names the :term[script class]{id=script-class}; the fields are the class's own |
| `Text` | `Text`, `FontSize` (32), `ScreenSpace` (true), `ScreenAnchor` |
| `UICanvas` | `ScaleMode` (`ScaleWithScreen`), `ReferenceResolution` (1920 by 1080), `SortOrder` |
| `UIRect` | `AnchorMin`, `AnchorMax`, `Pivot`, `Position`, `Size`: where a UI element sits in its parent |
| `UIText`, `UIButton` | `UIText`: `Text`, `FontSize`, `Alignment`. `UIButton`: `EventTarget` |

## The script SDK

[Your first script](../make/first-script.md) and [the loop from a script's side](../make/script-loop.md) teach scripts; [the script reference](../reference/script-api.md) lists every call of the software development kit (SDK). A script is a class that derives from `Script`, registered with `ST_SCRIPT_CLASS(Name)` in a `.cpp` file. Inside its braces, `ST_SCRIPT_FIELD(Member)` makes a public member a field that the Inspector edits and the scene saves. A field has one of the types `bool`, `int32_t`, `float`, `glm::vec2`, `glm::vec3`, `glm::vec4`, `glm::quat`, `std::string`, `Entity` or `AssetHandle`.

The engine calls only the callbacks that your class overrides. The next table lists them; a frame runs `OnUpdate`, `OnFixedUpdate` and `OnLateUpdate` in that order, and the UI callbacks before `OnUpdate`.

| Callback | When it runs |
| --- | --- |
| `OnCreate()` | Once, before the first update; after a :term[hot reload]{id=hot-reload} `OnReload()` runs instead |
| `OnUpdate(float deltaTime)` | Every frame |
| `OnFixedUpdate(float fixedDeltaTime)` | Zero or more times a frame, at the fixed step |
| `OnLateUpdate(float deltaTime)` | Every frame, after the fixed updates |
| `OnDestroy()` | When the entity goes away, the script is removed or play stops |
| `OnCollisionEnter`, `OnCollisionExit` | A body starts or stops touching another |
| `OnTriggerEnter`, `OnTriggerExit` | The same, where one body is a trigger |
| `OnAnimationEvent(name)` | The animator passes an event of its state |
| `OnUIClick`, `OnUIValueChanged`, `OnUIFocusChanged`, `OnUISubmit` | The player uses a button, slider, toggle or input field |

The calls you reach for most are in the next table. A name with `::` is called on the class itself, with no object, as in `Time::GetDeltaTime()`; a name without it is called on an object that you hold, as in `entity.GetName()`.

| Class | Calls |
| --- | --- |
| `Entity` | `GetName`, `GetTag`, `SetActive`, `GetParent`, `GetChildren`, `Destroy`, `HasComponent`, `GetTransform`, `GetRigidBody`, `GetAnimator`, `GetUI` |
| `Entity` (any component) | `GetProperty<T>(component, property)` and `SetProperty(component, property, value)`, by the Inspector's names |
| `TransformComponent` | `GetTranslation`, `SetTranslation`, `GetWorldPosition`, `SetWorldPosition`, `GetEulerAngles`, `SetEulerAngles`, `GetForward`, `GetRight`, `GetUp` |
| `Scene` | `Scene::FindEntityByName`, `Scene::FindEntitiesByTag`, `Scene::CreateEntity`, `Scene::Instantiate`, `Scene::GetPrimaryCamera` |
| `Input` | `Input::IsKeyDown`, `Input::IsKeyPressed`, `Input::GetMousePosition`, `Input::GetMouseDelta`, `Input::GetActionValue`, `Input::IsActionPressed` |
| `Time` | `Time::GetDeltaTime`, `Time::GetFixedDeltaTime`, `Time::GetElapsedTime`, `Time::GetTimeScale`, `Time::SetTimeScale` |
| `Physics` | `Physics::Raycast`, `Physics::OverlapSphere`, `Physics::OverlapBox`, `Physics::GetLayerIndex` |
| `RigidBody` | `GetLinearVelocity`, `SetLinearVelocity`, `AddForce`, `AddImpulse`, `Teleport` |
| `CharacterController` | `Move`, `Jump`, `IsGrounded`, `Teleport`, `GetVelocity` |
| `Audio`, `AudioSource` | `Audio::PlayOneShot`, `Audio::SetMasterVolume`; `Play`, `Pause`, `Stop`, `IsPlaying` |
| `Animator` | `Play`, `CrossFade`, `SetFloat`, `SetBool`, `SetTrigger`, `GetCurrentState` |
| `UIElement` | `GetText`, `SetText`, `GetValue`, `SetValue`, `SetInteractable`, `Focus` |
| `Game` | `Game::Quit`, `Game::LoadScene`, `Game::ReloadScene`, `Game::WriteSaveFile`, `Game::ReadSaveText` |
| `Log` | `Log::Info`, `Log::Warn`, `Log::Error` |
| `Random`, `Timer` | `Seed`, `Range`, `Chance`; `Start`, `Update`, `IsRunning` |

## The conventions

[Positions, rotations and units](../make/transforms-units.md) teaches these rules, and [the notation page](../reference/notation.md) lists the symbols. A model that breaks one of them looks too large, upside down or backwards, so check them first when something looks wrong.

| Convention | What it means for you |
| --- | --- |
| Units | One unit is one metre; a character is about 1.8 m tall (the default `CharacterController` `Height`) |
| Up | The +Y axis points up |
| Forward | Cameras, lights and `GetForward()` look along -Z |
| Imported models | A glTF model faces +Z, so it looks backwards on a -Z forward; turn the model or compute its facing |
| Rotation in the Inspector and in commands | Euler angles in degrees, in the order pitch, yaw, roll |
| Rotation in a script | `SetEulerAngles` takes radians; `GetRotation` and `SetRotation` use a :term[quaternion]{id=quaternion} |
| Field of view | `PerspectiveFOV` is the vertical angle in degrees |

## The commands

[Commands from the command line](../make/commands.md) and [automated playtests](../make/automated-playtests.md) teach them; [the commands reference](../reference/commands.md) lists all :value{key="commands.count"} with their parameters. The editor registers every command as a method that `StrataCLI call <method> @file.json` runs, and the tool server for an artificial intelligence (AI) agent (`StrataCLI mcp`) offers the same commands. A command script is a JSON array of `{command, parameters, expect, bind}` steps that `StrataEditor --commands <file> --quit-after-commands` runs and then closes; it exits with code 1 when a step fails.

| Command | What it does |
| --- | --- |
| `project.create` | Makes a project in a folder (`template`: `empty` by default, or `basic3d`) |
| `scene.save` | Writes the edited scene to its file |
| `entity.create`, `entity.get`, `component.set` | Create an entity, read all its values, set component properties in one undo step |
| `prefab.instantiate` | Places a :term[prefab]{id=prefab-make} or a model in the scene |
| `script.build`, `script.reload`, `script.status` | Build the scripts, load them again, list classes, fields and errors |
| `play.start` | Starts play mode; `build: false` skips the script build, `paused: true` starts paused |
| `play.step` | While paused, runs `steps` fixed steps and answers when they ran |
| `play.simulate`, `play.pause`, `play.stop`, `play.state` | Run physics only, pause or resume, stop, report the mode |
| `input.key` | Taps a key for `steps` fixed steps; `action` can be `press` or `release` |
| `input.action` | Holds an input action, whatever its bindings |
| `input.sequence` | Plays timed input in fixed steps, with `events` and `observe` |
| `input.releaseAll` | Ends every held key, button and action |
| `viewport.capture` | Saves a picture to `path`; `camera`, `width`, `height` and `debugView` choose the view |
| `editor.activity.export` | Writes the session as a command script |
| `project.export` | Exports the game to `directory`; `prune` omits unused assets |
| `project.exportStatus` | Reports the running export or the last one |

## The runtime's options

The :term[runtime]{id=runtime} is the program that plays an exported game. [Exporting a game](../make/export.md) teaches the export, and [the worlds and runtime reference](../reference/worlds-runtime.md) holds the rest. An exported game runs through `StrataRuntime`, renamed to the game's name, which reads the `.stgame` file beside it. The options below start it from a terminal or a test. The runtime exits with code 1 when the game cannot start, and with code 2 when scripts crash in a headless run.

::include{file="options-runtime.md"}

## The project folder

[Project files](../make/project-files.md) teaches the folder and [the samples page](../make/samples.md) the finished games. The table lists what `project.create` writes and what you add. Never edit a scene, model or material file by hand: the editor and the commands write them.

| Path | What it holds | Version control |
| --- | --- | --- |
| `<Name>.stproj` | The project file: name, start scene, settings, the game's title and version | Keep it |
| `Assets/` | Scenes, prefabs, models, materials, textures and sounds, each with a `.meta` file beside it that holds its handle | Keep both files of each asset |
| `Scripts/` | The :term[script module]{id=script-module}: `CMakeLists.txt` and your `.cpp` files, with the example `Spinner.cpp` | Keep it |
| `.strata/` | What the editor makes for itself: the import `Cache`, the script builds in `Scripts/Build` and `Scripts/Bin`, `Saves`, `Trash`, `Recovery` and `Thumbnails` | Omit it |

The `.gitignore` that `Project::Create` writes lists `/.strata/`, so [version control with git](../basics/git.md) skips it from the first commit. Deleted assets wait in `.strata/Trash` for 30 days. When you create a project you choose a template, and when you open a sample the editor copies it, because a sample itself stays unchanged.

| Choice | Name in the editor | What you get |
| --- | --- | --- |
| Template `empty` | Empty | A project with no scene; the default |
| Template `basic3d` | Basic 3D | A lit start scene: camera, sun, sky, ground with a collider and post-processing |
| Sample `Tetris` | Tetris | The falling-block game, made by an agent: scripts, UI and sounds |
| Sample `ThirdPerson` | Third-Person Adventure | A robot on floating islands, with menus, saves and an attract mode |
| Sample `OpenWorld` | Open World | A 768 m island that streams in cells, with a day and night cycle |
| Sample `PhysicsPlayground` | Physics Playground | About 600 bodies, triggers, impact sounds and a ball pit |
| Sample `Showcase` | High Desert Outpost | The graphics reference scene at three times of day |

## Where it lives in Strata

- `StrataEditor/src/EditorLayer.cpp`: `RegisterBuiltinPanels` lists the panels; the toolbar and the global shortcuts (**Ctrl+P**, **Ctrl+Z**, **Ctrl+S**, **Ctrl+B**) are here.
- `StrataEditor/src/Panels/ViewportPanel.cpp`: the gizmo and framing keys and the chips of the **Scene** panel.
- `StrataEditor/src/UI/EditorActions.cpp`: the selection shortcuts, such as **Ctrl+D** and **Delete**.
- `Strata/src/Strata/Scene/ComponentRegistration.cpp`: the component registry that the components table follows; `reference/components` is its dump.
- `StrataScriptCore/Include/StrataScript/Script.h`: the callbacks, `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`.
- `StrataScriptCore/Include/StrataScript/Entity.h`: `Entity` and `TransformComponent`; the other :term[SDK]{id=sdk} headers are in the same folder.
- `StrataEditor/src/Editor/Commands/PlayCommands.cpp`: the `play` commands.
- `StrataEditor/src/Editor/EditorInputCommands.cpp`: the `input` commands.
- `StrataEditor/src/Editor/EditorViewportCommands.cpp`: `viewport.capture`.
- `StrataEditor/src/Editor/EditorScriptCommands.cpp`: the `script` commands.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: `project.create`, `project.templates` and `project.export`.
- `StrataEditor/src/Editor/ProjectTemplates.cpp`: the two templates.
- `Strata/src/Strata/Project/Project.cpp`: `Project::Create`, which writes the `.gitignore`.
- `Strata/src/Strata/Project/Project.h`: the folders of `.strata`.
- `StrataEditor/src/Editor/EditorContext.cpp`: the trash, the thumbnails and the saves of a game played in the editor.
- `StrataEditor/src/Editor/ScriptProject.cpp`: the files of a new script module.
- `Samples/Samples.json`: the five samples and their descriptions.
- `StrataRuntime/src/RuntimeApplication.cpp`: the runtime's options and exit codes.
- `StrataCLI/src/CLI/CliApplication.cpp`: the commands of `StrataCLI`.
