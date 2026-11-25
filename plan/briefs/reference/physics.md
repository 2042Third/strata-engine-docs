# Brief: `reference/physics`

| Field | Value |
| --- | --- |
| Title | Physics reference |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | `physics/bodies-colliders` |
| From | physics ch. 13 |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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
| critic-reference-2 | should | shape | `reference/physics`, `reference/animation`, `reference/audio-input`, `reference/ui`, `reference/worlds-runtime`, `reference/editor`, `reference/automation`; some tables of `reference/renderer`, `reference/assets`, `reference/build` | The catalogue pages and `reference/scene`, `reference/core` and `reference/settings` name the teaching page of each group or table. These area pages plan only "one introduction per table", and their Covers never says that an introduction names where the subject is taught, so a reader who looks up a limit, a format or a service cannot go on to the page that explains it. | Each of these Covers says that every table introduction names the page that teaches its subject, one sentence each (about 20 words a table, about 40 tables, about 800 words in all; kind R has no size check). On `reference/renderer` this concerns the bindings, switches, fallbacks and device tables; on `reference/assets` the types, importers, budgets and statistics; on `reference/build` the options, presets, labels and shards. | `allocation/reference.md:480`, `:567`, `:629-630`, `:689`, `:744-745`, `:801`, `:867`, `:930`, `:1050`, `:394-395`; compare `:110-111`, `:190`, `:263`, `:328`, `:989` |
| critic-reference-8 | should | missing-item | new items on `reference/assets`, `reference/renderer`, `reference/script-api` | The other area pages have a parsed table of limits, and `appendix/not-in-strata` sends "caps and limits of the features Strata has" to `reference/renderer`, but these three pages have none. Unlisted at the pin: a texture's longest side of 16,384 texels and 2^28 decoded pixels, a glTF scale of at most 10,000, 8 levels of detail, a hierarchy depth of 1,024 and a 64 MiB document, 4,096 joints per mesh, built-in handles 1 to 255; 32,768 bindless textures, 256 GPU timestamps a frame, a 2 GiB geometry pool, the draw key's submesh and LOD bits, 8,192-texel cascades, the font limits; save file names of 64 characters and files of 64 MiB, 65,536 script classes, 4,096 fields a class, names of 1,024 bytes and strings of 256 MiB. | Each of the three pages adds a parsed limits table through `tools/reference-limits.json`, as `reference/physics` and `reference/ui` have, with one introduction that names the teaching page. About 40 words each. | `allocation/reference.md:385-406`, `:460-485`, `:5-28`; `allocation/appendix.md:48`; `Strata/src/Strata/Asset/TextureImporter.h:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:24`; `Strata/src/Strata/Asset/GltfImporter.cpp:68-74`; `Strata/src/Strata/Asset/GltfImporter.h:54`; `Strata/src/Strata/Renderer/Mesh.h:46`; `Strata/src/Strata/Asset/Asset.h:36`; `Strata/src/Strata/Renderer/GraphicsDevice.h:135`; `Strata/src/Strata/Renderer/GPUProfiler.h:95`; `Strata/src/Strata/Renderer/GeometryPool.h:87`; `Strata/src/Strata/Renderer/SceneDrawKey.h:28-29`; `Strata/src/Strata/Renderer/RendererQuality.h:191`; `Strata/src/Strata/Renderer/FontValidation.h:47-58`; `Strata/src/Strata/Core/SaveFiles.h:23-24`; `Strata/src/Strata/Scripting/ScriptModule.cpp:55-57`, `:957`, `:1046`; `Strata/src/Strata/Scripting/ScriptValue.h:17` |
| critic-reference-12 | should | missing-item | `reference/audio-input`, `reference/ui`, `reference/worlds-runtime` | `reference/physics` and `reference/animation` list their scene services with each function's comment; the other area pages do not. So `IAudioPlayback` and `IAudioOutput`, `IUIControl` (beside the event types of `IUIEvents`), `IWorldStreaming` (a link row with no table) and the engine services `IGameWindow`, `IGameSaves` and `IGameGraphics` are on no reference page, though engine code reaches those modules only through them. | Each of the three pages adds the parsed table of its services, as `reference/physics` (4) does (about 30 words each); `reference/worlds-runtime` also takes the three engine services of `EngineServices.h`, which the runtime and the editor provide, with an introduction that names `scripting/host-api` and `worlds/runtime`. | `allocation/reference.md:564-566`, `:627-628`, `:679-691`, `:736-746`, `:788-801`, `:829`; `Strata/src/Strata/Scene/SceneServices.h:242`, `:485`, `:538`, `:552`, `:584`; `Strata/src/Strata/Core/EngineServices.h:103`, `:125`, `:152` |
| critic-reference-21 | could | missing-item | `reference/audio-input` | The audio properties have no descriptions at the pin, so the generated component rows give only ranges, and no reference page gives their units, while `reference/physics` has a units table: `Volume` is a linear gain from 0 to 4 (1 plays the clip as recorded), `Pitch` a rate factor from 0.01 to 8, `MinDistance` and `MaxDistance` metres, `Rolloff` a factor of the Inverse model. | `reference/audio-input` adds a hand-checked units table for `AudioSource`, checked against `AudioComponents.cpp` and `AudioVoice.cpp`, naming `audio/clips-voices-sources` and `audio/spatial`. About 60 words. | `allocation/reference.md:679-691`, `:558-560`; `Strata/src/Strata/Audio/AudioComponents.cpp:16-23`; `Strata/src/Strata/Audio/AudioComponents.h:12-21`; `Strata/src/Strata/Audio/AudioVoice.cpp:304-316` |
