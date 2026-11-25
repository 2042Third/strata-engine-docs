---
id: reference/performance
title: "Measured costs and their budgets"
description: "Every cost the engine's speed tests measure, with the value measured on the reference machine and the budget its test enforces."
kind: reference
size: M
tracks: []
needs: [engineering/perf-lab]
status: final
---

A game that runs well on one frame can run badly on the next release, and nobody notices until a player complains. Strata guards against this with speed tests: each one runs a fixed piece of work and compares its cost with a stored limit. The engine's speed tests measure :value{key="perfBudgets.count"} costs. The table below lists them, grouped by suite, in the order of the file `StrataTests/Perf/Budgets.json`.

A row has four columns. The first is the metric, written `<Suite>.<Metric>`: the suite is a group of tests, and a suite named `Perf.*` runs on the :term[central processing unit]{id=processor} (CPU) alone, while `PerfGPU.*` needs a :term[graphics processing unit]{id=gpu} (GPU). The next two columns are `Measured`, the value the :term[reference machine]{id=reference-machine} gave, and `Budget`, the limit the test enforces. The last holds the unit of both: `ms` (milliseconds), `us` (microseconds), `MB`, `count` or `ratio`. Lower is always better, so a rate is written as the cost of one item.

As an example, take the metric `Evaluate1000` of the `Perf.Animation` suite: a frame of 1,000 animators. Its measured value is :value{key="perf.Perf.Animation.Evaluate1000.Measured"} :value{key="perf.Perf.Animation.Evaluate1000.Unit"} and its budget is :value{key="perf.Perf.Animation.Evaluate1000.Budget"} :value{key="perf.Perf.Animation.Evaluate1000.Unit"}, exactly 1.5 times the measurement. A test fails only when every attempt of its check costs more than the budget. A check that goes over measures again, so one slow run on a busy machine does not fail the build.

## What the numbers mean

The **reference machine** is the computer that measured the values: an Intel Core i7-13700K with an NVIDIA `RTX 5090` graphics card, running Windows 11 and a Release build, on a quiet machine. Your computer gives other numbers, and that is expected: compare a result of yours only with a run of the same code on the same machine. The numbers of other machines never enter `Budgets.json`.

A **budget** is at most 1.5 times the measurement, or a lower limit set for that metric. Budgets only go down, apart from rare cases such as a change of the reference machine. A change that makes a cost smaller lowers its entry in the same commit, and a cost over its budget is a regression to fix, not a limit to raise. A row may also give a `Target`, a goal below the budget that the metric has not reached on every run.

A metric that the reference machine has not measured yet is **provisional**. Its entry holds a unit and the flag `Provisional` (and perhaps a target), so its row has no measured value and no budget. Its test measures once, prints and records the value, and never fails, until the reference machine measures it.

At the pin, about a third of the entries are provisional, in many suites. Among them are the newest :term[renderer]{id=renderer} rows: the lights shaped as rectangles (`AreaLights8`, `AreaShadows4`) and the scenes of 64 and 256 shadowed point lights. Why budgets come from one machine, and how the perf lab keeps the numbers honest, is the subject of [the perf lab](../engineering/perf-lab.md).

Other pages quote single numbers with keys of the form `perf.<name>.Measured`, `perf.<name>.Budget` and `perf.<name>.Unit`. A key exists only where the file gives the value, so a page that cites a provisional metric states its budget or says that it is provisional.

::include{file="performance.md"}

## The suites

A suite is the unit of the test names: every cost above belongs to one, and `ctest --preset windows-release -L perf` runs them all. The next table has one row per suite at the pin, 16 on the CPU and 8 with a GPU. It is written by hand from the `TEST_SUITE` names of `StrataTests/src/Perf/` and of the perf files in `StrataTests/src/Editor/`. A suite may live in several files, and a name such as `Boxes70k` of the metrics in the table above is a group of metrics of the suite `Perf.Physics`, not a suite.

| Suite | What it measures | Test files | Read next |
| --- | --- | --- | --- |
| `Perf.Animation` | Evaluating 1,000 cross-fading animators, and 10,000 animators no :term[renderer]{id=renderer} sees | `AnimationPerfTests.cpp` | [Animation system](../animation/system.md) |
| `Perf.Asset` | The first and the warm scan of a project of 10,000 materials | `WorldIOPerfTests.cpp` | [Loading assets](../assets/loading.md) |
| `Perf.Editor` | Entity edits, undo, the hierarchy, selection, prefab instances, imports, saves and recovery files in scenes of up to a million entities | `EditorPerfTests.cpp`, `EditorWorldPerfTests.cpp`, `WorldIOPerfTests.cpp` | [Worlds in the editor](../editor/worlds.md) |
| `Perf.EditorPanels` | The Performance, Content Browser and Streaming panels over 10,000 assets | `EditorPanelPerfTests.cpp` | [Instrument panels](../editor-ui/instrument-panels.md) |
| `Perf.FramePacer` | How well the editor holds the frame rates it offers | `FramePacerPerfTests.cpp` | [Frame timing](../core/frame-loop.md) |
| `Perf.FrameProfiler` | The cost of timing a frame of 16 stages | `FrameProfilerPerfTests.cpp` | [Profiling](../core/profiling.md) |
| `Perf.GameUI` | A full layout and an idle frame of 10,000 interface elements | `GameUIPerfTests.cpp` | [Layout](../ui/layout.md) |
| `Perf.Harness` | A sort that serves as a canary: it shows whether the machine itself is slow | `PerfHarnessTests.cpp` | [The perf lab](../engineering/perf-lab.md) |
| `Perf.Input` | Evaluating 256 input actions with every gamepad connected | `InputPerfTests.cpp` | [Input actions](../input/actions.md) |
| `Perf.Jobs` | Submitting, waiting for and waking jobs | `JobsPerfTests.cpp` | [Jobs](../core/jobs.md) |
| `Perf.Physics` | Falling, sleeping and settling boxes, character controllers, body creation and the memory a world reserves | `PhysicsPerfTests.cpp` | [Physics at scale](../physics/scale-streaming.md) |
| `Perf.Runtime` | Switching scenes, starting an exported world of a million entities and quitting while it loads | `RuntimePerfTests.cpp`, `WorldGamePerfTests.cpp` | [Exported games](../worlds/runtime.md) |
| `Perf.Scene` | Transform updates, :term[interpolation]{id=interpolation}, play copies and prefab copies in scenes of up to a million entities | `ScenePerfTests.cpp`, `WorldIOPerfTests.cpp` | [The scene graph](../world/scene-graph.md) |
| `Perf.Scripting` | Play frames with 100,000 and 300,000 scripts, and frames that spawn or destroy scripted entities | `ScriptingPerfTests.cpp` | [The script system](../scripting/script-system.md) |
| `Perf.TextureCook` | Cooking the stress project's textures, and the memory of an import | `TextureCookPerfTests.cpp` | [Texture cooking](../assets/texture-cooking.md) |
| `Perf.World` | Streaming and unloading cells while driving across large worlds | `WorldPerfTests.cpp` | [The streamer](../worlds/streamer.md) |
| `PerfGPU.Editor` | Editor frames, start up, opening and saving a world, imports and panels with a GPU | `EditorFramePerfTests.cpp`, `EditorLaunchPerfTests.cpp`, `EditorPanelPerfTests.cpp`, `EditorPerfTests.cpp` | [Instrument panels](../editor-ui/instrument-panels.md) |
| `PerfGPU.GameUI` | The interface pass on 10,000 elements, changing and idle | `GameUIPerfTests.cpp` | [Drawing the interface](../ui/drawing.md) |
| `PerfGPU.Harness` | A check that GPU perf tests run on a device without validation | `PerfGPUHarnessTests.cpp` | [The perf lab](../engineering/perf-lab.md) |
| `PerfGPU.Pack` | Opening and streaming the stress project's packs | `PackPerfTests.cpp` | [Packs and export](../assets/packs-export.md) |
| `PerfGPU.Renderer` | Frames of 100,000 to a million cubes, under up to 256 shadowed point lights or lights shaped as rectangles, and the cost of each post effect and lighting feature at 4K | `RendererPerfTests.cpp`, `RendererFramePerfTests.cpp`, `AnimationPerfTests.cpp` | [The render scene](../draw/render-scene.md) |
| `PerfGPU.Samples` | The tours of the Open World and Showcase samples: GPU time and the work of each frame | `SamplePerfTests.cpp` | [The samples](../make/samples.md) |
| `PerfGPU.Streaming` | Frames, memory and upload steps while textures stream in | `StreamingPerfTests.cpp` | [Residency](../assets/residency.md) |
| `PerfGPU.World` | Driving across a large world while the renderer draws | `WorldPerfTests.cpp` | [The streamer](../worlds/streamer.md) |

Two more suites, `PerfLab` and `PerfLab.WorldFixture`, hold no budgets. The first tests the harness: the budget file's rules, the :term[confirmed check]{id=confirmed-check} and the results files. The second tests the generators of the large worlds and projects that the other suites measure.

Three tools sit around the suites. `Tools/PerfStability.py` repeats runs to show how much a metric varies, and `Tools/PerfLock.py` runs a command under a lock, so that two perf runs on one machine never measure at the same time. A budget changes only with the evidence they give: [the perf lab](../engineering/perf-lab.md) explains how. Making your own game fast is the subject of [performance for a game maker](../make/performance.md).

## The CPU stages

The Performance panel and the perf log of the :term[runtime]{id=runtime} show a frame as a list of stages, each timed on the :term[main thread]{id=main-thread}. This table is written by hand. It was read from `c_BuiltinFrameStages` in `Strata/src/Strata/Core/FrameProfiler.h`, from the names that code passes to `ST_PROFILE_STAGE`, and from the `ProfileStage` of each :term[scene system]{id=scene-system}. The first twelve rows are the built-in stages; the others register themselves when their code first runs. Stages that time the GPU are listed elsewhere, in [the renderer reference](renderer.md), and measuring a frame is taught in [profiling](../core/profiling.md).

| Stage | What it times | File that times it |
| --- | --- | --- |
| `Input` | The input state and the window's events | `Strata/src/Strata/Core/Application.cpp` |
| `Assets.Update` | The :term[asset manager's]{id=asset-manager} update, without completing loads | `Strata/src/Strata/Asset/AssetManager.cpp`, `Strata/src/Strata/Asset/EditorAssetManager.cpp` |
| `Assets.Finalize` | Completing loaded assets on the main thread, with their GPU uploads | `Strata/src/Strata/Asset/AssetManager.cpp` |
| `Scene.Load` | The main thread's work of a scene load | `Strata/src/Strata/Runtime/GameRuntime.cpp`, `Strata/src/Strata/Scene/SceneSubScenes.cpp`, `StrataEditor/src/Editor/EditorContext.cpp` |
| `Scene.Scripts` | The scripting system's :term[callbacks]{id=callback} | `Strata/src/Strata/Scripting/ScriptingRegistration.cpp` |
| `Scene.Physics` | Physics steps and contact callbacks | `Strata/src/Strata/Physics/PhysicsRegistration.cpp` |
| `Scene.Audio` | The audio system | `Strata/src/Strata/Audio/AudioRegistration.cpp` |
| `Scene.Transforms` | Updating the cached :term[world transforms]{id=world-transform} | `Strata/src/Strata/Scene/Scene.cpp`, `Strata/src/Strata/Scene/SceneInterpolation.cpp` |
| `Render.Extract` | Gathering lights, draws and shadow casters from the scene | `Strata/src/Strata/Renderer/SceneRenderer.cpp`, `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`, `Strata/src/Strata/Renderer/SceneRendererLocalShadows.cpp` |
| `Render.Submit` | Recording and submitting the renderer's :term[command list]{id=command-list} | `Strata/src/Strata/Renderer/SceneRenderer.cpp` |
| `Editor.UI` | The editor's interface layers and drawing them | `Strata/src/Strata/ImGui/ImGuiModule.cpp` |
| `Present` | Presenting the :term[back buffer]{id=back-buffer}, after the :term[work time]{id=work-time} | `Strata/src/Strata/Renderer/GraphicsModule.cpp`, `Strata/src/Strata/Renderer/Renderer.cpp` |
| `Render.UI` | The game interface's draw pass | `Strata/src/Strata/GameUI/GameUIRenderer.cpp` |
| `Scene.UI` | The interface system's update | `Strata/src/Strata/GameUI/GameUIRegistration.cpp` |
| `Scene.Animation` | The animation system | `Strata/src/Strata/Animation/AnimationRegistration.cpp` |
| `World.Streaming` | The world streamer | `Strata/src/Strata/World/WorldRegistration.cpp`, `StrataEditor/src/Editor/EditorContext.cpp` |
| `Editor.Commands` | Running editor commands | `StrataEditor/src/Editor/EditorCommandRunner.cpp`, `StrataEditor/src/Editor/EditorCommands.cpp` |

## Where it lives in Strata

- `StrataTests/Perf/Budgets.json`: every budget, and in its `_comment` the form of an entry.
- `StrataTests/src/Perf/`: the suites that need no editor, with the harness in `PerfUtils.h`.
- `StrataTests/src/Editor/`: the editor's perf suites, in the files named `*PerfTests.cpp`.
- `Tools/PerfStability.py`: repeats runs and reports how much each metric varies.
- `Tools/PerfLock.py`: runs a command under a lock that keeps perf runs on one machine from overlapping.
- `Strata/src/Strata/Core/FrameProfiler.h`: the :term[profiler]{id=profiler-instrumenting-vs-sampling}, its built-in stages and `RegisterStage`.
