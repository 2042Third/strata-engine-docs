# Allocation: reference

## `reference/script-api` — The complete script API

**Covers.** The paragraph on top says what the page is: every name a game script can call, generated from the SDK's
headers and the C table at the pin, never typed. It says how to read the two layers: game code includes only
`StrataScript.h` and calls the C++ SDK; each SDK function wraps a member of `StrataScriptHostAPI`, the C table that
the engine fills. Then the generated tables, in this order. (1) The SDK by header, in the groups of the headers:
`Entity`, the `Component` proxy and `TransformComponent`; `Scene`, `Assets` and `SubScene`; `Input` with its `Key`
and `Mouse` enums, gamepads, actions and binding capture; `Time`; `Log`; `RigidBody`, `Physics`, `RaycastHit` and
`Collision`; `CharacterController` and `GroundState`; `AudioSource` and `Audio`; `Animator` and `JointTransform`;
`Game` and `WindowMode`; `Graphics`, `GraphicsOption` and `QualityPreset`; `UIElement`, `UI` and `UIAction`; `World`
and `WorldCellRequest`; the helpers of `Gameplay.h` (`Random`, `Timer`, `KeyRepeat`, `Motion`); `AssetHandle` and the
value traits. Each function shows its declaration, the `//` comment the header gives it (the SDKReader's rules), and the
host function it calls. (2) The `Script` base class: its 15 virtual callbacks in the order of `StrataScriptClassDesc`,
with when each runs, and `GetEntity` and `GetTransform`. (3) Script fields: `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and
the field types that `c_IsFieldType` accepts. (4) The host functions in declaration order, which is the ABI's append
order, grouped as the header comments group them, each with "added in" (the first release tag that contains the commit
that added it); the count is `:value{key="hostFunctions.count"}`. (5) The C types a module sees: the value types of
`StrataScriptValue`, `StrataScriptResult`, the frozen structs with their sizes, the extensible structs that start with
`StructSize`, and the enums. Hand-written around them: one sentence per SDK group naming the page that teaches it; one
note on failure values (an SDK function returns its failure value and does nothing when the running engine lacks the
host member, `ST_SCRIPT_DETAIL_HOST_WITH`); one note that `ST_SCRIPT_ABI_VERSION` stays 1 while functions are only
appended; one note that `ST_SCRIPT_HOST_FUNCTIONS` is the engine's list in `ScriptHostAPI.cpp`, not part of the SDK.
`## Where it lives in Strata`: `StrataScriptCore/Include/StrataScript/`, `ScriptABI.h`, `ScriptHostAPI.cpp`, the
feature test's SDK reader and `SDKCoverageTests.cpp`. The tool is `tools/reference.py`, route "script API". A reader
who arrives with a name finds its declaration, its comment, the host function behind it, the release it came in and
the page that teaches it.

**Leaves out.**

- Writing, attaching and building a first script → `make/first-script`
- When each callback runs within a frame, and the fixed step → `make/script-loop`
- How the SDK turns callbacks into C calls (thunks, override detection, self-registration, class records) →
  `scripting/abi-sdk`
- How the engine implements a host function (`HostCall`, `ResolveContext`, `ReportProblem`) → `scripting/host-api`
- Adding a host function or a callback → `scripting/tutorial-host-function`
- Building and shipping a module (`strata_add_script_module`) → `make/script-builds`
- Which release brought each group, as a history → `appendix/history`

**Fit.** `fits`: about 2,250 words against XL (8,000). The generated tables give the page its size: about 165
host-function rows and some 500 SDK declarations with their comments, roughly 10,000 words. The prose is the paragraph
on top (400 words), one sentence for each of the 15 SDK groups and the 27 groups of host functions (1,250), four section
introductions and four notes (500) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:706` | open | home | The count of host functions, confirmed by the generated table (`hostFunctions.count`; 165 members between `ScriptABI.h:312` and `:756` at the pin, the same number that `ST_SCRIPT_HOST_FUNCTIONS` lists) |
| `scripting:38-39` | feature | link | The two entry points a module exports and `ST_SCRIPT_ABI_VERSION`, in the note on the ABI version |
| `scripting:42-51` | feature | link | Size-prefixed structs, handles, strings, results, the value types, transforms, frozen and extensible structs and the enums, as the table of C types |
| `scripting:53-57` | feature | link | The host table, the buffer protocol of text and array functions, and the field, class and module descriptors |
| `scripting:63-90` | feature | link | The 27 groups of host functions, one introduction each with the page that teaches the group |
| `scripting:92` | feature | link | The 15 class callbacks and their order |
| `scripting:102` | feature | link | `StrataScript.h`, the one header game code includes |
| `scripting:104` | feature | use | Graceful degradation, used in the note on failure values |
| `scripting:105` | feature | link | The `Script` base class, its callbacks, `GetEntity` and `GetTransform` |
| `scripting:113-117` | feature | link | `ScriptClassBuilder`, the field macros, the field types, the value traits and `AssetHandle` |
| `scripting:118-121` | feature | link | `Entity`, the `Component` proxy, `TransformComponent`, `Scene`, `Assets` and `SubScene` as generated rows (every function with its declaration, comment, host function and failure value), linked to `make/scripting-scene`, which teaches them |
| `scripting:122` | feature | link | `Input` with its `Key` and `Mouse` enums, gamepads, actions and binding capture, as generated rows, linked to `input/devices-state` |
| `scripting:123` | feature | link | `Time`, as generated rows, linked to `make/timers-events` |
| `scripting:124` | feature | link | `Log`, as generated rows, linked to `basics/programming-1` |
| `scripting:125-126` | feature | link | `RigidBody`, `Physics`, `RaycastHit`, `Collision`, `CharacterController` and `GroundState`, as generated rows, linked to `physics/world-step` |
| `scripting:127` | feature | link | `AudioSource` and `Audio`, as generated rows, linked to `audio/scene-system` |
| `scripting:128` | feature | link | `Animator` and `JointTransform`, as generated rows, linked to `make/animation` |
| `scripting:129` | feature | link | `Game` and `WindowMode`, as generated rows, linked to `make/levels-saves` |
| `scripting:130` | feature | link | `Graphics`, `GraphicsOption` and `QualityPreset`, linked to `image/quality-settings` |
| `scripting:131` | feature | link | `UIElement`, `UI` and `UIAction`, as generated rows, linked to `ui/input` |
| `scripting:132` | feature | link | `World` and `WorldCellRequest`, linked to `worlds/physics-scripts` |
| `scripting:133` | feature | link | `Random`, as generated rows, linked to `make/recipes`; the sentence of the `Gameplay.h` group also links `scripting/abi-sdk`, which says why its helpers live in the module |
| `scripting:134-135` | feature | link | `Timer` and `KeyRepeat`, as generated rows, linked to `make/timers-events` |
| `scripting:136` | feature | link | `Motion`, as generated rows, linked to `make/gameplay-math` |
| `physics:177` | feature | link | The physics host functions and SDK classes, linked to the physics part |
| `audio-input:94-96` | feature | link | `AudioSource`, `Audio` and their host functions |
| `audio-input:173-176` | feature | link | `Input`, `KeyRepeat`, the input part of the ABI and its host functions |
| `animation:176-178` | feature | link | The animator host functions, `Animator` and `OnAnimationEvent` |
| `gameui:203-204` | feature | link | The UI host functions and the four UI callbacks, read only when `StructSize` covers them |
| `gameui:206` | feature | link | `UIElement`, `UI` and `UIAction` |
| `worlds-runtime:89-93` | feature | link | `World`, its host functions, and the window, graphics and scene-load calls of the worlds part |
| `render-image:250` | feature | link | The `Graphics` SDK of players' graphics options |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reading a C++ declaration: types, functions, classes and their members | `basics/programming-3` | must |
| References and `const` in parameters | `basics/cpp-memory` | helps |
| What a script is and when its callbacks run | `make/script-loop` | helps |
| The script system and the dispatch of callbacks | `scripting/script-system` | helps |
| The host API: engine services behind a C table | `scripting/host-api` | helps |
| The ABI, appending and structs that start with their size | `scripting/abi-sdk` | helps |
| Entities, components and their registered names | `world/ecs` | helps |
| Asset handles | `assets/handles-meta` | helps |
| Vectors and quaternions | `basics/math-rotations` | helps |
| The fixed step and time scale | `core/time` | helps |

## `reference/commands` — The command catalogue

**Covers.** The paragraph on top says what the catalogue is: every command the editor registers, from the dump of
`editor.commands` in a `--no-gpu` editor at the pin, so the count is `:value{key="commands.count"}` and is never typed.
It says how to read an entry: the name `<group>.<action>`; the kind (Edit, Query or Session: what an undo step,
a replay and the journal do with it); the description, written for agents and shown as the engine wrote it; the
parameters as a table (name, type, required, default, description) with the JSON Schema in a closed block; the parsed
flags `MayDefer` (the command may take frames), `WaitsForAssets` (it waits for the background asset scan) and
`Results` (Content or Session: whether a replay may bind identifiers from its result); and the MCP toolset that
offers it as a tool. There is no result schema, so the result is the description's own words, with an example result
where a tutorial run recorded one (`reference/_examples/`). The generated part opens with a table of the command
groups (group, count, toolset), then one section per group in the order of `EditorCommandRegistry`, from `scene.*`,
`entity.*`, `component.*` and `prefab.*` to `graphics.resetPlayerOptions`. Hand-written: one sentence per group that
names the page teaching what the group does; a note that `editor.showPanel` and `editor.showDialog` are registered by
the editor's window (`EditorLayer`), not by `StrataEditorCore`, and fail in an editor without a window; and the
erratum on the count (`new:1`). `## Where it lives in Strata`: `EditorCommands.cpp`, the `Editor*Commands.cpp` and
`Commands/` files, `CommandJournalTests.cpp` (which pins every command's kind and flags) and `McpToolsets.cpp`. The
tool is `tools/reference.py`, route "commands". When the rendered file passes the site's largest-page budget, the
catalogue becomes one page per group (`reference/commands/<group>`, `../site.md`), and the outline gets those rows first.

**Leaves out.**

- How a command is registered, checked against its schema and run → `editor/commands`
- Commands that take frames and the poll that owns their data → `editor/deferred-commands`
- What an undo step records → `editor/undo`
- Running commands from the CLI and in command scripts → `make/commands`
- Command scripts, batches and expectations → `editor/command-scripts`
- The journal and replays, which use the kinds → `editor/journal`
- How commands become MCP tools and what each toolset is for → `automation/mcp`
- The protocol that carries a command, its errors and the CLI → `reference/automation`
- Adding a command → `editor/tutorial-command`

**Fit.** `fits`: about 2,000 words against XL (8,000). The generated catalogue gives the page its size: about 150
commands with their descriptions and parameter tables, roughly 18,000 words; the spike built it at that size, and its
largest page was the glossary (`../spike-report-1.md`), so no split by group is expected. The prose is the paragraph on
top, about 25 group sentences, the note on the window's two commands, the erratum and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | erratum | home | The inventories count 151, 153 and 154 commands. The fact: `StrataEditorCore` registers 151 (63 Edit, 46 Query, 42 Session), and the editor's window adds `editor.showPanel` and `editor.showDialog`, also in a `--no-gpu` editor, where they fail. The page never types a count: `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` (the three lists), `:234` (the check of their total); `StrataEditor/src/EditorLayer.cpp:177`, `:233`; `StrataEditor/src/EditorLayer.cpp:187`, `:242` (they fail without a window) |
| `editor-core:54` | feature | use | The fields of `EditorCommand` that the columns show: name, description, schema, kind, results, flags |
| `editor-core:60-62` | feature | link | The kinds as a tested decision, the wait for the asset scan, and `editor.commands`, the dump's source |
| `editor-core:63` | feature | use | The two commands of the window, in the note |
| `editor-core:74-97` | feature | link | Every command group with its purpose, one sentence and a link each |
| `editor-core:236` | feature | link | `Defer(poll)`, behind the `MayDefer` column |
| `automation:149` | feature | link | `editor.commands` as agents call it |
| `automation:169` | feature | link | `EditorCommandResults`, behind the `Results` column |
| `automation:209` | feature | link | Every command becomes an MCP tool |
| `automation:211` | feature | link | The toolsets, behind the toolset column |
| `scene-ecs:235` | feature | link | The `entity.*` and `component.*` commands seen from the scene's side |
| `assets:212` | feature | home | The `asset.*` commands as catalogue entries; each is named on the page of its subject |
| `render-direct:50` | feature | link | The `material.*` commands |
| `scripting:205` | feature | link | The `script.*` commands |
| `animation:92` | feature | link | The `animation.*` commands |
| `audio-input:98` | feature | link | `audio.state` |
| `audio-input:179-180` | feature | link | The `input.*` and `inputActions.*` commands |
| `physics:172` | feature | link | `physics.stats` and `physics.setDetailedStats` |
| `gameui:214` | feature | link | `ui.create`, `ui.layout` and `ui.hitTest` |
| `worlds-runtime:111` | feature | link | The `world.*` commands |
| `worlds-runtime:167` | feature | link | The export commands of `project.*` |
| `worlds-runtime:181` | feature | link | The commands of the launcher, templates and samples |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a command is and how to run one: names, schemas, kinds and the registry | `editor/commands` | must |
| JSON values and objects | `basics/data-formats` | must |
| Undo steps | `editor/undo` | helps |
| Commands that take frames | `editor/deferred-commands` | helps |
| The journal and replays | `editor/journal` | helps |
| MCP tools and toolsets | `automation/mcp` | helps |

## `reference/components` — Components and their properties

**Covers.** The paragraph on top says what the page is: every component the engine registers, with every property, its
type, range, options, section and default, generated at the pin. It says how to read a component's entry: the
registered name (what scripts, commands and scene files use) and the display name (what the Inspector shows); the
category; the description; whether a person can add it (`addable`); then one row per property with the name, display
name, `PropertyType`, description, the Inspector's section, minimum and maximum, the asset type of an asset property,
the options of an enum, read-only and the collision-layer flag; the default from the defaults dump (an entity made,
the component added, read back with `entity.get`); and the inactive reason where the property can be turned off by
another, parsed from the `SetInactiveReason` calls. The generated part groups the components by their registered
category, in the order of `ComponentRegistry`: Core (`Name`, `Transform`, `Tag`, `PrefabInstance`), Rendering
(`Camera`, `MeshRenderer`, `HeightFog`, `ReflectionProbe`, `PostProcess`), Lighting (the three lights and `SkyLight`),
Physics (`RigidBody`, the four colliders, `CharacterController`), Audio, Animation (`Animator`, `Skin`,
`AttachToJoint`), Scripting (`Script`), World (`World`, `StreamingSource`) and UI (`Text` and the eleven `UI*`
components; `Text` is the renderer's, so one sentence says where it is taught). A last table, parsed from the source, lists what
`component.list` leaves out: the hidden components `ID`, `Relationship` and `Inactive`, and the hidden or transient
properties of the others, each with the reason it is hidden. The count is `:value{key="components.count"}`.
Hand-written: one sentence per category naming the part that teaches it; a note on components with no defaults (not
addable, or refused by `component.add`, with the error the dump recorded); the erratum on the count (`new:2`); and
`## Where it lives in Strata`: `ComponentRegistry.h`, each module's `<Module>Components.cpp`, `PropertyJson.cpp`,
`EntityCommands.cpp` and `StrataTests/Architecture/ComponentSchema.json`, which pins the set. The tools are
`tools/reference.py dump` (`component.list` and the defaults run) and `parse` (inactive reasons, hidden entries). A
reader with a property name from a script or a scene file finds its type, range, default and the page that explains it.

**Leaves out.**

- How a component is registered and reflected → `world/reflection`
- How the Inspector draws properties, sections and inactive reasons → `editor-ui/inspectors`
- Adding a component of one's own → `world/tutorial-component`
- What each component does, for game makers → `make/scenes-entities`
- The physics, animation, audio and UI facts beyond the properties (units, limits, formats) → `reference/physics`,
  `reference/animation`, `reference/audio-input`, `reference/ui`
- The flags and property types themselves, as types → `reference/scene`

**Fit.** `fits`: about 1,050 words against XL (8,000). The generated tables give the page its size: 42 components with
several hundred properties and the table of hidden entries, roughly 12,000 words. The prose is the paragraph on top with
how to read an entry (400 words), the nine category sentences and the one on `Text` (300), the note on components
without defaults and the introduction of the hidden entries (130), the erratum (100) and the strip (120).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:2` | erratum | home | `gamedev.md:67` and `:272` count 40 registered components; the engine registers 42, and `component.list` returns 39 of them, because it leaves out the hidden `ID`, `Relationship` and `Inactive`. The page lists all 42 and types no count. Evidence: `StrataTests/Architecture/ComponentSchema.json` (42 entries); `StrataEditor/src/Editor/Commands/EntityCommands.cpp:619-620`; `Strata/src/Strata/Scene/ComponentRegistration.cpp:72`, `:90`, `:100` |
| `scene-ecs:189-191` | feature | use | `PropertyType`, `PropertyInfo` and `PropertyFlags`, in the paragraph on how to read a property row |
| `scene-ecs:195` | feature | use | `ComponentFlags`, behind `addable` and the hidden entries |
| `scene-ecs:198` | feature | use | `SetInactiveReason`, the source of the inactive-reason column |
| `scene-ecs:51-60` | feature | link | The Scene module's components, from `ID` to the types `MeshRenderer` and `Skin` |
| `scene-ecs:62` | feature | link | The unregistered runtime-only components, named in the note on what the list leaves out |
| `render-core:247` | feature | link | `Text` and `MeshRenderer`, registered by the renderer |
| `render-direct:74` | feature | link | `DirectionalLight` |
| `render-direct:76-77` | feature | link | `PointLight` and `SpotLight` |
| `render-direct:151` | feature | link | `SkyLight` |
| `render-direct:167` | feature | link | `HeightFog` |
| `render-indirect:103` | feature | link | The ambient-occlusion fields |
| `render-indirect:118` | feature | link | `ReflectionProbe` |
| `render-indirect:137` | feature | link | The screen-space reflection fields |
| `render-image:194` | feature | link | `PostProcess.AntiAliasing` and its methods |
| `render-image:268` | feature | link | `PostProcess` |
| `physics:28-35` | feature | link | `RigidBody`, the four colliders, `CharacterController`, their gizmos and the rule of what makes one body |
| `audio-input:73` | feature | link | `AudioSource` and `AudioListener` |
| `animation:74-78` | feature | link | `Animator`, its clip's inactive reason, its culling mode, `Skin` and `AttachToJoint` |
| `scripting:154` | feature | link | `Script`, an ordered list of class names and their fields |
| `worlds-runtime:41-42` | feature | link | `World` and `StreamingSource` |
| `gameui:53-65` | feature | link | The eleven UI components and their enums |
| `gamedev:67` | feature | link | The components as a game maker meets them, whose count the erratum corrects |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities and components | `world/what-a-world-is` | must |
| Reflection: one registration, many uses | `world/reflection` | helps |
| Inspectors from reflection; inactive reasons | `editor-ui/inspectors` | helps |
| Asset handles and asset types | `assets/handles-meta` | helps |
| Collision layers | `physics/collision-layers` | helps |
| Prefab instances and overrides | `world/prefabs` | helps |

## `reference/settings` — Project settings and preferences

**Covers.** The paragraph on top says what the page is: every settings section a project or the editor's preferences
can hold, with every field and its default, generated at the pin from `project.settings` on a new `empty` project and
from `preferences.get`, using each field's `default` and never its `value`, so nothing of the machine that made the
dump leaks in. It says how to read a section: its id `<Module>.<Name>`; its scope (Project: stored in the `.stproj`
file and shipped with the game; User: the person's preferences, never shipped); its title and category as the
settings windows show them; its version; for a simple section one row per field (name, title, `SettingsField` type,
default, range or options, description); for a complex section its JSON Schema in a closed block and its default
value. The generated part has two tables. Project sections, in the order `project.settings` returns them: `Input.Actions` (the action
maps and the reserved UI map), `Physics.Simulation`, `Renderer.Quality` (the preset and the Custom values),
`Scene.CollisionLayers` (32 named layers and the matrix) and `Scene.Timing`. Preference sections:
`Editor.ExternalEditor`, `Editor.FrameRate` and `Editor.Interface`. Hand-written: one sentence per section naming its
home page and the editor's settings page that edits it; a note that the four preset values of each quality row stand
in `reference/renderer`'s quality table, so this page shows only the section's fields; a note on the commands that
change a section (`project.setSettings`, `project.setCollisionLayers`, `inputActions.*`, `preferences.set`); and
`## Where it lives in Strata`: `SettingsRegistry.h`, each section's registering file, `EditorPreferences.cpp` and the
settings windows. The tool is `tools/reference.py dump`, routes "settings" and "preferences". A reader with a section
id from a `.stproj` file finds every field, its default and the page that explains it.

**Leaves out.**

- What a settings section is, its validation, versions and the hand-over to scenes → `world/projects-settings`
- How the settings windows are drawn from schemas → `editor-ui/settings-windows`
- The quality rows with their four presets and what each costs → `reference/renderer`
- The `SettingsField` types and the 512 KiB cap, as types and limits → `reference/scene`
- The project file's other keys (game info, export settings) and the manifest → `reference/worlds-runtime`
- Changing settings in the editor, for game makers → `make/project-files`

**Fit.** `fits`: about 1,600 words against L (5,000). The generated tables give the page its size: eight sections with
their fields and defaults, two schemas and the default action maps, roughly 3,500 words. The prose is the paragraph on
top, eight section sentences, three notes and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:218-220` | feature | use | `SettingsSection`, `SettingsField`, scopes, versions, the registry and `IProjectSettings`, in the paragraph on how to read a section |
| `scene-ecs:221-223` | feature | link | `Scene.CollisionLayers`, `Scene.Timing` and the list of the other sections |
| `physics:123` | feature | link | `Scene.CollisionLayers` from the physics side |
| `physics:146` | feature | link | `Physics.Simulation` and its fields |
| `physics:158` | feature | link | `Scene.Timing` from the physics side |
| `audio-input:153` | feature | link | `Input.Actions` |
| `render-image:234` | feature | link | `Renderer.Quality` |
| `editor-ui:118` | feature | link | Idle throttling, which `Editor.FrameRate` sets |
| `editor-ui:226-232` | feature | link | The settings browser, the generic page, the custom pages that edit the sections, and the Preferences dialog |
| `editor-core:95` | feature | link | `preferences.get`, `set` and `save` |
| `gamedev:61` | feature | link | Preferences as a game maker meets them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections | `world/projects-settings` | must |
| JSON values and objects | `basics/data-formats` | must |
| Settings windows from schemas | `editor-ui/settings-windows` | helps |
| Collision layers | `physics/collision-layers` | helps |
| Input actions and maps | `input/actions` | helps |
| Quality rows and presets | `image/quality-settings` | helps |
| The fixed rate | `core/time` | helps |

## `reference/scene` — Scene, reflection and settings: types, flags, formats, limits

**Covers.** The paragraph on top says what the page is: the types, flags, file formats and limits of the scene, of
reflection and of settings, parsed from the headers at the pin, for a reader who meets a name in code or a number in an
error message. The generated tables, in this order: (1) the public API of `Scene` and of `Entity`, by group (entities,
hierarchy, transforms, lookups, systems and services, the runtime and time, sub-scenes, requests to the owner), each
member with its declaration and the header's comment; (2) the enums of reflection: `ComponentFlags`, `PropertyType`
and `PropertyFlags`, each value with its comment; (3) the `SettingsField` types and the settings scopes; (4) the
limits, parsed as `tools/reference-limits.json` lists them: `Scene::c_MaxEntities`, `c_MaxHierarchyMoves`,
`c_MaxTransformChanges`, `c_MaxInterpolatedSpeed`, the per-frame loading budget `c_MaxSubSceneMillisecondsPerFrame`,
`c_MaxEntitiesInstantiatedLimit` and `c_MaxEntitiesDestroyedLimit` (the physics capacities of `Scene.h` are
`reference/physics`'), `SettingsRegistry::c_MaxValueBytes` (512 KiB) and `c_MaxIdSize`,
`Project::c_MaxFileBytes` and `c_MaxScriptModuleNameSize`, `c_MaxBinaryStringBytes` and the cooked scene's
`c_MaxBlobBytes`, each with its value and where it is checked. (5) A hand-checked table of the file formats: the scene
document (`.stscene`, the `{"Strata": {"Format", "Version"}}` header, one entity per line), prefabs and models in the
same form, the cooked scene ("STSC" v1, its 64-byte header and CRC-32C), the project file (`.stproj`, format v3), each
with its version constant, the reader and writer that own it and the page that teaches it. Hand-written: one sentence
per table naming the page that teaches it, and a note that unknown components and properties are kept, not dropped,
when a document is read. `## Where it lives in Strata`: `Scene.h`, `Entity.h`, `ComponentRegistry.h`, `Property.h`,
`SettingsRegistry.h`, `Project.h`, `SceneDocumentWriter.h`, `CookedScene.h`. The tool is `tools/reference.py parse`
(route "scene and world limits", and the parse of `Scene`, `Entity` and the reflection enums that the answer to
reference-q3 adds to `../pipelines.md` §7.1).

**Leaves out.**

- The ECS, entities and handles → `world/ecs`
- The hierarchy and the transform contract → `world/scene-graph`
- Systems, phases and fixed steps → `world/systems`
- Reflection as a design → `world/reflection`
- Scene documents and the cooked form, how they are read and written → `world/serialization`
- Settings sections, validation and versions → `world/projects-settings`
- Every component and property → `reference/components`
- Every settings section and field → `reference/settings`
- World and physics limits → `reference/worlds-runtime`, `reference/physics`

**Fit.** `fits`: about 1,400 words against M (3,000). The generated tables give the page its size: some 150 members of
`Scene` and `Entity`, three enums, the settings types and about 15 limits, roughly 4,000 words. The prose is the
paragraph on top, five table introductions, the hand-checked formats table (about 6 rows), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:25-41` | feature | link | The `Scene` and `Entity` API: the registry, handles, tags, `MarkModified`, identity, creation, the entity limit, destruction, duplication, copies, background release, prepared states, requests to the owner, lineage and `GetAssetManager` |
| `scene-ecs:75` | feature | link | `c_MaxHierarchyMoves` |
| `scene-ecs:83` | feature | link | `c_MaxTransformChanges` |
| `scene-ecs:109-113` | feature | link | Pause and steps, time scale and unscaled time, time dilation, the fixed step and `SceneSettings` |
| `scene-ecs:138` | feature | link | `c_MaxInterpolatedSpeed` |
| `scene-ecs:147` | feature | link | `SceneWorkBudget` and the per-frame loading limit |
| `scene-ecs:153` | feature | link | The scene document's header and version |
| `scene-ecs:156-158` | feature | link | Unknown components kept, the streaming writer and reader, in the formats table and its note |
| `scene-ecs:161` | feature | link | The cooked scene "STSC" v1 |
| `scene-ecs:189-191` | feature | link | `PropertyType`, `PropertyInfo` and `PropertyFlags` |
| `scene-ecs:195` | feature | link | `ComponentFlags` |
| `scene-ecs:205` | feature | link | `c_MaxBinaryStringBytes` |
| `scene-ecs:212` | feature | link | The project file `.stproj`, format v3, and its size cap |
| `scene-ecs:218-219` | feature | link | `SettingsField` types, scopes, the 512 KiB value cap and the id rule |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reading a C++ declaration and an enum | `basics/programming-3` | must |
| Entities, components and handles | `world/ecs` | helps |
| The scene graph and the transform contract | `world/scene-graph` | helps |
| Reflection: one registration, many uses | `world/reflection` | helps |
| Scene documents and the cooked form | `world/serialization` | helps |
| Projects and settings sections | `world/projects-settings` | helps |
| Bytes, KiB and MiB | `basics/numbers` | helps |
| JSON values and objects | `basics/data-formats` | helps |

## `reference/assets` — Asset types, file formats, importer versions, budgets and statistics

**Covers.** The paragraph on top says what the page is: the asset types, the importers with their versions, the stored
forms, the residency budgets with their defaults and the statistics the asset manager reports, parsed at the pin. The
generated tables, in this order: (1) the asset types of `enum class AssetType`, in their stored order (append only),
each with its name, its native extension where the engine writes the type itself (`.stscene`, `.stprefab`, `.stmat`,
`.stanimator`, `.stworld`), the module that registers its loader and the importer that makes it; (2) the importers,
each with the source extensions it reads and `GetVersion()` as `:value{key="importer.<type>.version"}`, so no version
is typed (a bump of a version re-imports every asset of the importer); (3) the residency budgets of
`AssetResidencyBudgets`: the pools (GPU textures, GPU buffers, CPU), the default shares of the device's memory budget,
the bytes in flight, the upload and finalization budgets per frame and the staging budget, with `c_AssetUploadStepBytes`;
(4) the fields of `AssetManagerStats`, which `asset.stats` returns and the Streaming panel shows. Hand-written: a
hand-checked table of the stored forms, each with its version constant, its reader and the page that teaches it: the
`.meta` sidecar, the cooked texture "STTX" v2 and its block sizes, the asset pack "STPK" v2 with its v1 still read,
patch packs, the cooked mesh "STMH" v3 with its versions 1 and 2 still read (`Mesh::c_CookedVersion`;
`assets/models-gltf`), the cooked color lookup "STLU" v1 (`ColorLookup::c_FormatVersion`; `image/grading`) and the
import records file `ImportRecords.log` v1 in the project's cache folder (`ImportRecordStore::c_Version`;
`assets/importing`); two more rows name the cooked audio clip "STAU" and the cooked scene "STSC" and link the rows of
`reference/audio-input` and `reference/scene` that state them; one sentence on how budgets are changed
(`asset.setBudget` in the editor, `--asset-budget-mb` in the runtime); a short table of the Streaming panel's columns,
checked against `StreamingPanel.cpp`; the erratum on where the budgets come from (`new:3`); and `## Where it lives in
Strata`: `AssetTypes.h`, `AssetImporters.cpp`, each importer's header, `AssetResidency.h`, `AssetManager.h`,
`AssetPack.h`, `CookedTexture.h`, `Mesh.h`, `ColorLookup.h`, `ImportRecordStore.h`, `StreamingPanel.cpp`. The tool is
`tools/reference.py parse`, route "asset types and importers", and from v0.8.1 the command `asset.types`.

**Leaves out.**

- What an asset is, handles and `.meta` files → `assets/what-is-an-asset`, `assets/handles-meta`
- Importing, the import cache and settings → `assets/importing`
- How textures are cooked and compressed → `assets/texture-cooking`
- Residency, eviction and pins → `assets/residency`
- Budgeted uploads → `assets/uploads`
- Packs and export → `assets/packs-export`
- The `asset.*` commands with their parameters → `reference/commands`
- The runtime's options → `reference/worlds-runtime`
- Bringing assets into a game, for game makers → `make/assets`

**Fit.** `fits`: about 1,150 words against M (3,000). The generated tables give the page its size: the 13 asset types,
the importers with their versions, the residency budgets and the fields of `AssetManagerStats`, about 1,500 words. The
prose is the paragraph on top (250 words), four table introductions (200), the stored-forms table with its introduction
(seven rows and two that link, 290), the sentence on budgets (40), the Streaming panel's eight columns (135), the
erratum (100) and the strip (130).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:3` | erratum | home | `../pipelines.md` §7.1 takes the asset budgets from "the asset settings sections of the settings dump", but no asset settings section exists at the pin: the budgets are the defaults of `AssetResidencyBudgets`, shares of the device's memory budget, changed by `asset.setBudget` and the runtime's option, and the statistics are `AssetManagerStats`, which `asset.stats` returns. The page parses them from the headers and says so. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:34-71` (the struct and its defaults); `Strata/src/Strata/Asset/AssetResidency.cpp:31-40` (`FromDeviceBudget`: 50% and 15% of the device's budget); `Strata/src/Strata/Asset/AssetManager.cpp:218-222` (the defaults from the device's memory budget); `Strata/src/Strata/Asset/AssetManager.h:31` (`AssetManagerStats`); `StrataEditor/src/Editor/EditorStreamingCommands.cpp:164`, `:218` (`asset.stats`, `asset.setBudget`); `StrataRuntime/src/RuntimeApplication.cpp:349` (`--asset-budget-mb`); `git grep -n "section.Id = " 822a7a46 -- Strata/src StrataEditor/src` finds the eight sections the engine and the editor register, none of them an asset section |
| `assets:38-48` | feature | link | Handles, the 13 types, native extensions, states, the base class, metadata, `.meta` sidecars, sub-assets, derived handles, built-in assets and duplicate handles |
| `assets:101` | feature | link | `AssetResidencyBudgets` and its defaults |
| `assets:108` | feature | link | `AssetManagerStats` |
| `assets:110` | feature | link | The budget controls |
| `assets:132` | feature | link | The import record store's file `ImportRecords.log` and its version, a row of the stored-forms table |
| `assets:152-161` | feature | link | The importers, from the native importer to the color lookup importer |
| `assets:162-163` | feature | link | The cooked texture "STTX" v2 and the block sizes |
| `assets:172` | feature | link | The pack format v2 |
| `assets:175` | feature | link | Packs of version 1, still read |
| `assets:180` | feature | link | Patch packs |
| `assets:199` | feature | link | The upload step and `c_AssetUploadStepBytes` |
| `assets:212-214` | feature | link | The asset commands, the Streaming panel and the asset debug views |
| `render-core:246` | feature | link | The asset types the renderer registers |
| `render-image:131` | feature | link | The cooked color lookup "STLU" v1, a row of the stored-forms table |
| `audio-input:50` | feature | link | The cooked clip "STAU", a row of the stored-forms table that links `reference/audio-input` |
| `scene-ecs:161` | feature | link | The cooked scene "STSC", a row of the stored-forms table that links `reference/scene` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset is; handles and `.meta` files | `assets/handles-meta` | must |
| Importing and import versions | `assets/importing` | helps |
| Residency pools, budgets and eviction | `assets/residency` | helps |
| Bytes, KiB and MiB | `basics/numbers` | helps |
| Texture block compression | `assets/textures` | helps |

## `reference/renderer` — Passes, bindings, switches, statistics, debug views, quality rows, device requirements

**Covers.** The paragraph on top says what the page is: the renderer's facts that the engine can list, generated or
parsed at the pin, so that no page of `gpu`, `draw`, `light`, `image` or `indirect` holds a copy of them
(`../pipelines.md` §7.1). The tables, in this order. (1) The GPU stages in frame order (the names passed to
`RegisterGPUStage` and to `RegisterStage(…, FrameStageKind::GPU)`), each with the pass it times, the quality row that
changes its cost where a row's traits name it, and the page that teaches the pass. (2) The scene bindings: the
registers of the one scene binding layout (the constant buffer, the SRV, UAV and sampler slots and the push
constants), each with what it holds, from the slot ledger of `Include/Scene.slang`. (3) The switches: the fields of
`SceneRendererSpecification` with their defaults and comments; a note that `GPUDriven`, `OcclusionCulling`,
`VisibilityFeedback`, `FadeLevelsOfDetail` and `BatchAcrossMaterials` are switches of code only, with no command or
menu. (4) The statistics: the fields of `SceneRendererStats` and the keys of the `renderStats` object that
`viewport.capture` and `editor.perf` report, each key with its field, its unit and the page that names it
(`render-image:57`). (5) The debug views: the `debugView` values of `viewport.capture`, the count as
`:value{key="debugViews.count"}`, each with what it shows and its page. (6) The quality rows: every row of
`RendererQualitySettings` with its four presets (Low, Medium, High, Ultra) from the `c_<Row>Row` lines, its Custom
range from the `Renderer.Quality` schema, its traits (players' row, GPU stage, memory) and its page; values in prose
only as `:value{key="quality.<field>.<preset>"}`. (7) The fallback textures and the common samplers of `Renderer`.
(8) The device requirements: Vulkan 1.2, the features and extensions the device selection requires, the swapchain's
formats and present modes, and the capabilities of `GraphicsDeviceInfo` that switch paths. (9) A hand-checked table
of the renderer's rules: each rule of `AGENTS.md`'s "Renderer conventions", "Shaders", "NVRHI pitfalls" and
"Rendering" bullets, and each rule of the five rendering inventories that is not one of them, in one line each with a
link to the page that states it with its reason. Hand-written besides: one introduction per table and `## Where it
lives in Strata` (`SceneRenderer.h`, `GPUProfiler.cpp`, `RendererQuality.cpp`, `Renderer.cpp`,
`EditorStateCommands.cpp`, `EditorViewportCommands.cpp`, `VulkanGraphicsDevice.cpp`, `Include/Scene.slang`). The
tools are `tools/reference.py parse` (routes "quality rows and presets", "debug views", "GPU stages", "render
statistics", "renderer specification and statistics") and the parses of the slot ledger, the fallback textures and
samplers and the device requirements that the answer to reference-q3 adds to `../pipelines.md` §7.1.

**Leaves out.**

- The order of the passes and why → `gpu/frame-tour`
- Binding layouts, registers and bindless → `gpu/binding`
- The device, NVRHI and the `Renderer`'s services → `gpu/vulkan-nvrhi`
- GPU timing and the stages' plumbing → `gpu/readback-timing`
- What each debug view shows and how to read it → `light/measuring-light`, `gpu/debugging`
- Quality rows, presets, traits and players' options → `image/quality-settings`
- The shader dialect's rules with their reasons → `gpu/shaders`
- The editor's Performance panel → `editor-ui/instrument-panels`
- Measured costs and their budgets → `reference/performance`

**Fit.** `fits`: about 3,600 words against L (5,000). The generated tables give the page its size: the GPU stages, the
scene bindings, the switches, the statistics, the debug views, the quality rows, the fallbacks and samplers and the
device requirements, roughly 5,000 words. The prose is the paragraph on top, eight table introductions, the note on
code-only switches, the hand-checked rules table (about 100 rows of one line, some 2,000 words, checked again at each
pin move and in phase B for the rows of local lights and global illumination) and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:57` | feature | home | The statistics of the image chain (`SceneRendererStats` fields from `PreExposure` on) and their `renderStats` keys, as generated rows; each page of `image` names only its own |
| `render-core:30` | feature | link | `GraphicsDeviceInfo`, the capabilities that switch paths |
| `render-core:32-33` | feature | link | The device requirements and the swapchain |
| `render-core:62-63` | feature | link | The common samplers and the fallback textures |
| `render-core:97-98` | feature | link | The scene binding layout and push constants |
| `render-core:155-178` | feature | link | The steps of the frame, which order the stages table |
| `render-core:210-214` | feature | link | `GPUProfiler`, `GPUPassTimer`, `RendererGPUStages`, the GPU statistics and the present stage |
| `render-direct:177-180` | feature | link | The shadows and lighting debug views, the lighting statistics and their access from the editor and agents |
| `render-direct:189-196` | feature | link | The quality rows of direct light and shadows |
| `render-direct:198` | feature | home | The `SceneRendererSpecification` switches of lights (`MaxLights`, the light cluster grid and the others the item lists), as rows of the switches table; each light page uses the switches it tunes |
| `render-direct:204` | feature | link | The GPU stages of direct light |
| `render-direct:210` | feature | home | The scene bindings of direct light and shadows, as rows of the bindings table; each light page names the slots it reads |
| `render-image:55` | feature | link | The GPU stages of the image chain |
| `render-image:227-238` | feature | link | `RendererQualitySettings`, the preset table, the `Renderer.Quality` section, row traits and players' rows |
| `render-indirect:96` | feature | link | The ambient-occlusion quality samples |
| `render-indirect:128` | feature | link | Reflection probe statistics |
| `render-indirect:138` | feature | link | The `Reflections` quality row |
| `render-indirect:163` | feature | link | The global illumination quality row |
| `render-indirect:181` | feature | link | Global illumination statistics |
| `render-indirect:183` | feature | link | The global illumination GPU stage |
| `render-indirect:189-193` | feature | link | The lighting views, value views, statistics and their access |
| `render-scene:50` | feature | link | The render scene's statistics |
| `render-scene:123` | feature | link | The GPU-driven mode switch |
| `render-scene:181-184` | feature | link | `renderStats`, the viewport debug views, quality rows and the stats overlay |
| `render-scene:722` | open | use | The switches with no command or menu, in the note on code-only switches |
| `render-core:549-618` | rule | link | The rules of the renderer's core, one line each in the rules table |
| `render-scene:461-513` | rule | link | The rules of drawing a scene, one line each |
| `render-direct:571-627` | rule | link | The rules of direct light and shadows, one line each |
| `render-image:525-579` | rule | link | The rules of the image chain, one line each |
| `render-indirect:467-520` | rule | link | The rules of indirect light, one line each |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A frame of the scene renderer, pass by pass | `gpu/frame-tour` | must |
| Pipelines, binding layouts and registers | `gpu/binding` | helps |
| GPU timing and stages | `gpu/readback-timing` | helps |
| Quality rows, presets and traits | `image/quality-settings` | helps |
| The debug views and their statistics | `light/measuring-light` | helps |
| The device and its capabilities | `gpu/vulkan-nvrhi` | helps |
| Running a command (`viewport.capture`) | `editor/commands` | helps |

## `reference/physics` — Physics reference

**Covers.** The paragraph on top says what the page is: the facts of physics in one place, for a reader who tunes a
body or reads a number from `physics.stats`, and how it shares the work with the catalogue pages: the full rows of the
six physics components, of the `Physics.Simulation` section, of the `physics.*` commands and of the physics SDK stand
in `reference/components`, `reference/settings`, `reference/commands` and `reference/script-api`, and this page lists
their names as generated links to those rows. What only this page holds: (1) a hand-checked table of units, one row per
physics property and settings field (metres, kilograms, seconds, metres per second, newtons for forces, newton-seconds
for impulses, degrees as the Inspector shows rotations), checked against the property descriptions and the code; (2)
the body types and shapes (static, dynamic, kinematic; box, sphere, capsule, mesh), parsed from `PhysicsComponents.h`;
(3) the limits, parsed: `c_MaxBodyCoordinate` (bodies beyond 1e5 m wait), the 128 worlds of box3d, the capacity limits
of `PhysicsCapacitySettings` (`c_MaxBodiesLimit`, `c_MaxContactConstraintsLimit`), the room reserved at creation, the
hull vertex counts; (4) the scene services physics offers (`ICollisionEventSource`, `IBodyMotionQuery`, `IBodyControl`,
`IPhysicsQueries`, `ICharacterControl`, `IPhysicsCapacity`, `IPhysicsDiagnostics`), each function with its comment,
parsed from the headers; (5) the statistics: the fields of `PhysicsStats`, `PhysicsLibraryProfile` and
`PhysicsLibraryCounters` that `physics.stats` returns, with their units. Hand-written: one introduction per table, one
note that gravity is `SceneSettings::Gravity` and the fixed step comes from `Scene.Timing`, and `## Where it lives in
Strata` (`Strata/src/Strata/Physics/`, `PhysicsTypes.h`, `PhysicsWorld.h`, `Scene.h`). The tools are
`tools/reference.py parse` and the dumps of the catalogue pages.

**Leaves out.**

- Bodies, colliders and what each type does → `physics/bodies-colliders`
- The step, contacts, queries and character controllers, as mechanisms → `physics/world-step`,
  `physics/contacts-triggers`, `physics/queries`, `physics/character-controllers`
- Collision layers → `physics/collision-layers`
- Tuning and measuring a scene → `physics/tuning`
- Limits at scale and in streamed worlds, with their reasons → `physics/scale-streaming`
- Physics for game makers → `make/physics`
- The perf budgets of physics → `reference/performance`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the body types and
shapes, the limits, the seven scene services and the statistics, about 2,500 words. The prose is the paragraph on top,
five introductions, the units table (about 35 rows of a few words), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `physics:28-35` | feature | link | The six components, their gizmos and the body composition rule, as names linking `reference/components` |
| `physics:41` | feature | link | The three body types |
| `physics:46-51` | feature | link | Material, mass, rotation locks, continuous collision, triggers and the coordinate limit, in the units and limits tables |
| `physics:72` | feature | link | The 128-world limit |
| `physics:77-79` | feature | link | Capacities and growth, the reserved bytes and `IPhysicsCapacity` |
| `physics:102` | feature | link | `ICollisionEventSource` |
| `physics:114` | feature | link | The queries of `IPhysicsQueries` |
| `physics:116` | feature | link | No shape sweeps in the API, named beside the queries |
| `physics:122` | feature | link | 32 layers and the matrix |
| `physics:138` | feature | link | `ICharacterControl` |
| `physics:145-146` | feature | link | `PhysicsSettings` and `Physics.Simulation` |
| `physics:157-158` | feature | link | `SceneSettings` and `Scene.Timing`, in the note on gravity and the fixed step |
| `physics:167-172` | feature | link | `PhysicsStats`, the library profile and counters, `IPhysicsDiagnostics`, the settling instruments, contact growth and the editor's commands |
| `physics:177` | feature | link | The physics host functions and SDK, as names linking `reference/script-api` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rigid bodies and colliders | `physics/bodies-colliders` | must |
| Force, mass, velocity and impulse | `basics/math-change` | helps |
| The fixed step | `core/time` | helps |
| Scene services | `world/systems` | helps |
| Collision layers | `physics/collision-layers` | helps |

## `reference/animation` — Animation reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
`Animator`, `Skin` and `AttachToJoint`, of the `animation.*` commands and of the SDK's `Animator` stand in
`reference/components`, `reference/commands` and `reference/script-api`, and this page links them by name. What only
this page holds: (1) the animation controller format (`.stanimator`, `c_FormatVersion` 1) as a hand-checked table of
its keys: parameters and their types, states with their clip, speed, loop and events, transitions with exit time,
duration and conditions, the "any state" source; checked against `AnimationController.cpp` and the sample controllers;
(2) the cooked forms "STSK" (skeleton) and "STAC" (clip), each with its version and its reader; (3) the limits, parsed:
`Skeleton::c_MaxJoints`, the clip's `c_MaxChannels`, `c_MaxKeys` and `c_MaxValues`, the controller's `c_MaxParameters`,
`c_MaxStates`, `c_MaxTransitions`, `c_MaxConditions`, `c_MaxEventsPerState`, `c_MaxSpeed` and `c_MaxDuration`, and the
animator's `c_MaxPlaying`; (4) the condition operators and parameter kinds, parsed from the enums; (5) the scene
services (`ISkinningPoses`, `IAnimatorControl`, `IAnimationEventSource`), each function with its comment; (6) the glTF
importer's version as `:value{key="importer.Model.version"}`, which animated models follow. Hand-written: one
introduction per table, one line that names `animation/limits` for what the module does not do, and `## Where it lives
in Strata` (`Strata/src/Strata/Animation/`, `GltfImporter.h`). The tools are `tools/reference.py parse` and the
catalogue dumps.

**Leaves out.**

- Skeletons, clips, state machines, blending and events, as mechanisms → `animation/skeletons`, `animation/clips`,
  `animation/state-machines`, `animation/blending`, `animation/time-events`
- Root motion → `animation/root-motion`
- Importing animated models → `animation/importing`
- What Strata's animation does not do → `animation/limits`
- Animation for game makers → `make/animation`
- The perf budgets of animation → `reference/performance`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the two cooked forms,
the limits, the condition operators and parameter kinds, the three services and the importer's version, about 1,200
words. The prose is the paragraph on top, six introductions, the controller format table (about 25 keys), one line and
the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:44` | feature | link | The skeleton's cooked form "STSK" v1 |
| `animation:47` | feature | link | The clip's cooked form "STAC" v1 |
| `animation:53-55` | feature | link | The controller asset, its validation and its transitions grouped by source, in the format table |
| `animation:57` | feature | link | The animation asset types |
| `animation:68` | feature | link | The importer version that animated models follow |
| `animation:74-78` | feature | link | The three components, the clip's inactive reason and the culling mode, as names linking `reference/components` |
| `animation:85-88` | feature | link | The state machine's conditions, triggers and exit times, behind the format's keys |
| `animation:141-143` | feature | link | `ISkinningPoses`, `IAnimatorControl` and `IAnimationEventSource` |
| `animation:176-178` | feature | link | The animator host functions, `Animator` and `OnAnimationEvent`, as names linking `reference/script-api` |
| `animation:185-189` | feature | link | The `animation.*` commands and `viewport.setSettings {editPose}`, as names linking `reference/commands` |
| `animation:223` | feature | link | What is not in Strata yet, in the line that links `animation/limits` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Skeletons, clips and state machines | `animation/state-machines` | must |
| Cross-fades | `animation/blending` | helps |
| Events and loops | `animation/time-events` | helps |
| JSON values and objects | `basics/data-formats` | helps |

## `reference/audio-input` — Audio and input reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
`AudioSource` and `AudioListener`, of `Input.Actions`, of the `audio.state`, `input.*` and `inputActions.*` commands
and of the SDK's `AudioSource`, `Audio`, `Input` and `KeyRepeat` stand in `reference/components`, `reference/settings`,
`reference/commands` and `reference/script-api`, linked by name. What only this page holds. Audio: (1) the source
formats the audio importer reads (`.wav`, `.mp3`, `.flac`, `.ogg`), its load modes and the size above which a clip
starts streamed, and the cooked form "STAU" v1; (2) the attenuation models of `AudioSource` (the component always
uses Inverse); (3) the limits, parsed: `c_MaxOneShots`, `c_MaxDopplerSpeed`, `c_MaxOneShotClipWait`; (4) `AudioStats`.
Input: (5) the names of keys, mouse buttons, gamepad buttons and axes as bindings and commands spell them, generated
from `InputNames` with their codes (`KeyCode` by position on a US keyboard); (6) the binding grammar (`Key/<k>`,
`Mouse/<b>`, `Gamepad/<button>`, half axes, `1D:` and `2D:` composites, at most 96 bytes), as a hand-checked table
with one example each; (7) the reserved `UI` map and its default bindings, generated from `InputActionSet.cpp`; (8) the
limits and thresholds, parsed: `c_MaxKeyCode`, `c_MaxMouseButtons`, `c_MaxGamepads`, `c_MaxTypedTextBytes`,
`c_MaxMaps`, `c_MaxActions`, `c_MaxBindings`, `c_MaxDeadZone`, the press and release thresholds, the players'
bindings file's size cap and version. Hand-written: one introduction per table and `## Where it lives in Strata`
(`Strata/src/Strata/Audio/`, `Strata/src/Strata/Input/`, `AssetImporters.cpp`). The tools are
`tools/reference.py parse` and the catalogue dumps.

**Leaves out.**

- The audio engine, clips, voices and spatial sound, as mechanisms → `audio/engine`, `audio/clips-voices-sources`,
  `audio/spatial`
- Devices, per-frame state and gamepads → `input/devices-state`, `input/gamepads`
- Input actions, how bindings are evaluated, and players' bindings → `input/actions`, `input/rebinding`
- Sound and input for game makers → `make/sound`, `make/input`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the names of some 120
keys, 8 mouse buttons, 15 gamepad buttons and 6 axes, the reserved UI map, the limits and `AudioStats`, roughly 2,000
words. The prose is the paragraph on top, eight introductions, the binding grammar table (about 10 rows) and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:37` | feature | link | `AudioStats` |
| `audio-input:50` | feature | link | The cooked clip "STAU" v1 |
| `audio-input:52` | feature | link | The audio importer's formats, load modes and version |
| `audio-input:62` | feature | link | The attenuation models |
| `audio-input:73` | feature | link | The audio components, as names linking `reference/components` |
| `audio-input:94-96` | feature | link | The audio SDK and host functions, as names linking `reference/script-api` |
| `audio-input:98` | feature | link | `audio.state`, as a name linking `reference/commands` |
| `audio-input:107-110` | feature | link | Key, mouse and gamepad codes and their names |
| `audio-input:148-153` | feature | link | The action model, the binding grammar, kind fitting, names, the reserved UI map and the section |
| `audio-input:156-157` | feature | link | The thresholds with hysteresis and the radial dead zone |
| `audio-input:162` | feature | link | The players' bindings file |
| `audio-input:173-176` | feature | link | The input SDK and host functions, as names linking `reference/script-api` |
| `audio-input:179-180` | feature | link | The `input.*` and `inputActions.*` commands, as names linking `reference/commands` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Clips, voices and sources | `audio/clips-voices-sources` | helps |
| Sound in space: attenuation | `audio/spatial` | helps |
| Input actions, maps and bindings | `input/actions` | must |
| Gamepads, sticks and dead zones | `input/gamepads` | helps |

## `reference/ui` — Game UI reference

**Covers.** The paragraph on top says what the page is and how it shares the work with the catalogue pages: the rows of
the eleven UI components (and `Text`), of the `ui.*` commands and of the SDK's `UIElement`, `UI` and `UIAction` stand
in `reference/components`, `reference/commands` and `reference/script-api`, linked by name. What only this page holds:
(1) the conventions every UI property follows (canvas units, the y axis, anchors and pivots in 0 to 1, colors in display
values), from the comment of `GameUIComponents.h`, as a short hand-checked table; (2) every enum of
`GameUIComponents.h` (`UICanvasScaleMode`, `UICanvasRenderMode`, `UIFitContent`, `UIImageType`, `UIFillDirection`,
`UITextVerticalAlignment`, `UITextOverflow`, `UISelectableTransition`, `UINavigation`, `UILayoutType` and
`UIChildAlignment`), each value with its comment, parsed; (3) the four UI callbacks of `StrataScriptClassDesc` and the
event types of `IUIEvents`, with when each fires; (4) the reserved `UI` action map, linked to `reference/audio-input`'s
table; (5) the limits, parsed: `c_MaxLayoutsPerCanvas`, `c_MaxQuadChanges`, `c_MaxBoundAtlases`, `c_MaxUIFonts`; (6)
`GameUISceneStats` and the stages `GPU.UI` and `Render.UI`. Hand-written: one introduction per table, one line naming
the absent widgets with a link to `ui/what-game-ui-does`, and `## Where it lives in Strata`
(`Strata/src/Strata/GameUI/`, `EditorUICommands.cpp`). The tools are `tools/reference.py parse` and the catalogue dumps.

**Leaves out.**

- What a game UI must do, and the widgets Strata lacks → `ui/what-game-ui-does`
- Rects, anchors and layout → `ui/layout`
- The UI contract → `ui/contract`
- Text and text fields → `ui/text`
- Drawing and input → `ui/drawing`, `ui/input`
- Menus and HUDs for game makers → `make/menus`, `make/hud`

**Fit.** `fits`: about 1,300 words against M (3,000). The generated tables give the page its size: the eleven enums with
their values, the four callbacks and the event types, four limits, `GameUISceneStats` and two stages, about 1,000 words.
The prose is the paragraph on top, six introductions, the conventions table (about 8 rows), one line and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:52` | feature | link | The coordinate and color conventions |
| `gameui:53-65` | feature | link | The components and their enums, as names linking `reference/components` |
| `gameui:79` | feature | link | `c_MaxLayoutsPerCanvas` |
| `gameui:92` | feature | link | `GameUISceneStats` |
| `gameui:128` | feature | link | `c_MaxBoundAtlases` |
| `gameui:130` | feature | link | `c_MaxQuadChanges` |
| `gameui:155` | feature | link | The stages `GPU.UI` and `Render.UI` |
| `gameui:185` | feature | link | The UI action map |
| `gameui:201` | feature | link | `UIEventType` and `IUIEvents` |
| `gameui:203-204` | feature | link | The UI host functions and the four callbacks |
| `gameui:206` | feature | link | `UIElement`, `UI` and `UIAction`, as names linking `reference/script-api` |
| `gameui:214` | feature | link | The `ui.*` commands, as names linking `reference/commands` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Rects, anchors and layout | `ui/layout` | must |
| The UI contract | `ui/contract` | helps |
| UI input and events | `ui/input` | helps |

## `reference/worlds-runtime` — Worlds, export, runtime options, manifest

**Covers.** The paragraph on top says what the page is: the formats, options and outputs of large worlds, the export
and the runtime, parsed at the pin. The tables, in this order. (1) The world document (`.stworld`, `{"Strata":
{"Format": "World", "Version": 1}}`): its keys (name, persistent scene, grid origin, layers, cells, the optional cooked
index), as a hand-checked table checked against `WorldAsset.cpp`, with the cell files' layout and derived handles. (2)
The world limits, parsed: `c_MaxLayers`, `c_MaxCells`, `c_MaxCellSize`, `c_MaxStreamingDistance`, `c_MaxExtent` and
`WorldData::c_SupportedExtent` (20 km). (3) The game manifest (`.stgame`, `c_FormatVersion` 5): every key with its
type, and the versions 1 to 4 that still load, each with what it added; checked against `GameManifest.cpp`. (4)
`GraphicsOptions.json`, the players' options file that only `GameGraphicsService` writes, and the players' bindings
file. (5) The runtime's command line, generated from `c_Arguments` of `RuntimeApplication.cpp` (every option, its
value and help text), with its exit codes. (6) The columns of the runtime's perf log, generated from `FramePerfLog`,
`GameRenderer::MakePerfLogColumns` and the runtime's own columns (`GameRuntime.cpp`), each with its unit. (7) The
`world.*` commands and the `project.*` commands of export, game info and templates, as names linking
`reference/commands`. (8) The installed layout of an exported game (the executable, the manifest, the pack, patch
packs, the script module, the icon), as a hand-checked list. Hand-written: one introduction per table, the plain
file-name rule of the manifest, and `## Where it lives in Strata` (`Strata/src/Strata/World/`,
`Strata/src/Strata/Runtime/`, `Strata/src/Strata/Project/`, `StrataRuntime/src/RuntimeApplication.cpp`,
`StrataEditor/src/Editor/GameExport.*`). The tools are `tools/reference.py parse` (routes "program options", "runtime
perf log", "scene and world limits") and the catalogue dumps.

**Leaves out.**

- Why levels stream; grids, keys and layers → `worlds/why-streaming`, `worlds/grids`
- The streamer → `worlds/streamer`
- The export and its steps → `worlds/export`
- The manifest, icons and platform files, as a design → `worlds/game-identity`
- The runtime and its headless runs → `worlds/runtime`
- Exporting and running a game, for game makers → `make/export`
- Reading a perf log to make a game fast → `make/performance`

**Fit.** `fits`: about 1,900 words against M (3,000). The generated tables give the page its size: the world limits, the
runtime's command line with its exit codes and the columns of the perf log, about 1,500 words. The prose is the
paragraph on top, eight introductions, the world-document and manifest tables (about 30 keys, with the manifest's
versions 1 to 4), the installed layout, one rule and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `worlds-runtime:23-29` | feature | link | The world document, layers, cells, the cell files' layout, the cooked index, validation and the limits |
| `worlds-runtime:34` | feature | link | Cell keys |
| `worlds-runtime:41-42` | feature | link | `World` and `StreamingSource`, as names linking `reference/components` |
| `worlds-runtime:46` | feature | link | `IWorldStreaming` |
| `worlds-runtime:57` | feature | link | The cell states that `world.status` reports |
| `worlds-runtime:90` | feature | link | The world host functions, as names linking `reference/script-api` |
| `worlds-runtime:110-112` | feature | link | `world.cook`, the world commands and `world.create`'s defaults |
| `worlds-runtime:125` | feature | link | `GameRuntimeOptions` behind the command line |
| `worlds-runtime:130` | feature | link | The runtime's perf-log columns |
| `worlds-runtime:132` | feature | link | The render perf columns |
| `worlds-runtime:135-138` | feature | link | `GameGraphicsService` and `GraphicsOptions.json`, `FramePerfLog`, the `StrataRuntime` executable with its options and exit codes, manifest discovery |
| `worlds-runtime:146-149` | feature | link | The `.stgame` manifest v5, the plain file-name rule, the game info and the save and log identity |
| `worlds-runtime:167` | feature | link | The export commands |
| `worlds-runtime:169` | feature | link | The installed layout |
| `scene-ecs:214-216` | feature | link | The export settings, the game info and `GameManifest` from the project's side |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Worlds, cells and layers | `worlds/grids` | must |
| The export | `worlds/export` | helps |
| The runtime and its options | `worlds/runtime` | must |
| A command line with options | `basics/tools` | helps |
| JSON values and objects | `basics/data-formats` | helps |

## `reference/editor` — Editor reference: panels, shortcuts, arguments

**Covers.** The paragraph on top says what the page is: the editor's surfaces as facts to look up, for a reader who
needs a panel's id, a key or an option. The tables, in this order. (1) The editor's command line, generated from
`c_Arguments` in `EditorApplication.cpp` (every option, its value and help text: `--project`, `--commands`,
`--quit-after-commands`, `--frames`, `--screenshot`, `--headless`, `--no-gpu`, `--windowed`, `--ui-scale`,
`--layout`, `--no-automation`, `--automation-port`, `--idle-timeout`, `--imgui-demo`, `--version`, `--help`), the
three ways the editor runs (window, headless, scripted) and the exit code of a bad argument
(`CommandLineOptions::c_UsageExitCode`). (2) The panels, generated from the built-in registrations in drawing order:
id (as `editor.showPanel` takes it), title, icon, menu path, whether it opens by default and where it docks. (3) The
menus of the menu bar with their items and shortcuts, parsed from `EditorLayer::DrawMenuBar`. (4) A hand-checked table
of the shortcuts: each key, its route (global, focused on the Hierarchy or the Scene view, local to a panel), what it
does, and when it is refused (behind a modal, or while the running game has the input), checked against
`EditorLayer.cpp`, `UI/EditorActions.cpp` and `ViewportPanel.cpp`. (5) A hand-checked table of the Scene view's chips
and the status bar's pills, each with what it shows and where it leads. (6) The drag payload names and the probe-key
conventions of the UI tests, for a contributor. Hand-written besides: one introduction per table, a line that sends
preferences to `reference/settings` and environment variables to `reference/automation`, and `## Where it lives in
Strata` (`EditorApplication.cpp`, `EditorLayer.cpp`, `StrataEditor/src/Panels/`, `UI/EditorActions.cpp`). The tools
are `tools/reference.py parse` (route "program options", and the parse of the panels and the menu bar that the answer to
reference-q3 adds to `../pipelines.md` §7.1) and the commands dump (`editor.showPanel`'s panel names).

**Leaves out.**

- The editor as a program: core, UI and host → `editor/program`
- The shell, docking and the panel registry → `editor-ui/shell`
- Shortcuts and who owns the keyboard, with the reasons → `editor-ui/game-view`
- The Scene view's tools and chips, as a design → `editor-ui/scene-view`
- The status bar and toasts → `editor-ui/status`
- The instrument panels → `editor-ui/instrument-panels`
- A tour of the editor for game makers → `make/editor-tour`
- Preferences and their fields → `reference/settings`

**Fit.** `fits`: about 1,700 words against M (3,000). The generated tables give the page its size: 16 options, 13 panels
and some 60 menu items, about 1,200 words. The prose is the paragraph on top, six introductions, the shortcuts table
(about 35 rows), the chips and pills table (about 15 rows), one line and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:48` | feature | link | The ways the editor runs and the exit code of a bad argument |
| `automation:141` | feature | link | The editor's automation options |
| `editor-ui:54` | feature | link | The options that matter to the UI |
| `editor-ui:112-117` | feature | link | The default layout, the panels that dock when opened, the menu bar, the main toolbar and the status pills |
| `editor-ui:122` | feature | link | `editor.showPanel` and `editor.showDialog` |
| `editor-ui:130` | feature | link | `EditorPanelDescriptor`, the columns of the panels table |
| `editor-ui:136` | feature | link | The built-in panels in drawing order with their ids |
| `editor-ui:142-155` | feature | link | Every panel, and the canvas mode view inside the Scene view |
| `editor-ui:197-199` | feature | link | The view toolbar, its chips and the debug view legend |
| `editor-ui:203` | feature | link | The Scene view's keys |
| `editor-ui:238-242` | feature | link | The global, focused and panel-local shortcuts, the shared Edit actions and the drag payloads |
| `editor-ui:257` | feature | link | The test editor whose probes the conventions name |
| `gamedev:43-46` | feature | link | The panels, menus, look and pills as a game maker meets them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's windows and panels: the shell, docking and the panel registry | `editor-ui/shell` | must |
| A command line with options | `basics/tools` | helps |
| Shortcuts and keyboard focus | `editor-ui/game-view` | helps |

## `reference/automation` — Protocol, errors, CLI

**Covers.** The paragraph on top says what the page is: the facts an automation client needs, for a reader who writes
a client or reads an error. The tables, in this order. (1) `StrataCLI`'s usage, generated from its usage text
(`call`, `list`, `status`, `launch`, `mcp`, with their connection options) and its exit codes (0 success, 1 the editor
answered with an error, 2 no editor reachable, and the others the usage text lists). (2) The error codes, parsed from
`JsonRpc.h`: the five of JSON-RPC 2.0 and Strata's six (`Unauthorized`, `ConnectionClosed`, `Timeout`, `ServerBusy`,
`OperationFailed`, `Cancelled`), and how the editor's command errors map onto them. (3) The built-in methods the
server serves before and after the handshake. (4) The limits, parsed: the message size and depth limits, the client
limit, the pre-authentication limits, the stalled-client timeout, the reply bound and the idle timeout's default. (5)
The MCP server's generic tools (`strata_describe` among them) and the toolsets, generated from `McpToolsets.cpp`: each
toolset with its commands and the size budget of `core` (its count from `values.json` or the test that pins it). (6) The
environment variables Strata's programs read, one row each with the program and what it changes:
`STRATA_EDITOR_PATH`, `STRATA_EDITOR_PORT`, `STRATA_EDITOR_TOKEN`, `STRATA_SESSION_DIR` (automation),
`STRATA_EXTERNAL_EDITOR`, `STRATA_RECENT_PROJECTS`, `STRATA_SCRIPT_BUILDS_DIR` (the editor),
`STRATA_RUNTIME_DIR` and `STRATA_ERROR_DIALOG_FILE` (every program); a hand-checked table, since no route lists them.
Hand-written besides: one introduction per table, a note that the token never crosses the wire and never appears in
a dump, and `## Where it lives in Strata` (`Strata/src/Strata/Network/`, `StrataCLI/src/CLI/`,
`StrataEditor/src/Editor/EditorAutomation*`). The tools are `tools/reference.py parse` (route "program options" for
the CLI, and the parses of the error codes, the limits and the toolsets that the answer to reference-q3 adds to
`../pipelines.md` §7.1).

**Leaves out.**

- Sockets, framing and JSON-RPC → `automation/json-rpc`
- The server's threads and limits, with their reasons → `automation/rpc-server`
- The handshake and the security model → `automation/security`
- Sessions, discovery and launching → `automation/sessions`
- The MCP server and how commands become tools → `automation/mcp`
- Every command → `reference/commands`
- The editor's own options → `reference/editor`
- Driving the editor from the CLI, for game makers → `make/commands`

**Fit.** `fits`: about 1,500 words against M (3,000). The generated tables give the page its size: the CLI's usage and
exit codes, the error codes, the built-in methods, the limits and the toolsets with their commands, about 1,500 words.
The prose is the paragraph on top, six introductions, the environment table (9 rows), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:55-56` | feature | link | The message size and depth limits |
| `automation:60` | feature | link | The error codes |
| `automation:67` | feature | link | The built-in methods |
| `automation:74` | feature | link | The pre-authentication limits |
| `automation:76` | feature | link | The client limit |
| `automation:78-79` | feature | link | The stalled-client timeout and bounded replies |
| `automation:123` | feature | link | `STRATA_SESSION_DIR` |
| `automation:132` | feature | link | How command errors map to error codes |
| `automation:136` | feature | link | The idle timeout |
| `automation:192-194` | feature | link | The CLI's commands, exit codes and argument parsing |
| `automation:197` | feature | link | Endpoint discovery and the variables it reads |
| `automation:199-201` | feature | link | Launching, the editor's path and the token on the command line |
| `automation:208` | feature | link | The MCP server's generic tools |
| `automation:211` | feature | link | The toolsets |
| `automation:213-214` | feature | link | The size budget of the toolsets and `strata_describe` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sockets, framing and JSON-RPC | `automation/json-rpc` | must |
| The MCP server and its toolsets | `automation/mcp` | helps |
| A command line with options; environment variables | `basics/tools` | helps |
| The security model | `automation/security` | helps |

## `reference/core` — Core utilities

**Covers.** The paragraph on top says what the page is: the small utilities of the Core layer that engine code calls
everywhere, generated from their headers at the pin, each with its functions and the header's comments, for a
contributor who meets a name in code. The tables, one per header, in this order: `UUID` (64 bits, random, never zero);
`Hash` (FNV-1a, `Combine`, CRC-32C); `Crypto` (SHA-256, HMAC, the constant-time compare); `Base64`; `BinaryWriter` and
`BinaryReader` (bounds-checked, with a sticky failure); `JsonUtils` and `JsonEvents`; `StringUtils`; `RadixSort` and
`SortIndices`; `RangeAllocator`; `AmortizedCheck`; `Prefetch`; `ParallelClone`; `CommandLine` and
`CommandLineOptions`; `EmbeddedFiles` and `Version.h`; the base macros and the `Ref`, `Scope` and `WeakRef` aliases.
Hand-written: one sentence per header naming the page that uses or teaches it, where one does, and the rule that
engine code includes `stpch.h` first; `## Where it lives in Strata` (`Strata/src/Strata/Core/`). The tool is
`tools/reference.py parse` (the parse of the Core headers that the answer to reference-q3 adds to `../pipelines.md`
§7.1). The page is the home of the facts of the utilities that no other page teaches: `Base64`, `StringUtils`,
`Prefetch` and `ParallelClone`.

**Leaves out.**

- Ownership, errors and logging → `core/conventions`
- The math toolkit → `core/math`
- Jobs and `ParallelFor` → `core/jobs`
- Files and paths → `core/files`
- UUIDs as stable identities → `world/ecs`
- How Strata hashes and checks bytes (FNV-1a, `Combine`, CRC-32C) → `basics/data-formats`
- SHA-256 and HMAC in the handshake → `automation/security`
- Binary reading of untrusted data → `assets/robustness`
- The radix sort's use → `draw/batching`
- The range allocator's use → `gpu/geometry-pool`
- Embedded files and the version header → `engineering/generated-code`

**Fit.** `fits`: about 850 words against M (3,000). The generated tables give the page its size: the functions and
comments of about 15 headers, about 2,500 words. The prose is the paragraph on top (250 words), one sentence per header
naming the page that uses or teaches it (450), the rule on `stpch.h` (50) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:111` | feature | home | `ParallelClone`, a small helper the render scene uses: its function and comment |
| `foundation:155` | feature | link | `Hash`: FNV-1a, `Combine` and CRC-32C, linked to `basics/data-formats`, which teaches them; the generated table keeps the whole header |
| `foundation:157` | feature | home | `Base64` |
| `foundation:160` | feature | home | `StringUtils`; `core/first-change` changes it |
| `foundation:164` | feature | home | `Prefetch`, a one-line hint the script system uses |
| `foundation:56` | feature | link | `CommandLine` and `CommandLineOptions` |
| `foundation:152-154` | feature | link | The ownership aliases, the base macros and `UUID` |
| `foundation:156` | feature | link | `Crypto` |
| `foundation:158-159` | feature | link | The binary streams, `JsonUtils` and `JsonEvents` |
| `foundation:161-163` | feature | link | `RadixSort`, `RangeAllocator` and `AmortizedCheck` |
| `foundation:165-167` | feature | link | `EmbeddedFiles`, `Version.h` and `stpch.h` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reading a C++ declaration | `basics/programming-3` | must |
| Bytes, text, JSON and hashes | `basics/data-formats` | helps |
| Ownership, errors and logging in Strata | `core/conventions` | helps |
| Smart pointers | `basics/cpp-memory` | helps |

## `reference/build` — CMake options, presets, test labels, tools

**Covers.** The paragraph on top says what the page is: what a person types to configure, build and test Strata, and
the tools of `Tools/`, parsed at the pin. The tables, in this order. (1) The CMake options, parsed from every
`option(` of `CMakeLists.txt` and `CMake/*.cmake`, each with its default and help text (the program switches, Tracy,
warnings as errors, the optional modules `ST_WITH_*`, the window backend, the compiler cache, precompiled headers, the
instruction set). (2) The presets of `CMakePresets.json`: configure, build and test presets, with their build folders.
(3) The CTest names and labels of `StrataTests/CMakeLists.txt` (`gpu`, `perf`, `package` and the others), with what each
label selects. (4) The shards of `StrataTests/CoreShards.json`, each with its suites, from the file, never from the
Developer Guide (its count is wrong there; `engineering`'s brief holds that erratum). (5) The tools, one row each with
what it does, how it is run and the page that teaches it: the 15 scripts of `Tools/` and the `LookDev` folder, and the
generators kept elsewhere (`StrataTests/FeatureTest/Tools/GenerateAssets.py`, `StrataEditor/Tools/GenerateIconHeader.py`,
the CI scripts); a hand-checked table, since no route lists them (`new:4`). Hand-written besides: one introduction per
table and `## Where it lives in Strata` (`CMakeLists.txt`, `CMake/`, `CMakePresets.json`, `StrataTests/CMakeLists.txt`,
`Tools/`). The tool is `tools/reference.py parse`, route "build".

**Leaves out.**

- Building Strata step by step → `engineering/building`
- Inside the CMake project → `engineering/cmake`
- Compiler flags and portability → `engineering/flags-portability`
- The test program, shards, sweeps and locks → `engineering/test-program`
- Test kinds and labels, with their reasons → `engineering/test-kinds`
- The perf lab's tools → `engineering/perf-lab`
- Generated code and its generators → `engineering/generated-code`

**Fit.** `fits`: about 1,100 words against S (1,500). The generated tables give the page its size: the CMake options,
the presets, the CTest names and labels and the shards, about 1,500 words. The prose is the paragraph on top, five
introductions, the tools table (about 20 rows of one line), the erratum and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:4` | erratum | home | `Docs/DeveloperGuide.md:828` writes `Tools/GenerateAssets.py`; the file is `StrataTests/FeatureTest/Tools/GenerateAssets.py`, and the tools table names it there. Evidence: `Docs/DeveloperGuide.md:828`; `git ls-tree --name-only 822a7a46 Tools/` has no `GenerateAssets.py`; `StrataTests/FeatureTest/Tools/GenerateAssets.py` exists at the pin |
| `build-test:28-39` | feature | link | The root project, its switches and options, the optional modules, `ST_WITH_*`, the compiler cache, precompiled headers, instruction sets and the configurations |
| `build-test:43` | feature | link | The output layout, `build/<preset>/bin/<Config>/` |
| `build-test:55-58` | feature | link | The configure, build and test presets and the parallel-agent build folders |
| `build-test:113-114` | feature | link | The shards and `Testing.Shards` |
| `build-test:118` | feature | link | The labels |
| `build-test:221-238` | feature | link | Every tool, from `Tools/CIStatus.py` to the CI scripts |
| `build-test:240` | feature | link | The rule that every tool is standard-library Python run with `python -I` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a C++ program is built: from two files by hand to CMake | `basics/build` | must |
| A terminal and its commands | `basics/tools` | must |
| Building Strata | `engineering/building` | helps |
| Test kinds and labels | `engineering/test-kinds` | helps |

## `reference/performance` — Measured costs and their budgets

**Covers.** The paragraph on top says what the page is: every perf budget of the engine in one table, generated from
`StrataTests/Perf/Budgets.json`, and how to read an entry: the metric `<Suite>.<Metric>` (suites `Perf.*` on the CPU,
`PerfGPU.*` with a GPU), its unit, `Measured` (the value measured on the reference machine), `Budget` (the limit the test
enforces, at most 1.5 times the measurement), the optional `Target` (a goal below the budget), and provisional entries
(`Provisional`: measured once and recorded, never failing, until the reference machine measures them). It names the
reference machine as `Docs/DeveloperGuide.md` ("Perf tests") states it: i7-13700K, RTX 5090, Windows 11, Release, a
quiet machine; and it says that a reader's machine gives other numbers, that budgets only go down, and that the
numbers of other machines never enter the file. The generated part: the budgets grouped by suite, about 250 entries,
in the file's order (route "perf budgets", `../pipelines.md` §7.1). Each budget also gives its keys
`perf.<name>.Measured`, `perf.<name>.Budget` and `perf.<name>.Unit` of `values.json` (§7.3), which other pages use in
prose; a key exists only where `Budgets.json` gives the value, so a page that cites a budget without a measurement
states the budget and says that it is provisional. A second generated table lists every CPU stage the Performance
panel can show, each with the file that times it (route "CPU stages"): the twelve built-in stages of
`c_BuiltinFrameStages`, the names passed to `ST_PROFILE_STAGE` and to `RegisterStage` without `FrameStageKind::GPU`,
and the `ProfileStage` of each scene system's descriptor; `core/profiling` links it, and the GPU stages are
`reference/renderer`'s. Hand-written: the catalogue of perf suites, one row per suite (`Perf.Scene`, `Perf.Physics`,
`PerfGPU.Renderer` and the others) with what it measures, its test file and the page that explains the cost, checked
against the `TEST_SUITE` names of `StrataTests/src/Perf/` and `StrataTests/src/Editor/*Perf*` at the pin; and
`## Where it lives in Strata` (`StrataTests/Perf/Budgets.json`, `StrataTests/src/Perf/`, `Tools/PerfStability.py`,
`Tools/PerfLock.py`, `Strata/src/Strata/Core/FrameProfiler.h`). The tool is `tools/reference.py parse`, routes "perf
budgets" and "CPU stages". Why budgets are measured on one machine, and how the lab keeps the numbers honest, is
`engineering/perf-lab`'s.

**Leaves out.**

- Benchmarks, noise, percentiles and the perf lab → `engineering/perf-lab`
- Measuring a frame → `core/profiling`
- Making a game run fast → `make/performance`
- A budget added in one change → `capstone/land`

**Fit.** `fits`: about 1,250 words against M (3,000). The generated tables give the page its size: about 250 budgets
with their `perf.<name>` keys, roughly 2,500 words, and the CPU stages with the files that time them, about 300. The
prose is the paragraph on top with the reference machine (400 words), the sentence on the keys and the introduction of
the stages (120), the catalogue of 24 suites with its introduction (640) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:146` | feature | home | The catalogue of perf suites: one row per suite with what it measures, its test file and the page that explains the cost. Taken from the `TEST_SUITE` names at the pin, not from the inventory's list: 24 suites (16 `Perf.*`, 8 `PerfGPU.*`), among them `Perf.Asset`, `Perf.GameUI`, `Perf.Input`, `PerfGPU.GameUI`, `PerfGPU.World` and the two `Harness` suites, which the list leaves out |
| `build-test:135-139` | feature | link | The perf suites, the measurement, the budget file, confirmed checks and the results file |
| `build-test:145`, `build-test:147` | feature | link | The Medium preset rule and the ratchet |
| `build-test:148-149` | feature | link | `Tools/PerfStability.py` and `Tools/PerfLock.py` |
| `foundation:96` | feature | link | `ST_PROFILE_STAGE` and `FrameProfiler`: every CPU stage with the file that times it, as the generated table that `core/profiling` links |
| `animation:202` | feature | link | The animation perf tests |
| `physics:173` | feature | link | The physics perf tests |
| `gameui:241` | feature | link | The game UI perf tests |
| `editor-ui:260` | feature | link | The editor panels' perf tests |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Benchmarks, noise, perf budgets, the perf lab | `engineering/perf-lab` | must |
| Measuring the frame | `core/profiling` | helps |

## `reference/game-makers` — Cheat sheet for game makers

**Covers.** The paragraph on top says what the page is: the names a game maker uses every day on one page, each row
linking its full entry in the catalogue pages, for a reader who has made Coin Run and wants a name back without
searching. It is written for that reader: no internals, every term linked to its use home in `make`. The rows are
chosen by hand in the selection file `tools/data/game-makers.json` (`../pipelines.md` §7.2: the ids per table, for
commands, components, SDK names and runtime options), which the part's brief lists and this page's writer writes in
phase B; their facts (names, descriptions, defaults, options) come from the dumps and the parsed tables, so nothing is
typed twice, and `tools/reference.py check` fails when a chosen id leaves them at a pin move. The sections, in this
order. (1) The editor: the panels, the shortcuts a maker uses most (play and stop, save, undo and redo, the gizmo tools,
frame selection), the Scene view's chips. (2) The components a maker adds most (`Transform`, `Camera`, `MeshRenderer`,
the lights, `SkyLight`, `PostProcess`, `RigidBody` and the colliders, `CharacterController`, `AudioSource`, `Animator`,
`Script`, `Text`, the UI components), each with the few properties that matter first. (3) The script SDK in one table:
the callbacks in the order they run, `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` with the field types, and the calls of
`Entity`, `TransformComponent`, `Input`, `Time`, `Physics`, `RigidBody`, `CharacterController`, `Audio`, `Animator`,
`UI`, `Game` and the helpers that the `make` pages use. (4) The conventions a maker must know: metres, +Y up, -Z forward
for cameras, lights and `GetForward()`, glTF models facing +Z, Euler angles in degrees in the Inspector and in commands
but radians in `SetEulerAngles`. (5) The commands a maker runs from the CLI or a command script (play, input, capture,
export, batches). (6) The runtime's options a maker passes to an exported game. (7) The project folder: the `.stproj`
file, `Assets/` with its `.meta` files, `Scripts/`, `.strata/` (the import cache and script builds, which the
`.gitignore` that `Project::Create` writes leaves out), and what to keep under version control. Hand-written: one
sentence per section linking its `make` page, the conventions, the project folder table, and `## Where it lives in
Strata` (the panels, menus, commands and files a maker opens). The tool is `tools/reference.py render`, which reads
`tools/data/game-makers.json`.

**Leaves out.**

- Everything about each name beyond one line → `reference/components`, `reference/script-api`, `reference/commands`,
  `reference/editor`, `reference/worlds-runtime`
- Making the first game → `start/first-game`
- Positions, rotations and units, taught → `make/transforms-units`
- The editor, taught → `make/editor-tour`
- Projects and saving → `make/project-files`

**Fit.** `fits`: about 1,800 words against M (3,000). The generated facts of the about 80 rows that
`tools/data/game-makers.json` chooses give the page its size, about 1,500 words. The prose is the paragraph on top,
seven section sentences, a one-line use for each chosen row, the conventions and project tables and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:30-36` | feature | link | The launcher, templates, project creation, the project file, samples and recent projects |
| `gamedev:43-56` | feature | link | The editor's windows, from the panel set to the Streaming and Performance panels |
| `gamedev:67-71` | feature | link | The components, reflection-driven editing, built-in meshes, scene settings and the conventions a maker must know |
| `gamedev:124-128` | feature | link | The script module, script classes and fields, the 15 callbacks, the SDK namespaces and generic component access |
| `gamedev:131` | feature | link | Attaching scripts and editing their fields |
| `gamedev:222` | feature | link | Play, Simulate, Stop, Pause and Step |
| `gamedev:224` | feature | link | Simulated input |
| `gamedev:226-227` | feature | link | Viewport capture, command scripts and expectations |
| `gamedev:236` | feature | link | Export |
| `gamedev:239` | feature | link | The runtime's options |
| `gamedev:246-247` | feature | link | Commands are the API; `StrataCLI` and MCP |
| `gamedev:254-258` | feature | link | The five samples, named where each shows a row's name in use |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor's windows | `make/editor-tour` | must |
| Entities and components | `make/scenes-entities` | must |
| Writing and attaching a script | `make/first-script` | must |
| The game loop from a script's side | `make/script-loop` | helps |
| Positions, rotations and units | `make/transforms-units` | helps |
| Running a command from the CLI | `make/commands` | helps |
| Exporting a game | `make/export` | helps |

## `reference/notation` — Conventions and notation

**Covers.** The paragraph on top says what the page is: every convention and symbol the book uses, in one place, each
row linking the page that teaches it; the page defines nothing (`../book.md`, one-home table). The tables, in this
order. (1) Strata's conventions, hand-checked against the pin, each with its evidence and its home: right-handed, +Y
up, -Z forward (`Math.h`), glTF models facing +Z; D3D-style clip space through NVRHI (framebuffer origin top-left, NDC
+Y up, depth from 0 to 1); reversed Z (near is 1, far is 0, depth cleared to 0, `GreaterOrEqual`); the fullscreen UVs
`uv = (ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5)`; front faces counter-clockwise, mirrored instances clockwise;
column-major matrices with `mul(M, v)` and matrix constructors that take rows in shaders; quaternions stored x, y, z, w
across the ABI; Euler angles in degrees in the Inspector and commands, radians in code; camera-relative positions in
scene shaders. (2) Units: SI for space, mass and time; the photometric units of light (lux for the sun, candela for
points and spots, nits for the sky, ambient and emission) and exposure in EV, with the reference values table's
light levels; bytes as KiB and MiB. (3) Color spaces: linear scene values, pre-exposed HDR targets, sRGB encoding at
the end, textures marked sRGB or linear, normal maps as X and Y with Z rebuilt. (4) The symbols of the parts, collected
by the build from the notation tables of the part index pages (and of the first pages of parts without one): symbol,
how it is read, meaning, unit, the page that introduces it. Hand-written: the paragraph on top, the three hand-checked
tables, one note that a page using another convention says so and links here (`../style.md` §4), and `## Where it
lives in Strata` (`Strata/src/Strata/Math/Math.h`, `Strata/shaders/Include/Common.slang`, `CMake/StrataShaders.cmake`,
`AGENTS.md` "Renderer conventions"). It is checked against `gpu/coordinates` and `basics/math-matrices`.

**Leaves out.**

- Matrices, transforms and spaces, taught → `basics/math-matrices`
- Strata's API conventions and the camera, taught → `gpu/coordinates`
- Light units and exposure, taught → `light/units-exposure`
- Color, linear and sRGB, taught → `basics/color`
- Every symbol with the page that teaches it, for mathematics → `appendix/math-cheatsheet`
- Positions, rotations and units for game makers → `make/transforms-units`

**Fit.** `fits`: about 1,300 words against M (3,000). The symbol tables that the build collects from the part index
pages give the page its size, about 1,500 words written on those pages. The prose is the paragraph on top, the
conventions table (about 15 rows), the units and color tables (about 15 rows), one note and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:139` | feature | link | The conventions comment of `Math.h` |
| `render-core:137-143` | feature | link | Clip space, reversed Z, fullscreen UVs, front faces, handedness, camera-relative space and column-major matrices |
| `scripting:47` | feature | link | The ABI's transform: quaternions as x, y, z, w |
| `scripting:120` | feature | link | `TransformComponent`'s forward, right and up (-Z forward) |
| `gamedev:71` | feature | link | The conventions a maker must know |
| `render-direct:101` | feature | link | The photometric units on one scale |
| `render-direct:105` | feature | link | The reference values table of light levels |
| `render-image:130` | feature | link | The sRGB encoding at the end of the chain |
| `render-image:27` | feature | link | The HDR scene color target |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Matrices and transforms | `basics/math-matrices` | helps |
| Coordinate systems and the camera | `gpu/coordinates` | helps |
| Rotations and quaternions | `basics/math-rotations` | helps |
| Color: linear, sRGB and HDR | `basics/color` | helps |
| Light units | `light/units-exposure` | helps |

## `reference/glossary` — Glossary

**Covers.** The paragraph on top says what the page is and how to read an entry: every term of the book in one
definition list, in alphabetical order and without a table of contents (`../site.md`, "Glossary"), drawn by
`::glossary` from `src/content/glossary.json`. Each entry gives the term, its one-sentence definition, its home page
(the page that teaches it) and, where there is one, its use home in `make`, and its other accepted names. The list
holds the seed of 400 entries of a beginner's vocabulary (homes in `start` and `basics`), the inventories' terms
(about 1,590 until the glossary step counts them) with the homes the allocation gave them, and the new terms the
writers' notes admit (`../pipelines.md` §9). A word with two meanings has two entries, each qualified by a word ("pack
block" and "BC block"; "prefetch", "block", "journal", "snapshot", "hot reload" and "batch", `../book.md`, one-home rule
6), never one entry with two definitions; and an inventory entry that defines several terms is split into one entry per
term at the merge. Pages link entries with `:term[text]{id=…}`; a reader who arrives from a popover lands on the entry.
Hand-written: only the paragraph on top, the note on qualified entries and `## Where it lives in Strata`, which names
the glossary file of the book and, for engine terms, the homes' "Where it lives" sections. The tools are
`tools/pages.py check` and `tools/lint.py` (homes that exist, no duplicate term or alias, every home defines its term).

**Leaves out.**

- A beginner's vocabulary taught from zero, which the seed's entries link → `basics/computer`
- The index of engine identifiers and the pages that quote them → `reference/term-index`
- The symbols of mathematics → `appendix/math-cheatsheet`

**Fit.** `fits`: about 450 words against XL (8,000). The entries give the page its size: about 2,000 after the merge
(the seed's 400 and the inventories' terms), roughly 50,000 words drawn from the glossary file; the spike measured 1,600
terms at 116 KB gzipped (`../spike-report-1.md`), so they stay within the largest-page budget of `../site.md` (row 10,
300 KB) and no split is needed. The prose is the paragraph on top and the note on qualified entries.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:527-589` | term | link | The 63 entries of the animation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `assets:637-737` | term | link | The 101 entries of the assets glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `audio-input:606-693` | term | link | The 87 entries of the audio-input glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `automation:703-786` | term | link | The 81 entries of the automation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `build-test:609-698` | term | link | The 84 entries of the build-test glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `editor-core:648-740` | term | link | The 93 entries of the editor-core glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `editor-ui:700-794` | term | link | The 88 entries of the editor-ui glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `foundation:548-645` | term | link | The 94 entries of the foundation glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `gamedev:569-665` | term | link | The 97 entries of the gamedev glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `gameui:617-685` | term | link | The 69 entries of the gameui glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `physics:477-541` | term | link | The 65 entries of the physics glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-core:679-775` | term | link | The 89 entries of the render-core glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-direct:671-758` | term | link | The 88 entries of the render-direct glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-image:634-736` | term | link | The 101 entries of the render-image glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-indirect:564-650` | term | link | The 87 entries of the render-indirect glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `render-scene:569-654` | term | link | The 86 entries of the render-scene glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `scene-ecs:611-693` | term | link | The 80 entries of the scene-ecs glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `scripting:557-621` | term | link | The 58 entries of the scripting glossary, merged into the one list; an entry that defines several terms becomes one entry per term |
| `worlds-runtime:513-568` | term | link | The 56 entries of the worlds-runtime glossary, merged into the one list; an entry that defines several terms becomes one entry per term |

**Assumes.**

none

## `reference/term-index` — Index of terms and engine identifiers

**Covers.** The paragraph on top says what the page is: an index that sends a reader from a name to the page that
defines it, generated from two sources, and how it differs from the glossary (no definitions, only places) and from
`reference/index` (the part's generated map). (1) Terms: every glossary entry with its home page and use home,
alphabetical, with its aliases pointing to the same entry. (2) Engine identifiers: every symbol that the excerpt
fences of the book name (classes, functions, macros, commands, settings sections, files), from the fences' `symbol`
attributes, which `excerpts.py fill` writes (`../pipelines.md` §3), each with the page whose excerpt quotes it first and
the other pages that quote it, so that a reader with `Scene::OnUpdateRuntime` or `ST_CORE_ASSERT` finds where the book
shows it. The two lists share one alphabet, each entry marked as a term or an identifier. Hand-written: the paragraph on
top and `## Where it lives in Strata`. The tool is `tools/reference.py render`, route "terms" (`../pipelines.md` §7.1),
which reads `src/content/glossary.json` (its entries' terms, aliases, `home` and `use`) and the `symbol` attributes of
the pages' quotes, so it runs after `excerpts.py fill`; the search test of `../site.md` expects a concept's home among
the first results, and this page is the fallback.

**Leaves out.**

- The definitions → `reference/glossary`
- The full facts of each identifier → `reference/script-api`, `reference/commands`, `reference/components`,
  `reference/settings`, `reference/core`

**Fit.** `fits`: about 350 words against XL (8,000). The generated index gives the page its size: about 2,000 terms and
several thousand identifiers, roughly 20,000 words of names and links, fewer bytes than the glossary, whose size the
spike measured within the largest-page budget. The prose is the paragraph on top and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:527-589` | term | link | The 63 terms of the animation glossary, each with its home page |
| `assets:637-737` | term | link | The 101 terms of the assets glossary, each with its home page |
| `audio-input:606-693` | term | link | The 87 terms of the audio-input glossary, each with its home page |
| `automation:703-786` | term | link | The 81 terms of the automation glossary, each with its home page |
| `build-test:609-698` | term | link | The 84 terms of the build-test glossary, each with its home page |
| `editor-core:648-740` | term | link | The 93 terms of the editor-core glossary, each with its home page |
| `editor-ui:700-794` | term | link | The 88 terms of the editor-ui glossary, each with its home page |
| `foundation:548-645` | term | link | The 94 terms of the foundation glossary, each with its home page |
| `gamedev:569-665` | term | link | The 97 terms of the gamedev glossary, each with its home page |
| `gameui:617-685` | term | link | The 69 terms of the gameui glossary, each with its home page |
| `physics:477-541` | term | link | The 65 terms of the physics glossary, each with its home page |
| `render-core:679-775` | term | link | The 89 terms of the render-core glossary, each with its home page |
| `render-direct:671-758` | term | link | The 88 terms of the render-direct glossary, each with its home page |
| `render-image:634-736` | term | link | The 101 terms of the render-image glossary, each with its home page |
| `render-indirect:564-650` | term | link | The 87 terms of the render-indirect glossary, each with its home page |
| `render-scene:569-654` | term | link | The 86 terms of the render-scene glossary, each with its home page |
| `scene-ecs:611-693` | term | link | The 80 terms of the scene-ecs glossary, each with its home page |
| `scripting:557-621` | term | link | The 58 terms of the scripting glossary, each with its home page |
| `worlds-runtime:513-568` | term | link | The 56 terms of the worlds-runtime glossary, each with its home page |
| `animation:334-365` | code | link | The identifiers of the 31 excerpts of the animation inventory, each with the page that quotes it |
| `assets:375-444` | code | link | The identifiers of the 34 excerpts of the assets inventory, each with the page that quotes it |
| `audio-input:376-408` | code | link | The identifiers of the 32 excerpts of the audio-input inventory, each with the page that quotes it |
| `automation:458-520` | code | link | The identifiers of the 32 excerpts of the automation inventory, each with the page that quotes it |
| `build-test:378-411` | code | link | The identifiers of the 34 excerpts of the build-test inventory, each with the page that quotes it |
| `editor-core:381-450` | code | link | The identifiers of the 35 excerpts of the editor-core inventory, each with the page that quotes it |
| `editor-ui:429-466` | code | link | The identifiers of the 38 excerpts of the editor-ui inventory, each with the page that quotes it |
| `foundation:342-373` | code | link | The identifiers of the 31 excerpts of the foundation inventory, each with the page that quotes it |
| `gamedev:359-388` | code | link | The identifiers of the 30 excerpts of the gamedev inventory, each with the page that quotes it |
| `gameui:394-425` | code | link | The identifiers of the 31 excerpts of the gameui inventory, each with the page that quotes it |
| `physics:296-325` | code | link | The identifiers of the 30 excerpts of the physics inventory, each with the page that quotes it |
| `render-core:442-474` | code | link | The identifiers of the 33 excerpts of the render-core inventory, each with the page that quotes it |
| `render-direct:433-469` | code | link | The identifiers of the 37 excerpts of the render-direct inventory, each with the page that quotes it |
| `render-image:395-426` | code | link | The identifiers of the 31 excerpts of the render-image inventory, each with the page that quotes it |
| `render-indirect:338-367` | code | link | The identifiers of the 30 excerpts of the render-indirect inventory, each with the page that quotes it |
| `render-scene:341-373` | code | link | The identifiers of the 32 excerpts of the render-scene inventory, each with the page that quotes it |
| `scene-ecs:373-407` | code | link | The identifiers of the 35 excerpts of the scene-ecs inventory, each with the page that quotes it |
| `scripting:354-387` | code | link | The identifiers of the 34 excerpts of the scripting inventory, each with the page that quotes it |
| `worlds-runtime:308-338` | code | link | The identifiers of the 31 excerpts of the worlds-runtime inventory, each with the page that quotes it |

**Assumes.**

none

## `reference/figures` — Index of figures and their recipes

**Covers.** The paragraph on top says what the page is: every picture of the book, generated from the figure
manifests and `taken.json` (`../pipelines.md` §5.8), and how to read a row: the figure's id and the page that shows
it, what it shows (the recipe's `shows` line), its kind (scene, live, editor, runtime, text, reference, tool), its
recipe (project or sample, camera, settings and steps), the pin it was taken at, the GPU it was taken on (from `taken.json`),
its size and, for a slider, its pair. Hand-written: (1) how the pictures are made, in one
short section that names the photographer's run (`figures.py take` with the GPU, one run at a time, under the perf
lock), the project copies a recipe starts from, and how each picture is isolated from the machine (the recorded
settings, the forced CPU path of thumbnails, the GPU-driven path that never ran on the CI's GPUs and the
`expectAlso` check of figures that need it), written for readers; the inventories' notes on how pictures are made
instruct the photographer and stand in `../pipelines.md` §5.5, not here (R44); (2) how a reader makes a picture again
from its recipe with a build of the pin; (3) where "before" pictures come from (the look-dev baseline sets of older
releases, named with their tag). `## Where it lives in Strata` names the look-dev harness (`Tools/LookDev.py`),
`viewport.capture` and the sample screenshots. The tool is `tools/figures.py`; the page is rendered from the manifests
by the build.

**Leaves out.**

- The look-dev harness as a tool → `engineering/look-dev`
- Credits and licenses of the assets in the pictures → `appendix/credits`
- Capturing the viewport for a game → `make/automated-playtests`

**Fit.** `fits`: about 1,100 words against L (5,000). The generated rows give the page its size: about 600 pictures with
their recipes, roughly 18,000 words, which may need a split by part under the site's largest-page budget; the rows of
the W8 pages' figures arrive in phase B. The prose is the paragraph on top and the three hand-written sections.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:374-427` | figure | link | The 26 figures of the animation inventory, as rows once their manifests and recipes exist |
| `assets:453-514` | figure | link | The 29 figures of the assets inventory, as rows once their manifests and recipes exist |
| `audio-input:419-483` | figure | link | The 36 figures of the audio-input inventory, as rows once their manifests and recipes exist |
| `automation:530-590` | figure | link | The 24 figures of the automation inventory, as rows once their manifests and recipes exist |
| `build-test:420-472` | figure | link | The 28 figures of the build-test inventory, as rows once their manifests and recipes exist |
| `editor-core:461-535` | figure | link | The 35 figures of the editor-core inventory, as rows once their manifests and recipes exist |
| `editor-ui:476-582` | figure | link | The 58 figures of the editor-ui inventory, as rows once their manifests and recipes exist |
| `foundation:385-441` | figure | link | The 26 figures of the foundation inventory, as rows once their manifests and recipes exist |
| `gamedev:396-475` | figure | link | The 53 figures of the gamedev inventory, as rows once their manifests and recipes exist |
| `gameui:435-505` | figure | link | The 38 figures of the gameui inventory, as rows once their manifests and recipes exist |
| `physics:333-382` | figure | link | The 26 figures of the physics inventory, as rows once their manifests and recipes exist |
| `render-core:484-543` | figure | link | The 26 figures of the render-core inventory, as rows once their manifests and recipes exist |
| `render-direct:480-565` | figure | link | The 50 figures of the render-direct inventory, as rows once their manifests and recipes exist |
| `render-image:437-519` | figure | link | The 50 figures of the render-image inventory, as rows once their manifests and recipes exist |
| `render-indirect:375-461` | figure | link | The 58 figures of the render-indirect inventory, as rows once their manifests and recipes exist |
| `render-scene:383-454` | figure | link | The 31 figures of the render-scene inventory, as rows once their manifests and recipes exist |
| `scene-ecs:417-494` | figure | link | The 37 figures of the scene-ecs inventory, as rows once their manifests and recipes exist |
| `scripting:398-442` | figure | link | The 22 figures of the scripting inventory, as rows once their manifests and recipes exist |
| `worlds-runtime:346-408` | figure | link | The 36 figures of the worlds-runtime inventory, as rows once their manifests and recipes exist |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Capturing the viewport and debug views | `gpu/debugging` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## Passed on

none

## Not taken

none

## Questions for the planner

none
