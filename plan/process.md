# Process: who does what, in which order, and when a page is done

This file is the contract of the work. It names the roles, what each role is given and returns, the stages that every
page passes, the checks between the stages, the order of the work, and when a page and the book are done. The formats
and tools it names are defined in [pipelines.md](pipelines.md) and [site.md](site.md). How a page is written is
[style.md](style.md). The pages are the rows of `outline-1.md` to `outline-4.md`; the reading orders are
[tracks.md](tracks.md).

Counts in this file are the ones that `plan/check_outline.py --counts --words --waves` prints for the final outline:
335 pages in 25 parts, 299 of them written in phase A and 36 in phase B. When the outline changes, the planner updates
the counts here in the same change.

## Roles

| Role | Who | Does |
| --- | --- | --- |
| **Planner** | the orchestrator | Writes this plan and the rulings on its critique; writes the part briefs; chooses when the pin build and every engine-program run happen; calls the freezes; judges the pilot and a sample of every wave; decides when reviewers disagree. Only the planner changes the outline, and then `plan/check_outline.py` must pass |
| **Tool builder** | Opus, one | Makes the pin clone and the pin build, once per pin (pipelines.md §1.3); brings the spike's Python tools to pipelines.md, with their unit tests; runs `reference.py dump`, `parse` and `render` at every pin |
| **Site builder** | Opus | The web project of site.md: plugins, scripts, CI, deployment. Changes the spike to meet site.md, measures it and writes the spike's report |
| **Glossary admitter** | Opus, one at a time | Writes the seed of the base vocabulary, merges the inventories' terms, and admits the new terms of every batch (pipelines.md §9) |
| **Allocator** | Opus, one per part | Maps every inventory item of its part to exactly one page and lists what has no home |
| **Completeness critic** | Opus, one | Checks all allocations against all inventories: every item has exactly one home |
| **Writer** | Opus, one per page | Writes the page, its figure manifest, its tutorial, its sketches and its notes, and passes the writer's exit checks |
| **Technical reviewer** | Opus, never the page's writer | Tries to refute every claim of the page against the engine at the pin |
| **Provenance reviewer** | Opus, never the page's writer, without access to the engine's source | Checks, section by section, that every idea the page uses was taught to the page's persona ([The provenance check](#the-provenance-check)) |
| **Fixer** | Opus | Answers every finding of the reviews and walks: fixed, or rejected with the reason where a rejection is allowed |
| **Integrator** | Opus, one | Takes reviewed pages in batches: builds the site with every check, makes mechanical repairs, commits and pushes; the only agent that commits and the only one that runs `npm ci`. Runs the tutorials' engine programs, one at a time. Moves the pin during a freeze |
| **Part editor** | Opus, one per part | The edit pass over a whole part; the part's index and review pages; sets `final` |
| **Photographer** | Opus, phase B; in phase A only the captures of the checks before writing (pipelines.md §5.4) | Takes the pictures of the recipes and the pictures of the tutorials' steps, and judges each one against what it must show |
| **Track walker** | Opus, a fresh agent for each walk | Follows one track as its persona, with only the book and the program a reader has, and logs every place where it had to guess or leave the book ([Track walks](#track-walks)) |

No stage is done by the agent that did the stage it checks. A **fresh** agent is a new agent run that has not read the
page, its notes or its reviews before.

## Allocation and part briefs

**Allocation.** `plan/allocation/README.md` is its contract: the items of the inventories, the units, the format of a
unit's file and the check (`plan/allocation/check_allocation.py`). One allocator works on one unit. A unit is a part,
except that `make` is four units, `basics` is two, and `audio` and `input` are one. Every inventory has one owner,
which places each of its items exactly once; `gamedev.md`, whose pages are spread over `start` and `make`, is routed
by one agent first. Each allocator:

- reads the inventory it owns, whole, and the inventory items that the From column of its pages names;
- for `editor`, also reads the files that no inventory surveyed: `StrataEditor/src/Editor/ScriptBuild*`,
  `ScriptToolchain*`, `ScriptProject*`, `ScriptSources*` and `ExternalEditor*`; for `editor-ui`,
  `StrataEditor/src/Panels/ProblemsPanel*`;
- writes `plan/allocation/<unit>.md`: for each page, what it covers and leaves out, whether its content fits its
  size, its items (features, concepts, code worth showing with files and lines at the pin, figures, rules and
  pitfalls, hands-on ideas, glossary terms), each with its inventory file and line, and what the page assumes and
  which page teaches that; then the items it passes on to another unit's page;
- applies these notes of the critique:
  - `CameraComponent`: `GetProjection` goes to `gpu/coordinates`, the depth-of-field fields to
    `image/depth-of-field`, the lookup of the primary camera to `world/scene-graph`;
  - the `FrameCounterModule` exercise (`plan/inventory/foundation.md`, hands-on) is a required exercise of
    `core/engine-modules`;
  - `image/encoding` gets a sentence that points forward to FXAA and film grain;
  - the structure of `StrataCLI` goes to `automation/mcp`;
- places a step that only a command can do by the rule of its page's tracks (style.md §10;
  `plan/critique/rulings-7.md`, R33). On track G or B, the page that teaches running such a step is in the page's
  Needs closure: `make/automated-playtests` for a step that runs a command script (the editor's `--commands`),
  `make/commands` for a step that calls a command (StrataCLI). On a page that comes before that page, the step moves
  to a later page, or into the tutorial's starting checkpoint. On track E, a page before `editor/commands` keeps the
  step: it gives the complete line to paste, one sentence on what it does, and a link forward to `editor/commands`
  (`plan/critique/rulings-4.md`, R11). A page on track E and on track G or B follows the rule for tracks G and B.

The units of `basics` come last: they start from what the other units assume from their pages. Then every unit
takes the items that were passed to its pages.

The check writes `plan/allocation/coverage.md`: every inventory item with no home page or with two, every item that
nobody took, every concept a page must have that no page in its Needs teaches, and every page whose content does not
fit its size. The **completeness critics** (one per inventory, and one for the tables of book.md) read the
inventories against the allocation files: is each home the page where a reader would look, and is anything of the
area missing? `plan/allocation/completeness.md` records their findings. The planner settles each row of both files,
in an allocation or, with `plan/check_outline.py` passing, in the outline.

**Part briefs.** The planner writes `plan/briefs/<part>.md` for each of the 25 parts. A size is a budget of words:
when a brief shows that a page cannot hold its content, the planner makes the page larger or splits it, with
`plan/check_outline.py` passing, before the page is written (`plan/critique/rulings-4.md`, R7 and R11). A page whose
allocation holds an item labelled "Check:" (a claim that rests on code alone and that a run can settle:
`plan/allocation/README.md`, "Checks before writing") gets no brief until the check's result has replaced the item
(`plan/critique/rulings-7.md`, R34). The four checks of the engine's agents do not block a brief: such a page states
only what the code at the pin shows and says that it was read, not run, and the result corrects the page when it is
in (`plan/critique/rulings-9.md`, R39). A brief holds:

1. For each page: what it covers, its draft learn lines (two to five, as style.md §6.1 writes them), and what it
   leaves to which page.
2. The order of ideas across the part's pages.
3. The running examples: Coin Run (track G, block A of `make`) and WindZone (track E, from `world/tutorial-component`
   to `capstone/land`); what happens to them in this part; the part's own small running example, if it has one.
4. The internals pages that carry the full section "The problem and how engines solve it" (style.md §7.3). The other
   internals pages of the part link to them.
5. Which page gets which figures. For `light`, `image` and `indirect`: the effect off and on where it has a switch, its
   debug view where one exists, a sweep of its main setting, and a crop where detail matters; a feature without a
   switch gets a diagram or a lab (style.md §11). The owner page of each lab and of each file under
   `tutorials/assets/`.
6. The steps of track G pages that only a command can do. Each such step says so on its page (style.md §10).
7. The errata and docs drift that the part's pages must not repeat (the table below, and what the allocator found).
8. For `basics` only: the seed of `tools/data/cpp-features.json` (style.md §9).

**Errata known at 822a7a46.** Each was checked against the code at the pin. A page states the code's fact and never
the wrong one. The column Kind says what is wrong: `engine`, a document or comment of the engine at the pin;
`inventory`, a slip of an inventory of `plan/inventory/`, which writers and technical reviewers read as background
([What a writer is given](#what-a-writer-is-given), item 5). The rows of kind `engine` also go to the engine's agents,
with the list of findings of pipelines.md §11 (`plan/critique/rulings-7.md`, R33 and R34). A slip that stands only in
the rows of an allocation is corrected in those rows and has no row here.

| Kind | Erratum | The fact at 822a7a46 | Briefs |
| --- | --- | --- | --- |
| `engine` | `Docs/DeveloperGuide.md:402-405` and `.claude/skills/strata-build-test/SKILL.md:73-74` name 12 test shards | `StrataTests/CoreShards.json` has 13; the guide and the skill omit `SceneTiming`, which runs `Scene.Timing*` | `engineering` |
| `engine` | The comment at `Strata/src/Strata/Engine/BuiltinModules.h:26-27` names six modules: Scene, Renderer, Physics, Audio, Animation, Scripting | The table at `Strata/src/Strata/Engine/BuiltinModules.cpp:62-76` registers nine: also Input, World and GameUI. `BuiltinModules.cpp:80` refuses to exclude Input, Scene and Renderer; the comment at `BuiltinModules.h:21-22` names only Scene and Renderer | `core` |
| `engine` | `Strata/src/Strata/Scene/SceneRegistration.h:6-8` names one settings section, the collision layers | `SceneRegistration.cpp:22` also registers `Scene.Timing` | `core`, `world` |
| `engine` | `Docs/DeveloperGuide.md:828` writes `Tools/GenerateAssets.py` | The file is `StrataTests/FeatureTest/Tools/GenerateAssets.py` | `engineering`, `reference` |
| `inventory` | `plan/inventory/gameui.md:44` counts 12 UI components | `Strata/src/Strata/GameUI/GameUIComponents.cpp:211-397` registers 11 | `ui` |
| `engine` | `Docs/Architecture.md:2626` says that `GltfImporter` is version 9 | `Strata/src/Strata/Asset/GltfImporter.h:39` returns 11 | `assets`, `animation` |
| `engine` | `Strata/src/Strata/Core/Symbolizer.h:14` says that POSIX uses `dladdr` only | `Strata/src/Platform/Posix/PosixSymbolizer.cpp:32-35` reads the ELF `.symtab` on Linux | `scripting` |
| `engine` | `Strata/src/Strata/Input/UIActions.h:12-13` gives the UI's default bindings as Enter, Escape and the arrows | The defaults are `Strata/src/Strata/Input/InputActionSet.cpp:147-152`: Submit is Enter, keypad Enter, Space or gamepad A, as `StrataScriptCore/Include/StrataScript/UI.h:17-18` says | `ui`, `input`, `make` |
| `inventory` | The inventories count 151, 153 and 154 editor commands | `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` lists the 151 commands of `StrataEditorCore` (63 Edit, 46 Query, 42 Session), and `:234` checks that number. `StrataEditor/src/EditorLayer.cpp:177` and `:233` add `editor.showPanel` and `editor.showDialog`. Pages never type the count: they write `:value{key="commands.count"}` (style.md §13) | `editor`, `automation`, `reference`, `make` |
| `engine` | `Docs/DeveloperGuide.md:6397-6398` gives the tool definitions of every command, about 99 KB, as those of "151 commands" | The test that prints the figure counts the commands of `StrataEditorCore`'s registry (`StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:31`, `:114-125`). A running editor also registers `editor.showPanel` and `editor.showDialog` (`StrataEditor/src/EditorLayer.cpp:177`, `:233`), and every command it registers is a tool | `automation` |
| `engine` | `Samples/OpenWorld/CREDITS.md:11` and `ThirdPartyNotices.md:92` credit the Open World sample's fox (model CC0 1.0; rigging, animation and glTF conversion CC BY 4.0) without the upstream's two copyright lines | The license file beside the model in the Khronos glTF sample assets at commit `edc7c9e67c639d230715049ee31f9a96a6babbbe`, from which the sample took it, holds "© 2014, tomkranis." and "© 2017, @AsoboStudio and @scurest.". The book states the full credit, copied from that file with the link to that commit: `appendix/credits` holds the entry, and every figure that shows the fox names its authors and license in its caption (`plan/critique/rulings-6.md`, R22) | `animation`, `appendix`, and each part whose brief plans a picture of the Open World sample |
| `engine` | The archive's `README.md` (`Docs/Releases/PackageReadme.md:18`, `:20`) lists four samples, without the High Desert Outpost, and nine guides, without `Graphics.md` | `CMake/StrataPackaging.cmake:65` installs that file as `README.md`. The archive holds five samples (`Samples/Samples.json:6-38`; the whole folder is installed by `CMake/StrataPackaging.cmake:68`) and ten guides, `Graphics.md` among them (`Docs/Manual/`, installed by `:83`) | `start` |
| `engine` | `.claude/skills/strata-make-a-game/SKILL.md:470` says that an exported game has no `--help` and that it ignores unknown arguments | The game prints its usage for `--help` or `-h` and exits with code 0; for a command line it does not understand, it prints the problem and the usage and exits with the usage exit code (`StrataRuntime/src/RuntimeApplication.cpp:354`, `:372-375`, `:409`, `:429-440`) | `make` |
| `engine` | `Samples/Tetris/README.md:14` says that the sample's cells are "created and destroyed by a script" | The board creates its cells once and then only shows, hides and recolors them (`Samples/Tetris/Scripts/TetrisBoard.cpp:222-247`, `:355-369`); `git grep -n Destroy 822a7a46 -- Samples/Tetris/Scripts` finds nothing | `make` |
| `engine` | `StrataTests/Editor/TetrisCommands.json.in:28`, the Tetris sample's command script, waits 300 frames (`editor.wait {frames}`) | The engine's rule for tests is to wait by the clock or a condition, never by frames (`AGENTS.md:117-118`); the book's command scripts count game time in fixed steps (pipelines.md §6.2) | `make` |
| `engine` | `Docs/Roadmap.md:106` speaks of eleven built-in frame stages | `c_BuiltinFrameStages` holds twelve: eleven inside the work time and `Present` after it (`Strata/src/Strata/Core/FrameProfiler.h:67-81`) | `core` |
| `engine` | The comment at `Strata/src/Strata/Scene/SceneServices.h:28-29` names six services that `PhysicsSystem` offers | `PhysicsSystem` registers seven, `IPhysicsDiagnostics` among them (`Strata/src/Strata/Physics/PhysicsSystem.cpp:61-67`, `PhysicsSystem.h:54-55`) | `world`, `capstone` |
| `engine` | `Docs/DeveloperGuide.md:6235-6237` says that `RendererGPUStages::Get` registers the GPU stages in frame order with one exception, `GPU.DepthOfField` | `GPU.Aerial` is a second exception: it is registered before `GPU.Cull` (`Strata/src/Strata/Renderer/GPUProfiler.cpp:52-53`) and timed after it (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3360`, `:3381`) | `gpu` |
| `engine` | `Docs/Manual/Lighting.md:156` gives the sun's shadow 3, 4, 4 and 4 cascades at Low, Medium, High and Ultra, and `:160` speaks of "four 8192 texel cascades" at High and Ultra | The presets' row gives 3, 4, 5 and 5 (`c_ShadowCascadesRow`, `Strata/src/Strata/Renderer/RendererQuality.cpp:40`) | `light` |
| `engine` | `Docs/Manual/Lighting.md:180` says that at most 16 point and spot lights in view cast shadows | 16 holds at Medium, High and Ultra; Low allows 4 (`c_MaxShadowedLocalLightsRow`, `Strata/src/Strata/Renderer/RendererQuality.cpp:43`) | `light` |
| `engine` | `Docs/DeveloperGuide.md:4031` says that the five players' rows (`AntiAliasing`, `MotionBlur`, `DepthOfField`, `FilmGrain`, `ChromaticAberration`) only turn off what a scene uses; `plan/inventory/render-image.md:238` and `:565` say the same | The four comfort rows only turn off (`SceneEffectChoice`, `Strata/src/Strata/Renderer/RendererQuality.h:65-66`). The `AntiAliasing` row can also choose FXAA, TAA or Morphological, and then turns anti-aliasing on for a scene that has it off (`AntiAliasingChoice`, `RendererQuality.h:55-63`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:458-479`), as `Docs/Manual/AntiAliasing.md:58-59` says | `image` |
| `engine` | `Docs/DeveloperGuide.md:5682-5684` names the tone mapping's second binding layout `m_ColorLookupLayout` and its set `GetColorLookupSet` | The code names them `m_TonemapInputLayout` (`Strata/src/Strata/Renderer/SceneRenderer.h:2300`, `SceneRendererPost.cpp:109`) and `GetTonemapInputSet`, whose set holds the lens flare beside the lookup (`SceneRenderer.h:1663`, `SceneRendererPost.cpp:1167`); `git grep -n -e m_ColorLookupLayout -e GetColorLookupSet 822a7a46 -- Strata/src` finds nothing | `image` |
| `engine` | `Docs/DeveloperGuide.md:4466` writes `TonemapParameters::Sharpening` | The field is `Sharpening` of `RenderData::TonemapConstants` (`Strata/src/Strata/Renderer/PostProcessData.h:19`, `:28`); `git grep -n TonemapParameters 822a7a46 -- Strata/src Strata/shaders` finds nothing | `image` |
| `engine` | The comment at `Strata/src/Strata/Renderer/RendererComponents.h:313-314` says that screen-space reflections work "with TAA only" | Only the Checkerboard row reads the TAA's history; Spatial and SpatialHigh run with or without TAA (`Strata/src/Strata/Renderer/RendererQuality.h:88-91`) | `indirect` |
| `engine` | The comment at `Strata/src/Strata/Renderer/RendererQuality.h:166-168` gives the world-space global illumination 18 MiB per view at Low and 111 MiB at High | `GetMemory` gives 23,659,120 bytes at Low and 153,469,552 at High, 22.6 and 146.4 MiB (`StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:153`, `:167`), as `Docs/DeveloperGuide.md:4975-4976` says | `indirect` |
| `engine` | `Docs/DeveloperGuide.md:4974` gives the probe cascades 16 to 1,024 directions; `plan/inventory/render-indirect.md:164` and `:411` repeat it | Cascade 0 marches cascade 1's 64 directions: High's four cascades have 64, 64, 256 and 1,024 directions, Low's three 64, 64 and 256 (`Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:167-169`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:102-105`, `:127-129`) | `indirect` |
| `engine` | `Samples/PhysicsPlayground/README.md:16` calls the rule between the Ghost and Ball layers "the scene's layer matrix" in "Scene settings", and `:52` says that the layers were set with `scene.setSettings` | The layers are the project's: `Samples/PhysicsPlayground/PhysicsPlayground.stproj:25-39` holds `Scene.CollisionLayers` (Ball 1, Ghost 2, the pair in `NoCollisions`), and `scene.setSettings` refuses collision layers since 0.6.0 (`StrataEditor/src/Editor/EditorSceneCommands.cpp:568`, `:599-600`) | `physics` |
| `engine` | The comment at `Strata/src/Strata/Audio/AudioEngine.h:70-71` says that `AudioEngine::SetPaused` pauses all output "e.g. while the editor pauses the game" | Only tests call it (`StrataTests/src/Audio/AudioTests.cpp:148`, `:208`). The editor pauses the playing scene (`Scene::SetPaused`, `StrataEditor/src/Editor/EditorContext.cpp:1568`), and `AudioSystem::OnPausedChanged` pauses that scene's sources and one-shots (`Strata/src/Strata/Audio/AudioSystem.cpp:203-247`) | `audio` |
| `engine` | The comment at `Strata/src/Strata/Audio/AudioEngine.h:98-101` says that the Application calls `AudioEngine::AdvanceNullDevice` every frame | `AudioModule::OnUpdate` calls it while no output device pulls the mix (`Strata/src/Strata/Audio/AudioModule.cpp:29-35`); `Application` calls no module code (`AGENTS.md:218-219`) | `audio` |
| `engine` | The MCP server's instructions to the model (`StrataCLI/src/CLI/McpServer.cpp:39-40`) name eleven toolsets besides `core` and leave out `settings`; the guide's description of `settings` (`Docs/DeveloperGuide.md:6382-6385`) leaves out the prefix `graphics.` | The table of `StrataCLI/src/CLI/McpToolsets.cpp:43-69` holds twelve toolsets besides `core`: `graphics.` belongs to `settings` (`:54`), and `settings` is the twelfth (`:69`); `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:101-105` checks what `settings` holds | `automation` |
| `engine` | The first comment of `Samples/OpenWorld/Scripts/Wander.cpp:1-2` says that a fox's target stays inside its own world cell, so that it never walks into a cell that is not loaded | `Choose` (`Wander.cpp:68-77`) picks a spot 0.3 to 1 times `Range` (22 m, `:20`) from the fox's home and tests no cell. The Wildlife layer's cells are 64 m (`Samples/OpenWorld/Assets/Worlds/Island.stworld:2649`); 27 of the 30 foxes stand within 22 m of an edge of their cell, and none changes `Range` | `appendix` |
| `inventory` | `plan/inventory/gamedev.md:67` and `:272` count 40 registered components | The line's own list names 42, and `StrataTests/Architecture/ComponentSchema.json` holds 42, from the `ComponentRegistry::Register` calls of eight files under `Strata/src/Strata/`. `component.list` returns 39 of them: it leaves out the hidden `ID`, `Relationship` and `Inactive` (`StrataEditor/src/Editor/Commands/EntityCommands.cpp:619-620`; `Strata/src/Strata/Scene/ComponentRegistration.cpp:72`, `:90`, `:100`) | `make`, `reference` |
| `inventory` | `plan/inventory/gamedev.md:322` says that inactive entities get nothing | They get no `OnUpdate`, `OnFixedUpdate` or `OnLateUpdate` (`Strata/src/Strata/Scripting/ScriptSystem.cpp:276-280`), but `OnCreate` and `OnDestroy` run regardless (`ScriptSystem.h:55-56`; `ScriptSystem.cpp:664-679`), and a contact that began before the entity was deactivated still ends with its Exit (`StrataScriptCore/Include/StrataScript/Script.h:57-58`) | `make`, `basics` |
| `inventory` | `plan/inventory/foundation.md:173` counts 21 layers | `StrataTests/Architecture/Layers.json` holds 19, three of them tooling (`grep -c '"Name"' StrataTests/Architecture/Layers.json` prints 19) | `core` |
| `inventory` | `plan/inventory/foundation.md:264-266`, `:465-466` and `:551-552` say that Strata's registries open, accept and then freeze | Only the component and settings registries freeze (`Strata/src/Strata/Engine/BuiltinModules.cpp:159-160`). The asset loader, asset-manager extension, built-in asset, mesh geometry and scene-system registries, which the composition root opens beside the component registry (`:134-139`), stay open | `core`, `assets`, `world`, `worlds` |
| `inventory` | `plan/inventory/scene-ecs.md:293` and `:630` say that decomposing a matrix fails for shear | `DecomposeTransform` fails only for non-finite values, a homogeneous w near zero and a scale axis near zero (`Strata/src/Strata/Math/Math.cpp:12-33`, `:46-48`). It folds a mirror into a negative X scale (`:39-44`), and it drops a shear without a word: it makes a quaternion of the normalized columns as they are (`:35-37`, `:46`) | `world`, `basics`, `make` |
| `inventory` | `plan/inventory/render-core.md:162` and `plan/inventory/render-direct.md:205` time light culling and the light clusters in `GPU.Cull`, and the exercise of `render-direct.md:658` measures them there | `GPU.Cull` starts only on GPU-driven frames (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3343`, `:3360`). Light culling and the clusters are recorded after it (`:3365-3376`), so they are timed in `GPU.Cull` on GPU-driven frames and in `GPU.Setup` on frames of the CPU path (the timer starts in `GPU.Setup` at `:3289`) | `gpu`, `light` |
| `inventory` | `plan/inventory/assets.md` cites lines past the end of four headers of `Strata/src/Strata/Asset/`: `AssetRegistration.h:283-304`, `:319-330` and `:233-281` (its lines 44, 48 and 130; the header has 121 lines), `GltfImporter.h:262-282`, `:303-308` and `:262-309` (lines 45, 139 and 158; 57 lines), `AssetDependencies.h:349-386` (line 116; 56 lines) and `ImportRecordStore.h:85-163` (line 132; 111 lines) | The places at the pin: `AssetRegistration.h:72-93` (the `.meta` status, reader and writer), `:113-120` (`FindDuplicateHandles`), `:23-70` (the scan's phases, progress and options); `GltfImporter.h:10-21` (the sub-asset keys), `:29-55` (the class), `:52` (`EstimateImportMemory`); `AssetDependencies.h:30-52` (`Scan`, `ScanDocument`, `ScanEntities`, `ReferenceList`, `ScanEntity`); `ImportRecordStore.h:31-50` (the design note), `:51-109` (the class) | `assets` |
| `inventory` | Concept 16 of `plan/inventory/scripting.md` (lines 330-333) gives Simulate as the case where a gameplay service is absent | Scripts never run in Simulate: the Scripting system runs only in Play (`Strata/src/Strata/Scripting/ScriptingRegistration.cpp:15-17`; `ScriptSystem.h:36-37`). A host function reports an absent service when the engine has no physics, audio or animation module, or when the scene streams no world (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1172-1174`, `:2649`) | `scripting` |
| `inventory` | `plan/inventory/gameui.md:369-370` gives as a mistake "a menu unusable with a gamepad because nothing is focused" | With nothing focused, the first direction press or Submit focuses the topmost input canvas's `FirstSelected`, else its top-left selectable (`Strata/src/Strata/GameUI/GameUISystem.cpp:526-531`, `:539-542`, `:769-807`): the menu works, and that first press only focuses | `ui`, `make` |
| `inventory` | Concept 19 of `plan/inventory/worlds-runtime.md` (lines 298-300) says that the window mode, resolution and vsync the player chooses are kept in the save directory | The engine keeps only the graphics options, in `GraphicsOptions.json` of the save directory (`Strata/src/Strata/Runtime/GameGraphicsService.h:22-28`). `GameWindowService` applies window requests between frames and writes no file (`Strata/src/Strata/Runtime/GameWindowService.h:15-18`); a game that keeps its display settings saves them itself, as the Third-Person sample does (`Samples/ThirdPerson/Scripts/ThirdPerson.cpp:81`, `:97-98`) | `worlds` |
| `inventory` | `plan/inventory/editor-core.md:739` defines headless as running without a window or GPU (`--no-gpu`) | These are two options: `--headless` runs without a window and keeps the graphics device, so captures still work; `--no-gpu` runs without a graphics device and implies `--headless` (`StrataEditor/src/EditorApplication.cpp:70-71`, `:323-324`) | `editor`, `core`, `automation` |
| `inventory` | `plan/inventory/animation.md:219` names a "Showcase Fox (0.5.0 notes 38)" among the animated content of the samples | `Samples/Showcase` holds no fox and no animator; the fox of `Docs/Releases/0.5.0.md:38` is the Open World sample's (`Samples/OpenWorld/Assets/Prefabs/Fox.stprefab`) | `animation` |

## What a writer is given

1. `plan/style.md`; the page's row of the outline; the page's entries in `plan/tracks.md` (the page before and after it
   on each of its tracks); the part brief.
2. The page's allocation in `plan/allocation/<part>.md`. A page is complete when every allocated item is taught on it
   or passed on in its notes to a page that will teach it.
3. The page's persona: the least prepared persona of its tracks (from least to most prepared: B0, G0, E1), and E1 for
   a page on no track (style.md §1.2), with its Has and Has not lists (style.md §1.1).
4. The page's Needs closure, as style.md §1.2 defines it, computed from the Needs column of the outline (never chosen
   by the writer): for each page of the closure, its learn lines, its Summary section and the glossary terms whose home
   it is. A closure page that has not passed its own exit checks yet is given by its entry in its part brief.
5. Read-only access to the pin clone `G:/GameEngineAI/.worktrees/docs-pin` at the pin (the engine's code, its `Docs/`,
   `AGENTS.md` and skills), the dumps `reference/_dumps/<pin>/`, the glossary, `plan/inventory/` and `plan/research/`
   (background only: where a study and the plan differ, the plan decides).
6. On a page marked W8r: the section that its mark names. In phase A that section states no preset value in prose
   (`w8r-preset`, style.md §13).

A writer never starts an engine program, never reads `G:/GameEngineAI` or a worktree of the engine's work, and never
installs `node_modules`.

A writer returns:

- the page `src/content/docs/<part>/<chapter>.md`, with `status: draft`;
- its figure manifest, its tutorial file and the tutorial's files, its sketches (named `<part>-<chapter>-<name>`), and
  the solution files of its exercises;
- its notes `plan/notes/<part>/<chapter>.md`, with these level-2 sections:
  - `## Not verified`: what the writer could not check, for the technical reviewer;
  - `## Passed on`: allocated items passed to another page, each with that page's id;
  - `## New terms`: each with its one-sentence definition, its home (this page) and its aliases, for the glossary
    admitter;
  - `## Since`: the evidence for the front matter's `since` (the earliest release tag whose tree holds the subject);
  - `## Movable claims`: every claim of the page that wave 8 can move (numbers of shadowed lights, views per frame,
    noise, quality values, GI views), each with its source: a file and line at the pin, or a key of `values.json`.
    `None` on a page that wave 8 cannot touch. On W8 and W8r pages the section is required (`pin.py report` fails
    without it);
  - `## Requests`: changes asked of other pages and shared files (a lab, a tutorial asset and its credit line, teaching
    moved to a prerequisite);
  - `## Look hardest at`: what a reviewer should check first.

## The stages of a page

```
per part:  allocate → completeness critic (all parts) → brief
per page:  write → exit checks → first run (tutorials) → technical review  ─┐
                                                        provenance review ─┴→ fix → exit checks → confirms → integrate
per part:  edit pass
phase B:   pin moves → revisions → pictures → re-read after pictures → final runs → final
```

**Write and the writer's exit checks.** A page enters review only when every one of these passes (pipelines.md §13;
style.md §14):

```sh
python -I tools/excerpts.py fill --engine <clone> <page> && python -I tools/excerpts.py check --engine <clone> <page>
python -I tools/sketches.py check <page>
python -I tools/figures.py check --engine <clone> --dumps reference/_dumps/<pin>
python -I tools/tutorials.py check --dumps reference/_dumps/<pin> <page>     # tutorial pages
python -I tools/names.py check --dumps reference/_dumps/<pin> --engine <clone> <page>
python -I tools/lint.py <page>
python -I tools/pages.py check
```

- `excerpts.py check` refuses a quote in a draft form (an anchor in place of lines, pipelines.md §3.3): a page that
  still has one cannot enter review, so every reviewer sees the code the reader will see.
- The writer also checks, and the technical reviewer checks again: every allocated item is taught or in
  `## Passed on`; every learn id is in the `tests` of a Check-yourself answer (strips); the notes have their sections.
- After every fix the exit checks run again.

**First run (tutorials).** A tutorial page that passed its exit checks is run once before its technical review: the
integrator runs `tutorials.py run` on it (pipelines.md §6.3), one run at a time, inside the perf lock, with `--no-gpu`.
The run log and the stamp go to the technical reviewer. A tutorial whose commands need the GPU, and every tutorial
with a `patch` key, gets its first run in phase B; its technical reviewer reads its commands and its patch instead.
Editor exercises written as tutorial files run with their page.

**Technical review.** The technical reviewer is given the page, its notes, its allocation, its brief, the output of the
writer's exit checks (the names lint output among them), the run log and stamp of a tutorial, the figures'
`result.json` files where they exist, the dumps, and read-only access to the pin clone, the inventories and the
research. It:

- opens every quoted file at the pin and checks every statement about the engine against the code;
- checks every number against its source, and every claim about other engines or the field against a source it finds
  itself;
- checks the evidence for `since`, and that the page repeats no erratum of its brief;
- checks that the internals sections "The problem and how engines solve it" and "Alternatives Strata did not choose"
  have their sources in Further reading;
- judges the choice of quotes, and reports what the page should have quoted;
- writes `plan/reviews/<part>/<chapter>-technical.md`: findings `T1`, `T2`…, each with the sentence or fence, the
  evidence (a file and line at the pin, or a source), and a severity: *wrong*, *misleading*, *missing* or *weak*.

**Provenance review.** Runs beside the technical review, on the same draft, when every page of the page's Needs closure
has passed its own exit checks (in the pilot, the briefs stand in for unwritten closure pages). Its inputs, its method,
its findings and the fixer's limits are in [The provenance check](#the-provenance-check).

**Fix.** The fixer answers every finding in `plan/reviews/<part>/<chapter>-fix.md`: "fixed" with what changed, or
"rejected" with the reason. A *wrong* or *misleading* technical finding may be rejected only with evidence at the pin.
The provenance findings `untaught` and `order`, and walk findings where a step failed, cannot be rejected. The fixer
then runs the exit checks again.

**Confirms.** A confirm reads the fix, the finding and the evidence, and writes
`plan/reviews/<part>/<chapter>-confirm-<n>.md`. A fix it does not accept goes back to the fixer, and the confirm runs
again.

- A **technical confirm**, by the page's technical reviewer, runs for pages of size L and XL, for any page with a
  *wrong* finding, and for any page whose fences changed `src` or lines after the technical review
  (`excerpts.py list --since <commit the review read>`).
- A **provenance confirm**, by a fresh provenance reviewer, runs for every page with a fixed provenance finding.

**Integrate.** Per batch: the pages whose findings were all answered and whose confirms passed since the last batch.

1. The glossary admitter admits the batch's `## New terms` into `src/content/glossary.json`, one term per thing and
   two qualified entries for a word with two meanings, never the unqualified word (pipelines.md §9).
2. The integrator writes `status: reviewed` into each page whose review files show every finding answered and every
   confirm passed, builds the site with every check of site.md ("Checks"), stages the build and runs gate (a) on it
   (`tools/crawl.py`), and runs `npm run diagrams` for new diagrams.
3. It makes mechanical repairs only: link paths, front-matter syntax, fence fill, the sidebar. A content failure goes
   back to the page's fixer, never into an integrator's edit.
4. It lists the pages already reviewed whose Needs closure holds a page of the batch whose learn lines or Summary
   changed; each gets a provenance confirm of the sections that used what changed.
5. It commits each page in a commit of its own (see [Files and who writes them](#files-and-who-writes-them)) and pushes
   to `main` of the docs repository, never forced. If the docs repository is private, it pushes each batch to a branch
   `ci/<name>` instead, never single pages (`plan/critique/rulings-6.md`, R25). A failed CI run on `main` is repaired
   before the next batch is pushed.

**Edit pass.** A part's edit pass runs when every page of the part that phase A writes is integrated, and again in
phase B over the part's W8 pages, its W8r sections and what the pin moves changed. The part editor:

- checks one home per concept across the part and in its links into other parts: a page explains nothing whose home
  is another page, it says one sentence and links;
- checks terms against the glossary, repeats, the order of ideas, the flow between pages, and the brief's figure list
  against the manifests;
- writes the part's index paragraph and the five to ten cumulative exercises of `<part>/review`, each with a worked
  solution (style.md §7.7), for the 17 parts of eight or more pages: `make`, `basics`, `core`, `world`, `gpu`,
  `assets`, `draw`, `light`, `image`, `indirect`, `physics`, `animation`, `scripting`, `editor`, `editor-ui`,
  `engineering` and `reference`;
- sends a change that alters a claim, a fence or what a section teaches through the exit checks and the confirm of
  that kind.

**Phase B stages of a page.** At the final pin: its pictures are taken and judged; its re-read after pictures and, for
tutorials and level-1 pages, its second provenance check ([After the pictures](#after-the-pictures-phase-b)); its final
runs; then `final`.

**Status** (the front matter's `status`, style.md §6.1):

| Status | Holds when | Written by |
| --- | --- | --- |
| `draft` | the writer's exit checks pass | the writer |
| `reviewed` | every finding is answered and every confirm passed | the integrator |
| `final` | the page meets the [definition of done](#definition-of-done), at the final pin | the part editor |

A change to a page after `reviewed` keeps that status only when the change passed the exit checks and the confirm that
its kind of change asks for.

## The provenance check

The provenance check replaces a reviewer's feeling of being lost with a list that can be checked: every idea a page
uses must have a source that the page's persona can reach.

**Who and when.** A provenance reviewer is an Opus agent that is not the page's writer and has no access to the
engine's source: no pin clone, no inventories, no engine documents, no research files. It reviews a page after the
page's exit checks pass and after every page of its Needs closure has passed its own exit checks. In the pilot only, a
closure page that is not written yet is given by its entry in its part brief (what it covers and its draft learn
lines); when that page passes its exit checks, the pilot page gets a provenance confirm against it.

**What the reviewer is given.**

1. The page with its quotes filled, its figure manifest (captions and alternative texts) and, for a tutorial, its
   steps.
2. The reading report that `tools/lint.py` writes for the page (style.md §2.2).
3. The page's persona with its Has and Has not lists (style.md §1.1) and the rule that chose it (style.md §1.2).
4. The page's Needs closure, computed from the Needs column of the outline, not from the writer's choice: the page's
   Needs, their Needs, and so on; the first page of the part for a row with `-`; for a Need `a|b`, only what both `a`
   and `b` (with their closures) teach. For each page of the closure: its learn lines, its Summary section and the
   glossary terms whose home it is. Nothing else of those pages.
5. The glossary.

**What the reviewer does.** For each level-2 section of the page, in order:

1. It lists every item that the section uses: each idea, term, symbol (in prose, formulas and code), C++ feature,
   programming construct, UI action (a menu, a panel, a shortcut, a drag) and tool (a program, a command, a file
   format).
2. For each item it names the source, which is one of:
   - an item of the persona's Has list, by its number ("G0 Has 6");
   - a page of the closure, with the learn id, the Summary item or the glossary term;
   - an earlier sentence of this page, quoted.
3. An item without a source is a finding `untaught`, with the sentence that uses it. An item used on the page before
   the sentence that teaches it is a finding `order`, with both sentences.

Then, for the whole page:

4. **Reading.** It upholds or dismisses each warning of the reading report (`noun-stack`, `passive`), and reports
   idioms, phrasal verbs and words beyond a reader at CEFR level B1 that the linter's lists let through (`reading`).
5. **Steps.** It reports every step whose "You should see" names nothing the reader can see or check, and every action
   that assumes a state the steps have not reached (`step`).
6. **Why.** On a page whose persona is B0, it reports every "why" that the page raises, or that a B0 reader would ask,
   which neither the page nor a page on track B answers (`why`).
7. **Answers.** It answers every Test out question, every Check-yourself question and every conceptual exercise from
   the page and its closure only, then compares its answers with the page's hidden answers. A question it cannot answer
   from them, or whose answer differs from the page's, is a finding `answer`. Code exercises are judged by the runs of
   their solution files (sketches, tutorial files, patches, and their stamps), never by the reviewer.

**What it returns.** `plan/reviews/<part>/<chapter>-provenance.md`:

- for each section, a table: Item, Kind, Used in (the sentence), Source;
- for each learning objective, one row of a table: the learn id and its text; the questions whose `tests` name it
  (Test out, Check yourself, Exercises, Practice); whether the reviewer answered each of them from the page and its
  closure only (step 7), with the finding where it could not; and whether the page's Summary holds the objective's
  sentence;
- the findings `P1`, `P2`…, each with its type (`untaught`, `order`, `reading`, `step`, `why`, `answer`), its
  section, the sentence quoted, what is missing, and the learn ids of the objectives it touches;
- the number of items listed, and of findings per type.

**What the fixer may do, and may not do.**

- An `untaught` or `order` finding cannot be rejected. The fixer may only:
  1. teach the item on the page before its first use (for `order`: move the teaching or the use);
  2. remove the use, when the page does not need the item;
  3. move the teaching to a page of the Needs closure, naming the page and its section. The fixer does not edit that
     page: it writes the request in the notes' `## Requests`; the planner starts a fix on that page; the finding stays
     open until that page teaches the item, and the confirm reads both pages.
- The fixer may not close such a finding with a link to a page outside the closure, add a Need (only the planner
  changes the outline), delete what a rule requires (a learn line, the question that tests it, a step's "You should
  see"), or edit another page.
- A `reading`, `step`, `why` or `answer` finding may be rejected only with a reason that can be checked: for `reading`,
  the rule that the sentence meets; for `answer`, the sentence of the page or of the closure that gives the answer.

**Confirm.** A fresh provenance reviewer, given the same inputs and the fixed page, checks each fixed finding and each
rejection. It reports new findings only in text that the fix changed. A fix it does not accept goes back to the fixer.

### After the pictures (phase B)

- **Every page with figures**: once its pictures are taken, a provenance reviewer that sees the pictures re-reads every
  caption, every alternative text, and the paragraph before and after each `::figure` and `::compare`. It reports
  each place where the text points at something the picture does not show (`picture`).
- **Tutorials and level-1 pages** (the level of style.md §6.2): a second provenance check, as above, with the pictures.
- Both write `plan/reviews/<part>/<chapter>-reread.md`, and their fixes are confirmed by a fresh provenance reviewer.
  `final` requires both where they apply.

## Track walks

A track walk tests a track as a whole: a fresh agent with the track's persona, the built book and the program a reader
has, following the track's list in `plan/tracks.md`.

| Walk | When | Entries of the track | Engine program |
| --- | --- | --- | --- |
| G, first | after wave 2 | track G from `start/install` (entry 3) to `make/project-coin-run` (entry 29) | the pin build, `--no-gpu` |
| G, final | phase B, step 16 | track G from `start/install` (entry 3) to `make/project-platformer` (entry 54) | the official v0.8.1 Windows package |
| E, final | phase B, step 16 | track E from `start/install` (entry 3) through `core/first-change` (entry 38) to `world/tutorial-component` (entry 63) | the official v0.8.1 Windows package; the pin clone's patch build for changes to the engine |

- **What the walker has.** The persona's lists (G0 or E1); the built book (the staged site of `main` for the first walk,
  the release's site for the final walks); the engine program; a terminal; and a work folder
  `G:/GameEngineAI/.worktrees/docs-work/walk-<track>-<first|final>`. It has no plan files, no inventories and no
  tutorial files, and of the engine's source only what a page tells the reader to open, read in the pin clone.
- **No Strata data of the owner.** `STRATA_SESSION_DIR` is a new folder in the user's temporary folder;
  `STRATA_RECENT_PROJECTS` and `STRATA_SCRIPT_BUILDS_DIR` point into the work folder; every project is made in the work
  folder (pipelines.md §2). The preferences file cannot be redirected at the pin
  (`StrataEditor/src/Editor/EditorPreferences.cpp:61-66`): the walker never changes preferences and logs each step that
  depends on them.
- **Steps.** No agent controls the owner's screen. The walker does each step through its command tab with `StrataCLI`
  (pipelines.md §2, "Driving editors"), and compares the step's editor tab with the pictures that the page shows (which
  exist in phase B). Every engine program runs as
  [Not interfering with the engine's work](#not-interfering-with-the-engines-work) says. In the first walk, steps that
  need what phase A cannot give (the release download, the GPU) are logged as not walked; the final walk walks them.
- **Engine changes.** Steps that build or change the engine (`core/first-change`, `world/tutorial-component`) are done
  in the pin clone's patch build `build/docs-patch` (pipelines.md §6.6): the walker writes the change the page describes
  as a patch in its work folder, and the integrator applies, builds, tests and reverts it as `tutorials.py patch` does.
  The walker makes no clone and no build folder of its own.
- **Side steps.** It takes a side step only where it cannot go on without it, and logs that.
- **The log.** `plan/walks/<track>-<first|final>.md`: one entry `WK1`, `WK2`… for every place where it had to guess,
  left the book, met a "You should see" that did not match, or ran a command that failed; each with the track entry,
  the page, the step or section, what it did and what happened.
- **Findings.** Each entry goes to the page's fixer. An entry where a step failed or did not match cannot be rejected.
  A fresh walker confirms the fix by repeating the steps from the stage's start state.
- **People.** The owner is invited to walk one tutorial by hand in a windowed editor, and to give the book to a real
  beginner. The book is checked by personas and agents, and does not wait for either.

## Files and who writes them

Inside the docs clone, every agent writes only the files of its role in this table. Two page pipelines never write
the same file. Paths are those of site.md ("Layout of the repository") and pipelines.md §12.

| Files | Hold | Written only by |
| --- | --- | --- |
| `src/content/docs/<part>/<chapter>.md` | pages | the writer, then the fixer, then the part editor; the integrator for mechanical repairs only (link paths, front-matter syntax, fence fill, `status: reviewed`); `excerpts.py fill`, `sketches.py fill` and `figures.py fill` write fence bodies and `src` |
| `src/content/docs/<part>/index.md`, `review.md` | part pages | the part editor (its paragraph and exercises); the build draws the generated parts |
| `src/content/figures/<part>/<chapter>.json` | figure recipes | the writer, the fixer |
| `src/assets/figures/<part>/<chapter>/` | published pictures, `taken.json`, `*.result.json`, text figures | `figures.py publish`, run by the photographer (text figures in phase A: by the integrator) |
| `originals/<sha256>.png` (ignored, never committed) | the PNG original of every published picture | `figures.py publish`, run by the photographer |
| `layouts/<name>.ini` | editor layouts for pictures | the photographer |
| `labs/<name>.json`, `labs/<name>/` | labs | the lab's owner page, named in the brief; other pages ask in `## Requests` |
| `sketches/<part>-<chapter>-<name>.<ext>` | sketches | that page's writer and fixer |
| `tutorials/<part>/<chapter>.tutorial.json`, `.patch`, `tutorials/<part>/<chapter>/` | tutorials, patches, their files, exercise solutions | the writer, the fixer |
| `tutorials/<part>/<chapter>.stamp.json` | stamps | `tutorials.py run` and `patch` |
| `tutorials/assets/` | tutorial assets | the asset's owner page, named in the brief; `tutorials/assets/CREDITS.md` by the integrator, from the `## Requests` of the notes |
| `public/downloads/tutorials/<part>/<chapter>/`, `public/downloads/tutorials/<part>/<chapter>.patch` | reader copies, end-state archives, patches | `tutorials.py compile` and `run` |
| `public/downloads/solutions/<part>/<chapter>/` | the downloads of worked solutions | `tutorials.py compile` |
| `labs/CREDITS.md` | the credits of the labs' third-party files | the integrator, from the `## Requests` of the notes |
| `public/downloads/labs/<name>.zip` | lab downloads | `figures.py labs`, run by the integrator |
| `public/third-party-notices.txt` | the notices the site serves | `notices.py write`, run by the integrator |
| `tools/data/notices.json` | what the site ships: per component its package, version, license id and copyright lines | first the tool builder; afterwards whoever changes `package-lock.json`, in the same commit |
| `reference/_dumps/<pin>/` | dumps and parsed tables | `reference.py dump` and `parse`, run by the tool builder |
| `reference/_examples/` | example results of commands | `tutorials.py run --record-examples` |
| `src/generated/reference/` | rendered tables, `values.json` | `reference.py render`, run by the tool builder |
| `src/generated/diagrams/` | prerendered diagrams | `npm run diagrams`, run by the integrator |
| `src/content/glossary.json` | the glossary | the glossary admitter, one at a time |
| `src/sidebar.json`, `src/redirects.json`, `src/published-pages.json` | navigation and moved pages | the integrator |
| `engine.pin` | the pin | `pin.py move`, run by the integrator during a freeze |
| The tools that pipelines.md specifies (`excerpts.py`, `sketches.py`, `figures.py`, `tutorials.py`, `reference.py`, `names.py`, `lint.py`, `pin.py`, `wordlists.py`, `notices.py`) and `tools/pages.py`, with their modules in `tools/booklib/`; `tools/data/`, `tools/schemas/`; the scripts that pipelines.md §12 names | the book's tools | the tool builder |
| `src/plugins/`, `src/lib/`, `src/integrations/`, `src/components/`, `src/pages/`, `src/styles/`, the other `scripts/`, `deploy/`, `.github/`, `astro.config.mjs`, `ec.config.mjs`, `package.json`, `package-lock.json`, `site.json` (its values are the owner's: `plan/critique/rulings-6.md`, R24); the tools that site.md specifies (`crawl.py`, `servertest.py`, `release.py`, `budgets.py`, `measure.py`, `bootstrap.py`, `deployfiles.py`, `cistatus.py`, `toolchain.json`), with their modules in `tools/booklib/` | the web project | the site builder |
| `plan/` except the rows below; `plan/briefs/<part>.md` | the plan, the rulings, the briefs | the planner |
| `plan/spike-report.md` | the spike's report | the site builder |
| `plan/allocation/<part>.md` | allocations | the part's allocator |
| `plan/allocation/completeness.md` | the completeness report | the completeness critic |
| `plan/notes/<part>/<chapter>.md` | a page's notes | the writer, then the fixer |
| `plan/reviews/<part>/<chapter>-<stage>.md` | reviews and answers; `<stage>` is `technical`, `provenance`, `fix`, `confirm-<n>`, `pictures` or `reread` | each its own author |
| `plan/walks/<track>-<first\|final>.md` | walk logs | the track walker |

Outside the repository, never committed: the pin clone `G:/GameEngineAI/.worktrees/docs-pin` and its builds, the
release packages `docs-package-<version>`, `docs-baselines`, the work folders `docs-work/<tool>` and
`docs-work/walk-…`, and the session folders in the user's temporary folder.

**Who commits.** During page work the integrator is the only agent that commits and pushes. Every other agent leaves
its files in the docs clone and reports them; the site builder and the tool builder hand over each finished change
with its commit message. Before page work (order steps 4 and 5) there is no integrator: the site builder and the tool
builder commit their own files, each commit naming its paths, and the site builder pushes only the branch `ci/site`
(`plan/critique/rulings-5.md`, R16). The owner has allowed pushing; the repository is public for now, so the first
push waits only for `LICENSE` and the footer's line in the tree (`plan/critique/rulings-6.md`, R27). CI's result is
read through git, for a private repository as for a public one: CI's last job, `report`, commits `runs/<commit>-<attempt>.json` (every job's conclusion and every `::error`
annotation) to the branch `ci-results`, and `tools/cistatus.py <commit>` fetches that branch and prints the result
(R25; site.md, "CI"). `main` moves by the planner's fast-forward push when CI is green; nobody forces a push.

- One commit per page: the page and its own files (manifest, tutorial files and stamps, sketches, notes, reviews),
  staged by path. The subject is `Add <part>/<chapter>: <title>` for the page's first commit and
  `Revise <part>/<chapter>: <what changed>` after it. Glossary admissions, the sidebar and tool or site changes are
  commits of their own.
- The integrator never commits a file of a page outside its batch.
- The integrator's kit: the pin clone, the pinned Node.js and Python tools in `.tools/`, the dumps, and the
  `node_modules` of its own `npm ci`.
- Only the integrator runs `npm ci`, in the docs clone, and again whenever `package-lock.json` changes. Site builds use
  that `node_modules` and run one at a time: the integrator's, or the site builder's while it works on the web project.
  Writers and reviewers run only the Python tools.
- **Freeze.** The pin moves only during a freeze: the planner starts no page pipeline, every open pipeline reaches
  integrate, and then the integrator runs `pin.py move` (pipelines.md §10).

## Order

### Phase A: before engine release 0.8.0

Text is written against the pin `822a7a46` (`engine.pin`: `release 0.8.0`, `prerelease yes`). No docs agent uses the
GPU, except the photographer for the four captures of the checks before writing (pipelines.md §5.4;
`plan/critique/rulings-7.md`, R34).

1. **Survey (done).** The inventories of the engine's 19 areas (`plan/inventory/`) and three studies (framework,
   curricula, captures: `plan/research/`), at `822a7a46`.
2. **Critique (done).** Ten critics read the plan: a complete beginner, a game maker, a curriculum editor, five
   completeness critics (foundation, rendering in two parts, simulation, editor), a site operator and a pipelines
   critic. `plan/critique/summary.md` merges their reports: 8 blockers, 62 major and 41 minor findings.
3. **Revision (done).** The planner ruled on the critique (`plan/critique/rulings-1.md` to `rulings-3.md`); a finding
   that no ruling names is accepted as the summary states it. The plan's files were revised by the rulings;
   `plan/critique/dispositions.md` records the outcome of each finding. The planner read the revised plan and
   decided what it left open (`rulings-4.md`: four sizes, the split of `basics/math-change`, the place of
   `editor/projects`, and what the briefs and the tool builder must do). The outline is final, and
   `plan/check_outline.py` passes.
4. **The spike's verdict.** The site builder changes the spike to meet site.md ("The spike against this file"), builds
   the scale test from the outline's 335 rows at their sizes, measures every row of site.md's budget table, and writes
   the report: each row's value, pass or fail, the remedy tried, and the verdict (`.tools/spike-report.md`, copied to
   `plan/spike-report.md` when final). A row that still fails after its remedy fails the spike: then the fallback is
   built at the same scale and measured against the same table. The planner reads the report and settles site.md's
   "(spike)" places. No page of the book is written before a passing verdict.
   The first spike, built against the plan as it stood before the critique, passed on the framework
   (`plan/critique/rulings-5.md`, R12): the fallback is not built, and what remains of this step is the completed
   site's report. The owner has allowed pushing, and the first push is the CI stage's, of the branch `ci/site`
   (`plan/critique/rulings-6.md`, R27). Until then rows 8, 15 and 16 are measured on the authoring machine (Windows,
   both nginx versions), and again on `ubuntu-latest` once the branch `ci/site` is pushed (R16); rows 2, 3 and 14
   stay open. By R12 none of them holds the pilot back.
5. **The pin build and the tools** (beside step 4). The tool builder makes the pin clone and its one Release build at a
   time the planner chooses (pipelines.md §1.3). It brings the tools to pipelines.md, each with its unit tests:
   `excerpts.py`, `sketches.py`, `figures.py check`, `tutorials.py check`, `compile` and `run`, `reference.py`,
   `names.py`, `pin.py`, `lint.py`, `notices.py` and `pages.py`. It runs `reference.py dump`, `parse` and `render` at
   the pin, so that the dumps the exit checks read exist.
6. **Glossary seed** (beside steps 4 and 5). The glossary admitter writes 400 entries of a beginner's base
   vocabulary, each with its home on a page of `start` or `basics` (pipelines.md §9). The seed is `plan/glossary/seed.json`
   until the spike's verdict; then it becomes `src/content/glossary.json`.
7. **Allocation** (beside steps 4 and 5; it reads only the plan and the pin clone). The allocators, the check, the
   completeness critics, and the planner's settling ([Allocation and part briefs](#allocation-and-part-briefs)). The
   inventories' terms, about 1,590, then enter the glossary, one entry per term, their homes taken in the
   order of pipelines.md §9 (`plan/README.md`, step 5; `plan/critique/rulings-7.md`, R33).
8. **Part briefs.** The planner writes the 25 briefs. Once the pin build exists, and before the briefs of the pages that
   wait for them, the photographer takes the four captures of the checks before writing (pipelines.md §5.4).
9. **Pilot.** Seven pages pass every stage of phase A:

   | Page | Kind, size | Tracks | Persona | What it tries |
   | --- | --- | --- | --- | --- |
   | `start/install` | how-to, M | G, E, B | B0 | steps with tabs per OS; the first page where a beginner can fail |
   | `basics/programming-1` | primer, L | G, B, E | B0 | programming from zero, with a Strata script as the playground |
   | `basics/math-vectors` | primer, L | B, E (side step of G) | B0 | a mathematics primer |
   | `make/first-script` | tutorial, M | G, B | B0 | a tutorial, run and stamped with the pin build (`--no-gpu`) |
   | `core/time` | concept, L | E | E1 | a concept page |
   | `world/ecs` | internals, L | E | E1 | an internals page |
   | `image/tone-mapping` | internals, L | E | E1 | rendering internals: its recipes pass `figures.py check` offline; its pictures are taken in phase B |

   The planner reads the seven pages as their personas would, corrects style.md and the briefs, and records the work
   that each page took per stage. The pilot's pages belong to waves 1, 2 and 4; those waves do not write them again,
   and their parts' edit passes include them.
10. **Waves 1 to 6.** Each wave is a workflow over its pages, one pipeline per page. A wave may be written in several
    writing batches, each a workflow over some of the wave's pages (`plan/critique/rulings-7.md`, R30). No page of a
    wave needs a page of a later wave: `plan/check_outline.py` proves it, and its table `WAVES` is this one.

    | Wave | Parts | Pages | Estimated words |
    | --- | --- | --- | --- |
    | 1 | `start`, `basics`, `core`, `world` | 63 | 293,500 |
    | 2 | `make` block A, `gpu` | 33 | 141,000 |
    | 3 | `assets`, `make` block B without its W8 pages | 32 | 151,000 |
    | 4 | `draw`, `light` without its W8 pages, `image`, `physics`, `audio`, `input` | 67 | 291,000 |
    | 5 | `indirect` without its W8 pages, `animation`, `scripting`, `ui`, `worlds`, `editor`, `make` block C | 64 | 281,000 |
    | 6 | `editor-ui`, `automation`, `engineering`, `capstone` | 40 | 199,000 |
    | B | phase B: the 7 W8 pages, `reference` (22 pages), `appendix` (7 pages) | 36 | 155,000 |

    Rulings 3 put `editor` in wave 3 and `scripting` in wave 4. The check found seven Needs on a later wave:
    `scripting/script-system` needs `animation/time-events`; `editor/play-mode` needs `scripting/script-system`;
    `editor/worlds` needs `worlds/streamer`; `editor/script-builds` needs `scripting/hot-reload`; `editor/stepping`
    needs `input/simulated`; `editor/placement` and `editor/camera-viewport` need `draw/bounds-culling`. As the ruling
    says (fix the wave list, not the Needs), `editor` and `scripting` moved to wave 5.

    Inside a wave:

    - Writing does not wait: every page's pipeline starts with the wave, or with its writing batch. A page's
      provenance review waits until every page of its Needs closure has passed its exit checks.
    - `editor/placement` is written last in wave 5. `editor-ui/scene-view` is written last in wave 6 but for
      `editor-ui/game-view`, which needs it and follows it. Both are read again at every pin move.
    - A W8r page is written in its wave; the section its mark names states no preset value in prose.
    - After wave 2: the first track G walk.
    - After each wave, before the next one starts, the planner reads a sample: at least one page of each kind in the
      wave and every XL page. It corrects the briefs and style.md for the later waves, and sends the pages the sample
      shows wrong back to their fixer.

### Phase B: after engine release 0.8.0

11. **The pin moves to v0.8.0.** A freeze; `pin.py move` to the commit of the tag `v0.8.0` (`release 0.8.0`,
    `prerelease no`); then, in this order: the pin build again (in the same clone and folder); `reference.py dump`,
    `parse` and `render`; `names.py check` and `excerpts.py check` on every page; `tutorials.py run` (pipelines.md
    §10.2). The pages that the pin report lists are revised and confirmed: quotes that moved, changed or are missing;
    tutorials to run again; numbers in the prose of pages that link to a changed generated table; and the `## Movable
    claims` of every W8 and W8r page, reviewed again with the report. These pages are read again whether or not the
    report lists them: `assets/references`, `animation/root-motion`, `world/interpolation`, `editor/placement`,
    `editor-ui/scene-view`, `light/units-exposure` (its sentence on the units of rectangle lights is a movable claim),
    and `reference/assets` once it is written.
    The planner reads the 0.8.0 release notes (`Docs/Releases/0.8.0.md` at the tag) beside the report. The plan
    expects area lights in 0.8.0, and expects that the animation graph, volumetric fog, new showcase materials and new
    placement tools are not in it. A feature the notes list that no page holds is allocated to a page (a new row only
    with `plan/check_outline.py` passing); an entry of "What Strata does not do" (book.md) that the release contradicts
    is corrected.
12. **Wave B.** Through the stages of a page:
    - the 7 W8 pages are written: `make/lamps`, `make/gi`, `light/area-lights`, `light/local-shadows`,
      `indirect/gi-voxels`, `indirect/gi-cascades`, `indirect/gi-limits`;
    - the 7 W8r pages have the section of their mark revised: `make/look` (the effects' quality presets),
      `make/quality` (the presets table), `make/performance` (the `renderStats` keys and the Performance panel's
      numbers), `gpu/frame-tour` (the list of passes and the statistics they report), `light/lights` (light components
      and records), `light/many-lights` (the forward light loop), `image/quality-settings` (the quality rows and their
      presets);
    - the 22 pages of `reference` are written (most of them around their generated tables), and the 7 pages of
      `appendix`.
13. **v0.8.1, the final pin.** The engine additions of pipelines.md §11 (tiers 1 and 2, and the tier 3 items requested
    with the figures that need them) are engine work: the engine's agents make them under the engine's rules, land them
    on the engine's `main` through its CI, and ship them as v0.8.1. The planner hands them the request list
    (`figures.py list --waits`) and, with it, the list of findings that pipelines.md §11 holds beside the additions:
    what the allocation found in the engine, the errata of kind `engine` among them (`plan/critique/rulings-7.md`,
    R34); no docs agent changes the engine. Then a freeze, and the move to the commit of the tag
    `v0.8.1` with every step of step 11. v0.8.1 is the book's final pin, for text and pictures alike.
14. **Pictures.** At the final pin, with the GPU and one run at a time, the photographer runs `figures.py take` of every
    kind and `tutorials.py run --pictures`. It judges each picture against its recipe's `shows` line, and each picture
    of a tutorial's step against the step's text, in `plan/reviews/<part>/<chapter>-pictures.md`; a picture that does
    not show what it must is taken again or its recipe is changed. "Before" pictures come from the engine's look-dev
    baseline sets of older releases, named with their tag. The sets are not committed in the engine repository
    (`Docs/DeveloperGuide.md:769-773` at 822a7a46): the planner copies them once, read-only, to
    `G:/GameEngineAI/.worktrees/docs-baselines/` after confirming that their folders still exist (pipelines.md §5.5). A figure whose engine addition did not
    ship in v0.8.1 is replaced by its diagram. Then the re-read after pictures and the second provenance checks
    ([After the pictures](#after-the-pictures-phase-b)). The pictures of wave 8's features are offered to the engine's
    agents for the engine's release notes and Manual.
15. **Final runs.** `tutorials.py patch` for every tutorial with a `patch` key; `tutorials.py run` with the official
    v0.8.1 Windows package (pipelines.md §1.3); the check of the frame captures of `gpu/debugging` and `gpu/frame-tour`
    (pipelines.md §11); the stamps at the final pin. A run that fails goes back to the page's fixer.
16. **Final track walks.** The final walks of tracks G and E ([Track walks](#track-walks)), and the fixes of their
    findings.
17. **Edit passes and the release.** Every part's edit pass over what phase B changed; `final` page by page; the release
    build with every check and `--release` (a missing picture or stamp is an error); the release that site.md
    ("Deployment") describes: the site, the deploy folder, `SHA256SUMS` and the archive of the PNG originals. The owner
    gets the release and `deploy/README.md`.

## Not interfering with the engine's work

The engine's own agents work in worktrees of `G:/GameEngineAI` on the same machine, and measure performance under the
engine's perf lock (`Tools/PerfLock.py`). The docs work stays out of their way:

- Allocators, writers, reviewers, fixers and editors only read code and write text. They may run beside the engine's
  agents.
- The engine is read only from the pin clone `G:/GameEngineAI/.worktrees/docs-pin`, a separate clone (pipelines.md
  §1.2). No docs agent reads or writes `G:/GameEngineAI` itself or a worktree of the engine's work, and none commits
  to the engine's repository.
- **One pin build per pin.** The tool builder builds the pin clone once in Release, at a time the planner chooses, with
  `--parallel 2 -- /p:CL_MPCount=4` (the engine agents' form), inside `Tools/PerfLock.py --label docs-pin-build`, in
  slices that each hold the lock for less than its default limit of 25 minutes (pipelines.md §1.3); a pin move builds
  again in the same folder. The only other build of the engine is the patch runner's `build/docs-patch` in phase B
  (pipelines.md §6.6). No docs agent builds anything else of the engine.
- **One engine program at a time.** Every engine program that a tool or a walker starts runs inside
  `Tools/PerfLock.py`, with a private `STRATA_SESSION_DIR` and the work-folder variables of pipelines.md §2. At most one
  docs agent runs or waits for an engine program at any time; the planner's workflow orders them. PerfLock's exit codes
  75 (no lock within 30 minutes) and 124 (over the limit) are failures: the run is tried again later, never in a loop.
  An engine agent's perf run waits 30 minutes for the lock and then fails. So while engine agents work, no hold of the
  book's is longer than PerfLock's default limit of 25 minutes, and the book's runs wait with `--wait 120`
  (`plan/critique/rulings-5.md`, R19).
- **No GPU in phase A** but for the four captures of the checks before writing, which the photographer takes one at a
  time (pipelines.md §5.4). Every other editor runs with `--no-gpu`. In phase B only the photographer's runs
  (`figures.py take`, `tutorials.py run --pictures`), the patch runner and the final track walks use the GPU, still one
  at a time.
- No tool calls `preferences.set` or `preferences.save`, and the owner's recent projects and script builds are never
  read or changed (pipelines.md §2).
- The engine additions of v0.8.1 are made by the engine's agents, under the engine's review and CI.

## Order of the work and of cuts

The work is large: 335 pages, and each one passes through at least four agents (writer, technical reviewer, provenance
reviewer, fixer), plus its runs, confirms, re-reads and its part's edit pass. Rules:

- The work is ordered so that what is finished is a coherent book: the waves in the order above, each wave finished
  before the next one starts, never many parts half done.
- The pilot measures the work that one page of each kind and size takes, per stage (agent runs, their length, the
  findings per review). The planner plans the waves from that measurement.
- After the pilot and after every wave, the planner compares the work done with the work that remains, and reports both
  to the owner.
- If depth must be cut, it is cut in this order, and the planner records each cut in the briefs of the parts it
  affects:
  1. exercises and questions at the minimums of style.md §8 (three Check-yourself questions, one exercise, three
     Practice items on primers);
  2. the technical confirm only where a *wrong* finding or a changed fence asks for it, not for every L and XL page;
  3. shorter prose on reference pages (the generated tables stay complete);
  4. the second provenance check after the pictures only for tutorials of tracks G and B, not for every level-1 page.
- Never cut: the writer's exit checks; the technical review; the provenance review and its fresh confirm; the one-home
  rule; the excerpt check at every pin; the track walks; the re-read of captions after the pictures.

## Definition of done

A **page** is done (`final`) when, at the final pin:

1. every item of its allocation is taught on it, or passed on to a page that teaches it;
2. every claim survived the technical review, and every confirm passed;
3. no provenance finding `untaught` or `order` is open, and a fresh provenance reviewer confirmed every fix;
4. every learn id is tested by a Check-yourself answer; every question and exercise has its answer; every code
   exercise's solution passes its run (a sketch check, a current stamp);
5. its quotes match the final pin (`excerpts.py check`), and its names pass `names.py check` against the final pin's
   dumps;
6. its pictures exist and show what their recipes' `shows` lines say; its re-read after pictures, and for a tutorial or
   a level-1 page its second provenance check, have no open finding;
7. a tutorial has a stamp that is current at the final pin, as pipelines.md §6.4 defines it;
8. every track-walk finding that names it is fixed and confirmed;
9. its part's edit pass is done;
10. the site's checks pass with `--release`.

The **book** is done when:

1. all 335 pages of the outline are `final`, and the 17 parts of eight or more pages have their index and review pages;
2. every inventory item has exactly one home (`plan/allocation/completeness.md` has no open row);
3. the reference holds every component that `component.list` returns, with the hidden and `NoSerialize` components
   listed from the source, every command, every settings and preferences section, every host function and SDK name of
   the script API, and every asset type; counts in prose come from `values.json` or from a test that the page names;
4. every figure that the briefs assign exists at the final pin, or was replaced by its diagram because its engine
   addition did not ship;
5. the final walks of tracks G and E have no open finding;
6. the pin is v0.8.1, and `pin.py report` reports nothing at it;
7. the release build passes every check of site.md with `--release`, and the staged site passes gates (a), (b) and (c)
   under `/strata-engine-docs`;
8. the owner has the release (the site, the deploy folder, `SHA256SUMS`, the archive of originals) and
   `deploy/README.md`, and has deployed it or has all that is needed to do so.
