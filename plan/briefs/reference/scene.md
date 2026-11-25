# Brief: `reference/scene`

| Field | Value |
| --- | --- |
| Title | Scene, reflection and settings: types, flags, formats, limits |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `basics/programming-3` |
| From | scene-ecs ch. 12 (the Scene and Entity API, `ComponentFlags`, `PropertyType` and `PropertyFlags`, `SettingsField` types, file formats, the `c_Max*` limits, the 512 KiB settings cap), generated from the headers |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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
| critic-reference-1 | must | missing-item | new item on `reference/worlds-runtime`; the Leaves out of `reference/settings` | No page of the unit lists the keys of the project file `.stproj`. `reference/settings` sends "the project file's other keys (game info, export settings)" to `reference/worlds-runtime`, whose eight tables do not hold them, and `reference/scene` gives the file one row (format v3), so the link leads to a table that does not exist. | `reference/worlds-runtime` adds a hand-checked table of the project file, checked against `Project.cpp`: the header (Format "Project", Version 3; versions 1 and 2 still read and migrated); `Project` with `Name`, `AssetDirectory`, `StartScene`, `Scripts` (`SourceDirectory`, `ModuleName`), `Export` (`AlwaysInclude`, `LoadingScene`) and `Game` (`Title`, `Version`, `Company`, `Copyright`, `Icon`); `Settings`, whose sections are `reference/settings`'; unknown members kept; the 1 MiB cap. Its introduction names `world/projects-settings`. The row `scene-ecs:214-216` widens its take to this table, and `reference/scene`'s row links it. About 150 words. | `allocation/reference.md:277`, `:788-801`, `:326-328`, `:840`; `allocation/world.md:848-853`; `Strata/src/Strata/Project/Project.cpp:22-23`, `:229-310`, `:388-415`; `Strata/src/Strata/Project/Project.h:71-73`, `:101-103` |
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-16 | could | thin-home | `reference/core` | The generated tables cover about 18 of the 50 headers of `Strata/src/Strata/Core/` and none of `Strata/src/Strata/Math/`. A contributor who meets `FileSystem::FromUTF8`, `Platform::EnsurePrivateDirectory`, `JobSystem`, `ErrorThrottle`, `SequenceLock`, `AtomicFileWriter` or a helper of `Math.h` finds no declaration with its comment on a reference page, while `reference/scene` gives the whole API of `Scene`. | The parse covers every public header of the two folders, each with one sentence that names its teaching page (`core/files`, `core/platform`, `core/jobs`, `core/math`, `core/conventions` and the others). About 30 more sentences, about 450 words. | `allocation/reference.md:984-993`, `:997-1007`; `Strata/src/Strata/Core/` (50 headers at the pin); `Strata/src/Strata/Math/` (`AABB.h`, `Frustum.h`, `Math.h`, `Random.h`, `Ray.h`) |
| critic-reference-18 | could | missing-item | `reference/scene` | The six scene systems (UI, Scripting, Animation, World, Physics, Audio) with what their descriptors declare (whether they run in Simulate, hard and soft order constraints, the profile stage, the callbacks they take part in, a prepare hook) are on no reference page; `reference/scene` lists the `Scene` API only. A reader who asks whether Audio runs in Simulate reads `world/systems` again. | `reference/scene` adds a table parsed from the six `MakeSceneSystemDescriptor` registrations, with an introduction that names `world/systems`. About 40 words. | `allocation/reference.md:316-318`; `allocation/world.md:257-262`; `Strata/src/Strata/Scene/SceneSystem.h:64-100`; `Strata/src/Strata/Physics/PhysicsRegistration.cpp:20`; `Strata/src/Strata/World/WorldRegistration.cpp:60`; `Strata/src/Strata/Audio/AudioRegistration.cpp:44`; `Strata/src/Strata/Animation/AnimationRegistration.cpp:36`; `Strata/src/Strata/GameUI/GameUIRegistration.cpp:21`; `Strata/src/Strata/Scripting/ScriptingRegistration.cpp:17` |
