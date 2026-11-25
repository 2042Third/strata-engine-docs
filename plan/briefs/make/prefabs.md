# Brief: `make/prefabs`

| Field | Value |
| --- | --- |
| Title | Prefabs |
| Kind | T |
| Size | M |
| Tracks | G, B |
| Needs | `make/materials` |
| From | gamedev "Prefabs" (§1.7, concept 7; hands-on G5); editor-core "Using prefabs"; Coin Run's coin becomes a prefab |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/prefabs` — Prefabs

**Covers.** The page turns Coin Run's coin into a prefab and fills the level with coins. The idea first, in one
paragraph and the override figure: one coin saved as an asset, many linked copies in the scene, one place to change
them all, and each copy keeping values of its own. The steps. (1) Right-click the coin in the Hierarchy ▸ **Create
Prefab** (or drag it into the Content Browser): `Prefabs/Coin.stprefab`; the coin in the scene becomes its first
instance, with a prefab badge in the Hierarchy and the prefab bar in the Inspector. (2) Place four more: drag the
prefab into the Scene view; the box ghost rests on the surface under the pointer with its label ("Coin on 'Ground'"),
dimmed over empty space; Escape cancels; Snap puts it on the grid; End drops a selection to the ground. (3) An
override: give one coin a silver material; its overridden property is drawn bold with an accent bar, and the root's
own position and name never count as overrides. (4) Change the prefab: change another coin's emission and **Apply to
Prefab**; every coin takes it except where it overrides. (5) Revert: right-click the overridden property ▸ **Revert**,
or the prefab bar's Overrides menu ▸ **Revert All**; unpack an instance into plain entities, then undo the unpack. (6)
Save. Outdated instances in one paragraph: an instance whose prefab changed in another scene since it last took the
prefab's values is marked, and applying it over those newer changes asks first. Models as prefabs: the coin model of
`make/assets` was already placed as a linked group, and a model's instance offers only Revert. What Strata does not do
here: nested prefabs and prefab variants (a prefab made from linked entities keeps no inner links, so `Coin.stprefab`
no longer follows `coin-gold.glb`; `new:4`), and a prefab edit mode (a prefab changes through an instance and Apply;
`new:5`). At the end the reader can make, place, override, apply, revert and unpack prefabs; the checkpoint has five
coins, all instances of `Prefabs/Coin.stprefab`.

**Leaves out.**

- Prefabs as data: prototypes, instantiation, propagation → `world/prefabs`
- Keeping instances exact while editing, baselines and catch-up → `editor/prefab-instances`
- How a drop finds its surface → `editor/placement`
- Unity's prefab variants and Unreal's Blueprints compared → `start/coming-from`
- Placing many instances with one command → `make/commands`
- Instantiating prefabs from a script → `make/scripting-scene`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 2,700 words against M (3,000). Six steps at B0's length take most of it, with the idea and its
override figure, the paragraph on outdated instances and its exercise, two pictures and the two absences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:60` | feature | home | Placement and the drop ghost: the label, the dimmed ghost, Escape, Snap, a material dropped on a mesh, End to the ground |
| `gamedev:96` | feature | home | Creating a prefab and placing instances |
| `gamedev:97` | feature | home | Overrides, Apply, Revert, Unpack, outdated instances; models offer Revert only |
| `gamedev:98` | feature | home | Models as prefabs: the imported coin placed as a linked group |
| `gamedev:306` | concept | home | Prefabs and instances: reuse with overrides; the mistakes (editing every copy by hand, expecting a moved root to count) |
| `gamedev:416` | figure | home | The override model: the prefab, its instances, values per property, Apply and Revert |
| `gamedev:446` | figure | home | The drop ghost "Coin on 'Ground'" and a dimmed ghost over empty space |
| `gamedev:447` | figure | home | The prefab bar, the overridden properties and the Overrides menu |
| `gamedev:538` | hands-on | home | G5 on Coin Run: the coin made a prefab, five placed, one overridden, another's change applied |
| `gamedev:591` | term | home | Prefab, instance, override |
| `gamedev:592` | term | home | Apply, Revert, Unpack |
| `gamedev:593` | term | home | Outdated instance |
| `editor-core:184` | feature | home | No prefab edit mode; the page's paragraph is `new:5` |
| `editor-core:606` | hands-on | home | The prefab round trip: create, place, override, apply, revert |
| `scene-ecs:599` | hands-on | home | Overrides, propagation, revert and unpack in the editor, as steps 3 to 5 |
| `new:4` | not-done | home | Nested prefabs and prefab variants: a prefab made from linked entities stores no inner links. Evidence: `Strata/src/Strata/Scene/PrefabInstances.h:129-130` (`StripLinks`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` (run at the pin) |
| `new:5` | not-done | home | A prefab edit mode: a prefab changes through an instance and Apply. Evidence: `Docs/Releases/0.7.0.md:380` (run at the pin); the inventory's twin is `editor-core:184` |
| `editor-core:174-178` | feature | use | The `prefab.*` commands in the steps' command tabs |
| `editor-core:191` | feature | use | One placement for the drop and its ghost |
| `editor-core:194` | feature | use | The placement ghost while dragging |
| `editor-core:196-197` | feature | use | `asset.place` and `entity.dropToGround` in the command tabs |
| `editor-core:340` | concept | use | Prefabs as reusable templates with linked instances, at the user's level |
| `editor-core:363` | concept | use | Placing objects in 3D, at the user's level |
| `editor-core:522` | figure | use | The prefab bar with overrides marked |
| `editor-core:526` | figure | use | The placement ghost on a surface and over empty space |
| `editor-core:609` | hands-on | use | Outdated instances, as the paragraph's exercise |
| `editor-core:723` | term | use | Outdated |
| `editor-core:729` | term | use | Placement ghost |
| `scene-ecs:174-175` | feature | use | Per-property overrides; the root's transform and name are the instance's own |
| `scene-ecs:349` | concept | use | Prefabs, at the user's level |
| `scene-ecs:564` | rule | use | The root's transform and name are the instance's own |
| `scene-ecs:666` | term | use | Prefab |
| `scene-ecs:669` | term | use | Instance and instance root |
| `scene-ecs:671-672` | term | use | Override; Apply, Revert, Unpack and propagation |
| `editor-ui:184` | feature | use | The prefab bar and the override marks |
| `editor-ui:205` | feature | use | The drop and its ghost in the Scene view |
| `editor-ui:568` | figure | use | A prefab dragged over the Scene view with its ghost |
| `editor-ui:690` | hands-on | home | A prefab made, values overridden on an instance, applied and reverted through the Inspector |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Entities, the Hierarchy and the Inspector | `make/scenes-entities` | must |
| The Content Browser and models placed as linked groups | `make/assets` | must |
| Materials and assigning them | `make/materials` | must |
| Undo | `make/project-files` | must |

**Starting state.** The end state of `make/materials` (`startsFrom {"tutorial": "make/materials"}`): the level, the
gold coin and the metal ball. The silver material of step 3 is made in the step from the gold one. The page ends with
five instances of `Prefabs/Coin.stprefab`.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `prefab-make` | Prefab (make) | - |
| `revert` | Revert (use) | - |
| `unpack` | Unpack (use) | - |
| `outdated-instance` | Outdated instance (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-2 | must | stale-item | `make/prefabs` (step 4), `make/scripting-scene` (step 7), `make/project-coin-run` (step 5) | Three steps treat a coin's emission as a value of the entity. Emission belongs to the material asset `Gold.stmat` that every gold coin shares; a Mesh Renderer holds only Mesh, Material and Cast Shadows, and it sits on a child of the model's root. So `make/prefabs` step 4 changes every gold coin before Apply is pressed, and the emission raised from a script (`make/scripting-scene`) and the glow (`make/project-coin-run`) cannot be done, as the page's own `new:19` says. | `make/prefabs` step 4 changes a value an instance holds (the mesh child's Scale or its Cast Shadows on one coin) and applies it. `make/scripting-scene` step 7 swaps the mesh child's material, `SetProperty("MeshRenderer", "Material", glow)`, with `Materials/GoldGlow.stmat` asked for early, as Tetris swaps materials; `make/project-coin-run` step 5's glow is the same swap. About 60 words in all. | `allocation/make-a.md:615-616`, `:1063-1065`, `:1812-1813`, `:568`; `Strata/src/Strata/Renderer/Material.h:30-31`; `StrataTests/Architecture/ComponentSchema.json:404` (MeshRenderer: Mesh, Material, CastShadows); `Strata/src/Strata/Asset/GltfImporter.cpp:1974-1987`; `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| critic-make-a-20 | should | missing-item | `make/assets` (step 4), `make/materials` (step 3), `make/prefabs` (step 3) | A placed model is a root entity named after its file, with one child entity per node of the file; the Mesh Renderer is on a child, and the root holds only its Transform and what the reader adds. `make/materials` step 3 sets the coin's Mesh Renderer in the Inspector and `make/prefabs` step 3 overrides its material; with the root `Coin` selected the reader finds no Mesh Renderer. | `make/assets` step 4 shows the placed group expanded in the Hierarchy (the root, its children with the mesh) in two sentences; `make/materials` step 3 and `make/prefabs` step 3 select the child, or drop the material on the mesh in the view (about 60 words). | `allocation/make-a.md:411-412`, `:419-420`, `:519-520`, `:613-614`; `Strata/src/Strata/Asset/GltfImporter.cpp:592`, `:1974-1987` |
