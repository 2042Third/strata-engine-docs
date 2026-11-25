# Brief: `world/reflection`

| Field | Value |
| --- | --- |
| Title | Reflection: one registration, many uses |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `world/ecs`, `basics/cpp-modern`, `basics/data-formats`, `core/layers-registries` |
| From | scene-ecs; `ComponentRegistry`'s builder (registries that open, accept and freeze are `core/layers-registries`') |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/reflection` — Reflection: one registration, many uses

**Covers.** The job: one description of each component type (its properties, its metadata and its type-erased
operations) drives files, the Inspector, commands, undo, scripts, cooking and prefab diffs, with no code generator.
Registries that open and accept, and the component and settings registries that then freeze, are
`core/layers-registries`'; this page covers `ComponentRegistry`'s builder. This page carries the full section on the
problem: C++ has no runtime reflection, and engines use macros with a code generator (Unreal's UHT), external
generators, or registration DSLs (RTTR, EnTT's meta, Hazel's style), compared in a table. The map:
`ComponentRegistry` → `ComponentInfo` → `PropertyInfo`, with the consumers drawn around them. Then, in this order:

1. Properties: `PropertyType` (14 types) and `PropertyValue` (a variant of 10 alternatives); `PropertyInfo` (name,
   display name, tooltip, section, type, flags, range, speed, asset filter, enum values, the type-erased getter and
   setter, the inactive reason that section 6 teaches); `PropertyFlags`; `PropertyOptions` (`Range`,
   `Slider`, `Color`, `WithTooltip`, `c_Unbounded`).
2. The builder: `PropertyBuilderBase` as a CRTP builder, the property's type deduced from the member pointer, `Property`,
   `EnumProperty`, `AssetProperty`, `EntityProperty`, `CustomProperty`, `Section`; `PropertyListBuilder` for structs that
   are not components (materials).
3. `ComponentInfo`: its metadata and about 20 type-erased operations; `Register<T>` fills them with lambdas, with
   `if constexpr` for tag types: the page's central mechanism. `ComponentFlags`; `ComponentInfoBuilder`'s metadata
   (`DisplayName`, `Category`, `Description`, `Flags`, `Requires`, `Extra`, `Gizmo` named, `ExtraReferences`,
   `ExtraBinary`); names compared without case, refusals that return a builder which discards, `Find`, `FindByTypeId`,
   `GetAll` in registration order; registration only while the composition root runs, so workers read the frozen
   registry without locks.
4. A real registration: the camera's, with ranges, tooltips and sections; where the Scene module registers
   (`RegisterSceneModule`: its components, two settings sections and three loaders, called second after Input); what one
   registration gives, shown in the Inspector's sections and in the Add Component menu grouped by category.
5. Validation and leniency: `PropertyInfo::SetValue` by type, enum membership, clamping, finite values, normalized
   quaternions; `IsInRange` refuses for commands; strict reads for commands against lenient reads for files (unknown
   properties and bad values become warnings, values out of range are clamped); `ComponentAccess` sets, then signals.
6. Requirements: `Requires`, and `AddWithRequirements` adding the needed components first with a guard against
   cycles; `Freeze` drops requirements that name nothing; metadata for the UI kept as data. Inactive reasons:
   `SetInactiveReason<T>(property, fn)`, called next to the property's registration while the registry is open, gives
   the property a function of the component that says why the property has no effect now ("" when it has), and refuses
   a closed registry or an unknown component or property; the rule that a property another turns off gets one, on the
   camera's registration; how the Inspector shows a reason is `editor-ui/inspectors`' (about 300 words).
7. Data that is not a property: `Extra` serializers, `ExtraReferences` for entity and asset references inside them
   (script fields), `ComponentValueArray` for components kept outside registries (prototypes), `ComponentObserver`.
8. Values as JSON: canonical JSON with the shortest floats that read back exactly, lenient parsing for agents (vectors as
   objects, Euler angles for quaternions, enums by name or number, UUID forms), the `Append` functions that need no DOM,
   `DescribeProperty` for tools.
9. `ComponentAccess`: the one validated path for reads and writes, used by the serializer, the Inspector, commands, undo
   and scripts. Engine code's typed `Entity::AddComponent` and `GetComponent` write raw, with no range, no validation
   and no `Requires`, so ranges hold only on the paths through reflection; and the newcomer's error: a field added to a
   component without being registered is not saved, not shown and out of reach of commands and scripts, and nothing
   warns (a play copy still copies it, with the whole struct) (about 80 words).

Then the alternatives, the tests (`Reflection`, `Reflection.ComponentSchema`, `Scene.InactiveProperties`), changing it
safely, and the exercise: predict, then run, a camera's `PerspectiveFOV` of 200 sent with `component.set` (refused) and
written into a hand-edited `.stscene` (clamped to 179 when the scene loads), with a trace from `component.set` to
`PropertyInfo::IsInRange`. At the end the reader can register a component with properties, ranges and metadata, and
predict what a file, a command and the Inspector each do with a value out of range.

**Leaves out.**

- Registries that open and accept, the component and settings registries that then freeze, and the composition root → `core/layers-registries`
- How the Inspector draws properties and shows an inactive reason → `editor-ui/inspectors`
- The gizmo shapes a component asks for → `gpu/debug-drawing`
- Binary property values in cooked scenes → `world/serialization`
- How commands check parameters against schemas → `editor/commands`
- Script fields and how scripts reach components → `scripting/abi-sdk`
- Type erasure and CRTP as C++ → `basics/cpp-generic`
- Adding a component from start to end → `world/tutorial-component`

**Fit.** `fits`: about 6,900 words against XL (8,000). Six excerpts, three figures, the problem section with its table
and the section on inactive reasons (about 300 words) take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:155` | feature | home | Lenient reads: unknown properties and bad values become warnings, values out of range are clamped |
| `scene-ecs:189-197` | feature | home | `PropertyType` and `PropertyValue`, `PropertyInfo`, `PropertyFlags`, the builders, `PropertyOptions`, `ComponentInfo`, `ComponentFlags`, `ComponentRegistry`'s registration and lookups, `ComponentInfoBuilder` |
| `scene-ecs:199-202` | feature | home | `Requires`, `ComponentValueArray`, `ComponentExtraReferences`, `ComponentObserver` |
| `scene-ecs:204` | feature | home | Canonical JSON of values, lenient parsing for agents, shortest floats, the `Append` functions, `DescribeProperty` |
| `scene-ecs:206` | feature | home | `ComponentAccess`, the single validated read and write path; engine code's typed `Entity::AddComponent` and `GetComponent` bypass it and write raw, with no range, no validation and no `Requires` (`Entity.h:24-35`, `ComponentAccess.h:17-19`, `:38-40`) |
| `scene-ecs:228` | feature | home | `RegisterSceneModule`: components, the two settings sections, the three loaders; called second, after Input |
| `scene-ecs:198` | feature | home | `ComponentRegistry::SetInactiveReason<T>(property, fn)`, called next to the property's registration while the registry is open: the function gets the component and returns why the property has no effect in its current state, or "" when it has; false, with the reason logged, for a closed registry or an unknown component or property (`ComponentRegistry.h:249-258`, `ComponentRegistry.cpp:93-119`); with `scene-ecs:531` and `scene-ecs:654` about 300 words in section 6; how the Inspector shows a reason is `editor-ui/inspectors`' |
| `scene-ecs:203` | feature | link | `ComponentGizmo`, named as a builder call; taught in `gpu/debug-drawing` |
| `scene-ecs:331`, `scene-ecs:338`, `scene-ecs:340` | concept | home | Reflection and Strata's builder DSL, with its newcomer's error: a field added without being registered is not saved, not shown and out of reach of commands and scripts, and nothing warns; validation, ranges and leniency; requirements and metadata for the UI as data, inactive reasons among them |
| `scene-ecs:336` | concept | use | Type erasure, CRTP and `std::variant` as `basics/cpp-generic` and `basics/cpp-modern` teach them |
| `scene-ecs:392` | code | home | `Strata/src/Strata/Reflection/ComponentRegistry.h:382-476`: `Register<T>`, the central mechanism: one template fills about 15 lambdas, `if constexpr` for tags |
| `scene-ecs:393` | code | home | `Strata/src/Strata/Reflection/PropertyBuilder.h:17-65`: the type deduced from a member pointer; the CRTP builder |
| `scene-ecs:394` | code | home | `Strata/src/Strata/Scene/ComponentRegistration.cpp:153-185`: a real registration (the camera's): ranges, tooltips, sections, inactive reasons |
| `scene-ecs:395` | code | home | `Strata/src/Strata/Reflection/Property.cpp:192-286`: `PropertyInfo::SetValue`: by type, enum membership, clamping, finite values, normalized quaternions |
| `scene-ecs:396` | code | home | `Strata/src/Strata/Scene/ComponentAccess.cpp:30-96`: strict against lenient reads; the page also shows `SetProperty`, set then signal, at `ComponentAccess.cpp:117-146` |
| `scene-ecs:397` | code | home | `Strata/src/Strata/Scene/ComponentAccess.cpp:153-192`: `AddWithRequirements`, recursion with a guard against cycles |
| `scene-ecs:444`, `scene-ecs:477`, `scene-ecs:478` | figure | home | The reflection model with its consumers; the Inspector's section headings (a sun or a post-process component); the Add Component menu grouped by category |
| `new:20` | hands-on | home | The page's exercise (D27), predict then run, with its "trace it yourself": a camera's `PerspectiveFOV` (range 1 to 179) set to 200 with `component.set`, which refuses it with the range in the error, against the same value in a hand-edited `.stscene`, which loads clamped to 179 (`SetValue` clamps and succeeds, so the lenient read logs no warning for it); the trace goes from the command's handler through `ApplyComponents` to `PropertyInfo::IsInRange` (about 250 words). Evidence: `Strata/src/Strata/Scene/ComponentRegistration.cpp:156`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:721`; `StrataEditor/src/Editor/CommandUtils.cpp:580-587`; `Strata/src/Strata/Reflection/Property.cpp:136`, `:233`; `Strata/src/Strata/Scene/ComponentAccess.cpp:67` |
| `scene-ecs:447` | figure | link | The component registry's states (Closed, Open, Frozen), drawn on `core/layers-registries` |
| `scene-ecs:522`, `scene-ecs:524`, `scene-ecs:526`, `scene-ecs:528` | rule | home | Register only while the composition root runs (or through `Extra` options); never rename a registered name; choose ranges that make bad states impossible; data that is not a property describes its references |
| `scene-ecs:531` | rule | home | A property another turns off gets an `InactiveReason`, so that people and agents do not edit a value that does nothing; shown on the camera's registration (`ComponentRegistration.cpp:178-182`) |
| `scene-ecs:649-650`, `scene-ecs:653`, `scene-ecs:655-656`, `scene-ecs:658` | term | home | Reflection, property, component flags, requirement, extra data, canonical JSON |
| `scene-ecs:654` | term | home | Inactive reason: text that says why a property has no effect in the component's current state, defined in section 6 |
| `editor-ui:755-756` | term | home | The editor UI survey's entries for reflection and for `PropertyInfo` and `ComponentInfo`: one glossary entry with `scene-ecs:649`, and one for each of the two types, defined in sections 1 and 3 |
| `scene-ecs:651-652` | term | link | Type erasure and CRTP, defined in `basics/cpp-generic` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Templates, lambdas, `std::function`, type erasure, CRTP and pointers to members | `basics/cpp-generic` | must |
| `std::variant`, `std::visit`, `if constexpr`, `std::optional` and `std::string_view` | `basics/cpp-modern` | must |
| JSON, UTF-8, and numbers written as text | `basics/data-formats` | must |
| Floating point: infinities, NaN and rounding | `basics/numbers` | must |
| Registries that open and accept, the component registry that then freezes; the composition root and module registration | `core/layers-registries` | must |
| Entities, storages and the `Entity` class | `world/ecs` | must |
| Change signals, which `ComponentAccess` emits | `world/scene-graph` | helps |
| Quaternions and Euler angles | `basics/math-rotations` | helps |
| The Inspector and its Add Component menu | `start/first-game` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `canonical-json` | Canonical JSON | - |
| `component-flags` | Component flags | - |
| `componentinfo` | ComponentInfo | - |
| `extra-data` | Extra data | - |
| `inactive-reason` | Inactive reason | - |
| `property` | Property | - |
| `reflection` | Reflection | PropertyInfo |
| `requirement` | Requirement | - |
