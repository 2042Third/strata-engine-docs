# Brief: `editor/prefab-instances`

| Field | Value |
| --- | --- |
| Title | How prefab instances stay linked |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor/saving`, `world/prefabs` |
| From | editor-core ch. 8 (`PrefabSync`, `UpdatePrefabOverrides` in `CommitEdit`, baselines, catch-up by versions and hashes, apply and revert as undo steps); the data model is `world/prefabs` |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/prefab-instances` — How prefab instances stay linked

**Covers.** The problem: many instances of one prefab must stay in step with it while people edit both sides, in open and
closed scenes, with undo. The data model (links, instance roots, overrides and their computation), the approaches of
other engines and propagation are `world/prefabs`', and the page links them; this page keeps the model exact while
editing. Strata's choice: an override list kept current on every edit, and versions and hashes so that closed scenes
catch up, with "outdated" when both sides changed. The commands come first:
`prefab.create` (entities captured into a `.stprefab` and linked, as one step), `prefab.instantiate` (one or many,
checked up front, one step, names made unique, marked synced), `prefab.status` (changed, added and removed entities,
overrides, modified, outdated), `prefab.apply` (an instance or one override written into the prefab, added entities
linked, the other instances given the change except their overrides, as one step that wraps the document's step and the
scene's; refused for models, while playing, and for an outdated instance without `force`), `prefab.revert` (whole, one
component or one property, UUIDs kept), `prefab.unpack` and `prefab.select`. Then the upkeep: `UpdatePrefabOverrides`
inside `CommitEdit`, which tracks the instance roots an edit touched (so that a drag still merges) and updates their lists
incrementally unless the instance was reshaped. Then `PrefabSync`, every frame in edit mode: a baseline per prefab in use,
the source revisions it watches, a change on disk propagated in one undo step, the editor's own writes setting the
baseline first, settling over runs of edits. Then the catch-up when a scene opens: an instance whose recorded version
differs and whose synced hash still matches takes the new values; a modified one becomes outdated. The rules: code that
writes a prefab sets the baseline and marks instances synced; code that records a scene step outside `CommitEdit` keeps
override lists current; an outdated instance is never applied without `force`. The perf tests of override upkeep close
the testing section. The example is a crate prefab used in two scenes: change an instance in scene B, close it, apply
from scene A, open B again and read `prefab.status`. The trace exercise follows a drag of an instance's child through
`UpdatePrefabOverrides`. Afterwards the reader can change prefab code without double propagation, stale overrides or
lost values.

**Leaves out.**

- `PrefabInstanceComponent`, instance roots, `PrefabOverrides` and propagation as data, the approaches of other
  engines, and the words apply, revert and unpack → `world/prefabs`
- The inspector's prefab bar and overrides menu as they are drawn → `editor-ui/inspectors`
- Making and using prefabs as a game maker → `make/prefabs`
- No prefab edit mode, nested prefabs or variants → `make/prefabs`, `world/prefabs`
- Models as entity templates → `assets/models-gltf`

**Fit.** `fits`: about 5,400 words against L (5,000). Counted again from the sections, after the approaches and
propagation left for `world/prefabs` and with the trace exercise: nine features, three excerpts (the apply is long) and
five figures take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:340` | concept | home | Linked instances while editing: Strata's upkeep, versions, hashes and outdated instances; the approaches and propagation are `world/prefabs`' (`scene-ecs:349`), and the page links them |
| `editor-core:174-178` | feature | home | `prefab.create`, `prefab.instantiate`, `prefab.status`, `prefab.apply`, `prefab.revert`, `prefab.unpack`, `prefab.select` |
| `editor-core:180-183` | feature | home | Override upkeep on every edit, `PrefabSync`, the catch-up when a scene opens, the perf instrumentation |
| `editor-core:172-173` | feature | use | The instance link and the root's own transform and name, which `world/prefabs` teaches |
| `editor-core:179` | feature | use | The override API, which `world/prefabs` teaches |
| `editor-core:184` | feature | link | No prefab edit mode; `make/prefabs` says it |
| `editor-core:429` | code | home | `StrataEditor/src/Editor/EditorContext.cpp:1893-1981`: `UpdatePrefabOverrides`, touched instances, reshaped or incremental |
| `editor-core:431` | code | home | `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436-583`: `prefab.apply`; with `:39-72` (`PrefabApplyAction`, one step for file and scene) |
| `editor-core:434` | code | home | `StrataEditor/src/Editor/PrefabSync.cpp:336-383`: `CatchUp`, where version and hash decide updated or outdated |
| `editor-core:486` | figure | home | The anatomy of an instance, with the version and the synced hash the catch-up reads |
| `editor-core:489` | figure | home | The states of an instance: synced, modified, outdated |
| `editor-core:491` | figure | home | Propagation of a change: from `prefab.apply` and from a file changed on disk |
| `editor-core:522` | figure | home | The inspector's prefab bar with overrides marked |
| `editor-core:524` | figure | home | The Hierarchy's marks of a modified and an outdated instance |
| `editor-core:582` | rule | home | Code that writes a prefab sets the sync's baseline and marks instances synced |
| `editor-core:585` | rule | home | Code that records a scene step outside `CommitEdit` keeps override lists current |
| `editor-core:587` | rule | home | Never apply an outdated instance without `force` |
| `editor-core:609` | hands-on | home | The example: outdated instances across two scenes |
| `new:55` | hands-on | home | Trace it yourself (D27): with a breakpoint in `EditorContext::UpdatePrefabOverrides`, drag a value of an instance's child in the Inspector and see the touched instance root updated incrementally; then add an entity under the instance and see its list computed again because the instance was reshaped. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:1893-1981` |
| `editor-core:719` | term | use | Apply, revert, unpack, homed on `world/prefabs`; the page teaches the commands that do them |
| `editor-core:721-724` | term | home | Baseline, catch-up, outdated, part version and synced hash |
| `scene-ecs:173-175` | feature | use | Instance roots, per-property overrides and the root's own transform and name, from the data model |
| `scene-ecs:566` | rule | home | Code that writes a prefab or gives instances its values keeps the bookkeeping exact; taught with `editor-core:582` |
| `scene-ecs:674` | term | home | Outdated instance |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The prefab data model: links, instance roots, overrides, propagation | `world/prefabs` | must |
| Undo groups, `CommitEdit` and `AssetDocumentAction` | `editor/undo` | must |
| Asset documents written by the editor, and saves | `editor/saving` | must |
| Hashes | `basics/data-formats` | must |
| Source revisions and the file watcher | `assets/importing` | helps |
| When a scene's open swaps it in | `editor/projects` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `baseline-editor` | Baseline (editor) | - |
| `catch-up` | Catch-up | - |
| `outdated` | Outdated | - |
| `outdated-instance` | Outdated instance | - |
| `part-version` | Part version | - |
| `synced-hash` | synced hash | - |
