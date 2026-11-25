# Brief: `reference/components`

| Field | Value |
| --- | --- |
| Title | Components and their properties |
| Kind | R |
| Size | XL |
| Tracks | - |
| Needs | `world/what-a-world-is` |
| From | the component registry (`component.list`; defaults from a dump, inactive reasons parsed from the sources); scene-ecs, gameui, physics, animation, audio-input |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
