# Hand-written tables of the reference and appendix pages

Collected by script from the `## Hand-written tables` sections of `plan/notes/reference/*.md` and
`plan/notes/appendix/*.md` (the clerk after wave B, 2026-11-17). Each table was read by hand from the engine at the
pin `822a7a46`; after the pin moves (rulings-12.md, R56, step 2), each is checked again against the files named.
A page whose section says "None" is left out.

## reference/animation

Page: `src/content/docs/reference/animation.md`; notes: `plan/notes/reference/animation.md`.

All tables are hand-written; src/generated/reference/ holds no animation table. Each was read at the pin from:
- Controller format keys, parameter kinds, condition operators: `Strata/src/Strata/Animation/AnimationController.h`, `AnimationController.cpp` (DataFromJson, Create, DataToJson), `AnimatorInstance.cpp` (ConditionsHold, ConsumeTriggers, exit times, transition order).
- "STSK" and "STAC" layouts: `Skeleton.cpp`, `AnimationClip.cpp`, `AnimationClip.h` (Serialize, Deserialize, enums).
- Limits: `Skeleton.h`, `AnimationClip.h`, `AnimationController.h`, `AnimatorInstance.h`.
- Scene services: `Strata/src/Strata/Scene/SceneServices.h` (ISkinningPoses, IAnimatorControl, IAnimationEventSource).

## reference/assets

Page: `src/content/docs/reference/assets.md`; notes: `plan/notes/reference/assets.md`.

- Types by native extension, loader module and importer: Strata/src/Strata/Asset/AssetTypes.cpp, the five *Registration.cpp files, GltfImporter.h.
- Stored forms: AssetRegistration.h, CookedTexture.h, AssetPack.h, Mesh.h, ColorLookup.h, ImportRecordStore.h, AudioClipAsset.h, CookedScene.h.
- Residency budgets: AssetResidency.h.
- AssetManagerStats fields: AssetManager.h.
- Streaming panel columns: StreamingPanel.cpp.

## reference/audio-input

Page: `src/content/docs/reference/audio-input.md`; notes: `plan/notes/reference/audio-input.md`.

The folder src/generated/reference/ holds no audio or input table, so every table of the page is written by hand from the pin (commit 822a7a46):
- Source formats, cooked clip: Strata/src/Strata/Asset/AssetImporters.cpp, Strata/src/Strata/Audio/AudioClipAsset.cpp, AudioClip.h.
- Attenuation models, units: Strata/src/Strata/Audio/AudioSource.h, AudioComponents.cpp, AudioComponents.h.
- Audio limits, AudioStats: Strata/src/Strata/Audio/AudioSystem.h, AudioEngine.h.
- Audio services: Strata/src/Strata/Scene/SceneServices.h.
- Key, mouse, gamepad names and codes: Strata/src/Strata/Input/InputNames.cpp, KeyCodes.h, MouseCodes.h, GamepadCodes.h (keys grouped in ranges).
- Binding grammar, reserved UI map, input limits and thresholds: Strata/src/Strata/Input/InputActionSet.h, InputActionSet.cpp, InputActions.h.

## reference/automation

Page: `src/content/docs/reference/automation.md`; notes: `plan/notes/reference/automation.md`.

- Error codes: `Strata/src/Strata/Network/JsonRpc.h`.
- Command error mapping: `StrataEditor/src/Editor/EditorAutomation.cpp` (`ToRpcResult`).
- Built-in methods: `Strata/src/Strata/Network/RpcServer.h`, `RpcServer.cpp`.
- Limits: `JsonRpc.h`, `RpcServer.h`, `RpcServer.cpp`, `StrataCLI/src/CLI/McpServer.h` (idle default 600), `EditorApplication.cpp`.
- MCP generic tools: `StrataCLI/src/CLI/McpServer.cpp`.
- Environment variables: `CliApplication.cpp`, `EditorLauncher.cpp`, `EditorSession.cpp`, `ExternalEditor.cpp`, `RecentProjects.h`, `ScriptBuild.cpp`, `PosixPlatform.cpp`, `WindowsPlatform.cpp`, `Application.cpp`, `ScriptToolchain.cpp`.

## reference/build

Page: `src/content/docs/reference/build.md`; notes: `plan/notes/reference/build.md`.

- Label table: `StrataTests/CMakeLists.txt` (set_tests_properties LABELS).
- Tools table: the docstrings of `Tools/*.py`, `StrataTests/FeatureTest/Tools/GenerateAssets.py`, `StrataEditor/Tools/GenerateIconHeader.py`, `.github/scripts/*`.

## reference/commands

Page: `src/content/docs/reference/commands.md`; notes: `plan/notes/reference/commands.md`.

- "How values are written": read from `Strata/src/Strata/Reflection/PropertyJson.cpp` (ReadNumber, ReadVector, UUIDFromJson, PropertyValueFromJson) and `StrataEditor/src/Editor/CommandUtils.cpp` (FindAsset); the range refusal and case-insensitive property names are from `.claude/skills/strata-editor-automation/SKILL.md` section 4.
- Built-in assets: `Strata/src/Strata/Asset/BuiltinAssets.h` and `BuiltinAssets.cpp`.
- Step of a command script: `StrataEditor/src/Editor/EditorCommandRunner.h` and `Commands/BatchCommands.cpp`.
- The groups (toolsets and teaching page): toolsets read from the generated group files, order from `EditorCommands.cpp`.

## reference/core

Page: `src/content/docs/reference/core.md`; notes: `plan/notes/reference/core.md`.

All tables of the page: no generated file for Core exists in src/generated/reference/. Read from, at the pin,
Strata/src/Strata/Core/: UUID.h, Hash.h, Crypto.h, Base64.h, BinaryStream.h, JsonUtils.h, JsonEvents.h, StringUtils.h,
RadixSort.h, RangeAllocator.h, AmortizedCheck.h, Prefetch.h, ParallelClone.h, CommandLine.h, CommandLineOptions.h,
EmbeddedFiles.h, Version.h.in, Base.h; and Strata/src/stpch.h.

## reference/editor

Page: `src/content/docs/reference/editor.md`; notes: `plan/notes/reference/editor.md`.

- Panels table: `StrataEditor/src/EditorLayer.cpp` (`RegisterBuiltinPanels`, `BuildDefaultLayout`, `DockNewToolPanels`), `StrataEditor/src/EditorLayer.h` (`EditorPanels`), `StrataEditor/src/UI/EditorPanelRegistry.h`.
- Exit codes: `EditorLayer.cpp` (StartAutomation, UpdateCommandScript, screenshot, frame limit), `Strata/src/Strata/Core/CommandLineOptions.h`, `Strata/src/Strata/Core/Application.h`.
- Menus: `EditorLayer.cpp` `DrawMenuBar`.
- Shortcuts: `EditorLayer.cpp` `HandleShortcuts`, `UI/EditorActions.cpp`, `Panels/ViewportPanel.cpp`, `Panels/ContentBrowserPanel.cpp`, `PerformancePanel.cpp`, `GameViewPanel.cpp`, `UI/Widgets.cpp`.
- Chips and pills: `ViewportPanel.cpp` `DrawChips` and helpers; `EditorLayer.cpp` `DrawStatusBar` and the pill functions.
- Drag payloads and probe keys: `UI/PropertyWidgets.h`, `Panels/ContentBrowserPanel.h`, `UI/ItemProbe.h`.
- Files outside the assets: `Strata/src/Strata/Core/Platform.h`, `Project/Project.h`, `Editor/RecentProjects.*`, `EditorPreferences.cpp`, `ExternalEditor.cpp`, `ScriptBuild.cpp`, `EditorContext.cpp`, `Network/EditorSession.cpp`, `SceneRecovery.h`, `RuntimeApplication.cpp`.

## reference/game-makers

Page: `src/content/docs/reference/game-makers.md`; notes: `plan/notes/reference/game-makers.md`.

The selection file `tools/data/game-makers.json` does not exist at this commit, so every table except the runtime options (included from `options-runtime.md`) is hand-written. Check again when the pin moves.

- Panels: `StrataEditor/src/EditorLayer.cpp` (`RegisterBuiltinPanels`).
- Shortcuts: `EditorLayer.cpp` (global shortcuts, menu items), `Panels/ViewportPanel.cpp` (Q, W, E, R, F, Home, F8), `UI/EditorActions.cpp`.
- Chips: `Panels/ViewportPanel.cpp` (`DrawChips`).
- Components: `src/generated/reference/components.md` (names, defaults).
- Callbacks, SDK calls: `StrataScriptCore/Include/StrataScript/Script.h`, `src/generated/reference/script-api.md`; callback order from `Strata/src/Strata/Scene/Scene.cpp` (`OnUpdateRuntime`).
- Conventions: `Entity.h` (`GetForward`, `SetEulerAngles`), `.claude/skills/strata-make-a-game/SKILL.md` (glTF faces +Z; Euler degrees in commands).
- Commands: `src/generated/reference/commands-*.md`, `options-editor.md`, `options-cli.md`.
- Project folder: `Project.cpp` (`Create`), `Project.h`, `EditorContext.cpp` (Trash, Thumbnails, Saves), `ScriptProject.cpp`.
- Templates and samples: `ProjectTemplates.cpp`, `Samples/Samples.json`.

## reference/notation

Page: `src/content/docs/reference/notation.md`; notes: `plan/notes/reference/notation.md`.

- Space and geometry, Units, Light levels, Color: read from Math.h, Common.slang, Scene.slang, StrataShaders.cmake, SceneRenderer.cpp, ScriptABI.h, RendererComponents.h, TextureImporter.h, MaterialTextures.slang, Docs/DeveloperGuide.md (reference values).

## reference/performance

Page: `src/content/docs/reference/performance.md`; notes: `plan/notes/reference/performance.md`.

- The suites table: read from the TEST_SUITE names of StrataTests/src/Perf/*.cpp and StrataTests/src/Editor/*Perf*.cpp, and the metric names of StrataTests/Perf/Budgets.json.
- The CPU stages table: read from c_BuiltinFrameStages (Strata/src/Strata/Core/FrameProfiler.h), the ST_PROFILE_STAGE calls and the ProfileStage of each scene system's registration, at the pin.

## reference/renderer

Page: `src/content/docs/reference/renderer.md`; notes: `plan/notes/reference/renderer.md`.

- Stage notes (stage, pass, quality rows, page): `Strata/src/Strata/Renderer/GPUProfiler.cpp`, `RendererQuality.cpp` (`c_RowTraits`), `StrataEditor/src/Editor/EditorStateCommands.cpp` (perf description).
- Scene bindings: `Strata/src/Strata/Renderer/SceneRenderer.cpp` (`CreateResources`, binding set at the `Sampler(8..10)` lines), `Strata/shaders/Include/Scene.slang` and the included `.slang` files.
- Statistics families: field names of `SceneRenderer.h`.
- Debug view meanings: `viewport.capture` text, `Scene.slang` lighting view constants.
- Quality row traits and Custom ranges: `RendererQuality.cpp` (`c_RowTraits`, `MakeSection`, option arrays).
- Fallback textures and samplers: `Renderer.cpp`, `Renderer.h`.
- Device requirements and `GraphicsDeviceInfo`: `VulkanGraphicsDevice.cpp`, `GraphicsDevice.h`.
- Rules (about 70 rows): pin's `AGENTS.md` rendering rules and the five renderer inventories (render-core 549-618, render-scene 461-513, render-direct 571-627, render-image 525-579, render-indirect 467-520).

## reference/scene

Page: `src/content/docs/reference/scene.md`; notes: `plan/notes/reference/scene.md`.

All tables except the generated limits table are written by hand, because src/generated/reference/ holds no Scene, Entity, reflection, settings-type or format table.
- Scene API (eight groups): Strata/src/Strata/Scene/Scene.h
- Entity API: Strata/src/Strata/Scene/Entity.h
- Systems table: Strata/src/Strata/Scene/SceneSystem.h and the six *Registration.cpp (Scripting, GameUI, Animation, World, Physics, Audio)
- ComponentFlags, PropertyType, PropertyFlags: Strata/src/Strata/Reflection/ComponentRegistry.h, Property.h
- SettingsFieldType, SettingsScope: Strata/src/Strata/Core/SettingsRegistry.h
- Extra limits table: SettingsRegistry.h, Project/Project.h, Reflection/PropertyBinary.h, Scene/CookedScene.h
- File formats table: SceneSerializer.h, Prefab.h, SceneDocumentReader.cpp, SceneDocumentWriter.cpp, CookedScene.h, Project/Project.h

## reference/script-api

Page: `src/content/docs/reference/script-api.md`; notes: `plan/notes/reference/script-api.md`.

- Header groups and teaching pages: read from the header list of StrataScriptCore/Include/StrataScript/ and the brief.
- Callback table (when each runs): Script.h and the comments of StrataScriptClassDesc in ScriptABI.h.
- Field types: c_IsFieldType in Script.h.
- C types, enums, struct sizes, ABI macros: ScriptABI.h.
- strata_add_script_module options: StrataScriptCore/CMake/StrataScriptModule.cmake.

## reference/settings

Page: `src/content/docs/reference/settings.md`; notes: `plan/notes/reference/settings.md`.

- "What each section is for": scope and editing pages read from Strata/src/Strata/*/*Registration.cpp, StrataEditor/src/EditorLayer.cpp (m_SettingsPages.Register: Input.Actions, Scene.CollisionLayers, Renderer.Quality, Editor.ExternalEditor have custom pages; the others use the generic page).

## reference/term-index

Page: `src/content/docs/reference/term-index.md`; notes: `plan/notes/reference/term-index.md`.

- The whole index table: read from src/content/glossary.json (terms, aliases, home, use), the fences of src/content/docs/**/*.md (`symbol=` or a `#Symbol` in `src=`) and src/generated/outline.json (titles, order). It lists only the pages that exist now; run build.py again after the later pages land.

## reference/ui

Page: `src/content/docs/reference/ui.md`; notes: `plan/notes/reference/ui.md`.

- Conventions (`GameUIComponents.h`, the comment at its top and the field comments; `GameUIRenderer`-independent).
- The enums: `Strata/src/Strata/GameUI/GameUIComponents.h` (all eleven enums; values without a comment are described from `GameUIQuads.cpp` and the component comments).
- Events and callbacks: `Strata/src/Strata/Scene/SceneServices.h` (`UIEventType`, `UIEventInfo`, `IUIEvents`), `StrataScriptCore/Include/StrataScript/ScriptABI.h` and `Script.h` (callbacks).
- `IUIControl` functions: `Strata/src/Strata/Scene/SceneServices.h`.
- The UI action map: `Strata/src/Strata/Input/UIActions.h`.
- Limits: `GameUIScene.h`, `GameUIRenderData.h`, `GameUIQuads.cpp`.
- `GameUISceneStats` and the two stages: `GameUIScene.h`, `GameUIRenderer.cpp`.

## reference/worlds-runtime

Page: `src/content/docs/reference/worlds-runtime.md`; notes: `plan/notes/reference/worlds-runtime.md`.

- World document, layer, cell and index keys; world limits (cells are :value keys of limits.* in values.json): `Strata/src/Strata/World/WorldAsset.cpp`, `WorldAsset.h`, `WorldGrid.h`.
- Project file keys: `Strata/src/Strata/Project/Project.cpp`, `Project.h`, `GameInfo.h` (critic-reference-1 applied).
- Manifest keys and versions 1 to 5: `Strata/src/Strata/Project/GameManifest.cpp`, `GameManifest.h` (version steps from the header comment and the `LoadingScene` "version 4" comment).
- Players' files: `Strata/src/Strata/Runtime/GameGraphicsService.cpp` and `.h`, `Strata/src/Strata/Input/InputActionSet.h`.
- Engine services and `IWorldStreaming`: `Strata/src/Strata/Core/EngineServices.h`, `Strata/src/Strata/Scene/SceneServices.h` (critic-reference-12).
- Exit codes: `StrataRuntime/src/RuntimeApplication.cpp`, `Strata/src/Strata/Core/CommandLineOptions.h`, `Strata/src/Strata/Core/Application.h` (critic-reference-10).
- Perf log unit suffixes: column names in `FramePerfLog.cpp`, `GameRuntime.cpp`.
- Commands list and `world.create` defaults: `StrataEditor/src/Editor/EditorWorldCommands.cpp` (inventory), generated command files.
- Exported folder: `StrataEditor/src/Editor/GameExport.cpp`, `GameExport.h`.

## appendix/credits

Page: `src/content/docs/appendix/credits.md`; notes: `plan/notes/appendix/credits.md`.

- Libraries, fonts, sample packs: `ThirdPartyNotices.md` at the pin. Fox lines: brief item new:185. Re-check when the pin moves.

## appendix/math-cheatsheet

Page: `src/content/docs/appendix/math-cheatsheet.md`; notes: `plan/notes/appendix/math-cheatsheet.md`.

- Both tables (symbols; formulas in 14 groups): no file of src/generated/reference/ holds them. Read from the basics pages (numbers, data-structures, trees-graphs, math-vectors, -matrices, -bases, -projection, -rotations, -geometry, -change, -interpolation, color, signals, math-probability, math-sphere) and Strata/shaders/Include/Scene.slang (OctahedralEncode).
