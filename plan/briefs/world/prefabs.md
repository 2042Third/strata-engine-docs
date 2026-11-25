# Brief: `world/prefabs`

| Field | Value |
| --- | --- |
| Title | Prefabs: the data model |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/serialization` |
| From | scene-ecs "Prefabs"; the data model, overrides and propagation (`EntityPrototype`, instantiation, `PrefabInstances`, `PrefabOverrides`); prefabs and models as entity templates, the asset side taken as given; keeping them exact while editing is `editor/prefab-instances`' |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/prefabs` — Prefabs: the data model

**Covers.** The job: prefabs and models as entity templates: prototypes compiled once, instantiation in slices, linked
instances with per-property overrides, and propagation of a prefab's change. The asset side is taken as given, and
keeping instances exact while editing is `editor/prefab-instances`'. This page carries the full section on the problem:
copy on place with no link, linked instances with overrides (Unity's prefabs, the defaults of Unreal's Blueprints), and
nested prefabs with variants. The map: a `.stprefab` read by `EntityTemplate` into an `EntityPrototype`, instantiated by
`ContinueInstantiation` into linked instance entities, with apply, revert and propagation drawn as arrows. Then, in this
order:

1. `EntityPrototype`: a compiled, immutable hierarchy in hierarchy order, with parent indices, one
   `ComponentValueArray` per type and the list of references between its entities; `Compile`, `FromSnapshot`,
   `Serialize`; immutable, so the loading worker and the main thread share it without locks; its own arrays because
   EnTT's pages of 1,024 waste memory in small prefabs; measured at 17 ms before and 0.3 ms after per 1,000-entity prefab.
2. Instantiation: `BeginInstantiation` and `ContinueInstantiation` in slices: checks first (capacity, collisions of kept
   IDs), then create, link, remap the references, link to the prefab, and signal every component. A slice is the part
   of a long job done in one frame: each call creates at most the entities it is given and returns, and the next frame
   goes on, so that no frame stalls (the frame's shared budget is `world/sub-scenes`').
3. `EntityTemplate` and its two kinds: `Prefab` (`.stprefab`, authored, `CreateFromEntities`, `WriteDocument`) and
   `Model` (imported, read only); `Instantiate`, `InstantiateMany`, `CompareInstance`, `GetSnapshot`; the loaders of
   Scene, Prefab and Model that the Scene module registers.
4. Linked instances: `PrefabInstanceComponent` (the prefab, the entity's template id `PrefabEntityID` in it, the version
   and hash it last took, the overrides); instance roots (a linked entity whose parent is not linked to the same prefab)
   and parts; `PrefabInstances`' operations (`ExtractTemplate`, `MakeTemplate`, `Compare`,
   `Replace` to revert, `ReplaceTemplate` to apply, `Link`, `Unpack`, `StripLinks`), and the versions and hashes they keep
   (the catch-up of outdated instances is `editor/prefab-instances`').
5. Overrides: `PrefabOverride` records (a property, an added component, a removed component, a removed entity; script
   fields as `Script` and `<Class>.<Field>`); `ComputeOverrides` as a diff of the part's JSON against the instance's,
   worked through on an example; `UpdateOverrides`; `Propagate`, which brings a prefab's change to its instances except
   their overrides; `Revert` and `ApplyToPart`. Inside the worked example of the override figure, the rules a reader
   needs to predict a change (about 150 words): entities the instance added are its own; components and entities the
   prefab added are made unless a Removed override says no; those it removed go unless the instance added them, and what
   the instance keeps below a removed entity moves up to the nearest entity that stays, keeping its place in the world;
   reverting a script field that the prefab does not store gives the class default. The root's transform and name are
   the instance's own, never overrides: left out of comparisons, kept by `Replace` and replaced by the prefab's own in
   `MakeTemplate`.
6. What Strata does not do: nested prefabs and prefab variants; a prefab made from linked entities stores no inner links.

Then the alternatives, the tests (`Scene.Prefab`, `Scene.PrefabInstances`, `Scene.PrefabOverrides`), changing it
safely, and the exercise: three instances of one prefab, one untouched, one with an overridden property, one with a
removed component; the reader predicts which values a change applied from a fourth instance reaches, checks it, and
traces `prefab.apply` to `PrefabOverrides::Propagate`. At the end the reader can predict which values a prefab's
change reaches, and instantiate a prototype from engine code without stalling a frame.

**Leaves out.**

- Apply and revert as undo steps; keeping instances exact while editing; outdated instances → `editor/prefab-instances`
- How the glTF importer makes a model → `assets/models-gltf`
- Making and placing prefabs in the editor, for game makers → `make/prefabs`
- The Inspector's prefab bar and override marks → `editor-ui/inspectors`
- Placing a prefab with its ghost → `editor/placement`
- A prefab asset's handle, references and loading → `assets/handles-meta`
- Sub-scenes, which compile a prepared scene into a prototype → `world/sub-scenes`

**Fit.** `fits`: about 4,850 words against L (5,000). Three excerpts, the worked example of the override figure with the
rules of propagation, and the exercise take most of it; the catch-up by versions and hashes is
`editor/prefab-instances`', and section 4 names it only.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:57` | feature | home | `PrefabInstanceComponent`: its fields, EngineAdded, IDs and hashes as read-only properties, overrides as extra data |
| `scene-ecs:168-170` | feature | home | `EntityPrototype`; instantiation in slices; `EntityTemplate`, `Prefab` and `Model` |
| `scene-ecs:172-175` | feature | home | The three loaders; `PrefabInstances`; per-property overrides and propagation; the root's own transform and name |
| `editor-core:172-173`, `editor-core:179` | feature | home | The editor survey's rows on the same data model: the instance link and the instance root, the root's own transform and name (kept by `Replace`, replaced in `MakeTemplate`), the override API; the same as `scene-ecs:57` and `scene-ecs:173-175`, taught once in sections 4 and 5 |
| `scene-ecs:349` | concept | home | Prefabs: the approaches, Strata's compiled prototype, linked instances, overrides as a JSON diff, propagation, no nested prefabs |
| `scene-ecs:402` | code | home | `Strata/src/Strata/Scene/SceneInstantiation.cpp:95-271`: `ContinueInstantiation`, a prototype copied in slices: checks, create, link, remap, link to the prefab, signal |
| `scene-ecs:403` | code | home | `Strata/src/Strata/Scene/PrefabOverrides.cpp:158-210`: `IsRootOwn` and `CompareComponents`, two JSON component maps diffed into override records |
| `new:22` | feature | home | The rules of propagation and revert, inside the worked example of section 5 (critic-scene-ecs-4; the survey did not read `Propagate` or `Revert`): entities the instance added are its own; components and entities the prefab added are made unless a Removed override says no; those the prefab removed go unless the instance added them, and what the instance keeps below a removed entity moves up to the nearest entity that stays, keeping its place in the world; reverting a script field that the prefab does not store gives the class default (about 150 words). Evidence: `Strata/src/Strata/Scene/PrefabOverrides.h:22-28`, `:106-116`, `:118-122` |
| `new:5` | code | home | `Strata/src/Strata/Scene/EntityPrototype.h:24-50`: the prototype's contract: hierarchy order, one array per type, immutable and shared without locks, `Compile` and `FromSnapshot` |
| `scene-ecs:456`, `scene-ecs:458` | figure | home | The prefab data flow; the override computation as a worked example, the part's JSON beside the instance's and the records between |
| `new:23` | hands-on | home | The page's exercise (D27), predict then run, with its "trace it yourself": three instances of one prefab (one untouched, one that overrides a property, one with a Removed component override), and a change applied from a fourth with `prefab.apply`; the reader predicts which values reach each instance, checks them, and follows the command to `PrefabOverrides::Propagate`, called for every other instance (about 250 words). Evidence: `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436`, `:556`; `Strata/src/Strata/Scene/PrefabOverrides.h:106-116` |
| `scene-ecs:564` | rule | home | The root's transform and name are the instance's own |
| `scene-ecs:566` | rule | link | The bookkeeping rule (`MarkSynced`, `PrefabSync::SetBaseline`, `UpdatePrefabOverrides`), taught in `editor/prefab-instances` |
| `scene-ecs:666-672` | term | home | Prefab, model, prototype, prefab instance (the qualified entry, against `VkInstance`, `InstanceData` and the script instance) and instance root, part, override, apply, revert, unpack and propagate |
| `editor-core:715-720`, `editor-ui:759` | term | home | The editor surveys' entries for prefab, prefab instance and instance root, override, apply, revert and unpack, and propagation: one glossary entry each with `scene-ecs:666`, `scene-ecs:669`, `scene-ecs:671` and `scene-ecs:672` (`editor-core:719`, apply, revert and unpack, is one entry with `scene-ecs:672`); template id (`PrefabEntityID`) is an entry of this page's own |
| `scene-ecs:674` | term | link | Outdated instance, defined in `editor/prefab-instances` |
| `new:6` | not-done | home | Nested prefabs and prefab variants: a prefab made from linked entities stores no inner links. Evidence: `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON values and their comparison | `basics/data-formats` | must |
| Snapshots, sinks and the remapping of references | `world/serialization` | must |
| `ComponentInfo`'s type-erased copies and `ComponentValueArray` | `world/reflection` | must |
| Change signals and the hierarchy | `world/scene-graph` | must |
| Immutable data shared between a worker and the main thread | `core/jobs` | must |
| Deadlines and work time in a frame, which the slices of instantiation respect | `core/frame-loop` | helps |
| Asset handles and loaders | `assets/handles-meta` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `instance-root` | instance root | - |
| `model` | Model | - |
| `part-of-a-prefab` | Part (of a prefab) | - |
| `prefab-world` | Prefab (world) | Template id, PrefabEntityID, Propagation, Override (prefab) |
| `propagate` | Propagate | - |
| `prototype` | Prototype | EntityPrototype |
| `revert` | Revert | - |
| `unpack` | Unpack | - |
