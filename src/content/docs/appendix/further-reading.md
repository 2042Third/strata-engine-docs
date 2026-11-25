---
id: appendix/further-reading
title: "Further reading"
description: "Where to read next: the engine's own documents, the books and sites that serve the whole field, and the sources of every part of the book."
kind: reference
size: M
tracks: []
needs: []
status: final
---

This page lists where to read after the book, and where to read beside it. Each source has one line that says what it gives and its level. **Beginner** means you need only the book's first parts. **Intermediate** means you have written programs of some size. **Advanced** means you read papers or source code for pleasure, or you are willing to.

The page has three groups. The first holds the engine's own documents, which are the source of truth about Strata: where this book and a document disagree, trust the document. The second holds the books and sites that teach the whole field of game engines, from several authors. The third holds, for each part of the book, the sources its pages cite most often. A page's own `## Further reading` section lists every source that page used.

Sources marked "not fetched" were named by a reviewer or from memory, and the book's authors have not opened them for this edition. Check their address before you rely on them.

## Further reading

### The engine's own documents

A release archive holds `README.md`, `ThirdPartyNotices.md`, the folder `Docs/Manual/`, the samples with their `README.md` files, and a folder `Skills/` with three of the five skills, each at `Skills/<name>/SKILL.md`. Every other document below is only in the source repository. The book pages named at the end of a line draw on that document.

- `Docs/README.md`: the index of the guides, with a paragraph on what each one holds; beginner. Start here in the source repository.
- `AGENTS.md`: the rules that each change to the engine obeys, with a short list per area of what to do and what to avoid; intermediate. It serves contributors and agents. Backs [contributing](../engineering/contributing.md) and [layers and registries](../core/layers-registries.md).
- `Docs/Architecture.md`: the targets, the engine modules, the frame loop, the threads, the asset pipeline, streaming, the render scene and the editor; intermediate. Backs [the map of the engine](../core/map.md), [the frame loop](../core/frame-loop.md) and [engine modules](../core/engine-modules.md).
- `Docs/DeveloperGuide.md`: the details behind each rule of `AGENTS.md`, area by area: builds, tests, assets, scripting, the editor, rendering and automation; advanced. Backs [building](../engineering/building.md), [testing](../engineering/testing.md) and [the feature test](../engineering/feature-test.md).
- `Docs/Roadmap.md`: what Strata is meant to be, the waves of work and what each landed wave delivered; beginner. Backs [what an engine is](../start/what-an-engine-is.md).
- `Docs/Releases/`: the release notes of the versions 0.3.0 to 0.8.0 and `PackageReadme.md`, which the archive installs as its `README.md`; beginner. Backs [releasing](../engineering/releasing.md).
- `Docs/Plans/`: the plans, release notes and specifications of waves 7 and 8, which many pages cite; advanced. Source repository only.
- `Docs/Manual/AntiAliasing.md`: FXAA, morphological anti-aliasing and TAA, and when to use each; beginner. Backs [spatial anti-aliasing](../image/spatial-aa.md) and [temporal anti-aliasing](../image/taa.md).
- `Docs/Manual/Camera.md`: exposure, the tone curve, color, bloom and the other effects of a camera's image; beginner. Backs [exposure](../image/exposure.md) and [tone mapping](../image/tone-mapping.md).
- `Docs/Manual/GameUI.md`: menus, HUDs, anchors, scale modes and the look of images and texts; beginner. Backs [what game UI does](../ui/what-game-ui-does.md).
- `Docs/Manual/GameView.md`: playing and testing in the editor, resolutions, input, pausing and stepping; beginner. Backs [play, test and debug](../make/play-test-debug.md).
- `Docs/Manual/Graphics.md`: what graphics quality spends and how to choose it; beginner. Backs [quality](../make/quality.md).
- `Docs/Manual/Lighting.md`: lights and their units, exposure, the sky and fog; beginner. Backs [lighting](../make/lighting.md).
- `Docs/Manual/Prefabs.md`: making prefabs, placing instances, overrides and unpacking; beginner. Backs [prefabs](../make/prefabs.md).
- `Docs/Manual/Scripting.md`: creating, building, debugging and hot reloading scripts; beginner. Backs [your first script](../make/first-script.md).
- `Docs/Manual/Settings.md`: project settings and preferences, and why Strata keeps them apart; beginner. Backs [settings](../reference/settings.md).
- `Docs/Manual/Worlds.md`: worlds of streamed cells, editing, cooking, exporting and their limits; intermediate. Backs [large worlds](../make/large-worlds.md).
- `Samples/Tetris/README.md`, `Samples/ThirdPerson/README.md`, `Samples/OpenWorld/README.md` and `Samples/PhysicsPlayground/README.md`: each has a section "How it was made", which tells how an agent built that game through the editor; intermediate. In the archive. Backs [the samples](../make/samples.md).
- `.claude/skills/strata-editor-automation/SKILL.md`: how to start an editor, list its commands and drive it from outside; intermediate. In the archive. Backs [working with an agent](../make/with-an-agent.md) and [agents](../automation/agents.md).
- `.claude/skills/strata-make-a-game/SKILL.md`: a playbook that takes an agent from an empty project to an exported game; intermediate. In the archive. Backs [working with an agent](../make/with-an-agent.md).
- `.claude/skills/strata-scripting/SKILL.md`: the lifecycle of scripts and the whole gameplay interface; intermediate. In the archive. Backs [your first script](../make/first-script.md).
- `.claude/skills/strata-add-component/SKILL.md`: the steps that add a component so that it is saved, editable, scriptable and tested; advanced. Source repository only.
- `.claude/skills/strata-build-test/SKILL.md`: building, running the tests and checking a change in a clean copy; advanced. Source repository only.
- The section "Connect an AI agent" of `README.md` in the archive: the exact command that connects Claude Code to a running editor; beginner. Backs [agents](../automation/agents.md).

### Books and sites of the field

Each line gives the level, then the parts of this book that the source serves. Few of these sources link here, because the book may link only to hosts it has checked.

- Jason Gregory, "Game Engine Architecture", 4th edition: the whole of an engine, from the loop to tools, with the industry's habits; intermediate. Serves Core, Assets, Animation and Engineering.
- Tomas Akenine-Moller, Eric Haines and Naty Hoffman, "Real-Time Rendering", 4th edition: the reference for every technique of the renderer; advanced. Serves Draw, Light, Image and Indirect.
- [Matt Pharr, Wenzel Jakob and Greg Humphreys, "Physically Based Rendering", 4th edition](https://pbr-book.org/): light transport from first principles, with working code; advanced. Serves Light and Indirect.
- Eric Lengyel, "Foundations of Game Engine Development": a full engine in four volumes, with math, rendering and physics; intermediate. Serves Core, Draw and Physics.
- Fletcher Dunn and Ian Parberry, "3D Math Primer for Graphics and Game Development": vectors, matrices and quaternions from the start; beginner. Serves Basics and Draw.
- Christer Ericson, "Real-Time Collision Detection": the standard book on shapes, bounding volumes, queries and speed; advanced. Serves Physics and World.
- [Robert Nystrom, "Game Programming Patterns"](https://gameprogrammingpatterns.com/): the loop, components, the command, the observer and other patterns, each with its cost; beginner. Serves Core and Scripting.
- [learncpp.com](https://learncpp.com/): a free course in C++ from the first program to templates; beginner. Serves Basics.
- LearnOpenGL: a free course that draws a first triangle and builds up to lighting and shadows; beginner. Serves Draw and Light.
- [The Vulkan Tutorial](https://vulkan-tutorial.com/) and the Khronos Vulkan tutorial: every step from an instance to a first triangle in Vulkan; intermediate. Serves GPU.
- vkguide.dev: building a small Vulkan engine, with chapters on asset systems and GPU-driven drawing; intermediate. Serves GPU and Draw.
- [Gaffer on Games](https://gafferongames.com/): articles on fixed time steps, physics, networking and saving; intermediate. Serves Core, Physics and Appendix.
- Gabriel Gambetta, "Fast-Paced Multiplayer": prediction, interpolation and lag compensation, with a live demonstration; beginner. Serves Appendix.
- Red Blob Games: interactive articles on grids, paths, noise and maps; beginner. Serves Make and Appendix.
- Erin Catto's publications, collected on [Box2D's site](https://box2d.org/): the talks and papers behind the physics solver that box3d continues; advanced. Serves Physics.
- Filament, "Physically Based Rendering in Filament": materials, lights and the real-time approximations, with the formulas and shader code; intermediate. Serves Light and Image.
- Bartosz Ciechanowski's articles: interactive explanations of light, shadows, the camera and other physical ideas; beginner. Serves Light and Image.
- Scratchapixel: lessons that give results first and put the math where a lesson needs it; beginner. Serves Draw.
- Handmade Hero: a long video series that builds a game from nothing; not fetched; intermediate. Serves Core.

The reviewers asked for sources on the ideas of the pages on game artificial intelligence (AI) and networking, which the sources above do not cover. They are named from memory and not fetched:

- Craig Reynolds, "Steering Behaviors For Autonomous Characters" (Game Developers Conference, 1999): the steering behaviors that move groups and followers; intermediate.
- Damian Isla, "Handling Complexity in the Halo 2 AI" (Game Developers Conference, 2005): behavior trees in a shipped game; intermediate.
- Jeff Orkin, "Three States and a Plan: The A.I. of F.E.A.R." (Game Developers Conference, 2006): goal-oriented planning in a shipped game; intermediate.
- Mikko Mononen, Recast and Detour: the navigation mesh builder and the path search that many engines use; intermediate. Its repository is on [github.com](https://github.com/recastnavigation/recastnavigation).
- GGPO, the rollback library by Tony Cannon, and the Game Developers Conference talks about it: rollback for games where every player must see the same match; advanced.

### Sources by part

Each part shows the sources that its pages cite most, up to four, with the pages that cite them. The choice favors sources that several pages cite and sources with an address.

#### Start here

- [CMake's tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html): what CMake does with a project's `CMakeLists.txt`, step by step; beginner. Cited by [install](../start/install.md).
- [Microsoft's guide to C++ in Visual Studio](https://learn.microsoft.com/en-us/cpp/build/vscpp-step-0-installation): installing Visual Studio with its C++ workload; beginner. Cited by [install](../start/install.md).
- [Glenn Fiedler's article on the fixed step](https://gafferongames.com/post/fix_your_timestep/): what goes wrong when a game moves by the measured time of each frame, and the fixed step that cures it; intermediate. Cited by [what-an-engine-is](../start/what-an-engine-is.md).
- [The Unity manual](https://docs.unity3d.com/Manual/index.html): the languages, editor and platforms of another engine, for comparison; beginner. Cited by [what-an-engine-is](../start/what-an-engine-is.md).

#### Making games

- [Creative Commons, "About CC0"](https://creativecommons.org/publicdomain/zero/1.0/): what the CC0 dedication says, for beginners. Cited by [assets](../make/assets.md).
- [Kenney, "Platformer Kit"](https://kenney.nl/assets/platformer-kit): the pack the coin comes from, for beginners. Cited by [assets](../make/assets.md).
- [Gaffer On Games, "Fix Your Timestep!"](https://gafferongames.com/post/fix_your_timestep/): why physics runs in fixed steps (intermediate). Cited by [physics](../make/physics.md).
- [cppreference, "to_string"](https://en.cppreference.com/w/cpp/string/basic_string/to_string): the function that turns a number into text; intermediate. Cited by [hud](../make/hud.md).

#### Foundations

- [The glm manual](https://github.com/g-truc/glm/blob/master/manual.md): the math functions these pages call; intermediate. Cited by [math-vectors](../basics/math-vectors.md), [math-matrices](../basics/math-matrices.md), [math-bases](../basics/math-bases.md).
- [3Blue1Brown, "Essence of linear algebra"](https://www.3blue1brown.com/topics/linear-algebra): videos that draw vectors and matrices as movements of space; beginner. Cited by [math-vectors](../basics/math-vectors.md), [math-bases](../basics/math-bases.md), [math-rotations](../basics/math-rotations.md).
- [PowerShell: about environment variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables): how PowerShell reads and sets them; beginner. Cited by [tools](../basics/tools.md).
- [PowerShell: about redirection](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_redirection): `>`, `2>` and the other streams of PowerShell; intermediate. Cited by [tools](../basics/tools.md).

#### Engine architecture

- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): every filter and option of the test program; beginner. Cited by [first-change](../core/first-change.md), [debugging](../core/debugging.md).
- [The spdlog repository](https://github.com/gabime/spdlog): the logging library behind the loggers; intermediate. Cited by [conventions](../core/conventions.md), [debugging](../core/debugging.md).
- [Robert Nystrom, "Game Loop", in Game Programming Patterns](https://gameprogrammingpatterns.com/game-loop.html): why a game runs a loop, and how it keeps time; beginner. Cited by [frame-loop](../core/frame-loop.md), [time](../core/time.md).
- [Glenn Fiedler on fixing the time step](https://gafferongames.com/post/fix_your_timestep/): from a measured step to a fixed step with interpolation; intermediate. Cited by [frame-loop](../core/frame-loop.md), [time](../core/time.md).

#### Scenes and the ECS

- [The EnTT repository](https://github.com/skypjack/entt): the registry and its documentation, which Strata uses. Advanced. Cited by [what-a-world-is](../world/what-a-world-is.md), [reflection](../world/reflection.md).
- [Robert Nystrom, "Component", in Game Programming Patterns](https://gameprogrammingpatterns.com/component.html): the second way, objects that own components, and why it was invented. Beginner. Cited by [what-a-world-is](../world/what-a-world-is.md).
- [Michele Caini, "ECS back and forth"](https://skypjack.github.io/2019-02-14-ecs-baf-part-1/): the writer of EnTT on entity-component systems and sparse sets. Intermediate. Cited by [what-a-world-is](../world/what-a-world-is.md).
- [The Unity manual, "GameObjects"](https://docs.unity3d.com/Manual/GameObjects.html): how Unity builds a thing from components. Beginner. Cited by [what-a-world-is](../world/what-a-world-is.md).

#### The GPU and the renderer's core

- [NVRHI on GitHub](https://github.com/NVIDIA-RTX/NVRHI): the library behind `nvrhi::IDevice`, with the command list and the other objects Strata draws through; intermediate. Cited by [first-triangle](../gpu/first-triangle.md), [debugging](../gpu/debugging.md).
- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): the filters that run one suite of tests; beginner. Cited by [first-triangle](../gpu/first-triangle.md).
- [The Vulkan specification, on registry.khronos.org](https://registry.khronos.org/vulkan/specs/1.3/html/vkspec.html): the exact rules of Vulkan, to consult one point at a time; advanced. Cited by [first-triangle](../gpu/first-triangle.md).
- [Microsoft's page of the HLSL function `mul`](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-mul): how `mul` multiplies a vector and a matrix in each order; intermediate. Cited by [first-triangle](../gpu/first-triangle.md).

#### Assets

- [doctest's documentation of its command line](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): `--test-suite` and the other filters. Beginner. Cited by [extending](../assets/extending.md).

#### The image

- [NVRHI](https://github.com/NVIDIA-RTX/NVRHI): the graphics layer that Strata renders through; its repository documents binding sets, layouts and push constants. Intermediate. Cited by [tutorial-post-effect](../image/tutorial-post-effect.md).
- [The Vulkan specification](https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html): the chapter on push constants gives the 128 byte guarantee behind the limit. Advanced. Cited by [tutorial-post-effect](../image/tutorial-post-effect.md).
- [doctest](https://github.com/doctest/doctest): the test framework of Strata's tests, with its filters and `CHECK` macros. Beginner. Cited by [tutorial-post-effect](../image/tutorial-post-effect.md).

#### Game UI

- [Game Programming Patterns, "Dirty Flag"](https://gameprogrammingpatterns.com/dirty-flag.html): the pattern of marking what changed so that only it is computed again; beginner. Cited by [contract](../ui/contract.md).
- [Game Programming Patterns, "Observer"](https://gameprogrammingpatterns.com/observer.html): the idea behind signals and events; beginner. Cited by [contract](../ui/contract.md).
- [Dear ImGui FAQ](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md): immediate mode compared with retained mode; intermediate. Cited by [contract](../ui/contract.md).

#### Capstone: one feature through every layer

- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): every filter and option of the test program. Beginner. Cited by [land](../capstone/land.md).
- [Pro Git, "Git Branching"](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell): branches, the base of the CI branch. Beginner. Cited by [land](../capstone/land.md).
- [GitHub Actions documentation](https://docs.github.com/en/actions): how a workflow runs and how annotations appear. Intermediate. Cited by [land](../capstone/land.md).

## Where it lives in Strata

- `Docs/README.md`: the index of the engine's guides.
- `Docs/Manual/`: the guides for people who make games in the editor.
- `.claude/skills/`: the skills for agents, five at the pin.
- `Docs/Releases/PackageReadme.md`: the text of the archive's `README.md`.
- `CMake/StrataPackaging.cmake`: the rules that decide which documents a release archive installs.
