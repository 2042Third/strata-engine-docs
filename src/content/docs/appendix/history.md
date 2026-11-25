---
id: appendix/history
title: "Which release brought what"
description: "Each Strata release from 0.3.0 to 0.8.0 with its date, its development wave, what it brought by area and what changed for existing projects."
kind: reference
size: M
tracks: []
needs: []
status: final
---

This page answers one question: in which release did a feature arrive? Strata is built in development waves, planned batches of work that each end in a release ([Releasing Strata](../engineering/releasing.md) teaches the steps). Version numbers follow the waves: release 0.3.0, the first, holds waves 1 to 3, and each later minor version holds one wave, so 0.4.0 is wave 4 and 0.8.0 is wave 8. Patch versions carry fixes only.

The book describes release 0.8.0, and its programs report version 0.8.0. A build made between two releases reports the release before it, because the version changes only in the commit that cuts a release. The version comes from `CMakeLists.txt` and reaches the programs through `c_EngineVersion` in `Strata/src/Strata/Core/Version.h.in`.

Each section below names a release, its date and its wave. Its table has one row per area, in the order the release notes use. A row says what arrived and links the pages that teach it. The dates come from the Status paragraph of each wave in `Docs/Roadmap.md` and from the notes of each release.

Where a release changed what happens to an existing project, a list of upgrade notes follows the table. A feature that the documents never date is not guessed: the section "Features without a release date" lists those.

## Release 0.3.0: waves 1 to 3

Release 0.3.0 holds three waves: wave 1 landed on 2026-10-10, wave 2 on 2026-10-11 and wave 3, the last, on 2026-10-12. Nothing of the engine is dated before it. Its release notes start at 0.3.0, and what they describe already worked as a whole.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Editor | The launcher with the Basic 3D template and the Tetris sample; panels you can dock; imports in the background; a trash with undo; recovery of work not yet saved after a crash; **File ▸ Export Game...** | [Projects](../editor/projects.md), [Recovery](../editor/recovery.md), [Undo](../editor/undo.md) |
| Rendering | Physically based shading, clustered point and spot lights, soft sun shadows, ambient occlusion, automatic exposure, bloom, tone mapping, color grading, fast approximate anti-aliasing (FXAA) and text | [Sun shadows](../light/sun-shadows-1.md), [Exposure](../image/exposure.md), [Text](../gpu/text.md) |
| Streaming | Compressed textures, loads in the background within memory budgets, textures that refine from small levels | [Mip streaming](../draw/mip-streaming.md), [Residency](../assets/residency.md) |
| Scenes | Scenes load in the background; additive sub-scenes; prefabs that spawn many instances | [Sub-scenes](../world/sub-scenes.md), [Prefabs](../world/prefabs.md) |
| Physics | Jolt rigid bodies, triggers, raycasts, character controllers and named collision layers | [Bodies and colliders](../physics/bodies-colliders.md), [Character controllers](../physics/character-controllers.md) |
| Audio and animation | Spatial sound with a listener; skins, clips and animation controllers with cross-fades, events and root motion | [Audio engine](../audio/engine.md), [Animation system](../animation/system.md) |
| Input | Keyboard, mouse, gamepads and cursor modes | [Gamepads](../input/gamepads.md) |
| Scripting | C++ script classes built by the editor, hot reload and crash containment | [Why scripts](../scripting/why-scripts.md), [Hot reload](../scripting/hot-reload.md) |
| Exported games | A folder with the runtime, a manifest and a compressed asset pack; a window or a headless run | [Packs and export](../assets/packs-export.md) |
| Artificial intelligence (AI) agents | Every operation is a command with a schema; the command line and a server of the Model Context Protocol (MCP); simulated input; captures; the Activity panel | [Model Context Protocol](../automation/mcp.md), [Simulated input](../input/simulated.md), [The journal](../editor/journal.md) |
| Instruments and scale | The Streaming and Performance panels; scenes of up to 1,048,575 entities | [Instrument panels](../editor-ui/instrument-panels.md) |
| Build and tests | The perf lab arrived in wave 1 | [The perf lab](../engineering/perf-lab.md) |

## Release 0.4.0: wave 4

Release 0.4.0 is wave 4, completed on 2026-10-19. The wave's step 0 landed earlier, on 2026-10-13. Step 0 is the shared work that lands before a wave's streams of work begin. It finished wave 3, cut release 0.3.0 and added a job of the continuous integration (CI) that builds Dist, the shipping configuration. It also added the perf lock, which keeps two speed measurements on one machine from running at the same time, a check of the code against the CI's older compilers and the CI status tool.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Worlds | Worlds streamed in cells, made with `world.create` (**New ▸ World** in the Content Browser), a cell map and cooking | [Why streaming](../worlds/why-streaming.md), [The streamer](../worlds/streamer.md) |
| Rendering | Drawing and culling driven by the graphics processing unit (GPU), generated levels of detail, rendering relative to the camera, shadow cascades fitted on the GPU | [GPU-driven drawing](../draw/gpu-driven.md), [Levels of detail](../draw/lod.md) |
| Game user interface (UI) | Canvases, rects, buttons, input fields, masks and world-space canvases | [What game UI does](../ui/what-game-ui-does.md), [UI layout](../ui/layout.md) |
| Editor | The Game view; prefab overrides; background saves; large projects; **File ▸ Open Scene...** | [The Game view](../editor-ui/game-view.md), [Prefab instances](../editor/prefab-instances.md), [Saving](../editor/saving.md) |
| AI agents | `play.step`, `input.sequence`, `editor.batch` and toolsets of the MCP server | [Agents](../automation/agents.md), [Playtests](../make/automated-playtests.md) |
| Scale | Binary scenes in exported games; a million entities saved without freezing the editor | [Serialization](../world/serialization.md) |
| Build and tests | One library per layer, optional modules, precompiled headers, test shards, a fuzz run, a compiler cache and a Windows Debug job | [Layers and registries](../core/layers-registries.md), [Continuous integration](../engineering/ci.md) |

## Release 0.5.0: wave 5

Release 0.5.0 is wave 5, completed on 2026-10-20. The wave did what the owner asked for: physics on box3d instead of Jolt, and sample games that show what the engine can do. Tetris dates from 0.3.0, and its heads-up display (HUD) became a game UI canvas in 0.4.0. The Showcase sample waits for wave 8.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Samples | Third-Person Adventure, Open World and Physics Playground beside Tetris, all made by an AI agent through commands | [The samples](../make/samples.md) |
| Physics | The simulation runs on box3d, behind the same components, script application programming interface (API) and commands | [Why this physics engine](../physics/why.md), [The world step](../physics/world-step.md) |
| AI agents | Query steps that wait with `until`; simulated input in a game paused at time scale 0 | [Command scripts](../editor/command-scripts.md), [Simulated input](../input/simulated.md) |

Existing projects change as follows:

- Steadier stacks: a crate tower drifts about 1 cm where it drifted 11 to 15 cm on Jolt.
- Fast bodies are swept against static ones, so they no longer pass through walls and floors.
- Triggers no longer report static triangle-mesh colliders. Give a wall that a trigger must see a box collider.
- Overlapping bodies are pushed apart at up to 3 m/s, so spawn bodies apart.
- Damping follows a new formula, so bodies keep slightly more speed.
- A convex collider becomes a hull of at most 64 vertices.
- Creating many bodies at once takes longer, because box3d adds them one at a time.
- `MaxBodyPairs` is gone from the scene settings; older scenes load and ignore it.

## Release 0.6.0: wave 6

Release 0.6.0 is wave 6, completed on 2026-10-23. Its two streams took the quality of the rendering and settings for the whole project.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Rendering | Temporal anti-aliasing (TAA) with the presets Sharp and Original; shadows of point and spot lights; blended sun cascades; light in real units; a physical atmosphere and height fog; clear coat and glass | [Temporal anti-aliasing](../image/taa.md), [Units and exposure](../light/units-exposure.md), [Atmosphere](../light/atmosphere.md), [Fog](../light/fog.md), [Clear coat and transmission](../light/clearcoat-transmission.md) |
| Lighting | Reflection probes, screen-space reflections and **Extract Sun** for a high dynamic range (HDR) sky | [Probes](../indirect/probes.md), [Screen-space reflections](../indirect/ssr.md) |
| Editor | **File ▸ Project Settings...** and **File ▸ Preferences...** | [Project settings](../world/projects-settings.md), [Settings windows](../editor-ui/settings-windows.md) |
| Physics | Collision layers become one table for the whole project | [Collision layers](../physics/collision-layers.md) |
| Input | Input actions with maps, composites and rebinding by players | [Input actions](../input/actions.md), [Rebinding](../input/rebinding.md) |
| Exported games | The game's title, version, company, copyright and icon | [Game identity](../worlds/game-identity.md) |
| AI agents | The `settings` toolset, `input.action`, `lighting.bakeProbes` and `lighting.extractSun` | [Agents](../automation/agents.md) |

Existing projects change as follows:

- The first time 0.6.0 opens a project saved by 0.5.0, it reads the scenes' collision layers in the background and makes them the project's. A pair of layers that any scene kept apart stays apart.
- The new version then saves the project file as version 3, which 0.5.0 cannot open. Keep a copy if you still need 0.5.0.
- `scene.setSettings` refuses collision layers and names `project.setCollisionLayers`.
- The external code editor is copied once into 0.6.0's own preferences file.
- Textures and glTF models import once more, in the background.
- Sun cascades blend by default and **Auto Exposure Max EV** defaults to 16; scenes that stored 12 keep it.
- Script modules built for 0.5.0 load unchanged: the script application binary interface (ABI) keeps version 1, and thirteen host functions were appended.

## Release 0.7.0: wave 7

Release 0.7.0 is wave 7, integrated on 2026-10-28 by its notes; the Status paragraph dates the wave's landing a day later, 2026-10-29. The wave took on the image: shadows at the screen's own resolution, a camera-like tone curve and a choice of cost.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Rendering | Graphics Quality presets Low, Medium, High and `Ultra`; sun shadows as fine as the screen; contact shadows; the Filmic tone curve; dithered output; motion blur, film grain, lens effects and color lookups; morphological anti-aliasing; a physical lens for depth of field | [Quality settings](../image/quality-settings.md), [Sun shadows, part 2](../light/sun-shadows-2.md), [Tone mapping](../image/tone-mapping.md), [Depth of field](../image/depth-of-field.md), [Spatial anti-aliasing](../image/spatial-aa.md) |
| Lighting | Energy compensation for rough metals; ambient occlusion with its noise removed; aerial perspective; sun and sky presets; five lighting debug views | [Energy](../light/energy.md), [Ambient occlusion](../indirect/ao.md), [Measuring light](../light/measuring-light.md) |
| Physics | Less work around each step; the **Physics ▸ Simulation** settings; no stale contacts for characters and kinematic bodies | [Tuning physics](../physics/tuning.md) |
| Scripting and games | The Graphics menu API for players; the players' bindings and options kept in the player's data folder | [Rebinding](../input/rebinding.md), [Quality in a game](../make/quality.md) |
| Editor | A Performance panel that costs less than half; fewer hitches while a large scene opens | [Instrument panels](../editor-ui/instrument-panels.md) |
| AI agents | `graphics.resetPlayerOptions`, `lighting.applySkyPreset`, `physics.setDetailedStats` and a quality field for captures | [Agents](../automation/agents.md) |
| Build and tests | The look-dev harness `Tools/LookDev.py` | [Look development](../engineering/look-dev.md) |

Existing projects change as follows:

- A project without a Graphics Quality setting draws at High. Choose Medium to keep 0.6.0's costs.
- The soft edges of sun shadows are half as wide for the same softness; contact shadows appear at High and `Ultra`.
- Scenes that stored the Academy Color Encoding System (ACES) curve keep it; a scene moved to Filmic needs about 0.8 exposure value (EV) less exposure compensation.
- Automatic exposure meters the center more and adapts faster to bright light.
- Bodies fall asleep below 0.08 m/s instead of 0.05, and characters no longer keep contacts from earlier steps.
- Every glTF model imports once more in the background.
- Script modules built for 0.6.0 load unchanged: seven host functions were appended.

## Release 0.8.0: wave 8

Release 0.8.0 is wave 8, landed on 2026-11-23. Its step 0 landed on 2026-11-02, and the streams followed. The wave took on light: highlights, lamps with shadows, glowing surfaces that light a room, light that bounces, and motion that stays smooth at any frame rate.

| Area | What arrived | Where to learn it |
| --- | --- | --- |
| Samples | A fifth sample, High Desert Outpost, first in the launcher | [The samples](../make/samples.md) |
| Editor | A ghost that shows where a dropped asset lands; frame-rate preferences for idle and busy editors | [Placement](../editor/placement.md), [Status](../editor-ui/status.md) |
| Physics and time | **Physics ▸ Timing** with a fixed rate; bodies drawn between their last two fixed poses | [Interpolation](../world/interpolation.md), [Time](../core/time.md) |
| Rendering | Stable sun cascades with fixed splits by distance, and a fifth cascade near the camera at High and `Ultra`; contact shadows off in every preset; a sun highlight that takes the light's size; reflectance from the index of refraction; more point and spot lights with shadows at High and `Ultra`, faded in and out by time | [Sun shadows, part 2](../light/sun-shadows-2.md), [Reflectance](../light/reflectance.md), [Shadows of point and spot lights](../light/local-shadows.md) |
| Lighting | Rectangle lights, glowing rectangles whose highlight has their shape; reflections without a screen-door pattern; probes of 256 texels at High; experimental global illumination in the **Post Process** | [Area lights](../light/area-lights.md), [Screen-space reflections](../indirect/ssr.md), [Probes](../indirect/probes.md), [The problem of indirect light](../indirect/problem.md), [Radiance cascades](../indirect/gi-cascades.md) |
| AI agents | `asset.place` and `scene.raycast` to place content where it lands, `lighting.makeAreaLight`, `editor.screenshot` and `asset.types` | [Agents](../automation/agents.md), [Placement](../editor/placement.md) |
| Platform | GLFW sealed behind the window; no window means a null result | [Windows and events](../core/windows-events.md), [Platform](../core/platform.md) |
| Build and tests | Slang replaces `glslang` as the shader compiler; the macOS 15 job | [Shaders](../gpu/shaders.md), [Continuous integration](../engineering/ci.md) |

Existing projects change as follows:

- Stored values never change: only new components, new projects and scenes without the value get the new defaults.
- Scripts that follow a moving body read `GetDrawnPosition()` and `GetDrawnRotation()`, because the body is drawn up to a step behind its last fixed pose. Turn **Interpolation** off to draw the last pose.
- Scripts that move an entity far in `OnFixedUpdate` call `GetTransform().ResetInterpolation()` after the move.
- Script modules built for 0.7.0 load unchanged: three host functions were appended.
- A prefab dropped with the **Game camera** lands under the pointer, and a drop on empty space lands on the grid plane.
- The sun's shadow maps at High take 1 GiB at 3840x2160 instead of 256 MiB; choose Medium or Custom to spend less.
- The first configure of a clone downloads the Slang archive once, or reads `STRATA_SLANG_ROOT`.
- The `glslang` folder may be deleted after pulling.

## Features without a release date

The documents date a feature by its wave or release only when they say so, and several areas stay without a date. The list names each gap rather than guess, so a reader never mistakes a missing date for a date of 0.3.0.

- Audio and input: the documents date audio, gamepads and simulated input to 0.3.0, `input.sequence` and UI navigation to 0.4.0, and input at time scale 0 to 0.5.0. Which wave added the hand-off of the listener, Doppler shift from bodies and `audio.state` was not traced.
- Scripting: the notes do not say in which wave the script API gained bodies, queries, audio and game flow. All of them are in 0.3.0.
- Editor: the documents date idle throttling, the launcher, multi-edit, the Activity, Streaming, Performance and Problems panels and fonts for Chinese, Japanese and Korean text to 0.3.0. The documents give no date for time dilation, cameras kept per scene, scene switches in play mode or the limits of recovery.
- Game UI: masks, input fields and world-space canvases appear in the 0.4.0 notes; later refinements are not traced.
- Rendering: the horizon fade of shadows, cascade occlusion culling, prepared loads and the deferred release queue have no stated release. Bloom, tone mapping and FXAA appear in 0.3.0's list; which tone curves existed then is not stated.
- Animation, assets, physics and scenes: the refinements of drawing only visible animators, small asset items and several physics internals have no stated release.
- Foundation: the documents do not say when the application class, layers, events, logging or the job system first arrived.
- Build and tests: the long-path build fallback and the Scripts root of the Content Browser are without a date, and so are the Hierarchy's search tokens.
- Automation: the command server and its first connection step exist already in 0.3.0; earlier forms are not dated.

## Questions this page does not answer

What each feature does is in [the term index](../reference/glossary.md). What the engine's documents plan for later is on the page of what Strata lacks, and how a release is built, packaged and published is in [Releasing Strata](../engineering/releasing.md).

## Where it lives in Strata

- `Docs/Releases/0.3.0.md`, `Docs/Releases/0.4.0.md`, `Docs/Releases/0.5.0.md`, `Docs/Releases/0.6.0.md`, `Docs/Releases/0.7.0.md` and `Docs/Releases/0.8.0.md`: the release notes, with their sections on what is new and on upgrading.
- `Docs/Roadmap.md`: the Status paragraph of each wave, with its dates.
- `CMakeLists.txt` and `Strata/src/Strata/Core/Version.h.in`: the version a build reports.
