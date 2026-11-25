---
id: appendix/not-in-strata
title: "What Strata does not do, and how engines do it"
description: "An index of what Strata lacks, the evidence for each absence, the technique other engines use to fill it, and how to check a feature yourself."
kind: concept
size: L
tracks: []
needs: []
time: 55
learn:
  - id: three-kinds
    text: explain why a missing feature is a decision, planned work or work left to game code
  - id: four-approaches
    text: compare the four ways an engine can offer a feature, and say which one Strata uses
  - id: find-evidence
    text: find the evidence for or against a feature with a search of the engine's files
  - id: read-notes
    text: trace a line of a release's lists to a row of the index or to a feature's page
status: final
---

You have made games in another engine for three years. You open Strata, search for the menu that adds a particle system, and find none. You search the manual for "navigation mesh", "online play" and "toon shader" and find nothing there either.

Three questions follow. Does Strata lack these features, or have you missed where they hide? If it lacks them, did the makers decide so, or did they not get to it yet? And what would you do in a game that needs them?

This page answers those questions for every area of the engine. It lists what Strata does not do, names the page of this book that says so, and gives the evidence: a file or a search that you can run yourself. After each list it describes the general technique that engines use for the missing features, so that you know what you would build or fetch to fill the gap.

## A missing menu is not proof, and memory is not evidence

Two habits mislead. The first is to guess from memory: "an engine of this size surely has decals". The second is to read a missing menu as a missing feature. Both fail in both directions.

A feature can exist without the menu you expect. Strata has no switch for light culling, yet it limits the lights each pixel reads by clusters, and the page [Many lights](../light/many-lights.md) teaches how. A feature can also hide behind a command: you create an animation controller from the editor's command `animation.createController`, and the content browser's menus do not offer it. And a feature can look absent because it has another name. Water in Strata is a material with an index of refraction of 1.33, as `Strata/src/Strata/Renderer/Material.h` says in the comment of its `IOR` field, so a search for "water" in the code finds little.

The opposite mistake is as common. A menu may suggest a feature that is only half there. The editor has an **Add Component** list, but nothing in it adds a navigation mesh, because no such component exists.

So this book states no absence without evidence. The evidence is one of two kinds. The first is a search of the engine's files that finds nothing, together with a note on the matches that do exist. The second is a file that shows the choice: a table of modules, an `#error` line, or a sentence in the engine's own plans. In every case you can repeat the check, and the last section of this page shows how.

## An engine is a set of choices of scope

Every engine decides what it will do itself. A game engine could include a particle system, a physics solver, a network stack, a visual scripting language and a cloth solver. No team can build and keep all of these well, so each engine draws a line around its scope, and everything outside the line is an absence.

An absence is one of three things, and the three call for different answers.

1. **A decision with a reason.** The makers chose not to build it and wrote down why. Strata never renders below the native resolution of the screen. No setting lowers the resolution of the 3D image and scales it up, because that would blur the picture the engine wants to keep sharp.
2. **Planned work.** The engine's own documents list it for a later release. This book quotes such a plan and never gives a date or promises it. A plan can change, and a book that repeated a plan as a promise would be wrong the day the plan changes.
3. **Work left to game code or to engine changes.** The feature is a game's business (the steering of a guard, the camera of a story scene), or it needs a change to the engine's source that nobody has made.

The picture below sorts a missing feature by the evidence you find.

```mermaid caption="A missing feature is one of three things, and each has its own kind of evidence." alt="A diagram from a missing feature to three boxes: a decision with a reason, planned work in the engine's documents, and work left to game code or to engine changes."
flowchart LR
    Q["A feature is missing"] --> E{"What does the evidence say?"}
    E -->|"a written reason"| D["A decision"]
    E -->|"a line in the plans"| P["Planned work"]
    E -->|"neither"| G["Game code or an engine change"]
```

The question on the left is the one you asked. The answer on the right says what you can do: accept the decision, read the plan to see whether it mentions your feature, or write the feature yourself. The next section shows four ways in which engines make this last step cheaper.

Here is what a decision looks like in the engine's own words.

> Strata never renders below native resolution: no render scaling below 1, no dynamic resolution, no TAA or other temporal upscaling
> — `Docs/Roadmap.md`

And here is what a plan looks like. The notes of release 0.8.0 have a section headed "Not in this release", and its plans follow the words "Planned for later waves". An item in that list is a plan, and a plan is not a promise.

## Four ways to offer a feature

An engine can put a feature into a game in four ways. Each way answers a flaw of the one before it.

The first way is to build the feature into the engine. The engine's team writes it and ships it in the same program, so the editor, the saved files and the tests all know it. The flaw is size: every feature adds code to build, test and keep working, and a game that does not need it still carries it.

The second way answers that flaw. The engine ships without the feature, and a game uses an outside library: one made by another team, such as a sound mixer or a physics solver, that the game links beside the engine. The team of the engine writes less, and the library's makers know their field well. The flaw is the seam: the library has its own data, its own tools and its own idea of time, and someone must connect it to the scene and the editor.

The third way is the extension loaded at run time. The engine defines an interface, and a file that the program loads while it starts, or while it runs, adds the feature. Many people can extend the engine without changing its source. The flaw is the interface itself: it must stay stable for years, an extension written for one version can break in the next, and an extension that crashes takes the whole program with it.

The fourth way is to leave the feature to game code. The engine offers the pieces (entities, a place to put logic, ways to draw and to play sound) and the game builds the feature on them. Nothing is added to the engine, and a game gets exactly the feature it needs. The flaw is repeated work: every game that needs a navigation mesh writes one, and the editor does not know it.

| Approach | Cost to the engine's team | Quality for the game | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Built in | High: write, test and keep it | Consistent, with editor support | The engine grows | Unity's built-in particle system; Godot's particle nodes |
| Outside library beside the engine | Low: write the connection | Depends on the connection | Two sets of data and tools | Sound libraries such as Wwise and FMOD |
| Extension loaded at run time | Medium: keep an interface stable | Varies by extension | Versions, crashes, trust | Unreal Engine's `plugins`; Godot's native extensions |
| Left to game code | None | Fits one game | Each game repeats it | Hand-written game logic in any engine |

:::elsewhere[Engines that load extensions]
Godot loads native code at run time through its `GDExtension` mechanism, and its documentation says that such code runs inside the engine's own process. Unreal Engine groups code into units that the editor or the game loads at start, and calls them `plugins`. Unity offers packages, which add features as files of source or compiled code in the project. The sources are in Further reading.
:::

## Strata chooses compile-time modules and script modules

Strata uses the first and the fourth way, and it refuses the third for the engine itself. The engine is a set of modules that the build chooses. The file `Strata/src/Strata/Engine/BuiltinModules.cpp` holds a table of them: `Input`, `Scene` and `Renderer` are always present, and `Physics`, `Audio` and `Animation` appear only when the build defines `ST_WITH_PHYSICS`, `ST_WITH_AUDIO` or `ST_WITH_ANIMATION`. The modules `Scripting`, `World` and `GameUI` appear in every build. The page [Layers and registries](../core/layers-registries.md) teaches how a module plugs into the engine.

A game's own logic is not an engine module. It lives in a **script module**, a shared library (a file of compiled code that a program can load while it runs) that you build apart from the engine and that the engine loads. That is the third way, offered to games only: the module sees the engine through a small C interface and never links the engine's code. The page [Why scripts](../scripting/why-scripts.md) teaches why. A crash in a script is contained and the module can be rebuilt while the game runs.

A search shows that no other file loads code at run time. The search `git grep -lw DynamicLibrary -- Strata/src` lists the files that name the loader class. They are its own files, the script module code (`Strata/src/Strata/Project/Project.cpp` among them), and `Strata/src/Platform/Vulkan/VulkanLoader.cpp`, which loads the graphics driver. Nothing else loads an engine extension.

:::why[Why no engine extensions at run time?]
An extension that runs in the engine's process can read and write any engine memory, so one bug crashes the editor and may corrupt a scene. Strata already pays for a stable boundary once, for scripts: plain C data, guarded calls, a version number. A second boundary for the engine's inner types would cost far more, because those types change with every release. The price is that a game cannot add, for example, a particle system to the renderer without changing the engine's source and building it.
:::

The choice costs something when you want a feature. If the feature is absent, three roads remain. Write it in a script module, if it is game logic. Change the engine and rebuild, if it needs the renderer or the editor. Or read the plans and wait.

The index below helps you to choose.

:::example[Does Strata have particles?]
Follow your first question from the start. You open the index below and find the row "Particles, trails and decals" in the rendering table. Its evidence cell sends you to this example, which searches the engine's source and shaders for the words of the feature.

Run the search yourself. The command below searches for three words in the engine's source and in its shader folder. Look at what it prints: two lines.

```sh
git grep -ni -e particle -e decal -e emitter -- Strata/src Strata/shaders
```

The first is a comment in `Strata/src/Strata/Audio/AudioSystem.cpp` about a pooled sound `emitter`, an entity that plays sounds. The second is a comment in `Strata/src/Strata/Renderer/RendererComponents.h` that calls a glowing surface an `emitter`. Neither is a particle feature. A search for a common word can match something that is not the feature.

Search for the word "trail" next, with `git grep -niwE "trails?" -- Strata/src`. It finds three lines in `Strata/src/Strata/Renderer/RendererComponents.cpp`, and each is a tooltip of the anti-aliasing settings that says moving objects leave "trails" when the image smears. None is a feature.

The row names the page that says it ([Frame tour](../gpu/frame-tour.md)), and the plans agree: the 0.8.0 notes list "particles, trails and decals" under what is planned for later waves, so the kind is planned work. Strata's choice of scope then answers your last question. A particle system would be game code (a script that moves many small entities) or an engine change (a pass in the renderer). No extension can add it to the engine at run time.
:::

## The index, area by area

Each table below has one row for an absence. The columns are the feature, the page of this book that teaches the area, and the evidence. Where a search is named, it ran in a copy of the engine's files at the version this book describes, and a search that "finds nothing" found no line at all. After each table comes the technique that other engines use. The index is not complete: it holds the rows a reader asks about most, and a feature that has no row is not thereby present.

### Assets, core and platform

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Import of `.obj` and `.fbx` models; models are glTF only | [Models and glTF](../assets/models-gltf.md) | `AssetImporters.cpp` in `Strata/src/Strata/Asset/` registers the texture, glTF, audio clip, font and color lookup importers beside the native ones |
| Engine extensions loaded at run time | [Layers and registries](../core/layers-registries.md) | the module table of `Strata/src/Strata/Engine/BuiltinModules.cpp`; the search above |
| A build without scripting | [Layers and registries](../core/layers-registries.md) | `Scripting` stands in the table without an `ST_WITH_` condition |
| Targets other than Windows, Linux and macOS | [The platform layer](../core/platform.md) | `Strata/src/Strata/Core/PlatformDetection.h` ends in an `#error` for every other target |
| Work stealing, fibers and a frame task graph | [Jobs](../core/jobs.md) | `git grep -ni fiber -- Strata/src` finds nothing; `Docs/Roadmap.md` lists a second job system as later work, to be built once the perf tests show a need |
| A crash handler for the engine's own crashes | [Debugging the engine](../core/debugging.md) | a search for `MiniDumpWriteDump`, `SetUnhandledExceptionFilter` and `set_terminate` in the engine, editor and runtime finds nothing |

Most engines solve the asset questions with a converter and a cache. A **model** file from a modelling program is read by an importer, converted to the engine's own compact form once, and stored beside a small record of the source. Strata does this for glTF alone. One format keeps the list of importers short, while many formats disagree about units, axes and materials. Engines that read `.fbx` files usually rely on a library from the file's maker.

Work stealing and fibers answer a different problem. A job system with one shared queue makes every worker fight for the queue. With work stealing, each worker has its own queue and idle workers take work from a busy one. Fibers let a job pause in the middle without blocking its thread.

Crash handling is usually a small program or a signal handler that writes a memory dump when the process dies, so that the next start can offer to send it.

### Scenes, prefabs and editing

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Nested prefabs and prefab variants | [Prefabs](../make/prefabs.md) | `StripLinks` in `Strata/src/Strata/Scene/PrefabInstances.h` removes inner links when a prefab is made from linked entities |
| A prefab edit mode | [Prefabs](../make/prefabs.md) | a prefab changes through an instance and its apply step; the 0.8.0 notes list the mode as planned |

A prefab is a saved group of entities that a scene can place many times. The usual technique for nesting is a reference: a prefab holds a link to another prefab together with the values it overrides, and the engine resolves the links when it loads. A variant is a prefab that points to a base prefab and keeps only its differences. The difficulty is the overrides: when the base changes, each difference must still find the thing it changed, so engines give every entity a stable identity inside the prefab.

### Rendering

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Particles, trails and decals | [Frame tour](../gpu/frame-tour.md) | the worked example above |
| A terrain system with sculpting and painting | [Large worlds](../make/large-worlds.md) | the word "terrain" stands only in comments of `Strata/src`; the sample terrains are meshes that `Tools/GenerateIslandTerrain.py` makes |
| Multiple-sample anti-aliasing (MSAA) and supersampling | [Spatial anti-aliasing](../image/spatial-aa.md) | `Strata/src/Strata/Renderer/SceneRenderer.cpp` reports an error for a target whose sample count is not one; the 0.8.0 notes list MSAA and supersampling of still images as planned |
| Disk lights | [Lights: the sun, points and spots](../light/lights.md) | 0.8.0 adds rectangle lights alone; its notes list disk lights as planned |
| Material layers that blend, with wetness | [Strata's material model](../light/materials.md) | the coat and glass layers are fixed parts of one material; the 0.8.0 notes list blended layers as planned |
| Rendering below native resolution | [Quality settings](../image/quality-settings.md) | a decision; the quotation above |
| High dynamic range (HDR) display output | [Encoding](../image/encoding.md) | `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp` asks for a `UNORM` back buffer in the sRGB color space |
| Hardware ray tracing | [The problem of indirect light](../indirect/problem.md) | a search for ray tracing terms in `Strata/src` and `Strata/shaders` finds nothing |
| Lightmaps and baked global illumination | [The problem of indirect light](../indirect/problem.md) | `git grep -ni lightmap -- Strata/src Strata/shaders` finds nothing; reflection probes are the only bake |
| Mesh shaders and a render graph | [GPU-driven drawing](../draw/gpu-driven.md) | a search for `meshlet`, `RenderGraph` and `FrameGraph` finds nothing |
| Toon shading | [Materials](../light/materials.md) | a search for toon, cel and hatching terms finds nothing; the only outlines are the selection outline and the outlines of text |
| A second view (split screen, a mirror, a small map) | [Frame tour](../gpu/frame-tour.md) | `Scene::GetPrimaryCameraEntity` in `Strata/src/Strata/Scene/Scene.cpp` returns the first active primary camera |

A particle system updates thousands of tiny points each frame, often on the graphics card, and draws each as a flat square that faces the camera; a billboard is such a square. A trail is a ribbon that follows a moving point. A **decal** projects a texture onto the surfaces inside a box, which is how bullet holes and stains are drawn. These three share one design: data in a compact buffer, a pass that updates it and a pass that draws it, with blending that needs sorting or a trick for order.

Anti-aliasing smooths jagged edges. MSAA takes several coverage samples per pixel at the edges of triangles, which is cheap but does not help shaders that shimmer inside a surface. Supersampling renders more pixels than the screen holds and averages them. Engines that render below the screen's resolution and scale the image up trade sharpness for speed; Strata declined that trade.

A light with a surface, such as a rectangle or a disk, gives soft highlights and shadows, and each shape needs its own way to sum the light over its face. A layered material blends two materials by a mask, such as dry stone under a film of water, so that rain can darken a street without a second mesh.

Ray tracing follows a ray through the scene to find what it hits, which gives exact reflections and shadows. It needs a structure that stores the scene's triangles for fast queries, and a graphics card that supports it.

A **lightmap** is a texture that stores the indirect light of a static scene, computed once before the game runs. It costs nothing per frame, but it cannot follow a moving light.

Mesh shaders replace the fixed steps that read vertices with programs that work on small groups of triangles, which suits skipping hidden groups on the graphics card. A render graph is a list of passes with the resources each reads and writes, from which the engine works out the order and the memory. Strata orders its passes by hand in `SceneRenderer::RenderFrame`, which is simple to read and does not scale to hundreds of passes.

Toon shading replaces the smooth light of a physical material with a few flat bands and draws an outline around objects. A second view draws the scene again from another camera into a texture, which doubles the cost of that part of the frame. Split screen shares the screen between two such views.

### Physics

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Joints, ragdolls and vehicles | [Why a physics engine](../physics/why.md) | a search for "joint" in `Strata/src/Strata/Physics` finds nothing (elsewhere it names skeleton joints); the 0.8.0 notes list them as planned |
| Shape sweeps in the public query application programming interface (API) | [Queries](../physics/queries.md) | only `Strata/src/Strata/Physics/CharacterControllers.cpp` calls `b3World_CastMover`; scripts cast rays |
| Cloth, soft bodies, fluids and destruction | [Why a physics engine](../physics/why.md) | a search for cloth, soft body, fluid and fracture in `Strata/src` finds nothing; "destruction" matches only the removal of objects in code |
| Triggers that see triangle-mesh colliders | [Contacts and triggers](../physics/contacts-triggers.md) | the 0.8.0 notes list it under known issues |

A joint is a rule that links two bodies: a hinge lets a door swing, a ball joint lets a shoulder turn. Ragdolls link many bodies with such joints and replace an animated skeleton when a character falls. A sweep moves a shape along a line and reports the first thing it touches, which is a ray with thickness; games use it to ask whether a character can step forward. Cloth and soft bodies simulate many linked points with springs, and fluids simulate particles that push on each other, so each is a different solver from the one that moves boxes. Engines usually take these from a physics library that has them or leave them to specialists.

### Animation

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Blend trees, layers, inverse kinematics, morph targets and clip compression | [Animation limits](../animation/limits.md) | a search of `Strata/src/Strata/Animation` for these terms finds nothing |
| Additive clips, sync markers, motion matching | [Animation limits](../animation/limits.md) | the same kind of search finds nothing |

A blend tree mixes clips by a number, such as walking toward running by speed. Inverse kinematics works backward: given where a hand must reach, it finds the joint angles, which keeps a foot on uneven ground. A morph target stores a second shape of a mesh, usually a face, and blends between shapes. An additive clip stores a difference from a pose and adds it to another motion, so a character can breathe while it walks. Motion matching searches a large library of recorded motion for the frame that best continues the present movement, which replaces most hand-made state machines at the cost of memory and a good library.

### Audio

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Buses, effects, `reverb` and head-related filtering | [The audio engine](../audio/engine.md) | `Strata/src/Strata/Audio` holds no sound group, `reverb` or filter node |
| Streaming a long clip from disk | [Clips, voices and sources](../audio/clips-voices-sources.md) | `Strata/src/Strata/Audio/AudioClip.h`: the `Streamed` mode decodes as it plays, but from the whole encoded file kept in memory |

A **bus** is a mixing channel: all footsteps go to one bus and the game lowers that bus with a single control. Effects such as `reverb` sit on a bus and make a sound seem to come from a hall or a tunnel. Head-related filtering changes a sound slightly for each ear so that the player hears it placed in space.

Streaming reads a long file in small pieces as it plays, so a ten-minute song does not sit in memory. Engines pair it with a mixer that has a limit on voices and drops the quiet ones first.

### Input

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Touch input | [How input works](../input/how-input-works.md) | `Strata/src/Strata/Input` and `Strata/src/Platform/GLFW` hold no touch code |
| Force feedback | [Gamepads](../input/gamepads.md) | a search for rumble and vibration in the engine and the script folder finds nothing |
| Chords, modifiers and processors on input actions | [Input actions](../input/actions.md) | `Strata/src/Strata/Input/InputActionSet.cpp` refuses every binding but keys, mouse buttons, gamepad controls and composites of buttons (`1D:` and `2D:`); the 0.8.0 notes list the gap |

Touch input arrives as several points that start, move and end, so an engine must track each by number and turn gestures into events. Force feedback sends a strength and a duration to the motors of a pad. A chord is two or more controls pressed together, and a processor changes a value on its way from the device to the game, for example a dead zone around the center of a stick. Engines with action systems treat these as stages in a pipeline between the device and the action.

### Scripting

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Visual scripting | [Why scripts](../scripting/why-scripts.md) | no node or graph scripting in `Strata/src` or `StrataEditor/src` |
| Script languages other than C++ | [Why scripts](../scripting/why-scripts.md) | no Lua, `Mono` or `.NET` runtime code in `Strata/src` |
| Coroutines | [Timers and events](../make/timers-events.md) | a search for `coroutine` and `co_await` in `Strata/src` and `StrataScriptCore` finds nothing; timers and state machines do that work |

Visual scripting shows logic as boxes joined by wires, so people who do not write code can build behavior. The cost is that big graphs are hard to read and compare. An embedded language such as Lua runs inside the engine and can change without rebuilding.

A coroutine is a function that can stop in the middle, wait for a time or an event and continue later. A sequence such as "wait two seconds, then open the door" then reads as straight lines.

### Game user interface

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Scroll views, drop-downs, rich text and multi-line input | [What the game user interface does](../ui/what-game-ui-does.md) | `Strata/src/Strata/GameUI/GameUIComponents.h` holds no such widget; a mask clips a list |
| Translation of text and right-to-left text | [Text](../ui/text.md) | a search for `localiz` in `Strata/src` finds nothing |

Translation keeps every sentence a player reads in a table keyed by an identifier and picks the column for the player's language. Right-to-left text needs a layout that reverses the order of lines and handles words of both directions in one line. Engines add both at the text layer, so that widgets never hold a literal sentence.

### Editor, export and automation

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Panels torn out into windows of their own | [The editor shell](../editor-ui/shell.md) | one main viewport only; `Docs/Roadmap.md` lists it as later work |
| A box in the editor to type and run any command | [Commands](../make/commands.md) | `EditorLayer::DrawMenuBar` in `StrataEditor/src/EditorLayer.cpp` offers none |
| Command scripts and simulated input in an exported game | [Automated playtests](../make/automated-playtests.md) | they run in the editor only; `StrataRuntime/src` reads no command script |
| A ghost of the mesh while an asset is dragged into the Scene view | [Placing content](../editor/placement.md) | `StrataEditor/src/Editor/PlacementPreview.h` draws the box where the asset lands; the 0.8.0 notes list a mesh ghost as planned |
| Exports for another platform, signed exports | [Exporting a game](../make/export.md) | the export copies the runtime that sits next to the editor |
| In-game consoles and console variables | [Play, test, debug](../make/play-test-debug.md) | no match in `Strata/src`, `StrataRuntime/src` or `StrataScriptCore` |

An in-game console is a text line that a developer opens in the running game to call functions and change settings, and a console variable is a named setting that it reads and writes. Engines register each variable once, with a default and a help line. Exports for another platform need that platform's compiler and runtime, which is why an engine usually exports from a machine of the target's kind or ships cross-compilers.

### Gameplay

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Networking for games | [Json-RPC](../automation/json-rpc.md) | the network code is the tooling layer `Network` in `StrataTests/Architecture/Layers.json`, which games never link |
| Game artificial intelligence (AI): steering, paths and navigation meshes | [Patterns](../make/patterns.md) | no match in `Strata/src` or `StrataScriptCore`; scripts do it |
| A `sequencer` for scripted camera scenes | [Characters and cameras](../make/characters-cameras.md) | the Showcase's camera tour is a script, `Samples/Showcase/Scripts/TourPath.h` |

A `sequencer` stores tracks over time, such as a camera position, an animation to play and a sound to start, and a player runs them in step. Engines with one let a designer edit a camera scene in the editor instead of writing code. Networking and artificial intelligence are subjects of their own. A game that needs them builds them in script code, on a library of its choice.

### Building, testing and the GPU

| Not in Strata | Page | Evidence |
| --- | --- | --- |
| Asynchronous compute | [Compute](../gpu/compute.md) | `git grep -n "CommandQueue::Compute" -- Strata/src` finds nothing |
| Unity builds | [Flags and portability](../engineering/flags-portability.md) | a search for `UNITY_BUILD` in the CMake files finds nothing |
| A package manager such as `vcpkg` or `Conan` | [Third-party code](../engineering/third-party.md) | no `vcpkg` or `conanfile` file in the repository |
| Measured line coverage | [Testing](../engineering/testing.md) | a search for coverage tools in the CMake files, the workflows and `Tools` finds nothing |
| `Fuzzers` and `sanitizer` builds | [Continuous integration](../engineering/ci.md) | a search for `fsanitize` in the build files finds nothing |
| Signed release archives | [Releasing](../engineering/releasing.md) | a search for `signtool` and `codesign` finds nothing |

A unity build joins many source files into one before compiling, which cuts the time spent reading the same headers. A package manager downloads a library at the version a project names, where Strata pins its libraries as git submodules: copies of each library's code at a fixed version inside the engine's repository. Line coverage counts the lines that tests ran.

A `fuzzer` feeds a program changing random input and keeps the inputs that reach new code. A `sanitizer` is a compiler mode that halts on memory errors. Signing proves that an archive comes from its maker. Asynchronous compute runs graphics work and compute work at the same time on separate queues of the graphics card.

## Reading a release's own lists

A release's notes have two lists that bear on this page: "Known issues" and "Not in this release". The version this book describes is release 0.8.0, and its notes are `Docs/Releases/0.8.0.md`, where "Not in this release" closes the known issues. Read each line in turn and sort it into one of four places.

1. The line is an absence: it maps to a row of the tables above. "Particles, trails and decals" and the import of `.obj` and `.fbx` models are examples.
2. The line is a limit of a feature that Strata has: the page of that feature states it. "Triggers do not see triangle-mesh colliders" is a limit of triggers, and the physics page says so.
3. The line is no longer true: drop it. The notes of an older release show how this happens. 0.7.0 said that the fixed step and gravity remain settings of each scene. The project's `Scene.Timing` section then gained a `FixedRate` field that overrides the step of every scene, as `Strata/src/Strata/Scene/ProjectSceneTiming.h` says, and the 0.8.0 line keeps only gravity. 0.7.0 also listed a graphical showcase sample as planned, and the `Showcase` sample landed afterward.
4. The line holds, but a document beside it says more than the programs do. 0.8.0 says that an endless loop in a script blocks the editor or the game, and that is still true. The engine's developer guide adds that the script watchdog, a timer that notices a call running too long, reports such calls. No editor or runtime program sets a watchdog timeout (only tests call `SetWatchdogTimeout`), so nothing is logged.

One line needs care. The list "Not in this release" names a mesh ghost for drops. The Scene view already draws a ghost while you drag an asset into it, a box where the asset will land, so the line cannot become a row that says "no ghost". The row above says that the ghost is a box, not the mesh. Read what the line means before you place it.

## What this index cannot do

The index is a snapshot. It states what the engine lacks at one version, and the next release may add a row's feature and so remove the row. A page of this book that makes a claim about a missing feature must be checked again when the engine moves.

The search method has limits. A search that finds nothing proves that the words are absent, not that the idea is. A feature written under another name escapes the search, which is why the evidence cells name the words searched and why a careful reader tries two or three other words for the idea. The index also omits the caps and ranges of features Strata has; the reference pages hold those.

## Common mistakes

- **Stating an absence from memory.** Symptom: a sentence such as "Strata has no light culling" that a search proves wrong. Fix: search the engine's files first and write the search beside the claim.
- **Reading a cap as an absence.** Symptom: "Strata has no more than four gamepads" turned into "Strata has no gamepads". A limit belongs to the feature's page. Fix: ask whether the feature exists, then read its limits on its own page.
- **Repeating a plan as a promise.** Symptom: "the next release adds particles". Fix: quote the plan and add no date.
- **Trusting an old release's known issue.** Symptom: believing the 0.7.0 line on the fixed step. Fix: check each line against the files of the version you use.
- **Treating a command-only feature as missing.** Symptom: "there is no way to create an animation controller" when the command `animation.createController` does it. Fix: list the commands before you decide.
- **Counting every match as the feature.** Symptom: three "trail" matches taken for a trail renderer. Fix: read each match and name what it is.

## Summary

- A missing feature is a decision with a reason, planned work in the engine's documents, or work left to game code and engine changes, and each kind has its own evidence.
- An engine offers a feature by building it in, by a library from another team beside it, by an extension loaded at run time or by leaving it to game code. Strata builds modules in at compile time and loads only script modules at run time.
- To find evidence for a feature, search the engine's files for its words and for other words of the idea, and read every match.
- Each line of a release's lists is an absence with a row, a limit of an existing feature, a line no longer true, or a true line that another document describes wrongly.

## Check yourself

1. A friend says that Strata cannot limit the lights that reach a pixel because the editor has no switch for it. Which mistake is this?

   - A. Reading a cap as an absence.
   - B. Reading a missing menu as a missing feature.
   - C. Repeating a plan as a promise.
   - D. Taking an old known issue as true.

   :::answer{tests="three-kinds find-evidence"}
   The answer is B. The editor has no switch, but the engine limits the lights of each pixel by clusters, which the page on many lights teaches. Option A is wrong because no cap is involved. Option C is wrong because nobody quoted a plan. Option D is wrong because no release note is involved.
   :::

2. Which approach does Strata use for the logic of a game, and which does it refuse for the engine itself?

   :::answer{tests="four-approaches"}
   A game's logic is left to game code, in script modules that the engine loads while it runs. The engine refuses extensions loaded at run time: its modules are chosen when it is built, with the `ST_WITH_` switches. The reason is that an extension runs in the engine's process and needs a stable interface for the engine's inner types.
   :::

3. The 0.8.0 notes list "terrain with sculpting and painting" under what is planned. Is the absence a decision, planned work or work left to game code, and how does the page know?

   :::answer{tests="three-kinds"}
   The absence is planned work, because the engine's own document lists it under what is planned for later waves. A decision would carry a written reason, as the rule on native resolution does. The page quotes the plan and gives no date.
   :::

4. A search for "cloud" in `Strata/src` finds three comments: two about files stored in a cloud service, and one in the presets of the sky. Does Strata have clouds in its sky?

   :::answer{tests="find-evidence"}
   The first two matches are not the feature: they concern cloud folders for files. The third, in `Strata/src/Strata/Renderer/SkyPresets.cpp`, says that the atmosphere has no clouds, so the sky has none. Read each match and name what it is. A search on its own does not prove an absence, so read the sky's own page too, which says that the `Overcast` preset is a nearly uniform procedural sky.
   :::

5. A line of 0.8.0 says that a script's endless loop blocks the editor or the game. The engine's developer guide adds that the script watchdog reports long calls. What do the files at this version show?

   :::answer{tests="read-notes"}
   The blocking is true, but no editor or runtime program sets the watchdog timeout, so nothing reports the loop and nothing is logged. Only tests call `SetWatchdogTimeout`. The line belongs in the fourth place of the list above: it holds, but the report needs a timeout that no program sets.
   :::

## Exercises

1. **Basic.** Place each of these absences in one of the three kinds, with a one-line reason: rendering below native resolution; joints and ragdolls; a navigation mesh.

   :::answer[Worked solution]{tests="three-kinds"}
   Rendering below native resolution is a decision: `Docs/Roadmap.md` states that Strata never does it. Joints and ragdolls are planned work: the 0.8.0 notes list them for later waves. A navigation mesh is left to game code: no engine module has it, and scripts do the work. Each reason names its evidence, which is the point of the exercise.
   :::

2. **Medium.** Run the two queries that list the editor's components and commands, then search for three words in them. This is the done exercise: the file named in its answer runs both queries as a command script.

   :::answer[Worked solution]{tests="find-evidence" solution="tutorials/appendix/not-in-strata/exercise-2.tutorial.json"}
   Open a project and run the script of the solution file. It sends `component.list` and `editor.commands`, and each step checks that the answer has a first entry. A step can only compare a value, so it cannot say that an entry is missing. You do that part.

   Write both results to files with the command line client. Then search the files for "particle", "navigation" and "network", and read every match. Check at the version you use whether any component or command is a particle system, a navigation mesh or a network session of a game. At this book's version none is, and the page on automation explains that its network code serves the editor only.
   :::

3. **Hard.** A game needs particles for smoke. Weigh the four approaches under Strata's choice of scope: what does each cost you, and which would you pick?

   :::answer[Worked solution]{tests="four-approaches three-kinds"}
   Built in: you change the renderer's source and build the engine yourself, which fits smoke that must look good but costs work in every later release. Outside library: you link a particle library, and you write the connection to the scene and the renderer, which Strata has no place for beyond the engine's source. Extension loaded at run time: not possible, because only script modules load, and they see only the script interface. Game code: a script moves a pool of small entities each frame, which needs no engine change but draws every particle as an entity and does not scale to thousands. For a few dozen puffs, pick game code; for a large effect, pick the engine change.
   :::

## Where it lives in Strata

- The module table: `Strata/src/Strata/Engine/BuiltinModules.cpp`, and the `ST_WITH_` switches that the build defines.
- Script modules: `Strata/src/Strata/Scripting/ScriptModule.cpp` and the interface in `StrataScriptCore/`.
- The queries of the exercise: the commands `component.list` and `editor.commands`.
- The planned work: `Docs/Roadmap.md` and the release notes in `Docs/Releases/`.

## Further reading

- *Game Engine Architecture* by Jason Gregory: how engines decide what to build in and what to buy; intermediate.
- *Real-Time Rendering* by Tomas Akenine-Moller, Eric Haines and Naty Hoffman: the techniques named in the rendering section; intermediate to advanced.
- The Godot documentation on GDExtension and the Unity documentation on packages (docs.godotengine.org, docs.unity3d.com): how two engines load extensions; beginner.
- The Unreal Engine documentation on plugins: how a third engine does it; beginner.
- *Game Programming Patterns* by Robert Nystrom (gameprogrammingpatterns.com): the patterns of game code that stands in for features; beginner.
- Glenn Fiedler's articles on game networking (gafferongames.com): the technique behind networked games; intermediate.
